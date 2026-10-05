"""Real browser, real server (background math, 2026-10-01): a background that does
not satisfy its defining statement is said under the method menu, is not drawn,
and Run Fit refuses it before anything changes (no undo entry, no fit); an
explicit background on the same data draws and fits. Skips cleanly when
Playwright / Chromium / gunicorn are absent."""
import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import _new_page, browser, server  # noqa: E402,F401

U_TAB = """() => {
    // convex: every interior point below the line between the (unequal) edge levels
    const raw = [], inten = [];
    for (let i = 0; i <= 120; i++) { const be = 280 + i * 0.1; raw.push(be); inten.push(1000 + 40 * (be - 285) ** 2); }
    tabManager.createTab('U', raw, inten);
    document.getElementById('roi-min').value = 280; document.getElementById('roi-max').value = 292;
    document.getElementById('bg-start').value = 292; document.getElementById('bg-end').value = 280;
    document.getElementById('bg-endpoint-avg').value = 1;
    document.getElementById('bg-type').value = 'shirley'; _onBgTypeChange();
    addPeak({ center: 285, fwhm: 1.0, amplitude: 100, shape: 'GL', glMix: 30 });
    updatePlot();
}"""

SEEN = """() => ({
    note: getComputedStyle(document.getElementById('bg-not-converged')).display !== 'none',
    text: document.getElementById('bg-not-converged').textContent,
    drawn: state.chart.data.datasets.some(d => d.label === 'Background'),
    iterVisible: document.getElementById('shirley-iter').offsetParent !== null,
})"""


def test_a_non_converged_background_is_said_not_drawn_and_not_fitted(browser, server):
    pg = _new_page(browser, server)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    try:
        pg.evaluate(U_TAB)
        seen = pg.evaluate(SEEN)
        assert seen["note"] and "Shirley background not converged" in seen["text"] and "no net signal" in seen["text"], seen
        assert not seen["drawn"], "a non-converged background is not drawn"
        assert not seen["iterVisible"], "the retired iterations setting is hidden"
        undo0 = pg.evaluate("() => (tabManager._getTab(tabManager.activeId).undoStack || []).length")
        pg.evaluate("() => { window.__n = []; const o = notify; window.notify = (m, k) => { window.__n.push(m); return o(m, k); }; }")
        pg.evaluate("() => runFit()")
        pg.wait_for_timeout(300)
        after = pg.evaluate("() => ({ fit: state.fitResult, undo: (tabManager._getTab(tabManager.activeId).undoStack || []).length, n: window.__n })")
        assert after["fit"] is None and after["undo"] == undo0, after
        assert any(m.startswith("Fit not run: Shirley background not converged") for m in after["n"]), after["n"]
        # an explicit background on the same data draws and fits
        pg.evaluate("() => { document.getElementById('bg-type').value = 'linear'; _onBgTypeChange(); updatePlot(); }")
        seen = pg.evaluate(SEEN)
        assert not seen["note"] and seen["drawn"], seen
        pg.evaluate("() => { window.__n = []; window.__d = false; runFit().then(() => window.__d = true, () => window.__d = true); }")
        pg.wait_for_function("() => window.__d === true", timeout=120000)
        n = pg.evaluate("() => window.__n")
        # the fit is attempted (a linear background is explicit: nothing to converge); whether a
        # peak on U-shaped data converges is the fit's own outcome, not the background's
        assert n and not any(m.startswith("Fit not run") for m in n), n
    finally:
        pg.close()
    assert errors == [], errors


CAPTURE = """() => { window.__dl = []; window._downloadBlob = async (blob, name) => {
  window.__dl.push({ name, text: await blob.text() }); }; }"""


