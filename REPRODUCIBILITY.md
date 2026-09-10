# Reproducibility workflow

## 1. Obtain the study boundary and CGMD stack

Open the Google Earth Engine Code Editor and run:

- `scripts/gee/01_export_cgmd_19m_stack.js`

Confirm that the console reports **19 municipalities**, including **Lugus** and **Tapul**. Export the 29-band 1995–2023 CGMD stack aligned to the GMW grid.

## 2. Obtain predictor stack

Run:

- `scripts/gee/02_export_predictor_stack.js`

The export contains 16 acquisition/audit bands at approximately 90 m. The primary model later retains only the eight predictors documented in `CODEBOOK.md`.

## 3. Download GMW v4.1.12

Register with the JAXA/EORC Global Mangrove Watch download service and obtain the five exact Sulu tiles listed in `data/source_manifest.csv`. Keep the filenames unchanged.

## 4. Arrange external inputs

Create `data/external/` and place:

```text
data/external/
├── Sulu_CGMD_1995_2023_19Muni_OPTIMIZED.tif
├── Sulu_Mangrove_Driver_Predictors_90m.tif
├── Sulu_Municipal_Boundaries_19_CORRECTED.geojson
├── GMW_N06E119_v4112_mng_ext.tif
├── GMW_N06E120_v4112_mng_ext.tif
├── GMW_N06E121_v4112_mng_ext.tif
├── GMW_N07E120_v4112_mng_ext.tif
└── GMW_N07E121_v4112_mng_ext.tif
```

## 5. Cross-product consensus

```bash
python scripts/python/01_cross_product_consensus.py --config config/pipeline.yml
```

This writes annual agreement diagnostics, extent trajectories, endpoint change summaries, consensus rasters, and municipality-level change summaries to the configured output directory.

## 6. Hotspot analysis

```bash
python scripts/python/02_spatial_hotspots.py --config config/pipeline.yml
```

The primary grid is 1 km; 2- and 3-km grids are used as sensitivity checks. The analysis uses Getis–Ord Gi* to identify statistically concentrated gain and loss cells.

## 7. Explainable GeoAI

```bash
python scripts/python/03_explainable_geoai.py --config config/pipeline.yml
```

The script:

- resamples consensus response masks to the predictor grid;
- constructs conservative loss and gain domains;
- compares Random Forest and XGBoost;
- reports random and spatial-block CV;
- performs block-size sensitivity;
- fits final XGBoost models;
- computes SHAP and fold-wise permutation importance; and
- produces relative management-screening score surfaces.

## 8. Figures and release tables

```bash
python scripts/python/04_make_release_figures.py --config config/pipeline.yml
```

## Expected interpretation

Reproducing the workflow should preserve the manuscript's qualitative conclusions even if minor numerical differences occur:

1. both products indicate net expansion over the common period;
2. annual extent maps agree much more strongly than exact year-to-year changes;
3. a large all-year persistent core is independently corroborated;
4. gain is more spatially transferable than loss;
5. random CV overstates predictive performance; and
6. low elevation and water-connected settings dominate gain-associated model structure.

## Reproducibility boundary

The repository provides scripts and lightweight derived results but not raw third-party rasters. Full byte-for-byte reproduction therefore requires obtaining the same external product versions from their official providers.
