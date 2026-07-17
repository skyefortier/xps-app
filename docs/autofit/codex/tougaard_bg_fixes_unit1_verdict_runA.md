OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f7212-a323-7540-8f2f-68dd0cdc647a
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
I’ll review this as a code-review pass: first verify the commit scope, then inspect the Tougaard diff and tests, then run the relevant test subset if the read-only sandbox allows it. After that I’ll check the repository for pinned numeric fixtures and caller compatibility.
exec
/bin/zsh -lc 'git show --name-only --format=fuller 3d9ff54' in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'git diff-tree --no-commit-id --name-status -r 3d9ff54' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3PtgIF7y' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4OozXF04' (errno=Operation not permitted)
M	fitting.py
M	templates/index.html
M	tests/js/tougaard_twin.test.js
M	tests/test_tougaard_background.py

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yuuwiFuH' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-N0YfrCSW' (errno=Operation not permitted)
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

fitting.py
templates/index.html
tests/js/tougaard_twin.test.js
tests/test_tougaard_background.py

exec
/bin/zsh -lc 'git status --short && git branch --show-current && git show --stat --oneline --decorate --find-renames 3d9ff54' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-kcjXg7Fk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-w2fNrsO6' (errno=Operation not permitted)
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OkKrl5jW' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2Zqw47lr' (errno=Operation not permitted)
feature-autofit-stage2
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UR0qeRGa' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JW4K6JRO' (errno=Operation not permitted)
3d9ff54 fix(fitting): Tougaard pre-loss constant (F1) + non-uniform quadrature weights (F2)
 fitting.py                        | 110 +++++++++++++++++++++-----------
 templates/index.html              |  50 ++++++++++-----
 tests/js/tougaard_twin.test.js    |  44 ++++++++++---
 tests/test_tougaard_background.py | 129 ++++++++++++++++++++++++++++++++++----
 4 files changed, 260 insertions(+), 73 deletions(-)

codex
The commit is on `feature-autofit-stage2` and its file scope is the four expected files. Git is emitting macOS temp-cache warnings because the sandbox is read-only, but the read operations are still returning usable data.
exec
/bin/zsh -lc 'git show --unified=80 -- templates/index.html' in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'git show --unified=80 -- fitting.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Bm7dI6xs' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5jFuZ9kQ' (errno=Operation not permitted)

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hKPicrII' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DUzPdK5y' (errno=Operation not permitted)

exec
/bin/zsh -lc 'git diff 3d9ff54''^ 3d9ff54 -- autofit/engine.py autofit/methods fitting.py templates/index.html | sed -n '"'1,260p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vfwNrwnM' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-e4EjH0Li' (errno=Operation not permitted)
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
 

codex
The implementation diff matches the stated containment so far: `fitting.py` only shows `tougaard_background`, and the explicit diff check against `autofit/engine.py`/`autofit/methods` is empty. I’m now reading the rewritten tests and the live caller sites, because that’s where scope mistakes or laundered assertions usually show up.
exec
/bin/zsh -lc 'git show --unified=120 3d9ff54 -- tests/js/tougaard_twin.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0vjF86K4' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-I2QHNsTp' (errno=Operation not permitted)
commit 3d9ff542e5b341717b4967f085d6bb22380dfdbf
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Fri Jul 17 15:50:56 2026 -0600

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

diff --git a/tests/js/tougaard_twin.test.js b/tests/js/tougaard_twin.test.js
index 668c2a4..7b64aaf 100644
--- a/tests/js/tougaard_twin.test.js
+++ b/tests/js/tougaard_twin.test.js
@@ -1,168 +1,192 @@
 // Tougaard background — JS twin of fitting.py's tougaard_background.
 //
 // The function lives inline in templates/index.html; extract its source and
 // evaluate it so these tests exercise the exact shipped code. Pins the
 // 2026-07-04 fix (mirrored from the backend, see
 // tests/test_tougaard_background.py):
 //   1. Universal cross-section constant C = 1643 eV² (was shipped squared:
 //      1643*1643). Kernel K(T) = B·T/(C+T²)² peaks at sqrt(C/3) ≈ 23.4 eV.
 //      S. Tougaard, Surf. Interface Anal. 11, 453 (1988).
 //   2. Order-robustness: the one-sided loss sum needs a descending-BE grid;
 //      ascending input is normalized internally and flipped back.
 //   3. Amplitude anchored to the measured intensity at the HIGH-BE edge
 //      (the old "trailing endpoint" rescale was degenerate: K(0)=0 forced
 //      the zero-guard, multiplying by raw trailing counts instead).
 
 const { test } = require('node:test');
 const assert = require('node:assert');
 const fs = require('node:fs');
 const path = require('node:path');
 
 const html = fs.readFileSync(
   path.join(__dirname, '../../templates/index.html'), 'utf8');
 const match = html.match(/function tougaardBackground\([\s\S]*?\n\}/);
 assert.ok(match, 'tougaardBackground not found in templates/index.html');
 const tougaardBackground = eval('(' + match[0] + ')');
 
 const avgMatch = html.match(/function _applyEndpointAveraging\([\s\S]*?\n\}/);
 assert.ok(avgMatch, '_applyEndpointAveraging not found in templates/index.html');
 const _applyEndpointAveraging = eval('(' + avgMatch[0] + ')');
 
 function syntheticSpectrum() {
   // Same C 1s-like region as the Python tests: descending BE, dx = 0.1 eV.
   const be = [], intensity = [];
   for (let i = 0; i <= 150; i++) {
     const x = 295.0 - 0.1 * i;
     be.push(x);
     intensity.push(
       100.0
       + 5000.0 * Math.exp(-0.5 * Math.pow((x - 287.0) / 0.8, 2))
       + 400.0 / (1.0 + Math.exp(-(287.0 - x)))
     );
   }
   return { be, intensity };
 }
 
 test('loss-kernel response peaks ~23.4 eV above a delta-like peak', () => {
   const n = 1001;
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
 
   const bg = tougaardBackground(be, intensity);
 
   let maxV = -Infinity, maxX = NaN;
   for (let i = 0; i < spikeIdx; i++) {   // high-BE side: traces K(be − 20)
     if (bg[i] > maxV) { maxV = bg[i]; maxX = be[i]; }
   }
   const expected = 20.0 + Math.sqrt(1643.0 / 3.0);  // ≈ 43.4 eV
   assert.ok(Math.abs(maxX - expected) <= 0.25,
     `kernel response peaks at ${maxX.toFixed(2)} eV, expected ~${expected.toFixed(2)}; ` +
     'a peak near 100 eV means the squared constant (1643*1643) is back');
 });
 
 test('ascending and descending BE input give the identical background', () => {
   const { be, intensity } = syntheticSpectrum();
   const bgDesc = tougaardBackground(be, intensity);
   const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
   bgAsc.reverse();
   for (let i = 0; i < be.length; i++) {
     assert.strictEqual(bgDesc[i], bgAsc[i],
       `order-dependent output at index ${i}: ${bgDesc[i]} vs ${bgAsc[i]}`);
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
   //   y = (100.0 + 5000.0*np.exp(-0.5*((x-287.0)/0.8)**2)
   //        + 400.0/(1.0+np.exp(-(287.0-x))))
   //   bg = tougaard_background(x, y)
   //   print([float(bg[i]) for i in (0, 30, 75, 110, 149, 150)])
   //   EOF
   // Regenerate with that snippet if the backend numerics change for a
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
   for (const [idx, want] of Object.entries(expected)) {
     const got = bg[Number(idx)];
     const tol = want === 0 ? 1e-15 : Math.abs(want) * 1e-9;
     assert.ok(Math.abs(got - want) <= tol,
       `backend/frontend disagree at index ${idx}: js ${got} vs python ${want}`);
   }
 });
 
 // --- Codex review finding (2026-07-04, both runs, MAJOR): the shipped
 // caller computeBackgroundCore passed RAW intensity to tougaardBackground
 // while every backend caller applies endpoint averaging first. With the
 // high-BE-edge anchor, averaging directly sets the anchor amplitude, so
 // the caller contract — not just the function — must match the backend
 // (fitting.py run_fit / compute_background_only both do
 // tougaard_background(x, _apply_endpoint_averaging(y, n))).
 test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
   const coreMatch = html.match(/function computeBackgroundCore\([\s\S]*?\n\}/);
   assert.ok(coreMatch, 'computeBackgroundCore not found in templates/index.html');
   // Stubs for background types this test never routes to; the eval'd
   // function closes over this scope, so these names resolve at call time.
   const manualAnchorBackground = () => { throw new Error('unexpected route: manual'); };
   const shirleyBackground = () => { throw new Error('unexpected route: shirley'); };
   const smartBackground = () => { throw new Error('unexpected route: smart'); };
   const smartExperimentalBackground = () => { throw new Error('unexpected route: smart_exp'); };
   const shirleyLinearBackground = () => { throw new Error('unexpected route: shirley_linear'); };
   const linearBackground = () => { throw new Error('unexpected route: linear'); };
   const computeBackgroundCore = eval('(' + coreMatch[0] + ')');
 
   // Descending grid with an outlier at the high-BE edge: raw vs 3-point
   // averaged anchors differ by construction (Codex's concrete scenario).
   const n = 21;
   const be = [], intensity = [];
   for (let i = 0; i < n; i++) { be.push(292.0 - 0.5 * i); intensity.push(100); }
   intensity[0] = 10000;   // high-BE outlier
   intensity[10] = 4000;   // a peak so the correlation is non-trivial
 
   const nAvg = 3;
   const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
 
   // Branch 1: bg window covers the data (main sliced path)
   const mainOut = computeBackgroundCore(be, intensity, {
     bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
     bgStart: '292', bgEnd: '282',
   });
   // Branch 2: bg window misses the data entirely (fallback full-range path)
   const fallbackOut = computeBackgroundCore(be, intensity, {
     bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
     bgStart: '900', bgEnd: '905',
   });
 
   for (const [label, out] of [['main', mainOut], ['fallback', fallbackOut]]) {
     for (let i = 0; i < n; i++) {
       assert.strictEqual(out[i], expected[i],
         `${label} branch: caller bypasses endpoint averaging at index ${i}: ` +
         `${out[i]} vs averaged ${expected[i]}`);
     }
   }
 });

exec
/bin/zsh -lc 'git show --unified=120 3d9ff54 -- tests/test_tougaard_background.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Qemf7338' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-op15KleA' (errno=Operation not permitted)
commit 3d9ff542e5b341717b4967f085d6bb22380dfdbf
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Fri Jul 17 15:50:56 2026 -0600

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

