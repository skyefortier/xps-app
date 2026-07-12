"""Real-browser test for the expanded Find Peaks element/region selector
(2026-07-11, unit 3).

Proves the acceptance bar that needs a live DOM + real backend round-trip
(the pure filter/label/tier-note helpers are pinned separately in
tests/js/find_peaks_coverage.test.js): the selector lists far more than
the original 5 basis-test elements, a search filter narrows it live, each
option's tier is real (not a placeholder), picking a fallback element
(Fe 2p) sets a plausible ROI and shows the honest "not cited grammar"
note while a curated element (C 1s) shows the "cited grammar" note and
sets a grammar-derived ROI, and the existing 5 curated elements' basic
behavior (selectable, same values) is unchanged. Skips cleanly when
Playwright/Chromium/gunicorn are absent, same as the other browser tests.
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


def _new_page(browser, server):
    pg = browser.new_page(viewport={"width": 1400, "height": 950})
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
    pg.wait_for_function(
        "document.getElementById('fp-regions').options.length > 5", timeout=5000)


def test_selector_lists_far_more_than_the_original_five(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        count = pg.eval_on_selector(
            "#fp-regions", "el => el.options.length")
        assert count > 100
    finally:
        pg.close()


def test_every_option_shows_a_real_tier_tag(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        tags = pg.eval_on_selector_all(
            "#fp-regions option",
            "els => els.map(e => e.textContent.match(/^\\[([^\\]]+)\\]/)[1])")
        assert set(tags) <= {"cited", "sourced", "structure only"}
        assert "cited" in tags
        assert "sourced" in tags or "structure only" in tags
    finally:
        pg.close()


def test_search_filter_narrows_the_list_live(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        pg.fill("#fp-regions-filter", "iron")
        pg.wait_for_timeout(100)
        opts = pg.eval_on_selector_all(
            "#fp-regions option", "els => els.map(e => e.value)")
        assert opts, "searching 'iron' found nothing"
        assert all("Fe " in v for v in opts)

        pg.fill("#fp-regions-filter", "zzz-nonexistent-element")
        pg.wait_for_timeout(100)
        empty = pg.eval_on_selector_all(
            "#fp-regions option", "els => els.length")
        assert empty == 0
    finally:
        pg.close()


def test_selecting_fe2p_shows_honest_fallback_note_and_sets_roi(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        pg.fill("#fp-regions-filter", "Fe 2p")
        pg.wait_for_timeout(100)
        pg.select_option("#fp-regions", "Fe 2p")
        pg.dispatch_event("#fp-regions", "change")
        pg.wait_for_timeout(50)
        note = pg.eval_on_selector(
            "#fp-regions-tier-note", "el => el.textContent")
        assert "not cited grammar" in note.lower() or "sourced" in note.lower()
        roi_min = pg.eval_on_selector("#roi-min", "el => el.value")
        roi_max = pg.eval_on_selector("#roi-max", "el => el.value")
        assert float(roi_min) < float(roi_max)
        assert 690.0 <= float(roi_min) <= 715.0    # Fe 2p3/2 neighborhood
    finally:
        pg.close()


def test_selecting_curated_element_shows_cited_grammar_note_and_sets_roi(
        browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        pg.fill("#fp-regions-filter", "C 1s")
        pg.wait_for_timeout(100)
        pg.select_option("#fp-regions", "C 1s")
        pg.dispatch_event("#fp-regions", "change")
        pg.wait_for_timeout(50)
        note = pg.eval_on_selector(
            "#fp-regions-tier-note", "el => el.textContent")
        assert "cited fitting grammar" in note.lower()
        roi_min = pg.eval_on_selector("#roi-min", "el => el.value")
        roi_max = pg.eval_on_selector("#roi-max", "el => el.value")
        assert float(roi_min) < float(roi_max)
        assert 270.0 <= float(roi_min) <= 285.0
    finally:
        pg.close()


def test_existing_five_curated_elements_still_selectable_and_unchanged(
        browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        for region in ("B 1s", "C 1s", "Cl 2p", "N 1s", "U 4f"):
            pg.fill("#fp-regions-filter", region)
            pg.wait_for_timeout(80)
            values = pg.eval_on_selector_all(
                "#fp-regions option", "els => els.map(e => e.value)")
            assert region in values, f"{region} not found via its own filter"
        pg.fill("#fp-regions-filter", "")
    finally:
        pg.close()
