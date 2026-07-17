OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f7233-3f68-75a1-9eb7-ed0cdd7d7531
--------
user
You are an adversarial reviewer for a scoped feature commit in this repo
(XPS peak-fitting web app). Review commit c5a24ac ("feat(fitting): unify
n_avg convention across background functions (F3)") on branch
feature-autofit-stage2 — `git show c5a24ac` gives the full diff. This is
Unit 2 of a 2-unit split of a larger patch that arrived from a sandbox
clone with no access to this worktree; Unit 1 (Tougaard F1+F2, commits
3d9ff54 / 173f002) already landed and is review-complete. Read-only sandbox
is fine; if pytest is runnable, run it — otherwise reason from the diff and
static analysis / small extracted-function probes.

RELEVANT HISTORY, so you calibrate scrutiny correctly: Unit 1's first
review round split GO/NO-GO — the NO-GO run caught a "laundered" regression
test whose fixture made the assertion trivially true regardless of whether
the actual fix was present (an F1 anchor collapsed a fixture's signal to
near-zero, so a test comparing weighted-vs-unweighted quadrature passed
even with the real fix reverted). That was independently reproduced and
fixed. Apply the SAME LEVEL of scrutiny here — for every new test in this
commit, ask "would this test actually fail if the feature were absent or
silently broken?", not just "does it pass."

SCOPE OF THE CHANGE (verify it is contained):
- fitting.py: _apply_endpoint_averaging relocated from after
  smart_experimental_background to immediately before shirley_background
  (its first consumer in source order) — verify its BODY is byte-identical
  before and after the move (git diff should show it as a pure relocation,
  not a rewrite). shirley_background gains n_avg: int = 1 (default) and
  n_avg>1 triggers _apply_endpoint_averaging internally. smart_background
  gains n_avg: int = 1 and forwards it to shirley_background.
- autofit/engine.py: _compute_background gains endpoint_avg: int = 1,
  forwarded as n_avg=endpoint_avg to shirley_background / smart_background
  / smart_experimental_background / tougaard_background; linear_background
  is unaffected (no endpoint-averaging concept).
- tests/test_background_n_avg.py: new file, 13 tests.
- No changes to templates/index.html, /api/fit's contract,
  autofit/methods/*.py, or peak lineshapes — confirm zero diff in all of
  these.

THE CORE CLAIM TO VERIFY: this is "pure wiring that changes no current
output." Specifically:
(a) At every REAL call site of _compute_background in autofit/engine.py
    (grep for it — there should be exactly 3), confirm none of them pass
    endpoint_avg today, so the default of 1 is what actually executes.
(b) Confirm shirley_background(x, y) with no n_avg argument, and
    shirley_background(x, y, n_avg=1) explicitly, produce byte-identical
    output to the pre-this-commit implementation (n_avg=1 must be a true
    no-op, not an approximately-equal one — check _apply_endpoint_averaging
    is only invoked when n_avg > 1, never unconditionally).
(c) Same for smart_background and for _compute_background across all 5
    BackgroundType branches (SHIRLEY, SMART, SMART_EXP, LINEAR, TOUGAARD).
(d) app.py's own endpoint_avg default (lines ~718, ~794) is also 1 —
    confirm this claim (grep app.py) rather than trusting the commit
    message.

TESTS TO INTERROGATE — attack each for the laundered-pin failure mode:
- test_shirley_background_n_avg_changes_output_on_noisy_endpoints /
  test_smart_background_n_avg_changes_output_on_noisy_endpoints: these
  assert `not np.allclose(raw, averaged)` on a fixture with a deliberate
  ±500-count single-point endpoint outlier. Is that outlier large enough,
  relative to the Shirley normalization (B_low, B_high, and the
  cum_right/total ratio), to survive to the final output and not get
  washed out? Compute it yourself if you can run Python.
- test_shirley_background_n_avg_matches_external_pre_averaging /
  test_smart_background_forwards_n_avg_to_shirley: do these actually
  distinguish "n_avg correctly implemented" from "n_avg silently ignored"?
  (They would NOT catch a bug where n_avg is accepted as a parameter but
  never used — check whether any test would catch THAT specific failure
  mode, since it's exactly the class of bug this whole effort exists to
  close for autofit/engine.py.)
- test_compute_background_forwards_endpoint_avg (parametrized over
  SHIRLEY/SMART/SMART_EXP/TOUGAARD): same question — does it discriminate
  "endpoint_avg forwarded correctly" from "endpoint_avg accepted but
  dropped on the floor"? Given the n_avg values tested are (1, 4, 8), is
  there a value where forwarding vs. dropping would look identical by
  coincidence on the shared fixture?
- test_compute_background_linear_ignores_endpoint_avg: confirm
  linear_background genuinely has no endpoint concept worth wiring (it
  reads only x[0]/x[-1]/y[0]/y[-1], not a window of points), so "ignores
  it" is correct behavior, not a missed wiring gap.
- test_apply_endpoint_averaging_still_importable_and_unchanged: this test
  passed even BEFORE the relocation (it's not read/green-cycle evidence of
  anything this commit did) — is that fine as a regression pin for the
  future, or should it be flagged as decorative?

Also verify the RED claim in the commit message: temporarily comment out
the `if n_avg > 1: y = _apply_endpoint_averaging(...)` line in
shirley_background (or otherwise defeat the n_avg forwarding chain at each
of the 3 layers: shirley_background itself, smart_background's forward,
_compute_background's forward) and confirm the corresponding tests in
tests/test_background_n_avg.py actually go red for each defeat
independently — not just for all three defeated simultaneously.

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll review this as a code review, starting from the target commit diff and call sites, then I’ll run the focused tests/probes if the read-only sandbox allows it. I’ll also check whether the new tests have real red-cycle value against the specific dropped-wiring failures you called out.
exec
/bin/zsh -lc "rg -n \"_compute_background\\(|endpoint_avg|def (shirley_background|smart_background|linear_background)|def _apply_endpoint_averaging\" fitting.py autofit/engine.py app.py tests/test_background_n_avg.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/test_background_n_avg.py:4:autofit/engine.py's _compute_background must forward an endpoint_avg knob to
tests/test_background_n_avg.py:99:def test_compute_background_default_endpoint_avg_matches_pre_f3_output():
tests/test_background_n_avg.py:100:    """autofit/engine.py's _compute_background(x, y, bg) with no
tests/test_background_n_avg.py:101:    endpoint_avg argument must reproduce pre-F3 output exactly, for every
tests/test_background_n_avg.py:109:        no_arg = _compute_background(x, y, bg_type)
tests/test_background_n_avg.py:110:        default_arg = _compute_background(x, y, bg_type, endpoint_avg=1)
tests/test_background_n_avg.py:120:def test_compute_background_forwards_endpoint_avg(bg_type_name, direct_fn):
tests/test_background_n_avg.py:121:    """_compute_background(x, y, bg, endpoint_avg=N) must match calling the
tests/test_background_n_avg.py:123:    manual Run Fit must agree once both pass the same endpoint_avg."""
tests/test_background_n_avg.py:129:        via_engine = _compute_background(x, y, bg_type, endpoint_avg=n_avg)
tests/test_background_n_avg.py:132:            f"{bg_type_name} mismatch at endpoint_avg={n_avg}"
tests/test_background_n_avg.py:136:def test_compute_background_linear_ignores_endpoint_avg():
tests/test_background_n_avg.py:138:    reads only the two edge points); endpoint_avg must be accepted without
tests/test_background_n_avg.py:143:    no_avg = _compute_background(x, y, BackgroundType.LINEAR)
tests/test_background_n_avg.py:144:    with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
app.py:716:        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
app.py:718:            ep_avg = max(1, int(body.get("endpoint_avg", 1)))
app.py:720:            return _err("endpoint_avg must be an integer")
app.py:726:                endpoint_avg=ep_avg,
app.py:792:        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
app.py:794:            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
app.py:796:            return _err("endpoint_avg must be an integer")
app.py:839:                endpoint_avg=endpoint_avg,
autofit/engine.py:287:def _compute_background(
autofit/engine.py:291:    endpoint_avg: int = 1,
autofit/engine.py:295:    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
autofit/engine.py:299:    to do, leaving Find Peaks unable to express an endpoint_avg the manual
autofit/engine.py:305:        return shirley_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:307:        return smart_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:310:        return smart_experimental_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:315:        return tougaard_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:866:    bg = _compute_background(x, y, model.background)
autofit/engine.py:2182:    bg = _compute_background(x, y, aug_model.background)
autofit/engine.py:2591:        det_bg = _compute_background(x, y, det_bg_family)
fitting.py:306:def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
fitting.py:320:def shirley_background(
fitting.py:384:def smart_background(
fitting.py:404:def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
fitting.py:965:    endpoint_avg: int = 1,
fitting.py:1050:        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1052:        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1054:        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1056:        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1058:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1280:    endpoint_avg: int = 1,
fitting.py:1288:        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
fitting.py:1290:        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
fitting.py:1292:        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
fitting.py:1294:        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
fitting.py:1296:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))

exec
/bin/zsh -lc 'git show --format=fuller --find-renames c5a24ac -- fitting.py autofit/engine.py tests/test_background_n_avg.py app.py templates/index.html autofit/methods' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uC9uZbca' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cxCbHFQK' (errno=Operation not permitted)
commit c5a24acaba52c645861e54daf5412d6e0ace5709
Author:     Skye Fortier <skyefortier@gmail.com>
AuthorDate: Fri Jul 17 16:27:58 2026 -0600
Commit:     Skye Fortier <skyefortier@gmail.com>
CommitDate: Fri Jul 17 16:27:58 2026 -0600

    feat(fitting): unify n_avg convention across background functions (F3)
    
    shirley_background and smart_background now take n_avg directly, matching
    the convention already used by smart_experimental_background /
    shirley_linear_background. The old convention — callers pre-average the
    array via _apply_endpoint_averaging before calling — was easy to forget,
    and autofit/engine.py did forget it: Find Peaks had no way to express an
    endpoint_avg the manual /api/fit path honours. _apply_endpoint_averaging
    is relocated above shirley_background (its first consumer in source
    order); its own behavior is unchanged.
    
    autofit/engine.py's _compute_background gains an endpoint_avg param,
    default 1 — matching both its previous behaviour and app.py's own default
    (app.py:718,794), so this is pure wiring and changes no current output at
    any of its 3 real call sites (none of which pass endpoint_avg today).
    Forwards to shirley/smart/smart_exp/tougaard as n_avg=endpoint_avg;
    linear_background has no endpoint-averaging concept and ignores it.
    
    Originally F3 of a larger sandboxed patch (see Unit 1, commits 3d9ff54 /
    173f002, for F1+F2). Deliberately held as its own unit: F1/F2 live inside
    tougaard_background's own body and were inseparable from each other, but
    F3 is naturally independent code, sequenced after Unit 1 only because
    _compute_background's tougaard_background call needed the 3-arg signature
    to already exist.
    
    The original patch shipped ZERO tests for this behavior change. Added
    tests/test_background_n_avg.py (13 tests) first: confirmed n_avg=1 (the
    default) reproduces pre-F3 output byte-for-byte on both shirley_background
    and _compute_background for every background type; confirmed n_avg>1
    actually changes output on a fixture with a deliberate single-point
    endpoint outlier; confirmed shirley_background(x,y,n_avg=N) equals the old
    external-pre-averaging call exactly (pure convenience wrapper, not a new
    algorithm); confirmed smart_background clamps against raw data, not the
    averaged copy; confirmed _compute_background(...,endpoint_avg=N) matches
    calling the underlying fitting.py function directly. Red confirmed first:
    12/13 failed with TypeError on the missing kwargs before implementation;
    green after.
    
    Full suite: 679 passed, 6 skipped, 0 failed (679 = Unit 1's 666 + these 13
    new tests). Scope: fitting.py, autofit/engine.py, and the one new test
    file — zero changes to /api/fit's contract, autofit/methods/*.py, peak
    lineshapes, or templates/index.html (this is a Python-only Find-Peaks-vs-
    manual-fit wiring gap; no JS-side equivalent exists to fix).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

diff --git a/autofit/engine.py b/autofit/engine.py
index d542f54..fa9695d 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -284,19 +284,35 @@ def _slot_prefix(role: str) -> str:
 # Background
 # ─────────────────────────────────────────────────────────────────────────────
 
-def _compute_background(x: np.ndarray, y: np.ndarray, bg: BackgroundType) -> np.ndarray:
+def _compute_background(
+    x: np.ndarray,
+    y: np.ndarray,
+    bg: BackgroundType,
+    endpoint_avg: int = 1,
+) -> np.ndarray:
+    """Background for the autofit path.
+
+    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
+    (audit F3, 2026-07-17). Every background here now takes ``n_avg``
+    directly rather than requiring the caller to pre-average the array via
+    _apply_endpoint_averaging — which is exactly what this function forgot
+    to do, leaving Find Peaks unable to express an endpoint_avg the manual
+    path honours. Default 1 (raw endpoints) matches both the previous
+    behaviour of this function and app.py's own default, so wiring alone
+    changes nothing.
+    """
     if bg is BackgroundType.SHIRLEY:
-        return shirley_background(x, y)
+        return shirley_background(x, y, n_avg=endpoint_avg)
     if bg is BackgroundType.SMART:
-        return smart_background(x, y)
+        return smart_background(x, y, n_avg=endpoint_avg)
     if bg is BackgroundType.SMART_EXP:
         from fitting import smart_experimental_background
-        return smart_experimental_background(x, y)
+        return smart_experimental_background(x, y, n_avg=endpoint_avg)
     if bg is BackgroundType.LINEAR:
         return linear_background(x, y)
     if bg is BackgroundType.TOUGAARD:
         from fitting import tougaard_background
-        return tougaard_background(x, y)
+        return tougaard_background(x, y, n_avg=endpoint_avg)
     raise ValueError(f"Unknown background type: {bg}")
 
 
diff --git a/fitting.py b/fitting.py
index ae08d1e..93bb345 100644
--- a/fitting.py
+++ b/fitting.py
@@ -303,17 +303,41 @@ def _ds_g_dscore_gauss(
 # Background functions
 # ─────────────────────────────────────────────────────────────────────────────
 
+def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
+    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
+    n = len(y)
+    if n_avg <= 1 or n < 4:
+        return y.copy()
+    cap = min(n_avg, n // 4)
+    if cap < 1:
+        return y.copy()
+    out = y.copy()
+    out[:cap] = np.mean(y[:cap])
+    out[-cap:] = np.mean(y[-cap:])
+    return out
+
+
 def shirley_background(
     x: np.ndarray,
     y: np.ndarray,
     n_iter: int = 200,
     tol: float = 1e-6,
+    n_avg: int = 1,
 ) -> np.ndarray:
     """
     Iterative Shirley background (Proctor & Sherwood, Surf. Sci. 1982).
 
     Works on ascending or descending binding energy arrays.
 
+    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
+    levels B_low/B_high are read (audit F3, 2026-07-17). Shirley scales the
+    ENTIRE background off those two levels, so a single noisy endpoint
+    sample propagates straight into the net area. n_avg=1 = raw endpoints =
+    previous behaviour. Callers previously had to pre-average the input
+    array themselves via _apply_endpoint_averaging; that convention was
+    easy to forget (autofit/engine.py did), so the knob now lives here,
+    matching smart_experimental_background / shirley_linear_background.
+
     At each energy Eᵢ the background equals:
         B(Eᵢ) = B_high + (B_low – B_high) · ∫_{Eᵢ}^{E_max} s(E) dE
                                                ─────────────────────────
@@ -324,6 +348,9 @@ def shirley_background(
     if len(x) < 2:
         return np.zeros_like(y)
 
+    if n_avg > 1:
+        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)
+
     # Work on ascending copy
     if x[0] > x[-1]:
         xs, ys = x[::-1].copy(), y[::-1].copy()
@@ -359,11 +386,18 @@ def smart_background(
     y: np.ndarray,
     n_iter: int = 200,
     tol: float = 1e-6,
+    n_avg: int = 1,
 ) -> np.ndarray:
-    """Smart (constrained Shirley): standard Shirley clamped to never exceed data."""
+    """Smart (constrained Shirley): standard Shirley clamped to never exceed data.
+
+    ``n_avg`` is forwarded to shirley_background (audit F3). The clamp is
+    applied against the RAW data, not the endpoint-averaged copy, so
+    averaging only ever moves the background — never the reported net
+    counts.
+    """
     if len(x) < 2:
         return np.zeros_like(y)
-    shir = shirley_background(x, y, n_iter, tol)
+    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
     return np.minimum(shir, y)
 
 
@@ -429,20 +463,6 @@ def smart_experimental_background(
     return B[::-1] if flipped else B
 
 
-def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
-    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
-    n = len(y)
-    if n_avg <= 1 or n < 4:
-        return y.copy()
-    cap = min(n_avg, n // 4)
-    if cap < 1:
-        return y.copy()
-    out = y.copy()
-    out[:cap] = np.mean(y[:cap])
-    out[-cap:] = np.mean(y[-cap:])
-    return out
-
-
 def shirley_linear_background(
     x: np.ndarray,
     y: np.ndarray,
diff --git a/tests/test_background_n_avg.py b/tests/test_background_n_avg.py
new file mode 100644
index 0000000..9a4cbca
--- /dev/null
+++ b/tests/test_background_n_avg.py
@@ -0,0 +1,145 @@
+"""F3 regression tests (2026-07-17 background audit): shirley_background and
+smart_background must accept n_avg directly, matching the convention already
+used by smart_experimental_background / shirley_linear_background, and
+autofit/engine.py's _compute_background must forward an endpoint_avg knob to
+every background type it dispatches.
+
+The original sandboxed patch that introduced this wiring shipped with no
+tests at all for it -- these are net-new coverage, not a port of anything
+upstream.
+"""
+import numpy as np
+import pytest
+
+from fitting import (
+    _apply_endpoint_averaging,
+    shirley_background,
+    smart_background,
+    smart_experimental_background,
+    tougaard_background,
+)
+
+
+def _noisy_endpoint_fixture():
+    """A spectrum whose single first/last SAMPLE is a noise outlier relative
+    to its neighborhood, so endpoint averaging visibly changes the reported
+    B_low/B_high and therefore the whole background curve."""
+    rng = np.random.default_rng(0)
+    x = np.linspace(700.0, 740.0, 200)
+    y = 4000.0 + 3000.0 * np.exp(-0.5 * ((x - 720.0) / 4.0) ** 2)
+    y = y.copy()
+    y[0] += 500.0    # single-point low-BE outlier
+    y[-1] -= 500.0   # single-point high-BE outlier
+    return x, y
+
+
+def test_shirley_background_default_n_avg_matches_pre_f3_output():
+    """n_avg=1 (the default) must reproduce the pre-F3 raw-endpoint
+    behaviour byte-for-byte -- this wiring must change no current output."""
+    x, y = _noisy_endpoint_fixture()
+    assert np.array_equal(shirley_background(x, y), shirley_background(x, y, n_avg=1))
+
+
+def test_shirley_background_n_avg_changes_output_on_noisy_endpoints():
+    """n_avg > 1 must actually average the endpoints internally and change
+    the result relative to raw endpoints, on a fixture designed so that
+    difference is visible."""
+    x, y = _noisy_endpoint_fixture()
+    raw = shirley_background(x, y, n_avg=1)
+    averaged = shirley_background(x, y, n_avg=8)
+    assert not np.allclose(raw, averaged), (
+        "n_avg=8 produced the same background as n_avg=1 on a fixture with "
+        "a deliberate single-point endpoint outlier"
+    )
+
+
+def test_shirley_background_n_avg_matches_external_pre_averaging():
+    """Calling shirley_background(x, y, n_avg=N) must equal the OLD calling
+    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
+    so this is a pure convenience wrapper, not a new averaging algorithm."""
+    x, y = _noisy_endpoint_fixture()
+    for n_avg in (1, 4, 8):
+        direct = shirley_background(x, y, n_avg=n_avg)
+        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
+        assert np.array_equal(direct, pre_averaged), f"mismatch at n_avg={n_avg}"
+
+
+def test_smart_background_default_n_avg_matches_pre_f3_output():
+    x, y = _noisy_endpoint_fixture()
+    assert np.array_equal(smart_background(x, y), smart_background(x, y, n_avg=1))
+
+
+def test_smart_background_forwards_n_avg_to_shirley():
+    """smart_background(x, y, n_avg=N) must equal
+    minimum(shirley_background(x, y, n_avg=N), y) -- the clamp applies
+    against the RAW data, not an endpoint-averaged copy, so averaging only
+    ever moves the background curve, never the reported net counts."""
+    x, y = _noisy_endpoint_fixture()
+    for n_avg in (1, 4, 8):
+        got = smart_background(x, y, n_avg=n_avg)
+        expected = np.minimum(shirley_background(x, y, n_avg=n_avg), y)
+        assert np.array_equal(got, expected), f"mismatch at n_avg={n_avg}"
+
+
+def test_smart_background_n_avg_changes_output_on_noisy_endpoints():
+    x, y = _noisy_endpoint_fixture()
+    raw = smart_background(x, y, n_avg=1)
+    averaged = smart_background(x, y, n_avg=8)
+    assert not np.allclose(raw, averaged)
+
+
+def test_apply_endpoint_averaging_still_importable_and_unchanged():
+    """F3 relocates _apply_endpoint_averaging above shirley_background in
+    fitting.py's source order; its behaviour must not change."""
+    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
+    out = _apply_endpoint_averaging(y, 2)
+    assert np.array_equal(out, np.array([1.5, 1.5, 3.0, 4.0, 5.0, 6.0, 7.5, 7.5]))
+
+
+def test_compute_background_default_endpoint_avg_matches_pre_f3_output():
+    """autofit/engine.py's _compute_background(x, y, bg) with no
+    endpoint_avg argument must reproduce pre-F3 output exactly, for every
+    background type it dispatches -- pure wiring, no behaviour change."""
+    from autofit.engine import BackgroundType, _compute_background
+
+    x, y = _noisy_endpoint_fixture()
+    for bg_type in (BackgroundType.SHIRLEY, BackgroundType.SMART,
+                    BackgroundType.SMART_EXP, BackgroundType.LINEAR,
+                    BackgroundType.TOUGAARD):
+        no_arg = _compute_background(x, y, bg_type)
+        default_arg = _compute_background(x, y, bg_type, endpoint_avg=1)
+        assert np.array_equal(no_arg, default_arg), f"mismatch for {bg_type}"
+
+
+@pytest.mark.parametrize("bg_type_name,direct_fn", [
+    ("SHIRLEY", shirley_background),
+    ("SMART", smart_background),
+    ("SMART_EXP", smart_experimental_background),
+    ("TOUGAARD", tougaard_background),
+])
+def test_compute_background_forwards_endpoint_avg(bg_type_name, direct_fn):
+    """_compute_background(x, y, bg, endpoint_avg=N) must match calling the
+    underlying fitting.py function directly with n_avg=N -- Find Peaks and
+    manual Run Fit must agree once both pass the same endpoint_avg."""
+    from autofit.engine import BackgroundType, _compute_background
+
+    x, y = _noisy_endpoint_fixture()
+    bg_type = getattr(BackgroundType, bg_type_name)
+    for n_avg in (1, 4, 8):
+        via_engine = _compute_background(x, y, bg_type, endpoint_avg=n_avg)
+        direct = direct_fn(x, y, n_avg=n_avg)
+        assert np.array_equal(via_engine, direct), (
+            f"{bg_type_name} mismatch at endpoint_avg={n_avg}"
+        )
+
+
+def test_compute_background_linear_ignores_endpoint_avg():
+    """linear_background has no endpoint-averaging concept (it already
+    reads only the two edge points); endpoint_avg must be accepted without
+    error and have no effect."""
+    from autofit.engine import BackgroundType, _compute_background
+
+    x, y = _noisy_endpoint_fixture()
+    no_avg = _compute_background(x, y, BackgroundType.LINEAR)
+    with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
+    assert np.array_equal(no_avg, with_avg)

exec
/bin/zsh -lc 'git status --short && git branch --show-current && git show --stat --oneline --decorate --name-only c5a24ac' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-r4yobRZG' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-KEDWeiMT' (errno=Operation not permitted)
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-aIiLMwJZ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gRv5Tqkq' (errno=Operation not permitted)
feature-autofit-stage2
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mTzvFsV7' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BONkr1dF' (errno=Operation not permitted)
c5a24ac feat(fitting): unify n_avg convention across background functions (F3)
autofit/engine.py
fitting.py
tests/test_background_n_avg.py

codex
The initial diff scope matches the stated three files: `fitting.py`, `autofit/engine.py`, and the new test file. I’m drilling into the exact source around the moved helper, the dispatch call sites, and the older `/api/fit` path because there may be an interaction there beyond the commit’s stated Find Peaks wiring.
exec
/bin/zsh -lc "sed -n '300,470p' fitting.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:


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
    Iterative Shirley background (Proctor & Sherwood, Surf. Sci. 1982).

    Works on ascending or descending binding energy arrays.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels B_low/B_high are read (audit F3, 2026-07-17). Shirley scales the
    ENTIRE background off those two levels, so a single noisy endpoint
    sample propagates straight into the net area. n_avg=1 = raw endpoints =
    previous behaviour. Callers previously had to pre-average the input
    array themselves via _apply_endpoint_averaging; that convention was
    easy to forget (autofit/engine.py did), so the knob now lives here,
    matching smart_experimental_background / shirley_linear_background.

    At each energy Eᵢ the background equals:
        B(Eᵢ) = B_high + (B_low – B_high) · ∫_{Eᵢ}^{E_max} s(E) dE
                                               ─────────────────────────
                                               ∫_{E_min}^{E_max} s(E) dE
    where s(E) = max(y(E) – B(E), 0) is the net signal.
    B_low  = y(E_min),  B_high = y(E_max)  (the endpoint levels).
    """
    if len(x) < 2:
        return np.zeros_like(y)

    if n_avg > 1:
        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    b_low = ys[0]    # background at low‑BE end
    b_high = ys[-1]  # background at high‑BE end

    B = np.linspace(b_low, b_high, len(ys))  # linear initial guess

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # O(n) cumulative integral from high-x end back to each point
        cum_right = np.zeros(len(ys))
        for i in range(len(ys) - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = b_high + (b_low - b_high) * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break

    return B[::-1] if flipped else B


def smart_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Smart (constrained Shirley): standard Shirley clamped to never exceed data.

    ``n_avg`` is forwarded to shirley_background (audit F3). The clamp is
    applied against the RAW data, not the endpoint-averaged copy, so
    averaging only ever moves the background — never the reported net
    counts.
    """
    if len(x) < 2:
        return np.zeros_like(y)
    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
    return np.minimum(shir, y)


def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Straight‑line background connecting the first and last data points."""
    slope = (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
    return y[0] + slope * (x - x[0])


def smart_experimental_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Experimental constrained Shirley background, closer to public Avantage
    Smart description.  The data constraint is enforced *during* iteration,
    not as a post-hoc clamp.  Where the background would exceed the data it
    locks to the data, effectively moving the Shirley start inward.  Better
    for narrow spectral windows with sloped baselines."""
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    b_low = float(np.mean(ys[:cap]))      # low-BE endpoint
    b_high = float(np.mean(ys[-cap:]))     # high-BE endpoint
    step = b_low - b_high

    # Linear initial guess
    B = np.linspace(b_low, b_high, n)

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # Cumulative integral from high-BE end (right) back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            dx = xs[i + 1] - xs[i]
            cum_right[i] = cum_right[i + 1] + (signal[i] + signal[i + 1]) / 2 * dx
        total = cum_right[0]
        if total <= 0.0:
            break

        B = b_high + step * (cum_right / total)

        # Constrain during iteration: lock to data where bg exceeds it
        B = np.minimum(B, ys)

        if np.max(np.abs(B - B_prev)) < tol:
            break

    B = np.minimum(B, ys)  # final safety clamp
    return B[::-1] if flipped else B


def shirley_linear_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,

exec
/bin/zsh -lc "sed -n '690,850p' app.py && sed -n '940,1070p' fitting.py && sed -n '1268,1302p' fitting.py" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "sed -n '840,885p' autofit/engine.py && sed -n '2168,2192p' autofit/engine.py && sed -n '2578,2600p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    y: np.ndarray,
    weights: np.ndarray,
    model: CandidateModel,
    initial_params: Optional[Parameters] = None,
    max_nfev: int = FIT_CANDIDATE_MAX_NFEV,
    fit_full_window: bool = False,
) -> FitOutcome:
    """One fit of ``model`` to (x, y, weights); background subtracted first.

    ``max_nfev`` bounds leastsq's own effort per call. lmfit's default
    (200000*(nvars+1), see lmfit.Minimizer) is effectively unbounded: a
    candidate whose params wander to a valid-but-degenerate corner (e.g.
    DS+G's alpha/beta pinned at their bounds — a shape preference, not a
    param error; see _BOUNDARY_EXCLUDED) produces a landscape leastsq can't
    descend, and it spins for tens of thousands of evaluations without
    terminating. Diagnostic run (2026-07-05, Suggest-peaks hang
    investigation) showed a clean bimodal split: converged fits topped out
    at nfev=14890; non-convergent ones started at nfev=21604. This cap sits
    between the two so lmfit's own AbortFitException (caught internally by
    leastsq(), surfacing as result.success=False) cuts off the latter
    deterministically, without clipping legitimate slow-but-converging fits.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)

    bg = _compute_background(x, y, model.background)
    y_sub = y - bg
    composite = _build_composite_model(model)
    params = initial_params if initial_params is not None else \
        _default_params_from_slots(model, x=x, y_net=y_sub,
                                   fit_full_window=fit_full_window)

    try:
        result = composite.fit(y_sub, params, x=x, weights=weights,
                               method="leastsq", nan_policy="omit",
                               max_nfev=max_nfev)
        if (not result.success and result.chisqr is not None
                and np.isfinite(result.chisqr)):
            # ONE warm restart (Stage-2, measured on the real diagnosis
            # scans): a model whose optimum sits against parameter bounds
            # stalls MINPACK on a flat transformed gradient — it reaches
            # the minimum, then burns the whole nfev budget without
            # satisfying ftol (success=False at a genuinely converged
            # χ²).  Restarting AT the exit point resets leastsq's internal
            # diag scaling and it certifies in tens of evaluations
    def _fast(reason: str):
        pr.rejection_reason = reason
        return None, pr, "fast_rejected"

    # An augmented fit_candidate has no internal wall clock and runs
    # ~10-12 s worst-case; starting one with less than PROPOSAL_MIN_FIT_
    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
    # caller passes budget_remaining = min(pass budget, sweep budget) left.
    if budget_remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
        return _fast(
            f"insufficient_budget: {budget_remaining:.1f}s left < "
            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")

    bg = _compute_background(x, y, aug_model.background)
    try:
        init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
                                             fit_full_window=fit_full_window)
    except Exception as exc:
        return _fast(f"init_params_error: {exc}")

    primary = fit_candidate(x, y, weights, aug_model, initial_params=init)
    if not primary.converged:
        return _fast("augmented_fit_did_not_converge")
    comp = next((c for c in primary.components if c.slot_role == spec.role), None)
    pool_error: Optional[str] = None
    detection_overflow: list[dict] = []
    if enable_preseed and (candidates or not grammar.candidates):
        # Detection-only background: today every candidate in a resolved
        # grammar shares one background family (C 1s/B 1s/Cl 2p/U 4f modules
        # are each homogeneous), so the first candidate's is representative.
        # A future mixed-background grammar only affects DETECTION here —
        # each candidate still fits with its own background.  Structural-
        # fallback regions (ZERO grammar candidates — the across-the-
        # periodic-table path) default to Shirley, the standard core-level
        # background (CLAUDE.md convention).
        det_bg_family = (candidates[0].background if candidates
                         else BackgroundType.SHIRLEY)
        det_bg = _compute_background(x, y, det_bg_family)
        preseed_specs = detect_out_of_grammar_dominants(
            x, y, det_bg, candidates, diagnostic_windows,
            noise_floor=noise_floor,
        )
        # Candidate-generation layer (autofit.candidates): overcomplete,
        # provenance-tagged pool.  The reviewed dominant channel above is
        # UNCHANGED; the pool's CWT curvature channel adds seeds the
        # local-max view structurally cannot produce — shoulders with no
        # local maximum, and resolved close pairs the dominant channel's

 succeeded in 0ms:

    @app.post("/api/background")
    @_require_json
    def background():
        """
        Request body
        ------------
        {
          "session_id": "...",
          "method":     "shirley" | "linear" | "none",
          "start_idx":  0,      // optional
          "end_idx":    -1      // optional
        }
        """
        body = request.get_json()
        session_id = body.get("session_id", "")
        _validate_session_id(session_id)

        try:
            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
        except KeyError:
            return _err(f"Session '{session_id}' not found", 404)

        method = body.get("method", "shirley")
        start_idx = _parse_int(body.get("start_idx"), 0, len(energy))
        end_idx = _parse_int(body.get("end_idx"), 0, len(energy), default=len(energy))
        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
        try:
            ep_avg = max(1, int(body.get("endpoint_avg", 1)))
        except (TypeError, ValueError):
            return _err("endpoint_avg must be an integer")

        try:
            result = fitting.compute_background_only(
                energy, counts, method=method,
                start_idx=start_idx, end_idx=end_idx,
                endpoint_avg=ep_avg,
            )
        except ValueError as exc:
            # Our own validation, e.g. "Unknown background method" (audit F10).
            return _err(str(exc))
        except Exception:
            app.logger.exception("Unexpected background error")
            return _err("Internal background error — see server log.", 500)

        return jsonify(result)

    # ── Peak fitting ──────────────────────────────────────────────────────────

    @app.post("/api/fit")
    @_require_json
    def fit():
        """
        Request body
        ------------
        {
          "session_id": "...",

          "background": {
            "method":    "shirley",   // "shirley" | "linear" | "none"
            "start_idx": 0,           // optional – slice into data array
            "end_idx":   -1           // optional
          },

          "peaks": [
            {
              "id":           "p1",               // unique string id
              "shape":        "pseudo_voigt_gl",  // peak lineshape
              "center":       284.8,
              "center_min":   283.0,              // optional bound
              "center_max":   286.0,              // optional bound
              "amplitude":    10000,
              "amplitude_min": 0,                 // optional (default 0)
              "fwhm":         1.5,
              "fwhm_min":     0.2,                // optional
              "fwhm_max":     3.0,                // optional
              "gl_ratio":     0.3,                // Lorentzian fraction [0–1]
              "fwhm_l":       1.5,                // asymmetric_gl only
              "fwhm_r":       1.5,                // asymmetric_gl only
              "alpha":        0.1,                // doniach_sunjic only
              "constrain_to": null,               // id of master peak, or null
              "splitting":    3.67,               // BE offset from master (eV)
              "area_ratio":   0.75,               // amplitude = master × ratio
              "fix_fwhm":     true                // lock FWHM to master
            }
          ]
        }
        """
        body = request.get_json()
        session_id = body.get("session_id", "")
        _validate_session_id(session_id)

        try:
            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
        except KeyError:
            return _err(f"Session '{session_id}' not found", 404)

        # Background config
        bg_cfg = body.get("background", {})
        bg_method = bg_cfg.get("method", "shirley")
        bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
        bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
        try:
            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
        except (TypeError, ValueError):
            return _err("endpoint_avg must be an integer")
        manual_bg = bg_cfg.get("manual_bg")

        # Peak specs
        peak_specs = body.get("peaks", [])
        if not peak_specs:
            return _err("'peaks' list is empty – provide at least one peak")

        # Validate peak ids are unique
        ids = [p.get("id") for p in peak_specs]
        if len(ids) != len(set(ids)):
            return _err("Duplicate peak ids found – each peak must have a unique 'id'")

        _ALLOWED_METHODS = {
            "leastsq", "least_squares", "nelder",
            "differential_evolution", "basinhopping",
        }
        fit_method = body.get("fit_method", "leastsq")
        if fit_method not in _ALLOWED_METHODS:
            return _err(f"Unknown fit_method '{fit_method}'")

        # Bounded, type-checked n_perturb (audit F7; also covers the F9
        # ValueError-on-bad-input case for this field). Reject out-of-range or
        # non-integer values with a clean 400 instead of a 500 or a worker hang.
        try:
            n_perturb = int(body.get("n_perturb", 5))
        except (TypeError, ValueError):
            return _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
        if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
            return _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")

        try:
            result = fitting.run_fit(
                energy=energy,
                counts=counts,
                peak_specs=peak_specs,
                background_method=bg_method,
                bg_start_idx=bg_start,
                bg_end_idx=bg_end,
                charge_shift_ev=0.0,
                fit_kws={"method": fit_method},
                manual_bg=manual_bg,
                n_perturb=n_perturb,
                endpoint_avg=endpoint_avg,
            )
        except ValueError as exc:
            # Our own validation: unknown shape/method, self/circular constraint,
            # "Master peak not found", bad numeric field, etc. (audit F10/F11).
            return _err(str(exc))
        except RuntimeError:
            # Solver-internal failure (e.g. lmfit non-convergence). Log the
            # detail; return a generic 422 that leaks no library internals.
            app.logger.exception("Fit failed")
            return _err("Fit failed — see server log for details.", 422)
        except Exception:
        _set("alpha", spec.get("alpha", 1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_alpha", False))
        _set("beta",  spec.get("beta",  1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_beta", False))
        _set("m",     spec.get("m",    50.0), min_=0.0, max_=499.0,
             vary=not spec.get("fix_m", True))

    return p


# ─────────────────────────────────────────────────────────────────────────────
# Main fitting API
# ─────────────────────────────────────────────────────────────────────────────

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
    if len(energy) != len(counts):
        raise ValueError("energy and counts must have the same length")
    if not peak_specs:
        raise ValueError("At least one peak specification is required")
    # Reject self/cyclic spin-orbit constraints before building lmfit exprs (F11)
    _validate_constraint_graph(peak_specs)

    # Apply charge correction
    energy = energy + charge_shift_ev

    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
    # narrow only the anchor window used to construct the background
    # curve. Reusing the slice for both was the bug where putting bg
    # anchors inside the ROI silently chopped the fit window — and the
    # reported χ², residuals, and σ — down to that same sub-slice.
    i0 = bg_start_idx if bg_start_idx is not None else 0
    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
    i0 = max(0, i0)
    i1 = min(len(energy), i1)
    # Normalize the user-supplied anchor pair: reversed order is a valid
    # choice — the frontend sends bg-start = higher BE and bg-end = lower
    # BE, so the index order depends on whether the data array is
    # BE-ascending or BE-descending. Treat the pair as an unordered
    # anchor window regardless of direction.
    if i0 > i1:
        i0, i1 = i1, i0
    # Bail to the full ROI only if the normalized window is genuinely
    # unusable (< 2 points): the integral / interp / linear-fit
    # functions below all need at least two distinct anchor points.
    if i1 - i0 < 2:
        i0, i1 = 0, len(energy)

    x = energy
    y = counts
    x_bg = energy[i0:i1]
    y_bg = counts[i0:i1]

    # ── Background ────────────────────────────────────────────────────────────
    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
    # physically defined only between the user's two anchor points: the
    # integral represents inelastic-loss cumulation through the peaks
    # *between* those anchors. Computing them over the full ROI would
    # let peaks outside the anchor window contribute to the loss
    # integral, which violates the model's premise. We therefore
    # compute them on [i0:i1] and flat-hold the endpoint value across
    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
    # values by construction, so constant extension is the least-bad
    # continuation. Linear backgrounds are extrapolated across the
    # full ROI (the line is well-defined outside the anchor window).
    bg_method = background_method.lower()
    bg_inner: np.ndarray | None = None

    if manual_bg is not None and bg_method == "manual":
        # manual_bg is a list of [be, intensity] anchor points from the
        # frontend. The anchors are BE-anchored (independent of i0/i1),
        # so interpolate them across the full ROI grid.
        anchors = sorted(manual_bg, key=lambda a: a[0])
        if len(anchors) >= 2:
            anchor_x = np.array([a[0] for a in anchors])
            anchor_y = np.array([a[1] for a in anchors])
            bg = np.interp(x, anchor_x, anchor_y)
        else:
            bg = linear_background(x, y)
    elif bg_method == "shirley":
        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
    elif bg_method == "smart":
        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
    elif bg_method == "smart_exp":
        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "shirley_linear":
        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "tougaard":
        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
    elif bg_method == "linear":
        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
        # across the full ROI. The line is well-defined everywhere, so
        # constant extension would discard real information.
        if x[i1 - 1] != x[i0]:
            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
        else:
            slope = 0.0
        bg = y[i0] + slope * (x - x[i0])
    elif bg_method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
            "bic": float(result.bic) if result.bic is not None else None,
        },
        "charge_shift_applied": charge_shift_ev,
    }


def compute_background_only(
    energy: np.ndarray,
    counts: np.ndarray,
    method: str = "shirley",
    start_idx: int | None = None,
    end_idx: int | None = None,
    endpoint_avg: int = 1,
) -> dict[str, Any]:
    """Return just the background array without fitting peaks."""
    i0 = start_idx if start_idx is not None else 0
    i1 = end_idx if end_idx is not None else len(energy)
    x, y = energy[i0:i1], counts[i0:i1]

    if method == "shirley":
        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
    elif method == "smart":
        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
    elif method == "smart_exp":
        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
    elif method == "shirley_linear":
        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
    elif method == "tougaard":
        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
    elif method == "linear":
        bg = linear_background(x, y)
    elif method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{method}'")

exec
/bin/zsh -lc 'git show c5a24ac''^:fitting.py | sed -n '"'300,470p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8Xa5o8g7' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uO2InUgq' (errno=Operation not permitted)


# ─────────────────────────────────────────────────────────────────────────────
# Background functions
# ─────────────────────────────────────────────────────────────────────────────

def shirley_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
) -> np.ndarray:
    """
    Iterative Shirley background (Proctor & Sherwood, Surf. Sci. 1982).

    Works on ascending or descending binding energy arrays.

    At each energy Eᵢ the background equals:
        B(Eᵢ) = B_high + (B_low – B_high) · ∫_{Eᵢ}^{E_max} s(E) dE
                                               ─────────────────────────
                                               ∫_{E_min}^{E_max} s(E) dE
    where s(E) = max(y(E) – B(E), 0) is the net signal.
    B_low  = y(E_min),  B_high = y(E_max)  (the endpoint levels).
    """
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    b_low = ys[0]    # background at low‑BE end
    b_high = ys[-1]  # background at high‑BE end

    B = np.linspace(b_low, b_high, len(ys))  # linear initial guess

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # O(n) cumulative integral from high-x end back to each point
        cum_right = np.zeros(len(ys))
        for i in range(len(ys) - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = b_high + (b_low - b_high) * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break

    return B[::-1] if flipped else B


def smart_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
) -> np.ndarray:
    """Smart (constrained Shirley): standard Shirley clamped to never exceed data."""
    if len(x) < 2:
        return np.zeros_like(y)
    shir = shirley_background(x, y, n_iter, tol)
    return np.minimum(shir, y)


def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Straight‑line background connecting the first and last data points."""
    slope = (y[-1] - y[0]) / (x[-1] - x[0]) if x[-1] != x[0] else 0.0
    return y[0] + slope * (x - x[0])


def smart_experimental_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Experimental constrained Shirley background, closer to public Avantage
    Smart description.  The data constraint is enforced *during* iteration,
    not as a post-hoc clamp.  Where the background would exceed the data it
    locks to the data, effectively moving the Shirley start inward.  Better
    for narrow spectral windows with sloped baselines."""
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    b_low = float(np.mean(ys[:cap]))      # low-BE endpoint
    b_high = float(np.mean(ys[-cap:]))     # high-BE endpoint
    step = b_low - b_high

    # Linear initial guess
    B = np.linspace(b_low, b_high, n)

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # Cumulative integral from high-BE end (right) back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            dx = xs[i + 1] - xs[i]
            cum_right[i] = cum_right[i + 1] + (signal[i] + signal[i + 1]) / 2 * dx
        total = cum_right[0]
        if total <= 0.0:
            break

        B = b_high + step * (cum_right / total)

        # Constrain during iteration: lock to data where bg exceeds it
        B = np.minimum(B, ys)

        if np.max(np.abs(B - B_prev)) < tol:
            break

    B = np.minimum(B, ys)  # final safety clamp
    return B[::-1] if flipped else B


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


def shirley_linear_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Hybrid Shirley + Linear background.

    1. Average *n_avg* points at each endpoint.
    2. Compute a linear baseline between the averaged endpoints.
    3. Subtract the linear baseline → flattened data.
    4. Iteratively compute a Shirley‑like cumulative correction on the
       flattened data, scaled by the endpoint step height.
    5. Add the correction back onto the linear baseline.
    6. Clamp so the background never exceeds the data.
    """
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:

codex
One concrete risk is emerging: the new direct `smart_background(..., n_avg=N)` semantics clamp against raw `y`, while the existing manual `run_fit`/`compute_background_only` paths still pre-average `y` before calling `smart_background`, so they clamp against the averaged copy. I’m going to quantify that and then check whether the focused tests would catch dropped `n_avg` at each layer.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 pytest -q -p no:cacheprovider tests/test_background_n_avg.py' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: pytest

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '300,420p' && nl -ba fitting.py | sed -n '1038,1062p' && nl -ba fitting.py | sed -n '1284,1298p'" in /Users/skyefortier/xps-verify
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
  1050	        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
  1051	    elif bg_method == "smart":
  1052	        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
  1053	    elif bg_method == "smart_exp":
  1054	        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
  1055	    elif bg_method == "shirley_linear":
  1056	        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
  1057	    elif bg_method == "tougaard":
  1058	        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
  1059	    elif bg_method == "linear":
  1060	        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
  1061	        # across the full ROI. The line is well-defined everywhere, so
  1062	        # constant extension would discard real information.
  1284	    i1 = end_idx if end_idx is not None else len(energy)
  1285	    x, y = energy[i0:i1], counts[i0:i1]
  1286	
  1287	    if method == "shirley":
  1288	        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
  1289	    elif method == "smart":
  1290	        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
  1291	    elif method == "smart_exp":
  1292	        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
  1293	    elif method == "shirley_linear":
  1294	        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
  1295	    elif method == "tougaard":
  1296	        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
  1297	    elif method == "linear":
  1298	        bg = linear_background(x, y)

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '284,318p' && nl -ba autofit/engine.py | sed -n '862,868p' && nl -ba autofit/engine.py | sed -n '2178,2184p' && nl -ba autofit/engine.py | sed -n '2587,2593p' && nl -ba tests/test_background_n_avg.py | sed -n '1,150p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   284	# Background
   285	# ─────────────────────────────────────────────────────────────────────────────
   286	
   287	def _compute_background(
   288	    x: np.ndarray,
   289	    y: np.ndarray,
   290	    bg: BackgroundType,
   291	    endpoint_avg: int = 1,
   292	) -> np.ndarray:
   293	    """Background for the autofit path.
   294	
   295	    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
   296	    (audit F3, 2026-07-17). Every background here now takes ``n_avg``
   297	    directly rather than requiring the caller to pre-average the array via
   298	    _apply_endpoint_averaging — which is exactly what this function forgot
   299	    to do, leaving Find Peaks unable to express an endpoint_avg the manual
   300	    path honours. Default 1 (raw endpoints) matches both the previous
   301	    behaviour of this function and app.py's own default, so wiring alone
   302	    changes nothing.
   303	    """
   304	    if bg is BackgroundType.SHIRLEY:
   305	        return shirley_background(x, y, n_avg=endpoint_avg)
   306	    if bg is BackgroundType.SMART:
   307	        return smart_background(x, y, n_avg=endpoint_avg)
   308	    if bg is BackgroundType.SMART_EXP:
   309	        from fitting import smart_experimental_background
   310	        return smart_experimental_background(x, y, n_avg=endpoint_avg)
   311	    if bg is BackgroundType.LINEAR:
   312	        return linear_background(x, y)
   313	    if bg is BackgroundType.TOUGAARD:
   314	        from fitting import tougaard_background
   315	        return tougaard_background(x, y, n_avg=endpoint_avg)
   316	    raise ValueError(f"Unknown background type: {bg}")
   317	
   318	
   862	    x = np.asarray(x, dtype=float)
   863	    y = np.asarray(y, dtype=float)
   864	    weights = np.asarray(weights, dtype=float)
   865	
   866	    bg = _compute_background(x, y, model.background)
   867	    y_sub = y - bg
   868	    composite = _build_composite_model(model)
  2178	        return _fast(
  2179	            f"insufficient_budget: {budget_remaining:.1f}s left < "
  2180	            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")
  2181	
  2182	    bg = _compute_background(x, y, aug_model.background)
  2183	    try:
  2184	        init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
  2587	        # periodic-table path) default to Shirley, the standard core-level
  2588	        # background (CLAUDE.md convention).
  2589	        det_bg_family = (candidates[0].background if candidates
  2590	                         else BackgroundType.SHIRLEY)
  2591	        det_bg = _compute_background(x, y, det_bg_family)
  2592	        preseed_specs = detect_out_of_grammar_dominants(
  2593	            x, y, det_bg, candidates, diagnostic_windows,
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
    16	    shirley_background,
    17	    smart_background,
    18	    smart_experimental_background,
    19	    tougaard_background,
    20	)
    21	
    22	
    23	def _noisy_endpoint_fixture():
    24	    """A spectrum whose single first/last SAMPLE is a noise outlier relative
    25	    to its neighborhood, so endpoint averaging visibly changes the reported
    26	    B_low/B_high and therefore the whole background curve."""
    27	    rng = np.random.default_rng(0)
    28	    x = np.linspace(700.0, 740.0, 200)
    29	    y = 4000.0 + 3000.0 * np.exp(-0.5 * ((x - 720.0) / 4.0) ** 2)
    30	    y = y.copy()
    31	    y[0] += 500.0    # single-point low-BE outlier
    32	    y[-1] -= 500.0   # single-point high-BE outlier
    33	    return x, y
    34	
    35	
    36	def test_shirley_background_default_n_avg_matches_pre_f3_output():
    37	    """n_avg=1 (the default) must reproduce the pre-F3 raw-endpoint
    38	    behaviour byte-for-byte -- this wiring must change no current output."""
    39	    x, y = _noisy_endpoint_fixture()
    40	    assert np.array_equal(shirley_background(x, y), shirley_background(x, y, n_avg=1))
    41	
    42	
    43	def test_shirley_background_n_avg_changes_output_on_noisy_endpoints():
    44	    """n_avg > 1 must actually average the endpoints internally and change
    45	    the result relative to raw endpoints, on a fixture designed so that
    46	    difference is visible."""
    47	    x, y = _noisy_endpoint_fixture()
    48	    raw = shirley_background(x, y, n_avg=1)
    49	    averaged = shirley_background(x, y, n_avg=8)
    50	    assert not np.allclose(raw, averaged), (
    51	        "n_avg=8 produced the same background as n_avg=1 on a fixture with "
    52	        "a deliberate single-point endpoint outlier"
    53	    )
    54	
    55	
    56	def test_shirley_background_n_avg_matches_external_pre_averaging():
    57	    """Calling shirley_background(x, y, n_avg=N) must equal the OLD calling
    58	    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
    59	    so this is a pure convenience wrapper, not a new averaging algorithm."""
    60	    x, y = _noisy_endpoint_fixture()
    61	    for n_avg in (1, 4, 8):
    62	        direct = shirley_background(x, y, n_avg=n_avg)
    63	        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
    64	        assert np.array_equal(direct, pre_averaged), f"mismatch at n_avg={n_avg}"
    65	
    66	
    67	def test_smart_background_default_n_avg_matches_pre_f3_output():
    68	    x, y = _noisy_endpoint_fixture()
    69	    assert np.array_equal(smart_background(x, y), smart_background(x, y, n_avg=1))
    70	
    71	
    72	def test_smart_background_forwards_n_avg_to_shirley():
    73	    """smart_background(x, y, n_avg=N) must equal
    74	    minimum(shirley_background(x, y, n_avg=N), y) -- the clamp applies
    75	    against the RAW data, not an endpoint-averaged copy, so averaging only
    76	    ever moves the background curve, never the reported net counts."""
    77	    x, y = _noisy_endpoint_fixture()
    78	    for n_avg in (1, 4, 8):
    79	        got = smart_background(x, y, n_avg=n_avg)
    80	        expected = np.minimum(shirley_background(x, y, n_avg=n_avg), y)
    81	        assert np.array_equal(got, expected), f"mismatch at n_avg={n_avg}"
    82	
    83	
    84	def test_smart_background_n_avg_changes_output_on_noisy_endpoints():
    85	    x, y = _noisy_endpoint_fixture()
    86	    raw = smart_background(x, y, n_avg=1)
    87	    averaged = smart_background(x, y, n_avg=8)
    88	    assert not np.allclose(raw, averaged)
    89	
    90	
    91	def test_apply_endpoint_averaging_still_importable_and_unchanged():
    92	    """F3 relocates _apply_endpoint_averaging above shirley_background in
    93	    fitting.py's source order; its behaviour must not change."""
    94	    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    95	    out = _apply_endpoint_averaging(y, 2)
    96	    assert np.array_equal(out, np.array([1.5, 1.5, 3.0, 4.0, 5.0, 6.0, 7.5, 7.5]))
    97	
    98	
    99	def test_compute_background_default_endpoint_avg_matches_pre_f3_output():
   100	    """autofit/engine.py's _compute_background(x, y, bg) with no
   101	    endpoint_avg argument must reproduce pre-F3 output exactly, for every
   102	    background type it dispatches -- pure wiring, no behaviour change."""
   103	    from autofit.engine import BackgroundType, _compute_background
   104	
   105	    x, y = _noisy_endpoint_fixture()
   106	    for bg_type in (BackgroundType.SHIRLEY, BackgroundType.SMART,
   107	                    BackgroundType.SMART_EXP, BackgroundType.LINEAR,
   108	                    BackgroundType.TOUGAARD):
   109	        no_arg = _compute_background(x, y, bg_type)
   110	        default_arg = _compute_background(x, y, bg_type, endpoint_avg=1)
   111	        assert np.array_equal(no_arg, default_arg), f"mismatch for {bg_type}"
   112	
   113	
   114	@pytest.mark.parametrize("bg_type_name,direct_fn", [
   115	    ("SHIRLEY", shirley_background),
   116	    ("SMART", smart_background),
   117	    ("SMART_EXP", smart_experimental_background),
   118	    ("TOUGAARD", tougaard_background),
   119	])
   120	def test_compute_background_forwards_endpoint_avg(bg_type_name, direct_fn):
   121	    """_compute_background(x, y, bg, endpoint_avg=N) must match calling the
   122	    underlying fitting.py function directly with n_avg=N -- Find Peaks and
   123	    manual Run Fit must agree once both pass the same endpoint_avg."""
   124	    from autofit.engine import BackgroundType, _compute_background
   125	
   126	    x, y = _noisy_endpoint_fixture()
   127	    bg_type = getattr(BackgroundType, bg_type_name)
   128	    for n_avg in (1, 4, 8):
   129	        via_engine = _compute_background(x, y, bg_type, endpoint_avg=n_avg)
   130	        direct = direct_fn(x, y, n_avg=n_avg)
   131	        assert np.array_equal(via_engine, direct), (
   132	            f"{bg_type_name} mismatch at endpoint_avg={n_avg}"
   133	        )
   134	
   135	
   136	def test_compute_background_linear_ignores_endpoint_avg():
   137	    """linear_background has no endpoint-averaging concept (it already
   138	    reads only the two edge points); endpoint_avg must be accepted without
   139	    error and have no effect."""
   140	    from autofit.engine import BackgroundType, _compute_background
   141	
   142	    x, y = _noisy_endpoint_fixture()
   143	    no_avg = _compute_background(x, y, BackgroundType.LINEAR)
   144	    with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
   145	    assert np.array_equal(no_avg, with_avg)

codex
`pytest` is not installed in this environment (`zsh: command not found: pytest`), and the read-only sandbox also blocks here-doc temp files, so I’m switching to `python -c` probes with bytecode disabled. That should still let me test the numerical behavior without touching the worktree.
exec
/bin/zsh -lc "rg -n \"def (pseudo|voigt|gaussian|lorentzian|doniach|asymmetric|_.*peak|.*lineshape)|endpoint_avg|_compute_background\\(\" templates/index.html autofit/methods fitting.py app.py autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:208:    def __init__(self, x, y, method_id, opts, peak_specs, grammar):
app.py:716:        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
app.py:718:            ep_avg = max(1, int(body.get("endpoint_avg", 1)))
app.py:720:            return _err("endpoint_avg must be an integer")
app.py:726:                endpoint_avg=ep_avg,
app.py:792:        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
app.py:794:            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
app.py:796:            return _err("endpoint_avg must be an integer")
app.py:839:                endpoint_avg=endpoint_avg,
fitting.py:771:def _validate_constraint_graph(peak_specs: list[dict]) -> None:
fitting.py:802:def _make_peak_params(
fitting.py:965:    endpoint_avg: int = 1,
fitting.py:1050:        bg_inner = shirley_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1052:        bg_inner = smart_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1054:        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1056:        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
fitting.py:1058:        bg_inner = tougaard_background(x_bg, _apply_endpoint_averaging(y_bg, endpoint_avg))
fitting.py:1280:    endpoint_avg: int = 1,
fitting.py:1288:        bg = shirley_background(x, _apply_endpoint_averaging(y, endpoint_avg))
fitting.py:1290:        bg = smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))
fitting.py:1292:        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
fitting.py:1294:        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
fitting.py:1296:        bg = tougaard_background(x, _apply_endpoint_averaging(y, endpoint_avg))
autofit/engine.py:287:def _compute_background(
autofit/engine.py:291:    endpoint_avg: int = 1,
autofit/engine.py:295:    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
autofit/engine.py:299:    to do, leaving Find Peaks unable to express an endpoint_avg the manual
autofit/engine.py:305:        return shirley_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:307:        return smart_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:310:        return smart_experimental_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:315:        return tougaard_background(x, y, n_avg=endpoint_avg)
autofit/engine.py:338:def _peak_estimate_in_window(
autofit/engine.py:866:    bg = _compute_background(x, y, model.background)
autofit/engine.py:2182:    bg = _compute_background(x, y, aug_model.background)
autofit/engine.py:2591:        det_bg = _compute_background(x, y, det_bg_family)
templates/index.html:6675:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvg };
templates/index.html:6783:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvgVal };
autofit/methods/ic_model_comparison.py:206:def _peaks_from_report(
autofit/methods/sparse_map.py:198:        bg = _compute_background(x, y, grammar.candidates[0].background)
autofit/methods/least_squares.py:21:    "background_method", "bg_start_idx", "bg_end_idx", "endpoint_avg",
autofit/methods/least_squares.py:57:            endpoint_avg=opts.pop("endpoint_avg", 1),
autofit/methods/bayesian_exchange_mc.py:348:            bg = _compute_background(x, y, model.background)
autofit/methods/bayesian_exchange_mc.py:493:def _posterior_peaks(win: dict, ci_level: float) -> tuple[list[dict], dict]:

exec
/bin/zsh -lc "python3 -c \"import subprocess, ast, difflib; old=subprocess.check_output(['git','show','c5a24ac"'^:fitting.py'"'], text=True); new=open('fitting.py').read(); get=lambda s: ast.get_source_segment(s, next(n for n in ast.parse(s).body if isinstance(n, ast.FunctionDef) and n.name=='_apply_endpoint_averaging')); o=get(old); n=get(new); print('helper_byte_identical', o==n); print('old_lines', len(o.splitlines()), 'new_lines', len(n.splitlines())); print('\\n'.join(difflib.unified_diff(o.splitlines(), n.splitlines(), lineterm='')))\"" in /Users/skyefortier/xps-verify
 succeeded in 124ms:
helper_byte_identical True
old_lines 12 new_lines 12


codex
The helper relocation checks out: AST source extraction from `c5a24ac^:fitting.py` and current `fitting.py` reports the `_apply_endpoint_averaging` function source is byte-identical. I also confirmed `app.py` still defaults `endpoint_avg` to `1` in both `/api/background` and `/api/fit`.
exec
/bin/zsh -lc "sed -n '180,215p' autofit/methods/sparse_map.py && sed -n '336,356p' autofit/methods/bayesian_exchange_mc.py && sed -n '45,63p' autofit/methods/least_squares.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> MethodResult:
        if grammar is None:
            raise ValueError("sparse_map requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown sparse_map options: {sorted(unknown)}")
        cfg = {k: type(DEFAULTS[k])(opts.pop(k, DEFAULTS[k])) for k in DEFAULTS}
        lambda_fixed = opts.pop("lambda_fixed", None)

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        bg = _compute_background(x, y, grammar.candidates[0].background)
        y_net = y - bg
        n = len(y_net)

        A, atoms, norms, unexpressible = _build_dictionary(
            x, grammar, cfg["n_widths"])
        An = A / np.linalg.norm(A, axis=0)

        lam_max = float(np.max(An.T @ y_net))
        if lam_max <= 0:
            return MethodResult(method_id=self.id, success=False,
                                message="no positive correlation with any atom")
        if lambda_fixed is not None:
            lam_path = [float(lambda_fixed)]
        else:
            lam_path = list(np.geomspace(
                lam_max * 0.999, lam_max * cfg["lambda_min_ratio"],
                cfg["n_lambdas"]))
        # confidently-resolved F gap that a different seed flips — the
        # split-half proxy is a LOWER bound and can miss it).  k replicates
        # cost k× runtime; the across-replicate half-range is a genuine
        # independent-run MC error and dominates the split-half bound in the
        # selection warning.  Default 1 = cost-neutral single run.
        seed_replicates = int(opts.pop("seed_replicates", 1))
        if seed_replicates < 1:
            raise ValueError("seed_replicates must be >= 1")

        per_candidate: list[dict] = []
        runs: dict[str, dict] = {}
        for model in candidates:
            bg = _compute_background(x, y, model.background)
            y_net = y - bg
            try:
                space = _param_space(model, x, y_net)
                run = run_exchange_mc(x, y_net, space, weights=weights, **mc_kwargs)
                rep_fs = [run["free_energy"]]
                for j in range(1, seed_replicates):
                    rep_kwargs = dict(mc_kwargs,
                                      rng_seed=mc_kwargs["rng_seed"] + j)
        if unknown:
            raise ValueError(f"unknown least_squares options: {sorted(unknown)}")
        fit_method = opts.pop("fit_method", None)
        fit_kws = {"method": fit_method} if fit_method else None

        res = run_fit(
            np.asarray(x, dtype=float),
            np.asarray(y, dtype=float),
            peak_specs,
            background_method=opts.pop("background_method", "shirley"),
            bg_start_idx=opts.pop("bg_start_idx", None),
            bg_end_idx=opts.pop("bg_end_idx", None),
            endpoint_avg=opts.pop("endpoint_avg", 1),
            n_perturb=opts.pop("n_perturb", 0),
            manual_bg=opts.pop("manual_bg", None),
            fit_kws=fit_kws,
        )

        peaks = []

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'exec(\"\"\"
import numpy as np
from fitting import shirley_background, smart_background, smart_experimental_background, tougaard_background, linear_background, _apply_endpoint_averaging, compute_background_only
from autofit.engine import BackgroundType, _compute_background
x=np.linspace(700.0,740.0,200)
y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2)
y=y.copy(); y[0]+=500.0; y[-1]-=500.0
for name,fn in [(\"shirley\",shirley_background),(\"smart\",smart_background),(\"smart_exp\",smart_experimental_background),(\"tougaard\",tougaard_background)]:
    raw=fn(x,y,n_avg=1); avg=fn(x,y,n_avg=8); d=avg-raw
    print(name, \"allclose?\", np.allclose(raw,avg), \"max_abs_diff\", float(np.max(np.abs(d))), \"first/raw_avg\", float(raw[0]), float(avg[0]), \"last/raw_avg\", float(raw[-1]), float(avg[-1]))
old_smart=smart_background(x,_apply_endpoint_averaging(y,8))
new_smart=smart_background(x,y,n_avg=8)
print(\"smart old_preavg_vs_new_direct array_equal\", np.array_equal(old_smart,new_smart), \"allclose\", np.allclose(old_smart,new_smart), \"max_abs_diff\", float(np.max(np.abs(old_smart-new_smart))))
print(\"old_new endpoints\", float(old_smart[0]), float(new_smart[0]), float(old_smart[-1]), float(new_smart[-1]))
manual=compute_background_only(x,y,method=\"smart\",endpoint_avg=8)[\"background\"]
engine=_compute_background(x,y,BackgroundType.SMART,endpoint_avg=8)
print(\"compute_background_only smart vs engine array_equal\", np.array_equal(manual,engine), \"allclose\", np.allclose(manual,engine), \"max_abs_diff\", float(np.max(np.abs(manual-engine))))
\"\"\")'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'git diff --name-only c5a24ac''^ c5a24ac && git diff --stat c5a24ac''^ c5a24ac -- templates/index.html '"'autofit/methods/*.py' app.py && git diff --name-only c5a24ac"'^ c5a24ac -- templates/index.html autofit/methods app.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-aOi29bVi' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mqpjPkIz' (errno=Operation not permitted)
autofit/engine.py
fitting.py
tests/test_background_n_avg.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cCaa8rAX' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1oY3ZM8W' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-EwPLknI0' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-eIv9mjPj' (errno=Operation not permitted)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'exec(\"\"\"
import numpy as np, fitting
from fitting import _apply_endpoint_averaging
x=np.linspace(700.0,740.0,200)
y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2)
y=y.copy(); y[0]+=500.0; y[-1]-=500.0
orig_shirley=fitting.shirley_background
orig_smart=fitting.smart_background

def broken_shirley(x,y,n_iter=200,tol=1e-6,n_avg=1):
    return orig_shirley(x,y,n_iter,tol,n_avg=1)

def broken_smart_drop_forward(x,y,n_iter=200,tol=1e-6,n_avg=1):
    return np.minimum(orig_shirley(x,y,n_iter,tol,n_avg=1), y)

for label, fn in [(\"broken_shirley_n_avg_ignored\", broken_shirley), (\"broken_smart_drops_forward\", broken_smart_drop_forward)]:
    raw=fn(x,y,n_avg=1); avg=fn(x,y,n_avg=8)
    print(label, \"change_test_would_pass\", not np.allclose(raw,avg), \"max_abs_diff\", float(np.max(np.abs(avg-raw))))
# Engine forwarding probes by replacing engine globals/import target after import.
from autofit import engine
from autofit.engine import BackgroundType
# For SHIRLEY/SMART, engine holds imported globals.
for bg, attr, direct in [(BackgroundType.SHIRLEY,\"shirley_background\",fitting.shirley_background),(BackgroundType.SMART,\"smart_background\",fitting.smart_background),(BackgroundType.LINEAR,\"linear_background\",fitting.linear_background)]:
    old=getattr(engine,attr)
    def drop(x,y,*args, _direct=direct, **kwargs):
        kwargs.pop(\"n_avg\", None)
        return _direct(x,y,*args,**kwargs)
    setattr(engine,attr,drop)
    via=engine._compute_background(x,y,bg,endpoint_avg=8)
    exp=direct(x,y,n_avg=8) if attr "'!= "linear_background" else direct(x,y)
    print("engine drop", bg.name, "test_would_fail", not np.array_equal(via,exp), "max_abs_diff", float(np.max(np.abs(via-exp))))
    setattr(engine,attr,old)
# SMART_EXP/TOUGAARD are imported inside function from fitting, so monkeypatch fitting module.
for bg, attr in [(BackgroundType.SMART_EXP,"smart_experimental_background"),(BackgroundType.TOUGAARD,"tougaard_background")]:
    direct=getattr(fitting, attr); old=getattr(fitting, attr)
    def drop(x,y,*args, _direct=direct, **kwargs):
        kwargs.pop("n_avg", None)
        return _direct(x,y,*args,**kwargs)
    setattr(fitting, attr, drop)
    via=engine._compute_background(x,y,bg,endpoint_avg=8)
    exp=direct(x,y,n_avg=8)
    print("engine drop", bg.name, "test_would_fail", not np.array_equal(via,exp), "max_abs_diff", float(np.max(np.abs(via-exp))))
    setattr(fitting, attr, old)
""")'"'" in /Users/skyefortier/xps-verify
 exited 1 in 128ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<string>", line 3, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

 exited 1 in 120ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<string>", line 2, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

codex
The local Python environment also lacks `lmfit`, so importing `fitting.py` directly fails before any background function can run. I can still probe by stubbing the missing imports or extracting the background functions, but the absence of both `pytest` and `lmfit` means I cannot execute the committed tests as-is here.
exec
/bin/zsh -lc "sed -n '1,80p' fitting.py && sed -n '1,80p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
"""
fitting.py – XPS peak fitting engine using lmfit.

Supported lineshapes
--------------------
  gaussian        – pure Gaussian (amplitude at peak max, FWHM parameterised)
  lorentzian      – pure Lorentzian
  pseudo_voigt_gl – linear GL mix: (1‑η)·G + η·L  (η = Lorentzian fraction)
  asymmetric_gl   – GL mix with independent left/right FWHM
  doniach_sunjic  – metallic asymmetric lineshape
  ds_g            – DS+G: DS core × Gaussian convolution (formerly "la_casaxps")
  la_casaxps      – TRUE CasaXPS LA(α,β,m): asymmetric base Lorentzian + integer-kernel Gauss conv

Backgrounds
-----------
  shirley         – iterative Shirley (Proctor & Sherwood 1982)
  linear          – straight‑line between endpoints
  none            – flat zero

Spin‑orbit constraints are handled via lmfit parameter expressions.
"""

from __future__ import annotations

import logging
import warnings
from typing import Any

import numpy as np
from lmfit import Model, Parameters
from scipy.integrate import trapezoid

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lineshape functions (all FWHM‑parameterised, amplitude = peak maximum)
# ─────────────────────────────────────────────────────────────────────────────

_LN2 = np.log(2.0)
_SQRT_PI_4LN2 = np.sqrt(np.pi / (4.0 * _LN2))  # ≈ 1.06447


def _gaussian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Gaussian; amplitude is the peak maximum value."""
    return amplitude * np.exp(-4.0 * _LN2 * ((x - center) / fwhm) ** 2)


def _lorentzian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Lorentzian; amplitude is the peak maximum value."""
    hwhm = fwhm / 2.0
    return amplitude * hwhm ** 2 / ((x - center) ** 2 + hwhm ** 2)


def _pseudo_voigt_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    gl_ratio: float,
) -> np.ndarray:
    """
    Pseudo‑Voigt as a linear combination of Gaussian and Lorentzian.

    gl_ratio : Lorentzian fraction  (0 = pure Gaussian, 1 = pure Lorentzian)
    """
    eta = float(np.clip(gl_ratio, 0.0, 1.0))
    return (1.0 - eta) * _gaussian(x, amplitude, center, fwhm) + eta * _lorentzian(
        x, amplitude, center, fwhm
    )


def _asymmetric_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    asymmetry: float,
    gl_ratio: float,
) -> np.ndarray:
    """
"""
Model-comparison engine — the fitalg pipeline ported onto main's fitting.py
and generalized to region-agnostic grammars (spec v2.1 §6).

Pipeline per candidate: primary fit → N perturbed refits (stability) →
slot matching by grammar role → absent-slot detection → residual
diagnostics → residual-guided proposal pass → filter-then-rank with BIC*.

Provenance: ported from the public ``xps-app-fitalg`` repo's
``model_comparison.py`` (validated there on HOPG + PET C 1s).  Changes made
in the port, besides symbol renames:

- lineshape layer rebuilt against CURRENT ``fitting.py``: fitalg's
  ``LA_ASYMMETRIC`` (α, β=Lorentzian-HWHM, m_gauss) is main's ``ds_g``; the
  true CasaXPS ``la_casaxps`` (exponent α/β + kernel-points m) is new here,
  as are ``asymmetric_gl`` / ``gaussian`` / ``lorentzian``.
- generic per-slot ``fixed_params`` / ``param_ranges`` replace the
  LA-specific ``fixed_lorentzian_hwhm`` / ``alpha_range`` fields.
- spin-orbit amplitude linkage (``area_ratio`` fixed, or
  ``area_ratio_range`` bounded-relaxed) — needed by doublet regions.
- boundary-hit shape-parameter exclusions are per-lineshape (a width-like
  ``beta`` in DS+G at a bound is a pathology; an exponent-like ``beta`` in
  LACX at a bound is a shape preference).

All numeric thresholds below are **UNVERIFIED tunables** (spec §9 —
sensitivity-test before publication claims); they carry fitalg's defaults.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from lmfit import Model, Parameters
from lmfit.model import ModelResult
from scipy.integrate import trapezoid

from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background

from .candidates import (build_candidate_pool, build_detection_candidate,
                         merge_residual_attempts)

from .grammar import (
    BACKEND_SHAPE,
    BackgroundType,
    CandidateGrammar,
    CandidateModel,
    ComponentSlot,
    LineShape,
)

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# UNVERIFIED tunables (fitalg defaults; spec §9 sensitivity-test items)
# ─────────────────────────────────────────────────────────────────────────────

ABSENT_SLOT_AREA_FRACTION = 0.02
ABSENT_SLOT_PERSISTENCE_THRESHOLD = 0.7
DEFAULT_PERSISTENCE_THRESHOLD = 0.7
DEFAULT_BIC_AMBIGUITY = 2.0
# Decisive-override DOMINANCE rule (Codex cookbook review, blockers 2–3).
# A stable-but-boundary-limited candidate is promoted ahead of the clean
# tier only when ALL of the following hold:
#   (1) it is REFIT with its pegged parameters FIXED at their bounds — the
#       Laplace-style BIC* approximation is invalid at a constraint wall,
#       and the fixed-bound refit gives an honest parameter count;
#   (2) the refit's BIC* beats the best clean candidate's by more than
#       CONDITIONAL_OVERRIDE_DELTA_BIC (10 — the conventional "very strong"
#       threshold, Kass & Raftery, JASA 90 (1995) 773; UNVERIFIED as applied
#       to this heuristic BIC* on processed XPS data — tunable);
#   (3) its reduced χ² is also strictly better (BIC* is never the sole
#       decision axis — spec §6 trust order); and
#   (4) the clean best shows residual-structure flags (autocorrelation or
#       flagged windows) — evidence that it is genuinely mis-fitting, not

exec
/bin/zsh -lc 'rg -n "''^(import|from) " fitting.py autofit/engine.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
fitting.py:23:from __future__ import annotations
fitting.py:25:import logging
fitting.py:26:import warnings
fitting.py:27:from typing import Any
fitting.py:29:import numpy as np
fitting.py:30:from lmfit import Model, Parameters
fitting.py:31:from scipy.integrate import trapezoid
autofit/engine.py:29:from __future__ import annotations
autofit/engine.py:31:import logging
autofit/engine.py:32:import re
autofit/engine.py:33:import time
autofit/engine.py:34:from dataclasses import dataclass, field
autofit/engine.py:35:from typing import Callable, Optional
autofit/engine.py:37:import numpy as np
autofit/engine.py:38:from lmfit import Model, Parameters
autofit/engine.py:39:from lmfit.model import ModelResult
autofit/engine.py:40:from scipy.integrate import trapezoid
autofit/engine.py:42:from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background
autofit/engine.py:44:from .candidates import (build_candidate_pool, build_detection_candidate,
autofit/engine.py:47:from .grammar import (

exec
/bin/zsh -lc "rg -n \"_compute_background\\(\" -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/engine.py:287:def _compute_background(
autofit/engine.py:866:    bg = _compute_background(x, y, model.background)
autofit/engine.py:2182:    bg = _compute_background(x, y, aug_model.background)
autofit/engine.py:2591:        det_bg = _compute_background(x, y, det_bg_family)
autofit/methods/bayesian_exchange_mc.py:348:            bg = _compute_background(x, y, model.background)
autofit/methods/sparse_map.py:198:        bg = _compute_background(x, y, grammar.candidates[0].background)
tests/test_background_n_avg.py:100:    """autofit/engine.py's _compute_background(x, y, bg) with no
tests/test_background_n_avg.py:109:        no_arg = _compute_background(x, y, bg_type)
tests/test_background_n_avg.py:110:        default_arg = _compute_background(x, y, bg_type, endpoint_avg=1)
tests/test_background_n_avg.py:121:    """_compute_background(x, y, bg, endpoint_avg=N) must match calling the
tests/test_background_n_avg.py:129:        via_engine = _compute_background(x, y, bg_type, endpoint_avg=n_avg)
tests/test_background_n_avg.py:143:    no_avg = _compute_background(x, y, BackgroundType.LINEAR)
tests/test_background_n_avg.py:144:    with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
tests/autofit/test_preseed_dominants.py:62:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:85:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:104:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:298:    bg = eng._compute_background(x, y, aug_model.background)
tests/autofit/test_candidate_pool_real_gate.py:101:    det_bg = eng._compute_background(x, y, cands[0].background)
tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_stage2_completeness.py:397:    dom = e2.detect_out_of_grammar_dominants(x, y, e2._compute_background(

exec
/bin/zsh -lc "rg -n \"def tougaard_background|def smart_experimental_background|def shirley_linear_background|def compute_background_only|def run_fit\" fitting.py && sed -n '410,570p' fitting.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
410:def smart_experimental_background(
466:def shirley_linear_background(
528:def tougaard_background(
954:def run_fit(
1274:def compute_background_only(
def smart_experimental_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Experimental constrained Shirley background, closer to public Avantage
    Smart description.  The data constraint is enforced *during* iteration,
    not as a post-hoc clamp.  Where the background would exceed the data it
    locks to the data, effectively moving the Shirley start inward.  Better
    for narrow spectral windows with sloped baselines."""
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    b_low = float(np.mean(ys[:cap]))      # low-BE endpoint
    b_high = float(np.mean(ys[-cap:]))     # high-BE endpoint
    step = b_low - b_high

    # Linear initial guess
    B = np.linspace(b_low, b_high, n)

    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        # Cumulative integral from high-BE end (right) back to each point
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            dx = xs[i + 1] - xs[i]
            cum_right[i] = cum_right[i + 1] + (signal[i] + signal[i + 1]) / 2 * dx
        total = cum_right[0]
        if total <= 0.0:
            break

        B = b_high + step * (cum_right / total)

        # Constrain during iteration: lock to data where bg exceeds it
        B = np.minimum(B, ys)

        if np.max(np.abs(B - B_prev)) < tol:
            break

    B = np.minimum(B, ys)  # final safety clamp
    return B[::-1] if flipped else B


def shirley_linear_background(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 200,
    tol: float = 1e-6,
    n_avg: int = 1,
) -> np.ndarray:
    """Hybrid Shirley + Linear background.

    1. Average *n_avg* points at each endpoint.
    2. Compute a linear baseline between the averaged endpoints.
    3. Subtract the linear baseline → flattened data.
    4. Iteratively compute a Shirley‑like cumulative correction on the
       flattened data, scaled by the endpoint step height.
    5. Add the correction back onto the linear baseline.
    6. Clamp so the background never exceeds the data.
    """
    if len(x) < 2:
        return np.zeros_like(y)

    # Work on ascending copy
    if x[0] > x[-1]:
        xs, ys = x[::-1].copy(), y[::-1].copy()
        flipped = True
    else:
        xs, ys = x.copy(), y.copy()
        flipped = False

    n = len(ys)
    cap = max(1, min(n_avg, n // 4))
    IL = float(np.mean(ys[:cap]))      # low‑BE endpoint
    IH = float(np.mean(ys[-cap:]))     # high‑BE endpoint

    # Linear baseline
    linear = np.linspace(IL, IH, n)

    # Flatten
    flat = ys - linear

    step_h = abs(IL - IH)
    if step_h < 1e-12:
        return linear[::-1] if flipped else linear

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


def tougaard_background(
    x: np.ndarray,
    y: np.ndarray,
    n_avg: int = 1,
) -> np.ndarray:
    """Single-pass Tougaard universal-cross-section background, with the
    constant (pre-loss) term the window-limited integral cannot generate.

    Uses the two-parameter universal loss function
    K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
    cross-section fitted to noble/transition-metal optical data; the
    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).

    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
    window BEGINS in a loss-free region, so that J at the low-BE edge is
    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
    there is a large inelastic baseline produced by every lower-BE
    (higher-KE) transition OUTSIDE the window, which a window-limited
    integral structurally cannot reproduce.  Because K(0) = 0, the bare
    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
    — the background visibly dove to ~0 there, and a flat featureless
    window produced a full-amplitude phantom "signal".

    So the low-BE edge level is taken as a constant offset C0 (the
    out-of-window baseline the kernel cannot see), the kernel runs over the
    net (J - C0), and the amplitude is then anchored so the background
    meets the measured intensity at the HIGH-BE edge — the standard
    practical Tougaard criterion (B is effectively fitted, which is why the
    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
    fitting B together with an offset rather than B alone.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels are read, so neither C0 nor the high-BE anchor rests on a single
    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
    endpoints = previous behaviour.

    The background at each binding energy accumulates loss contributions
    from electrons emitted at LOWER BE (higher kinetic energy), so the
    one-sided sum requires a descending-BE grid; input in either BE order
    is normalized internally.  Mirrors the frontend JS twin
    ``tougaardBackground``.

exec
/bin/zsh -lc "sed -n '1,90p' autofit/grammar.py && rg -n \"class BackgroundType|BackgroundType\" autofit/grammar.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
"""
Composable grammar for the autofit engine (spec v2.1 §2).

``resolve(phases, regions, ...)`` → :class:`CandidateGrammar`.

Three layers:

- **Layer A** — material class (per phase): lineshape family admissibility,
  charge strategy, reference.
- **Layer B** — region/element module (``autofit.regions``): doublet
  Δso/ratio, BE windows, allowed lineshapes, satellites, core-hole width.
- **Layer C** — oxidation-state override (multiplet fingerprint, BE shift).
  Seam only in Stage 2 — region modules may accept it, none require it.

Multi-phase model (v2 B1 fix): a ``phases`` list, never a pairwise
``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
``phase_id``; when the same region is contributed by more than one phase the
caller MUST disambiguate with ``target_phases`` (Codex precondition 2 — a
region is not a unique key).

Multi-region co-fit ([Skye]): ``regions`` is multi-valued; the grammars of
all requested regions are composed into joint candidates fit together in the
shared window (e.g. U 4f + N 1s overlap).
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .fit_physics import provenance_entries as _fit_physics_provenance

__all__ = [
    "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
    "CandidateModel", "CandidateGrammar", "PhaseAmbiguityError",
    "UnknownRegionError", "resolve", "BACKEND_SHAPE",
]


class LineShape(Enum):
    GAUSSIAN = "gaussian"
    LORENTZIAN = "lorentzian"
    PSEUDO_VOIGT = "pseudo_voigt"    # backend pseudo_voigt_gl
    ASYM_GL = "asym_gl"              # backend asymmetric_gl
    DS = "doniach_sunjic"
    DS_G = "ds_g"                    # DS core ⊗ Gaussian (fitalg's "LA_ASYMMETRIC")
    LACX = "la_casaxps"              # true CasaXPS LA(α, β, m)


# LineShape → fitting.py _SHAPE_FUNCS key
BACKEND_SHAPE: dict[LineShape, str] = {
    LineShape.GAUSSIAN: "gaussian",
    LineShape.LORENTZIAN: "lorentzian",
    LineShape.PSEUDO_VOIGT: "pseudo_voigt_gl",
    LineShape.ASYM_GL: "asymmetric_gl",
    LineShape.DS: "doniach_sunjic",
    LineShape.DS_G: "ds_g",
    LineShape.LACX: "la_casaxps",
}

# Shapes whose asymmetric tail encodes physics (metallic screening or an
# unresolvable multiplet envelope) — admissible only where Layer A allows.
ASYMMETRIC_SHAPES = frozenset({LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX})


class BackgroundType(Enum):
    SHIRLEY = "shirley"
    SMART = "smart"
    SMART_EXP = "smart_exp"      # Avantage-style constrained Shirley
    LINEAR = "linear"
    TOUGAARD = "tougaard"


class MaterialClass(Enum):
    CONDUCTOR = "conductor"
    SEMICONDUCTOR = "semiconductor"
    INSULATOR = "insulator"


@dataclass(frozen=True)
class Phase:
    """
    One physical phase of the sample (spec §2).  ``regions`` declares which
    core-level regions this phase's material contributes signal to — the
    resolver uses it to detect region↔phase ambiguity.
    """
    id: str
37:    "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
69:class BackgroundType(Enum):
168:    background: BackgroundType

exec
/bin/zsh -lc "sed -n '528,620p' fitting.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
def tougaard_background(
    x: np.ndarray,
    y: np.ndarray,
    n_avg: int = 1,
) -> np.ndarray:
    """Single-pass Tougaard universal-cross-section background, with the
    constant (pre-loss) term the window-limited integral cannot generate.

    Uses the two-parameter universal loss function
    K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
    cross-section fitted to noble/transition-metal optical data; the
    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).

    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
    window BEGINS in a loss-free region, so that J at the low-BE edge is
    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
    there is a large inelastic baseline produced by every lower-BE
    (higher-KE) transition OUTSIDE the window, which a window-limited
    integral structurally cannot reproduce.  Because K(0) = 0, the bare
    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
    — the background visibly dove to ~0 there, and a flat featureless
    window produced a full-amplitude phantom "signal".

    So the low-BE edge level is taken as a constant offset C0 (the
    out-of-window baseline the kernel cannot see), the kernel runs over the
    net (J - C0), and the amplitude is then anchored so the background
    meets the measured intensity at the HIGH-BE edge — the standard
    practical Tougaard criterion (B is effectively fitted, which is why the
    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
    fitting B together with an offset rather than B alone.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels are read, so neither C0 nor the high-BE anchor rests on a single
    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
    endpoints = previous behaviour.

    The background at each binding energy accumulates loss contributions
    from electrons emitted at LOWER BE (higher kinetic energy), so the
    one-sided sum requires a descending-BE grid; input in either BE order
    is normalized internally.  Mirrors the frontend JS twin
    ``tougaardBackground``.
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
    if n_avg > 1:
        ya = _apply_endpoint_averaging(ya, n_avg)

    # The one-sided loss sum below (j >= i) is physical only when BE
    # DESCENDS along the array: the loss contributions at x[i] must come
    # from lower-BE (higher-KE) emitters, which sit at higher indices only
    # on a descending grid. Normalize to descending internally and flip
    # the result back — the mirror of shirley_background's ascending
    # normalization — so both BE orderings give identical output.
    flipped = bool(xa[0] < xa[-1])
    if flipped:
        xa, ya = xa[::-1].copy(), ya[::-1].copy()

    # C0: the low-BE edge level = index -1 on the descending working array.
    # This is the out-of-window (pre-loss) baseline; the kernel integral is
    # run on the net above it.
    c0 = float(ya[-1])
    net = ya - c0

    dx = float(abs(xa[1] - xa[0]))

    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·net[j]·w[j],  K(T) = B·T / (C + T²)²,
    # w[j] = the local quadrature weight (energy spacing) at point j.
    #
    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx and w[j] == dx, so the
    # kernel depends only on the index gap and this one-sided correlation
    # collapses to a convolution against a single precomputed kernel vector —
    # evaluated in C via np.convolve instead of an n-iteration Python loop
    # (audit F7). On a NONUNIFORM grid neither identity holds, so we keep the
    # exact per-point separation loop AND per-point weights (audit F2,
    # 2026-07-17: the loop previously used exact separations but omitted the
    # spacing weights, silently applying a uniform-grid quadrature inside the
    # branch written precisely because the grid is not uniform — up to ~24%
    # error on a genuinely nonuniform grid). np.gradient returns dx exactly
    # on a uniform grid, so both branches agree to floating point and the
    # uniformity test is a pure optimization, not a semantic fork.

codex
There are two additional `_compute_background` call sites outside `autofit/engine.py` (`sparse_map.py` and `bayesian_exchange_mc.py`). They still call the new defaulted signature, so current behavior stays unchanged, but the “3 real call sites” statement is only true if scoped strictly to `autofit/engine.py`.
exec
/bin/zsh -lc "sed -n '620,700p' fitting.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    # uniformity test is a pure optimization, not a semantic fork.
    diffs = np.diff(xa)
    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)

    if uniform:
        m = np.arange(n, dtype=float)
        T = m * dx
        k = (B_coef * T) / (C_coef + T * T) ** 2          # k[m] = K(m·dx)
        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·net[i+m]  =  conv(net, reverse(k))[n-1+i]
        bg = np.convolve(net, k[::-1])[n - 1:] * dx
    else:
        w = np.abs(np.gradient(xa))
        bg = np.zeros(n)
        for i in range(n):
            T = np.abs(xa[i:] - xa[i])
            kernel = (B_coef * T) / (C_coef + T * T) ** 2
            bg[i] = float(np.sum(kernel * net[i:] * w[i:]))

    # Amplitude anchor: scale the loss integral so the background equals the
    # measured intensity at the HIGH-BE edge (index 0 on the descending
    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
    # flat or empty window), the honest background is the flat pre-loss level
    # C0 itself, NOT zeros: a featureless window contains no loss signal to
    # model, and returning zeros would report the entire baseline as net
    # signal (the pre-F1 behaviour). Negative counts (physically invalid
    # input) pass through signed; no clamping policy is imposed here.
    if bg[0] == 0.0:
        out = np.full(n, c0)
    else:
        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])
    return out[::-1] if flipped else out


def _la_casaxps_true(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    alpha: float,
    beta: float,
    m: float,
) -> np.ndarray:
    """
    True CasaXPS LA(α, β, m) lineshape.

    Built in two steps per the CasaXPS LA manual:

    1.  Asymmetric base Lorentzian. Start with a unit-amplitude Lorentzian
        of FWHM `fwhm` centered at `center`:
            L(x) = 1 / (1 + 4·((x − center)/fwhm)²)
        Apply piecewise exponents to introduce asymmetry. CasaXPS defines
        these on a kinetic-energy axis. We use a binding-energy axis, so
        the sides flip:
            LA_base(x) = L(x)^α   for x ≥ center  (high-BE side)
            LA_base(x) = L(x)^β   for x <  center  (low-BE side)
        Increasing α relative to β SUPPRESSES the high-BE tail; decreasing
        α extends it.

    2.  Gaussian convolution with an integer-point kernel of width `m`.
        m=0 means no convolution. For m>0, build a discrete Gaussian
        kernel of length 2m+1 with σ_pts = m/3 (so the 3σ tail just
        reaches the kernel edge). Convolve with mode='same' on the
        uniform x grid.

    With α=β=1 and m=0, this reduces exactly to amplitude × L(x) (a pure
    Lorentzian of peak height = amplitude, FWHM = `fwhm`).

    Parameters
    ----------
    fwhm  : Lorentzian FWHM in eV (must be > 0)
    alpha : high-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    beta  : low-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    m     : Gaussian convolution kernel width in DATA POINTS (not eV);
            integer 0–499. Stored as float in lmfit, rounded to int here.
    """
    fwhm = max(float(fwhm), 1e-9)
    alpha = max(float(alpha), 1e-3)
    beta = max(float(beta), 1e-3)
    # Continuous-σ kernel: m flows through to the kernel weights as a real
    # number, so the Jacobian column for m is well-defined under lmfit's

codex
Because full imports are blocked by missing dependencies, I’m extracting just the relevant function definitions from `fitting.py` with `ast` and executing them in a tiny namespace. That avoids changing files and is enough to measure whether the noisy endpoint fixture actually exercises the implementation.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'exec(\"\"\"
import ast, numpy as np
from typing import Any
src=open(\"fitting.py\").read()
mod=ast.parse(src)
keep={\"_apply_endpoint_averaging\",\"shirley_background\",\"smart_background\",\"linear_background\",\"smart_experimental_background\",\"tougaard_background\",\"compute_background_only\"}
ns={\"np\":np,\"Any\":Any}
for node in mod.body:
    if isinstance(node, ast.FunctionDef) and node.name in keep:
        code=compile(ast.Module(body=[node], type_ignores=[]), \"fitting.py\", \"exec\")
        exec(code, ns)
x=np.linspace(700.0,740.0,200)
y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2)
y=y.copy(); y[0]+=500.0; y[-1]-=500.0
for name in [\"shirley_background\",\"smart_background\",\"smart_experimental_background\",\"tougaard_background\"]:
    fn=ns[name]; raw=fn(x,y,n_avg=1); avg=fn(x,y,n_avg=8); d=avg-raw
    print(name, \"allclose?\", np.allclose(raw,avg), \"max_abs_diff\", float(np.max(np.abs(d))), \"first/raw_avg\", float(raw[0]), float(avg[0]), \"last/raw_avg\", float(raw[-1]), float(avg[-1]))
old_smart=ns[\"smart_background\"](x,ns[\"_apply_endpoint_averaging\"](y,8))
new_smart=ns[\"smart_background\"](x,y,n_avg=8)
print(\"smart old_preavg_vs_new_direct array_equal\", np.array_equal(old_smart,new_smart), \"allclose\", np.allclose(old_smart,new_smart), \"max_abs_diff\", float(np.max(np.abs(old_smart-new_smart))))
print(\"old_new endpoints\", float(old_smart[0]), float(new_smart[0]), float(old_smart[-1]), float(new_smart[-1]))
manual=ns[\"compute_background_only\"](x,y,method=\"smart\",endpoint_avg=8)[\"background\"]
engine=ns[\"smart_background\"](x,y,n_avg=8)
print(\"compute_background_only smart vs engine direct array_equal\", np.array_equal(manual,engine), \"allclose\", np.allclose(manual,engine), \"max_abs_diff\", float(np.max(np.abs(manual-engine))))
\"\"\")'" in /Users/skyefortier/xps-verify
 exited 1 in 114ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<string>", line 11, in <module>
  File "fitting.py", line 1278, in <module>
    start_idx: int | None = None,
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'

codex
The system Python is old enough that the repo’s `int | None` annotations fail unless the module-level future import is present. I’m stripping annotations in the extracted-function probe so the runtime behavior can still be measured.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'exec(\"\"\"
import ast, numpy as np
from typing import Any
src=open(\"fitting.py\").read(); mod=ast.parse(src)
keep={\"_apply_endpoint_averaging\",\"shirley_background\",\"smart_background\",\"linear_background\",\"smart_experimental_background\",\"tougaard_background\",\"compute_background_only\"}
class StripAnn(ast.NodeTransformer):
    def visit_FunctionDef(self,node):
        node.returns=None
        for a in list(node.args.args)+list(node.args.kwonlyargs): a.annotation=None
        if node.args.vararg: node.args.vararg.annotation=None
        if node.args.kwarg: node.args.kwarg.annotation=None
        return node
ns={\"np\":np,\"Any\":Any}
for node in mod.body:
    if isinstance(node, ast.FunctionDef) and node.name in keep:
        node=StripAnn().visit(node); ast.fix_missing_locations(node)
        exec(compile(ast.Module(body=[node], type_ignores=[]), \"fitting.py\", \"exec\"), ns)
x=np.linspace(700.0,740.0,200)
y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2)
y=y.copy(); y[0]+=500.0; y[-1]-=500.0
for name in [\"shirley_background\",\"smart_background\",\"smart_experimental_background\",\"tougaard_background\"]:
    fn=ns[name]; raw=fn(x,y,n_avg=1); avg=fn(x,y,n_avg=8); d=avg-raw
    print(name, \"allclose?\", np.allclose(raw,avg), \"max_abs_diff\", float(np.max(np.abs(d))), \"first/raw_avg\", float(raw[0]), float(avg[0]), \"last/raw_avg\", float(raw[-1]), float(avg[-1]))
old_smart=ns[\"smart_background\"](x,ns[\"_apply_endpoint_averaging\"](y,8))
new_smart=ns[\"smart_background\"](x,y,n_avg=8)
print(\"smart old_preavg_vs_new_direct array_equal\", np.array_equal(old_smart,new_smart), \"allclose\", np.allclose(old_smart,new_smart), \"max_abs_diff\", float(np.max(np.abs(old_smart-new_smart))))
print(\"old_new endpoints\", float(old_smart[0]), float(new_smart[0]), float(old_smart[-1]), float(new_smart[-1]))
manual=ns[\"compute_background_only\"](x,y,method=\"smart\",endpoint_avg=8)[\"background\"]
engine=ns[\"smart_background\"](x,y,n_avg=8)
print(\"compute_background_only smart vs engine direct array_equal\", np.array_equal(manual,engine), \"allclose\", np.allclose(manual,engine), \"max_abs_diff\", float(np.max(np.abs(manual-engine))))
\"\"\")'" in /Users/skyefortier/xps-verify
 succeeded in 126ms:
shirley_background allclose? False max_abs_diff 440.075897556163 first/raw_avg 4500.011179959516 4062.5305802339585 last/raw_avg 3500.011179959516 3937.5305802339585
smart_background allclose? False max_abs_diff 440.075897556163 first/raw_avg 4500.011179959516 4062.5305802339585 last/raw_avg 3500.011179959516 3500.011179959516
smart_experimental_background allclose? False max_abs_diff 440.24684064952726 first/raw_avg 4500.011179959516 4062.5305802339585 last/raw_avg 3500.011179959516 3500.011179959516
tougaard_background allclose? False max_abs_diff 698.6998781124239 first/raw_avg 4500.011179959516 4062.5305802339585 last/raw_avg 3500.011179959516 3937.5305802339585
smart old_preavg_vs_new_direct array_equal False allclose False max_abs_diff 437.51940027444243
old_new endpoints 4062.5305802339585 4062.5305802339585 3937.5305802339585 3500.011179959516
compute_background_only smart vs engine direct array_equal False allclose False max_abs_diff 437.51940027444243

codex
The noisy endpoint fixture is not laundered: the extracted probe shows `n_avg=8` changes Shirley by about `440` counts and Tougaard by about `699` counts, so `not np.allclose(...)` has real signal. It also exposes a SMART inconsistency between the new direct API and the existing manual background path.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'exec(\"\"\"
import ast, numpy as np
from enum import Enum
src=open(\"fitting.py\").read(); mod=ast.parse(src)
keep={\"_apply_endpoint_averaging\",\"shirley_background\",\"smart_background\",\"linear_background\",\"smart_experimental_background\",\"tougaard_background\"}
class StripAnn(ast.NodeTransformer):
    def visit_FunctionDef(self,node):
        node.returns=None
        for a in list(node.args.args)+list(node.args.kwonlyargs): a.annotation=None
        return node
ns={\"np\":np}
for node in mod.body:
    if isinstance(node, ast.FunctionDef) and node.name in keep:
        node=StripAnn().visit(node); ast.fix_missing_locations(node); exec(compile(ast.Module(body=[node], type_ignores=[]), \"fitting.py\", \"exec\"), ns)
apply_avg=ns[\"_apply_endpoint_averaging\"]; shirley=ns[\"shirley_background\"]; smart=ns[\"smart_background\"]; smart_exp=ns[\"smart_experimental_background\"]; tougaard=ns[\"tougaard_background\"]; linear=ns[\"linear_background\"]
x=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500; y[-1]-=500
# Defeat 1: shirley accepts n_avg but ignores it.
def shirley_ignored(x,y,n_iter=200,tol=1e-6,n_avg=1): return shirley(x,y,n_iter,tol,n_avg=1)
raw=shirley_ignored(x,y,n_avg=1); avg=shirley_ignored(x,y,n_avg=8); pre=shirley_ignored(x,apply_avg(y,8))
print(\"defeat_shirley_ignore: change_test_fails\", np.allclose(raw,avg), \"external_preavg_test_fails\", not np.array_equal(avg,pre), \"max_direct_pre_diff\", float(np.max(np.abs(avg-pre))))
# Defeat 2: smart accepts n_avg but drops it when calling Shirley.
def smart_drops(x,y,n_iter=200,tol=1e-6,n_avg=1): return np.minimum(shirley(x,y,n_iter,tol,n_avg=1), y)
raw=smart_drops(x,y,n_avg=1); avg=smart_drops(x,y,n_avg=8); expected=np.minimum(shirley(x,y,n_avg=8), y)
print(\"defeat_smart_drop_forward: change_test_fails\", np.allclose(raw,avg), \"forward_test_fails\", not np.array_equal(avg,expected), \"max_expected_diff\", float(np.max(np.abs(avg-expected))))
# Defeat 3: _compute_background accepts endpoint_avg but drops it.
class BackgroundType(Enum): SHIRLEY=\"shirley\"; SMART=\"smart\"; SMART_EXP=\"smart_exp\"; LINEAR=\"linear\"; TOUGAARD=\"tougaard\"
def compute_drop(x,y,bg,endpoint_avg=1):
    if bg is BackgroundType.SHIRLEY: return shirley(x,y)
    if bg is BackgroundType.SMART: return smart(x,y)
    if bg is BackgroundType.SMART_EXP: return smart_exp(x,y)
    if bg is BackgroundType.LINEAR: return linear(x,y)
    if bg is BackgroundType.TOUGAARD: return tougaard(x,y)
for bg,fn in [(BackgroundType.SHIRLEY,shirley),(BackgroundType.SMART,smart),(BackgroundType.SMART_EXP,smart_exp),(BackgroundType.TOUGAARD,tougaard)]:
    for n in (1,4,8):
        via=compute_drop(x,y,bg,endpoint_avg=n); direct=fn(x,y,n_avg=n)
        print(\"defeat_compute_drop\", bg.name, \"n\", n, \"test_fails\", not np.array_equal(via,direct), \"max_diff\", float(np.max(np.abs(via-direct))))
\"\"\")'" in /Users/skyefortier/xps-verify
 succeeded in 149ms:
defeat_shirley_ignore: change_test_fails True external_preavg_test_fails True max_direct_pre_diff 440.075897556163
defeat_smart_drop_forward: change_test_fails True forward_test_fails True max_expected_diff 440.075897556163
defeat_compute_drop SHIRLEY n 1 test_fails False max_diff 0.0
defeat_compute_drop SHIRLEY n 4 test_fails True max_diff 378.93845192245317
defeat_compute_drop SHIRLEY n 8 test_fails True max_diff 440.075897556163
defeat_compute_drop SMART n 1 test_fails False max_diff 0.0
defeat_compute_drop SMART n 4 test_fails True max_diff 378.93845192245317
defeat_compute_drop SMART n 8 test_fails True max_diff 440.075897556163
defeat_compute_drop SMART_EXP n 1 test_fails False max_diff 0.0
defeat_compute_drop SMART_EXP n 4 test_fails True max_diff 379.23413489938866
defeat_compute_drop SMART_EXP n 8 test_fails True max_diff 440.24684064952726
defeat_compute_drop TOUGAARD n 1 test_fails False max_diff 0.0
defeat_compute_drop TOUGAARD n 4 test_fails True max_diff 634.0011258789418
defeat_compute_drop TOUGAARD n 8 test_fails True max_diff 698.6998781124239

codex
1. MAJOR [fitting.py](/Users/skyefortier/xps-verify/fitting.py:400), [fitting.py](/Users/skyefortier/xps-verify/fitting.py:1052), [fitting.py](/Users/skyefortier/xps-verify/fitting.py:1290): `smart_background(..., n_avg=N)` now clamps against raw `y`, but the manual `run_fit` / `compute_background_only` paths still pre-average `y` before calling `smart_background`, so they clamp against the averaged copy. For the test fixture with `endpoint_avg=8`, direct/engine SMART and manual SMART differ by `437.5` counts. That means once Find Peaks passes `endpoint_avg`, SMART backgrounds will not match manual Run Fit for the same knob value, contradicting the stated wiring goal and the test docstring claim.

Notes from verification: `_apply_endpoint_averaging` is byte-identical after relocation; the diff is limited to `fitting.py`, `autofit/engine.py`, and `tests/test_background_n_avg.py`; `app.py` defaults are `1`; the 3 `_compute_background` call sites inside `autofit/engine.py` do not pass `endpoint_avg`. There are also 2 real `_compute_background` call sites outside `engine.py`, both still using the default. I could not run pytest because `pytest` and `lmfit` are missing, but extracted-function probes confirm the noisy endpoint tests are not laundered and the forwarding tests go red for dropped `n_avg` at `n_avg=4/8`.

VERDICT: NO-GO
tokens used
65,122
1. MAJOR [fitting.py](/Users/skyefortier/xps-verify/fitting.py:400), [fitting.py](/Users/skyefortier/xps-verify/fitting.py:1052), [fitting.py](/Users/skyefortier/xps-verify/fitting.py:1290): `smart_background(..., n_avg=N)` now clamps against raw `y`, but the manual `run_fit` / `compute_background_only` paths still pre-average `y` before calling `smart_background`, so they clamp against the averaged copy. For the test fixture with `endpoint_avg=8`, direct/engine SMART and manual SMART differ by `437.5` counts. That means once Find Peaks passes `endpoint_avg`, SMART backgrounds will not match manual Run Fit for the same knob value, contradicting the stated wiring goal and the test docstring claim.

Notes from verification: `_apply_endpoint_averaging` is byte-identical after relocation; the diff is limited to `fitting.py`, `autofit/engine.py`, and `tests/test_background_n_avg.py`; `app.py` defaults are `1`; the 3 `_compute_background` call sites inside `autofit/engine.py` do not pass `endpoint_avg`. There are also 2 real `_compute_background` call sites outside `engine.py`, both still using the default. I could not run pytest because `pytest` and `lmfit` are missing, but extracted-function probes confirm the noisy endpoint tests are not laundered and the forwarding tests go red for dropped `n_avg` at `n_avg=4/8`.

VERDICT: NO-GO
