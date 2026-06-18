"""Real-browser tests for Phase A legacy-Auger source projection.

Legacy photoelectron markers are source-invariant apparent BEs (drawn as-is).
Legacy Auger markers are NOT: their kinetic energy is the source-invariant
quantity, so the displayed apparent BE must move with the photon energy exactly
like the curated Auger path. These tests drive the real frontend (templates/
index.html) in headless Chromium against a live gunicorn and assert marker
positions returned by the same data path that feeds the chart overlay
(`_refTransitionsFor`), toggling the Al Kα / Mg Kα source.

Skips cleanly when Playwright or a cached Chromium build is unavailable, so the
standard `pytest tests/` run is unaffected on machines without a browser.
"""
import glob
import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

playwright_api = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_chromium():
    """Locate a cached Chromium/Chrome-for-Testing/headless-shell binary."""
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
    """Start a gunicorn serving the worktree app on a free port."""
    gunicorn = os.path.join(os.path.dirname(sys.executable), "gunicorn")
    if not os.path.exists(gunicorn):
        pytest.skip("gunicorn not found next to the test interpreter")
    port = _free_port()
    proc = subprocess.Popen(
        [gunicorn, "app:app", "-w", "1", "-b", f"127.0.0.1:{port}", "--timeout", "60"],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        ok = False
        for _ in range(50):  # ~10s
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
def page(server):
    exe = _find_chromium()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception:
            if not exe:
                pytest.skip("no usable Chromium build found")
            browser = p.chromium.launch(headless=True, executable_path=exe)
        pg = browser.new_page()
        pg.goto(server + "/", wait_until="load")
        pg.click("#btn-ref-panel")
        pg.wait_for_function("window._refPayload && window._refPayload.legacy", timeout=10000)
        yield pg
        browser.close()


def _be_map(page, sym, source):
    """{orbital: {be, auger}} for an element under a given X-ray source."""
    return page.evaluate(
        """([sym, src]) => {
            const sel = _refGetSel(); sel.source = src;
            const out = {};
            for (const m of _refTransitionsFor(sym))
                out[m.t.orbital] = { be: m.be, auger: m.isAuger };
            sel.source = 'AlKa';
            return out;
        }""",
        [sym, source],
    )


def _photon_gap(page):
    return page.evaluate(
        "() => _refPayload.conventions.photon_energy_ev.AlKa - "
        "_refPayload.conventions.photon_energy_ev.MgKa"
    )


def test_photon_gap_is_233(page):
    # Al Kα (1486.6) − Mg Kα (1253.6) = 233.0; the Auger marker shift.
    assert abs(_photon_gap(page) - 233.0) < 1e-6


def test_legacy_photoelectron_fixed_across_sources(page):
    # V stays legacy (its 2p3/2 conflict was not promoted); Fe's bare 2p is now
    # superseded by a machine 2p3/2, so use V as the legacy-photoelectron example.
    al = _be_map(page, "V", "AlKa")
    mg = _be_map(page, "V", "MgKa")
    assert al["2p"]["auger"] is False
    assert abs(al["2p"]["be"] - 517.0) < 0.05
    assert abs(al["2p"]["be"] - mg["2p"]["be"]) < 1e-6  # photoelectron does NOT move


def test_legacy_na_kll_moves_497_to_264(page):
    al = _be_map(page, "Na", "AlKa")
    mg = _be_map(page, "Na", "MgKa")
    # photoelectron 1s stays put
    assert abs(al["1s"]["be"] - mg["1s"]["be"]) < 1e-6
    # KLL Auger is recognized and reprojected
    assert al["KLL"]["auger"] is True
    assert abs(al["KLL"]["be"] - 497.0) < 0.05
    assert abs(mg["KLL"]["be"] - 264.0) < 0.05
    assert abs((al["KLL"]["be"] - mg["KLL"]["be"]) - 233.0) < 0.05


def test_legacy_mg_kll_moves_306_to_73(page):
    al = _be_map(page, "Mg", "AlKa")
    mg = _be_map(page, "Mg", "MgKa")
    assert al["KLL"]["auger"] is True
    assert abs(al["KLL"]["be"] - 306.0) < 0.05
    assert abs(mg["KLL"]["be"] - 73.0) < 0.05
    assert abs((al["KLL"]["be"] - mg["KLL"]["be"]) - 233.0) < 0.05


def test_curated_cu_lmm_unchanged(page):
    al = _be_map(page, "Cu", "AlKa")
    mg = _be_map(page, "Cu", "MgKa")
    # 2p photoelectron doublet fixed
    assert abs(al["2p3/2"]["be"] - 932.67) < 0.05
    assert abs(al["2p3/2"]["be"] - mg["2p3/2"]["be"]) < 1e-6
    # LMM Auger moves by the same 233.0 (curated path, ke 918.62)
    assert al["L3M4,5M4,5"]["auger"] is True
    assert abs(al["L3M4,5M4,5"]["be"] - 563.48) < 0.05
    assert abs(mg["L3M4,5M4,5"]["be"] - 330.48) < 0.05
    assert abs((al["L3M4,5M4,5"]["be"] - mg["L3M4,5M4,5"]["be"]) - 233.0) < 0.05
