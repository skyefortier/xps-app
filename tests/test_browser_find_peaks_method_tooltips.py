"""Real-browser test for the Find Peaks Method dropdown's tooltips
(2026-07-14 bug report: "the dropdown was renamed but the tooltip still
reads the vague '...the right choice unless you have a reason
otherwise' instead of explaining what the method does").

Two distinct tooltips were involved:
1. The "Method" field LABEL's own hover tooltip
   (``FP_STRINGS.tips.method``) — previously a single vague sentence
   pointing at the recommended default with no explanation of what any
   option actually does.
2. Each ``<option>``'s own ``title`` attribute — previously the RAW
   BACKEND METHOD LABEL (e.g. "Auto — model comparison (IC)", straight
   from ``autofit/methods/*.py``'s ``label`` class attribute), so
   hovering an option before selecting it showed jargon, not an
   explanation.

Both are fixed to show plain-English text that states what each method
does and when to use it — the SAME quality bar as the hint box already
shown below the dropdown once a method is selected
(``FP_STRINGS.methods[id].hint``), just available on hover too, without
requiring a click first.
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


def _open_modal(pg, browser, server):
    pg2 = browser.new_page(viewport={"width": 1000, "height": 900})
    pg2.goto(server + "/", wait_until="load")
    pg2.evaluate("""() => {
        const raw = [], inten = [];
        for (let i = 0; i <= 200; i++) { raw.push(190 + i * 0.1); inten.push(1000); }
        tabManager.createTab('T', raw, inten);
    }""")
    pg2.evaluate("() => openFindPeaksModal()")
    pg2.wait_for_selector("#find-peaks-overlay.open", timeout=5000)
    return pg2


def test_method_field_tooltip_is_not_the_old_vague_sentence(browser, server):
    pg = _open_modal(None, browser, server)
    try:
        title = pg.eval_on_selector("#fp-method-label", "el => el.title")
        assert "right choice unless you have a reason" not in title, title
        # must actually explain something, not just point at the default
        assert len(title) > 60
    finally:
        pg.close()


def test_every_method_option_has_a_plain_english_tooltip_not_the_raw_backend_label(
        browser, server):
    pg = _open_modal(None, browser, server)
    try:
        options = pg.eval_on_selector_all(
            "#fp-method option",
            "els => els.map(e => ({ value: e.value, title: e.title, text: e.textContent }))")
        assert len(options) == 4, options
        for opt in options:
            # the OLD behavior put the raw backend method label here
            # (e.g. "Auto — model comparison (IC)", "Sparse / MAP (fast
            # auto)", "Bayesian (exchange Monte Carlo)") -- none of
            # those exact jargon strings should appear as a tooltip now
            assert "IC)" not in opt["title"], opt
            assert "Sparse / MAP" not in opt["title"], opt
            assert "exchange Monte Carlo" not in opt["title"], opt
            # each tooltip must be a real, substantive explanation, not
            # just repeating the visible option label back
            assert len(opt["title"]) > 40, opt
            assert opt["title"] != opt["text"], opt
    finally:
        pg.close()


def test_each_method_tooltip_explains_what_it_does_and_when_to_use_it(browser, server):
    pg = _open_modal(None, browser, server)
    try:
        titles = {
            o["value"]: o["title"]
            for o in pg.eval_on_selector_all(
                "#fp-method option",
                "els => els.map(e => ({ value: e.value, title: e.title }))")
        }
        # spot-check content, not just length -- each method's tooltip
        # should mention its own distinguishing behavior
        assert "models" in titles["ic_model_comparison"].lower()
        assert "confidence" in titles["bayesian_exchange_mc"].lower()
        assert "count" in titles["sparse_map"].lower() or "estimate" in titles["sparse_map"].lower()
        assert "current" in titles["least_squares"].lower() or "refit" in titles["least_squares"].lower()
    finally:
        pg.close()
