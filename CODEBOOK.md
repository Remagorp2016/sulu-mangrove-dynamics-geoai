# Codebook

## Mangrove state and change conventions

For binary annual rasters:

- `1` = mangrove
- `0` = non-mangrove

For endpoint change products created by the Python workflow:

- `0` = no consensus / outside analysis domain
- `1` = consensus gain (non-mangrove in baseline, mangrove at endpoint in both products)
- `2` = consensus loss (mangrove in baseline, non-mangrove at endpoint in both products)
- `3` = consensus persistent mangrove (mangrove at baseline and endpoint in both products)

The all-year persistent core is stricter: a pixel must be mangrove in **every annual observation from 1995–2023 in both CGMD and GMW**.

## Primary model predictors

| Predictor | Unit / meaning | Primary model? |
|---|---|---|
| `elevation_m` | NASADEM elevation, m | Yes |
| `slope_deg` | terrain slope, degrees | Yes |
| `water_occurrence_pct` | JRC surface-water occurrence, % | Yes |
| `water_seasonality_months` | months/year surface water observed | Yes |
| `rain_mean_annual_mm` | mean annual CHIRPS precipitation | Yes |
| `rain_interannual_cv_pct` | interannual precipitation CV, % | Yes |
| `rain_trend_mm_per_year` | linear annual precipitation trend | Yes |
| `built_fraction_2000` | GHSL built-up fraction at baseline | Yes |
| `water_recurrence_pct` | JRC recurrence | No, screened out from primary set |
| `water_change_abs_pct` | JRC absolute water change | No; invalid sentinel / temporal overlap concerns |
| `water_max_extent` | JRC maximum extent | No, redundant with water metrics |
| `built_fraction_2020` | GHSL 2020 built-up | No; post-baseline leakage concern |
| `built_fraction_change_2000_2020` | built-up change | No; post-baseline leakage concern |
| population bands | WorldPop-derived densities/change | No; failed internal temporal plausibility check |

## Model tasks

### Loss model
- Positive class: high-confidence consensus loss.
- Reference class: high-confidence consensus persistent mangrove.

### Gain model
- Positive class: high-confidence consensus gain.
- Reference class: stable non-mangrove within 500 m of the 1995 consensus mangrove edge.

## Validation

- Primary spatial block size: 5 km.
- Sensitivity: 3, 7.5, and 10 km.
- Metrics: ROC-AUC, PR-AUC, Brier score, balanced accuracy, F1, precision, recall.
- PR-AUC is emphasized for the rare loss event class.

## Screening scores

Final XGBoost outputs are **relative susceptibility / environmental-analog scores**, not calibrated probabilities. The top 10% thresholds are used only for province-wide screening and do not imply a universal ecological threshold.
