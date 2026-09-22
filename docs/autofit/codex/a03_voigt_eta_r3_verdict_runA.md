OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0c7ce-b207-78b0-b2e0-9fbba7c211cd
--------
user
RECHECK, round 3, of unit A03: branch fix-voigt-eta-identity, git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round 2 (docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md / runB.md, both NO-GO) confirmed round-1 items 1, 3, 4 closed and found: (1) MAJOR scripts/voigt_saved_vs_refit.js integrated the saved side on the current ROI grid where Results uses fitResult.be, and sent the refit request without the page's upload rounding (4 dp energies, 2 dp intensities; the rounding also sets the seed); (2) MINOR the control arm in scripts/local_server_gap.js held LA m at the stored fractional value where the local engine rounds it; (3) MINOR "every shape parameter locked at its bounds" was seven cases; (4) MINOR numbers ("10-13 %", "12 %", stale test counts).

What changed since (plan §9 round 2; commit "fix(A03): Codex round 2"): the saved side integrates on fitResult.be (fallback ROI exactly as Results), the request is rounded as uploadToBackend rounds; re-run (docs/findings/a03/voigt_saved_vs_refit.json: median 0.36 pp, max 0.69 pp, none > 1 pp). The control arm holds m at Math.round(caM); re-run (docs/findings/a03/local_server_gap.json; plan §6 table: local chi2r above the held-m server's +5.4 / +9.7 / +1.1 / +13.1 % on Scan_4/5/6/8). tests/js/lineshape_roundtrip.test.js now locks every shape parameter of every shape at each of its bounds (18 cases; the convolved shapes where their evaluators are exact: DS+G with m < 0.001, LA with m = 0), asserting the request value, the server's vary:false at that value, and drawn == fitted. Doing so found a FOURTH identity defect: lmfit clips a held value to its bounds, so a DS+G with m locked at 0 was fitted with m = 0.05 (the free-parameter floor) - fitting._make_peak_params._set now widens a limit to a held value (vary False, no expr), pinned in tests/test_voigt_contract.py. Numbers corrected throughout.

Verify each round-2 item is closed, then try to break: the _set change (any request where clipping a fixed value into bounds was RELIED on - a fixed amplitude below amplitude_min 0, a fixed centre outside the +/-2 eV window, DE's _finite_search_box with a fixed parameter outside its former bounds, the seed's effective-role hash, the scattered-starts clamp, _component_required's retained parameters created from result.params values/min/max; does widening a bound for a HELD parameter leak into any later refit that FREES it?); the 18 locked cases (do they exercise the LOCKED path on the server and the page's drawn curve? any bound omitted that a lock can reach?); voigt_saved_vs_refit.js (saved grid selection vs Results' exact rule at templates/index.html renderResults; the rounding; is the refit side's grid the one the page would hold after Run Fit?); the control arm; docs vs artifacts (every number in the plan §2b/§6/§7/§9, findings §7, CLAUDE.md, the two code comments and the JS test header must match docs/findings/a03/*.json and voigt_eta_summary.txt).

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check the round-2 fixes against the code and artifacts, then probe the held-parameter bounds change and curve identity tests. I’ll keep this read-only and finish with a ranked verdict.

exec
/bin/zsh -lc "pwd; git status --short; git diff --stat main..HEAD; rg --files -g 'AGENTS.md' -g '*a03*' -g '*voigt*' -g '*local_server_gap*' -g '*lineshape_roundtrip*' -g 'CLAUDE.md'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
exec
/bin/zsh -lc 'git diff main..HEAD -- fitting.py templates/index.html autofit/parity.py autofit/reference.py tests/test_voigt_contract.py; cat scripts/voigt_saved_vs_refit.js scripts/local_server_gap.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DtORMKhn' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-l6RegGmk' (errno=Operation not permitted)
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

exec
/bin/zsh -lc 'cat tests/js/lineshape_roundtrip.test.js tests/js/lineshape_roundtrip_backend.py; cat docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md; cat docs/findings/a03/voigt_eta_summary.txt' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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

exec
/bin/zsh -lc "cat scripts/voigt_saved_vs_refit.js scripts/local_server_gap.js; sed -n '1,220p' tests/js/lineshape_roundtrip.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
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

exec
/bin/zsh -lc "rg -n '_finite_search_box|_component_required|def _make_peak_params|def _seed|scatter|amplitude_min|center_min' fitting.py; sed -n '750,1040p' fitting.py; rg -n 'function renderResults|fitResult.be|function uploadToBackend|toFixed\\(4\\)|data.energy|res.energy' templates/index.html; cat tests/test_voigt_contract.py; ls -d .venv venv /Users/skyefortier/xps-app/.venv 2>/dev/null; rg --files /Users/skyefortier -g AGENTS.md -g '"'!Library/**'"' -g '"'!node_modules/**'"' -g '"'!docs/**'"' 2>/dev/null | head -40" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 7617ms:
exec
/bin/zsh -lc "sed -n '65,215p' tests/js/lineshape_roundtrip.test.js; sed -n '6180,6228p' templates/index.html; sed -n '8375,8420p' templates/index.html; rg -n '_component_required|_request_seed|_finite_search_box|clip|vary = True|vary=True' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
}

// ═══════════════════════════════════════════════════
// ═══════════════════════════════════════════════════
// FLASK BACKEND HELPERS
// ═══════════════════════════════════════════════════
async function uploadToBackend(be, inten) {
  const csv = be.map((e, i) => e.toFixed(4) + ',' + inten[i].toFixed(2)).join('\n');
  const form = new FormData();
  form.append('file', new Blob([csv], { type: 'text/plain' }), 'spectrum.csv');
  const resp = await fetch('/api/upload', { method: 'POST', body: form });
  // A server-side failure (HTTP error, error body, or no session id) is not a
  // transport failure: runFit must report it, never switch engines (unit A0).
  const serverError = (msg) => { const err = new Error(msg); err.serverError = true; return err; };
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
      ${backendResult ? `<div style="flex:1;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:8px 10px">
        <div style="font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px">Engine</div>
        <div style="font-family:var(--mono);font-size:11px;color:var(--green)">lmfit</div>
      </div>` : ''}
    </div>
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
    </tr>`;
      return;
    }
    html += `<tr>
      <td><span style="display:inline-block;width:8px;height:8px;border-radius:2px;background:${p.color};margin-right:5px"></span>${_escHtml(p.name)}</td>
69:    eta = float(np.clip(gl_ratio, 0.0, 1.0))
93:    asym = float(np.clip(asymmetry, 0.0, 1.0))
126:    alpha      = float(np.clip(alpha, 0.0, 0.995))
188:    alpha   = float(np.clip(alpha, 0.0, 0.495))
846:    def _set(name, value, min_=None, max_=None, expr=None, vary=True):
852:            # the optimiser's search limits; lmfit clips a value outside them
969:def _finite_search_box(params: Parameters, x: np.ndarray,
1051:    generated = _finite_search_box(boxed, x, y_sub)
1135:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1376:def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
1627:        random_seed = _request_seed(
1788:                    required = {"ran": True, **_component_required(

codex
The saved-grid selection and held-m control have been corrected. The 18 new cases also assert `vary:false` and compare the page evaluator with the server curve. I found a stale “12%” in the test header; I’m now checking whether widened bounds survive into a later fit and whether the measurement uses the grid Results actually receives.

exec
/bin/zsh -lc "sed -n '1035,1195p' fitting.py; sed -n '1376,1435p' fitting.py; sed -n '1530,1730p' fitting.py; cat tests/js/local_lm_server_parity_backend.py; rg -n 'be:|energy|uploadToBackend|_applyBackendParams' templates/index.html | awk '"'$1+0 >= 6300 && $1+0 <= 6850'"'; sed -n '5900,6135p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart":
        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart_exp":
        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "shirley_linear":
        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "tougaard":
        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
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
        raise ValueError(f"Unknown background method '{background_method}'")

    if bg_inner is not None:
        # Embed the anchor-window integral background into a full-ROI
        # array; flat-hold the endpoint value outside [i0, i1]. In the
        # common case where the user keeps bg anchors at the ROI edges
        # this is a no-op (i0=0, i1=len(y)).
        bg = np.zeros_like(y)
        if len(bg_inner) > 0:
            bg[i0:i1] = bg_inner
            if i0 > 0:
                bg[:i0] = bg_inner[0]
            if i1 < len(y):
                bg[i1:] = bg_inner[-1]

    y_sub = y - bg

    # Poisson weights: σ = √(raw counts), weight = 1/σ
    # Use raw counts (before background subtraction) for uncertainty estimate,
    # since the noise comes from the total photon counting statistics.
    # Floor at 1.0 to avoid division by zero for zero-count channels.
    sigma = np.sqrt(np.maximum(y, 1.0))
    weights = 1.0 / sigma

    # ── Build composite lmfit model ───────────────────────────────────────────
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
6319:    _applyBackendParams(p, ipeak.params);
6542:      strong.push({ be: rawBE[i], intensity: bgSubInten[i] });
    for (const p of state.peaks) { const a = _peakArea(p, _roiBE); _peakAreas[p.id] = a; if (!_isUnsupported(p)) totalArea += a; }
  }

  for (const p of state.peaks) {
    const item = document.createElement('div');
    item.className = 'peak-item';
    item.id = 'peak-item-' + p.id;
    item.style.borderLeftColor = p.color;
    const isLinked = !!p.linked;
    const pArea = _peakAreas[p.id] || 0;
    const unsupported = _isUnsupported(p);
    const areaPct = unsupported ? '\u2014' : (totalArea > 0 && pArea > 0 ? ((pArea / totalArea) * 100).toFixed(1) : '\u2014');
    const dash = '\u2014';

    item.innerHTML = `
      <div class="peak-header" onclick="togglePeakBody(${p.id})">
        <div class="peak-color" style="background:${p.color}"></div>
        <span class="peak-name">${_escHtml(p.name)}${isLinked ? ' <span class="linked-badge">linked</span>' : ''}${p.isChargeReference ? ' <span class="chargeref-badge" title="Charge-correction reference (C 1s graphite 284.5 eV)">C-ref</span>' : ''}${unsupported ? ' ' + _unsupportedBadge(p.id) : ''}</span>
        <span class="peak-info">${unsupported ? dash : p.center.toFixed(2) + ' eV'}</span>
        <button class="btn btn-icon btn-sm" style="margin-left:4px;color:var(--red)" onclick="event.stopPropagation();removePeak(${p.id})">&times;</button>
      </div>
      <div class="peak-summary" onclick="togglePeakBody(${p.id})">
        <span class="peak-summary-label">Center</span>
        <span class="peak-summary-label">FWHM</span>
        <span class="peak-summary-label">Area</span>
        <span class="peak-summary-val">${unsupported ? dash : p.center.toFixed(2)}</span>
        <span class="peak-summary-val">${unsupported ? dash : p.fwhm.toFixed(2)}</span>
        <span class="peak-summary-val">${areaPct === '\u2014' ? areaPct : areaPct + '%'}</span>
      </div>
      <div class="peak-body" id="peak-body-${p.id}">
        ${renderPeakForm(p)}
      </div>
    `;
    el.appendChild(item);
    if (expandedIds.has(p.id)) document.getElementById('peak-body-' + p.id).classList.add('open');
    item.addEventListener('mouseenter', () => _highlightChartPeak(p.id, true));
    item.addEventListener('mouseleave', () => _highlightChartPeak(p.id, false));
  }
}

function renderPeakForm(p) {
  const isLinked = !!p.linked;
  const showChargeRef = _isChargeRefAllowed();
  return `
    <div class="field">
      <label>Name</label>
      <input type="text" value="${_escAttr(p.name)}" oninput="updatePeakParam(${p.id},'name',this.value);document.querySelector('#peak-item-${p.id} .peak-name').childNodes[0].textContent=this.value">
    </div>
    ${showChargeRef ? `
    <div class="field" style="display:flex;align-items:center;gap:6px;margin-top:2px">
      <input type="checkbox" id="pk-cref-${p.id}"
             ${p.isChargeReference ? 'checked' : ''}
             onchange="toggleChargeReference(${p.id})"
             style="margin:0">
      <label for="pk-cref-${p.id}"
             style="margin:0;font-size:11px;cursor:pointer;user-select:none"
             title="Mark this peak as the charge-correction reference (typically C 1s graphite at 284.5 eV). Only one peak per fit can hold this marker.">
        Charge-correction reference (C&nbsp;1s graphite)
      </label>
    </div>` : ''}
    <div class="field">
      <label>Line shape</label>
      <select id="pk-shape-${p.id}" class="xps-tip-select" onchange="_switchPeakShape(${p.id}, this.value)">
        <option data-tip="Pure Gaussian. Dominated by instrument broadening. Rarely used alone — most XPS peaks need some Lorentzian character." ${p.shape==='Gaussian'?'selected':''}>Gaussian</option>
        <option data-tip="Pure Lorentzian. Dominated by core-hole lifetime. Rarely used alone — too sharp for most real XPS peaks." ${p.shape==='Lorentzian'?'selected':''}>Lorentzian</option>
        <option data-tip="Fixed 50/50 Gaussian-Lorentzian mix (η = 0.5, not fitted). A reasonable default for most insulating and polymeric samples; choose GL to fit the mix." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
        <option value="GL" data-tip="Adjustable Gaussian/Lorentzian ratio. Use when you need control over the peak shape — common for oxides, polymers, and organic materials." ${p.shape==='GL'?'selected':''}>GL pseudo-Voigt (&eta; mixing)</option>
        <option value="asym-GL" data-tip="GL with asymmetric broadening. Use for peaks with vibrational fine structure (e.g., C 1s in polymers) or when one side is broader than the other." ${p.shape==='asym-GL'?'selected':''}>Asymmetric GL</option>
        <option value="DS" data-tip="Asymmetric metallic lineshape with tail toward higher BE. Use for metals and conductive samples (e.g., Au, Cu, Fe metal). Not appropriate for insulators or oxides." ${p.shape==='DS'?'selected':''}>Doniach-&Scaron;unji&#263; (&alpha; + &gamma;)</option>
        <option value="DSG_LA" data-tip="Doniach-Šunjić core convolved with a Gaussian. A defensible asymmetric shape — good for metals and transition metals with complex screening. Previously this entry was mis-labeled as 'LA [CasaXPS]'. The genuine CasaXPS LA(α,β,m) lives in the new entry below." ${p.shape==='DSG_LA'?'selected':''}>DS+G</option>
        <option value="LACX" data-tip="True CasaXPS LA(α,β,m). Asymmetric Lorentzian raised to exponents α (high-BE tail side) and β (low-BE side), convolved with a Gaussian of integer point width m. Reduces to a pure Lorentzian at α=β=1, m=0. Match to CasaXPS by using the same α, β, m values." ${p.shape==='LACX'?'selected':''}>LA(&alpha;,&beta;,m) [CasaXPS]</option>
      </select>
    </div>
    <div id="shape-controls-${p.id}">
      ${renderShapeControls(p)}
    </div>
    <div class="field-row">
      <div class="field">
        <label data-xps-tip="Peak position in binding energy. After charge correction, this should match the expected literature value for the chemical state being modeled.">Center (eV)${isLinked ? ' <em style="color:var(--purple);font-size:9px">auto</em>' : ''}
          ${!isLinked ? '<button class="lock-btn' + (p.fixCenter ? ' locked' : '') + '" onclick="event.stopPropagation();toggleLock(' + p.id + ',\'fixCenter\',this)" title="' + (p.fixCenter ? 'Unlock' : 'Lock') + ' during fitting">' + (p.fixCenter ? '&#x1f512;' : '&#x1f513;') + '</button>' : ''}
        </label>
        <input type="number" id="pk-center-${p.id}" value="${p.center.toFixed(3)}" step="0.05"
          ${isLinked ? 'readonly style="opacity:0.5"' : ''}
          oninput="updatePeakParam(${p.id},'center',parseFloat(this.value));_patchPeakCardsForSupport()">
      </div>
      <div class="field" id="fwhm-field-${p.id}" ${p.shape === 'DSG_LA' ? 'style="opacity:0.4"' : ''}>
        <label data-xps-tip="${p.shape === 'DS' ? 'Lorentzian half-width parameter (γ = width/2). When α > 0, the measured FWHM of the peak is broader than this input value because of the asymmetric tail.' : 'Full width at half maximum. Typical XPS peak widths range from 0.5 to 3.0 eV depending on the element, chemical state, and spectrometer resolution. Peaks from the same chemical environment should have similar FWHM values.'}">${p.shape === 'DS' ? 'Width parameter γ (eV)' : 'FWHM (eV)'}${p.shape === 'DSG_LA' ? ' <em style="color:var(--amber);font-size:9px">set by \\u03b2, m</em>' : ''}
          ${!isLinked && p.shape !== 'DSG_LA' ? '<button class="lock-btn' + (p.fixFwhm ? ' locked' : '') + '" onclick="event.stopPropagation();toggleLock(' + p.id + ',\'fixFwhm\',this)" title="' + (p.fixFwhm ? 'Unlock' : 'Lock') + ' during fitting">' + (p.fixFwhm ? '&#x1f512;' : '&#x1f513;') + '</button>' : ''}
        </label>
        <input type="number" id="pk-fwhm-${p.id}" value="${p.fwhm.toFixed(3)}" step="0.05" min="0.1"
          ${p.shape === 'DSG_LA' ? 'readonly ' : ''}oninput="updatePeakParam(${p.id},'fwhm',parseFloat(this.value))">
      </div>
    </div>
    <div class="field">
      <label data-xps-tip="Peak height in counts. Proportional to the concentration of the chemical state, modified by the relative sensitivity factor (RSF) and spectrometer transmission function.">Amplitude
        ${!isLinked ? '<button class="lock-btn' + (p.fixAmplitude ? ' locked' : '') + '" onclick="event.stopPropagation();toggleLock(' + p.id + ',\'fixAmplitude\',this)" title="' + (p.fixAmplitude ? 'Unlock' : 'Lock') + ' during fitting">' + (p.fixAmplitude ? '&#x1f512;' : '&#x1f513;') + '</button>' : ''}
      </label>
      <input type="number" id="pk-amp-${p.id}" value="${p.amplitude.toFixed(0)}" step="100"
        ${isLinked ? 'readonly style="opacity:0.5"' : ''}
        oninput="updatePeakParam(${p.id},'amplitude',parseFloat(this.value))">
    </div>
    ${isLinked ? `
    <div class="divider"></div>
    <div style="font-size:10px;color:var(--purple);margin-bottom:6px;display:flex;justify-content:space-between;align-items:center">
      <span>Multiplet constraints</span>
      <button class="btn btn-sm" style="font-size:10px;padding:1px 7px;color:var(--amber);border-color:var(--amber)" onclick="unlinkPeak(${p.id})">Unlink</button>
    </div>
    <div class="field-row">
      <div class="field">
        <label>Offset (eV)</label>
        <input type="number" value="${p.linkOffset.toFixed(2)}" step="0.05"
          oninput="getPeak(${p.id}).linkOffset=parseFloat(this.value);getPeak(${p.id}).center=getPeak(${p.linked}).center+parseFloat(this.value);updatePeakParam(${p.id},'center',getPeak(${p.id}).center)">
      </div>
      <div class="field">
        <label>Ratio (I&#8322;/I&#8321;)</label>
        <input type="number" value="${p.linkRatio.toFixed(3)}" step="0.05" min="0.01" max="2"
          oninput="_onLinkRatioInput(${p.id}, this.value)">
      </div>
    </div>
    ` : ''}
  `;
}

function renderShapeControls(p) {
  const isLinked = !!p.linked;
  if (p.shape === 'asym-GL') {
    return `
      <div class="asym-field">
        <label data-xps-tip="Empirical asymmetry parameter that broadens the high-BE side of the peak: fwhm_right = fwhm × (1 + asymmetry). This is NOT the same as the Doniach-Šunjić singularity index α from metallic-screening literature — it's an empirical width-broadening factor specific to this app's asymmetric pseudo-Voigt formulation.">Asymmetry factor <span style="color:var(--text3);font-size:9px">0=symmetric &middot; empirical broadening factor, not DS &alpha;</span>
          ${!isLinked ? `<button class="lock-btn${p.fixAsymmetry ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixAsymmetry',this)" title="${p.fixAsymmetry ? 'Unlock' : 'Lock'} during fitting">${p.fixAsymmetry ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
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
  }
  return '';
}

function renderPeakControls(p) {

exec
/bin/zsh -lc "rg -n 'be:|energy|uploadToBackend|_applyBackendParams' templates/index.html | awk '"'$1+0 >= 6300 && $1+0 <= 6850'"'; cat tests/js/local_lm_server_parity_backend.py; rg -n 'function updatePeakParam|laAlpha|dsAlpha' templates/index.html | head -35; rg -n 'A03|13.9|12 %|10–13|10-13|5–13|29 pass|10 pass|18|0.36|0.69' CLAUDE.md docs/findings/2026-09-fit-determinacy.md; ls /Users/skyefortier/xps-app/venv/bin/python3; for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if test -f \""'$p"; then cat "$p"; fi; done' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
6319:    _applyBackendParams(p, ipeak.params);
6542:      strong.push({ be: rawBE[i], intensity: bgSubInten[i] });
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
4159:    y = doniachSunjic(x, center, fwhm, p.dsAlpha, p.dsGamma);
4160:    const yMax = doniachSunjic(center, center, fwhm, p.dsAlpha, 0.001);
4166:    y = laCasaXPS(x, center, p.laAlpha, p.laBeta, p.laM);
4237:    const yArr = dsgDeltaKernel_array(beArr, p.center, p.laAlpha, p.laBeta);
5031:    dsAlpha: 0.10,
5033:    laAlpha: 0.10,
5081:// Do NOT cross-map look-alike params across shapes (e.g. DSG_LA's laAlpha vs
5090:  'DS':         { dsAlpha: 0.10, fixDsAlpha: false, dsGamma: 0.0, fixDsGamma: false },
5091:  'DSG_LA':     { laAlpha: 0.10, fixLaAlpha: false, laBeta: 0.3, fixLaBeta: false, laM: 0.4, fixLaM: false },
5755:function updatePeakParam(id, key, value) {
5765:  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
6062:        <input type="number" value="${p.dsAlpha.toFixed(3)}" step="0.005" min="0" max="0.5"
6063:          oninput="updatePeakParam(${p.id},'dsAlpha',parseFloat(this.value))">
6083:          <input type="number" value="${p.laAlpha.toFixed(3)}" step="0.005" min="0" max="0.5"
6084:            oninput="updatePeakParam(${p.id},'laAlpha',parseFloat(this.value))">
6256:    spec.alpha      = Number.isFinite(p.dsAlpha) ? p.dsAlpha : 0.1;
6262:    spec.alpha   = Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10;
6303:  if (par.alpha && p.shape === 'DS' && !p.fixDsAlpha) p.dsAlpha = par.alpha.value;
6305:  if (par.alpha   && p.shape === 'DSG_LA' && !p.fixLaAlpha) p.laAlpha = par.alpha.value;
7374:const _STARTS_MODEL_FIELDS = ['id', 'shape', 'center', 'fwhm', 'amplitude', 'glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
7375:  'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM', 'linked', 'linkOffset', 'linkRatio', '_afAsymMin', '_afAsymMax',
7962:        freeParams.push(p.dsAlpha); paramMap.push({id: p.id, param: 'dsAlpha'});
7968:        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
7991:    if (param === 'dsAlpha')      return Math.max(0, Math.min(0.49, v));
7993:    if (param === 'laAlpha')      return Math.max(0, Math.min(0.49, v));
8001:  const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
8002:    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];
11070:// `p.dsAlpha ?? p.laAlpha ?? p.caAlpha` fallback chains, which picked the
11076:    case 'DS':      return { gl: '',            alpha: p.dsAlpha ?? '', beta: '',  m: '' };
11077:    case 'DSG_LA':  return { gl: '',            alpha: p.laAlpha ?? '', beta: p.laBeta ?? '', m: p.laM ?? '' };
15681:      o.dsAlpha = p.alpha ?? 0.1; o.dsGamma = p.gamma_asym ?? 0; break;
15683:      o.laAlpha = p.alpha ?? 0.1; o.laBeta = p.beta ?? 0.3; o.laM = p.m_gauss ?? p.fwhm ?? 1; break;
docs/findings/2026-09-fit-determinacy.md:29:## 2. Two optimisers, one model, two decompositions — and the server was the one in a local minimum (unit W1, 2026-09-18)
docs/findings/2026-09-fit-determinacy.md:39:| local engine (weighted LM), from the batch start | 18.218 | 4.5 | converged |
docs/findings/2026-09-fit-determinacy.md:40:| server, Trust-Region, RESTARTED from the local solution | 18.212 | 0.0 | converged |
docs/findings/2026-09-fit-determinacy.md:41:| server, Levenberg–Marquardt (`leastsq`), from the batch start | 18.212 | 0.0 | converged |
docs/findings/2026-09-fit-determinacy.md:42:| server, basin-hopping, from the batch start | 18.212 | 0.0 | converged |
docs/findings/2026-09-fit-determinacy.md:45:percentage points between the 19.06 and the 18.21 solutions.
docs/findings/2026-09-fit-determinacy.md:66:not the best of the three on 18 (8.9 %) and leaves a student more than 5 pp
docs/findings/2026-09-fit-determinacy.md:88:  (8-JT C1s Scan_6: χ²ᵣ 70.6, 18.5, 70.6, 38.3, 18.5 from five presses).
docs/findings/2026-09-fit-determinacy.md:126:## 3. DECIDED 2026-09-18 — the amplitude lower bound (owner decision; reasoning kept below)
docs/findings/2026-09-fit-determinacy.md:155:**Decision (Skye, 2026-09-18): option (b), reasoning intact.** Allow zero
docs/findings/2026-09-fit-determinacy.md:167:Checked 2026-09-18 with the shipped `peakToBackendSpec` and the real
docs/findings/2026-09-fit-determinacy.md:221:| C1s Scan_6 | scattered starts (3 of 3) | 56.82 → 18.45 | −1.40 eV |
docs/findings/2026-09-fit-determinacy.md:259:## 7. A03 (2026-09-22) — a "Voigt" was fitted with a mix the page never drew; the sweep found DS+G's preview wrong across its fitted range
docs/findings/2026-09-fit-determinacy.md:262:both requests), `scripts/local_server_gap.js` (the 18 W1 targets),
docs/findings/2026-09-fit-determinacy.md:270:projects, one Cl 2p; 180 Voigt components): the server's free η ended at
docs/findings/2026-09-fit-determinacy.md:271:pure Gaussian (< 0.01) on 60 of the 180 and pure Lorentzian (> 0.99) on
docs/findings/2026-09-fit-determinacy.md:275:median 13.9 %, p90 19.2 %, max 20.1 % (116 of 180 components > 10 %); as
docs/findings/2026-09-fit-determinacy.md:283:median 0.36 pp, p90 0.51 pp, max 0.69 pp (none > 1 pp); a Voigt's own area
docs/findings/2026-09-fit-determinacy.md:288:student had not chosen; 76 of 180 fitted values sitting on a bound says the
docs/findings/2026-09-fit-determinacy.md:298:**The re-measurement (W1 methodology, 18 targets).** C 1s unchanged (8 of 9
docs/findings/2026-09-fit-determinacy.md:300:W1 → A03: max Δcentre 39.7 → 28.8 meV, ΔFWHM 17.2 → 15.8 %, Δarea 20.8 →
docs/findings/2026-09-fit-determinacy.md:329:fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
CLAUDE.md:113:| `Voigt` | Pseudo-Voigt, fixed η = 0.5 on BOTH sides (A03, 2026-09-22: the request sends `gl_ratio: 0.5, fix_gl_ratio: true`; until then the server fitted η FREE from 0.3 while the page drew, integrated and exported 0.5). Use `GL` to fit the mix. |
CLAUDE.md:127:each shape's FREE parameters across the fit's bounds. Both were added in A03
CLAUDE.md:471:(2026-09-18): it minimises Σ(w·r)² with w = 1/√max(raw counts, 1), the
CLAUDE.md:479:`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
CLAUDE.md:483:components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
CLAUDE.md:491:three the local descent stopping at a χ²ᵣ 5–13 % above the server's from
CLAUDE.md:498:2 dp before the server weights them. A03 is done and the designation
CLAUDE.md:502:DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
CLAUDE.md:507:See `docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md`.
CLAUDE.md:510:2026-09-18).** A component whose amplitude the fit drove to its floor,
/Users/skyefortier/xps-app/venv/bin/python3

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/lineshape_roundtrip.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -m pytest tests/test_voigt_contract.py -q -p no:cacheprovider --capture=no' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 2 in 1764ms:

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
=========================== short test summary info ============================
ERROR tests/test_voigt_contract.py - FileNotFoundError: [Errno 2] No usable t...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 1.41s

exec
/bin/zsh -lc "sed -n '125,174p' docs/findings/2026-09-fit-determinacy.md; sed -n '259,335p' docs/findings/2026-09-fit-determinacy.md; sed -n '475,507p' CLAUDE.md; rg -n 'uploadToBackend|be: .*energy|be: json|be: result|be: be|be,' templates/index.html | tail -50; sed -n '1198,1265p' fitting.py; sed -n '5755,5768p' templates/index.html; sed -n '1700,1735p' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:

## 3. DECIDED 2026-09-18 — the amplitude lower bound (owner decision; reasoning kept below)

Local engine floor: 1. Server (`fitting.py`, `amplitude_min` default): 0.
A fixed-shape peak of true amplitude 0.1 converges to 1 locally and 0.1 on
the server (~900 % area difference; Codex W1 round 1). Do NOT assume the
server is right:

- **Against 0:** at amplitude 0 the component's centre and width are
  unidentifiable; the Jacobian columns vanish, the covariance is singular,
  and any reported σ for that component is meaningless. §2's better
  solution sits exactly there and still reports a centre and a width for
  the vanished peak. A fit that silently parks a component at 0 is
  reporting a model with fewer components under the old name.
- **Against 1:** the floor is in intensity UNITS. One count is negligible
  on a 40 000-count line and substantial on CPS data where a real weak
  satellite can be below 1. A fixed floor of 1 biases weak components
  upward by an amount that depends on how the instrument reports
  intensity, and it hides the "this component is not needed" signal.
- **Options to weigh:** (a) a unit-free floor tied to the noise at the
  component's position (e.g. a fraction of √(local intensity)); (b) allow
  0 in both engines but treat "amplitude at its lower bound" as an explicit
  outcome — flag the component as not supported by the data, exclude its
  centre/width/σ from results and quantification, and say so in exports;
  (c) keep a positive floor but make it relative to the largest peak.
- **Recommendation (not a decision):** (b), with the flag carried by the
  acceptance rule, because it turns the degenerate case into information
  instead of hiding it behind either bound. Whatever is chosen applies to
  BOTH engines; parity with a wrong bound is not an improvement.

**Decision (Skye, 2026-09-18): option (b), reasoning intact.** Allow zero
in BOTH engines, and treat "amplitude at its lower bound" as an explicit
outcome: flag the component as unsupported by the data and suppress its
centre, width and σ (results, Quantify, exports, saves). "Reporting a
centre and width for a vanished peak is precisely the class of overclaim
this project exists to remove." To be implemented in the unit that follows
the optimiser-disagreement frequency measurement, not before. Until then
the difference stays listed among the reasons a local result is a starting
point.

## 4. FIXED 2026-09-20 — Differential Evolution could not run from the UI

Checked 2026-09-18 with the shipped `peakToBackendSpec` and the real
`/api/fit` route: the UI sends `amplitude_min: 0` and never an
`amplitude_max`, so every free amplitude is unbounded above, and lmfit's
`differential_evolution` requires finite bounds for every varying
parameter. Result for any model with a free amplitude (i.e. essentially
every fit): HTTP 422, "Fit failed — see server log for details"; server
log: `ValueError: differential_evolution requires finite bound for all
varying parameters`. Before unit A0 that error fell through silently to
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
by median 4.6 %, max 15.3 %. The refit vs the server's own free-η fit is
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
floor; `_set` now widens the limit to a held value.

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
the integer-clamped `caM` is not optimised (carried at its start value).

**A local result is a STARTING POINT, not a reportable result** (keyed on
`engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
generator `scripts/local_server_gap.js`): weighted, it matches the server on
GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
U 4f targets where both engines reach the same minimum every component
agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
to 20.8 % area on the Voigt satellites); it still differs on the other 4
U 4f targets (satellite areas up to 8.9 %, 0.77 pp) for two reasons,
separated by a control arm (the server with every LA m held at its start):
on one target the `caM` clamp (`caM` held at its start locally while the
server fits m continuously; holding m on the server closes the gap), on
three the local descent stopping at a χ²ᵣ 5–13 % above the server's from
the same start with the same free parameters — a worse minimum, the
"several minima" case (both engines' amplitude floor is 0 since unit
step (b)). Both engines weight by
√intensity whether the data are counts or CPS (a convention, not a
calibrated uncertainty for rates); the formula is the same but the inputs
are not bit-identical, because `uploadToBackend` rounds intensities to
2 dp before the server weights them. A03 is done and the designation
STAYS on both grounds; the `caM` clamp is the next unit, the worse-minimum
outcome is recorded for the local-engine work after it, and the label is
reconsidered only on a re-measurement after both. (The amplitude-bound change
DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
implemented: unit step (b), 2026-09-22, below.) The same file records that a
converged server fit is not ground truth: on a committed C 1s scan the
server's default method stopped in a local minimum the local engine
avoided.
See `docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md`.
8701://   { be, bg, fittedY, peaks: [{peak, y}] }
8711://       LM fit) → fittedY = evalAllPeaks(be, peaks) + bg.
8714://       bg via _computeBackgroundForSource(be, inten, src.ui).
8752:  let be, bg, rawY;
8777:    bg = _computeBackgroundForSource(be, rawY, src.ui);
8787:    const model = evalAllPeaks(be, peaks);
8795:    const peakOnly = evalPeakArray(be, p);
8799:  return { be, bg, rawY, fittedY, peaks: peakCurves };
9221:  const { be, inten } = getROIData();
9246:                         : (be.length ? computeBackground(be, inten) : []);
9470:          markers.push({ label: sym + ' ' + line, px, be, color, auger: isAuger });
9739:function updateResiduals(be, residuals, invert, show) {
9985:  const { be, inten } = getROIData();
9986:  const bgIntensity = computeBackground(be, inten);
9987:  const modelFull = evalAllPeaks(be, state.peaks);
9997:    const yArr = evalPeakArray(be, p);
10038:    roiBE: be,
10654:  const { be, inten } = getROIData();
10657:  const bgIntensity = computeBackground(be, inten);
10658:  const modelFull = evalAllPeaks(be, state.peaks);
10664:  const peakCols = state.peaks.map(p => evalPeakArray(be, p));
10711:  const { be, inten } = getROIData();
10714:  const bgArr   = computeBackground(be, inten);
10811:      const pkArr = evalPeakArray(be, p);
10824:  polyline(be, bgArr, yM);
10829:  polyline(be, inten, yM);
10834:    polyline(be, fittedY, yM);
10843:      const pkArr = evalPeakArray(be, p);
10847:      polyline(be, pkY, yM);
10941:      const pArr = evalPeakArray(be, p);
11017:    polyline(be, residArr, yR);
11194:function numericalDerivative(be, intensity, order) {
11195:  if (order === 2) return numericalDerivative(be, numericalDerivative(be, intensity, 1), 1);
11226:    const modelY = evalAllPeaks(be, state.peaks);
11881:    const { be, inten } = getROIData();
11882:    const bgI = computeBackground(be, inten);
11884:    const outcome = runFitLocal(be, bgSub, bgI);
11926:// element overlays are per-tab/stack-excluded. Shape: { id, sym, state, be, ref }.
12274:      let be, region;
12304:      out.push({ t, sym, fam: fam.family, isAuger, be, region, visEff, visFallback, tier });
12664:    _refAddCompoundMarker(sym, el.getAttribute('data-state') || (sym + ' ' + be.toFixed(1)), be, el.getAttribute('data-ref') || '');
12690:function _refAddCompoundMarker(sym, stateLabel, be, ref) {
12692:  _refCompoundMarkers.push({ id, sym, state: stateLabel, be, ref: ref || '' });
13296:function _refSignalElevatedNear(be, tol) {
13401:        be: m.be, dist, inRegion, hasRegion, vis: m.visEff, score, dataTier: m.tier,
13434:  tab._refIdentify = { be: beClicked, tol, widened, ccUnverified, cands: top, anchor: keepAnchor };
13450:  if (tab && tab._refIdentify) _refIdentifyAt(tab._refIdentify.be, tab._refIdentify.anchor);
13941:function manualAnchorBackground(be, intensity) {
13947:  if (!anchors || anchors.length < 2) return linearBackground(be, intensity);
15513:    payload.session_id = await uploadToBackend(be, inten);
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

exec
/bin/zsh -lc "rg -n 'uploadToBackend|be:.*energy|energy.*be|state.fitResult =|result.energy' templates/index.html | head -55; sed -n '3940,4025p' templates/index.html; sed -n '4170,4248p' templates/index.html; sed -n '1,60p' fitting.py; sed -n '175,215p' fitting.py; rg -n 'amplitude.*0|at_bound|held|fixed' fitting.py | tail -25; rg --files tests | rg 'seed|starts|component|bound|support|differential|contract'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
250:  .ref-blend-kind.energy { color: var(--amber); border-color: var(--amber); }
3231:    state.fitResult = tab.fitResult;
3297:      state.peaks = []; state.fitResult = null;
3419:      state.fitResult = null;
4542:// the frontend grid before uploadToBackend rounds BE to 4 decimals; the
5719:  state.fitResult = null;
5978:        <label data-xps-tip="Peak position in binding energy. After charge correction, this should match the expected literature value for the chemical state being modeled.">Center (eV)${isLinked ? ' <em style="color:var(--purple);font-size:9px">auto</em>' : ''}
6186:async function uploadToBackend(be, inten) {
6793:  state.fitResult = snap.fitResult;
7103:  state.fitResult = {
7211:  state.fitResult = null;
7269:    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
7660:    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
7732:    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
8261:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
10339:    state.fitResult = fr;
11863:      state.fitResult = null;   // live copy of tgt.fitResult = null above (unit A0)
13801:  state.fitResult = snap.fitResult ? { ...snap.fitResult } : null;
15513:    payload.session_id = await uploadToBackend(be, inten);
15791:    state.fitResult = null;
15814:    // state.fitResult === null correctly (falls back to its own
        form.append('file', file);
        fetch('/api/parse-vgd', { method: 'POST', body: form })
          .then(r => r.json())
          .then(json => {
            if (!json.error && json.be && json.be.length > 4) {
              this.createTab(file.name, json.be, json.inten, sp);
            }
            resolve();
          })
          .catch(() => resolve());
        return;
      }
      const reader = new FileReader();
      if (ext === 'xlsx' || ext === 'xls') {
        reader.readAsArrayBuffer(file);
        reader.onload = e => {
          try {
            const r = parseXLSX(e.target.result);
            if (r.be.length > 0) this.createTab(file.name, r.be, r.inten, sp);
          } catch(err) { /* skip unparseable files */ }
          resolve();
        };
      } else {
        reader.readAsText(file);
        reader.onload = e => {
          try {
            const r = parseCSV(e.target.result);
            if (r.be.length > 0) this.createTab(file.name, r.be, r.inten, sp);
          } catch(err) { /* skip unparseable files */ }
          resolve();
        };
      }
    });
  }

  _esc(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}

