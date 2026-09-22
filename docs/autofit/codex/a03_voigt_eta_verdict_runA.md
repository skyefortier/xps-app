OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0c7ac-a721-7c03-be80-0f7260bdc5ab
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
I’ll read the plan first, trace the contract and measurement paths, then run the focused tests. I’ll report concrete failures by severity and finish with a verdict.

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
/bin/zsh -lc 'git status --short && git diff --stat main..HEAD && rg --files -g AGENTS.md -g CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-19BTDQDX' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8WkmylnF' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_review_prompt.txt
?? docs/autofit/codex/a03_voigt_eta_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-AWax3WKd' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VbzB5RJ2' (errno=Operation not permitted)
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
CLAUDE.md

exec
/bin/zsh -lc 'cat tests/js/lineshape_roundtrip.test.js tests/js/lineshape_roundtrip_backend.py tests/test_voigt_contract.py && git diff main..HEAD -- tests/js/lineshape_parity.test.js tests/js/lineshape_parity_backend.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html autofit/reference.py autofit/parity.py tests/autofit/battery_common.py tests/autofit/test_u4f_parity_battery.py scripts/gen_u4f_battery_fixture.py CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NMCpIvMl' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-38NTNpKL' (errno=Operation not permitted)
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

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-l4Vb1WZo' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fnZChlFK' (errno=Operation not permitted)
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
/bin/zsh -lc 'cat scripts/local_server_gap.js scripts/voigt_eta_measure.py docs/findings/a03/voigt_eta_summary.txt && git log -1 --format=fuller' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
targets 90, both fits converged 90
free eta of 180 Voigt components: 46 at 0 (pure Gaussian), 17 at 1 (pure Lorentzian), 24 within 0.4–0.6
per-Voigt-component DISPLAYED area vs the fitted curve (%): median 11.82, p90 19.18, max 20.11; > 10 % on 103 of 180; displayed high (eta < 0.5) 114, low 66
A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.49, max 1.61; > 1 pp on 35 targets
B. fixed refit vs displayed (what changes on screen), max |delta| pp: median 0.30, p90 0.46, max 1.02; > 1 pp on 1 targets
C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 34 targets
chi2r fixed/free: median 1.09, p90 1.18, max 5.39; fixed lower on 11 targets (the free fit in a worse minimum)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NL64OI6a' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hUAdrBKl' (errno=Operation not permitted)
commit 712e1363af5f44685a3c4f43722ecc9584d79709
Author:     Skye Fortier <skyefortier@gmail.com>
AuthorDate: Mon Sep 21 23:51:53 2026 -0600
Commit:     Skye Fortier <skyefortier@gmail.com>
CommitDate: Mon Sep 21 23:51:53 2026 -0600

    fix(A03): a Voigt is the fixed 50/50 mix on BOTH sides; page->server->page identity test; parameter-range sweep; U 4f gap re-measured
    
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
/bin/zsh -lc 'git diff main..HEAD -- tests/autofit/battery_common.py tests/autofit/test_u4f_parity_battery.py tests/js/lineshape_parity.test.js && cat tests/js/local_lm_server_parity_backend.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IDuez6VW' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7fhg7kdQ' (errno=Operation not permitted)
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

codex
The production change appears narrow: Voigt requests now hold η at 0.5, while GL requests retain their existing behavior. I’m checking the evidence behind the release claims next, especially whether the measurement scripts can reproduce the old-versus-new comparison and how much the new tests actually cover.

exec
/bin/zsh -lc "rg -n 'Voigt|glMix|pseudo_voigt_gl|_STARTS_MODEL_FIELDS|gl_ratio' templates/index.html autofit/reference.py scripts/optimizer_disagreement_targets.py | head -180" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
rg: scripts/optimizer_disagreement_targets.py: No such file or directory (os error 2)
autofit/reference.py:96:        "fix_gl_ratio": bool(p.get("fixGlMix")),
autofit/reference.py:103:    elif shape == "Voigt":
autofit/reference.py:105:        spec["shape"] = "pseudo_voigt_gl"
autofit/reference.py:106:        spec["gl_ratio"] = 0.5
autofit/reference.py:107:        spec["fix_gl_ratio"] = True
autofit/reference.py:109:        spec["shape"] = "pseudo_voigt_gl"
autofit/reference.py:110:        spec["gl_ratio"] = p["glMix"] / 100.0
autofit/reference.py:113:        spec["gl_ratio"] = (p.get("glMix") or 50) / 100.0
autofit/reference.py:159:    a Voigt keeps the ``glMix`` it carries for a later switch to GL). ``par``
autofit/reference.py:173:    if "gl_ratio" in par and shape in ("GL", "asym-GL") and not p.get("fixGlMix"):
autofit/reference.py:174:        p["glMix"] = val("gl_ratio") * 100
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
templates/index.html:6233:    spec.shape = 'pseudo_voigt_gl';
templates/index.html:6234:    spec.gl_ratio = 0.5;
templates/index.html:6235:    spec.fix_gl_ratio = true;
templates/index.html:6237:    spec.shape = 'pseudo_voigt_gl';
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
templates/index.html:11333:      if (!['center','fwhm','fwhm_l','amplitude','gl_ratio'].includes(pName)) continue;
templates/index.html:14777:                   offset: 'separation', gl_ratio: 'G/L mix',
templates/index.html:14790:  pseudo_voigt_gl: 'Voigt-type (GL)', asymmetric_gl: 'Asymmetric GL',
templates/index.html:15667:      o.glMix = 100 * (p.gl_ratio ?? 0.3); o.asymmetry = p.asymmetry ?? 0.1; break;
templates/index.html:15674:    default:                o.shape = 'GL'; o.glMix = 100 * (p.gl_ratio ?? 0.3);

