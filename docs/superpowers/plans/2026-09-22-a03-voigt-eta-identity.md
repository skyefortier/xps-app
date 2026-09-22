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

## 2. Measured before deciding

### 2a. The two requests (`scripts/voigt_eta_measure.py` → `docs/findings/a03/voigt_eta_summary.txt`)

The 90 committed targets with a Voigt component (89 U 4f tabs across five
projects and one Cl 2p; 180 Voigt components; 48 saved models and 42 Batch
Fit starts from `scripts/optimizer_disagreement_targets.js`), each fitted
with the page's settings (Trust-Region, `n_perturb: 3`) under BOTH requests,
constructed explicitly by the script (Codex round 1: it used to take the
target file's own Voigt specs as the "old" arm): before A03 (η free from
0.3) and since (η held at 0.5). All 180 fits converged. These rows use the
SERVER's curves and trapezoidal integration on the fitted grid; they
characterise the two requests, not a screen (that is 2b).

| | median | p90 | max |
|---|---:|---:|---:|
| free η of the 180 Voigt components | 60 < 0.01 (pure Gaussian), 16 > 0.99 (pure Lorentzian), 24 within 0.4–0.6 | | |
| the 0.5 curve under the free fit's parameters (what the page drew) vs the curve the server fitted, per Voigt | 13.9 % | 19.2 % | 20.1 % (116 of 180 > 10 %) |
| A. the same, as area fractions per target | 0.96 pp | 1.48 pp | 1.55 pp (35 of 90 > 1 pp) |
| B. fixed-η refit vs that 0.5 curve | 0.34 pp | 0.54 pp | 1.02 pp (1 of 90 > 1 pp) |
| C. fixed-η refit vs the free fit | 0.93 pp | 1.31 pp | 2.04 pp (33 of 90 > 1 pp) |
| χ²ᵣ fixed / free | 1.09 | 1.19 | 5.4 (fixed LOWER on 10 of 90: the free fit was in a worse minimum) |

Row A is the error that was shipping.

### 2b. What a student sees change (`scripts/voigt_saved_vs_refit.js` → `docs/findings/a03/voigt_saved_vs_refit.json`)

Every committed spectrum tab with a saved fit and a Voigt component (55
tabs across six projects, all converged): the PAGE's area of each saved
peak (`evalPeakArray` over the ROI grid × step, as `_peakArea` — a Voigt
at 0.5, an LA at its rounded m, exactly the Results table) against the
page's area of the same peaks after the server refit under the A03 request
(Trust-Region, the page's `n_perturb: 3`, written back through
`_applyBackendParams`). Grids as the page holds them (Codex round 2): the
saved side on the saved fit's own grid (`fitResult.be`, what Results shows
for a loaded project — 11 of the 55 tabs have a saved grid that differs
from the current ROI), the refit side on the request's grid, rounded as
`uploadToBackend` rounds (energies 4 dp, intensities 2 dp — the rounding
also determines the request seed).

| | median | p90 | max |
|---|---:|---:|---:|
| area fraction, per tab | 0.36 pp | 0.51 pp | 0.69 pp (0 of 55 > 1 pp) |
| a Voigt component's own area | 4.6 % | 7.6 % | 15.3 % |

That is the release-note number.

## 3. Contract chosen: fixed η = 0.5 on BOTH sides

`peakToBackendSpec` (and the twin) send `gl_ratio: 0.5, fix_gl_ratio: true`
for a Voigt; `_applyBackendParams` writes `glMix` only for GL / asym-GL (a
Voigt keeps the mix it carries for a later switch to GL); the dropdown says
"Fixed 50/50 … choose GL to fit the mix". The other candidate — make the
page honour the fitted η — would have turned "Voigt" into a GL with a
hidden slider and kept, silently, a shape the student never chose (the
owner's rule from the scattered-starts unit: never substitute an
interpretation because it scored better); 76 of 180 fitted η values on a
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
7.9 while the local engine holds it at 8, and χ²ᵣ (local/server − 1) is
+9.6 %, +10.1 %, −5.0 % and +12.7 %. Movement in m alone does not
attribute the residual (Codex round 1), so the script has a CONTROL arm:
the server fitted with every LA m HELD at the value the local engine
effectively uses — its start rounded to an integer, as
`laTrueCasaXPS_array` rounds it (Codex round 2) — the one thing the local
engine cannot move.

