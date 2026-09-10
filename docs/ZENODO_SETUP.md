# Zenodo release workflow

## Preferred route: GitHub integration

1. Log in to Zenodo.
2. Open the **GitHub** integration from your Zenodo profile.
3. Enable `Remagorp2016/sulu-mangrove-dynamics-geoai`.
4. Verify the repository contains `.zenodo.json` **before** creating the GitHub release.
5. Create GitHub release/tag `v1.0.0`.
6. Wait for Zenodo to archive the release and mint the DOI.
7. Open the Zenodo record and verify title, creator, version, access, license, keywords, and files.
8. Copy the **version DOI** and **concept DOI** into your publication records.

Zenodo's current GitHub guidance states that GitHub releases are archived as software records. If both `.zenodo.json` and `CITATION.cff` are present, Zenodo uses `.zenodo.json` metadata for the GitHub release archive.

## After DOI minting

Update the manuscript Data Availability statement using `docs/DATA_AVAILABILITY_STATEMENT.md` and replace the placeholder DOI.

Optionally add a DOI badge to the GitHub README in a post-release commit. Do not change the already archived v1.0.0 tag.
