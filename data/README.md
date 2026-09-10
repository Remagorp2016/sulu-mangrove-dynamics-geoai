# Data acquisition

`data/external/` is intentionally git-ignored. Populate it with the exact external inputs below before running the Python workflow.

## A. Global Mangrove Watch v4.1.12

Obtain the five official GMW raster tiles from JAXA EORC after registration:

- `GMW_N06E119_v4112_mng_ext.tif`
- `GMW_N06E120_v4112_mng_ext.tif`
- `GMW_N06E121_v4112_mng_ext.tif`
- `GMW_N07E120_v4112_mng_ext.tif`
- `GMW_N07E121_v4112_mng_ext.tif`

Do not rename the files.

## B. CGMD 1995–2023 study-area stack

Run `scripts/gee/01_export_cgmd_19m_stack.js` in Google Earth Engine. Export the optimized 29-band GeoTIFF and save it as:

`Sulu_CGMD_1995_2023_19Muni_OPTIMIZED.tif`

## C. Predictor stack

Run `scripts/gee/02_export_predictor_stack.js` and save the GeoTIFF as:

`Sulu_Mangrove_Driver_Predictors_90m.tif`

## D. Municipality boundary

The first Earth Engine script also exports the 19-municipality Sulu boundary. Save it as:

`Sulu_Municipal_Boundaries_19_CORRECTED.geojson`

The Python workflow checks input existence and raster compatibility before analysis.
