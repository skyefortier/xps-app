OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f7212-a2ff-7650-a4c1-ffa36726da69
--------
user
You are an adversarial reviewer for a scoped bug-fix commit in this repo
(XPS peak-fitting web app). Review commit 3d9ff54 ("fix(fitting):
Tougaard pre-loss constant (F1) + non-uniform quadrature weights (F2)") on
branch feature-autofit-stage2 — `git show 3d9ff54` gives the full
diff. This commit was originally drafted as part of a larger patch written
in a sandbox WITHOUT access to this real worktree; it has since been
independently re-verified here, but treat it as unproven until you confirm
it yourself. Read-only sandbox is fine; if pytest is runnable, run it —
otherwise read everything and reason from the diff plus static analysis.

SCOPE OF THE CHANGE (verify it is contained):
- fitting.py: ONLY tougaard_background (signature, docstring, body).
  Nothing else in fitting.py may have changed. In particular,
  shirley_background, smart_background, _apply_endpoint_averaging, and
  _compute_background in autofit/engine.py must be UNTOUCHED by this
  commit — their n_avg/endpoint_avg unification is a deliberately separate
  Unit 2, not yet applied. Confirm autofit/engine.py has zero diff.
- templates/index.html: ONLY the tougaardBackground JS function (+ its
  leading comment). computeBackgroundCore and _applyEndpointAveraging are
  unmodified — their two call sites into tougaardBackground still use the
  pre-existing external-pre-averaging convention (no 3rd argument passed).
- tests/test_tougaard_background.py, tests/js/tougaard_twin.test.js.
- No changes to /api/fit's contract, autofit/methods/*.py, or peak
  lineshapes.

BACKGROUND — WHY THIS CHANGED (reported bug, F1):

The previous tougaard_background computed the idealized integral
B(E) = Σ_{E' < E} K(E-E')·J(E') with K(T) = B·T/(C+T²)² (B=2866, C=1643,
Tougaard 1988). This assumes the analysis window begins in a loss-free
region. Real XPS windows never do — e.g. at Fe 2p (~700 eV BE) there is a
large inelastic baseline from every lower-BE/higher-KE transition OUTSIDE
the window, which a window-limited integral structurally cannot generate.
Because K(0) = 0, the bare integral is identically zero at the low-BE
edge REGARDLESS OF THE DATA: measured on a synthetic Fe 2p region, old
behavior gave low-BE edge bg=0.0 (data=4000, net=4000 — "the dive"), and a
flat 500-count featureless window produced a full-amplitude phantom
signal (net spanning 0..500 with nothing there to model).

THE FIX: take the low-BE edge level (post any n_avg endpoint-averaging) as
a constant C0 (the out-of-window pre-loss baseline the kernel cannot see),
run the kernel over the net (J - C0), then anchor amplitude at the
high-BE edge exactly as before (out = c0 + bg * ((ya[0]-c0)/bg[0])).
Degenerate-window guard changed: when bg[0] == 0 (no net loss signal —
e.g. a flat window), the function now returns flat C0 instead of all
zeros, because zeros would report the entire baseline as net signal (the
exact F1 failure mode).

SECOND FIX BUNDLED IN THE SAME FUNCTION (F2, non-uniform grid quadrature):

The non-uniform branch (exact per-point separations, for grids that don't
support the np.convolve shortcut) used the correct kernel value K(T) per
point but never weighted by the local spacing — i.e. it silently applied
uniform-grid quadrature inside the branch written precisely because the
grid is not uniform. Measured ~23.7% error vs a spacing-weighted reference
on a genuinely non-uniform (dense/sparse-halves) grid. Fixed by weighting
each term by np.abs(np.gradient(xa)) — which returns dx exactly on a
uniform grid, so both branches now agree to floating point and the
uniformity test is a pure optimization, not a semantic fork. The old
dead `bg = bg * dx` (previously applied AFTER the sum, to both branches
alike, and canceling exactly against the anchor normalization) is removed;
in the uniform branch dx is now applied once inline against np.convolve's
result, and the nonuniform branch's per-point `w` supplies the equivalent
role directly in the sum.

WHY THESE TWO ARE BUNDLED IN ONE COMMIT, NOT SPLIT: both fixes live in the
same function body and were only ever tested together by the original
patch author (no verified intermediate state exists with F1 applied but
not F2, or vice versa). Splitting them would require hand-authoring an
untested intermediate — judged riskier than reviewing them together. F3
(n_avg convention unification for shirley/smart + engine.py wiring) IS
naturally independent and is deliberately held for a separate Unit 2 commit,
landing after this one.

ADVERSARIAL QUESTIONS — ATTACK THESE SPECIFICALLY:

(a) C0 CHOICE. Is taking C0 from the single (or n_avg-averaged) low-BE
    edge point the right pre-loss estimate, versus e.g. a fitted constant
    (joint least-squares over B and C0) or a wider pre-peak average window
    (more than n_avg points, e.g. a fixed fraction of the ROI)? Under what
    realistic spectra (e.g. a region where the loss tail itself extends
    across most of the window) does an edge-point C0 give a visibly wrong
    answer? Is n_avg (when the caller passes n_avg>1) a sufficient mitigant,
    or just cosmetic?

(b) NEGATIVE-SCALE ANCHORING. The anchor is
    `out = c0 + bg * ((ya[0] - c0) / bg[0])`. If the baseline FALLS with
    increasing BE — i.e. ya[0] (high-BE edge, post any averaging) is LESS
    than c0 (low-BE edge) — the scale factor is negative, and it is passed
    through signed with no clamping, consistent with this codebase's
    existing no-clamping stance elsewhere in fitting.py. Construct a
    concrete (x, y) input where this produces a background that inverts the
    kernel shape (goes negative in the middle of the window, or overshoots
    past the data) and assess whether that is merely "an unclamped
    pathological input" (acceptable, matches project philosophy) or an
    actual correctness bug that would fire on realistic data (e.g. a region
    with a decaying secondary electron background, not just adversarial
    input).

(c) SAVED-FIT / FIXTURE PINNING. Grep the full repo (tests/, tests/autofit/,
    docs/autofit/inventory/, scripts/, any .json/.proj.json/.proj.zip
    fixtures) for anything that pins a Tougaard background NUMERIC VALUE —
    not just the string "tougaard". The claim is that nothing outside the
    2 test files touched in this commit encodes the old (pre-F1) Tougaard
    output, so no other test silently regresses. Verify independently.

TESTS TO INTERROGATE — DO THESE ACTUALLY DISCRIMINATE, AND ARE THE TWO
REWRITTEN TESTS LEGITIMATE OR A LAUNDERED BUG:

- test_background_anchored_at_high_be_edge: previously asserted
  `bg[-1] == 0.0` (the low-BE edge) — that assertion WAS the bug, pinned as
  if it were correct behavior. Now asserts `bg[-1] == y[-1]` (meets C0).
  Confirm the new assertion is actually meaningful (not trivially true for
  all inputs) and that reverting fitting.py's C0 logic would make this test
  fail.
- test_no_loss_signal_returns_unanchored_zeros, renamed to
  test_no_loss_signal_returns_flat_pre_loss_level: the degenerate-window
  guard still exists; only the fallback value changed 0 -> C0. In this
  test's specific fixture C0 happens to be 0, so the numeric assertion is
  UNCHANGED — only the name/rationale moved. Confirm this is true (i.e. the
  fixture's low-BE edge really is 0) and that the test still exercises the
  `bg[0] == 0.0` guard branch (not some other code path).
- test_kernel_peak_near_sqrt_c_over_3: needed a non-zero high-BE step added
  to its fixture (a flat pedestal alone has zero net loss signal post-F1,
  so there's no kernel shape left to inspect). Confirm the C=1643**2
  regression guard (the OLDER 2026-07-04 transcription-slip bug) still
  fires correctly against this modified fixture.
- The 4 new tests (flat-window-zero-net, low-BE-baseline-tracking,
  non-uniform-quadrature-weights, both-edge-anchoring): for each, would it
  fail on the pre-F1/F2 code and pass on the current code? Is
  test_nonuniform_grid_uses_local_quadrature_weights's reference
  implementation independent enough to be a real regression guard, or does
  it share enough structure with the production code that it would pass
  even if both were wrong the same way?
- JS twin: confirm the regenerated cross-twin expected-value table was
  generated from the ACTUAL current fitting.py (not hand-computed or
  copied from the sandbox), and that tougaard_twin.test.js still evals the
  real tougaardBackground out of templates/index.html rather than a
  reimplementation.

CALLERS. fitting.py dispatches tougaard_background at the /api/background
and /api/fit background paths; autofit reaches it via BackgroundType.TOUGAARD
in autofit/engine.py (UNCHANGED by this commit — still calls the 2-arg form,
which remains valid since n_avg defaults to 1) and autofit/parity.py. The
frontend calls tougaardBackground at ~2 sites inside computeBackgroundCore.
Verify every caller still gets a valid call with this commit alone applied
(i.e. before Unit 2 adds the endpoint_avg wiring).

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll inspect the scoped commit as a review, then run the available focused tests if the read-only sandbox permits it. I’ll also grep fixtures and callers rather than relying on the commit description.
exec
/bin/zsh -lc 'git diff --name-only 3d9ff54''^ 3d9ff54' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-dMauPTTg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yNI8jiWY' (errno=Operation not permitted)
fitting.py
templates/index.html
tests/js/tougaard_twin.test.js
tests/test_tougaard_background.py

exec
/bin/zsh -lc 'git show --stat --oneline --decorate --name-only 3d9ff54' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5aVho6Mb' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BziiQLzt' (errno=Operation not permitted)
3d9ff54 fix(fitting): Tougaard pre-loss constant (F1) + non-uniform quadrature weights (F2)
fitting.py
templates/index.html
tests/js/tougaard_twin.test.js
tests/test_tougaard_background.py

exec
/bin/zsh -lc 'git show --format=fuller --no-ext-diff --find-renames 3d9ff54 -- fitting.py templates/index.html tests/test_tougaard_background.py tests/js/tougaard_twin.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-WpRDcWUX' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZWGs6nzE' (errno=Operation not permitted)
commit 3d9ff542e5b341717b4967f085d6bb22380dfdbf
Author:     Skye Fortier <skyefortier@gmail.com>
AuthorDate: Fri Jul 17 15:50:56 2026 -0600
Commit:     Skye Fortier <skyefortier@gmail.com>
CommitDate: Fri Jul 17 15:50:56 2026 -0600

    fix(fitting): Tougaard pre-loss constant (F1) + non-uniform quadrature weights (F2)
    
    Tougaard background used the idealized integral B(E) = Σ_{E'<E} K(E-E')·J(E'),
    which assumes the analysis window begins loss-free. Real windows never do
    (e.g. Fe 2p sits on a large inelastic baseline from transitions outside the
    window), and because K(0)=0 the bare integral is identically zero at the
    low-BE edge regardless of the data — background dove to ~0 there, and a
    flat featureless window produced a full-amplitude phantom signal.
    
    Fix: take the low-BE edge level as a pre-loss constant C0, run the kernel
    over the net (J - C0), anchor amplitude at the high-BE edge as before.
    Tougaard now meets the data at both edges, like Shirley. Degenerate-window
    guard now returns flat C0 instead of all-zeros (zeros would report the
    whole baseline as net signal — the exact failure this fixes).
    
    Bundled in the same function body: the non-uniform-grid branch computed
    exact per-point separations but never weighted by local spacing, silently
    applying uniform-grid quadrature inside the branch written because the
    grid isn't uniform (~23.7% measured error). Fixed via np.gradient-based
    local weights, which reduce to dx exactly on a uniform grid. Dead
    `bg = bg * dx` (previously canceled exactly against the anchor) removed.
    
    tougaard_background also gains n_avg (default 1, no-op), matching the
    convention already used by smart_experimental_background /
    shirley_linear_background — needed so the anchor/C0 endpoints aren't read
    from a single noisy sample when a caller opts in. All existing callers use
    the 2-arg form and are unaffected.
    
    Originally drafted as part of a larger sandboxed patch (no access to this
    worktree) covering 3 findings; independently re-verified here and split
    into 2 units for review. This unit bundles F1+F2 because both live in the
    same function body and were only ever tested together upstream — splitting
    further would mean hand-authoring an untested intermediate. F3 (n_avg
    convention unification for shirley_background/smart_background +
    autofit/engine.py wiring) is a separate, naturally-independent Unit 2.
    
    Two existing tests encoded the old (buggy) behavior and are rewritten,
    not just added to:
    - test_background_anchored_at_high_be_edge asserted bg[-1] == 0.0 at the
      low-BE edge — that assertion WAS the bug, pinned. Now asserts
      bg[-1] == y[-1] (meets C0).
    - test_no_loss_signal_returns_unanchored_zeros (2026-07-04 pin) renamed to
      test_no_loss_signal_returns_flat_pre_loss_level; guard still exists, only
      the fallback value changed 0 -> C0 (numerically unchanged in this
      fixture since C0 == 0 there).
    test_kernel_peak_near_sqrt_c_over_3 needed a non-zero high-BE step added
    (a flat pedestal has no loss signal to model post-fix). The C=1643**2
    transcription-slip regression guard still fires against the modified
    fixture.
    
    Verification: tests/test_tougaard_background.py 9/9, tests/js/ 114/114
    (incl. regenerated tougaard_twin.test.js cross-language table), full
    pytest suite 666 passed / 6 skipped / 0 failed (browser suites included).
    Confirmed via git grep: no saved-fit fixture or inventory JSON pins
    Tougaard output anywhere in the repo. Scope: fitting.py's
    tougaard_background, templates/index.html's tougaardBackground JS twin,
    and their 2 test files only — zero changes to autofit/engine.py,
    autofit/methods/*.py, or /api/fit's contract.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

diff --git a/fitting.py b/fitting.py
index ee26392..ae08d1e 100644
--- a/fitting.py
+++ b/fitting.py
@@ -505,21 +505,49 @@ def shirley_linear_background(
     return result[::-1] if flipped else result
 
 
-def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-    """Simplified single-pass Tougaard universal-cross-section background.
+def tougaard_background(
+    x: np.ndarray,
+    y: np.ndarray,
+    n_avg: int = 1,
+) -> np.ndarray:
+    """Single-pass Tougaard universal-cross-section background, with the
+    constant (pre-loss) term the window-limited integral cannot generate.
 
     Uses the two-parameter universal loss function
     K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
     (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
     cross-section fitted to noble/transition-metal optical data; the
-    kernel maximum sits at T = sqrt(C/3) ≈ 23.4 eV energy loss).
+    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).
+
+    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
+    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
+    window BEGINS in a loss-free region, so that J at the low-BE edge is
+    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
+    there is a large inelastic baseline produced by every lower-BE
+    (higher-KE) transition OUTSIDE the window, which a window-limited
+    integral structurally cannot reproduce.  Because K(0) = 0, the bare
+    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
+    — the background visibly dove to ~0 there, and a flat featureless
+    window produced a full-amplitude phantom "signal".
+
+    So the low-BE edge level is taken as a constant offset C0 (the
+    out-of-window baseline the kernel cannot see), the kernel runs over the
+    net (J - C0), and the amplitude is then anchored so the background
+    meets the measured intensity at the HIGH-BE edge — the standard
+    practical Tougaard criterion (B is effectively fitted, which is why the
+    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
+    fitting B together with an offset rather than B alone.
+
+    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
+    levels are read, so neither C0 nor the high-BE anchor rests on a single
+    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
+    endpoints = previous behaviour.
 
     The background at each binding energy accumulates loss contributions
     from electrons emitted at LOWER BE (higher kinetic energy), so the
     one-sided sum requires a descending-BE grid; input in either BE order
-    is normalized internally (see below). The amplitude is anchored so the
-    background matches the measured intensity at the high-BE edge of the
-    window, matching the frontend JS twin ``tougaardBackground``.
+    is normalized internally.  Mirrors the frontend JS twin
+    ``tougaardBackground``.
     """
     n = len(x)
     if n < 2:
@@ -534,6 +562,8 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
 
     xa = np.asarray(x, dtype=float)
     ya = np.asarray(y, dtype=float)
+    if n_avg > 1:
+        ya = _apply_endpoint_averaging(ya, n_avg)
 
     # The one-sided loss sum below (j >= i) is physical only when BE
     # DESCENDS along the array: the loss contributions at x[i] must come
@@ -545,17 +575,29 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
     if flipped:
         xa, ya = xa[::-1].copy(), ya[::-1].copy()
 
+    # C0: the low-BE edge level = index -1 on the descending working array.
+    # This is the out-of-window (pre-loss) baseline; the kernel integral is
+    # run on the net above it.
+    c0 = float(ya[-1])
+    net = ya - c0
+
     dx = float(abs(xa[1] - xa[0]))
 
-    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·y[j],  K(T) = B·T / (C + T²)².
+    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·net[j]·w[j],  K(T) = B·T / (C + T²)²,
+    # w[j] = the local quadrature weight (energy spacing) at point j.
     #
-    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx, so the kernel depends
-    # only on the index gap and this one-sided correlation collapses to a
-    # convolution against a single precomputed kernel vector — evaluated in C
-    # via np.convolve instead of an n-iteration Python loop (audit F7). On a
-    # NONUNIFORM grid that identity does not hold, so we keep the exact
-    # per-point separation loop (slower, but numerically unchanged). Never
-    # substitute (j-i)·dx for the true separation unless uniformity is verified.
+    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx and w[j] == dx, so the
+    # kernel depends only on the index gap and this one-sided correlation
+    # collapses to a convolution against a single precomputed kernel vector —
+    # evaluated in C via np.convolve instead of an n-iteration Python loop
+    # (audit F7). On a NONUNIFORM grid neither identity holds, so we keep the
+    # exact per-point separation loop AND per-point weights (audit F2,
+    # 2026-07-17: the loop previously used exact separations but omitted the
+    # spacing weights, silently applying a uniform-grid quadrature inside the
+    # branch written precisely because the grid is not uniform — up to ~24%
+    # error on a genuinely nonuniform grid). np.gradient returns dx exactly
+    # on a uniform grid, so both branches agree to floating point and the
+    # uniformity test is a pure optimization, not a semantic fork.
     diffs = np.diff(xa)
     uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)
 
@@ -563,36 +605,30 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
         m = np.arange(n, dtype=float)
         T = m * dx
         k = (B_coef * T) / (C_coef + T * T) ** 2          # k[m] = K(m·dx)
-        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·y[i+m]  =  conv(y, reverse(k))[n-1+i]
-        bg = np.convolve(ya, k[::-1])[n - 1:]
+        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·net[i+m]  =  conv(net, reverse(k))[n-1+i]
+        bg = np.convolve(net, k[::-1])[n - 1:] * dx
     else:
+        w = np.abs(np.gradient(xa))
         bg = np.zeros(n)
         for i in range(n):
             T = np.abs(xa[i:] - xa[i])
             kernel = (B_coef * T) / (C_coef + T * T) ** 2
-            bg[i] = float(np.sum(kernel * ya[i:]))
-
-    bg = bg * dx
+            bg[i] = float(np.sum(kernel * net[i:] * w[i:]))
 
-    # Amplitude anchor: scale the correlation so the background equals the
+    # Amplitude anchor: scale the loss integral so the background equals the
     # measured intensity at the HIGH-BE edge (index 0 on the descending
-    # working array) — the standard practical Tougaard criterion, i.e. B is
-    # effectively fitted so the background meets the spectrum above the
-    # peak (which also makes the nominal B_coef cancel; C alone sets the
-    # kernel shape). History: this used to "rescale to the trailing
-    # endpoint", but K(0) = 0 makes bg[-1] identically zero, so the
-    # zero-guard always fired and the code multiplied by the raw trailing
-    # counts instead — a scale that is harmless only while the squared-C
-    # kernel kept bg near zero, and off by ~the baseline counts once C is
-    # corrected. Guard semantics: if NO net loss signal accumulates at the
-    # high-BE edge (bg[0] == 0 — e.g. all counts zero, or zero everywhere
-    # below the edge point), the correlation is returned UNANCHORED (all
-    # zeros in practice) rather than force-matched to the edge intensity.
-    # Negative counts (physically invalid input) pass through signed; no
-    # clamping policy is imposed here.
-    denom = bg[0] if bg[0] != 0.0 else 1.0
-    bg = bg * (float(ya[0]) / denom)
-    return bg[::-1] if flipped else bg
+    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
+    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
+    # flat or empty window), the honest background is the flat pre-loss level
+    # C0 itself, NOT zeros: a featureless window contains no loss signal to
+    # model, and returning zeros would report the entire baseline as net
+    # signal (the pre-F1 behaviour). Negative counts (physically invalid
+    # input) pass through signed; no clamping policy is imposed here.
+    if bg[0] == 0.0:
+        out = np.full(n, c0)
+    else:
+        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])
+    return out[::-1] if flipped else out
 
 
 def _la_casaxps_true(
diff --git a/templates/index.html b/templates/index.html
index 173e1c1..61ff8a7 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4133,7 +4133,7 @@ function linearBackground(be, intensity) {
 // K(T) = B·T/(C+T²)² with B = 2866 eV², C = 1643 eV² (S. Tougaard,
 // Surf. Interface Anal. 11, 453 (1988); kernel max at sqrt(C/3) ≈ 23.4 eV).
 // C was long shipped squared (1643*1643) — fixed 2026-07-04 with the backend.
-function tougaardBackground(be, intensity) {
+function tougaardBackground(be, intensity, nAvg) {
   const n = be.length;
   if (n < 2) return new Array(n).fill(0);
   const B = 2866, C = 1643;
@@ -4142,29 +4142,51 @@ function tougaardBackground(be, intensity) {
   // Normalize to descending internally and flip back, like the backend.
   const flipped = be[0] < be[n - 1];
   const beW = flipped ? [...be].reverse() : be;
-  const inW = flipped ? [...intensity].reverse() : intensity;
-  const dx = Math.abs(beW[1] - beW[0]);
+  let inW = flipped ? [...intensity].reverse() : intensity;
+  if (nAvg > 1) inW = _applyEndpointAveraging(inW, nAvg);
+  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
+  // integral assumes the window BEGINS loss-free, so J at the low-BE edge is
+  // the zero-loss level. Real windows never satisfy that: the out-of-window
+  // inelastic baseline from every lower-BE (higher-KE) transition cannot be
+  // reproduced by a window-limited integral, and since K(0) = 0 the bare
+  // integral is identically zero at the low-BE edge REGARDLESS of the data —
+  // the background dove to ~0 there and a flat window produced phantom
+  // signal. Take the low-BE level as a constant offset, run the kernel over
+  // the net above it, then anchor the amplitude at the high-BE edge.
+  const c0 = inW[n - 1];
+  // Local quadrature weights (F2, 2026-07-17): weight each term by its own
+  // energy spacing instead of a single dx lifted from the first two points,
+  // which silently assumed a uniform grid.
+  const w = new Array(n);
+  for (let i = 0; i < n; i++) {
+    if (i === 0) w[0] = Math.abs(beW[1] - beW[0]);
+    else if (i === n - 1) w[n - 1] = Math.abs(beW[n - 1] - beW[n - 2]);
+    else w[i] = Math.abs(beW[i + 1] - beW[i - 1]) / 2;
+  }
   const bg = new Array(n).fill(0);
   for (let i = 0; i < n; i++) {
     let sum = 0;
     for (let j = i; j < n; j++) {
       const T = Math.abs(beW[j] - beW[i]);
-      sum += (B * T) / Math.pow(C + T * T, 2) * inW[j];
+      sum += (B * T) / Math.pow(C + T * T, 2) * (inW[j] - c0) * w[j];
     }
-    bg[i] = sum * dx;
+    bg[i] = sum;
   }
   // Amplitude anchor at the HIGH-BE edge (index 0 after normalization):
   // scale so the background meets the measured intensity above the peak —
-  // the practical Tougaard criterion (B effectively fitted; C alone sets
-  // the kernel shape). The old code "rescaled to the trailing endpoint",
-  // but K(0)=0 makes bg[n-1] identically zero, so the || 1 guard always
-  // fired and it multiplied by raw trailing counts instead. Guard
-  // semantics: if no net loss signal accumulates at the high-BE edge
-  // (bg[0] === 0), the correlation is returned UNANCHORED (all zeros in
-  // practice) rather than force-matched to the edge. Negative counts
+  // the practical Tougaard criterion (B effectively fitted; C alone sets the
+  // kernel shape). Guard: if no net loss signal accumulates at the high-BE
+  // edge (bg[0] === 0 — e.g. a flat or empty window) the honest background is
+  // the flat pre-loss level C0 itself, NOT zeros; zeros would report the
+  // whole baseline as net signal (the pre-F1 behaviour). Negative counts
   // (physically invalid input) pass through signed; no clamping here.
-  const scale = inW[0] / (bg[0] || 1);
-  const out = bg.map(v => v * scale);
+  let out;
+  if (bg[0] === 0) {
+    out = new Array(n).fill(c0);
+  } else {
+    const scale = (inW[0] - c0) / bg[0];
+    out = bg.map(v => c0 + v * scale);
+  }
   return flipped ? out.reverse() : out;
 }
 
diff --git a/tests/js/tougaard_twin.test.js b/tests/js/tougaard_twin.test.js
index 668c2a4..7b64aaf 100644
--- a/tests/js/tougaard_twin.test.js
+++ b/tests/js/tougaard_twin.test.js
@@ -48,8 +48,14 @@ test('loss-kernel response peaks ~23.4 eV above a delta-like peak', () => {
   const be = [], intensity = [];
   for (let i = 0; i < n; i++) {
     be.push(100.0 - 0.1 * i);      // descending 100 → 0 eV
-    intensity.push(1e-9);          // pedestal keeps the amplitude anchor finite
+    intensity.push(1e-9);
   }
+  // A high-BE step is required since the F1 offset fix (2026-07-17): the
+  // fitted amplitude is proportional to the measured rise across the window
+  // (high-BE edge minus the low-BE pre-loss level), so a perfectly flat
+  // pedestal has no loss intensity to model and yields a flat background with
+  // no kernel shape to inspect. Mirrors the Python twin test.
+  intensity[0] = 2e-9;
   const spikeIdx = 800;            // be = 20.0 eV
   intensity[spikeIdx] = 1e6;
 
@@ -76,17 +82,35 @@ test('ascending and descending BE input give the identical background', () => {
   }
 });
 
-test('background anchored to the data at the high-BE edge, zero at low-BE edge', () => {
+test('background meets the data at BOTH edges (high-BE anchor, low-BE C0)', () => {
   const { be, intensity } = syntheticSpectrum();
   const bg = tougaardBackground(be, intensity);
   const rel = Math.abs(bg[0] - intensity[0]) / intensity[0];
   assert.ok(rel < 1e-12,
     `high-BE-edge anchor broken: bg[0] = ${bg[0]}, data = ${intensity[0]}`);
-  assert.strictEqual(bg[bg.length - 1], 0);
+  // Since the F1 offset fix (2026-07-17) the low-BE edge carries the pre-loss
+  // constant C0, NOT zero. K(0)=0 still kills the LOSS integral there, so the
+  // background equals C0 exactly. Asserting 0 pinned the bug: it forced the
+  // background to dive to zero regardless of the data.
+  const last = bg.length - 1;
+  const relLow = Math.abs(bg[last] - intensity[last]) / intensity[last];
+  assert.ok(relLow < 1e-12,
+    `low-BE edge should sit on C0 = ${intensity[last]}, got ${bg[last]}`);
+});
+
+test('flat window yields no phantom signal (F1 regression pin)', () => {
+  const be = [], intensity = [];
+  for (let i = 0; i < 200; i++) { be.push(740.0 - 40.0 * i / 199); intensity.push(500.0); }
+  const bg = tougaardBackground(be, intensity);
+  for (let i = 0; i < bg.length; i++) {
+    assert.ok(Math.abs(intensity[i] - bg[i]) < 1e-6,
+      `flat window must leave ~zero net; net ${intensity[i] - bg[i]} at ${i}`);
+  }
 });
 
 test('agrees with the backend implementation (fitting.py) on the same spectrum', () => {
-  // Expected values generated by the CORRECTED backend on 2026-07-04:
+  // Expected values regenerated against the backend on 2026-07-17 after the
+  // F1 (pre-loss constant C0) + F2 (local quadrature weights) fixes:
   //   venv/bin/python - <<'EOF'
   //   import numpy as np; from fitting import tougaard_background
   //   x = np.linspace(295.0, 280.0, 151)
@@ -99,12 +123,12 @@ test('agrees with the backend implementation (fitting.py) on the same spectrum',
   // reviewed reason. Tolerance 1e-9 relative: np.convolve vs the JS loop
   // differ only by floating-point summation order.
   const expected = {
-    0: 100.1341400521866,
-    30: 68.83942567577668,
-    75: 17.647993800534383,
-    110: 3.6432237281257964,
-    149: 0.0045035685195542186,
-    150: 0.0,
+    0: 100.13414005218658,
+    30: 219.3991381848062,
+    75: 461.76541491579644,
+    110: 499.7312788702072,
+    149: 499.6355795222399,
+    150: 499.6355795222399,
   };
   const { be, intensity } = syntheticSpectrum();
   const bg = tougaardBackground(be, intensity);
diff --git a/tests/test_tougaard_background.py b/tests/test_tougaard_background.py
index 51ec8ca..84cb4ca 100644
--- a/tests/test_tougaard_background.py
+++ b/tests/test_tougaard_background.py
@@ -59,7 +59,15 @@ def test_kernel_peak_near_sqrt_c_over_3():
     kernel maximum.
     """
     x = np.linspace(100.0, 0.0, 1001)  # descending, dx = 0.1 eV
-    y = np.full_like(x, 1e-9)  # tiny pedestal keeps the amplitude anchor finite
+    # A pedestal PLUS a high-BE step. The step matters: since the F1 offset
+    # fix (2026-07-17) the fitted amplitude is proportional to the measured
+    # rise across the window (data at the high-BE edge minus the low-BE
+    # pre-loss level). A perfectly flat pedestal therefore has NO loss
+    # intensity to model, so the honest background is flat and carries no
+    # kernel shape to inspect. The step gives the anchor something to fit;
+    # the background shape it scales is still the pure kernel response.
+    y = np.full_like(x, 1e-9)
+    y[0] = 2e-9  # high-BE edge: a measured rise -> nonzero fitted amplitude
     spike_idx = 800  # x = 20.0 eV
     y[spike_idx] = 1.0e6
 
@@ -118,26 +126,123 @@ def test_background_anchored_at_high_be_edge():
     assert np.isclose(bg[0], y[0], rtol=1e-12), (
         f"high-BE-edge anchor broken: bg[0] = {bg[0]}, data = {y[0]}"
     )
-    assert bg[-1] == 0.0, f"low-BE edge should carry zero loss background, got {bg[-1]}"
+    # Since the F1 offset fix (2026-07-17) the low-BE edge carries the
+    # pre-loss constant C0 (the out-of-window baseline), NOT zero. K(0) = 0
+    # still makes the LOSS integral vanish there, so the background equals C0
+    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
+    # Asserting 0.0 here was pinning the bug: it forced the background to dive
+    # to zero at the low-BE edge regardless of the data, reporting the entire
+    # baseline as net signal.
+    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
+        f"low-BE edge should sit on the pre-loss level C0 = {y[-1]}, got {bg[-1]}"
+    )
     assert np.all(np.isfinite(bg))
     assert np.all(bg >= 0.0)
 
     # Same anchor semantics for ascending input: the high-BE edge is x[-1]
     bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
     assert np.isclose(bg_a[-1], y[0], rtol=1e-12)
-    assert bg_a[0] == 0.0
-
-
-def test_no_loss_signal_returns_unanchored_zeros():
-    """Codex review pin (2026-07-04, run A MINOR): when no net loss signal
-    accumulates at the high-BE edge (bg[0] == 0 — e.g. counts are zero
-    everywhere below the edge point), the background is returned UNANCHORED
-    (all zeros), NOT force-matched to the edge intensity. Documented
-    degenerate-input fallback, mirrored in the JS twin's ``|| 1`` guard."""
+    # ...and the low-BE edge (index 0 when ascending) sits on C0, per above.
+    assert np.isclose(bg_a[0], y[-1], rtol=1e-12)
+
+
+def test_no_loss_signal_returns_flat_pre_loss_level():
+    """Degenerate input: no net loss signal accumulates at the high-BE edge
+    (bg[0] == 0 — counts are zero everywhere below the edge point).
+
+    Supersedes the 2026-07-04 Codex pin ``..._returns_unanchored_zeros``.
+    That pin asserted all-zeros, which was correct ONLY while the background
+    carried no constant term: with the F1 offset fix (2026-07-17) the honest
+    answer for a window containing no modellable loss signal is the flat
+    pre-loss level C0, not zero. Returning zeros would report the entire
+    baseline as net signal — the exact failure F1 fixes. The guard itself
+    still exists (no force-matching to the edge intensity, no divide-by-zero);
+    only its fallback VALUE changed from 0 to C0. Mirrored in the JS twin."""
     x = np.array([291.0, 290.0, 289.0, 288.0])  # descending
     y = np.array([100.0, 0.0, 0.0, 0.0])        # signal only at the edge itself
     bg = tougaard_background(x, y)
-    assert np.array_equal(bg, np.zeros(4)), f"expected unanchored zeros, got {bg}"
+    assert np.array_equal(bg, np.zeros(4)), (
+        f"C0 is 0.0 here (low-BE edge counts are zero), so the flat pre-loss "
+        f"level IS zeros; got {bg}"
+    )
+
+
+def test_flat_window_yields_no_phantom_signal():
+    """F1 regression pin (2026-07-17): a flat, featureless window must yield
+    ~zero net counts everywhere.
+
+    Before the offset fix, K(0) = 0 forced the background to zero at the
+    low-BE edge regardless of the data, so a flat 500-count window produced a
+    background ramping 0 -> 500 and reported up to 500 counts of phantom
+    "signal" fabricated from a featureless baseline."""
+    x = np.linspace(740.0, 700.0, 200)   # descending, flat data
+    y = np.full_like(x, 500.0)
+    bg = tougaard_background(x, y)
+    net = y - bg
+    assert np.max(np.abs(net)) < 1e-6, (
+        f"flat window must leave ~zero net; net spans "
+        f"{net.min():.3f}..{net.max():.3f}"
+    )
+
+
+def test_background_tracks_low_be_baseline_on_wide_region():
+    """F1 regression pin (2026-07-17): on a wide 2p-like region sitting on a
+    large out-of-window inelastic baseline, the background must track that
+    baseline at the low-BE edge instead of diving to zero."""
+    x = np.linspace(740.0, 700.0, 600)   # descending
+    pk = (6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2)
+          + 3000.0 * np.exp(-0.5 * ((x - 724.5) / 1.9) ** 2))
+    baseline = 4000.0 + 3000.0 * np.cumsum(pk[::-1])[::-1] / np.sum(pk)
+    y = pk + baseline
+    bg = tougaard_background(x, y)
+    # low-BE edge is index -1 on this descending grid
+    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
+        f"low-BE edge dove to {bg[-1]:.1f} instead of tracking the "
+        f"{y[-1]:.1f}-count baseline"
+    )
+    assert np.isclose(bg[0], y[0], rtol=1e-12)
+
+
+def test_nonuniform_grid_uses_local_quadrature_weights():
+    """F2 regression pin (2026-07-17): the nonuniform-grid branch must weight
+    each term by its local energy spacing.
+
+    It previously used exact per-point separations but omitted the spacing
+    weights, silently applying uniform-grid quadrature inside the branch
+    written precisely BECAUSE the grid is not uniform (~24% error on a
+    genuinely nonuniform grid). np.gradient returns dx exactly on a uniform
+    grid, so the two branches must now agree to floating point -- the
+    uniformity test is an optimization, not a semantic fork."""
+    # Uniform grid, then the same grid perturbed below the uniformity
+    # tolerance so the nonuniform branch runs on near-identical data.
+    x = np.linspace(740.0, 700.0, 300)
+    y = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))
+    bg_uniform = tougaard_background(x, y)
+    x_jitter = x.copy()
+    x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
+    bg_nonuniform = tougaard_background(x_jitter, y)
+    assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
+        "uniform and nonuniform branches disagree on near-identical grids"
+    )
+
+    # Genuinely nonuniform grid vs an explicit spacing-weighted reference.
+    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
+                         np.linspace(720.0, 700.0, 400)])
+    ya = np.interp(xa[::-1], x[::-1], y[::-1])[::-1]
+    got = tougaard_background(xa, ya)
+
+    B_coef, C_coef = 2866.0, 1643.0
+    c0 = float(ya[-1])
+    net = ya - c0
+    w = np.abs(np.gradient(xa))
+    ref = np.zeros(len(xa))
+    for i in range(len(xa)):
+        T = np.abs(xa[i:] - xa[i])
+        ref[i] = float(np.sum((B_coef * T) / (C_coef + T * T) ** 2 * net[i:] * w[i:]))
+    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
+    assert np.allclose(got, ref, rtol=1e-9), (
+        "nonuniform branch does not match spacing-weighted quadrature"
+    )
 
 
 def test_short_input_returns_zeros():

exec
/bin/zsh -lc 'git status --short && git branch --show-current && git rev-parse --show-toplevel' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-FMq381m2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mVoZD8WU' (errno=Operation not permitted)
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sKNEZj76' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4KGmJiQZ' (errno=Operation not permitted)
feature-autofit-stage2
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2n5e9QnS' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-TDEprZqo' (errno=Operation not permitted)
/Users/skyefortier/xps-verify

codex
The commit touches only the four named files at the Git level. I’m now checking whether the changed hunks stay inside the allowed functions and whether any callers or numeric fixtures still encode the old Tougaard behavior.
exec
/bin/zsh -lc "rg -n \"def _apply_endpoint_averaging|def tougaard_background|def shirley_background|def smart_background|tougaard_background\\(|BackgroundType\\.TOUGAARD|tougaardBackground\\(|function computeBackgroundCore|function _applyEndpointAveraging\" fitting.py autofit templates tests app.py routes.py 2>/dev/null" in /Users/skyefortier/xps-verify
 exited 2 in 0ms:
fitting.py:306:def shirley_background(
fitting.py:357:def smart_background(
fitting.py:432:def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
fitting.py:508:def tougaard_background(
fitting.py:1038:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1276:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
templates/index.html.pre-audit:1900:function tougaardBackground(be, intensity) {
templates/index.html.pre-audit:1937:    if (type === 'tougaard') return tougaardBackground(be, intensity);
templates/index.html.pre-audit:1953:  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, inSub);
tests/test_tougaard_background.py:74:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:92:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:93:    bg_a = tougaard_background(x_a, y_a)
tests/test_tougaard_background.py:108:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:109:    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
tests/test_tougaard_background.py:123:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:143:    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
tests/test_tougaard_background.py:163:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:180:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:197:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:220:    bg_uniform = tougaard_background(x, y)
tests/test_tougaard_background.py:223:    bg_nonuniform = tougaard_background(x_jitter, y)
tests/test_tougaard_background.py:232:    got = tougaard_background(xa, ya)
tests/test_tougaard_background.py:251:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
tests/test_tougaard_background.py:253:    assert tougaard_background(np.array([]), np.array([])).size == 0
templates/index.html:4136:function tougaardBackground(be, intensity, nAvg) {
templates/index.html:4196:function _applyEndpointAveraging(intensity, nAvg) {
templates/index.html:4292:function computeBackgroundCore(be, intensity, settings) {
templates/index.html:4322:    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
templates/index.html:4323:    if (type === 'tougaard') return tougaardBackground(be, avgIn);
templates/index.html:4344:  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
tests/js/tougaard_twin.test.js:27:const avgMatch = html.match(/function _applyEndpointAveraging\([\s\S]*?\n\}/);
tests/js/tougaard_twin.test.js:62:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:76:  const bgDesc = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:77:  const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
tests/js/tougaard_twin.test.js:87:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:104:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:119:  //   bg = tougaard_background(x, y)
tests/js/tougaard_twin.test.js:134:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:149:// tougaard_background(x, _apply_endpoint_averaging(y, n))).
tests/js/tougaard_twin.test.js:151:  const coreMatch = html.match(/function computeBackgroundCore\([\s\S]*?\n\}/);
tests/js/tougaard_twin.test.js:172:  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
autofit/engine.py:297:    if bg is BackgroundType.TOUGAARD:
autofit/engine.py:299:        return tougaard_background(x, y)
autofit/parity.py:107:        bg_inner = tougaard_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))

exec
/bin/zsh -lc "rg -n -i \"tougaard|background_type|backgroundType|background\\\"\\s*:\\s*\\\"tougaard|type\\\"\\s*:\\s*\\\"tougaard\" tests tests/autofit docs/autofit/inventory scripts . --glob '"'!venv/**'"' --glob '"'!node_modules/**'"' --glob '"'!__pycache__/**'"' --glob '"'!*.pyc'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
./CLAUDE.md:258:| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
tests/test_tougaard_background.py:1:"""Tougaard universal-cross-section background — correctness pins.
tests/test_tougaard_background.py:10:   ~20 eV XPS window the shipped "Tougaard" background was essentially
tests/test_tougaard_background.py:11:   flat/zero.  Reference: S. Tougaard, Surf. Interface Anal. 11, 453
tests/test_tougaard_background.py:27:   window (the standard practical Tougaard criterion: B is effectively
tests/test_tougaard_background.py:30:No pre-existing test or fixture pinned the old (wrong) Tougaard output
tests/test_tougaard_background.py:37:from fitting import tougaard_background
tests/test_tougaard_background.py:74:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:92:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:93:    bg_a = tougaard_background(x_a, y_a)
tests/test_tougaard_background.py:108:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:109:    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
tests/test_tougaard_background.py:119:    of the window (practical Tougaard criterion: the universal cross-section
tests/test_tougaard_background.py:123:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:132:    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
tests/test_tougaard_background.py:143:    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
tests/test_tougaard_background.py:163:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:180:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:197:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:220:    bg_uniform = tougaard_background(x, y)
tests/test_tougaard_background.py:223:    bg_nonuniform = tougaard_background(x_jitter, y)
tests/test_tougaard_background.py:232:    got = tougaard_background(xa, ya)
tests/test_tougaard_background.py:251:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
tests/test_tougaard_background.py:253:    assert tougaard_background(np.array([]), np.array([])).size == 0
tests/autofit/test_cl2p_freewidth.py:27:    BackgroundType,
tests/autofit/test_cl2p_freewidth.py:136:        name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:148:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:159:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:177:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:190:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:203:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_criteria.py:15:    BackgroundType,
tests/autofit/test_criteria.py:31:                           background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:6:    BackgroundType,
tests/autofit/test_resolver.py:120:            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:122:            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
tests/autofit/stress_cases.py:52:    BackgroundType,
tests/autofit/stress_cases.py:113:def _cand(name, slots, bg=BackgroundType.LINEAR):
tests/autofit/stress_cases.py:132:                   bg=BackgroundType.LINEAR):
tests/autofit/stress_cases.py:431:    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
tests/autofit/test_bayesian_method.py:16:    BackgroundType,
tests/autofit/test_bayesian_method.py:35:    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:37:    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:40:    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:254:    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:257:    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
./fitting.py:508:def tougaard_background(
./fitting.py:513:    """Single-pass Tougaard universal-cross-section background, with the
./fitting.py:518:    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
./fitting.py:523:    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
./fitting.py:537:    practical Tougaard criterion (B is effectively fitted, which is why the
./fitting.py:550:    ``tougaardBackground``.
./fitting.py:556:    # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
./fitting.py:1004:    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
./fitting.py:1011:    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
./fitting.py:1037:    elif bg_method == "tougaard":
./fitting.py:1038:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
./fitting.py:1275:    elif method == "tougaard":
./fitting.py:1276:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
tests/autofit/test_preseed_dominants.py:165:                                 BackgroundType)
tests/autofit/test_preseed_dominants.py:177:    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
tests/autofit/test_preseed_dominants.py:199:    from autofit.grammar import CandidateModel, BackgroundType
tests/autofit/test_preseed_dominants.py:200:    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
tests/autofit/test_preseed_dominants.py:256:                                 BackgroundType)
tests/autofit/test_preseed_dominants.py:262:    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
tests/autofit/test_preseed_dominants.py:368:    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:382:    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
./templates/index.html.pre-audit:789:                <option value="tougaard">Tougaard (simplified)</option>
./templates/index.html.pre-audit:1900:function tougaardBackground(be, intensity) {
./templates/index.html.pre-audit:1937:    if (type === 'tougaard') return tougaardBackground(be, intensity);
./templates/index.html.pre-audit:1953:  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, inSub);
tests/autofit/test_engine_doublet.py:12:    BackgroundType,
tests/autofit/test_engine_doublet.py:36:    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
tests/autofit/test_engine_doublet.py:124:    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
tests/autofit/test_engine_doublet.py:134:        name="joint", background=BackgroundType.SHIRLEY,
tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",
tests/autofit/test_fit_full_window_option.py:37:from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape
tests/autofit/test_fit_full_window_option.py:47:    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))
tests/autofit/test_sparse_map.py:15:    BackgroundType,
tests/autofit/test_sparse_map.py:34:    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:160:    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:162:    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
tests/autofit/test_candidate_pool.py:159:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool.py:346:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool_wiring.py:184:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool_wiring.py:190:                              bg=BackgroundType.SHIRLEY)])
tests/autofit/test_stage2_completeness.py:289:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:296:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:313:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:321:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:365:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:372:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:392:    from autofit.grammar import BackgroundType
tests/autofit/test_stage2_completeness.py:398:        x, y, BackgroundType.LINEAR), [], {})
tests/autofit/test_stage2_completeness.py:405:        pool, BackgroundType.LINEAR, step_ev=0.05)
tests/autofit/test_preseed_dominants.py:165:                                 BackgroundType)
tests/autofit/test_preseed_dominants.py:177:    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
tests/autofit/test_preseed_dominants.py:199:    from autofit.grammar import CandidateModel, BackgroundType
tests/autofit/test_preseed_dominants.py:200:    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
tests/autofit/test_preseed_dominants.py:256:                                 BackgroundType)
tests/autofit/test_preseed_dominants.py:262:    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
tests/autofit/test_preseed_dominants.py:368:    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:382:    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
./templates/index.html:1988:                <option value="tougaard" data-tip="Physics-based universal background using electron energy loss cross-sections. More accurate than Shirley but requires wider energy range.">Tougaard-like (single pass)</option>
./templates/index.html:3700:      // Endpoint averaging also applies to Tougaard (it sets the high-BE
./templates/index.html:3702:      const needsEpAvg = needsIter || ui.bgType === 'tougaard';
./templates/index.html:4130:// Single-pass Tougaard background — JS twin of fitting.py's
./templates/index.html:4131:// tougaard_background (keep the two numerically in agreement; pinned by
./templates/index.html:4132:// tests/js/tougaard_twin.test.js). Universal loss kernel
./templates/index.html:4133:// K(T) = B·T/(C+T²)² with B = 2866 eV², C = 1643 eV² (S. Tougaard,
./templates/index.html:4136:function tougaardBackground(be, intensity, nAvg) {
./templates/index.html:4147:  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
./templates/index.html:4177:  // the practical Tougaard criterion (B effectively fitted; C alone sets the
./templates/index.html:4320:    // Endpoint averaging matters for Tougaard since the amplitude is
./templates/index.html:4322:    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
./templates/index.html:4323:    if (type === 'tougaard') return tougaardBackground(be, avgIn);
./templates/index.html:4341:  // Averaged for the same reason as Shirley types: the Tougaard amplitude
./templates/index.html:4344:  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
./templates/index.html:12386:  // Grey out endpoint avg for types it can't affect. Tougaard keeps it:
./templates/index.html:12388:  // it for tougaard regardless, so the control must stay honest).
./templates/index.html:12389:  const needsEpAvg = needsIter || type === 'tougaard';
tests/js/batch_propagation.test.js:42:  const src = ui({ bgType: 'tougaard', bgStart: '690', bgEnd: '750', shirleyIter: '9' });
tests/js/batch_propagation.test.js:45:  assert.strictEqual(out.bgType, 'tougaard');
tests/js/tougaard_twin.test.js:1:// Tougaard background — JS twin of fitting.py's tougaard_background.
tests/js/tougaard_twin.test.js:6:// tests/test_tougaard_background.py):
tests/js/tougaard_twin.test.js:9://      S. Tougaard, Surf. Interface Anal. 11, 453 (1988).
tests/js/tougaard_twin.test.js:23:const match = html.match(/function tougaardBackground\([\s\S]*?\n\}/);
tests/js/tougaard_twin.test.js:24:assert.ok(match, 'tougaardBackground not found in templates/index.html');
tests/js/tougaard_twin.test.js:25:const tougaardBackground = eval('(' + match[0] + ')');
tests/js/tougaard_twin.test.js:62:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:76:  const bgDesc = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:77:  const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
tests/js/tougaard_twin.test.js:87:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:104:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:115:  //   import numpy as np; from fitting import tougaard_background
tests/js/tougaard_twin.test.js:119:  //   bg = tougaard_background(x, y)
tests/js/tougaard_twin.test.js:134:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:144:// caller computeBackgroundCore passed RAW intensity to tougaardBackground
tests/js/tougaard_twin.test.js:149:// tougaard_background(x, _apply_endpoint_averaging(y, n))).
tests/js/tougaard_twin.test.js:150:test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
tests/js/tougaard_twin.test.js:172:  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
tests/js/tougaard_twin.test.js:176:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/js/tougaard_twin.test.js:181:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/autofit/test_fit_full_window_option.py:37:from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape
tests/autofit/test_fit_full_window_option.py:47:    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))
tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",
tests/autofit/stress_cases.py:52:    BackgroundType,
tests/autofit/stress_cases.py:113:def _cand(name, slots, bg=BackgroundType.LINEAR):
tests/autofit/stress_cases.py:132:                   bg=BackgroundType.LINEAR):
tests/autofit/stress_cases.py:431:    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
tests/autofit/test_stage2_completeness.py:289:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:296:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:313:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:321:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:365:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:372:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:392:    from autofit.grammar import BackgroundType
tests/autofit/test_stage2_completeness.py:398:        x, y, BackgroundType.LINEAR), [], {})
tests/autofit/test_stage2_completeness.py:405:        pool, BackgroundType.LINEAR, step_ev=0.05)
tests/autofit/test_cl2p_freewidth.py:27:    BackgroundType,
tests/autofit/test_cl2p_freewidth.py:136:        name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:148:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:159:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:177:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:190:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:203:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_candidate_pool.py:159:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool.py:346:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_criteria.py:15:    BackgroundType,
tests/autofit/test_criteria.py:31:                           background=BackgroundType.SHIRLEY,
tests/autofit/test_candidate_pool_wiring.py:184:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool_wiring.py:190:                              bg=BackgroundType.SHIRLEY)])
tests/autofit/test_bayesian_method.py:16:    BackgroundType,
tests/autofit/test_bayesian_method.py:35:    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:37:    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:40:    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:254:    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:257:    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
tests/autofit/test_resolver.py:6:    BackgroundType,
tests/autofit/test_resolver.py:120:            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:122:            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
tests/autofit/test_engine_doublet.py:12:    BackgroundType,
tests/autofit/test_engine_doublet.py:36:    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
tests/autofit/test_engine_doublet.py:124:    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
tests/autofit/test_engine_doublet.py:134:        name="joint", background=BackgroundType.SHIRLEY,
tests/autofit/test_sparse_map.py:15:    BackgroundType,
tests/autofit/test_sparse_map.py:34:    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:160:    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:162:    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
./xps-fitting-tool.html:469:                <option value="tougaard">Tougaard (simplified)</option>
./xps-fitting-tool.html:755:function tougaardBackground(be, intensity) {
./xps-fitting-tool.html:756:  // Simplified Tougaard: B*T^2 / (C + T^2)^2 convolution approximation
./xps-fitting-tool.html:778:  if (type === 'tougaard') return tougaardBackground(be, intensity);
./docs/audit-2026-06-09.md:35:| F7  | P2       | Backend  | `/api/fit` has no upper bound on `n_perturb`; pure-Python Tougaard scales O(n²)         |
./docs/audit-2026-06-09.md:245:### F7 — No upper bound on `n_perturb`; pure-Python Tougaard is O(n²)
./docs/audit-2026-06-09.md:251:- `fitting.py:508-533` (`tougaard_background` — `for i in range(n)` in
./docs/audit-2026-06-09.md:268:auditor's own laptop. Independently, `tougaard_background` on an
./docs/audit-2026-06-09.md:271:as the ROI with `method=tougaard` is many seconds to many minutes per
./docs/audit-2026-06-09.md:276:`n_perturb` (or a Tougaard background over a large ROI). With four
./docs/audit-2026-06-09.md:283:the Tougaard loop with `numpy` (the kernel is a function of `|i - j|`,
./docs/audit-2026-06-09.md:526:3. **F7** (`n_perturb` / Tougaard DoS). Quick to cap; protects the
./autofit/parity.py:37:    tougaard_background,
./autofit/parity.py:106:    elif m == "tougaard":
./autofit/parity.py:107:        bg_inner = tougaard_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
./autofit/grammar.py:37:    "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
./autofit/grammar.py:69:class BackgroundType(Enum):
./autofit/grammar.py:74:    TOUGAARD = "tougaard"
./autofit/grammar.py:168:    background: BackgroundType
./autofit/regions/u4f.py:38:    BackgroundType,
./autofit/regions/u4f.py:110:U4F_BACKGROUND = BackgroundType.SMART
./tests/test_tougaard_background.py:1:"""Tougaard universal-cross-section background — correctness pins.
./tests/test_tougaard_background.py:10:   ~20 eV XPS window the shipped "Tougaard" background was essentially
./tests/test_tougaard_background.py:11:   flat/zero.  Reference: S. Tougaard, Surf. Interface Anal. 11, 453
./tests/test_tougaard_background.py:27:   window (the standard practical Tougaard criterion: B is effectively
./tests/test_tougaard_background.py:30:No pre-existing test or fixture pinned the old (wrong) Tougaard output
./tests/test_tougaard_background.py:37:from fitting import tougaard_background
./tests/test_tougaard_background.py:74:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:92:    bg_d = tougaard_background(x_d, y_d)
./tests/test_tougaard_background.py:93:    bg_a = tougaard_background(x_a, y_a)
./tests/test_tougaard_background.py:108:    bg_d = tougaard_background(x_d, y_d)
./tests/test_tougaard_background.py:109:    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
./tests/test_tougaard_background.py:119:    of the window (practical Tougaard criterion: the universal cross-section
./tests/test_tougaard_background.py:123:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:132:    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
./tests/test_tougaard_background.py:143:    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
./tests/test_tougaard_background.py:163:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:180:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:197:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:220:    bg_uniform = tougaard_background(x, y)
./tests/test_tougaard_background.py:223:    bg_nonuniform = tougaard_background(x_jitter, y)
./tests/test_tougaard_background.py:232:    got = tougaard_background(xa, ya)
./tests/test_tougaard_background.py:251:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
./tests/test_tougaard_background.py:253:    assert tougaard_background(np.array([]), np.array([])).size == 0
./autofit/engine.py:49:    BackgroundType,
./autofit/engine.py:287:def _compute_background(x: np.ndarray, y: np.ndarray, bg: BackgroundType) -> np.ndarray:
./autofit/engine.py:288:    if bg is BackgroundType.SHIRLEY:
./autofit/engine.py:290:    if bg is BackgroundType.SMART:
./autofit/engine.py:292:    if bg is BackgroundType.SMART_EXP:
./autofit/engine.py:295:    if bg is BackgroundType.LINEAR:
./autofit/engine.py:297:    if bg is BackgroundType.TOUGAARD:
./autofit/engine.py:298:        from fitting import tougaard_background
./autofit/engine.py:299:        return tougaard_background(x, y)
./autofit/engine.py:2574:                         else BackgroundType.SHIRLEY)
./autofit/regions/cl2p.py:39:    BackgroundType,
./autofit/regions/cl2p.py:71:CL2P_BACKGROUND = BackgroundType.SMART_EXP
./autofit/regions/c1s.py:28:    BackgroundType,
./autofit/regions/c1s.py:272:                name=name, background=BackgroundType.SHIRLEY,
./autofit/regions/n1s.py:24:    BackgroundType,
./autofit/regions/n1s.py:40:N1S_BACKGROUND = BackgroundType.SMART
./autofit/regions/b1s.py:24:    BackgroundType,
./autofit/regions/b1s.py:53:B1S_BACKGROUND = BackgroundType.SMART_EXP
./docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md:22:XPS spectra ride on a curved background (Shirley, Tougaard, etc.). In the current view, peak fills are drawn on top of this curved baseline, which makes peaks look "wavy" and forces the user to mentally subtract the background to judge fit quality. Background-subtracted view is the standard presentation in XPS publications and is significantly easier to read for both fit-quality assessment and visual communication.
./docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md:58:The disabled state activates whenever the tab's background method is "None" or no background data is available. When the user changes the background method to a real one (Shirley, Tougaard, Smart), the pill re-enables and remembers its previous active/inactive state.
./docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md:118:**Background method changed mid-session.** When the user switches background methods (e.g., Shirley to Tougaard), the chart re-renders with the new background. If subtracted view is on, the new background is what gets subtracted. No special handling.
./docs/autofit/peak-fit-methods-decision-matrix.md:71:**Curve fitting / practice:** Major et al., *JVST A* 38, 061203 (2020), 10.1116/6.0000377 · Shirley, *PRB* 5, 4709 (1972), 10.1103/PhysRevB.5.4709 · Tougaard, *SIA* 11, 453 (1988), 10.1002/sia.740110902 · Doniach & Šunjić, *J. Phys. C* 3, 285 (1970), 10.1088/0022-3719/3/2/010 · Morgan, *SIA* (2023), 10.1002/sia.7215 · box-plot overfitting, *JESRP* 253, 147094 (2021), 10.1016/j.elspec.2021.147094.
./docs/autofit/PROGRESS.md:32:| Tougaard background bug-fix (C constant + BE-order + amplitude anchor) | DONE | ✅ 5 py + 4 js tests | `fitting.py::tougaard_background` + JS twin `tougaardBackground`: C was shipped SQUARED (1643² ≈ 2.7e6 eV², kernel max ~949 eV → flat/zero bg on real windows) → corrected to 1643 eV² (Tougaard 1988, SIA 11, 453); one-sided sum made order-robust (descending normalization, shirley-mirror); degenerate trailing rescale (K(0)=0 ⇒ scale ≡ raw trailing counts) replaced by the high-BE-edge anchor. Cross-language parity pinned at 1e-9. Codex checkpoint ×2: NO-GO ×2 (same MAJOR: frontend callers bypassed endpoint averaging → anchor mismatch; + 1 MINOR comment honesty) → all fixed same-session + caller-level pin; re-check ×2 **GO ×2** — unit review-complete. |
./docs/autofit/PROGRESS.md:1153:## Tougaard background bug-fix (2026-07-04 goal session) — constant, BE-order, amplitude anchor
./docs/autofit/PROGRESS.md:1155:Small scoped fix to the EXISTING `tougaard` background (manual-fit path
./docs/autofit/PROGRESS.md:1156:math; the autofit engine only reaches it via `BackgroundType.TOUGAARD` —
./docs/autofit/PROGRESS.md:1159:implementations: `fitting.py::tougaard_background` and its JS twin
./docs/autofit/PROGRESS.md:1160:`tougaardBackground` in `templates/index.html` (kept in numerical
./docs/autofit/PROGRESS.md:1161:agreement, pinned at 1e-9 relative by `tests/js/tougaard_twin.test.js`).
./docs/autofit/PROGRESS.md:1167:   constants verified against the source: S. Tougaard, *Surf. Interface
./docs/autofit/PROGRESS.md:1169:   **B = 2866 eV², C = 1643 eV²** (also restated in the QUASES-Tougaard
./docs/autofit/PROGRESS.md:1172:   ~1e-9-scale, so the "Tougaard" background was essentially zero/flat.
./docs/autofit/PROGRESS.md:1194:   regression than the bug. Replaced with the standard practical Tougaard
./docs/autofit/PROGRESS.md:1200:4. **Tests** (`tests/test_tougaard_background.py`, 5;
./docs/autofit/PROGRESS.md:1201:   `tests/js/tougaard_twin.test.js`, 4 — the JS tests extract the function
./docs/autofit/PROGRESS.md:1216:through the existing `BackgroundType.TOUGAARD` dispatch). Codex
./docs/autofit/PROGRESS.md:1222:`docs/autofit/codex/tougaard_fix_review_prompt.txt`, verdicts archived at
./docs/autofit/PROGRESS.md:1223:`docs/autofit/codex/tougaard_fix_verdict_runA.md` / `_runB.md`. Both runs
./docs/autofit/PROGRESS.md:1228:   for Tougaard while every backend caller applies
./docs/autofit/PROGRESS.md:1233:   noted the UI greys out the endpoint-avg control for Tougaard while the
./docs/autofit/PROGRESS.md:1235:   `computeBackgroundCore` Tougaard branches (sliced + fallback) now pass
./docs/autofit/PROGRESS.md:1237:   both UI gates enable the endpoint-avg control for Tougaard (it now
./docs/autofit/PROGRESS.md:1241:   `tougaardBackground(be, averaged)` (watched fail first).
./docs/autofit/PROGRESS.md:1255:calls tougaard_background WITHOUT averaging, but it does so for EVERY
./docs/autofit/PROGRESS.md:1257:internally consistent design, not a Tougaard-specific mismatch, and
./docs/autofit/PROGRESS.md:1258:engine changes are out of scope per rails. Post-fix: JS 53/53, Tougaard
./docs/autofit/PROGRESS.md:1264:`docs/autofit/codex/tougaard_fix_recheck_prompt.txt` (verdicts archived:
./docs/autofit/PROGRESS.md:1265:`docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md` / `_runB.md`;
./docs/autofit/PROGRESS.md:1272:consistent (shirley-iter stays disabled for Tougaard, endpoint-avg
./docs/autofit/PROGRESS.md:1280:mixed-sign pass-through match the documented policy. **The Tougaard
./docs/superpowers/plans/2026-04-07-manual-spline-background.md:11:**CRITICAL CONSTRAINT:** Do NOT modify any existing `shirleyBackground`, `smartBackground`, `linearBackground`, `tougaardBackground` functions, or any existing loading/parsing logic. Only ADD new code.
./docs/superpowers/plans/2026-04-07-manual-spline-background.md:105:A pure math function with no DOM dependencies. Add it near the existing background functions (after `tougaardBackground`, around line 2749).
./docs/superpowers/plans/2026-04-07-manual-spline-background.md:804:- [ ] `tougaardBackground` function: NOT modified
./docs/superpowers/plans/2026-04-07-manual-spline-background.md:809:- [ ] Existing `computeBackground` cases (shirley/smart/linear/tougaard/none): NOT modified — only a new `"spline"` case added
./tests/js/batch_propagation.test.js:42:  const src = ui({ bgType: 'tougaard', bgStart: '690', bgEnd: '750', shirleyIter: '9' });
./tests/js/batch_propagation.test.js:45:  assert.strictEqual(out.bgType, 'tougaard');
./tests/js/tougaard_twin.test.js:1:// Tougaard background — JS twin of fitting.py's tougaard_background.
./tests/js/tougaard_twin.test.js:6:// tests/test_tougaard_background.py):
./tests/js/tougaard_twin.test.js:9://      S. Tougaard, Surf. Interface Anal. 11, 453 (1988).
./tests/js/tougaard_twin.test.js:23:const match = html.match(/function tougaardBackground\([\s\S]*?\n\}/);
./tests/js/tougaard_twin.test.js:24:assert.ok(match, 'tougaardBackground not found in templates/index.html');
./tests/js/tougaard_twin.test.js:25:const tougaardBackground = eval('(' + match[0] + ')');
./tests/js/tougaard_twin.test.js:62:  const bg = tougaardBackground(be, intensity);
./tests/js/tougaard_twin.test.js:76:  const bgDesc = tougaardBackground(be, intensity);
./tests/js/tougaard_twin.test.js:77:  const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
./tests/js/tougaard_twin.test.js:87:  const bg = tougaardBackground(be, intensity);
./tests/js/tougaard_twin.test.js:104:  const bg = tougaardBackground(be, intensity);
./tests/js/tougaard_twin.test.js:115:  //   import numpy as np; from fitting import tougaard_background
./tests/js/tougaard_twin.test.js:119:  //   bg = tougaard_background(x, y)
./tests/js/tougaard_twin.test.js:134:  const bg = tougaardBackground(be, intensity);
./tests/js/tougaard_twin.test.js:144:// caller computeBackgroundCore passed RAW intensity to tougaardBackground
./tests/js/tougaard_twin.test.js:149:// tougaard_background(x, _apply_endpoint_averaging(y, n))).
./tests/js/tougaard_twin.test.js:150:test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
./tests/js/tougaard_twin.test.js:172:  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
./tests/js/tougaard_twin.test.js:176:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
./tests/js/tougaard_twin.test.js:181:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
./tests/autofit/test_criteria.py:15:    BackgroundType,
./tests/autofit/test_criteria.py:31:                           background=BackgroundType.SHIRLEY,
./tests/autofit/stress_cases.py:52:    BackgroundType,
./tests/autofit/stress_cases.py:113:def _cand(name, slots, bg=BackgroundType.LINEAR):
./tests/autofit/stress_cases.py:132:                   bg=BackgroundType.LINEAR):
./tests/autofit/stress_cases.py:431:    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
./tests/autofit/test_cl2p_freewidth.py:27:    BackgroundType,
./tests/autofit/test_cl2p_freewidth.py:136:        name="bad", background=BackgroundType.LINEAR,
./tests/autofit/test_cl2p_freewidth.py:148:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
./tests/autofit/test_cl2p_freewidth.py:159:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
./tests/autofit/test_cl2p_freewidth.py:177:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
./tests/autofit/test_cl2p_freewidth.py:190:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
./tests/autofit/test_cl2p_freewidth.py:203:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
./tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",
./tests/autofit/test_preseed_dominants.py:165:                                 BackgroundType)
./tests/autofit/test_preseed_dominants.py:177:    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
./tests/autofit/test_preseed_dominants.py:199:    from autofit.grammar import CandidateModel, BackgroundType
./tests/autofit/test_preseed_dominants.py:200:    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
./tests/autofit/test_preseed_dominants.py:256:                                 BackgroundType)
./tests/autofit/test_preseed_dominants.py:262:    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
./tests/autofit/test_preseed_dominants.py:368:    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
./tests/autofit/test_preseed_dominants.py:382:    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
./tests/autofit/test_candidate_pool_wiring.py:184:    from autofit.grammar import BackgroundType
./tests/autofit/test_candidate_pool_wiring.py:190:                              bg=BackgroundType.SHIRLEY)])
./tests/autofit/test_bayesian_method.py:16:    BackgroundType,
./tests/autofit/test_bayesian_method.py:35:    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
./tests/autofit/test_bayesian_method.py:37:    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
./tests/autofit/test_bayesian_method.py:40:    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
./tests/autofit/test_bayesian_method.py:254:    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
./tests/autofit/test_bayesian_method.py:257:    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
./tests/autofit/test_engine_doublet.py:12:    BackgroundType,
./tests/autofit/test_engine_doublet.py:36:    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
./tests/autofit/test_engine_doublet.py:124:    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
./tests/autofit/test_engine_doublet.py:134:        name="joint", background=BackgroundType.SHIRLEY,
./tests/autofit/test_sparse_map.py:15:    BackgroundType,
./tests/autofit/test_sparse_map.py:34:    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
./tests/autofit/test_sparse_map.py:160:    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
./tests/autofit/test_sparse_map.py:162:    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
./tests/autofit/test_fit_full_window_option.py:37:from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape
./tests/autofit/test_fit_full_window_option.py:47:    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))
./tests/autofit/test_candidate_pool.py:159:    from autofit.grammar import BackgroundType
./tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
./tests/autofit/test_candidate_pool.py:346:    from autofit.grammar import BackgroundType
./tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
./tests/autofit/test_resolver.py:6:    BackgroundType,
./tests/autofit/test_resolver.py:120:            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
./tests/autofit/test_resolver.py:122:            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
./tests/autofit/test_stage2_completeness.py:289:    from autofit.grammar import (BackgroundType, CandidateModel,
./tests/autofit/test_stage2_completeness.py:296:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
./tests/autofit/test_stage2_completeness.py:313:    from autofit.grammar import (BackgroundType, CandidateModel,
./tests/autofit/test_stage2_completeness.py:321:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
./tests/autofit/test_stage2_completeness.py:365:    from autofit.grammar import (BackgroundType, CandidateModel,
./tests/autofit/test_stage2_completeness.py:372:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
./tests/autofit/test_stage2_completeness.py:392:    from autofit.grammar import BackgroundType
./tests/autofit/test_stage2_completeness.py:398:        x, y, BackgroundType.LINEAR), [], {})
./tests/autofit/test_stage2_completeness.py:405:        pool, BackgroundType.LINEAR, step_ev=0.05)
./docs/autofit/codex/tougaard_fix_verdict_runA.md:1:# Codex review — Tougaard bug-fix (commit 37861fd) — RUN A (2026-07-04)
./docs/autofit/codex/tougaard_fix_verdict_runA.md:4:Prompt: docs/autofit/codex/tougaard_fix_review_prompt.txt
./docs/autofit/codex/tougaard_fix_verdict_runA.md:7:   Frontend Tougaard still bypasses `_applyEndpointAveraging`, while backend `/api/fit`, `/api/background`, and autofit parity paths apply `_apply_endpoint_averaging` before `tougaard_background`. With the new high-BE anchor this is no longer a small shape-only mismatch: endpoint averaging directly sets the anchor amplitude. Concrete scenario: descending 11-point window, `endpointAvg=2`, high-BE first point is a spike/outlier `10000`, second point and rest are `100`; frontend anchors Tougaard to `10000`, backend anchors to averaged `5050`. The committed JS twin test only calls `tougaardBackground` directly on the same raw array, so it does not catch the shipped caller contract mismatch.
./docs/autofit/codex/phaseD_unit2_recheck3_prompt.txt:24:load — especially ones exercising the new stripping: "Tougaard, Surf.
./docs/autofit/codex/tougaard_fix_verdict_runB.md:1:# Codex review — Tougaard bug-fix (commit 37861fd) — RUN B (2026-07-04)
./docs/autofit/codex/tougaard_fix_verdict_runB.md:4:Prompt: docs/autofit/codex/tougaard_fix_review_prompt.txt
./docs/autofit/codex/tougaard_fix_verdict_runB.md:6:1. **MAJOR** [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4202), [fitting.py](/Users/skyefortier/xps-app/fitting.py:997), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1235) — Tougaard endpoint averaging is inconsistent between shipped frontend callers and backend callers. The UI disables `endpointAvg` for Tougaard, but stale values are still sent to `/api/background` and `/api/fit`; backend applies `_apply_endpoint_averaging(...)` before `tougaard_background`, while frontend preview/stack calls `tougaardBackground(...)` on raw intensity. Concrete failure: set endpoint avg to `10`, switch to Tougaard, with high-BE endpoint `500` and next 9 points `100`; frontend anchors Tougaard to `500`, backend anchors to averaged `140`. That breaks the claimed frontend/backend twin contract exactly at the new high-BE anchor, and current tests only compare direct function calls with unaveraged data.
./docs/autofit/codex/phaseD_unit2_recheck3_verdict_runA.md:10:3. Legitimate citation false-rejection check: CLOSED. These all load as `CONDITIONAL`: Tougaard citation, `Powe95`, `10.1116/1.1247741`, `Smith & Jones 1990-1995 survey`, and `-30 mV vs SCE study`.
./docs/autofit/codex/phaseD_unit2_recheck2_prompt.txt:23:   citations still load (e.g. "Tougaard, Surf. Interface Anal. 11, 453
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:6:CONTEXT: Commit 37861fd fixed the Tougaard background (squared constant
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:7:C=1643**2 → 1643 eV² per Tougaard 1988 SIA 11,453; BE-order robustness via
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:10:docs/autofit/codex/tougaard_fix_review_prompt.txt, verdicts archived at
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:11:docs/autofit/codex/tougaard_fix_verdict_runA.md / _runB.md) each returned
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:17:averaging for Tougaard while all backend callers apply
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:21:control for Tougaard while its value is still sent to and applied by the
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:23:DISPOSITION: templates/index.html computeBackgroundCore — BOTH Tougaard
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:29:~line 12180) now compute `needsEpAvg = needsIter || type === 'tougaard'`
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:30:so the control is enabled for Tougaard (it genuinely affects the anchor;
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:32:dishonest). PIN: new test in tests/js/tougaard_twin.test.js
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:33:('computeBackgroundCore applies endpoint averaging for tougaard (both
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:35:stubs the non-tougaard routes, and asserts BOTH branches bit-equal
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:36:tougaardBackground(be, _applyEndpointAveraging(intensity, 3)) on run A's
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:40:consistent (shirley-iter stays disabled for tougaard, endpoint-avg
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:41:enabled)? Any OTHER shipped caller of tougaardBackground we missed?
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:49:tougaard_background anchor block; templates/index.html tougaardBackground
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:53:input). PIN: tests/test_tougaard_background.py::
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:63:fitting.py's tougaard_background NUMERICS must be byte-identical to
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:1:# Codex re-check — Tougaard fix dispositions (fix commit 2731edc) — RUN A (2026-07-04 late)
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:4:Prompt: docs/autofit/codex/tougaard_fix_recheck_prompt.txt
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:9:- Fallback full-range path now computes `avgIn = _applyEndpointAveraging(intensity, nAvg)` and passes it to Tougaard at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184) and [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4193).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:10:- Main sliced path now passes `_applyEndpointAveraging(inSub, nAvg)` to Tougaard at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4214).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:11:- The pin discriminates: on the outlier-edge scenario, raw Tougaard anchors at `10000`; averaged expected/main/fallback all anchor at `3400`. So the old raw-intensity call would fail it.
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:12:- UI gates are consistent: `shirley-iter` remains disabled for Tougaard because `needsIter` excludes it, while `bg-endpoint-avg` is enabled because `needsEpAvg = needsIter || type === 'tougaard'` at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3594) and [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:12197).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:15:Tracked stale HTML copies still contain old Tougaard code, but project docs and `CLAUDE.md` identify `templates/index.html` as the active frontend; I do not count those stale copies as an active shipped caller for this disposition.
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:22:- The pin covers the concrete `[100, 0, 0, 0]` case at [tests/test_tougaard_background.py](/Users/skyefortier/xps-app/tests/test_tougaard_background.py:132).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:29:Scope matches the expected commit footprint: only docs/prompt/verdict archives, `fitting.py`, `templates/index.html`, and the two Tougaard tests changed. `fitting.py` Tougaard executable numerics are unchanged from `37861fd`; the diff is comment-only in that function.
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:32:- `node --test tests/js/tougaard_twin.test.js` passed.
./docs/autofit/codex/phaseD_unit2_recheck2_verdict_runA.md:10:3. CLOSED. No false-rejection issue found in probes: `Powe95`, DOI, URL, Tougaard citation, `No. 5, J. Chem.`, and `None et al...` all load. `0` remains rejected as intended.
./docs/autofit/codex/tougaard_fix_review_prompt.txt:2:repo (XPS peak-fitting web app). Review commit 37861fd ("tougaard: fix
./docs/autofit/codex/tougaard_fix_review_prompt.txt:9:- fitting.py: ONLY tougaard_background (docstring + body). Nothing else in
./docs/autofit/codex/tougaard_fix_review_prompt.txt:11:- templates/index.html: ONLY the tougaardBackground JS function (+ leading
./docs/autofit/codex/tougaard_fix_review_prompt.txt:13:- New tests: tests/test_tougaard_background.py, tests/js/tougaard_twin.test.js.
./docs/autofit/codex/tougaard_fix_review_prompt.txt:20:   slip of "C = 1643 eV²" (S. Tougaard, Surf. Interface Anal. 11, 453
./docs/autofit/codex/tougaard_fix_review_prompt.txt:48:   Decision taken: replace it with the standard practical Tougaard
./docs/autofit/codex/tougaard_fix_review_prompt.txt:54:   claim "standard practical Tougaard criterion" fair? (c) was there a
./docs/autofit/codex/tougaard_fix_review_prompt.txt:59:4. TESTS. tests/test_tougaard_background.py (5 tests) and
./docs/autofit/codex/tougaard_fix_review_prompt.txt:60:   tests/js/tougaard_twin.test.js (4 tests; they extract the function
./docs/autofit/codex/tougaard_fix_review_prompt.txt:67:   no pre-existing test or fixture pinned the old Tougaard output (grep
./docs/autofit/codex/tougaard_fix_review_prompt.txt:70:5. CALLERS. fitting.py dispatches tougaard_background at the /api/background
./docs/autofit/codex/tougaard_fix_review_prompt.txt:71:   and /api/fit background paths (grep "tougaard"); autofit reaches it only
./docs/autofit/codex/tougaard_fix_review_prompt.txt:72:   via BackgroundType.TOUGAARD (autofit/engine.py) and autofit/parity.py.
./docs/autofit/codex/tougaard_fix_review_prompt.txt:73:   The frontend calls tougaardBackground at two sites (~line 4162/4180).
./docs/autofit/codex/tougaard_fix_review_prompt.txt:80:   PROGRESS.md section "Tougaard background bug-fix (2026-07-04 goal
./docs/autofit/codex/phaseD_unit2_recheck3_verdict_runB.md:9:`Tougaard, Surf. Interface Anal. 11, 453 (1988)`, `Powe95`, `10.1116/1.1247741`, `Smith & Jones 1990-1995 survey`, and `-30 mV vs SCE study`. Internal hyphen survives; leading hyphen only affects the placeholder check.
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:3:Tougaard pre-loss constant (F1) + non-uniform quadrature weights (F2)") on
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:12:- fitting.py: ONLY tougaard_background (signature, docstring, body).
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:18:- templates/index.html: ONLY the tougaardBackground JS function (+ its
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:20:  unmodified — their two call sites into tougaardBackground still use the
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:22:- tests/test_tougaard_background.py, tests/js/tougaard_twin.test.js.
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:28:The previous tougaard_background computed the idealized integral
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:30:Tougaard 1988). This assumes the analysis window begins in a loss-free
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:102:    fixtures) for anything that pins a Tougaard background NUMERIC VALUE —
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:103:    not just the string "tougaard". The claim is that nothing outside the
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:104:    2 test files touched in this commit encodes the old (pre-F1) Tougaard
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:137:  copied from the sandbox), and that tougaard_twin.test.js still evals the
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:138:  real tougaardBackground out of templates/index.html rather than a
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:141:CALLERS. fitting.py dispatches tougaard_background at the /api/background
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:142:and /api/fit background paths; autofit reaches it via BackgroundType.TOUGAARD
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:145:frontend calls tougaardBackground at ~2 sites inside computeBackgroundCore.
./docs/autofit/codex/phaseD_unit2_recheck2_verdict_runB.md:6:1. **CLOSED**: round-1 residual probes now reject, including `n-a`, `false`, `0`, `n–a`, `None.`, `n - a`, `n\t-a`, `...`, `(none)`. Legitimate citations load: Tougaard citation, `Powe95`, DOI, URL, and `No. 5, J. Chem.`.
./docs/autofit/codex/phaseD_unit2_recheck2_verdict_runB.md:14:3. **CLOSED**: no false rejections found in normal citation probes. `Powe95`, DOI, URL, Tougaard reference, `No. 5, J. Chem.`, and `Nonequilibrium Surf. Sci...` all load. Internal punctuation is not stripped, only edge punctuation.
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:1:# Codex re-check — Tougaard fix dispositions (fix commit 2731edc) — RUN B (2026-07-04 late)
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:4:Prompt: docs/autofit/codex/tougaard_fix_recheck_prompt.txt
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:8:`computeBackgroundCore` now averages Tougaard input in both frontend branches:
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:10:- Fallback/full-range path uses `avgIn` before Tougaard: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184)
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:12:- Backend parity remains: `/api/fit` and `/api/background` both call `tougaard_background(..., _apply_endpoint_averaging(...))`: [fitting.py](/Users/skyefortier/xps-app/fitting.py:1002), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1240)
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:16:- `shirley-iter` remains disabled for Tougaard because `needsIter` excludes it.
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:17:- endpoint averaging is enabled for Tougaard via `needsEpAvg = needsIter || type === 'tougaard'`: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3594), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:12197)
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:19:The new JS pin discriminates. Against `37861fd`, the same outlier case produced raw anchor `10000` vs averaged `3400` for both branches. Against `2731edc`, both branches were bit-equal to averaged expected output. `node --test tests/js/tougaard_twin.test.js` passed.
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:25:Comments now state the real guard behavior and signed negative-count policy at both sites: [fitting.py](/Users/skyefortier/xps-app/fitting.py:587), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4053). The new Python pin matches the documented `[100,0,0,0]` behavior: [tests/test_tougaard_background.py](/Users/skyefortier/xps-app/tests/test_tougaard_background.py:131).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:27:I could not run pytest because the read-only sandbox has no usable temp directory, but I executed the extracted `tougaard_background` body directly and confirmed `[100,0,0,0] -> [0,0,0,0]`. I also checked the mixed-sign cancellation edge: it returns a signed unanchored correlation, consistent with the “negative counts pass through signed; no clamping” policy.
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:31:`git diff 37861fd 2731edc -- fitting.py` changes only the Tougaard guard comment; no numeric code changed. The `2731edc` file list matches the expected scope: docs, `templates/index.html`, `fitting.py`, and the two Tougaard test files.

exec
/bin/zsh -lc 'git diff --check 3d9ff54''^ 3d9ff54' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-I2ckyUlH' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-bYtJvxOH' (errno=Operation not permitted)

exec
/bin/zsh -lc 'git diff --unified=0 3d9ff54''^ 3d9ff54 -- fitting.py templates/index.html autofit/engine.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hkCoARQF' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZlSEfmbp' (errno=Operation not permitted)
diff --git a/fitting.py b/fitting.py
index ee26392..ae08d1e 100644
--- a/fitting.py
+++ b/fitting.py
@@ -508,2 +508,7 @@ def shirley_linear_background(
-def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-    """Simplified single-pass Tougaard universal-cross-section background.
+def tougaard_background(
+    x: np.ndarray,
+    y: np.ndarray,
+    n_avg: int = 1,
+) -> np.ndarray:
+    """Single-pass Tougaard universal-cross-section background, with the
+    constant (pre-loss) term the window-limited integral cannot generate.
@@ -515 +520,25 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-    kernel maximum sits at T = sqrt(C/3) ≈ 23.4 eV energy loss).
+    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).
+
+    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
+    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
+    window BEGINS in a loss-free region, so that J at the low-BE edge is
+    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
+    there is a large inelastic baseline produced by every lower-BE
+    (higher-KE) transition OUTSIDE the window, which a window-limited
+    integral structurally cannot reproduce.  Because K(0) = 0, the bare
+    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
+    — the background visibly dove to ~0 there, and a flat featureless
+    window produced a full-amplitude phantom "signal".
+
+    So the low-BE edge level is taken as a constant offset C0 (the
+    out-of-window baseline the kernel cannot see), the kernel runs over the
+    net (J - C0), and the amplitude is then anchored so the background
+    meets the measured intensity at the HIGH-BE edge — the standard
+    practical Tougaard criterion (B is effectively fitted, which is why the
+    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
+    fitting B together with an offset rather than B alone.
+
+    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
+    levels are read, so neither C0 nor the high-BE anchor rests on a single
+    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
+    endpoints = previous behaviour.
@@ -520,3 +549,2 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-    is normalized internally (see below). The amplitude is anchored so the
-    background matches the measured intensity at the high-BE edge of the
-    window, matching the frontend JS twin ``tougaardBackground``.
+    is normalized internally.  Mirrors the frontend JS twin
+    ``tougaardBackground``.
@@ -536,0 +565,2 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
+    if n_avg > 1:
+        ya = _apply_endpoint_averaging(ya, n_avg)
@@ -547,0 +578,6 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
+    # C0: the low-BE edge level = index -1 on the descending working array.
+    # This is the out-of-window (pre-loss) baseline; the kernel integral is
+    # run on the net above it.
+    c0 = float(ya[-1])
+    net = ya - c0
+
@@ -550 +586,2 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·y[j],  K(T) = B·T / (C + T²)².
+    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·net[j]·w[j],  K(T) = B·T / (C + T²)²,
+    # w[j] = the local quadrature weight (energy spacing) at point j.
@@ -552,7 +589,12 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx, so the kernel depends
-    # only on the index gap and this one-sided correlation collapses to a
-    # convolution against a single precomputed kernel vector — evaluated in C
-    # via np.convolve instead of an n-iteration Python loop (audit F7). On a
-    # NONUNIFORM grid that identity does not hold, so we keep the exact
-    # per-point separation loop (slower, but numerically unchanged). Never
-    # substitute (j-i)·dx for the true separation unless uniformity is verified.
+    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx and w[j] == dx, so the
+    # kernel depends only on the index gap and this one-sided correlation
+    # collapses to a convolution against a single precomputed kernel vector —
+    # evaluated in C via np.convolve instead of an n-iteration Python loop
+    # (audit F7). On a NONUNIFORM grid neither identity holds, so we keep the
+    # exact per-point separation loop AND per-point weights (audit F2,
+    # 2026-07-17: the loop previously used exact separations but omitted the
+    # spacing weights, silently applying a uniform-grid quadrature inside the
+    # branch written precisely because the grid is not uniform — up to ~24%
+    # error on a genuinely nonuniform grid). np.gradient returns dx exactly
+    # on a uniform grid, so both branches agree to floating point and the
+    # uniformity test is a pure optimization, not a semantic fork.
@@ -566,2 +608,2 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·y[i+m]  =  conv(y, reverse(k))[n-1+i]
-        bg = np.convolve(ya, k[::-1])[n - 1:]
+        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·net[i+m]  =  conv(net, reverse(k))[n-1+i]
+        bg = np.convolve(net, k[::-1])[n - 1:] * dx
@@ -568,0 +611 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
+        w = np.abs(np.gradient(xa))
@@ -573,3 +616 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-            bg[i] = float(np.sum(kernel * ya[i:]))
-
-    bg = bg * dx
+            bg[i] = float(np.sum(kernel * net[i:] * w[i:]))
@@ -577 +618 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-    # Amplitude anchor: scale the correlation so the background equals the
+    # Amplitude anchor: scale the loss integral so the background equals the
@@ -579,17 +620,12 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
-    # working array) — the standard practical Tougaard criterion, i.e. B is
-    # effectively fitted so the background meets the spectrum above the
-    # peak (which also makes the nominal B_coef cancel; C alone sets the
-    # kernel shape). History: this used to "rescale to the trailing
-    # endpoint", but K(0) = 0 makes bg[-1] identically zero, so the
-    # zero-guard always fired and the code multiplied by the raw trailing
-    # counts instead — a scale that is harmless only while the squared-C
-    # kernel kept bg near zero, and off by ~the baseline counts once C is
-    # corrected. Guard semantics: if NO net loss signal accumulates at the
-    # high-BE edge (bg[0] == 0 — e.g. all counts zero, or zero everywhere
-    # below the edge point), the correlation is returned UNANCHORED (all
-    # zeros in practice) rather than force-matched to the edge intensity.
-    # Negative counts (physically invalid input) pass through signed; no
-    # clamping policy is imposed here.
-    denom = bg[0] if bg[0] != 0.0 else 1.0
-    bg = bg * (float(ya[0]) / denom)
-    return bg[::-1] if flipped else bg
+    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
+    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
+    # flat or empty window), the honest background is the flat pre-loss level
+    # C0 itself, NOT zeros: a featureless window contains no loss signal to
+    # model, and returning zeros would report the entire baseline as net
+    # signal (the pre-F1 behaviour). Negative counts (physically invalid
+    # input) pass through signed; no clamping policy is imposed here.
+    if bg[0] == 0.0:
+        out = np.full(n, c0)
+    else:
+        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])
+    return out[::-1] if flipped else out
diff --git a/templates/index.html b/templates/index.html
index 173e1c1..61ff8a7 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4136 +4136 @@ function linearBackground(be, intensity) {
-function tougaardBackground(be, intensity) {
+function tougaardBackground(be, intensity, nAvg) {
@@ -4145,2 +4145,21 @@ function tougaardBackground(be, intensity) {
-  const inW = flipped ? [...intensity].reverse() : intensity;
-  const dx = Math.abs(beW[1] - beW[0]);
+  let inW = flipped ? [...intensity].reverse() : intensity;
+  if (nAvg > 1) inW = _applyEndpointAveraging(inW, nAvg);
+  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
+  // integral assumes the window BEGINS loss-free, so J at the low-BE edge is
+  // the zero-loss level. Real windows never satisfy that: the out-of-window
+  // inelastic baseline from every lower-BE (higher-KE) transition cannot be
+  // reproduced by a window-limited integral, and since K(0) = 0 the bare
+  // integral is identically zero at the low-BE edge REGARDLESS of the data —
+  // the background dove to ~0 there and a flat window produced phantom
+  // signal. Take the low-BE level as a constant offset, run the kernel over
+  // the net above it, then anchor the amplitude at the high-BE edge.
+  const c0 = inW[n - 1];
+  // Local quadrature weights (F2, 2026-07-17): weight each term by its own
+  // energy spacing instead of a single dx lifted from the first two points,
+  // which silently assumed a uniform grid.
+  const w = new Array(n);
+  for (let i = 0; i < n; i++) {
+    if (i === 0) w[0] = Math.abs(beW[1] - beW[0]);
+    else if (i === n - 1) w[n - 1] = Math.abs(beW[n - 1] - beW[n - 2]);
+    else w[i] = Math.abs(beW[i + 1] - beW[i - 1]) / 2;
+  }
@@ -4152 +4171 @@ function tougaardBackground(be, intensity) {
-      sum += (B * T) / Math.pow(C + T * T, 2) * inW[j];
+      sum += (B * T) / Math.pow(C + T * T, 2) * (inW[j] - c0) * w[j];
@@ -4154 +4173 @@ function tougaardBackground(be, intensity) {
-    bg[i] = sum * dx;
+    bg[i] = sum;
@@ -4158,7 +4177,5 @@ function tougaardBackground(be, intensity) {
-  // the practical Tougaard criterion (B effectively fitted; C alone sets
-  // the kernel shape). The old code "rescaled to the trailing endpoint",
-  // but K(0)=0 makes bg[n-1] identically zero, so the || 1 guard always
-  // fired and it multiplied by raw trailing counts instead. Guard
-  // semantics: if no net loss signal accumulates at the high-BE edge
-  // (bg[0] === 0), the correlation is returned UNANCHORED (all zeros in
-  // practice) rather than force-matched to the edge. Negative counts
+  // the practical Tougaard criterion (B effectively fitted; C alone sets the
+  // kernel shape). Guard: if no net loss signal accumulates at the high-BE
+  // edge (bg[0] === 0 — e.g. a flat or empty window) the honest background is
+  // the flat pre-loss level C0 itself, NOT zeros; zeros would report the
+  // whole baseline as net signal (the pre-F1 behaviour). Negative counts
@@ -4166,2 +4183,7 @@ function tougaardBackground(be, intensity) {
-  const scale = inW[0] / (bg[0] || 1);
-  const out = bg.map(v => v * scale);
+  let out;
+  if (bg[0] === 0) {
+    out = new Array(n).fill(c0);
+  } else {
+    const scale = (inW[0] - c0) / bg[0];
+    out = bg.map(v => c0 + v * scale);
+  }

exec
/bin/zsh -lc 'git diff --stat 3d9ff54''^ 3d9ff54 -- autofit/engine.py autofit/methods fitting.py templates/index.html tests tests/autofit docs/autofit/inventory scripts' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cBAB7CMT' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3SiGZlqP' (errno=Operation not permitted)
 fitting.py                        | 110 +++++++++++++++++++++-----------
 templates/index.html              |  50 ++++++++++-----
 tests/js/tougaard_twin.test.js    |  44 ++++++++++---
 tests/test_tougaard_background.py | 129 ++++++++++++++++++++++++++++++++++----
 4 files changed, 260 insertions(+), 73 deletions(-)

codex
The caller paths look compatible so far: backend call sites still pass already endpoint-averaged arrays, and frontend call sites still pass two arguments after external pre-averaging. I’m running the focused Python and JS tests next, with bytecode/cache writes disabled where possible because the workspace is read-only.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_tougaard_background.py' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: pytest

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '4130,4350p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
  4130	// Single-pass Tougaard background — JS twin of fitting.py's
  4131	// tougaard_background (keep the two numerically in agreement; pinned by
  4132	// tests/js/tougaard_twin.test.js). Universal loss kernel
  4133	// K(T) = B·T/(C+T²)² with B = 2866 eV², C = 1643 eV² (S. Tougaard,
  4134	// Surf. Interface Anal. 11, 453 (1988); kernel max at sqrt(C/3) ≈ 23.4 eV).
  4135	// C was long shipped squared (1643*1643) — fixed 2026-07-04 with the backend.
  4136	function tougaardBackground(be, intensity, nAvg) {
  4137	  const n = be.length;
  4138	  if (n < 2) return new Array(n).fill(0);
  4139	  const B = 2866, C = 1643;
  4140	  // The one-sided loss sum (j >= i) is physical only on a DESCENDING BE
  4141	  // grid (loss contributions come from lower-BE / higher-KE emitters).
  4142	  // Normalize to descending internally and flip back, like the backend.
  4143	  const flipped = be[0] < be[n - 1];
  4144	  const beW = flipped ? [...be].reverse() : be;
  4145	  let inW = flipped ? [...intensity].reverse() : intensity;
  4146	  if (nAvg > 1) inW = _applyEndpointAveraging(inW, nAvg);
  4147	  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
  4148	  // integral assumes the window BEGINS loss-free, so J at the low-BE edge is
  4149	  // the zero-loss level. Real windows never satisfy that: the out-of-window
  4150	  // inelastic baseline from every lower-BE (higher-KE) transition cannot be
  4151	  // reproduced by a window-limited integral, and since K(0) = 0 the bare
  4152	  // integral is identically zero at the low-BE edge REGARDLESS of the data —
  4153	  // the background dove to ~0 there and a flat window produced phantom
  4154	  // signal. Take the low-BE level as a constant offset, run the kernel over
  4155	  // the net above it, then anchor the amplitude at the high-BE edge.
  4156	  const c0 = inW[n - 1];
  4157	  // Local quadrature weights (F2, 2026-07-17): weight each term by its own
  4158	  // energy spacing instead of a single dx lifted from the first two points,
  4159	  // which silently assumed a uniform grid.
  4160	  const w = new Array(n);
  4161	  for (let i = 0; i < n; i++) {
  4162	    if (i === 0) w[0] = Math.abs(beW[1] - beW[0]);
  4163	    else if (i === n - 1) w[n - 1] = Math.abs(beW[n - 1] - beW[n - 2]);
  4164	    else w[i] = Math.abs(beW[i + 1] - beW[i - 1]) / 2;
  4165	  }
  4166	  const bg = new Array(n).fill(0);
  4167	  for (let i = 0; i < n; i++) {
  4168	    let sum = 0;
  4169	    for (let j = i; j < n; j++) {
  4170	      const T = Math.abs(beW[j] - beW[i]);
  4171	      sum += (B * T) / Math.pow(C + T * T, 2) * (inW[j] - c0) * w[j];
  4172	    }
  4173	    bg[i] = sum;
  4174	  }
  4175	  // Amplitude anchor at the HIGH-BE edge (index 0 after normalization):
  4176	  // scale so the background meets the measured intensity above the peak —
  4177	  // the practical Tougaard criterion (B effectively fitted; C alone sets the
  4178	  // kernel shape). Guard: if no net loss signal accumulates at the high-BE
  4179	  // edge (bg[0] === 0 — e.g. a flat or empty window) the honest background is
  4180	  // the flat pre-loss level C0 itself, NOT zeros; zeros would report the
  4181	  // whole baseline as net signal (the pre-F1 behaviour). Negative counts
  4182	  // (physically invalid input) pass through signed; no clamping here.
  4183	  let out;
  4184	  if (bg[0] === 0) {
  4185	    out = new Array(n).fill(c0);
  4186	  } else {
  4187	    const scale = (inW[0] - c0) / bg[0];
  4188	    out = bg.map(v => c0 + v * scale);
  4189	  }
  4190	  return flipped ? out.reverse() : out;
  4191	}
  4192	
  4193	// Apply endpoint averaging: replace first/last N points with their mean so
  4194	// existing Shirley/Smart functions pick up averaged endpoint intensities.
  4195	// Returns a new array — does not mutate the input.
  4196	function _applyEndpointAveraging(intensity, nAvg) {
  4197	  const n = intensity.length;
  4198	  if (nAvg <= 1 || n < 4) return intensity;
  4199	  const cap = Math.min(nAvg, Math.floor(n / 4));
  4200	  const out = [...intensity];
  4201	  let sumL = 0, sumR = 0;
  4202	  for (let i = 0; i < cap; i++) sumL += intensity[i];
  4203	  for (let i = n - cap; i < n; i++) sumR += intensity[i];
  4204	  const avgL = sumL / cap, avgR = sumR / cap;
  4205	  for (let i = 0; i < cap; i++) out[i] = avgL;
  4206	  for (let i = n - cap; i < n; i++) out[i] = avgR;
  4207	  return out;
  4208	}
  4209	
  4210	// Shirley + Linear: a linear baseline plus a Shirley-like cumulative correction.
  4211	// Completely standalone — does not call shirleyBackground / smartBackground.
  4212	function shirleyLinearBackground(be, intensity, maxIter, nAvg) {
  4213	  const n = be.length;
  4214	  if (n < 2) return new Array(n).fill(0);
  4215	
  4216	  // 1. Averaged endpoints
  4217	  const cap = Math.min(nAvg || 1, Math.floor(n / 4)) || 1;
  4218	  let sL = 0, sR = 0;
  4219	  for (let i = 0; i < cap; i++) sL += intensity[i];
  4220	  for (let i = n - cap; i < n; i++) sR += intensity[i];
  4221	  const IL = sL / cap;   // left (high-BE) endpoint
  4222	  const IR = sR / cap;   // right (low-BE) endpoint
  4223	
  4224	  // 2. Linear baseline between averaged endpoints
  4225	  const linear = new Array(n);
  4226	  for (let i = 0; i < n; i++) linear[i] = IL + (IR - IL) * i / (n - 1);
  4227	
  4228	  // 3. Flatten: subtract linear baseline
  4229	  const flat = intensity.map((v, i) => v - linear[i]);
  4230	
  4231	  // 4. Iterative Shirley-like correction on the flattened data.
  4232	  //    Step height = |IL - IR| (the endpoint difference drives the Shirley step).
  4233	  const stepH = Math.abs(IL - IR);
  4234	  if (stepH < 1e-12) return linear;   // endpoints equal → pure linear
  4235	
  4236	  let bg = new Array(n).fill(0);      // Shirley correction term
  4237	
  4238	  for (let iter = 0; iter < maxIter; iter++) {
  4239	    const newBg = new Array(n).fill(0);
  4240	    // Cumulative integral of (flattened signal - current bg) from right to left
  4241	    let totalInt = 0;
  4242	    for (let j = 0; j < n - 1; j++) {
  4243	      totalInt += ((Math.max(flat[j] - bg[j], 0) + Math.max(flat[j + 1] - bg[j + 1], 0)) / 2)
  4244	                  * Math.abs(be[j + 1] - be[j]);
  4245	    }
  4246	    if (totalInt <= 0) break;
  4247	
  4248	    for (let i = 0; i < n; i++) {
  4249	      let sumRight = 0;
  4250	      for (let j = i; j < n - 1; j++) {
  4251	        sumRight += ((Math.max(flat[j] - bg[j], 0) + Math.max(flat[j + 1] - bg[j + 1], 0)) / 2)
  4252	                    * Math.abs(be[j + 1] - be[j]);
  4253	      }
  4254	      // Scale by step height, normalised by total integral
  4255	      newBg[i] = stepH * (sumRight / totalInt);
  4256	    }
  4257	    bg = newBg;
  4258	  }
  4259	
  4260	  // 5. Combine: linear baseline + Shirley correction, clamped to data
  4261	  const result = new Array(n);
  4262	  for (let i = 0; i < n; i++) {
  4263	    result[i] = Math.min(linear[i] + bg[i], intensity[i]);
  4264	  }
  4265	  return result;
  4266	}
  4267	
  4268	// Clear stored background so updatePlot recomputes it
  4269	function _invalidateBgCache() {
  4270	  if (state.fitResult) state.fitResult.bgIntensity = null;
  4271	}
  4272	
  4273	// Clear stored fit envelope so the fallback (modelFull + bg) is used after a manual peak edit
  4274	function _invalidateFittedY() {
  4275	  if (state.fitResult) state.fitResult.fittedY = null;
  4276	}
  4277	
  4278	function _clampShirleyIter() {
  4279	  const el = document.getElementById('shirley-iter');
  4280	  let v = parseInt(el.value);
  4281	  if (isNaN(v)) return;
  4282	  if (v < 1) el.value = 1;
  4283	  else if (v > 50) el.value = 50;
  4284	}
  4285	
  4286	// Pure-functional background computation. Takes explicit `settings`
  4287	// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
  4288	// endpointAvg) instead of reading from DOM. Used by stack-view render
  4289	// to reproduce a source tab's background from its persisted ui state.
  4290	// computeBackground() below is a thin DOM-reading wrapper for callers
  4291	// in the single-tab plot path.
  4292	function computeBackgroundCore(be, intensity, settings) {
  4293	  const type = settings.bgType;
  4294	  const iter = parseInt(settings.shirleyIter) || 5;
  4295	  const nAvg = parseInt(settings.endpointAvg) || 1;
  4296	
  4297	  // Manual anchor background uses its own anchor points, not bg-start/end
  4298	  if (type === 'manual') return manualAnchorBackground(be, intensity);
  4299	
  4300	  // Get background endpoint range from settings
  4301	  const bgStartBE = parseFloat(settings.bgStart);
  4302	  const bgEndBE   = parseFloat(settings.bgEnd);
  4303	  const bgLo = Math.min(bgStartBE, bgEndBE);
  4304	  const bgHi = Math.max(bgStartBE, bgEndBE);
  4305	
  4306	  // Find indices within the bg range
  4307	  const bgIndices = [];
  4308	  for (let i = 0; i < be.length; i++) {
  4309	    if (be[i] >= bgLo && be[i] <= bgHi) bgIndices.push(i);
  4310	  }
  4311	
  4312	  // If bg range doesn't overlap data, fall back to full range
  4313	  if (bgIndices.length < 2) {
  4314	    const avgIn = _applyEndpointAveraging(intensity, nAvg);
  4315	    if (type === 'shirley') return shirleyBackground(be, avgIn, iter);
  4316	    if (type === 'smart') return smartBackground(be, avgIn, iter);
  4317	    if (type === 'smart_exp') return smartExperimentalBackground(be, intensity, iter, nAvg);
  4318	    if (type === 'shirley_linear') return shirleyLinearBackground(be, intensity, iter, nAvg);
  4319	    if (type === 'linear') return linearBackground(be, intensity);
  4320	    // Endpoint averaging matters for Tougaard since the amplitude is
  4321	    // anchored at the high-BE edge — mirror the backend callers, which all
  4322	    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
  4323	    if (type === 'tougaard') return tougaardBackground(be, avgIn);
  4324	    return new Array(be.length).fill(0);
  4325	  }
  4326	
  4327	  const i0 = bgIndices[0];
  4328	  const i1 = bgIndices[bgIndices.length - 1];
  4329	
  4330	  // Slice data to background region
  4331	  const beSub = be.slice(i0, i1 + 1);
  4332	  const inSub = intensity.slice(i0, i1 + 1);
  4333	
  4334	  // Compute background on the sliced region — apply endpoint averaging for Shirley types
  4335	  let bgSub;
  4336	  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  4337	  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  4338	  else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
  4339	  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
  4340	  else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
  4341	  // Averaged for the same reason as Shirley types: the Tougaard amplitude
  4342	  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
  4343	  // directly. Mirrors fitting.py's run_fit / compute_background_only.
  4344	  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
  4345	  else return new Array(be.length).fill(0);
  4346	
  4347	  // Extend background across full data range:
  4348	  // - Points before bg region: hold first bg value (flat)
  4349	  // - Points inside bg region: use computed bg
  4350	  // - Points after bg region: hold last bg value (flat)

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '432,625p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   432	def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
   433	    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
   434	    n = len(y)
   435	    if n_avg <= 1 or n < 4:
   436	        return y.copy()
   437	    cap = min(n_avg, n // 4)
   438	    if cap < 1:
   439	        return y.copy()
   440	    out = y.copy()
   441	    out[:cap] = np.mean(y[:cap])
   442	    out[-cap:] = np.mean(y[-cap:])
   443	    return out
   444	
   445	
   446	def shirley_linear_background(
   447	    x: np.ndarray,
   448	    y: np.ndarray,
   449	    n_iter: int = 200,
   450	    tol: float = 1e-6,
   451	    n_avg: int = 1,
   452	) -> np.ndarray:
   453	    """Hybrid Shirley + Linear background.
   454	
   455	    1. Average *n_avg* points at each endpoint.
   456	    2. Compute a linear baseline between the averaged endpoints.
   457	    3. Subtract the linear baseline → flattened data.
   458	    4. Iteratively compute a Shirley‑like cumulative correction on the
   459	       flattened data, scaled by the endpoint step height.
   460	    5. Add the correction back onto the linear baseline.
   461	    6. Clamp so the background never exceeds the data.
   462	    """
   463	    if len(x) < 2:
   464	        return np.zeros_like(y)
   465	
   466	    # Work on ascending copy
   467	    if x[0] > x[-1]:
   468	        xs, ys = x[::-1].copy(), y[::-1].copy()
   469	        flipped = True
   470	    else:
   471	        xs, ys = x.copy(), y.copy()
   472	        flipped = False
   473	
   474	    n = len(ys)
   475	    cap = max(1, min(n_avg, n // 4))
   476	    IL = float(np.mean(ys[:cap]))      # low‑BE endpoint
   477	    IH = float(np.mean(ys[-cap:]))     # high‑BE endpoint
   478	
   479	    # Linear baseline
   480	    linear = np.linspace(IL, IH, n)
   481	
   482	    # Flatten
   483	    flat = ys - linear
   484	
   485	    step_h = abs(IL - IH)
   486	    if step_h < 1e-12:
   487	        return linear[::-1] if flipped else linear
   488	
   489	    B = np.zeros(n)
   490	    for _ in range(n_iter):
   491	        B_prev = B.copy()
   492	        signal = np.maximum(flat - B, 0.0)
   493	        # O(n) cumulative integral from high-x end back to each point
   494	        cum_right = np.zeros(n)
   495	        for i in range(n - 2, -1, -1):
   496	            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
   497	        total = cum_right[0]
   498	        if total <= 0.0:
   499	            break
   500	        B = step_h * cum_right / total
   501	        if np.max(np.abs(B - B_prev)) < tol:
   502	            break
   503	
   504	    result = np.minimum(linear + B, ys)
   505	    return result[::-1] if flipped else result
   506	
   507	
   508	def tougaard_background(
   509	    x: np.ndarray,
   510	    y: np.ndarray,
   511	    n_avg: int = 1,
   512	) -> np.ndarray:
   513	    """Single-pass Tougaard universal-cross-section background, with the
   514	    constant (pre-loss) term the window-limited integral cannot generate.
   515	
   516	    Uses the two-parameter universal loss function
   517	    K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
   518	    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
   519	    cross-section fitted to noble/transition-metal optical data; the
   520	    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).
   521	
   522	    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
   523	    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
   524	    window BEGINS in a loss-free region, so that J at the low-BE edge is
   525	    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
   526	    there is a large inelastic baseline produced by every lower-BE
   527	    (higher-KE) transition OUTSIDE the window, which a window-limited
   528	    integral structurally cannot reproduce.  Because K(0) = 0, the bare
   529	    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
   530	    — the background visibly dove to ~0 there, and a flat featureless
   531	    window produced a full-amplitude phantom "signal".
   532	
   533	    So the low-BE edge level is taken as a constant offset C0 (the
   534	    out-of-window baseline the kernel cannot see), the kernel runs over the
   535	    net (J - C0), and the amplitude is then anchored so the background
   536	    meets the measured intensity at the HIGH-BE edge — the standard
   537	    practical Tougaard criterion (B is effectively fitted, which is why the
   538	    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
   539	    fitting B together with an offset rather than B alone.
   540	
   541	    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
   542	    levels are read, so neither C0 nor the high-BE anchor rests on a single
   543	    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
   544	    endpoints = previous behaviour.
   545	
   546	    The background at each binding energy accumulates loss contributions
   547	    from electrons emitted at LOWER BE (higher kinetic energy), so the
   548	    one-sided sum requires a descending-BE grid; input in either BE order
   549	    is normalized internally.  Mirrors the frontend JS twin
   550	    ``tougaardBackground``.
   551	    """
   552	    n = len(x)
   553	    if n < 2:
   554	        return np.zeros_like(y, dtype=float)
   555	
   556	    # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
   557	    # C = 1643 eV². A long-standing transcription slip shipped C = 1643²
   558	    # (~2.7e6 eV²), which pushed the kernel maximum from ~23 eV to ~949 eV
   559	    # of energy loss and flattened the background to ~zero over any real
   560	    # XPS window. Fixed 2026-07-04 together with the JS twin.
   561	    B_coef, C_coef = 2866.0, 1643.0
   562	
   563	    xa = np.asarray(x, dtype=float)
   564	    ya = np.asarray(y, dtype=float)
   565	    if n_avg > 1:
   566	        ya = _apply_endpoint_averaging(ya, n_avg)
   567	
   568	    # The one-sided loss sum below (j >= i) is physical only when BE
   569	    # DESCENDS along the array: the loss contributions at x[i] must come
   570	    # from lower-BE (higher-KE) emitters, which sit at higher indices only
   571	    # on a descending grid. Normalize to descending internally and flip
   572	    # the result back — the mirror of shirley_background's ascending
   573	    # normalization — so both BE orderings give identical output.
   574	    flipped = bool(xa[0] < xa[-1])
   575	    if flipped:
   576	        xa, ya = xa[::-1].copy(), ya[::-1].copy()
   577	
   578	    # C0: the low-BE edge level = index -1 on the descending working array.
   579	    # This is the out-of-window (pre-loss) baseline; the kernel integral is
   580	    # run on the net above it.
   581	    c0 = float(ya[-1])
   582	    net = ya - c0
   583	
   584	    dx = float(abs(xa[1] - xa[0]))
   585	
   586	    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·net[j]·w[j],  K(T) = B·T / (C + T²)²,
   587	    # w[j] = the local quadrature weight (energy spacing) at point j.
   588	    #
   589	    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx and w[j] == dx, so the
   590	    # kernel depends only on the index gap and this one-sided correlation
   591	    # collapses to a convolution against a single precomputed kernel vector —
   592	    # evaluated in C via np.convolve instead of an n-iteration Python loop
   593	    # (audit F7). On a NONUNIFORM grid neither identity holds, so we keep the
   594	    # exact per-point separation loop AND per-point weights (audit F2,
   595	    # 2026-07-17: the loop previously used exact separations but omitted the
   596	    # spacing weights, silently applying a uniform-grid quadrature inside the
   597	    # branch written precisely because the grid is not uniform — up to ~24%
   598	    # error on a genuinely nonuniform grid). np.gradient returns dx exactly
   599	    # on a uniform grid, so both branches agree to floating point and the
   600	    # uniformity test is a pure optimization, not a semantic fork.
   601	    diffs = np.diff(xa)
   602	    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)
   603	
   604	    if uniform:
   605	        m = np.arange(n, dtype=float)
   606	        T = m * dx
   607	        k = (B_coef * T) / (C_coef + T * T) ** 2          # k[m] = K(m·dx)
   608	        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·net[i+m]  =  conv(net, reverse(k))[n-1+i]
   609	        bg = np.convolve(net, k[::-1])[n - 1:] * dx
   610	    else:
   611	        w = np.abs(np.gradient(xa))
   612	        bg = np.zeros(n)
   613	        for i in range(n):
   614	            T = np.abs(xa[i:] - xa[i])
   615	            kernel = (B_coef * T) / (C_coef + T * T) ** 2
   616	            bg[i] = float(np.sum(kernel * net[i:] * w[i:]))
   617	
   618	    # Amplitude anchor: scale the loss integral so the background equals the
   619	    # measured intensity at the HIGH-BE edge (index 0 on the descending
   620	    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
   621	    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
   622	    # flat or empty window), the honest background is the flat pre-loss level
   623	    # C0 itself, NOT zeros: a featureless window contains no loss signal to
   624	    # model, and returning zeros would report the entire baseline as net
   625	    # signal (the pre-F1 behaviour). Negative counts (physically invalid

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '285,305p' && nl -ba autofit/parity.py | sed -n '96,112p' && nl -ba fitting.py | sed -n '1028,1042p;1268,1280p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   285	# ─────────────────────────────────────────────────────────────────────────────
   286	
   287	def _compute_background(x: np.ndarray, y: np.ndarray, bg: BackgroundType) -> np.ndarray:
   288	    if bg is BackgroundType.SHIRLEY:
   289	        return shirley_background(x, y)
   290	    if bg is BackgroundType.SMART:
   291	        return smart_background(x, y)
   292	    if bg is BackgroundType.SMART_EXP:
   293	        from fitting import smart_experimental_background
   294	        return smart_experimental_background(x, y)
   295	    if bg is BackgroundType.LINEAR:
   296	        return linear_background(x, y)
   297	    if bg is BackgroundType.TOUGAARD:
   298	        from fitting import tougaard_background
   299	        return tougaard_background(x, y)
   300	    raise ValueError(f"Unknown background type: {bg}")
   301	
   302	
   303	# ─────────────────────────────────────────────────────────────────────────────
   304	# lmfit model construction
   305	# ─────────────────────────────────────────────────────────────────────────────
    96	    m = (method or "shirley").lower()
    97	
    98	    if m == "shirley":
    99	        bg_inner = shirley_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
   100	    elif m == "smart":
   101	        bg_inner = smart_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
   102	    elif m == "smart_exp":
   103	        bg_inner = smart_experimental_background(xb, yb, n_avg=endpoint_avg)
   104	    elif m == "shirley_linear":
   105	        bg_inner = shirley_linear_background(xb, yb, n_avg=endpoint_avg)
   106	    elif m == "tougaard":
   107	        bg_inner = tougaard_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
   108	    elif m == "linear":
   109	        if x[i1 - 1] != x[i0]:
   110	            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
   111	        else:
   112	            slope = 0.0
  1028	            bg = linear_background(x, y)
  1029	    elif bg_method == "shirley":
  1030	        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
  1031	    elif bg_method == "smart":
  1032	        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
  1033	    elif bg_method == "smart_exp":
  1034	        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
  1035	    elif bg_method == "shirley_linear":
  1036	        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
  1037	    elif bg_method == "tougaard":
  1038	        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
  1039	    elif bg_method == "linear":
  1040	        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
  1041	        # across the full ROI. The line is well-defined everywhere, so
  1042	        # constant extension would discard real information.
  1268	        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
  1269	    elif method == "smart":
  1270	        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
  1271	    elif method == "smart_exp":
  1272	        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
  1273	    elif method == "shirley_linear":
  1274	        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
  1275	    elif method == "tougaard":
  1276	        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
  1277	    elif method == "linear":
  1278	        bg = linear_background(x, y)
  1279	    elif method in ("none", "flat", "", "manual"):
  1280	        bg = np.zeros_like(y)

exec
/bin/zsh -lc 'node --test tests/js/tougaard_twin.test.js' in /Users/skyefortier/xps-verify
 succeeded in 151ms:
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 1 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 14.168309
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 2 - ascending and descending BE input give the identical background
  ---
  duration_ms: 0.688508
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 3 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.372308
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 4 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 2.858788
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 5 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 2.083041
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 6 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 0.779334
  type: 'test'
  ...
1..6
# tests 6
# suites 0
# pass 6
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 107.818879

codex
The JS twin passes. `pytest` is not installed on this PATH, so I can’t execute the Python test file through pytest here; I’ll still run small direct Python probes against `fitting.py` if Python and NumPy import cleanly.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '625,635p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   625	    # signal (the pre-F1 behaviour). Negative counts (physically invalid
   626	    # input) pass through signed; no clamping policy is imposed here.
   627	    if bg[0] == 0.0:
   628	        out = np.full(n, c0)
   629	    else:
   630	        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])
   631	    return out[::-1] if flipped else out
   632	
   633	
   634	def _la_casaxps_true(
   635	    x: np.ndarray,

exec
/bin/zsh -lc 'git diff --exit-code 3d9ff54''^ 3d9ff54 -- autofit/methods; printf '"'methods_diff_exit=%s\\n' "'$?' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ADUZbqak' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-zuS3DKld' (errno=Operation not permitted)
methods_diff_exit=0

exec
/bin/zsh -lc 'git diff --exit-code 3d9ff54''^ 3d9ff54 -- autofit/engine.py; printf '"'engine_diff_exit=%s\\n' "'$?' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qPs6I5it' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-n0TPLBFb' (errno=Operation not permitted)
engine_diff_exit=0

codex
Shell here-docs are blocked by the read-only temp setup, but ordinary one-line Python commands should still work. I’m using those for numeric probes and expected-value verification.
exec
/bin/zsh -lc "python3 -c \"import numpy as np; from fitting import tougaard_background; x=np.linspace(740.0,700.0,200); y=np.full_like(x,500.0); bg=tougaard_background(x,y); print('flat_max_net', float(np.max(np.abs(y-bg))), 'edges', float(bg[0]), float(bg[-1])); x2=np.linspace(10.0,0.0,11); y2=np.linspace(100.0,200.0,11); bg2=tougaard_background(x2,y2); print('neg_scale_edges', float(bg2[0]), float(bg2[-1]), 'min', float(bg2.min()), 'max', float(bg2.max())); print('neg_scale_bg', np.array2string(bg2, precision=3)); x3=np.array([291.0,290.0,289.0,288.0]); y3=np.array([100.0,0.0,0.0,0.0]); print('guard_fixture', tougaard_background(x3,y3))\"" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'python3 -c "import numpy as np; from fitting import tougaard_background; x=np.linspace(295.0,280.0,151); y=500.0 + 1000*np.exp(-0.5*((x-284.0)/1.2)**2) + 250*np.exp(-0.5*((x-289.2)/0.7)**2); bg=tougaard_background(x,y); [print(i, repr(float(bg[i]))) for i in [0,30,75,110,149,150]]"' in /Users/skyefortier/xps-verify
 exited 1 in 433ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

 exited 1 in 403ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

codex
The system Python lacks both `pytest` and `lmfit`, so direct import of `fitting.py` is blocked there. I’m checking for a project virtualenv before falling back fully to static analysis plus the passing JS test.
exec
/bin/zsh -lc "rg --files -g 'pyproject.toml' -g 'pytest.ini' -g 'requirements*.txt' -g 'venv/bin/python' -g '.venv/bin/python' -g 'package.json' -g 'package-lock.json'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
requirements-dev.txt
requirements.txt

exec
/bin/zsh -lc "ls -ld venv .venv 2>/dev/null; ls venv/bin 2>/dev/null | sed -n '1,40p'; ls .venv/bin 2>/dev/null | sed -n '1,40p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
exec
/bin/zsh -lc 'git show 3d9ff54''^:fitting.py | nl -ba | sed -n '"'1028,1040p;1268,1278p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ssyGa1Eo' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-moG9DpFr' (errno=Operation not permitted)
  1028	                bg[i1:] = bg_inner[-1]
  1029	
  1030	    y_sub = y - bg
  1031	
  1032	    # Poisson weights: σ = √(raw counts), weight = 1/σ
  1033	    # Use raw counts (before background subtraction) for uncertainty estimate,
  1034	    # since the noise comes from the total photon counting statistics.
  1035	    # Floor at 1.0 to avoid division by zero for zero-count channels.
  1036	    sigma = np.sqrt(np.maximum(y, 1.0))
  1037	    weights = 1.0 / sigma
  1038	
  1039	    # ── Build composite lmfit model ───────────────────────────────────────────
  1040	    # Sort so unconstrained (master) peaks come before constrained ones

exec
/bin/zsh -lc 'git show 3d9ff54''^:templates/index.html | nl -ba | sed -n '"'4286,4346p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-lTAhC27L' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-o4RNDMSN' (errno=Operation not permitted)
  4286	  for (let i = 0; i < be.length; i++) {
  4287	    if (be[i] >= bgLo && be[i] <= bgHi) bgIndices.push(i);
  4288	  }
  4289	
  4290	  // If bg range doesn't overlap data, fall back to full range
  4291	  if (bgIndices.length < 2) {
  4292	    const avgIn = _applyEndpointAveraging(intensity, nAvg);
  4293	    if (type === 'shirley') return shirleyBackground(be, avgIn, iter);
  4294	    if (type === 'smart') return smartBackground(be, avgIn, iter);
  4295	    if (type === 'smart_exp') return smartExperimentalBackground(be, intensity, iter, nAvg);
  4296	    if (type === 'shirley_linear') return shirleyLinearBackground(be, intensity, iter, nAvg);
  4297	    if (type === 'linear') return linearBackground(be, intensity);
  4298	    // Endpoint averaging matters for Tougaard since the amplitude is
  4299	    // anchored at the high-BE edge — mirror the backend callers, which all
  4300	    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
  4301	    if (type === 'tougaard') return tougaardBackground(be, avgIn);
  4302	    return new Array(be.length).fill(0);
  4303	  }
  4304	
  4305	  const i0 = bgIndices[0];
  4306	  const i1 = bgIndices[bgIndices.length - 1];
  4307	
  4308	  // Slice data to background region
  4309	  const beSub = be.slice(i0, i1 + 1);
  4310	  const inSub = intensity.slice(i0, i1 + 1);
  4311	
  4312	  // Compute background on the sliced region — apply endpoint averaging for Shirley types
  4313	  let bgSub;
  4314	  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  4315	  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  4316	  else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
  4317	  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
  4318	  else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
  4319	  // Averaged for the same reason as Shirley types: the Tougaard amplitude
  4320	  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
  4321	  // directly. Mirrors fitting.py's run_fit / compute_background_only.
  4322	  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
  4323	  else return new Array(be.length).fill(0);
  4324	
  4325	  // Extend background across full data range:
  4326	  // - Points before bg region: hold first bg value (flat)
  4327	  // - Points inside bg region: use computed bg
  4328	  // - Points after bg region: hold last bg value (flat)
  4329	  const full = new Array(be.length).fill(0);
  4330	  const bgLeft  = bgSub[0];
  4331	  const bgRight = bgSub[bgSub.length - 1];
  4332	
  4333	  for (let i = 0; i < be.length; i++) {
  4334	    if (i < i0) full[i] = bgLeft;
  4335	    else if (i <= i1) full[i] = bgSub[i - i0];
  4336	    else full[i] = bgRight;
  4337	  }
  4338	
  4339	  return full;
  4340	}
  4341	
  4342	// Thin DOM-reading wrapper used by single-tab updatePlot. Stack render
  4343	// path calls computeBackgroundCore directly with source-tab settings.
  4344	function computeBackground(be, intensity) {
  4345	  return computeBackgroundCore(be, intensity, {
  4346	    bgType:      document.getElementById('bg-type').value,

codex
There is no `venv` or `.venv` in this checkout; dependency installation is not possible under the current no-network/read-only constraints. I confirmed the parent commit already had the current frontend pre-averaging call convention, so this commit did not move that Unit 2 boundary.
exec
/bin/zsh -lc "nl -ba tests/test_tougaard_background.py | sed -n '50,260p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    50	    return x, y
    51	
    52	
    53	def test_kernel_peak_near_sqrt_c_over_3():
    54	    """The loss-kernel response to a delta-like peak must peak ~23.4 eV
    55	    above the peak (sqrt(C/3) with C = 1643 eV²), not ~949 eV.
    56	
    57	    A spike at x0 on a descending grid produces bg(x) ∝ K(x − x0) on the
    58	    high-BE side, so the argmax of the background directly locates the
    59	    kernel maximum.
    60	    """
    61	    x = np.linspace(100.0, 0.0, 1001)  # descending, dx = 0.1 eV
    62	    # A pedestal PLUS a high-BE step. The step matters: since the F1 offset
    63	    # fix (2026-07-17) the fitted amplitude is proportional to the measured
    64	    # rise across the window (data at the high-BE edge minus the low-BE
    65	    # pre-loss level). A perfectly flat pedestal therefore has NO loss
    66	    # intensity to model, so the honest background is flat and carries no
    67	    # kernel shape to inspect. The step gives the anchor something to fit;
    68	    # the background shape it scales is still the pure kernel response.
    69	    y = np.full_like(x, 1e-9)
    70	    y[0] = 2e-9  # high-BE edge: a measured rise -> nonzero fitted amplitude
    71	    spike_idx = 800  # x = 20.0 eV
    72	    y[spike_idx] = 1.0e6
    73	
    74	    bg = tougaard_background(x, y)
    75	
    76	    high_be_side = slice(0, spike_idx)  # x > 20 eV: traces K(x − 20)
    77	    peak_x = x[high_be_side][np.argmax(bg[high_be_side])]
    78	    expected = 20.0 + np.sqrt(1643.0 / 3.0)  # 20 + 23.402...
    79	    assert abs(peak_x - expected) <= 0.25, (
    80	        f"kernel response peaks at x = {peak_x:.2f} eV; expected "
    81	        f"{expected:.2f} eV (spike at 20.0 + sqrt(C/3) ≈ 23.4 eV). "
    82	        f"A peak near x = 100 means the squared constant (C = 1643²) is back."
    83	    )
    84	
    85	
    86	def test_ascending_and_descending_input_agree_exactly():
    87	    """The same spectrum fed in ascending vs descending BE order must give
    88	    the identical background (element-wise, after re-reversal)."""
    89	    x_d, y_d = _synthetic_spectrum(descending=True)
    90	    x_a, y_a = _synthetic_spectrum(descending=False)
    91	
    92	    bg_d = tougaard_background(x_d, y_d)
    93	    bg_a = tougaard_background(x_a, y_a)
    94	
    95	    assert np.array_equal(bg_d, bg_a[::-1]), (
    96	        f"order-dependent output: max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
    97	    )
    98	
    99	
   100	def test_ascending_descending_parity_on_nonuniform_grid():
   101	    """Order-robustness must also hold on the non-uniform-grid code path
   102	    (which uses the exact per-point separation loop, not the convolution)."""
   103	    # Deterministic, mildly non-uniform descending grid
   104	    steps = 0.08 + 0.04 * np.sin(np.arange(120))
   105	    x_d = 295.0 - np.concatenate(([0.0], np.cumsum(steps)))
   106	    y_d = 100.0 + 4000.0 * np.exp(-0.5 * ((x_d - 290.0) / 1.0) ** 2)
   107	
   108	    bg_d = tougaard_background(x_d, y_d)
   109	    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
   110	
   111	    assert np.array_equal(bg_d, bg_a[::-1]), (
   112	        f"non-uniform grid is order-dependent: "
   113	        f"max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
   114	    )
   115	
   116	
   117	def test_background_anchored_at_high_be_edge():
   118	    """The background must equal the measured intensity at the high-BE edge
   119	    of the window (practical Tougaard criterion: the universal cross-section
   120	    amplitude is scaled so the background meets the data above the peak),
   121	    and must vanish at the low-BE edge (no in-window emitters below it)."""
   122	    x, y = _synthetic_spectrum(descending=True)
   123	    bg = tougaard_background(x, y)
   124	
   125	    # x[0] is the high-BE edge on this descending grid
   126	    assert np.isclose(bg[0], y[0], rtol=1e-12), (
   127	        f"high-BE-edge anchor broken: bg[0] = {bg[0]}, data = {y[0]}"
   128	    )
   129	    # Since the F1 offset fix (2026-07-17) the low-BE edge carries the
   130	    # pre-loss constant C0 (the out-of-window baseline), NOT zero. K(0) = 0
   131	    # still makes the LOSS integral vanish there, so the background equals C0
   132	    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
   133	    # Asserting 0.0 here was pinning the bug: it forced the background to dive
   134	    # to zero at the low-BE edge regardless of the data, reporting the entire
   135	    # baseline as net signal.
   136	    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
   137	        f"low-BE edge should sit on the pre-loss level C0 = {y[-1]}, got {bg[-1]}"
   138	    )
   139	    assert np.all(np.isfinite(bg))
   140	    assert np.all(bg >= 0.0)
   141	
   142	    # Same anchor semantics for ascending input: the high-BE edge is x[-1]
   143	    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
   144	    assert np.isclose(bg_a[-1], y[0], rtol=1e-12)
   145	    # ...and the low-BE edge (index 0 when ascending) sits on C0, per above.
   146	    assert np.isclose(bg_a[0], y[-1], rtol=1e-12)
   147	
   148	
   149	def test_no_loss_signal_returns_flat_pre_loss_level():
   150	    """Degenerate input: no net loss signal accumulates at the high-BE edge
   151	    (bg[0] == 0 — counts are zero everywhere below the edge point).
   152	
   153	    Supersedes the 2026-07-04 Codex pin ``..._returns_unanchored_zeros``.
   154	    That pin asserted all-zeros, which was correct ONLY while the background
   155	    carried no constant term: with the F1 offset fix (2026-07-17) the honest
   156	    answer for a window containing no modellable loss signal is the flat
   157	    pre-loss level C0, not zero. Returning zeros would report the entire
   158	    baseline as net signal — the exact failure F1 fixes. The guard itself
   159	    still exists (no force-matching to the edge intensity, no divide-by-zero);
   160	    only its fallback VALUE changed from 0 to C0. Mirrored in the JS twin."""
   161	    x = np.array([291.0, 290.0, 289.0, 288.0])  # descending
   162	    y = np.array([100.0, 0.0, 0.0, 0.0])        # signal only at the edge itself
   163	    bg = tougaard_background(x, y)
   164	    assert np.array_equal(bg, np.zeros(4)), (
   165	        f"C0 is 0.0 here (low-BE edge counts are zero), so the flat pre-loss "
   166	        f"level IS zeros; got {bg}"
   167	    )
   168	
   169	
   170	def test_flat_window_yields_no_phantom_signal():
   171	    """F1 regression pin (2026-07-17): a flat, featureless window must yield
   172	    ~zero net counts everywhere.
   173	
   174	    Before the offset fix, K(0) = 0 forced the background to zero at the
   175	    low-BE edge regardless of the data, so a flat 500-count window produced a
   176	    background ramping 0 -> 500 and reported up to 500 counts of phantom
   177	    "signal" fabricated from a featureless baseline."""
   178	    x = np.linspace(740.0, 700.0, 200)   # descending, flat data
   179	    y = np.full_like(x, 500.0)
   180	    bg = tougaard_background(x, y)
   181	    net = y - bg
   182	    assert np.max(np.abs(net)) < 1e-6, (
   183	        f"flat window must leave ~zero net; net spans "
   184	        f"{net.min():.3f}..{net.max():.3f}"
   185	    )
   186	
   187	
   188	def test_background_tracks_low_be_baseline_on_wide_region():
   189	    """F1 regression pin (2026-07-17): on a wide 2p-like region sitting on a
   190	    large out-of-window inelastic baseline, the background must track that
   191	    baseline at the low-BE edge instead of diving to zero."""
   192	    x = np.linspace(740.0, 700.0, 600)   # descending
   193	    pk = (6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2)
   194	          + 3000.0 * np.exp(-0.5 * ((x - 724.5) / 1.9) ** 2))
   195	    baseline = 4000.0 + 3000.0 * np.cumsum(pk[::-1])[::-1] / np.sum(pk)
   196	    y = pk + baseline
   197	    bg = tougaard_background(x, y)
   198	    # low-BE edge is index -1 on this descending grid
   199	    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
   200	        f"low-BE edge dove to {bg[-1]:.1f} instead of tracking the "
   201	        f"{y[-1]:.1f}-count baseline"
   202	    )
   203	    assert np.isclose(bg[0], y[0], rtol=1e-12)
   204	
   205	
   206	def test_nonuniform_grid_uses_local_quadrature_weights():
   207	    """F2 regression pin (2026-07-17): the nonuniform-grid branch must weight
   208	    each term by its local energy spacing.
   209	
   210	    It previously used exact per-point separations but omitted the spacing
   211	    weights, silently applying uniform-grid quadrature inside the branch
   212	    written precisely BECAUSE the grid is not uniform (~24% error on a
   213	    genuinely nonuniform grid). np.gradient returns dx exactly on a uniform
   214	    grid, so the two branches must now agree to floating point -- the
   215	    uniformity test is an optimization, not a semantic fork."""
   216	    # Uniform grid, then the same grid perturbed below the uniformity
   217	    # tolerance so the nonuniform branch runs on near-identical data.
   218	    x = np.linspace(740.0, 700.0, 300)
   219	    y = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))
   220	    bg_uniform = tougaard_background(x, y)
   221	    x_jitter = x.copy()
   222	    x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
   223	    bg_nonuniform = tougaard_background(x_jitter, y)
   224	    assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
   225	        "uniform and nonuniform branches disagree on near-identical grids"
   226	    )
   227	
   228	    # Genuinely nonuniform grid vs an explicit spacing-weighted reference.
   229	    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
   230	                         np.linspace(720.0, 700.0, 400)])
   231	    ya = np.interp(xa[::-1], x[::-1], y[::-1])[::-1]
   232	    got = tougaard_background(xa, ya)
   233	
   234	    B_coef, C_coef = 2866.0, 1643.0
   235	    c0 = float(ya[-1])
   236	    net = ya - c0
   237	    w = np.abs(np.gradient(xa))
   238	    ref = np.zeros(len(xa))
   239	    for i in range(len(xa)):
   240	        T = np.abs(xa[i:] - xa[i])
   241	        ref[i] = float(np.sum((B_coef * T) / (C_coef + T * T) ** 2 * net[i:] * w[i:]))
   242	    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
   243	    assert np.allclose(got, ref, rtol=1e-9), (
   244	        "nonuniform branch does not match spacing-weighted quadrature"
   245	    )
   246	
   247	
   248	def test_short_input_returns_zeros():
   249	    """< 2 points: no background can be defined; must return zeros."""
   250	    assert np.array_equal(
   251	        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
   252	    )
   253	    assert tougaard_background(np.array([]), np.array([])).size == 0

exec
/bin/zsh -lc "nl -ba tests/js/tougaard_twin.test.js | sed -n '1,210p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	// Tougaard background — JS twin of fitting.py's tougaard_background.
     2	//
     3	// The function lives inline in templates/index.html; extract its source and
     4	// evaluate it so these tests exercise the exact shipped code. Pins the
     5	// 2026-07-04 fix (mirrored from the backend, see
     6	// tests/test_tougaard_background.py):
     7	//   1. Universal cross-section constant C = 1643 eV² (was shipped squared:
     8	//      1643*1643). Kernel K(T) = B·T/(C+T²)² peaks at sqrt(C/3) ≈ 23.4 eV.
     9	//      S. Tougaard, Surf. Interface Anal. 11, 453 (1988).
    10	//   2. Order-robustness: the one-sided loss sum needs a descending-BE grid;
    11	//      ascending input is normalized internally and flipped back.
    12	//   3. Amplitude anchored to the measured intensity at the HIGH-BE edge
    13	//      (the old "trailing endpoint" rescale was degenerate: K(0)=0 forced
    14	//      the zero-guard, multiplying by raw trailing counts instead).
    15	
    16	const { test } = require('node:test');
    17	const assert = require('node:assert');
    18	const fs = require('node:fs');
    19	const path = require('node:path');
    20	
    21	const html = fs.readFileSync(
    22	  path.join(__dirname, '../../templates/index.html'), 'utf8');
    23	const match = html.match(/function tougaardBackground\([\s\S]*?\n\}/);
    24	assert.ok(match, 'tougaardBackground not found in templates/index.html');
    25	const tougaardBackground = eval('(' + match[0] + ')');
    26	
    27	const avgMatch = html.match(/function _applyEndpointAveraging\([\s\S]*?\n\}/);
    28	assert.ok(avgMatch, '_applyEndpointAveraging not found in templates/index.html');
    29	const _applyEndpointAveraging = eval('(' + avgMatch[0] + ')');
    30	
    31	function syntheticSpectrum() {
    32	  // Same C 1s-like region as the Python tests: descending BE, dx = 0.1 eV.
    33	  const be = [], intensity = [];
    34	  for (let i = 0; i <= 150; i++) {
    35	    const x = 295.0 - 0.1 * i;
    36	    be.push(x);
    37	    intensity.push(
    38	      100.0
    39	      + 5000.0 * Math.exp(-0.5 * Math.pow((x - 287.0) / 0.8, 2))
    40	      + 400.0 / (1.0 + Math.exp(-(287.0 - x)))
    41	    );
    42	  }
    43	  return { be, intensity };
    44	}
    45	
    46	test('loss-kernel response peaks ~23.4 eV above a delta-like peak', () => {
    47	  const n = 1001;
    48	  const be = [], intensity = [];
    49	  for (let i = 0; i < n; i++) {
    50	    be.push(100.0 - 0.1 * i);      // descending 100 → 0 eV
    51	    intensity.push(1e-9);
    52	  }
    53	  // A high-BE step is required since the F1 offset fix (2026-07-17): the
    54	  // fitted amplitude is proportional to the measured rise across the window
    55	  // (high-BE edge minus the low-BE pre-loss level), so a perfectly flat
    56	  // pedestal has no loss intensity to model and yields a flat background with
    57	  // no kernel shape to inspect. Mirrors the Python twin test.
    58	  intensity[0] = 2e-9;
    59	  const spikeIdx = 800;            // be = 20.0 eV
    60	  intensity[spikeIdx] = 1e6;
    61	
    62	  const bg = tougaardBackground(be, intensity);
    63	
    64	  let maxV = -Infinity, maxX = NaN;
    65	  for (let i = 0; i < spikeIdx; i++) {   // high-BE side: traces K(be − 20)
    66	    if (bg[i] > maxV) { maxV = bg[i]; maxX = be[i]; }
    67	  }
    68	  const expected = 20.0 + Math.sqrt(1643.0 / 3.0);  // ≈ 43.4 eV
    69	  assert.ok(Math.abs(maxX - expected) <= 0.25,
    70	    `kernel response peaks at ${maxX.toFixed(2)} eV, expected ~${expected.toFixed(2)}; ` +
    71	    'a peak near 100 eV means the squared constant (1643*1643) is back');
    72	});
    73	
    74	test('ascending and descending BE input give the identical background', () => {
    75	  const { be, intensity } = syntheticSpectrum();
    76	  const bgDesc = tougaardBackground(be, intensity);
    77	  const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
    78	  bgAsc.reverse();
    79	  for (let i = 0; i < be.length; i++) {
    80	    assert.strictEqual(bgDesc[i], bgAsc[i],
    81	      `order-dependent output at index ${i}: ${bgDesc[i]} vs ${bgAsc[i]}`);
    82	  }
    83	});
    84	
    85	test('background meets the data at BOTH edges (high-BE anchor, low-BE C0)', () => {
    86	  const { be, intensity } = syntheticSpectrum();
    87	  const bg = tougaardBackground(be, intensity);
    88	  const rel = Math.abs(bg[0] - intensity[0]) / intensity[0];
    89	  assert.ok(rel < 1e-12,
    90	    `high-BE-edge anchor broken: bg[0] = ${bg[0]}, data = ${intensity[0]}`);
    91	  // Since the F1 offset fix (2026-07-17) the low-BE edge carries the pre-loss
    92	  // constant C0, NOT zero. K(0)=0 still kills the LOSS integral there, so the
    93	  // background equals C0 exactly. Asserting 0 pinned the bug: it forced the
    94	  // background to dive to zero regardless of the data.
    95	  const last = bg.length - 1;
    96	  const relLow = Math.abs(bg[last] - intensity[last]) / intensity[last];
    97	  assert.ok(relLow < 1e-12,
    98	    `low-BE edge should sit on C0 = ${intensity[last]}, got ${bg[last]}`);
    99	});
   100	
   101	test('flat window yields no phantom signal (F1 regression pin)', () => {
   102	  const be = [], intensity = [];
   103	  for (let i = 0; i < 200; i++) { be.push(740.0 - 40.0 * i / 199); intensity.push(500.0); }
   104	  const bg = tougaardBackground(be, intensity);
   105	  for (let i = 0; i < bg.length; i++) {
   106	    assert.ok(Math.abs(intensity[i] - bg[i]) < 1e-6,
   107	      `flat window must leave ~zero net; net ${intensity[i] - bg[i]} at ${i}`);
   108	  }
   109	});
   110	
   111	test('agrees with the backend implementation (fitting.py) on the same spectrum', () => {
   112	  // Expected values regenerated against the backend on 2026-07-17 after the
   113	  // F1 (pre-loss constant C0) + F2 (local quadrature weights) fixes:
   114	  //   venv/bin/python - <<'EOF'
   115	  //   import numpy as np; from fitting import tougaard_background
   116	  //   x = np.linspace(295.0, 280.0, 151)
   117	  //   y = (100.0 + 5000.0*np.exp(-0.5*((x-287.0)/0.8)**2)
   118	  //        + 400.0/(1.0+np.exp(-(287.0-x))))
   119	  //   bg = tougaard_background(x, y)
   120	  //   print([float(bg[i]) for i in (0, 30, 75, 110, 149, 150)])
   121	  //   EOF
   122	  // Regenerate with that snippet if the backend numerics change for a
   123	  // reviewed reason. Tolerance 1e-9 relative: np.convolve vs the JS loop
   124	  // differ only by floating-point summation order.
   125	  const expected = {
   126	    0: 100.13414005218658,
   127	    30: 219.3991381848062,
   128	    75: 461.76541491579644,
   129	    110: 499.7312788702072,
   130	    149: 499.6355795222399,
   131	    150: 499.6355795222399,
   132	  };
   133	  const { be, intensity } = syntheticSpectrum();
   134	  const bg = tougaardBackground(be, intensity);
   135	  for (const [idx, want] of Object.entries(expected)) {
   136	    const got = bg[Number(idx)];
   137	    const tol = want === 0 ? 1e-15 : Math.abs(want) * 1e-9;
   138	    assert.ok(Math.abs(got - want) <= tol,
   139	      `backend/frontend disagree at index ${idx}: js ${got} vs python ${want}`);
   140	  }
   141	});
   142	
   143	// --- Codex review finding (2026-07-04, both runs, MAJOR): the shipped
   144	// caller computeBackgroundCore passed RAW intensity to tougaardBackground
   145	// while every backend caller applies endpoint averaging first. With the
   146	// high-BE-edge anchor, averaging directly sets the anchor amplitude, so
   147	// the caller contract — not just the function — must match the backend
   148	// (fitting.py run_fit / compute_background_only both do
   149	// tougaard_background(x, _apply_endpoint_averaging(y, n))).
   150	test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
   151	  const coreMatch = html.match(/function computeBackgroundCore\([\s\S]*?\n\}/);
   152	  assert.ok(coreMatch, 'computeBackgroundCore not found in templates/index.html');
   153	  // Stubs for background types this test never routes to; the eval'd
   154	  // function closes over this scope, so these names resolve at call time.
   155	  const manualAnchorBackground = () => { throw new Error('unexpected route: manual'); };
   156	  const shirleyBackground = () => { throw new Error('unexpected route: shirley'); };
   157	  const smartBackground = () => { throw new Error('unexpected route: smart'); };
   158	  const smartExperimentalBackground = () => { throw new Error('unexpected route: smart_exp'); };
   159	  const shirleyLinearBackground = () => { throw new Error('unexpected route: shirley_linear'); };
   160	  const linearBackground = () => { throw new Error('unexpected route: linear'); };
   161	  const computeBackgroundCore = eval('(' + coreMatch[0] + ')');
   162	
   163	  // Descending grid with an outlier at the high-BE edge: raw vs 3-point
   164	  // averaged anchors differ by construction (Codex's concrete scenario).
   165	  const n = 21;
   166	  const be = [], intensity = [];
   167	  for (let i = 0; i < n; i++) { be.push(292.0 - 0.5 * i); intensity.push(100); }
   168	  intensity[0] = 10000;   // high-BE outlier
   169	  intensity[10] = 4000;   // a peak so the correlation is non-trivial
   170	
   171	  const nAvg = 3;
   172	  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
   173	
   174	  // Branch 1: bg window covers the data (main sliced path)
   175	  const mainOut = computeBackgroundCore(be, intensity, {
   176	    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
   177	    bgStart: '292', bgEnd: '282',
   178	  });
   179	  // Branch 2: bg window misses the data entirely (fallback full-range path)
   180	  const fallbackOut = computeBackgroundCore(be, intensity, {
   181	    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
   182	    bgStart: '900', bgEnd: '905',
   183	  });
   184	
   185	  for (const [label, out] of [['main', mainOut], ['fallback', fallbackOut]]) {
   186	    for (let i = 0; i < n; i++) {
   187	      assert.strictEqual(out[i], expected[i],
   188	        `${label} branch: caller bypasses endpoint averaging at index ${i}: ` +
   189	        `${out[i]} vs averaged ${expected[i]}`);
   190	    }
   191	  }
   192	});

exec
/bin/zsh -lc 'git show 3d9ff54''^:fitting.py | rg -n "tougaard_background'"\\(|_apply_endpoint_averaging\\(.*endpoint_avg|elif bg_method == \\\"tougaard\\\"|elif method == \\\"tougaard\\\"\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-AtAd0HOk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-lig2XV4F' (errno=Operation not permitted)
508:def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
994:        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
996:        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
1001:    elif bg_method == "tougaard":
1002:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
1232:        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
1234:        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
1239:    elif method == "tougaard":
1240:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))

exec
/bin/zsh -lc 'git show 3d9ff54''^:tests/test_tougaard_background.py | nl -ba | sed -n '"'50,150p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Tommshan' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DmUAJ6bd' (errno=Operation not permitted)
    50	    return x, y
    51	
    52	
    53	def test_kernel_peak_near_sqrt_c_over_3():
    54	    """The loss-kernel response to a delta-like peak must peak ~23.4 eV
    55	    above the peak (sqrt(C/3) with C = 1643 eV²), not ~949 eV.
    56	
    57	    A spike at x0 on a descending grid produces bg(x) ∝ K(x − x0) on the
    58	    high-BE side, so the argmax of the background directly locates the
    59	    kernel maximum.
    60	    """
    61	    x = np.linspace(100.0, 0.0, 1001)  # descending, dx = 0.1 eV
    62	    y = np.full_like(x, 1e-9)  # tiny pedestal keeps the amplitude anchor finite
    63	    spike_idx = 800  # x = 20.0 eV
    64	    y[spike_idx] = 1.0e6
    65	
    66	    bg = tougaard_background(x, y)
    67	
    68	    high_be_side = slice(0, spike_idx)  # x > 20 eV: traces K(x − 20)
    69	    peak_x = x[high_be_side][np.argmax(bg[high_be_side])]
    70	    expected = 20.0 + np.sqrt(1643.0 / 3.0)  # 20 + 23.402...
    71	    assert abs(peak_x - expected) <= 0.25, (
    72	        f"kernel response peaks at x = {peak_x:.2f} eV; expected "
    73	        f"{expected:.2f} eV (spike at 20.0 + sqrt(C/3) ≈ 23.4 eV). "
    74	        f"A peak near x = 100 means the squared constant (C = 1643²) is back."
    75	    )
    76	
    77	
    78	def test_ascending_and_descending_input_agree_exactly():
    79	    """The same spectrum fed in ascending vs descending BE order must give
    80	    the identical background (element-wise, after re-reversal)."""
    81	    x_d, y_d = _synthetic_spectrum(descending=True)
    82	    x_a, y_a = _synthetic_spectrum(descending=False)
    83	
    84	    bg_d = tougaard_background(x_d, y_d)
    85	    bg_a = tougaard_background(x_a, y_a)
    86	
    87	    assert np.array_equal(bg_d, bg_a[::-1]), (
    88	        f"order-dependent output: max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
    89	    )
    90	
    91	
    92	def test_ascending_descending_parity_on_nonuniform_grid():
    93	    """Order-robustness must also hold on the non-uniform-grid code path
    94	    (which uses the exact per-point separation loop, not the convolution)."""
    95	    # Deterministic, mildly non-uniform descending grid
    96	    steps = 0.08 + 0.04 * np.sin(np.arange(120))
    97	    x_d = 295.0 - np.concatenate(([0.0], np.cumsum(steps)))
    98	    y_d = 100.0 + 4000.0 * np.exp(-0.5 * ((x_d - 290.0) / 1.0) ** 2)
    99	
   100	    bg_d = tougaard_background(x_d, y_d)
   101	    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
   102	
   103	    assert np.array_equal(bg_d, bg_a[::-1]), (
   104	        f"non-uniform grid is order-dependent: "
   105	        f"max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
   106	    )
   107	
   108	
   109	def test_background_anchored_at_high_be_edge():
   110	    """The background must equal the measured intensity at the high-BE edge
   111	    of the window (practical Tougaard criterion: the universal cross-section
   112	    amplitude is scaled so the background meets the data above the peak),
   113	    and must vanish at the low-BE edge (no in-window emitters below it)."""
   114	    x, y = _synthetic_spectrum(descending=True)
   115	    bg = tougaard_background(x, y)
   116	
   117	    # x[0] is the high-BE edge on this descending grid
   118	    assert np.isclose(bg[0], y[0], rtol=1e-12), (
   119	        f"high-BE-edge anchor broken: bg[0] = {bg[0]}, data = {y[0]}"
   120	    )
   121	    assert bg[-1] == 0.0, f"low-BE edge should carry zero loss background, got {bg[-1]}"
   122	    assert np.all(np.isfinite(bg))
   123	    assert np.all(bg >= 0.0)
   124	
   125	    # Same anchor semantics for ascending input: the high-BE edge is x[-1]
   126	    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
   127	    assert np.isclose(bg_a[-1], y[0], rtol=1e-12)
   128	    assert bg_a[0] == 0.0
   129	
   130	
   131	def test_no_loss_signal_returns_unanchored_zeros():
   132	    """Codex review pin (2026-07-04, run A MINOR): when no net loss signal
   133	    accumulates at the high-BE edge (bg[0] == 0 — e.g. counts are zero
   134	    everywhere below the edge point), the background is returned UNANCHORED
   135	    (all zeros), NOT force-matched to the edge intensity. Documented
   136	    degenerate-input fallback, mirrored in the JS twin's ``|| 1`` guard."""
   137	    x = np.array([291.0, 290.0, 289.0, 288.0])  # descending
   138	    y = np.array([100.0, 0.0, 0.0, 0.0])        # signal only at the edge itself
   139	    bg = tougaard_background(x, y)
   140	    assert np.array_equal(bg, np.zeros(4)), f"expected unanchored zeros, got {bg}"
   141	
   142	
   143	def test_short_input_returns_zeros():
   144	    """< 2 points: no background can be defined; must return zeros."""
   145	    assert np.array_equal(
   146	        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
   147	    )
   148	    assert tougaard_background(np.array([]), np.array([])).size == 0

exec
/bin/zsh -lc 'git show 3d9ff54''^:templates/index.html | rg -n "tougaardBackground'"\\(|function computeBackgroundCore|_applyEndpointAveraging\\(.*nAvg|if \\(type === 'tougaard'\\)\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2iLHOaEY' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-C4wFjbJZ' (errno=Operation not permitted)
4136:function tougaardBackground(be, intensity) {
4174:function _applyEndpointAveraging(intensity, nAvg) {
4270:function computeBackgroundCore(be, intensity, settings) {
4292:    const avgIn = _applyEndpointAveraging(intensity, nAvg);
4301:    if (type === 'tougaard') return tougaardBackground(be, avgIn);
4314:  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
4315:  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
4322:  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));

codex
I found stale Tougaard code in tracked archival/static HTML copies (`templates/index.html.pre-audit`, `xps-fitting-tool.html`), but the active reviewed frontend is `templates/index.html`. I’m doing a narrower fixture-oriented grep now so I don’t conflate those stale copies with saved-fit numeric pins.
exec
/bin/zsh -lc "rg -n -i \"tougaard\" tests tests/autofit docs/autofit/inventory scripts --glob '"'!**/__pycache__/**'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/test_tougaard_background.py:1:"""Tougaard universal-cross-section background — correctness pins.
tests/test_tougaard_background.py:10:   ~20 eV XPS window the shipped "Tougaard" background was essentially
tests/test_tougaard_background.py:11:   flat/zero.  Reference: S. Tougaard, Surf. Interface Anal. 11, 453
tests/test_tougaard_background.py:27:   window (the standard practical Tougaard criterion: B is effectively
tests/test_tougaard_background.py:30:No pre-existing test or fixture pinned the old (wrong) Tougaard output
tests/test_tougaard_background.py:37:from fitting import tougaard_background
tests/test_tougaard_background.py:74:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:92:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:93:    bg_a = tougaard_background(x_a, y_a)
tests/test_tougaard_background.py:108:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:109:    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
tests/test_tougaard_background.py:119:    of the window (practical Tougaard criterion: the universal cross-section
tests/test_tougaard_background.py:123:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:132:    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
tests/test_tougaard_background.py:143:    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
tests/test_tougaard_background.py:163:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:180:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:197:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:220:    bg_uniform = tougaard_background(x, y)
tests/test_tougaard_background.py:223:    bg_nonuniform = tougaard_background(x_jitter, y)
tests/test_tougaard_background.py:232:    got = tougaard_background(xa, ya)
tests/test_tougaard_background.py:251:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
tests/test_tougaard_background.py:253:    assert tougaard_background(np.array([]), np.array([])).size == 0
tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",
tests/js/batch_propagation.test.js:42:  const src = ui({ bgType: 'tougaard', bgStart: '690', bgEnd: '750', shirleyIter: '9' });
tests/js/batch_propagation.test.js:45:  assert.strictEqual(out.bgType, 'tougaard');
tests/js/tougaard_twin.test.js:1:// Tougaard background — JS twin of fitting.py's tougaard_background.
tests/js/tougaard_twin.test.js:6:// tests/test_tougaard_background.py):
tests/js/tougaard_twin.test.js:9://      S. Tougaard, Surf. Interface Anal. 11, 453 (1988).
tests/js/tougaard_twin.test.js:23:const match = html.match(/function tougaardBackground\([\s\S]*?\n\}/);
tests/js/tougaard_twin.test.js:24:assert.ok(match, 'tougaardBackground not found in templates/index.html');
tests/js/tougaard_twin.test.js:25:const tougaardBackground = eval('(' + match[0] + ')');
tests/js/tougaard_twin.test.js:62:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:76:  const bgDesc = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:77:  const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
tests/js/tougaard_twin.test.js:87:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:104:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:115:  //   import numpy as np; from fitting import tougaard_background
tests/js/tougaard_twin.test.js:119:  //   bg = tougaard_background(x, y)
tests/js/tougaard_twin.test.js:134:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:144:// caller computeBackgroundCore passed RAW intensity to tougaardBackground
tests/js/tougaard_twin.test.js:149:// tougaard_background(x, _apply_endpoint_averaging(y, n))).
tests/js/tougaard_twin.test.js:150:test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
tests/js/tougaard_twin.test.js:172:  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
tests/js/tougaard_twin.test.js:176:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/js/tougaard_twin.test.js:181:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",

exec
/bin/zsh -lc "rg -n -i \"tougaard\" -g '*.json' -g '*.proj.json' -g '*.spec.json' -g '*.proj.zip' -g '*.zip' . --glob '"'!node_modules/**'"' --glob '"'!venv/**'"' --glob '"'!__pycache__/**'"'" in /Users/skyefortier/xps-verify
 exited 1 in 0ms:
exec
/bin/zsh -lc "rg --files -g '*.json' -g '*.proj.json' -g '*.proj.zip' -g '*.spec.json' -g '*.zip' | sed -n '1,240p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
data/xps/elements-machine.provenance.json
data/xps/schema.json
data/xps/elements-actinides.json
data/xps/elements-machine.skipped.json
data/xps/elements-machine.json
data/xps/legacy/chemical-states.json
data/xps/legacy/schema.json
data/xps/legacy/corrections.json
data/xps/legacy/survey-lines.json
data/xps/auger-lines.json
data/xps/elements-lanthanides.json
data/xps/elements-main.json
data/xps/sources.json
data/xps/fit-physics.json
docs/autofit/inventory/reference_fits_inventory.json
docs/autofit/inventory/replicate_noise_survey.json
docs/autofit/inventory/acquisition_exhaustion.json
tests/fixtures/curated_records_snapshot.json
tests/fixtures/xps_legacy_snapshot.json
tests/fixtures/machine_records_snapshot.json
tests/autofit/fixtures/c1s_battery_expected.json
tests/autofit/fixtures/u4f_battery_expected.json
tests/autofit/fixtures/b1s_battery_expected.json
tests/autofit/fixtures/example_cited_values.json
tests/autofit/fixtures/cl2p_battery_expected.json
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json
docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
docs/autofit/test_data/8-JT Graphite.proj.zip
docs/autofit/test_data/UCl4_on_graphite.proj.zip
docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
docs/autofit/test_data/Cl2p_projfit_test.proj.zip
docs/autofit/test_data/B4C-UCl4.proj.zip

exec
/bin/zsh -lc "rg -n -i \"tougaard|bgIntensity|background|bg_type|bgType\" docs/autofit/inventory scripts tests tests/autofit -g '*.json' -g '*.py' -g '*.md' -g '*.txt' --glob '"'!**/__pycache__/**'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/test_tougaard_background.py:1:"""Tougaard universal-cross-section background — correctness pins.
tests/test_tougaard_background.py:10:   ~20 eV XPS window the shipped "Tougaard" background was essentially
tests/test_tougaard_background.py:11:   flat/zero.  Reference: S. Tougaard, Surf. Interface Anal. 11, 453
tests/test_tougaard_background.py:16:   binding-energy grid; ascending input silently produced a background
tests/test_tougaard_background.py:20:   shirley_background's ascending normalization.
tests/test_tougaard_background.py:23:   trailing background sample identically zero, so the zero-guard always
tests/test_tougaard_background.py:26:   the background to the measured intensity at the HIGH-BE edge of the
tests/test_tougaard_background.py:27:   window (the standard practical Tougaard criterion: B is effectively
tests/test_tougaard_background.py:28:   fitted so the background meets the spectrum above the peak).
tests/test_tougaard_background.py:30:No pre-existing test or fixture pinned the old (wrong) Tougaard output
tests/test_tougaard_background.py:37:from fitting import tougaard_background
tests/test_tougaard_background.py:58:    high-BE side, so the argmax of the background directly locates the
tests/test_tougaard_background.py:66:    # intensity to model, so the honest background is flat and carries no
tests/test_tougaard_background.py:68:    # the background shape it scales is still the pure kernel response.
tests/test_tougaard_background.py:74:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:88:    the identical background (element-wise, after re-reversal)."""
tests/test_tougaard_background.py:92:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:93:    bg_a = tougaard_background(x_a, y_a)
tests/test_tougaard_background.py:108:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:109:    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
tests/test_tougaard_background.py:117:def test_background_anchored_at_high_be_edge():
tests/test_tougaard_background.py:118:    """The background must equal the measured intensity at the high-BE edge
tests/test_tougaard_background.py:119:    of the window (practical Tougaard criterion: the universal cross-section
tests/test_tougaard_background.py:120:    amplitude is scaled so the background meets the data above the peak),
tests/test_tougaard_background.py:123:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:131:    # still makes the LOSS integral vanish there, so the background equals C0
tests/test_tougaard_background.py:132:    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
tests/test_tougaard_background.py:133:    # Asserting 0.0 here was pinning the bug: it forced the background to dive
tests/test_tougaard_background.py:143:    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
tests/test_tougaard_background.py:154:    That pin asserted all-zeros, which was correct ONLY while the background
tests/test_tougaard_background.py:163:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:174:    Before the offset fix, K(0) = 0 forced the background to zero at the
tests/test_tougaard_background.py:176:    background ramping 0 -> 500 and reported up to 500 counts of phantom
tests/test_tougaard_background.py:180:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:188:def test_background_tracks_low_be_baseline_on_wide_region():
tests/test_tougaard_background.py:190:    large out-of-window inelastic baseline, the background must track that
tests/test_tougaard_background.py:197:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:220:    bg_uniform = tougaard_background(x, y)
tests/test_tougaard_background.py:223:    bg_nonuniform = tougaard_background(x_jitter, y)
tests/test_tougaard_background.py:232:    got = tougaard_background(xa, ya)
tests/test_tougaard_background.py:249:    """< 2 points: no background can be defined; must return zeros."""
tests/test_tougaard_background.py:251:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
tests/test_tougaard_background.py:253:    assert tougaard_background(np.array([]), np.array([])).size == 0
tests/autofit/test_stage2_rereview_findings.py:41:    y_fit = fit.lmfit_result.best_fit + fit.background
tests/test_browser_overlay_zip_roundtrip.py:251:            "ui": {"bgType": "shirley", "bgStart": "", "bgEnd": "", "shirleyIter": "5",
tests/autofit/test_browser_schema_roundtrip.py:293:            "ui": {"bgType": "shirley", "bgStart": "", "bgEnd": "", "shirleyIter": "5",
scripts/run_bayesian_real_validation.py:23:  venv/bin/python scripts/run_bayesian_real_validation.py           # full battery (background-scale)
tests/autofit/test_stage2_completeness.py:53:    y_fit = rep.primary_fit.lmfit_result.best_fit + rep.primary_fit.background
tests/autofit/test_stage2_completeness.py:289:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:296:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:313:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:321:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:365:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:372:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:392:    from autofit.grammar import BackgroundType
tests/autofit/test_stage2_completeness.py:397:    dom = e2.detect_out_of_grammar_dominants(x, y, e2._compute_background(
tests/autofit/test_stage2_completeness.py:398:        x, y, BackgroundType.LINEAR), [], {})
tests/autofit/test_stage2_completeness.py:405:        pool, BackgroundType.LINEAR, step_ev=0.05)
tests/autofit/test_cl2p_freewidth.py:27:    BackgroundType,
tests/autofit/test_cl2p_freewidth.py:136:        name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:148:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:159:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:177:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:190:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:203:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
scripts/run_stress_battery.py:127:    rec = _base(case, off, "least_squares", {"background_method":
tests/test_api_analyze_progress.py:14:(instant 400s, unchanged), then spawns a background THREAD (not a
tests/autofit/test_c1s_parity_gate.py:54:from fitting import shirley_background
tests/autofit/test_c1s_parity_gate.py:171:    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(
tests/autofit/test_candidate_pool_wiring.py:184:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool_wiring.py:190:                              bg=BackgroundType.SHIRLEY)])
tests/autofit/test_resolver.py:6:    BackgroundType,
tests/autofit/test_resolver.py:120:            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:122:            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
tests/autofit/test_fit_full_window_option.py:37:from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape
tests/autofit/test_fit_full_window_option.py:47:    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))
tests/autofit/test_criteria.py:15:    BackgroundType,
tests/autofit/test_criteria.py:31:                           background=BackgroundType.SHIRLEY,
tests/autofit/test_sparse_map.py:15:    BackgroundType,
tests/autofit/test_sparse_map.py:34:    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:160:    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:162:    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
tests/test_api_analyze.py:104:        "options": {"background_method": "linear"},
tests/autofit/test_max_entropy.py:69:    """Iterative deconvolution inherently amplifies background noise (~10×
scripts/calibrate_cwt_detector.py:13:   linear-drift / sigmoid-step backgrounds x counts 100..50000 x grid
tests/autofit/test_candidate_pool.py:152:    peakless step must seed NOTHING.  Backgrounds are ENGINE-computed
tests/autofit/test_candidate_pool.py:153:    (Shirley) as in production — a zeros background makes the height
tests/autofit/test_candidate_pool.py:158:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:159:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool.py:342:    background) stay OUT of the pool payload — overcomplete does not mean
tests/autofit/test_candidate_pool.py:343:    noise-transcript.  Background as the engine supplies it (its detection
tests/autofit/test_candidate_pool.py:344:    background, which absorbs the flat baseline)."""
tests/autofit/test_candidate_pool.py:345:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:346:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_engine_doublet.py:12:    BackgroundType,
tests/autofit/test_engine_doublet.py:36:    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
tests/autofit/test_engine_doublet.py:124:    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
tests/autofit/test_engine_doublet.py:134:        name="joint", background=BackgroundType.SHIRLEY,
tests/autofit/test_u4f_parity_battery.py:19:# Bounded by background-anchor drift / LACX FP wobble — measured and
tests/autofit/test_bayesian_method.py:16:    BackgroundType,
tests/autofit/test_bayesian_method.py:35:    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:37:    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:40:    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:254:    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:257:    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
tests/autofit/test_candidate_pool_real_gate.py:101:    det_bg = eng._compute_background(x, y, cands[0].background)
scripts/summarize_stress_battery.py:226:        "2. **Endpoint-anchored linear background + Lorentzian tails set a "
scripts/summarize_stress_battery.py:231:        "land below the truth-under-wrong-background score by bending "
scripts/summarize_stress_battery.py:234:        "absolute χ²-target criteria are miscalibrated whenever background "
scripts/summarize_stress_battery.py:236:        "the same integral background well (control case χ²ᵣ 1.24). Feeds "
scripts/summarize_stress_battery.py:299:        "tails, background curvature — those honesty cases surface via "
tests/autofit/test_stress_honesty.py:62:        options={"background_method": "linear"})
tests/test_mixed_ds_lacx_e2e.py:54:    background_method='none',
tests/test_browser_cc_overlay_repaint.py:108:# column reads as background (a handful). Returns {blue, white, sampled}.
tests/autofit/stress_cases.py:9:mis-specified-weights question separately).  Backgrounds are kept EXACTLY
tests/autofit/stress_cases.py:10:expressible (linear) in every regime except the background-mismatch regime,
tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
tests/autofit/stress_cases.py:33:the true baseline at the ROI edges — and the engine's LINEAR background is
tests/autofit/stress_cases.py:35:the engine-background χ²ᵣ is therefore not 1: measured 0.96 with the true
tests/autofit/stress_cases.py:36:baseline vs 34 with the engine background at height 90000 (≈2 at 9000 —
tests/autofit/stress_cases.py:38:This is the REALISTIC background-subtraction problem, kept on purpose:
tests/autofit/stress_cases.py:52:    BackgroundType,
tests/autofit/stress_cases.py:80:    bg: str = "linear"                       # generator background family
tests/autofit/stress_cases.py:95:    """Integral (Shirley-shaped) background: proportional to the signal area
tests/autofit/stress_cases.py:113:def _cand(name, slots, bg=BackgroundType.LINEAR):
tests/autofit/stress_cases.py:114:    return CandidateModel(name=name, background=bg, slots=tuple(slots))
tests/autofit/stress_cases.py:132:                   bg=BackgroundType.LINEAR):
tests/autofit/stress_cases.py:323:# Regime 6 — background mismatch (Shirley-shaped truth, linear-only fits)
tests/autofit/stress_cases.py:364:    endpoint-anchored linear background.)
tests/autofit/stress_cases.py:418:        notes="integral background fit with a straight line — the mismatch "
tests/autofit/stress_cases.py:425:    The engine's iterative Shirley should absorb the integral background."""
tests/autofit/stress_cases.py:431:    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
tests/autofit/stress_cases.py:440:        notes="control: matched background family",
tests/autofit/stress_cases.py:488:        # background mismatch + control
tests/autofit/test_cwt_detector.py:112:    linear backgrounds cancel identically — drift must produce nothing."""
tests/test_browser_batch_roi.py:3:The bug: runPropagation() copied only the background fields into each target's
tests/test_browser_batch_roi.py:4:UI, omitting the ROI, so batch fit changed the background but left every target's
tests/autofit/test_methods_seam.py:51:    res = m.run(x, y, peak_specs=specs, options={"background_method": "shirley"})
tests/autofit/test_c1s_parity_battery.py:13:   fitting.py's lineshapes + run_fit's background reconstruction reproduces
tests/autofit/test_preseed_dominants.py:62:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:85:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:104:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:165:                                 BackgroundType)
tests/autofit/test_preseed_dominants.py:177:    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
tests/autofit/test_preseed_dominants.py:199:    from autofit.grammar import CandidateModel, BackgroundType
tests/autofit/test_preseed_dominants.py:200:    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
tests/autofit/test_preseed_dominants.py:256:                                 BackgroundType)
tests/autofit/test_preseed_dominants.py:262:    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
tests/autofit/test_preseed_dominants.py:290:    y_fit = (base.primary_fit.lmfit_result.best_fit + base.primary_fit.background)
tests/autofit/test_preseed_dominants.py:298:    bg = eng._compute_background(x, y, aug_model.background)
tests/autofit/test_preseed_dominants.py:368:    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:382:    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:434:             + base_report.primary_fit.background)
tests/test_browser_identify_frame.py:220:        bg: getComputedStyle(document.getElementById('ref-identify-popover')).backgroundColor })""")
tests/test_browser_identify_frame.py:230:            bg: (()=>{const p=document.getElementById('ref-identify-popover');return p?getComputedStyle(p).backgroundColor:null;})() })""")
tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",
tests/autofit/battery_common.py:25:# - eval_tol: bounded below by BACKGROUND-ANCHOR DRIFT — ui bg-start/end
tests/autofit/battery_common.py:28:#   'smart' backgrounds that perturbs the recomputed background by
tests/autofit/battery_common.py:30:#   deviation profile exactly matching the background, not the shapes).
tests/test_browser_find_peaks_full_window.py:12:background/fit-curve rendering to ``state.fitResult``'s own frozen
tests/test_browser_find_peaks_full_window.py:13:``be``/``bgIntensity`` arrays once ANY fit exists (a prior manual Run
tests/test_browser_find_peaks_full_window.py:16:left the chart showing background/fit cropped to whatever OLD, possibly
tests/test_browser_find_peaks_full_window.py:24:``computeBackground()``), which correctly spans whatever the CURRENT
tests/test_browser_find_peaks_full_window.py:150:            be: narrowBE, bgIntensity: narrowBG, bgSubtracted: narrowSub,
tests/test_browser_find_peaks_full_window.py:209:def _background_span(pg):
tests/test_browser_find_peaks_full_window.py:211:        const bg = state.chart.data.datasets.find(d => /background/i.test(d.label || ''));
tests/test_browser_find_peaks_full_window.py:229:        before = _background_span(pg)
tests/test_browser_find_peaks_full_window.py:235:        after = _background_span(pg)
tests/test_browser_find_peaks_full_window.py:250:def test_checkbox_on_extends_fit_and_background_to_the_full_window(browser, server):
tests/test_browser_find_peaks_full_window.py:251:    """The actual fix: checked must make the background/fit-curve span
tests/test_browser_find_peaks_full_window.py:268:        before = _background_span(pg)
tests/test_browser_find_peaks_full_window.py:281:        after = _background_span(pg)
tests/test_browser_find_peaks_full_window.py:284:            f"checked must extend the background/fit to the full ROI: {after}")
tests/test_browser_find_peaks_full_window.py:314:    run on a tab) must also render peaks + background across the full
tests/test_browser_find_peaks_full_window.py:334:        after = _background_span(pg)
tests/autofit/test_preseed_dominants.py:62:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:85:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:104:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:165:                                 BackgroundType)
tests/autofit/test_preseed_dominants.py:177:    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
tests/autofit/test_preseed_dominants.py:199:    from autofit.grammar import CandidateModel, BackgroundType
tests/autofit/test_preseed_dominants.py:200:    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
tests/autofit/test_preseed_dominants.py:256:                                 BackgroundType)
tests/autofit/test_preseed_dominants.py:262:    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
tests/autofit/test_preseed_dominants.py:290:    y_fit = (base.primary_fit.lmfit_result.best_fit + base.primary_fit.background)
tests/autofit/test_preseed_dominants.py:298:    bg = eng._compute_background(x, y, aug_model.background)
tests/autofit/test_preseed_dominants.py:368:    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:382:    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:434:             + base_report.primary_fit.background)
tests/autofit/test_candidate_pool.py:152:    peakless step must seed NOTHING.  Backgrounds are ENGINE-computed
tests/autofit/test_candidate_pool.py:153:    (Shirley) as in production — a zeros background makes the height
tests/autofit/test_candidate_pool.py:158:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:159:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool.py:342:    background) stay OUT of the pool payload — overcomplete does not mean
tests/autofit/test_candidate_pool.py:343:    noise-transcript.  Background as the engine supplies it (its detection
tests/autofit/test_candidate_pool.py:344:    background, which absorbs the flat baseline)."""
tests/autofit/test_candidate_pool.py:345:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:346:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_c1s_parity_gate.py:54:from fitting import shirley_background
tests/autofit/test_c1s_parity_gate.py:171:    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(
tests/autofit/test_max_entropy.py:69:    """Iterative deconvolution inherently amplifies background noise (~10×
tests/autofit/test_cwt_detector.py:112:    linear backgrounds cancel identically — drift must produce nothing."""
tests/autofit/test_candidate_pool_real_gate.py:101:    det_bg = eng._compute_background(x, y, cands[0].background)
tests/autofit/test_stage2_rereview_findings.py:41:    y_fit = fit.lmfit_result.best_fit + fit.background
tests/autofit/battery_common.py:25:# - eval_tol: bounded below by BACKGROUND-ANCHOR DRIFT — ui bg-start/end
tests/autofit/battery_common.py:28:#   'smart' backgrounds that perturbs the recomputed background by
tests/autofit/battery_common.py:30:#   deviation profile exactly matching the background, not the shapes).
tests/autofit/test_criteria.py:15:    BackgroundType,
tests/autofit/test_criteria.py:31:                           background=BackgroundType.SHIRLEY,
tests/autofit/test_stage2_completeness.py:53:    y_fit = rep.primary_fit.lmfit_result.best_fit + rep.primary_fit.background
tests/autofit/test_stage2_completeness.py:289:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:296:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:313:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:321:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:365:    from autofit.grammar import (BackgroundType, CandidateModel,
tests/autofit/test_stage2_completeness.py:372:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:392:    from autofit.grammar import BackgroundType
tests/autofit/test_stage2_completeness.py:397:    dom = e2.detect_out_of_grammar_dominants(x, y, e2._compute_background(
tests/autofit/test_stage2_completeness.py:398:        x, y, BackgroundType.LINEAR), [], {})
tests/autofit/test_stage2_completeness.py:405:        pool, BackgroundType.LINEAR, step_ev=0.05)
tests/autofit/test_resolver.py:6:    BackgroundType,
tests/autofit/test_resolver.py:120:            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:122:            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
tests/autofit/test_c1s_parity_battery.py:13:   fitting.py's lineshapes + run_fit's background reconstruction reproduces
tests/autofit/test_candidate_pool_wiring.py:184:    from autofit.grammar import BackgroundType
tests/autofit/test_candidate_pool_wiring.py:190:                              bg=BackgroundType.SHIRLEY)])
tests/autofit/test_methods_seam.py:51:    res = m.run(x, y, peak_specs=specs, options={"background_method": "shirley"})
tests/autofit/test_stress_honesty.py:62:        options={"background_method": "linear"})
tests/autofit/test_bayesian_method.py:16:    BackgroundType,
tests/autofit/test_bayesian_method.py:35:    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:37:    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:40:    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:254:    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:257:    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
tests/autofit/test_browser_schema_roundtrip.py:293:            "ui": {"bgType": "shirley", "bgStart": "", "bgEnd": "", "shirleyIter": "5",
tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",
tests/autofit/stress_cases.py:9:mis-specified-weights question separately).  Backgrounds are kept EXACTLY
tests/autofit/stress_cases.py:10:expressible (linear) in every regime except the background-mismatch regime,
tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
tests/autofit/stress_cases.py:33:the true baseline at the ROI edges — and the engine's LINEAR background is
tests/autofit/stress_cases.py:35:the engine-background χ²ᵣ is therefore not 1: measured 0.96 with the true
tests/autofit/stress_cases.py:36:baseline vs 34 with the engine background at height 90000 (≈2 at 9000 —
tests/autofit/stress_cases.py:38:This is the REALISTIC background-subtraction problem, kept on purpose:
tests/autofit/stress_cases.py:52:    BackgroundType,
tests/autofit/stress_cases.py:80:    bg: str = "linear"                       # generator background family
tests/autofit/stress_cases.py:95:    """Integral (Shirley-shaped) background: proportional to the signal area
tests/autofit/stress_cases.py:113:def _cand(name, slots, bg=BackgroundType.LINEAR):
tests/autofit/stress_cases.py:114:    return CandidateModel(name=name, background=bg, slots=tuple(slots))
tests/autofit/stress_cases.py:132:                   bg=BackgroundType.LINEAR):
tests/autofit/stress_cases.py:323:# Regime 6 — background mismatch (Shirley-shaped truth, linear-only fits)
tests/autofit/stress_cases.py:364:    endpoint-anchored linear background.)
tests/autofit/stress_cases.py:418:        notes="integral background fit with a straight line — the mismatch "
tests/autofit/stress_cases.py:425:    The engine's iterative Shirley should absorb the integral background."""
tests/autofit/stress_cases.py:431:    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
tests/autofit/stress_cases.py:440:        notes="control: matched background family",
tests/autofit/stress_cases.py:488:        # background mismatch + control
tests/autofit/test_engine_doublet.py:12:    BackgroundType,
tests/autofit/test_engine_doublet.py:36:    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
tests/autofit/test_engine_doublet.py:124:    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
tests/autofit/test_engine_doublet.py:134:        name="joint", background=BackgroundType.SHIRLEY,
tests/autofit/test_sparse_map.py:15:    BackgroundType,
tests/autofit/test_sparse_map.py:34:    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:160:    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:162:    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
tests/autofit/test_u4f_parity_battery.py:19:# Bounded by background-anchor drift / LACX FP wobble — measured and
tests/autofit/test_cl2p_freewidth.py:27:    BackgroundType,
tests/autofit/test_cl2p_freewidth.py:136:        name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:148:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:159:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:177:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:190:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:203:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_fit_full_window_option.py:37:from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape
tests/autofit/test_fit_full_window_option.py:47:    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))

codex
The fixture grep did not find Tougaard numeric pins in JSON/proj-style saved data. The only active numeric Tougaard expectations are the two touched test files; the other Tougaard hits are citations, UI strings, or historical docs.
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text()\\nm=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s)\\nt=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\nns={\"np\":np}\\nexec(m.group(0)+\"\\\\n\"+t.group(0), ns)\\nf=ns[\"tougaard_background\"]\\nx=np.linspace(740.0,700.0,200); y=np.full_like(x,500.0); bg=f(x,y); print(\"flat_max_net\", float(np.max(np.abs(y-bg))), \"edges\", float(bg[0]), float(bg[-1]))\\nx2=np.linspace(10.0,0.0,11); y2=np.linspace(100.0,200.0,11); bg2=f(x2,y2); print(\"neg_scale_edges\", float(bg2[0]), float(bg2[-1]), \"min\", float(bg2.min()), \"max\", float(bg2.max())); print(\"neg_scale_bg\", np.array2string(bg2, precision=3))\\nx3=np.array([291.0,290.0,289.0,288.0]); y3=np.array([100.0,0.0,0.0,0.0]); print(\"guard_fixture\", f(x3,y3))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text()\\nm=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s)\\nt=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\nns={\"np\":np}\\nexec(m.group(0)+\"\\\\n\"+t.group(0), ns)\\nf=ns[\"tougaard_background\"]\\nx=np.linspace(295.0,280.0,151); y=100.0+5000.0*np.exp(-0.5*((x-287.0)/0.8)**2)+400.0/(1.0+np.exp(-(287.0-x))); bg=f(x,y)\\nfor i in [0,30,75,110,149,150]: print(i, repr(float(bg[i])))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text()\\nm=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s)\\nt=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\nns={\"np\":np}\\nexec(m.group(0)+\"\\\\n\"+t.group(0), ns)\\nf=ns[\"tougaard_background\"]\\nx=np.linspace(100.0,0.0,1001); y=np.full_like(x,1e-9); y[0]=2e-9; y[800]=1e6; bg=f(x,y); px=x[:800][np.argmax(bg[:800])]; print(\"peak_x\", float(px), \"expected\", float(20+np.sqrt(1643.0/3.0)))\\nx_bad=x.copy(); y_bad=y.copy(); # simulate squared-C by editing extracted source? omitted\\n'" in /Users/skyefortier/xps-verify
 succeeded in 120ms:
0 100.13414005218658
30 219.3991381848063
75 461.76541491579644
110 499.7312788702072
149 499.6355795222399
150 499.6355795222399

 succeeded in 112ms:
peak_x 43.4 expected 43.4022790912908

 succeeded in 123ms:
flat_max_net 0.0 edges 500.0 500.0
neg_scale_edges 100.0 200.0 min 100.0 max 200.0
neg_scale_bg [100.    126.788 148.444 165.445 178.303 187.552 193.756 197.496 199.373
 200.    200.   ]
guard_fixture [0. 0. 0. 0.]

codex
The extracted `tougaard_background` body verifies the regenerated JS table exactly and exercises the degenerate guard fixture as described. I’m also probing the negative-scale case explicitly rather than treating the comment as sufficient.
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text()\\nm=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s)\\nt=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\nold=t.group(0).replace(\"B_coef, C_coef = 2866.0, 1643.0\", \"B_coef, C_coef = 2866.0, 1643.0 * 1643.0\")\\nns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+old, ns); f=ns[\"tougaard_background\"]\\nx=np.linspace(100.0,0.0,1001); y=np.full_like(x,1e-9); y[0]=2e-9; y[800]=1e6; bg=f(x,y); px=x[:800][np.argmax(bg[:800])]; print(\"squared_C_peak_x\", float(px), \"expected_old_near_edge\")'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text()\\nm=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s)\\nt=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\nns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+t.group(0), ns); f=ns[\"tougaard_background\"]\\nx=np.linspace(740.0,700.0,201)\\ny=np.linspace(100.0,200.0,201)+1500*np.exp(-0.5*((x-724.0)/1.5)**2)\\nbg=f(x,y)\\nprint(\"edges\", y[0], y[-1], bg[0], bg[-1], \"bg_minmax\", float(bg.min()), float(bg.max()), \"net_minmax\", float((y-bg).min()), float((y-bg).max()))\\nfor i in [0,40,80,120,160,200]: print(i, float(x[i]), float(y[i]), float(bg[i]))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text()\\nm=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s)\\nt=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\nold=t.group(0).replace(\"c0 = float(ya[-1])\\\\n    net = ya - c0\", \"c0 = 0.0\\\\n    net = ya\")\\nold=old.replace(\"if bg[0] == 0.0:\\\\n        out = np.full(n, c0)\\\\n    else:\\\\n        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])\", \"denom = bg[0] if bg[0] "'!= 0.0 else 1.0'"\\\\n    out = bg * (float(ya[0]) / denom)\")\\nns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+old, ns); f=ns[\"tougaard_background\"]\\nx=np.linspace(740.0,700.0,200); y=np.full_like(x,500.0); bg=f(x,y); print(\"preF1_flat_edges\", float(bg[0]), float(bg[-1]), \"net_max\", float(np.max(np.abs(y-bg))))\\nx2=np.linspace(295.0,280.0,151); y2=100.0+5000.0*np.exp(-0.5*((x2-287.0)/0.8)**2)+400.0/(1.0+np.exp(-(287.0-x2))); bg2=f(x2,y2); print(\"preF1_low_edge\", float(bg2[-1]), \"y_low\", float(y2[-1]))'" in /Users/skyefortier/xps-verify
 succeeded in 113ms:
edges 100.0 200.0 100.0 200.0 bg_minmax 100.0 206.87848355834436 net_minmax -49.23013833900944 1437.1222261726043
0 740.0 100.0 100.0
40 732.0 120.00099875422048 137.03105068391991
80 724.0 1640.0 202.8777738273957
120 716.0 160.0009987542205 203.132984726101
160 708.0 180.0 200.4177105745831
200 700.0 200.0 200.0

 succeeded in 114ms:
squared_C_peak_x 100.0 expected_old_near_edge

 succeeded in 108ms:
exec
/bin/zsh -lc "rg -n \"@app\\.route\\('/api/(fit|background)|def run_fit|def compute_background_only|background_method|endpoint_avg\" app.py fitting.py templates/index.html autofit/engine.py autofit/parity.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/parity.py:76:    endpoint_avg: int = 1,
autofit/parity.py:99:        bg_inner = shirley_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
autofit/parity.py:101:        bg_inner = smart_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
autofit/parity.py:103:        bg_inner = smart_experimental_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:105:        bg_inner = shirley_linear_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:107:        bg_inner = tougaard_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
autofit/parity.py:182:        rf.roi_be, rf.roi_intensity, rf.bg_method, i0, i1, rf.endpoint_avg
autofit/parity.py:198:        background_method=rf.bg_method,
autofit/parity.py:201:        endpoint_avg=rf.endpoint_avg,
fitting.py:934:def run_fit(
fitting.py:938:    background_method: str = "shirley",
fitting.py:945:    endpoint_avg: int = 1,
fitting.py:955:    background_method : 'shirley' | 'linear' | 'none'
fitting.py:1015:    bg_method = background_method.lower()
fitting.py:1030:        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1032:        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1034:        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1036:        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1038:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1051:        raise ValueError(f"Unknown background method '{background_method}'")
fitting.py:1254:def compute_background_only(
fitting.py:1260:    endpoint_avg: int = 1,
fitting.py:1268:        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
fitting.py:1270:        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
fitting.py:1272:        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
fitting.py:1274:        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
fitting.py:1276:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
app.py:168:    "least_squares": {"background_method": "shirley"},
app.py:716:        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
app.py:718:            ep_avg = max(1, int(body.get("endpoint_avg", 1)))
app.py:720:            return _err("endpoint_avg must be an integer")
app.py:726:                endpoint_avg=ep_avg,
app.py:792:        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
app.py:794:            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
app.py:796:            return _err("endpoint_avg must be an integer")
app.py:832:                background_method=bg_method,
app.py:839:                endpoint_avg=endpoint_avg,
templates/index.html:6675:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvg };
templates/index.html:6783:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvgVal };
templates/index.html:13103:      { key: 'background_method', type: 'select',

exec
/bin/zsh -lc 'git diff --exit-code 3d9ff54''^ 3d9ff54 -- app.py routes.py 2>/dev/null; printf '"'api_surface_diff_exit=%s\\n' "'$?' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
api_surface_diff_exit=0

exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text()\\nm=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s)\\nt=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\ncurrent=t.group(0)\\nold=current.replace(\"w = np.abs(np.gradient(xa))\\\\n        bg = np.zeros(n)\", \"bg = np.zeros(n)\")\\nold=old.replace(\"kernel * net[i:] * w[i:]\", \"kernel * net[i:]\")\\n# keep uniform branch current, but old nonuniform branch lacks weights\\nns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+old, ns); f=ns[\"tougaard_background\"]\\nx=np.linspace(740.0,700.0,300); y=4000.0+6000.0*np.exp(-0.5*((x-710.9)/1.6)**2)\\nxa=np.concatenate([np.linspace(740.0,720.1,60), np.linspace(720.0,700.0,400)]); ya=np.interp(xa[::-1], x[::-1], y[::-1])[::-1]\\ngot=f(xa,ya)\\nB,C=2866.0,1643.0; c0=float(ya[-1]); net=ya-c0; w=np.abs(np.gradient(xa)); ref=np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T=np.abs(xa[i:]-xa[i]); ref[i]=float(np.sum((B*T)/(C+T*T)**2*net[i:]*w[i:]))\\nref=c0+ref*((float(ya[0])-c0)/ref[0])\\nprint(\"old_nonuniform_max_abs\", float(np.max(np.abs(got-ref))), \"allclose\", bool(np.allclose(got,ref,rtol=1e-9)))'" in /Users/skyefortier/xps-verify
 succeeded in 120ms:
old_nonuniform_max_abs 4.547473508864641e-13 allclose True

codex
A more adversarial check turned up something important in the test suite, not necessarily the production code: my first simulation suggests the “genuinely nonuniform” Python test may not actually fail if the nonuniform branch omits local weights, because the final high-edge anchor can cancel a global spacing error. I’m checking whether that’s a simulation mistake or a real test weakness.
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re\\ns=pathlib.Path(\"fitting.py\").read_text(); t=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s).group(0); old=t.replace(\"w = np.abs(np.gradient(xa))\\\\n        bg = np.zeros(n)\", \"bg = np.zeros(n)\").replace(\"kernel * net[i:] * w[i:]\", \"kernel * net[i:]\"); print(\"has_weight\", \"w[i:]\" in old); print(\"has_gradient\", \"gradient\" in old); print(old[old.find(\"else:\", old.find(\"if uniform\")):old.find(\"# Amplitude anchor\")])'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-Ocxi4dUa' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-m9SnQYpt' (errno=Operation not permitted)
has_weight False
has_gradient True
else:
        bg = np.zeros(n)
        for i in range(n):
            T = np.abs(xa[i:] - xa[i])
            kernel = (B_coef * T) / (C_coef + T * T) ** 2
            bg[i] = float(np.sum(kernel * net[i:]))

    

exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text(); m=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s); t=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\ncur_ns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+t.group(0), cur_ns); cur=cur_ns[\"tougaard_background\"]\\nold_src=t.group(0).replace(\"w = np.abs(np.gradient(xa))\\\\n        bg = np.zeros(n)\", \"bg = np.zeros(n)\").replace(\"kernel * net[i:] * w[i:]\", \"kernel * net[i:]\")\\nold_ns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+old_src, old_ns); old=old_ns[\"tougaard_background\"]\\nx=np.concatenate([np.linspace(740.0,720.1,60), np.linspace(720.0,700.0,400)]); y=4000.0+6000.0*np.exp(-0.5*((x-710.9)/1.6)**2)\\nbc=cur(x,y); bo=old(x,y); d=bo-bc; print(\"cur_old_max_abs\", float(np.max(np.abs(d))), \"max_rel_to_range\", float(np.max(np.abs(d))/(np.max(bc)-np.min(bc))))\\nfor i in [0,20,59,60,120,250,459]: print(i, float(x[i]), float(bc[i]), float(bo[i]), float(d[i]))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text(); m=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s); t=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\nold_src=t.group(0).replace(\"w = np.abs(np.gradient(xa))\\\\n        bg = np.zeros(n)\", \"bg = np.zeros(n)\").replace(\"kernel * net[i:] * w[i:]\", \"kernel * net[i:]\")\\nns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+old_src, ns); f=ns[\"tougaard_background\"]\\nx=np.linspace(740.0,700.0,300); y=(4000.0+6000.0*np.exp(-0.5*((x-710.9)/1.6)**2)); bg_uniform=f(x,y); x_j=x.copy(); x_j[1:-1]+=1e-4*np.sin(np.arange(len(x)-2)); bg_non=f(x_j,y); print(\"near_uniform_old_max\", float(np.max(np.abs(bg_uniform-bg_non))))'" in /Users/skyefortier/xps-verify
 succeeded in 132ms:
cur_old_max_abs 0.0 max_rel_to_range 0.0
0 740.0 4000.0 4000.0 0.0
20 733.2542372881356 3999.9999999822903 3999.9999999822903 0.0
59 720.1 4000.000000174185 4000.000000174185 0.0
60 720.0 4000.000000177065 4000.000000177065 0.0
120 716.9924812030075 4000.000000272484 4000.000000272484 0.0
250 710.4761904761905 4000.000000483851 4000.000000483851 0.0
459 700.0 4000.0000005015495 4000.0000005015495 0.0

 succeeded in 122ms:
near_uniform_old_max 3.637978807091713e-12

codex
That check was real: the current Python nonuniform test’s fixture has effectively equal high- and low-BE endpoints, so the post-F1 anchor scales the Tougaard integral almost to zero. In that fixture, the old no-weight nonuniform branch and the fixed branch are numerically identical after anchoring.
exec
/bin/zsh -lc 'git diff --unified=0 3d9ff54''^ 3d9ff54 -- tests/test_tougaard_background.py | sed -n '"'90,190p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tKynGR21' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UdMLU8zI' (errno=Operation not permitted)
+    # low-BE edge is index -1 on this descending grid
+    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
+        f"low-BE edge dove to {bg[-1]:.1f} instead of tracking the "
+        f"{y[-1]:.1f}-count baseline"
+    )
+    assert np.isclose(bg[0], y[0], rtol=1e-12)
+
+
+def test_nonuniform_grid_uses_local_quadrature_weights():
+    """F2 regression pin (2026-07-17): the nonuniform-grid branch must weight
+    each term by its local energy spacing.
+
+    It previously used exact per-point separations but omitted the spacing
+    weights, silently applying uniform-grid quadrature inside the branch
+    written precisely BECAUSE the grid is not uniform (~24% error on a
+    genuinely nonuniform grid). np.gradient returns dx exactly on a uniform
+    grid, so the two branches must now agree to floating point -- the
+    uniformity test is an optimization, not a semantic fork."""
+    # Uniform grid, then the same grid perturbed below the uniformity
+    # tolerance so the nonuniform branch runs on near-identical data.
+    x = np.linspace(740.0, 700.0, 300)
+    y = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))
+    bg_uniform = tougaard_background(x, y)
+    x_jitter = x.copy()
+    x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
+    bg_nonuniform = tougaard_background(x_jitter, y)
+    assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
+        "uniform and nonuniform branches disagree on near-identical grids"
+    )
+
+    # Genuinely nonuniform grid vs an explicit spacing-weighted reference.
+    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
+                         np.linspace(720.0, 700.0, 400)])
+    ya = np.interp(xa[::-1], x[::-1], y[::-1])[::-1]
+    got = tougaard_background(xa, ya)
+
+    B_coef, C_coef = 2866.0, 1643.0
+    c0 = float(ya[-1])
+    net = ya - c0
+    w = np.abs(np.gradient(xa))
+    ref = np.zeros(len(xa))
+    for i in range(len(xa)):
+        T = np.abs(xa[i:] - xa[i])
+        ref[i] = float(np.sum((B_coef * T) / (C_coef + T * T) ** 2 * net[i:] * w[i:]))
+    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
+    assert np.allclose(got, ref, rtol=1e-9), (
+        "nonuniform branch does not match spacing-weighted quadrature"
+    )

exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text(); m=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s); t=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\ncur_ns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+t.group(0), cur_ns); cur=cur_ns[\"tougaard_background\"]\\nold_src=t.group(0).replace(\"w = np.abs(np.gradient(xa))\\\\n        bg = np.zeros(n)\", \"bg = np.zeros(n)\").replace(\"kernel * net[i:] * w[i:]\", \"kernel * net[i:]\")\\nold_ns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+old_src, old_ns); old=old_ns[\"tougaard_background\"]\\n# Same nonuniform grid, add a high-BE endpoint rise so F1 anchor does not collapse the integral\\nxa=np.concatenate([np.linspace(740.0,720.1,60), np.linspace(720.0,700.0,400)]); y=4000.0+800.0*(xa-700.0)/40.0+6000.0*np.exp(-0.5*((xa-710.9)/1.6)**2)\\nbc=cur(xa,y); bo=old(xa,y); print(\"endpoint_delta\", float(y[0]-y[-1]), \"max_abs_current_old\", float(np.max(np.abs(bc-bo))), \"rel_span\", float(np.max(np.abs(bc-bo))/(np.max(bc)-np.min(bc))))\\nfor i in [0,59,60,120,250,459]: print(i, float(xa[i]), float(bc[i]), float(bo[i]), float(bo[i]-bc[i]))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'python3 -c $'"'import pathlib, re, numpy as np\\ns=pathlib.Path(\"fitting.py\").read_text(); m=re.search(r\"def _apply_endpoint_averaging[\\\\s\\\\S]*?(?=\\\\ndef shirley_linear_background)\", s); t=re.search(r\"def tougaard_background[\\\\s\\\\S]*?(?=\\\\ndef _la_casaxps_true)\", s)\\ncur_ns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+t.group(0), cur_ns); cur=cur_ns[\"tougaard_background\"]\\nold_src=t.group(0).replace(\"w = np.abs(np.gradient(xa))\\\\n        bg = np.zeros(n)\", \"bg = np.zeros(n)\").replace(\"kernel * net[i:] * w[i:]\", \"kernel * net[i:]\")\\nold_ns={\"np\":np}; exec(m.group(0)+\"\\\\n\"+old_src, old_ns); old=old_ns[\"tougaard_background\"]\\n# Recreate exact test fixture and report endpoint delta / span\\nx=np.linspace(740.0,700.0,300); y=(4000.0+6000.0*np.exp(-0.5*((x-710.9)/1.6)**2)); xa=np.concatenate([np.linspace(740.0,720.1,60), np.linspace(720.0,700.0,400)]); ya=np.interp(xa[::-1], x[::-1], y[::-1])[::-1]\\nbc=cur(xa,ya); bo=old(xa,ya); print(\"test_endpoint_delta\", float(ya[0]-ya[-1]), \"current_span\", float(np.max(bc)-np.min(bc)), \"old_current_max_abs\", float(np.max(np.abs(bo-bc))))'" in /Users/skyefortier/xps-verify
 succeeded in 125ms:
endpoint_delta 799.9999994984505 max_abs_current_old 104.82975035097024 rel_span 0.13103718802086484
0 740.0 4800.0 4800.0 0.0
59 720.1 4401.554276315047 4482.706361858399 81.15208554335186
60 720.0 4397.8145896677715 4478.213049287372 80.39845961960054
120 716.9924812030075 4277.838935435659 4333.990275782101 56.15134034644234
250 710.4761904761905 4026.05613517584 4031.322088583543 5.265953407702909
459 700.0 4000.0000005015495 4000.0000005015495 0.0

 succeeded in 124ms:
test_endpoint_delta -5.015494934923481e-07 current_span 5.202223292144481e-07 old_current_max_abs 4.547473508864641e-13

codex
1. **MAJOR** [tests/test_tougaard_background.py](/Users/skyefortier/xps-verify/tests/test_tougaard_background.py:218) — `test_nonuniform_grid_uses_local_quadrature_weights` does not actually guard F2. The fixture has effectively equal endpoints (`ya[0] - ya[-1] ~= -5e-7`), so the F1 anchor at [fitting.py](/Users/skyefortier/xps-verify/fitting.py:630) scales the Tougaard integral almost to zero. I simulated reverting only the nonuniform `* w[i:]` term at [fitting.py](/Users/skyefortier/xps-verify/fitting.py:616); this test fixture still matched current output to `4.5e-13`. With a high-BE endpoint rise on the same nonuniform grid, the old no-weight branch differs by about `105` counts, so the production fix is plausible, but this regression pin is laundered. Add an asymmetric endpoint step/slope so F2 failure survives anchoring.

Other checks: commit scope is contained to the four expected files; `autofit/engine.py`, `autofit/methods`, and API surface files have zero diff. JS twin test passes. `pytest` could not be run because this checkout lacks `pytest`/`lmfit`; I used extracted-function probes for the Python numerics. Fixture grep found no Tougaard numeric saved-fit pins outside the two touched test files.

C0 edge anchoring is a model limitation, not a new correctness bug: it will be visibly wrong if the low-BE edge is still contaminated by a peak/tail or strong slope, and `n_avg` only reduces endpoint noise. Negative-scale cases can overshoot the data on falling-baseline spectra, but that follows the existing unclamped endpoint-anchor policy rather than a scoped regression.

VERDICT: NO-GO
tokens used
93,091
1. **MAJOR** [tests/test_tougaard_background.py](/Users/skyefortier/xps-verify/tests/test_tougaard_background.py:218) — `test_nonuniform_grid_uses_local_quadrature_weights` does not actually guard F2. The fixture has effectively equal endpoints (`ya[0] - ya[-1] ~= -5e-7`), so the F1 anchor at [fitting.py](/Users/skyefortier/xps-verify/fitting.py:630) scales the Tougaard integral almost to zero. I simulated reverting only the nonuniform `* w[i:]` term at [fitting.py](/Users/skyefortier/xps-verify/fitting.py:616); this test fixture still matched current output to `4.5e-13`. With a high-BE endpoint rise on the same nonuniform grid, the old no-weight branch differs by about `105` counts, so the production fix is plausible, but this regression pin is laundered. Add an asymmetric endpoint step/slope so F2 failure survives anchoring.

Other checks: commit scope is contained to the four expected files; `autofit/engine.py`, `autofit/methods`, and API surface files have zero diff. JS twin test passes. `pytest` could not be run because this checkout lacks `pytest`/`lmfit`; I used extracted-function probes for the Python numerics. Fixture grep found no Tougaard numeric saved-fit pins outside the two touched test files.

C0 edge anchoring is a model limitation, not a new correctness bug: it will be visibly wrong if the low-BE edge is still contaminated by a peak/tail or strong slope, and `n_avg` only reduces endpoint noise. Negative-scale cases can overshoot the data on falling-baseline spectra, but that follows the existing unclamped endpoint-anchor policy rather than a scoped regression.

VERDICT: NO-GO
