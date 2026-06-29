"""Real-browser coverage for the batch-fit ROI-propagation bug fix.

The bug: runPropagation() copied only the background fields into each target's
UI, omitting the ROI, so batch fit changed the background but left every target's
region of interest untouched. The fix routes the merge through the shipped
BatchPropagation.propagateFitUi helper, which now propagates the ROI too.

These tests cover what the node unit tests cannot:
  * the helper module is actually wired into the page (script tag loads);
  * the UI-state path the bug lived in — a tab's ui.roiMin/roiMax reach the
    #roi-min/#roi-max inputs on activation (which is where getROIData reads them);
  * end-to-end runPropagation propagates the source ROI onto the target tab.

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


def _new_page(browser, server):
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.goto(server + "/", wait_until="load")
    return pg


def test_batch_propagation_module_is_wired_into_the_page(browser, server):
    # Proves the new helper's <script> tag loads (the extraction's only new wiring).
    pg = _new_page(browser, server)
    try:
        kinds = pg.evaluate("""() => ({
            mod: typeof window.BatchPropagation,
            fn: typeof (window.BatchPropagation && window.BatchPropagation.propagateFitUi) })""")
        assert kinds["mod"] == "object"
        assert kinds["fn"] == "function"
    finally:
        pg.close()


def test_tab_ui_roi_reaches_the_roi_inputs_on_activation(browser, server):
    # The UI-state path the bug lived in: once a tab's ui carries roiMin/roiMax
    # (which the fix now ensures for targets), activating it populates the
    # #roi-min/#roi-max inputs — where getROIData reads the fit window.
    pg = _new_page(browser, server)
    try:
        vals = pg.evaluate("""() => {
            const be=[], inten=[];
            for(let i=0;i<40;i++){ const x=520+i*0.5; be.push(x); inten.push(1000); }
            tabManager.createTab('A', be, inten);
            const aId = tabManager.activeId;
            tabManager.createTab('B', be, inten);     // switch away so a later activate is a REAL switch
            const a = tabManager._getTab(aId);
            a.ui.roiMin = '525'; a.ui.roiMax = '545';
            tabManager.activateTab(aId);              // genuine activation → _restoreUI populates the inputs
            return { min: document.getElementById('roi-min').value,
                     max: document.getElementById('roi-max').value };
        }""")
        assert vals["min"] == "525"
        assert vals["max"] == "545"
    finally:
        pg.close()


def test_runpropagation_propagates_source_roi_onto_target(browser, server):
    # End-to-end: a source spectrum with ROI 525–545 batch-fit onto a target whose
    # own ROI is 100–160 must leave the target with the SOURCE's ROI (the fix).
    pg = _new_page(browser, server)
    try:
        ids = pg.evaluate("""() => {
            const mk = (amp) => { const be=[], inten=[];
                for(let i=0;i<60;i++){ const x=520+i*0.5; be.push(x);
                    inten.push(1000 + amp*Math.exp(-Math.pow(x-530,2)/(2*1.5*1.5))); }
                return { be, inten }; };
            // SOURCE: ROI 525/545 + a peak at 530
            const s = mk(8000);
            tabManager.createTab('SRC', s.be, s.inten);
            const srcId = tabManager.activeId;
            document.getElementById('roi-min').value = '525';
            document.getElementById('roi-max').value = '545';
            addPeak({ center: 530, fwhm: 2, amplitude: 8000 });
            // TARGET: a DIFFERENT ROI 100/160
            const t = mk(7000);
            tabManager.createTab('TGT', t.be, t.inten);   // switches away from SRC (captures SRC ui)
            const tgtId = tabManager.activeId;
            document.getElementById('roi-min').value = '100';
            document.getElementById('roi-max').value = '160';
            tabManager.activateTab(srcId);                 // back to SRC (captures TGT ui=100/160)
            return { srcId, tgtId };
        }""")
        tgt_id = ids["tgtId"]
        # Open the propagate modal (source is active + has a peak) and run it.
        pg.evaluate("() => showPropagateModal()")
        pg.wait_for_timeout(100)
        # Only the target should be checkable; ensure its checkbox is checked, then run.
        pg.evaluate("""(tgtId) => {
            const chk = document.querySelector('.prop-chk[data-id="' + tgtId + '"]');
            if (chk) chk.checked = true;
        }""", tgt_id)
        # runPropagation is async (clones peaks, sets tgt.ui, activates, fits).
        pg.evaluate("() => runPropagation()")
        # Wait for it to finish (target tab's ui is set BEFORE the fit, so this is
        # robust regardless of fit outcome).
        pg.wait_for_function(
            """(tgtId) => { const t = tabManager._getTab(tgtId);
                 return t && t.ui && t.ui.roiMin === '525'; }""",
            arg=tgt_id, timeout=10000)
        # The propagated ROI is on the target record…
        rec = pg.evaluate("""(tgtId) => { const t = tabManager._getTab(tgtId);
            return { roiMin: t.ui.roiMin, roiMax: t.ui.roiMax }; }""", tgt_id)
        assert rec["roiMin"] == "525"
        assert rec["roiMax"] == "545"
        # …and reaches the #roi-min/#roi-max inputs when the target is activated.
        dom = pg.evaluate("""(tgtId) => { tabManager.activateTab(tgtId);
            return { min: document.getElementById('roi-min').value,
                     max: document.getElementById('roi-max').value }; }""", tgt_id)
        assert dom["min"] == "525"
        assert dom["max"] == "545"
    finally:
        pg.close()


def test_missing_module_fails_loudly_without_half_running(browser, server):
    # If batch_propagation.js fails to load, runPropagation must fail LOUDLY and
    # return BEFORE mutating any state (no half-run, no suppressed snapshots, no
    # propagation onto the target).
    pg = _new_page(browser, server)
    try:
        tgt_id = pg.evaluate("""() => {
            const be=[], inten=[];
            for(let i=0;i<40;i++){ const x=520+i*0.5; be.push(x); inten.push(1000); }
            tabManager.createTab('SRC', be, inten);
            const srcId = tabManager.activeId;
            document.getElementById('roi-min').value = '525';
            document.getElementById('roi-max').value = '545';
            addPeak({ center: 530, fwhm: 2, amplitude: 8000 });
            tabManager.createTab('TGT', be, inten);
            const tgtId = tabManager.activeId;
            document.getElementById('roi-min').value = '100';
            document.getElementById('roi-max').value = '160';
            tabManager.activateTab(srcId);
            return tgtId;
        }""")
        # Simulate the module failing to load.
        pg.evaluate("() => { delete window.BatchPropagation; }")
        pg.evaluate("() => showPropagateModal()")
        pg.wait_for_timeout(80)
        pg.evaluate("""(tgtId) => { const c=document.querySelector('.prop-chk[data-id=\"' + tgtId + '\"]'); if (c) c.checked = true; }""", tgt_id)
        res = pg.evaluate("""async (tgtId) => {
            let threw = false;
            try { await runPropagation(); } catch (e) { threw = true; }
            const t = tabManager._getTab(tgtId);
            return {
                threw,
                snapshotSuppressed: _snapshotSuppressed,
                toastShown: document.getElementById('prominent-toast').classList.contains('show'),
                toastText: document.getElementById('prominent-toast-inner').textContent,
                tgtRoiMin: t.ui.roiMin,
            };
        }""", tgt_id)
        assert res["threw"] is False                       # no raw TypeError escapes
        assert res["snapshotSuppressed"] is False          # guard returned before suppressing snapshots
        assert res["toastShown"] is True                   # LOUD error surfaced
        assert "failed to load" in res["toastText"]
        assert res["tgtRoiMin"] == "100"                   # target ROI NOT propagated (no half-run)
    finally:
        pg.close()
