# Changelog

All notable changes to this reproducibility repository are documented here.
## [1.0.1] - 2026-09-10

### Changed
- Updated release metadata for Zenodo archival.
- Added author ORCID metadata.
- Restored the intended reproducible repository directory structure.
- Archived the reproducibility release on Zenodo.

### DOI
- https://doi.org/10.5281/zenodo.22690576

No scientific results, model outputs, or manuscript conclusions were changed.

## [1.0.0]

### Added
- Complete 19-municipality Sulu study-boundary workflow.
- CGMD annual export and GMW grid-alignment scripts.
- 90-m environmental predictor export workflow.
- Cross-product annual agreement and consensus-change analysis.
- Multi-scale hotspot analysis workflow.
- Random vs spatial cross-validation for RF and XGBoost.
- XGBoost SHAP and spatial permutation-importance workflow.
- Municipality-level management-screening outputs.
- Zenodo and GitHub citation/release metadata.

### Methodological safeguards
- Neither CGMD nor GMW is treated as ground truth.
- Spatial validation is primary; random CV is reported only for comparison.
- SHAP is interpreted as attribution/association rather than causation.
- Population predictors were excluded from the primary model after internal temporal plausibility checks.
- `water_change_abs_pct` and post-baseline built-up change variables were excluded from the primary model to reduce invalid-value and temporal-leakage risks.
