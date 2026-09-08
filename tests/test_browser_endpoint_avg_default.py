"""Real-browser guard for the endpoint-averaging default (3 for NEW tabs, 1 for
legacy saved files). Decision and measurements:
docs/superpowers/plans/2026-09-03-endpoint-averaging-default.md.

"New fits only" is the contract: a fresh tab (and the /api/fit request built
from it) uses 3; a saved spectrum/v1 fit file whose ui does not carry
endpointAvg was fitted at 1 and must restore as 1, so its stored fit still
reconstructs against the background it was made with. Saved values are
honoured verbatim. The v1 fit-file writer never recorded the field at all;
it now does (in _doSaveFit, the production writer), so new saves round-trip.
Skips cleanly when Playwright/Chromium are absent.
"""
import glob
import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_chromium():
    base = os.path.expanduser("~/Library/Caches/ms-playwright")
    patterns = [
        base + "/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        base + "/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
        base + "/chromium-*/chrome-linux/chrome",
        base + "/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
    ]
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def server():
    gunicorn = os.path.join(os.path.dirname(sys.executable), "gunicorn")
    if not os.path.exists(gunicorn):
        pytest.skip("gunicorn not found next to the test interpreter")
    port = _free_port()
    proc = subprocess.Popen(
        [gunicorn, "app:app", "-w", "1", "-b", f"127.0.0.1:{port}", "--timeout", "60"],
        cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        ok = False
        for _ in range(50):
            if proc.poll() is not None:
                pytest.skip("gunicorn exited during startup")
            try:
                with urllib.request.urlopen(base + "/api/health", timeout=1) as r:
                    if r.status == 200:
                        ok = True
                        break
            except Exception:
                time.sleep(0.2)
        if not ok:
            pytest.skip("gunicorn did not become healthy")
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


@pytest.fixture(scope="module")
def browser():
    exe = _find_chromium()
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception:
            if not exe:
                pytest.skip("no usable Chromium build found")
            b = p.chromium.launch(headless=True, executable_path=exe)
        yield b
        b.close()




def _page(browser, server):
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.goto(server + "/", wait_until="load")
    return pg


GRID = """const be=[], inten=[];
    for (let i=0;i<120;i++){ const x=295-i*0.1; be.push(+x.toFixed(2)); inten.push(800+3000*Math.exp(-Math.pow(x-286.5,2)/0.5)); }"""


def test_fresh_tab_defaults_to_3_and_the_fit_request_carries_it(browser, server):
    pg = _page(browser, server)
    try:
        assert pg.evaluate("() => document.getElementById('bg-endpoint-avg').value") == "3"
        ui = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('fresh', be, inten);
            addPeak(); state.peaks[0].center = 286.5; updatePlot();
            return { tabUi: tabManager._getTab(tabManager.activeId).ui.endpointAvg,
                     dom: document.getElementById('bg-endpoint-avg').value }; }""")
        assert ui == {"tabUi": "3", "dom": "3"}, ui
        with pg.expect_request("**/api/fit", timeout=30000) as req:
            pg.evaluate("() => { runFit(); }")
        assert req.value.post_data_json["background"]["endpoint_avg"] == 3
        pg.wait_for_timeout(300)
    finally:
        pg.close()


def test_spectrum_file_without_endpoint_avg_restores_as_1_and_saved_values_win(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            const base = { spectrumName: 'legacy', rawBE: be, rawIntensity: inten, peaks: [], nextId: 1 };
            _loadSpectrumFile({ ...base, ui: { bgType: 'shirley', bgStart: '295', bgEnd: '283.1' } });
            const legacyUi = tabManager._getTab(tabManager.activeId).ui.endpointAvg;
            const legacyDom = document.getElementById('bg-endpoint-avg').value;
            _loadSpectrumFile({ ...base });                                  // no ui block at all
            const noUi = tabManager._getTab(tabManager.activeId).ui.endpointAvg;
            _loadSpectrumFile({ ...base, ui: { bgType: 'shirley', endpointAvg: '7' } });
            const saved = tabManager._getTab(tabManager.activeId).ui.endpointAvg;
            return { legacyUi, legacyDom, noUi, saved, savedDom: document.getElementById('bg-endpoint-avg').value }; }""")
        assert out == {"legacyUi": "1", "legacyDom": "1", "noUi": "1", "saved": "7", "savedDom": "7"}, out
    finally:
        pg.close()


