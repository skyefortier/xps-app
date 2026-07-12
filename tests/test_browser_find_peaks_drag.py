"""Real-browser test for the Find Peaks draggable modal (2026-07-11,
unit 2).

Proves the acceptance bar that needs a live DOM + real mouse events:
click-dragging the modal by its header repositions it, the position
clamps within the viewport (never fully off-screen — a header band stays
reachable, same contract as the Reference palette's clampToViewport),
only the header initiates a drag (clicking the close button must still
close the modal, never start a drag), and inner controls (the region
select) keep working after a drag. Skips cleanly when Playwright/
Chromium/gunicorn are absent, same as the other browser tests.
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


def _new_page(browser, server, width=1400, height=950):
    pg = browser.new_page(viewport={"width": width, "height": height})
    pg.goto(server + "/", wait_until="load")
    return pg


def _open_modal(pg):
    pg.evaluate("""() => {
        const raw = [], inten = [];
        for (let i = 0; i <= 200; i++) { raw.push(190 + i * 0.1); inten.push(1000); }
        tabManager.createTab('T', raw, inten);
    }""")
    pg.evaluate("() => openFindPeaksModal()")
    pg.wait_for_selector("#find-peaks-overlay.open", timeout=5000)


def _box(pg):
    return pg.eval_on_selector(
        "#find-peaks-modal-box",
        "el => { const r = el.getBoundingClientRect(); "
        "return { left: r.left, top: r.top, right: r.right, bottom: r.bottom, "
        "width: r.width, height: r.height }; }")


def test_drag_by_header_repositions_the_modal(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        before = _box(pg)
        header = pg.locator("#find-peaks-modal-box h3.fp-drag-handle")
        hb = header.bounding_box()
        start_x, start_y = hb["x"] + 30, hb["y"] + hb["height"] / 2
        pg.mouse.move(start_x, start_y)
        pg.mouse.down()
        pg.mouse.move(start_x + 220, start_y + 140, steps=8)
        pg.mouse.up()
        after = _box(pg)
        assert abs(after["left"] - before["left"] - 220) < 3
        assert abs(after["top"] - before["top"] - 140) < 3
        # position is now explicit (fixed), not the flex-centered default
        pos = pg.eval_on_selector(
            "#find-peaks-modal-box", "el => getComputedStyle(el).position")
        assert pos == "fixed"
    finally:
        pg.close()


def test_drag_clamps_within_viewport_never_fully_offscreen(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        header = pg.locator("#find-peaks-modal-box h3.fp-drag-handle")
        hb = header.bounding_box()
        start_x, start_y = hb["x"] + 30, hb["y"] + hb["height"] / 2
        pg.mouse.move(start_x, start_y)
        pg.mouse.down()
        # drag far past the top-left corner, well off-screen
        pg.mouse.move(-5000, -5000, steps=5)
        pg.mouse.up()
        b = _box(pg)
        vw = pg.evaluate("() => innerWidth")
        vh = pg.evaluate("() => innerHeight")
        assert b["right"] > 0 and b["left"] < vw       # not fully off-screen horizontally
        assert b["bottom"] > 0 and b["top"] < vh - 1   # header band stays reachable

        # drag far past the bottom-right corner too
        header2 = pg.locator("#find-peaks-modal-box h3.fp-drag-handle")
        hb2 = header2.bounding_box()
        pg.mouse.move(hb2["x"] + 30, hb2["y"] + hb2["height"] / 2)
        pg.mouse.down()
        pg.mouse.move(vw + 5000, vh + 5000, steps=5)
        pg.mouse.up()
        b2 = _box(pg)
        assert b2["left"] < vw and b2["right"] > 0
        assert b2["top"] < vh
    finally:
        pg.close()


def test_close_button_does_not_start_a_drag_and_still_closes(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        before = _box(pg)
        pg.click("#find-peaks-modal-box h3 button")   # the close (X) button
        # closed, not dragged
        is_open = pg.evaluate(
            "() => document.getElementById('find-peaks-overlay').classList.contains('open')")
        assert is_open is False
        is_dragging = pg.evaluate(
            "() => document.getElementById('find-peaks-modal-box').classList.contains('dragging')")
        assert is_dragging is False
    finally:
        pg.close()


def test_inner_controls_still_work_after_a_drag(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        header = pg.locator("#find-peaks-modal-box h3.fp-drag-handle")
        hb = header.bounding_box()
        pg.mouse.move(hb["x"] + 30, hb["y"] + hb["height"] / 2)
        pg.mouse.down()
        pg.mouse.move(hb["x"] + 120, hb["y"] + 60, steps=5)
        pg.mouse.up()
        # a select inside the (now-moved) modal must still be usable
        pg.select_option("#fp-material", "conductor")
        val = pg.eval_on_selector("#fp-material", "el => el.value")
        assert val == "conductor"
        pg.select_option("#fp-method", "least_squares")
        method_val = pg.eval_on_selector("#fp-method", "el => el.value")
        assert method_val == "least_squares"
    finally:
        pg.close()


def test_modal_resets_to_centered_on_fresh_open(browser, server):
    """A drag is a 'move it out of the way for now' convenience — the
    next fresh open starts centered again, not stuck wherever it was."""
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        header = pg.locator("#find-peaks-modal-box h3.fp-drag-handle")
        hb = header.bounding_box()
        pg.mouse.move(hb["x"] + 30, hb["y"] + hb["height"] / 2)
        pg.mouse.down()
        pg.mouse.move(hb["x"] + 300, hb["y"] + 200, steps=5)
        pg.mouse.up()
        assert pg.eval_on_selector(
            "#find-peaks-modal-box", "el => getComputedStyle(el).position") == "fixed"

        pg.click("#find-peaks-modal-box h3 button")  # close
        pg.evaluate("() => openFindPeaksModal()")     # reopen
        pg.wait_for_selector("#find-peaks-overlay.open", timeout=5000)
        pos = pg.eval_on_selector(
            "#find-peaks-modal-box", "el => el.style.position")
        assert pos == ""    # inline override cleared -> back to CSS-centered
    finally:
        pg.close()
