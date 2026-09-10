#!/usr/bin/env python
"""Spatially validated RF/XGBoost models with SHAP and screening surfaces."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
from scipy.ndimage import distance_transform_edt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, balanced_accuracy_score, f1_score, precision_score, recall_score
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier
import shap
from pyproj import Transformer

from _common import load_config, ensure_dir, require_files


def aggregate_to_grid(src_mask, src_transform, src_crs, dst_shape, dst_transform, dst_crs):
    dest=np.full(dst_shape,np.nan,dtype='float32')
    reproject(src_mask.astype('float32'),dest,src_transform=src_transform,src_crs=src_crs,dst_transform=dst_transform,dst_crs=dst_crs,resampling=Resampling.average,dst_nodata=np.nan)
    return dest


def xy_grid(transform,h,w):
    rr,cc=np.indices((h,w)); xs=transform.c+(cc+0.5)*transform.a+(rr+0.5)*transform.b; ys=transform.f+(cc+0.5)*transform.d+(rr+0.5)*transform.e
    return xs,ys


def group_ids(xs,ys,crs,block_m):
    tr=Transformer.from_crs(crs,32651,always_xy=True); e,n=tr.transform(xs,ys)
    return (np.floor(e/block_m).astype(int).astype(str)+'_'+np.floor(n/block_m).astype(int).astype(str)),e,n


def model_factory(kind, y, seed):
    if kind=='RF':
        return RandomForestClassifier(n_estimators=500,max_features='sqrt',min_samples_leaf=2,class_weight='balanced',n_jobs=-1,random_state=seed)
    ratio=(y==0).sum()/max(1,(y==1).sum())
    return XGBClassifier(n_estimators=160,max_depth=3,learning_rate=0.08,subsample=0.8,colsample_bytree=0.8,min_child_weight=5,reg_lambda=2.0,reg_alpha=0.1,scale_pos_weight=ratio,objective='binary:logistic',eval_metric='logloss',tree_method='hist',n_jobs=4,random_state=seed)


def evaluate_cv(X,y,groups,kind,cvtype,n_splits,seed):
    pred=np.full(len(y),np.nan)
    if cvtype=='random':
        splits=StratifiedKFold(n_splits=n_splits,shuffle=True,random_state=seed).split(X,y)
    else:
        splits=GroupKFold(n_splits=n_splits).split(X,y,groups)
    perm_rows=[]
    for fold,(tr,te) in enumerate(splits,1):
        m=model_factory(kind,y[tr],seed+fold); m.fit(X[tr],y[tr]); pred[te]=m.predict_proba(X[te])[:,1]
        if kind=='XGB' and cvtype=='spatial':
            pi=permutation_importance(m,X[te],y[te],scoring='average_precision',n_repeats=5,random_state=seed+fold,n_jobs=1)
            for j in range(X.shape[1]): perm_rows.append((fold,j,pi.importances_mean[j],pi.importances_std[j]))
    yhat=(pred>=0.5).astype(int)
    met={'roc_auc':roc_auc_score(y,pred),'pr_auc':average_precision_score(y,pred),'brier':brier_score_loss(y,pred),'balanced_accuracy_05':balanced_accuracy_score(y,yhat),'f1_05':f1_score(y,yhat),'precision_05':precision_score(y,yhat,zero_division=0),'recall_05':recall_score(y,yhat,zero_division=0)}
    return met,perm_rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default='config/pipeline.yml'); args=ap.parse_args()
    cfg=load_config(args.config); p=cfg['paths']; out=ensure_dir(Path(p['output_dir'])/'models')
    pred_path=Path(p['predictors']); muni_path=Path(p['municipalities']); base=Path(p['output_dir'])
    change_path=base/'consensus_change_1995_2023.tif'; baseline_path=base/'consensus_baseline_mangrove_1995.tif'; stable_non_path=base/'consensus_stable_nonmangrove_1995_2023.tif'
    require_files([pred_path,muni_path,change_path,baseline_path,stable_non_path])

    with rasterio.open(pred_path) as ds:
        parr=ds.read().astype('float32'); names=list(ds.descriptions); ptrans=ds.transform; pcrs=ds.crs; pshape=(ds.height,ds.width); profile=ds.profile.copy()
    features=cfg['model']['predictors']; idx=[names.index(f) for f in features]; gridX=np.stack([parr[i] for i in idx],axis=-1)
    valid=np.all(np.isfinite(gridX),axis=-1)
    muni=gpd.read_file(muni_path).to_crs(pcrs); mask90=rasterize([(g,1) for g in muni.geometry],out_shape=pshape,transform=ptrans,fill=0,dtype='uint8').astype(bool); valid &= mask90

    with rasterio.open(change_path) as ds:
        change=ds.read(1); ctrans=ds.transform; ccrs=ds.crs
    with rasterio.open(baseline_path) as ds: baseline=ds.read(1)
    with rasterio.open(stable_non_path) as ds: stable_non=ds.read(1)
    persist=(change==3); loss=(change==2); gain=(change==1)
    fp=aggregate_to_grid(persist,ctrans,ccrs,pshape,ptrans,pcrs); fl=aggregate_to_grid(loss,ctrans,ccrs,pshape,ptrans,pcrs); fg=aggregate_to_grid(gain,ctrans,ccrs,pshape,ptrans,pcrs)
    fbm=aggregate_to_grid(baseline==1,ctrans,ccrs,pshape,ptrans,pcrs); fsn=aggregate_to_grid(stable_non==1,ctrans,ccrs,pshape,ptrans,pcrs)
    baseline90=(fbm>=1/3)&mask90; dist=distance_transform_edt(~baseline90)*90.0
    loss_pos=(fl>=1/3)&valid; loss_neg=(fp>=2/3)&valid
    gain_pos=(fg>=1/3)&valid; gain_neg=(fsn>=2/3)&valid&(dist<=float(cfg['analysis']['gain_candidate_buffer_m']))

    xs,ys=xy_grid(ptrans,*pshape); seed=int(cfg['analysis']['random_seed']); ns=int(cfg['analysis']['n_splits'])
    performance=[]; all_perm=[]; final_models={}; score_surfaces={}
    for task,pos,neg in [('loss',loss_pos,loss_neg),('gain',gain_pos,gain_neg)]:
        sm=pos|neg; X=gridX[sm]; y=pos[sm].astype('uint8'); x=xs[sm]; yy=ys[sm]
        groups,easting,northing=group_ids(x,yy,pcrs,float(cfg['analysis']['primary_block_m']))
        pd.DataFrame(X,columns=features).assign(y=y,easting=easting,northing=northing,block=groups).to_csv(out/f'{task}_model_data.csv',index=False)
        for kind in ['RF','XGB']:
            for cv in ['spatial','random']:
                met,perm=evaluate_cv(X,y,groups,kind,cv,ns,seed); performance.append({'task':task,'model':kind,'cv':cv,**met})
                if kind=='XGB' and cv=='spatial':
                    for fold,j,mu,sd in perm: all_perm.append({'task':task,'fold':fold,'feature':features[j],'pr_auc_drop_mean':mu,'pr_auc_drop_sd':sd})
        # block sensitivity for XGB
        sens=[]
        for bm in cfg['analysis']['block_sensitivity_m']:
            grp,_,_=group_ids(x,yy,pcrs,float(bm)); met,_=evaluate_cv(X,y,grp,'XGB','spatial',ns,seed); sens.append({'task':task,'block_m':bm,'roc_auc':met['roc_auc'],'pr_auc':met['pr_auc']})
        pd.DataFrame(sens).to_csv(out/f'{task}_block_sensitivity.csv',index=False)
        # final common XGB + SHAP
        m=model_factory('XGB',y,seed); m.fit(X,y); final_models[task]=m
        rng=np.random.default_rng(seed); take=rng.choice(len(y),min(5000,len(y)),replace=False); ex=shap.TreeExplainer(m); sv=ex.shap_values(X[take]);
        sh=[]
        for j,f in enumerate(features):
            vals=sv[:,j]; feat=X[take,j]; q1,q3=np.nanquantile(feat,[.25,.75]); sh.append({'task':task,'feature':f,'mean_abs_shap':float(np.mean(np.abs(vals))),'mean_shap_low_quartile':float(np.mean(vals[feat<=q1])),'mean_shap_high_quartile':float(np.mean(vals[feat>=q3]))})
        pd.DataFrame(sh).sort_values('mean_abs_shap',ascending=False).to_csv(out/f'{task}_xgb_shap_importance.csv',index=False)
        # relative score domain
        domain=(fp>=2/3)&valid if task=='loss' else (fsn>=2/3)&valid&(dist<=float(cfg['analysis']['gain_candidate_buffer_m']))
        score=np.full(pshape,np.nan,dtype='float32'); score[domain]=m.predict_proba(gridX[domain])[:,1]; score_surfaces[task]=score
        prof=profile.copy(); prof.update(count=1,dtype='float32',nodata=-9999.0,compress='deflate')
        with rasterio.open(out/f'{task}_relative_score_90m.tif','w',**prof) as dst: dst.write(np.where(np.isfinite(score),score,-9999).astype('float32'),1)

    pd.DataFrame(performance).to_csv(out/'model_performance.csv',index=False); pd.DataFrame(all_perm).to_csv(out/'spatial_permutation_importance.csv',index=False)
    print(pd.DataFrame(performance).to_string(index=False))

if __name__=='__main__': main()
