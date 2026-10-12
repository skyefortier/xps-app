"""Real browser, real server (sealed-fit v6 Q5, owner 2026-10-12): ONE area — the server's formula on
ONE grid — in every reader. After a Run Fit the server's own area, Results (and Quantify, which takes
Results' areas), the spectrum save, the CSV export and the sidebar's area % agree; after a charge
correction (the fit's grid is now in another frame) they still agree with one another, on the live
grid; and the note for a component centred outside the window follows the model as it is edited,
with or without a fit. Skips cleanly when Playwright / Chromium / gunicorn are absent."""
import csv
import io
import json

import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import _new_page, browser, server  # noqa: E402,F401
from test_browser_background_not_converged import CAPTURE, PEAK_TAB  # noqa: E402

# every reader's areas, as each one shows or writes them
READERS = """() => {
  const q = document.getElementById('quantify-area');
  const rows = [...document.querySelectorAll('#results-area .results-table tbody tr')].map(tr => [...tr.children].map(td => td.textContent.trim()));
  const sidebar = state.peaks.map(p => { const v = document.querySelectorAll('#peak-item-' + p.id + ' .peak-summary-val'); return v[2] ? v[2].textContent.trim() : null; });
  const ip = (state.fitResult && state.fitResult.backendResult && state.fitResult.backendResult.individual_peaks) || [];
  return { results: q && q._areas ? Array.from(q._areas) : null, resultsPct: rows.map(r => r[4]), sidebarPct: sidebar,
           server: state.peaks.map(p => { const x = ip.find(i => String(i.id) === String(p.id)); return x ? x.params.area.value : null; }),
           live: state.peaks.map(p => _peakArea(p, getROIData().be)), stats: _statsLiveState(),
           note: ((document.querySelector('#results-area .outside-window-note') || {}).textContent || '').replace(/\s+/g, ' ').trim() || null };
}"""


def _save_and_csv(pg):
    pg.evaluate(CAPTURE)
    pg.evaluate("() => _doSaveSpectrum()")
    pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
    spec = json.loads(pg.evaluate("() => window.__dl[0].text"))
    pg.evaluate(CAPTURE)
    pg.evaluate("() => exportFitTable('csv')")
    pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
    rows = list(csv.reader(io.StringIO(pg.evaluate("() => window.__dl[0].text"))))
    head = next(i for i, r in enumerate(rows) if r and r[0] == "Peak Name" or (r and "Area" in r))
    col = rows[head].index("Area")
    return [c["area"] for c in spec["peakCurves"]] if "peakCurves" in spec else [c["area"] for c in spec["peaks"]], \
        [float(r[col]) for r in rows[head + 1:head + 1 + 2]]


def _agree(got, save, csv_areas):
    assert save == got["results"], (save, got["results"])                                   # the save writes what Results shows
    assert csv_areas == [round(a, 2) for a in got["results"]], (csv_areas, got["results"])  # the export, as it formats it
    assert got["sidebarPct"] == got["resultsPct"], got                                       # the sidebar's area %


def test_every_reader_shows_the_servers_area_on_one_grid(browser, server):
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("() => { document.getElementById('fit-method').value = 'least_squares'; }")
        assert pg.evaluate("async () => { await runFit(); return !!state.fitResult; }")
        got = pg.evaluate(READERS)
        assert got["stats"] == "current"
        assert got["results"] == got["server"], got          # the page's area IS the server's, bit for bit
        assert got["results"] == got["live"]                 # a current fit's grid is the live one
        _agree(got, *_save_and_csv(pg))
        assert got["note"] is None
        # a charge correction moves the model 1 eV; the fit's grid stays in the old frame: every reader
        # now integrates the current model on the live grid, and they agree with one another
        pg.evaluate("""() => { const cm = document.getElementById('cc-method'); cm.value = 'c1s';
            document.getElementById('cc-obs').value = '285.5'; document.getElementById('cc-lit').value = '284.50';
            updateChargeCorrection(); updatePlot(); }""")
        got = pg.evaluate(READERS)
        assert got["stats"] == "stale" and got["results"] == got["live"], got
        _agree(got, *_save_and_csv(pg))
        assert got["note"] is None, "both centres moved with the frame: still inside"
        # the note follows an edit made while the result is stale — no forced re-render
        pid = pg.evaluate("() => state.peaks[1].id")
        pg.evaluate("(id) => { updatePeakParam(id, 'center', 299); updatePlot(); }", pid)
        note = pg.evaluate(READERS)["note"]
        assert note and "is centred outside the window — its area is poorly determined by the data." in note, note
        pg.evaluate("(id) => { updatePeakParam(id, 'center', 285.5); updatePlot(); }", pid)
        assert pg.evaluate(READERS)["note"] is None
    finally:
        pg.close()


def test_the_note_needs_no_fit(browser, server):
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("() => { state.peaks[1].center = 295; state.peaks[1].name = 'far'; renderPeakList(); updatePlot(); }")
        assert pg.evaluate("() => state.fitResult") is None
        note = pg.evaluate(READERS)["note"]
        assert note == "far is centred outside the window — its area is poorly determined by the data.", note
    finally:
        pg.close()
