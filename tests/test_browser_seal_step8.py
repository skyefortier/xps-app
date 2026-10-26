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
NOTE = "saved before sealed records — press Run Fit to confirm"
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


# ── Codex step 8 round 1 ─────────────────────────────────────────────────────────────────────────────────────────────
XLSX_HOOK = """() => { window.__xlsx = null; XLSX.writeFile = wb => {
    const back = XLSX.read(XLSX.write(wb, { type: 'array', bookType: 'xlsx' }), { type: 'array' });
    window.__xlsx = Object.fromEntries(back.SheetNames.map(n => [n, XLSX.utils.sheet_to_json(back.Sheets[n], { header: 1, defval: null })])); }; }"""
PNG_HOOK = """() => { window.__png = undefined; window._pngWithText = async (blob, k, text) => { window.__png = text; return blob; };
  window._downloadBlob = async (blob, name) => { if (name.endsWith('.png') && window.__png === undefined) window.__png = null; }; }"""


def _png(pg):
    pg.evaluate(PNG_HOOK)
    pg.evaluate("() => _doPublicationExport()")
    pg.wait_for_function("() => window.__png !== undefined", timeout=20000)
    t = pg.evaluate("() => window.__png")
    return json.loads(t) if t else None


@pytest.mark.parametrize("record", [True, False], ids=["with-record", "recordless"])
def test_every_export_of_a_legacy_fit_carries_its_state(browser, server, record):  # noqa: F811
    """The committed legacy fits hold no record: their PNG must still say LEGACY (Codex step 8 round 1, MAJOR)."""
    pg = _fitted(browser, server)
    try:
        pg.evaluate(LEGACY)
        if not record:
            pg.evaluate("() => { delete state.fitResult.record; tabManager._syncActiveToRecord(); }")
        png = _png(pg)
        assert png is not None and png["sealState"] == "LEGACY: " + NOTE, png
        assert ("engine" in png) is record, png                                   # the record rides only when there is one
        pg.evaluate(XLSX_HOOK)
        pg.evaluate("() => exportFitTable('xlsx')")
        info = pg.evaluate("() => window.__xlsx.Info")
        blank = next(i for i, r in enumerate(info) if all(v is None for v in r))
        assert info[blank + 1][:2] == ["Fit state", "LEGACY: " + NOTE], info[blank:blank + 3]   # opens the appended rows
        csv, tsv = _exports(pg)
        for text in (csv, tsv):
            assert text.split("\n\n")[-1].split("\n")[0] == "# Fit state: LEGACY: " + NOTE
    finally:
        pg.close()


