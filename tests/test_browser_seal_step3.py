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
  // STRICT where the two must be the same values (numbers by Object.is, the same own keys, undefined included);
  // the RECORD rule (_jsonEqual: the JSON form) only where one side travelled as JSON (the wire body)
  const eq = (a, b) => {
    if (typeof a === 'number' || typeof b === 'number') return Object.is(a, b);
    if (a === null || b === null || typeof a !== 'object' || typeof b !== 'object') return a === b;
    if (Array.isArray(a) !== Array.isArray(b)) return false;
    const ka = Object.keys(a), kb = Object.keys(b);
    return ka.length === kb.length && ka.every(k => Object.hasOwn(b, k) && eq(a[k], b[k]));
  };
  const roi = getROIData();
  const out = {
    seal: true, frozen: Object.isFrozen(seal) && Object.isFrozen(seal.R) && Object.isFrozen(seal.O) && Object.isFrozen(R.pageModel[0]),
    engine: seal.engine, producer: seal.producer,
    idx: eq(R.idx, roi.idx), energies: eq(R.energies, roi.be), counts: eq(R.counts, roi.inten),
    page: !!(R.page && R.page.software && R.page.page && R.page.page.page_sha256),
    viewEnergies: eq(v.energies, fr.be), viewChi2r: v.statistics.chi2r === fr.chiReduced,
  };
  if (seal.engine === 'server') {
    out.request = _jsonEqual(R.request, window.__sent);   // the wire body, as the server received it
    out.step0 = eq(_buildFitRequest(seal.producer, R.pageModel, R.context0.live, R.energies,
                                    { requireComponent: R.context0.producer.require_component }), R.request);   // strictly: rebuilt from R
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
            // STRICT identity (numbers by Object.is, the same own keys, undefined included): all three sides are
            // in-page objects that never travelled as JSON
            const eq = (a, b) => {
              if (typeof a === 'number' || typeof b === 'number') return Object.is(a, b);
              if (a === null || b === null || typeof a !== 'object' || typeof b !== 'object') return a === b;
              if (Array.isArray(a) !== Array.isArray(b)) return false;
              const ka = Object.keys(a), kb = Object.keys(b);
              return ka.length === kb.length && ka.every(k => Object.hasOwn(b, k) && eq(a[k], b[k]));
            };
            const d = deriveAutoFit(E.R.pageModel, E.R.context0.live, E.O);
            const step0 = (r) => eq(_buildFitRequest('autoFit', r.pageModel, r.context0.live, r.energies,
                                     { requireComponent: r.context0.producer.require_component }), r.request);
            return { seal: true, producer: seal.producer, hasE: !!(E && E.R && E.O), frozen: Object.isFrozen(E.O),
                     step0R1: step0(E.R), step0R2: step0(R), derived: _sameModel(d.pageModel, R.pageModel),
                     derivedCtx: eq(d.ctx, R.context0.live),
                     O2: eq(seal.O, state.fitResult.backendResult) }; }""")
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


def test_use_this_solution_seals_the_alternative_start_and_the_choice(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        pg.evaluate("async () => { await runFit(); }")
        # an alternative in today's starts evidence (what Use this solution reads until step 7), from the fit itself
        pg.evaluate("""() => { const fr = state.fitResult, st = structuredClone(fr.starts), ips = fr.backendResult.individual_peaks;
            st.alternatives = [{ chi2r: st.fit.chi2r * 0.9, n_starts: 1,
              components: st.fit.components.map(c => { const ip = ips.find(q => q.id === c.id);
                return { ...c, area: ip.params.area.value, params: { center: ip.params.center.value + 0.05, amplitude: ip.params.amplitude.value, fwhm: ip.params.fwhm.value } }; }),
              largest_centre_shift_from_start: st.fit.largest_centre_shift_from_start, largest_fraction_difference_pp: 1 }];
            state.fitResult = { ...fr, starts: st }; }""")
        start = pg.evaluate("() => _altPeaks(_currentAlternative(0))")
        pg.evaluate("async () => { await useAlternative(0); }")
        got = pg.evaluate("""(start) => { const seal = state.fitResult.seal;
            return { producer: seal.producer, chosen: seal.D.chosenAlternative, sameStart: _sameModel(seal.R.pageModel, start),
                     step0: _jsonEqual(_buildFitRequest(seal.producer, seal.R.pageModel, seal.R.context0.live, seal.R.energies,
                                       { requireComponent: seal.R.context0.producer.require_component }), seal.R.request),
                     viewChosen: _sealView(seal).chosenAlternative }; }""", start)
    finally:
        pg.close()
    assert got["producer"] == "useSolution" and got["sameStart"] and got["step0"], got
    assert got["chosen"] and got["chosen"] == got["viewChosen"] and "toChi" in got["chosen"], got
    assert errors == [], errors


def test_batch_fit_seals_each_target_from_its_own_data_and_context(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    try:
        ids = pg.evaluate("""() => {
            const mk = (amp, off) => { const be = [], inten = [];
                for (let i = 0; i < 80; i++) { const x = 520 + i * 0.25; be.push(x);
                    inten.push(1000 + off + amp * Math.exp(-Math.pow(x - 530, 2) / (2 * 0.9 * 0.9)) + 37 * Math.sin(i)); }
                return { be, inten }; };
            const s = mk(8000, 0); tabManager.createTab('SRC', s.be, s.inten); const srcId = tabManager.activeId;
            document.getElementById('bg-type').value = 'linear';
            addPeak({ center: 530, fwhm: 2, amplitude: 8000 });
            const t = mk(5000, 200); tabManager.createTab('TGT', t.be, t.inten); const tgtId = tabManager.activeId;
            tabManager.activateTab(srcId);
            return { srcId, tgtId }; }""")
        pg.evaluate("() => showPropagateModal()")
        pg.evaluate("(id) => { const c = document.querySelector('.prop-chk[data-id=\"' + id + '\"]'); if (c) c.checked = true; }", ids["tgtId"])
        pg.evaluate("async () => { await runPropagation(); }")
        got = pg.evaluate("""(id) => { const t = tabManager._getTab(id), seal = t.fitResult && t.fitResult.seal;
            if (!seal) return { seal: false };
            if (tabManager.activeId === id) tabManager._syncActiveToRecord();
            const st = sealedState(t.fitResult, t);
            return { seal: true, engine: seal.engine, producer: seal.producer, state: st.state, check: st.check,
                     counts: _jsonEqual(seal.R.counts, _roiSelect(t.rawBE, t.rawIntensity, t.ccShift, t.ui.roiMin, t.ui.roiMax).inten),
                     ctx: _jsonEqual(seal.R.context0.live, _contextOf(t)) }; }""", ids["tgtId"])
    finally:
        pg.close()
    assert got["seal"] and got["engine"] == "local" and got["producer"] == "batch", got
    assert got["counts"] and got["ctx"] and got["state"] == "current", got
    assert errors == [], errors
