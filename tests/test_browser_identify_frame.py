"""Real-browser tests for reference-line frame coincidence, identify-mode, and
the identify toggle-off fix (bug 2).

Governing invariant: the displayed spectrum, the reference lines, and the
identify click all live in ONE frame (corrected/true BE). The spectrum series
is charge-corrected (peaks at true BE); reference lines draw at literature /
source-projected BE with NO ccShift; the identify click is read in the same
corrected frame and matched against literature with no extra shift.

Skips cleanly when Playwright or a cached Chromium build is unavailable.
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
def page(server):
    exe = _find_chromium()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception:
            if not exe:
                pytest.skip("no usable Chromium build found")
            browser = p.chromium.launch(headless=True, executable_path=exe)
        pg = browser.new_page(viewport={"width": 1500, "height": 950})
        pg.goto(server + "/", wait_until="load")
        pg.click("#btn-ref-panel")
        pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
        yield pg
        browser.close()


# A synthetic U spectrum: raw 4f7/2 at 380.0, 4f5/2 at 390.8. With ccShift=cc,
# corrected 4f7/2 = 380 - cc. cc=2.7 -> 377.3 (literature). U overlay selected.
def setup_u(page, cc=2.7):
    page.evaluate(
        """(cc) => {
            const N=451, raw=[], inten=[];
            const g=(be,c,a,w)=>a*Math.exp(-Math.pow(be-c,2)/(2*w*w));
            for(let i=0;i<N;i++){ const be=370+i*0.1; raw.push(be);
                inten.push(500 + g(be,380.0,10000,1.1) + g(be,390.8,7000,1.1)); }
            tabManager.createTab('U test', raw, inten);
            const t=tabManager._getTab(tabManager.activeId);
            state.ccShift=cc; if(t)t.ccShift=cc;
            if(typeof _refClearIdentify==='function') _refClearIdentify();
            if(placeMode) togglePlaceMode(placeMode);
            const sel=_refGetSel(); sel.syms=[]; sel.source='AlKa';
            _refToggleElement('U');
            updatePlot();
        }""", cc)
    page.wait_for_timeout(150)


def _peak_client_xy(page, corrected_be):
    return page.evaluate(
        """(be) => {
            const sx=state.chart.scales.x, sy=state.chart.scales.y;
            const rect=state.chart.canvas.getBoundingClientRect();
            return { x: rect.left + sx.getPixelForValue(be), y: rect.top + (sy.top+sy.bottom)/2 };
        }""", corrected_be)


def test_u_4f72_reference_coincides_with_corrected_peak(page):
    setup_u(page, 2.7)
    r = page.evaluate("""() => {
        const items=_refChartItems(state.chart)||[];
        const ref=items.find(m=>m.sym==='U' && m.t.orbital==='4f7/2');
        const ds=state.chart.data.datasets.find(d=>d.label==='Data');
        let pk=null; for(const p of ds.data){ if(!pk||p.y>pk.y) pk=p; }
        return { refBe: ref && ref.be, peakX: pk && +pk.x.toFixed(3) };
    }""")
    assert abs(r["refBe"] - 377.30) < 0.01            # reference at literature BE
    assert abs(r["peakX"] - 377.30) < 0.05            # corrected peak at same BE
    assert abs(r["refBe"] - r["peakX"]) < 0.05        # they coincide


def test_identify_returns_u_4f72_on_charge_corrected_spectrum(page):
    setup_u(page, 2.7)
    # Arm via the real button, real-click the corrected peak.
    page.click("#ref-identify-btn")
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])
    page.wait_for_timeout(200)
    r = page.evaluate("""() => {
        const tab=_refActiveTab(); const id=tab&&tab._refIdentify;
        return id ? { top:id.cands[0]&&id.cands[0].label, n:id.cands.length } : null;
    }""")
    assert r is not None
    assert r["top"] == "U 4f7/2"
    assert r["n"] >= 1


def test_identify_toggle_off_clears_state_and_restores_selection(page):
    setup_u(page, 2.7)
    page.click("#ref-identify-btn")                    # arm
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])                 # produce identify state + highlight
    page.wait_for_timeout(150)
    assert page.evaluate("() => !!(_refActiveTab() && _refActiveTab()._refIdentify)") is True
    # Re-click the Identify control -> toggle OFF
    page.click("#ref-identify-btn")
    page.wait_for_timeout(150)
    state = page.evaluate("""() => ({
        placeMode: placeMode,
        identify: !!(_refActiveTab() && _refActiveTab()._refIdentify)
    })""")
    assert state["placeMode"] is None                  # mode exited
    assert state["identify"] is False                  # state + highlight cleared
    # A subsequent chart click does NOT re-arm identify (normal click restored).
    page.mouse.click(xy["x"], xy["y"])
    page.wait_for_timeout(100)
    assert page.evaluate("() => !!(_refActiveTab() && _refActiveTab()._refIdentify)") is False


def test_identify_esc_clears_state(page):
    setup_u(page, 2.7)
    page.click("#ref-identify-btn")
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])
    page.wait_for_timeout(150)
    assert page.evaluate("() => !!(_refActiveTab() && _refActiveTab()._refIdentify)") is True
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    state = page.evaluate("""() => ({
        placeMode: placeMode,
        identify: !!(_refActiveTab() && _refActiveTab()._refIdentify)
    })""")
    assert state["placeMode"] is None
    assert state["identify"] is False


def test_u_shallow_lines_out_of_window(page):
    # Step 4: in the U 4f window (~367-412 eV) the shallow/deep lines sit OUTSIDE
    # the displayed range. Correct out-of-window behavior, not filtering.
    setup_u(page, 2.7)
    rows = page.evaluate("""() => {
        const sel=_refGetSel(); sel.showWeak=true;
        const sx=state.chart.scales.x, lo=sx.min, hi=sx.max;
        const o={};
        for(const m of _refTransitionsFor('U')) o[m.t.orbital] = (m.be>=lo && m.be<=hi);
        return o;
    }""")
    assert rows["4f7/2"] is True
    assert rows["4f5/2"] is True
    for orb in ["5d5/2", "5d3/2", "5p3/2", "6p3/2", "6p1/2", "6s", "4d5/2", "4s"]:
        assert rows[orb] is False                      # off-screen, correctly not drawn


def test_zero_ccshift_reference_positions_unchanged(page):
    # Regression: reference positions are source/charge invariant. ccShift=0
    # leaves U 4f7/2 at 377.30 and curated Cu 2p3/2 at 932.67 (no shift ever).
    setup_u(page, 0.0)
    r = page.evaluate("""() => {
        const u = _refTransitionsFor('U').find(m=>m.t.orbital==='4f7/2');
        const sel=_refGetSel(); sel.syms=[]; _refToggleElement('Cu');
        const cu = _refTransitionsFor('Cu').find(m=>m.t.orbital==='2p3/2');
        return { u: u.be, cu: cu.be };
    }""")
    assert abs(r["u"] - 377.30) < 0.01
    assert abs(r["cu"] - 932.67) < 0.01
