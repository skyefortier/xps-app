"""Seal 1c step 5 (plan docs/superpowers/plans/2026-10-14-seal-1c-page.md §5, §7): the CONSUMERS read a sealed fit's
VIEW while its record describes the model shown (CURRENT / PENDING / UNCONFIRMED) and today's live preview once it
is STALE. The switch (`_SEAL_AUTHORITATIVE`) is still off in the shipped page; these tests turn it on.

Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import pytest

pytest.importorskip("playwright.sync_api")

from test_browser_bg_window_request import browser, server  # noqa: F401,E402
from test_browser_seal_requests import SCENARIOS, _setup  # noqa: E402

VERIFY = "async (retry) => { await _ensureVerified(_activeTab(), !!retry); }"
STATE = "() => sealedState(state.fitResult, _activeTab()).state"
TAMPER = """(src) => { const s = structuredClone(state.fitResult.seal); (new Function('s', src))(s);
  state.fitResult = { ...state.fitResult, seal: _makeSeal(s) }; }"""

# what the main chart and the residual panel draw, against the view
CHART = """(bgSub) => {
  document.getElementById('show-individual').checked = true;
  document.getElementById('show-envelope').checked = true;
  document.getElementById('show-residuals').checked = true;
  const t = document.getElementById('bg-sub-toggle'); if (t) t.checked = !!bgSub;
  updatePlot();
  const v = sealedState(state.fitResult, _activeTab()).view;
  const ds = state.chart.data.datasets, ys = d => d.data.map(p => p.y);
  const eq = (a, b) => a.length === b.length && a.every((x, i) => Object.is(x, b[i]));
  const env = ds.find(d => d.label === 'Fit' || d.label.startsWith('Fit ('));
  const data = ds.find(d => d.label === 'Data');
  const out = { bgSub: _isBgSubViewActive() };
  out.envelope = eq(ys(env), out.bgSub ? v.fittedSub : v.fittedY);
  out.liveEnvelope = eq(ys(env), evalAllPeaks(v.energies, state.peaks).map((m, i) => m + (out.bgSub ? 0 : v.background[i])));
  out.data = out.bgSub ? eq(ys(data), v.counts.map((c, i) => c - v.background[i])) : null;
  out.components = state.peaks.every(p => { const d = ds.find(x => x._peakId === p.id), c = _sealComponent(v, p);
    return d && c && eq(ys(d), c.y.map((y, i) => y + (out.bgSub ? 0 : v.background[i]))); });
  out.labels = state.peaks.map(p => ds.find(x => x._peakId === p.id).label);
  const res = state.residChart.data.datasets[0].data.map(p => p.y);
  out.residuals = eq(res, v.residuals.map((r, i) => { const d = v.counts[i];
    return Math.abs(d) < 1e-10 ? 0 : Math.max(-100, Math.min(100, (r / d) * 100)); }));
  return out;
}"""


def _page(browser, server, scenario="asymgl_linked_smart", local=False):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    _setup(pg, SCENARIOS[scenario])
    if local:
        pg.route("**/api/upload", lambda route: route.abort())
    pg.evaluate("async () => { await runFit(); }")
    pg.evaluate("() => { _SEAL_AUTHORITATIVE = true; }")
    return pg


@pytest.mark.parametrize("bg_sub", [False, True])
def test_the_chart_draws_the_record_pending_and_current(browser, server, bg_sub):  # noqa: F811
    pg = _page(browser, server)
    try:
        assert pg.evaluate(STATE) == "pending"
        got = pg.evaluate(CHART, bg_sub)
        assert got["bgSub"] is bg_sub and got["envelope"] and got["components"] and got["residuals"], got
        if bg_sub:
            assert got["data"], got
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == "current"
        got = pg.evaluate(CHART, bg_sub)
        assert got["envelope"] and got["components"] and got["residuals"], got
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_the_local_engine_record_is_drawn_too(browser, server):  # noqa: F811
    pg = _page(browser, server, "gauss_voigt_linear_avg3_window", local=True)
    try:
        assert pg.evaluate("() => state.fitResult.seal.engine") == "local"
        got = pg.evaluate(CHART, False)
        assert got["envelope"] and got["components"] and got["residuals"], got
        assert pg.evaluate("() => state.chart.data.datasets.some(d => d.label === 'Fit (local, starting point)')")
    finally:
        pg.close()


def test_an_edit_draws_the_live_preview_and_the_undo_the_record_again(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(VERIFY)
        pg.evaluate("() => { state.peaks[0].center += 0.05; }")
        assert pg.evaluate(STATE) == "stale"
        pg.evaluate("() => updatePlot()")
        env_is_record = pg.evaluate("""() => { const ds = state.chart.data.datasets, env = ds.find(d => d.label === 'Fit');
            const v = sealedState(state.fitResult, _activeTab()).view;
            return env.data.every((p, i) => Object.is(p.y, v.fittedY[i])); }""")
        assert env_is_record is False
        pg.evaluate("() => { state.peaks[0].center -= 0.05; }")
        got = pg.evaluate(CHART, False)
        assert got["envelope"] and got["components"], got
    finally:
        pg.close()


def test_a_failed_server_check_stops_drawing_the_record(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(TAMPER, "s.O.fitted_y[5] += 1e-6")
        got = pg.evaluate(CHART, False)
        assert got["envelope"], got                       # PENDING: the record as recorded
        pg.evaluate(VERIFY)                               # the verdict repaints the chart by itself
        assert pg.evaluate(STATE) == "stale"
        assert pg.evaluate("""() => { const env = state.chart.data.datasets.find(d => d.label === 'Fit');
            const v = state.fitResult.seal.O; return env.data.some((p, i) => !Object.is(p.y, v.fitted_y[i])); }""")
    finally:
        pg.close()


def test_recorded_support_verdicts_flag_while_the_record_describes_the_model(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(TAMPER, "s.O.individual_peaks[0].support = { ...s.O.individual_peaks[0].support, supported: false }")
        got = pg.evaluate(CHART, False)
        assert got["labels"][0].endswith("(" + pg.evaluate("() => _UNSUPPORTED_LABEL") + ")"), got
        assert pg.evaluate("() => _isUnsupported(state.peaks[0])") is True
        pg.evaluate(VERIFY)                               # the server's check fails: nothing established
        assert pg.evaluate(STATE) == "stale"
        assert pg.evaluate("() => _isUnsupported(state.peaks[0])") is False
        assert pg.evaluate("() => _currentSupport(state.peaks[0])") is None
    finally:
        pg.close()


def test_a_stack_draws_its_sources_record(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        got = pg.evaluate("""async () => {
            const src = _activeTab(); await _ensureVerified(src);
            const stack = tabManager.createStackTab();
            _addSpectrumToStack(stack, src.id); updatePlot();
            const v = sealedState(src.fitResult, src).view, rd = _getEntryRenderData(stack.entries[0]);
            const eq = (a, b) => a.length === b.length && a.every((x, i) => Object.is(x, b[i]));
            return { state: sealedState(src.fitResult, src).state, be: eq(rd.be, v.energies), bg: eq(rd.bg, v.background),
                     env: eq(rd.fittedY, v.fittedY), sub: eq(rd.fittedSub, v.fittedSub), raw: eq(rd.rawY, v.counts),
                     peaks: rd.peaks.every(pc => eq(pc.peakOnly, _sealComponent(v, pc.peak).y)) }; }""")
        assert got == {"state": "current", "be": True, "bg": True, "env": True, "sub": True, "raw": True, "peaks": True}, got
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_switch_off_is_todays_chart(browser, server):  # noqa: F811
    """With the switch off nothing reads the seal: a record that DISAGREES with today's fields changes nothing."""
    pg = _page(browser, server)
    try:
        pg.evaluate("() => { _SEAL_AUTHORITATIVE = false; }")
        pg.evaluate(TAMPER, "s.O.fitted_y = s.O.fitted_y.map(v => v + 1000); s.O.individual_peaks[0].params.area.value *= 2;"
                            " s.O.statistics.reduced_chi_square = 123.456")
        got = pg.evaluate("""() => { updatePlot(); renderResults();
            const env = state.chart.data.datasets.find(d => d.label === 'Fit'), fr = state.fitResult;
            return { env: env.data.every((p, i) => Object.is(p.y, fr.fittedY[i])), header: document.getElementById('fit-quality').textContent,
                     area: _componentArea(state.peaks[0], _areaGrid()) === _peakArea(state.peaks[0], _areaGrid()),
                     display: _sealedDisplay(fr), stats: _statsLiveState() }; }""")
        assert got["env"] and "123.46" not in got["header"] and got["area"] and got["display"] is None, got
        assert got["stats"] in ("current", "unverified"), got
    finally:
        pg.close()


