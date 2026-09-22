OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0cade-0d18-7aa0-9196-84d23b12e202
--------
user
Review unit fix-dsg-page-evaluator: git diff main..HEAD (templates/index.html, tests/js/lineshape_parity.test.js, tests/js/lineshape_roundtrip.test.js, the four extractor lists, CLAUDE.md, docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md, docs/findings/2026-09-fit-determinacy.md §7). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

CONTEXT (read the plan first). The page's DS+G evaluator (laCasaXPS, a numerical quadrature) was wrong across the fitted beta/m range (A03 sweep: 1e52 x amplitude at beta 2 / m 0.05; 5-21 % low in area on the box Find Peaks emits for a graphitic C 1s line - every A- and M-family candidate). Owner: port the server's convolution to a grid-aware page evaluator; nothing de-listed, nothing changed in Find Peaks; acceptance = the todo tests (parity sweep DS+G box at 1e-6, the round-trip case) PLUS convergence across the full beta/m range the optimiser can reach, including the 1e52 corners.

THE CHANGE. dsgConvolved_array(beArr, center, alpha, beta, m) in templates/index.html mirrors fitting._ds_g_dscore_gauss for m >= 0.001 (the delta branch dsgDeltaKernel_array for m < 0.001 already existed): alpha clip [0, 0.495], beta >= 1e-6, m >= 0; step = numpy median |dx| (>= 1e-6); padded grid +/- max(10 m, 20 beta) at that step with np.linspace semantics; DS core with non-finite -> 0; half-cosine tapers np.linspace(0, pi, n_pad); Gaussian kernel sigma = m/(2 sqrt(2 ln 2)) on the same step centred at (n-1)/2, normalised to unit sum over the FULL padded length; the server's irfft(rfft(ds) * rfft(ifftshift(kernel))) evaluated DIRECTLY as out[i] = sum_j ds[j] * kernel[(i - j + floor(n/2)) mod n] with j restricted to |i - j| <= ceil(8 sigma/step) + 1; np.interp back to the data grid; normalisation by the value interpolated at the centre with the server's fallbacks; non-finite -> 0. evalPeakArray routes every DS+G through it. laCasaXPS (the scalar evalPeak branch) is now the normalised DS core with m IGNORED, the same status as evalPeak's LACX branch; parity guard (C) proves no shipped caller reaches evalPeak. Measured: <= 3e-15 of amplitude across alpha {0, 0.25, 0.49} x beta {0.05, 0.7, 2} x m {0.001, 0.05, 0.4, 2, 4} on the base grid and < 1e-6 on seven other grids (0.1 and 0.02 eV steps, descending, half-step and 0.03 eV off-grid centres, a 30-point window narrower than the pad, a 0.0503 eV step); the browser check on a committed C 1s scan agrees to 1.2e-12. Cost 0.3-5.5 ms per evaluation; a local fit with a DS+G converges in 69 ms.