| target | local χ²ᵣ | server χ²ᵣ, m free | server χ²ᵣ, m held | local vs server, m free (Δcentre / ΔFWHM / Δarea / Δfrac) | local vs server, m held | local χ²ᵣ above the held-m server's |
|---|---:|---:|---:|---|---|---:|
| Scan_4 | 1.970 | 1.798 | 1.870 | 26.6 meV / 5.3 % / 8.3 % / 0.33 pp | 13.4 meV / 3.1 % / 5.3 % / 0.19 pp | +5.4 % |
| Scan_5 | 2.393 | 2.174 | 2.182 | 4.7 meV / 4.3 % / 6.7 % / 0.35 pp | 6.3 meV / 3.5 % / 5.5 % / 0.25 pp | +9.7 % |
| Scan_6 | 2.657 | 2.798 | 2.629 | 28.8 meV / 15.8 % / 8.9 % / 0.77 pp | 3.6 meV / 1.1 % / 1.6 % / 0.07 pp | +1.1 % |
| Scan_8 | 4.656 | 4.129 | 4.117 | 5.7 meV / 5.0 % / 8.3 % / 0.32 pp | 5.8 meV / 5.0 % / 8.2 % / 0.32 pp | +13.1 % |

(The 5 agreeing targets are within 1.6 % of the held-m server's χ²ᵣ and
within 4.0 meV / 1.5 % / 2.1 % / 0.12 pp of it.) So: on Scan_6 the residual
IS the `caM` clamp (holding m on the server closes it to the
agreeing-target envelope). On Scan_5 and Scan_8 holding m changes nothing —
the local engine's descent stops at a χ²ᵣ 10–13 % above the server's from
the same start with the same free parameters: a worse minimum, the
"several minima" case (findings §2 had the mirror image on C 1s Scan_4,
where the local engine found the better one). Scan_4 is in between
(+5.4 %). The residual is therefore two things, and `caM` is the smaller.

**Decision: the "starting point" designation STAYS**, on two grounds now:
the `caM` clamp (one target) and the local engine landing in a worse
minimum than Trust-Region on three of nine U 4f targets. The `caM` clamp
remains the next unit; the worse-minimum finding is recorded in findings
§7 for the local-engine work that follows it. Wording in the page updated
to say so (LA components and several minima; no longer Voigt).

## 7. Release-note line

Voigt components are now fitted at the fixed 50/50 mix the page has always
drawn; until now Run Fit let their mix vary on the server and the page
reported the 50/50 curve's area under the other mix's parameters (up to
20 % off per component). Re-fitting a saved project with Voigt components
moves an area fraction by 0.36 pp at the median and 0.69 pp at most on the
55 committed tabs (a Voigt's own area by 4.6 % at the median, 15 % at
most). Use GL to fit the mix. Also fixed: an asym-GL mix of exactly 0 or a
DS α of exactly 0 was sent to the server as 50 / 0.1, and a locked value
outside the optimiser's search limits (a DS+G m locked at 0) was moved onto
the limit before fitting; such requests now also draw a different
random seed, since the seed hashes the parameters as the fit receives them.

## 8. Verification

- `tests/test_voigt_contract.py` 6 passed; `lineshape_roundtrip.test.js`
  29 passed, 2 todo; full `pytest tests/` and the JS suite (371 tests, 364
  pass, 7 todo — `node --test tests/js/*.test.js`; the directory form does
  not run in this node): see §9.
