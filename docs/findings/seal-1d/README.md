# Seal 1d — "Re-run this fit", measured on the committed records

`scripts/seal_1d_rerun_measure.py` (commit 93b1f18, clean) re-ran each of the 202 committed records of seal 1b's run v2
(`records.jsonl` sha256 `f06931f4…`, `targets.json` `2fb09e3d…`; `docs/findings/seal-1b/v2/MANIFEST.md`) the way the
page does — the record's samples uploaded, its request with `seed: O.random_seed` through `/api/fit`, the two replies
judged by `/api/compare-fits` — in process, on this branch. Output: `rerun_measure.json`, `rerun_measure.txt`.

| | |
|---|---|
| the fit reproduced within rounding (same_fit's rules) | **202 / 202** |
| a different solution | 0 |
| the scattered starts differ (the fit reproduced) | 1 — 1-GTA UCl4-graphite / U4f Scan_2 (LA): a "not better" solution's χ²ᵣ 3.11925932 vs 3.11925894, 1.2e-7 relative, just over the objective tolerance 1e-7 |
| failed to re-run | 0 |
| re-run time | median 1.8 s, max 59 s |

**"Other numerics" on all 202 — by the approved rule, not a difference in arithmetic.** These records were made on
2026-10-14, before the four identity fields added on 2026-10-15 (`asteval`, `machine`, `os`, `blas`); a record that
lacks them reads as made under other numerics (`fitting._NUMERICS_KEYS_SINCE_2026_10_15`, the numerics-rule unit, GO).
On all 202 those four are the ONLY differing fields. Every seal this release makes records them.

Compared with 1b's own replay (same records, `fit_equality`, at a46cd3f): every fit reproduced there too; 1b counted
the starts differing on 7 of 328 records (committed and synthetic together).
