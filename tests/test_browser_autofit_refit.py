"""Real browser, real server (sealed-fit v6 Q8, owner 2026-10-12): Auto-Fit refits after its charge
shift, so what it shows is ONE fit — the points, the background and the model the final fit was made
on. Before, the anchor fit's curve and statistics were shown with the points the shift re-selected:
on the committed 8-JT Graphite C 1s scans the R-factor read ~17 % for a fit whose own R is ~2 %
(docs/findings/q8-autofit-refit). Skips cleanly when Playwright / Chromium / gunicorn are absent."""
import json
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


# ── Codex Q8 round 1: the two fits are ONE transaction ────────────────────────
# everything Auto-Fit can change, and the tab's history
STATE = """() => { const t = _activeTab(), v = id => document.getElementById(id).value;
  return { peaks: JSON.stringify(state.peaks), ccShift: state.ccShift, anchors: JSON.stringify(_getManualAnchors()), nextId: state.nextId,
           fields: ['cc-method', 'cc-obs', 'cc-lit', 'roi-min', 'roi-max', 'bg-start', 'bg-end'].map(v),
           fit: state.fitResult ? JSON.stringify({ chi: state.fitResult.chiReduced, be: state.fitResult.be || null, bg: state.fitResult.bgIntensity || null, fitted: state.fitResult.fittedY || null }) : null,
           undo: JSON.stringify(t.undoStack || []), redo: JSON.stringify(t.redoStack || []) }; }"""
SETUP = """() => { window._showAutoFitConfirmModal = () => Promise.resolve(true);
  window.__notes = []; const n = window.notify; window.notify = (m, k, ...r) => { window.__notes.push([k, String(m)]); return n(m, k, ...r); };
  _setManualAnchors([{ x: 283.0, y: 1500 }, { x: 292.0, y: 1200 }]); updatePlot();
  pushUndo(); state.peaks[0].amplitude *= 1.01; undo();   // a redo entry Auto-Fit must not lose on a rollback
}"""


def _page_on_c1s(browser, server):
    pg = browser.new_page(viewport={"width": 1200, "height": 900})
    pg.goto(server + "/", wait_until="load")
    pg.set_input_files("#load-session-input", PROJECT)
    pg.wait_for_function("() => tabManager.tabs.some(t => t.name === 'C1s Scan')", timeout=60000)
    pg.evaluate("() => tabManager.activateTab(tabManager.tabs.find(t => t.name === 'C1s Scan').id)")
    pg.evaluate(SETUP)
    return pg


def _hold_final_fit(pg):
    """Hold the SECOND fit start (the final fit) until released; returns the held routes."""
    held, n = [], {"starts": 0}
    def route(r):
        n["starts"] += 1
        if n["starts"] == 2:
            held.append(r)
        else:
            r.continue_()
    pg.route("**/api/fit/start", route)
    return held


def test_between_the_fits_nothing_can_be_saved_exported_or_undone(browser, server):
    pg = _page_on_c1s(browser, server)
    try:
        held = _hold_final_fit(pg)
        before = pg.evaluate(STATE)
        pg.evaluate("() => { window.__af = runAutoFitC1sGraphite(); }")
        pg.wait_for_function("() => document.getElementById('autofit-busy-label').textContent.startsWith('Auto-Fit: anchor fitted')", timeout=60000)
        for _ in range(100):
            if held:
                break
            pg.wait_for_timeout(100)
        assert held, "the final fit's start is held"
        # the page is covered: a click on the tab bar lands on the overlay
        assert pg.evaluate("""() => { const tb = document.querySelector('.tab-bar, #tab-bar, .tabs') || document.body;
            const r = tb.getBoundingClientRect(); const el = document.elementFromPoint(r.left + 5, r.top + 5);
            return !!el && !!el.closest('#autofit-busy-overlay'); }""")
        pg.evaluate("""() => { window.__dl = []; const o = URL.createObjectURL; URL.createObjectURL = b => { window.__dl.push(b); return o(b); };
            for (const f of [() => _doSaveSpectrum(), () => _doSaveFit(), () => _doSaveProject(), () => exportFitTable('csv'), () => exportResults(), () => saveFit()]) f();
            document.dispatchEvent(new KeyboardEvent('keydown', { key: 'z', ctrlKey: true, bubbles: true })); }""")
        mid = pg.evaluate("() => ({ dl: window.__dl.length, refused: window.__notes.filter(n => /^Auto-Fit is running/.test(n[1])).length, fit: !!state.fitResult })")
        assert mid == {"dl": 0, "refused": 6, "fit": False}, mid
        # Ctrl+Z was refused: the history holds Auto-Fit's one entry and nothing was undone
        assert len(json.loads(pg.evaluate(STATE)["undo"])) == len(json.loads(before["undo"])) + 1
        held[0].continue_()
        pg.evaluate("async () => { await window.__af; }")
        assert pg.evaluate("() => document.getElementById('autofit-busy-overlay').style.display") == "none"
        assert pg.evaluate("() => document.getElementById('sb-msg').textContent") == "Auto-fit complete"
    finally:
        pg.close()