def test_a_saved_fit_whose_background_no_longer_converges_is_not_restored(browser, server):
    # Codex implementation round 1 (BLOCKER): a restored fit used to bypass the certificate —
    # its stored background drew, fed the stack and was saved again
    import json
    pg = _new_page(browser, server)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    try:
        pg.evaluate(U_TAB)
        # an older version's fit on this window: its stored background is the line (no solution now)
        pg.evaluate("""() => { const { be, inten } = getROIData();
            const line = be.map((b, i) => inten[0] + (inten[inten.length - 1] - inten[0]) * i / (be.length - 1));
            state.fitResult = { be, bgIntensity: line, bgSubtracted: inten.map((v, i) => v - line[i]), chiReduced: 1.0, chi: 100,
                                fittedY: inten.slice(),
                                startsModelKey: _startsLiveKey() };
            tabManager._syncActiveToRecord(); }""")
        pg.evaluate(CAPTURE)
        pg.evaluate("() => _doSaveProject()")
        pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
        saved = json.loads(pg.evaluate("() => window.__dl[0].text"))
    finally:
        pg.close()
    assert any(t.get("fitResult") for t in saved["tabs"] if not t.get("isStack")), "the fixture carries a saved fit"

    pg = _new_page(browser, server)
    errors2 = []
    pg.on("pageerror", lambda e: errors2.append(str(e)))
    try:
        pg.evaluate("() => { window.__n = []; const o = notify; window.notify = (m, k) => { window.__n.push(m); return o(m, k); }; }")
        pg.evaluate("data => _loadProjectJSON(data, 'old.proj.json')", saved)
        pg.wait_for_timeout(500)
        got = pg.evaluate("""() => ({ fit: tabManager.tabs.filter(t => !t.isStack).map(t => t.fitResult), live: state.fitResult,
                                     n: window.__n, peaks: state.peaks.length })""")
        assert all(f is None for f in got["fit"]) and got["live"] is None, got
        assert got["peaks"] == 1, "the model is kept"
        assert any(m.startswith("Saved fit not restored: U — its background settings give no converged background now: Shirley background not converged") for m in got["n"]), got["n"]
        # a stack built on it shows no fit
        rd = pg.evaluate("""() => { const id = tabManager.tabs.find(t => !t.isStack).id; tabManager.createStackTab();
            const st = tabManager._getTab(tabManager.activeId); _addSpectrumToStack(st, id);
            return st.entries.map(e => _buildEntryRenderData(e).be.length); }""")
        assert rd == [0], rd
    finally:
        pg.close()
    assert errors == [] and errors2 == [], (errors, errors2)


PEAK_TAB = """() => {
    const raw = [], inten = [];
    for (let i = 0; i <= 200; i++) { const be = 280 + i * 0.06; raw.push(be);
      const g = (c, a, w) => a * Math.exp(-4 * Math.log(2) * ((be - c) / w) ** 2);
      inten.push(Math.round((300 + g(284.5, 6000, 0.9) + g(286.4, 900, 1.2) + (be > 284.5 ? 400 : 0)) * 100) / 100); }
    tabManager.createTab('P', raw, inten);
    document.getElementById('roi-min').value = 280; document.getElementById('roi-max').value = 292;
    document.getElementById('bg-start').value = 292; document.getElementById('bg-end').value = 280;
    document.getElementById('bg-endpoint-avg').value = 3;
    document.getElementById('bg-type').value = 'shirley'; _onBgTypeChange();
    addPeak({ center: 284.4, fwhm: 1.0, amplitude: 5500, shape: 'GL', glMix: 30 });
    addPeak({ center: 286.5, fwhm: 1.2, amplitude: 800, shape: 'GL', glMix: 30 });
    updatePlot();
}"""


