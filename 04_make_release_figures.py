#!/usr/bin/env python
from pathlib import Path
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from _common import load_config, ensure_dir


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default='config/pipeline.yml'); args=ap.parse_args(); cfg=load_config(args.config)
    base=Path(cfg['paths']['output_dir']); out=ensure_dir(base/'figures'); models=base/'models'
    perf=pd.read_csv(models/'model_performance.csv')
    p=perf.pivot_table(index=['task','model'],columns='cv',values='pr_auc').reset_index(); labels=[f"{r.task.title()} {r.model}" for _,r in p.iterrows()]
    fig,ax=plt.subplots(figsize=(8,5)); x=range(len(labels)); x=list(x); width=.35
    ax.bar([v-width/2 for v in x],p['spatial'],width,label='Spatial CV'); ax.bar([v+width/2 for v in x],p['random'],width,label='Random CV')
    ax.set_xticks(x); ax.set_xticklabels(labels,rotation=20,ha='right'); ax.set_ylabel('PR-AUC'); ax.set_title('Random vs spatial cross-validation'); ax.legend(); fig.tight_layout(); fig.savefig(out/'random_vs_spatial_pr_auc.png',dpi=200); plt.close(fig)

    sens=pd.concat([pd.read_csv(models/'loss_block_sensitivity.csv'),pd.read_csv(models/'gain_block_sensitivity.csv')])
    fig,ax=plt.subplots(figsize=(8,5))
    for task in ['loss','gain']:
        d=sens[sens.task==task]; ax.plot(d.block_m/1000,d.pr_auc,marker='o',label=task.title())
    ax.set_xlabel('Spatial block size (km)'); ax.set_ylabel('PR-AUC'); ax.set_title('XGBoost spatial-CV sensitivity'); ax.legend(); fig.tight_layout(); fig.savefig(out/'block_size_sensitivity.png',dpi=200); plt.close(fig)

    for task in ['loss','gain']:
        d=pd.read_csv(models/f'{task}_xgb_shap_importance.csv').sort_values('mean_abs_shap')
        fig,ax=plt.subplots(figsize=(8,5)); ax.barh(d.feature,d.mean_abs_shap); ax.set_xlabel('Mean absolute SHAP value'); ax.set_title(f'{task.title()} model: XGBoost SHAP importance'); fig.tight_layout(); fig.savefig(out/f'{task}_xgb_shap_importance.png',dpi=200); plt.close(fig)

if __name__=='__main__': main()
