"""B3: .proj.zip parity for reference-overlay save/load.

The ≥5-tab project save produces a .proj.zip (manifest.json + one JSON per
spectrum). B3 has NO new wiring — the zip path already reuses the shared code:
  * SAVE: the manifest is `{ ...meta }` (so it carries B2's project-meta
    refCompoundMarkers) and each per-spectrum JSON is `buildTabData(t)` (so it
    carries B2's per-tab refOverlays);
  * LOAD: _loadZipProject reassembles `{ ...manifest, tabs }` and calls the same
    _loadProjectJSON used by .proj.json — including the B2 ephemeral-id
    rehydration of restored compound markers.

This test proves that round-trip end to end (the file format in the flesh):
  * overlays restored on the CORRECT tabs with deterministic colors + legend;
  * the global compound marker restored ONCE and removable after reload, with
    the two-marker correct-target removal check;
  * an OLD .proj.zip (no overlay/marker fields) loads clean, no console error;
  * a new pick after a .zip reload renders a color distinct from all restored.

Skips cleanly when Playwright/Chromium are absent.
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


def _ctx(browser, server):
    ctx = browser.new_context(viewport={"width": 1500, "height": 950}, accept_downloads=True)
    pg = ctx.new_page()
    pg.goto(server + "/", wait_until="load")
    pg.wait_for_timeout(1000)
    return ctx, pg


# Build 5 spectrum tabs; put overlays (distinct tiers) on three of them; place
# the requested compound markers. Returns the JS-side snapshot of expectations.
_BUILD = """(markerCount) => {
    const mk = () => { const be=[], inten=[];
        for(let i=0;i<=120;i++){ be.push(200+i*5); inten.push(1000); } return { be, inten }; };
    const ids = [];
    for (let i=0;i<5;i++){ const s=mk(); tabManager.createTab('T'+i, s.be, s.inten);
        const t=tabManager._getTab(tabManager.activeId); state.ccShift=0; if(t)t.ccShift=0; ids.push(t.id); }
    // overlays on T0 (Cu=curated), T2 (Ta=machine), T4 (F=legacy); T1/T3 none
    const put = (tabId, sym) => { tabManager.activateTab(tabId); _refToggleElement(sym); };
    put(ids[0], 'Cu'); put(ids[2], 'Ta'); put(ids[4], 'F');
    // global compound markers
    _refAddCompoundMarker('Cu', 'Cu2O', 932.5, 'r1');
    if (markerCount >= 2) _refAddCompoundMarker('Fe', 'Fe2O3', 710.8, 'r2');
    return { ids };
}"""


def _overlays_by_tabname(pg):
    return pg.evaluate("""() => {
        const out = {};
        for (const t of tabManager.tabs) {
            if (t.isStack) continue;
            const syms = (t._refSel && t._refSel.syms) || [];
            out[t.name] = syms.map(s => ({ sym: s.sym, colorIdx: s.colorIdx,
                color: ELEMENT_MARKER_COLORS[s.colorIdx % ELEMENT_MARKER_COLORS.length] }));
        }
        return out;
    }""")


def _markers(pg):
    return pg.evaluate("() => _refCompoundMarkers.map(m => ({ id: m.id, sym: m.sym, state: m.state, be: m.be }))")


def test_zip_roundtrip_overlays_on_correct_tabs_and_markers(browser, server):
    ctx, pg = _ctx(browser, server)
    try:
        pg.click("#btn-ref-panel")
        pg.wait_for_function("window._refPayload && window._refPayload.machine", timeout=15000)
        pg.evaluate(_BUILD, 2)   # 2 compound markers for the correct-removal check
        pg.wait_for_timeout(200)
        before = _overlays_by_tabname(pg)
        before_markers = _markers(pg)
        assert sorted(before.keys()) == ["T0", "T1", "T2", "T3", "T4"]      # 5 tabs → zip path
        assert [m["sym"] for m in before_markers] == ["Cu", "Fe"]

        # SAVE → must be a .proj.zip (≥5 tabs); intercept the download.
        with pg.expect_download() as dl:
            pg.evaluate("() => _doSaveProject()")
        zip_path = "/tmp/b3_roundtrip.proj.zip"
        dl.value.save_as(zip_path)
        assert zip_path.endswith(".proj.zip") and dl.value.suggested_filename.endswith(".proj.zip")

        # Inspect the archive: per-spectrum refOverlays + manifest refCompoundMarkers, NO ids.
        with zipfile.ZipFile(zip_path) as zf:
            manifest = json.loads(zf.read("manifest.json"))
            assert manifest["version"] == 3
            assert "refCompoundMarkers" in manifest                          # global, in the manifest
            assert all("id" not in m for m in manifest["refCompoundMarkers"]["markers"])  # ids never persisted
            spec_overlays = {}
            for ent in manifest["spectra"]:
                doc = json.loads(zf.read(ent["filename"]))
                if doc.get("refOverlays"):
                    spec_overlays[doc["name"]] = [s["sym"] for s in doc["refOverlays"]["syms"]]
            assert spec_overlays == {"T0": ["Cu"], "T2": ["Ta"], "T4": ["F"]}  # per-tab, correct tabs

        # RELOAD fresh, then load the .proj.zip.
        pg.goto(server + "/", wait_until="load"); pg.wait_for_timeout(900)
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        pg.set_input_files("#load-session-input", zip_path)
        pg.wait_for_function("() => window._refPayload && window._refPayload.machine", timeout=15000)
        pg.wait_for_timeout(800)

        after = _overlays_by_tabname(pg)
        # overlays restored on the CORRECT tabs with deterministic colors
        assert after == before, (before, after)
        # compound markers restored once globally, with fresh unique ids
        rl_markers = _markers(pg)
        assert [m["sym"] for m in rl_markers] == ["Cu", "Fe"]
        assert rl_markers[0]["id"] is not None and rl_markers[1]["id"] is not None
        assert rl_markers[0]["id"] != rl_markers[1]["id"]
        # legend shows the active tab's overlay (active tab is the saved active = T4/F)
        legend = pg.evaluate("() => [...document.querySelectorAll('#ref-chart-legend .ref-legend-chip')].map(c=>c.dataset.sym)")
        active_name = pg.evaluate("() => _refActiveTab().name")
        assert legend == [s["sym"] for s in after[active_name]]

        # two-marker CORRECT removal after reload: remove Fe → only Cu remains
        fe_id = [m for m in rl_markers if m["sym"] == "Fe"][0]["id"]
        pg.evaluate("(id) => _refRemoveCompoundMarker(id)", fe_id)
        pg.wait_for_timeout(120)
        after_rm = _markers(pg)
        assert [m["sym"] for m in after_rm] == ["Cu"]                        # correct one removed
        # single remaining marker removes cleanly
        pg.evaluate("(id) => _refRemoveCompoundMarker(id)", after_rm[0]["id"])
        pg.wait_for_timeout(120)
        assert _markers(pg) == []

        # new pick after a .zip reload → distinct RENDERED color vs all restored
        np = pg.evaluate("""() => {
            const used = new Set();
            for (const t of tabManager.tabs) { if (t.isStack) continue;
                for (const s of (t._refSel && t._refSel.syms) || [])
                    used.add(ELEMENT_MARKER_COLORS[s.colorIdx % ELEMENT_MARKER_COLORS.length]); }
            const cur = _refGetSel();
            const fresh = ['Nb','O','Sc','Cl','U','Ru'].find(s => !cur.syms.some(x=>x.sym===s) && _refActivation(s));
            _refToggleElement(fresh);
            const picked = cur.syms.find(s=>s.sym===fresh);
            const color = ELEMENT_MARKER_COLORS[picked.colorIdx % ELEMENT_MARKER_COLORS.length];
            return { fresh, color, collides: used.has(color) }; }""")
        assert np["collides"] is False, np

        assert [e for e in errs if "closest" not in e] == []                # no load-caused console error
    finally:
        ctx.close()


def _build_old_zip(path):
    """An OLD .proj.zip: version-3 manifest + per-spectrum JSON with NO overlay/
    marker fields (the pre-B2 shape)."""
    manifest = {"version": 3, "timestamp": "2026-01-01T00:00:00Z", "sample_name": "old",
                "activeId": "tab_oldz0", "spectra": []}
    files = {}
    for i in range(5):
        fn = f"spectrum_{i}_Told{i}.json"
        files[fn] = json.dumps({
            "id": f"tab_oldz{i}", "name": f"Told{i}", "color": "#4a9eff", "isSurvey": False,
            "rawBE": [200 + j * 5 for j in range(40)], "rawIntensity": [1000] * 40,
            "ccShift": 0, "chargeVerified": True, "peaks": [], "nextId": 1, "fitResult": None,
            "notes": "", "manualAnchors": [], "lineWidth": 1.5,
            "ui": {"bgType": "shirley", "bgStart": "", "bgEnd": "", "shirleyIter": "5",
                   "roiMin": "", "roiMax": "", "ccMethod": "none", "ccObs": "", "ccLit": ""},
        })
        manifest["spectra"].append({"index": i, "filename": fn, "name": f"Told{i}", "isSurvey": False})
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest))
        for fn, content in files.items():
            zf.writestr(fn, content)
    with open(path, "wb") as f:
        f.write(buf.getvalue())


def test_old_zip_without_overlay_fields_loads_clean(browser, server):
    ctx, pg = _ctx(browser, server)
    try:
        zip_path = "/tmp/b3_old.proj.zip"
        _build_old_zip(zip_path)
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR: " + str(e)))
        pg.set_input_files("#load-session-input", zip_path)
        pg.wait_for_timeout(1500)
        st = pg.evaluate("""() => ({
            tabs: tabManager.tabs.filter(t=>!t.isStack).map(t=>t.name),
            anyOverlays: tabManager.tabs.some(t=>!t.isStack && t._refSel && t._refSel.syms.length),
            markers: _refCompoundMarkers.length,
            legend: !!document.getElementById('ref-chart-legend') })""")
        assert st["tabs"] == ["Told0", "Told1", "Told2", "Told3", "Told4"]   # loaded
        assert st["anyOverlays"] is False                                   # no overlays
        assert st["markers"] == 0                                           # no markers
        assert st["legend"] is False                                       # no legend
        assert [e for e in errs if "closest" not in e] == []               # no load-caused console error
    finally:
        ctx.close()
