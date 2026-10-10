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


def _json_row(rows):
    """The lossless 'Fit record (JSON)' entry of an export's (label, text) rows."""
    hits = [json.loads(t) for k, t in rows if k == "Fit record (JSON)"]
    assert len(hits) == 1, rows
    return hits[0]


def _comment_rows(text):
    return [tuple(l[2:].split(": ", 1)) for l in text.splitlines() if l.startswith("# ") and ": " in l]


def test_the_exports_carry_the_whole_record(browser, server):
    pg = _new_page(browser, server)
    try:
        rec, _ = _fit(pg)
        csv = _download(pg, "() => exportFitTable('csv')")
        # XLSX: the SERIALISED workbook, read back (Codex round 1: not the in-memory sheet)
        pg.evaluate("""() => { window.__xlsx = null; XLSX.writeFile = wb => {
            const bytes = XLSX.write(wb, { type: 'array', bookType: 'xlsx' });
            const back = XLSX.read(bytes, { type: 'array' });
            window.__xlsx = XLSX.utils.sheet_to_json(back.Sheets['Info'], { header: 1 }); }; }""")
        pg.evaluate("() => exportFitTable('xlsx')")
        info = pg.evaluate("() => window.__xlsx")
        pg.evaluate("""() => { window.__tsv = null; const o = URL.createObjectURL;
            URL.createObjectURL = b => { b.text().then(t => { window.__tsv = t; }); return o(b); }; }""")
        pg.evaluate("() => exportResults()")
        pg.wait_for_function("() => window.__tsv !== null", timeout=20000)
        tsv = pg.evaluate("() => window.__tsv")
    finally:
        pg.close()
    # losslessly, in every export
    assert _json_row(_comment_rows(csv)) == rec
    assert _json_row(_comment_rows(tsv)) == rec
    assert _json_row([tuple(r[:2]) for r in info if len(r) >= 2]) == rec
    # and the readable summary
    want = {"Fit method": "least_squares", "Random seed": f"{rec['seed']} (request)"}
    for label, text in want.items():
        assert f"# {label}: {text}" in csv and f"# {label}: {text}" in tsv and [label, text] in info, label
    assert "shirley: converged (defining statement" in csv and "certified" in csv and rec["software"]["git_commit"] in csv
    assert f"numerics {rec['software']['numerics']}" in csv


def test_the_figure_png_carries_the_record(browser, server):
    import base64, struct, zlib
    pg = _new_page(browser, server)
    try:
        rec, _ = _fit(pg)
        pg.evaluate("""() => { window.__png = null; window._downloadBlob = async (blob, name) => {
            const b = new Uint8Array(await blob.arrayBuffer()); let s = '';
            for (let i = 0; i < b.length; i++) s += String.fromCharCode(b[i]); window.__png = btoa(s); }; }""")
        pg.evaluate("() => _doPublicationExport()")
        pg.wait_for_function("() => window.__png !== null", timeout=30000)
        png = base64.b64decode(pg.evaluate("() => window.__png"))
    finally:
        pg.close()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    pos, chunks = 8, []
    while pos < len(png):
        n, = struct.unpack(">I", png[pos:pos + 4])
        typ, data, crc = png[pos + 4:pos + 8], png[pos + 8:pos + 8 + n], png[pos + 8 + n:pos + 12 + n]
        assert struct.unpack(">I", crc)[0] == zlib.crc32(typ + data), f"bad CRC in {typ}"   # a valid PNG
        chunks.append((typ, data))
        pos += 12 + n
    assert chunks[0][0] == b"IHDR" and chunks[-1][0] == b"IEND"
    itxt = [d for t, d in chunks if t == b"iTXt" and d.startswith(b"XPS-Fit-Record\0")]
    assert len(itxt) == 1
    text = itxt[0][len(b"XPS-Fit-Record\0") + 4:]          # flag 0, method 0, empty language, empty translation
    assert json.loads(text.decode("utf-8")) == rec


