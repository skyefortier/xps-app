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
     {"lines": ["20 of 20 tabs show the old fit as saved, but it can’t be confirmed against today’s background (it was saved "
                "without the record of its charge correction), so no χ², R-factor or uncertainties are shown. In 10 of them "
                "the fit also used a Voigt mix the page no longer draws."],
      "nonempty": ["unconfirmed", "voigtAlsoUnconfirmed"]}),
    ("Cl2p_projfit_test.proj.zip",
     {"lines": ["14 of 18 tabs were saved without the fitted curve or the energies their fit needs (earlier versions saved "
                "fits this way): their peaks are loaded, but the old fit can’t be redrawn.",
                "3 of 18 tabs show the old fit as saved, but it can’t be confirmed against today’s background (it was saved "
                "without the record of its charge correction), so no χ², R-factor or uncertainties are shown. In one of them "
                "the fit also used a Voigt mix the page no longer draws."],
      "nonempty": ["earlier", "unconfirmed", "voigtAlsoUnconfirmed"]}),
])
def test_a_multi_tab_legacy_project_says_one_grouped_summary_that_stays(browser, server, name, expect):  # noqa: F811
    pg = _page(browser, server)
    try:
        _load_zip(pg, name)
        pg.wait_for_timeout(6000)                       # the old toast was gone after 3 s
        got = pg.evaluate(SUMMARY)
        assert got["shown"] and not got["prominent"], got
        assert got["title"].startswith("Project loaded: ") and got["items"] == got["last"]["lines"], got
        assert got["items"] == expect["lines"], got["items"]
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
        for k in expect["nonempty"]:                    # the per-tab checks below must not run zero times
            assert rep[k], (k, rep)
        for tid in rep["earlier"][:3]:
            txt = _results_of(pg, tid)
            assert "The saved fit of this model was not restored (it was saved without the" in txt, txt[:300]
        for tid in rep["unconfirmed"][:3]:
            txt = _results_of(pg, tid)
            assert "saved by an earlier version without the record of the fit's charge correction" in txt, txt[:300]
        for tid in (rep["voigt"] + rep["voigtAlsoUnconfirmed"] + rep["voigtAlsoBgchanged"])[:3]:
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
            "2 stack entries were removed from stack “▦ Stack 1” (2): their spectra are not in the file.",
            "1 spectrum file listed in the project was missing from the ZIP and not loaded.",
        ], got["lines"]
        n = pg.evaluate("() => window.__n")
        assert not [m for m in n if m[1] != "green" or m[2]], n
        assert len(got["report"]["unreadable"]) == 2
        for tid in got["report"]["unreadable"]:
            txt = _results_of(pg, tid)
            assert "the saved fit record cannot be read" in txt, txt[:300]
        # the stack says it in its own legend, after the summary is dismissed (round 1)
        pg.evaluate("() => dismissLoadSummary()")
        note = pg.evaluate("""() => { const st = tabManager.tabs.find(t => t.isStack); tabManager.activateTab(st.id);
            return (document.querySelector('#stack-legend-list .stack-pruned-note') || {}).textContent || ''; }""")
        assert note == "2 entries were removed when this stack was loaded: their spectra are not in the file.", note
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
        assert got["items"] == ["1 file was skipped: it could not be read as a spectrum."], got
        assert got["foot"] == "", got
    finally:
        pg.close()


