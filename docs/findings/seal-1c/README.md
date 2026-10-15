# Seal 1c — findings

## Legacy census (step 7, plan §11)

Every saved fit committed to the repository predates the seal. After step 7 the page installs seals only, so these
fits — and every student's save from before this release — reach the legacy path, which must be main's.

`scripts/seal_legacy_census.py` loads each committed project (`docs/autofit/test_data/*.proj.zip`) through two
running pages — this branch and main (ef750f6) — re-saves it, and compares tab by tab. Result
(`legacy_census.json`, 2026-10-15):

| | |
|---|---|
| projects / spectrum tabs with a saved fit | 7 / 121 |
| a seal installed on load | 0 |
| loaded LEGACY (the fit restored by the legacy adapter) | 81 |
| dropped to peaks only (legacy restore refused, as main) | 40 |
| restore verdict identical to main's | 121 / 121 |
| re-save identical to main's except the two new fields | 121 / 121 |
| new field `provenance` (null for a restored fit; V6.8) | 121 tabs |
| new field `ui.fitMethod` (§8.5) | 6 tabs |
| dropped fits keeping a record as provenance | 0 / 40 (none of the 121 carries a record: all predate 2026-10-10) |

The 81 / 40 split is the restore census already recorded in CLAUDE.md (81 STALE unconfirmed, 40 peaks only).
Pinned without main by `tests/test_browser_seal_step7.py::test_every_committed_saved_fit_loads_legacy_and_re_saves_without_a_seal`.

## Release measurements (step 8, plan §10)

What a student sees change when the page reads a fit's RECORD instead of re-deriving it.
`scripts/seal_1c_release_measure.js` (commit 2db1d60) reads ONE server reply per committed target — seal 1b's
run-v2 records (202 committed targets; `records.jsonl` sha256 `f06931f4…`, `targets.json` `2fb09e3d…`,
`tabs.json` `1b1ae9f9…`, as in `docs/findings/seal-1b/v2/MANIFEST.md`) — two ways: as **main** reads it (main's
own functions, extracted from `templates/index.html` at ef750f6, applied to the tab's own model) and as the
**record** says (what the sealed page shows). The same reply on both sides: no refit, no optimiser jitter.
Output: `release_measure.json`.

| what is shown | main | the record | difference on the 202 committed fits |
|---|---|---|---|
| χ² | χ²ᵣ × max(1, n − 3·peaks) | the server's χ² | wrong on the 113 fits whose free parameters ≠ 3 × peaks (links, locks, held or extra shape parameters): median 0.59 %, max 2.9 %; 60 fits > 1 %, none > 10 % |
| RMSE | over the reply's residuals | the server's | ≤ 9.3e-16 relative (rounding) |
| R-factor | `_computeRFactor` on the page's background (1b: bit-identical to the server's) | the server's | ≤ 9.8e-15 percentage points |
| component curves (865) | `evalPeakArray` on the fit's grid | the recorded curves | ≤ 8.0e-16 of the component's height (LA), ≤ 4e-16 for every other shape |
| areas | `_peakArea` (Q5: the server's trapezoid) | the recorded areas | ≤ 4.1e-16 relative; area % ≤ 2.1e-14 pp |

So on the committed fits the only number a student sees move is χ² itself (the reduced χ²ᵣ, which the
header, Results and the colour bands show, is the server's on both). Curves and areas were already the
server's to rounding since A03 / `caM` / DS+G parity and Q5; reading the record removes the dependence,
it does not move a value.

The other §10 changes and where each is measured:

| §10 change | measured |
|---|---|
| PENDING until checked; UNCONFIRMED offline / other numerics | 1b §1: 1,312 cross-process verifications, 0 mismatch; 64 unconfirmed, every one an LA record (the separate LA unit) |
| the page's background is the server's (the binding) | 1b §2: bit-identical on 328 / 328 |
| saves before this release are never current (Q1) | the legacy census above: 121 / 121 load LEGACY or peaks-only, as main restores them |
| a reloaded fit keeps σ and its scattered-starts detail | `tests/test_browser_export_prefix.py`: a reloaded fit's CSV / XLSX carry the σ main left blank and the not-better χ²ᵣ list main dropped — the only two differences from main's export |
| larger saves | below |

### Larger saves (`scripts/seal_1c_save_size.py`, commit 10813c2, `save_size.json`)

Each committed project loaded into this branch's page, Run Fit pressed on every spectrum tab with a model (the page's
default method), each fit's own check awaited, the project saved again:

| | committed (main-era saves) | re-saved, every fit sealed |
|---|---|---|
| the seven project files | 1,837,421 B | 5,023,286 B (× 2.73) |
| their content, uncompressed | 6,478,409 B | 20,651,111 B (× 3.19) |
| one seal (121) | — | median ≈ 90 KB raw, ≈ 35 KB gzipped; largest 95,112 B / 37,773 B |

All 121 fits sealed with no page error: **111 CURRENT, 10 UNCONFIRMED** right after Run Fit. All 10 unconfirmed are U 4f
fits holding an LA component (LACX) — the non-bit-reproducible lineshape (1b §1; the separate LA unit logged in
`docs/autofit/PROGRESS.md`). Until that unit lands, about one fresh fit in twelve on the committed data reads
"unconfirmed" with its reason and a Check again control.