exec
/bin/zsh -lc "rg -n '"'^def _make_peak_params|''^def run_fit|gamma_asym|m_gauss|fix_m|gl_ratio'"' fitting.py | head -120 && cat tests/autofit/battery_common.py && sed -n '1,170p' scripts/optimizer_disagreement_targets.py && sed -n '180,260p' autofit/parity.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 0ms:
62:    gl_ratio: float,
67:    gl_ratio : Lorentzian fraction  (0 = pure Gaussian, 1 = pure Lorentzian)
69:    eta = float(np.clip(gl_ratio, 0.0, 1.0))
81:    gl_ratio: float,
89:    gl_ratio  : common Lorentzian fraction for both sides.
97:    result[left] = _pseudo_voigt_gl(x[left], amplitude, center, fwhm, gl_ratio)
98:    result[~left] = _pseudo_voigt_gl(x[~left], amplitude, center, fwhm_r, gl_ratio)
108:    gamma_asym: float = 0.0,
116:              × exp(−gamma_asym · max(0, x−c))
120:    gamma_asym > 0 adds an exponential envelope that limits how far the
124:    gamma_asym: exponential tail-decay rate (eV⁻¹).  0 = standard DS.
127:    gamma_asym = max(float(gamma_asym), 0.0)
144:    # Use |dx| on the high-BE side only: exp(-gamma_asym * max(x - center, 0))
145:    if gamma_asym > 0.0:
146:        tail_decay = np.exp(-gamma_asym * np.maximum(x - center, 0.0))
158:    m_gauss: float,  # CasaXPS: Gaussian FWHM (eV) for convolution
179:    m_gauss : Gaussian FWHM (eV) for instrument/phonon broadening (0 = none)
190:    m_gauss = max(float(m_gauss), 0.0)
192:    # ── DS core evaluator (independent of m_gauss) ───────────────────────────
208:        """Evaluate DS kernel on arbitrary grid. Independent of m_gauss."""
221:    if m_gauss < 0.001:
232:    # Pad by ±10·m_gauss (≈ ±4.25σ) to avoid truncation artifacts.
238:    pad_ev = max(10.0 * m_gauss, 20.0 * beta)  # eV of padding on each side
271:    # σ_eV = m_gauss / (2√(2·ln2))  (convert FWHM to sigma)
272:    sigma_ev = m_gauss / (2.0 * np.sqrt(2.0 * np.log(2.0)))
810:def _make_peak_params(
830:    gl_ratio       : float – Lorentzian fraction for *_gl shapes  [0–1]
877:            _set("gl_ratio", spec.get("gl_ratio", 0.3),
878:                 expr=f"{m_prefix}gl_ratio" if spec.get("fix_fwhm", True) else None,
889:            _set("gamma_asym", spec.get("gamma_asym", 0.0),
890:                 expr=f"{m_prefix}gamma_asym" if spec.get("fix_fwhm", True) else None,
896:            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
928:        _set("gl_ratio", spec.get("gl_ratio", 0.3), min_=0.0, max_=1.0,
929:             vary=not spec.get("fix_gl_ratio", False))
938:        _set("gamma_asym", spec.get("gamma_asym", 0.0), min_=0.0, max_=5.0,
939:             vary=not spec.get("fix_gamma_asym", False))
945:        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0,
946:             vary=not spec.get("fix_m_gauss", False))
953:             vary=not spec.get("fix_m", True))
1136:    ``fix_gl_ratio`` the page still sends for a Gaussian, stale shape
1413:def run_fit(
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
sed: scripts/optimizer_disagreement_targets.py: No such file or directory

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/lineshape_roundtrip.test.js tests/js/lineshape_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -m pytest -p no:cacheprovider tests/test_voigt_contract.py tests/autofit/test_u4f_parity_battery.py -q' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 125ms:
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
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -m pytest -s -p no:cacheprovider tests/test_voigt_contract.py tests/autofit/test_u4f_parity_battery.py -q' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "sed -n '810,961p' fitting.py && sed -n '6195,6290p' templates/index.html && sed -n '11295,11390p' templates/index.html && sed -n '7355,7455p' templates/index.html && sed -n '183,250p' autofit/parity.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
def _make_peak_params(
    model: Model,
    spec: dict[str, Any],
    prefix: str,
    all_specs: list[dict],
) -> Parameters:
    """
    Build lmfit Parameters for one peak from a spec dict.

    Spec keys
    ---------
    shape          : str   – one of AVAILABLE_SHAPES
    center         : float – initial centre (eV)
    center_min     : float – lower bound   (optional)
    center_max     : float – upper bound   (optional)
    amplitude      : float – peak maximum counts
    amplitude_min  : float – lower bound   (default 0)
    fwhm           : float – full width at half max (eV)
    fwhm_min       : float – lower bound   (default 0.1)
    fwhm_max       : float – upper bound   (default 15.0)
    gl_ratio       : float – Lorentzian fraction for *_gl shapes  [0–1]
    asymmetry      : float – high-BE broadening factor for asymmetric_gl [0–1]
    alpha          : float – DS asymmetry index
    constrain_to   : str   – id of master peak (spin‑orbit slave)
    splitting      : float – centre offset from master (eV)
    area_ratio     : float – amplitude = master_amplitude × area_ratio
    fix_fwhm       : bool  – if True, lock FWHM to master value
    """
    shape = spec["shape"]
    p = model.make_params()

    center = spec.get("center", 285.0)
    amp = spec.get("amplitude", 1000.0)
    fwhm = spec.get("fwhm", 1.5)
    asymmetry = spec.get("asymmetry", 0.0)

    def _set(name, value, min_=None, max_=None, expr=None, vary=True):
        full = prefix + name
        if full not in p:
            return
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
            warnings.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> uncertainty could not be estimated (covariance matrix singular near this parameter). The fitted value may be unreliable.</li>`);
          }
        }
      }
    }
  }
  return { warnings, info };
}

// ═══════════════════════════════════════════════════
// SHORTCUTS MODAL
// ═══════════════════════════════════════════════════
function showShortcutsModal() {
  document.getElementById('shortcuts-modal-overlay').classList.add('open');
}
const _STARTS_TOOLTIP = "After your fit, the same method is run again from a few scattered starting points. If they all come back to your solution, that is what those starts found, no more: other starts or another method might not. If one finds a different solution with a lower χ²ᵣ it is listed here with how far each component moved from where you put it. Your fit is never replaced. A lower χ²ᵣ is not a better chemical model. Identical requests give identical results on real data in practice, but the underlying arithmetic is not bit-reproducible, so a fit sitting near a boundary between two solutions can still resolve differently; that is the situation this check is designed to surface.";

function _startsUnlinkedCount(peaks) { return (peaks || []).filter(p => !p.linked).length; }

// The evidence belongs to the FIT THAT PRODUCED IT: the model (everything the
// request reads from a peak) AND its context (background type and window,
// endpoint averaging, Shirley iterations, ROI, manual anchors, charge shift).
// The key is taken when the result is stored; it is compared, never
// invalidated by hand, so no edit path can be forgotten: after any change to
// a parameter, lock, shape, link, the peak list, the background, the ROI, the
// anchors or the charge correction — or an undo / history restore that brings
// back other values — the panel says the comparison no longer applies,
// nothing can be previewed or applied, and saves/exports carry no counts. A
// name, colour or visibility is not part of a fit and does not invalidate it.
const _STARTS_MODEL_FIELDS = ['id', 'shape', 'center', 'fwhm', 'amplitude', 'glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
  'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM', 'linked', 'linkOffset', 'linkRatio', '_afAsymMin', '_afAsymMax',
  'fixCenter', 'fixFwhm', 'fixAmplitude', 'fixGlMix', 'fixAsymmetry', 'fixDsAlpha', 'fixDsGamma',
  'fixLaAlpha', 'fixLaBeta', 'fixLaM', 'fixCaAlpha', 'fixCaBeta', 'fixCaM'];
const _STARTS_UI_FIELDS = ['bgType', 'bgStart', 'bgEnd', 'shirleyIter', 'endpointAvg', 'roiMin', 'roiMax'];
function _startsModelKey(peaks, ui, ccShift, anchors) {
  return JSON.stringify({
    p: (peaks || []).map(q => _STARTS_MODEL_FIELDS.map(k => (q[k] === undefined ? null : q[k]))),
    u: _STARTS_UI_FIELDS.map(k => String((ui || {})[k] ?? '')),
    s: Number(ccShift) || 0,
    a: (anchors || []).map(v => [v.x, v.y]),
  });
}
// The key of the ACTIVE tab as it stands now (live model, live controls).
function _startsLiveKey() {
  const ui = (typeof tabManager !== 'undefined' && tabManager && tabManager._captureUI) ? tabManager._captureUI() : {};
  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
}
// The key of a tab RECORD (project save runs after _syncActiveToRecord).
function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift, t.manualAnchors); }
// The starts evidence of `fr` if it still describes the fit whose key is `key`, else null.
function _startsIfCurrent(fr, key) {
  const st = fr && fr.starts;
  if (!st || !fr.startsModelKey || fr.startsModelKey !== key) return null;
  return st;
}
// After anything that may have changed the model or its context without going
// through a Results re-render (a lock toggle, Lock All, a background or ROI
// control): take a stale alternative overlay off the chart and bring the
// VISIBLE panel up to date (counts -> "the model has changed since this fit").
function _refreshStartsEvidence(repaint, fromPlot) {
  const hadAlt = !!(_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:'));
  _dropStaleAltPreview();
  if (repaint && hadAlt && !_historyPreview && typeof updatePlot === 'function') updatePlot();
  // The support verdicts are keyed the same way. If any is now stale (or
  // current again after an undo), every consumer that renders it must follow:
  // the Results table, the Quantify tab and the sidebar cards, not only the
  // starts panel. Rendered once, only when the visible state would change.
  // Each consumer is compared with ITS OWN rendering (a caller may have
  // redrawn the sidebar already, so the sidebar cannot vouch for the tables).
  const key = _startsLiveKey();
  const flaggedNow = state.peaks.filter(p => _isUnsupported(p, key)).map(p => String(p.id)).sort().join(',');
  const shownIn = sel => Array.from(document.querySelectorAll(sel)).map(e => e.getAttribute('data-peak-id')).sort().join(',');
  let rendered = false;
  if (shownIn('#peak-list .unsupported-badge') !== flaggedNow) { _patchPeakCardsForSupport(); rendered = true; }
  if (state.fitResult && shownIn('.results-table .unsupported-row') !== flaggedNow && typeof renderResults === 'function') { renderResults(); rendered = true; }   // renders Quantify and the starts panel too
  if (!fromPlot && state.chart && state.chart.data && typeof updatePlot === 'function') {
    const chartFlagged = (state.chart.data.datasets || []).filter(d => d._unsupported).map(d => String(d._peakId)).sort().join(',');
    if (chartFlagged !== flaggedNow) { updatePlot(); return; }
  }
  if (rendered) return;
  const el = document.querySelector('.starts-panel');
  if (el && state.fitResult) el.outerHTML = _startsPanelHtml(state.fitResult);
}

// An alternative's preview overlay is only valid beside the result it came from.
function _dropStaleAltPreview() {
  if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:') &&
      !(state.fitResult && _historyPreview.altKey === state.fitResult.startsModelKey && _startsIfCurrent(state.fitResult, _startsLiveKey()))) {
    _historyPreview = null;
  }
}

// What is persisted with a saved fit: the counts, never the alternatives'
// parameter sets (regenerable: the starts are a pure function of the request).
function _startsForSave(st) {
  if (!st) return null;
  if (!st.ran) return { ran: false, reason: st.reason || null };
  const alts = st.alternatives || [];
  return { ran: true, n_run: st.n_run, n_converged: st.n_converged, n_same_as_fit: st.n_same_as_fit,
           n_not_better_elsewhere: st.n_not_better_elsewhere,
           n_in_alternatives: st.n_in_alternatives ?? alts.reduce((n, a) => n + a.n_starts, 0),
           n_alternatives: alts.length || st.n_alternatives || 0,
           best_alternative_chi2r: alts.length ? alts[0].chi2r : (st.best_alternative_chi2r ?? null) };
}

// Counts STARTS and SOLUTIONS separately: three starts reaching one different
// solution is "3 starts found a DIFFERENT solution", not "one start".
function _startsSummaryText(st) {
  if (!st || !st.ran) return '';
  const nSol = (st.alternatives ? st.alternatives.length : st.n_alternatives) || 0;
  const nIn = st.n_in_alternatives ?? (st.alternatives || []).reduce((n, a) => n + a.n_starts, 0);
  const nb = st.n_not_better_elsewhere || 0, failed = st.n_run - st.n_converged;
  let t = `${st.n_same_as_fit} of ${st.n_run} scattered starts reached this solution`;
  const parts = [];
  if (nSol) parts.push(`${nIn} found ${nSol === 1 ? 'a DIFFERENT solution' : nSol + ' DIFFERENT solutions'} with a lower χ²ᵣ`);
  if (nb) {
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

exec
/bin/zsh -lc "git diff main..HEAD -- docs/findings/2026-09-fit-determinacy.md scripts/bg_window_worked_example.py scripts/endpoint_avg_sensitivity.py && rg --files | rg 'optimizer_disagreement|conftest|AGENTS' && rg -n 'def _peakArea|function _peakArea|n_perturb|startPeaks|_applyBackendParams|fix_fwhm' templates/index.html | head -80" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-TirLu0aY' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-wgx4dkuZ' (errno=Operation not permitted)
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
scripts/optimizer_disagreement_analyze.py
scripts/optimizer_disagreement_run_starts.py
scripts/optimizer_disagreement_analyze_starts.py
scripts/optimizer_disagreement_analyze_perturb.py
scripts/optimizer_disagreement_run.py
scripts/optimizer_disagreement_run_perturb.py
scripts/optimizer_disagreement_targets.js
tests/conftest.py
6216:    fix_fwhm: !!p.fixFwhm,
6280:      spec.fix_fwhm = true;
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
8313:function _peakArea(p, be) {

 exited 2 in 1860ms:

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
2 errors in 1.52s

exec
/bin/zsh -lc "cat scripts/optimizer_disagreement_targets.js && sed -n '6308,6335p' templates/index.html && sed -n '8300,8335p' templates/index.html && sed -n '120,175p' autofit/parity.py && sed -n '5055,5135p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "sed -n '1413,1455p' fitting.py && rg -n 'n_perturb|best_result|result =|perturb' fitting.py | tail -60 && sed -n '1,180p' tests/js/lineshape_parity.test.js && cat tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
def run_fit(
    energy: np.ndarray,
    counts: np.ndarray,
    peak_specs: list[dict[str, Any]],
    background_method: str = "shirley",
    bg_start_idx: int | None = None,
    bg_end_idx: int | None = None,
    charge_shift_ev: float = 0.0,
    fit_kws: dict | None = None,
    n_perturb: int = 0,
    manual_bg: list | None = None,
    endpoint_avg: int = 1,
    n_starts: int = 0,
    require_component=None,
) -> dict[str, Any]:
    """
    Run XPS peak fitting and return a serialisable result dict.

    Parameters
    ----------
    energy            : 1‑D array of binding energies (eV)
    counts            : 1‑D array of intensities (counts / CPS)
    peak_specs        : list of peak specification dicts (see _make_peak_params)
    background_method : 'shirley' | 'linear' | 'none'
    bg_start_idx      : slice start for background region (None → 0)
    bg_end_idx        : slice end for background region   (None → len)
    charge_shift_ev   : shift to apply to energy axis before fitting
    fit_kws           : extra kwargs forwarded to lmfit minimize

    Returns
    -------
    dict with keys: energy, fitted_y, background_y, residuals,
                    individual_peaks, statistics, charge_shift_applied, success
    """
    # One computation dtype: the weights are a function of the counts AND of
    # the precision they are held in (float32 counts give weights that differ
    # at 1e-8 and a different fit), and the seed hashes float64.
    energy = np.asarray(energy, dtype=float)
    counts = np.asarray(counts, dtype=float)
    if len(energy) != len(counts):
        raise ValueError("energy and counts must have the same length")
    if not peak_specs:
        raise ValueError("At least one peak specification is required")
95:    result = np.empty_like(x, dtype=float)
140:        result = amplitude * norm * np.cos(phase) / denom
147:        result = result * tail_decay
148:    result = np.where(np.isfinite(result), result, 0.0)
288:    result = np.interp(x, x_padded, ds_conv)
299:    result = amplitude * result / peak_val
527:    result = np.minimum(linear + B, ys)
709:    # finite-difference perturbation. Previously m was rounded with
1028:    perturb loop's comparison to a worse interior one, so every candidate is
1124:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1129:    solver options and ``n_perturb``.
1168:                       "n_perturb": n_perturb})
1422:    n_perturb: int = 0,
1608:    # Every random draw below (the perturbed restarts; the populations of the
1619:            fit_kws=fit_kws, n_perturb=n_perturb)
1622:    perturb_rng, solver_rng, starts_rng = (np.random.default_rng(child)
1638:        (one per minimisation, else every perturbed restart of differential
1670:        result = fit_once(all_params)
1686:    if n_perturb > 0 and result.success:
1687:        best_result = result
1689:        rng = perturb_rng
1691:        for attempt in range(n_perturb):
1692:            perturbed_params = result.params.copy()
1693:            for pname, par in perturbed_params.items():
1703:                    perturbed_params[pname].set(value=new_val)
1705:                    # For zero-valued params, add small absolute perturbation
1706:                    perturbed_params[pname].set(value=rng.uniform(0.001, 0.05))
1709:                trial = fit_once(perturbed_params)
1712:                          attempt + 1, n_perturb, trial_redchi, best_redchi)
1717:                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
1719:                    best_result = trial
1723:                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
1726:        if best_result is not result:
1729:            result = best_result
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
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
        bg[i0:i1] = bg_inner
        if i0 > 0:
            bg[:i0] = bg_inner[0]
        if i1 < len(y):
            bg[i1:] = bg_inner[-1]
    return bg


# ─────────────────────────────────────────────────────────────────────────────
# Parity records
# ─────────────────────────────────────────────────────────────────────────────

def battery_eligible(rf: ReferenceFit, region: str = "C 1s") -> tuple[bool, str]:
    """
    Single source of truth for battery/roster eligibility, shared by the
    fixture generator and the pytest battery so they can never disagree.

    Returns (eligible, reason-if-not).
    """
    if rf.region_guess() != region:
        return False, f"not {region}"
    fr = rf.fit_result
    if not fr.get("fittedY") or not fr.get("be"):
        return False, "legacy fitResult (no be/fittedY)"
    if len(fr["fittedY"]) != len(fr["be"]):
        return False, (
            f"internally inconsistent fitResult (fittedY {len(fr['fittedY'])} "
            f"pts vs be {len(fr['be'])} pts — stale fittedY from an earlier ROI)"
        )
    if not grid_matches(rf):
        return False, "fit-time grid drifted from current ui state"
    return True, ""


def grid_matches(rf: ReferenceFit, tol: float = 1e-3) -> bool:
    """
    True when the saved fit-time grid (``fitResult.be``) equals the ROI grid
    reconstructed from the tab's current ui state.  False means the tab's
    charge correction / ROI moved after the fit (the app shifts ui fields and
    peaks together but keeps ``fitResult`` in the fit-time frame) — those
    tabs are excluded from strict parity and logged instead.
    """
    saved_be = rf.fit_result.get("be")
    if not saved_be:
        return False
    roi = rf.roi_be
    if len(saved_be) != len(roi):
        return False
    return float(np.max(np.abs(np.asarray(saved_be, dtype=float) - roi))) <= tol


def eval_parity_relmax(rf: ReferenceFit) -> float:
    """
    Max |python_eval − saved fittedY| / max|fittedY| on the reconstructed
    ROI grid.  Requires ``grid_matches(rf)``.
    """
    fixCaM: true,
    isChargeReference: false
  }, overrides);
}

// ═══════════════════════════════════════════════════
// SHAPE-SPECIFIC PARAM SCHEMA
// ═══════════════════════════════════════════════════
// Single source of truth for the per-shape state of a peak. Used by
// _applyShapeSwitch to seed defaults ONLY for the parameters a newly-chosen
// Line Shape genuinely introduces (ones the peak does not already carry).
// Each entry includes both value defaults AND fix-flag defaults, matching
// defaultPeak, so a param a shape introduces for the first time lands in the
// same state as a freshly-created peak — the LACX `fixCaM: true` convention
// is the load-bearing example: omitting it from the schema would free `m`
// the first time a peak becomes LACX, which broke covariance estimation in
// the backend. NOTE: carried-over params are NEVER reset on a shape switch
// (that silently corrupted fitted values, e.g. DS+G's laM/laBeta on a
// round-trip) — the schema only fills in genuinely-new params.
//
// To add a new shape: register its value params AND fix-flag defaults
// here matching defaultPeak, then update evalPeak / renderShapeControls /
// peakToBackendSpec / applyBackendResult / runFit per the checklist in
// CLAUDE.md.
//
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

 exited 1 in 28093ms:
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
  duration_ms: 1156.817933
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
  duration_ms: 1195.497174
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
  duration_ms: 1143.280695
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
  duration_ms: 1155.668466
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
  duration_ms: 1124.667941
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
  duration_ms: 1147.008324
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
  duration_ms: 1151.893767
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
  duration_ms: 1119.319552
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
  duration_ms: 1138.529866
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
  duration_ms: 1129.077489
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
  duration_ms: 1344.40881
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
  duration_ms: 1196.424214
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
  duration_ms: 1120.107472
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
  duration_ms: 1131.707617
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
  duration_ms: 0.320228
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 16 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.16387
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 17 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.153473
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 18 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.154617
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 19 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.204627
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 20 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.245255
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
ok 21 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
  ---
  duration_ms: 10.155666
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 22 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.79177
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
  duration_ms: 2.768415
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
not ok 24 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1128.751818
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
  duration_ms: 1093.277924
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
  duration_ms: 1162.249441
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
  duration_ms: 1152.448973
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
  duration_ms: 1205.929249
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
  duration_ms: 1203.725808
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
  duration_ms: 1168.197382
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
  duration_ms: 1153.861659
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
  duration_ms: 1190.390832
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
  duration_ms: 1289.317645
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
  duration_ms: 1153.914743
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
  duration_ms: 1187.9347
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
  duration_ms: 1142.535648
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
  duration_ms: 1159.143229
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
  duration_ms: 1125.568662
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
  duration_ms: 1149.672351
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
  duration_ms: 1181.866115
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
  duration_ms: 1107.34902
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
  duration_ms: 1116.976282
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
  duration_ms: 1129.638041
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
  duration_ms: 1344.406685
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
  duration_ms: 1196.561012
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
  duration_ms: 1134.580885
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
# duration_ms 28136.56313

codex
I found two evidence problems: the eta measurement relies on an uncommitted target file and does not explicitly restore the old free-eta request; its “displayed” fractions also use trapezoidal integration and server LA curves, whereas the page uses rectangular integration and rounded LA smoothing.

The test runs stopped because dependency imports probe for a writable temporary directory. I’ll retry with an in-memory bootstrap that avoids that probe and leaves the checkout unchanged.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\", \"-p\", \"no:cacheprovider\", \"tests/test_voigt_contract.py\", \"tests/autofit/test_u4f_parity_battery.py\", \"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 5162ms:
...............................................................
63 passed in 4.81s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const cp = require('\\''node:child_process'\\''); const orig = cp.execFileSync;
cp.execFileSync = function(file, args, opts) {
 if(file.includes('\\''python'\\'')) args=['\\''-c'\\'','\\''import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name=\"__main__\")'\\'',...args];
 return orig(file,args,opts);
};
require('\\''./tests/js/lineshape_roundtrip.test.js'\\'');
require('\\''./tests/js/lineshape_parity.test.js'\\'');
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c '
import json
r=json.load(open('\\''docs/findings/a03/local_server_gap.json'\\''))
for region,rows in r['\\''regions'\\''].items():
 print(region)
 for x in rows:
  print(x['\\''target'\\''],round(x['\\''local_chi2r'\\''],5),round(x['\\''server_chi2r'\\''],5),'\\''chi %'\\'',round(100*(x['\\''local_chi2r'\\'']/x['\\''server_chi2r'\\'']-1),2),'\\''area %'\\'',round(x['\\''max_dArea_pct'\\''],3),'\\''frac pp'\\'',round(x['\\''max_dFrac_pp'\\''],3),'\\''m'\\'',[c['\\''server'\\''].get('\\''caM'\\'') for c in x['\\''comps'\\''] if c['\\''shape'\\'']=='\\''LACX'\\''])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
C1s
C1s Scan_0 4.35299 4.35719 chi % -0.1 area % 0.418 frac pp 0.04 m []
C1s Scan_1 13.07421 13.06613 chi % 0.06 area % 1.396 frac pp 0.322 m []
C1s Scan_2 4.08376 4.08696 chi % -0.08 area % 0.365 frac pp 0.049 m []
C1s Scan_3 4.42516 4.43167 chi % -0.15 area % 0.134 frac pp 0.019 m []
C1s Scan_4 18.21755 19.05636 chi % -4.4 area % 99.852 frac pp 15.066 m []
C1s Scan_5 4.33059 4.33204 chi % -0.03 area % 0.058 frac pp 0.005 m []
C1s Scan_6 5.21135 5.23013 chi % -0.36 area % 0.237 frac pp 0.022 m []
C1s Scan_7 7.99369 8.01581 chi % -0.28 area % 0.362 frac pp 0.035 m []
C1s Scan_8 2.74227 2.74076 chi % 0.06 area % 0.179 frac pp 0.018 m []
U4f
U4f Scan_0 2.06524 2.05519 chi % 0.49 area % 0.173 frac pp 0.013 m [8.072154418763597, 8.072154418763597]
U4f Scan_1 2.29609 2.26674 chi % 1.29 area % 1.954 frac pp 0.123 m [8.12187839344888, 8.12187839344888]
U4f Scan_2 1.93631 1.94006 chi % -0.19 area % 0.376 frac pp 0.016 m [8.335630649879592, 8.335630649879592]
U4f Scan_3 1.73175 1.73203 chi % -0.02 area % 1.741 frac pp 0.125 m [7.073802391508428, 7.073802391508428]
U4f Scan_4 1.97045 1.79827 chi % 9.57 area % 8.325 frac pp 0.33 m [2.693333881266681, 2.693333881266681]
U4f Scan_5 2.39286 2.17385 chi % 10.07 area % 6.649 frac pp 0.349 m [6.450794568196254, 6.450794568196254]
U4f Scan_6 2.65729 2.79758 chi % -5.01 area % 8.883 frac pp 0.766 m [9.995649813267388, 9.995649813267388]
U4f Scan_7 1.76359 1.75663 chi % 0.4 area % 0.488 frac pp 0.036 m [8.041257690555877, 8.041257690555877]
U4f Scan_8 4.65552 4.12926 chi % 12.74 area % 8.305 frac pp 0.323 m [7.930937469566035, 7.930937469566035]

exec
/bin/zsh -lc "sed -n '1,110p' autofit/reference.py && rg -n 'def load_project_tabs|def load_reference_fits|backend_peak_specs' autofit/reference.py && nl -ba scripts/voigt_eta_measure.py | sed -n '15,115p' && nl -ba tests/js/lineshape_roundtrip.test.js | sed -n '140,210p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
"""
Reference-fit loading for the autofit engine.

Reads the v3 ``.proj.zip`` / ``.proj.json`` project format (the same format
``templates/index.html`` saves) into plain-Python records, and reconstructs
the exact fit inputs the frontend would send to ``/api/fit``:

- corrected BE axis  = rawBE − ccShift          (``getCorrectedBE``)
- ROI slice          = corrected BE within [ui.roiMin, ui.roiMax], inclusive
                       (``getROIData``, index.html:4494)
- background indices = nearest ROI-grid index to ui.bgStart / ui.bgEnd
                       (the frontend rule up to 2026-09-03; kept here on
                       purpose so the committed expert-fit fixtures stay
                       byte-stable. Since unit 1c the frontend sends the
                       inside-range inclusive window, end_idx = i1 + 1, so
                       expert fits SAVED AFTER 1c are reconstructed one
                       point short here until the seal's settingsSnapshot
                       carries the actual indices — see the sealed-fit-
                       record memo, round-5 amendment)
- peak specs         = mirror of ``peakToBackendSpec`` (index.html:5708)

This module is read-only with respect to the app: it imports nothing from
``app.py`` and never mutates project files.
"""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Project loading
# ─────────────────────────────────────────────────────────────────────────────

def load_project_tabs(path: str | Path) -> list[dict]:
    """
    Return the list of raw tab dicts from a ``.proj.zip`` or ``.proj.json``.

    Zip layout (saved by ``_doSaveProject`` for >= 5 tabs): ``manifest.json``
    with ``{version: 3, spectra: [{index, filename, ...}]}`` plus one
    ``spectrum_<i>_<name>.json`` per tab.  JSON layout (< 5 tabs): a single
    object with ``tabs: [...]``.
    """
    path = Path(path)
    if path.suffix == ".zip" or path.name.endswith(".proj.zip"):
        with zipfile.ZipFile(path) as z:
            manifest = json.loads(z.read("manifest.json"))
            if manifest.get("version") != 3:
                raise ValueError(
                    f"{path.name}: unsupported project version "
                    f"{manifest.get('version')!r} (expected 3)"
                )
            tabs = []
            for entry in manifest.get("spectra", []):
                tabs.append(json.loads(z.read(entry["filename"])))
            return tabs
    data = json.loads(path.read_text())
    if not isinstance(data.get("tabs"), list):
        raise ValueError(f"{path.name}: no 'tabs' array — not a v3 project JSON")
    return data["tabs"]


# ─────────────────────────────────────────────────────────────────────────────
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
41:def load_project_tabs(path: str | Path) -> list[dict]:
261:    def backend_peak_specs(self) -> list[dict]:
304:def load_reference_fits(path: str | Path) -> list[ReferenceFit]:
    15	
    16	Usage:
    17	  python scripts/voigt_eta_measure.py targets.json out_dir shard n_shards   # one shard
    18	  python scripts/voigt_eta_measure.py --summary out_dir                     # the numbers
    19	targets.json is the optimizer-disagreement target file (uncommitted; built by
    20	scripts/optimizer_disagreement_targets.py from the committed projects).
    21	"""
    22	import copy
    23	import glob
    24	import json
    25	import os
    26	import statistics as st
    27	import sys
    28	import warnings
    29	
    30	import numpy as np
    31	
    32	sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    33	import fitting  # noqa: E402
    34	
    35	warnings.filterwarnings("ignore")
    36	
    37	
    38	def _pack(r):
    39	    return {"success": r["success"], "chi2r": r["statistics"]["reduced_chi_square"], "energy": r["energy"],
    40	            "peaks": [{"id": ip["id"], "y": ip["y"], "params": {k: v.get("value") for k, v in ip["params"].items()}}
    41	                      for ip in r["individual_peaks"]]}
    42	
    43	
    44	def measure(targets_path, out_dir, shard, n_shards):
    45	    targets = json.load(open(targets_path))
    46	    os.makedirs(out_dir, exist_ok=True)
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
   111	
   112	    print(f"free eta of {len(etas)} Voigt components: {sum(e < 0.01 for e in etas)} at 0 (pure Gaussian), "
   113	          f"{sum(e > 0.99 for e in etas)} at 1 (pure Lorentzian), {sum(0.4 <= e <= 0.6 for e in etas)} within 0.4–0.6")
   114	    e = [abs(c) for c in comp]
   115	    print(f"per-Voigt-component DISPLAYED area vs the fitted curve (%): {q(e)}; > 10 % on {sum(v > 10 for v in e)} of {len(e)}; "
   140	  const gl = res.individual_peaks[0].params.gl_ratio;
   141	  assert.equal(gl.vary, false, 'the server held η');
   142	  assert.equal(gl.value, 0.5);
   143	  assert.equal(peaks[0].glMix, 90, 'a Voigt keeps the glMix it carries for a later switch to GL; the fixed 0.5 is not written back');
   144	  assert.ok(maxRelDiff(env.evalPeakArray(res.energy, peaks[0]), res.individual_peaks[0].y, peaks[0].amplitude) < TIGHT_TOL);
   145	});
   146	
   147	test('a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)', () => {
   148	  const child = { truth: { id: 2, shape: 'Voigt', linked: 1, linkOffset: -10.9, linkRatio: 0.75, center: CENTER - 10.9, amplitude: 9000 }, start: { amplitude: 9000 * 0.8 } };
   149	  const { res, peaks } = roundTrip('Voigt', { ...CASES.Voigt, extraPeaks: [child] });
   150	  assert.equal(res.individual_peaks.length, 2);
   151	  for (const ip of res.individual_peaks) {
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

exec
/bin/zsh -lc "sed -n '70,165p' tests/js/lineshape_parity.test.js && sed -n '7540,7580p' templates/index.html && sed -n '7655,7745p' templates/index.html && cat tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
  if (peaks.length !== alt.components.length) return null;
  for (const c of alt.components) {
    const p = peaks.find(q => String(q.id) === String(c.id));
    if (!p) return null;
    const par = {};
    for (const k in c.params) par[k] = { value: c.params[k] };
    _applyBackendParams(p, par);
  }
  return peaks;
}

function _currentAlternative(k) {
  const st = _startsIfCurrent(state.fitResult, _startsLiveKey());
  return (st && st.ran && st.alternatives && st.alternatives[k]) || null;
}

const _STARTS_STALE_MSG = 'The model has changed since this fit. Run the fit again to compare solutions.';

function previewAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const key = 'alt:' + k;
  if (_historyPreview && _historyPreview.snapId === key) { _historyClearPreview(); return; }
  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  updatePlot();
}

// Adopting an alternative is the student's decision: explicit, undoable, and
// recorded. It is ATOMIC by construction: the alternative is only the START of
// an ordinary server fit (runFit's opts.startPeaks); the live model is written
// by that fit's success path and by nothing else, so a fit that fails, does
// not converge, is discarded because the tab changed, or cannot reach the
// server leaves peaks and result exactly as they were (no local fallback
// here: the local engine would start from the live model, not from the
// alternative). runFit's own pushUndo is the single undo entry. A solution
// that moves a component more than 1 eV from where the student put it is the
// measured trap (a lower chi-square bought by a chemically absurd relocation),
// so that case — and only that case — asks first, naming the component and
    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
    const fitReq = {
      session_id: sessionId,
      background: bgPayload,
      peaks: peakSpecs,
      fit_method: fitMethod,
      n_perturb: 3,
      n_starts: nStarts       // the server also skips it for the global methods
    };
    let resp, json;
    try {
      resp = await fetch('/api/fit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fitReq)
      });
    } catch (e) { _asTransport(e); }
    if (resp.ok === false) {
      // HTTP failure: read a message if the body is JSON, but a 502 HTML
      // page is still a SERVER failure, never a reason to switch engines.
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.serverError = true;
      throw err;
    }
    try { json = await resp.json(); } catch (e) { _asTransport(e); }
    if (json.error) {
      const err = new Error(json.error);
      err.serverError = true;
      throw err;
    }
    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
    // result that did not converge is a failed fit, not a result (audit A08:
    // until this unit success:false was applied and announced as complete).
    if (json.success !== true) {
      const err = new Error(json.message || 'the optimizer did not converge.');
      err.notConverged = true;
      throw err;
    }
    backendResult = json;

    // If the user switched tabs while the fit was running, discard the result
    // rather than overwriting the now-active tab's peaks.
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }

    // The peak controls stay editable while the fit runs. A result computed for
    // the model as it was must not be applied over an edited one (a newly locked
    // centre would keep its edited value under the server's statistics).
    if (_startsLiveKey() !== ctxAtRequest) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }

    // Capture pre-fit values for uncertainty validation
    const _preFit = {};
    for (const p of state.peaks) {
      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
    }
    applyBackendResult(backendResult);
    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
    const stats = backendResult.statistics || {};
    const chiReduced = stats.reduced_chi_square || 0;
    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
                        fittedY: backendResult.fitted_y, roiRange, _preFit,
                        starts: backendResult.starts || null,
                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
                        chosenAlternative: opts.chosenAlternative || null };
    // a preview of an alternative always belongs to the PREVIOUS result (an identical
    // key does not make it this one's): clear it unconditionally
    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
    state.fitResult.rFactor = _computeRFactor(state.fitResult);
    _applyStatDisplay(state.fitResult);
    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
    _updateRFactorUI(state.fitResult.rFactor);
    _updateROIDisplay(roiRange);
    _hideFitSpinner();
    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  } catch (e) {
    // Fall back to local Levenberg-Marquardt
    _hideFitSpinner();
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const cp=require('\\''child_process'\\''), fs=require('\\''fs'\\'');
const orig=cp.execFileSync;
cp.execFileSync=function(file,args,opts){
 if(file.includes('\\''python'\\'')){
   if(args[0]==='\\''-c'\\'') args=['\\''-c'\\'','\\''import tempfile; tempfile.tempdir=\"/tmp\"; '\\''+args[1],...args.slice(2)];
   else args=['\\''-c'\\'','\\''import tempfile,sys; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; code=open(sys.argv[0]).read().replace(\"fit_kws={\", \"n_perturb=3, fit_kws={\"); exec(compile(code,sys.argv[0],\"exec\"))'\\'',...args];
 }
 return orig(file,args,opts);
};
fs.writeFileSync=function(p,data){
 const r=JSON.parse(data); for(const [region,rows] of Object.entries(r.regions)) console.log(region,JSON.stringify(rows.map(x=>({target:x.target,chi:x.server_chi2r,area:x.max_dArea_pct,frac:x.max_dFrac_pp}))));
};
require('\\''./scripts/local_server_gap.js'\\'');
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c '
import tempfile; tempfile.tempdir=\"/tmp\"
import glob,json,subprocess,collections
from autofit.reference import load_project_tabs
tabs=[]
for path in glob.glob('\\''docs/autofit/test_data/*.proj.zip'\\''):
 for t in load_project_tabs(path):
  if t.get('\\''rawBE'\\'') and not t.get('\\''isStack'\\''):
   tabs.append(dict(t,project=path.split('\\''/'\\'')[-1]))
js=\"\"\"const fs=require('\\''fs'\\''), orig=fs.readFileSync; const data=fs.readFileSync(0,'\\''utf8'\\''); fs.readFileSync=(p,...a)=>p==='\\''virtual'\\''?data:orig(p,...a); process.argv[2]='\\''virtual'\\''; require('\\''./scripts/optimizer_disagreement_targets.js'\\'');\"\"\"
r=subprocess.run(['\\''node'\\'','\\''-e'\\'',js],input=json.dumps(tabs),text=True,capture_output=True,check=True)
targets=json.loads(r.stdout)
v=[t for t in targets if '\\''Voigt'\\'' in t['\\''shapes'\\'']]
print('\\''Voigt target count/kinds:'\\'',len(v),collections.Counter(t['\\''kind'\\''] for t in v))
t=v[0]; s=[s for s,sh in zip(t['\\''specs'\\''],t['\\''shapes'\\'']) if sh=='\\''Voigt'\\''][0]
print('\\''Regenerated input called free by measure():'\\'',s)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 626ms:
Voigt target count/kinds: 90 Counter({'own': 48, 'batch': 42})
Regenerated input called free by measure(): {'id': '4', 'name': 'Satellite 2', 'center': 396.98548110031726, 'amplitude': 1992.2050697513541, 'fwhm': 2.4312411268548155, 'amplitude_min': 0, 'fix_center': False, 'fix_fwhm': False, 'fix_amplitude': False, 'fix_gl_ratio': True, 'shape': 'pseudo_voigt_gl', 'gl_ratio': 0.5}

 succeeded in 63040ms:
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
  duration_ms: 1568.341243
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
ok 2 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1597.997585
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
ok 3 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1603.455393
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
ok 4 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1568.88432
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
ok 5 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1566.19277
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
ok 6 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1663.292529
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 7 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1733.761669
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
  duration_ms: 1648.002164
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
  duration_ms: 1766.096929
  type: 'test'
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
ok 10 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1697.90251
  type: 'test'
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
ok 11 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1753.847695
  type: 'test'
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
ok 12 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1763.118301
  type: 'test'
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
ok 13 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1670.538482
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Gaussian
ok 14 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1678.577753
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
ok 15 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1708.210208
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: GL
ok 16 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1648.111005
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Voigt
ok 17 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1676.134218
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DS
ok 18 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1662.556978
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
ok 19 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1644.474144
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)
not ok 20 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1673.156726
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
  duration_ms: 1685.287749
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed
not ok 22 - (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed # TODO DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above
  ---
  duration_ms: 1651.110623
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
  duration_ms: 1730.791054
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
ok 24 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1817.443364
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
ok 25 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1692.669454
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
ok 26 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1716.510846
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
ok 27 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1650.145236
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 28 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.234891
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 29 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.116263
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 30 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.15861
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 31 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.136137
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 32 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.444656
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 33 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.234295
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
ok 34 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
  ---
  duration_ms: 10.175225
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 35 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.341328
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
  duration_ms: 2.772647
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
ok 37 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1655.953575
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
ok 38 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1754.449209
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Voigt
ok 39 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1733.410088
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: GL
ok 40 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1662.022885
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
ok 41 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1746.139652
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DS
ok 42 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1745.849733
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
ok 43 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1744.815902
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
ok 44 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1831.216012
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP
not ok 45 - (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 2159.033997
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
  duration_ms: 1773.365016
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
# duration_ms 63094.307944

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\''),path=require('\\''path'\\''),Module=require('\\''module'\\'');
const orig=cp.execFileSync; cp.execFileSync=(file,args,opts)=>orig(file,['\\''-c'\\'','\\''import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name=\"__main__\")'\\'',...args],opts);
const filename=path.resolve('\\''tests/js/lineshape_roundtrip.test.js'\\''), src=fs.readFileSync(filename,'\\''utf8'\\'');
const tail="'`
for (const [shape,c] of [
 ['"'\\''asym-GL'\\'',{truth:{shape:'\\''asym-GL'\\'',glMix:0,asymmetry:0.35},start:{glMix:0,fixGlMix:true}}],
 ['\\''DS'\\'',{truth:{shape:'\\''DS'\\'',dsAlpha:0,dsGamma:0.3},start:{dsAlpha:0,fixDsAlpha:true,dsGamma:0.1}}]
]){
 const {res,peaks,specs}=roundTrip(shape,c);
 console.log(JSON.stringify({shape,spec:specs[0],peak:peaks[0],diffAmplitude:maxRelDiff(env.evalPeakArray(res.energy,peaks[0]),res.individual_peaks[0].y,peaks[0].amplitude)}));
}
"'`;
const m=new Module(filename,module);m.filename=filename;m.paths=module.paths;m._compile(src.slice(0,src.indexOf('"'\\''\\nfor (const [shape, c] of Object.entries(CASES))'\\''))+tail,filename);
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 3488ms:
/Users/skyefortier/.matplotlib is not a writable directory
{"shape":"asym-GL","spec":{"id":"1","name":"P","center":391.92,"amplitude":9600,"fwhm":1.92,"amplitude_min":0,"fix_center":false,"fix_fwhm":false,"fix_amplitude":false,"fix_gl_ratio":true,"shape":"asymmetric_gl","gl_ratio":0.5,"asymmetry":0.35,"fix_asymmetry":false},"peak":{"id":1,"name":"P","color":"#000","visible":true,"center":391.7375054934459,"amplitude":13612.422188283233,"fwhm":0.49125978764039885,"shape":"asym-GL","glMix":0,"asymmetry":0.6417761303263607,"dsAlpha":0.1,"dsGamma":0,"laAlpha":0.1,"laBeta":0.3,"laM":0.4,"caAlpha":1,"caBeta":1,"caM":50,"linked":null,"linkOffset":0,"linkRatio":1,"isChargeReference":false,"fixCenter":false,"fixFwhm":false,"fixAmplitude":false,"fixGlMix":true,"fixAsymmetry":false,"fixDsAlpha":false,"fixDsGamma":false,"fixLaAlpha":false,"fixLaBeta":false,"fixLaM":false,"fixCaAlpha":false,"fixCaBeta":false,"fixCaM":false,"_backendParams":{"amplitude":{"value":13612.422188283233,"stderr":1456.5139500745752,"vary":true,"expr":null,"min":0,"max":null},"center":{"value":391.7375054934459,"stderr":0.04147133863859532,"vary":true,"expr":null,"min":389.92,"max":393.92},"fwhm":{"value":0.49125978764039885,"stderr":0.058740533399402835,"vary":true,"expr":null,"min":0.1,"max":15},"asymmetry":{"value":0.6417761303263607,"stderr":0.2303066243581759,"vary":true,"expr":null,"min":0,"max":1},"gl_ratio":{"value":0.5,"stderr":0,"vary":false,"expr":null,"min":0,"max":1},"area":{"value":11387.088400929157,"stderr":1827.1234626375647}}},"diffAmplitude":0.06883634189452677}
/Users/skyefortier/.matplotlib is not a writable directory
{"shape":"DS","spec":{"id":"1","name":"P","center":391.92,"amplitude":9600,"fwhm":1.92,"amplitude_min":0,"fix_center":false,"fix_fwhm":false,"fix_amplitude":false,"fix_gl_ratio":false,"shape":"doniach_sunjic","alpha":0.1,"gamma_asym":0.1,"fix_alpha":true,"fix_gamma_asym":false},"peak":{"id":1,"name":"P","color":"#000","visible":true,"center":391.76395030367286,"amplitude":12266.75784492804,"fwhm":1.5575135611357056,"shape":"DS","glMix":30,"asymmetry":0,"dsAlpha":0,"dsGamma":0.5240689931834968,"laAlpha":0.1,"laBeta":0.3,"laM":0.4,"caAlpha":1,"caBeta":1,"caM":50,"linked":null,"linkOffset":0,"linkRatio":1,"isChargeReference":false,"fixCenter":false,"fixFwhm":false,"fixAmplitude":false,"fixGlMix":false,"fixAsymmetry":false,"fixDsAlpha":true,"fixDsGamma":false,"fixLaAlpha":false,"fixLaBeta":false,"fixLaM":false,"fixCaAlpha":false,"fixCaBeta":false,"fixCaM":false,"_backendParams":{"amplitude":{"value":12266.75784492804,"stderr":70.69157754947777,"vary":true,"expr":null,"min":0,"max":null},"center":{"value":391.76395030367286,"stderr":0.004574557961469793,"vary":true,"expr":null,"min":389.92,"max":393.92},"fwhm":{"value":1.5575135611357056,"stderr":0.010483799197364361,"vary":true,"expr":null,"min":0.1,"max":15},"alpha":{"value":0.1,"stderr":0,"vary":false,"expr":null,"min":0,"max":0.5},"gamma_asym":{"value":0.5240689931834968,"stderr":0.006503816761301644,"vary":true,"expr":null,"min":0,"max":5},"area":{"value":24585.60594870415,"stderr":217.85455653983652}}},"diffAmplitude":0.08799815719242636}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile,glob; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\",\"-p\",\"no:cacheprovider\", \"-q\"]+glob.glob(\"tests/autofit/test_*_parity_battery.py\")))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | sed -n '20,125p' && nl -ba scripts/local_server_gap.js | sed -n '56,82p' && rg -n 'Voigt' static app.py autofit --glob '"'!reference.py'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    20	The server fitted η; `_applyBackendParams` wrote it into `glMix`; nothing
    21	read `glMix` for a Voigt. So every number the page produced for a Voigt
    22	after Run Fit was the η = 0.5 curve evaluated with amplitude, width and
    23	centre fitted for a different mix, and the chart's components did not sum
    24	to the envelope (`fittedY` is the server's).
    25	
    26	## 2. Measured before deciding (`scripts/voigt_eta_measure.py`)
    27	
    28	The 90 committed targets with a Voigt component (89 U 4f tabs across five
    29	projects and one Cl 2p; 180 Voigt components), each fitted with the page's
    30	settings (Trust-Region, `n_perturb: 3`) both as sent before A03 (η free
    31	from 0.3) and as sent since (η held at 0.5). All 180 fits converged.
    32	
    33	| | median | p90 | max |
    34	|---|---:|---:|---:|
    35	| free η of the 180 Voigt components | 46 < 0.01 (pure Gaussian), 17 > 0.99 (pure Lorentzian), 24 within 0.4–0.6 | | |
    36	| DISPLAYED area of a Voigt vs the curve the server fitted | 11.8 % | 19.2 % | 20.1 % (103 of 180 > 10 %) |
    37	| A. displayed vs free-fit area fractions, per target | 0.96 pp | 1.49 pp | 1.60 pp (35 of 90 > 1 pp) |
    38	| B. fixed-η refit vs displayed — what a student sees change | 0.30 pp | 0.46 pp | 1.02 pp (1 of 90 > 1 pp) |
    39	| C. fixed-η refit vs the free fit | 0.93 pp | 1.31 pp | 2.04 pp (34 of 90 > 1 pp) |
    40	| χ²ᵣ fixed / free | 1.095 | 1.186 | 5.4 (fixed LOWER on 11 of 90: the free fit was in a worse minimum) |
    41	
    42	Row B is the release-note number: re-fitting a saved U 4f project moves an
    43	area fraction by 0.3 pp at the median and 1.0 pp at most, because the page
    44	already showed the 0.5 curve. Row A is the error that was shipping.
    45	
    46	## 3. Contract chosen: fixed η = 0.5 on BOTH sides
    47	
    48	`peakToBackendSpec` (and the twin) send `gl_ratio: 0.5, fix_gl_ratio: true`
    49	for a Voigt; `_applyBackendParams` writes `glMix` only for GL / asym-GL (a
    50	Voigt keeps the mix it carries for a later switch to GL); the dropdown says
    51	"Fixed 50/50 … choose GL to fit the mix". The other candidate — make the
    52	page honour the fitted η — would have turned "Voigt" into a GL with a
    53	hidden slider and kept, silently, a shape the student never chose (the
    54	owner's rule from the scattered-starts unit: never substitute an
    55	interpretation because it scored better); 63 of 180 fitted η values on a
    56	bound says the data did not determine the parameter in those fits. The
    57	seed hashes each parameter's effective role, so a Voigt request draws
    58	differently from the old one (test `test_seed_reflects_the_held_eta…`).
    59	
    60	Sites changed: `peakToBackendSpec`, `_applyBackendParams`, the Voigt
    61	`<option>` tooltip, `_localFitDetail`, `_LOCALFIT_TOOLTIP`, the fallback
    62	banner, `autofit/reference.py`, `scripts/endpoint_avg_sensitivity.py`,
    63	`scripts/bg_window_worked_example.py`, CLAUDE.md, `tests/js/fit_acceptance.test.js`.
    64	
    65	## 4. Two harnesses that would have caught it
    66	
    67	- `tests/js/lineshape_roundtrip.test.js` (+ `lineshape_roundtrip_backend.py`):
    68	  for every shape, synthetic data from a truth peak, a perturbed start,
    69	  request built by the PAGE's `peakToBackendSpec`, fitted by
    70	  `fitting.run_fit` (no background, Trust-Region), applied by the page's
    71	  `_applyBackendParams`, then `evalPeakArray` on the fitted grid must equal
    72	  `individual_peaks[].y` within 1e-6 of amplitude. Plus: the Voigt request
    73	  and write-back pins, a linked Voigt pair, a locked GL mix, and the Python
    74	  twin deep-equal to the page's builder for every shape and a link. Run
    75	  against main's page it fails on Voigt (0.93 % of amplitude), the Voigt
    76	  pins and the linked pair; on the branch 10 pass, 2 todo (below).
    77	- `tests/js/lineshape_parity.test.js` section (D): each shape's FREE
    78	  parameters swept across `_make_peak_params`'s bounds (η 0–1, asymmetry
    79	  0–1, DS α 0–0.5 / γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β
    80	  0.1–5 / m 0–499, fwhm 0.1–15), one bridge call per shape.
    81	- `tests/test_voigt_contract.py`: the twin, `run_fit` holding η and
    82	  returning the 0.5 curve, the seed.
    83	
    84	## 5. What the sweep found
    85	
    86	| shape | result |
    87	|---|---|
    88	| Gaussian, Lorentzian, Voigt (glMix 0 and 100 ignored), GL, asym-GL, DS | ≤ 6.1e-16 of amplitude at every combination |
    89	| DS+G, m < 0.001 (delta branch); LACX, m = 0 | exact |
    90	| LACX, m > 0 | up to 0.89 % of amplitude where the kernel is wide against the peak (m = 50 points on a 0.1 eV peak): the tracked discretisation gap (rounded m + 2m+1 kernel on the page vs continuous m on the server). `todo`, the `caM` clamp unit. |
    91	| DS+G, m ≥ 0.05 | the page's `laCasaXPS` quadrature sizes its step to resolve the Lorentzian core (β/3) and never the Gaussian kernel (σ = m/2.355): at β = 2, m = 0.05 the step is 0.67 eV against σ = 0.021 eV and the curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %; at the schema default (α 0.1, β 0.3, m 0.4) 3.9 %. 0 of 865 committed components use DS+G. `todo`; NOT fixed here (scope) — its own unit: port the server's padded-grid convolution to a grid-aware array evaluator, as `dsgDeltaKernel_array` already does for m < 0.001. |
    92	
    93	## 6. The re-measurement (`scripts/local_server_gap.js` → `docs/findings/a03/local_server_gap.json`)
    94	
    95	W1's 18 Batch Fit targets of the committed UCl4-graphite project, local
    96	engine vs server from the same scaled start, page semantics on both sides.
    97	
    98	| set | max Δcentre | max ΔFWHM | max Δarea | max Δfraction |
    99	|---|---:|---:|---:|---:|
   100	| C 1s, 8 of 9 (W1) | 3.8 meV | 0.50 % | 1.40 % | 0.32 pp |
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
    56	}
    57	const area = (env, be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return env.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
    58	const out = { generated: new Date().toISOString(), regions: {} };
    59	for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
    60	  const names = tabs.filter(t => new RegExp('^' + sourceName.replace(' ', ' ') + '_\\d+$').test(t.name)).map(t => t.name);
    61	  out.regions[region] = [];
    62	  for (const name of names) {
    63	    const env = makeEnv(); const T = target(env, sourceName, name);
    64	    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
    65	    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
    66	    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
    67	    const srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: T.start, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    68	    const serverPeaks = JSON.parse(JSON.stringify(T.start));
    69	    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(serverPeaks[i], par); });
    70	    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
    71	    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p));
    72	    const tL = aL.reduce((s, v) => s + v, 0), tS = aS.reduce((s, v) => s + v, 0);
    73	    const comps = localPeaks.map((p, i) => ({ name: p.name, shape: p.shape, linked: !!p.linked,
    74	      dCenter_meV: 1000 * (p.center - serverPeaks[i].center), dFwhm_pct: 100 * (p.fwhm / serverPeaks[i].fwhm - 1),
    75	      dArea_pct: aS[i] ? 100 * (aL[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aL[i] / tL - aS[i] / tS),
    76	      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM } }));
    77	    const mx = f => Math.max(...comps.map(c => Math.abs(c[f]) || 0));
    78	    out.regions[region].push({ target: name, local_success: loc.success, local_chi2r: env.state.fitResult && env.state.fitResult.chiReduced, server_success: srv.success, server_chi2r: srv.chi2r,
    79	      max_dCenter_meV: mx('dCenter_meV'), max_dFwhm_pct: mx('dFwhm_pct'), max_dArea_pct: mx('dArea_pct'), max_dFrac_pp: mx('dFrac_pp'), comps });
    80	    console.error(region, name, 'local', loc.success, (env.state.fitResult || {}).chiReduced && env.state.fitResult.chiReduced.toFixed(3), 'server', srv.success, srv.chi2r.toFixed(3), 'max Δcentre', mx('dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('dFwhm_pct').toFixed(2), '%, Δarea', mx('dArea_pct').toFixed(2), '%, Δfrac', mx('dFrac_pp').toFixed(2), 'pp');
    81	  }
    82	}
app.py:530:            "pseudo_voigt_gl": "Pseudo-Voigt GL mix  (η = Lorentzian fraction)",
autofit/engine.py:589:            # ONLY for the pseudo-Voigt with a shared mixing parameter —
autofit/engine.py:614:                    "share_parent_params (the pseudo-Voigt area factor "
autofit/engine.py:798:        # Olivero & Longbothum 1977 Voigt-FWHM approximation (0.02%).
autofit/regions/u4f.py:19:  Voigt pair (sat7/2 offset-linked to the main; sat5/2 linked to sat7/2 at

 succeeded in 6488ms:
......................................................................................................................
118 passed in 6.11s

codex
The focused tests pass with the read-only bootstrap: 63 Python tests, plus 39 JS passes and 7 declared TODOs. Two added endpoint probes expose gaps the harness misses: locked asym-GL mix 0 produces a 6.88% drawn-versus-fitted mismatch, and locked DS α=0 produces an 8.80% mismatch. Both request-builder defects predate A03.

I also confirmed that the 90 measurement targets contain 48 saved-model starts and 42 Batch Fit starts. They do not directly establish the claimed change from what a saved project displayed before refitting.

exec
/bin/zsh -lc "sed -n '258,272p' autofit/reference.py && rg -n 'uncertainty.*info|validation.info|\\.info\\.' templates/index.html && nl -ba docs/findings/2026-09-fit-determinacy.md | sed -n '277,298p' && git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 0ms:
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

exec
/bin/zsh -lc "rg -n '_validateUncertainties|uncInfo|info\\.length|info.join' templates/index.html && nl -ba docs/findings/2026-09-fit-determinacy.md | sed -n '277,298p' && git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
8431:  const { warnings: uncWarnings, info: uncInfo } = _validateUncertainties();
8438:  if (uncInfo.length) {
8441:      <ul>${uncInfo.join('')}</ul>
11311:function _validateUncertainties() {
   277	Fixed on both sides (η = 0.5 held in the request). What a student SEES
   278	change on re-fitting a saved project is small — the fixed refit vs what the
   279	page displayed: median 0.30 pp, max 1.02 pp (1 target > 1 pp) — because both
   280	are the 0.5 curve; the refit vs the server's own free-η fit is median
   281	0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9.5 % (the mix is one parameter
   282	fewer). The alternative — honour the fitted η on the page — would have made
   283	"Voigt" a GL with a hidden slider and silently kept a shape the student had
   284	not chosen; 63 of 180 fitted values sitting on a bound says the parameter
   285	was not determined by the data in those fits anyway.
   286	
   287	**The re-measurement (W1 methodology, 18 targets).** C 1s unchanged (8 of 9
   288	within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is the §2 finding). U 4f,
   289	W1 → A03: max Δcentre 39.7 → 28.8 meV, ΔFWHM 17.2 → 15.8 %, Δarea 20.8 →
   290	8.9 %, Δfraction 1.4 → 0.77 pp. On the 5 of 9 targets where both engines
   291	reach the same minimum (χ²ᵣ equal to 2–3 digits) every component is within
   292	4.3 meV, 2.6 %, 2.0 %, 0.12 pp — the Voigt gap is gone. On the other 4 the
   293	server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
   294	7.9 while the local engine holds it; χ²ᵣ differs by 8–20 % (the local engine
   295	LOWER on Scan_6, 2.657 vs 2.798), and the satellites, which share the
   296	region, differ by up to 8.9 % in area. That residual is the `caM` clamp,
   297	next; the "starting point" label stays until it is done and re-measured.
   298	
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-nNaBEqg7' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ulk2Zec2' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_review_prompt.txt
?? docs/autofit/codex/a03_voigt_eta_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_verdict_runB.md

exec
/bin/zsh -lc "rg -n 'U4f Scan_[4568]|local_chi2r|server_chi2r' docs/findings/a03/local_server_gap.json | tail -30 && nl -ba tests/js/lineshape_parity.test.js | sed -n '328,380p' && sed -n '8428,8445p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
763:    "local_chi2r": 4.33059226290776,
765:    "server_chi2r": 4.332040777459363,
914:    "local_chi2r": 5.211351022553858,
916:    "server_chi2r": 5.230133054457079,
1065:    "local_chi2r": 7.993689089250659,
1067:    "server_chi2r": 8.015808637637003,
1216:    "local_chi2r": 2.742274861910659,
1218:    "server_chi2r": 2.7407625419220305,
1369:    "local_chi2r": 2.065244443877729,
1371:    "server_chi2r": 2.0551875684374585,
1472:    "local_chi2r": 2.296093573631544,
1474:    "server_chi2r": 2.2667421415660436,
1575:    "local_chi2r": 1.9363101556852207,
1577:    "server_chi2r": 1.9400626785090727,
1678:    "local_chi2r": 1.731754888573654,
1680:    "server_chi2r": 1.7320297992148836,
1779:    "target": "U4f Scan_4",
1781:    "local_chi2r": 1.9704477171249217,
1783:    "server_chi2r": 1.7982704261503648,
1882:    "target": "U4f Scan_5",
1884:    "local_chi2r": 2.3928635306048918,
1886:    "server_chi2r": 2.173852692313437,
1985:    "target": "U4f Scan_6",
1987:    "local_chi2r": 2.657291813593791,
1989:    "server_chi2r": 2.797581089317341,
2090:    "local_chi2r": 1.7635921032129218,
2092:    "server_chi2r": 1.7566316793234622,
2191:    "target": "U4f Scan_8",
2193:    "local_chi2r": 4.655520835587359,
2195:    "server_chi2r": 4.129258441354809,
   328	  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
   329	  return JSON.parse(out);
   330	}
   331	function combos(ranges) {
   332	  let out = [{}];
   333	  for (const k of Object.keys(ranges)) out = out.flatMap(o => ranges[k].map(v => ({ ...o, [k]: v })));
   334	  return out;
   335	}
   336	const FWHM_RANGE = [0.1, 1.83, 15];
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
  // Uncertainty warnings (backend fit only). Genuine alarms go in the amber
  // warn-box; intentionally locked params get a neutral info-box so they
  // stop reading as scary regressions after auto-fit locks centers.
  const { warnings: uncWarnings, info: uncInfo } = _validateUncertainties();
  if (uncWarnings.length) {
    html += `<div class="unc-warn-box">
      <div class="uw-title">&#9888; Uncertainty Warnings</div>
      <ul>${uncWarnings.join('')}</ul>
    </div>`;
  }
  if (uncInfo.length) {
    html += `<div class="unc-info-box">
      <div class="uw-title">&#128274; Locked Parameters</div>
      <ul>${uncInfo.join('')}</ul>
    </div>`;
  }

  el.innerHTML = html;

 exited 130 in 111390ms:
/Users/skyefortier/.matplotlib is not a writable directory
C1s C1s Scan_0 local true 4.353 server true 4.357 max Δcentre 3.8 meV, ΔFWHM 0.29 %, Δarea 0.42 %, Δfrac 0.04 pp
/Users/skyefortier/.matplotlib is not a writable directory
C1s C1s Scan_1 local true 13.074 server true 13.066 max Δcentre 2.6 meV, ΔFWHM 0.50 %, Δarea 1.40 %, Δfrac 0.32 pp
/Users/skyefortier/.matplotlib is not a writable directory
C1s C1s Scan_2 local true 4.084 server true 4.087 max Δcentre 3.5 meV, ΔFWHM 0.07 %, Δarea 0.37 %, Δfrac 0.05 pp
/Users/skyefortier/.matplotlib is not a writable directory
C1s C1s Scan_3 local true 4.425 server true 4.432 max Δcentre 1.2 meV, ΔFWHM 0.04 %, Δarea 0.11 %, Δfrac 0.02 pp
/Users/skyefortier/.matplotlib is not a writable directory
C1s C1s Scan_4 local true 18.218 server true 19.056 max Δcentre 41.9 meV, ΔFWHM 8.97 %, Δarea 99.85 %, Δfrac 15.07 pp
/Users/skyefortier/.matplotlib is not a writable directory
C1s C1s Scan_5 local true 4.331 server true 4.332 max Δcentre 0.6 meV, ΔFWHM 0.03 %, Δarea 0.06 %, Δfrac 0.00 pp
/Users/skyefortier/.matplotlib is not a writable directory
C1s C1s Scan_6 local true 5.211 server true 5.230 max Δcentre 2.1 meV, ΔFWHM 0.17 %, Δarea 0.24 %, Δfrac 0.02 pp

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const cp=require('\\''child_process'\\''), fs=require('\\''fs'\\'');
const orig=cp.execFileSync;
cp.execFileSync=function(file,args,opts){
 if(file.includes('\\''python'\\'')){
   if(args[0]==='\\''-c'\\'') {
     args=['\\''-c'\\'','\\''import tempfile; tempfile.tempdir=\"/tmp\"; '\\''+args[1],...args.slice(2)];
     const tabs=JSON.parse(orig(file,args,opts));
     return JSON.stringify(tabs.filter(t=>['\\''U4f Scan'\\'','\\''U4f Scan_6'\\''].includes(t.name)));
   }
   else args=['\\''-c'\\'','\\''import tempfile,sys; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; code=open(sys.argv[0]).read().replace(\"fit_kws={\", \"n_perturb=3, fit_kws={\"); exec(compile(code,sys.argv[0],\"exec\"))'\\'',...args];
 }
 return orig(file,args,opts);
};
fs.writeFileSync=function(p,data){
 const r=JSON.parse(data); for(const [region,rows] of Object.entries(r.regions)) console.log(region,JSON.stringify(rows.map(x=>({target:x.target,chi:x.server_chi2r,area:x.max_dArea_pct,frac:x.max_dFrac_pp,m:x.comps.filter(c=>c.shape==='\\''LACX'\\'').map(c=>c.server.caM)}))));
};
require('\\''./scripts/local_server_gap.js'\\'');
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 2429ms:
/Users/skyefortier/.matplotlib is not a writable directory
U4f U4f Scan_6 local true 2.657 server true 2.798 max Δcentre 28.8 meV, ΔFWHM 15.81 %, Δarea 8.88 %, Δfrac 0.77 pp
C1s []
U4f [{"target":"U4f Scan_6","chi":2.797581088893732,"area":8.88303774390109,"frac":0.7658566210456907,"m":[9.99564981324184,9.99564981324184]}]

codex
All region parity batteries pass: 118 tests. Refit-from-refit is a meaningful stationarity check, and the frozen fixture remains an independent regression check.

The main concerns are the measurement claims and missing endpoint coverage. Keeping Voigt fixed at 0.5 preserves its existing contract, and retaining “starting point” is supported. The evidence does not yet isolate the entire residual to caM.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const cp=require('\\''child_process'\\''),fs=require('\\''fs'\\''),orig=cp.execFileSync;
cp.execFileSync=function(file,args,opts){
 if(args[0]==='\\''-c'\\''){
  const tabs=JSON.parse(orig(file,['\\''-c'\\'','\\''import tempfile; tempfile.tempdir=\"/tmp\"; '\\''+args[1],...args.slice(2)],opts));
  return JSON.stringify(tabs.filter(t=>['\\''U4f Scan'\\'','\\''U4f Scan_6'\\''].includes(t.name)));
 }
 const d=JSON.parse(opts.input); d.peaks.forEach(p=>{if(p.shape==='\\''LACX'\\'')p.fixCaM=true});
 opts={...opts,input:JSON.stringify(d)};
 return orig(file,['\\''-c'\\'','\\''import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name=\"__main__\")'\\'',...args],opts);
};
fs.writeFileSync=(p,data)=>{const r=JSON.parse(data); console.log(JSON.stringify(r.regions.U4f.map(x=>({target:x.target,localChi:x.local_chi2r,serverChi:x.server_chi2r,area:x.max_dArea_pct,frac:x.max_dFrac_pp,m:x.comps.filter(c=>c.shape==='\\''LACX'\\'').map(c=>c.server.caM)}))))};
require('\\''./scripts/local_server_gap.js'\\'');
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 2222ms:
/Users/skyefortier/.matplotlib is not a writable directory
U4f U4f Scan_6 local true 2.657 server true 2.634 max Δcentre 3.7 meV, ΔFWHM 1.31 %, Δarea 1.36 %, Δfrac 0.07 pp
[{"target":"U4f Scan_6","localChi":2.657291813593791,"serverChi":2.6341642390705946,"area":1.3594139989251186,"frac":0.06960876701660942,"m":[8.19934520780095,8.19934520780095]}]

codex
No BLOCKER found. Two MAJOR measurement defects prevent approval of A03 as documented.

1. **MAJOR — Regenerating inputs destroys the “old free-η” baseline.** [scripts/voigt_eta_measure.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:59) copies the input specs into `free` without restoring `gl_ratio=0.3, fix_gl_ratio=false`. The committed target generator extracts the **current page builder**, so regenerated Voigt specs already contain held 0.5. I verified this. Both measurement arms then fit the same request, producing zero differences instead of the committed summary. Explicitly construct both contracts and make regeneration self-contained; the documented `.py` target generator also does not exist—the generator is `.js`.

2. **MAJOR — The release-note numbers do not measure changes from a saved project’s displayed fractions.** [scripts/voigt_eta_measure.py:79](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:79) uses trapezoidal integration, retains server curves for non-Voigt components, and compares against a newly optimized free-η fit. The page uses rectangular integration and rounded LA smoothing. Furthermore, regenerating the 90 targets yields **48 own-model starts and 42 Batch Fit starts**, not 90 saved-tab refits. For a saved U 4f model containing LA components, neither baseline nor fraction denominator necessarily matches the screen. Measure saved page peaks versus applied refit peaks using page evaluation and integration before calling **0.30 pp / 1.02 pp** the student-visible migration impact.

3. **MINOR — The new harness misses real request/lock failures at zero endpoints.** [tests/js/lineshape_roundtrip.test.js:161](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:161) tests a locked GL mix only at 30; the sweep uses its own parameter mapping. Using the new round-trip machinery, I reproduced:
   - asym-GL, `glMix=0`, `fixGlMix=true`: request substitutes 0.5; drawn/fitted discrepancy **6.88% of amplitude**.
   - DS, `dsAlpha=0`, `fixDsAlpha=true`: request substitutes 0.1; discrepancy **8.80%**.

   These builder defects predate A03, but the claimed coverage misses them. Add endpoint lock cases and explicitly track these gaps. Comparing two matching twins cannot establish that their shared defaults are correct.

4. **MINOR — Voigt now offers an impossible unlock instruction.** Holding η at [templates/index.html:6235](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:6235) triggers `_validateUncertainties`’ generic “gl_ratio: locked — unlock the padlock to refine.” A supported, unlinked Voigt has no mix padlock. Describe the fixed shape contract and direct the user to GL instead.

5. **MINOR — Several documented numbers contradict the committed artifacts.** [plan:111](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:111) says χ²ᵣ differs by 8–20%. For Scan_4/5/6/8, the JSON gives **+9.57%, +10.07%, −5.01%, +12.74%**, relative to server χ²ᵣ. The request-builder comment says **24%** area error versus the summary’s **20.11%**; row A says **1.60 pp** versus **1.61 pp**. Correct the repeated claims in the plan, findings and CLAUDE.md.

The fixed-0.5 choice is defensible as preserving the explicit shape contract. The measurements do not establish that 0.5 is physically optimal for U 4f, and boundary-hitting alone does not establish non-identifiability.

Retaining **“starting point”** is correct. On Scan_6, using the page’s three perturbations retained the approximately 8.88% area gap. Holding server LA smoothing at its starting value reduced it to 1.36%, supporting caM as a substantial contributor without proving it explains every residual.

Refit-from-refit is meaningful, not tautological; the frozen fixture remains a separate regression check. I found no additional non-Voigt request, `/api/analyze`, or local-engine changes.

Validation: **122 Python tests passed** across the contract and region batteries; **39 JS tests passed, 7 TODOs**. Tests used an in-memory bootstrap for the read-only environment. No files changed.

**VERDICT: NO-GO**
tokens used
106,674
No BLOCKER found. Two MAJOR measurement defects prevent approval of A03 as documented.

1. **MAJOR — Regenerating inputs destroys the “old free-η” baseline.** [scripts/voigt_eta_measure.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:59) copies the input specs into `free` without restoring `gl_ratio=0.3, fix_gl_ratio=false`. The committed target generator extracts the **current page builder**, so regenerated Voigt specs already contain held 0.5. I verified this. Both measurement arms then fit the same request, producing zero differences instead of the committed summary. Explicitly construct both contracts and make regeneration self-contained; the documented `.py` target generator also does not exist—the generator is `.js`.

2. **MAJOR — The release-note numbers do not measure changes from a saved project’s displayed fractions.** [scripts/voigt_eta_measure.py:79](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:79) uses trapezoidal integration, retains server curves for non-Voigt components, and compares against a newly optimized free-η fit. The page uses rectangular integration and rounded LA smoothing. Furthermore, regenerating the 90 targets yields **48 own-model starts and 42 Batch Fit starts**, not 90 saved-tab refits. For a saved U 4f model containing LA components, neither baseline nor fraction denominator necessarily matches the screen. Measure saved page peaks versus applied refit peaks using page evaluation and integration before calling **0.30 pp / 1.02 pp** the student-visible migration impact.

3. **MINOR — The new harness misses real request/lock failures at zero endpoints.** [tests/js/lineshape_roundtrip.test.js:161](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:161) tests a locked GL mix only at 30; the sweep uses its own parameter mapping. Using the new round-trip machinery, I reproduced:
   - asym-GL, `glMix=0`, `fixGlMix=true`: request substitutes 0.5; drawn/fitted discrepancy **6.88% of amplitude**.
   - DS, `dsAlpha=0`, `fixDsAlpha=true`: request substitutes 0.1; discrepancy **8.80%**.

   These builder defects predate A03, but the claimed coverage misses them. Add endpoint lock cases and explicitly track these gaps. Comparing two matching twins cannot establish that their shared defaults are correct.

4. **MINOR — Voigt now offers an impossible unlock instruction.** Holding η at [templates/index.html:6235](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:6235) triggers `_validateUncertainties`’ generic “gl_ratio: locked — unlock the padlock to refine.” A supported, unlinked Voigt has no mix padlock. Describe the fixed shape contract and direct the user to GL instead.

5. **MINOR — Several documented numbers contradict the committed artifacts.** [plan:111](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:111) says χ²ᵣ differs by 8–20%. For Scan_4/5/6/8, the JSON gives **+9.57%, +10.07%, −5.01%, +12.74%**, relative to server χ²ᵣ. The request-builder comment says **24%** area error versus the summary’s **20.11%**; row A says **1.60 pp** versus **1.61 pp**. Correct the repeated claims in the plan, findings and CLAUDE.md.

The fixed-0.5 choice is defensible as preserving the explicit shape contract. The measurements do not establish that 0.5 is physically optimal for U 4f, and boundary-hitting alone does not establish non-identifiability.

Retaining **“starting point”** is correct. On Scan_6, using the page’s three perturbations retained the approximately 8.88% area gap. Holding server LA smoothing at its starting value reduced it to 1.36%, supporting caM as a substantial contributor without proving it explains every residual.

Refit-from-refit is meaningful, not tautological; the frozen fixture remains a separate regression check. I found no additional non-Voigt request, `/api/analyze`, or local-engine changes.

Validation: **122 Python tests passed** across the contract and region batteries; **39 JS tests passed, 7 TODOs**. Tests used an in-memory bootstrap for the read-only environment. No files changed.

**VERDICT: NO-GO**
