OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0c7ec-fa14-7690-ba8c-b3e86b0c9403
--------
user
RECHECK, round 5, of unit A03: branch fix-voigt-eta-identity, git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round 4 (docs/autofit/codex/a03_voigt_eta_r4_verdict_runA.md / runB.md, both NO-GO) confirmed every round-3 item closed and found: (1) MAJOR tests/autofit/battery_common.assert_eval_parity accepted "the contract mix, or else the saved mix" - a gate that passed a post-A03 Voigt with a wrong stored curve (glMix 90, metadata 0.5) and a legacy U 4f envelope with 3.5 % of a LACX line added; (2) MINOR the "Voigt component's own area" statistic was the per-tab maximum; (3) MINOR the sweep's comment said a lock cannot leave the optimiser's bounds.

What changed since (plan §9 round 4; commit "fix(A03): Codex round 4"): autofit/parity.recorded_voigt_eta(p) reads p._backendParams.gl_ratio.value - the mix the server recorded for the fit that produced fittedY (0.5 for an A03 fit, the free or held value of an older save; None when never server-fitted) - and eval_parity_relmax(rf, voigt_eta="recorded") (the default) evaluates each Voigt with it (the contract when None); assert_eval_parity makes ONE assertion with it, no fallback. Both round-4 reproducers now fail; the 29 U 4f and 3 Cl 2p battery tabs pass. scripts/voigt_saved_vs_refit.js reports per-tab maxima AND per-component quantiles (110 Voigt components: median 3.3 %, p90 6.0 %, max 15.3 %; re-run committed); plan §2b/§7 and findings §7 relabelled. The sweep comment corrected.

