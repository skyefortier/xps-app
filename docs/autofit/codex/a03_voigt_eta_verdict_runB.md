OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0c7ac-a811-7290-a610-a2902ff77c4e
--------
user
Review unit A03: branch fix-voigt-eta-identity, git diff main..HEAD (templates/index.html, autofit/reference.py, autofit/parity.py, tests/autofit/battery_common.py, tests/autofit/test_u4f_parity_battery.py, tests/autofit/fixtures/u4f_battery_expected.json (regenerated), tests/js/lineshape_roundtrip.test.js + lineshape_roundtrip_backend.py (new), tests/js/lineshape_parity.test.js section (D) + lineshape_parity_backend.py, tests/test_voigt_contract.py, scripts/voigt_eta_measure.py, scripts/local_server_gap.js, scripts/gen_u4f_battery_fixture.py, two mirror scripts, CLAUDE.md, docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md, docs/findings/2026-09-fit-determinacy.md §7, docs/findings/a03/). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

CONTEXT (read the plan first). A "Voigt" component had two definitions: the page drew, integrated, exported and fitted locally eta = 0.5 (evalPeak; runFitLocal never frees glMix for a Voigt; dropdown "50/50"; CLAUDE.md "fixed eta = 0.5"), while peakToBackendSpec (and its Python twin autofit.reference.peak_to_backend_spec) sent pseudo_voigt_gl with gl_ratio 0.3 FREE. The server fitted eta; _applyBackendParams wrote it into glMix; nothing read glMix for a Voigt. Measured on the 90 committed Voigt targets (180 components): eta ended pure Gaussian on 46, pure Lorentzian on 17; every displayed Voigt area was the 0.5 curve's under the other mix's parameters (median 11.8 % off, max 20.1 %). Owner's brief: "A03: Voigt eta identity, parity-harness sweep over each shape's FREE parameters across their fitted ranges, and re-measure the U 4f gap afterwards. That re-measurement is the test of whether Batch Fit's 'starting point' label can retire."

THE CHANGE
- Contract: eta = 0.5 HELD in the request (gl_ratio 0.5, fix_gl_ratio true) for a Voigt, page and Python twin; _applyBackendParams writes glMix only for GL / asym-GL; dropdown tooltip; the local-fit caveat wording no longer names Voigt. Measured consequence (plan §2): what a student sees change on re-fitting a saved project is median 0.30 pp, max 1.02 pp; the refit vs the old free-eta fit median 0.93 pp, max 2.04 pp, chi2r higher by median 9.5 %. The alternative (make the page honour the fitted eta) was rejected: "Voigt" would become a GL with a hidden slider and silently keep a shape the student did not choose.
- New harness tests/js/lineshape_roundtrip.test.js: for every shape, synthetic data from a truth peak, a perturbed start, request built by the PAGE's peakToBackendSpec, fitted by fitting.run_fit (background none, Trust-Region, n_perturb 0), applied by the page's _applyBackendParams; evalPeakArray on the fitted grid must equal individual_peaks[].y within 1e-6 of amplitude. Fails on main's page for Voigt (0.93 %). Also pins the Python twins peak_to_backend_spec and the NEW apply_backend_params to the page's functions, shape by shape and lock by lock. LACX and DSG_LA are `todo` with the unit that owns each gap.
- Parity harness section (D): each shape's free parameters swept across fitting._make_peak_params's bounds, one bridge call per shape (bridge accepts a list). Found: closed-form shapes exact; LACX m > 0 up to 0.89 % (tracked); DS+G m >= 0.05: the page's laCasaXPS quadrature steps at beta/3, blind to sigma = m/2.355, so at beta 2 / m 0.05 the page curve is 1e52 x amplitude and across the fitted beta/m range the page's area is 23-64 % of the server's. 0 of 865 committed components use DS+G. NOT fixed in A03 (scope); recorded as its own unit; `todo`.
- Re-measurement (scripts/local_server_gap.js, W1's 18 Batch Fit targets, local engine vs server from the same scaled start, page semantics on both sides): U 4f max area gap 20.8 -> 8.9 %, fraction 1.4 -> 0.77 pp; on the 5 of 9 targets where both engines reach the same minimum every component within 4.3 meV / 2.6 % / 2.0 % / 0.12 pp; on the other 4 the server's continuous LA m moved from 8 to 2.7-10.0 while the local engine holds it (chi2r apart 8-20 %, local LOWER on one). Decision: the "starting point" label STAYS; the caM clamp is next.
- U 4f parity battery: all 29 expert fits were saved under the old request; a refit under the new one moves the LACX main line's FWHM by up to 7.7 % and centre by up to 8 meV, so (i) the fixture was regenerated with its committed generator (the documented procedure for a reviewed numerics change) and (ii) stationarity is now measured against a refit FROM the refit (battery_common stationarity="refit"; refit_record(rf, start=rec) applies the record's params through the new apply_backend_params twin). Other regions unchanged.

