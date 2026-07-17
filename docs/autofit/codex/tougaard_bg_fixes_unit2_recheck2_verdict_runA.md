OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f7267-b736-7401-bea7-7f36b19d3e6c
--------
user
You are an adversarial reviewer for a scoped follow-up commit in this repo
(XPS peak-fitting web app), branch feature-autofit-stage2. Review commit
3cd6aad ("fix(fitting): unify remaining shirley/smart/tougaard call sites
onto n_avg (F3 cont.)") — `git show 3cd6aad` gives the full diff.

CONTEXT: commit c5a24ac ("feat(fitting): unify n_avg convention across
background functions") was reviewed and BOTH runs returned NO-GO with the
same MAJOR finding: smart_background(x, y, n_avg=N) clamps against raw y
via `np.minimum(shir, y)`, but fitting.py's run_fit / compute_background_only
and autofit/parity.py's mirror still called
`smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))` — the OLD
external-pre-averaging convention — so the clamp landed against the
AVERAGED copy instead. Once endpoint_avg > 1, the manual /api/fit path and
the new engine.py Find-Peaks path (which passes n_avg directly) produced
DIFFERENT smart backgrounds — defeating the entire point of the n_avg
unification effort (F3): Find Peaks and manual Run Fit must agree once
both pass the same endpoint_avg.

THE FIX in 3cd6aad: migrated the 6 remaining call sites (3 in run_fit, 3
in compute_background_only, mirrored 3 in autofit/parity.py) for
shirley_background/smart_background/tougaard_background from external
pre-averaging to the same direct n_avg convention already used by
smart_experimental_background/shirley_linear_background at those same
call sites. Removed autofit/parity.py's now-dead
_apply_endpoint_averaging import.

CONSEQUENCE: one real saved-fit fixture record changed.
tests/autofit/fixtures/u4f_battery_expected.json was regenerated via its
committed generator (scripts/gen_u4f_battery_fixture.py) because "U4f
Scan" in docs/autofit/test_data/4-GTA UCl4-BN.proj.zip uses smart
background with endpointAvg=6 — exactly the combination this bug
affects. Its reduced_chi_square moved from 11.399835330377146 to
11.281303682238963 (~1.04% improvement). This was surfaced to and
explicitly approved by the human maintainer before implementing (not a
unilateral call) — your job is to verify the TECHNICAL claims around it,
not to re-litigate whether asking was appropriate.

YOUR JOB — verify each claim, don't accept any of them on the commit
message's word alone:

1. MATHEMATICAL INVARIANCE CLAIM. The commit claims shirley_background and
   tougaard_background are mathematically INVARIANT to which convention is
   used (pre-average externally then call with n_avg=1, vs. call with the
   raw array and n_avg=N directly) — because neither function keeps a
   second reference to "the true raw array" after reading n_avg; the
   entire rest of each function only touches the (possibly-averaged)
   array it was handed. Prove or disprove this by tracing both functions'
   bodies line by line. Then verify smart_background is NOT invariant,
   specifically because of its `return np.minimum(shir, y)` step, which DOES
   retain a second reference to whatever `y` it was given.
2. FIXTURE SCOPE CLAIM. Independently re-derive: scan every *.proj.zip
   under docs/autofit/test_data/ for any spectrum using smart background
   with endpoint_avg (aka endpointAvg) > 1. The claim is there are exactly
   3 such spectra total in the whole corpus, 2 of which
   (scripts/gen_u4f_battery_fixture.py's own skip logic) are excluded from
   the frozen fixture for an unrelated pre-existing reason ("fit-time grid
   drifted from current ui state"), leaving exactly 1 fixture record
   ("U4f Scan" in 4-GTA UCl4-BN.proj.zip) that could possibly have
   changed. Verify this count and the skip reasons yourself.
3. FIXTURE DIFF CLAIM. `git show 3cd6aad^:tests/autofit/fixtures/u4f_battery_expected.json`
   gives the pre-commit fixture; diff it against the current file. Confirm
   ONLY the "U4f Scan" / "4-GTA UCl4-BN.proj.zip" record differs by more
   than 1e-6 relative in reduced_chi_square (or any other field) — every
   other record's diff, if any, should be attributable to ordinary lmfit
   refit floating-point noise (sub-1e-6 relative), not this change.
4. UNUSED IMPORT CLAIM. Confirm autofit/parity.py's removed
   _apply_endpoint_averaging import was genuinely dead after this commit's
   edits (grep the file for any remaining reference).
5. Re-verify the parametrized test added
   (test_compute_background_only_matches_direct_call_with_n_avg in
   tests/test_background_n_avg.py): does it discriminate correctly —
   would it have failed for "smart" on the PRE-3cd6aad code (i.e. before
   this fix, when compute_background_only still used external
   pre-averaging for smart)? Would it have already passed for
   "shirley"/"tougaard" even before this fix (consistent with claim #1)?
6. General adversarial sweep of `git show 3cd6aad`: any other regression,
   scope creep, or unrelated change smuggled in? Confirm scope is
   contained to fitting.py, autofit/parity.py, the one test file, and the
   one fixture file — zero diff in templates/index.html, app.py,
   autofit/engine.py, autofit/methods/*.py, or peak lineshapes.

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll review this as a code-review pass, starting from the commit diff and then independently checking the math paths and fixture corpus. I’m constrained to read-only access, which is enough for this review.
exec
/bin/zsh -lc 'git status --short' in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'git show --find-renames --find-copies --stat --patch 3cd6aad -- fitting.py autofit/parity.py tests/test_background_n_avg.py tests/autofit/fixtures/u4f_battery_expected.json' in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'git show --stat --oneline --decorate --name-only 3cd6aad' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vbe6Io8w' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xfXJzSug' (errno=Operation not permitted)
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5urt2gi7' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RRs85YkU' (errno=Operation not permitted)
3cd6aad fix(fitting): unify remaining shirley/smart/tougaard call sites onto n_avg (F3 cont.)
autofit/parity.py
fitting.py
tests/autofit/fixtures/u4f_battery_expected.json
tests/test_background_n_avg.py

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VkFfoFzV' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YNYPjBIQ' (errno=Operation not permitted)
commit 3cd6aad633be0f80bfd3bc94a4c91fe60f8cef64
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Fri Jul 17 17:26:08 2026 -0600

    fix(fitting): unify remaining shirley/smart/tougaard call sites onto n_avg (F3 cont.)
    
    Codex review of c5a24ac (n_avg convention unification) caught a real bug
    beyond the original patch's scope, independently on both round-1 runs:
    smart_background's post-hoc `np.minimum(shir, y)` clamp reads whatever y
    it's given. run_fit, compute_background_only, and autofit/parity.py's
    mirror all still called it as smart_background(x, _apply_endpoint_averaging(y,
    endpoint_avg)) — the old external-pre-averaging convention — so the clamp
    landed against the AVERAGED copy. The new engine.py path
    (_compute_background -> smart_background(x, y, n_avg=N)) clamps against
    the TRUE raw data. These diverge once endpoint_avg > 1, defeating F3's
    entire point: Find Peaks and manual Run Fit would disagree on SMART
    backgrounds for the same knob value. Independently reproduced (own probe
    matched Codex's ~437-count divergence) before acting on it.
    
    Fix: migrate all 6 remaining call sites (3 in run_fit, 3 in
    compute_background_only, mirrored in autofit/parity.py) from external
    pre-averaging to the same direct n_avg convention already used by
    smart_experimental_background / shirley_linear_background. shirley_background
    and tougaard_background are mathematically invariant to which convention
    is used — both read only the (possibly pre-averaged) array handed to them,
    with no second reference back to "true raw" — so this is a no-op for
    those two (proven by the existing test suite: they already passed the
    manual-vs-direct equivalence check). smart_background is the only one
    with a second raw-data reference, hence the only one that actually
    changes. Removed autofit/parity.py's now-unused _apply_endpoint_averaging
    import.
    
    New test: test_compute_background_only_matches_direct_call_with_n_avg,
    parametrized over shirley/smart/tougaard. Red confirmed first (fails only
    for smart, as expected — shirley/tougaard already passed); green after.
    
    Consequence, surfaced to and approved by Skye before implementing (the
    patch replaces rather than merely wires, and touches a real saved
    reference fit's frozen numbers — the same class of judgment call flagged
    for F1): one real fixture record changes. "U4f Scan" in
    docs/autofit/test_data/4-GTA UCl4-BN.proj.zip uses smart background with
    endpointAvg=6 — the exact combination this bug affects. Regenerated
    tests/autofit/fixtures/u4f_battery_expected.json via its committed
    generator (scripts/gen_u4f_battery_fixture.py); diffed before/after and
    confirmed only that one record changed meaningfully (reduced_chi_square
    11.399835330377146 -> 11.281303682238963, ~1.04% improvement — clamping
    against true raw data is physically the more correct reference, consistent
    with the improved fit). Every other record in the fixture differs by
    <1e-6 relative (ordinary lmfit refit floating-point noise, not this
    change). Grepped every *.proj.zip under docs/autofit/test_data/: only 3
    spectra anywhere use smart+endpoint_avg>1, 2 of which the generator
    already skips for an unrelated pre-existing reason ("fit-time grid
    drifted from current ui state"), leaving exactly this one affected
    record.
    
    Verified: tests/test_background_n_avg.py (16/16), tests/test_tougaard_background.py,
    and the C1s/U4f/B1s-Cl2p parity batteries (159 total) all green. Full
    suite: 681 passed, 6 skipped, 1 failed (test_u4f_n1s_cofit — a
    pre-existing timing/hash-seed-sensitive flake, confirmed byte-identical
    to a failure already independently ruled out earlier in this effort via
    git-stash A/B testing; it does not reproduce on every run, including the
    gated rerun below). RUN_AUTOFIT_GATE=1 real-data gate suite: 11 passed,
    1 failed (test_candidate_pool_real_gate.py's ds8 timing-budget flake,
    also previously confirmed pre-existing and unrelated) — test_u4f_n1s_cofit
    passed on this run, consistent with known flakiness in both directions,
    not a regression.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
---
 autofit/parity.py                                |  7 +-
 fitting.py                                       | 12 ++--
 tests/autofit/fixtures/u4f_battery_expected.json | 84 ++++++++++++------------
 tests/test_background_n_avg.py                   | 30 +++++++++
 4 files changed, 81 insertions(+), 52 deletions(-)

diff --git a/autofit/parity.py b/autofit/parity.py
index f579a3b..fb09ddd 100644
--- a/autofit/parity.py
+++ b/autofit/parity.py
@@ -28,7 +28,6 @@ import numpy as np
 
 from fitting import (
     _SHAPE_FUNCS,
-    _apply_endpoint_averaging,
     linear_background,
     shirley_background,
     shirley_linear_background,
@@ -96,15 +95,15 @@ def background_like_run_fit(
     m = (method or "shirley").lower()
 
     if m == "shirley":
-        bg_inner = shirley_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
+        bg_inner = shirley_background(xb, yb, n_avg=endpoint_avg)
     elif m == "smart":
-        bg_inner = smart_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
+        bg_inner = smart_background(xb, yb, n_avg=endpoint_avg)
     elif m == "smart_exp":
         bg_inner = smart_experimental_background(xb, yb, n_avg=endpoint_avg)
     elif m == "shirley_linear":
         bg_inner = shirley_linear_background(xb, yb, n_avg=endpoint_avg)
     elif m == "tougaard":
-        bg_inner = tougaard_background(xb, _apply_endpoint_averaging(yb, endpoint_avg))
+        bg_inner = tougaard_background(xb, yb, n_avg=endpoint_avg)
     elif m == "linear":
         if x[i1 - 1] != x[i0]:
             slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
diff --git a/fitting.py b/fitting.py
index 93bb345..00dfbbc 100644
--- a/fitting.py
+++ b/fitting.py
@@ -1047,15 +1047,15 @@ def run_fit(
         else:
             bg = linear_background(x, y)
     elif bg_method == "shirley":
-        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
+        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
     elif bg_method == "smart":
-        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
+        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
     elif bg_method == "smart_exp":
         bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
     elif bg_method == "shirley_linear":
         bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
     elif bg_method == "tougaard":
-        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
+        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
     elif bg_method == "linear":
         # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
         # across the full ROI. The line is well-defined everywhere, so
@@ -1285,15 +1285,15 @@ def compute_background_only(
     x, y = energy[i0:i1], counts[i0:i1]
 
     if method == "shirley":
-        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
+        bg = shirley_background(x, y, n_avg=endpoint_avg)
     elif method == "smart":
-        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
+        bg = smart_background(x, y, n_avg=endpoint_avg)
     elif method == "smart_exp":
         bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
     elif method == "shirley_linear":
         bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
     elif method == "tougaard":
-        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
+        bg = tougaard_background(x, y, n_avg=endpoint_avg)
     elif method == "linear":
         bg = linear_background(x, y)
     elif method in ("none", "flat", "", "manual"):
diff --git a/tests/autofit/fixtures/u4f_battery_expected.json b/tests/autofit/fixtures/u4f_battery_expected.json
index 0cd9b22..0f7e5d7 100644
--- a/tests/autofit/fixtures/u4f_battery_expected.json
+++ b/tests/autofit/fixtures/u4f_battery_expected.json
@@ -374,88 +374,88 @@
    "name": "U4f Scan",
    "peaks": [
     {
-     "amplitude": 7635.766080337974,
-     "area": -21878.05776656253,
-     "center": 380.604778490284,
-     "fwhm": 2.4788582828809957,
+     "amplitude": 7634.934773080449,
+     "area": -21862.45840089331,
+     "center": 380.6046583645018,
+     "fwhm": 2.4773151720223288,
      "id": "2"
     },
     {
-     "amplitude": 5726.824560253481,
-     "area": -16006.332799581052,
-     "center": 391.50477849028397,
-     "fwhm": 2.4788582828809957,
+     "amplitude": 5726.2010798103365,
+     "area": -15995.158743198761,
+     "center": 391.5046583645018,
+     "fwhm": 2.4773151720223288,
      "id": "3"
     },
     {
-     "amplitude": 1582.68042844834,
-     "area": -6691.060197214448,
-     "center": 386.8757399286858,
+     "amplitude": 1583.0468828413811,
+     "area": -6713.665921082466,
+     "center": 386.87524055507754,
      "fwhm": 3.3,
      "id": "10"
     },
     {
-     "amplitude": 1187.010321336255,
-     "area": -4887.733859924222,
-     "center": 397.77573992868577,
+     "amplitude": 1187.2851621310358,
+     "area": -4902.250280800907,
+     "center": 397.7752405550775,
      "fwhm": 3.3,
      "id": "11"
     },
     {
-     "amplitude": 105851.37098953135,
-     "area": -137429.0339355371,
-     "center": 398.3038844319093,
-     "fwhm": 1.0501567164994936,
+     "amplitude": 105851.69607784999,
+     "area": -137429.07665383045,
+     "center": 398.30386494123576,
+     "fwhm": 1.050116484190386,
      "id": "12"
     }
    ],
    "project": "4-GTA UCl4-BN.proj.zip",
-   "r_factor": 0.03871434979643854,
-   "reduced_chi_square": 11.399835330377146,
+   "r_factor": 0.03855137223759979,
+   "reduced_chi_square": 11.281303682238963,
    "success": true
   },
   {
    "name": "U4f Scan_5",
    "peaks": [
     {
-     "amplitude": 7438.971665168653,
-     "area": -20362.994930056404,
-     "center": 380.7881460141099,
-     "fwhm": 2.2972756365480214,
+     "amplitude": 7438.971665170913,
+     "area": -20362.994930060784,
+     "center": 380.78814601410994,
+     "fwhm": 2.297275636551439,
      "id": "2"
     },
     {
-     "amplitude": 5579.22874887649,
-     "area": -14918.427925166918,
-     "center": 391.68814601410986,
-     "fwhm": 2.2972756365480214,
+     "amplitude": 5579.228748878185,
+     "area": -14918.427925169704,
+     "center": 391.6881460141099,
+     "fwhm": 2.297275636551439,
      "id": "3"
     },
     {
-     "amplitude": 1337.469798833749,
-     "area": -5659.447945233339,
-     "center": 387.01508576567545,
-     "fwhm": 3.5752402300579225,
+     "amplitude": 1337.4697988345308,
+     "area": -5659.4479452296055,
+     "center": 387.01508576567437,
+     "fwhm": 3.5752402300533492,
      "id": "10"
     },
     {
-     "amplitude": 1003.1023491253118,
-     "area": -4171.358546544785,
-     "center": 397.9150857656754,
-     "fwhm": 3.5752402300579225,
+     "amplitude": 1003.1023491258982,
+     "area": -4171.358546542147,
+     "center": 397.91508576567435,
+     "fwhm": 3.5752402300533492,
      "id": "11"
     },
     {
-     "amplitude": 97015.14582081117,
-     "area": -125080.23806726343,
-     "center": 398.313299398849,
-     "fwhm": 1.046277706787133,
+     "amplitude": 97015.14582080937,
+     "area": -125080.23806726135,
+     "center": 398.3132993988489,
+     "fwhm": 1.0462777067870674,
      "id": "12"
     }
    ],
    "project": "4-GTA UCl4-BN.proj.zip",
-   "r_factor": 0.04748332187164556,
-   "reduced_chi_square": 17.896494217928357,
+   "r_factor": 0.047483321871641115,
+   "reduced_chi_square": 17.89649421792836,
    "success": true
   },
   {
diff --git a/tests/test_background_n_avg.py b/tests/test_background_n_avg.py
index 9a4cbca..d131f5e 100644
--- a/tests/test_background_n_avg.py
+++ b/tests/test_background_n_avg.py
@@ -13,6 +13,7 @@ import pytest
 
 from fitting import (
     _apply_endpoint_averaging,
+    compute_background_only,
     shirley_background,
     smart_background,
     smart_experimental_background,
@@ -143,3 +144,32 @@ def test_compute_background_linear_ignores_endpoint_avg():
     no_avg = _compute_background(x, y, BackgroundType.LINEAR)
     with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
     assert np.array_equal(no_avg, with_avg)
+
+
+@pytest.mark.parametrize("method", ["shirley", "smart", "tougaard"])
+def test_compute_background_only_matches_direct_call_with_n_avg(method):
+    """The manual /api/background and /api/fit dispatch (compute_background_only,
+    mirrored by run_fit and autofit/parity.py) must produce IDENTICAL output to
+    calling the underlying fitting.py function directly with the same n_avg --
+    the whole point of F3 is that Find Peaks (via _compute_background) and
+    manual Run Fit agree once both pass the same endpoint_avg.
+
+    This is the parity gap Codex review caught in c5a24ac: smart_background
+    has a post-hoc `np.minimum(shir, y)` clamp, so pre-averaging y externally
+    (the old convention, still used by compute_background_only/run_fit/
+    parity.py before this fix) clamps against the AVERAGED copy, while
+    passing n_avg directly (the new engine.py convention) clamps against the
+    TRUE raw data -- a real, non-trivial divergence for SMART specifically
+    once endpoint_avg > 1 is used (shirley/tougaard have no such post-hoc
+    step and were already equivalent either way)."""
+    x, y = _noisy_endpoint_fixture()
+    direct_fn = {"shirley": shirley_background, "smart": smart_background,
+                 "tougaard": tougaard_background}[method]
+    for n_avg in (1, 4, 8):
+        result = compute_background_only(x, y, method=method, endpoint_avg=n_avg)
+        via_dispatch = np.array(result["background"])
+        direct = direct_fn(x, y, n_avg=n_avg)
+        assert np.allclose(via_dispatch, direct, rtol=1e-9), (
+            f"{method} dispatch diverges from direct n_avg={n_avg} call by "
+            f"{np.max(np.abs(via_dispatch - direct)):.3f}"
+        )

codex
The diff scope matches the four claimed files. Next I’m reading the actual background implementations, because the invariance claim turns on whether those functions keep both raw and averaged arrays alive.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '1015,1315p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'rg -n "def (shirley_background|smart_background|tougaard_background|_apply_endpoint_averaging|compute_background_only|run_fit)" fitting.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
306:def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
320:def shirley_background(
384:def smart_background(
528:def tougaard_background(
954:def run_fit(
1274:def compute_background_only(

 succeeded in 0ms:
  1015	    if i1 - i0 < 2:
  1016	        i0, i1 = 0, len(energy)
  1017	
  1018	    x = energy
  1019	    y = counts
  1020	    x_bg = energy[i0:i1]
  1021	    y_bg = counts[i0:i1]
  1022	
  1023	    # ── Background ────────────────────────────────────────────────────────────
  1024	    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
  1025	    # physically defined only between the user's two anchor points: the
  1026	    # integral represents inelastic-loss cumulation through the peaks
  1027	    # *between* those anchors. Computing them over the full ROI would
  1028	    # let peaks outside the anchor window contribute to the loss
  1029	    # integral, which violates the model's premise. We therefore
  1030	    # compute them on [i0:i1] and flat-hold the endpoint value across
  1031	    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
  1032	    # values by construction, so constant extension is the least-bad
  1033	    # continuation. Linear backgrounds are extrapolated across the
  1034	    # full ROI (the line is well-defined outside the anchor window).
  1035	    bg_method = background_method.lower()
  1036	    bg_inner: np.ndarray | None = None
  1037	
  1038	    if manual_bg is not None and bg_method == "manual":
  1039	        # manual_bg is a list of [be, intensity] anchor points from the
  1040	        # frontend. The anchors are BE-anchored (independent of i0/i1),
  1041	        # so interpolate them across the full ROI grid.
  1042	        anchors = sorted(manual_bg, key=lambda a: a[0])
  1043	        if len(anchors) >= 2:
  1044	            anchor_x = np.array([a[0] for a in anchors])
  1045	            anchor_y = np.array([a[1] for a in anchors])
  1046	            bg = np.interp(x, anchor_x, anchor_y)
  1047	        else:
  1048	            bg = linear_background(x, y)
  1049	    elif bg_method == "shirley":
  1050	        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
  1051	    elif bg_method == "smart":
  1052	        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
  1053	    elif bg_method == "smart_exp":
  1054	        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
  1055	    elif bg_method == "shirley_linear":
  1056	        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
  1057	    elif bg_method == "tougaard":
  1058	        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
  1059	    elif bg_method == "linear":
  1060	        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
  1061	        # across the full ROI. The line is well-defined everywhere, so
  1062	        # constant extension would discard real information.
  1063	        if x[i1 - 1] != x[i0]:
  1064	            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
  1065	        else:
  1066	            slope = 0.0
  1067	        bg = y[i0] + slope * (x - x[i0])
  1068	    elif bg_method in ("none", "flat", "", "manual"):
  1069	        bg = np.zeros_like(y)
  1070	    else:
  1071	        raise ValueError(f"Unknown background method '{background_method}'")
  1072	
  1073	    if bg_inner is not None:
  1074	        # Embed the anchor-window integral background into a full-ROI
  1075	        # array; flat-hold the endpoint value outside [i0, i1]. In the
  1076	        # common case where the user keeps bg anchors at the ROI edges
  1077	        # this is a no-op (i0=0, i1=len(y)).
  1078	        bg = np.zeros_like(y)
  1079	        if len(bg_inner) > 0:
  1080	            bg[i0:i1] = bg_inner
  1081	            if i0 > 0:
  1082	                bg[:i0] = bg_inner[0]
  1083	            if i1 < len(y):
  1084	                bg[i1:] = bg_inner[-1]
  1085	
  1086	    y_sub = y - bg
  1087	
  1088	    # Poisson weights: σ = √(raw counts), weight = 1/σ
  1089	    # Use raw counts (before background subtraction) for uncertainty estimate,
  1090	    # since the noise comes from the total photon counting statistics.
  1091	    # Floor at 1.0 to avoid division by zero for zero-count channels.
  1092	    sigma = np.sqrt(np.maximum(y, 1.0))
  1093	    weights = 1.0 / sigma
  1094	
  1095	    # ── Build composite lmfit model ───────────────────────────────────────────
  1096	    # Sort so unconstrained (master) peaks come before constrained ones
  1097	    ordered = sorted(
  1098	        peak_specs,
  1099	        key=lambda s: 0 if s.get("constrain_to") is None else 1,
  1100	    )
  1101	
  1102	    composite_model: Model | None = None
  1103	    all_params = Parameters()
  1104	
  1105	    for spec in ordered:
  1106	        shape = spec.get("shape", "pseudo_voigt_gl")
  1107	        if shape not in _SHAPE_FUNCS:
  1108	            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
  1109	        func = _SHAPE_FUNCS[shape]
  1110	        prefix = f"p{spec['id']}_"
  1111	        m = Model(func, prefix=prefix)
  1112	        p = _make_peak_params(m, spec, prefix, ordered)
  1113	        all_params.update(p)
  1114	        composite_model = m if composite_model is None else composite_model + m
  1115	
  1116	    if composite_model is None:
  1117	        raise RuntimeError("No peaks were built")
  1118	
  1119	    # ── Fit ───────────────────────────────────────────────────────────────────
  1120	    kws = {"method": "leastsq", "nan_policy": "omit"}
  1121	    if fit_kws:
  1122	        kws.update(fit_kws)
  1123	
  1124	    # ── Diagnostic logging: BEFORE optimisation ──────────────────────────────
  1125	    if log.isEnabledFor(logging.DEBUG):
  1126	        log.debug("═══ FIT START ═══  method=%s  n_data=%d", kws.get('method'), len(y_sub))
  1127	        for pname, par in sorted(all_params.items()):
  1128	            log.debug("  BEFORE  %-30s value=%12.6f  vary=%-5s  expr=%s  min=%s  max=%s",
  1129	                      pname, par.value, str(par.vary), par.expr,
  1130	                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
  1131	                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')
  1132	
  1133	    try:
  1134	        result = composite_model.fit(y_sub, all_params, x=x, weights=weights, **kws)
  1135	    except Exception as exc:
  1136	        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc
  1137	
  1138	    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
  1139	    if log.isEnabledFor(logging.DEBUG):
  1140	        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
  1141	                  result.success, result.nfev, result.message)
  1142	        for pname, par in sorted(result.params.items()):
  1143	            init = all_params[pname].value if pname in all_params else None
  1144	            delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
  1145	            log.debug("  AFTER   %-30s value=%12.6f  stderr=%s%s",
  1146	                      pname, par.value,
  1147	                      f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)
  1148	
  1149	    # ── Perturb and refit to escape local minima ─────────────────────────
  1150	    if n_perturb > 0 and result.success:
  1151	        best_result = result
  1152	        best_redchi = result.redchi if result.redchi is not None else float('inf')
  1153	        rng = np.random.default_rng()
  1154	
  1155	        for attempt in range(n_perturb):
  1156	            perturbed_params = result.params.copy()
  1157	            for pname, par in perturbed_params.items():
  1158	                if par.vary and par.value != 0:
  1159	                    # Perturb by ±15% random
  1160	                    scale = 1.0 + rng.uniform(-0.15, 0.15)
  1161	                    new_val = par.value * scale
  1162	                    # Respect bounds
  1163	                    if np.isfinite(par.min):
  1164	                        new_val = max(new_val, par.min)
  1165	                    if np.isfinite(par.max):
  1166	                        new_val = min(new_val, par.max)
  1167	                    perturbed_params[pname].set(value=new_val)
  1168	                elif par.vary and par.value == 0:
  1169	                    # For zero-valued params, add small absolute perturbation
  1170	                    perturbed_params[pname].set(value=rng.uniform(0.001, 0.05))
  1171	
  1172	            try:
  1173	                trial = composite_model.fit(y_sub, perturbed_params, x=x, weights=weights, **kws)
  1174	                trial_redchi = trial.redchi if trial.redchi is not None else float('inf')
  1175	                log.debug("  PERTURB %d/%d  redchi=%.4f  (best=%.4f)",
  1176	                          attempt + 1, n_perturb, trial_redchi, best_redchi)
  1177	                if trial.success and trial_redchi < best_redchi:
  1178	                    best_result = trial
  1179	                    best_redchi = trial_redchi
  1180	                    log.debug("  *** New best found! redchi improved to %.4f", best_redchi)
  1181	            except Exception:
  1182	                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
  1183	                continue
  1184	
  1185	        if best_result is not result:
  1186	            log.debug("═══ PERTURB IMPROVED FIT ═══  redchi: %.4f → %.4f",
  1187	                      result.redchi, best_redchi)
  1188	            result = best_result
  1189	
  1190	    fitted_sub = result.best_fit
  1191	    fitted_y = fitted_sub + bg
  1192	
  1193	    # ── Per‑peak results ──────────────────────────────────────────────────────
  1194	    individual_peaks = []
  1195	    for spec in peak_specs:
  1196	        pid = spec["id"]
  1197	        prefix = f"p{pid}_"
  1198	        peak_y = composite_model.components[
  1199	            next(i for i, c in enumerate(composite_model.components)
  1200	                 if c.prefix == prefix)
  1201	        ].eval(result.params, x=x)
  1202	
  1203	        # Area by numerical integration
  1204	        area = float(trapezoid(peak_y, x))
  1205	
  1206	        # Parameter extraction with stderr
  1207	        param_info: dict[str, Any] = {}
  1208	        for pname in result.params:
  1209	            if pname.startswith(prefix):
  1210	                short = pname[len(prefix):]
  1211	                par = result.params[pname]
  1212	                param_info[short] = {
  1213	                    "value": float(par.value),
  1214	                    "stderr": float(par.stderr) if par.stderr is not None else None,
  1215	                    "vary": par.vary,
  1216	                    "expr": par.expr,
  1217	                    "min": float(par.min) if np.isfinite(par.min) else None,
  1218	                    "max": float(par.max) if np.isfinite(par.max) else None,
  1219	                }
  1220	
  1221	        param_info["area"] = {"value": area, "stderr": None}
  1222	
  1223	        # Approximate area stderr via amplitude + fwhm propagation
  1224	        amp_par = result.params.get(prefix + "amplitude")
  1225	        fwhm_par = result.params.get(prefix + "fwhm")
  1226	        if (amp_par and fwhm_par and amp_par.stderr and fwhm_par.stderr
  1227	                and amp_par.value and fwhm_par.value):
  1228	            rel_err = np.sqrt(
  1229	                (amp_par.stderr / amp_par.value) ** 2
  1230	                + (fwhm_par.stderr / fwhm_par.value) ** 2
  1231	            )
  1232	            param_info["area"]["stderr"] = abs(area) * rel_err
  1233	
  1234	        individual_peaks.append({
  1235	            "id": pid,
  1236	            "y": peak_y.tolist(),
  1237	            "params": param_info,
  1238	        })
  1239	
  1240	    # ── Statistics ────────────────────────────────────────────────────────────
  1241	    n_data = len(y_sub)
  1242	    n_free = result.nvarys
  1243	    chi_sq = float(result.chisqr) if result.chisqr is not None else None
  1244	    red_chi_sq = float(result.redchi) if result.redchi is not None else None
  1245	
  1246	    residuals = (y_sub - fitted_sub).tolist()
  1247	
  1248	    # R‑factor (like in crystallography: sum|obs-calc| / sum|obs|)
  1249	    r_factor = (float(np.sum(np.abs(y_sub - fitted_sub)) / np.sum(np.abs(y_sub)))
  1250	                if np.sum(np.abs(y_sub)) > 0 else None)
  1251	
  1252	    return {
  1253	        "success": result.success,
  1254	        "message": result.message,
  1255	        "energy": x.tolist(),
  1256	        "counts": y.tolist(),
  1257	        "fitted_y": fitted_y.tolist(),
  1258	        "background_y": bg.tolist(),
  1259	        "residuals": residuals,
  1260	        "individual_peaks": individual_peaks,
  1261	        "statistics": {
  1262	            "chi_square": chi_sq,
  1263	            "reduced_chi_square": red_chi_sq,
  1264	            "r_factor": r_factor,
  1265	            "n_data": n_data,
  1266	            "n_free_params": n_free,
  1267	            "aic": float(result.aic) if result.aic is not None else None,
  1268	            "bic": float(result.bic) if result.bic is not None else None,
  1269	        },
  1270	        "charge_shift_applied": charge_shift_ev,
  1271	    }
  1272	
  1273	
  1274	def compute_background_only(
  1275	    energy: np.ndarray,
  1276	    counts: np.ndarray,
  1277	    method: str = "shirley",
  1278	    start_idx: int | None = None,
  1279	    end_idx: int | None = None,
  1280	    endpoint_avg: int = 1,
  1281	) -> dict[str, Any]:
  1282	    """Return just the background array without fitting peaks."""
  1283	    i0 = start_idx if start_idx is not None else 0
  1284	    i1 = end_idx if end_idx is not None else len(energy)
  1285	    x, y = energy[i0:i1], counts[i0:i1]
  1286	
  1287	    if method == "shirley":
  1288	        bg = shirley_background(x, y, n_avg=endpoint_avg)
  1289	    elif method == "smart":
  1290	        bg = smart_background(x, y, n_avg=endpoint_avg)
  1291	    elif method == "smart_exp":
  1292	        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
  1293	    elif method == "shirley_linear":
  1294	        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
  1295	    elif method == "tougaard":
  1296	        bg = tougaard_background(x, y, n_avg=endpoint_avg)
  1297	    elif method == "linear":
  1298	        bg = linear_background(x, y)
  1299	    elif method in ("none", "flat", "", "manual"):
  1300	        bg = np.zeros_like(y)
  1301	    else:
  1302	        raise ValueError(f"Unknown background method '{method}'")
  1303	
  1304	    return {
  1305	        "energy": x.tolist(),
  1306	        "background": bg.tolist(),
  1307	        "net_counts": (y - bg).tolist(),
  1308	    }

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '1,260p'" in /Users/skyefortier/xps-verify
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
   221	                                   ds_core if x[-1] > x[0] else ds_core[::-1]))
   222	        if peak_val <= 0.0:
   223	            peak_val = np.max(np.abs(ds_core))
   224	        if peak_val <= 0.0:
   225	            return np.zeros_like(x)
   226	        return amplitude * ds_core / peak_val
   227	
   228	    # ── Build padded grid for convolution ─────────────────────────────────────
   229	    # Pad by ±10·m_gauss (≈ ±4.25σ) to avoid truncation artifacts.
   230	    # The DS power-law tail decays as |ε|^(α−1), which is slow for small α,
   231	    # so generous padding is essential.
   232	    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 0.05
   233	    step = max(step, 1e-6)
   234	
   235	    pad_ev = max(10.0 * m_gauss, 20.0 * beta)  # eV of padding on each side
   236	    n_pad = int(np.ceil(pad_ev / step))
   237	    n_pad = max(n_pad, 1)
   238	
   239	    # Determine sort direction of input x
   240	    ascending = (x[-1] > x[0]) if len(x) > 1 else True
   241	
   242	    # Create padded energy grid extending beyond the data range
   243	    if ascending:
   244	        x_pad_lo = x[0] - n_pad * step
   245	        x_pad_hi = x[-1] + n_pad * step
   246	    else:
   247	        x_pad_lo = x[-1] - n_pad * step
   248	        x_pad_hi = x[0] + n_pad * step
   249	
   250	    n_total = len(x) + 2 * n_pad
   251	    x_padded = np.linspace(x_pad_lo, x_pad_hi, n_total)  # always ascending
   252	
   253	    # Evaluate DS core on padded grid
   254	    ds_padded = _ds_core(x_padded)
   255	
   256	    # ── Cosine taper on pad regions ───────────────────────────────────────────
   257	    # Smoothly ramp to zero at the array edges to kill any residual signal
   258	    # that would cause Gibbs-like ringing in FFT convolution.
   259	    taper = np.ones(n_total)
   260	    if n_pad > 1:

exec
/bin/zsh -lc "nl -ba autofit/parity.py | sed -n '1,135p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	Parity / characterization utilities for the autofit engine.
     3	
     4	Two independent parity notions, both against the expert reference fits in
     5	``docs/autofit/test_data``:
     6	
     7	1. **Eval parity** — evaluating the saved peak parameters through
     8	   ``fitting.py``'s lineshape functions (+ the exact background
     9	   reconstruction ``run_fit`` performs) reproduces the saved
    10	   ``fitResult.fittedY``.  This proves the spec mirror
    11	   (``peak_to_backend_spec``) and the lineshape math agree with what
    12	   produced the expert fits.
    13	
    14	2. **Refit stability** — re-running ``fitting.run_fit`` seeded at the saved
    15	   parameters stays at the same minimum (no parameter drift, same χ²ᵣ).
    16	   Frozen into a fixture, this is the regression net that pins today's
    17	   manual-fit behavior.
    18	
    19	Neither imports anything from ``app.py`` and nothing here is reachable from
    20	the production request path.
    21	"""
    22	
    23	from __future__ import annotations
    24	
    25	from typing import Any
    26	
    27	import numpy as np
    28	
    29	from fitting import (
    30	    _SHAPE_FUNCS,
    31	    linear_background,
    32	    shirley_background,
    33	    shirley_linear_background,
    34	    smart_background,
    35	    smart_experimental_background,
    36	    tougaard_background,
    37	    run_fit,
    38	)
    39	from .reference import ReferenceFit
    40	
    41	
    42	def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
    43	    """Evaluate one backend peak spec at its own parameter values."""
    44	    f = _SHAPE_FUNCS[spec["shape"]]
    45	    a, c, s = spec["amplitude"], spec["center"], spec["shape"]
    46	    if s in ("gaussian", "lorentzian"):
    47	        return f(be, a, c, spec["fwhm"])
    48	    if s == "pseudo_voigt_gl":
    49	        return f(be, a, c, spec["fwhm"], spec["gl_ratio"])
    50	    if s == "asymmetric_gl":
    51	        return f(be, a, c, spec["fwhm"], spec["asymmetry"], spec["gl_ratio"])
    52	    if s == "doniach_sunjic":
    53	        return f(be, a, c, spec["fwhm"], spec["alpha"], spec["gamma_asym"])
    54	    if s == "ds_g":
    55	        return f(be, a, c, spec["alpha"], spec["beta"], spec["m_gauss"])
    56	    if s == "la_casaxps":
    57	        return f(be, a, c, spec["fwhm"], spec["alpha"], spec["beta"], spec["m"])
    58	    raise ValueError(f"Unknown backend shape {s!r}")
    59	
    60	
    61	def evaluate_model(be: np.ndarray, specs: list[dict]) -> np.ndarray:
    62	    """Sum of all peak evaluations (no background)."""
    63	    total = np.zeros_like(np.asarray(be, dtype=float))
    64	    for s in specs:
    65	        total = total + evaluate_peak(be, s)
    66	    return total
    67	
    68	
    69	def background_like_run_fit(
    70	    x: np.ndarray,
    71	    y: np.ndarray,
    72	    method: str,
    73	    bg_start_idx: int,
    74	    bg_end_idx: int,
    75	    endpoint_avg: int = 1,
    76	) -> np.ndarray:
    77	    """
    78	    Reproduce exactly the background array ``run_fit`` constructs — including
    79	    the anchor-window normalization (swap reversed indices, bail to full ROI
    80	    below 2 points), the ``[i0:i1]`` slice semantics, and the flat-hold
    81	    extension outside the anchor window.  Kept in lockstep with
    82	    ``fitting.run_fit``; the eval-parity battery fails if they diverge.
    83	    """
    84	    x = np.asarray(x, dtype=float)
    85	    y = np.asarray(y, dtype=float)
    86	    i0, i1 = bg_start_idx, bg_end_idx
    87	    i0 = max(0, i0)
    88	    i1 = min(len(x), i1)
    89	    if i0 > i1:
    90	        i0, i1 = i1, i0
    91	    if i1 - i0 < 2:
    92	        i0, i1 = 0, len(x)
    93	
    94	    xb, yb = x[i0:i1], y[i0:i1]
    95	    m = (method or "shirley").lower()
    96	
    97	    if m == "shirley":
    98	        bg_inner = shirley_background(xb, yb, n_avg=endpoint_avg)
    99	    elif m == "smart":
   100	        bg_inner = smart_background(xb, yb, n_avg=endpoint_avg)
   101	    elif m == "smart_exp":
   102	        bg_inner = smart_experimental_background(xb, yb, n_avg=endpoint_avg)
   103	    elif m == "shirley_linear":
   104	        bg_inner = shirley_linear_background(xb, yb, n_avg=endpoint_avg)
   105	    elif m == "tougaard":
   106	        bg_inner = tougaard_background(xb, yb, n_avg=endpoint_avg)
   107	    elif m == "linear":
   108	        if x[i1 - 1] != x[i0]:
   109	            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
   110	        else:
   111	            slope = 0.0
   112	        return y[i0] + slope * (x - x[i0])
   113	    elif m in ("none", "flat", "", "manual"):
   114	        return np.zeros_like(y)
   115	    else:
   116	        raise ValueError(f"Unknown background method {method!r}")
   117	
   118	    bg = np.zeros_like(y)
   119	    if len(bg_inner) > 0:
   120	        bg[i0:i1] = bg_inner
   121	        if i0 > 0:
   122	            bg[:i0] = bg_inner[0]
   123	        if i1 < len(y):
   124	            bg[i1:] = bg_inner[-1]
   125	    return bg
   126	
   127	
   128	# ─────────────────────────────────────────────────────────────────────────────
   129	# Parity records
   130	# ─────────────────────────────────────────────────────────────────────────────
   131	
   132	def battery_eligible(rf: ReferenceFit, region: str = "C 1s") -> tuple[bool, str]:
   133	    """
   134	    Single source of truth for battery/roster eligibility, shared by the
   135	    fixture generator and the pytest battery so they can never disagree.

codex
The implementation confirms the call-site side of the change: `run_fit`, `compute_background_only`, and the parity mirror now pass raw slices plus `n_avg`. I’m checking the fixture corpus next rather than trusting the regenerated JSON diff.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '300,575p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   300	
   301	
   302	# ─────────────────────────────────────────────────────────────────────────────
   303	# Background functions
   304	# ─────────────────────────────────────────────────────────────────────────────
   305	
   306	def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
   307	    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
   308	    n = len(y)
   309	    if n_avg <= 1 or n < 4:
   310	        return y.copy()
   311	    cap = min(n_avg, n // 4)
   312	    if cap < 1:
   313	        return y.copy()
   314	    out = y.copy()
   315	    out[:cap] = np.mean(y[:cap])
   316	    out[-cap:] = np.mean(y[-cap:])
   317	    return out
   318	
   319	
   320	def shirley_background(
   321	    x: np.ndarray,
   322	    y: np.ndarray,
   323	    n_iter: int = 200,
   324	    tol: float = 1e-6,
   325	    n_avg: int = 1,
   326	) -> np.ndarray:
   327	    """
   328	    Iterative Shirley background (Proctor & Sherwood, Surf. Sci. 1982).
   329	
   330	    Works on ascending or descending binding energy arrays.
   331	
   332	    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
   333	    levels B_low/B_high are read (audit F3, 2026-07-17). Shirley scales the
   334	    ENTIRE background off those two levels, so a single noisy endpoint
   335	    sample propagates straight into the net area. n_avg=1 = raw endpoints =
   336	    previous behaviour. Callers previously had to pre-average the input
   337	    array themselves via _apply_endpoint_averaging; that convention was
   338	    easy to forget (autofit/engine.py did), so the knob now lives here,
   339	    matching smart_experimental_background / shirley_linear_background.
   340	
   341	    At each energy Eᵢ the background equals:
   342	        B(Eᵢ) = B_high + (B_low – B_high) · ∫_{Eᵢ}^{E_max} s(E) dE
   343	                                               ─────────────────────────
   344	                                               ∫_{E_min}^{E_max} s(E) dE
   345	    where s(E) = max(y(E) – B(E), 0) is the net signal.
   346	    B_low  = y(E_min),  B_high = y(E_max)  (the endpoint levels).
   347	    """
   348	    if len(x) < 2:
   349	        return np.zeros_like(y)
   350	
   351	    if n_avg > 1:
   352	        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)
   353	
   354	    # Work on ascending copy
   355	    if x[0] > x[-1]:
   356	        xs, ys = x[::-1].copy(), y[::-1].copy()
   357	        flipped = True
   358	    else:
   359	        xs, ys = x.copy(), y.copy()
   360	        flipped = False
   361	
   362	    b_low = ys[0]    # background at low‑BE end
   363	    b_high = ys[-1]  # background at high‑BE end
   364	
   365	    B = np.linspace(b_low, b_high, len(ys))  # linear initial guess
   366	
   367	    for _ in range(n_iter):
   368	        B_prev = B.copy()
   369	        signal = np.maximum(ys - B, 0.0)
   370	        # O(n) cumulative integral from high-x end back to each point
   371	        cum_right = np.zeros(len(ys))
   372	        for i in range(len(ys) - 2, -1, -1):
   373	            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
   374	        total = cum_right[0]
   375	        if total <= 0.0:
   376	            break
   377	        B = b_high + (b_low - b_high) * cum_right / total
   378	        if np.max(np.abs(B - B_prev)) < tol:
   379	            break
   380	
   381	    return B[::-1] if flipped else B
   382	
   383	
   384	def smart_background(
   385	    x: np.ndarray,
   386	    y: np.ndarray,
   387	    n_iter: int = 200,
   388	    tol: float = 1e-6,
   389	    n_avg: int = 1,
   390	) -> np.ndarray:
   391	    """Smart (constrained Shirley): standard Shirley clamped to never exceed data.
   392	
   393	    ``n_avg`` is forwarded to shirley_background (audit F3). The clamp is
   394	    applied against the RAW data, not the endpoint-averaged copy, so
   395	    averaging only ever moves the background — never the reported net
   396	    counts.
   397	    """
   398	    if len(x) < 2:
   399	        return np.zeros_like(y)
   400	    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
   401	    return np.minimum(shir, y)
   402	
   403	
   404	def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
   405	    """Straight‑line background connecting the first and last data points."""
   406	    slope = (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
   407	    return y[0] + slope * (x - x[0])
   408	
   409	
   410	def smart_experimental_background(
   411	    x: np.ndarray,
   412	    y: np.ndarray,
   413	    n_iter: int = 200,
   414	    tol: float = 1e-6,
   415	    n_avg: int = 1,
   416	) -> np.ndarray:
   417	    """Experimental constrained Shirley background, closer to public Avantage
   418	    Smart description.  The data constraint is enforced *during* iteration,
   419	    not as a post-hoc clamp.  Where the background would exceed the data it
   420	    locks to the data, effectively moving the Shirley start inward.  Better
   421	    for narrow spectral windows with sloped baselines."""
   422	    if len(x) < 2:
   423	        return np.zeros_like(y)
   424	
   425	    # Work on ascending copy
   426	    if x[0] > x[-1]:
   427	        xs, ys = x[::-1].copy(), y[::-1].copy()
   428	        flipped = True
   429	    else:
   430	        xs, ys = x.copy(), y.copy()
   431	        flipped = False
   432	
   433	    n = len(ys)
   434	    cap = max(1, min(n_avg, n // 4))
   435	    b_low = float(np.mean(ys[:cap]))      # low-BE endpoint
   436	    b_high = float(np.mean(ys[-cap:]))     # high-BE endpoint
   437	    step = b_low - b_high
   438	
   439	    # Linear initial guess
   440	    B = np.linspace(b_low, b_high, n)
   441	
   442	    for _ in range(n_iter):
   443	        B_prev = B.copy()
   444	        signal = np.maximum(ys - B, 0.0)
   445	        # Cumulative integral from high-BE end (right) back to each point
   446	        cum_right = np.zeros(n)
   447	        for i in range(n - 2, -1, -1):
   448	            dx = xs[i + 1] - xs[i]
   449	            cum_right[i] = cum_right[i + 1] + (signal[i] + signal[i + 1]) / 2 * dx
   450	        total = cum_right[0]
   451	        if total <= 0.0:
   452	            break
   453	
   454	        B = b_high + step * (cum_right / total)
   455	
   456	        # Constrain during iteration: lock to data where bg exceeds it
   457	        B = np.minimum(B, ys)
   458	
   459	        if np.max(np.abs(B - B_prev)) < tol:
   460	            break
   461	
   462	    B = np.minimum(B, ys)  # final safety clamp
   463	    return B[::-1] if flipped else B
   464	
   465	
   466	def shirley_linear_background(
   467	    x: np.ndarray,
   468	    y: np.ndarray,
   469	    n_iter: int = 200,
   470	    tol: float = 1e-6,
   471	    n_avg: int = 1,
   472	) -> np.ndarray:
   473	    """Hybrid Shirley + Linear background.
   474	
   475	    1. Average *n_avg* points at each endpoint.
   476	    2. Compute a linear baseline between the averaged endpoints.
   477	    3. Subtract the linear baseline → flattened data.
   478	    4. Iteratively compute a Shirley‑like cumulative correction on the
   479	       flattened data, scaled by the endpoint step height.
   480	    5. Add the correction back onto the linear baseline.
   481	    6. Clamp so the background never exceeds the data.
   482	    """
   483	    if len(x) < 2:
   484	        return np.zeros_like(y)
   485	
   486	    # Work on ascending copy
   487	    if x[0] > x[-1]:
   488	        xs, ys = x[::-1].copy(), y[::-1].copy()
   489	        flipped = True
   490	    else:
   491	        xs, ys = x.copy(), y.copy()
   492	        flipped = False
   493	
   494	    n = len(ys)
   495	    cap = max(1, min(n_avg, n // 4))
   496	    IL = float(np.mean(ys[:cap]))      # low‑BE endpoint
   497	    IH = float(np.mean(ys[-cap:]))     # high‑BE endpoint
   498	
   499	    # Linear baseline
   500	    linear = np.linspace(IL, IH, n)
   501	
   502	    # Flatten
   503	    flat = ys - linear
   504	
   505	    step_h = abs(IL - IH)
   506	    if step_h < 1e-12:
   507	        return linear[::-1] if flipped else linear
   508	
   509	    B = np.zeros(n)
   510	    for _ in range(n_iter):
   511	        B_prev = B.copy()
   512	        signal = np.maximum(flat - B, 0.0)
   513	        # O(n) cumulative integral from high-x end back to each point
   514	        cum_right = np.zeros(n)
   515	        for i in range(n - 2, -1, -1):
   516	            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
   517	        total = cum_right[0]
   518	        if total <= 0.0:
   519	            break
   520	        B = step_h * cum_right / total
   521	        if np.max(np.abs(B - B_prev)) < tol:
   522	            break
   523	
   524	    result = np.minimum(linear + B, ys)
   525	    return result[::-1] if flipped else result
   526	
   527	
   528	def tougaard_background(
   529	    x: np.ndarray,
   530	    y: np.ndarray,
   531	    n_avg: int = 1,
   532	) -> np.ndarray:
   533	    """Single-pass Tougaard universal-cross-section background, with the
   534	    constant (pre-loss) term the window-limited integral cannot generate.
   535	
   536	    Uses the two-parameter universal loss function
   537	    K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
   538	    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
   539	    cross-section fitted to noble/transition-metal optical data; the
   540	    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).
   541	
   542	    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
   543	    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
   544	    window BEGINS in a loss-free region, so that J at the low-BE edge is
   545	    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
   546	    there is a large inelastic baseline produced by every lower-BE
   547	    (higher-KE) transition OUTSIDE the window, which a window-limited
   548	    integral structurally cannot reproduce.  Because K(0) = 0, the bare
   549	    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
   550	    — the background visibly dove to ~0 there, and a flat featureless
   551	    window produced a full-amplitude phantom "signal".
   552	
   553	    So the low-BE edge level is taken as a constant offset C0 (the
   554	    out-of-window baseline the kernel cannot see), the kernel runs over the
   555	    net (J - C0), and the amplitude is then anchored so the background
   556	    meets the measured intensity at the HIGH-BE edge — the standard
   557	    practical Tougaard criterion (B is effectively fitted, which is why the
   558	    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
   559	    fitting B together with an offset rather than B alone.
   560	
   561	    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
   562	    levels are read, so neither C0 nor the high-BE anchor rests on a single
   563	    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
   564	    endpoints = previous behaviour.
   565	
   566	    The background at each binding energy accumulates loss contributions
   567	    from electrons emitted at LOWER BE (higher kinetic energy), so the
   568	    one-sided sum requires a descending-BE grid; input in either BE order
   569	    is normalized internally.  Mirrors the frontend JS twin
   570	    ``tougaardBackground``.
   571	    """
   572	    n = len(x)
   573	    if n < 2:
   574	        return np.zeros_like(y, dtype=float)
   575	

exec
/bin/zsh -lc "nl -ba tests/test_background_n_avg.py | sed -n '1,190p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""F3 regression tests (2026-07-17 background audit): shirley_background and
     2	smart_background must accept n_avg directly, matching the convention already
     3	used by smart_experimental_background / shirley_linear_background, and
     4	autofit/engine.py's _compute_background must forward an endpoint_avg knob to
     5	every background type it dispatches.
     6	
     7	The original sandboxed patch that introduced this wiring shipped with no
     8	tests at all for it -- these are net-new coverage, not a port of anything
     9	upstream.
    10	"""
    11	import numpy as np
    12	import pytest
    13	
    14	from fitting import (
    15	    _apply_endpoint_averaging,
    16	    compute_background_only,
    17	    shirley_background,
    18	    smart_background,
    19	    smart_experimental_background,
    20	    tougaard_background,
    21	)
    22	
    23	
    24	def _noisy_endpoint_fixture():
    25	    """A spectrum whose single first/last SAMPLE is a noise outlier relative
    26	    to its neighborhood, so endpoint averaging visibly changes the reported
    27	    B_low/B_high and therefore the whole background curve."""
    28	    rng = np.random.default_rng(0)
    29	    x = np.linspace(700.0, 740.0, 200)
    30	    y = 4000.0 + 3000.0 * np.exp(-0.5 * ((x - 720.0) / 4.0) ** 2)
    31	    y = y.copy()
    32	    y[0] += 500.0    # single-point low-BE outlier
    33	    y[-1] -= 500.0   # single-point high-BE outlier
    34	    return x, y
    35	
    36	
    37	def test_shirley_background_default_n_avg_matches_pre_f3_output():
    38	    """n_avg=1 (the default) must reproduce the pre-F3 raw-endpoint
    39	    behaviour byte-for-byte -- this wiring must change no current output."""
    40	    x, y = _noisy_endpoint_fixture()
    41	    assert np.array_equal(shirley_background(x, y), shirley_background(x, y, n_avg=1))
    42	
    43	
    44	def test_shirley_background_n_avg_changes_output_on_noisy_endpoints():
    45	    """n_avg > 1 must actually average the endpoints internally and change
    46	    the result relative to raw endpoints, on a fixture designed so that
    47	    difference is visible."""
    48	    x, y = _noisy_endpoint_fixture()
    49	    raw = shirley_background(x, y, n_avg=1)
    50	    averaged = shirley_background(x, y, n_avg=8)
    51	    assert not np.allclose(raw, averaged), (
    52	        "n_avg=8 produced the same background as n_avg=1 on a fixture with "
    53	        "a deliberate single-point endpoint outlier"
    54	    )
    55	
    56	
    57	def test_shirley_background_n_avg_matches_external_pre_averaging():
    58	    """Calling shirley_background(x, y, n_avg=N) must equal the OLD calling
    59	    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
    60	    so this is a pure convenience wrapper, not a new averaging algorithm."""
    61	    x, y = _noisy_endpoint_fixture()
    62	    for n_avg in (1, 4, 8):
    63	        direct = shirley_background(x, y, n_avg=n_avg)
    64	        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
    65	        assert np.array_equal(direct, pre_averaged), f"mismatch at n_avg={n_avg}"
    66	
    67	
    68	def test_smart_background_default_n_avg_matches_pre_f3_output():
    69	    x, y = _noisy_endpoint_fixture()
    70	    assert np.array_equal(smart_background(x, y), smart_background(x, y, n_avg=1))
    71	
    72	
    73	def test_smart_background_forwards_n_avg_to_shirley():
    74	    """smart_background(x, y, n_avg=N) must equal
    75	    minimum(shirley_background(x, y, n_avg=N), y) -- the clamp applies
    76	    against the RAW data, not an endpoint-averaged copy, so averaging only
    77	    ever moves the background curve, never the reported net counts."""
    78	    x, y = _noisy_endpoint_fixture()
    79	    for n_avg in (1, 4, 8):
    80	        got = smart_background(x, y, n_avg=n_avg)
    81	        expected = np.minimum(shirley_background(x, y, n_avg=n_avg), y)
    82	        assert np.array_equal(got, expected), f"mismatch at n_avg={n_avg}"
    83	
    84	
    85	def test_smart_background_n_avg_changes_output_on_noisy_endpoints():
    86	    x, y = _noisy_endpoint_fixture()
    87	    raw = smart_background(x, y, n_avg=1)
    88	    averaged = smart_background(x, y, n_avg=8)
    89	    assert not np.allclose(raw, averaged)
    90	
    91	
    92	def test_apply_endpoint_averaging_still_importable_and_unchanged():
    93	    """F3 relocates _apply_endpoint_averaging above shirley_background in
    94	    fitting.py's source order; its behaviour must not change."""
    95	    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    96	    out = _apply_endpoint_averaging(y, 2)
    97	    assert np.array_equal(out, np.array([1.5, 1.5, 3.0, 4.0, 5.0, 6.0, 7.5, 7.5]))
    98	
    99	
   100	def test_compute_background_default_endpoint_avg_matches_pre_f3_output():
   101	    """autofit/engine.py's _compute_background(x, y, bg) with no
   102	    endpoint_avg argument must reproduce pre-F3 output exactly, for every
   103	    background type it dispatches -- pure wiring, no behaviour change."""
   104	    from autofit.engine import BackgroundType, _compute_background
   105	
   106	    x, y = _noisy_endpoint_fixture()
   107	    for bg_type in (BackgroundType.SHIRLEY, BackgroundType.SMART,
   108	                    BackgroundType.SMART_EXP, BackgroundType.LINEAR,
   109	                    BackgroundType.TOUGAARD):
   110	        no_arg = _compute_background(x, y, bg_type)
   111	        default_arg = _compute_background(x, y, bg_type, endpoint_avg=1)
   112	        assert np.array_equal(no_arg, default_arg), f"mismatch for {bg_type}"
   113	
   114	
   115	@pytest.mark.parametrize("bg_type_name,direct_fn", [
   116	    ("SHIRLEY", shirley_background),
   117	    ("SMART", smart_background),
   118	    ("SMART_EXP", smart_experimental_background),
   119	    ("TOUGAARD", tougaard_background),
   120	])
   121	def test_compute_background_forwards_endpoint_avg(bg_type_name, direct_fn):
   122	    """_compute_background(x, y, bg, endpoint_avg=N) must match calling the
   123	    underlying fitting.py function directly with n_avg=N -- Find Peaks and
   124	    manual Run Fit must agree once both pass the same endpoint_avg."""
   125	    from autofit.engine import BackgroundType, _compute_background
   126	
   127	    x, y = _noisy_endpoint_fixture()
   128	    bg_type = getattr(BackgroundType, bg_type_name)
   129	    for n_avg in (1, 4, 8):
   130	        via_engine = _compute_background(x, y, bg_type, endpoint_avg=n_avg)
   131	        direct = direct_fn(x, y, n_avg=n_avg)
   132	        assert np.array_equal(via_engine, direct), (
   133	            f"{bg_type_name} mismatch at endpoint_avg={n_avg}"
   134	        )
   135	
   136	
   137	def test_compute_background_linear_ignores_endpoint_avg():
   138	    """linear_background has no endpoint-averaging concept (it already
   139	    reads only the two edge points); endpoint_avg must be accepted without
   140	    error and have no effect."""
   141	    from autofit.engine import BackgroundType, _compute_background
   142	
   143	    x, y = _noisy_endpoint_fixture()
   144	    no_avg = _compute_background(x, y, BackgroundType.LINEAR)
   145	    with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
   146	    assert np.array_equal(no_avg, with_avg)
   147	
   148	
   149	@pytest.mark.parametrize("method", ["shirley", "smart", "tougaard"])
   150	def test_compute_background_only_matches_direct_call_with_n_avg(method):
   151	    """The manual /api/background and /api/fit dispatch (compute_background_only,
   152	    mirrored by run_fit and autofit/parity.py) must produce IDENTICAL output to
   153	    calling the underlying fitting.py function directly with the same n_avg --
   154	    the whole point of F3 is that Find Peaks (via _compute_background) and
   155	    manual Run Fit agree once both pass the same endpoint_avg.
   156	
   157	    This is the parity gap Codex review caught in c5a24ac: smart_background
   158	    has a post-hoc `np.minimum(shir, y)` clamp, so pre-averaging y externally
   159	    (the old convention, still used by compute_background_only/run_fit/
   160	    parity.py before this fix) clamps against the AVERAGED copy, while
   161	    passing n_avg directly (the new engine.py convention) clamps against the
   162	    TRUE raw data -- a real, non-trivial divergence for SMART specifically
   163	    once endpoint_avg > 1 is used (shirley/tougaard have no such post-hoc
   164	    step and were already equivalent either way)."""
   165	    x, y = _noisy_endpoint_fixture()
   166	    direct_fn = {"shirley": shirley_background, "smart": smart_background,
   167	                 "tougaard": tougaard_background}[method]
   168	    for n_avg in (1, 4, 8):
   169	        result = compute_background_only(x, y, method=method, endpoint_avg=n_avg)
   170	        via_dispatch = np.array(result["background"])
   171	        direct = direct_fn(x, y, n_avg=n_avg)
   172	        assert np.allclose(via_dispatch, direct, rtol=1e-9), (
   173	            f"{method} dispatch diverges from direct n_avg={n_avg} call by "
   174	            f"{np.max(np.abs(via_dispatch - direct)):.3f}"
   175	        )

exec
/bin/zsh -lc 'rg -n "_apply_endpoint_averaging" fitting.py autofit/parity.py tests/test_background_n_avg.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/test_background_n_avg.py:15:    _apply_endpoint_averaging,
tests/test_background_n_avg.py:59:    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
tests/test_background_n_avg.py:64:        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
tests/test_background_n_avg.py:92:def test_apply_endpoint_averaging_still_importable_and_unchanged():
tests/test_background_n_avg.py:93:    """F3 relocates _apply_endpoint_averaging above shirley_background in
tests/test_background_n_avg.py:96:    out = _apply_endpoint_averaging(y, 2)
fitting.py:306:def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
fitting.py:337:    array themselves via _apply_endpoint_averaging; that convention was
fitting.py:352:        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)
fitting.py:563:    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
fitting.py:586:        ya = _apply_endpoint_averaging(ya, n_avg)

exec
/bin/zsh -lc "rg -n \"fit-time grid drifted|skip|battery_eligible|U4f|endpointAvg|endpoint_avg|smart\" scripts/gen_u4f_battery_fixture.py autofit -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
scripts/gen_u4f_battery_fixture.py:18:from autofit.parity import battery_eligible, refit_record  # noqa: E402
scripts/gen_u4f_battery_fixture.py:30:    skipped = []
scripts/gen_u4f_battery_fixture.py:33:            ok, reason = battery_eligible(rf, region="U 4f")
scripts/gen_u4f_battery_fixture.py:36:                    skipped.append({"project": rf.project, "name": rf.name,
scripts/gen_u4f_battery_fixture.py:42:        json.dump({"records": records, "skipped": skipped}, f, indent=1, sort_keys=True)
scripts/gen_u4f_battery_fixture.py:43:    print(f"{len(records)} records frozen, {len(skipped)} skipped -> {OUT}")
scripts/gen_u4f_battery_fixture.py:44:    for s in skipped:
scripts/gen_u4f_battery_fixture.py:45:        print(f"  skipped: {s['project']} / {s['name']} — {s['reason']}")
autofit/lint.py:32:an unknown tab plus an unknown key is skipped, not guessed at.
autofit/candidates.py:161:    # oversized scales are skipped for short windows
autofit/reference.py:205:    def endpoint_avg(self) -> int:
autofit/reference.py:207:            return max(1, int(self.ui.get("endpointAvg", 1)))
autofit/engine.py:42:from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background
autofit/engine.py:184:# skipped and the sweep returns best-so-far, ranked normally, with
autofit/engine.py:291:    endpoint_avg: int = 1,
autofit/engine.py:295:    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
autofit/engine.py:299:    to do, leaving Find Peaks unable to express an endpoint_avg the manual
autofit/engine.py:305:        return shirley_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:307:        return smart_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:309:        from fitting import smart_experimental_background
autofit/engine.py:310:        return smart_experimental_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:315:        return tougaard_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:1164:    skipped — not run and not counted as failures — so one candidate stuck
autofit/engine.py:1196:                "after %d/%d refits — remaining refits skipped",
autofit/engine.py:2771:                "skipped, returning best-so-far",
autofit/grammar.py:71:    SMART = "smart"
autofit/grammar.py:72:    SMART_EXP = "smart_exp"      # Avantage-style constrained Shirley
autofit/parity.py:34:    smart_background,
autofit/parity.py:35:    smart_experimental_background,
autofit/parity.py:75:    endpoint_avg: int = 1,
autofit/parity.py:98:        bg_inner = shirley_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:99:    elif m == "smart":
autofit/parity.py:100:        bg_inner = smart_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:101:    elif m == "smart_exp":
autofit/parity.py:102:        bg_inner = smart_experimental_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:104:        bg_inner = shirley_linear_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:106:        bg_inner = tougaard_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:132:def battery_eligible(rf: ReferenceFit, region: str = "C 1s") -> tuple[bool, str]:
autofit/parity.py:150:        return False, "fit-time grid drifted from current ui state"
autofit/parity.py:181:        rf.roi_be, rf.roi_intensity, rf.bg_method, i0, i1, rf.endpoint_avg
autofit/parity.py:200:        endpoint_avg=rf.endpoint_avg,
autofit/methods/least_squares.py:21:    "background_method", "bg_start_idx", "bg_end_idx", "endpoint_avg",
autofit/methods/least_squares.py:57:            endpoint_avg=opts.pop("endpoint_avg", 1),
autofit/regions/b1s.py:51:# Expert practice for this data set (ui.bgType 'smart_exp') — UNVERIFIED
autofit/regions/b1s.py:77:            {"constant": "background", "value": "smart_exp",
autofit/regions/u4f.py:107:# Background: the labeled U 4f fits all use the 'smart' (constrained
autofit/regions/u4f.py:113:class U4fModule:
autofit/regions/u4f.py:156:            {"constant": "background", "value": "smart",
autofit/regions/u4f.py:271:register_region(U4fModule())
autofit/regions/n1s.py:59:            {"constant": "background", "value": "smart",
autofit/regions/cl2p.py:70:# Expert practice for this data set (ui.bgType 'smart_exp') — UNVERIFIED.
autofit/regions/cl2p.py:102:            {"constant": "background", "value": "smart_exp",

codex
The line-by-line trace supports the asymmetry claim: Shirley and Tougaard rebind/use one working `y`, while Smart computes Shirley from one convention and then clamps against the original argument. I’m now deriving the smart plus endpoint averaging population from the `.proj.zip` files directly.
exec
/bin/zsh -lc "nl -ba autofit/parity.py | sed -n '132,210p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '575,650p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   132	def battery_eligible(rf: ReferenceFit, region: str = "C 1s") -> tuple[bool, str]:
   133	    """
   134	    Single source of truth for battery/roster eligibility, shared by the
   135	    fixture generator and the pytest battery so they can never disagree.
   136	
   137	    Returns (eligible, reason-if-not).
   138	    """
   139	    if rf.region_guess() != region:
   140	        return False, f"not {region}"
   141	    fr = rf.fit_result
   142	    if not fr.get("fittedY") or not fr.get("be"):
   143	        return False, "legacy fitResult (no be/fittedY)"
   144	    if len(fr["fittedY"]) != len(fr["be"]):
   145	        return False, (
   146	            f"internally inconsistent fitResult (fittedY {len(fr['fittedY'])} "
   147	            f"pts vs be {len(fr['be'])} pts — stale fittedY from an earlier ROI)"
   148	        )
   149	    if not grid_matches(rf):
   150	        return False, "fit-time grid drifted from current ui state"
   151	    return True, ""
   152	
   153	
   154	def grid_matches(rf: ReferenceFit, tol: float = 1e-3) -> bool:
   155	    """
   156	    True when the saved fit-time grid (``fitResult.be``) equals the ROI grid
   157	    reconstructed from the tab's current ui state.  False means the tab's
   158	    charge correction / ROI moved after the fit (the app shifts ui fields and
   159	    peaks together but keeps ``fitResult`` in the fit-time frame) — those
   160	    tabs are excluded from strict parity and logged instead.
   161	    """
   162	    saved_be = rf.fit_result.get("be")
   163	    if not saved_be:
   164	        return False
   165	    roi = rf.roi_be
   166	    if len(saved_be) != len(roi):
   167	        return False
   168	    return float(np.max(np.abs(np.asarray(saved_be, dtype=float) - roi))) <= tol
   169	
   170	
   171	def eval_parity_relmax(rf: ReferenceFit) -> float:
   172	    """
   173	    Max |python_eval − saved fittedY| / max|fittedY| on the reconstructed
   174	    ROI grid.  Requires ``grid_matches(rf)``.
   175	    """
   176	    fittedY = np.asarray(rf.fit_result["fittedY"], dtype=float)
   177	    specs = rf.backend_peak_specs()
   178	    model = evaluate_model(rf.roi_be, specs)
   179	    i0, i1 = rf.bg_indices()
   180	    bg = background_like_run_fit(
   181	        rf.roi_be, rf.roi_intensity, rf.bg_method, i0, i1, rf.endpoint_avg
   182	    )
   183	    scale = max(float(np.max(np.abs(fittedY))), 1.0)
   184	    return float(np.max(np.abs(model + bg - fittedY)) / scale)
   185	
   186	
   187	def refit_record(rf: ReferenceFit) -> dict[str, Any]:
   188	    """
   189	    Deterministic seeded refit (leastsq, no perturbation) from the saved
   190	    parameters.  Returns a serializable record for fixture freezing.
   191	    """
   192	    i0, i1 = rf.bg_indices()
   193	    res = run_fit(
   194	        rf.roi_be,
   195	        rf.roi_intensity,
   196	        rf.backend_peak_specs(),
   197	        background_method=rf.bg_method,
   198	        bg_start_idx=i0,
   199	        bg_end_idx=i1,
   200	        endpoint_avg=rf.endpoint_avg,
   201	        n_perturb=0,
   202	    )
   203	    peaks = []
   204	    for ip in res["individual_peaks"]:
   205	        par = ip["params"]
   206	        peaks.append({
   207	            "id": ip["id"],
   208	            "center": par["center"]["value"],
   209	            "fwhm": par["fwhm"]["value"],
   210	            "amplitude": par["amplitude"]["value"],

 succeeded in 0ms:
   575	
   576	    # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
   577	    # C = 1643 eV². A long-standing transcription slip shipped C = 1643²
   578	    # (~2.7e6 eV²), which pushed the kernel maximum from ~23 eV to ~949 eV
   579	    # of energy loss and flattened the background to ~zero over any real
   580	    # XPS window. Fixed 2026-07-04 together with the JS twin.
   581	    B_coef, C_coef = 2866.0, 1643.0
   582	
   583	    xa = np.asarray(x, dtype=float)
   584	    ya = np.asarray(y, dtype=float)
   585	    if n_avg > 1:
   586	        ya = _apply_endpoint_averaging(ya, n_avg)
   587	
   588	    # The one-sided loss sum below (j >= i) is physical only when BE
   589	    # DESCENDS along the array: the loss contributions at x[i] must come
   590	    # from lower-BE (higher-KE) emitters, which sit at higher indices only
   591	    # on a descending grid. Normalize to descending internally and flip
   592	    # the result back — the mirror of shirley_background's ascending
   593	    # normalization — so both BE orderings give identical output.
   594	    flipped = bool(xa[0] < xa[-1])
   595	    if flipped:
   596	        xa, ya = xa[::-1].copy(), ya[::-1].copy()
   597	
   598	    # C0: the low-BE edge level = index -1 on the descending working array.
   599	    # This is the out-of-window (pre-loss) baseline; the kernel integral is
   600	    # run on the net above it.
   601	    c0 = float(ya[-1])
   602	    net = ya - c0
   603	
   604	    dx = float(abs(xa[1] - xa[0]))
   605	
   606	    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·net[j]·w[j],  K(T) = B·T / (C + T²)²,
   607	    # w[j] = the local quadrature weight (energy spacing) at point j.
   608	    #
   609	    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx and w[j] == dx, so the
   610	    # kernel depends only on the index gap and this one-sided correlation
   611	    # collapses to a convolution against a single precomputed kernel vector —
   612	    # evaluated in C via np.convolve instead of an n-iteration Python loop
   613	    # (audit F7). On a NONUNIFORM grid neither identity holds, so we keep the
   614	    # exact per-point separation loop AND per-point weights (audit F2,
   615	    # 2026-07-17: the loop previously used exact separations but omitted the
   616	    # spacing weights, silently applying a uniform-grid quadrature inside the
   617	    # branch written precisely because the grid is not uniform — up to ~24%
   618	    # error on a genuinely nonuniform grid). np.gradient returns dx exactly
   619	    # on a uniform grid, so both branches agree to floating point and the
   620	    # uniformity test is a pure optimization, not a semantic fork.
   621	    diffs = np.diff(xa)
   622	    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)
   623	
   624	    if uniform:
   625	        m = np.arange(n, dtype=float)
   626	        T = m * dx
   627	        k = (B_coef * T) / (C_coef + T * T) ** 2          # k[m] = K(m·dx)
   628	        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·net[i+m]  =  conv(net, reverse(k))[n-1+i]
   629	        bg = np.convolve(net, k[::-1])[n - 1:] * dx
   630	    else:
   631	        w = np.abs(np.gradient(xa))
   632	        bg = np.zeros(n)
   633	        for i in range(n):
   634	            T = np.abs(xa[i:] - xa[i])
   635	            kernel = (B_coef * T) / (C_coef + T * T) ** 2
   636	            bg[i] = float(np.sum(kernel * net[i:] * w[i:]))
   637	
   638	    # Amplitude anchor: scale the loss integral so the background equals the
   639	    # measured intensity at the HIGH-BE edge (index 0 on the descending
   640	    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
   641	    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
   642	    # flat or empty window), the honest background is the flat pre-loss level
   643	    # C0 itself, NOT zeros: a featureless window contains no loss signal to
   644	    # model, and returning zeros would report the entire baseline as net
   645	    # signal (the pre-F1 behaviour). Negative counts (physically invalid
   646	    # input) pass through signed; no clamping policy is imposed here.
   647	    if bg[0] == 0.0:
   648	        out = np.full(n, c0)
   649	    else:
   650	        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])

exec
/bin/zsh -lc "nl -ba scripts/gen_u4f_battery_fixture.py | sed -n '1,80p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	#!/usr/bin/env python
     2	"""
     3	Generate tests/autofit/fixtures/u4f_battery_expected.json — frozen
     4	characterization records for the U 4f parity battery (LACX mains + linked
     5	spin-orbit doublet + Voigt satellites through the MANUAL fit path).
     6	
     7	Regenerate ONLY for reviewed, intentional numerics changes:
     8	
     9	    venv/bin/python scripts/gen_u4f_battery_fixture.py
    10	"""
    11	import glob
    12	import json
    13	import os
    14	import sys
    15	
    16	sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    17	
    18	from autofit.parity import battery_eligible, refit_record  # noqa: E402
    19	from autofit.reference import load_reference_fits  # noqa: E402
    20	
    21	DATA = os.path.join(os.path.dirname(__file__), "..", "docs", "autofit", "test_data")
    22	OUT = os.path.join(
    23	    os.path.dirname(__file__), "..", "tests", "autofit", "fixtures",
    24	    "u4f_battery_expected.json",
    25	)
    26	
    27	
    28	def main() -> None:
    29	    records = []
    30	    skipped = []
    31	    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
    32	        for rf in load_reference_fits(zp):
    33	            ok, reason = battery_eligible(rf, region="U 4f")
    34	            if not ok:
    35	                if reason != "not U 4f":
    36	                    skipped.append({"project": rf.project, "name": rf.name,
    37	                                    "reason": reason})
    38	                continue
    39	            records.append(refit_record(rf))
    40	    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    41	    with open(OUT, "w") as f:
    42	        json.dump({"records": records, "skipped": skipped}, f, indent=1, sort_keys=True)
    43	    print(f"{len(records)} records frozen, {len(skipped)} skipped -> {OUT}")
    44	    for s in skipped:
    45	        print(f"  skipped: {s['project']} / {s['name']} — {s['reason']}")
    46	
    47	
    48	if __name__ == "__main__":
    49	    main()

exec
/bin/zsh -lc "rg --files docs/autofit/test_data -g '*.proj.zip'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
docs/autofit/test_data/8-JT Graphite.proj.zip
docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
docs/autofit/test_data/UCl4_on_graphite.proj.zip
docs/autofit/test_data/B4C-UCl4.proj.zip
docs/autofit/test_data/Cl2p_projfit_test.proj.zip

codex
The fixture generator excludes via `battery_eligible`, and that skip reason is exactly in the parity helper. I’m going to use the project loader to enumerate spectra, then cross-check names/methods/endpointAvg and whether each would enter the U4f frozen fixture.
exec
/bin/zsh -lc "nl -ba autofit/reference.py | sed -n '1,260p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	Reference-fit loading for the autofit engine.
     3	
     4	Reads the v3 ``.proj.zip`` / ``.proj.json`` project format (the same format
     5	``templates/index.html`` saves) into plain-Python records, and reconstructs
     6	the exact fit inputs the frontend would send to ``/api/fit``:
     7	
     8	- corrected BE axis  = rawBE + ccShift          (``getCorrectedBE``)
     9	- ROI slice          = corrected BE within [ui.roiMin, ui.roiMax], inclusive
    10	                       (``getROIData``, index.html:4494)
    11	- background indices = nearest ROI-grid index to ui.bgStart / ui.bgEnd
    12	                       (``runFit``, index.html:6575)
    13	- peak specs         = mirror of ``peakToBackendSpec`` (index.html:5708)
    14	
    15	This module is read-only with respect to the app: it imports nothing from
    16	``app.py`` and never mutates project files.
    17	"""
    18	
    19	from __future__ import annotations
    20	
    21	import json
    22	import zipfile
    23	from dataclasses import dataclass, field
    24	from pathlib import Path
    25	from typing import Any, Optional
    26	
    27	import numpy as np
    28	
    29	
    30	# ─────────────────────────────────────────────────────────────────────────────
    31	# Project loading
    32	# ─────────────────────────────────────────────────────────────────────────────
    33	
    34	def load_project_tabs(path: str | Path) -> list[dict]:
    35	    """
    36	    Return the list of raw tab dicts from a ``.proj.zip`` or ``.proj.json``.
    37	
    38	    Zip layout (saved by ``_doSaveProject`` for >= 5 tabs): ``manifest.json``
    39	    with ``{version: 3, spectra: [{index, filename, ...}]}`` plus one
    40	    ``spectrum_<i>_<name>.json`` per tab.  JSON layout (< 5 tabs): a single
    41	    object with ``tabs: [...]``.
    42	    """
    43	    path = Path(path)
    44	    if path.suffix == ".zip" or path.name.endswith(".proj.zip"):
    45	        with zipfile.ZipFile(path) as z:
    46	            manifest = json.loads(z.read("manifest.json"))
    47	            if manifest.get("version") != 3:
    48	                raise ValueError(
    49	                    f"{path.name}: unsupported project version "
    50	                    f"{manifest.get('version')!r} (expected 3)"
    51	                )
    52	            tabs = []
    53	            for entry in manifest.get("spectra", []):
    54	                tabs.append(json.loads(z.read(entry["filename"])))
    55	            return tabs
    56	    data = json.loads(path.read_text())
    57	    if not isinstance(data.get("tabs"), list):
    58	        raise ValueError(f"{path.name}: no 'tabs' array — not a v3 project JSON")
    59	    return data["tabs"]
    60	
    61	
    62	# ─────────────────────────────────────────────────────────────────────────────
    63	# peakToBackendSpec mirror (index.html:5708)
    64	# ─────────────────────────────────────────────────────────────────────────────
    65	
    66	def _finite(v: Any) -> bool:
    67	    """JS Number.isFinite: true only for finite numbers (not None/str/bool)."""
    68	    return isinstance(v, (int, float)) and not isinstance(v, bool) and np.isfinite(v)
    69	
    70	
    71	def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
    72	    """
    73	    Python mirror of the frontend's ``peakToBackendSpec``.
    74	
    75	    ``all_peaks`` is needed for the linked-peak branch (JS resolves the
    76	    parent via ``getPeak(p.linked)`` and silently drops the constraint when
    77	    the parent is missing).
    78	    """
    79	    spec: dict[str, Any] = {
    80	        "id": str(p["id"]),
    81	        "name": p.get("name"),
    82	        "center": p["center"],
    83	        "amplitude": p["amplitude"],
    84	        "fwhm": p["fwhm"],
    85	        "amplitude_min": 0,
    86	        "fix_center": bool(p.get("fixCenter")),
    87	        "fix_fwhm": bool(p.get("fixFwhm")),
    88	        "fix_amplitude": bool(p.get("fixAmplitude")),
    89	        "fix_gl_ratio": bool(p.get("fixGlMix")),
    90	    }
    91	    shape = p.get("shape")
    92	    if shape == "Gaussian":
    93	        spec["shape"] = "gaussian"
    94	    elif shape == "Lorentzian":
    95	        spec["shape"] = "lorentzian"
    96	    elif shape == "Voigt":
    97	        spec["shape"] = "pseudo_voigt_gl"
    98	        spec["gl_ratio"] = 0.3
    99	    elif shape == "GL":
   100	        spec["shape"] = "pseudo_voigt_gl"
   101	        spec["gl_ratio"] = p["glMix"] / 100.0
   102	    elif shape == "asym-GL":
   103	        spec["shape"] = "asymmetric_gl"
   104	        spec["gl_ratio"] = (p.get("glMix") or 50) / 100.0
   105	        spec["asymmetry"] = p.get("asymmetry") or 0
   106	        spec["fix_asymmetry"] = bool(p.get("fixAsymmetry"))
   107	        if _finite(p.get("_afAsymMin")):
   108	            spec["asymmetry_min"] = p["_afAsymMin"]
   109	        if _finite(p.get("_afAsymMax")):
   110	            spec["asymmetry_max"] = p["_afAsymMax"]
   111	    elif shape == "DS":
   112	        spec["shape"] = "doniach_sunjic"
   113	        spec["alpha"] = p.get("dsAlpha") or 0.1
   114	        spec["gamma_asym"] = p.get("dsGamma") or 0.0
   115	        spec["fix_alpha"] = bool(p.get("fixDsAlpha"))
   116	        spec["fix_gamma_asym"] = bool(p.get("fixDsGamma"))
   117	    elif shape == "DSG_LA":
   118	        spec["shape"] = "ds_g"
   119	        spec["alpha"] = p["laAlpha"] if _finite(p.get("laAlpha")) else 0.10
   120	        spec["beta"] = p["laBeta"] if _finite(p.get("laBeta")) else 0.3
   121	        spec["m_gauss"] = p["laM"] if _finite(p.get("laM")) else 0.4
   122	        spec["fix_alpha"] = bool(p.get("fixLaAlpha"))
   123	        spec["fix_beta"] = bool(p.get("fixLaBeta"))
   124	        spec["fix_m_gauss"] = bool(p.get("fixLaM"))
   125	    elif shape == "LACX":
   126	        spec["shape"] = "la_casaxps"
   127	        spec["alpha"] = p["caAlpha"] if _finite(p.get("caAlpha")) else 1.0
   128	        spec["beta"] = p["caBeta"] if _finite(p.get("caBeta")) else 1.0
   129	        spec["m"] = p["caM"] if _finite(p.get("caM")) else 50.0
   130	        spec["fix_alpha"] = bool(p.get("fixCaAlpha"))
   131	        spec["fix_beta"] = bool(p.get("fixCaBeta"))
   132	        spec["fix_m"] = bool(p.get("fixCaM"))
   133	    else:
   134	        spec["shape"] = "gaussian"
   135	
   136	    if p.get("linked"):
   137	        parent = next((q for q in all_peaks if q.get("id") == p["linked"]), None)
   138	        if parent is not None:
   139	            spec["constrain_to"] = str(p["linked"])
   140	            spec["splitting"] = p.get("linkOffset")
   141	            spec["area_ratio"] = p.get("linkRatio")
   142	            spec["fix_fwhm"] = True
   143	    return spec
   144	
   145	
   146	# ─────────────────────────────────────────────────────────────────────────────
   147	# ReferenceFit — one saved, fitted spectrum tab
   148	# ─────────────────────────────────────────────────────────────────────────────
   149	
   150	@dataclass
   151	class ReferenceFit:
   152	    """A saved spectrum tab with a fit, plus reconstructed fit inputs."""
   153	
   154	    project: str                 # source project filename
   155	    tab_file: str                # spectrum_*.json name (or index for .proj.json)
   156	    name: str
   157	    raw_be: np.ndarray
   158	    raw_intensity: np.ndarray
   159	    cc_shift: float
   160	    peaks: list[dict]
   161	    fit_result: dict
   162	    ui: dict = field(default_factory=dict)
   163	
   164	    # ── frontend-semantics reconstructions ──────────────────────────────────
   165	
   166	    @property
   167	    def corrected_be(self) -> np.ndarray:
   168	        # getCorrectedBE (index.html:4486): corrected = rawBE − ccShift
   169	        # (ccShift = observed − literature, so the applied shift is −ccShift).
   170	        return self.raw_be - self.cc_shift
   171	
   172	    def _roi_bounds(self) -> tuple[float, float]:
   173	        lo = _parse_float(self.ui.get("roiMin"), -np.inf)
   174	        hi = _parse_float(self.ui.get("roiMax"), np.inf)
   175	        return lo, hi
   176	
   177	    @property
   178	    def roi_mask(self) -> np.ndarray:
   179	        lo, hi = self._roi_bounds()
   180	        c = self.corrected_be
   181	        return (c >= lo) & (c <= hi)
   182	
   183	    @property
   184	    def roi_be(self) -> np.ndarray:
   185	        return self.corrected_be[self.roi_mask]
   186	
   187	    @property
   188	    def roi_intensity(self) -> np.ndarray:
   189	        return self.raw_intensity[self.roi_mask]
   190	
   191	    def bg_indices(self) -> tuple[int, int]:
   192	        """Nearest ROI-grid indices to ui.bgStart / ui.bgEnd (index.html:6575)."""
   193	        be = self.roi_be
   194	        bg_start = _parse_float(self.ui.get("bgStart"), be[0] if len(be) else 0.0)
   195	        bg_end = _parse_float(self.ui.get("bgEnd"), be[-1] if len(be) else 0.0)
   196	        i_start = int(np.argmin(np.abs(be - bg_start)))
   197	        i_end = int(np.argmin(np.abs(be - bg_end)))
   198	        return i_start, i_end
   199	
   200	    @property
   201	    def bg_method(self) -> str:
   202	        return self.ui.get("bgType") or "shirley"
   203	
   204	    @property
   205	    def endpoint_avg(self) -> int:
   206	        try:
   207	            return max(1, int(self.ui.get("endpointAvg", 1)))
   208	        except (TypeError, ValueError):
   209	            return 1
   210	
   211	    def backend_peak_specs(self) -> list[dict]:
   212	        return [peak_to_backend_spec(p, self.peaks) for p in self.peaks]
   213	
   214	    @property
   215	    def region_midpoint(self) -> Optional[float]:
   216	        lo, hi = self._roi_bounds()
   217	        if np.isfinite(lo) and np.isfinite(hi):
   218	            return 0.5 * (lo + hi)
   219	        be = self.corrected_be
   220	        return 0.5 * (float(be.min()) + float(be.max())) if len(be) else None
   221	
   222	    def region_guess(self) -> str:
   223	        """Coarse region label from the ROI midpoint (mirrors isC1sTab logic)."""
   224	        mid = self.region_midpoint
   225	        if mid is None:
   226	            return "unknown"
   227	        for label, lo, hi in _REGION_WINDOWS:
   228	            if lo <= mid <= hi:
   229	                return label
   230	        return "unknown"
   231	
   232	
   233	# Coarse corrected-BE midpoint windows for region labeling of the reference
   234	# data.  These are bookkeeping bins for test selection only — NOT physics
   235	# constants (the engine's physical BE windows live in the region modules and
   236	# are lit-cited there).
   237	_REGION_WINDOWS = [
   238	    ("C 1s", 270.0, 315.0),      # matches isC1sTab (index.html:6548)
   239	    ("B 1s", 178.0, 194.0),      # B 1s scans in the data set center ~186–191
   240	    ("Cl 2p", 194.0, 210.0),
   241	    ("N 1s", 390.0, 410.0),      # narrow N 1s scans center ~398; U 4f scans
   242	    ("U 4f", 370.0, 415.0),      # span ~35 eV so their midpoint lands ~387
   243	]
   244	
   245	
   246	def _parse_float(v: Any, default: float) -> float:
   247	    try:
   248	        f = float(v)
   249	        return f if np.isfinite(f) else default
   250	    except (TypeError, ValueError):
   251	        return default
   252	
   253	
   254	def load_reference_fits(path: str | Path) -> list[ReferenceFit]:
   255	    """All fitted spectrum tabs (>=1 peak, has rawBE + fitResult) in a project."""
   256	    path = Path(path)
   257	    out: list[ReferenceFit] = []
   258	    for i, t in enumerate(load_project_tabs(path)):
   259	        if t.get("isStack"):
   260	            continue

exec
/bin/zsh -lc 'venv/bin/python scripts/gen_u4f_battery_fixture.py' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: no such file or directory: venv/bin/python

codex
The repo-specific `venv/bin/python` referenced by the generator is not present here, and shell here-docs cannot create temp files under this read-only sandbox. I’ll switch to `python3 -c` one-liners for read-only verification.
exec
/bin/zsh -lc 'python3 --version' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-biAa2vH2' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-kHRDadeM' (errno=Operation not permitted)
Python 3.9.6

exec
/bin/zsh -lc "nl -ba autofit/reference.py | sed -n '254,330p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   254	def load_reference_fits(path: str | Path) -> list[ReferenceFit]:
   255	    """All fitted spectrum tabs (>=1 peak, has rawBE + fitResult) in a project."""
   256	    path = Path(path)
   257	    out: list[ReferenceFit] = []
   258	    for i, t in enumerate(load_project_tabs(path)):
   259	        if t.get("isStack"):
   260	            continue
   261	        raw_be = t.get("rawBE") or []
   262	        peaks = t.get("peaks") or []
   263	        fr = t.get("fitResult")
   264	        if not raw_be or not peaks or not fr:
   265	            continue
   266	        out.append(ReferenceFit(
   267	            project=path.name,
   268	            tab_file=f"tab_{i}" if not t.get("name") else t["name"],
   269	            name=t.get("name", f"tab_{i}"),
   270	            raw_be=np.asarray(raw_be, dtype=float),
   271	            raw_intensity=np.asarray(t.get("rawIntensity"), dtype=float),
   272	            cc_shift=float(t.get("ccShift") or 0.0),
   273	            peaks=peaks,
   274	            fit_result=fr,
   275	            ui=t.get("ui") or {},
   276	        ))
   277	    return out

exec
/bin/zsh -lc 'ls -la' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
total 560
drwxr-xr-x   29 skyefortier  staff    928 Jul 17 16:38 .
drwxr-xr-x+  74 skyefortier  staff   2368 Jul 17 17:24 ..
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
drwxr-xr-x    7 skyefortier  staff    224 Jul 17 16:38 __pycache__
-rw-r--r--    1 skyefortier  staff  52614 Jul 13 11:59 app.py
drwxr-xr-x   20 skyefortier  staff    640 Jul 17 16:39 autofit
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 data
drwxr-xr-x    6 skyefortier  staff    192 Jul 10 15:28 docs
-rw-r--r--    1 skyefortier  staff  56830 Jul 17 16:38 fitting.py
-rw-r--r--    1 skyefortier  staff  19994 Jul 10 15:28 parser.py
-rw-r--r--    1 skyefortier  staff    319 Jul 10 15:28 requirements-dev.txt
-rw-r--r--    1 skyefortier  staff    446 Jul 10 15:28 requirements.txt
drwxr-xr-x   22 skyefortier  staff    704 Jul 10 21:01 scripts
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 static
drwxr-xr-x    4 skyefortier  staff    128 Jul 17 15:30 templates
drwxr-xr-x   39 skyefortier  staff   1248 Jul 17 16:37 tests
drwxr-xr-x  163 skyefortier  staff   5216 Jul 17 17:15 uploads
-rw-r--r--    1 skyefortier  staff   6062 Jul 10 15:28 vgd_parser.py
-rw-r--r--    1 skyefortier  staff  68252 Jul 10 15:28 xps-fitting-tool.html
-rw-r--r--    1 skyefortier  staff  18124 Jul 10 15:28 xps_reference.py

codex
I’m also going to diff the pre-commit fixture from `git show` in-memory against the checked-out fixture. That avoids creating temporary files and lets me compute relative field deltas record-by-record.
exec
/bin/zsh -lc 'git diff-tree --no-commit-id --name-only -r 3cd6aad' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7loZ3cTS' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xCsiTNtX' (errno=Operation not permitted)
autofit/parity.py
fitting.py
tests/autofit/fixtures/u4f_battery_expected.json
tests/test_background_n_avg.py

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import glob, os\\nfrom autofit.reference import load_reference_fits\\nfrom autofit.parity import battery_eligible, grid_matches\\nrows=[]; smart=[]\\nfor zp in sorted(glob.glob(os.path.join(\"docs/autofit/test_data\",\"*.proj.zip\"))):\\n    for rf in load_reference_fits(zp):\\n        bg=(rf.bg_method or \"\").lower(); ep=rf.endpoint_avg\\n        if bg==\"smart\": smart.append((rf.project, rf.name, rf.region_guess(), ep, battery_eligible(rf, region=\"U 4f\")))\\n        if bg==\"smart\" and ep>1:\\n            frbe=rf.fit_result.get(\"be\") or []\\n            gm = grid_matches(rf) if (frbe and len(frbe)==len(rf.roi_be)) else None\\n            rows.append((rf.project, rf.name, rf.region_guess(), ep, battery_eligible(rf, region=\"U 4f\"), len(frbe), len(rf.roi_be), gm))\\nprint(\"smart total\", len(smart))\\nfor r in smart: print(\"SMART\", r)\\nprint(\"smart endpoint>1 count\", len(rows))\\nfor r in rows: print(\"SMART_EP_GT1\", r)'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import json, subprocess, math\\npath=\"tests/autofit/fixtures/u4f_battery_expected.json\"\\nold=json.loads(subprocess.check_output([\"git\",\"show\",\"3cd6aad"'^:"+path]))'"\\ncur=json.load(open(path))\\ndef key(r): return (r.get(\"project\"), r.get(\"name\"))\\nold_records={key(r):r for r in old[\"records\"]}; cur_records={key(r):r for r in cur[\"records\"]}\\nprint(\"record counts\", len(old_records), len(cur_records), \"same_keys\", set(old_records)==set(cur_records))\\nprint(\"skipped equal\", old.get(\"skipped\")==cur.get(\"skipped\"), old.get(\"skipped\"), cur.get(\"skipped\"))\\nmeaningful=[]; tiny=[]\\ndef scalars(obj,prefix=\"\"):\\n    out={}\\n    if isinstance(obj,dict):\\n        for k,v in obj.items(): out.update(scalars(v, prefix+\"/\"+str(k)))\\n    elif isinstance(obj,list):\\n        for i,v in enumerate(obj): out.update(scalars(v, prefix+\"/\"+str(i)))\\n    elif isinstance(obj,(int,float)) and not isinstance(obj,bool):\\n        out[prefix]=float(obj)\\n    else:\\n        out[prefix]=obj\\n    return out\\nfor k in sorted(old_records):\\n    a=scalars(old_records[k]); b=scalars(cur_records[k]); diffs=[]; maxrel=0.0; maxabs=0.0\\n    for f in sorted(set(a)|set(b)):\\n        av=a.get(f); bv=b.get(f)\\n        if isinstance(av,float) and isinstance(bv,float):\\n            absd=abs(bv-av); denom=max(abs(av),abs(bv),1.0); rel=absd/denom\\n            if absd: diffs.append((rel,absd,f,av,bv)); maxrel=max(maxrel,rel); maxabs=max(maxabs,absd)\\n        elif av"'!=bv:'"\\n            diffs.append((float(\"inf\"),float(\"inf\"),f,av,bv)); maxrel=float(\"inf\"); maxabs=float(\"inf\")\\n    if diffs:\\n        target = meaningful if maxrel>1e-6 else tiny\\n        target.append((k,maxrel,maxabs,sorted(diffs, reverse=True)[:5]))\\nprint(\"changed records\", len(meaningful)+len(tiny), \"meaningful\", len(meaningful), \"tiny\", len(tiny))\\nfor label, arr in ((\"MEANINGFUL\",meaningful),(\"TINY\",tiny)):\\n    for k,maxrel,maxabs,top in arr:\\n        print(label, k, \"maxrel\", \"%.12g\"%maxrel, \"maxabs\", \"%.12g\"%maxabs)\\n        for d in top: print(\"  \", \"rel=%.12g abs=%.12g field=%s old=%r new=%r\"%(d[0],d[1],d[2],d[3],d[4]))'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-SEwHrYDd' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-99cMJq2x' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JJEtDSZS' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-wte57EAS' (errno=Operation not permitted)
record counts 29 29 same_keys True
skipped equal True [{'name': 'U4f Scan_0', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_1', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_2', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_3', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_4', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_7', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_8', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_0', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_1', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_2', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_3', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_4', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_5', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_0', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_1', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_2', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_3', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_4', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_5', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan', 'project': 'UCl4_on_graphite.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_1', 'project': 'UCl4_on_graphite.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_2', 'project': 'UCl4_on_graphite.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_4', 'project': 'UCl4_on_graphite.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}] [{'name': 'U4f Scan_0', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_1', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_2', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_3', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_4', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_7', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_8', 'project': '4-GTA UCl4-BN.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_0', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_1', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_2', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_3', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_4', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_5', 'project': 'Cl2p_projfit_test.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_0', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_1', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_2', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_3', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_4', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan_5', 'project': 'Project9_CasaXPS_newfit.proj.zip', 'reason': 'legacy fitResult (no be/fittedY)'}, {'name': 'U4f Scan', 'project': 'UCl4_on_graphite.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_1', 'project': 'UCl4_on_graphite.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_2', 'project': 'UCl4_on_graphite.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}, {'name': 'U4f Scan_4', 'project': 'UCl4_on_graphite.proj.zip', 'reason': 'fit-time grid drifted from current ui state'}]
changed records 2 meaningful 1 tiny 1
MEANINGFUL ('4-GTA UCl4-BN.proj.zip', 'U4f Scan') maxrel 0.0103976631857 maxabs 22.605723868
   rel=0.0103976631857 abs=0.118531648138 field=/reduced_chi_square old=11.399835330377146 new=11.281303682238963
   rel=0.00336712075545 abs=22.605723868 field=/peaks/2/area old=-6691.060197214448 new=-6713.665921082466
   rel=0.00296117497989 abs=14.5164208767 field=/peaks/3/area old=-4887.733859924222 new=-4902.250280800907
   rel=0.000713014191464 abs=15.5993656692 field=/peaks/0/area old=-21878.05776656253 new=-21862.45840089331
   rel=0.000698102215055 abs=11.1740563823 field=/peaks/1/area old=-16006.332799581052 new=-15995.158743198761
TINY ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_5') maxrel 1.48772332959e-12 maxabs 4.38012648374e-09
   rel=1.48772332959e-12 abs=3.41771055901e-12 field=/peaks/1/fwhm old=2.2972756365480214 new=2.297275636551439
   rel=1.48772332959e-12 abs=3.41771055901e-12 field=/peaks/0/fwhm old=2.2972756365480214 new=2.297275636551439
   rel=1.27913941127e-12 abs=4.57323068304e-12 field=/peaks/3/fwhm old=3.5752402300579225 new=3.5752402300533492
   rel=1.27913941127e-12 abs=4.57323068304e-12 field=/peaks/2/fwhm old=3.5752402300579225 new=3.5752402300533492
   rel=6.59689034497e-13 abs=3.73347575078e-09 field=/peaks/2/area old=-5659.447945233339 new=-5659.4479452296055

 exited 1 in 220ms:
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/Users/skyefortier/xps-verify/autofit/parity.py", line 29, in <module>
    from fitting import (
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

codex
`lmfit` is not installed in this environment, so I cannot import `autofit.parity` or run pytest here. For the corpus count I don’t need lmfit; I’ll use `autofit.reference` plus a local copy of the simple eligibility predicates.
exec
/bin/zsh -lc 'git show --name-status --stat 3cd6aad' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1YtqYbBx' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9vSUh2nB' (errno=Operation not permitted)
commit 3cd6aad633be0f80bfd3bc94a4c91fe60f8cef64
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Fri Jul 17 17:26:08 2026 -0600

    fix(fitting): unify remaining shirley/smart/tougaard call sites onto n_avg (F3 cont.)
    
    Codex review of c5a24ac (n_avg convention unification) caught a real bug
    beyond the original patch's scope, independently on both round-1 runs:
    smart_background's post-hoc `np.minimum(shir, y)` clamp reads whatever y
    it's given. run_fit, compute_background_only, and autofit/parity.py's
    mirror all still called it as smart_background(x, _apply_endpoint_averaging(y,
    endpoint_avg)) — the old external-pre-averaging convention — so the clamp
    landed against the AVERAGED copy. The new engine.py path
    (_compute_background -> smart_background(x, y, n_avg=N)) clamps against
    the TRUE raw data. These diverge once endpoint_avg > 1, defeating F3's
    entire point: Find Peaks and manual Run Fit would disagree on SMART
    backgrounds for the same knob value. Independently reproduced (own probe
    matched Codex's ~437-count divergence) before acting on it.
    
    Fix: migrate all 6 remaining call sites (3 in run_fit, 3 in
    compute_background_only, mirrored in autofit/parity.py) from external
    pre-averaging to the same direct n_avg convention already used by
    smart_experimental_background / shirley_linear_background. shirley_background
    and tougaard_background are mathematically invariant to which convention
    is used — both read only the (possibly pre-averaged) array handed to them,
    with no second reference back to "true raw" — so this is a no-op for
    those two (proven by the existing test suite: they already passed the
    manual-vs-direct equivalence check). smart_background is the only one
    with a second raw-data reference, hence the only one that actually
    changes. Removed autofit/parity.py's now-unused _apply_endpoint_averaging
    import.
    
    New test: test_compute_background_only_matches_direct_call_with_n_avg,
    parametrized over shirley/smart/tougaard. Red confirmed first (fails only
    for smart, as expected — shirley/tougaard already passed); green after.
    
    Consequence, surfaced to and approved by Skye before implementing (the
    patch replaces rather than merely wires, and touches a real saved
    reference fit's frozen numbers — the same class of judgment call flagged
    for F1): one real fixture record changes. "U4f Scan" in
    docs/autofit/test_data/4-GTA UCl4-BN.proj.zip uses smart background with
    endpointAvg=6 — the exact combination this bug affects. Regenerated
    tests/autofit/fixtures/u4f_battery_expected.json via its committed
    generator (scripts/gen_u4f_battery_fixture.py); diffed before/after and
    confirmed only that one record changed meaningfully (reduced_chi_square
    11.399835330377146 -> 11.281303682238963, ~1.04% improvement — clamping
    against true raw data is physically the more correct reference, consistent
    with the improved fit). Every other record in the fixture differs by
    <1e-6 relative (ordinary lmfit refit floating-point noise, not this
    change). Grepped every *.proj.zip under docs/autofit/test_data/: only 3
    spectra anywhere use smart+endpoint_avg>1, 2 of which the generator
    already skips for an unrelated pre-existing reason ("fit-time grid
    drifted from current ui state"), leaving exactly this one affected
    record.
    
    Verified: tests/test_background_n_avg.py (16/16), tests/test_tougaard_background.py,
    and the C1s/U4f/B1s-Cl2p parity batteries (159 total) all green. Full
    suite: 681 passed, 6 skipped, 1 failed (test_u4f_n1s_cofit — a
    pre-existing timing/hash-seed-sensitive flake, confirmed byte-identical
    to a failure already independently ruled out earlier in this effort via
    git-stash A/B testing; it does not reproduce on every run, including the
    gated rerun below). RUN_AUTOFIT_GATE=1 real-data gate suite: 11 passed,
    1 failed (test_candidate_pool_real_gate.py's ds8 timing-budget flake,
    also previously confirmed pre-existing and unrelated) — test_u4f_n1s_cofit
    passed on this run, consistent with known flakiness in both directions,
    not a regression.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

M	autofit/parity.py
M	fitting.py
M	tests/autofit/fixtures/u4f_battery_expected.json
M	tests/test_background_n_avg.py

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import glob, os\\nfrom autofit.reference import load_project_tabs\\nfor zp in sorted(glob.glob(os.path.join(\"docs/autofit/test_data\",\"*.proj.zip\"))):\\n    for t in load_project_tabs(zp):\\n        ui=t.get(\"ui\") or {}; bg=(ui.get(\"bgType\") or \"shirley\").lower()\\n        try: ep=max(1,int(ui.get(\"endpointAvg\",1)))\\n        except Exception: ep=1\\n        if bg==\"smart\" and ep>1:\\n            print(os.path.basename(zp), t.get(\"name\"), \"bg\", bg, \"endpointAvg\", ep, \"rawBE\", len(t.get(\"rawBE\") or []), \"peaks\", len(t.get(\"peaks\") or []), \"hasFit\", bool(t.get(\"fitResult\")))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import glob, os, numpy as np\\nfrom autofit.reference import load_reference_fits\\ndef grid_matches(rf,tol=1e-3):\\n    saved=rf.fit_result.get(\"be\")\\n    if not saved: return False\\n    roi=rf.roi_be\\n    if len(saved)"'!=len(roi): return False'"\\n    return float(np.max(np.abs(np.asarray(saved,dtype=float)-roi))) <= tol\\ndef eligible(rf,region=\"U 4f\"):\\n    if rf.region_guess()"'!=region: return (False,"not "+region)'"\\n    fr=rf.fit_result\\n    if not fr.get(\"fittedY\") or not fr.get(\"be\"): return (False,\"legacy fitResult (no be/fittedY)\")\\n    if len(fr[\"fittedY\"]) "'!= len(fr["be"]): return (False, f"internally inconsistent fitResult (fittedY {len(fr['"\\'fittedY\\'])} pts vs be {len(fr[\\'be\\'])} pts - stale fittedY from an earlier ROI)\")\\n    if not grid_matches(rf): return (False,\"fit-time grid drifted from current ui state\")\\n    return (True,\"\")\\nrows=[]; smart=[]; skipped=[]\\nfor zp in sorted(glob.glob(os.path.join(\"docs/autofit/test_data\",\"*.proj.zip\"))):\\n    for rf in load_reference_fits(zp):\\n        bg=(rf.bg_method or \"\").lower(); ep=rf.endpoint_avg\\n        if bg==\"smart\": smart.append((rf.project, rf.name, rf.region_guess(), ep, eligible(rf,\"U 4f\")))\\n        if bg==\"smart\" and ep>1:\\n            frbe=rf.fit_result.get(\"be\") or []\\n            rows.append((rf.project, rf.name, rf.region_guess(), ep, eligible(rf,\"U 4f\"), len(frbe), len(rf.roi_be), grid_matches(rf)))\\n        ok, reason = eligible(rf,\"U 4f\")\\n        if not ok and reason "'!= "not U 4f": skipped.append((rf.project,rf.name,reason))'"\\nprint(\"smart total\", len(smart))\\nfor r in smart: print(\"SMART\", r)\\nprint(\"smart endpoint>1 count\", len(rows))\\nfor r in rows: print(\"SMART_EP_GT1\", r)\\nprint(\"u4f generator-style skipped\", len(skipped))\\nfor s in skipped: print(\"SKIP\", s)'" in /Users/skyefortier/xps-verify
 succeeded in 220ms:
4-GTA UCl4-BN.proj.zip U4f Scan bg smart endpointAvg 6 rawBE 351 peaks 5 hasFit True
4-GTA UCl4-BN.proj.zip U4f Scan_0 bg smart endpointAvg 6 rawBE 351 peaks 5 hasFit True
4-GTA UCl4-BN.proj.zip U4f Scan_3 bg smart endpointAvg 2 rawBE 351 peaks 5 hasFit True

 succeeded in 228ms:
smart total 65
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_0', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_1', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_2', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_3', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_4', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_5', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_6', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_7', 'U 4f', 1, (True, ''))
SMART ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_8', 'U 4f', 1, (True, ''))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan', 'U 4f', 6, (True, ''))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_0', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_0', 'U 4f', 6, (False, 'fit-time grid drifted from current ui state'))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_1', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_1', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_2', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_2', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_3', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_3', 'U 4f', 2, (False, 'fit-time grid drifted from current ui state'))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_4', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_4', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_5', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_5', 'U 4f', 1, (True, ''))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_6', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_6', 'U 4f', 1, (True, ''))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_7', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_7', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('4-GTA UCl4-BN.proj.zip', 'B1s Scan_8', 'B 1s', 1, (False, 'not U 4f'))
SMART ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_8', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('8-JT Graphite.proj.zip', 'C1s Scan_7', 'C 1s', 1, (False, 'not U 4f'))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_0', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_1', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_2', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_3', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_4', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_5', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_6', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_7', 'U 4f', 1, (True, ''))
SMART ('B4C-UCl4.proj.zip', 'U4f Scan_8', 'U 4f', 1, (True, ''))
SMART ('Cl2p_projfit_test.proj.zip', 'U4f Scan', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Cl2p_projfit_test.proj.zip', 'U4f Scan_0', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Cl2p_projfit_test.proj.zip', 'U4f Scan_1', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Cl2p_projfit_test.proj.zip', 'U4f Scan_2', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Cl2p_projfit_test.proj.zip', 'U4f Scan_3', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Cl2p_projfit_test.proj.zip', 'U4f Scan_4', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Cl2p_projfit_test.proj.zip', 'U4f Scan_5', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_0', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_1', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_2', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_3', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_4', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_5', 'U 4f', 1, (False, 'legacy fitResult (no be/fittedY)'))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_0', 'U 4f', 1, (True, ''))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_1', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_2', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_3', 'U 4f', 1, (True, ''))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_4', 'U 4f', 1, (False, 'fit-time grid drifted from current ui state'))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_5', 'U 4f', 1, (True, ''))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_6', 'U 4f', 1, (True, ''))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_7', 'U 4f', 1, (True, ''))
SMART ('UCl4_on_graphite.proj.zip', 'U4f Scan_8', 'U 4f', 1, (True, ''))
smart endpoint>1 count 3
SMART_EP_GT1 ('4-GTA UCl4-BN.proj.zip', 'U4f Scan', 'U 4f', 6, (True, ''), 326, 326, True)
SMART_EP_GT1 ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_0', 'U 4f', 6, (False, 'fit-time grid drifted from current ui state'), 326, 326, False)
SMART_EP_GT1 ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_3', 'U 4f', 2, (False, 'fit-time grid drifted from current ui state'), 327, 327, False)
u4f generator-style skipped 25
SKIP ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_0', 'fit-time grid drifted from current ui state')
SKIP ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_1', 'fit-time grid drifted from current ui state')
SKIP ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_2', 'fit-time grid drifted from current ui state')
SKIP ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_3', 'fit-time grid drifted from current ui state')
SKIP ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_4', 'fit-time grid drifted from current ui state')
SKIP ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_7', 'fit-time grid drifted from current ui state')
SKIP ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_8', 'fit-time grid drifted from current ui state')
SKIP ('Cl2p_projfit_test.proj.zip', 'U4f Scan', 'legacy fitResult (no be/fittedY)')
SKIP ('Cl2p_projfit_test.proj.zip', 'U4f Scan_0', 'legacy fitResult (no be/fittedY)')
SKIP ('Cl2p_projfit_test.proj.zip', 'U4f Scan_1', 'legacy fitResult (no be/fittedY)')
SKIP ('Cl2p_projfit_test.proj.zip', 'U4f Scan_2', 'legacy fitResult (no be/fittedY)')
SKIP ('Cl2p_projfit_test.proj.zip', 'U4f Scan_3', 'legacy fitResult (no be/fittedY)')
SKIP ('Cl2p_projfit_test.proj.zip', 'U4f Scan_4', 'legacy fitResult (no be/fittedY)')
SKIP ('Cl2p_projfit_test.proj.zip', 'U4f Scan_5', 'legacy fitResult (no be/fittedY)')
SKIP ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan', 'legacy fitResult (no be/fittedY)')
SKIP ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_0', 'legacy fitResult (no be/fittedY)')
SKIP ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_1', 'legacy fitResult (no be/fittedY)')
SKIP ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_2', 'legacy fitResult (no be/fittedY)')
SKIP ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_3', 'legacy fitResult (no be/fittedY)')
SKIP ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_4', 'legacy fitResult (no be/fittedY)')
SKIP ('Project9_CasaXPS_newfit.proj.zip', 'U4f Scan_5', 'legacy fitResult (no be/fittedY)')
SKIP ('UCl4_on_graphite.proj.zip', 'U4f Scan', 'fit-time grid drifted from current ui state')
SKIP ('UCl4_on_graphite.proj.zip', 'U4f Scan_1', 'fit-time grid drifted from current ui state')
SKIP ('UCl4_on_graphite.proj.zip', 'U4f Scan_2', 'fit-time grid drifted from current ui state')
SKIP ('UCl4_on_graphite.proj.zip', 'U4f Scan_4', 'fit-time grid drifted from current ui state')

codex
The corpus count now matches the commit claim: exactly three smart spectra have `endpointAvg > 1`, and only one is eligible for the U4f fixture. I’m going to exercise the new test’s core condition directly with a fake `lmfit` module, since the background functions don’t need lmfit but `fitting.py` imports it at module import time.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types\\nlmfit=types.ModuleType(\"lmfit\"); lmfit.Model=object; lmfit.Parameters=dict; sys.modules[\"lmfit\"]=lmfit\\nimport numpy as np\\nfrom fitting import _apply_endpoint_averaging, shirley_background, smart_background, tougaard_background, compute_background_only\\nx=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.0; y[-1]-=500.0\\nfor method,fn in [(\"shirley\",shirley_background),(\"smart\",smart_background),(\"tougaard\",tougaard_background)]:\\n    for n in (1,4,8):\\n        result=np.array(compute_background_only(x,y,method=method,endpoint_avg=n)[\"background\"])\\n        direct=fn(x,y,n_avg=n)\\n        print(\"current\",method,n,\"maxabs\",float(np.max(np.abs(result-direct))),\"allclose1e-9\",bool(np.allclose(result,direct,rtol=1e-9)))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types\\nlmfit=types.ModuleType(\"lmfit\"); lmfit.Model=object; lmfit.Parameters=dict; sys.modules[\"lmfit\"]=lmfit\\nimport numpy as np\\nfrom fitting import _apply_endpoint_averaging, shirley_background, smart_background, tougaard_background\\nx=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.0; y[-1]-=500.0\\nfor method,fn in [(\"shirley\",shirley_background),(\"smart\",smart_background),(\"tougaard\",tougaard_background)]:\\n    for n in (1,4,8):\\n        old=fn(x,_apply_endpoint_averaging(y,n))\\n        direct=fn(x,y,n_avg=n)\\n        print(method,n,\"maxabs\",float(np.max(np.abs(old-direct))),\"allclose1e-9\",bool(np.allclose(old,direct,rtol=1e-9,atol=1e-12)))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'rg -n "_apply_endpoint_averaging" autofit/parity.py' in /Users/skyefortier/xps-verify
 exited 1 in 0ms:
 exited 1 in 117ms:
Traceback (most recent call last):
  File "<string>", line 4, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 31, in <module>
    from scipy.integrate import trapezoid
ModuleNotFoundError: No module named 'scipy'

 exited 1 in 116ms:
Traceback (most recent call last):
  File "<string>", line 4, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 31, in <module>
    from scipy.integrate import trapezoid
ModuleNotFoundError: No module named 'scipy'

codex
This Python environment is missing both `lmfit` and `scipy`; I’ll stub `scipy.integrate.trapezoid` too. That still exercises the repository’s background code unchanged.
exec
/bin/zsh -lc "git show 3cd6aad -- tests/test_background_n_avg.py | sed -n '1,160p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fdTGA3SN' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-a19W5J7e' (errno=Operation not permitted)
commit 3cd6aad633be0f80bfd3bc94a4c91fe60f8cef64
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Fri Jul 17 17:26:08 2026 -0600

    fix(fitting): unify remaining shirley/smart/tougaard call sites onto n_avg (F3 cont.)
    
    Codex review of c5a24ac (n_avg convention unification) caught a real bug
    beyond the original patch's scope, independently on both round-1 runs:
    smart_background's post-hoc `np.minimum(shir, y)` clamp reads whatever y
    it's given. run_fit, compute_background_only, and autofit/parity.py's
    mirror all still called it as smart_background(x, _apply_endpoint_averaging(y,
    endpoint_avg)) — the old external-pre-averaging convention — so the clamp
    landed against the AVERAGED copy. The new engine.py path
    (_compute_background -> smart_background(x, y, n_avg=N)) clamps against
    the TRUE raw data. These diverge once endpoint_avg > 1, defeating F3's
    entire point: Find Peaks and manual Run Fit would disagree on SMART
    backgrounds for the same knob value. Independently reproduced (own probe
    matched Codex's ~437-count divergence) before acting on it.
    
    Fix: migrate all 6 remaining call sites (3 in run_fit, 3 in
    compute_background_only, mirrored in autofit/parity.py) from external
    pre-averaging to the same direct n_avg convention already used by
    smart_experimental_background / shirley_linear_background. shirley_background
    and tougaard_background are mathematically invariant to which convention
    is used — both read only the (possibly pre-averaged) array handed to them,
    with no second reference back to "true raw" — so this is a no-op for
    those two (proven by the existing test suite: they already passed the
    manual-vs-direct equivalence check). smart_background is the only one
    with a second raw-data reference, hence the only one that actually
    changes. Removed autofit/parity.py's now-unused _apply_endpoint_averaging
    import.
    
    New test: test_compute_background_only_matches_direct_call_with_n_avg,
    parametrized over shirley/smart/tougaard. Red confirmed first (fails only
    for smart, as expected — shirley/tougaard already passed); green after.
    
    Consequence, surfaced to and approved by Skye before implementing (the
    patch replaces rather than merely wires, and touches a real saved
    reference fit's frozen numbers — the same class of judgment call flagged
    for F1): one real fixture record changes. "U4f Scan" in
    docs/autofit/test_data/4-GTA UCl4-BN.proj.zip uses smart background with
    endpointAvg=6 — the exact combination this bug affects. Regenerated
    tests/autofit/fixtures/u4f_battery_expected.json via its committed
    generator (scripts/gen_u4f_battery_fixture.py); diffed before/after and
    confirmed only that one record changed meaningfully (reduced_chi_square
    11.399835330377146 -> 11.281303682238963, ~1.04% improvement — clamping
    against true raw data is physically the more correct reference, consistent
    with the improved fit). Every other record in the fixture differs by
    <1e-6 relative (ordinary lmfit refit floating-point noise, not this
    change). Grepped every *.proj.zip under docs/autofit/test_data/: only 3
    spectra anywhere use smart+endpoint_avg>1, 2 of which the generator
    already skips for an unrelated pre-existing reason ("fit-time grid
    drifted from current ui state"), leaving exactly this one affected
    record.
    
    Verified: tests/test_background_n_avg.py (16/16), tests/test_tougaard_background.py,
    and the C1s/U4f/B1s-Cl2p parity batteries (159 total) all green. Full
    suite: 681 passed, 6 skipped, 1 failed (test_u4f_n1s_cofit — a
    pre-existing timing/hash-seed-sensitive flake, confirmed byte-identical
    to a failure already independently ruled out earlier in this effort via
    git-stash A/B testing; it does not reproduce on every run, including the
    gated rerun below). RUN_AUTOFIT_GATE=1 real-data gate suite: 11 passed,
    1 failed (test_candidate_pool_real_gate.py's ds8 timing-budget flake,
    also previously confirmed pre-existing and unrelated) — test_u4f_n1s_cofit
    passed on this run, consistent with known flakiness in both directions,
    not a regression.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

diff --git a/tests/test_background_n_avg.py b/tests/test_background_n_avg.py
index 9a4cbca..d131f5e 100644
--- a/tests/test_background_n_avg.py
+++ b/tests/test_background_n_avg.py
@@ -13,6 +13,7 @@ import pytest
 
 from fitting import (
     _apply_endpoint_averaging,
+    compute_background_only,
     shirley_background,
     smart_background,
     smart_experimental_background,
@@ -143,3 +144,32 @@ def test_compute_background_linear_ignores_endpoint_avg():
     no_avg = _compute_background(x, y, BackgroundType.LINEAR)
     with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
     assert np.array_equal(no_avg, with_avg)
+
+
+@pytest.mark.parametrize("method", ["shirley", "smart", "tougaard"])
+def test_compute_background_only_matches_direct_call_with_n_avg(method):
+    """The manual /api/background and /api/fit dispatch (compute_background_only,
+    mirrored by run_fit and autofit/parity.py) must produce IDENTICAL output to
+    calling the underlying fitting.py function directly with the same n_avg --
+    the whole point of F3 is that Find Peaks (via _compute_background) and
+    manual Run Fit agree once both pass the same endpoint_avg.
+
+    This is the parity gap Codex review caught in c5a24ac: smart_background
+    has a post-hoc `np.minimum(shir, y)` clamp, so pre-averaging y externally
+    (the old convention, still used by compute_background_only/run_fit/
+    parity.py before this fix) clamps against the AVERAGED copy, while
+    passing n_avg directly (the new engine.py convention) clamps against the
+    TRUE raw data -- a real, non-trivial divergence for SMART specifically
+    once endpoint_avg > 1 is used (shirley/tougaard have no such post-hoc
+    step and were already equivalent either way)."""
+    x, y = _noisy_endpoint_fixture()
+    direct_fn = {"shirley": shirley_background, "smart": smart_background,
+                 "tougaard": tougaard_background}[method]
+    for n_avg in (1, 4, 8):
+        result = compute_background_only(x, y, method=method, endpoint_avg=n_avg)
+        via_dispatch = np.array(result["background"])
+        direct = direct_fn(x, y, n_avg=n_avg)
+        assert np.allclose(via_dispatch, direct, rtol=1e-9), (
+            f"{method} dispatch diverges from direct n_avg={n_avg} call by "
+            f"{np.max(np.abs(via_dispatch - direct)):.3f}"
+        )

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types, numpy as np\\nlmfit=types.ModuleType(\"lmfit\"); lmfit.Model=object; lmfit.Parameters=dict; sys.modules[\"lmfit\"]=lmfit\\nscipy=types.ModuleType(\"scipy\"); integrate=types.ModuleType(\"scipy.integrate\"); integrate.trapezoid=np.trapz; scipy.integrate=integrate; sys.modules[\"scipy\"]=scipy; sys.modules[\"scipy.integrate\"]=integrate\\nfrom fitting import _apply_endpoint_averaging, shirley_background, smart_background, tougaard_background\\nx=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.0; y[-1]-=500.0\\nfor method,fn in [(\"shirley\",shirley_background),(\"smart\",smart_background),(\"tougaard\",tougaard_background)]:\\n    for n in (1,4,8):\\n        old=fn(x,_apply_endpoint_averaging(y,n))\\n        direct=fn(x,y,n_avg=n)\\n        print(method,n,\"maxabs\",float(np.max(np.abs(old-direct))),\"allclose1e-9\",bool(np.allclose(old,direct,rtol=1e-9,atol=1e-12)))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types, numpy as np\\nlmfit=types.ModuleType(\"lmfit\"); lmfit.Model=object; lmfit.Parameters=dict; sys.modules[\"lmfit\"]=lmfit\\nscipy=types.ModuleType(\"scipy\"); integrate=types.ModuleType(\"scipy.integrate\"); integrate.trapezoid=np.trapz; scipy.integrate=integrate; sys.modules[\"scipy\"]=scipy; sys.modules[\"scipy.integrate\"]=integrate\\nfrom fitting import _apply_endpoint_averaging, shirley_background, smart_background, tougaard_background, compute_background_only\\nx=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.0; y[-1]-=500.0\\nfor method,fn in [(\"shirley\",shirley_background),(\"smart\",smart_background),(\"tougaard\",tougaard_background)]:\\n    for n in (1,4,8):\\n        current=np.array(compute_background_only(x,y,method=method,endpoint_avg=n)[\"background\"])\\n        direct=fn(x,y,n_avg=n)\\n        old_dispatch=fn(x,_apply_endpoint_averaging(y,n))\\n        print(method,n,\"current-direct\",float(np.max(np.abs(current-direct))),\"old-direct\",float(np.max(np.abs(old_dispatch-direct))))'" in /Users/skyefortier/xps-verify
 succeeded in 136ms:
shirley 1 maxabs 0.0 allclose1e-9 True
shirley 4 maxabs 0.0 allclose1e-9 True
shirley 8 maxabs 0.0 allclose1e-9 True
smart 1 maxabs 0.0 allclose1e-9 True
smart 4 maxabs 375.00567255237456 allclose1e-9 False
smart 8 maxabs 437.51940027444243 allclose1e-9 False
tougaard 1 maxabs 0.0 allclose1e-9 True
tougaard 4 maxabs 0.0 allclose1e-9 True
tougaard 8 maxabs 0.0 allclose1e-9 True

 succeeded in 135ms:
shirley 1 current-direct 0.0 old-direct 0.0
shirley 4 current-direct 0.0 old-direct 0.0
shirley 8 current-direct 0.0 old-direct 0.0
smart 1 current-direct 0.0 old-direct 0.0
smart 4 current-direct 0.0 old-direct 375.00567255237456
smart 8 current-direct 0.0 old-direct 437.51940027444243
tougaard 1 current-direct 0.0 old-direct 0.0
tougaard 4 current-direct 0.0 old-direct 0.0
tougaard 8 current-direct 0.0 old-direct 0.0

codex
The test discriminates the intended behavior: under the old dispatch convention Smart diverges by hundreds of counts on the existing fixture, while Shirley and Tougaard remain identical. I’m doing one last sweep for stray old call sites and unrelated files before forming the verdict.
exec
/bin/zsh -lc "rg -n \"shirley_background\\(|smart_background\\(|tougaard_background\\(\" . -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
./fitting.py:320:def shirley_background(
./fitting.py:384:def smart_background(
./fitting.py:400:    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
./fitting.py:528:def tougaard_background(
./fitting.py:1050:        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
./fitting.py:1052:        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
./fitting.py:1058:        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
./fitting.py:1288:        bg = shirley_background(x, y, n_avg=endpoint_avg)
./fitting.py:1290:        bg = smart_background(x, y, n_avg=endpoint_avg)
./fitting.py:1296:        bg = tougaard_background(x, y, n_avg=endpoint_avg)
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
./tests/test_tougaard_background.py:245:    got = tougaard_background(xa, ya)
./tests/test_tougaard_background.py:275:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
./tests/test_tougaard_background.py:277:    assert tougaard_background(np.array([]), np.array([])).size == 0
./tests/test_background_n_avg.py:41:    assert np.array_equal(shirley_background(x, y), shirley_background(x, y, n_avg=1))
./tests/test_background_n_avg.py:49:    raw = shirley_background(x, y, n_avg=1)
./tests/test_background_n_avg.py:50:    averaged = shirley_background(x, y, n_avg=8)
./tests/test_background_n_avg.py:58:    """Calling shirley_background(x, y, n_avg=N) must equal the OLD calling
./tests/test_background_n_avg.py:59:    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
./tests/test_background_n_avg.py:63:        direct = shirley_background(x, y, n_avg=n_avg)
./tests/test_background_n_avg.py:64:        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
./tests/test_background_n_avg.py:70:    assert np.array_equal(smart_background(x, y), smart_background(x, y, n_avg=1))
./tests/test_background_n_avg.py:74:    """smart_background(x, y, n_avg=N) must equal
./tests/test_background_n_avg.py:75:    minimum(shirley_background(x, y, n_avg=N), y) -- the clamp applies
./tests/test_background_n_avg.py:80:        got = smart_background(x, y, n_avg=n_avg)
./tests/test_background_n_avg.py:81:        expected = np.minimum(shirley_background(x, y, n_avg=n_avg), y)
./tests/test_background_n_avg.py:87:    raw = smart_background(x, y, n_avg=1)
./tests/test_background_n_avg.py:88:    averaged = smart_background(x, y, n_avg=8)
./autofit/parity.py:98:        bg_inner = shirley_background(xb, yb, n_avg=endpoint_avg)
./autofit/parity.py:100:        bg_inner = smart_background(xb, yb, n_avg=endpoint_avg)
./autofit/parity.py:106:        bg_inner = tougaard_background(xb, yb, n_avg=endpoint_avg)
./autofit/engine.py:305:        return shirley_background(x, y, n_avg=endpoint_avg)
./autofit/engine.py:307:        return smart_background(x, y, n_avg=endpoint_avg)
./autofit/engine.py:315:        return tougaard_background(x, y, n_avg=endpoint_avg)
./tests/autofit/test_c1s_parity_gate.py:171:    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(

exec
/bin/zsh -lc "rg -n \"(shirley_background|smart_background|tougaard_background)\\(["'^'"\\n]*_apply_endpoint_averaging|_apply_endpoint_averaging\\(["'^'"\\n]*endpoint_avg|_apply_endpoint_averaging\\(["'^'"\\n]*endpointAvg\" . -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
./tests/test_background_n_avg.py:59:    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
./tests/test_background_n_avg.py:64:        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))

exec
/bin/zsh -lc 'git diff 3cd6aad''^ 3cd6aad -- templates/index.html app.py autofit/engine.py '"'autofit/methods/*.py' fitting.py | wc -l" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6SHgo2lQ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-u3hU59l4' (errno=Operation not permitted)
      42

exec
/bin/zsh -lc 'git show --check 3cd6aad' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-S0FiCKlP' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YND3bB3i' (errno=Operation not permitted)
commit 3cd6aad633be0f80bfd3bc94a4c91fe60f8cef64
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Fri Jul 17 17:26:08 2026 -0600

    fix(fitting): unify remaining shirley/smart/tougaard call sites onto n_avg (F3 cont.)
    
    Codex review of c5a24ac (n_avg convention unification) caught a real bug
    beyond the original patch's scope, independently on both round-1 runs:
    smart_background's post-hoc `np.minimum(shir, y)` clamp reads whatever y
    it's given. run_fit, compute_background_only, and autofit/parity.py's
    mirror all still called it as smart_background(x, _apply_endpoint_averaging(y,
    endpoint_avg)) — the old external-pre-averaging convention — so the clamp
    landed against the AVERAGED copy. The new engine.py path
    (_compute_background -> smart_background(x, y, n_avg=N)) clamps against
    the TRUE raw data. These diverge once endpoint_avg > 1, defeating F3's
    entire point: Find Peaks and manual Run Fit would disagree on SMART
    backgrounds for the same knob value. Independently reproduced (own probe
    matched Codex's ~437-count divergence) before acting on it.
    
    Fix: migrate all 6 remaining call sites (3 in run_fit, 3 in
    compute_background_only, mirrored in autofit/parity.py) from external
    pre-averaging to the same direct n_avg convention already used by
    smart_experimental_background / shirley_linear_background. shirley_background
    and tougaard_background are mathematically invariant to which convention
    is used — both read only the (possibly pre-averaged) array handed to them,
    with no second reference back to "true raw" — so this is a no-op for
    those two (proven by the existing test suite: they already passed the
    manual-vs-direct equivalence check). smart_background is the only one
    with a second raw-data reference, hence the only one that actually
    changes. Removed autofit/parity.py's now-unused _apply_endpoint_averaging
    import.
    
    New test: test_compute_background_only_matches_direct_call_with_n_avg,
    parametrized over shirley/smart/tougaard. Red confirmed first (fails only
    for smart, as expected — shirley/tougaard already passed); green after.
    
    Consequence, surfaced to and approved by Skye before implementing (the
    patch replaces rather than merely wires, and touches a real saved
    reference fit's frozen numbers — the same class of judgment call flagged
    for F1): one real fixture record changes. "U4f Scan" in
    docs/autofit/test_data/4-GTA UCl4-BN.proj.zip uses smart background with
    endpointAvg=6 — the exact combination this bug affects. Regenerated
    tests/autofit/fixtures/u4f_battery_expected.json via its committed
    generator (scripts/gen_u4f_battery_fixture.py); diffed before/after and
    confirmed only that one record changed meaningfully (reduced_chi_square
    11.399835330377146 -> 11.281303682238963, ~1.04% improvement — clamping
    against true raw data is physically the more correct reference, consistent
    with the improved fit). Every other record in the fixture differs by
    <1e-6 relative (ordinary lmfit refit floating-point noise, not this
    change). Grepped every *.proj.zip under docs/autofit/test_data/: only 3
    spectra anywhere use smart+endpoint_avg>1, 2 of which the generator
    already skips for an unrelated pre-existing reason ("fit-time grid
    drifted from current ui state"), leaving exactly this one affected
    record.
    
    Verified: tests/test_background_n_avg.py (16/16), tests/test_tougaard_background.py,
    and the C1s/U4f/B1s-Cl2p parity batteries (159 total) all green. Full
    suite: 681 passed, 6 skipped, 1 failed (test_u4f_n1s_cofit — a
    pre-existing timing/hash-seed-sensitive flake, confirmed byte-identical
    to a failure already independently ruled out earlier in this effort via
    git-stash A/B testing; it does not reproduce on every run, including the
    gated rerun below). RUN_AUTOFIT_GATE=1 real-data gate suite: 11 passed,
    1 failed (test_candidate_pool_real_gate.py's ds8 timing-budget flake,
    also previously confirmed pre-existing and unrelated) — test_u4f_n1s_cofit
    passed on this run, consistent with known flakiness in both directions,
    not a regression.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>


codex
The old external pre-averaging pattern only remains in a historical test assertion/comment, not production or parity dispatch. The committed file list is still just the four scoped files.
exec
/bin/zsh -lc 'git diff --name-only 3cd6aad''^ 3cd6aad -- templates/index.html app.py autofit/engine.py autofit/methods parser.py vgd_parser.py xps_reference.py static | sort' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-V586XZMq' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UkeZ3Gub' (errno=Operation not permitted)

exec
/bin/zsh -lc 'git diff --name-only 3cd6aad''^ 3cd6aad -- templates/index.html app.py autofit/engine.py autofit/methods fitting.py | sort' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VwAd72gu' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-x6ElefB8' (errno=Operation not permitted)
fitting.py

exec
/bin/zsh -lc 'git diff --numstat 3cd6aad''^ 3cd6aad' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Sf60ROaB' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qrELgHtY' (errno=Operation not permitted)
3	4	autofit/parity.py
6	6	fitting.py
42	42	tests/autofit/fixtures/u4f_battery_expected.json
30	0	tests/test_background_n_avg.py

exec
/bin/zsh -lc 'git diff --name-only 3cd6aad''^ 3cd6aad -- autofit | sort' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yy97vVJi' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gKoXRdhm' (errno=Operation not permitted)
autofit/parity.py

codex
One subtle edge I’m checking before finalizing: the invariance proof assumes endpoint averaging itself is identical in both conventions. Since `_apply_endpoint_averaging` preserves input dtype unless its caller casts first, integer count arrays could make that assumption false.
exec
/bin/zsh -lc "rg -n \"compute_background_only|run_fit\\(|np\\.array\\(|np\\.asarray\\(\" app.py fitting.py autofit -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
fitting.py:352:        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)
fitting.py:583:    xa = np.asarray(x, dtype=float)
fitting.py:584:    ya = np.asarray(y, dtype=float)
fitting.py:954:def run_fit(
fitting.py:1044:            anchor_x = np.array([a[0] for a in anchors])
fitting.py:1045:            anchor_y = np.array([a[1] for a in anchors])
fitting.py:1274:def compute_background_only(
app.py:154:                        filename=np.array([filename]))
app.py:723:            result = fitting.compute_background_only(
app.py:828:            result = fitting.run_fit(
autofit/candidates.py:148:    x = np.asarray(x, dtype=float)
autofit/candidates.py:149:    y = np.asarray(y, dtype=float)
autofit/candidates.py:581:    x = np.asarray(x, dtype=float)
autofit/candidates.py:582:    y = np.asarray(y, dtype=float)
autofit/candidates.py:583:    background = np.asarray(background, dtype=float)
autofit/reference.py:270:            raw_be=np.asarray(raw_be, dtype=float),
autofit/reference.py:271:            raw_intensity=np.asarray(t.get("rawIntensity"), dtype=float),
autofit/noise.py:94:        y = np.asarray(y, dtype=float)
autofit/noise.py:191:    x = np.asarray(x, dtype=float)
autofit/noise.py:192:    ys = [np.asarray(s, dtype=float) for s in scans]
autofit/noise.py:383:    bi_a, bv_a = np.asarray(bi_a), np.asarray(bv_a)
autofit/noise.py:398:        bi_a = bv_a = np.asarray([])
autofit/noise.py:399:        pred = np.asarray([])
autofit/noise.py:422:    y = np.asarray(y, dtype=float)
autofit/engine.py:862:    x = np.asarray(x, dtype=float)
autofit/engine.py:863:    y = np.asarray(y, dtype=float)
autofit/engine.py:864:    weights = np.asarray(weights, dtype=float)
autofit/engine.py:1235:        arr = np.asarray(v)
autofit/engine.py:1543:        r = np.asarray(lm.residual, dtype=float)
autofit/parity.py:63:    total = np.zeros_like(np.asarray(be, dtype=float))
autofit/parity.py:69:def background_like_run_fit(
autofit/parity.py:84:    x = np.asarray(x, dtype=float)
autofit/parity.py:85:    y = np.asarray(y, dtype=float)
autofit/parity.py:168:    return float(np.max(np.abs(np.asarray(saved_be, dtype=float) - roi))) <= tol
autofit/parity.py:176:    fittedY = np.asarray(rf.fit_result["fittedY"], dtype=float)
autofit/parity.py:180:    bg = background_like_run_fit(
autofit/parity.py:193:    res = run_fit(
autofit/confidence.py:72:    covar = np.asarray(result.covar, dtype=float)
autofit/methods/base.py:90:    return 1.0 / np.sqrt(np.maximum(np.asarray(y, dtype=float), 1.0))
autofit/methods/ic_model_comparison.py:53:        x = np.asarray(x, dtype=float)
autofit/methods/ic_model_comparison.py:54:        y = np.asarray(y, dtype=float)
autofit/methods/ic_model_comparison.py:55:        w = np.asarray(weights, dtype=float) if weights is not None \
autofit/methods/bayesian_exchange_mc.py:110:    return _ParamSpace(names=names, lows=np.array(lows), highs=np.array(highs),
autofit/methods/bayesian_exchange_mc.py:139:    w = np.ones(n) if weights is None else np.asarray(weights, dtype=float)
autofit/methods/bayesian_exchange_mc.py:155:    lls = np.array([loglik(t) for t in thetas])
autofit/methods/bayesian_exchange_mc.py:212:            lr = d * np.asarray(ll_records[k][sl])
autofit/methods/bayesian_exchange_mc.py:231:    samples = np.asarray(post_samples)
autofit/methods/bayesian_exchange_mc.py:234:    rss_samples = np.exp(-2.0 * np.asarray(post_lls) / n)
autofit/methods/bayesian_exchange_mc.py:316:        x = np.asarray(x, dtype=float)
autofit/methods/bayesian_exchange_mc.py:317:        y = np.asarray(y, dtype=float)
autofit/methods/bayesian_exchange_mc.py:408:        fs = np.array([c["free_energy"] for c in scored])
autofit/methods/least_squares.py:50:        res = run_fit(
autofit/methods/least_squares.py:51:            np.asarray(x, dtype=float),
autofit/methods/least_squares.py:52:            np.asarray(y, dtype=float),
autofit/methods/sparse_map.py:161:            wts = np.array([e[3] for e in cl])
autofit/methods/sparse_map.py:195:        x = np.asarray(x, dtype=float)
autofit/methods/sparse_map.py:196:        y = np.asarray(y, dtype=float)
autofit/methods/sparse_map.py:271:            wts = np.array([e[3] for e in cl])
autofit/methods/multivariate_mcr.py:76:        grid = np.asarray(grid, dtype=float)
autofit/methods/multivariate_mcr.py:84:        x = np.asarray(x, dtype=float)
autofit/methods/multivariate_mcr.py:85:        y = np.asarray(y, dtype=float)
autofit/methods/multivariate_mcr.py:122:        x = np.asarray(x, dtype=float)
autofit/methods/multivariate_mcr.py:123:        D = np.asarray(y, dtype=float)
autofit/methods/multivariate_mcr.py:167:        S = np.asarray(S).T                    # n × k
autofit/methods/max_entropy.py:95:        x = np.asarray(x, dtype=float)
autofit/methods/max_entropy.py:96:        y = np.asarray(y, dtype=float)

exec
/bin/zsh -lc "nl -ba app.py | sed -n '80,180p' && nl -ba app.py | sed -n '300,430p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    80	    _register_routes(app)
    81	    _register_error_handlers(app)
    82	
    83	    return app
    84	
    85	
    86	# ─────────────────────────────────────────────────────────────────────────────
    87	# Helpers
    88	# ─────────────────────────────────────────────────────────────────────────────
    89	
    90	def _json_sanitize(obj):
    91	    """Defensive numpy→native + non-finite→None conversion for
    92	    /api/analyze payloads: a stray np scalar must not 500 the route, and
    93	    inf/NaN (e.g. BIC of a degenerate fit) must not emit non-standard JSON
    94	    that browsers refuse to parse."""
    95	    if isinstance(obj, dict):
    96	        return {str(k): _json_sanitize(v) for k, v in obj.items()}
    97	    if isinstance(obj, (list, tuple)):
    98	        return [_json_sanitize(v) for v in obj]
    99	    if isinstance(obj, np.generic):
   100	        obj = obj.item()
   101	    if isinstance(obj, np.ndarray):
   102	        return [_json_sanitize(v) for v in obj.tolist()]
   103	    if isinstance(obj, float) and not np.isfinite(obj):
   104	        return None
   105	    return obj
   106	
   107	
   108	def _session_path(session_id: str, upload_folder: str) -> Path:
   109	    return Path(upload_folder) / f"{session_id}.npz"
   110	
   111	
   112	def _load_session(session_id: str, upload_folder: str) -> tuple[np.ndarray, np.ndarray]:
   113	    """Load energy and counts arrays from a session file."""
   114	    path = _session_path(session_id, upload_folder)
   115	    if not path.exists():
   116	        raise KeyError(session_id)
   117	    archive = np.load(path)
   118	    return archive["energy"], archive["counts"]
   119	
   120	
   121	def _sweep_expired_sessions(upload_folder: str) -> None:
   122	    """Opportunistically delete session files older than SESSION_TTL_DAYS.
   123	
   124	    Runs on each new session write (audit F13) — no scheduler/thread, which
   125	    would risk duplicate sweeps under multi-worker gunicorn. Touches ONLY
   126	    ``*.npz`` session files (never .vgd scratch or temp uploads), tolerates a
   127	    concurrent worker deleting the same file first, and never raises (cleanup
   128	    must not break a successful upload).
   129	    """
   130	    cutoff = time.time() - SESSION_TTL_DAYS * 86400
   131	    try:
   132	        candidates = list(Path(upload_folder).glob("*.npz"))
   133	    except OSError:
   134	        return
   135	    for p in candidates:
   136	        try:
   137	            if p.stat().st_mtime < cutoff:
   138	                p.unlink(missing_ok=True)
   139	        except FileNotFoundError:
   140	            pass  # another worker swept it first — fine
   141	        except OSError:
   142	            pass  # never let cleanup break the request
   143	
   144	
   145	def _save_session(
   146	    session_id: str,
   147	    upload_folder: str,
   148	    energy: np.ndarray,
   149	    counts: np.ndarray,
   150	    filename: str = "",
   151	) -> None:
   152	    path = _session_path(session_id, upload_folder)
   153	    np.savez_compressed(path, energy=energy, counts=counts,
   154	                        filename=np.array([filename]))
   155	    # Opportunistic TTL cleanup of stale sessions (audit F13). Never raises.
   156	    _sweep_expired_sessions(upload_folder)
   157	
   158	
   159	def _err(message: str, status: int = 400) -> tuple:
   160	    return jsonify({"error": message}), status
   161	
   162	
   163	# adjustable defaults surfaced by /api/analyze/meta (spec §5A); anything the
   164	# client sends in `options` overrides these and is validated by the METHOD's
   165	# own option whitelist (ValueError → 400). Module-level (not just a
   166	# _register_routes local) so the shared /api/analyze helpers below can see it.
   167	_ANALYZE_METHODS = {
   168	    "least_squares": {"background_method": "shirley"},
   169	    "ic_model_comparison": {"n_refits": 4, "rng_seed": 0,
   170	                            "enable_proposal_pass": True,
   171	                            "fit_full_window": False},
   172	    "bayesian_exchange_mc": {"n_replicas": 8, "n_sweeps": 600,
   173	                             "rng_seed": 0},
   174	    "sparse_map": {},
   175	}
   176	
   177	
   178	# ─────────────────────────────────────────────────────────────────────────────
   179	# /api/analyze shared helpers (Find Peaks; strictly additive — the manual
   180	# /api/fit path never touches this code) — extracted so /api/analyze (sync)
   300	
   301	    return _AnalyzeContext(x, y, method_id, opts, peak_specs, grammar)
   302	
   303	
   304	def _run_analyze_method(ctx: _AnalyzeContext, progress_cb=None):
   305	    """The one genuinely slow/unpredictable step — the ONLY part that
   306	    runs on a background thread for the async job path.  ``progress_cb``
   307	    is None for the synchronous /api/analyze route (no poller to feed)."""
   308	    from autofit.methods import get_method
   309	
   310	    try:
   311	        return get_method(ctx.method_id).run(
   312	            ctx.x, ctx.y, grammar=ctx.grammar, peak_specs=ctx.peak_specs,
   313	            options=ctx.opts, progress_cb=progress_cb)
   314	    except (ValueError, TypeError) as exc:
   315	        # the method's own option/spec validation — TypeError included:
   316	        # a malformed option VALUE (e.g. n_refits: []) raises TypeError
   317	        # from the methods' numeric casts (Codex re-check blocker)
   318	        raise _AnalyzeError(f"invalid option or spec: {exc}")
   319	    except Exception:
   320	        logging.getLogger(__name__).exception("analyze failed")
   321	        raise _AnalyzeError("Internal analyze error — see server log.", 500)
   322	
   323	
   324	def _build_analyze_payload(ctx: _AnalyzeContext, res) -> dict:
   325	    """Shape the method result into the wire payload — byte-identical to
   326	    the pre-refactor inline logic, incl. the Stage-2 structural-only
   327	    degradation branch (a region with zero grammar candidates still RUNS
   328	    via the detection family; the honest structure-report stub returns
   329	    only when detection found nothing fittable either)."""
   330	    grammar = ctx.grammar
   331	    if (grammar is not None and grammar.structural_only
   332	            and not grammar.candidates and not res.success):
   333	        non_verified = sorted({
   334	            f"{slug}:{e['constant']}"
   335	            for slug, entries in grammar.provenance.items()
   336	            for e in entries if e.get("status") != "VERIFIED"
   337	        })
   338	        return {
   339	            "method": ctx.method_id,
   340	            "success": False,
   341	            "structural_only": list(grammar.structural_only),
   342	            "structure_report": grammar.provenance,
   343	            "notes": grammar.notes,
   344	            "uses_conditional_or_unverified_constants": non_verified,
   345	            "peaks": [],
   346	            "confidence": {},
   347	            "message": (
   348	                "structure known, positions UNVERIFIED — detection "
   349	                "found no fittable features in this window; supply a "
   350	                "cited source (autofit.cited_values schema) and "
   351	                "curated windows to enable grammar fitting for: "
   352	                + ", ".join(grammar.structural_only)),
   353	            "review_gate": {
   354	                "reviewed_by": None,
   355	                "note": "results are candidates + honesty flags, "
   356	                        "not ground truth — a named human review is "
   357	                        "required before export (spec §8)",
   358	            },
   359	        }
   360	
   361	    payload = {
   362	        "method": ctx.method_id,
   363	        "success": bool(res.success),
   364	        # Phase D: regions that resolved structure-only in a MIXED
   365	        # request (deep + structural) are flagged here; their derived
   366	        # structure rides in analysis.constants_provenance.
   367	        "structural_only": list(grammar.structural_only) if grammar else [],
   368	        "peaks": res.peaks,
   369	        "confidence": res.confidence,
   370	        "analysis": res.analysis,
   371	        "diagnostics": res.diagnostics,
   372	        "message": res.message,
   373	        "review_gate": {
   374	            "reviewed_by": None,
   375	            "note": "results are candidates + confidence flags, not "
   376	                    "ground truth — a named human review is required "
   377	                    "before export (spec §8)",
   378	        },
   379	    }
   380	    if grammar is not None and grammar.structural_only:
   381	        # structural regions that DID fit (detection family) still ship
   382	        # their derived-structure report for the honesty surface
   383	        payload["structure_report"] = grammar.provenance
   384	        payload["notes"] = grammar.notes
   385	    return payload
   386	
   387	
   388	def _analyze_progress_message(evt: dict) -> str:
   389	    """Human-readable progress line from one engine progress_cb event —
   390	    the exact wording the goal asked for ('candidate 7 of 29 . stabilizing')."""
   391	    phase = evt.get("phase")
   392	    idx, total = evt.get("candidate_index"), evt.get("candidate_total")
   393	    name = evt.get("candidate_name")
   394	    if phase == "screening" and idx and total:
   395	        msg = f"screening candidate {idx} of {total}"
   396	    elif phase == "stabilizing" and idx and total:
   397	        msg = f"candidate {idx} of {total} — stabilizing"
   398	    else:
   399	        return phase or "working…"
   400	    return msg + (f" ({name})" if name else "")
   401	
   402	
   403	def _job_progress_path(job_id: str, upload_folder: str) -> Path:
   404	    return Path(upload_folder) / f"{job_id}.job.json"
   405	
   406	
   407	def _write_job_progress(job_id: str, upload_folder: str, data: dict) -> None:
   408	    """Atomic write (temp file + os.replace) — required because the
   409	    writer (background thread, possibly in a DIFFERENT gunicorn worker
   410	    process than whichever one later serves a poll GET) and the reader
   411	    are never synchronized otherwise; a half-written file must never be
   412	    visible to a concurrent poll."""
   413	    path = _job_progress_path(job_id, upload_folder)
   414	    tmp = path.with_suffix(".tmp")
   415	    try:
   416	        tmp.write_text(json.dumps(_json_sanitize(data)))
   417	        os.replace(tmp, path)
   418	    except OSError:
   419	        logging.getLogger(__name__).exception(
   420	            "failed to write progress for job %s", job_id)
   421	
   422	
   423	def _sweep_expired_jobs(upload_folder: str) -> None:
   424	    """Opportunistic TTL cleanup of stale job progress files — same
   425	    pattern as _sweep_expired_sessions (audit F13): runs on each new job
   426	    start, no scheduler/thread, tolerates a concurrent worker deleting the
   427	    same file first, never raises."""
   428	    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
   429	    try:
   430	        candidates = list(Path(upload_folder).glob("*.job.json"))

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types, numpy as np\\nlmfit=types.ModuleType(\"lmfit\"); lmfit.Model=object; lmfit.Parameters=dict; sys.modules[\"lmfit\"]=lmfit\\nscipy=types.ModuleType(\"scipy\"); integrate=types.ModuleType(\"scipy.integrate\"); integrate.trapezoid=np.trapz; scipy.integrate=integrate; sys.modules[\"scipy\"]=scipy; sys.modules[\"scipy.integrate\"]=integrate\\nfrom fitting import _apply_endpoint_averaging, shirley_background, tougaard_background\\nx=np.linspace(0,10,40); y=(1000+200*np.exp(-0.5*((x-5)/1.5)**2)).astype(int); y[0]+=7; y[-1]-=5\\nfor method,fn in [(\"shirley\",shirley_background),(\"tougaard\",tougaard_background)]:\\n    for n in (4,8):\\n        old=fn(x,_apply_endpoint_averaging(y,n)); direct=fn(x,y,n_avg=n)\\n        print(method,n,\"yavg dtype\",_apply_endpoint_averaging(y,n).dtype,\"maxabs\",float(np.max(np.abs(old-direct))))'" in /Users/skyefortier/xps-verify
 succeeded in 116ms:
shirley 4 yavg dtype int64 maxabs 0.2514979305193492
shirley 8 yavg dtype int64 maxabs 0.5000000001438138
tougaard 4 yavg dtype int64 maxabs 0.25081263258039144
tougaard 8 yavg dtype int64 maxabs 0.5

codex
That dtype edge is real in the low-level functions: external pre-averaging an integer array truncates endpoint means, while the new direct path casts to float first. I’m checking whether public/manual callers already provide float arrays, which would keep this out of the claimed web-app scenario.
exec
/bin/zsh -lc "nl -ba app.py | sed -n '680,850p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   766	              "gl_ratio":     0.3,                // Lorentzian fraction [0–1]
   767	              "fwhm_l":       1.5,                // asymmetric_gl only
   768	              "fwhm_r":       1.5,                // asymmetric_gl only
   769	              "alpha":        0.1,                // doniach_sunjic only
   770	              "constrain_to": null,               // id of master peak, or null
   771	              "splitting":    3.67,               // BE offset from master (eV)
   772	              "area_ratio":   0.75,               // amplitude = master × ratio
   773	              "fix_fwhm":     true                // lock FWHM to master
   774	            }
   775	          ]
   776	        }
   777	        """
   778	        body = request.get_json()
   779	        session_id = body.get("session_id", "")
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
   836	                fit_kws={"method": fit_method},
   837	                manual_bg=manual_bg,
   838	                n_perturb=n_perturb,
   839	                endpoint_avg=endpoint_avg,
   840	            )
   841	        except ValueError as exc:
   842	            # Our own validation: unknown shape/method, self/circular constraint,
   843	            # "Master peak not found", bad numeric field, etc. (audit F10/F11).
   844	            return _err(str(exc))
   845	        except RuntimeError:
   846	            # Solver-internal failure (e.g. lmfit non-convergence). Log the
   847	            # detail; return a generic 422 that leaks no library internals.
   848	            app.logger.exception("Fit failed")
   849	            return _err("Fit failed — see server log for details.", 422)
   850	        except Exception:

exec
/bin/zsh -lc "nl -ba app.py | sed -n '430,680p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   430	        candidates = list(Path(upload_folder).glob("*.job.json"))
   431	    except OSError:
   432	        return
   433	    for p in candidates:
   434	        try:
   435	            if p.stat().st_mtime < cutoff:
   436	                p.unlink(missing_ok=True)
   437	        except FileNotFoundError:
   438	            pass
   439	        except OSError:
   440	            pass
   441	
   442	
   443	def _require_json(f):
   444	    """Decorator: return 400 if request body is not valid JSON."""
   445	    @wraps(f)
   446	    def wrapper(*args, **kwargs):
   447	        if not request.is_json:
   448	            return _err("Request must be JSON (Content-Type: application/json)")
   449	        return f(*args, **kwargs)
   450	    return wrapper
   451	
   452	
   453	# ─────────────────────────────────────────────────────────────────────────────
   454	# Spin‑orbit element presets
   455	# ─────────────────────────────────────────────────────────────────────────────
   456	
   457	#  (splitting eV, area_ratio = intensity(high‑j) / intensity(low‑j))
   458	#  Convention: the primary peak is the high‑j component (lower BE in BE scale).
   459	SPIN_ORBIT_PRESETS = {
   460	    "Si 2p":  {"splitting": 0.61,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   461	    "Al 2p":  {"splitting": 0.41,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   462	    "P 2p":   {"splitting": 0.84,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   463	    "S 2p":   {"splitting": 1.18,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   464	    "Cl 2p":  {"splitting": 1.60,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   465	    "Ti 2p":  {"splitting": 5.54,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   466	    "Fe 2p":  {"splitting": 13.1,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   467	    "Co 2p":  {"splitting": 15.0,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   468	    "Ni 2p":  {"splitting": 17.3,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   469	    "Cu 2p":  {"splitting": 19.8,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   470	    "Zn 2p":  {"splitting": 23.1,  "area_ratio": 0.5,  "description": "2p3/2 → 2p1/2 (2:1)"},
   471	    "Mo 3d":  {"splitting": 3.13,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
   472	    "Ag 3d":  {"splitting": 6.00,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
   473	    "Cd 3d":  {"splitting": 6.74,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
   474	    "Sn 3d":  {"splitting": 8.43,  "area_ratio": 0.667, "description": "3d5/2 → 3d3/2 (3:2)"},
   475	    "W 4f":   {"splitting": 2.18,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
   476	    "Au 4f":  {"splitting": 3.67,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
   477	    "Pt 4f":  {"splitting": 3.33,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
   478	    "Pb 4f":  {"splitting": 4.86,  "area_ratio": 0.75, "description": "4f7/2 → 4f5/2 (4:3)"},
   479	}
   480	
   481	
   482	# ─────────────────────────────────────────────────────────────────────────────
   483	# Route registration
   484	# ─────────────────────────────────────────────────────────────────────────────
   485	
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
   515	            "in <code>templates/</code> or <code>static/</code>.</p>"
   516	            "<p>API ready at <code>/api/</code></p>",
   517	            200,
   518	        )
   519	
   520	    # ── Metadata endpoints ────────────────────────────────────────────────────
   521	
   522	    @app.get("/api/peak-shapes")
   523	    def peak_shapes():
   524	        descriptions = {
   525	            "gaussian":        "Pure Gaussian",
   526	            "lorentzian":      "Pure Lorentzian",
   527	            "pseudo_voigt_gl": "Pseudo-Voigt GL mix  (η = Lorentzian fraction)",
   528	            "asymmetric_gl":   "Asymmetric GL  (independent left/right FWHM)",
   529	            "doniach_sunjic":  "Doniach-Sunjic  (metallic systems, asymmetric)",
   530	            "ds_g":            "DS+G  (Doniach-Sunjic core convolved with Gaussian)",
   531	            "la_casaxps":      "LA(alpha,beta,m) [CasaXPS]  (asymmetric Lorentzian + Gaussian conv)",
   532	        }
   533	        return jsonify({k: descriptions[k] for k in fitting.AVAILABLE_SHAPES})
   534	
   535	    @app.get("/api/elements")
   536	    def elements():
   537	        return jsonify(SPIN_ORBIT_PRESETS)
   538	
   539	    @app.get("/api/xps-reference")
   540	    def xps_reference():
   541	        """Serve the validated data/xps reference dataset (cached on mtime).
   542	
   543	        On invalid data this fails loudly with a structured error naming the
   544	        offending file and JSON path — a malformed transition is never
   545	        silently dropped.
   546	        """
   547	        try:
   548	            payload = load_reference_cached(app.config["XPS_DATA_DIR"])
   549	        except XPSReferenceError as e:
   550	            logging.getLogger(__name__).error("XPS reference dataset invalid: %s", e)
   551	            return jsonify({"error": e.message, "file": e.filename,
   552	                            "path": e.json_path}), 500
   553	        return jsonify(payload)
   554	
   555	    # ── File upload ───────────────────────────────────────────────────────────
   556	
   557	    @app.post("/api/upload")
   558	    def upload():
   559	        if "file" not in request.files:
   560	            return _err("No file field in the request")
   561	        f = request.files["file"]
   562	        if not f.filename:
   563	            return _err("No filename provided")
   564	
   565	        filename = secure_filename(f.filename)
   566	        suffix = Path(filename).suffix.lower()
   567	        if suffix not in xps_parser.ALLOWED_EXTENSIONS:
   568	            return _err(
   569	                f"File type '{suffix}' not supported. "
   570	                f"Allowed: {sorted(xps_parser.ALLOWED_EXTENSIONS)}"
   571	            )
   572	
   573	        # Save raw upload temporarily. Prefix with a UUID so concurrent uploads
   574	        # of files with the same name never collide in the shared upload dir.
   575	        tmp_path = Path(app.config["UPLOAD_FOLDER"]) / f"{uuid.uuid4().hex}_{filename}"
   576	        f.save(str(tmp_path))
   577	
   578	        try:
   579	            energy, counts = xps_parser.parse_file(tmp_path)
   580	        except ValueError as exc:
   581	            # Our own validation (clean, user-facing): bad format, empty file,
   582	            # too few points, "Not a valid Thermo VGD file", etc. (audit F10).
   583	            tmp_path.unlink(missing_ok=True)
   584	            return _err(f"Could not parse file: {exc}")
   585	        except Exception:
   586	            # Unexpected library/internal failure — log the detail, return generic.
   587	            app.logger.exception("Unexpected file-parse error")
   588	            tmp_path.unlink(missing_ok=True)
   589	            return _err("Internal parse error — see server log for details.", 500)
   590	        finally:
   591	            tmp_path.unlink(missing_ok=True)
   592	
   593	        session_id = str(uuid.uuid4())
   594	        try:
   595	            _save_session(session_id, app.config["UPLOAD_FOLDER"],
   596	                          energy, counts, filename)
   597	        except Exception:
   598	            app.logger.exception("Failed to store session")
   599	            return _err("Could not store the session — see server log.", 500)
   600	
   601	        return jsonify({
   602	            "session_id": session_id,
   603	            "filename": filename,
   604	            "n_points": int(len(energy)),
   605	            "energy_range": [float(energy.min()), float(energy.max())],
   606	            "counts_range": [float(counts.min()), float(counts.max())],
   607	            # Return a downsampled preview (max 2000 points) to keep payload small
   608	            **_preview(energy, counts, max_pts=2000),
   609	        })
   610	
   611	    # ── VGD parse (Thermo Avantage binary format) ─────────────────────────────
   612	
   613	    @app.post("/api/parse-vgd")
   614	    def parse_vgd_endpoint():
   615	        """Parse a Thermo Avantage VGD file and return (be, inten) arrays.
   616	
   617	        Accepts a multipart/form-data POST with a single 'file' field.
   618	        Optional form fields:
   619	          photon_energy  – X-ray source energy in eV (default 1486.6, Al Kα)
   620	          work_function  – spectrometer WF in eV      (default 4.5)
   621	
   622	        Returns JSON: { be: [...], inten: [...], n_points: int, be_range: [min,max] }
   623	        """
   624	        if "file" not in request.files:
   625	            return _err("No file field in the request")
   626	        f = request.files["file"]
   627	        if not f.filename:
   628	            return _err("No filename provided")
   629	
   630	        # Reject non-.vgd before spending the upload budget / writing to disk
   631	        # (audit F12). olefile content validation remains the real gate.
   632	        if Path(f.filename).suffix.lower() != ".vgd":
   633	            return _err("Only .vgd files are accepted by this endpoint.")
   634	
   635	        try:
   636	            photon_energy = float(request.form.get("photon_energy", vgd_parser.DEFAULT_PHOTON_ENERGY))
   637	            work_function = float(request.form.get("work_function", vgd_parser.DEFAULT_WORK_FUNCTION))
   638	        except ValueError:
   639	            return _err("photon_energy and work_function must be numbers")
   640	
   641	        # Save to a temp file so olefile can open it by path
   642	        tmp_path = Path(app.config["UPLOAD_FOLDER"]) / f"vgd_tmp_{uuid.uuid4().hex}.vgd"
   643	        try:
   644	            f.save(str(tmp_path))
   645	            be, inten = vgd_parser.parse_vgd(
   646	                str(tmp_path),
   647	                photon_energy=photon_energy,
   648	                work_function=work_function,
   649	            )
   650	        except (ValueError, ImportError) as exc:
   651	            # Clean, user/operator-facing: "Not a valid Thermo VGD file",
   652	            # "olefile is required: pip install olefile" (audit F10).
   653	            return _err(str(exc))
   654	        except Exception:
   655	            app.logger.exception("Unexpected VGD parse error")
   656	            return _err("Internal VGD parse error — see server log.", 500)
   657	        finally:
   658	            tmp_path.unlink(missing_ok=True)
   659	
   660	        return jsonify({
   661	            "be":       be,
   662	            "inten":    inten,
   663	            "n_points": len(be),
   664	            "be_range": [min(be), max(be)] if be else [0, 0],
   665	        })
   666	
   667	    # ── Session management ────────────────────────────────────────────────────
   668	
   669	    @app.get("/api/session/<session_id>")
   670	    def get_session(session_id: str):
   671	        _validate_session_id(session_id)
   672	        try:
   673	            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
   674	        except KeyError:
   675	            return _err(f"Session '{session_id}' not found", 404)
   676	        return jsonify({
   677	            "session_id": session_id,
   678	            "n_points": int(len(energy)),
   679	            **_preview(energy, counts, max_pts=2000),
   680	        })

exec
/bin/zsh -lc "rg -n \"loadtxt|genfromtxt|rawIntensity|counts|intensity|astype\\(float|dtype=float\" app.py parser.py vgd_parser.py xps_reference.py -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
parser.py:6:  CSV   – two‑column (energy, counts); auto‑detects delimiter and header rows
parser.py:12:  parse_file(filepath)  →  (energy: np.ndarray, counts: np.ndarray)
parser.py:47:    counts : np.ndarray  – intensity (counts or CPS), shape (N,)
parser.py:65:        # fabricated counts. vgd_parser raises ValueError on non-OLE input.
parser.py:67:        return np.asarray(be, dtype=float), np.asarray(inten, dtype=float)
parser.py:85:    Parse a delimited text file with two numeric columns (energy, counts).
parser.py:126:            "columns (binding energy, intensity)."
parser.py:154:                "Expected (energy, counts)."
parser.py:157:    energy = df[numeric_cols[0]].to_numpy(dtype=float)
parser.py:158:    counts = df[numeric_cols[1]].to_numpy(dtype=float)
parser.py:160:    mask = np.isfinite(energy) & np.isfinite(counts)
parser.py:164:    return energy[mask], counts[mask]
parser.py:170:    counts = {d: sample.count(d) for d in candidates}
parser.py:171:    return max(counts, key=counts.get)
parser.py:195:            "with two numeric columns (binding energy, intensity)."
parser.py:209:            energy = df[numeric_cols[0]].to_numpy(dtype=float)
parser.py:210:            counts = df[numeric_cols[1]].to_numpy(dtype=float)
parser.py:211:            mask = np.isfinite(energy) & np.isfinite(counts)
parser.py:213:                return energy[mask], counts[mask]
parser.py:217:        "Expected (energy, counts)."
parser.py:352:      offset 512 : float32[n_points] intensity
parser.py:395:    This recovers intensity data but loses the true energy calibration; the
parser.py:403:        all_floats = np.frombuffer(data, dtype="<f4", count=n_floats).astype(float)
parser.py:427:    counts = all_floats[best_start: best_start + best_len]
parser.py:428:    energy = np.arange(best_len, dtype=float)  # placeholder index axis
parser.py:434:    return energy, counts
parser.py:480:        arr = np.frombuffer(data, dtype=f"{endian}f4", count=n, offset=offset).astype(float)
parser.py:486:            arr = np.frombuffer(data, dtype=">f4", count=n, offset=offset).astype(float)
parser.py:498:def ensure_ascending(energy: np.ndarray, counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
parser.py:501:        return energy[::-1].copy(), counts[::-1].copy()
parser.py:502:    return energy.copy(), counts.copy()
vgd_parser.py:7:  VGData      – float64 array, intensity counts per point.
vgd_parser.py:54:    (be, intensity) : two Python lists of floats, sorted by increasing BE.
vgd_parser.py:55:    For overlay (multi-scan) files the intensity is the per-point average
vgd_parser.py:74:        # ── 1. Intensity counts ────────────────────────────────────────────────
vgd_parser.py:91:    # ── 4. Build intensity array (average overlapping scans if present) ────────
vgd_parser.py:97:        all_counts = np.frombuffer(raw_data[: n_pts * n_scans * 8], dtype="<f8")
vgd_parser.py:98:        counts = all_counts.reshape(n_scans, n_pts).mean(axis=0)
vgd_parser.py:102:        counts = np.frombuffer(raw_data[: n_use * 8], dtype="<f8")
vgd_parser.py:112:        counts = counts[::-1]
vgd_parser.py:114:    return be.tolist(), counts.tolist()
app.py:113:    """Load energy and counts arrays from a session file."""
app.py:118:    return archive["energy"], archive["counts"]
app.py:149:    counts: np.ndarray,
app.py:153:    np.savez_compressed(path, energy=energy, counts=counts,
app.py:229:        energy, counts = _load_session(session_id, upload_folder)
app.py:269:    x, y = corrected[mask], counts[mask]
app.py:457:#  (splitting eV, area_ratio = intensity(high‑j) / intensity(low‑j))
app.py:579:            energy, counts = xps_parser.parse_file(tmp_path)
app.py:596:                          energy, counts, filename)
app.py:606:            "counts_range": [float(counts.min()), float(counts.max())],
app.py:608:            **_preview(energy, counts, max_pts=2000),
app.py:673:            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
app.py:679:            **_preview(energy, counts, max_pts=2000),
app.py:709:            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
app.py:724:                energy, counts, method=method,
app.py:783:            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
app.py:830:                counts=counts,
app.py:1107:    counts: np.ndarray,
app.py:1110:    """Return (possibly downsampled) energy/counts lists for API responses."""
app.py:1113:        return {"energy": energy.tolist(), "counts": counts.tolist()}
app.py:1118:        "counts": counts[idx].tolist(),

codex
1. MINOR [fitting.py](/Users/skyefortier/xps-verify/fitting.py:306): the Shirley/Tougaard invariance claim is true for the app’s normal float arrays, but not strictly true for integer `y` arrays. `_apply_endpoint_averaging` preserves input dtype, so old external pre-averaging on `int64` truncates fractional endpoint means, while the new direct path casts to float before averaging in `shirley_background` and `tougaard_background`. Concrete scenario: low-level callers using integer counts with `endpoint_avg > 1` can see ~0.25 to 0.5 count changes for Shirley/Tougaard. The web/app and fixture paths appear to use float arrays, so I do not consider this a GO blocker.

Verification notes:

- Math trace: `shirley_background` rebinds `y` to the averaged copy at [fitting.py:351](/Users/skyefortier/xps-verify/fitting.py:351), then only uses `ys`. `tougaard_background` similarly uses `ya` after [fitting.py:583](/Users/skyefortier/xps-verify/fitting.py:583). `smart_background` is not invariant because it computes Shirley with `n_avg` but clamps against the original argument at [fitting.py:400](/Users/skyefortier/xps-verify/fitting.py:400).
- Fixture scope: independently enumerated all `docs/autofit/test_data/*.proj.zip`; exactly 3 fitted spectra are `smart` with `endpointAvg > 1`: `U4f Scan` endpoint 6, `U4f Scan_0` endpoint 6, `U4f Scan_3` endpoint 2, all in `4-GTA UCl4-BN.proj.zip`. The latter two are skipped as `fit-time grid drifted from current ui state`; only `U4f Scan` is eligible.
- Fixture diff: 29 records before and after, same keys, same skipped list. Meaningful diff only for `4-GTA UCl4-BN.proj.zip / U4f Scan`: `reduced_chi_square` `11.399835330377146 -> 11.281303682238963` with max relative diff ~1.04%. `U4f Scan_5` has only tiny refit noise, max relative diff ~`1.49e-12`.
- Import claim: `rg _apply_endpoint_averaging autofit/parity.py` finds no remaining references; removal is dead-code cleanup.
- Test discrimination: the new test at [tests/test_background_n_avg.py:149](/Users/skyefortier/xps-verify/tests/test_background_n_avg.py:149) would fail under the old Smart dispatch: I reproduced old-vs-direct max divergences of `375.0` and `437.5` counts for `n_avg=4/8`; Shirley and Tougaard stayed identical for the float fixture.
- Scope sweep: `git diff-tree` shows only `autofit/parity.py`, `fitting.py`, `tests/test_background_n_avg.py`, and `tests/autofit/fixtures/u4f_battery_expected.json`. No diffs in `templates/index.html`, `app.py`, `autofit/engine.py`, `autofit/methods`, or lineshapes. I could not run the full pytest suite here because this environment lacks `lmfit` and `scipy`.

VERDICT: GO
tokens used
91,324
1. MINOR [fitting.py](/Users/skyefortier/xps-verify/fitting.py:306): the Shirley/Tougaard invariance claim is true for the app’s normal float arrays, but not strictly true for integer `y` arrays. `_apply_endpoint_averaging` preserves input dtype, so old external pre-averaging on `int64` truncates fractional endpoint means, while the new direct path casts to float before averaging in `shirley_background` and `tougaard_background`. Concrete scenario: low-level callers using integer counts with `endpoint_avg > 1` can see ~0.25 to 0.5 count changes for Shirley/Tougaard. The web/app and fixture paths appear to use float arrays, so I do not consider this a GO blocker.

Verification notes:

- Math trace: `shirley_background` rebinds `y` to the averaged copy at [fitting.py:351](/Users/skyefortier/xps-verify/fitting.py:351), then only uses `ys`. `tougaard_background` similarly uses `ya` after [fitting.py:583](/Users/skyefortier/xps-verify/fitting.py:583). `smart_background` is not invariant because it computes Shirley with `n_avg` but clamps against the original argument at [fitting.py:400](/Users/skyefortier/xps-verify/fitting.py:400).
- Fixture scope: independently enumerated all `docs/autofit/test_data/*.proj.zip`; exactly 3 fitted spectra are `smart` with `endpointAvg > 1`: `U4f Scan` endpoint 6, `U4f Scan_0` endpoint 6, `U4f Scan_3` endpoint 2, all in `4-GTA UCl4-BN.proj.zip`. The latter two are skipped as `fit-time grid drifted from current ui state`; only `U4f Scan` is eligible.
- Fixture diff: 29 records before and after, same keys, same skipped list. Meaningful diff only for `4-GTA UCl4-BN.proj.zip / U4f Scan`: `reduced_chi_square` `11.399835330377146 -> 11.281303682238963` with max relative diff ~1.04%. `U4f Scan_5` has only tiny refit noise, max relative diff ~`1.49e-12`.
- Import claim: `rg _apply_endpoint_averaging autofit/parity.py` finds no remaining references; removal is dead-code cleanup.
- Test discrimination: the new test at [tests/test_background_n_avg.py:149](/Users/skyefortier/xps-verify/tests/test_background_n_avg.py:149) would fail under the old Smart dispatch: I reproduced old-vs-direct max divergences of `375.0` and `437.5` counts for `n_avg=4/8`; Shirley and Tougaard stayed identical for the float fixture.
- Scope sweep: `git diff-tree` shows only `autofit/parity.py`, `fitting.py`, `tests/test_background_n_avg.py`, and `tests/autofit/fixtures/u4f_battery_expected.json`. No diffs in `templates/index.html`, `app.py`, `autofit/engine.py`, `autofit/methods`, or lineshapes. I could not run the full pytest suite here because this environment lacks `lmfit` and `scipy`.

VERDICT: GO
