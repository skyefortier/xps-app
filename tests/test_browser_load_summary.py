"""Real browser, real server (owner 2026-10-28): what a load could not restore is said ONCE, in plain words, grouped
by reason, and stays until dismissed; each tab's Results panel carries its own detail. Until this, opening a
21-file legacy project concatenated every tab's reason into one prominent toast that cleared after 3 s (and the
dropped / stale / unreadable toasts replaced one another), stacks with pruned entries each raised a toast, and a
folder load said "Loaded N spectra" counting files it could not read."""
import base64
import os

import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import browser, server  # noqa: E402,F401

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "docs", "autofit", "test_data")

CAPTURE = """() => { window.__n = []; const o = notify;
    window.notify = (m, k, pr) => { window.__n.push([String(m), k || null, !!pr]); return o(m, k, pr); }; }"""
LOAD_ZIP = """async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i); await _loadZipProject(new File([b], name)); }"""
SUMMARY = """() => { const box = document.getElementById('load-summary');
    return { shown: !box.hidden, title: document.getElementById('load-summary-title').textContent,
             items: Array.from(document.querySelectorAll('#load-summary-list li')).map(li => li.textContent),
             foot: document.getElementById('load-summary-foot').textContent,
             last: _lastLoadSummary && { title: _lastLoadSummary.title, lines: _lastLoadSummary.lines, report: _lastLoadSummary.report },
             prominent: document.getElementById('prominent-toast').classList.contains('show'), n: window.__n }; }"""


def _page(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1400, "height": 900})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    pg.evaluate(CAPTURE)
    return pg


def _load_zip(pg, name):
    f = os.path.join(DATA, name)
    pg.evaluate(LOAD_ZIP, [base64.b64encode(open(f, "rb").read()).decode(), name])


def _results_of(pg, tab_id):
    return pg.evaluate("""id => { tabManager.activateTab(id); renderResults();
        return document.getElementById('results-area').textContent.replace(/\\s+/g, ' '); }""", tab_id)