let tabManager;

// ═══════════════════════════════════════════════════
// PEAK MATH
// ═══════════════════════════════════════════════════
function gaussian(x, center, fwhm) {
  const sigma = fwhm / (2 * Math.sqrt(2 * Math.log(2)));
  return Math.exp(-Math.pow(x - center, 2) / (2 * sigma * sigma));
}

function lorentzian(x, center, fwhm) {
  const gamma = fwhm / 2;
  return (gamma * gamma) / (Math.pow(x - center, 2) + gamma * gamma);
}

function pseudoVoigt(x, center, fwhm, eta) {
  // Linear GL mix: eta = Lorentzian fraction (0=Gauss, 1=Lorentz)
  return eta * lorentzian(x, center, fwhm) + (1 - eta) * gaussian(x, center, fwhm);
}

function asymmGL(x, center, fwhm, glMix, alpha) {
  // Asymmetric GL: piecewise TWO-CONSTANT-WIDTH pseudo-Voigt, mirroring
  // fitting.py::_asymmetric_gl exactly. Low-BE side (x <= center) uses the
  // base fwhm; high-BE side uses a single wider, BOUNDED fwhm = fwhm*(1+asym)
  // — not a width that keeps growing with distance from center (that was
  // the bug: the frontend chart/export curve diverged from the backend fit
  // by ~10% of peak height on real U 4f data; see
  // docs/autofit/codex/asym_gl_mismatch_verdict_run{A,B}.md).
  const asym = Math.max(0, Math.min(1, alpha));
  const fwhmEff = x <= center ? fwhm : fwhm * (1 + asym);
  return pseudoVoigt(x, center, fwhmEff, glMix / 100);
}

