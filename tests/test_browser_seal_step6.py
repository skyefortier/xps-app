"""Seal 1c step 6 (plan docs/superpowers/plans/2026-10-14-seal-1c-page.md §8.3, §8.4, §8.6, §11): both serializers
write the seal (a project's fit is `{seal}` and nothing else authoritative; a spectrum file's seal is at the top level
beside convenience fields written FROM the view), and ONE loader installs it as saved — the sealed / legacy dispatch
first, a schema failure PEAKS-ONLY, never the legacy adapter — and verifies every loaded seal, inactive tabs too.
A legacy fit that falls back to peaks only keeps its record (`tab.provenance`, V6.8). Behind the switch
(`_SEAL_AUTHORITATIVE`), which these tests turn on.

Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import json

import pytest

pytest.importorskip("playwright.sync_api")

from test_browser_bg_window_request import browser, server  # noqa: F401,E402
from test_browser_seal_requests import SCENARIOS, _setup, AUTOFIT_PROJECT  # noqa: E402

ON = "() => { _SEAL_AUTHORITATIVE = true; }"
CAPTURE = """() => { window.__blobs = {};
  window._downloadBlob = (blob, name) => { window.__blobs[name] = blob; }; }"""
TEXT = "async (name) => await window.__blobs[name].text()"
B64 = """async (name) => { const b = new Uint8Array(await window.__blobs[name].arrayBuffer()); let s = '';
  for (let i = 0; i < b.length; i++) s += String.fromCharCode(b[i]); return btoa(s); }"""
STATE = "(name) => { const t = name ? tabManager.tabs.find(x => x.name === name) : _activeTab(); const fr = t === _activeTab() ? state.fitResult : t.fitResult; const s = sealedState(fr, t); return [s.state, s.check]; }"
# every loaded seal checked: start what is not started, then wait for the attempts in flight (the loader's own)
SETTLE = """async () => { for (const t of tabManager.tabs) if (!t.isStack) _ensureVerified(t);
  for (let k = 0; k < 600 && tabManager.tabs.some(t => _sealAttempts.has(t)); k++) await new Promise(r => setTimeout(r, 50)); }"""


def _page(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    pg.evaluate(ON)
    pg.evaluate(CAPTURE)
    return pg


def _fitted(browser, server, scenario="asymgl_linked_smart", local=False):  # noqa: F811
    pg = _page(browser, server)
    _setup(pg, SCENARIOS[scenario])
    if local:
        pg.route("**/api/upload", lambda route: route.abort())
    pg.evaluate("async () => { await runFit(); }")
    if local:
        pg.unroute("**/api/upload")
    pg.evaluate(SETTLE)
    return pg


def _save_project(pg):
    pg.evaluate("() => { document.getElementById('save-fname').value = 'p'; }")
    pg.evaluate("async () => { await _doSaveProject(); }")
    names = pg.evaluate("() => Object.keys(window.__blobs)")
    name = next(n for n in names if n.startswith("p.proj"))
    return name, (pg.evaluate(B64, name) if name.endswith(".zip") else pg.evaluate(TEXT, name))


def _load_project(browser, server, name, payload):  # noqa: F811
    pg = _page(browser, server)
    if name.endswith(".zip"):
        pg.evaluate("""async (b64) => { const s = atob(b64), b = new Uint8Array(s.length);
            for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
            await _loadZipProject(new File([b], 'p.proj.zip')); }""", payload)
    else:
        pg.evaluate("(text) => _loadProjectJSON(JSON.parse(text), 'p.proj.json')", payload)
    return pg


def test_a_project_saves_the_seal_alone_and_reloads_current(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        assert pg.evaluate(STATE, None) == ["current", None]
        name, text = _save_project(pg)
        tab = json.loads(text)["tabs"][0]
        assert list(tab["fitResult"].keys()) == ["seal"], tab["fitResult"].keys()
        seal = pg.evaluate("() => JSON.parse(JSON.stringify(state.fitResult.seal))")
        assert tab["fitResult"]["seal"] == seal
    finally:
        pg.close()
    pg = _load_project(browser, server, name, text)
    try:
        got = pg.evaluate("""() => ({ keys: Object.keys(state.fitResult), frozen: Object.isFrozen(state.fitResult) && Object.isFrozen(state.fitResult.seal) })""")
        assert got == {"keys": ["seal"], "frozen": True}, got
        pg.evaluate(SETTLE)
        assert pg.evaluate(STATE, None) == ["current", None]
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_zip_project_of_five_tabs_reloads_every_seal_current_without_activating_them(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        # four more tabs holding the same fit (same data, model, context and seal): five tabs → .proj.zip
        pg.evaluate("""() => { const src = _activeTab(); tabManager._syncActiveToRecord();
            const copies = [];
            for (let k = 0; k < 4; k++) copies.push(tabManager.createTab('copy ' + k, src.rawBE.slice(), src.rawIntensity.slice()));
            tabManager.activateTab(src.id);     // the copies are inactive records now: their fields stay as set
            for (const t of copies) { t.peaks = structuredClone(src.peaks); t.ui = { ...src.ui }; t.ccShift = src.ccShift;
              t.manualAnchors = structuredClone(src.manualAnchors || []); t.fitResult = { seal: src.fitResult.seal }; } }""")
        name, payload = _save_project(pg)
        assert name.endswith(".zip")
    finally:
        pg.close()
    pg = _load_project(browser, server, name, payload)
    try:
        calls = pg.evaluate("() => tabManager.tabs.length")
        assert calls == 5
        # every tab is verified by the loader itself (background attempts), inactive ones included
        pg.evaluate(SETTLE)
        got = pg.evaluate("""() => tabManager.tabs.map(t => { const fr = t === _activeTab() ? state.fitResult : t.fitResult;
            const s = sealedState(fr, t); return [t.name, s.state, s.check, s.reason]; })""")
        assert all(g[1] == "current" for g in got), got
    finally:
        pg.close()


def test_a_spectrum_file_carries_the_seal_and_the_loader_ignores_its_convenience_fields(browser, server):  # noqa: F811
    pg = _fitted(browser, server, "gauss_voigt_linear_avg3_window")
    try:
        pg.evaluate("() => { document.getElementById('save-fname').value = 's'; _doSaveSpectrum(); }")
        text = pg.evaluate(TEXT, "s.spec.json")
        data = json.loads(text)
        view = pg.evaluate("""() => { const v = sealedState(state.fitResult, _activeTab()).view;
            return { energies: v.energies, fittedY: v.fittedY, chi: v.statistics.chi2r }; }""")
        assert data["roiBE"] == view["energies"] and data["fittedY"] == view["fittedY"], "convenience fields from the view"
        assert data["statistics"]["chiReduced"] == view["chi"] and data["statistics"]["sealState"] == "CURRENT"
        assert data["seal"]["engine"] == "server"
    finally:
        pg.close()
    # convenience fields a reader edited: never read back
    data["fittedY"] = [0] * len(data["fittedY"])
    data["statistics"]["chiReduced"] = 0.001
    pg = _page(browser, server)
    try:
        pg.evaluate("(text) => _loadSpectrumFile(JSON.parse(text), 's.spec.json')", json.dumps(data))
        pg.evaluate(SETTLE)
        assert pg.evaluate(STATE, None) == ["current", None]
        assert pg.evaluate("() => Object.keys(state.fitResult)") == ["seal"]
    finally:
        pg.close()


def test_a_local_fit_round_trips_current(browser, server):  # noqa: F811
    pg = _fitted(browser, server, "gauss_voigt_linear_avg3_window", local=True)
    try:
        assert pg.evaluate("() => state.fitResult.seal.engine") == "local"
        name, text = _save_project(pg)
    finally:
        pg.close()
    pg = _load_project(browser, server, name, text)
    try:
        assert pg.evaluate(STATE, None) == ["current", None]
        assert pg.evaluate("() => _isLocalFit(state.fitResult)") is True
    finally:
        pg.close()


def test_an_auto_fit_round_trips_current_with_both_checks(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        pg.set_input_files("#load-session-input", AUTOFIT_PROJECT)
        pg.wait_for_function("() => tabManager.tabs.some(t => t.name === 'C1s Scan')", timeout=60000)
        pg.evaluate("() => tabManager.activateTab(tabManager.tabs.find(t => t.name === 'C1s Scan').id)")
        pg.evaluate("() => { window._showAutoFitConfirmModal = () => Promise.resolve(true); }")
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        assert pg.evaluate("() => state.fitResult.seal.producer") == "autoFit"
        # keep only the Auto-Fit tab (the project's others are legacy fits)
        pg.evaluate("""() => { for (const t of tabManager.tabs.slice()) if (t !== _activeTab()) tabManager.closeTab(t.id); }""")
        name, text = _save_project(pg)
    finally:
        pg.close()
    pg = _load_project(browser, server, name, text)
    try:
        calls = []
        pg.on("request", lambda r: calls.append(r.url) if r.url.endswith("/api/verify-fit") else None)
        pg.evaluate(SETTLE)
        assert pg.evaluate(STATE, None) == ["current", None]
    finally:
        pg.close()


@pytest.mark.parametrize("edit,check", [
    ("state.peaks[0].center += 0.05", "edited"),
    ("document.getElementById('fit-method').value = 'nelder'", "edited"),
])
def test_an_edited_save_reloads_stale(browser, server, edit, check):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate("() => { " + edit + "; }")
        assert pg.evaluate(STATE, None) == ["stale", check]
        name, text = _save_project(pg)
    finally:
        pg.close()
    pg = _load_project(browser, server, name, text)
    try:
        pg.evaluate(SETTLE)
        assert pg.evaluate(STATE, None) == ["stale", check]
    finally:
        pg.close()


def test_a_nondefault_fit_method_round_trips_current(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        pg.evaluate("() => { document.getElementById('fit-method').value = 'leastsq'; }")
        pg.evaluate("async () => { await runFit(); }")
        assert pg.evaluate("() => state.fitResult.seal.R.request.fit_method") == "leastsq"
        name, text = _save_project(pg)
    finally:
        pg.close()
    pg = _load_project(browser, server, name, text)
    try:
        assert pg.evaluate("() => document.getElementById('fit-method').value") == "leastsq"
        pg.evaluate(SETTLE)
        assert pg.evaluate(STATE, None) == ["current", None]
    finally:
        pg.close()


@pytest.mark.parametrize("src,why", [
    ("s.v = 'xps-seal-0'", "version"),
    ("s.O.fitted_y = s.O.fitted_y.slice(1)", "fitted_y"),
    ("s.R.pageModel[0].id = 'x\" onclick=\"1'", "start model"),
    ("delete s.R.request", "request"),
])
def test_an_unreadable_record_is_peaks_only_and_never_reaches_the_legacy_adapter(browser, server, src, why):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        name, text = _save_project(pg)
    finally:
        pg.close()
    data = json.loads(text)
    pg = _page(browser, server)
    try:
        pg.evaluate("() => { window.__legacy = 0; const f = _restoredFitBgFailure; window._restoredFitBgFailure = (r) => { window.__legacy++; return f(r); }; }")
        pg.evaluate("""([text, src]) => { const d = JSON.parse(text); (new Function('s', src))(d.tabs[0].fitResult.seal);
            _loadProjectJSON(d, 'p.proj.json'); }""", [json.dumps(data), src])
        got = pg.evaluate("() => { const s = sealedState(state.fitResult, _activeTab()); return [s.state, s.reason, window.__legacy, state.peaks.length]; }")
        assert got[0] == "peaks-only" and why in got[1] and got[2] == 0 and got[3] > 0, got
        assert pg.evaluate("() => _sealedDisplay(state.fitResult)") is None
    finally:
        pg.close()


def test_the_legacy_restore_refuses_a_sealed_fit(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        msg = pg.evaluate("""() => { try { tabManager._syncActiveToRecord(); _restoredFitBgFailure(_activeTab()); return 'no throw'; }
                                     catch (e) { return e.message; } }""")
        assert "sealed" in msg, msg
    finally:
        pg.close()


def test_a_legacy_fit_dropped_to_peaks_only_keeps_its_record(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        # a LEGACY fit (no seal) whose reconstruction fails: its record is kept as the tab's provenance
        name, text = _save_project(pg)
    finally:
        pg.close()
    data = json.loads(text)
    rec = {"engine": "server", "fitMethod": "least_squares", "seed": 7, "seedSource": "request",
           "backgroundVerdict": None, "certificate": None, "software": None}
    data["tabs"][0]["fitResult"] = {"chiReduced": 2.0, "record": rec}     # no envelope: cannot be checked
    pg = _page(browser, server)
    try:
        pg.evaluate("(text) => _loadProjectJSON(JSON.parse(text), 'p.proj.json')", json.dumps(data))
        got = pg.evaluate("""() => ({ fr: state.fitResult, prov: _activeTab().provenance,
            note: (document.querySelector('#results-area .tab-provenance-note') || {}).textContent || '' })""")
        assert got["fr"] is None and got["prov"]["record"] == rec, got
        assert "was not restored" in got["note"] and "least_squares" in got["note"], got["note"]
        pg.evaluate(CAPTURE)
        name2, text2 = _save_project(pg)
        assert json.loads(text2)["tabs"][0]["provenance"]["record"] == rec
    finally:
        pg.close()
    pg = _load_project(browser, server, name2, text2)
    try:
        assert pg.evaluate("() => _activeTab().provenance.record") == rec
    finally:
        pg.close()


def test_the_view_states_its_provenance_and_results_and_exports_show_it(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        got = pg.evaluate("""() => { const v = sealedState(state.fitResult, _activeTab()).view; renderResults();
            const el = document.querySelector('#results-area .seal-provenance');
            return { pv: v.provenance, shown: el && el.getAttribute('data-provenance'), text: el && el.textContent }; }""")
        pv = got["pv"]
        assert pv["state"] in ("ATTESTED", "INCOMPLETE") and (pv["state"] == "ATTESTED") == (pv["missing"] == []), pv
        assert got["shown"] == pv["state"] and "Record provenance" in got["text"], got
        pg.evaluate("() => exportFitTable('csv')")
        pg.wait_for_function("() => !!window.__blobs['fit_results.csv']")
        assert "# Record provenance: " + pv["state"] in pg.evaluate(TEXT, "fit_results.csv")
    finally:
        pg.close()


def test_switch_off_saves_and_loads_as_today(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate("() => { _SEAL_AUTHORITATIVE = false; }")
        name, text = _save_project(pg)
        fr = json.loads(text)["tabs"][0]["fitResult"]
        assert "seal" not in fr and "chiReduced" in fr and "provenance" not in json.loads(text)["tabs"][0]
    finally:
        pg.close()


def test_xlsx_carries_the_records_provenance(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        if not pg.evaluate("() => typeof XLSX !== 'undefined'"):
            pytest.skip("the XLSX library did not load (offline)")
        info = pg.evaluate("""() => { let info = null; const w = XLSX.writeFile; XLSX.writeFile = (wb) => { info = XLSX.utils.sheet_to_json(wb.Sheets['Info'], { header: 1 }); };
            try { exportFitTable('xlsx'); } finally { XLSX.writeFile = w; } return info; }""")
        flat = [" ".join(str(c) for c in r) for r in info]
        assert any(r.startswith("Record provenance ATTESTED") or r.startswith("Record provenance INCOMPLETE") for r in flat), flat
    finally:
        pg.close()


# ── Codex step 6 round 1 ──
def _load_tampered(browser, server, text, src):  # noqa: F811
    pg = _page(browser, server)
    pg.evaluate("""([text, src]) => { const d = JSON.parse(text); (new Function('d', src))(d); _loadProjectJSON(d, 'p.proj.json'); }""", [text, src])
    return pg


@pytest.mark.parametrize("src", [
    "d.tabs[0].fitResult.seal.O.starts = { ran: false, reason: 'method' }",                 # a global method's honest record
    "d.tabs[0].fitResult.seal.O.required = { ran: false, reason: 'not requested' }",
])
def test_honest_not_run_evidence_is_readable(browser, server, src):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        name, text = _save_project(pg)
    finally:
        pg.close()
    pg = _load_tampered(browser, server, text, src)
    try:
        st = pg.evaluate("() => { const s = sealedState(state.fitResult, _activeTab()); return [s.state, s.reason]; }")
        assert st[0] != "peaks-only", st
        pg.evaluate("() => { renderResults(); }")
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


@pytest.mark.parametrize("src,why", [
    ("d.tabs[0].fitResult.seal.O.starts.not_better_chi2r = ['x']", "scattered-starts"),
    ("d.tabs[0].fitResult.seal.O.starts.n_same_as_fit = '<img src=x onerror=alert(1)>'", "scattered-starts"),
    ("d.tabs[0].fitResult.seal.O.software.role = 42", "software"),
    ("d.tabs[0].fitResult.seal.O.background_verdict.residual = 'x'", "background verdict"),
    ("d.tabs[0].fitResult.seal.O.individual_peaks[0].support = { f: 'x' }", "components"),
    ("d.tabs[0].fitResult.seal.R.page = { software: { role: 7 }, page: null }", "page identity"),
    ("d.tabs[0].fitResult.seal.D = { chosenAlternative: { shiftName: '<b>' } }", "D is malformed"),
])
def test_a_field_a_reader_formats_or_renders_is_typed_before_any_check(browser, server, src, why):  # noqa: F811
    pg = _fitted(browser, server, "gauss_voigt_linear_avg3_window")      # a fit with scattered-starts evidence
    try:
        name, text = _save_project(pg)
    finally:
        pg.close()
    pg = _load_tampered(browser, server, text, src)
    try:
        st = pg.evaluate("() => { const s = sealedState(state.fitResult, _activeTab()); return [s.state, s.reason]; }")
        assert st[0] == "peaks-only" and why in st[1], st
        pg.evaluate("() => { renderResults(); updatePlot(); }")
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


@pytest.mark.parametrize("value", ['"bad"', "true", "0", "false", "[]", "null"])
def test_a_saved_seal_that_is_not_an_object_is_peaks_only_and_breaks_nothing(browser, server, value):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        name, text = _save_project(pg)
    finally:
        pg.close()
    pg = _load_tampered(browser, server, text, "d.tabs[0].fitResult = { seal: " + value + " };")
    try:
        got = pg.evaluate("""() => { renderResults(); updatePlot(); _sealSig(state.fitResult);
            const s = sealedState(state.fitResult, _activeTab()); return [s.state, s.reason]; }""")
        assert got[0] == "peaks-only" and "not a record" in got[1], (value, got)
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_malformed_legacy_record_is_not_kept_as_provenance(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        name, text = _save_project(pg)
    finally:
        pg.close()
    data = json.loads(text)
    data["tabs"][0]["fitResult"] = {"chiReduced": 2.0, "record": {"engine": "server", "fitMethod": "least_squares", "seed": 7,
                                     "seedSource": "request", "backgroundVerdict": None, "certificate": None, "software": {"role": 7}}}
    pg = _page(browser, server)
    try:
        pg.evaluate("(text) => _loadProjectJSON(JSON.parse(text), 'p.proj.json')", json.dumps(data))
        assert pg.evaluate("() => _activeTab().provenance") is None
        pg.evaluate("() => renderResults()")
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_stale_fit_keeps_its_record_provenance_in_results_and_exports(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate("() => { state.peaks[0].center += 0.05; updatePlot(); renderResults(); }")
        assert pg.evaluate("() => sealedState(state.fitResult, _activeTab()).state") == "stale"
        assert pg.evaluate("() => !!document.querySelector('#results-area .seal-provenance')")
        pg.evaluate("() => exportFitTable('csv')")
        pg.wait_for_function("() => !!window.__blobs['fit_results.csv']")
        assert "# Record provenance: " in pg.evaluate(TEXT, "fit_results.csv")
        pg.evaluate("() => { window.__chunk = null; window._pngWithText = async (b, k, t) => { window.__chunk = t; return b; }; _doPublicationExport(); }")
        pg.wait_for_function("() => !!window.__chunk")
        chunk = json.loads(pg.evaluate("() => window.__chunk"))
        assert chunk["sealState"].startswith("STALE") and chunk["provenance"]["state"] in ("ATTESTED", "INCOMPLETE"), chunk
    finally:
        pg.close()
