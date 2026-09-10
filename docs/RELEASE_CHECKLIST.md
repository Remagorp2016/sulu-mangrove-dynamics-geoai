# Release checklist — v1.0.0

## Scientific integrity

- [ ] Study boundary explicitly contains all 19 Sulu municipalities.
- [ ] Manuscript and release tables use the corrected 19-municipality results.
- [ ] Raw GMW tiles are absent from the repository.
- [ ] No superseded 13,700-ha incomplete-boundary results are present.
- [ ] Cross-product agreement is not described as ground-truth accuracy.
- [ ] SHAP language uses attribution/association, not causality.
- [ ] Spatial CV is presented as primary validation.
- [ ] Screening scores are not called calibrated probabilities.

## Repository

- [ ] `README.md` renders correctly.
- [ ] `CITATION.cff` validates.
- [ ] `.zenodo.json` is valid JSON.
- [ ] `LICENSE` and `DATA_LICENSE.md` are present.
- [ ] `THIRD_PARTY_DATA.md` is present.
- [ ] `data/external/` is empty/untracked.
- [ ] `SHA256SUMS.txt` matches all released files.

## GitHub

- [ ] Repository is public.
- [ ] Zenodo integration is enabled before the release.
- [ ] Tag is exactly `v1.0.0`.
- [ ] Release title: `v1.0.0 — JEM submission reproducibility release`.
- [ ] Release notes use `zenodo/RELEASE_NOTES_v1.0.0.md`.

## Zenodo

- [ ] Creator spelling is correct: Adju, Fadzlur-Nijar A.
- [ ] ORCID is correct: 0009-0003-1865-7596.
- [ ] Email is correct in `CITATION.cff` and `README.md`: fadzlur-nijar.adju@msusulu.edu.ph.
- [ ] Affiliation is correct.
- [ ] Resource type is Software.
- [ ] Version is 1.0.0.
- [ ] Access is Open.
- [ ] License is MIT for the software record.
- [ ] DOI has been copied into the manuscript Data Availability statement.
