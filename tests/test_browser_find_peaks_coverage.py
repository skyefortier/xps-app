"""Real-browser test for the Find Peaks periodic-table region picker
(2026-07-13, unit 2 of the "Find Peaks UI improvements round 2" session
— supersedes the flat <select multiple> selector from 2026-07-11 unit 3).

Proves the acceptance bar that needs a live DOM + real backend round-trip
(the pure selection-set/tier-rank helpers are pinned separately in
tests/js/find_peaks_periodic_table.test.js; the tier/filter/label/note
helpers unchanged from unit 3 stay pinned in
tests/js/find_peaks_coverage.test.js): the grid renders far more than the
original 5 basis-test elements, clicking an element reveals its available
core levels color-coded by tier, an element with zero PRACTICAL coverage
(e.g. Hydrogen — its only level, 1s, is valence character for a 1-electron
atom) is disabled, a search filter narrows the grid/offers direct picks
live, picking a fallback level (Fe 2p) sets a plausible ROI and shows the
honest "not cited grammar" note while a curated level (C 1s) shows the
"cited grammar" note and sets a grammar-derived ROI, ctrl-click preserves
a two-region co-fit selection across a filter that hides one of them, and
the existing 5 curated elements are still reachable. Skips cleanly when
Playwright/Chromium/gunicorn are absent, same as the other browser tests.
"""
import glob
import os
import re
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
        "document.querySelectorAll('#fp-pt-grid .fp-pt-cell.selectable').length > 5",
        timeout=5000)


def _click_element(pg, symbol):
    pg.click(f"#fp-pt-grid >> text='{symbol}'")


def _click_level_chip(pg, tag_and_level, ctrl=False):
    selector = f"#fp-expanded-panel >> text='{tag_and_level}'"
    if ctrl:
        # A held-modifier page.click(modifiers=[...]) does not reliably
        # surface as event.ctrlKey on this headless Chromium build (a test
        # harness quirk, not a product bug — verified the shipped handler
        # correctly reads ctrlKey off a genuine MouseEvent). Dispatch one
        # directly instead of holding a key through a mouse move + click.
        pg.dispatch_event(selector, "click", {"ctrlKey": True})
    else:
        pg.click(selector)