TRY TO BREAK
a. The contract. Any site that still reads a Voigt's glMix, sends it free, or builds a Voigt with another expectation: Batch Fit's copy, .fit.json import (pseudo_voigt_gl -> GL, unchanged), Find Peaks candidate models, Auto-Fit models, the scattered-starts alternative preview/adoption (runFit({startPeaks})), _STARTS_MODEL_FIELDS (glMix is in the key; inert for a Voigt — a problem?), the request seed (a Voigt request now hashes a held 0.5 — the test pins that it differs from the old request; any OTHER request whose seed changes?), the uncertainty panel (gl_ratio vary false -> "locked" info note for a Voigt? is that wrong/misleading?), save/load of pre-A03 projects (glMix carries 0..100 from the old free fit).
b. Is "fixed 0.5" actually right for the lab's U 4f satellites, or should the unit have honoured the fitted mix? Argue it from the measurements in the plan, not from taste.
c. The round-trip test: does it prove what it claims (page -> server -> page) or only that both sides call the same closed form? Would it catch: a write-back that skips a parameter; a spec builder that sends a wrong default; a lock mishandled; a linked child? Synthetic data with no background — anything the real path does that this bypasses?
d. The sweep: the ranges vs the ACTUAL bounds (a linked peak's DS gamma is 0-1, its ds_g m_gauss min 0.0; LACX m is fixed by default server-side but the page sends fix_m from fixCaM); the batch bridge; the `todo` tests that now pass "as todo" — is anything real hidden under a todo?
e. The battery re-basing: is refit-from-refit a meaningful stationarity property or a tautology? Does regenerating the fixture hide a real numerics regression elsewhere in fitting.py? apply_backend_params: linked peaks (no gate, like the page), lock semantics, the `val()` helper for both param formats.
f. Measurement fairness: local_server_gap.js applies the server's parameters onto the start copy and evaluates with the page's rounded caM on BOTH sides; server bridge runs without n_perturb while the page sends 3. Do the numbers support "the Voigt gap is gone" and "the residual is the caM clamp"? Is "the label STAYS" the right call from these numbers?
g. Docs: CLAUDE.md, the plan, findings §7 and the commit message — every number must match docs/findings/a03/voigt_eta_summary.txt and local_server_gap.json; every claim must match the code.
h. Anything that changes for GL / asym-GL / DS / DSG_LA / LACX requests, or for /api/analyze, or for the local engine.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll read the plan first, then check the contract, test coverage, and measurements against the diff. I’ll keep this read-only and finish with ranked findings and a GO/NO-GO verdict.
exec
/bin/zsh -lc "pwd && rg --files -g 'AGENTS.md' -g '*a03*' -g '*2026-09-22-a03*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md
docs/autofit/codex/a03_voigt_eta_review_prompt.txt
docs/autofit/codex/a03_voigt_eta_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_verdict_runA.md

exec
/bin/zsh -lc 'cat docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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

exec
/bin/zsh -lc "git status --short && git diff --stat main..HEAD && git log -3 --format='%h %s%n%b'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tVc3Rg1k' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-25qluXqL' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_review_prompt.txt
?? docs/autofit/codex/a03_voigt_eta_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-dTBp9yLI' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-eBJRisUh' (errno=Operation not permitted)
 CLAUDE.md                                          |   42 +-
 autofit/parity.py                                  |   23 +-
 autofit/reference.py                               |   45 +-
 docs/findings/2026-09-fit-determinacy.md           |   55 +
 docs/findings/a03/local_server_gap.json            | 2295 ++++++++++++++++++++
 docs/findings/a03/local_server_gap.log             |   18 +
 docs/findings/a03/voigt_eta_summary.txt            |    7 +
 .../plans/2026-09-22-a03-voigt-eta-identity.md     |  146 ++
 scripts/bg_window_worked_example.py                |    2 +-
 scripts/endpoint_avg_sensitivity.py                |    2 +-
 scripts/gen_u4f_battery_fixture.py                 |    5 +-
 scripts/local_server_gap.js                        |   83 +
 scripts/voigt_eta_measure.py                       |  127 ++
 templates/index.html                               |   35 +-
 tests/autofit/battery_common.py                    |   25 +-
 tests/autofit/fixtures/u4f_battery_expected.json   | 1064 ++++-----
 tests/autofit/test_u4f_parity_battery.py           |   13 +-
 tests/js/fit_acceptance.test.js                    |    2 +-
 tests/js/lineshape_parity.test.js                  |   80 +
 tests/js/lineshape_parity_backend.py               |   19 +-
 tests/js/lineshape_roundtrip.test.js               |  205 ++
 tests/js/lineshape_roundtrip_backend.py            |   37 +
 tests/test_voigt_contract.py                       |   67 +
 23 files changed, 3827 insertions(+), 570 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-k598Ljrk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iMRQ5CXA' (errno=Operation not permitted)
712e136 fix(A03): a Voigt is the fixed 50/50 mix on BOTH sides; page->server->page identity test; parameter-range sweep; U 4f gap re-measured
Until now peakToBackendSpec (and its Python twin) sent a "Voigt" as
pseudo_voigt_gl with gl_ratio 0.3 FREE while the page drew, integrated,
exported and fitted locally eta = 0.5. On the 90 committed Voigt targets
(180 components) the server's eta ended at pure Gaussian on 46 and pure
Lorentzian on 17, and every displayed Voigt area was the 0.5 curve's under
the other mix's parameters: median 11.8 % off, max 20.1 %. The request now
sends gl_ratio 0.5 held; _applyBackendParams writes glMix only for GL /
asym-GL; the dropdown says fixed 50/50, use GL to fit the mix. What a
student sees change on re-fitting a saved project: median 0.30 pp, max
1.02 pp (scripts/voigt_eta_measure.py, docs/findings/a03/).

tests/js/lineshape_roundtrip.test.js: for every shape, the request built by
the page's own builder, fitted by fitting.run_fit, applied by the page's own
write-back, then evalPeakArray on the fitted grid must equal
individual_peaks[].y (fails on main's Voigt at 0.93 % of amplitude); pins
the Python twins peak_to_backend_spec and the new apply_backend_params to
the page, shape by shape. Parity harness section (D): each shape's free
parameters swept across the fit's bounds. Found: DS+G's page quadrature
(laCasaXPS) is wrong across its fitted beta/m range (1e52 x amplitude at
beta 2 / m 0.05; 0 of 865 committed components use DS+G) - recorded as its
own unit, not fixed here; LACX m > 0 up to 0.89 % (tracked, caM clamp).

Re-measured (scripts/local_server_gap.js, W1's 18 targets): U 4f max
area gap 20.8 -> 8.9 %, fraction 1.4 -> 0.77 pp; on the 5 of 9 targets
where both engines reach the same minimum every component within 4.3 meV /
2.6 % / 2.0 % / 0.12 pp; the residual is the held caM (server's m moved
2.7-10.0 from 8). The "starting point" designation STAYS; caveat wording
now names LA components and several minima.

U 4f parity battery: the 29 expert fits were saved under the old request;
fixture regenerated (reviewed numerics change) and stationarity measured
against a refit FROM the refit (battery_common stationarity="refit").

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>

c6f358e docs: design rule 'Thresholds on data-scaled quantities fail' (owner, 2026-09-22) recorded in CLAUDE.md; deploy-log entry for step (c) with the release-note line
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>

1eaafd6 docs(required): step (c) final verification — Codex GO x2 (round 4); full suite 983 passed / 7 skipped; JS suite green; browser check (real anchor required, Auto-Fit completes; tampered required:false refused with nothing touched)
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>


exec
/bin/zsh -lc 'git diff main..HEAD -- autofit/reference.py autofit/parity.py tests/autofit/battery_common.py tests/autofit/test_u4f_parity_battery.py templates/index.html' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fTVvzBHn' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Tl6t35Lq' (errno=Operation not permitted)
diff --git a/autofit/parity.py b/autofit/parity.py
index fb09ddd..5187f85 100644
--- a/autofit/parity.py
+++ b/autofit/parity.py
@@ -36,7 +36,7 @@ from fitting import (
     tougaard_background,
     run_fit,
 )
-from .reference import ReferenceFit
+from .reference import ReferenceFit, apply_backend_params, peak_to_backend_spec
 
 
 def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
@@ -184,16 +184,30 @@ def eval_parity_relmax(rf: ReferenceFit) -> float:
     return float(np.max(np.abs(model + bg - fittedY)) / scale)
 
 
-def refit_record(rf: ReferenceFit) -> dict[str, Any]:
+def refit_record(rf: ReferenceFit, start: dict[str, Any] | None = None) -> dict[str, Any]:
     """
     Deterministic seeded refit (leastsq, no perturbation) from the saved
-    parameters.  Returns a serializable record for fixture freezing.
+    parameters.  Returns a serializable record for fixture freezing; each
+    peak also carries ``params`` (every server parameter's fitted value) so
+    the record can be the START of another refit: with ``start`` (a record
+    from this function) the saved peaks are first overwritten with that
+    record's parameters through the page's write-back twin, exactly as the
+    page holds a model after Run Fit.
     """
+    import copy
+    peaks = rf.peaks
+    if start is not None:
+        peaks = copy.deepcopy(rf.peaks)
+        by_id = {str(pk["id"]): pk for pk in start["peaks"]}
+        for p in peaks:
+            pk = by_id.get(str(p["id"]))
+            if pk is not None and pk.get("params"):
+                apply_backend_params(p, pk["params"])
     i0, i1 = rf.bg_indices()
     res = run_fit(
         rf.roi_be,
         rf.roi_intensity,
-        rf.backend_peak_specs(),
+        [peak_to_backend_spec(p, peaks) for p in peaks],
         background_method=rf.bg_method,
         bg_start_idx=i0,
         bg_end_idx=i1,
@@ -209,6 +223,7 @@ def refit_record(rf: ReferenceFit) -> dict[str, Any]:
             "fwhm": par["fwhm"]["value"],
             "amplitude": par["amplitude"]["value"],
             "area": par["area"]["value"],
+            "params": {k: v["value"] for k, v in par.items() if k != "area"},
         })
     return {
         "project": rf.project,
diff --git a/autofit/reference.py b/autofit/reference.py
index fe46d48..2690adb 100644
--- a/autofit/reference.py
+++ b/autofit/reference.py
@@ -101,8 +101,10 @@ def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
     elif shape == "Lorentzian":
         spec["shape"] = "lorentzian"
     elif shape == "Voigt":
+        # A03: the fixed 50/50 mix the page draws (twin of peakToBackendSpec)
         spec["shape"] = "pseudo_voigt_gl"
-        spec["gl_ratio"] = 0.3
+        spec["gl_ratio"] = 0.5
+        spec["fix_gl_ratio"] = True
     elif shape == "GL":
         spec["shape"] = "pseudo_voigt_gl"
         spec["gl_ratio"] = p["glMix"] / 100.0
@@ -150,6 +152,47 @@ def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
     return spec
 
 
+def apply_backend_params(p: dict, par: dict) -> dict:
+    """Write a server component's fitted parameters onto a page peak dict, in
+    place — the twin of the page's ``_applyBackendParams`` (honours the peak's
+    locks; a shape parameter is written only for the shape that reads it, so
+    a Voigt keeps the ``glMix`` it carries for a later switch to GL). ``par``
+    is ``individual_peaks[].params`` (``{name: {"value": …}}``) or a plain
+    ``{name: value}`` map. Pinned to the page's function, shape by shape, by
+    tests/js/lineshape_roundtrip.test.js."""
+    def val(name):
+        v = par[name]
+        return v["value"] if isinstance(v, dict) else v
+    shape = p.get("shape")
+    if "center" in par and not p.get("fixCenter"):
+        p["center"] = val("center")
+    if "amplitude" in par and not p.get("fixAmplitude"):
+        p["amplitude"] = val("amplitude")
+    if "fwhm" in par and not p.get("fixFwhm"):
+        p["fwhm"] = val("fwhm")
+    if "gl_ratio" in par and shape in ("GL", "asym-GL") and not p.get("fixGlMix"):
+        p["glMix"] = val("gl_ratio") * 100
+    if "asymmetry" in par and shape == "asym-GL" and not p.get("fixAsymmetry"):
+        p["asymmetry"] = val("asymmetry")
+    if "alpha" in par and shape == "DS" and not p.get("fixDsAlpha"):
+        p["dsAlpha"] = val("alpha")
+    if "gamma_asym" in par and shape == "DS" and not p.get("fixDsGamma"):
+        p["dsGamma"] = val("gamma_asym")
+    if "alpha" in par and shape == "DSG_LA" and not p.get("fixLaAlpha"):
+        p["laAlpha"] = val("alpha")
+    if "beta" in par and shape == "DSG_LA" and not p.get("fixLaBeta"):
+        p["laBeta"] = val("beta")
+    if "m_gauss" in par and shape == "DSG_LA" and not p.get("fixLaM"):
+        p["laM"] = val("m_gauss")
+    if "alpha" in par and shape == "LACX" and not p.get("fixCaAlpha"):
+        p["caAlpha"] = val("alpha")
+    if "beta" in par and shape == "LACX" and not p.get("fixCaBeta"):
+        p["caBeta"] = val("beta")
+    if "m" in par and shape == "LACX" and not p.get("fixCaM"):
+        p["caM"] = val("m")
+    return p
+
+
 # ─────────────────────────────────────────────────────────────────────────────
 # ReferenceFit — one saved, fitted spectrum tab
 # ─────────────────────────────────────────────────────────────────────────────
diff --git a/templates/index.html b/templates/index.html
index 8393b2c..4fbb066 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -5962,7 +5962,7 @@ function renderPeakForm(p) {
       <select id="pk-shape-${p.id}" class="xps-tip-select" onchange="_switchPeakShape(${p.id}, this.value)">
         <option data-tip="Pure Gaussian. Dominated by instrument broadening. Rarely used alone — most XPS peaks need some Lorentzian character." ${p.shape==='Gaussian'?'selected':''}>Gaussian</option>
         <option data-tip="Pure Lorentzian. Dominated by core-hole lifetime. Rarely used alone — too sharp for most real XPS peaks." ${p.shape==='Lorentzian'?'selected':''}>Lorentzian</option>
-        <option data-tip="50/50 Gaussian-Lorentzian mix. Good default starting point for most insulating and polymeric samples." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
+        <option data-tip="Fixed 50/50 Gaussian-Lorentzian mix (η = 0.5, not fitted). A reasonable default for most insulating and polymeric samples; choose GL to fit the mix." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
         <option value="GL" data-tip="Adjustable Gaussian/Lorentzian ratio. Use when you need control over the peak shape — common for oxides, polymers, and organic materials." ${p.shape==='GL'?'selected':''}>GL pseudo-Voigt (&eta; mixing)</option>
         <option value="asym-GL" data-tip="GL with asymmetric broadening. Use for peaks with vibrational fine structure (e.g., C 1s in polymers) or when one side is broader than the other." ${p.shape==='asym-GL'?'selected':''}>Asymmetric GL</option>
         <option value="DS" data-tip="Asymmetric metallic lineshape with tail toward higher BE. Use for metals and conductive samples (e.g., Au, Cu, Fe metal). Not appropriate for insulators or oxides." ${p.shape==='DS'?'selected':''}>Doniach-&Scaron;unji&#263; (&alpha; + &gamma;)</option>
@@ -6223,8 +6223,16 @@ function peakToBackendSpec(p) {
   } else if (shape === 'Lorentzian') {
     spec.shape = 'lorentzian';
   } else if (shape === 'Voigt') {
+    // A03 (2026-09-22): Voigt IS the fixed 50/50 mix the page draws, exports
+    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
+    // the request sent eta FREE from 0.3, so the server fitted a mix the page
+    // never showed — on the 90 committed Voigt targets 46 of 180 components
+    // went to pure Gaussian and 17 to pure Lorentzian, and every area the page
+    // reported for them was the 0.5 curve's, up to 24 % off the fitted one.
+    // Fixed on both sides; use GL to fit the mix.
     spec.shape = 'pseudo_voigt_gl';
-    spec.gl_ratio = 0.3;
+    spec.gl_ratio = 0.5;
+    spec.fix_gl_ratio = true;
   } else if (shape === 'GL') {
     spec.shape = 'pseudo_voigt_gl';
     spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
@@ -6282,7 +6290,10 @@ function _applyBackendParams(p, par) {
   if (par.center    && !p.fixCenter)    p.center    = par.center.value;
   if (par.amplitude && !p.fixAmplitude) p.amplitude = par.amplitude.value;
   if (par.fwhm      && !p.fixFwhm)     p.fwhm      = par.fwhm.value;
-  if (par.gl_ratio  && !p.fixGlMix)    p.glMix     = par.gl_ratio.value * 100;
+  // glMix is read only by GL / asym-GL; a Voigt's fixed 0.5 (A03) is not a
+  // fitted value and must not overwrite the mix the peak carries for a later
+  // switch to GL.
+  if (par.gl_ratio  && (p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) p.glMix = par.gl_ratio.value * 100;
   if (par.asymmetry && p.shape === 'asym-GL' && !p.fixAsymmetry) p.asymmetry = par.asymmetry.value;
   if (par.alpha && p.shape === 'DS' && !p.fixDsAlpha) p.dsAlpha = par.alpha.value;
   if (par.gamma_asym && p.shape === 'DS' && !p.fixDsGamma) p.dsGamma = par.gamma_asym.value;
@@ -7780,10 +7791,14 @@ function _fitStatLabel(fr) {
 // A LOCAL result is a STARTING POINT, not a reportable result. Measured in
 // unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
 // with Poisson weighting the local engine matches the server on GL-type
-// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) but still differs
-// where the model has Voigt or LA components (server fits the Voigt mix
-// free; caM is integer-held locally) or several minima, and it gives no
-// uncertainties. Unweighted A0-era results differed by more than 100 %.
+// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
+// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
+// wherever the two engines reach the same minimum (5 of 9 committed U 4f
+// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
+// it still differs where an LA component's m moves on the server (held at
+// its start locally: the other 4 U 4f targets, chi2r apart by 8-20 %,
+// satellite areas by up to 8.9 %, 0.77 pp) or the model has several
+// minima, and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
 // Every site that shows, exports or saves a fit result carries the
 // designation, keyed on persisted identity so reloaded results are labelled.
 const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
@@ -7802,7 +7817,7 @@ function _governingProvenance() {
 function _localFitDetail(fr) {
   return _isUnweightedLocal(fr)
     ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
-    : 'It can differ from the server fit for Voigt or LA components, for very weak components (different parameter bounds), or where the model has several minima.';
+    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
 }
 // The designation follows the MODEL, not only a live fit result: parameters
 // imported from a .fit.json that was saved from a local fit are a starting
@@ -11248,7 +11263,7 @@ function _updateROIDisplay(roiRange) {
   el.textContent = `ROI: ${roiRange.min}\u2013${roiRange.max} eV`;
 }
 
-const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for Voigt or LA components or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
+const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
 const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the goodness of fit weighted by data uncertainty. Computed within the ROI range.\n\n\u2022 \u03c7\u00b2 \u2248 1.0 = ideal fit (residuals match expected noise)\n\u2022 \u03c7\u00b2 >> 1 = poor fit or underestimated uncertainties\n\u2022 \u03c7\u00b2 << 1 = possible overfitting or overestimated uncertainties\n\nNote: a low \u03c7\u00b2 does not guarantee a correct model \u2014 always check the R-factor and visually inspect residuals.";
 
 // Wire up custom tooltip for data-xps-tip elements (R-factor, chi-squared, etc.)
@@ -14283,7 +14298,7 @@ document.addEventListener('mousedown', function(e) {
 <div id="localfit-warn-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
   <div class="xps-modal" style="max-width:460px;border-color:var(--amber,#f59e0b)">
     <h3 style="color:var(--amber,#f59e0b)">&#9888; Local fit used (server unreachable) <button class="btn btn-sm" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">&#x2715;</button></h3>
-    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for Voigt or LA components or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
+    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
     <p style="font-size:11px;color:var(--text2);line-height:1.6;margin:0 0 12px"><strong style="color:var(--text)">Possible causes:</strong><br>
     &bull; The server may be offline or restarting<br>
     &bull; The fit request may have timed out<br>
diff --git a/tests/autofit/battery_common.py b/tests/autofit/battery_common.py
index 4c994a7..ceee984 100644
--- a/tests/autofit/battery_common.py
+++ b/tests/autofit/battery_common.py
@@ -78,24 +78,39 @@ def assert_refit_stability_and_fixture(
     center_tol=CENTER_DRIFT_TOL_EV,
     rel_tol=REL_DRIFT_TOL,
     fixture_rtol=FIXTURE_PARAM_RTOL,
+    stationarity="expert",
 ):
+    """stationarity: what the seeded refit must stay at.
+    "expert" — the saved expert fit itself (the fit is a fixed point of
+    today's fitter). "refit" — a refit FROM the refit (the fitter's own fixed
+    point): for a region whose saved fits were made under a request the page
+    no longer sends (U 4f: Voigt satellites fitted with eta free until A03,
+    2026-09-22), the expert's parameters are those of another model and the
+    "expert" base cannot hold; the frozen fixture still pins the refit's
+    numbers."""
     rec = refit_record(rf)
     assert rec["success"], f"{rf.project}/{rf.name}: seeded refit did not converge"
 
-    by_id = {str(p["id"]): p for p in rf.peaks}
-    for pk in rec["peaks"]:
+    if stationarity == "refit":
+        rec2 = refit_record(rf, start=rec)
+        assert rec2["success"], f"{rf.project}/{rf.name}: refit from the refit did not converge"
+        base, moving, base_name = rec["peaks"], rec2["peaks"], "the refit"
+    else:
+        base, moving, base_name = rf.peaks, rec["peaks"], "expert fit"
+    by_id = {str(p["id"]): p for p in base}
+    for pk in moving:
         saved = by_id[str(pk["id"])]
         dc = abs(pk["center"] - saved["center"])
         dfw = abs(pk["fwhm"] - saved["fwhm"]) / max(saved["fwhm"], 1e-9)
         dam = abs(pk["amplitude"] - saved["amplitude"]) / max(abs(saved["amplitude"]), 1e-9)
         assert dc <= center_tol, (
-            f"{rf.name} peak {pk['id']}: center drifted {dc:.4f} eV from expert fit"
+            f"{rf.name} peak {pk['id']}: center drifted {dc:.4f} eV from {base_name}"
         )
         assert dfw <= rel_tol, (
-            f"{rf.name} peak {pk['id']}: fwhm drifted {dfw:.2%} from expert fit"
+            f"{rf.name} peak {pk['id']}: fwhm drifted {dfw:.2%} from {base_name}"
         )
         assert dam <= rel_tol, (
-            f"{rf.name} peak {pk['id']}: amplitude drifted {dam:.2%} from expert fit"
+            f"{rf.name} peak {pk['id']}: amplitude drifted {dam:.2%} from {base_name}"
         )
 
     exp = expected[(rf.project, rf.name)]
diff --git a/tests/autofit/test_u4f_parity_battery.py b/tests/autofit/test_u4f_parity_battery.py
index fd2f2d2..e18df2a 100644
--- a/tests/autofit/test_u4f_parity_battery.py
+++ b/tests/autofit/test_u4f_parity_battery.py
@@ -6,6 +6,16 @@ battery_common.py).
 
 Regenerate the fixture ONLY for reviewed numerics changes:
     venv/bin/python scripts/gen_u4f_battery_fixture.py
+
+A03 (2026-09-22): the page now sends a Voigt with eta HELD at 0.5 (the mix
+it has always drawn); the 29 expert U 4f fits were saved under the old
+request (eta free from 0.3, ending at pure Gaussian or pure Lorentzian on
+most satellites), so their saved parameters belong to another model and a
+refit under today's request moves the LACX main line's width by up to 7.7 %
+and its centre by up to 8 meV (the satellites' tails changed). The fixture
+was regenerated for that reviewed change, and stationarity is measured
+against a refit FROM the refit (battery_common, stationarity="refit"): the
+fitter's own fixed point, not the pre-A03 save.
 """
 
 import pytest
@@ -48,4 +58,5 @@ def test_eval_parity(rf):
 @pytest.mark.parametrize("rf", _FITS, ids=_IDS)
 def test_refit_stability_and_fixture(rf):
     bc.assert_refit_stability_and_fixture(rf, _EXPECTED,
-                                          fixture_rtol=FIXTURE_RTOL)
+                                          fixture_rtol=FIXTURE_RTOL,
+                                          stationarity="refit")

exec
/bin/zsh -lc "ls -la /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md 2>/dev/null; rg --files tests/js docs/findings/a03 scripts | rg '(roundtrip|parity_backend|voigt_eta|local_server_gap|gen_u4f|a03)'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
tests/js/local_lm_server_parity_backend.py
tests/js/shape_switch_roundtrip.test.js
docs/findings/a03/local_server_gap.log
docs/findings/a03/local_server_gap.json
docs/findings/a03/voigt_eta_summary.txt
tests/js/lineshape_parity_backend.py
tests/js/lineshape_roundtrip.test.js
tests/js/lineshape_roundtrip_backend.py
scripts/gen_u4f_battery_fixture.py
scripts/local_server_gap.js
scripts/voigt_eta_measure.py

exec
/bin/zsh -lc 'cat tests/js/lineshape_roundtrip.test.js tests/js/lineshape_roundtrip_backend.py tests/test_voigt_contract.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
// Page → server → page identity (A03, 2026-09-22).
//
// The parity harness (lineshape_parity.test.js) proves the two EVALUATORS
// agree for the same parameters. It cannot see a request that asks the
// server to fit a parameter the page never draws: until A03 a "Voigt" was
// sent as pseudo_voigt_gl with gl_ratio FREE from 0.3 while evalPeak drew
// η = 0.5, so every chart component, area, percentage and export for a
// Voigt was the 0.5 curve under parameters fitted for another mix (on the
// 90 committed Voigt targets: displayed areas 12 % off the fitted curve at
// the median, 20 % at worst; 46 of 180 components had gone to pure
// Gaussian, 17 to pure Lorentzian). This test closes that class: for every
// shape, build the request with the PAGE's own peakToBackendSpec, fit it
// on the server (fitting.run_fit, no background, Trust-Region), apply the
// result with the page's own _applyBackendParams, and require the curve the
// page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
// server FITTED (individual_peaks[].y).
//
// Two shapes carry a known drawn-vs-fitted gap and are marked todo with the
// unit that owns it: LACX (the page sends m free and draws it ROUNDED —
// the caM clamp unit) and DSG_LA (the page's quadrature — see the parity
// harness's section (D)).
const { test } = require('node:test');
const assert = require('node:assert');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
  'evalPeakArray', 'getPeak', 'peakToBackendSpec', '_applyBackendParams'];
const state = { peaks: [] };
const env = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, peakToBackendSpec, _applyBackendParams };')(state);

function findPython() {
  for (const c of [process.env.XPS_PYTHON, path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3']) {
    if (c && fs.existsSync(c)) return c;
  }
  return 'python3';
}
const PYTHON = findPython();
const BRIDGE = path.join(__dirname, 'lineshape_roundtrip_backend.py');
function bridge(payload) {
  return JSON.parse(execFileSync(PYTHON, [BRIDGE, REPO_ROOT], { input: JSON.stringify(payload), encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

// A realistic BE grid, descending like a real acquisition: 12 eV, 0.05 eV step.
const CENTER = 391.8;
const GRID = Array.from({ length: 241 }, (_, i) => CENTER + 6 - 0.05 * i);
// Deterministic noise (LCG), so the fit is a real fit and the test is repeatable.
function noise(seed, n, scale) {
  let s = seed >>> 0; const out = [];
  for (let i = 0; i < n; i++) { s = (1664525 * s + 1013904223) >>> 0; out.push(scale * ((s / 4294967296) - 0.5)); }
  return out;
}
function fullPeak(over) {
  return {
    id: 1, name: 'P', color: '#000', visible: true, center: CENTER, amplitude: 12000, fwhm: 1.6,
    shape: 'GL', glMix: 30, asymmetry: 0.0, dsAlpha: 0.1, dsGamma: 0.0,
    laAlpha: 0.10, laBeta: 0.3, laM: 0.4, caAlpha: 1.0, caBeta: 1.0, caM: 50,
    linked: null, linkOffset: 0, linkRatio: 1, isChargeReference: false,
    fixCenter: false, fixFwhm: false, fixAmplitude: false, fixGlMix: false, fixAsymmetry: false,
    fixDsAlpha: false, fixDsGamma: false, fixLaAlpha: false, fixLaBeta: false, fixLaM: false,
    fixCaAlpha: false, fixCaBeta: false, fixCaM: false,
    ...over,
  };
}
// truth → data; start → what the student placed (the fit has to move every free parameter)
const CASES = {
  'Gaussian':   { truth: { shape: 'Gaussian' }, start: {} },
  'Lorentzian': { truth: { shape: 'Lorentzian' }, start: {} },
  'Voigt':      { truth: { shape: 'Voigt' }, start: { glMix: 90 } },                       // glMix must play no part
  'GL':         { truth: { shape: 'GL', glMix: 72 }, start: { glMix: 30 } },
  'asym-GL':    { truth: { shape: 'asym-GL', glMix: 40, asymmetry: 0.35 }, start: { glMix: 30, asymmetry: 0.05 } },
  'DS':         { truth: { shape: 'DS', dsAlpha: 0.18, dsGamma: 0.3 }, start: { dsAlpha: 0.05, dsGamma: 0.1 } },
  'DSG_LA':     { truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.8 }, start: { laAlpha: 0.10, laBeta: 0.3, laM: 0.4 } },
  'LACX':       { truth: { shape: 'LACX', caAlpha: 1.6, caBeta: 0.7, caM: 20 }, start: { caAlpha: 1.0, caBeta: 1.0, caM: 30 } },
};
const TIGHT_TOL = 1e-6;      // of amplitude; both curves are the same closed form on the same grid
const KNOWN_GAP = {
  'DSG_LA': 'DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit',
  'LACX':   'LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit',
};

function roundTrip(shape, { truth, start, extraPeaks = [] }) {
  const truthPeaks = [fullPeak(truth), ...extraPeaks.map(e => fullPeak(e.truth))];
  state.peaks = truthPeaks;
  const counts = GRID.map(() => 0);
  for (const tp of truthPeaks) { const y = env.evalPeakArray(GRID, tp); for (let i = 0; i < GRID.length; i++) counts[i] += y[i]; }
  const nz = noise(0x5eed + shape.length, GRID.length, 0.01 * truthPeaks[0].amplitude);
  for (let i = 0; i < GRID.length; i++) counts[i] = Math.max(0, counts[i] + 40 + nz[i]);
  const startPeaks = [fullPeak({ ...truth, ...start, amplitude: 0.8 * 12000, center: CENTER + 0.12, fwhm: 1.6 * 1.2 }),
    ...extraPeaks.map(e => fullPeak({ ...e.truth, ...e.start }))];
  state.peaks = startPeaks;                       // peakToBackendSpec resolves links through getPeak(state.peaks)
  const specs = startPeaks.map(p => env.peakToBackendSpec(p));
  const res = bridge({ energy: GRID, counts, specs }).fit;
  assert.equal(res.success, true, `${shape}: the server fit must converge for the identity to be tested`);
  for (const ip of res.individual_peaks) {
    const p = startPeaks.find(q => String(q.id) === String(ip.id));
    env._applyBackendParams(p, ip.params);
    p._backendParams = ip.params;
  }
  return { res, peaks: startPeaks, specs };
}
function maxRelDiff(a, b, amp) { let m = 0; for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i])); return m / amp; }

for (const [shape, c] of Object.entries(CASES)) {
  const opts = KNOWN_GAP[shape] ? { todo: KNOWN_GAP[shape] } : undefined;
  test(`page → server → page: what the page draws after applying the result IS the curve the server fitted — ${shape}`, opts, () => {
    const { res, peaks } = roundTrip(shape, c);
    const ip = res.individual_peaks[0];
    const drawn = env.evalPeakArray(res.energy, peaks[0]);
    const rel = maxRelDiff(drawn, ip.y, peaks[0].amplitude);
    assert.ok(rel < TIGHT_TOL, `${shape}: drawn vs fitted curve differ by ${(rel * 100).toExponential(3)} % of amplitude`);
  });
}

test('Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve', () => {
  const p = fullPeak({ shape: 'Voigt', glMix: 90, fixGlMix: false });
  state.peaks = [p];
  const spec = env.peakToBackendSpec(p);
  assert.equal(spec.shape, 'pseudo_voigt_gl');
  assert.equal(spec.gl_ratio, 0.5, 'the request carries the mix the page draws');
  assert.equal(spec.fix_gl_ratio, true, 'and asks the server not to fit it');
  const { res, peaks } = roundTrip('Voigt', CASES.Voigt);
  const gl = res.individual_peaks[0].params.gl_ratio;
  assert.equal(gl.vary, false, 'the server held η');
  assert.equal(gl.value, 0.5);
  assert.equal(peaks[0].glMix, 90, 'a Voigt keeps the glMix it carries for a later switch to GL; the fixed 0.5 is not written back');
  assert.ok(maxRelDiff(env.evalPeakArray(res.energy, peaks[0]), res.individual_peaks[0].y, peaks[0].amplitude) < TIGHT_TOL);
});

test('a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)', () => {
  const child = { truth: { id: 2, shape: 'Voigt', linked: 1, linkOffset: -10.9, linkRatio: 0.75, center: CENTER - 10.9, amplitude: 9000 }, start: { amplitude: 9000 * 0.8 } };
  const { res, peaks } = roundTrip('Voigt', { ...CASES.Voigt, extraPeaks: [child] });
  assert.equal(res.individual_peaks.length, 2);
  for (const ip of res.individual_peaks) {
    const p = peaks.find(q => String(q.id) === String(ip.id));
    const rel = maxRelDiff(env.evalPeakArray(res.energy, p), ip.y, p.amplitude);
    assert.ok(rel < TIGHT_TOL, `peak ${ip.id}: drawn vs fitted ${(rel * 100).toExponential(3)} %`);
  }
  const ipChild = res.individual_peaks.find(ip => String(ip.id) === '2');
  assert.equal(ipChild.params.gl_ratio.value, 0.5);
  assert.ok(ipChild.params.gl_ratio.expr, 'the child’s η is an expression on the parent');
});

test('a locked GL mix is sent locked, held by the server and drawn at the locked value', () => {
  const { res, peaks, specs } = roundTrip('GL', { truth: { shape: 'GL', glMix: 72 }, start: { glMix: 30, fixGlMix: true } });
  assert.equal(specs[0].fix_gl_ratio, true);
  assert.equal(res.individual_peaks[0].params.gl_ratio.vary, false);
  assert.equal(peaks[0].glMix, 30, 'the lock is honoured on write-back');
  assert.ok(maxRelDiff(env.evalPeakArray(res.energy, peaks[0]), res.individual_peaks[0].y, peaks[0].amplitude) < TIGHT_TOL);
});

// The Python twin (autofit.reference.peak_to_backend_spec) is what the local
// engine's parity test and the measurement scripts use to build requests. It
// must build the request the page builds, for every shape and for a link.
test('autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape', () => {
  const peaks = [
    ...Object.entries(CASES).map(([shape, c], i) => fullPeak({ ...c.truth, id: i + 1, name: shape })),
    fullPeak({ id: 99, name: 'child', shape: 'Voigt', linked: 3, linkOffset: -10.9, linkRatio: 0.75, center: CENTER - 10.9 }),
    fullPeak({ id: 100, name: 'auto', shape: 'asym-GL', _afAsymMin: 0.02, _afAsymMax: 0.6 }),
  ];
  state.peaks = peaks;
  const js = peaks.map(p => env.peakToBackendSpec(p));
  const py = bridge({ twin_peaks: peaks }).twin_specs;
  assert.equal(py.length, js.length);
  for (let i = 0; i < js.length; i++) {
    assert.deepStrictEqual(py[i], js[i], `peak ${peaks[i].name}: Python twin and page builder differ`);
  }
});

// The write-back twin (autofit.reference.apply_backend_params, used by the
// U 4f battery to refit from a refit) must write exactly what the page's
// _applyBackendParams writes: every shape, every lock, a Voigt's glMix kept.
test('autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock', () => {
  const PAR = { center: 391.55, amplitude: 9876.5, fwhm: 1.91, gl_ratio: 0.81, asymmetry: 0.44, alpha: 0.27, gamma_asym: 0.9, beta: 0.66, m_gauss: 1.7, m: 23.4 };
  const params = Object.fromEntries(Object.entries(PAR).map(([k, v]) => [k, { value: v, stderr: null, vary: true, expr: null, min: null, max: null }]));
  const items = [];
  for (const [shape, c] of Object.entries(CASES)) {
    items.push({ peak: fullPeak({ ...c.truth, id: items.length + 1 }), params });
    items.push({ peak: fullPeak({ ...c.truth, id: items.length + 1, fixCenter: true, fixFwhm: true, fixAmplitude: true, fixGlMix: true, fixAsymmetry: true,
      fixDsAlpha: true, fixDsGamma: true, fixLaAlpha: true, fixLaBeta: true, fixLaM: true, fixCaAlpha: true, fixCaBeta: true, fixCaM: true }), params });
  }
  const py = bridge({ twin_apply: items }).twin_applied;
  items.forEach((it, i) => {
    const js = { ...it.peak };
    env._applyBackendParams(js, it.params);
    assert.deepStrictEqual(py[i], js, `peak ${it.peak.shape}${it.peak.fixCenter ? ' (locked)' : ''}: Python twin and page write-back differ`);
  });
});
#!/usr/bin/env python3
"""Bridge for tests/js/lineshape_roundtrip.test.js (A03, 2026-09-22).

stdin: {"energy": [...], "counts": [...], "specs": [<peakToBackendSpec output>...],
        "twin_peaks": [<frontend peak objects>] (optional),
        "twin_apply": [{"peak": <frontend peak>, "params": <individual_peaks[].params>}] (optional)}
argv[1]: repo root.

Runs fitting.run_fit on the specs EXACTLY as the page built them (no
background, Trust-Region, no restarts) and returns what /api/fit would:
the fitted grid, every component's curve and parameters. With
"twin_peaks" it also returns autofit.reference.peak_to_backend_spec's
output for those peaks, so the test can pin the Python twin to the page's
builder.
"""
import json
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import fitting  # noqa: E402
from autofit.reference import apply_backend_params, peak_to_backend_spec  # noqa: E402

d = json.load(sys.stdin)
out = {}
if d.get("specs"):
    res = fitting.run_fit(np.asarray(d["energy"], float), np.asarray(d["counts"], float), d["specs"],
                          background_method="none", fit_kws={"method": "least_squares"}, n_perturb=0)
    out["fit"] = {"success": bool(res["success"]), "energy": res["energy"],
                  "individual_peaks": [{"id": ip["id"], "y": ip["y"], "params": ip["params"]} for ip in res["individual_peaks"]]}
if d.get("twin_peaks"):
    out["twin_specs"] = [peak_to_backend_spec(p, d["twin_peaks"]) for p in d["twin_peaks"]]
if d.get("twin_apply"):
    # [{"peak": <page peak>, "params": <individual_peaks[].params>}] -> the peaks after the write-back twin
    out["twin_applied"] = [apply_backend_params(dict(item["peak"]), item["params"]) for item in d["twin_apply"]]
print(json.dumps(out))
"""A03 (2026-09-22): a "Voigt" component is the fixed 50/50 mix everywhere.

The page draws, integrates, exports and fits locally with eta = 0.5
(evalPeak; runFitLocal never frees glMix for a Voigt). Until A03 the
request built by peakToBackendSpec — and its Python twin
autofit.reference.peak_to_backend_spec — sent pseudo_voigt_gl with
gl_ratio FREE from 0.3, so the server fitted a mix the page never showed.
These tests pin the twin and what run_fit does with the request.
"""
import numpy as np
import pytest

import fitting
from autofit.reference import peak_to_backend_spec


def _peak(**over):
    p = {"id": 1, "name": "sat", "shape": "Voigt", "center": 386.5, "amplitude": 3000.0, "fwhm": 1.4,
         "glMix": 90, "fixGlMix": False}
    p.update(over)
    return p


def test_twin_sends_voigt_as_fixed_half_mix():
    spec = peak_to_backend_spec(_peak(), [_peak()])
    assert spec["shape"] == "pseudo_voigt_gl"
    assert spec["gl_ratio"] == 0.5
    assert spec["fix_gl_ratio"] is True
    # the page's glMix (kept for a later switch to GL) plays no part
    assert peak_to_backend_spec(_peak(glMix=5), [_peak(glMix=5)])["gl_ratio"] == 0.5


def test_twin_still_sends_gl_mix_free():
    spec = peak_to_backend_spec(_peak(shape="GL", glMix=72), [_peak(shape="GL", glMix=72)])
    assert spec["gl_ratio"] == pytest.approx(0.72)
    assert spec["fix_gl_ratio"] is False


def test_run_fit_holds_eta_and_returns_the_half_mix_curve():
    x = np.arange(392.0, 380.0, -0.05)
    truth = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=3000.0, center=386.5, fwhm=1.4, gl_ratio=0.5)
    rng = np.random.default_rng(3)
    y = np.maximum(truth + rng.normal(0, 8, x.size), 0)   # no offset: the request carries no background
    start = _peak(center=386.65, amplitude=2400.0, fwhm=1.7)
    spec = peak_to_backend_spec(start, [start])
    res = fitting.run_fit(x, y, [spec], background_method="none", fit_kws={"method": "least_squares"})
    assert res["success"] is True
    ip = res["individual_peaks"][0]
    gl = ip["params"]["gl_ratio"]
    assert gl["vary"] is False and gl["value"] == 0.5 and not gl["stderr"]   # lmfit reports 0.0 or None for a held parameter
    q = ip["params"]
    drawn = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](np.asarray(res["energy"]), amplitude=q["amplitude"]["value"],
                                                    center=q["center"]["value"], fwhm=q["fwhm"]["value"], gl_ratio=0.5)
    np.testing.assert_allclose(np.asarray(ip["y"]), drawn, rtol=0, atol=1e-9 * 3000.0)
    assert abs(q["center"]["value"] - 386.5) < 0.02 and abs(q["fwhm"]["value"] - 1.4) < 0.03


def test_seed_reflects_the_held_eta_not_the_old_free_start():
    """The request seed hashes each parameter's EFFECTIVE role: a held eta of
    0.5 and a free eta from 0.3 are different requests and draw differently."""
    x = np.arange(392.0, 380.0, -0.05)
    y = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=3000.0, center=386.5, fwhm=1.4, gl_ratio=0.5) + 20.0
    spec = peak_to_backend_spec(_peak(), [_peak()])
    old = dict(spec, gl_ratio=0.3, fix_gl_ratio=False)
    s_new = fitting.run_fit(x, y, [spec], background_method="none", n_perturb=1)["random_seed"]
    s_old = fitting.run_fit(x, y, [old], background_method="none", n_perturb=1)["random_seed"]
    assert s_new != s_old

exec
/bin/zsh -lc "rg -n 'AGENTS|Review|review|test|venv' CLAUDE.md | head -65; rg -n 'Voigt|glMix|fix_gl_ratio|_STARTS_MODEL_FIELDS' templates/index.html autofit fitting.py | head -180; cat docs/findings/a03/voigt_eta_summary.txt; cat tests/js/local_lm_server_parity_backend.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
27:tests/                    # pytest suite (focused on LA + DS+G correctness)
31:venv/                     # virtualenv (do not commit)
49:| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
51:| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
121:it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
126:shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
146:anchor (answer: a scale-free F test), then two tolerances on that F test
200:were actually being fit against, due to a pre-existing preview/backend
338:(in review each such no-op edit moved an area fraction by 15–45 pp
347:makes (observed through Levenberg-Marquardt) are pinned by tests; numpy does not promise the same `default_rng` stream across
371:(`tests/test_fit_reproducibility.py` docstring). Do not patch scipy
383:second thing (a reviewer tried a deterministic perturbation base: identical
416:the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
417:history-preview overlay, on a copy) and "Use this solution": explicit, one
435:the comparison no longer applies, nothing can be previewed or applied, an
436:open alternative preview is dropped (`_dropStaleAltPreview`), and
564:not detected (a refit without the component is the test; step (c) does it
601:| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
649:`tests/js/fixtures/autofit_anchor.json`. SCOPE: it answers "do the data
688:  the un-committed target file, not a test); the round-6 reproduction (two symmetric GL
803:tests/test_la_continuous_m.py   # LA(α,β,m) continuity across integer-m kernel widths
804:tests/test_la_short_input.py    # LA edge cases on very-short input arrays
805:tests/test_mixed_ds_lacx_e2e.py # End-to-end: a fit with both DS+G and CasaXPS LA peaks
808:Run via `pytest tests/`.
814:Typical regions for hand-testing:
fitting.py:65:    Pseudo‑Voigt as a linear combination of Gaussian and Lorentzian.
fitting.py:84:    Asymmetric GL pseudo‑Voigt with independent asymmetry parameter.
fitting.py:929:             vary=not spec.get("fix_gl_ratio", False))
fitting.py:1136:    ``fix_gl_ratio`` the page still sends for a Gaussian, stale shape
templates/index.html:3995:function pseudoVoigt(x, center, fwhm, eta) {
templates/index.html:4000:function asymmGL(x, center, fwhm, glMix, alpha) {
templates/index.html:4001:  // Asymmetric GL: piecewise TWO-CONSTANT-WIDTH pseudo-Voigt, mirroring
templates/index.html:4010:  return pseudoVoigt(x, center, fwhmEff, glMix / 100);
templates/index.html:4155:    y = pseudoVoigt(x, center, fwhm, p.glMix / 100);
templates/index.html:4157:    y = asymmGL(x, center, fwhm, p.glMix, p.asymmetry);
templates/index.html:4162:  } else if (p.shape === 'Voigt') {
templates/index.html:4163:    y = pseudoVoigt(x, center, fwhm, 0.5);
templates/index.html:5029:    glMix: 30,
templates/index.html:5080:// Note: glMix uses the frontend 0-100 slider scale (= backend gl_ratio × 100).
templates/index.html:5087:  'Voigt':      {},
templates/index.html:5088:  'GL':         { glMix: 30, fixGlMix: false },
templates/index.html:5089:  'asym-GL':    { glMix: 30, fixGlMix: false, asymmetry: 0.0, fixAsymmetry: false },
templates/index.html:5765:  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
templates/index.html:5965:        <option data-tip="Fixed 50/50 Gaussian-Lorentzian mix (η = 0.5, not fitted). A reasonable default for most insulating and polymeric samples; choose GL to fit the mix." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
templates/index.html:5966:        <option value="GL" data-tip="Adjustable Gaussian/Lorentzian ratio. Use when you need control over the peak shape — common for oxides, polymers, and organic materials." ${p.shape==='GL'?'selected':''}>GL pseudo-Voigt (&eta; mixing)</option>
templates/index.html:6028:        <label data-xps-tip="Empirical asymmetry parameter that broadens the high-BE side of the peak: fwhm_right = fwhm × (1 + asymmetry). This is NOT the same as the Doniach-Šunjić singularity index α from metallic-screening literature — it's an empirical width-broadening factor specific to this app's asymmetric pseudo-Voigt formulation.">Asymmetry factor <span style="color:var(--text3);font-size:9px">0=symmetric &middot; empirical broadening factor, not DS &alpha;</span>
templates/index.html:6037:          <input type="range" min="0" max="100" step="1" value="${p.glMix}"
templates/index.html:6038:            oninput="updatePeakParam(${p.id},'glMix',parseFloat(this.value));document.getElementById('glmix-${p.id}').textContent=this.value+'%'">
templates/index.html:6039:          <span id="glmix-${p.id}" style="font-family:var(--mono);font-size:11px;min-width:42px">${(+p.glMix).toFixed(3)}%</span>
templates/index.html:6049:          <input type="range" min="0" max="100" step="1" value="${p.glMix}"
templates/index.html:6050:            oninput="updatePeakParam(${p.id},'glMix',parseFloat(this.value));document.getElementById('glmix-${p.id}').textContent=this.value+'%'">
templates/index.html:6051:          <span id="glmix-${p.id}" style="font-family:var(--mono);font-size:11px;min-width:42px">${(+p.glMix).toFixed(3)}%</span>
templates/index.html:6218:    fix_gl_ratio: !!p.fixGlMix
templates/index.html:6225:  } else if (shape === 'Voigt') {
templates/index.html:6226:    // A03 (2026-09-22): Voigt IS the fixed 50/50 mix the page draws, exports
templates/index.html:6229:    // never showed — on the 90 committed Voigt targets 46 of 180 components
templates/index.html:6235:    spec.fix_gl_ratio = true;
templates/index.html:6238:    spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
templates/index.html:6241:    spec.gl_ratio = (p.glMix || 50) / 100;
templates/index.html:6293:  // glMix is read only by GL / asym-GL; a Voigt's fixed 0.5 (A03) is not a
templates/index.html:6296:  if (par.gl_ratio  && (p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) p.glMix = par.gl_ratio.value * 100;
templates/index.html:6630:    glMix: 30,            // η = 30% Lorentzian, free
templates/index.html:6640:  // All four use pseudo-Voigt (shape='GL') with eta free; the satellite
templates/index.html:6656:      glMix: 30,
templates/index.html:6674:      glMix: 30,
templates/index.html:6690:      glMix: 30,
templates/index.html:7369:const _STARTS_MODEL_FIELDS = ['id', 'shape', 'center', 'fwhm', 'amplitude', 'glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
templates/index.html:7376:    p: (peaks || []).map(q => _STARTS_MODEL_FIELDS.map(k => (q[k] === undefined ? null : q[k]))),
templates/index.html:7719:      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
templates/index.html:7795:// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
templates/index.html:7949:        freeParams.push(p.glMix); paramMap.push({id: p.id, param: 'glMix'});
templates/index.html:7982:    if (param === 'glMix')        return Math.max(0, Math.min(100, v));
templates/index.html:7994:  const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
templates/index.html:11068:    case 'asym-GL': return { gl: p.glMix ?? '', alpha: '',        beta: '',       m: '' };
templates/index.html:11072:    default:        return { gl: '',            alpha: '',        beta: '',       m: '' };  // Gaussian/Lorentzian/Voigt
templates/index.html:11318:  const nameMap = { center: 'center', fwhm: 'fwhm', fwhm_l: 'fwhm', amplitude: 'amplitude', gl_ratio: 'glMix' };
templates/index.html:14790:  pseudo_voigt_gl: 'Voigt-type (GL)', asymmetric_gl: 'Asymmetric GL',
templates/index.html:15667:      o.glMix = 100 * (p.gl_ratio ?? 0.3); o.asymmetry = p.asymmetry ?? 0.1; break;
templates/index.html:15674:    default:                o.shape = 'GL'; o.glMix = 100 * (p.gl_ratio ?? 0.3);
autofit/reference.py:96:        "fix_gl_ratio": bool(p.get("fixGlMix")),
autofit/reference.py:103:    elif shape == "Voigt":
autofit/reference.py:107:        spec["fix_gl_ratio"] = True
autofit/reference.py:110:        spec["gl_ratio"] = p["glMix"] / 100.0
autofit/reference.py:113:        spec["gl_ratio"] = (p.get("glMix") or 50) / 100.0
autofit/reference.py:159:    a Voigt keeps the ``glMix`` it carries for a later switch to GL). ``par``
autofit/reference.py:174:        p["glMix"] = val("gl_ratio") * 100
autofit/engine.py:589:            # ONLY for the pseudo-Voigt with a shared mixing parameter —
autofit/engine.py:614:                    "share_parent_params (the pseudo-Voigt area factor "
autofit/engine.py:798:        # Olivero & Longbothum 1977 Voigt-FWHM approximation (0.02%).
autofit/regions/u4f.py:19:  Voigt pair (sat7/2 offset-linked to the main; sat5/2 linked to sat7/2 at
autofit/regions/c1s.py:144:# bracket the expert reference fits (asymmetry ≈ 0.10, glMix ≈ 0.08–0.5)
autofit/regions/c1s.py:220:                       "reference fits (asymmetry ≈ 0.10, glMix ≈ "
targets 90, both fits converged 90
free eta of 180 Voigt components: 46 at 0 (pure Gaussian), 17 at 1 (pure Lorentzian), 24 within 0.4–0.6
per-Voigt-component DISPLAYED area vs the fitted curve (%): median 11.82, p90 19.18, max 20.11; > 10 % on 103 of 180; displayed high (eta < 0.5) 114, low 66
A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.49, max 1.61; > 1 pp on 35 targets
B. fixed refit vs displayed (what changes on screen), max |delta| pp: median 0.30, p90 0.46, max 1.02; > 1 pp on 1 targets
C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 34 targets
chi2r fixed/free: median 1.09, p90 1.18, max 5.39; fixed lower on 11 targets (the free fit in a worse minimum)
"""Bridge for tests/js/local_lm_descent.test.js: run the SERVER fit (fitting.run_fit,
Poisson weights, Trust-Region) from the same scaled starting model the local
engine received, so the JS test can pin local-vs-server parity (unit W1).
stdin: {be, inten, peaks (frontend peak objects), ui}; argv[1]: repo root.
"""
import json
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import fitting  # noqa: E402
from autofit.reference import peak_to_backend_spec  # noqa: E402

d = json.load(sys.stdin)
x = np.asarray(d["be"], float)
y = np.asarray(d["inten"], float)
ui = d["ui"]
specs = [peak_to_backend_spec(p, d["peaks"]) for p in d["peaks"]]
lo, hi = sorted([float(ui["bgStart"]), float(ui["bgEnd"])])
idx = [i for i, b in enumerate(x) if lo <= b <= hi]
res = fitting.run_fit(x, y, specs, background_method=ui["bgType"], bg_start_idx=idx[0], bg_end_idx=idx[-1] + 1,
                      endpoint_avg=int(ui.get("endpointAvg") or 1), fit_kws={"method": "least_squares"})
print(json.dumps({"success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"],
                  "peaks": [{k: v["value"] for k, v in ip["params"].items()} for ip in res["individual_peaks"]]}))

exec
/bin/zsh -lc 'git diff main..HEAD -- tests/js/lineshape_parity.test.js tests/js/lineshape_parity_backend.py; cat scripts/local_server_gap.js scripts/voigt_eta_measure.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-w9pmPF81' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-nvmBmDVq' (errno=Operation not permitted)
diff --git a/tests/js/lineshape_parity.test.js b/tests/js/lineshape_parity.test.js
index d9ca8ec..e5c0264 100644
--- a/tests/js/lineshape_parity.test.js
+++ b/tests/js/lineshape_parity.test.js
@@ -296,3 +296,83 @@ test('(C) evalPeak() has no direct callers outside evalPeakArray()', () => {
     'instead (see file header: evalPeak() silently ignores Gaussian convolution for LACX with m>0, which evalPeakArray() ' +
     'handles correctly).');
 });
+
+// ── (D) A03 (2026-09-22): sweep each shape's FREE parameters across the ──
+// ranges the FIT can reach. Every test above evaluates ONE base peak per
+// shape; a divergence that only appears at the edge of a bound (η = 0 or 1,
+// α at 0.5, a Gaussian kernel narrower than the quadrature step) was
+// invisible to it. The ranges below are fitting.py `_make_peak_params`'s
+// bounds for a free peak (gl_ratio 0–1, asymmetry 0–1, DS α 0–0.5 and
+// γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β 0.1–5 / m 0–499,
+// fwhm 0.1–15); a lock or a link cannot take a parameter outside them.
+// One interpreter start per shape (the bridge accepts a list of specs).
+//
+// Measured on the first run of this sweep (worktree fix-voigt-eta-identity):
+//   Gaussian, Lorentzian, Voigt, GL, asym-GL, DS: ≤ 6.1e-16 everywhere.
+//   LACX, m = 0: exact. LACX, m > 0: up to 0.89 % of amplitude — the tracked
+//     kernel-discretisation gap (continuous m + ceil(3.5σ) kernel on the
+//     server vs rounded m + 2m+1 kernel on the page), largest where the
+//     kernel is wide against the peak (m = 50 points on a 0.1 eV peak).
+//   DSG_LA, m < 0.001: the delta branch, exact. DSG_LA, m ≥ 0.05: the page's
+//     quadrature (laCasaXPS) sizes its step to resolve the Lorentzian core
+//     (β/3) but NOT the Gaussian kernel (σ = m/2.355): at β = 2, m = 0.05
+//     the step is 0.67 eV against σ = 0.021 eV, the kernel weights sample
+//     nothing, and the curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the
+//     page's area is 23 % of the server's; at β = 2, m = 0.4 (the default
+//     m) 64 %. Zero committed components use DS+G (0 of 865), so no saved
+//     figure is affected today; it is the fit range nonetheless. Its own
+//     unit (the file header already names it); recorded in
+//     docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md.
+function backendEvalMany(specs) {
+  const input = JSON.stringify(specs);
+  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
+  return JSON.parse(out);
+}
+function combos(ranges) {
+  let out = [{}];
+  for (const k of Object.keys(ranges)) out = out.flatMap(o => ranges[k].map(v => ({ ...o, [k]: v })));
+  return out;
+}
+const FWHM_RANGE = [0.1, 1.83, 15];
+const SWEEP = {
+  'Gaussian':   { fwhm: FWHM_RANGE },
+  'Lorentzian': { fwhm: FWHM_RANGE },
+  'Voigt':      { fwhm: FWHM_RANGE, glMix: [0, 100] },          // glMix must be IGNORED: Voigt is η = 0.5 (A03)
+  'GL':         { glMix: [0, 25, 50, 75, 100], fwhm: FWHM_RANGE },
+  'asym-GL':    { glMix: [0, 50, 100], asymmetry: [0, 0.5, 1], fwhm: FWHM_RANGE },
+  'DS':         { dsAlpha: [0, 0.25, 0.5], dsGamma: [0, 1, 5], fwhm: FWHM_RANGE },
+  'DSG_LA (delta kernel)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0, 0.0009] },
+  'LACX (m = 0)': { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0], fwhm: FWHM_RANGE },
+};
+const SWEEP_KNOWN_GAP = {
+  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.05, 0.4, 2, 4] },
+  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
+};
+function sweepShape(label) { return label.split(' ')[0]; }
+function runSweep(label, ranges) {
+  const shape = sweepShape(label);
+  const cases = combos(ranges).map(c => ({ c, p: { ...basePeak(shape), ...c } }));
+  const specs = cases.map(k => { const b = BACKEND[shape](k.p); return { ...b, x: grid(k.p.center) }; });
+  const beYs = backendEvalMany(specs);
+  return cases.map((k, i) => {
+    const x = grid(k.p.center);
+    const rel = maxRelDiff(evalPeakArray(x, k.p), beYs[i], k.p.amplitude);
+    return { c: k.c, rel };
+  }).sort((a, b) => b.rel - a.rel);
+}
+for (const [label, ranges] of Object.entries(SWEEP)) {
+  test(`(D) sweep across the fitted range: ${label}`, () => {
+    const worst = runSweep(label, ranges);
+    assert.ok(worst[0].rel < TIGHT_TOL,
+      `${label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} parameter combinations diverge; worst ` +
+      `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
+  });
+}
+for (const [label, ranges] of Object.entries(SWEEP_KNOWN_GAP)) {
+  test(`(D) sweep across the fitted range: ${label} — KNOWN GAP`, { todo: 'convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)' }, () => {
+    const worst = runSweep(label, ranges);
+    assert.ok(worst[0].rel < TIGHT_TOL,
+      `${label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} parameter combinations diverge; worst ` +
+      `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
+  });
+}
diff --git a/tests/js/lineshape_parity_backend.py b/tests/js/lineshape_parity_backend.py
index 2473772..17861eb 100644
--- a/tests/js/lineshape_parity_backend.py
+++ b/tests/js/lineshape_parity_backend.py
@@ -3,7 +3,8 @@
 
 Reads a JSON spec from stdin:
     {"shape": "<key in fitting._SHAPE_FUNCS>", "params": {...}, "x": [...]}
-Writes a JSON array of y-values to stdout.
+or a JSON list of such specs.
+Writes a JSON array of y-values (or a list of arrays) to stdout.
 
 Calls fitting.py's OWN registered shape functions (_SHAPE_FUNCS) directly —
 never a reimplementation — so the JS parity test is always comparing against
@@ -19,12 +20,20 @@ sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspa
 from fitting import _SHAPE_FUNCS  # noqa: E402
 
 
-def main() -> None:
-    spec = json.load(sys.stdin)
+def _eval(spec: dict) -> list[float]:
     x = np.array(spec["x"], dtype=float)
     fn = _SHAPE_FUNCS[spec["shape"]]
-    y = fn(x, **spec["params"])
-    json.dump([float(v) for v in y], sys.stdout)
+    return [float(v) for v in fn(x, **spec["params"])]
+
+
+def main() -> None:
+    spec = json.load(sys.stdin)
+    # A list of specs (the A03 parameter sweep) is answered with a list of
+    # curves in one interpreter start; a single spec as before.
+    if isinstance(spec, list):
+        json.dump([_eval(s) for s in spec], sys.stdout)
+    else:
+        json.dump(_eval(spec), sys.stdout)
 
 
 if __name__ == "__main__":
#!/usr/bin/env node
// Local engine vs server from the SAME scaled start on the committed
// UCl4-graphite project's Batch Fit targets (unit W1's methodology,
// 2026-09-18; re-run for A03, 2026-09-22 — the test of whether Batch Fit's
// "starting point" label can retire). Every C1s Scan_N and U4f Scan_N tab is
// a target; the source is the scan the student fitted ('C1s Scan' / 'U4f
// Scan'); the start is the source's model with amplitudes scaled to the
// target's maximum (what runPropagation does); both engines fit that start
// on the same background (the page's computeBackgroundCore; the server
// recomputes its own from the same settings). Differences are evaluated with
// the PAGE's semantics — the server's parameters written onto a copy of the
// start with _applyBackendParams, areas as _peakArea (evalPeakArray over the
// ROI grid × step) — so the comparison is about parameters, not about which
// side integrated. Usage: node scripts/local_server_gap.js [out.json]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
  throw new Error('unbalanced ' + name);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_applyBackendParams'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
function makeEnv() {
  const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const f = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, _applyBackendParams };');
  return { ...f(document, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => new Array(be.length).fill(0)), state };
}
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const PROJECT = path.join(ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 1 << 26 }));
function target(env, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  return { be, inten, bg, bgSub: inten.map((v, i) => v - bg[i]), ui, start: cloned };
}
const area = (env, be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return env.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), regions: {} };
for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
  const names = tabs.filter(t => new RegExp('^' + sourceName.replace(' ', ' ') + '_\\d+$').test(t.name)).map(t => t.name);
  out.regions[region] = [];
  for (const name of names) {
    const env = makeEnv(); const T = target(env, sourceName, name);
    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
    const srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: T.start, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    const serverPeaks = JSON.parse(JSON.stringify(T.start));
    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(serverPeaks[i], par); });
    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p));
    const tL = aL.reduce((s, v) => s + v, 0), tS = aS.reduce((s, v) => s + v, 0);
    const comps = localPeaks.map((p, i) => ({ name: p.name, shape: p.shape, linked: !!p.linked,
      dCenter_meV: 1000 * (p.center - serverPeaks[i].center), dFwhm_pct: 100 * (p.fwhm / serverPeaks[i].fwhm - 1),
      dArea_pct: aS[i] ? 100 * (aL[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aL[i] / tL - aS[i] / tS),
      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM } }));
    const mx = f => Math.max(...comps.map(c => Math.abs(c[f]) || 0));
    out.regions[region].push({ target: name, local_success: loc.success, local_chi2r: env.state.fitResult && env.state.fitResult.chiReduced, server_success: srv.success, server_chi2r: srv.chi2r,
      max_dCenter_meV: mx('dCenter_meV'), max_dFwhm_pct: mx('dFwhm_pct'), max_dArea_pct: mx('dArea_pct'), max_dFrac_pp: mx('dFrac_pp'), comps });
    console.error(region, name, 'local', loc.success, (env.state.fitResult || {}).chiReduced && env.state.fitResult.chiReduced.toFixed(3), 'server', srv.success, srv.chi2r.toFixed(3), 'max Δcentre', mx('dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('dFwhm_pct').toFixed(2), '%, Δarea', mx('dArea_pct').toFixed(2), '%, Δfrac', mx('dFrac_pp').toFixed(2), 'pp');
  }
}
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/local_server_gap.json'), JSON.stringify(out, null, 1));
#!/usr/bin/env python3
"""A03 (2026-09-22): what the free-eta Voigt request did, on the committed targets.

Until A03 the page sent a "Voigt" component as pseudo_voigt_gl with gl_ratio
FREE from 0.3 while it drew, integrated and exported eta = 0.5. For every
committed target with a Voigt component this script fits the request BOTH
ways with the page's settings (Trust-Region, n_perturb 3) — (free) as sent
before A03, (fixed) eta held at 0.5 as sent since — and compares three
things per target:
  A. what the page DISPLAYED (the 0.5 curve under the free fit's parameters)
     against the free fit's own curve — the reporting error that shipped;
  B. the fixed fit against what the page displayed — what a student SEES
     change on re-fitting a saved project;
  C. the fixed fit against the free fit.

Usage:
  python scripts/voigt_eta_measure.py targets.json out_dir shard n_shards   # one shard
  python scripts/voigt_eta_measure.py --summary out_dir                     # the numbers
targets.json is the optimizer-disagreement target file (uncommitted; built by
scripts/optimizer_disagreement_targets.py from the committed projects).
"""
import copy
import glob
import json
import os
import statistics as st
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fitting  # noqa: E402

warnings.filterwarnings("ignore")


def _pack(r):
    return {"success": r["success"], "chi2r": r["statistics"]["reduced_chi_square"], "energy": r["energy"],
            "peaks": [{"id": ip["id"], "y": ip["y"], "params": {k: v.get("value") for k, v in ip["params"].items()}}
                      for ip in r["individual_peaks"]]}


def measure(targets_path, out_dir, shard, n_shards):
    targets = json.load(open(targets_path))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"shard{shard}.jsonl"), "w") as out:
        for k, t in enumerate(targets):
            if k % n_shards != shard:
                continue
            vidx = [i for i, sh in enumerate(t["shapes"]) if sh == "Voigt"]
            if not vidx:
                continue
            b = t["background"]
            kw = dict(background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
                      endpoint_avg=b["endpoint_avg"], n_perturb=3, fit_kws={"method": "least_squares"})
            x = np.asarray(t["be"], float)
            y = np.round(np.asarray(t["inten"], float), 2)   # the upload rounds to 2 dp
            free = copy.deepcopy(t["specs"])                  # as sent before A03: gl_ratio 0.3, free
            fixed = copy.deepcopy(t["specs"])
            for i in vidx:
                fixed[i]["gl_ratio"] = 0.5
                fixed[i]["fix_gl_ratio"] = True
            rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"],
                   "voigt_ids": [str(t["specs"][i]["id"]) for i in vidx]}
            for lab, specs in (("free", free), ("fixed", fixed)):
                try:
                    rec[lab] = _pack(fitting.run_fit(x, y, specs, **kw))
                except Exception as e:  # noqa: BLE001 — a failed fit is a row, not a crash
                    rec[lab] = {"error": str(e)[:160]}
            out.write(json.dumps(rec) + "\n")
            out.flush()


def summary(out_dir):
    recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(out_dir, "shard*.jsonl"))) for l in open(f)]
    ok = [r for r in recs if "peaks" in r["free"] and "peaks" in r["fixed"] and r["free"]["success"] and r["fixed"]["success"]]
    print(f"targets {len(recs)}, both fits converged {len(ok)}")
    area = lambda x, y: float(abs(np.trapezoid(y, x)))  # noqa: E731
    dA, dB, dC, comp = [], [], [], []
    etas = []
    chi_ratio = []
    for r in ok:
        x = np.asarray(r["free"]["energy"])
        vids = set(r["voigt_ids"])
        a_free, a_disp = [], []
        for pk in r["free"]["peaks"]:
            a = area(x, np.asarray(pk["y"]))
            a_free.append(a)
            if str(pk["id"]) in vids:
                q = pk["params"]
                etas.append(q["gl_ratio"])
                yd = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=q["amplitude"], center=q["center"], fwhm=q["fwhm"], gl_ratio=0.5)
                ad = area(x, yd)
                a_disp.append(ad)
                if a > 0:
                    comp.append(100 * (ad - a) / a)
            else:
                a_disp.append(a)
        a_fix = [area(x, np.asarray(pk["y"])) for pk in r["fixed"]["peaks"]]
        frac = lambda A: [100 * v / sum(A) for v in A]  # noqa: E731
        Ff, Fd, Fx = frac(a_free), frac(a_disp), frac(a_fix)
        dA.append(max(abs(a - b) for a, b in zip(Fd, Ff)))
        dB.append(max(abs(a - b) for a, b in zip(Fx, Fd)))
        dC.append(max(abs(a - b) for a, b in zip(Fx, Ff)))
        chi_ratio.append(r["fixed"]["chi2r"] / r["free"]["chi2r"])

    def q(v):
        v = sorted(v)
        return f"median {st.median(v):.2f}, p90 {v[int(0.9 * len(v))]:.2f}, max {v[-1]:.2f}"

    print(f"free eta of {len(etas)} Voigt components: {sum(e < 0.01 for e in etas)} at 0 (pure Gaussian), "
          f"{sum(e > 0.99 for e in etas)} at 1 (pure Lorentzian), {sum(0.4 <= e <= 0.6 for e in etas)} within 0.4–0.6")
    e = [abs(c) for c in comp]
    print(f"per-Voigt-component DISPLAYED area vs the fitted curve (%): {q(e)}; > 10 % on {sum(v > 10 for v in e)} of {len(e)}; "
          f"displayed high (eta < 0.5) {sum(c > 0 for c in comp)}, low {sum(c < 0 for c in comp)}")
    print(f"A. displayed vs free-fit fractions, max |delta| pp per target: {q(dA)}; > 1 pp on {sum(v > 1 for v in dA)} targets")
    print(f"B. fixed refit vs displayed (what changes on screen), max |delta| pp: {q(dB)}; > 1 pp on {sum(v > 1 for v in dB)} targets")
    print(f"C. fixed refit vs free fit, max |delta| pp: {q(dC)}; > 1 pp on {sum(v > 1 for v in dC)} targets")
    print(f"chi2r fixed/free: {q(chi_ratio)}; fixed lower on {sum(v < 1 for v in chi_ratio)} targets (the free fit in a worse minimum)")


if __name__ == "__main__":
    if sys.argv[1] == "--summary":
        summary(sys.argv[2])
    else:
        measure(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))

codex
The production change is confined to the Voigt request and write-back paths; I haven’t found a change to the local fitter or backend equations. I’m checking two evidence risks next: whether the measurement script can reproduce the old free-η baseline, and whether the sweep actually covers the claimed parameter bounds.
exec
/bin/zsh -lc "sed -n '298,390p' tests/js/lineshape_parity.test.js; cat tests/js/lineshape_parity_backend.py; cat scripts/optimizer_disagreement_targets.py; cat scripts/local_server_gap.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
});

// ── (D) A03 (2026-09-22): sweep each shape's FREE parameters across the ──
// ranges the FIT can reach. Every test above evaluates ONE base peak per
// shape; a divergence that only appears at the edge of a bound (η = 0 or 1,
// α at 0.5, a Gaussian kernel narrower than the quadrature step) was
// invisible to it. The ranges below are fitting.py `_make_peak_params`'s
// bounds for a free peak (gl_ratio 0–1, asymmetry 0–1, DS α 0–0.5 and
// γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β 0.1–5 / m 0–499,
// fwhm 0.1–15); a lock or a link cannot take a parameter outside them.
// One interpreter start per shape (the bridge accepts a list of specs).
//
// Measured on the first run of this sweep (worktree fix-voigt-eta-identity):
//   Gaussian, Lorentzian, Voigt, GL, asym-GL, DS: ≤ 6.1e-16 everywhere.
//   LACX, m = 0: exact. LACX, m > 0: up to 0.89 % of amplitude — the tracked
//     kernel-discretisation gap (continuous m + ceil(3.5σ) kernel on the
//     server vs rounded m + 2m+1 kernel on the page), largest where the
//     kernel is wide against the peak (m = 50 points on a 0.1 eV peak).
//   DSG_LA, m < 0.001: the delta branch, exact. DSG_LA, m ≥ 0.05: the page's
//     quadrature (laCasaXPS) sizes its step to resolve the Lorentzian core
//     (β/3) but NOT the Gaussian kernel (σ = m/2.355): at β = 2, m = 0.05
//     the step is 0.67 eV against σ = 0.021 eV, the kernel weights sample
//     nothing, and the curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the
//     page's area is 23 % of the server's; at β = 2, m = 0.4 (the default
//     m) 64 %. Zero committed components use DS+G (0 of 865), so no saved
//     figure is affected today; it is the fit range nonetheless. Its own
//     unit (the file header already names it); recorded in
//     docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md.
function backendEvalMany(specs) {
  const input = JSON.stringify(specs);
  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
  return JSON.parse(out);
}
function combos(ranges) {
  let out = [{}];
  for (const k of Object.keys(ranges)) out = out.flatMap(o => ranges[k].map(v => ({ ...o, [k]: v })));
  return out;
}
const FWHM_RANGE = [0.1, 1.83, 15];
const SWEEP = {
  'Gaussian':   { fwhm: FWHM_RANGE },
  'Lorentzian': { fwhm: FWHM_RANGE },
  'Voigt':      { fwhm: FWHM_RANGE, glMix: [0, 100] },          // glMix must be IGNORED: Voigt is η = 0.5 (A03)
  'GL':         { glMix: [0, 25, 50, 75, 100], fwhm: FWHM_RANGE },
  'asym-GL':    { glMix: [0, 50, 100], asymmetry: [0, 0.5, 1], fwhm: FWHM_RANGE },
  'DS':         { dsAlpha: [0, 0.25, 0.5], dsGamma: [0, 1, 5], fwhm: FWHM_RANGE },
  'DSG_LA (delta kernel)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0, 0.0009] },
  'LACX (m = 0)': { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0], fwhm: FWHM_RANGE },
};
const SWEEP_KNOWN_GAP = {
  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.05, 0.4, 2, 4] },
  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
};
function sweepShape(label) { return label.split(' ')[0]; }
function runSweep(label, ranges) {
  const shape = sweepShape(label);
  const cases = combos(ranges).map(c => ({ c, p: { ...basePeak(shape), ...c } }));
  const specs = cases.map(k => { const b = BACKEND[shape](k.p); return { ...b, x: grid(k.p.center) }; });
  const beYs = backendEvalMany(specs);
  return cases.map((k, i) => {
    const x = grid(k.p.center);
    const rel = maxRelDiff(evalPeakArray(x, k.p), beYs[i], k.p.amplitude);
    return { c: k.c, rel };
  }).sort((a, b) => b.rel - a.rel);
}
for (const [label, ranges] of Object.entries(SWEEP)) {
  test(`(D) sweep across the fitted range: ${label}`, () => {
    const worst = runSweep(label, ranges);
    assert.ok(worst[0].rel < TIGHT_TOL,
      `${label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} parameter combinations diverge; worst ` +
      `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
  });
}
for (const [label, ranges] of Object.entries(SWEEP_KNOWN_GAP)) {
  test(`(D) sweep across the fitted range: ${label} — KNOWN GAP`, { todo: 'convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)' }, () => {
    const worst = runSweep(label, ranges);
    assert.ok(worst[0].rel < TIGHT_TOL,
      `${label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} parameter combinations diverge; worst ` +
      `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
  });
}
#!/usr/bin/env python3
"""Backend-shape evaluator bridge for tests/js/lineshape_parity.test.js.

Reads a JSON spec from stdin:
    {"shape": "<key in fitting._SHAPE_FUNCS>", "params": {...}, "x": [...]}
or a JSON list of such specs.
Writes a JSON array of y-values (or a list of arrays) to stdout.

Calls fitting.py's OWN registered shape functions (_SHAPE_FUNCS) directly —
never a reimplementation — so the JS parity test is always comparing against
whatever the backend actually ships, with no fixture staleness risk.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from fitting import _SHAPE_FUNCS  # noqa: E402


def _eval(spec: dict) -> list[float]:
    x = np.array(spec["x"], dtype=float)
    fn = _SHAPE_FUNCS[spec["shape"]]
    return [float(v) for v in fn(x, **spec["params"])]


def main() -> None:
    spec = json.load(sys.stdin)
    # A list of specs (the A03 parameter sweep) is answered with a list of
    # curves in one interpreter start; a single spec as before.
    if isinstance(spec, list):
        json.dump([_eval(s) for s in spec], sys.stdout)
    else:
        json.dump(_eval(spec), sys.stdout)


if __name__ == "__main__":
    main()
cat: scripts/optimizer_disagreement_targets.py: No such file or directory
#!/usr/bin/env node
// Local engine vs server from the SAME scaled start on the committed
// UCl4-graphite project's Batch Fit targets (unit W1's methodology,
// 2026-09-18; re-run for A03, 2026-09-22 — the test of whether Batch Fit's
// "starting point" label can retire). Every C1s Scan_N and U4f Scan_N tab is
// a target; the source is the scan the student fitted ('C1s Scan' / 'U4f
// Scan'); the start is the source's model with amplitudes scaled to the
// target's maximum (what runPropagation does); both engines fit that start
// on the same background (the page's computeBackgroundCore; the server
// recomputes its own from the same settings). Differences are evaluated with
// the PAGE's semantics — the server's parameters written onto a copy of the
// start with _applyBackendParams, areas as _peakArea (evalPeakArray over the
// ROI grid × step) — so the comparison is about parameters, not about which
// side integrated. Usage: node scripts/local_server_gap.js [out.json]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
  throw new Error('unbalanced ' + name);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_applyBackendParams'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
function makeEnv() {
  const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const f = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, _applyBackendParams };');
  return { ...f(document, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => new Array(be.length).fill(0)), state };
}
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const PROJECT = path.join(ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 1 << 26 }));
function target(env, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  return { be, inten, bg, bgSub: inten.map((v, i) => v - bg[i]), ui, start: cloned };
}
const area = (env, be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return env.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), regions: {} };
for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
  const names = tabs.filter(t => new RegExp('^' + sourceName.replace(' ', ' ') + '_\\d+$').test(t.name)).map(t => t.name);
  out.regions[region] = [];
  for (const name of names) {
    const env = makeEnv(); const T = target(env, sourceName, name);
    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
    const srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: T.start, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    const serverPeaks = JSON.parse(JSON.stringify(T.start));
    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(serverPeaks[i], par); });
    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p));
    const tL = aL.reduce((s, v) => s + v, 0), tS = aS.reduce((s, v) => s + v, 0);
    const comps = localPeaks.map((p, i) => ({ name: p.name, shape: p.shape, linked: !!p.linked,
      dCenter_meV: 1000 * (p.center - serverPeaks[i].center), dFwhm_pct: 100 * (p.fwhm / serverPeaks[i].fwhm - 1),
      dArea_pct: aS[i] ? 100 * (aL[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aL[i] / tL - aS[i] / tS),
      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM } }));
    const mx = f => Math.max(...comps.map(c => Math.abs(c[f]) || 0));
    out.regions[region].push({ target: name, local_success: loc.success, local_chi2r: env.state.fitResult && env.state.fitResult.chiReduced, server_success: srv.success, server_chi2r: srv.chi2r,
      max_dCenter_meV: mx('dCenter_meV'), max_dFwhm_pct: mx('dFwhm_pct'), max_dArea_pct: mx('dArea_pct'), max_dFrac_pp: mx('dFrac_pp'), comps });
    console.error(region, name, 'local', loc.success, (env.state.fitResult || {}).chiReduced && env.state.fitResult.chiReduced.toFixed(3), 'server', srv.success, srv.chi2r.toFixed(3), 'max Δcentre', mx('dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('dFwhm_pct').toFixed(2), '%, Δarea', mx('dArea_pct').toFixed(2), '%, Δfrac', mx('dFrac_pp').toFixed(2), 'pp');
  }
}
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/local_server_gap.json'), JSON.stringify(out, null, 1));

exec
/bin/zsh -lc "sed -n '895,1075p' fitting.py; sed -n '6178,6295p' templates/index.html; sed -n '70,153p' autofit/reference.py; git diff main..HEAD -- CLAUDE.md docs/findings/2026-09-fit-determinacy.md scripts/gen_u4f_battery_fixture.py scripts/bg_window_worked_example.py scripts/endpoint_avg_sensitivity.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
            _set("beta",    spec.get("beta",    0.3),  expr=f"{m_prefix}beta"    if fix else None, min_=0.05, max_=2.0)
            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
        if shape == "la_casaxps":
            fix = spec.get("fix_fwhm", True)
            _set("alpha", spec.get("alpha", 1.0),
                 expr=f"{m_prefix}alpha" if fix else None,
                 min_=0.1, max_=5.0)
            _set("beta",  spec.get("beta",  1.0),
                 expr=f"{m_prefix}beta" if fix else None,
                 min_=0.1, max_=5.0)
            _set("m",     spec.get("m",    50.0),
                 expr=f"{m_prefix}m" if fix else None,
                 min_=0.0, max_=499.0)
        return p

    # Free (master or unconstrained) peak
    # Non-DS+G peaks (satellites, etc.) get a default ±2 eV constraint to prevent
    # the optimizer from drifting to physically unreasonable positions.
    c_min = spec.get("center_min")
    c_max = spec.get("center_max")
    if shape != "ds_g" and c_min is None:
        c_min = center - 2.0
    if shape != "ds_g" and c_max is None:
        c_max = center + 2.0
    _set("center", center, min_=c_min, max_=c_max, vary=not spec.get("fix_center", False))
    _set("amplitude", amp,
         min_=spec.get("amplitude_min", 0.0), max_=spec.get("amplitude_max"),
         vary=not spec.get("fix_amplitude", False))
    _set("fwhm", fwhm,
         min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0),
         vary=not spec.get("fix_fwhm", False))

    if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
        _set("gl_ratio", spec.get("gl_ratio", 0.3), min_=0.0, max_=1.0,
             vary=not spec.get("fix_gl_ratio", False))
    if shape == "asymmetric_gl":
        _set("asymmetry", asymmetry,
             min_=spec.get("asymmetry_min", 0.0),
             max_=spec.get("asymmetry_max", 1.0),
             vary=not spec.get("fix_asymmetry", False))
    if shape == "doniach_sunjic":
        _set("alpha", spec.get("alpha", 0.1), min_=0.0, max_=0.5,
             vary=not spec.get("fix_alpha", False))
        _set("gamma_asym", spec.get("gamma_asym", 0.0), min_=0.0, max_=5.0,
             vary=not spec.get("fix_gamma_asym", False))
    if shape == "ds_g":
        _set("alpha",   spec.get("alpha",   0.10), min_=0.0,  max_=0.49,
             vary=not spec.get("fix_alpha", False))
        _set("beta",    spec.get("beta",    0.3),  min_=0.05, max_=2.0,
             vary=not spec.get("fix_beta", False))
        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0,
             vary=not spec.get("fix_m_gauss", False))
    if shape == "la_casaxps":
        _set("alpha", spec.get("alpha", 1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_alpha", False))
        _set("beta",  spec.get("beta",  1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_beta", False))
        _set("m",     spec.get("m",    50.0), min_=0.0, max_=499.0,
             vary=not spec.get("fix_m", True))

    return p


def _finite_search_box(params: Parameters, x: np.ndarray,
                       y_sub: np.ndarray) -> dict[str, dict[str, float]]:
    """Give every freely varying parameter a finite box, in place.

    lmfit's ``differential_evolution`` samples its population from the
    parameter bounds and refuses to run when any varying parameter has an
    open one. The page sends ``amplitude_min: 0`` and no ``amplitude_max``,
    and a free DS+G centre has no default window, so without this every
    ordinary request for that method failed (HTTP 422). Only open sides of
    freely varying parameters are closed; fixed and expression-constrained
    parameters, and bounds the request did set, are left alone.

    The box is a SEARCH limit, not a constraint the request made: an
    amplitude reaches max(10 x the largest |background-subtracted
    intensity|, 2 x |start|, 1) (both signs when the request leaves the
    floor open too; the page never does), a centre the fitted energy range.
    A component centred outside a narrowed ROI can need far more than the
    visible intensity, and a box can shape an answer that lies nowhere near
    its sides, so ``_search_then_refine`` refines every boxed search under
    the request's own bounds.

    Returns ``{name: {side: width}}`` for the sides it generated (``width``
    is the extent it gave that side).
    """
    xf = np.asarray(x, float)
    yf = np.asarray(y_sub, float)
    xf, yf = xf[np.isfinite(xf)], yf[np.isfinite(yf)]
    if xf.size == 0 or yf.size == 0:
        raise ValueError("differential_evolution needs finite energy and intensity values")
    x_lo, x_hi = float(xf.min()), float(xf.max())
    span = (x_hi - x_lo) or 1.0
    y_top = float(np.max(np.abs(yf)))
    generated: dict[str, dict[str, float]] = {}
    for name, par in params.items():
        if not par.vary or par.expr is not None:
            continue
        open_min, open_max = not np.isfinite(par.min), not np.isfinite(par.max)
        if not (open_min or open_max):
            continue
        if name.endswith("_amplitude"):
            width = max(10.0 * y_top, 2.0 * abs(par.value), 1.0)
            lo, hi = -width, width
        elif name.endswith("_center"):
            width = span
            lo, hi = min(x_lo, par.value), max(x_hi, par.value)
        else:
            raise ValueError(
                f"differential_evolution needs finite bounds for '{name}'")
        new_min = lo if open_min else par.min
        new_max = hi if open_max else par.max
        # A bound the request did set can sit at or beyond the generated
        # side (centre_min = 300 on a 280-290 eV ROI): keep a real interval.
        if open_max and new_max <= new_min:
            new_max = new_min + width
        if open_min and new_min >= new_max:
            new_min = new_max - width
        par.set(min=new_min, max=new_max)
        generated[name] = {side: width for side, is_open in (("min", open_min), ("max", open_max)) if is_open}
    return generated


def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
    """One differential-evolution candidate: search inside a generated box,
    then refine FROM that solution with ``least_squares`` under the request's
    own (open) bounds.

    Whenever a side was generated the refinement is unconditional (a request
    that bounds everything itself is returned as found). A box can shape the answer without the
    solution lying anywhere near a side (centre and width compensate for a
    capped amplitude), and an unrefined boundary candidate can lose the
    perturb loop's comparison to a worse interior one, so every candidate is
    freed from the box before it is compared or returned. The refined fit
    replaces the search result whenever it converged; if it did not (or
    raised) the search result is returned marked
    ``box_unverified`` (with the sides we generated, so they are not
    reported as bounds) and ``run_fit`` does not call it a success.
    """
    # ``params`` may come from an earlier candidate and still carry that
    # candidate's generated sides: always start from the request's bounds.
    boxed = params.copy()
    for name, (lo, hi) in requested.items():
        boxed[name].set(min=lo, max=hi)
    generated = _finite_search_box(boxed, x, y_sub)
    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
    found.box_unverified, found.search_box = bool(generated), generated
    if not generated:
        return found
    free = found.params.copy()
    for name in generated:
        free[name].set(min=requested[name][0], max=requested[name][1])
    # Only what a local solver understands: DE options (seed, popsize, ...)
    # passed through fit_kws would make least_squares raise.
    refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
    try:
        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
    except Exception:
        log.debug("refinement outside the search box raised", exc_info=True)
        return found
    # A converged refinement IS the result: it is a least_squares fit of the
    # requested model under the requested bounds, which is what the default
    # method returns and the acceptance rule accepts. It is deliberately NOT
    # compared with the boxed search's chi-square. least_squares descends
    # from its start, so it cannot end materially above it (four review
    # rounds found no reachable case), but it does end a hair above an EXACT
    # start that sits on a requested bound (the bound transform is degenerate
    # there; the centre moves ~1e-7 eV), by an amount that depends on peak
    # width, position and counts. Every tolerance tried for that comparison
    # produced reachable false failures and no reachable protection.
    if refined.success:
        refined.box_unverified, refined.search_box = False, {}
        return refined
    return found


def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws):
    """A differential-evolution candidate that is never worse than the
    default method from the same start.

  }
  state.chart.update('none');
}

// ═══════════════════════════════════════════════════
// ═══════════════════════════════════════════════════
// FLASK BACKEND HELPERS
// ═══════════════════════════════════════════════════
async function uploadToBackend(be, inten) {
  const csv = be.map((e, i) => e.toFixed(4) + ',' + inten[i].toFixed(2)).join('\n');
  const form = new FormData();
  form.append('file', new Blob([csv], { type: 'text/plain' }), 'spectrum.csv');
  const resp = await fetch('/api/upload', { method: 'POST', body: form });
  // A server-side failure (HTTP error, error body, or no session id) is not a
  // transport failure: runFit must report it, never switch engines (unit A0).
  const serverError = (msg) => { const err = new Error(msg); err.serverError = true; return err; };
  if (resp.ok === false) {
    let msg = null;
    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
    throw serverError(msg || ('Upload failed (HTTP ' + resp.status + ').'));
  }
  const json = await resp.json();
  if (!json || typeof json !== 'object') throw serverError('Upload returned an unexpected response.');
  if (json.error) throw serverError(json.error);
  if (!json.session_id) throw serverError('Upload returned no session id.');
  return json.session_id;
}

function peakToBackendSpec(p) {
  // All initial values go at top level — fitting.py reads spec.get("center") etc.
  const spec = {
    id: String(p.id),
    name: p.name,
    center: p.center,
    amplitude: p.amplitude,
    fwhm: p.fwhm,
    amplitude_min: 0,
    fix_center: !!p.fixCenter,
    fix_fwhm: !!p.fixFwhm,
    fix_amplitude: !!p.fixAmplitude,
    fix_gl_ratio: !!p.fixGlMix
  };
  const shape = p.shape;
  if (shape === 'Gaussian') {
    spec.shape = 'gaussian';
  } else if (shape === 'Lorentzian') {
    spec.shape = 'lorentzian';
  } else if (shape === 'Voigt') {
    // A03 (2026-09-22): Voigt IS the fixed 50/50 mix the page draws, exports
    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
    // the request sent eta FREE from 0.3, so the server fitted a mix the page
    // never showed — on the 90 committed Voigt targets 46 of 180 components
    // went to pure Gaussian and 17 to pure Lorentzian, and every area the page
    // reported for them was the 0.5 curve's, up to 24 % off the fitted one.
    // Fixed on both sides; use GL to fit the mix.
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = 0.5;
    spec.fix_gl_ratio = true;
  } else if (shape === 'GL') {
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
  } else if (shape === 'asym-GL') {
    spec.shape = 'asymmetric_gl';
    spec.gl_ratio = (p.glMix || 50) / 100;
    spec.asymmetry = p.asymmetry || 0;
    spec.fix_asymmetry = !!p.fixAsymmetry;
    // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
    // For non-auto-fit peaks these fields are absent and the backend falls back
    // to its [0.0, 1.0] default.
    if (Number.isFinite(p._afAsymMin)) spec.asymmetry_min = p._afAsymMin;
    if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
  } else if (shape === 'DS') {
    spec.shape = 'doniach_sunjic';
    spec.alpha      = p.dsAlpha || 0.1;
    spec.gamma_asym = p.dsGamma || 0.0;
    spec.fix_alpha      = !!p.fixDsAlpha;
    spec.fix_gamma_asym = !!p.fixDsGamma;
  } else if (shape === 'DSG_LA') {
    spec.shape = 'ds_g';
    spec.alpha   = Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10;
    spec.beta    = Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3;
    spec.m_gauss = Number.isFinite(p.laM)     ? p.laM     : 0.4;
    spec.fix_alpha   = !!p.fixLaAlpha;
    spec.fix_beta    = !!p.fixLaBeta;
    spec.fix_m_gauss = !!p.fixLaM;
  } else if (shape === 'LACX') {
    spec.shape = 'la_casaxps';
    spec.alpha = Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0;
    spec.beta  = Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0;
    spec.m     = Number.isFinite(p.caM)     ? p.caM     : 50.0;
    spec.fix_alpha = !!p.fixCaAlpha;
    spec.fix_beta  = !!p.fixCaBeta;
    spec.fix_m     = !!p.fixCaM;
  } else {
    spec.shape = 'gaussian';
  }
  if (p.linked) {
    const parent = getPeak(p.linked);
    if (parent) {
      spec.constrain_to = String(p.linked);
      spec.splitting = p.linkOffset;
      spec.area_ratio = p.linkRatio;
      spec.fix_fwhm = true;
    }
  }
  return spec;
}

// Server parameter names -> the peak's fields, honouring the peak's locks.
// Shared by a fit result and by an alternative solution (previewed on a COPY
// of the peaks, or adopted as the start of a new fit).
function _applyBackendParams(p, par) {
  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
  if (par.amplitude && !p.fixAmplitude) p.amplitude = par.amplitude.value;
  if (par.fwhm      && !p.fixFwhm)     p.fwhm      = par.fwhm.value;
  // glMix is read only by GL / asym-GL; a Voigt's fixed 0.5 (A03) is not a
  // fitted value and must not overwrite the mix the peak carries for a later
  // switch to GL.
# peakToBackendSpec mirror (index.html:5708)
# ─────────────────────────────────────────────────────────────────────────────

def _finite(v: Any) -> bool:
    """JS Number.isFinite: true only for finite numbers (not None/str/bool)."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and np.isfinite(v)


def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
    """
    Python mirror of the frontend's ``peakToBackendSpec``.

    ``all_peaks`` is needed for the linked-peak branch (JS resolves the
    parent via ``getPeak(p.linked)`` and silently drops the constraint when
    the parent is missing).
    """
    spec: dict[str, Any] = {
        "id": str(p["id"]),
        "name": p.get("name"),
        "center": p["center"],
        "amplitude": p["amplitude"],
        "fwhm": p["fwhm"],
        "amplitude_min": 0,
        "fix_center": bool(p.get("fixCenter")),
        "fix_fwhm": bool(p.get("fixFwhm")),
        "fix_amplitude": bool(p.get("fixAmplitude")),
        "fix_gl_ratio": bool(p.get("fixGlMix")),
    }
    shape = p.get("shape")
    if shape == "Gaussian":
        spec["shape"] = "gaussian"
    elif shape == "Lorentzian":
        spec["shape"] = "lorentzian"
    elif shape == "Voigt":
        # A03: the fixed 50/50 mix the page draws (twin of peakToBackendSpec)
        spec["shape"] = "pseudo_voigt_gl"
        spec["gl_ratio"] = 0.5
        spec["fix_gl_ratio"] = True
    elif shape == "GL":
        spec["shape"] = "pseudo_voigt_gl"
        spec["gl_ratio"] = p["glMix"] / 100.0
    elif shape == "asym-GL":
        spec["shape"] = "asymmetric_gl"
        spec["gl_ratio"] = (p.get("glMix") or 50) / 100.0
        spec["asymmetry"] = p.get("asymmetry") or 0
        spec["fix_asymmetry"] = bool(p.get("fixAsymmetry"))
        if _finite(p.get("_afAsymMin")):
            spec["asymmetry_min"] = p["_afAsymMin"]
        if _finite(p.get("_afAsymMax")):
            spec["asymmetry_max"] = p["_afAsymMax"]
    elif shape == "DS":
        spec["shape"] = "doniach_sunjic"
        spec["alpha"] = p.get("dsAlpha") or 0.1
        spec["gamma_asym"] = p.get("dsGamma") or 0.0
        spec["fix_alpha"] = bool(p.get("fixDsAlpha"))
        spec["fix_gamma_asym"] = bool(p.get("fixDsGamma"))
    elif shape == "DSG_LA":
        spec["shape"] = "ds_g"
        spec["alpha"] = p["laAlpha"] if _finite(p.get("laAlpha")) else 0.10
        spec["beta"] = p["laBeta"] if _finite(p.get("laBeta")) else 0.3
        spec["m_gauss"] = p["laM"] if _finite(p.get("laM")) else 0.4
        spec["fix_alpha"] = bool(p.get("fixLaAlpha"))
        spec["fix_beta"] = bool(p.get("fixLaBeta"))
        spec["fix_m_gauss"] = bool(p.get("fixLaM"))
    elif shape == "LACX":
        spec["shape"] = "la_casaxps"
        spec["alpha"] = p["caAlpha"] if _finite(p.get("caAlpha")) else 1.0
        spec["beta"] = p["caBeta"] if _finite(p.get("caBeta")) else 1.0
        spec["m"] = p["caM"] if _finite(p.get("caM")) else 50.0
        spec["fix_alpha"] = bool(p.get("fixCaAlpha"))
        spec["fix_beta"] = bool(p.get("fixCaBeta"))
        spec["fix_m"] = bool(p.get("fixCaM"))
    else:
        spec["shape"] = "gaussian"

    if p.get("linked"):
        parent = next((q for q in all_peaks if q.get("id") == p["linked"]), None)
        if parent is not None:
            spec["constrain_to"] = str(p["linked"])
            spec["splitting"] = p.get("linkOffset")
            spec["area_ratio"] = p.get("linkRatio")
            spec["fix_fwhm"] = True
    return spec

git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0V9nnWB1' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cQ8Bth5t' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index c1eeada..6527c0f 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -110,13 +110,30 @@ tab reordering exists.
 |----|-------------|
 | `Gaussian` | Pure Gaussian |
 | `Lorentzian` | Pure Lorentzian |
-| `Voigt` | Pseudo-Voigt (Thompson et al.), fixed η = 0.5 |
+| `Voigt` | Pseudo-Voigt, fixed η = 0.5 on BOTH sides (A03, 2026-09-22: the request sends `gl_ratio: 0.5, fix_gl_ratio: true`; until then the server fitted η FREE from 0.3 while the page drew, integrated and exported 0.5). Use `GL` to fit the mix. |
 | `GL` | Pseudo-Voigt with adjustable GL mixing (0–100) |
 | `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
 | `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
 | `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
 | `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + integer-kernel Gauss conv. Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |
 
+**What the page draws must be what the server fitted.** Two harnesses pin
+it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
+page's own `peakToBackendSpec`, fits it with `fitting.run_fit`, applies the
+result with `_applyBackendParams` and requires `evalPeakArray` on the fitted
+grid to equal `individual_peaks[].y` for every shape (it also pins the
+Python twin `autofit.reference.peak_to_backend_spec` to the page's builder,
+shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
+each shape's FREE parameters across the fit's bounds. Both were added in A03
+(2026-09-22) after a "Voigt" was found to be fitted with η free while drawn
+at 0.5. Tracked gaps, `todo` in both files: LACX with m > 0 (the page draws
+a rounded integer kernel; the server fits m continuously — the `caM` clamp
+unit) and DS+G with m ≥ 0.05 (the page's quadrature `laCasaXPS` sizes its
+step to the Lorentzian core, not the Gaussian kernel, and is wrong by up to
+80 % of amplitude across the fitted β/m range — 1e52 × at β = 2, m = 0.05;
+0 of 865 committed components use DS+G; its own unit). Details in
+`docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+
 ---
 
 ## Design Rules
@@ -459,16 +476,25 @@ the integer-clamped `caM` is not optimised (carried at its start value).
 
 **A local result is a STARTING POINT, not a reportable result** (keyed on
 `engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
-`_localFitCaveat`). Measured in unit W1: weighted, it matches the server
-on GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) but still
-differs for Voigt components (the server fits their mix free — audit A03),
-LA components (`caM` held), and where the model has several minima
-(both engines' amplitude floor is 0 since unit step (b)). Both engines weight by
+`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
+(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
+generator `scripts/local_server_gap.js`): weighted, it matches the server on
+GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
+components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
+U 4f targets where both engines reach the same minimum every component
+agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
+to 20.8 % area on the Voigt satellites); it still differs for LA components
+(`caM` held at its start locally while the server fits m continuously: on
+the other 4 U 4f targets the server's m moved from 8 to 2.7–10.0, χ²ᵣ
+differs by 8–20 % and satellite areas by up to 8.9 %, 0.77 pp) and where the
+model has several minima (both engines' amplitude floor is 0 since unit
+step (b)). Both engines weight by
 √intensity whether the data are counts or CPS (a convention, not a
 calibrated uncertainty for rates); the formula is the same but the inputs
 are not bit-identical, because `uploadToBackend` rounds intensities to
-2 dp before the server weights them. Retire the designation only on a
-re-measurement after A03 and the `caM` clamp. (The amplitude-bound change
+2 dp before the server weights them. A03 is done and the designation
+STAYS: the `caM` clamp is what remains, and the label is reconsidered only
+on a re-measurement after it. (The amplitude-bound change
 DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
 implemented: unit step (b), 2026-09-22, below.) The same file records that a
 converged server fit is not ground truth: on a committed C 1s scan the
diff --git a/docs/findings/2026-09-fit-determinacy.md b/docs/findings/2026-09-fit-determinacy.md
index 8ad6c2f..6e2eee2 100644
--- a/docs/findings/2026-09-fit-determinacy.md
+++ b/docs/findings/2026-09-fit-determinacy.md
@@ -255,3 +255,58 @@ whether the result names the slot by its ROLE (so a migrated slot is still
 called C–O). Narrower per-role centre windows are the structural remedy; the
 manual path has only the ± 2 eV default.
 
+
+## 7. A03 (2026-09-22) — a "Voigt" was fitted with a mix the page never drew; the sweep found DS+G's preview wrong across its fitted range
+
+Generators: `scripts/voigt_eta_measure.py` (the 90 committed Voigt targets,
+both requests), `scripts/local_server_gap.js` (the 18 W1 targets),
+section (D) of `tests/js/lineshape_parity.test.js` (the sweep). Plan and
+tables: `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+
+**The Voigt identity.** `peakToBackendSpec` sent a Voigt as
+`pseudo_voigt_gl` with `gl_ratio: 0.3` FREE; `evalPeak` drew η = 0.5;
+`runFitLocal` held 0.5; the dropdown said "50/50"; CLAUDE.md said fixed 0.5.
+On the 90 committed targets with a Voigt component (89 U 4f tabs across five
+projects, one Cl 2p; 180 Voigt components): the server's free η ended at
+pure Gaussian (< 0.01) on 46 of the 180 and pure Lorentzian (> 0.99) on
+17, within 0.4–0.6 on 24. Every area, percentage, chart
+component and export the page produced for those components was the 0.5
+curve under parameters fitted for another mix: displayed area vs the fitted
+curve median 11.8 %, p90 19.2 %, max 20.1 % (103 of 180 components > 10 %);
+area fractions off by median 0.96 pp, max 1.60 pp (35 of 90 targets > 1 pp).
+Fixed on both sides (η = 0.5 held in the request). What a student SEES
+change on re-fitting a saved project is small — the fixed refit vs what the
+page displayed: median 0.30 pp, max 1.02 pp (1 target > 1 pp) — because both
+are the 0.5 curve; the refit vs the server's own free-η fit is median
+0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9.5 % (the mix is one parameter
+fewer). The alternative — honour the fitted η on the page — would have made
+"Voigt" a GL with a hidden slider and silently kept a shape the student had
+not chosen; 63 of 180 fitted values sitting on a bound says the parameter
+was not determined by the data in those fits anyway.
+
+**The re-measurement (W1 methodology, 18 targets).** C 1s unchanged (8 of 9
+within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is the §2 finding). U 4f,
+W1 → A03: max Δcentre 39.7 → 28.8 meV, ΔFWHM 17.2 → 15.8 %, Δarea 20.8 →
+8.9 %, Δfraction 1.4 → 0.77 pp. On the 5 of 9 targets where both engines
+reach the same minimum (χ²ᵣ equal to 2–3 digits) every component is within
+4.3 meV, 2.6 %, 2.0 %, 0.12 pp — the Voigt gap is gone. On the other 4 the
+server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
+7.9 while the local engine holds it; χ²ᵣ differs by 8–20 % (the local engine
+LOWER on Scan_6, 2.657 vs 2.798), and the satellites, which share the
+region, differ by up to 8.9 % in area. That residual is the `caM` clamp,
+next; the "starting point" label stays until it is done and re-measured.
+
+**The sweep.** Gaussian, Lorentzian, Voigt, GL, asym-GL and DS agree with
+the server to 1e-15 across every bound. LACX with m > 0: up to 0.89 % of
+amplitude when the kernel is wide against the peak (the tracked
+discretisation gap). DS+G with m ≥ 0.05: the page's `laCasaXPS` quadrature
+uses a step of 2·(6σ + 50β)/max(300, ⌈2·(6σ + 50β)/(β/3)⌉) — sized to the
+Lorentzian core, blind to the Gaussian kernel — so at β = 2, m = 0.05 the
+step is 0.67 eV against σ = 0.021 eV, the kernel weights sample nothing,
+and the page's curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's
+area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
+865 committed components use DS+G, so no saved figure is affected; it is the
+fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
+recorded as its own unit. The general lesson repeats §6's: a harness that
+evaluates one representative point per shape proves nothing about the range
+the optimiser can reach.
diff --git a/scripts/bg_window_worked_example.py b/scripts/bg_window_worked_example.py
index 57602d7..4dc4e16 100644
--- a/scripts/bg_window_worked_example.py
+++ b/scripts/bg_window_worked_example.py
@@ -22,7 +22,7 @@ def spec_of(p):
              amplitude_min=0, fix_center=bool(p.get('fixCenter')), fix_fwhm=bool(p.get('fixFwhm')),
              fix_amplitude=bool(p.get('fixAmplitude')), fix_gl_ratio=bool(p.get('fixGlMix')))
     sh = p['shape']
-    if sh == 'Voigt': s.update(shape='pseudo_voigt_gl', gl_ratio=0.3)
+    if sh == 'Voigt': s.update(shape='pseudo_voigt_gl', gl_ratio=0.5, fix_gl_ratio=True)  # A03: fixed 50/50 mix
     elif sh == 'GL': s.update(shape='pseudo_voigt_gl', gl_ratio=p['glMix'] / 100)
     elif sh == 'Gaussian': s.update(shape='gaussian')
     elif sh == 'Lorentzian': s.update(shape='lorentzian')
diff --git a/scripts/endpoint_avg_sensitivity.py b/scripts/endpoint_avg_sensitivity.py
index 7c2095c..739e9df 100644
--- a/scripts/endpoint_avg_sensitivity.py
+++ b/scripts/endpoint_avg_sensitivity.py
@@ -45,7 +45,7 @@ def spec_of(p):
              amplitude_min=0, fix_center=bool(p.get('fixCenter')), fix_fwhm=bool(p.get('fixFwhm')),
              fix_amplitude=bool(p.get('fixAmplitude')), fix_gl_ratio=bool(p.get('fixGlMix')))
     sh = p['shape']
-    if sh == 'Voigt': s.update(shape='pseudo_voigt_gl', gl_ratio=0.3)
+    if sh == 'Voigt': s.update(shape='pseudo_voigt_gl', gl_ratio=0.5, fix_gl_ratio=True)  # A03: fixed 50/50 mix
     elif sh == 'GL': s.update(shape='pseudo_voigt_gl', gl_ratio=p['glMix'] / 100)
     elif sh == 'Gaussian': s.update(shape='gaussian')
     elif sh == 'Lorentzian': s.update(shape='lorentzian')
diff --git a/scripts/gen_u4f_battery_fixture.py b/scripts/gen_u4f_battery_fixture.py
index a3720ce..7e0d6ec 100644
--- a/scripts/gen_u4f_battery_fixture.py
+++ b/scripts/gen_u4f_battery_fixture.py
@@ -36,7 +36,10 @@ def main() -> None:
                     skipped.append({"project": rf.project, "name": rf.name,
                                     "reason": reason})
                 continue
-            records.append(refit_record(rf))
+            rec = refit_record(rf)
+            for pk in rec["peaks"]:
+                pk.pop("params", None)   # the fixture pins numbers, not the full model
+            records.append(rec)
     os.makedirs(os.path.dirname(OUT), exist_ok=True)
     with open(OUT, "w") as f:
         json.dump({"records": records, "skipped": skipped}, f, indent=1, sort_keys=True)

exec
/bin/zsh -lc "ls -ld venv /Users/skyefortier/xps-app/venv/bin/python*; sed -n '1,160p' tests/autofit/battery_common.py; sed -n '175,250p' autofit/parity.py; rg -n 'n_perturb|def run_fit|share_parent_params|gamma_asym.*min|m_gauss.*min' fitting.py; cat docs/findings/a03/local_server_gap.log" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
ls: venv: No such file or directory
lrwxr-xr-x  1 skyefortier  staff  10 May  7 11:22 /Users/skyefortier/xps-app/venv/bin/python -> python3.12
lrwxr-xr-x  1 skyefortier  staff  10 May  7 11:22 /Users/skyefortier/xps-app/venv/bin/python3 -> python3.12
lrwxr-xr-x  1 skyefortier  staff  41 May  7 11:22 /Users/skyefortier/xps-app/venv/bin/python3.12 -> /usr/local/opt/python@3.12/bin/python3.12
"""
Shared characterization-battery harness (used by the per-region
test_*_parity_battery.py files).

Three layers per region (see test_c1s_parity_battery.py for the rationale):
roster guard, eval parity vs saved fittedY, seeded-refit stability vs the
expert fit + frozen fixture records.
"""

import glob
import json
import os

import numpy as np

from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

# Default tolerances (C 1s levels).  Per-region batteries may override:
#
# - eval_tol: bounded below by BACKGROUND-ANCHOR DRIFT — ui bg-start/end
#   fields move with post-fit charge-correction nudges and round to 0.1 eV,
#   so the nearest-index anchors can shift ±1 grid point vs fit time; for
#   'smart' backgrounds that perturbs the recomputed background by
#   O(100 counts) mid-window (measured U 4f: eval relmax ~7e-3 with the
#   deviation profile exactly matching the background, not the shapes).
# - fixture_rtol: bounded below by CROSS-PROCESS FP wobble in the LACX
#   convolution path (~6e-6 relative on fitted params; exactly 0.0 within
#   one process).  Simple shapes (C 1s) reproduce at 1e-6.
EVAL_PARITY_TOL = 1e-5
CENTER_DRIFT_TOL_EV = 0.005
REL_DRIFT_TOL = 0.005
FIXTURE_CHI_RTOL = 1e-6
FIXTURE_PARAM_RTOL = 1e-6


def battery_fits(region):
    fits = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            if battery_eligible(rf, region=region)[0]:
                fits.append(rf)
    return fits


def load_fixture(name):
    with open(os.path.join(FIXTURE_DIR, name)) as f:
        return {(r["project"], r["name"]): r for r in json.load(f)["records"]}


def assert_roster(fits, expected, min_size, min_projects, gen_script):
    assert len(fits) >= min_size, (
        f"battery shrank to {len(fits)} fits (< {min_size}) — reference data "
        "or eligibility rules changed"
    )
    projects = {rf.project for rf in fits}
    assert len(projects) >= min_projects, f"battery covers only {projects}"
    assert {(rf.project, rf.name) for rf in fits} == set(expected), (
        "battery roster no longer matches the frozen fixture — regenerate "
        f"{gen_script} only if this change is intentional"
    )


def assert_eval_parity(rf, tol=EVAL_PARITY_TOL):
    relmax = eval_parity_relmax(rf)
    assert relmax < tol, (
        f"{rf.project}/{rf.name}: python eval of saved params deviates from "
        f"saved fittedY by {relmax:.3e} (tol {tol})"
    )


def assert_refit_stability_and_fixture(
    rf, expected,
    center_tol=CENTER_DRIFT_TOL_EV,
    rel_tol=REL_DRIFT_TOL,
    fixture_rtol=FIXTURE_PARAM_RTOL,
    stationarity="expert",
):
    """stationarity: what the seeded refit must stay at.
    "expert" — the saved expert fit itself (the fit is a fixed point of
    today's fitter). "refit" — a refit FROM the refit (the fitter's own fixed
    point): for a region whose saved fits were made under a request the page
    no longer sends (U 4f: Voigt satellites fitted with eta free until A03,
    2026-09-22), the expert's parameters are those of another model and the
    "expert" base cannot hold; the frozen fixture still pins the refit's
    numbers."""
    rec = refit_record(rf)
    assert rec["success"], f"{rf.project}/{rf.name}: seeded refit did not converge"

    if stationarity == "refit":
        rec2 = refit_record(rf, start=rec)
        assert rec2["success"], f"{rf.project}/{rf.name}: refit from the refit did not converge"
        base, moving, base_name = rec["peaks"], rec2["peaks"], "the refit"
    else:
        base, moving, base_name = rf.peaks, rec["peaks"], "expert fit"
    by_id = {str(p["id"]): p for p in base}
    for pk in moving:
        saved = by_id[str(pk["id"])]
        dc = abs(pk["center"] - saved["center"])
        dfw = abs(pk["fwhm"] - saved["fwhm"]) / max(saved["fwhm"], 1e-9)
        dam = abs(pk["amplitude"] - saved["amplitude"]) / max(abs(saved["amplitude"]), 1e-9)
        assert dc <= center_tol, (
            f"{rf.name} peak {pk['id']}: center drifted {dc:.4f} eV from {base_name}"
        )
        assert dfw <= rel_tol, (
            f"{rf.name} peak {pk['id']}: fwhm drifted {dfw:.2%} from {base_name}"
        )
        assert dam <= rel_tol, (
            f"{rf.name} peak {pk['id']}: amplitude drifted {dam:.2%} from {base_name}"
        )

    exp = expected[(rf.project, rf.name)]
    assert np.isclose(rec["reduced_chi_square"], exp["reduced_chi_square"],
                      rtol=max(FIXTURE_CHI_RTOL, fixture_rtol)), (
        f"{rf.name}: χ²ᵣ {rec['reduced_chi_square']} != frozen "
        f"{exp['reduced_chi_square']} — fitting.py numerics changed"
    )
    exp_peaks = {str(p["id"]): p for p in exp["peaks"]}
    for pk in rec["peaks"]:
        ep = exp_peaks[str(pk["id"])]
        for key in ("center", "fwhm", "amplitude", "area"):
            assert np.isclose(pk[key], ep[key], rtol=fixture_rtol, atol=1e-9), (
                f"{rf.name} peak {pk['id']}: {key} {pk[key]} != frozen {ep[key]}"
            )
    """
    fittedY = np.asarray(rf.fit_result["fittedY"], dtype=float)
    specs = rf.backend_peak_specs()
    model = evaluate_model(rf.roi_be, specs)
    i0, i1 = rf.bg_indices()
    bg = background_like_run_fit(
        rf.roi_be, rf.roi_intensity, rf.bg_method, i0, i1, rf.endpoint_avg
    )
    scale = max(float(np.max(np.abs(fittedY))), 1.0)
    return float(np.max(np.abs(model + bg - fittedY)) / scale)


def refit_record(rf: ReferenceFit, start: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Deterministic seeded refit (leastsq, no perturbation) from the saved
    parameters.  Returns a serializable record for fixture freezing; each
    peak also carries ``params`` (every server parameter's fitted value) so
    the record can be the START of another refit: with ``start`` (a record
    from this function) the saved peaks are first overwritten with that
    record's parameters through the page's write-back twin, exactly as the
    page holds a model after Run Fit.
    """
    import copy
    peaks = rf.peaks
    if start is not None:
        peaks = copy.deepcopy(rf.peaks)
        by_id = {str(pk["id"]): pk for pk in start["peaks"]}
        for p in peaks:
            pk = by_id.get(str(p["id"]))
            if pk is not None and pk.get("params"):
                apply_backend_params(p, pk["params"])
    i0, i1 = rf.bg_indices()
    res = run_fit(
        rf.roi_be,
        rf.roi_intensity,
        [peak_to_backend_spec(p, peaks) for p in peaks],
        background_method=rf.bg_method,
        bg_start_idx=i0,
        bg_end_idx=i1,
        endpoint_avg=rf.endpoint_avg,
        n_perturb=0,
    )
    peaks = []
    for ip in res["individual_peaks"]:
        par = ip["params"]
        peaks.append({
            "id": ip["id"],
            "center": par["center"]["value"],
            "fwhm": par["fwhm"]["value"],
            "amplitude": par["amplitude"]["value"],
            "area": par["area"]["value"],
            "params": {k: v["value"] for k, v in par.items() if k != "area"},
        })
    return {
        "project": rf.project,
        "name": rf.name,
        "reduced_chi_square": res["statistics"]["reduced_chi_square"],
        "r_factor": res["statistics"]["r_factor"],
        "success": bool(res["success"]),
        "peaks": peaks,
    }
896:            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
938:        _set("gamma_asym", spec.get("gamma_asym", 0.0), min_=0.0, max_=5.0,
945:        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0,
1124:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1129:    solver options and ``n_perturb``.
1168:                       "n_perturb": n_perturb})
1413:def run_fit(
1422:    n_perturb: int = 0,
1619:            fit_kws=fit_kws, n_perturb=n_perturb)
1686:    if n_perturb > 0 and result.success:
1691:        for attempt in range(n_perturb):
1712:                          attempt + 1, n_perturb, trial_redchi, best_redchi)
1723:                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
C1s C1s Scan_0 local true 4.353 server true 4.357 max Δcentre 3.8 meV, ΔFWHM 0.29 %, Δarea 0.42 %, Δfrac 0.04 pp
C1s C1s Scan_1 local true 13.074 server true 13.066 max Δcentre 2.6 meV, ΔFWHM 0.50 %, Δarea 1.40 %, Δfrac 0.32 pp
C1s C1s Scan_2 local true 4.084 server true 4.087 max Δcentre 3.5 meV, ΔFWHM 0.07 %, Δarea 0.37 %, Δfrac 0.05 pp
C1s C1s Scan_3 local true 4.425 server true 4.432 max Δcentre 1.6 meV, ΔFWHM 0.06 %, Δarea 0.13 %, Δfrac 0.02 pp
C1s C1s Scan_4 local true 18.218 server true 19.056 max Δcentre 41.9 meV, ΔFWHM 8.97 %, Δarea 99.85 %, Δfrac 15.07 pp
C1s C1s Scan_5 local true 4.331 server true 4.332 max Δcentre 0.6 meV, ΔFWHM 0.03 %, Δarea 0.06 %, Δfrac 0.00 pp
C1s C1s Scan_6 local true 5.211 server true 5.230 max Δcentre 2.1 meV, ΔFWHM 0.17 %, Δarea 0.24 %, Δfrac 0.02 pp
C1s C1s Scan_7 local true 7.994 server true 8.016 max Δcentre 1.4 meV, ΔFWHM 0.24 %, Δarea 0.36 %, Δfrac 0.04 pp
C1s C1s Scan_8 local true 2.742 server true 2.741 max Δcentre 0.8 meV, ΔFWHM 0.12 %, Δarea 0.18 %, Δfrac 0.02 pp
U4f U4f Scan_0 local true 2.065 server true 2.055 max Δcentre 1.6 meV, ΔFWHM 0.22 %, Δarea 0.17 %, Δfrac 0.01 pp
U4f U4f Scan_1 local true 2.296 server true 2.267 max Δcentre 4.3 meV, ΔFWHM 1.36 %, Δarea 1.95 %, Δfrac 0.12 pp
U4f U4f Scan_2 local true 1.936 server true 1.940 max Δcentre 1.9 meV, ΔFWHM 1.39 %, Δarea 0.38 %, Δfrac 0.02 pp
U4f U4f Scan_3 local true 1.732 server true 1.732 max Δcentre 3.0 meV, ΔFWHM 2.59 %, Δarea 1.74 %, Δfrac 0.12 pp
U4f U4f Scan_4 local true 1.970 server true 1.798 max Δcentre 26.6 meV, ΔFWHM 5.30 %, Δarea 8.32 %, Δfrac 0.33 pp
U4f U4f Scan_5 local true 2.393 server true 2.174 max Δcentre 4.7 meV, ΔFWHM 4.26 %, Δarea 6.65 %, Δfrac 0.35 pp
U4f U4f Scan_6 local true 2.657 server true 2.798 max Δcentre 28.8 meV, ΔFWHM 15.81 %, Δarea 8.88 %, Δfrac 0.77 pp
U4f U4f Scan_7 local true 1.764 server true 1.757 max Δcentre 2.6 meV, ΔFWHM 0.36 %, Δarea 0.49 %, Δfrac 0.04 pp
U4f U4f Scan_8 local true 4.656 server true 4.129 max Δcentre 5.7 meV, ΔFWHM 5.02 %, Δarea 8.31 %, Δfrac 0.32 pp

exec
/bin/zsh -lc "sed -n '6198,6290p' templates/index.html; sed -n '850,899p' fitting.py; sed -n '11275,11375p' templates/index.html; sed -n '1,110p' autofit/regions/u4f.py; sed -n '76,143p' CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
  }
  const json = await resp.json();
  if (!json || typeof json !== 'object') throw serverError('Upload returned an unexpected response.');
  if (json.error) throw serverError(json.error);
  if (!json.session_id) throw serverError('Upload returned no session id.');
  return json.session_id;
}

