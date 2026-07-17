OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f7267-b71a-7963-9271-33eec5fbd850
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
I’ll review this as a code-review pass and verify the claims from the repo, not from the commit text. I’ll start by reading the target diff, current background implementations, parity/fitting call sites, and the fixture generator/fixtures.
exec
/bin/zsh -lc "rg -n \"def (shirley_background|smart_background|tougaard_background)|_apply_endpoint_averaging|smart_background\\(|shirley_background\\(|tougaard_background\\(\" fitting.py autofit/parity.py tests/test_background_n_avg.py scripts/gen_u4f_battery_fixture.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/test_background_n_avg.py:15:    _apply_endpoint_averaging,
tests/test_background_n_avg.py:41:    assert np.array_equal(shirley_background(x, y), shirley_background(x, y, n_avg=1))
tests/test_background_n_avg.py:49:    raw = shirley_background(x, y, n_avg=1)
tests/test_background_n_avg.py:50:    averaged = shirley_background(x, y, n_avg=8)
tests/test_background_n_avg.py:58:    """Calling shirley_background(x, y, n_avg=N) must equal the OLD calling
tests/test_background_n_avg.py:59:    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
tests/test_background_n_avg.py:63:        direct = shirley_background(x, y, n_avg=n_avg)
tests/test_background_n_avg.py:64:        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
tests/test_background_n_avg.py:70:    assert np.array_equal(smart_background(x, y), smart_background(x, y, n_avg=1))
tests/test_background_n_avg.py:74:    """smart_background(x, y, n_avg=N) must equal
tests/test_background_n_avg.py:75:    minimum(shirley_background(x, y, n_avg=N), y) -- the clamp applies
tests/test_background_n_avg.py:80:        got = smart_background(x, y, n_avg=n_avg)
tests/test_background_n_avg.py:81:        expected = np.minimum(shirley_background(x, y, n_avg=n_avg), y)
tests/test_background_n_avg.py:87:    raw = smart_background(x, y, n_avg=1)
tests/test_background_n_avg.py:88:    averaged = smart_background(x, y, n_avg=8)
tests/test_background_n_avg.py:92:def test_apply_endpoint_averaging_still_importable_and_unchanged():
tests/test_background_n_avg.py:93:    """F3 relocates _apply_endpoint_averaging above shirley_background in
tests/test_background_n_avg.py:96:    out = _apply_endpoint_averaging(y, 2)
autofit/parity.py:98:        bg_inner = shirley_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:100:        bg_inner = smart_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:106:        bg_inner = tougaard_background(xb, yb, n_avg=endpoint_avg)
fitting.py:306:def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
fitting.py:320:def shirley_background(
fitting.py:337:    array themselves via _apply_endpoint_averaging; that convention was
fitting.py:352:        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)
fitting.py:384:def smart_background(
fitting.py:400:    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
fitting.py:528:def tougaard_background(
fitting.py:563:    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
fitting.py:586:        ya = _apply_endpoint_averaging(ya, n_avg)
fitting.py:1050:        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1052:        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1058:        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1288:        bg = shirley_background(x, y, n_avg=endpoint_avg)
fitting.py:1290:        bg = smart_background(x, y, n_avg=endpoint_avg)
fitting.py:1296:        bg = tougaard_background(x, y, n_avg=endpoint_avg)

exec
/bin/zsh -lc 'git show --find-renames --find-copies --stat --patch 3cd6aad -- fitting.py autofit/parity.py tests/test_background_n_avg.py tests/autofit/fixtures/u4f_battery_expected.json' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tHL09RS2' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-U9k6fH7X' (errno=Operation not permitted)
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

exec
/bin/zsh -lc 'git show --stat --oneline 3cd6aad && git show --name-only --format= 3cd6aad' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-wfqIB3SY' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mAnPZEYk' (errno=Operation not permitted)
3cd6aad fix(fitting): unify remaining shirley/smart/tougaard call sites onto n_avg (F3 cont.)
 autofit/parity.py                                |  7 +-
 fitting.py                                       | 12 ++--
 tests/autofit/fixtures/u4f_battery_expected.json | 84 ++++++++++++------------
 tests/test_background_n_avg.py                   | 30 +++++++++
 4 files changed, 81 insertions(+), 52 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-78TcaB6C' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-V3ITV97C' (errno=Operation not permitted)
autofit/parity.py
fitting.py
tests/autofit/fixtures/u4f_battery_expected.json
tests/test_background_n_avg.py

codex
The target commit only reports four changed files, matching the claimed scope at the file-list level. Next I’m going deeper on the function bodies and deriving the project/fixture evidence with small read-only probes.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '300,420p;520,610p;1038,1062p;1278,1300p'" in /Users/skyefortier/xps-verify
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

exec
/bin/zsh -lc "nl -ba autofit/parity.py | sed -n '20,115p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
/bin/zsh -lc "nl -ba scripts/gen_u4f_battery_fixture.py | sed -n '1,260p'" in /Users/skyefortier/xps-verify
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

codex
The line-by-line read supports the core convention distinction so far: `shirley_background` and `tougaard_background` replace their working `y`/`ya` and then operate only on that working array, while `smart_background` computes an averaged Shirley but clamps against the original argument it received. I’m now checking the corpus counts and fixture diff independently.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '610,700p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   651	    return out[::-1] if flipped else out
   652	
   653	
   654	def _la_casaxps_true(
   655	    x: np.ndarray,
   656	    amplitude: float,
   657	    center: float,
   658	    fwhm: float,
   659	    alpha: float,
   660	    beta: float,
   661	    m: float,
   662	) -> np.ndarray:
   663	    """
   664	    True CasaXPS LA(α, β, m) lineshape.
   665	
   666	    Built in two steps per the CasaXPS LA manual:
   667	
   668	    1.  Asymmetric base Lorentzian. Start with a unit-amplitude Lorentzian
   669	        of FWHM `fwhm` centered at `center`:
   670	            L(x) = 1 / (1 + 4·((x − center)/fwhm)²)
   671	        Apply piecewise exponents to introduce asymmetry. CasaXPS defines
   672	        these on a kinetic-energy axis. We use a binding-energy axis, so
   673	        the sides flip:
   674	            LA_base(x) = L(x)^α   for x ≥ center  (high-BE side)
   675	            LA_base(x) = L(x)^β   for x <  center  (low-BE side)
   676	        Increasing α relative to β SUPPRESSES the high-BE tail; decreasing
   677	        α extends it.
   678	
   679	    2.  Gaussian convolution with an integer-point kernel of width `m`.
   680	        m=0 means no convolution. For m>0, build a discrete Gaussian
   681	        kernel of length 2m+1 with σ_pts = m/3 (so the 3σ tail just
   682	        reaches the kernel edge). Convolve with mode='same' on the
   683	        uniform x grid.
   684	
   685	    With α=β=1 and m=0, this reduces exactly to amplitude × L(x) (a pure
   686	    Lorentzian of peak height = amplitude, FWHM = `fwhm`).
   687	
   688	    Parameters
   689	    ----------
   690	    fwhm  : Lorentzian FWHM in eV (must be > 0)
   691	    alpha : high-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
   692	    beta  : low-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
   693	    m     : Gaussian convolution kernel width in DATA POINTS (not eV);
   694	            integer 0–499. Stored as float in lmfit, rounded to int here.
   695	    """
   696	    fwhm = max(float(fwhm), 1e-9)
   697	    alpha = max(float(alpha), 1e-3)
   698	    beta = max(float(beta), 1e-3)
   699	    # Continuous-σ kernel: m flows through to the kernel weights as a real
   700	    # number, so the Jacobian column for m is well-defined under lmfit's

exec
/bin/zsh -lc "find docs/autofit/test_data -name '*.proj.zip' -maxdepth 1 -print | sort" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip
docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
docs/autofit/test_data/8-JT Graphite.proj.zip
docs/autofit/test_data/B4C-UCl4.proj.zip
docs/autofit/test_data/Cl2p_projfit_test.proj.zip
docs/autofit/test_data/Project9_CasaXPS_newfit.proj.zip
docs/autofit/test_data/UCl4_on_graphite.proj.zip

exec
/bin/zsh -lc "rg -n \"def (load_reference_fits|battery_eligible|refit_record)|background|endpointAvg|endpoint_avg|fit-time grid drifted\" autofit scripts tests docs -g '*.py' -g '*.json'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/test_tougaard_background.py:1:"""Tougaard universal-cross-section background — correctness pins.
tests/test_tougaard_background.py:10:   ~20 eV XPS window the shipped "Tougaard" background was essentially
tests/test_tougaard_background.py:16:   binding-energy grid; ascending input silently produced a background
tests/test_tougaard_background.py:20:   shirley_background's ascending normalization.
tests/test_tougaard_background.py:23:   trailing background sample identically zero, so the zero-guard always
tests/test_tougaard_background.py:26:   the background to the measured intensity at the HIGH-BE edge of the
tests/test_tougaard_background.py:28:   fitted so the background meets the spectrum above the peak).
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
tests/test_tougaard_background.py:120:    amplitude is scaled so the background meets the data above the peak),
tests/test_tougaard_background.py:123:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:131:    # still makes the LOSS integral vanish there, so the background equals C0
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
tests/test_tougaard_background.py:245:    got = tougaard_background(xa, ya)
tests/test_tougaard_background.py:273:    """< 2 points: no background can be defined; must return zeros."""
tests/test_tougaard_background.py:275:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
tests/test_tougaard_background.py:277:    assert tougaard_background(np.array([]), np.array([])).size == 0
autofit/candidates.py:33:zero-mean and symmetric, constant and linear backgrounds cancel
autofit/candidates.py:34:identically, and smooth-background curvature only enters through the
autofit/candidates.py:41:background families, and grid steps) and the shoulder/doublet sensitivity
autofit/candidates.py:57:# sigmoid-step backgrounds x counts 100..50000 x steps 0.05/0.1, committed
autofit/candidates.py:138:    Raw counts (not background-subtracted) on purpose: the zero-mean kernel
autofit/candidates.py:139:    cancels constant/linear backgrounds exactly, while subtracting an
autofit/candidates.py:140:    iterative background from a low-structure window injects the background
autofit/candidates.py:364:        channel seed: local-max-only entries can be background-bridging
autofit/candidates.py:406:    background,
autofit/candidates.py:471:    return CandidateModel(name=name, background=background,
autofit/candidates.py:547:    background: np.ndarray,
autofit/candidates.py:583:    background = np.asarray(background, dtype=float)
autofit/candidates.py:599:        x, y, background = x[::-1], y[::-1], background[::-1]
autofit/candidates.py:601:    y_net = y - background
autofit/reference.py:11:- background indices = nearest ROI-grid index to ui.bgStart / ui.bgEnd
autofit/reference.py:205:    def endpoint_avg(self) -> int:
autofit/reference.py:207:            return max(1, int(self.ui.get("endpointAvg", 1)))
autofit/reference.py:254:def load_reference_fits(path: str | Path) -> list[ReferenceFit]:
tests/test_api_analyze_progress.py:14:(instant 400s, unchanged), then spawns a background THREAD (not a
scripts/run_bayesian_real_validation.py:23:  venv/bin/python scripts/run_bayesian_real_validation.py           # full battery (background-scale)
scripts/run_stress_battery.py:127:    rec = _base(case, off, "least_squares", {"background_method":
autofit/engine.py:42:from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background
autofit/engine.py:205:# prominent smoothed local maxima of the background-subtracted DATA that no
autofit/engine.py:287:def _compute_background(
autofit/engine.py:291:    endpoint_avg: int = 1,
autofit/engine.py:295:    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
autofit/engine.py:296:    (audit F3, 2026-07-17). Every background here now takes ``n_avg``
autofit/engine.py:299:    to do, leaving Find Peaks unable to express an endpoint_avg the manual
autofit/engine.py:305:        return shirley_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:307:        return smart_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:309:        from fitting import smart_experimental_background
autofit/engine.py:310:        return smart_experimental_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:312:        return linear_background(x, y)
autofit/engine.py:314:        from fitting import tougaard_background
autofit/engine.py:315:        return tougaard_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:316:    raise ValueError(f"Unknown background type: {bg}")
autofit/engine.py:651:    background: Optional[np.ndarray] = None
autofit/engine.py:847:    """One fit of ``model`` to (x, y, weights); background subtracted first.
autofit/engine.py:866:    bg = _compute_background(x, y, model.background)
autofit/engine.py:902:            n_data=len(y_sub), lmfit_result=None, background=bg,
autofit/engine.py:914:        background=bg,
autofit/engine.py:1183:    # the primary fit's background rather than recomputing per refit.
autofit/engine.py:1184:    bg = primary_fit.background
autofit/engine.py:1738:    amplitude_net: float          # smoothed background-subtracted height
autofit/engine.py:1788:    background: np.ndarray,
autofit/engine.py:1794:    Prominent smoothed local maxima of the background-subtracted data that
autofit/engine.py:1805:        x_asc, y_asc, bg_asc = x[::-1], y[::-1], background[::-1]
autofit/engine.py:1807:        x_asc, y_asc, bg_asc = x, y, background
autofit/engine.py:1899:        background=base.background,
autofit/engine.py:2106:        background=base.background,
autofit/engine.py:2182:    bg = _compute_background(x, y, aug_model.background)
autofit/engine.py:2290:    y_fit_aug = (primary.lmfit_result.best_fit + primary.background
autofit/engine.py:2429:    y_fit = (outcome.lmfit_result.best_fit + outcome.background
autofit/engine.py:2581:        # Detection-only background: today every candidate in a resolved
autofit/engine.py:2582:        # grammar shares one background family (C 1s/B 1s/Cl 2p/U 4f modules
autofit/engine.py:2584:        # A future mixed-background grammar only affects DETECTION here —
autofit/engine.py:2585:        # each candidate still fits with its own background.  Structural-
autofit/engine.py:2588:        # background (CLAUDE.md convention).
autofit/engine.py:2589:        det_bg_family = (candidates[0].background if candidates
autofit/engine.py:2591:        det_bg = _compute_background(x, y, det_bg_family)
autofit/engine.py:2802:                 (primary.background if primary.background is not None else 0.0)
autofit/engine.py:2885:                            pf.lmfit_result.best_fit + pf.background
tests/test_api_analyze.py:104:        "options": {"background_method": "linear"},
autofit/grammar.py:166:    """A candidate model M = (background, slots) with admissibility built in."""
autofit/grammar.py:168:    background: BackgroundType
autofit/grammar.py:526:    multiple phases) to stay unique; the shared window uses ONE background
autofit/grammar.py:531:        backgrounds = {c.background for c in combo}
autofit/grammar.py:532:        if len(backgrounds) != 1:
autofit/grammar.py:534:                f"joint candidates must share one background, got {backgrounds} "
autofit/grammar.py:549:            background=combo[0].background,
autofit/parity.py:8:   ``fitting.py``'s lineshape functions (+ the exact background
autofit/parity.py:31:    linear_background,
autofit/parity.py:32:    shirley_background,
autofit/parity.py:33:    shirley_linear_background,
autofit/parity.py:34:    smart_background,
autofit/parity.py:35:    smart_experimental_background,
autofit/parity.py:36:    tougaard_background,
autofit/parity.py:62:    """Sum of all peak evaluations (no background)."""
autofit/parity.py:69:def background_like_run_fit(
autofit/parity.py:75:    endpoint_avg: int = 1,
autofit/parity.py:78:    Reproduce exactly the background array ``run_fit`` constructs — including
autofit/parity.py:98:        bg_inner = shirley_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:100:        bg_inner = smart_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:102:        bg_inner = smart_experimental_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:104:        bg_inner = shirley_linear_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:106:        bg_inner = tougaard_background(xb, yb, n_avg=endpoint_avg)
autofit/parity.py:116:        raise ValueError(f"Unknown background method {method!r}")
autofit/parity.py:132:def battery_eligible(rf: ReferenceFit, region: str = "C 1s") -> tuple[bool, str]:
autofit/parity.py:150:        return False, "fit-time grid drifted from current ui state"
autofit/parity.py:180:    bg = background_like_run_fit(
autofit/parity.py:181:        rf.roi_be, rf.roi_intensity, rf.bg_method, i0, i1, rf.endpoint_avg
autofit/parity.py:187:def refit_record(rf: ReferenceFit) -> dict[str, Any]:
autofit/parity.py:197:        background_method=rf.bg_method,
autofit/parity.py:200:        endpoint_avg=rf.endpoint_avg,
scripts/calibrate_cwt_detector.py:13:   linear-drift / sigmoid-step backgrounds x counts 100..50000 x grid
scripts/summarize_stress_battery.py:226:        "2. **Endpoint-anchored linear background + Lorentzian tails set a "
scripts/summarize_stress_battery.py:231:        "land below the truth-under-wrong-background score by bending "
scripts/summarize_stress_battery.py:234:        "absolute χ²-target criteria are miscalibrated whenever background "
scripts/summarize_stress_battery.py:236:        "the same integral background well (control case χ²ᵣ 1.24). Feeds "
scripts/summarize_stress_battery.py:299:        "tails, background curvature — those honesty cases surface via "
autofit/methods/ic_model_comparison.py:349:            "autocorrelation and background misspecification — see "
autofit/methods/sparse_map.py:44:from ..engine import _compute_background
autofit/methods/sparse_map.py:198:        bg = _compute_background(x, y, grammar.candidates[0].background)
autofit/methods/least_squares.py:21:    "background_method", "bg_start_idx", "bg_end_idx", "endpoint_avg",
autofit/methods/least_squares.py:54:            background_method=opts.pop("background_method", "shirley"),
autofit/methods/least_squares.py:57:            endpoint_avg=opts.pop("endpoint_avg", 1),
tests/test_browser_cc_overlay_repaint.py:108:# column reads as background (a handful). Returns {blue, white, sampled}.
autofit/methods/bayesian_exchange_mc.py:57:    _compute_background,
autofit/methods/bayesian_exchange_mc.py:348:            bg = _compute_background(x, y, model.background)
tests/test_browser_identify_frame.py:220:        bg: getComputedStyle(document.getElementById('ref-identify-popover')).backgroundColor })""")
tests/test_browser_identify_frame.py:230:            bg: (()=>{const p=document.getElementById('ref-identify-popover');return p?getComputedStyle(p).backgroundColor:null;})() })""")
autofit/regions/u4f.py:108:# Shirley) background — adopted to match expert practice; UNVERIFIED
autofit/regions/u4f.py:156:            {"constant": "background", "value": "smart",
autofit/regions/u4f.py:259:            CandidateModel(name="U0_mains", background=U4F_BACKGROUND,
autofit/regions/u4f.py:261:            CandidateModel(name="U1_mains_satpair", background=U4F_BACKGROUND,
autofit/regions/u4f.py:264:                           background=U4F_BACKGROUND,
autofit/regions/u4f.py:266:            CandidateModel(name="U2_mains_satfree", background=U4F_BACKGROUND,
autofit/methods/multivariate_mcr.py:136:            # intensities (over-subtracted background) violate it
autofit/methods/multivariate_mcr.py:138:                             "background over-subtraction before MCR")
tests/test_browser_batch_roi.py:3:The bug: runPropagation() copied only the background fields into each target's
tests/test_browser_batch_roi.py:4:UI, omitting the ROI, so batch fit changed the background but left every target's
autofit/regions/n1s.py:38:# Matches the U 4f family so joint co-fit candidates share one background
autofit/regions/n1s.py:39:# (composition requires background agreement).  UNVERIFIED choice.
autofit/regions/n1s.py:59:            {"constant": "background", "value": "smart",
autofit/regions/n1s.py:83:            CandidateModel(name="N0_pv", background=N1S_BACKGROUND,
autofit/regions/n1s.py:85:            CandidateModel(name="N0_asymGL", background=N1S_BACKGROUND,
tests/test_browser_find_peaks_full_window.py:12:background/fit-curve rendering to ``state.fitResult``'s own frozen
tests/test_browser_find_peaks_full_window.py:16:left the chart showing background/fit cropped to whatever OLD, possibly
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
autofit/regions/b1s.py:77:            {"constant": "background", "value": "smart_exp",
autofit/regions/b1s.py:103:            return CandidateModel(name=name, background=B1S_BACKGROUND,
tests/autofit/battery_common.py:28:#   'smart' backgrounds that perturbs the recomputed background by
tests/autofit/battery_common.py:30:#   deviation profile exactly matching the background, not the shapes).
tests/autofit/test_stage2_rereview_findings.py:41:    y_fit = fit.lmfit_result.best_fit + fit.background
autofit/regions/c1s.py:272:                name=name, background=BackgroundType.SHIRLEY,
tests/autofit/test_c1s_parity_gate.py:54:from fitting import shirley_background
tests/autofit/test_c1s_parity_gate.py:171:    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(
tests/autofit/test_c1s_parity_battery.py:13:   fitting.py's lineshapes + run_fit's background reconstruction reproduces
tests/autofit/stress_cases.py:10:expressible (linear) in every regime except the background-mismatch regime,
tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
tests/autofit/stress_cases.py:33:the true baseline at the ROI edges — and the engine's LINEAR background is
tests/autofit/stress_cases.py:35:the engine-background χ²ᵣ is therefore not 1: measured 0.96 with the true
tests/autofit/stress_cases.py:36:baseline vs 34 with the engine background at height 90000 (≈2 at 9000 —
tests/autofit/stress_cases.py:38:This is the REALISTIC background-subtraction problem, kept on purpose:
tests/autofit/stress_cases.py:80:    bg: str = "linear"                       # generator background family
tests/autofit/stress_cases.py:95:    """Integral (Shirley-shaped) background: proportional to the signal area
tests/autofit/stress_cases.py:114:    return CandidateModel(name=name, background=bg, slots=tuple(slots))
tests/autofit/stress_cases.py:323:# Regime 6 — background mismatch (Shirley-shaped truth, linear-only fits)
tests/autofit/stress_cases.py:364:    endpoint-anchored linear background.)
tests/autofit/stress_cases.py:418:        notes="integral background fit with a straight line — the mismatch "
tests/autofit/stress_cases.py:425:    The engine's iterative Shirley should absorb the integral background."""
tests/autofit/stress_cases.py:440:        notes="control: matched background family",
tests/autofit/stress_cases.py:488:        # background mismatch + control
tests/test_background_n_avg.py:1:"""F3 regression tests (2026-07-17 background audit): shirley_background and
tests/test_background_n_avg.py:2:smart_background must accept n_avg directly, matching the convention already
tests/test_background_n_avg.py:3:used by smart_experimental_background / shirley_linear_background, and
tests/test_background_n_avg.py:4:autofit/engine.py's _compute_background must forward an endpoint_avg knob to
tests/test_background_n_avg.py:5:every background type it dispatches.
tests/test_background_n_avg.py:16:    compute_background_only,
tests/test_background_n_avg.py:17:    shirley_background,
tests/test_background_n_avg.py:18:    smart_background,
tests/test_background_n_avg.py:19:    smart_experimental_background,
tests/test_background_n_avg.py:20:    tougaard_background,
tests/test_background_n_avg.py:27:    B_low/B_high and therefore the whole background curve."""
tests/test_background_n_avg.py:37:def test_shirley_background_default_n_avg_matches_pre_f3_output():
tests/test_background_n_avg.py:41:    assert np.array_equal(shirley_background(x, y), shirley_background(x, y, n_avg=1))
tests/test_background_n_avg.py:44:def test_shirley_background_n_avg_changes_output_on_noisy_endpoints():
tests/test_background_n_avg.py:49:    raw = shirley_background(x, y, n_avg=1)
tests/test_background_n_avg.py:50:    averaged = shirley_background(x, y, n_avg=8)
tests/test_background_n_avg.py:52:        "n_avg=8 produced the same background as n_avg=1 on a fixture with "
tests/test_background_n_avg.py:57:def test_shirley_background_n_avg_matches_external_pre_averaging():
tests/test_background_n_avg.py:58:    """Calling shirley_background(x, y, n_avg=N) must equal the OLD calling
tests/test_background_n_avg.py:59:    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
tests/test_background_n_avg.py:63:        direct = shirley_background(x, y, n_avg=n_avg)
tests/test_background_n_avg.py:64:        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
tests/test_background_n_avg.py:68:def test_smart_background_default_n_avg_matches_pre_f3_output():
tests/test_background_n_avg.py:70:    assert np.array_equal(smart_background(x, y), smart_background(x, y, n_avg=1))
tests/test_background_n_avg.py:73:def test_smart_background_forwards_n_avg_to_shirley():
tests/test_background_n_avg.py:74:    """smart_background(x, y, n_avg=N) must equal
tests/test_background_n_avg.py:75:    minimum(shirley_background(x, y, n_avg=N), y) -- the clamp applies
tests/test_background_n_avg.py:77:    ever moves the background curve, never the reported net counts."""
tests/test_background_n_avg.py:80:        got = smart_background(x, y, n_avg=n_avg)
tests/test_background_n_avg.py:81:        expected = np.minimum(shirley_background(x, y, n_avg=n_avg), y)
tests/test_background_n_avg.py:85:def test_smart_background_n_avg_changes_output_on_noisy_endpoints():
tests/test_background_n_avg.py:87:    raw = smart_background(x, y, n_avg=1)
tests/test_background_n_avg.py:88:    averaged = smart_background(x, y, n_avg=8)
tests/test_background_n_avg.py:93:    """F3 relocates _apply_endpoint_averaging above shirley_background in
tests/test_background_n_avg.py:100:def test_compute_background_default_endpoint_avg_matches_pre_f3_output():
tests/test_background_n_avg.py:101:    """autofit/engine.py's _compute_background(x, y, bg) with no
tests/test_background_n_avg.py:102:    endpoint_avg argument must reproduce pre-F3 output exactly, for every
tests/test_background_n_avg.py:103:    background type it dispatches -- pure wiring, no behaviour change."""
tests/test_background_n_avg.py:104:    from autofit.engine import BackgroundType, _compute_background
tests/test_background_n_avg.py:110:        no_arg = _compute_background(x, y, bg_type)
tests/test_background_n_avg.py:111:        default_arg = _compute_background(x, y, bg_type, endpoint_avg=1)
tests/test_background_n_avg.py:116:    ("SHIRLEY", shirley_background),
tests/test_background_n_avg.py:117:    ("SMART", smart_background),
tests/test_background_n_avg.py:118:    ("SMART_EXP", smart_experimental_background),
tests/test_background_n_avg.py:119:    ("TOUGAARD", tougaard_background),
tests/test_background_n_avg.py:121:def test_compute_background_forwards_endpoint_avg(bg_type_name, direct_fn):
tests/test_background_n_avg.py:122:    """_compute_background(x, y, bg, endpoint_avg=N) must match calling the
tests/test_background_n_avg.py:124:    manual Run Fit must agree once both pass the same endpoint_avg."""
tests/test_background_n_avg.py:125:    from autofit.engine import BackgroundType, _compute_background
tests/test_background_n_avg.py:130:        via_engine = _compute_background(x, y, bg_type, endpoint_avg=n_avg)
tests/test_background_n_avg.py:133:            f"{bg_type_name} mismatch at endpoint_avg={n_avg}"
tests/test_background_n_avg.py:137:def test_compute_background_linear_ignores_endpoint_avg():
tests/test_background_n_avg.py:138:    """linear_background has no endpoint-averaging concept (it already
tests/test_background_n_avg.py:139:    reads only the two edge points); endpoint_avg must be accepted without
tests/test_background_n_avg.py:141:    from autofit.engine import BackgroundType, _compute_background
tests/test_background_n_avg.py:144:    no_avg = _compute_background(x, y, BackgroundType.LINEAR)
tests/test_background_n_avg.py:145:    with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
tests/test_background_n_avg.py:150:def test_compute_background_only_matches_direct_call_with_n_avg(method):
tests/test_background_n_avg.py:151:    """The manual /api/background and /api/fit dispatch (compute_background_only,
tests/test_background_n_avg.py:154:    the whole point of F3 is that Find Peaks (via _compute_background) and
tests/test_background_n_avg.py:155:    manual Run Fit agree once both pass the same endpoint_avg.
tests/test_background_n_avg.py:157:    This is the parity gap Codex review caught in c5a24ac: smart_background
tests/test_background_n_avg.py:159:    (the old convention, still used by compute_background_only/run_fit/
tests/test_background_n_avg.py:163:    once endpoint_avg > 1 is used (shirley/tougaard have no such post-hoc
tests/test_background_n_avg.py:166:    direct_fn = {"shirley": shirley_background, "smart": smart_background,
tests/test_background_n_avg.py:167:                 "tougaard": tougaard_background}[method]
tests/test_background_n_avg.py:169:        result = compute_background_only(x, y, method=method, endpoint_avg=n_avg)
tests/test_background_n_avg.py:170:        via_dispatch = np.array(result["background"])
autofit/regions/cl2p.py:102:            {"constant": "background", "value": "smart_exp",
autofit/regions/cl2p.py:160:            CandidateModel(name="Cl0_doublet", background=CL2P_BACKGROUND,
autofit/regions/cl2p.py:163:                           background=CL2P_BACKGROUND,
autofit/regions/cl2p.py:170:                           background=CL2P_BACKGROUND,
autofit/regions/cl2p.py:174:                           background=CL2P_BACKGROUND,
tests/test_mixed_ds_lacx_e2e.py:54:    background_method='none',
tests/autofit/test_criteria.py:31:                           background=BackgroundType.SHIRLEY,
tests/autofit/test_methods_seam.py:51:    res = m.run(x, y, peak_specs=specs, options={"background_method": "shirley"})
tests/autofit/test_preseed_dominants.py:62:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:85:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:104:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:177:    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
tests/autofit/test_preseed_dominants.py:200:    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
tests/autofit/test_preseed_dominants.py:262:    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
tests/autofit/test_preseed_dominants.py:290:    y_fit = (base.primary_fit.lmfit_result.best_fit + base.primary_fit.background)
tests/autofit/test_preseed_dominants.py:298:    bg = eng._compute_background(x, y, aug_model.background)
tests/autofit/test_preseed_dominants.py:368:    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:382:    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:434:             + base_report.primary_fit.background)
autofit/criteria.py:63:    identical line shapes on the shared roles (and identical backgrounds).
autofit/criteria.py:66:    if smaller.model.background is not larger.model.background:
tests/autofit/test_cl2p_freewidth.py:136:        name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:148:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:159:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:177:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:190:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:203:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_max_entropy.py:69:    """Iterative deconvolution inherently amplifies background noise (~10×
tests/autofit/test_cwt_detector.py:112:    linear backgrounds cancel identically — drift must produce nothing."""
tests/autofit/test_candidate_pool_real_gate.py:101:    det_bg = eng._compute_background(x, y, cands[0].background)
tests/autofit/test_stress_honesty.py:62:        options={"background_method": "linear"})
tests/autofit/test_sparse_map.py:34:    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:160:    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:162:    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
tests/autofit/test_resolver.py:120:            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:122:            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
tests/autofit/test_engine_doublet.py:36:    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
tests/autofit/test_engine_doublet.py:134:        name="joint", background=BackgroundType.SHIRLEY,
docs/autofit/test_data/U4f_5_Scan1_newCasaXPS_FitAllFree.fit.json.fit.json:342:  "background": {
tests/autofit/fixtures/b1s_battery_expected.json:86:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/b1s_battery_expected.json:91:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/b1s_battery_expected.json:96:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/b1s_battery_expected.json:101:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/b1s_battery_expected.json:106:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/test_u4f_parity_battery.py:19:# Bounded by background-anchor drift / LACX FP wobble — measured and
tests/autofit/fixtures/u4f_battery_expected.json:1102:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1107:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1112:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1117:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1122:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1127:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1132:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1207:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1212:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1217:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/fixtures/u4f_battery_expected.json:1222:   "reason": "fit-time grid drifted from current ui state"
tests/autofit/test_bayesian_method.py:35:    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:37:    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:40:    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:254:    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:257:    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
tests/autofit/test_fit_full_window_option.py:47:    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))
tests/autofit/test_stage2_completeness.py:53:    y_fit = rep.primary_fit.lmfit_result.best_fit + rep.primary_fit.background
tests/autofit/test_stage2_completeness.py:296:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:321:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:372:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:397:    dom = e2.detect_out_of_grammar_dominants(x, y, e2._compute_background(
tests/autofit/test_candidate_pool.py:153:    (Shirley) as in production — a zeros background makes the height
tests/autofit/test_candidate_pool.py:158:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool.py:342:    background) stay OUT of the pool payload — overcomplete does not mean
tests/autofit/test_candidate_pool.py:344:    background, which absorbs the flat baseline)."""
tests/autofit/test_candidate_pool.py:345:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)

exec
/bin/zsh -lc "nl -ba autofit/reference.py | sed -n '1,290p'" in /Users/skyefortier/xps-verify
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
/bin/zsh -lc "nl -ba autofit/parity.py | sed -n '120,230p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   211	            "area": par["area"]["value"],
   212	        })
   213	    return {
   214	        "project": rf.project,
   215	        "name": rf.name,
   216	        "reduced_chi_square": res["statistics"]["reduced_chi_square"],
   217	        "r_factor": res["statistics"]["r_factor"],
   218	        "success": bool(res["success"]),
   219	        "peaks": peaks,
   220	    }

exec
/bin/zsh -lc "unzip -l 'docs/autofit/test_data/4-GTA UCl4-BN.proj.zip' | sed -n '1,120p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
Archive:  docs/autofit/test_data/4-GTA UCl4-BN.proj.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
    22454  06-25-2026 00:13   spectrum_0_B1s_Scan.json
    45401  06-25-2026 00:13   spectrum_1_U4f_Scan.json
    20746  06-25-2026 00:13   spectrum_2_B1s_Scan_0.json
    45260  06-25-2026 00:13   spectrum_3_U4f_Scan_0.json
    20790  06-25-2026 00:13   spectrum_4_B1s_Scan_1.json
    45145  06-25-2026 00:13   spectrum_5_U4f_Scan_1.json
    20754  06-25-2026 00:13   spectrum_6_B1s_Scan_2.json
    45519  06-25-2026 00:13   spectrum_7_U4f_Scan_2.json
    20734  06-25-2026 00:13   spectrum_8_B1s_Scan_3.json
    45550  06-25-2026 00:13   spectrum_9_U4f_Scan_3.json
    20850  06-25-2026 00:13   spectrum_10_B1s_Scan_4.json
    45433  06-25-2026 00:13   spectrum_11_U4f_Scan_4.json
    20303  06-25-2026 00:13   spectrum_12_B1s_Scan_5.json
    50239  06-25-2026 00:13   spectrum_13_U4f_Scan_5.json
    22445  06-25-2026 00:13   spectrum_14_B1s_Scan_6.json
    44898  06-25-2026 00:13   spectrum_15_U4f_Scan_6.json
    22362  06-25-2026 00:13   spectrum_16_B1s_Scan_7.json
    45671  06-25-2026 00:13   spectrum_17_U4f_Scan_7.json
    20301  06-25-2026 00:13   spectrum_18_B1s_Scan_8.json
    45648  06-25-2026 00:13   spectrum_19_U4f_Scan_8.json
     2782  06-25-2026 00:13   manifest.json
---------                     -------
   673285                     21 files

exec
/bin/zsh -lc 'rg -n "_apply_endpoint_averaging" autofit/parity.py && true' in /Users/skyefortier/xps-verify
 exited 1 in 0ms:
codex
The shell cannot create heredoc temp files in this read-only sandbox, so I’m switching the probes to `python -c` one-liners that only read repo data. The previous grep for `_apply_endpoint_averaging` in `autofit/parity.py` returned no matches.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python -c $'"'from pathlib import Path\\nfrom autofit.reference import load_reference_fits\\nfrom autofit.parity import battery_eligible\\nrows=[]\\nfor zp in sorted(Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\")):\\n    for rf in load_reference_fits(zp):\\n        if (rf.bg_method or \"\").lower()==\"smart\" and rf.endpoint_avg>1:\\n            ok, reason = battery_eligible(rf, region=\"U 4f\")\\n            rows.append((rf.project, rf.name, rf.tab_file, rf.region_guess(), rf.bg_method, rf.endpoint_avg, ok, reason, len(rf.fit_result.get(\"be\") or []), len(rf.roi_be)))\\nprint(\"count\", len(rows))\\nfor r in rows:\\n    print(\"\\\\t\".join(map(str,r)))'" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python -c $'"'from pathlib import Path\\nfrom autofit.reference import load_reference_fits\\nfrom autofit.parity import battery_eligible\\nrecords=[]; skipped=[]\\nfor zp in sorted(Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\")):\\n    for rf in load_reference_fits(zp):\\n        ok, reason = battery_eligible(rf, region=\"U 4f\")\\n        if ok: records.append((rf.project, rf.name, rf.bg_method, rf.endpoint_avg))\\n        elif reason "'!= "not U 4f": skipped.append((rf.project, rf.name, rf.bg_method, rf.endpoint_avg, reason))'"\\nprint(\"eligible records\", len(records))\\nprint(\"smart endpoint>1 eligible\", [r for r in records if str(r[2]).lower()==\"smart\" and r[3]>1])\\nprint(\"skipped\", len(skipped))\\nfor s in skipped:\\n    marker = \" SMART_GT1\" if str(s[2]).lower()==\"smart\" and s[3]>1 else \"\"\\n    print(\"\\\\t\".join(map(str,s))+marker)'" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python -c $'"'import json, subprocess\\nfrom pathlib import Path\\nold=json.loads(subprocess.check_output([\"git\",\"show\",\"3cd6aad"'^:tests/autofit/fixtures/u4f_battery_expected.json"]))'"\\nnew=json.loads(Path(\"tests/autofit/fixtures/u4f_battery_expected.json\").read_text())\\nold_records={(r[\"project\"],r[\"name\"]):r for r in old[\"records\"]}\\nnew_records={(r[\"project\"],r[\"name\"]):r for r in new[\"records\"]}\\nprint(\"old records\", len(old_records), \"new records\", len(new_records), \"old skipped\", len(old.get(\"skipped\",[])), \"new skipped\", len(new.get(\"skipped\",[])))\\nprint(\"record keys changed\", sorted(set(old_records)"'^set(new_records)))'"\\nprint(\"skipped equal\", old.get(\"skipped\",[]) == new.get(\"skipped\",[]))\\ndef walk(o,n,path=\"\"):\\n    diffs=[]\\n    if isinstance(o,dict) and isinstance(n,dict):\\n        for k in sorted(set(o)|set(n)):\\n            diffs += walk(o.get(k,\"<MISSING>\"), n.get(k,\"<MISSING>\"), f\"{path}.{k}\" if path else str(k))\\n    elif isinstance(o,list) and isinstance(n,list):\\n        for i,(oi,ni) in enumerate(zip(o,n)):\\n            diffs += walk(oi,ni,f\"{path}[{i}]\")\\n        if len(o)"'!=len(n): diffs.append((path+".length",len(o),len(n),float("inf")))'"\\n    elif isinstance(o,(int,float)) and isinstance(n,(int,float)) and not isinstance(o,bool) and not isinstance(n,bool):\\n        absd=abs(float(n)-float(o)); denom=max(abs(float(o)),1e-300); rel=absd/denom\\n        if absd"'!=0: diffs.append((path,o,n,rel))'"\\n    else:\\n        if o"'!=n: diffs.append((path,o,n,float("inf")))'"\\n    return diffs\\nmeaningful=[]; tiny=[]\\nfor key in sorted(old_records):\\n    ds=walk(old_records[key], new_records[key])\\n    if ds:\\n        maxrel=max(d[3] for d in ds)\\n        gt=[d for d in ds if d[3] > 1e-6]\\n        if gt: meaningful.append((key, maxrel, len(ds), len(gt), gt[:8]))\\n        else: tiny.append((key, maxrel, len(ds)))\\nprint(\"records with any diff\", len(meaningful)+len(tiny))\\nprint(\"meaningful >1e-6\", len(meaningful))\\nfor key,maxrel,nd,ngt,first in meaningful:\\n    print(\"MEANINGFUL\", key, \"maxrel\", maxrel, \"numdiffs\", nd, \"gt\", ngt)\\n    for d in first: print(\" \", d)\\nprint(\"tiny records\", len(tiny))\\nfor t in tiny: print(\"TINY\", t)'" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'rg -n "_apply_endpoint_averaging" autofit/parity.py' in /Users/skyefortier/xps-verify
 exited 1 in 0ms:
codex
`python` is not on PATH here; I’m using `python3` for the same read-only probes.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from pathlib import Path\\nfrom autofit.reference import load_reference_fits\\nfrom autofit.parity import battery_eligible\\nrecords=[]; skipped=[]\\nfor zp in sorted(Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\")):\\n    for rf in load_reference_fits(zp):\\n        ok, reason = battery_eligible(rf, region=\"U 4f\")\\n        if ok: records.append((rf.project, rf.name, rf.bg_method, rf.endpoint_avg))\\n        elif reason "'!= "not U 4f": skipped.append((rf.project, rf.name, rf.bg_method, rf.endpoint_avg, reason))'"\\nprint(\"eligible records\", len(records))\\nprint(\"smart endpoint>1 eligible\", [r for r in records if str(r[2]).lower()==\"smart\" and r[3]>1])\\nprint(\"skipped\", len(skipped))\\nfor s in skipped:\\n    marker = \" SMART_GT1\" if str(s[2]).lower()==\"smart\" and s[3]>1 else \"\"\\n    print(\"\\\\t\".join(map(str,s))+marker)'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from pathlib import Path\\nfrom autofit.reference import load_reference_fits\\nfrom autofit.parity import battery_eligible\\nrows=[]\\nfor zp in sorted(Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\")):\\n    for rf in load_reference_fits(zp):\\n        if (rf.bg_method or \"\").lower()==\"smart\" and rf.endpoint_avg>1:\\n            ok, reason = battery_eligible(rf, region=\"U 4f\")\\n            rows.append((rf.project, rf.name, rf.tab_file, rf.region_guess(), rf.bg_method, rf.endpoint_avg, ok, reason, len(rf.fit_result.get(\"be\") or []), len(rf.roi_be)))\\nprint(\"count\", len(rows))\\nfor r in rows:\\n    print(\"\\\\t\".join(map(str,r)))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import json, subprocess\\nfrom pathlib import Path\\nold=json.loads(subprocess.check_output([\"git\",\"show\",\"3cd6aad"'^:tests/autofit/fixtures/u4f_battery_expected.json"]))'"\\nnew=json.loads(Path(\"tests/autofit/fixtures/u4f_battery_expected.json\").read_text())\\nold_records={(r[\"project\"],r[\"name\"]):r for r in old[\"records\"]}\\nnew_records={(r[\"project\"],r[\"name\"]):r for r in new[\"records\"]}\\nprint(\"old records\", len(old_records), \"new records\", len(new_records), \"old skipped\", len(old.get(\"skipped\",[])), \"new skipped\", len(new.get(\"skipped\",[])))\\nprint(\"record keys changed\", sorted(set(old_records)"'^set(new_records)))'"\\nprint(\"skipped equal\", old.get(\"skipped\",[]) == new.get(\"skipped\",[]))\\ndef walk(o,n,path=\"\"):\\n    diffs=[]\\n    if isinstance(o,dict) and isinstance(n,dict):\\n        for k in sorted(set(o)|set(n)):\\n            diffs += walk(o.get(k,\"<MISSING>\"), n.get(k,\"<MISSING>\"), f\"{path}.{k}\" if path else str(k))\\n    elif isinstance(o,list) and isinstance(n,list):\\n        for i,(oi,ni) in enumerate(zip(o,n)):\\n            diffs += walk(oi,ni,f\"{path}[{i}]\")\\n        if len(o)"'!=len(n): diffs.append((path+".length",len(o),len(n),float("inf")))'"\\n    elif isinstance(o,(int,float)) and isinstance(n,(int,float)) and not isinstance(o,bool) and not isinstance(n,bool):\\n        absd=abs(float(n)-float(o)); denom=max(abs(float(o)),1e-300); rel=absd/denom\\n        if absd"'!=0: diffs.append((path,o,n,rel))'"\\n    else:\\n        if o"'!=n: diffs.append((path,o,n,float("inf")))'"\\n    return diffs\\nmeaningful=[]; tiny=[]\\nfor key in sorted(old_records):\\n    ds=walk(old_records[key], new_records[key])\\n    if ds:\\n        maxrel=max(d[3] for d in ds)\\n        gt=[d for d in ds if d[3] > 1e-6]\\n        if gt: meaningful.append((key, maxrel, len(ds), len(gt), gt[:8]))\\n        else: tiny.append((key, maxrel, len(ds)))\\nprint(\"records with any diff\", len(meaningful)+len(tiny))\\nprint(\"meaningful >1e-6\", len(meaningful))\\nfor key,maxrel,nd,ngt,first in meaningful:\\n    print(\"MEANINGFUL\", key, \"maxrel\", maxrel, \"numdiffs\", nd, \"gt\", ngt)\\n    for d in first: print(\" \", d)\\nprint(\"tiny records\", len(tiny))\\nfor t in tiny: print(\"TINY\", t)'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-fZG6UFnu' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-7Vmkl9dc' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-alipiEs4' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xob2Smnh' (errno=Operation not permitted)
old records 29 new records 29 old skipped 25 new skipped 25
record keys changed []
skipped equal True
records with any diff 2
meaningful >1e-6 1
MEANINGFUL ('4-GTA UCl4-BN.proj.zip', 'U4f Scan') maxrel 0.01039766318574189 numdiffs 20 gt 16
  ('peaks[0].amplitude', 7635.766080337974, 7634.934773080449, 0.00010887018391845735)
  ('peaks[0].area', -21878.05776656253, -21862.45840089331, 0.0007130141914637412)
  ('peaks[0].fwhm', 2.4788582828809957, 2.4773151720223288, 0.0006225087046418564)
  ('peaks[1].amplitude', 5726.824560253481, 5726.2010798103365, 0.00010887018391857645)
  ('peaks[1].area', -16006.332799581052, -15995.158743198761, 0.000698102215054772)
  ('peaks[1].fwhm', 2.4788582828809957, 2.4773151720223288, 0.0006225087046418564)
  ('peaks[2].amplitude', 1582.68042844834, 1583.0468828413811, 0.0002315403580243544)
  ('peaks[2].area', -6691.060197214448, -6713.665921082466, 0.0033784965613416038)
tiny records 1
TINY (('4-GTA UCl4-BN.proj.zip', 'U4f Scan_5'), 1.4877233295964742e-12, 22)

 exited 1 in 146ms:
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/Users/skyefortier/xps-verify/autofit/parity.py", line 29, in <module>
    from fitting import (
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

 exited 1 in 143ms:
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/Users/skyefortier/xps-verify/autofit/parity.py", line 29, in <module>
    from fitting import (
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

exec
/bin/zsh -lc "find . -maxdepth 2 -type f -path '*/bin/python*' -o -type f -path '*/bin/pytest'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
The base `python3` can read project JSON but lacks the app’s runtime dependencies, so I’m avoiding imports that transitively need `lmfit` for corpus counting. The fixture diff already shows one meaningful changed record plus one tiny-noise record.
exec
/bin/zsh -lc "find . -maxdepth 3 \\( -path './venv/bin/python' -o -path './.venv/bin/python' -o -path './venv/bin/pytest' -o -path './.venv/bin/pytest' \\) -print" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from pathlib import Path\\nimport numpy as np\\nfrom autofit.reference import load_reference_fits\\ndef grid_matches(rf,tol=1e-3):\\n    saved=rf.fit_result.get(\"be\")\\n    if not saved: return False\\n    roi=rf.roi_be\\n    if len(saved)"'!=len(roi): return False'"\\n    return float(np.max(np.abs(np.asarray(saved,dtype=float)-roi))) <= tol\\ndef eligible(rf, region=\"U 4f\"):\\n    if rf.region_guess()"'!=region: return False, "not "+region'"\\n    fr=rf.fit_result\\n    if not fr.get(\"fittedY\") or not fr.get(\"be\"): return False, \"legacy fitResult (no be/fittedY)\"\\n    if len(fr[\"fittedY\"]) "'!= len(fr["be"]): return False, "internally inconsistent fitResult"'"\\n    if not grid_matches(rf): return False, \"fit-time grid drifted from current ui state\"\\n    return True, \"\"\\nrows=[]\\nfor zp in sorted(Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\")):\\n    for rf in load_reference_fits(zp):\\n        if (rf.bg_method or \"\").lower()==\"smart\" and rf.endpoint_avg>1:\\n            ok, reason=eligible(rf,\"U 4f\")\\n            rows.append((rf.project, rf.name, rf.tab_file, rf.region_guess(), rf.bg_method, rf.endpoint_avg, ok, reason, len(rf.fit_result.get(\"be\") or []), len(rf.roi_be)))\\nprint(\"count\", len(rows))\\nfor r in rows: print(\"\\\\t\".join(map(str,r)))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from pathlib import Path\\nimport numpy as np\\nfrom autofit.reference import load_reference_fits\\ndef grid_matches(rf,tol=1e-3):\\n    saved=rf.fit_result.get(\"be\")\\n    if not saved: return False\\n    roi=rf.roi_be\\n    if len(saved)"'!=len(roi): return False'"\\n    return float(np.max(np.abs(np.asarray(saved,dtype=float)-roi))) <= tol\\ndef eligible(rf, region=\"U 4f\"):\\n    if rf.region_guess()"'!=region: return False, "not "+region'"\\n    fr=rf.fit_result\\n    if not fr.get(\"fittedY\") or not fr.get(\"be\"): return False, \"legacy fitResult (no be/fittedY)\"\\n    if len(fr[\"fittedY\"]) "'!= len(fr["be"]): return False, "internally inconsistent fitResult"'"\\n    if not grid_matches(rf): return False, \"fit-time grid drifted from current ui state\"\\n    return True, \"\"\\nrecords=[]; skipped=[]\\nfor zp in sorted(Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\")):\\n    for rf in load_reference_fits(zp):\\n        ok, reason=eligible(rf,\"U 4f\")\\n        if ok: records.append((rf.project, rf.name, rf.bg_method, rf.endpoint_avg))\\n        elif reason "'!= "not U 4f": skipped.append((rf.project, rf.name, rf.bg_method, rf.endpoint_avg, reason))'"\\nprint(\"eligible records\", len(records))\\nprint(\"smart endpoint>1 eligible\", [r for r in records if str(r[2]).lower()==\"smart\" and r[3]>1])\\nprint(\"skipped\", len(skipped))\\nfor s in skipped:\\n    marker = \" SMART_GT1\" if str(s[2]).lower()==\"smart\" and s[3]>1 else \"\"\\n    print(\"\\\\t\".join(map(str,s))+marker)'" in /Users/skyefortier/xps-verify
 succeeded in 248ms:
count 3
4-GTA UCl4-BN.proj.zip	U4f Scan	U4f Scan	U 4f	smart	6	True		326	326
4-GTA UCl4-BN.proj.zip	U4f Scan_0	U4f Scan_0	U 4f	smart	6	False	fit-time grid drifted from current ui state	326	326
4-GTA UCl4-BN.proj.zip	U4f Scan_3	U4f Scan_3	U 4f	smart	2	False	fit-time grid drifted from current ui state	327	327

 succeeded in 250ms:
eligible records 29
smart endpoint>1 eligible [('4-GTA UCl4-BN.proj.zip', 'U4f Scan', 'smart', 6)]
skipped 25
4-GTA UCl4-BN.proj.zip	U4f Scan_0	smart	6	fit-time grid drifted from current ui state SMART_GT1
4-GTA UCl4-BN.proj.zip	U4f Scan_1	smart	1	fit-time grid drifted from current ui state
4-GTA UCl4-BN.proj.zip	U4f Scan_2	smart	1	fit-time grid drifted from current ui state
4-GTA UCl4-BN.proj.zip	U4f Scan_3	smart	2	fit-time grid drifted from current ui state SMART_GT1
4-GTA UCl4-BN.proj.zip	U4f Scan_4	smart	1	fit-time grid drifted from current ui state
4-GTA UCl4-BN.proj.zip	U4f Scan_7	smart	1	fit-time grid drifted from current ui state
4-GTA UCl4-BN.proj.zip	U4f Scan_8	smart	1	fit-time grid drifted from current ui state
Cl2p_projfit_test.proj.zip	U4f Scan	smart	1	legacy fitResult (no be/fittedY)
Cl2p_projfit_test.proj.zip	U4f Scan_0	smart	1	legacy fitResult (no be/fittedY)
Cl2p_projfit_test.proj.zip	U4f Scan_1	smart	1	legacy fitResult (no be/fittedY)
Cl2p_projfit_test.proj.zip	U4f Scan_2	smart	1	legacy fitResult (no be/fittedY)
Cl2p_projfit_test.proj.zip	U4f Scan_3	smart	1	legacy fitResult (no be/fittedY)
Cl2p_projfit_test.proj.zip	U4f Scan_4	smart	1	legacy fitResult (no be/fittedY)
Cl2p_projfit_test.proj.zip	U4f Scan_5	smart	1	legacy fitResult (no be/fittedY)
Project9_CasaXPS_newfit.proj.zip	U4f Scan	smart	1	legacy fitResult (no be/fittedY)
Project9_CasaXPS_newfit.proj.zip	U4f Scan_0	smart	1	legacy fitResult (no be/fittedY)
Project9_CasaXPS_newfit.proj.zip	U4f Scan_1	smart	1	legacy fitResult (no be/fittedY)
Project9_CasaXPS_newfit.proj.zip	U4f Scan_2	smart	1	legacy fitResult (no be/fittedY)
Project9_CasaXPS_newfit.proj.zip	U4f Scan_3	smart	1	legacy fitResult (no be/fittedY)
Project9_CasaXPS_newfit.proj.zip	U4f Scan_4	smart	1	legacy fitResult (no be/fittedY)
Project9_CasaXPS_newfit.proj.zip	U4f Scan_5	smart	1	legacy fitResult (no be/fittedY)
UCl4_on_graphite.proj.zip	U4f Scan	smart	1	fit-time grid drifted from current ui state
UCl4_on_graphite.proj.zip	U4f Scan_1	smart	1	fit-time grid drifted from current ui state
UCl4_on_graphite.proj.zip	U4f Scan_2	smart	1	fit-time grid drifted from current ui state
UCl4_on_graphite.proj.zip	U4f Scan_4	smart	1	fit-time grid drifted from current ui state

codex
The corpus scan now independently matches the fixture-scope claim: exactly three smart+endpointAvg>1 spectra, all in `4-GTA UCl4-BN.proj.zip`; only `U4f Scan` is fixture-eligible, while `U4f Scan_0` and `_3` are skipped for fit-time grid drift. I’m checking the new parametrized test’s red/green behavior by simulating the old dispatch convention against direct `n_avg`.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import numpy as np\\ndef avg(y,n_avg):\\n    n=len(y)\\n    if n_avg<=1 or n<4: return y.copy()\\n    cap=min(n_avg,n//4)\\n    if cap<1: return y.copy()\\n    out=y.copy(); out[:cap]=np.mean(y[:cap]); out[-cap:]=np.mean(y[-cap:]); return out\\ndef shirley(x,y,n_iter=200,tol=1e-6,n_avg=1):\\n    if len(x)<2: return np.zeros_like(y)\\n    if n_avg>1: y=avg(np.asarray(y,dtype=float),n_avg)\\n    if x[0]>x[-1]: xs,ys=x[::-1].copy(),y[::-1].copy(); flipped=True\\n    else: xs,ys=x.copy(),y.copy(); flipped=False\\n    b_low=ys[0]; b_high=ys[-1]; B=np.linspace(b_low,b_high,len(ys))\\n    for _ in range(n_iter):\\n        B_prev=B.copy(); signal=np.maximum(ys-B,0.0); cum_right=np.zeros(len(ys))\\n        for i in range(len(ys)-2,-1,-1): cum_right[i]=cum_right[i+1]+0.5*(signal[i]+signal[i+1])*(xs[i+1]-xs[i])\\n        total=cum_right[0]\\n        if total<=0.0: break\\n        B=b_high+(b_low-b_high)*cum_right/total\\n        if np.max(np.abs(B-B_prev))<tol: break\\n    return B[::-1] if flipped else B\\ndef smart(x,y,n_iter=200,tol=1e-6,n_avg=1):\\n    if len(x)<2: return np.zeros_like(y)\\n    sh=shirley(x,y,n_iter,tol,n_avg=n_avg)\\n    return np.minimum(sh,y)\\ndef tougaard(x,y,n_avg=1):\\n    n=len(x)\\n    if n<2: return np.zeros_like(y,dtype=float)\\n    B_coef,C_coef=2866.0,1643.0; xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float)\\n    if n_avg>1: ya=avg(ya,n_avg)\\n    flipped=bool(xa[0]<xa[-1])\\n    if flipped: xa,ya=xa[::-1].copy(),ya[::-1].copy()\\n    c0=float(ya[-1]); net=ya-c0; dx=float(abs(xa[1]-xa[0])); diffs=np.diff(xa); uniform=bool(dx>0.0 and np.max(np.abs(diffs-diffs[0])) <= 1e-6*dx)\\n    if uniform:\\n        m=np.arange(n,dtype=float); T=m*dx; k=(B_coef*T)/(C_coef+T*T)**2; bg=np.convolve(net,k[::-1])[n-1:]*dx\\n    else:\\n        w=np.abs(np.gradient(xa)); bg=np.zeros(n)\\n        for i in range(n):\\n            T=np.abs(xa[i:]-xa[i]); kernel=(B_coef*T)/(C_coef+T*T)**2; bg[i]=float(np.sum(kernel*net[i:]*w[i:]))\\n    if bg[0]==0.0: out=np.full(n,c0)\\n    else: out=c0+bg*((float(ya[0])-c0)/bg[0])\\n    return out[::-1] if flipped else out\\nrng=np.random.default_rng(0); x=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.0; y[-1]-=500.0\\nfor method,fn in [(\"shirley\",shirley),(\"smart\",smart),(\"tougaard\",tougaard)]:\\n    for n in (1,4,8):\\n        old=fn(x, avg(y,n))\\n        direct=fn(x, y, n_avg=n)\\n        print(method,n,\"array_equal\",np.array_equal(old,direct),\"allclose1e-9\",np.allclose(old,direct,rtol=1e-9),\"maxabs\",float(np.max(np.abs(old-direct))))'" in /Users/skyefortier/xps-verify
 succeeded in 431ms:
shirley 1 array_equal True allclose1e-9 True maxabs 0.0
shirley 4 array_equal True allclose1e-9 True maxabs 0.0
shirley 8 array_equal True allclose1e-9 True maxabs 0.0
smart 1 array_equal True allclose1e-9 True maxabs 0.0
smart 4 array_equal False allclose1e-9 False maxabs 375.00567255237456
smart 8 array_equal False allclose1e-9 False maxabs 437.51940027444243
tougaard 1 array_equal True allclose1e-9 True maxabs 0.0
tougaard 4 array_equal True allclose1e-9 True maxabs 0.0
tougaard 8 array_equal True allclose1e-9 True maxabs 0.0

codex
The simulated pre-fix dispatch does exactly what the added test is meant to catch: it matches direct `n_avg` for Shirley and Tougaard, but SMART diverges by about 375 counts at `n_avg=4` and about 437.5 counts at `n_avg=8`. That is a discriminating regression test for the reviewed bug.
exec
/bin/zsh -lc "nl -ba tests/autofit/fixtures/u4f_battery_expected.json | sed -n '360,470p;1088,1230p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   360	    {
   361	     "amplitude": 2965.0618164774064,
   362	     "area": -6742.949484699173,
   363	     "center": 385.800118602644,
   364	     "fwhm": 1.9742314795376352,
   365	     "id": "5"
   366	    }
   367	   ],
   368	   "project": "1-GTA UCl4-graphite one set of U doublets.proj.zip",
   369	   "r_factor": 0.050269795554081884,
   370	   "reduced_chi_square": 2.964092180557157,
   371	   "success": true
   372	  },
   373	  {
   374	   "name": "U4f Scan",
   375	   "peaks": [
   376	    {
   377	     "amplitude": 7634.934773080449,
   378	     "area": -21862.45840089331,
   379	     "center": 380.6046583645018,
   380	     "fwhm": 2.4773151720223288,
   381	     "id": "2"
   382	    },
   383	    {
   384	     "amplitude": 5726.2010798103365,
   385	     "area": -15995.158743198761,
   386	     "center": 391.5046583645018,
   387	     "fwhm": 2.4773151720223288,
   388	     "id": "3"
   389	    },
   390	    {
   391	     "amplitude": 1583.0468828413811,
   392	     "area": -6713.665921082466,
   393	     "center": 386.87524055507754,
   394	     "fwhm": 3.3,
   395	     "id": "10"
   396	    },
   397	    {
   398	     "amplitude": 1187.2851621310358,
   399	     "area": -4902.250280800907,
   400	     "center": 397.7752405550775,
   401	     "fwhm": 3.3,
   402	     "id": "11"
   403	    },
   404	    {
   405	     "amplitude": 105851.69607784999,
   406	     "area": -137429.07665383045,
   407	     "center": 398.30386494123576,
   408	     "fwhm": 1.050116484190386,
   409	     "id": "12"
   410	    }
   411	   ],
   412	   "project": "4-GTA UCl4-BN.proj.zip",
   413	   "r_factor": 0.03855137223759979,
   414	   "reduced_chi_square": 11.281303682238963,
   415	   "success": true
   416	  },
   417	  {
   418	   "name": "U4f Scan_5",
   419	   "peaks": [
   420	    {
   421	     "amplitude": 7438.971665170913,
   422	     "area": -20362.994930060784,
   423	     "center": 380.78814601410994,
   424	     "fwhm": 2.297275636551439,
   425	     "id": "2"
   426	    },
   427	    {
   428	     "amplitude": 5579.228748878185,
   429	     "area": -14918.427925169704,
   430	     "center": 391.6881460141099,
   431	     "fwhm": 2.297275636551439,
   432	     "id": "3"
   433	    },
   434	    {
   435	     "amplitude": 1337.4697988345308,
   436	     "area": -5659.4479452296055,
   437	     "center": 387.01508576567437,
   438	     "fwhm": 3.5752402300533492,
   439	     "id": "10"
   440	    },
   441	    {
   442	     "amplitude": 1003.1023491258982,
   443	     "area": -4171.358546542147,
   444	     "center": 397.91508576567435,
   445	     "fwhm": 3.5752402300533492,
   446	     "id": "11"
   447	    },
   448	    {
   449	     "amplitude": 97015.14582080937,
   450	     "area": -125080.23806726135,
   451	     "center": 398.3132993988489,
   452	     "fwhm": 1.0462777067870674,
   453	     "id": "12"
   454	    }
   455	   ],
   456	   "project": "4-GTA UCl4-BN.proj.zip",
   457	   "r_factor": 0.047483321871641115,
   458	   "reduced_chi_square": 17.89649421792836,
   459	   "success": true
   460	  },
   461	  {
   462	   "name": "U4f Scan_6",
   463	   "peaks": [
   464	    {
   465	     "amplitude": 7414.394781460895,
   466	     "area": -20435.317309988648,
   467	     "center": 380.8044299515421,
   468	     "fwhm": 2.3820615345273253,
   469	     "id": "2"
   470	    },
  1088	     "fwhm": 1.9742382628323831,
  1089	     "id": "5"
  1090	    }
  1091	   ],
  1092	   "project": "UCl4_on_graphite.proj.zip",
  1093	   "r_factor": 0.05026934336104625,
  1094	   "reduced_chi_square": 2.964092193326995,
  1095	   "success": true
  1096	  }
  1097	 ],
  1098	 "skipped": [
  1099	  {
  1100	   "name": "U4f Scan_0",
  1101	   "project": "4-GTA UCl4-BN.proj.zip",
  1102	   "reason": "fit-time grid drifted from current ui state"
  1103	  },
  1104	  {
  1105	   "name": "U4f Scan_1",
  1106	   "project": "4-GTA UCl4-BN.proj.zip",
  1107	   "reason": "fit-time grid drifted from current ui state"
  1108	  },
  1109	  {
  1110	   "name": "U4f Scan_2",
  1111	   "project": "4-GTA UCl4-BN.proj.zip",
  1112	   "reason": "fit-time grid drifted from current ui state"
  1113	  },
  1114	  {
  1115	   "name": "U4f Scan_3",
  1116	   "project": "4-GTA UCl4-BN.proj.zip",
  1117	   "reason": "fit-time grid drifted from current ui state"
  1118	  },
  1119	  {
  1120	   "name": "U4f Scan_4",
  1121	   "project": "4-GTA UCl4-BN.proj.zip",
  1122	   "reason": "fit-time grid drifted from current ui state"
  1123	  },
  1124	  {
  1125	   "name": "U4f Scan_7",
  1126	   "project": "4-GTA UCl4-BN.proj.zip",
  1127	   "reason": "fit-time grid drifted from current ui state"
  1128	  },
  1129	  {
  1130	   "name": "U4f Scan_8",
  1131	   "project": "4-GTA UCl4-BN.proj.zip",
  1132	   "reason": "fit-time grid drifted from current ui state"
  1133	  },
  1134	  {
  1135	   "name": "U4f Scan",
  1136	   "project": "Cl2p_projfit_test.proj.zip",
  1137	   "reason": "legacy fitResult (no be/fittedY)"
  1138	  },
  1139	  {
  1140	   "name": "U4f Scan_0",
  1141	   "project": "Cl2p_projfit_test.proj.zip",
  1142	   "reason": "legacy fitResult (no be/fittedY)"
  1143	  },
  1144	  {
  1145	   "name": "U4f Scan_1",
  1146	   "project": "Cl2p_projfit_test.proj.zip",
  1147	   "reason": "legacy fitResult (no be/fittedY)"
  1148	  },
  1149	  {
  1150	   "name": "U4f Scan_2",
  1151	   "project": "Cl2p_projfit_test.proj.zip",
  1152	   "reason": "legacy fitResult (no be/fittedY)"
  1153	  },
  1154	  {
  1155	   "name": "U4f Scan_3",
  1156	   "project": "Cl2p_projfit_test.proj.zip",
  1157	   "reason": "legacy fitResult (no be/fittedY)"
  1158	  },
  1159	  {
  1160	   "name": "U4f Scan_4",
  1161	   "project": "Cl2p_projfit_test.proj.zip",
  1162	   "reason": "legacy fitResult (no be/fittedY)"
  1163	  },
  1164	  {
  1165	   "name": "U4f Scan_5",
  1166	   "project": "Cl2p_projfit_test.proj.zip",
  1167	   "reason": "legacy fitResult (no be/fittedY)"
  1168	  },
  1169	  {
  1170	   "name": "U4f Scan",
  1171	   "project": "Project9_CasaXPS_newfit.proj.zip",
  1172	   "reason": "legacy fitResult (no be/fittedY)"
  1173	  },
  1174	  {
  1175	   "name": "U4f Scan_0",
  1176	   "project": "Project9_CasaXPS_newfit.proj.zip",
  1177	   "reason": "legacy fitResult (no be/fittedY)"
  1178	  },
  1179	  {
  1180	   "name": "U4f Scan_1",
  1181	   "project": "Project9_CasaXPS_newfit.proj.zip",
  1182	   "reason": "legacy fitResult (no be/fittedY)"
  1183	  },
  1184	  {
  1185	   "name": "U4f Scan_2",
  1186	   "project": "Project9_CasaXPS_newfit.proj.zip",
  1187	   "reason": "legacy fitResult (no be/fittedY)"
  1188	  },
  1189	  {
  1190	   "name": "U4f Scan_3",
  1191	   "project": "Project9_CasaXPS_newfit.proj.zip",
  1192	   "reason": "legacy fitResult (no be/fittedY)"
  1193	  },
  1194	  {
  1195	   "name": "U4f Scan_4",
  1196	   "project": "Project9_CasaXPS_newfit.proj.zip",
  1197	   "reason": "legacy fitResult (no be/fittedY)"
  1198	  },
  1199	  {
  1200	   "name": "U4f Scan_5",
  1201	   "project": "Project9_CasaXPS_newfit.proj.zip",
  1202	   "reason": "legacy fitResult (no be/fittedY)"
  1203	  },
  1204	  {
  1205	   "name": "U4f Scan",
  1206	   "project": "UCl4_on_graphite.proj.zip",
  1207	   "reason": "fit-time grid drifted from current ui state"
  1208	  },
  1209	  {
  1210	   "name": "U4f Scan_1",
  1211	   "project": "UCl4_on_graphite.proj.zip",
  1212	   "reason": "fit-time grid drifted from current ui state"
  1213	  },
  1214	  {
  1215	   "name": "U4f Scan_2",
  1216	   "project": "UCl4_on_graphite.proj.zip",
  1217	   "reason": "fit-time grid drifted from current ui state"
  1218	  },
  1219	  {
  1220	   "name": "U4f Scan_4",
  1221	   "project": "UCl4_on_graphite.proj.zip",
  1222	   "reason": "fit-time grid drifted from current ui state"
  1223	  }
  1224	 ]
  1225	}
exec
/bin/zsh -lc 'git show --name-status --format= 3cd6aad' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-b8Iw5HXB' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vlmiXwXE' (errno=Operation not permitted)
M	autofit/parity.py
M	fitting.py
M	tests/autofit/fixtures/u4f_battery_expected.json
M	tests/test_background_n_avg.py

exec
/bin/zsh -lc 'git show --stat --format= 3cd6aad -- templates/index.html app.py autofit/engine.py autofit/methods fitting.py autofit/parity.py tests/test_background_n_avg.py tests/autofit/fixtures/u4f_battery_expected.json' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IJdxPFID' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-75TGpjhu' (errno=Operation not permitted)
 autofit/parity.py                                |  7 +-
 fitting.py                                       | 12 ++--
 tests/autofit/fixtures/u4f_battery_expected.json | 84 ++++++++++++------------
 tests/test_background_n_avg.py                   | 30 +++++++++
 4 files changed, 81 insertions(+), 52 deletions(-)

exec
/bin/zsh -lc 'git status --short' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OfuF9CML' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-x7MFsO9I' (errno=Operation not permitted)
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json

codex
One nuance surfaced during the line trace: the invariance is mathematically true for the float arrays this app uses. As a pure helper property, `shirley_background(x, y, n_avg=N)` casts to float before applying averaging, while an external caller that pre-averaged an integer array would have truncated means in `_apply_endpoint_averaging`; that is outside the reviewed XPS path if counts are float, but it is worth accounting for in the review wording.
codex
I’m checking the input normalization around `run_fit` and `compute_background_only` to decide whether that dtype caveat is a real regression risk or just a theoretical helper edge case.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '930,1018p;1258,1278p;1300,1312p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   930	        _set("gamma_asym", spec.get("gamma_asym", 0.0), min_=0.0, max_=5.0,
   931	             vary=not spec.get("fix_gamma_asym", False))
   932	    if shape == "ds_g":
   933	        _set("alpha",   spec.get("alpha",   0.10), min_=0.0,  max_=0.49,
   934	             vary=not spec.get("fix_alpha", False))
   935	        _set("beta",    spec.get("beta",    0.3),  min_=0.05, max_=2.0,
   936	             vary=not spec.get("fix_beta", False))
   937	        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0,
   938	             vary=not spec.get("fix_m_gauss", False))
   939	    if shape == "la_casaxps":
   940	        _set("alpha", spec.get("alpha", 1.0), min_=0.1, max_=5.0,
   941	             vary=not spec.get("fix_alpha", False))
   942	        _set("beta",  spec.get("beta",  1.0), min_=0.1, max_=5.0,
   943	             vary=not spec.get("fix_beta", False))
   944	        _set("m",     spec.get("m",    50.0), min_=0.0, max_=499.0,
   945	             vary=not spec.get("fix_m", True))
   946	
   947	    return p
   948	
   949	
   950	# ─────────────────────────────────────────────────────────────────────────────
   951	# Main fitting API
   952	# ─────────────────────────────────────────────────────────────────────────────
   953	
   954	def run_fit(
   955	    energy: np.ndarray,
   956	    counts: np.ndarray,
   957	    peak_specs: list[dict[str, Any]],
   958	    background_method: str = "shirley",
   959	    bg_start_idx: int | None = None,
   960	    bg_end_idx: int | None = None,
   961	    charge_shift_ev: float = 0.0,
   962	    fit_kws: dict | None = None,
   963	    n_perturb: int = 0,
   964	    manual_bg: list | None = None,
   965	    endpoint_avg: int = 1,
   966	) -> dict[str, Any]:
   967	    """
   968	    Run XPS peak fitting and return a serialisable result dict.
   969	
   970	    Parameters
   971	    ----------
   972	    energy            : 1‑D array of binding energies (eV)
   973	    counts            : 1‑D array of intensities (counts / CPS)
   974	    peak_specs        : list of peak specification dicts (see _make_peak_params)
   975	    background_method : 'shirley' | 'linear' | 'none'
   976	    bg_start_idx      : slice start for background region (None → 0)
   977	    bg_end_idx        : slice end for background region   (None → len)
   978	    charge_shift_ev   : shift to apply to energy axis before fitting
   979	    fit_kws           : extra kwargs forwarded to lmfit minimize
   980	
   981	    Returns
   982	    -------
   983	    dict with keys: energy, fitted_y, background_y, residuals,
   984	                    individual_peaks, statistics, charge_shift_applied, success
   985	    """
   986	    if len(energy) != len(counts):
   987	        raise ValueError("energy and counts must have the same length")
   988	    if not peak_specs:
   989	        raise ValueError("At least one peak specification is required")
   990	    # Reject self/cyclic spin-orbit constraints before building lmfit exprs (F11)
   991	    _validate_constraint_graph(peak_specs)
   992	
   993	    # Apply charge correction
   994	    energy = energy + charge_shift_ev
   995	
   996	    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
   997	    # narrow only the anchor window used to construct the background
   998	    # curve. Reusing the slice for both was the bug where putting bg
   999	    # anchors inside the ROI silently chopped the fit window — and the
  1000	    # reported χ², residuals, and σ — down to that same sub-slice.
  1001	    i0 = bg_start_idx if bg_start_idx is not None else 0
  1002	    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
  1003	    i0 = max(0, i0)
  1004	    i1 = min(len(energy), i1)
  1005	    # Normalize the user-supplied anchor pair: reversed order is a valid
  1006	    # choice — the frontend sends bg-start = higher BE and bg-end = lower
  1007	    # BE, so the index order depends on whether the data array is
  1008	    # BE-ascending or BE-descending. Treat the pair as an unordered
  1009	    # anchor window regardless of direction.
  1010	    if i0 > i1:
  1011	        i0, i1 = i1, i0
  1012	    # Bail to the full ROI only if the normalized window is genuinely
  1013	    # unusable (< 2 points): the integral / interp / linear-fit
  1014	    # functions below all need at least two distinct anchor points.
  1015	    if i1 - i0 < 2:
  1016	        i0, i1 = 0, len(energy)
  1017	
  1018	    x = energy
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
/bin/zsh -lc "rg -n \"compute_background_only\\(|run_fit\\(\" app.py autofit tests -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:723:            result = fitting.compute_background_only(
app.py:828:            result = fitting.run_fit(
autofit/parity.py:69:def background_like_run_fit(
autofit/parity.py:180:    bg = background_like_run_fit(
autofit/parity.py:193:    res = run_fit(
tests/test_mixed_ds_lacx_e2e.py:50:result = run_fit(
autofit/methods/least_squares.py:50:        res = run_fit(
tests/test_background_n_avg.py:169:        result = compute_background_only(x, y, method=method, endpoint_avg=n_avg)

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import numpy as np\\ndef avg(y,n_avg):\\n    n=len(y)\\n    if n_avg<=1 or n<4: return y.copy()\\n    cap=min(n_avg,n//4)\\n    if cap<1: return y.copy()\\n    out=y.copy(); out[:cap]=np.mean(y[:cap]); out[-cap:]=np.mean(y[-cap:]); return out\\nprint(avg(np.array([1,2,4,8,16,32,64,128]),2), avg(np.asarray(np.array([1,2,4,8,16,32,64,128]),dtype=float),2))'" in /Users/skyefortier/xps-verify
 succeeded in 109ms:
[ 1  1  4  8 16 32 96 96] [ 1.5  1.5  4.   8.  16.  32.  96.  96. ]

exec
/bin/zsh -lc "nl -ba autofit/methods/least_squares.py | sed -n '1,75p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	Method 1 — classical constrained least-squares (the manual-model baseline).
     3	
     4	Thin wrapper over the EXISTING ``fitting.run_fit`` (unchanged, same code the
     5	manual UI uses) so the method seam has an honest baseline entry.  Consumes
     6	explicit ``peak_specs``; no grammar required.
     7	"""
     8	
     9	from __future__ import annotations
    10	
    11	from typing import Any, Callable, Optional
    12	
    13	import numpy as np
    14	
    15	from fitting import run_fit
    16	
    17	from ..grammar import CandidateGrammar
    18	from .base import MethodResult, PeakFitMethod
    19	
    20	_ALLOWED_OPTIONS = {
    21	    "background_method", "bg_start_idx", "bg_end_idx", "endpoint_avg",
    22	    "fit_method", "n_perturb", "manual_bg",
    23	}
    24	
    25	
    26	class LeastSquaresMethod(PeakFitMethod):
    27	    id = "least_squares"
    28	    label = "Least-squares (manual model)"
    29	    requires_grammar = False
    30	
    31	    def run(
    32	        self,
    33	        x: np.ndarray,
    34	        y: np.ndarray,
    35	        weights: Optional[np.ndarray] = None,
    36	        grammar: Optional[CandidateGrammar] = None,
    37	        peak_specs: Optional[list[dict]] = None,
    38	        options: Optional[dict[str, Any]] = None,
    39	        progress_cb: Optional[Callable[[dict], None]] = None,
    40	    ) -> MethodResult:
    41	        if not peak_specs:
    42	            raise ValueError("least_squares requires explicit peak_specs (manual model)")
    43	        opts = dict(options or {})
    44	        unknown = set(opts) - _ALLOWED_OPTIONS
    45	        if unknown:
    46	            raise ValueError(f"unknown least_squares options: {sorted(unknown)}")
    47	        fit_method = opts.pop("fit_method", None)
    48	        fit_kws = {"method": fit_method} if fit_method else None
    49	
    50	        res = run_fit(
    51	            np.asarray(x, dtype=float),
    52	            np.asarray(y, dtype=float),
    53	            peak_specs,
    54	            background_method=opts.pop("background_method", "shirley"),
    55	            bg_start_idx=opts.pop("bg_start_idx", None),
    56	            bg_end_idx=opts.pop("bg_end_idx", None),
    57	            endpoint_avg=opts.pop("endpoint_avg", 1),
    58	            n_perturb=opts.pop("n_perturb", 0),
    59	            manual_bg=opts.pop("manual_bg", None),
    60	            fit_kws=fit_kws,
    61	        )
    62	
    63	        peaks = []
    64	        confidence: dict[str, dict] = {}
    65	        for ip in res["individual_peaks"]:
    66	            par = ip["params"]
    67	            rec = {"id": ip["id"]}
    68	            for name, info in par.items():
    69	                rec[name] = info["value"]
    70	            peaks.append(rec)
    71	            stderr = {name: info.get("stderr") for name, info in par.items()}
    72	            has_cov = any(v is not None for v in stderr.values())
    73	            confidence[str(ip["id"])] = {
    74	                "sigma_stat": {
    75	                    "uncertainty_kind": "covariance" if has_cov else "unavailable",

exec
/bin/zsh -lc "nl -ba app.py | sed -n '690,850p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
/bin/zsh -lc "rg -n \"def _load_session|rawIntensity|loadtxt|astype\\(float|np.asarray\\(.*dtype=float\" app.py parser.py vgd_parser.py xps_reference.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:112:def _load_session(session_id: str, upload_folder: str) -> tuple[np.ndarray, np.ndarray]:
parser.py:67:        return np.asarray(be, dtype=float), np.asarray(inten, dtype=float)
parser.py:403:        all_floats = np.frombuffer(data, dtype="<f4", count=n_floats).astype(float)
parser.py:480:        arr = np.frombuffer(data, dtype=f"{endian}f4", count=n, offset=offset).astype(float)
parser.py:486:            arr = np.frombuffer(data, dtype=">f4", count=n, offset=offset).astype(float)

codex
The public app and autofit least-squares path pass float arrays into `run_fit`/`compute_background_only` (`parser.py` produces floats, and the method wrapper casts to float). The integer-array caveat is therefore not a failure scenario for the scoped app behavior.
exec
/bin/zsh -lc "nl -ba app.py | sed -n '100,125p'; nl -ba parser.py | sed -n '55,72p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
    55	
    56	    if suffix in (".csv", ".txt", ".xy"):
    57	        return parse_csv(path)
    58	    elif suffix in (".xlsx", ".xls"):
    59	        return parse_xlsx(path)
    60	    elif suffix == ".vgd":
    61	        # Audit F6: route through the strict olefile-based parser — the same
    62	        # one /api/parse-vgd uses. The heuristic parse_vgd in this module has
    63	        # a brute-force fallback that fabricates a plausible-looking spectrum
    64	        # from arbitrary bytes; a junk .vgd must fail cleanly, not return
    65	        # fabricated counts. vgd_parser raises ValueError on non-OLE input.
    66	        be, inten = vgd_parser.parse_vgd(str(path))
    67	        return np.asarray(be, dtype=float), np.asarray(inten, dtype=float)
    68	    else:
    69	        # Try CSV as a fallback
    70	        try:
    71	            return parse_csv(path)
    72	        except Exception:

exec
/bin/zsh -lc 'rg -n "def parse_csv|np.savez|counts" app.py parser.py | head -80' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
parser.py:6:  CSV   – two‑column (energy, counts); auto‑detects delimiter and header rows
parser.py:12:  parse_file(filepath)  →  (energy: np.ndarray, counts: np.ndarray)
parser.py:47:    counts : np.ndarray  – intensity (counts or CPS), shape (N,)
parser.py:65:        # fabricated counts. vgd_parser raises ValueError on non-OLE input.
parser.py:83:def parse_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
parser.py:85:    Parse a delimited text file with two numeric columns (energy, counts).
parser.py:154:                "Expected (energy, counts)."
parser.py:158:    counts = df[numeric_cols[1]].to_numpy(dtype=float)
parser.py:160:    mask = np.isfinite(energy) & np.isfinite(counts)
parser.py:164:    return energy[mask], counts[mask]
parser.py:170:    counts = {d: sample.count(d) for d in candidates}
parser.py:171:    return max(counts, key=counts.get)
parser.py:210:            counts = df[numeric_cols[1]].to_numpy(dtype=float)
parser.py:211:            mask = np.isfinite(energy) & np.isfinite(counts)
parser.py:213:                return energy[mask], counts[mask]
parser.py:217:        "Expected (energy, counts)."
parser.py:427:    counts = all_floats[best_start: best_start + best_len]
parser.py:434:    return energy, counts
parser.py:498:def ensure_ascending(energy: np.ndarray, counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
parser.py:501:        return energy[::-1].copy(), counts[::-1].copy()
parser.py:502:    return energy.copy(), counts.copy()
app.py:113:    """Load energy and counts arrays from a session file."""
app.py:118:    return archive["energy"], archive["counts"]
app.py:149:    counts: np.ndarray,
app.py:153:    np.savez_compressed(path, energy=energy, counts=counts,
app.py:229:        energy, counts = _load_session(session_id, upload_folder)
app.py:269:    x, y = corrected[mask], counts[mask]
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

exec
/bin/zsh -lc "nl -ba app.py | sed -n '140,160p;570,600p'; nl -ba parser.py | sed -n '83,165p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
    83	def parse_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    84	    """
    85	    Parse a delimited text file with two numeric columns (energy, counts).
    86	
    87	    • Supports comma, tab, semicolon, and space delimiters.
    88	    • Skips comment lines beginning with '#' or '%'.
    89	    • Auto‑skips any header rows that are not entirely numeric.
    90	    • Accepts both KE and BE axes (caller must know which was exported).
    91	    """
    92	    raw = path.read_bytes()
    93	
    94	    # Decode; try UTF‑8 then latin‑1
    95	    try:
    96	        text = raw.decode("utf-8")
    97	    except UnicodeDecodeError:
    98	        text = raw.decode("latin-1")
    99	
   100	    # Filter comment lines
   101	    lines = [
   102	        line for line in text.splitlines()
   103	        if line.strip() and not line.lstrip().startswith(("#", "%"))
   104	    ]
   105	    if not lines:
   106	        raise ValueError("File appears to be empty or contains only comments")
   107	
   108	    # Detect delimiter from the first non‑empty data‑looking line
   109	    delimiter = _detect_delimiter("\n".join(lines[:20]))
   110	
   111	    try:
   112	        df = pd.read_csv(
   113	            io.StringIO("\n".join(lines)),
   114	            sep=delimiter,
   115	            header=None,
   116	            comment="#",
   117	            engine="python",
   118	        )
   119	    except Exception as exc:
   120	        # Clean, non-leaking message (audit F10): a corrupt/unreadable file is a
   121	        # user-fixable problem, so surface a helpful 400 rather than a generic
   122	        # 500 — but never echo the raw pandas text. The original is preserved on
   123	        # the exception chain (`from exc`) for a server-side traceback if needed.
   124	        raise ValueError(
   125	            "Could not parse the file as delimited text. Expected two numeric "
   126	            "columns (binding energy, intensity)."
   127	        ) from exc
   128	
   129	    # Drop any entirely‑NaN columns (e.g. trailing delimiter)
   130	    df.dropna(axis=1, how="all", inplace=True)
   131	
   132	    # Extract the first two numeric columns
   133	    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
   134	    if len(numeric_cols) < 2:
   135	        # Possibly header row(s) still present – try skiprows
   136	        for skip in range(1, min(20, len(df))):
   137	            df2 = pd.read_csv(
   138	                io.StringIO("\n".join(lines)),
   139	                sep=delimiter,
   140	                header=None,
   141	                skiprows=skip,
   142	                comment="#",
   143	                engine="python",
   144	            )
   145	            df2.dropna(axis=1, how="all", inplace=True)
   146	            nc = [c for c in df2.columns if pd.api.types.is_numeric_dtype(df2[c])]
   147	            if len(nc) >= 2:
   148	                df = df2
   149	                numeric_cols = nc
   150	                break
   151	        else:
   152	            raise ValueError(
   153	                "Could not find two numeric columns in the file. "
   154	                "Expected (energy, counts)."
   155	            )
   156	
   157	    energy = df[numeric_cols[0]].to_numpy(dtype=float)
   158	    counts = df[numeric_cols[1]].to_numpy(dtype=float)
   159	
   160	    mask = np.isfinite(energy) & np.isfinite(counts)
   161	    if mask.sum() < 2:
   162	        raise ValueError("Fewer than 2 valid (finite) data points found")
   163	
   164	    return energy[mask], counts[mask]
   165	

codex
**Findings**
1. MINOR: The Shirley/Tougaard invariance claim is true for the float XPS paths, but slightly overbroad as a helper-level statement. [fitting.py](/Users/skyefortier/xps-verify/fitting.py:351) casts to float before internal endpoint averaging, while external `_apply_endpoint_averaging` preserves input dtype and can truncate means for integer arrays at [fitting.py](/Users/skyefortier/xps-verify/fitting.py:314). Concrete scenario: `np.array([1,2,4,8,16,32,64,128])` with `n_avg=2` externally averages to integer endpoints `[1,1,...,96,96]`, while direct internal averaging uses `[1.5,1.5,...,96,96]`. This does not affect the app/manual/autofit paths I checked, which feed float arrays.

**Verification**
- `shirley_background`: after optional averaging, all subsequent work uses `ys` derived from the working `y`; no second raw reference remains. See [fitting.py](/Users/skyefortier/xps-verify/fitting.py:351).
- `tougaard_background`: same pattern with working `ya`; after optional averaging, all later math uses `ya`. See [fitting.py](/Users/skyefortier/xps-verify/fitting.py:583).
- `smart_background`: not invariant, because it computes averaged Shirley but clamps with the original argument via `np.minimum(shir, y)`. See [fitting.py](/Users/skyefortier/xps-verify/fitting.py:400).
- Corpus scan: exactly 3 spectra under `docs/autofit/test_data/*.proj.zip` are `smart` with `endpointAvg > 1`: `U4f Scan` endpoint 6 eligible, `U4f Scan_0` endpoint 6 skipped for grid drift, `U4f Scan_3` endpoint 2 skipped for grid drift. The generator uses `battery_eligible` and records non-`not U 4f` skips at [scripts/gen_u4f_battery_fixture.py](/Users/skyefortier/xps-verify/scripts/gen_u4f_battery_fixture.py:31); the grid-drift skip is at [autofit/parity.py](/Users/skyefortier/xps-verify/autofit/parity.py:149).
- Fixture diff: 29 records before and after, skipped list unchanged. Only `4-GTA UCl4-BN.proj.zip / U4f Scan` has >1e-6 relative differences; reduced chi-square moved to `11.281303682238963` at [u4f_battery_expected.json](/Users/skyefortier/xps-verify/tests/autofit/fixtures/u4f_battery_expected.json:414). `U4f Scan_5` has only tiny refit noise, max relative diff `1.49e-12`.
- Removed import is dead: `rg _apply_endpoint_averaging autofit/parity.py` returned no matches.
- Added parametrized test discriminates correctly. Simulating the pre-3cd6aad dispatch showed Shirley/Tougaard still match direct `n_avg`, while SMART diverges by ~375 counts at `n_avg=4` and ~437.5 counts at `n_avg=8`. The test is at [tests/test_background_n_avg.py](/Users/skyefortier/xps-verify/tests/test_background_n_avg.py:149).
- Scope is contained: `git show --name-status 3cd6aad` lists only `autofit/parity.py`, `fitting.py`, `tests/test_background_n_avg.py`, and `tests/autofit/fixtures/u4f_battery_expected.json`. No diff in `templates/index.html`, `app.py`, `autofit/engine.py`, `autofit/methods/*.py`, or peak lineshapes.

I did not run pytest because the available base `python3` lacks `lmfit` and no repo venv is present; I used read-only source/fixture/corpus probes instead.

VERDICT: GO
tokens used
85,893
**Findings**
1. MINOR: The Shirley/Tougaard invariance claim is true for the float XPS paths, but slightly overbroad as a helper-level statement. [fitting.py](/Users/skyefortier/xps-verify/fitting.py:351) casts to float before internal endpoint averaging, while external `_apply_endpoint_averaging` preserves input dtype and can truncate means for integer arrays at [fitting.py](/Users/skyefortier/xps-verify/fitting.py:314). Concrete scenario: `np.array([1,2,4,8,16,32,64,128])` with `n_avg=2` externally averages to integer endpoints `[1,1,...,96,96]`, while direct internal averaging uses `[1.5,1.5,...,96,96]`. This does not affect the app/manual/autofit paths I checked, which feed float arrays.

**Verification**
- `shirley_background`: after optional averaging, all subsequent work uses `ys` derived from the working `y`; no second raw reference remains. See [fitting.py](/Users/skyefortier/xps-verify/fitting.py:351).
- `tougaard_background`: same pattern with working `ya`; after optional averaging, all later math uses `ya`. See [fitting.py](/Users/skyefortier/xps-verify/fitting.py:583).
- `smart_background`: not invariant, because it computes averaged Shirley but clamps with the original argument via `np.minimum(shir, y)`. See [fitting.py](/Users/skyefortier/xps-verify/fitting.py:400).
- Corpus scan: exactly 3 spectra under `docs/autofit/test_data/*.proj.zip` are `smart` with `endpointAvg > 1`: `U4f Scan` endpoint 6 eligible, `U4f Scan_0` endpoint 6 skipped for grid drift, `U4f Scan_3` endpoint 2 skipped for grid drift. The generator uses `battery_eligible` and records non-`not U 4f` skips at [scripts/gen_u4f_battery_fixture.py](/Users/skyefortier/xps-verify/scripts/gen_u4f_battery_fixture.py:31); the grid-drift skip is at [autofit/parity.py](/Users/skyefortier/xps-verify/autofit/parity.py:149).
- Fixture diff: 29 records before and after, skipped list unchanged. Only `4-GTA UCl4-BN.proj.zip / U4f Scan` has >1e-6 relative differences; reduced chi-square moved to `11.281303682238963` at [u4f_battery_expected.json](/Users/skyefortier/xps-verify/tests/autofit/fixtures/u4f_battery_expected.json:414). `U4f Scan_5` has only tiny refit noise, max relative diff `1.49e-12`.
- Removed import is dead: `rg _apply_endpoint_averaging autofit/parity.py` returned no matches.
- Added parametrized test discriminates correctly. Simulating the pre-3cd6aad dispatch showed Shirley/Tougaard still match direct `n_avg`, while SMART diverges by ~375 counts at `n_avg=4` and ~437.5 counts at `n_avg=8`. The test is at [tests/test_background_n_avg.py](/Users/skyefortier/xps-verify/tests/test_background_n_avg.py:149).
- Scope is contained: `git show --name-status 3cd6aad` lists only `autofit/parity.py`, `fitting.py`, `tests/test_background_n_avg.py`, and `tests/autofit/fixtures/u4f_battery_expected.json`. No diff in `templates/index.html`, `app.py`, `autofit/engine.py`, `autofit/methods/*.py`, or peak lineshapes.

I did not run pytest because the available base `python3` lacks `lmfit` and no repo venv is present; I used read-only source/fixture/corpus probes instead.

VERDICT: GO
