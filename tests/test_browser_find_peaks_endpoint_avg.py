"""Real-browser guard: Find Peaks sends the Background panel's endpoint
averaging to the engine (F3 round two). The request's options.endpoint_avg
must equal the panel value for methods that fit a background; an explicit
value typed into the Advanced JSON wins. (Every method in the menu fits a
background and accepts the key; the frontend still only sends it when the
method's advertised default_options include it, pinned structurally in
tests/js/find_peaks_endpoint_avg.test.js.)
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
    for (let i=0;i<140;i++){ const x=294-i*0.1; be.push(+x.toFixed(2)); inten.push(400+12000*Math.exp(-Math.pow(x-284.4,2)/1.28)+1500*Math.exp(-Math.pow(x-286.2,2)/2.88)); }"""


def _open_modal_with_region(pg, method):
    pg.evaluate("() => { " + GRID + """
        tabManager.createTab('C1s fresh', be, inten);
        addPeak(); state.peaks[0].center = 284.4; state.peaks[0].amplitude = 12000; state.peaks[0].fwhm = 1.2;
        return openFindPeaksModal(); }""")
    pg.wait_for_timeout(300)
    pg.select_option("#fp-method", method)
    pg.evaluate("() => { _fpRegionsSelected.clear(); _fpRegionsSelected.add('C 1s'); if (typeof _fpSyncSelectionUI === 'function') _fpSyncSelectionUI(); }")


def _captured_analyze_request(pg):
    with pg.expect_request("**/api/analyze/start", timeout=30000) as req:
        pg.evaluate("() => { runFindPeaks(); }")
    return req.value.post_data_json


def test_find_peaks_sends_the_panels_endpoint_avg(browser, server):
    pg = _page(browser, server)
    try:
        _open_modal_with_region(pg, "least_squares")
        assert pg.evaluate("() => document.getElementById('bg-endpoint-avg').value") == "3"
        body = _captured_analyze_request(pg)
        assert body["options"].get("endpoint_avg") == 3, body["options"]
        assert pg.evaluate("() => _fpLast === null || _fpLast.endpointAvg === '3'")
    finally:
        pg.close()


def test_advanced_json_endpoint_avg_wins_over_the_panel(browser, server):
    pg = _page(browser, server)
    try:
        _open_modal_with_region(pg, "least_squares")
        pg.evaluate("""() => { const o = JSON.parse(document.getElementById('fp-options').value || '{}');
                              o.endpoint_avg = 7; document.getElementById('fp-options').value = JSON.stringify(o); }""")
        body = _captured_analyze_request(pg)
        assert body["options"].get("endpoint_avg") == 7, body["options"]
    finally:
        pg.close()
