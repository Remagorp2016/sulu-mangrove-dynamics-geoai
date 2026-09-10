#!/usr/bin/env python
"""Cross-product annual agreement and consensus mangrove change analysis.

Neither CGMD nor GMW is treated as ground truth. Agreement is interpreted as
independent corroboration; disagreement is retained as product uncertainty.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.merge import merge
from rasterio.features import rasterize
from scipy.stats import pearsonr
from sklearn.metrics import cohen_kappa_score

from _common import load_config, ensure_dir, require_files, geodesic_pixel_area_grid


def similarity(a, b, mask):
    aa = a[mask].astype(bool); bb = b[mask].astype(bool)
    inter = np.logical_and(aa, bb).sum()
    union = np.logical_or(aa, bb).sum()
    sa, sb = aa.sum(), bb.sum()
    iou = inter / union if union else np.nan
    dice = 2*inter/(sa+sb) if (sa+sb) else np.nan
    overall = (aa == bb).mean()
    kappa = cohen_kappa_score(aa.astype('uint8'), bb.astype('uint8'))
    return iou, dice, kappa, overall


def write_mask(path, arr, profile, desc):
    p = profile.copy(); p.update(count=1, dtype='uint8', nodata=0, compress='deflate')
    with rasterio.open(path, 'w', **p) as dst:
        dst.write(arr.astype('uint8'), 1)
        dst.set_band_description(1, desc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default='config/pipeline.yml')
    args = ap.parse_args()
    cfg = load_config(args.config)
    paths = cfg['paths']; out = ensure_dir(paths['output_dir'])
    cgmd_path = Path(paths['cgmd_stack']); muni_path = Path(paths['municipalities'])
    gmw_paths = [Path(x) for x in paths['gmw_tiles']]
    require_files([cgmd_path, muni_path, *gmw_paths])

    muni = gpd.read_file(muni_path)
    with rasterio.open(cgmd_path) as cg:
        if cg.count != 29:
            raise ValueError(f'CGMD stack must have 29 bands (1995-2023); found {cg.count}')
        transform, crs, h, w, bounds = cg.transform, cg.crs, cg.height, cg.width, cg.bounds
        profile = cg.profile.copy()
        mask = rasterize([(g,1) for g in muni.to_crs(crs).geometry], out_shape=(h,w), transform=transform, fill=0, dtype='uint8').astype(bool)
        area = geodesic_pixel_area_grid(transform, h, w)

        annual=[]; cg_arrays=[]; gw_arrays=[]
        years=range(1995,2024)
        for year in years:
            c = cg.read(year-1995+1).astype('uint8')
            band = year-1985+1
            srcs=[rasterio.open(p) for p in gmw_paths]
            try:
                gm,_ = merge(srcs, indexes=[band], bounds=bounds, nodata=0, dtype='uint8')
            finally:
                for s in srcs: s.close()
            g=gm[0].astype('uint8')
            cg_arrays.append(c); gw_arrays.append(g)
            iou,dice,kappa,overall=similarity(c,g,mask)
            annual.append({
                'year':year,
                'cgmd_area_ha':float(area[mask & (c==1)].sum()),
                'gmw_area_ha':float(area[mask & (g==1)].sum()),
                'iou':iou,'dice_f1':dice,'kappa':kappa,'overall_agreement':overall
            })

    annual=pd.DataFrame(annual)
    annual.to_csv(out/'annual_cross_product_metrics.csv', index=False)
    r_extent,p_extent=pearsonr(annual.cgmd_area_ha, annual.gmw_area_ha)
    dc=annual.cgmd_area_ha.diff().dropna(); dg=annual.gmw_area_ha.diff().dropna()
    r_inc,p_inc=pearsonr(dc,dg)
    direction=(np.sign(dc.values)==np.sign(dg.values)).mean()

    c95,c23=cg_arrays[0],cg_arrays[-1]; g95,g23=gw_arrays[0],gw_arrays[-1]
    cg_persist=mask&(c95==1)&(c23==1); cg_gain=mask&(c95==0)&(c23==1); cg_loss=mask&(c95==1)&(c23==0)
    gw_persist=mask&(g95==1)&(g23==1); gw_gain=mask&(g95==0)&(g23==1); gw_loss=mask&(g95==1)&(g23==0)
    consensus_persist=cg_persist&gw_persist; consensus_gain=cg_gain&gw_gain; consensus_loss=cg_loss&gw_loss
    all_year = mask.copy()
    for c,g in zip(cg_arrays,gw_arrays): all_year &= (c==1)&(g==1)

    change=np.zeros((h,w),dtype='uint8'); change[consensus_gain]=1; change[consensus_loss]=2; change[consensus_persist]=3
    write_mask(out/'consensus_change_1995_2023.tif',change,profile,'0 none/uncertain; 1 gain; 2 loss; 3 persistent')
    write_mask(out/'consensus_all_year_persistent_1995_2023.tif',all_year.astype('uint8'),profile,'1 mangrove every common year in both products')
    baseline_mang=mask&(c95==1)&(g95==1); baseline_non=mask&(c95==0)&(g95==0); stable_non=baseline_non&(c23==0)&(g23==0)
    write_mask(out/'consensus_baseline_mangrove_1995.tif',baseline_mang.astype('uint8'),profile,'1 consensus mangrove in 1995')
    write_mask(out/'consensus_stable_nonmangrove_1995_2023.tif',stable_non.astype('uint8'),profile,'1 consensus nonmangrove at both endpoints')

    summary=pd.DataFrame([
        ['mean_annual_iou',annual.iou.mean()],['mean_annual_dice_f1',annual.dice_f1.mean()],
        ['mean_annual_kappa',annual.kappa.mean()],['mean_overall_agreement_pct',100*annual.overall_agreement.mean()],
        ['extent_trajectory_r',r_extent],['extent_trajectory_p',p_extent],
        ['annual_increment_r',r_inc],['annual_increment_p',p_inc],['direction_agreement_pct',100*direction],
        ['consensus_persistent_ha',float(area[consensus_persist].sum())],
        ['consensus_gain_ha',float(area[consensus_gain].sum())],['consensus_loss_ha',float(area[consensus_loss].sum())],
        ['all_year_consensus_persistent_ha',float(area[all_year].sum())],
    ],columns=['metric','value'])
    summary.to_csv(out/'cross_product_summary.csv',index=False)

    # Municipality summary on consensus endpoint classes.
    mid=rasterize([(geom,i+1) for i,geom in enumerate(muni.to_crs(crs).geometry)],out_shape=(h,w),transform=transform,fill=0,dtype='int16')
    name_col='shapeName' if 'shapeName' in muni.columns else muni.columns[0]
    rows=[]
    for i,row in muni.reset_index(drop=True).iterrows():
        mm=mid==(i+1)
        p=float(area[mm&consensus_persist].sum()); ga=float(area[mm&consensus_gain].sum()); lo=float(area[mm&consensus_loss].sum())
        rows.append({'municipality':row[name_col],'consensus_persistent_ha':p,'consensus_gain_ha':ga,'consensus_loss_ha':lo,'consensus_net_change_ha':ga-lo})
    pd.DataFrame(rows).sort_values('consensus_net_change_ha',ascending=False).to_csv(out/'municipality_consensus_change.csv',index=False)

    # GMW-only 2025 endpoint summary.
    srcs=[rasterio.open(p) for p in gmw_paths]
    try:
        gm25,_=merge(srcs,indexes=[41],bounds=bounds,nodata=0,dtype='uint8')
    finally:
        for s in srcs:s.close()
    g25=gm25[0]
    gmw_30=pd.DataFrame([{
        'period':'1995-2025','start_ha':float(area[mask&(g95==1)].sum()),'end_ha':float(area[mask&(g25==1)].sum()),
        'gain_ha':float(area[mask&(g95==0)&(g25==1)].sum()),'loss_ha':float(area[mask&(g95==1)&(g25==0)].sum())
    }]); gmw_30['net_ha']=gmw_30.end_ha-gmw_30.start_ha; gmw_30['net_pct']=100*gmw_30.net_ha/gmw_30.start_ha
    gmw_30.to_csv(out/'gmw_1995_2025_summary.csv',index=False)
    print(summary.to_string(index=False))

if __name__=='__main__': main()
