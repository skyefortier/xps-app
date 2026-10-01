"""Real browser, real server (background math, 2026-10-01): a background that does
not satisfy its defining statement is said under the method menu, is not drawn,
and Run Fit refuses it before anything changes (no undo entry, no fit); an
explicit background on the same data draws and fits. Skips cleanly when
Playwright / Chromium / gunicorn are absent."""
import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import _new_page, browser, server  # noqa: E402,F401

U_TAB = """() => {
    // convex: every interior point below the line between the (unequal) edge levels
    const raw = [], inten = [];
    for (let i = 0; i <= 120; i++) { const be = 280 + i * 0.1; raw.push(be); inten.push(1000 + 40 * (be - 285) ** 2); }
    tabManager.createTab('U', raw, inten);
    document.getElementById('roi-min').value = 280; document.getElementById('roi-max').value = 292;
    document.getElementById('bg-start').value = 292; document.getElementById('bg-end').value = 280;
    document.getElementById('bg-endpoint-avg').value = 1;
    document.getElementById('bg-type').value = 'shirley'; _onBgTypeChange();
    addPeak({ center: 285, fwhm: 1.0, amplitude: 100, shape: 'GL', glMix: 30 });
    updatePlot();
}"""

SEEN = """() => ({
    note: getComputedStyle(document.getElementById('bg-not-converged')).display !== 'none',
    text: document.getElementById('bg-not-converged').textContent,
    drawn: state.chart.data.datasets.some(d => d.label === 'Background'),
    iterVisible: document.getElementById('shirley-iter').offsetParent !== null,
})"""


def test_a_non_converged_background_is_said_not_drawn_and_not_fitted(browser, server):
    pg = _new_page(browser, server)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    try:
        pg.evaluate(U_TAB)
        seen = pg.evaluate(SEEN)
        assert seen["note"] and "Shirley background not converged" in seen["text"] and "no net signal" in seen["text"], seen
        assert not seen["drawn"], "a non-converged background is not drawn"
        assert not seen["iterVisible"], "the retired iterations setting is hidden"
        undo0 = pg.evaluate("() => (tabManager._getTab(tabManager.activeId).undoStack || []).length")
        pg.evaluate("() => { window.__n = []; const o = notify; window.notify = (m, k) => { window.__n.push(m); return o(m, k); }; }")
        pg.evaluate("() => runFit()")
        pg.wait_for_timeout(300)
        after = pg.evaluate("() => ({ fit: state.fitResult, undo: (tabManager._getTab(tabManager.activeId).undoStack || []).length, n: window.__n })")
        assert after["fit"] is None and after["undo"] == undo0, after
        assert any(m.startswith("Fit not run: Shirley background not converged") for m in after["n"]), after["n"]
        # an explicit background on the same data draws and fits
        pg.evaluate("() => { document.getElementById('bg-type').value = 'linear'; _onBgTypeChange(); updatePlot(); }")
        seen = pg.evaluate(SEEN)
        assert not seen["note"] and seen["drawn"], seen
        pg.evaluate("() => { window.__n = []; window.__d = false; runFit().then(() => window.__d = true, () => window.__d = true); }")
        pg.wait_for_function("() => window.__d === true", timeout=120000)
        n = pg.evaluate("() => window.__n")
        # the fit is attempted (a linear background is explicit: nothing to converge); whether a
        # peak on U-shaped data converges is the fit's own outcome, not the background's
        assert n and not any(m.startswith("Fit not run") for m in n), n
    finally:
        pg.close()
    assert errors == [], errors