diff --git a/tests/test_tougaard_background.py b/tests/test_tougaard_background.py
index 51ec8ca..84cb4ca 100644
--- a/tests/test_tougaard_background.py
+++ b/tests/test_tougaard_background.py
@@ -1,148 +1,253 @@
 """Tougaard universal-cross-section background — correctness pins.
 
 Pins the 2026-07-04 bug-fix (branch feature-autofit-stage2):
 
 1. The universal-cross-section constant C was shipped SQUARED
    (``C = 1643.0**2`` ≈ 2.7e6 eV² instead of C = 1643 eV²), a
    transcription slip of "C = 1643 eV²".  The loss kernel
    K(T) = B·T/(C + T²)² peaks at T = sqrt(C/3): ≈ 23.4 eV with the
    correct constant, ≈ 948.6 eV with the squared one — so over any real
    ~20 eV XPS window the shipped "Tougaard" background was essentially
    flat/zero.  Reference: S. Tougaard, Surf. Interface Anal. 11, 453
    (1988) — two-parameter universal cross-section, B = 2866 eV²,
    C = 1643 eV².
 
 2. The one-sided loss sum (j >= i) is only physical on a DESCENDING
    binding-energy grid; ascending input silently produced a background
    accumulating on the wrong side (same bug class as the np.interp
    descending-grid registration bug).  The function now normalizes to
    descending internally and flips the result back, mirroring
    shirley_background's ascending normalization.
 
 3. The trailing-endpoint rescale was degenerate: K(0) = 0 makes the
    trailing background sample identically zero, so the zero-guard always
    fired and the "match the trailing endpoint" scale was in fact
    "multiply by the trailing raw counts".  The normalization now anchors
    the background to the measured intensity at the HIGH-BE edge of the
    window (the standard practical Tougaard criterion: B is effectively
    fitted so the background meets the spectrum above the peak).
 
 No pre-existing test or fixture pinned the old (wrong) Tougaard output
 (verified by grep over tests/, tests/autofit/, docs/autofit/inventory/,
 scripts/ on 2026-07-04), so nothing needed regeneration.
 """
 
 import numpy as np
 
 from fitting import tougaard_background
 
 
 def _synthetic_spectrum(descending: bool = True):
     """Realistic C 1s-like region: baseline + Gaussian peak + loss step."""
     x = np.linspace(295.0, 280.0, 151)  # descending BE, dx = 0.1 eV
     y = (
         100.0
         + 5000.0 * np.exp(-0.5 * ((x - 287.0) / 0.8) ** 2)
         + 400.0 / (1.0 + np.exp(-(287.0 - x)))  # step rising toward high BE
     )
     if not descending:
         return x[::-1].copy(), y[::-1].copy()
     return x, y
 
 
 def test_kernel_peak_near_sqrt_c_over_3():
     """The loss-kernel response to a delta-like peak must peak ~23.4 eV
     above the peak (sqrt(C/3) with C = 1643 eV²), not ~949 eV.
 
     A spike at x0 on a descending grid produces bg(x) ∝ K(x − x0) on the
     high-BE side, so the argmax of the background directly locates the
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
 
     bg = tougaard_background(x, y)
 
     high_be_side = slice(0, spike_idx)  # x > 20 eV: traces K(x − 20)
     peak_x = x[high_be_side][np.argmax(bg[high_be_side])]
     expected = 20.0 + np.sqrt(1643.0 / 3.0)  # 20 + 23.402...
     assert abs(peak_x - expected) <= 0.25, (
         f"kernel response peaks at x = {peak_x:.2f} eV; expected "
         f"{expected:.2f} eV (spike at 20.0 + sqrt(C/3) ≈ 23.4 eV). "
         f"A peak near x = 100 means the squared constant (C = 1643²) is back."
     )
 
 
 def test_ascending_and_descending_input_agree_exactly():
     """The same spectrum fed in ascending vs descending BE order must give
     the identical background (element-wise, after re-reversal)."""
     x_d, y_d = _synthetic_spectrum(descending=True)
     x_a, y_a = _synthetic_spectrum(descending=False)
 
     bg_d = tougaard_background(x_d, y_d)
     bg_a = tougaard_background(x_a, y_a)
 
     assert np.array_equal(bg_d, bg_a[::-1]), (
         f"order-dependent output: max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
     )
 
 
 def test_ascending_descending_parity_on_nonuniform_grid():
     """Order-robustness must also hold on the non-uniform-grid code path
     (which uses the exact per-point separation loop, not the convolution)."""
     # Deterministic, mildly non-uniform descending grid
     steps = 0.08 + 0.04 * np.sin(np.arange(120))
     x_d = 295.0 - np.concatenate(([0.0], np.cumsum(steps)))
     y_d = 100.0 + 4000.0 * np.exp(-0.5 * ((x_d - 290.0) / 1.0) ** 2)
 
     bg_d = tougaard_background(x_d, y_d)
     bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
 
     assert np.array_equal(bg_d, bg_a[::-1]), (
         f"non-uniform grid is order-dependent: "
         f"max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
     )
 
 
 def test_background_anchored_at_high_be_edge():
     """The background must equal the measured intensity at the high-BE edge
     of the window (practical Tougaard criterion: the universal cross-section
     amplitude is scaled so the background meets the data above the peak),
     and must vanish at the low-BE edge (no in-window emitters below it)."""
     x, y = _synthetic_spectrum(descending=True)
     bg = tougaard_background(x, y)
 
     # x[0] is the high-BE edge on this descending grid
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
     """< 2 points: no background can be defined; must return zeros."""
     assert np.array_equal(
         tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
     )
     assert tougaard_background(np.array([]), np.array([])).size == 0

exec
/bin/zsh -lc "rg -n \"tougaard_background|tougaardBackground|BackgroundType\\.TOUGAARD|computeBackgroundCore|_applyEndpointAveraging|/api/fit|/api/background\" ." in /Users/skyefortier/xps-verify
 succeeded in 0ms:
./fitting.py:508:def tougaard_background(
./fitting.py:550:    ``tougaardBackground``.
./fitting.py:1038:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
./fitting.py:1276:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
./tests/test_tougaard_background.py:37:from fitting import tougaard_background
./tests/test_tougaard_background.py:74:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:92:    bg_d = tougaard_background(x_d, y_d)
./tests/test_tougaard_background.py:93:    bg_a = tougaard_background(x_a, y_a)
./tests/test_tougaard_background.py:108:    bg_d = tougaard_background(x_d, y_d)
./tests/test_tougaard_background.py:109:    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
./tests/test_tougaard_background.py:123:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:143:    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
./tests/test_tougaard_background.py:163:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:180:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:197:    bg = tougaard_background(x, y)
./tests/test_tougaard_background.py:220:    bg_uniform = tougaard_background(x, y)
./tests/test_tougaard_background.py:223:    bg_nonuniform = tougaard_background(x_jitter, y)
./tests/test_tougaard_background.py:232:    got = tougaard_background(xa, ya)
./tests/test_tougaard_background.py:251:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
./tests/test_tougaard_background.py:253:    assert tougaard_background(np.array([]), np.array([])).size == 0
./tests/test_mixed_ds_lacx_e2e.py:4:same code path as /api/fit, and assert each peak's parameters recover
./CLAUDE.md:53:| `POST`   | `/api/background`         | Compute background curve for a session. |
./CLAUDE.md:54:| `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |
./CLAUDE.md:233:`POST /api/fit` runs lmfit on the server. Selectable methods: `leastsq`
./CLAUDE.md:258:| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
./app.py:21:POST /api/background        Compute background for a session
./app.py:22:POST /api/fit               Run peak fitting; returns full result
./app.py:51:# /api/fit. Each perturbation re-runs the full composite fit, so an unbounded
./app.py:180:# /api/fit path never touches this code) — extracted so /api/analyze (sync)
./app.py:691:    @app.post("/api/background")
./app.py:739:    @app.post("/api/fit")
./app.py:857:    #    /api/fit path above is untouched) ──────────────────────────────────
./xps-fitting-tool.html:755:function tougaardBackground(be, intensity) {
./xps-fitting-tool.html:778:  if (type === 'tougaard') return tougaardBackground(be, intensity);
./tests/js/tougaard_twin.test.js:1:// Tougaard background — JS twin of fitting.py's tougaard_background.
./tests/js/tougaard_twin.test.js:6:// tests/test_tougaard_background.py):
./tests/js/tougaard_twin.test.js:23:const match = html.match(/function tougaardBackground\([\s\S]*?\n\}/);
./tests/js/tougaard_twin.test.js:24:assert.ok(match, 'tougaardBackground not found in templates/index.html');
./tests/js/tougaard_twin.test.js:25:const tougaardBackground = eval('(' + match[0] + ')');
./tests/js/tougaard_twin.test.js:27:const avgMatch = html.match(/function _applyEndpointAveraging\([\s\S]*?\n\}/);
./tests/js/tougaard_twin.test.js:28:assert.ok(avgMatch, '_applyEndpointAveraging not found in templates/index.html');
./tests/js/tougaard_twin.test.js:29:const _applyEndpointAveraging = eval('(' + avgMatch[0] + ')');
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
./tests/js/tougaard_twin.test.js:151:  const coreMatch = html.match(/function computeBackgroundCore\([\s\S]*?\n\}/);
./tests/js/tougaard_twin.test.js:152:  assert.ok(coreMatch, 'computeBackgroundCore not found in templates/index.html');
./tests/js/tougaard_twin.test.js:161:  const computeBackgroundCore = eval('(' + coreMatch[0] + ')');
./tests/js/tougaard_twin.test.js:172:  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
./tests/js/tougaard_twin.test.js:175:  const mainOut = computeBackgroundCore(be, intensity, {
./tests/js/tougaard_twin.test.js:180:  const fallbackOut = computeBackgroundCore(be, intensity, {
./tests/test_api_analyze.py:3:(spec §5A/§8).  STRICTLY ADDITIVE: /api/fit and the manual path are
./autofit/__init__.py:5:path (`fitting.run_fit`, `/api/fit`) is unchanged.  See
./templates/index.html.pre-audit:1900:function tougaardBackground(be, intensity) {
./templates/index.html.pre-audit:1937:    if (type === 'tougaard') return tougaardBackground(be, intensity);
./templates/index.html.pre-audit:1953:  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, inSub);
./templates/index.html.pre-audit:2803:    const resp = await fetch('/api/fit', {
./autofit/parity.py:37:    tougaard_background,
./autofit/parity.py:107:        bg_inner = tougaard_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
./docs/audit-2026-06-09.md:35:| F7  | P2       | Backend  | `/api/fit` has no upper bound on `n_perturb`; pure-Python Tougaard scales O(n²)         |
./docs/audit-2026-06-09.md:251:- `fitting.py:508-533` (`tougaard_background` — `for i in range(n)` in
./docs/audit-2026-06-09.md:268:auditor's own laptop. Independently, `tougaard_background` on an
./docs/audit-2026-06-09.md:275:gunicorn workers by sending a few `/api/fit` requests with a very large
./docs/audit-2026-06-09.md:333:POST /api/background {"session_id":"…","endpoint_avg":"not-a-number"}
./docs/audit-2026-06-09.md:395:POST /api/fit { … peaks: [{"id":"p1","constrain_to":"p1","splitting":0,"area_ratio":1,…}] }
./docs/audit-2026-06-09.md:503:- **`/api/fit` shape validation.** `fitting.run_fit` raises
./templates/index.html:4131:// tougaard_background (keep the two numerically in agreement; pinned by
./templates/index.html:4136:function tougaardBackground(be, intensity, nAvg) {
./templates/index.html:4146:  if (nAvg > 1) inW = _applyEndpointAveraging(inW, nAvg);
./templates/index.html:4196:function _applyEndpointAveraging(intensity, nAvg) {
./templates/index.html:4292:function computeBackgroundCore(be, intensity, settings) {
./templates/index.html:4314:    const avgIn = _applyEndpointAveraging(intensity, nAvg);
./templates/index.html:4322:    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
./templates/index.html:4323:    if (type === 'tougaard') return tougaardBackground(be, avgIn);
./templates/index.html:4336:  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
./templates/index.html:4337:  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
./templates/index.html:4344:  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
./templates/index.html:4365:// path calls computeBackgroundCore directly with source-tab settings.
./templates/index.html:4367:  return computeBackgroundCore(be, intensity, {
./templates/index.html:6642:  // Step 5: run /api/fit with AbortController + spinner.
./templates/index.html:6681:    const resp = await fetch('/api/fit', {
./templates/index.html:6796:    const resp = await fetch('/api/fit', {
./templates/index.html:7378:  return computeBackgroundCore(be, inten, settings);
./templates/index.html:12858:     STRICTLY ADDITIVE: the manual fit path (/api/fit, Run Fit, peak
./autofit/candidates.py:10:or the /api/fit contract.
./autofit/engine.py:297:    if bg is BackgroundType.TOUGAARD:
./autofit/engine.py:298:        from fitting import tougaard_background
./autofit/engine.py:299:        return tougaard_background(x, y)
./tests/autofit/test_progress_callback.py:8:manual /api/fit path never calls compare_models at all).
./tests/autofit/test_structural_fallback.py:11:registered deep regions are untouched, /api/fit and the manual path are
./docs/superpowers/plans/2026-04-25-la-lineshape-rename-and-true-la.md:13:3. **Migration (JavaScript only — NOT `parser.py`):** the `.fit.json` and `.proj.json` formats are loaded entirely in JS via `_applyFitJSON` (line 6566) and `_loadProjectJSON` (line 6632). Add a `_migrateLineshapeAliases(peaks)` helper called at the top of both functions. Maps `'LA'` → `'DSG_LA'` (frontend enum). Backend doesn't need migration because the `/api/fit` request is built fresh on each fit; if peak.shape is `'DSG_LA'` after migration, `peakToBackendSpec` emits `spec.shape = 'ds_g'` and the backend dispatch finds `_ds_g_dscore_gauss`. Both are equivalent because the math is identical and we keep all DS+G parameters identical to the old LA.
./docs/superpowers/plans/2026-04-25-la-lineshape-rename-and-true-la.md:88:| `app.py` | **NO CHANGES** (the `/api/fit` request shape isn't versioned by lineshape; renames pass through transparently) |
./docs/superpowers/plans/2026-04-25-la-lineshape-rename-and-true-la.md:1309:path the /api/fit endpoint uses, and confirm:
./docs/autofit/fable-weekend-marathon-RUN-THIS.md:20:- Work ONLY on the current feature branch. NEVER merge to main. NEVER deploy. NEVER git push --force. NEVER touch the existing /api/fit route or the manual-fit default path. The new engine is strictly additive and opt-in.
./docs/autofit/fable-weekend-marathon-RUN-THIS.md:45:- **Branch-only, no merge, no deploy, no touching `/api/fit`** → your live app is untouched no matter what it does.
./autofit/reference.py:6:the exact fit inputs the frontend would send to ``/api/fit``:
./docs/superpowers/plans/2026-04-07-manual-spline-background.md:11:**CRITICAL CONSTRAINT:** Do NOT modify any existing `shirleyBackground`, `smartBackground`, `linearBackground`, `tougaardBackground` functions, or any existing loading/parsing logic. Only ADD new code.
./docs/superpowers/plans/2026-04-07-manual-spline-background.md:105:A pure math function with no DOM dependencies. Add it near the existing background functions (after `tougaardBackground`, around line 2749).
./docs/superpowers/plans/2026-04-07-manual-spline-background.md:582:Find the `/api/fit` route in `app.py` (around line 346–404). Look for where `run_fit()` is called. Add `manual_bg` to the keyword arguments. Find the line that looks like:
./docs/superpowers/plans/2026-04-07-manual-spline-background.md:804:- [ ] `tougaardBackground` function: NOT modified
./docs/autofit/codex/full_window_crop_fix_recheck3_prompt.txt:72:   test file — no backend Python changes, no `/api/fit` involvement, no
./docs/autofit/codex/shape_switch_recheck_verdict_runA.md:7:1. Severity: none; file: n/a; concrete scenario: none found; fix: n/a. Verified `_shapeExportCols` is shape-gated, export row wiring uses `sc.gl/sc.alpha/sc.beta/sc.m` in unchanged header order, and the LACX stale-param scenario exports `caAlpha/caBeta/caM`. The pinned JS test discriminates against the old fallback chain and `node --test tests/js/shape_switch_roundtrip.test.js` passes 6/6. Original shape-switch scope remains confined to template/test changes; `runFit`, fitting math, `evalPeak/evalPeakArray`, backend `/api/fit`, save/load spread-copy, results, and backend-result application did not reveal a new stale inactive-param consumer.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-2.md:263:The previous helper read ip.params.area.value from the /api/fit response.
./docs/autofit/codex/fit_full_window_recheck_prompt.txt:85:   byte-identical for every existing caller; `/api/fit` / manual Run Fit
./docs/autofit/codex/analyze_ui_wiring_review_prompt.txt:13:   tests/test_api_analyze.py): STRICTLY ADDITIVE claim vs /api/fit;
./docs/autofit/codex/fe2p_roi_widen_review_prompt.txt:73:7. Manual Run Fit / `/api/fit` — confirm this change touches NEITHER
./docs/autofit/codex/full_window_crop_fix_verdict_round3_runA.md:29:apply). No backend Python or `/api/fit` path changes. Could not run pytest here (not
./docs/autofit/codex/fit_full_window_verdict_round1_runA.md:20:The bound override rule itself matches the requested design: primary slots only, `region == "unassigned"` gets full ROI, curated slots get only lowest lower / highest upper widened, and interior curated slots keep exact original windows. Linked slots excluded correctly. Starting center/amplitude estimates stay anchored to `slot.be_window`. Threading through `compare_models()` looked complete for parameter construction. `_detect_boundary_hits()` reads live lmfit parameter bounds. Manual Run Fit `/api/fit` not touched.
./docs/autofit/codex/self_citation_removal_review_prompt.txt:110:   /api/fit.
./docs/autofit/codex/fp_periodic_table_picker_review_prompt.txt:56:1. Manual Run Fit / `/api/fit` / the manual fitting path must be
./docs/autofit/codex/fp_periodic_table_picker_review_prompt.txt:61:   change to `/api/fit`'s request/response shape.
./docs/autofit/codex/region_provenance_honesty_recheck_prompt.txt:70:   `/api/fit`.
./docs/autofit/codex/full_window_crop_fix_verdict_round2_runA.md:29:could still pass. No backend Python or `/api/fit` changes. Could not run tests here
./docs/autofit/codex/tougaard_fix_verdict_runA.md:7:   Frontend Tougaard still bypasses `_applyEndpointAveraging`, while backend `/api/fit`, `/api/background`, and autofit parity paths apply `_apply_endpoint_averaging` before `tougaard_background`. With the new high-BE anchor this is no longer a small shape-only mismatch: endpoint averaging directly sets the anchor amplitude. Concrete scenario: descending 11-point window, `endpointAvg=2`, high-BE first point is a spike/outlier `10000`, second point and rest are `100`; frontend anchors Tougaard to `10000`, backend anchors to averaged `5050`. The committed JS twin test only calls `tougaardBackground` directly on the same raw array, so it does not catch the shipped caller contract mismatch.
./docs/autofit/codex/fit_full_window_review_prompt.txt:8:manual Run Fit / /api/fit, which this change must not touch) resolves a
./docs/autofit/codex/fit_full_window_review_prompt.txt:112:7. Manual Run Fit / `/api/fit` — confirm this change touches NEITHER
./docs/autofit/codex/tougaard_fix_verdict_runB.md:6:1. **MAJOR** [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4202), [fitting.py](/Users/skyefortier/xps-app/fitting.py:997), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1235) — Tougaard endpoint averaging is inconsistent between shipped frontend callers and backend callers. The UI disables `endpointAvg` for Tougaard, but stale values are still sent to `/api/background` and `/api/fit`; backend applies `_apply_endpoint_averaging(...)` before `tougaard_background`, while frontend preview/stack calls `tougaardBackground(...)` on raw intensity. Concrete failure: set endpoint avg to `10`, switch to Tougaard, with high-BE endpoint `500` and next 9 points `100`; frontend anchors Tougaard to `500`, backend anchors to averaged `140`. That breaks the claimed frontend/backend twin contract exactly at the new high-BE anchor, and current tests only compare direct function calls with unaveraged data.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:5:**Goal:** Add a single-action "Auto-Fit C1s Graphite" Actions-menu entry that produces a complete C1s fit and applies charge correction from the fitted graphite peak, calling the existing `/api/fit` endpoint exactly once.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:9:**Tech Stack:** Vanilla JS + inline HTML/CSS in `templates/index.html`; Python 3 (lmfit) backend via the existing `/api/fit` endpoint, unchanged.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:49:- **No** client-side fitting; every fit goes through `/api/fit`.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:70:3. **End-to-end Python harness** (Task 12) that POSTs a representative C1s spectrum + the auto-fit peak model to `/api/fit` and checks: success=true, graphite center within ±0.3 of 284.50, all peak amplitudes finite. Runs against the live `127.0.0.1:5000` server.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:805:  // backend spec before /api/fit. peakToBackendSpec doesn't read these; we
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:935://   json         : raw /api/fit response (already passed through applyBackendResult)
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:1109:  // Step 5: run /api/fit with AbortController + spinner.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:1122:    // Build /api/fit request matching runFit's shape (templates/index.html:4582-4592).
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:1144:    const resp = await fetch('/api/fit', {
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:1264:## Task 12: End-to-end Python harness (against running /api/fit)
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:1268:This validates that the auto-fit peak model, when posted to the running `/api/fit`, converges and lands graphite within bounds. It exercises the entire backend round-trip independent of the browser, catching backend-spec mistakes early.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md:1351:req = urllib.request.Request('http://127.0.0.1:5000/api/fit',
./docs/autofit/codex/stage2cal_review_verdict_runA.md:16:Checked rails: `/api/fit` and the manual least-squares path are untouched; the app diff is `/api/analyze` structural-fallback handling only. The F1 dominant detector body is not changed by the range. DS+G `beta` is HWHM in `fitting.py`, so `f_L = 2β` is correct. The committed calibration artifact supports q95 6.92646, FP@7 4.833%, and broad off-center 1/20. I did not run pytest per the read-only constraint.
./docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runA.md:10:- `/api/fit` and `runFit()` were not touched in the current worktree diff; `region_coverage_index()` is only wired through `/api/analyze/meta`.
./docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runA.md:11:- `practical` is additive on coverage entries; I did not see removed/renamed existing entry fields or `/api/fit` shape changes.
./docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runB.md:11:- Current dirty diff is scoped to `autofit/coverage_index.py`, `templates/index.html`, and tests. `/api/fit` is not touched by the replacement; `region_coverage_index()` is consumed by `/api/analyze/meta` in [app.py](/Users/skyefortier/xps-verify/app.py:858).
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md:68:the existing /api/fit endpoint (which already uses lmfit). If you believe a
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md:111:Use the existing /api/fit endpoint (which wraps lmfit). Do NOT implement any
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md:200:   - Invoke /api/fit. Match the shape of runFit().
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md:206:   - Enforce a frontend timeout using AbortController: if the /api/fit
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md:265:- No client-side fitting (all fitting goes through /api/fit)
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md:276:  /api/fit invocation (match runFit()), charge-correction state updates,
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md:389:`graphite_area / sum(all_peak_areas)` from the `/api/fit`
./docs/autofit/codex/full_window_crop_fix_recheck_prompt.txt:74:   test file — no backend Python changes, no `/api/fit` involvement,
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:23:DISPOSITION: templates/index.html computeBackgroundCore — BOTH Tougaard
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:25:endpoint-averaged intensity (`avgIn` / `_applyEndpointAveraging(inSub,
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:33:('computeBackgroundCore applies endpoint averaging for tougaard (both
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:34:branches)') extracts computeBackgroundCore from the shipped template,
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:36:tougaardBackground(be, _applyEndpointAveraging(intensity, 3)) on run A's
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:41:enabled)? Any OTHER shipped caller of tougaardBackground we missed?
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:49:tougaard_background anchor block; templates/index.html tougaardBackground
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:53:input). PIN: tests/test_tougaard_background.py::
./docs/autofit/codex/tougaard_fix_recheck_prompt.txt:63:fitting.py's tougaard_background NUMERICS must be byte-identical to
./docs/autofit/codex/findpeaks_unit3_verdict_round2.md:18:   `git show fa085f4 --stat` touches only `autofit/coverage_index.py`, `templates/index.html`, the three test files, `docs/autofit/PROGRESS.md`, and archived `docs/autofit/codex/` artifacts. No `app.py`, manual Run Fit, `/api/fit`, core math, or reviewed-apply gate drift.
./docs/autofit/codex/findpeaks_unit3_verdict_round2.md:42:   `git show fa085f4 --stat` / name-only touches only `autofit/coverage_index.py`, `templates/index.html`, the three test files, `docs/autofit/PROGRESS.md`, and archived `docs/autofit/codex/` artifacts. No drift into `app.py`, `/api/fit`, manual Run Fit, core math, or the honesty/reviewed-apply gate.
./docs/autofit/codex/tooltip_markup_leak_verdict_round1_runB.md:28:frontend change: no backend Python, `/api/fit`, math, or candidate-selection code
./docs/autofit/codex/full_window_crop_fix_verdict_round1_runA.md:25:Python/`/api/fit` touched. Provenance stamp (`autoSuggested`/`verified`) and toast
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md:9:**Tech Stack:** Vanilla JS in `templates/index.html`; Python 3 (lmfit) backend via `/api/fit`, unchanged.
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md:169:// Compute graphite's area fraction from a /api/fit response and decide
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md:393:`graphite_area / sum(all_peak_areas)` from the `/api/fit`
./docs/autofit/codex/findpeaks_unit1_review_prompt.txt:11:strictly additive — manual Run Fit, POST /api/fit, the core analysis math,
./docs/autofit/codex/findpeaks_unit3_recheck_prompt.txt:107:   /api/fit, the core analysis math, or the honesty/reviewed-apply gate,
./docs/autofit/codex/self_citation_removal_recheck_prompt.txt:80:   autofit/methods/*.py, fitting.py, or /api/fit changes.
./docs/autofit/codex/fit_full_window_verdict_round3_runA.md:14:- Prior invariants still hold: curated interiors remain exact, linked offsets untouched, initial center/amplitude estimation uses original `be_window`, stability acceptance uses widened bounds, `/api/fit` and manual Run Fit untouched, `_detect_boundary_hits()` reads live lmfit bounds.
./docs/autofit/codex/stage2cal_recheck_prompt.txt:40:Also confirm the fix commits touch no manual-fit or /api/fit code.
./docs/autofit/codex/reference_bridge_mechanism_review_prompt.txt:102:   `/api/fit`.
./docs/autofit/codex/stage2_review1_verdict.md:39:Manual-fit path check: `app.py` and `fitting.py` are unchanged vs `main`; I did not find a silent `/api/fit` or `fitting.run_fit` code change. Template diff is confined to the intended `analysis` save/load additions and keeps v3.
./docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runB.md:13:- `/api/fit` current route remains the manual `fitting.run_fit(...)` path at [app.py](/Users/skyefortier/xps-verify/app.py:740), while `region_coverage_index()` is only pulled into `/api/analyze/meta` at [app.py](/Users/skyefortier/xps-verify/app.py:858).
./docs/autofit/codex/shape_switch_recheck_prompt.txt:33:evalPeak/evalPeakArray, or /api/fit. Look for any OTHER non-shape-gated
./docs/autofit/codex/fe2p_roi_widen_verdict_runA.md:14:Scope checks also look right. Singlets are effectively exempt because their single derived label matches the sourced orbital; fully-covered non-curated doublets I found (`Cu 2p`, `Nb 3d`) satisfy `component_labels <= covered`, so they keep the expected-region union. I found no shrink path across sourced records. The changed commit touches only `autofit/coverage_index.py`, `tests/autofit/test_coverage_index.py`, and the review prompt doc; `/api/fit` remains separate, while `coverage_index` is imported only by `/api/analyze/meta`: [app.py](/Users/skyefortier/xps-verify/app.py:738), [app.py](/Users/skyefortier/xps-verify/app.py:858). The UI copies that meta ROI into Find Peaks inputs only on single-region selection: [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13290).
./docs/autofit/codex/candidate_pool_review_prompt.txt:48:1. /api/fit and the manual Run Fit path untouched (grep the diff).
./docs/autofit/codex/full_window_crop_fix_verdict_round2_runB.md:15:   No backend Python or `/api/fit` changes present.
./docs/autofit/codex/stage2cal_recheck_verdict_runA.md:17:The fix commits do not touch manual fit or `/api/fit` files; the relevant diffs list only `autofit/candidates.py`, `autofit/engine.py`, docs, and tests. `/api/fit` remains the manual `fitting.run_fit` endpoint, with autofit analyze separated below it: [app.py](/Users/skyefortier/xps-verify/app.py:457), [app.py](/Users/skyefortier/xps-verify/app.py:574).
./docs/autofit/codex/fp_periodic_table_picker_recheck_prompt.txt:45:   flag as NO-GO) still holds on the current disk state — /api/fit
./docs/autofit/codex/fit_full_window_verdict_round2_runA.md:14:Run 2's curated-bound fix (min/max wrapping) is correct: cannot narrow or invert the touched side. Interior curated slots and linked slots remain untouched. Run 1's direct orphaning bug is mostly dispositioned: `run_stability_analysis()` computes bound overrides once for matching, and refit params are built with equivalent deterministic overrides. The new stability regression test does call `run_stability_analysis()` directly. Flag threading, `/api/fit` isolation, and `_detect_boundary_hits()` all confirmed correct.
./docs/autofit/codex/shape_switch_review_prompt.txt:26:/api/fit / the backend. Confirm the diff (git show d5c3222) is confined to
./docs/autofit/codex/fwhm_cap_recheck_prompt.txt:63:flagged); routes to CONDITIONAL; strictly additive; /api/fit + manual path
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:8:`computeBackgroundCore` now averages Tougaard input in both frontend branches:
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:11:- Main sliced path uses `_applyEndpointAveraging(inSub, nAvg)`: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4214)
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:12:- Backend parity remains: `/api/fit` and `/api/background` both call `tougaard_background(..., _apply_endpoint_averaging(...))`: [fitting.py](/Users/skyefortier/xps-app/fitting.py:1002), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1240)
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:25:Comments now state the real guard behavior and signed negative-count policy at both sites: [fitting.py](/Users/skyefortier/xps-app/fitting.py:587), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4053). The new Python pin matches the documented `[100,0,0,0]` behavior: [tests/test_tougaard_background.py](/Users/skyefortier/xps-app/tests/test_tougaard_background.py:131).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:27:I could not run pytest because the read-only sandbox has no usable temp directory, but I executed the extracted `tougaard_background` body directly and confirmed `[100,0,0,0] -> [0,0,0,0]`. I also checked the mixed-sign cancellation edge: it returns a signed unanchored correlation, consistent with the “negative counts pass through signed; no clamping” policy.
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:9:- Fallback full-range path now computes `avgIn = _applyEndpointAveraging(intensity, nAvg)` and passes it to Tougaard at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184) and [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4193).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:10:- Main sliced path now passes `_applyEndpointAveraging(inSub, nAvg)` to Tougaard at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4214).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:13:- Active shipped frontend callers funnel through `computeBackgroundCore`; `computeBackground` is only a DOM wrapper at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4236). Flask serves `templates/index.html` at [app.py](/Users/skyefortier/xps-app/app.py:214).
./docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:22:- The pin covers the concrete `[100, 0, 0, 0]` case at [tests/test_tougaard_background.py](/Users/skyefortier/xps-app/tests/test_tougaard_background.py:132).
./docs/autofit/codex/fwhm_cap_recheck_verdict_runA.md:7:1. Severity: none; file: n/a; scenario: no new issue found. Verified final-primary post-stability peg re-check at `autofit/engine.py:1962-1982`, shape endpoint disposition at `autofit/engine.py:623-639`, width-cap/conditional routing at `autofit/engine.py:2002-2027` and `autofit/engine.py:1426-1451`, bfix lineage copy at `autofit/engine.py:2132-2154`, and `/api/fit` remains manual-path only at `app.py:457-558`. Fix: n/a. Note: pinned pytest execution could not start because the read-only sandbox has no usable temp directory.
./docs/autofit/codex/fwhm_cap_review_prompt.txt:16:zero regressions, don't touch /api/fit or the manual path.
./docs/autofit/codex/fwhm_cap_review_prompt.txt:80:4. STRICTLY ADDITIVE / no regression. /api/fit + fitting.py::run_fit
./docs/autofit/codex/analyze_ui_verdicts.md:19:/api/fit additive, corrected-frame convention consistency, lineshape
./docs/autofit/codex/stage2_review_prompt.txt:5:Scope of the stage under review (all strictly additive; the existing manual-fit path /api/fit + fitting.run_fit must be byte-identical to main):
./docs/autofit/codex/tougaard_fix_review_prompt.txt:9:- fitting.py: ONLY tougaard_background (docstring + body). Nothing else in
./docs/autofit/codex/tougaard_fix_review_prompt.txt:10:  fitting.py, /api/fit, or the autofit engine may have changed.
./docs/autofit/codex/tougaard_fix_review_prompt.txt:11:- templates/index.html: ONLY the tougaardBackground JS function (+ leading
./docs/autofit/codex/tougaard_fix_review_prompt.txt:13:- New tests: tests/test_tougaard_background.py, tests/js/tougaard_twin.test.js.
./docs/autofit/codex/tougaard_fix_review_prompt.txt:59:4. TESTS. tests/test_tougaard_background.py (5 tests) and
./docs/autofit/codex/tougaard_fix_review_prompt.txt:70:5. CALLERS. fitting.py dispatches tougaard_background at the /api/background
./docs/autofit/codex/tougaard_fix_review_prompt.txt:71:   and /api/fit background paths (grep "tougaard"); autofit reaches it only
./docs/autofit/codex/tougaard_fix_review_prompt.txt:72:   via BackgroundType.TOUGAARD (autofit/engine.py) and autofit/parity.py.
./docs/autofit/codex/tougaard_fix_review_prompt.txt:73:   The frontend calls tougaardBackground at two sites (~line 4162/4180).
./docs/autofit/codex/tougaard_fix_review_prompt.txt:76:   _applyEndpointAveraging) composes sensibly with the new high-BE anchor.
./docs/autofit/codex/fe2p_roi_widen_verdict_runB.md:16:Scope check: the committed ROI fix touches only `autofit/coverage_index.py`, the coverage-index test, and a review prompt doc. `/api/fit` remains the separate manual route at [app.py](/Users/skyefortier/xps-verify/app.py:738), and this change feeds only `/api/analyze/meta` coverage. Note: the current worktree has additional uncommitted `practical`-flag edits in the same files; they are separate from the committed ROI fix and also do not touch `/api/fit`.
./docs/autofit/codex/c1s_multienv_fix_review_prompt.txt:17:work: strictly additive (do NOT touch /api/fit or the manual path), no
./docs/autofit/codex/c1s_multienv_fix_review_prompt.txt:97:   - /api/fit and fitting.py::run_fit (the manual path) are untouched.
./docs/autofit/codex/stage2_calibration_review_prompt.txt:40:a. /api/fit + manual Run Fit path untouched across ALL five commits
./docs/autofit/codex/phaseD_unit3_fallback_prompt.txt:65:- Confirm /api/fit and the manual path are untouched by all commits in
./docs/autofit/codex/region_provenance_honesty_review_prompt.txt:90:   `/api/fit`.
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:12:- fitting.py: ONLY tougaard_background (signature, docstring, body).
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:18:- templates/index.html: ONLY the tougaardBackground JS function (+ its
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:19:  leading comment). computeBackgroundCore and _applyEndpointAveraging are
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:20:  unmodified — their two call sites into tougaardBackground still use the
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:22:- tests/test_tougaard_background.py, tests/js/tougaard_twin.test.js.
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:23:- No changes to /api/fit's contract, autofit/methods/*.py, or peak
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:28:The previous tougaard_background computed the idealized integral
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:138:  real tougaardBackground out of templates/index.html rather than a
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:141:CALLERS. fitting.py dispatches tougaard_background at the /api/background
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:142:and /api/fit background paths; autofit reaches it via BackgroundType.TOUGAARD
./docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:145:frontend calls tougaardBackground at ~2 sites inside computeBackgroundCore.
./docs/autofit/codex/stage2cal_recheck_verdict_runB.md:17:Commit scope check: the fix range after the archived verdicts (`dd877ec..HEAD`) touches only `autofit/candidates.py`, `autofit/engine.py`, `docs/autofit/PROGRESS.md`, `docs/autofit/codex/stage2cal_recheck_prompt.txt`, and `tests/autofit/test_stage2_completeness.py`; no `app.py`, `/api/fit`, templates/static UI, manual-fit path, or `fitting.py` changes are in that fix range.
./docs/autofit/codex/tooltip_markup_leak_review_prompt.txt:85:   changed, no change to `/api/fit`, no change to any analysis math or
./docs/autofit/codex/fit_full_window_verdict_round2_runB.md:13:- Original invariants hold: linked slots excluded, offsets untouched, starting center/amplitude use original `be_window`, default False additive, `/api/fit` not wired, `_detect_boundary_hits()` reads live bounds.
./docs/autofit/codex/full_window_crop_fix_verdict_round4_runA.md:22:`autofit/engine.py`, `autofit/methods/*.py`, `fitting.py`, `/api/fit`, peak math,
./docs/autofit/codex/c1s_badge_fix_review_prompt.txt:111:   /api/fit.
./docs/autofit/codex/full_window_crop_fix_verdict_round3_runB.md:26:optional chaining). No backend Python, `/api/fit`, peak position/width/chemical-anchor
./docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runA.md:12:The rest of run 1's verified section still holds: `/api/fit` remains separate at [app.py](/Users/skyefortier/xps-verify/app.py:738), and `region_coverage_index()` is wired only into `/api/analyze/meta` at [app.py](/Users/skyefortier/xps-verify/app.py:858). `practical` is additive in [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:76). Selection remains Set-based via `_fpNextSelection`/`_fpToggleRegion`, and `runFindPeaks()` submits `Array.from(_fpRegionsSelected)` rather than scraped DOM state at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13671). Tier meaning is not color-only: legend labels, chip tags, titles, and tier notes all carry text.
./docs/autofit/codex/tooltip_markup_leak_verdict_round1_runA.md:30:backend Python, `/api/fit`, `/api/analyze`, analysis math, or candidate-selection
./docs/autofit/codex/fit_full_window_recheck2_prompt.txt:87:   byte-identical for every existing caller; `/api/fit` / manual Run Fit
./docs/autofit/codex/candpool_review_verdict_runB.md:8:Non-finding checks: `/api/fit`, `fitting.py`, and frontend Run Fit are absent from the candidate-generation commit diff; `enable_preseed=False` leaves `candidate_pool` null; descending grids are normalized in detector and pool; residual merge only mutates payload post-fit; `autofit/` has no hard-coded 278/279/280 detector logic beyond an existing comment.
./docs/autofit/codex/full_window_crop_fix_recheck2_prompt.txt:73:   test file — no backend Python changes, no `/api/fit` involvement, no
./docs/autofit/codex/plain_english_pass_review_prompt.txt:9:from manual Run Fit / /api/fit which this change must not touch) had
./docs/autofit/codex/fit_full_window_verdict_round3_runB.md:12:- Prior invariants rechecked: curated interior slots unchanged, linked slots excluded, offset ranges not widened, starting center/amplitude use `slot.be_window`, stability builds and matches against the same widened accept bounds, widening uses min/max so it cannot narrow or invert, `/api/fit` still calls `fitting.run_fit()` directly, `_detect_boundary_hits()` reads live lmfit bounds.
./docs/autofit/codex/stage2cal_review_verdict_runB.md:24:Read-only verification only: I did not run pytest. The committed calibration artifact supports H0 q95 ≈ 6.93, FP@7 = 29/600 = 4.83%, and broad off-center = 1/20. `/api/fit` and manual Run Fit files were not touched; `app.py` changes are confined to `/api/analyze`. New held-out ds7/ds8/Fe files are untracked, while tests only commit numeric gates.
./docs/autofit/codex/refpop_unit1_bridge_prompt.txt:68:test_reference_bridge.py (new), PROGRESS.md. /api/fit, the manual path,
./docs/autofit/codex/fit_full_window_verdict_round1_runB.md:14:The intended outer-envelope logic is otherwise present: primary slots only, `region == "unassigned"` gets full ROI, curated interior slots keep both original bounds exactly in the normal wider-ROI case. Linked slots excluded. Starting center/amplitude estimates anchored to original `slot.be_window`. No missed fresh-parameter call inside `compare_models`. Default behavior additive. `_detect_boundary_hits()` reads live bounds. Manual `/api/fit` untouched.
./docs/autofit/PROGRESS.md:7:**Rails honored:** no merge to main, no deploy, no force-push, `/api/fit` and the manual-fit
./docs/autofit/PROGRESS.md:32:| Tougaard background bug-fix (C constant + BE-order + amplitude anchor) | DONE | ✅ 5 py + 4 js tests | `fitting.py::tougaard_background` + JS twin `tougaardBackground`: C was shipped SQUARED (1643² ≈ 2.7e6 eV², kernel max ~949 eV → flat/zero bg on real windows) → corrected to 1643 eV² (Tougaard 1988, SIA 11, 453); one-sided sum made order-robust (descending normalization, shirley-mirror); degenerate trailing rescale (K(0)=0 ⇒ scale ≡ raw trailing counts) replaced by the high-BE-edge anchor. Cross-language parity pinned at 1e-9. Codex checkpoint ×2: NO-GO ×2 (same MAJOR: frontend callers bypassed endpoint averaging → anchor mismatch; + 1 MINOR comment honesty) → all fixed same-session + caller-level pin; re-check ×2 **GO ×2** — unit review-complete. |
./docs/autofit/PROGRESS.md:1053:**Backend** (`app.py`, strictly additive — `/api/fit` and the manual path
./docs/autofit/PROGRESS.md:1156:math; the autofit engine only reaches it via `BackgroundType.TOUGAARD` —
./docs/autofit/PROGRESS.md:1159:implementations: `fitting.py::tougaard_background` and its JS twin
./docs/autofit/PROGRESS.md:1160:`tougaardBackground` in `templates/index.html` (kept in numerical
./docs/autofit/PROGRESS.md:1200:4. **Tests** (`tests/test_tougaard_background.py`, 5;
./docs/autofit/PROGRESS.md:1214:0 failures**; JS suite 52/52. Rails: branch-only, `/api/fit` and the
./docs/autofit/PROGRESS.md:1216:through the existing `BackgroundType.TOUGAARD` dispatch). Codex
./docs/autofit/PROGRESS.md:1235:   `computeBackgroundCore` Tougaard branches (sliced + fallback) now pass
./docs/autofit/PROGRESS.md:1236:   `_applyEndpointAveraging(...)` exactly like the Shirley family, and
./docs/autofit/PROGRESS.md:1239:   a new caller-level JS test that extracts `computeBackgroundCore` from
./docs/autofit/PROGRESS.md:1241:   `tougaardBackground(be, averaged)` (watched fail first).
./docs/autofit/PROGRESS.md:1255:calls tougaard_background WITHOUT averaging, but it does so for EVERY
./docs/autofit/PROGRESS.md:1360:the payload. Unparseable/unknown regions still 400. `/api/fit`, the
./docs/autofit/PROGRESS.md:1800:Units F1/F2/F3 landed (engine + IC method, strictly additive; `/api/fit`
./docs/autofit/PROGRESS.md:1959:**Fix (engine + IC method, strictly additive; `/api/fit` and the manual
./docs/autofit/PROGRESS.md:2044:that `/api/fit` stays manual-path-only.  **FWHM-CAP UNIT REVIEW-COMPLETE.**
./docs/autofit/PROGRESS.md:2055:`evalPeak`/`evalPeakArray`, or `/api/fit` — only the shape-switch handler +
./docs/autofit/PROGRESS.md:2101:fallback, the switch fix stays scoped (runFit / evalPeak / `/api/fit` /
./docs/autofit/PROGRESS.md:2152:selection judges.  `/api/fit` and the manual path untouched; the reviewed
./docs/autofit/PROGRESS.md:2240:the rails: `/api/fit` + manual path untouched, `enable_preseed=False`
./docs/autofit/PROGRESS.md:2522:the fix commits touching no manual-fit//api/fit code.
./docs/autofit/PROGRESS.md:2528:additive — manual Run Fit, `/api/fit`, the analysis math, and the
./docs/autofit/PROGRESS.md:2831:touches neither `/api/fit` nor the manual fit path. Archived at
./docs/autofit/PROGRESS.md:3003:Manual Run Fit / `/api/fit` untouched (confirmed: `region_coverage_index`
./docs/autofit/PROGRESS.md:3005:`/api/fit` never imports `compare_models`).
./docs/autofit/PROGRESS.md:3412:  `/api/fit`.
./docs/autofit/PROGRESS.md:3815:`/api/fit`, `autofit/engine.py`, or `autofit/methods/*.py` anywhere in
./docs/autofit/codex/full_window_crop_fix_review_prompt.txt:91:4. Confirm this change does NOT touch manual Run Fit, `/api/fit`, any

exec
/bin/zsh -lc "nl -ba tests/test_tougaard_background.py | sed -n '1,340p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '500,640p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   636	    amplitude: float,
   637	    center: float,
   638	    fwhm: float,
   639	    alpha: float,
   640	    beta: float,

 succeeded in 0ms:
     1	"""Tougaard universal-cross-section background — correctness pins.
     2	
     3	Pins the 2026-07-04 bug-fix (branch feature-autofit-stage2):
     4	
     5	1. The universal-cross-section constant C was shipped SQUARED
     6	   (``C = 1643.0**2`` ≈ 2.7e6 eV² instead of C = 1643 eV²), a
     7	   transcription slip of "C = 1643 eV²".  The loss kernel
     8	   K(T) = B·T/(C + T²)² peaks at T = sqrt(C/3): ≈ 23.4 eV with the
     9	   correct constant, ≈ 948.6 eV with the squared one — so over any real
    10	   ~20 eV XPS window the shipped "Tougaard" background was essentially
    11	   flat/zero.  Reference: S. Tougaard, Surf. Interface Anal. 11, 453
    12	   (1988) — two-parameter universal cross-section, B = 2866 eV²,
    13	   C = 1643 eV².
    14	
    15	2. The one-sided loss sum (j >= i) is only physical on a DESCENDING
    16	   binding-energy grid; ascending input silently produced a background
    17	   accumulating on the wrong side (same bug class as the np.interp
    18	   descending-grid registration bug).  The function now normalizes to
    19	   descending internally and flips the result back, mirroring
    20	   shirley_background's ascending normalization.
    21	
    22	3. The trailing-endpoint rescale was degenerate: K(0) = 0 makes the
    23	   trailing background sample identically zero, so the zero-guard always
    24	   fired and the "match the trailing endpoint" scale was in fact
    25	   "multiply by the trailing raw counts".  The normalization now anchors
    26	   the background to the measured intensity at the HIGH-BE edge of the
    27	   window (the standard practical Tougaard criterion: B is effectively
    28	   fitted so the background meets the spectrum above the peak).
    29	
    30	No pre-existing test or fixture pinned the old (wrong) Tougaard output
    31	(verified by grep over tests/, tests/autofit/, docs/autofit/inventory/,
    32	scripts/ on 2026-07-04), so nothing needed regeneration.
    33	"""
    34	
    35	import numpy as np
    36	
    37	from fitting import tougaard_background
    38	
    39	
    40	def _synthetic_spectrum(descending: bool = True):
    41	    """Realistic C 1s-like region: baseline + Gaussian peak + loss step."""
    42	    x = np.linspace(295.0, 280.0, 151)  # descending BE, dx = 0.1 eV
    43	    y = (
    44	        100.0
    45	        + 5000.0 * np.exp(-0.5 * ((x - 287.0) / 0.8) ** 2)
    46	        + 400.0 / (1.0 + np.exp(-(287.0 - x)))  # step rising toward high BE
    47	    )
    48	    if not descending:
    49	        return x[::-1].copy(), y[::-1].copy()
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
/bin/zsh -lc "nl -ba tests/js/tougaard_twin.test.js | sed -n '1,260p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '4128,4350p'" in /Users/skyefortier/xps-verify
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

 succeeded in 0ms:
  4128	}
  4129	
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

codex
A couple of important details are emerging. The commit itself doesn’t change `computeBackgroundCore`; its existing Tougaard calls already pre-average externally and still call `tougaardBackground(...)` with two arguments. The new optional `nAvg` path inside the JS/Python functions is therefore compatibility surface, not currently exercised by those call sites.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_tougaard_background.py' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: pytest

exec
/bin/zsh -lc 'git diff --check 3d9ff54''^ 3d9ff54' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0hTgQ1Q2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sYjf9KAK' (errno=Operation not permitted)

exec
/bin/zsh -lc 'node --test tests/js/tougaard_twin.test.js' in /Users/skyefortier/xps-verify
 succeeded in 159ms:
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 1 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 13.809682
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 2 - ascending and descending BE input give the identical background
  ---
  duration_ms: 0.668568
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 3 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.361398
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 4 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 2.716166
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 5 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 1.762217
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 6 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 0.75061
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
# duration_ms 115.775379

codex
`node --test tests/js/tougaard_twin.test.js` passes 6/6. The `pytest` entrypoint is not installed on `PATH`, so I’m checking whether the project’s Python environment exposes it via `python -m pytest` or a local venv before falling back to static execution.
exec
/bin/zsh -lc 'python -m pytest -q -p no:cacheprovider tests/test_tougaard_background.py' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "rg --files -g 'pyproject.toml' -g 'requirements*.txt' -g 'pytest.ini' -g 'tox.ini' -g 'venv/bin/pytest' -g '.venv/bin/pytest' -g 'package.json'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
requirements-dev.txt
requirements.txt

codex
There is no runnable pytest in this sandbox (`pytest`, `python`, and `python3 -m pytest` all fail; `python3` exists but lacks the module). I’ll still use `python3` for small direct numeric probes if dependencies are importable, and I’ll keep those separate from test-run claims.
exec
/bin/zsh -lc "sed -n '1,220p' requirements-dev.txt && sed -n '1,220p' requirements.txt" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
# Test/development dependencies (runtime deps live in requirements.txt).
# The browser tests (tests/test_browser_*.py, tests/autofit/test_browser_*)
# additionally need a Playwright Chromium build:  playwright install chromium
# They self-skip when playwright/gunicorn/chromium are absent.
pytest>=9.0
playwright>=1.60
# XPS Peak Fitting – Python dependencies
# Install: pip install -r requirements.txt

flask>=3.0,<4
werkzeug>=3.0
gunicorn>=22.0

# Numerics & fitting
numpy>=1.26
scipy>=1.13
lmfit>=1.3

# File parsing
pandas>=2.2
openpyxl>=3.1       # .xlsx read/write

# Reference-data validation (data/xps/ against schema.json)
jsonschema>=4.21

# Optional – uncomment if you need CORS (e.g. separate frontend dev server)
# flask-cors>=4.0
olefile
gunicorn

exec
/bin/zsh -lc 'ls -la' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
total 560
drwxr-xr-x   29 skyefortier  staff    928 Jul 17 15:35 .
drwxr-xr-x+  74 skyefortier  staff   2368 Jul 17 15:50 ..
-rw-r--r--    1 skyefortier  staff     61 Jul 10 15:28 .git
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 .github
-rw-r--r--    1 skyefortier  staff    111 Jul 10 15:28 .gitignore
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 .impeccable
drwxr-xr-x    6 skyefortier  staff    192 Jul 10 19:53 .pytest_cache
drwxr-xr-x   27 skyefortier  staff    864 Jul 16 12:39 .stage9
-rw-r--r--    1 skyefortier  staff  20250 Jul 10 15:28 CLAUDE.md
-rw-r--r--    1 skyefortier  staff   2656 Jul 10 15:28 DEPLOY.md
-rw-r--r--    1 skyefortier  staff   8758 Jul 10 15:28 DESIGN.md
-rw-r--r--    1 skyefortier  staff   2735 Jul 10 15:28 PRODUCT.md
drwxr-xr-x    7 skyefortier  staff    224 Jul 17 15:35 __pycache__
-rw-r--r--    1 skyefortier  staff  52614 Jul 13 11:59 app.py
drwxr-xr-x   20 skyefortier  staff    640 Jul 17 15:33 autofit
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 data
drwxr-xr-x    6 skyefortier  staff    192 Jul 10 15:28 docs
-rw-r--r--    1 skyefortier  staff  55991 Jul 17 15:35 fitting.py
-rw-r--r--    1 skyefortier  staff  19994 Jul 10 15:28 parser.py
-rw-r--r--    1 skyefortier  staff    319 Jul 10 15:28 requirements-dev.txt
-rw-r--r--    1 skyefortier  staff    446 Jul 10 15:28 requirements.txt
drwxr-xr-x   22 skyefortier  staff    704 Jul 10 21:01 scripts
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 static
drwxr-xr-x    4 skyefortier  staff    128 Jul 17 15:30 templates
drwxr-xr-x   38 skyefortier  staff   1216 Jul 17 15:30 tests
drwxr-xr-x  159 skyefortier  staff   5088 Jul 17 15:49 uploads
-rw-r--r--    1 skyefortier  staff   6062 Jul 10 15:28 vgd_parser.py
-rw-r--r--    1 skyefortier  staff  68252 Jul 10 15:28 xps-fitting-tool.html
-rw-r--r--    1 skyefortier  staff  18124 Jul 10 15:28 xps_reference.py

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"import numpy as np; from fitting import tougaard_background; print('import ok'); print(tougaard_background(np.array([291.,290.,289.,288.]), np.array([100.,0.,0.,0.])))\"" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"import numpy as np; from fitting import tougaard_background; x=np.linspace(10.,0.,11); y=np.array([100.,90.,80.,70.,60.,50.,40.,30.,20.,10.,200.]); bg=tougaard_background(x,y); print(np.array2string(bg, precision=6)); print('min', bg.min(), 'max', bg.max(), 'netminmax', (y-bg).min(), (y-bg).max())\"" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"import numpy as np; from fitting import tougaard_background; x=np.linspace(740.,700.,600); y=7000-50*np.arange(600)/599; bg=tougaard_background(x,y); print('edge', bg[0],y[0],bg[-1],y[-1]); print('minmax', bg.min(),bg.max()); print('sample', np.array2string(bg[::100], precision=3))\"" in /Users/skyefortier/xps-verify
 exited 1 in 136ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

 exited 1 in 133ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

 exited 1 in 136ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

codex
Direct Python import is blocked by missing runtime deps (`lmfit`), so I can’t execute the backend function in this environment. I’m switching numeric probes to the extracted JS twin where possible, and I’m continuing the static checks against the actual commit diff.
exec
/bin/zsh -lc 'git diff --unified=0 3d9ff54''^ 3d9ff54 -- fitting.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZG2xWKZE' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3ATywclx' (errno=Operation not permitted)
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

exec
/bin/zsh -lc 'git diff --unified=0 3d9ff54''^ 3d9ff54 -- templates/index.html' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-D7wMLTeu' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-rrux8M7q' (errno=Operation not permitted)
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
/bin/zsh -lc 'git diff --name-only 3d9ff54''^ 3d9ff54 -- app.py autofit/engine.py autofit/methods parser.py xps_reference.py data static docs/autofit/inventory scripts tests/autofit '"'*.json' '*.proj.json' '*.proj.zip'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6h2I3NQs' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-i0Go4bpR' (errno=Operation not permitted)

codex
The zero-context diff confirms the scope claim more tightly: no hunks appear outside `tougaard_background` in `fitting.py`, and no hunks appear outside `tougaardBackground` in `templates/index.html`. The checked `app.py`, `autofit/engine.py`, `autofit/methods`, and fixture glob diff is empty for this commit.
exec
/bin/zsh -lc "rg --files tests tests/autofit docs/autofit/inventory scripts docs uploads data | rg -i '\\.(json|proj\\.json|proj\\.zip|spec\\.json|fit\\.json)"'$'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/inventory/reference_fits_inventory.json
docs/autofit/inventory/replicate_noise_survey.json
docs/autofit/inventory/acquisition_exhaustion.json
data/xps/elements-main.json
data/xps/sources.json
data/xps/fit-physics.json
data/xps/auger-lines.json
data/xps/elements-lanthanides.json
data/xps/elements-machine.json
data/xps/elements-machine.provenance.json
data/xps/schema.json
data/xps/elements-actinides.json
data/xps/elements-machine.skipped.json
data/xps/legacy/chemical-states.json
data/xps/legacy/schema.json
data/xps/legacy/corrections.json
data/xps/legacy/survey-lines.json
tests/fixtures/curated_records_snapshot.json
tests/fixtures/xps_legacy_snapshot.json
tests/fixtures/machine_records_snapshot.json
tests/autofit/fixtures/c1s_battery_expected.json
tests/autofit/fixtures/u4f_battery_expected.json
tests/autofit/fixtures/b1s_battery_expected.json
tests/autofit/fixtures/example_cited_values.json
tests/autofit/fixtures/cl2p_battery_expected.json
uploads/3ee1dcee-2f3a-4c83-a33e-ce349f9dd4e8.job.json
tests/autofit/fixtures/c1s_battery_expected.json
tests/autofit/fixtures/u4f_battery_expected.json
tests/autofit/fixtures/b1s_battery_expected.json
tests/autofit/fixtures/example_cited_values.json
tests/autofit/fixtures/cl2p_battery_expected.json
docs/autofit/inventory/reference_fits_inventory.json
docs/autofit/inventory/replicate_noise_survey.json
docs/autofit/inventory/acquisition_exhaustion.json
uploads/58ef8f7c-8e65-4581-a1d5-b342298d1425.job.json
uploads/a0499bc7-9313-4388-8408-d6e42386862c.job.json
docs/autofit/test_data/B4C-UCl4.proj.zip
docs/autofit/test_data/Cl2p_projfit_test.proj.zip
docs/autofit/test_data/8-JT Graphite.proj.zip
docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json
docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
docs/autofit/test_data/UCl4_on_graphite.proj.zip
docs/autofit/test_data/4-GTA UCl4-BN.proj.zip

exec
/bin/zsh -lc "rg -n -i \"tougaard\" tests tests/autofit docs/autofit/inventory scripts docs --glob '*.py' --glob '*.js' --glob '*.json' --glob '*.md' --glob '*.txt' --glob '*.proj.json' --glob '*.spec.json' --glob '*.fit.json'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/audit-2026-06-09.md:35:| F7  | P2       | Backend  | `/api/fit` has no upper bound on `n_perturb`; pure-Python Tougaard scales O(n²)         |
docs/audit-2026-06-09.md:245:### F7 — No upper bound on `n_perturb`; pure-Python Tougaard is O(n²)
docs/audit-2026-06-09.md:251:- `fitting.py:508-533` (`tougaard_background` — `for i in range(n)` in
docs/audit-2026-06-09.md:268:auditor's own laptop. Independently, `tougaard_background` on an
docs/audit-2026-06-09.md:271:as the ROI with `method=tougaard` is many seconds to many minutes per
docs/audit-2026-06-09.md:276:`n_perturb` (or a Tougaard background over a large ROI). With four
docs/audit-2026-06-09.md:283:the Tougaard loop with `numpy` (the kernel is a function of `|i - j|`,
docs/audit-2026-06-09.md:526:3. **F7** (`n_perturb` / Tougaard DoS). Quick to cap; protects the
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
docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md:22:XPS spectra ride on a curved background (Shirley, Tougaard, etc.). In the current view, peak fills are drawn on top of this curved baseline, which makes peaks look "wavy" and forces the user to mentally subtract the background to judge fit quality. Background-subtracted view is the standard presentation in XPS publications and is significantly easier to read for both fit-quality assessment and visual communication.
docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md:58:The disabled state activates whenever the tab's background method is "None" or no background data is available. When the user changes the background method to a real one (Shirley, Tougaard, Smart), the pill re-enables and remembers its previous active/inactive state.
docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle.md:118:**Background method changed mid-session.** When the user switches background methods (e.g., Shirley to Tougaard), the chart re-renders with the new background. If subtracted view is on, the new background is what gets subtracted. No special handling.
docs/superpowers/plans/2026-04-07-manual-spline-background.md:11:**CRITICAL CONSTRAINT:** Do NOT modify any existing `shirleyBackground`, `smartBackground`, `linearBackground`, `tougaardBackground` functions, or any existing loading/parsing logic. Only ADD new code.
docs/superpowers/plans/2026-04-07-manual-spline-background.md:105:A pure math function with no DOM dependencies. Add it near the existing background functions (after `tougaardBackground`, around line 2749).
docs/superpowers/plans/2026-04-07-manual-spline-background.md:804:- [ ] `tougaardBackground` function: NOT modified
docs/superpowers/plans/2026-04-07-manual-spline-background.md:809:- [ ] Existing `computeBackground` cases (shirley/smart/linear/tougaard/none): NOT modified — only a new `"spline"` case added
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
docs/autofit/peak-fit-methods-decision-matrix.md:71:**Curve fitting / practice:** Major et al., *JVST A* 38, 061203 (2020), 10.1116/6.0000377 · Shirley, *PRB* 5, 4709 (1972), 10.1103/PhysRevB.5.4709 · Tougaard, *SIA* 11, 453 (1988), 10.1002/sia.740110902 · Doniach & Šunjić, *J. Phys. C* 3, 285 (1970), 10.1088/0022-3719/3/2/010 · Morgan, *SIA* (2023), 10.1002/sia.7215 · box-plot overfitting, *JESRP* 253, 147094 (2021), 10.1016/j.elspec.2021.147094.
docs/autofit/PROGRESS.md:32:| Tougaard background bug-fix (C constant + BE-order + amplitude anchor) | DONE | ✅ 5 py + 4 js tests | `fitting.py::tougaard_background` + JS twin `tougaardBackground`: C was shipped SQUARED (1643² ≈ 2.7e6 eV², kernel max ~949 eV → flat/zero bg on real windows) → corrected to 1643 eV² (Tougaard 1988, SIA 11, 453); one-sided sum made order-robust (descending normalization, shirley-mirror); degenerate trailing rescale (K(0)=0 ⇒ scale ≡ raw trailing counts) replaced by the high-BE-edge anchor. Cross-language parity pinned at 1e-9. Codex checkpoint ×2: NO-GO ×2 (same MAJOR: frontend callers bypassed endpoint averaging → anchor mismatch; + 1 MINOR comment honesty) → all fixed same-session + caller-level pin; re-check ×2 **GO ×2** — unit review-complete. |
docs/autofit/PROGRESS.md:1153:## Tougaard background bug-fix (2026-07-04 goal session) — constant, BE-order, amplitude anchor
docs/autofit/PROGRESS.md:1155:Small scoped fix to the EXISTING `tougaard` background (manual-fit path
docs/autofit/PROGRESS.md:1156:math; the autofit engine only reaches it via `BackgroundType.TOUGAARD` —
docs/autofit/PROGRESS.md:1159:implementations: `fitting.py::tougaard_background` and its JS twin
docs/autofit/PROGRESS.md:1160:`tougaardBackground` in `templates/index.html` (kept in numerical
docs/autofit/PROGRESS.md:1161:agreement, pinned at 1e-9 relative by `tests/js/tougaard_twin.test.js`).
docs/autofit/PROGRESS.md:1167:   constants verified against the source: S. Tougaard, *Surf. Interface
docs/autofit/PROGRESS.md:1169:   **B = 2866 eV², C = 1643 eV²** (also restated in the QUASES-Tougaard
docs/autofit/PROGRESS.md:1172:   ~1e-9-scale, so the "Tougaard" background was essentially zero/flat.
docs/autofit/PROGRESS.md:1194:   regression than the bug. Replaced with the standard practical Tougaard
docs/autofit/PROGRESS.md:1200:4. **Tests** (`tests/test_tougaard_background.py`, 5;
docs/autofit/PROGRESS.md:1201:   `tests/js/tougaard_twin.test.js`, 4 — the JS tests extract the function
docs/autofit/PROGRESS.md:1216:through the existing `BackgroundType.TOUGAARD` dispatch). Codex
docs/autofit/PROGRESS.md:1222:`docs/autofit/codex/tougaard_fix_review_prompt.txt`, verdicts archived at
docs/autofit/PROGRESS.md:1223:`docs/autofit/codex/tougaard_fix_verdict_runA.md` / `_runB.md`. Both runs
docs/autofit/PROGRESS.md:1228:   for Tougaard while every backend caller applies
docs/autofit/PROGRESS.md:1233:   noted the UI greys out the endpoint-avg control for Tougaard while the
docs/autofit/PROGRESS.md:1235:   `computeBackgroundCore` Tougaard branches (sliced + fallback) now pass
docs/autofit/PROGRESS.md:1237:   both UI gates enable the endpoint-avg control for Tougaard (it now
docs/autofit/PROGRESS.md:1241:   `tougaardBackground(be, averaged)` (watched fail first).
docs/autofit/PROGRESS.md:1255:calls tougaard_background WITHOUT averaging, but it does so for EVERY
docs/autofit/PROGRESS.md:1257:internally consistent design, not a Tougaard-specific mismatch, and
docs/autofit/PROGRESS.md:1258:engine changes are out of scope per rails. Post-fix: JS 53/53, Tougaard
docs/autofit/PROGRESS.md:1264:`docs/autofit/codex/tougaard_fix_recheck_prompt.txt` (verdicts archived:
docs/autofit/PROGRESS.md:1265:`docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md` / `_runB.md`;
docs/autofit/PROGRESS.md:1272:consistent (shirley-iter stays disabled for Tougaard, endpoint-avg
docs/autofit/PROGRESS.md:1280:mixed-sign pass-through match the documented policy. **The Tougaard
docs/autofit/codex/tougaard_fix_verdict_runB.md:1:# Codex review — Tougaard bug-fix (commit 37861fd) — RUN B (2026-07-04)
docs/autofit/codex/tougaard_fix_verdict_runB.md:4:Prompt: docs/autofit/codex/tougaard_fix_review_prompt.txt
docs/autofit/codex/tougaard_fix_verdict_runB.md:6:1. **MAJOR** [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4202), [fitting.py](/Users/skyefortier/xps-app/fitting.py:997), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1235) — Tougaard endpoint averaging is inconsistent between shipped frontend callers and backend callers. The UI disables `endpointAvg` for Tougaard, but stale values are still sent to `/api/background` and `/api/fit`; backend applies `_apply_endpoint_averaging(...)` before `tougaard_background`, while frontend preview/stack calls `tougaardBackground(...)` on raw intensity. Concrete failure: set endpoint avg to `10`, switch to Tougaard, with high-BE endpoint `500` and next 9 points `100`; frontend anchors Tougaard to `500`, backend anchors to averaged `140`. That breaks the claimed frontend/backend twin contract exactly at the new high-BE anchor, and current tests only compare direct function calls with unaveraged data.
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:1:# Codex re-check — Tougaard fix dispositions (fix commit 2731edc) — RUN A (2026-07-04 late)
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:4:Prompt: docs/autofit/codex/tougaard_fix_recheck_prompt.txt
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:9:- Fallback full-range path now computes `avgIn = _applyEndpointAveraging(intensity, nAvg)` and passes it to Tougaard at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184) and [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4193).
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:10:- Main sliced path now passes `_applyEndpointAveraging(inSub, nAvg)` to Tougaard at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4214).
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:11:- The pin discriminates: on the outlier-edge scenario, raw Tougaard anchors at `10000`; averaged expected/main/fallback all anchor at `3400`. So the old raw-intensity call would fail it.
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:12:- UI gates are consistent: `shirley-iter` remains disabled for Tougaard because `needsIter` excludes it, while `bg-endpoint-avg` is enabled because `needsEpAvg = needsIter || type === 'tougaard'` at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3594) and [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:12197).
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:15:Tracked stale HTML copies still contain old Tougaard code, but project docs and `CLAUDE.md` identify `templates/index.html` as the active frontend; I do not count those stale copies as an active shipped caller for this disposition.
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:22:- The pin covers the concrete `[100, 0, 0, 0]` case at [tests/test_tougaard_background.py](/Users/skyefortier/xps-app/tests/test_tougaard_background.py:132).
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:29:Scope matches the expected commit footprint: only docs/prompt/verdict archives, `fitting.py`, `templates/index.html`, and the two Tougaard tests changed. `fitting.py` Tougaard executable numerics are unchanged from `37861fd`; the diff is comment-only in that function.
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md:32:- `node --test tests/js/tougaard_twin.test.js` passed.
docs/autofit/codex/phaseD_unit2_recheck3_verdict_runA.md:10:3. Legitimate citation false-rejection check: CLOSED. These all load as `CONDITIONAL`: Tougaard citation, `Powe95`, `10.1116/1.1247741`, `Smith & Jones 1990-1995 survey`, and `-30 mV vs SCE study`.
docs/autofit/codex/tougaard_fix_verdict_runA.md:1:# Codex review — Tougaard bug-fix (commit 37861fd) — RUN A (2026-07-04)
docs/autofit/codex/tougaard_fix_verdict_runA.md:4:Prompt: docs/autofit/codex/tougaard_fix_review_prompt.txt
docs/autofit/codex/tougaard_fix_verdict_runA.md:7:   Frontend Tougaard still bypasses `_applyEndpointAveraging`, while backend `/api/fit`, `/api/background`, and autofit parity paths apply `_apply_endpoint_averaging` before `tougaard_background`. With the new high-BE anchor this is no longer a small shape-only mismatch: endpoint averaging directly sets the anchor amplitude. Concrete scenario: descending 11-point window, `endpointAvg=2`, high-BE first point is a spike/outlier `10000`, second point and rest are `100`; frontend anchors Tougaard to `10000`, backend anchors to averaged `5050`. The committed JS twin test only calls `tougaardBackground` directly on the same raw array, so it does not catch the shipped caller contract mismatch.
docs/autofit/codex/phaseD_unit2_recheck2_verdict_runA.md:10:3. CLOSED. No false-rejection issue found in probes: `Powe95`, DOI, URL, Tougaard citation, `No. 5, J. Chem.`, and `None et al...` all load. `0` remains rejected as intended.
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:6:CONTEXT: Commit 37861fd fixed the Tougaard background (squared constant
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:7:C=1643**2 → 1643 eV² per Tougaard 1988 SIA 11,453; BE-order robustness via
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:10:docs/autofit/codex/tougaard_fix_review_prompt.txt, verdicts archived at
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:11:docs/autofit/codex/tougaard_fix_verdict_runA.md / _runB.md) each returned
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:17:averaging for Tougaard while all backend callers apply
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:21:control for Tougaard while its value is still sent to and applied by the
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:23:DISPOSITION: templates/index.html computeBackgroundCore — BOTH Tougaard
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:29:~line 12180) now compute `needsEpAvg = needsIter || type === 'tougaard'`
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:30:so the control is enabled for Tougaard (it genuinely affects the anchor;
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:32:dishonest). PIN: new test in tests/js/tougaard_twin.test.js
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:33:('computeBackgroundCore applies endpoint averaging for tougaard (both
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:35:stubs the non-tougaard routes, and asserts BOTH branches bit-equal
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:36:tougaardBackground(be, _applyEndpointAveraging(intensity, 3)) on run A's
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:40:consistent (shirley-iter stays disabled for tougaard, endpoint-avg
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:41:enabled)? Any OTHER shipped caller of tougaardBackground we missed?
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:49:tougaard_background anchor block; templates/index.html tougaardBackground
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:53:input). PIN: tests/test_tougaard_background.py::
docs/autofit/codex/tougaard_fix_recheck_prompt.txt:63:fitting.py's tougaard_background NUMERICS must be byte-identical to
docs/autofit/codex/phaseD_unit2_recheck2_prompt.txt:23:   citations still load (e.g. "Tougaard, Surf. Interface Anal. 11, 453
docs/autofit/codex/tougaard_fix_review_prompt.txt:2:repo (XPS peak-fitting web app). Review commit 37861fd ("tougaard: fix
docs/autofit/codex/tougaard_fix_review_prompt.txt:9:- fitting.py: ONLY tougaard_background (docstring + body). Nothing else in
docs/autofit/codex/tougaard_fix_review_prompt.txt:11:- templates/index.html: ONLY the tougaardBackground JS function (+ leading
docs/autofit/codex/tougaard_fix_review_prompt.txt:13:- New tests: tests/test_tougaard_background.py, tests/js/tougaard_twin.test.js.
docs/autofit/codex/tougaard_fix_review_prompt.txt:20:   slip of "C = 1643 eV²" (S. Tougaard, Surf. Interface Anal. 11, 453
docs/autofit/codex/tougaard_fix_review_prompt.txt:48:   Decision taken: replace it with the standard practical Tougaard
docs/autofit/codex/tougaard_fix_review_prompt.txt:54:   claim "standard practical Tougaard criterion" fair? (c) was there a
docs/autofit/codex/tougaard_fix_review_prompt.txt:59:4. TESTS. tests/test_tougaard_background.py (5 tests) and
docs/autofit/codex/tougaard_fix_review_prompt.txt:60:   tests/js/tougaard_twin.test.js (4 tests; they extract the function
docs/autofit/codex/tougaard_fix_review_prompt.txt:67:   no pre-existing test or fixture pinned the old Tougaard output (grep
docs/autofit/codex/tougaard_fix_review_prompt.txt:70:5. CALLERS. fitting.py dispatches tougaard_background at the /api/background
docs/autofit/codex/tougaard_fix_review_prompt.txt:71:   and /api/fit background paths (grep "tougaard"); autofit reaches it only
docs/autofit/codex/tougaard_fix_review_prompt.txt:72:   via BackgroundType.TOUGAARD (autofit/engine.py) and autofit/parity.py.
docs/autofit/codex/tougaard_fix_review_prompt.txt:73:   The frontend calls tougaardBackground at two sites (~line 4162/4180).
docs/autofit/codex/tougaard_fix_review_prompt.txt:80:   PROGRESS.md section "Tougaard background bug-fix (2026-07-04 goal
docs/autofit/codex/phaseD_unit2_recheck3_prompt.txt:24:load — especially ones exercising the new stripping: "Tougaard, Surf.
docs/autofit/codex/phaseD_unit2_recheck2_verdict_runB.md:6:1. **CLOSED**: round-1 residual probes now reject, including `n-a`, `false`, `0`, `n–a`, `None.`, `n - a`, `n\t-a`, `...`, `(none)`. Legitimate citations load: Tougaard citation, `Powe95`, DOI, URL, and `No. 5, J. Chem.`.
docs/autofit/codex/phaseD_unit2_recheck2_verdict_runB.md:14:3. **CLOSED**: no false rejections found in normal citation probes. `Powe95`, DOI, URL, Tougaard reference, `No. 5, J. Chem.`, and `Nonequilibrium Surf. Sci...` all load. Internal punctuation is not stripped, only edge punctuation.
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:3:Tougaard pre-loss constant (F1) + non-uniform quadrature weights (F2)") on
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:12:- fitting.py: ONLY tougaard_background (signature, docstring, body).
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:18:- templates/index.html: ONLY the tougaardBackground JS function (+ its
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:20:  unmodified — their two call sites into tougaardBackground still use the
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:22:- tests/test_tougaard_background.py, tests/js/tougaard_twin.test.js.
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:28:The previous tougaard_background computed the idealized integral
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:30:Tougaard 1988). This assumes the analysis window begins in a loss-free
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:102:    fixtures) for anything that pins a Tougaard background NUMERIC VALUE —
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:103:    not just the string "tougaard". The claim is that nothing outside the
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:104:    2 test files touched in this commit encodes the old (pre-F1) Tougaard
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:137:  copied from the sandbox), and that tougaard_twin.test.js still evals the
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:138:  real tougaardBackground out of templates/index.html rather than a
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:141:CALLERS. fitting.py dispatches tougaard_background at the /api/background
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:142:and /api/fit background paths; autofit reaches it via BackgroundType.TOUGAARD
docs/autofit/codex/tougaard_bg_fixes_unit1_review_prompt.txt:145:frontend calls tougaardBackground at ~2 sites inside computeBackgroundCore.
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:1:# Codex re-check — Tougaard fix dispositions (fix commit 2731edc) — RUN B (2026-07-04 late)
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:4:Prompt: docs/autofit/codex/tougaard_fix_recheck_prompt.txt
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:8:`computeBackgroundCore` now averages Tougaard input in both frontend branches:
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:10:- Fallback/full-range path uses `avgIn` before Tougaard: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184)
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:12:- Backend parity remains: `/api/fit` and `/api/background` both call `tougaard_background(..., _apply_endpoint_averaging(...))`: [fitting.py](/Users/skyefortier/xps-app/fitting.py:1002), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1240)
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:16:- `shirley-iter` remains disabled for Tougaard because `needsIter` excludes it.
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:17:- endpoint averaging is enabled for Tougaard via `needsEpAvg = needsIter || type === 'tougaard'`: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3594), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:12197)
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:19:The new JS pin discriminates. Against `37861fd`, the same outlier case produced raw anchor `10000` vs averaged `3400` for both branches. Against `2731edc`, both branches were bit-equal to averaged expected output. `node --test tests/js/tougaard_twin.test.js` passed.
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:25:Comments now state the real guard behavior and signed negative-count policy at both sites: [fitting.py](/Users/skyefortier/xps-app/fitting.py:587), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4053). The new Python pin matches the documented `[100,0,0,0]` behavior: [tests/test_tougaard_background.py](/Users/skyefortier/xps-app/tests/test_tougaard_background.py:131).
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:27:I could not run pytest because the read-only sandbox has no usable temp directory, but I executed the extracted `tougaard_background` body directly and confirmed `[100,0,0,0] -> [0,0,0,0]`. I also checked the mixed-sign cancellation edge: it returns a signed unanchored correlation, consistent with the “negative counts pass through signed; no clamping” policy.
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md:31:`git diff 37861fd 2731edc -- fitting.py` changes only the Tougaard guard comment; no numeric code changed. The `2731edc` file list matches the expected scope: docs, `templates/index.html`, `fitting.py`, and the two Tougaard test files.
docs/autofit/codex/phaseD_unit2_recheck3_verdict_runB.md:9:`Tougaard, Surf. Interface Anal. 11, 453 (1988)`, `Powe95`, `10.1116/1.1247741`, `Smith & Jones 1990-1995 survey`, and `-30 mV vs SCE study`. Internal hyphen survives; leading hyphen only affects the placeholder check.

exec
/bin/zsh -lc "rg -n -i \"bgIntensity|bgSubtracted|background|tougaard|bgType|bg_type|background_type\" tests tests/autofit docs/autofit/inventory scripts docs uploads data --glob '*.json' --glob '*.proj.json' --glob '*.spec.json' --glob '*.fit.json'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
uploads/3ee1dcee-2f3a-4c83-a33e-ce349f9dd4e8.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 21.9, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.5000049005795, "fwhm": 0.8000022727809339, "amplitude": 5999.985762735916, "gl_ratio": 8.555378627761456e-13, "stderr": {"center": 1.962102350870924e-06, "amplitude": 0.04162189670815025, "fwhm": 4.680060151954143e-06, "gl_ratio": 3.7802776622909907e-06}}], "confidence": {"main_aliphatic": {"sigma_stat": {"uncertainty_kind": "covariance", "values": {"center": 1.962102350870924e-06, "fwhm": 4.680060151954143e-06, "amplitude": 0.04162189670815025}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 2.7853275241795927e-12, "fwhm_mad": 4.9372728128105337e-11, "amplitude_mad": 2.594129000499379e-07}, "detectability": {"amplitude": 5999.985762735916, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:fwhm@min"], "max_cross_correlation": 0.6776994710374912}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "AG0_graphite_asymGL_satellite", "n_components": 2, "reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "bic_raw": -1732.2640251122796, "bic_weighted": 52.64466679288834, "n_eff_lag1": 366.3534125802044, "survived": true, "rank": 3, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['satellite_pi:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 3.186674785301061e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["satellite_pi:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_linked", "n_components": 3, "reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "bic_raw": -1721.6806443935482, "bic_weighted": 58.4939949414036, "n_eff_lag1": 363.28017154566334, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:fwhm@min', 'contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 5.19904519042311e-12}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.186864808391868e-11}], "proposed_peaks": [{"role": "proposed_peak_0", "accepted": false, "fitted_center": 284.0562, "fitted_fwhm": 0.5, "width_capped": false, "rejection_reason": "amplitude 1.0 \u2264 noise_floor 1.0", "near_roi_endpoint": false}], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_graphite_sym_CO_C=O", "n_components": 3, "reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "bic_raw": -1709.979884899033, "bic_weighted": 70.19264450130285, "n_eff_lag1": 363.28024523651777, "survived": true, "rank": 2, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_C=O:fwhm@max'], unphysical_widths=['contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.1271782252075944e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.382268211640556e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": ["contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)"], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["contamination_CO:center@max", "contamination_C=O:fwhm@max"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "bic_raw": -1708.8655954986962, "bic_weighted": 76.0419659126833, "n_eff_lag1": 366.35338688232457, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 7.909867801039288e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["main_aliphatic:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_linked", "n_components": 3, "reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "bic_raw": -1708.8655820330348, "bic_weighted": 76.04196591267502, "n_eff_lag1": 366.3533885732838, "survived": true, "rank": 5, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.4061902357893664e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 1.3408724708678914e-14}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "n_components": 3, "reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "bic_raw": -1708.8655817728024, "bic_weighted": 76.04196591267494, "n_eff_lag1": 366.3533923770929, "survived": true, "rank": 4, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.628908028198292e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.753864998110036e-16}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}], "non_converged": [], "ambiguous_pairs": [["B2_linked", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.12); structural difference: {'main_graphitic', 'main_aliphatic', 'contamination_CO', 'contamination_C=O', 'satellite_pi'}"], ["B2_graphite_sym_CO_C=O", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.11); structural difference: {'contamination_C=O', 'satellite_pi', 'contamination_CO'}"], ["AG0_graphite_asymGL_satellite", "AG1_graphite_asymGL_sat_plus_CO", "Indistinguishable on fit quality and BIC* (\u0394BIC*=0.00); structural difference: {'contamination_CO'}"]], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max", "residual_gap"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8, "residual_gap": {"n_attempts": 1, "n_accepted": 0}}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 2356.1031279564713, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 2379.5009607446636, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 2402.898356672834, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 2426.2955913250544, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 2379.5009606895596, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 2397.0489719191914, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 2414.5969365032793, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 2379.500437560467, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 2397.0484483372284, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 2414.596388869996, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": -1732.2628630458792, "selected": true}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": -1708.8655817728024, "selected": true}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": -1685.4717428556983, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": -1662.0718740907616, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": -1708.8655820330348, "selected": true}, {"name": "AG2_linked", "converged": true, "bic": -1691.3175603688178, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": -1673.7697813731577, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2379.5009857340206, "selected": false}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2402.8983010024053, "selected": false}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2426.29571673858, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2449.693448965505, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": -1708.8655888943526, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": -1685.4680086668614, "selected": false}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": -1662.0707790890274, "selected": false}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": -690.5033612735614, "selected": false}, {"name": "B2_linked", "converged": true, "bic": -1721.6789198318845, "selected": true}, {"name": "B3_linked", "converged": true, "bic": -1704.1305018737503, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": -1709.9798453429748, "selected": true}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": -1686.5824714043713, "selected": false}], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"AG0_graphite_asymGL_satellite": {"reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "aicc": -1766.373823502721, "n_params": 9, "n_params_adjusted": 5, "n_components": 2}, "B2_linked": {"reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "aicc": -1759.519130288255, "n_params": 10, "n_params_adjusted": 4, "n_components": 3}, "B2_graphite_sym_CO_C=O": {"reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "aicc": -1755.2376505218683, "n_params": 12, "n_params_adjusted": 4, "n_components": 3}, "MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "aicc": -1757.8137245449122, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "AG1_linked": {"reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "aicc": -1757.8137110792509, "n_params": 13, "n_params_adjusted": 6, "n_components": 3}, "AG1_graphite_asymGL_sat_plus_CO": {"reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "aicc": -1757.8137108190185, "n_params": 13, "n_params_adjusted": 5, "n_components": 3}}, "top_by_bic_star": "B2_linked", "top_by_aicc": "AG0_graphite_asymGL_satellite", "bic_ambiguous": true, "criteria_conflict": true, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "B2_linked", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "preseeded_features": [], "n_survivors": 5, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner B2_linked has constraint violations ['main_aliphatic:fwhm@min', 'contamination_CO:center@min'] (see analysis.candidates). ", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
uploads/58ef8f7c-8e65-4581-a1d5-b342298d1425.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 60.5, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_graphitic", "region": "C 1s", "phase_id": "sample", "shape": "ds_g", "center": 284.40862660161633, "fwhm": 0.6625927514639813, "amplitude": 3312.068644701938, "alpha": 4.6264159170306125e-12, "beta": 0.05, "m_gauss": 0.6625927514639813}, {"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.60000000001236, "fwhm": 0.8000000000185057, "amplitude": 2954.930348377461, "gl_ratio": 1.5421386390102043e-11}], "confidence": {"main_graphitic": {"sigma_stat": {"uncertainty_kind": "stability_mad", "values": {"center": 0.04460548852011925, "fwhm": 0.02629222009172294, "amplitude": 1333.794922536627}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 0.04460548852011925, "fwhm_mad": 0.02629222009172294, "amplitude_mad": 1333.794922536627}, "detectability": {"amplitude": 3312.068644701938, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": [], "max_cross_correlation": null}}, "main_aliphatic": {"sigma_stat": {"uncertainty_kind": "stability_mad", "values": {"center": 1.1368683772161603e-13, "fwhm": 0.0, "amplitude": 0.01636871560003783}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 0.75, "position_mad": 1.1368683772161603e-13, "fwhm_mad": 0.0, "amplitude_mad": 0.01636871560003783}, "detectability": {"amplitude": 2954.930348377461, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "max_cross_correlation": null}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866390594288e-06, "bic_star": -1732.2629233085559, "bic_raw": -1708.8656241887684, "bic_weighted": 76.04196591268362, "n_eff_lag1": 366.3533853562398, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.732479228417388e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 4}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "n_components": 4, "reduced_chi_sq": 2.2538587778357373e-06, "bic_star": -1732.262137328864, "bic_raw": -1685.467539089289, "bic_weighted": 99.4392650324933, "n_eff_lag1": 366.353460351388, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:offset@max', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.4702538358659414e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.515142706037034e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["contamination_CO:fwhm@min", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:offset@max", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 4}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "n_components": 5, "reduced_chi_sq": 2.2815134764749067e-06, "bic_star": -1732.262147660311, "bic_raw": -1662.0702503009486, "bic_weighted": 122.83656415227738, "n_eff_lag1": 366.3534720499048, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_C=O:center@max', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.5356066679308465e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.3563402013254895e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 6.937798106689261e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.25, "boundary_hits": ["contamination_C=O:center@max", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 3}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "n_components": 6, "reduced_chi_sq": 2.1990369814617878e-06, "bic_star": -1762.164200824285, "bic_raw": -1668.5750043451353, "bic_weighted": 146.2338275885795, "n_eff_lag1": 401.06051089289645, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 2.889000740966408e-10}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.084367297735124e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 3.3135447554575374e-11}, {"role": "contamination_OC=O", "persistence": 0.0, "area_fraction": 5.868305324176354e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.25, "boundary_hits": ["contamination_CO:center@max", "contamination_CO:fwhm@min", "contamination_C=O:fwhm@min", "contamination_OC=O:fwhm@min", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 1}, {"name": "M0_graph_asym_aliph_sym_satellite", "n_components": 3, "reduced_chi_sq": 0.5445546916051832, "bic_star": 2199.204211199102, "bic_raw": 2222.6015103188893, "bic_weighted": 252.6177190470987, "n_eff_lag1": 4.371020551972791, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:center@min', 'main_aliphatic:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 1.1139261674936666e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": true, "min_active_persistence": 0.25, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 1}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "n_components": 4, "reduced_chi_sq": 0.5511354169322392, "bic_star": 2199.1834191338194, "bic_raw": 2245.9780173733943, "bic_weighted": 276.01501948372095, "n_eff_lag1": 4.3708990513348684, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:center@min', 'main_aliphatic:fwhm@min', 'contamination_CO:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.2370351534164325e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.487697359241712e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": true, "min_active_persistence": 0.75, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_CO:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 2}], "non_converged": [], "ambiguous_pairs": [], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 3753.6915569887074, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 3777.0797675518816, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 3800.4736710871393, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 3823.878033686888, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 3777.0797675518816, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 3794.6107745192317, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 3812.179292646422, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 3777.07751804941, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 3794.603988962943, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 3812.1648087337817, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": 3203.092457785431, "selected": false}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": 3226.4895926311533, "selected": false}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": 3249.886864603099, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 3273.2841770393084, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": 3226.4896031446615, "selected": false}, {"name": "AG2_linked", "converged": true, "bic": 3244.0434203132595, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": 3261.5855136976834, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2263.1271879845717, "selected": true}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2286.5244671115156, "selected": true}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2309.921556825529, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2333.3190793743943, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": 1953.573584264419, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": 1976.9708924404435, "selected": true}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": 2000.3681945376777, "selected": true}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": 2023.7655196301753, "selected": true}, {"name": "B2_linked", "converged": true, "bic": 3807.15449535746, "selected": false}, {"name": "B3_linked", "converged": true, "bic": 3824.7024555091207, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": 3813.7161299169506, "selected": false}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": 3837.514037613595, "selected": false}], "filtered_dominant_alternative": {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "bic_star": -1762.164200824285, "delta_bic_vs_winner": 3961.3476199581046, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866390594288e-06, "bic_star": -1732.2629233085559, "aicc": -1757.8137532349845, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "MG1_graphAsymGL_aliph_sat_CO": {"reduced_chi_sq": 2.2538587778357373e-06, "bic_star": -1732.262137328864, "aicc": -1749.045877977565, "n_params": 17, "n_params_adjusted": 9, "n_components": 4}, "MG2_graphAsymGL_aliph_sat_CO_C=O": {"reduced_chi_sq": 2.2815134764749067e-06, "bic_star": -1732.262147660311, "aicc": -1740.0629937567558, "n_params": 21, "n_params_adjusted": 9, "n_components": 5}, "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O": {"reduced_chi_sq": 2.1990369814617878e-06, "bic_star": -1762.164200824285, "aicc": -1760.7582796070465, "n_params": 25, "n_params_adjusted": 9, "n_components": 6}, "M0_graph_asym_aliph_sym_satellite": {"reduced_chi_sq": 0.5445546916051832, "bic_star": 2199.204211199102, "aicc": 2177.343744696054, "n_params": 12, "n_params_adjusted": 8, "n_components": 3}, "M1_graph_asym_aliph_sym_sat_CO": {"reduced_chi_sq": 0.5511354169322392, "bic_star": 2199.1834191338194, "aicc": 2186.037305742729, "n_params": 16, "n_params_adjusted": 8, "n_components": 4}}, "top_by_bic_star": "M1_graph_asym_aliph_sym_sat_CO", "top_by_aicc": "M1_graph_asym_aliph_sym_sat_CO", "bic_ambiguous": false, "criteria_conflict": false, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "M1_graph_asym_aliph_sym_sat_CO", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_CO:fwhm@min", "satellite_pi:fwhm@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "bic_star": -1762.164200824285, "delta_bic_vs_winner": 3961.3476199581046, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "preseeded_features": [], "n_survivors": 1, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner M1_graph_asym_aliph_sym_sat_CO has constraint violations ['main_aliphatic:center@min', 'main_aliphatic:fwhm@min', 'contamination_CO:fwhm@min', 'satellite_pi:fwhm@min'] (see analysis.candidates).  WARNING: filtered candidate MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O beats this winner by \u0394BIC* 3961.3 but did not survive filtering (plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True))", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
uploads/a0499bc7-9313-4388-8408-d6e42386862c.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 22.5, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.5000049005795, "fwhm": 0.8000022727809339, "amplitude": 5999.985762735916, "gl_ratio": 8.555378627761456e-13, "stderr": {"center": 1.962102350870924e-06, "amplitude": 0.04162189670815025, "fwhm": 4.680060151954143e-06, "gl_ratio": 3.7802776622909907e-06}}], "confidence": {"main_aliphatic": {"sigma_stat": {"uncertainty_kind": "covariance", "values": {"center": 1.962102350870924e-06, "fwhm": 4.680060151954143e-06, "amplitude": 0.04162189670815025}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 2.7853275241795927e-12, "fwhm_mad": 4.9372728128105337e-11, "amplitude_mad": 2.594129000499379e-07}, "detectability": {"amplitude": 5999.985762735916, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:fwhm@min"], "max_cross_correlation": 0.6776994710374912}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "AG0_graphite_asymGL_satellite", "n_components": 2, "reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "bic_raw": -1732.2640251122796, "bic_weighted": 52.64466679288834, "n_eff_lag1": 366.3534125802044, "survived": true, "rank": 3, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['satellite_pi:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 3.186674785301061e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["satellite_pi:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_linked", "n_components": 3, "reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "bic_raw": -1721.6806443935482, "bic_weighted": 58.4939949414036, "n_eff_lag1": 363.28017154566334, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:fwhm@min', 'contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 5.19904519042311e-12}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.186864808391868e-11}], "proposed_peaks": [{"role": "proposed_peak_0", "accepted": false, "fitted_center": 284.0562, "fitted_fwhm": 0.5, "width_capped": false, "rejection_reason": "amplitude 1.0 \u2264 noise_floor 1.0", "near_roi_endpoint": false}], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_graphite_sym_CO_C=O", "n_components": 3, "reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "bic_raw": -1709.979884899033, "bic_weighted": 70.19264450130285, "n_eff_lag1": 363.28024523651777, "survived": true, "rank": 2, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_C=O:fwhm@max'], unphysical_widths=['contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.1271782252075944e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.382268211640556e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": ["contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)"], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["contamination_CO:center@max", "contamination_C=O:fwhm@max"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "bic_raw": -1708.8655954986962, "bic_weighted": 76.0419659126833, "n_eff_lag1": 366.35338688232457, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 7.909867801039288e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["main_aliphatic:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_linked", "n_components": 3, "reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "bic_raw": -1708.8655820330348, "bic_weighted": 76.04196591267502, "n_eff_lag1": 366.3533885732838, "survived": true, "rank": 5, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.4061902357893664e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 1.3408724708678914e-14}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "n_components": 3, "reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "bic_raw": -1708.8655817728024, "bic_weighted": 76.04196591267494, "n_eff_lag1": 366.3533923770929, "survived": true, "rank": 4, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.628908028198292e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.753864998110036e-16}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}], "non_converged": [], "ambiguous_pairs": [["B2_linked", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.12); structural difference: {'main_graphitic', 'main_aliphatic', 'contamination_CO', 'contamination_C=O', 'satellite_pi'}"], ["B2_graphite_sym_CO_C=O", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.11); structural difference: {'contamination_C=O', 'satellite_pi', 'contamination_CO'}"], ["AG0_graphite_asymGL_satellite", "AG1_graphite_asymGL_sat_plus_CO", "Indistinguishable on fit quality and BIC* (\u0394BIC*=0.00); structural difference: {'contamination_CO'}"]], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max", "residual_gap"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8, "residual_gap": {"n_attempts": 1, "n_accepted": 0}}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 2356.1031279564713, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 2379.5009607446636, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 2402.898356672834, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 2426.2955913250544, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 2379.5009606895596, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 2397.0489719191914, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 2414.5969365032793, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 2379.500437560467, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 2397.0484483372284, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 2414.596388869996, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": -1732.2628630458792, "selected": true}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": -1708.8655817728024, "selected": true}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": -1685.4717428556983, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": -1662.0718740907616, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": -1708.8655820330348, "selected": true}, {"name": "AG2_linked", "converged": true, "bic": -1691.3175603688178, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": -1673.7697813731577, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2379.5009857340206, "selected": false}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2402.8983010024053, "selected": false}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2426.29571673858, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2449.693448965505, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": -1708.8655888943526, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": -1685.4680086668614, "selected": false}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": -1662.0707790890274, "selected": false}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": -690.5033612735614, "selected": false}, {"name": "B2_linked", "converged": true, "bic": -1721.6789198318845, "selected": true}, {"name": "B3_linked", "converged": true, "bic": -1704.1305018737503, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": -1709.9798453429748, "selected": true}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": -1686.5824714043713, "selected": false}], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"AG0_graphite_asymGL_satellite": {"reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "aicc": -1766.373823502721, "n_params": 9, "n_params_adjusted": 5, "n_components": 2}, "B2_linked": {"reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "aicc": -1759.519130288255, "n_params": 10, "n_params_adjusted": 4, "n_components": 3}, "B2_graphite_sym_CO_C=O": {"reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "aicc": -1755.2376505218683, "n_params": 12, "n_params_adjusted": 4, "n_components": 3}, "MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "aicc": -1757.8137245449122, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "AG1_linked": {"reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "aicc": -1757.8137110792509, "n_params": 13, "n_params_adjusted": 6, "n_components": 3}, "AG1_graphite_asymGL_sat_plus_CO": {"reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "aicc": -1757.8137108190185, "n_params": 13, "n_params_adjusted": 5, "n_components": 3}}, "top_by_bic_star": "B2_linked", "top_by_aicc": "AG0_graphite_asymGL_satellite", "bic_ambiguous": true, "criteria_conflict": true, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "B2_linked", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "preseeded_features": [], "n_survivors": 5, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner B2_linked has constraint violations ['main_aliphatic:fwhm@min', 'contamination_CO:center@min'] (see analysis.candidates). ", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:342:  "background": {

codex
The broad text grep found Tougaard mentions mostly in docs and the two intended test files. I’m doing a second pass on saved JSON/proj/proj.zip artifacts specifically, since those are the places old numeric background arrays would be easy to miss.
exec
/bin/zsh -lc "rg -n -i \"tougaard|bgIntensity|bgSubtracted|bgType|bg_type|\\\"background\\\"\" docs/autofit/test_data tests docs/autofit/inventory scripts --glob '*.json' --glob '*.proj.json' --glob '*.fit.json' --glob '*.spec.json'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:342:  "background": {

exec
/bin/zsh -lc "rg -n -i \"tougaard\" uploads data tests/fixtures tests/autofit/fixtures docs/autofit/inventory docs/autofit/test_data --glob '*.json' --glob '*.proj.json' --glob '*.fit.json' --glob '*.spec.json'" in /Users/skyefortier/xps-verify
 exited 1 in 0ms:
exec
/bin/zsh -lc 'for f in docs/autofit/test_data/*.proj.zip; do unzip -p "$f" 2>/dev/null | rg -n -i "tougaard|bgIntensity|bgSubtracted|background|bgType|bg_type" && printf '"'FILE %s\\n' \""'$f"; done' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
1283:    "bgIntensity": [
1476:    "bgSubtracted": [
1678:    "bgType": "shirley",
1688:    "bgSubtractedView": false
3444:    "bgIntensity": [
3796:    "bgSubtracted": [
4157:    "bgType": "smart",
4167:    "bgSubtractedView": false
5443:    "bgIntensity": [
5632:    "bgSubtracted": [
5830:    "bgType": "shirley",
5840:    "bgSubtractedView": false
7596:    "bgIntensity": [
7948:    "bgSubtracted": [
8309:    "bgType": "smart",
8319:    "bgSubtractedView": false
9585:    "bgIntensity": [
9774:    "bgSubtracted": [
9972:    "bgType": "shirley",
9982:    "bgSubtractedView": false
11736:    "bgIntensity": [
12087:    "bgSubtracted": [
12447:    "bgType": "smart",
12457:    "bgSubtractedView": false
13723:    "bgIntensity": [
13912:    "bgSubtracted": [
14110:    "bgType": "shirley",
14120:    "bgSubtractedView": false
15876:    "bgIntensity": [
16228:    "bgSubtracted": [
16589:    "bgType": "smart",
16599:    "bgSubtractedView": false
17863:    "bgIntensity": [
18051:    "bgSubtracted": [
18248:    "bgType": "shirley",
18258:    "bgSubtractedView": false
20014:    "bgIntensity": [
20366:    "bgSubtracted": [
20727:    "bgType": "smart",
20737:    "bgSubtractedView": false
22003:    "bgIntensity": [
22192:    "bgSubtracted": [
22390:    "bgType": "shirley",
22400:    "bgSubtractedView": false
24156:    "bgIntensity": [
24508:    "bgSubtracted": [
24869:    "bgType": "smart",
24879:    "bgSubtractedView": false
26145:    "bgIntensity": [
26334:    "bgSubtracted": [
26532:    "bgType": "shirley",
26542:    "bgSubtractedView": false
28298:    "bgIntensity": [
28650:    "bgSubtracted": [
29011:    "bgType": "smart",
29021:    "bgSubtractedView": false
30303:    "bgIntensity": [
30495:    "bgSubtracted": [
30696:    "bgType": "shirley",
30706:    "bgSubtractedView": false
32462:    "bgIntensity": [
32814:    "bgSubtracted": [
33175:    "bgType": "smart",
33185:    "bgSubtractedView": false
34451:    "bgIntensity": [
34640:    "bgSubtracted": [
34838:    "bgType": "shirley",
34848:    "bgSubtractedView": false
36602:    "bgIntensity": [
36953:    "bgSubtracted": [
37313:    "bgType": "smart",
37323:    "bgSubtractedView": false
38603:    "bgIntensity": [
38794:    "bgSubtracted": [
38994:    "bgType": "shirley",
39004:    "bgSubtractedView": false
40760:    "bgIntensity": [
41112:    "bgSubtracted": [
41473:    "bgType": "smart",
41483:    "bgSubtractedView": false
FILE docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
840:    "bgIntensity": [
957:    "bgSubtracted": [
1083:    "bgType": "smart",
1093:    "bgSubtractedView": false
2891:    "bgIntensity": null,
2892:    "bgSubtracted": [
3229:    "bgType": "smart",
3239:    "bgSubtractedView": false
4080:    "bgIntensity": null,
4081:    "bgSubtracted": [
4207:    "bgType": "smart",
4217:    "bgSubtractedView": false
6017:    "bgIntensity": null,
6018:    "bgSubtracted": [
6355:    "bgType": "smart",
6365:    "bgSubtractedView": false
7204:    "bgIntensity": null,
7205:    "bgSubtracted": [
7330:    "bgType": "smart",
7340:    "bgSubtractedView": false
9140:    "bgIntensity": null,
9141:    "bgSubtracted": [
9478:    "bgType": "smart",
9488:    "bgSubtractedView": false
10327:    "bgIntensity": null,
10328:    "bgSubtracted": [
10453:    "bgType": "smart",
10463:    "bgSubtractedView": false
12265:    "bgIntensity": null,
12266:    "bgSubtracted": [
12604:    "bgType": "smart",
12614:    "bgSubtractedView": false
13453:    "bgIntensity": null,
13454:    "bgSubtracted": [
13579:    "bgType": "smart",
13589:    "bgSubtractedView": false
15391:    "bgIntensity": null,
15392:    "bgSubtracted": [
15730:    "bgType": "smart",
15740:    "bgSubtractedView": false
16579:    "bgIntensity": null,
16580:    "bgSubtracted": [
16705:    "bgType": "smart",
16715:    "bgSubtractedView": false
18517:    "bgIntensity": null,
18518:    "bgSubtracted": [
18856:    "bgType": "smart",
18866:    "bgSubtractedView": false
19667:    "bgIntensity": null,
19668:    "bgSubtracted": [
19870:    "bgType": "smart",
19880:    "bgSubtractedView": false
21682:    "bgIntensity": [
22011:    "bgSubtracted": [
22349:    "bgType": "smart",
22359:    "bgSubtractedView": false
23198:    "bgIntensity": [
23314:    "bgSubtracted": [
23439:    "bgType": "smart",
23449:    "bgSubtractedView": false
25251:    "bgIntensity": null,
25252:    "bgSubtracted": [
25590:    "bgType": "smart",
25600:    "bgSubtractedView": false
26439:    "bgIntensity": [
26555:    "bgSubtracted": [
26680:    "bgType": "smart",
26690:    "bgSubtractedView": false
28492:    "bgIntensity": null,
28493:    "bgSubtracted": [
28831:    "bgType": "smart",
28841:    "bgSubtractedView": false
29642:    "bgIntensity": null,
29643:    "bgSubtracted": [
29845:    "bgType": "smart",
29855:    "bgSubtractedView": false
31657:    "bgIntensity": null,
31658:    "bgSubtracted": [
31996:    "bgType": "smart",
32006:    "bgSubtractedView": false
FILE docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
2741:    "bgType": "shirley",
2751:    "bgSubtractedView": false
5493:    "bgType": "shirley",
5503:    "bgSubtractedView": false
8245:    "bgType": "shirley",
8255:    "bgSubtractedView": false
10997:    "bgType": "shirley",
11007:    "bgSubtractedView": false
13749:    "bgType": "shirley",
13759:    "bgSubtractedView": false
16501:    "bgType": "shirley",
16511:    "bgSubtractedView": false
19253:    "bgType": "shirley",
19263:    "bgSubtractedView": false
22005:    "bgType": "shirley",
22015:    "bgSubtractedView": false
24757:    "bgType": "shirley",
24767:    "bgSubtractedView": false
27509:    "bgType": "shirley",
27519:    "bgSubtractedView": false
28660:    "bgIntensity": [
28822:    "bgSubtracted": [
28993:    "bgType": "shirley",
29003:    "bgSubtractedView": false
30144:    "bgIntensity": [
30306:    "bgSubtracted": [
30477:    "bgType": "shirley",
30487:    "bgSubtractedView": false
31628:    "bgIntensity": [
31790:    "bgSubtracted": [
31961:    "bgType": "shirley",
31971:    "bgSubtractedView": false
33112:    "bgIntensity": [
33274:    "bgSubtracted": [
33445:    "bgType": "shirley",
33455:    "bgSubtractedView": false
34596:    "bgIntensity": [
34758:    "bgSubtracted": [
34929:    "bgType": "shirley",
34939:    "bgSubtractedView": false
36100:    "bgIntensity": [
36272:    "bgSubtracted": [
36453:    "bgType": "shirley",
36463:    "bgSubtractedView": false
37624:    "bgIntensity": [
37796:    "bgSubtracted": [
37977:    "bgType": "shirley",
37987:    "bgSubtractedView": false
39148:    "bgIntensity": [
39320:    "bgSubtracted": [
39501:    "bgType": "shirley",
39511:    "bgSubtractedView": false
40652:    "bgIntensity": [
40814:    "bgSubtracted": [
40985:    "bgType": "smart",
40995:    "bgSubtractedView": false
42217:    "bgIntensity": [
42379:    "bgSubtracted": [
42550:    "bgType": "shirley",
42560:    "bgSubtractedView": false
FILE docs/autofit/test_data/8-JT Graphite.proj.zip
2741:    "bgType": "shirley",
2751:    "bgSubtractedView": false
5493:    "bgType": "shirley",
5503:    "bgSubtractedView": false
8245:    "bgType": "shirley",
8255:    "bgSubtractedView": false
10997:    "bgType": "shirley",
11007:    "bgSubtractedView": false
13749:    "bgType": "shirley",
13759:    "bgSubtractedView": false
16501:    "bgType": "shirley",
16511:    "bgSubtractedView": false
19253:    "bgType": "shirley",
19263:    "bgSubtractedView": false
22005:    "bgType": "shirley",
22015:    "bgSubtractedView": false
24757:    "bgType": "shirley",
24767:    "bgSubtractedView": false
27509:    "bgType": "shirley",
27519:    "bgSubtractedView": false
28239:    "bgIntensity": null,
28240:    "bgSubtracted": [
28411:    "bgType": "smart_exp",
28421:    "bgSubtractedView": false
29141:    "bgIntensity": null,
29142:    "bgSubtracted": [
29313:    "bgType": "smart_exp",
29323:    "bgSubtractedView": false
30043:    "bgIntensity": null,
30044:    "bgSubtracted": [
30215:    "bgType": "smart_exp",
30225:    "bgSubtractedView": false
30945:    "bgIntensity": null,
30946:    "bgSubtracted": [
31117:    "bgType": "smart_exp",
31127:    "bgSubtractedView": false
31847:    "bgIntensity": [
32009:    "bgSubtracted": [
32180:    "bgType": "smart_exp",
32190:    "bgSubtractedView": false
32910:    "bgIntensity": null,
32911:    "bgSubtracted": [
33082:    "bgType": "smart_exp",
33092:    "bgSubtractedView": false
33812:    "bgIntensity": null,
33813:    "bgSubtracted": [
33984:    "bgType": "smart_exp",
33994:    "bgSubtractedView": false
34714:    "bgIntensity": null,
34715:    "bgSubtracted": [
34886:    "bgType": "smart_exp",
34896:    "bgSubtractedView": false
35777:    "bgIntensity": [
35939:    "bgSubtracted": [
36110:    "bgType": "smart_exp",
36120:    "bgSubtractedView": false
36840:    "bgIntensity": null,
36841:    "bgSubtracted": [
37012:    "bgType": "smart_exp",
37022:    "bgSubtractedView": false
37424:    "bgType": "shirley",
37434:    "bgSubtractedView": false
37836:    "bgType": "shirley",
37846:    "bgSubtractedView": false
38248:    "bgType": "shirley",
38258:    "bgSubtractedView": false
38660:    "bgType": "shirley",
38670:    "bgSubtractedView": false
39072:    "bgType": "shirley",
39082:    "bgSubtractedView": false
39484:    "bgType": "shirley",
39494:    "bgSubtractedView": false
39896:    "bgType": "shirley",
39906:    "bgSubtractedView": false
40308:    "bgType": "shirley",
40318:    "bgSubtractedView": false
40720:    "bgType": "shirley",
40730:    "bgSubtractedView": false
41132:    "bgType": "shirley",
41142:    "bgSubtractedView": false
41564:    "bgType": "shirley",
41574:    "bgSubtractedView": false
41996:    "bgType": "shirley",
42006:    "bgSubtractedView": false
42428:    "bgType": "shirley",
42438:    "bgSubtractedView": false
44194:    "bgIntensity": [
44546:    "bgSubtracted": [
44907:    "bgType": "smart",
44917:    "bgSubtractedView": false
46673:    "bgIntensity": [
47025:    "bgSubtracted": [
47386:    "bgType": "smart",
47396:    "bgSubtractedView": false
49152:    "bgIntensity": [
49504:    "bgSubtracted": [
49865:    "bgType": "smart",
49875:    "bgSubtractedView": false
51631:    "bgIntensity": [
51983:    "bgSubtracted": [
52344:    "bgType": "smart",
52354:    "bgSubtractedView": false
54110:    "bgIntensity": [
54462:    "bgSubtracted": [
54823:    "bgType": "smart",
54833:    "bgSubtractedView": false
56589:    "bgIntensity": [
56941:    "bgSubtracted": [
57302:    "bgType": "smart",
57312:    "bgSubtractedView": false
59068:    "bgIntensity": [
59420:    "bgSubtracted": [
59781:    "bgType": "smart",
59791:    "bgSubtractedView": false
61547:    "bgIntensity": [
61899:    "bgSubtracted": [
62260:    "bgType": "smart",
62270:    "bgSubtractedView": false
64026:    "bgIntensity": [
64378:    "bgSubtracted": [
64739:    "bgType": "smart",
64749:    "bgSubtractedView": false
66505:    "bgIntensity": [
66857:    "bgSubtracted": [
67218:    "bgType": "smart",
67228:    "bgSubtractedView": false
FILE docs/autofit/test_data/B4C-UCl4.proj.zip
2741:    "bgType": "shirley",
3840:    "bgIntensity": null,
3841:    "bgSubtracted": null,
3848:    "bgType": "shirley",
5028:    "bgIntensity": null,
5029:    "bgSubtracted": null,
5036:    "bgType": "shirley",
6135:    "bgIntensity": null,
6136:    "bgSubtracted": null,
6143:    "bgType": "shirley",
7242:    "bgIntensity": null,
7243:    "bgSubtracted": null,
7250:    "bgType": "shirley",
8349:    "bgIntensity": null,
8350:    "bgSubtracted": null,
8357:    "bgType": "shirley",
8367:    "bgSubtractedView": false
9457:    "bgIntensity": null,
9458:    "bgSubtracted": null,
9465:    "bgType": "shirley",
9475:    "bgSubtractedView": false
10565:    "bgIntensity": null,
10566:    "bgSubtracted": null,
10573:    "bgType": "shirley",
10583:    "bgSubtractedView": false
11987:    "bgIntensity": null,
11988:    "bgSubtracted": null,
11995:    "bgType": "smart",
13408:    "bgIntensity": null,
13409:    "bgSubtracted": null,
13416:    "bgType": "smart",
14829:    "bgIntensity": null,
14830:    "bgSubtracted": null,
14837:    "bgType": "smart",
16250:    "bgIntensity": null,
16251:    "bgSubtracted": null,
16258:    "bgType": "smart",
17671:    "bgIntensity": null,
17672:    "bgSubtracted": null,
17679:    "bgType": "smart",
19092:    "bgIntensity": null,
19093:    "bgSubtracted": null,
19100:    "bgType": "smart",
20513:    "bgIntensity": null,
20514:    "bgSubtracted": null,
20521:    "bgType": "smart",
20531:    "bgSubtractedView": false
21499:    "bgIntensity": [
21701:    "bgSubtracted": [
21912:    "bgType": "smart_exp",
21922:    "bgSubtractedView": false
22866:    "bgIntensity": [
23068:    "bgSubtracted": [
23279:    "bgType": "smart_exp",
23289:    "bgSubtractedView": false
24255:    "bgIntensity": [
24457:    "bgSubtracted": [
24668:    "bgType": "smart_exp",
24678:    "bgSubtractedView": false
FILE docs/autofit/test_data/Cl2p_projfit_test.proj.zip
2740:    "bgType": "shirley",
3842:    "bgType": "shirley",
5025:    "bgType": "shirley",
6127:    "bgType": "shirley",
7229:    "bgType": "shirley",
8331:    "bgType": "shirley",
9433:    "bgType": "shirley",
10535:    "bgType": "shirley",
11951:    "bgType": "smart",
13367:    "bgType": "smart",
14783:    "bgType": "smart",
16199:    "bgType": "smart",
17615:    "bgType": "smart",
19031:    "bgType": "smart",
20447:    "bgType": "smart",
FILE docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
2741:    "bgType": "shirley",
2751:    "bgSubtractedView": false
5493:    "bgType": "shirley",
5503:    "bgSubtractedView": false
8245:    "bgType": "shirley",
8255:    "bgSubtractedView": false
10997:    "bgType": "shirley",
11007:    "bgSubtractedView": false
13749:    "bgType": "shirley",
13759:    "bgSubtractedView": false
16501:    "bgType": "shirley",
16511:    "bgSubtractedView": false
19253:    "bgType": "shirley",
19263:    "bgSubtractedView": false
22005:    "bgType": "shirley",
22015:    "bgSubtractedView": false
24757:    "bgType": "shirley",
24767:    "bgSubtractedView": false
27509:    "bgType": "shirley",
27519:    "bgSubtractedView": false
28801:    "bgIntensity": [
28993:    "bgSubtracted": [
29194:    "bgType": "shirley",
29204:    "bgSubtractedView": false
30484:    "bgIntensity": [
30675:    "bgSubtracted": [
30875:    "bgType": "shirley",
30885:    "bgSubtractedView": false
32073:    "bgIntensity": [
32218:    "bgSubtracted": [
32372:    "bgType": "shirley",
32382:    "bgSubtractedView": false
33570:    "bgIntensity": [
33715:    "bgSubtracted": [
33869:    "bgType": "shirley",
33879:    "bgSubtractedView": false
35065:    "bgIntensity": [
35209:    "bgSubtracted": [
35362:    "bgType": "shirley",
35372:    "bgSubtractedView": false
36640:    "bgIntensity": [
36784:    "bgSubtracted": [
36937:    "bgType": "shirley",
36947:    "bgSubtractedView": false
38133:    "bgIntensity": [
38277:    "bgSubtracted": [
38430:    "bgType": "shirley",
38440:    "bgSubtractedView": false
39628:    "bgIntensity": [
39773:    "bgSubtracted": [
39927:    "bgType": "shirley",
39937:    "bgSubtractedView": false
41123:    "bgIntensity": [
41267:    "bgSubtracted": [
41420:    "bgType": "shirley",
41430:    "bgSubtractedView": false
42616:    "bgIntensity": [
42760:    "bgSubtracted": [
42913:    "bgType": "shirley",
42923:    "bgSubtractedView": false
44679:    "bgIntensity": null,
44680:    "bgSubtracted": [
45041:    "bgType": "smart",
45051:    "bgSubtractedView": false
46807:    "bgIntensity": [
47159:    "bgSubtracted": [
47520:    "bgType": "smart",
47530:    "bgSubtractedView": false
49286:    "bgIntensity": null,
49287:    "bgSubtracted": [
49648:    "bgType": "smart",
49658:    "bgSubtractedView": false
51414:    "bgIntensity": null,
51415:    "bgSubtracted": [
51776:    "bgType": "smart",
51786:    "bgSubtractedView": false
53542:    "bgIntensity": [
53894:    "bgSubtracted": [
54255:    "bgType": "smart",
54265:    "bgSubtractedView": false
56021:    "bgIntensity": null,
56022:    "bgSubtracted": [
56383:    "bgType": "smart",
56393:    "bgSubtractedView": false
58149:    "bgIntensity": [
58501:    "bgSubtracted": [
58862:    "bgType": "smart",
58872:    "bgSubtractedView": false
60628:    "bgIntensity": [
60980:    "bgSubtracted": [
61341:    "bgType": "smart",
61351:    "bgSubtractedView": false
63107:    "bgIntensity": [
63459:    "bgSubtracted": [
63820:    "bgType": "smart",
63830:    "bgSubtractedView": false
65586:    "bgIntensity": [
65938:    "bgSubtracted": [
66299:    "bgType": "smart",
66309:    "bgSubtractedView": false
FILE docs/autofit/test_data/UCl4_on_graphite.proj.zip

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '286,304p' && nl -ba autofit/parity.py | sed -n '96,112p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '1018,1048p;1260,1284p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

 succeeded in 0ms:
  1018	    if manual_bg is not None and bg_method == "manual":
  1019	        # manual_bg is a list of [be, intensity] anchor points from the
  1020	        # frontend. The anchors are BE-anchored (independent of i0/i1),
  1021	        # so interpolate them across the full ROI grid.
  1022	        anchors = sorted(manual_bg, key=lambda a: a[0])
  1023	        if len(anchors) >= 2:
  1024	            anchor_x = np.array([a[0] for a in anchors])
  1025	            anchor_y = np.array([a[1] for a in anchors])
  1026	            bg = np.interp(x, anchor_x, anchor_y)
  1027	        else:
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
  1043	        if x[i1 - 1] != x[i0]:
  1044	            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
  1045	        else:
  1046	            slope = 0.0
  1047	        bg = y[i0] + slope * (x - x[i0])
  1048	    elif bg_method in ("none", "flat", "", "manual"):
  1260	    endpoint_avg: int = 1,
  1261	) -> dict[str, Any]:
  1262	    """Return just the background array without fitting peaks."""
  1263	    i0 = start_idx if start_idx is not None else 0
  1264	    i1 = end_idx if end_idx is not None else len(energy)
  1265	    x, y = energy[i0:i1], counts[i0:i1]
  1266	
  1267	    if method == "shirley":
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
  1281	    else:
  1282	        raise ValueError(f"Unknown background method '{method}'")
  1283	
  1284	    return {

exec
/bin/zsh -lc 'git diff 3d9ff54''^ 3d9ff54 -- app.py autofit/engine.py autofit/parity.py autofit/methods fitting.py templates/index.html | rg -n "''^diff|''^@@|tougaard|api/fit|run_fit|BackgroundType|computeBackgroundCore|_applyEndpoint"' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-X4Hb8xiO' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-enOzOkf3' (errno=Operation not permitted)
1:diff --git a/fitting.py b/fitting.py
5:@@ -505,21 +505,49 @@ def shirley_linear_background(
9:-def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
11:+def tougaard_background(
55:-    window, matching the frontend JS twin ``tougaardBackground``.
57:+    ``tougaardBackground``.
61:@@ -534,6 +562,8 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
70:@@ -545,17 +575,29 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
108:@@ -563,36 +605,30 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
162:diff --git a/templates/index.html b/templates/index.html
166:@@ -4133,7 +4133,7 @@ function linearBackground(be, intensity) {
170:-function tougaardBackground(be, intensity) {
171:+function tougaardBackground(be, intensity, nAvg) {
175:@@ -4142,29 +4142,51 @@ function tougaardBackground(be, intensity) {
182:+  if (nAvg > 1) inW = _applyEndpointAveraging(inW, nAvg);

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '60,115p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    60	) -> np.ndarray:
    61	    """
    62	    Pseudo‑Voigt as a linear combination of Gaussian and Lorentzian.
    63	
    64	    gl_ratio : Lorentzian fraction  (0 = pure Gaussian, 1 = pure Lorentzian)
    65	    """
    66	    eta = float(np.clip(gl_ratio, 0.0, 1.0))
    67	    return (1.0 - eta) * _gaussian(x, amplitude, center, fwhm) + eta * _lorentzian(
    68	        x, amplitude, center, fwhm
    69	    )
    70	
    71	
    72	def _asymmetric_gl(
    73	    x: np.ndarray,
    74	    amplitude: float,
    75	    center: float,
    76	    fwhm: float,
    77	    asymmetry: float,
    78	    gl_ratio: float,
    79	) -> np.ndarray:
    80	    """
    81	    Asymmetric GL pseudo‑Voigt with independent asymmetry parameter.
    82	
    83	    fwhm      : base FWHM (used on the low‑BE side, i.e. x ≤ center)
    84	    asymmetry : broadening factor for the high‑BE side;
    85	                fwhm_right = fwhm × (1 + asymmetry).  0 = symmetric.
    86	    gl_ratio  : common Lorentzian fraction for both sides.
    87	
    88	    Both halves meet at x = center with value = amplitude.
    89	    """
    90	    asym = float(np.clip(asymmetry, 0.0, 1.0))
    91	    fwhm_r = fwhm * (1.0 + asym)
    92	    result = np.empty_like(x, dtype=float)
    93	    left = x <= center
    94	    result[left] = _pseudo_voigt_gl(x[left], amplitude, center, fwhm, gl_ratio)
    95	    result[~left] = _pseudo_voigt_gl(x[~left], amplitude, center, fwhm_r, gl_ratio)
    96	    return result
    97	
    98	
    99	def _doniach_sunjic(
   100	    x: np.ndarray,
   101	    amplitude: float,
   102	    center: float,
   103	    fwhm: float,
   104	    alpha: float,
   105	    gamma_asym: float = 0.0,
   106	) -> np.ndarray:
   107	    """
   108	    Doniach‑Sunjic lineshape for metallic core‑level spectra.
   109	
   110	      DS(x) = A · N · cos(πα/2 + (1‑α)·arctan((c‑x)/γ))
   111	                    ─────────────────────────────────────────
   112	                         ((c‑x)² + γ²)^((1‑α)/2)
   113	              × exp(−gamma_asym · max(0, x−c))
   114	
   115	    where γ = fwhm/2,  N = γ^(1‑α)/cos(πα/2)  so that DS(c) = A.

