# v1.0.0 — JEM submission reproducibility release

Initial public reproducibility release associated with the manuscript:

**Three decades of mangrove persistence and turnover in Sulu, Philippines: Cross-product uncertainty and interpretable spatial modelling for management prioritization**

## Included

- Google Earth Engine scripts for the corrected 19-municipality Sulu boundary, CGMD stack, and predictor stack.
- Python workflow for annual CGMD–GMW agreement and consensus change.
- Multi-scale spatial hotspot workflow.
- Random Forest and XGBoost model comparison under random and spatial CV.
- XGBoost block-size sensitivity, SHAP importance, and spatial permutation importance.
- Municipality-level management-screening summary.
- Lightweight manuscript-aligned derived tables and analytical figures.
- Complete data-source manifest, attribution/redistribution notes, and reproducibility instructions.

## Important methodological notes

- CGMD and GMW are treated as independent products, not ground truth.
- The complete 19-municipality Sulu boundary supersedes earlier exploratory runs based on an incomplete administrative extent.
- Population predictors were excluded from the primary model after an internal temporal plausibility check.
- Post-baseline built-up change and invalid water-change values were excluded to reduce temporal leakage and data-quality risk.
- Relative loss/gain score surfaces are screening aids and require local validation.

## External source data

Raw GMW/JAXA tiles and other third-party source rasters are not redistributed in this release. Exact acquisition information is provided in `data/source_manifest.csv` and `THIRD_PARTY_DATA.md`.
