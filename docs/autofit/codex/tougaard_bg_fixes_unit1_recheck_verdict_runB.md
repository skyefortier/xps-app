OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f721d-6a55-7483-ba4b-6028c92d5c6a
--------
user
You are an adversarial reviewer for a scoped follow-up commit in this repo
(XPS peak-fitting web app), branch feature-autofit-stage2. This is a RECHECK
of a prior review round, not a fresh review — read the disposition below
before diffing anything.

CONTEXT: commit 3d9ff54 ("fix(fitting): Tougaard pre-loss constant (F1) +
non-uniform quadrature weights (F2)") was reviewed twice already. One run
returned GO with no findings. The other run returned NO-GO with one MAJOR
finding: `test_nonuniform_grid_uses_local_quadrature_weights`
(tests/test_tougaard_background.py) used a fixture where both window edges
sat at ~4000 counts (a symmetric Gaussian on a flat baseline), so the F1
amplitude anchor — which rescales the whole background by
`(ya[0]-c0)/bg[0]` — collapsed the signal toward zero on that fixture. The
reviewer proved (by reimplementing tougaard_background with the F2
weighting term removed and re-running the test's own comparison) that the
test would still pass even with F2 fully reverted from production: max
diff was 4.5e-13, far inside the test's rtol=1e-9.

THE FIX, now in commit 173f002 ("fix(tests): ..."): the fixture gained a
genuine high-BE endpoint rise (a linear ramp under the Gaussian, ~800-count
endpoint delta) so the anchor scale stays non-degenerate, plus an explicit
"guard the guard" assertion that the weighted and unweighted reference
implementations diverge by more than 10 counts before trusting the
allclose comparison between them. `git show 173f002` gives the full diff —
it touches ONLY tests/test_tougaard_background.py; fitting.py has zero
diff in this commit (the production F2 fix from 3d9ff54 is unchanged).

YOUR JOB — verify the fix actually closes the finding, and look for new
problems it might have introduced:

1. Does the new fixture (xa = concatenated dense/sparse nonuniform grid,
   ya = 4000 + 800*(xa-700)/40 + 6000*gaussian(xa, 710.9, 1.6)) actually
   produce a meaningful endpoint delta that survives the F1 anchor? Confirm
   by computation, not just reading the comment.
2. Does removing the F2 `w[i:]` weighting from a working copy of
   tougaard_background now make THIS test fail? (This is the load-bearing
   claim — reproduce the reviewer's own methodology from the prior round:
   reimplement the unweighted version, run it through the test's actual
   assertions, confirm failure.)
3. Does the "guard the guard" assertion (`max(abs(ref - ref_unweighted)) >
   10.0`) itself hold on this fixture, and is 10.0 counts a reasonable
   margin given the ~105-count divergence measured, or is it either so
   loose it could pass by accident or so tight it's fragile to unrelated
   changes?
4. Scope check: confirm fitting.py, templates/index.html,
   tests/js/tougaard_twin.test.js, autofit/engine.py, autofit/methods/*.py,
   and /api/fit have ZERO diff in commit 173f002 — this must be a pure
   test-only fix.
5. Re-run (or re-verify) the other 8 tests in
   tests/test_tougaard_background.py plus the 6 tests in
   tests/js/tougaard_twin.test.js still pass unmodified/unaffected.
6. Any OTHER regression pin in this test file (or the JS twin) that shares
   the same class of bug — an assertion that looks like it exercises a code
   path but is actually neutralized by a fixture choice (endpoint
   collapse, degenerate guard, etc.)? Do a fresh sweep, don't just take the
   "only one MAJOR finding" disposition on faith.

Also re-confirm the two items the FIRST round's GO run already checked
(cheap to re-verify, don't skip): (a) no saved-fit fixture or inventory
JSON anywhere in the repo pins Tougaard numeric output; (b) the negative-
scale anchoring behavior (baseline falls with BE -> negative scale factor,
passed through unclamped) is a deliberate, pre-existing project stance,
not a new bug introduced by this change.

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll recheck this as a review, focusing on whether the new test actually fails under an F2 revert and whether the commit stays test-only. I’ll start by inspecting the target commit diff and the Tougaard tests, then run focused computations/tests where the read-only workspace allows it.
exec
/bin/zsh -lc 'git show --unified=80 173f002 -- tests/test_tougaard_background.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GtYVrIEK' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-SbSBOfVu' (errno=Operation not permitted)
commit 173f0025cb843948111fa8e880b6bef053949ca5
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Fri Jul 17 16:05:11 2026 -0600

    fix(tests): test_nonuniform_grid_uses_local_quadrature_weights didn't guard F2
    
    Codex review of 3d9ff54 (run B) caught a laundered regression pin: the
    fixture put a symmetric Gaussian on a flat baseline, so both window edges
    sat at ~4000 counts (endpoint delta ~5e-7). The F1 anchor scales the whole
    background by (ya[0]-c0)/bg[0], which collapsed to near-zero on that
    fixture — so the F2 weighted-vs-unweighted difference (measured ~105
    counts on a fixture with a real endpoint rise) vanished into the noise
    floor after anchoring. Independently verified: reverting the w[i:]
    weighting entirely from tougaard_background still passed this assertion
    (max diff 4.5e-13, well inside rtol=1e-9), i.e. the pin did not fail if F2
    regressed.
    
    Fix: give the fixture a genuine high-BE endpoint rise (linear ramp under
    the Gaussian) so the anchor scale stays non-degenerate, and add an
    explicit "guard the guard" assertion that the weighted/unweighted
    reference implementations actually diverge by a meaningful margin (>10
    counts) before trusting the allclose comparison between them.
    
    Verified red/green: reverting fitting.py's w[i:] weighting makes the
    rewritten test fail; restoring it passes. fitting.py itself is untouched
    by this commit — test-only fix. All 9 Python + 6 JS Tougaard tests pass.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

diff --git a/tests/test_tougaard_background.py b/tests/test_tougaard_background.py
index 84cb4ca..bb5e504 100644
--- a/tests/test_tougaard_background.py
+++ b/tests/test_tougaard_background.py
@@ -149,105 +149,129 @@ def test_background_anchored_at_high_be_edge():
 def test_no_loss_signal_returns_flat_pre_loss_level():
     """Degenerate input: no net loss signal accumulates at the high-BE edge
     (bg[0] == 0 — counts are zero everywhere below the edge point).
 
     Supersedes the 2026-07-04 Codex pin ``..._returns_unanchored_zeros``.
     That pin asserted all-zeros, which was correct ONLY while the background
     carried no constant term: with the F1 offset fix (2026-07-17) the honest
     answer for a window containing no modellable loss signal is the flat
     pre-loss level C0, not zero. Returning zeros would report the entire
     baseline as net signal — the exact failure F1 fixes. The guard itself
     still exists (no force-matching to the edge intensity, no divide-by-zero);
     only its fallback VALUE changed from 0 to C0. Mirrored in the JS twin."""
     x = np.array([291.0, 290.0, 289.0, 288.0])  # descending
     y = np.array([100.0, 0.0, 0.0, 0.0])        # signal only at the edge itself
     bg = tougaard_background(x, y)
     assert np.array_equal(bg, np.zeros(4)), (
         f"C0 is 0.0 here (low-BE edge counts are zero), so the flat pre-loss "
         f"level IS zeros; got {bg}"
     )
 
 
 def test_flat_window_yields_no_phantom_signal():
     """F1 regression pin (2026-07-17): a flat, featureless window must yield
     ~zero net counts everywhere.
 
     Before the offset fix, K(0) = 0 forced the background to zero at the
     low-BE edge regardless of the data, so a flat 500-count window produced a
     background ramping 0 -> 500 and reported up to 500 counts of phantom
     "signal" fabricated from a featureless baseline."""
     x = np.linspace(740.0, 700.0, 200)   # descending, flat data
     y = np.full_like(x, 500.0)
     bg = tougaard_background(x, y)
     net = y - bg
     assert np.max(np.abs(net)) < 1e-6, (
         f"flat window must leave ~zero net; net spans "
         f"{net.min():.3f}..{net.max():.3f}"
     )
 
 
 def test_background_tracks_low_be_baseline_on_wide_region():
     """F1 regression pin (2026-07-17): on a wide 2p-like region sitting on a
     large out-of-window inelastic baseline, the background must track that
     baseline at the low-BE edge instead of diving to zero."""
     x = np.linspace(740.0, 700.0, 600)   # descending
     pk = (6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2)
           + 3000.0 * np.exp(-0.5 * ((x - 724.5) / 1.9) ** 2))
     baseline = 4000.0 + 3000.0 * np.cumsum(pk[::-1])[::-1] / np.sum(pk)
     y = pk + baseline
     bg = tougaard_background(x, y)
     # low-BE edge is index -1 on this descending grid
     assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
         f"low-BE edge dove to {bg[-1]:.1f} instead of tracking the "
         f"{y[-1]:.1f}-count baseline"
     )
     assert np.isclose(bg[0], y[0], rtol=1e-12)
 
 
 def test_nonuniform_grid_uses_local_quadrature_weights():
     """F2 regression pin (2026-07-17): the nonuniform-grid branch must weight
     each term by its local energy spacing.
 
     It previously used exact per-point separations but omitted the spacing
     weights, silently applying uniform-grid quadrature inside the branch
     written precisely BECAUSE the grid is not uniform (~24% error on a
     genuinely nonuniform grid). np.gradient returns dx exactly on a uniform
     grid, so the two branches must now agree to floating point -- the
     uniformity test is an optimization, not a semantic fork."""
     # Uniform grid, then the same grid perturbed below the uniformity
     # tolerance so the nonuniform branch runs on near-identical data.
     x = np.linspace(740.0, 700.0, 300)
     y = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))
     bg_uniform = tougaard_background(x, y)
     x_jitter = x.copy()
     x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
     bg_nonuniform = tougaard_background(x_jitter, y)
     assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
         "uniform and nonuniform branches disagree on near-identical grids"
     )
 
     # Genuinely nonuniform grid vs an explicit spacing-weighted reference.
+    # A high-BE endpoint RISE (not just a symmetric peak on a flat baseline)
+    # is required here: the F1 anchor rescales by (ya[0]-c0)/bg[0], so a
+    # fixture whose two edges sit at nearly the same level collapses that
+    # scale factor toward zero and the F2 weighting difference vanishes
+    # into the noise floor *after* anchoring -- passing this assertion even
+    # with the w[i:] weighting removed entirely (caught by Codex review,
+    # 2026-07-17: the original flat-baseline fixture measured a 4.5e-13 max
+    # diff between weighted and unweighted output, i.e. it did not actually
+    # guard F2). The endpoint delta below (~800 counts) keeps the anchored
+    # scale non-degenerate, so the ~105-count weighted-vs-unweighted
+    # divergence survives anchoring and this pin is falsifiable again.
     xa = np.concatenate([np.linspace(740.0, 720.1, 60),
                          np.linspace(720.0, 700.0, 400)])
-    ya = np.interp(xa[::-1], x[::-1], y[::-1])[::-1]
+    ya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(
+        -0.5 * ((xa - 710.9) / 1.6) ** 2
+    )
     got = tougaard_background(xa, ya)
 
     B_coef, C_coef = 2866.0, 1643.0
     c0 = float(ya[-1])
     net = ya - c0
     w = np.abs(np.gradient(xa))
     ref = np.zeros(len(xa))
+    ref_unweighted = np.zeros(len(xa))
     for i in range(len(xa)):
         T = np.abs(xa[i:] - xa[i])
-        ref[i] = float(np.sum((B_coef * T) / (C_coef + T * T) ** 2 * net[i:] * w[i:]))
+        kernel = (B_coef * T) / (C_coef + T * T) ** 2
+        ref[i] = float(np.sum(kernel * net[i:] * w[i:]))
+        ref_unweighted[i] = float(np.sum(kernel * net[i:]))
     ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
+    ref_unweighted = c0 + ref_unweighted * ((float(ya[0]) - c0) / ref_unweighted[0])
+
+    # The pin only means something if weighted and unweighted actually
+    # disagree on this fixture -- guard the guard.
+    assert np.max(np.abs(ref - ref_unweighted)) > 10.0, (
+        "fixture does not separate weighted from unweighted quadrature -- "
+        "endpoint delta too small to survive the F1 anchor, pin is dead"
+    )
     assert np.allclose(got, ref, rtol=1e-9), (
         "nonuniform branch does not match spacing-weighted quadrature"
     )
 
 
 def test_short_input_returns_zeros():
     """< 2 points: no background can be defined; must return zeros."""
     assert np.array_equal(
         tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
     )
     assert tougaard_background(np.array([]), np.array([])).size == 0

exec
/bin/zsh -lc 'git show --stat --oneline 173f002 && git show --name-only --format=fuller 173f002' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Cjt0Walk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BUQGUdHi' (errno=Operation not permitted)
173f002 fix(tests): test_nonuniform_grid_uses_local_quadrature_weights didn't guard F2
 tests/test_tougaard_background.py | 28 ++++++++++++++++++++++++++--
 1 file changed, 26 insertions(+), 2 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-pxtnnft9' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qUPKf24A' (errno=Operation not permitted)
commit 173f0025cb843948111fa8e880b6bef053949ca5
Author:     Skye Fortier <skyefortier@gmail.com>
AuthorDate: Fri Jul 17 16:05:11 2026 -0600
Commit:     Skye Fortier <skyefortier@gmail.com>
CommitDate: Fri Jul 17 16:05:11 2026 -0600

    fix(tests): test_nonuniform_grid_uses_local_quadrature_weights didn't guard F2
    
    Codex review of 3d9ff54 (run B) caught a laundered regression pin: the
    fixture put a symmetric Gaussian on a flat baseline, so both window edges
    sat at ~4000 counts (endpoint delta ~5e-7). The F1 anchor scales the whole
    background by (ya[0]-c0)/bg[0], which collapsed to near-zero on that
    fixture — so the F2 weighted-vs-unweighted difference (measured ~105
    counts on a fixture with a real endpoint rise) vanished into the noise
    floor after anchoring. Independently verified: reverting the w[i:]
    weighting entirely from tougaard_background still passed this assertion
    (max diff 4.5e-13, well inside rtol=1e-9), i.e. the pin did not fail if F2
    regressed.
    
    Fix: give the fixture a genuine high-BE endpoint rise (linear ramp under
    the Gaussian) so the anchor scale stays non-degenerate, and add an
    explicit "guard the guard" assertion that the weighted/unweighted
    reference implementations actually diverge by a meaningful margin (>10
    counts) before trusting the allclose comparison between them.
    
    Verified red/green: reverting fitting.py's w[i:] weighting makes the
    rewritten test fail; restoring it passes. fitting.py itself is untouched
    by this commit — test-only fix. All 9 Python + 6 JS Tougaard tests pass.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

tests/test_tougaard_background.py

exec
/bin/zsh -lc 'git status --short && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fvN6A5TH' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JoUmp3B3' (errno=Operation not permitted)
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UfWdFXRY' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-KS79vOf2' (errno=Operation not permitted)
feature-autofit-stage2
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gA1aWFfu' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-nQtew7G1' (errno=Operation not permitted)
03b656aff4ec533bef308447051d4539cfb7af63

codex
The commit is indeed a one-file diff by `git show --name-only`, and the working tree has unrelated untracked data fixtures under `docs/autofit/test_data`. I’ll leave those alone and use read-only checks plus isolated scripts rather than modifying the working copy.
exec
/bin/zsh -lc "nl -ba tests/test_tougaard_background.py | sed -n '1,280p'" in /Users/skyefortier/xps-verify
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
   229	    # A high-BE endpoint RISE (not just a symmetric peak on a flat baseline)
   230	    # is required here: the F1 anchor rescales by (ya[0]-c0)/bg[0], so a
   231	    # fixture whose two edges sit at nearly the same level collapses that
   232	    # scale factor toward zero and the F2 weighting difference vanishes
   233	    # into the noise floor *after* anchoring -- passing this assertion even
   234	    # with the w[i:] weighting removed entirely (caught by Codex review,
   235	    # 2026-07-17: the original flat-baseline fixture measured a 4.5e-13 max
   236	    # diff between weighted and unweighted output, i.e. it did not actually
   237	    # guard F2). The endpoint delta below (~800 counts) keeps the anchored
   238	    # scale non-degenerate, so the ~105-count weighted-vs-unweighted
   239	    # divergence survives anchoring and this pin is falsifiable again.
   240	    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
   241	                         np.linspace(720.0, 700.0, 400)])
   242	    ya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(
   243	        -0.5 * ((xa - 710.9) / 1.6) ** 2
   244	    )
   245	    got = tougaard_background(xa, ya)
   246	
   247	    B_coef, C_coef = 2866.0, 1643.0
   248	    c0 = float(ya[-1])
   249	    net = ya - c0
   250	    w = np.abs(np.gradient(xa))
   251	    ref = np.zeros(len(xa))
   252	    ref_unweighted = np.zeros(len(xa))
   253	    for i in range(len(xa)):
   254	        T = np.abs(xa[i:] - xa[i])
   255	        kernel = (B_coef * T) / (C_coef + T * T) ** 2
   256	        ref[i] = float(np.sum(kernel * net[i:] * w[i:]))
   257	        ref_unweighted[i] = float(np.sum(kernel * net[i:]))
   258	    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
   259	    ref_unweighted = c0 + ref_unweighted * ((float(ya[0]) - c0) / ref_unweighted[0])
   260	
   261	    # The pin only means something if weighted and unweighted actually
   262	    # disagree on this fixture -- guard the guard.
   263	    assert np.max(np.abs(ref - ref_unweighted)) > 10.0, (
   264	        "fixture does not separate weighted from unweighted quadrature -- "
   265	        "endpoint delta too small to survive the F1 anchor, pin is dead"
   266	    )
   267	    assert np.allclose(got, ref, rtol=1e-9), (
   268	        "nonuniform branch does not match spacing-weighted quadrature"
   269	    )
   270	
   271	
   272	def test_short_input_returns_zeros():
   273	    """< 2 points: no background can be defined; must return zeros."""
   274	    assert np.array_equal(
   275	        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
   276	    )
   277	    assert tougaard_background(np.array([]), np.array([])).size == 0

exec
/bin/zsh -lc 'rg -n "def tougaard_background|tougaard_background|Tougaard|/api/fit|fit" fitting.py templates/index.html tests/js/tougaard_twin.test.js autofit/engine.py autofit/methods -S' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/js/tougaard_twin.test.js:1:// Tougaard background — JS twin of fitting.py's tougaard_background.
tests/js/tougaard_twin.test.js:6:// tests/test_tougaard_background.py):
tests/js/tougaard_twin.test.js:9://      S. Tougaard, Surf. Interface Anal. 11, 453 (1988).
tests/js/tougaard_twin.test.js:54:  // fitted amplitude is proportional to the measured rise across the window
tests/js/tougaard_twin.test.js:111:test('agrees with the backend implementation (fitting.py) on the same spectrum', () => {
tests/js/tougaard_twin.test.js:115:  //   import numpy as np; from fitting import tougaard_background
tests/js/tougaard_twin.test.js:119:  //   bg = tougaard_background(x, y)
tests/js/tougaard_twin.test.js:148:// (fitting.py run_fit / compute_background_only both do
tests/js/tougaard_twin.test.js:149:// tougaard_background(x, _apply_endpoint_averaging(y, n))).
autofit/engine.py:2:Model-comparison engine — the fitalg pipeline ported onto main's fitting.py
autofit/engine.py:5:Pipeline per candidate: primary fit → N perturbed refits (stability) →
autofit/engine.py:9:Provenance: ported from the public ``xps-app-fitalg`` repo's
autofit/engine.py:13:- lineshape layer rebuilt against CURRENT ``fitting.py``: fitalg's
autofit/engine.py:26:sensitivity-test before publication claims); they carry fitalg's defaults.
autofit/engine.py:38:from lmfit import Model, Parameters
autofit/engine.py:39:from lmfit.model import ModelResult
autofit/engine.py:42:from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background
autofit/engine.py:60:# UNVERIFIED tunables (fitalg defaults; spec §9 sensitivity-test items)
autofit/engine.py:72:#       and the fixed-bound refit gives an honest parameter count;
autofit/engine.py:73:#   (2) the refit's BIC* beats the best clean candidate's by more than
autofit/engine.py:80:#       flagged windows) — evidence that it is genuinely mis-fitting, not
autofit/engine.py:84:# Without any override, a clean-but-terrible fit masks a decisively better
autofit/engine.py:85:# fit that merely brushes a constraint wall (observed on the U 4f + N 1s
autofit/engine.py:86:# co-fit: clean χ²ᵣ 38 vs boundary-limited χ²ᵣ 7).
autofit/engine.py:95:# Relative χ² tolerance for counting multi-start fits as landing in the SAME
autofit/engine.py:111:# no known-broad justification) is NOT silently widened: the fit is held at
autofit/engine.py:113:# conditional/low-confidence), per the fit-quality rail "a defensible fit
autofit/engine.py:119:# widths — e.g. a real-data 281 eV feature fitting at 3.0 eV).
autofit/engine.py:133:# residual.  fitalg's Iteration B was already capped/timeout-guarded; this
autofit/engine.py:139:# PROPOSAL_MAX_PER_CANDIDATE accepted rounds of (augmented fit + stability).
autofit/engine.py:144:# n_refits=4 stability of a slow augmented model to 3 attempts and QUANTIZED
autofit/engine.py:148:# because the 4th refit never ran.  35 s fits n_refits=4 at the measured
autofit/engine.py:149:# ~7-8 s worst-case per refit on 191-point real data.  UNVERIFIED tunable.
autofit/engine.py:152:# started inside the proposal pass.  A single fit_candidate at
autofit/engine.py:156:# (Codex c1s-fix review, run B MAJOR).  A proposal attempt that cannot fit
autofit/engine.py:160:# See fit_candidate() docstring: deterministic per-call ceiling on lmfit's
autofit/engine.py:164:                                 # finite fit (measured need: ~33 evals;
autofit/engine.py:167:# Wall-clock ceiling on ONE candidate's entire primary-fit + stability-refit
autofit/engine.py:171:# taking further stability refits rather than consuming the rest of the
autofit/engine.py:174:# couple of such calls (primary + 1-2 refits) before cutting the rest.
autofit/engine.py:181:# fits already runs ~3-4 minutes, and several candidates hitting the
autofit/engine.py:197:# ── Pre-fit out-of-grammar dominant seeding (unit F1, 2026-07-07) ──────────
autofit/engine.py:201:# candidate faces an unfittable 40k-count residual — fits either burn
autofit/engine.py:203:# floors (χ²ᵣ ~656), and the post-fit proposal pass can only patch ONE
autofit/engine.py:207:# absent-eligible, region-`unassigned` slots BEFORE fitting — the proposal
autofit/engine.py:209:# adjudication, never window inheritance), moved ahead of the fit so the
autofit/engine.py:241:                                       # fitted width ≥ this × the slot's
autofit/engine.py:257:# candidate set is larger than SCREEN_TOP_K, compare_models first fits EVERY
autofit/engine.py:258:# candidate once (primary fit only, SCREEN_MAX_NFEV effort cap), ranks the
autofit/engine.py:261:# fit as that candidate's primary, so no work repeats.  Candidates screened
autofit/engine.py:279:    """Slot role → lmfit parameter-name prefix (must match grammar._slot_param_prefix)."""
autofit/engine.py:293:        from fitting import smart_experimental_background
autofit/engine.py:298:        from fitting import tougaard_background
autofit/engine.py:299:        return tougaard_background(x, y)
autofit/engine.py:304:# lmfit model construction
autofit/engine.py:313:                f"Shape {shape_name!r} not registered in fitting._SHAPE_FUNCS"
autofit/engine.py:339:    # DS+G: fitalg convention — slot.fwhm_range bounds m_gauss (the Gaussian
autofit/engine.py:416:    """Opt-in "fit the entire window" (unit 1, 2026-07-13): per-slot center
autofit/engine.py:465:    fit_full_window: bool = False,
autofit/engine.py:469:    ``fit_full_window`` (default False — every existing caller's behavior
autofit/engine.py:493:                       if fit_full_window else {})
autofit/engine.py:511:    # order so a chain (main ← sat7/2 ← sat5/2) resolves: lmfit exprs may
autofit/engine.py:620:    fwhm: float          # width-parameter value (m_gauss for DS+G — fitalg convention)
autofit/engine.py:634:    lmfit_result: Optional[ModelResult] = None
autofit/engine.py:639:def _extract_fitted_components(
autofit/engine.py:748:    proposal slots (all capped AT the ordinary ceiling) — that fits at/above
autofit/engine.py:784:            # (fitting.py convention) — the MEAN effective width
autofit/engine.py:822:def fit_candidate(
autofit/engine.py:829:    fit_full_window: bool = False,
autofit/engine.py:831:    """One fit of ``model`` to (x, y, weights); background subtracted first.
autofit/engine.py:833:    ``max_nfev`` bounds leastsq's own effort per call. lmfit's default
autofit/engine.py:834:    (200000*(nvars+1), see lmfit.Minimizer) is effectively unbounded: a
autofit/engine.py:840:    investigation) showed a clean bimodal split: converged fits topped out
autofit/engine.py:842:    between the two so lmfit's own AbortFitException (caught internally by
autofit/engine.py:844:    deterministically, without clipping legitimate slow-but-converging fits.
autofit/engine.py:855:                                   fit_full_window=fit_full_window)
autofit/engine.py:858:        result = composite.fit(y_sub, params, x=x, weights=weights,
autofit/engine.py:871:            # χ²).  Fires ONLY on a failed-but-finite fit, so converging
autofit/engine.py:872:            # fits are byte-identical; cost is bounded by one
autofit/engine.py:873:            # WARM_RESTART_MAX_NFEV fit.
autofit/engine.py:874:            retry = composite.fit(y_sub, result.params.copy(), x=x,
autofit/engine.py:881:        log.debug("fit_candidate failed for %s: %s", model.name, exc)
autofit/engine.py:886:            n_data=len(y_sub), lmfit_result=None, background=bg,
autofit/engine.py:889:    unweighted_r = y_sub - result.best_fit
autofit/engine.py:892:        components=_extract_fitted_components(result, model),
autofit/engine.py:897:        lmfit_result=result,
autofit/engine.py:906:    if primary.lmfit_result is None:
autofit/engine.py:908:    composite = primary.lmfit_result.model
autofit/engine.py:909:    params = primary.lmfit_result.params
autofit/engine.py:928:    fit_full_window: bool = False,
autofit/engine.py:931:    Perturbed starting parameters for a multi-start refit (bounds-clipped).
autofit/engine.py:933:    Port improvement over fitalg: when (x, y_net) are provided the defaults
autofit/engine.py:936:    (and systematically failed) stability refits on peaks brighter than 1e5
autofit/engine.py:941:                                        fit_full_window=fit_full_window)
autofit/engine.py:989:    """``bound_override`` (fit_full_window, unit 1 2026-07-13): the SAME
autofit/engine.py:990:    widened bound the fit itself was built with
autofit/engine.py:991:    (``_full_window_bound_overrides``) — a primary slot's fitted position
autofit/engine.py:993:    to search, or a component the widened fit correctly placed outside
autofit/engine.py:1014:    """Assign fitted peaks to grammar slots (role + effective window + width).
autofit/engine.py:1016:    ``bound_overrides`` (fit_full_window) — see ``_effective_be_window``.
autofit/engine.py:1104:    # Best converged refit found during the multi-start pass (by weighted χ²).
autofit/engine.py:1105:    # Port improvement over fitalg, which always reported the primary fit even
autofit/engine.py:1106:    # when a perturbed refit found a deeper minimum: the driver promotes this
autofit/engine.py:1110:    # How many multi-start fits (refits + primary) landed within
autofit/engine.py:1116:    # How many of the requested n_refits were actually attempted before the
autofit/engine.py:1118:    # n_refits unless timed_out is True — used as the honest denominator for
autofit/engine.py:1120:    # understating them against the full nominal n_refits.
autofit/engine.py:1136:    primary_fit: FitOutcome,
autofit/engine.py:1138:    n_refits: int = 20,
autofit/engine.py:1142:    fit_full_window: bool = False,
autofit/engine.py:1147:    primary fit + all its refits. Once passed, remaining refits are
autofit/engine.py:1158:    # Same widened bounds every refit was actually built with (constant
autofit/engine.py:1160:    # must agree with the bound the fit was allowed to search, or a
autofit/engine.py:1164:    bound_overrides = _full_window_bound_overrides(model, x) if fit_full_window else None
autofit/engine.py:1167:    # the primary fit's background rather than recomputing per refit.
autofit/engine.py:1168:    bg = primary_fit.background
autofit/engine.py:1172:    refit_chis: list[float] = [float(primary_fit.weighted_chi_sq)]
autofit/engine.py:1175:    for _ in range(n_refits):
autofit/engine.py:1180:                "after %d/%d refits — remaining refits skipped",
autofit/engine.py:1181:                model.name, CANDIDATE_TIMEOUT_SEC, n_attempted, n_refits,
autofit/engine.py:1187:                                      fit_full_window=fit_full_window)
autofit/engine.py:1189:            # bound-fixed refit stability: the constrained parameters stay
autofit/engine.py:1190:            # fixed at their bounds in every multi-start refit
autofit/engine.py:1194:        outcome = fit_candidate(x, y, weights, model, initial_params=init)
autofit/engine.py:1198:        refit_chis.append(float(outcome.weighted_chi_sq))
autofit/engine.py:1232:    best_chi = min(refit_chis)
autofit/engine.py:1233:    basin_support = sum(1 for c in refit_chis
autofit/engine.py:1254:    fitted_area: float
autofit/engine.py:1262:    if primary.lmfit_result is None:
autofit/engine.py:1265:    return sum(1 for pname, par in primary.lmfit_result.params.items()
autofit/engine.py:1313:    (region, phase) when any exist — in a joint co-fit, normalizing against
autofit/engine.py:1343:            role=slot.role, persistence=sstab.persistence, fitted_area=area,
autofit/engine.py:1372:    y_fit: np.ndarray,
autofit/engine.py:1377:    r = y - y_fit
autofit/engine.py:1420:    fitted_center: Optional[float] = None
autofit/engine.py:1421:    fitted_fwhm: Optional[float] = None
autofit/engine.py:1422:    fitted_amplitude: Optional[float] = None
autofit/engine.py:1432:    # the fit is held at the physical limit and the result is CONDITIONAL
autofit/engine.py:1459:    primary_fit: FitOutcome
autofit/engine.py:1467:    # Full lmfit param names fixed at their bounds by the decisive-override
autofit/engine.py:1468:    # bound-fixed refit (empty for ordinary reports).  Stability figures on
autofit/engine.py:1469:    # such a report are inherited from the free (pegged) fit — a documented
autofit/engine.py:1475:        dof = max(self.primary_fit.n_data - self.primary_fit.n_params, 1)
autofit/engine.py:1476:        return self.primary_fit.weighted_chi_sq / dof
autofit/engine.py:1481:        return max(self.primary_fit.n_params - removed, 1)
autofit/engine.py:1488:        n = self.primary_fit.n_data
autofit/engine.py:1489:        rss = self.primary_fit.residual_sum_sq
autofit/engine.py:1499:        return compute_bic(self.primary_fit)
autofit/engine.py:1508:        criterion CONSISTENT with the Poisson-weighted fits; the ranking
autofit/engine.py:1511:        n = self.primary_fit.n_data
autofit/engine.py:1512:        chi = self.primary_fit.weighted_chi_sq
autofit/engine.py:1515:        return chi + self.primary_fit.n_params * np.log(n)
autofit/engine.py:1524:        lm = self.primary_fit.lmfit_result
autofit/engine.py:1544:def compute_bic(fit: FitOutcome) -> float:
autofit/engine.py:1545:    """fitalg likelihood convention: BIC = n·ln(RSS/n) + k·ln(n)."""
autofit/engine.py:1546:    n, rss = fit.n_data, fit.residual_sum_sq
autofit/engine.py:1549:    return n * np.log(rss / n) + fit.n_params * np.log(n)
autofit/engine.py:1564:    #   'decisive_override'  — clean survivors exist but a bound-fixed refit
autofit/engine.py:1581:    # The weighted-χ² criterion (consistent with the fit weights) prefers a
autofit/engine.py:1584:    # selection must not silently rest on a likelihood the fits reject).
autofit/engine.py:1594:    # Pre-fit out-of-grammar dominant seeding (unit F1): the detected
autofit/engine.py:1604:    # Candidate-generation layer (autofit.candidates): the OVERCOMPLETE,
autofit/engine.py:1622:    Two-tier semantics (departure from fitalg, which returned zero survivors
autofit/engine.py:1627:    failures are never promoted — an unstable fit is pathology, not a
autofit/engine.py:1640:            # refits repeatedly producing unmatched components is a
autofit/engine.py:1665:        # forcing an answer on featureless data (a flat-noise grammar fit
autofit/engine.py:1667:        # Every candidate failed BOTH tiers — typically cross-refit
autofit/engine.py:1675:                  if r.primary_fit.converged
autofit/engine.py:1684:    # bound-fixed refit of a conditional candidate dominates) lives in
autofit/engine.py:1685:    # compare_models — it needs the spectrum to refit; rank_and_filter is
autofit/engine.py:1688:    # BIC* is the ranking default (spec §6); χ²ᵣ breaks ties only.  fitalg
autofit/engine.py:1701:                    f"Indistinguishable on fit quality and BIC* "
autofit/engine.py:1714:# Pre-fit out-of-grammar dominant seeding (unit F1 — see the constants block)
autofit/engine.py:1726:    # 'curvature_shoulder' (the CWT ridge channel of autofit.candidates)
autofit/engine.py:1927:    fitted_components: list["FittedComponent"],
autofit/engine.py:1933:    (i)  PROXIMITY to a fitted component — within
autofit/engine.py:1935:         fitted width`` (transferable units: half its width, whatever the
autofit/engine.py:1948:    Deliberately NEVER uses the fit_full_window bound override (Codex-
autofit/engine.py:1954:    territory, not the fit's search bound; the two are different
autofit/engine.py:1956:    populated_roles = {c.slot_role for c in fitted_components}
autofit/engine.py:1957:    for comp in fitted_components:
autofit/engine.py:1964:        lo, hi = _effective_be_window(slot, fitted_components)
autofit/engine.py:1973:    y_fit: np.ndarray,
autofit/engine.py:1976:    fitted_components: list["FittedComponent"],
autofit/engine.py:1980:    r = y - y_fit
autofit/engine.py:2039:        if _proposal_blocked(center, base_model, fitted_components):
autofit/engine.py:2061:    round, colliding the slot role and its lmfit param prefix (Codex
autofit/engine.py:2078:    # joint fits (Codex Stage-2 finding #2).  Region/phase assignment of a
autofit/engine.py:2098:    base_fit: FitOutcome,
autofit/engine.py:2102:    fit_full_window: bool = False,
autofit/engine.py:2105:                                        fit_full_window=fit_full_window)
autofit/engine.py:2106:    if base_fit.lmfit_result is not None:
autofit/engine.py:2107:        for pname, par in base_fit.lmfit_result.params.items():
autofit/engine.py:2131:    n_refits: int,
autofit/engine.py:2137:    fit_full_window: bool = False,
autofit/engine.py:2141:    base_fit = base_report.primary_fit
autofit/engine.py:2156:    # An augmented fit_candidate has no internal wall clock and runs
autofit/engine.py:2164:            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")
autofit/engine.py:2168:        init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
autofit/engine.py:2169:                                             fit_full_window=fit_full_window)
autofit/engine.py:2173:    primary = fit_candidate(x, y, weights, aug_model, initial_params=init)
autofit/engine.py:2175:        return _fast("augmented_fit_did_not_converge")
autofit/engine.py:2180:    pr.fitted_center = comp.position
autofit/engine.py:2181:    pr.fitted_fwhm = comp.fwhm
autofit/engine.py:2182:    pr.fitted_amplitude = comp.amplitude
autofit/engine.py:2219:    # budget_remaining was a snapshot BEFORE the augmented fit; that fit has
autofit/engine.py:2223:    # min(stale_budget, 35) s past the fit and overrun the sweep budget).
autofit/engine.py:2226:    # fit_candidate — so starting stability with only a few seconds left
autofit/engine.py:2227:    # would still overrun by ~one worst-case fit (Codex c1s-fix RE-CHECK,
autofit/engine.py:2233:            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s (one refit could overrun)")
autofit/engine.py:2238:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2241:        fit_full_window=fit_full_window,
autofit/engine.py:2248:            pr.fitted_center = comp.position
autofit/engine.py:2249:            pr.fitted_fwhm = comp.fwhm
autofit/engine.py:2250:            pr.fitted_amplitude = comp.amplitude
autofit/engine.py:2253:    # wall the initial fit did not touch (Codex fwhm-cap review, run B
autofit/engine.py:2274:    y_fit_aug = (primary.lmfit_result.best_fit + primary.background
autofit/engine.py:2275:                 if primary.lmfit_result is not None else np.zeros_like(y))
autofit/engine.py:2276:    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
autofit/engine.py:2284:        model=aug_model, primary_fit=primary, bic=compute_bic(primary),
autofit/engine.py:2317:                 "be": float(pr.fitted_center if pr.fitted_center is not None
autofit/engine.py:2344:# Bound the number of conditional candidates the override may refit — a
autofit/engine.py:2349:def _bound_fixed_refit(
autofit/engine.py:2356:    n_refits: int,
autofit/engine.py:2358:    fit_full_window: bool = False,
autofit/engine.py:2361:    Refit a boundary-limited candidate with each pegged parameter FIXED at
autofit/engine.py:2367:    - the refit must not itself peg any NEW bound — otherwise the
autofit/engine.py:2370:      parameters stay fixed in every multi-start refit) — no inherited
autofit/engine.py:2372:    - NO absent-slot adjustment is applied to the refit: its BIC* uses the
autofit/engine.py:2377:    lm = report.primary_fit.lmfit_result
autofit/engine.py:2398:    outcome = fit_candidate(x, y, weights, report.model, initial_params=params)
autofit/engine.py:2402:        # fixing one wall pushed the fit onto another — still not an
autofit/engine.py:2408:        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2411:        fit_full_window=fit_full_window,
autofit/engine.py:2413:    y_fit = (outcome.lmfit_result.best_fit + outcome.background
autofit/engine.py:2414:             if outcome.lmfit_result is not None else np.zeros_like(y))
autofit/engine.py:2417:        primary_fit=outcome,
autofit/engine.py:2421:            x, y, y_fit, noise_floor, diagnostic_windows),
autofit/engine.py:2448:    n_refits: int,
autofit/engine.py:2450:    fit_full_window: bool = False,
autofit/engine.py:2466:        refit = _bound_fixed_refit(x, y, weights, candidate,
autofit/engine.py:2468:                                   n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2469:                                   fit_full_window=fit_full_window)
autofit/engine.py:2470:        if refit is None:
autofit/engine.py:2473:        if refit.active_min_persistence < persistence_threshold:
autofit/engine.py:2476:        if not (refit.bic_adjusted + CONDITIONAL_OVERRIDE_DELTA_BIC
autofit/engine.py:2478:                and refit.reduced_chi_sq < clean_best.reduced_chi_sq):
autofit/engine.py:2480:        result.reports.append(refit)
autofit/engine.py:2481:        result.survivors = [refit] + result.survivors  # clean kept as alternatives
autofit/engine.py:2514:    n_refits: int = 20,
autofit/engine.py:2524:    fit_full_window: bool = False,
autofit/engine.py:2529:    ``fit_full_window`` (Find Peaks UI, 2026-07-13): OPTIONAL, default
autofit/engine.py:2535:    Threaded through every place a candidate's initial/refit parameters
autofit/engine.py:2536:    get built from scratch (screen fit, deep-phase primary fit, stability
autofit/engine.py:2537:    refits, the proposal pass, and the bound-fixed decisive-override
autofit/engine.py:2538:    refit) so the relaxed bound is consistent across a candidate's whole
autofit/engine.py:2543:    pre-fit out-of-grammar dominant seeding (unit F1) — detection-driven, so
autofit/engine.py:2550:    fit — the REAL screen->stabilize sweep progress (unit F3), not a fake
autofit/engine.py:2569:        # each candidate still fits with its own background.  Structural-
autofit/engine.py:2580:        # Candidate-generation layer (autofit.candidates): overcomplete,
autofit/engine.py:2631:            # family with the full seed set made all 29 screen fits blow
autofit/engine.py:2700:    screen_fit: dict[str, FitOutcome] = {}
autofit/engine.py:2716:            outcome = fit_candidate(x, y, weights, model,
autofit/engine.py:2718:                                    fit_full_window=fit_full_window)
autofit/engine.py:2734:        screen_fit = {m.name: o for m, o, _ in selected_models}
autofit/engine.py:2753:                "compare_models: sweep budget cannot fit another candidate "
autofit/engine.py:2760:        log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
autofit/engine.py:2763:        # Shared wall-clock budget for this candidate's primary fit + all its
autofit/engine.py:2764:        # stability refits (CANDIDATE_TIMEOUT_SEC) — see run_stability_analysis.
autofit/engine.py:2766:        # reuse the screen fit as this candidate's primary (no repeated work)
autofit/engine.py:2767:        primary = screen_fit.get(model.name) or fit_candidate(
autofit/engine.py:2768:            x, y, weights, model, fit_full_window=fit_full_window)
autofit/engine.py:2775:            noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2777:            fit_full_window=fit_full_window,
autofit/engine.py:2785:        y_fit = (primary.lmfit_result.best_fit +
autofit/engine.py:2787:                 if primary.lmfit_result is not None else np.zeros_like(y))
autofit/engine.py:2788:        residuals = compute_residual_diagnostics(x, y, y_fit, noise_floor, diagnostic_windows)
autofit/engine.py:2796:            model=model, primary_fit=primary, bic=compute_bic(primary),
autofit/engine.py:2824:            current_y_fit = y_fit
autofit/engine.py:2830:                    x, y, current_y_fit, noise_floor, current.model,
autofit/engine.py:2831:                    fitted_components=current.primary_fit.components,
autofit/engine.py:2852:                        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
autofit/engine.py:2857:                        fit_full_window=fit_full_window,
autofit/engine.py:2867:                        pf = current.primary_fit
autofit/engine.py:2868:                        current_y_fit = (
autofit/engine.py:2869:                            pf.lmfit_result.best_fit + pf.background
autofit/engine.py:2870:                            if pf.lmfit_result is not None else np.zeros_like(y))
autofit/engine.py:2902:        n_refits=n_refits,
autofit/engine.py:2904:        fit_full_window=fit_full_window,
autofit/engine.py:2926:            [{"center_be": (pr.fitted_center
autofit/engine.py:2927:                            if pr.fitted_center is not None
autofit/engine.py:2984:    """Result-level flag when the weighted-χ² BIC (consistent with the fit
autofit/engine.py:2994:        "note": "the weighted-χ² criterion (consistent with the fit "
fitting.py:2:fitting.py – XPS peak fitting engine using lmfit.
fitting.py:20:Spin‑orbit constraints are handled via lmfit parameter expressions.
fitting.py:30:from lmfit import Model, Parameters
fitting.py:508:def tougaard_background(
fitting.py:513:    """Single-pass Tougaard universal-cross-section background, with the
fitting.py:518:    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
fitting.py:519:    cross-section fitted to noble/transition-metal optical data; the
fitting.py:523:    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
fitting.py:537:    practical Tougaard criterion (B is effectively fitted, which is why the
fitting.py:539:    fitting B together with an offset rather than B alone.
fitting.py:556:    # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
fitting.py:674:            integer 0–499. Stored as float in lmfit, rounded to int here.
fitting.py:680:    # number, so the Jacobian column for m is well-defined under lmfit's
fitting.py:686:    # spec or caller bypasses the lmfit bound.
fitting.py:706:    # backwards compat with previously-saved (integer-m) fits. With 3.5
fitting.py:717:    # holds. lmfit's composite-fit residual path will broadcast the
fitting.py:735:# lmfit Model factory
fitting.py:755:    A→B→A — produces a self-referencing lmfit expression that recurses to
fitting.py:757:    (→ 400) before any lmfit parameter/expression is built. A ``constrain_to``
fitting.py:789:    Build lmfit Parameters for one peak from a spec dict.
fitting.py:931:# Main fitting API
fitting.py:934:def run_fit(
fitting.py:942:    fit_kws: dict | None = None,
fitting.py:948:    Run XPS peak fitting and return a serialisable result dict.
fitting.py:958:    charge_shift_ev   : shift to apply to energy axis before fitting
fitting.py:959:    fit_kws           : extra kwargs forwarded to lmfit minimize
fitting.py:963:    dict with keys: energy, fitted_y, background_y, residuals,
fitting.py:970:    # Reject self/cyclic spin-orbit constraints before building lmfit exprs (F11)
fitting.py:976:    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
fitting.py:979:    # anchors inside the ROI silently chopped the fit window — and the
fitting.py:993:    # unusable (< 2 points): the integral / interp / linear-fit
fitting.py:1004:    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
fitting.py:1011:    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
fitting.py:1038:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1075:    # ── Build composite lmfit model ───────────────────────────────────────────
fitting.py:1101:    if fit_kws:
fitting.py:1102:        kws.update(fit_kws)
fitting.py:1114:        result = composite_model.fit(y_sub, all_params, x=x, weights=weights, **kws)
fitting.py:1116:        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc
fitting.py:1129:    # ── Perturb and refit to escape local minima ─────────────────────────
fitting.py:1153:                trial = composite_model.fit(y_sub, perturbed_params, x=x, weights=weights, **kws)
fitting.py:1170:    fitted_sub = result.best_fit
fitting.py:1171:    fitted_y = fitted_sub + bg
fitting.py:1226:    residuals = (y_sub - fitted_sub).tolist()
fitting.py:1229:    r_factor = (float(np.sum(np.abs(y_sub - fitted_sub)) / np.sum(np.abs(y_sub)))
fitting.py:1237:        "fitted_y": fitted_y.tolist(),
fitting.py:1262:    """Return just the background array without fitting peaks."""
fitting.py:1276:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
templates/index.html:11:<!-- Batch-fit settings-propagation pure-logic module (shipped source of truth). -->
templates/index.html:114:  #fit-method {
templates/index.html:124:  #fit-method:focus { border-color: var(--accent); outline: none; }
templates/index.html:1088:  .stack-legend-row .fit-toggle { cursor: pointer; accent-color: var(--accent); }
templates/index.html:1089:  .stack-legend-row .fit-toggle:disabled { opacity: 0.3; cursor: not-allowed; }
templates/index.html:1148:  /* ── Hide peak/fit controls when a stack tab is active ──── */
templates/index.html:1149:  body.stack-tab-active .peak-fit-control { display: none !important; }
templates/index.html:1234:  .fit-spinner-overlay {
templates/index.html:1245:  .fit-spinner {
templates/index.html:1257:     modal-covering overlay like .fit-spinner-overlay: the results area
templates/index.html:1362:  .fit-spinner-label {
templates/index.html:1369:  .fit-spinner-label .ellipsis::after {
templates/index.html:1863:    <h1><span class="title-xps">XPS</span> Fitting Studio <span class="title-sub">// lmfit backend</span></h1>
templates/index.html:1865:      <span class="hbadge" id="fit-quality" style="cursor:help">&#967;&#178; &mdash;</span>
templates/index.html:1879:      <div class="hselect-wrap peak-fit-control">
templates/index.html:1880:        <label for="fit-method">Method</label>
templates/index.html:1881:        <select id="fit-method" class="xps-tip-select">
templates/index.html:1883:          <option value="leastsq" data-tip="Fast gradient-based optimizer. Best for refining fits that are already close to the solution. Most commonly used in XPS software.">Levenberg-Marquardt</option>
templates/index.html:1884:          <option value="nelder" data-tip="Derivative-free optimizer. Useful when the chi-squared surface is rough or noisy. Slower but can handle difficult fits.">Nelder-Mead</option>
templates/index.html:1889:      <button class="btn btn-green peak-fit-control" id="btn-run-fit" onclick="runFit()">Run Fit</button>
templates/index.html:1890:      <button class="btn peak-fit-control" id="btn-batch-fit" onclick="showPropagateModal()" title="Propagate fit model to other spectra">Batch Fit</button>
templates/index.html:1891:      <button class="btn" onclick="showHistoryModal()" title="View and restore fit history">History</button>
templates/index.html:1897:          <button class="save-dropdown-item" onclick="saveSpectrum()"><span class="dd-icon">&#128196;</span><div>Save Spectrum<small>Data + fit curves (~50-200 KB)</small></div></button>
templates/index.html:1900:          <button class="save-dropdown-item" onclick="exportFitTable('csv')"><span class="dd-icon">&#128202;</span><div>Export Table (CSV)<small>All fit parameters</small></div></button>
templates/index.html:1901:          <button class="save-dropdown-item" onclick="exportFitTable('xlsx')"><span class="dd-icon">&#128202;</span><div>Export Table (XLSX)<small>All fit parameters</small></div></button>
templates/index.html:1903:          <button class="save-dropdown-item" id="auto-fit-c1s-menu-item" onclick="runAutoFitC1sGraphite()" title="Available only on C1s spectra (ROI midpoint 270–315 eV)"><span class="dd-icon">&#128293;</span><div>Auto-Fit C1s Graphite<small>One-click fit + charge correction</small></div></button>
templates/index.html:1904:          <button class="save-dropdown-item" id="find-peaks-menu-item" onclick="openFindPeaksModal()" title="Suggests peaks for the region you pick and shows how confident it is. Suggestions only — nothing changes your fit unless you add them."><span class="dd-icon">&#129517;</span><div>Find Peaks (beta)<small>Suggested peaks + confidence, reviewed by you</small></div></button>
templates/index.html:1906:          <button class="save-dropdown-item" onclick="loadSession()"><span class="dd-icon">&#128194;</span><div>Load Fit or Project<small>Restore saved fit params</small></div></button>
templates/index.html:1935:          <p>.csv &middot; .txt &middot; .xlsx &middot; .vgd &middot; .fit.json &middot; .proj.json</p>
templates/index.html:1969:              <span id="cc-warn-asterisk" title="This charge correction was copied from another spectrum during fit propagation. Please verify the observed BE value for this spectrum.">*</span>
templates/index.html:1988:                <option value="tougaard" data-tip="Physics-based universal background using electron energy loss cross-sections. More accurate than Shirley but requires wider energy range.">Tougaard-like (single pass)</option>
templates/index.html:2029:          <div class="section-head" onclick="toggleSection(this)" title="The Region of Interest (ROI) defines the energy range used for all fitting operations. Only data points within this range are included when you click Run Fit — this affects peak fitting, background subtraction, and fit quality metrics (χ² and R-factor). The ROI is independent of the chart zoom — you can zoom in or out freely without affecting which data is fitted.">
templates/index.html:2088:        <button class="btn btn-sm peak-fit-control" id="btn-add-peak" onclick="togglePlaceMode('peak')">+ Add Peak</button>
templates/index.html:2089:        <button class="btn btn-sm peak-fit-control" id="btn-add-multiplet" onclick="_onMultipletBtnClick()">+ Multiplet Pair</button>
templates/index.html:2097:        <button class="btn btn-sm peak-fit-control" id="ref-identify-btn" onclick="togglePlaceMode('identify')" title="Identify mode: click a spectrum feature to list candidate elemental lines (works with the Reference palette closed). Esc or right-click to exit.">&#8982; Identify</button>
templates/index.html:2111:        <label class="pill-toggle active peak-fit-control">
templates/index.html:2131:        <div id="fit-spinner-overlay" class="fit-spinner-overlay" style="display:none">
templates/index.html:2132:          <div class="fit-spinner"></div>
templates/index.html:2133:          <div class="fit-spinner-label" id="fit-spinner-label">Fitting<span class="ellipsis"></span></div>
templates/index.html:2197:            <p style="color:var(--text3);font-size:11px;text-align:center;padding:20px 0;">Run the fit to see results.</p>
templates/index.html:2203:            <p style="color:var(--text3);font-size:11px;text-align:center;padding:20px 0;">Run fit to quantify.</p>
templates/index.html:2291:  fitResult: null,
templates/index.html:2371:      '<input type="checkbox" class="fit-toggle"'
templates/index.html:2373:        + ' title="' + (hasFit ? 'Show fit envelope' : 'No fit available') + '">' +
templates/index.html:2385:    const ft = row.querySelector('.fit-toggle');
templates/index.html:2457:  // showFit defaults true if source has a fit at add time (Phase 4 wires the toggle).
templates/index.html:2459:  const srcHasFit = !!(src && src.fitResult && Array.isArray(src.peaks) && src.peaks.length > 0);
templates/index.html:2602:// dependent controls, show a persistent banner, and log — while the fitting
templates/index.html:2616:      console.error('[xps] LEGACY_REFERENCE injection failed — reference features disabled; fitting unaffected.');
templates/index.html:2656:// shows a banner; the fitting app is untouched. (Codex CkptA #1 / CkptB P0.)
templates/index.html:2794:// M.C. Biesinger, xpsfitting.com "Relative Sensitivity Factors" (library + component convention).
templates/index.html:3014:      fitResult: null,
templates/index.html:3051:      peaks: [], nextId: 1, fitResult: null,
templates/index.html:3081:    state.fitResult = tab.fitResult;
templates/index.html:3091:    // Update chi-squared display for this tab's fit result
templates/index.html:3092:    const fqEl = document.getElementById('fit-quality');
templates/index.html:3094:    if (state.fitResult && state.fitResult.chiReduced != null) {
templates/index.html:3095:      fqEl.textContent = '\u03c7\u00b2\u1d63 = ' + state.fitResult.chiReduced.toFixed(2);
templates/index.html:3097:      if (chiEl) chiEl.textContent = state.fitResult.chiReduced.toFixed(3);
templates/index.html:3103:    if (state.fitResult && state.fitResult.rFactor == null) {
templates/index.html:3104:      state.fitResult.rFactor = _computeRFactor(state.fitResult);
templates/index.html:3106:    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
templates/index.html:3107:    _updateROIDisplay(state.fitResult ? state.fitResult.roiRange : null);
templates/index.html:3148:      state.peaks = []; state.fitResult = null;
templates/index.html:3263:      state.fitResult = null;
templates/index.html:3266:      active.fitResult = null;
templates/index.html:3641:    t.fitResult = state.fitResult;
templates/index.html:3700:      // Endpoint averaging also applies to Tougaard (it sets the high-BE
templates/index.html:3901:// Mirrors fitting.py:_la_casaxps_true. BE axis: high-BE side (eps ≥ 0)
templates/index.html:4130:// Single-pass Tougaard background — JS twin of fitting.py's
templates/index.html:4131:// tougaard_background (keep the two numerically in agreement; pinned by
templates/index.html:4133:// K(T) = B·T/(C+T²)² with B = 2866 eV², C = 1643 eV² (S. Tougaard,
templates/index.html:4147:  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
templates/index.html:4177:  // the practical Tougaard criterion (B effectively fitted; C alone sets the
templates/index.html:4270:  if (state.fitResult) state.fitResult.bgIntensity = null;
templates/index.html:4273:// Clear stored fit envelope so the fallback (modelFull + bg) is used after a manual peak edit
templates/index.html:4275:  if (state.fitResult) state.fitResult.fittedY = null;
templates/index.html:4320:    // Endpoint averaging matters for Tougaard since the amplitude is
templates/index.html:4322:    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
templates/index.html:4341:  // Averaged for the same reason as Shirley types: the Tougaard amplitude
templates/index.html:4343:  // directly. Mirrors fitting.py's run_fit / compute_background_only.
templates/index.html:4795:// (that silently corrupted fitted values, e.g. DS+G's laM/laBeta on a
templates/index.html:4821:// readonly and excluded from fitting — see renderShapeControls / runFit).
templates/index.html:4843://      delete-then-default behaviour that silently reset fitted values
templates/index.html:4903:    // stack. Clear explicit Y and X bounds, let Chart.js auto-fit, and
templates/index.html:4928:    // Reset Y — remove explicit min/max so Chart.js auto-fits to data
templates/index.html:5441:  state.fitResult = null;
templates/index.html:5520:  btn.title = (p[key] ? 'Unlock' : 'Lock') + ' during fitting';
templates/index.html:5560:    btn.title = 'Unlock all fit parameters on all peaks';
templates/index.html:5563:    btn.title = 'Lock all fit parameters on all peaks';
templates/index.html:5668:             title="Mark this peak as the charge-correction reference (typically C 1s graphite at 284.5 eV). Only one peak per fit can hold this marker.">
templates/index.html:5691:          ${!isLinked ? '<button class="lock-btn' + (p.fixCenter ? ' locked' : '') + '" onclick="event.stopPropagation();toggleLock(' + p.id + ',\'fixCenter\',this)" title="' + (p.fixCenter ? 'Unlock' : 'Lock') + ' during fitting">' + (p.fixCenter ? '&#x1f512;' : '&#x1f513;') + '</button>' : ''}
templates/index.html:5699:          ${!isLinked && p.shape !== 'DSG_LA' ? '<button class="lock-btn' + (p.fixFwhm ? ' locked' : '') + '" onclick="event.stopPropagation();toggleLock(' + p.id + ',\'fixFwhm\',this)" title="' + (p.fixFwhm ? 'Unlock' : 'Lock') + ' during fitting">' + (p.fixFwhm ? '&#x1f512;' : '&#x1f513;') + '</button>' : ''}
templates/index.html:5707:        ${!isLinked ? '<button class="lock-btn' + (p.fixAmplitude ? ' locked' : '') + '" onclick="event.stopPropagation();toggleLock(' + p.id + ',\'fixAmplitude\',this)" title="' + (p.fixAmplitude ? 'Unlock' : 'Lock') + ' during fitting">' + (p.fixAmplitude ? '&#x1f512;' : '&#x1f513;') + '</button>' : ''}
templates/index.html:5741:          ${!isLinked ? `<button class="lock-btn${p.fixAsymmetry ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixAsymmetry',this)" title="${p.fixAsymmetry ? 'Unlock' : 'Lock'} during fitting">${p.fixAsymmetry ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5752:          ${!isLinked ? `<button class="lock-btn${p.fixGlMix ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixGlMix',this)" title="${p.fixGlMix ? 'Unlock' : 'Lock'} during fitting">${p.fixGlMix ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5764:          ${!isLinked ? `<button class="lock-btn${p.fixGlMix ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixGlMix',this)" title="${p.fixGlMix ? 'Unlock' : 'Lock'} during fitting">${p.fixGlMix ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5772:          ${!isLinked ? `<button class="lock-btn${p.fixDsAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixDsAlpha',this)" title="${p.fixDsAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixDsAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5779:          ${!isLinked ? `<button class="lock-btn${p.fixDsGamma ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixDsGamma',this)" title="${p.fixDsGamma ? 'Unlock' : 'Lock'} during fitting">${p.fixDsGamma ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5793:            ${!isLinked ? `<button class="lock-btn${p.fixLaAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixLaAlpha',this)" title="${p.fixLaAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixLaAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5800:            ${!isLinked ? `<button class="lock-btn${p.fixLaBeta ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixLaBeta',this)" title="${p.fixLaBeta ? 'Unlock' : 'Lock'} during fitting">${p.fixLaBeta ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5808:          ${!isLinked ? `<button class="lock-btn${p.fixLaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixLaM',this)" title="${p.fixLaM ? 'Unlock' : 'Lock'} during fitting">${p.fixLaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5822:            ${!isLinked ? `<button class="lock-btn${p.fixCaAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaAlpha',this)" title="${p.fixCaAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixCaAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5829:            ${!isLinked ? `<button class="lock-btn${p.fixCaBeta ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaBeta',this)" title="${p.fixCaBeta ? 'Unlock' : 'Lock'} during fitting">${p.fixCaBeta ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5837:          ${!isLinked ? `<button class="lock-btn${p.fixCaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaM',this)" title="${p.fixCaM ? 'Unlock' : 'Lock'} during fitting">${p.fixCaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
templates/index.html:5909:  // All initial values go at top level — fitting.py reads spec.get("center") etc.
templates/index.html:5938:    // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
templates/index.html:5939:    // For non-auto-fit peaks these fields are absent and the backend falls back
templates/index.html:6012:// bg-type is "none", or a fit is running. The pill's checked state
templates/index.html:6042:  const fitting = _bgSubFitInFlight;
templates/index.html:6056:    const disabled = !anyBg || fitting;
templates/index.html:6059:    if (fitting) {
templates/index.html:6060:      pill.title = 'Background subtraction toggle is locked while a fit is running.';
templates/index.html:6073:  const disabled = noBg || noSpectrum || fitting;
templates/index.html:6076:  if (fitting) {
templates/index.html:6077:    pill.title = 'Background subtraction toggle is locked while a fit is running.';
templates/index.html:6128:  const overlay = document.getElementById('fit-spinner-overlay');
templates/index.html:6129:  const label = document.getElementById('fit-spinner-label');
templates/index.html:6141:  const overlay = document.getElementById('fit-spinner-overlay');
templates/index.html:6152:  const item = document.getElementById('auto-fit-c1s-menu-item');
templates/index.html:6161:    item.title = 'Auto-Fit C1s Graphite — one-click fit + charge correction';
templates/index.html:6179:    const span = document.getElementById('auto-fit-c1s-confirm-count');
templates/index.html:6181:    const proceed = document.getElementById('auto-fit-c1s-confirm-proceed');
templates/index.html:6183:      document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
templates/index.html:6187:    document.getElementById('auto-fit-c1s-confirm-overlay').classList.add('open');
templates/index.html:6191:  document.getElementById('auto-fit-c1s-confirm-overlay').classList.remove('open');
templates/index.html:6230:// Decide how many low-BE peaks (0, 1, or 2) the auto-fit model should include.
templates/index.html:6295:// Build the auto-fit peak list in the corrected-BE frame.
templates/index.html:6306:  // matches what users employ successfully in manual fits.
templates/index.html:6388:  // not relative to graphite's fitted center — if graphite drifts to its
templates/index.html:6391:  // need an lmfit derived-parameter mechanism not present in the backend.
templates/index.html:6414:    fitResult:    state.fitResult ? { ...state.fitResult } : null,
templates/index.html:6430:  state.fitResult = snap.fitResult;
templates/index.html:6450:// Apply a successful auto-fit result. Mutates state and DOM so the tab
templates/index.html:6458:// /tmp/test_autofit_decide_warning.py can validate it without simulating
templates/index.html:6478:    'for a graphite-dominated sample. Review the fit and consider manual ' +
templates/index.html:6488:  const be = state.fitResult && state.fitResult.be;
templates/index.html:6498:    notify('Auto-fit failed: graphite center not found in fit result.', 'red', true);
templates/index.html:6506:  // 3. Compute fitted raw center using APP CONVENTION:
templates/index.html:6511:  // Self-consistency: cc-obs = graphite_fitted_raw (NOT graphite_raw_BE),
templates/index.html:6523:  // 5. Build state.fitResult exactly as runFit() does.
templates/index.html:6531:  state.fitResult = {
templates/index.html:6536:    fittedY: json.fitted_y,
templates/index.html:6539:  state.fitResult.rFactor = _computeRFactor(state.fitResult);
templates/index.html:6542:  const fq = document.getElementById('fit-quality');
templates/index.html:6550:  if (sbMsg) sbMsg.textContent = 'Auto-fit complete';
templates/index.html:6551:  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult.rFactor);
templates/index.html:6553:  // Lock all peak centers after a successful auto-fit. Users frequently
templates/index.html:6555:  // converged auto-fit positions can drift. The user can manually unlock
templates/index.html:6568:  // 8. Sanity check: warn if graphite area fraction is below 40%. The fit
templates/index.html:6569:  // is kept regardless — this is a triage signal, not a fit-quality gate.
templates/index.html:6603:    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
templates/index.html:6626:  state.fitResult = null;
templates/index.html:6642:  // Step 5: run /api/fit with AbortController + spinner.
templates/index.html:6644:  const spinLabel = document.getElementById('fit-spinner-label');
templates/index.html:6645:  if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
templates/index.html:6649:  const fittingTabId = tabManager.activeId;
templates/index.html:6662:    const fitMethod = document.getElementById('fit-method').value;
templates/index.html:6681:    const resp = await fetch('/api/fit', {
templates/index.html:6688:        fit_method: fitMethod,
templates/index.html:6696:    if (!json.success) throw new Error('fit did not converge');
templates/index.html:6697:    if (tabManager.activeId !== fittingTabId) {
templates/index.html:6699:      notify('Auto-fit discarded — tab switched during fit.', 'amber');
templates/index.html:6714:    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
templates/index.html:6721:      msg = 'Auto-fit exceeded the 2-minute timeout.';
templates/index.html:6724:      console.warn('Auto-fit error:', e);
templates/index.html:6726:      msg = 'Auto-fit failed.';
templates/index.html:6759:  // Capture the tab that owns this fit so that if the user switches tabs
templates/index.html:6762:  const fittingTabId = tabManager.activeId;
templates/index.html:6781:    const fitMethod = document.getElementById('fit-method').value;
templates/index.html:6789:    const fitReq = {
templates/index.html:6793:      fit_method: fitMethod,
templates/index.html:6796:    const resp = await fetch('/api/fit', {
templates/index.html:6799:      body: JSON.stringify(fitReq)
templates/index.html:6805:    // If the user switched tabs while the fit was running, discard the result
templates/index.html:6807:    if (tabManager.activeId !== fittingTabId) {
templates/index.html:6810:      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
templates/index.html:6814:    // Capture pre-fit values for uncertainty validation
templates/index.html:6824:    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
templates/index.html:6826:                        fittedY: backendResult.fitted_y, roiRange, _preFit };
templates/index.html:6827:    state.fitResult.rFactor = _computeRFactor(state.fitResult);
templates/index.html:6828:    document.getElementById('fit-quality').textContent = '\u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(2);
templates/index.html:6829:    document.getElementById('fit-quality').setAttribute('data-xps-tip', _CHISQ_TOOLTIP);
templates/index.html:6831:    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
templates/index.html:6832:    _updateRFactorUI(state.fitResult.rFactor);
templates/index.html:6839:    if (tabManager.activeId !== fittingTabId) {
templates/index.html:6841:      notify('Fit cancelled — tab switched during fit.', 'amber');
templates/index.html:6845:    if (e && e.message) console.warn('Backend fit failed, falling back to local LM:', e.message);
templates/index.html:6847:    if (!_snapshotSuppressed) document.getElementById('localfit-warn-overlay').classList.add('open');
templates/index.html:6984:  // KNOWN LIMITATION: this fallback fitter does not produce parameter
templates/index.html:6985:  // uncertainties. The backend lmfit path returns stderr per-param via the
templates/index.html:6987:  // results panel shows blank σ for every shape after a fallback fit. To
templates/index.html:6992:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange };
templates/index.html:6993:  state.fitResult.rFactor = _computeRFactor(state.fitResult);
templates/index.html:6995:  document.getElementById('fit-quality').textContent = '\u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(2);
templates/index.html:6996:  document.getElementById('fit-quality').setAttribute('data-xps-tip', _CHISQ_TOOLTIP);
templates/index.html:6999:  _updateRFactorUI(state.fitResult.rFactor);
templates/index.html:7039:// Build {peakId: paramMap} from backend fit result (null-safe)
templates/index.html:7040:function _buildStderrMap(fitResult) {
templates/index.html:7042:  const peaks = fitResult?.backendResult?.individual_peaks;
templates/index.html:7055:  if (!state.fitResult) {
templates/index.html:7056:    el.innerHTML = '<p style="color:var(--text3);font-size:11px;text-align:center;padding:20px 0">Run the fit to see results.</p>';
templates/index.html:7059:    // a PRIOR fit's area/RSF/At% table after state.fitResult was cleared
templates/index.html:7062:    // no-fit placeholder as its initial static markup.
templates/index.html:7064:    if (qEl) qEl.innerHTML = '<p style="color:var(--text3);font-size:11px;text-align:center;padding:20px 0;">Run fit to quantify.</p>';
templates/index.html:7068:  const { chiReduced, rmse, backendResult } = state.fitResult;
templates/index.html:7069:  const stderrMap = _buildStderrMap(state.fitResult);
templates/index.html:7088:        <div style="font-family:var(--mono);font-size:11px;color:var(--green)">lmfit</div>
templates/index.html:7091:    ${_renderRFactorPanel(state.fitResult.rFactor)}
templates/index.html:7099:  // Fit grid for area integration. Current-format fits carry fitResult.be; older
templates/index.html:7103:  let be = state.fitResult.be;
templates/index.html:7128:  // Uncertainty warnings (backend fit only). Genuine alarms go in the amber
templates/index.html:7130:  // stop reading as scary regressions after auto-fit locks centers.
templates/index.html:7330:// identified by `${entry.id}:raw` and `${entry.id}:fit` (stored as
templates/index.html:7348:// Has-fit detection — source tab must have a non-null fitResult AND
templates/index.html:7350:// called and whether the legend's fit-toggle is enabled.
templates/index.html:7353:  return !!(src && src.fitResult && Array.isArray(src.peaks) && src.peaks.length > 0);
templates/index.html:7364:// "Stack view of post-load fits: support manual-anchor background
templates/index.html:7381:// Build all render data for one entry's fit visualization:
templates/index.html:7382://   { be, bg, fittedY, peaks: [{peak, y}] }
templates/index.html:7384:// `fittedY` is the raw-level envelope; each peak's `y` is the raw-level
templates/index.html:7388://   A:  fitResult.be + fitResult.fittedY both present, lengths match
templates/index.html:7389://       → use fittedY directly (already raw-level). Frozen to fit-time
templates/index.html:7391://   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
templates/index.html:7392://       LM fit) → fittedY = evalAllPeaks(be, peaks) + bg.
templates/index.html:7398:// Returns empty arrays if source isn't available or has no fit.
templates/index.html:7399:// Align src.rawIntensity to a fit-time `be` array (Path A/A2). fr.be is
templates/index.html:7400:// a contiguous slice of corrBE at fit time; if ccShift hasn't drifted,
templates/index.html:7423:    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
templates/index.html:7426:  const fr = src.fitResult;
templates/index.html:7428:    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
templates/index.html:7437:    // Path A/A2: fit-time be + bg both present (frozen).
templates/index.html:7462:  let fittedY;
templates/index.html:7463:  if (Array.isArray(fr.fittedY) && fr.fittedY.length === be.length) {
templates/index.html:7464:    // Path A: backend fittedY directly (already raw-level).
templates/index.html:7465:    fittedY = fr.fittedY.slice();
templates/index.html:7469:    fittedY = model.map((v, i) => v + bg[i]);
templates/index.html:7480:  return { be, bg, rawY, fittedY, peaks: peakCurves };
templates/index.html:7487:// (peak edits, ccShift edits, re-fits all happen while user is on the
templates/index.html:7493:// fires on every offset/line-width slider tick (60 Hz) for every fit
templates/index.html:7532:// pbg + peak datasets only exist when source has a fit (_entryHasFit).
templates/index.html:7551:    // fit visualization; toolbar pills gate which layers show.
templates/index.html:7557:    // has bg available (i.e., has a fit). Unfit entries' raw stays full.
templates/index.html:7628:    // Envelope dataset (always present; hidden when no fit or
templates/index.html:7633:        ? rd.be.map((b, i) => ({ x: b, y: (rd.fittedY[i] - rd.bg[i]) + yShift }))
templates/index.html:7634:        : rd.be.map((b, i) => ({ x: b, y: rd.fittedY[i]              + yShift }));
templates/index.html:7638:      label: (src ? src.name : 'entry') + ' (fit)',
templates/index.html:7656:  // source-tab changes (peaks/fits/ccShift edited while user was on the
templates/index.html:7805:            ? rd.be.map((b, i) => ({ x: b, y: (rd.fittedY[i] - rd.bg[i]) + yShift }))
templates/index.html:7806:            : rd.be.map((b, i) => ({ x: b, y: rd.fittedY[i]              + yShift })))
templates/index.html:7877:  // Stack-tab early branch: render multi-spectrum overlay, no peaks/fits.
templates/index.html:7899:  // ROI-filtered data (for fitting, background, peaks)
templates/index.html:7913:  // After a fit, freeze all curve data to the stored fit state so that
templates/index.html:7914:  // changing ROI never re-draws or recomputes the fit, background, or peaks.
templates/index.html:7915:  const haveFit = !!(state.fitResult && Array.isArray(state.fitResult.be) &&
templates/index.html:7916:                     state.fitResult.be.length > 0 &&
templates/index.html:7917:                     Array.isArray(state.fitResult.bgIntensity) &&
templates/index.html:7918:                     state.fitResult.bgIntensity.length === state.fitResult.be.length);
templates/index.html:7920:  // plotBE/plotBG/plotInten drive all fit-related curves (peaks, background, envelope).
templates/index.html:7921:  // When a fit exists, they come from the frozen fit state — ROI changes don't affect them.
templates/index.html:7922:  // Before fitting, they come from the current ROI so live peak previews still work.
templates/index.html:7923:  const plotBE = haveFit ? state.fitResult.be : be;
templates/index.html:7924:  const plotBG = haveFit ? state.fitResult.bgIntensity
templates/index.html:7926:  const plotInten = haveFit && Array.isArray(state.fitResult.bgSubtracted)
templates/index.html:7927:                    ? state.fitResult.bgSubtracted.map((v, i) => v + plotBG[i])
templates/index.html:7929:  const bgSubtracted = haveFit && Array.isArray(state.fitResult.bgSubtracted)
templates/index.html:7930:                       ? state.fitResult.bgSubtracted
templates/index.html:7934:  // Use backend fitted_y when available (authoritative lmfit result);
templates/index.html:7935:  // fall back to JS-recomputed modelFull + bg for pre-fit / local-LM fits.
templates/index.html:7936:  const fittedYBacked = haveFit && state.fitResult.fittedY &&
templates/index.html:7937:                        state.fitResult.fittedY.length === plotBE.length
templates/index.html:7938:                        ? state.fitResult.fittedY : null;
templates/index.html:7939:  const rawResiduals = fittedYBacked
templates/index.html:7940:    ? plotInten.map((v, i) => v - fittedYBacked[i])
templates/index.html:7942:  // Percentage residuals: ((data - fit) / data) × 100, clamped to ±100%
templates/index.html:7944:    const d = fittedYBacked ? plotInten[i] : bgSubtracted[i];
templates/index.html:7957:  // Individual peaks drawn first (bottom layer) — frozen to fit range after fit
templates/index.html:7993:  // Background — frozen to fit range after fit. Hidden in subtracted view.
templates/index.html:8023:  // Fit envelope — frozen to fit range after fit; use backend fitted_y when available
templates/index.html:8025:  if (showEnvelope && plotBE.length && (fittedYBacked || state.peaks.length)) {
templates/index.html:8028:      data: fittedYBacked
templates/index.html:8029:        ? plotBE.map((b, i) => ({ x: b, y: fittedYBacked[i] - (bgSubView ? plotBG[i] : 0) }))
templates/index.html:8101:  // Residuals go to separate panel — use frozen fit range so ROI changes don't affect them
templates/index.html:8408:        <div class="onboard-label">Run fit</div>
templates/index.html:8554:let _saveMode = null; // 'fit', 'spectrum', 'project'
templates/index.html:8574:  if (_saveMode === 'fit') _doSaveFit();
templates/index.html:8584:  _openSaveDialog('fit', tab?.name || 'spectrum', '.fit.json', 'Save Fit');
templates/index.html:8631:    fname + '.fit.json'
templates/index.html:8647:  const fittedY = state.fitResult?.fittedY || modelFull.map((v, i) => v + bgIntensity[i]);
templates/index.html:8660:  const stats = state.fitResult ? {
templates/index.html:8661:    chi: state.fitResult.chi,
templates/index.html:8662:    chiReduced: state.fitResult.chiReduced,
templates/index.html:8663:    rmse: state.fitResult.rmse,
templates/index.html:8678:    fittedY: fittedY,
templates/index.html:8691:  notify('Spectrum + fit saved.', 'green');
templates/index.html:8706:  // Size control for the frozen fit grid: BE to 4 decimals, intensities to
templates/index.html:8734:      fitResult: t.fitResult ? {
templates/index.html:8735:        chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
templates/index.html:8736:        rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
templates/index.html:8737:        // Frozen fit grid: persisted so post-load updatePlot() renders the
templates/index.html:8738:        // recorded fit (haveFit path) instead of recomputing background and
templates/index.html:8741:        be: _roundBE(t.fitResult.be),
templates/index.html:8742:        bgIntensity: _roundIntensity(t.fitResult.bgIntensity),
templates/index.html:8743:        bgSubtracted: _roundIntensity(t.fitResult.bgSubtracted),
templates/index.html:8744:        roiRange: t.fitResult.roiRange || null,
templates/index.html:8757:    // Autofit engine candidate-set annotations (spec v2.1 §1): whitelisted on
templates/index.html:8812:// Migrate lineshape enum values in saved fits to the current naming.
templates/index.html:8817://                       but its fit was already DS-only (the request
templates/index.html:8819://                       restores the curve that was actually being fit.
templates/index.html:8842:    console.info('[migration] Migrated ' + counts['DSG->DS'] + " peaks from 'DSG' → 'DS' (DSG's Gaussian-broadening preview was cosmetic only and did not affect fits; loading as DS shows the curve that was actually being fit).");
templates/index.html:8848:  if (!state.rawBE.length) { notify('Load a spectrum first before loading a fit.', 'amber', true); return; }
templates/index.html:8880:    if (name.endsWith('.fit.json'))  { _applyFitJSON(data); return; }
templates/index.html:8938:    if (data.fittedY) fr.fittedY = data.fittedY;
templates/index.html:8939:    active.fitResult = fr;
templates/index.html:8940:    state.fitResult = fr;
templates/index.html:9066:        peaks: [], nextId: 1, fitResult: null,
templates/index.html:9083:      fitResult: t.fitResult || null,
templates/index.html:9084:      // Autofit candidate-set annotations — restored verbatim when present
templates/index.html:9277:  a.href = url; a.download = 'xps_fit_result.tsv';
templates/index.html:9292:  document.getElementById('expfig-residuals').checked = !!state.fitResult;
templates/index.html:9307:  const fittedY = (state.fitResult?.fittedY?.length === be.length) ? state.fitResult.fittedY : null;
templates/index.html:9308:  const residArr = fittedY ? inten.map((v, i) => v - fittedY[i]) : null;
templates/index.html:9335:  for (const arr of [inten, bgArr, fittedY]) {
templates/index.html:9421:  if (fittedY) {
templates/index.html:9423:    polyline(be, fittedY, yM);
templates/index.html:9507:  if (state.fitResult) {
templates/index.html:9510:    ctx.fillText('\u03c7\u00b2_r\u2009=\u2009' + state.fitResult.chiReduced.toFixed(3),
templates/index.html:9533:  if (fittedY) lgItems.push({ label: 'Fit',        type: 'line', color: '#cc0000' });
templates/index.html:9662:  if (!state.fitResult) { notify('Run a fit first.', 'red'); return; }
templates/index.html:9663:  const { be } = state.fitResult;
templates/index.html:9664:  const stderrMap = _buildStderrMap(state.fitResult);
templates/index.html:9677:  const chiStr = state.fitResult.chiReduced.toFixed(4);
templates/index.html:9708:    XLSX.writeFile(wb, 'fit_results.xlsx');
templates/index.html:9716:    _downloadBlob(new Blob([csv], { type: 'text/csv' }), 'fit_results.csv');
templates/index.html:9772:function _computeRFactor(fitResult) {
templates/index.html:9773:  if (!fitResult || !fitResult.be) return null;
templates/index.html:9774:  const be = fitResult.be;
templates/index.html:9775:  const bgSub = fitResult.bgSubtracted;
templates/index.html:9778:  if (fitResult.fittedY && fitResult.fittedY.length === be.length) {
templates/index.html:9779:    const bgI = fitResult.bgIntensity;
templates/index.html:9781:      residuals = bgSub.map((v, i) => (v + bgI[i]) - fitResult.fittedY[i]);
templates/index.html:9783:      residuals = bgSub.map((v, i) => v - (fitResult.fittedY[i] - (bgI ? bgI[i] : 0)));
templates/index.html:9800:const _RFACTOR_TOOLTIP = "The R-factor (reliability factor) measures the overall agreement between the fit and the data as a percentage. Computed within the ROI range.\n\nR = \u03a3|residual| / \u03a3|data| \u00d7 100%\n\n\u2022 R < 5% = excellent fit\n\u2022 R = 5\u201310% = acceptable fit, check residuals visually\n\u2022 R > 10% = poor fit, the model is likely incomplete\n\nUnlike chi-squared, the R-factor is intuitive \u2014 it represents the fraction of the total signal that is unexplained by the model.";
templates/index.html:9806:  const label = rf.level === 'good' ? 'Excellent fit' : rf.level === 'amber' ? 'Acceptable \u2014 check residuals' : 'Poor fit \u2014 model likely incomplete';
templates/index.html:9833:const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the goodness of fit weighted by data uncertainty. Computed within the ROI range.\n\n\u2022 \u03c7\u00b2 \u2248 1.0 = ideal fit (residuals match expected noise)\n\u2022 \u03c7\u00b2 >> 1 = poor fit or underestimated uncertainties\n\u2022 \u03c7\u00b2 << 1 = possible overfitting or overestimated uncertainties\n\nNote: a low \u03c7\u00b2 does not guarantee a correct model \u2014 always check the R-factor and visually inspect residuals.";
templates/index.html:9878:  if (!state.fitResult?.backendResult?.individual_peaks) return { warnings: [], info: [] };
templates/index.html:9881:  const stderrMap = _buildStderrMap(state.fitResult);
templates/index.html:9882:  const preFit = state.fitResult._preFit || {};
templates/index.html:9883:  // Map backend param names to pre-fit property names
templates/index.html:9896:      //   - linked satellite (expr set): tied to master via lmfit expr; intentional
templates/index.html:9898:      //   - genuinely locked (vary=false, no expr): user or auto-fit set this lock
templates/index.html:9924:      // Rule 2: param was free (vary=true, no expr) but lmfit returned no
templates/index.html:9935:            warnings.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> uncertainty could not be estimated (covariance matrix singular near this parameter). The fitted value may be unreliable.</li>`);
templates/index.html:10135:    e.returnValue = 'All loaded data and fit results will be lost if you leave this page.';
templates/index.html:10319:  // Loud missing-load guard (mirrors the RefCore guard): batch fit depends on the
templates/index.html:10324:    notify('Batch-fit module failed to load (static/js/batch_propagation.js). Reload the page and try again.', 'red', true);
templates/index.html:10391:    // Run local fit
templates/index.html:10400:    const chi = state.fitResult ? state.fitResult.chiReduced : null;
templates/index.html:12134:// Preview state: { peaks, fitResult } or null — drawn in orange overlay
templates/index.html:12139:  if (!tabManager.activeId || !state.peaks.length || !state.fitResult) return;
templates/index.html:12144:  if (!tab._fitCount) tab._fitCount = 0;
templates/index.html:12145:  tab._fitCount++;
templates/index.html:12147:  const chi = state.fitResult.chiReduced;
templates/index.html:12149:  const label = `Fit #${tab._fitCount} (${n} peak${n !== 1 ? 's' : ''})`;
templates/index.html:12156:    fitResult: {
templates/index.html:12157:      ...state.fitResult,
templates/index.html:12158:      be: [...(state.fitResult.be || [])],
templates/index.html:12159:      bgSubtracted: [...(state.fitResult.bgSubtracted || [])],
templates/index.html:12160:      bgIntensity: state.fitResult.bgIntensity ? [...state.fitResult.bgIntensity] : null,
templates/index.html:12161:      fittedY: state.fitResult.fittedY ? [...state.fitResult.fittedY] : null,
templates/index.html:12164:    rFactor: state.fitResult.rFactor ?? null,
templates/index.html:12196:    list.innerHTML = '<div style="font-size:11px;color:var(--text3);padding:12px 8px;font-family:var(--mono)">Load a spectrum and run a fit to start recording history.</div>';
templates/index.html:12202:    list.innerHTML = '<div style="font-size:11px;color:var(--text3);padding:12px 8px;font-family:var(--mono)">No snapshots yet. Snapshots are saved automatically after each fit.</div>';
templates/index.html:12236:// User-controlled strings from loaded project/spectrum/fit files reach
templates/index.html:12282:  _historyPreview = { snapId, peaks: snap.peaks, fitResult: snap.fitResult };
templates/index.html:12303:  state.fitResult = snap.fitResult ? { ...snap.fitResult } : null;
templates/index.html:12386:  // Grey out endpoint avg for types it can't affect. Tougaard keeps it:
templates/index.html:12757:      <span class="save-fname-ext" id="save-fname-ext">.fit.json</span>
templates/index.html:12794:<div id="localfit-warn-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
templates/index.html:12796:    <h3 style="color:var(--amber,#f59e0b)">&#9888; Warning: Local Fit Performed <button class="btn btn-sm" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">&#x2715;</button></h3>
templates/index.html:12797:    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) did not respond. A simplified local fit was used instead. Results may be less accurate.</p>
templates/index.html:12800:    &bull; The fit request may have timed out<br>
templates/index.html:12804:      <button class="btn btn-accent" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">Dismiss</button>
templates/index.html:12810:<div id="auto-fit-c1s-confirm-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
templates/index.html:12816:      This tab has <span id="auto-fit-c1s-confirm-count">0</span> peak(s) and a fit result.
templates/index.html:12817:      Auto-Fit will clear them and run a fresh fit. Continue?
templates/index.html:12821:      <button class="btn btn-accent" id="auto-fit-c1s-confirm-proceed">Proceed</button>
templates/index.html:12833:    <p style="font-size:10px;color:var(--text3);margin:0 0 8px;line-height:1.5">Auto-saved after each fit (max 10). Preview overlays in orange.</p>
templates/index.html:12858:     STRICTLY ADDITIVE: the manual fit path (/api/fit, Run Fit, peak
templates/index.html:12875:      <label style="font-size:11px;grid-column:1 / -1" id="fp-regions-label">Region(s) <small style="color:var(--text3)">(click an element for its levels; ctrl/&#8984;-click a level to fit two together)</small>
templates/index.html:12916:                title="Replaces this tab's current peaks with the suggested ones. You can undo this.">Add peaks to my fit</button>
templates/index.html:12951:// see autofit/coverage_index.py's module docstring for why the same word
templates/index.html:12956:                    label: 'Cited fit recipe' },
templates/index.html:13017:         'review — not final answers</b>. Nothing changes your manual fit ' +
templates/index.html:13027:            '“Compare peak models” fits most regions; the others trade ' +
templates/index.html:13028:            'speed for confidence ranges, a quick estimate, or refitting ' +
templates/index.html:13033:    chi2r: 'Goodness of fit: about 1 means the model matches the data ' +
templates/index.html:13037:    sigmaCenter: 'Statistical uncertainty in the fitted peak position (eV).',
templates/index.html:13055:      hint: 'Does the same comparison, but samples many fits to attach ' +
templates/index.html:13067:      label: 'Refit my current peaks',
templates/index.html:13068:      hint: 'Refits the peaks already on this tab, using their current ' +
templates/index.html:13070:            'polish a fit you’ve already built manually — add peaks first.',
templates/index.html:13077:      { key: 'n_refits', type: 'number', min: 1, max: 32, step: 1,
templates/index.html:13078:        label: 'Stability re-fits',
templates/index.html:13079:        tip: 'How many times each model is re-fitted from different ' +
templates/index.html:13084:        tip: 'After fitting, scan the leftover signal for a clear peak ' +
templates/index.html:13086:      { key: 'fit_full_window', type: 'checkbox',
templates/index.html:13089:             'peaks. Check this to fit the full window you selected — ' +
templates/index.html:13095:        tip: 'Parallel samplers exploring the fit. More handles hard, ' +
templates/index.html:13108:             'fitting. Shirley is the usual choice for core levels.' },
templates/index.html:13114:    winner: 'Best fit',
templates/index.html:13118:    notFitted: 'Not fitted',
templates/index.html:13121:    noResult: 'No usable fit came out of this run — see Technical ' +
templates/index.html:13123:    pinnedLimit: 'Treat with caution: the best fit only held together by ' +
templates/index.html:13126:    constraintBind: 'Treat with caution: this fit is pressing against a ' +
templates/index.html:13134:    provisional: 'Some values behind this fit are provisional (not yet ' +
templates/index.html:13144:  toastApplied: 'Added {n} suggested peak(s) to your fit. These are ' +
templates/index.html:13149:    stability: 'the fit would not reproduce reliably',
templates/index.html:13150:    orphan: 'components kept losing their identity between re-fits',
templates/index.html:13226:// lmfit param slug ('s_main_cl2p12_ratio') → plain words
templates/index.html:13298:// branching the backend's raw message uses (autofit/methods/
templates/index.html:13302:  // The honest "structure known, no fittable features" stub (app.py's
templates/index.html:13314:    return 'No fittable peaks were found in this window for ' +
templates/index.html:13343:        `(${_fpModelLabel(d.winner)}) only fits well with ` +
templates/index.html:13349:        'when re-fit from different starting points, so component ' +
templates/index.html:13380:      're-fits, no parameter limits hit, no unexplained extra peaks.');
templates/index.html:13519:// picked region (e.g. one member of a ctrl-click co-fit pair) stays
templates/index.html:13530:// `practical` flag, autofit/coverage_index.py — never invents a BE, just
templates/index.html:13531:// hides valence/too-deep levels a bench chemist would not try to fit).
templates/index.html:13562:// invented coverage. A search query dims (not hides — a co-fit pick stays
templates/index.html:13679:// to fit two together)"). Returns a NEW Set — never mutates `current`.
templates/index.html:13704:  // hint — a co-fit selection (2 regions) has no single "right" window,
templates/index.html:13848:  // co-fit member filtered/collapsed out of view by the search box or the
templates/index.html:13863:    // corrected-frame data, same convention as the manual fit path
templates/index.html:13876:        status.textContent = '“Refit my current peaks” needs peaks on ' +
templates/index.html:13906:    _fpLast = { body, method, regions, fitFullWindow: !!options.fit_full_window };
templates/index.html:13940:    // plainly: a literature-based limit had to hold the fit together
templates/index.html:14006:    th('fit quality (χ²ᵣ)', T.chi2r) + th('ranking score', T.bic) +
templates/index.html:14014:      // "<b>Best fit</b>" text in the tooltip instead of rendering bold
templates/index.html:14102:  // The chart FREEZES its background/fit-curve display to state.fitResult's
templates/index.html:14103:  // OWN be/bgIntensity arrays once a fit exists (updatePlot's "haveFit"
templates/index.html:14105:  // set, frozen to THAT fit's own (possibly narrower) range. Applying new
templates/index.html:14107:  // background/fit cropped to the OLD frozen range regardless of how wide
templates/index.html:14108:  // a window Find Peaks actually used — root cause of "fit + background
templates/index.html:14110:  // Peaks' own response has no be/fittedY/bgIntensity arrays to rebuild a
templates/index.html:14111:  // proper fitResult from, so when this run used "fit the entire window,"
templates/index.html:14113:  // unfit-preview path (getROIData() + client-side computeBackground()),
templates/index.html:14116:  // Default (unchecked) leaves state.fitResult untouched — today's
templates/index.html:14118:  if (_fpLast && _fpLast.fitFullWindow) {
templates/index.html:14119:    state.fitResult = null;
templates/index.html:14120:    // Clearing state.fitResult fixes the CHART (updatePlot's "haveFit"
templates/index.html:14125:    // could still read the OLD fit's stale "ROI: 278.0-290.4 eV" even
templates/index.html:14127:    // "no committed fit yet" state TabManager.activateTab already uses
templates/index.html:14128:    // when a tab has no state.fitResult, rather than inventing a new
templates/index.html:14130:    const fqEl = document.getElementById('fit-quality');
templates/index.html:14137:    // DOM state keyed off state.fitResult, separate from both the chart
templates/index.html:14139:    // this call it kept showing the OLD fit's chi/RMSE/table after
templates/index.html:14140:    // state.fitResult was cleared, until some unrelated later action
templates/index.html:14142:    // state.fitResult === null correctly (falls back to its own
templates/index.html:14143:    // "Run the fit to see results." placeholder).
autofit/methods/base.py:7:when-each-wins live in docs/autofit/peak-fit-methods-decision-matrix.md.
autofit/methods/base.py:27:    # fitted parameters ({role, shape, center, fwhm, amplitude, ...}).
autofit/methods/base.py:66:        (``autofit.engine.compare_models``'s screen->stabilize sweep).
autofit/methods/base.py:80:            f"{self.reason} — see docs/autofit/peak-fit-methods-decision-matrix.md"
autofit/methods/base.py:86:    1/√max(y,1) weights — matching the existing manual-fit path.  Valid for
autofit/methods/base.py:88:    noise estimate (fitalg LIMITATIONS §8; spec §9) when replicates exist.
autofit/methods/ic_model_comparison.py:2:Method 2 — grammar + information-criterion model comparison (fitalg engine).
autofit/methods/ic_model_comparison.py:22:    "noise_floor", "n_refits", "rng_seed", "candidate_filter",
autofit/methods/ic_model_comparison.py:25:    "enable_preseed", "fit_full_window",
autofit/methods/ic_model_comparison.py:28:ENGINE_VERSION = "autofit-stage2"
autofit/methods/ic_model_comparison.py:62:            n_refits=int(opts.pop("n_refits", 20)),
autofit/methods/ic_model_comparison.py:73:            fit_full_window=bool(opts.pop("fit_full_window", False)),
autofit/methods/ic_model_comparison.py:99:        # Slots classified "correctly absent" won the BIC*-adjustment benefit
autofit/methods/ic_model_comparison.py:101:        # fitted peaks would contradict that classification (Codex finding
autofit/methods/ic_model_comparison.py:119:                for c in top.primary_fit.components if c.slot_role == r
autofit/methods/ic_model_comparison.py:134:                    "exist but a bound-fixed refit of a constraint-limited "
autofit/methods/ic_model_comparison.py:144:                    "across refits (min persistence "
autofit/methods/ic_model_comparison.py:211:    lm = report.primary_fit.lmfit_result
autofit/methods/ic_model_comparison.py:215:        comp = next((c for c in report.primary_fit.components
autofit/methods/ic_model_comparison.py:260:            # review): full-k raw BIC, the weighted-χ² criterion the fits
autofit/methods/ic_model_comparison.py:278:                 "fitted_center": p.fitted_center,
autofit/methods/ic_model_comparison.py:279:                 "fitted_fwhm": p.fitted_fwhm,
autofit/methods/ic_model_comparison.py:295:            # multi-start fits reproduced the reported minimum's χ² basin
autofit/methods/ic_model_comparison.py:315:        # physical constant this fit was built on (never comments-only).
autofit/methods/__init__.py:6:  1. least_squares           — wraps existing run_fit (the honest baseline)
autofit/methods/__init__.py:7:  2. ic_model_comparison     — fitalg engine port (peak-count by IC panel)
autofit/methods/sparse_map.py:12:L1 shrinkage biases amplitudes (mitigated here by a debiased NNLS refit on
autofit/methods/sparse_map.py:302:                    "kind": "unavailable_single_fit", "range_ev": None,
autofit/methods/least_squares.py:4:Thin wrapper over the EXISTING ``fitting.run_fit`` (unchanged, same code the
autofit/methods/least_squares.py:15:from fitting import run_fit
autofit/methods/least_squares.py:22:    "fit_method", "n_perturb", "manual_bg",
autofit/methods/least_squares.py:47:        fit_method = opts.pop("fit_method", None)
autofit/methods/least_squares.py:48:        fit_kws = {"method": fit_method} if fit_method else None
autofit/methods/least_squares.py:50:        res = run_fit(
autofit/methods/least_squares.py:60:            fit_kws=fit_kws,
autofit/methods/least_squares.py:79:                    "kind": "unavailable_single_fit", "range_ev": None,
autofit/methods/least_squares.py:94:            diagnostics={"lmfit_message": res.get("message")},
autofit/methods/bayesian_exchange_mc.py:21:  estimated noise scale is the defensible default (fitalg LIMITATIONS §8;
autofit/methods/bayesian_exchange_mc.py:60:    _extract_fitted_components,
autofit/methods/bayesian_exchange_mc.py:80:    """Free-parameter view of a CandidateModel's lmfit Parameters."""
autofit/methods/bayesian_exchange_mc.py:84:    params: Any                       # lmfit Parameters (exprs resolve here)
autofit/methods/bayesian_exchange_mc.py:85:    composite: Any                    # lmfit composite Model
autofit/methods/bayesian_exchange_mc.py:508:    class _R:  # minimal ModelResult stand-in for _extract_fitted_components
autofit/methods/bayesian_exchange_mc.py:511:    comps = _extract_fitted_components(_R, model)
autofit/methods/bayesian_exchange_mc.py:549:                    "meaningless; refit with larger steps/more sweeps")
autofit/methods/bayesian_exchange_mc.py:567:                "kind": "unavailable_single_fit", "range_ev": None,
autofit/methods/multivariate_mcr.py:14:THIS METHOD'S JOB IS DIFFERENT from the single-spectrum fitters: given a
autofit/methods/multivariate_mcr.py:22:(deterministic; no RNG).  It does NOT emit fitted peaks — `peaks` is empty
autofit/methods/multivariate_mcr.py:25:fits equally well) and is stated in the payload, never hidden.
autofit/methods/multivariate_mcr.py:51:    als_tol=1e-3,              # relative lack-of-fit change per iteration —
autofit/methods/multivariate_mcr.py:246:            "lack_of_fit": history[-1],
autofit/methods/multivariate_mcr.py:253:                "T with CT ≥ 0, T⁻¹Sᵀ ≥ 0 fits equally); treat pure spectra "
autofit/methods/multivariate_mcr.py:264:            peaks=[],                # by design: states, not fitted peaks
autofit/methods/multivariate_mcr.py:269:                         "lack_of_fit": history[-1],
autofit/methods/max_entropy.py:24:THIS METHOD'S JOB IS DIFFERENT from the fitters: given a single spectrum

exec
/bin/zsh -lc "rg -n \"Tougaard|tougaard|background|saved|inventory|spec\\.json|fit\" --glob '*.json' --glob '*.spec.json' --glob '*.fixture*' --glob '*.yaml' --glob '*.yml' --glob '*.toml' --glob '*.csv' --glob '*.tsv' ." in /Users/skyefortier/xps-verify
 succeeded in 0ms:
./data/xps/schema.json:130:          "description": "Curated-tier opt-OUT: false marks a record whose source_id resolves to a real external citation, but whose stored value is a disclosed curator convention that deliberately diverges from that citation (e.g. an internal calibration anchor), not a value confirmed against it. Absent (the default for every existing curated record) means true — the bridge's VERIFIED status is unaffected unless a curator explicitly sets this to false. See autofit/reference_bridge.py.",
./data/xps/schema.json:163:          "description": "Curated-tier opt-OUT: false marks a record whose source_id resolves to a real external citation, but whose stored value is a disclosed curator convention that deliberately diverges from that citation, not a value confirmed against it. Absent (the default) means true. See autofit/reference_bridge.py.",
./data/xps/legacy/chemical-states.json:508:          "state": "Sulfite (SO₃²⁻)",
./data/xps/fit-physics.json:20:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:46:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:72:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:98:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:124:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:169:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:195:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:224:     "source": "metallic-screening asymmetry on sp2 carbon; engine C 1s grammar families A/AG/MG (see autofit/regions/c1s.py provenance)",
./data/xps/fit-physics.json:245:     "source": "fitalg tunable; labeled-set fits 5.9-6.7",
./data/xps/fit-physics.json:270:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:296:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:329:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:362:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:388:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:414:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:440:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:466:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:499:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:532:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:558:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:584:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:610:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:636:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:662:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:688:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:714:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:740:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:766:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:792:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:818:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:844:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:870:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:896:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:922:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:948:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:974:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1000:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1026:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1052:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1078:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1104:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1137:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1170:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1196:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1222:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1248:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1312:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1338:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1364:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1390:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1416:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1442:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1468:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1494:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1520:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1546:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1572:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1598:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1624:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1650:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1676:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1702:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1728:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1754:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1780:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1806:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1832:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1858:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1884:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1910:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1936:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1962:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:1988:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2014:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2040:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2066:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2092:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2125:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2158:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2197:     "source": "Ilton & Bagus 2011; Schindler et al., GCA 73 (2009) 2488, DOI 10.1016/j.gca.2009.02.008; labeled set fits 6.07-6.38",
./data/xps/fit-physics.json:2210:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2249:     "source": "Ilton & Bagus 2011; Schindler et al., GCA 73 (2009) 2488, DOI 10.1016/j.gca.2009.02.008; labeled set fits 6.07-6.38",
./data/xps/fit-physics.json:2262:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2314:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2347:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2373:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2406:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2439:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2484:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2510:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2536:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2562:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2588:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2614:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2640:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2666:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2692:    "caveat": "measured intensity ratios deviate (e.g. U 4f fitted 0.65-0.75; satellite pairs ~0.9)",
./data/xps/fit-physics.json:2703: "schema": "fit-physics-v1",
./data/xps/fit-physics.json:2716:     "source": "metallic-screening asymmetry on sp2 carbon; engine C 1s grammar families A/AG/MG (see autofit/regions/c1s.py provenance)",
./data/xps/fit-physics.json:2732:     "source": "fitalg tunable; labeled-set fits 5.9-6.7",
./data/xps/fit-physics.json:2753:     "source": "Ilton & Bagus 2011; Schindler et al., GCA 73 (2009) 2488, DOI 10.1016/j.gca.2009.02.008; labeled set fits 6.07-6.38",
./data/xps/elements-main.json:27:              "notes": "Nominal is the raw NIST-evaluated value (Powe95, starred: 284.44) — the literature-verified C 1s elemental-carbon position, carrying this record's VERIFIED/curated status honestly (provenance audit, 2026-07-16). The app's own C 1s graphite charge-correction default is a SEPARATE, disclosed engineering convention (284.5 eV; see templates/index.html's cc-lit dropdown and Auto-Fit C1s Graphite logic) — chosen for internal fit-to-fit consistency, not asserted as a literature value, and intentionally does NOT flow through this reference/citation pipeline (curator decision, S. Fortier 2026-06). NIST evidence: 20 elemental-form records span 282.0-286.9 incl. the Powe95 evaluated 284.44; NIST compound records (2015 page) extend organic C 1s components to 289.22 — region spans both. Carbonate/fluorocarbon upward extension (>289.5) is a future expansion."
./tests/fixtures/curated_records_snapshot.json:22:      "notes": "Nominal is the raw NIST-evaluated value (Powe95, starred: 284.44) — the literature-verified C 1s elemental-carbon position, carrying this record's VERIFIED/curated status honestly (provenance audit, 2026-07-16). The app's own C 1s graphite charge-correction default is a SEPARATE, disclosed engineering convention (284.5 eV; see templates/index.html's cc-lit dropdown and Auto-Fit C1s Graphite logic) — chosen for internal fit-to-fit consistency, not asserted as a literature value, and intentionally does NOT flow through this reference/citation pipeline (curator decision, S. Fortier 2026-06). NIST evidence: 20 elemental-form records span 282.0-286.9 incl. the Powe95 evaluated 284.44; NIST compound records (2015 page) extend organic C 1s components to 289.22 — region spans both. Carbonate/fluorocarbon upward extension (>289.5) is a future expansion."
./tests/fixtures/curated_records_snapshot.json:2019:              "state": "Sulfite (SO₃²⁻)",
./tests/fixtures/xps_legacy_snapshot.json:552:    "state": "Sulfite (SO₃²⁻)",
./tests/autofit/fixtures/c1s_battery_expected.json:1423:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1424:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1428:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1429:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1433:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1434:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1438:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1439:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1443:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1444:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1448:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1449:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1453:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1454:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1458:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1459:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1463:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1464:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1468:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1469:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1473:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1474:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1478:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1479:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1483:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1484:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1488:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/c1s_battery_expected.json:1489:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/c1s_battery_expected.json:1494:   "reason": "internally inconsistent fitResult (fittedY 143 pts vs be 142 pts \u2014 stale fittedY from an earlier ROI)"
./tests/autofit/fixtures/cl2p_battery_expected.json:21:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/cl2p_battery_expected.json:44:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/cl2p_battery_expected.json:67:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/b1s_battery_expected.json:86:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/b1s_battery_expected.json:91:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/b1s_battery_expected.json:96:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/b1s_battery_expected.json:101:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/b1s_battery_expected.json:106:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/b1s_battery_expected.json:111:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:116:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:121:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:126:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:131:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:136:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:141:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:146:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:151:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:156:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/b1s_battery_expected.json:161:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1102:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1107:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1112:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1117:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1122:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1127:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1132:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1136:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1137:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1141:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1142:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1146:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1147:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1151:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1152:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1156:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1157:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1161:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1162:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1166:   "project": "Cl2p_projfit_test.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1167:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1171:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1172:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1176:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1177:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1181:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1182:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1186:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1187:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1191:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1192:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1196:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1197:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1201:   "project": "Project9_CasaXPS_newfit.proj.zip",
./tests/autofit/fixtures/u4f_battery_expected.json:1202:   "reason": "legacy fitResult (no be/fittedY)"
./tests/autofit/fixtures/u4f_battery_expected.json:1207:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1212:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1217:   "reason": "fit-time grid drifted from current ui state"
./tests/autofit/fixtures/u4f_battery_expected.json:1222:   "reason": "fit-time grid drifted from current ui state"
./docs/autofit/inventory/replicate_noise_survey.json:2: "note": "replicate-difference noise survey; see autofit/noise.py for the estimator and its corrections",
./docs/autofit/inventory/replicate_noise_survey.json:25:   "fit_residual_rel": 0.8814844175820874,
./docs/autofit/inventory/replicate_noise_survey.json:27:    "drift_dominated: 96% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:29:    "poor_variance_fit: rel residual 0.88 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/replicate_noise_survey.json:58:   "fit_residual_rel": 0.6659894378107989,
./docs/autofit/inventory/replicate_noise_survey.json:61:    "drift_dominated: 96% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:63:    "poor_variance_fit: rel residual 0.67 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/replicate_noise_survey.json:92:   "fit_residual_rel": 0.30467005315976586,
./docs/autofit/inventory/replicate_noise_survey.json:94:    "drift_dominated: 96% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:124:   "fit_residual_rel": 0.5827309259583758,
./docs/autofit/inventory/replicate_noise_survey.json:126:    "drift_dominated: 97% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:128:    "poor_variance_fit: rel residual 0.58 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/replicate_noise_survey.json:157:   "fit_residual_rel": 0.2665439549545222,
./docs/autofit/inventory/replicate_noise_survey.json:159:    "drift_dominated: 100% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:189:   "fit_residual_rel": 0.27571051089469667,
./docs/autofit/inventory/replicate_noise_survey.json:191:    "drift_dominated: 89% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:221:   "fit_residual_rel": 0.31736770203699866,
./docs/autofit/inventory/replicate_noise_survey.json:223:    "drift_dominated: 95% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:233:   "project": "Cl2p_projfit_test.proj.zip",
./docs/autofit/inventory/replicate_noise_survey.json:250:   "fit_residual_rel": 0.8714066452578878,
./docs/autofit/inventory/replicate_noise_survey.json:252:    "drift_dominated: 97% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:253:    "poor_variance_fit: rel residual 0.87 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/replicate_noise_survey.json:262:   "project": "Cl2p_projfit_test.proj.zip",
./docs/autofit/inventory/replicate_noise_survey.json:275:   "fit_residual_rel": 0.45308613160471783,
./docs/autofit/inventory/replicate_noise_survey.json:278:    "drift_dominated: 93% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:288:   "project": "Cl2p_projfit_test.proj.zip",
./docs/autofit/inventory/replicate_noise_survey.json:305:   "fit_residual_rel": 0.7674118847871513,
./docs/autofit/inventory/replicate_noise_survey.json:308:    "drift_dominated: 88% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:310:    "poor_variance_fit: rel residual 0.77 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/replicate_noise_survey.json:319:   "project": "Project9_CasaXPS_newfit.proj.zip",
./docs/autofit/inventory/replicate_noise_survey.json:336:   "fit_residual_rel": 0.8714066452578878,
./docs/autofit/inventory/replicate_noise_survey.json:338:    "drift_dominated: 97% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:339:    "poor_variance_fit: rel residual 0.87 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/replicate_noise_survey.json:348:   "project": "Project9_CasaXPS_newfit.proj.zip",
./docs/autofit/inventory/replicate_noise_survey.json:365:   "fit_residual_rel": 0.7674118847871513,
./docs/autofit/inventory/replicate_noise_survey.json:368:    "drift_dominated: 88% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:370:    "poor_variance_fit: rel residual 0.77 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/replicate_noise_survey.json:399:   "fit_residual_rel": 0.8814844175820874,
./docs/autofit/inventory/replicate_noise_survey.json:401:    "drift_dominated: 96% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:403:    "poor_variance_fit: rel residual 0.88 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/replicate_noise_survey.json:432:   "fit_residual_rel": 0.6659894378107989,
./docs/autofit/inventory/replicate_noise_survey.json:435:    "drift_dominated: 96% of the pair-difference variance was drift \u2014 the \u03c3(I) fit rests on the residual; treat with caution",
./docs/autofit/inventory/replicate_noise_survey.json:437:    "poor_variance_fit: rel residual 0.67 \u2014 \u03c3\u00b2(I) = a + b\u00b7I may be the wrong family here"
./docs/autofit/inventory/reference_fits_inventory.json:3724: "Cl2p_projfit_test.proj.zip": [
./docs/autofit/inventory/reference_fits_inventory.json:4716: "Project9_CasaXPS_newfit.proj.zip": [
./docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:342:  "background": {

exec
/bin/zsh -lc 'git diff --name-status 173f002''^ 173f002 -- fitting.py templates/index.html tests/js/tougaard_twin.test.js autofit/engine.py autofit/methods tests/test_tougaard_background.py && git diff --stat 173f002''^ 173f002 -- fitting.py templates/index.html tests/js/tougaard_twin.test.js autofit/engine.py autofit/methods tests/test_tougaard_background.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Pzfp6SWs' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BUtco9Tw' (errno=Operation not permitted)
M	tests/test_tougaard_background.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2RAAPDfv' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-okUHiM4U' (errno=Operation not permitted)
 tests/test_tougaard_background.py | 28 ++++++++++++++++++++++++++--
 1 file changed, 26 insertions(+), 2 deletions(-)

codex
The Python Tougaard file has 9 tests total; the changed regression pin is at [tests/test_tougaard_background.py](/Users/skyefortier/xps-verify/tests/test_tougaard_background.py:206). I’m narrowing the fixture search now to actual Tougaard/background numeric pins instead of broad “fit” hits, because the initial repo-wide JSON scan is too noisy.
exec
/bin/zsh -lc "rg -n -i \"tougaard\" --glob '*.json' --glob '*.spec.json' --glob '*.fit.json*' --glob '*.proj*' --glob '*.yaml' --glob '*.yml' --glob '*.toml' ." in /Users/skyefortier/xps-verify
 exited 1 in 0ms:
exec
/bin/zsh -lc "nl -ba tests/js/tougaard_twin.test.js | sed -n '1,260p'" in /Users/skyefortier/xps-verify
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
/bin/zsh -lc "rg -n '\"background\"|bgIntensity|bgSubtracted|background_type|backgroundType|bg_type' tests docs scripts data --glob '*.json' --glob '*.spec.json' --glob '*.fit.json*' --glob '*.yaml' --glob '*.yml'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:342:  "background": {

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '1,220p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	fitting.py – XPS peak fitting engine using lmfit.
     3	
     4	Supported lineshapes
     5	--------------------
     6	  gaussian        – pure Gaussian (amplitude at peak max, FWHM parameterised)
     7	  lorentzian      – pure Lorentzian
     8	  pseudo_voigt_gl – linear GL mix: (1‑η)·G + η·L  (η = Lorentzian fraction)
     9	  asymmetric_gl   – GL mix with independent left/right FWHM
    10	  doniach_sunjic  – metallic asymmetric lineshape
    11	  ds_g            – DS+G: DS core × Gaussian convolution (formerly "la_casaxps")
    12	  la_casaxps      – TRUE CasaXPS LA(α,β,m): asymmetric base Lorentzian + integer-kernel Gauss conv
    13	
    14	Backgrounds
    15	-----------
    16	  shirley         – iterative Shirley (Proctor & Sherwood 1982)
    17	  linear          – straight‑line between endpoints
    18	  none            – flat zero
    19	
    20	Spin‑orbit constraints are handled via lmfit parameter expressions.
    21	"""
    22	
    23	from __future__ import annotations
    24	
    25	import logging
    26	import warnings
    27	from typing import Any
    28	
    29	import numpy as np
    30	from lmfit import Model, Parameters
    31	from scipy.integrate import trapezoid
    32	
    33	log = logging.getLogger(__name__)
    34	
    35	# ─────────────────────────────────────────────────────────────────────────────
    36	# Lineshape functions (all FWHM‑parameterised, amplitude = peak maximum)
    37	# ─────────────────────────────────────────────────────────────────────────────
    38	
    39	_LN2 = np.log(2.0)
    40	_SQRT_PI_4LN2 = np.sqrt(np.pi / (4.0 * _LN2))  # ≈ 1.06447
    41	
    42	
    43	def _gaussian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    44	    """Gaussian; amplitude is the peak maximum value."""
    45	    return amplitude * np.exp(-4.0 * _LN2 * ((x - center) / fwhm) ** 2)
    46	
    47	
    48	def _lorentzian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    49	    """Lorentzian; amplitude is the peak maximum value."""
    50	    hwhm = fwhm / 2.0
    51	    return amplitude * hwhm ** 2 / ((x - center) ** 2 + hwhm ** 2)
    52	
    53	
    54	def _pseudo_voigt_gl(
    55	    x: np.ndarray,
    56	    amplitude: float,
    57	    center: float,
    58	    fwhm: float,
    59	    gl_ratio: float,
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
   116	    dx = c − x so the power-law tail extends toward HIGHER BE (inelastic losses).
   117	    gamma_asym > 0 adds an exponential envelope that limits how far the
   118	    high-BE tail extends (0 = pure DS power-law tail, no limit).
   119	
   120	    alpha     : asymmetry index  (0 = symmetric Lorentzian, typical 0–0.3)
   121	    gamma_asym: exponential tail-decay rate (eV⁻¹).  0 = standard DS.
   122	    """
   123	    alpha      = float(np.clip(alpha, 0.0, 0.995))
   124	    gamma_asym = max(float(gamma_asym), 0.0)
   125	    gamma      = max(fwhm / 2.0, 1e-12)
   126	    cos0 = np.cos(np.pi * alpha / 2.0)
   127	    if abs(cos0) < 1e-12:
   128	        cos0 = 1e-12
   129	    norm = gamma ** (1.0 - alpha) / cos0
   130	    # dx = center − x  →  positive on LOW-BE side, negative on HIGH-BE side.
   131	    # The arctan and power-law terms produce a tail toward HIGH-BE (dx < 0).
   132	    dx = center - x
   133	    phase = np.pi * alpha / 2.0 + (1.0 - alpha) * np.arctan(dx / gamma)
   134	    denom = (dx ** 2 + gamma ** 2) ** ((1.0 - alpha) / 2.0)
   135	    with warnings.catch_warnings():
   136	        warnings.simplefilter("ignore")
   137	        result = amplitude * norm * np.cos(phase) / denom
   138	    # Exponential envelope to gently limit the HIGH-BE tail extent.
   139	    # dx = center - x: negative on the HIGH-BE side (x > center).
   140	    # We want: decay = 1 at center, tapering toward zero far into the tail.
   141	    # Use |dx| on the high-BE side only: exp(-gamma_asym * max(x - center, 0))
   142	    if gamma_asym > 0.0:
   143	        tail_decay = np.exp(-gamma_asym * np.maximum(x - center, 0.0))
   144	        result = result * tail_decay
   145	    result = np.where(np.isfinite(result), result, 0.0)
   146	    return result
   147	
   148	
   149	def _ds_g_dscore_gauss(
   150	    x: np.ndarray,
   151	    amplitude: float,
   152	    center: float,
   153	    alpha: float,    # CasaXPS: dimensionless asymmetry index, 0 ≤ α < 0.5
   154	    beta: float,     # CasaXPS: Lorentzian half-width (eV)
   155	    m_gauss: float,  # CasaXPS: Gaussian FWHM (eV) for convolution
   156	) -> np.ndarray:
   157	    """
   158	    DS+G lineshape (formerly mislabeled "LA(α,β,m) [CasaXPS]") —
   159	    Doniach-Šunjić asymmetric core convolved analytically with a Gaussian
   160	    instrument-broadening kernel. NOT to be confused with the true CasaXPS
   161	    LA shape (see _la_casaxps_true), which uses a piecewise-asymmetric
   162	    Lorentzian with point-domain Gaussian convolution.
   163	
   164	    The DS core with asymmetry index α and Lorentzian half-width β is convolved
   165	    with a Gaussian of FWHM m for instrument broadening.
   166	
   167	    Tail direction: eps = x − center > 0 → HIGHER binding energy (physically
   168	    correct: low-energy electron-hole pair excitations produce intensity on the
   169	    high-BE side only).
   170	
   171	    Parameters
   172	    ----------
   173	    alpha   : dimensionless asymmetry index, 0 ≤ α < 0.5
   174	              (0 = symmetric Lorentzian, ~0.1–0.3 for metallic systems)
   175	    beta    : Lorentzian half-width at half-maximum (eV); controls core width
   176	    m_gauss : Gaussian FWHM (eV) for instrument/phonon broadening (0 = none)
   177	
   178	    Fixes (v2)
   179	    ----------
   180	    1. Convolution uses a padded grid (±10·m on each side) with cosine taper
   181	       to eliminate cliff artifacts at array boundaries.
   182	    2. Explicit FFT convolution with a properly normalised Gaussian kernel,
   183	       so DS tail direction is preserved regardless of m value.
   184	    """
   185	    alpha   = float(np.clip(alpha, 0.0, 0.495))
   186	    beta    = max(float(beta),    1e-6)
   187	    m_gauss = max(float(m_gauss), 0.0)
   188	
   189	    # ── DS core evaluator (independent of m_gauss) ───────────────────────────
   190	    #
   191	    # eps = x − center: positive on HIGH-BE side (where tail belongs)
   192	    # DS formula:  cos(πα/2 − (1−α)·arctan2(ε, β)) / (ε² + β²)^((1−α)/2)
   193	    #
   194	    # Sign convention proof:
   195	    #   At ε >> β (high BE):  arctan2(ε, β) → +π/2
   196	    #     phase → πα/2 − (1−α)·π/2 → −π(1−2α)/2  (negative for α < 0.5)
   197	    #     cos(phase) > 0, and denominator grows as |ε|^(1−α)
   198	    #     → slow power-law decay toward HIGH BE  ✓
   199	    #   At ε << −β (low BE): arctan2(ε, β) → −π/2
   200	    #     phase → πα/2 + (1−α)·π/2 → π/2  (for small α)
   201	    #     cos(phase) → 0, faster falloff
   202	    #     → steeper decay toward LOW BE  ✓
   203	
   204	    def _ds_core(xgrid):
   205	        """Evaluate DS kernel on arbitrary grid. Independent of m_gauss."""
   206	        eps = xgrid - center
   207	        r2 = eps ** 2 + beta ** 2
   208	        r2 = np.maximum(r2, 1e-30)
   209	        rPow = r2 ** ((1.0 - alpha) / 2.0)
   210	        phase = np.pi * alpha / 2.0 - (1.0 - alpha) * np.arctan2(eps, beta)
   211	        with warnings.catch_warnings():
   212	            warnings.simplefilter("ignore")
   213	            core = np.cos(phase) / rPow
   214	        core = np.where(np.isfinite(core), core, 0.0)
   215	        return core
   216	
   217	    # ── No Gaussian broadening — just return normalised DS core ──────────────
   218	    if m_gauss < 0.001:
   219	        ds_core = _ds_core(x)
   220	        peak_val = float(np.interp(center, x if x[-1] > x[0] else x[::-1],

codex
The narrowed `tougaard` search across JSON-like fixtures returns no hits; one saved fit JSON has a generic background block, so I’ll inspect that single file to confirm it is not a Tougaard numeric output pin.
exec
/bin/zsh -lc "nl -ba docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json | sed -n '320,370p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   320	          "vary": true
   321	        },
   322	        "gl_ratio": {
   323	          "expr": null,
   324	          "max": 1,
   325	          "min": 0,
   326	          "stderr": null,
   327	          "value": 0.9999999999999999,
   328	          "vary": true
   329	        }
   330	      },
   331	      "_rsfKey": "U 4f",
   332	      "_rsf": 9.674,
   333	      "isChargeReference": false
   334	    }
   335	  ],
   336	  "nextId": 10,
   337	  "chargeCorrection": {
   338	    "method": "c1s",
   339	    "observedBE": "279.833",
   340	    "shift": -4.666999999999973
   341	  },
   342	  "background": {
   343	    "type": "smart",
   344	    "start": "405.1",
   345	    "end": "370.1",
   346	    "shirleyIter": "50"
   347	  },
   348	  "roi": {
   349	    "min": "370.1",
   350	    "max": "405.1"
   351	  },
   352	  "notes": "",
   353	  "manualAnchors": []
   354	}
exec
/bin/zsh -lc 'rg -n "def tougaard_background|Tougaard|tougaard_background|tougaardBackground|background_type|bg_type|bgType" fitting.py templates/index.html app.py -S' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
fitting.py:508:def tougaard_background(
fitting.py:513:    """Single-pass Tougaard universal-cross-section background, with the
fitting.py:518:    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
fitting.py:523:    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
fitting.py:537:    practical Tougaard criterion (B is effectively fitted, which is why the
fitting.py:550:    ``tougaardBackground``.
fitting.py:556:    # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
fitting.py:1004:    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
fitting.py:1011:    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
fitting.py:1038:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1276:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
templates/index.html:1988:                <option value="tougaard" data-tip="Physics-based universal background using electron energy loss cross-sections. More accurate than Shirley but requires wider energy range.">Tougaard-like (single pass)</option>
templates/index.html:3019:        bgType: 'shirley', bgStart: maxBE, bgEnd: minBE,
templates/index.html:3053:      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
templates/index.html:3282:        active.ui.bgType = data.background.type || 'shirley';
templates/index.html:3652:      bgType:      document.getElementById('bg-type')?.value || 'shirley',
templates/index.html:3671:    set('bg-type', ui.bgType);
templates/index.html:3693:      if (mc) mc.style.display = ui.bgType === 'manual' ? 'block' : 'none';
templates/index.html:3694:      const needsIter = (ui.bgType === 'shirley' || ui.bgType === 'smart' || ui.bgType === 'smart_exp' || ui.bgType === 'shirley_linear');
templates/index.html:3700:      // Endpoint averaging also applies to Tougaard (it sets the high-BE
templates/index.html:3702:      const needsEpAvg = needsIter || ui.bgType === 'tougaard';
templates/index.html:4130:// Single-pass Tougaard background — JS twin of fitting.py's
templates/index.html:4131:// tougaard_background (keep the two numerically in agreement; pinned by
templates/index.html:4133:// K(T) = B·T/(C+T²)² with B = 2866 eV², C = 1643 eV² (S. Tougaard,
templates/index.html:4136:function tougaardBackground(be, intensity, nAvg) {
templates/index.html:4147:  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
templates/index.html:4177:  // the practical Tougaard criterion (B effectively fitted; C alone sets the
templates/index.html:4287:// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
templates/index.html:4293:  const type = settings.bgType;
templates/index.html:4320:    // Endpoint averaging matters for Tougaard since the amplitude is
templates/index.html:4322:    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
templates/index.html:4323:    if (type === 'tougaard') return tougaardBackground(be, avgIn);
templates/index.html:4341:  // Averaged for the same reason as Shirley types: the Tougaard amplitude
templates/index.html:4344:  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
templates/index.html:4368:    bgType:      document.getElementById('bg-type').value,
templates/index.html:6032:  const bgType = document.getElementById('bg-type')?.value || 'shirley';
templates/index.html:6033:  if (bgType === 'none') return false;
templates/index.html:6070:  const bgType = document.getElementById('bg-type')?.value || 'shirley';
templates/index.html:6071:  const noBg = bgType === 'none';
templates/index.html:6655:    const bgType = document.getElementById('bg-type').value;
templates/index.html:6675:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvg };
templates/index.html:6676:    if (bgType === 'manual') {
templates/index.html:6771:    const bgType  = document.getElementById('bg-type').value;
templates/index.html:6783:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvgVal };
templates/index.html:6784:    if (bgType === 'manual') {
templates/index.html:7371:    bgType:      (srcUi && srcUi.bgType)      || 'shirley',
templates/index.html:7377:  if (settings.bgType === 'manual') settings = { ...settings, bgType: 'shirley' };
templates/index.html:9068:        ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
templates/index.html:9092:        bgType: 'shirley', bgStart: '', bgEnd: '',
templates/index.html:9676:  const bgType = document.getElementById('bg-type')?.value || '';
templates/index.html:9703:      ['Chi-squared reduced', chiStr], ['Background type', bgType],
templates/index.html:9712:    csv += `# Chi-squared reduced: ${chiStr}\n# Background: ${bgType}\n`;
templates/index.html:12386:  // Grey out endpoint avg for types it can't affect. Tougaard keeps it:

exec
/bin/zsh -lc "find . -iname '*inventory*.json' -o -iname '*.fit.json' -o -iname '*.fit.json.fit.json' -o -iname '*.spec.json' | sort" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
./docs/autofit/inventory/reference_fits_inventory.json
./docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json
./docs/autofit/test_data/Ugly_Fe_2p.spec.json
./docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
./docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
./docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '500,610p'" in /Users/skyefortier/xps-verify
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

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '4128,4198p'" in /Users/skyefortier/xps-verify
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

exec
/bin/zsh -lc 'rg -n -i "tougaard|bgIntensity|background" docs/autofit/inventory/reference_fits_inventory.json docs/autofit/test_data/*.spec.json docs/autofit/test_data/*.fit.json.fit.json' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:342:  "background": {
docs/autofit/test_data/Ugly_Fe_2p_2.spec.json:1229:  "background": [
docs/autofit/test_data/Ugly_Fe_2p.spec.json:1229:  "background": [
docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json:1062:  "background": [
docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json:1254:  "background": [

codex
Production and JS both carry comments that negative signed scale is intentional and unclamped: [fitting.py](/Users/skyefortier/xps-verify/fitting.py:581) anchors with `c0`, and [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:4181) explicitly says signed input passes through. Next I’m computing the actual endpoint delta, guard margin, and an unweighted-production simulation.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '610,660p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba docs/autofit/test_data/Ugly_Fe_2p.spec.json | sed -n '1218,1240p' && nl -ba docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json | sed -n '1056,1070p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   641	    m: float,
   642	) -> np.ndarray:
   643	    """
   644	    True CasaXPS LA(α, β, m) lineshape.
   645	
   646	    Built in two steps per the CasaXPS LA manual:
   647	
   648	    1.  Asymmetric base Lorentzian. Start with a unit-amplitude Lorentzian
   649	        of FWHM `fwhm` centered at `center`:
   650	            L(x) = 1 / (1 + 4·((x − center)/fwhm)²)
   651	        Apply piecewise exponents to introduce asymmetry. CasaXPS defines
   652	        these on a kinetic-energy axis. We use a binding-energy axis, so
   653	        the sides flip:
   654	            LA_base(x) = L(x)^α   for x ≥ center  (high-BE side)
   655	            LA_base(x) = L(x)^β   for x <  center  (low-BE side)
   656	        Increasing α relative to β SUPPRESSES the high-BE tail; decreasing
   657	        α extends it.
   658	
   659	    2.  Gaussian convolution with an integer-point kernel of width `m`.
   660	        m=0 means no convolution. For m>0, build a discrete Gaussian

 succeeded in 0ms:
  1218	    691.3199999999998,
  1219	    691.2199999999998,
  1220	    691.1199999999999,
  1221	    691.0199999999999,
  1222	    690.9199999999998,
  1223	    690.8199999999998,
  1224	    690.7199999999998,
  1225	    690.6199999999999,
  1226	    690.5199999999999,
  1227	    690.4199999999998
  1228	  ],
  1229	  "background": [
  1230	    6033.695407760403,
  1231	    6033.509405194101,
  1232	    6033.488780062195,
  1233	    6033.915596704785,
  1234	    6034.561697804864,
  1235	    6035.05103114091,
  1236	    6035.401810827079,
  1237	    6036.123405161516,
  1238	    6036.567858514341,
  1239	    6036.387477508301,
  1240	    6036.387305126137,
  1056	    274.81999999999994,
  1057	    274.7199999999998,
  1058	    274.6199999999999,
  1059	    274.51999999999975,
  1060	    274.41999999999985
  1061	  ],
  1062	  "background": [
  1063	    3528.318178787814,
  1064	    3528.310377111912,
  1065	    3528.272142972568,
  1066	    3528.2354244825356,
  1067	    3528.2494310206785,
  1068	    3528.29860554677,
  1069	    3528.2892595698568,
  1070	    3528.228482631018,

codex
The shell cannot create here-doc temp files under this sandbox, so I’ll switch computations to `python -c` one-liners. That avoids writing files while still reproducing the numeric claims.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python -c $'"'import numpy as np\\nfrom fitting import tougaard_background\\nB_coef,C_coef=2866.0,1643.0\\nxa=np.concatenate([np.linspace(740.0,720.1,60),np.linspace(720.0,700.0,400)])\\nya=4000.0+800.0*(xa-700.0)/40.0+6000.0*np.exp(-0.5*((xa-710.9)/1.6)**2)\\nc0=float(ya[-1]); net=ya-c0; w=np.abs(np.gradient(xa)); ref=np.zeros(len(xa)); refu=np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2; ref[i]=float(np.sum(kernel*net[i:]*w[i:])); refu[i]=float(np.sum(kernel*net[i:]))\\nraw0=float(ref[0]); rawu0=float(refu[0]); scale=(float(ya[0])-c0)/ref[0]; scaleu=(float(ya[0])-c0)/refu[0]; ref=c0+ref*scale; refu=c0+refu*scaleu; got=tougaard_background(xa,ya)\\ndef badprod(x,y):\\n    xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float); n=len(xa)\\n    if n<2: return np.zeros_like(ya,dtype=float)\\n    flipped=bool(xa[0]<xa[-1])\\n    if flipped: xa,ya=xa[::-1].copy(),ya[::-1].copy()\\n    c0=float(ya[-1]); net=ya-c0; dx=float(abs(xa[1]-xa[0])); diffs=np.diff(xa); uniform=bool(dx>0.0 and np.max(np.abs(diffs-diffs[0]))<=1e-6*dx)\\n    if uniform:\\n        m=np.arange(n,dtype=float); T=m*dx; k=(B_coef*T)/(C_coef+T*T)**2; bg=np.convolve(net,k[::-1])[n-1:]*dx\\n    else:\\n        bg=np.zeros(n,dtype=float)\\n        for i in range(n):\\n            T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2; bg[i]=float(np.sum(kernel*net[i:]))\\n    out=np.full(n,c0) if bg[0]==0.0 else c0+bg*((float(ya[0])-c0)/bg[0])\\n    return out[::-1] if flipped else out\\nbad=badprod(xa,ya)\\nx=np.linspace(740.0,700.0,300); y=4000.0+6000.0*np.exp(-0.5*((x-710.9)/1.6)**2); xj=x.copy(); xj[1:-1]+=1e-4*np.sin(np.arange(len(x)-2))\\nprint(\"n\",len(xa),\"xa0\",xa[0],\"xa_last\",xa[-1])\\nprint(\"ya0\",ya[0],\"c0\",c0,\"endpoint_delta\",ya[0]-c0)\\nprint(\"raw_ref0_weighted\",raw0,\"raw_ref0_unweighted\",rawu0)\\nprint(\"anchor_scale_weighted\",scale,\"anchor_scale_unweighted\",scaleu)\\nprint(\"guard_margin\",float(np.max(np.abs(ref-refu))))\\nprint(\"got_vs_ref_max\",float(np.max(np.abs(got-ref))),\"allclose\",bool(np.allclose(got,ref,rtol=1e-9)))\\nprint(\"bad_vs_ref_max\",float(np.max(np.abs(bad-ref))),\"allclose\",bool(np.allclose(bad,ref,rtol=1e-9)))\\nprint(\"bad_test_result\", \"PASS\" if (np.max(np.abs(ref-refu))>10.0 and np.allclose(bad,ref,rtol=1e-9)) else \"FAIL\")\\nprint(\"jitter_uniform_nonuniform_max\",float(np.max(np.abs(tougaard_background(x,y)-tougaard_background(xj,y)))))'" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "rg -n '\"background\"|\"background_type\"|\"bgType\"|\"type\"|\"method\"' docs/autofit/test_data/Ugly_Fe_2p.spec.json docs/autofit/test_data/Ugly_Fe_2p_2.spec.json docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:338:    "method": "c1s",
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:342:  "background": {
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:343:    "type": "smart",
docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json:1050:    "bgType": "shirley",
docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json:1254:  "background": [
docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json:858:    "bgType": "shirley",
docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json:1062:  "background": [
docs/autofit/test_data/Ugly_Fe_2p_2.spec.json:815:    "bgType": "shirley",
docs/autofit/test_data/Ugly_Fe_2p_2.spec.json:1229:  "background": [
docs/autofit/test_data/Ugly_Fe_2p.spec.json:815:    "bgType": "shirley",
docs/autofit/test_data/Ugly_Fe_2p.spec.json:1229:  "background": [

exec
/bin/zsh -lc "find tests -type f \\( -name '*tougaard*' -o -name '*.test.js' -o -name '*.py' \\) | sort | sed -n '1,200p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/__pycache__/test_tougaard_background.cpython-312-pytest-9.0.3.pyc
tests/autofit/battery_common.py
tests/autofit/stress_cases.py
tests/autofit/test_b1s_cl2p_batteries.py
tests/autofit/test_b1s_cl2p_parity_gates.py
tests/autofit/test_bayesian_method.py
tests/autofit/test_bayesian_real_gate.py
tests/autofit/test_bayesian_u4f_unresolved_gate.py
tests/autofit/test_bic_companions.py
tests/autofit/test_browser_schema_roundtrip.py
tests/autofit/test_c1s_parity_battery.py
tests/autofit/test_c1s_parity_gate.py
tests/autofit/test_candidate_pool.py
tests/autofit/test_candidate_pool_real_gate.py
tests/autofit/test_candidate_pool_wiring.py
tests/autofit/test_cited_values.py
tests/autofit/test_cl2p_freewidth.py
tests/autofit/test_coverage_index.py
tests/autofit/test_coverage_structure.py
tests/autofit/test_criteria.py
tests/autofit/test_cwt_detector.py
tests/autofit/test_engine_doublet.py
tests/autofit/test_filtered_dominant_flag.py
tests/autofit/test_fit_full_window_option.py
tests/autofit/test_fit_physics.py
tests/autofit/test_fit_physics_wiring.py
tests/autofit/test_max_entropy.py
tests/autofit/test_methods_seam.py
tests/autofit/test_multivariate_mcr.py
tests/autofit/test_noise_model.py
tests/autofit/test_preseed_dominants.py
tests/autofit/test_progress_callback.py
tests/autofit/test_quantification_lint.py
tests/autofit/test_reference_bridge.py
tests/autofit/test_region_provenance_honesty.py
tests/autofit/test_resolver.py
tests/autofit/test_sparse_map.py
tests/autofit/test_stage2_completeness.py
tests/autofit/test_stage2_rereview_findings.py
tests/autofit/test_stress_honesty.py
tests/autofit/test_structural_fallback.py
tests/autofit/test_u4f_parity_battery.py
tests/autofit/test_u4f_parity_gate.py
tests/conftest.py
tests/fixtures/regen_curated_snapshot.py
tests/js/batch_propagation.test.js
tests/js/find_peaks_coverage.test.js
tests/js/find_peaks_periodic_table.test.js
tests/js/find_peaks_plain_message.test.js
tests/js/find_peaks_progress.test.js
tests/js/ref_core.test.js
tests/js/shape_switch_roundtrip.test.js
tests/js/tougaard_twin.test.js
tests/test_api_analyze.py
tests/test_api_analyze_coverage.py
tests/test_api_analyze_progress.py
tests/test_api_fit_full_window_option.py
tests/test_browser_batch_roi.py
tests/test_browser_cc_overlay_repaint.py
tests/test_browser_find_peaks_coverage.py
tests/test_browser_find_peaks_drag.py
tests/test_browser_find_peaks_full_window.py
tests/test_browser_find_peaks_method_tooltips.py
tests/test_browser_find_peaks_progress.py
tests/test_browser_find_peaks_tooltip_markup.py
tests/test_browser_identify_frame.py
tests/test_browser_legacy_auger.py
tests/test_browser_overlay_zip_roundtrip.py
tests/test_browser_palette.py
tests/test_browser_reference_mode.py
tests/test_chem_state_tier.py
tests/test_conflict_resolution.py
tests/test_coverage_exhaustion.py
tests/test_cutover.py
tests/test_expand_coverage.py
tests/test_la_continuous_m.py
tests/test_la_short_input.py
tests/test_legacy_hardening.py
tests/test_legacy_parity.py
tests/test_machine_tier.py
tests/test_mixed_ds_lacx_e2e.py
tests/test_short_caveat.py
tests/test_tougaard_background.py
tests/test_xps_reference.py

codex
This environment exposes no `python` binary, so I’ll use the project’s interpreter if present, or `python3`. The fixture files with saved background arrays all declare `bgType: "shirley"` or `"smart"`, not Tougaard, which supports the “no saved Tougaard numeric pin” claim.
exec
/bin/zsh -lc 'ls -d venv .venv 2>/dev/null; command -v python3; command -v node; command -v pytest; command -v npm' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
/usr/bin/python3
/Users/skyefortier/.local/bin/node
/Users/skyefortier/.local/bin/npm

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 venv/bin/python -c $'"'import sys; print(sys.version)'" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: no such file or directory: venv/bin/python

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys; print(sys.version)'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-AkOh87PG' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-gP9p1cD0' (errno=Operation not permitted)
3.9.6 (default, Apr 30 2025, 02:07:18) 
[Clang 17.0.0 (clang-1700.0.13.5)]

codex
There is no local `venv` in this checkout; I’ll test with system `python3` first. If imports are missing, I’ll still be able to compute the pure NumPy fixture/reference path, but not invoke the backend test runner.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import numpy as np\\nfrom fitting import tougaard_background\\nB_coef,C_coef=2866.0,1643.0\\nxa=np.concatenate([np.linspace(740.0,720.1,60),np.linspace(720.0,700.0,400)])\\nya=4000.0+800.0*(xa-700.0)/40.0+6000.0*np.exp(-0.5*((xa-710.9)/1.6)**2)\\nc0=float(ya[-1]); net=ya-c0; w=np.abs(np.gradient(xa)); ref=np.zeros(len(xa)); refu=np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2; ref[i]=float(np.sum(kernel*net[i:]*w[i:])); refu[i]=float(np.sum(kernel*net[i:]))\\nraw0=float(ref[0]); rawu0=float(refu[0]); scale=(float(ya[0])-c0)/ref[0]; scaleu=(float(ya[0])-c0)/refu[0]; ref=c0+ref*scale; refu=c0+refu*scaleu; got=tougaard_background(xa,ya)\\ndef badprod(x,y):\\n    xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float); n=len(xa)\\n    if n<2: return np.zeros_like(ya,dtype=float)\\n    flipped=bool(xa[0]<xa[-1])\\n    if flipped: xa,ya=xa[::-1].copy(),ya[::-1].copy()\\n    c0=float(ya[-1]); net=ya-c0; dx=float(abs(xa[1]-xa[0])); diffs=np.diff(xa); uniform=bool(dx>0.0 and np.max(np.abs(diffs-diffs[0]))<=1e-6*dx)\\n    if uniform:\\n        m=np.arange(n,dtype=float); T=m*dx; k=(B_coef*T)/(C_coef+T*T)**2; bg=np.convolve(net,k[::-1])[n-1:]*dx\\n    else:\\n        bg=np.zeros(n,dtype=float)\\n        for i in range(n):\\n            T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2; bg[i]=float(np.sum(kernel*net[i:]))\\n    out=np.full(n,c0) if bg[0]==0.0 else c0+bg*((float(ya[0])-c0)/bg[0])\\n    return out[::-1] if flipped else out\\nbad=badprod(xa,ya)\\nx=np.linspace(740.0,700.0,300); y=4000.0+6000.0*np.exp(-0.5*((x-710.9)/1.6)**2); xj=x.copy(); xj[1:-1]+=1e-4*np.sin(np.arange(len(x)-2))\\nprint(\"n\",len(xa),\"xa0\",xa[0],\"xa_last\",xa[-1])\\nprint(\"ya0\",ya[0],\"c0\",c0,\"endpoint_delta\",ya[0]-c0)\\nprint(\"raw_ref0_weighted\",raw0,\"raw_ref0_unweighted\",rawu0)\\nprint(\"anchor_scale_weighted\",scale,\"anchor_scale_unweighted\",scaleu)\\nprint(\"guard_margin\",float(np.max(np.abs(ref-refu))))\\nprint(\"got_vs_ref_max\",float(np.max(np.abs(got-ref))),\"allclose\",bool(np.allclose(got,ref,rtol=1e-9)))\\nprint(\"bad_vs_ref_max\",float(np.max(np.abs(bad-ref))),\"allclose\",bool(np.allclose(bad,ref,rtol=1e-9)))\\nprint(\"bad_test_result\", \"PASS\" if (np.max(np.abs(ref-refu))>10.0 and np.allclose(bad,ref,rtol=1e-9)) else \"FAIL\")\\nprint(\"jitter_uniform_nonuniform_max\",float(np.max(np.abs(tougaard_background(x,y)-tougaard_background(xj,y)))))'" in /Users/skyefortier/xps-verify
 exited 1 in 113ms:
Traceback (most recent call last):
  File "<string>", line 2, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

codex
System Python lacks `lmfit`, so importing `fitting.py` fails before `tougaard_background` is available. I’m going to re-run the Tougaard math directly from the reviewed function body, which is enough for the F2 red/green check and the other pure Tougaard assertions; I’ll separately run the JS twin with Node.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import numpy as np\\nB_coef,C_coef=2866.0,1643.0\\ndef tougaard_background(x,y,n_avg=1,unweighted=False):\\n    n=len(x)\\n    if n<2: return np.zeros_like(y,dtype=float)\\n    xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float)\\n    flipped=bool(xa[0]<xa[-1])\\n    if flipped: xa,ya=xa[::-1].copy(),ya[::-1].copy()\\n    c0=float(ya[-1]); net=ya-c0; dx=float(abs(xa[1]-xa[0])); diffs=np.diff(xa); uniform=bool(dx>0.0 and np.max(np.abs(diffs-diffs[0]))<=1e-6*dx)\\n    if uniform:\\n        m=np.arange(n,dtype=float); T=m*dx; k=(B_coef*T)/(C_coef+T*T)**2; bg=np.convolve(net,k[::-1])[n-1:]*dx\\n    else:\\n        w=np.abs(np.gradient(xa)); bg=np.zeros(n,dtype=float)\\n        for i in range(n):\\n            T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2\\n            bg[i]=float(np.sum(kernel*net[i:] if unweighted else kernel*net[i:]*w[i:]))\\n    out=np.full(n,c0) if bg[0]==0.0 else c0+bg*((float(ya[0])-c0)/bg[0])\\n    return out[::-1] if flipped else out\\nxa=np.concatenate([np.linspace(740.0,720.1,60),np.linspace(720.0,700.0,400)])\\nya=4000.0+800.0*(xa-700.0)/40.0+6000.0*np.exp(-0.5*((xa-710.9)/1.6)**2)\\nc0=float(ya[-1]); net=ya-c0; w=np.abs(np.gradient(xa)); ref=np.zeros(len(xa)); refu=np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2; ref[i]=float(np.sum(kernel*net[i:]*w[i:])); refu[i]=float(np.sum(kernel*net[i:]))\\nraw0=float(ref[0]); rawu0=float(refu[0]); scale=(float(ya[0])-c0)/ref[0]; scaleu=(float(ya[0])-c0)/refu[0]; ref=c0+ref*scale; refu=c0+refu*scaleu; got=tougaard_background(xa,ya); bad=tougaard_background(xa,ya,unweighted=True)\\nx=np.linspace(740.0,700.0,300); y=4000.0+6000.0*np.exp(-0.5*((x-710.9)/1.6)**2); xj=x.copy(); xj[1:-1]+=1e-4*np.sin(np.arange(len(x)-2))\\nprint(\"n\",len(xa),\"xa0\",xa[0],\"xa_last\",xa[-1])\\nprint(\"ya0\",ya[0],\"c0\",c0,\"endpoint_delta\",ya[0]-c0)\\nprint(\"raw_ref0_weighted\",raw0,\"raw_ref0_unweighted\",rawu0)\\nprint(\"anchor_scale_weighted\",scale,\"anchor_scale_unweighted\",scaleu)\\nprint(\"guard_margin\",float(np.max(np.abs(ref-refu))))\\nprint(\"got_vs_ref_max\",float(np.max(np.abs(got-ref))),\"allclose\",bool(np.allclose(got,ref,rtol=1e-9)))\\nprint(\"bad_vs_ref_max\",float(np.max(np.abs(bad-ref))),\"allclose\",bool(np.allclose(bad,ref,rtol=1e-9)))\\nprint(\"bad_test_result\", \"PASS\" if (np.max(np.abs(ref-refu))>10.0 and np.allclose(bad,ref,rtol=1e-9)) else \"FAIL\")\\nprint(\"jitter_uniform_nonuniform_max\",float(np.max(np.abs(tougaard_background(x,y)-tougaard_background(xj,y)))))'" in /Users/skyefortier/xps-verify
 succeeded in 122ms:
n 460 xa0 740.0 xa_last 700.0
ya0 4800.0 c0 4000.0000005015495 endpoint_delta 799.9999994984505
raw_ref0_weighted 470.200100113026 raw_ref0_unweighted 7803.418538117508
anchor_scale_weighted 1.7014032946954876 anchor_scale_unweighted 0.10251917100059098
guard_margin 104.82975035097024
got_vs_ref_max 0.0 allclose True
bad_vs_ref_max 104.82975035097024 allclose False
bad_test_result FAIL
jitter_uniform_nonuniform_max 3.637978807091713e-12

exec
/bin/zsh -lc "nl -ba tests/test_tougaard_background.py | sed -n '272,380p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   272	def test_short_input_returns_zeros():
   273	    """< 2 points: no background can be defined; must return zeros."""
   274	    assert np.array_equal(
   275	        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
   276	    )
   277	    assert tougaard_background(np.array([]), np.array([])).size == 0

codex
The numeric recheck matches the commit message: endpoint delta is about 800 counts, weighted vs unweighted anchored outputs diverge by about 104.83 counts, and the simulated F2 revert fails the test’s `allclose`. I’m now sweeping the rest of the Python assertions with the same implementation and running the six JS twin tests from the checked-in HTML extraction.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import numpy as np\\nB_coef,C_coef=2866.0,1643.0\\ndef tb(x,y):\\n    n=len(x)\\n    if n<2: return np.zeros_like(y,dtype=float)\\n    xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float); flipped=bool(xa[0]<xa[-1])\\n    if flipped: xa,ya=xa[::-1].copy(),ya[::-1].copy()\\n    c0=float(ya[-1]); net=ya-c0; dx=float(abs(xa[1]-xa[0])); diffs=np.diff(xa); uniform=bool(dx>0.0 and np.max(np.abs(diffs-diffs[0]))<=1e-6*dx)\\n    if uniform:\\n        m=np.arange(n,dtype=float); T=m*dx; k=(B_coef*T)/(C_coef+T*T)**2; bg=np.convolve(net,k[::-1])[n-1:]*dx\\n    else:\\n        w=np.abs(np.gradient(xa)); bg=np.zeros(n)\\n        for i in range(n):\\n            T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2; bg[i]=float(np.sum(kernel*net[i:]*w[i:]))\\n    out=np.full(n,c0) if bg[0]==0.0 else c0+bg*((float(ya[0])-c0)/bg[0])\\n    return out[::-1] if flipped else out\\ndef synth(desc=True):\\n    x=np.linspace(295.0,280.0,151); y=100.0+5000.0*np.exp(-0.5*((x-287.0)/0.8)**2)+400.0/(1.0+np.exp(-(287.0-x)))\\n    return (x,y) if desc else (x[::-1].copy(),y[::-1].copy())\\n# 1 kernel peak\\nx=np.linspace(100.0,0.0,1001); y=np.full_like(x,1e-9); y[0]=2e-9; spike_idx=800; y[spike_idx]=1e6; bg=tb(x,y); peak_x=x[:spike_idx][np.argmax(bg[:spike_idx])]; assert abs(peak_x-(20.0+np.sqrt(1643.0/3.0)))<=0.25, peak_x\\n# 2 ascending/descending\\nxd,yd=synth(True); xa,ya=synth(False); assert np.array_equal(tb(xd,yd),tb(xa,ya)[::-1])\\n# 3 ascending/descending nonuniform\\nsteps=0.08+0.04*np.sin(np.arange(120)); xd=295.0-np.concatenate(([0.0],np.cumsum(steps))); yd=100.0+4000.0*np.exp(-0.5*((xd-290.0)/1.0)**2); assert np.array_equal(tb(xd,yd),tb(xd[::-1].copy(),yd[::-1].copy())[::-1])\\n# 4 anchors\\nx,y=synth(True); bg=tb(x,y); assert np.isclose(bg[0],y[0],rtol=1e-12); assert np.isclose(bg[-1],y[-1],rtol=1e-12); assert np.all(np.isfinite(bg)); assert np.all(bg>=0.0); bga=tb(x[::-1].copy(),y[::-1].copy()); assert np.isclose(bga[-1],y[0],rtol=1e-12); assert np.isclose(bga[0],y[-1],rtol=1e-12)\\n# 5 no loss signal\\nx=np.array([291.0,290.0,289.0,288.0]); y=np.array([100.0,0.0,0.0,0.0]); assert np.array_equal(tb(x,y),np.zeros(4))\\n# 6 flat window\\nx=np.linspace(740.0,700.0,200); y=np.full_like(x,500.0); bg=tb(x,y); assert np.max(np.abs(y-bg))<1e-6\\n# 7 wide region\\nx=np.linspace(740.0,700.0,600); pk=6000.0*np.exp(-0.5*((x-710.9)/1.6)**2)+3000.0*np.exp(-0.5*((x-724.5)/1.9)**2); baseline=4000.0+3000.0*np.cumsum(pk[::-1])[::-1]/np.sum(pk); y=pk+baseline; bg=tb(x,y); assert np.isclose(bg[-1],y[-1],rtol=1e-12); assert np.isclose(bg[0],y[0],rtol=1e-12)\\n# 8 nonuniform weighted pin including guard\\nx=np.linspace(740.0,700.0,300); y=4000.0+6000.0*np.exp(-0.5*((x-710.9)/1.6)**2); xj=x.copy(); xj[1:-1]+=1e-4*np.sin(np.arange(len(x)-2)); assert np.max(np.abs(tb(x,y)-tb(xj,y)))<1e-1\\nxa=np.concatenate([np.linspace(740.0,720.1,60),np.linspace(720.0,700.0,400)]); ya=4000.0+800.0*(xa-700.0)/40.0+6000.0*np.exp(-0.5*((xa-710.9)/1.6)**2); got=tb(xa,ya); c0=float(ya[-1]); net=ya-c0; w=np.abs(np.gradient(xa)); ref=np.zeros(len(xa)); refu=np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2; ref[i]=float(np.sum(kernel*net[i:]*w[i:])); refu[i]=float(np.sum(kernel*net[i:]))\\nref=c0+ref*((float(ya[0])-c0)/ref[0]); refu=c0+refu*((float(ya[0])-c0)/refu[0]); assert np.max(np.abs(ref-refu))>10.0; assert np.allclose(got,ref,rtol=1e-9)\\n# 9 short input\\nassert np.array_equal(tb(np.array([284.8]),np.array([123.0])),np.array([0.0])); assert tb(np.array([]),np.array([])).size==0\\nprint(\"pure Tougaard assertion sweep passed: 9/9\")'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'node --test tests/js/tougaard_twin.test.js' in /Users/skyefortier/xps-verify
 succeeded in 133ms:
pure Tougaard assertion sweep passed: 9/9

 succeeded in 150ms:
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 1 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 13.094776
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 2 - ascending and descending BE input give the identical background
  ---
  duration_ms: 0.648201
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 3 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.359284
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 4 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 2.665686
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 5 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 1.800991
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 6 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 0.676734
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
# duration_ms 103.727946

codex
The JS twin passes all 6 tests. Python’s actual `pytest` cannot run here because neither `pytest` nor `lmfit` is installed, but the pure Tougaard assertion sweep passes all 9 test scenarios against the same function logic, including the changed pin.
exec
/bin/zsh -lc "rg -n \"negative|clamp|signed|C0|flat pre-loss|phantom|endpoint|allclose|array_equal|isclose|max\\(np\\.abs|strictEqual|ok\\(\" tests/test_tougaard_background.py tests/js/tougaard_twin.test.js fitting.py templates/index.html -S" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/js/tougaard_twin.test.js:13://      (the old "trailing endpoint" rescale was degenerate: K(0)=0 forced
tests/js/tougaard_twin.test.js:24:assert.ok(match, 'tougaardBackground not found in templates/index.html');
tests/js/tougaard_twin.test.js:28:assert.ok(avgMatch, '_applyEndpointAveraging not found in templates/index.html');
tests/js/tougaard_twin.test.js:69:  assert.ok(Math.abs(maxX - expected) <= 0.25,
tests/js/tougaard_twin.test.js:80:    assert.strictEqual(bgDesc[i], bgAsc[i],
tests/js/tougaard_twin.test.js:85:test('background meets the data at BOTH edges (high-BE anchor, low-BE C0)', () => {
tests/js/tougaard_twin.test.js:89:  assert.ok(rel < 1e-12,
tests/js/tougaard_twin.test.js:92:  // constant C0, NOT zero. K(0)=0 still kills the LOSS integral there, so the
tests/js/tougaard_twin.test.js:93:  // background equals C0 exactly. Asserting 0 pinned the bug: it forced the
tests/js/tougaard_twin.test.js:97:  assert.ok(relLow < 1e-12,
tests/js/tougaard_twin.test.js:98:    `low-BE edge should sit on C0 = ${intensity[last]}, got ${bg[last]}`);
tests/js/tougaard_twin.test.js:101:test('flat window yields no phantom signal (F1 regression pin)', () => {
tests/js/tougaard_twin.test.js:106:    assert.ok(Math.abs(intensity[i] - bg[i]) < 1e-6,
tests/js/tougaard_twin.test.js:113:  // F1 (pre-loss constant C0) + F2 (local quadrature weights) fixes:
tests/js/tougaard_twin.test.js:138:    assert.ok(Math.abs(got - want) <= tol,
tests/js/tougaard_twin.test.js:145:// while every backend caller applies endpoint averaging first. With the
tests/js/tougaard_twin.test.js:149:// tougaard_background(x, _apply_endpoint_averaging(y, n))).
tests/js/tougaard_twin.test.js:150:test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
tests/js/tougaard_twin.test.js:152:  assert.ok(coreMatch, 'computeBackgroundCore not found in templates/index.html');
tests/js/tougaard_twin.test.js:176:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/js/tougaard_twin.test.js:181:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/js/tougaard_twin.test.js:187:      assert.strictEqual(out[i], expected[i],
tests/js/tougaard_twin.test.js:188:        `${label} branch: caller bypasses endpoint averaging at index ${i}: ` +
fitting.py:17:  linear          – straight‑line between endpoints
fitting.py:130:    # dx = center − x  →  positive on LOW-BE side, negative on HIGH-BE side.
fitting.py:139:    # dx = center - x: negative on the HIGH-BE side (x > center).
fitting.py:196:    #     phase → πα/2 − (1−α)·π/2 → −π(1−2α)/2  (negative for α < 0.5)
fitting.py:223:            peak_val = np.max(np.abs(ds_core))
fitting.py:292:        peak_val = np.max(np.abs(result))
fitting.py:322:    B_low  = y(E_min),  B_high = y(E_max)  (the endpoint levels).
fitting.py:351:        if np.max(np.abs(B - B_prev)) < tol:
fitting.py:363:    """Smart (constrained Shirley): standard Shirley clamped to never exceed data."""
fitting.py:385:    not as a post-hoc clamp.  Where the background would exceed the data it
fitting.py:401:    b_low = float(np.mean(ys[:cap]))      # low-BE endpoint
fitting.py:402:    b_high = float(np.mean(ys[-cap:]))     # high-BE endpoint
fitting.py:425:        if np.max(np.abs(B - B_prev)) < tol:
fitting.py:428:    B = np.minimum(B, ys)  # final safety clamp
fitting.py:432:def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
fitting.py:455:    1. Average *n_avg* points at each endpoint.
fitting.py:456:    2. Compute a linear baseline between the averaged endpoints.
fitting.py:459:       flattened data, scaled by the endpoint step height.
fitting.py:476:    IL = float(np.mean(ys[:cap]))      # low‑BE endpoint
fitting.py:477:    IH = float(np.mean(ys[-cap:]))     # high‑BE endpoint
fitting.py:501:        if np.max(np.abs(B - B_prev)) < tol:
fitting.py:531:    window produced a full-amplitude phantom "signal".
fitting.py:533:    So the low-BE edge level is taken as a constant offset C0 (the
fitting.py:535:    net (J - C0), and the amplitude is then anchored so the background
fitting.py:541:    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
fitting.py:542:    levels are read, so neither C0 nor the high-BE anchor rests on a single
fitting.py:543:    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
fitting.py:544:    endpoints = previous behaviour.
fitting.py:566:        ya = _apply_endpoint_averaging(ya, n_avg)
fitting.py:578:    # C0: the low-BE edge level = index -1 on the descending working array.
fitting.py:602:    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)
fitting.py:620:    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
fitting.py:622:    # flat or empty window), the honest background is the flat pre-loss level
fitting.py:623:    # C0 itself, NOT zeros: a featureless window contains no loss signal to
fitting.py:626:    # input) pass through signed; no clamping policy is imposed here.
fitting.py:945:    endpoint_avg: int = 1,
fitting.py:1010:    # compute them on [i0:i1] and flat-hold the endpoint value across
fitting.py:1030:        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1032:        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1034:        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1036:        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1038:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1055:        # array; flat-hold the endpoint value outside [i0, i1]. In the
fitting.py:1260:    endpoint_avg: int = 1,
fitting.py:1268:        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
fitting.py:1270:        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
fitting.py:1272:        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
fitting.py:1274:        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
fitting.py:1276:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
tests/test_tougaard_background.py:22:3. The trailing-endpoint rescale was degenerate: K(0) = 0 makes the
tests/test_tougaard_background.py:24:   fired and the "match the trailing endpoint" scale was in fact
tests/test_tougaard_background.py:95:    assert np.array_equal(bg_d, bg_a[::-1]), (
tests/test_tougaard_background.py:96:        f"order-dependent output: max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
tests/test_tougaard_background.py:111:    assert np.array_equal(bg_d, bg_a[::-1]), (
tests/test_tougaard_background.py:113:        f"max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
tests/test_tougaard_background.py:126:    assert np.isclose(bg[0], y[0], rtol=1e-12), (
tests/test_tougaard_background.py:130:    # pre-loss constant C0 (the out-of-window baseline), NOT zero. K(0) = 0
tests/test_tougaard_background.py:131:    # still makes the LOSS integral vanish there, so the background equals C0
tests/test_tougaard_background.py:136:    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
tests/test_tougaard_background.py:137:        f"low-BE edge should sit on the pre-loss level C0 = {y[-1]}, got {bg[-1]}"
tests/test_tougaard_background.py:144:    assert np.isclose(bg_a[-1], y[0], rtol=1e-12)
tests/test_tougaard_background.py:145:    # ...and the low-BE edge (index 0 when ascending) sits on C0, per above.
tests/test_tougaard_background.py:146:    assert np.isclose(bg_a[0], y[-1], rtol=1e-12)
tests/test_tougaard_background.py:157:    pre-loss level C0, not zero. Returning zeros would report the entire
tests/test_tougaard_background.py:160:    only its fallback VALUE changed from 0 to C0. Mirrored in the JS twin."""
tests/test_tougaard_background.py:164:    assert np.array_equal(bg, np.zeros(4)), (
tests/test_tougaard_background.py:165:        f"C0 is 0.0 here (low-BE edge counts are zero), so the flat pre-loss "
tests/test_tougaard_background.py:170:def test_flat_window_yields_no_phantom_signal():
tests/test_tougaard_background.py:176:    background ramping 0 -> 500 and reported up to 500 counts of phantom
tests/test_tougaard_background.py:182:    assert np.max(np.abs(net)) < 1e-6, (
tests/test_tougaard_background.py:199:    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
tests/test_tougaard_background.py:203:    assert np.isclose(bg[0], y[0], rtol=1e-12)
tests/test_tougaard_background.py:224:    assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
tests/test_tougaard_background.py:229:    # A high-BE endpoint RISE (not just a symmetric peak on a flat baseline)
tests/test_tougaard_background.py:237:    # guard F2). The endpoint delta below (~800 counts) keeps the anchored
tests/test_tougaard_background.py:263:    assert np.max(np.abs(ref - ref_unweighted)) > 10.0, (
tests/test_tougaard_background.py:265:        "endpoint delta too small to survive the F1 anchor, pin is dead"
tests/test_tougaard_background.py:267:    assert np.allclose(got, ref, rtol=1e-9), (
tests/test_tougaard_background.py:274:    assert np.array_equal(
templates/index.html:1986:                <option value="linear" data-tip="Simple straight line between endpoints. Use for spectra with minimal background variation or when Shirley is inappropriate.">Linear</option>
templates/index.html:1987:                <option value="shirley_linear" data-tip="Hybrid: a linear baseline between endpoints, plus a Shirley-like cumulative correction on top. Combines slope tracking with inelastic-scattering step.">Shirley + Linear</option>
templates/index.html:2018:                <input type="number" id="shirley-iter" value="5" min="1" max="50" step="1" oninput="_clampShirleyIter(); _invalidateBgCache(); updatePlot()" title="Number of iterations for the Shirley background calculation. The algorithm converges quickly — most of the change happens between 1 and 5 iterations. Values above 10 rarely produce visible differences. Default: 5.">
templates/index.html:2022:                <input type="number" id="bg-endpoint-avg" value="1" min="1" max="50" step="1" oninput="_invalidateBgCache(); updatePlot()" title="Number of points to average at each endpoint for smoother background anchoring">
templates/index.html:2708:// Colors assigned to elements for markers
templates/index.html:3020:        shirleyIter: '5', endpointAvg: '1',
templates/index.html:3054:            endpointAvg: '1', roiMin: '', roiMax: '',
templates/index.html:3656:      endpointAvg: document.getElementById('bg-endpoint-avg')?.value || '1',
templates/index.html:3675:    set('bg-endpoint-avg', ui.endpointAvg || '1');
templates/index.html:3703:      const epAvg = document.getElementById('bg-endpoint-avg');
templates/index.html:3843:  const dx = center - x;   // negative on HIGH-BE side (x > center)
templates/index.html:4044:  // Smart (constrained Shirley): standard Shirley clamped to never exceed data.
templates/index.html:4054:// a post-hoc clamp.  Where the background would exceed the data, it locks to
templates/index.html:4061:  // Averaged endpoints
templates/index.html:4066:  const I0 = sL / cap;   // left endpoint (index 0, typically high-BE)
templates/index.html:4067:  const I1 = sR / cap;   // right endpoint (index n-1, typically low-BE)
templates/index.html:4115:  // Final clamp to data (safety)
templates/index.html:4147:  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
templates/index.html:4153:  // the background dove to ~0 there and a flat window produced phantom
templates/index.html:4180:  // the flat pre-loss level C0 itself, NOT zeros; zeros would report the
templates/index.html:4182:  // (physically invalid input) pass through signed; no clamping here.
templates/index.html:4193:// Apply endpoint averaging: replace first/last N points with their mean so
templates/index.html:4194:// existing Shirley/Smart functions pick up averaged endpoint intensities.
templates/index.html:4216:  // 1. Averaged endpoints
templates/index.html:4221:  const IL = sL / cap;   // left (high-BE) endpoint
templates/index.html:4222:  const IR = sR / cap;   // right (low-BE) endpoint
templates/index.html:4224:  // 2. Linear baseline between averaged endpoints
templates/index.html:4232:  //    Step height = |IL - IR| (the endpoint difference drives the Shirley step).
templates/index.html:4234:  if (stepH < 1e-12) return linear;   // endpoints equal → pure linear
templates/index.html:4260:  // 5. Combine: linear baseline + Shirley correction, clamped to data
templates/index.html:4278:function _clampShirleyIter() {
templates/index.html:4288:// endpointAvg) instead of reading from DOM. Used by stack-view render
templates/index.html:4295:  const nAvg = parseInt(settings.endpointAvg) || 1;
templates/index.html:4300:  // Get background endpoint range from settings
templates/index.html:4322:    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
templates/index.html:4334:  // Compute background on the sliced region — apply endpoint averaging for Shirley types
templates/index.html:4342:  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
templates/index.html:4370:    endpointAvg: document.getElementById('bg-endpoint-avg').value,
templates/index.html:4612:    // Background endpoints
templates/index.html:6114:    // obvious — matches the shirley-iter / bg-endpoint-avg pattern.
templates/index.html:6660:    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
templates/index.html:6675:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvg };
templates/index.html:6782:    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
templates/index.html:6783:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvgVal };
templates/index.html:7373:    endpointAvg: (srcUi && srcUi.endpointAvg) || '1',
templates/index.html:7715:  // wheel handler's first event computes null * zoomFactor = 0, clamping
templates/index.html:7942:  // Percentage residuals: ((data - fit) / data) × 100, clamped to ±100%
templates/index.html:8200:  // behind all data series. Helps users orient since negative values
templates/index.html:8201:  // can appear from background-subtraction noise at endpoints.
templates/index.html:8340:    // 5% padding below data minimum, clamped at 0
templates/index.html:9069:              endpointAvg: '1', roiMin: '', roiMax: '',
templates/index.html:10598:  // colorIdx is assigned per-pick via RefCore.nextColorIdx (residue-aware), so no
templates/index.html:10847:      else { _refError = j || { error: 'reference endpoint failed' }; }
templates/index.html:10851:                     if (_refPanelOpen) _refApplyPaletteGeometry();   // re-clamp once content fills the panel (A5)
templates/index.html:10876:  return RefCore.clampToViewport(left, top, w, h, window.innerWidth, window.innerHeight, 8);
templates/index.html:10896:// Apply persisted collapse + position (clamped). Stale/offscreen/bad positions
templates/index.html:10897:// clamp safely; on mobile the bottom-sheet CSS owns geometry so inline pos clears.
templates/index.html:10940:// Re-clamp an open palette when the viewport changes (prevents offscreen drift).
templates/index.html:11045:// position:fixed portal escapes overflow:hidden; clamp to the viewport.
templates/index.html:11736:  // `new Chart()` constructor's initial render `state.chart` is not yet assigned,
templates/index.html:11959:// markup, anchored at the click pixel, viewport-clamped, ABOVE the palette
templates/index.html:11981:  // Anchor at the click pixel (viewport coords), clamped on-screen.
templates/index.html:12250:    return 'peak id ' + JSON.stringify(p.id) + ' is not a non-negative integer';
templates/index.html:12386:  // Grey out endpoint avg for types it can't affect. Tougaard keeps it:
templates/index.html:12390:  const epAvg = document.getElementById('bg-endpoint-avg');
templates/index.html:12429:  // ROI endpoints so that existing peaks stay visible while the user
templates/index.html:13331:  const unassignedPeaks = (body.peaks || []).filter(p => p.region === 'unassigned');
templates/index.html:13332:  if (unassignedPeaks.length) {
templates/index.html:13333:    const centers = unassignedPeaks.map(p => (+p.center).toFixed(2)).join(', ');
templates/index.html:13334:    parts.push(`Found ${unassignedPeaks.length} extra peak(s) at ${centers} eV ` +
templates/index.html:13448:// (static/js/ref_identify_core.js RefCore.clampToViewport is the shared,
templates/index.html:13449:// tested clamp math) — but scoped to ONLY the Find Peaks modal: every
templates/index.html:13465:  return RefCore.clampToViewport(left, top, w, h, window.innerWidth, window.innerHeight, 8);
templates/index.html:13498:// Re-clamp an open, already-dragged modal when the viewport changes

exec
/bin/zsh -lc "git show --unified=20 3d9ff54 -- fitting.py | sed -n '1,220p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-M57FHwgI' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-j6mf1Zdx' (errno=Operation not permitted)
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

diff --git a/fitting.py b/fitting.py
index ee26392..ae08d1e 100644
--- a/fitting.py
+++ b/fitting.py
@@ -488,128 +488,164 @@ def shirley_linear_background(
 
     B = np.zeros(n)
     for _ in range(n_iter):
         B_prev = B.copy()
         signal = np.maximum(flat - B, 0.0)
         # O(n) cumulative integral from high-x end back to each point
         cum_right = np.zeros(n)
         for i in range(n - 2, -1, -1):
             cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
         total = cum_right[0]
         if total <= 0.0:
             break
         B = step_h * cum_right / total
         if np.max(np.abs(B - B_prev)) < tol:
             break
 
     result = np.minimum(linear + B, ys)
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
         return np.zeros_like(y, dtype=float)
 
     # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
     # C = 1643 eV². A long-standing transcription slip shipped C = 1643²
     # (~2.7e6 eV²), which pushed the kernel maximum from ~23 eV to ~949 eV
     # of energy loss and flattened the background to ~zero over any real
     # XPS window. Fixed 2026-07-04 together with the JS twin.
     B_coef, C_coef = 2866.0, 1643.0
 
     xa = np.asarray(x, dtype=float)
     ya = np.asarray(y, dtype=float)
+    if n_avg > 1:
+        ya = _apply_endpoint_averaging(ya, n_avg)
 
     # The one-sided loss sum below (j >= i) is physical only when BE
     # DESCENDS along the array: the loss contributions at x[i] must come
     # from lower-BE (higher-KE) emitters, which sit at higher indices only
     # on a descending grid. Normalize to descending internally and flip
     # the result back — the mirror of shirley_background's ascending
     # normalization — so both BE orderings give identical output.
     flipped = bool(xa[0] < xa[-1])
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
 
     if uniform:
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

exec
/bin/zsh -lc 'git show --name-status --format=short 173f002' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-TYorFFhG' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HwRgFaN9' (errno=Operation not permitted)
commit 173f0025cb843948111fa8e880b6bef053949ca5
Author: Skye Fortier <skyefortier@gmail.com>

    fix(tests): test_nonuniform_grid_uses_local_quadrature_weights didn't guard F2

M	tests/test_tougaard_background.py

exec
/bin/zsh -lc 'git diff --name-status 173f002''^ 173f002 && git diff --exit-code --quiet 173f002''^ 173f002 -- fitting.py templates/index.html tests/js/tougaard_twin.test.js autofit/engine.py autofit/methods app.py && echo scoped_paths_zero_diff' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gBh8qCO2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XkejjEMx' (errno=Operation not permitted)
M	tests/test_tougaard_background.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-R9BhT2aO' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-aVGAYDoS' (errno=Operation not permitted)
scoped_paths_zero_diff

codex
I’m doing the last review pass now: checking whether the other Tougaard regression pins would still fire under their corresponding historical failures, and whether any assertion is silently neutralized by its fixture. So far the only deliberately weak-looking fixture is the zero-C0 degenerate guard, but the same F1 behavior is also covered by nonzero-C0 flat and wide-region tests.
exec
/bin/zsh -lc 'rg -n -i "tougaard|background" docs/autofit/inventory/reference_fits_inventory.json docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json docs/autofit/test_data/Ugly_Fe_2p.spec.json docs/autofit/test_data/Ugly_Fe_2p_2.spec.json docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json tests/autofit/fixtures/*.json tests/fixtures/*.json' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:342:  "background": {
docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json:1062:  "background": [
docs/autofit/test_data/Ugly_Fe_2p.spec.json:1229:  "background": [
docs/autofit/test_data/Ugly_Fe_2p_2.spec.json:1229:  "background": [
docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json:1254:  "background": [

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import numpy as np\\ndef tb(x,y,C=1643.0,force_desc=True,old_f1=False):\\n    B=2866.0; n=len(x)\\n    if n<2: return np.zeros_like(y,dtype=float)\\n    xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float); flipped=False\\n    if force_desc:\\n        flipped=bool(xa[0]<xa[-1])\\n        if flipped: xa,ya=xa[::-1].copy(),ya[::-1].copy()\\n    dx=float(abs(xa[1]-xa[0])); diffs=np.diff(xa); uniform=bool(dx>0.0 and np.max(np.abs(diffs-diffs[0]))<=1e-6*dx)\\n    if old_f1:\\n        net=ya; c0=0.0\\n    else:\\n        c0=float(ya[-1]); net=ya-c0\\n    if uniform:\\n        m=np.arange(n,dtype=float); T=m*dx; k=(B*T)/(C+T*T)**2; bg=np.convolve(net,k[::-1])[n-1:]*dx\\n    else:\\n        w=np.abs(np.gradient(xa)); bg=np.zeros(n)\\n        for i in range(n):\\n            T=np.abs(xa[i:]-xa[i]); kernel=(B*T)/(C+T*T)**2; bg[i]=float(np.sum(kernel*net[i:]*w[i:]))\\n    if old_f1:\\n        out=bg*float(ya[0]) if bg[0]==0.0 else bg*(float(ya[0])/bg[0])\\n    else:\\n        out=np.full(n,c0) if bg[0]==0.0 else c0+bg*((float(ya[0])-c0)/bg[0])\\n    return out[::-1] if (force_desc and flipped) else out\\n# C-squared pin\\nx=np.linspace(100.0,0.0,1001); y=np.full_like(x,1e-9); y[0]=2e-9; y[800]=1e6\\nfor C in (1643.0,1643.0**2):\\n    bg=tb(x,y,C=C); peak_x=x[:800][np.argmax(bg[:800])]; print(\"C\",C,\"peak_x\",peak_x,\"passes\",abs(peak_x-(20+np.sqrt(1643.0/3.0)))<=0.25)\\n# order pin under no normalization\\nxd=np.linspace(295.0,280.0,151); yd=100.0+5000.0*np.exp(-0.5*((xd-287.0)/0.8)**2)+400.0/(1.0+np.exp(-(287.0-xd)))\\nprint(\"ascending_without_normalization_maxdiff\",float(np.max(np.abs(tb(xd,yd)-tb(xd[::-1].copy(),yd[::-1].copy(),force_desc=False)[::-1]))))\\n# F1 old behavior against nonzero C0 pins\\nxflat=np.linspace(740.0,700.0,200); yflat=np.full_like(xflat,500.0); print(\"old_f1_flat_net_max\",float(np.max(np.abs(yflat-tb(xflat,yflat,old_f1=True)))))\\nxw=np.linspace(740.0,700.0,600); pk=6000.0*np.exp(-0.5*((xw-710.9)/1.6)**2)+3000.0*np.exp(-0.5*((xw-724.5)/1.9)**2); baseline=4000.0+3000.0*np.cumsum(pk[::-1])[::-1]/np.sum(pk); yw=pk+baseline; bgold=tb(xw,yw,old_f1=True); print(\"old_f1_wide_low_edge\",bgold[-1],\"want\",yw[-1],\"diff\",bgold[-1]-yw[-1])\\n# negative scale scenario\\nxn=np.linspace(295.0,280.0,151); yn=500.0-400.0*(xn-280.0)/15.0; bg=tb(xn,yn); print(\"negative_scale_endpoint_delta\",yn[0]-yn[-1],\"bg_edges\",bg[0],bg[-1],\"minmax\",float(bg.min()),float(bg.max()))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "git show --name-only --format='' 173f002 | sort && git diff --exit-code --quiet 173f002"'^ 173f002 -- fitting.py templates/index.html tests/js/tougaard_twin.test.js autofit/engine.py autofit/methods app.py; echo exit:$?' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-e02YIcxt' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hfjAJTmg' (errno=Operation not permitted)
tests/test_tougaard_background.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XL2tlvdP' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jpdDrSdO' (errno=Operation not permitted)
exit:0

 succeeded in 149ms:
C 1643.0 peak_x 43.4 passes True
C 2699449.0 peak_x 100.0 passes False
ascending_without_normalization_maxdiff 362.35456069651923
old_f1_flat_net_max 500.0
old_f1_wide_low_edge 0.0 want 4000.0000005041693 diff -4000.0000005041693
negative_scale_endpoint_delta -400.0 bg_edges 100.0 500.0 minmax 100.0 500.0

codex
1. No BLOCKER/MAJOR/MINOR findings.

Recheck evidence:
- New fixture endpoint delta: `ya[0] - ya[-1] = 799.9999995`, so the F1 anchor is non-degenerate.
- Guard margin: weighted vs unweighted anchored refs diverge by `104.82975` counts; `>10` is a reasonable guard, not close to the threshold.
- Simulated F2 revert: unweighted production path differs from ref by `104.82975` and fails `np.allclose(..., rtol=1e-9)`.
- Scope: `173f002` changes only `tests/test_tougaard_background.py`; `fitting.py`, `templates/index.html`, JS twin, `autofit/engine.py`, `autofit/methods/*`, and `app.py` are zero-diff.
- JS twin: `node --test tests/js/tougaard_twin.test.js` passes 6/6.
- Python pytest could not run in this sandbox because `pytest` and `lmfit` are not installed; I re-verified all 9 Tougaard test scenarios with the reviewed function logic, and they pass.
- Fixture/inventory search found no Tougaard saved-output pins; saved background arrays inspected are `shirley`/`smart`, not Tougaard.
- Negative-scale anchoring is pre-existing production behavior in this scope and explicitly documented as signed/unclamped in `fitting.py` and the JS twin.

VERDICT: GO
tokens used
112,123
1. No BLOCKER/MAJOR/MINOR findings.

Recheck evidence:
- New fixture endpoint delta: `ya[0] - ya[-1] = 799.9999995`, so the F1 anchor is non-degenerate.
- Guard margin: weighted vs unweighted anchored refs diverge by `104.82975` counts; `>10` is a reasonable guard, not close to the threshold.
- Simulated F2 revert: unweighted production path differs from ref by `104.82975` and fails `np.allclose(..., rtol=1e-9)`.
- Scope: `173f002` changes only `tests/test_tougaard_background.py`; `fitting.py`, `templates/index.html`, JS twin, `autofit/engine.py`, `autofit/methods/*`, and `app.py` are zero-diff.
- JS twin: `node --test tests/js/tougaard_twin.test.js` passes 6/6.
- Python pytest could not run in this sandbox because `pytest` and `lmfit` are not installed; I re-verified all 9 Tougaard test scenarios with the reviewed function logic, and they pass.
- Fixture/inventory search found no Tougaard saved-output pins; saved background arrays inspected are `shirley`/`smart`, not Tougaard.
- Negative-scale anchoring is pre-existing production behavior in this scope and explicitly documented as signed/unclamped in `fitting.py` and the JS twin.

VERDICT: GO