def test_a_stale_legacy_fits_header_says_it_too(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate(LEGACY)
        pg.evaluate("() => { state.peaks[0].center += 0.05; updatePlot(); renderResults(); _applyStatDisplay(state.fitResult); }")
        got = pg.evaluate("""() => ({ stats: _statsLiveState(), header: document.getElementById('fit-quality').textContent,
            tip: document.getElementById('fit-quality').getAttribute('data-xps-tip'),
            note: (document.querySelector('#results-area .stats-legacy-note') || {}).textContent || '' })""")
        assert got["stats"] == "stale" and got["header"].endswith("— (model changed) (saved before sealed records)"), got
        assert NOTE in got["tip"] and got["note"].strip().startswith("This fit was " + NOTE), got
    finally:
        pg.close()


def test_a_legacy_fit_dropped_to_peaks_only_says_so_until_a_fit_is_shown(browser, server):  # noqa: F811
    f = os.path.join(ROOT, "docs/autofit/test_data/4-GTA UCl4-BN.proj.zip")       # two of its fits are dropped (the census)
    pg = _page(browser, server)
    try:
        pg.evaluate("""async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
            for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i); await _loadZipProject(new File([b], name)); }""",
                    [base64.b64encode(open(f, "rb").read()).decode(), os.path.basename(f)])
        pg.wait_for_timeout(500)
        name = pg.evaluate("() => { const t = tabManager.tabs.find(x => !x.isStack && !x.fitResult && _droppedLegacyFits.has(x)); return t ? t.name : null; }")
        assert name, "this project has a saved fit the restore drops"
        pg.evaluate("(n) => { tabManager.activateTab(tabManager.tabs.find(t => t.name === n).id); renderResults(); }", name)
        note = pg.evaluate("() => (document.querySelector('#results-area .stats-legacy-note') || {}).textContent || ''")
        assert "The saved fit of this model was not restored" in note and NOTE in note, note
        pg.evaluate(CAPTURE)
        pg.evaluate("() => exportResults()")
        pg.wait_for_function("() => window.__tsv !== null")
        tail = pg.evaluate("() => window.__tsv").split("\n\n")[-1].split("\n")
        assert tail[0].startswith("# Fit state: PEAKS-ONLY: the saved fit was not restored") and NOTE in tail[0], tail[:2]
        png = _png(pg)
        assert png and png["sealState"].startswith("PEAKS-ONLY: the saved fit was not restored"), png
        # a fit shown on the tab ends it: cleared afterwards, the tab says nothing about the old file's fit
        pg.evaluate("async () => { await runFit(); }")
        pg.evaluate(SETTLE)
        pg.evaluate("() => { state.fitResult = null; tabManager._syncActiveToRecord(); renderResults(); }")
        assert pg.evaluate("() => !!document.querySelector('#results-area .stats-legacy-note')") is False
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def _saves(pg):
    pg.evaluate(CAPTURE)
    pg.evaluate("async () => { document.getElementById('save-fname').value = 'p'; await _doSaveProject(); await _doSaveFit(); await _doSaveSpectrum(); }")
    pg.wait_for_function("() => Object.keys(window.__files).length >= 3")
    out = {}
    for name, text in pg.evaluate("() => window.__files").items():
        d = json.loads(text)
        d.pop("timestamp", None)
        out[name] = d
    return out


def test_a_legacy_fit_re_saves_identically_and_its_saves_carry_no_state_wording(browser, server):  # noqa: F811
    """Saves are main's (the legacy census compares them with main's page field by field, 121 / 121): here, a legacy
    fit's project, fit and spectrum saves hold no state wording, and saving them twice gives the same content."""
    pg = _fitted(browser, server)
    try:
        pg.evaluate(LEGACY)
        first = _saves(pg)
        second = _saves(pg)
        assert sorted(first) == ["p.fit.json", "p.proj.json", "p.spec.json"], sorted(first)
        assert first == second
        for name, d in first.items():
            text = json.dumps(d)
            assert "LEGACY" not in text and "sealed records" not in text and "not proven" not in text, name
            assert '"seal"' not in text, name
    finally:
        pg.close()


@pytest.mark.parametrize("answer,word", [("hold", "confirming"), ("unconfirmed", "unconfirmed")])
def test_acceptance_reads_as_recorded_while_pending_or_unconfirmed(browser, server, answer, word):  # noqa: F811
    pg = _page(browser, server)
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        if answer == "hold":
            pg.route("**/api/verify-fit", lambda route: None)
        else:
            pg.route("**/api/verify-fit", lambda route: route.abort())
        pg.evaluate("async () => { await runFit(); }")
        if answer != "hold":
            pg.evaluate(SETTLE)
        got = pg.evaluate("""() => { renderResults(); const ra = document.getElementById('results-area');
            return { state: sealedState(state.fitResult, _activeTab()).state,
                     line: (ra.querySelector('div.seal-not-proven') || {}).textContent || '', text: ra.textContent }; }""")
        assert got["state"] == ("pending" if answer == "hold" else "unconfirmed"), got
        assert "as recorded — not proven" in got["line"] and word in got["text"], got
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_the_certificate_notice_reads_as_recorded(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        # a record whose continuation moved a centre past the red band (the notice's trigger), checked again
        pg.evaluate("""async () => { const s = structuredClone(state.fitResult.seal), c = s.O.certificate;
            const id = s.O.individual_peaks[0].id;
            c.moved = true; c.centre_moves = [{ id, ev: -1.5 }]; c.largest_centre_move = { id, ev: -1.5 };
            state.fitResult = Object.freeze({ seal: _makeSeal(s) }); await _ensureVerified(_activeTab(), true); renderResults(); }""")
        got = pg.evaluate("""() => ({ state: sealedState(state.fitResult, _activeTab()).state,
            note: (document.querySelector('#results-area .certificate-move-note') || {}).textContent || '' })""")
        assert got["note"] and "moved" in got["note"] and "(as recorded — not proven)" in got["note"], got
    finally:
        pg.close()
