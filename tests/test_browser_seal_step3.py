"""Seal 1c step 3 (plan docs/superpowers/plans/2026-10-14-seal-1c-page.md §1, §6, §7, §12): every producer
creates a deep-frozen seal BESIDE today's result (nothing reads it yet). Real page, real server: the seal's R is
exactly what the fit was made from (the request the page sent, the samples `_roiSelect` chose, the start model,
the context), its O the reply verbatim, step 0 already rebuilds R.request from R; its VIEW gives the numbers
today's fitResult holds (the differences the plan release-notes — the page's approximate chi-square — named).

Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import json
import os

import pytest

pytest.importorskip("playwright.sync_api")

from test_browser_bg_window_request import browser, server  # noqa: F401,E402
from test_browser_seal_requests import SCENARIOS, _setup, AUTOFIT_PROJECT  # noqa: E402

CHECK = """async () => {
  const fr = state.fitResult, seal = fr && fr.seal;
  if (!seal) return { seal: false };
  const v = _sealView(seal), R = seal.R, O = seal.O;
  const eq = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const roi = getROIData();
  const out = {
    seal: true, frozen: Object.isFrozen(seal) && Object.isFrozen(seal.R) && Object.isFrozen(seal.O) && Object.isFrozen(R.pageModel[0]),
    engine: seal.engine, producer: seal.producer,
    idx: eq(R.idx, roi.idx), energies: eq(R.energies, roi.be), counts: eq(R.counts, roi.inten),
    page: !!(R.page && R.page.software && R.page.page && R.page.page.page_sha256),
    viewEnergies: eq(v.energies, fr.be), viewChi2r: v.statistics.chi2r === fr.chiReduced,
  };
  if (seal.engine === 'server') {
    out.request = eq(R.request, window.__sent);
    out.step0 = eq(_buildFitRequest(seal.producer, R.pageModel, R.context0.live, R.energies,
                                    { requireComponent: R.context0.producer.require_component }), R.request);
    out.O = eq(O, fr.backendResult);
    out.viewBg = eq(v.background, Array.from(fr.bgIntensity));
    out.viewFittedY = eq(v.fittedY, fr.fittedY);
    out.viewModel = state.peaks.every(p => { const q = v.model.find(x => x.id === p.id);
      return q && ['center', 'amplitude', 'fwhm', 'glMix'].every(k => Object.is(q[k], p[k])); });
    out.rmseRel = Math.abs(v.statistics.rmse - fr.rmse) / fr.rmse;
    out.rPct = v.rPanel ? Math.abs(v.rPanel.rPct - fr.rFactor.rPct) : null;
  } else {
    out.viewRmse = v.statistics.rmse === fr.rmse;
    out.viewR = v.rPanel && v.rPanel.rPct === fr.rFactor.rPct;
    out.viewBg = eq(v.background, Array.from(fr.bgIntensity));
    out.model = state.peaks.every(p => { const q = v.model.find(x => x.id === p.id);
      return q && ['center', 'amplitude', 'fwhm'].every(k => Object.is(q[k], p[k])); });
    out.bgCert = !!(seal.O.background.certificate || ['linear', 'none', 'manual'].includes(seal.O.background.bgType));
  }
  return out;
}"""


def _record_sent(page):
    page.route("**/api/fit/start", lambda route: (page.evaluate("(b) => { window.__sent = b; }",
                                                                {k: v for k, v in json.loads(route.request.post_data).items()
                                                                 if k != "session_id"}), route.continue_()))


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_run_fit_writes_a_seal_beside_its_result(browser, server, name):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    try:
        _setup(pg, SCENARIOS[name])
        _record_sent(pg)
        pg.evaluate("async () => { await runFit(); }")
        got = pg.evaluate(CHECK)
    finally:
        pg.close()
    assert got["seal"] and got["frozen"] and got["engine"] == "server" and got["producer"] == "runFit", got
    for k in ("idx", "energies", "counts", "page", "request", "step0", "O", "viewEnergies", "viewBg", "viewFittedY", "viewChi2r", "viewModel"):
        assert got[k] is True, (k, got)
    # the page summed the RMSE in its own order and formed R from fitted_y − background: rounding only
    assert got["rmseRel"] < 1e-12 and (got["rPct"] is None or got["rPct"] < 1e-9), got
    assert errors == [], errors


def test_auto_fit_seals_its_final_fit_with_the_anchor_fit_as_evidence(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1200, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    try:
        pg.goto(server + "/", wait_until="load")
        pg.set_input_files("#load-session-input", AUTOFIT_PROJECT)
        pg.wait_for_function("() => tabManager.tabs.some(t => t.name === 'C1s Scan')", timeout=60000)
        pg.evaluate("() => tabManager.activateTab(tabManager.tabs.find(t => t.name === 'C1s Scan').id)")
        pg.evaluate("() => { window._showAutoFitConfirmModal = () => Promise.resolve(true); }")
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        got = pg.evaluate("""() => {
            const seal = state.fitResult && state.fitResult.seal; if (!seal) return { seal: false };
            const E = seal.E, R = seal.R;
            const d = deriveAutoFit(E.R.pageModel, E.R.context0.live, E.O);
            const step0 = (r) => JSON.stringify(_buildFitRequest('autoFit', r.pageModel, r.context0.live, r.energies,
                                     { requireComponent: r.context0.producer.require_component })) === JSON.stringify(r.request);
            return { seal: true, producer: seal.producer, hasE: !!(E && E.R && E.O), frozen: Object.isFrozen(E.O),
                     step0R1: step0(E.R), step0R2: step0(R), derived: _sameModel(d.pageModel, R.pageModel),
                     derivedCtx: JSON.stringify(d.ctx) === JSON.stringify(R.context0.live),
                     O2: JSON.stringify(seal.O) === JSON.stringify(state.fitResult.backendResult) }; }""")
    finally:
        pg.close()
    assert got["seal"] and got["producer"] == "autoFit" and got["hasE"] and got["frozen"], got
    assert got["step0R1"] and got["step0R2"] and got["derived"] and got["derivedCtx"] and got["O2"], got
    assert errors == [], errors


def test_the_local_fallback_seals_its_own_snapshot(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        pg.route("**/api/upload", lambda route: route.abort())   # transport failure: the local engine fits
        pg.evaluate("async () => { await runFit(); }")
        got = pg.evaluate(CHECK)
    finally:
        pg.close()
    assert got["seal"] and got["frozen"] and got["engine"] == "local" and got["producer"] == "local", got
    for k in ("idx", "energies", "counts", "page", "viewEnergies", "viewChi2r", "viewRmse", "viewR", "viewBg", "model", "bgCert"):
        assert got[k] is True, (k, got)
    assert errors == [], errors
