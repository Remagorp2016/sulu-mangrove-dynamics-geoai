# Sulu Mangrove Dynamics GeoAI
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22690576.svg)](https://doi.org/10.5281/zenodo.22690576)

**Reproducibility repository for:**  
*Three decades of mangrove persistence and turnover in Sulu, Philippines: Cross-product uncertainty and interpretable spatial modelling for management prioritization*

**Author:** Fadzlur-Nijar A. Adju  
**Affiliation:** Mindanao State University-Sulu, Jolo, Sulu, Philippines  
**Email:** fadzlur-nijar.adju@msusulu.edu.ph  
**ORCID:** https://orcid.org/0009-0003-1865-7596  
**Version:** 1.0.1

This repository contains the analysis code, Google Earth Engine export scripts, configuration files, derived summary tables, and manuscript-ready analytical figures used for an uncertainty-aware assessment of mangrove persistence, loss, gain, spatial clustering, and environmental correlates across Sulu Province, Philippines.

The study combines two independent annual 30-m mangrove products—**Continuous Global Mangrove Dynamics (CGMD)** and **Global Mangrove Watch (GMW) v4.1.12**—and deliberately treats cross-product disagreement as uncertainty rather than assuming either product is ground truth. Environmental models are evaluated using spatially blocked cross-validation and interpreted using SHAP and spatial permutation importance.

## Core study design

1. **Complete 19-municipality Sulu boundary** is used as the reporting extent.
2. **CGMD (1995–2023)** and **GMW v4.1.12 (1995–2025)** are harmonized on a common grid.
3. Annual extent agreement is quantified with IoU, Dice/F1, Cohen's kappa, and trajectory correlations.
4. Consensus persistence, gain, and loss are retained only where CGMD and GMW agree.
5. Consensus change is evaluated with multi-scale spatial hotspot analysis.
6. Separate **loss** and **gain** models are evaluated with random and spatial cross-validation.
7. XGBoost is interpreted with SHAP; spatial permutation importance provides an additional robustness check.
8. Final model outputs are used only as **relative management-screening scores**, not calibrated probabilities or causal effects.

## Headline reproducibility targets

The manuscript reports the following rounded results for the final 19-municipality analysis:

| Result | Value |
|---|---:|
| CGMD net change, 1995–2023 | +4.43% |
| GMW net change, 1995–2023 | +7.18% |
| GMW net change, 1995–2025 | +4.54% |
| Mean annual IoU, 1995–2023 | 0.884 |
| Mean annual Dice/F1 | 0.939 |
| Mean Cohen's kappa | 0.927 |
| Extent trajectory correlation | r = 0.849 |
| All-year persistent core corroborated by both products | ~20,107 ha |
| XGBoost loss spatial PR-AUC | 0.456 |
| XGBoost gain spatial PR-AUC | 0.812 |

Small differences can arise from software versions, geodesic-area implementation, and hotspot permutation settings. The release tables in `results/tables/` are the manuscript-aligned reference outputs.

## Repository structure

```text
.
├── config/                    # Pipeline configuration
├── data/
│   ├── README.md              # What must be downloaded/generated locally
│   ├── source_manifest.csv    # Dataset IDs, source URLs, and redistribution notes
│   └── derived/               # Lightweight derived summary data
├── docs/                      # GitHub/Zenodo and manuscript workflow notes
├── results/
│   ├── figures/               # Releasable analytical figures
│   └── tables/                # Releasable derived result tables
├── scripts/
│   ├── gee/                   # Google Earth Engine export scripts
│   └── python/                # Local cross-product, hotspot, and GeoAI analysis
├── .zenodo.json               # Zenodo GitHub-release metadata
├── CITATION.cff               # GitHub citation metadata
├── environment.yml            # Conda environment
├── requirements.txt           # pip dependencies
└── THIRD_PARTY_DATA.md        # Attribution and redistribution boundaries
```

## Data that are **not** redistributed here

Raw third-party source rasters are intentionally excluded. In particular, this repository does **not** redistribute raw GMW/JAXA tiles, the full CGMD source product, NASADEM, JRC Global Surface Water, CHIRPS, GHSL, or WorldPop. See `THIRD_PARTY_DATA.md` and `data/source_manifest.csv`.

The exact GMW v4.1.12 tiles required for the complete Sulu extent are:

```text
GMW_N06E119_v4112_mng_ext.tif
GMW_N06E120_v4112_mng_ext.tif
GMW_N06E121_v4112_mng_ext.tif
GMW_N07E120_v4112_mng_ext.tif
GMW_N07E121_v4112_mng_ext.tif
```

## Quick start

### 1. Create the environment

```bash
conda env create -f environment.yml
conda activate sulu-mangrove-geoai
```

or

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Acquire/export source inputs

Follow `data/README.md`. Run the Earth Engine scripts in `scripts/gee/`, download the five official GMW tiles from JAXA, and place all external inputs under `data/external/` using the filenames specified in `config/pipeline.yml`.

### 3. Run the analysis

```bash
python scripts/python/01_cross_product_consensus.py --config config/pipeline.yml
python scripts/python/02_spatial_hotspots.py --config config/pipeline.yml
python scripts/python/03_explainable_geoai.py --config config/pipeline.yml
python scripts/python/04_make_release_figures.py --config config/pipeline.yml
```

See `REPRODUCIBILITY.md` for details and interpretation safeguards.

## Interpretation safeguards

- **Cross-product agreement is corroboration, not ground-truth accuracy.**
- **SHAP values are model attributions, not causal effects.**
- **Random pixel splitting is reported only as a comparison; spatial blocking is the primary validation.**
- **Loss/gain score surfaces are relative prioritization aids, not calibrated event probabilities.**
- **Restoration-screening outputs require field validation of hydrology, substrate, exposure, tenure, species suitability, and existing habitat values.**

## Citation

The archived reproducibility release for this study is available on Zenodo:

**Adju, Fadzlur-Nijar A. (2026). Sulu Mangrove Dynamics GeoAI: reproducibility code and derived results (Version 1.0.1). Zenodo. https://doi.org/10.5281/zenodo.22690576**

DOI: **10.5281/zenodo.22690576**

When the associated journal article is published, please cite both the article and this reproducibility archive.
## License

- Analysis code: **MIT License** (`LICENSE`).
- Author-created derived summary tables and figures: **CC BY 4.0** (`DATA_LICENSE.md`).
- Third-party data retain their original provider terms and licenses; see `THIRD_PARTY_DATA.md`.

## Contact

Fadzlur-Nijar A. Adju  
fadzlur-nijar.adju@msusulu.edu.ph  
ORCID: https://orcid.org/0009-0003-1865-7596
