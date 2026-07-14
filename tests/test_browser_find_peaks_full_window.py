"""Real-browser test for the "fit the entire window" checkbox's actual
visible effect (2026-07-14 bug report — the checkbox was a no-op).

ROOT CAUSE (found by tracing, not guessed): the backend's position-bound
widening (autofit/engine.py's ``fit_full_window`` — added 2026-07-13)
works exactly as designed and reaches the winning candidate correctly,
but has near-zero observable effect on real spectra, because Find
Peaks' out-of-grammar detection/proposal machinery already finds real
peaks wherever they sit, independent of this flag. The user's actual
symptom ("ROI: 278.0-290.4" shown when 278-298 was set) traced to a
DIFFERENT, purely-frontend bug: ``updatePlot()`` freezes the chart's
background/fit-curve rendering to ``state.fitResult``'s own frozen
``be``/``bgIntensity`` arrays once ANY fit exists (a prior manual Run
Fit, or Auto-Fit C1s Graphite) — and ``applyFindPeaks()`` never touched
``state.fitResult`` at all, so applying new Find-Peaks-suggested peaks
left the chart showing background/fit cropped to whatever OLD, possibly
much narrower range a prior fit happened to freeze it to, regardless of
how wide a window Find Peaks itself just used.

The fix: when the analyze request that produced the applied peaks used
``fit_full_window: true``, ``applyFindPeaks()`` now clears
``state.fitResult`` before re-rendering — ``updatePlot()`` then falls
back to its existing unfit-preview path (``getROIData()`` + client-side
``computeBackground()``), which correctly spans whatever the CURRENT
``#roi-min``/``#roi-max`` fields say (the same fields Find Peaks itself
just read at submit time). Default (unchecked) leaves
``state.fitResult`` untouched — today's (possibly stale/cropped)
behavior is unchanged, as required.

This file proves the full, real bug scenario end to end: a tab with a
PRIOR, narrower frozen fit (matching the bug report's exact numbers),
then Find Peaks run + applied with the checkbox on vs. off, checking the
ACTUAL RENDERED CHART DATA (not just the backend response) for both.
Skips cleanly when Playwright/Chromium/gunicorn are absent, same as the
other browser tests.
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
        [gunicorn, "app:app", "-w", "1", "-b", f"127.0.0.1:{port}", "--timeout", "90"],
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
    pg = browser.new_page(viewport={"width": 1000, "height": 1000})
    pg.goto(server + "/", wait_until="load")
    return pg


def _load_c1s_with_stale_narrow_fit(pg):
    """A clean, single-peak C1s-shaped spectrum on a wide 275-300 eV
    range, with a PRE-EXISTING frozen ``state.fitResult`` spanning only
    278.0-290.4 eV (the bug report's own numbers) — reproducing the
    "prior manual fit / Auto-Fit C1s Graphite left the chart frozen
    narrow" scenario exactly."""
    pg.evaluate("""() => {
        const raw = [], inten = [];
        for (let i = 0; i <= 400; i++) {
            const be = 275.0 + i * 0.05625;
            raw.push(be);
            const g = (c, a, w) => a * Math.exp(-4 * Math.log(2) * ((be - c) / w) ** 2);
            inten.push(300 + g(284.5, 6000, 0.8));
        }
        tabManager.createTab('C1s', raw, inten);
        const narrowBE = raw.filter(b => b >= 278.0 && b <= 290.4);
        const narrowBG = narrowBE.map(() => 300);
        const narrowSub = narrowBE.map((b, i) => inten[raw.indexOf(narrowBE[i])] - 300);
        state.fitResult = {
            chi: 10, chiReduced: 1.0, rmse: 1,
            be: narrowBE, bgIntensity: narrowBG, bgSubtracted: narrowSub,
            fittedY: narrowBE.map((b, i) => narrowSub[i] + 300),
            roiRange: { min: '278.0', max: '290.4' },
        };
        document.getElementById('roi-min').value = 278.0;
        document.getElementById('roi-max').value = 298.0;
        updatePlot();
        // The status bar (χ²ᵣ, R-factor, "ROI: ..." readout) AND the
        // right-side Results panel are all SEPARATE pieces of DOM state
        // from the chart -- populate them the same way a prior real fit
        // would have (via _updateROIDisplay/_updateRFactorUI/
        // renderResults, not hand-rolled strings), to reproduce the bug
        // report's exact status-bar/results-panel symptom, not just the
        // chart-dataset symptom.
        _updateROIDisplay(state.fitResult.roiRange);
        document.getElementById('sb-chi').textContent = '1.000';
        document.getElementById('fit-quality').textContent = 'χ²ᵣ = 1.00';
        document.getElementById('fit-quality').setAttribute('data-xps-tip', 'stale tip');
        _updateRFactorUI({ rPct: 3.2, level: 'good' });
        renderResults();
    }""")


def _status_bar_snapshot(pg):
    return pg.evaluate("""() => ({
        sbRoi: document.getElementById('sb-roi').textContent,
        sbChi: document.getElementById('sb-chi').textContent,
        fitQuality: document.getElementById('fit-quality').textContent,
        sbRuns: document.getElementById('sb-runs').textContent,
        resultsArea: document.getElementById('results-area').innerHTML,
        quantifyArea: document.getElementById('quantify-area').innerHTML,
    })""")


def _run_and_apply_find_peaks(pg, full_window):
    pg.evaluate("() => openFindPeaksModal()")
    pg.wait_for_selector("#find-peaks-overlay.open", timeout=5000)
    pg.wait_for_selector("#fp-pt-grid .fp-pt-cell.selectable", timeout=5000)
    pg.click("#fp-pt-grid >> text='C'")
    pg.wait_for_timeout(150)
    pg.click("#fp-expanded-panel >> text='[cited] 1s'")
    pg.wait_for_timeout(150)
    if full_window:
        pg.check("#fp-opt-fit_full_window")
    else:
        pg.uncheck("#fp-opt-fit_full_window")
    opts = pg.eval_on_selector("#fp-options", "el => JSON.parse(el.value).fit_full_window")
    assert opts is full_window, f"checkbox state not reflected in request options: {opts}"
    pg.click("#fp-run")
    pg.wait_for_function(
        "document.getElementById('fp-results').style.display === 'block'",
        timeout=90000)
    pg.wait_for_timeout(200)
    pg.click("#fp-apply")
    pg.wait_for_selector("#find-peaks-apply-confirm-overlay.open", timeout=5000)
    pg.click("#find-peaks-apply-confirm-proceed")
    pg.wait_for_timeout(200)


def _background_span(pg):
    return pg.evaluate("""() => {
        const bg = state.chart.data.datasets.find(d => /background/i.test(d.label || ''));
        if (!bg) return null;
        const xs = bg.data.map(p => p.x);
        return { min: Math.min(...xs), max: Math.max(...xs) };
    }""")


def test_checkbox_off_preserves_todays_cropped_behavior(browser, server):
    """Regression guard for the DEFAULT path: unchecked must produce
    byte-for-byte the same (buggy/stale) behavior as before this fix —
    the chart stays frozen to the prior fit's narrow 278.0-290.4 range,
    exactly matching the bug report's own observed numbers, AND the
    status bar (χ²ᵣ, R-factor, "ROI: ...") and the Results panel stay
    exactly as stale as they always were too — the fix must not touch
    anything when unchecked."""
    pg = _new_page(browser, server)
    try:
        _load_c1s_with_stale_narrow_fit(pg)
        before = _background_span(pg)
        assert before["max"] == pytest.approx(290.35625, abs=0.01)
        status_before = _status_bar_snapshot(pg)

        _run_and_apply_find_peaks(pg, full_window=False)

        after = _background_span(pg)
        assert after["max"] == pytest.approx(290.35625, abs=0.01), (
            "default (unchecked) must leave today's cropped behavior "
            f"unchanged: {after}")
        fit_result_is_null = pg.evaluate("() => state.fitResult === null")
        assert not fit_result_is_null, (
            "unchecked must NOT touch state.fitResult at all")
        status_after = _status_bar_snapshot(pg)
        assert status_after == status_before, (
            f"unchecked must not touch the status bar either: "
            f"{status_before} -> {status_after}")
    finally:
        pg.close()


def test_checkbox_on_extends_fit_and_background_to_the_full_window(browser, server):
    """The actual fix: checked must make the background/fit-curve span
    the FULL user-set ROI (278-298), not the stale frozen 278.0-290.4
    range from a prior fit — this is the literal "checkbox on -> the
    result fit spans the full ROI" behavior asked for. ALSO must clear
    the status bar's stale "ROI: 278.0-290.4 eV" / χ²ᵣ / R-factor
    readouts (Codex review finding, 2026-07-14: the chart-only fix left
    this half of the bug report's own reported symptom unaddressed —
    the header could still show the OLD fit's numbers even after the
    chart itself was fixed) AND the Results panel + Quantify panel
    (Codex recheck findings, 2026-07-14: renderResults() was never
    called, so the Results panel kept showing the OLD fit's
    chi/RMSE/table, and even once renderResults() was added it only
    reset #results-area and never touched #quantify-area, so THAT kept
    showing the OLD fit's area/RSF/At% table too)."""
    pg = _new_page(browser, server)
    try:
        _load_c1s_with_stale_narrow_fit(pg)
        before = _background_span(pg)
        assert before["max"] == pytest.approx(290.35625, abs=0.01)
        status_before = _status_bar_snapshot(pg)
        assert "278.0" in status_before["sbRoi"] and "290.4" in status_before["sbRoi"]
        assert "Run the fit" not in status_before["resultsArea"], (
            "sanity: the stale results panel must actually look populated "
            "before the fix is exercised")
        assert "Run fit to quantify" not in status_before["quantifyArea"], (
            "sanity: the stale quantify panel must actually look populated "
            "before the fix is exercised")

        _run_and_apply_find_peaks(pg, full_window=True)

        after = _background_span(pg)
        assert after["min"] == pytest.approx(278.0375, abs=0.01)
        assert after["max"] == pytest.approx(297.5, abs=0.5), (
            f"checked must extend the background/fit to the full ROI: {after}")
        assert after["max"] > before["max"] + 5, (
            "must be a REAL, visible extension, not a rounding artifact")

        peaks = pg.evaluate("() => state.peaks.length")
        assert peaks > 0, "peaks must actually have been applied"

        status_after = _status_bar_snapshot(pg)
        assert "290.4" not in status_after["sbRoi"], (
            f"stale ROI readout must be cleared, not left showing the "
            f"OLD fit's numbers: {status_after}")
        assert status_after["sbChi"] != status_before["sbChi"], (
            f"stale χ²ᵣ readout must be cleared too: {status_after}")
        assert status_after["fitQuality"] != status_before["fitQuality"], (
            f"stale fit-quality readout must be cleared too: {status_after}")
        assert status_after["sbRuns"] != status_before["sbRuns"], (
            f"stale R-factor readout must be cleared too: {status_after}")
        assert "Run the fit" in status_after["resultsArea"], (
            "stale Results panel (chi/RMSE/table from the OLD fit) must be "
            f"cleared back to its no-fit placeholder too: {status_after}")
        assert "Run fit to quantify" in status_after["quantifyArea"], (
            "stale Quantify panel (area/RSF/At% table from the OLD fit) "
            f"must be cleared back to its no-fit placeholder too: {status_after}")
    finally:
        pg.close()


def test_checkbox_on_from_a_fresh_tab_with_no_prior_fit_still_works(browser, server):
    """Sanity: the fix must not assume a prior state.fitResult exists —
    a fresh tab (the common case: Find Peaks is often the FIRST thing
    run on a tab) must also render peaks + background across the full
    ROI when checked, and must not error."""
    pg = _new_page(browser, server)
    try:
        pg.evaluate("""() => {
            const raw = [], inten = [];
            for (let i = 0; i <= 400; i++) {
                const be = 275.0 + i * 0.05625;
                raw.push(be);
                const g = (c, a, w) => a * Math.exp(-4 * Math.log(2) * ((be - c) / w) ** 2);
                inten.push(300 + g(284.5, 6000, 0.8));
            }
            tabManager.createTab('C1sFresh', raw, inten);
            document.getElementById('roi-min').value = 278.0;
            document.getElementById('roi-max').value = 298.0;
        }""")
        assert pg.evaluate("() => state.fitResult") is None

        _run_and_apply_find_peaks(pg, full_window=True)

        after = _background_span(pg)
        assert after["max"] == pytest.approx(297.5, abs=0.5)
        assert pg.evaluate("() => state.fitResult === null")
        assert pg.evaluate("() => state.peaks.length") > 0
    finally:
        pg.close()
