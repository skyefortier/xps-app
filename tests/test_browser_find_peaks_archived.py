"""Find Peaks is ARCHIVED (owner, 2026-09-30): hidden, not deleted.

Real browser, real server: the page offers no way to start Find Peaks; a
project whose peaks came from Find Peaks (the analysis run programmatically,
as the kept Find Peaks tests do) saves, reloads in a fresh page and fits
exactly as before; and a Find Peaks result cached in a saved tab — injected,
as an older save might carry one — does not resurface anywhere.
Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import json

import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import (  # noqa: E402,F401  (fixtures + helpers)
    _new_page, _run_and_apply_find_peaks, browser, server)

CAPTURE = """() => { window.__dl = []; window._downloadBlob = async (blob, name) => {
  window.__dl.push({ name, text: await blob.text() }); }; }"""

VISIBLE = """() => ({
  text: document.body.innerText,
  overlayOpen: !!document.querySelector('#find-peaks-overlay.open'),
  menuItem: !!document.getElementById('find-peaks-menu-item'),
  resultsShown: (document.getElementById('fp-results') || {}).style ? document.getElementById('fp-results').style.display : null,
})"""


def _c1s_tab(pg):
    pg.evaluate("""() => {
        const raw = [], inten = [];
        for (let i = 0; i <= 400; i++) {
            const be = 280.0 + i * 0.0375;
            raw.push(be);
            const g = (c, a, w) => a * Math.exp(-4 * Math.log(2) * ((be - c) / w) ** 2);
            inten.push(300 + g(284.5, 6000, 0.8) + g(286.4, 900, 1.2));
        }
        tabManager.createTab('C1s', raw, inten);
        document.getElementById('roi-min').value = 280.0;
        document.getElementById('roi-max').value = 295.0;
        updatePlot();
    }""")


def _assert_nothing_of_find_peaks_visible(pg, where):
    v = pg.evaluate(VISIBLE)
    assert not v["menuItem"], f"{where}: the Find Peaks menu entry is back"
    assert not v["overlayOpen"], f"{where}: the Find Peaks modal is open"
    assert "Find Peaks" not in v["text"], f"{where}: 'Find Peaks' is visible on the page"
    assert v["resultsShown"] in (None, "", "none"), f"{where}: Find Peaks results are displayed"


def test_find_peaks_cannot_be_started_from_the_page(browser, server):
    pg = _new_page(browser, server)
    try:
        _assert_nothing_of_find_peaks_visible(pg, "fresh page")
        pg.evaluate("() => toggleSaveMenu()")
        pg.wait_for_timeout(200)
        menu = pg.evaluate("() => { const m = document.querySelector('#save-dropdown .save-dropdown-menu'); return { shown: getComputedStyle(m).display !== 'none', items: [...m.querySelectorAll('.save-dropdown-item')].map(b => b.innerText) }; }")
        assert menu["shown"] and any("Auto-Fit C1s Graphite" in t for t in menu["items"]), menu   # the menu really is open
        assert not any("Find Peaks" in t for t in menu["items"]), menu
        _assert_nothing_of_find_peaks_visible(pg, "Actions menu open")
    finally:
        pg.close()


def test_a_project_whose_peaks_came_from_find_peaks_loads_and_fits_as_before(browser, server):
    pg = _new_page(browser, server)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("dialog", lambda d: d.accept())
    try:
        _c1s_tab(pg)
        _run_and_apply_find_peaks(pg, full_window=False)          # programmatic, as the kept tests do
        pg.evaluate("() => document.getElementById('find-peaks-overlay').classList.remove('open')")
        peaks = pg.evaluate("() => state.peaks.map(p => ({ id: p.id, shape: p.shape, center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, fp: !!p._findPeaks }))")
        assert peaks and all(p["fp"] for p in peaks), "the applied peaks carry Find Peaks' provenance"
        pg.evaluate(CAPTURE)
        pg.evaluate("() => _doSaveProject()")
        pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
        saved = json.loads(pg.evaluate("() => window.__dl[0].text"))
    finally:
        pg.close()
    assert errors == [], errors
    spectrum = [t for t in saved["tabs"] if not t.get("isStack")]
    assert spectrum and all("findPeaks" not in t for t in spectrum), "a Find Peaks cache is never saved"
    # an older save could carry one: inject it
    for t in spectrum:
        t["findPeaks"] = {"last": {"body": {"success": True, "peaks": [], "diagnostics": {"winner": "MG2"}},
                                   "method": "ic_model_comparison", "regions": ["C 1s"]}}

    pg = _new_page(browser, server)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("dialog", lambda d: d.accept())
    try:
        pg.evaluate("data => _loadProjectJSON(data, 'archived.proj.json')", saved)
        pg.wait_for_timeout(500)
        loaded = pg.evaluate("() => state.peaks.map(p => ({ id: p.id, shape: p.shape, center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, fp: !!p._findPeaks }))")
        assert loaded == peaks, "the peaks load exactly as saved"
        cached = pg.evaluate("() => tabManager.tabs.filter(t => !t.isStack).map(t => !!(t.findPeaks && t.findPeaks.last))")
        assert not any(cached), "a saved Find Peaks cache was restored onto a tab"
        _assert_nothing_of_find_peaks_visible(pg, "after loading")
        pg.evaluate("() => { window.__d = false; runFit().then(() => window.__d = true, () => window.__d = true); }")
        pg.wait_for_function("() => window.__d === true", timeout=120000)
        fit = pg.evaluate("() => ({ sb: document.getElementById('sb-msg').textContent, engine: state.fitResult && (state.fitResult.engine || 'server'), stats: _statsLiveState() })")
        assert fit["engine"] == "server" and fit["stats"] == "current" and "complete" in fit["sb"].lower(), fit
        _assert_nothing_of_find_peaks_visible(pg, "after Run Fit")
    finally:
        pg.close()
    assert errors == [], errors