def test_restored_fits_keep_only_a_stored_curve_that_satisfies_its_statement(browser, server):
    # Codex implementation round 2: a fit whose settings converge NOW used to keep its OLD stored
    # curve uncertified. Owner 2026-10-03: the evidence is the background the fit USED (its
    # envelope less its peaks), not the stored preview curve: a fit saved by this version reloads
    # current, and so does one made against the old page's 5-iteration Shirley (1.7e-6 of its
    # scale here: within rounding); one made against a genuinely different background (a single
    # Shirley step, 4 %) reloads STALE, sized, with its own background — and a garbage stored
    # preview is no evidence.
    import json
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("() => { window.__d = false; runFit().then(() => window.__d = true, () => window.__d = true); }")
        pg.wait_for_function("() => window.__d === true", timeout=120000)
        assert pg.evaluate("() => !!state.fitResult && state.fitResult.bgIntensity.converged === true")
        pg.evaluate(CAPTURE)
        pg.evaluate("() => _doSaveProject()")
        pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
        fresh = json.loads(pg.evaluate("() => window.__dl[0].text"))
        # the same project as an older version saved it: its stored curve the old 5-iteration preview
        curve = lambda it: pg.evaluate("""it => { const { be, inten } = getROIData(); const w = _bgWindowIndices(be, '292', '280');
            const ys = inten.slice(w.i0, w.i1 + 1), xs = be.slice(w.i0, w.i1 + 1);
            const five = shirleyBackground(xs, ys, it, 3);   // `it` iterations: no solution yet
            const full = be.map((_, i) => i < w.i0 ? five[0] : i > w.i1 ? five[five.length - 1] : five[i - w.i0]);
            return full; }""", it)
        old_curve, one_step = curve(5), curve(1)
    finally:
        pg.close()
    def against(c):
        d = json.loads(json.dumps(fresh))
        for t in d["tabs"]:
            if t.get("fitResult"):
                fr = t["fitResult"]
                fr["fittedY"] = [y - b + o for y, b, o in zip(fr["fittedY"], fr["bgIntensity"], c)]
                # a fit made against that background has its own RMSE (the record is consistent)
                at = {round(e * 1e4) / 1e4: v for e, v in zip(t["rawBE"], t["rawIntensity"])}
                r = [at[e] - f for e, f in zip(fr["be"], fr["fittedY"])]
                fr["rmse"] = (sum(v * v for v in r) / len(r)) ** 0.5
        return d
    five, old, preview = against(old_curve), against(one_step), json.loads(json.dumps(fresh))
    for t in preview["tabs"]:
        if t.get("fitResult"):
            t["fitResult"]["bgIntensity"] = old_curve
    for data, stale in ((fresh, False), (preview, False), (five, False), (old, True)):
        pg = _new_page(browser, server)
        try:
            pg.evaluate("() => { window.__n = []; const o = notify; window.notify = (m, k) => { window.__n.push(m); return o(m, k); }; }")
            pg.evaluate("data => _loadProjectJSON(data, 'p.proj.json')", data)
            pg.wait_for_timeout(400)
            got = pg.evaluate("""() => ({ fit: !!state.fitResult, n: window.__n, stale: state.fitResult && state.fitResult.backgroundStale,
                st: _statsLiveState(), certified: !!(state.fitResult && state.fitResult.bgIntensity.converged === true) })""")
            assert got["fit"], got
            if stale:
                assert got["stale"] and got["stale"]["pct"] > 0.1 and got["st"] == "stale" and not got["certified"], got
                assert any(m.startswith("Saved fit restored as STALE: ") and "differs from the one its settings give now" in m for m in got["n"]), got["n"]
            else:
                assert not got["stale"] and got["certified"], got
        finally:
            pg.close()


def test_a_manual_background_fit_is_restored(browser, server):
    # Codex implementation round 2: the restore check used to compute a SHIRLEY background for a
    # manual fit (the stack helper's substitution) and drop a valid fit
    import json
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        pg.evaluate("""() => { _setManualAnchors([{ x: 280, y: 300 }, { x: 292, y: 700 }]);
            document.getElementById('bg-type').value = 'manual'; _onBgTypeChange(); updatePlot(); }""")
        pg.evaluate("() => { window.__d = false; runFit().then(() => window.__d = true, () => window.__d = true); }")
        pg.wait_for_function("() => window.__d === true", timeout=120000)
        assert pg.evaluate("() => !!state.fitResult")
        pg.evaluate(CAPTURE)
        pg.evaluate("() => _doSaveProject()")
        pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
        saved = json.loads(pg.evaluate("() => window.__dl[0].text"))
    finally:
        pg.close()
    pg = _new_page(browser, server)
    try:
        pg.evaluate("data => _loadProjectJSON(data, 'm.proj.json')", saved)
        pg.wait_for_timeout(400)
        assert pg.evaluate("() => !!state.fitResult")
    finally:
        pg.close()


