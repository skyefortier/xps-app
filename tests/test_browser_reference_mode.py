"""Real-browser tests for A7: the no-spectrum reference chart is bound to
OVERLAYS EXISTING, not to the palette being open.

  * selecting an element with no spectrum renders the bare 0–1200 eV reference
    chart (palette open OR closed);
  * closing the palette does not tear it down while overlays persist;
  * removing the LAST overlay tears it back down to the onboarding card — proving
    the trigger is bound to overlays, NOT to spectrum-absence (an empty chart
    only earns its place when there is something to show);
  * stack tabs are still excluded;
  * a source switch still repositions Auger markers in reference mode.

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


def _open_ref(browser, server):
    """Fresh page (no spectrum). Open the palette once to load the reference
    payload; selecting overlays then drives reference mode."""
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.goto(server + "/", wait_until="load")
    pg.click("#btn-ref-panel")
    pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
    assert pg.evaluate("() => !(state.rawBE && state.rawBE.length)") is True   # no spectrum
    return pg


def test_selecting_overlay_with_no_spectrum_shows_reference_chart(browser, server):
    pg = _open_ref(browser, server)
    try:
        pg.evaluate("() => _refToggleElement('U')")
        pg.wait_for_timeout(150)
        st = pg.evaluate("""() => ({
            wanted: _refReferenceModeWanted(),
            xmax: state.chart && state.chart.options.scales.x.max,
            onboard: !!document.querySelector('.onboard-wrap'),
            markers: (_refChartItems(state.chart) || []).length })""")
        assert st["wanted"] is True
        assert st["xmax"] == 1200          # the bare 0–1200 eV reference chart
        assert st["onboard"] is False
        # The overlay markers actually render: _refChartItems(state.chart) is
        # non-empty only when state.chart IS the freshly-built reference chart
        # (the xpsRefLinesPlugin gates on chart === state.chart). Guards the
        # render-timing gap where markers were skipped on the first paint.
        assert st["markers"] > 0
    finally:
        pg.close()


def test_closing_palette_keeps_reference_chart_while_overlays_persist(browser, server):
    pg = _open_ref(browser, server)
    try:
        pg.evaluate("() => _refToggleElement('U')")
        pg.wait_for_timeout(120)
        pg.evaluate("() => toggleRefPanel()")          # CLOSE the palette
        pg.wait_for_timeout(120)
        st = pg.evaluate("""() => ({
            panelOpen: _refPanelOpen, wanted: _refReferenceModeWanted(),
            xmax: state.chart && state.chart.options.scales.x.max })""")
        assert st["panelOpen"] is False
        assert st["wanted"] is True and st["xmax"] == 1200    # persists palette-closed
    finally:
        pg.close()


def test_removing_last_overlay_tears_down_reference_chart(browser, server):
    pg = _open_ref(browser, server)
    try:
        pg.evaluate("() => _refToggleElement('U')")
        pg.wait_for_timeout(120)
        assert pg.evaluate("() => _refReferenceModeWanted()") is True
        pg.evaluate("() => _refToggleElement('U')")    # remove the LAST overlay
        pg.wait_for_timeout(150)
        st = pg.evaluate("""() => ({
            syms: _refGetSel().syms.length, wanted: _refReferenceModeWanted(),
            onboard: !!document.querySelector('.onboard-wrap') })""")
        assert st["syms"] == 0
        assert st["wanted"] is False                   # bound to overlays, not spectrum-absence
        assert st["onboard"] is True                   # onboarding card returns; no empty chart left behind
    finally:
        pg.close()


def test_stack_tab_excluded_from_reference_mode(browser, server):
    pg = _open_ref(browser, server)
    try:
        pg.evaluate("() => { tabManager.createStackTab(); }")
        pg.wait_for_timeout(120)
        st = pg.evaluate("""() => ({
            isStack: isStackTab(tabManager._getTab(tabManager.activeId)),
            wanted: _refReferenceModeWanted() })""")
        assert st["isStack"] is True
        assert st["wanted"] is False                   # stack tabs never enter reference mode
    finally:
        pg.close()


def test_source_switch_updates_auger_in_reference_mode(browser, server):
    pg = _open_ref(browser, server)
    try:
        # Cu has the Cu LMM Auger line; its apparent BE = hv − KE − wf moves with source.
        pg.evaluate("() => { _refToggleElement('Cu'); _refGetSel().includeAuger = true; }")
        pg.wait_for_timeout(120)
        al = pg.evaluate("""() => { _refSetSource('AlKa');
            const it=(_refChartItems(state.chart)||[]).find(m=>m.isAuger); return it?+it.be.toFixed(2):null; }""")
        mg = pg.evaluate("""() => { _refSetSource('MgKa');
            const it=(_refChartItems(state.chart)||[]).find(m=>m.isAuger); return it?+it.be.toFixed(2):null; }""")
        assert al is not None and mg is not None, (al, mg)
        assert al != mg                                # Auger repositions on source switch in reference mode
        # …and a photoelectron line does NOT move on source switch.
        pe_al = pg.evaluate("""() => { _refSetSource('AlKa');
            const it=(_refChartItems(state.chart)||[]).find(m=>!m.isAuger && m.t.orbital==='2p3/2'); return it?+it.be.toFixed(2):null; }""")
        pe_mg = pg.evaluate("""() => { _refSetSource('MgKa');
            const it=(_refChartItems(state.chart)||[]).find(m=>!m.isAuger && m.t.orbital==='2p3/2'); return it?+it.be.toFixed(2):null; }""")
        assert pe_al == pe_mg                          # PE source-invariant
    finally:
        pg.close()