function peakToBackendSpec(p) {
  // All initial values go at top level — fitting.py reads spec.get("center") etc.
  const spec = {
    id: String(p.id),
    name: p.name,
    center: p.center,
    amplitude: p.amplitude,
    fwhm: p.fwhm,
    amplitude_min: 0,
    fix_center: !!p.fixCenter,
    fix_fwhm: !!p.fixFwhm,
    fix_amplitude: !!p.fixAmplitude,
    fix_gl_ratio: !!p.fixGlMix
  };
  const shape = p.shape;
  if (shape === 'Gaussian') {
    spec.shape = 'gaussian';
  } else if (shape === 'Lorentzian') {
    spec.shape = 'lorentzian';
  } else if (shape === 'Voigt') {
    // A03 (2026-09-22): Voigt IS the fixed 50/50 mix the page draws, exports
    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
    // the request sent eta FREE from 0.3, so the server fitted a mix the page
    // never showed — on the 90 committed Voigt targets 46 of 180 components
    // went to pure Gaussian and 17 to pure Lorentzian, and every area the page
    // reported for them was the 0.5 curve's, up to 24 % off the fitted one.
    // Fixed on both sides; use GL to fit the mix.
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = 0.5;
    spec.fix_gl_ratio = true;
  } else if (shape === 'GL') {
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
  } else if (shape === 'asym-GL') {
    spec.shape = 'asymmetric_gl';
    spec.gl_ratio = (p.glMix || 50) / 100;
    spec.asymmetry = p.asymmetry || 0;
    spec.fix_asymmetry = !!p.fixAsymmetry;
    // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
    // For non-auto-fit peaks these fields are absent and the backend falls back
    // to its [0.0, 1.0] default.
    if (Number.isFinite(p._afAsymMin)) spec.asymmetry_min = p._afAsymMin;
    if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
  } else if (shape === 'DS') {
    spec.shape = 'doniach_sunjic';
    spec.alpha      = p.dsAlpha || 0.1;
    spec.gamma_asym = p.dsGamma || 0.0;
    spec.fix_alpha      = !!p.fixDsAlpha;
    spec.fix_gamma_asym = !!p.fixDsGamma;
  } else if (shape === 'DSG_LA') {
    spec.shape = 'ds_g';
    spec.alpha   = Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10;
    spec.beta    = Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3;
    spec.m_gauss = Number.isFinite(p.laM)     ? p.laM     : 0.4;
    spec.fix_alpha   = !!p.fixLaAlpha;
    spec.fix_beta    = !!p.fixLaBeta;
    spec.fix_m_gauss = !!p.fixLaM;
  } else if (shape === 'LACX') {
    spec.shape = 'la_casaxps';
    spec.alpha = Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0;
    spec.beta  = Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0;
    spec.m     = Number.isFinite(p.caM)     ? p.caM     : 50.0;
    spec.fix_alpha = !!p.fixCaAlpha;
    spec.fix_beta  = !!p.fixCaBeta;
    spec.fix_m     = !!p.fixCaM;
  } else {
    spec.shape = 'gaussian';
  }
  if (p.linked) {
    const parent = getPeak(p.linked);
    if (parent) {
      spec.constrain_to = String(p.linked);
      spec.splitting = p.linkOffset;
      spec.area_ratio = p.linkRatio;
      spec.fix_fwhm = true;
    }
  }
  return spec;
}

