"""Regression (fix #5): element reference overlays must stay PAINTED across a
charge-correction change.

Bug: `updateChargeCorrection()` rebuilds the main chart via `updatePlot()`, but the
`xpsRefLinesPlugin` gates on `chart === state.chart` and is skipped on the fresh
`new Chart()` first paint (the same render-timing gap `_refRenderReferenceChart`
already works around with a follow-up `state.chart.update('none')`). The CC path
only refreshed panel/legend DOM (renderPeakList / _refOnTabChange) — no chart
repaint — so the overlay lines/bands/labels vanished until the next hover/toggle.
The fix re-issues the guarded overlay repaint (`_refRepaint`) after the CC rebuild.

Why pixel sampling: `_refChartItems(state.chart)` returning items proves the markers
EXIST, not that they were painted — the bug had items present but an unpainted canvas.
So this asserts on the actual pixels in the overlay (line) column.

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


# Count marker-blue pixels down the canvas column at a given corrected BE.
# The element overlay line is solid #4a9eff drawn full-height OVER the data, so a
# painted overlay column reads as a long run of saturated-blue pixels; an unpainted
# column reads as background (a handful). Returns {blue, white, sampled}.
_SAMPLE = r"""(beVal) => {
  const cv = state.chart.canvas, ctx = cv.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const area = state.chart.chartArea, xs = state.chart.scales.x;
  const xpx = Math.round(xs.getPixelForValue(beVal) * dpr);
  const y0 = Math.round(area.top * dpr) + 2, y1 = Math.round(area.bottom * dpr) - 2;
  const d = ctx.getImageData(xpx, y0, 1, y1 - y0).data;
  let blue = 0, white = 0, tot = 0;
  for (let i = 0; i < d.length; i += 4) {
    const r = d[i], g = d[i+1], b = d[i+2], a = d[i+3];
    tot++;
    if (a > 0 && b > 110 && b > r + 25 && b > g + 15) blue++;   // saturated marker blue
    if (a > 0 && r > 180 && g > 180 && b > 180) white++;        // white data curve
  }
  return { blue, white, sampled: tot };
}"""


def _setup_c(page):
    """Inject a C1s-region spectrum with a peak at RAW BE 286.5 (uncorrected),
    select the C overlay (ccShift stays 0). The overlay is added LAST so its
    _refRepaint leaves the baseline chart painted."""
    page.evaluate(
        """() => {
            const raw = [], inten = [];
            const g = (be, c, a, w) => a * Math.exp(-Math.pow(be - c, 2) / (2 * w * w));
            for (let i = 0; i <= 150; i++) {           // 295.0 -> 280.0 step 0.1
                const be = +(295.0 - i * 0.1).toFixed(2);
                raw.push(be); inten.push(500 + g(be, 286.5, 8000, 0.6));
            }
            tabManager.createTab('C cc test', raw, inten);
            const t = tabManager._getTab(tabManager.activeId);
            state.ccShift = 0; if (t) t.ccShift = 0;
            const sel = _refGetSel(); sel.syms = []; sel.source = 'AlKa';
            updatePlot();
            _refToggleElement('C');                    // add overlay last -> painted
        }"""
    )
    page.wait_for_timeout(200)


def test_charge_correction_keeps_reference_overlay_painted(browser, server):
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.goto(server + "/", wait_until="load")
    pg.click("#btn-ref-panel")
    pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
    try:
        _setup_c(pg)

        # Baseline sanity: the C 1s overlay line (nominal 284.44, the literature
        # Powe95 value data/xps/elements-main.json carries as of the 2026-07-16
        # provenance audit -- in range with cc=0) is painted.
        base = pg.evaluate(_SAMPLE, 284.44)
        assert base["blue"] > 200, f"sanity: overlay not painted at baseline: {base}"

        # Apply a REAL charge correction through the actual handler (NOT by poking
        # state.ccShift): graphitic method, observed 286.5 -> ccShift = +2.0. No
        # hover / toggle / panel interaction afterwards — this is exactly the path
        # that used to drop the overlay.
        cc = pg.evaluate(
            """() => {
                document.getElementById('cc-method').value = 'c1s';
                document.getElementById('cc-obs').value = '286.5';
                updateChargeCorrection();
                const items = _refChartItems(state.chart) || [];
                const c = items.find(m => m.t && m.t.orbital === '1s');
                const corr = getCorrectedBE();
                return {
                    ccShift: state.ccShift,
                    cBe: c ? +c.be.toFixed(3) : null,
                    corrLo: +Math.min(...corr).toFixed(2),
                    corrHi: +Math.max(...corr).toFixed(2),
                };
            }"""
        )
        pg.wait_for_timeout(150)

        # Positioning math is unchanged: the overlay stays at its own fixed nominal
        # BE (284.44) regardless of ccShift — it never moves with the correction.
        # The axis (data) shifts by the correction instead: the demo peak (raw
        # 286.5, cc=+2.0) lands at corrected 284.5, close to but not exactly on
        # the 284.44 overlay — that 0.06 eV gap is expected and irrelevant here,
        # since this test samples the OVERLAY's own paint column, not the data
        # curve's position.
        assert abs(cc["ccShift"] - 2.0) < 1e-6, cc
        assert cc["cBe"] == 284.44, f"overlay BE shifted by ccShift (must not): {cc}"
        assert abs(cc["corrLo"] - 278.0) < 0.05 and abs(cc["corrHi"] - 293.0) < 0.05, cc

        # THE REGRESSION ASSERTION: without any further interaction, the overlay is
        # still painted after the charge-correction rebuild.
        after = pg.evaluate(_SAMPLE, 284.44)
        assert after["blue"] > 200, (
            f"regression: reference overlay vanished after charge correction "
            f"(baseline={base}, after={after})"
        )
    finally:
        pg.close()
