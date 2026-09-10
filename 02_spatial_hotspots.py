#!/usr/bin/env python
"""Multi-scale Getis-Ord Gi* screening of consensus gain and loss."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape, box
from libpysal.weights import Queen
from esda.getisord import G_Local

from _common import load_config, ensure_dir, require_files


def raster_event_polygons(path, code):
    with rasterio.open(path) as ds:
        arr=ds.read(1); mask=arr==code
        geoms=[shape(g) for g,v in shapes(mask.astype('uint8'), mask=mask, transform=ds.transform) if v==1]
        return gpd.GeoDataFrame({'event':[code]*len(geoms)},geometry=geoms,crs=ds.crs)


def make_grid(bounds, size):
    minx,miny,maxx,maxy=bounds
    xs=np.arange(np.floor(minx/size)*size, maxx+size, size)
    ys=np.arange(np.floor(miny/size)*size, maxy+size, size)
    cells=[]
    for x in xs[:-1]:
        for y in ys[:-1]: cells.append(box(x,y,x+size,y+size))
    return cells


def analyze(event_gdf, muni, grid_m, alpha, permutations, seed):
    # EPSG:32651 is appropriate for the great majority of Sulu and matches the manuscript workflow.
    ev=event_gdf.to_crs(32651); study=muni.to_crs(32651).dissolve()
    grid=gpd.GeoDataFrame(geometry=make_grid(study.total_bounds,grid_m),crs=32651)
    grid=gpd.overlay(grid,study[['geometry']],how='intersection')
    inter=gpd.overlay(grid.reset_index(names='cell_id'),ev[['geometry']],how='intersection')
    areas=inter.geometry.area.groupby(inter.cell_id).sum() if len(inter) else pd.Series(dtype=float)
    grid=grid.reset_index(names='cell_id'); grid['event_ha']=grid.cell_id.map(areas).fillna(0)/10000.0
    w=Queen.from_dataframe(grid,use_index=False); w.transform='r'
    gl=G_Local(grid.event_ha.values,w,star=True,permutations=permutations,seed=seed)
    grid['gi_z']=gl.Zs; grid['gi_p']=gl.p_sim
    grid['hotspot']=(grid.gi_p<alpha)&(grid.gi_z>0)
    grid['coldspot']=(grid.gi_p<alpha)&(grid.gi_z<0)
    return grid


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default='config/pipeline.yml'); args=ap.parse_args()
    cfg=load_config(args.config); p=cfg['paths']; out=ensure_dir(Path(p['output_dir'])/'hotspots')
    change=Path(p['output_dir'])/'consensus_change_1995_2023.tif'; muni=Path(p['municipalities']); require_files([change,muni])
    municipalities=gpd.read_file(muni); alpha=float(cfg['analysis']['hotspot_alpha']); perms=int(cfg['analysis']['hotspot_permutations']); seed=int(cfg['analysis']['random_seed'])
    rows=[]
    for event,code in [('gain',1),('loss',2)]:
        ev=raster_event_polygons(change,code)
        total_ha=ev.to_crs(32651).area.sum()/10000
        for grid_m in cfg['analysis']['hotspot_grid_m']:
            g=analyze(ev,municipalities,int(grid_m),alpha,perms,seed)
            hot=g[g.hotspot].copy(); hot_ha=hot.event_ha.sum()
            rows.append({'event':event,'grid_m':grid_m,'significant_hotspot_cells':len(hot),'hotspot_event_ha':hot_ha,'share_of_event_pct':100*hot_ha/total_ha if total_ha else np.nan})
            g.to_file(out/f'{event}_gi_star_{int(grid_m)}m.geojson',driver='GeoJSON')
    pd.DataFrame(rows).to_csv(out/'hotspot_scale_sensitivity.csv',index=False)
    print(pd.DataFrame(rows).to_string(index=False))

if __name__=='__main__': main()