def test_the_lines_say_each_reason_once_with_a_voigt_mix_on_its_own_line(browser, server):  # noqa: F811
    """Round 1: "In N of those" after a later line pointed at the wrong group. A: unconfirmed + Voigt, B: background
    changed, C: Voigt only — each said on its own line, never counted twice."""
    pg = _page(browser, server)
    try:
        lines = pg.evaluate("""() => { const r = _newLoadReport();
            r.unconfirmed.push('a'); r.voigtAlsoUnconfirmed.push('a'); r.bgchanged.push('b'); r.voigt.push('c');
            return _loadSummaryLines(r, n => n + ' of 3 tabs'); }""")
        assert lines == [
            "1 of 3 tabs shows the old fit as saved, but it can’t be confirmed against today’s background (it was saved without "
            "the record of its charge correction), so no χ², R-factor or uncertainties are shown. In one of them the fit also "
            "used a Voigt mix the page no longer draws.",
            "1 of 3 tabs shows the old fit as saved, but today’s background differs from the one it was fitted against, so no "
            "χ², R-factor or uncertainties are shown.",
            "1 of 3 tabs shows the old fit as saved, but it used a Voigt mix the page no longer draws, so no χ², R-factor or "
            "uncertainties are shown.",
        ], lines
        # every reason the restore can return lands in a group (the catch-all only for record damage)
        groups = pg.evaluate("""() => [
            'it was saved without its fitted envelope, so …', 'it was saved without the energies it was fitted on …',
            'its raw data are missing or incomplete …', 'its background settings give no converged background now: …',
            'it was saved after its model or settings changed …', 'its stored points are not points of its raw data …',
            'its stored points match more than one set …', 'it has more stored points (9) than …',
            'its stored statistics cannot be compared with its data in floating point …',
            "its stored envelope and today's background cannot be compared in floating point …",
            'its stored envelope and the energies it was fitted on have different lengths',
            'its stored RMSE is negative …'].map(_restoreDropGroup)""")
        assert groups == ["earlier", "earlier", "rawdata", "background", "editedsave", "unmatched", "unmatched",
                          "uncheckable", "uncheckable", "uncheckable", "damaged", "damaged"], groups
    finally:
        pg.close()


def test_a_long_summary_keeps_its_dismiss_button_on_a_phone(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 320, "height": 568})
    try:
        pg.goto(server + "/", wait_until="load")
        pg.evaluate("""() => { const r = _newLoadReport();
            for (const k of ['earlier', 'rawdata', 'background', 'editedsave', 'unmatched', 'uncheckable', 'damaged', 'unreadable',
                             'unconfirmed', 'bgchanged', 'voigt']) r[k].push('x');
            r.stackEntries = 3; r.stacks = [['▦ ' + 'a-very-long-stack-name-'.repeat(8), 3]]; r.missingFiles = 2; r.skippedFiles = 1;
            showLoadSummary('Project loaded: "' + 'an-unbroken-sample-name-'.repeat(10) + '" — 12 tabs.', r, n => n + ' of 12 tabs'); }""")
        box = pg.evaluate("""() => { const b = document.getElementById('load-summary').getBoundingClientRect(),
            c = document.querySelector('#load-summary .load-summary-close').getBoundingClientRect(),
            body = document.querySelector('#load-summary .load-summary-body');
            return { top: b.top, bottom: b.bottom, left: b.left, right: b.right, ctop: c.top, cbottom: c.bottom, cright: c.right,
                     scrolls: body.scrollHeight > body.clientHeight, docw: document.documentElement.scrollWidth }; }""")
        assert box["top"] >= 0 and box["bottom"] <= 568 and box["left"] >= 0 and box["right"] <= 320, box
        assert 0 <= box["ctop"] and box["cbottom"] <= 568 and box["cright"] <= 320, box
        assert box["scrolls"], "the body scrolls inside the box"
        pg.click("#load-summary .load-summary-close")
        assert pg.evaluate("() => document.getElementById('load-summary').hidden")
    finally:
        pg.close()