def test_save_fit_records_endpoint_avg_and_round_trips(browser, server):
    # The PRODUCTION writer is _doSaveFit (Save Fit button), not TabManager.toJSON
    # (Codex round 1, both runs). Capture the actual downloaded blob.
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('target', be, inten);
            addPeak(); state.peaks[0].center = 286.5;
            const saved = [];
            window._downloadBlob = (blob, name) => { saved.push(blob.text()); };
            _doSaveFit();
            return Promise.all(saved).then(texts => {
                const data = JSON.parse(texts[0]);
                const writtenEp = data.background && data.background.endpointAvg;
                tabManager.fromJSON(data);                                  // reload the real artifact
                return { writtenEp, reloaded: tabManager._getTab(tabManager.activeId).ui.endpointAvg,
                         dom: document.getElementById('bg-endpoint-avg').value };
            }); }""")
        assert out == {"writtenEp": "3", "reloaded": "3", "dom": "3"}, out
    finally:
        pg.close()


def test_v1_fit_file_without_endpoint_avg_loads_as_1_even_without_a_background_block(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('target', be, inten);
            tabManager.fromJSON({ peaks: [], background: { type: 'shirley', start: '295', end: '283.1', shirleyIter: '5' } });
            const legacy = tabManager._getTab(tabManager.activeId).ui.endpointAvg;
            const legacyDom = document.getElementById('bg-endpoint-avg').value;
            tabManager.createTab('target2', be, inten);
            tabManager.fromJSON({ version: 1, peaks: [] });                // accepted peaks-only legacy file
            const noBg = tabManager._getTab(tabManager.activeId).ui.endpointAvg;
            const noBgDom = document.getElementById('bg-endpoint-avg').value;
            tabManager.fromJSON({ peaks: [], background: { type: 'shirley', start: '295', end: '283.1', shirleyIter: '5', endpointAvg: '9' } });
            const saved = tabManager._getTab(tabManager.activeId).ui.endpointAvg;
            return { legacy, legacyDom, noBg, noBgDom, saved }; }""")
        assert out == {"legacy": "1", "legacyDom": "1", "noBg": "1", "noBgDom": "1", "saved": "9"}, out
    finally:
        pg.close()


def test_applying_find_peaks_sets_the_panel_to_the_averaging_the_engine_used(browser, server):
    # Find Peaks' engine does not read the Background panel: it fits at 1 unless
    # the advanced options carry endpoint_avg. With new tabs at 3 the preview
    # background would be drawn at 3 under peaks fitted at 1 (Codex round 1,
    # both runs). Applying suggestions must set the panel (and the tab record)
    # to what the engine used, so preview == fit.
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('fresh', be, inten);
            window.confirm = () => true;
            window._showFindPeaksApplyConfirmModal = async () => true;
            _fpLast = { body: { peaks: [ { role: 'C-C', center: 284.8, fwhm: 1.2, amplitude: 3000, shape: 'pseudo_voigt_gl', gl_ratio: 0.3 } ],
                                diagnostics: {} },
                        method: 'ic_model_comparison', regions: ['C1s'], fitFullWindow: true, endpointAvg: '1' };
            return applyFindPeaks().then(() => ({
                dom: document.getElementById('bg-endpoint-avg').value,
                tabUi: tabManager._getTab(tabManager.activeId).ui.endpointAvg,
                nPeaks: state.peaks.length })); }""")
        assert out == {"dom": "1", "tabUi": "1", "nPeaks": 1}, out
    finally:
        pg.close()