function doniachSunjic(x, center, fwhm, alpha, gamma_asym) {
  // Doniach-Sunjic lineshape. dx = center - x so the power-law tail extends
  // toward HIGHER binding energy (left side on inverted BE axis).
  // gamma_asym > 0 adds exp(-gamma_asym*(x-center)) damping on the HIGH-BE
  // tail, limiting how far it extends. 0 = pure DS power-law.
  const dx = center - x;   // negative on HIGH-BE side (x > center)
  const gamma = Math.max(fwhm / 2, 1e-12);
  const r2 = dx * dx + gamma * gamma;
  const rPow = Math.pow(r2, (1 - alpha) / 2);
  if (rPow === 0) return 0;
  const phase = Math.PI * alpha / 2 + (1 - alpha) * Math.atan(dx / gamma);
  const core = Math.cos(phase) / rPow;
  // Exponential envelope: exp(gamma_asym * min(dx, 0)) = 1 at/below center,
    y = laTrueCasaXPS(x, center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
  } else if (p.shape === 'Gaussian') {
    y = gaussian(x, center, fwhm);
  } else if (p.shape === 'Lorentzian') {
    y = lorentzian(x, center, fwhm);
  }
  return amp * y;
}

// Grid-aware DSG_LA delta-kernel branch. Mirrors the backend's
// _ds_g_dscore_gauss `m_gauss < 0.001` path EXACTLY, including its
// normalisation by np.interp(center, x, ds_core) on the DATA GRID (the
// backend reverses a descending grid before interpolating). Normalising by
// the analytic core value at eps=0 instead differs by ~1e-3 of amplitude
// when the fitted center falls between grid points — the Codex run-A MAJOR
// on the first cut of this fix. Pinned by tests/js/lineshape_parity.test.js.
function dsgDeltaKernel_array(beArr, center, alpha, beta) {
  const N = beArr.length;
  const core = new Array(N);
  for (let i = 0; i < N; i++) core[i] = laCasaXPSCore(beArr[i] - center, alpha, beta);
  let peakVal;
  if (N === 1) {
    peakVal = core[0];                      // np.interp on a 1-pt grid
  } else {
    const asc = beArr[N - 1] > beArr[0];
    // np.interp semantics on the ascending orientation: clamp outside the
    // grid, linear interpolation between the bracketing points inside.
    const xAt = i => (asc ? beArr[i] : beArr[N - 1 - i]);
    const cAt = i => (asc ? core[i] : core[N - 1 - i]);
    if (center <= xAt(0)) {
      peakVal = cAt(0);
    } else if (center >= xAt(N - 1)) {
      peakVal = cAt(N - 1);
    } else {
      let j = 1;
      while (j < N - 1 && xAt(j) < center) j++;
      const x0 = xAt(j - 1), x1 = xAt(j);
      const t = x1 !== x0 ? (center - x0) / (x1 - x0) : 0;
      peakVal = cAt(j - 1) + t * (cAt(j) - cAt(j - 1));
    }
  }
  if (!(peakVal > 0)) {
    let mx = 0;
    for (let i = 0; i < N; i++) mx = Math.max(mx, Math.abs(core[i]));
    peakVal = mx;
  }
  if (!(peakVal > 0)) return new Array(N).fill(0);
  for (let i = 0; i < N; i++) core[i] = core[i] / peakVal;
  return core;
}

