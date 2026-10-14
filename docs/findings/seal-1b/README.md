# Seal 1b — what the seal's states rest on, measured (2026-10-14)

Branch `seal-1b-measure` (on `seal-1a-server` 828f264); design memo V6.11 1b, V5.4 / V6.5 (option (b)).
Every number below: `python scripts/seal_1b_summarise.py`. Generators: `scripts/seal_1b_measure.py`
(record, record-synthetic, verify, replay, sizes), `scripts/seal_1b_background_twin.js`.

**Corpus.** The 202 committed fit targets (`optimizer-disagreement/targets.json`) recorded through the
real `/api/fit` route with the page's request (full-precision upload, the target's background,
Trust-Region, n_perturb 3, n_starts 3 when ≥ 2 unlinked components), plus 126 SYNTHETIC fits covering
what the committed targets lack — every lineshape (Gaussian, Lorentzian, pseudo-Voigt, asym-GL, DS,
DS+G, LA) × every background method (Shirley with averaging 3, Smart, Tougaard, linear, none, manual
anchors) × three spectra. 328 records, all HTTP 200 and converged, recorded and judged on ONE clean
commit (db50327; `software` names the commit and its cleanliness). The verbatim records (~20 MB) are
not committed; `records_index.jsonl` lists them.

## 1. Cross-process bit-stability per lineshape (Q7)

Every record verified (`/api/verify-fit`) in four settings the producer did not run in: two fresh
processes, a process with shaken memory (arrays of random size allocated between checks), and a
four-worker gunicorn reached over HTTP.

| setting | committed (202) | synthetic (126) |
|---|---|---|
| fresh process 1 | 175 consistent, 27 unconfirmed | 126 consistent |
| fresh process 2 | 177 consistent, 25 unconfirmed | 126 consistent |
| shaken memory | 179 consistent, 23 unconfirmed | 126 consistent |
| gunicorn, 4 workers | 168 consistent, 34 unconfirmed | 119 consistent, 7 unconfirmed |

- **No record reads `mismatch` in any setting** (1,312 verifications): no honest fit is ever called
  stale by the server's check.
- Every `unconfirmed` is a fit holding LA(α,β,m) (the committed U 4f models; 7 synthetic LA fits under
  gunicorn), always on an evaluation identity (`components`). Every other lineshape — Gaussian,
  Lorentzian, pseudo-Voigt / GL, asym-GL, DS, DS+G (FFT) — verifies `consistent` in every setting.
- So Q7's set stays `NOT_BIT_STABLE_SHAPES = {la_casaxps}`: LA's `np.convolve` is the one evaluator
  that is not bit-stable here; DS+G's FFT is (on these 18 synthetic DS+G fits × 4 settings). An LA fit
  is shown, never current, until LA's evaluator is made deterministic (owner Q7: a separate unit).

## 2. The page's background is the server's (V5.4.4 / V6.5 step 4)

The page's own `computeBackgroundCore` (extracted verbatim), given each record's request as the page's
form gives it (the window's edge energies as text, or blank for the whole region; the request's
averaging; a manual request's anchors), against `O.background_y`: **bit-identical on 328 / 328** —
Shirley 90, Smart 130, smart_exp 24, Tougaard 21, linear 21, none 21, manual 21 — and the window is
recovered exactly from the edge text on all 328. The binding "the page's certified background equals
the recorded one" can be exact, as the plan requires.

## 3. The seal's size

Per committed fit, as JSON: R median 9.5 kB (max 15.4 kB), O median 52.7 kB (max 76.7 kB); gzipped
3.2 kB and 23.8 kB. All 202: R 2.2 MB, O 11.2 MB raw; 0.76 MB and 5.1 MB gzipped. A 30-tab project
gains about 2 MB of JSON (0.8 MB in a .proj.zip).

## 4. "Re-run this fit" (REPLAY-CHECKED, 1d)

Each record re-run through `/api/fit` with its recorded seed as the caller's seed, compared with the
record by `tests/fit_equality.py` (same fit within rounding; σ and certificate history excluded):

| | records | reproduced | differ |
|---|---|---|---|
| committed | 202 | 196 (134 byte-identical) | 6 — all LA U 4f |
| synthetic | 126 | 121 (86 byte-identical) | 5 — all DS+G |

The 11 that differ: 9 differ ONLY in the scattered-starts evidence (a not-better solution's χ²ᵣ a few
1e-7 apart, or one start landing in a different not-better solution) — the fit itself reproduced; 1
(U4f Scan_1) has the fit's χ²ᵣ 3e-7 relative apart, above the comparator's 10·ftol for the objective;
1 (U4f Scan_3) reaches a different minimum (a component's amplitude 0.7 % apart) — the LA several-minima
case CLAUDE.md records. For 1d: the re-run verdict must judge THE FIT and report the scattered-starts
evidence separately (otherwise 9 reproduced fits would read "different"); an LA fit can honestly read
"a different solution".

## Notes

- Q5 (areas) was measured and switched before this unit (`docs/findings/q5-area`), so 1b does not
  re-measure it.
- `scripts/seal_1b_background_twin.js` was corrected during the run (it first handled only requests
  with explicit window indices and no anchors, so the synthetic requests were not compared); the
  committed version gives the 328 / 328 above from the same records.
