# A03 — Voigt η identity, parameter-range sweep, U 4f gap re-measurement (2026-09-22)

Branch `fix-voigt-eta-identity` off main `c6f358e`. Owner's brief (2026-09-22):
"A03: Voigt eta identity, parity-harness sweep over each shape's FREE
parameters across their fitted ranges, and re-measure the U 4f gap
afterwards. That re-measurement is the test of whether Batch Fit's
'starting point' label can retire."

## 1. The defect

A "Voigt" component had two definitions:

| site | η |
|---|---|
| `evalPeak` (chart, `_peakArea` → Results, sidebar, Quantify, CSV/XLSX/TSV, figure, stack) | 0.5 |
| `runFitLocal` (Batch Fit, fallback) | 0.5 (glMix never freed for a Voigt) |
| dropdown tooltip, CLAUDE.md lineshape table, parity harness | 0.5 |
| `peakToBackendSpec` → `/api/fit`; Python twin `autofit.reference.peak_to_backend_spec` | `gl_ratio: 0.3`, FREE |

The server fitted η; `_applyBackendParams` wrote it into `glMix`; nothing
read `glMix` for a Voigt. So every number the page produced for a Voigt
after Run Fit was the η = 0.5 curve evaluated with amplitude, width and
centre fitted for a different mix, and the chart's components did not sum
to the envelope (`fittedY` is the server's).

## 2. Measured before deciding (`scripts/voigt_eta_measure.py`)

The 90 committed targets with a Voigt component (89 U 4f tabs across five
projects and one Cl 2p; 180 Voigt components), each fitted with the page's
settings (Trust-Region, `n_perturb: 3`) both as sent before A03 (η free
from 0.3) and as sent since (η held at 0.5). All 180 fits converged.

| | median | p90 | max |
|---|---:|---:|---:|
| free η of the 180 Voigt components | 46 < 0.01 (pure Gaussian), 17 > 0.99 (pure Lorentzian), 24 within 0.4–0.6 | | |
| DISPLAYED area of a Voigt vs the curve the server fitted | 11.8 % | 19.2 % | 20.1 % (103 of 180 > 10 %) |
| A. displayed vs free-fit area fractions, per target | 0.96 pp | 1.49 pp | 1.60 pp (35 of 90 > 1 pp) |
| B. fixed-η refit vs displayed — what a student sees change | 0.30 pp | 0.46 pp | 1.02 pp (1 of 90 > 1 pp) |
| C. fixed-η refit vs the free fit | 0.93 pp | 1.31 pp | 2.04 pp (34 of 90 > 1 pp) |
| χ²ᵣ fixed / free | 1.095 | 1.186 | 5.4 (fixed LOWER on 11 of 90: the free fit was in a worse minimum) |

Row B is the release-note number: re-fitting a saved U 4f project moves an
area fraction by 0.3 pp at the median and 1.0 pp at most, because the page
already showed the 0.5 curve. Row A is the error that was shipping.

## 3. Contract chosen: fixed η = 0.5 on BOTH sides

`peakToBackendSpec` (and the twin) send `gl_ratio: 0.5, fix_gl_ratio: true`
for a Voigt; `_applyBackendParams` writes `glMix` only for GL / asym-GL (a
Voigt keeps the mix it carries for a later switch to GL); the dropdown says
"Fixed 50/50 … choose GL to fit the mix". The other candidate — make the
page honour the fitted η — would have turned "Voigt" into a GL with a
hidden slider and kept, silently, a shape the student never chose (the
owner's rule from the scattered-starts unit: never substitute an
interpretation because it scored better); 63 of 180 fitted η values on a
bound says the data did not determine the parameter in those fits. The
seed hashes each parameter's effective role, so a Voigt request draws
differently from the old one (test `test_seed_reflects_the_held_eta…`).

Sites changed: `peakToBackendSpec`, `_applyBackendParams`, the Voigt
`<option>` tooltip, `_localFitDetail`, `_LOCALFIT_TOOLTIP`, the fallback
banner, `autofit/reference.py`, `scripts/endpoint_avg_sensitivity.py`,
`scripts/bg_window_worked_example.py`, CLAUDE.md, `tests/js/fit_acceptance.test.js`.

## 4. Two harnesses that would have caught it

- `tests/js/lineshape_roundtrip.test.js` (+ `lineshape_roundtrip_backend.py`):
  for every shape, synthetic data from a truth peak, a perturbed start,
  request built by the PAGE's `peakToBackendSpec`, fitted by
  `fitting.run_fit` (no background, Trust-Region), applied by the page's
  `_applyBackendParams`, then `evalPeakArray` on the fitted grid must equal
  `individual_peaks[].y` within 1e-6 of amplitude. Plus: the Voigt request
  and write-back pins, a linked Voigt pair, a locked GL mix, and the Python
  twin deep-equal to the page's builder for every shape and a link. Run
  against main's page it fails on Voigt (0.93 % of amplitude), the Voigt
  pins and the linked pair; on the branch 10 pass, 2 todo (below).
- `tests/js/lineshape_parity.test.js` section (D): each shape's FREE
  parameters swept across `_make_peak_params`'s bounds (η 0–1, asymmetry
  0–1, DS α 0–0.5 / γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β
  0.1–5 / m 0–499, fwhm 0.1–15), one bridge call per shape.
