"""Real-browser guard for the SAFE de-listing of the shirley_linear background.

Decision (owner, 2026-09-03): zero usage found in every saved project and
fixture visible on this machine, and the JS preview of this method diverges
27-33 % of span from the background the backend actually fits on real
(descending) grids (task-4 parity report). De-list means: it cannot be NEWLY
selected from the menu, but the implementation stays and any saved file that
carries bgType 'shirley_linear' still loads, renders and fits exactly as
before, with a visible note explaining why the option looks unusual.

Pins:
  * fresh page: the option exists but is disabled + hidden; no note shown;
  * a restored tab with ui.bgType == 'shirley_linear' selects it, un-hides
    the option, shows the note, and the JS background still computes;
  * choosing any other type re-hides the option and the note.
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


def _probe(pg):
    return pg.evaluate("""() => {
        const sel = document.getElementById('bg-type');
        const opt = sel.querySelector('option[value="shirley_linear"]');
        const note = document.getElementById('bg-legacy-note');
        return { value: sel.value,
                 optExists: !!opt, optDisabled: !!(opt && opt.disabled), optHidden: !!(opt && opt.hidden),
                 noteExists: !!note,
                 noteShown: !!(note && getComputedStyle(note).display !== 'none') };
    }""")


def test_fresh_page_cannot_newly_select_shirley_linear(browser, server):
    pg = _page(browser, server)
    try:
        p = _probe(pg)
        assert p["optExists"], "option must remain in the DOM so saved files can restore it"
        assert p["optDisabled"] and p["optHidden"], p
        assert p["noteExists"] and not p["noteShown"], p
    finally:
        pg.close()


def test_saved_file_with_shirley_linear_still_loads_renders_and_notes(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("""() => {
            const be=[], inten=[];
            for (let i=0;i<120;i++){ const x=295-i*0.1; be.push(+x.toFixed(2)); inten.push(800+3000*Math.exp(-Math.pow(x-286.5,2)/0.5)+(x<286.5?400:0)); }
            tabManager.createTab('legacy', be, inten);
            const aId = tabManager.activeId;
            tabManager.createTab('other', be, inten);      // switch away so activate is a real switch
            const a = tabManager._getTab(aId);
            a.ui.bgType = 'shirley_linear'; a.ui.bgStart = '295'; a.ui.bgEnd = '283.1';
            tabManager.activateTab(aId);
            const bg = computeBackground(be, inten);
            return { n: be.length, bgLen: bg.length, finite: bg.every(Number.isFinite), nonzero: bg.some(v => v !== 0) };
        }""")
        p = _probe(pg)
        assert p["value"] == "shirley_linear", p
        assert not p["optDisabled"] and not p["optHidden"], p
        assert p["noteShown"], p
        assert out["bgLen"] == out["n"] and out["finite"] and out["nonzero"], out
    finally:
        pg.close()


def test_switching_away_rehides_the_option_and_note(browser, server):
    pg = _page(browser, server)
    try:
        pg.evaluate("""() => {
            const be=[], inten=[];
            for (let i=0;i<60;i++){ be.push(+(295-i*0.1).toFixed(2)); inten.push(1000); }
            tabManager.createTab('legacy', be, inten);
            const aId = tabManager.activeId;
            tabManager.createTab('other', be, inten);
            tabManager._getTab(aId).ui.bgType = 'shirley_linear';
            tabManager.activateTab(aId);
        }""")
        assert _probe(pg)["value"] == "shirley_linear"
        pg.evaluate("""() => { document.getElementById('bg-type').value = 'shirley'; _onBgTypeChange(); }""")
        p = _probe(pg)
        assert p["value"] == "shirley" and p["optDisabled"] and p["optHidden"] and not p["noteShown"], p
    finally:
        pg.close()