@pytest.mark.parametrize("how", ["http-error", "not-converged", "cancel", "cancel-stalled-upload"])
def test_a_final_fit_that_fails_or_is_cancelled_restores_everything_and_the_history(browser, server, how):
    pg = _page_on_c1s(browser, server)
    try:
        before = pg.evaluate(STATE)
        held = []
        n = {"starts": 0}
        def route(r):
            n["starts"] += 1
            if n["starts"] < 2:
                return r.continue_()
            if how == "http-error":
                return r.fulfill(status=400, content_type="application/json", body='{"error": "forced for the test"}')
            if how == "not-converged":
                return r.fulfill(status=202, content_type="application/json", body='{"job_id": "q8-forced"}')
            held.append(r)
        pg.route("**/api/fit/start", route if how != "cancel-stalled-upload" else (lambda r: r.continue_()))
        if how == "cancel-stalled-upload":
            # the final fit's UPLOAD never answers: only the operation's signal can end it
            ups = {"n": 0}
            def up(r):
                ups["n"] += 1
                if ups["n"] == 2:
                    held.append(r)
                else:
                    r.continue_()
            pg.route("**/api/upload", up)
        pg.route("**/api/fit/progress/q8-forced", lambda r: r.fulfill(status=200, content_type="application/json",
                 body='{"status": "done", "elapsed_sec": 1, "heartbeat_age_sec": 0, "result": {"success": false, "message": "forced for the test"}}'))
        pg.evaluate("() => { window.__af = runAutoFitC1sGraphite(); }")
        if how.startswith("cancel"):
            for _ in range(600):
                if held:
                    break
                pg.wait_for_timeout(100)
            assert held
            pg.click("#autofit-busy-cancel")
        pg.evaluate("async () => { await window.__af; }")
        after = pg.evaluate(STATE)
        notes = pg.evaluate("() => window.__notes")
        assert after == before, {k: (before[k], after[k]) for k in before if before[k] != after[k]}
        assert pg.evaluate("() => document.getElementById('autofit-busy-overlay').style.display") == "none"
        want = {"http-error": r"^Auto-fit failed: forced for the test", "not-converged": r"^Auto-fit not applied: the final fit in the corrected frame did not converge \(forced for the test\)",
                "cancel": r"^Auto-fit cancelled\. Nothing was changed\.$", "cancel-stalled-upload": r"^Auto-fit cancelled\. Nothing was changed\.$"}[how]
        import re
        assert any(re.search(want, m) for k, m in notes), notes
    finally:
        pg.close()


def test_one_undo_returns_the_whole_spectrum_and_redo_the_auto_fit(browser, server):
    pg = _page_on_c1s(browser, server)
    try:
        before = pg.evaluate(STATE)
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        after = pg.evaluate(STATE)
        assert after["ccShift"] != before["ccShift"] and after["anchors"] != before["anchors"]
        assert len(json.loads(after["undo"])) == len(json.loads(before["undo"])) + 1, "ONE undo entry"
        pg.evaluate("() => undo()")
        u = pg.evaluate(STATE)
        for k in ("peaks", "ccShift", "anchors", "fields", "fit", "nextId"):   # the previous result too (Codex round 2)
            assert u[k] == before[k], (k, before[k], u[k])
        pg.evaluate("() => redo()")
        r = pg.evaluate(STATE)
        for k in ("peaks", "ccShift", "anchors", "fields", "fit", "nextId"):
            assert r[k] == after[k], (k, after[k], r[k])
    finally:
        pg.close()


# ── Codex Q8 round 2 ───────────────────────────────────────────────────────────

def test_a_slider_edit_just_before_a_failed_auto_fit_stays_undoable(browser, server):
    pg = _page_on_c1s(browser, server)
    try:
        pg.route("**/api/fit/start", _fail_second_start())
        # a slider burst still pending (its undo entry is pushed 500 ms later) when Auto-Fit starts
        amp0 = pg.evaluate("() => { const a = state.peaks[0].amplitude; _pushUndoDebounced(); state.peaks[0].amplitude = a * 1.25; return a; }")
        n0 = len(json.loads(pg.evaluate(STATE)["undo"]))
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        after = pg.evaluate(STATE)
        assert len(json.loads(after["undo"])) == n0 + 1, "the slider edit's entry survives the rollback"
        assert json.loads(after["peaks"])[0]["amplitude"] == amp0 * 1.25
        pg.evaluate("() => undo()")
        assert json.loads(pg.evaluate(STATE)["peaks"])[0]["amplitude"] == amp0, "and undoes it"
    finally:
        pg.close()


def _fail_second_start():
    n = {"starts": 0}
    def route(r):
        n["starts"] += 1
        if n["starts"] < 2:
            return r.continue_()
        return r.fulfill(status=400, content_type="application/json", body='{"error": "forced for the test"}')
    return route


def test_the_busy_dialog_works_by_keyboard(browser, server):
    pg = _page_on_c1s(browser, server)
    try:
        before = pg.evaluate(STATE)
        held = _hold_final_fit(pg)
        pg.evaluate("() => { window.__af = runAutoFitC1sGraphite(); }")
        for _ in range(600):
            if held:
                break
            pg.wait_for_timeout(100)
        assert held
        assert pg.evaluate("() => document.activeElement && document.activeElement.id") == "autofit-busy-cancel"
        pg.keyboard.press("Tab")
        assert pg.evaluate("() => document.activeElement.id") == "autofit-busy-cancel", "focus stays in the dialog"
        pg.keyboard.press("Control+z")
        assert len(json.loads(pg.evaluate(STATE)["undo"])) == len(json.loads(before["undo"])) + 1, "no shortcut runs"
        pg.keyboard.press("Enter")                     # presses Cancel
        pg.evaluate("async () => { await window.__af; }")
        assert pg.evaluate(STATE) == before
        assert any("Auto-fit cancelled" in m for k, m in pg.evaluate("() => window.__notes"))
    finally:
        pg.close()