@pytest.mark.parametrize("name, expect", [
    ("1-GTA UCl4-graphite one set of U doublets.proj.zip",
     ["20 of 20 tabs show the old fit as saved, but it can’t be confirmed against today’s background",
      "In 10 of those, the fit also used a Voigt mix the page no longer draws."]),
    ("Cl2p_projfit_test.proj.zip",
     ["14 of 18 tabs were saved by an earlier version: their peaks are loaded, but the old fit can’t be redrawn.",
      "3 of 18 tabs show the old fit as saved, but it can’t be confirmed against today’s background",
      "In 1 of those, the fit also used a Voigt mix the page no longer draws."]),
])
def test_a_multi_tab_legacy_project_says_one_grouped_summary_that_stays(browser, server, name, expect):  # noqa: F811
    pg = _page(browser, server)
    try:
        _load_zip(pg, name)
        pg.wait_for_timeout(6000)                       # the old toast was gone after 3 s
        got = pg.evaluate(SUMMARY)
        assert got["shown"] and not got["prominent"], got
        assert got["title"].startswith("Project loaded: ") and got["items"] == got["last"]["lines"], got
        for e in expect:
            assert any(i.startswith(e) for i in got["items"]), (e, got["items"])
        assert len(got["items"]) <= 4, got["items"]
        assert got["foot"].startswith("Press Run Fit on a tab to refit it."), got
        # never one line per tab, and no tab name in the summary
        names = pg.evaluate("() => tabManager.tabs.map(t => t.name)")
        assert not any(n in i for n in names for i in got["items"]), got["items"]
        # no per-tab text reached any toast
        assert not [m for m in got["n"] if m[1] != "green" or m[2]], got["n"]
        # dismissal
        pg.click("#load-summary .load-summary-close")
        assert pg.evaluate("() => document.getElementById('load-summary').hidden")
        # each affected tab's Results panel says what happened to ITS fit
        rep = got["last"]["report"]
        for tid in rep["earlier"][:3]:
            txt = _results_of(pg, tid)
            assert "The saved fit of this model was not restored (it was saved without the" in txt, txt[:300]
        for tid in rep["unconfirmed"][:3]:
            txt = _results_of(pg, tid)
            assert "saved by an earlier version without the record of the fit's charge correction" in txt, txt[:300]
        for tid in (rep["voigt"] + rep["voigtAlso"])[:3]:
            txt = _results_of(pg, tid)
            assert "fitted with a Voigt G/L mix the page does not draw" in txt, txt[:300]
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_unreadable_records_pruned_stack_entries_and_missing_zip_files_are_said_once(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        got = pg.evaluate("""async () => {
            const be = [], y = []; for (let i = 0; i < 100; i++) { be.push(280 + i * 0.1); y.push(100 + 50 * Math.exp(-(((i - 50) / 5) ** 2))); }
            tabManager.createTab('A', be, y); tabManager.createTab('B', be, y);
            const data = JSON.parse(JSON.stringify(tabManager.toJSON()));
            for (const t of data.tabs) if (!t.isStack) { t.fitResult = { seal: 'not a record' }; t.id = t.id + 'x'; }
            data.tabs.push({ id: 'stk1', name: '▦ Stack 1', isStack: true, lineWidth: 1.5, verticalOffset: 0,
              entries: [{ id: 'e1', sourceTabId: 'nope', color: '#ff0000', visible: true, showFit: true },
                        { id: 'e2', sourceTabId: 'nope2', color: '#00ff00', visible: true, showFit: true }] });
            // as a ZIP with one more spectrum listed than stored
            const zip = new JSZip(), spectra = [];
            data.tabs.forEach((t, i) => { const f = 'spectrum_' + i + '.json'; spectra.push({ filename: f }); zip.file(f, JSON.stringify(t)); });
            spectra.push({ filename: 'spectrum_missing.json' });
            zip.file('manifest.json', JSON.stringify({ version: 3, spectra, activeId: data.activeId }));
            const blob = await zip.generateAsync({ type: 'uint8array' });
            await _loadZipProject(new File([blob], 'x.proj.zip'));
            return _lastLoadSummary; }""")
        assert got["lines"] == [
            "2 of 2 tabs: the saved fit record can’t be read, so it isn’t shown; their peaks are loaded.",
            "2 stack entries were removed from 1 stack: their spectra are not in the file.",
            "1 spectrum file listed in the project was missing from the ZIP and not loaded.",
        ], got["lines"]
        n = pg.evaluate("() => window.__n")
        assert not [m for m in n if m[1] != "green" or m[2]], n
        for tid in got["report"]["unreadable"]:
            txt = _results_of(pg, tid)
            assert "the saved fit record cannot be read" in txt, txt[:300]
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_project_restored_in_full_says_the_short_green_notice(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate("""() => { const be = [], y = []; for (let i = 0; i < 50; i++) { be.push(280 + i * 0.1); y.push(100 + i); }
            tabManager.createTab('A', be, y); const data = JSON.parse(JSON.stringify(tabManager.toJSON()));
            for (const t of data.tabs) t.id = t.id + 'y';
            _loadProjectJSON(data, 'ok.proj.json'); }""")
        got = pg.evaluate(SUMMARY)
        assert not got["shown"] and got["last"]["lines"] == [], got
        assert any(m[0].startswith("Project loaded: ") and m[1] == "green" for m in got["n"]), got["n"]
    finally:
        pg.close()


def test_a_folder_load_counts_only_what_it_read_and_says_what_it_skipped(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate("""async () => {
            const good = Array.from({ length: 40 }, (_, i) => (280 + i * 0.1).toFixed(2) + ',' + (100 + i)).join('\\n');
            await tabManager.loadFolder([new File([good], 'good.csv'), new File(['no numbers here\\nat all'], 'bad.csv')]); }""")
        got = pg.evaluate(SUMMARY)
        assert got["shown"] and got["title"] == "Loaded 1 spectrum.", got
        assert got["items"] == ["1 file was skipped: it holds no spectrum the app can read."], got
        assert got["foot"] == "", got
    finally:
        pg.close()