exec
/bin/zsh -lc 'rg -n "def _apply_endpoint_averaging|def shirley_background|def smart_background|def _compute_background" fitting.py autofit/engine.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
fitting.py:306:def shirley_background(
fitting.py:357:def smart_background(
fitting.py:432:def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
autofit/engine.py:287:def _compute_background(x: np.ndarray, y: np.ndarray, bg: BackgroundType) -> np.ndarray:

exec
/bin/zsh -lc 'git diff --unified=0 3d9ff54''^ 3d9ff54 -- fitting.py | rg -n "shirley_background|smart_background|_apply_endpoint_averaging|_compute_background|def "' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jY4GgVTn' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GCaiVVCd' (errno=Operation not permitted)
5:@@ -508,2 +508,7 @@ def shirley_linear_background(
6:-def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
8:+def tougaard_background(
15:@@ -515 +520,25 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
40:+    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
42:@@ -520,3 +549,2 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
48:@@ -536,0 +565,2 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
50:+        ya = _apply_endpoint_averaging(ya, n_avg)
51:@@ -547,0 +578,6 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
58:@@ -550 +586,2 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
62:@@ -552,7 +589,12 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
82:@@ -566,2 +608,2 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
87:@@ -568,0 +611 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
89:@@ -573,3 +616 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
94:@@ -577 +618 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
97:@@ -579,17 +620,12 @@ def tougaard_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:

codex
The saved-fit artifact pass did not surface Tougaard numeric pins: the `.proj.zip` files contain `bgIntensity` arrays, but their `bgType` values are Shirley/Smart/Smart Exp, not Tougaard; the JSON grep for Tougaard in fixtures returned no hits outside docs/tests.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '420,455p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   420	        B = b_high + step * (cum_right / total)
   421	
   422	        # Constrain during iteration: lock to data where bg exceeds it
   423	        B = np.minimum(B, ys)
   424	
   425	        if np.max(np.abs(B - B_prev)) < tol:
   426	            break
   427	
   428	    B = np.minimum(B, ys)  # final safety clamp
   429	    return B[::-1] if flipped else B
   430	
   431	
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

codex
One more sandbox wrinkle: here-doc commands also try to create temp files, so they fail under read-only. Single-line `node -e` probes still work; I’ll use those for the negative-scale scenario instead of here-docs.
exec
/bin/zsh -lc "node -e \"const fs=require('fs'); const html=fs.readFileSync('templates/index.html','utf8'); const m=html.match(/function tougaardBackground\\([\\s\\S]*?\\n\\}/); const a=html.match(/function _applyEndpointAveraging\\([\\s\\S]*?\\n\\}/); const _applyEndpointAveraging=eval('('+a[0]+')'); const tougaardBackground=eval('('+m[0]+')'); function p(y,label){const be=y.map((_,i)=>10-i); const bg=tougaardBackground(be,y); console.log(label,'bg',bg.map(v=>Number(v.toFixed(3))).join(','),'min',Math.min(...bg),'max',Math.max(...bg));} p([100,90,80,70,60,50,40,30,20,10,200],'monotone-ish highBE lower than lowBE'); p([100,100,100,100,100,10000,100,100,100,100,200],'central peak with lowBE higher'); p([500,500,500,500,500,10000,500,500,500,500,1000],'decay plus peak');\"" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "node -e \"const fs=require('fs'); const html=fs.readFileSync('templates/index.html','utf8'); const m=html.match(/function tougaardBackground\\([\\s\\S]*?\\n\\}/); const a=html.match(/function _applyEndpointAveraging\\([\\s\\S]*?\\n\\}/); const _applyEndpointAveraging=eval('('+a[0]+')'); const tougaardBackground=eval('('+m[0]+')'); const be=[],intensity=[]; for(let i=0;i<=150;i++){const x=295-.1*i; be.push(x); intensity.push(100+5000*Math.exp(-0.5*Math.pow((x-287)/.8,2))+400/(1+Math.exp(-(287-x))));} const bg=tougaardBackground(be,intensity); console.log([0,30,75,110,149,150].map(i=>i+':'+bg[i]).join('\\n'));\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
monotone-ish highBE lower than lowBE bg 100,117.41,133.799,148.919,162.526,174.384,184.267,191.96,197.266,200,200 min 100 max 200
central peak with lowBE higher bg 100,119.127,139.056,159.653,180.771,202.258,201.361,200.683,200.228,200,200 min 100 max 202.2576457492849
decay plus peak bg 500,595.517,704.069,824.896,957.121,1099.772,1060.153,1030.186,1010.086,1000,1000 min 500 max 1099.7722524146402

 succeeded in 0ms:
0:100.13414005218658
30:219.399138184813
75:461.76541491579786
110:499.7312788702072
149:499.6355795222399
150:499.6355795222399

exec
/bin/zsh -lc "node -e \"const fs=require('fs'); const html=fs.readFileSync('templates/index.html','utf8'); const fn=eval('('+html.match(/function tougaardBackground\\([\\s\\S]*?\\n\\}/)[0]+')'); const avg=eval('('+html.match(/function _applyEndpointAveraging\\([\\s\\S]*?\\n\\}/)[0]+')'); global._applyEndpointAveraging=avg; const be=[291,290,289,288], y=[100,0,0,0]; const bg=fn(be,y); console.log(bg.join(','));\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
0,0,0,0

exec
/bin/zsh -lc "node -e \"const fs=require('fs'); const html=fs.readFileSync('templates/index.html','utf8'); const avg=eval('('+html.match(/function _applyEndpointAveraging\\([\\s\\S]*?\\n\\}/)[0]+')'); const _applyEndpointAveraging=avg; const fn=eval('('+html.match(/function tougaardBackground\\([\\s\\S]*?\\n\\}/)[0]+')'); function p(y){const be=y.map((_,i)=>10-i); const bg=fn(be,y); console.log('y',y.join(',')); console.log('bg',bg.map(v=>Number(v.toFixed(1))).join(','),'min',Math.min(...bg),'max',Math.max(...bg)); console.log('overshoot idx', bg.map((v,i)=>v>y[i]||v<0?i+':'+v.toFixed(1)+'>'+y[i]:null).filter(Boolean).join(' '));} p([0,0,0,0,0,10000,0,0,0,0,1000]); p([0,0,0,0,0,100000,0,0,0,0,1000]); p([400,350,300,250,200,5000,150,100,50,25,1000]);\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
y 0,0,0,0,0,10000,0,0,0,0,1000
bg 0,189.1,556,1098,1810.8,2688.8,2018.2,1510.9,1170.7,1000,1000 min 0 max 2688.8172183079896
overshoot idx 1:189.1>0 2:556.0>0 3:1098.0>0 4:1810.8>0 6:2018.2>0 7:1510.9>0 8:1170.7>0 9:1000.0>0
y 0,0,0,0,0,100000,0,0,0,0,1000
bg 0,191.3,390.5,596.5,807.6,1022.3,1013.5,1006.8,1002.3,1000,1000 min 0 max 1022.3289246060109
overshoot idx 1:191.3>0 2:390.5>0 3:596.5>0 4:807.6>0 6:1013.5>0 7:1006.8>0 8:1002.3>0 9:1000.0>0
y 400,350,300,250,200,5000,150,100,50,25,1000
bg 400,494.2,563.5,605.3,617.3,597.4,753.6,874.7,957.8,1000,1000 min 400 max 1000
overshoot idx 1:494.2>350 2:563.5>300 3:605.3>250 4:617.3>200 6:753.6>150 7:874.7>100 8:957.8>50 9:1000.0>25

codex
The negative-scale probe confirms the expected behavior class: when the low-BE edge is higher than the high-BE edge and a central peak dominates the kernel integral, the signed anchor can produce a background that exceeds local data away from the anchor. That is a real shape pathology, but it follows directly from the unclamped two-edge constraint and does not look like a new caller/API failure.
exec
/bin/zsh -lc "node -e \"const cp=require('child_process'), fs=require('fs'); function load(src){ const am=src.match(/function _applyEndpointAveraging\\([\\s\\S]*?\\n\\}/); if(am){ const _applyEndpointAveraging=eval('('+am[0]+')'); global._applyEndpointAveraging=_applyEndpointAveraging; } else { global._applyEndpointAveraging=(a)=>a; } return eval('('+src.match(/function tougaardBackground\\([\\s\\S]*?\\n\\}/)[0]+')'); } const oldHtml=cp.execSync('git show 3d9ff54"'^:templates/index.html'"',{encoding:'utf8'}); const newHtml=fs.readFileSync('templates/index.html','utf8'); const oldFn=load(oldHtml), newFn=load(newHtml); function flat(fn){const be=[],y=[]; for(let i=0;i<200;i++){be.push(740-40*i/199); y.push(500);} const bg=fn(be,y); return {first:bg[0],last:bg[199],maxnet:Math.max(...y.map((v,i)=>Math.abs(v-bg[i])))};} function synth(fn){const be=[],y=[]; for(let i=0;i<=150;i++){const x=295-.1*i; be.push(x); y.push(100+5000*Math.exp(-0.5*Math.pow((x-287)/.8,2))+400/(1+Math.exp(-(287-x))));} const bg=fn(be,y); return {hi:bg[0],lo:bg[150],wantlo:y[150]};} console.log('old flat', JSON.stringify(flat(oldFn))); console.log('new flat', JSON.stringify(flat(newFn))); console.log('old edges', JSON.stringify(synth(oldFn))); console.log('new edges', JSON.stringify(synth(newFn)));\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4f7wZuag' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1YZOJB41' (errno=Operation not permitted)
old flat {"first":500,"last":0,"maxnet":500}
new flat {"first":500,"last":500,"maxnet":0}
old edges {"hi":100.1341400521866,"lo":0,"wantlo":499.6355795222399}
new edges {"hi":100.13414005218658,"lo":499.6355795222399,"wantlo":499.6355795222399}

codex
I checked the key F1 discriminators against the parent JS implementation: the old code gives flat-window `last=0` and `maxnet=500`, while current gives `last=500` and `maxnet=0`; the old synthetic edge case gives low-BE background `0` versus current `499.635...`. So those rewritten assertions are not laundering the old behavior.
exec
/bin/zsh -lc "node -e \"const fs=require('fs'); let html=fs.readFileSync('templates/index.html','utf8'); let body=html.match(/function tougaardBackground\\([\\s\\S]*?\\n\\}/)[0].replace('const B = 2866, C = 1643;','const B = 2866, C = 1643*1643;'); const avg=eval('('+html.match(/function _applyEndpointAveraging\\([\\s\\S]*?\\n\\}/)[0]+')'); const _applyEndpointAveraging=avg; const fn=eval('('+body+')'); const be=[],y=[]; for(let i=0;i<1001;i++){be.push(100-.1*i); y.push(1e-9);} y[0]=2e-9; y[800]=1e6; const bg=fn(be,y); let max=-Infinity,maxX=NaN; for(let i=0;i<800;i++){if(bg[i]>max){max=bg[i]; maxX=be[i];}} console.log(maxX);\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
100

codex
The squared-`C` regression pin still discriminates with the modified fixture: replacing `C = 1643` with `1643*1643` moves the JS kernel-test argmax to `100 eV`, outside the expected `43.4 eV` window. That supports the same reasoning for the Python twin because the fixture construction is identical.
exec
/bin/zsh -lc "nl -ba app.py | sed -n '200,235p;680,765p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'rg -n "xps-fitting-tool|render_template|send_file|send_from_directory|index.html" app.py CLAUDE.md DEPLOY.md README.md templates static xps-fitting-tool.html' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   200	
   201	
   202	class _AnalyzeContext:
   203	    """Everything _run_analyze_method / _build_analyze_payload need,
   204	    assembled once by _validate_analyze_request."""
   205	
   206	    __slots__ = ("x", "y", "method_id", "opts", "peak_specs", "grammar")
   207	
   208	    def __init__(self, x, y, method_id, opts, peak_specs, grammar):
   209	        self.x = x
   210	        self.y = y
   211	        self.method_id = method_id
   212	        self.opts = opts
   213	        self.peak_specs = peak_specs
   214	        self.grammar = grammar
   215	
   216	
   217	def _validate_analyze_request(body: dict, upload_folder: str) -> _AnalyzeContext:
   218	    """ALL the synchronous, cheap validation /api/analyze has always done
   219	    (session lookup through grammar resolution) — pure extract-method
   220	    refactor, byte-identical checks/messages/order, raising
   221	    ``_AnalyzeError`` in place of the old inline ``return _err(...)``."""
   222	    from autofit.grammar import (MaterialClass, Phase,
   223	                                 PhaseAmbiguityError, UnknownRegionError,
   224	                                 resolve)
   225	
   226	    session_id = body.get("session_id", "")
   227	    _validate_session_id(session_id)
   228	    try:
   229	        energy, counts = _load_session(session_id, upload_folder)
   230	    except KeyError:
   231	        raise _AnalyzeError(f"Session '{session_id}' not found", 404)
   232	
   233	    method_id = body.get("method", "ic_model_comparison")
   234	    if method_id not in _ANALYZE_METHODS:
   235	        raise _AnalyzeError(f"Unknown analyze method '{method_id}' "
   680	        })
   681	
   682	    @app.delete("/api/session/<session_id>")
   683	    def delete_session(session_id: str):
   684	        _validate_session_id(session_id)
   685	        path = _session_path(session_id, app.config["UPLOAD_FOLDER"])
   686	        path.unlink(missing_ok=True)
   687	        return jsonify({"deleted": session_id})
   688	
   689	    # ── Background ────────────────────────────────────────────────────────────
   690	
   691	    @app.post("/api/background")
   692	    @_require_json
   693	    def background():
   694	        """
   695	        Request body
   696	        ------------
   697	        {
   698	          "session_id": "...",
   699	          "method":     "shirley" | "linear" | "none",
   700	          "start_idx":  0,      // optional
   701	          "end_idx":    -1      // optional
   702	        }
   703	        """
   704	        body = request.get_json()
   705	        session_id = body.get("session_id", "")
   706	        _validate_session_id(session_id)
   707	
   708	        try:
   709	            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
   710	        except KeyError:
   711	            return _err(f"Session '{session_id}' not found", 404)
   712	
   713	        method = body.get("method", "shirley")
   714	        start_idx = _parse_int(body.get("start_idx"), 0, len(energy))
   715	        end_idx = _parse_int(body.get("end_idx"), 0, len(energy), default=len(energy))
   716	        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
   717	        try:
   718	            ep_avg = max(1, int(body.get("endpoint_avg", 1)))
   719	        except (TypeError, ValueError):
   720	            return _err("endpoint_avg must be an integer")
   721	
   722	        try:
   723	            result = fitting.compute_background_only(
   724	                energy, counts, method=method,
   725	                start_idx=start_idx, end_idx=end_idx,
   726	                endpoint_avg=ep_avg,
   727	            )
   728	        except ValueError as exc:
   729	            # Our own validation, e.g. "Unknown background method" (audit F10).
   730	            return _err(str(exc))
   731	        except Exception:
   732	            app.logger.exception("Unexpected background error")
   733	            return _err("Internal background error — see server log.", 500)
   734	
   735	        return jsonify(result)
   736	
   737	    # ── Peak fitting ──────────────────────────────────────────────────────────
   738	
   739	    @app.post("/api/fit")
   740	    @_require_json
   741	    def fit():
   742	        """
   743	        Request body
   744	        ------------
   745	        {
   746	          "session_id": "...",
   747	
   748	          "background": {
   749	            "method":    "shirley",   // "shirley" | "linear" | "none"
   750	            "start_idx": 0,           // optional – slice into data array
   751	            "end_idx":   -1           // optional
   752	          },
   753	
   754	          "peaks": [
   755	            {
   756	              "id":           "p1",               // unique string id
   757	              "shape":        "pseudo_voigt_gl",  // peak lineshape
   758	              "center":       284.8,
   759	              "center_min":   283.0,              // optional bound
   760	              "center_max":   286.0,              // optional bound
   761	              "amplitude":    10000,
   762	              "amplitude_min": 0,                 // optional (default 0)
   763	              "fwhm":         1.5,
   764	              "fwhm_min":     0.2,                // optional
   765	              "fwhm_max":     3.0,                // optional

 exited 2 in 0ms:
rg: README.md: No such file or directory (os error 2)
DEPLOY.md:31:Production gunicorn serves `templates/index.html` and `data/xps/**` from disk,
CLAUDE.md:6:`templates/index.html`. Deployed at xps.fortierlab.org via a gunicorn
CLAUDE.md:15:- **Frontend:** Single-page HTML/JS in `templates/index.html` (~8500 LOC). Vanilla JS, no build step.
CLAUDE.md:26:templates/index.html      # Frontend — CSS + HTML + JS in one file
CLAUDE.md:34:The Flask backend serves the frontend via `render_template('index.html')`
CLAUDE.md:45:| `GET`    | `/`                       | Serve the frontend (`templates/index.html`). |
CLAUDE.md:78:`TabManager` (a class in `templates/index.html`) holds `tabs[]` and an
CLAUDE.md:187:- `defaultPeak` defaults block in `templates/index.html`
CLAUDE.md:244:`runFitLocal` in `templates/index.html` is a JS Levenberg-Marquardt
CLAUDE.md:402:  (`templates/index.html` around the `data-xps-tip` listeners); events
CLAUDE.md:406:  `templates/index.html` are NOT picked up** outside Flask debug mode
CLAUDE.md:414:  `templates/index.html`. Browser-verify changes on a separate dev
app.py:492:        # Serve index.html from the templates folder when the frontend is ready
app.py:493:        from flask import render_template, send_from_directory
app.py:496:        if templates.exists() and (templates / "index.html").exists():
app.py:509:            return render_template("index.html", legacy_reference=legacy)
app.py:510:        if static.exists() and (static / "index.html").exists():
app.py:511:            return send_from_directory(str(static), "index.html")
app.py:514:            "<p>Frontend not yet installed.  Place your <code>index.html</code> "
static/js/ref_identify_core.js:3: * workspace. THE SHIPPED MODULE: index.html must not copy these functions.
static/js/ref_identify_core.js:20:  // --amber design tokens in index.html.
static/js/batch_propagation.js:3: * propagation. THE SHIPPED MODULE: index.html must not copy this function.
templates/index.html:1277:     templates/index.html ~10442/11158) — but unlike that grid, THIS one

exec
/bin/zsh -lc 'git ls-files xps-fitting-tool.html templates/index.html templates/index.html.pre-audit' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8McUbA8J' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-KznkJxae' (errno=Operation not permitted)
templates/index.html
templates/index.html.pre-audit
xps-fitting-tool.html

codex
The stale top-level `xps-fitting-tool.html` still has the old Tougaard code, but `app.py` and repo docs identify `templates/index.html` as the served frontend. I’m not treating that stale HTML copy as an active caller for this scoped commit.
exec
/bin/zsh -lc "nl -ba app.py | sed -n '486,514p;780,835p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   486	def _register_routes(app: Flask) -> None:
   487	
   488	    # ── Index ─────────────────────────────────────────────────────────────────
   489	
   490	    @app.route("/")
   491	    def index():
   492	        # Serve index.html from the templates folder when the frontend is ready
   493	        from flask import render_template, send_from_directory
   494	        templates = Path(app.template_folder)
   495	        static = Path(app.static_folder) if app.static_folder else Path("static")
   496	        if templates.exists() and (templates / "index.html").exists():
   497	            # Inject the validated legacy reference data synchronously so the
   498	            # survey-marker / NIST-modal consumers (rewired to the unified
   499	            # accessor in Stage 9) have it at parse time — no async-load race.
   500	            # Falls back to null on validation failure; the frontend accessor
   501	            # degrades gracefully (and, pre-cutover, the legacy constants
   502	            # remain as a backstop).
   503	            try:
   504	                legacy = load_reference_cached(app.config["XPS_DATA_DIR"]).get("legacy")
   505	            except XPSReferenceError as e:
   506	                logging.getLogger(__name__).error(
   507	                    "legacy reference unavailable for template injection: %s", e)
   508	                legacy = None
   509	            return render_template("index.html", legacy_reference=legacy)
   510	        if static.exists() and (static / "index.html").exists():
   511	            return send_from_directory(str(static), "index.html")
   512	        return (
   513	            "<h1>XPS Fitting API</h1>"
   514	            "<p>Frontend not yet installed.  Place your <code>index.html</code> "
   780	        _validate_session_id(session_id)
   781	
   782	        try:
   783	            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
   784	        except KeyError:
   785	            return _err(f"Session '{session_id}' not found", 404)
   786	
   787	        # Background config
   788	        bg_cfg = body.get("background", {})
   789	        bg_method = bg_cfg.get("method", "shirley")
   790	        bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
   791	        bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
   792	        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
   793	        try:
   794	            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
   795	        except (TypeError, ValueError):
   796	            return _err("endpoint_avg must be an integer")
   797	        manual_bg = bg_cfg.get("manual_bg")
   798	
   799	        # Peak specs
   800	        peak_specs = body.get("peaks", [])
   801	        if not peak_specs:
   802	            return _err("'peaks' list is empty – provide at least one peak")
   803	
   804	        # Validate peak ids are unique
   805	        ids = [p.get("id") for p in peak_specs]
   806	        if len(ids) != len(set(ids)):
   807	            return _err("Duplicate peak ids found – each peak must have a unique 'id'")
   808	
   809	        _ALLOWED_METHODS = {
   810	            "leastsq", "least_squares", "nelder",
   811	            "differential_evolution", "basinhopping",
   812	        }
   813	        fit_method = body.get("fit_method", "leastsq")
   814	        if fit_method not in _ALLOWED_METHODS:
   815	            return _err(f"Unknown fit_method '{fit_method}'")
   816	
   817	        # Bounded, type-checked n_perturb (audit F7; also covers the F9
   818	        # ValueError-on-bad-input case for this field). Reject out-of-range or
   819	        # non-integer values with a clean 400 instead of a 500 or a worker hang.
   820	        try:
   821	            n_perturb = int(body.get("n_perturb", 5))
   822	        except (TypeError, ValueError):
   823	            return _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
   824	        if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
   825	            return _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
   826	
   827	        try:
   828	            result = fitting.run_fit(
   829	                energy=energy,
   830	                counts=counts,
   831	                peak_specs=peak_specs,
   832	                background_method=bg_method,
   833	                bg_start_idx=bg_start,
   834	                bg_end_idx=bg_end,
   835	                charge_shift_ev=0.0,

codex
1. No findings. I did not find a BLOCKER/MAJOR/MINOR issue in commit `3d9ff54`.

Scope checks passed: `fitting.py` changes are confined to `tougaard_background`; `templates/index.html` changes are confined to `tougaardBackground`; `autofit/engine.py`, `autofit/methods/*.py`, `app.py` `/api/fit`, and peak math have no diff in this commit.

Test/caller checks: `node --test tests/js/tougaard_twin.test.js` passes 6/6. Python tests could not be run here because `pytest` and `lmfit` are not installed in the sandbox. Static review plus JS probes confirmed the key F1 assertions fail against the parent behavior: old flat window gives `maxnet=500`, current gives `0`; old low-BE edge gives `0`, current tracks `499.635...`. The squared-`C` guard still discriminates: forcing `C=1643*1643` moves the kernel argmax to `100 eV`.

Adversarial notes: C0-from-edge is a pragmatic endpoint model, not a robust estimator; if the ROI edge sits on a tail/shoulder or strong slope, `n_avg` only reduces noise, it does not solve model bias. Negative-scale/overshoot cases are constructible when low-BE exceeds high-BE and a central peak dominates, but that matches the project’s existing unclamped behavior rather than a new scoped correctness bug. Grep/zip inspection found no Tougaard numeric pins outside the touched test files.

VERDICT: GO
tokens used
185,515
1. No findings. I did not find a BLOCKER/MAJOR/MINOR issue in commit `3d9ff54`.

Scope checks passed: `fitting.py` changes are confined to `tougaard_background`; `templates/index.html` changes are confined to `tougaardBackground`; `autofit/engine.py`, `autofit/methods/*.py`, `app.py` `/api/fit`, and peak math have no diff in this commit.

Test/caller checks: `node --test tests/js/tougaard_twin.test.js` passes 6/6. Python tests could not be run here because `pytest` and `lmfit` are not installed in the sandbox. Static review plus JS probes confirmed the key F1 assertions fail against the parent behavior: old flat window gives `maxnet=500`, current gives `0`; old low-BE edge gives `0`, current tracks `499.635...`. The squared-`C` guard still discriminates: forcing `C=1643*1643` moves the kernel argmax to `100 eV`.

Adversarial notes: C0-from-edge is a pragmatic endpoint model, not a robust estimator; if the ROI edge sits on a tail/shoulder or strong slope, `n_avg` only reduces noise, it does not solve model bias. Negative-scale/overshoot cases are constructible when low-BE exceeds high-BE and a central peak dominates, but that matches the project’s existing unclamped behavior rather than a new scoped correctness bug. Grep/zip inspection found no Tougaard numeric pins outside the touched test files.

VERDICT: GO