def _fit_and_capture(pg, setup, save, after_fit="() => {}"):
    import json
    pg.evaluate(setup)
    pg.evaluate("() => { window.__d = false; runFit().then(() => window.__d = true, () => window.__d = true); }")
    pg.wait_for_function("() => window.__d === true", timeout=120000)
    assert pg.evaluate("() => !!state.fitResult")
    pg.evaluate(after_fit)
    pg.evaluate(CAPTURE)
    pg.evaluate(save)
    pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
    return json.loads(pg.evaluate("() => window.__dl[0].text"))


NOTIFY = "() => { window.__n = []; const o = notify; window.notify = (m, k) => { window.__n.push(m); return o(m, k); }; }"


def test_a_spectrum_file_fit_is_restored_and_a_stale_one_is_not(browser, server):
    # Codex implementation round 3: the spectrum loader built its fit without the stored grid and
    # curve, so EVERY fit saved to a .spec.json was dropped on load
    saves = {}
    for name, after in (("current", "() => {}"),
                        ("stale", "() => { state.peaks[0].fwhm = 1.4; updatePlot(); }")):
        pg = _new_page(browser, server)
        try:
            saves[name] = _fit_and_capture(pg, PEAK_TAB, "() => _doSaveSpectrum()", after)
        finally:
            pg.close()
    assert saves["current"]["background"] and saves["current"]["statistics"]
    # Codex impl round 4: the same file written in ascending BE order (as a spectrum saved from an
    # ascending record is) — createTab re-sorts the raw data, so the fit's arrays must follow
    import copy
    asc = copy.deepcopy(saves["current"])
    for k in ("rawBE", "rawIntensity", "roiBE", "background", "fittedY"):
        asc[k] = list(reversed(asc[k]))
    saves["ascending"] = asc
    for name, kept in (("current", True), ("ascending", True), ("stale", False)):
        pg = _new_page(browser, server)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        try:
            pg.evaluate(NOTIFY)
            pg.evaluate("data => _loadSpectrumFile(data, 'p.spec.json')", saves[name])
            pg.wait_for_timeout(400)
            got = pg.evaluate("""() => ({ fit: !!state.fitResult, n: window.__n,
                bgOk: !!(state.fitResult && state.fitResult.bgIntensity && state.fitResult.bgIntensity.converged === true),
                be: state.fitResult && state.fitResult.be, fittedY: state.fitResult && state.fitResult.fittedY })""")
            assert got["fit"] is kept, (name, got["n"])
            if kept:
                assert got["bgOk"], "the certified curve replaces the stored one"
                # the file's own order is kept (round 5): the grid and curve as saved, point for point
                assert got["be"] == saves[name]["roiBE"] and got["fittedY"] == saves[name]["fittedY"], name
            else:
                assert any("saved after its model or settings changed" in m for m in got["n"]), got["n"]
        finally:
            pg.close()
        assert errors == [], errors