// Compute per-peak intensities across an array of BE values. Special-cases
// LACX with non-zero m so the Gaussian convolution sees the whole grid, and
// DSG_LA below the 0.001 delta-kernel threshold so the normalisation sees
// the whole grid (see dsgDeltaKernel_array above).
function evalPeakArray(beArr, p) {
  if (p.shape === 'LACX' && Math.round(p.caM || 0) > 0) {
    const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
    const out = new Array(beArr.length);
    const amp = p.amplitude;
    for (let i = 0; i < beArr.length; i++) out[i] = amp * yArr[i];
    return out;
  }
  if (p.shape === 'DSG_LA' && (p.laM || 0) < 0.001) {
    // (p.laM || 0): negative laM matches the backend's clamp-to-0-then-delta
    // path; NaN/undefined coerce to 0 → delta, which peakToBackendSpec's
    // non-finite→default sanitisation makes unreachable in fit flows.
    const yArr = dsgDeltaKernel_array(beArr, p.center, p.laAlpha, p.laBeta);
    const amp = p.amplitude;
    return yArr.map(v => amp * v);
  }
  return beArr.map(x => evalPeak(x, p));
}

function evalAllPeaks(beArray, peaks) {
  const N = beArray.length;
  const sums = new Array(N).fill(0);
  for (const p of peaks) {
    const yArr = evalPeakArray(beArray, p);
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

import hashlib
import json
import logging
import re
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
48:    return amplitude * np.exp(-4.0 * _LN2 * ((x - center) / fwhm) ** 2)
826:    amplitude_min  : float – lower bound   (default 0)
842:    amp = spec.get("amplitude", 1000.0)
851:            # A HELD parameter is held at the value requested. The bounds are
932:         min_=spec.get("amplitude_min", 0.0), max_=spec.get("amplitude_max"),
975:    open one. The page sends ``amplitude_min: 0`` and no ``amplitude_max``,
978:    freely varying parameters are closed; fixed and expression-constrained
982:    amplitude reaches max(10 x the largest |background-subtracted
1143:    expression (its own start value and bounds are overridden), a fixed one
1175:            roles.append([name, "fixed", par.value])
1208:    amplitudes x/÷ 3 (sign kept), free widths x/÷ 1.5, free centres ± 0.5 eV —
1327:# accepted residue). With the OTHER components held at their fitted values,
1459:    # the precision they are held in (float32 counts give weights that differ
tests/test_component_required.py
tests/test_scattered_starts.py
tests/test_component_support.py
tests/test_voigt_contract.py
tests/test_differential_evolution_bounds.py
tests/js/unsupported_components.test.js
tests/js/scattered_starts.test.js
tests/autofit/test_preseed_dominants.py

exec
/bin/zsh -lc "sed -n '7615,7745p' templates/index.html; sed -n '7075,7125p' templates/index.html; sed -n '4025,4057p' templates/index.html; sed -n '1320,1375p' fitting.py; sed -n '1,110p' tests/test_differential_evolution_bounds.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
  // LA(α, β, m) — CasaXPS convention
  // α: dimensionless asymmetry index (0–0.5) — tail toward HIGHER binding energy
  // β: Lorentzian half-width (eV)
  // m: Gaussian FWHM (eV) convolved with the DS core
  // Returns value normalised to 1 at x = center.
  //
  // m below the same 0.001 eV threshold the backend uses
  // (fitting.py _ds_g_dscore_gauss) means a delta kernel: skip the
  // convolution and return the normalised DS core directly. The quadrature
  // below degenerates as sigma → 0 (its Gaussian weights divide by
  // 2·sigma², collapsing the curve to ~0), so this branch is a correctness
  // fix, not just a fast path. Pinned by tests/js/lineshape_parity.test.js.
                "components": [{k: c[k] for k in ("id", "area_percent", "center_shift_from_start")} for c in fit_comps]},
        "alternatives": lower,
    }


# ── "Not supported by the data": the one statement that needs no intensity floor
# (six were tried for the Auto-Fit anchor and each rejected real components or
# accepted residue). With the OTHER components held at their fitted values,
# taking this component out of the model must make the fit to the data
# significantly worse:
#     chi2_with    = sum w (y - fitted)^2          w = the fit's own weights
#     chi2_without = sum w (y - fitted + component)^2
#     F = ((chi2_without - chi2_with) / p) / (chi2_with / dof)
# A component driven to its amplitude floor, pinned on a bound or fitted to
# numerical residue has chi2_without <= chi2_with (removing it costs nothing).
# Owner decision 2026-09-18: such a component is an explicit OUTCOME — the fit
# did not determine it — and its centre, width and sigma are not reported.
# Known limits, same as the Auto-Fit anchor: a gross single-channel artefact
# inflates chi2_with and can mark a real component unsupported; redundancy
# under overlap is NOT detected (a refit without the component is the test for
# that; step (c) does it for the Auto-Fit anchor). Threshold F >= 10 (~ p 1e-9
# at these sizes); on the 202 committed targets resolved components have
# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
# they were refitted still passes. The test for that is the refit itself:
# remove the component, refit the rest from their fitted values under the
# request's own bounds, and compare the fit to the data with and without it:
#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
# p = the component's free parameters, dof = n - nvarys of the full model.
# One extra fit, so it is done only when asked for (Auto-Fit asks for its
# charge-reference anchor: an anchor that is not required must not set the
# energy reference of a whole spectrum). Same threshold as `support`.
"""Differential Evolution must be runnable from the requests the page sends.

Confirmed bug (docs/findings/2026-09-fit-determinacy.md section 4, 2026-09-18):
the page sends ``amplitude_min: 0`` and never an ``amplitude_max``; a DS+G
peak's centre has no default bounds either. lmfit's ``differential_evolution``
refuses any varying parameter without finite bounds, so every ordinary fit
with that method returned HTTP 422 "Fit failed". ``run_fit`` now gives the
global search a finite box where the request left one open, and leaves every
other method's parameters exactly as they were.
"""

import io

import numpy as np
import pytest
from lmfit import Parameters

import fitting
from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _two_peak_spectrum(seed=3):
    rng = np.random.default_rng(seed)
    x = np.arange(280.0, 295.0, 0.1)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = rng.poisson(200.0 + g(284.8, 4000.0, 1.1) + g(288.6, 900.0, 1.4)).astype(float)
    return x, y


def _page_like_specs():
    # What peakToBackendSpec sends for two free GL peaks: a lower amplitude
    # bound of zero and NO upper bound.
    return [
        {"id": 1, "shape": "pseudo_voigt_gl", "center": 284.6, "amplitude": 3500.0,
         "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
        {"id": 2, "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0,
         "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
    ]


def test_api_fit_differential_evolution_runs_with_page_like_request(client):
    x, y = _two_peak_spectrum()
    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    up = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "c1s.csv")})
    assert up.status_code == 200, up.get_json()
    resp = client.post("/api/fit", json={
        "session_id": up.get_json()["session_id"],
        "background": {"method": "linear"},
        "peaks": _page_like_specs(),
        "fit_method": "differential_evolution",
        "n_perturb": 3,
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["success"] is True
    centres = sorted(p["params"]["center"]["value"] for p in body["individual_peaks"])
    assert centres[0] == pytest.approx(284.8, abs=0.05)
    assert centres[1] == pytest.approx(288.6, abs=0.1)


def test_differential_evolution_agrees_with_least_squares():
    x, y = _two_peak_spectrum()
    kw = dict(background_method="linear", n_perturb=0)
    de = fitting.run_fit(x, y, _page_like_specs(), fit_kws={"method": "differential_evolution"}, **kw)
    ls = fitting.run_fit(x, y, _page_like_specs(), fit_kws={"method": "least_squares"}, **kw)
    assert de["success"] and ls["success"]
    assert de["statistics"]["reduced_chi_square"] == pytest.approx(
        ls["statistics"]["reduced_chi_square"], rel=1e-3)


def test_differential_evolution_runs_with_unbounded_dsg_centre():
    # A free DS+G peak gets no default centre window, so its centre is
    # unbounded as well as its amplitude.
    x, y = _two_peak_spectrum()
    specs = [{"id": 1, "shape": "ds_g", "center": 284.7, "amplitude": 3500.0, "fwhm": 1.0,
              "alpha": 0.05, "beta": 0.3, "m_gauss": 0.8, "amplitude_min": 0},
             {"id": 2, "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0,
              "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True
    assert np.isfinite(res["statistics"]["reduced_chi_square"])
    centre = next(p for p in res["individual_peaks"] if p["id"] == 1)["params"]["center"]["value"]
    assert x.min() <= centre <= x.max()


def test_finite_search_box_only_touches_open_varying_bounds():
    p = Parameters()
    p.add("p1_amplitude", value=50.0, min=0.0)                     # open above
    p.add("p1_center", value=285.0)                                # open both sides
    p.add("p1_fwhm", value=1.0, min=0.1, max=15.0)                 # already boxed
    p.add("p2_amplitude", value=9.0e6, min=0.0, vary=False)        # fixed: untouched
    p.add("p3_amplitude", expr="p1_amplitude * 0.5")               # constrained: untouched
    x = np.linspace(280.0, 290.0, 101)
    y_sub = np.full_like(x, 100.0)
    generated = fitting._finite_search_box(p, x, y_sub)
    assert set(generated) == {"p1_amplitude", "p1_center"}
    assert set(generated["p1_amplitude"]) == {"max"} and set(generated["p1_center"]) == {"min", "max"}
    assert p["p1_amplitude"].min == 0.0

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"tests/test_voigt_contract.py\", \"tests/test_differential_evolution_bounds.py\", \"tests/test_scattered_starts.py\", \"tests/test_component_required.py\", \"-q\", \"-p\", \"no:cacheprovider\", \"--capture=no\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 36594ms:
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
  duration_ms: 1229.18988
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
  duration_ms: 1232.509618
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
  duration_ms: 1253.207656
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
  duration_ms: 1206.727264
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
  duration_ms: 1167.979843
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
  duration_ms: 1160.918116
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
  duration_ms: 1187.797697
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
  duration_ms: 1244.403182
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
  duration_ms: 1145.620337
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
  duration_ms: 1095.42854
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
  duration_ms: 1103.816092
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
  duration_ms: 1158.65787
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
  duration_ms: 1106.98177
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
  duration_ms: 1097.970696
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
  duration_ms: 1107.64392
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
  duration_ms: 1120.852077
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
  duration_ms: 1180.676817
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
  duration_ms: 1101.705967
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
  duration_ms: 1098.723529
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
  duration_ms: 1093.144522
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
  duration_ms: 1192.251267
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
  duration_ms: 1189.810641
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
  duration_ms: 1202.048026
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
  duration_ms: 1198.968878
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
  duration_ms: 1250.614079
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
  duration_ms: 1259.721979
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
  duration_ms: 1199.580863
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
  duration_ms: 1198.623328
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
  duration_ms: 1252.78458
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
  duration_ms: 1272.848065
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
  duration_ms: 1222.215787
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
# duration_ms 36654.351824

codex
The refit-grid check found another mismatch: `runFit()` retains the unrounded ROI grid in `fitResult.be`, while the script integrates the refit on upload-rounded energies. I’m checking the numerical impact and whether rounding also changes background-window selection. Normal test startup hit a temporary-directory write restriction; I’m running the focused checks with an in-memory workaround.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import json, pathlib, numpy as np
from autofit.reference import load_project_tabs
n=0
for z in sorted(pathlib.Path('\\''docs/autofit/test_data'\\'').glob('\\''*.proj.zip'\\'')):
 for t in load_project_tabs(z):
  if not t.get('\\''fitResult'\\'') or not any(p['\\''shape'\\'']=='\\''Voigt'\\'' for p in t.get('\\''peaks'\\'',[])) or not t.get('\\''rawBE'\\''): continue
  u=t['\\''ui'\\'']; lo,hi=map(float,[u['\\''roiMin'\\''],u['\\''roiMax'\\'']]); b=np.array([v-(t.get('\\''ccShift'\\'') or 0) for v in t['\\''rawBE'\\'']]); b=b[(b>=lo)&(b<=hi)]; br=np.round(b,4)
  lo,hi=sorted(map(float,[u['\\''bgStart'\\''],u['\\''bgEnd'\\'']])); i=np.where((b>=lo)&(b<=hi))[0]; ir=np.where((br>=lo)&(br<=hi))[0]
  if not np.array_equal(i,ir): print('\\''BG DIFFERENT'\\'',z.name,t['\\''name'\\''],(i[0],i[-1]),(ir[0],ir[-1]),lo,hi,b[0],br[0]); n+=1
print('\\''different backgrounds'\\'',n)
a=json.load(open('\\''docs/findings/a03/voigt_saved_vs_refit.json'\\'')); print('\\''summary'\\'',a['\\''summary'\\''])
g=json.load(open('\\''docs/findings/a03/local_server_gap.json'\\''))
for r in g['\\''regions'\\'']['\\''U4f'\\'']:
 print(r['\\''target'\\''], round(100*(r['\\''local_chi2r'\\'']/r['\\''server_held_m_chi2r'\\'']-1),3),*[round(r[k],4) for k in ['\\''held_max_dCenter_meV'\\'','\\''held_max_dFwhm_pct'\\'','\\''held_max_dArea_pct'\\'','\\''held_max_dFrac_pp'\\'']])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 167ms:
different backgrounds 0
summary {'n_tabs': 55, 'n_converged': 55, 'dFrac_pp': {'median': 0.36397402720980065, 'p90': 0.5078511773598887, 'max': 0.6882979245316376}, 'gt_1pp': 0, 'voigt_dArea_pct': {'median': 4.576866262303724, 'p90': 7.556793905659809, 'max': 15.300735561732603}}
U4f Scan_0 0.785 1.5193 0.2129 0.2836 0.0149
U4f Scan_1 1.588 3.975 1.4559 2.107 0.1221
U4f Scan_2 0.071 1.477 0.3008 0.4118 0.0225
U4f Scan_3 0.066 1.425 0.289 0.4041 0.0199
U4f Scan_4 5.35 13.3501 3.1315 5.2677 0.1899
U4f Scan_5 9.656 6.3035 3.5056 5.4905 0.2462
U4f Scan_6 1.084 3.6326 1.0713 1.5887 0.0694
U4f Scan_7 0.693 2.5448 0.399 0.5509 0.0367
U4f Scan_8 13.077 5.8261 4.9735 8.2432 0.3249

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require('\\''child_process'\\''); const original=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(file.includes('\\''python'\\'')){args=['\\''-c'\\'','\\''import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; p=sys.argv.pop(1); sys.argv[0]=p; runpy.run_path(p,run_name=\"__main__\")'\\'',...args];}return original(file,args,opts);};
require('\\''./tests/js/lineshape_roundtrip.test.js'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const fs=require('\\''fs'\\''),cp=require('\\''child_process'\\''),Module=require('\\''module'\\''); const orig=cp.execFileSync;
cp.execFileSync=function(f,a,o){if(f.includes('\\''python'\\'')) a=['\\''-c'\\'','\\''import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; p=sys.argv.pop(1); sys.argv[0]=p; runpy.run_path(p,run_name=\"__main__\")'\\'',...a]; return orig(f,a,o);};
let s=fs.readFileSync('\\''tests/js/lineshape_roundtrip.test.js'\\'','\\''utf8'\\'');
s=s.slice(0,s.indexOf('\\''for (const [shape, c] of Object.entries(CASES))'\\''))+
"'`
const c={truth:{shape:'"'\\''DSG_LA'\\'',laAlpha:0.5,laBeta:0.5,laM:0,fixLaAlpha:true,fixLaM:true},start:{}};
const {res,peaks,specs}=roundTrip('\\''DSG_LA'\\'',c);
console.log(JSON.stringify({spec:specs[0],alpha:res.individual_peaks[0].params.alpha,m:res.individual_peaks[0].params.m_gauss,rel:maxRelDiff(env.evalPeakArray(res.energy,peaks[0]),res.individual_peaks[0].y,peaks[0].amplitude)}));
"'`;
const m=new Module(process.cwd()+'"'\\''/tests/js/probe.js'\\'');m.filename=m.id;m.paths=module.paths;m._compile(s,m.filename);'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import fitting, numpy as np
from lmfit import Model
x=np.linspace(280,290,101); y=fitting._gaussian(x,100,285,1)+5
base=dict(id=1,shape='\\''gaussian'\\'',center=285,amplitude=-10,fwhm=1,fix_amplitude=True,fix_center=True,center_min=280,center_max=282)
p=fitting._make_peak_params(Model(fitting._gaussian,prefix='\\''p1_'\\''),base,'\\''p1_'\\'',[base])
print('\\''held'\\'',[(k,v.value,v.min,v.max,v.vary) for k,v in p.items()])
print('\\''box'\\'',fitting._finite_search_box(p,x,y)); print('\\''scattered'\\'',[(k,v.value,v.vary) for k,v in fitting._scattered_start(p,np.random.default_rng(1)).items()])
for method in ['\\''least_squares'\\'','\\''differential_evolution'\\'']:
 r=fitting.run_fit(x,y,[base],background_method='\\''none'\\'',fit_kws={'\\''method'\\'':method},n_starts=1)
 print(method,r['\\''success'\\''],r['\\''individual_peaks'\\''][0]['\\''params'\\''])
free=dict(base,fix_amplitude=False,fix_center=False)
pf=fitting._make_peak_params(Model(fitting._gaussian,prefix='\\''p1_'\\''),free,'\\''p1_'\\'',[free])
print('\\''fresh freed'\\'',[(k,v.value,v.min,v.max,v.vary) for k,v in pf.items()])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 1817ms:
/Users/skyefortier/.matplotlib is not a writable directory
{"spec":{"id":"1","name":"P","center":391.92,"amplitude":9600,"fwhm":1.92,"amplitude_min":0,"fix_center":false,"fix_fwhm":false,"fix_amplitude":false,"fix_gl_ratio":false,"shape":"ds_g","alpha":0.5,"beta":0.5,"m_gauss":0,"fix_alpha":true,"fix_beta":false,"fix_m_gauss":true},"alpha":{"value":0.5,"stderr":0,"vary":false,"expr":null,"min":0,"max":0.5},"m":{"value":0,"stderr":0,"vary":false,"expr":null,"min":0,"max":4},"rel":0.009068664085173084}

 succeeded in 1796ms:
/Users/skyefortier/.matplotlib is not a writable directory
held [('p1_amplitude', -10, -10, inf, False), ('p1_center', 285, 280, 285, False), ('p1_fwhm', 1, 0.1, 15.0, True)]
box {}
scattered [('p1_amplitude', -10.0, False), ('p1_center', 285.0, False), ('p1_fwhm', 1.0096326104747961, True)]
least_squares True {'amplitude': {'value': -10.0, 'stderr': 0.0, 'vary': False, 'expr': None, 'min': -10.0, 'max': None}, 'center': {'value': 285.0, 'stderr': 0.0, 'vary': False, 'expr': None, 'min': 280.0, 'max': 285.0}, 'fwhm': {'value': 0.10000000000552914, 'stderr': 0.8234776547693704, 'vary': True, 'expr': None, 'min': 0.1, 'max': 15.0}, 'area': {'value': 1.125030517645654, 'stderr': None}}
differential_evolution True {'amplitude': {'value': -10.0, 'stderr': None, 'vary': False, 'expr': None, 'min': -10.0, 'max': None}, 'center': {'value': 285.0, 'stderr': None, 'vary': False, 'expr': None, 'min': 280.0, 'max': 285.0}, 'fwhm': {'value': 0.1, 'stderr': None, 'vary': True, 'expr': None, 'min': 0.1, 'max': 15.0}, 'area': {'value': 1.1250305176072914, 'stderr': None}}
fresh freed [('p1_amplitude', -10, 0.0, inf, True), ('p1_center', 285, 280, 282, True), ('p1_fwhm', 1, 0.1, 15.0, True)]

 succeeded in 57437ms:
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
  duration_ms: 1935.920643
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
ok 2 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1802.311341
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
ok 3 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1843.317762
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
ok 4 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1847.287639
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
ok 5 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1782.009541
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
ok 6 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1934.397459
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 7 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1862.447292
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
  duration_ms: 1807.972521
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
  duration_ms: 1866.211163
  type: 'test'
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
ok 10 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1822.801832
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
ok 11 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1889.857494
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
ok 12 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1853.688984
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
ok 13 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1778.669802
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
ok 14 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1834.844038
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
ok 15 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1836.290811
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
ok 16 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1779.179714
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
ok 17 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1923.947545
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
ok 18 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1869.105682
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
ok 19 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1787.732713
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
ok 20 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1914.365199
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
ok 21 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1753.655315
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
ok 22 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1857.407867
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
ok 23 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1860.520543
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
ok 24 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1860.398004
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
ok 25 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1976.663929
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
ok 26 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1855.829356
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
ok 27 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1861.369463
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
ok 28 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1992.21717
  type: 'test'
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
ok 29 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1754.035671
  type: 'test'
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
ok 30 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1862.637233
  type: 'test'
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
ok 31 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1861.151802
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
# duration_ms 57486.730632

exec
/bin/zsh -lc "rg -n 'function _bgWindowIndices|function getROIData|function _peakArea' templates/index.html; nl -ba scripts/voigt_saved_vs_refit.js | sed -n '36,61p'; nl -ba tests/js/lineshape_roundtrip.test.js | sed -n '4,13p'; nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | sed -n '99,114p'; git log -3 --oneline" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
4545:function _bgWindowIndices(be, bgStart, bgEnd) {
4936:function getROIData() {
8320:function _peakArea(p, be) {
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
   111	## 5. What the sweep found
   112	
   113	| shape | result |
   114	|---|---|
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gh3garcp' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fTp8zt0Y' (errno=Operation not permitted)
a61bd05 fix(A03): Codex round 2 (NO-GO x2) - saved side on the saved fit's grid with upload rounding; control arm at the rounded m; every shape parameter locked at each bound, which found lmfit clipping a HELD value to its bounds
4d623f5 fix(A03): Codex round 1 (NO-GO x2) - explicit measurement arms; release-note number from the page's own numbers; builders sent a mix or DS alpha of exactly 0 as the default; Voigt uncertainty note; caM attribution by a control arm
712e136 fix(A03): a Voigt is the fixed 50/50 mix on BOTH sides; page->server->page identity test; parameter-range sweep; U 4f gap re-measured

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import fitting, numpy as np
from lmfit import Model
from types import SimpleNamespace
s=dict(id=1,shape='\\''ds_g'\\'',center=285,amplitude=100,fwhm=1,alpha=.1,beta=.3,m_gauss=0,fix_m_gauss=True)
m=Model(fitting._SHAPE_FUNCS['\\''ds_g'\\''],prefix='\\''p1_'\\'')
p=fitting._make_peak_params(m,s,'\\''p1_'\\'',[s]); x=np.linspace(280,290,101); y=np.ones(101)
p2=p.copy(); p2['\\''p1_m_gauss'\\''].min=-10
seed=lambda p:fitting._request_seed(x,y,y,['\\''ds_g'\\''],['\\''p1_'\\''],p,fit_kws={'\\''method'\\'':'\\''least_squares'\\''},n_perturb=3)
print('\\''held bound does not change seed'\\'',seed(p),seed(p2))
def retained(q):
 print('\\''required retained'\\'',q['\\''p1_m_gauss'\\''].value,q['\\''p1_m_gauss'\\''].min,q['\\''p1_m_gauss'\\''].vary)
 return SimpleNamespace(chisqr=2.,success=True)
fitting._component_required(retained,p,[],y,y,1.,1,3)
s['\\''fix_m_gauss'\\'']=False
pf=fitting._make_peak_params(m,s,'\\''p1_'\\'',[s])
print('\\''new request free m floor'\\'',pf['\\''p1_m_gauss'\\''].min)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "sed -n '4540,4573p' templates/index.html; sed -n '4936,4955p' templates/index.html; sed -n '8318,8330p' templates/index.html; rg -n '"'^def test_'"' tests/test_component_required.py tests/test_scattered_starts.py tests/test_differential_evolution_bounds.py | tail -15" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
tests/test_differential_evolution_bounds.py:482:def test_a_verified_candidate_displaces_an_unverified_one_even_at_higher_chi_square(monkeypatch):
tests/test_differential_evolution_bounds.py:505:def test_exact_refinement_is_accepted_at_any_intensity_scale(scale, n_perturb):
tests/test_differential_evolution_bounds.py:525:def test_zero_signal_fit_is_accepted(n_perturb):
tests/test_differential_evolution_bounds.py:551:def test_narrow_exact_peak_on_a_requested_centre_bound_is_accepted(case, n_perturb):
tests/test_differential_evolution_bounds.py:572:def test_a_converged_refinement_is_returned_without_a_chi_square_gate(monkeypatch):
tests/test_differential_evolution_bounds.py:598:def test_differential_evolution_is_never_worse_than_least_squares_from_the_same_start(case, n_perturb):
tests/test_differential_evolution_bounds.py:616:def test_the_search_still_wins_when_it_is_better_than_the_local_fit():
tests/test_component_required.py:52:def test_a_redundant_anchor_is_supported_but_not_required():
tests/test_component_required.py:70:def test_a_real_graphite_anchor_is_required():
tests/test_component_required.py:80:def test_the_fit_itself_is_unchanged_by_the_check():
tests/test_component_required.py:96:def test_everything_linked_to_the_removed_component_goes_with_it_transitively():
tests/test_component_required.py:121:def test_differential_evolution_goes_through_its_own_candidate_machinery():
tests/test_component_required.py:130:def test_the_refit_of_a_stochastic_method_is_seeded(monkeypatch):
tests/test_component_required.py:146:def test_known_limit_noise_free_exact_fit_reports_a_redundant_component_as_required():
tests/test_component_required.py:167:def test_a_resolved_anchor_at_extreme_dynamic_range_is_required():

 succeeded in 1689ms:
/Users/skyefortier/.matplotlib is not a writable directory
held bound does not change seed 103360943 103360943
required retained 0 0 False
new request free m floor 0.05

 exited 1 in 180648ms:
......E....................................................................EEEEEE............
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
86 passed, 7 errors in 180.19s (0:03:00)

codex
A locked value is still missed by the new coverage: the DS+G control allows α = 0.5, but the tests stop at the optimizer’s 0.49 bound. With α locked at 0.5 and m locked at 0, the server reports α = 0.5 but its evaluator clips it to 0.495. The page does not clip it; the reproduced curves differ by 0.907% of amplitude.

The 31-test round-trip suite passed with 29 passes and the two declared todos. Probes of DE, scattered starts, and a fresh unlocked request have not shown widened bounds leaking into free parameters.

exec
/bin/zsh -lc "nl -ba tests/js/lineshape_roundtrip.test.js | sed -n '179,198p'; nl -ba fitting.py | sed -n '846,865p'; nl -ba templates/index.html | sed -n '6079,6086p'; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
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
   846	    def _set(name, value, min_=None, max_=None, expr=None, vary=True):
   847	        full = prefix + name
   848	        if full not in p:
   849	            return
   850	        if not vary and expr is None:
   851	            # A HELD parameter is held at the value requested. The bounds are
   852	            # the optimiser's search limits; lmfit clips a value outside them
   853	            # even when it does not vary, which silently changed a locked
   854	            # DS+G m of 0 (the page's delta-kernel branch, drawn without
   855	            # convolution) into 0.05 (a convolved fit) — A03 Codex round 2's
   856	            # locked-at-bounds round trips. Widen the limit to the value.
   857	            if min_ is not None and value < min_:
   858	                min_ = value
   859	            if max_ is not None and value > max_:
   860	                max_ = value
   861	        p[full].set(value=value)
   862	        if expr is not None:
   863	            p[full].expr = expr
   864	            p[full].vary = False
   865	        else:
  6079	        <div class="field">
  6080	          <label data-xps-tip="Dimensionless asymmetry parameter (0-0.5). Controls the tail toward higher binding energy from metallic screening. Similar in meaning to the DS singularity index. Typical values: 0.01-0.05 for most metals.">&alpha; (asymmetry, 0&ndash;0.5)
  6081	            ${!isLinked ? `<button class="lock-btn${p.fixLaAlpha ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixLaAlpha',this)" title="${p.fixLaAlpha ? 'Unlock' : 'Lock'} during fitting">${p.fixLaAlpha ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
  6082	          </label>
  6083	          <input type="number" value="${p.laAlpha.toFixed(3)}" step="0.005" min="0" max="0.5"
  6084	            oninput="updatePeakParam(${p.id},'laAlpha',parseFloat(this.value))">
  6085	        </div>
  6086	        <div class="field">
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-H0QunqG5' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xLsJRcui' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_r3_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_r3_verdict_runB.md
?? docs/autofit/codex/a03_voigt_eta_recheck2_prompt.txt

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import numpy as np, fitting
raw=np.array([280.00004+.1*i for i in range(101)]); x=np.round(raw,4)
y=np.round(20+fitting._pseudo_voigt_gl(raw,1000,285,1.2,.5),2); y[-1]=20000
s=[dict(id=1,shape='\\''pseudo_voigt_gl'\\'',center=285,amplitude=1000,fwhm=1.2,gl_ratio=.5,fix_gl_ratio=True)]
for label,grid in [('\\''page'\\'',raw),('\\''script'\\'',x)]:
 idx=np.where((grid>=280)&(grid<=290))[0]
 r=fitting.run_fit(x,y,s,background_method='\\''linear'\\'',bg_start_idx=int(idx[0]),bg_end_idx=int(idx[-1])+1,fit_kws={'\\''method'\\'':'\\''least_squares'\\''},n_perturb=3)
 p=r['\\''individual_peaks'\\''][0]['\\''params'\\'']
 print(label,'\\''bg rows'\\'',int(idx[0]),int(idx[-1]),'\\''success'\\'',r['\\''success'\\''],'\\''amp'\\'',p['\\''amplitude'\\'']['\\''value'\\''],'\\''center'\\'',p['\\''center'\\'']['\\''value'\\''],'\\''fwhm'\\'',p['\\''fwhm'\\'']['\\''value'\\''],'\\''seed'\\'',r['\\''random_seed'\\''])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 1543ms:
/Users/skyefortier/.matplotlib is not a writable directory
page bg rows 0 99 success True amp 1002.1865445676165 center 284.9999732037745 fwhm 1.1548141780164614 seed 487518052
script bg rows 0 100 success True amp 7.439793613529637e-15 center 286.9999994571153 fwhm 0.10000000000000002 seed 330327185

codex
No BLOCKER found. Two MAJOR findings remain.

1. **MAJOR — A reachable locked DS+G endpoint still breaks identity.** [fitting.py:850](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py:850), [lineshape_roundtrip.test.js:184](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:184). Set `laAlpha=0.5`, `fixLaAlpha=true`, `laM=0`, `fixLaM=true`. The UI permits α=0.5. `_set` now preserves and reports it, but the server evaluator clips α to 0.495; the page evaluates 0.5. Reproduced **0.907% of amplitude** drawn-versus-fitted error, even in the supposedly exact delta branch. The test covers 0.49, missing this reachable endpoint. Align the accepted domain and evaluators, and test the UI endpoint.

2. **MAJOR — Upload rounding now changes the measurement’s background request.** [voigt_saved_vs_refit.js:43](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:43), [local_lm_server_parity_backend.py:25](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/local_lm_server_parity_backend.py:25). The bridge computes background indices **after rounding**; the page computes them beforehand. Reproduction: energies `280.00004 + 0.1*i`, 101 channels, background window `[280,290]`, linear background, a Voigt peak plus an elevated last channel. The page selects rows 0–99; the script selects 0–100. Both fits converge, but amplitudes are **1002.19 versus approximately zero**, with different seeds. Preserve the page’s pre-upload indices. None of the current 55 tabs crossed a boundary in this check.

3. **MINOR — Refit and fallback integration still use the wrong grid.** [voigt_saved_vs_refit.js:45](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:45), [voigt_saved_vs_refit.js:53](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:53). `runFit()` stores the **unrounded** ROI energies in `fitResult.be` at [index.html:7733](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:7733). The script integrates refits—and saves missing `fitResult.be`—on rounded energies. For a grid spacing of 0.10004 eV, its rectangular integration step becomes 0.1000. Keep separate display and upload grids.

4. **MINOR — Documentation cleanup remains incomplete.** [lineshape_roundtrip.test.js:9](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:9) still says “12%” beside “13.9%”; the artifact says **13.89%**. [Plan:103](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:103) still says **10 pass, 2 todo**, versus the verified **29 pass, 2 todo**.

Round-2 closure: **item 1 partial; item 2 closed; item 3 partial; item 4 partial.** The saved-fit grid selection, upload values, rounded-m control, and quoted artifact summaries check out. The 18 cases genuinely exercise server locks and page curves, but coverage misses the endpoint above and positive-m boundary locks.

No widened-bound leakage was found through DE, scattered starts, effective-role hashing, retained `_component_required` parameters, or fresh requests that unlock parameters. Fixed negative amplitude and out-of-window center values are now honored; fresh free requests restore their original bounds.

Validation: **29 JS passes, 2 known todos; 86 Python passes, 7 setup errors caused by read-only temporary-directory restrictions.** No files changed.

**VERDICT: NO-GO.**
tokens used
104,763
No BLOCKER found. Two MAJOR findings remain.

1. **MAJOR — A reachable locked DS+G endpoint still breaks identity.** [fitting.py:850](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py:850), [lineshape_roundtrip.test.js:184](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:184). Set `laAlpha=0.5`, `fixLaAlpha=true`, `laM=0`, `fixLaM=true`. The UI permits α=0.5. `_set` now preserves and reports it, but the server evaluator clips α to 0.495; the page evaluates 0.5. Reproduced **0.907% of amplitude** drawn-versus-fitted error, even in the supposedly exact delta branch. The test covers 0.49, missing this reachable endpoint. Align the accepted domain and evaluators, and test the UI endpoint.

2. **MAJOR — Upload rounding now changes the measurement’s background request.** [voigt_saved_vs_refit.js:43](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:43), [local_lm_server_parity_backend.py:25](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/local_lm_server_parity_backend.py:25). The bridge computes background indices **after rounding**; the page computes them beforehand. Reproduction: energies `280.00004 + 0.1*i`, 101 channels, background window `[280,290]`, linear background, a Voigt peak plus an elevated last channel. The page selects rows 0–99; the script selects 0–100. Both fits converge, but amplitudes are **1002.19 versus approximately zero**, with different seeds. Preserve the page’s pre-upload indices. None of the current 55 tabs crossed a boundary in this check.

3. **MINOR — Refit and fallback integration still use the wrong grid.** [voigt_saved_vs_refit.js:45](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:45), [voigt_saved_vs_refit.js:53](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:53). `runFit()` stores the **unrounded** ROI energies in `fitResult.be` at [index.html:7733](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:7733). The script integrates refits—and saves missing `fitResult.be`—on rounded energies. For a grid spacing of 0.10004 eV, its rectangular integration step becomes 0.1000. Keep separate display and upload grids.

4. **MINOR — Documentation cleanup remains incomplete.** [lineshape_roundtrip.test.js:9](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:9) still says “12%” beside “13.9%”; the artifact says **13.89%**. [Plan:103](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:103) still says **10 pass, 2 todo**, versus the verified **29 pass, 2 todo**.

Round-2 closure: **item 1 partial; item 2 closed; item 3 partial; item 4 partial.** The saved-fit grid selection, upload values, rounded-m control, and quoted artifact summaries check out. The 18 cases genuinely exercise server locks and page curves, but coverage misses the endpoint above and positive-m boundary locks.

No widened-bound leakage was found through DE, scattered starts, effective-role hashing, retained `_component_required` parameters, or fresh requests that unlock parameters. Fixed negative amplitude and out-of-window center values are now honored; fresh free requests restore their original bounds.

Validation: **29 JS passes, 2 known todos; 86 Python passes, 7 setup errors caused by read-only temporary-directory restrictions.** No files changed.

**VERDICT: NO-GO.**
