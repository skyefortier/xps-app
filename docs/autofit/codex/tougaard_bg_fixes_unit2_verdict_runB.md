OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f7233-3f3b-76c0-b67e-565d55432922
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
I’ll inspect the commit diff and nearby call sites first, then run the focused tests if the environment allows it. I’ll also probe the “red” cases without editing the worktree, since this sandbox is read-only.
exec
/bin/zsh -lc "rg -n \"_compute_background\\(|endpoint_avg|def (shirley_background|smart_background|linear_background|smart_experimental_background|tougaard_background)|_apply_endpoint_averaging\" app.py fitting.py autofit/engine.py tests/test_background_n_avg.py autofit/methods templates/index.html" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/test_background_n_avg.py:4:autofit/engine.py's _compute_background must forward an endpoint_avg knob to
tests/test_background_n_avg.py:15:    _apply_endpoint_averaging,
tests/test_background_n_avg.py:58:    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
tests/test_background_n_avg.py:63:        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
tests/test_background_n_avg.py:91:def test_apply_endpoint_averaging_still_importable_and_unchanged():
tests/test_background_n_avg.py:92:    """F3 relocates _apply_endpoint_averaging above shirley_background in
tests/test_background_n_avg.py:95:    out = _apply_endpoint_averaging(y, 2)
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
autofit/engine.py:287:def _compute_background(
autofit/engine.py:291:    endpoint_avg: int = 1,
autofit/engine.py:295:    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
autofit/engine.py:298:    _apply_endpoint_averaging — which is exactly what this function forgot
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
fitting.py:337:    array themselves via _apply_endpoint_averaging; that convention was
fitting.py:352:        y = _apply_endpoint_averaging(np.asarray(y, dtype=float), n_avg)
fitting.py:384:def smart_background(
fitting.py:404:def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
fitting.py:410:def smart_experimental_background(
fitting.py:528:def tougaard_background(
fitting.py:563:    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
fitting.py:586:        ya = _apply_endpoint_averaging(ya, n_avg)
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
templates/index.html:4322:    // do tougaard_background(x, _apply_endpoint_averaging(y, n)).
templates/index.html:6675:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvg };
templates/index.html:6783:    const bgPayload = { method: bgType, start_idx: bgStartIdx, end_idx: bgEndIdx, endpoint_avg: epAvgVal };
app.py:716:        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
app.py:718:            ep_avg = max(1, int(body.get("endpoint_avg", 1)))
app.py:720:            return _err("endpoint_avg must be an integer")
app.py:726:                endpoint_avg=ep_avg,
app.py:792:        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
app.py:794:            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
app.py:796:            return _err("endpoint_avg must be an integer")
app.py:839:                endpoint_avg=endpoint_avg,
autofit/methods/sparse_map.py:198:        bg = _compute_background(x, y, grammar.candidates[0].background)
autofit/methods/least_squares.py:21:    "background_method", "bg_start_idx", "bg_end_idx", "endpoint_avg",
autofit/methods/least_squares.py:57:            endpoint_avg=opts.pop("endpoint_avg", 1),
autofit/methods/bayesian_exchange_mc.py:348:            bg = _compute_background(x, y, model.background)

exec
/bin/zsh -lc 'git show --stat --oneline --decorate --name-status c5a24ac' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-WpmVsHUo' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5Fz0wj91' (errno=Operation not permitted)
c5a24ac feat(fitting): unify n_avg convention across background functions (F3)
M	autofit/engine.py
M	fitting.py
A	tests/test_background_n_avg.py

exec
/bin/zsh -lc 'git show --find-renames --find-copies --color=never c5a24ac -- fitting.py autofit/engine.py tests/test_background_n_avg.py app.py templates/index.html autofit/methods' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Gq15LDCw' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RCj6hGWe' (errno=Operation not permitted)
commit c5a24acaba52c645861e54daf5412d6e0ace5709
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Fri Jul 17 16:27:58 2026 -0600

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

codex
The diff is contained to `fitting.py`, `autofit/engine.py`, and the new test file; `git show` reports no changes to templates, methods, or app. I did notice `_compute_background` is referenced by method modules too, so I’m checking whether those are just indirect existing users or relevant to the “3 real call sites” claim.
exec
/bin/zsh -lc 'pytest -q tests/test_background_n_avg.py' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: pytest

exec
/bin/zsh -lc 'git diff --color=never c5a24ac''^ c5a24ac --stat -- app.py templates/index.html '"'autofit/methods/*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CSu2KJKy' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UMh7VS0B' (errno=Operation not permitted)

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '320,410p' && nl -ba autofit/engine.py | sed -n '284,318p;850,872p;2174,2188p;2584,2598p' && nl -ba autofit/methods/sparse_map.py | sed -n '190,203p' && nl -ba autofit/methods/bayesian_exchange_mc.py | sed -n '342,352p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
   850	    (200000*(nvars+1), see lmfit.Minimizer) is effectively unbounded: a
   851	    candidate whose params wander to a valid-but-degenerate corner (e.g.
   852	    DS+G's alpha/beta pinned at their bounds — a shape preference, not a
   853	    param error; see _BOUNDARY_EXCLUDED) produces a landscape leastsq can't
   854	    descend, and it spins for tens of thousands of evaluations without
   855	    terminating. Diagnostic run (2026-07-05, Suggest-peaks hang
   856	    investigation) showed a clean bimodal split: converged fits topped out
   857	    at nfev=14890; non-convergent ones started at nfev=21604. This cap sits
   858	    between the two so lmfit's own AbortFitException (caught internally by
   859	    leastsq(), surfacing as result.success=False) cuts off the latter
   860	    deterministically, without clipping legitimate slow-but-converging fits.
   861	    """
   862	    x = np.asarray(x, dtype=float)
   863	    y = np.asarray(y, dtype=float)
   864	    weights = np.asarray(weights, dtype=float)
   865	
   866	    bg = _compute_background(x, y, model.background)
   867	    y_sub = y - bg
   868	    composite = _build_composite_model(model)
   869	    params = initial_params if initial_params is not None else \
   870	        _default_params_from_slots(model, x=x, y_net=y_sub,
   871	                                   fit_full_window=fit_full_window)
   872	
  2174	    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
  2175	    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
  2176	    # caller passes budget_remaining = min(pass budget, sweep budget) left.
  2177	    if budget_remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
  2178	        return _fast(
  2179	            f"insufficient_budget: {budget_remaining:.1f}s left < "
  2180	            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")
  2181	
  2182	    bg = _compute_background(x, y, aug_model.background)
  2183	    try:
  2184	        init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
  2185	                                             fit_full_window=fit_full_window)
  2186	    except Exception as exc:
  2187	        return _fast(f"init_params_error: {exc}")
  2188	
  2584	        # A future mixed-background grammar only affects DETECTION here —
  2585	        # each candidate still fits with its own background.  Structural-
  2586	        # fallback regions (ZERO grammar candidates — the across-the-
  2587	        # periodic-table path) default to Shirley, the standard core-level
  2588	        # background (CLAUDE.md convention).
  2589	        det_bg_family = (candidates[0].background if candidates
  2590	                         else BackgroundType.SHIRLEY)
  2591	        det_bg = _compute_background(x, y, det_bg_family)
  2592	        preseed_specs = detect_out_of_grammar_dominants(
  2593	            x, y, det_bg, candidates, diagnostic_windows,
  2594	            noise_floor=noise_floor,
  2595	        )
  2596	        # Candidate-generation layer (autofit.candidates): overcomplete,
  2597	        # provenance-tagged pool.  The reviewed dominant channel above is
  2598	        # UNCHANGED; the pool's CWT curvature channel adds seeds the
   190	        if unknown:
   191	            raise ValueError(f"unknown sparse_map options: {sorted(unknown)}")
   192	        cfg = {k: type(DEFAULTS[k])(opts.pop(k, DEFAULTS[k])) for k in DEFAULTS}
   193	        lambda_fixed = opts.pop("lambda_fixed", None)
   194	
   195	        x = np.asarray(x, dtype=float)
   196	        y = np.asarray(y, dtype=float)
   197	
   198	        bg = _compute_background(x, y, grammar.candidates[0].background)
   199	        y_net = y - bg
   200	        n = len(y_net)
   201	
   202	        A, atoms, norms, unexpressible = _build_dictionary(
   203	            x, grammar, cfg["n_widths"])
   342	        if seed_replicates < 1:
   343	            raise ValueError("seed_replicates must be >= 1")
   344	
   345	        per_candidate: list[dict] = []
   346	        runs: dict[str, dict] = {}
   347	        for model in candidates:
   348	            bg = _compute_background(x, y, model.background)
   349	            y_net = y - bg
   350	            try:
   351	                space = _param_space(model, x, y_net)
   352	                run = run_exchange_mc(x, y_net, space, weights=weights, **mc_kwargs)

