"""Real-browser tests for the A5 floating Reference palette + its interim
identify-passthrough guard.

Proves the A5 acceptance criteria that need a live DOM/layout:
  * the palette is removed from the chart flex flow — the chart reclaims full
    width whether the palette is open or closed (not merely overlapped);
  * a stale/offscreen saved position clamps back inside the viewport on open;
  * collapsed state persists across a reload;
  * below ~640px the palette docks as a bottom sheet and dragging is disabled;
  * the palette is normally interactive (pointer-events auto) when identify is
    NOT armed;
  * the interim guard yields pointer events while identify IS armed, AND Esc
    still disarms it then — so the guard can never soft-lock the user.

(The "identify click reaches the chart while the palette floats" criterion is
already proven by the identify tests in test_browser_identify_frame.py, which
fail without this guard.) Skips cleanly when Playwright/Chromium are absent.
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


def _new_page(browser, server, width=1500, height=950):
    pg = browser.new_page(viewport={"width": width, "height": height})
    pg.goto(server + "/", wait_until="load")
    return pg


# A synthetic U spectrum + U overlay; opens the palette. Mirrors the identify
# tests' setup so the identify controls (#ref-identify-btn) render.
def _setup_u(pg, cc=2.7):
    pg.evaluate(
        """(cc) => {
            const raw=[], inten=[];
            for (let i=0;i<=450;i++){ raw.push(370+i*0.1); inten.push(1000); }
            tabManager.createTab('U', raw, inten);
            const t=tabManager._getTab(tabManager.activeId);
            state.ccShift=cc; if(t)t.ccShift=cc;
        }""", cc)
    pg.click("#btn-ref-panel")
    pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
    pg.evaluate("() => _refToggleElement('U')")
    pg.wait_for_timeout(200)


def test_chart_reclaims_full_width_palette_out_of_flow(browser, server):
    pg = _new_page(browser, server)
    try:
        w_closed = pg.evaluate("() => document.getElementById('main-chart-wrap').offsetWidth")
        pg.click("#btn-ref-panel")
        pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
        pg.wait_for_timeout(150)
        info = pg.evaluate("""() => {
            const wrap=document.getElementById('main-chart-wrap');
            const panel=document.getElementById('ref-panel');
            return { wrapW: wrap.offsetWidth, pos: getComputedStyle(panel).position };
        }""")
        # position:fixed => out of flex flow => chart width unchanged by opening.
        assert info["pos"] == "fixed"
        assert abs(info["wrapW"] - w_closed) <= 2, (w_closed, info["wrapW"])
    finally:
        pg.close()


def test_stale_offscreen_position_clamps_into_viewport(browser, server):
    pg = _new_page(browser, server)
    try:
        # Seed a far-offscreen (stale) saved geometry BEFORE opening.
        pg.evaluate("() => localStorage.setItem('xps.refPalette.v1', JSON.stringify({left:9000, top:9000}))")
        pg.click("#btn-ref-panel")
        pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
        pg.wait_for_timeout(150)
        r = pg.evaluate("""() => {
            const p=document.getElementById('ref-panel').getBoundingClientRect();
            return { left:p.left, top:p.top, right:p.right, vw:innerWidth, vh:innerHeight };
        }""")
        assert r["left"] >= 0 and r["right"] <= r["vw"] + 1          # fully on-screen horizontally
        assert 0 <= r["top"] <= r["vh"] - 80                        # header band reachable
    finally:
        pg.close()


def test_collapse_state_persists_across_reload(browser, server):
    pg = _new_page(browser, server)
    try:
        pg.evaluate("() => localStorage.removeItem('xps.refPalette.v1')")
        pg.click("#btn-ref-panel")
        pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
        pg.click("#ref-collapse-btn")
        pg.wait_for_timeout(100)
        assert pg.evaluate("() => document.getElementById('ref-panel').classList.contains('collapsed')") is True
        # reload; reopen; collapse must be remembered
        pg.reload(wait_until="load")
        pg.click("#btn-ref-panel")
        pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
        pg.wait_for_timeout(150)
        st = pg.evaluate("""() => {
            const p=document.getElementById('ref-panel');
            return { collapsed: p.classList.contains('collapsed'),
                     bodyHidden: getComputedStyle(p.querySelector('.panel-body')).display === 'none' };
        }""")
        assert st["collapsed"] is True and st["bodyHidden"] is True
    finally:
        pg.close()


def test_mobile_fallback_is_bottom_sheet_with_drag_disabled(browser, server):
    pg = _new_page(browser, server, width=600, height=800)
    try:
        # Open via the API: at 600px the app's toolbar restacks and can intercept a
        # real button click — unrelated to the palette. This test targets the
        # palette's bottom-sheet geometry + drag-disable, not the narrow toolbar.
        pg.evaluate("() => toggleRefPanel()")
        pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
        pg.wait_for_timeout(150)
        info = pg.evaluate("""() => {
            const p=document.getElementById('ref-panel'), r=p.getBoundingClientRect();
            // simulate a header drag attempt; mobile must NOT enter dragging
            _refPaletteDragStart({ clientX:100, clientY:10, target:document.getElementById('ref-panel-header'),
                                   preventDefault(){} });
            const dragging = p.classList.contains('dragging');
            return { isMobile:_refPaletteIsMobile(), left:r.left, right:r.right, bottom:r.bottom,
                     vw:innerWidth, vh:innerHeight, dragging };
        }""")
        assert info["isMobile"] is True
        assert info["left"] <= 1 and abs(info["right"] - info["vw"]) <= 1     # full width
        assert abs(info["bottom"] - info["vh"]) <= 1                          # docked to bottom
        assert info["dragging"] is False                                     # drag disabled on touch
    finally:
        pg.close()


def test_palette_interactive_when_identify_not_armed(browser, server):
    pg = _new_page(browser, server)
    try:
        _setup_u(pg)
        st = pg.evaluate("""() => {
            const p=document.getElementById('ref-panel');
            return { passthrough: p.classList.contains('identify-passthrough'),
                     pe: getComputedStyle(p).pointerEvents };
        }""")
        assert st["passthrough"] is False and st["pe"] != "none"
    finally:
        pg.close()


def test_esc_disarms_identify_even_under_passthrough_guard(browser, server):
    pg = _new_page(browser, server)
    try:
        _setup_u(pg)
        pg.wait_for_selector("#ref-identify-btn", timeout=10000)
        pg.click("#ref-identify-btn")                       # arm identify
        pg.wait_for_timeout(100)
        armed = pg.evaluate("""() => {
            const p=document.getElementById('ref-panel');
            return { mode: placeMode, passthrough: p.classList.contains('identify-passthrough'),
                     pe: getComputedStyle(p).pointerEvents };
        }""")
        assert armed["mode"] == "identify"
        assert armed["passthrough"] is True and armed["pe"] == "none"   # guard active
        pg.keyboard.press("Escape")                        # the always-available exit
        pg.wait_for_timeout(100)
        after = pg.evaluate("""() => {
            const p=document.getElementById('ref-panel');
            return { mode: placeMode, passthrough: p.classList.contains('identify-passthrough'),
                     pe: getComputedStyle(p).pointerEvents };
        }""")
        assert after["mode"] is None                       # disarmed despite guard (no soft-lock)
        assert after["passthrough"] is False and after["pe"] != "none"  # interactivity restored
    finally:
        pg.close()