def test_a_manual_fit_whose_anchors_moved_after_the_fit_is_not_restored(browser, server):
    # Codex implementation round 3 (BLOCKER): manual / none were exempt by the CURRENT method, so a
    # fit whose anchors (or method) changed after it was fitted drew its old stored curve as
    # current. Owner 2026-10-03: it reloads STALE — its own background and peaks, statistics not
    # reported, the size of the difference said
    setup_manual = PEAK_TAB[:-1] + """;
        _setManualAnchors([{ x: 280, y: 300 }, { x: 292, y: 700 }]);
        document.getElementById('bg-type').value = 'manual'; _onBgTypeChange(); updatePlot(); }"""
    for name, after in (("anchors moved", "() => { _setManualAnchors([{ x: 280, y: 300 }, { x: 292, y: 900 }]); updatePlot(); }"),
                        ("method changed to none", "() => { document.getElementById('bg-type').value = 'none'; _onBgTypeChange(); updatePlot(); tabManager._syncActiveToRecord(); }")):
        pg = _new_page(browser, server)
        try:
            saved = _fit_and_capture(pg, setup_manual, "() => _doSaveProject()", after)
        finally:
            pg.close()
        pg = _new_page(browser, server)
        try:
            pg.evaluate(NOTIFY)
            pg.evaluate("data => _loadProjectJSON(data, 'm.proj.json')", saved)
            pg.wait_for_timeout(400)
            got = pg.evaluate("""() => ({ fit: !!state.fitResult, n: window.__n, peaks: state.peaks.length,
                stale: state.fitResult && state.fitResult.backgroundStale, st: _statsLiveState() })""")
            assert got["peaks"] == 2, (name, got)
            if got["fit"]:
                assert got["stale"] and got["st"] == "stale", (name, got)
                assert any(m.startswith("Saved fit restored as STALE: ") for m in got["n"]), (name, got["n"])
            else:   # a save that carried no envelope: peaks only, said plainly
                assert any("saved without its fitted envelope" in m for m in got["n"]), (name, got["n"])
        finally:
            pg.close()


def test_an_ascending_spectrum_with_repeated_energies_restores_its_fit(browser, server):
    # Codex impl round 5: re-sorting is not neutral — repeated energies integrate in another
    # order (12 % of the span on this case) — so the loader keeps the file's order
    setup = """() => {
        const raw = [0, 1, 2, 2, 3, 4, 5].map(e => 280 + e), inten = [10, 12, 40, 15, 30, 22, 20];
        tabManager.createTab('Asc', raw, inten);
        const t = tabManager._getTab(tabManager.activeId);
        t.rawBE = raw.slice(); t.rawIntensity = inten.slice(); state.rawBE = t.rawBE; state.rawIntensity = t.rawIntensity;
        document.getElementById('roi-min').value = 280; document.getElementById('roi-max').value = 285;
        document.getElementById('bg-start').value = 285; document.getElementById('bg-end').value = 280;
        document.getElementById('bg-endpoint-avg').value = 1;
        document.getElementById('bg-type').value = 'shirley'; _onBgTypeChange();
        addPeak({ center: 282, fwhm: 1.0, amplitude: 20, shape: 'Gaussian' });
        updatePlot();
    }"""
    pg = _new_page(browser, server)
    try:
        saved = _fit_and_capture(pg, setup, "() => _doSaveSpectrum()")
    finally:
        pg.close()
    assert saved["rawBE"][0] < saved["rawBE"][-1] and saved["background"], "an ascending file with its background"
    pg = _new_page(browser, server)
    try:
        pg.evaluate(NOTIFY)
        pg.evaluate("data => _loadSpectrumFile(data, 'asc.spec.json')", saved)
        pg.wait_for_timeout(400)
        got = pg.evaluate("() => ({ fit: !!state.fitResult, n: window.__n, raw: state.rawBE })")
        assert got["fit"], got["n"]
        assert got["raw"] == saved["rawBE"], "the file's order is kept"
    finally:
        pg.close()


