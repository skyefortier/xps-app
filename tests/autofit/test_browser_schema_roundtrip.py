"""
Stage-2 schema round-trip (spec v2.1 §1, Task #1 of Stage 2).

Proves, through the real browser save/load path, that:

  * the new whitelisted tab-level ``analysis`` namespace survives
    save → load → save on BOTH project formats (.proj.json < 5 tabs,
    .proj.zip >= 5 tabs), staying on manifest version 3;
  * per-peak ``_confidence`` rides the peak-spread channel (like
    ``_backendParams``) and round-trips bit-exact;
  * save → load → save produces identical per-tab documents (deep diff of
    every field — the "fail the build on any silent loss" gate);
  * pre-engine saves (no ``analysis`` key) still load clean.

Skips cleanly when Playwright/Chromium/gunicorn are absent (same convention
as the other test_browser_* files).
"""
import glob
import io
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import zipfile

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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


def _ctx(browser, server):
    ctx = browser.new_context(viewport={"width": 1500, "height": 950}, accept_downloads=True)
    pg = ctx.new_page()
    pg.goto(server + "/", wait_until="load")
    pg.wait_for_timeout(800)
    return ctx, pg


# Representative analysis payload — candidate set + ambiguity + criteria panel
# (spec §6 shape). Values are arbitrary but nested + typed like real output.
_ANALYSIS = {
    "engine_version": "stage2-test",
    "candidates": [
        {"name": "A1_linked", "bic_star": -1234.5, "aicc": -1230.1,
         "reduced_chi_sq": 1.42, "n_components": 3, "rank": 1},
        {"name": "B2_linked", "bic_star": -1233.0, "aicc": -1231.9,
         "reduced_chi_sq": 1.44, "n_components": 4, "rank": 2},
    ],
    "ambiguous_pairs": [["A1_linked", "B2_linked", "ΔBIC*=1.5 < τ"]],
    "criteria_panel": {"note": "not independent tests", "bic_ambiguous": True,
                       "criteria_conflict": False},
}

_CONFIDENCE = {
    "uncertainty_kind": "covariance",
    "sigma_stat": {"center": 0.012, "fwhm": 0.03, "amplitude": 145.2},
    "reference_sensitivity_range": [284.31, 285.15],
    "persistence": 0.95,
    "detectability": "above_floor",
}

# Build N spectrum tabs; attach analysis to tabs 0 and (N-1); give tab 0 a peak
# carrying _confidence. Tab 0 ends non-active (last created is active) so the
# non-active-record path is covered too.
_BUILD = """(args) => {
    const { n, analysis, confidence } = args;
    const mk = () => { const be=[], inten=[];
        for (let i=0;i<=100;i++){ be.push(280+i*0.15); inten.push(1000+800*Math.exp(-((280+i*0.15-287)**2)/0.8)); }
        return { be, inten }; };
    const ids = [];
    for (let i=0;i<n;i++){ const s=mk(); tabManager.createTab('RT'+i, s.be, s.inten);
        const t=tabManager._getTab(tabManager.activeId); state.ccShift=0; if(t)t.ccShift=0; ids.push(t.id); }
    const t0 = tabManager._getTab(ids[0]);
    t0.analysis = analysis;
    t0.peaks = [{
        id: 1, name: 'test peak', color: '#4a9eff', visible: true,
        center: 287.0, fwhm: 1.2, amplitude: 800, shape: 'GL', glMix: 30,
        asymmetry: 0, dsAlpha: 0.1, dsGamma: 0.01,
        laAlpha: 0.1, laBeta: 0.3, laM: 0.4, caAlpha: 1, caBeta: 1, caM: 50,
        linked: null, linkOffset: 10.9, linkRatio: 0.5,
        fixCenter: false, fixFwhm: false, fixAmplitude: false, fixGlMix: false,
        isChargeReference: false,
        _confidence: confidence,
    }];
    t0.nextId = 2;
    const tLast = tabManager._getTab(ids[n-1]);
    tLast.analysis = { engine_version: 'stage2-test', candidates: [], ambiguous_pairs: [],
                       criteria_panel: null };
    return { ids };
}"""


def _save_project(pg, tmp_path, label):
    with pg.expect_download() as dl:
        pg.evaluate("() => _doSaveProject()")
    fname = dl.value.suggested_filename
    out = str(tmp_path / f"{label}_{fname}")
    dl.value.save_as(out)
    return out


def _read_tab_docs(path):
    """{tab name: per-tab document} for either project format."""
    if path.endswith(".proj.zip"):
        with zipfile.ZipFile(path) as zf:
            manifest = json.loads(zf.read("manifest.json"))
            assert manifest["version"] == 3
            return {e["name"]: json.loads(zf.read(e["filename"])) for e in manifest["spectra"]}
    data = json.loads(open(path).read())
    assert data["version"] == 3
    return {t["name"]: t for t in data["tabs"]}


def _deep_diff(a, b, path=""):
    """Return list of 'path: a != b' strings for every differing leaf."""
    diffs = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                diffs.append(f"{path}.{k}: missing in first")
            elif k not in b:
                diffs.append(f"{path}.{k}: LOST in second save")
            else:
                diffs.extend(_deep_diff(a[k], b[k], f"{path}.{k}"))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            diffs.append(f"{path}: length {len(a)} != {len(b)}")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diffs.extend(_deep_diff(x, y, f"{path}[{i}]"))
    else:
        if a != b:
            diffs.append(f"{path}: {a!r} != {b!r}")
    return diffs


