"""The fit record FOLLOWS every export's existing content (owner 2026-10-10): students'
spreadsheets and scripts read the same lines, rows and columns they read before. The same
saved fit is loaded into the page as deployed before the record (main 52e5b4a, rendered from
git) and into this page, and each exports CSV, TSV and XLSX: the earlier CSV and TSV are an
EXACT PREFIX of today's (then a blank line and the record's '#' lines), and both XLSX sheets
agree row for row, the record's rows following the Info sheet's. Each record line is ONE cell
to Python's csv, pandas and either delimiter, and a reader skipping '#' comments reads exactly
what it read before. (Excel is not driven here — its automation needs an interactive
permission; each line holds no comma, double quote, tab or line break, so under RFC 4180 it is
one cell to any delimiter-based reader.)"""
import base64
import csv
import io
import json
import re
import subprocess

import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import REPO_ROOT, _new_page, browser, server  # noqa: E402,F401
from test_browser_fit_recording import RECORD, _download, _fit  # noqa: E402
from test_browser_background_not_converged import PEAK_TAB  # noqa: E402

BEFORE = "52e5b4a"   # main as deployed before the fit record

XLSX_HOOK = """() => { window.__xlsx = null; XLSX.writeFile = wb => {
    const back = XLSX.read(XLSX.write(wb, { type: 'array', bookType: 'xlsx' }), { type: 'array' });
    window.__xlsx = Object.fromEntries(back.SheetNames.map(n => [n, XLSX.utils.sheet_to_json(back.Sheets[n], { header: 1, defval: null })])); }; }"""
TSV_HOOK = """() => { window.__tsv = null; const o = URL.createObjectURL;
    URL.createObjectURL = b => { if (String(b.type).includes('tab-separated')) b.text().then(t => { window.__tsv = t; }); return o(b); }; }"""