def test_a_stack_shows_the_fits_own_counts_after_the_charge_shift_changes(browser, server):
    # Codex impl round 8: the stack re-derived raw counts for the frozen fit grid from the
    # CURRENT charge shift, subtracting the background from other samples
    pg = _new_page(browser, server)
    try:
        pg.evaluate(PEAK_TAB)
        # an ROI INSIDE the data (at the data's edge the old nearest-start slice happens to land right)
        pg.evaluate("""() => { document.getElementById('roi-min').value = 281; document.getElementById('roi-max').value = 291;
            document.getElementById('bg-start').value = 291; document.getElementById('bg-end').value = 281; updatePlot(); }""")
        pg.evaluate("() => { window.__d = false; runFit().then(() => window.__d = true, () => window.__d = true); }")
        pg.wait_for_function("() => window.__d === true", timeout=120000)
        got = pg.evaluate("""() => {
            const src = tabManager._getTab(tabManager.activeId);
            const net = state.fitResult.bgSubtracted.slice();
            src.ccShift = 1.0; state.ccShift = 1.0; tabManager._syncActiveToRecord();
            const id = src.id; tabManager.createStackTab();
            const st = tabManager._getTab(tabManager.activeId); _addSpectrumToStack(st, id);
            const rd = _buildEntryRenderData(st.entries[0]);
            const shown = rd.rawY.map((v, i) => v - rd.bg[i]);
            return { n: net.length, m: shown.length, worst: Math.max(...shown.map((v, i) => Math.abs(v - net[i]))),
                     scale: Math.max(...net.map(Math.abs)) };
        }""")
        assert got["n"] == got["m"] > 0 and got["worst"] <= 1e-12 * got["scale"], got
    finally:
        pg.close()


def test_a_background_stale_fit_shows_no_evidence_and_survives_a_spectrum_save(browser, server):
    # Codex impl round 18: a background-stale reload kept its scattered-starts comparison and
    # recorded choice (_startsIfCurrent read only the model key), and Save Spectrum wrote
    # today's background and a recomposed envelope, so the reload then dropped the fit
    import json
    setup = PEAK_TAB[:-1] + """;
        _setManualAnchors([{ x: 280, y: 300 }, { x: 292, y: 700 }]);
        document.getElementById('bg-type').value = 'manual'; _onBgTypeChange(); updatePlot(); }"""
    pg = _new_page(browser, server)
    try:
        saved = _fit_and_capture(pg, setup, "() => _doSaveProject()",
                                 "() => { if (state.fitResult) state.fitResult.chosenAlternative = { fromChi: 9, toChi: 3, shiftName: 'x', shiftEv: 0.1 }; tabManager._syncActiveToRecord(); }")
    finally:
        pg.close()
    t = next(t for t in saved["tabs"] if t.get("fitResult"))
    assert t["fitResult"].get("starts"), "the fixture fit carries scattered-starts evidence"
    t["manualAnchors"] = [{"x": 280, "y": 300}, {"x": 292, "y": 900}]      # today's anchors give another background
    pg = _new_page(browser, server)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    try:
        pg.evaluate(NOTIFY)
        pg.evaluate("data => _loadProjectJSON(data, 'm.proj.json')", saved)
        pg.wait_for_timeout(400)
        got = pg.evaluate("""() => ({ stale: state.fitResult && state.fitResult.backgroundStale, st: _statsLiveState(),
            starts: _startsIfCurrent(state.fitResult, _startsLiveKey()), chosen: _startsChosenText(state.fitResult),
            raw: state.fitResult && state.fitResult.starts, panel: document.getElementById('results-area').innerText })""")
        assert got["stale"] and got["st"] == "stale", got
        assert got["starts"] is None and got["chosen"] == "" and got["raw"] is None, got
        assert "scattered start" not in got["panel"], got["panel"][:400]
        pct = got["stale"]["pct"]
        pg.evaluate(CAPTURE)
        pg.evaluate("() => _doSaveSpectrum()")
        pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
        spec = json.loads(pg.evaluate("() => window.__dl[0].text"))
    finally:
        pg.close()
    assert spec["statistics"]["restoredStale"] is True
    # Codex impl round 19: the file's residuals belong to ITS envelope, on its own samples
    at = dict(zip(spec["rawBE"], spec["rawIntensity"]))
    assert all(abs(r + f - at[e]) <= 1e-9 * max(1.0, abs(at[e]))
               for e, r, f in zip(spec["roiBE"], spec["residuals"], spec["fittedY"])), "residual = counts − the saved envelope"
    pg = _new_page(browser, server)
    try:
        pg.evaluate(NOTIFY)
        pg.evaluate("data => _loadSpectrumFile(data, 'm.spec.json')", spec)
        pg.wait_for_timeout(400)
        got = pg.evaluate("() => ({ fit: !!state.fitResult, stale: state.fitResult && state.fitResult.backgroundStale, n: window.__n })")
        assert got["fit"] and got["stale"], got
        assert abs(got["stale"]["pct"] - pct) <= 1e-9 * pct, (got["stale"], pct)
        assert any(m.startswith("Saved fit restored as STALE: ") for m in got["n"]), got["n"]
    finally:
        pg.close()
    assert errors == [], errors