Verify each round-4 item is closed, then try to break: recorded_voigt_eta (a Voigt whose _backendParams is stale from an EARLIER fit than the saved fittedY - can the page save fittedY from one fit and _backendParams from another? read applyBackendResult / _syncActiveToRecord / the save path; a linked Voigt whose gl_ratio is an expr; a Voigt with fixGlMix under the old request; a peak with _backendParams but no gl_ratio key); whether the "recorded" default changes any OTHER battery's evaluation (C 1s, B 1s: no Voigt - confirm); the per-component statistic's convention vs the per-tab one; the whole unit once more at a glance for anything left open (plan §9, all rounds) and every number in plan/findings/CLAUDE.md/comments against docs/findings/a03/*.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll review the diff and round-4 fixes, trace how saves pair `fittedY` with `_backendParams`, and check the parity gate and published numbers. I’ll keep this read-only and finish with a ranked verdict.

exec
/bin/zsh -lc "pwd; git status --short; git branch --show-current; git diff --stat main..HEAD; rg --files -g 'AGENTS.md' -g '*a03*' -g '*voigt*' -g '*parity*' -g 'CLAUDE.md' -g 'battery_common.py'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 25ms:
 CLAUDE.md                                          |    52 +-
 autofit/parity.py                                  |    50 +-
 autofit/reference.py                               |    54 +-
 .../autofit/codex/a03_voigt_eta_r2_verdict_runA.md |  8771 +++++++++++++++
 .../autofit/codex/a03_voigt_eta_r2_verdict_runB.md |  8492 ++++++++++++++
 .../autofit/codex/a03_voigt_eta_r3_verdict_runA.md |  7096 ++++++++++++
 .../autofit/codex/a03_voigt_eta_r3_verdict_runB.md |  7690 +++++++++++++
 .../autofit/codex/a03_voigt_eta_r4_verdict_runA.md | 10939 +++++++++++++++++++
 .../autofit/codex/a03_voigt_eta_r4_verdict_runB.md | 10240 +++++++++++++++++
 .../codex/a03_voigt_eta_recheck2_prompt.txt        |     9 +
 .../codex/a03_voigt_eta_recheck3_prompt.txt        |     9 +
 .../autofit/codex/a03_voigt_eta_recheck_prompt.txt |     9 +
 docs/autofit/codex/a03_voigt_eta_review_prompt.txt |    22 +
 docs/autofit/codex/a03_voigt_eta_verdict_runA.md   |  7974 ++++++++++++++
 docs/autofit/codex/a03_voigt_eta_verdict_runB.md   |  7777 +++++++++++++
 docs/findings/2026-09-fit-determinacy.md           |    85 +
 docs/findings/a03/local_server_gap.json            |  3375 ++++++
 docs/findings/a03/local_server_gap.log             |    18 +
 docs/findings/a03/voigt_eta_summary.txt            |     7 +
 docs/findings/a03/voigt_saved_vs_refit.json        |  2456 +++++
 docs/findings/a03/voigt_saved_vs_refit.log         |    56 +
 .../plans/2026-09-22-a03-voigt-eta-identity.md     |   299 +
 fitting.py                                         |    11 +
 scripts/bg_window_worked_example.py                |     2 +-
 scripts/endpoint_avg_sensitivity.py                |     2 +-
 scripts/gen_region_battery_fixture.py              |     5 +-
 scripts/gen_u4f_battery_fixture.py                 |     5 +-
 scripts/local_server_gap.js                        |   102 +
 scripts/voigt_eta_measure.py                       |   138 +
 scripts/voigt_saved_vs_refit.js                    |    79 +
 templates/index.html                               |    65 +-
 tests/autofit/battery_common.py                    |    31 +-
 tests/autofit/fixtures/cl2p_battery_expected.json  |    20 +-
 tests/autofit/fixtures/u4f_battery_expected.json   |  1064 +-
 tests/autofit/test_b1s_cl2p_batteries.py           |     9 +-
 tests/autofit/test_u4f_parity_battery.py           |    13 +-
 tests/js/fit_acceptance.test.js                    |     2 +-
 tests/js/lineshape_parity.test.js                  |    96 +
 tests/js/lineshape_parity_backend.py               |    19 +-
 tests/js/lineshape_roundtrip.test.js               |   258 +
 tests/js/lineshape_roundtrip_backend.py            |    37 +
 tests/js/local_lm_descent.test.js                  |     2 +-
 tests/js/local_lm_server_parity_backend.py         |    14 +-
 tests/test_voigt_contract.py                       |    99 +
 44 files changed, 76955 insertions(+), 598 deletions(-)
CLAUDE.md
scripts/voigt_eta_measure.py
scripts/voigt_saved_vs_refit.js
autofit/parity.py
tests/test_legacy_parity.py
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md
docs/superpowers/plans/2026-09-02-task4-background-twin-parity.md
docs/findings/a03/voigt_saved_vs_refit.json
docs/findings/a03/voigt_saved_vs_refit.log
docs/findings/a03/voigt_eta_summary.txt
tests/test_voigt_contract.py
tests/js/local_lm_server_parity_backend.py
tests/autofit/test_u4f_parity_gate.py
tests/autofit/test_u4f_parity_battery.py
tests/autofit/test_c1s_parity_gate.py
tests/autofit/battery_common.py
tests/autofit/test_b1s_cl2p_parity_gates.py
tests/autofit/test_c1s_parity_battery.py
tests/js/lineshape_parity_backend.py
tests/js/lineshape_parity.test.js
docs/autofit/codex/a03_voigt_eta_r5_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_recheck4_prompt.txt
docs/autofit/codex/a03_voigt_eta_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r2_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_r3_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_r4_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_recheck3_prompt.txt
docs/autofit/codex/a03_voigt_eta_r4_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r3_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_recheck_prompt.txt
docs/autofit/codex/a03_voigt_eta_recheck2_prompt.txt
docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r5_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_review_prompt.txt

exec
/bin/zsh -lc 'rg --files -g AGENTS.md /Users/skyefortier/xps-app /Users/skyefortier/.codex 2>/dev/null | head -50; git diff main..HEAD -- autofit/parity.py autofit/reference.py fitting.py tests/autofit/battery_common.py; cat docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7582xFBu' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-C8oQ8c0r' (errno=Operation not permitted)
diff --git a/autofit/parity.py b/autofit/parity.py
index fb09ddd..09284f2 100644
--- a/autofit/parity.py
+++ b/autofit/parity.py
@@ -36,7 +36,7 @@ from fitting import (
     tougaard_background,
     run_fit,
 )
-from .reference import ReferenceFit
+from .reference import ReferenceFit, apply_backend_params, peak_to_backend_spec
 
 
 def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
@@ -168,13 +168,38 @@ def grid_matches(rf: ReferenceFit, tol: float = 1e-3) -> bool:
     return float(np.max(np.abs(np.asarray(saved_be, dtype=float) - roi))) <= tol
 
 
-def eval_parity_relmax(rf: ReferenceFit) -> float:
+def recorded_voigt_eta(p: dict) -> float | None:
+    """The mix the server actually fitted this Voigt with, from the record
+    the page keeps of that fit (``p._backendParams.gl_ratio.value``, written
+    by applyBackendResult): 0.5 for a fit under the A03 request, the free or
+    held value the request BEFORE A03 sent for an older save. None when the
+    peak carries no such record (never server-fitted)."""
+    bp = p.get("_backendParams")
+    g = bp.get("gl_ratio") if isinstance(bp, dict) else None
+    v = g.get("value") if isinstance(g, dict) else None
+    return float(v) if isinstance(v, (int, float)) and np.isfinite(v) else None
+
+
+def eval_parity_relmax(rf: ReferenceFit, voigt_eta: str = "recorded") -> float:
     """
     Max |python_eval − saved fittedY| / max|fittedY| on the reconstructed
     ROI grid.  Requires ``grid_matches(rf)``.
+
+    voigt_eta: "recorded" (default) evaluates each Voigt with the mix the
+    server recorded for the fit that produced ``fittedY``
+    (``recorded_voigt_eta``; the contract's 0.5 when there is no record) —
+    ONE deterministic choice from the record itself, never "whichever
+    passes" (A03 Codex round 4). "contract" evaluates every Voigt at the
+    page's current request (eta = 0.5, A03 2026-09-22); saves made under the
+    old request (eta free from 0.3) cannot reproduce their own fittedY that
+    way, and that difference is the A03 change, not a numerics regression.
     """
     fittedY = np.asarray(rf.fit_result["fittedY"], dtype=float)
     specs = rf.backend_peak_specs()
+    if voigt_eta == "recorded":   # backend_peak_specs keeps the peaks' order
+        specs = [dict(s, gl_ratio=recorded_voigt_eta(p))
+                 if p.get("shape") == "Voigt" and recorded_voigt_eta(p) is not None else s
+                 for s, p in zip(specs, rf.peaks)]
     model = evaluate_model(rf.roi_be, specs)
     i0, i1 = rf.bg_indices()
     bg = background_like_run_fit(
@@ -184,16 +209,30 @@ def eval_parity_relmax(rf: ReferenceFit) -> float:
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
@@ -209,6 +248,7 @@ def refit_record(rf: ReferenceFit) -> dict[str, Any]:
             "fwhm": par["fwhm"]["value"],
             "amplitude": par["amplitude"]["value"],
             "area": par["area"]["value"],
+            "params": {k: v["value"] for k, v in par.items() if k != "area"},
         })
     return {
         "project": rf.project,
diff --git a/autofit/reference.py b/autofit/reference.py
index fe46d48..6bb2eb0 100644
--- a/autofit/reference.py
+++ b/autofit/reference.py
@@ -101,15 +101,18 @@ def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
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
     elif shape == "asym-GL":
         spec["shape"] = "asymmetric_gl"
-        spec["gl_ratio"] = (p.get("glMix") or 50) / 100.0
-        spec["asymmetry"] = p.get("asymmetry") or 0
+        # only a NON-NUMBER falls back to the default (a 0 is a value; A03 Codex round 1)
+        spec["gl_ratio"] = (p["glMix"] if _finite(p.get("glMix")) else 50) / 100.0
+        spec["asymmetry"] = p["asymmetry"] if _finite(p.get("asymmetry")) else 0
         spec["fix_asymmetry"] = bool(p.get("fixAsymmetry"))
         if _finite(p.get("_afAsymMin")):
             spec["asymmetry_min"] = p["_afAsymMin"]
@@ -117,8 +120,8 @@ def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
             spec["asymmetry_max"] = p["_afAsymMax"]
     elif shape == "DS":
         spec["shape"] = "doniach_sunjic"
-        spec["alpha"] = p.get("dsAlpha") or 0.1
-        spec["gamma_asym"] = p.get("dsGamma") or 0.0
+        spec["alpha"] = p["dsAlpha"] if _finite(p.get("dsAlpha")) else 0.1
+        spec["gamma_asym"] = p["dsGamma"] if _finite(p.get("dsGamma")) else 0.0
         spec["fix_alpha"] = bool(p.get("fixDsAlpha"))
         spec["fix_gamma_asym"] = bool(p.get("fixDsGamma"))
     elif shape == "DSG_LA":
@@ -150,6 +153,47 @@ def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
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
diff --git a/fitting.py b/fitting.py
index cfcfb9e..78fec0d 100644
--- a/fitting.py
+++ b/fitting.py
@@ -847,6 +847,17 @@ def _make_peak_params(
         full = prefix + name
         if full not in p:
             return
+        if not vary and expr is None:
+            # A HELD parameter is held at the value requested. The bounds are
+            # the optimiser's search limits; lmfit clips a value outside them
+            # even when it does not vary, which silently changed a locked
+            # DS+G m of 0 (the page's delta-kernel branch, drawn without
+            # convolution) into 0.05 (a convolved fit) — A03 Codex round 2's
+            # locked-at-bounds round trips. Widen the limit to the value.
+            if min_ is not None and value < min_:
+                min_ = value
+            if max_ is not None and value > max_:
+                max_ = value
         p[full].set(value=value)
         if expr is not None:
             p[full].expr = expr
diff --git a/tests/autofit/battery_common.py b/tests/autofit/battery_common.py
index 4c994a7..b9331b2 100644
--- a/tests/autofit/battery_common.py
+++ b/tests/autofit/battery_common.py
@@ -66,6 +66,12 @@ def assert_roster(fits, expected, min_size, min_projects, gen_script):
 
 
 def assert_eval_parity(rf, tol=EVAL_PARITY_TOL):
+    # A Voigt is evaluated with the mix the server RECORDED for the fit that
+    # produced fittedY (autofit.parity.recorded_voigt_eta): the contract's 0.5
+    # for a fit under the A03 request, the free or held value the request
+    # before A03 sent for an older save. One deterministic choice from the
+    # record itself — never "the contract, or else the saved one" (A03 Codex
+    # round 4 showed that gate accepting a corrupted envelope).
     relmax = eval_parity_relmax(rf)
     assert relmax < tol, (
         f"{rf.project}/{rf.name}: python eval of saved params deviates from "
@@ -78,24 +84,39 @@ def assert_refit_stability_and_fixture(
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

## 2. Measured before deciding

### 2a. The two requests (`scripts/voigt_eta_measure.py` → `docs/findings/a03/voigt_eta_summary.txt`)

The 90 committed targets with a Voigt component (89 U 4f tabs across five
projects and one Cl 2p; 180 Voigt components; 48 saved models and 42 Batch
Fit starts from `scripts/optimizer_disagreement_targets.js`), each fitted
with the page's settings (Trust-Region, `n_perturb: 3`) under BOTH requests,
constructed explicitly by the script (Codex round 1: it used to take the
target file's own Voigt specs as the "old" arm): before A03 (η free from
0.3) and since (η held at 0.5). All 180 fits converged. These rows use the
SERVER's curves and trapezoidal integration on the fitted grid; they
characterise the two requests, not a screen (that is 2b).

| | median | p90 | max |
|---|---:|---:|---:|
| free η of the 180 Voigt components | 60 < 0.01 (pure Gaussian), 16 > 0.99 (pure Lorentzian), 24 within 0.4–0.6 | | |
| the 0.5 curve under the free fit's parameters (what the page drew) vs the curve the server fitted, per Voigt | 13.9 % | 19.2 % | 20.1 % (116 of 180 > 10 %) |
| A. the same, as area fractions per target | 0.96 pp | 1.48 pp | 1.55 pp (35 of 90 > 1 pp) |
| B. fixed-η refit vs that 0.5 curve | 0.34 pp | 0.54 pp | 1.02 pp (1 of 90 > 1 pp) |
| C. fixed-η refit vs the free fit | 0.93 pp | 1.31 pp | 2.04 pp (33 of 90 > 1 pp) |
| χ²ᵣ fixed / free | 1.09 | 1.19 | 5.4 (fixed LOWER on 10 of 90: the free fit was in a worse minimum) |

Row A is the error that was shipping.

### 2b. What a student sees change (`scripts/voigt_saved_vs_refit.js` → `docs/findings/a03/voigt_saved_vs_refit.json`)

Every committed spectrum tab with a saved fit and a Voigt component (55
tabs across six projects, all converged): the PAGE's area of each saved
peak (`evalPeakArray` over the ROI grid × step, as `_peakArea` — a Voigt
at 0.5, an LA at its rounded m, exactly the Results table) against the
page's area of the same peaks after the server refit under the A03 request
(Trust-Region, the page's `n_perturb: 3`, written back through
`_applyBackendParams`). Grids as the page holds them (Codex rounds 2–3):
the page keeps its DISPLAY grid (the corrected ROI energies, unrounded —
`fitResult.be` after Run Fit and the integration grid of Results) apart
from the UPLOAD it sends (energies 4 dp, intensities 2 dp; the rounding also
determines the request seed) and selects the background window on the
display grid before uploading. So: the saved side integrates on the saved
fit's own grid (`fitResult.be`, present on 41 of the 55 tabs; the display
grid otherwise), the refit side on the display grid; the request carries
the rounded arrays and the window indices chosen on the display grid
(`_bgWindowIndices`).

| | median | p90 | max |
|---|---:|---:|---:|
| largest area-fraction move, per tab | 0.36 pp | 0.51 pp | 0.69 pp (0 of 55 > 1 pp) |
| largest Voigt area change, per tab | 4.6 % | 7.6 % | 15.3 % |
| a Voigt component's own area change, per component (110) | 3.3 % | 6.0 % | 15.3 % |

That is the release-note number.

## 3. Contract chosen: fixed η = 0.5 on BOTH sides

`peakToBackendSpec` (and the twin) send `gl_ratio: 0.5, fix_gl_ratio: true`
for a Voigt; `_applyBackendParams` writes `glMix` only for GL / asym-GL (a
Voigt keeps the mix it carries for a later switch to GL); the dropdown says
"Fixed 50/50 … choose GL to fit the mix". The other candidate — make the
page honour the fitted η — would have turned "Voigt" into a GL with a
hidden slider and kept, silently, a shape the student never chose (the
owner's rule from the scattered-starts unit: never substitute an
interpretation because it scored better); 76 of 180 fitted η values on a
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
  pins and the linked pair; on the branch 33 pass, 2 todo (below).
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
7.9 while the local engine holds it at 8, and χ²ᵣ (local/server − 1) is
+9.6 %, +10.1 %, −5.0 % and +12.7 %. Movement in m alone does not
attribute the residual (Codex round 1), so the script has a CONTROL arm:
the server fitted with every LA m HELD at the value the local engine
effectively uses — its start rounded to an integer, as
`laTrueCasaXPS_array` rounds it (Codex round 2) — the one thing the local
engine cannot move.

| target | local χ²ᵣ | server χ²ᵣ, m free | server χ²ᵣ, m held | local vs server, m free (Δcentre / ΔFWHM / Δarea / Δfrac) | local vs server, m held | local χ²ᵣ above the held-m server's |
|---|---:|---:|---:|---|---|---:|
| Scan_4 | 1.970 | 1.798 | 1.870 | 26.6 meV / 5.3 % / 8.3 % / 0.33 pp | 13.4 meV / 3.1 % / 5.3 % / 0.19 pp | +5.4 % |
| Scan_5 | 2.393 | 2.174 | 2.182 | 4.7 meV / 4.3 % / 6.6 % / 0.35 pp | 6.3 meV / 3.5 % / 5.5 % / 0.25 pp | +9.7 % |
| Scan_6 | 2.657 | 2.798 | 2.629 | 28.8 meV / 15.8 % / 8.9 % / 0.77 pp | 3.6 meV / 1.1 % / 1.6 % / 0.07 pp | +1.1 % |
| Scan_8 | 4.656 | 4.129 | 4.117 | 5.7 meV / 5.0 % / 8.3 % / 0.32 pp | 5.8 meV / 5.0 % / 8.2 % / 0.32 pp | +13.1 % |

(The 5 agreeing targets are within 1.6 % of the held-m server's χ²ᵣ and
within 4.0 meV / 1.5 % / 2.1 % / 0.12 pp of it.) So: on Scan_6 the residual
IS the `caM` clamp (holding m on the server closes it to the
agreeing-target envelope). On Scan_5 and Scan_8 holding m changes nothing —
the local engine's descent stops at a χ²ᵣ 10–13 % above the server's from
the same start with the same free parameters: a worse minimum, the
"several minima" case (findings §2 had the mirror image on C 1s Scan_4,
where the local engine found the better one). Scan_4 is in between
(+5.4 %). The residual is therefore two things, and `caM` is the smaller.

**Decision: the "starting point" designation STAYS**, on two grounds now:
the `caM` clamp (one target) and the local engine landing in a worse
minimum than Trust-Region on three of nine U 4f targets. The `caM` clamp
remains the next unit; the worse-minimum finding is recorded in findings
§7 for the local-engine work that follows it. Wording in the page updated
to say so (LA components and several minima; no longer Voigt).

## 7. Release-note line

Voigt components are now fitted at the fixed 50/50 mix the page has always
drawn; until now Run Fit let their mix vary on the server and the page
reported the 50/50 curve's area under the other mix's parameters (up to
20 % off per component). Re-fitting a saved project with Voigt components
moves an area fraction by 0.36 pp at the median and 0.69 pp at most on the
55 committed tabs (a Voigt component's own area by 3.3 % at the median,
15 % at most). Use GL to fit the mix. Also fixed: an asym-GL mix of exactly 0 or a
DS α of exactly 0 was sent to the server as 50 / 0.1, and a locked value
outside the optimiser's search limits (a DS+G m locked at 0) was moved onto
the limit before fitting; such requests now also draw a different
random seed, since the seed hashes the parameters as the fit receives them.

## 8. Verification

- `tests/test_voigt_contract.py` 6 passed; `lineshape_roundtrip.test.js`
  33 passed, 2 todo; the JS suite 375 tests, 368 pass, 7 todo (`node --test
  tests/js/*.test.js`; the directory form does not run in this node); full
  `pytest tests/`: see §9.
- Browser check (`browser_check_a03.py`, dev gunicorn :5151 from the
  worktree, re-run after round 1): the request carries `gl_ratio 0.5, fix_gl_ratio true` for
  both Voigt components; the server returns `vary: false, 0.5`; drawn vs
  fitted curve 1.3e-13 of amplitude for the Voigts (LACX 5.6e-3 — the caM
  rounding); the Results area of a Voigt equals the server curve's to
  0.0000 % (LACX −0.66 %, the same rounding); the chart dataset is the drawn curve; `glMix` unchanged in the
  live model and the saved record; Batch Fit onto U4f Scan_1 converges
  locally; no page errors.

## 9. Codex rounds

**Round 1 (`docs/autofit/codex/a03_voigt_eta_verdict_run{A,B}.md`): NO-GO ×2,
no blocker, converging findings.** Fixed:
1. MAJOR — the measurement script took the target file's own Voigt specs as
   the "old" arm, so a target file regenerated with the A03 builder would
   have made both arms identical. Both requests are now constructed
   explicitly; the generator is named correctly (`.js`); re-run (§2a).
2. MAJOR — the release-note number was a server-curve/trapezoid comparison
   of two refits, not the page's saved numbers against the page's refit
   numbers. Replaced by `scripts/voigt_saved_vs_refit.js` (§2b); the old
   rows relabelled as what they are.
3. MAJOR/MINOR — the builder sent an asym-GL mix of 0 as 50 and a DS α of 0
   as 0.1 (`p.glMix || 50`, `p.dsAlpha || 0.1`; the Python twin likewise);
   locked, the server held the substitute and the drawn curve differed from
   the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders
   (only a non-number falls back); the round-trip test now locks every shape
   parameter at its bounds; the sweep's backend parameters now come THROUGH
   `peakToBackendSpec` rather than a mapping of the harness's own.
4. MINOR — the uncertainty panel told a Voigt's user to "unlock the padlock"
   for a mix that has none: it now says the shape fixes the mix and points
   to GL.
5. MINOR — "χ²ᵣ differs by 8–20 %" was wrong (the four are +9.6, +10.1,
   −5.0, +12.7 %), the comment's "24 %" was 20 %, row A's 1.60 was 1.61 (now
   1.55 with the explicit arms); and attributing the whole residual to the
   `caM` clamp was an inference — the control arm (§6) shows it is one
   target of four.

**Round 2 (`a03_voigt_eta_r2_verdict_run{A,B}.md`): NO-GO ×2; round-1
items 1, 3, 4 confirmed closed; found:**
1. MAJOR — the saved side of 2b integrated on the current ROI grid where
   Results uses the saved fit's grid (11 tabs differ; 1.2 % on one area),
   and the refit request bypassed the page's upload rounding (which also
   sets the seed). Both fixed; re-run: median 0.35 → 0.36 pp, max 0.69 pp.
2. MINOR — the control arm held m at the stored fractional value (8.199)
   where the local engine rounds it (8). Now held at the rounded value;
   re-run (table in §6).
3. MINOR — "every shape parameter locked at its bounds" was seven cases.
   Now 18: both bounds of every shape parameter of every shape, the
   convolved shapes where their evaluators are exact. Doing so found a
   FOURTH identity defect: lmfit clips a held value to its bounds, so a
   DS+G with m locked at 0 (the delta-kernel branch the page draws) was
   fitted with m = 0.05, the free-parameter floor — a convolved curve the
   page never drew. `fitting._make_peak_params._set` now widens the limit
   to a held value; pinned in `tests/test_voigt_contract.py`.
4. MINOR — "10–13 %" (the three worse-minimum targets are +5.4, +9.7,
   +13.1 % above the held-m server), "12 %" median in the harness header,
   stale test counts. Corrected. Commit 712e136's message carries the
   superseded round-0 numbers; the merge is fast-forward, so this plan and
   the deploy-log entry are the record.

**Round 3 (`a03_voigt_eta_r3_verdict_run{A,B}.md`): NO-GO ×2; found:**
1. MAJOR — a DS+G with α locked at 0.5 (the page's input allows it): the
   server's evaluator clips α to 0.495, the page's did not — 0.9 % of
   amplitude apart even in the exact delta branch. The page now clips as
   the server does (`_dsgAlpha`, used by `evalPeak` and the delta-kernel
   branch); the locked-0.5 case is in the round-trip test.
2. MAJOR — the measurement's bridge selected the background window on the
   ROUNDED grid where the page selects it on the display grid before
   uploading (a window edge can move one channel), and the refit side
   integrated on the rounded grid where the page integrates on the
   unrounded one. Display and upload grids are now kept apart and the
   window indices are passed to the bridge; re-run: unchanged to the
   quoted precision (median 0.36 pp, max 0.69 pp).
3. MINOR — the m locks of the convolved shapes (DS+G m 0.05 and 4, LA
   m 499) are now pinned for the request value and the server's hold; their
   drawn-vs-fitted comparison stays under the evaluator todo.
4. MINOR — "12 %" in the harness header, "10 pass" and "6.7 %" in this
   plan. Corrected.
Also in this round: the full suite showed the Cl 2p battery's Scan_1 (two
Voigt lines, saved under the old request with η written back as 15.7 %)
failing exactly as the U 4f battery did. Eval parity for a save made under
the old request holds with the SAVED mix, not the contract's
(`battery_common.assert_eval_parity` tries the saved mix when the contract
mix fails on a tab with a Voigt); its refit is a fixed point of a refit
from the refit (stationarity="refit"); the Cl 2p fixture regenerated with
its committed generator (B 1s untouched).

**Round 4 (`a03_voigt_eta_r4_verdict_run{A,B}.md`): NO-GO ×2; round-3
items closed; found:**
1. MAJOR — the eval-parity gate written above ("the contract mix, or else
   the saved mix") was a loophole: either reproducer — a post-A03 Voigt
   whose stored curve is wrong, or a legacy envelope with 3.5 % of a LACX
   line added — passed on whichever mix fit. Replaced by ONE deterministic
   choice from the record itself: a Voigt is evaluated with the mix the
   server RECORDED for the fit that produced `fittedY`
   (`autofit.parity.recorded_voigt_eta`, from the peak's `_backendParams`;
   0.5 for an A03 fit, the free or held value of an older save; the
   contract when there is no record). Both reproducers now fail; the 29
   U 4f and 3 Cl 2p tabs pass.
2. MINOR — the "Voigt component's own area" statistic was the per-tab
   maximum; relabelled, and the per-component quantiles added (110
   components: median 3.3 %, p90 6.0 %, max 15.3 %).
3. MINOR — the sweep's comment said a lock cannot take a parameter outside
   the optimiser's bounds; since round 2 a held value is honoured as
   requested. Corrected.

exec
/bin/zsh -lc "git diff main..HEAD -- templates/index.html scripts/voigt_saved_vs_refit.js scripts/local_server_gap.js tests/js/lineshape_parity.test.js CLAUDE.md; rg -n 'applyBackendResult|_syncActiveToRecord|_backendParams|fittedY:|fitResult =|JSON.stringify|function save|async function save' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Q7CxviMC' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-bh3gr10h' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index c1eeada..739c108 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -110,13 +110,36 @@ tab reordering exists.
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
+at 0.5; the same harnesses then found `p.glMix || 50` / `p.dsAlpha || 0.1`
+sending a mix or α of exactly 0 as the default, lmfit clipping a HELD value
+to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
+`_make_peak_params._set` now widens a limit to a held value), and the
+server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
+held parameter is held at its value; what the page draws is what the
+server fitted. Tracked gaps, `todo` in both files: LACX with m > 0 (the page draws
+a rounded integer kernel; the server fits m continuously — the `caM` clamp
+unit) and DS+G with m ≥ 0.05 (the page's quadrature `laCasaXPS` sizes its
+step to the Lorentzian core, not the Gaussian kernel, and is wrong by up to
+80 % of amplitude across the fitted β/m range — 1e52 × at β = 2, m = 0.05;
+0 of 865 committed components use DS+G; its own unit). Details in
+`docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+
 ---
 
 ## Design Rules
@@ -459,16 +482,29 @@ the integer-clamped `caM` is not optimised (carried at its start value).
 
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
+to 20.8 % area on the Voigt satellites); it still differs on the other 4
+U 4f targets (satellite areas up to 8.9 %, 0.77 pp) for two reasons,
+separated by a control arm (the server with every LA m held at its start):
+on one target the `caM` clamp (`caM` held at its start locally while the
+server fits m continuously; holding m on the server closes the gap), on
+three the local descent stopping at a χ²ᵣ 5–13 % above the server's from
+the same start with the same free parameters — a worse minimum, the
+"several minima" case (both engines' amplitude floor is 0 since unit
+step (b)). Both engines weight by
 √intensity whether the data are counts or CPS (a convention, not a
 calibrated uncertainty for rates); the formula is the same but the inputs
 are not bit-identical, because `uploadToBackend` rounds intensities to
-2 dp before the server weights them. Retire the designation only on a
-re-measurement after A03 and the `caM` clamp. (The amplitude-bound change
+2 dp before the server weights them. A03 is done and the designation
+STAYS on both grounds; the `caM` clamp is the next unit, the worse-minimum
+outcome is recorded for the local-engine work after it, and the label is
+reconsidered only on a re-measurement after both. (The amplitude-bound change
 DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
 implemented: unit step (b), 2026-09-22, below.) The same file records that a
 converged server fit is not ground truth: on a committed C 1s scan the
diff --git a/scripts/local_server_gap.js b/scripts/local_server_gap.js
new file mode 100644
index 0000000..370c215
--- /dev/null
+++ b/scripts/local_server_gap.js
@@ -0,0 +1,102 @@
+#!/usr/bin/env node
+// Local engine vs server from the SAME scaled start on the committed
+// UCl4-graphite project's Batch Fit targets (unit W1's methodology,
+// 2026-09-18; re-run for A03, 2026-09-22 — the test of whether Batch Fit's
+// "starting point" label can retire). Every C1s Scan_N and U4f Scan_N tab is
+// a target; the source is the scan the student fitted ('C1s Scan' / 'U4f
+// Scan'); the start is the source's model with amplitudes scaled to the
+// target's maximum (what runPropagation does); both engines fit that start
+// on the same background (the page's computeBackgroundCore; the server
+// recomputes its own from the same settings). Differences are evaluated with
+// the PAGE's semantics — the server's parameters written onto a copy of the
+// start with _applyBackendParams, areas as _peakArea (evalPeakArray over the
+// ROI grid × step) — so the comparison is about parameters, not about which
+// side integrated. A third arm (Codex round 1: "movement in m alone does not
+// establish that the residual is the local clamp") fits the server with every
+// LA m HELD at the value the local engine effectively uses — its start
+// ROUNDED to an integer, as laTrueCasaXPS_array rounds it (Codex round 2) —
+// the one thing the local engine cannot move: if that arm agrees with the local engine where the
+// free-m arm did not, the attribution is established by a controlled
+// comparison, not inferred. Usage: node scripts/local_server_gap.js [out.json]
+const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
+const ROOT = path.join(__dirname, '..');
+const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
+function extractFn(name) {
+  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
+  if (start < 0) throw new Error('missing ' + name);
+  let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
+  throw new Error('unbalanced ' + name);
+}
+const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
+  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
+  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
+  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
+  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_applyBackendParams'];
+const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
+function makeEnv() {
+  const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
+  const document = { getElementById: el, querySelectorAll: () => [] };
+  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
+  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
+  const f = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
+    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, _applyBackendParams };');
+  return { ...f(document, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => new Array(be.length).fill(0)), state };
+}
+const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
+const PROJECT = path.join(ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
+const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
+const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 1 << 26 }));
+function target(env, sourceName, targetName) {
+  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
+  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
+  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
+  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
+  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
+  const be = [], inten = [];
+  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
+  const bg = env.computeBackgroundCore(be, inten, ui);
+  return { be, inten, bg, bgSub: inten.map((v, i) => v - bg[i]), ui, start: cloned };
+}
+const area = (env, be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return env.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
+const out = { generated: new Date().toISOString(), regions: {} };
+for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
+  const names = tabs.filter(t => new RegExp('^' + sourceName.replace(' ', ' ') + '_\\d+$').test(t.name)).map(t => t.name);
+  out.regions[region] = [];
+  for (const name of names) {
+    const env = makeEnv(); const T = target(env, sourceName, name);
+    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
+    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
+    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
+    const serverFit = startPeaks => {
+      const r = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: startPeaks, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
+      const peaks = JSON.parse(JSON.stringify(startPeaks));
+      r.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(peaks[i], par); });
+      return { r, peaks };
+    };
+    const { r: srv, peaks: serverPeaks } = serverFit(T.start);
+    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, caM: Math.round(p.caM || 0), fixCaM: true } : p);
+    const { r: srvHeld, peaks: serverHeldPeaks } = serverFit(heldStart);
+    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
+    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p)), aH = serverHeldPeaks.map(p => area(env, T.be, p));
+    const tL = aL.reduce((s, v) => s + v, 0), tS = aS.reduce((s, v) => s + v, 0), tH = aH.reduce((s, v) => s + v, 0);
+    const comps = localPeaks.map((p, i) => ({ name: p.name, shape: p.shape, linked: !!p.linked,
+      dCenter_meV: 1000 * (p.center - serverPeaks[i].center), dFwhm_pct: 100 * (p.fwhm / serverPeaks[i].fwhm - 1),
+      dArea_pct: aS[i] ? 100 * (aL[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aL[i] / tL - aS[i] / tS),
+      // the held-m arm: local vs server with every LA m held at its start
+      held_dCenter_meV: 1000 * (p.center - serverHeldPeaks[i].center), held_dFwhm_pct: 100 * (p.fwhm / serverHeldPeaks[i].fwhm - 1),
+      held_dArea_pct: aH[i] ? 100 * (aL[i] / aH[i] - 1) : null, held_dFrac_pp: 100 * (aL[i] / tL - aH[i] / tH),
+      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM },
+      server_held_m: { center: serverHeldPeaks[i].center, fwhm: serverHeldPeaks[i].fwhm, amplitude: serverHeldPeaks[i].amplitude, area: aH[i], caM: serverHeldPeaks[i].caM } }));
+    const mx = f => Math.max(...comps.map(c => Math.abs(c[f]) || 0));
+    out.regions[region].push({ target: name, local_success: loc.success, local_chi2r: env.state.fitResult && env.state.fitResult.chiReduced, server_success: srv.success, server_chi2r: srv.chi2r,
+      server_held_m_success: srvHeld.success, server_held_m_chi2r: srvHeld.chi2r,
+      max_dCenter_meV: mx('dCenter_meV'), max_dFwhm_pct: mx('dFwhm_pct'), max_dArea_pct: mx('dArea_pct'), max_dFrac_pp: mx('dFrac_pp'),
+      held_max_dCenter_meV: mx('held_dCenter_meV'), held_max_dFwhm_pct: mx('held_dFwhm_pct'), held_max_dArea_pct: mx('held_dArea_pct'), held_max_dFrac_pp: mx('held_dFrac_pp'), comps });
+    console.error(region, name, 'local', loc.success, (env.state.fitResult || {}).chiReduced && env.state.fitResult.chiReduced.toFixed(3), 'server', srv.success, srv.chi2r.toFixed(3), 'max Δcentre', mx('dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('dFwhm_pct').toFixed(2), '%, Δarea', mx('dArea_pct').toFixed(2), '%, Δfrac', mx('dFrac_pp').toFixed(2), 'pp',
+      '| m held: server', srvHeld.chi2r.toFixed(3), 'Δcentre', mx('held_dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('held_dFwhm_pct').toFixed(2), '%, Δarea', mx('held_dArea_pct').toFixed(2), '%, Δfrac', mx('held_dFrac_pp').toFixed(2), 'pp');
+  }
+}
+fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/local_server_gap.json'), JSON.stringify(out, null, 1));
diff --git a/scripts/voigt_saved_vs_refit.js b/scripts/voigt_saved_vs_refit.js
new file mode 100644
index 0000000..e79c90a
--- /dev/null
+++ b/scripts/voigt_saved_vs_refit.js
@@ -0,0 +1,79 @@
+#!/usr/bin/env node
+// A03 (Codex round 1): what a student SEES change when a saved project with
+// Voigt components is re-fitted under the fixed-eta request — measured with
+// the PAGE's own numbers on both sides. For every committed spectrum tab
+// that carries a saved fit and a Voigt component: the page's area of each
+// saved peak (evalPeakArray over the ROI grid × step, as _peakArea; a Voigt
+// at eta 0.5, an LA at its rounded m — exactly the Results table) versus the
+// page's area of the same peaks after the server refit (the page's request
+// builder, Trust-Region, the page's n_perturb 3, parameters written back
+// through the page's _applyBackendParams). Grids as the page holds them
+// (Codex rounds 2–3): the page keeps its DISPLAY grid (the corrected ROI
+// energies, unrounded — fitResult.be after Run Fit, the integration grid
+// of Results) apart from the UPLOAD it sends (energies 4 dp, intensities
+// 2 dp, uploadToBackend), and selects the background window on the display
+// grid (_bgWindowIndices) before uploading. So here: the SAVED side
+// integrates on the saved fit's own grid (fitResult.be; the display grid
+// only when a save lacks it), the REFIT side on the display grid; the
+// request carries the rounded arrays and the window indices chosen on the
+// display grid.
+// Usage: node scripts/voigt_saved_vs_refit.js [out.json]
+const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
+const ROOT = path.join(__dirname, '..');
+const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
+function extractFn(name) {
+  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
+  if (start < 0) throw new Error('missing ' + name);
+  let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
+  throw new Error('unbalanced ' + name);
+}
+const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS',
+  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
+const state = { peaks: [] };
+const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams, _bgWindowIndices };')(state);
+const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
+const DATA = path.join(ROOT, 'docs/autofit/test_data');
+const area = (be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return fns.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
+const out = { generated: new Date().toISOString(), n_perturb: 3, targets: [] };
+for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
+  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
+  for (const t of tabs) {
+    if (!t.fitResult || !(t.peaks || []).some(p => p.shape === 'Voigt')) continue;
+    const ui = t.ui || {};
+    const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
+    if (!Number.isFinite(roiMin) || !Number.isFinite(roiMax) || !ui.bgType) continue;
+    const be = [], inten = [];                       // the display grid and its intensities (getROIData)
+    t.rawBE.forEach((b, i) => { const c = b - (t.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(t.rawIntensity[i]); } });
+    if (be.length < 10) continue;
+    const upBe = be.map(v => +v.toFixed(4)), upInten = inten.map(v => +v.toFixed(2));   // what uploadToBackend sends
+    const bgWin = fns._bgWindowIndices(be, ui.bgStart, ui.bgEnd);                        // chosen on the display grid, as runFit does
+    const savedGrid = (t.fitResult.be && t.fitResult.be.length) ? t.fitResult.be : be;
+    const saved = JSON.parse(JSON.stringify(t.peaks));
+    let srv;
+    try {
+      srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: upBe, inten: upInten, peaks: saved, ui, n_perturb: 3, bg_idx: [bgWin.i0, bgWin.i1 + 1] }), encoding: 'utf8', maxBuffer: 1 << 26 }));
+    } catch (e) { out.targets.push({ project: zp, tab: t.name, error: String(e.message).slice(0, 200) }); continue; }
+    const refit = JSON.parse(JSON.stringify(saved));
+    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; fns._applyBackendParams(refit[i], par); });
+    const aS = saved.map(p => area(savedGrid, p)), aR = refit.map(p => area(be, p));
+    const tS = aS.reduce((s, v) => s + v, 0), tR = aR.reduce((s, v) => s + v, 0);
+    const comps = saved.map((p, i) => ({ name: p.name, shape: p.shape, saved_area: aS[i], refit_area: aR[i],
+      dArea_pct: aS[i] ? 100 * (aR[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aR[i] / tR - aS[i] / tS) }));
+    const rec = { project: zp, tab: t.name, server_success: srv.success, chi2r: srv.chi2r, saved_grid: t.fitResult.be && t.fitResult.be.length ? 'fitResult.be' : 'roi',
+      max_dFrac_pp: Math.max(...comps.map(c => Math.abs(c.dFrac_pp))),
+      max_voigt_dArea_pct: Math.max(...comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct))), comps };
+    out.targets.push(rec);
+    console.error(zp.slice(0, 28), t.name, 'server', srv.success, 'max Δfrac', rec.max_dFrac_pp.toFixed(2), 'pp, max Voigt Δarea', rec.max_voigt_dArea_pct.toFixed(1), '%');
+  }
+}
+const ok = out.targets.filter(r => r.server_success);
+const q = v => { v = [...v].sort((a, b) => a - b); return { median: v[Math.floor(v.length / 2)], p90: v[Math.floor(0.9 * (v.length - 1))], max: v[v.length - 1] }; };
+const voigtComps = ok.flatMap(r => r.comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct)));
+out.summary = { n_tabs: out.targets.length, n_converged: ok.length,
+  dFrac_pp: q(ok.map(r => r.max_dFrac_pp)),                           // per tab: the largest fraction move
+  gt_1pp: ok.filter(r => r.max_dFrac_pp > 1).length,
+  voigt_dArea_pct_tab_max: q(ok.map(r => r.max_voigt_dArea_pct)),     // per tab: the largest Voigt area change
+  voigt_dArea_pct_component: q(voigtComps), n_voigt_components: voigtComps.length };   // per component, all Voigts
+console.error(JSON.stringify(out.summary));
+fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/voigt_saved_vs_refit.json'), JSON.stringify(out, null, 1));
diff --git a/templates/index.html b/templates/index.html
index 8393b2c..f272259 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4162,8 +4162,10 @@ function evalPeak(x, p) {
   } else if (p.shape === 'Voigt') {
     y = pseudoVoigt(x, center, fwhm, 0.5);
   } else if (p.shape === 'DSG_LA') {
-    // laCasaXPS already returns a normalised [0,1] value
-    y = laCasaXPS(x, center, p.laAlpha, p.laBeta, p.laM);
+    // laCasaXPS already returns a normalised [0,1] value. α is clipped as
+    // the server clips it (_ds_g_dscore_gauss: 0 ≤ α ≤ 0.495) so a locked
+    // 0.5 is drawn as it is fitted (A03 Codex round 3: 0.9 % apart before).
+    y = laCasaXPS(x, center, _dsgAlpha(p.laAlpha), p.laBeta, p.laM);
   } else if (p.shape === 'LACX') {
     // Per-point fallback: m=0 base, ignores Gaussian conv. Chart series
     // build paths use laTrueCasaXPS_array via evalPeakArray.
@@ -4183,6 +4185,10 @@ function evalPeak(x, p) {
 // the analytic core value at eps=0 instead differs by ~1e-3 of amplitude
 // when the fitted center falls between grid points — the Codex run-A MAJOR
 // on the first cut of this fix. Pinned by tests/js/lineshape_parity.test.js.
+// The server's DS+G clips α to [0, 0.495] (_ds_g_dscore_gauss); the page
+// must evaluate the same α or a locked 0.5 is drawn 0.9 % from its fit.
+function _dsgAlpha(a) { return Math.min(Math.max(a, 0), 0.495); }
+
 function dsgDeltaKernel_array(beArr, center, alpha, beta) {
   const N = beArr.length;
   const core = new Array(N);
@@ -4234,7 +4240,7 @@ function evalPeakArray(beArr, p) {
     // (p.laM || 0): negative laM matches the backend's clamp-to-0-then-delta
     // path; NaN/undefined coerce to 0 → delta, which peakToBackendSpec's
     // non-finite→default sanitisation makes unreachable in fit flows.
-    const yArr = dsgDeltaKernel_array(beArr, p.center, p.laAlpha, p.laBeta);
+    const yArr = dsgDeltaKernel_array(beArr, p.center, _dsgAlpha(p.laAlpha), p.laBeta);
     const amp = p.amplitude;
     return yArr.map(v => amp * v);
   }
@@ -5962,7 +5968,7 @@ function renderPeakForm(p) {
       <select id="pk-shape-${p.id}" class="xps-tip-select" onchange="_switchPeakShape(${p.id}, this.value)">
         <option data-tip="Pure Gaussian. Dominated by instrument broadening. Rarely used alone — most XPS peaks need some Lorentzian character." ${p.shape==='Gaussian'?'selected':''}>Gaussian</option>
         <option data-tip="Pure Lorentzian. Dominated by core-hole lifetime. Rarely used alone — too sharp for most real XPS peaks." ${p.shape==='Lorentzian'?'selected':''}>Lorentzian</option>
-        <option data-tip="50/50 Gaussian-Lorentzian mix. Good default starting point for most insulating and polymeric samples." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
+        <option data-tip="Fixed 50/50 Gaussian-Lorentzian mix (η = 0.5, not fitted). A reasonable default for most insulating and polymeric samples; choose GL to fit the mix." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
         <option value="GL" data-tip="Adjustable Gaussian/Lorentzian ratio. Use when you need control over the peak shape — common for oxides, polymers, and organic materials." ${p.shape==='GL'?'selected':''}>GL pseudo-Voigt (&eta; mixing)</option>
         <option value="asym-GL" data-tip="GL with asymmetric broadening. Use for peaks with vibrational fine structure (e.g., C 1s in polymers) or when one side is broader than the other." ${p.shape==='asym-GL'?'selected':''}>Asymmetric GL</option>
         <option value="DS" data-tip="Asymmetric metallic lineshape with tail toward higher BE. Use for metals and conductive samples (e.g., Au, Cu, Fe metal). Not appropriate for insulators or oxides." ${p.shape==='DS'?'selected':''}>Doniach-&Scaron;unji&#263; (&alpha; + &gamma;)</option>
@@ -6223,15 +6229,28 @@ function peakToBackendSpec(p) {
   } else if (shape === 'Lorentzian') {
     spec.shape = 'lorentzian';
   } else if (shape === 'Voigt') {
+    // A03 (2026-09-22): Voigt IS the fixed 50/50 mix the page draws, exports
+    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
+    // the request sent eta FREE from 0.3, so the server fitted a mix the page
+    // never showed — on the 90 committed Voigt targets 60 of 180 components
+    // went to pure Gaussian and 16 to pure Lorentzian, and every area the page
+    // reported for them was the 0.5 curve's, up to 20 % off the fitted one.
+    // Fixed on both sides; use GL to fit the mix.
     spec.shape = 'pseudo_voigt_gl';
-    spec.gl_ratio = 0.3;
+    spec.gl_ratio = 0.5;
+    spec.fix_gl_ratio = true;
   } else if (shape === 'GL') {
     spec.shape = 'pseudo_voigt_gl';
     spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
   } else if (shape === 'asym-GL') {
     spec.shape = 'asymmetric_gl';
-    spec.gl_ratio = (p.glMix || 50) / 100;
-    spec.asymmetry = p.asymmetry || 0;
+    // A03 Codex round 1: `p.glMix || 50` sent a mix of 0 as 50 (and a DS α of 0
+    // as 0.1 below) — a value the page draws but never requested; locked, the
+    // server held the substitute and the drawn curve differed from the fitted
+    // one by 6.9 % (asym-GL) and 8.8 % (DS) of amplitude. Only a NON-NUMBER
+    // falls back to the default.
+    spec.gl_ratio = (Number.isFinite(p.glMix) ? p.glMix : 50) / 100;
+    spec.asymmetry = Number.isFinite(p.asymmetry) ? p.asymmetry : 0;
     spec.fix_asymmetry = !!p.fixAsymmetry;
     // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
     // For non-auto-fit peaks these fields are absent and the backend falls back
@@ -6240,8 +6259,8 @@ function peakToBackendSpec(p) {
     if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
   } else if (shape === 'DS') {
     spec.shape = 'doniach_sunjic';
-    spec.alpha      = p.dsAlpha || 0.1;
-    spec.gamma_asym = p.dsGamma || 0.0;
+    spec.alpha      = Number.isFinite(p.dsAlpha) ? p.dsAlpha : 0.1;
+    spec.gamma_asym = Number.isFinite(p.dsGamma) ? p.dsGamma : 0.0;
     spec.fix_alpha      = !!p.fixDsAlpha;
     spec.fix_gamma_asym = !!p.fixDsGamma;
   } else if (shape === 'DSG_LA') {
@@ -6282,7 +6301,10 @@ function _applyBackendParams(p, par) {
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
@@ -7780,9 +7802,15 @@ function _fitStatLabel(fr) {
 // A LOCAL result is a STARTING POINT, not a reportable result. Measured in
 // unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
 // with Poisson weighting the local engine matches the server on GL-type
-// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) but still differs
-// where the model has Voigt or LA components (server fits the Voigt mix
-// free; caM is integer-held locally) or several minima, and it gives no
+// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
+// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
+// wherever the two engines reach the same minimum (5 of 9 committed U 4f
+// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
+// it still differs on the other 4 U 4f targets (satellite areas up to
+// 8.9 %, 0.77 pp): on one because the LA m is held at its start locally
+// (the gap closes when the server holds m too), on three because the local
+// descent stops at a higher chi2r than the server from the same start
+// (+5 to +13 %, with m held as well) - several minima - and it gives no
 // uncertainties. Unweighted A0-era results differed by more than 100 %.
 // Every site that shows, exports or saves a fit result carries the
 // designation, keyed on persisted identity so reloaded results are labelled.
@@ -7802,7 +7830,7 @@ function _governingProvenance() {
 function _localFitDetail(fr) {
   return _isUnweightedLocal(fr)
     ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
-    : 'It can differ from the server fit for Voigt or LA components, for very weak components (different parameter bounds), or where the model has several minima.';
+    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
 }
 // The designation follows the MODEL, not only a live fit result: parameters
 // imported from a .fit.json that was saved from a local fit are a starting
@@ -11248,7 +11276,7 @@ function _updateROIDisplay(roiRange) {
   el.textContent = `ROI: ${roiRange.min}\u2013${roiRange.max} eV`;
 }
 
-const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for Voigt or LA components or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
+const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
 const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the goodness of fit weighted by data uncertainty. Computed within the ROI range.\n\n\u2022 \u03c7\u00b2 \u2248 1.0 = ideal fit (residuals match expected noise)\n\u2022 \u03c7\u00b2 >> 1 = poor fit or underestimated uncertainties\n\u2022 \u03c7\u00b2 << 1 = possible overfitting or overestimated uncertainties\n\nNote: a low \u03c7\u00b2 does not guarantee a correct model \u2014 always check the R-factor and visually inspect residuals.";
 
 // Wire up custom tooltip for data-xps-tip elements (R-factor, chi-squared, etc.)
@@ -11323,6 +11351,11 @@ function _validateUncertainties() {
       //     by construction → silent
       //   - genuinely locked (vary=false, no expr): user or auto-fit set this lock
       //     → neutral info note pointing at the padlock toggle, not an alarm
+      if (pName === 'gl_ratio' && p.shape === 'Voigt') {
+        // A03: a Voigt's mix is fixed by the SHAPE (η = 0.5), not by a padlock — there is none to unlock.
+        info.push(`<li><b>${_escHtml(p.name)} / mix:</b> fixed at 50/50 by the Voigt shape — choose GL to fit the mix.</li>`);
+        continue;
+      }
       if (pData.vary === false) {
         const isLinked = pData.expr != null && pData.expr !== '';
         if (!isLinked) {
@@ -14283,7 +14316,7 @@ document.addEventListener('mousedown', function(e) {
 <div id="localfit-warn-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
   <div class="xps-modal" style="max-width:460px;border-color:var(--amber,#f59e0b)">
     <h3 style="color:var(--amber,#f59e0b)">&#9888; Local fit used (server unreachable) <button class="btn btn-sm" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">&#x2715;</button></h3>
-    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for Voigt or LA components or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
+    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
     <p style="font-size:11px;color:var(--text2);line-height:1.6;margin:0 0 12px"><strong style="color:var(--text)">Possible causes:</strong><br>
     &bull; The server may be offline or restarting<br>
     &bull; The fit request may have timed out<br>
diff --git a/tests/js/lineshape_parity.test.js b/tests/js/lineshape_parity.test.js
index d9ca8ec..eea6493 100644
--- a/tests/js/lineshape_parity.test.js
+++ b/tests/js/lineshape_parity.test.js
@@ -296,3 +296,99 @@ test('(C) evalPeak() has no direct callers outside evalPeakArray()', () => {
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
+// fwhm 0.1–15) — what the OPTIMISER can reach. A lock can hold a value
+// outside them (a held value is honoured as requested since A03 round 2;
+// the round-trip harness covers those), a link follows its parent.
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
+// The backend parameters of the sweep come from the PAGE's request builder,
+// not from a mapping of this file's own (Codex round 1: a mapping written
+// here could not see `p.glMix || 50` sending an asym-GL mix of 0 as 50).
+const _specState = { peaks: [] };
+const { peakToBackendSpec } = new Function('state', 'getPeak',
+  extract(/function peakToBackendSpec\(p\) \{[\s\S]*?\n\}\n/, 'peakToBackendSpec definition') + '\nreturn { peakToBackendSpec };')(_specState, id => _specState.peaks.find(q => q.id === id));
+function backendParamsFromRequest(p) {
+  const spec = peakToBackendSpec(p);
+  const keep = spec.shape === 'ds_g' ? ['amplitude', 'center', 'alpha', 'beta', 'm_gauss']
+    : ['amplitude', 'center', 'fwhm', 'gl_ratio', 'asymmetry', 'alpha', 'gamma_asym', 'beta', 'm'];
+  const params = {};
+  for (const k of keep) if (k in spec) params[k] = spec[k];
+  return { shape: spec.shape, params };
+}
+function runSweep(label, ranges) {
+  const shape = sweepShape(label);
+  const cases = combos(ranges).map(c => ({ c, p: { ...basePeak(shape), ...c } }));
+  const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: grid(k.p.center) }; });
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
2367:  const snap = JSON.parse(JSON.stringify(state.peaks));
2378:  tab.modelProvenance = snap._modelProvenance ? JSON.parse(JSON.stringify(snap._modelProvenance)) : null;
2405:  const snap = JSON.parse(JSON.stringify(tab.peaks || []));
3222:    this._syncActiveToRecord();
3231:    state.fitResult = tab.fitResult;
3297:      state.peaks = []; state.fitResult = null;
3357:    this._syncActiveToRecord();
3419:      state.fitResult = null;
3422:      active.fitResult = null;
3800:  _syncActiveToRecord() {
3809:    t.fitResult = state.fitResult;
5083:// peakToBackendSpec / applyBackendResult / runFit per the checklist in
5725:  state.fitResult = null;
6319:function applyBackendResult(result) {
6326:    p._backendParams = ipeak.params;
6744:    peaks:        JSON.parse(JSON.stringify(state.peaks || [])),
6751:    manualAnchors: JSON.parse(JSON.stringify(_getManualAnchors())),
6752:    modelProvenance: (() => { const o = _opOwner(); return o && o.modelProvenance ? JSON.parse(JSON.stringify(o.modelProvenance)) : null; })(),
6787:    t.fitResult = snap.fitResult;
6799:  state.fitResult = snap.fitResult;
7109:  state.fitResult = {
7114:    fittedY: json.fitted_y,
7147:  if (typeof tabManager !== 'undefined' && tabManager._syncActiveToRecord) {
7148:    tabManager._syncActiveToRecord();
7217:  state.fitResult = null;
7279:      body: JSON.stringify({
7303:    applyBackendResult(json);
7386:  return JSON.stringify({
7398:// The key of a tab RECORD (project save runs after _syncActiveToRecord).
7550:  const peaks = JSON.parse(JSON.stringify(state.peaks));
7680:        body: JSON.stringify(fitReq)
7732:    applyBackendResult(backendResult);
7738:    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
7740:                        fittedY: backendResult.fitted_y, roiRange, _preFit,
7875:  if (tab.modelProvenance) return JSON.parse(JSON.stringify(tab.modelProvenance));
8234:    // A local fit has no backend covariance; any _backendParams on the peak
8237:    delete live._backendParams;
8267:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
8748:    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
8753:    return { be: [], bg: [], rawY: [], fittedY: [], peaks: [] };
9910:function saveFit() {
9917:function saveSpectrum() {
9933:  tabManager._syncActiveToRecord();
9979:    new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
9987:  tabManager._syncActiveToRecord();
10046:    fittedY: fittedY,
10057:    new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
10065:  tabManager._syncActiveToRecord();
10105:        rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
10144:    // like _backendParams/_confidence), never this namespace.
10166:      new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
10174:      zip.file(zname, JSON.stringify(buildTabData(t), null, 2));
10177:    zip.file('manifest.json', JSON.stringify(manifest, null, 2));
10344:    active.fitResult = fr;
10345:    state.fitResult = fr;
10383:      notify('Project not loaded: tab id ' + JSON.stringify(t.id).slice(0, 60)
10391:          notify('Project not loaded: stack-entry id ' + JSON.stringify(e.id).slice(0, 60)
10397:          notify('Project not loaded: stack-entry color ' + JSON.stringify(e.color).slice(0, 60)
11791:  tabManager._syncActiveToRecord();
11815:  const srcPeaks = JSON.parse(JSON.stringify(sourceTab.peaks || []));
11859:    tgt.fitResult = null;
11869:      state.fitResult = null;   // live copy of tgt.fitResult = null above (unit A0)
11893:    tabManager._syncActiveToRecord();
12372:    localStorage.setItem(REF_PALETTE_LS, JSON.stringify({ ...(_refLoadPaletteState() || {}), ...patch }));
13657:    peaks: JSON.parse(JSON.stringify(state.peaks)),
13663:      fittedY: state.fitResult.fittedY ? [...state.fitResult.fittedY] : null,
13752:    return 'peak id ' + JSON.stringify(p.id) + ' is not a non-negative integer';
13754:    return 'peak link target ' + JSON.stringify(p.linked) + ' is not a valid peak id';
13757:    return 'peak color ' + JSON.stringify(p.color) + ' is not a valid hex color';
13806:  state.peaks = _normalizePeaksCRef(JSON.parse(JSON.stringify(snap.peaks)));
13807:  state.fitResult = snap.fitResult ? { ...snap.fitResult } : null;
13809:  tabManager._syncActiveToRecord();
15332:  document.getElementById('fp-options').value = JSON.stringify(shown, null, 1);
15400:  document.getElementById('fp-options').value = JSON.stringify(opts, null, 1);
15487:                         ENDPOINT_AVG_MAX + ' (got ' + JSON.stringify(options.endpoint_avg) + ').';
15522:      body: JSON.stringify(payload),
15797:    state.fitResult = null;
15820:    // state.fitResult === null correctly (falls back to its own

exec
/bin/zsh -lc "cat scripts/voigt_saved_vs_refit.js; cat docs/findings/a03/voigt_saved_vs_refit.log; cat docs/findings/a03/voigt_eta_summary.txt; sed -n '1,160p' tests/autofit/test_b1s_cl2p_batteries.py; sed -n '1,120p' tests/autofit/test_u4f_parity_battery.py; sed -n '1,110p' tests/autofit/test_c1s_parity_battery.py; ls -d venv /Users/skyefortier/xps-app/venv" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 0ms:
#!/usr/bin/env node
// A03 (Codex round 1): what a student SEES change when a saved project with
// Voigt components is re-fitted under the fixed-eta request — measured with
// the PAGE's own numbers on both sides. For every committed spectrum tab
// that carries a saved fit and a Voigt component: the page's area of each
// saved peak (evalPeakArray over the ROI grid × step, as _peakArea; a Voigt
// at eta 0.5, an LA at its rounded m — exactly the Results table) versus the
// page's area of the same peaks after the server refit (the page's request
// builder, Trust-Region, the page's n_perturb 3, parameters written back
// through the page's _applyBackendParams). Grids as the page holds them
// (Codex rounds 2–3): the page keeps its DISPLAY grid (the corrected ROI
// energies, unrounded — fitResult.be after Run Fit, the integration grid
// of Results) apart from the UPLOAD it sends (energies 4 dp, intensities
// 2 dp, uploadToBackend), and selects the background window on the display
// grid (_bgWindowIndices) before uploading. So here: the SAVED side
// integrates on the saved fit's own grid (fitResult.be; the display grid
// only when a save lacks it), the REFIT side on the display grid; the
// request carries the rounded arrays and the window indices chosen on the
// display grid.
// Usage: node scripts/voigt_saved_vs_refit.js [out.json]
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
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS',
  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
const state = { peaks: [] };
const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams, _bgWindowIndices };')(state);
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const DATA = path.join(ROOT, 'docs/autofit/test_data');
const area = (be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return fns.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), n_perturb: 3, targets: [] };
for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
  for (const t of tabs) {
    if (!t.fitResult || !(t.peaks || []).some(p => p.shape === 'Voigt')) continue;
    const ui = t.ui || {};
    const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
    if (!Number.isFinite(roiMin) || !Number.isFinite(roiMax) || !ui.bgType) continue;
    const be = [], inten = [];                       // the display grid and its intensities (getROIData)
    t.rawBE.forEach((b, i) => { const c = b - (t.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(t.rawIntensity[i]); } });
    if (be.length < 10) continue;
    const upBe = be.map(v => +v.toFixed(4)), upInten = inten.map(v => +v.toFixed(2));   // what uploadToBackend sends
    const bgWin = fns._bgWindowIndices(be, ui.bgStart, ui.bgEnd);                        // chosen on the display grid, as runFit does
    const savedGrid = (t.fitResult.be && t.fitResult.be.length) ? t.fitResult.be : be;
    const saved = JSON.parse(JSON.stringify(t.peaks));
    let srv;
    try {
      srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: upBe, inten: upInten, peaks: saved, ui, n_perturb: 3, bg_idx: [bgWin.i0, bgWin.i1 + 1] }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    } catch (e) { out.targets.push({ project: zp, tab: t.name, error: String(e.message).slice(0, 200) }); continue; }
    const refit = JSON.parse(JSON.stringify(saved));
    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; fns._applyBackendParams(refit[i], par); });
    const aS = saved.map(p => area(savedGrid, p)), aR = refit.map(p => area(be, p));
    const tS = aS.reduce((s, v) => s + v, 0), tR = aR.reduce((s, v) => s + v, 0);
    const comps = saved.map((p, i) => ({ name: p.name, shape: p.shape, saved_area: aS[i], refit_area: aR[i],
      dArea_pct: aS[i] ? 100 * (aR[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aR[i] / tR - aS[i] / tS) }));
    const rec = { project: zp, tab: t.name, server_success: srv.success, chi2r: srv.chi2r, saved_grid: t.fitResult.be && t.fitResult.be.length ? 'fitResult.be' : 'roi',
      max_dFrac_pp: Math.max(...comps.map(c => Math.abs(c.dFrac_pp))),
      max_voigt_dArea_pct: Math.max(...comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct))), comps };
    out.targets.push(rec);
    console.error(zp.slice(0, 28), t.name, 'server', srv.success, 'max Δfrac', rec.max_dFrac_pp.toFixed(2), 'pp, max Voigt Δarea', rec.max_voigt_dArea_pct.toFixed(1), '%');
  }
}
const ok = out.targets.filter(r => r.server_success);
const q = v => { v = [...v].sort((a, b) => a - b); return { median: v[Math.floor(v.length / 2)], p90: v[Math.floor(0.9 * (v.length - 1))], max: v[v.length - 1] }; };
const voigtComps = ok.flatMap(r => r.comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct)));
out.summary = { n_tabs: out.targets.length, n_converged: ok.length,
  dFrac_pp: q(ok.map(r => r.max_dFrac_pp)),                           // per tab: the largest fraction move
  gt_1pp: ok.filter(r => r.max_dFrac_pp > 1).length,
  voigt_dArea_pct_tab_max: q(ok.map(r => r.max_voigt_dArea_pct)),     // per tab: the largest Voigt area change
  voigt_dArea_pct_component: q(voigtComps), n_voigt_components: voigtComps.length };   // per component, all Voigts
console.error(JSON.stringify(out.summary));
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/voigt_saved_vs_refit.json'), JSON.stringify(out, null, 1));
1-GTA UCl4-graphite one set  U4f Scan server true max Δfrac 0.39 pp, max Voigt Δarea 5.1 %
1-GTA UCl4-graphite one set  U4f Scan_0 server true max Δfrac 0.31 pp, max Voigt Δarea 5.9 %
1-GTA UCl4-graphite one set  U4f Scan_1 server true max Δfrac 0.37 pp, max Voigt Δarea 2.8 %
1-GTA UCl4-graphite one set  U4f Scan_2 server true max Δfrac 0.20 pp, max Voigt Δarea 2.7 %
1-GTA UCl4-graphite one set  U4f Scan_3 server true max Δfrac 0.36 pp, max Voigt Δarea 4.5 %
1-GTA UCl4-graphite one set  U4f Scan_4 server true max Δfrac 0.63 pp, max Voigt Δarea 15.3 %
1-GTA UCl4-graphite one set  U4f Scan_5 server true max Δfrac 0.24 pp, max Voigt Δarea 3.2 %
1-GTA UCl4-graphite one set  U4f Scan_6 server true max Δfrac 0.24 pp, max Voigt Δarea 3.8 %
1-GTA UCl4-graphite one set  U4f Scan_7 server true max Δfrac 0.16 pp, max Voigt Δarea 3.4 %
1-GTA UCl4-graphite one set  U4f Scan_8 server true max Δfrac 0.27 pp, max Voigt Δarea 5.0 %
4-GTA UCl4-BN.proj.zip U4f Scan server true max Δfrac 0.04 pp, max Voigt Δarea 0.6 %
4-GTA UCl4-BN.proj.zip U4f Scan_0 server true max Δfrac 0.19 pp, max Voigt Δarea 0.0 %
4-GTA UCl4-BN.proj.zip U4f Scan_1 server true max Δfrac 0.18 pp, max Voigt Δarea 0.0 %
4-GTA UCl4-BN.proj.zip U4f Scan_2 server true max Δfrac 0.50 pp, max Voigt Δarea 4.7 %
4-GTA UCl4-BN.proj.zip U4f Scan_3 server true max Δfrac 0.59 pp, max Voigt Δarea 6.0 %
4-GTA UCl4-BN.proj.zip U4f Scan_4 server true max Δfrac 0.06 pp, max Voigt Δarea 0.7 %
4-GTA UCl4-BN.proj.zip U4f Scan_5 server true max Δfrac 0.49 pp, max Voigt Δarea 3.3 %
4-GTA UCl4-BN.proj.zip U4f Scan_6 server true max Δfrac 0.25 pp, max Voigt Δarea 2.4 %
4-GTA UCl4-BN.proj.zip U4f Scan_7 server true max Δfrac 0.35 pp, max Voigt Δarea 2.9 %
4-GTA UCl4-BN.proj.zip U4f Scan_8 server true max Δfrac 0.27 pp, max Voigt Δarea 2.5 %
B4C-UCl4.proj.zip U4f Scan server true max Δfrac 0.40 pp, max Voigt Δarea 4.7 %
B4C-UCl4.proj.zip U4f Scan_0 server true max Δfrac 0.53 pp, max Voigt Δarea 4.5 %
B4C-UCl4.proj.zip U4f Scan_1 server true max Δfrac 0.43 pp, max Voigt Δarea 4.5 %
B4C-UCl4.proj.zip U4f Scan_2 server true max Δfrac 0.69 pp, max Voigt Δarea 8.5 %
B4C-UCl4.proj.zip U4f Scan_3 server true max Δfrac 0.40 pp, max Voigt Δarea 4.8 %
B4C-UCl4.proj.zip U4f Scan_4 server true max Δfrac 0.51 pp, max Voigt Δarea 5.0 %
B4C-UCl4.proj.zip U4f Scan_5 server true max Δfrac 0.37 pp, max Voigt Δarea 4.4 %
B4C-UCl4.proj.zip U4f Scan_6 server true max Δfrac 0.48 pp, max Voigt Δarea 4.6 %
B4C-UCl4.proj.zip U4f Scan_7 server true max Δfrac 0.25 pp, max Voigt Δarea 3.2 %
B4C-UCl4.proj.zip U4f Scan_8 server true max Δfrac 0.33 pp, max Voigt Δarea 5.0 %
Cl2p_projfit_test.proj.zip U4f Scan server true max Δfrac 0.45 pp, max Voigt Δarea 7.9 %
Cl2p_projfit_test.proj.zip U4f Scan_0 server true max Δfrac 0.41 pp, max Voigt Δarea 5.5 %
Cl2p_projfit_test.proj.zip U4f Scan_1 server true max Δfrac 0.26 pp, max Voigt Δarea 3.5 %
Cl2p_projfit_test.proj.zip U4f Scan_2 server true max Δfrac 0.33 pp, max Voigt Δarea 5.0 %
Cl2p_projfit_test.proj.zip U4f Scan_3 server true max Δfrac 0.41 pp, max Voigt Δarea 7.5 %
Cl2p_projfit_test.proj.zip U4f Scan_4 server true max Δfrac 0.27 pp, max Voigt Δarea 4.1 %
Cl2p_projfit_test.proj.zip U4f Scan_5 server true max Δfrac 0.39 pp, max Voigt Δarea 6.0 %
Cl2p_projfit_test.proj.zip Cl2p Scan_1 server true max Δfrac 0.00 pp, max Voigt Δarea 7.6 %
Project9_CasaXPS_newfit.proj U4f Scan server true max Δfrac 0.45 pp, max Voigt Δarea 7.9 %
Project9_CasaXPS_newfit.proj U4f Scan_0 server true max Δfrac 0.41 pp, max Voigt Δarea 5.5 %
Project9_CasaXPS_newfit.proj U4f Scan_1 server true max Δfrac 0.26 pp, max Voigt Δarea 3.5 %
Project9_CasaXPS_newfit.proj U4f Scan_2 server true max Δfrac 0.33 pp, max Voigt Δarea 5.0 %
Project9_CasaXPS_newfit.proj U4f Scan_3 server true max Δfrac 0.41 pp, max Voigt Δarea 7.5 %
Project9_CasaXPS_newfit.proj U4f Scan_4 server true max Δfrac 0.27 pp, max Voigt Δarea 4.1 %
Project9_CasaXPS_newfit.proj U4f Scan_5 server true max Δfrac 0.39 pp, max Voigt Δarea 6.0 %
UCl4_on_graphite.proj.zip U4f Scan server true max Δfrac 0.44 pp, max Voigt Δarea 5.1 %
UCl4_on_graphite.proj.zip U4f Scan_0 server true max Δfrac 0.31 pp, max Voigt Δarea 5.9 %
UCl4_on_graphite.proj.zip U4f Scan_1 server true max Δfrac 0.39 pp, max Voigt Δarea 3.0 %
UCl4_on_graphite.proj.zip U4f Scan_2 server true max Δfrac 0.56 pp, max Voigt Δarea 8.4 %
UCl4_on_graphite.proj.zip U4f Scan_3 server true max Δfrac 0.36 pp, max Voigt Δarea 4.5 %
UCl4_on_graphite.proj.zip U4f Scan_4 server true max Δfrac 0.59 pp, max Voigt Δarea 15.1 %
UCl4_on_graphite.proj.zip U4f Scan_5 server true max Δfrac 0.24 pp, max Voigt Δarea 3.2 %
UCl4_on_graphite.proj.zip U4f Scan_6 server true max Δfrac 0.24 pp, max Voigt Δarea 3.7 %
UCl4_on_graphite.proj.zip U4f Scan_7 server true max Δfrac 0.13 pp, max Voigt Δarea 2.5 %
UCl4_on_graphite.proj.zip U4f Scan_8 server true max Δfrac 0.27 pp, max Voigt Δarea 5.0 %
{"n_tabs":55,"n_converged":55,"dFrac_pp":{"median":0.3640215087774637,"p90":0.5078511773600608,"max":0.6882978905471321},"gt_1pp":0,"voigt_dArea_pct_tab_max":{"median":4.576983178447858,"p90":7.556793905528403,"max":15.30072477001817},"voigt_dArea_pct_component":{"median":3.2748648211409437,"p90":5.981860444395726,"max":15.30072477001817},"n_voigt_components":110}
targets 90, both fits converged 90
free eta of 180 Voigt components: 60 at 0 (pure Gaussian), 16 at 1 (pure Lorentzian), 24 within 0.4–0.6
per-Voigt-component DISPLAYED area vs the fitted curve (%): median 13.89, p90 19.18, max 20.11; > 10 % on 116 of 180; displayed high (eta < 0.5) 110, low 70
A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.48, max 1.55; > 1 pp on 35 targets
B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: median 0.34, p90 0.54, max 1.02; > 1 pp on 1 targets
C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 33 targets
chi2r fixed/free: median 1.09, p90 1.19, max 5.39; fixed lower on 10 targets (the free fit in a worse minimum)
"""
B 1s and Cl 2p characterization batteries (manual fit path; shared logic in
battery_common.py).  Small rosters — the labeled sets are small (B 1s: 4
eligible incl. 3 known-rough 4-GTA tabs, still valid as numeric pins;
Cl 2p: 3, incl. the uncorrected Scan_1).

Regenerate fixtures ONLY for reviewed numerics changes:
    venv/bin/python scripts/gen_region_battery_fixture.py "B 1s" b1s_battery_expected.json
    venv/bin/python scripts/gen_region_battery_fixture.py "Cl 2p" cl2p_battery_expected.json

A03 (2026-09-22): Cl2p Scan_1 is two Voigt lines saved under the old request
(eta free, written back as glMix 15.7); the page now requests eta = 0.5, so
its eval parity holds with the saved mix (battery_common.assert_eval_parity)
and its refit is a fixed point only of a refit FROM the refit
(stationarity="refit", as the U 4f battery). The Cl 2p fixture was
regenerated for that reviewed change; B 1s is untouched.
"""

import pytest

import battery_common as bc

_B1S = bc.battery_fits("B 1s")
_B1S_EXPECTED = bc.load_fixture("b1s_battery_expected.json")
_CL2P = bc.battery_fits("Cl 2p")
_CL2P_EXPECTED = bc.load_fixture("cl2p_battery_expected.json")

# Cl 2p eval parity is bounded by the same bg-anchor drift documented in
# battery_common.py (measured: 1.7e-2 on the uncorrected Scan_1 tab;
# ≤6.8e-7 on the corrected tabs).
CL2P_EVAL_TOL = 2.5e-2


def test_b1s_roster():
    bc.assert_roster(_B1S, _B1S_EXPECTED, min_size=3, min_projects=2,
                     gen_script="scripts/gen_region_battery_fixture.py 'B 1s'")


def test_cl2p_roster():
    bc.assert_roster(_CL2P, _CL2P_EXPECTED, min_size=2, min_projects=1,
                     gen_script="scripts/gen_region_battery_fixture.py 'Cl 2p'")


@pytest.mark.parametrize("rf", _B1S, ids=[f"{r.project}::{r.name}" for r in _B1S])
def test_b1s_eval_parity(rf):
    bc.assert_eval_parity(rf)


@pytest.mark.parametrize("rf", _B1S, ids=[f"{r.project}::{r.name}" for r in _B1S])
def test_b1s_refit_stability_and_fixture(rf):
    bc.assert_refit_stability_and_fixture(rf, _B1S_EXPECTED)


@pytest.mark.parametrize("rf", _CL2P, ids=[f"{r.project}::{r.name}" for r in _CL2P])
def test_cl2p_eval_parity(rf):
    bc.assert_eval_parity(rf, tol=CL2P_EVAL_TOL)


@pytest.mark.parametrize("rf", _CL2P, ids=[f"{r.project}::{r.name}" for r in _CL2P])
def test_cl2p_refit_stability_and_fixture(rf):
    bc.assert_refit_stability_and_fixture(rf, _CL2P_EXPECTED, stationarity="refit")
"""
U 4f characterization battery — pins the MANUAL fit path's LACX + linked
spin-orbit doublet + Voigt satellite numerics against 29 expert reference
fits (structure mirrors test_c1s_parity_battery.py; shared logic in
battery_common.py).

Regenerate the fixture ONLY for reviewed numerics changes:
    venv/bin/python scripts/gen_u4f_battery_fixture.py

A03 (2026-09-22): the page now sends a Voigt with eta HELD at 0.5 (the mix
it has always drawn); the 29 expert U 4f fits were saved under the old
request (eta free from 0.3, ending at pure Gaussian or pure Lorentzian on
most satellites), so their saved parameters belong to another model and a
refit under today's request moves the LACX main line's width by up to 7.7 %
and its centre by up to 8 meV (the satellites' tails changed). The fixture
was regenerated for that reviewed change, and stationarity is measured
against a refit FROM the refit (battery_common, stationarity="refit"): the
fitter's own fixed point, not the pre-A03 save.
"""

import pytest

import battery_common as bc

REGION = "U 4f"
FIXTURE = "u4f_battery_expected.json"
MIN_BATTERY_SIZE = 20
MIN_PROJECTS = 3
# Bounded by background-anchor drift / LACX FP wobble — measured and
# documented in battery_common.py.  The worst LACX tab (UCl4_on_graphite
# U4f Scan_6, a flat alpha/beta/m valley) wobbles at 1.4e-4 relative
# across PROCESSES on one platform, but 1.9e-3 across PLATFORMS (first CI
# run on ubuntu/openBLAS vs the macOS/arm64 fixture, 2026-07-04 — fwhm
# 3.00971 vs frozen 3.00396 on that tab).  3e-3 covers the measured
# cross-platform wobble with ~1.6x headroom while still catching any real
# numerics change (C 1s pins the shared machinery at 1e-6).
# Eval-parity across all 29 eligible fits: median 6.0e-3, max 1.12e-2
# (bg-anchor drift) — 1.5e-2 keeps ~34% headroom without masking a real
# 2%-level regression (Codex Stage-3 finding #4).
EVAL_TOL = 1.5e-2
FIXTURE_RTOL = 3e-3

_FITS = bc.battery_fits(REGION)
_IDS = [f"{rf.project}::{rf.name}" for rf in _FITS]
_EXPECTED = bc.load_fixture(FIXTURE)


def test_battery_roster():
    bc.assert_roster(_FITS, _EXPECTED, MIN_BATTERY_SIZE, MIN_PROJECTS,
                     "scripts/gen_u4f_battery_fixture.py")


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_eval_parity(rf):
    bc.assert_eval_parity(rf, tol=EVAL_TOL)


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_refit_stability_and_fixture(rf):
    bc.assert_refit_stability_and_fixture(rf, _EXPECTED,
                                          fixture_rtol=FIXTURE_RTOL,
                                          stationarity="refit")
"""
C 1s characterization battery — the Stage-2 parity / regression safety net.

Anchors (docs/autofit/phase1-grammar-architecture-spec-v2.md §3.1): the
expert C 1s fits in docs/autofit/test_data are the parity reference for the
autofit engine, and the seeded-refit records frozen in
fixtures/c1s_battery_expected.json pin today's ``fitting.run_fit`` numerics
so any unintentional change to the manual-fit path fails here first.

Three layers:

1. ``test_eval_parity_*`` — evaluating the saved peak params through
   fitting.py's lineshapes + run_fit's background reconstruction reproduces
   the saved ``fitResult.fittedY`` to ≤ 1e-5 relative (measured headroom:
   worst case 1.2e-7 across all 30 eligible fits).
2. ``test_refit_stability_*`` — a seeded, deterministic refit (leastsq,
   n_perturb=0) stays at the expert minimum: center drift ≤ 5 meV,
   FWHM/amplitude relative drift ≤ 0.5% (measured worst case: 2e-4).
3. ``test_battery_fixture_*`` — the same refit reproduces the frozen
   fixture records (χ²ᵣ, per-peak center/fwhm/amplitude/area) to tight
   tolerance.  Regenerate the fixture ONLY for reviewed, intentional
   numerics changes: ``venv/bin/python scripts/gen_c1s_battery_fixture.py``.

Tabs whose fit-time frame drifted from the saved ui state (charge correction
adjusted after fitting) and legacy saves without ``fitResult.be`` are
excluded by the same rules the generator applies, so fixture and battery
always agree on the roster.
"""

import glob
import json
import os

import numpy as np
import pytest

from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")
FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "c1s_battery_expected.json")

EVAL_PARITY_TOL = 1e-5          # measured worst case 1.2e-7
CENTER_DRIFT_TOL_EV = 0.005     # measured worst case 2e-4 eV
REL_DRIFT_TOL = 0.005           # FWHM / amplitude, measured worst case 1e-4
FIXTURE_CHI_RTOL = 1e-6
FIXTURE_PARAM_RTOL = 1e-6
MIN_BATTERY_SIZE = 25           # roster shrinking silently = data loss — fail


def _battery_fits():
    fits = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            if battery_eligible(rf, region="C 1s")[0]:
                fits.append(rf)
    return fits


_FITS = _battery_fits()
_IDS = [f"{rf.project}::{rf.name}" for rf in _FITS]


with open(FIXTURE) as _f:
    _EXPECTED = {(r["project"], r["name"]): r for r in json.load(_f)["records"]}


def test_battery_roster():
    assert len(_FITS) >= MIN_BATTERY_SIZE, (
        f"C 1s battery shrank to {len(_FITS)} fits (< {MIN_BATTERY_SIZE}) — "
        "reference data or eligibility rules changed"
    )
    projects = {rf.project for rf in _FITS}
    assert len(projects) >= 3, f"battery covers only {projects}"
    # fixture roster must match exactly
    assert {(rf.project, rf.name) for rf in _FITS} == set(_EXPECTED), (
        "battery roster no longer matches the frozen fixture — regenerate "
        "scripts/gen_c1s_battery_fixture.py only if this change is intentional"
    )


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_eval_parity(rf):
    relmax = eval_parity_relmax(rf)
    assert relmax < EVAL_PARITY_TOL, (
        f"{rf.project}/{rf.name}: python eval of saved params deviates from "
        f"saved fittedY by {relmax:.3e} (tol {EVAL_PARITY_TOL})"
    )


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_refit_stability_and_fixture(rf):
    rec = refit_record(rf)
    assert rec["success"], f"{rf.project}/{rf.name}: seeded refit did not converge"

    # (2) stays at the expert minimum
    by_id = {str(p["id"]): p for p in rf.peaks}
    for pk in rec["peaks"]:
        saved = by_id[str(pk["id"])]
        dc = abs(pk["center"] - saved["center"])
        dfw = abs(pk["fwhm"] - saved["fwhm"]) / max(saved["fwhm"], 1e-9)
        dam = abs(pk["amplitude"] - saved["amplitude"]) / max(abs(saved["amplitude"]), 1e-9)
        assert dc <= CENTER_DRIFT_TOL_EV, (
            f"{rf.name} peak {pk['id']}: center drifted {dc:.4f} eV from expert fit"
        )
        assert dfw <= REL_DRIFT_TOL, (
            f"{rf.name} peak {pk['id']}: fwhm drifted {dfw:.2%} from expert fit"
        )
        assert dam <= REL_DRIFT_TOL, (
/Users/skyefortier/xps-app/venv
ls: venv: No such file or directory

exec
/bin/zsh -lc "sed -n '3790,3835p' templates/index.html; sed -n '6200,6348p' templates/index.html; sed -n '7080,7155p' templates/index.html; sed -n '7268,7322p' templates/index.html; sed -n '7705,7765p' templates/index.html; sed -n '8215,8280p' templates/index.html; sed -n '9980,10160p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    if (prev) {
      this.activateTab(this._preSurveyTabId);
    }
    this._preSurveyTabId = null;
  }

  // ── Private helpers ─────────────────────────────

  _getTab(id) { return this.tabs.find(t => t.id === id) || null; }

  _syncActiveToRecord() {
    if (!this.activeId) return;
    const t = this._getTab(this.activeId);
    if (!t) return;
    if (t.isStack) return;  // stack tabs have no UI/form state to sync back
    // Re-capture peaks reference in case removePeak/clearAllPeaks replaced the array
    t.peaks = state.peaks;
    t.ccShift = isNaN(state.ccShift) ? 0 : state.ccShift;
    t.nextId = state.nextId;
    t.fitResult = state.fitResult;
    t.lineWidth = state.lineWidth ?? 1.5;
    t.yZoom = state._mainYMax || null;
    t.xZoomMin = state._mainXMin ?? null;
    t.xZoomMax = state._mainXMax ?? null;
    t.notes = document.getElementById('spectrum-notes')?.value || '';
    t.ui = this._captureUI();
  }

  _captureUI() {
    return {
      bgType:      document.getElementById('bg-type')?.value || 'shirley',
      bgStart:     document.getElementById('bg-start')?.value || '',
      bgEnd:       document.getElementById('bg-end')?.value || '',
      shirleyIter: document.getElementById('shirley-iter')?.value || '5',
      endpointAvg: document.getElementById('bg-endpoint-avg')?.value || LEGACY_ENDPOINT_AVG,
      roiMin:      document.getElementById('roi-min')?.value || '',
      roiMax:      document.getElementById('roi-max')?.value || '',
      ccMethod:    document.getElementById('cc-method')?.value || 'none',
      ccObs:       document.getElementById('cc-obs')?.value || '',
      ccLit:       document.getElementById('cc-lit')?.value || '',
      bgSubtractedView: !!document.getElementById('bg-sub-toggle')?.checked,
    };
  }

  _restoreUI(ui) {
    const set = (id, val) => {
  if (resp.ok === false) {
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
    // never showed — on the 90 committed Voigt targets 60 of 180 components
    // went to pure Gaussian and 16 to pure Lorentzian, and every area the page
    // reported for them was the 0.5 curve's, up to 20 % off the fitted one.
    // Fixed on both sides; use GL to fit the mix.
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = 0.5;
    spec.fix_gl_ratio = true;
  } else if (shape === 'GL') {
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
  } else if (shape === 'asym-GL') {
    spec.shape = 'asymmetric_gl';
    // A03 Codex round 1: `p.glMix || 50` sent a mix of 0 as 50 (and a DS α of 0
    // as 0.1 below) — a value the page draws but never requested; locked, the
    // server held the substitute and the drawn curve differed from the fitted
    // one by 6.9 % (asym-GL) and 8.8 % (DS) of amplitude. Only a NON-NUMBER
    // falls back to the default.
    spec.gl_ratio = (Number.isFinite(p.glMix) ? p.glMix : 50) / 100;
    spec.asymmetry = Number.isFinite(p.asymmetry) ? p.asymmetry : 0;
    spec.fix_asymmetry = !!p.fixAsymmetry;
    // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
    // For non-auto-fit peaks these fields are absent and the backend falls back
    // to its [0.0, 1.0] default.
    if (Number.isFinite(p._afAsymMin)) spec.asymmetry_min = p._afAsymMin;
    if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
  } else if (shape === 'DS') {
    spec.shape = 'doniach_sunjic';
    spec.alpha      = Number.isFinite(p.dsAlpha) ? p.dsAlpha : 0.1;
    spec.gamma_asym = Number.isFinite(p.dsGamma) ? p.dsGamma : 0.0;
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
  if (par.amplitude && !p.fixAmplitude) p.amplitude = par.amplitude.value;
  if (par.fwhm      && !p.fixFwhm)     p.fwhm      = par.fwhm.value;
  // glMix is read only by GL / asym-GL; a Voigt's fixed 0.5 (A03) is not a
  // fitted value and must not overwrite the mix the peak carries for a later
  // switch to GL.
  if (par.gl_ratio  && (p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) p.glMix = par.gl_ratio.value * 100;
  if (par.asymmetry && p.shape === 'asym-GL' && !p.fixAsymmetry) p.asymmetry = par.asymmetry.value;
  if (par.alpha && p.shape === 'DS' && !p.fixDsAlpha) p.dsAlpha = par.alpha.value;
  if (par.gamma_asym && p.shape === 'DS' && !p.fixDsGamma) p.dsGamma = par.gamma_asym.value;
  if (par.alpha   && p.shape === 'DSG_LA' && !p.fixLaAlpha) p.laAlpha = par.alpha.value;
  if (par.beta    && p.shape === 'DSG_LA' && !p.fixLaBeta)  p.laBeta  = par.beta.value;
  if (par.m_gauss && p.shape === 'DSG_LA' && !p.fixLaM)     p.laM     = par.m_gauss.value;
  if (par.alpha   && p.shape === 'LACX' && !p.fixCaAlpha) p.caAlpha = par.alpha.value;
  if (par.beta    && p.shape === 'LACX' && !p.fixCaBeta)  p.caBeta  = par.beta.value;
  if (par.m       && p.shape === 'LACX' && !p.fixCaM)     p.caM     = par.m.value;
}

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
// (they're full-spectrum / non-bg-aware). When subtracted view is
// effectively active we disable them with the existing app
  if (Math.abs(gPeak.center - 284.50) > 0.30 + 1e-6) {
    notify('Fit failed to converge or produced an unphysical graphite position.', 'red', true);
    return false;
  }
  // 3. Compute fitted raw center using APP CONVENTION:
  //    raw = corrected + state.ccShift (state.ccShift is the provisional value).
  const graphiteFittedRaw = gPeak.center + (Number.isFinite(state.ccShift) ? state.ccShift : 0);

  // 4. Drive updateChargeCorrection() to refine the shift.
  // Self-consistency: cc-obs = graphite_fitted_raw (NOT graphite_raw_BE),
  // approved design point.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  if (cm && co && cl) {
    cm.value = 'c1s';
    co.value = graphiteFittedRaw.toFixed(3);
    cl.value = '284.50';
    if (typeof updateChargeCorrection === 'function') updateChargeCorrection();
  }

  // 5. Build state.fitResult exactly as runFit() does.
  const { be: be2, inten: inten2 } = getROIData();
  const bgI2 = computeBackground(be2, inten2);
  const bgSub2 = inten2.map((v, i) => v - bgI2[i]);
  const stats = json.statistics || {};
  const chiReduced = stats.reduced_chi_square || 0;
  const rmse = Math.sqrt((json.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be2.length));
  const roiRange = { min: _arrMin(be2).toFixed(1), max: _arrMax(be2).toFixed(1) };
  state.fitResult = {
    chi: chiReduced * Math.max(1, be2.length - state.peaks.length * 3),
    chiReduced, rmse,
    be: be2, bgSubtracted: bgSub2, bgIntensity: bgI2,
    backendResult: json,
    fittedY: json.fitted_y,
    roiRange,
  };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  // 6. Update the same DOM elements runFit() updates.
  const fq = document.getElementById('fit-quality');
  if (fq) {
    fq.textContent = 'χ²ᵣ = ' + chiReduced.toFixed(2);
    if (typeof _CHISQ_TOOLTIP !== 'undefined') fq.setAttribute('data-xps-tip', _CHISQ_TOOLTIP);
  }
  { const _t = typeof _activeTab === 'function' ? _activeTab() : null; if (_t) _t.modelProvenance = null; }
  if (typeof _applyStatDisplay === 'function') _applyStatDisplay(state.fitResult);
  const sbChi = document.getElementById('sb-chi');
  if (sbChi) sbChi.textContent = chiReduced.toFixed(3);
  const sbMsg = document.getElementById('sb-msg');
  if (sbMsg) sbMsg.textContent = 'Auto-fit complete';
  if (typeof _updateRFactorUI === 'function') _updateRFactorUI(state.fitResult.rFactor);
  if (typeof _updateROIDisplay === 'function') _updateROIDisplay(roiRange);
  // Lock all peak centers after a successful auto-fit. Users frequently
  // run "Run Fit" again to refine FWHMs/amplitudes; without this lock the
  // converged auto-fit positions can drift. The user can manually unlock
  // any center via the existing padlock icon in the peak editor.
  for (const p of state.peaks) p.fixCenter = true;
  // the locks and the refined charge shift are part of THIS result: the
  // support verdicts describe the model as finalised here
  if (typeof _restampSupport === 'function') _restampSupport();
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
  if (typeof renderResults === 'function') renderResults();
  if (typeof _autoSnapshot === 'function') _autoSnapshot();

  // 7. Sync to tab record so tab switching preserves the result.
  if (typeof tabManager !== 'undefined' && tabManager._syncActiveToRecord) {
    tabManager._syncActiveToRecord();
  }

  // 8. Sanity check: warn if graphite area fraction is below 40%. The fit
  // is kept regardless — this is a triage signal, not a fit-quality gate.
  // Uses _peakArea so the warning matches the user-visible AREA column
  // exactly (and so it doesn't depend on backend response shape).
  const gPeak2 = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];

    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvg };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
    const resp = await fetch('/api/fit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        background: bgPayload,
        peaks: peakSpecs,
        fit_method: fitMethod,
        n_perturb: 3,
        // step (c): is the charge-reference anchor REQUIRED? The server refits
        // the model without it; a redundant anchor must not set the energy
        // reference of a whole spectrum (see applyAutoFitResult).
        require_component: anchorId,
      }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    const json = await resp.json();
    if (json.error) throw new Error(json.error);
    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }

    applyBackendResult(json);

    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
    if (!ok) {
      _hideFitSpinner();
      _autoFitRestore(snap, fittingTab);
      return;
    }

    _hideFitSpinner();
    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  } catch (e) {
    clearTimeout(timer);
    _hideFitSpinner();
    // The catch path can also fire after a mid-flight tab switch (fetch
    // error/timeout after the user moved on) — same wrong-tab hazard as
    // the explicit discard branch, so it gets the same tab-aware restore.
    _autoFitRestore(snap, fittingTab);
    let msg;
    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
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
    if (!_ownerActive(fittingTab)) {
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit cancelled — tab switched during fit.', 'amber');
      return;
    }
    if (e && e.transportFailure && opts.startPeaks) {
      // Adopting an alternative needs the server: the local engine would start
      // from the live model, not from the alternative. Nothing was changed.
      document.getElementById('sb-msg').textContent = 'Fit failed';
        if (certify()) { converged = true; break; }
      }
    } else {
      lambda *= 3;
      if (lambda > 1e8) {
        // Even a tiny steepest-descent step no longer reduces the residual,
        // yet the projected gradient is not small: stalled, not converged.
        return fail('the optimiser stalled (no step reduces the residual) after ' + iterations + ' iterations.', iterations);
      }
    }
  }
  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);

  // ── Converged: commit the working copy to the live peaks ──────────────────
  applyParams(params);
  for (const p of work) {
    const live = getPeak(p.id);
    if (!live) continue;
    Object.assign(live, p);
    // A local fit has no backend covariance; any _backendParams on the peak
    // belong to an earlier server fit (or, in Batch Fit, to the SOURCE
    // spectrum's fit) and must not travel with this result.
    delete live._backendParams;
  }

  // Degrees of freedom count the parameters this engine actually varies: the
  // integer-clamped caM is carried at its start value and is not one of them
  // (continuous parameters temporarily blocked at a wall still count).
  const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
  const dof = Math.max(1, be.length - nVaried);
  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
  const _raw = rawResiduals(params);
  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
  // "Not supported by the data": the same removal statistic the server
  // computes, from this engine's own residuals and weights (a component driven
  // to the zero floor is an outcome here too, not something to hide).
  {
    const model = evalAllPeaks(be, work);
    const verdicts = {};
    for (const wp of work) {
      if (wp.linked) continue;
      const comp = evalPeakArray(be, wp);
      const nFreeComp = paramMap.filter(d => d.id === wp.id && !isDiscrete(paramMap.indexOf(d))).length;
      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
    }
    _applySupportVerdicts(state.peaks, id => verdicts[String(id)] || null, _startsLiveKey());
  }

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
    fname + '.fit.json'
  );
  notify('Fit parameters saved.', 'green');
}

// ── 2. Save Spectrum (v2) — active tab only ──────────
function _doSaveSpectrum() {
  tabManager._syncActiveToRecord();
  const tab = tabManager._getTab(tabManager.activeId);

  // Compute current curves
  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const modelFull = evalAllPeaks(be, state.peaks);
  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
  const residuals = bgSub.map((v, i) => v - modelFull[i]);
  const fittedY = state.fitResult?.fittedY || modelFull.map((v, i) => v + bgIntensity[i]);

  // Per-peak curves and areas. evalPeakArray(), not per-point evalPeak:
  // for LACX with caM > 0, only the array evaluator applies the shape's
  // Gaussian convolution — evalPeak silently ignores caM. These curves
  // and areas are written into the saved .spec.json file.
  const peakCurves = state.peaks.map(p => {
    const yArr = evalPeakArray(be, p);
    return {
      id: p.id, name: p.name,
      y: yArr,
      area: yArr.reduce((sum, y, i) => {
        if (i === 0) return 0;
        const dx = Math.abs(be[i] - be[i - 1]);
        return sum + 0.5 * (yArr[i - 1] + y) * dx;
      }, 0)
    };
  });

  const stats = state.fitResult ? {
    chi: state.fitResult.chi,
    chiReduced: state.fitResult.chiReduced,
    rmse: state.fitResult.rmse,
    // Engine identity travels with the statistic so a reloaded local-engine
    // result is never relabelled as chi-square (unit A0).
    engine: state.fitResult.engine || null,
    objective: state.fitResult.objective || null,
    weighting: state.fitResult.weighting || null,
    status: state.fitResult.status || null,
    starts: _startsForSave(_startsIfCurrent(state.fitResult, _startsLiveKey())),
    startsModelKey: state.fitResult.startsModelKey || null,
    chosenAlternative: _startsIfCurrent(state.fitResult, _startsLiveKey()) ? (state.fitResult.chosenAlternative || null) : null,
    // Derived from the objective so an older local result (saved before
    // these fields existed) is designated on re-save too.
    reportable: _isLocalFit(state.fitResult) ? false : (state.fitResult.reportable ?? null),
    caveat: _localFitCaveat(state.fitResult) || state.fitResult.caveat || null,
  } : null;

  const data = {
    version: 2,
    timestamp: new Date().toISOString(),
    spectrumName: tab.name,
    rawBE: tab.rawBE,
    rawIntensity: tab.rawIntensity,
    ccShift: tab.ccShift,
    peaks: tab.peaks.map(p => ({...p})),
    nextId: tab.nextId,
    ui: {...tab.ui},
    roiBE: be,
    background: bgIntensity,
    fittedY: fittedY,
    residuals: residuals,
    peakCurves: peakCurves,
    statistics: stats,
    notes: tab.notes || '',
    manualAnchors: tab.manualAnchors || [],
    modelProvenance: tab.modelProvenance || null,
  };

  const fname = document.getElementById('save-fname').value.trim() || 'spectrum';
  _downloadBlob(
    new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
    fname + '.spec.json'
  );
  notify('Spectrum + fit saved.', 'green');
}

// ── 3. Save Project (v3) ─────────────────────────────
async function _doSaveProject() {
  tabManager._syncActiveToRecord();
  const sampleName = document.getElementById('proj-sample').value.trim();
  const instrument = document.getElementById('proj-instrument').value.trim();
  const fname = document.getElementById('save-fname').value.trim() || 'project';

  // Phase 5: stack tabs now persist. Spectrum tab shape unchanged;
  // stack tabs serialize with stack-specific fields only (entries +
  // visualization state). Source data lives on the spectrum tabs and
  // is reached via entry.sourceTabId at load time.
  const tabs = tabManager.tabs;
  // Size control for the frozen fit grid: BE to 4 decimals, intensities to
  // 6 significant figures — both far beyond instrument resolution. Keep
  // values as JSON numbers: toPrecision returns a STRING, so it must be
  // wrapped in Number() or downstream math silently breaks.
  const _roundBE = (a) => Array.isArray(a) ? a.map(v => Math.round(v * 1e4) / 1e4) : null;
  const _roundIntensity = (a) => Array.isArray(a) ? a.map(v => Number(v.toPrecision(6))) : null;
  const buildTabData = (t) => {
    if (t.isStack) {
      return {
        id: t.id, name: t.name, isStack: true,
        _nextColorIdx: t._nextColorIdx || 0,
        lineWidth: t.lineWidth ?? 1.5,
        verticalOffset: t.verticalOffset ?? 0,
        entries: (t.entries || []).map(e => ({
          id: e.id,
          sourceTabId: e.sourceTabId,
          color: e.color,
          visible: !!e.visible,
          showFit: !!e.showFit,
        })),
      };
    }
    const rec = {
      id: t.id, name: t.name, color: t.color, isSurvey: t.isSurvey,
      rawBE: t.rawBE, rawIntensity: t.rawIntensity,
      ccShift: t.ccShift, chargeVerified: t.chargeVerified ?? true,
      peaks: t.peaks.map(p => ({...p})),
      nextId: t.nextId,
      fitResult: t.fitResult ? {
        chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
        rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
        // Frozen fit grid: persisted so post-load updatePlot() renders the
        // recorded fit (haveFit path) instead of recomputing background and
        // residuals from current settings. Absent in older saves — loaders
        // fall back to reconstruction.
        be: _roundBE(t.fitResult.be),
        bgIntensity: _roundIntensity(t.fitResult.bgIntensity),
        bgSubtracted: _roundIntensity(t.fitResult.bgSubtracted),
        roiRange: t.fitResult.roiRange || null,
        // Engine identity (unit A0): a local-engine result stays labelled
        // "Residual variance" after reload instead of becoming chi-square.
        engine: t.fitResult.engine || null,
        objective: t.fitResult.objective || null,
        weighting: t.fitResult.weighting || null,
        status: t.fitResult.status || null,
        starts: _startsForSave(_startsIfCurrent(t.fitResult, _startsRecordKey(t))),
        startsModelKey: t.fitResult.startsModelKey || null,
        chosenAlternative: _startsIfCurrent(t.fitResult, _startsRecordKey(t)) ? (t.fitResult.chosenAlternative || null) : null,
        iterations: t.fitResult.iterations ?? null,
        reportable: _isLocalFit(t.fitResult) ? false : (t.fitResult.reportable ?? null),
        caveat: _localFitCaveat(t.fitResult) || t.fitResult.caveat || null,
      } : null,
      modelProvenance: t.modelProvenance || null,
      notes: t.notes || '',
      manualAnchors: t.manualAnchors || [],
      lineWidth: t.lineWidth ?? 1.5,
      ui: {...t.ui},
    };
    // B2: per-tab element overlays. Additive + optional — serializeRefOverlays
    // returns null when the tab has no valid selection, and we omit the key
    // entirely then so old-shaped saves stay byte-clean. Identify transient
    // state (_refIdentify / tolEv) is structurally never serialized here.
    const _ov = RefCore.serializeRefOverlays(t._refSel);
    if (_ov) rec.refOverlays = _ov;
    // Autofit engine candidate-set annotations (spec v2.1 §1): whitelisted on
    // BOTH save and load, staying on version 3. Omitted when absent so
    // pre-engine saves stay byte-clean. REGENERABLE data only — older clients
    // silently drop this key on resave, so durable facts (human decisions,
    // per-peak confidence) must ride peak-level fields (the spread channel,
    // like _backendParams/_confidence), never this namespace.
    if (t.analysis != null) rec.analysis = t.analysis;
    return rec;
  };

  const meta = {
    version: 3,
    timestamp: new Date().toISOString(),
    sample_name: sampleName,
    instrument: instrument,
    activeId: tabManager.activeId,
  };
  // B2: compound markers are GLOBAL (project-meta scope, not per-tab). Additive +
  // optional — omit the key when there are no markers (serializer returns null).
  // Top-level version stays 3. (Flows to both the .proj.json `{...meta}` and the
  // .proj.zip manifest `{...meta}`, which reuse this same meta object.)
  const _refCM = RefCore.serializeRefCompoundMarkers(_refCompoundMarkers);

codex
The gate now makes one choice from the recorded mix; the fallback is gone. Normal server fitting updates the parameters and curve synchronously, and successful local fitting deletes old backend metadata. I’m checking restore/save paths and linked or locked peaks next, then testing the reproducers and recalculating the statistics.

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_voigt_contract.py tests/autofit/test_u4f_parity_battery.py tests/autofit/test_b1s_cl2p_batteries.py tests/autofit/test_c1s_parity_battery.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 88ms:
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
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/lineshape_roundtrip.test.js tests/js/lineshape_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "sed -n '9980,10155p' templates/index.html; sed -n '8226,8279p' templates/index.html; sed -n '13648,13682p' templates/index.html; sed -n '13790,13815p' templates/index.html; sed -n '35,100p' autofit/parity.py; sed -n '820,910p' fitting.py; sed -n '1,110p' tests/js/lineshape_roundtrip.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    fname + '.fit.json'
  );
  notify('Fit parameters saved.', 'green');
}

// ── 2. Save Spectrum (v2) — active tab only ──────────
function _doSaveSpectrum() {
  tabManager._syncActiveToRecord();
  const tab = tabManager._getTab(tabManager.activeId);

  // Compute current curves
  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const modelFull = evalAllPeaks(be, state.peaks);
  const bgSub = inten.map((v, i) => v - bgIntensity[i]);
  const residuals = bgSub.map((v, i) => v - modelFull[i]);
  const fittedY = state.fitResult?.fittedY || modelFull.map((v, i) => v + bgIntensity[i]);

  // Per-peak curves and areas. evalPeakArray(), not per-point evalPeak:
  // for LACX with caM > 0, only the array evaluator applies the shape's
  // Gaussian convolution — evalPeak silently ignores caM. These curves
  // and areas are written into the saved .spec.json file.
  const peakCurves = state.peaks.map(p => {
    const yArr = evalPeakArray(be, p);
    return {
      id: p.id, name: p.name,
      y: yArr,
      area: yArr.reduce((sum, y, i) => {
        if (i === 0) return 0;
        const dx = Math.abs(be[i] - be[i - 1]);
        return sum + 0.5 * (yArr[i - 1] + y) * dx;
      }, 0)
    };
  });

  const stats = state.fitResult ? {
    chi: state.fitResult.chi,
    chiReduced: state.fitResult.chiReduced,
    rmse: state.fitResult.rmse,
    // Engine identity travels with the statistic so a reloaded local-engine
    // result is never relabelled as chi-square (unit A0).
    engine: state.fitResult.engine || null,
    objective: state.fitResult.objective || null,
    weighting: state.fitResult.weighting || null,
    status: state.fitResult.status || null,
    starts: _startsForSave(_startsIfCurrent(state.fitResult, _startsLiveKey())),
    startsModelKey: state.fitResult.startsModelKey || null,
    chosenAlternative: _startsIfCurrent(state.fitResult, _startsLiveKey()) ? (state.fitResult.chosenAlternative || null) : null,
    // Derived from the objective so an older local result (saved before
    // these fields existed) is designated on re-save too.
    reportable: _isLocalFit(state.fitResult) ? false : (state.fitResult.reportable ?? null),
    caveat: _localFitCaveat(state.fitResult) || state.fitResult.caveat || null,
  } : null;

  const data = {
    version: 2,
    timestamp: new Date().toISOString(),
    spectrumName: tab.name,
    rawBE: tab.rawBE,
    rawIntensity: tab.rawIntensity,
    ccShift: tab.ccShift,
    peaks: tab.peaks.map(p => ({...p})),
    nextId: tab.nextId,
    ui: {...tab.ui},
    roiBE: be,
    background: bgIntensity,
    fittedY: fittedY,
    residuals: residuals,
    peakCurves: peakCurves,
    statistics: stats,
    notes: tab.notes || '',
    manualAnchors: tab.manualAnchors || [],
    modelProvenance: tab.modelProvenance || null,
  };

  const fname = document.getElementById('save-fname').value.trim() || 'spectrum';
  _downloadBlob(
    new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
    fname + '.spec.json'
  );
  notify('Spectrum + fit saved.', 'green');
}

// ── 3. Save Project (v3) ─────────────────────────────
async function _doSaveProject() {
  tabManager._syncActiveToRecord();
  const sampleName = document.getElementById('proj-sample').value.trim();
  const instrument = document.getElementById('proj-instrument').value.trim();
  const fname = document.getElementById('save-fname').value.trim() || 'project';

  // Phase 5: stack tabs now persist. Spectrum tab shape unchanged;
  // stack tabs serialize with stack-specific fields only (entries +
  // visualization state). Source data lives on the spectrum tabs and
  // is reached via entry.sourceTabId at load time.
  const tabs = tabManager.tabs;
  // Size control for the frozen fit grid: BE to 4 decimals, intensities to
  // 6 significant figures — both far beyond instrument resolution. Keep
  // values as JSON numbers: toPrecision returns a STRING, so it must be
  // wrapped in Number() or downstream math silently breaks.
  const _roundBE = (a) => Array.isArray(a) ? a.map(v => Math.round(v * 1e4) / 1e4) : null;
  const _roundIntensity = (a) => Array.isArray(a) ? a.map(v => Number(v.toPrecision(6))) : null;
  const buildTabData = (t) => {
    if (t.isStack) {
      return {
        id: t.id, name: t.name, isStack: true,
        _nextColorIdx: t._nextColorIdx || 0,
        lineWidth: t.lineWidth ?? 1.5,
        verticalOffset: t.verticalOffset ?? 0,
        entries: (t.entries || []).map(e => ({
          id: e.id,
          sourceTabId: e.sourceTabId,
          color: e.color,
          visible: !!e.visible,
          showFit: !!e.showFit,
        })),
      };
    }
    const rec = {
      id: t.id, name: t.name, color: t.color, isSurvey: t.isSurvey,
      rawBE: t.rawBE, rawIntensity: t.rawIntensity,
      ccShift: t.ccShift, chargeVerified: t.chargeVerified ?? true,
      peaks: t.peaks.map(p => ({...p})),
      nextId: t.nextId,
      fitResult: t.fitResult ? {
        chi: t.fitResult.chi, chiReduced: t.fitResult.chiReduced,
        rmse: t.fitResult.rmse, fittedY: t.fitResult.fittedY || null,
        // Frozen fit grid: persisted so post-load updatePlot() renders the
        // recorded fit (haveFit path) instead of recomputing background and
        // residuals from current settings. Absent in older saves — loaders
        // fall back to reconstruction.
        be: _roundBE(t.fitResult.be),
        bgIntensity: _roundIntensity(t.fitResult.bgIntensity),
        bgSubtracted: _roundIntensity(t.fitResult.bgSubtracted),
        roiRange: t.fitResult.roiRange || null,
        // Engine identity (unit A0): a local-engine result stays labelled
        // "Residual variance" after reload instead of becoming chi-square.
        engine: t.fitResult.engine || null,
        objective: t.fitResult.objective || null,
        weighting: t.fitResult.weighting || null,
        status: t.fitResult.status || null,
        starts: _startsForSave(_startsIfCurrent(t.fitResult, _startsRecordKey(t))),
        startsModelKey: t.fitResult.startsModelKey || null,
        chosenAlternative: _startsIfCurrent(t.fitResult, _startsRecordKey(t)) ? (t.fitResult.chosenAlternative || null) : null,
        iterations: t.fitResult.iterations ?? null,
        reportable: _isLocalFit(t.fitResult) ? false : (t.fitResult.reportable ?? null),
        caveat: _localFitCaveat(t.fitResult) || t.fitResult.caveat || null,
      } : null,
      modelProvenance: t.modelProvenance || null,
      notes: t.notes || '',
      manualAnchors: t.manualAnchors || [],
      lineWidth: t.lineWidth ?? 1.5,
      ui: {...t.ui},
    };
    // B2: per-tab element overlays. Additive + optional — serializeRefOverlays
    // returns null when the tab has no valid selection, and we omit the key
    // entirely then so old-shaped saves stay byte-clean. Identify transient
    // state (_refIdentify / tolEv) is structurally never serialized here.
    const _ov = RefCore.serializeRefOverlays(t._refSel);
    if (_ov) rec.refOverlays = _ov;
    // Autofit engine candidate-set annotations (spec v2.1 §1): whitelisted on
    // BOTH save and load, staying on version 3. Omitted when absent so
    // pre-engine saves stay byte-clean. REGENERABLE data only — older clients
    // silently drop this key on resave, so durable facts (human decisions,
    // per-peak confidence) must ride peak-level fields (the spread channel,
    // like _backendParams/_confidence), never this namespace.
    if (t.analysis != null) rec.analysis = t.analysis;
    return rec;
  };

  const meta = {
    version: 3,
    timestamp: new Date().toISOString(),
    sample_name: sampleName,
    instrument: instrument,
    activeId: tabManager.activeId,
  };
  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);

  // ── Converged: commit the working copy to the live peaks ──────────────────
  applyParams(params);
  for (const p of work) {
    const live = getPeak(p.id);
    if (!live) continue;
    Object.assign(live, p);
    // A local fit has no backend covariance; any _backendParams on the peak
    // belong to an earlier server fit (or, in Batch Fit, to the SOURCE
    // spectrum's fit) and must not travel with this result.
    delete live._backendParams;
  }

  // Degrees of freedom count the parameters this engine actually varies: the
  // integer-clamped caM is carried at its start value and is not one of them
  // (continuous parameters temporarily blocked at a wall still count).
  const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
  const dof = Math.max(1, be.length - nVaried);
  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
  const _raw = rawResiduals(params);
  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
  // "Not supported by the data": the same removal statistic the server
  // computes, from this engine's own residuals and weights (a component driven
  // to the zero floor is an outcome here too, not something to hide).
  {
    const model = evalAllPeaks(be, work);
    const verdicts = {};
    for (const wp of work) {
      if (wp.linked) continue;
      const comp = evalPeakArray(be, wp);
      const nFreeComp = paramMap.filter(d => d.id === wp.id && !isDiscrete(paramMap.indexOf(d))).length;
      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
    }
    _applySupportVerdicts(state.peaks, id => verdicts[String(id)] || null, _startsLiveKey());
  }

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

  const chi = state.fitResult.chiReduced;
  const n = state.peaks.length;
  const label = `Fit #${tab._fitCount} (${n} peak${n !== 1 ? 's' : ''})`;

  const snap = {
    id: Date.now(),
    label,
    timestamp: new Date().toLocaleTimeString(),
    peaks: JSON.parse(JSON.stringify(state.peaks)),
    fitResult: {
      ...state.fitResult,
      be: [...(state.fitResult.be || [])],
      bgSubtracted: [...(state.fitResult.bgSubtracted || [])],
      bgIntensity: state.fitResult.bgIntensity ? [...state.fitResult.bgIntensity] : null,
      fittedY: state.fitResult.fittedY ? [...state.fitResult.fittedY] : null,
    },
    chi,
    rFactor: state.fitResult.rFactor ?? null,
  };

  tab.snapshots.unshift(snap);
  if (tab.snapshots.length > SNAPSHOT_MAX) tab.snapshots.pop();
}

function showHistoryModal() {
  _renderHistoryList();
  const panel = document.getElementById('history-panel');
  if (!panel.classList.contains('open')) {
    // Position at top-right of viewport, offset from the right panel
    const rp = document.getElementById('right-panel');
    const rpLeft = rp ? rp.getBoundingClientRect().left : window.innerWidth - 360;
    panel.style.top = '60px';
    panel.style.left = Math.max(20, rpLeft - 360) + 'px';
    panel.style.right = '';
}

function _historyClearPreview() {
  _historyPreview = null;
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  updatePlot();
}

function _historyRestoreSnap(snapId) {
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab || !tab.snapshots) return;
  const snap = tab.snapshots.find(s => s.id === snapId);
  if (!snap) return;

  pushUndo();
  state.peaks = _normalizePeaksCRef(JSON.parse(JSON.stringify(snap.peaks)));
  state.fitResult = snap.fitResult ? { ...snap.fitResult } : null;
  tab.modelProvenance = null;   // the restored result governs the designation (unit A0)
  tabManager._syncActiveToRecord();

  _historyClearPreview();
  renderPeakList();
  updatePlot();
  renderResults();
  _closeHistoryPanel();
    smart_experimental_background,
    tougaard_background,
    run_fit,
)
from .reference import ReferenceFit, apply_backend_params, peak_to_backend_spec


def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
    """Evaluate one backend peak spec at its own parameter values."""
    f = _SHAPE_FUNCS[spec["shape"]]
    a, c, s = spec["amplitude"], spec["center"], spec["shape"]
    if s in ("gaussian", "lorentzian"):
        return f(be, a, c, spec["fwhm"])
    if s == "pseudo_voigt_gl":
        return f(be, a, c, spec["fwhm"], spec["gl_ratio"])
    if s == "asymmetric_gl":
        return f(be, a, c, spec["fwhm"], spec["asymmetry"], spec["gl_ratio"])
    if s == "doniach_sunjic":
        return f(be, a, c, spec["fwhm"], spec["alpha"], spec["gamma_asym"])
    if s == "ds_g":
        return f(be, a, c, spec["alpha"], spec["beta"], spec["m_gauss"])
    if s == "la_casaxps":
        return f(be, a, c, spec["fwhm"], spec["alpha"], spec["beta"], spec["m"])
    raise ValueError(f"Unknown backend shape {s!r}")


def evaluate_model(be: np.ndarray, specs: list[dict]) -> np.ndarray:
    """Sum of all peak evaluations (no background)."""
    total = np.zeros_like(np.asarray(be, dtype=float))
    for s in specs:
        total = total + evaluate_peak(be, s)
    return total


def background_like_run_fit(
    x: np.ndarray,
    y: np.ndarray,
    method: str,
    bg_start_idx: int,
    bg_end_idx: int,
    endpoint_avg: int = 1,
) -> np.ndarray:
    """
    Reproduce exactly the background array ``run_fit`` constructs — including
    the anchor-window normalization (swap reversed indices, bail to full ROI
    below 2 points), the ``[i0:i1]`` slice semantics, and the flat-hold
    extension outside the anchor window.  Kept in lockstep with
    ``fitting.run_fit``; the eval-parity battery fails if they diverge.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    i0, i1 = bg_start_idx, bg_end_idx
    i0 = max(0, i0)
    i1 = min(len(x), i1)
    if i0 > i1:
        i0, i1 = i1, i0
    if i1 - i0 < 2:
        i0, i1 = 0, len(x)

    xb, yb = x[i0:i1], y[i0:i1]
    m = (method or "shirley").lower()

    if m == "shirley":
        bg_inner = shirley_background(xb, yb, n_avg=endpoint_avg)
    elif m == "smart":
        bg_inner = smart_background(xb, yb, n_avg=endpoint_avg)
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
        if not vary and expr is None:
            # A HELD parameter is held at the value requested. The bounds are
            # the optimiser's search limits; lmfit clips a value outside them
            # even when it does not vary, which silently changed a locked
            # DS+G m of 0 (the page's delta-kernel branch, drawn without
            # convolution) into 0.05 (a convolved fit) — A03 Codex round 2's
            # locked-at-bounds round trips. Widen the limit to the value.
            if min_ is not None and value < min_:
                min_ = value
            if max_ is not None and value > max_:
                max_ = value
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
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
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

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -s -q -p no:cacheprovider tests/test_voigt_contract.py tests/autofit/test_u4f_parity_battery.py tests/autofit/test_b1s_cl2p_batteries.py tests/autofit/test_c1s_parity_battery.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "cat autofit/parity.py | head -70; sed -n '198,290p' autofit/reference.py; sed -n '250,370p' docs/findings/2026-09-fit-determinacy.md; rg -n '3.5|reproducer|FINAL|VERDICT|0.9' docs/autofit/codex/a03_voigt_eta_r4_verdict_runA.md | tail -35; rg -n '_backendParams|fitResult' static/js/batch_propagation.js; sed -n '2360,2398p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
"""
Parity / characterization utilities for the autofit engine.

Two independent parity notions, both against the expert reference fits in
``docs/autofit/test_data``:

1. **Eval parity** — evaluating the saved peak parameters through
   ``fitting.py``'s lineshape functions (+ the exact background
   reconstruction ``run_fit`` performs) reproduces the saved
   ``fitResult.fittedY``.  This proves the spec mirror
   (``peak_to_backend_spec``) and the lineshape math agree with what
   produced the expert fits.

2. **Refit stability** — re-running ``fitting.run_fit`` seeded at the saved
   parameters stays at the same minimum (no parameter drift, same χ²ᵣ).
   Frozen into a fixture, this is the regression net that pins today's
   manual-fit behavior.

Neither imports anything from ``app.py`` and nothing here is reachable from
the production request path.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from fitting import (
    _SHAPE_FUNCS,
    linear_background,
    shirley_background,
    shirley_linear_background,
    smart_background,
    smart_experimental_background,
    tougaard_background,
    run_fit,
)
from .reference import ReferenceFit, apply_backend_params, peak_to_backend_spec


def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
    """Evaluate one backend peak spec at its own parameter values."""
    f = _SHAPE_FUNCS[spec["shape"]]
    a, c, s = spec["amplitude"], spec["center"], spec["shape"]
    if s in ("gaussian", "lorentzian"):
        return f(be, a, c, spec["fwhm"])
    if s == "pseudo_voigt_gl":
        return f(be, a, c, spec["fwhm"], spec["gl_ratio"])
    if s == "asymmetric_gl":
        return f(be, a, c, spec["fwhm"], spec["asymmetry"], spec["gl_ratio"])
    if s == "doniach_sunjic":
        return f(be, a, c, spec["fwhm"], spec["alpha"], spec["gamma_asym"])
    if s == "ds_g":
        return f(be, a, c, spec["alpha"], spec["beta"], spec["m_gauss"])
    if s == "la_casaxps":
        return f(be, a, c, spec["fwhm"], spec["alpha"], spec["beta"], spec["m"])
    raise ValueError(f"Unknown backend shape {s!r}")


def evaluate_model(be: np.ndarray, specs: list[dict]) -> np.ndarray:
    """Sum of all peak evaluations (no background)."""
    total = np.zeros_like(np.asarray(be, dtype=float))
    for s in specs:
        total = total + evaluate_peak(be, s)
    return total


def background_like_run_fit(
    x: np.ndarray,
# ReferenceFit — one saved, fitted spectrum tab
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ReferenceFit:
    """A saved spectrum tab with a fit, plus reconstructed fit inputs."""

    project: str                 # source project filename
    tab_file: str                # spectrum_*.json name (or index for .proj.json)
    name: str
    raw_be: np.ndarray
    raw_intensity: np.ndarray
    cc_shift: float
    peaks: list[dict]
    fit_result: dict
    ui: dict = field(default_factory=dict)

    # ── frontend-semantics reconstructions ──────────────────────────────────

    @property
    def corrected_be(self) -> np.ndarray:
        # getCorrectedBE (index.html:4486): corrected = rawBE − ccShift
        # (ccShift = observed − literature, so the applied shift is −ccShift).
        return self.raw_be - self.cc_shift

    def _roi_bounds(self) -> tuple[float, float]:
        lo = _parse_float(self.ui.get("roiMin"), -np.inf)
        hi = _parse_float(self.ui.get("roiMax"), np.inf)
        return lo, hi

    @property
    def roi_mask(self) -> np.ndarray:
        lo, hi = self._roi_bounds()
        c = self.corrected_be
        return (c >= lo) & (c <= hi)

    @property
    def roi_be(self) -> np.ndarray:
        return self.corrected_be[self.roi_mask]

    @property
    def roi_intensity(self) -> np.ndarray:
        return self.raw_intensity[self.roi_mask]

    def bg_indices(self) -> tuple[int, int]:
        """Nearest ROI-grid indices to ui.bgStart / ui.bgEnd (index.html:6575)."""
        be = self.roi_be
        bg_start = _parse_float(self.ui.get("bgStart"), be[0] if len(be) else 0.0)
        bg_end = _parse_float(self.ui.get("bgEnd"), be[-1] if len(be) else 0.0)
        i_start = int(np.argmin(np.abs(be - bg_start)))
        i_end = int(np.argmin(np.abs(be - bg_end)))
        return i_start, i_end

    @property
    def bg_method(self) -> str:
        return self.ui.get("bgType") or "shirley"

    @property
    def endpoint_avg(self) -> int:
        try:
            return max(1, int(self.ui.get("endpointAvg", 1)))
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
        """Coarse region label from the ROI midpoint (mirrors isC1sTab logic)."""
        mid = self.region_midpoint
        if mid is None:
            return "unknown"
        for label, lo, hi in _REGION_WINDOWS:
            if lo <= mid <= hi:
                return label
        return "unknown"


# Coarse corrected-BE midpoint windows for region labeling of the reference
# data.  These are bookkeeping bins for test selection only — NOT physics
# constants (the engine's physical BE windows live in the region modules and
# are lit-cited there).
_REGION_WINDOWS = [
    ("C 1s", 270.0, 315.0),      # matches isC1sTab (index.html:6548)
    ("B 1s", 178.0, 194.0),      # B 1s scans in the data set center ~186–191
to reach it, should be expected to rank the migrated model first on graphitic
C 1s. Checks worth making there: whether candidate centre windows let an
adventitious slot reach the main line; whether the ranking can prefer
"asymmetric line + broad carbon under it" over "asymmetric line + C–O"; and
whether the result names the slot by its ROLE (so a migrated slot is still
called C–O). Narrower per-role centre windows are the structural remedy; the
manual path has only the ± 2 eV default.


## 7. A03 (2026-09-22) — a "Voigt" was fitted with a mix the page never drew; the sweep found DS+G's preview wrong across its fitted range

Generators: `scripts/voigt_eta_measure.py` (the 90 committed Voigt targets,
both requests), `scripts/local_server_gap.js` (the 18 W1 targets),
section (D) of `tests/js/lineshape_parity.test.js` (the sweep). Plan and
tables: `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.

**The Voigt identity.** `peakToBackendSpec` sent a Voigt as
`pseudo_voigt_gl` with `gl_ratio: 0.3` FREE; `evalPeak` drew η = 0.5;
`runFitLocal` held 0.5; the dropdown said "50/50"; CLAUDE.md said fixed 0.5.
On the 90 committed targets with a Voigt component (89 U 4f tabs across five
projects, one Cl 2p; 180 Voigt components): the server's free η ended at
pure Gaussian (< 0.01) on 60 of the 180 and pure Lorentzian (> 0.99) on
16, within 0.4–0.6 on 24. Every area, percentage, chart
component and export the page produced for those components was the 0.5
curve under parameters fitted for another mix: that curve vs the fitted one
median 13.9 %, p90 19.2 %, max 20.1 % (116 of 180 components > 10 %); as
area fractions median 0.96 pp, max 1.55 pp (35 of 90 targets > 1 pp; server
curves, trapezoid). Fixed on both sides (η = 0.5 held in the request). What
a student SEES change on re-fitting a saved project, measured with the
PAGE's own integration of the saved peaks against the page's integration of
the refit (`scripts/voigt_saved_vs_refit.js`, 55 committed tabs with a
saved fit and a Voigt, six projects; the saved side on the saved fit's own
grid, the refit on the upload-rounded request): an area fraction moves by
median 0.36 pp, p90 0.51 pp, max 0.69 pp (none > 1 pp); a Voigt's own area
by median 3.3 %, p90 6.0 %, max 15.3 % per component (110 components). The
refit vs the server's own free-η fit is
median 0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9 % (the mix is one
parameter fewer). The alternative — honour the fitted η on the page — would
have made "Voigt" a GL with a hidden slider and silently kept a shape the
student had not chosen; 76 of 180 fitted values sitting on a bound says the
parameter was not determined by the data in those fits anyway. The same
review found the builder sending an asym-GL mix of exactly 0 as 50 and a
DS α of exactly 0 as 0.1 (`||` defaults); locked, the drawn curve differed
from the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders.
Locking every shape parameter at each of its bounds then found a fourth:
lmfit clips a held value to its bounds, so a DS+G with m locked at 0 (the
page's delta-kernel branch) was fitted with m = 0.05, the free-parameter
floor; `_set` now widens the limit to a held value. And a fifth: the
server's DS+G evaluator clips α to 0.495 while the page's did not, so an α
locked at 0.5 (the input allows it) was drawn 0.9 % from its fit; the page
now clips as the server does. Two committed saves show the class in the
lab's data: the U 4f expert fits (29) and the Cl 2p Scan_1 fit (two Voigt
lines, η written back as 15.7 %) reproduce their own saved curves only with
the mix the old request fitted; both batteries were re-based on that
fact — each Voigt is evaluated with the mix the server RECORDED for the fit
that produced the saved curve (the peak's `_backendParams`), one
deterministic choice, never "whichever mix passes".

**The re-measurement (W1 methodology, 18 targets).** C 1s unchanged (8 of 9
within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is the §2 finding). U 4f,
W1 → A03: max Δcentre 39.7 → 28.8 meV, ΔFWHM 17.2 → 15.8 %, Δarea 20.8 →
8.9 %, Δfraction 1.4 → 0.77 pp. On the 5 of 9 targets where both engines
reach the same minimum (χ²ᵣ equal to 2–3 digits) every component is within
4.3 meV, 2.6 %, 2.0 %, 0.12 pp — the Voigt gap is gone. On the other 4 the
server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
7.9 while the local engine holds it; χ²ᵣ (local/server − 1) is +9.6, +10.1,
−5.0 and +12.7 %, and the satellites, which share the region, differ by up
to 8.9 % in area. A control arm (the server with every LA m HELD at its
start, rounded as the local engine rounds it) attributes it: on Scan_6
holding m closes the gap to 3.6 meV / 1.1 % / 1.6 % / 0.07 pp — that one IS
the `caM` clamp; on Scan_5 and Scan_8 holding m changes nothing and the
local engine's χ²ᵣ stays 9.7 % and 13.1 % above the server's from the same
start with the same free parameters — a WORSE MINIMUM (the mirror image of
§2, where the local engine found the better one on C 1s Scan_4); Scan_4 is
in between (+5.4 %). The "starting point" label stays
on both grounds; the `caM` clamp is the next unit, and the local engine's
worse-minimum outcome on 3 of 9 U 4f targets is a finding for the
local-engine work after it.

**The sweep.** Gaussian, Lorentzian, Voigt, GL, asym-GL and DS agree with
the server to 1e-15 across every bound. LACX with m > 0: up to 0.89 % of
amplitude when the kernel is wide against the peak (the tracked
discretisation gap). DS+G with m ≥ 0.05: the page's `laCasaXPS` quadrature
uses a step of 2·(6σ + 50β)/max(300, ⌈2·(6σ + 50β)/(β/3)⌉) — sized to the
Lorentzian core, blind to the Gaussian kernel — so at β = 2, m = 0.05 the
step is 0.67 eV against σ = 0.021 eV, the kernel weights sample nothing,
and the page's curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's
area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
865 committed components use DS+G, so no saved figure is affected; it is the
fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
recorded as its own unit. The general lesson repeats §6's: a harness that
evaluates one representative point per shape proves nothing about the range
the optimiser can reach.
9975:CORRUPT fittedY PASSES scale 1.0250000000000004 contract 0.03447011182703159 saved 0.02439048258022448
9988:saved vs refit recalculated {"n":55,"projects":6,"savedGrid":41,"dFrac":{"median":0.3640236960289873,"p90":0.5078511773600608,"max":0.6882980473358474},"dArea":{"median":4.576983178447858,"p90":7.556793905528403,"max":15.30071242466854}}
9989:U4f Scan_0 2.065244443877729 2.0551875684374585 2.0491576562300122 0.7850439227459427
9990:U4f Scan_1 2.296093573631544 2.2667421415660436 2.2601976569590905 1.5881759969943676
9992:U4f Scan_3 1.731754888573654 1.7320297992148836 1.7306122270448678 0.06602643335864578
9994:U4f Scan_5 2.3928635306048918 2.173852692315494 2.182160504818794 9.655707053665807
9995:U4f Scan_6 2.657291813593791 2.797581089317341 2.6287976699999613 1.0839230390001786
9997:U4f Scan_8 4.655520835587359 4.129258441352779 4.11711950166436 13.077136422815737
10162:  duration_ms: 1733.733251
10210:  duration_ms: 1711.146049
10346:  error: 'LACX: frontend vs backend max diff = 0.1496% of amplitude (tol 0.00009999999999999999%)'
10374:  error: 'DSG_LA: frontend vs backend max diff = 1.7518% of amplitude (tol 0.00009999999999999999%)'
10401:# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
10402:ok 47 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
10407:# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
10408:ok 48 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
10416:  duration_ms: 1762.463955
10468:  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7170.363795150584, rel diff=24.2055%'
10616: for mul in [0.96,.97,.98,1.02,1.03,1.04]:
10706:median 0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9 % (the mix is one
10718://     kernel-discretisation gap (continuous m + ceil(3.5σ) kernel on the
10723://     (β/3) but NOT the Gaussian kernel (σ = m/2.355): at β = 2, m = 0.05
10725: succeeded in 5099ms:
10782:   305	// bounds for a free peak (gl_ratio 0–1, asymmetry 0–1, DS α 0–0.5 and
10794:   285	median 0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9 % (the mix is one
10823: succeeded in 2099ms:
10826:original errors [(0.007087793702285558, 2.0113346039771816e-07)]
10885:NEW false acceptance UCl4_on_graphite.proj.zip U4f Scan_8 LACX 3 multiplier 0.035 contract 0.014571003220117961 saved 0.01656132412972441 main 0.015660672240234517 all assertions PASS
10894:for(const m of [0,.0009,.05,.4,.9,4]){p.laM=m;assert.deepStrictEqual(env.evalPeakArray(grid,p),env.evalPeakArray(grid,{...p,laAlpha:.495}));for(const x of grid)assert.equal(env.evalPeak(x,p),env.evalPeak(x,{...p,laAlpha:.495}));}
10897:const be=[1.000049,.950049,.900049],up=be.map(x=>+x.toFixed(4));console.log('\\''edge reproducer display'\\'',bg(be,.9,1.00003),'\\''rounded'\\'',bg(up,.9,1.00003));
10901:edge reproducer display { i0: 1, i1: 2 } rounded { i0: 0, i1: 2 }
10904:- **MAJOR — The parity gate can hide an unrelated envelope error by accepting either Voigt mix.** [tests/autofit/battery_common.py:69](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/autofit/battery_common.py:69). Concrete reproducer: on committed `UCl4_on_graphite.proj.zip / U4f Scan_8`, add `0.035 × evaluated LACX peak 3` to saved `fittedY`, leaving everything else unchanged. Saved-mix error becomes **1.6561%**, exceeding the **1.5%** tolerance; contract-mix error is **1.4571%**, so the gate passes. Stationarity and frozen-fixture assertions also pass. Main’s η=0.3 evaluation rejects this corruption at **1.5661%**. Select the evaluation contract explicitly for known legacy fixtures; do not choose whichever passes.
10920:**VERDICT: NO-GO**
10923:- **MAJOR — The parity gate can hide an unrelated envelope error by accepting either Voigt mix.** [tests/autofit/battery_common.py:69](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/autofit/battery_common.py:69). Concrete reproducer: on committed `UCl4_on_graphite.proj.zip / U4f Scan_8`, add `0.035 × evaluated LACX peak 3` to saved `fittedY`, leaving everything else unchanged. Saved-mix error becomes **1.6561%**, exceeding the **1.5%** tolerance; contract-mix error is **1.4571%**, so the gate passes. Stationarity and frozen-fixture assertions also pass. Main’s η=0.3 evaluation rejects this corruption at **1.5661%**. Select the evaluation contract explicitly for known legacy fixtures; do not choose whichever passes.
10939:**VERDICT: NO-GO**

// Undo snapshots are deep copies of state.peaks. An action that ALSO changes
// endpoint averaging (today: applying Find Peaks suggestions, which sets the
// panel to what the engine fitted at) passes { endpointAvg } so the snapshot
// carries the pre-action value as a non-index property; undo/redo restore it
// to the panel AND the tab record. Peak-only actions leave it absent.
function _peaksSnapshot(extra) {
  const snap = JSON.parse(JSON.stringify(state.peaks));
  if (extra && extra.endpointAvg !== undefined) snap._endpointAvg = String(extra.endpointAvg);
  // The model's provenance (imported local fit = starting point) travels
  // with the model through undo/redo (unit A0).
  const t = _historyTab();
  // The active tab's live result is state.fitResult (the record is synced on switch-away).
  snap._modelProvenance = t ? _provenanceOf({ modelProvenance: t.modelProvenance, fitResult: state.fitResult }) : null;
  return snap;
}
function _restoreSnapshotProvenance(tab, snap) {
  if (!tab || !snap) return;
  tab.modelProvenance = snap._modelProvenance ? JSON.parse(JSON.stringify(snap._modelProvenance)) : null;
}
function _restoreSnapshotEndpointAvg(tab, snap) {
  if (!snap || snap._endpointAvg === undefined) return;
  const el = document.getElementById('bg-endpoint-avg');
  if (el) el.value = snap._endpointAvg;
  if (tab && tab.ui) tab.ui.endpointAvg = snap._endpointAvg;
}
function _pushSnapshot(t, snap) {
  if (!t.undoStack) t.undoStack = [];
  if (!t.redoStack) t.redoStack = [];
  t.undoStack.push(snap);
  if (t.undoStack.length > MAX_UNDO) t.undoStack.shift();
  t.redoStack.length = 0;
  _updateUndoButtons();
}
function pushUndo(extra) {
  _flushUndoDebounce();     // a pending slider burst is OLDER than this action: it goes first
  const t = _historyTab();
  if (!t) return;
  _pushSnapshot(t, _peaksSnapshot(extra));

 exited 2 in 2142ms:

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
__________ ERROR collecting tests/autofit/test_b1s_cl2p_batteries.py ___________
tests/autofit/test_b1s_cl2p_batteries.py:21: in <module>
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
__________ ERROR collecting tests/autofit/test_c1s_parity_battery.py ___________
tests/autofit/test_c1s_parity_battery.py:37: in <module>
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
ERROR tests/autofit/test_b1s_cl2p_batteries.py - FileNotFoundError: [Errno 2]...
ERROR tests/autofit/test_c1s_parity_battery.py - FileNotFoundError: [Errno 2]...
!!!!!!!!!!!!!!!!!!! Interrupted: 4 errors during collection !!!!!!!!!!!!!!!!!!!!
4 errors in 1.81s

exec
/bin/zsh -lc "sed -n '2420,2510p' templates/index.html; rg -n 'function invalidateFit|function undo|pushUndo\\(' templates/index.html | head -40; sed -n '5690,5740p' templates/index.html; sed -n '275,346p' docs/findings/2026-09-fit-determinacy.md; cat tests/test_voigt_contract.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    if (_undoDebounce) _flushUndoDebounce();
    _undoDebounce = { owner: t, snap: _peaksSnapshot() };
  }
  clearTimeout(_undoDebounceTimer);
  _undoDebounceTimer = setTimeout(_flushUndoDebounce, 500);
}
function _flushUndoDebounce() {
  clearTimeout(_undoDebounceTimer);
  const d = _undoDebounce; _undoDebounce = null;
  if (!d || !_ownerLive(d.owner)) return;      // owner closed: drop the entry
  _pushSnapshot(d.owner, d.snap);
}

function _updateUndoButtons() {
  const t = _activeTab();
  const u = document.getElementById('btn-undo');
  const r = document.getElementById('btn-redo');
  if (u) u.disabled = !(t && !t.isStack && t.undoStack && t.undoStack.length);
  if (r) r.disabled = !(t && !t.isStack && t.redoStack && t.redoStack.length);
}

function undo() {
  _flushUndoDebounce();     // never undo past a pending burst
  const t = _historyTab();
  if (!t || !t.undoStack.length) return;
  const snap = t.undoStack.pop();
  // Mirror the averaging into the redo entry only when the undo entry
  // carried one, so a redo re-applies exactly what the action did.
  t.redoStack.push(_peaksSnapshot(snap._endpointAvg !== undefined
    ? { endpointAvg: document.getElementById('bg-endpoint-avg')?.value } : null));
  state.peaks = snap;
  _restoreSnapshotEndpointAvg(t, snap);
  _restoreSnapshotProvenance(t, snap);
  renderPeakList();
  updatePlot();
  renderResults();   // the restored model's designation (or its absence) must be visible immediately
  _updateUndoButtons();
}

function redo() {
  _flushUndoDebounce();
  const t = _historyTab();
  if (!t || !t.redoStack.length) return;
  const snap = t.redoStack.pop();
  t.undoStack.push(_peaksSnapshot(snap._endpointAvg !== undefined
    ? { endpointAvg: document.getElementById('bg-endpoint-avg')?.value } : null));
  state.peaks = snap;
  _restoreSnapshotEndpointAvg(t, snap);
  _restoreSnapshotProvenance(t, snap);
  renderPeakList();
  updatePlot();
  renderResults();   // the restored model's designation (or its absence) must be visible immediately
  _updateUndoButtons();
}

// ═══════════════════════════════════════════════════
// STACK FEATURE — data model
// ═══════════════════════════════════════════════════
// Wong colorblind-safe palette for stack-entry traces.
const STACK_PALETTE = ['#E69F00','#56B4E9','#009E73','#F0E442','#0072B2','#D55E00','#CC79A7'];

let _nextStackNum = 1;  // monotonic counter for '▦ Stack N' default names

function isStackTab(tab) { return !!(tab && tab.isStack); }

// Render the legend panel for the given stack tab.
function renderStackLegend(stackTab) {
  const list = document.getElementById('stack-legend-list');
  const empty = document.getElementById('stack-legend-empty');
  if (!list || !empty) return;
  const entries = stackTab.entries || [];
  empty.style.display = entries.length ? 'none' : 'block';
  list.innerHTML = '';
  for (const entry of entries) {
    const src = tabManager._getTab(entry.sourceTabId);
    const name = (src ? src.name : '(missing source)') +
      (src && _isLocalFit(src.fitResult) ? ' \u2014 local fit: starting point, not reportable' : '');
    const shift = src ? (src.ccShift || 0) : 0;
    const shiftStr = (shift >= 0 ? '+' : '') + shift.toFixed(2);
    const hasFit = _entryHasFit(entry);
    const row = document.createElement('div');
    row.className = 'stack-legend-row';
    row.innerHTML =
      '<span class="swatch"></span>' +
      '<span class="name"></span>' +
      '<span class="cc">ΔCC: ' + shiftStr + ' eV</span>' +
      '<input type="checkbox" class="vis" ' + (entry.visible ? 'checked' : '') + ' title="Show spectrum">' +
      '<input type="checkbox" class="fit-toggle"'
        + (hasFit ? (entry.showFit ? ' checked' : '') : ' disabled')
        + ' title="' + (hasFit ? 'Show fit envelope' : 'No fit available') + '">' +
      '<span class="remove" title="Remove">×</span>';
2394:function pushUndo(extra) {
2441:function undo() {
3413:      pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
5008:  pushUndo();
5683:  pushUndo();
5713:  pushUndo();
5723:  pushUndo();
5735:  pushUndo();
7215:  pushUndo();
7609:  pushUndo();
13805:  pushUndo();
15741:  pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
}

function addMultiplet() {
  const p1 = addPeak({ name: 'Peak ' + state.nextId + ' (\u2087/\u2082)', center: 380 });
  const p2 = defaultPeak({
    name: 'Peak ' + state.nextId + ' (\u2085/\u2082)',
    center: p1.center + 10.9,
    amplitude: p1.amplitude * 0.75,
    color: p1.color,
    linked: p1.id,
    linkOffset: 10.9,
    linkRatio: 0.75
  });
  state.peaks.push(p2);
  renderPeakList();
  updatePlot();
  // Auto-expand the linked peak so the offset/ratio fields are immediately visible
  const body = document.getElementById('peak-body-' + p2.id);
  if (body) body.classList.add('open');
  notify('Multiplet pair added \u2014 edit offset & ratio below \u201c' + p2.name + '\u201d', 'green');
}

function removePeak(id) {
  pushUndo();
  state.peaks = state.peaks.filter(p => p.id !== id && p.linked !== id);
  _invalidateFittedY();
  renderPeakList();
  updatePlot();
}

function clearAllPeaks() {
  if (!state.peaks.length) return;
  if (!confirm('Are you sure you want to clear all peaks?')) return;
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }
  renderPeakList();
  updatePlot();
}

function getPeak(id) { return state.peaks.find(p => p.id === id); }

function unlinkPeak(id) {
  if (!confirm('Unlink this peak? It will become fully independent.')) return;
  pushUndo();
  const p = getPeak(id);
  if (!p) return;
  p.linked = null;
  renderPeakList();
  updatePlot();
median 13.9 %, p90 19.2 %, max 20.1 % (116 of 180 components > 10 %); as
area fractions median 0.96 pp, max 1.55 pp (35 of 90 targets > 1 pp; server
curves, trapezoid). Fixed on both sides (η = 0.5 held in the request). What
a student SEES change on re-fitting a saved project, measured with the
PAGE's own integration of the saved peaks against the page's integration of
the refit (`scripts/voigt_saved_vs_refit.js`, 55 committed tabs with a
saved fit and a Voigt, six projects; the saved side on the saved fit's own
grid, the refit on the upload-rounded request): an area fraction moves by
median 0.36 pp, p90 0.51 pp, max 0.69 pp (none > 1 pp); a Voigt's own area
by median 3.3 %, p90 6.0 %, max 15.3 % per component (110 components). The
refit vs the server's own free-η fit is
median 0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9 % (the mix is one
parameter fewer). The alternative — honour the fitted η on the page — would
have made "Voigt" a GL with a hidden slider and silently kept a shape the
student had not chosen; 76 of 180 fitted values sitting on a bound says the
parameter was not determined by the data in those fits anyway. The same
review found the builder sending an asym-GL mix of exactly 0 as 50 and a
DS α of exactly 0 as 0.1 (`||` defaults); locked, the drawn curve differed
from the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders.
Locking every shape parameter at each of its bounds then found a fourth:
lmfit clips a held value to its bounds, so a DS+G with m locked at 0 (the
page's delta-kernel branch) was fitted with m = 0.05, the free-parameter
floor; `_set` now widens the limit to a held value. And a fifth: the
server's DS+G evaluator clips α to 0.495 while the page's did not, so an α
locked at 0.5 (the input allows it) was drawn 0.9 % from its fit; the page
now clips as the server does. Two committed saves show the class in the
lab's data: the U 4f expert fits (29) and the Cl 2p Scan_1 fit (two Voigt
lines, η written back as 15.7 %) reproduce their own saved curves only with
the mix the old request fitted; both batteries were re-based on that
fact — each Voigt is evaluated with the mix the server RECORDED for the fit
that produced the saved curve (the peak's `_backendParams`), one
deterministic choice, never "whichever mix passes".

**The re-measurement (W1 methodology, 18 targets).** C 1s unchanged (8 of 9
within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is the §2 finding). U 4f,
W1 → A03: max Δcentre 39.7 → 28.8 meV, ΔFWHM 17.2 → 15.8 %, Δarea 20.8 →
8.9 %, Δfraction 1.4 → 0.77 pp. On the 5 of 9 targets where both engines
reach the same minimum (χ²ᵣ equal to 2–3 digits) every component is within
4.3 meV, 2.6 %, 2.0 %, 0.12 pp — the Voigt gap is gone. On the other 4 the
server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
7.9 while the local engine holds it; χ²ᵣ (local/server − 1) is +9.6, +10.1,
−5.0 and +12.7 %, and the satellites, which share the region, differ by up
to 8.9 % in area. A control arm (the server with every LA m HELD at its
start, rounded as the local engine rounds it) attributes it: on Scan_6
holding m closes the gap to 3.6 meV / 1.1 % / 1.6 % / 0.07 pp — that one IS
the `caM` clamp; on Scan_5 and Scan_8 holding m changes nothing and the
local engine's χ²ᵣ stays 9.7 % and 13.1 % above the server's from the same
start with the same free parameters — a WORSE MINIMUM (the mirror image of
§2, where the local engine found the better one on C 1s Scan_4); Scan_4 is
in between (+5.4 %). The "starting point" label stays
on both grounds; the `caM` clamp is the next unit, and the local engine's
worse-minimum outcome on 3 of 9 U 4f targets is a finding for the
local-engine work after it.

**The sweep.** Gaussian, Lorentzian, Voigt, GL, asym-GL and DS agree with
the server to 1e-15 across every bound. LACX with m > 0: up to 0.89 % of
amplitude when the kernel is wide against the peak (the tracked
discretisation gap). DS+G with m ≥ 0.05: the page's `laCasaXPS` quadrature
uses a step of 2·(6σ + 50β)/max(300, ⌈2·(6σ + 50β)/(β/3)⌉) — sized to the
Lorentzian core, blind to the Gaussian kernel — so at β = 2, m = 0.05 the
step is 0.67 eV against σ = 0.021 eV, the kernel weights sample nothing,
and the page's curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's
area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
865 committed components use DS+G, so no saved figure is affected; it is the
fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
recorded as its own unit. The general lesson repeats §6's: a harness that
evaluates one representative point per shape proves nothing about the range
the optimiser can reach.
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


def test_twin_sends_a_zero_as_a_zero():
    """A 0 is a value, not an absent field (Codex round 1: `or 50` / `or 0.1`)."""
    a = _peak(shape="asym-GL", glMix=0, asymmetry=0)
    s = peak_to_backend_spec(a, [a])
    assert s["gl_ratio"] == 0.0 and s["asymmetry"] == 0
    d = _peak(shape="DS", dsAlpha=0, dsGamma=0)
    s = peak_to_backend_spec(d, [d])
    assert s["alpha"] == 0.0 and s["gamma_asym"] == 0.0
    # a non-number still falls back to the default
    d2 = _peak(shape="DS", dsAlpha=None)
    assert peak_to_backend_spec(d2, [d2])["alpha"] == 0.1


def test_a_locked_value_outside_the_optimiser_bounds_is_held_as_requested():
    """lmfit clips a value to its bounds even when it does not vary: a DS+G
    with m locked at 0 (the page's delta-kernel branch) was fitted with
    m = 0.05, the free-parameter floor — a convolved curve the page never
    drew (A03 Codex round 2). A held parameter is held at its value."""
    x = np.arange(397.8, 385.8, -0.05)
    y = fitting._SHAPE_FUNCS["ds_g"](x, amplitude=12000.0, center=391.8, alpha=0.0, beta=0.5, m_gauss=0.0) + 5.0
    p = {"id": 1, "name": "d", "shape": "DSG_LA", "center": 391.8, "amplitude": 12000.0, "fwhm": 1.6,
         "laAlpha": 0.0, "laBeta": 0.5, "laM": 0.0, "fixLaAlpha": True, "fixLaM": True}
    res = fitting.run_fit(x, y, [peak_to_backend_spec(p, [p])], background_method="none", fit_kws={"method": "least_squares"})
    par = res["individual_peaks"][0]["params"]
    assert par["m_gauss"]["vary"] is False and par["m_gauss"]["value"] == 0.0
    assert par["alpha"]["vary"] is False and par["alpha"]["value"] == 0.0
    q = par
    drawn = fitting._SHAPE_FUNCS["ds_g"](np.asarray(res["energy"]), amplitude=q["amplitude"]["value"], center=q["center"]["value"],
                                         alpha=0.0, beta=q["beta"]["value"], m_gauss=0.0)
    np.testing.assert_allclose(np.asarray(res["individual_peaks"][0]["y"]), drawn, rtol=0, atol=1e-9 * 12000.0)


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
/bin/zsh -lc "rg -n 'function _invalidateFittedY|function updatePlot|_invalidateFittedY' templates/index.html; sed -n '7588,7625p' templates/index.html; sed -n '8300,8345p' templates/index.html; sed -n '1,120p' scripts/voigt_eta_measure.py; git log -5 --oneline" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
4519:function _invalidateFittedY() {
5166:  _invalidateFittedY();
5686:  _invalidateFittedY();
5715:  _invalidateFittedY();
5799:  _invalidateFittedY();
9203:function updatePlot() {
// alternative). runFit's own pushUndo is the single undo entry. A solution
// that moves a component more than 1 eV from where the student put it is the
// measured trap (a lower chi-square bought by a chemically absurd relocation),
// so that case — and only that case — asks first, naming the component and
// the distance.
async function useAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const shift = alt.largest_centre_shift_from_start;
  const name = _startsPeakName(shift.id);
  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  if (_historyPreview) _historyClearPreview();
  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
}

async function runFit(opts = {}) {
  if (!state.rawBE.length) { notify('Load a spectrum first.', 'red', true); return; }
  if (!state.peaks.length) { notify('Add at least one peak.', 'red'); return; }
  pushUndo();

  _showFitSpinner();
  document.getElementById('sb-msg').textContent = 'Fitting\u2026';

  // Capture the tab that owns this fit so that if the user switches tabs
  // mid-request, we can discard the stale result instead of corrupting the
  // now-active tab's state.
  const fittingTab = _opOwner();

  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);

  // Try Flask backend first
  let backendResult = null;
  try {
      for (let k = col; k <= n; k++) M[row][k] -= f * M[col][k];
    }
  }
  const x = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    if (Math.abs(M[i][i]) < 1e-15) { x[i] = 0; continue; }
    x[i] = M[i][n];
    for (let j = i + 1; j < n; j++) x[i] -= M[i][j] * x[j];
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
#!/usr/bin/env python3
"""A03 (2026-09-22): what the free-eta Voigt request did, on the committed targets.

Until A03 the page sent a "Voigt" component as pseudo_voigt_gl with gl_ratio
FREE from 0.3 while it drew, integrated and exported eta = 0.5. For every
committed target with a Voigt component this script fits the request BOTH
ways with the page's settings (Trust-Region, n_perturb 3) — (free) as sent
before A03, (fixed) eta held at 0.5 as sent since — and compares three
things per target:
  A. the 0.5 curve under the free fit's parameters (what the page drew for
     that fit) against the free fit's own curve — the reporting error that
     shipped, per component and as area fractions;
  B. the fixed fit against that 0.5 curve;
  C. the fixed fit against the free fit.
All three use the SERVER's curves and trapezoidal integration on the fitted
grid (non-Voigt components as the server fitted them); they characterise
the two requests, not a screen. The student-visible change on re-fitting a
SAVED project — the page's own integration of the saved peaks against the
page's integration of the refit — is scripts/voigt_saved_vs_refit.js.

Usage:
  python scripts/voigt_eta_measure.py targets.json out_dir shard n_shards   # one shard
  python scripts/voigt_eta_measure.py --summary out_dir                     # the numbers
targets.json is the optimizer-disagreement target file (uncommitted; built by
scripts/optimizer_disagreement_targets.js from the committed projects with
the page's CURRENT request builder). Both arms are constructed here
explicitly from the target's shapes — the target file's own Voigt specs are
never used as either baseline, so the numbers do not depend on which
builder produced the file (A03 Codex round 1).
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
            free = copy.deepcopy(t["specs"])
            fixed = copy.deepcopy(t["specs"])
            for i in vidx:
                free[i]["gl_ratio"] = 0.3                     # the request before A03: eta free from 0.3
                free[i]["fix_gl_ratio"] = False
                fixed[i]["gl_ratio"] = 0.5                    # the request since A03: eta held at 0.5
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-lQ5LmF9U' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-f6hU6sWQ' (errno=Operation not permitted)
afd5484 fix(A03): Codex round 4 (NO-GO x2) - eval parity evaluates a Voigt with the mix the server RECORDED for that fit, never "the contract or else the saved mix"; per-component statistic; sweep comment
be1f2fa fix(A03): Codex round 3 (NO-GO x2) - page clips DS+G alpha as the server does; measurement keeps display and upload grids apart; m locks pinned; Cl 2p battery re-based like U 4f
a61bd05 fix(A03): Codex round 2 (NO-GO x2) - saved side on the saved fit's grid with upload rounding; control arm at the rounded m; every shape parameter locked at each bound, which found lmfit clipping a HELD value to its bounds
4d623f5 fix(A03): Codex round 1 (NO-GO x2) - explicit measurement arms; release-note number from the page's own numbers; builders sent a mix or DS alpha of exactly 0 as the default; Voigt uncertainty note; caM attribution by a control arm
712e136 fix(A03): a Voigt is the fixed 50/50 mix on BOTH sides; page->server->page identity test; parameter-range sweep; U 4f gap re-measured

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\",\"-q\",\"-p\",\"no:cacheprovider\",\"tests/test_voigt_contract.py\",\"tests/autofit/test_u4f_parity_battery.py\",\"tests/autofit/test_b1s_cl2p_batteries.py\",\"tests/autofit/test_c1s_parity_battery.py\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 43022ms:
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
  duration_ms: 1150.786609
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
  duration_ms: 1243.924787
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
  duration_ms: 1138.517128
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
  duration_ms: 1123.078136
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
  duration_ms: 1142.951558
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
  duration_ms: 1258.003347
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
  duration_ms: 1227.126012
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
  duration_ms: 1210.605693
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
  duration_ms: 1238.901809
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
  duration_ms: 1277.03271
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
  duration_ms: 1243.84598
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
  duration_ms: 1263.412046
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
  duration_ms: 1265.502205
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
  duration_ms: 1285.478759
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
  duration_ms: 0.332065
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 16 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.130974
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 17 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.148906
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 18 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.143677
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 19 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.217915
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 20 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.277584
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
ok 21 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
  ---
  duration_ms: 10.721332
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 22 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.640588
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
  duration_ms: 2.931803
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
not ok 24 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1196.554411
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:380:3'
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
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:381:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
not ok 25 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1254.671191
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:380:3'
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
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:381:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Voigt
not ok 26 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1308.541167
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:380:3'
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
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:381:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: GL
not ok 27 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1296.701126
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:380:3'
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
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:381:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
not ok 28 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1194.793413
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:380:3'
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
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:381:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DS
not ok 29 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1231.440291
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:380:3'
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
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:381:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
not ok 30 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1215.227634
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:380:3'
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
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:381:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
not ok 31 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1293.866891
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:380:3'
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
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:381:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP
not ok 32 - (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1222.681201
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:388:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:389:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP
not ok 33 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1214.825289
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:388:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:330:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:372:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:389:19)
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
  duration_ms: 1147.462408
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
  duration_ms: 1227.66627
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
  duration_ms: 1138.861978
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
  duration_ms: 1114.219481
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
  duration_ms: 1129.03
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
  duration_ms: 1263.281213
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
  duration_ms: 1242.363585
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
  duration_ms: 1210.038941
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
  duration_ms: 1203.462377
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
  duration_ms: 1265.920749
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
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
not ok 44 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1238.941614
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
not ok 45 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1260.765513
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
not ok 46 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1255.139622
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
not ok 47 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1289.093706
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
not ok 48 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1200.776231
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
not ok 49 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1250.50716
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
not ok 50 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1290.02775
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
not ok 51 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1321.672411
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
not ok 52 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1195.48691
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
not ok 53 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1232.282184
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
not ok 54 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1212.190403
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
not ok 55 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1288.560992
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
not ok 56 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1238.653539
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
not ok 57 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1220.49367
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
not ok 58 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1197.586139
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
not ok 59 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1262.537405
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
not ok 60 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1202.520818
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
not ok 61 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1192.572263
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
not ok 62 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
  ---
  duration_ms: 1192.010545
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked (request and hold only)
not ok 63 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked (request and hold only)
  ---
  duration_ms: 1285.092254
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked (request and hold only)
not ok 64 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked (request and hold only)
  ---
  duration_ms: 1220.342724
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
not ok 65 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
  ---
  duration_ms: 1229.894532
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:200:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:201:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
not ok 66 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1218.885433
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:214:1'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:215:33)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
not ok 67 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1278.781617
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:225:1'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:233:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
not ok 68 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1250.314444
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:243:1'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:252:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
1..68
# tests 68
# suites 0
# pass 8
# fail 53
# cancelled 0
# skipped 0
# todo 7
# duration_ms 43090.729285

 succeeded in 7215ms:
............................................................................................................................................
140 passed in 6.72s

exec
/bin/zsh -lc "sed -n '4510,4540p' templates/index.html; sed -n '9203,9255p' templates/index.html; sed -n '5150,5173p' templates/index.html; sed -n '5780,5810p' templates/index.html; rg -n 'function renderPeakList|function syncLinked|shape = parent|shape = master' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
  return result;
}

// Clear stored background so updatePlot recomputes it
function _invalidateBgCache() {
  if (state.fitResult) state.fitResult.bgIntensity = null;
}

// Clear stored fit envelope so the fallback (modelFull + bg) is used after a manual peak edit
function _invalidateFittedY() {
  if (state.fitResult) state.fitResult.fittedY = null;
}

function _clampShirleyIter() {
  const el = document.getElementById('shirley-iter');
  let v = parseInt(el.value);
  if (isNaN(v)) return;
  if (v < 1) el.value = 1;
  else if (v > 50) el.value = 50;
}

// The background window. The user types two binding energies; the window
// is every grid point with lo <= BE <= hi, INCLUSIVE at both ends — the same
// rule getROIData uses for the ROI. This is the single definition shared by
// the preview (computeBackgroundCore) and both /api/fit request builders,
// which send end_idx = i1 + 1 because the backend slices Python-end-exclusive
// (unit 1c of docs/superpowers/plans/2026-09-02-background-architecture-
// sealed-fit-record.md, round-5 amendment — before 1c the builders sent the
// nearest grid index per bound and end_idx = i1, so the fit anchored one
// point inside the window the user drew).
// Returns inclusive indices { i0, i1 }. A blank/NaN bound, or fewer than two
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

// Switch a peak's lineshape and re-render. Shape-agnostic fields (id, name,
// color, center, amplitude, linked/linkOffset/linkRatio, fixCenter/
// fixAmplitude, isChargeReference) survive untouched; the width and every
// carried-over shape param are preserved by _applyShapeSwitch. Linked
// children share their parent's shape and shape-specific params, so the
// switch is applied to the whole multiplet family.
function _switchPeakShape(id, newShape) {
  const p = getPeak(id);
  if (!p || p.shape === newShape) return;
  if (!(newShape in SHAPE_PARAM_SCHEMA)) return;
  const parent = p.linked ? (getPeak(p.linked) || p) : p;
  if (parent.shape === newShape) return;
  const family = [parent, ...state.peaks.filter(q => q.linked === parent.id)];
  _pushUndoDebounced();
  for (const peak of family) _applyShapeSwitch(peak, newShape);
  _invalidateFittedY();
  for (const peak of family) renderPeakControls(peak);
  updatePlot();
}

// ═══════════════════════════════════════════════════
// ZOOM HELPERS
// ═══════════════════════════════════════════════════
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
5883:function renderPeakList() {

codex
I found a provenance hole in Undo: it restores a deep copy of the peaks, including `_backendParams`, but keeps the latest `fitResult.fittedY`. That permits the mixed-fit save the new helper assumes cannot occur. I’m testing whether it can fool the gate. The test runners also hit the read-only temp-directory restriction; I’m adjusting them to run without file writes.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import sys,copy,json,numpy as np
sys.path.insert(0,'\\''tests/autofit'\\'')
import battery_common as bc
from autofit.parity import *
from autofit.reference import ReferenceFit
for region in ['\\''C 1s'\\'','\\''B 1s'\\'','\\''U 4f'\\'','\\''Cl 2p'\\'']:
 fs=bc.battery_fits(region)
 print(region,'\\''tabs'\\'',len(fs),'\\''Voigts'\\'',sum(p['\\''shape'\\'']=='\\''Voigt'\\'' for r in fs for p in r.peaks),'\\''max parity'\\'',max(map(eval_parity_relmax,fs)))
r=next(r for r in bc.battery_fits('\\''U 4f'\\'') if r.project=='\\''UCl4_on_graphite.proj.zip'\\'' and r.name=='\\''U4f Scan_8'\\'')
r=copy.deepcopy(r)
s=next(s for s in r.backend_peak_specs() if str(s['\\''id'\\''])=='\\''3'\\'')
r.fit_result['\\''fittedY'\\'']=np.asarray(r.fit_result['\\''fittedY'\\''])+.035*evaluate_peak(r.roi_be,s)
print('\\''r4 corrupted legacy error'\\'',eval_parity_relmax(r))
x=np.linspace(392,380,241)
p={'\\''id'\\'':1,'\\''name'\\'':'\\''v'\\'','\\''shape'\\'':'\\''Voigt'\\'','\\''center'\\'':386,'\\''amplitude'\\'':3000,'\\''fwhm'\\'':1.4,'\\''glMix'\\'':90,'\\''_backendParams'\\'':{'\\''gl_ratio'\\'':{'\\''value'\\'':.5}}}
r=ReferenceFit('\\''synthetic'\\'','\\''s'\\'','\\''s'\\'',x,np.ones(len(x))*3000,0,[p],{}, {'\\''bgType'\\'':'\\''none'\\''})
s=r.backend_peak_specs()[0]
r.fit_result['\\''fittedY'\\'']=evaluate_peak(x,dict(s,gl_ratio=.9))
print('\\''r4 corrupt modern error'\\'',eval_parity_relmax(r))
for bp in [None,{}, {'\\''center'\\'':{'\\''value'\\'':386}}, {'\\''gl_ratio'\\'':{'\\''value'\\'':.3,'\\''vary'\\'':False}}, {'\\''gl_ratio'\\'':{'\\''value'\\'':.7,'\\''expr'\\'':'\\''p1_gl_ratio'\\''}}]:
 p['\\''_backendParams'\\'']=bp
 eta=recorded_voigt_eta(p)
 r.fit_result['\\''fittedY'\\'']=evaluate_peak(x,dict(s,gl_ratio=.5 if eta is None else eta))
 print('\\''metadata'\\'',bp,'\\''eta'\\'',eta,'\\''parity'\\'',eval_parity_relmax(r))
d=json.load(open('\\''docs/findings/a03/voigt_saved_vs_refit.json'\\''))
v=sorted(abs(c['\\''dArea_pct'\\'']) for t in d['\\''targets'\\''] for c in t['\\''comps'\\''] if c['\\''shape'\\'']=='\\''Voigt'\\'')
print('\\''component quantiles'\\'',len(v),v[55],np.median(v),v[98],np.quantile(v,.9),max(v),'\\''summary'\\'',d['\\''summary'\\''])
g=json.load(open('\\''docs/findings/a03/local_server_gap.json'\\''))
for region,ts in g['\\''regions'\\''].items():
 for t in ts:
  print(region,t['\\''target'\\''],[round(t['\\''max_'\\''+k],4) for k in ['\\''dCenter_meV'\\'','\\''dFwhm_pct'\\'','\\''dArea_pct'\\'','\\''dFrac_pp'\\'']], '\\''chi free/held'\\'',round(100*(t['\\''local_chi2r'\\'']/t['\\''server_chi2r'\\'']-1),3),round(100*(t['\\''local_chi2r'\\'']/t['\\''server_held_m_chi2r'\\'']-1),3))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 2417ms:
/Users/skyefortier/.matplotlib is not a writable directory
C 1s tabs 29 Voigts 0 max parity 1.1457298276804487e-07
B 1s tabs 4 Voigts 0 max parity 5.375504226217888e-07
U 4f tabs 29 Voigts 58 max parity 0.0007920224118505396
Cl 2p tabs 3 Voigts 2 max parity 6.815131681110832e-07
r4 corrupted legacy error 0.01656132412972441
r4 corrupt modern error 0.055166715288463876
metadata None eta None parity 0.0
metadata {} eta None parity 0.0
metadata {'center': {'value': 386}} eta None parity 0.0
metadata {'gl_ratio': {'value': 0.3, 'vary': False}} eta 0.3 parity 0.0
metadata {'gl_ratio': {'value': 0.7, 'expr': 'p1_gl_ratio'}} eta 0.7 parity 0.0
component quantiles 110 3.2748648211409437 3.2411875511686894 5.981860444395726 5.981862326317915 15.30072477001817 summary {'n_tabs': 55, 'n_converged': 55, 'dFrac_pp': {'median': 0.3640215087774637, 'p90': 0.5078511773600608, 'max': 0.6882978905471321}, 'gt_1pp': 0, 'voigt_dArea_pct_tab_max': {'median': 4.576983178447858, 'p90': 7.556793905528403, 'max': 15.30072477001817}, 'voigt_dArea_pct_component': {'median': 3.2748648211409437, 'p90': 5.981860444395726, 'max': 15.30072477001817}, 'n_voigt_components': 110}
C1s C1s Scan_0 [3.8402, 0.2886, 0.4179, 0.0399] chi free/held -0.097 -0.097
C1s C1s Scan_1 [2.635, 0.5017, 1.3959, 0.3223] chi free/held 0.062 0.062
C1s C1s Scan_2 [3.4887, 0.0729, 0.365, 0.0489] chi free/held -0.078 -0.078
C1s C1s Scan_3 [1.6115, 0.0576, 0.1344, 0.019] chi free/held -0.147 -0.147
C1s C1s Scan_4 [41.8708, 8.9695, 99.852, 15.0663] chi free/held -4.402 -4.402
C1s C1s Scan_5 [0.5678, 0.0303, 0.0575, 0.0048] chi free/held -0.033 -0.033
C1s C1s Scan_6 [2.0949, 0.1668, 0.237, 0.0218] chi free/held -0.359 -0.359
C1s C1s Scan_7 [1.3962, 0.2412, 0.3616, 0.0354] chi free/held -0.276 -0.276
C1s C1s Scan_8 [0.8341, 0.1247, 0.1788, 0.018] chi free/held 0.055 0.055
U4f U4f Scan_0 [1.5747, 0.2196, 0.1728, 0.0133] chi free/held 0.489 0.785
U4f U4f Scan_1 [4.2717, 1.3551, 1.9535, 0.1233] chi free/held 1.295 1.588
U4f U4f Scan_2 [1.9401, 1.3889, 0.3758, 0.0162] chi free/held -0.193 0.071
U4f U4f Scan_3 [2.9959, 2.5937, 1.7412, 0.1248] chi free/held -0.016 0.066
U4f U4f Scan_4 [26.5874, 5.295, 8.3249, 0.3304] chi free/held 9.575 5.35
U4f U4f Scan_5 [4.6761, 4.2618, 6.6486, 0.3493] chi free/held 10.075 9.656
U4f U4f Scan_6 [28.7684, 15.81, 8.883, 0.7659] chi free/held -5.015 1.084
U4f U4f Scan_7 [2.6234, 0.3585, 0.4878, 0.0358] chi free/held 0.396 0.693
U4f U4f Scan_8 [5.6811, 5.0171, 8.3053, 0.3229] chi free/held 12.745 13.077

exec
/bin/zsh -lc "sed -n '10155,10185p' templates/index.html; sed -n '5883,5905p' templates/index.html; nl -ba autofit/parity.py | sed -n '168,205p'; nl -ba scripts/voigt_saved_vs_refit.js | tail -18; sed -n '1,85p' tests/js/lineshape_roundtrip_backend.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
  };
  // B2: compound markers are GLOBAL (project-meta scope, not per-tab). Additive +
  // optional — omit the key when there are no markers (serializer returns null).
  // Top-level version stays 3. (Flows to both the .proj.json `{...meta}` and the
  // .proj.zip manifest `{...meta}`, which reuse this same meta object.)
  const _refCM = RefCore.serializeRefCompoundMarkers(_refCompoundMarkers);
  if (_refCM) meta.refCompoundMarkers = _refCM;

  if (tabs.length < 5) {
    const data = { ...meta, tabs: tabs.map(buildTabData) };
    _downloadBlob(
      new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}),
      fname + '.proj.json'
    );
  } else {
    const zip = new JSZip();
    const manifest = { ...meta, spectra: [] };
    tabs.forEach((t, i) => {
      const zname = `spectrum_${i}_${t.name.replace(/[^a-zA-Z0-9_-]/g, '_')}.json`;
      zip.file(zname, JSON.stringify(buildTabData(t), null, 2));
      manifest.spectra.push({ index: i, filename: zname, name: t.name, isSurvey: t.isSurvey });
    });
    zip.file('manifest.json', JSON.stringify(manifest, null, 2));
    const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE', compressionOptions: { level: 6 } });
    _downloadBlob(blob, fname + '.proj.zip');
  }
  notify('Project saved (' + tabs.length + ' tab' + (tabs.length !== 1 ? 's' : '') + ').', 'green');
}

// ── Unified Load ─────────────────────────────────────
function loadSession() {
function renderPeakList() {
  _clearDisallowedChargeRef();
  _updateLocalModelBanner();
  const el = document.getElementById('peak-list');
  const empty = document.getElementById('peak-empty');
  // Preserve which peak cards are expanded before clearing
  const expandedIds = new Set();
  el.querySelectorAll('.peak-body.open').forEach(b => {
    const m = b.id.match(/peak-body-(\d+)/);
    if (m) expandedIds.add(Number(m[1]));
  });
  el.innerHTML = '';
  empty.style.display = state.peaks.length ? 'none' : 'block';
  const clearWrap = document.getElementById('peak-clear-wrap');
  if (clearWrap) clearWrap.style.display = state.peaks.length ? 'block' : 'none';
  document.getElementById('sb-peaks').textContent = state.peaks.length;
  _updateLockAllBtn();

  // Compute total area for percentage (using ROI data if available)
  const { be: _roiBE } = (typeof getROIData === 'function' && state.rawBE.length) ? getROIData() : { be: [] };
  const _peakAreas = {};
  let totalArea = 0;
  if (_roiBE.length) {
   168	    return float(np.max(np.abs(np.asarray(saved_be, dtype=float) - roi))) <= tol
   169	
   170	
   171	def recorded_voigt_eta(p: dict) -> float | None:
   172	    """The mix the server actually fitted this Voigt with, from the record
   173	    the page keeps of that fit (``p._backendParams.gl_ratio.value``, written
   174	    by applyBackendResult): 0.5 for a fit under the A03 request, the free or
   175	    held value the request BEFORE A03 sent for an older save. None when the
   176	    peak carries no such record (never server-fitted)."""
   177	    bp = p.get("_backendParams")
   178	    g = bp.get("gl_ratio") if isinstance(bp, dict) else None
   179	    v = g.get("value") if isinstance(g, dict) else None
   180	    return float(v) if isinstance(v, (int, float)) and np.isfinite(v) else None
   181	
   182	
   183	def eval_parity_relmax(rf: ReferenceFit, voigt_eta: str = "recorded") -> float:
   184	    """
   185	    Max |python_eval − saved fittedY| / max|fittedY| on the reconstructed
   186	    ROI grid.  Requires ``grid_matches(rf)``.
   187	
   188	    voigt_eta: "recorded" (default) evaluates each Voigt with the mix the
   189	    server recorded for the fit that produced ``fittedY``
   190	    (``recorded_voigt_eta``; the contract's 0.5 when there is no record) —
   191	    ONE deterministic choice from the record itself, never "whichever
   192	    passes" (A03 Codex round 4). "contract" evaluates every Voigt at the
   193	    page's current request (eta = 0.5, A03 2026-09-22); saves made under the
   194	    old request (eta free from 0.3) cannot reproduce their own fittedY that
   195	    way, and that difference is the A03 change, not a numerics regression.
   196	    """
   197	    fittedY = np.asarray(rf.fit_result["fittedY"], dtype=float)
   198	    specs = rf.backend_peak_specs()
   199	    if voigt_eta == "recorded":   # backend_peak_specs keeps the peaks' order
   200	        specs = [dict(s, gl_ratio=recorded_voigt_eta(p))
   201	                 if p.get("shape") == "Voigt" and recorded_voigt_eta(p) is not None else s
   202	                 for s, p in zip(specs, rf.peaks)]
   203	    model = evaluate_model(rf.roi_be, specs)
   204	    i0, i1 = rf.bg_indices()
   205	    bg = background_like_run_fit(
    62	      dArea_pct: aS[i] ? 100 * (aR[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aR[i] / tR - aS[i] / tS) }));
    63	    const rec = { project: zp, tab: t.name, server_success: srv.success, chi2r: srv.chi2r, saved_grid: t.fitResult.be && t.fitResult.be.length ? 'fitResult.be' : 'roi',
    64	      max_dFrac_pp: Math.max(...comps.map(c => Math.abs(c.dFrac_pp))),
    65	      max_voigt_dArea_pct: Math.max(...comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct))), comps };
    66	    out.targets.push(rec);
    67	    console.error(zp.slice(0, 28), t.name, 'server', srv.success, 'max Δfrac', rec.max_dFrac_pp.toFixed(2), 'pp, max Voigt Δarea', rec.max_voigt_dArea_pct.toFixed(1), '%');
    68	  }
    69	}
    70	const ok = out.targets.filter(r => r.server_success);
    71	const q = v => { v = [...v].sort((a, b) => a - b); return { median: v[Math.floor(v.length / 2)], p90: v[Math.floor(0.9 * (v.length - 1))], max: v[v.length - 1] }; };
    72	const voigtComps = ok.flatMap(r => r.comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct)));
    73	out.summary = { n_tabs: out.targets.length, n_converged: ok.length,
    74	  dFrac_pp: q(ok.map(r => r.max_dFrac_pp)),                           // per tab: the largest fraction move
    75	  gt_1pp: ok.filter(r => r.max_dFrac_pp > 1).length,
    76	  voigt_dArea_pct_tab_max: q(ok.map(r => r.max_voigt_dArea_pct)),     // per tab: the largest Voigt area change
    77	  voigt_dArea_pct_component: q(voigtComps), n_voigt_components: voigtComps.length };   // per component, all Voigts
    78	console.error(JSON.stringify(out.summary));
    79	fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/voigt_saved_vs_refit.json'), JSON.stringify(out, null, 1));
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

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require('\\''child_process'\\'');const old=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(/python/.test(file)&&args&&args[0].endsWith('\\''.py'\\'')){const script=args[0];args=['\\''-B'\\'','\\''-c'\\'','\\''import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; p=sys.argv.pop(1); sys.argv[0]=p; runpy.run_path(p,run_name=\"__main__\")'\\'',script,...args.slice(1)];}return old(file,args,opts)};
require('\\''./tests/js/lineshape_roundtrip.test.js'\\'');require('\\''./tests/js/lineshape_parity.test.js'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function fn(name){const a=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l));let d=0;for(let i=a;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++;if(c==='\\''}'\\'')d--;}if("'!d)return lines.slice(a,i+1).join('"'\\''\\n'\\'');}throw Error(name);}
const state={peaks:[],fitResult:null,ccShift:0,nextId:2};
const t={id:'\\''t'\\'',name:'\\''test'\\'',undoStack:[],redoStack:[],rawBE:[],rawIntensity:[],ui:{bgType:'\\''none'\\''}};
const noop=()=>{};
const document={getElementById:()=>({value:'\\''test'\\'',classList:{},style:{}})};
let savedBlob;
const tabManager={activeId:'\\''t'\\'',tabs:[t],_getTab:()=>t,_captureUI:()=>t.ui};
const sync=html.match(/  _syncActiveToRecord\\(\\) \\{[\\s\\S]*?\\n  \\}/)[0].trim();
tabManager._syncActiveToRecord=new Function('\\''state'\\'','\\''document'\\'','\\''return function '\\''+sync)(state,document);
const names=['\\''getPeak'\\'','\\''_applyBackendParams'\\'','\\''applyBackendResult'\\'','\\''_peaksSnapshot'\\'','\\''undo'\\'','\\''_doSaveProject'\\'','\\''peakToBackendSpec'\\''];
const vars={state,document,tabManager,_historyTab:()=>t,_flushUndoDebounce:noop,_restoreSnapshotEndpointAvg:noop,_restoreSnapshotProvenance:noop,renderPeakList:noop,updatePlot:noop,renderResults:noop,_updateUndoButtons:noop,_applySupport:noop,_startsLiveKey:()=>'\\'''\\'',_provenanceOf:()=>null,_startsForSave:()=>null,_startsIfCurrent:()=>null,_startsRecordKey:()=>'\\'''\\'',_isLocalFit:()=>false,_localFitCaveat:()=>null,RefCore:{serializeRefOverlays:()=>null,serializeRefCompoundMarkers:()=>null},_refCompoundMarkers:[],_downloadBlob:b=>savedBlob=b,notify:noop};
const e=new Function(...Object.keys(vars),names.map(fn).join('\\''\\n'\\'')+'\\'';return {'\\''+names.join('\\'','\\'')+'\\''};'\\'')(...Object.values(vars));
const py='\\''import tempfile; tempfile.tempdir=\"/tmp\"; import json,sys,numpy as np; from fitting import run_fit; from autofit.parity import evaluate_peak; d=json.load(sys.stdin); x=np.linspace(392,380,241); s=d[\"spec\"]; y=evaluate_peak(x,dict(s,gl_ratio=.9)); r=run_fit(x,y,[s],background_method=\"none\"); print(json.dumps(r))'\\'';
function fit(s){return JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python'\\'',['\\''-B'\\'','\\''-c'\\'',py],{input:JSON.stringify({spec:s}),encoding:'\\''utf8'\\''}));}
(async()=>{
state.peaks=[{id:1,name:'\\''v'\\'',shape:'\\''Voigt'\\'',center:386,amplitude:3000,fwhm:1.4,glMix:90}];
const oldspec={...e.peakToBackendSpec(state.peaks[0]),gl_ratio:.3,fix_gl_ratio:false};
const old=fit(oldspec);e.applyBackendResult(old);state.fitResult={fittedY:old.fitted_y,be:old.energy};
t.rawBE=old.energy;t.rawIntensity=old.fitted_y;
t.undoStack.push(e._peaksSnapshot());
state.peaks[0].shape='\\''GL'\\'';state.peaks[0].glMix=90;state.fitResult.fittedY=null;
t.undoStack.push(e._peaksSnapshot());
const latest=fit(e.peakToBackendSpec(state.peaks[0]));e.applyBackendResult(latest);
state.fitResult={fittedY:latest.fitted_y,be:latest.energy};
e.undo();e.undo();await e._doSaveProject();
const rec=JSON.parse(await savedBlob.text()).tabs[0];
console.log('\\''saved shape'\\'',rec.peaks[0].shape,'\\''metadata eta'\\'',rec.peaks[0]._backendParams.gl_ratio.value,'\\''current result retained'\\'',rec.fitResult.fittedY.every((v,i)=>v===latest.fitted_y[i]));
const check='\\''import tempfile; tempfile.tempdir=\"/tmp\"; import json,sys,numpy as np; from autofit.reference import ReferenceFit; from autofit.parity import eval_parity_relmax; d=json.load(sys.stdin); r=ReferenceFit(\"undo\",\"t\",\"t\",np.array(d[\"rawBE\"]),np.array(d[\"rawIntensity\"]),0,d[\"peaks\"],d[\"fitResult\"],{\"bgType\":\"none\"}); print(\"recorded error\",eval_parity_relmax(r),\"contract error\",eval_parity_relmax(r,voigt_eta=\"contract\"))'\\'';
console.log(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python'\\'',['\\''-B'\\'','\\''-c'\\'',check],{input:JSON.stringify(rec),encoding:'\\''utf8'\\''}));
})().catch(e=>{console.error(e);process.exitCode=1});'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 5143ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
saved shape Voigt metadata eta 0.8999999999999999 current result retained true
/Users/skyefortier/.matplotlib is not a writable directory
recorded error 1.5158245029548803e-16 contract error 0.055166715288463876


exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '2440,2461p'; nl -ba tests/autofit/test_u4f_parity_battery.py | sed -n '32,45p'; nl -ba tests/autofit/test_b1s_cl2p_batteries.py | sed -n '28,39p'; sed -n '124,140p' scripts/voigt_eta_measure.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
  2440	
  2441	function undo() {
  2442	  _flushUndoDebounce();     // never undo past a pending burst
  2443	  const t = _historyTab();
  2444	  if (!t || !t.undoStack.length) return;
  2445	  const snap = t.undoStack.pop();
  2446	  // Mirror the averaging into the redo entry only when the undo entry
  2447	  // carried one, so a redo re-applies exactly what the action did.
  2448	  t.redoStack.push(_peaksSnapshot(snap._endpointAvg !== undefined
  2449	    ? { endpointAvg: document.getElementById('bg-endpoint-avg')?.value } : null));
  2450	  state.peaks = snap;
  2451	  _restoreSnapshotEndpointAvg(t, snap);
  2452	  _restoreSnapshotProvenance(t, snap);
  2453	  renderPeakList();
  2454	  updatePlot();
  2455	  renderResults();   // the restored model's designation (or its absence) must be visible immediately
  2456	  _updateUndoButtons();
  2457	}
  2458	
  2459	function redo() {
  2460	  _flushUndoDebounce();
  2461	  const t = _historyTab();
    32	# across PROCESSES on one platform, but 1.9e-3 across PLATFORMS (first CI
    33	# run on ubuntu/openBLAS vs the macOS/arm64 fixture, 2026-07-04 — fwhm
    34	# 3.00971 vs frozen 3.00396 on that tab).  3e-3 covers the measured
    35	# cross-platform wobble with ~1.6x headroom while still catching any real
    36	# numerics change (C 1s pins the shared machinery at 1e-6).
    37	# Eval-parity across all 29 eligible fits: median 6.0e-3, max 1.12e-2
    38	# (bg-anchor drift) — 1.5e-2 keeps ~34% headroom without masking a real
    39	# 2%-level regression (Codex Stage-3 finding #4).
    40	EVAL_TOL = 1.5e-2
    41	FIXTURE_RTOL = 3e-3
    42	
    43	_FITS = bc.battery_fits(REGION)
    44	_IDS = [f"{rf.project}::{rf.name}" for rf in _FITS]
    45	_EXPECTED = bc.load_fixture(FIXTURE)
    28	# Cl 2p eval parity is bounded by the same bg-anchor drift documented in
    29	# battery_common.py (measured: 1.7e-2 on the uncorrected Scan_1 tab;
    30	# ≤6.8e-7 on the corrected tabs).
    31	CL2P_EVAL_TOL = 2.5e-2
    32	
    33	
    34	def test_b1s_roster():
    35	    bc.assert_roster(_B1S, _B1S_EXPECTED, min_size=3, min_projects=2,
    36	                     gen_script="scripts/gen_region_battery_fixture.py 'B 1s'")
    37	
    38	
    39	def test_cl2p_roster():
          f"{sum(e > 0.99 for e in etas)} at 1 (pure Lorentzian), {sum(0.4 <= e <= 0.6 for e in etas)} within 0.4–0.6")
    e = [abs(c) for c in comp]
    print(f"per-Voigt-component DISPLAYED area vs the fitted curve (%): {q(e)}; > 10 % on {sum(v > 10 for v in e)} of {len(e)}; "
          f"displayed high (eta < 0.5) {sum(c > 0 for c in comp)}, low {sum(c < 0 for c in comp)}")
    print(f"A. displayed vs free-fit fractions, max |delta| pp per target: {q(dA)}; > 1 pp on {sum(v > 1 for v in dA)} targets")
    print(f"B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: {q(dB)}; > 1 pp on {sum(v > 1 for v in dB)} targets")
    print(f"C. fixed refit vs free fit, max |delta| pp: {q(dC)}; > 1 pp on {sum(v > 1 for v in dC)} targets")
    print(f"chi2r fixed/free: {q(chi_ratio)}; fixed lower on {sum(v < 1 for v in chi_ratio)} targets (the free fit in a worse minimum)")


if __name__ == "__main__":
    if sys.argv[1] == "--summary":
        summary(sys.argv[2])
    else:
        measure(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile;tempfile.tempdir=\"/tmp\"
import numpy as np
from fitting import run_fit
from autofit.reference import peak_to_backend_spec
from autofit.parity import evaluate_peak
p={\"id\":1,\"name\":\"v\",\"shape\":\"Voigt\",\"center\":386,\"amplitude\":3000,\"fwhm\":1.4,\"glMix\":90,\"fixCenter\":True,\"fixAmplitude\":True,\"fixFwhm\":True}
s=peak_to_backend_spec(p,[p]);x=np.linspace(392,380,241);y=evaluate_peak(x,s)
r=run_fit(x,y,[s],background_method=\"none\")
print(r[\"success\"],r.get(\"message\"),r[\"individual_peaks\"][0][\"params\"][\"gl_ratio\"])'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 1586ms:
/Users/skyefortier/.matplotlib is not a writable directory
False Invalid Input Parameters. I.e. more variables than data points given, tolerance < 0.0, or no data provided. Could not estimate error-bars. {'value': 0.5, 'stderr': None, 'vary': False, 'expr': None, 'min': 0.0, 'max': 1.0}

 succeeded in 101117ms:
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
  duration_ms: 1940.855004
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
ok 2 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1814.307117
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
ok 3 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1719.595642
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
ok 4 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1891.028159
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
ok 5 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1909.242462
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
ok 6 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1864.298089
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 7 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1833.044003
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
  duration_ms: 1784.433312
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
  duration_ms: 1874.422382
  type: 'test'
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
ok 10 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1747.449092
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
ok 11 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1737.343482
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
ok 12 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1892.649274
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
ok 13 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1747.851945
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
ok 14 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1729.413695
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
ok 15 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1764.789855
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
ok 16 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1717.602723
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
ok 17 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1729.174997
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
ok 18 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1751.53768
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
ok 19 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1679.964421
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
ok 20 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1642.868053
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
ok 21 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1699.464883
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
ok 22 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1615.663799
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
ok 23 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1632.314002
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
ok 24 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1665.399819
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
ok 25 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1655.95898
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
ok 26 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1666.197902
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
ok 27 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1754.262423
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
ok 28 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1677.845123
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
ok 29 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
  ---
  duration_ms: 1741.844357
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked (request and hold only)
ok 30 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked (request and hold only)
  ---
  duration_ms: 1815.7944
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked (request and hold only)
ok 31 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked (request and hold only)
  ---
  duration_ms: 1676.12092
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
ok 32 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
  ---
  duration_ms: 1662.62263
  type: 'test'
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
ok 33 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1662.384453
  type: 'test'
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
ok 34 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1608.00584
  type: 'test'
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
ok 35 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1618.588975
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Gaussian
ok 36 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1669.881563
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
ok 37 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1593.643065
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: GL
ok 38 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1605.224982
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Voigt
ok 39 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1671.734893
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DS
ok 40 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1609.425081
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
ok 41 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1631.312599
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)
not ok 42 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1678.034223
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
ok 43 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1592.459921
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed
not ok 44 - (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed # TODO DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above
  ---
  duration_ms: 1616.168901
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
ok 45 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1706.506539
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
ok 46 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1602.682531
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
ok 47 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1617.405884
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
ok 48 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1739.402167
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
ok 49 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1691.06166
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 50 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.544111
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 51 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.227612
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 52 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.437796
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 53 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.160108
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 54 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.204745
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 55 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.253057
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
ok 56 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
  ---
  duration_ms: 11.330159
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 57 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.341238
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
ok 58 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 3.045322
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
ok 59 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1743.632368
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
ok 60 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1671.300028
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Voigt
ok 61 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1616.882354
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: GL
ok 62 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1602.212225
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
ok 63 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1679.623829
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DS
ok 64 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1648.843196
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
ok 65 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1606.757579
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
ok 66 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1698.38362
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP
not ok 67 - (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 2077.809372
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:388:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA (m > 0): 36 of 36 parameter combinations diverge; worst 1.129e+55 % of amplitude at {"laAlpha":0.49,"laBeta":2,"laM":0.05}'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:390:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP
not ok 68 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1802.358821
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:388:3'
  failureType: 'testCodeFailure'
  error: 'LACX (m > 0): 81 of 108 parameter combinations diverge; worst 8.941e-1 % of amplitude at {"caAlpha":5,"caBeta":5,"caM":50,"fwhm":0.1}'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:390:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
1..68
# tests 68
# suites 0
# pass 61
# fail 0
# cancelled 0
# skipped 0
# todo 7
# duration_ms 101152.154289

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile;tempfile.tempdir='\\''/tmp'\\''
import copy,json,subprocess,numpy as np
from fitting import run_fit
from autofit.reference import ReferenceFit,peak_to_backend_spec,apply_backend_params
from autofit.parity import evaluate_peak,eval_parity_relmax
x=np.linspace(392,380,241)
p={'\\''id'\\'':1,'\\''name'\\'':'\\''v'\\'','\\''shape'\\'':'\\''GL'\\'','\\''center'\\'':386.,'\\''amplitude'\\'':3000.,'\\''fwhm'\\'':1.4,'\\''glMix'\\'':90,'\\''fixGlMix'\\'':True}
s=peak_to_backend_spec(p,[p]);y=evaluate_peak(x,dict(s,gl_ratio=.5))
old=run_fit(x,y,[s],background_method='\\''none'\\'')
p['\\''_backendParams'\\'']=old['\\''individual_peaks'\\''][0]['\\''params'\\'']
# User switches shape and sets the three starting values to those of the exact Voigt data.
p['\\''shape'\\'']='\\''Voigt'\\''
snap=copy.deepcopy(p)
new=run_fit(x,y,[peak_to_backend_spec(p,[p])],background_method='\\''none'\\'')
apply_backend_params(p,new['\\''individual_peaks'\\''][0]['\\''params'\\'']);p['\\''_backendParams'\\'']=new['\\''individual_peaks'\\''][0]['\\''params'\\'']
js=\"\"\"const fs=require('\\''fs'\\''),h=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),d=JSON.parse(fs.readFileSync(0,'\\''utf8'\\''));
const state={peaks:[d.p],fitResult:d.fr},t={undoStack:[[d.snap]],redoStack:[]};
const noop=()=>{};const code=h.match(/function undo\\\\(\\\\) \\\\{[\\\\s\\\\S]*?\\\\n\\\\}/)[0];
new Function('\\''state'\\'','\\''_historyTab'\\'','\\''_flushUndoDebounce'\\'','\\''_peaksSnapshot'\\'','\\''_restoreSnapshotEndpointAvg'\\'','\\''_restoreSnapshotProvenance'\\'','\\''renderPeakList'\\'','\\''updatePlot'\\'','\\''renderResults'\\'','\\''_updateUndoButtons'\\'',code+'\\'';undo();'\\'')(state,()=>t,noop,()=>state.peaks,noop,noop,noop,noop,noop,noop);
console.log(JSON.stringify(state));\"\"\"
d=json.loads(subprocess.check_output(['\\''node'\\'','\\''-e'\\'',js],input=json.dumps({'\\''p'\\'':p,'\\''snap'\\'':snap,'\\''fr'\\'':{'\\''be'\\'':new['\\''energy'\\''],'\\''fittedY'\\'':new['\\''fitted_y'\\'']}}).encode()))
r=ReferenceFit('\\''undo'\\'','\\''t'\\'','\\''t'\\'',x,y,0,d['\\''peaks'\\''],d['\\''fitResult'\\''],{'\\''bgType'\\'':'\\''none'\\''})
print('\\''old GL success'\\'',old['\\''success'\\''],'\\''new Voigt success'\\'',new['\\''success'\\''])
print('\\''earlier metadata eta'\\'',d['\\''peaks'\\''][0]['\\''_backendParams'\\'']['\\''gl_ratio'\\'']['\\''value'\\''],'\\''latest fitted eta'\\'',new['\\''individual_peaks'\\''][0]['\\''params'\\'']['\\''gl_ratio'\\'']['\\''value'\\''])
print('\\''recorded error'\\'',eval_parity_relmax(r),'\\''contract error'\\'',eval_parity_relmax(r,voigt_eta='\\''contract'\\''))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 1689ms:
/Users/skyefortier/.matplotlib is not a writable directory
old GL success True new Voigt success True
earlier metadata eta 0.9 latest fitted eta 0.5
recorded error 0.055166715288463876 contract error 0.0

codex
The stale-metadata case is reproduced: after GL→Voigt, fitting, and Undo, the saved peaks can retain η=0.9 from the earlier GL fit while their values and retained curve exactly match the new η=0.5 Voigt fit. The recorded gate reports 5.52% error; contract evaluation reports zero.

Both round-4 corruption reproducers now fail, and the targeted tests pass: 140 Python tests, plus 61 JavaScript tests with seven existing TODOs. I also found a median-convention discrepancy and stale parity-error comments.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile;tempfile.tempdir='\\''/tmp'\\''
import sys,statistics,json
sys.path.insert(0,'\\''tests/autofit'\\'')
import battery_common as bc
from autofit.parity import eval_parity_relmax
for reg in ['\\''U 4f'\\'','\\''Cl 2p'\\'']:
 a=[eval_parity_relmax(r) for r in bc.battery_fits(reg)]
 print(reg,'\\''median'\\'',statistics.median(a),'\\''max'\\'',max(a))
d=json.load(open('\\''docs/findings/a03/voigt_saved_vs_refit.json'\\''))
print('\\''saved grids'\\'',sum(t['\\''saved_grid'\\'']=='\\''fitResult.be'\\'' for t in d['\\''targets'\\'']),'\\''projects'\\'',len(set(t['\\''project'\\''] for t in d['\\''targets'\\''])))
v=sorted(abs(c['\\''dArea_pct'\\'']) for t in d['\\''targets'\\''] for c in t['\\''comps'\\''] if c['\\''shape'\\'']=='\\''Voigt'\\'')
print('\\''middle values'\\'',v[54:56])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "nl -ba tests/autofit/battery_common.py | sed -n '20,44p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    20	DATA = os.path.join(REPO, "docs", "autofit", "test_data")
    21	FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    22	
    23	# Default tolerances (C 1s levels).  Per-region batteries may override:
    24	#
    25	# - eval_tol: bounded below by BACKGROUND-ANCHOR DRIFT — ui bg-start/end
    26	#   fields move with post-fit charge-correction nudges and round to 0.1 eV,
    27	#   so the nearest-index anchors can shift ±1 grid point vs fit time; for
    28	#   'smart' backgrounds that perturbs the recomputed background by
    29	#   O(100 counts) mid-window (measured U 4f: eval relmax ~7e-3 with the
    30	#   deviation profile exactly matching the background, not the shapes).
    31	# - fixture_rtol: bounded below by CROSS-PROCESS FP wobble in the LACX
    32	#   convolution path (~6e-6 relative on fitted params; exactly 0.0 within
    33	#   one process).  Simple shapes (C 1s) reproduce at 1e-6.
    34	EVAL_PARITY_TOL = 1e-5
    35	CENTER_DRIFT_TOL_EV = 0.005
    36	REL_DRIFT_TOL = 0.005
    37	FIXTURE_CHI_RTOL = 1e-6
    38	FIXTURE_PARAM_RTOL = 1e-6
    39	
    40	
    41	def battery_fits(region):
    42	    fits = []
    43	    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
    44	        for rf in load_reference_fits(zp):
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Jvu0DmWT' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uF7Jgvxx' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_r5_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_r5_verdict_runB.md
?? docs/autofit/codex/a03_voigt_eta_recheck4_prompt.txt

 succeeded in 1981ms:
/Users/skyefortier/.matplotlib is not a writable directory
U 4f median 1.9506420291552006e-07 max 0.0007920224118505396
Cl 2p median 6.132823293509703e-07 max 6.815131681110832e-07
saved grids 41 projects 6
middle values [3.207510281196435, 3.2748648211409437]

codex
No BLOCKER found. Three findings remain:

- **MAJOR — Recorded η is not reliably tied to saved `fittedY`.** [autofit/parity.py:199](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/autofit/parity.py:199) trusts peak metadata, but [templates/index.html:2450](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:2450) restores peaks during Undo without restoring or invalidating `fitResult`. Concrete reproducer: fit GL with η locked at 0.9; switch to Voigt and set the exact parameters of synthetic η=0.5 data; Run Fit successfully; Undo; save. Undo restores the earlier GL metadata alongside the correct Voigt parameters and latest curve. **Recorded evaluation errors by 5.5167%; contract evaluation errors by zero.** `_syncActiveToRecord` and project serialization preserve that mismatch. Restore/invalidate the paired result, or establish fit-level provenance before trusting recorded η.

- **MINOR — “Median” uses an undocumented upper-middle convention.** [scripts/voigt_saved_vs_refit.js:71](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:71). For the committed 110 components, the middle values are **3.207510% and 3.274865%**. Their conventional median is **3.241188%, rounding to 3.2%**, whereas the script selects the latter and publishes **3.3%**. The 55-tab median is unaffected. Use the conventional median consistently with `voigt_eta_measure.py`, or explicitly label the convention.

- **MINOR — Parity-error comments retain superseded measurements.** [test_u4f_parity_battery.py:37](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/autofit/test_u4f_parity_battery.py:37) claims median `6.0e-3`, maximum `1.12e-2`; current recorded evaluation gives **`1.95e-7` and `7.92e-4`**. [test_b1s_cl2p_batteries.py:28](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/autofit/test_b1s_cl2p_batteries.py:28) still claims `1.7e-2`; all three tabs are now **≤`6.82e-7`**. These comments incorrectly justify the retained tolerance headroom.

Round-4 closure: both original corruption reproducers now fail; per-tab and per-component populations are separated; the sweep’s lock comment is corrected. Linked expression values, legacy held η, and missing `gl_ratio` behave as specified. C 1s and B 1s contain no Voigts and are unaffected. The remaining published measurement tables agree with the committed artifacts, subject to the median issue above.

Validation: **140 Python tests passed; 61 JavaScript tests passed, seven existing TODOs.** Read-only; no files changed.

**VERDICT: NO-GO**
tokens used
106,921
No BLOCKER found. Three findings remain:

- **MAJOR — Recorded η is not reliably tied to saved `fittedY`.** [autofit/parity.py:199](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/autofit/parity.py:199) trusts peak metadata, but [templates/index.html:2450](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:2450) restores peaks during Undo without restoring or invalidating `fitResult`. Concrete reproducer: fit GL with η locked at 0.9; switch to Voigt and set the exact parameters of synthetic η=0.5 data; Run Fit successfully; Undo; save. Undo restores the earlier GL metadata alongside the correct Voigt parameters and latest curve. **Recorded evaluation errors by 5.5167%; contract evaluation errors by zero.** `_syncActiveToRecord` and project serialization preserve that mismatch. Restore/invalidate the paired result, or establish fit-level provenance before trusting recorded η.

- **MINOR — “Median” uses an undocumented upper-middle convention.** [scripts/voigt_saved_vs_refit.js:71](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:71). For the committed 110 components, the middle values are **3.207510% and 3.274865%**. Their conventional median is **3.241188%, rounding to 3.2%**, whereas the script selects the latter and publishes **3.3%**. The 55-tab median is unaffected. Use the conventional median consistently with `voigt_eta_measure.py`, or explicitly label the convention.

- **MINOR — Parity-error comments retain superseded measurements.** [test_u4f_parity_battery.py:37](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/autofit/test_u4f_parity_battery.py:37) claims median `6.0e-3`, maximum `1.12e-2`; current recorded evaluation gives **`1.95e-7` and `7.92e-4`**. [test_b1s_cl2p_batteries.py:28](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/autofit/test_b1s_cl2p_batteries.py:28) still claims `1.7e-2`; all three tabs are now **≤`6.82e-7`**. These comments incorrectly justify the retained tolerance headroom.

Round-4 closure: both original corruption reproducers now fail; per-tab and per-component populations are separated; the sweep’s lock comment is corrected. Linked expression values, legacy held η, and missing `gl_ratio` behave as specified. C 1s and B 1s contain no Voigts and are unaffected. The remaining published measurement tables agree with the committed artifacts, subject to the median issue above.

Validation: **140 Python tests passed; 61 JavaScript tests passed, seven existing TODOs.** Read-only; no files changed.

**VERDICT: NO-GO**
