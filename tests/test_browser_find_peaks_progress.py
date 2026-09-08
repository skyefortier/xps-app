"""Browser contract for rendering analysis progress and clearing it.

Controlled transport responses exercise the real browser request/poll/UI
path. A genuine small engine run can finish within one poll interval, so
requiring a visible intermediate phase from it is not a valid UI test.
Engine progress emission and science are covered by separate API tests.
"""
import glob
import json
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
def server(tmp_path_factory):
    gunicorn = os.path.join(os.path.dirname(sys.executable), "gunicorn")
    if not os.path.exists(gunicorn):
        pytest.skip("gunicorn not found next to the test interpreter")
    port = _free_port()
    uploads = tmp_path_factory.mktemp("uploads")
    proc = subprocess.Popen(
        [gunicorn, "app:create_app(upload_folder=%r)" % str(uploads),
         "-w", "1", "-b", f"127.0.0.1:{port}", "--timeout", "60"],
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


def _load_cl2p_doublet(pg):
    """A real, small Cl 2p-like doublet — fast enough (n_refits=2) for a
    browser test, but with a genuine multi-candidate sweep to observe."""
    pg.evaluate("""() => {
        const rng_like = (seed) => { let s = seed; return () => {
            s = (s * 1103515245 + 12345) & 0x7fffffff; return s / 0x7fffffff; }; };
        const rnd = rng_like(7);
        const raw = [], inten = [];
        for (let i = 0; i <= 260; i++) {
            const be = 192.0 + i * 0.05;
            const g1 = 9000 * Math.exp(-4*Math.log(2)*((be-197.9)/1.65)**2);
            const g2 = 4950 * Math.exp(-4*Math.log(2)*((be-199.5)/1.65)**2);
            const noise = (rnd() - 0.5) * 40;
            raw.push(be); inten.push(300 + g1 + g2 + noise);
        }
        tabManager.createTab('Cl2p', raw, inten);
        const t = tabManager._getTab(tabManager.activeId);
        state.ccShift = 0; if (t) t.ccShift = 0;
        document.getElementById('roi-min').value = '192';
        document.getElementById('roi-max').value = '205';
    }""")


def _stub_progress(pg, error=None):
    control = {'finish': False, 'polls': 0}
    pg.route('**/api/analyze/start', lambda route: route.fulfill(
        status=202, content_type='application/json',
        body=json.dumps({'job_id': 'progress-contract'})))

    def progress(route):
        control['polls'] += 1
        if control['finish']:
            payload = ({'status': 'error', 'error': error} if error else {
                'status': 'done', 'result': {'success': True, 'peaks': [],
                    'diagnostics': {}, 'analysis': {}, 'confidence': {}},
            })
        else:
            payload = {'status': 'running', 'phase': 'stabilizing',
                'elapsed_sec': control['polls'] - 1,
                'message': 'candidate 1 of 4 — stabilizing'}
        route.fulfill(status=200, content_type='application/json',
                      body=json.dumps(payload))
    pg.route('**/api/analyze/progress/*', progress)
    return control


def test_progress_indicator_shows_spinner_timer_and_real_readout_then_clears(
        browser, server):
    pg = _new_page(browser, server)
    try:
        progress = _stub_progress(pg)
        _load_cl2p_doublet(pg)
        pg.evaluate("() => openFindPeaksModal()")
        pg.wait_for_selector("#find-peaks-overlay.open", timeout=5000)
        # region picker is the periodic-table grid (2026-07-13, unit 2 of
        # the "Find Peaks UI improvements round 2" session) — click the
        # element cell, then its "2p" level chip, instead of a <select>.
        pg.click("#fp-pt-grid >> text='Cl'")
        pg.click("#fp-expanded-panel >> text='[cited] 2p'")
        pg.select_option("#fp-method", "ic_model_comparison")
        # Exercise the actual options/request controls; numerical work is
        # intentionally outside this transport/UI contract.
        pg.evaluate("""() => {
            document.getElementById('fp-options').value =
                JSON.stringify({ n_refits: 2, enable_proposal_pass: false });
        }""")
        pg.click("#fp-run")

        # spinner visible + button disabled the instant the run starts
        pg.wait_for_function(
            "document.getElementById('fp-spinner').style.display === 'inline-block'",
            timeout=5000)
        assert pg.eval_on_selector("#fp-run", "el => el.disabled") is True

        # a REAL readout: elapsed ticks upward and the message names an
        # actual phase (never a static "please wait" placeholder)
        first = pg.eval_on_selector("#fp-status", "el => el.textContent")
        assert "Analyzing" in first
        pg.wait_for_function(
            """() => {
                const t = document.getElementById('fp-status').textContent;
                return /Analyzing… \\d/.test(t);
            }""", timeout=10000)
        seen_phase_word = False
        deadline = time.time() + 60
        last_elapsed = -1
        elapsed_ticked = False
        while time.time() < deadline:
            text = pg.eval_on_selector("#fp-status", "el => el.textContent")
            if "candidate" in text or "screening" in text or "stabilizing" in text:
                seen_phase_word = True
            m = None
            import re
            mm = re.search(r"Analyzing… (\d+)s", text)
            if mm:
                val = int(mm.group(1))
                if last_elapsed >= 0 and val > last_elapsed:
                    elapsed_ticked = True
                last_elapsed = val
            if not pg.eval_on_selector("#fp-run", "el => el.disabled"):
                break  # finished
            if seen_phase_word and elapsed_ticked:
                break
            pg.wait_for_timeout(300)

        assert seen_phase_word, "never saw a real candidate/phase readout"
        assert elapsed_ticked, "elapsed timer never ticked upward"

        # MUST clear on success — never spins forever
        progress['finish'] = True
        pg.wait_for_function(
            "document.getElementById('fp-spinner').style.display === 'none'",
            timeout=60000)
        assert pg.eval_on_selector("#fp-run", "el => el.disabled") is False
        assert pg.eval_on_selector("#fp-results", "el => el.style.display") == "block"
    finally:
        pg.close()


def test_progress_indicator_clears_on_error(browser, server):
    """An error received on the progress channel must clear the UI."""
    pg = _new_page(browser, server)
    try:
        progress = _stub_progress(pg, error='invalid option: n_refits')
        _load_cl2p_doublet(pg)
        pg.evaluate("() => openFindPeaksModal()")
        pg.wait_for_selector("#find-peaks-overlay.open", timeout=5000)
        # region picker is the periodic-table grid (2026-07-13, unit 2 of
        # the "Find Peaks UI improvements round 2" session) — click the
        # element cell, then its "2p" level chip, instead of a <select>.
        pg.click("#fp-pt-grid >> text='Cl'")
        pg.click("#fp-expanded-panel >> text='[cited] 2p'")
        pg.select_option("#fp-method", "ic_model_comparison")
        pg.evaluate("""() => {
            document.getElementById('fp-options').value =
                JSON.stringify({ n_refits: [] });
        }""")
        pg.click("#fp-run")
        pg.wait_for_function(
            "document.getElementById('fp-spinner').style.display === 'inline-block'",
            timeout=5000)
        progress['finish'] = True
        pg.wait_for_function(
            "document.getElementById('fp-spinner').style.display === 'none'",
            timeout=15000)
        assert pg.eval_on_selector("#fp-run", "el => el.disabled") is False
        status_text = pg.eval_on_selector("#fp-status", "el => el.textContent")
        assert "Failed" in status_text
        assert "invalid option" in status_text.lower()
    finally:
        pg.close()