def test_a_stale_spectrum_save_keeps_the_fits_curves_only_when_its_peaks_are_the_fits(browser, server):
    # Codex impl round 20: a model edited (and the anchors moved) before the project save
    # reloads stale with the fit's own background (from its key) beside the EDITED peaks;
    # Save Spectrum then wrote the fit's envelope beside component curves of the edited
    # model. Such a file is an ordinary stale save (the edited state's curves), not the fit's.
    import json
    setup = PEAK_TAB[:-1] + """;
        _setManualAnchors([{ x: 280, y: 300 }, { x: 292, y: 700 }]);
        document.getElementById('bg-type').value = 'manual'; _onBgTypeChange(); updatePlot(); }"""
    pg = _new_page(browser, server)
    try:
        saved = _fit_and_capture(pg, setup, "() => _doSaveProject()",
                                 "() => { state.peaks[0].amplitude *= 2; tabManager._syncActiveToRecord(); }")
    finally:
        pg.close()
    t = next(t for t in saved["tabs"] if t.get("fitResult"))
    t["manualAnchors"] = [{"x": 280, "y": 300}, {"x": 292, "y": 900}]
    pg = _new_page(browser, server)
    try:
        pg.evaluate("data => _loadProjectJSON(data, 'm.proj.json')", saved)
        pg.wait_for_timeout(400)
        assert pg.evaluate("() => !!(state.fitResult && state.fitResult.backgroundStale)")
        assert pg.evaluate("() => !_restoredModelIsFit(tabManager._getTab(tabManager.activeId))")
        pg.evaluate(CAPTURE)
        pg.evaluate("() => _doSaveSpectrum()")
        pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
        spec = json.loads(pg.evaluate("() => window.__dl[0].text"))
    finally:
        pg.close()
    assert spec["statistics"]["statisticsState"] == "stale" and not spec["statistics"].get("restoredStale"), spec["statistics"]
    # the file's curves are one model's: envelope = background + the components written beside it
    comp = [sum(c["y"][i] for c in spec["peakCurves"]) for i in range(len(spec["roiBE"]))]
    assert all(abs(f - b - m) <= 1e-9 * max(1.0, abs(f)) for f, b, m in zip(spec["fittedY"], spec["background"], comp))


