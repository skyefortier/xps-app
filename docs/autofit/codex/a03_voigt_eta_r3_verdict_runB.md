OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0c7ce-b1d0-7990-87fd-4be672beb119
--------
user
RECHECK, round 3, of unit A03: branch fix-voigt-eta-identity, git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round 2 (docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md / runB.md, both NO-GO) confirmed round-1 items 1, 3, 4 closed and found: (1) MAJOR scripts/voigt_saved_vs_refit.js integrated the saved side on the current ROI grid where Results uses fitResult.be, and sent the refit request without the page's upload rounding (4 dp energies, 2 dp intensities; the rounding also sets the seed); (2) MINOR the control arm in scripts/local_server_gap.js held LA m at the stored fractional value where the local engine rounds it; (3) MINOR "every shape parameter locked at its bounds" was seven cases; (4) MINOR numbers ("10-13 %", "12 %", stale test counts).

What changed since (plan §9 round 2; commit "fix(A03): Codex round 2"): the saved side integrates on fitResult.be (fallback ROI exactly as Results), the request is rounded as uploadToBackend rounds; re-run (docs/findings/a03/voigt_saved_vs_refit.json: median 0.36 pp, max 0.69 pp, none > 1 pp). The control arm holds m at Math.round(caM); re-run (docs/findings/a03/local_server_gap.json; plan §6 table: local chi2r above the held-m server's +5.4 / +9.7 / +1.1 / +13.1 % on Scan_4/5/6/8). tests/js/lineshape_roundtrip.test.js now locks every shape parameter of every shape at each of its bounds (18 cases; the convolved shapes where their evaluators are exact: DS+G with m < 0.001, LA with m = 0), asserting the request value, the server's vary:false at that value, and drawn == fitted. Doing so found a FOURTH identity defect: lmfit clips a held value to its bounds, so a DS+G with m locked at 0 was fitted with m = 0.05 (the free-parameter floor) - fitting._make_peak_params._set now widens a limit to a held value (vary False, no expr), pinned in tests/test_voigt_contract.py. Numbers corrected throughout.

Verify each round-2 item is closed, then try to break: the _set change (any request where clipping a fixed value into bounds was RELIED on - a fixed amplitude below amplitude_min 0, a fixed centre outside the +/-2 eV window, DE's _finite_search_box with a fixed parameter outside its former bounds, the seed's effective-role hash, the scattered-starts clamp, _component_required's retained parameters created from result.params values/min/max; does widening a bound for a HELD parameter leak into any later refit that FREES it?); the 18 locked cases (do they exercise the LOCKED path on the server and the page's drawn curve? any bound omitted that a lock can reach?); voigt_saved_vs_refit.js (saved grid selection vs Results' exact rule at templates/index.html renderResults; the rounding; is the refit side's grid the one the page would hold after Run Fit?); the control arm; docs vs artifacts (every number in the plan §2b/§6/§7/§9, findings §7, CLAUDE.md, the two code comments and the JS test header must match docs/findings/a03/*.json and voigt_eta_summary.txt).

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check each round-2 fix, then trace held parameters through fitting and refitting and compare the reported numbers with the artifacts. I’ll keep this read-only and finish with a ranked review and verdict.

exec
/bin/zsh -lc "git status --short; git diff --stat main..HEAD; rg --files -g AGENTS.md -g '*a03*' -g '*voigt*' -g '*local_server_gap*' -g '*lineshape_roundtrip*' -g CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-l2s1ISJz' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-myLrdoDJ' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_r3_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_r3_verdict_runB.md
?? docs/autofit/codex/a03_voigt_eta_recheck2_prompt.txt
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-QEY0blvN' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PcMcwGak' (errno=Operation not permitted)
 CLAUDE.md                                          |   46 +-
 autofit/parity.py                                  |   23 +-
 autofit/reference.py                               |   54 +-
 .../autofit/codex/a03_voigt_eta_r2_verdict_runA.md | 8771 ++++++++++++++++++++
 .../autofit/codex/a03_voigt_eta_r2_verdict_runB.md | 8492 +++++++++++++++++++
 .../autofit/codex/a03_voigt_eta_recheck_prompt.txt |    9 +
 docs/autofit/codex/a03_voigt_eta_review_prompt.txt |   22 +
 docs/autofit/codex/a03_voigt_eta_verdict_runA.md   | 7974 ++++++++++++++++++
 docs/autofit/codex/a03_voigt_eta_verdict_runB.md   | 7777 +++++++++++++++++
 docs/findings/2026-09-fit-determinacy.md           |   75 +
 docs/findings/a03/local_server_gap.json            | 3375 ++++++++
 docs/findings/a03/local_server_gap.log             |   18 +
 docs/findings/a03/voigt_eta_summary.txt            |    7 +
 docs/findings/a03/voigt_saved_vs_refit.json        | 2450 ++++++
 docs/findings/a03/voigt_saved_vs_refit.log         |   56 +
 .../plans/2026-09-22-a03-voigt-eta-identity.md     |  248 +
 fitting.py                                         |   11 +
 scripts/bg_window_worked_example.py                |    2 +-
 scripts/endpoint_avg_sensitivity.py                |    2 +-
 scripts/gen_u4f_battery_fixture.py                 |    5 +-
 scripts/local_server_gap.js                        |  102 +
 scripts/voigt_eta_measure.py                       |  138 +
 scripts/voigt_saved_vs_refit.js                    |   68 +
 templates/index.html                               |   53 +-
 tests/autofit/battery_common.py                    |   25 +-
 tests/autofit/fixtures/u4f_battery_expected.json   | 1064 +--
 tests/autofit/test_u4f_parity_battery.py           |   13 +-
 tests/js/fit_acceptance.test.js                    |    2 +-
 tests/js/lineshape_parity.test.js                  |   94 +
 tests/js/lineshape_parity_backend.py               |   19 +-
 tests/js/lineshape_roundtrip.test.js               |  250 +
 tests/js/lineshape_roundtrip_backend.py            |   37 +
 tests/js/local_lm_server_parity_backend.py         |    3 +-
 tests/test_voigt_contract.py                       |   99 +
 34 files changed, 40806 insertions(+), 578 deletions(-)
CLAUDE.md
scripts/voigt_eta_measure.py
scripts/local_server_gap.js
scripts/voigt_saved_vs_refit.js
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md
docs/findings/a03/local_server_gap.log
docs/findings/a03/voigt_saved_vs_refit.json
docs/findings/a03/voigt_saved_vs_refit.log
docs/findings/a03/local_server_gap.json
docs/findings/a03/voigt_eta_summary.txt
tests/test_voigt_contract.py
tests/js/lineshape_roundtrip.test.js
tests/js/lineshape_roundtrip_backend.py
docs/autofit/codex/a03_voigt_eta_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r2_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_r3_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_r3_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_recheck_prompt.txt
docs/autofit/codex/a03_voigt_eta_recheck2_prompt.txt
docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_review_prompt.txt

exec
/bin/zsh -lc 'pwd; rg --files -g AGENTS.md /Users/skyefortier/xps-app /Users/skyefortier/.codex 2>/dev/null | head -40; git diff main..HEAD -- fitting.py templates/index.html autofit/parity.py autofit/reference.py tests/test_voigt_contract.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ooOZ2dvy' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5KJzLV2m' (errno=Operation not permitted)
diff --git a/autofit/parity.py b/autofit/parity.py
index fb09ddd..5187f85 100644
--- a/autofit/parity.py
+++ b/autofit/parity.py
@@ -36,7 +36,7 @@ from fitting import (
     tougaard_background,
     run_fit,
 )
-from .reference import ReferenceFit
+from .reference import ReferenceFit, apply_backend_params, peak_to_backend_spec
 
 
 def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
@@ -184,16 +184,30 @@ def eval_parity_relmax(rf: ReferenceFit) -> float:
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
@@ -209,6 +223,7 @@ def refit_record(rf: ReferenceFit) -> dict[str, Any]:
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
diff --git a/templates/index.html b/templates/index.html
index 8393b2c..68500f2 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -5962,7 +5962,7 @@ function renderPeakForm(p) {
       <select id="pk-shape-${p.id}" class="xps-tip-select" onchange="_switchPeakShape(${p.id}, this.value)">
         <option data-tip="Pure Gaussian. Dominated by instrument broadening. Rarely used alone — most XPS peaks need some Lorentzian character." ${p.shape==='Gaussian'?'selected':''}>Gaussian</option>
         <option data-tip="Pure Lorentzian. Dominated by core-hole lifetime. Rarely used alone — too sharp for most real XPS peaks." ${p.shape==='Lorentzian'?'selected':''}>Lorentzian</option>
-        <option data-tip="50/50 Gaussian-Lorentzian mix. Good default starting point for most insulating and polymeric samples." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
+        <option data-tip="Fixed 50/50 Gaussian-Lorentzian mix (η = 0.5, not fitted). A reasonable default for most insulating and polymeric samples; choose GL to fit the mix." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
         <option value="GL" data-tip="Adjustable Gaussian/Lorentzian ratio. Use when you need control over the peak shape — common for oxides, polymers, and organic materials." ${p.shape==='GL'?'selected':''}>GL pseudo-Voigt (&eta; mixing)</option>
         <option value="asym-GL" data-tip="GL with asymmetric broadening. Use for peaks with vibrational fine structure (e.g., C 1s in polymers) or when one side is broader than the other." ${p.shape==='asym-GL'?'selected':''}>Asymmetric GL</option>
         <option value="DS" data-tip="Asymmetric metallic lineshape with tail toward higher BE. Use for metals and conductive samples (e.g., Au, Cu, Fe metal). Not appropriate for insulators or oxides." ${p.shape==='DS'?'selected':''}>Doniach-&Scaron;unji&#263; (&alpha; + &gamma;)</option>
@@ -6223,15 +6223,28 @@ function peakToBackendSpec(p) {
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
@@ -6240,8 +6253,8 @@ function peakToBackendSpec(p) {
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
@@ -6282,7 +6295,10 @@ function _applyBackendParams(p, par) {
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
@@ -7780,9 +7796,15 @@ function _fitStatLabel(fr) {
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
@@ -7802,7 +7824,7 @@ function _governingProvenance() {
 function _localFitDetail(fr) {
   return _isUnweightedLocal(fr)
     ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
-    : 'It can differ from the server fit for Voigt or LA components, for very weak components (different parameter bounds), or where the model has several minima.';
+    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
 }
 // The designation follows the MODEL, not only a live fit result: parameters
 // imported from a .fit.json that was saved from a local fit are a starting
@@ -11248,7 +11270,7 @@ function _updateROIDisplay(roiRange) {
   el.textContent = `ROI: ${roiRange.min}\u2013${roiRange.max} eV`;
 }
 
-const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for Voigt or LA components or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
+const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
 const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the goodness of fit weighted by data uncertainty. Computed within the ROI range.\n\n\u2022 \u03c7\u00b2 \u2248 1.0 = ideal fit (residuals match expected noise)\n\u2022 \u03c7\u00b2 >> 1 = poor fit or underestimated uncertainties\n\u2022 \u03c7\u00b2 << 1 = possible overfitting or overestimated uncertainties\n\nNote: a low \u03c7\u00b2 does not guarantee a correct model \u2014 always check the R-factor and visually inspect residuals.";
 
 // Wire up custom tooltip for data-xps-tip elements (R-factor, chi-squared, etc.)
@@ -11323,6 +11345,11 @@ function _validateUncertainties() {
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
@@ -14283,7 +14310,7 @@ document.addEventListener('mousedown', function(e) {
 <div id="localfit-warn-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
   <div class="xps-modal" style="max-width:460px;border-color:var(--amber,#f59e0b)">
     <h3 style="color:var(--amber,#f59e0b)">&#9888; Local fit used (server unreachable) <button class="btn btn-sm" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">&#x2715;</button></h3>
-    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for Voigt or LA components or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
+    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
     <p style="font-size:11px;color:var(--text2);line-height:1.6;margin:0 0 12px"><strong style="color:var(--text)">Possible causes:</strong><br>
     &bull; The server may be offline or restarting<br>
     &bull; The fit request may have timed out<br>
diff --git a/tests/test_voigt_contract.py b/tests/test_voigt_contract.py
new file mode 100644
index 0000000..8fba515
--- /dev/null
+++ b/tests/test_voigt_contract.py
@@ -0,0 +1,99 @@
+"""A03 (2026-09-22): a "Voigt" component is the fixed 50/50 mix everywhere.
+
+The page draws, integrates, exports and fits locally with eta = 0.5
+(evalPeak; runFitLocal never frees glMix for a Voigt). Until A03 the
+request built by peakToBackendSpec — and its Python twin
+autofit.reference.peak_to_backend_spec — sent pseudo_voigt_gl with
+gl_ratio FREE from 0.3, so the server fitted a mix the page never showed.
+These tests pin the twin and what run_fit does with the request.
+"""
+import numpy as np
+import pytest
+
+import fitting
+from autofit.reference import peak_to_backend_spec
+
+
+def _peak(**over):
+    p = {"id": 1, "name": "sat", "shape": "Voigt", "center": 386.5, "amplitude": 3000.0, "fwhm": 1.4,
+         "glMix": 90, "fixGlMix": False}
+    p.update(over)
+    return p
+
+
+def test_twin_sends_voigt_as_fixed_half_mix():
+    spec = peak_to_backend_spec(_peak(), [_peak()])
+    assert spec["shape"] == "pseudo_voigt_gl"
+    assert spec["gl_ratio"] == 0.5
+    assert spec["fix_gl_ratio"] is True
+    # the page's glMix (kept for a later switch to GL) plays no part
+    assert peak_to_backend_spec(_peak(glMix=5), [_peak(glMix=5)])["gl_ratio"] == 0.5
+
+
+def test_twin_still_sends_gl_mix_free():
+    spec = peak_to_backend_spec(_peak(shape="GL", glMix=72), [_peak(shape="GL", glMix=72)])
+    assert spec["gl_ratio"] == pytest.approx(0.72)
+    assert spec["fix_gl_ratio"] is False
+
+
+def test_twin_sends_a_zero_as_a_zero():
+    """A 0 is a value, not an absent field (Codex round 1: `or 50` / `or 0.1`)."""
+    a = _peak(shape="asym-GL", glMix=0, asymmetry=0)
+    s = peak_to_backend_spec(a, [a])
+    assert s["gl_ratio"] == 0.0 and s["asymmetry"] == 0
+    d = _peak(shape="DS", dsAlpha=0, dsGamma=0)
+    s = peak_to_backend_spec(d, [d])
+    assert s["alpha"] == 0.0 and s["gamma_asym"] == 0.0
+    # a non-number still falls back to the default
+    d2 = _peak(shape="DS", dsAlpha=None)
+    assert peak_to_backend_spec(d2, [d2])["alpha"] == 0.1
+
+
+def test_a_locked_value_outside_the_optimiser_bounds_is_held_as_requested():
+    """lmfit clips a value to its bounds even when it does not vary: a DS+G
+    with m locked at 0 (the page's delta-kernel branch) was fitted with
+    m = 0.05, the free-parameter floor — a convolved curve the page never
+    drew (A03 Codex round 2). A held parameter is held at its value."""
+    x = np.arange(397.8, 385.8, -0.05)
+    y = fitting._SHAPE_FUNCS["ds_g"](x, amplitude=12000.0, center=391.8, alpha=0.0, beta=0.5, m_gauss=0.0) + 5.0
+    p = {"id": 1, "name": "d", "shape": "DSG_LA", "center": 391.8, "amplitude": 12000.0, "fwhm": 1.6,
+         "laAlpha": 0.0, "laBeta": 0.5, "laM": 0.0, "fixLaAlpha": True, "fixLaM": True}
+    res = fitting.run_fit(x, y, [peak_to_backend_spec(p, [p])], background_method="none", fit_kws={"method": "least_squares"})
+    par = res["individual_peaks"][0]["params"]
+    assert par["m_gauss"]["vary"] is False and par["m_gauss"]["value"] == 0.0
+    assert par["alpha"]["vary"] is False and par["alpha"]["value"] == 0.0
+    q = par
+    drawn = fitting._SHAPE_FUNCS["ds_g"](np.asarray(res["energy"]), amplitude=q["amplitude"]["value"], center=q["center"]["value"],
+                                         alpha=0.0, beta=q["beta"]["value"], m_gauss=0.0)
+    np.testing.assert_allclose(np.asarray(res["individual_peaks"][0]["y"]), drawn, rtol=0, atol=1e-9 * 12000.0)
+
+
+def test_run_fit_holds_eta_and_returns_the_half_mix_curve():
+    x = np.arange(392.0, 380.0, -0.05)
+    truth = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=3000.0, center=386.5, fwhm=1.4, gl_ratio=0.5)
+    rng = np.random.default_rng(3)
+    y = np.maximum(truth + rng.normal(0, 8, x.size), 0)   # no offset: the request carries no background
+    start = _peak(center=386.65, amplitude=2400.0, fwhm=1.7)
+    spec = peak_to_backend_spec(start, [start])
+    res = fitting.run_fit(x, y, [spec], background_method="none", fit_kws={"method": "least_squares"})
+    assert res["success"] is True
+    ip = res["individual_peaks"][0]
+    gl = ip["params"]["gl_ratio"]
+    assert gl["vary"] is False and gl["value"] == 0.5 and not gl["stderr"]   # lmfit reports 0.0 or None for a held parameter
+    q = ip["params"]
+    drawn = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](np.asarray(res["energy"]), amplitude=q["amplitude"]["value"],
+                                                    center=q["center"]["value"], fwhm=q["fwhm"]["value"], gl_ratio=0.5)
+    np.testing.assert_allclose(np.asarray(ip["y"]), drawn, rtol=0, atol=1e-9 * 3000.0)
+    assert abs(q["center"]["value"] - 386.5) < 0.02 and abs(q["fwhm"]["value"] - 1.4) < 0.03
+
+
+def test_seed_reflects_the_held_eta_not_the_old_free_start():
+    """The request seed hashes each parameter's EFFECTIVE role: a held eta of
+    0.5 and a free eta from 0.3 are different requests and draw differently."""
+    x = np.arange(392.0, 380.0, -0.05)
+    y = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=3000.0, center=386.5, fwhm=1.4, gl_ratio=0.5) + 20.0
+    spec = peak_to_backend_spec(_peak(), [_peak()])
+    old = dict(spec, gl_ratio=0.3, fix_gl_ratio=False)
+    s_new = fitting.run_fit(x, y, [spec], background_method="none", n_perturb=1)["random_seed"]
+    s_old = fitting.run_fit(x, y, [old], background_method="none", n_perturb=1)["random_seed"]
+    assert s_new != s_old

exec
/bin/zsh -lc "cat scripts/voigt_saved_vs_refit.js scripts/local_server_gap.js tests/js/lineshape_roundtrip.test.js tests/js/lineshape_roundtrip_backend.py; sed -n '800,1030p' fitting.py; rg -n '_finite_search_box|_component_required|scattered|effective.role|def .*seed|random_seed' fitting.py; rg -n 'function renderResults|fitResult.be|uploadToBackend|toFixed\\(4\\)|toFixed\\(2\\)' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
// (Codex round 2): the SAVED side integrates on the saved fit's own grid
// (fitResult.be — what Results shows for a loaded project; the ROI only
// when a save lacks it), the REFIT side on the grid the request carried,
// rounded exactly as uploadToBackend rounds (energies 4 dp, intensities
// 2 dp), which is the grid the page holds after Run Fit.
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
  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array', 'evalPeakArray', 'getPeak', '_applyBackendParams'];
const state = { peaks: [] };
const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams };')(state);
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
    const be = [], inten = [];
    t.rawBE.forEach((b, i) => { const c = b - (t.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(+c.toFixed(4)); inten.push(+t.rawIntensity[i].toFixed(2)); } });
    if (be.length < 10) continue;
    const savedGrid = (t.fitResult.be && t.fitResult.be.length) ? t.fitResult.be : be;
    const saved = JSON.parse(JSON.stringify(t.peaks));
    let srv;
    try {
      srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be, inten, peaks: saved, ui, n_perturb: 3 }), encoding: 'utf8', maxBuffer: 1 << 26 }));
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
out.summary = { n_tabs: out.targets.length, n_converged: ok.length, dFrac_pp: q(ok.map(r => r.max_dFrac_pp)), gt_1pp: ok.filter(r => r.max_dFrac_pp > 1).length, voigt_dArea_pct: q(ok.map(r => r.max_voigt_dArea_pct)) };
console.error(JSON.stringify(out.summary));
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/voigt_saved_vs_refit.json'), JSON.stringify(out, null, 1));
#!/usr/bin/env node
// Local engine vs server from the SAME scaled start on the committed
// UCl4-graphite project's Batch Fit targets (unit W1's methodology,
// 2026-09-18; re-run for A03, 2026-09-22 — the test of whether Batch Fit's
// "starting point" label can retire). Every C1s Scan_N and U4f Scan_N tab is
// a target; the source is the scan the student fitted ('C1s Scan' / 'U4f
// Scan'); the start is the source's model with amplitudes scaled to the
// target's maximum (what runPropagation does); both engines fit that start
// on the same background (the page's computeBackgroundCore; the server
// recomputes its own from the same settings). Differences are evaluated with
// the PAGE's semantics — the server's parameters written onto a copy of the
// start with _applyBackendParams, areas as _peakArea (evalPeakArray over the
// ROI grid × step) — so the comparison is about parameters, not about which
// side integrated. A third arm (Codex round 1: "movement in m alone does not
// establish that the residual is the local clamp") fits the server with every
// LA m HELD at the value the local engine effectively uses — its start
// ROUNDED to an integer, as laTrueCasaXPS_array rounds it (Codex round 2) —
// the one thing the local engine cannot move: if that arm agrees with the local engine where the
// free-m arm did not, the attribution is established by a controlled
// comparison, not inferred. Usage: node scripts/local_server_gap.js [out.json]
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
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_applyBackendParams'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
function makeEnv() {
  const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const f = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, _applyBackendParams };');
  return { ...f(document, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => new Array(be.length).fill(0)), state };
}
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const PROJECT = path.join(ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 1 << 26 }));
function target(env, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  return { be, inten, bg, bgSub: inten.map((v, i) => v - bg[i]), ui, start: cloned };
}
const area = (env, be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return env.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), regions: {} };
for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
  const names = tabs.filter(t => new RegExp('^' + sourceName.replace(' ', ' ') + '_\\d+$').test(t.name)).map(t => t.name);
  out.regions[region] = [];
  for (const name of names) {
    const env = makeEnv(); const T = target(env, sourceName, name);
    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
    const serverFit = startPeaks => {
      const r = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: startPeaks, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
      const peaks = JSON.parse(JSON.stringify(startPeaks));
      r.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(peaks[i], par); });
      return { r, peaks };
    };
    const { r: srv, peaks: serverPeaks } = serverFit(T.start);
    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, caM: Math.round(p.caM || 0), fixCaM: true } : p);
    const { r: srvHeld, peaks: serverHeldPeaks } = serverFit(heldStart);
    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p)), aH = serverHeldPeaks.map(p => area(env, T.be, p));
    const tL = aL.reduce((s, v) => s + v, 0), tS = aS.reduce((s, v) => s + v, 0), tH = aH.reduce((s, v) => s + v, 0);
    const comps = localPeaks.map((p, i) => ({ name: p.name, shape: p.shape, linked: !!p.linked,
      dCenter_meV: 1000 * (p.center - serverPeaks[i].center), dFwhm_pct: 100 * (p.fwhm / serverPeaks[i].fwhm - 1),
      dArea_pct: aS[i] ? 100 * (aL[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aL[i] / tL - aS[i] / tS),
      // the held-m arm: local vs server with every LA m held at its start
      held_dCenter_meV: 1000 * (p.center - serverHeldPeaks[i].center), held_dFwhm_pct: 100 * (p.fwhm / serverHeldPeaks[i].fwhm - 1),
      held_dArea_pct: aH[i] ? 100 * (aL[i] / aH[i] - 1) : null, held_dFrac_pp: 100 * (aL[i] / tL - aH[i] / tH),
      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM },
      server_held_m: { center: serverHeldPeaks[i].center, fwhm: serverHeldPeaks[i].fwhm, amplitude: serverHeldPeaks[i].amplitude, area: aH[i], caM: serverHeldPeaks[i].caM } }));
    const mx = f => Math.max(...comps.map(c => Math.abs(c[f]) || 0));
    out.regions[region].push({ target: name, local_success: loc.success, local_chi2r: env.state.fitResult && env.state.fitResult.chiReduced, server_success: srv.success, server_chi2r: srv.chi2r,
      server_held_m_success: srvHeld.success, server_held_m_chi2r: srvHeld.chi2r,
      max_dCenter_meV: mx('dCenter_meV'), max_dFwhm_pct: mx('dFwhm_pct'), max_dArea_pct: mx('dArea_pct'), max_dFrac_pp: mx('dFrac_pp'),
      held_max_dCenter_meV: mx('held_dCenter_meV'), held_max_dFwhm_pct: mx('held_dFwhm_pct'), held_max_dArea_pct: mx('held_dArea_pct'), held_max_dFrac_pp: mx('held_dFrac_pp'), comps });
    console.error(region, name, 'local', loc.success, (env.state.fitResult || {}).chiReduced && env.state.fitResult.chiReduced.toFixed(3), 'server', srv.success, srv.chi2r.toFixed(3), 'max Δcentre', mx('dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('dFwhm_pct').toFixed(2), '%, Δarea', mx('dArea_pct').toFixed(2), '%, Δfrac', mx('dFrac_pp').toFixed(2), 'pp',
      '| m held: server', srvHeld.chi2r.toFixed(3), 'Δcentre', mx('held_dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('held_dFwhm_pct').toFixed(2), '%, Δarea', mx('held_dArea_pct').toFixed(2), '%, Δfrac', mx('held_dFrac_pp').toFixed(2), 'pp');
  }
}
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/local_server_gap.json'), JSON.stringify(out, null, 1));
// Page → server → page identity (A03, 2026-09-22).
//
// The parity harness (lineshape_parity.test.js) proves the two EVALUATORS
// agree for the same parameters. It cannot see a request that asks the
// server to fit a parameter the page never draws: until A03 a "Voigt" was
// sent as pseudo_voigt_gl with gl_ratio FREE from 0.3 while evalPeak drew
// η = 0.5, so every chart component, area, percentage and export for a
// Voigt was the 0.5 curve under parameters fitted for another mix (on the
// 90 committed Voigt targets: displayed areas 12 % off the fitted curve at
// the median (13.9 %), 20 % at worst; 60 of 180 components had gone to pure
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
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
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
  });
});
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
        chain = [start]
        cur = parent[start]
        while cur is not None:
            chain.append(cur)
            if cur == start or cur in chain[:-1]:
                pretty = " → ".join(str(x) for x in chain)
                raise ValueError(f"Circular peak constraint detected: {pretty}")
            cur = parent.get(cur)


def _make_peak_params(
    model: Model,
    spec: dict[str, Any],
    prefix: str,
    all_specs: list[dict],
) -> Parameters:
    """
    Build lmfit Parameters for one peak from a spec dict.

    Spec keys
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
                 expr=f"{m_prefix}alpha" if fix else None,
                 min_=0.1, max_=5.0)
            _set("beta",  spec.get("beta",  1.0),
                 expr=f"{m_prefix}beta" if fix else None,
                 min_=0.1, max_=5.0)
            _set("m",     spec.get("m",    50.0),
                 expr=f"{m_prefix}m" if fix else None,
                 min_=0.0, max_=499.0)
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
    _set("fwhm", fwhm,
         min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0),
         vary=not spec.get("fix_fwhm", False))

    if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
        _set("gl_ratio", spec.get("gl_ratio", 0.3), min_=0.0, max_=1.0,
             vary=not spec.get("fix_gl_ratio", False))
    if shape == "asymmetric_gl":
        _set("asymmetry", asymmetry,
             min_=spec.get("asymmetry_min", 0.0),
             max_=spec.get("asymmetry_max", 1.0),
             vary=not spec.get("fix_asymmetry", False))
    if shape == "doniach_sunjic":
        _set("alpha", spec.get("alpha", 0.1), min_=0.0, max_=0.5,
             vary=not spec.get("fix_alpha", False))
        _set("gamma_asym", spec.get("gamma_asym", 0.0), min_=0.0, max_=5.0,
             vary=not spec.get("fix_gamma_asym", False))
    if shape == "ds_g":
        _set("alpha",   spec.get("alpha",   0.10), min_=0.0,  max_=0.49,
             vary=not spec.get("fix_alpha", False))
        _set("beta",    spec.get("beta",    0.3),  min_=0.05, max_=2.0,
             vary=not spec.get("fix_beta", False))
        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0,
             vary=not spec.get("fix_m_gauss", False))
    if shape == "la_casaxps":
        _set("alpha", spec.get("alpha", 1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_alpha", False))
        _set("beta",  spec.get("beta",  1.0), min_=0.1, max_=5.0,
             vary=not spec.get("fix_beta", False))
        _set("m",     spec.get("m",    50.0), min_=0.0, max_=499.0,
             vary=not spec.get("fix_m", True))

    return p


def _finite_search_box(params: Parameters, x: np.ndarray,
                       y_sub: np.ndarray) -> dict[str, dict[str, float]]:
    """Give every freely varying parameter a finite box, in place.

    lmfit's ``differential_evolution`` samples its population from the
    parameter bounds and refuses to run when any varying parameter has an
    open one. The page sends ``amplitude_min: 0`` and no ``amplitude_max``,
    and a free DS+G centre has no default window, so without this every
    ordinary request for that method failed (HTTP 422). Only open sides of
    freely varying parameters are closed; fixed and expression-constrained
    parameters, and bounds the request did set, are left alone.

    The box is a SEARCH limit, not a constraint the request made: an
    amplitude reaches max(10 x the largest |background-subtracted
    intensity|, 2 x |start|, 1) (both signs when the request leaves the
    floor open too; the page never does), a centre the fitted energy range.
    A component centred outside a narrowed ROI can need far more than the
    visible intensity, and a box can shape an answer that lies nowhere near
    its sides, so ``_search_then_refine`` refines every boxed search under
    the request's own bounds.

    Returns ``{name: {side: width}}`` for the sides it generated (``width``
    is the extent it gave that side).
    """
    xf = np.asarray(x, float)
    yf = np.asarray(y_sub, float)
    xf, yf = xf[np.isfinite(xf)], yf[np.isfinite(yf)]
    if xf.size == 0 or yf.size == 0:
        raise ValueError("differential_evolution needs finite energy and intensity values")
    x_lo, x_hi = float(xf.min()), float(xf.max())
    span = (x_hi - x_lo) or 1.0
    y_top = float(np.max(np.abs(yf)))
    generated: dict[str, dict[str, float]] = {}
    for name, par in params.items():
        if not par.vary or par.expr is not None:
            continue
        open_min, open_max = not np.isfinite(par.min), not np.isfinite(par.max)
        if not (open_min or open_max):
            continue
        if name.endswith("_amplitude"):
            width = max(10.0 * y_top, 2.0 * abs(par.value), 1.0)
            lo, hi = -width, width
        elif name.endswith("_center"):
            width = span
            lo, hi = min(x_lo, par.value), max(x_hi, par.value)
        else:
            raise ValueError(
                f"differential_evolution needs finite bounds for '{name}'")
        new_min = lo if open_min else par.min
        new_max = hi if open_max else par.max
        # A bound the request did set can sit at or beyond the generated
        # side (centre_min = 300 on a 280-290 eV ROI): keep a real interval.
        if open_max and new_max <= new_min:
            new_max = new_min + width
        if open_min and new_min >= new_max:
            new_min = new_max - width
        par.set(min=new_min, max=new_max)
        generated[name] = {side: width for side, is_open in (("min", open_min), ("max", open_max)) if is_open}
    return generated


def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
969:def _finite_search_box(params: Parameters, x: np.ndarray,
1051:    generated = _finite_search_box(boxed, x, y_sub)
1135:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1139:    in fitting order, each lmfit parameter's effective role, the method,
1193:# three more fits of the SAME method from scattered starts expose it (3.2 %),
1205:def _scattered_start(params: Parameters, rng) -> Parameters:
1206:    """One scattered start, anchored to the REQUEST's start (``params`` as
1280:def _scattered_starts(n_starts, fit_once, model, start_params, result, peak_specs, x, rng) -> dict[str, Any]:
1289:            trial = fit_once(_scattered_start(start_params, rng))
1291:            log.debug("scattered start raised", exc_info=True)
1376:def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
1625:        random_seed = int(caller_seed)
1627:        random_seed = _request_seed(
1632:    # scattered-starts stream leaves every existing draw (and its pins) alone.
1634:                                           for child in np.random.SeedSequence(random_seed).spawn(3))
1647:    def seeded(call_kws):
1659:    # scattered starts and the required-component refit go through it too.
1754:                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
1757:                log.exception("scattered starts failed")
1788:                    required = {"ran": True, **_component_required(
1917:        "random_seed": random_seed,
2498:    const shiftStr = (shift >= 0 ? '+' : '') + shift.toFixed(2);
2620:  return v.toFixed(2);
4542:// the frontend grid before uploadToBackend rounds BE to 4 decimals; the
5578:    notify('Peak placed at ' + beValue.toFixed(2) + ' eV', 'green');
5617:    notify('Multiplet pair placed at ' + beValue.toFixed(2) + ' eV (' + presetKey + ')', 'green');
5918:        <span class="peak-info">${unsupported ? dash : p.center.toFixed(2) + ' eV'}</span>
5925:        <span class="peak-summary-val">${unsupported ? dash : p.center.toFixed(2)}</span>
5926:        <span class="peak-summary-val">${unsupported ? dash : p.fwhm.toFixed(2)}</span>
6010:        <input type="number" value="${p.linkOffset.toFixed(2)}" step="0.05"
6069:        <input type="number" value="${p.dsGamma.toFixed(4)}" step="0.001" min="0"
6186:async function uploadToBackend(be, inten) {
6187:  const csv = be.map((e, i) => e.toFixed(4) + ',' + inten[i].toFixed(2)).join('\n');
6859:  const be = state.fitResult && state.fitResult.be;
7008:    if (info) info.textContent = un ? dash : p.center.toFixed(2) + ' eV';
7010:    if (vals[0]) vals[0].textContent = un ? dash : p.center.toFixed(2);
7011:    if (vals[1]) vals[1].textContent = un ? dash : p.fwhm.toFixed(2);
7116:    fq.textContent = 'χ²ᵣ = ' + chiReduced.toFixed(2);
7269:    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
7461:    const worst = (st.not_better_chi2r && st.not_better_chi2r.length) ? ` (χ²ᵣ ${st.not_better_chi2r.map(c => c.toFixed(2)).join(', ')})` : '';
7473:  return `this fit started from a solution chosen from the scattered starts (\u03c7\u00b2\u1d63 ${Number(c.fromChi).toFixed(2)} \u2192 ${Number(c.toChi).toFixed(2)}; largest move from the original start: ${c.shiftName} ${_startsEv(c.shiftEv)})`;
7482:function _startsEv(ev) { return (ev >= 0 ? '+' : '−') + Math.abs(ev).toFixed(2) + ' eV'; }
7499:    html += `<div style="color:var(--text3);margin-top:2px">This fit started from a solution you chose from the scattered starts (χ²ᵣ ${Number(c.fromChi).toFixed(2)} → ${Number(c.toChi).toFixed(2)}; largest move from your original start: ${_escHtml(c.shiftName)} ${_startsEv(c.shiftEv)}).</div>`;
7524:      <td style="padding:2px 4px">${label}</td><td style="text-align:right;padding:2px 4px;font-family:var(--mono)">${chi.toFixed(2)}</td>
7660:    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
7882:  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
8329:function renderResults() {
8388:  // Fit grid for area integration. Current-format fits carry fitResult.be; older
8392:  let be = state.fitResult.be;
8707://   A:  fitResult.be + fitResult.fittedY both present, lengths match
8710://   A2: fitResult.be + fitResult.bgIntensity present, no fittedY (local
9236:  const haveFit = !!(state.fitResult && Array.isArray(state.fitResult.be) &&
9237:                     state.fitResult.be.length > 0 &&
9239:                     state.fitResult.bgIntensity.length === state.fitResult.be.length);
9244:  const plotBE = haveFit ? state.fitResult.be : be;
10104:        be: _roundBE(t.fitResult.be),
10674:      be[i].toFixed(4), inten[i].toFixed(2), bgIntensity[i].toFixed(2),
10675:      bgSub[i].toFixed(2), modelFull[i].toFixed(2), resid[i].toFixed(2),
10676:      ...peakCols.map(col => col[i].toFixed(2))
11101:  const chiStr = state.fitResult.chiReduced.toFixed(4);
11118:      return [p.name, _UNSUPPORTED_LABEL, '', '', '', '', p.amplitude.toFixed(2), '', areas[i].toFixed(2),
11119:              p.shape, sc.gl, sc.alpha, '', '', rsfVals[i].toFixed(4), '', ''];
11122:      p.name, (_currentSupport(p) && _currentSupport(p).supported) ? 'supported' : '', p.center.toFixed(4), cse !== '' ? Number(cse).toFixed(5) : '',
11123:      p.fwhm.toFixed(4), fse !== '' ? Number(fse).toFixed(5) : '',
11124:      p.amplitude.toFixed(2), ase !== '' ? Number(ase).toFixed(3) : '',
11125:      areas[i].toFixed(2), p.shape, sc.gl, sc.alpha,
11127:      rsfVals[i].toFixed(4), normAreas[i].toFixed(4), atPcts[i].toFixed(2)
11213:  if (!fitResult || !fitResult.be) return null;
11214:  const be = fitResult.be;
12836:      ? 'KE ' + m.t.auger_ke_ev.toFixed(2) + ' → ' + m.be.toFixed(1) + ' eV'
12837:      : (m.t._legacy ? m.be.toFixed(1) + ' eV' : m.t.nominal_be_ev.toFixed(2) + ' eV');
12840:            ? 'Legacy Auger marker — KE ' + m.t.auger_ke_ev.toFixed(2) + ' eV (' +
13511:  if (lbl) lbl.innerHTML = '&plusmn; ' + ev.toFixed(2) + ' eV';
13560:    '<input type="range" id="ref-tol-range" min="0.25" max="5" step="0.25" value="' + tol.toFixed(2) + '" ' +
13562:    '<span class="ref-ident-tol" id="ref-tol-val">&plusmn; ' + tol.toFixed(2) + ' eV</span></div>';
13581:  html += '<div class="ref-context">Clicked: ' + ident.be.toFixed(2) + ' eV &middot; &plusmn;' +
13582:    ident.tol.toFixed(2) + ' eV &mdash; <button type="button" class="ref-note-more" onclick="_refClearIdentify()">clear</button></div>';
13606:      '<span class="ref-cand-ev">' + c.be.toFixed(2) + ' eV &middot; &Delta;' + c.dist.toFixed(2) + '</span></div>' +
13615:      (c.isAuger ? '<div class="ref-cand-line">KE ' + c.ke.toFixed(2) + ' eV &rarr; apparent BE on ' + srcLabel + '</div>' : '') +
13654:      be: [...(state.fitResult.be || [])],
14891:    const centers = unassignedPeaks.map(p => (+p.center).toFixed(2)).join(', ');
15513:    payload.session_id = await uploadToBackend(be, inten);
15664:        `<td style="${td}">${c.reduced_chi_sq != null ? (+c.reduced_chi_sq).toFixed(2) : '—'}</td>` +

exec
/bin/zsh -lc "sed -n '68,250p' tests/js/lineshape_roundtrip.test.js; sed -n '8380,8415p' templates/index.html; sed -n '7620,7770p' templates/index.html; cat tests/js/local_lm_server_parity_backend.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
  });
});
    ${_renderRFactorPanel(state.fitResult.rFactor)}
    <table class="results-table">
      <thead><tr>
        <th>Peak</th><th>Center (eV)</th><th>FWHM (eV)</th><th>Area</th><th>%</th>
      </tr></thead>
      <tbody>
  `;

  // Fit grid for area integration. Current-format fits carry fitResult.be; older
  // saves omit it, and without a guard _peakArea(p, be) throws on be.length —
  // leaving the panel stale and aborting the tab switch. Fall back to the live ROI
  // grid, exactly as renderPeakList already does for its area/percentage column.
  let be = state.fitResult.be;
  if ((!be || !be.length) && typeof getROIData === 'function' && state.rawBE.length) {
    be = getROIData().be;
  }
  if (!be) be = [];
  const areas = state.peaks.map(p => _peakArea(p, be));
  // percentages are over the components the fit DID determine
  const totalArea = areas.reduce((s, v, i) => s + (_isUnsupported(state.peaks[i]) ? 0 : v), 0);
  const unsupportedPeaks = state.peaks.filter(p => _isUnsupported(p));

  state.peaks.forEach((p, i) => {
    const pct = totalArea > 0 ? (areas[i] / totalArea * 100) : 0;
    const par = stderrMap[String(p.id)] || {};
    const centerSE = par.center ? par.center.stderr : null;
    const fwhmSE   = par.fwhm   ? par.fwhm.stderr   :
                     par.fwhm_l ? par.fwhm_l.stderr  : null;
    if (_isUnsupported(p)) {
      // the fit did not determine this component: no centre, width or sigma is reported
      html += `<tr class="unsupported-row" data-peak-id="${p.id}" style="color:var(--text3)">
      <td><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${p.color};margin-right:5px;opacity:.4"></span>${_escHtml(p.name)} ${_unsupportedBadge(p.id)}</td>
      <td style="font-family:var(--mono)">&mdash;</td>
      <td style="font-family:var(--mono)">&mdash;</td>
      <td>${areas[i].toFixed(0)}</td>
      <td>&mdash;</td>
    const bgType  = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
    // EVERY request input is read from the owner before the upload await:
    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
    // request could carry A's spectrum with B's averaging and anchors).
    // opts.startPeaks: the request starts from an adopted alternative; the live
    // model is still the student's until this fit succeeds (useAlternative).
    const startModel = opts.startPeaks || state.peaks;
    const peakSpecs = startModel.map(peakToBackendSpec);
    // scattered-starts check: decided HERE, with the other request inputs,
    // before the first await (a tab switch during the upload must not turn it off)
    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
    // the live model and its fit context as the student pressed the button: a
    // result must not be written over a model that was edited while it ran
    const ctxAtRequest = _startsLiveKey();
    const fitMethod = document.getElementById('fit-method').value;
    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    // Transport failures (server unreachable, timeout, non-JSON reply) are
    // the ONLY reason to fall back to the local optimiser. A server-side
    // validation error or a non-converged optimisation surfaces its message
    // and leaves the model untouched (unit A0: nothing is shown as a fit
    // result unless it converged; an HTTP 400 is not a reason to silently
    // switch engines).
    // Only a genuine transport failure (network rejection, abort, unparsable
    // 2xx body) is marked for fallback; server errors carry `serverError`.
    const _asTransport = (e) => {
      if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
      throw e;
    };
    let sessionId;
    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
    const fitReq = {
      session_id: sessionId,
      background: bgPayload,
      peaks: peakSpecs,
      fit_method: fitMethod,
      n_perturb: 3,
      n_starts: nStarts       // the server also skips it for the global methods
    };
    let resp, json;
    try {
      resp = await fetch('/api/fit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fitReq)
      });
    } catch (e) { _asTransport(e); }
    if (resp.ok === false) {
      // HTTP failure: read a message if the body is JSON, but a 502 HTML
      // page is still a SERVER failure, never a reason to switch engines.
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.serverError = true;
      throw err;
    }
    try { json = await resp.json(); } catch (e) { _asTransport(e); }
    if (json.error) {
      const err = new Error(json.error);
      err.serverError = true;
      throw err;
    }
    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
    // result that did not converge is a failed fit, not a result (audit A08:
    // until this unit success:false was applied and announced as complete).
    if (json.success !== true) {
      const err = new Error(json.message || 'the optimizer did not converge.');
      err.notConverged = true;
      throw err;
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
      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
      return;
    }
    if (e && e.transportFailure) {
      // Server unreachable: the local optimiser is the honest fallback, and
      // the overlay saying so opens only if it actually converged.
      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
      const local = runFitLocal(be, bgSubtracted, bgIntensity);
      if (local && local.success && !_snapshotSuppressed) {
        document.getElementById('localfit-warn-overlay').classList.add('open');
      }
"""Bridge for tests/js/local_lm_descent.test.js: run the SERVER fit (fitting.run_fit,
Poisson weights, Trust-Region) from the same scaled starting model the local
engine received, so the JS test can pin local-vs-server parity (unit W1).
stdin: {be, inten, peaks (frontend peak objects), ui}; argv[1]: repo root.
"""
import json
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import fitting  # noqa: E402
from autofit.reference import peak_to_backend_spec  # noqa: E402

d = json.load(sys.stdin)
x = np.asarray(d["be"], float)
y = np.asarray(d["inten"], float)
ui = d["ui"]
specs = [peak_to_backend_spec(p, d["peaks"]) for p in d["peaks"]]
lo, hi = sorted([float(ui["bgStart"]), float(ui["bgEnd"])])
idx = [i for i, b in enumerate(x) if lo <= b <= hi]
res = fitting.run_fit(x, y, specs, background_method=ui["bgType"], bg_start_idx=idx[0], bg_end_idx=idx[-1] + 1,
                      endpoint_avg=int(ui.get("endpointAvg") or 1), fit_kws={"method": "least_squares"},
                      n_perturb=int(d.get("n_perturb") or 0))   # the page sends 3; the W1 test sends none
print(json.dumps({"success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"],
                  "peaks": [{k: v["value"] for k, v in ip["params"].items()} for ip in res["individual_peaks"]]}))

exec
/bin/zsh -lc "cat docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md; cat docs/findings/a03/voigt_eta_summary.txt; sed -n '1130,1265p' fitting.py; sed -n '1376,1455p' fitting.py; git diff main..HEAD -- CLAUDE.md docs/findings/2026-09-fit-determinacy.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
`_applyBackendParams`). Grids as the page holds them (Codex round 2): the
saved side on the saved fit's own grid (`fitResult.be`, what Results shows
for a loaded project — 11 of the 55 tabs have a saved grid that differs
from the current ROI), the refit side on the request's grid, rounded as
`uploadToBackend` rounds (energies 4 dp, intensities 2 dp — the rounding
also determines the request seed).

| | median | p90 | max |
|---|---:|---:|---:|
| area fraction, per tab | 0.36 pp | 0.51 pp | 0.69 pp (0 of 55 > 1 pp) |
| a Voigt component's own area | 4.6 % | 7.6 % | 15.3 % |

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
  pins and the linked pair; on the branch 10 pass, 2 todo (below).
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
| Scan_5 | 2.393 | 2.174 | 2.182 | 4.7 meV / 4.3 % / 6.7 % / 0.35 pp | 6.3 meV / 3.5 % / 5.5 % / 0.25 pp | +9.7 % |
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
55 committed tabs (a Voigt's own area by 4.6 % at the median, 15 % at
most). Use GL to fit the mix. Also fixed: an asym-GL mix of exactly 0 or a
DS α of exactly 0 was sent to the server as 50 / 0.1, and a locked value
outside the optimiser's search limits (a DS+G m locked at 0) was moved onto
the limit before fitting; such requests now also draw a different
random seed, since the seed hashes the parameters as the fit receives them.

## 8. Verification

- `tests/test_voigt_contract.py` 6 passed; `lineshape_roundtrip.test.js`
  29 passed, 2 todo; full `pytest tests/` and the JS suite (371 tests, 364
  pass, 7 todo — `node --test tests/js/*.test.js`; the directory form does
  not run in this node): see §9.
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
targets 90, both fits converged 90
free eta of 180 Voigt components: 60 at 0 (pure Gaussian), 16 at 1 (pure Lorentzian), 24 within 0.4–0.6
per-Voigt-component DISPLAYED area vs the fitted curve (%): median 13.89, p90 19.18, max 20.11; > 10 % on 116 of 180; displayed high (eta < 0.5) 110, low 70
A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.48, max 1.55; > 1 pp on 35 targets
B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: median 0.34, p90 0.54, max 1.02; > 1 pp on 1 targets
C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 33 targets
chi2r fixed/free: median 1.09, p90 1.19, max 5.39; fixed lower on 10 targets (the free fit in a worse minimum)
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value) + 0.0
    return repr(value)


def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
    """The seed for every random draw of one fit: a pure function of the
    NUMBERS THE OPTIMISER IS HANDED — energies, counts and the computed
    background curve (little-endian float64), the lineshape of each component
    in fitting order, each lmfit parameter's effective role, the method,
    solver options and ``n_perturb``.

    A parameter's role is what it can do to the fit: a constrained one is its
    expression (its own start value and bounds are overridden), a fixed one
    is its value (its bounds cannot act), a free one is its value and bounds.
    Settings are hashed by their EFFECT, never as sent, so nothing the fit
    ignores can change the draws: a peak's name or colour, the
    ``fix_gl_ratio`` the page still sends for a Gaussian, stale shape
    parameters kept after a shape switch, the ``endpoint_avg`` a linear
    background does not use, anchor order, and the peaks' internal IDs —
    parameter names and constraint references are rewritten by component
    POSITION (``prefixes`` lists each component's lmfit prefix in fitting
    order), because the page never reuses an ID and the same model rebuilt
    after deleting a peak would otherwise fit differently. (Measured in review: each such
    no-op edit moved an area fraction by 15-45 percentage points while the
    request was hashed as sent.) It is a seed, not an identity: 32 bits
    collide, never use it as a cache key. Changing this derivation changes
    what saved projects regenerate: bump the version tag and say so.
    """
    kws = dict(fit_kws or {})
    solver = {k: v for k, v in dict(kws.pop("fit_kws", None) or {}).items() if k != "seed"}
    # longest prefix first so "p1_" cannot match inside "p11_"
    alias = sorted(((pre, f"c{k}_") for k, pre in enumerate(prefixes)), key=lambda a: -len(a[0]))

    def by_position(text):
        for pre, pos in alias:
            text = re.sub(r"(?<![A-Za-z0-9_])" + re.escape(pre), pos, text)
        return text

    roles = []
    for name, par in params.items():
        name = by_position(name)
        if par.expr is not None:
            roles.append([name, "expr", by_position(par.expr)])
        elif not par.vary:
            roles.append([name, "fixed", par.value])
        else:
            roles.append([name, "free", par.value, par.min, par.max])
    rest = _canonical({"shapes": list(shapes), "params": roles, "fit_kws": kws, "solver": solver,
                       "n_perturb": n_perturb})
    h = hashlib.sha256(b"xps-fit-seed-v1\0")
    for arr in (x, counts, background):
        a = np.ascontiguousarray(arr, dtype="<f8") + 0.0       # -0.0 -> 0.0 (the CSV path keeps "-0.00")
        h.update(str(a.size).encode() + b"\0" + a.tobytes())
    h.update(json.dumps(rest, sort_keys=True, separators=(",", ":"), allow_nan=True).encode())
    return int.from_bytes(h.digest()[:4], "little")            # 32 bits: what scipy's seed accepts


# ── Scattered starts: is the fit the only solution the data allow? ────────────
# Measured on the lab's 202 committed fit targets (docs/findings/
# 2026-09-fit-determinacy.md): the default method's result is more than 5 pp of
# area fraction from the best known solution on 7.8 % of not-yet-fitted starts;
# a second METHOD from the same start shares the minimum too often to help;
# three more fits of the SAME method from scattered starts expose it (3.2 %),
# at ~0.6 s. The fit the student asked for is never replaced (owner decision:
# the lowest chi-square can be a chemically absurd relocation of a component);
# solutions with a lower reduced chi-square are returned beside it, with how
# far each component moved from the student's start.
MAX_N_STARTS = 10
_STARTS_METHODS = ("leastsq", "least_squares", "nelder")     # the global methods already search
_SAME_FRACTION_PP = 1.0      # "same solution": every area fraction within 1 pp ...
_SAME_CENTRE_EV = 0.1        # ... and every centre within 0.1 eV (presentation grain, not science)
_LOWER_CHI_REL = 1e-3        # an alternative's reduced chi-square is lower by more than 0.1 %


def _scattered_start(params: Parameters, rng) -> Parameters:
    """One scattered start, anchored to the REQUEST's start (``params`` as
    built from the request, never a fitted solution, which jitters): free
    amplitudes x/÷ 3 (sign kept), free widths x/÷ 1.5, free centres ± 0.5 eV —
    each clamped into the request's bounds, a thousandth of the interval off
    a finite wall (lmfit's bound transform has zero gradient ON a wall) —
    and every other freely varying parameter with finite bounds redrawn
    inside the middle 90 % of its range. Fixed and constrained parameters,
    and the integer CasaXPS ``m``, are left alone."""
    out = params.copy()
    for name, par in out.items():
        if not par.vary or par.expr is not None:
            continue
        lo, hi = par.min, par.max
        both = np.isfinite(lo) and np.isfinite(hi)
        edge = 1e-3 * (hi - lo) if both else 0.0

        def clamp(v):
            if np.isfinite(lo):
                v = max(v, lo + edge)
            if np.isfinite(hi):
                v = min(v, hi - edge)
            return v

        if name.endswith("_amplitude"):
            sign = -1.0 if par.value < 0 else 1.0
            value = clamp(sign * max(abs(par.value), 1.0) * float(np.exp(rng.uniform(-np.log(3), np.log(3)))))
        elif name.endswith("_fwhm"):
            value = clamp(par.value * float(np.exp(rng.uniform(-np.log(1.5), np.log(1.5)))))
        elif name.endswith("_center"):
            value = clamp(par.value + float(rng.uniform(-0.5, 0.5)))
        elif name.endswith("_m"):
            continue
        elif both:
            value = float(rng.uniform(lo + 0.05 * (hi - lo), hi - 0.05 * (hi - lo)))
        else:
            continue
        par.set(value=float(value))
    return out


def _solution_components(model, result, peak_specs, x) -> list[dict[str, Any]]:
    """Per component, in the request's order: area, area %, and every fitted
    parameter value (what the page needs to show and to apply a solution)."""
    comps = []
    for spec in peak_specs:
        prefix = f"p{spec['id']}_"
        comp = next(c for c in model.components if c.prefix == prefix)
        area = float(abs(trapezoid(comp.eval(result.params, x=x), x)))
        values = {n[len(prefix):]: float(par.value) for n, par in result.params.items() if n.startswith(prefix)}
        comps.append({"id": spec["id"], "area": area, "params": values})
    total = sum(c["area"] for c in comps)
    for c, spec in zip(comps, peak_specs):
        c["area_percent"] = 100.0 * c["area"] / total if total > 0 else 0.0
        c["center_shift_from_start"] = c["params"]["center"] - float(spec["center"])
    return comps


def _same_solution(a, b) -> bool:
    """Same decomposition: every area fraction within 1 pp and every centre
    within 0.1 eV, COMPONENT BY COMPONENT (by the request's ids). No
def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
    """``fit_reduced(params)`` is the run's own fitter for the reduced model
    (the same candidate machinery and seeding the fit used, so differential
    evolution's box/refinement and the request seed apply to the refit too).
    ``removed_prefixes`` is the removed component AND everything linked to it,
    transitively. The reduced start is built in dependency order: plain
    parameters first, expressions after, so a child ordered before its parent
    in the request still resolves."""
    kept = [(name, par) for name, par in params_full.items() if not any(name.startswith(r) for r in removed_prefixes)]
    # ALL retained parameters exist before any expression is assigned, so a
    # chain of links in any request order resolves (lmfit evaluates an
    # expression when it is set).
    start = Parameters()
    for name, par in kept:
        start.add(name, value=par.value, min=par.min, max=par.max, vary=par.vary)
    for name, par in kept:
        if par.expr:
            start[name].set(expr=par.expr)
    refit = fit_reduced(start)
    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
    delta = chi2_without - chi2_with
    p = max(1, int(n_free_comp))
    dof = max(1, len(y_sub) - int(n_free_total))
    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
    # change relative to the data's power, and then an "exactness" cutoff on
    # the reduced fit, each masked a resolved anchor at high dynamic range —
    # the same lesson as the DE unit). Known limit, accepted: on NOISE-FREE
    # data whose full fit is numerically exact (chi2_with ~ 1e-28) F is not
    # meaningful and a truly redundant component (two identical half-amplitude
    # components) reports "required"; real data never fit to machine precision.
    if not np.isfinite(chi2_without):
        f, required = None, True                     # the rest could not even be fitted without it
    elif delta <= 0:
        f, required = 0.0, False
    elif chi2_with == 0:
        f, required = None, True
    else:
        f = (delta / p) / (chi2_with / dof)
        required = f >= SUPPORT_MIN_F
    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
            "refit_converged": bool(refit.success)}


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
    n_starts: int = 0,
    require_component=None,
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
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-AGqXnNJB' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yd9SxnTB' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index c1eeada..158bd9b 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -110,13 +110,30 @@ tab reordering exists.
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
+at 0.5. Tracked gaps, `todo` in both files: LACX with m > 0 (the page draws
+a rounded integer kernel; the server fits m continuously — the `caM` clamp
+unit) and DS+G with m ≥ 0.05 (the page's quadrature `laCasaXPS` sizes its
+step to the Lorentzian core, not the Gaussian kernel, and is wrong by up to
+80 % of amplitude across the fitted β/m range — 1e52 × at β = 2, m = 0.05;
+0 of 865 committed components use DS+G; its own unit). Details in
+`docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+
 ---
 
 ## Design Rules
@@ -459,16 +476,29 @@ the integer-clamped `caM` is not optimised (carried at its start value).
 
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
diff --git a/docs/findings/2026-09-fit-determinacy.md b/docs/findings/2026-09-fit-determinacy.md
index 8ad6c2f..0f7f250 100644
--- a/docs/findings/2026-09-fit-determinacy.md
+++ b/docs/findings/2026-09-fit-determinacy.md
@@ -255,3 +255,78 @@ whether the result names the slot by its ROLE (so a migrated slot is still
 called C–O). Narrower per-role centre windows are the structural remedy; the
 manual path has only the ± 2 eV default.
 
+
+## 7. A03 (2026-09-22) — a "Voigt" was fitted with a mix the page never drew; the sweep found DS+G's preview wrong across its fitted range
+
+Generators: `scripts/voigt_eta_measure.py` (the 90 committed Voigt targets,
+both requests), `scripts/local_server_gap.js` (the 18 W1 targets),
+section (D) of `tests/js/lineshape_parity.test.js` (the sweep). Plan and
+tables: `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+
+**The Voigt identity.** `peakToBackendSpec` sent a Voigt as
+`pseudo_voigt_gl` with `gl_ratio: 0.3` FREE; `evalPeak` drew η = 0.5;
+`runFitLocal` held 0.5; the dropdown said "50/50"; CLAUDE.md said fixed 0.5.
+On the 90 committed targets with a Voigt component (89 U 4f tabs across five
+projects, one Cl 2p; 180 Voigt components): the server's free η ended at
+pure Gaussian (< 0.01) on 60 of the 180 and pure Lorentzian (> 0.99) on
+16, within 0.4–0.6 on 24. Every area, percentage, chart
+component and export the page produced for those components was the 0.5
+curve under parameters fitted for another mix: that curve vs the fitted one
+median 13.9 %, p90 19.2 %, max 20.1 % (116 of 180 components > 10 %); as
+area fractions median 0.96 pp, max 1.55 pp (35 of 90 targets > 1 pp; server
+curves, trapezoid). Fixed on both sides (η = 0.5 held in the request). What
+a student SEES change on re-fitting a saved project, measured with the
+PAGE's own integration of the saved peaks against the page's integration of
+the refit (`scripts/voigt_saved_vs_refit.js`, 55 committed tabs with a
+saved fit and a Voigt, six projects; the saved side on the saved fit's own
+grid, the refit on the upload-rounded request): an area fraction moves by
+median 0.36 pp, p90 0.51 pp, max 0.69 pp (none > 1 pp); a Voigt's own area
+by median 4.6 %, max 15.3 %. The refit vs the server's own free-η fit is
+median 0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9 % (the mix is one
+parameter fewer). The alternative — honour the fitted η on the page — would
+have made "Voigt" a GL with a hidden slider and silently kept a shape the
+student had not chosen; 76 of 180 fitted values sitting on a bound says the
+parameter was not determined by the data in those fits anyway. The same
+review found the builder sending an asym-GL mix of exactly 0 as 50 and a
+DS α of exactly 0 as 0.1 (`||` defaults); locked, the drawn curve differed
+from the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders.
+Locking every shape parameter at each of its bounds then found a fourth:
+lmfit clips a held value to its bounds, so a DS+G with m locked at 0 (the
+page's delta-kernel branch) was fitted with m = 0.05, the free-parameter
+floor; `_set` now widens the limit to a held value.
+
+**The re-measurement (W1 methodology, 18 targets).** C 1s unchanged (8 of 9
+within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is the §2 finding). U 4f,
+W1 → A03: max Δcentre 39.7 → 28.8 meV, ΔFWHM 17.2 → 15.8 %, Δarea 20.8 →
+8.9 %, Δfraction 1.4 → 0.77 pp. On the 5 of 9 targets where both engines
+reach the same minimum (χ²ᵣ equal to 2–3 digits) every component is within
+4.3 meV, 2.6 %, 2.0 %, 0.12 pp — the Voigt gap is gone. On the other 4 the
+server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
+7.9 while the local engine holds it; χ²ᵣ (local/server − 1) is +9.6, +10.1,
+−5.0 and +12.7 %, and the satellites, which share the region, differ by up
+to 8.9 % in area. A control arm (the server with every LA m HELD at its
+start, rounded as the local engine rounds it) attributes it: on Scan_6
+holding m closes the gap to 3.6 meV / 1.1 % / 1.6 % / 0.07 pp — that one IS
+the `caM` clamp; on Scan_5 and Scan_8 holding m changes nothing and the
+local engine's χ²ᵣ stays 9.7 % and 13.1 % above the server's from the same
+start with the same free parameters — a WORSE MINIMUM (the mirror image of
+§2, where the local engine found the better one on C 1s Scan_4); Scan_4 is
+in between (+5.4 %). The "starting point" label stays
+on both grounds; the `caM` clamp is the next unit, and the local engine's
+worse-minimum outcome on 3 of 9 U 4f targets is a finding for the
+local-engine work after it.
+
+**The sweep.** Gaussian, Lorentzian, Voigt, GL, asym-GL and DS agree with
+the server to 1e-15 across every bound. LACX with m > 0: up to 0.89 % of
+amplitude when the kernel is wide against the peak (the tracked
+discretisation gap). DS+G with m ≥ 0.05: the page's `laCasaXPS` quadrature
+uses a step of 2·(6σ + 50β)/max(300, ⌈2·(6σ + 50β)/(β/3)⌉) — sized to the
+Lorentzian core, blind to the Gaussian kernel — so at β = 2, m = 0.05 the
+step is 0.67 eV against σ = 0.021 eV, the kernel weights sample nothing,
+and the page's curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's
+area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
+865 committed components use DS+G, so no saved figure is affected; it is the
+fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
+recorded as its own unit. The general lesson repeats §6's: a harness that
+evaluates one representative point per shape proves nothing about the range
+the optimiser can reach.

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/lineshape_roundtrip.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc 'cat docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
`_applyBackendParams`). Grids as the page holds them (Codex round 2): the
saved side on the saved fit's own grid (`fitResult.be`, what Results shows
for a loaded project — 11 of the 55 tabs have a saved grid that differs
from the current ROI), the refit side on the request's grid, rounded as
`uploadToBackend` rounds (energies 4 dp, intensities 2 dp — the rounding
also determines the request seed).

| | median | p90 | max |
|---|---:|---:|---:|
| area fraction, per tab | 0.36 pp | 0.51 pp | 0.69 pp (0 of 55 > 1 pp) |
| a Voigt component's own area | 4.6 % | 7.6 % | 15.3 % |

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
  pins and the linked pair; on the branch 10 pass, 2 todo (below).
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
| Scan_5 | 2.393 | 2.174 | 2.182 | 4.7 meV / 4.3 % / 6.7 % / 0.35 pp | 6.3 meV / 3.5 % / 5.5 % / 0.25 pp | +9.7 % |
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
55 committed tabs (a Voigt's own area by 4.6 % at the median, 15 % at
most). Use GL to fit the mix. Also fixed: an asym-GL mix of exactly 0 or a
DS α of exactly 0 was sent to the server as 50 / 0.1, and a locked value
outside the optimiser's search limits (a DS+G m locked at 0) was moved onto
the limit before fitting; such requests now also draw a different
random seed, since the seed hashes the parameters as the fit receives them.

## 8. Verification

- `tests/test_voigt_contract.py` 6 passed; `lineshape_roundtrip.test.js`
  29 passed, 2 todo; full `pytest tests/` and the JS suite (371 tests, 364
  pass, 7 todo — `node --test tests/js/*.test.js`; the directory form does
  not run in this node): see §9.
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

codex
The round-2 changes are present, including the rounded control arm and real server fits in all 18 locked cases. The JS test header still says both “12 %” and “13.9 %” for the median. I’m checking the remaining grid details and whether widened held bounds survive safely through refits.

exec
/bin/zsh -lc "sed -n '7700,7765p' templates/index.html; cat tests/js/local_lm_server_parity_backend.py; sed -n '1135,1186p' fitting.py; sed -n '1030,1135p' fitting.py; sed -n '1590,1685p' fitting.py; rg -n 'def .*gauss|_SHAPE_FUNCS|Model\\(|\\.vary\\s*=|vary=True|set\\(.*vary' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
      return;
    }
    if (e && e.transportFailure) {
      // Server unreachable: the local optimiser is the honest fallback, and
      // the overlay saying so opens only if it actually converged.
"""Bridge for tests/js/local_lm_descent.test.js: run the SERVER fit (fitting.run_fit,
Poisson weights, Trust-Region) from the same scaled starting model the local
engine received, so the JS test can pin local-vs-server parity (unit W1).
stdin: {be, inten, peaks (frontend peak objects), ui}; argv[1]: repo root.
"""
import json
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import fitting  # noqa: E402
from autofit.reference import peak_to_backend_spec  # noqa: E402

d = json.load(sys.stdin)
x = np.asarray(d["be"], float)
y = np.asarray(d["inten"], float)
ui = d["ui"]
specs = [peak_to_backend_spec(p, d["peaks"]) for p in d["peaks"]]
lo, hi = sorted([float(ui["bgStart"]), float(ui["bgEnd"])])
idx = [i for i, b in enumerate(x) if lo <= b <= hi]
res = fitting.run_fit(x, y, specs, background_method=ui["bgType"], bg_start_idx=idx[0], bg_end_idx=idx[-1] + 1,
                      endpoint_avg=int(ui.get("endpointAvg") or 1), fit_kws={"method": "least_squares"},
                      n_perturb=int(d.get("n_perturb") or 0))   # the page sends 3; the W1 test sends none
print(json.dumps({"success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"],
                  "peaks": [{k: v["value"] for k, v in ip["params"].items()} for ip in res["individual_peaks"]]}))
def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
    """The seed for every random draw of one fit: a pure function of the
    NUMBERS THE OPTIMISER IS HANDED — energies, counts and the computed
    background curve (little-endian float64), the lineshape of each component
    in fitting order, each lmfit parameter's effective role, the method,
    solver options and ``n_perturb``.

    A parameter's role is what it can do to the fit: a constrained one is its
    expression (its own start value and bounds are overridden), a fixed one
    is its value (its bounds cannot act), a free one is its value and bounds.
    Settings are hashed by their EFFECT, never as sent, so nothing the fit
    ignores can change the draws: a peak's name or colour, the
    ``fix_gl_ratio`` the page still sends for a Gaussian, stale shape
    parameters kept after a shape switch, the ``endpoint_avg`` a linear
    background does not use, anchor order, and the peaks' internal IDs —
    parameter names and constraint references are rewritten by component
    POSITION (``prefixes`` lists each component's lmfit prefix in fitting
    order), because the page never reuses an ID and the same model rebuilt
    after deleting a peak would otherwise fit differently. (Measured in review: each such
    no-op edit moved an area fraction by 15-45 percentage points while the
    request was hashed as sent.) It is a seed, not an identity: 32 bits
    collide, never use it as a cache key. Changing this derivation changes
    what saved projects regenerate: bump the version tag and say so.
    """
    kws = dict(fit_kws or {})
    solver = {k: v for k, v in dict(kws.pop("fit_kws", None) or {}).items() if k != "seed"}
    # longest prefix first so "p1_" cannot match inside "p11_"
    alias = sorted(((pre, f"c{k}_") for k, pre in enumerate(prefixes)), key=lambda a: -len(a[0]))

    def by_position(text):
        for pre, pos in alias:
            text = re.sub(r"(?<![A-Za-z0-9_])" + re.escape(pre), pos, text)
        return text

    roles = []
    for name, par in params.items():
        name = by_position(name)
        if par.expr is not None:
            roles.append([name, "expr", by_position(par.expr)])
        elif not par.vary:
            roles.append([name, "fixed", par.value])
        else:
            roles.append([name, "free", par.value, par.min, par.max])
    rest = _canonical({"shapes": list(shapes), "params": roles, "fit_kws": kws, "solver": solver,
                       "n_perturb": n_perturb})
    h = hashlib.sha256(b"xps-fit-seed-v1\0")
    for arr in (x, counts, background):
        a = np.ascontiguousarray(arr, dtype="<f8") + 0.0       # -0.0 -> 0.0 (the CSV path keeps "-0.00")
        h.update(str(a.size).encode() + b"\0" + a.tobytes())
    h.update(json.dumps(rest, sort_keys=True, separators=(",", ":"), allow_nan=True).encode())
    return int.from_bytes(h.digest()[:4], "little")            # 32 bits: what scipy's seed accepts

def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
    """One differential-evolution candidate: search inside a generated box,
    then refine FROM that solution with ``least_squares`` under the request's
    own (open) bounds.

    Whenever a side was generated the refinement is unconditional (a request
    that bounds everything itself is returned as found). A box can shape the answer without the
    solution lying anywhere near a side (centre and width compensate for a
    capped amplitude), and an unrefined boundary candidate can lose the
    perturb loop's comparison to a worse interior one, so every candidate is
    freed from the box before it is compared or returned. The refined fit
    replaces the search result whenever it converged; if it did not (or
    raised) the search result is returned marked
    ``box_unverified`` (with the sides we generated, so they are not
    reported as bounds) and ``run_fit`` does not call it a success.
    """
    # ``params`` may come from an earlier candidate and still carry that
    # candidate's generated sides: always start from the request's bounds.
    boxed = params.copy()
    for name, (lo, hi) in requested.items():
        boxed[name].set(min=lo, max=hi)
    generated = _finite_search_box(boxed, x, y_sub)
    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
    found.box_unverified, found.search_box = bool(generated), generated
    if not generated:
        return found
    free = found.params.copy()
    for name in generated:
        free[name].set(min=requested[name][0], max=requested[name][1])
    # Only what a local solver understands: DE options (seed, popsize, ...)
    # passed through fit_kws would make least_squares raise.
    refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
    try:
        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
    except Exception:
        log.debug("refinement outside the search box raised", exc_info=True)
        return found
    # A converged refinement IS the result: it is a least_squares fit of the
    # requested model under the requested bounds, which is what the default
    # method returns and the acceptance rule accepts. It is deliberately NOT
    # compared with the boxed search's chi-square. least_squares descends
    # from its start, so it cannot end materially above it (four review
    # rounds found no reachable case), but it does end a hair above an EXACT
    # start that sits on a requested bound (the bound transform is degenerate
    # there; the centre moves ~1e-7 eV), by an amount that depends on peak
    # width, position and counts. Every tolerance tried for that comparison
    # produced reachable false failures and no reachable protection.
    if refined.success:
        refined.box_unverified, refined.search_box = False, {}
        return refined
    return found


def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws):
    """A differential-evolution candidate that is never worse than the
    default method from the same start.

    Differential evolution ignores the starting values. On a needle-narrow
    peak in a wide box it can converge, "successfully", with the component
    outside the fitted range (chi-square 1e7 where ``least_squares`` from the
    request's start reaches 1e-4), and the refinement has nothing to descend
    to from there. So a ``least_squares`` fit from the candidate's own start,
    under the request's bounds, competes with the search: a verified result
    beats an unverified one, then the lower chi-square wins.
    """
    searched = _search_then_refine(model, params, requested, y_sub, x, weights, kws)
    start = params.copy()
    for name, (lo, hi) in requested.items():
        start[name].set(min=lo, max=hi)
    try:
        local = model.fit(y_sub, start, x=x, weights=weights,
                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"))
    except Exception:
        log.debug("local candidate from the start raised", exc_info=True)
        return searched
    if not local.success:
        return searched
    local.box_unverified, local.search_box = False, {}
    if searched.box_unverified or not searched.success or local.chisqr < searched.chisqr:
        return local
    return searched


# The methods run_fit accepts, and the two of them that draw random numbers.
# Validated HERE, not only in the /api/fit route: /api/analyze forwards
# options.fit_method straight to run_fit, and lmfit also understands e.g.
# "ampgo", "dual_annealing" and "BasinHopping", which would run with
# numpy's global generator, unseeded.
_FIT_METHODS = ("leastsq", "least_squares", "nelder", "differential_evolution", "basinhopping")
_STOCHASTIC_METHODS = ("differential_evolution", "basinhopping")

def _canonical(value):
    """Spelling-independent form: keys sorted, every number a float (a browser
    writes 1.0 as ``1``; -0.0 folds to 0.0), arrays as lists."""
    if isinstance(value, dict):
        return {str(k): _canonical(value[k]) for k in sorted(value, key=str)}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_canonical(v) for v in value]
    if isinstance(value, (bool, np.bool_)) or value is None or isinstance(value, str):
        return bool(value) if isinstance(value, np.bool_) else value
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value) + 0.0
    return repr(value)


def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
    # Sort so unconstrained (master) peaks come before constrained ones
    ordered = sorted(
        peak_specs,
        key=lambda s: 0 if s.get("constrain_to") is None else 1,
    )

    composite_model: Model | None = None
    all_params = Parameters()

    for spec in ordered:
        shape = spec.get("shape", "pseudo_voigt_gl")
        if shape not in _SHAPE_FUNCS:
            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
        func = _SHAPE_FUNCS[shape]
        prefix = f"p{spec['id']}_"
        m = Model(func, prefix=prefix)
        p = _make_peak_params(m, spec, prefix, ordered)
        all_params.update(p)
        composite_model = m if composite_model is None else composite_model + m

    if composite_model is None:
        raise RuntimeError("No peaks were built")
    if require_component is not None:
        ids = [str(spec["id"]) for spec in peak_specs]
        if str(require_component) not in ids:
            raise ValueError(f"require_component '{require_component}' is not one of the peaks")
        if len(ids) < 2:
            raise ValueError("require_component needs at least two components")

    # Every random draw below (the perturbed restarts; the populations of the
    # two stochastic methods, which lmfit otherwise takes from numpy's GLOBAL
    # generator) comes from this one seed, so an identical request gives
    # identical DRAWS. (Not an identical Trust-Region result: see CLAUDE.md,
    # "Reproducibility".)
    if caller_seed is not None:
        random_seed = int(caller_seed)
    else:
        random_seed = _request_seed(
            x, y, bg, [spec.get("shape", "pseudo_voigt_gl") for spec in ordered],
            [f"p{spec['id']}_" for spec in ordered], all_params,
            fit_kws=fit_kws, n_perturb=n_perturb)
    # spawn(3) yields the same first two children as spawn(2): adding the
    # scattered-starts stream leaves every existing draw (and its pins) alone.
    perturb_rng, solver_rng, starts_rng = (np.random.default_rng(child)
                                           for child in np.random.SeedSequence(random_seed).spawn(3))
    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")

    # ── Fit ───────────────────────────────────────────────────────────────────
    kws = {"method": "leastsq", "nan_policy": "omit"}
    if fit_kws:
        kws.update(fit_kws)

    # Differential evolution needs a finite box and the page leaves amplitudes
    # open above: each candidate is searched in a generated box and then
    # refined under the request's own bounds (_search_then_refine). Every
    # other method fits the request's parameters exactly as before.
    def seeded(call_kws):
        """``call_kws`` with a fresh solver seed for the stochastic methods
        (one per minimisation, else every perturbed restart of differential
        evolution would replay the same population); unchanged otherwise."""
        if call_kws.get("method") not in _STOCHASTIC_METHODS:
            return call_kws
        solver_kws = dict(call_kws.get("fit_kws") or {})
        solver_kws["seed"] = int(solver_rng.integers(0, 2 ** 32 - 1))
        return {**call_kws, "fit_kws": solver_kws}

    # One fitter for any (sub)model of this request: the DE candidate machinery
    # when the method is differential evolution, else a plain seeded fit. The
    # scattered starts and the required-component refit go through it too.
    requested_bounds = {name: (par.min, par.max) for name, par in all_params.items()}

    def fit_model(model, params):
        if kws.get("method") == "differential_evolution":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))

    def fit_once(params):
        return fit_model(composite_model, params)

    # ── Diagnostic logging: BEFORE optimisation ──────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT START ═══  method=%s  n_data=%d", kws.get('method'), len(y_sub))
        for pname, par in sorted(all_params.items()):
            log.debug("  BEFORE  %-30s value=%12.6f  vary=%-5s  expr=%s  min=%s  max=%s",
                      pname, par.value, str(par.vary), par.expr,
                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')

    try:
        result = fit_once(all_params)
    except Exception as exc:
        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc

    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
46:def _gaussian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
152:def _ds_g_dscore_gauss(
766:_SHAPE_FUNCS = {
776:AVAILABLE_SHAPES = list(_SHAPE_FUNCS.keys())
846:    def _set(name, value, min_=None, max_=None, expr=None, vary=True):
864:            p[full].vary = False
870:            p[full].vary = vary
930:    _set("center", center, min_=c_min, max_=c_max, vary=not spec.get("fix_center", False))
1601:        if shape not in _SHAPE_FUNCS:
1603:        func = _SHAPE_FUNCS[shape]
1605:        m = Model(func, prefix=prefix)

exec
/bin/zsh -lc "cat docs/findings/a03/voigt_eta_summary.txt; sed -n '6030,6130p' templates/index.html; rg -n 'def .*fit|amplitude_min|fix_amplitude|center_min' app.py | head -70; ls /Users/skyefortier/xps-app/venv/bin/python*; rg --files tests | rg 'seed|starts|differential|support|component|bound|determin|search' " in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
targets 90, both fits converged 90
free eta of 180 Voigt components: 60 at 0 (pure Gaussian), 16 at 1 (pure Lorentzian), 24 within 0.4–0.6
per-Voigt-component DISPLAYED area vs the fitted curve (%): median 13.89, p90 19.18, max 20.11; > 10 % on 116 of 180; displayed high (eta < 0.5) 110, low 70
A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.48, max 1.55; > 1 pp on 35 targets
B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: median 0.34, p90 0.54, max 1.02; > 1 pp on 1 targets
C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 33 targets
chi2r fixed/free: median 1.09, p90 1.19, max 5.39; fixed lower on 10 targets (the free fit in a worse minimum)
        </label>
        <input type="number" value="${p.asymmetry.toFixed(3)}" step="0.01" min="0" max="1"
          oninput="updatePeakParam(${p.id},'asymmetry',parseFloat(this.value))">
      </div>
      <div class="field">
        <label data-xps-tip="Controls the Gaussian-Lorentzian character of the peak. η = 0% is pure Gaussian, η = 100% is pure Lorentzian. A common starting point for XPS is ~30% Lorentzian (GL(30)), which works well for most insulating and polymeric samples. The optimal value depends on your spectrometer and the chemical environment. Let the optimizer refine this unless you have a reason to fix it.">GL mixing &eta; (0=Gauss, 100=Lorentz)</label>
        <div style="display:flex;gap:8px;align-items:center">
          <input type="range" min="0" max="100" step="1" value="${p.glMix}"
            oninput="updatePeakParam(${p.id},'glMix',parseFloat(this.value));document.getElementById('glmix-${p.id}').textContent=this.value+'%'">
          <span id="glmix-${p.id}" style="font-family:var(--mono);font-size:11px;min-width:42px">${(+p.glMix).toFixed(3)}%</span>
          ${!isLinked ? `<button class="lock-btn${p.fixGlMix ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixGlMix',this)" title="${p.fixGlMix ? 'Unlock' : 'Lock'} during fitting">${p.fixGlMix ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
        </div>
      </div>
    `;
  } else if (p.shape === 'GL') {
    return `
      <div class="field">
        <label data-xps-tip="Controls the Gaussian-Lorentzian character of the peak. η = 0% is pure Gaussian, η = 100% is pure Lorentzian. A common starting point for XPS is ~30% Lorentzian (GL(30)), which works well for most insulating and polymeric samples. The optimal value depends on your spectrometer and the chemical environment. Let the optimizer refine this unless you have a reason to fix it.">GL mixing &eta; (0=Gauss, 100=Lorentz)</label>
        <div style="display:flex;gap:8px;align-items:center">
          <input type="range" min="0" max="100" step="1" value="${p.glMix}"
            oninput="updatePeakParam(${p.id},'glMix',parseFloat(this.value));document.getElementById('glmix-${p.id}').textContent=this.value+'%'">
          <span id="glmix-${p.id}" style="font-family:var(--mono);font-size:11px;min-width:42px">${(+p.glMix).toFixed(3)}%</span>
          ${!isLinked ? `<button class="lock-btn${p.fixGlMix ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixGlMix',this)" title="${p.fixGlMix ? 'Unlock' : 'Lock'} during fitting">${p.fixGlMix ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
        </div>
      </div>
    `;
  } else if (p.shape === 'DS') {
    return `
      <div class="asym-field">
        <label data-xps-tip="The singularity index controlling the asymmetric tail from metallic screening. Typical values: 0.02-0.05 for simple metals (Cu, Ag, Au), 0.05-0.15 for graphite and transition metals, up to 0.2 for strong screening. Higher values produce a longer tail toward higher binding energy.">DS &alpha; (asymmetry) <span style="color:var(--text3);font-size:9px">typical 0.02&ndash;0.15</span>
          ${!isLinked ? `<button class="lock-btn${p.fixDsAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixDsAlpha',this)" title="${p.fixDsAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixDsAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
        </label>
        <input type="number" value="${p.dsAlpha.toFixed(3)}" step="0.005" min="0" max="0.5"
          oninput="updatePeakParam(${p.id},'dsAlpha',parseFloat(this.value))">
      </div>
      <div class="field">
        <label data-xps-tip="Controls the Lorentzian lifetime broadening width in eV. Typical values range from 0.1 to 0.5 eV. Larger values produce broader peaks.">DS &gamma; (tail decay)
          ${!isLinked ? `<button class="lock-btn${p.fixDsGamma ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixDsGamma',this)" title="${p.fixDsGamma ? 'Unlock' : 'Lock'} during fitting">${p.fixDsGamma ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
        </label>
        <input type="number" value="${p.dsGamma.toFixed(4)}" step="0.001" min="0"
          oninput="updatePeakParam(${p.id},'dsGamma',parseFloat(this.value))">
      </div>
    `;
  } else if (p.shape === 'DSG_LA') {
    return `
      <div style="font-size:10px;color:var(--text3);margin-bottom:6px">
        CasaXPS convention — tail toward higher BE
      </div>
      <div class="field-row">
        <div class="field">
          <label data-xps-tip="Dimensionless asymmetry parameter (0-0.5). Controls the tail toward higher binding energy from metallic screening. Similar in meaning to the DS singularity index. Typical values: 0.01-0.05 for most metals.">&alpha; (asymmetry, 0&ndash;0.5)
            ${!isLinked ? `<button class="lock-btn${p.fixLaAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixLaAlpha',this)" title="${p.fixLaAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixLaAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
          </label>
          <input type="number" value="${p.laAlpha.toFixed(3)}" step="0.005" min="0" max="0.5"
            oninput="updatePeakParam(${p.id},'laAlpha',parseFloat(this.value))">
        </div>
        <div class="field">
          <label data-xps-tip="Lorentzian half-width in eV. Controls the intrinsic lifetime broadening. Typical values: 0.05-0.5 eV.">&beta; Lorentz HW (eV)
            ${!isLinked ? `<button class="lock-btn${p.fixLaBeta ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixLaBeta',this)" title="${p.fixLaBeta ? 'Unlock' : 'Lock'} during fitting">${p.fixLaBeta ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
          </label>
          <input type="number" value="${p.laBeta.toFixed(3)}" step="0.01" min="0.05" max="2.0"
            oninput="updatePeakParam(${p.id},'laBeta',parseFloat(this.value))">
        </div>
      </div>
      <div class="field">
        <label data-xps-tip="Gaussian full width at half maximum in eV. Represents instrumental and phonon broadening. Typical values: 0.2-1.5 eV depending on your spectrometer pass energy.">m Gauss FWHM (eV)
          ${!isLinked ? `<button class="lock-btn${p.fixLaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixLaM',this)" title="${p.fixLaM ? 'Unlock' : 'Lock'} during fitting">${p.fixLaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
        </label>
        <input type="number" value="${p.laM.toFixed(3)}" step="0.01" min="0.05" max="4.0"
          oninput="updatePeakParam(${p.id},'laM',parseFloat(this.value))">
      </div>
    `;
  } else if (p.shape === 'LACX') {
    return `
      <div style="font-size:10px;color:var(--text3);margin-bottom:6px">
        True CasaXPS LA — &alpha;/&beta; are exponents (BE convention: &alpha; applies to high-BE side)
      </div>
      <div class="field-row">
        <div class="field">
          <label data-xps-tip="High-BE-side exponent. CasaXPS-equivalent α. Smaller α extends the high-BE tail. Default 1.0 (symmetric Lorentzian). Bounds 0.1–5.0.">&alpha; (high-BE exp)
            ${!isLinked ? `<button class="lock-btn${p.fixCaAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaAlpha',this)" title="${p.fixCaAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixCaAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
          </label>
          <input type="number" value="${(p.caAlpha ?? 1.0).toFixed(3)}" step="0.05" min="0.1" max="5.0"
            oninput="updatePeakParam(${p.id},'caAlpha',parseFloat(this.value))">
        </div>
        <div class="field">
          <label data-xps-tip="Low-BE-side exponent. CasaXPS-equivalent β. Default 1.0 (symmetric). Bounds 0.1–5.0.">&beta; (low-BE exp)
            ${!isLinked ? `<button class="lock-btn${p.fixCaBeta ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaBeta',this)" title="${p.fixCaBeta ? 'Unlock' : 'Lock'} during fitting">${p.fixCaBeta ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
          </label>
          <input type="number" value="${(p.caBeta ?? 1.0).toFixed(3)}" step="0.05" min="0.1" max="5.0"
            oninput="updatePeakParam(${p.id},'caBeta',parseFloat(this.value))">
        </div>
      </div>
      <div class="field">
        <label data-xps-tip="Gaussian convolution kernel width in DATA POINTS (not eV). Integer 0–499. m=0 = no convolution. Effective eV width ≈ (m/3) × dx where dx is the data step size.">m (Gauss kernel pts)
          ${!isLinked ? `<button class="lock-btn${p.fixCaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaM',this)" title="${p.fixCaM ? 'Unlock' : 'Lock'} during fitting">${p.fixCaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
        </label>
        <input type="number" value="${Math.round(p.caM ?? 50)}" step="1" min="0" max="499"
          oninput="updatePeakParam(${p.id},'caM',parseFloat(this.value))">
      </div>
    `;
744:    def fit():
762:              "center_min":   283.0,              // optional bound
765:              "amplitude_min": 0,                 // optional (default 0)
/Users/skyefortier/xps-app/venv/bin/python
/Users/skyefortier/xps-app/venv/bin/python3
/Users/skyefortier/xps-app/venv/bin/python3.12
tests/test_component_required.py
tests/test_scattered_starts.py
tests/test_component_support.py
tests/autofit/test_preseed_dominants.py
tests/test_differential_evolution_bounds.py
tests/js/unsupported_components.test.js
tests/js/scattered_starts.test.js

 exited 1 in 37784ms:
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
not ok 1 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1619.798337
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
not ok 2 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1202.846058
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
not ok 3 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1100.662526
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
not ok 4 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1149.882988
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
not ok 5 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1207.08194
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
not ok 6 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1290.955241
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
not ok 7 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1209.31126
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
not ok 8 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX # TODO LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit
  ---
  duration_ms: 1239.644478
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
not ok 9 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1196.061676
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
not ok 10 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1277.978186
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
not ok 11 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1171.357178
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
not ok 12 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1129.143994
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
not ok 13 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1178.077754
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
not ok 14 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1274.367366
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
not ok 15 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1254.217948
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
not ok 16 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1254.293611
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
not ok 17 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1100.907439
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
not ok 18 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1232.009731
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
not ok 19 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1220.153624
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
not ok 20 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1187.51793
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
not ok 21 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1188.685512
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
not ok 22 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1220.956577
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
not ok 23 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1157.242322
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
not ok 24 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1213.793126
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
not ok 25 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1231.667526
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
not ok 26 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1252.938422
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
not ok 27 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1190.712695
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
not ok 28 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1166.693804
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:193:3'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:194:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
not ok 29 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1160.47048
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:206:1'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:207:33)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
not ok 30 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1170.004323
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:217:1'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:225:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
not ok 31 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1243.944502
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:235:1'
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
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:244:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
1..31
# tests 31
# suites 0
# pass 0
# fail 29
# cancelled 0
# skipped 0
# todo 2
# duration_ms 37821.958596

exec
/bin/zsh -lc "cat docs/findings/a03/voigt_eta_summary.txt; sed -n '7595,7625p' templates/index.html; rg -n 'function getROIData|function _bgWindowIndices|function _peakArea' templates/index.html; rg -n 'def load_project_tabs' autofit/reference.py; nl -ba tests/js/lineshape_roundtrip.test.js | head -24" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
targets 90, both fits converged 90
free eta of 180 Voigt components: 60 at 0 (pure Gaussian), 16 at 1 (pure Lorentzian), 24 within 0.4–0.6
per-Voigt-component DISPLAYED area vs the fitted curve (%): median 13.89, p90 19.18, max 20.11; > 10 % on 116 of 180; displayed high (eta < 0.5) 110, low 70
A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.48, max 1.55; > 1 pp on 35 targets
B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: median 0.34, p90 0.54, max 1.02; > 1 pp on 1 targets
C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 33 targets
chi2r fixed/free: median 1.09, p90 1.19, max 5.39; fixed lower on 10 targets (the free fit in a worse minimum)
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
    const bgType  = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
4545:function _bgWindowIndices(be, bgStart, bgEnd) {
4936:function getROIData() {
8320:function _peakArea(p, be) {
41:def load_project_tabs(path: str | Path) -> list[dict]:
     1	// Page → server → page identity (A03, 2026-09-22).
     2	//
     3	// The parity harness (lineshape_parity.test.js) proves the two EVALUATORS
     4	// agree for the same parameters. It cannot see a request that asks the
     5	// server to fit a parameter the page never draws: until A03 a "Voigt" was
     6	// sent as pseudo_voigt_gl with gl_ratio FREE from 0.3 while evalPeak drew
     7	// η = 0.5, so every chart component, area, percentage and export for a
     8	// Voigt was the 0.5 curve under parameters fitted for another mix (on the
     9	// 90 committed Voigt targets: displayed areas 12 % off the fitted curve at
    10	// the median (13.9 %), 20 % at worst; 60 of 180 components had gone to pure
    11	// Gaussian, 16 to pure Lorentzian). This test closes that class: for every
    12	// shape, build the request with the PAGE's own peakToBackendSpec, fit it
    13	// on the server (fitting.run_fit, no background, Trust-Region), apply the
    14	// result with the page's own _applyBackendParams, and require the curve the
    15	// page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
    16	// server FITTED (individual_peaks[].y).
    17	//
    18	// Two shapes carry a known drawn-vs-fitted gap and are marked todo with the
    19	// unit that owns it: LACX (the page sends m free and draws it ROUNDED —
    20	// the caM clamp unit) and DSG_LA (the page's quadrature — see the parity
    21	// harness's section (D)).
    22	const { test } = require('node:test');
    23	const assert = require('node:assert');
    24	const { execFileSync } = require('node:child_process');

exec
/bin/zsh -lc "sed -n '4535,4580p' templates/index.html; sed -n '4936,4965p' templates/index.html; sed -n '8315,8330p' templates/index.html; sed -n '35,65p' autofit/reference.py; sed -n '744,850p' app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
// grid points inside the bounds, falls back to the full range.
// Contract notes (Codex round 1, both runs): (a) the window is the contiguous
// index span from the FIRST to the LAST in-range point — exact on a monotonic
// grid, which is what createTab guarantees (it sorts descending) and what
// every saved project written by this app carries; a hand-edited
// non-monotonic rawBE would make the span include out-of-window rows, and
// the preview and the request would still agree. (b) Indices are computed on
// the frontend grid before uploadToBackend rounds BE to 4 decimals; the
// backend only ever applies the indices to that same-length, same-order
// session grid, so rounding cannot change which rows are used.
function _bgWindowIndices(be, bgStart, bgEnd) {
  const n = be.length;
  const full = { i0: 0, i1: n - 1 };
  const a = parseFloat(bgStart), b = parseFloat(bgEnd);
  if (!Number.isFinite(a) || !Number.isFinite(b)) return full;
  const lo = Math.min(a, b), hi = Math.max(a, b);
  let i0 = -1, i1 = -1;
  for (let i = 0; i < n; i++) {
    if (be[i] >= lo && be[i] <= hi) { if (i0 < 0) i0 = i; i1 = i; }
  }
  if (i0 < 0 || i1 - i0 < 1) return full;
  return { i0, i1 };
}

// Pure-functional background computation. Takes explicit `settings`
// (matches the shape of tab.ui — bgType, bgStart, bgEnd, shirleyIter,
// endpointAvg) instead of reading from DOM. Used by stack-view render
// to reproduce a source tab's background from its persisted ui state.
// computeBackground() below is a thin DOM-reading wrapper for callers
// in the single-tab plot path.
function computeBackgroundCore(be, intensity, settings) {
  const type = settings.bgType;
  const iter = parseInt(settings.shirleyIter) || 5;
  const nAvg = parseInt(settings.endpointAvg) || 1;

  // Manual anchor background uses its own anchor points, not bg-start/end
  if (type === 'manual') return manualAnchorBackground(be, intensity);

  // The background window — the one definition shared with both /api/fit
  // request builders (see _bgWindowIndices). A blank bound or a window with
  // fewer than two points falls back to the full range inside the helper;
  // slicing the full range below is then a no-op.
  const { i0, i1 } = _bgWindowIndices(be, settings.bgStart, settings.bgEnd);

  // Slice data to background region
  const beSub = be.slice(i0, i1 + 1);
function getROIData() {
  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
  // NaN bounds mean the field is empty — use full range rather than filtering everything out
  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
  const roiMax = isNaN(roiMaxRaw) ?  Infinity : roiMaxRaw;
  const corrBE = getCorrectedBE();
  const be = [], inten = [];
  for (let i = 0; i < corrBE.length; i++) {
    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
      be.push(corrBE[i]);
      inten.push(state.rawIntensity[i]);
    }
  }
  return { be, inten };
}

function maxROI() {
  if (!state.rawBE.length) return;
  const be = getCorrectedBE();
  const lo = _arrMin(be);
  const hi = _arrMax(be);
  document.getElementById('roi-min').value = lo.toFixed(1);
  document.getElementById('roi-max').value = hi.toFixed(1);
  document.getElementById('bg-start').value = hi.toFixed(1);
  document.getElementById('bg-end').value = lo.toFixed(1);
  updatePlot();
}

function autoSetROI() {
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


# ─────────────────────────────────────────────────────────────────────────────
# Project loading
# ─────────────────────────────────────────────────────────────────────────────

def load_project_tabs(path: str | Path) -> list[dict]:
    """
    Return the list of raw tab dicts from a ``.proj.zip`` or ``.proj.json``.

    Zip layout (saved by ``_doSaveProject`` for >= 5 tabs): ``manifest.json``
    with ``{version: 3, spectra: [{index, filename, ...}]}`` plus one
    ``spectrum_<i>_<name>.json`` per tab.  JSON layout (< 5 tabs): a single
    object with ``tabs: [...]``.
    """
    path = Path(path)
    if path.suffix == ".zip" or path.name.endswith(".proj.zip"):
        with zipfile.ZipFile(path) as z:
            manifest = json.loads(z.read("manifest.json"))
            if manifest.get("version") != 3:
                raise ValueError(
                    f"{path.name}: unsupported project version "
                    f"{manifest.get('version')!r} (expected 3)"
                )
            tabs = []
            for entry in manifest.get("spectra", []):
                tabs.append(json.loads(z.read(entry["filename"])))
            return tabs
    data = json.loads(path.read_text())
    if not isinstance(data.get("tabs"), list):
        raise ValueError(f"{path.name}: no 'tabs' array — not a v3 project JSON")
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

        # Scattered-starts check (optional; the page sends 3). Same clean-400
        # treatment as n_perturb; run_fit validates again for other callers.
        n_starts = body.get("n_starts", 0)
        if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
            return _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
        # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
        require_component = body.get("require_component")
        if require_component is not None and not isinstance(require_component, (str, int)):
            return _err("require_component must be a peak id")

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

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp = require('\\''child_process'\\''); const orig = cp.execFileSync;
cp.execFileSync = (file,args,opts) => file.includes('\\''python'\\'') ? orig(file,['\\''-c'\\'', '\\''import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; p=sys.argv.pop(1); runpy.run_path(p,run_name=\"__main__\")'\\'', ...args],opts) : orig(file,args,opts);
require('\\''./tests/js/lineshape_roundtrip.test.js'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import pytest
raise SystemExit(pytest.main(['\\''-q'\\'','\\''-s'\\'','\\''-p'\\'','\\''no:cacheprovider'\\'','\\''tests/test_voigt_contract.py'\\'','\\''tests/test_differential_evolution_bounds.py'\\'','\\''tests/test_component_required.py'\\'','\\''tests/test_scattered_starts.py'\\'']))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\''); const tabs=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'',\"import json,zipfile,pathlib\\nout=[]\\nfor p in pathlib.Path(\\\"docs/autofit/test_data\\\").glob(\\\"*.proj.zip\\\"):\\n with zipfile.ZipFile(p) as z:\\n  for e in json.loads(z.read(\\\"manifest.json\\\"))[\\\"spectra\\\"]:\\n   t=json.loads(z.read(e[\\\"filename\\\"]))\\n   if t.get(\\\"fitResult\\\") and any(p.get(\\\"shape\\\")==\\\"Voigt\\\" for p in t.get(\\\"peaks\\\",[])): out.append(dict(project=p.name,**t))\\nprint(json.dumps(out))\"],{maxBuffer:1<<27,encoding:'\\''utf8'\\''}));
let changed=[];
for(const t of tabs){
 const u=t.ui,b=t.rawBE.map(x=>x-(t.ccShift||0)).filter(x=>x>=+u.roiMin&&x<=+u.roiMax),r=b.map(x=>+x.toFixed(4));
 const idx=a=>a.flatMap((x,i)=>x>=Math.min(+u.bgStart,+u.bgEnd)&&x<=Math.max(+u.bgStart,+u.bgEnd)?[i]:[]);
 const a=idx(b),c=idx(r);
 if(a[0]"'!==c[0]||a.at(-1)!==c.at(-1))changed.push({project:t.project,tab:t.name,ui:[u.bgStart,u.bgEnd],raw:[a[0],a.at(-1)],rounded:[c[0],c.at(-1)],edge:[b[a[0]],b[a.at(-1)]],bg:u.bgType});
}
console.log(JSON.stringify({total:tabs.length,changed},null,2));'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 263ms:
{
  "total": 55,
  "changed": []
}

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\''); const tabs=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'',\"import json,zipfile,pathlib\\nout=[]\\nfor p in pathlib.Path(\\\"docs/autofit/test_data\\\").glob(\\\"*.proj.zip\\\"):\\n with zipfile.ZipFile(p) as z:\\n  for e in json.loads(z.read(\\\"manifest.json\\\"))[\\\"spectra\\\"]:\\n   t=json.loads(z.read(e[\\\"filename\\\"]))\\n   if t.get(\\\"fitResult\\\") and any(p.get(\\\"shape\\\")==\\\"Voigt\\\" for p in t.get(\\\"peaks\\\",[])): out.append(dict(project=p.name,**t))\\nprint(json.dumps(out))\"],{maxBuffer:1<<27,encoding:'\\''utf8'\\''}));
const a=tabs.map(t=>{const u=t.ui,b=t.rawBE.map(x=>x-(t.ccShift||0)).filter(x=>x>=+u.roiMin&&x<=+u.roiMax),r=b.map(x=>+x.toFixed(4));return {project:t.project,tab:t.name,first:b.slice(0,3),rounded:r.slice(0,3),step_error_pct:100*((r[0]-r[1])/(b[0]-b[1])-1),max_energy_delta:Math.max(...b.map((x,i)=>Math.abs(x-r[i])))};}).sort((a,b)=>Math.abs(b.step_error_pct)-Math.abs(a.step_error_pct));
console.log(JSON.stringify(a.slice(0,4),null,2));
const j=JSON.parse(fs.readFileSync('\\''docs/findings/a03/local_server_gap.json'\\''));
for(const [k,rows] of Object.entries(j.regions)) console.log(k,rows.map(r=>({target:r.target,d:[r.max_dCenter_meV,r.max_dFwhm_pct,r.max_dArea_pct,r.max_dFrac_pp],held:[r.held_max_dCenter_meV,r.held_max_dFwhm_pct,r.held_max_dArea_pct,r.held_max_dFrac_pp],chi:[r.local_chi2r,r.server_chi2r,r.server_held_m_chi2r],pct:100*(r.local_chi2r/r.server_held_m_chi2r-1)})));
console.log(JSON.parse(fs.readFileSync('\\''docs/findings/a03/voigt_saved_vs_refit.json'\\'')).summary);'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 239ms:
[
  {
    "project": "Cl2p_projfit_test.proj.zip",
    "tab": "U4f Scan_2",
    "first": [
      405.04599999999994,
      404.9459999999998,
      404.8459999999999
    ],
    "rounded": [
      405.046,
      404.946,
      404.846
    ],
    "step_error_pct": -1.7053025658242404e-10,
    "max_energy_delta": 2.2737367544323206e-13
  },
  {
    "project": "Cl2p_projfit_test.proj.zip",
    "tab": "U4f Scan_4",
    "first": [
      405.0199999999999,
      404.9199999999998,
      404.8199999999999
    ],
    "rounded": [
      405.02,
      404.92,
      404.82
    ],
    "step_error_pct": -1.7053025658242404e-10,
    "max_energy_delta": 2.8421709430404007e-13
  },
  {
    "project": "B4C-UCl4.proj.zip",
    "tab": "U4f Scan_1",
    "first": [
      406.2099999999999,
      406.1099999999998,
      406.0099999999999
    ],
    "rounded": [
      406.21,
      406.11,
      406.01
    ],
    "step_error_pct": -1.7053025658242404e-10,
    "max_energy_delta": 2.8421709430404007e-13
  },
  {
    "project": "B4C-UCl4.proj.zip",
    "tab": "U4f Scan_7",
    "first": [
      406.2099999999999,
      406.1099999999998,
      406.0099999999999
    ],
    "rounded": [
      406.21,
      406.11,
      406.01
    ],
    "step_error_pct": -1.7053025658242404e-10,
    "max_energy_delta": 2.8421709430404007e-13
  }
]
C1s [
  {
    target: 'C1s Scan_0',
    d: [
      3.8402331608153872,
      0.2885686377046781,
      0.4179468101759065,
      0.03985203589995101
    ],
    held: [
      3.8402331608153872,
      0.2885686377046781,
      0.4179468101759065,
      0.03985203589995101
    ],
    chi: [ 4.352986964401883, 4.35719248064345, 4.35719248064345 ],
    pct: -0.09651894563412755
  },
  {
    target: 'C1s Scan_1',
    d: [
      2.635049739240003,
      0.5016632184147163,
      1.3959223341595384,
      0.32230081705666436
    ],
    held: [
      2.635049739240003,
      0.5016632184147163,
      1.3959223341595384,
      0.32230081705666436
    ],
    chi: [ 13.07421180007245, 13.066130162252884, 13.066130162252884 ],
    pct: 0.061851808601387503
  },
  {
    target: 'C1s Scan_2',
    d: [
      3.4886504280393638,
      0.07286490885719532,
      0.3650057752607405,
      0.04894005698611037
    ],
    held: [
      3.4886504280393638,
      0.07286490885719532,
      0.3650057752607405,
      0.04894005698611037
    ],
    chi: [ 4.0837589252567215, 4.086955847696259, 4.086955847696259 ],
    pct: -0.0782225832299921
  },
  {
    target: 'C1s Scan_3',
    d: [
      1.6114622980580862,
      0.0576084761082063,
      0.13443184552095477,
      0.01901946420254097
    ],
    held: [
      1.6114622980580862,
      0.0576084761082063,
      0.13443184552095477,
      0.01901946420254097
    ],
    chi: [ 4.425159626748753, 4.431665047182297, 4.431665047182297 ],
    pct: -0.1467940461267525
  },
  {
    target: 'C1s Scan_4',
    d: [
      41.87075389546635,
      8.969517734781896,
      99.85202428954928,
      15.066299222843721
    ],
    held: [
      41.87075389546635,
      8.969517734781896,
      99.85202428954928,
      15.066299222843721
    ],
    chi: [ 18.217549717868096, 19.05635979966984, 19.05635979966984 ],
    pct: -4.401733020470555
  },
  {
    target: 'C1s Scan_5',
    d: [
      0.5678477010633287,
      0.030304112806955885,
      0.05751329703411745,
      0.004804121845305986
    ],
    held: [
      0.5678477010633287,
      0.030304112806955885,
      0.05751329703411745,
      0.004804121845305986
    ],
    chi: [ 4.33059226290776, 4.332040777459363, 4.332040777459363 ],
    pct: -0.033437232611932544
  },
  {
    target: 'C1s Scan_6',
    d: [
      2.094895057780377,
      0.1667540656891342,
      0.2369670417026848,
      0.021811370309338107
    ],
    held: [
      2.094895057780377,
      0.1667540656891342,
      0.2369670417026848,
      0.021811370309338107
    ],
    chi: [ 5.211351022553858, 5.230133054457079, 5.230133054457079 ],
    pct: -0.3591119328640313
  },
  {
    target: 'C1s Scan_7',
    d: [
      1.3962350000724655,
      0.24116725970961816,
      0.3615884354576382,
      0.03536729184366039
    ],
    held: [
      1.3962350000724655,
      0.24116725970961816,
      0.3615884354576382,
      0.03536729184366039
    ],
    chi: [ 7.993689089250659, 8.015808637637003, 8.015808637637003 ],
    pct: -0.27594905749726006
  },
  {
    target: 'C1s Scan_8',
    d: [
      0.83405029045025,
      0.12465874612326289,
      0.1787839172815442,
      0.018047550793454104
    ],
    held: [
      0.83405029045025,
      0.12465874612326289,
      0.1787839172815442,
      0.018047550793454104
    ],
    chi: [ 2.742274861910659, 2.7407625419220305, 2.7407625419220305 ],
    pct: 0.055178803909372576
  }
]
U4f [
  {
    target: 'U4f Scan_0',
    d: [
      1.5746607713822414,
      0.21957561263026282,
      0.17276333502012076,
      0.013308282211811628
    ],
    held: [
      1.519279114006622,
      0.21289000463879937,
      0.28359942852270725,
      0.014859190782517268
    ],
    chi: [ 2.065244443877729, 2.0551875684374585, 2.0491576562300122 ],
    pct: 0.7850439227459427
  },
  {
    target: 'U4f Scan_1',
    d: [
      4.271689838958537,
      1.3550854849925686,
      1.9535255311116217,
      0.12330890043952131
    ],
    held: [
      3.9750460014715827,
      1.4559117331585103,
      2.107047834610798,
      0.12210426684961528
    ],
    chi: [ 2.296093573631544, 2.2667421415660436, 2.2601976569590905 ],
    pct: 1.5881759969943676
  },
  {
    target: 'U4f Scan_2',
    d: [
      1.9401325737931074,
      1.3889213118864152,
      0.3757655700552309,
      0.016219614306994812
    ],
    held: [
      1.4769946210435592,
      0.30077094859223275,
      0.41177065384457867,
      0.0224615533079231
    ],
    chi: [ 1.9363101556852207, 1.9400626785128714, 1.9349336266995205 ],
    pct: 0.07114088910884497
  },
  {
    target: 'U4f Scan_3',
    d: [
      2.9959296796278068,
      2.5937151574351613,
      1.7412020303063436,
      0.12476533004328605
    ],
    held: [
      1.424996244054455,
      0.28902214712275276,
      0.4041223656612636,
      0.019931624585985824
    ],
    chi: [ 1.731754888573654, 1.7320297992148836, 1.7306122270448678 ],
    pct: 0.06602643335864578
  },
  {
    target: 'U4f Scan_4',
    d: [
      26.58740803605042,
      5.29503868340595,
      8.324851997832605,
      0.330385536114678
    ],
    held: [
      13.350128184413279,
      3.1314811620814065,
      5.267672920032595,
      0.18988172536209824
    ],
    chi: [ 1.9704477171249217, 1.7982704261503648, 1.870376646451508 ],
    pct: 5.350316518508147
  },
  {
    target: 'U4f Scan_5',
    d: [
      4.67610014567299,
      4.261786708909321,
      6.648582529188795,
      0.34932218014270333
    ],
    held: [
      6.303465103997041,
      3.505591425500687,
      5.490539368228675,
      0.24615136704759233
    ],
    chi: [ 2.3928635306048918, 2.173852692315494, 2.182160504818794 ],
    pct: 9.655707053665807
  },
  {
    target: 'U4f Scan_6',
    d: [
      28.7684068875933,
      15.809964778791286,
      8.88303776367998,
      0.7658566228242125
    ],
    held: [
      3.6326385103393477,
      1.0713453768573133,
      1.5887110733381782,
      0.06940184966579
    ],
    chi: [ 2.657291813593791, 2.797581089317341, 2.6287976699999613 ],
    pct: 1.0839230390001786
  },
  {
    target: 'U4f Scan_7',
    d: [
      2.623444500898131,
      0.35849528781087825,
      0.4877998957486418,
      0.035840428963344884
    ],
    held: [
      2.5447976101418135,
      0.3990464275176131,
      0.5509473590417868,
      0.03670897357778008
    ],
    chi: [ 1.7635921032129218, 1.7566316793234622, 1.7514615928539647 ],
    pct: 0.6925935691910245
  },
  {
    target: 'U4f Scan_8',
    d: [
      5.681111538024197,
      5.017080020509967,
      8.305336303107158,
      0.32285014407215096
    ],
    held: [
      5.826128925832563,
      4.973490351394084,
      8.243232417685697,
      0.32493707104317215
    ],
    chi: [ 4.655520835587359, 4.129258441352779, 4.11711950166436 ],
    pct: 13.077136422815737
  }
]
{
  n_tabs: 55,
  n_converged: 55,
  dFrac_pp: {
    median: 0.36397402720980065,
    p90: 0.5078511773598887,
    max: 0.6882979245316376
  },
  gt_1pp: 0,
  voigt_dArea_pct: {
    median: 4.576866262303724,
    p90: 7.556793905659809,
    max: 15.300735561732603
  }
}

 succeeded in 55869ms:
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
  duration_ms: 1768.810299
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
ok 2 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1746.83793
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
ok 3 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1855.678531
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
ok 4 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1758.723109
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
ok 5 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1767.928815
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
ok 6 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1872.516134
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 7 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1844.165165
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
  duration_ms: 1773.418511
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
  duration_ms: 1808.085347
  type: 'test'
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
ok 10 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1753.341733
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
ok 11 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1829.279122
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
ok 12 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1826.351657
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
ok 13 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1762.826687
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
ok 14 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1820.203493
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
ok 15 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1747.311795
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
ok 16 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1768.362006
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
ok 17 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1897.874948
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
ok 18 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1798.799198
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
ok 19 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1775.646871
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
ok 20 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1838.423849
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
ok 21 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1795.304515
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
ok 22 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1799.566895
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
ok 23 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1843.591765
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
ok 24 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1763.371544
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
ok 25 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1944.734302
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
ok 26 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1743.545722
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
ok 27 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1758.692771
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
ok 28 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1843.138762
  type: 'test'
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
ok 29 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1733.815133
  type: 'test'
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
ok 30 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1801.32515
  type: 'test'
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
ok 31 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1837.417765
  type: 'test'
  ...
1..31
# tests 31
# suites 0
# pass 29
# fail 0
# cancelled 0
# skipped 0
# todo 2
# duration_ms 55897.690495

codex
The measurement script still differs from the page: Run Fit retains the unrounded ROI grid in `fitResult.be`, but the script integrates refitted peaks on the rounded upload grid. Its bridge also selects background indices after rounding; the page selects them before. The 55 committed tabs have only floating-point-scale grid differences, so this does not invalidate their reported summary. I’m testing a higher-precision grid to measure the failure.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import fitting, numpy as np
from lmfit import Model
def pars(s): return fitting._make_peak_params(Model(fitting._SHAPE_FUNCS[s[\"shape\"]],prefix=\"p1_\"),s,\"p1_\",[s])
base=dict(id=1,shape=\"gaussian\",center=0.,amplitude=100.,fwhm=1.)
for name,changes in [(\"negative amplitude\",dict(amplitude=-7,fix_amplitude=True)),(\"out of window\",dict(center=4,center_min=-2,center_max=2,fix_center=True)),(\"DS m zero\",dict(shape=\"ds_g\",m_gauss=0,fix_m_gauss=True))]:
 s=dict(base,**changes); p=pars(s); namep={\"negative amplitude\":\"amplitude\",\"out of window\":\"center\",\"DS m zero\":\"m_gauss\"}[name]; k=\"p1_\"+namep
 fitting._finite_search_box(p,np.linspace(-5,5,101),np.ones(101))
 sc=fitting._scattered_start(p,np.random.default_rng(1))
 unlock=dict(s); unlock[\"fix_\"+namep]=False; free=pars(unlock)
 print(name,\"held\",p[k].value,p[k].min,p[k].max,p[k].vary,\"scattered\",sc[k].value,\"new free\",free[k].value,free[k].min,free[k].max)
 copied=[]
 class Res: chisqr=11.; success=True
 fitting._component_required(lambda kept:(copied.append(kept) or Res()),p,[\"p2_\"],np.ones(101),np.ones(101),10.,1,3)
 print(\"required kept\",copied[0][k].value,copied[0][k].vary)
x=np.linspace(-5,5,101); y=100*np.exp(-x*x)+10
for method in [\"least_squares\",\"differential_evolution\"]:
 s=dict(base,amplitude=-7,fix_amplitude=True)
 try:
  r=fitting.run_fit(x,y,[s],background_method=\"none\",fit_kws={\"method\":method})
  print(method,r[\"success\"],r[\"individual_peaks\"][0][\"params\"][\"amplitude\"])
 except Exception as e: print(method,type(e).__name__,str(e))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "rg -n 'function updatePeakParam|Math.max.*fwhm|fix_amplitude|amplitude_min' templates/index.html tests/test_differential_evolution_bounds.py tests/test_component_required.py | head -70; nl -ba scripts/voigt_saved_vs_refit.js | sed -n '35,62p'; nl -ba tests/js/local_lm_server_parity_backend.py | sed -n '20,33p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
tests/test_differential_evolution_bounds.py:4:the page sends ``amplitude_min: 0`` and never an ``amplitude_max``; a DS+G
tests/test_differential_evolution_bounds.py:46:         "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
tests/test_differential_evolution_bounds.py:48:         "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
tests/test_differential_evolution_bounds.py:87:              "alpha": 0.05, "beta": 0.3, "m_gauss": 0.8, "amplitude_min": 0},
tests/test_differential_evolution_bounds.py:89:              "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0}]
tests/test_differential_evolution_bounds.py:152:              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
tests/test_differential_evolution_bounds.py:178:              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
tests/test_differential_evolution_bounds.py:207:              "fwhm": 1.0, "alpha": 0.05, "beta": 0.3, "m_gauss": 0.8, "amplitude_min": 0}]
tests/test_differential_evolution_bounds.py:235:              "gl_ratio": 0.3, "amplitude_min": 0},
tests/test_differential_evolution_bounds.py:237:              "gl_ratio": 0.3, "amplitude_min": 0, "constrain_to": 1, "splitting": 1.6, "area_ratio": 0.5}]
tests/test_differential_evolution_bounds.py:260:    # amplitude_min: null leaves the floor open; a generated floor of zero
tests/test_differential_evolution_bounds.py:265:              "fix_center": True, "fix_fwhm": True, "amplitude_min": None}]
tests/test_differential_evolution_bounds.py:281:            "alpha": 0.05, "beta": 0.3, "m_gauss": 0.2, "fix_amplitude": True, "fix_fwhm": True,
tests/test_differential_evolution_bounds.py:299:            "alpha": 0.0, "beta": 0.05, "m_gauss": 0.05, "fix_amplitude": True,
tests/test_differential_evolution_bounds.py:334:              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
tests/test_differential_evolution_bounds.py:368:              "amplitude_min": 0}]
tests/test_differential_evolution_bounds.py:392:              "amplitude": 1000.0, "amplitude_min": 0, "fwhm": 1.0, "fix_fwhm": True}]
tests/test_differential_evolution_bounds.py:404:              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
tests/test_differential_evolution_bounds.py:440:              "amplitude": 1000.0, "amplitude_min": 0, "fwhm": 1.0, "fix_fwhm": True}]
tests/test_differential_evolution_bounds.py:453:              "amplitude": 10.0, "amplitude_min": 0, "fwhm": 0.2}]
tests/test_differential_evolution_bounds.py:514:              "amplitude": scale, "amplitude_min": 0, "fwhm": 0.5, "fix_fwhm": True}]
tests/test_differential_evolution_bounds.py:534:              "fix_fwhm": True, "amplitude": 1.0, "amplitude_min": 0}]
tests/test_differential_evolution_bounds.py:559:    spec = {"id": 1, "shape": "gaussian", "center": case["c"], "amplitude": 1e6, "amplitude_min": 0,
tests/test_differential_evolution_bounds.py:605:            "amplitude_min": 0, "fwhm": case["w"], "fix_fwhm": True, **case["extra"]}
tests/test_differential_evolution_bounds.py:623:              "amplitude": 500.0, "amplitude_min": 0, "fwhm": 1.0},
tests/test_differential_evolution_bounds.py:625:              "amplitude": 500.0, "amplitude_min": 0, "fwhm": 1.0}]
templates/index.html:4019:  const gamma = Math.max(fwhm / 2, 1e-12);
templates/index.html:4092:  const F = Math.max(fwhm, 1e-9);
templates/index.html:4104:  const F = Math.max(fwhm, 1e-9);
templates/index.html:5755:function updatePeakParam(id, key, value) {
templates/index.html:6214:    amplitude_min: 0,
templates/index.html:6217:    fix_amplitude: !!p.fixAmplitude,
templates/index.html:7259:      spec.amplitude_min = 0;
tests/test_component_required.py:41:              "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0}]
tests/test_component_required.py:44:                      "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0})
tests/test_component_required.py:93:            "amplitude_min": 0, "constrain_to": master, "splitting": offset, "area_ratio": 0.01}
tests/test_component_required.py:154:    specs = [{"id": "1", "name": "Graphite", "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 5000.0, "fwhm": 1.4, "gl_ratio": 0.3, "amplitude_min": 0},
tests/test_component_required.py:155:             {"id": "2", "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 5000.0, "fwhm": 1.4, "gl_ratio": 0.3, "amplitude_min": 0}]
    35	for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
    36	  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
    37	  for (const t of tabs) {
    38	    if (!t.fitResult || !(t.peaks || []).some(p => p.shape === 'Voigt')) continue;
    39	    const ui = t.ui || {};
    40	    const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
    41	    if (!Number.isFinite(roiMin) || !Number.isFinite(roiMax) || !ui.bgType) continue;
    42	    const be = [], inten = [];
    43	    t.rawBE.forEach((b, i) => { const c = b - (t.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(+c.toFixed(4)); inten.push(+t.rawIntensity[i].toFixed(2)); } });
    44	    if (be.length < 10) continue;
    45	    const savedGrid = (t.fitResult.be && t.fitResult.be.length) ? t.fitResult.be : be;
    46	    const saved = JSON.parse(JSON.stringify(t.peaks));
    47	    let srv;
    48	    try {
    49	      srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be, inten, peaks: saved, ui, n_perturb: 3 }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    50	    } catch (e) { out.targets.push({ project: zp, tab: t.name, error: String(e.message).slice(0, 200) }); continue; }
    51	    const refit = JSON.parse(JSON.stringify(saved));
    52	    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; fns._applyBackendParams(refit[i], par); });
    53	    const aS = saved.map(p => area(savedGrid, p)), aR = refit.map(p => area(be, p));
    54	    const tS = aS.reduce((s, v) => s + v, 0), tR = aR.reduce((s, v) => s + v, 0);
    55	    const comps = saved.map((p, i) => ({ name: p.name, shape: p.shape, saved_area: aS[i], refit_area: aR[i],
    56	      dArea_pct: aS[i] ? 100 * (aR[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aR[i] / tR - aS[i] / tS) }));
    57	    const rec = { project: zp, tab: t.name, server_success: srv.success, chi2r: srv.chi2r, saved_grid: t.fitResult.be && t.fitResult.be.length ? 'fitResult.be' : 'roi',
    58	      max_dFrac_pp: Math.max(...comps.map(c => Math.abs(c.dFrac_pp))),
    59	      max_voigt_dArea_pct: Math.max(...comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct))), comps };
    60	    out.targets.push(rec);
    61	    console.error(zp.slice(0, 28), t.name, 'server', srv.success, 'max Δfrac', rec.max_dFrac_pp.toFixed(2), 'pp, max Voigt Δarea', rec.max_voigt_dArea_pct.toFixed(1), '%');
    62	  }
    20	lo, hi = sorted([float(ui["bgStart"]), float(ui["bgEnd"])])
    21	idx = [i for i, b in enumerate(x) if lo <= b <= hi]
    22	res = fitting.run_fit(x, y, specs, background_method=ui["bgType"], bg_start_idx=idx[0], bg_end_idx=idx[-1] + 1,
    23	                      endpoint_avg=int(ui.get("endpointAvg") or 1), fit_kws={"method": "least_squares"},
    24	                      n_perturb=int(d.get("n_perturb") or 0))   # the page sends 3; the W1 test sends none
    25	print(json.dumps({"success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"],
    26	                  "peaks": [{k: v["value"] for k, v in ip["params"].items()} for ip in res["individual_peaks"]]}))

 succeeded in 1806ms:
/Users/skyefortier/.matplotlib is not a writable directory
negative amplitude held -7 -7 inf False scattered -7.0 new free -7 0.0 inf
required kept -7 False
out of window held 4 -2 4 False scattered 4.0 new free 4 -2 2
required kept 4 False
DS m zero held 0 0 4.0 False scattered 0.0 new free 0 0.05 4.0
required kept 0 False
least_squares True {'value': -7.0, 'stderr': 0.0, 'vary': False, 'expr': None, 'min': -7.0, 'max': None}
differential_evolution True {'value': -7.0, 'stderr': None, 'vary': False, 'expr': None, 'min': -7.0, 'max': None}

exec
/bin/zsh -lc "sed -n '5755,5805p' templates/index.html; sed -n '46,95p' fitting.py; sed -n '1685,1745p' fitting.py; git log -3 --oneline; rg -n 'def test_|tmp_path|tmpdir' tests/test_differential_evolution_bounds.py tests/test_component_required.py tests/test_scattered_starts.py | tail -35" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
    Asymmetric GL pseudo‑Voigt with independent asymmetry parameter.

    fwhm      : base FWHM (used on the low‑BE side, i.e. x ≤ center)
    asymmetry : broadening factor for the high‑BE side;
                fwhm_right = fwhm × (1 + asymmetry).  0 = symmetric.
    gl_ratio  : common Lorentzian fraction for both sides.

    Both halves meet at x = center with value = amplitude.
    """
    asym = float(np.clip(asymmetry, 0.0, 1.0))
    fwhm_r = fwhm * (1.0 + asym)
    result = np.empty_like(x, dtype=float)
    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
                  result.success, result.nfev, result.message)
        for pname, par in sorted(result.params.items()):
            init = all_params[pname].value if pname in all_params else None
            delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
            log.debug("  AFTER   %-30s value=%12.6f  stderr=%s%s",
                      pname, par.value,
                      f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)

    # ── Perturb and refit to escape local minima ─────────────────────────
    if n_perturb > 0 and result.success:
        best_result = result
        best_redchi = result.redchi if result.redchi is not None else float('inf')
        rng = perturb_rng

        for attempt in range(n_perturb):
            perturbed_params = result.params.copy()
            for pname, par in perturbed_params.items():
                if par.vary and par.value != 0:
                    # Perturb by ±15% random
                    scale = 1.0 + rng.uniform(-0.15, 0.15)
                    new_val = par.value * scale
                    # Respect bounds
                    if np.isfinite(par.min):
                        new_val = max(new_val, par.min)
                    if np.isfinite(par.max):
                        new_val = min(new_val, par.max)
                    perturbed_params[pname].set(value=new_val)
                elif par.vary and par.value == 0:
                    # For zero-valued params, add small absolute perturbation
                    perturbed_params[pname].set(value=rng.uniform(0.001, 0.05))

            try:
                trial = fit_once(perturbed_params)
                trial_redchi = trial.redchi if trial.redchi is not None else float('inf')
                log.debug("  PERTURB %d/%d  redchi=%.4f  (best=%.4f)",
                          attempt + 1, n_perturb, trial_redchi, best_redchi)
                # A candidate whose search box was never cleared by its
                # refinement (differential evolution only) does not displace
                # one that was; for every other method both flags are False.
                trial_rank = (getattr(trial, "box_unverified", False), trial_redchi)
                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
                if trial.success and trial_rank < best_rank:
                    best_result = trial
                    best_redchi = trial_redchi
                    log.debug("  *** New best found! redchi improved to %.4f", best_redchi)
            except Exception:
                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
                continue

        if best_result is not result:
            log.debug("═══ PERTURB IMPROVED FIT ═══  redchi: %.4f → %.4f",
                      result.redchi, best_redchi)
            result = best_result

    # ── Scattered starts (never changes `result`) ────────────────────────────
    starts = None
    if n_starts:
        n_unlinked = sum(1 for spec in peak_specs if spec.get("constrain_to") is None)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4gSsr1SZ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1BR31N7J' (errno=Operation not permitted)
a61bd05 fix(A03): Codex round 2 (NO-GO x2) - saved side on the saved fit's grid with upload rounding; control arm at the rounded m; every shape parameter locked at each bound, which found lmfit clipping a HELD value to its bounds
4d623f5 fix(A03): Codex round 1 (NO-GO x2) - explicit measurement arms; release-note number from the page's own numbers; builders sent a mix or DS alpha of exactly 0 as the default; Voigt uncertainty note; caM attribution by a control arm
712e136 fix(A03): a Voigt is the fixed 50/50 mix on BOTH sides; page->server->page identity test; parameter-range sweep; U 4f gap re-measured
tests/test_component_required.py:167:def test_a_resolved_anchor_at_extreme_dynamic_range_is_required():
tests/test_differential_evolution_bounds.py:23:def client(tmp_path):
tests/test_differential_evolution_bounds.py:24:    app = create_app(upload_folder=str(tmp_path))
tests/test_differential_evolution_bounds.py:52:def test_api_fit_differential_evolution_runs_with_page_like_request(client):
tests/test_differential_evolution_bounds.py:72:def test_differential_evolution_agrees_with_least_squares():
tests/test_differential_evolution_bounds.py:82:def test_differential_evolution_runs_with_unbounded_dsg_centre():
tests/test_differential_evolution_bounds.py:98:def test_finite_search_box_only_touches_open_varying_bounds():
tests/test_differential_evolution_bounds.py:118:def test_finite_search_box_keeps_a_start_above_the_data_inside_the_box():
tests/test_differential_evolution_bounds.py:127:def test_other_methods_keep_an_open_amplitude_bound(monkeypatch):
tests/test_differential_evolution_bounds.py:144:def test_generated_amplitude_limit_never_sets_the_answer():
tests/test_differential_evolution_bounds.py:163:def test_without_a_converged_refinement_the_boxed_answer_is_not_a_success(monkeypatch):
tests/test_differential_evolution_bounds.py:188:def test_one_sided_centre_bound_outside_the_roi_keeps_a_real_interval(bound):
tests/test_differential_evolution_bounds.py:204:def test_one_sided_dsg_centre_bound_runs_end_to_end():
tests/test_differential_evolution_bounds.py:213:def test_generated_limits_are_not_reported_as_bounds():
tests/test_differential_evolution_bounds.py:226:def test_linked_doublet_runs_with_open_slave_bounds():
tests/test_differential_evolution_bounds.py:245:def test_nonfinite_data_is_a_validation_error_not_a_nan_bound():
tests/test_differential_evolution_bounds.py:259:def test_open_amplitude_floor_searches_negative_heights():
tests/test_differential_evolution_bounds.py:274:def test_exact_fit_beside_a_broad_one_sided_centre_bound_is_accepted(bound):
tests/test_differential_evolution_bounds.py:305:def test_the_returned_fit_is_never_worse_than_a_candidate_it_saw(monkeypatch, seed, n_perturb):
tests/test_differential_evolution_bounds.py:328:def test_exact_amplitude_just_under_a_generated_ceiling_is_accepted():
tests/test_differential_evolution_bounds.py:343:def test_refinement_runs_only_for_differential_evolution(monkeypatch):
tests/test_differential_evolution_bounds.py:360:def test_box_limited_fit_far_from_the_ceiling_is_refined():
tests/test_differential_evolution_bounds.py:383:def test_a_boundary_candidate_is_refined_before_it_can_lose_the_comparison(n_perturb):
tests/test_differential_evolution_bounds.py:400:def test_solver_options_for_differential_evolution_do_not_reach_the_refinement():
tests/test_differential_evolution_bounds.py:411:def test_a_perturbed_search_starts_from_the_requests_bounds_not_the_last_box():
tests/test_differential_evolution_bounds.py:432:def test_numerically_exact_refinement_is_accepted(n_perturb):
tests/test_differential_evolution_bounds.py:448:def test_exact_fit_on_a_requested_width_floor_is_accepted():
tests/test_differential_evolution_bounds.py:460:def test_an_unverified_perturbed_candidate_does_not_displace_a_verified_fit(monkeypatch):
tests/test_differential_evolution_bounds.py:482:def test_a_verified_candidate_displaces_an_unverified_one_even_at_higher_chi_square(monkeypatch):
tests/test_differential_evolution_bounds.py:505:def test_exact_refinement_is_accepted_at_any_intensity_scale(scale, n_perturb):
tests/test_differential_evolution_bounds.py:525:def test_zero_signal_fit_is_accepted(n_perturb):
tests/test_differential_evolution_bounds.py:551:def test_narrow_exact_peak_on_a_requested_centre_bound_is_accepted(case, n_perturb):
tests/test_differential_evolution_bounds.py:572:def test_a_converged_refinement_is_returned_without_a_chi_square_gate(monkeypatch):
tests/test_differential_evolution_bounds.py:598:def test_differential_evolution_is_never_worse_than_least_squares_from_the_same_start(case, n_perturb):
tests/test_differential_evolution_bounds.py:616:def test_the_search_still_wins_when_it_is_better_than_the_local_fit():

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import fitting,numpy as np
x=np.array([round(397.800049-.05003*i,4) for i in range(241)])
y=100+fitting._pseudo_voigt_gl(x,12000,391.8,1.6,.5); y[0]=100000
spec=dict(id=1,shape=\"pseudo_voigt_gl\",center=391.8,amplitude=12000,fwhm=1.6,gl_ratio=.5,fix_gl_ratio=True)
for label,start in [(\"page pre-round indices\",1),(\"script post-round indices\",0)]:
 r=fitting.run_fit(x,np.round(y,2),[spec],background_method=\"linear\",bg_start_idx=start,bg_end_idx=241,fit_kws={\"method\":\"least_squares\"},n_perturb=3)
 p=r[\"individual_peaks\"][0][\"params\"]
 print(label,\"success\",r[\"success\"],\"seed\",r[\"random_seed\"],\"amp\",p[\"amplitude\"][\"value\"],\"fwhm\",p[\"fwhm\"][\"value\"],\"chi\",r[\"statistics\"][\"reduced_chi_square\"])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/voigt_saved_vs_refit.js'\\'','\\''utf8'\\'');src=src.slice(0,src.indexOf('\\''const PY ='\\''))+'\\''\\nreturn {area: (be,p)=>fns.evalPeakArray(be,p).reduce((a,b)=>a+b,0)*Math.abs(be[0]-be[1])};'\\'';const {area}=new Function('\\''require'\\'','\\''__dirname'\\'',src)(require,process.cwd()+'\\''/scripts'\\'');const b=Array.from({length:241},(_,i)=>397.800049-.05003*i), r=b.map(x=>+x.toFixed(4));const p={shape:'\\''Voigt'\\'',center:391.8,amplitude:12000,fwhm:1.6};console.log({page_area:area(b,p),script_area:area(r,p),error_pct:100*(area(r,p)/area(b,p)-1),page_bg_start:1,script_bg_start:0});'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 0ms:
<anonymous_script>:3
#!/usr/bin/env node
^

SyntaxError: Invalid or unexpected token
    at new Function (<anonymous>)
    at [eval]:1:241
    at runScriptInThisContext (node:internal/vm:209:10)
    at node:internal/process/execution:446:12
    at [eval]-wrapper:6:24
    at runScriptInContext (node:internal/process/execution:444:60)
    at evalFunction (node:internal/process/execution:279:30)
    at evalTypeScript (node:internal/process/execution:291:3)
    at node:internal/main/eval_string:74:3

Node.js v22.22.2

 succeeded in 1782ms:
/Users/skyefortier/.matplotlib is not a writable directory
page pre-round indices success True seed 515968812 amp 12042.613788629857 fwhm 1.5191597499425806 chi 434.23486501533125
script post-round indices success True seed 2322987047 amp 5.638931162288419e-13 fwhm 0.10000000000000002 chi 8059162.783456694

codex
The round-trip suite passed all 29 active tests, with the two documented evaluator TODOs. The `_set` probes preserved held values through DE, scattered starts and component-removal refits; fresh unlocked requests restored the original bounds. Coverage still omits locked DS+G `m = 0.05/4` and LA `m = 499`; the existing TODO tests leave those parameters free.

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/voigt_saved_vs_refit.js'\\'','\\''utf8'\\'').replace(/"'^#!.*'"\\n/,'\\'''\\'');src=src.slice(0,src.indexOf('\\''const PY ='\\''))+'\\''\\nreturn {area: (be,p)=>fns.evalPeakArray(be,p).reduce((a,b)=>a+b,0)*Math.abs(be[0]-be[1])};'\\'';const {area}=new Function('\\''require'\\'','\\''__dirname'\\'',src)(require,process.cwd()+'\\''/scripts'\\'');const b=Array.from({length:241},(_,i)=>397.800049-.05003*i), r=b.map(x=>+x.toFixed(4));const p={shape:'\\''Voigt'\\'',center:391.8,amplitude:12000,fwhm:1.6};console.log({page_area:area(b,p),script_area:area(r,p),error_pct:100*(area(r,p)/area(b,p)-1),page_bg_start:1,script_bg_start:0});'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
{
  page_area: 24032.009975987836,
  script_area: 24017.59947138498,
  error_pct: -0.059963792530270954,
  page_bg_start: 1,
  script_bg_start: 0
}

exec
/bin/zsh -lc "nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | sed -n '92,110p'; nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | tail -28; nl -ba tests/js/lineshape_roundtrip.test.js | sed -n '161,202p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    92	## 4. Two harnesses that would have caught it
    93	
    94	- `tests/js/lineshape_roundtrip.test.js` (+ `lineshape_roundtrip_backend.py`):
    95	  for every shape, synthetic data from a truth peak, a perturbed start,
    96	  request built by the PAGE's `peakToBackendSpec`, fitted by
    97	  `fitting.run_fit` (no background, Trust-Region), applied by the page's
    98	  `_applyBackendParams`, then `evalPeakArray` on the fitted grid must equal
    99	  `individual_peaks[].y` within 1e-6 of amplitude. Plus: the Voigt request
   100	  and write-back pins, a linked Voigt pair, a locked GL mix, and the Python
   101	  twin deep-equal to the page's builder for every shape and a link. Run
   102	  against main's page it fails on Voigt (0.93 % of amplitude), the Voigt
   103	  pins and the linked pair; on the branch 10 pass, 2 todo (below).
   104	- `tests/js/lineshape_parity.test.js` section (D): each shape's FREE
   105	  parameters swept across `_make_peak_params`'s bounds (η 0–1, asymmetry
   106	  0–1, DS α 0–0.5 / γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β
   107	  0.1–5 / m 0–499, fwhm 0.1–15), one bridge call per shape.
   108	- `tests/test_voigt_contract.py`: the twin, `run_fit` holding η and
   109	  returning the 0.5 curve, the seed.
   110	
   221	5. MINOR — "χ²ᵣ differs by 8–20 %" was wrong (the four are +9.6, +10.1,
   222	   −5.0, +12.7 %), the comment's "24 %" was 20 %, row A's 1.60 was 1.61 (now
   223	   1.55 with the explicit arms); and attributing the whole residual to the
   224	   `caM` clamp was an inference — the control arm (§6) shows it is one
   225	   target of four.
   226	
   227	**Round 2 (`a03_voigt_eta_r2_verdict_run{A,B}.md`): NO-GO ×2; round-1
   228	items 1, 3, 4 confirmed closed; found:**
   229	1. MAJOR — the saved side of 2b integrated on the current ROI grid where
   230	   Results uses the saved fit's grid (11 tabs differ; 1.2 % on one area),
   231	   and the refit request bypassed the page's upload rounding (which also
   232	   sets the seed). Both fixed; re-run: median 0.35 → 0.36 pp, max 0.69 pp.
   233	2. MINOR — the control arm held m at the stored fractional value (8.199)
   234	   where the local engine rounds it (8). Now held at the rounded value;
   235	   re-run (table in §6).
   236	3. MINOR — "every shape parameter locked at its bounds" was seven cases.
   237	   Now 18: both bounds of every shape parameter of every shape, the
   238	   convolved shapes where their evaluators are exact. Doing so found a
   239	   FOURTH identity defect: lmfit clips a held value to its bounds, so a
   240	   DS+G with m locked at 0 (the delta-kernel branch the page draws) was
   241	   fitted with m = 0.05, the free-parameter floor — a convolved curve the
   242	   page never drew. `fitting._make_peak_params._set` now widens the limit
   243	   to a held value; pinned in `tests/test_voigt_contract.py`.
   244	4. MINOR — "10–13 %" (the three worse-minimum targets are +5.4, +9.7,
   245	   +13.1 % above the held-m server), "12 %" median in the harness header,
   246	   stale test counts. Corrected. Commit 712e136's message carries the
   247	   superseded round-0 numbers; the merge is fast-forward, so this plan and
   248	   the deploy-log entry are the record.
   161	// Codex round 1 reproduced two builder defects at ZERO endpoints: `p.glMix || 50`
   162	// sent an asym-GL mix of 0 as 50 and `p.dsAlpha || 0.1` a DS alpha of 0 as
   163	// 0.1 — values the page never drew; locked, the server held the substitute
   164	// and the drawn curve differed from the fitted one by 6.9 % / 8.8 % of
   165	// amplitude. Every shape parameter of every shape is now round-tripped
   166	// LOCKED AT EACH OF ITS BOUNDS (fitting._make_peak_params): GL / asym-GL
   167	// mix 0 and 1, asymmetry 0 and 1, DS α 0 and 0.5, γ 0 and 5, DS+G α 0 and
   168	// 0.49, β 0.05 and 2, LA α and β 0.1 and 5. The two convolved shapes are
   169	// exercised where their evaluators are exact (DS+G with m < 0.001, the
   170	// delta branch; LA with m = 0); their m locks at m > 0 sit under the
   171	// evaluator gaps marked todo above.
   172	const LOCKED_AT_BOUNDS = [
   173	  { label: 'GL mix 0 locked',            truth: { shape: 'GL', glMix: 0, fixGlMix: true }, held: { gl_ratio: 0 } },
   174	  { label: 'GL mix 100 locked',          truth: { shape: 'GL', glMix: 100, fixGlMix: true }, held: { gl_ratio: 1 } },
   175	  { label: 'asym-GL mix 0 locked',       truth: { shape: 'asym-GL', glMix: 0, asymmetry: 0.3, fixGlMix: true }, held: { gl_ratio: 0 } },
   176	  { label: 'asym-GL mix 100 locked',     truth: { shape: 'asym-GL', glMix: 100, asymmetry: 0.3, fixGlMix: true }, held: { gl_ratio: 1 } },
   177	  { label: 'asym-GL asymmetry 0 locked', truth: { shape: 'asym-GL', glMix: 40, asymmetry: 0, fixAsymmetry: true }, held: { asymmetry: 0 } },
   178	  { label: 'asym-GL asymmetry 1 locked', truth: { shape: 'asym-GL', glMix: 40, asymmetry: 1, fixAsymmetry: true }, held: { asymmetry: 1 } },
   179	  { label: 'DS alpha 0 locked',          truth: { shape: 'DS', dsAlpha: 0, dsGamma: 0.2, fixDsAlpha: true }, held: { alpha: 0 } },
   180	  { label: 'DS alpha 0.5 locked',        truth: { shape: 'DS', dsAlpha: 0.5, dsGamma: 0.2, fixDsAlpha: true }, held: { alpha: 0.5 } },
   181	  { label: 'DS gamma 0 locked',          truth: { shape: 'DS', dsAlpha: 0.2, dsGamma: 0, fixDsGamma: true }, held: { gamma_asym: 0 } },
   182	  { label: 'DS gamma 5 locked',          truth: { shape: 'DS', dsAlpha: 0.2, dsGamma: 5, fixDsGamma: true }, held: { gamma_asym: 5 } },
   183	  { label: 'DS+G alpha 0 locked (delta kernel)',    truth: { shape: 'DSG_LA', laAlpha: 0, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0, m_gauss: 0 } },
   184	  { label: 'DS+G alpha 0.49 locked (delta kernel)', truth: { shape: 'DSG_LA', laAlpha: 0.49, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0.49, m_gauss: 0 } },
   185	  { label: 'DS+G beta 0.05 locked (delta kernel)',  truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.05, laM: 0, fixLaBeta: true, fixLaM: true }, held: { beta: 0.05, m_gauss: 0 } },
   186	  { label: 'DS+G beta 2 locked (delta kernel)',     truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 2, laM: 0, fixLaBeta: true, fixLaM: true }, held: { beta: 2, m_gauss: 0 } },
   187	  { label: 'LA alpha 0.1 locked (m = 0)', truth: { shape: 'LACX', caAlpha: 0.1, caBeta: 1, caM: 0, fixCaAlpha: true, fixCaM: true }, held: { alpha: 0.1, m: 0 } },
   188	  { label: 'LA alpha 5 locked (m = 0)',   truth: { shape: 'LACX', caAlpha: 5, caBeta: 1, caM: 0, fixCaAlpha: true, fixCaM: true }, held: { alpha: 5, m: 0 } },
   189	  { label: 'LA beta 0.1 locked (m = 0)',  truth: { shape: 'LACX', caAlpha: 1, caBeta: 0.1, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 0.1, m: 0 } },
   190	  { label: 'LA beta 5 locked (m = 0)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 5, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 5, m: 0 } },
   191	];
   192	for (const c of LOCKED_AT_BOUNDS) {
   193	  test(`locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — ${c.label}`, () => {
   194	    const { res, peaks, specs } = roundTrip(c.truth.shape, { truth: c.truth, start: {} });
   195	    const p = peaks[0];
   196	    for (const [name, value] of Object.entries(c.held)) {
   197	      assert.equal(specs[0][name], value, `${c.label}: the request carries ${name} = ${value}`);
   198	      assert.equal(res.individual_peaks[0].params[name].vary, false, `${c.label}: the server held ${name}`);
   199	      assert.equal(res.individual_peaks[0].params[name].value, value, `${c.label}: at the locked value`);
   200	    }
   201	    const rel = maxRelDiff(env.evalPeakArray(res.energy, p), res.individual_peaks[0].y, p.amplitude);
   202	    assert.ok(rel < TIGHT_TOL, `${c.label}: drawn vs fitted curve differ by ${(rel * 100).toExponential(3)} % of amplitude`);
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-oHicmg82' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yZl75hWm' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_r3_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_r3_verdict_runB.md
?? docs/autofit/codex/a03_voigt_eta_recheck2_prompt.txt

 exited 1 in 173637ms:
......E............................................................................EEEEEE....
==================================== ERRORS ====================================
_ ERROR at setup of test_api_fit_differential_evolution_runs_with_page_like_request _

self = PosixPath('/private/tmp/pytest-of-skyefortier'), mode = 448
parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-skyefortier'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError

During handling of the above exception, another exception occurred:

self = PosixPath('/private/tmp/pytest-of-unknown'), mode = 448, parents = False
exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-unknown'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError
_______________ ERROR at setup of test_n_starts_is_validated[-1] _______________

self = PosixPath('/private/tmp/pytest-of-skyefortier'), mode = 448
parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-skyefortier'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError

During handling of the above exception, another exception occurred:

self = PosixPath('/private/tmp/pytest-of-unknown'), mode = 448, parents = False
exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-unknown'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError
_______________ ERROR at setup of test_n_starts_is_validated[11] _______________

self = PosixPath('/private/tmp/pytest-of-skyefortier'), mode = 448
parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-skyefortier'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError

During handling of the above exception, another exception occurred:

self = PosixPath('/private/tmp/pytest-of-unknown'), mode = 448, parents = False
exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-unknown'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError
______________ ERROR at setup of test_n_starts_is_validated[2.5] _______________

self = PosixPath('/private/tmp/pytest-of-skyefortier'), mode = 448
parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-skyefortier'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError

During handling of the above exception, another exception occurred:

self = PosixPath('/private/tmp/pytest-of-unknown'), mode = 448, parents = False
exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-unknown'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError
_______________ ERROR at setup of test_n_starts_is_validated[3] ________________

self = PosixPath('/private/tmp/pytest-of-skyefortier'), mode = 448
parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-skyefortier'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError

During handling of the above exception, another exception occurred:

self = PosixPath('/private/tmp/pytest-of-unknown'), mode = 448, parents = False
exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-unknown'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError
______________ ERROR at setup of test_n_starts_is_validated[True] ______________

self = PosixPath('/private/tmp/pytest-of-skyefortier'), mode = 448
parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-skyefortier'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError

During handling of the above exception, another exception occurred:

self = PosixPath('/private/tmp/pytest-of-unknown'), mode = 448, parents = False
exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-unknown'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError
___________ ERROR at setup of test_the_api_passes_the_check_through ____________

self = PosixPath('/private/tmp/pytest-of-skyefortier'), mode = 448
parents = False, exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-skyefortier'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError

During handling of the above exception, another exception occurred:

self = PosixPath('/private/tmp/pytest-of-unknown'), mode = 448, parents = False
exist_ok = True

    def mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """
        Create a new directory at this given path.
        """
        try:
>           os.mkdir(self, mode)
E           PermissionError: [Errno 1] Operation not permitted: '/private/tmp/pytest-of-unknown'

/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/pathlib.py:1311: PermissionError
=========================== short test summary info ============================
ERROR tests/test_differential_evolution_bounds.py::test_api_fit_differential_evolution_runs_with_page_like_request
ERROR tests/test_scattered_starts.py::test_n_starts_is_validated[-1] - Permis...
ERROR tests/test_scattered_starts.py::test_n_starts_is_validated[11] - Permis...
ERROR tests/test_scattered_starts.py::test_n_starts_is_validated[2.5] - Permi...
ERROR tests/test_scattered_starts.py::test_n_starts_is_validated[3] - Permiss...
ERROR tests/test_scattered_starts.py::test_n_starts_is_validated[True] - Perm...
ERROR tests/test_scattered_starts.py::test_the_api_passes_the_check_through
86 passed, 7 errors in 173.13s (0:02:53)

exec
/bin/zsh -lc 'git diff main..HEAD -- tests/autofit/battery_common.py tests/autofit/test_u4f_parity_battery.py scripts/voigt_eta_measure.py tests/js/lineshape_parity_backend.py scripts/gen_u4f_battery_fixture.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-I8EXK5W0' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4qhTg7CJ' (errno=Operation not permitted)
diff --git a/scripts/gen_u4f_battery_fixture.py b/scripts/gen_u4f_battery_fixture.py
index a3720ce..7e0d6ec 100644
--- a/scripts/gen_u4f_battery_fixture.py
+++ b/scripts/gen_u4f_battery_fixture.py
@@ -36,7 +36,10 @@ def main() -> None:
                     skipped.append({"project": rf.project, "name": rf.name,
                                     "reason": reason})
                 continue
-            records.append(refit_record(rf))
+            rec = refit_record(rf)
+            for pk in rec["peaks"]:
+                pk.pop("params", None)   # the fixture pins numbers, not the full model
+            records.append(rec)
     os.makedirs(os.path.dirname(OUT), exist_ok=True)
     with open(OUT, "w") as f:
         json.dump({"records": records, "skipped": skipped}, f, indent=1, sort_keys=True)
diff --git a/scripts/voigt_eta_measure.py b/scripts/voigt_eta_measure.py
new file mode 100644
index 0000000..f436ee8
--- /dev/null
+++ b/scripts/voigt_eta_measure.py
@@ -0,0 +1,138 @@
+#!/usr/bin/env python3
+"""A03 (2026-09-22): what the free-eta Voigt request did, on the committed targets.
+
+Until A03 the page sent a "Voigt" component as pseudo_voigt_gl with gl_ratio
+FREE from 0.3 while it drew, integrated and exported eta = 0.5. For every
+committed target with a Voigt component this script fits the request BOTH
+ways with the page's settings (Trust-Region, n_perturb 3) — (free) as sent
+before A03, (fixed) eta held at 0.5 as sent since — and compares three
+things per target:
+  A. the 0.5 curve under the free fit's parameters (what the page drew for
+     that fit) against the free fit's own curve — the reporting error that
+     shipped, per component and as area fractions;
+  B. the fixed fit against that 0.5 curve;
+  C. the fixed fit against the free fit.
+All three use the SERVER's curves and trapezoidal integration on the fitted
+grid (non-Voigt components as the server fitted them); they characterise
+the two requests, not a screen. The student-visible change on re-fitting a
+SAVED project — the page's own integration of the saved peaks against the
+page's integration of the refit — is scripts/voigt_saved_vs_refit.js.
+
+Usage:
+  python scripts/voigt_eta_measure.py targets.json out_dir shard n_shards   # one shard
+  python scripts/voigt_eta_measure.py --summary out_dir                     # the numbers
+targets.json is the optimizer-disagreement target file (uncommitted; built by
+scripts/optimizer_disagreement_targets.js from the committed projects with
+the page's CURRENT request builder). Both arms are constructed here
+explicitly from the target's shapes — the target file's own Voigt specs are
+never used as either baseline, so the numbers do not depend on which
+builder produced the file (A03 Codex round 1).
+"""
+import copy
+import glob
+import json
+import os
+import statistics as st
+import sys
+import warnings
+
+import numpy as np
+
+sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
+import fitting  # noqa: E402
+
+warnings.filterwarnings("ignore")
+
+
+def _pack(r):
+    return {"success": r["success"], "chi2r": r["statistics"]["reduced_chi_square"], "energy": r["energy"],
+            "peaks": [{"id": ip["id"], "y": ip["y"], "params": {k: v.get("value") for k, v in ip["params"].items()}}
+                      for ip in r["individual_peaks"]]}
+
+
+def measure(targets_path, out_dir, shard, n_shards):
+    targets = json.load(open(targets_path))
+    os.makedirs(out_dir, exist_ok=True)
+    with open(os.path.join(out_dir, f"shard{shard}.jsonl"), "w") as out:
+        for k, t in enumerate(targets):
+            if k % n_shards != shard:
+                continue
+            vidx = [i for i, sh in enumerate(t["shapes"]) if sh == "Voigt"]
+            if not vidx:
+                continue
+            b = t["background"]
+            kw = dict(background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
+                      endpoint_avg=b["endpoint_avg"], n_perturb=3, fit_kws={"method": "least_squares"})
+            x = np.asarray(t["be"], float)
+            y = np.round(np.asarray(t["inten"], float), 2)   # the upload rounds to 2 dp
+            free = copy.deepcopy(t["specs"])
+            fixed = copy.deepcopy(t["specs"])
+            for i in vidx:
+                free[i]["gl_ratio"] = 0.3                     # the request before A03: eta free from 0.3
+                free[i]["fix_gl_ratio"] = False
+                fixed[i]["gl_ratio"] = 0.5                    # the request since A03: eta held at 0.5
+                fixed[i]["fix_gl_ratio"] = True
+            rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"],
+                   "voigt_ids": [str(t["specs"][i]["id"]) for i in vidx]}
+            for lab, specs in (("free", free), ("fixed", fixed)):
+                try:
+                    rec[lab] = _pack(fitting.run_fit(x, y, specs, **kw))
+                except Exception as e:  # noqa: BLE001 — a failed fit is a row, not a crash
+                    rec[lab] = {"error": str(e)[:160]}
+            out.write(json.dumps(rec) + "\n")
+            out.flush()
+
+
+def summary(out_dir):
+    recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(out_dir, "shard*.jsonl"))) for l in open(f)]
+    ok = [r for r in recs if "peaks" in r["free"] and "peaks" in r["fixed"] and r["free"]["success"] and r["fixed"]["success"]]
+    print(f"targets {len(recs)}, both fits converged {len(ok)}")
+    area = lambda x, y: float(abs(np.trapezoid(y, x)))  # noqa: E731
+    dA, dB, dC, comp = [], [], [], []
+    etas = []
+    chi_ratio = []
+    for r in ok:
+        x = np.asarray(r["free"]["energy"])
+        vids = set(r["voigt_ids"])
+        a_free, a_disp = [], []
+        for pk in r["free"]["peaks"]:
+            a = area(x, np.asarray(pk["y"]))
+            a_free.append(a)
+            if str(pk["id"]) in vids:
+                q = pk["params"]
+                etas.append(q["gl_ratio"])
+                yd = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=q["amplitude"], center=q["center"], fwhm=q["fwhm"], gl_ratio=0.5)
+                ad = area(x, yd)
+                a_disp.append(ad)
+                if a > 0:
+                    comp.append(100 * (ad - a) / a)
+            else:
+                a_disp.append(a)
+        a_fix = [area(x, np.asarray(pk["y"])) for pk in r["fixed"]["peaks"]]
+        frac = lambda A: [100 * v / sum(A) for v in A]  # noqa: E731
+        Ff, Fd, Fx = frac(a_free), frac(a_disp), frac(a_fix)
+        dA.append(max(abs(a - b) for a, b in zip(Fd, Ff)))
+        dB.append(max(abs(a - b) for a, b in zip(Fx, Fd)))
+        dC.append(max(abs(a - b) for a, b in zip(Fx, Ff)))
+        chi_ratio.append(r["fixed"]["chi2r"] / r["free"]["chi2r"])
+
+    def q(v):
+        v = sorted(v)
+        return f"median {st.median(v):.2f}, p90 {v[int(0.9 * len(v))]:.2f}, max {v[-1]:.2f}"
+
+    print(f"free eta of {len(etas)} Voigt components: {sum(e < 0.01 for e in etas)} at 0 (pure Gaussian), "
+          f"{sum(e > 0.99 for e in etas)} at 1 (pure Lorentzian), {sum(0.4 <= e <= 0.6 for e in etas)} within 0.4–0.6")
+    e = [abs(c) for c in comp]
+    print(f"per-Voigt-component DISPLAYED area vs the fitted curve (%): {q(e)}; > 10 % on {sum(v > 10 for v in e)} of {len(e)}; "
+          f"displayed high (eta < 0.5) {sum(c > 0 for c in comp)}, low {sum(c < 0 for c in comp)}")
+    print(f"A. displayed vs free-fit fractions, max |delta| pp per target: {q(dA)}; > 1 pp on {sum(v > 1 for v in dA)} targets")
+    print(f"B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: {q(dB)}; > 1 pp on {sum(v > 1 for v in dB)} targets")
+    print(f"C. fixed refit vs free fit, max |delta| pp: {q(dC)}; > 1 pp on {sum(v > 1 for v in dC)} targets")
+    print(f"chi2r fixed/free: {q(chi_ratio)}; fixed lower on {sum(v < 1 for v in chi_ratio)} targets (the free fit in a worse minimum)")
+
+
+if __name__ == "__main__":
+    if sys.argv[1] == "--summary":
+        summary(sys.argv[2])
+    else:
+        measure(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
diff --git a/tests/autofit/battery_common.py b/tests/autofit/battery_common.py
index 4c994a7..ceee984 100644
--- a/tests/autofit/battery_common.py
+++ b/tests/autofit/battery_common.py
@@ -78,24 +78,39 @@ def assert_refit_stability_and_fixture(
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
diff --git a/tests/autofit/test_u4f_parity_battery.py b/tests/autofit/test_u4f_parity_battery.py
index fd2f2d2..e18df2a 100644
--- a/tests/autofit/test_u4f_parity_battery.py
+++ b/tests/autofit/test_u4f_parity_battery.py
@@ -6,6 +6,16 @@ battery_common.py).
 
 Regenerate the fixture ONLY for reviewed numerics changes:
     venv/bin/python scripts/gen_u4f_battery_fixture.py
+
+A03 (2026-09-22): the page now sends a Voigt with eta HELD at 0.5 (the mix
+it has always drawn); the 29 expert U 4f fits were saved under the old
+request (eta free from 0.3, ending at pure Gaussian or pure Lorentzian on
+most satellites), so their saved parameters belong to another model and a
+refit under today's request moves the LACX main line's width by up to 7.7 %
+and its centre by up to 8 meV (the satellites' tails changed). The fixture
+was regenerated for that reviewed change, and stationarity is measured
+against a refit FROM the refit (battery_common, stationarity="refit"): the
+fitter's own fixed point, not the pre-A03 save.
 """
 
 import pytest
@@ -48,4 +58,5 @@ def test_eval_parity(rf):
 @pytest.mark.parametrize("rf", _FITS, ids=_IDS)
 def test_refit_stability_and_fixture(rf):
     bc.assert_refit_stability_and_fixture(rf, _EXPECTED,
-                                          fixture_rtol=FIXTURE_RTOL)
+                                          fixture_rtol=FIXTURE_RTOL,
+                                          stationarity="refit")
diff --git a/tests/js/lineshape_parity_backend.py b/tests/js/lineshape_parity_backend.py
index 2473772..17861eb 100644
--- a/tests/js/lineshape_parity_backend.py
+++ b/tests/js/lineshape_parity_backend.py
@@ -3,7 +3,8 @@
 
 Reads a JSON spec from stdin:
     {"shape": "<key in fitting._SHAPE_FUNCS>", "params": {...}, "x": [...]}
-Writes a JSON array of y-values to stdout.
+or a JSON list of such specs.
+Writes a JSON array of y-values (or a list of arrays) to stdout.
 
 Calls fitting.py's OWN registered shape functions (_SHAPE_FUNCS) directly —
 never a reimplementation — so the JS parity test is always comparing against
@@ -19,12 +20,20 @@ sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspa
 from fitting import _SHAPE_FUNCS  # noqa: E402
 
 
-def main() -> None:
-    spec = json.load(sys.stdin)
+def _eval(spec: dict) -> list[float]:
     x = np.array(spec["x"], dtype=float)
     fn = _SHAPE_FUNCS[spec["shape"]]
-    y = fn(x, **spec["params"])
-    json.dump([float(v) for v in y], sys.stdout)
+    return [float(v) for v in fn(x, **spec["params"])]
+
+
+def main() -> None:
+    spec = json.load(sys.stdin)
+    # A list of specs (the A03 parameter sweep) is answered with a list of
+    # curves in one interpreter start; a single spec as before.
+    if isinstance(spec, list):
+        json.dump([_eval(s) for s in spec], sys.stdout)
+    else:
+        json.dump(_eval(spec), sys.stdout)
 
 
 if __name__ == "__main__":

exec
/bin/zsh -lc "nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | sed -n '145,173p'; nl -ba templates/index.html | sed -n '7727,7737p'; nl -ba scripts/local_server_gap.js | sed -n '76,82p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
   145	
   146	| target | local χ²ᵣ | server χ²ᵣ, m free | server χ²ᵣ, m held | local vs server, m free (Δcentre / ΔFWHM / Δarea / Δfrac) | local vs server, m held | local χ²ᵣ above the held-m server's |
   147	|---|---:|---:|---:|---|---|---:|
   148	| Scan_4 | 1.970 | 1.798 | 1.870 | 26.6 meV / 5.3 % / 8.3 % / 0.33 pp | 13.4 meV / 3.1 % / 5.3 % / 0.19 pp | +5.4 % |
   149	| Scan_5 | 2.393 | 2.174 | 2.182 | 4.7 meV / 4.3 % / 6.7 % / 0.35 pp | 6.3 meV / 3.5 % / 5.5 % / 0.25 pp | +9.7 % |
   150	| Scan_6 | 2.657 | 2.798 | 2.629 | 28.8 meV / 15.8 % / 8.9 % / 0.77 pp | 3.6 meV / 1.1 % / 1.6 % / 0.07 pp | +1.1 % |
   151	| Scan_8 | 4.656 | 4.129 | 4.117 | 5.7 meV / 5.0 % / 8.3 % / 0.32 pp | 5.8 meV / 5.0 % / 8.2 % / 0.32 pp | +13.1 % |
   152	
   153	(The 5 agreeing targets are within 1.6 % of the held-m server's χ²ᵣ and
   154	within 4.0 meV / 1.5 % / 2.1 % / 0.12 pp of it.) So: on Scan_6 the residual
   155	IS the `caM` clamp (holding m on the server closes it to the
   156	agreeing-target envelope). On Scan_5 and Scan_8 holding m changes nothing —
   157	the local engine's descent stops at a χ²ᵣ 10–13 % above the server's from
   158	the same start with the same free parameters: a worse minimum, the
   159	"several minima" case (findings §2 had the mirror image on C 1s Scan_4,
   160	where the local engine found the better one). Scan_4 is in between
   161	(+5.4 %). The residual is therefore two things, and `caM` is the smaller.
   162	
   163	**Decision: the "starting point" designation STAYS**, on two grounds now:
   164	the `caM` clamp (one target) and the local engine landing in a worse
   165	minimum than Trust-Region on three of nine U 4f targets. The `caM` clamp
   166	remains the next unit; the worse-minimum finding is recorded in findings
   167	§7 for the local-engine work that follows it. Wording in the page updated
   168	to say so (LA components and several minima; no longer Voigt).
   169	
   170	## 7. Release-note line
   171	
   172	Voigt components are now fitted at the fixed 50/50 mix the page has always
   173	drawn; until now Run Fit let their mix vary on the server and the page
  7727	    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  7728	    const stats = backendResult.statistics || {};
  7729	    const chiReduced = stats.reduced_chi_square || 0;
  7730	    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
  7731	    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  7732	    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
  7733	                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
  7734	                        fittedY: backendResult.fitted_y, roiRange, _preFit,
  7735	                        starts: backendResult.starts || null,
  7736	                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
  7737	                        chosenAlternative: opts.chosenAlternative || null };
    76	      r.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(peaks[i], par); });
    77	      return { r, peaks };
    78	    };
    79	    const { r: srv, peaks: serverPeaks } = serverFit(T.start);
    80	    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, caM: Math.round(p.caM || 0), fixCaM: true } : p);
    81	    const { r: srvHeld, peaks: serverHeldPeaks } = serverFit(heldStart);
    82	    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)

codex
No BLOCKER found. Three findings remain:

1. **MAJOR — measurement still does not reproduce the page’s grid semantics.** [scripts/voigt_saved_vs_refit.js:43](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:43) rounds the only ROI grid, using it for refit integration, the saved-grid fallback, and background-window selection through the bridge. The page selects background indices **before rounding** and retains unrounded `be` in `fitResult` at `templates/index.html:7733`.

   Concrete reproduction: 241 energies `397.800049 − 0.05003*i`, background upper bound `397.80004`. The page excludes point 0; the script includes it after rounding. With a large excluded endpoint and a Voigt peak, both fits converged, but fitted amplitude was **12,042.6 versus approximately zero**, with different seeds. Independently, integration of identical Voigt parameters differed by **0.060%** between those grids.

   Preserve separate display and upload arrays; compute background indices on the display array. **The existing 55 tabs have only floating-point-scale grid differences**, so this finding does not overturn their reported 0.36/0.69 pp summary.

2. **MINOR — “every shape parameter at each bound” remains incomplete.** [tests/js/lineshape_roundtrip.test.js:172](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:172) omits locked DS+G `m_gauss = 0.05, 4` and LA `m = 499`. The two TODO round trips leave these parameters free; they do not test their locks. A regression dropping either lock at those endpoints can escape the claimed coverage. Request-value and server-held-value assertions can run independently of the deferred curve assertions.

3. **MINOR — numerical/documentation cleanup is not complete.** [tests/js/lineshape_roundtrip.test.js:9](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:9) still says “12 %” immediately before “median (13.9 %).” The [plan:103](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:103) still reports 10 passing round-trip tests; there are 29. Its line 149 reports Scan_5’s area difference as 6.7%; the artifact’s 6.6485825% rounds to **6.6%**.

Round-2 closure: **item 1 partial; item 2 closed; items 3 and 4 partial.** The rounded control arm and its +5.4/+9.7/+1.1/+13.1% figures check out.

No additional `_set` regression was established. Probes preserved held negative amplitude, out-of-window centre and zero DS+G smoothing through the relevant parameter-copy paths; fresh unlocked requests restored their original bounds.

Validation: **29 JS passes, 2 documented TODOs; 86 Python passes**, including all six Voigt contract tests. Seven API test setups were blocked by the read-only sandbox’s temporary-directory restriction. No files changed.

**VERDICT: NO-GO**
tokens used
106,511
No BLOCKER found. Three findings remain:

1. **MAJOR — measurement still does not reproduce the page’s grid semantics.** [scripts/voigt_saved_vs_refit.js:43](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:43) rounds the only ROI grid, using it for refit integration, the saved-grid fallback, and background-window selection through the bridge. The page selects background indices **before rounding** and retains unrounded `be` in `fitResult` at `templates/index.html:7733`.

   Concrete reproduction: 241 energies `397.800049 − 0.05003*i`, background upper bound `397.80004`. The page excludes point 0; the script includes it after rounding. With a large excluded endpoint and a Voigt peak, both fits converged, but fitted amplitude was **12,042.6 versus approximately zero**, with different seeds. Independently, integration of identical Voigt parameters differed by **0.060%** between those grids.

   Preserve separate display and upload arrays; compute background indices on the display array. **The existing 55 tabs have only floating-point-scale grid differences**, so this finding does not overturn their reported 0.36/0.69 pp summary.

2. **MINOR — “every shape parameter at each bound” remains incomplete.** [tests/js/lineshape_roundtrip.test.js:172](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:172) omits locked DS+G `m_gauss = 0.05, 4` and LA `m = 499`. The two TODO round trips leave these parameters free; they do not test their locks. A regression dropping either lock at those endpoints can escape the claimed coverage. Request-value and server-held-value assertions can run independently of the deferred curve assertions.

3. **MINOR — numerical/documentation cleanup is not complete.** [tests/js/lineshape_roundtrip.test.js:9](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:9) still says “12 %” immediately before “median (13.9 %).” The [plan:103](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:103) still reports 10 passing round-trip tests; there are 29. Its line 149 reports Scan_5’s area difference as 6.7%; the artifact’s 6.6485825% rounds to **6.6%**.

Round-2 closure: **item 1 partial; item 2 closed; items 3 and 4 partial.** The rounded control arm and its +5.4/+9.7/+1.1/+13.1% figures check out.

No additional `_set` regression was established. Probes preserved held negative amplitude, out-of-window centre and zero DS+G smoothing through the relevant parameter-copy paths; fresh unlocked requests restored their original bounds.

Validation: **29 JS passes, 2 documented TODOs; 86 Python passes**, including all six Voigt contract tests. Seven API test setups were blocked by the read-only sandbox’s temporary-directory restriction. No files changed.

**VERDICT: NO-GO**