- Browser check (`browser_check_a03.py`, dev gunicorn :5151 from the
  worktree, re-run after round 1): the request carries `gl_ratio 0.5, fix_gl_ratio true` for
  both Voigt components; the server returns `vary: false, 0.5`; drawn vs
  fitted curve 1.3e-13 of amplitude for the Voigts (LACX 5.6e-3 — the caM
  rounding); the Results area of a Voigt equals the server curve's to
  0.0000 % (LACX −0.66 %, the same rounding); the chart dataset is the drawn curve; `glMix` unchanged in the
  live model and the saved record; Batch Fit onto U4f Scan_1 converges
  locally; no page errors.

## 9. Codex rounds

**Round 1 (`docs/autofit/codex/a03_voigt_eta_verdict_run{A,B}.md`): NO-GO ×2,
no blocker, converging findings.** Fixed:
1. MAJOR — the measurement script took the target file's own Voigt specs as
   the "old" arm, so a target file regenerated with the A03 builder would
   have made both arms identical. Both requests are now constructed
   explicitly; the generator is named correctly (`.js`); re-run (§2a).
2. MAJOR — the release-note number was a server-curve/trapezoid comparison
   of two refits, not the page's saved numbers against the page's refit
   numbers. Replaced by `scripts/voigt_saved_vs_refit.js` (§2b); the old
   rows relabelled as what they are.
3. MAJOR/MINOR — the builder sent an asym-GL mix of 0 as 50 and a DS α of 0
   as 0.1 (`p.glMix || 50`, `p.dsAlpha || 0.1`; the Python twin likewise);
   locked, the server held the substitute and the drawn curve differed from
   the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders
   (only a non-number falls back); the round-trip test now locks every shape
   parameter at its bounds; the sweep's backend parameters now come THROUGH
   `peakToBackendSpec` rather than a mapping of the harness's own.
4. MINOR — the uncertainty panel told a Voigt's user to "unlock the padlock"
   for a mix that has none: it now says the shape fixes the mix and points
   to GL.
5. MINOR — "χ²ᵣ differs by 8–20 %" was wrong (the four are +9.6, +10.1,
   −5.0, +12.7 %), the comment's "24 %" was 20 %, row A's 1.60 was 1.61 (now
   1.55 with the explicit arms); and attributing the whole residual to the
   `caM` clamp was an inference — the control arm (§6) shows it is one
   target of four.

**Round 2 (`a03_voigt_eta_r2_verdict_run{A,B}.md`): NO-GO ×2; round-1
items 1, 3, 4 confirmed closed; found:**
1. MAJOR — the saved side of 2b integrated on the current ROI grid where
   Results uses the saved fit's grid (11 tabs differ; 1.2 % on one area),
   and the refit request bypassed the page's upload rounding (which also
   sets the seed). Both fixed; re-run: median 0.35 → 0.36 pp, max 0.69 pp.
2. MINOR — the control arm held m at the stored fractional value (8.199)
   where the local engine rounds it (8). Now held at the rounded value;
   re-run (table in §6).
3. MINOR — "every shape parameter locked at its bounds" was seven cases.
   Now 18: both bounds of every shape parameter of every shape, the
   convolved shapes where their evaluators are exact. Doing so found a
   FOURTH identity defect: lmfit clips a held value to its bounds, so a
   DS+G with m locked at 0 (the delta-kernel branch the page draws) was
   fitted with m = 0.05, the free-parameter floor — a convolved curve the
   page never drew. `fitting._make_peak_params._set` now widens the limit
   to a held value; pinned in `tests/test_voigt_contract.py`.
4. MINOR — "10–13 %" (the three worse-minimum targets are +5.4, +9.7,
   +13.1 % above the held-m server), "12 %" median in the harness header,
   stale test counts. Corrected. Commit 712e136's message carries the
   superseded round-0 numbers; the merge is fast-forward, so this plan and
   the deploy-log entry are the record.
