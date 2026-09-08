"""Legacy numerical-model archives survive real project/spectrum roundtrips."""
from test_browser_find_peaks_full_window import browser, server, _new_page  # noqa: F401


def _load_record(pg, current=False):
    return pg.evaluate("""current => {
        const be = Array.from({length: 101}, (_,i) => 290-i*0.1);
        const raw = be.map((b,i) => 100+i);
        const peak = defaultPeak({id: 1, name: 'Legacy DS+G', shape: 'DSG_LA',
            center: 284.5, amplitude: 100, fwhm: 1, laAlpha: 0.1, laBeta: 0.3, laM: 0.4});
        const fr = {be, bgIntensity: be.map(() => 10), bgSubtracted: raw.map(v => v-10),
            fittedY: raw.map(v => v-0.123456789), chi: 7, chiReduced: 0.25, rmse: 0.1,
            provenance: current ? {software: {numerical_version: XPS_SOFTWARE.numerical_version}} : null};
        _loadProjectJSON({version: 3, activeId: 'legacy', tabs: [{id: 'legacy', name: 'Legacy',
            rawBE: be, rawIntensity: raw, peaks: [peak], nextId: 2, ccShift: 0,
            ui: {bgType: 'none', roiMin: '280', roiMax: '290'}, fitResult: fr}]}, 'legacy.proj.json');
        return fr.fittedY;
    }""", current)


def test_legacy_arrays_survive_project_then_spectrum_roundtrip_without_active_diagnostics(browser, server):
    pg = _new_page(browser, server)
    try:
        original = _load_record(pg)
        assert pg.evaluate('() => state.fitResult === null')
        assert 'Run the fit' in pg.locator('#results-area').inner_text()
        assert 'Historical fits retained' in pg.locator('body').inner_text()
        first = pg.evaluate("""() => {
            const t = tabManager._getTab(tabManager.activeId);
            state.peaks[0].center += 0.2;
            return {n: t.historicalFits.length, curve: t.historicalFits[0].fitResult.fittedY,
                historicalCenter: t.historicalFits[0].peaks[0].center};
        }""")
        assert first == {'n': 1, 'curve': original, 'historicalCenter': 284.5}
        roundtrip = pg.evaluate("""async () => {
            const oldDownload = _downloadBlob;
            let blob;
            _downloadBlob = b => {blob = b;};
            try {
                await _doSaveProject();
                const project = JSON.parse(await blob.text());
                _loadProjectJSON(project, 'retained.proj.json');
                _doSaveSpectrum();
                const spectrum = JSON.parse(await blob.text());
                _loadSpectrumFile(spectrum, 'retained.spec.json');
                const t = tabManager._getTab(tabManager.activeId);
                return {projectN: project.tabs[0].historicalFits.length,
                    spectrumN: spectrum.historicalFits.length, active: state.fitResult,
                    loadedN: t.historicalFits.length, curve: t.historicalFits[0].fitResult.fittedY};
            } finally {_downloadBlob = oldDownload;}
        }""")
        assert roundtrip == {'projectN': 1, 'spectrumN': 1, 'active': None,
                             'loadedN': 1, 'curve': original}
    finally:
        pg.close()


def test_same_numerical_version_retains_active_fitted_result(browser, server):
    pg = _new_page(browser, server)
    try:
        curve = _load_record(pg, current=True)
        saved = pg.evaluate("""() => ({curve: state.fitResult.fittedY,
            history: tabManager._getTab(tabManager.activeId).historicalFits})""")
        assert saved == {'curve': curve, 'history': []}
    finally:
        pg.close()
