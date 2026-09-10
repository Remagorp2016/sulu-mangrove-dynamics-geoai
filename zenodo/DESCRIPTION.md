# Zenodo description

This software release provides the reproducibility code and lightweight derived results for the study **“Three decades of mangrove persistence and turnover in Sulu, Philippines: Cross-product uncertainty and interpretable spatial modelling for management prioritization”**.

The workflow evaluates three decades of mangrove dynamics across the complete 19-municipality extent of Sulu Province, Philippines. It harmonizes two independent annual 30-m mangrove products—Continuous Global Mangrove Dynamics (CGMD) and Global Mangrove Watch (GMW) v4.1.12—to quantify annual cross-product agreement, consensus persistence, loss and gain, and product-sensitive uncertainty. Consensus change is evaluated with multi-scale spatial hotspot analysis. Separate mangrove-loss and mangrove-gain models are compared using Random Forest and XGBoost under random and spatially blocked cross-validation, with XGBoost interpretation using SHAP and spatial permutation importance.

The release supports environmental-management screening while explicitly avoiding causal overinterpretation: cross-product agreement is treated as corroboration rather than ground truth; SHAP values are model attributions rather than causal effects; and final score surfaces are relative prioritization aids rather than calibrated probabilities.

Raw third-party source rasters are not redistributed. The repository documents the exact GMW tile identifiers, Google Earth Engine dataset IDs, acquisition scripts, and provider links needed to reconstruct the analysis inputs.
