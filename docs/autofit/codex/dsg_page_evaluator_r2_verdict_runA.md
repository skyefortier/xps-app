OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0cae8-64e8-7472-8ede-dbadd4e98a27
--------
user
RECHECK, round 2, of unit fix-dsg-page-evaluator: git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round 1 (docs/autofit/codex/dsg_page_evaluator_verdict_runA.md / runB.md, both NO-GO) found: (1) MAJOR the direct convolution sum clipped at the padded array's ends and omitted the wrapped contributions the server's circular FFT includes (a centre 10 eV outside a [-5, 5] window: 0.41 x amplitude; a 6-point irregular grid: 2.9e-4); (2) MAJOR quadratic cost on fine grids (13.5 s per curve at 0.001 eV; 1.35 s per local-LM iteration at 0.01 eV); (3) MINOR the "irregular-ish" grid was uniform, and the m = 0.001 case on a 0.1 eV grid passed on a curve that had vanished on both sides (the server's kernel underflows there); (4) MINOR findings §7 overstated "3e-15 across seven grids".

What changed since (plan §6 round 1; commit "fix(DS+G): Codex round 1"): templates/index.html gained _fftRadix2 (iterative radix-2 Cooley-Tukey, inverse divides by n) and _circularConvolve (zero-padded linear convolution at the power of two >= 2n-1, folded back to n: out[i] = lin[i] + lin[i+n]); dsgConvolved_array builds ks = ifftshift(kernel) literally (ks[t] = kernel[(t + floor(n/2)) mod n]) and convolves ds with it - exactly the server's irfft(rfft(ds) * rfft(ifftshift(kernel))). Measured: both reproducers agree to 5e-12 (server max 48) and 1.1e-16; the full box on the base grid <= 3e-15, seven other grids < 1e-6; 58 ms per curve at 0.001 eV over 10 eV, 8 ms at 0.02 eV, local fit 38 ms. tests/js/lineshape_parity.test.js (D'') pins: the two reproducers, alternating 0.05/0.06 steps, the 0.001 eV corner, 2- and 1-point grids (each under 2 s), and m = 0.001/0.002/0.02/0.05 on a 0.1 eV grid where the server's curve is asserted to be all-zero at m <= 0.002 (a known server limit, plan §3a, mirrored - not changed on the server, outside this unit). Function-extractor lists in tests/scripts list the two helpers. JS suite 392 tests, 387 pass, 5 todo (LACX m > 0 x3, (B) DS+G by design, LACX round trip).

Verify each round-1 item is closed, then try to break: the FFT (bit reversal, twiddle recurrence accuracy for N up to 2^18 - accumulated error vs 1e-6 of amplitude after normalisation; the fold for even/odd n; N when 2n-1 is itself a power of two); ifftshift for even n_total; a DS core that is non-zero at BOTH ends of the padded array (centre outside the window on the low-BE side; a very large beta so the tail is everywhere); numpy's median for an even count on an irregular grid vs the JS; np.linspace endpoint; the m-underflow characterisation (is the zone's description right? parity of the padded length; what does the page do when ksum = 0 - NaN handling identical to the server's np.where(isfinite)?); any DS+G path on the page still not through evalPeakArray; memory/GC of Float64Arrays in a chart redraw loop; docs vs measured numbers (plan §2, §3, §3a, §5, §6; findings §7; CLAUDE.md).

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check the diff, rerun the parity tests, and probe the FFT and edge cases you listed. I’ll keep this read-only and return a ranked review with a verdict.

exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g '*dsg*' -g '*lineshape*' -g 'CLAUDE.md' -g 'package.json' -g '*extract*'; git status --short; git diff --stat main..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
CLAUDE.md
docs/superpowers/plans/2026-04-25-la-lineshape-rename-and-true-la.md
docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md
tests/js/lineshape_roundtrip_backend.py
tests/js/lineshape_parity_backend.py
tests/js/lineshape_roundtrip.test.js
tests/js/lineshape_parity.test.js
docs/autofit/codex/dsg_page_evaluator_recheck_prompt.txt
docs/autofit/codex/dsg_page_evaluator_verdict_runA.md
docs/autofit/codex/dsgla_m0_collapse_r2_verdict_runB.md
docs/autofit/codex/dsgla_m0_collapse_verdict_runA.md
docs/autofit/codex/dsgla_m0_collapse_r2_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_r2_verdict_runB.md
docs/autofit/codex/dsg_page_evaluator_r2_verdict_runA.md
docs/autofit/codex/dsgla_m0_collapse_verdict_runB.md
docs/autofit/codex/dsg_page_evaluator_review_prompt.txt
docs/autofit/codex/dsgla_m0_collapse_review_prompt.txt
docs/autofit/codex/dsgla_m0_collapse_r2_review_prompt.txt
docs/autofit/codex/dsg_page_evaluator_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-zHyJAXfD' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-kDE9rODH' (errno=Operation not permitted)
?? docs/autofit/codex/dsg_page_evaluator_r2_verdict_runA.md
?? docs/autofit/codex/dsg_page_evaluator_r2_verdict_runB.md
?? docs/autofit/codex/dsg_page_evaluator_recheck_prompt.txt
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-AAdNpOSQ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3t2Yz0O2' (errno=Operation not permitted)
 CLAUDE.md                                          |   17 +-
 .../codex/dsg_page_evaluator_review_prompt.txt     |   15 +
 .../codex/dsg_page_evaluator_verdict_runA.md       | 3730 ++++++++
 .../codex/dsg_page_evaluator_verdict_runB.md       | 9548 ++++++++++++++++++++
 docs/findings/2026-09-fit-determinacy.md           |   12 +-
 .../plans/2026-09-22-dsg-page-evaluator.md         |  158 +
 scripts/local_server_gap.js                        |    2 +-
 scripts/voigt_saved_vs_refit.js                    |    2 +-
 templates/index.html                               |  188 +-
 tests/js/lineshape_parity.test.js                  |  117 +-
 tests/js/lineshape_roundtrip.test.js               |   19 +-
 tests/js/local_lm_descent.test.js                  |    2 +-
 12 files changed, 13728 insertions(+), 82 deletions(-)

exec
/bin/zsh -lc 'rg --files -g AGENTS.md /Users/skyefortier/xps-app /Users/skyefortier/.codex 2>/dev/null; git diff main..HEAD -- templates/index.html tests/js/lineshape_parity.test.js tests/js/lineshape_roundtrip.test.js tests/js/local_lm_descent.test.js scripts/local_server_gap.js scripts/voigt_saved_vs_refit.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-TNJ7JL08' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-U68AwT1T' (errno=Operation not permitted)
diff --git a/scripts/local_server_gap.js b/scripts/local_server_gap.js
index 370c215..0344a54 100644
--- a/scripts/local_server_gap.js
+++ b/scripts/local_server_gap.js
@@ -29,7 +29,7 @@ function extractFn(name) {
   throw new Error('unbalanced ' + name);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
diff --git a/scripts/voigt_saved_vs_refit.js b/scripts/voigt_saved_vs_refit.js
index db893cb..72cb798 100644
--- a/scripts/voigt_saved_vs_refit.js
+++ b/scripts/voigt_saved_vs_refit.js
@@ -29,7 +29,7 @@ function extractFn(name) {
   throw new Error('unbalanced ' + name);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS',
-  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
+  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
 const state = { peaks: [] };
 const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams, _bgWindowIndices };')(state);
 const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
diff --git a/templates/index.html b/templates/index.html
index f272259..864a4d0 100644
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
@@ -4224,10 +4195,141 @@ function dsgDeltaKernel_array(beArr, center, alpha, beta) {
   return core;
 }
 
+// In-place iterative radix-2 FFT (Cooley–Tukey) on arrays of a power-of-two
+// length; inverse = true divides by n. Double precision, as numpy's pocketfft.
+function _fftRadix2(re, im, inverse) {
+  const n = re.length;
+  for (let i = 1, j = 0; i < n; i++) {                   // bit-reversal permutation
+    let bit = n >> 1;
+    for (; j & bit; bit >>= 1) j ^= bit;
+    j ^= bit;
+    if (i < j) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
+  }
+  for (let len = 2; len <= n; len <<= 1) {
+    const ang = (inverse ? 2 : -2) * Math.PI / len;
+    const wr = Math.cos(ang), wi = Math.sin(ang);
+    for (let i = 0; i < n; i += len) {
+      let cr = 1, ci = 0;
+      for (let k = 0; k < len / 2; k++) {
+        const ar = re[i + k], ai = im[i + k];
+        const br = re[i + k + len / 2] * cr - im[i + k + len / 2] * ci;
+        const bi = re[i + k + len / 2] * ci + im[i + k + len / 2] * cr;
+        re[i + k] = ar + br; im[i + k] = ai + bi;
+        re[i + k + len / 2] = ar - br; im[i + k + len / 2] = ai - bi;
+        const ncr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = ncr;
+      }
+    }
+  }
+  if (inverse) for (let i = 0; i < n; i++) { re[i] /= n; im[i] /= n; }
+}
+
+// Circular convolution of two real arrays of the same length n — what
+// numpy's irfft(rfft(a)·rfft(b)) returns — as a zero-padded linear
+// convolution (FFT length the power of two ≥ 2n − 1) folded back to n.
+function _circularConvolve(a, b) {
+  const n = a.length;
+  let N = 1; while (N < 2 * n - 1) N <<= 1;
+  const ar = new Float64Array(N), ai = new Float64Array(N), br = new Float64Array(N), bi = new Float64Array(N);
+  for (let i = 0; i < n; i++) { ar[i] = a[i]; br[i] = b[i]; }
+  _fftRadix2(ar, ai, false); _fftRadix2(br, bi, false);
+  for (let i = 0; i < N; i++) { const r = ar[i] * br[i] - ai[i] * bi[i]; const im = ar[i] * bi[i] + ai[i] * br[i]; ar[i] = r; ai[i] = im; }
+  _fftRadix2(ar, ai, true);
+  const out = new Float64Array(n);
+  for (let i = 0; i < n; i++) out[i] = ar[i] + (i + n < 2 * n - 1 ? ar[i + n] : 0);
+  return out;
+}
+
+// DS+G with Gaussian broadening, a literal mirror of the server's
+// fitting._ds_g_dscore_gauss (m ≥ 0.001; below that the delta branch above):
+// the DS core on a grid PADDED by ±max(10 m, 20 β) at the data step
+// (np.linspace semantics, always ascending), a half-cosine taper over each
+// pad, a Gaussian kernel of σ = m / 2√(2 ln 2) on the same step normalised to
+// unit sum over the FULL padded length, circular convolution
+// (irfft(rfft(ds)·rfft(ifftshift(kernel))) on the server), linear
+// interpolation back to the data grid, and normalisation by the value
+// interpolated AT the centre. The convolution is the server's circular one,
+// computed by FFT (_circularConvolve) so every wrapped contribution is
+// included and the cost is O(n log n) on any grid (a first cut summed
+// directly within 8 σ and clipped at the array ends: Codex round 1 showed
+// a centre outside the window 0.41 × amplitude off, and 13 s per curve at
+// 0.001 eV). Pinned by tests/js/lineshape_parity.test.js (D)/(D′), the full
+// β/m box incl. the corners that made the old quadrature explode. Returns
+// the curve normalised to 1 at the centre; the caller applies the amplitude.
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
+  // The server's circular convolution, exactly: irfft(rfft(ds)·rfft(ifftshift(kernel)))
+  // is the length-nTot circular convolution of ds with the shifted kernel;
+  // computed here as a zero-padded linear convolution by radix-2 FFT, folded
+  // back to length nTot (out[i] = lin[i] + lin[i + nTot]). Every wrapped
+  // contribution the server includes — a DS tail that runs into the padded
+  // array's far end, a centre outside the window — is included; the cost is
+  // O(n log n) on any grid (13 ms at 0.001 eV over a 10 eV window).
+  const fl = Math.floor(nTot / 2);                        // np.fft.ifftshift's shift
+  const ks = new Float64Array(nTot);
+  for (let t = 0; t < nTot; t++) ks[t] = kernel[(t + fl) % nTot];
+  const conv = _circularConvolve(ds, ks);
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
@@ -4236,11 +4338,11 @@ function evalPeakArray(beArr, p) {
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
index 260f3c1..e653e4c 100644
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
@@ -393,3 +392,85 @@ for (const [label, ranges] of Object.entries(SWEEP_KNOWN_GAP)) {
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
+
+// ── (D″) DS+G: the cases Codex round 1 broke the first cut with, and the ──
+// server's own degenerate zone. The first cut summed the convolution
+// directly within 8 σ and clipped at the padded array's ends; the server's
+// FFT is CIRCULAR, so a DS tail that reaches the far end wraps — visible
+// with a centre outside the window (0.41 × amplitude off) and on a
+// short irregular grid. _circularConvolve now does what the FFT does.
+const DSG_REGRESSIONS = [
+  { label: 'centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)', x: Array.from({ length: 200 }, (_, i) => (i - 99.5) * 0.05), center: 10, laAlpha: 0.25, laBeta: 0.05, laM: 0.4 },
+  { label: 'a 6-point irregular grid', x: [-3, -2.9, -2.8, 0, 2, 3], center: 0, laAlpha: 0.25, laBeta: 0.05, laM: 0.05 },
+  { label: 'genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)', x: (() => { const o = []; let v = 280; for (let i = 0; i < 200; i++) { o.push(v); v += i % 2 ? 0.06 : 0.05; } return o; })(), center: 285.3, laAlpha: 0.3, laBeta: 0.7, laM: 1.2 },
+  { label: 'a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)', x: Array.from({ length: 10001 }, (_, i) => 280 + 0.001 * i), center: 285, laAlpha: 0.49, laBeta: 2, laM: 4 },
+  { label: 'a 2-point grid', x: [284.4, 284.6], center: 284.5, laAlpha: 0.2, laBeta: 0.3, laM: 0.4 },
+  { label: 'a 1-point grid', x: [284.5], center: 284.5, laAlpha: 0.2, laBeta: 0.3, laM: 0.4 },
+];
+for (const c of DSG_REGRESSIONS) {
+  test(`(D″) DS+G regression: ${c.label}`, () => {
+    const p = { ...basePeak('DSG_LA'), amplitude: 1, center: c.center, laAlpha: c.laAlpha, laBeta: c.laBeta, laM: c.laM };
+    const { shape, params } = backendParamsFromRequest(p);
+    const beY = backendEval(shape, params, c.x);
+    const t0 = Date.now();
+    const jsY = evalPeakArray(c.x, p);
+    const ms = Date.now() - t0;
+    const rel = maxRelDiff(jsY, beY, 1);
+    assert.ok(rel < TIGHT_TOL, `${c.label}: max diff ${rel.toExponential(3)} of amplitude (server max ${Math.max(...beY.map(Math.abs)).toExponential(2)})`);
+    assert.ok(ms < 2000, `${c.label}: ${ms} ms for one curve — the cost must stay bounded (O(n log n))`);
+  });
+}
+
+// KNOWN SERVER LIMIT (not this unit's to change; recorded for the owner):
+// just above the 0.001 delta threshold the server's Gaussian kernel can
+// UNDERFLOW on a coarse grid — σ = m/2.355 far below the step, so no
+// padded-grid sample carries kernel weight (for an even padded length the
+// nearest sample is half a step from the centre) — and the server returns
+// an all-zero curve for the component. The page mirrors it exactly (a
+// vanished curve drawn as vanished, never a curve the server did not fit).
+// The zone closes quickly: at 0.1 eV, m = 0.02 is already ordinary.
+for (const laM of [0.001, 0.002, 0.02, 0.05]) {
+  test(`(D″) DS+G at m = ${laM} on a 0.1 eV grid: page equals server${laM <= 0.002 ? ' (both an all-zero curve — the server kernel underflows; known server limit)' : ''}`, () => {
+    const x = Array.from({ length: 120 }, (_, i) => 290 - 0.1 * i);
+    const p = { ...basePeak('DSG_LA'), amplitude: 1, center: 284.5, laAlpha: 0.25, laBeta: 0.7, laM };
+    const { shape, params } = backendParamsFromRequest(p);
+    const beY = backendEval(shape, params, x);
+    const jsY = evalPeakArray(x, p);
+    assert.ok(maxRelDiff(jsY, beY, 1) < TIGHT_TOL, `m = ${laM}: page vs server ${maxRelDiff(jsY, beY, 1).toExponential(3)}`);
+    const serverMax = Math.max(...beY.map(Math.abs));
+    if (laM <= 0.002) assert.equal(serverMax, 0, `m = ${laM}: the server curve is expected to vanish here (kernel underflow) — if it no longer does, the server changed; update this characterisation`);
+    else assert.ok(serverMax > 0.9, `m = ${laM}: a real curve`);
+  });
+}
diff --git a/tests/js/lineshape_roundtrip.test.js b/tests/js/lineshape_roundtrip.test.js
index b0153d6..4103c52 100644
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
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
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
index 5c42284..024ca96 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -35,7 +35,7 @@ function extractFn(name) {
 }
 
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',

exec
/bin/zsh -lc "rg -n 'def _ds_g_dscore_gauss|evalPeak\\(|laCasaXPS\\(|dsgConvolved_array|DSG_LA' fitting.py templates/index.html | head -100; ls -d venv /Users/skyefortier/xps-app/venv; for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if test -f \""'$p"; then cat "$p"; fi; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
fitting.py:152:def _ds_g_dscore_gauss(
templates/index.html:4045:function laCasaXPS(x, center, alpha, beta, mGauss) {
templates/index.html:4046:  // Per-point DS+G fallback for the scalar evaluator's DSG_LA branch: the
templates/index.html:4048:  // convolution is a GRID operation and lives in dsgConvolved_array (called
templates/index.html:4119:function evalPeak(x, p) {
templates/index.html:4135:  } else if (p.shape === 'DSG_LA') {
templates/index.html:4139:    y = laCasaXPS(x, center, _dsgAlpha(p.laAlpha), p.laBeta, p.laM);
templates/index.html:4152:// Grid-aware DSG_LA delta-kernel branch. Mirrors the backend's
templates/index.html:4258:function dsgConvolved_array(beArr, center, alpha, beta, mGauss) {
templates/index.html:4331:// DSG_LA (every m: the delta branch below 0.001, the convolution above) so
templates/index.html:4341:  if (p.shape === 'DSG_LA') {
templates/index.html:4345:    const yArr = dsgConvolved_array(beArr, p.center, p.laAlpha, p.laBeta, p.laM || 0);
templates/index.html:4349:  return beArr.map(x => evalPeak(x, p));
templates/index.html:5189:// Do NOT cross-map look-alike params across shapes (e.g. DSG_LA's laAlpha vs
templates/index.html:5199:  'DSG_LA':     { laAlpha: 0.10, fixLaAlpha: false, laBeta: 0.3, fixLaBeta: false, laM: 0.4, fixLaM: false },
templates/index.html:5204:// shape stores its width in the top-level `fwhm` EXCEPT DS+G (DSG_LA), whose
templates/index.html:5210:function _widthField(shape) { return shape === 'DSG_LA' ? 'laM' : 'fwhm'; }
templates/index.html:5211:function _widthFixField(shape) { return shape === 'DSG_LA' ? 'fixLaM' : 'fixFwhm'; }
templates/index.html:6077:        <option value="DSG_LA" data-tip="Doniach-Šunjić core convolved with a Gaussian. A defensible asymmetric shape — good for metals and transition metals with complex screening. Previously this entry was mis-labeled as 'LA [CasaXPS]'. The genuine CasaXPS LA(α,β,m) lives in the new entry below." ${p.shape==='DSG_LA'?'selected':''}>DS+G</option>
templates/index.html:6093:      <div class="field" id="fwhm-field-${p.id}" ${p.shape === 'DSG_LA' ? 'style="opacity:0.4"' : ''}>
templates/index.html:6094:        <label data-xps-tip="${p.shape === 'DS' ? 'Lorentzian half-width parameter (γ = width/2). When α > 0, the measured FWHM of the peak is broader than this input value because of the asymmetric tail.' : 'Full width at half maximum. Typical XPS peak widths range from 0.5 to 3.0 eV depending on the element, chemical state, and spectrometer resolution. Peaks from the same chemical environment should have similar FWHM values.'}">${p.shape === 'DS' ? 'Width parameter γ (eV)' : 'FWHM (eV)'}${p.shape === 'DSG_LA' ? ' <em style="color:var(--amber);font-size:9px">set by \\u03b2, m</em>' : ''}
templates/index.html:6095:          ${!isLinked && p.shape !== 'DSG_LA' ? '<button class="lock-btn' + (p.fixFwhm ? ' locked' : '') + '" onclick="event.stopPropagation();toggleLock(' + p.id + ',\'fixFwhm\',this)" title="' + (p.fixFwhm ? 'Unlock' : 'Lock') + ' during fitting">' + (p.fixFwhm ? '&#x1f512;' : '&#x1f513;') + '</button>' : ''}
templates/index.html:6098:          ${p.shape === 'DSG_LA' ? 'readonly ' : ''}oninput="updatePeakParam(${p.id},'fwhm',parseFloat(this.value))">
templates/index.html:6181:  } else if (p.shape === 'DSG_LA') {
templates/index.html:6257:    const isLA = p.shape === 'DSG_LA';
templates/index.html:6368:  } else if (shape === 'DSG_LA') {
templates/index.html:6413:  if (par.alpha   && p.shape === 'DSG_LA' && !p.fixLaAlpha) p.laAlpha = par.alpha.value;
templates/index.html:6414:  if (par.beta    && p.shape === 'DSG_LA' && !p.fixLaBeta)  p.laBeta  = par.beta.value;
templates/index.html:6415:  if (par.m_gauss && p.shape === 'DSG_LA' && !p.fixLaM)     p.laM     = par.m_gauss.value;
templates/index.html:8061:      if (!p.fixFwhm && p.shape !== 'DSG_LA') { freeParams.push(p.fwhm); paramMap.push({id: p.id, param: 'fwhm'}); }
templates/index.html:8075:      if (p.shape === 'DSG_LA') {
templates/index.html:10298://   'LA'  → 'DSG_LA' — old LA was DS-core × Gauss conv, mislabeled as
templates/index.html:10309:    'LA': 'DSG_LA',
templates/index.html:10322:  if (counts['LA->DSG_LA']) {
templates/index.html:10323:    console.info('[migration] Remapped ' + counts['LA->DSG_LA'] + " peak(s) from 'LA' → 'DSG_LA' (DS+G is the new label).");
templates/index.html:11185:    case 'DSG_LA':  return { gl: '',            alpha: p.laAlpha ?? '', beta: p.laBeta ?? '', m: p.laM ?? '' };
templates/index.html:15790:    case 'ds_g':            o.shape = 'DSG_LA';
ls: venv: No such file or directory
/Users/skyefortier/xps-app/venv

exec
/bin/zsh -lc "git diff main..HEAD -- CLAUDE.md docs/findings/2026-09-fit-determinacy.md; cat docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md; sed -n '1,155p' tests/js/lineshape_parity.test.js; cat tests/js/lineshape_parity_backend.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-e86uejwi' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-zpyh9aCu' (errno=Operation not permitted)
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
index dce89de..112dbc3 100644
--- a/docs/findings/2026-09-fit-determinacy.md
+++ b/docs/findings/2026-09-fit-determinacy.md
@@ -338,6 +338,16 @@ area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
 the 530 peak records in the seven committed projects use DS+G (and none of
 the 202 measurement targets), so no saved figure is affected; it is the
 fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
-recorded as its own unit. The general lesson repeats §6's: a harness that
+FIXED the same day in `fix-dsg-page-evaluator` after the owner asked whether
+Find Peaks emits DS+G: it does (every A- and M-family C 1s candidate's
+graphitic main line, β fixed at 0.05, α 0–0.3, m 0.4–1.8), and on that box
+the page's area was 5–21 % low for α 0.15–0.3. `dsgConvolved_array` mirrors
+the server's padded-grid convolution by the same FFT circular convolution:
+≤ 3e-15 of amplitude across the whole β/m box on the base grid, < 1e-6
+(measured ≤ 5.5e-15) on seven other grids, and exact on the reviewers'
+reproducers (a centre outside the window, irregular grids, a 0.001 eV
+grid); nothing changed in Find Peaks or the dropdown
+(a science decision is not altered to work around a rendering bug —
+owner, 2026-09-22). The general lesson repeats §6's: a harness that
 evaluates one representative point per shape proves nothing about the range
 the optimiser can reach.
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
  computed as what it is: `_circularConvolve` — a zero-padded linear
  convolution by radix-2 FFT (`_fftRadix2`, length the power of two
  ≥ 2n − 1) folded back to n. Every wrapped contribution the server
  includes is included; O(n log n) on any grid. (The first cut summed
  directly within 8 σ and clipped at the array ends; Codex round 1 showed a
  centre outside the window 0.41 × amplitude off — the DS tail reaches the
  padded array's far end and the server's FFT wraps it — and 13 s per
  curve at 0.001 eV. Both gone.)
- `np.interp` back to the data grid; normalised by the value interpolated AT
  the centre (fallbacks as the server's); non-finite → 0.

`evalPeakArray` routes every DS+G through it (the delta branch inside). The
scalar `evalPeak` DSG_LA branch keeps the name `laCasaXPS` but is now the
normalised DS core with m ignored — the same status as its LACX branch;
guard (C) of the parity harness proves no shipped caller reaches it. The
old quadrature is deleted, not tuned.

Cost (FFT, one curve at the box's far corner β 2, m 4, α 0.49): 1.1 ms on a
241-point 0.05 eV grid, 8 ms at 0.02 eV (601 points), 13 ms at 0.005 eV,
58 ms at 0.001 eV over 10 eV (the first cut: 13 s); Find Peaks-like
parameters 0.2–1.1 ms; a local fit of a DS+G component converges in 38 ms.

## 3. Acceptance (measured)

| check | result |
|---|---|
| parity sweep (D), DS+G box α {0, 0.25, 0.49} × β {0.05, 0.7, 2} × m {0.001, 0.05, 0.4, 2, 4}, base grid | ≤ 3e-15 of amplitude (was 1e52 at β 2, m 0.05) — now a hard assertion |
| (D′) the same box on: 0.1 eV step; 0.02 eV step; descending grid; centre half a step off-grid; descending + 0.03 eV off-grid; a 30-point window narrower than the pad; a 0.0503 eV step | < 1e-6 on every combination — hard assertions |
| (A) DS+G at the base peak (was todo) | hard, passes |
| round trip page → server → page, DS+G (was todo), and DS+G m locked at 0.05 and at 4 (curve comparison was disabled) | hard, pass |
| (B) scalar vs array evaluator, DS+G | now `todo` like LACX: the convolution is a grid operation; guard (C) holds |
| Find Peaks box (β 0.05, α 0–0.3, m 0.4–1.8, 0.05 and 0.1 eV grids) | agrees with the server to 1e-6 (was 5–21 % low in area) |
| (D″) regressions: a centre 10 eV outside a [−5, 5] window; a 6-point irregular grid; alternating 0.05/0.06 steps (median ≠ mean); a 0.001 eV grid over 10 eV at β 2, m 4, α 0.49; 2- and 1-point grids | < 1e-6 (5e-12 relative on the outside-centre case whose server maximum is 48; 3.5e-13 at 0.001 eV) — hard; each curve under 2 s asserted |
| (D″) m = 0.001, 0.002, 0.02, 0.05 on a 0.1 eV grid | page equals server at every m; at m ≤ 0.002 BOTH are an all-zero curve — a KNOWN SERVER LIMIT (§3a), pinned as such |

### 3a. Server limit found on the way (not this unit's to change)

Just above the 0.001 delta threshold on a coarse grid the server's Gaussian
kernel underflows: σ = m/2.355 is far below the step, no padded-grid sample
carries weight (for an even padded length the nearest sample is half a
step from the centre), the kernel normalises to NaN and
`_ds_g_dscore_gauss` returns an all-zero curve for the component (its final
"suppress NaN/Inf" turns it to zeros). At 0.1 eV the zone is roughly
0.001 ≤ m ≲ 0.004 and depends on the parity of the padded length; m = 0.02
is already ordinary. A fit will not settle there (a zero curve fits
nothing), but a LOCKED m in that zone is fitted as zero. The page mirrors
it exactly (a vanished curve drawn as vanished, never a curve the server
did not fit). Recorded for the owner; the fix belongs to the server (a
kernel that collapses to a delta below the grid's resolution, as the
threshold branch does).

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

- JS suite: 392 tests, 387 pass, 0 fail, 5 todo (`node --test tests/js/*.test.js`).
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

**Round 1 (`docs/autofit/codex/dsg_page_evaluator_verdict_run{A,B}.md`):
NO-GO ×2.** Fixed:
1. MAJOR — the first cut's direct sum clipped at the padded array's ends
   and so omitted the wrapped contributions the server's circular FFT
   includes: a centre 10 eV outside a [−5, 5] window was 0.41 × amplitude
   off (the normalisation at the clamped centre scales every value), a
   6-point irregular grid 2.9e-4. Replaced by the same circular
   convolution, computed by FFT (`_fftRadix2`, `_circularConvolve`); both
   reproducers are regression tests, agreeing to 5e-12 and 1e-16.
2. MAJOR — quadratic cost on fine grids (13.5 s per curve at 0.001 eV).
   The FFT makes it O(n log n): 58 ms at 0.001 eV, 8 ms at 0.02 eV; a test
   asserts each regression curve under 2 s.
3. MINOR — (D′)'s "irregular-ish" grid was uniform, and its m = 0.001 case
   passed on a curve that had vanished on BOTH sides. A genuinely
   irregular grid (alternating 0.05/0.06 steps) is in (D″); the vanished
   curve is the server's own kernel underflow just above the delta
   threshold on a coarse grid — characterised in §3a and pinned as a known
   server limit (page equals server; the server curve is asserted to be
   zero there so a server change surfaces).
4. MINOR — findings §7 said ≤ 3e-15 across seven grids; that was the base
   grid (the seven are < 1e-6, measured ≤ 5.5e-15). Corrected.
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

exec
/bin/zsh -lc "sed -n '130,285p' fitting.py; sed -n '280,310p' tests/js/lineshape_parity.test.js; rg -n 'evalPeak|laCasaXPS|evalPeakArray' templates/index.html; sed -n '1,95p' CLAUDE.md; rg -n 'evalPeak|laCasaXPS' static scripts tests/js --glob '*.js' | head -65" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
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
4031:function laCasaXPSCore(eps, alpha, beta) {
4045:function laCasaXPS(x, center, alpha, beta, mGauss) {
4049:  // through evalPeakArray, the only shipped path — parity guard (C)). Until
4053:  const peakVal = laCasaXPSCore(0, alpha, beta);
4055:  return laCasaXPSCore(x - center, alpha, beta) / peakVal;
4119:function evalPeak(x, p) {
4136:    // laCasaXPS already returns a normalised [0,1] value. α is clipped as
4139:    y = laCasaXPS(x, center, _dsgAlpha(p.laAlpha), p.laBeta, p.laM);
4142:    // build paths use laTrueCasaXPS_array via evalPeakArray.
4166:  for (let i = 0; i < N; i++) core[i] = laCasaXPSCore(beArr[i] - center, alpha, beta);
4285:  for (let i = 0; i < nTot; i++) { const v = laCasaXPSCore(xp[i] - center, a, b); ds[i] = Number.isFinite(v) ? v : 0; }
4333:function evalPeakArray(beArr, p) {
4349:  return beArr.map(x => evalPeak(x, p));
4356:    const yArr = evalPeakArray(beArray, p);
5184:// here matching defaultPeak, then update evalPeak / renderShapeControls /
5223:// ones evalPeak reads for shape A — to their originals, so the rendered curve
6335:    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
8358:      const comp = evalPeakArray(be, wp);
8430:  // evalPeakArray(), not a per-point evalPeak map: for LACX with caM > 0,
8432:  // evalPeak silently returns the unconvolved base regardless of caM.
8434:  return evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step;
8903:    const peakOnly = evalPeakArray(be, p);
9407:      const peakY = evalPeakArray(plotBE, p);
10100:  // Per-peak curves and areas. evalPeakArray(), not per-point evalPeak:
10102:  // Gaussian convolution — evalPeak silently ignores caM. These curves
10105:    const yArr = evalPeakArray(be, p);
10767:  // evalPeakArray() per peak, once, not per-point evalPeak per row: for
10769:  // Gaussian convolution — evalPeak silently ignores caM, which would
10772:  const peakCols = state.peaks.map(p => evalPeakArray(be, p));
10917:      // evalPeakArray(), not per-point evalPeak: applies Gaussian
10918:      // convolution for LACX with caM > 0, which evalPeak ignores.
10919:      const pkArr = evalPeakArray(be, p);
10949:      // evalPeakArray(), not per-point evalPeak: applies Gaussian
10950:      // convolution for LACX with caM > 0, which evalPeak ignores.
10951:      const pkArr = evalPeakArray(be, p);
11048:      // evalPeakArray(), not per-point evalPeak: see fill/outline loops above.
11049:      const pArr = evalPeakArray(be, p);
11174:// columns — read ONLY the ACTIVE shape's params (matching evalPeak /
# XPS Fitting Studio

Web application for XPS (X-ray Photoelectron Spectroscopy) peak fitting,
multi-spectrum visualization, and project management. Python/Flask backend
with an lmfit-driven peak-fitting pipeline; single-page frontend in
`templates/index.html`. Deployed at xps.fortierlab.org via a gunicorn
LaunchAgent + Cloudflare Tunnel.

## Stack

- **Backend:** Python/Flask, served by gunicorn. App factory in [app.py](app.py).
- **Fitting engine:** lmfit ≥ 1.3 (5 methods: leastsq, least_squares, nelder, differential_evolution, basinhopping).
- **Numerics:** numpy, scipy.
- **File parsing:** pandas, openpyxl (xlsx), olefile (vgd).
- **Frontend:** Single-page HTML/JS in `templates/index.html` (~8500 LOC). Vanilla JS, no build step.
- **Charting:** Chart.js 4.4 (CDN).
- **Deployment:** macOS LaunchAgent runs gunicorn on **127.0.0.1:5050** (NOT :5000 — macOS AirTunes intercepts :5000 and returns 403, so health-check :5050); Cloudflare Tunnel publishes to xps.fortierlab.org. Dev gunicorn typically runs on :5151 with `--reload` for pre-merge verification. See [DEPLOY.md](DEPLOY.md) for the full deploy sequence.

## Project Layout

```
app.py                    # Flask app factory + REST routes
fitting.py                # lmfit pipeline, lineshape impls, background algorithms
parser.py                 # File parsers (csv / tsv / txt / xy / xlsx / xls / vgd)
vgd_parser.py             # Thermo Avantage VGD binary parser (uses olefile)
templates/index.html      # Frontend — CSS + HTML + JS in one file
tests/                    # pytest suite (focused on LA + DS+G correctness)
docs/superpowers/plans/   # Agent-authored design memos and implementation plans
uploads/                  # Per-session .npz storage (gitignored)
requirements.txt
venv/                     # virtualenv (do not commit)
```

The Flask backend serves the frontend via `render_template('index.html')`
and exposes a REST API consumed by the page through fetch.

## Backend API

Per-upload sessions store parsed `(energy, counts)` arrays as compressed
`.npz` in `uploads/<session_id>.npz`. No server-side memory state —
compatible with multi-worker gunicorn.

| Method | Path | Purpose |
|---|---|---|
| `GET`    | `/`                       | Serve the frontend (`templates/index.html`). |
| `GET`    | `/api/health`             | Liveness probe. Returns `{status: "ok"}`. |
| `GET`    | `/api/peak-shapes`        | List backend-registered lineshapes (gaussian / lorentzian / pseudo_voigt_gl / asymmetric_gl / doniach_sunjic / ds_g / la_casaxps). |
| `GET`    | `/api/elements`           | Spin-orbit element presets (splitting + area ratio). |
| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
| `POST`   | `/api/parse-vgd`          | Parse Thermo Avantage VGD binary directly (no session storage). |
| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
| `DELETE` | `/api/session/<id>`       | Delete session files. |
| `POST`   | `/api/background`         | Compute background curve for a session. |
| `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |

## Frontend Architecture

### State

Module-global `state` holds the currently-active tab's working values
(swapped on tab switch by `TabManager.activateTab`):

```js
state = {
  rawBE, rawIntensity,   // full spectrum as loaded
  ccShift,               // charge-correction rigid shift (eV)
  peaks[],               // array of peak objects
  nextId,                // auto-increment peak ID
  chart,                 // Chart.js instance
  residChart,            // Residuals sub-chart instance
  fitResult,             // last fit diagnostics (be, bgIntensity, bgSubtracted, fittedY, chi, etc.)
  lineWidth,             // per-tab line width (sync of tab.lineWidth)
}
```

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
tests/js/fit_acceptance.test.js:541:    new Function('state', '_activeTab', 'getROIData', 'computeBackground', 'evalAllPeaks', 'evalPeakArray', 'Blob', 'URL', 'document', 'notify',
tests/js/lineshape_roundtrip.test.js:6:// sent as pseudo_voigt_gl with gl_ratio FREE from 0.3 while evalPeak drew
tests/js/lineshape_roundtrip.test.js:15:// page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
tests/js/lineshape_roundtrip.test.js:44:  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
tests/js/lineshape_roundtrip.test.js:45:  'evalPeakArray', 'getPeak', 'peakToBackendSpec', '_applyBackendParams'];
tests/js/lineshape_roundtrip.test.js:47:const env = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, peakToBackendSpec, _applyBackendParams };')(state);
tests/js/lineshape_roundtrip.test.js:102:  for (const tp of truthPeaks) { const y = env.evalPeakArray(GRID, tp); for (let i = 0; i < GRID.length; i++) counts[i] += y[i]; }
tests/js/lineshape_roundtrip.test.js:125:    const drawn = env.evalPeakArray(res.energy, peaks[0]);
tests/js/lineshape_roundtrip.test.js:143:  assert.ok(maxRelDiff(env.evalPeakArray(res.energy, peaks[0]), res.individual_peaks[0].y, peaks[0].amplitude) < TIGHT_TOL);
tests/js/lineshape_roundtrip.test.js:152:    const rel = maxRelDiff(env.evalPeakArray(res.energy, p), ip.y, p.amplitude);
tests/js/lineshape_roundtrip.test.js:208:    const rel = maxRelDiff(env.evalPeakArray(res.energy, p), res.individual_peaks[0].y, p.amplitude);
tests/js/lineshape_roundtrip.test.js:218:  assert.ok(maxRelDiff(env.evalPeakArray(res.energy, peaks[0]), res.individual_peaks[0].y, peaks[0].amplitude) < TIGHT_TOL);
tests/js/local_lm_descent.test.js:38:  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
tests/js/local_lm_descent.test.js:39:  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
tests/js/local_lm_descent.test.js:60:    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
tests/js/lineshape_parity.test.js:7://       (evalPeakArray, called for chart data build paths) must numerically
tests/js/lineshape_parity.test.js:15://       evalPeak(x, p) and evalPeakArray(...)[i] at the same x, must agree
tests/js/lineshape_parity.test.js:19://       This is exactly what the LACX per-point fallback did: evalPeak()
tests/js/lineshape_parity.test.js:20://       silently ignores Gaussian convolution (m) while evalPeakArray()
tests/js/lineshape_parity.test.js:21://       applies it correctly, so any evalPeak() caller — export/save/Results
tests/js/lineshape_parity.test.js:26:// "the convolved value at an isolated point" via evalPeakArray([x], p)[0] —
tests/js/lineshape_parity.test.js:29:// trivially, for ANY x/alpha/beta) regardless of what evalPeak() does. That
tests/js/lineshape_parity.test.js:31:// asserts evalPeak(x, p) against evalPeakArray(realisticGrid, p)[indexOfX] —
tests/js/lineshape_parity.test.js:50:// ── Extract the shipped lineshape block (gaussian … evalPeakArray) ─────────
tests/js/lineshape_parity.test.js:52:  + extract(/function gaussian\(x, center, fwhm\) \{[\s\S]*?\nfunction evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}/,
tests/js/lineshape_parity.test.js:54:  + 'return { evalPeak, evalPeakArray };\n})()');
tests/js/lineshape_parity.test.js:55:const { evalPeak, evalPeakArray } = evalCtx;
tests/js/lineshape_parity.test.js:137:    const jsY = evalPeakArray(x, p);
tests/js/lineshape_parity.test.js:160://   evaluator used to be a numerical quadrature (laCasaXPS) whose step
tests/js/lineshape_parity.test.js:173:  const jsY = evalPeakArray(x, p);
tests/js/lineshape_parity.test.js:185:  const jsY = evalPeakArray(x, p);
tests/js/lineshape_parity.test.js:196:  const jsY = evalPeakArray(x, p);
tests/js/lineshape_parity.test.js:206:// core, no convolution), evalPeakArray now takes a grid-aware branch that
tests/js/lineshape_parity.test.js:222:      const jsY = evalPeakArray(x, p);
tests/js/lineshape_parity.test.js:239:  const jsY = evalPeakArray(x, p);
tests/js/lineshape_parity.test.js:247:// ── (B) Frontend vs frontend: evalPeak(x,p) vs evalPeakArray(grid,p)[i] ────
tests/js/lineshape_parity.test.js:248:// For every shape EXCEPT LACX, evalPeakArray falls through to
tests/js/lineshape_parity.test.js:249:// `beArr.map(x => evalPeak(x, p))` — so this is trivially true by
tests/js/lineshape_parity.test.js:251:// structural fact (a future special-case added to evalPeakArray for another
tests/js/lineshape_parity.test.js:253:// immediately). LACX with m>0 is the one shape where evalPeakArray takes a
tests/js/lineshape_parity.test.js:255:// evalPeak (laTrueCasaXPS, WITHOUT convolution) — tracked as `todo` since
tests/js/lineshape_parity.test.js:256:// unit 1/commit 2 reroutes evalPeak()'s CALLERS away from the bad path but
tests/js/lineshape_parity.test.js:257:// does not change evalPeak()'s own (now-unreachable-from-shipped-code-paths)
tests/js/lineshape_parity.test.js:262:  const opts = shape === 'LACX' ? { todo: 'evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header' }
tests/js/lineshape_parity.test.js:263:    : shape === 'DSG_LA' ? { todo: 'evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)' } : undefined;
tests/js/lineshape_parity.test.js:264:  test(`(B) evalPeak vs evalPeakArray agree pointwise: ${shape}`, opts, () => {
tests/js/lineshape_parity.test.js:267:    const arr = evalPeakArray(x, p);
tests/js/lineshape_parity.test.js:269:    const single = evalPeak(x[idx], p);
tests/js/lineshape_parity.test.js:272:      `${shape} at x=${x[idx]}: evalPeak=${single}, evalPeakArray[i]=${arr[idx]}, rel diff=${(diff * 100).toFixed(4)}%`);
tests/js/lineshape_parity.test.js:276:// ── (C) Structural guard: evalPeak() must have no callers of its own ──────
tests/js/lineshape_parity.test.js:277:// outside evalPeakArray()'s internal fallback. This is what actually closes
tests/js/lineshape_parity.test.js:279:// function that calls evalPeak(...) directly instead of evalPeakArray(...)
tests/js/lineshape_parity.test.js:284:test('(C) evalPeak() has no direct callers outside evalPeakArray()', () => {
tests/js/lineshape_parity.test.js:285:  const evalPeakDef = extract(/function evalPeak\(x, p\) \{[\s\S]*?\n\}\n/, 'evalPeak definition');
tests/js/lineshape_parity.test.js:286:  const evalPeakArrayDef = extract(/function evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}\n/, 'evalPeakArray definition');
tests/js/lineshape_parity.test.js:287:  assert.ok(/\bevalPeak\(x, p\)/.test(evalPeakArrayDef),
tests/js/lineshape_parity.test.js:288:    'evalPeakArray() no longer contains its expected internal evalPeak() fallback call — update this test\'s assumption');
tests/js/lineshape_parity.test.js:289:  const rest = html.split(evalPeakDef).join('\n').split(evalPeakArrayDef).join('\n');
tests/js/lineshape_parity.test.js:290:  const strayCalls = [...rest.matchAll(/\bevalPeak\(/g)];
tests/js/lineshape_parity.test.js:292:    `evalPeak() is called directly ${strayCalls.length} time(s) outside evalPeakArray() — route through evalPeakArray() ` +
tests/js/lineshape_parity.test.js:293:    'instead (see file header: evalPeak() silently ignores Gaussian convolution for LACX with m>0, which evalPeakArray() ' +
tests/js/lineshape_parity.test.js:316://     quadrature (laCasaXPS) sizes its step to resolve the Lorentzian core
tests/js/lineshape_parity.test.js:375:    const rel = maxRelDiff(evalPeakArray(x, k.p), beYs[i], k.p.amplitude);
tests/js/lineshape_parity.test.js:422:    const worst = cases.map((k, i) => ({ c: k.c, rel: maxRelDiff(evalPeakArray(specs[i].x, k.p), beYs[i], k.p.amplitude) })).sort((a, b) => b.rel - a.rel);
tests/js/lineshape_parity.test.js:448:    const jsY = evalPeakArray(c.x, p);

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/*.test.js | tail -18' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
codex
The code now computes circular convolution, and I found no page caller bypassing `evalPeakArray`. I’m checking numerical agreement next, especially where an out-of-window centre makes the normalization value tiny and could amplify FFT roundoff.

 succeeded in 53161ms:
  duration_ms: 18.319222
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 392 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 7.233474
  type: 'test'
  ...
1..392
# tests 392
# suites 0
# pass 313
# fail 74
# cancelled 0
# skipped 0
# todo 5
# duration_ms 53173.850147

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const {evalPeakArray,_circularConvolve,_fftRadix2}=new Function(block+'\\'';return {evalPeakArray,_circularConvolve,_fftRadix2}'\\'')();
const cases=[];
function add(x,center,alpha,beta,m,label){cases.push({shape:'\\''ds_g'\\'',params:{amplitude:1,center,alpha,beta,m_gauss:m},x,label})}
for(const n of [20,21,100,101])for(const step of [.05,.1,.5])for(const center of [-30,-10,0,10,30])for(const m of [.001,.002,.003,.004,.05,.4,4])add(Array.from({length:n},(_,i)=>(i-(n-1)/2)*step),center,.49,.05,m,'\\''outside/coarse'\\'');
for(const n of [200,201])for(const beta of [2,10,100])for(const center of [-10,0,10])add(Array.from({length:n},(_,i)=>(i-(n-1)/2)*.05),center,.49,beta,.4,'\\''large beta'\\'');
for(const n of [5,7,101])add(Array.from({length:n},(_,i)=>Math.floor(i/2)*.11+(i%2)*.05),.12,.3,.7,1.2,'\\''even median'\\'');
const backend=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''tests/js/lineshape_parity_backend.py'\\''],{input:JSON.stringify(cases),maxBuffer:50e6,encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']}));
const results=cases.map((c,i)=>{const p=c.params;const y=evalPeakArray(c.x,{shape:'\\''DSG_LA'\\'',...p,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss});return {label:c.label,n:c.x.length,step:c.x[1]-c.x[0],...p,err:Math.max(...y.map((v,k)=>Math.abs(v-backend[i][k]))),jsMax:Math.max(...y),pyMax:Math.max(...backend[i])}}).sort((a,b)=>b.err-a.err);
console.log(JSON.stringify({total:results.length,failed:results.filter(r=>r.err>=1e-6).length,worst:results.slice(0,12),ordinary:results.filter(r=>r.label"'!=='"'\\''outside/coarse'\\'').slice(0,3)},null,2));
let max=0;
for(let n=1;n<=100;n++){const a=Array.from({length:n},(_,i)=>Math.sin(i+.2)),b=Array.from({length:n},(_,i)=>Math.cos(i*.37));const out=_circularConvolve(a,b);for(let i=0;i<n;i++){let v=0;for(let j=0;j<n;j++)v+=a[j]*b[(i-j+n)%n];max=Math.max(max,Math.abs(v-out[i]));}}
console.log('\\''direct circular lengths 1..100 worst'\\'',max);
for(const n of [2,4,256,65536,262144]){const re=Float64Array.from({length:n},(_,i)=>Math.sin(i*.123)+Math.cos(i*.087)),im=new Float64Array(n),orig=re.slice();_fftRadix2(re,im,false);_fftRadix2(re,im,true);let err=0;for(let i=0;i<n;i++)err=Math.max(err,Math.abs(re[i]-orig[i]),Math.abs(im[i]));console.log('\\''fft roundtrip'\\'',n,err)}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 exited 1 in 1587ms:
<ref *1> node:child_process:955
    throw err;
    ^

Error: spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE
    at Object.spawnSync (node:internal/child_process:1120:20)
    at spawnSync (node:child_process:902:24)
    at Object.execFileSync (node:child_process:945:15)
    at [eval]:10:29
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
  output: [ null, '', null ],
  pid: 38752,
  stdout: '',
  stderr: null
}

Node.js v22.22.2

exec
/bin/zsh -lc "sed -n '285,315p' fitting.py; sed -n '4018,4045p' templates/index.html; sed -n '8860,8920p' templates/index.html; sed -n '9350,9430p' templates/index.html; sed -n '8410,8450p' templates/index.html; rg -n 'updateChart\\(|renderResults\\(|peakArea\\(' templates/index.html | head -45" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:

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
  const dx = center - x;   // negative on HIGH-BE side (x > center)
  const gamma = Math.max(fwhm / 2, 1e-12);
  const r2 = dx * dx + gamma * gamma;
  const rPow = Math.pow(r2, (1 - alpha) / 2);
  if (rPow === 0) return 0;
  const phase = Math.PI * alpha / 2 + (1 - alpha) * Math.atan(dx / gamma);
  const core = Math.cos(phase) / rPow;
  // Exponential envelope: exp(gamma_asym * min(dx, 0)) = 1 at/below center,
  // decays as x moves to higher BE (dx < 0).
  const tailDecay = gamma_asym > 0 ? Math.exp(gamma_asym * Math.min(dx, 0)) : 1;
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
// which is the only path that runs when source-tab state changes
// (peak edits, ccShift edits, re-fits all happen while user is on the
// source tab — they return to the stack via activateTab → updatePlot →
// _renderStackChart, picking up fresh data).
//
// The big win: Path B (post-load) recomputes a Shirley background per
// call, which costs ~1-2 ms per entry. Without the cache, that compute
// fires on every offset/line-width slider tick (60 Hz) for every fit
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
    }
  }

  // Background — frozen to fit range after fit. Hidden in subtracted view.
  if (plotBE.length && !bgSubView) {
    datasets.push({
      label: 'Background',
      data: plotBE.map((b, i) => ({ x: b, y: plotBG[i] })),
      borderColor: '#4a5a78',
      borderWidth: 1,
      borderDash: [4, 3],
    x[i] /= M[i][i];
  }
  return x;
}

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
2455:  renderResults();   // the restored model's designation (or its absence) must be visible immediately
2471:  renderResults();   // the restored model's designation (or its absence) must be visible immediately
3257:    renderResults();
3475:      renderResults();   // installs the imported model's designation (or the plain placeholder) and clears stale widgets
6008:    for (const p of state.peaks) { const a = _peakArea(p, _roiBE); _peakAreas[p.id] = a; if (!_isUnsupported(p)) totalArea += a; }
6969:  const peakAreas = state.peaks.map(p => ({ id: p.id, area: _peakArea(p, be) }));
7110:  if (roiBE.length) for (const p of state.peaks) { areas[p.id] = _peakArea(p, roiBE); if (!_isUnsupported(p, key)) total += areas[p.id]; }
7245:  if (typeof renderResults === 'function') renderResults();
7527:  if (state.fitResult && shownIn('.results-table .unsupported-row') !== flaggedNow && typeof renderResults === 'function') { renderResults(); rendered = true; }   // renders Quantify and the starts panel too
7892:  renderResults();
8382:  renderResults();
8428:function _peakArea(p, be) {
8437:function renderResults() {
8497:  // saves omit it, and without a guard _peakArea(p, be) throws on be.length —
8505:  const areas = state.peaks.map(p => _peakArea(p, be));
10453:  renderResults();   // installs the restored result's designation in Results/Quantify and the statistic display (unit A0)
11195:  const areas = state.peaks.map(p => _peakArea(p, be));
11532:  if (name === 'results' || name === 'quantify') renderResults();
13916:  renderResults();
15921:    // happened to re-render it. renderResults() already handles
15924:    renderResults();

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import fitting; print(\"ready\")'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 exited 1 in 1247ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
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

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const child=require('\\''child_process'\\'');const original=child.execFileSync;child.execFileSync=function(file,args,opts){if(file.includes('\\''python'\\'')&&args[0]?.endsWith('\\''.py'\\''))return original(file,['\\''-c'\\'',\"import tempfile, runpy, sys; tempfile.tempdir='\\''/tmp'\\''; p=sys.argv.pop(1); runpy.run_path(p,run_name='\\''__main__'\\'')\",...args],opts);return original(file,args,opts)};const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const {evalPeakArray,_circularConvolve,_fftRadix2}=new Function(block+'\\'';return {evalPeakArray,_circularConvolve,_fftRadix2}'\\'')();
const cases=[];
function add(x,center,alpha,beta,m,label){cases.push({shape:'\\''ds_g'\\'',params:{amplitude:1,center,alpha,beta,m_gauss:m},x,label})}
for(const n of [20,21,100,101])for(const step of [.05,.1,.5])for(const center of [-30,-10,0,10,30])for(const m of [.001,.002,.003,.004,.05,.4,4])add(Array.from({length:n},(_,i)=>(i-(n-1)/2)*step),center,.49,.05,m,'\\''outside/coarse'\\'');
for(const n of [200,201])for(const beta of [2,10,100])for(const center of [-10,0,10])add(Array.from({length:n},(_,i)=>(i-(n-1)/2)*.05),center,.49,beta,.4,'\\''large beta'\\'');
for(const n of [5,7,101])add(Array.from({length:n},(_,i)=>Math.floor(i/2)*.11+(i%2)*.05),.12,.3,.7,1.2,'\\''even median'\\'');
const backend=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''tests/js/lineshape_parity_backend.py'\\''],{input:JSON.stringify(cases),maxBuffer:50e6,encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']}));
const results=cases.map((c,i)=>{const p=c.params;const y=evalPeakArray(c.x,{shape:'\\''DSG_LA'\\'',...p,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss});return {label:c.label,n:c.x.length,step:c.x[1]-c.x[0],...p,err:Math.max(...y.map((v,k)=>Math.abs(v-backend[i][k]))),jsMax:Math.max(...y),pyMax:Math.max(...backend[i])}}).sort((a,b)=>b.err-a.err);
console.log(JSON.stringify({total:results.length,failed:results.filter(r=>r.err>=1e-6).length,worst:results.slice(0,12),ordinary:results.filter(r=>r.label"'!=='"'\\''outside/coarse'\\'').slice(0,3)},null,2));
let max=0;
for(let n=1;n<=100;n++){const a=Array.from({length:n},(_,i)=>Math.sin(i+.2)),b=Array.from({length:n},(_,i)=>Math.cos(i*.37));const out=_circularConvolve(a,b);for(let i=0;i<n;i++){let v=0;for(let j=0;j<n;j++)v+=a[j]*b[(i-j+n)%n];max=Math.max(max,Math.abs(v-out[i]));}}
console.log('\\''direct circular lengths 1..100 worst'\\'',max);
for(const n of [2,4,256,65536,262144]){const re=Float64Array.from({length:n},(_,i)=>Math.sin(i*.123)+Math.cos(i*.087)),im=new Float64Array(n),orig=re.slice();_fftRadix2(re,im,false);_fftRadix2(re,im,true);let err=0;for(let i=0;i<n;i++)err=Math.max(err,Math.abs(re[i]-orig[i]),Math.abs(im[i]));console.log('\\''fft roundtrip'\\'',n,err)}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const child=require('\\''child_process'\\'');const original=child.execFileSync;child.execFileSync=function(file,args,opts){if(file.includes('\\''python'\\'')&&args[0]?.endsWith('\\''.py'\\''))return original(file,['\\''-c'\\'',\"import tempfile, runpy, sys; tempfile.tempdir='\\''/tmp'\\''; p=sys.argv.pop(1); runpy.run_path(p,run_name='\\''__main__'\\'')\",...args],opts);return original(file,args,opts)};const fs=require('\\''fs'\\'');for(const f of fs.readdirSync('\\''tests/js'\\''))if(f.endsWith('\\''.test.js'\\''))require('\\''./tests/js/'\\''+f);' | tail -18" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 3265ms:
{
  "total": 441,
  "failed": 94,
  "worst": [
    {
      "label": "outside/coarse",
      "n": 101,
      "step": 0.04999999999999982,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.001,
      "err": 98895000515543740,
      "jsMax": 1,
      "pyMax": 98895000515543740
    },
    {
      "label": "outside/coarse",
      "n": 101,
      "step": 0.04999999999999982,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.002,
      "err": 98895000515543740,
      "jsMax": 1,
      "pyMax": 98895000515543740
    },
    {
      "label": "outside/coarse",
      "n": 101,
      "step": 0.04999999999999982,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.003,
      "err": 98895000515543740,
      "jsMax": 1,
      "pyMax": 98895000515543740
    },
    {
      "label": "outside/coarse",
      "n": 101,
      "step": 0.04999999999999982,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.004,
      "err": 98895000515543740,
      "jsMax": 1,
      "pyMax": 98895000515543740
    },
    {
      "label": "outside/coarse",
      "n": 21,
      "step": 0.5,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.001,
      "err": 48501712413941790,
      "jsMax": 48501712413941790,
      "pyMax": 1
    },
    {
      "label": "outside/coarse",
      "n": 21,
      "step": 0.5,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.002,
      "err": 48501712413941790,
      "jsMax": 48501712413941790,
      "pyMax": 1
    },
    {
      "label": "outside/coarse",
      "n": 21,
      "step": 0.5,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.003,
      "err": 48501712413941790,
      "jsMax": 48501712413941790,
      "pyMax": 1
    },
    {
      "label": "outside/coarse",
      "n": 21,
      "step": 0.5,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.004,
      "err": 48501712413941790,
      "jsMax": 48501712413941790,
      "pyMax": 1
    },
    {
      "label": "outside/coarse",
      "n": 21,
      "step": 0.5,
      "amplitude": 1,
      "center": 10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.05,
      "err": 48501712413941790,
      "jsMax": 48501712413941790,
      "pyMax": 1
    },
    {
      "label": "outside/coarse",
      "n": 100,
      "step": 0.5,
      "amplitude": 1,
      "center": 30,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.05,
      "err": 33796377994053388,
      "jsMax": 1,
      "pyMax": 33796377994053388
    },
    {
      "label": "outside/coarse",
      "n": 21,
      "step": 0.5,
      "amplitude": 1,
      "center": -10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.001,
      "err": 24764730805051452,
      "jsMax": 1,
      "pyMax": 24764730805051452
    },
    {
      "label": "outside/coarse",
      "n": 21,
      "step": 0.5,
      "amplitude": 1,
      "center": -10,
      "alpha": 0.49,
      "beta": 0.05,
      "m_gauss": 0.002,
      "err": 24764730805051452,
      "jsMax": 1,
      "pyMax": 24764730805051452
    }
  ],
  "ordinary": [
    {
      "label": "large beta",
      "n": 201,
      "step": 0.04999999999999982,
      "amplitude": 1,
      "center": 0,
      "alpha": 0.49,
      "beta": 100,
      "m_gauss": 0.4,
      "err": 2.999822612537173e-13,
      "jsMax": 1.0237113089358372,
      "pyMax": 1.0237113089357412
    },
    {
      "label": "large beta",
      "n": 200,
      "step": 0.04999999999999982,
      "amplitude": 1,
      "center": 0,
      "alpha": 0.49,
      "beta": 100,
      "m_gauss": 0.4,
      "err": 2.9687363678476686e-13,
      "jsMax": 1.0235848870172373,
      "pyMax": 1.0235848870171553
    },
    {
      "label": "large beta",
      "n": 201,
      "step": 0.04999999999999982,
      "amplitude": 1,
      "center": -10,
      "alpha": 0.49,
      "beta": 100,
      "m_gauss": 0.4,
      "err": 2.7755575615628914e-13,
      "jsMax": 1.0645911862405824,
      "pyMax": 1.0645911862406972
    }
  ]
}
direct circular lengths 1..100 worst 1.865174681370263e-14
fft roundtrip 2 2.220446049250313e-16
fft roundtrip 4 2.220446049250313e-16
fft roundtrip 256 9.325873406851315e-15
fft roundtrip 65536 3.623323863166661e-12
fft roundtrip 262144 7.400968726756219e-12

codex
The standard test run hit a read-only sandbox issue: Python’s `dill` import tries to probe for a writable temporary directory. I’m rerunning with that probe bypassed in memory; no files are being changed.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node --expose-gc -e 'const child=require('\\''child_process'\\'');const original=child.execFileSync;child.execFileSync=function(file,args,opts){if(file.includes('\\''python'\\'')&&args[0]?.endsWith('\\''.py'\\''))return original(file,['\\''-c'\\'',\"import tempfile, runpy, sys; tempfile.tempdir='\\''/tmp'\\''; p=sys.argv.pop(1); runpy.run_path(p,run_name='\\''__main__'\\'')\",...args],opts);return original(file,args,opts)};const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const {evalPeakArray,_circularConvolve,_fftRadix2}=new Function(block+'\\'';return {evalPeakArray,_circularConvolve,_fftRadix2}'\\'')();

const specs=[];
function add(label,x,center,alpha,beta,m){specs.push({label,shape:'\\''ds_g'\\'',x,params:{amplitude:1,center,alpha,beta,m_gauss:m}})}
add('\\''free-box reproducer'\\'',Array.from({length:21},(_,i)=>(i-10)*.5),10,.49,.05,.05);
add('\\''low-BE reproducer'\\'',Array.from({length:21},(_,i)=>(i-10)*.5),-10,.49,.05,.05);
for(const n of [120,121])for(const m of [.001,.002,.003,.0031,.004,.02])add('\\''underflow'\\'',Array.from({length:n},(_,i)=>290-.1*i),284.5,.25,.7,m);
for(const g of [{step:.05,n:200},{step:.1,n:120},{step:.02,n:500},{step:.0503,n:181}])for(const a of [0,.25,.49])for(const b of [.05,.7,2])for(const m of [.001,.05,.4,2,4])add('\\''box '\\''+g.step,Array.from({length:g.n},(_,i)=>391.8-g.step*g.n/2+g.step*i),391.8,a,b,m);
add('\\''fine 2"'^18 FFT'"'\\'',Array.from({length:10001},(_,i)=>280+.001*i),285,.49,2,4);
const py=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''tests/js/lineshape_parity_backend.py'\\''],{input:JSON.stringify(specs),maxBuffer:50e6,encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']}));
const worst={};for(let i=0;i<specs.length;i++){const c=specs[i],p=c.params;const start=performance.now();const y=evalPeakArray(c.x,{shape:'\\''DSG_LA'\\'',...p,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss});const r={label:c.label,n:c.x.length,m:p.m_gauss,center:p.center,err:Math.max(...y.map((v,j)=>Math.abs(v-py[i][j]))),jsMax:Math.max(...y),pyMax:Math.max(...py[i]),ms:performance.now()-start};if(c.label.includes('\\''box'\\'')){if("'!worst[c.label]||r.err>worst[c.label].err)worst[c.label]=r}else console.log(JSON.stringify(r));}
console.log('"'\\''sweeps'\\'',JSON.stringify(worst));
const x=Array.from({length:10001},(_,i)=>280+.001*i),p={shape:'\\''DSG_LA'\\'',amplitude:1,center:285,laAlpha:.49,laBeta:2,laM:4};
global.gc();const before=process.memoryUsage();let times=[];for(let i=0;i<100;i++){const t=performance.now();evalPeakArray(x,p);times.push(performance.now()-t);}const during=process.memoryUsage();global.gc();const after=process.memoryUsage();times.sort((a,b)=>a-b);console.log('\\''100 fine-grid redraw evaluations'\\'',JSON.stringify({medianMs:times[50],maxMs:times[99],before,during,after}));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '4300,4330p'; nl -ba docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md | sed -n '65,98p'; nl -ba docs/findings/2026-09-fit-determinacy.md | tail -22" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
  4300	  // is the length-nTot circular convolution of ds with the shifted kernel;
  4301	  // computed here as a zero-padded linear convolution by radix-2 FFT, folded
  4302	  // back to length nTot (out[i] = lin[i] + lin[i + nTot]). Every wrapped
  4303	  // contribution the server includes — a DS tail that runs into the padded
  4304	  // array's far end, a centre outside the window — is included; the cost is
  4305	  // O(n log n) on any grid (13 ms at 0.001 eV over a 10 eV window).
  4306	  const fl = Math.floor(nTot / 2);                        // np.fft.ifftshift's shift
  4307	  const ks = new Float64Array(nTot);
  4308	  for (let t = 0; t < nTot; t++) ks[t] = kernel[(t + fl) % nTot];
  4309	  const conv = _circularConvolve(ds, ks);
  4310	  // np.interp(query, xp, conv): xp ascending; clamped outside; linear inside
  4311	  const interp = q => {
  4312	    if (q <= xp[0]) return conv[0];
  4313	    if (q >= xp[nTot - 1]) return conv[nTot - 1];
  4314	    let lo2 = 0, hi2 = nTot - 1;
  4315	    while (hi2 - lo2 > 1) { const mid = (lo2 + hi2) >> 1; if (xp[mid] <= q) lo2 = mid; else hi2 = mid; }
  4316	    const x0 = xp[lo2], x1 = xp[hi2];
  4317	    const tt = x1 !== x0 ? (q - x0) / (x1 - x0) : 0;
  4318	    return conv[lo2] + tt * (conv[hi2] - conv[lo2]);
  4319	  };
  4320	  const out = new Array(N);
  4321	  for (let i = 0; i < N; i++) out[i] = interp(beArr[i]);
  4322	  let peakVal = interp(center);
  4323	  if (!(peakVal > 0)) { let mx = 0; for (let i = 0; i < N; i++) mx = Math.max(mx, Math.abs(out[i])); peakVal = mx; }
  4324	  if (!(peakVal > 0)) return new Array(N).fill(0);
  4325	  for (let i = 0; i < N; i++) { const v = out[i] / peakVal; out[i] = Number.isFinite(v) ? v : 0; }
  4326	  return out;
  4327	}
  4328	
  4329	// Compute per-peak intensities across an array of BE values. Special-cases
  4330	// LACX with non-zero m so the Gaussian convolution sees the whole grid, and
    65	| check | result |
    66	|---|---|
    67	| parity sweep (D), DS+G box α {0, 0.25, 0.49} × β {0.05, 0.7, 2} × m {0.001, 0.05, 0.4, 2, 4}, base grid | ≤ 3e-15 of amplitude (was 1e52 at β 2, m 0.05) — now a hard assertion |
    68	| (D′) the same box on: 0.1 eV step; 0.02 eV step; descending grid; centre half a step off-grid; descending + 0.03 eV off-grid; a 30-point window narrower than the pad; a 0.0503 eV step | < 1e-6 on every combination — hard assertions |
    69	| (A) DS+G at the base peak (was todo) | hard, passes |
    70	| round trip page → server → page, DS+G (was todo), and DS+G m locked at 0.05 and at 4 (curve comparison was disabled) | hard, pass |
    71	| (B) scalar vs array evaluator, DS+G | now `todo` like LACX: the convolution is a grid operation; guard (C) holds |
    72	| Find Peaks box (β 0.05, α 0–0.3, m 0.4–1.8, 0.05 and 0.1 eV grids) | agrees with the server to 1e-6 (was 5–21 % low in area) |
    73	| (D″) regressions: a centre 10 eV outside a [−5, 5] window; a 6-point irregular grid; alternating 0.05/0.06 steps (median ≠ mean); a 0.001 eV grid over 10 eV at β 2, m 4, α 0.49; 2- and 1-point grids | < 1e-6 (5e-12 relative on the outside-centre case whose server maximum is 48; 3.5e-13 at 0.001 eV) — hard; each curve under 2 s asserted |
    74	| (D″) m = 0.001, 0.002, 0.02, 0.05 on a 0.1 eV grid | page equals server at every m; at m ≤ 0.002 BOTH are an all-zero curve — a KNOWN SERVER LIMIT (§3a), pinned as such |
    75	
    76	### 3a. Server limit found on the way (not this unit's to change)
    77	
    78	Just above the 0.001 delta threshold on a coarse grid the server's Gaussian
    79	kernel underflows: σ = m/2.355 is far below the step, no padded-grid sample
    80	carries weight (for an even padded length the nearest sample is half a
    81	step from the centre), the kernel normalises to NaN and
    82	`_ds_g_dscore_gauss` returns an all-zero curve for the component (its final
    83	"suppress NaN/Inf" turns it to zeros). At 0.1 eV the zone is roughly
    84	0.001 ≤ m ≲ 0.004 and depends on the parity of the padded length; m = 0.02
    85	is already ordinary. A fit will not settle there (a zero curve fits
    86	nothing), but a LOCKED m in that zone is fitted as zero. The page mirrors
    87	it exactly (a vanished curve drawn as vanished, never a curve the server
    88	did not fit). Recorded for the owner; the fix belongs to the server (a
    89	kernel that collapses to a delta below the grid's resolution, as the
    90	threshold branch does).
    91	
    92	Nothing changed on the server, in `autofit/`, in Find Peaks or in the
    93	dropdown. Python suite untouched by this unit (no Python change); JS suite
    94	and browser check in §5.
    95	
    96	## 4. Sites
    97	
    98	`laCasaXPS` (rewritten), `dsgConvolved_array` (new), `evalPeakArray`;
   332	discretisation gap). DS+G with m ≥ 0.05: the page's `laCasaXPS` quadrature
   333	uses a step of 2·(6σ + 50β)/max(300, ⌈2·(6σ + 50β)/(β/3)⌉) — sized to the
   334	Lorentzian core, blind to the Gaussian kernel — so at β = 2, m = 0.05 the
   335	step is 0.67 eV against σ = 0.021 eV, the kernel weights sample nothing,
   336	and the page's curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's
   337	area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
   338	the 530 peak records in the seven committed projects use DS+G (and none of
   339	the 202 measurement targets), so no saved figure is affected; it is the
   340	fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
   341	FIXED the same day in `fix-dsg-page-evaluator` after the owner asked whether
   342	Find Peaks emits DS+G: it does (every A- and M-family C 1s candidate's
   343	graphitic main line, β fixed at 0.05, α 0–0.3, m 0.4–1.8), and on that box
   344	the page's area was 5–21 % low for α 0.15–0.3. `dsgConvolved_array` mirrors
   345	the server's padded-grid convolution by the same FFT circular convolution:
   346	≤ 3e-15 of amplitude across the whole β/m box on the base grid, < 1e-6
   347	(measured ≤ 5.5e-15) on seven other grids, and exact on the reviewers'
   348	reproducers (a centre outside the window, irregular grids, a 0.001 eV
   349	grid); nothing changed in Find Peaks or the dropdown
   350	(a science decision is not altered to work around a rendering bug —
   351	owner, 2026-09-22). The general lesson repeats §6's: a harness that
   352	evaluates one representative point per shape proves nothing about the range
   353	the optimiser can reach.

 succeeded in 8143ms:
{"label":"low-BE reproducer","n":21,"m":0.05,"center":-10,"err":24764730805051452,"jsMax":1,"pyMax":24764730805051452,"ms":1.0427709999999024}
{"label":"underflow","n":120,"m":0.001,"center":284.5,"err":0,"jsMax":0,"pyMax":0,"ms":5.338788999999906}
{"label":"underflow","n":120,"m":0.002,"center":284.5,"err":0,"jsMax":0,"pyMax":0,"ms":0.8390730000000985}
{"label":"underflow","n":120,"m":0.003,"center":284.5,"err":0,"jsMax":0,"pyMax":0,"ms":0.8157419999997728}
{"label":"underflow","n":120,"m":0.0031,"center":284.5,"err":5.773159728050814e-15,"jsMax":1.0163843751732473,"pyMax":1.0163843751732495,"ms":0.8067909999999756}
{"label":"underflow","n":120,"m":0.004,"center":284.5,"err":5.773159728050814e-15,"jsMax":1.0163843751732473,"pyMax":1.0163843751732495,"ms":0.954059000000143}
{"label":"underflow","n":120,"m":0.02,"center":284.5,"err":5.773159728050814e-15,"jsMax":1.0163843751732473,"pyMax":1.0163843751732495,"ms":0.5929049999999734}
{"label":"underflow","n":121,"m":0.001,"center":284.5,"err":8.215650382226158e-15,"jsMax":1.0332685438058575,"pyMax":1.0332685438058629,"ms":0.5546789999998509}
{"label":"underflow","n":121,"m":0.002,"center":284.5,"err":8.215650382226158e-15,"jsMax":1.0332685438058575,"pyMax":1.0332685438058629,"ms":0.600390999999945}
{"label":"underflow","n":121,"m":0.003,"center":284.5,"err":8.215650382226158e-15,"jsMax":1.0332685438058575,"pyMax":1.0332685438058629,"ms":0.5362860000000182}
{"label":"underflow","n":121,"m":0.0031,"center":284.5,"err":8.215650382226158e-15,"jsMax":1.0332685438058575,"pyMax":1.0332685438058629,"ms":0.5208170000000791}
{"label":"underflow","n":121,"m":0.004,"center":284.5,"err":8.215650382226158e-15,"jsMax":1.0332685438058575,"pyMax":1.0332685438058629,"ms":0.4920529999999417}
{"label":"underflow","n":121,"m":0.02,"center":284.5,"err":8.215650382226158e-15,"jsMax":1.0332685438058575,"pyMax":1.0332685438058629,"ms":0.4887410000001182}
{"label":"fine 2^18 FFT","n":10001,"m":4,"center":285,"err":3.459454944731988e-13,"jsMax":1.1548195640281882,"pyMax":1.1548195640281318,"ms":55.77859400000034}
sweeps {"free-box reproducer":{"label":"free-box reproducer","n":21,"m":0.05,"center":10,"err":48501712413941790,"jsMax":48501712413941790,"pyMax":1,"ms":1.2209789999997156},"box 0.05":{"label":"box 0.05","n":200,"m":0.05,"center":391.8,"err":1.9539925233402755e-14,"jsMax":1.0000000000000089,"pyMax":1,"ms":1.1806480000000192},"box 0.1":{"label":"box 0.1","n":120,"m":0.05,"center":391.8,"err":9.769962616701378e-15,"jsMax":1.120496504265489,"pyMax":1.1204965042654913,"ms":0.3519469999996545},"box 0.02":{"label":"box 0.02","n":500,"m":4,"center":391.8,"err":5.784261958297066e-14,"jsMax":1.000000000003924,"pyMax":1.0000000000039129,"ms":3.0238469999999325},"box 0.0503":{"label":"box 0.0503","n":181,"m":0.001,"center":391.8,"err":4.263256414560601e-14,"jsMax":1.1341191904426777,"pyMax":1.1341191904427204,"ms":1.026491999999962}}
100 fine-grid redraw evaluations {"medianMs":57.68336099999942,"maxMs":71.2211470000002,"before":{"rss":91033600,"heapTotal":16261120,"heapUsed":6977008,"external":2177815,"arrayBuffers":10475},"during":{"rss":353521664,"heapTotal":16261120,"heapUsed":10299488,"external":30678223,"arrayBuffers":28965179},"after":{"rss":353652736,"heapTotal":16523264,"heapUsed":6978056,"external":30678223,"arrayBuffers":26085083}}

codex
I found a new MAJOR parity failure within the free β/m bounds: on `[-5, 5]` at 0.5 eV spacing, with centre 10, α=0.49, β=0.05 and m=0.05, the page peaks at about `4.85e16 × amplitude`; the server peaks at `1 × amplitude`. The clamped normalization value is near zero, so FFT roundoff changes whether the fallback runs. I’m confirming that cause and checking the remaining documentation claims.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node --expose-gc -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const {evalPeakArray,_circularConvolve,_fftRadix2}=new Function(block+'\\'';return {evalPeakArray,_circularConvolve,_fftRadix2}'\\'')();

const trace=new Function(block.replace('\\''let peakVal = interp(center);'\\'','\\''let peakVal = interp(center); console.log(\"JS normalizer\", center, peakVal, \"nTot\", nTot, \"ksum\", ksum);'\\'')+'\\'';return evalPeakArray'\\'')();
for(const center of [10,-10])trace(Array.from({length:21},(_,i)=>(i-10)*.5),{shape:'\\''DSG_LA'\\'',amplitude:1,center,laAlpha:.49,laBeta:.05,laM:.05});
const py=\"import tempfile; tempfile.tempdir='\\''/tmp'\\''\\nimport numpy as np\\nfrom fitting import _ds_g_dscore_gauss\\nold=np.interp\\ndef traced(q,x,y):\\n r=old(q,x,y)\\n if np.ndim(q)==0: print('\\''Python normalizer'\\'',q,repr(r),'\\''nTot'\\'',len(x))\\n return r\\nnp.interp=traced\\nfor c in [10,-10]:\\n y=_ds_g_dscore_gauss(np.arange(-5,5.01,.5),1,c,.49,.05,.05)\\n print('\\''Python maximum'\\'',max(y))\";
console.log(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'',py],{encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']}));
(async()=>{const x=Array.from({length:10001},(_,i)=>280+.001*i),p={shape:'\\''DSG_LA'\\'',amplitude:1,center:285,laAlpha:.49,laBeta:2,laM:4};for(let b=0;b<3;b++){for(let i=0;i<50;i++)evalPeakArray(x,p);await new Promise(setImmediate);global.gc();await new Promise(setImmediate);global.gc();console.log('\\''GC batch'\\'',b,process.memoryUsage())}})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 10577ms:
Python normalizer 10 np.float64(-6.938893903907229e-20) nTot 25
Python maximum 1.0
Python normalizer -10 np.float64(1.7763568394002505e-17) nTot 25
Python maximum 2.4764730805051452e+16

GC batch 0 {
  rss: 239599616,
  heapTotal: 15212544,
  heapUsed: 5826280,
  external: 1683268,
  arrayBuffers: 10475
}
GC batch 1 {
  rss: 306675712,
  heapTotal: 15212544,
  heapUsed: 5852376,
  external: 1683308,
  arrayBuffers: 10475
}
GC batch 2 {
  rss: 358453248,
  heapTotal: 15212544,
  heapUsed: 5869728,
  external: 1683308,
  arrayBuffers: 10475
}

exec
/bin/zsh -lc "ps -eo pid,etime,args | rg 'node -e|lineshape_roundtrip_backend|lineshape_parity_backend' | cut -c 1-200; nl -ba tests/js/lineshape_parity.test.js | sed -n '160,171p'; nl -ba templates/index.html | sed -n '4218,4240p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
zsh:1: operation not permitted: ps
   160	//   evaluator used to be a numerical quadrature (laCasaXPS) whose step
   161	//   resolved the Lorentzian core (β/3) but not the Gaussian kernel, so it
   162	//   was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and by 4-14 % of
   163	//   amplitude on the very box Find Peaks emits for a graphitic C 1s line
   164	//   (β 0.05, α 0-0.3, m 0.4-1.8) — the A03 sweep, section (D) below. The
   165	//   m < 0.001 delta branch (dsgDeltaKernel_array) had been mirrored in
   166	//   2026-08; dsgConvolved_array now mirrors the server's padded-grid
   167	//   convolution for every m (≤ 3e-15 of amplitude across the fitted box,
   168	//   every grid step, orientation and off-grid centre tested below).
   169	//
   170	test('(A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)', { todo: 'unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)' }, () => {
   171	  const p = basePeak('LACX');
  4218	        re[i + k + len / 2] = ar - br; im[i + k + len / 2] = ai - bi;
  4219	        const ncr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = ncr;
  4220	      }
  4221	    }
  4222	  }
  4223	  if (inverse) for (let i = 0; i < n; i++) { re[i] /= n; im[i] /= n; }
  4224	}
  4225	
  4226	// Circular convolution of two real arrays of the same length n — what
  4227	// numpy's irfft(rfft(a)·rfft(b)) returns — as a zero-padded linear
  4228	// convolution (FFT length the power of two ≥ 2n − 1) folded back to n.
  4229	function _circularConvolve(a, b) {
  4230	  const n = a.length;
  4231	  let N = 1; while (N < 2 * n - 1) N <<= 1;
  4232	  const ar = new Float64Array(N), ai = new Float64Array(N), br = new Float64Array(N), bi = new Float64Array(N);
  4233	  for (let i = 0; i < n; i++) { ar[i] = a[i]; br[i] = b[i]; }
  4234	  _fftRadix2(ar, ai, false); _fftRadix2(br, bi, false);
  4235	  for (let i = 0; i < N; i++) { const r = ar[i] * br[i] - ai[i] * bi[i]; const im = ar[i] * bi[i] + ai[i] * br[i]; ar[i] = r; ai[i] = im; }
  4236	  _fftRadix2(ar, ai, true);
  4237	  const out = new Float64Array(n);
  4238	  for (let i = 0; i < n; i++) out[i] = ar[i] + (i + n < 2 * n - 1 ? ar[i + n] : 0);
  4239	  return out;
  4240	}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const child=require('\\''child_process'\\'');const original=child.execFileSync;child.execFileSync=function(file,args,opts){if(file.includes('\\''python'\\'')&&args[0]?.endsWith('\\''.py'\\''))return original(file,['\\''-c'\\'',\"import tempfile, runpy, sys; tempfile.tempdir='\\''/tmp'\\''; p=sys.argv.pop(1); runpy.run_path(p,run_name='\\''__main__'\\'')\",...args],opts);return original(file,args,opts)};const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const {evalPeakArray,_circularConvolve,_fftRadix2}=new Function(block+'\\'';return {evalPeakArray,_circularConvolve,_fftRadix2}'\\'')();

const x=Array.from({length:200},(_,i)=>391.8-5+.05*i);
const cases=[];for(const alpha of [0,.25,.49])for(const beta of [.05,.7,2])for(const m_gauss of [.001,.05,.4,2,4])cases.push({shape:'\\''ds_g'\\'',x,params:{amplitude:17794,center:391.8,alpha,beta,m_gauss}});
const ys=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''tests/js/lineshape_parity_backend.py'\\''],{input:JSON.stringify(cases),maxBuffer:32e6,encoding:'\\''utf8'\\'',stdio:['\\''pipe'\\'','\\''pipe'\\'','\\''ignore'\\'']}));
const worst=cases.map((c,i)=>{const p=c.params,y=evalPeakArray(x,{...p,shape:'\\''DSG_LA'\\'',laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss});return {...p,err:Math.max(...y.map((v,k)=>Math.abs(v-ys[i][k])))/p.amplitude}}).sort((a,b)=>b.err-a.err);console.log(worst.slice(0,3));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 1799ms:
[
  {
    amplitude: 17794,
    center: 391.8,
    alpha: 0,
    beta: 2,
    m_gauss: 0.05,
    err: 1.9422726012909563e-14
  },
  {
    amplitude: 17794,
    center: 391.8,
    alpha: 0.25,
    beta: 2,
    m_gauss: 0.05,
    err: 1.901382651790094e-14
  },
  {
    amplitude: 17794,
    center: 391.8,
    alpha: 0.49,
    beta: 2,
    m_gauss: 0.05,
    err: 1.7787128032875073e-14
  }
]

 succeeded in 143910ms:
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
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/.matplotlib is not a writable directory
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
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
  duration_ms: 8.859105
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 392 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 3.763861
  type: 'test'
  ...
1..392
# tests 392
# suites 0
# pass 387
# fail 0
# cancelled 0
# skipped 0
# todo 5
# duration_ms 143918.567472

codex
1. **MAJOR — near-zero normalization still causes catastrophic page/server divergence.** [templates/index.html:4322](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/templates/index.html:4322)

   Concrete reproducer: `x = [-5, -4.5, …, 5]`, amplitude `1`, centre `10`, α `0.49`, β `0.05`, m `0.05`. These β/m values are within the free fitting bounds.

   The page’s maximum is **4.85017e16**; the server’s maximum is **1**. Their clamped normalization values are respectively `+4.62712e-20` and `−6.93889e-20`. FFT roundoff therefore makes the page divide by numerical noise while the server takes its fallback.

   Moving the centre to **−10** reverses the failure: page maximum **1**, server maximum **2.47647e16**. Circular-convolution algebra is correct, but the strict-positive normalization decision makes numerical equivalence fail. Both directions need regression coverage and consistent handling.

2. **MINOR — precision claims remain overstated after the FFT replacement.** [docs/findings/2026-09-fit-determinacy.md:346](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/docs/findings/2026-09-fit-determinacy.md:346), [plan:67](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md:67), [tests/js/lineshape_parity.test.js:167](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:167)

   On the exact base grid, α `0`, β `2`, m `0.05` produces **1.9423e-14 of amplitude**, exceeding the claimed `3e-15`. The 0.02 eV grid reaches approximately **5.78e-14**, exceeding the findings’ `5.5e-15`. The actual hard assertion is `1e-6`; these results comfortably pass it. Update the measured claims and remove “exact” for the reproducers.

Round-1 closure:

- **Clipped convolution:** original reproducers pass; clipping is fixed. The distinct normalization failure above remains.
- **Quadratic cost:** closed. Fine-grid evaluations measured approximately **58 ms median**, versus 13.5 seconds previously.
- **Vacuous coverage:** closed for the reported gaps. Genuine irregular-grid and explicit vanished-curve tests pass.
- **Documentation overstatement:** partially corrected; finding 2 remains.

Other adversarial checks:

- Direct circular convolution agreed within `1.87e-14` for lengths 1–100, covering odd/even folds. The only integer case where `2n−1` itself is a power of two is `n=1`; it passed.
- FFT round-trip error at `2^18` was `7.4e-12`; the normalized fine-grid DS+G discrepancy was `3.46e-13`.
- Even-count median, endpoint behavior, broad β through 100, and page routing checks passed.
- Zero-kernel NaN handling matches. At 0.1 eV spacing, even-length curves vanish at m `0.003` but recover by `0.0031`; odd-length curves remain nonzero at `0.001`. §3a’s approximate `0.004` boundary is too broad.
- Repeated fine-grid evaluations reclaimed typed arrays after GC; substantial transient RSS occurred, but no retained-array leak was established. Browser redraw behavior was not measured.

**Validation:** 392 tests, **387 pass, 0 fail, 5 todo**, using an in-memory workaround for Python’s temporary-directory probe under the read-only sandbox. No files changed.

**VERDICT: NO-GO.**
tokens used
72,814
1. **MAJOR — near-zero normalization still causes catastrophic page/server divergence.** [templates/index.html:4322](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/templates/index.html:4322)

   Concrete reproducer: `x = [-5, -4.5, …, 5]`, amplitude `1`, centre `10`, α `0.49`, β `0.05`, m `0.05`. These β/m values are within the free fitting bounds.

   The page’s maximum is **4.85017e16**; the server’s maximum is **1**. Their clamped normalization values are respectively `+4.62712e-20` and `−6.93889e-20`. FFT roundoff therefore makes the page divide by numerical noise while the server takes its fallback.

   Moving the centre to **−10** reverses the failure: page maximum **1**, server maximum **2.47647e16**. Circular-convolution algebra is correct, but the strict-positive normalization decision makes numerical equivalence fail. Both directions need regression coverage and consistent handling.

2. **MINOR — precision claims remain overstated after the FFT replacement.** [docs/findings/2026-09-fit-determinacy.md:346](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/docs/findings/2026-09-fit-determinacy.md:346), [plan:67](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md:67), [tests/js/lineshape_parity.test.js:167](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:167)

   On the exact base grid, α `0`, β `2`, m `0.05` produces **1.9423e-14 of amplitude**, exceeding the claimed `3e-15`. The 0.02 eV grid reaches approximately **5.78e-14**, exceeding the findings’ `5.5e-15`. The actual hard assertion is `1e-6`; these results comfortably pass it. Update the measured claims and remove “exact” for the reproducers.

Round-1 closure:

- **Clipped convolution:** original reproducers pass; clipping is fixed. The distinct normalization failure above remains.
- **Quadratic cost:** closed. Fine-grid evaluations measured approximately **58 ms median**, versus 13.5 seconds previously.
- **Vacuous coverage:** closed for the reported gaps. Genuine irregular-grid and explicit vanished-curve tests pass.
- **Documentation overstatement:** partially corrected; finding 2 remains.

Other adversarial checks:

- Direct circular convolution agreed within `1.87e-14` for lengths 1–100, covering odd/even folds. The only integer case where `2n−1` itself is a power of two is `n=1`; it passed.
- FFT round-trip error at `2^18` was `7.4e-12`; the normalized fine-grid DS+G discrepancy was `3.46e-13`.
- Even-count median, endpoint behavior, broad β through 100, and page routing checks passed.
- Zero-kernel NaN handling matches. At 0.1 eV spacing, even-length curves vanish at m `0.003` but recover by `0.0031`; odd-length curves remain nonzero at `0.001`. §3a’s approximate `0.004` boundary is too broad.
- Repeated fine-grid evaluations reclaimed typed arrays after GC; substantial transient RSS occurred, but no retained-array leak was established. Browser redraw behavior was not measured.

**Validation:** 392 tests, **387 pass, 0 fail, 5 todo**, using an in-memory workaround for Python’s temporary-directory probe under the read-only sandbox. No files changed.

**VERDICT: NO-GO.**
