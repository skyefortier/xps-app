"""Real browser, real server (Q10 0c', owner 2026-10-11): a link the server cannot fit as drawn is
refused in plain words before anything changes — a Voigt child of a GL parent; a peak left linked
to a deleted peak (removing a chain's root deletes only its immediate children); Batch Fit before
any target is touched. Skips cleanly when Playwright / Chromium / gunicorn are absent."""
import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import _new_page, browser, server  # noqa: E402,F401
from test_browser_background_not_converged import PEAK_TAB  # noqa: E402

SPY = """() => { window.__api = []; window.__notes = [];
    const o = window.fetch; window.fetch = (url, opts) => { if (String(url).includes('/api/')) window.__api.push(String(url)); return o(url, opts); };
    const n = window.notify; window.notify = (m, k, ...r) => { window.__notes.push([k, m]); return n(m, k, ...r); }; }"""


def _refused(pg, setup):
    pg.evaluate(PEAK_TAB)
    pg.evaluate(setup)
    before = pg.evaluate("() => ({ peaks: JSON.stringify(state.peaks), undo: (_activeTab().undoStack || []).length })")
    pg.evaluate(SPY)
    pg.evaluate("async () => { await runFit(); }")
    got = pg.evaluate("() => ({ api: window.__api, notes: window.__notes, fit: !!state.fitResult, peaks: JSON.stringify(state.peaks), undo: (_activeTab().undoStack || []).length })")
    assert got["api"] == [] and not got["fit"], got
    assert got["peaks"] == before["peaks"] and got["undo"] == before["undo"]
    return [m for k, m in got["notes"] if k == "red"]


def test_run_fit_refuses_a_voigt_child_of_a_gl_parent(browser, server):
    pg = _new_page(browser, server)
    try:
        red = _refused(pg, """() => { const [a, b] = state.peaks; a.name = 'C-C'; b.name = 'C-O';
            b.shape = 'Voigt'; b.linked = a.id; b.linkOffset = 2; b.linkRatio = 0.2; updatePlot(); }""")
    finally:
        pg.close()
    assert any(m.startswith('Fit not run: "C-O" is linked to "C-C" but has a different lineshape (Voigt, GL)') for m in red), red


def test_run_fit_refuses_a_peak_left_linked_to_a_deleted_peak(browser, server):
    pg = _new_page(browser, server)
    try:
        red = _refused(pg, """() => { const [a, b] = state.peaks;
            const c = addPeak({ center: 288.5, fwhm: 1.2, amplitude: 300, shape: 'GL', glMix: 30, name: 'grandchild' });
            b.linked = a.id; b.linkOffset = 2; b.linkRatio = 0.2; c.linked = b.id; c.linkOffset = 2; c.linkRatio = 0.5;
            removePeak(a.id); updatePlot(); }""")
        left = pg.evaluate("() => state.peaks.map(p => p.name)")
    finally:
        pg.close()
    assert left == ["grandchild"], left
    assert any(m.startswith('Fit not run: "grandchild" is linked to a peak that is no longer in the model') for m in red), red


def test_batch_fit_refuses_an_invalid_graph_before_any_target_is_changed(browser, server):
    pg = _new_page(browser, server)
    try:
        ids = pg.evaluate("""() => {
            const mk = () => { const be = [], y = []; for (let i = 0; i < 120; i++) { const x = 520 + i * 0.25; be.push(x); y.push(1000 + 5000 * Math.exp(-((x - 535) ** 2) / 4)); } return { be, y }; };
            const t = mk(); tabManager.createTab('TGT', t.be, t.y); const tgtId = tabManager.activeId;
            addPeak({ center: 535, fwhm: 3, amplitude: 5000 });
            const s = mk(); tabManager.createTab('SRC', s.be, s.y); const srcId = tabManager.activeId;
            const a = addPeak({ center: 535, fwhm: 3, amplitude: 5000, shape: 'GL', name: 'parent' });
            const b = addPeak({ center: 538, fwhm: 3, amplitude: 500, shape: 'Voigt', name: 'child' });
            b.linked = a.id; b.linkOffset = 3; b.linkRatio = 0.1;
            return { srcId, tgtId }; }""")
        before = pg.evaluate("id => JSON.stringify(tabManager._getTab(id).peaks)", ids["tgtId"])
        pg.evaluate(SPY)
        pg.evaluate("() => showPropagateModal()")
        pg.wait_for_timeout(100)
        pg.evaluate("""id => { const c = document.querySelector('.prop-chk[data-id="' + id + '"]'); if (c) c.checked = true; }""", ids["tgtId"])
        pg.evaluate("async () => { await runPropagation(); }")
        after = pg.evaluate("id => JSON.stringify(tabManager._getTab(id).peaks)", ids["tgtId"])
        red = [m for k, m in pg.evaluate("() => window.__notes") if k == "red"]
    finally:
        pg.close()
    assert after == before, "the target is untouched"
    assert any(m.startswith('Batch fit not run: "child" is linked to "parent" but has a different lineshape') for m in red), red
