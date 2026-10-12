#!/usr/bin/env python3
"""Sealed-fit v6 Q8 (owner 2026-10-11: "measure first and show me the numbers before switching"):
Auto-Fit refits after its charge shift (ship step 0d). TODAY Auto-Fit makes ONE fit (A) in the
provisional frame, then moves the frame by its fitted graphite centre, re-selects the window,
recomputes the background, locks every centre and shows A's numbers with them. The PROPOSAL makes
a second, FINAL fit (B) in the corrected frame: the same model (A's values projected onto the
peaks, every centre locked), the same overlays, method, n_perturb and require_component, on the
re-selected window — which is what the student sees and what is sealed.

This runs the deployed page's own Auto-Fit (runAutoFitC1sGraphite) on every committed C 1s tab,
in a real browser against a local server, then builds B's request from the finalised page state
exactly as Auto-Fit builds its own, and reports for each tab what the student would see today and
after the change: χ²ᵣ, R, each component's FWHM, area and area % (the page's area definition, and
the server's — Q5), the anchor's gates on B, and the 40 % graphite warning.
Usage: venv/bin/python scripts/q8_autofit_refit.py BASE_URL. Writes docs/findings/q8-autofit-refit/results.json.
"""
import glob, json, os, sys, time
from playwright.sync_api import sync_playwright

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5151"
OUT = os.path.join(REPO, "docs/findings/q8-autofit-refit/results.json")

SETUP = """() => { window.__notes = [];
  const n = window.notify; window.notify = (m, k, ...r) => { window.__notes.push([k, String(m)]); return n(m, k, ...r); };
  window._showAutoFitConfirmModal = () => Promise.resolve(true); }"""

# what the student sees for the CURRENT state (after Auto-Fit, or after the B fit is applied below)
VIEW = """() => {
  const fr = state.fitResult; const be = fr && fr.be;
  const peaks = state.peaks.map(p => ({ id: p.id, name: p.name, shape: p.shape, center: p.center, fwhm: p.fwhm, amplitude: p.amplitude,
                                        fixCenter: !!p.fixCenter, area: be ? _peakArea(p, be) : null }));
  const tot = peaks.reduce((s, p) => s + (p.area || 0), 0);
  peaks.forEach(p => { p.pct = tot > 0 ? 100 * p.area / tot : null; });
  const ip = (fr && fr.backendResult && fr.backendResult.individual_peaks) || [];
  const sArea = q => (q && q.params && q.params.area) ? q.params.area.value : null;   // individual_peaks[].params.area.value
  const sTot = ip.reduce((s, q) => s + (sArea(q) || 0), 0);
  peaks.forEach(p => { const q = ip.find(q => String(q.id) === String(p.id)); p.server_area = sArea(q); p.server_pct = sArea(q) != null && sTot > 0 ? 100 * sArea(q) / sTot : null; });
  const g = state.peaks.find(p => p.name === 'Graphite');
  return { ccShift: state.ccShift, n_points: be ? be.length : 0, be_min: be ? _arrMin(be) : null, be_max: be ? _arrMax(be) : null,
           n_fitted: fr && fr.fittedY ? fr.fittedY.length : 0,
           chi2r: fr ? fr.chiReduced : null, rFactor: fr ? fr.rFactor : null, peaks,
           warn40: g ? _autoFitCheckGraphiteFraction(g.id) : null };
}"""

# B: the final fit in the corrected frame, built from the finalised state exactly as Auto-Fit builds
# its request (overlays, amplitude_min 0, n_perturb 3, require_component), applied like a fit result
REFIT = """async () => {
  const { be: be2, inten: inten2 } = getROIData();
  const bgType = document.getElementById('bg-type').value;
  const bgWin = _bgWindowIndices(be2, parseFloat(document.getElementById('bg-start').value), parseFloat(document.getElementById('bg-end').value));
  const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
  const fitMethod = document.getElementById('fit-method').value;
  const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
  const peakSpecs = state.peaks.map(p => {
    const spec = peakToBackendSpec(p);
    if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
    if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
    if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
    if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
    spec.amplitude_min = 0;
    return spec;
  });
  const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvg };
  if (bgType === 'manual') bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
  const sessionId = await uploadToBackend(be2, inten2);
  const r = await fetch('/api/fit', { method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, background: bgPayload, peaks: peakSpecs, fit_method: fitMethod, n_perturb: 3, require_component: anchorId }) });
  const json = await r.json();
  if (!r.ok || json.success !== true) return { ok: false, status: r.status, error: json.error || json.message };
  const g = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  const gates = { supported: _autoFitGraphiteIsSupported(g, json), required: json.required ? json.required.required : null,
                  refit_converged: json.required ? json.required.refit_converged : null };
  const bgI2 = computeBackground(be2, inten2);
  applyBackendResult(json);   // the peaks take B's values (centres locked: unchanged)
  const stats = json.statistics || {};
  state.fitResult = { chiReduced: stats.reduced_chi_square, be: be2, bgSubtracted: inten2.map((v, i) => v - bgI2[i]), bgIntensity: bgI2,
                      fittedY: json.fitted_y, backendResult: json };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);
  return { ok: true, gates };
}"""


def main():
    files = sorted(glob.glob(os.path.join(REPO, "docs/autofit/test_data/**/*.proj.*"), recursive=True))
    results = []
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        for f in files:
            pg = b.new_page(viewport={"width": 1200, "height": 900})
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(BASE + "/", wait_until="load")
            pg.set_input_files("#load-session-input", f)
            pg.wait_for_function("() => tabManager && tabManager.tabs && tabManager.tabs.length > 0", timeout=120000)
            time.sleep(2)
            tabs = pg.evaluate("() => tabManager.tabs.filter(t => !t.isStack).map(t => ({ id: t.id, name: t.name }))")
            for t in tabs:
                pg.evaluate("(id) => tabManager.activateTab(id)", t["id"])
                if not pg.evaluate("() => isC1sTab(tabManager._getTab(tabManager.activeId))"):
                    continue
                pg.evaluate(SETUP)
                t0 = time.time()
                pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
                notes = pg.evaluate("() => window.__notes")
                applied = pg.evaluate("() => !!(state.fitResult && document.getElementById('sb-msg').textContent === 'Auto-fit complete')")
                row = {"file": os.path.basename(f), "tab": t["name"], "applied": applied, "notes": notes, "secs_A": round(time.time() - t0, 1)}
                if applied:
                    row["A"] = pg.evaluate(VIEW)
                    t1 = time.time()
                    ref = pg.evaluate(REFIT)
                    row["secs_B"] = round(time.time() - t1, 1)
                    row["B_status"] = ref
                    if ref.get("ok"):
                        row["B"] = pg.evaluate(VIEW)
                row["page_errors"] = list(errs)
                results.append(row)
                print(row["file"][:28], row["tab"], "applied" if applied else "refused", row.get("secs_A"), row.get("secs_B"), flush=True)
                with open(OUT, "w") as fh:
                    json.dump(results, fh, indent=1)
            pg.close()
        b.close()


if __name__ == "__main__":
    main()
