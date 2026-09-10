# Third-party data, attribution, and redistribution

This repository intentionally separates **original analysis code/derived summaries** from **third-party source data**.

## Global Mangrove Watch (GMW) v4.1.12

- Provider: Global Mangrove Watch / JAXA EORC distribution.
- Product used: annual 30-m mangrove extent, 1985–2025.
- The raw GMW GeoTIFF tiles are **not redistributed in this repository or Zenodo release**.
- Users must obtain the required tiles from the official provider and comply with the provider's current Terms of Use.
- Required Sulu tiles are listed in `data/source_manifest.csv`.

## Continuous Global Mangrove Dynamics (CGMD)

- Earth Engine asset: `projects/mangrovedatahub2/assets/CGMD-Extent30`.
- The global source product is not redistributed.
- The repository provides an Earth Engine script that extracts/rasterizes the study-area time series.
- Users should follow the dataset catalog citation and license/usage information current at the time of access.

## geoBoundaries

- Used to construct the complete 19-municipality Sulu study boundary.
- The repository does not assert ownership over the source boundary data.
- Users should follow geoBoundaries attribution and licensing requirements.

## NASADEM, JRC Global Surface Water, CHIRPS, GHSL, WorldPop

These products were accessed through Google Earth Engine to construct the predictor audit stack. The source datasets remain governed by their own provider terms. The release contains only original scripts and lightweight analytical summaries; it does not relicense the underlying data.

## Derived outputs

The author-created summary statistics and analytical figures in `results/` may be reused under `DATA_LICENSE.md`, but this permission does not override any rights or attribution requirements that may attach to third-party inputs represented in a derivative product.

When in doubt, obtain source data from the original provider rather than redistributing copies from this project.