def test_grid_lists_far_more_than_the_original_five(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        count = pg.eval_on_selector_all(
            "#fp-pt-grid .fp-pt-cell.selectable", "els => els.length")
        assert count > 20
    finally:
        pg.close()


def test_hydrogen_has_zero_practical_coverage_and_is_disabled(browser, server):
    """Hydrogen's only occupied level (1s) is its single valence electron
    (occupancy 1 of capacity 2) — the practical-fittability filter (unit 1
    of this round) correctly excludes it, so H must render as a disabled,
    non-clickable cell, never a fabricated coverage entry."""
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        cls = pg.eval_on_selector(
            "#fp-pt-grid >> text='H'", "el => el.className")
        assert "selectable" not in cls, cls
    finally:
        pg.close()


def test_clicking_an_element_reveals_its_practical_levels_by_tier(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        _click_element(pg, "Fe")
        chips = pg.eval_on_selector_all(
            "#fp-expanded-panel .fp-level-chip", "els => els.map(e => e.textContent)")
        # Fe 1s (deep core) and Fe 3d (valence) must NOT appear as chips —
        # only the practical levels (2p, 2s, 3p, 4s per the coverage index).
        assert any("2p" in c for c in chips), chips
        assert not any(c.strip() == "1s" or "] 1s" in c for c in chips), chips
        assert not any("3d" in c for c in chips), chips
        # tags are real, not placeholders
        joined = " ".join(chips)
        assert "[sourced]" in joined or "[structure only]" in joined
    finally:
        pg.close()


def test_legend_shows_all_four_coverage_states(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        text = pg.eval_on_selector("#fp-legend", "el => el.textContent")
        assert "Cited grammar" in text
        assert "Sourced position" in text
        assert "No reference position" in text
        assert "No coverage" in text
    finally:
        pg.close()


def test_search_dropdown_item_activates_on_space_key_not_just_enter(browser, server):
    """Regression (2026-07-13 Codex review, unit 2 round 1 NO-GO): the
    search dropdown's focusable role="button" rows only wired up Enter,
    not Space — a keyboard user tabbing to a result and pressing Space
    (the standard button-activation key) got nothing. Both keys must
    select the result."""
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        pg.fill("#fp-regions-filter", "iron")
        pg.wait_for_timeout(100)
        pg.focus("#fp-search-dropdown .fp-search-dropdown-item")
        pg.keyboard.press(" ")
        selected = pg.evaluate("() => Array.from(_fpRegionsSelected)")
        assert selected, "Space on a focused search result must select it"
    finally:
        pg.close()


def test_search_filter_offers_direct_picks_live(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        pg.fill("#fp-regions-filter", "iron")
        pg.wait_for_timeout(100)
        values = pg.eval_on_selector_all(
            "#fp-search-dropdown .fp-search-dropdown-item",
            "els => els.map(e => e.textContent)")
        assert values, "searching 'iron' found nothing in the dropdown"
        assert all("Fe " in v for v in values)

        pg.fill("#fp-regions-filter", "zzz-nonexistent-element")
        pg.wait_for_timeout(100)
        empty = pg.eval_on_selector_all(
            "#fp-search-dropdown .fp-search-dropdown-item", "els => els.length")
        assert empty == 0
    finally:
        pg.close()


def test_selecting_fe2p_shows_honest_fallback_note_and_sets_roi(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        _click_element(pg, "Fe")
        _click_level_chip(pg, "[sourced] 2p")
        note = pg.eval_on_selector(
            "#fp-regions-tier-note", "el => el.textContent")
        # Require the actual negation ("not cited"/"not a cited ... grammar"),
        # not a loose OR of weak substrings — a mis-worded note like "sourced
        # cited fitting grammar" (no negation) must FAIL this (2026-07-11
        # Codex review finding: the prior assertion would have passed it).
        assert re.search(r"not (a )?cited( fitting)? grammar", note.lower()), note
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
        _click_element(pg, "C")
        _click_level_chip(pg, "[cited] 1s")
        note = pg.eval_on_selector(
            "#fp-regions-tier-note", "el => el.textContent")
        assert "cited fitting grammar" in note.lower()
        roi_min = pg.eval_on_selector("#roi-min", "el => el.value")
        roi_max = pg.eval_on_selector("#roi-max", "el => el.value")
        assert float(roi_min) < float(roi_max)
        assert 270.0 <= float(roi_min) <= 285.0
    finally:
        pg.close()


def test_existing_five_curated_elements_still_reachable(browser, server):
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        for region in ("B 1s", "C 1s", "Cl 2p", "N 1s", "U 4f"):
            pg.fill("#fp-regions-filter", region)
            pg.wait_for_timeout(80)
            values = pg.eval_on_selector_all(
                "#fp-search-dropdown .fp-search-dropdown-item",
                "els => els.map(e => e.textContent)")
            assert any(region in v for v in values), \
                f"{region} not found via its own filter: {values}"
        pg.fill("#fp-regions-filter", "")
    finally:
        pg.close()


def test_a_selection_survives_being_filtered_out_of_view(browser, server):
    """Regression (2026-07-11 Codex review, unit 3 round 1 NO-GO — still
    guarded after the unit 2 periodic-table rewrite): select C 1s, then
    ctrl-click Fe 2p to add it as a co-fit pick ("ctrl-click to fit two
    together"). Filtering the view down to something that hides the C
    cell must NOT silently collapse the selection to just Fe 2p —
    _fpRegionsSelected (the single source of truth) is never rebuilt from
    only what's currently rendered."""
    pg = _new_page(browser, server)
    try:
        _open_modal(pg)
        _click_element(pg, "C")
        _click_level_chip(pg, "[cited] 1s")
        _click_element(pg, "Fe")
        _click_level_chip(pg, "[sourced] 2p", ctrl=True)

        selected = pg.evaluate("() => Array.from(_fpRegionsSelected)")
        assert set(selected) == {"C 1s", "Fe 2p"}, selected

        # filter to something that hides the Carbon cell entirely
        pg.fill("#fp-regions-filter", "iron")
        pg.wait_for_timeout(80)
        visible_selectable = pg.eval_on_selector_all(
            "#fp-pt-grid .fp-pt-cell.selectable:not(.dimmed)",
            "els => els.map(e => e.textContent)")
        assert "C" not in visible_selectable, "test setup: C must be dimmed/hidden"

        # selection persists even while C's cell is dimmed out of view
        selected = pg.evaluate("() => Array.from(_fpRegionsSelected)")
        assert set(selected) == {"C 1s", "Fe 2p"}, selected

        # clearing the filter re-renders BOTH cells with the has-selection state
        pg.fill("#fp-regions-filter", "")
        pg.wait_for_timeout(80)
        has_sel = pg.eval_on_selector_all(
            "#fp-pt-grid .fp-pt-cell.has-selection", "els => els.map(e => e.textContent.trim())")
        assert set(has_sel) == {"C", "Fe"}, has_sel
    finally:
        pg.close()
