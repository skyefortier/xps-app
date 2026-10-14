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
