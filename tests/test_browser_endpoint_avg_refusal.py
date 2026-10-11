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


def test_batch_fit_refuses_before_any_target_is_changed(browser, server):
    # Codex averaging round 1: the refusal used to come after the target's undo entry, peaks,
    # settings and charge correction were replaced and its fit cleared
    pg = _new_page(browser, server)
    try:
        ids = pg.evaluate("""() => {
            const mk = amp => { const be = [], inten = [];
                for (let i = 0; i < 120; i++) { const x = 520 + i * 0.25; be.push(x);
                    inten.push(1000 + amp * Math.exp(-Math.pow(x - 535, 2) / (2 * 1.5 * 1.5)) + (x > 535 ? 200 : 0)); }
                return { be, inten }; };
            const t = mk(7000);
            tabManager.createTab('TGT', t.be, t.inten);
            const tgtId = tabManager.activeId;
            addPeak({ center: 535.2, fwhm: 2.5, amplitude: 6000 });
            const s = mk(8000);
            tabManager.createTab('SRC', s.be, s.inten);
            const srcId = tabManager.activeId;
            addPeak({ center: 535, fwhm: 3, amplitude: 8000 });
            return { srcId, tgtId };
        }""")
        # the target has a fit of its own
        pg.evaluate("id => tabManager.activateTab(id)", ids["tgtId"])
        pg.evaluate("async () => { await runFit(); }")
        pg.evaluate("id => tabManager.activateTab(id)", ids["srcId"])
        before = pg.evaluate("""id => { const t = tabManager._getTab(id);
            return JSON.stringify({ peaks: t.peaks, ui: t.ui, cc: t.ccShift, fit: !!t.fitResult, undo: (t.undoStack || []).length }); }""", ids["tgtId"])
        assert '"fit":true' in before
        pg.evaluate("() => { document.getElementById('bg-endpoint-avg').value = '51'; }")
        pg.evaluate(SPY)
        pg.evaluate("() => showPropagateModal()")
        pg.wait_for_timeout(100)
        pg.evaluate("""id => { const c = document.querySelector('.prop-chk[data-id="' + id + '"]'); if (c) c.checked = true; }""", ids["tgtId"])
        pg.evaluate("async () => { await runPropagation(); }")
        after = pg.evaluate("""id => { const t = tabManager._getTab(id);
            return JSON.stringify({ peaks: t.peaks, ui: t.ui, cc: t.ccShift, fit: !!t.fitResult, undo: (t.undoStack || []).length }); }""", ids["tgtId"])
        notes = pg.evaluate("() => window.__notes")
        active = pg.evaluate("() => tabManager.activeId")
    finally:
        pg.close()
    assert after == before, "the target is exactly as it was"
    assert active == ids["srcId"], "no target was activated"
    assert ["red", 'Batch fit not run: endpoint averaging must be a whole number from 1 to 50 (it is "51").'] in notes, notes


def test_a_saved_fit_at_an_averaging_outside_1_to_50_is_not_restored_as_current(browser, server):
    # Codex averaging round 1: restore and stack reconstruction computed backgrounds at 51
    import json
    # fitted at 50 on this 201-point window (its quarter is 50), then saved as 51 in the settings
    # AND the fit key: 51 would average the same 50 points, so the key and the background match —
    # only the refusal can keep it from being current
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("() => { document.getElementById('bg-endpoint-avg').value = '50'; }")
        pg.evaluate(RUN)
        assert pg.evaluate("() => _statsLiveState()") == "current"
        idx = pg.evaluate("() => _STARTS_UI_FIELDS.indexOf('endpointAvg')")
        proj = json.loads(pg.evaluate("""async () => { let out = null; const o = window._downloadBlob;
            window._downloadBlob = async (b) => { out = await b.text(); }; _doSaveProject();
            for (let i = 0; i < 100 && out === null; i++) await new Promise(r => setTimeout(r, 50));
            window._downloadBlob = o; return out; }"""))
    finally:
        pg.close()
    for t in proj["tabs"]:
        if t.get("ui"):
            assert t["ui"]["endpointAvg"] == "50"
            t["ui"]["endpointAvg"] = "51"
        fr = t.get("fitResult")
        if fr and fr.get("startsModelKey"):
            key = json.loads(fr["startsModelKey"])
            assert key["u"][idx] == "50"
            key["u"][idx] = "51"
            fr["startsModelKey"] = json.dumps(key)
    pg = _new_page(browser, server)
    try:
        pg.evaluate("data => _loadProjectJSON(data, 'p.proj.json')", proj)
        pg.wait_for_timeout(800)
        got = pg.evaluate("() => ({ fit: !!state.fitResult, stats: _statsLiveState(), peaks: state.peaks.length })")
    finally:
        pg.close()
    assert got["peaks"] == 2 and got["stats"] != "current", got


def test_editing_the_field_while_a_fit_runs_discards_its_result(browser, server):
    # Codex averaging round 1: the fit key read "1e2" as 1, so a result for 1 was applied after
    # the field was changed to a refused "1e2" during the upload
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("() => { document.getElementById('bg-endpoint-avg').value = '1'; }")
        pg.evaluate(SPY)
        pg.evaluate("""() => { const o = uploadToBackend; window.uploadToBackend = async (...a) => {
            const sid = await o(...a); document.getElementById('bg-endpoint-avg').value = '1e2'; return sid; }; }""")
        pg.evaluate(RUN)
        got = pg.evaluate("() => ({ fit: !!state.fitResult, msg: document.getElementById('sb-msg').textContent, notes: window.__notes })")
    finally:
        pg.close()
    assert not got["fit"], got
    assert got["msg"] == "Fit discarded (model edited)", got
