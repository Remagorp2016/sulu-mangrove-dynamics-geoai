
## Important: preserve the repository folders

When uploading through the GitHub web interface, **do not upload files from a Windows search result or any view that flattens folders**. After extracting the ZIP, open the inner `sulu-mangrove-dynamics-geoai-v1.0.0` folder and drag the folders and root files together into GitHub's **Add file → Upload files** page. GitHub should display paths such as `scripts/python/01_cross_product_consensus.py`, `scripts/gee/01_export_cgmd_19m_stack.js`, `config/pipeline.yml`, and `results/tables/Stage08_Model_Performance.csv`.

Before committing, confirm that `.zenodo.json` remains named exactly `.zenodo.json` at the repository root and that files have **not** become duplicates such as `README (1).md` or `cross_product_agreement_summary (2).csv`.

# GitHub setup for the publication repository

Recommended repository name:

`Remagorp2016/sulu-mangrove-dynamics-geoai`

## Repository description

> Reproducibility code and derived results for cross-product mangrove dynamics, spatial hotspots, and interpretable GeoAI in Sulu, Philippines.

## Suggested topics

`mangroves`, `remote-sensing`, `geoai`, `xgboost`, `shap`, `spatial-cross-validation`, `philippines`, `sulu`, `environmental-management`, `global-mangrove-watch`

## Upload sequence

1. Create the repository as **Public**.
2. Upload the complete contents of this package to the repository root.
3. Confirm that `.zenodo.json`, `CITATION.cff`, `LICENSE`, and `README.md` are at the root.
4. Do **not** commit `data/external/` or raw GMW tiles.
5. Check that GitHub renders the citation panel from `CITATION.cff`.
6. Commit with a message such as:

   `Prepare reproducibility release v1.0.0`

7. Connect the repository in Zenodo's GitHub integration **before creating the release**.
8. Create the GitHub release/tag `v1.0.0`.

GitHub supports `CITATION.cff` to display citation guidance. Zenodo can read repository metadata when archiving a GitHub release; when both `.zenodo.json` and `CITATION.cff` are present, Zenodo uses `.zenodo.json` for the archived release, while GitHub still uses `CITATION.cff` for the citation interface.