@pytest.fixture(scope="module")
def before_html():
    try:
        src = subprocess.run(["git", "-C", REPO_ROOT, "show", f"{BEFORE}:templates/index.html"],
                             capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.fail(f"commit {BEFORE} is not in this checkout (CI checks out full history for this test)")
    from app import create_app
    from xps_reference import load_reference_cached
    app = create_app()
    with app.test_request_context("/"):
        legacy = load_reference_cached(app.config["XPS_DATA_DIR"]).get("legacy")
        return app.jinja_env.from_string(src).render(legacy_reference=legacy)


def _exports(pg, project):
    if project is None:
        # a local fit (it saves no fitted envelope, so a project reloads it peaks-only, on both
        # pages): run the local engine itself — deterministic page code, unchanged by the record
        pg.evaluate(PEAK_TAB)
        assert pg.evaluate("""() => { const { be, inten } = getROIData(); const b = computeBackground(be, inten);
            return runFitLocal(be, inten.map((v, i) => v - b[i]), b).success; }""")
    else:
        pg.evaluate("data => _loadProjectJSON(data, 'p.proj.json')", project)
        pg.wait_for_timeout(500)
    out = {"csv": _download(pg, "() => exportFitTable('csv')")}
    pg.evaluate(TSV_HOOK)
    pg.evaluate("() => exportResults()")
    pg.wait_for_function("() => window.__tsv !== null", timeout=20000)
    out["tsv"] = pg.evaluate("() => window.__tsv")
    pg.evaluate(XLSX_HOOK)
    pg.evaluate("() => exportFitTable('xlsx')")
    out["xlsx"] = pg.evaluate("() => window.__xlsx")
    out["record"] = pg.evaluate(RECORD)
    return out


def _project(browser, server, local):
    if local:
        return None
    pg = _new_page(browser, server)
    try:
        _fit(pg)
        return json.loads(_download(pg, "() => _doSaveProject()"))
    finally:
        pg.close()


def _record_lines(tail):
    assert tail.startswith("\n\n"), repr(tail[:40])
    lines = tail[2:].split("\n")
    assert lines and all(l.startswith("# ") for l in lines), lines
    for l in lines:
        assert not any(c in l for c in ',"\t\r'), l   # one cell to every reader
    return lines


PART = re.compile(r"^# Fit record \(JSON base64 part (\d+) of (\d+)\): (.*)$")


def _decoded(lines):
    """The record from its numbered base64 parts (in order, all of them)."""
    parts = [PART.match(l) for l in lines if l.startswith("# Fit record")]
    assert parts and all(parts), lines
    n = int(parts[0].group(2))
    assert [(int(m.group(1)), int(m.group(2))) for m in parts] == [(i + 1, n) for i in range(n)]
    return json.loads(base64.b64decode("".join(m.group(3) for m in parts)).decode("utf-8"))


def _xlsx_record(extra):
    cells = [r for r in extra if r and str(r[0]).startswith("Fit record (JSON part ")]
    n = len(cells)
    assert [r[0] for r in cells] == [f"Fit record (JSON part {i + 1} of {n})" for i in range(n)]
    assert all(len(r[1]) <= 32767 for r in cells)
    return json.loads("".join(r[1] for r in cells))


@pytest.mark.parametrize("local", [False, True], ids=["server-fit", "local-fit"])
def test_the_record_follows_every_existing_line_row_and_column(browser, server, before_html, local):
    project = _project(browser, server, local)
    pg = _new_page(browser, server)
    try:
        now = _exports(pg, project)
    finally:
        pg.close()
    pg = browser.new_page(viewport={"width": 1000, "height": 1000})
    try:
        pg.route(server + "/", lambda route: route.fulfill(status=200, content_type="text/html; charset=utf-8", body=before_html))
        pg.goto(server + "/", wait_until="load")
        assert pg.evaluate("() => typeof _fitRecordRows") == "undefined", "the page before the record"
        then = _exports(pg, project)
    finally:
        pg.close()
    rec = now["record"]
    assert rec and rec["engine"] == ("local" if local else "server")
    for fmt in ("csv", "tsv"):
        assert now[fmt].startswith(then[fmt]), f"{fmt}: an existing line moved or changed"
        lines = _record_lines(now[fmt][len(then[fmt]):])
        assert _decoded(lines) == rec, fmt
        assert len(lines) == (5 if local else 6)
    # XLSX: every sheet the same, row for row; the record's rows follow the Info sheet's
    assert list(now["xlsx"]) == list(then["xlsx"]) == ["Info", "Fit Results"]
    assert now["xlsx"]["Fit Results"] == then["xlsx"]["Fit Results"]
    info_now, info_then = now["xlsx"]["Info"], then["xlsx"]["Info"]
    assert info_now[:len(info_then)] == info_then
    # the blank row that ended the Info sheet is still there (a reader drops a TRAILING blank row,
    # so the earlier sheet reads back without it), then the record's rows
    assert all(v is None for v in info_now[len(info_then)]), info_now[len(info_then)]
    extra = info_now[len(info_then) + 1:]
    assert _xlsx_record(extra) == rec
    assert [r[0] for r in extra] == [k for k in ("Fit method", "Random seed", "Background check", "Minimum certificate",
                                                   "Software", "Fit record (JSON part 1 of 1)") if not (local and k == "Random seed")]


def test_each_record_line_is_one_cell_to_every_reader_and_a_comment_to_a_comment_reader(browser, server, before_html):
    import pandas as pd
    project = _project(browser, server, False)
    pg = _new_page(browser, server)
    try:
        now = _exports(pg, project)
    finally:
        pg.close()
    pg = browser.new_page(viewport={"width": 1000, "height": 1000})
    try:
        pg.route(server + "/", lambda route: route.fulfill(status=200, content_type="text/html; charset=utf-8", body=before_html))
        pg.goto(server + "/", wait_until="load")
        then = _exports(pg, project)
    finally:
        pg.close()
    rec = now["record"]
    for fmt, sep in (("csv", ","), ("tsv", "\t")):
        text = now[fmt]
        # Python's csv module: each record line is one cell; the JSON decodes to the record
        rows = list(csv.reader(io.StringIO(text), delimiter=sep))
        tail = [r for r in rows if r and r[0].startswith("# ") and r[0][2:].split(":")[0] in
                ("Fit method", "Random seed", "Background check", "Minimum certificate", "Software", "Fit record (JSON base64 part 1 of 1)")]
        assert len(tail) == 6 and all(len(r) == 1 for r in tail), (fmt, tail)
        assert _decoded([r[0] for r in tail]) == rec
        # pandas without comment handling: one non-empty cell per record line
        width = max(len(r) for r in rows)
        df = pd.read_csv(io.StringIO(text), sep=sep, header=None, names=range(width), skip_blank_lines=True, dtype=str)
        rec_rows = df[df[0].fillna("").str.startswith("# Fit record (JSON base64 part ")]
        assert len(rec_rows) == 1 and rec_rows.iloc[0, 1:].isna().all(), fmt
        # pandas skipping '#' comments: exactly the table it read before the record existed
        a, b = (pd.read_csv(io.StringIO(t), sep=sep, comment="#") for t in (text, then[fmt]))
        pd.testing.assert_frame_equal(a, b)


def test_a_record_of_any_size_stays_within_every_readers_limit(browser, server):
    # Codex recording round 5: 4 000 manual-background anchors (a crafted import; the page caps
    # anchors at 20) made a 207 352-character line Python's csv refuses (field limit 131 072) and
    # a 155 491-character XLSX cell (Excel holds 32 767). The record is split into numbered parts.
    import pandas as pd
    pg = _new_page(browser, server)
    try:
        _fit(pg)
        pg.evaluate("""() => { const bv = state.fitResult.record.backgroundVerdict;
            bv.effect = { method: 'manual', anchors: Array.from({ length: 8000 }, (_, i) => [280 + i * 0.00125, 1000 + i / 7]) }; }""")
        rec = pg.evaluate(RECORD)
        text = {"csv": _download(pg, "() => exportFitTable('csv')")}
        pg.evaluate(TSV_HOOK)
        pg.evaluate("() => exportResults()")
        pg.wait_for_function("() => window.__tsv !== null", timeout=20000)
        text["tsv"] = pg.evaluate("() => window.__tsv")
        pg.evaluate(XLSX_HOOK)
        pg.evaluate("() => exportFitTable('xlsx')")
        info = pg.evaluate("() => window.__xlsx")["Info"]
    finally:
        pg.close()
    # larger than one field may be, even before base64
    assert len(json.dumps(rec, separators=(",", ":"), ensure_ascii=False)) > 131072
    for fmt, sep in (("csv", ","), ("tsv", "\t")):
        rows = list(csv.reader(io.StringIO(text[fmt]), delimiter=sep))      # the default field limit
        lines = [r[0] for r in rows if r and r[0].startswith("# Fit record")]
        assert len(lines) > 1 and all(len(r) == 1 for r in rows if r and r[0].startswith("# "))
        assert _decoded(lines) == rec
        for engine in ("c", "python"):
            pd.read_csv(io.StringIO(text[fmt]), sep=sep, comment="#", engine=engine)
            width = max(len(r) for r in rows)
            pd.read_csv(io.StringIO(text[fmt]), sep=sep, header=None, names=range(width), dtype=str, engine=engine)
        assert all(len(l) <= 32767 for l in text[fmt].split("\n"))
    assert _xlsx_record([r for r in info if r]) == rec