def test_a_restored_stale_spectrum_save_writes_one_fits_curves_on_one_grid(browser, server):
    # Codex impl round 22: (a) after a charge shift the "its peaks are the fit's" check compared
    # centres in two frames, so the save fell back to today's curves and the reload dropped the
    # fit; (b) an older fit's components were written on full-precision energies beside an
    # envelope the server had computed on 4-dp ones
    import json
    SHARP = """() => {
        const raw = [], inten = [];
        for (let i = 0; i <= 40; i++) { const be = 280.00004 + 0.1 * i; raw.push(be);
          inten.push(Math.round((10 + 1000 * Math.exp(-4 * Math.log(2) * ((be - 282) / 0.4) ** 2) + (i % 3 - 1) * 0.5) * 100) / 100); }
        tabManager.createTab('S', raw, inten);
        document.getElementById('roi-min').value = 280; document.getElementById('roi-max').value = 284.1;
        _setManualAnchors([{ x: 280, y: 10 }, { x: 284.1, y: 10 }]);
        document.getElementById('bg-type').value = 'manual'; _onBgTypeChange();
        addPeak({ center: 282, fwhm: 0.4, amplitude: 1000, shape: 'Gaussian' });
        updatePlot();
    }"""
    LEGACY = """() => { const fr = state.fitResult, t = tabManager._getTab(tabManager.activeId);   // as an older version fitted it
        delete fr.uploadFull; delete fr.startsModelKey;
        const m = evalAllPeaks(fr.be.map(v => Number(v.toFixed(4))), state.peaks);
        fr.fittedY = fr.be.map((_, i) => 10 + m[i]);
        const { inten } = getROIData();
        fr.rmse = Math.sqrt(inten.reduce((a, v, i) => a + (v - fr.fittedY[i]) ** 2, 0) / inten.length);
        tabManager._syncActiveToRecord(); }"""
    for name, after, shift in (("shifted", "() => {}", True), ("legacy", LEGACY, False), ("legacy current", LEGACY, None)):
        pg = _new_page(browser, server)
        try:
            saved = _fit_and_capture(pg, SHARP, "() => _doSaveProject()", after)
        finally:
            pg.close()
        t = next(t for t in saved["tabs"] if t.get("fitResult"))
        if shift is None:                                    # unchanged: it restores CURRENT (Codex impl round 23)
            t["fitResult"]["startsModelKey"] = None
        else:
            t["manualAnchors"] = [{"x": 280, "y": 20}, {"x": 284.1, "y": 20}]      # today's background differs
        if shift:                                                                   # the charge correction moved after the fit
            t["ccShift"] = 0.5
            for p in t["peaks"]:
                p["center"] -= 0.5
            t["ui"]["roiMin"], t["ui"]["roiMax"] = "279.5", "283.6"
            t["manualAnchors"] = [{"x": 279.5, "y": 20}, {"x": 283.6, "y": 20}]
        pg = _new_page(browser, server)
        try:
            pg.evaluate(NOTIFY)
            pg.evaluate("data => _loadProjectJSON(data, 'p.proj.json')", saved)
            pg.wait_for_timeout(400)
            want_stale = shift is not None
            assert pg.evaluate("() => !!(state.fitResult && state.fitResult.backgroundStale)") is want_stale, (name, pg.evaluate("() => window.__n"))
            pg.evaluate(CAPTURE)
            pg.evaluate("() => _doSaveSpectrum()")
            pg.wait_for_function("() => window.__dl && window.__dl.length > 0", timeout=20000)
            spec = json.loads(pg.evaluate("() => window.__dl[0].text"))
        finally:
            pg.close()
        assert spec["statistics"].get("restoredStale") is (True if want_stale else None), (name, spec["statistics"])
        comp = [sum(c["y"][i] for c in spec["peakCurves"]) for i in range(len(spec["roiBE"]))]
        # stale: the fit's own background, so envelope = background + components exactly; current:
        # today's certified background, equal to the fit's within the restore's tolerance
        tol = 1e-9 if want_stale else 1e-3
        scale = max(abs(b) for b in spec["background"])
        assert all(abs(f - b - m) <= tol * max(1.0, scale) for f, b, m in zip(spec["fittedY"], spec["background"], comp)), name
        at = {b - (spec.get("ccShift") or 0): v for b, v in zip(spec["rawBE"], spec["rawIntensity"])}   # today's corrected energies
        assert all(abs(r + f - at[e]) <= 1e-9 * max(1.0, abs(at[e])) for e, r, f in zip(spec["roiBE"], spec["residuals"], spec["fittedY"])), \
            name + ": residual = counts − the saved envelope"
        pg = _new_page(browser, server)
        try:
            pg.evaluate(NOTIFY)
            pg.evaluate("data => _loadSpectrumFile(data, 's.spec.json')", spec)
            pg.wait_for_timeout(400)
            assert pg.evaluate("() => !!state.fitResult"), (name, pg.evaluate("() => window.__n"))
            assert pg.evaluate("() => !!state.fitResult.backgroundStale") is want_stale, (name, pg.evaluate("() => window.__n"))
        finally:
            pg.close()
