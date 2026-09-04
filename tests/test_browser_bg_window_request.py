"""Real-browser guard for the background-window request contract (unit 1c).

The /api/fit request must carry the SAME set of grid points the on-screen
preview uses for the background: every point with lo <= BE <= hi, inclusive
at both ends, sent as start_idx = i0 and end_idx = i1 + 1 because the backend
slices Python-end-exclusive. Before 1c the builder sent the nearest index to
each bound and end_idx = i1, so the fit anchored one point inside the window
the user drew (docs/superpowers/plans/2026-09-02-background-architecture-
sealed-fit-record.md, round-5 amendment).

Captures the actual wire payload with Playwright request interception; the
node unit tests pin the helper itself and the structural shape of the
builders, this pins the end-to-end path DOM fields -> getROIData -> request.

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


def _setup(page, bg_start, bg_end):
    """C1s-like descending grid 298.16 … 279.16 (191 pts, 0.1 eV), ROI 279.0–298.5
    (all points), shirley background, one peak; bg bounds as given."""
    page.evaluate(
        """([bs, be_]) => {
            const raw = [], inten = [];
            const g = (be, c, a, w) => a * Math.exp(-Math.pow(be - c, 2) / (2 * w * w));
            for (let i = 0; i < 191; i++) {
                const be = Math.round((298.16 - i * 0.1) * 1000) / 1000;
                raw.push(be); inten.push(800 + g(be, 284.8, 6000, 0.7) + g(be, 286.4, 1500, 0.8));
            }
            tabManager.createTab('bg window test', raw, inten);
            const t = tabManager._getTab(tabManager.activeId);
            state.ccShift = 0; if (t) t.ccShift = 0;
            document.getElementById('roi-min').value = '279.0';
            document.getElementById('roi-max').value = '298.5';
            document.getElementById('bg-type').value = 'shirley';
            if (typeof _onBgTypeChange === 'function') _onBgTypeChange();
            document.getElementById('bg-start').value = bs;
            document.getElementById('bg-end').value = be_;
            addPeak();
            state.peaks[0].center = 284.8;
            state.peaks[0].fwhm = 1.2;
            state.peaks[0].amplitude = 6000;
            updatePlot();
        }""",
        [bg_start, bg_end],
    )
    page.wait_for_timeout(150)


def _captured_fit_request(page):
    with page.expect_request("**/api/fit", timeout=30000) as req_info:
        page.evaluate("() => { runFit(); }")
    body = req_info.value.post_data_json
    page.wait_for_timeout(300)
    return body


def test_window_at_roi_edges_sends_every_point_end_inclusive(browser, server):
    # bounds land exactly on the first/last grid points → all 191 points,
    # end_idx == len (the backend slices [0:191)).
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.goto(server + "/", wait_until="load")
    try:
        _setup(pg, "298.16", "279.16")
        body = _captured_fit_request(pg)
        assert body["background"]["method"] == "shirley"
        assert body["background"]["start_idx"] == 0
        assert body["background"]["end_idx"] == 191
    finally:
        pg.close()


def test_off_grid_bound_inside_roi_excludes_the_point_outside_it(browser, server):
    # typed 279.2 lies between 279.26 (index 189, inside) and 279.16 (index
    # 190, outside). The window must end at 279.26: end_idx == 190, i.e. the
    # slice [0:190) — the preview's point set, not the nearest grid point.
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.goto(server + "/", wait_until="load")
    try:
        _setup(pg, "298.2", "279.2")
        body = _captured_fit_request(pg)
        assert body["background"]["start_idx"] == 0
        assert body["background"]["end_idx"] == 190
    finally:
        pg.close()
