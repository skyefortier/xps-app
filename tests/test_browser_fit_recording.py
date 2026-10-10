"""Real browser, real server (owner 2026-10-10): every fit carries its RECORD — the method, the
seed and where it came from, the background's verdict, the whole certificate, the software —
and the page saves it with the fit (projects, spectrum files), restores it on load, and writes
it to the exports (CSV, XLSX, TSV). Old saves without it load exactly as before. RECORDING ONLY:
nothing reads it to decide current / stale. And the saved seed re-runs the fit: the request the
page sent, sent again with the seed read back from the save, reproduces the fit within rounding
(tests/fit_equality.py). (This unit records the seed, not the request's starting values — the
request below is the one captured from the page's own fetch; recording the request is the
sealed-fit design's v6.) Skips cleanly when Playwright / Chromium / gunicorn are absent."""
import json

import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import _new_page, browser, server  # noqa: E402,F401
from test_browser_background_not_converged import CAPTURE, PEAK_TAB  # noqa: E402
from fit_equality import assert_same_fit  # noqa: E402

# capture the fit request the page sends (the start route carries exactly the /api/fit body)
SPY = """() => { window.__req = null; const o = window.fetch;
    window.fetch = (url, opts) => { if (String(url).includes('/api/fit/start')) window.__req = JSON.parse(opts.body); return o(url, opts); }; }"""
FIT = """async () => { await runFit(); return !!state.fitResult; }"""
RECORD = "() => state.fitResult && state.fitResult.record"
BACKEND = """() => { const r = state.fitResult.backendResult; return { fit_method: r.fit_method, random_seed: r.random_seed,
    seed_source: r.seed_source, background_verdict: r.background_verdict, certificate: r.certificate, software: r.software }; }"""


def _fit(pg):
    pg.evaluate(PEAK_TAB)
    pg.evaluate("() => { document.getElementById('fit-method').value = 'least_squares'; }")
    pg.evaluate(SPY)
    assert pg.evaluate(FIT)
    return pg.evaluate(RECORD), pg.evaluate(BACKEND)


def _download(pg, action):
    pg.evaluate(CAPTURE)
    pg.evaluate(action)
    pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
    return pg.evaluate("() => window.__dl[0].text")


def test_a_server_fit_records_the_servers_own_fields(browser, server):
    pg = _new_page(browser, server)
    try:
        rec, br = _fit(pg)
        assert rec == {"engine": "server", "fitMethod": br["fit_method"], "seed": br["random_seed"],
                       "seedSource": br["seed_source"], "backgroundVerdict": br["background_verdict"],
                       "certificate": br["certificate"], "software": br["software"]}
        assert rec["fitMethod"] == "least_squares" and rec["seedSource"] == "request" and isinstance(rec["seed"], int)
        assert rec["backgroundVerdict"]["method"] == "shirley" and rec["backgroundVerdict"]["converged"] is True
        assert rec["certificate"]["certified"] is True and "restarts" in rec["certificate"]
        assert len(rec["software"]["git_commit"]) == 40 and rec["software"]["seed_derivation"] == "xps-fit-seed-v2"
    finally:
        pg.close()


def test_the_record_round_trips_through_a_project_and_a_spectrum_file(browser, server):
    pg = _new_page(browser, server)
    try:
        rec, _ = _fit(pg)
        proj = json.loads(_download(pg, "() => _doSaveProject()"))
        spec = json.loads(_download(pg, "() => _doSaveSpectrum()"))
    finally:
        pg.close()
    saved_tab = next(t for t in proj["tabs"] if not t.get("isStack") and t.get("fitResult"))
    assert saved_tab["fitResult"]["record"] == rec
    assert spec["statistics"]["record"] == rec
    for loader, data, name in (("_loadProjectJSON", proj, "r.proj.json"), ("_loadSpectrumFile", spec, "r.spec.json")):
        pg = _new_page(browser, server)
        try:
            pg.evaluate(f"data => {loader}(data, '{name}')", data)
            pg.wait_for_timeout(500)
            assert pg.evaluate(RECORD) == rec, loader
            assert pg.evaluate("() => _statsLiveState()") == "current", f"{loader}: the fit restores as it did before"
        finally:
            pg.close()