- `tests/test_voigt_contract.py`: the twin, `run_fit` holding η and
  returning the 0.5 curve, the seed.

## 5. What the sweep found

| shape | result |
|---|---|
| Gaussian, Lorentzian, Voigt (glMix 0 and 100 ignored), GL, asym-GL, DS | ≤ 6.1e-16 of amplitude at every combination |
| DS+G, m < 0.001 (delta branch); LACX, m = 0 | exact |
| LACX, m > 0 | up to 0.89 % of amplitude where the kernel is wide against the peak (m = 50 points on a 0.1 eV peak): the tracked discretisation gap (rounded m + 2m+1 kernel on the page vs continuous m on the server). `todo`, the `caM` clamp unit. |
| DS+G, m ≥ 0.05 | the page's `laCasaXPS` quadrature sizes its step to resolve the Lorentzian core (β/3) and never the Gaussian kernel (σ = m/2.355): at β = 2, m = 0.05 the step is 0.67 eV against σ = 0.021 eV and the curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %; at the schema default (α 0.1, β 0.3, m 0.4) 3.9 %. 0 of 865 committed components use DS+G. `todo`; NOT fixed here (scope) — its own unit: port the server's padded-grid convolution to a grid-aware array evaluator, as `dsgDeltaKernel_array` already does for m < 0.001. |

## 6. The re-measurement (`scripts/local_server_gap.js` → `docs/findings/a03/local_server_gap.json`)

W1's 18 Batch Fit targets of the committed UCl4-graphite project, local
engine vs server from the same scaled start, page semantics on both sides.

| set | max Δcentre | max ΔFWHM | max Δarea | max Δfraction |
|---|---:|---:|---:|---:|
| C 1s, 8 of 9 (W1) | 3.8 meV | 0.50 % | 1.40 % | 0.32 pp |
| C 1s, 8 of 9 (A03) | 3.8 meV | 0.50 % | 1.40 % | 0.32 pp |
| C 1s Scan_4 (findings §2, unchanged) | 41.9 meV | 9.0 % | 99.9 % | 15.1 pp |
| U 4f, 9 (W1) | 39.7 meV | 17.2 % | 20.8 % | 1.4 pp |
| U 4f, 9 (A03) | 28.8 meV | 15.8 % | 8.9 % | 0.77 pp |
| U 4f, the 5 where both engines reach the same minimum (Scan_0/1/2/3/7; χ²ᵣ equal to 2–3 digits) | 4.3 meV | 2.6 % | 2.0 % | 0.12 pp |
| U 4f, the other 4 (Scan_4/5/6/8) | 28.8 meV | 15.8 % | 8.9 % | 0.77 pp |

On the 5 agreeing targets the Voigt satellites match within 2 % — the W1
gap on them (7–21 %) was the η identity and is gone. On the other 4 the
server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
7.9 while the local engine holds it at 8; χ²ᵣ differs by 8–20 % (the local
engine is LOWER on Scan_6: 2.657 vs 2.798, so neither side is the
reference), and the satellites, which share the region with the main
lines, differ by up to 8.9 % in area.

**Decision: the "starting point" designation STAYS.** The residual is the
`caM` clamp (the local engine cannot move m; the page draws it rounded),
the next unit the W1 plan named; the label is reconsidered only on a
re-measurement after it. Wording in the page updated to say so (LA
components and several minima; no longer Voigt).

## 7. Release-note line

Voigt components are now fitted at the fixed 50/50 mix the page has always
drawn; until now Run Fit let their mix vary on the server and the page
reported the 50/50 curve's area under the other mix's parameters (up to
20 % off per component). Re-fitting a saved U 4f project moves an area
fraction by 0.3 pp at the median and 1.0 pp at most. Use GL to fit the mix.

## 8. Verification

- `tests/test_voigt_contract.py` 4 passed; full `pytest tests/` — see §9.
- JS suite: `node --test tests/js/*.test.js` (the directory form does not
  run in this node): see §9.
- Browser check (`browser_check_a03.py`, dev gunicorn :5151 from the
  worktree): the request carries `gl_ratio 0.5, fix_gl_ratio true` for
  both Voigt components; the server returns `vary: false, 0.5`; drawn vs
  fitted curve 1.3e-13 of amplitude for the Voigts (LACX 5.6e-3 — the caM
  rounding); the Results area of a Voigt equals the server curve's to
  0.0000 % (LACX −0.66 %, the same rounding); the chart dataset is the drawn curve; `glMix` unchanged in the
  live model and the saved record; Batch Fit onto U4f Scan_1 converges
  locally; no page errors.

## 9. Codex rounds

(filled in below as they run)