def test_a_project_with_a_real_fit_restored_in_full_says_the_short_green_notice(browser, server):  # noqa: F811
    """Round 1: the earlier fixture held no fit. Here a real server fit is saved and reloaded: current, no summary."""
    pg = _page(browser, server)
    try:
        pg.evaluate("""async () => { const be = [], y = [];
            for (let i = 0; i < 160; i++) { const e = 280 + i * 0.1; be.push(e); y.push(200 + 5000 * Math.exp(-(((e - 288) / 0.7) ** 2) * 2.77)); }
            tabManager.createTab('C1s fit', be, y); addPeak({ center: 288, amplitude: 5000, fwhm: 1.2 }); await runFit(); }""")
        pg.wait_for_function("() => !!(state.fitResult && state.fitResult.seal)", timeout=60000)
        # the page's own Save Project (the sealed record), captured, then loaded into a fresh page
        pg.evaluate("""() => { window.__dl = []; window._downloadBlob = async (blob, name) => {
            window.__dl.push({ name, text: await blob.text() }); }; }""")
        pg.evaluate("() => _doSaveProject()")
        pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
        text = pg.evaluate("() => window.__dl[0].text")
        pg.close()
        pg = _page(browser, server)
        pg.evaluate("text => _loadProjectJSON(JSON.parse(text), 'fit.proj.json')", text)
        got = pg.evaluate(SUMMARY)
        assert not got["shown"] and got["last"]["lines"] == [], got
        assert any(m[0].startswith("Project loaded: ") and m[1] == "green" for m in got["n"]), got["n"]
        loaded = pg.evaluate("() => tabManager.tabs.filter(t => !t.isStack).map(t => !!(t.fitResult && t.fitResult.seal))")
        assert loaded == [True], loaded                 # the reloaded tab holds its sealed fit
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_later_load_clears_an_earlier_summary(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        _load_zip(pg, "Project9_CasaXPS_newfit.proj.zip")
        pg.wait_for_timeout(300)
        assert pg.evaluate("() => !document.getElementById('load-summary').hidden")
        pg.evaluate("""() => { const be = [], y = []; for (let i = 0; i < 40; i++) { be.push(280 + i * 0.1); y.push(100 + i); }
            setSpectrum(be, y, 'next.csv'); }""")
        assert pg.evaluate("() => document.getElementById('load-summary').hidden")
        # and a fit file applied after it
        _load_zip(pg, "Project9_CasaXPS_newfit.proj.zip")
        pg.wait_for_timeout(300)
        assert pg.evaluate("() => !document.getElementById('load-summary').hidden")
        pg.evaluate("() => _applyFitJSON({ version: 1, peaks: [] })")
        assert pg.evaluate("() => document.getElementById('load-summary').hidden")
    finally:
        pg.close()


def test_a_load_error_quotes_at_most_60_characters_of_the_file_and_stays(browser, server):  # noqa: F811
    """Round 1: a peak's invalid colour was quoted whole (1438 characters) into a 3-second toast."""
    pg = _page(browser, server)
    try:
        pg.evaluate("""() => { const be = [], y = []; for (let i = 0; i < 40; i++) { be.push(280 + i * 0.1); y.push(100 + i); }
            tabManager.createTab('A', be, y); const data = JSON.parse(JSON.stringify(tabManager.toJSON()));
            for (const t of data.tabs) { t.id = t.id + 'w'; t.peaks = [{ id: 1, color: 'invalid'.repeat(200), center: 284, fwhm: 1, amplitude: 10, shape: 'GL' }]; }
            _loadProjectJSON(data, 'bad.proj.json'); }""")
        pg.wait_for_timeout(4500)
        got = pg.evaluate(SUMMARY)
        assert got["shown"] and got["title"] == "Project not loaded.", got
        assert len(got["items"]) == 1 and len(got["items"][0]) < 160, got["items"]
        assert got["items"][0].startswith('In the file, peak color "invalidinvalid') and "…" in got["items"][0], got["items"]
        assert pg.evaluate("() => document.getElementById('load-summary').classList.contains('is-error')")
        assert not [m for m in got["n"] if m[2]], got["n"]
    finally:
        pg.close()


def test_a_file_the_browser_cannot_read_is_skipped_not_waited_on(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.evaluate("""async () => {
            const real = FileReader.prototype.readAsText;
            FileReader.prototype.readAsText = function (f) { if (f.name === 'unreadable.csv') { setTimeout(() => this.onerror && this.onerror(new Event('error')), 0); return; } return real.call(this, f); };
            const good = Array.from({ length: 40 }, (_, i) => (280 + i * 0.1).toFixed(2) + ',' + (100 + i)).join('\\n');
            await Promise.race([tabManager.loadFolder([new File([good], 'good.csv'), new File(['x'], 'unreadable.csv')]),
                                new Promise((_, rej) => setTimeout(() => rej(new Error('the folder load waited on the unreadable file')), 5000))]);
            FileReader.prototype.readAsText = real; }""")
        got = pg.evaluate(SUMMARY)
        assert got["title"] == "Loaded 1 spectrum." and got["items"] == ["1 file was skipped: it could not be read as a spectrum."], got
    finally:
        pg.close()
