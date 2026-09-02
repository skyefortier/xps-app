"""Manual background anchors must migrate when the charge correction changes.

Student-reported bug (2026-09-01): anchors are stored per-tab as
{x: corrected BE at placement time, y: rawIntensity[i]} — DATA-ATTACHED, x
snapped to a data point (index.html `_handleManualAnchorClick`). On a charge-
correction change, `updateChargeCorrection()` migrates every other
data-attached energy value by -delta (ROI min/max, bg-start/bg-end, EVERY
peak center) but never touched `manualAnchors`, so the anchors visibly
detached from the spectrum.

The convention pinned here is the peak-center one (anchors follow their data
points), NOT the reference-marker one (literature markers stay at nominal
corrected BE) — anchors are measured-data positions, like peak centers.
Saved files need no migration: anchors persist alongside the tab's ccShift,
so every save is a self-consistent snapshot; only a LATER cc change moves
them, which is exactly when they were previously left behind.

Harness pattern mirrors test_browser_cc_overlay_repaint.py. Skips cleanly
when Playwright/Chromium/gunicorn are absent.
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


def _setup(page):
    """C1s-like spectrum (descending raw grid, peak at raw 286.5), manual bg,
    two anchors snapped to data points, one peak — ccShift starts at 0."""
    page.evaluate(
        """() => {
            const raw = [], inten = [];
            const g = (be, c, a, w) => a * Math.exp(-Math.pow(be - c, 2) / (2 * w * w));
            for (let i = 0; i <= 150; i++) {           // 295.0 -> 280.0 step 0.1
                const be = +(295.0 - i * 0.1).toFixed(2);
                raw.push(be); inten.push(500 + g(be, 286.5, 8000, 0.6));
            }
            tabManager.createTab('anchor cc test', raw, inten);
            const t = tabManager._getTab(tabManager.activeId);
            state.ccShift = 0; if (t) t.ccShift = 0;
            document.getElementById('bg-type').value = 'manual';
            if (typeof _onBgTypeChange === 'function') _onBgTypeChange();
            // Anchors exactly as _handleManualAnchorClick stores them:
            // x = corrected BE of a data point (== raw here), y = its intensity.
            const iA = 30, iB = 120;                   // 292.0 and 283.0
            _setManualAnchors([
                { x: raw[iA], y: inten[iA] },
                { x: raw[iB], y: inten[iB] },
            ]);
            addPeak();
            state.peaks[0].center = 286.5;
            updatePlot();
            window.__t6 = { rawA: raw[iA], rawB: raw[iB], yA: inten[iA], yB: inten[iB] };
        }"""
    )
    page.wait_for_timeout(150)


def _apply_cc(page, observed):
    page.evaluate(
        """(obs) => {
            document.getElementById('cc-method').value = 'c1s';
            document.getElementById('cc-obs').value = String(obs);
            updateChargeCorrection();
        }""",
        observed,
    )
    page.wait_for_timeout(100)


def _snapshot(page):
    return page.evaluate(
        """() => ({
            ccShift: state.ccShift,
            anchors: _getManualAnchors().map(a => ({ x: a.x, y: a.y })),
            peakCenter: state.peaks[0].center,
            t6: window.__t6,
        })"""
    )


def test_anchors_follow_peak_centers_through_cc_change(browser, server):
    pg = browser.new_page(viewport={"width": 1400, "height": 900})
    pg.goto(server + "/", wait_until="load")
    pg.wait_for_function("typeof tabManager !== 'undefined'", timeout=10000)
    _setup(pg)

    # cc change #1: observed graphite at raw 286.5 -> ccShift = +2.0, delta = +2.0.
    _apply_cc(pg, 286.5)
    s = _snapshot(pg)
    assert abs(s["ccShift"] - 2.0) < 1e-9
    # Control: the peak center migrated by -delta (existing, correct behavior).
    assert abs(s["peakCenter"] - 284.5) < 1e-9
    # Anchors must migrate identically: x_new = x_old - delta, i.e. each anchor
    # stays at its data point's CORRECTED position (raw - ccShift).
    assert abs(s["anchors"][0]["x"] - (s["t6"]["rawA"] - 2.0)) < 1e-9, (
        f"anchor A x={s['anchors'][0]['x']} did not migrate with the cc change "
        f"(expected {s['t6']['rawA'] - 2.0})"
    )
    assert abs(s["anchors"][1]["x"] - (s["t6"]["rawB"] - 2.0)) < 1e-9
    # y is intensity at the SAME data point — must be untouched.
    assert s["anchors"][0]["y"] == s["t6"]["yA"]
    assert s["anchors"][1]["y"] == s["t6"]["yB"]


def test_autofit_rollback_restores_anchors(browser, server):
    """Codex round-1 MAJOR (both runs): Auto-Fit applies a provisional cc
    shift through updateChargeCorrection() — which now migrates anchors —
    and on failure _autoFitRestore() rolled back ccShift/ROI/bg/peaks but
    left anchors in the provisional frame. The snapshot/restore pair must
    round-trip anchors exactly like the rest of the mutated state."""
    pg = browser.new_page(viewport={"width": 1400, "height": 900})
    pg.goto(server + "/", wait_until="load")
    pg.wait_for_function("typeof tabManager !== 'undefined'", timeout=10000)
    _setup(pg)

    s = pg.evaluate(
        """() => {
            const snap = _autoFitSnapshot();
            document.getElementById('cc-method').value = 'c1s';
            document.getElementById('cc-obs').value = '286.5';
            updateChargeCorrection();                      // provisional shift
            const shifted = _getManualAnchors().map(a => a.x);
            _autoFitRestore(snap);                         // simulated failure
            return {
                shifted,
                restored: _getManualAnchors().map(a => ({ x: a.x, y: a.y })),
                ccShift: state.ccShift,
                t6: window.__t6,
            };
        }"""
    )
    # sanity: the provisional shift really moved them first
    assert abs(s["shifted"][0] - (s["t6"]["rawA"] - 2.0)) < 1e-9
    # rollback must return them to the placement frame, like ccShift itself
    assert abs(s["ccShift"]) < 1e-9
    assert abs(s["restored"][0]["x"] - s["t6"]["rawA"]) < 1e-9, (
        f"anchor A left at {s['restored'][0]['x']} after auto-fit rollback "
        f"(expected placement x {s['t6']['rawA']})"
    )
    assert abs(s["restored"][1]["x"] - s["t6"]["rawB"]) < 1e-9
    assert s["restored"][0]["y"] == s["t6"]["yA"]


def test_spec_json_load_restores_anchors(browser, server):
    """Codex round-1 MAJOR (run A): _doSaveSpectrum writes manualAnchors but
    _loadSpectrumFile never read them back — the one anchor-persisting load
    path that dropped them (v1 fit files and project tabs both restore)."""
    pg = browser.new_page(viewport={"width": 1400, "height": 900})
    pg.goto(server + "/", wait_until="load")
    pg.wait_for_function("typeof tabManager !== 'undefined'", timeout=10000)
    s = pg.evaluate(
        """() => {
            const raw = [], inten = [];
            for (let i = 0; i <= 50; i++) { raw.push(295.0 - 0.1 * i); inten.push(500 + i); }
            _loadSpectrumFile({
                spectrumName: 'roundtrip', rawBE: raw, rawIntensity: inten,
                ccShift: 1.25, peaks: [], nextId: 1,
                manualAnchors: [ { x: 293.0, y: 520 }, { x: 291.0, y: 540 } ],
            });
            return _getManualAnchors().map(a => ({ x: a.x, y: a.y }));
        }"""
    )
    assert s == [{"x": 293.0, "y": 520}, {"x": 291.0, "y": 540}], (
        f".spec.json manualAnchors dropped on load: got {s}"
    )


def test_anchor_migration_composes_across_two_cc_changes(browser, server):
    pg = browser.new_page(viewport={"width": 1400, "height": 900})
    pg.goto(server + "/", wait_until="load")
    pg.wait_for_function("typeof tabManager !== 'undefined'", timeout=10000)
    _setup(pg)

    _apply_cc(pg, 286.5)   # ccShift 0 -> +2.0
    _apply_cc(pg, 285.0)   # ccShift +2.0 -> +0.5, delta = -1.5
    s = _snapshot(pg)
    assert abs(s["ccShift"] - 0.5) < 1e-9
    # Net migration is -0.5 from placement frame; composition must not drift.
    assert abs(s["anchors"][0]["x"] - (s["t6"]["rawA"] - 0.5)) < 1e-9, (
        f"anchor A x={s['anchors'][0]['x']} after two cc changes "
        f"(expected {s['t6']['rawA'] - 0.5})"
    )
    assert abs(s["anchors"][1]["x"] - (s["t6"]["rawB"] - 0.5)) < 1e-9
    assert s["anchors"][0]["y"] == s["t6"]["yA"]
