"""Real browser, real server (sealed-fit v6 Q8, owner 2026-10-12): Auto-Fit refits after its charge
shift, so what it shows is ONE fit — the points, the background and the model the final fit was made
on. Before, the anchor fit's curve and statistics were shown with the points the shift re-selected:
on the committed 8-JT Graphite C 1s scans the R-factor read ~17 % for a fit whose own R is ~2 %
(docs/findings/q8-autofit-refit). Skips cleanly when Playwright / Chromium / gunicorn are absent."""
import os

import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import browser, server  # noqa: E402,F401

PROJECT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs/autofit/test_data/8-JT Graphite.proj.zip")


def test_auto_fit_shows_the_fit_it_made_in_the_corrected_frame(browser, server):
    pg = browser.new_page(viewport={"width": 1200, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    try:
        pg.goto(server + "/", wait_until="load")
        pg.set_input_files("#load-session-input", PROJECT)
        pg.wait_for_function("() => tabManager.tabs.some(t => t.name === 'C1s Scan')", timeout=60000)
        pg.evaluate("() => tabManager.activateTab(tabManager.tabs.find(t => t.name === 'C1s Scan').id)")
        pg.evaluate("() => { window._showAutoFitConfirmModal = () => Promise.resolve(true); }")
        before = pg.evaluate("() => state.ccShift")
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        got = pg.evaluate("""() => {
            const fr = state.fitResult, br = fr && fr.backendResult;
            return { msg: document.getElementById('sb-msg').textContent, cc: state.ccShift,
                     shownBe: fr && fr.be, fittedBe: br && br.energy, nFitted: fr && fr.fittedY && fr.fittedY.length,
                     r: fr && fr.rFactor && fr.rFactor.rPct, locked: state.peaks.every(p => p.fixCenter),
                     graphite: (state.peaks.find(p => p.name === 'Graphite') || {}).center }; }""")
    finally:
        pg.close()
    assert got["msg"] == "Auto-fit complete", got["msg"]
    assert got["cc"] != before, "the frame moved (the case the anchor fit's numbers misdescribed)"
    # ONE fit: the points shown ARE the points the published fit was made on, exactly
    assert got["shownBe"] == got["fittedBe"] and got["nFitted"] == len(got["shownBe"])
    assert got["locked"] and abs(got["graphite"] - 284.5) < 1e-3
    assert got["r"] < 5, f"R {got['r']:.2f} % (the anchor fit's curve against the moved points read ~17 %)"
    assert errors == [], errors