TRY TO BREAK
a. The mirror, line by line against fitting.py 152-305: the median step (even/odd counts, an irregular grid where the median differs from the mean), np.linspace's endpoint, the taper's n_pad == 1 case, kernel centring for EVEN n_total (k_half half-integer; ifftshift's floor(n/2)), the circular wrap at the array ends (does the window restriction ever drop kernel mass that the FFT includes? construct a grid where n_total is small relative to 8 sigma/step), the 8-sigma truncation's error bound against 1e-6, np.interp clamping outside the padded grid (can a data point lie outside it? it cannot, by construction - verify), the centre outside the data range (a free DS+G centre has no window on the server), peak_val <= 0 fallbacks, a grid of 1 or 2 points (short-input tests exist for LA: tests/test_la_short_input.py - what does the page do for DS+G on N = 1, 2?).
b. Precision: JS Math.exp/cos/pow vs numpy at these magnitudes; accumulation order in the convolution sum vs the FFT - is 1e-6 of amplitude honest headroom at the corners (beta 0.05 with m 4: sigma/step = 34; beta 2 with m 0.05)?
c. Every page path that evaluates a DS+G: chart, _peakArea (Results, sidebar, Quantify, CSV/XLSX/TSV), figure export, stack tabs, the local engine's Jacobian (runFitLocal evaluates through evalAllPeaks -> evalPeakArray; the finite-difference step in laM/laBeta - does the grid-dependent padding change discontinuously with a parameter step and upset the derivative?), the Find Peaks candidate preview, Batch Fit. Any caller that still reaches the scalar evalPeak for a DS+G? (guard C.)
d. Performance: the padded length is (N + 2 n_pad) with n_pad = max(10 m, 20 beta)/step - for beta 2 on a 0.02 eV grid that is 2000 points each side and W = 8 sigma/step; is a chart redraw or a local fit still responsive? Where is the worst case reachable from the UI?
e. Tests: are the hard assertions really hard (no todo left that hides a DS+G case)? Does (D') exercise the delta threshold on the other grids? Is anything in the sweep still comparing the page against a mapping of the harness's own rather than the page's request builder?
f. Docs vs code: every number in the plan, CLAUDE.md and findings §7 against the tests' output; the plan's §5a finding (110 s server cost) is stated as outside this unit - agree?

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll read the plan first, then check the diff against the server evaluator and try to break the numerical, caller, and performance assumptions. I’ll keep this read-only and finish with ranked findings and a verdict.

exec
/bin/zsh -lc 'cat docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
# DS+G page evaluator — a grid-aware mirror of the server's convolution (2026-09-22)

Branch `fix-dsg-page-evaluator` off main `b3c9e37` (A03 deployed). Owner's
brief: "Port the server's convolution to a grid-aware page evaluator.
Acceptance: the existing todo tests (parity sweep DS+G box at 1e-6, the
round-trip case), PLUS convergence demonstrated across the full β/m range the
optimiser can reach — including the corners that produced 1e52, not only the
Find Peaks box. Nothing de-listed, nothing changed in Find Peaks." Interim
red notice skipped unless a third Codex round or more than a day.

## 1. The defect (A03 sweep, section (D))

The page drew, integrated and exported a DS+G component with `laCasaXPS`, a
numerical quadrature whose step resolved the Lorentzian core (β/3) but not
the Gaussian kernel (σ = m/2.355). At β = 2, m = 0.05 the step was 0.67 eV
against σ = 0.021 eV and the curve was 1e52 × amplitude; across the fitted
box the page's area was 23–64 % of the server's. On the exact box Find Peaks
emits for a graphitic C 1s line (`autofit/regions/c1s.py`: β fixed at 0.05,
α 0–0.3, m in the graphitic FWHM range 0.4–1.2, polymers 0.8–1.8) the page's
curve was off by up to 13.7 % of amplitude and its area 5–21 % low for
α 0.15–0.3 (α = 0 was fine). Every A- and M-family candidate is built on
that slot, so an applied suggestion was drawn and quantified wrong; the
manual dropdown was the same path. 0 of the 530 committed peak records use
DS+G.

## 2. The fix

`dsgConvolved_array(beArr, center, alpha, beta, m)` in `templates/index.html`
is a literal mirror of `fitting._ds_g_dscore_gauss` for m ≥ 0.001 (the
m < 0.001 delta branch, `dsgDeltaKernel_array`, was already mirrored):

- α clipped to [0, 0.495], β ≥ 1e-6, m ≥ 0 — as the server;
- step = median |Δx| (numpy's median), ≥ 1e-6;
- padded grid ±max(10 m, 20 β) at that step, `np.linspace` semantics
  (always ascending, endpoint set exactly);
- DS core on the padded grid, non-finite → 0; half-cosine tapers over each
  pad (`np.linspace(0, π, n_pad)`);
- Gaussian kernel of σ = m/(2√(2 ln 2)) on the same step, centred at
  (n − 1)/2, normalised to unit sum over the FULL padded length;
- the server's circular convolution `irfft(rfft(ds)·rfft(ifftshift(k)))`
  evaluated DIRECTLY: out[i] = Σⱼ ds[j]·k[(i − j + ⌊n/2⌋) mod n], the sum
  restricted to |i − j| ≤ ⌈8σ/step⌉ + 1 (the kernel is e⁻³² ≈ 1e-14 of its
  peak beyond 8σ; the circular wrap reaches no other kernel mass);
- `np.interp` back to the data grid; normalised by the value interpolated AT
  the centre (fallbacks as the server's); non-finite → 0.

`evalPeakArray` routes every DS+G through it (the delta branch inside). The
scalar `evalPeak` DSG_LA branch keeps the name `laCasaXPS` but is now the
normalised DS core with m ignored — the same status as its LACX branch;
guard (C) of the parity harness proves no shipped caller reaches it. The
old quadrature is deleted, not tuned.

Cost: 0.3–1.1 ms per evaluation on a 241-point grid for Find Peaks-like
parameters, 5.5 ms at the box's far corner (β 2, m 4); a local fit of a
DS+G component converges in 69 ms.

## 3. Acceptance (measured)

| check | result |
|---|---|
| parity sweep (D), DS+G box α {0, 0.25, 0.49} × β {0.05, 0.7, 2} × m {0.001, 0.05, 0.4, 2, 4}, base grid | ≤ 3e-15 of amplitude (was 1e52 at β 2, m 0.05) — now a hard assertion |
| (D′) the same box on: 0.1 eV step; 0.02 eV step; descending grid; centre half a step off-grid; descending + 0.03 eV off-grid; a 30-point window narrower than the pad; a 0.0503 eV step | < 1e-6 on every combination — hard assertions |
| (A) DS+G at the base peak (was todo) | hard, passes |
| round trip page → server → page, DS+G (was todo), and DS+G m locked at 0.05 and at 4 (curve comparison was disabled) | hard, pass |
| (B) scalar vs array evaluator, DS+G | now `todo` like LACX: the convolution is a grid operation; guard (C) holds |
| Find Peaks box (β 0.05, α 0–0.3, m 0.4–1.8, 0.05 and 0.1 eV grids) | agrees with the server to 1e-6 (was 5–21 % low in area) |

Nothing changed on the server, in `autofit/`, in Find Peaks or in the
dropdown. Python suite untouched by this unit (no Python change); JS suite
and browser check in §5.

## 4. Sites

`laCasaXPS` (rewritten), `dsgConvolved_array` (new), `evalPeakArray`;
every function-extractor list that names the lineshape block
(`tests/js/lineshape_roundtrip.test.js`, `local_lm_descent.test.js`,
`scripts/local_server_gap.js`, `scripts/voigt_saved_vs_refit.js`) now lists
`dsgConvolved_array`; `tests/js/lineshape_parity.test.js` (A), (B), (D),
(D′); `tests/js/lineshape_roundtrip.test.js`; CLAUDE.md; findings §7.

## 5. Verification

- JS suite: 382 tests, 377 pass, 0 fail, 5 todo (`node --test tests/js/*.test.js`).
  The five: LACX m > 0 in (A), (B) and (D); (B) DS+G (scalar evaluator
  ignores m, by design); the LACX round trip.
- Python suite: untouched by this unit (no Python change); the A03 run on
  the same server code was 989 passed / 7 skipped.
- Browser check (`browser_check_dsg.py`, dev gunicorn :5151 with the
  production `--timeout 300`): the committed UCl4-graphite C1s Scan with its
  Graphite line switched to DS+G at Find Peaks' parameters (β 0.05, α 0.2,
  m 0.8), Run Fit (fitted α 0, β 0.053, m 0.62): the curve the page draws
  for it equals the server's fitted curve to 1.2e-12 of amplitude (the five
  GL lines 1e-13); its Results area equals the server curve's to 0.0000 %;
  the chart dataset is the drawn curve; a `ds_g` Find Peaks candidate maps
  to DSG_LA with its α, β, m; no page errors.

## 5a. Finding on the way: a DS+G Run Fit costs the server ~110 s

Not this unit's change (fitting.py is untouched) and present on main
today. On the committed UCl4-graphite C1s Scan (191 points, 0.1 eV) with
the Graphite line switched to DS+G at Find Peaks' parameters (β 0.05,
α 0.2, m 0.8) and five GL lines: the plain fit takes 0.4 s (640 DS+G
evaluations, 0.3 ms each), but each of the page's `n_perturb: 3` restarts
takes ~18 s (28,821 evaluations — the perturbed descent runs to the
optimiser's evaluation budget), and with `n_starts: 3` the request takes
110 s. Production's gunicorn `--timeout 300` covers it; a dev server on the
30 s default returns a worker timeout and the page reports "Fit failed".
Every A- and M-family Find Peaks candidate applied and re-fitted pays this.
Logged for its own look (why the perturbed DS+G descent does not converge;
whether the restarts should be skipped or capped for this shape).

## 6. Codex rounds

(filled in as they run)

exec
/bin/zsh -lc "git diff --stat main..HEAD; rg --files -g AGENTS.md -g '*extract*' -g '*parity*' -g '*roundtrip*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-16OHTCGk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-KN6z2PVq' (errno=Operation not permitted)
 CLAUDE.md                                          |  17 ++-
 docs/findings/2026-09-fit-determinacy.md           |   9 +-
 .../plans/2026-09-22-dsg-page-evaluator.md         | 114 ++++++++++++++++
 scripts/local_server_gap.js                        |   2 +-
 scripts/voigt_saved_vs_refit.js                    |   2 +-
 templates/index.html                               | 144 +++++++++++++++------
 tests/js/lineshape_parity.test.js                  |  67 +++++++---
 tests/js/lineshape_roundtrip.test.js               |  19 ++-
 tests/js/local_lm_descent.test.js                  |   2 +-
 9 files changed, 294 insertions(+), 82 deletions(-)
autofit/parity.py
docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md
tests/test_browser_overlay_zip_roundtrip.py
tests/test_legacy_parity.py
tests/js/local_lm_server_parity_backend.py
tests/js/shape_switch_roundtrip.test.js
tests/autofit/test_browser_schema_roundtrip.py
tests/autofit/test_u4f_parity_gate.py
tests/autofit/test_u4f_parity_battery.py
tests/autofit/test_c1s_parity_gate.py
tests/js/lineshape_roundtrip_backend.py
tests/js/lineshape_parity_backend.py
tests/autofit/test_b1s_cl2p_parity_gates.py
tests/js/lineshape_roundtrip.test.js
tests/autofit/test_c1s_parity_battery.py
tests/js/lineshape_parity.test.js

exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html tests/js/lineshape_parity.test.js tests/js/lineshape_roundtrip.test.js tests/js/local_lm_descent.test.js scripts/local_server_gap.js scripts/voigt_saved_vs_refit.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-LD9YjTrU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ugzh0yf5' (errno=Operation not permitted)
diff --git a/scripts/local_server_gap.js b/scripts/local_server_gap.js
index 370c215..b2bc870 100644
--- a/scripts/local_server_gap.js
+++ b/scripts/local_server_gap.js
@@ -29,7 +29,7 @@ function extractFn(name) {
   throw new Error('unbalanced ' + name);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
diff --git a/scripts/voigt_saved_vs_refit.js b/scripts/voigt_saved_vs_refit.js
index db893cb..8c0c205 100644
--- a/scripts/voigt_saved_vs_refit.js
+++ b/scripts/voigt_saved_vs_refit.js
@@ -29,7 +29,7 @@ function extractFn(name) {
   throw new Error('unbalanced ' + name);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS',
-  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
+  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'dsgConvolved_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
 const state = { peaks: [] };
 const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams, _bgWindowIndices };')(state);
 const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
diff --git a/templates/index.html b/templates/index.html
index f272259..690b848 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4043,45 +4043,16 @@ function laCasaXPSCore(eps, alpha, beta) {
 }
 
 function laCasaXPS(x, center, alpha, beta, mGauss) {
-  // LA(α, β, m) — CasaXPS convention
-  // α: dimensionless asymmetry index (0–0.5) — tail toward HIGHER binding energy
-  // β: Lorentzian half-width (eV)
-  // m: Gaussian FWHM (eV) convolved with the DS core
-  // Returns value normalised to 1 at x = center.
-  //
-  // m below the same 0.001 eV threshold the backend uses
-  // (fitting.py _ds_g_dscore_gauss) means a delta kernel: skip the
-  // convolution and return the normalised DS core directly. The quadrature
-  // below degenerates as sigma → 0 (its Gaussian weights divide by
-  // 2·sigma², collapsing the curve to ~0), so this branch is a correctness
-  // fix, not just a fast path. Pinned by tests/js/lineshape_parity.test.js.
-  if (mGauss < 0.001) {
-    const peakVal = laCasaXPSCore(0, alpha, beta);
-    if (!(peakVal > 0)) return 0;
-    return laCasaXPSCore(x - center, alpha, beta) / peakVal;
-  }
-  const sigma = mGauss / (2.0 * Math.sqrt(2.0 * Math.LN2));
-  // Wide window: DS power-law tail decays slowly (~1/ε^1.85), need large range.
-  const halfRange = 6 * sigma + 50 * beta;
-  // Scale N so dEps ≤ β/3 (resolves the Lorentzian core) with floor of 300
-  const N = Math.max(300, Math.ceil(2 * halfRange / (beta / 3)));
-  const dEps = 2 * halfRange / N;
-  // Cosine taper: smoothly fade the DS core to zero over the outer 40% of
-  // the window, eliminating cliff artifacts from the power-law tail cutoff.
-  const taperStart = 0.6 * halfRange;
-  const u0 = x - center;
-  let val = 0, norm = 0;
-  for (let k = 0; k <= N; k++) {
-    const eps = -halfRange + k * dEps;
-    const absEps = Math.abs(eps);
-    const taper = absEps > taperStart
-      ? 0.5 * (1 + Math.cos(Math.PI * (absEps - taperStart) / (halfRange - taperStart)))
-      : 1.0;
-    const ds = laCasaXPSCore(eps, alpha, beta) * taper;
-    val  += ds * Math.exp(-((u0 - eps) * (u0 - eps)) / (2 * sigma * sigma));
-    norm += ds * Math.exp(-(eps * eps)                / (2 * sigma * sigma));
-  }
-  return norm > 0 ? val / norm : 0;
+  // Per-point DS+G fallback for the scalar evaluator's DSG_LA branch: the
+  // NORMALISED DS core, m IGNORED — exactly as its LACX branch ignores m. The Gaussian
+  // convolution is a GRID operation and lives in dsgConvolved_array (called
+  // through evalPeakArray, the only shipped path — parity guard (C)). Until
+  // 2026-09-22 this function was a numerical quadrature whose step resolved
+  // the Lorentzian core (β/3) but not the Gaussian kernel, and was wrong by
+  // up to 1e52 × amplitude across the fitted β/m range (A03 sweep).
+  const peakVal = laCasaXPSCore(0, alpha, beta);
+  if (!(peakVal > 0)) return 0;
+  return laCasaXPSCore(x - center, alpha, beta) / peakVal;
 }
 
 // True LA(α, β, m) [CasaXPS] — piecewise-asymmetric Lorentzian + integer-kernel Gauss conv.
@@ -4224,10 +4195,97 @@ function dsgDeltaKernel_array(beArr, center, alpha, beta) {
   return core;
 }
 
+// DS+G with Gaussian broadening, a literal mirror of the server's
+// fitting._ds_g_dscore_gauss (m ≥ 0.001; below that the delta branch above):
+// the DS core on a grid PADDED by ±max(10 m, 20 β) at the data step
+// (np.linspace semantics, always ascending), a half-cosine taper over each
+// pad, a Gaussian kernel of σ = m / 2√(2 ln 2) on the same step normalised to
+// unit sum over the FULL padded length, circular convolution
+// (irfft(rfft(ds)·rfft(ifftshift(kernel))) on the server), linear
+// interpolation back to the data grid, and normalisation by the value
+// interpolated AT the centre. The convolution is evaluated directly rather
+// than by FFT: the kernel is negligible beyond 8 σ (e⁻³² ≈ 1e-14 of its
+// peak), so the sum is restricted to that window — identical to the
+// server's circular product to far below the 1e-6-of-amplitude parity
+// tolerance (tests/js/lineshape_parity.test.js (D), the full β/m box incl.
+// the corners that made the old quadrature explode). Returns the curve
+// normalised to 1 at the centre; the caller applies the amplitude.
+function dsgConvolved_array(beArr, center, alpha, beta, mGauss) {
+  const N = beArr.length;
+  const a = _dsgAlpha(alpha);
+  const b = Math.max(beta, 1e-6);
+  const m = Math.max(mGauss, 0);
+  if (m < 0.001) return dsgDeltaKernel_array(beArr, center, a, b);
+  // step = median |Δx| (numpy: the mean of the two middle values for an even count)
+  let step = 0.05;
+  if (N > 1) {
+    const d = new Array(N - 1);
+    for (let i = 1; i < N; i++) d[i - 1] = Math.abs(beArr[i] - beArr[i - 1]);
+    d.sort((u, v) => u - v);
+    const n = d.length;
+    step = n % 2 ? d[(n - 1) / 2] : 0.5 * (d[n / 2 - 1] + d[n / 2]);
+  }
+  step = Math.max(step, 1e-6);
+  const padEv = Math.max(10 * m, 20 * b);
+  const nPad = Math.max(Math.ceil(padEv / step), 1);
+  const asc = N > 1 ? beArr[N - 1] > beArr[0] : true;
+  const lo = (asc ? beArr[0] : beArr[N - 1]) - nPad * step;
+  const hi = (asc ? beArr[N - 1] : beArr[0]) + nPad * step;
+  const nTot = N + 2 * nPad;
+  const xp = new Float64Array(nTot);
+  const dxLin = (hi - lo) / (nTot - 1);
+  for (let i = 0; i < nTot; i++) xp[i] = lo + i * dxLin;
+  xp[nTot - 1] = hi;                                   // np.linspace sets the endpoint exactly
+  const ds = new Float64Array(nTot);
+  for (let i = 0; i < nTot; i++) { const v = laCasaXPSCore(xp[i] - center, a, b); ds[i] = Number.isFinite(v) ? v : 0; }
+  if (nPad > 1) {
+    for (let k = 0; k < nPad; k++) {
+      const th = Math.PI * k / (nPad - 1);                // np.linspace(0, π, nPad)[k]
+      ds[k] *= 0.5 * (1 - Math.cos(th));
+      ds[nTot - nPad + k] *= 0.5 * (1 + Math.cos(th));
+    }
+  }
+  const sigma = m / (2 * Math.sqrt(2 * Math.LN2));
+  const kHalf = (nTot - 1) / 2;
+  const kernel = new Float64Array(nTot);
+  let ksum = 0;
+  for (let t = 0; t < nTot; t++) { const kg = (t - kHalf) * step; kernel[t] = Math.exp(-0.5 * (kg / sigma) * (kg / sigma)); ksum += kernel[t]; }
+  for (let t = 0; t < nTot; t++) kernel[t] /= ksum;
+  const fl = Math.floor(nTot / 2);                        // np.fft.ifftshift's shift
+  const W = Math.ceil(8 * sigma / step) + 1;              // the kernel's support in samples
+  const conv = new Float64Array(nTot);
+  for (let i = 0; i < nTot; i++) {
+    let acc = 0;
+    const j0 = Math.max(0, i - W), j1 = Math.min(nTot - 1, i + W);
+    for (let j = j0; j <= j1; j++) {
+      let t = (i - j + fl) % nTot; if (t < 0) t += nTot;
+      acc += ds[j] * kernel[t];
+    }
+    conv[i] = acc;
+  }
+  // np.interp(query, xp, conv): xp ascending; clamped outside; linear inside
+  const interp = q => {
+    if (q <= xp[0]) return conv[0];
+    if (q >= xp[nTot - 1]) return conv[nTot - 1];
+    let lo2 = 0, hi2 = nTot - 1;
+    while (hi2 - lo2 > 1) { const mid = (lo2 + hi2) >> 1; if (xp[mid] <= q) lo2 = mid; else hi2 = mid; }
+    const x0 = xp[lo2], x1 = xp[hi2];
+    const tt = x1 !== x0 ? (q - x0) / (x1 - x0) : 0;
+    return conv[lo2] + tt * (conv[hi2] - conv[lo2]);
+  };
+  const out = new Array(N);
+  for (let i = 0; i < N; i++) out[i] = interp(beArr[i]);
+  let peakVal = interp(center);
+  if (!(peakVal > 0)) { let mx = 0; for (let i = 0; i < N; i++) mx = Math.max(mx, Math.abs(out[i])); peakVal = mx; }
+  if (!(peakVal > 0)) return new Array(N).fill(0);
+  for (let i = 0; i < N; i++) { const v = out[i] / peakVal; out[i] = Number.isFinite(v) ? v : 0; }
+  return out;
+}
+
 // Compute per-peak intensities across an array of BE values. Special-cases
 // LACX with non-zero m so the Gaussian convolution sees the whole grid, and
-// DSG_LA below the 0.001 delta-kernel threshold so the normalisation sees
-// the whole grid (see dsgDeltaKernel_array above).
+// DSG_LA (every m: the delta branch below 0.001, the convolution above) so
+// the padding, kernel and normalisation see the whole grid.
 function evalPeakArray(beArr, p) {
   if (p.shape === 'LACX' && Math.round(p.caM || 0) > 0) {
     const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
@@ -4236,11 +4294,11 @@ function evalPeakArray(beArr, p) {
     for (let i = 0; i < beArr.length; i++) out[i] = amp * yArr[i];
     return out;
   }
-  if (p.shape === 'DSG_LA' && (p.laM || 0) < 0.001) {
+  if (p.shape === 'DSG_LA') {
     // (p.laM || 0): negative laM matches the backend's clamp-to-0-then-delta
     // path; NaN/undefined coerce to 0 → delta, which peakToBackendSpec's
     // non-finite→default sanitisation makes unreachable in fit flows.
-    const yArr = dsgDeltaKernel_array(beArr, p.center, _dsgAlpha(p.laAlpha), p.laBeta);
+    const yArr = dsgConvolved_array(beArr, p.center, p.laAlpha, p.laBeta, p.laM || 0);
     const amp = p.amplitude;
     return yArr.map(v => amp * v);
   }
diff --git a/tests/js/lineshape_parity.test.js b/tests/js/lineshape_parity.test.js
index 260f3c1..93b5e78 100644
--- a/tests/js/lineshape_parity.test.js
+++ b/tests/js/lineshape_parity.test.js
@@ -156,21 +156,17 @@ for (const shape of ['Gaussian', 'Lorentzian', 'GL', 'Voigt', 'DS', 'asym-GL'])
 //   consistent with backend continuous-m + ceil(3.5*sigma) kernel vs
 //   frontend rounded-m + 2m+1 kernel. Small, monotonic, unit-2 material.
 //
-//   DSG_LA: error is HIGHEST at m=0 (101.8% at laAlpha=0.18/laBeta=0.7 —
-//   the frontend curve is ~zero everywhere) and DECREASES as m grows —
-//   the OPPOSITE shape from LACX. Root cause is NOT a kernel-discretization
-//   gap: JS laCasaXPS() (templates/index.html) sets
-//   `sigma = mGauss / (2*sqrt(2*ln2))`, so mGauss -> 0 drives sigma -> 0 and
-//   its Gaussian-weighted quadrature divides by `2*sigma*sigma` — a literal
-//   division-by-zero/degenerate-weight bug, not a discretization mismatch.
-//   NARROWER than the above sweep alone suggests, though: measured against
-//   the SCHEMA DEFAULT (laM=0.4, laAlpha=0.10, laBeta=0.3, 2026-08-31):
-//   laM=0 -> 100%, 0.1 -> 11.8%, 0.2 -> 0.05%, 0.4 (DEFAULT) -> 0.02%,
-//   0.6+ -> 0%. The shipped default is NOT affected; only laM at or very
-//   near zero (roughly <=0.1) is, and when it fires the peak visibly
-//   vanishes/flattens on screen — loud, not a quiet export-only drift like
-//   LACX/asym-GL were. Its own unit, normal priority — do not fold it into
-//   the LACX kernel-construction fix, and do not hold anything for it.
+//   DSG_LA: FIXED 2026-09-22 (unit fix-dsg-page-evaluator). The page's
+//   evaluator used to be a numerical quadrature (laCasaXPS) whose step
+//   resolved the Lorentzian core (β/3) but not the Gaussian kernel, so it
+//   was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and by 4-14 % of
+//   amplitude on the very box Find Peaks emits for a graphitic C 1s line
+//   (β 0.05, α 0-0.3, m 0.4-1.8) — the A03 sweep, section (D) below. The
+//   m < 0.001 delta branch (dsgDeltaKernel_array) had been mirrored in
+//   2026-08; dsgConvolved_array now mirrors the server's padded-grid
+//   convolution for every m (≤ 3e-15 of amplitude across the fitted box,
+//   every grid step, orientation and off-grid centre tested below).
+//
 test('(A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)', { todo: 'unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)' }, () => {
   const p = basePeak('LACX');
   const x = grid(p.center);
@@ -194,7 +190,7 @@ test('(A) frontend vs backend parity: LACX at m=0 (no convolution)', () => {
     `LACX at m=0: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
 });
 
-test('(A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed', { todo: 'DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above' }, () => {
+test('(A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)', () => {
   const p = basePeak('DSG_LA');
   const x = grid(p.center);
   const jsY = evalPeakArray(x, p);
@@ -263,7 +259,8 @@ test('(A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid c
 // this mechanism for real callers.
 const ALL_SHAPES = ['Gaussian', 'Lorentzian', 'Voigt', 'GL', 'asym-GL', 'DS', 'DSG_LA', 'LACX'];
 for (const shape of ALL_SHAPES) {
-  const opts = shape === 'LACX' ? { todo: 'evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header' } : undefined;
+  const opts = shape === 'LACX' ? { todo: 'evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header' }
+    : shape === 'DSG_LA' ? { todo: 'evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)' } : undefined;
   test(`(B) evalPeak vs evalPeakArray agree pointwise: ${shape}`, opts, () => {
     const p = basePeak(shape);
     const x = grid(p.center);
@@ -346,9 +343,11 @@ const SWEEP = {
   'DS':         { dsAlpha: [0, 0.25, 0.5], dsGamma: [0, 1, 5], fwhm: FWHM_RANGE },
   'DSG_LA (delta kernel)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0, 0.0009] },
   'LACX (m = 0)': { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0], fwhm: FWHM_RANGE },
+  // the full β/m box the optimiser can reach, incl. the corner that made the
+  // old quadrature 1e52 × amplitude (β 2, m 0.05) and the delta threshold
+  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] },
 };
 const SWEEP_KNOWN_GAP = {
-  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.05, 0.4, 2, 4] },
   'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
 };
 function sweepShape(label) { return label.split(' ')[0]; }
@@ -393,3 +392,35 @@ for (const [label, ranges] of Object.entries(SWEEP_KNOWN_GAP)) {
       `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
   });
 }
+
+// ── (D′) DS+G convergence beyond the base grid (unit fix-dsg-page-evaluator) ──
+// The convolution is a GRID operation: the server pads at the data step,
+// builds its kernel on it and normalises at the interpolated centre. So the
+// box is swept again on a coarser and a finer step, a DESCENDING grid (real
+// acquisitions), a centre half a step off-grid, a short window, and a
+// window narrower than the pad — every case at the 1e-6 tolerance.
+function gridOf(center, step, n, { descending = false, offset = 0 } = {}) {
+  const x = [];
+  for (let i = 0; i < n; i++) x.push(center - (step * n) / 2 + step * i + offset);
+  return descending ? x.reverse() : x;
+}
+const DSG_GRID_CASES = [
+  { label: 'step 0.1 eV, 120 pts', step: 0.1, n: 120 },
+  { label: 'step 0.02 eV, 500 pts', step: 0.02, n: 500 },
+  { label: 'step 0.05 eV, descending', step: 0.05, n: 200, descending: true },
+  { label: 'step 0.05 eV, centre half a step off-grid', step: 0.05, n: 200, offset: 0.025 },
+  { label: 'step 0.1 eV, descending, centre 0.03 eV off-grid', step: 0.1, n: 120, descending: true, offset: 0.03 },
+  { label: 'short window: 30 pts at 0.1 eV (narrower than the pad)', step: 0.1, n: 30 },
+  { label: 'irregular-ish step 0.0503 eV (median step), 181 pts', step: 0.0503, n: 181 },
+];
+const DSG_BOX = { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] };
+for (const g of DSG_GRID_CASES) {
+  test(`(D′) DS+G convolution converges on another grid: ${g.label}`, () => {
+    const cases = combos(DSG_BOX).map(c => ({ c, p: { ...basePeak('DSG_LA'), ...c } }));
+    const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: gridOf(k.p.center, g.step, g.n, g) }; });
+    const beYs = backendEvalMany(specs);
+    const worst = cases.map((k, i) => ({ c: k.c, rel: maxRelDiff(evalPeakArray(specs[i].x, k.p), beYs[i], k.p.amplitude) })).sort((a, b) => b.rel - a.rel);
+    assert.ok(worst[0].rel < TIGHT_TOL,
+      `${g.label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} combinations diverge; worst ${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
+  });
+}
diff --git a/tests/js/lineshape_roundtrip.test.js b/tests/js/lineshape_roundtrip.test.js
index b0153d6..ffbfa9f 100644
--- a/tests/js/lineshape_roundtrip.test.js
+++ b/tests/js/lineshape_roundtrip.test.js
@@ -15,10 +15,10 @@
 // page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
 // server FITTED (individual_peaks[].y).
 //
-// Two shapes carry a known drawn-vs-fitted gap and are marked todo with the
-// unit that owns it: LACX (the page sends m free and draws it ROUNDED —
-// the caM clamp unit) and DSG_LA (the page's quadrature — see the parity
-// harness's section (D)).
+// One shape carries a known drawn-vs-fitted gap and is marked todo with the
+// unit that owns it: LACX (the page sends m free and draws it ROUNDED — the
+// caM clamp unit). DSG_LA was the other until 2026-09-22 (the page's
+// quadrature; now dsgConvolved_array mirrors the server).
 const { test } = require('node:test');
 const assert = require('node:assert');
 const { execFileSync } = require('node:child_process');
@@ -41,7 +41,7 @@ function extractFn(name) {
   assert.fail(`unbalanced braces extracting ${name}`);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'dsgConvolved_array',
   'evalPeakArray', 'getPeak', 'peakToBackendSpec', '_applyBackendParams'];
 const state = { peaks: [] };
 const env = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, peakToBackendSpec, _applyBackendParams };')(state);
@@ -92,7 +92,6 @@ const CASES = {
 };
 const TIGHT_TOL = 1e-6;      // of amplitude; both curves are the same closed form on the same grid
 const KNOWN_GAP = {
-  'DSG_LA': 'DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit',
   'LACX':   'LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit',
 };
 
@@ -190,10 +189,10 @@ const LOCKED_AT_BOUNDS = [
   { label: 'LA beta 5 locked (m = 0)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 5, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 5, m: 0 } },
   // the page's input allows α = 0.5; the server's evaluator clips α to 0.495 and so, since round 3, does the page's
   { label: 'DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)', truth: { shape: 'DSG_LA', laAlpha: 0.5, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0.5, m_gauss: 0 } },
-  // the convolved shapes' m locks at m > 0: request and server-held value are pinned; the drawn-vs-fitted
-  // comparison sits under the evaluator gaps marked todo above (curve: false)
-  { label: 'DS+G m 0.05 locked (request and hold only)', truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.05, fixLaM: true }, held: { m_gauss: 0.05 }, curve: false },
-  { label: 'DS+G m 4 locked (request and hold only)',    truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 4, fixLaM: true }, held: { m_gauss: 4 }, curve: false },
+  // LA's m lock at m > 0: request and server-held value are pinned; the drawn-vs-fitted
+  // comparison sits under the caM evaluator gap marked todo above (curve: false)
+  { label: 'DS+G m 0.05 locked', truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.05, fixLaM: true }, held: { m_gauss: 0.05 } },
+  { label: 'DS+G m 4 locked',    truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 4, fixLaM: true }, held: { m_gauss: 4 } },
   { label: 'LA m 499 locked (request and hold only)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 }, curve: false },
 ];
 for (const c of LOCKED_AT_BOUNDS) {
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 5c42284..1bbbd13 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -35,7 +35,7 @@ function extractFn(name) {
 }
 
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',

exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g 'package.json' -g '*browser_check_dsg*'; ls -d .venv venv 2>/dev/null; rg -n 'laBeta|laM|dsgConvolved_array|evalPeak\\(' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
4048:  // convolution is a GRID operation and lives in dsgConvolved_array (called
4119:function evalPeak(x, p) {
4139:    y = laCasaXPS(x, center, _dsgAlpha(p.laAlpha), p.laBeta, p.laM);
4213:function dsgConvolved_array(beArr, center, alpha, beta, mGauss) {
4298:    // (p.laM || 0): negative laM matches the backend's clamp-to-0-then-delta
4301:    const yArr = dsgConvolved_array(beArr, p.center, p.laAlpha, p.laBeta, p.laM || 0);
4305:  return beArr.map(x => evalPeak(x, p));
5098:    laBeta: 0.3,
5099:    laM: 0.4,
5136:// (that silently corrupted fitted values, e.g. DS+G's laM/laBeta on a
5155:  'DSG_LA':     { laAlpha: 0.10, fixLaAlpha: false, laBeta: 0.3, fixLaBeta: false, laM: 0.4, fixLaM: false },
5161:// width is the Gaussian FWHM `laM` (DS+G's `fwhm` field is display-only /
5166:function _widthField(shape) { return shape === 'DSG_LA' ? 'laM' : 'fwhm'; }
5174:// top-level fields), and the effective WIDTH (mapped across the laM↔fwhm
5182://      carries (e.g. DS+G's laBeta) survives the excursion through B and is
5185://      (observed: laBeta 0.05 → 0.30, laM 3.11 → 0.40 on DS+G → GL → DS+G).
5187://      laM↔fwhm boundary. The map is the identity in eV, so it is invertible
5192:  // 1. carry the effective width (value + lock) across the laM↔fwhm boundary
5829:  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
6154:          <input type="number" value="${p.laBeta.toFixed(3)}" step="0.01" min="0.05" max="2.0"
6155:            oninput="updatePeakParam(${p.id},'laBeta',parseFloat(this.value))">
6162:        <input type="number" value="${p.laM.toFixed(3)}" step="0.01" min="0.05" max="4.0"
6163:          oninput="updatePeakParam(${p.id},'laM',parseFloat(this.value))">
6327:    spec.beta    = Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3;
6328:    spec.m_gauss = Number.isFinite(p.laM)     ? p.laM     : 0.4;
6370:  if (par.beta    && p.shape === 'DSG_LA' && !p.fixLaBeta)  p.laBeta  = par.beta.value;
6371:  if (par.m_gauss && p.shape === 'DSG_LA' && !p.fixLaM)     p.laM     = par.m_gauss.value;
7439:  'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM', 'linked', 'linkOffset', 'linkRatio', '_afAsymMin', '_afAsymMax',
8033:        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
8034:        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
8058:    if (param === 'laBeta')       return Math.max(0.05, Math.min(2.0, v));
8059:    if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
8066:    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];
11141:    case 'DSG_LA':  return { gl: '',            alpha: p.laAlpha ?? '', beta: p.laBeta ?? '', m: p.laM ?? '' };
15747:      o.laAlpha = p.alpha ?? 0.1; o.laBeta = p.beta ?? 0.3; o.laM = p.m_gauss ?? p.fwhm ?? 1; break;

exec
/bin/zsh -lc "sed -n '130,330p' fitting.py; cat tests/js/lineshape_parity_backend.py; cat tests/js/lineshape_roundtrip_backend.py; git diff main..HEAD -- CLAUDE.md docs/findings/2026-09-fit-determinacy.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
    if abs(cos0) < 1e-12:
        cos0 = 1e-12
    norm = gamma ** (1.0 - alpha) / cos0
    # dx = center − x  →  positive on LOW-BE side, negative on HIGH-BE side.
    # The arctan and power-law terms produce a tail toward HIGH-BE (dx < 0).
    dx = center - x
    phase = np.pi * alpha / 2.0 + (1.0 - alpha) * np.arctan(dx / gamma)
    denom = (dx ** 2 + gamma ** 2) ** ((1.0 - alpha) / 2.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = amplitude * norm * np.cos(phase) / denom
    # Exponential envelope to gently limit the HIGH-BE tail extent.
    # dx = center - x: negative on the HIGH-BE side (x > center).
    # We want: decay = 1 at center, tapering toward zero far into the tail.
    # Use |dx| on the high-BE side only: exp(-gamma_asym * max(x - center, 0))
    if gamma_asym > 0.0:
        tail_decay = np.exp(-gamma_asym * np.maximum(x - center, 0.0))
        result = result * tail_decay
    result = np.where(np.isfinite(result), result, 0.0)
    return result


def _ds_g_dscore_gauss(
    x: np.ndarray,
    amplitude: float,
    center: float,
    alpha: float,    # CasaXPS: dimensionless asymmetry index, 0 ≤ α < 0.5
    beta: float,     # CasaXPS: Lorentzian half-width (eV)
    m_gauss: float,  # CasaXPS: Gaussian FWHM (eV) for convolution
) -> np.ndarray:
    """
    DS+G lineshape (formerly mislabeled "LA(α,β,m) [CasaXPS]") —
    Doniach-Šunjić asymmetric core convolved analytically with a Gaussian
    instrument-broadening kernel. NOT to be confused with the true CasaXPS
    LA shape (see _la_casaxps_true), which uses a piecewise-asymmetric
    Lorentzian with point-domain Gaussian convolution.

    The DS core with asymmetry index α and Lorentzian half-width β is convolved
    with a Gaussian of FWHM m for instrument broadening.

    Tail direction: eps = x − center > 0 → HIGHER binding energy (physically
    correct: low-energy electron-hole pair excitations produce intensity on the
    high-BE side only).

    Parameters
    ----------
    alpha   : dimensionless asymmetry index, 0 ≤ α < 0.5
              (0 = symmetric Lorentzian, ~0.1–0.3 for metallic systems)
    beta    : Lorentzian half-width at half-maximum (eV); controls core width
    m_gauss : Gaussian FWHM (eV) for instrument/phonon broadening (0 = none)

    Fixes (v2)
    ----------
    1. Convolution uses a padded grid (±10·m on each side) with cosine taper
       to eliminate cliff artifacts at array boundaries.
    2. Explicit FFT convolution with a properly normalised Gaussian kernel,
       so DS tail direction is preserved regardless of m value.
    """
    alpha   = float(np.clip(alpha, 0.0, 0.495))
    beta    = max(float(beta),    1e-6)
    m_gauss = max(float(m_gauss), 0.0)

    # ── DS core evaluator (independent of m_gauss) ───────────────────────────
    #
    # eps = x − center: positive on HIGH-BE side (where tail belongs)
    # DS formula:  cos(πα/2 − (1−α)·arctan2(ε, β)) / (ε² + β²)^((1−α)/2)
    #
    # Sign convention proof:
    #   At ε >> β (high BE):  arctan2(ε, β) → +π/2
    #     phase → πα/2 − (1−α)·π/2 → −π(1−2α)/2  (negative for α < 0.5)
    #     cos(phase) > 0, and denominator grows as |ε|^(1−α)
    #     → slow power-law decay toward HIGH BE  ✓
    #   At ε << −β (low BE): arctan2(ε, β) → −π/2
    #     phase → πα/2 + (1−α)·π/2 → π/2  (for small α)
    #     cos(phase) → 0, faster falloff
    #     → steeper decay toward LOW BE  ✓

    def _ds_core(xgrid):
        """Evaluate DS kernel on arbitrary grid. Independent of m_gauss."""
        eps = xgrid - center
        r2 = eps ** 2 + beta ** 2
        r2 = np.maximum(r2, 1e-30)
        rPow = r2 ** ((1.0 - alpha) / 2.0)
        phase = np.pi * alpha / 2.0 - (1.0 - alpha) * np.arctan2(eps, beta)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            core = np.cos(phase) / rPow
        core = np.where(np.isfinite(core), core, 0.0)
        return core

    # ── No Gaussian broadening — just return normalised DS core ──────────────
    if m_gauss < 0.001:
        ds_core = _ds_core(x)
        peak_val = float(np.interp(center, x if x[-1] > x[0] else x[::-1],
                                   ds_core if x[-1] > x[0] else ds_core[::-1]))
        if peak_val <= 0.0:
            peak_val = np.max(np.abs(ds_core))
        if peak_val <= 0.0:
            return np.zeros_like(x)
        return amplitude * ds_core / peak_val

    # ── Build padded grid for convolution ─────────────────────────────────────
    # Pad by ±10·m_gauss (≈ ±4.25σ) to avoid truncation artifacts.
    # The DS power-law tail decays as |ε|^(α−1), which is slow for small α,
    # so generous padding is essential.
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 0.05
    step = max(step, 1e-6)

    pad_ev = max(10.0 * m_gauss, 20.0 * beta)  # eV of padding on each side
    n_pad = int(np.ceil(pad_ev / step))
    n_pad = max(n_pad, 1)

    # Determine sort direction of input x
    ascending = (x[-1] > x[0]) if len(x) > 1 else True

    # Create padded energy grid extending beyond the data range
    if ascending:
        x_pad_lo = x[0] - n_pad * step
        x_pad_hi = x[-1] + n_pad * step
    else:
        x_pad_lo = x[-1] - n_pad * step
        x_pad_hi = x[0] + n_pad * step

    n_total = len(x) + 2 * n_pad
    x_padded = np.linspace(x_pad_lo, x_pad_hi, n_total)  # always ascending

    # Evaluate DS core on padded grid
    ds_padded = _ds_core(x_padded)

    # ── Cosine taper on pad regions ───────────────────────────────────────────
    # Smoothly ramp to zero at the array edges to kill any residual signal
    # that would cause Gibbs-like ringing in FFT convolution.
    taper = np.ones(n_total)
    if n_pad > 1:
        # Left taper: 0→1 over n_pad points (half cosine)
        taper[:n_pad] = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, n_pad)))
        # Right taper: 1→0 over n_pad points
        taper[-n_pad:] = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, n_pad)))
    ds_padded *= taper

    # ── FFT convolution with Gaussian kernel ──────────────────────────────────
    # σ_eV = m_gauss / (2√(2·ln2))  (convert FWHM to sigma)
    sigma_ev = m_gauss / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    # Kernel grid centred at zero, same length as padded array (for FFT)
    n_k = len(x_padded)
    k_half = (n_k - 1) / 2.0
    k_grid = (np.arange(n_k) - k_half) * step  # eV relative to centre
    gauss_kernel = np.exp(-0.5 * (k_grid / sigma_ev) ** 2)
    gauss_kernel /= gauss_kernel.sum()  # normalise to unit area

    # FFT convolution (circular, but padding makes edge effects negligible)
    ft_ds = np.fft.rfft(ds_padded)
    ft_gk = np.fft.rfft(np.fft.ifftshift(gauss_kernel))
    ds_conv = np.fft.irfft(ft_ds * ft_gk, n=n_total)

    # ── Interpolate back to original x grid ───────────────────────────────────
    # x_padded is always ascending; np.interp handles arbitrary query points.
    result = np.interp(x, x_padded, ds_conv)

    # ── Normalise so value at x = center equals amplitude ─────────────────────
    # Interpolate at exact center rather than nearest grid point to avoid
    # normalization error when center falls between data points.
    peak_val = float(np.interp(center, x_padded, ds_conv))
    if peak_val <= 0.0:
        peak_val = np.max(np.abs(result))
    if peak_val <= 0.0:
        return np.zeros_like(x)

    result = amplitude * result / peak_val

    # Final safety: suppress any NaN/Inf
    return np.where(np.isfinite(result), result, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Background functions
# ─────────────────────────────────────────────────────────────────────────────

def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
    n = len(y)
    if n_avg <= 1 or n < 4:
        return y.copy()
    cap = min(n_avg, n // 4)
    if cap < 1:
        return y.copy()
    out = y.copy()
    out[:cap] = np.mean(y[:cap])
    out[-cap:] = np.mean(y[-cap:])
    return out


def shirley_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9rnXAKgB' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-SFMbWUcW' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index e54491f..46fbd96 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -132,13 +132,16 @@ to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
 `_make_peak_params._set` now widens a limit to a held value), and the
 server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
 held parameter is held at its value; what the page draws is what the
-server fitted. Tracked gaps, `todo` in both files: LACX with m > 0 (the page draws
+server fitted. Tracked gap, `todo` in both files: LACX with m > 0 (the page draws
 a rounded integer kernel; the server fits m continuously — the `caM` clamp
-unit) and DS+G with m ≥ 0.05 (the page's quadrature `laCasaXPS` sizes its
-step to the Lorentzian core, not the Gaussian kernel, and is wrong by up to
-80 % of amplitude across the fitted β/m range — 1e52 × at β = 2, m = 0.05;
-0 of the 530 peak records in the seven committed projects use DS+G; its own unit). Details in
-`docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+unit). DS+G was the other gap until 2026-09-22 (the page's quadrature
+`laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
+and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
+in area on the very box Find Peaks emits for a graphitic C 1s line);
+`dsgConvolved_array` now mirrors the server's padded-grid convolution for
+every m, pinned at 1e-6 across the full β/m box on seven grids
+(`docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md`). Details of
+A03 in `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
 
 ---
 
@@ -234,7 +237,7 @@ them to (use grep to find current line numbers — the file evolves):
 - `peakToBackendSpec` LACX branch
 - `applyBackendResult` LACX backend-param mapping
 - `runFit` JS LM free-params block + per-param clamps + linked-peak sync
-- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`)
+- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`; DS+G's grid-aware twin is `dsgConvolved_array` — a convolved shape's scalar `evalPeak` branch ignores m and must have no caller, parity guard (C))
 - `_migrateLineshapeAliases` if backwards-compat alias needed
 
 ### UCl4 U 4f Asymmetric Broadening
diff --git a/docs/findings/2026-09-fit-determinacy.md b/docs/findings/2026-09-fit-determinacy.md
index dce89de..07d89cb 100644
--- a/docs/findings/2026-09-fit-determinacy.md
+++ b/docs/findings/2026-09-fit-determinacy.md
@@ -338,6 +338,13 @@ area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
 the 530 peak records in the seven committed projects use DS+G (and none of
 the 202 measurement targets), so no saved figure is affected; it is the
 fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
-recorded as its own unit. The general lesson repeats §6's: a harness that
+FIXED the same day in `fix-dsg-page-evaluator` after the owner asked whether
+Find Peaks emits DS+G: it does (every A- and M-family C 1s candidate's
+graphitic main line, β fixed at 0.05, α 0–0.3, m 0.4–1.8), and on that box
+the page's area was 5–21 % low for α 0.15–0.3. `dsgConvolved_array` mirrors
+the server's padded-grid convolution to ≤ 3e-15 of amplitude across the
+whole β/m box on seven grids; nothing changed in Find Peaks or the dropdown
+(a science decision is not altered to work around a rendering bug —
+owner, 2026-09-22). The general lesson repeats §6's: a harness that
 evaluates one representative point per shape proves nothing about the range
 the optimiser can reach.

exec
/bin/zsh -lc "sed -n '1,155p' tests/js/lineshape_parity.test.js; sed -n '275,392p' tests/js/lineshape_parity.test.js; sed -n '1,255p' tests/js/lineshape_roundtrip.test.js; sed -n '4028,4047p' templates/index.html; sed -n '7980,8245p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
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

// ── (C) Structural guard: evalPeak() must have no callers of its own ──────
// outside evalPeakArray()'s internal fallback. This is what actually closes
// the bug-(B) mechanism for shipped code: any FUTURE export/save/results
// function that calls evalPeak(...) directly instead of evalPeakArray(...)
// will silently reintroduce the LACX-ignores-convolution bug for that call
// site, exactly as happened in commits 8ff030e..5093487 (2026-04-25 through
// 2026-08-30, per docs/autofit/codex git-archaeology). This test makes that
// impossible to do silently.
test('(C) evalPeak() has no direct callers outside evalPeakArray()', () => {
  const evalPeakDef = extract(/function evalPeak\(x, p\) \{[\s\S]*?\n\}\n/, 'evalPeak definition');
  const evalPeakArrayDef = extract(/function evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}\n/, 'evalPeakArray definition');
  assert.ok(/\bevalPeak\(x, p\)/.test(evalPeakArrayDef),
    'evalPeakArray() no longer contains its expected internal evalPeak() fallback call — update this test\'s assumption');
  const rest = html.split(evalPeakDef).join('\n').split(evalPeakArrayDef).join('\n');
  const strayCalls = [...rest.matchAll(/\bevalPeak\(/g)];
  assert.strictEqual(strayCalls.length, 0,
    `evalPeak() is called directly ${strayCalls.length} time(s) outside evalPeakArray() — route through evalPeakArray() ` +
    'instead (see file header: evalPeak() silently ignores Gaussian convolution for LACX with m>0, which evalPeakArray() ' +
    'handles correctly).');
});

// ── (D) A03 (2026-09-22): sweep each shape's FREE parameters across the ──
// ranges the FIT can reach. Every test above evaluates ONE base peak per
// shape; a divergence that only appears at the edge of a bound (η = 0 or 1,
// α at 0.5, a Gaussian kernel narrower than the quadrature step) was
// invisible to it. The ranges below are fitting.py `_make_peak_params`'s
// bounds for a free peak (gl_ratio 0–1, asymmetry 0–1, DS α 0–0.5 and
// γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β 0.1–5 / m 0–499,
// fwhm 0.1–15) — what the OPTIMISER can reach. A lock can hold a value
// outside them (a held value is honoured as requested since A03 round 2;
// the round-trip harness covers those), a link follows its parent.
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
//     m) 64 %. Zero committed components use DS+G (0 of the 530 peak records
//     in the seven committed projects), so no saved
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
  // the full β/m box the optimiser can reach, incl. the corner that made the
  // old quadrature 1e52 × amplitude (β 2, m 0.05) and the delta threshold
  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] },
};
const SWEEP_KNOWN_GAP = {
  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
};
function sweepShape(label) { return label.split(' ')[0]; }
// The backend parameters of the sweep come from the PAGE's request builder,
// not from a mapping of this file's own (Codex round 1: a mapping written
// here could not see `p.glMix || 50` sending an asym-GL mix of 0 as 50).
const _specState = { peaks: [] };
const { peakToBackendSpec } = new Function('state', 'getPeak',
  extract(/function peakToBackendSpec\(p\) \{[\s\S]*?\n\}\n/, 'peakToBackendSpec definition') + '\nreturn { peakToBackendSpec };')(_specState, id => _specState.peaks.find(q => q.id === id));
function backendParamsFromRequest(p) {
  const spec = peakToBackendSpec(p);
  const keep = spec.shape === 'ds_g' ? ['amplitude', 'center', 'alpha', 'beta', 'm_gauss']
    : ['amplitude', 'center', 'fwhm', 'gl_ratio', 'asymmetry', 'alpha', 'gamma_asym', 'beta', 'm'];
  const params = {};
  for (const k of keep) if (k in spec) params[k] = spec[k];
  return { shape: spec.shape, params };
}
function runSweep(label, ranges) {
  const shape = sweepShape(label);
  const cases = combos(ranges).map(c => ({ c, p: { ...basePeak(shape), ...c } }));
  const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: grid(k.p.center) }; });
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
// Page → server → page identity (A03, 2026-09-22).
//
// The parity harness (lineshape_parity.test.js) proves the two EVALUATORS
// agree for the same parameters. It cannot see a request that asks the
// server to fit a parameter the page never draws: until A03 a "Voigt" was
// sent as pseudo_voigt_gl with gl_ratio FREE from 0.3 while evalPeak drew
// η = 0.5, so every chart component, area, percentage and export for a
// Voigt was the 0.5 curve under parameters fitted for another mix (on the
// 90 committed Voigt targets: displayed areas 13.9 % off the fitted curve at
// the median, 20 % at worst; 60 of 180 components had gone to pure
// Gaussian, 16 to pure Lorentzian). This test closes that class: for every
// shape, build the request with the PAGE's own peakToBackendSpec, fit it
// on the server (fitting.run_fit, no background, Trust-Region), apply the
// result with the page's own _applyBackendParams, and require the curve the
// page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
// server FITTED (individual_peaks[].y).
//
// One shape carries a known drawn-vs-fitted gap and is marked todo with the
// unit that owns it: LACX (the page sends m free and draws it ROUNDED — the
// caM clamp unit). DSG_LA was the other until 2026-09-22 (the page's
// quadrature; now dsgConvolved_array mirrors the server).
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
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'dsgConvolved_array',
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

// Codex round 1 reproduced two builder defects at ZERO endpoints: `p.glMix || 50`
// sent an asym-GL mix of 0 as 50 and `p.dsAlpha || 0.1` a DS alpha of 0 as
// 0.1 — values the page never drew; locked, the server held the substitute
// and the drawn curve differed from the fitted one by 6.9 % / 8.8 % of
// amplitude. Every shape parameter of every shape is now round-tripped
// LOCKED AT EACH OF ITS BOUNDS (fitting._make_peak_params): GL / asym-GL
// mix 0 and 1, asymmetry 0 and 1, DS α 0 and 0.5, γ 0 and 5, DS+G α 0 and
// 0.49, β 0.05 and 2, LA α and β 0.1 and 5. The two convolved shapes are
// exercised where their evaluators are exact (DS+G with m < 0.001, the
// delta branch; LA with m = 0); their m locks at m > 0 sit under the
// evaluator gaps marked todo above.
const LOCKED_AT_BOUNDS = [
  { label: 'GL mix 0 locked',            truth: { shape: 'GL', glMix: 0, fixGlMix: true }, held: { gl_ratio: 0 } },
  { label: 'GL mix 100 locked',          truth: { shape: 'GL', glMix: 100, fixGlMix: true }, held: { gl_ratio: 1 } },
  { label: 'asym-GL mix 0 locked',       truth: { shape: 'asym-GL', glMix: 0, asymmetry: 0.3, fixGlMix: true }, held: { gl_ratio: 0 } },
  { label: 'asym-GL mix 100 locked',     truth: { shape: 'asym-GL', glMix: 100, asymmetry: 0.3, fixGlMix: true }, held: { gl_ratio: 1 } },
  { label: 'asym-GL asymmetry 0 locked', truth: { shape: 'asym-GL', glMix: 40, asymmetry: 0, fixAsymmetry: true }, held: { asymmetry: 0 } },
  { label: 'asym-GL asymmetry 1 locked', truth: { shape: 'asym-GL', glMix: 40, asymmetry: 1, fixAsymmetry: true }, held: { asymmetry: 1 } },
  { label: 'DS alpha 0 locked',          truth: { shape: 'DS', dsAlpha: 0, dsGamma: 0.2, fixDsAlpha: true }, held: { alpha: 0 } },
  { label: 'DS alpha 0.5 locked',        truth: { shape: 'DS', dsAlpha: 0.5, dsGamma: 0.2, fixDsAlpha: true }, held: { alpha: 0.5 } },
  { label: 'DS gamma 0 locked',          truth: { shape: 'DS', dsAlpha: 0.2, dsGamma: 0, fixDsGamma: true }, held: { gamma_asym: 0 } },
  { label: 'DS gamma 5 locked',          truth: { shape: 'DS', dsAlpha: 0.2, dsGamma: 5, fixDsGamma: true }, held: { gamma_asym: 5 } },
  { label: 'DS+G alpha 0 locked (delta kernel)',    truth: { shape: 'DSG_LA', laAlpha: 0, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0, m_gauss: 0 } },
  { label: 'DS+G alpha 0.49 locked (delta kernel)', truth: { shape: 'DSG_LA', laAlpha: 0.49, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0.49, m_gauss: 0 } },
  { label: 'DS+G beta 0.05 locked (delta kernel)',  truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.05, laM: 0, fixLaBeta: true, fixLaM: true }, held: { beta: 0.05, m_gauss: 0 } },
  { label: 'DS+G beta 2 locked (delta kernel)',     truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 2, laM: 0, fixLaBeta: true, fixLaM: true }, held: { beta: 2, m_gauss: 0 } },
  { label: 'LA alpha 0.1 locked (m = 0)', truth: { shape: 'LACX', caAlpha: 0.1, caBeta: 1, caM: 0, fixCaAlpha: true, fixCaM: true }, held: { alpha: 0.1, m: 0 } },
  { label: 'LA alpha 5 locked (m = 0)',   truth: { shape: 'LACX', caAlpha: 5, caBeta: 1, caM: 0, fixCaAlpha: true, fixCaM: true }, held: { alpha: 5, m: 0 } },
  { label: 'LA beta 0.1 locked (m = 0)',  truth: { shape: 'LACX', caAlpha: 1, caBeta: 0.1, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 0.1, m: 0 } },
  { label: 'LA beta 5 locked (m = 0)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 5, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 5, m: 0 } },
  // the page's input allows α = 0.5; the server's evaluator clips α to 0.495 and so, since round 3, does the page's
  { label: 'DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)', truth: { shape: 'DSG_LA', laAlpha: 0.5, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0.5, m_gauss: 0 } },
  // LA's m lock at m > 0: request and server-held value are pinned; the drawn-vs-fitted
  // comparison sits under the caM evaluator gap marked todo above (curve: false)
  { label: 'DS+G m 0.05 locked', truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.05, fixLaM: true }, held: { m_gauss: 0.05 } },
  { label: 'DS+G m 4 locked',    truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 4, fixLaM: true }, held: { m_gauss: 4 } },
  { label: 'LA m 499 locked (request and hold only)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 }, curve: false },
];
for (const c of LOCKED_AT_BOUNDS) {
  test(`locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — ${c.label}`, () => {
    const { res, peaks, specs } = roundTrip(c.truth.shape, { truth: c.truth, start: {} });
    const p = peaks[0];
    for (const [name, value] of Object.entries(c.held)) {
      assert.equal(specs[0][name], value, `${c.label}: the request carries ${name} = ${value}`);
      assert.equal(res.individual_peaks[0].params[name].vary, false, `${c.label}: the server held ${name}`);
      assert.equal(res.individual_peaks[0].params[name].value, value, `${c.label}: at the locked value`);
    }
    if (c.curve === false) return;
    const rel = maxRelDiff(env.evalPeakArray(res.energy, p), res.individual_peaks[0].y, p.amplitude);
    assert.ok(rel < TIGHT_TOL, `${c.label}: drawn vs fitted curve differ by ${(rel * 100).toExponential(3)} % of amplitude`);
  });
}

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
  return core * tailDecay;
}