// Server parameter names -> the peak's fields, honouring the peak's locks.
// Shared by a fit result and by an alternative solution (previewed on a COPY
// of the peaks, or adopted as the start of a new fit).
function _applyBackendParams(p, par) {
  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
        p[full].set(value=value)
        if expr is not None:
            p[full].expr = expr
            p[full].vary = False
        else:
            if min_ is not None:
                p[full].min = min_
            if max_ is not None:
                p[full].max = max_
            p[full].vary = vary

    # Constrain to a master peak (spin‑orbit doublet)?
    master_id = spec.get("constrain_to")
    if master_id is not None:
        # Find the master spec to get its prefix
        master_spec = next((s for s in all_specs if s["id"] == master_id), None)
        if master_spec is None:
            raise ValueError(f"Master peak '{master_id}' not found for spin‑orbit constraint")
        m_prefix = f"p{master_spec['id']}_"
        splitting = float(spec.get("splitting", 0.0))
        area_ratio = float(spec.get("area_ratio", 1.0))

        _set("center", center, expr=f"{m_prefix}center + {splitting}")
        _set("amplitude", amp, expr=f"{m_prefix}amplitude * {area_ratio}")
        _set("fwhm", fwhm, expr=f"{m_prefix}fwhm" if spec.get("fix_fwhm", True) else None,
             min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0))
        if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
            _set("gl_ratio", spec.get("gl_ratio", 0.3),
                 expr=f"{m_prefix}gl_ratio" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "asymmetric_gl":
            _set("asymmetry", asymmetry,
                 expr=f"{m_prefix}asymmetry" if spec.get("fix_fwhm", True) else None,
                 min_=spec.get("asymmetry_min", 0.0),
                 max_=spec.get("asymmetry_max", 1.0))
        if shape == "doniach_sunjic":
            _set("alpha", spec.get("alpha", 0.1),
                 expr=f"{m_prefix}alpha" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=0.5)
            _set("gamma_asym", spec.get("gamma_asym", 0.0),
                 expr=f"{m_prefix}gamma_asym" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "ds_g":
            fix = spec.get("fix_fwhm", True)
            _set("alpha",   spec.get("alpha",   0.10), expr=f"{m_prefix}alpha"   if fix else None, min_=0.0,  max_=0.49)
            _set("beta",    spec.get("beta",    0.3),  expr=f"{m_prefix}beta"    if fix else None, min_=0.05, max_=2.0)
            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
        if shape == "la_casaxps":
            fix = spec.get("fix_fwhm", True)
            _set("alpha", spec.get("alpha", 1.0),
    if (!el) return;
    clearTimeout(timer);
    timer = setTimeout(() => {
      const tip = document.getElementById('xps-tooltip');
      if (!tip) return;
      tip.textContent = '';
      const lines = el.dataset.xpsTip.split('\n');
      lines.forEach((line, i) => {
        if (i > 0) tip.appendChild(document.createElement('br'));
        tip.appendChild(document.createTextNode(line));
      });
      tip.classList.remove('tip-above', 'visible');
      const rect = el.getBoundingClientRect();
      const tipH = 160;
      const spaceBelow = window.innerHeight - rect.bottom;
      if (spaceBelow < tipH && rect.top > tipH) {
        tip.classList.add('tip-above');
        tip.style.top = (rect.top - tipH - 6) + 'px';
      } else {
        tip.style.top = (rect.bottom + 6) + 'px';
      }
      tip.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - 320)) + 'px';
      tip.classList.add('visible');
    }, DELAY);
  }, true);
  document.addEventListener('mouseleave', function (e) {
    if (!(e.target instanceof Element) || !e.target.closest('[data-xps-tip]')) return;
    clearTimeout(timer);
    const tip = document.getElementById('xps-tooltip');
    if (tip) tip.classList.remove('visible');
  }, true);
})();