exec
/bin/zsh -lc 'git show c5a24ac''^:fitting.py | sed -n '"'420,445p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BB2yI4Ev' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-P7c2wl76' (errno=Operation not permitted)
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



exec
/bin/zsh -lc "git show c5a24ac:fitting.py | sed -n '300,318p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sn6IHvzm' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Duvapohy' (errno=Operation not permitted)


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


codex
`pytest` is not on PATH, so I’m trying module invocation next. The relocation body is byte-identical by direct `git show` extraction, and the new `n_avg` path is guarded by `if n_avg > 1`, which supports the byte-identical no-op claim for `n_avg=1`.
exec
/bin/zsh -lc 'python -m pytest -q tests/test_background_n_avg.py' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

codex
The local Python has no `pytest` module, so I can’t run the test suite here. I’m switching to small `python3 -c` probes with bytecode writes disabled to quantify the fixtures and simulate the failure modes.
exec
/bin/zsh -lc "nl -ba tests/test_background_n_avg.py | sed -n '1,160p'" in /Users/skyefortier/xps-verify
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

exec
/bin/zsh -lc "git show --color=never c5a24ac -- tests/test_background_n_avg.py | nl -ba | sed -n '1,180p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BbeGT7EJ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-shCWYtmb' (errno=Operation not permitted)
     1	commit c5a24acaba52c645861e54daf5412d6e0ace5709
     2	Author: Skye Fortier <skyefortier@gmail.com>
     3	Date:   Fri Jul 17 16:27:58 2026 -0600
     4	
     5	    feat(fitting): unify n_avg convention across background functions (F3)
     6	    
     7	    shirley_background and smart_background now take n_avg directly, matching
     8	    the convention already used by smart_experimental_background /
     9	    shirley_linear_background. The old convention — callers pre-average the
    10	    array via _apply_endpoint_averaging before calling — was easy to forget,
    11	    and autofit/engine.py did forget it: Find Peaks had no way to express an
    12	    endpoint_avg the manual /api/fit path honours. _apply_endpoint_averaging
    13	    is relocated above shirley_background (its first consumer in source
    14	    order); its own behavior is unchanged.
    15	    
    16	    autofit/engine.py's _compute_background gains an endpoint_avg param,
    17	    default 1 — matching both its previous behaviour and app.py's own default
    18	    (app.py:718,794), so this is pure wiring and changes no current output at
    19	    any of its 3 real call sites (none of which pass endpoint_avg today).
    20	    Forwards to shirley/smart/smart_exp/tougaard as n_avg=endpoint_avg;
    21	    linear_background has no endpoint-averaging concept and ignores it.
    22	    
    23	    Originally F3 of a larger sandboxed patch (see Unit 1, commits 3d9ff54 /
    24	    173f002, for F1+F2). Deliberately held as its own unit: F1/F2 live inside
    25	    tougaard_background's own body and were inseparable from each other, but
    26	    F3 is naturally independent code, sequenced after Unit 1 only because
    27	    _compute_background's tougaard_background call needed the 3-arg signature
    28	    to already exist.
    29	    
    30	    The original patch shipped ZERO tests for this behavior change. Added
    31	    tests/test_background_n_avg.py (13 tests) first: confirmed n_avg=1 (the
    32	    default) reproduces pre-F3 output byte-for-byte on both shirley_background
    33	    and _compute_background for every background type; confirmed n_avg>1
    34	    actually changes output on a fixture with a deliberate single-point
    35	    endpoint outlier; confirmed shirley_background(x,y,n_avg=N) equals the old
    36	    external-pre-averaging call exactly (pure convenience wrapper, not a new
    37	    algorithm); confirmed smart_background clamps against raw data, not the
    38	    averaged copy; confirmed _compute_background(...,endpoint_avg=N) matches
    39	    calling the underlying fitting.py function directly. Red confirmed first:
    40	    12/13 failed with TypeError on the missing kwargs before implementation;
    41	    green after.
    42	    
    43	    Full suite: 679 passed, 6 skipped, 0 failed (679 = Unit 1's 666 + these 13
    44	    new tests). Scope: fitting.py, autofit/engine.py, and the one new test
    45	    file — zero changes to /api/fit's contract, autofit/methods/*.py, peak
    46	    lineshapes, or templates/index.html (this is a Python-only Find-Peaks-vs-
    47	    manual-fit wiring gap; no JS-side equivalent exists to fix).
    48	    
    49	    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
    50	
    51	diff --git a/tests/test_background_n_avg.py b/tests/test_background_n_avg.py
    52	new file mode 100644
    53	index 0000000..9a4cbca
    54	--- /dev/null
    55	+++ b/tests/test_background_n_avg.py
    56	@@ -0,0 +1,145 @@
    57	+"""F3 regression tests (2026-07-17 background audit): shirley_background and
    58	+smart_background must accept n_avg directly, matching the convention already
    59	+used by smart_experimental_background / shirley_linear_background, and
    60	+autofit/engine.py's _compute_background must forward an endpoint_avg knob to
    61	+every background type it dispatches.
    62	+
    63	+The original sandboxed patch that introduced this wiring shipped with no
    64	+tests at all for it -- these are net-new coverage, not a port of anything
    65	+upstream.
    66	+"""
    67	+import numpy as np
    68	+import pytest
    69	+
    70	+from fitting import (
    71	+    _apply_endpoint_averaging,
    72	+    shirley_background,
    73	+    smart_background,
    74	+    smart_experimental_background,
    75	+    tougaard_background,
    76	+)
    77	+
    78	+
    79	+def _noisy_endpoint_fixture():
    80	+    """A spectrum whose single first/last SAMPLE is a noise outlier relative
    81	+    to its neighborhood, so endpoint averaging visibly changes the reported
    82	+    B_low/B_high and therefore the whole background curve."""
    83	+    rng = np.random.default_rng(0)
    84	+    x = np.linspace(700.0, 740.0, 200)
    85	+    y = 4000.0 + 3000.0 * np.exp(-0.5 * ((x - 720.0) / 4.0) ** 2)
    86	+    y = y.copy()
    87	+    y[0] += 500.0    # single-point low-BE outlier
    88	+    y[-1] -= 500.0   # single-point high-BE outlier
    89	+    return x, y
    90	+
    91	+
    92	+def test_shirley_background_default_n_avg_matches_pre_f3_output():
    93	+    """n_avg=1 (the default) must reproduce the pre-F3 raw-endpoint
    94	+    behaviour byte-for-byte -- this wiring must change no current output."""
    95	+    x, y = _noisy_endpoint_fixture()
    96	+    assert np.array_equal(shirley_background(x, y), shirley_background(x, y, n_avg=1))
    97	+
    98	+
    99	+def test_shirley_background_n_avg_changes_output_on_noisy_endpoints():
   100	+    """n_avg > 1 must actually average the endpoints internally and change
   101	+    the result relative to raw endpoints, on a fixture designed so that
   102	+    difference is visible."""
   103	+    x, y = _noisy_endpoint_fixture()
   104	+    raw = shirley_background(x, y, n_avg=1)
   105	+    averaged = shirley_background(x, y, n_avg=8)
   106	+    assert not np.allclose(raw, averaged), (
   107	+        "n_avg=8 produced the same background as n_avg=1 on a fixture with "
   108	+        "a deliberate single-point endpoint outlier"
   109	+    )
   110	+
   111	+
   112	+def test_shirley_background_n_avg_matches_external_pre_averaging():
   113	+    """Calling shirley_background(x, y, n_avg=N) must equal the OLD calling
   114	+    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
   115	+    so this is a pure convenience wrapper, not a new averaging algorithm."""
   116	+    x, y = _noisy_endpoint_fixture()
   117	+    for n_avg in (1, 4, 8):
   118	+        direct = shirley_background(x, y, n_avg=n_avg)
   119	+        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
   120	+        assert np.array_equal(direct, pre_averaged), f"mismatch at n_avg={n_avg}"
   121	+
   122	+
   123	+def test_smart_background_default_n_avg_matches_pre_f3_output():
   124	+    x, y = _noisy_endpoint_fixture()
   125	+    assert np.array_equal(smart_background(x, y), smart_background(x, y, n_avg=1))
   126	+
   127	+
   128	+def test_smart_background_forwards_n_avg_to_shirley():
   129	+    """smart_background(x, y, n_avg=N) must equal
   130	+    minimum(shirley_background(x, y, n_avg=N), y) -- the clamp applies
   131	+    against the RAW data, not an endpoint-averaged copy, so averaging only
   132	+    ever moves the background curve, never the reported net counts."""
   133	+    x, y = _noisy_endpoint_fixture()
   134	+    for n_avg in (1, 4, 8):
   135	+        got = smart_background(x, y, n_avg=n_avg)
   136	+        expected = np.minimum(shirley_background(x, y, n_avg=n_avg), y)
   137	+        assert np.array_equal(got, expected), f"mismatch at n_avg={n_avg}"
   138	+
   139	+
   140	+def test_smart_background_n_avg_changes_output_on_noisy_endpoints():
   141	+    x, y = _noisy_endpoint_fixture()
   142	+    raw = smart_background(x, y, n_avg=1)
   143	+    averaged = smart_background(x, y, n_avg=8)
   144	+    assert not np.allclose(raw, averaged)
   145	+
   146	+
   147	+def test_apply_endpoint_averaging_still_importable_and_unchanged():
   148	+    """F3 relocates _apply_endpoint_averaging above shirley_background in
   149	+    fitting.py's source order; its behaviour must not change."""
   150	+    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
   151	+    out = _apply_endpoint_averaging(y, 2)
   152	+    assert np.array_equal(out, np.array([1.5, 1.5, 3.0, 4.0, 5.0, 6.0, 7.5, 7.5]))
   153	+
   154	+
   155	+def test_compute_background_default_endpoint_avg_matches_pre_f3_output():
   156	+    """autofit/engine.py's _compute_background(x, y, bg) with no
   157	+    endpoint_avg argument must reproduce pre-F3 output exactly, for every
   158	+    background type it dispatches -- pure wiring, no behaviour change."""
   159	+    from autofit.engine import BackgroundType, _compute_background
   160	+
   161	+    x, y = _noisy_endpoint_fixture()
   162	+    for bg_type in (BackgroundType.SHIRLEY, BackgroundType.SMART,
   163	+                    BackgroundType.SMART_EXP, BackgroundType.LINEAR,
   164	+                    BackgroundType.TOUGAARD):
   165	+        no_arg = _compute_background(x, y, bg_type)
   166	+        default_arg = _compute_background(x, y, bg_type, endpoint_avg=1)
   167	+        assert np.array_equal(no_arg, default_arg), f"mismatch for {bg_type}"
   168	+
   169	+
   170	+@pytest.mark.parametrize("bg_type_name,direct_fn", [
   171	+    ("SHIRLEY", shirley_background),
   172	+    ("SMART", smart_background),
   173	+    ("SMART_EXP", smart_experimental_background),
   174	+    ("TOUGAARD", tougaard_background),
   175	+])
   176	+def test_compute_background_forwards_endpoint_avg(bg_type_name, direct_fn):
   177	+    """_compute_background(x, y, bg, endpoint_avg=N) must match calling the
   178	+    underlying fitting.py function directly with n_avg=N -- Find Peaks and
   179	+    manual Run Fit must agree once both pass the same endpoint_avg."""
   180	+    from autofit.engine import BackgroundType, _compute_background

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import numpy as np; import fitting; from autofit.engine import BackgroundType,_compute_background; x=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.0; y[-1]-=500.0; print(\"ignored shirley vs external8 equal\", bool(np.array_equal(fitting.shirley_background(x,y,n_avg=1), fitting.shirley_background(x,fitting._apply_endpoint_averaging(y,8))))); print(\"ignored smart vs expected8 equal\", bool(np.array_equal(fitting.smart_background(x,y,n_avg=1), np.minimum(fitting.shirley_background(x,y,n_avg=8), y))));
for name,direct in [(\"SHIRLEY\",fitting.shirley_background),(\"SMART\",fitting.smart_background),(\"SMART_EXP\",fitting.smart_experimental_background),(\"TOUGAARD\",fitting.tougaard_background)]:
    bg=getattr(BackgroundType,name); drop=_compute_background(x,y,bg,endpoint_avg=1); direct8=direct(x,y,n_avg=8); print(\"engine drop\", name, \"equals direct8\", bool(np.array_equal(drop,direct8)), \"maxdiff\", float(np.max(np.abs(drop-direct8))))'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import numpy as np; from fitting import shirley_background, smart_background, _apply_endpoint_averaging, smart_experimental_background, tougaard_background; from autofit.engine import BackgroundType, _compute_background; x=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.0; y[-1]-=500.0; funcs=[(\"shirley\",shirley_background),(\"smart\",smart_background),(\"smart_exp\",smart_experimental_background),(\"tougaard\",tougaard_background)];
for name,fn in funcs:
    raw=fn(x,y,n_avg=1); avg4=fn(x,y,n_avg=4); avg8=fn(x,y,n_avg=8); print(name, \"maxdiff4\", float(np.max(np.abs(raw-avg4))), \"allclose4\", bool(np.allclose(raw,avg4)), \"maxdiff8\", float(np.max(np.abs(raw-avg8))), \"allclose8\", bool(np.allclose(raw,avg8)))
print(\"shirley ext eq\", bool(np.array_equal(shirley_background(x,y,n_avg=8), shirley_background(x,_apply_endpoint_averaging(y,8))))); print(\"smart expected eq\", bool(np.array_equal(smart_background(x,y,n_avg=8), np.minimum(shirley_background(x,y,n_avg=8), y)))); print(\"linear engine ep8 maxdiff\", float(np.max(np.abs(_compute_background(x,y,BackgroundType.LINEAR)-_compute_background(x,y,BackgroundType.LINEAR,endpoint_avg=8)))));
for bg in [BackgroundType.SHIRLEY,BackgroundType.SMART,BackgroundType.SMART_EXP,BackgroundType.LINEAR,BackgroundType.TOUGAARD]:
    print(\"engine default\", bg.name, bool(np.array_equal(_compute_background(x,y,bg), _compute_background(x,y,bg,endpoint_avg=1))))'" in /Users/skyefortier/xps-verify
 exited 1 in 150ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

 exited 1 in 150ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

codex
The probe can’t import app code because this environment lacks `lmfit`, so runtime verification is limited. I’ll still compute the core numeric behavior by extracting the relevant background functions into a standalone probe, which is enough to test whether the new fixture is laundered.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '410,610p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "rg --files -g 'pytest*' -g 'pyproject.toml' -g 'requirements*.txt' -g 'setup.cfg' -g 'tox.ini' -g '.venv/**' -g 'venv/**' -g 'uv.lock' -g 'poetry.lock'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
requirements-dev.txt
requirements.txt

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '940,1070p;1268,1302p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
  1063	        if x[i1 - 1] != x[i0]:
  1064	            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
  1065	        else:
  1066	            slope = 0.0
  1067	        bg = y[i0] + slope * (x - x[i0])
  1068	    elif bg_method in ("none", "flat", "", "manual"):
  1069	        bg = np.zeros_like(y)
  1070	    else:
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
  1299	    elif method in ("none", "flat", "", "manual"):
  1300	        bg = np.zeros_like(y)
  1301	    else:
  1302	        raise ValueError(f"Unknown background method '{method}'")

exec
/bin/zsh -lc 'git diff --color=never c5a24ac''^ c5a24ac -- fitting.py | sed -n '"'1,140p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-AB5vsBMK' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Dan9N8gU' (errno=Operation not permitted)
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

codex
Static review turned up an important distinction: the low-level `smart_background(x, y, n_avg=N)` intentionally clamps against raw `y`, but the existing manual fitting path still calls `smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))`, which clamps against the averaged copy. I’m checking whether that creates a real divergence rather than just a comment mismatch.
exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '1038,1060p;1286,1298p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
/bin/zsh -lc "nl -ba app.py | sed -n '710,730p;788,844p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c '
import numpy as np

def avg(y,n_avg):
    n=len(y)
    if n_avg<=1 or n<4: return y.copy()
    cap=min(n_avg,n//4)
    if cap<1: return y.copy()
    out=y.copy(); out[:cap]=np.mean(y[:cap]); out[-cap:]=np.mean(y[-cap:]); return out

def shirley(x,y,n_iter=200,tol=1e-6,n_avg=1):
    if len(x)<2: return np.zeros_like(y)
    if n_avg>1: y=avg(np.asarray(y,dtype=float),n_avg)
    if x[0]>x[-1]: xs,ys=x[::-1].copy(),y[::-1].copy(); flipped=True
    else: xs,ys=x.copy(),y.copy(); flipped=False
    b_low=ys[0]; b_high=ys[-1]; B=np.linspace(b_low,b_high,len(ys))
    for _ in range(n_iter):
        B_prev=B.copy(); signal=np.maximum(ys-B,0.0); cum_right=np.zeros(len(ys))
        for i in range(len(ys)-2,-1,-1): cum_right[i]=cum_right[i+1]+0.5*(signal[i]+signal[i+1])*(xs[i+1]-xs[i])
        total=cum_right[0]
        if total<=0.0: break
        B=b_high+(b_low-b_high)*cum_right/total
        if np.max(np.abs(B-B_prev))<tol: break
    return B[::-1] if flipped else B

def smart_new(x,y,n_avg=1):
    if len(x)<2: return np.zeros_like(y)
    return np.minimum(shirley(x,y,n_avg=n_avg), y)

def smart_old_manual(x,y,n_avg):
    ya=avg(y,n_avg)
    return np.minimum(shirley(x, ya), ya)

x=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.; y[-1]-=500.
for n in (4,8):
    a=smart_new(x,y,n_avg=n); b=smart_old_manual(x,y,n); print(n, \"maxdiff\", float(np.max(np.abs(a-b))), \"first\", float(a[0]-b[0]), \"last\", float(a[-1]-b[-1]), \"allclose\", bool(np.allclose(a,b)))
print(\"change new raw vs n1\", float(np.max(np.abs(smart_new(x,y,8)-smart_new(x,y,1)))), bool(np.allclose(smart_new(x,y,8),smart_new(x,y,1))))
'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c '
import numpy as np

def avg(y,n_avg):
    n=len(y)
    if n_avg<=1 or n<4: return y.copy()
    cap=min(n_avg,n//4)
    if cap<1: return y.copy()
    out=y.copy(); out[:cap]=np.mean(y[:cap]); out[-cap:]=np.mean(y[-cap:]); return out

def shirley(x,y,n_iter=200,tol=1e-6,n_avg=1):
    if len(x)<2: return np.zeros_like(y)
    if n_avg>1: y=avg(np.asarray(y,dtype=float),n_avg)
    if x[0]>x[-1]: xs,ys=x[::-1].copy(),y[::-1].copy(); flipped=True
    else: xs,ys=x.copy(),y.copy(); flipped=False
    b_low=ys[0]; b_high=ys[-1]; B=np.linspace(b_low,b_high,len(ys))
    for _ in range(n_iter):
        B_prev=B.copy(); signal=np.maximum(ys-B,0.0); cum_right=np.zeros(len(ys))
        for i in range(len(ys)-2,-1,-1): cum_right[i]=cum_right[i+1]+0.5*(signal[i]+signal[i+1])*(xs[i+1]-xs[i])
        total=cum_right[0]
        if total<=0.0: break
        B=b_high+(b_low-b_high)*cum_right/total
        if np.max(np.abs(B-B_prev))<tol: break
    return B[::-1] if flipped else B

def smart(x,y,n_avg=1): return np.minimum(shirley(x,y,n_avg=n_avg), y) if len(x)>=2 else np.zeros_like(y)
def smart_exp(x,y,n_iter=200,tol=1e-6,n_avg=1):
    if len(x)<2: return np.zeros_like(y)
    if x[0]>x[-1]: xs,ys=x[::-1].copy(),y[::-1].copy(); flipped=True
    else: xs,ys=x.copy(),y.copy(); flipped=False
    n=len(ys); cap=max(1,min(n_avg,n//4)); b_low=float(np.mean(ys[:cap])); b_high=float(np.mean(ys[-cap:])); step=b_low-b_high; B=np.linspace(b_low,b_high,n)
    for _ in range(n_iter):
        B_prev=B.copy(); signal=np.maximum(ys-B,0.0); cum_right=np.zeros(n)
        for i in range(n-2,-1,-1): cum_right[i]=cum_right[i+1]+(signal[i]+signal[i+1])/2*(xs[i+1]-xs[i])
        total=cum_right[0]
        if total<=0.0: break
        B=b_high+step*(cum_right/total); B=np.minimum(B,ys)
        if np.max(np.abs(B-B_prev))<tol: break
    B=np.minimum(B,ys); return B[::-1] if flipped else B

def tougaard(x,y,n_avg=1):
    n=len(x)
    if n<2: return np.zeros_like(y,dtype=float)
    B_coef,C_coef=2866.0,1643.0; xa=np.asarray(x,dtype=float); ya=np.asarray(y,dtype=float)
    if n_avg>1: ya=avg(ya,n_avg)
    flipped=bool(xa[0]<xa[-1])
    if flipped: xa,ya=xa[::-1].copy(),ya[::-1].copy()
    c0=float(ya[-1]); net=ya-c0; dx=float(abs(xa[1]-xa[0])); bg=np.empty(n,dtype=float)
    for i in range(n):
        acc=0.0
        for j in range(i,n):
            T=abs(xa[j]-xa[i]); K=B_coef*T/((C_coef+T*T)**2); acc += K*net[j]*dx
        bg[i]=c0+acc
    if bg[-1]"'!=bg[0]:
        scale=(float(ya[0])-c0)/(bg[0]-bg[-1]); bg=c0+(bg-c0)*scale
    return bg[::-1] if flipped else bg
x=np.linspace(700.0,740.0,200); y=4000.0+3000.0*np.exp(-0.5*((x-720.0)/4.0)**2); y=y.copy(); y[0]+=500.; y[-1]-=500.
for name,fn in [("shirley",shirley),("smart",smart),("smart_exp",smart_exp),("tougaard",tougaard)]:
    r=fn(x,y,n_avg=1); a4=fn(x,y,n_avg=4); a8=fn(x,y,n_avg=8); print(name,"d4",float(np.max(np.abs(r-a4))),bool(np.allclose(r,a4)),"d8",float(np.max(np.abs(r-a8))),bool(np.allclose(r,a8)))
'"'" in /Users/skyefortier/xps-verify
 succeeded in 120ms:
4 maxdiff 375.00567255237456 first 0.0 last -375.00567255237456 allclose False
8 maxdiff 437.51940027444243 first 0.0 last -437.51940027444243 allclose False
change new raw vs n1 440.075897556163 False

 succeeded in 160ms:
shirley d4 378.93845192245317 False d8 440.075897556163 False
smart d4 378.93845192245317 False d8 440.075897556163 False
smart_exp d4 379.23413489938866 False d8 440.24684064952726 False
tougaard d4 634.0011258789536 False d8 698.6998781124316 False

codex
I have enough to form the review. The focused pytest file can’t run here because both `pytest` and `lmfit` are missing, but the standalone probes confirm the endpoint-outlier fixture is not laundered: `n_avg=8` changes Shirley/Smart by about 440 counts, Smart Exp by about 440, and Tougaard by about 699 on that fixture.
codex
1. **MAJOR** [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:307), [fitting.py](/Users/skyefortier/xps-verify/fitting.py:1052): `SMART` endpoint averaging now has two incompatible semantics. `_compute_background(..., BackgroundType.SMART, endpoint_avg=N)` calls `smart_background(x, y, n_avg=N)`, which clamps against raw `y`. The existing manual `/api/fit` paths still call `smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))`, which clamps against the averaged copy. On the new noisy-endpoint fixture, a standalone probe shows `smart_background(x, y, n_avg=8)` differs from the manual convention by about `437.5` counts at the high endpoint. So the commit’s parity claim for “Find Peaks and manual Run Fit must agree once both pass the same endpoint_avg” is false for Smart backgrounds, and the new tests do not cover that product-level parity path.

Verification notes:
- Scope is otherwise contained: `git show` changes only `fitting.py`, `autofit/engine.py`, and `tests/test_background_n_avg.py`; no diff in `app.py`, `templates/index.html`, or `autofit/methods/*.py`.
- `_apply_endpoint_averaging` body is byte-identical before/after relocation.
- `n_avg=1` is guarded as a true no-op path in `shirley_background`.
- `_compute_background` has 3 call sites inside `autofit/engine.py`; none pass `endpoint_avg`. There are also existing external module call sites, and they also omit it.
- `app.py` defaults are `1` at lines 718 and 794.
- I could not run pytest here: `pytest` is unavailable, and importing app code fails because `lmfit` is not installed.
- Standalone probes confirm the noisy fixture is strong enough; `n_avg=8` changes Shirley/Smart by about `440` counts, Smart Exp by about `440`, and Tougaard by about `699`.
- The relocation/importability test is decorative as red/green evidence for this commit, but acceptable as a small future regression pin.

VERDICT: NO-GO
tokens used
49,039
1. **MAJOR** [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:307), [fitting.py](/Users/skyefortier/xps-verify/fitting.py:1052): `SMART` endpoint averaging now has two incompatible semantics. `_compute_background(..., BackgroundType.SMART, endpoint_avg=N)` calls `smart_background(x, y, n_avg=N)`, which clamps against raw `y`. The existing manual `/api/fit` paths still call `smart_background(x, _apply_endpoint_averaging(y, endpoint_avg))`, which clamps against the averaged copy. On the new noisy-endpoint fixture, a standalone probe shows `smart_background(x, y, n_avg=8)` differs from the manual convention by about `437.5` counts at the high endpoint. So the commit’s parity claim for “Find Peaks and manual Run Fit must agree once both pass the same endpoint_avg” is false for Smart backgrounds, and the new tests do not cover that product-level parity path.

Verification notes:
- Scope is otherwise contained: `git show` changes only `fitting.py`, `autofit/engine.py`, and `tests/test_background_n_avg.py`; no diff in `app.py`, `templates/index.html`, or `autofit/methods/*.py`.
- `_apply_endpoint_averaging` body is byte-identical before/after relocation.
- `n_avg=1` is guarded as a true no-op path in `shirley_background`.
- `_compute_background` has 3 call sites inside `autofit/engine.py`; none pass `endpoint_avg`. There are also existing external module call sites, and they also omit it.
- `app.py` defaults are `1` at lines 718 and 794.
- I could not run pytest here: `pytest` is unavailable, and importing app code fails because `lmfit` is not installed.
- Standalone probes confirm the noisy fixture is strong enough; `n_avg=8` changes Shirley/Smart by about `440` counts, Smart Exp by about `440`, and Tougaard by about `699`.
- The relocation/importability test is decorative as red/green evidence for this commit, but acceptable as a small future regression pin.

VERDICT: NO-GO