_IGNORED_TAB_FIELDS = {
    # assigned fresh on every load by design:
    "id", "color", "sourcePath",
}


def _normalize(doc):
    d = {k: v for k, v in doc.items() if k not in _IGNORED_TAB_FIELDS}
    return d


def _roundtrip(browser, server, tmp_path, n_tabs, expect_ext):
    ctx, pg = _ctx(browser, server)
    try:
        pg.evaluate(_BUILD, {"n": n_tabs, "analysis": _ANALYSIS, "confidence": _CONFIDENCE})
        pg.wait_for_timeout(150)
        save1 = _save_project(pg, tmp_path, "save1")
        assert save1.endswith(expect_ext), save1
        docs1 = _read_tab_docs(save1)

        # analysis + _confidence present in the first save
        assert docs1["RT0"]["analysis"] == _ANALYSIS
        assert docs1[f"RT{n_tabs-1}"]["analysis"]["engine_version"] == "stage2-test"
        assert "analysis" not in docs1["RT1"], "analysis key must be omitted when absent"
        assert docs1["RT0"]["peaks"][0]["_confidence"] == _CONFIDENCE

        # fresh page → load → assert in-memory restoration
        pg.goto(server + "/", wait_until="load")
        pg.wait_for_timeout(700)
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        pg.set_input_files("#load-session-input", save1)
        pg.wait_for_timeout(1200)

        restored = pg.evaluate("""() => {
            const out = {};
            for (const t of tabManager.tabs) if (!t.isStack)
                out[t.name] = { analysis: t.analysis ?? null,
                                conf: (t.peaks[0] && t.peaks[0]._confidence) || null };
            return out; }""")
        assert restored["RT0"]["analysis"] == _ANALYSIS
        assert restored["RT0"]["conf"] == _CONFIDENCE
        assert restored["RT1"]["analysis"] is None
        assert restored[f"RT{n_tabs-1}"]["analysis"]["engine_version"] == "stage2-test"
        assert [e for e in errs if "closest" not in e] == [], errs

        # save again → deep-diff every tab document field
        save2 = _save_project(pg, tmp_path, "save2")
        docs2 = _read_tab_docs(save2)
        assert sorted(docs1) == sorted(docs2)
        all_diffs = []
        for name in docs1:
            all_diffs += _deep_diff(_normalize(docs1[name]), _normalize(docs2[name]), name)
        assert all_diffs == [], "silent field loss/change across save→load→save:\n" + "\n".join(all_diffs)
    finally:
        ctx.close()


def test_roundtrip_zip_path(browser, server, tmp_path):
    _roundtrip(browser, server, tmp_path, n_tabs=5, expect_ext=".proj.zip")


def test_roundtrip_json_path(browser, server, tmp_path):
    _roundtrip(browser, server, tmp_path, n_tabs=3, expect_ext=".proj.json")


def test_pre_engine_save_loads_clean(browser, server, tmp_path):
    """A v3 save with NO analysis key anywhere loads with t.analysis == null."""
    manifest = {"version": 3, "timestamp": "2026-01-01T00:00:00Z", "sample_name": "old",
                "activeId": "tab_pre0", "spectra": []}
    files = {}
    for i in range(5):
        fn = f"spectrum_{i}_Pre{i}.json"
        files[fn] = json.dumps({
            "id": f"tab_pre{i}", "name": f"Pre{i}", "color": "#4a9eff", "isSurvey": False,
            "rawBE": [280 + j * 0.5 for j in range(60)], "rawIntensity": [1000] * 60,
            "ccShift": 0, "chargeVerified": True, "peaks": [], "nextId": 1, "fitResult": None,
            "notes": "", "manualAnchors": [], "lineWidth": 1.5,
            "ui": {"bgType": "shirley", "bgStart": "", "bgEnd": "", "shirleyIter": "5",
                   "roiMin": "", "roiMax": "", "ccMethod": "none", "ccObs": "", "ccLit": ""},
        })
        manifest["spectra"].append({"index": i, "filename": fn, "name": f"Pre{i}", "isSurvey": False})
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        for fn, content in files.items():
            zf.writestr(fn, content)
    zip_path = str(tmp_path / "pre_engine.proj.zip")
    with open(zip_path, "wb") as f:
        f.write(buf.getvalue())

    ctx, pg = _ctx(browser, server)
    try:
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        pg.set_input_files("#load-session-input", zip_path)
        pg.wait_for_timeout(1200)
        st = pg.evaluate("""() => ({
            names: tabManager.tabs.filter(t=>!t.isStack).map(t=>t.name),
            analyses: tabManager.tabs.filter(t=>!t.isStack).map(t=>t.analysis ?? null) })""")
        assert st["names"] == ["Pre0", "Pre1", "Pre2", "Pre3", "Pre4"]
        assert st["analyses"] == [None] * 5
        assert [e for e in errs if "closest" not in e] == [], errs
    finally:
        ctx.close()
