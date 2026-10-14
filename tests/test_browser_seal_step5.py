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
    pg = _page(browser, server)
    try:
        pg.evaluate("() => { _SEAL_AUTHORITATIVE = false; }")
        assert pg.evaluate("() => _sealedDisplay(state.fitResult)") is None
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
    sidebarPct: state.peaks.map(p => document.querySelector('#peak-item-' + p.id + ' .peak-summary-val:nth-of-type(3)')),
  };
}"""


def test_results_and_the_header_show_the_record_with_its_state(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        got = pg.evaluate(PANELS)
        assert "confirming" in got["header"] and got["chi2"] in got["header"], got
        assert got["sb"] == got["chi"] and got["stat"] == got["chi"], got
        assert got["areas"] and got["centres"], got
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
