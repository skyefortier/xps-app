"""Seal 1c step 8 (plan §5 matrix, §10): the state wording. A sealed fit's acceptance — convergence, its certificate,
the scattered starts, the required-component check — is shown "as recorded — not proven" (the server's check
recomputes statistics and curves, not those claims). An UNSEALED fit (saved before this release, Q1) is shown as
today and says so: header, Results, R panel, status bar and every export carry "saved before sealed records"; its
SAVES are untouched (the legacy census: re-saves are main's).

Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import base64
import json
import os

import pytest

pytest.importorskip("playwright.sync_api")

from test_browser_bg_window_request import browser, server  # noqa: F401,E402
from test_browser_seal_requests import SCENARIOS, _setup  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
NOTE = "saved before sealed records — re-run this fit to confirm"
SETTLE = """async () => { for (let k = 0; k < 600 && tabManager.tabs.some(t => _sealAttempts.has(t)); k++)
  await new Promise(r => setTimeout(r, 50)); }"""
CAPTURE = """() => { window.__files = {}; window._downloadBlob = async (blob, name) => { window.__files[name] = await blob.text(); };
  window.__tsv = null; const o = URL.createObjectURL;
  URL.createObjectURL = b => { if (String(b.type).includes('tab-separated')) b.text().then(t => { window.__tsv = t; }); return o(b); }; }"""
# the fresh fit as main's runFit built it (a fit saved before this release, restored current)
LEGACY = """() => { const v = _sealView(state.fitResult.seal), json = structuredClone(state.fitResult.seal.O);
  state.fitResult = { chi: v.statistics.chi2, chiReduced: v.statistics.chi2r, rmse: v.statistics.rmse, be: v.energies.slice(),
                      bgIntensity: v.background.slice(), bgSubtracted: v.counts.map((c, i) => c - v.background[i]),
                      backendResult: json, fittedY: v.fittedY.slice(), uploadFull: true, record: _fitRecordFrom(json),
                      startsModelKey: _startsLiveKey() };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);
  tabManager._syncActiveToRecord(); _applyStatDisplay(state.fitResult); _updateRFactorUI(state.fitResult.rFactor);
  updatePlot(); renderResults(); }"""


def _page(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    return pg


def _fitted(browser, server):  # noqa: F811
    pg = _page(browser, server)
    _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
    pg.evaluate("async () => { await runFit(); }")
    pg.evaluate(SETTLE)
    return pg


def _exports(pg):
    pg.evaluate(CAPTURE)
    pg.evaluate("() => exportFitTable('csv')")
    pg.wait_for_function("() => !!window.__files['fit_results.csv']")
    pg.evaluate("() => exportResults()")
    pg.wait_for_function("() => window.__tsv !== null")
    return pg.evaluate("() => window.__files['fit_results.csv']"), pg.evaluate("() => window.__tsv")


def test_a_sealed_fits_acceptance_reads_as_recorded_not_proven(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        assert pg.evaluate("() => sealedState(state.fitResult, _activeTab()).state") == "current"
        got = pg.evaluate("""() => { renderResults(); const ra = document.getElementById('results-area');
            const sp = ra.querySelector('.starts-panel');
            return { line: (ra.querySelector('div.seal-not-proven') || {}).textContent || null,
                     starts: sp ? sp.textContent : null, legacy: !!ra.querySelector('.stats-legacy-note'),
                     header: document.getElementById('fit-quality').textContent }; }""")
        assert got["line"] == "Acceptance (convergence, its certificate, scattered starts, required checks): as recorded — not proven.", got
        assert got["starts"] and "(as recorded — not proven)" in got["starts"], got
        assert not got["legacy"] and "sealed records" not in got["header"], got
        # STALE: nothing is shown as recorded, so nothing is labelled so
        pg.evaluate("() => { state.peaks[0].center += 0.05; updatePlot(); renderResults(); }")
        assert pg.evaluate("() => !!document.querySelector('#results-area div.seal-not-proven')") is False
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_an_unsealed_fit_is_shown_as_today_and_says_it_was_saved_before_sealed_records(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate(LEGACY)
        got = pg.evaluate("""() => { const ra = document.getElementById('results-area');
            return { header: document.getElementById('fit-quality').textContent, tip: document.getElementById('fit-quality').getAttribute('data-xps-tip'),
                     sb: document.getElementById('sb-runs').textContent, note: (ra.querySelector('.stats-legacy-note') || {}).textContent || '',
                     r: ra.textContent, proven: !!ra.querySelector('div.seal-not-proven'), chi: state.fitResult.chiReduced.toFixed(2),
                     state: sealedState(state.fitResult, _activeTab()).state }; }""")
        assert got["state"] == "legacy", got
        assert got["header"].endswith(" = " + got["chi"] + " (saved before sealed records)"), got        # the value as today
        assert NOTE in got["tip"] and got["sb"].endswith("% (legacy)"), got
        assert got["note"].strip().startswith("This fit was " + NOTE), got
        assert "(saved before sealed records)" in got["r"] and not got["proven"], got                   # the R panel
        csv, tsv = _exports(pg)
        for text in (csv, tsv):
            tail = text.split("\n\n")[-1].split("\n")
            assert tail[0] == "# Fit state: LEGACY: " + NOTE.replace(",", ";"), tail[:2]               # opens the appended block
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_legacy_fits_saves_are_untouched(browser, server):  # noqa: F811
    """Q1 / the census: what a legacy fit SAVES is main's — the qualifier is presentation and exports only."""
    pg = _fitted(browser, server)
    try:
        pg.evaluate(LEGACY)
        pg.evaluate(CAPTURE)
        pg.evaluate("async () => { document.getElementById('save-fname').value = 'p'; await _doSaveProject(); await _doSaveFit(); }")
        pg.wait_for_function("() => Object.keys(window.__files).length >= 2")
        files = pg.evaluate("() => window.__files")
        for name, text in files.items():
            assert "LEGACY" not in text and "sealed records" not in text, name
            assert '"seal"' not in text, name
    finally:
        pg.close()


def test_a_committed_legacy_fit_restored_stale_says_it_too(browser, server):  # noqa: F811
    """The committed fits restore LEGACY, most of them stale (no fit key: 'unconfirmed'): the note shows there too."""
    f = os.path.join(ROOT, "docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip")
    pg = _page(browser, server)
    try:
        pg.evaluate("""async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
            for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i); await _loadZipProject(new File([b], name)); }""",
                    [base64.b64encode(open(f, "rb").read()).decode(), os.path.basename(f)])
        pg.wait_for_timeout(500)
        got = pg.evaluate("""() => { const t = tabManager.tabs.find(x => !x.isStack && x.fitResult); tabManager.activateTab(t.id); renderResults();
            return { state: sealedState(state.fitResult, t).state, stats: _statsLiveState(),
                     note: (document.querySelector('#results-area .stats-legacy-note') || {}).textContent || '' }; }""")
        assert got["state"] == "legacy" and got["note"].strip().startswith("This fit was " + NOTE), got
        assert pg.errors == [], pg.errors
    finally:
        pg.close()