def test_a_fit_json_carries_the_record_and_an_import_keeps_it_as_provenance(browser, server):
    pg = _new_page(browser, server)
    try:
        rec, _ = _fit(pg)
        fj = json.loads(_download(pg, "() => _doSaveFit()"))
        assert fj["fitStatistics"]["record"] == rec
        # import onto another spectrum: parameters only, no fit — the record is the parameters' provenance
        pg.evaluate(PEAK_TAB)
        pg.evaluate("data => tabManager.fromJSON(data)", fj)
        got = pg.evaluate("() => ({ fit: state.fitResult, prov: (_activeTab() || {}).modelProvenance, local: _isLocalModel() })")
        assert got["fit"] is None and got["local"] is False
        assert got["prov"] == {"importedFrom": "fit.json", "record": rec}
        proj = json.loads(_download(pg, "() => _doSaveProject()"))
        spec = json.loads(_download(pg, "() => _doSaveSpectrum()"))
    finally:
        pg.close()
    assert any(t.get("modelProvenance") == {"importedFrom": "fit.json", "record": rec} for t in proj["tabs"])
    assert spec["modelProvenance"] == {"importedFrom": "fit.json", "record": rec}
    pg = _new_page(browser, server)
    try:
        pg.evaluate("data => _loadSpectrumFile(data, 'i.spec.json')", spec)
        pg.wait_for_timeout(300)
        assert pg.evaluate("() => (_activeTab() || {}).modelProvenance") == {"importedFrom": "fit.json", "record": rec}
    finally:
        pg.close()


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
    assert rec["engine"] == "local" and rec["fitMethod"] == "local_lm" and rec["seed"] is None
    c = rec["certificate"]
    assert c["check"] == "coordinate" and isinstance(c["restarts"], int) and isinstance(c["moved"], bool)
    assert isinstance(c["centre_moves"], list) and len(c["centre_moves"]) == 2 and all(isinstance(m["ev"], float) or m["ev"] == 0 for m in c["centre_moves"])
    assert c["largest_centre_move"] in c["centre_moves"]
    bv = rec["backgroundVerdict"]
    assert bv["method"] == "shirley" and bv["check"] == "page_certificate" and bv["converged"] is True and isinstance(bv["residual"], float)
    # the software that served the page (its <meta name="xps-software">)
    sw = rec["software"]
    assert sw["role"] == "served_the_page" and len(sw["git_commit"]) == 40 and sw["numerics"] and sw["numpy"]


@pytest.mark.parametrize("bg,start,end,avg,anchors", [
    ("shirley", 292, 280, 3, None), ("shirley", 289, 281, 10, None), ("smart", 292, 280, 50, None),
    ("tougaard", 292, 280, 1, None), ("linear", 290, 281, 3, None),
    ("manual", 292, 280, 3, [[291.7, 700], [280.3, 300], [286.0, 450]]), ("manual", 292, 280, 3, []),
    ("none", 292, 280, 3, None)])
def test_the_page_records_the_background_by_its_effect_as_the_server_does(browser, server, bg, start, end, avg, anchors):
    # two readings of one field: the local engine's record states the background exactly as the
    # server's verdict states the background of the SAME settings (fitting._background_effect:
    # window end exclusive, averaging as it acts, anchors in energy order)
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("""([bg, s, e, avg, anchors]) => {
            document.getElementById('bg-start').value = s; document.getElementById('bg-end').value = e;
            document.getElementById('bg-endpoint-avg').value = avg;
            document.getElementById('bg-type').value = bg; _onBgTypeChange();
            if (anchors) _setManualAnchors(anchors.map(([x, y]) => ({ x, y })));
            updatePlot(); }""", [bg, start, end, avg, anchors])
        pg.evaluate("() => { document.getElementById('fit-method').value = 'least_squares'; }")
        assert pg.evaluate(FIT)
        server_rec = pg.evaluate(RECORD)
        assert server_rec["engine"] == "server"
        pg.evaluate("""() => { const { be, inten } = getROIData(); const b = computeBackground(be, inten);
            runFitLocal(be, inten.map((v, i) => v - b[i]), b); }""")
        local_rec = pg.evaluate(RECORD)
    finally:
        pg.close()
    assert local_rec["engine"] == "local"
    sv, lv = server_rec["backgroundVerdict"], local_rec["backgroundVerdict"]
    assert lv["effect"] == sv["effect"], (lv, sv)
    assert lv["method"] == sv["method"] == bg and lv["converged"] is sv["converged"] is True
    assert lv["check"] == ("explicit" if sv["check"] == "explicit" else "page_certificate")
    if bg == "manual" and anchors:
        assert sv["effect"] == {"method": "manual", "anchors": sorted(anchors)}
    elif bg == "manual":
        assert sv["effect"]["method"] == "manual-line"
    elif bg != "none":
        assert sv["effect"]["method"] == bg and sv["effect"]["k"] == min(avg, (sv["effect"]["window"][1] - sv["effect"]["window"][0]) // 4)


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