def test_a_seed_of_zero_survives_the_spectrum_loader(browser, server):
    # the spectrum loader copies most statistics fields only when truthy: the record is copied explicitly
    pg = _new_page(browser, server)
    try:
        _fit(pg)
        spec = json.loads(_download(pg, "() => _doSaveSpectrum()"))
    finally:
        pg.close()
    spec["statistics"]["record"]["seed"] = 0
    pg = _new_page(browser, server)
    try:
        pg.evaluate("data => _loadSpectrumFile(data, 'z.spec.json')", spec)
        pg.wait_for_timeout(500)
        assert pg.evaluate(RECORD)["seed"] == 0
    finally:
        pg.close()


def test_the_exports_carry_the_record(browser, server):
    pg = _new_page(browser, server)
    try:
        rec, _ = _fit(pg)
        csv = _download(pg, "() => exportFitTable('csv')")
        pg.evaluate("""() => { window.__xlsx = null; XLSX.writeFile = wb => { window.__xlsx = XLSX.utils.sheet_to_json(wb.Sheets['Info'], { header: 1 }); }; }""")
        pg.evaluate("() => exportFitTable('xlsx')")
        info = pg.evaluate("() => window.__xlsx")
        pg.evaluate("""() => { window.__tsv = null; const o = URL.createObjectURL;
            URL.createObjectURL = b => { b.text().then(t => { window.__tsv = t; }); return o(b); }; }""")
        pg.evaluate("() => exportResults()")
        pg.wait_for_function("() => window.__tsv !== null", timeout=20000)
        tsv = pg.evaluate("() => window.__tsv")
    finally:
        pg.close()
    want = {"Fit method": "least_squares", "Random seed": f"{rec['seed']} (request)"}
    for label, text in want.items():
        assert f"# {label}: {text}" in csv, label
        assert f"# {label}: {text}" in tsv, label
        assert [label, text] in info, label
    for label in ("Background check", "Minimum certificate", "Software"):
        assert f"# {label}: " in csv and f"# {label}: " in tsv and any(r and r[0] == label for r in info), label
    assert "shirley: converged (defining statement" in csv and "certified" in csv and rec["software"]["git_commit"] in csv


def test_an_older_save_without_a_record_loads_as_before(browser, server):
    pg = _new_page(browser, server)
    try:
        _fit(pg)
        proj = json.loads(_download(pg, "() => _doSaveProject()"))
    finally:
        pg.close()
    for t in proj["tabs"]:
        if t.get("fitResult"):
            t["fitResult"].pop("record", None)
    pg = _new_page(browser, server)
    try:
        pg.evaluate("data => _loadProjectJSON(data, 'old.proj.json')", proj)
        pg.wait_for_timeout(500)
        assert pg.evaluate(RECORD) is None
        assert pg.evaluate("() => _statsLiveState()") == "current", "the legacy rule is unchanged"
        csv = _download(pg, "() => exportFitTable('csv')")
        assert "# Fit method:" not in csv
    finally:
        pg.close()


def test_the_local_engine_records_its_own(browser, server):
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("""() => { const { be, inten } = getROIData(); const bg = computeBackground(be, inten);
            runFitLocal(be, inten.map((v, i) => v - bg[i]), bg); }""")
        rec = pg.evaluate(RECORD)
    finally:
        pg.close()
    assert rec["engine"] == "local" and rec["fitMethod"] == "local_lm" and rec["seed"] is None and rec["software"] is None
    assert rec["certificate"]["check"] == "coordinate" and isinstance(rec["certificate"]["restarts"], int)
    assert rec["backgroundVerdict"] == {"method": "shirley", "check": "page_certificate", "converged": True, "residual": None, "reason": ""}


def test_a_re_run_with_the_saved_seed_reproduces_the_fit(browser, server):
    import urllib.request
    pg = _new_page(browser, server)
    try:
        _fit(pg)
        req = pg.evaluate("() => window.__req")
        first = pg.evaluate("() => state.fitResult.backendResult")
        proj = json.loads(_download(pg, "() => _doSaveProject()"))
    finally:
        pg.close()
    assert req and "seed" not in req, "the page's own request: the seed was derived"
    pg = _new_page(browser, server)
    try:
        pg.evaluate("data => _loadProjectJSON(data, 'r.proj.json')", proj)
        pg.wait_for_timeout(500)
        seed = pg.evaluate(RECORD)["seed"]
    finally:
        pg.close()
    body = json.dumps({**req, "seed": seed}).encode()
    again = json.loads(urllib.request.urlopen(urllib.request.Request(server + "/api/fit", data=body,
                                              headers={"Content-Type": "application/json"}), timeout=300).read())
    assert again["random_seed"] == first["random_seed"] == seed and again["seed_source"] == "caller"
    assert_same_fit({**first, "seed_source": None}, {**again, "seed_source": None})