function laCasaXPSCore(eps, alpha, beta) {
  // Doniach-Šunjić core (BE convention) for LA(α,β,m)
  // α: dimensionless asymmetry index (0–0.5); tail at eps > 0 → HIGHER binding energy
  // β: Lorentzian half-width at half-maximum (eV)
  // Formula: cos(πα/2 − (1−α)·atan2(ε,β)) / (ε²+β²)^((1−α)/2)
  // The πα/2 offset + sign flip create the asymmetric power-law tail.
  const r2 = eps * eps + beta * beta;
  if (r2 < 1e-30) return 1.0;
  const rPow = Math.pow(r2, (1 - alpha) / 2);
  if (rPow === 0) return 0;
  const phase = Math.PI * alpha / 2 - (1 - alpha) * Math.atan2(eps, beta);
  return Math.cos(phase) / rPow;
}

function laCasaXPS(x, center, alpha, beta, mGauss) {
  // Per-point DS+G fallback for the scalar evaluator's DSG_LA branch: the
  // NORMALISED DS core, m IGNORED — exactly as its LACX branch ignores m. The Gaussian
//
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
  }
  // weighted residual: what the optimiser minimises (chi = sum of squares)
  function residuals(params) {
    return rawResiduals(params).map((v, i) => v * _w[i]);
  }

  function chiSq(params) {
    const r = residuals(params);
    return r.reduce((s, v) => s + v * v, 0);
  }

  let params = freeParams.map((v, i) => clamp(paramMap[i].param, v));
  let chi = chiSq(params);
  if (!Number.isFinite(chi)) return fail('the model is not finite at the starting parameters.');
  let lambda = 0.001;
  // Feasible-descent certificate (see PROBE_REL below). Returns true when
  // no single-parameter feasible move improves the residual by more than
  // FTOL; otherwise moves to the best such point and returns false.
  function certify() {
    applyParams(params);                     // working copy = current point
    let bestChi = chi, bestParams = null;
    for (let j = 0; j < params.length; j++) {
      if (isDiscrete(j)) continue;
      for (const sgn of [-1, 1]) {
        const trial = [...params];
        trial[j] = clamp(paramMap[j].param, params[j] + sgn * PROBE_REL * paramScale(j, params));
        if (trial[j] === params[j]) continue;
        const c = chiSq(trial);
        if (Number.isFinite(c) && c < bestChi) { bestChi = c; bestParams = trial; }
      }
    }
    applyParams(params);
    if (bestParams && bestChi < chi * (1 - FTOL)) {
      params = bestParams; chi = bestChi; certifyRestarts++;
      lambda = Math.max(lambda, 1e-3);
      return false;
    }
    return true;
  }
  // Finite-difference step per parameter. A centre's natural scale is the
  // peak WIDTH, not its binding energy: h*|285 eV| = 0.03 eV is wider than
  // a narrow peak and gave misleading derivatives (Codex round 1).
  const H_REL = 1e-4;
  // Scale of parameter j at the parameter VECTOR `vec` — a pure function of
  // the vector, never of the mutable working copy (which the Jacobian loop
  // leaves at its last perturbation — Codex round 5). A centre's scale is
  // its peak's width: from the vector when the width is free, from the
  // (never perturbed) fixed value otherwise.
  const fwhmIndex = {};
  paramMap.forEach((d, k) => { if (d.param === 'fwhm') fwhmIndex[d.id] = k; });
  const paramScale = (j, vec) => {
    const { id, param } = paramMap[j];
    if (param === 'center') {
      const w = fwhmIndex[id] !== undefined ? vec[fwhmIndex[id]] : (workPeak(id) || {}).fwhm;
      return Math.max(0.05, Number.isFinite(w) ? w : 1);
    }
    return Math.max(1, Math.abs(vec[j]));
  };
  // caM is rounded to an integer by its clamp, so a finite difference cannot
  // see it: it is carried at its starting value (inherited behaviour; see the
  // A0 follow-up list) and excluded from the stationarity test.
  const isDiscrete = j => paramMap[j].param === 'caM';
  // MINPACK-style termination: (ftol) actual AND predicted relative
  // reductions both below FTOL, with the linearised model agreeing with
  // the actual reduction; (xtol) relative step below XTOL; (gtol) the
  // largest cosine between the residual and any Jacobian column below
  // GTOL. Tiny steps alone never count. FTOL = 1e-6 (relative chi-square):
  // on real 6-component C1s data with a vanished component the optimiser
  // otherwise crawls a flat valley for thousands of iterations changing
  // chi-square in its 7th digit and no parameter in its 5th.
  const FTOL = 1e-6, XTOL = 1e-8, GTOL = 1e-6, SENS_MIN = 1e-12;
  // CERTIFICATE: a tentative convergence (gtol / ftol / xtol) is accepted
  // only if no feasible move of PROBE_REL (scaled) in any single free
  // parameter reduces the residual by more than FTOL of its value. If one
  // does, that point is taken and iteration continues (Codex round 3: the
  // linearised model is not a stationarity certificate; a column-norm
  // cutoff froze determined parameters).
  const PROBE_REL = 1e-3, MAX_CERTIFY = 200;
  // No exit is exempt from the certificate: a tiny absolute residual is
  // still probed relatively (Codex round 4). The certificate is a
  // single-parameter (coordinate) feasible-descent check, not a proof of a
  // local minimum along coupled directions; the LM step handles coupling
  // during optimisation.
  let converged = params.length === 0 || (chi === 0 && certify());
  let iterations = 0;
  let acceptedSteps = 0;
  let certifyRestarts = 0;

  for (let iter = 0; iter < maxIter && !converged; iter++) {
    iterations++;
    if (certifyRestarts > MAX_CERTIFY) return fail('could not certify a stationary point after ' + iterations + ' iterations.', iterations);
    const r = residuals(params);
    const n = params.length;
    // Central-difference Jacobian d r / d p, stepping inside the parameter
    // box (one-sided at a wall).
    const J = [];
    for (let j = 0; j < n; j++) {
      const { param } = paramMap[j];
      const step = H_REL * paramScale(j, params);
      const pPlus = [...params], pMinus = [...params];
      pPlus[j] = clamp(param, params[j] + step);
      pMinus[j] = clamp(param, params[j] - step);
      const span = pPlus[j] - pMinus[j];
      if (span === 0) { J.push(r.map(() => 0)); continue; }
      const rPlus = pPlus[j] === params[j] ? r : residuals(pPlus);
      const rMinus = pMinus[j] === params[j] ? r : residuals(pMinus);
      J.push(rPlus.map((v, i) => (v - rMinus[i]) / span));
    }
    const JtJ = Array.from({length: n}, () => new Array(n).fill(0));
    const Jtr = new Array(n).fill(0);
    for (let a = 0; a < n; a++) {
      for (let b = 0; b < n; b++) {
        for (let i = 0; i < r.length; i++) JtJ[a][b] += J[a][i] * J[b][i];
      }
      for (let i = 0; i < r.length; i++) Jtr[a] += J[a][i] * r[i];
    }
    if (!Jtr.every(Number.isFinite) || !JtJ.every(row => row.every(Number.isFinite))) {
      return fail('the model derivative is not finite.', iterations);
    }
    // Sensitivity: a model that does not respond to any free parameter here
    // (e.g. a peak far outside the window) cannot be optimised — that is a
    // failure, not a stationary point.
    let sens = 0;
    for (let j = 0; j < n; j++) if (!isDiscrete(j)) sens = Math.max(sens, JtJ[j][j] * paramScale(j, params) ** 2);
    if (n > 0 && sens / Math.max(chi, 1e-300) < SENS_MIN) {
      return fail('the model has no measurable sensitivity to its free parameters in this region.', iterations);
    }
    // ACTIVE SET: a parameter whose descent direction points into a wall of
    // the parameter box (or that has no sensitivity, or is discrete) is held
    // FIXED for this step. Solving the joint system with such a parameter
    // and then clipping it would leave the other components of the step
    // meaningless and let a tiny "agreed" step pass the ftol test at a
    // non-stationary point (Codex round 2). With r = data - model,
    // d(chi)/dp_j = +2 * (J_j . r), so the descent direction is -sign(J_j . r).
    const active = [];
    let gradCos = 0;
    const rNorm = Math.sqrt(chi);
    for (let j = 0; j < n; j++) {
      if (isDiscrete(j) || !(JtJ[j][j] > 0)) continue;
      if (Jtr[j] !== 0) {
        const probe = clamp(paramMap[j].param, params[j] - Math.sign(Jtr[j]) * 1e-6 * paramScale(j, params));
        if (probe === params[j]) continue;          // blocked by the box
      }
      active.push(j);
      if (rNorm > 0) gradCos = Math.max(gradCos, Math.abs(Jtr[j]) / (Math.sqrt(JtJ[j][j]) * rNorm));
    }
    // Projected gradient test (gtol) over the active set only. A failed
    // certificate has moved the point: restart the iteration so the
    // derivatives and active set are rebuilt there.
    if (gradCos < GTOL) { if (certify()) { converged = true; break; } continue; }
    // Linear model of the residual, for the predicted reduction (ftol test).
    const JtJ0 = JtJ.map(row => row.slice());

    // Marquardt damping, then the DESCENT step on the active set:

exec
/bin/zsh -lc "ls /Users/skyefortier/xps-app/venv/bin/python3; rg -n 'evalPeakArray|evalAllPeaks|laCasaXPS|function updatePeakParam|function _peakArea' templates/index.html; cat tests/test_la_short_input.py; ls /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md 2>/dev/null" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 exited 1 in 0ms:
/Users/skyefortier/xps-app/venv/bin/python3
4031:function laCasaXPSCore(eps, alpha, beta) {
4045:function laCasaXPS(x, center, alpha, beta, mGauss) {
4049:  // through evalPeakArray, the only shipped path — parity guard (C)). Until
4053:  const peakVal = laCasaXPSCore(0, alpha, beta);
4055:  return laCasaXPSCore(x - center, alpha, beta) / peakVal;
4136:    // laCasaXPS already returns a normalised [0,1] value. α is clipped as
4139:    y = laCasaXPS(x, center, _dsgAlpha(p.laAlpha), p.laBeta, p.laM);
4142:    // build paths use laTrueCasaXPS_array via evalPeakArray.
4166:  for (let i = 0; i < N; i++) core[i] = laCasaXPSCore(beArr[i] - center, alpha, beta);
4240:  for (let i = 0; i < nTot; i++) { const v = laCasaXPSCore(xp[i] - center, a, b); ds[i] = Number.isFinite(v) ? v : 0; }
4289:function evalPeakArray(beArr, p) {
4308:function evalAllPeaks(beArray, peaks) {
4312:    const yArr = evalPeakArray(beArray, p);
5819:function updatePeakParam(id, key, value) {
8090:    const model = evalAllPeaks(be, work);
8310:    const model = evalAllPeaks(be, work);
8314:      const comp = evalPeakArray(be, wp);
8384:function _peakArea(p, be) {
8386:  // evalPeakArray(), not a per-point evalPeak map: for LACX with caM > 0,
8390:  return evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step;
8775://       LM fit) → fittedY = evalAllPeaks(be, peaks) + bg.
8851:    const model = evalAllPeaks(be, peaks);
8859:    const peakOnly = evalPeakArray(be, p);
9318:  const modelFull = evalAllPeaks(plotBE, state.peaks);
9363:      const peakY = evalPeakArray(plotBE, p);
9427:    const prevPeakY = evalAllPeaks(plotBE, _historyPreview.peaks);
10051:  const modelFull = evalAllPeaks(be, state.peaks);
10056:  // Per-peak curves and areas. evalPeakArray(), not per-point evalPeak:
10061:    const yArr = evalPeakArray(be, p);
10722:  const modelFull = evalAllPeaks(be, state.peaks);
10723:  // evalPeakArray() per peak, once, not per-point evalPeak per row: for
10727:  // Model/Residual columns above (built from evalAllPeaks) are correct.
10728:  const peakCols = state.peaks.map(p => evalPeakArray(be, p));
10873:      // evalPeakArray(), not per-point evalPeak: applies Gaussian
10875:      const pkArr = evalPeakArray(be, p);
10905:      // evalPeakArray(), not per-point evalPeak: applies Gaussian
10907:      const pkArr = evalPeakArray(be, p);
11004:      // evalPeakArray(), not per-point evalPeak: see fill/outline loops above.
11005:      const pArr = evalPeakArray(be, p);
11290:    const modelY = evalAllPeaks(be, state.peaks);
"""
Regression: _la_casaxps_true must return len(output) == len(x) for any
input length, including the case where the input grid is shorter than
the Gaussian convolution kernel (2m+1 points).

np.convolve(..., mode='same') returns max(len(a), len(v)), not len(a),
so without an explicit trim the function returned a kernel-length array
when the input grid was shorter than the kernel — breaking the lmfit
residual computation in composite fits and surfacing as cryptic shape
mismatches like "operands could not be broadcast together with shapes
(995,) (349,)".
"""
import sys
sys.path.insert(0, "/home/skye/xps-app")
import numpy as np
from fitting import _la_casaxps_true


def test_short_input_returns_input_length():
    # When len(x) < 2m+1 the kernel is longer than the input. Output must
    # still match len(x). Span the boundary where len(x) crosses 2m+1.
    for n in [10, 50, 100, 101, 102, 200, 500]:
        x = np.linspace(370, 405, n)
        y = _la_casaxps_true(x, 1000, 380, 1.5, 1.0, 1.0, m=50)
        assert len(y) == n, f"len mismatch for n={n}: got {len(y)}"
    print("OK — short-input length contract holds across 2m+1 boundary")


def test_zero_kernel():
    # m=0 still works (no convolution branch).
    x = np.linspace(370, 405, 10)
    y = _la_casaxps_true(x, 1000, 380, 1.5, 1.0, 1.0, m=0)
    assert len(y) == 10
    print("OK — m=0 short-input passes through unconvolved")


if __name__ == "__main__":
    test_short_input_returns_input_length()
    test_zero_kernel()

codex
The hard DS+G sweep uses the page’s request builder, and I found no shipped caller bypassing `evalPeakArray`. I’m now testing outside those assertions: short and irregular grids, centres beyond the data window, and redraw costs on finer grids.

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/*.test.js | tail -n 22' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc "sed -n '90,190p' tests/js/lineshape_roundtrip.test.js; sed -n '5808,5848p' templates/index.html; sed -n '9250,9375p' templates/index.html; sed -n '1,105p' tests/js/local_lm_descent.test.js; rg -n 'center.*min|center.*max|center_window|ds_g' fitting.py | head -n 45" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
  'DSG_LA':     { truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.8 }, start: { laAlpha: 0.10, laBeta: 0.3, laM: 0.4 } },
  'LACX':       { truth: { shape: 'LACX', caAlpha: 1.6, caBeta: 0.7, caM: 20 }, start: { caAlpha: 1.0, caBeta: 1.0, caM: 30 } },
};
const TIGHT_TOL = 1e-6;      // of amplitude; both curves are the same closed form on the same grid
const KNOWN_GAP = {
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

// Codex round 1 reproduced two builder defects at ZERO endpoints: `p.glMix || 50`
// sent an asym-GL mix of 0 as 50 and `p.dsAlpha || 0.1` a DS alpha of 0 as
// 0.1 — values the page never drew; locked, the server held the substitute
// and the drawn curve differed from the fitted one by 6.9 % / 8.8 % of
// amplitude. Every shape parameter of every shape is now round-tripped
// LOCKED AT EACH OF ITS BOUNDS (fitting._make_peak_params): GL / asym-GL
// mix 0 and 1, asymmetry 0 and 1, DS α 0 and 0.5, γ 0 and 5, DS+G α 0 and
// 0.49, β 0.05 and 2, LA α and β 0.1 and 5. The two convolved shapes are
// exercised where their evaluators are exact (DS+G with m < 0.001, the
// delta branch; LA with m = 0); their m locks at m > 0 sit under the
// evaluator gaps marked todo above.
const LOCKED_AT_BOUNDS = [
  { label: 'GL mix 0 locked',            truth: { shape: 'GL', glMix: 0, fixGlMix: true }, held: { gl_ratio: 0 } },
  { label: 'GL mix 100 locked',          truth: { shape: 'GL', glMix: 100, fixGlMix: true }, held: { gl_ratio: 1 } },
  { label: 'asym-GL mix 0 locked',       truth: { shape: 'asym-GL', glMix: 0, asymmetry: 0.3, fixGlMix: true }, held: { gl_ratio: 0 } },
  { label: 'asym-GL mix 100 locked',     truth: { shape: 'asym-GL', glMix: 100, asymmetry: 0.3, fixGlMix: true }, held: { gl_ratio: 1 } },
  { label: 'asym-GL asymmetry 0 locked', truth: { shape: 'asym-GL', glMix: 40, asymmetry: 0, fixAsymmetry: true }, held: { asymmetry: 0 } },
  { label: 'asym-GL asymmetry 1 locked', truth: { shape: 'asym-GL', glMix: 40, asymmetry: 1, fixAsymmetry: true }, held: { asymmetry: 1 } },
  { label: 'DS alpha 0 locked',          truth: { shape: 'DS', dsAlpha: 0, dsGamma: 0.2, fixDsAlpha: true }, held: { alpha: 0 } },
  { label: 'DS alpha 0.5 locked',        truth: { shape: 'DS', dsAlpha: 0.5, dsGamma: 0.2, fixDsAlpha: true }, held: { alpha: 0.5 } },
  { label: 'DS gamma 0 locked',          truth: { shape: 'DS', dsAlpha: 0.2, dsGamma: 0, fixDsGamma: true }, held: { gamma_asym: 0 } },
  { label: 'DS gamma 5 locked',          truth: { shape: 'DS', dsAlpha: 0.2, dsGamma: 5, fixDsGamma: true }, held: { gamma_asym: 5 } },
  { label: 'DS+G alpha 0 locked (delta kernel)',    truth: { shape: 'DSG_LA', laAlpha: 0, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0, m_gauss: 0 } },
  { label: 'DS+G alpha 0.49 locked (delta kernel)', truth: { shape: 'DSG_LA', laAlpha: 0.49, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0.49, m_gauss: 0 } },
  { label: 'DS+G beta 0.05 locked (delta kernel)',  truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.05, laM: 0, fixLaBeta: true, fixLaM: true }, held: { beta: 0.05, m_gauss: 0 } },
  { label: 'DS+G beta 2 locked (delta kernel)',     truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 2, laM: 0, fixLaBeta: true, fixLaM: true }, held: { beta: 2, m_gauss: 0 } },
  { label: 'LA alpha 0.1 locked (m = 0)', truth: { shape: 'LACX', caAlpha: 0.1, caBeta: 1, caM: 0, fixCaAlpha: true, fixCaM: true }, held: { alpha: 0.1, m: 0 } },
  { label: 'LA alpha 5 locked (m = 0)',   truth: { shape: 'LACX', caAlpha: 5, caBeta: 1, caM: 0, fixCaAlpha: true, fixCaM: true }, held: { alpha: 5, m: 0 } },
  { label: 'LA beta 0.1 locked (m = 0)',  truth: { shape: 'LACX', caAlpha: 1, caBeta: 0.1, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 0.1, m: 0 } },
  { label: 'LA beta 5 locked (m = 0)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 5, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 5, m: 0 } },
  // the page's input allows α = 0.5; the server's evaluator clips α to 0.495 and so, since round 3, does the page's
  if (!child || !child.linked) return;
  const parent = getPeak(child.linked);
  if (!parent) return;
  let r = parseFloat(rawVal);
  if (!isFinite(r) || r < 0.01) r = 0.01;
  if (r > 2) r = 2;
  child.linkRatio = r;
  child.amplitude = parent.amplitude * r;
  updatePeakParam(id, 'amplitude', child.amplitude);
}

function updatePeakParam(id, key, value) {
  _pushUndoDebounced();
  const p = getPeak(id);
  if (!p) return;
  // asymmetry: clamp to the backend's own bound (fitting.py np.clip(asymmetry,
  // 0, 1)) — a plain assignment let out-of-range values (e.g. pasted/loaded)
  // sit on the peak until a backend fit result overwrote them.
  if (key === 'asymmetry') value = Math.max(0, Math.min(1, value));
  p[key] = value;

  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
  if (syncKeys.includes(key)) {
    // Resolve canonical parent: if p is a child, find its parent first
    let parent = p.linked ? getPeak(p.linked) : p;
    if (!parent) parent = p;

    if (p.linked && parent) {
      // p is a child — back-propagate changed value to parent
      if (key === 'center') parent.center = p.center - p.linkOffset;
      else if (key === 'amplitude') {
        // Only divide back to the parent when the ratio is meaningfully >0.
        // Otherwise (child was zeroed or ratio is tiny) leave the parent alone.
        if (p.linkRatio && p.linkRatio > 1e-6) {
          parent.amplitude = p.amplitude / p.linkRatio;
        }
      }
      else parent[key] = p[key];
      renderPeakControls(parent);
    }

    if (sc.y) {
      if (sc.y.ticks) sc.y.ticks.display = !offsetActive;
      if (sc.y.title) {
        sc.y.title.display = true;
        sc.y.title.text = offsetActive ? 'Intensity (offset stacked)' : 'Intensity (counts/s)';
      }
    }
  }
  state.chart.update('none');
}

function updatePlot() {
  // Stack-tab early branch: render multi-spectrum overlay, no peaks/fits.
  // Route through _updateStackChart so toolbar-pill toggles (Envelope,
  // Individual Peaks, Fill, Bkgrd Sub) and other state changes preserve
  // zoom by in-place updating. _updateStackChart delegates to
  // _renderStackChart automatically when no chart exists.
  {
    const _activeTab = (typeof tabManager !== 'undefined') ? tabManager._getTab(tabManager.activeId) : null;
    const _emptyEl = document.getElementById('stack-empty-state');
    const _canvas = document.getElementById('mainChart');
    if (isStackTab(_activeTab)) {
      _updateStackChart(_activeTab);
      return;
    } else {
      if (_canvas) _canvas.style.display = '';
      if (_emptyEl) _emptyEl.style.display = 'none';
    }
  }

  // Full corrected spectrum (for raw data display and axis range)
  const corrBE = getCorrectedBE();
  const fullInten = state.rawIntensity;

  // ROI-filtered data (for fitting, background, peaks)
  const { be, inten } = getROIData();
  const invert = document.getElementById('invert-be').checked;
  const showIndividual = document.getElementById('show-individual').checked;
  const showResiduals = document.getElementById('show-residuals').checked;

  const _ob = document.getElementById('main-chart-wrap').querySelector('.onboard-wrap');
  if (_ob) _ob.remove();

  if (!corrBE.length) {
    renderEmptyChart();
    return;
  }

  // After a fit, freeze all curve data to the stored fit state so that
  // changing ROI never re-draws or recomputes the fit, background, or peaks.
  const haveFit = !!(state.fitResult && Array.isArray(state.fitResult.be) &&
                     state.fitResult.be.length > 0 &&
                     Array.isArray(state.fitResult.bgIntensity) &&
                     state.fitResult.bgIntensity.length === state.fitResult.be.length);

  // plotBE/plotBG/plotInten drive all fit-related curves (peaks, background, envelope).
  // When a fit exists, they come from the frozen fit state — ROI changes don't affect them.
  // Before fitting, they come from the current ROI so live peak previews still work.
  const plotBE = haveFit ? state.fitResult.be : be;
  const plotBG = haveFit ? state.fitResult.bgIntensity
                         : (be.length ? computeBackground(be, inten) : []);
  const plotInten = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                    ? state.fitResult.bgSubtracted.map((v, i) => v + plotBG[i])
                    : inten;
  const bgSubtracted = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                       ? state.fitResult.bgSubtracted
                       : plotInten.map((v, i) => v - plotBG[i]);

  const modelFull = evalAllPeaks(plotBE, state.peaks);
  // Use backend fitted_y when available (authoritative lmfit result);
  // fall back to JS-recomputed modelFull + bg for pre-fit / local-LM fits.
  const fittedYBacked = haveFit && state.fitResult.fittedY &&
                        state.fitResult.fittedY.length === plotBE.length
                        ? state.fitResult.fittedY : null;
  const rawResiduals = fittedYBacked
    ? plotInten.map((v, i) => v - fittedYBacked[i])
    : bgSubtracted.map((v, i) => v - modelFull[i]);
  // Percentage residuals: ((data - fit) / data) × 100, clamped to ±100%
  const residuals = rawResiduals.map((r, i) => {
    const d = fittedYBacked ? plotInten[i] : bgSubtracted[i];
    if (Math.abs(d) < 1e-10) return 0;
    return Math.max(-100, Math.min(100, (r / d) * 100));
  });

  const datasets = [];

  // Bkgrd Sub view: redraws the chart with the background subtracted.
  // The flag is read once per updatePlot() call so all dataset branches
  // see a consistent value. _isBgSubViewActive() is defensive — it
  // returns false if bg-type is "none" even when the pill is checked.
  const bgSubView = _isBgSubViewActive();

  // Individual peaks drawn first (bottom layer) — frozen to fit range after fit
  const showFill = document.getElementById('show-fill').checked;
  if (showIndividual && plotBE.length) {
    if (showFill) {
      // First add invisible background-level datasets as fill targets
      for (let pi = 0; pi < state.peaks.length; pi++) {
        const p = state.peaks[pi];
        datasets.push({
          label: '_bg_' + p.id,
          data: plotBE.map((b, i) => ({ x: b, y: bgSubView ? 0 : plotBG[i] })),
          borderColor: 'transparent',
          borderWidth: 0,
          pointRadius: 0,
          fill: false,
          hidden: false,
        });
      }
    }
    for (let pi = 0; pi < state.peaks.length; pi++) {
      const p = state.peaks[pi];
      const fillTarget = showFill ? { target: pi, above: p.color + '40', below: 'transparent' } : false;
      const peakY = evalPeakArray(plotBE, p);
      datasets.push({
        label: _isUnsupported(p) ? p.name + ' (' + _UNSUPPORTED_LABEL + ')' : p.name,
        _unsupported: _isUnsupported(p),
        data: plotBE.map((b, i) => ({ x: b, y: peakY[i] + (bgSubView ? 0 : plotBG[i]) })),
        borderColor: p.color,
        backgroundColor: p.color + '40',
        borderWidth: state.lineWidth ?? 1.5,
        pointRadius: 0,
        fill: fillTarget,
        tension: 0,
        _peakId: p.id
      });
// Local Levenberg–Marquardt: it must DESCEND and it must never present a
// non-converged attempt as a result (unit A0, 2026-09-15).
//
// Background: from the initial commit (f20d71b) until this unit, runFitLocal
// solved JᵀJ·dp = +Jᵀr with r = data − model, so every step was an ascent
// step, no step was ever accepted, and after 24 rejections λ passed 1e8 and
// the loop exited with the STARTING parameters, announced as "Fit complete
// (local LM)". Every Batch Fit called that path. The empirical proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md; this file is
// that proof turned into a regression test on the SHIPPED functions.
//
// Everything under test is extracted verbatim from templates/index.html by
// function name (brace-matched) — the same functions the browser runs.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found in templates/index.html`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
  return { be, bgSub, bg, initial: JSON.parse(JSON.stringify(cloned)) };
}

// The objective the local engine minimises since unit W1: the Poisson-weighted
// sum of squares, w = 1/sqrt(max(raw counts, 1)), raw = bgSub + bg.
function residualSS(env, be, bgSub, bg) {
  const m = env.evalAllPeaks(be, env.state.peaks);
  return be.reduce((s, _, i) => { const raw = bgSub[i] + (bg ? bg[i] : 0); return s + (bgSub[i] - m[i]) ** 2 / Math.max(raw, 1); }, 0);
}

test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
  const tabs = loadProjectTabs();
  for (const target of ['C1s Scan_0', 'C1s Scan_4', 'C1s Scan_8']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
11:  ds_g            – DS+G: DS core × Gaussian convolution (formerly "la_casaxps")
152:def _ds_g_dscore_gauss(
772:    "ds_g": _ds_g_dscore_gauss,
823:    center_min     : float – lower bound   (optional)
824:    center_max     : float – upper bound   (optional)
903:        if shape == "ds_g":
924:    c_min = spec.get("center_min")
925:    c_max = spec.get("center_max")
926:    if shape != "ds_g" and c_min is None:
928:    if shape != "ds_g" and c_max is None:
930:    _set("center", center, min_=c_min, max_=c_max, vary=not spec.get("fix_center", False))
951:    if shape == "ds_g":

 succeeded in 44740ms:
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 381 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 17.503375
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 382 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 8.746905
  type: 'test'
  ...
1..382
# tests 382
# suites 0
# pass 313
# fail 64
# cancelled 0
# skipped 0
# todo 5
# duration_ms 44770.400577

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();
const cases=[];
for(const n of [1,2,3,30,200]) for(const m of [.001,.05,.4,4]) for(const beta of [.05,2]) for(const alpha of [0,.25,.49]) for(const center of [0,6,10,50,-50]) {
 const x=Array.from({length:n},(_,i)=>(i-(n-1)/2)*.05);
 cases.push({x,params:{amplitude:1,center,alpha,beta,m_gauss:m},shape:'\\''ds_g'\\''});
}
for(const x of [[-3,-2.9,-2.8,0,2,3],[0,1,2,8,15],[0,2],[0,10]]) for(const m of [.05,.4,4]) cases.push({x,params:{amplitude:1,center:0,alpha:.25,beta:.05,m_gauss:m},shape:'\\''ds_g'\\''});
const raw=cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''tests/js/lineshape_parity_backend.py'\\''],{input:JSON.stringify(cases),encoding:'\\''utf8'\\'',maxBuffer:64*1024*1024});
const yy=JSON.parse(raw); const results=cases.map((c,i)=>{const p=c.params;const j=ev(c.x,{shape:'\\''DSG_LA'\\'',amplitude:1,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss});return {n:c.x.length,x:c.x.length<10?c.x:[c.x[0],c.x.at(-1)],...p,err:Math.max(...j.map((v,k)=>Math.abs(v-yy[i][k]))),js:j.slice(0,3),py:yy[i].slice(0,3)};});
console.log('\\''worst'\\'',JSON.stringify(results.sort((a,b)=>b.err-a.err).slice(0,8),null,2));console.log('\\''within centre zero'\\'',JSON.stringify(results.filter(r=>r.center===0).slice(0,5),null,2));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 exited 1 in 1062ms:
Traceback (most recent call last):
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
    from fitting import _SHAPE_FUNCS  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
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
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
<ref *1> node:child_process:955
    throw err;
    ^

Error: spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE
    at Object.spawnSync (node:internal/child_process:1120:20)
    at spawnSync (node:child_process:902:24)
    at Object.execFileSync (node:child_process:945:15)
    at [eval]:12:14
    at runScriptInThisContext (node:internal/vm:209:10)
    at node:internal/process/execution:446:12
    at [eval]-wrapper:6:24
    at runScriptInContext (node:internal/process/execution:444:60)
    at evalFunction (node:internal/process/execution:279:30)
    at evalTypeScript (node:internal/process/execution:291:3) {
  errno: -32,
  code: 'EPIPE',
  syscall: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3',
  path: '/Users/skyefortier/xps-app/venv/bin/python3',
  spawnargs: [ 'tests/js/lineshape_parity_backend.py' ],
  error: [Circular *1],
  status: 1,
  signal: null,
  output: [
    null,
    '',
    'Traceback (most recent call last):\n' +
      '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>\n' +
      '    from fitting import _SHAPE_FUNCS  # noqa: E402\n' +
      '    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n' +
      '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>\n' +
      '    from lmfit import Model, Parameters\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\n' +
      '    from .confidence import conf_interval, conf_interval2d\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\n' +
      '    from .minimizer import MinimizerException\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\n' +
      '    from .parameter import Parameter, Parameters\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\n' +
      '    from .jsonutils import decode4js, encode4js\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\n' +
      '    import dill\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\n' +
      '    from .session import (\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\n' +
      '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\n' +
      '                               ^^^^^^^^^^^^^^^^^^^^^\n' +
      '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\n' +
      '    return _os.fsdecode(_gettempdir())\n' +
      '                        ^^^^^^^^^^^^^\n' +
      '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\n' +
      '    tempdir = _get_default_tempdir()\n' +
      '              ^^^^^^^^^^^^^^^^^^^^^^\n' +
      '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\n' +
      '    raise FileNotFoundError(_errno.ENOENT,\n' +
      "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']\n"
  ],
  pid: 33099,
  stdout: '',
  stderr: 'Traceback (most recent call last):\n' +
    '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>\n' +
    '    from fitting import _SHAPE_FUNCS  # noqa: E402\n' +
    '    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n' +
    '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>\n' +
    '    from lmfit import Model, Parameters\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\n' +
    '    from .confidence import conf_interval, conf_interval2d\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\n' +
    '    from .minimizer import MinimizerException\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\n' +
    '    from .parameter import Parameter, Parameters\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\n' +
    '    from .jsonutils import decode4js, encode4js\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\n' +
    '    import dill\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\n' +
    '    from .session import (\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\n' +
    '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\n' +
    '                               ^^^^^^^^^^^^^^^^^^^^^\n' +
    '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\n' +
    '    return _os.fsdecode(_gettempdir())\n' +
    '                        ^^^^^^^^^^^^^\n' +
    '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\n' +
    '    tempdir = _get_default_tempdir()\n' +
    '              ^^^^^^^^^^^^^^^^^^^^^^\n' +
    '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\n' +
    '    raise FileNotFoundError(_errno.ENOENT,\n' +
    "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']\n"
}

Node.js v22.22.2

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();

const cases=[];
for(const n of [1,2,3,30,200]) for(const m of [.001,.05,.4,4]) for(const beta of [.05,2]) for(const alpha of [0,.25,.49]) for(const center of [0,6,10,50,-50]) {
 const x=Array.from({length:n},(_,i)=>(i-(n-1)/2)*.05);
 cases.push({x,params:{amplitude:1,center,alpha,beta,m_gauss:m},shape:'\\''ds_g'\\''});
}
for(const x of [[-3,-2.9,-2.8,0,2,3],[0,1,2,8,15],[0,2],[0,10]]) for(const m of [.05,.4,4]) cases.push({x,params:{amplitude:1,center:0,alpha:.25,beta:.05,m_gauss:m},shape:'\\''ds_g'\\''});
const raw=cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'','\\''import tempfile,runpy; tempfile.tempdir=\"/tmp\"; runpy.run_path(\"tests/js/lineshape_parity_backend.py\",run_name=\"__main__\")'\\''],{input:JSON.stringify(cases),encoding:'\\''utf8'\\'',maxBuffer:64*1024*1024});
const yy=JSON.parse(raw); const results=cases.map((c,i)=>{const p=c.params;const j=ev(c.x,{shape:'\\''DSG_LA'\\'',amplitude:1,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss});return {n:c.x.length,x:c.x.length<10?c.x:[c.x[0],c.x.at(-1)],...p,err:Math.max(...j.map((v,k)=>Math.abs(v-yy[i][k]))),js:j.slice(0,3),py:yy[i].slice(0,3)};});
console.log('\\''worst'\\'',JSON.stringify(results.sort((a,b)=>b.err-a.err).slice(0,8),null,2));console.log('\\''within centre zero'\\'',JSON.stringify(results.filter(r=>r.center===0).slice(0,5),null,2));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require('\\''child_process'\\''); const orig=cp.execFileSync; cp.execFileSync=function(file,args,opts) {if(/python/.test(file) && args[0].endsWith('\\''.py'\\'')) args=['\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name=\"__main__\")'\\'',...args]; return orig(file,args,opts);}; require('\\''./tests/js/lineshape_parity.test.js'\\''); require('\\''./tests/js/lineshape_roundtrip.test.js'\\'');' | tail -n 16" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 2934ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
worst [
  {
    "n": 3,
    "x": [
      -0.05,
      0,
      0.05
    ],
    "amplitude": 1,
    "center": 50,
    "alpha": 0.49,
    "beta": 0.05,
    "m_gauss": 0.001,
    "err": 293858473191024500,
    "js": [
      0.9969845571283097,
      0.9984903863760375,
      1
    ],
    "py": [
      292972359752754600,
      293414860436378400,
      293858473191024500
    ]
  },
  {
    "n": 3,
    "x": [
      -0.05,
      0,
      0.05
    ],
    "amplitude": 1,
    "center": 6,
    "alpha": 0.25,
    "beta": 0.05,
    "m_gauss": 0.001,
    "err": 187452880342391700,
    "js": [
      0.9712557228716205,
      0.9854631976560123,
      1
    ],
    "py": [
      182064682801317060,
      184727914872043200,
      187452880342391700
    ]
  },
  {
    "n": 3,
    "x": [
      -0.05,
      0,
      0.05
    ],
    "amplitude": 1,
    "center": 50,
    "alpha": 0,
    "beta": 2,
    "m_gauss": 0.001,
    "err": 34100212036656070,
    "js": [
      0.9960143523173075,
      0.9980041932907336,
      1
    ],
    "py": [
      33964300605572844,
      34032154604685948,
      34100212036656070
    ]
  },
  {
    "n": 3,
    "x": [
      -0.05,
      0,
      0.05
    ],
    "amplitude": 1,
    "center": 10,
    "alpha": 0,
    "beta": 0.05,
    "m_gauss": 0.001,
    "err": 26054691174569220,
    "js": [
      0.9801990000494969,
      0.9900252493687554,
      1
    ],
    "py": [
      25538782235911200,
      25794802127328788,
      26054691174569220
    ]
  },
  {
    "n": 1,
    "x": [
      0
    ],
    "amplitude": 1,
    "center": 10,
    "alpha": 0.25,
    "beta": 0.05,
    "m_gauss": 0.001,
    "err": 17242501328460568,
    "js": [
      1
    ],
    "py": [
      17242501328460570
    ]
  },
  {
    "n": 3,
    "x": [
      -0.05,
      0,
      0.05
    ],
    "amplitude": 1,
    "center": 50,
    "alpha": 0.25,
    "beta": 0.05,
    "m_gauss": 0.001,
    "err": 14698833563451640,
    "js": [
      0.99650611989467,
      0.9982506579081339,
      1
    ],
    "py": [
      14647477601292734,
      14673120275197764,
      14698833563451640
    ]
  },
  {
    "n": 1,
    "x": [
      0
    ],
    "amplitude": 1,
    "center": 50,
    "alpha": 0.49,
    "beta": 0.05,
    "m_gauss": 0.001,
    "err": 13759065129117248,
    "js": [
      1
    ],
    "py": [
      13759065129117248
    ]
  },
  {
    "n": 1,
    "x": [
      0
    ],
    "amplitude": 1,
    "center": 6,
    "alpha": 0,
    "beta": 0.05,
    "m_gauss": 0.001,
    "err": 10197734475317512,
    "js": [
      1
    ],
    "py": [
      10197734475317512
    ]
  }
]
within centre zero [
  {
    "n": 6,
    "x": [
      -3,
      -2.9,
      -2.8,
      0,
      2,
      3
    ],
    "amplitude": 1,
    "center": 0,
    "alpha": 0.25,
    "beta": 0.05,
    "m_gauss": 0.05,
    "err": 0.0002894310819680501,
    "js": [
      0.013380989270880725,
      0.01407037918326,
      0.017624012659971943
    ],
    "py": [
      0.013380989270880743,
      0.014070379183260017,
      0.017624012659971953
    ]
  },
  {
    "n": 200,
    "x": [
      -4.9750000000000005,
      4.9750000000000005
    ],
    "amplitude": 1,
    "center": 0,
    "alpha": 0.49,
    "beta": 2,
    "m_gauss": 4,
    "err": 3.1086244689504383e-15,
    "js": [
      0.22887271573272444,
      0.23250512104429835,
      0.23621704191997628
    ],
    "py": [
      0.22887271573272439,
      0.23250512104429838,
      0.2362170419199763
    ]
  },
  {
    "n": 30,
    "x": [
      -0.7250000000000001,
      0.7250000000000001
    ],
    "amplitude": 1,
    "center": 0,
    "alpha": 0,
    "beta": 2,
    "m_gauss": 4,
    "err": 2.6645352591003757e-15,
    "js": [
      0.9649596977270846,
      0.9697036123529177,
      0.9741230449628102
    ],
    "py": [
      0.964959697727085,
      0.9697036123529191,
      0.9741230449628099
    ]
  },
  {
    "n": 200,
    "x": [
      -4.9750000000000005,
      4.9750000000000005
    ],
    "amplitude": 1,
    "center": 0,
    "alpha": 0,
    "beta": 0.05,
    "m_gauss": 4,
    "err": 2.55351295663786e-15,
    "js": [
      0.01925445266327328,
      0.02066591168522913,
      0.02217954542422317
    ],
    "py": [
      0.01925445266327333,
      0.020665911685229126,
      0.022179545424223204
    ]
  },
  {
    "n": 30,
    "x": [
      -0.7250000000000001,
      0.7250000000000001
    ],
    "amplitude": 1,
    "center": 0,
    "alpha": 0.49,
    "beta": 0.05,
    "m_gauss": 4,
    "err": 2.3314683517128287e-15,
    "js": [
      0.7714874915379059,
      0.7888993964474644,
      0.8061633832516846
    ],
    "py": [
      0.7714874915379057,
      0.7888993964474637,
      0.806163383251683
    ]
  }
]

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();

for(const step of [.1,.05,.02,.01,.005,.001]) {
 const x=Array.from({length:Math.round(10/step)+1},(_,i)=>280+step*i);
 const p={shape:'\\''DSG_LA'\\'',center:285,amplitude:1,laAlpha:.49,laBeta:2,laM:4};
 const ts=[];for(let i=0;i<3;i++){let t=performance.now();ev(x,p);ts.push(performance.now()-t);}
 console.log(JSON.stringify({step,n:x.length,ms:ts}));
}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
codex
I found a parity failure in the convolution’s boundary handling. The sum uses circular kernel indices but omits source samples across the array boundary. That changes the centre normalisation when the centre lies near or beyond a padded edge; a nonuniform grid also produces a measurable mismatch at a data point.

The suite initially hit Python temporary-directory errors in this read-only sandbox. I’m rerunning the focused tests with an in-memory import workaround and isolating the failing cases.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();

const cases=[];
for(const n of [1,2,200]) for(const m of [.05,.4,4]) for(const center of [-50,-10,0,10,50]) cases.push({x:Array.from({length:n},(_,i)=>(i-(n-1)/2)*.05),shape:'\\''ds_g'\\'',params:{amplitude:1,center,alpha:.25,beta:.05,m_gauss:m}});
cases.push({x:[-3,-2.9,-2.8,0,2,3],shape:'\\''ds_g'\\'',params:{amplitude:1,center:0,alpha:.25,beta:.05,m_gauss:.05}});
const yy=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'','\\''import tempfile,runpy,warnings; tempfile.tempdir=\"/tmp\"; warnings.filterwarnings(\"ignore\"); runpy.run_path(\"tests/js/lineshape_parity_backend.py\",run_name=\"__main__\")'\\''],{input:JSON.stringify(cases),encoding:'\\''utf8'\\'',maxBuffer:32*1024*1024,stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''pipe'\\'']}));
for(let i=0;i<cases.length;i++){const c=cases[i],p=c.params,j=ev(c.x,{shape:'\\''DSG_LA'\\'',amplitude:1,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss}), err=Math.max(...j.map((v,k)=>Math.abs(v-yy[i][k])));if((c.x.length===200&&p.m_gauss===.4)||c.x.length===6||(p.center===0))console.log(JSON.stringify({n:c.x.length,...p,err,js:[j[0],j.at(-1)],py:[yy[i][0],yy[i].at(-1)]}));}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 1996ms:
{"n":1,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":0.05,"err":0,"js":[1,1],"py":[1,1]}
{"n":1,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":0.4,"err":0,"js":[1,1],"py":[1,1]}
{"n":1,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":4,"err":0,"js":[1,1],"py":[1,1]}
{"n":2,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":0.05,"err":2.220446049250313e-16,"js":[1.0233517604965536,0.9766482395034459],"py":[1.0233517604965534,0.9766482395034459]}
{"n":2,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":0.4,"err":0,"js":[0.9793071074091405,1.0206928925908587],"py":[0.9793071074091405,1.0206928925908587]}
{"n":2,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":4,"err":0,"js":[0.9962819657351798,1.00371803426482],"py":[0.9962819657351798,1.00371803426482]}
{"n":200,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":0.05,"err":1.1102230246251565e-16,"js":[0.00030974602704906103,0.028907996164099097],"py":[0.0003097460270490896,0.028907996164099135]}
{"n":200,"amplitude":1,"center":-50,"alpha":0.25,"beta":0.05,"m_gauss":0.4,"err":74.59707500309611,"js":[335.89185261757393,288.95543069075256],"py":[261.2947776144778,224.78230541899575]}
{"n":200,"amplitude":1,"center":-10,"alpha":0.25,"beta":0.05,"m_gauss":0.4,"err":5.580260129335485,"js":[123.18988303630219,54.113435473668666],"py":[117.6096229069667,51.662202961774014]}
{"n":200,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":0.4,"err":4.440892098500626e-16,"js":[0.0006120655932857043,0.05696587062325305],"py":[0.0006120655932856832,0.056965870623253076]}
{"n":200,"amplitude":1,"center":10,"alpha":0.25,"beta":0.05,"m_gauss":0.4,"err":0.4068117538343614,"js":[7.173589815614611,48.84300469105817],"py":[7.113841225767661,48.43619293722381]}
{"n":200,"amplitude":1,"center":50,"alpha":0.25,"beta":0.05,"m_gauss":0.4,"err":172.0789141611029,"js":[347.07262749872416,491.9572339873149],"py":[225.67207324534095,319.878319826212]}
{"n":200,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":4,"err":1.887379141862766e-15,"js":[0.014124506552691348,0.3164509666336354],"py":[0.014124506552691431,0.3164509666336355]}
{"n":6,"amplitude":1,"center":0,"alpha":0.25,"beta":0.05,"m_gauss":0.05,"err":0.0002894310819680501,"js":[0.013380989270880725,0.37552624251332206],"py":[0.013380989270880743,0.3758156735952901]}

 succeeded in 43000ms:
{"step":0.02,"n":501,"ms":[35.37664000000001,35.995761,33.859421]}
{"step":0.01,"n":1001,"ms":[143.942525,147.557433,137.45831700000002]}
{"step":0.005,"n":2001,"ms":[552.119419,553.4696329999999,578.6379070000003]}
{"step":0.001,"n":10001,"ms":[13566.93023,13495.862476,13719.287436999999]}

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '4220,4286p'; nl -ba tests/js/lineshape_parity.test.js | sed -n '400,431p'; sed -n '8320,8358p' templates/index.html; rg -n 'step.*0\\.0|step.*min|decimat|downsampl|resampl' parsing.py app.py templates/index.html | head -n 55" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
  4220	  let step = 0.05;
  4221	  if (N > 1) {
  4222	    const d = new Array(N - 1);
  4223	    for (let i = 1; i < N; i++) d[i - 1] = Math.abs(beArr[i] - beArr[i - 1]);
  4224	    d.sort((u, v) => u - v);
  4225	    const n = d.length;
  4226	    step = n % 2 ? d[(n - 1) / 2] : 0.5 * (d[n / 2 - 1] + d[n / 2]);
  4227	  }
  4228	  step = Math.max(step, 1e-6);
  4229	  const padEv = Math.max(10 * m, 20 * b);
  4230	  const nPad = Math.max(Math.ceil(padEv / step), 1);
  4231	  const asc = N > 1 ? beArr[N - 1] > beArr[0] : true;
  4232	  const lo = (asc ? beArr[0] : beArr[N - 1]) - nPad * step;
  4233	  const hi = (asc ? beArr[N - 1] : beArr[0]) + nPad * step;
  4234	  const nTot = N + 2 * nPad;
  4235	  const xp = new Float64Array(nTot);
  4236	  const dxLin = (hi - lo) / (nTot - 1);
  4237	  for (let i = 0; i < nTot; i++) xp[i] = lo + i * dxLin;
  4238	  xp[nTot - 1] = hi;                                   // np.linspace sets the endpoint exactly
  4239	  const ds = new Float64Array(nTot);
  4240	  for (let i = 0; i < nTot; i++) { const v = laCasaXPSCore(xp[i] - center, a, b); ds[i] = Number.isFinite(v) ? v : 0; }
  4241	  if (nPad > 1) {
  4242	    for (let k = 0; k < nPad; k++) {
  4243	      const th = Math.PI * k / (nPad - 1);                // np.linspace(0, π, nPad)[k]
  4244	      ds[k] *= 0.5 * (1 - Math.cos(th));
  4245	      ds[nTot - nPad + k] *= 0.5 * (1 + Math.cos(th));
  4246	    }
  4247	  }
  4248	  const sigma = m / (2 * Math.sqrt(2 * Math.LN2));
  4249	  const kHalf = (nTot - 1) / 2;
  4250	  const kernel = new Float64Array(nTot);
  4251	  let ksum = 0;
  4252	  for (let t = 0; t < nTot; t++) { const kg = (t - kHalf) * step; kernel[t] = Math.exp(-0.5 * (kg / sigma) * (kg / sigma)); ksum += kernel[t]; }
  4253	  for (let t = 0; t < nTot; t++) kernel[t] /= ksum;
  4254	  const fl = Math.floor(nTot / 2);                        // np.fft.ifftshift's shift
  4255	  const W = Math.ceil(8 * sigma / step) + 1;              // the kernel's support in samples
  4256	  const conv = new Float64Array(nTot);
  4257	  for (let i = 0; i < nTot; i++) {
  4258	    let acc = 0;
  4259	    const j0 = Math.max(0, i - W), j1 = Math.min(nTot - 1, i + W);
  4260	    for (let j = j0; j <= j1; j++) {
  4261	      let t = (i - j + fl) % nTot; if (t < 0) t += nTot;
  4262	      acc += ds[j] * kernel[t];
  4263	    }
  4264	    conv[i] = acc;
  4265	  }
  4266	  // np.interp(query, xp, conv): xp ascending; clamped outside; linear inside
  4267	  const interp = q => {
  4268	    if (q <= xp[0]) return conv[0];
  4269	    if (q >= xp[nTot - 1]) return conv[nTot - 1];
  4270	    let lo2 = 0, hi2 = nTot - 1;
  4271	    while (hi2 - lo2 > 1) { const mid = (lo2 + hi2) >> 1; if (xp[mid] <= q) lo2 = mid; else hi2 = mid; }
  4272	    const x0 = xp[lo2], x1 = xp[hi2];
  4273	    const tt = x1 !== x0 ? (q - x0) / (x1 - x0) : 0;
  4274	    return conv[lo2] + tt * (conv[hi2] - conv[lo2]);
  4275	  };
  4276	  const out = new Array(N);
  4277	  for (let i = 0; i < N; i++) out[i] = interp(beArr[i]);
  4278	  let peakVal = interp(center);
  4279	  if (!(peakVal > 0)) { let mx = 0; for (let i = 0; i < N; i++) mx = Math.max(mx, Math.abs(out[i])); peakVal = mx; }
  4280	  if (!(peakVal > 0)) return new Array(N).fill(0);
  4281	  for (let i = 0; i < N; i++) { const v = out[i] / peakVal; out[i] = Number.isFinite(v) ? v : 0; }
  4282	  return out;
  4283	}
  4284	
  4285	// Compute per-peak intensities across an array of BE values. Special-cases
  4286	// LACX with non-zero m so the Gaussian convolution sees the whole grid, and
   400	// acquisitions), a centre half a step off-grid, a short window, and a
   401	// window narrower than the pad — every case at the 1e-6 tolerance.
   402	function gridOf(center, step, n, { descending = false, offset = 0 } = {}) {
   403	  const x = [];
   404	  for (let i = 0; i < n; i++) x.push(center - (step * n) / 2 + step * i + offset);
   405	  return descending ? x.reverse() : x;
   406	}
   407	const DSG_GRID_CASES = [
   408	  { label: 'step 0.1 eV, 120 pts', step: 0.1, n: 120 },
   409	  { label: 'step 0.02 eV, 500 pts', step: 0.02, n: 500 },
   410	  { label: 'step 0.05 eV, descending', step: 0.05, n: 200, descending: true },
   411	  { label: 'step 0.05 eV, centre half a step off-grid', step: 0.05, n: 200, offset: 0.025 },
   412	  { label: 'step 0.1 eV, descending, centre 0.03 eV off-grid', step: 0.1, n: 120, descending: true, offset: 0.03 },
   413	  { label: 'short window: 30 pts at 0.1 eV (narrower than the pad)', step: 0.1, n: 30 },
   414	  { label: 'irregular-ish step 0.0503 eV (median step), 181 pts', step: 0.0503, n: 181 },
   415	];
   416	const DSG_BOX = { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] };
   417	for (const g of DSG_GRID_CASES) {
   418	  test(`(D′) DS+G convolution converges on another grid: ${g.label}`, () => {
   419	    const cases = combos(DSG_BOX).map(c => ({ c, p: { ...basePeak('DSG_LA'), ...c } }));
   420	    const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: gridOf(k.p.center, g.step, g.n, g) }; });
   421	    const beYs = backendEvalMany(specs);
   422	    const worst = cases.map((k, i) => ({ c: k.c, rel: maxRelDiff(evalPeakArray(specs[i].x, k.p), beYs[i], k.p.amplitude) })).sort((a, b) => b.rel - a.rel);
   423	    assert.ok(worst[0].rel < TIGHT_TOL,
   424	      `${g.label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} combinations diverge; worst ${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
   425	  });
   426	}

  // KNOWN LIMITATION: this engine produces no parameter uncertainties; the
  // results panel shows blank sigma for every parameter after a local fit.
  const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
                      engine: 'local', status: 'converged',
                      objective: 'poisson_weighted_chi_square', weighting: '1/sqrt(max(counts,1))', iterations,
                      reportable: false, caveat: _LOCAL_FIT_CAVEAT };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  _applyStatDisplay(state.fitResult);
  document.getElementById('sb-msg').textContent = 'Fit complete (local)';
  _updateRFactorUI(state.fitResult.rFactor);
  _updateROIDisplay(roiRange);

  renderPeakList();
  updatePlot();
  renderResults();

  _hideFitSpinner();
  notify('Local fit converged in ' + iterations + ' iteration' + (iterations === 1 ? '' : 's') +
         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
  _autoSnapshot();
  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };
}

function solveLinear(A, b, n) {
  const M = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(M[row][col]) > Math.abs(M[maxRow][col])) maxRow = row;
    }
    [M[col], M[maxRow]] = [M[maxRow], M[col]];
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(M[col][col]) < 1e-15) continue;
      const f = M[row][col] / M[col][col];
      for (let k = col; k <= n; k++) M[row][k] -= f * M[col][k];
rg: parsing.py: No such file or directory (os error 2)
app.py:50:# Upper bound on the Monte-Carlo uncertainty resampling count accepted by
app.py:53:# Adjust here if more resampling is ever needed.
app.py:610:            # Return a downsampled preview (max 2000 points) to keep payload small
app.py:1125:    """Return (possibly downsampled) energy/counts lists for API responses."""
app.py:1129:    # Uniform stride downsample (preserves endpoints)
app.py:1134:        "downsampled": True,
templates/index.html:1974:              <input type="number" id="cc-obs" value="284.8" step="0.05" oninput="_onCCObsInput()">
templates/index.html:1978:              <input type="number" id="cc-lit" value="284.8" step="0.05" oninput="updateChargeCorrection()">
templates/index.html:4220:  let step = 0.05;
templates/index.html:6045:        <input type="number" id="pk-center-${p.id}" value="${p.center.toFixed(3)}" step="0.05"
templates/index.html:6053:        <input type="number" id="pk-fwhm-${p.id}" value="${p.fwhm.toFixed(3)}" step="0.05" min="0.1"
templates/index.html:6074:        <input type="number" value="${p.linkOffset.toFixed(2)}" step="0.05"
templates/index.html:6079:        <input type="number" value="${p.linkRatio.toFixed(3)}" step="0.05" min="0.01" max="2"
templates/index.html:6095:        <input type="number" value="${p.asymmetry.toFixed(3)}" step="0.01" min="0" max="1"
templates/index.html:6126:        <input type="number" value="${p.dsAlpha.toFixed(3)}" step="0.005" min="0" max="0.5"
templates/index.html:6133:        <input type="number" value="${p.dsGamma.toFixed(4)}" step="0.001" min="0"
templates/index.html:6147:          <input type="number" value="${p.laAlpha.toFixed(3)}" step="0.005" min="0" max="0.5"
templates/index.html:6154:          <input type="number" value="${p.laBeta.toFixed(3)}" step="0.01" min="0.05" max="2.0"
templates/index.html:6162:        <input type="number" value="${p.laM.toFixed(3)}" step="0.01" min="0.05" max="4.0"
templates/index.html:6176:          <input type="number" value="${(p.caAlpha ?? 1.0).toFixed(3)}" step="0.05" min="0.1" max="5.0"
templates/index.html:6183:          <input type="number" value="${(p.caBeta ?? 1.0).toFixed(3)}" step="0.05" min="0.1" max="5.0"
templates/index.html:6191:        <input type="number" value="${Math.round(p.caM ?? 50)}" step="1" min="0" max="499"
templates/index.html:8597:      <td><input type="number" value="${useRSF.toFixed(3)}" step="0.001" min="0.001" style="width:62px;font-size:11px;padding:2px 4px" onchange="onRSFInputChange(${p.id},this.value)" id="rsf-${p.id}"></td>
templates/index.html:10850:    for (let t = first; t <= hi + step * 0.01; t = Math.round((t + step) * 1e10) / 1e10)

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();

const circular=new Function(block.replace('\\''const j0 = Math.max(0, i - W), j1 = Math.min(nTot - 1, i + W);'\\'','\\''const j0 = 0, j1 = nTot - 1;'\\'')+'\\''; return evalPeakArray;'\\'')();
for(const c of [{x:Array.from({length:200},(_,i)=>(i-99.5)*.05),center:10,m:.4},{x:[-3,-2.9,-2.8,0,2,3],center:0,m:.05}]) {
 const p={shape:'\\''DSG_LA'\\'',amplitude:1,center:c.center,laAlpha:.25,laBeta:.05,laM:c.m};
 console.log(JSON.stringify({center:c.center,n:c.x.length,original:ev(c.x,p).at(-1),fullCircular:circular(c.x,p).at(-1)}));
}
const step=.05,x=Array.from({length:200},(_,i)=>280+i*step);
for(const key of ['\\''laM'\\'','\\''laBeta'\\'']) {const p={shape:'\\''DSG_LA'\\'',center:285,amplitude:1,laAlpha:.25,laBeta:.05,laM:.4};if(key==='\\''laBeta'\\'')p.laBeta=.7;const a=ev(x,{...p,[key]:p[key]-1e-10}), b=ev(x,{...p,[key]:p[key]+1e-10}); console.log('\\''grid-boundary jump'\\'',key,Math.max(...a.map((v,i)=>Math.abs(v-b[i]))));}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
{"center":10,"n":200,"original":48.84300469105817,"fullCircular":48.43619293722327}
{"center":0,"n":6,"original":0.37552624251332206,"fullCircular":0.37581567359529017}
grid-boundary jump laM 0.0000024012902816866744
grid-boundary jump laBeta 1.9265107906174528e-7

exec
/bin/zsh -lc "rg -n 'evalPeak\\b|laCasaXPS\\b' static templates --glob '*.js' --glob '*.html'; sed -n '5848,5880p' templates/index.html; rg -n 'DSG_LA|DS\\+G' tests/js/local_lm_descent.test.js; nl -ba docs/findings/2026-09-fit-determinacy.md | sed -n '337,354p'; nl -ba docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md | sed -n '55,66p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
templates/index.html:4045:function laCasaXPS(x, center, alpha, beta, mGauss) {
templates/index.html:4119:function evalPeak(x, p) {
templates/index.html:4136:    // laCasaXPS already returns a normalised [0,1] value. α is clipped as
templates/index.html:4139:    y = laCasaXPS(x, center, _dsgAlpha(p.laAlpha), p.laBeta, p.laM);
templates/index.html:4305:  return beArr.map(x => evalPeak(x, p));
templates/index.html:5140:// here matching defaultPeak, then update evalPeak / renderShapeControls /
templates/index.html:5179:// ones evalPeak reads for shape A — to their originals, so the rendered curve
templates/index.html:6291:    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
templates/index.html:8386:  // evalPeakArray(), not a per-point evalPeak map: for LACX with caM > 0,
templates/index.html:8388:  // evalPeak silently returns the unconvolved base regardless of caM.
templates/index.html:10056:  // Per-peak curves and areas. evalPeakArray(), not per-point evalPeak:
templates/index.html:10058:  // Gaussian convolution — evalPeak silently ignores caM. These curves
templates/index.html:10723:  // evalPeakArray() per peak, once, not per-point evalPeak per row: for
templates/index.html:10725:  // Gaussian convolution — evalPeak silently ignores caM, which would
templates/index.html:10873:      // evalPeakArray(), not per-point evalPeak: applies Gaussian
templates/index.html:10874:      // convolution for LACX with caM > 0, which evalPeak ignores.
templates/index.html:10905:      // evalPeakArray(), not per-point evalPeak: applies Gaussian
templates/index.html:10906:      // convolution for LACX with caM > 0, which evalPeak ignores.
templates/index.html:11004:      // evalPeakArray(), not per-point evalPeak: see fill/outline loops above.
templates/index.html:11130:// columns — read ONLY the ACTIVE shape's params (matching evalPeak /

    // Forward-propagate from parent to all children (including p if it is one)
    for (const child of state.peaks.filter(q => q.linked === parent.id)) {
      if (key === 'center') child.center = parent.center + child.linkOffset;
      else if (key === 'amplitude') child.amplitude = parent.amplitude * child.linkRatio;
      else child[key] = parent[key];
      if (child.id !== id) renderPeakControls(child);
    }
  }
  _invalidateFittedY();
  updatePlot();
}

function toggleLock(id, key, btn) {
  const p = getPeak(id);
  if (!p) return;
  p[key] = !p[key];
  btn.className = 'lock-btn' + (p[key] ? ' locked' : '');
  btn.innerHTML = p[key] ? '&#x1f512;' : '&#x1f513;';
  btn.title = (p[key] ? 'Unlock' : 'Lock') + ' during fitting';
  _updateLockAllBtn();
  _refreshStartsEvidence(true);      // a lock is part of the fitted model
}

const LOCK_ALL_KEYS = ['fixCenter', 'fixFwhm', 'fixAmplitude', 'fixAsymmetry', 'fixGlMix', 'fixDsAlpha', 'fixDsGamma'];

function _lockAllStats() {
  let locked = 0, total = 0;
  for (const p of state.peaks) {
    if (p.linked) continue;
    for (const k of LOCK_ALL_KEYS) {
      total++;
      if (p[k]) locked++;
276:  if (!p.fixFwhm && p.shape !== 'DSG_LA') out.push('fwhm');
281:  if (p.shape === 'DSG_LA') { if (!p.fixLaAlpha) out.push('laAlpha'); if (!p.fixLaBeta) out.push('laBeta'); if (!p.fixLaM) out.push('laM'); }
   337	area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
   338	the 530 peak records in the seven committed projects use DS+G (and none of
   339	the 202 measurement targets), so no saved figure is affected; it is the
   340	fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
   341	FIXED the same day in `fix-dsg-page-evaluator` after the owner asked whether
   342	Find Peaks emits DS+G: it does (every A- and M-family C 1s candidate's
   343	graphitic main line, β fixed at 0.05, α 0–0.3, m 0.4–1.8), and on that box
   344	the page's area was 5–21 % low for α 0.15–0.3. `dsgConvolved_array` mirrors
   345	the server's padded-grid convolution to ≤ 3e-15 of amplitude across the
   346	whole β/m box on seven grids; nothing changed in Find Peaks or the dropdown
   347	(a science decision is not altered to work around a rendering bug —
   348	owner, 2026-09-22). The general lesson repeats §6's: a harness that
   349	evaluates one representative point per shape proves nothing about the range
   350	the optimiser can reach.
    55	DS+G component converges in 69 ms.
    56	
    57	## 3. Acceptance (measured)
    58	
    59	| check | result |
    60	|---|---|
    61	| parity sweep (D), DS+G box α {0, 0.25, 0.49} × β {0.05, 0.7, 2} × m {0.001, 0.05, 0.4, 2, 4}, base grid | ≤ 3e-15 of amplitude (was 1e52 at β 2, m 0.05) — now a hard assertion |
    62	| (D′) the same box on: 0.1 eV step; 0.02 eV step; descending grid; centre half a step off-grid; descending + 0.03 eV off-grid; a 30-point window narrower than the pad; a 0.0503 eV step | < 1e-6 on every combination — hard assertions |
    63	| (A) DS+G at the base peak (was todo) | hard, passes |
    64	| round trip page → server → page, DS+G (was todo), and DS+G m locked at 0.05 and at 4 (curve comparison was disabled) | hard, pass |
    65	| (B) scalar vs array evaluator, DS+G | now `todo` like LACX: the convolution is a grid operation; guard (C) holds |
    66	| Find Peaks box (β 0.05, α 0–0.3, m 0.4–1.8, 0.05 and 0.1 eV grids) | agrees with the server to 1e-6 (was 5–21 % low in area) |

 succeeded in 116133ms:
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
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
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
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
ok 75 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1590.042408
  type: 'test'
  ...
1..75
# tests 75
# suites 0
# pass 70
# fail 0
# cancelled 0
# skipped 0
# todo 5
# duration_ms 116185.230606

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\'');
const path=require('\\''path'\\'');
let src=fs.readFileSync('\\''tests/js/local_lm_descent.test.js'\\'','\\''utf8'\\'').split('\\''// ── Committed lab project'\\'')[0];
src=src.replace(\"const { test } = require('\\''node:test'\\'');\",\"\").replace(\"path.join(__dirname, '\\''../..'\\'')\",\"process.cwd()\");
const env=new Function('\\''require'\\'',src+'\\'';return makeEnv();'\\'')(require);
for(const step of [.05,.02,.01]) {
 const x=Array.from({length:Math.round(10/step)+1},(_,i)=>280+i*step);
 const p={id:1,shape:'\\''DSG_LA'\\'',center:285,amplitude:10000,fwhm:1,laAlpha:.25,laBeta:2,laM:4,fixCenter:false,fixAmplitude:false,fixLaAlpha:false,fixLaBeta:false,fixLaM:false};
 const y=env.evalPeakArray(x,{...p,amplitude:11000,center:285.1,laBeta:1.9,laM:3.9});env.state.peaks=[{...p}];
 let t=performance.now();const r=env.runFitLocal(x,y,x.map(()=>0),{maxIterations:1}); console.log(JSON.stringify({step,ms:performance.now()-t,result:r}));
}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 1881ms:
{"step":0.05,"ms":67.32523300000001,"result":{"success":false,"engine":"local","message":"iteration limit (1) reached.","iterations":1}}
{"step":0.02,"ms":344.68297300000006,"result":{"success":false,"engine":"local","message":"iteration limit (1) reached.","iterations":1}}
{"step":0.01,"ms":1347.6284339999997,"result":{"success":false,"engine":"local","message":"iteration limit (1) reached.","iterations":1}}

codex
Including the omitted circular terms makes both failing cases agree with NumPy again. On a 200-point grid with a free centre beyond the padded range, the current page differs by `0.4068 × amplitude`. On the nonuniform grid, the error is `2.894e-4 × amplitude`, above the required `1e-6`.

The 75 focused parity and round-trip tests pass with 5 expected todos. Performance also needs attention: at β=2/m=4, one evaluation takes about 35 ms at 0.02 eV spacing, 140 ms at 0.01 eV, and 13.5 seconds at 0.001 eV, all synchronously.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();

const gs=[{step:.05,n:200},{step:.1,n:120},{step:.02,n:500},{step:.05,n:200,desc:true},{step:.05,n:200,offset:.025},{step:.1,n:120,desc:true,offset:.03},{step:.1,n:30},{step:.0503,n:181}],cases=[];
gs.forEach((g,gi)=>{for(const alpha of [0,.25,.49]) for(const beta of [.05,.7,2]) for(const m of [.001,.05,.4,2,4]) {let x=Array.from({length:g.n},(_,i)=>391.8-g.step*g.n/2+g.step*i+(g.offset||0));if(g.desc)x.reverse();cases.push({gi,x,shape:'\\''ds_g'\\'',params:{amplitude:17794,center:391.8,alpha,beta,m_gauss:m}});}});
const yy=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'','\\''import tempfile,runpy,warnings; tempfile.tempdir=\"/tmp\"; warnings.filterwarnings(\"ignore\"); runpy.run_path(\"tests/js/lineshape_parity_backend.py\",run_name=\"__main__\")'\\''],{input:JSON.stringify(cases),encoding:'\\''utf8'\\'',maxBuffer:32*1024*1024,stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''pipe'\\'']}));
const stats=gs.map(g=>({g,max:0,zeroAtThreshold:0}));
cases.forEach((c,i)=>{const p=c.params,j=ev(c.x,{shape:'\\''DSG_LA'\\'',amplitude:p.amplitude,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss});stats[c.gi].max=Math.max(stats[c.gi].max,...j.map((v,k)=>Math.abs(v-yy[i][k])/p.amplitude));if(p.m_gauss===.001&&j.every(v=>v===0))stats[c.gi].zeroAtThreshold++;});console.log(JSON.stringify(stats));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc "sed -n '8780,8868p' templates/index.html; rg -n 'preview.*peak|peak.*preview|individual_peaks|runFitLocal' templates/index.html | tail -n 32; sed -n '919,933p' fitting.py; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
//
// Returns empty arrays if source isn't available or has no fit.
// Align src.rawIntensity to a fit-time `be` array (Path A/A2). fr.be is
// a contiguous slice of corrBE at fit time; if ccShift hasn't drifted,
// we can find the matching window in current rawBE by locating the
// index where (rawBE - shift) is closest to be[0]. Returns rawIntensity
// slice of length matching `be` (or shorter if data runs out).
function _alignRawToFitBe(src, be) {
  if (!Array.isArray(src.rawBE) || !Array.isArray(src.rawIntensity)
      || src.rawBE.length === 0 || !be || be.length === 0) return [];
  const shift = src.ccShift || 0;
  const target = be[0];
  let i0 = 0;
  let minDiff = Math.abs((src.rawBE[0] - shift) - target);
  for (let i = 1; i < src.rawBE.length; i++) {
    const d = Math.abs((src.rawBE[i] - shift) - target);
    if (d < minDiff) { minDiff = d; i0 = i; }
    else if (i0 > 0) break;  // rawBE is monotonic; past the closest match.
  }
  const len = Math.min(be.length, src.rawBE.length - i0);
  return src.rawIntensity.slice(i0, i0 + len);
}

function _buildEntryRenderData(entry) {
  const src = tabManager._getTab(entry.sourceTabId);
  if (!src || !Array.isArray(src.rawBE) || src.rawBE.length < 2) {
    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
  }
  const peaks = Array.isArray(src.peaks) ? src.peaks : [];
  const fr = src.fitResult;
  if (!fr || peaks.length === 0) {
    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
  }
  const shift = src.ccShift || 0;

  // be + bg + rawY
  let be, bg, rawY;
  if (Array.isArray(fr.be) && fr.be.length >= 2
      && Array.isArray(fr.bgIntensity)
      && fr.bgIntensity.length === fr.be.length) {
    // Path A/A2: fit-time be + bg both present (frozen).
    be = fr.be.slice();
    bg = fr.bgIntensity.slice();
    rawY = _alignRawToFitBe(src, be);
  } else {
    // Path B: post-load — derive ROI-window be from rawBE + ui.roiMin/Max,
    // recompute bg from raw via source's persisted bg settings.
    const corrBE = src.rawBE.map(b => b - shift);
    const roiMinV = parseFloat(src.ui && src.ui.roiMin);
    const roiMaxV = parseFloat(src.ui && src.ui.roiMax);
    let i0 = 0, i1 = corrBE.length - 1;
    if (isFinite(roiMinV) && isFinite(roiMaxV)) {
      const lo = Math.min(roiMinV, roiMaxV);
      const hi = Math.max(roiMinV, roiMaxV);
      // corrBE is descending (highest BE first); locate ROI bounds.
      while (i0 < corrBE.length && corrBE[i0] > hi) i0++;
      while (i1 >= 0 && corrBE[i1] < lo) i1--;
      if (i1 < i0) { i0 = 0; i1 = corrBE.length - 1; }
    }
    be = corrBE.slice(i0, i1 + 1);
    rawY = src.rawIntensity.slice(i0, i1 + 1);
    bg = _computeBackgroundForSource(be, rawY, src.ui);
  }

  // Envelope (raw-level)
  let fittedY;
  if (Array.isArray(fr.fittedY) && fr.fittedY.length === be.length) {
    // Path A: backend fittedY directly (already raw-level).
    fittedY = fr.fittedY.slice();
  } else {
    // Path A2/B: compose envelope from peaks + bg.
    const model = evalAllPeaks(be, peaks);
    fittedY = model.map((v, i) => v + bg[i]);
  }

  // Per-peak curves. peakOnly = pure peak shape (bg-subtracted level);
  // y = peakOnly + bg (raw level). Both kept so Bkgrd Sub view can
  // pick the appropriate one without recomputing.
  const peakCurves = peaks.map(p => {
    const peakOnly = evalPeakArray(be, p);
    return { peak: p, peakOnly, y: peakOnly.map((v, i) => v + bg[i]) };
  });

  return { be, bg, rawY, fittedY, peaks: peakCurves };
}

// Cached wrapper around _buildEntryRenderData. Stored on the entry as
// entry._renderDataCache. Slider drags and other in-place updates hit
// the cache; _renderStackChart clears all entry caches before rebuild,
6291:    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
6378:  for (const ipeak of result.individual_peaks) {
6933:// curve individual_peaks[].y, the server's weights 1/max(counts, 1)):
7009:  const ip = ((json && json.individual_peaks) || []).find(q => String(q.id) === String(peakId));
7089:  const ip = ((json && json.individual_peaks) || []).find(q => String(q.id) === String(gPeak.id));
7831:      const local = runFitLocal(be, bgSubtracted, bgIntensity);
7989:function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
8378:  const peaks = fitResult?.backendResult?.individual_peaks;
9307:  // Before fitting, they come from the current ROI so live peak previews still work.
10282:    console.info('[migration] Migrated ' + counts['DSG->DS'] + " peaks from 'DSG' → 'DS' (DSG's Gaussian-broadening preview was cosmetic only and did not affect fits; loading as DS shows the curve that was actually being fit).");
11383:  if (!state.fitResult?.backendResult?.individual_peaks) return { warnings: [], info: [] };
11948:    const outcome = runFitLocal(be, bgSub, bgI);
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BTMc2bA4' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sL55CCgE' (errno=Operation not permitted)
?? docs/autofit/codex/dsg_page_evaluator_review_prompt.txt
?? docs/autofit/codex/dsg_page_evaluator_verdict_runA.md
?? docs/autofit/codex/dsg_page_evaluator_verdict_runB.md

 succeeded in 2993ms:
[{"g":{"step":0.05,"n":200},"max":3.0667462125646675e-15,"zeroAtThreshold":9},{"g":{"step":0.1,"n":120},"max":2.3511720962995784e-15,"zeroAtThreshold":9},{"g":{"step":0.02,"n":500},"max":5.5201431826164016e-15,"zeroAtThreshold":0},{"g":{"step":0.05,"n":200,"desc":true},"max":3.0667462125646675e-15,"zeroAtThreshold":9},{"g":{"step":0.05,"n":200,"offset":0.025},"max":3.47564570757329e-15,"zeroAtThreshold":9},{"g":{"step":0.1,"n":120,"desc":true,"offset":0.03},"max":2.0444974750431117e-15,"zeroAtThreshold":9},{"g":{"step":0.1,"n":30},"max":2.0444974750431117e-15,"zeroAtThreshold":9},{"g":{"step":0.0503,"n":181},"max":2.453396970051734e-15,"zeroAtThreshold":0}]

exec
/bin/zsh -lc "sed -n '560,627p' app.py; rg -n 'rawBE =|rawBE:' templates/index.html | head -n 25; nl -ba docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md | sed -n '45,56p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
    @app.post("/api/upload")
    def upload():
        if "file" not in request.files:
            return _err("No file field in the request")
        f = request.files["file"]
        if not f.filename:
            return _err("No filename provided")

        filename = secure_filename(f.filename)
        suffix = Path(filename).suffix.lower()
        if suffix not in xps_parser.ALLOWED_EXTENSIONS:
            return _err(
                f"File type '{suffix}' not supported. "
                f"Allowed: {sorted(xps_parser.ALLOWED_EXTENSIONS)}"
            )

        # Save raw upload temporarily. Prefix with a UUID so concurrent uploads
        # of files with the same name never collide in the shared upload dir.
        tmp_path = Path(app.config["UPLOAD_FOLDER"]) / f"{uuid.uuid4().hex}_{filename}"
        f.save(str(tmp_path))

        try:
            energy, counts = xps_parser.parse_file(tmp_path)
        except ValueError as exc:
            # Our own validation (clean, user-facing): bad format, empty file,
            # too few points, "Not a valid Thermo VGD file", etc. (audit F10).
            tmp_path.unlink(missing_ok=True)
            return _err(f"Could not parse file: {exc}")
        except Exception:
            # Unexpected library/internal failure — log the detail, return generic.
            app.logger.exception("Unexpected file-parse error")
            tmp_path.unlink(missing_ok=True)
            return _err("Internal parse error — see server log for details.", 500)
        finally:
            tmp_path.unlink(missing_ok=True)

        session_id = str(uuid.uuid4())
        try:
            _save_session(session_id, app.config["UPLOAD_FOLDER"],
                          energy, counts, filename)
        except Exception:
            app.logger.exception("Failed to store session")
            return _err("Could not store the session — see server log.", 500)

        return jsonify({
            "session_id": session_id,
            "filename": filename,
            "n_points": int(len(energy)),
            "energy_range": [float(energy.min()), float(energy.max())],
            "counts_range": [float(counts.min()), float(counts.max())],
            # Return a downsampled preview (max 2000 points) to keep payload small
            **_preview(energy, counts, max_pts=2000),
        })

    # ── VGD parse (Thermo Avantage binary format) ─────────────────────────────

    @app.post("/api/parse-vgd")
    def parse_vgd_endpoint():
        """Parse a Thermo Avantage VGD file and return (be, inten) arrays.

        Accepts a multipart/form-data POST with a single 'file' field.
        Optional form fields:
          photon_energy  – X-ray source energy in eV (default 1486.6, Al Kα)
          work_function  – spectrometer WF in eV      (default 4.5)

        Returns JSON: { be: [...], inten: [...], n_points: int, be_range: [min,max] }
        """
        if "file" not in request.files:
2307:  rawBE: [],
3159:      rawBE: sortedBE,
3200:      rawBE: [], rawIntensity: [], ccShift: 0,
3226:    state.rawBE = tab.rawBE;
3296:      state.rawBE = []; state.rawIntensity = [];
3364:        rawBE: t.rawBE,
7259:  const rawBE = corrBE.map(b => b + curShift);
10096:    rawBE: tab.rawBE,
10157:      rawBE: t.rawBE, rawIntensity: t.rawIntensity,
10335:      if (!data.rawBE && data.be) data.rawBE = data.be;
10529:        rawBE: [], rawIntensity: [], ccShift: 0,
10543:      rawBE: t.rawBE || [], rawIntensity: t.rawIntensity || [],
    45	  the centre (fallbacks as the server's); non-finite → 0.
    46	
    47	`evalPeakArray` routes every DS+G through it (the delta branch inside). The
    48	scalar `evalPeak` DSG_LA branch keeps the name `laCasaXPS` but is now the
    49	normalised DS core with m ignored — the same status as its LACX branch;
    50	guard (C) of the parity harness proves no shipped caller reaches it. The
    51	old quadrature is deleted, not tuned.
    52	
    53	Cost: 0.3–1.1 ms per evaluation on a 241-point grid for Find Peaks-like
    54	parameters, 5.5 ms at the box's far corner (β 2, m 4); a local fit of a
    55	DS+G component converges in 69 ms.
    56	

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();

const oldHtml=cp.execFileSync('\\''git'\\'',['\\''show'\\'','\\''main:templates/index.html'\\''],{encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''pipe'\\'']});
const oldBlock=oldHtml.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const oldEv=new Function(oldBlock+'\\''; return evalPeakArray;'\\'')();
for(const step of [.01,.001]) {const x=Array.from({length:Math.round(10/step)+1},(_,i)=>280+i*step),p={shape:'\\''DSG_LA'\\'',center:285,amplitude:1,laAlpha:.49,laBeta:2,laM:4};const t=performance.now();oldEv(x,p);console.log(JSON.stringify({main:true,step,ms:performance.now()-t}));}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 447ms:
{"main":true,"step":0.01,"ms":47.406816000000006}
{"main":true,"step":0.001,"ms":381.96368599999994}

codex
1. **MAJOR — Circular convolution drops wrapped contributions.** [templates/index.html:4259](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/templates/index.html:4259) clips source indices to `[0,nTot−1]`; applying modulo to the kernel index does not restore omitted sources.

   Reproducer: `x[i]=(i−99.5)*0.05`, 200 points, amplitude=1, centre=10, α=0.25, β=0.05, m=0.4. The last sample is **48.8430046911** on the page versus **48.4361929372** on the server: error **0.4068 × amplitude**. DS+G centres are unbounded by default. The missing wrap changes the clamped centre normalisation, scaling every displayed/exported value incorrectly.

   This also fails with an **in-window centre**: `x=[−3,−2.9,−2.8,0,2,3]`, centre=0, α=0.25, β=m=0.05. Error is **2.8943e−4 × amplitude**. Including all circular contributions in an in-memory probe restores agreement in both cases. Sum over circular support and add these regressions.

2. **MAJOR — Fine-grid evaluations freeze the UI.** [templates/index.html:4257](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/templates/index.html:4257) performs approximately quadratic work in inverse grid spacing, synchronously, including throughout the padding.

   With a 10 eV window, α=0.49, β=2, m=4, measured evaluation times were **35 ms at 0.02 eV**, **140 ms at 0.01 eV**, and **13.5 seconds at 0.001 eV**. Main took approximately **0.38 seconds** for that last case. A chart redraw evaluates the component for both the envelope and individual curve, implying roughly **27 seconds blocked**. One local-LM iteration at 0.01 eV took **1.35 seconds**. These parameters are inside the optimiser’s bounds. The implementation needs a bounded-cost convolution strategy.

3. **MINOR — The added threshold coverage can pass on vanished curves.** [tests/js/lineshape_parity.test.js:416](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:416) includes m=0.001 but no below-threshold value in D′. On the 120-point, 0.1 eV grid, all nine α/β combinations at m=0.001 return **all zeros on both sides** because the Gaussian kernel underflows. Agreement therefore passes despite a vanished peak. This is inherited server behaviour; explicitly characterise it and test below/at/above the threshold. The “irregular-ish” grid is also uniformly spaced and misses finding 1.

The focused parity/round-trip run produced **70 passes, 0 failures, 5 todos**, using an in-memory workaround for Python’s temporary-directory discovery in this read-only environment. Ordinary tested grids agreed within approximately `5.6e−15`; caller routing and request-builder usage checked out. I agree the unchanged server’s reported 110-second restart cost belongs outside this unit.

**VERDICT: NO-GO**
tokens used
93,404
1. **MAJOR — Circular convolution drops wrapped contributions.** [templates/index.html:4259](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/templates/index.html:4259) clips source indices to `[0,nTot−1]`; applying modulo to the kernel index does not restore omitted sources.

   Reproducer: `x[i]=(i−99.5)*0.05`, 200 points, amplitude=1, centre=10, α=0.25, β=0.05, m=0.4. The last sample is **48.8430046911** on the page versus **48.4361929372** on the server: error **0.4068 × amplitude**. DS+G centres are unbounded by default. The missing wrap changes the clamped centre normalisation, scaling every displayed/exported value incorrectly.

   This also fails with an **in-window centre**: `x=[−3,−2.9,−2.8,0,2,3]`, centre=0, α=0.25, β=m=0.05. Error is **2.8943e−4 × amplitude**. Including all circular contributions in an in-memory probe restores agreement in both cases. Sum over circular support and add these regressions.

2. **MAJOR — Fine-grid evaluations freeze the UI.** [templates/index.html:4257](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/templates/index.html:4257) performs approximately quadratic work in inverse grid spacing, synchronously, including throughout the padding.

   With a 10 eV window, α=0.49, β=2, m=4, measured evaluation times were **35 ms at 0.02 eV**, **140 ms at 0.01 eV**, and **13.5 seconds at 0.001 eV**. Main took approximately **0.38 seconds** for that last case. A chart redraw evaluates the component for both the envelope and individual curve, implying roughly **27 seconds blocked**. One local-LM iteration at 0.01 eV took **1.35 seconds**. These parameters are inside the optimiser’s bounds. The implementation needs a bounded-cost convolution strategy.

3. **MINOR — The added threshold coverage can pass on vanished curves.** [tests/js/lineshape_parity.test.js:416](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:416) includes m=0.001 but no below-threshold value in D′. On the 120-point, 0.1 eV grid, all nine α/β combinations at m=0.001 return **all zeros on both sides** because the Gaussian kernel underflows. Agreement therefore passes despite a vanished peak. This is inherited server behaviour; explicitly characterise it and test below/at/above the threshold. The “irregular-ish” grid is also uniformly spaced and misses finding 1.

The focused parity/round-trip run produced **70 passes, 0 failures, 5 todos**, using an in-memory workaround for Python’s temporary-directory discovery in this read-only environment. Ordinary tested grids agreed within approximately `5.6e−15`; caller routing and request-builder usage checked out. I agree the unchanged server’s reported 110-second restart cost belongs outside this unit.

**VERDICT: NO-GO**