# ── group 2: Results, header, status bar, sidebar, Quantify ──
PANELS = """() => {
  updatePlot(); renderResults(); renderPeakList();
  const fr = state.fitResult, v = sealedState(fr, _activeTab()).view;
  const ra = document.getElementById('results-area');
  const rows = Array.from(ra.querySelectorAll('.results-table tbody tr')).filter(r => !r.classList.contains('unsupported-row'));
  const comp = p => _sealComponent(v, p), model = p => v.model.find(m => String(m.id) === String(p.id));
  return {
    header: document.getElementById('fit-quality').textContent,
    sb: document.getElementById('sb-chi').textContent, sbR: document.getElementById('sb-runs').textContent,
    stat: ra.querySelector('div[style*="font-size:16px"]').textContent.trim(),
    chi: v.statistics.chi2r.toFixed(3), chi2: v.statistics.chi2r.toFixed(2),
    rPanel: (ra.querySelector('[data-xps-tip*="R-factor"], div[style*="R-factor"]') || {}).textContent || ra.textContent,
    rPct: v.rPanel ? v.rPanel.rPct.toFixed(1) : null,
    areas: rows.every((r, i) => r.children[3].textContent === comp(state.peaks[i]).area.toFixed(0)),
    centres: rows.every((r, i) => r.children[1].textContent.startsWith(model(state.peaks[i]).center.toFixed(3))),
    sealNote: (ra.querySelector('.stats-seal-note') || {}).textContent || null,
    staleBanner: !!ra.querySelector('[data-seal-stale]'),
    quantify: (document.querySelector('#quantify-area .quantify-seal-note') || {}).textContent || null,
    sidebarPct: state.peaks.map(p => { const vals = document.querySelectorAll('#peak-item-' + p.id + ' .peak-summary-val'); return vals[2] ? vals[2].textContent : null; }),
    wantPct: (() => { const a = state.peaks.map(p => comp(p).area), unsup = state.peaks.map(p => _sealUnsupported(v, p));
                      const tot = a.reduce((t, x, i) => t + (unsup[i] ? 0 : x), 0);
                      return a.map((x, i) => unsup[i] || !(tot > 0 && x > 0) ? '\u2014' : (x / tot * 100).toFixed(1) + '%'); })(),
    rPanelText: (ra.querySelector('[data-xps-tip]') || {}).textContent || '',
  };
}"""


