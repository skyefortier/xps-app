"""Real browser, real server (owner 2026-10-11): endpoint averaging outside the field's own 1-50
is REFUSED, never clamped — Run Fit says so in plain words before any request, undo entry or
local fit; a value in range fits as before; Batch Fit leaves that target unfitted with the
reason. Skips cleanly when Playwright / Chromium / gunicorn are absent."""
import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import _new_page, browser, server  # noqa: E402,F401
from test_browser_background_not_converged import PEAK_TAB  # noqa: E402

SPY = """() => { window.__api = []; window.__notes = [];
    const o = window.fetch; window.fetch = (url, opts) => { if (String(url).includes('/api/')) window.__api.push(String(url)); return o(url, opts); };
    const n = window.notify; window.notify = (m, k, ...r) => { window.__notes.push([k, m]); return n(m, k, ...r); }; }"""
RUN = """async () => { await runFit(); }"""


@pytest.mark.parametrize("text", ["1e21", "0", "51", "2.5", "1e1"])
def test_run_fit_refuses_an_averaging_outside_1_to_50(browser, server, text):
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("t => { document.getElementById('bg-endpoint-avg').value = t; }", text)
        before = pg.evaluate("() => ({ peaks: JSON.stringify(state.peaks), undo: (_activeTab().undoStack || []).length })")
        pg.evaluate(SPY)
        pg.evaluate(RUN)
        got = pg.evaluate("() => ({ api: window.__api, notes: window.__notes, fit: !!state.fitResult, peaks: JSON.stringify(state.peaks), undo: (_activeTab().undoStack || []).length })")
    finally:
        pg.close()
    assert got["api"] == [], "no upload, no request"
    assert got["undo"] == before["undo"] and got["peaks"] == before["peaks"] and not got["fit"]
    assert ["red", f'Fit not run: endpoint averaging must be a whole number from 1 to 50 (it is "{text}").'] in got["notes"], got["notes"]


def test_a_value_in_range_fits_as_before(browser, server):
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("() => { document.getElementById('bg-endpoint-avg').value = '50'; }")
        pg.evaluate(SPY)
        pg.evaluate(RUN)
        got = pg.evaluate("() => ({ fit: !!state.fitResult && state.fitResult.record.engine, notes: window.__notes, k: state.fitResult && state.fitResult.record.backgroundVerdict.effect.k })")
    finally:
        pg.close()
    assert got["fit"] == "server", got["notes"]
    assert not any("endpoint averaging" in m for _, m in got["notes"])
    assert got["k"] == 50


def test_batch_fit_leaves_the_target_unfitted_with_the_reason(browser, server):
    pg = _new_page(browser, server)
    try:
        ids = pg.evaluate("""() => {
            const mk = amp => { const be = [], inten = [];
                for (let i = 0; i < 120; i++) { const x = 520 + i * 0.25; be.push(x);
                    inten.push(1000 + amp * Math.exp(-Math.pow(x - 535, 2) / (2 * 1.5 * 1.5)) + (x > 535 ? 200 : 0)); }
                return { be, inten }; };
            const s = mk(8000);
            tabManager.createTab('SRC', s.be, s.inten);
            const srcId = tabManager.activeId;
            document.getElementById('bg-endpoint-avg').value = '1e21';
            addPeak({ center: 535, fwhm: 3, amplitude: 8000 });
            const t = mk(7000);
            tabManager.createTab('TGT', t.be, t.inten);
            const tgtId = tabManager.activeId;
            tabManager.activateTab(srcId);
            return { srcId, tgtId };
        }""")
        pg.evaluate("() => showPropagateModal()")
        pg.wait_for_timeout(100)
        pg.evaluate("""id => { const c = document.querySelector('.prop-chk[data-id="' + id + '"]'); if (c) c.checked = true; }""", ids["tgtId"])
        pg.evaluate("async () => { await runPropagation(); }")
        got = pg.evaluate("""id => ({ fit: !!tabManager._getTab(id).fitResult, ep: tabManager._getTab(id).ui.endpointAvg,
                                     summary: document.getElementById('propagate-summary').textContent })""", ids["tgtId"])
    finally:
        pg.close()
    assert got["ep"] == "1e21", "the source's averaging reached the target (propagateFitUi)"
    assert not got["fit"], "the target is not fitted"
    assert 'endpoint averaging must be a whole number from 1 to 50 (it is "1e21")' in got["summary"], got["summary"]