// ═══════════════════════════════════════════════════
// UNCERTAINTY VALIDATION
// ═══════════════════════════════════════════════════
function _validateUncertainties() {
  if (!state.fitResult?.backendResult?.individual_peaks) return { warnings: [], info: [] };
  const warnings = [];
  const info = [];
  const stderrMap = _buildStderrMap(state.fitResult);
  const preFit = state.fitResult._preFit || {};
  // Map backend param names to pre-fit property names
  const nameMap = { center: 'center', fwhm: 'fwhm', fwhm_l: 'fwhm', amplitude: 'amplitude', gl_ratio: 'glMix' };

  for (const [rawId, params] of Object.entries(stderrMap)) {
    const p = getPeak(Number(rawId));
    if (!p) continue;
    // Rule 0: the fit did not determine this component at all. Reported once,
    // here, instead of the per-parameter alarms (or, after Auto-Fit's centre
    // lock, the neutral "locked" note) that would otherwise misdescribe it.
    if (_isUnsupported(p)) {
      warnings.push(`<li><b>${_escHtml(p.name)}:</b> ${_UNSUPPORTED_LABEL} — with the other components held as fitted, removing it does not make the fit significantly worse${p.support.f != null ? ' (F = ' + p.support.f.toFixed(1) + ', threshold 10)' : ''}. Its centre, width and uncertainties are not reported. Try another starting position or width, lock the centre where chemistry says it belongs, or drop the component.</li>`);
      continue;
    }
    const init = preFit[Number(rawId)] || {};

    for (const [pName, pData] of Object.entries(params)) {
      if (!['center','fwhm','fwhm_l','amplitude','gl_ratio'].includes(pName)) continue;
      const val = pData.value;

      // Locked or linked: skip the alarm-style movement/stderr checks.
      //   - linked satellite (expr set): tied to master via lmfit expr; intentional
      //     by construction → silent
      //   - genuinely locked (vary=false, no expr): user or auto-fit set this lock
      //     → neutral info note pointing at the padlock toggle, not an alarm
      if (pData.vary === false) {
        const isLinked = pData.expr != null && pData.expr !== '';
        if (!isLinked) {
          info.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> locked — unlock the padlock to refine.</li>`);
        }
        continue;
      }

      // Rule 1: parameter sitting at its bound (within 1% of range from min or max)
      const lo = pData.min, hi = pData.max;
      if (lo != null && hi != null && isFinite(lo) && isFinite(hi)) {
        const range = hi - lo;
        if (range > 0) {
          if ((val - lo) <= range * 0.01) {
            warnings.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> at lower bound (${lo}). Widen bounds or lock this parameter.</li>`);
            continue;
          }
          if ((hi - val) <= range * 0.01) {
            warnings.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> at upper bound (${hi}). Widen bounds or lock this parameter.</li>`);
            continue;
          }
        }
      }

      // Rule 2: param was free (vary=true, no expr) but lmfit returned no
      // stderr AND the value barely moved → covariance matrix singular near
      // this parameter. Distinct from "locked" (handled above) and from
      // "converged at start with valid stderr" (silent — normal convergence).
      const se = pData.stderr;
      if (se == null) {
        const initKey = nameMap[pName] || pName;
        const initVal = init[initKey];
        if (initVal != null) {
          const denom = Math.max(Math.abs(initVal), 1e-10);
          if (Math.abs(val - initVal) / denom < 0.001) {
"""
U 4f region module (spec v2.1 §3.2 — the Stage-3 deliverable).

Model decision (Skye, domain expert; spec §3.2): U(IV) 5f² is an open-shell
final state whose multiplet manifold is an unknown number of closely-spaced,
individually unresolvable lines — the **asymmetric LACX lineshape is the
physically-correct envelope of that manifold** (multiplet/final-state
origin, NOT metallic screening — Ilton & Bagus, Surf. Interface Anal. 43
(2011) 1549, DOI 10.1002/sia.3836; VERIFIED per spec §9).  The engine does
not force a multiplet-peak decomposition; oxidation-state ASSIGNMENT is out
of scope (parked).

Structure (validated against 40+ expert U 4f fits in docs/autofit/test_data;
see PROGRESS.md "U 4f design extraction"):

- **Main doublet**: LACX 4f7/2 (free α/β/m — "FitAllFree" expert practice)
  + 4f5/2 amplitude- and shape-linked at the spin-orbit splitting.
- **Satellite doublet**: the U(IV) shake-up satellite rides BOTH mains — one
  Voigt pair (sat7/2 offset-linked to the main; sat5/2 linked to sat7/2 at
  the same splitting).  This one pair explains both observed satellites
  (main+~6.3 eV and main+~17.2 eV = 6.3 + Δso).
- Everything fits JOINTLY in one window; N 1s overlap is handled by
  composing this module with the N 1s module via ``resolve`` (spec §2).

Safeguards (spec §3.2, retained):
- **Bounded asymmetry**: LACX α/β confined to a labeled-set-calibrated
  window so the tail cannot silently absorb a genuinely separable feature.
- The residual/proposal pass (engine-level) flags unexplained tail
  structure as a possible separate component without forcing
  over-parameterization.
"""

from __future__ import annotations

from typing import Optional

from ..grammar import (
    BackgroundType,
    CandidateModel,
    ComponentSlot,
    LineShape,
    Phase,
)
from . import register_region

REGION = "U 4f"

# ── Constants (cited or flagged) ────────────────────────────────────────────

# Spin-orbit splitting: 10.8–10.9 eV — VERIFIED (Ilton & Bagus 2011,
# 10.1002/sia.3836; NIST SRD 20 gives 10.8, see data/xps/elements-actinides.json
# U-4f7/2.spin_orbit).  Expert fits use 10.90 exactly.  Bounded, not fixed,
# so small calibration deviations remain expressible.
U4F_SPLITTING_RANGE = (10.75, 10.95)

# Theoretical 4f7/2:4f5/2 area ratio 4:3 → 0.75 — VERIFIED (Bagus et al.,
# 10.1063/1.4846135; NIST SRD 20 area_ratio 0.75).  Expert fits use a
# RELAXED empirical ratio 0.65–0.75 (spec §3.2: "relaxed empirical ratio,
# not a contradiction").  Default 0.75, bounded relaxation; the bounds are
# UNVERIFIED-empirical (labeled set ± margin).
U4F_RATIO_DEFAULT = 0.75
U4F_RATIO_RANGE = (0.60, 0.85)

# 4f7/2 BE window (corrected frame): inside the NIST-curated, oxidation-
# widened expected region 375.5–383.0 eV (data/xps/elements-actinides.json,
# nist-srd-20; metal nominal 377.3, real samples oxidized → higher).
# Tightened to the U(IV)-like practice of the labeled set (379.5–380.6):
# UNVERIFIED-calibration widths around cited anchors.
U4F72_WINDOW = (378.0, 382.5)
# 4f5/2 fallback window = 7/2 window + splitting (matching only; the fitted
# center is expression-driven).
U4F52_WINDOW = (388.75, 393.45)

# Main FWHM range — UNVERIFIED-empirical (labeled set 2.44–2.74 eV).
U4F_MAIN_FWHM_RANGE = (1.5, 3.5)

# Bounded-asymmetry safeguard (spec §3.2): LACX exponents confined around
# the labeled set (α 0.96–1.24, β 2.23–2.85) with margin.  UNVERIFIED-
# empirical — deliberately narrower than the generic (0.1, 5.0) so the tail
# cannot silently absorb a separable overlapping feature; the residual pass
# flags what the bounded tail cannot express.
U4F_LACX_ALPHA_RANGE = (0.5, 2.0)
U4F_LACX_BETA_RANGE = (1.0, 4.5)
# Gaussian kernel width in DATA POINTS (labeled set 0–8.2) — UNVERIFIED.
U4F_LACX_M_RANGE = (0.0, 100.0)

# Shake-up satellite offset from its main line: literature U(IV)
# satellite-to-main separation ≈ 6.8–7.1 eV (Ilton & Bagus 2011; Schindler
# et al., GCA 73 (2009) 2488, 10.1016/j.gca.2009.02.008); labeled set fits
# 6.07–6.38 eV.  Envelope brackets both — UNVERIFIED-calibration.
U4F_SAT_OFFSET_RANGE = (5.5, 8.5)
# Satellite-PAIR separation window for the free-separation candidates: the
# labeled set fits the pair 11.2 eV apart while the core splitting is 10.9
# (satellite separations need not track the core splitting) — bracketed
# around both; UNVERIFIED-calibration.
U4F_SATPAIR_SEP_RANGE = (10.5, 12.0)
# Satellite width — UNVERIFIED-empirical (labeled set 2.09–3.30 eV).
U4F_SAT_FWHM_RANGE = (1.5, 4.5)
# Satellite absolute fallback windows: DERIVED from the cited/flagged
# constants above (main window ± satellite offsets; used for slot MATCHING
# only — fitted centers are expression-driven off the mains).
U4F_SAT72_WINDOW = (U4F72_WINDOW[0] + U4F_SAT_OFFSET_RANGE[0],
                    U4F72_WINDOW[1] + U4F_SAT_OFFSET_RANGE[1])
U4F_SAT52_WINDOW = (U4F_SAT72_WINDOW[0] + U4F_SATPAIR_SEP_RANGE[0],
                    U4F_SAT72_WINDOW[1] + U4F_SATPAIR_SEP_RANGE[1])

# Background: the labeled U 4f fits all use the 'smart' (constrained
# Shirley) background — adopted to match expert practice; UNVERIFIED
# methodological choice (plain Shirley is the spec default elsewhere).
U4F_BACKGROUND = BackgroundType.SMART
### Tab model

`TabManager` (a class in `templates/index.html`) holds `tabs[]` and an
`activeId`. Two tab types share the array:

- **Spectrum tab:** has `rawBE`, `rawIntensity`, `peaks`, `fitResult`, `ccShift`, `manualAnchors`, `lineWidth`, `ui` (form field snapshot incl. bg settings, ROI, charge correction method).
- **Stack tab** (`isStack: true`): viewer-only container for references to other spectrum tabs. Has `entries[{id, sourceTabId, color, visible, showFit}]`, `lineWidth`, `verticalOffset`, `_nextColorIdx`. No raw data of its own — entries resolve their source tab at render time.

Lifecycle: `createTab`, `createStackTab`, `activateTab`, `closeTab`,
`_syncActiveToRecord` (writes state-back-to-tab on switch-away). Drag-and-drop
tab reordering exists.

### Peak Object Schema — core fields

(Non-exhaustive. Additional optional fields appear for multiplet linkage, fix-flags per parameter, auto-fit asymmetry bounds, etc. Search the source for `defaultPeak` to see the full shape.)

```js
{
  id, name, color, visible,
  center, fwhm, amplitude,
  shape,       // 'Gaussian'|'Lorentzian'|'Voigt'|'GL'|'asym-GL'|'DS'|'DSG_LA'|'LACX'
  glMix,       // 0–100 (Gauss → Lorentz)
  asymmetry,   // asym-GL asymmetry index
  dsAlpha, dsGamma,                       // DS params
  laAlpha, laBeta, laM,                   // DS+G params (laAlpha=α, laBeta=Lorentzian half-width, laM=Gauss FWHM)
  caAlpha, caBeta, caM,                   // CasaXPS LA params (caM is in DATA POINTS, not eV)
  linked, linkOffset, linkRatio,          // multiplet linkage to parent peak
  isChargeReference,                      // marks this peak as the cc anchor
}
```

### Lineshapes

| ID | Description |
|----|-------------|
| `Gaussian` | Pure Gaussian |
| `Lorentzian` | Pure Lorentzian |
| `Voigt` | Pseudo-Voigt, fixed η = 0.5 on BOTH sides (A03, 2026-09-22: the request sends `gl_ratio: 0.5, fix_gl_ratio: true`; until then the server fitted η FREE from 0.3 while the page drew, integrated and exported 0.5). Use `GL` to fit the mix. |
| `GL` | Pseudo-Voigt with adjustable GL mixing (0–100) |
| `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
| `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
| `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + integer-kernel Gauss conv. Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |

**What the page draws must be what the server fitted.** Two harnesses pin
it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
page's own `peakToBackendSpec`, fits it with `fitting.run_fit`, applies the
result with `_applyBackendParams` and requires `evalPeakArray` on the fitted
grid to equal `individual_peaks[].y` for every shape (it also pins the
Python twin `autofit.reference.peak_to_backend_spec` to the page's builder,
shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
each shape's FREE parameters across the fit's bounds. Both were added in A03
(2026-09-22) after a "Voigt" was found to be fitted with η free while drawn
at 0.5. Tracked gaps, `todo` in both files: LACX with m > 0 (the page draws
a rounded integer kernel; the server fits m continuously — the `caM` clamp
unit) and DS+G with m ≥ 0.05 (the page's quadrature `laCasaXPS` sizes its
step to the Lorentzian core, not the Gaussian kernel, and is wrong by up to
80 % of amplitude across the fitted β/m range — 1e52 × at β = 2, m = 0.05;
0 of 865 committed components use DS+G; its own unit). Details in
`docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.

---

## Design Rules

### Thresholds on data-scaled quantities fail

XPS spans many orders of magnitude within one spectrum, so any absolute

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/lineshape_roundtrip.test.js tests/js/lineshape_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -m pytest -p no:cacheprovider tests/test_voigt_contract.py tests/autofit/test_u4f_parity_battery.py -q' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 115ms:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pytest/__main__.py", line 9, in <module>
    raise SystemExit(pytest.console_main())
                     ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -m pytest -s -p no:cacheprovider tests/test_voigt_contract.py tests/autofit/test_u4f_parity_battery.py -q' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "rg --files | rg '(optimizer_disagreement|AGENTS.md|conftest.py)'; sed -n '1,210p' tests/js/lineshape_parity.test.js; rg -n 'backend_peak_specs|_backendParams' autofit/reference.py; rg -n '_applyBackendParams|startPeaks|syncLinkedPeaks|n_perturb' templates/index.html | head -55; sed -n '7910,8020p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
scripts/optimizer_disagreement_targets.js
scripts/optimizer_disagreement_run_perturb.py
scripts/optimizer_disagreement_run_starts.py
scripts/optimizer_disagreement_analyze_starts.py
scripts/optimizer_disagreement_analyze_perturb.py
scripts/optimizer_disagreement_run.py
scripts/optimizer_disagreement_analyze.py
tests/conftest.py
// Lineshape parity harness — the invariant that was missing until the
// 2026-08-30 asym-GL/LACX bug (see docs/autofit/codex/asym_gl_mismatch_*).
//
// Two DISTINCT invariants, both silently unchecked before this file:
//
//   (A) FRONTEND vs BACKEND: for every shape, the frontend's array evaluator
//       (evalPeakArray, called for chart data build paths) must numerically
//       match fitting.py's registered shape function (_SHAPE_FUNCS) over a
//       realistic BE grid and parameter sweep, including m>0 for the two
//       Gaussian-convolved shapes (DSG_LA, LACX). This is what asym-GL failed
//       — the frontend chart and the backend fit disagreed by ~10% of peak
//       height on real U 4f data.
//
//   (B) FRONTEND vs FRONTEND: the two JS evaluators for a single point,
//       evalPeak(x, p) and evalPeakArray(...)[i] at the same x, must agree
//       with each other. This is a SEPARATE bug class from (A) — even a
//       frontend that's perfectly correct vs. the backend can still disagree
//       with itself if it has two code paths computing "the same" curve.
//       This is exactly what the LACX per-point fallback did: evalPeak()
//       silently ignores Gaussian convolution (m) while evalPeakArray()
//       applies it correctly, so any evalPeak() caller — export/save/Results
//       panel — showed a materially different number than the chart.
//
// NOTE on (B)'s exact formulation: convolution is a GRID operation (it needs
// neighboring points to define a kernel), so it is not well-posed to ask for
// "the convolved value at an isolated point" via evalPeakArray([x], p)[0] —
// with only one point in the array, laTrueCasaXPS_array's own peak-finding +
// renormalization logic collapses to a degenerate constant (amplitude,
// trivially, for ANY x/alpha/beta) regardless of what evalPeak() does. That
// isn't a meaningful comparison for any shape, correct or not. Instead (B)
// asserts evalPeak(x, p) against evalPeakArray(realisticGrid, p)[indexOfX] —
// same real grid the chart/export code actually uses — which is the
// meaningful version of "do the two evaluators agree."

const { test } = require('node:test');
const assert = require('node:assert');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');

function extract(re, name) {
  const m = html.match(re);
  assert.ok(m, name + ' not found in templates/index.html');
  return m[0];
}

// ── Extract the shipped lineshape block (gaussian … evalPeakArray) ─────────
const evalCtx = eval('(function(){\n'
  + extract(/function gaussian\(x, center, fwhm\) \{[\s\S]*?\nfunction evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}/,
            'lineshape block') + '\n'
  + 'return { evalPeak, evalPeakArray };\n})()');
const { evalPeak, evalPeakArray } = evalCtx;

// ── Python bridge: call fitting.py's OWN _SHAPE_FUNCS, never a reimpl ──────
// A git-worktree checkout does NOT get its own venv/ (confirmed 2026-07-11,
// see memory xps-autofit-session-ops) — the venv only exists in the main
// repo checkout, so a worktree run must fall back to that absolute path.
function findPython() {
  const candidates = [
    process.env.XPS_PYTHON,
    path.join(REPO_ROOT, 'venv/bin/python3'),          // main checkout's own venv
    '/Users/skyefortier/xps-app/venv/bin/python3',      // worktree -> main repo venv
    'python3',
  ].filter(Boolean);
  for (const c of candidates) {
    try {
      if (c === 'python3' || fs.existsSync(c)) return c;
    } catch { /* keep looking */ }
  }
  return 'python3';
}
const PYTHON = findPython();
const BRIDGE = path.join(__dirname, 'lineshape_parity_backend.py');

function backendEval(shape, params, x) {
  const input = JSON.stringify({ shape, params, x });
  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
  return JSON.parse(out);
}

// ── Realistic BE grid: 10 eV window, 0.05 eV step (200 pts) around center ──
function grid(center) {
  const x = [];
  for (let i = 0; i < 200; i++) x.push(center - 5.0 + 0.05 * i);
  return x;
}

function maxRelDiff(a, b, amplitude) {
  let m = 0;
  for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i]));
  return m / amplitude;
}

// ── One representative peak per shape (distinctive, non-default values) ───
const AMPLITUDE = 17794.0;
const CENTER = 391.8;
const FWHM = 1.83;

function basePeak(shape) {
  return {
    id: 1, name: 'P', color: '#000', center: CENTER, amplitude: AMPLITUDE, fwhm: FWHM,
    shape,
    glMix: 55, asymmetry: 0.59,
    dsAlpha: 0.22, dsGamma: 0.05,
    laAlpha: 0.18, laBeta: 0.7, laM: 0.9,
    caAlpha: 1.4, caBeta: 0.8, caM: 50,
    linked: null, isChargeReference: false, visible: true,
  };
}

// backend shape id + kwargs builder per frontend shape
const BACKEND = {
  'Gaussian':   p => ({ shape: 'gaussian',       params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm } }),
  'Lorentzian': p => ({ shape: 'lorentzian',      params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm } }),
  'Voigt':      p => ({ shape: 'pseudo_voigt_gl', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, gl_ratio: 0.5 } }),
  'GL':         p => ({ shape: 'pseudo_voigt_gl', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, gl_ratio: p.glMix / 100 } }),
  'asym-GL':    p => ({ shape: 'asymmetric_gl',   params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, asymmetry: p.asymmetry, gl_ratio: p.glMix / 100 } }),
  'DS':         p => ({ shape: 'doniach_sunjic',  params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.dsAlpha, gamma_asym: p.dsGamma } }),
  'DSG_LA':     p => ({ shape: 'ds_g',            params: { amplitude: p.amplitude, center: p.center, alpha: p.laAlpha, beta: p.laBeta, m_gauss: p.laM } }),
  'LACX':       p => ({ shape: 'la_casaxps',      params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.caAlpha, beta: p.caBeta, m: p.caM } }),
};

const TIGHT_TOL = 1e-6; // relative to amplitude; both sides are closed-form double-precision math

// ── (A) Frontend vs backend, shapes that must match tightly ───────────────
// Gaussian/Lorentzian/GL/Voigt/DS: no convolution, identical formulas on
// both sides — proven to agree by the earlier Codex sweep. asym-GL: fixed
// by unit-1 commit 1 (frontend rewritten to the backend's piecewise
// two-constant-width formula) — this assertion is what proves that fix.
for (const shape of ['Gaussian', 'Lorentzian', 'GL', 'Voigt', 'DS', 'asym-GL']) {
  test(`(A) frontend vs backend parity: ${shape}`, () => {
    const p = basePeak(shape);
    const x = grid(p.center);
    const jsY = evalPeakArray(x, p);
    const { shape: beShape, params } = BACKEND[shape](p);
    const beY = backendEval(beShape, params, x);
    const rel = maxRelDiff(jsY, beY, p.amplitude);
    assert.ok(rel < TIGHT_TOL,
      `${shape}: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
  });
}

// ── (A) Frontend vs backend, shapes with a KNOWN, tracked residual ────────
// LACX and DSG_LA were BOTH suspected (2026-08-30 scoping) to share one root
// cause — a Gaussian-conv kernel-construction difference that should grow
// monotonically with m. An explicit m=0,1,2,5,10,50 sweep (see
// docs/autofit/codex git-archaeology notes / session record) DISPROVED that
// for DSG_LA: the two shapes have DIFFERENT, unrelated defects. Do not
// re-merge these into one explanation without re-running the sweep.
//
//   LACX: error GROWS with m as hypothesized (m=0: 0.0000%, m=1: 0.0000%,
//   m=2: 0.0001%, m=5: 0.0061%, m=10: 0.0312%, m=50: 0.1496% of amplitude) —
//   consistent with backend continuous-m + ceil(3.5*sigma) kernel vs
//   frontend rounded-m + 2m+1 kernel. Small, monotonic, unit-2 material.
//
//   DSG_LA: error is HIGHEST at m=0 (101.8% at laAlpha=0.18/laBeta=0.7 —
//   the frontend curve is ~zero everywhere) and DECREASES as m grows —
//   the OPPOSITE shape from LACX. Root cause is NOT a kernel-discretization
//   gap: JS laCasaXPS() (templates/index.html) sets
//   `sigma = mGauss / (2*sqrt(2*ln2))`, so mGauss -> 0 drives sigma -> 0 and
//   its Gaussian-weighted quadrature divides by `2*sigma*sigma` — a literal
//   division-by-zero/degenerate-weight bug, not a discretization mismatch.
//   NARROWER than the above sweep alone suggests, though: measured against
//   the SCHEMA DEFAULT (laM=0.4, laAlpha=0.10, laBeta=0.3, 2026-08-31):
//   laM=0 -> 100%, 0.1 -> 11.8%, 0.2 -> 0.05%, 0.4 (DEFAULT) -> 0.02%,
//   0.6+ -> 0%. The shipped default is NOT affected; only laM at or very
//   near zero (roughly <=0.1) is, and when it fires the peak visibly
//   vanishes/flattens on screen — loud, not a quiet export-only drift like
//   LACX/asym-GL were. Its own unit, normal priority — do not fold it into
//   the LACX kernel-construction fix, and do not hold anything for it.
test('(A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)', { todo: 'unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)' }, () => {
  const p = basePeak('LACX');
  const x = grid(p.center);
  const jsY = evalPeakArray(x, p);
  const { shape: beShape, params } = BACKEND.LACX(p);
  const beY = backendEval(beShape, params, x);
  const rel = maxRelDiff(jsY, beY, p.amplitude);
  assert.ok(rel < TIGHT_TOL,
    `LACX: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
});

test('(A) frontend vs backend parity: LACX at m=0 (no convolution)', () => {
  const p = basePeak('LACX');
  p.caM = 0;
  const x = grid(p.center);
  const jsY = evalPeakArray(x, p);
  const { shape: beShape, params } = BACKEND.LACX(p);
  const beY = backendEval(beShape, params, x);
  const rel = maxRelDiff(jsY, beY, p.amplitude);
  assert.ok(rel < TIGHT_TOL,
    `LACX at m=0: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
});

test('(A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed', { todo: 'DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above' }, () => {
  const p = basePeak('DSG_LA');
  const x = grid(p.center);
  const jsY = evalPeakArray(x, p);
  const { shape: beShape, params } = BACKEND.DSG_LA(p);
  const beY = backendEval(beShape, params, x);
  const rel = maxRelDiff(jsY, beY, p.amplitude);
  assert.ok(rel < TIGHT_TOL,
    `DSG_LA: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
});

// FIXED (fix-dsgla-m0-collapse): for laM below the backend's 0.001 delta-
// kernel threshold (_ds_g_dscore_gauss, `m_gauss < 0.001` → normalised DS
// core, no convolution), evalPeakArray now takes a grid-aware branch that
261:    def backend_peak_specs(self) -> list[dict]:
6289:function _applyBackendParams(p, par) {
6314:    _applyBackendParams(p, ipeak.params);
7273:        n_perturb: 3,
7546:    _applyBackendParams(p, par);
7572:// an ordinary server fit (runFit's opts.startPeaks); the live model is written
7592:  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
7624:    // opts.startPeaks: the request starts from an adopted alternative; the live
7626:    const startModel = opts.startPeaks || state.peaks;
7661:      n_perturb: 3,
7751:    if (e && e.transportFailure && opts.startPeaks) {
// History: from the initial commit (f20d71b) until this unit the update
// step solved JtJ.dp = +Jt.r with r = data - model, i.e. an ASCENT step, so
// every step was rejected, lambda inflated past 1e8 and the loop returned
// the STARTING model announced as "Fit complete (local LM)". The
// convergence test also compared chi-square with itself after acceptance.
// Both are pinned by tests/js/local_lm_descent.test.js, which replays the
// committed lab project; the proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md.
function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
  const maxIter = Number.isFinite(options.maxIterations) ? options.maxIterations : 3000;
  const fail = (message, iterations) => {
    _hideFitSpinner();
    document.getElementById('sb-msg').textContent = 'Local fit failed';
    notify('Local fit did not converge: ' + message + ' Previous peaks and result kept.', 'red', true);
    return { success: false, engine: 'local', message, iterations: iterations || 0 };
  };
  if (!Array.isArray(be) || be.length < 2 ||
      !Array.isArray(bgSubtracted) || bgSubtracted.length !== be.length ||
      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
    return fail('invalid or non-finite data in the fitting region.');
  }
  // POISSON WEIGHTS (unit W1): the same weighting fitting.run_fit applies on
  // the server — sigma = sqrt(raw counts), floored at 1, where the raw
  // counts are the background-subtracted signal plus the background.
  const _w = be.map((_, i) => 1 / Math.sqrt(Math.max(bgSubtracted[i] + bgIntensity[i], 1)));
  // Work on copies: live peaks are touched only on success.
  const work = state.peaks.map(p => ({ ...p }));
  if (!work.length) return fail('no peaks to fit.');
  const workPeak = id => work.find(q => q.id === id);

  const freeParams = [];
  const paramMap = [];
  for (const p of work) {
    if (!p.linked) {
      if (!p.fixCenter)    { freeParams.push(p.center);    paramMap.push({id: p.id, param: 'center'}); }
      if (!p.fixFwhm && p.shape !== 'DSG_LA') { freeParams.push(p.fwhm); paramMap.push({id: p.id, param: 'fwhm'}); }
      if (!p.fixAmplitude) { freeParams.push(p.amplitude); paramMap.push({id: p.id, param: 'amplitude'}); }
      if ((p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) {
        freeParams.push(p.glMix); paramMap.push({id: p.id, param: 'glMix'});
      }
      if (p.shape === 'asym-GL' && !p.fixAsymmetry) {
        freeParams.push(p.asymmetry); paramMap.push({id: p.id, param: 'asymmetry'});
      }
      if (p.shape === 'DS' && !p.fixDsAlpha) {
        freeParams.push(p.dsAlpha); paramMap.push({id: p.id, param: 'dsAlpha'});
      }
      if (p.shape === 'DS' && !p.fixDsGamma) {
        freeParams.push(p.dsGamma); paramMap.push({id: p.id, param: 'dsGamma'});
      }
      if (p.shape === 'DSG_LA') {
        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
      }
      if (p.shape === 'LACX') {
        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
        if (!p.fixCaM)     { freeParams.push(Number.isFinite(p.caM)     ? p.caM     : 50);  paramMap.push({id: p.id, param: 'caM'}); }
      }
    }
  }
  if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');

  // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
  // (owner decision 2026-09-18: zero allowed in both engines; a component at
  // its floor is an explicit outcome). The active-set step holds a parameter
  // pushed into the wall, and paramScale is floored at 1, so a zero amplitude
  // is a valid, stationary point rather than a division by zero.
  function clamp(param, v) {
    if (param === 'fwhm')         return Math.max(0.1, Math.min(15, v));
    if (param === 'amplitude')    return Math.max(0, v);
    if (param === 'glMix')        return Math.max(0, Math.min(100, v));
    if (param === 'asymmetry')    return Math.max(0, Math.min(1, v));
    if (param === 'dsAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'dsGamma')      return Math.max(0, Math.min(5.0, v));
    if (param === 'laAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'laBeta')       return Math.max(0.05, Math.min(2.0, v));
    if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
    if (param === 'caAlpha')      return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caBeta')       return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caM')          return Math.max(0,   Math.min(499, Math.round(v)));
    return v;
  }
  const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];

  function applyParams(params) {
    for (let i = 0; i < params.length; i++) {
      const { id, param } = paramMap[i];
      const p = workPeak(id);
      if (p) p[param] = clamp(param, params[i]);
    }
    // Linked peaks follow their parent: centre + offset, amplitude x ratio,
    // and every lineshape parameter (the same constraint set the backend
    // enforces through lmfit expressions).
    for (const q of work) {
      if (!q.linked) continue;
      const parent = workPeak(q.linked);
      if (!parent) continue;
      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
      if (Number.isFinite(q.linkRatio))  q.amplitude = parent.amplitude * q.linkRatio;
      q.fwhm = parent.fwhm;
      for (const k of LINK_SYNC_KEYS) if (parent[k] !== undefined) q[k] = parent[k];
    }
  }

  function rawResiduals(params) {
    applyParams(params);
    const model = evalAllPeaks(be, work);
    return be.map((_, i) => bgSubtracted[i] - model[i]);

 exited 2 in 1662ms:

==================================== ERRORS ====================================
________________ ERROR collecting tests/test_voigt_contract.py _________________
tests/test_voigt_contract.py:13: in <module>
    import fitting
fitting.py:33: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
__________ ERROR collecting tests/autofit/test_u4f_parity_battery.py ___________
tests/autofit/test_u4f_parity_battery.py:23: in <module>
    import battery_common as bc
tests/autofit/battery_common.py:16: in <module>
    from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
autofit/parity.py:29: in <module>
    from fitting import (
fitting.py:33: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
=========================== short test summary info ============================
ERROR tests/test_voigt_contract.py - FileNotFoundError: [Errno 2] No usable t...
ERROR tests/autofit/test_u4f_parity_battery.py - FileNotFoundError: [Errno 2]...
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 1.42s

 exited 1 in 27518ms:
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Subtest: (A) frontend vs backend parity: Gaussian
not ok 1 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1165.006074
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
    startSubtestAfterBootstrap (node:internal/test_runner/harness:296:17)
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
not ok 2 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1153.421056
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: GL
not ok 3 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1228.251534
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: Voigt
not ok 4 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1210.029151
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DS
not ok 5 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1180.558156
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
not ok 6 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1159.381926
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)
not ok 7 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1211.718505
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:174:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:179:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX at m=0 (no convolution)
not ok 8 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1272.770701
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:185:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:191:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed
not ok 9 - (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed # TODO DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above
  ---
  duration_ms: 1163.139402
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:197:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:202:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
not ok 10 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1125.701673
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:221:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:228:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
not ok 11 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1147.77768
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:221:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:228:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
not ok 12 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1187.890864
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:221:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:228:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
not ok 13 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1165.784527
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:221:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:228:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
not ok 14 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1144.529264
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:238:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:245:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 15 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.3139
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 16 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.13082
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 17 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.153966
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 18 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.142835
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 19 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.192075
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 20 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.236445
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
ok 21 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
  ---
  duration_ms: 10.61236
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 22 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.551093
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:267:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7170.363795150584, rel diff=24.2055%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:274:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (C) evalPeak() has no direct callers outside evalPeakArray()
ok 23 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 2.81218
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
not ok 24 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1072.882577
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:364:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:365:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
not ok 25 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1138.75829
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:364:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:365:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Voigt
not ok 26 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1072.024027
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:364:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:365:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: GL
not ok 27 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1078.85754
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:364:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:365:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
not ok 28 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1073.339359
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:364:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:365:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DS
not ok 29 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1108.013119
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:364:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:365:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
not ok 30 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1129.780314
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:364:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:365:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
not ok 31 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1065.64714
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:364:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:365:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP
not ok 32 - (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1065.60436
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:373:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP
not ok 33 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1104.000461
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:356:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:373:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
not ok 34 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1157.920144
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
not ok 35 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1153.869109
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
not ok 36 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1230.389182
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
not ok 37 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1208.984034
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
not ok 38 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1170.023061
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
not ok 39 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1177.753402
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 40 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1228.456112
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
not ok 41 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX # TODO LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit
  ---
  duration_ms: 1288.137518
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
not ok 42 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1132.644349
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:132:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:139:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
not ok 43 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1123.410743
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:147:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:149:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
not ok 44 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1150.831704
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:161:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:162:33)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
not ok 45 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1183.026671
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:172:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:180:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
not ok 46 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1152.619088
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:190:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:199:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
1..46
# tests 46
# suites 0
# pass 8
# fail 31
# cancelled 0
# skipped 0
# todo 7
# duration_ms 27567.252402

codex
I found that the η measurement depends on an uncommitted old target file: it copies the input specs for the “free” baseline without explicitly freeing η. Fresh targets generated on this branch would therefore compare fixed η against itself. I also confirmed that the uncertainty panel tells Voigt users to “unlock the padlock,” although Voigt has no mix padlock.

The test runs hit the read-only sandbox’s temporary-directory probe. I’m trying an in-memory setup that avoids that probe and keeps the checkout unchanged.
exec
/bin/zsh -lc "sed -n '1,190p' scripts/optimizer_disagreement_targets.js; sed -n '248,282p' autofit/reference.py; sed -n '7615,7642p' templates/index.html; sed -n '5080,5145p' templates/index.html; cat tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
#!/usr/bin/env node
// Build the fit targets for the optimiser-disagreement frequency measurement
// (investigation 2026-09-18). NO app code is changed: the requests are built
// by the SHIPPED frontend functions extracted from templates/index.html
// (peakToBackendSpec, _bgWindowIndices) and static/js/batch_propagation.js,
// so every target is exactly what Run Fit would send.
//
// Two kinds of start per committed project:
//   batch : the region's first fitted tab is propagated onto every other tab
//           of the same region, as runPropagation does (scaled clone, source
//           background/ROI/charge shift) — a start that is NOT yet a solution;
//   own   : each fitted tab's own saved model and settings — what pressing
//           Run Fit again on a saved project sends.
// Usage: node scripts/optimizer_disagreement_targets.js <tabs.json> > targets.json
const fs = require('fs'); const path = require('path'); const crypto = require('crypto');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) { const re = new RegExp('^(async )?function ' + name + '\\('); const s = lines.findIndex(l => re.test(l)); if (s < 0) throw new Error(name); let d = 0, seen = false;
  for (let i = s; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { d++; seen = true; } else if (ch === '}') d--; } if (seen && d === 0) return lines.slice(s, i + 1).join('\n'); } }
const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
const state = { peaks: [] };
const fns = new Function('state', 'getPeak', extractFn('peakToBackendSpec') + '\n' + extractFn('_bgWindowIndices') + '\nreturn { peakToBackendSpec, _bgWindowIndices };')(state, id => state.peaks.find(p => p.id === id));
const tabs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const region = name => name.replace(/_\d+$/, '').trim();
function request(kind, project, tab, peaks, ui, ccShift, rawBE, rawIntensity, sourceName) {
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const lo = isNaN(roiMin) ? -Infinity : roiMin, hi = isNaN(roiMax) ? Infinity : roiMax;
  const be = [], inten = [];
  rawBE.forEach((b, i) => { const c = b - (isNaN(ccShift) ? 0 : ccShift); if (c >= lo && c <= hi) { be.push(c); inten.push(rawIntensity[i]); } });
  if (be.length < 10 || !peaks.length) return null;
  const win = fns._bgWindowIndices(be, parseFloat(ui.bgStart), parseFloat(ui.bgEnd));
  state.peaks = peaks;
  const specs = peaks.map(fns.peakToBackendSpec);
  const bgType = ui.bgType || 'shirley';
  if (bgType === 'manual') return null;        // anchors are per-tab hand work; out of scope for a method comparison
  const t = { kind, project, region: region(tab), tab, source: sourceName || null, be, inten,
    background: { method: bgType, start_idx: win.i0, end_idx: win.i1 + 1, endpoint_avg: parseInt(ui.endpointAvg) || 1 },
    specs, n_peaks: peaks.length, shapes: peaks.map(p => p.shape) };
  t.id = crypto.createHash('sha1').update(JSON.stringify([t.kind, be, inten, specs, t.background])).digest('hex').slice(0, 12);
  return t;
}
const out = []; const seen = new Set();
const byProject = {};
for (const t of tabs) { if (!t.peaks || !t.peaks.length) continue; (byProject[t.project] ||= []).push(t); }
for (const [project, list] of Object.entries(byProject)) {
  const groups = {};
  for (const t of list) (groups[region(t.name)] ||= []).push(t);
  for (const g of Object.values(groups)) {
    for (const t of g) { const r = request('own', project, t.name, JSON.parse(JSON.stringify(t.peaks)), t.ui, t.ccShift, t.rawBE, t.rawIntensity); if (r && !seen.has(r.id)) { seen.add(r.id); out.push(r); } }
    const src = g[0]; const srcMax = Math.max(...src.rawIntensity);
    for (const tgt of g.slice(1)) {
      const scale = srcMax > 0 ? Math.max(...tgt.rawIntensity) / srcMax : 1;
      const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
      const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
      const r = request('batch', project, tgt.name, cloned, ui, src.ccShift, tgt.rawBE, tgt.rawIntensity, src.name);
      if (r && !seen.has(r.id)) { seen.add(r.id); out.push(r); }
    }
  }
}
process.stdout.write(JSON.stringify(out));
process.stderr.write(`targets: ${out.length} (own ${out.filter(t => t.kind === 'own').length}, batch ${out.filter(t => t.kind === 'batch').length})\n`);
        return i_start, i_end

    @property
    def bg_method(self) -> str:
        return self.ui.get("bgType") or "shirley"

    @property
    def endpoint_avg(self) -> int:
        try:
            return max(1, int(self.ui.get("endpointAvg", 1)))
        except (TypeError, ValueError):
            return 1

    def backend_peak_specs(self) -> list[dict]:
        return [peak_to_backend_spec(p, self.peaks) for p in self.peaks]

    @property
    def region_midpoint(self) -> Optional[float]:
        lo, hi = self._roi_bounds()
        if np.isfinite(lo) and np.isfinite(hi):
            return 0.5 * (lo + hi)
        be = self.corrected_be
        return 0.5 * (float(be.min()) + float(be.max())) if len(be) else None

    def region_guess(self) -> str:
        """Coarse region label from the ROI midpoint (mirrors isC1sTab logic)."""
        mid = self.region_midpoint
        if mid is None:
            return "unknown"
        for label, lo, hi in _REGION_WINDOWS:
            if lo <= mid <= hi:
                return label
        return "unknown"


    const bgType  = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
    // EVERY request input is read from the owner before the upload await:
    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
    // request could carry A's spectrum with B's averaging and anchors).
    // opts.startPeaks: the request starts from an adopted alternative; the live
    // model is still the student's until this fit succeeds (useAlternative).
    const startModel = opts.startPeaks || state.peaks;
    const peakSpecs = startModel.map(peakToBackendSpec);
    // scattered-starts check: decided HERE, with the other request inputs,
    // before the first await (a tab switch during the upload must not turn it off)
    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
    // the live model and its fit context as the student pressed the button: a
    // result must not be written over a model that was edited while it ran
    const ctxAtRequest = _startsLiveKey();
    const fitMethod = document.getElementById('fit-method').value;
    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    // Transport failures (server unreachable, timeout, non-JSON reply) are
// Note: glMix uses the frontend 0-100 slider scale (= backend gl_ratio × 100).
// Do NOT cross-map look-alike params across shapes (e.g. DSG_LA's laAlpha vs
// LACX's caAlpha) — they are mathematically different parameters that share
// a Greek letter.
const SHAPE_PARAM_SCHEMA = {
  'Gaussian':   {},
  'Lorentzian': {},
  'Voigt':      {},
  'GL':         { glMix: 30, fixGlMix: false },
  'asym-GL':    { glMix: 30, fixGlMix: false, asymmetry: 0.0, fixAsymmetry: false },
  'DS':         { dsAlpha: 0.10, fixDsAlpha: false, dsGamma: 0.0, fixDsGamma: false },
  'DSG_LA':     { laAlpha: 0.10, fixLaAlpha: false, laBeta: 0.3, fixLaBeta: false, laM: 0.4, fixLaM: false },
  'LACX':       { caAlpha: 1.0,  fixCaAlpha: false, caBeta: 1.0, fixCaBeta: false, caM: 50, fixCaM: true },
};

// Which peak field holds the effective eV WIDTH for a given shape. Every
// shape stores its width in the top-level `fwhm` EXCEPT DS+G (DSG_LA), whose
// width is the Gaussian FWHM `laM` (DS+G's `fwhm` field is display-only /
// readonly and excluded from fitting — see renderShapeControls / runFit).
// Used to CARRY the width across a shape switch instead of resetting it to a
// per-shape default. The two accessors return the value field and its
// lock (fix-flag) field respectively.
function _widthField(shape) { return shape === 'DSG_LA' ? 'laM' : 'fwhm'; }
function _widthFixField(shape) { return shape === 'DSG_LA' ? 'fixLaM' : 'fixFwhm'; }

// Switch ONE peak object's lineshape IN PLACE. Pure — no DOM, no state, no
// rendering (_switchPeakShape wraps it with the family / undo / render / plot
// orchestration; the JS round-trip tests exercise it directly).
//
// Preserves the parameters that carry over — center and amplitude (untouched
// top-level fields), and the effective WIDTH (mapped across the laM↔fwhm
// boundary, not reset) — and seeds a default ONLY for a parameter the new
// shape genuinely introduces that the peak does not already carry.
//
// Round-trip guarantee (A → B → A returns the peak's ACTIVE parameters — the
// ones evalPeak reads for shape A — to their originals, so the rendered curve
// is unchanged):
//   1. Non-width shape params are NEVER deleted, so a value the peak already
//      carries (e.g. DS+G's laBeta) survives the excursion through B and is
//      not re-defaulted coming back. This replaces the old
//      delete-then-default behaviour that silently reset fitted values
//      (observed: laBeta 0.05 → 0.30, laM 3.11 → 0.40 on DS+G → GL → DS+G).
//   2. The width is MAPPED, not reset: the eV width is copied across the
//      laM↔fwhm boundary. The map is the identity in eV, so it is invertible
//      and the round-trip restores the original width (and its lock).
function _applyShapeSwitch(peak, newShape) {
  const oldShape = peak.shape;
  if (oldShape === newShape || !(newShape in SHAPE_PARAM_SCHEMA)) return;
  // 1. carry the effective width (value + lock) across the laM↔fwhm boundary
  const oldWF = _widthField(oldShape), newWF = _widthField(newShape);
  if (newWF !== oldWF) {
    const w = peak[oldWF];
    if (Number.isFinite(w)) peak[newWF] = w;
    const lock = peak[_widthFixField(oldShape)];
    if (typeof lock === 'boolean') peak[_widthFixField(newShape)] = lock;
  }
  // 2. switch shape; seed a default ONLY for a param the new shape introduces
  //    that the peak does not already carry (carried-over values preserved)
  peak.shape = newShape;
  const schema = SHAPE_PARAM_SCHEMA[newShape];
  for (const [k, v] of Object.entries(schema)) {
    if (!(k in peak)) peak[k] = v;
  }
}

// Switch a peak's lineshape and re-render. Shape-agnostic fields (id, name,
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir=\"/tmp\"
import pytest
raise SystemExit(pytest.main([\"-s\",\"-p\",\"no:cacheprovider\",\"tests/test_voigt_contract.py\",\"tests/autofit/test_u4f_parity_battery.py\",\"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp = require(\"child_process\");
const orig = cp.execFileSync;
cp.execFileSync = function(file,args,opts) {
 if (file.includes(\"python\")) {
 const boot = '\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; p=sys.argv.pop(1); sys.argv[0]=p; runpy.run_path(p,run_name=\"__main__\")'\\'';
 return orig(file,[\"-B\",\"-c\",boot,...args],opts);
 }
 return orig(file,args,opts);
};
require(\"./tests/js/lineshape_roundtrip.test.js\");
require(\"./tests/js/lineshape_parity.test.js\");'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "nl -ba scripts/voigt_eta_measure.py | sed -n '47,110p'; nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | sed -n '101,146p'; rg -n 'shape.*Voigt|Voigt.*shape|gl_ratio.*0.3' --glob '*.py' --glob '*.js' --glob '"'!tests/**'"' scripts autofit | head -80" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    47	    with open(os.path.join(out_dir, f"shard{shard}.jsonl"), "w") as out:
    48	        for k, t in enumerate(targets):
    49	            if k % n_shards != shard:
    50	                continue
    51	            vidx = [i for i, sh in enumerate(t["shapes"]) if sh == "Voigt"]
    52	            if not vidx:
    53	                continue
    54	            b = t["background"]
    55	            kw = dict(background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
    56	                      endpoint_avg=b["endpoint_avg"], n_perturb=3, fit_kws={"method": "least_squares"})
    57	            x = np.asarray(t["be"], float)
    58	            y = np.round(np.asarray(t["inten"], float), 2)   # the upload rounds to 2 dp
    59	            free = copy.deepcopy(t["specs"])                  # as sent before A03: gl_ratio 0.3, free
    60	            fixed = copy.deepcopy(t["specs"])
    61	            for i in vidx:
    62	                fixed[i]["gl_ratio"] = 0.5
    63	                fixed[i]["fix_gl_ratio"] = True
    64	            rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"],
    65	                   "voigt_ids": [str(t["specs"][i]["id"]) for i in vidx]}
    66	            for lab, specs in (("free", free), ("fixed", fixed)):
    67	                try:
    68	                    rec[lab] = _pack(fitting.run_fit(x, y, specs, **kw))
    69	                except Exception as e:  # noqa: BLE001 — a failed fit is a row, not a crash
    70	                    rec[lab] = {"error": str(e)[:160]}
    71	            out.write(json.dumps(rec) + "\n")
    72	            out.flush()
    73	
    74	
    75	def summary(out_dir):
    76	    recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(out_dir, "shard*.jsonl"))) for l in open(f)]
    77	    ok = [r for r in recs if "peaks" in r["free"] and "peaks" in r["fixed"] and r["free"]["success"] and r["fixed"]["success"]]
    78	    print(f"targets {len(recs)}, both fits converged {len(ok)}")
    79	    area = lambda x, y: float(abs(np.trapezoid(y, x)))  # noqa: E731
    80	    dA, dB, dC, comp = [], [], [], []
    81	    etas = []
    82	    chi_ratio = []
    83	    for r in ok:
    84	        x = np.asarray(r["free"]["energy"])
    85	        vids = set(r["voigt_ids"])
    86	        a_free, a_disp = [], []
    87	        for pk in r["free"]["peaks"]:
    88	            a = area(x, np.asarray(pk["y"]))
    89	            a_free.append(a)
    90	            if str(pk["id"]) in vids:
    91	                q = pk["params"]
    92	                etas.append(q["gl_ratio"])
    93	                yd = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=q["amplitude"], center=q["center"], fwhm=q["fwhm"], gl_ratio=0.5)
    94	                ad = area(x, yd)
    95	                a_disp.append(ad)
    96	                if a > 0:
    97	                    comp.append(100 * (ad - a) / a)
    98	            else:
    99	                a_disp.append(a)
   100	        a_fix = [area(x, np.asarray(pk["y"])) for pk in r["fixed"]["peaks"]]
   101	        frac = lambda A: [100 * v / sum(A) for v in A]  # noqa: E731
   102	        Ff, Fd, Fx = frac(a_free), frac(a_disp), frac(a_fix)
   103	        dA.append(max(abs(a - b) for a, b in zip(Fd, Ff)))
   104	        dB.append(max(abs(a - b) for a, b in zip(Fx, Fd)))
   105	        dC.append(max(abs(a - b) for a, b in zip(Fx, Ff)))
   106	        chi_ratio.append(r["fixed"]["chi2r"] / r["free"]["chi2r"])
   107	
   108	    def q(v):
   109	        v = sorted(v)
   110	        return f"median {st.median(v):.2f}, p90 {v[int(0.9 * len(v))]:.2f}, max {v[-1]:.2f}"
   101	| C 1s, 8 of 9 (A03) | 3.8 meV | 0.50 % | 1.40 % | 0.32 pp |
   102	| C 1s Scan_4 (findings §2, unchanged) | 41.9 meV | 9.0 % | 99.9 % | 15.1 pp |
   103	| U 4f, 9 (W1) | 39.7 meV | 17.2 % | 20.8 % | 1.4 pp |
   104	| U 4f, 9 (A03) | 28.8 meV | 15.8 % | 8.9 % | 0.77 pp |
   105	| U 4f, the 5 where both engines reach the same minimum (Scan_0/1/2/3/7; χ²ᵣ equal to 2–3 digits) | 4.3 meV | 2.6 % | 2.0 % | 0.12 pp |
   106	| U 4f, the other 4 (Scan_4/5/6/8) | 28.8 meV | 15.8 % | 8.9 % | 0.77 pp |
   107	
   108	On the 5 agreeing targets the Voigt satellites match within 2 % — the W1
   109	gap on them (7–21 %) was the η identity and is gone. On the other 4 the
   110	server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
   111	7.9 while the local engine holds it at 8; χ²ᵣ differs by 8–20 % (the local
   112	engine is LOWER on Scan_6: 2.657 vs 2.798, so neither side is the
   113	reference), and the satellites, which share the region with the main
   114	lines, differ by up to 8.9 % in area.
   115	
   116	**Decision: the "starting point" designation STAYS.** The residual is the
   117	`caM` clamp (the local engine cannot move m; the page draws it rounded),
   118	the next unit the W1 plan named; the label is reconsidered only on a
   119	re-measurement after it. Wording in the page updated to say so (LA
   120	components and several minima; no longer Voigt).
   121	
   122	## 7. Release-note line
   123	
   124	Voigt components are now fitted at the fixed 50/50 mix the page has always
   125	drawn; until now Run Fit let their mix vary on the server and the page
   126	reported the 50/50 curve's area under the other mix's parameters (up to
   127	20 % off per component). Re-fitting a saved U 4f project moves an area
   128	fraction by 0.3 pp at the median and 1.0 pp at most. Use GL to fit the mix.
   129	
   130	## 8. Verification
   131	
   132	- `tests/test_voigt_contract.py` 4 passed; full `pytest tests/` — see §9.
   133	- JS suite: `node --test tests/js/*.test.js` (the directory form does not
   134	  run in this node): see §9.
   135	- Browser check (`browser_check_a03.py`, dev gunicorn :5151 from the
   136	  worktree): the request carries `gl_ratio 0.5, fix_gl_ratio true` for
   137	  both Voigt components; the server returns `vary: false, 0.5`; drawn vs
   138	  fitted curve 1.3e-13 of amplitude for the Voigts (LACX 5.6e-3 — the caM
   139	  rounding); the Results area of a Voigt equals the server curve's to
   140	  0.0000 % (LACX −0.66 %, the same rounding); the chart dataset is the drawn curve; `glMix` unchanged in the
   141	  live model and the saved record; Batch Fit onto U4f Scan_1 converges
   142	  locally; no page errors.
   143	
   144	## 9. Codex rounds
   145	
   146	(filled in below as they run)
scripts/bg_window_worked_example.py:25:    if sh == 'Voigt': s.update(shape='pseudo_voigt_gl', gl_ratio=0.5, fix_gl_ratio=True)  # A03: fixed 50/50 mix
autofit/reference.py:103:    elif shape == "Voigt":
scripts/voigt_eta_measure.py:51:            vidx = [i for i, sh in enumerate(t["shapes"]) if sh == "Voigt"]
scripts/voigt_eta_measure.py:59:            free = copy.deepcopy(t["specs"])                  # as sent before A03: gl_ratio 0.3, free
autofit/engine.py:352:    LineShape.PSEUDO_VOIGT: [("gl_ratio", 0.30, 0.0, 1.0)],
autofit/engine.py:353:    LineShape.ASYM_GL: [("gl_ratio", 0.30, 0.0, 1.0), ("asymmetry", 0.10, 0.0, 1.0)],
scripts/endpoint_avg_sensitivity.py:48:    if sh == 'Voigt': s.update(shape='pseudo_voigt_gl', gl_ratio=0.5, fix_gl_ratio=True)  # A03: fixed 50/50 mix
scripts/gen_autofit_anchor_fixtures.py:27:    return fitting._SHAPE_FUNCS["asymmetric_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=0.3, asymmetry=0.25)
scripts/gen_autofit_anchor_fixtures.py:31:    return fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=0.3)
scripts/gen_autofit_anchor_fixtures.py:49:             "amplitude": max(amp * (1 if i == 0 else 0.2), 1e-3), "fwhm": w, "gl_ratio": 0.3,
scripts/optimizer_disagreement_analyze.py:52:        "has_voigt": float(any(s == "Voigt" for s in t["shapes"])),

 succeeded in 5571ms:
...............................................................
63 passed in 5.21s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require(\"fs\"), cp=require(\"child_process\"), Module=require(\"module\"),path=require(\"path\");
const orig=cp.execFileSync;
cp.execFileSync=(file,args,opts)=>orig(file,file.includes(\"python\")?[\"-B\",\"-c\",'\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; p=sys.argv.pop(1); sys.argv[0]=p; runpy.run_path(p,run_name=\"__main__\")'\\'',...args]:args,opts);
let s=fs.readFileSync(\"tests/js/lineshape_roundtrip.test.js\",\"utf8\");
s=s.slice(0,s.indexOf(\"for (const [shape, c] of Object.entries(CASES))\"));
s+="'`
for (const c of [
{shape:"asym-GL",truth:{shape:"asym-GL",glMix:0,asymmetry:0.35},start:{glMix:0,fixGlMix:true}},
{shape:"DS",truth:{shape:"DS",dsAlpha:0,dsGamma:0.3},start:{dsAlpha:0,fixDsAlpha:true}}
]) {
const {res,peaks,specs}=roundTrip(c.shape,c);
console.log(JSON.stringify({shape:c.shape,spec:specs[0],drawn_vs_fitted_relative:maxRelDiff(env.evalPeakArray(res.energy,peaks[0]),res.individual_peaks[0].y,peaks[0].amplitude)}));
}
`;
const m=new Module(path.resolve("tests/js/review_probe.js"));m.filename=path.resolve("tests/js/review_probe.js");m.paths=module.paths;m._compile(s,m.filename);'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "python3 -c 'import json; d=json.load(open(\"docs/findings/a03/local_server_gap.json\")); print([(r[\"target\"], round(100*(r[\"local_chi2r\"]/r[\"server_chi2r\"]-1),2)) for r in d[\"regions\"][\"U4f\"]]); print([(r[\"target\"], [(p[\"shape\"],p[\"server\"].get(\"caM\")) for p in r[\"comps\"]]) for r in d[\"regions\"][\"U4f\"]])'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-PbsE6DqL' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-H6ZZHQmo' (errno=Operation not permitted)
[('U4f Scan_0', 0.49), ('U4f Scan_1', 1.29), ('U4f Scan_2', -0.19), ('U4f Scan_3', -0.02), ('U4f Scan_4', 9.57), ('U4f Scan_5', 10.07), ('U4f Scan_6', -5.01), ('U4f Scan_7', 0.4), ('U4f Scan_8', 12.74)]
[('U4f Scan_0', [('LACX', 8.072154418763597), ('LACX', 8.072154418763597), ('Voigt', None), ('Voigt', None)]), ('U4f Scan_1', [('LACX', 8.12187839344888), ('LACX', 8.12187839344888), ('Voigt', None), ('Voigt', None)]), ('U4f Scan_2', [('LACX', 8.335630649879592), ('LACX', 8.335630649879592), ('Voigt', None), ('Voigt', None)]), ('U4f Scan_3', [('LACX', 7.073802391508428), ('LACX', 7.073802391508428), ('Voigt', None), ('Voigt', None)]), ('U4f Scan_4', [('LACX', 2.693333881266681), ('LACX', 2.693333881266681), ('Voigt', None), ('Voigt', None)]), ('U4f Scan_5', [('LACX', 6.450794568196254), ('LACX', 6.450794568196254), ('Voigt', None), ('Voigt', None)]), ('U4f Scan_6', [('LACX', 9.995649813267388), ('LACX', 9.995649813267388), ('Voigt', None), ('Voigt', None)]), ('U4f Scan_7', [('LACX', 8.041257690555877), ('LACX', 8.041257690555877), ('Voigt', None), ('Voigt', None)]), ('U4f Scan_8', [('LACX', 7.930937469566035), ('LACX', 7.930937469566035), ('Voigt', None), ('Voigt', None)])]

 succeeded in 3591ms:
/Users/skyefortier/.matplotlib is not a writable directory
{"shape":"asym-GL","spec":{"id":"1","name":"P","center":391.92,"amplitude":9600,"fwhm":1.92,"amplitude_min":0,"fix_center":false,"fix_fwhm":false,"fix_amplitude":false,"fix_gl_ratio":true,"shape":"asymmetric_gl","gl_ratio":0.5,"asymmetry":0.35,"fix_asymmetry":false},"drawn_vs_fitted_relative":0.06883634189452677}
/Users/skyefortier/.matplotlib is not a writable directory
{"shape":"DS","spec":{"id":"1","name":"P","center":391.92,"amplitude":9600,"fwhm":1.92,"amplitude_min":0,"fix_center":false,"fix_fwhm":false,"fix_amplitude":false,"fix_gl_ratio":false,"shape":"doniach_sunjic","alpha":0.1,"gamma_asym":0.3,"fix_alpha":true,"fix_gamma_asym":false},"drawn_vs_fitted_relative":0.08799817206414795}

exec
/bin/zsh -lc "nl -ba tests/js/lineshape_roundtrip.test.js | sed -n '79,95p;152,207p'; nl -ba tests/js/lineshape_parity.test.js | sed -n '337,380p'; rg -n 'function _peakArea|function renderUncertainty|function _buildStderrMap' templates/index.html; sed -n '6308,6350p' templates/index.html; rg -n 'Voigt|GL' static/js/batch_propagation.js; git diff --numstat main..HEAD -- fitting.py app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    79	    ...over,
    80	  };
    81	}
    82	// truth → data; start → what the student placed (the fit has to move every free parameter)
    83	const CASES = {
    84	  'Gaussian':   { truth: { shape: 'Gaussian' }, start: {} },
    85	  'Lorentzian': { truth: { shape: 'Lorentzian' }, start: {} },
    86	  'Voigt':      { truth: { shape: 'Voigt' }, start: { glMix: 90 } },                       // glMix must play no part
    87	  'GL':         { truth: { shape: 'GL', glMix: 72 }, start: { glMix: 30 } },
    88	  'asym-GL':    { truth: { shape: 'asym-GL', glMix: 40, asymmetry: 0.35 }, start: { glMix: 30, asymmetry: 0.05 } },
    89	  'DS':         { truth: { shape: 'DS', dsAlpha: 0.18, dsGamma: 0.3 }, start: { dsAlpha: 0.05, dsGamma: 0.1 } },
    90	  'DSG_LA':     { truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.8 }, start: { laAlpha: 0.10, laBeta: 0.3, laM: 0.4 } },
    91	  'LACX':       { truth: { shape: 'LACX', caAlpha: 1.6, caBeta: 0.7, caM: 20 }, start: { caAlpha: 1.0, caBeta: 1.0, caM: 30 } },
    92	};
    93	const TIGHT_TOL = 1e-6;      // of amplitude; both curves are the same closed form on the same grid
    94	const KNOWN_GAP = {
    95	  'DSG_LA': 'DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit',
   152	    const p = peaks.find(q => String(q.id) === String(ip.id));
   153	    const rel = maxRelDiff(env.evalPeakArray(res.energy, p), ip.y, p.amplitude);
   154	    assert.ok(rel < TIGHT_TOL, `peak ${ip.id}: drawn vs fitted ${(rel * 100).toExponential(3)} %`);
   155	  }
   156	  const ipChild = res.individual_peaks.find(ip => String(ip.id) === '2');
   157	  assert.equal(ipChild.params.gl_ratio.value, 0.5);
   158	  assert.ok(ipChild.params.gl_ratio.expr, 'the child’s η is an expression on the parent');
   159	});
   160	
   161	test('a locked GL mix is sent locked, held by the server and drawn at the locked value', () => {
   162	  const { res, peaks, specs } = roundTrip('GL', { truth: { shape: 'GL', glMix: 72 }, start: { glMix: 30, fixGlMix: true } });
   163	  assert.equal(specs[0].fix_gl_ratio, true);
   164	  assert.equal(res.individual_peaks[0].params.gl_ratio.vary, false);
   165	  assert.equal(peaks[0].glMix, 30, 'the lock is honoured on write-back');
   166	  assert.ok(maxRelDiff(env.evalPeakArray(res.energy, peaks[0]), res.individual_peaks[0].y, peaks[0].amplitude) < TIGHT_TOL);
   167	});
   168	
   169	// The Python twin (autofit.reference.peak_to_backend_spec) is what the local
   170	// engine's parity test and the measurement scripts use to build requests. It
   171	// must build the request the page builds, for every shape and for a link.
   172	test('autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape', () => {
   173	  const peaks = [
   174	    ...Object.entries(CASES).map(([shape, c], i) => fullPeak({ ...c.truth, id: i + 1, name: shape })),
   175	    fullPeak({ id: 99, name: 'child', shape: 'Voigt', linked: 3, linkOffset: -10.9, linkRatio: 0.75, center: CENTER - 10.9 }),
   176	    fullPeak({ id: 100, name: 'auto', shape: 'asym-GL', _afAsymMin: 0.02, _afAsymMax: 0.6 }),
   177	  ];
   178	  state.peaks = peaks;
   179	  const js = peaks.map(p => env.peakToBackendSpec(p));
   180	  const py = bridge({ twin_peaks: peaks }).twin_specs;
   181	  assert.equal(py.length, js.length);
   182	  for (let i = 0; i < js.length; i++) {
   183	    assert.deepStrictEqual(py[i], js[i], `peak ${peaks[i].name}: Python twin and page builder differ`);
   184	  }
   185	});
   186	
   187	// The write-back twin (autofit.reference.apply_backend_params, used by the
   188	// U 4f battery to refit from a refit) must write exactly what the page's
   189	// _applyBackendParams writes: every shape, every lock, a Voigt's glMix kept.
   190	test('autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock', () => {
   191	  const PAR = { center: 391.55, amplitude: 9876.5, fwhm: 1.91, gl_ratio: 0.81, asymmetry: 0.44, alpha: 0.27, gamma_asym: 0.9, beta: 0.66, m_gauss: 1.7, m: 23.4 };
   192	  const params = Object.fromEntries(Object.entries(PAR).map(([k, v]) => [k, { value: v, stderr: null, vary: true, expr: null, min: null, max: null }]));
   193	  const items = [];
   194	  for (const [shape, c] of Object.entries(CASES)) {
   195	    items.push({ peak: fullPeak({ ...c.truth, id: items.length + 1 }), params });
   196	    items.push({ peak: fullPeak({ ...c.truth, id: items.length + 1, fixCenter: true, fixFwhm: true, fixAmplitude: true, fixGlMix: true, fixAsymmetry: true,
   197	      fixDsAlpha: true, fixDsGamma: true, fixLaAlpha: true, fixLaBeta: true, fixLaM: true, fixCaAlpha: true, fixCaBeta: true, fixCaM: true }), params });
   198	  }
   199	  const py = bridge({ twin_apply: items }).twin_applied;
   200	  items.forEach((it, i) => {
   201	    const js = { ...it.peak };
   202	    env._applyBackendParams(js, it.params);
   203	    assert.deepStrictEqual(py[i], js, `peak ${it.peak.shape}${it.peak.fixCenter ? ' (locked)' : ''}: Python twin and page write-back differ`);
   204	  });
   205	});
   337	const SWEEP = {
   338	  'Gaussian':   { fwhm: FWHM_RANGE },
   339	  'Lorentzian': { fwhm: FWHM_RANGE },
   340	  'Voigt':      { fwhm: FWHM_RANGE, glMix: [0, 100] },          // glMix must be IGNORED: Voigt is η = 0.5 (A03)
   341	  'GL':         { glMix: [0, 25, 50, 75, 100], fwhm: FWHM_RANGE },
   342	  'asym-GL':    { glMix: [0, 50, 100], asymmetry: [0, 0.5, 1], fwhm: FWHM_RANGE },
   343	  'DS':         { dsAlpha: [0, 0.25, 0.5], dsGamma: [0, 1, 5], fwhm: FWHM_RANGE },
   344	  'DSG_LA (delta kernel)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0, 0.0009] },
   345	  'LACX (m = 0)': { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0], fwhm: FWHM_RANGE },
   346	};
   347	const SWEEP_KNOWN_GAP = {
   348	  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.05, 0.4, 2, 4] },
   349	  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
   350	};
   351	function sweepShape(label) { return label.split(' ')[0]; }
   352	function runSweep(label, ranges) {
   353	  const shape = sweepShape(label);
   354	  const cases = combos(ranges).map(c => ({ c, p: { ...basePeak(shape), ...c } }));
   355	  const specs = cases.map(k => { const b = BACKEND[shape](k.p); return { ...b, x: grid(k.p.center) }; });
   356	  const beYs = backendEvalMany(specs);
   357	  return cases.map((k, i) => {
   358	    const x = grid(k.p.center);
   359	    const rel = maxRelDiff(evalPeakArray(x, k.p), beYs[i], k.p.amplitude);
   360	    return { c: k.c, rel };
   361	  }).sort((a, b) => b.rel - a.rel);
   362	}
   363	for (const [label, ranges] of Object.entries(SWEEP)) {
   364	  test(`(D) sweep across the fitted range: ${label}`, () => {
   365	    const worst = runSweep(label, ranges);
   366	    assert.ok(worst[0].rel < TIGHT_TOL,
   367	      `${label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} parameter combinations diverge; worst ` +
   368	      `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
   369	  });
   370	}
   371	for (const [label, ranges] of Object.entries(SWEEP_KNOWN_GAP)) {
   372	  test(`(D) sweep across the fitted range: ${label} — KNOWN GAP`, { todo: 'convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)' }, () => {
   373	    const worst = runSweep(label, ranges);
   374	    assert.ok(worst[0].rel < TIGHT_TOL,
   375	      `${label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} parameter combinations diverge; worst ` +
   376	      `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
   377	  });
   378	}
8305:function _buildStderrMap(fitResult) {
8313:function _peakArea(p, be) {
function applyBackendResult(result) {
  for (const ipeak of result.individual_peaks) {
    // Backend returns string IDs; state.peaks uses numeric IDs
    const p = getPeak(Number(ipeak.id)) || getPeak(ipeak.id);
    if (!p) continue;
    // Only apply parameters that were NOT locked — locked params must stay unchanged
    _applyBackendParams(p, ipeak.params);
    p._backendParams = ipeak.params;
  }
  // the verdict describes the model as it now stands (values applied) in its fit context
  _applySupport(state.peaks, result, _startsLiveKey());
}

// LEVENBERG-MARQUARDT FITTING (local JS engine)
// ═══════════════════════════════════════════════════
// ═══════════════════════════════════════════════════
// BKGRD SUB VIEW TOGGLE
// ═══════════════════════════════════════════════════
// The pill at id="bg-sub-pill" / id="bg-sub-toggle" can be in three
// visual states (active, inactive, disabled). The disabled state
// applies whenever subtraction is meaningless: no spectrum loaded,
// bg-type is "none", or a fit is running. The pill's checked state
// is preserved across disable cycles so users get their preference
// back when bg becomes available again.

let _bgSubFitInFlight = false;

// IDs of overlay controls that don't compose with subtracted view
// (they're full-spectrum / non-bg-aware). When subtracted view is
// effectively active we disable them with the existing app
// convention (opacity 0.4 + disabled attr + title tooltip), so users
// see why their checkbox appears inert. Identical pattern to how
// `shirley-iter` is gated when bg-type doesn't need iteration.
const _BG_SUB_DEPENDENT_CONTROL_IDS = ['smooth-enable', 'deriv1-enable', 'deriv2-enable'];

function _isBgSubViewActive() {
  const toggle = document.getElementById('bg-sub-toggle');
  if (!toggle || !toggle.checked) return false;
  // Even if the pill is checked, fall back to raw view when bg is
  // unavailable (defensive: covers the moment between bg-type=none
  // and the pill recompute, and any transient bg gap).
  const bgType = document.getElementById('bg-type')?.value || 'shirley';
  if (bgType === 'none') return false;
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mgVQIuRX' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-i7GvJOb6' (errno=Operation not permitted)

exec
/bin/zsh -lc "git diff main..HEAD -- tests/autofit/fixtures/u4f_battery_expected.json | head -105; sed -n '5950,5978p' templates/index.html; rg -n '_validateUncertainties|validation.info' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2UblmDxc' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-MKlZRRyU' (errno=Operation not permitted)
diff --git a/tests/autofit/fixtures/u4f_battery_expected.json b/tests/autofit/fixtures/u4f_battery_expected.json
index 3f592f2..18e0ccd 100644
--- a/tests/autofit/fixtures/u4f_battery_expected.json
+++ b/tests/autofit/fixtures/u4f_battery_expected.json
@@ -4,1094 +4,1094 @@
    "name": "U4f Scan",
    "peaks": [
     {
-     "amplitude": 20549.239066563052,
-     "area": 55706.064928636086,
-     "center": 379.5411983880395,
-     "fwhm": 2.439706490741759,
+     "amplitude": 20523.59428562886,
+     "area": 54795.52375621333,
+     "center": 379.54553006530386,
+     "fwhm": 2.6055322777792354,
      "id": "2"
     },
     {
-     "amplitude": 13357.005393265985,
-     "area": 35790.67130565624,
-     "center": 390.4411983880395,
-     "fwhm": 2.439706490741759,
+     "amplitude": 13340.33628565876,
+     "area": 35296.29509834129,
+     "center": 390.44553006530384,
+     "fwhm": 2.6055322777792354,
      "id": "3"
     },
     {
-     "amplitude": 1989.4857545655448,
-     "area": 5058.74612807137,
-     "center": 396.9712251693392,
-     "fwhm": 2.388745267364792,
+     "amplitude": 2114.869484942877,
+     "area": 6068.442934281255,
+     "center": 396.9516682264294,
+     "fwhm": 2.2548070904616297,
      "id": "4"
     },
     {
-     "amplitude": 2628.5012391928685,
-     "area": 6802.696993588804,
-     "center": 385.9247159321286,
-     "fwhm": 2.0891771271477393,
+     "amplitude": 2692.0095677127997,
+     "area": 7363.5593837829565,
+     "center": 385.9128586234601,
+     "fwhm": 2.1254771557019185,
      "id": "5"
     }
    ],
    "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
-   "r_factor": 0.04485615744017836,
-   "reduced_chi_square": 2.130853079960093,
+   "r_factor": 0.04623101189059859,
+   "reduced_chi_square": 2.2463714369001466,
    "success": true
   },
   {
    "name": "U4f Scan_0",
    "peaks": [
     {
-     "amplitude": 13750.73674660914,
-     "area": 44164.438359031716,
-     "center": 379.5736061050387,
-     "fwhm": 2.749490801416237,
+     "amplitude": 13780.168603934413,
+     "area": 44429.99886398937,
+     "center": 379.5790029808743,
+     "fwhm": 2.7841309774912397,
      "id": "2"
     },
     {
-     "amplitude": 8937.978885295941,
-     "area": 28126.031629074198,
-     "center": 390.4736061050387,
-     "fwhm": 2.749490801416237,
+     "amplitude": 8957.109592557368,
+     "area": 28291.514382331527,
+     "center": 390.47900298087427,
+     "fwhm": 2.7841309774912397,
      "id": "3"
     },
     {
-     "amplitude": 1169.8956229407977,
-     "area": 3112.9813222097064,
-     "center": 397.0393523721098,
-     "fwhm": 2.499753520428009,
+     "amplitude": 1233.6601113057095,
+     "area": 3463.803066603189,
+     "center": 397.0008467741776,
+     "fwhm": 2.20495572903937,
      "id": "4"
     },
     {
-     "amplitude": 1729.3948026931675,
-     "area": 5448.711481995413,
-     "center": 385.9753028365857,
-     "fwhm": 2.1162471748851557,
+     "amplitude": 1678.7918017188933,
+     "area": 4754.905575096549,
+     "center": 385.9884083029769,
+     "fwhm": 2.202708620743477,
      "id": "5"
      <input type="checkbox" id="pk-cref-${p.id}"
             ${p.isChargeReference ? 'checked' : ''}
             onchange="toggleChargeReference(${p.id})"
             style="margin:0">
      <label for="pk-cref-${p.id}"
             style="margin:0;font-size:11px;cursor:pointer;user-select:none"
             title="Mark this peak as the charge-correction reference (typically C 1s graphite at 284.5 eV). Only one peak per fit can hold this marker.">
        Charge-correction reference (C&nbsp;1s graphite)
      </label>
    </div>` : ''}
    <div class="field">
      <label>Line shape</label>
      <select id="pk-shape-${p.id}" class="xps-tip-select" onchange="_switchPeakShape(${p.id}, this.value)">
        <option data-tip="Pure Gaussian. Dominated by instrument broadening. Rarely used alone — most XPS peaks need some Lorentzian character." ${p.shape==='Gaussian'?'selected':''}>Gaussian</option>
        <option data-tip="Pure Lorentzian. Dominated by core-hole lifetime. Rarely used alone — too sharp for most real XPS peaks." ${p.shape==='Lorentzian'?'selected':''}>Lorentzian</option>
        <option data-tip="Fixed 50/50 Gaussian-Lorentzian mix (η = 0.5, not fitted). A reasonable default for most insulating and polymeric samples; choose GL to fit the mix." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
        <option value="GL" data-tip="Adjustable Gaussian/Lorentzian ratio. Use when you need control over the peak shape — common for oxides, polymers, and organic materials." ${p.shape==='GL'?'selected':''}>GL pseudo-Voigt (&eta; mixing)</option>
        <option value="asym-GL" data-tip="GL with asymmetric broadening. Use for peaks with vibrational fine structure (e.g., C 1s in polymers) or when one side is broader than the other." ${p.shape==='asym-GL'?'selected':''}>Asymmetric GL</option>
        <option value="DS" data-tip="Asymmetric metallic lineshape with tail toward higher BE. Use for metals and conductive samples (e.g., Au, Cu, Fe metal). Not appropriate for insulators or oxides." ${p.shape==='DS'?'selected':''}>Doniach-&Scaron;unji&#263; (&alpha; + &gamma;)</option>
        <option value="DSG_LA" data-tip="Doniach-Šunjić core convolved with a Gaussian. A defensible asymmetric shape — good for metals and transition metals with complex screening. Previously this entry was mis-labeled as 'LA [CasaXPS]'. The genuine CasaXPS LA(α,β,m) lives in the new entry below." ${p.shape==='DSG_LA'?'selected':''}>DS+G</option>
        <option value="LACX" data-tip="True CasaXPS LA(α,β,m). Asymmetric Lorentzian raised to exponents α (high-BE tail side) and β (low-BE side), convolved with a Gaussian of integer point width m. Reduces to a pure Lorentzian at α=β=1, m=0. Match to CasaXPS by using the same α, β, m values." ${p.shape==='LACX'?'selected':''}>LA(&alpha;,&beta;,m) [CasaXPS]</option>
      </select>
    </div>
    <div id="shape-controls-${p.id}">
      ${renderShapeControls(p)}
    </div>
    <div class="field-row">
      <div class="field">
        <label data-xps-tip="Peak position in binding energy. After charge correction, this should match the expected literature value for the chemical state being modeled.">Center (eV)${isLinked ? ' <em style="color:var(--purple);font-size:9px">auto</em>' : ''}
8431:  const { warnings: uncWarnings, info: uncInfo } = _validateUncertainties();
11311:function _validateUncertainties() {

codex
The Voigt contract tests and all 59 U 4f battery checks passed. Adversarial round trips exposed cases the new harness misses: locked asym-GL at mix 0 sends 0.5, and locked DS at α=0 sends 0.1. Their displayed curves differ from the fitted curves by 6.88% and 8.80% of amplitude. Those builder defects predate A03, but the new boundary sweep bypasses the builder and reports both boundaries as passing.

The committed JSON also contradicts the documented “8–20%” residual χ² gap: the four cited targets differ by about 5–13%.
 succeeded in 63852ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
ok 1 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1761.817543
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
ok 2 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1684.530994
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
ok 3 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1777.992046
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
ok 4 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1761.739506
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
ok 5 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1669.201073
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
ok 6 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1728.024425
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 7 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1743.632459
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA: drawn vs fitted curve differ by 5.462e-3 % of amplitude'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:128:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
not ok 8 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX # TODO LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit
  ---
  duration_ms: 1673.471777
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: 'LACX: drawn vs fitted curve differ by 1.467e-1 % of amplitude'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:128:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
ok 9 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1708.829033
  type: 'test'
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
ok 10 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1660.968264
  type: 'test'
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
ok 11 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1648.057913
  type: 'test'
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
ok 12 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1694.85915
  type: 'test'
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
ok 13 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1644.795891
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Gaussian
ok 14 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1660.268896
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
ok 15 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1803.066643
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: GL
ok 16 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1775.957003
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Voigt
ok 17 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1658.30062
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DS
ok 18 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1717.186069
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
ok 19 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1640.29211
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)
not ok 20 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1653.152573
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:174:1'
  failureType: 'testCodeFailure'
  error: 'LACX: frontend vs backend max diff = 0.1496% of amplitude (tol 0.00009999999999999999%)'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:181:10)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (A) frontend vs backend parity: LACX at m=0 (no convolution)
ok 21 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1791.970585
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed
not ok 22 - (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed # TODO DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above
  ---
  duration_ms: 1701.664956
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:197:1'
  failureType: 'testCodeFailure'
  error: 'DSG_LA: frontend vs backend max diff = 1.7518% of amplitude (tol 0.00009999999999999999%)'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:204:10)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
ok 23 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1640.904308
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
ok 24 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1752.796107
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
ok 25 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1745.243557
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
ok 26 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1719.113031
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
ok 27 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1815.383919
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 28 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.528447
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 29 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.121063
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 30 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.143032
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 31 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.135019
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 32 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.18723
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 33 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.228325
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
ok 34 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
  ---
  duration_ms: 10.288993
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 35 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.414154
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:267:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7170.363795150584, rel diff=24.2055%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:274:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (C) evalPeak() has no direct callers outside evalPeakArray()
ok 36 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 3.076909
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
ok 37 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1675.002655
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
ok 38 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1697.85047
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Voigt
ok 39 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1737.481918
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: GL
ok 40 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1788.73817
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
ok 41 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1702.077832
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DS
ok 42 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1746.274377
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
ok 43 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1671.136499
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
ok 44 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1691.139448
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP
not ok 45 - (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 2175.667638
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA (m > 0): 36 of 36 parameter combinations diverge; worst 1.129e+55 % of amplitude at {"laAlpha":0.49,"laBeta":2,"laM":0.05}'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:374:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP
not ok 46 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1718.215194
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:3'
  failureType: 'testCodeFailure'
  error: 'LACX (m > 0): 81 of 108 parameter combinations diverge; worst 8.941e-1 % of amplitude at {"caAlpha":5,"caBeta":5,"caM":50,"fwhm":0.1}'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:374:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
1..46
# tests 46
# suites 0
# pass 39
# fail 0
# cancelled 0
# skipped 0
# todo 7
# duration_ms 63887.376409

exec
/bin/zsh -lc "sed -n '8300,8343p' templates/index.html; sed -n '11420,11445p' templates/index.html; rg -n '"'^def load_project_tabs|''^def load_reference_fits'"' autofit/reference.py; sed -n '1,80p' scripts/gen_u4f_battery_fixture.py; rg -n 'LineShape.PSEUDO_VOIGT|\"Voigt\"|gl_ratio' autofit/regions/u4f.py | tail -15" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
// ═══════════════════════════════════════════════════
// RESULTS
// ═══════════════════════════════════════════════════

// Build {peakId: paramMap} from backend fit result (null-safe)
function _buildStderrMap(fitResult) {
  const m = {};
  const peaks = fitResult?.backendResult?.individual_peaks;
  if (peaks) for (const ip of peaks) m[ip.id] = ip.params || {};
  return m;
}

// Rectangular-rule area for one peak over a BE grid
function _peakArea(p, be) {
  const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1;
  // evalPeakArray(), not a per-point evalPeak map: for LACX with caM > 0,
  // only the array evaluator applies the shape's Gaussian convolution —
  // evalPeak silently returns the unconvolved base regardless of caM.
  // Feeds the Results panel/sidebar Area+% and the CSV/XLSX export.
  return evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step;
}

function renderResults() {
  const el = document.getElementById('results-area');
  _applyStatDisplay(state.fitResult);   // header + status bar track every result change (clear, restore, auto-fit) as one unit
  _updateLocalModelBanner();
  if (!state.fitResult) {
    el.innerHTML = _isLocalModel()
      ? '<p style="color:var(--amber,#f59e0b);font-size:11px;text-align:center;padding:20px 0">&#9888; This model was imported from a local fit: a starting point, not a reportable result. Run Fit to obtain results.</p>'
      : '<p style="color:var(--text3);font-size:11px;text-align:center;padding:20px 0">Run the fit to see results.</p>';
    // Quantify (#quantify-area) is populated by renderQuantify(), called
    // only from the non-null path below — without this it kept showing
    // a PRIOR fit's area/RSF/At% table after state.fitResult was cleared
    // elsewhere (Codex review finding, 2026-07-14: same class of stale-
    // DOM bug as the Results panel itself). Reset it to the same
    // no-fit placeholder as its initial static markup.
    const qEl = document.getElementById('quantify-area');
    if (qEl) qEl.innerHTML = '<p style="color:var(--text3);font-size:11px;text-align:center;padding:20px 0;">Run fit to quantify.</p>';
    return;
  }

  const { chiReduced, rmse, backendResult } = state.fitResult;
  const _statIsChi = _fitStatLabel(state.fitResult) !== 'Residual variance';
  const stderrMap = _buildStderrMap(state.fitResult);
    inner.textContent = msg;
    inner.style.color = type === 'red' ? 'var(--red)' : type === 'amber' ? 'var(--amber)' : 'var(--text)';
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(dismissToast, 3000);
    return;
  }
  const el = document.getElementById('notify');
  el.textContent = msg;
  el.style.color = type === 'red' ? 'var(--red)' : type === 'amber' ? 'var(--amber)' : 'var(--green)';
  el.style.display = 'block';
  clearTimeout(el._timer);
  el._timer = setTimeout(() => { el.style.display = 'none'; }, 4000);
}

function dismissToast() {
  const toast = document.getElementById('prominent-toast');
  toast.classList.remove('show');
  clearTimeout(toast._timer);
}

// ═══════════════════════════════════════════════════
// RESID PANEL RESIZE
// ═══════════════════════════════════════════════════
(function() {
  const handle = document.getElementById('resid-handle');
41:def load_project_tabs(path: str | Path) -> list[dict]:
304:def load_reference_fits(path: str | Path) -> list[ReferenceFit]:
#!/usr/bin/env python
"""
Generate tests/autofit/fixtures/u4f_battery_expected.json — frozen
characterization records for the U 4f parity battery (LACX mains + linked
spin-orbit doublet + Voigt satellites through the MANUAL fit path).

Regenerate ONLY for reviewed, intentional numerics changes:

    venv/bin/python scripts/gen_u4f_battery_fixture.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autofit.parity import battery_eligible, refit_record  # noqa: E402
from autofit.reference import load_reference_fits  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "docs", "autofit", "test_data")
OUT = os.path.join(
    os.path.dirname(__file__), "..", "tests", "autofit", "fixtures",
    "u4f_battery_expected.json",
)


def main() -> None:
    records = []
    skipped = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            ok, reason = battery_eligible(rf, region="U 4f")
            if not ok:
                if reason != "not U 4f":
                    skipped.append({"project": rf.project, "name": rf.name,
                                    "reason": reason})
                continue
            rec = refit_record(rf)
            for pk in rec["peaks"]:
                pk.pop("params", None)   # the fixture pins numbers, not the full model
            records.append(rec)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"records": records, "skipped": skipped}, f, indent=1, sort_keys=True)
    print(f"{len(records)} records frozen, {len(skipped)} skipped -> {OUT}")
    for s in skipped:
        print(f"  skipped: {s['project']} / {s['name']} — {s['reason']}")


if __name__ == "__main__":
    main()
235:            "satellite_u4f72", U4F_SAT72_WINDOW, LineShape.PSEUDO_VOIGT,
242:            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
248:            share_parent_params=("gl_ratio", "fwhm"),
253:            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
259:            share_parent_params=("gl_ratio", "fwhm"),
266:            "satellite_u4f72", U4F_SAT72_WINDOW, LineShape.PSEUDO_VOIGT,
273:            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile
tempfile.tempdir=\"/tmp\"
from autofit.reference import load_project_tabs
import glob,os,collections
counts=collections.Counter()
rows=[]
for f in glob.glob(\"docs/autofit/test_data/*.proj.zip\"):
 ts=[t for t in load_project_tabs(f) if t.get(\"rawBE\") and any(p.get(\"shape\")==\"Voigt\" for p in t.get(\"peaks\",[]))]
 if ts: rows.append((os.path.basename(f),len(ts),[t[\"name\"] for t in ts if not t[\"name\"].startswith(\"U4f\")]))
print(rows)
print(\"unique saved Voigt tabs\",sum(r[1] for r in rows))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 153ms:
[('Cl2p_projfit_test.proj.zip', 8, ['Cl2p Scan_1']), ('B4C-UCl4.proj.zip', 10, []), ('UCl4_on_graphite.proj.zip', 10, []), ('4-GTA UCl4-BN.proj.zip', 10, []), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 10, []), ('Project9_CasaXPS_newfit.proj.zip', 7, [])]
unique saved Voigt tabs 55

exec
/bin/zsh -lc "rg --files tests/autofit | rg 'parity_battery.py"'$'"'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
tests/autofit/test_u4f_parity_battery.py
tests/autofit/test_c1s_parity_battery.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4T1O6nkP' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-q17Cyd4u' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_review_prompt.txt
?? docs/autofit/codex/a03_voigt_eta_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_verdict_runB.md

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\",\"-p\",\"no:cacheprovider\",\"tests/autofit/test_c1s_parity_battery.py\",\"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '11332,11346p'; nl -ba scripts/optimizer_disagreement_targets.js | sed -n '51,65p'; nl -ba docs/findings/a03/voigt_eta_summary.txt" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
 11332	    for (const [pName, pData] of Object.entries(params)) {
 11333	      if (!['center','fwhm','fwhm_l','amplitude','gl_ratio'].includes(pName)) continue;
 11334	      const val = pData.value;
 11335	
 11336	      // Locked or linked: skip the alarm-style movement/stderr checks.
 11337	      //   - linked satellite (expr set): tied to master via lmfit expr; intentional
 11338	      //     by construction → silent
 11339	      //   - genuinely locked (vary=false, no expr): user or auto-fit set this lock
 11340	      //     → neutral info note pointing at the padlock toggle, not an alarm
 11341	      if (pData.vary === false) {
 11342	        const isLinked = pData.expr != null && pData.expr !== '';
 11343	        if (!isLinked) {
 11344	          info.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> locked — unlock the padlock to refine.</li>`);
 11345	        }
 11346	        continue;
    51	    for (const tgt of g.slice(1)) {
    52	      const scale = srcMax > 0 ? Math.max(...tgt.rawIntensity) / srcMax : 1;
    53	      const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
    54	      const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
    55	      const r = request('batch', project, tgt.name, cloned, ui, src.ccShift, tgt.rawBE, tgt.rawIntensity, src.name);
    56	      if (r && !seen.has(r.id)) { seen.add(r.id); out.push(r); }
    57	    }
    58	  }
    59	}
    60	process.stdout.write(JSON.stringify(out));
    61	process.stderr.write(`targets: ${out.length} (own ${out.filter(t => t.kind === 'own').length}, batch ${out.filter(t => t.kind === 'batch').length})\n`);
     1	targets 90, both fits converged 90
     2	free eta of 180 Voigt components: 46 at 0 (pure Gaussian), 17 at 1 (pure Lorentzian), 24 within 0.4–0.6
     3	per-Voigt-component DISPLAYED area vs the fitted curve (%): median 11.82, p90 19.18, max 20.11; > 10 % on 103 of 180; displayed high (eta < 0.5) 114, low 66
     4	A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.49, max 1.61; > 1 pp on 35 targets
     5	B. fixed refit vs displayed (what changes on screen), max |delta| pp: median 0.30, p90 0.46, max 1.02; > 1 pp on 1 targets
     6	C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 34 targets
     7	chi2r fixed/free: median 1.09, p90 1.18, max 5.39; fixed lower on 11 targets (the free fit in a worse minimum)

 succeeded in 2794ms:
...........................................................
59 passed in 2.45s

codex
No BLOCKER found. Three MAJOR findings prevent accepting A03 as complete.

1. **MAJOR — The measurement cannot reliably reproduce its old baseline.** [scripts/voigt_eta_measure.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:59) copies incoming specs into `free` without restoring `gl_ratio=0.3, fix_gl_ratio=false`. Regenerate targets using the committed target generator on this branch, and both arms receive held η=0.5: the reported old-vs-new differences collapse to zero. Explicitly construct both contracts; document the actual `.js` target generator and input preparation.

2. **MAJOR — Row B does not measure the claimed saved-project screen change.** [scripts/voigt_eta_measure.py:87](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:87) constructs “displayed” areas from a **new free-η refit**, not the saved model. It also uses server curves for non-Voigt components and trapezoidal integration, whereas Results uses page evaluators and rectangular integration. A U 4f fit with fractional LACX `m` therefore has a different denominator on screen—the plan itself records a −0.66% LACX area discrepancy. The **0.30/1.02 pp release-note claim is not established by this calculation**. Measure saved-page versus refitted-page fractions, or accurately relabel this comparison.

3. **MAJOR — The new harness misses existing request/lock identity failures at swept boundaries.** [tests/js/lineshape_roundtrip.test.js:83](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:83), [tests/js/lineshape_parity.test.js:355](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:355). The sweep builds backend parameters independently of `peakToBackendSpec`; the round trips use interior values. Reusing the new round-trip machinery, I reproduced:
   - Locked asym-GL `glMix=0`: request sends **0.5**, page retains **0**; curve discrepancy **6.88% of amplitude**.
   - Locked DS `dsAlpha=0`: request sends **0.1**, page retains **0**; discrepancy **8.80%**.

   The builder defects predate A03, but the new claimed coverage misses them. Add boundary-and-lock round trips and fix or explicitly track these gaps.

4. **MINOR — Voigt uncertainty guidance offers a nonexistent control.** [templates/index.html:11344](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:11344). After fitting an unlinked Voigt, its newly held `gl_ratio` produces “locked — unlock the padlock to refine.” Voigt has no mix padlock. Explain that the shape fixes η and direct users to GL.

5. **MINOR — Documentation overstates numerical agreement and residual causation.** [plan:111](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:111). The committed JSON gives `(local/server−1)` χ² differences of **+9.57%, +10.07%, −5.01%, +12.74%** for Scan_4/5/6/8, not “8–20%.” Movement in `m` alone does not establish that the entire residual is caused by its local clamp; no controlled comparison establishes that attribution. Also correct the template’s “24%” area comment to the summary’s **20.11%**, and row A’s **1.60 pp** to **1.61 pp**.

The fixed-0.5 contract itself is coherent with the existing page and local-engine semantics. The measurements support correcting the identity mismatch; they do not establish that 0.5 is physically optimal or that boundary η values prove non-identifiability. Keeping **“starting point”** is justified.

Refit-from-refit is a meaningful stability check, not a tautology: it reruns the optimizer after write-back, while the fixture independently pins results. Validation passed: **122 Python tests; 39 JS tests passed, 7 TODO**. The convolved-shape TODO failures reproduced. No files changed.

**VERDICT: NO-GO**
tokens used
101,611
No BLOCKER found. Three MAJOR findings prevent accepting A03 as complete.

1. **MAJOR — The measurement cannot reliably reproduce its old baseline.** [scripts/voigt_eta_measure.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:59) copies incoming specs into `free` without restoring `gl_ratio=0.3, fix_gl_ratio=false`. Regenerate targets using the committed target generator on this branch, and both arms receive held η=0.5: the reported old-vs-new differences collapse to zero. Explicitly construct both contracts; document the actual `.js` target generator and input preparation.

2. **MAJOR — Row B does not measure the claimed saved-project screen change.** [scripts/voigt_eta_measure.py:87](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:87) constructs “displayed” areas from a **new free-η refit**, not the saved model. It also uses server curves for non-Voigt components and trapezoidal integration, whereas Results uses page evaluators and rectangular integration. A U 4f fit with fractional LACX `m` therefore has a different denominator on screen—the plan itself records a −0.66% LACX area discrepancy. The **0.30/1.02 pp release-note claim is not established by this calculation**. Measure saved-page versus refitted-page fractions, or accurately relabel this comparison.

3. **MAJOR — The new harness misses existing request/lock identity failures at swept boundaries.** [tests/js/lineshape_roundtrip.test.js:83](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:83), [tests/js/lineshape_parity.test.js:355](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:355). The sweep builds backend parameters independently of `peakToBackendSpec`; the round trips use interior values. Reusing the new round-trip machinery, I reproduced:
   - Locked asym-GL `glMix=0`: request sends **0.5**, page retains **0**; curve discrepancy **6.88% of amplitude**.
   - Locked DS `dsAlpha=0`: request sends **0.1**, page retains **0**; discrepancy **8.80%**.

   The builder defects predate A03, but the new claimed coverage misses them. Add boundary-and-lock round trips and fix or explicitly track these gaps.

4. **MINOR — Voigt uncertainty guidance offers a nonexistent control.** [templates/index.html:11344](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:11344). After fitting an unlinked Voigt, its newly held `gl_ratio` produces “locked — unlock the padlock to refine.” Voigt has no mix padlock. Explain that the shape fixes η and direct users to GL.

5. **MINOR — Documentation overstates numerical agreement and residual causation.** [plan:111](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:111). The committed JSON gives `(local/server−1)` χ² differences of **+9.57%, +10.07%, −5.01%, +12.74%** for Scan_4/5/6/8, not “8–20%.” Movement in `m` alone does not establish that the entire residual is caused by its local clamp; no controlled comparison establishes that attribution. Also correct the template’s “24%” area comment to the summary’s **20.11%**, and row A’s **1.60 pp** to **1.61 pp**.

The fixed-0.5 contract itself is coherent with the existing page and local-engine semantics. The measurements support correcting the identity mismatch; they do not establish that 0.5 is physically optimal or that boundary η values prove non-identifiability. Keeping **“starting point”** is justified.

Refit-from-refit is a meaningful stability check, not a tautology: it reruns the optimizer after write-back, while the fixture independently pins results. Validation passed: **122 Python tests; 39 JS tests passed, 7 TODO**. The convolved-shape TODO failures reproduced. No files changed.

**VERDICT: NO-GO**