def test_results_and_the_header_show_the_record_with_its_state(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        got = pg.evaluate(PANELS)
        assert "confirming" in got["header"] and got["chi2"] in got["header"], got
        assert got["sb"] == got["chi"] and got["stat"] == got["chi"], got
        assert got["areas"] and got["centres"], got
        assert got["sidebarPct"] == got["wantPct"], got          # the sidebar's area % from the record's areas
        assert got["rPct"] in got["rPanelText"] and "confirming" in got["rPanelText"] and "Excellent" not in got["rPanelText"], got
        assert got["sealNote"] and "confirming" in got["sealNote"], got
        assert got["quantify"] and "confirming" in got["quantify"], got
        assert "confirming" in got["sbR"] and got["rPct"] in got["sbR"], got
        pg.evaluate(VERIFY)                                   # the verdict repaints Results and the header
        got = pg.evaluate("() => ({ header: document.getElementById('fit-quality').textContent,"
                          " note: !!document.querySelector('#results-area .stats-seal-note'),"
                          " q: !!document.querySelector('#quantify-area .quantify-seal-note'),"
                          " sbR: document.getElementById('sb-runs').textContent })")
        assert "confirming" not in got["header"] and not got["note"] and not got["q"] and "confirming" not in got["sbR"], got
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_unconfirmed_says_why_and_a_failed_check_reports_nothing(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.route("**/api/verify-fit", lambda route: route.abort())
        pg.evaluate(VERIFY)
        got = pg.evaluate(PANELS)
        assert "unconfirmed: the server could not be reached" in got["header"], got
        assert got["sealNote"] and "unconfirmed" in got["sealNote"] and got["areas"], got
        pg.unroute("**/api/verify-fit")
        pg.evaluate(TAMPER, "s.O.statistics.chi_square *= 1.000001")
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == "stale"
        got = pg.evaluate("""() => { renderResults(); const ra = document.getElementById('results-area');
            return { header: document.getElementById('fit-quality').textContent, sb: document.getElementById('sb-chi').textContent,
                     banner: !!ra.querySelector('[data-seal-stale]'), sigma: ra.textContent.includes('±'),
                     q: (document.querySelector('#quantify-area .quantify-seal-note') || {}).textContent || '' }; }""")
        assert "check failed: statistics" in got["header"] and got["sb"] == "—", got
        assert got["banner"] and not got["sigma"] and "current model" in got["q"], got
    finally:
        pg.close()


def test_an_edit_makes_every_panel_say_model_changed(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(VERIFY)
        pg.evaluate("() => { state.peaks[0].fwhm *= 1.1; updatePlot(); }")   # updatePlot refreshes the panels
        got = pg.evaluate("""() => ({ header: document.getElementById('fit-quality').textContent,
            state: document.getElementById('results-area').getAttribute('data-stats-state'),
            banner: !!document.querySelector('#results-area [data-seal-stale]') })""")
        assert "model changed" in got["header"] and got["state"] == "stale" and got["banner"], got
    finally:
        pg.close()


# ── group 3: uncertainties, evidence, history, designation ──
def test_uncertainty_rules_read_the_records_sigma_and_bounds(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        # a recorded bound at the recorded value: the rule fires on the RECORD while it describes the model
        pg.evaluate(TAMPER, """const c = s.O.individual_peaks[0].params.center; c.min = c.value - 1e-6; c.max = c.value + 10;""")
        got = pg.evaluate("() => _validateUncertainties().warnings.join(' ')")
        assert "at lower bound" in got, got
        pg.evaluate(VERIFY)                               # the server's check fails: no rule is judged
        assert pg.evaluate(STATE) == "stale"
        assert pg.evaluate("() => _validateUncertainties().warnings.length") == 0
    finally:
        pg.close()


def test_the_starts_panel_and_use_this_solution_follow_the_state(browser, server):  # noqa: F811
    pg = _page(browser, server, "gauss_voigt_linear_avg3_window")
    try:
        # an alternative in the recorded starts (the server's check reads their form, not their values: "as recorded")
        pg.evaluate(TAMPER, """const st = s.O.starts, ips = s.O.individual_peaks;
            st.alternatives = [{ chi2r: st.fit.chi2r * 0.9, n_starts: 1,
              components: st.fit.components.map(c => { const ip = ips.find(q => q.id === c.id);
                return { ...c, area: ip.params.area.value,
                         params: Object.fromEntries(Object.entries(ip.params).filter(([k]) => k !== 'area').map(([k, v]) => [k, v.value])) }; }),
              largest_centre_shift_from_start: st.fit.largest_centre_shift_from_start, largest_fraction_difference_pp: 2.0 }];
            st.n_in_alternatives = 1;""")
        panel = """() => { renderResults(); const sp = document.querySelector('#results-area .starts-panel');
            return { state: sp.getAttribute('data-seal-state'), text: sp.textContent,
                     blocked: sp.querySelectorAll('.use-alt-blocked').length,
                     use: Array.from(sp.querySelectorAll('button')).filter(b => b.textContent === 'Use this solution').length }; }"""
        got = pg.evaluate(panel)
        assert got["state"] == "pending" and "confirming" in got["text"] and got["blocked"] == 1 and got["use"] == 0, got
        pg.route("**/api/verify-fit", lambda route: route.abort())
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == "unconfirmed"
        got = pg.evaluate(panel)
        assert got["state"] == "unconfirmed" and got["blocked"] == 1 and "unconfirmed" in got["text"], got
        # the handler itself refuses: no fit is started
        calls = []
        pg.on("request", lambda r: calls.append(r.url) if "/api/fit" in r.url else None)
        pg.evaluate("async () => { await useAlternative(0); }")
        assert calls == [], calls
        # Preview stays available
        pg.evaluate("() => previewAlternative(0)")
        assert pg.evaluate("() => !!(_historyPreview && _historyPreview.snapId === 'alt:0')")
        pg.unroute("**/api/verify-fit")
        pg.evaluate("async () => { await _ensureVerified(_activeTab(), true); }")   # check again
        assert pg.evaluate(STATE) == "current", pg.evaluate("() => { const s = sealedState(state.fitResult, _activeTab()); return [s.check, s.reason]; }")
        got = pg.evaluate(panel)
        assert got["state"] == "current" and got["blocked"] == 0 and got["use"] == 1 and "confirming" not in got["text"], got
        # an edit: the comparison no longer applies and the preview is dropped
        pg.evaluate("() => { state.peaks[0].fwhm *= 1.05; updatePlot(); }")
        got = pg.evaluate("() => ({ text: document.querySelector('#results-area .starts-panel').textContent, prev: !!_historyPreview })")
        assert "no longer applies" in got["text"] and not got["prev"], got
    finally:
        pg.close()


def test_history_rows_and_previews_are_the_snapshots_record(browser, server):  # noqa: F811
    pg = _page(browser, server)
    pg.evaluate(VERIFY)                                   # a record confirmed by the server reads "as recorded"
    try:
        got = pg.evaluate("""() => { const tab = _activeTab(), snap = tab.snapshots[0];
            _renderHistoryList(); const meta = document.querySelector('#hist-row-' + snap.id + ' .hist-row-chi');
            const v = _sealView(snap.fitResult.seal);
            _historyPreviewSnap(snap.id);
            const ds = state.chart.data.datasets.find(d => d._historyPreview);
            return { text: meta.textContent, sealed: meta.getAttribute('data-sealed'), chi: v.statistics.chi2r.toFixed(3),
                     label: ds.label, data: ds.data.every((p, i) => Object.is(p.x, v.energies[i]) && Object.is(p.y, v.fittedY[i])) }; }""")
        assert got["sealed"] == "1" and got["chi"] in got["text"] and "as recorded" in got["text"], got
        assert got["label"] == "Preview (as recorded)" and got["data"], got
    finally:
        pg.close()


def test_the_designation_is_the_records_engine(browser, server):  # noqa: F811
    pg = _page(browser, server, "gauss_voigt_linear_avg3_window", local=True)
    try:
        got = pg.evaluate("""() => { const fr = state.fitResult;
            const out = [_isLocalFit(fr), !!_provenanceOf({ fitResult: fr })];
            state.fitResult = { ...fr, engine: 'server', objective: undefined };   // today's fields say server
            out.push(_isLocalFit(state.fitResult), _isLocalModel());
            return out; }""")
        assert got == [True, True, True, True], got
    finally:
        pg.close()


# ── group 4: exports ──
CAPTURE = """() => { window.__files = {};
  window._downloadBlob = (blob, name) => { blob.text().then(t => { window.__files[name] = t; }); };
  URL.createObjectURL = b => { b.text().then(t => { window.__files['tsv'] = t; }); return 'blob:x'; };
  HTMLAnchorElement.prototype.click = function () {};
  window._pngWithText = async (blob, k, text) => { window.__files['png-record'] = text; return blob; }; }"""
WAIT = "(name) => !!(window.__files && window.__files[name])"


def _export(pg, call, name):
    pg.evaluate("() => { window.__files = {}; }")
    pg.evaluate(call)
    pg.wait_for_function(WAIT, arg=name, timeout=20000)
    return pg.evaluate("(n) => window.__files[n]", name)


def test_tsv_and_csv_export_the_record_and_its_state(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(CAPTURE)
        tsv = _export(pg, "() => exportResults()", "tsv")
        lines = tsv.split("\n")
        assert lines[0].startswith("# Fit state: PENDING"), lines[:2]
        first = lines[2].split("\t")
        want = pg.evaluate("""() => { const v = sealedState(state.fitResult, _activeTab()).view, i = 0;
            return [v.energies[i].toFixed(4), v.counts[i].toFixed(2), v.background[i].toFixed(2), (v.counts[i] - v.background[i]).toFixed(2),
                    v.fittedSub[i].toFixed(2), v.residuals[i].toFixed(2), ...state.peaks.map(p => _sealComponent(v, p).y[i].toFixed(2))]; }""")
        assert first == want, (first, want)
        assert "Fit method" in tsv
        pg.evaluate(VERIFY)
        csv = _export(pg, "() => exportFitTable('csv')", "fit_results.csv")
        assert "# Fit state: CURRENT" in csv, csv[:400]
        chi = pg.evaluate("() => sealedState(state.fitResult, _activeTab()).view.statistics.chi2r.toFixed(4)")
        assert ("Chi-squared reduced: " + chi) in csv, csv[:400]
        centre = pg.evaluate("() => sealedState(state.fitResult, _activeTab()).view.model[0].center.toFixed(4)")
        assert '"' + centre + '"' in csv
        # an edit: the live recompute, labelled, and no fit state line
        pg.evaluate("() => { state.peaks[0].center += 0.05; }")
        tsv = _export(pg, "() => exportResults()", "tsv")
        assert "# Fit state: STALE (edited)" in tsv and "model has changed" in tsv, tsv[:300]   # the live recompute, labelled
    finally:
        pg.close()


def test_the_figure_record_and_the_fit_file_carry_the_record(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(CAPTURE)
        rec = _export(pg, "() => _doPublicationExport()", "png-record")
        assert '"sealState":"PENDING' in rec and '"engine":"server"' in rec, rec[:300]
        pg.evaluate(VERIFY)
        fj = _export(pg, "() => _doSaveFit()", pg.evaluate("() => (document.getElementById('save-fname').value.trim() || 'spectrum') + '.fit.json'"))
        import json
        stats = json.loads(fj)["fitStatistics"]
        chi = pg.evaluate("() => sealedState(state.fitResult, _activeTab()).view.statistics.chi2r")
        assert stats["chiReduced"] == chi and stats["sealState"] == "CURRENT" and stats["engine"] == "server", stats
        assert stats["record"]["engine"] == "server"
    finally:
        pg.close()



# ── step 5 round 1 fixes ──
def test_the_stack_updates_in_place_from_the_record_and_follows_a_verdict(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        # a record whose subtracted envelope is NOT fitted_y − background (the stack must draw O's own array) and whose
        # first component is recorded unsupported (PENDING applies recorded verdicts)
        pg.evaluate(TAMPER, "s.O.fitted_sub = s.O.fitted_sub.map(v => v + 7); "
                            "s.O.individual_peaks[0].support = { ...s.O.individual_peaks[0].support, supported: false }")
        got = pg.evaluate("""() => { const src = _activeTab(); tabManager._syncActiveToRecord();
            const stack = tabManager.createStackTab(); _addSpectrumToStack(stack, src.id);
            document.getElementById('bg-sub-toggle').checked = true;
            const env = () => state.chart.data.datasets.find(d => d._stackKey && d._stackKey.endsWith(':env'));
            const peak0 = () => state.chart.data.datasets.find(d => d._stackKey && d._stackKey.endsWith(':peak:' + src.peaks[0].id));
            const O = src.fitResult.seal.O;
            _updateStackChart(stack, { invalidate: 'datasets' });
            const built = env().data.every((p, i) => Object.is(p.y, O.fitted_sub[i]));
            stack.verticalOffset = 0; _updateStackChart(stack);           // the in-place path (a slider)
            const inPlace = env().data.every((p, i) => Object.is(p.y, O.fitted_sub[i]));
            return { built, inPlace, label: peak0().label, envLabel: env().label, srcId: src.id }; }""")
        assert got["built"] and got["inPlace"], got
        assert got["label"].endswith("(" + pg.evaluate("() => _UNSUPPORTED_LABEL") + ")") and "confirming" in got["envLabel"], got
        legend = pg.evaluate("() => Array.from(document.querySelectorAll('#stack-legend-list .name')).map(e => e.textContent)")
        assert any("fit confirming" in t for t in legend), legend
        # the server's check fails while the stack is shown: the verdict repaints it in place — no flag, "no longer applies"
        pg.evaluate("async (id) => { await _ensureVerified(tabManager._getTab(id)); }", got["srcId"])
        after = pg.evaluate("""(id) => { const ds = state.chart.data.datasets, t = tabManager._getTab(id);
            return { peak: ds.find(d => d._stackKey && d._stackKey.endsWith(':peak:' + t.peaks[0].id)).label,
                     env: ds.find(d => d._stackKey && d._stackKey.endsWith(':env')).label }; }""", got["srcId"])
        assert "(" + pg.evaluate("() => _UNSUPPORTED_LABEL") + ")" not in after["peak"] and "no longer applies" in after["env"], after
        # what the student SEES: the stack legend (the chart's own legend is hidden) — repainted by the verdict
        legend = pg.evaluate("() => Array.from(document.querySelectorAll('#stack-legend-list .name')).map(e => e.textContent)")
        assert any("fit no longer applies (record does not hold" in t for t in legend), legend
    finally:
        pg.close()


def test_history_judges_each_snapshot_by_its_own_record(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(VERIFY)
        # a later edit does not make the snapshot's record fail: it is judged by itself, not by the live model
        pg.evaluate("() => { state.peaks[0].center += 0.2; updatePlot(); showHistoryModal(); }")
        row = pg.evaluate("() => document.querySelector('#history-list .hist-row-chi').textContent")
        assert "as recorded" in row, row
        # a snapshot whose record does not hold: its row says so, without statistics, and its preview draws no record
        pg.evaluate("""() => { const t = _activeTab(), snap = t.snapshots[0], s = structuredClone(snap.fitResult.seal);
            s.O.fitted_y[2] += 1e-6; snap.fitResult = { ...snap.fitResult, seal: _makeSeal(s) }; _renderHistoryList(); }""")
        pg.wait_for_function("() => /record does not hold/.test(document.querySelector('#history-list .hist-row-meta').textContent)", timeout=30000)
        got = pg.evaluate("""() => { const t = _activeTab(), snap = t.snapshots[0]; _historyPreviewSnap(snap.id);
            const ds = state.chart.data.datasets.find(d => d._historyPreview);
            return { meta: document.querySelector('#history-list .hist-row-meta').textContent, label: ds.label }; }""")
        assert "χ" not in got["meta"] and "record does not hold" in got["label"], got
    finally:
        pg.close()


def test_history_shows_an_unconfirmed_snapshot_as_unconfirmed(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.route("**/api/verify-fit", lambda route: route.abort())
        pg.evaluate("() => { showHistoryModal(); }")
        pg.wait_for_function("() => /unconfirmed/.test(document.querySelector('#history-list .hist-row-chi').textContent)", timeout=30000)
    finally:
        pg.close()


@pytest.mark.parametrize("local", [False, True])
def test_a_fit_file_keeps_its_engine_through_a_save_and_import(browser, server, local):  # noqa: F811
    pg = _page(browser, server, "gauss_voigt_linear_avg3_window", local=local)
    try:
        pg.evaluate(CAPTURE)
        name = pg.evaluate("() => (document.getElementById('save-fname').value.trim() || 'spectrum') + '.fit.json'")
        fj = _export(pg, "() => _doSaveFit()", name)
        import json
        data = json.loads(fj)
        assert data["fitStatistics"]["reportable"] is (not local), data["fitStatistics"]
        got = pg.evaluate("""(text) => { const d = JSON.parse(text); tabManager.createTab('imp', state.rawBE.slice(), state.rawIntensity.slice());
            _applyFitJSON(d); return { localModel: _isLocalModel(), prov: _activeTab().modelProvenance }; }""", fj)
        assert got["localModel"] is local, got
    finally:
        pg.close()


def test_a_stale_sealed_fit_exports_its_failed_check(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(CAPTURE)
        pg.evaluate(TAMPER, "s.O.statistics.chi_square *= 1.000001")
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == "stale"
        tsv = _export(pg, "() => exportResults()", "tsv")
        assert "# Fit state: STALE (statistics)" in tsv and "record does not hold (statistics)" in tsv, tsv[:400]
        rec = _export(pg, "() => _doPublicationExport()", "png-record")
        assert '"sealState":"STALE (statistics)' in rec, rec[:300]
    finally:
        pg.close()


def test_xlsx_carries_the_state_and_the_records_values(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        if not pg.evaluate("() => typeof XLSX !== 'undefined'"):
            pytest.skip("the XLSX library did not load (offline)")
        got = pg.evaluate("""() => { let info = null, res = null; const w = XLSX.writeFile;
            XLSX.writeFile = (wb) => { info = XLSX.utils.sheet_to_json(wb.Sheets['Info'], { header: 1 });
                                       res = XLSX.utils.sheet_to_json(wb.Sheets['Fit Results'], { header: 1 }); };
            try { exportFitTable('xlsx'); } finally { XLSX.writeFile = w; }
            const v = sealedState(state.fitResult, _activeTab()).view;
            return { info, res, centre: v.model[0].center.toFixed(4), area: _sealComponent(v, state.peaks[0]).area.toFixed(2) }; }""")
        flat = [" ".join(str(c) for c in r) for r in got["info"]]
        assert any(r.startswith("Fit state PENDING") for r in flat), flat
        row = got["res"][1]
        assert str(row[2]) == got["centre"] and str(row[8]) == got["area"], (row, got)
    finally:
        pg.close()



def _seal_only(pg, src=None):
    """The result as a LOADED sealed fit holds it: the seal and nothing else (no legacy copy to fall back on)."""
    pg.evaluate("(src) => { const s = structuredClone(state.fitResult.seal); if (src) (new Function('s', src))(s);"
                " state.fitResult = Object.freeze({ seal: _makeSeal(s) }); }", src)


@pytest.mark.parametrize("fmt", ["csv", "xlsx"])
def test_a_stale_seal_only_fit_exports_its_warning_without_a_statistic(browser, server, fmt):  # noqa: F811
    pg = _page(browser, server)
    try:
        if fmt == "xlsx" and not pg.evaluate("() => typeof XLSX !== 'undefined'"):
            pytest.skip("the XLSX library did not load (offline)")
        pg.evaluate(CAPTURE)
        _seal_only(pg, "s.O.statistics.chi_square *= 1.000001")
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == "stale"
        if fmt == "csv":
            csv = _export(pg, "() => exportFitTable('csv')", "fit_results.csv")
            assert "# WARNING:" in csv and "# Fit state: STALE (statistics)" in csv and "Chi-squared reduced:" not in csv, csv[:500]
        else:
            info = pg.evaluate("""() => { let info = null; const w = XLSX.writeFile; XLSX.writeFile = (wb) => { info = XLSX.utils.sheet_to_json(wb.Sheets['Info'], { header: 1 }); };
                try { exportFitTable('xlsx'); } finally { XLSX.writeFile = w; } return info; }""")
            flat = [" ".join(str(c) for c in r) for r in info]
            assert any(r.startswith("WARNING") for r in flat) and any(r.startswith("Fit state STALE (statistics)") for r in flat), flat
            assert not any(r.startswith("Chi-squared") for r in flat), flat
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_seal_only_server_fit_shows_its_engine_card(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        _seal_only(pg)
        pg.evaluate(VERIFY)
        got = pg.evaluate("() => { renderResults(); return document.getElementById('results-area').textContent; }")
        assert "lmfit" in got, got[:300]
    finally:
        pg.close()


def test_an_open_preview_follows_its_records_verdict(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        # a snapshot whose record does not hold, previewed BEFORE its check answers: the verdict repaints the preview
        held = []
        pg.route("**/api/verify-fit", lambda route: held.append(route))
        pg.evaluate("""() => { const t = _activeTab(), snap = t.snapshots[0], s = structuredClone(snap.fitResult.seal);
            s.O.fitted_y[2] += 1e-6; snap.fitResult = { ...snap.fitResult, seal: _makeSeal(s) }; showHistoryModal(); _historyPreviewSnap(snap.id); }""")
        assert "confirming" in pg.evaluate("() => state.chart.data.datasets.find(d => d._historyPreview).label")
        pg.wait_for_timeout(300)
        for r in held:
            r.continue_()
        pg.unroute("**/api/verify-fit")
        pg.wait_for_function("() => /record does not hold/.test(state.chart.data.datasets.find(d => d._historyPreview).label)", timeout=30000)
        # and its CURVE is no longer the record's envelope (a model-only preview on today's grid)
        assert pg.evaluate("""() => { const ds = state.chart.data.datasets.find(d => d._historyPreview), O = _activeTab().snapshots[0].fitResult.seal.O;
            return ds.data.some((p, i) => !Object.is(p.y, O.fitted_y[i])) || ds.data.length !== O.fitted_y.length; }""")
    finally:
        pg.close()


def test_an_open_history_panel_follows_the_active_tab(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate("() => showHistoryModal()")
        assert pg.evaluate("() => document.querySelectorAll('#history-list .hist-row').length") >= 1
        pg.evaluate("() => tabManager.createTab('B', state.rawBE.slice(), state.rawIntensity.slice())")
        assert pg.evaluate("() => document.querySelectorAll('#history-list .hist-row').length") == 0
    finally:
        pg.close()



def test_returning_to_a_tab_whose_result_is_only_its_seal(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        _seal_only(pg)
        pg.evaluate(VERIFY)
        got = pg.evaluate("""() => { const a = _activeTab();
            tabManager.createTab('B', state.rawBE.slice(), state.rawIntensity.slice());
            tabManager.activateTab(a.id);
            return { frozen: Object.isFrozen(state.fitResult), keys: Object.keys(state.fitResult), state: sealedState(state.fitResult, a).state,
                     header: document.getElementById('fit-quality').textContent }; }""")
        assert got["frozen"] and got["keys"] == ["seal"] and got["state"] == "current" and "\u03c7" in got["header"], got
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_real_undo_of_an_edit_returns_the_record(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(VERIFY)
        pg.evaluate("() => { pushUndo(); state.peaks[0].center += 0.05; updatePlot(); }")
        assert pg.evaluate(STATE) == "stale"
        pg.evaluate("() => undo()")
        assert pg.evaluate(STATE) == "current"
        got = pg.evaluate(CHART, False)
        assert got["envelope"] and got["components"], got
    finally:
        pg.close()


def test_sigma_is_the_records(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(TAMPER, "s.O.individual_peaks[0].params.center.stderr = 0.123456")   # PENDING: the record as recorded
        txt = pg.evaluate("() => { renderResults(); return document.querySelector('#results-area .results-table tbody tr').textContent; }")
        assert "\u00b1 0.123" in txt, txt
    finally:
        pg.close()


def test_legacy_duplicates_that_disagree_are_never_read(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(VERIFY)
        pg.evaluate("""() => { const fr = state.fitResult;
            state.fitResult = { ...fr, chiReduced: 999.5, rmse: 999.5, rFactor: { rPct: 99, level: 'red' },
                                fittedY: fr.fittedY.map(v => v + 50), bgIntensity: fr.bgIntensity.map(v => v + 50),
                                backendResult: { ...fr.backendResult, individual_peaks: fr.backendResult.individual_peaks.map(ip => ({ ...ip, params: { ...ip.params, center: { ...ip.params.center, stderr: 9.99 } } })) } }; }""")
        got = pg.evaluate(CHART, False)
        assert got["envelope"] and got["components"] and got["residuals"], got
        txt = pg.evaluate("() => { renderResults(); return [document.getElementById('fit-quality').textContent, document.getElementById('results-area').textContent]; }")
        assert "999.5" not in txt[0] and "999.5" not in txt[1] and "9.99" not in txt[1], txt
    finally:
        pg.close()


def test_the_figure_annotates_the_record_and_its_state(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        spy = """() => { window.__texts = []; const f = CanvasRenderingContext2D.prototype.fillText;
            CanvasRenderingContext2D.prototype.fillText = function (t, ...a) { window.__texts.push(String(t)); return f.call(this, t, ...a); };
            window._downloadBlob = () => {}; window._pngWithText = async (b) => b; }"""
        pg.evaluate(spy)
        pg.evaluate("() => _doPublicationExport()")
        texts = pg.evaluate("() => window.__texts")
        chi = pg.evaluate("() => sealedState(state.fitResult, _activeTab()).view.statistics.chi2r.toFixed(3)")
        assert any(chi in t and "not yet confirmed" in t for t in texts), texts
        pg.evaluate(TAMPER, "s.O.statistics.chi_square *= 1.000001")
        pg.evaluate(VERIFY)
        pg.evaluate("() => { window.__texts = []; _doPublicationExport(); }")
        texts = pg.evaluate("() => window.__texts")
        assert any("record does not hold (statistics)" in t for t in texts), texts
    finally:
        pg.close()


def test_the_status_bar_range_and_a_stale_fit_file_read_the_record(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        _seal_only(pg)
        pg.evaluate(VERIFY)
        got = pg.evaluate("""() => { const a = _activeTab(); tabManager.createTab('B', state.rawBE.slice(), state.rawIntensity.slice());
            tabManager.activateTab(a.id); const v = sealedState(state.fitResult, a).view;
            return [document.getElementById('sb-roi').textContent, _arrMin(v.energies).toFixed(1), _arrMax(v.energies).toFixed(1)]; }""")
        assert got[1] in got[0] and got[2] in got[0], got
        # a stale record with a disagreeing legacy duplicate: the fit file writes no statistic
        pg.evaluate(CAPTURE)
        pg.evaluate("() => { state.fitResult = { ...state.fitResult.seal ? { seal: state.fitResult.seal } : {}, chiReduced: 999.5 }; state.peaks[0].center += 0.05; }")
        name = pg.evaluate("() => (document.getElementById('save-fname').value.trim() || 'spectrum') + '.fit.json'")
        import json
        stats = json.loads(_export(pg, "() => _doSaveFit()", name))["fitStatistics"]
        assert stats["chiReduced"] is None and stats["sealState"].startswith("STALE"), stats
    finally:
        pg.close()


def test_a_stale_sealed_fit_draws_the_same_preview_with_or_without_legacy_copies(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        got = pg.evaluate("""() => { const fr = state.fitResult;
            const draw = (x) => { state.fitResult = x; updatePlot(); const ds = state.chart.data.datasets;
              return JSON.stringify(ds.filter(d => d.label !== 'Data').map(d => [d.label, d.data.map(p => [p.x, p.y])])); };
            state.peaks[0].center += 0.05;                                   // STALE (edited)
            const poisoned = { ...fr, be: fr.be.map(x => x + 1), bgIntensity: fr.bgIntensity.map(v => v + 99),
                               bgSubtracted: fr.bgSubtracted.map(v => v + 99), fittedY: fr.fittedY.map(v => v + 99) };
            const a = draw(Object.freeze({ seal: fr.seal })), b = draw(poisoned);
            return [sealedState(state.fitResult, _activeTab()).state, a === b]; }""")
        assert got == ["stale", True], got
    finally:
        pg.close()


def test_a_poisoned_legacy_r_factor_is_never_shown(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate(VERIFY)
        pg.evaluate("() => { state.fitResult = { ...state.fitResult, rFactor: { rPct: 99.9, level: 'red' } }; updatePlot(); renderResults(); _updateRFactorUI(state.fitResult.rFactor); }")
        txt = pg.evaluate("() => [document.getElementById('sb-runs').textContent, document.getElementById('results-area').textContent]")
        assert "99.9" not in txt[0] and "99.9" not in txt[1], txt
    finally:
        pg.close()


def test_the_uncertainty_rules_read_the_records_sigma(browser, server):  # noqa: F811
    pg = _page(browser, server, "gauss_voigt_linear_avg3_window")
    try:
        # a sigma the server could not estimate, recorded in O (the legacy copy keeps the real one): rule 2 fires only
        # if the RECORD is read — for the parameter whose fitted value barely moved from its start
        got = pg.evaluate("""() => { const s = structuredClone(state.fitResult.seal), v = _sealView(state.fitResult.seal);
            let target = null;
            for (const ip of s.O.individual_peaks) for (const k of ['center', 'fwhm']) {
              const start = s.R.pageModel.find(q => String(q.id) === String(ip.id))[k], val = ip.params[k] && ip.params[k].value;
              if (!target && ip.params[k] && ip.params[k].vary && Math.abs(val - start) / Math.abs(start) < 0.001) { target = [ip, k]; } }
            if (!target) return null;
            target[0].params[target[1]].stderr = null;
            state.fitResult = { ...state.fitResult, seal: _makeSeal(s) };
            return _validateUncertainties().warnings.join(' '); }""")
        if got is None:
            pytest.skip("no parameter in this fit stayed within 0.1 % of its start")
        assert "could not be estimated" in got, got
    finally:
        pg.close()
