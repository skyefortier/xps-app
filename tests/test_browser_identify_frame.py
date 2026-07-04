"""Real-browser tests for reference-line frame coincidence, identify-mode, and
the identify toggle-off fix (bug 2).

Governing invariant: the displayed spectrum, the reference lines, and the
identify click all live in ONE frame (corrected/true BE). The spectrum series
is charge-corrected (peaks at true BE); reference lines draw at literature /
source-projected BE with NO ccShift; the identify click is read in the same
corrected frame and matched against literature with no extra shift.

Skips cleanly when Playwright or a cached Chromium build is unavailable.
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
def page(server):
    exe = _find_chromium()
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception:
            if not exe:
                pytest.skip("no usable Chromium build found")
            browser = p.chromium.launch(headless=True, executable_path=exe)
        pg = browser.new_page(viewport={"width": 1500, "height": 950})
        pg.goto(server + "/", wait_until="load")
        pg.click("#btn-ref-panel")
        pg.wait_for_function("window._refPayload && window._refPayload.elements", timeout=10000)
        yield pg
        browser.close()


# A synthetic U spectrum: raw 4f7/2 at 380.0, 4f5/2 at 390.8. With ccShift=cc,
# corrected 4f7/2 = 380 - cc. cc=2.7 -> 377.3 (literature). U overlay selected.
def setup_u(page, cc=2.7):
    page.evaluate(
        """(cc) => {
            const N=451, raw=[], inten=[];
            const g=(be,c,a,w)=>a*Math.exp(-Math.pow(be-c,2)/(2*w*w));
            for(let i=0;i<N;i++){ const be=370+i*0.1; raw.push(be);
                inten.push(500 + g(be,380.0,10000,1.1) + g(be,390.8,7000,1.1)); }
            tabManager.createTab('U test', raw, inten);
            const t=tabManager._getTab(tabManager.activeId);
            state.ccShift=cc; if(t)t.ccShift=cc;
            if(typeof _refClearIdentify==='function') _refClearIdentify();
            if(placeMode) togglePlaceMode(placeMode);
            const sel=_refGetSel(); sel.syms=[]; sel.source='AlKa';
            _refToggleElement('U');
            // A6: identify works with the palette CLOSED — close it so the
            // real-clicked peak (which can sit under the floating palette)
            // reaches the chart. Overlays persist regardless (A1).
            if(_refPanelOpen) toggleRefPanel();
            updatePlot();
        }""", cc)
    page.wait_for_timeout(150)


def _peak_client_xy(page, corrected_be):
    return page.evaluate(
        """(be) => {
            const sx=state.chart.scales.x, sy=state.chart.scales.y;
            const rect=state.chart.canvas.getBoundingClientRect();
            return { x: rect.left + sx.getPixelForValue(be), y: rect.top + (sy.top+sy.bottom)/2 };
        }""", corrected_be)


def test_u_4f72_reference_coincides_with_corrected_peak(page):
    setup_u(page, 2.7)
    r = page.evaluate("""() => {
        const items=_refChartItems(state.chart)||[];
        const ref=items.find(m=>m.sym==='U' && m.t.orbital==='4f7/2');
        const ds=state.chart.data.datasets.find(d=>d.label==='Data');
        let pk=null; for(const p of ds.data){ if(!pk||p.y>pk.y) pk=p; }
        return { refBe: ref && ref.be, peakX: pk && +pk.x.toFixed(3) };
    }""")
    assert abs(r["refBe"] - 377.30) < 0.01            # reference at literature BE
    assert abs(r["peakX"] - 377.30) < 0.05            # corrected peak at same BE
    assert abs(r["refBe"] - r["peakX"]) < 0.05        # they coincide


def test_identify_returns_u_4f72_on_charge_corrected_spectrum(page):
    setup_u(page, 2.7)
    # Arm via the real button, real-click the corrected peak.
    page.click("#ref-identify-btn")
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])
    page.wait_for_timeout(200)
    r = page.evaluate("""() => {
        const tab=_refActiveTab(); const id=tab&&tab._refIdentify;
        return id ? { top:id.cands[0]&&id.cands[0].label, n:id.cands.length } : null;
    }""")
    assert r is not None
    assert r["top"] == "U 4f7/2"
    assert r["n"] >= 1


def test_identify_toggle_off_clears_state_and_restores_selection(page):
    setup_u(page, 2.7)
    page.click("#ref-identify-btn")                    # arm
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])                 # produce identify state + highlight
    page.wait_for_timeout(150)
    assert page.evaluate("() => !!(_refActiveTab() && _refActiveTab()._refIdentify)") is True
    # Re-click the Identify control -> toggle OFF
    page.click("#ref-identify-btn")
    page.wait_for_timeout(150)
    state = page.evaluate("""() => ({
        placeMode: placeMode,
        identify: !!(_refActiveTab() && _refActiveTab()._refIdentify)
    })""")
    assert state["placeMode"] is None                  # mode exited
    assert state["identify"] is False                  # state + highlight cleared
    # A subsequent chart click does NOT re-arm identify (normal click restored).
    page.mouse.click(xy["x"], xy["y"])
    page.wait_for_timeout(100)
    assert page.evaluate("() => !!(_refActiveTab() && _refActiveTab()._refIdentify)") is False


def test_identify_esc_clears_state(page):
    setup_u(page, 2.7)
    page.click("#ref-identify-btn")
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])
    page.wait_for_timeout(150)
    assert page.evaluate("() => !!(_refActiveTab() && _refActiveTab()._refIdentify)") is True
    page.keyboard.press("Escape")
    page.wait_for_timeout(150)
    state = page.evaluate("""() => ({
        placeMode: placeMode,
        identify: !!(_refActiveTab() && _refActiveTab()._refIdentify)
    })""")
    assert state["placeMode"] is None
    assert state["identify"] is False


def test_identify_popover_survives_theme_switch(page):
    # Regression (dark-mode identify bug): toggling the theme while the identify
    # popover is open must NOT tear it down and strand identify in an armed-but-
    # empty state. The theme toggle is chrome, exempt from outside-dismiss; the
    # popover stays open, re-themes live, and identify state stays consistent.
    setup_u(page, 2.7)
    page.click("#ref-identify-btn")                       # arm from toolbar
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])                    # popover opens
    page.wait_for_timeout(150)
    before = page.evaluate("""() => ({
        popover: !!document.getElementById('ref-identify-popover'),
        identify: !!(_refActiveTab() && _refActiveTab()._refIdentify),
        light: document.body.classList.contains('light-theme'),
        bg: getComputedStyle(document.getElementById('ref-identify-popover')).backgroundColor })""")
    assert before["popover"] is True and before["identify"] is True
    try:
        page.click("#theme-toggle")                       # toggle theme with popover OPEN
        page.wait_for_timeout(300)
        after = page.evaluate("""() => ({
            popover: !!document.getElementById('ref-identify-popover'),
            identify: !!(_refActiveTab() && _refActiveTab()._refIdentify),
            armed: placeMode === 'identify',
            light: document.body.classList.contains('light-theme'),
            bg: (()=>{const p=document.getElementById('ref-identify-popover');return p?getComputedStyle(p).backgroundColor:null;})() })""")
        # popover preserved + identify still consistent (open, armed) across the switch
        assert after["popover"] is True and after["identify"] is True and after["armed"] is True
        assert after["light"] != before["light"]          # theme actually changed
        assert after["bg"] != before["bg"]                # popover re-themed live
        # a GENUINE outside click still dismisses (dismiss-elsewhere preserved)
        page.mouse.click(120, 400)
        page.wait_for_timeout(150)
        assert page.evaluate("() => !!document.getElementById('ref-identify-popover')") is False
    finally:
        # restore dark theme + clear identify so the shared page stays clean
        page.evaluate("""() => { if (document.body.classList.contains('light-theme')) toggleTheme();
                                 if (typeof _refClearIdentify === 'function') _refClearIdentify();
                                 if (placeMode === 'identify') togglePlaceMode('identify'); }""")
        page.wait_for_timeout(100)


def test_u_shallow_lines_out_of_window(page):
    # Step 4: in the U 4f window (~367-412 eV) the shallow/deep lines sit OUTSIDE
    # the displayed range. Correct out-of-window behavior, not filtering.
    setup_u(page, 2.7)
    rows = page.evaluate("""() => {
        const sel=_refGetSel(); sel.showWeak=true;
        const sx=state.chart.scales.x, lo=sx.min, hi=sx.max;
        const o={};
        for(const m of _refTransitionsFor('U')) o[m.t.orbital] = (m.be>=lo && m.be<=hi);
        return o;
    }""")
    assert rows["4f7/2"] is True
    assert rows["4f5/2"] is True
    for orb in ["5d5/2", "5d3/2", "5p3/2", "6p3/2", "6p1/2", "6s", "4d5/2", "4s"]:
        assert rows[orb] is False                      # off-screen, correctly not drawn


def test_zero_ccshift_reference_positions_unchanged(page):
    # Regression: reference positions are source/charge invariant. ccShift=0
    # leaves U 4f7/2 at 377.30 and curated Cu 2p3/2 at 932.67 (no shift ever).
    setup_u(page, 0.0)
    r = page.evaluate("""() => {
        const u = _refTransitionsFor('U').find(m=>m.t.orbital==='4f7/2');
        const sel=_refGetSel(); sel.syms=[]; _refToggleElement('Cu');
        const cu = _refTransitionsFor('Cu').find(m=>m.t.orbital==='2p3/2');
        return { u: u.be, cu: cu.be };
    }""")
    assert abs(r["u"] - 377.30) < 0.01
    assert abs(r["cu"] - 932.67) < 0.01


# ── Legacy identify-coverage (candidate pool = full activatable set) ──────────

def setup_spectrum(page, lo, hi, source="AlKa", include_auger=False):
    """A flat spectrum spanning [lo, hi]; identify scans references, not the
    spectrum, so the content is irrelevant — the window/tab/source are what matter."""
    page.evaluate(
        """([lo,hi,src,auger]) => {
            const N=Math.max(60, Math.round((hi-lo)/0.2)), raw=[], inten=[];
            for(let i=0;i<N;i++){ raw.push(lo + i*(hi-lo)/(N-1)); inten.push(1000); }
            tabManager.createTab('probe', raw, inten);
            const t=tabManager._getTab(tabManager.activeId); state.ccShift=0; if(t)t.ccShift=0;
            if(typeof _refClearIdentify==='function') _refClearIdentify();
            if(placeMode) togglePlaceMode(placeMode);
            const sel=_refGetSel(); sel.syms=[]; sel.source=src; sel.includeAuger=!!auger; sel.tolMode='normal';
            updatePlot();
        }""", [lo, hi, source, include_auger])
    page.wait_for_timeout(120)


def identify(page, be):
    return page.evaluate(
        """(be) => {
            _refIdentifyAt(be);
            const tab=_refActiveTab(); const id=tab&&tab._refIdentify;
            return id ? id.cands.map(c=>({label:c.label, tier:c.dataTier,
                dist:+c.dist.toFixed(3), isAuger:c.isAuger,
                hasRegion:c.hasRegion, inRegion:c.inRegion})) : [];
        }""", be)


def test_machine_tier_precedence_and_count(page):
    # Activation resolves by precedence curated > machine > legacy.
    setup_spectrum(page, 360, 380)
    r = page.evaluate("""() => {
        const t={curated:0,machine:0,legacy:0,unavailable:0};
        for(const e of REF_PT_LAYOUT){const a=_refActivation(e.sym);
            if(a==='curated')t.curated++;else if(a==='machine')t.machine++;else if(a==='legacy')t.legacy++;else t.unavailable++;}
        return {tally:t,
            C:_refActivation('C'), O:_refActivation('O'), U:_refActivation('U'),
            Si:_refActivation('Si'), Ag:_refActivation('Ag'), Pt:_refActivation('Pt'),
            Fe:_refActivation('Fe'), V:_refActivation('V'), He:_refActivation('He'),
            Ta:_refActivation('Ta'), Sc:_refActivation('Sc'), Rb:_refActivation('Rb')};
    }""")
    # Machine-tier tally after the full-table coverage sweep (2026-07-03):
    # elements-machine.json now holds 51 elements (was 37; new incl. Rh, Pr,
    # Mg + the lanthanide 4d family), but Cu and Nb also carry curated
    # records and resolve 'curated' by precedence -> 49 tally as machine.
    assert r["tally"]["machine"] == 49
    assert r["tally"]["curated"] == 6
    assert r["C"] == "curated" and r["O"] == "curated" and r["U"] == "curated"
    assert r["Si"] == "machine" and r["Ag"] == "machine" and r["Pt"] == "machine"
    assert r["Fe"] == "machine"                         # promoted via conflict-resolution
    assert r["Ta"] == "machine" and r["Sc"] == "machine"   # coverage-expansion (newly clickable)
    assert r["V"] == "legacy"                           # V stays legacy (no NIST-evaluated value)
    assert r["Rb"] is None                              # FAILED acquisition → stays unavailable
    assert r["He"] is None


def test_per_subshell_merge_and_no_duplicate_orbitals(page):
    setup_spectrum(page, 90, 540)
    r = page.evaluate("""() => {
        const lines = sym => _refTransitionsFor(sym).map(m => [m.t.orbital, m.tier]);
        // every activated element: no duplicate orbital after the merge
        let dup = null;
        for (const e of REF_PT_LAYOUT) {
            if (!_refActivation(e.sym)) continue;
            const orbs = _refTransitionsFor(e.sym).map(m => m.t.orbital);
            if (orbs.length !== new Set(orbs).size) { dup = e.sym; break; }
        }
        return { Si: lines('Si'), Cl: lines('Cl'), dup };
    }""")
    assert r["dup"] is None, f"duplicate orbital after merge for {r['dup']}"
    # Si: machine 2p3/2 supersedes legacy bare 2p (same subshell); legacy 2s kept.
    assert sorted(r["Si"]) == [["2p3/2", "machine"], ["2s", "legacy"]], r["Si"]
    # Cl is curated -> legacy fully suppressed (no legacy 2s leaks onto a curated element).
    assert sorted(r["Cl"]) == [["2p1/2", "curated"], ["2p3/2", "curated"]], r["Cl"]


def test_machine_identifies_via_region_legacy_via_proximity(page):
    # Ag 3d5/2 (machine, region 367.9-368.4) matches via REGION scoring; a legacy
    # line (V 2p, region=null) matches via proximity. (Fe is no longer legacy — it
    # was promoted to machine via conflict-resolution; V stays legacy.)
    setup_spectrum(page, 360, 380)
    ag = identify(page, 368.27)
    hit = [c for c in ag if c["label"] == "Ag 3d5/2"]
    assert hit, [c["label"] for c in ag]
    assert hit[0]["tier"] == "machine"
    assert hit[0]["hasRegion"] is True and hit[0]["inRegion"] is True   # region scoring

    setup_spectrum(page, 500, 530)
    v = identify(page, 517.0)
    vhit = [c for c in v if c["label"] == "V 2p"]
    assert vhit and vhit[0]["tier"] == "legacy"
    assert vhit[0]["hasRegion"] is False               # proximity fallback (no region)


def test_legacy_v_2p_returns_candidate_at_517(page):
    setup_spectrum(page, 500, 530)
    cands = identify(page, 517.0)
    v = [c for c in cands if c["label"] == "V 2p"]
    assert v, f"expected V 2p, got {[c['label'] for c in cands]}"
    assert v[0]["tier"] == "legacy"           # legacy-unverified
    assert v[0]["dist"] <= 0.01               # Δ ~0, shown


def test_legacy_v_absent_when_far_off(page):
    setup_spectrum(page, 500, 530)
    cands = identify(page, 523.0)             # 517 + 6 > 3.0 proximity window
    assert not any(c["label"] == "V 2p" for c in cands)


def test_curated_u_outranks_nearby_legacy(page):
    setup_spectrum(page, 370, 415)
    cands = identify(page, 377.3)
    assert cands and cands[0]["label"] == "U 4f7/2"
    assert cands[0]["tier"] == "curated"
    # K 2s (legacy, 378.0) is within the proximity window but ranks below U.
    k = [(i, c) for i, c in enumerate(cands) if c["label"] == "K 2s"]
    if k:
        idx, kc = k[0]
        assert kc["tier"] == "legacy" and idx > 0


def test_curated_outranks_legacy_on_near_tie(page):
    # Equidistant between U 4f7/2 (377.3, curated) and K 2s (378.0, legacy):
    # Δ within 0.5 eV -> tier priority -> curated wins.
    setup_spectrum(page, 370, 415)
    cands = identify(page, 377.65)
    assert cands[0]["label"] == "U 4f7/2" and cands[0]["tier"] == "curated"


def test_mgka_legacy_na_kll_and_curated_cu_lmm_project(page):
    setup_spectrum(page, 200, 400, source="MgKa", include_auger=True)
    na = identify(page, 264.0)               # Na KLL projected onto Mg Kα
    assert any(c["label"] == "Na KLL" and c["tier"] == "legacy" and c["isAuger"] for c in na), na
    cu = identify(page, 330.48)              # Cu LMM projected onto Mg Kα
    assert any(c["label"].startswith("Cu L") and c["tier"] == "curated" and c["isAuger"] for c in cu), cu


def test_region_null_identify_never_throws(page):
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    setup_spectrum(page, 500, 530)
    identify(page, 517.0)                     # legacy V 2p, region=null
    identify(page, 516.4)
    region_errs = [e for e in errs if "min" in e or "region" in e or "Cannot read" in e]
    assert not region_errs, region_errs


def test_legacy_candidate_card_shows_tier_and_delta(page):
    setup_spectrum(page, 500, 530)
    page.evaluate("() => _refIdentifyAt(517.0)")
    page.wait_for_timeout(150)
    # A6: identify candidate cards render in the click-anchored popover, not the
    # panel body.
    txt = page.inner_text("#ref-identify-popover")
    assert "V 2p" in txt
    assert "approximate" in txt              # data-tier badge (plain-language), non-authoritative
    assert "Δ" in txt                   # Δ shown


# ── A6: identify de-gated from the palette + click-anchored popover ───────────

def test_identify_works_with_palette_closed(page):
    setup_u(page, 2.7)
    assert page.evaluate("() => _refPanelOpen") is False     # palette is CLOSED (setup_u closed it)
    page.click("#ref-identify-btn")                          # arm from the TOOLBAR (no palette needed)
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])                       # real click reaches the chart
    page.wait_for_timeout(150)
    r = page.evaluate("""() => {
        const tab=_refActiveTab(); const id=tab&&tab._refIdentify;
        const pop=document.getElementById('ref-identify-popover');
        return { has:!!id, top:id&&id.cands[0]&&id.cands[0].label,
                 popover:!!pop, popHasCard: pop ? /U 4f7\\/2/.test(pop.innerText) : false };
    }""")
    assert r["has"] is True
    assert r["top"] == "U 4f7/2"
    assert r["popover"] is True and r["popHasCard"] is True
    page.click("#ref-identify-btn")                          # disarm (leave clean state)


def test_identify_works_with_palette_open(page):
    setup_u(page, 2.7)
    # Open the palette and move it LEFT so the right-side U peak is not under it.
    page.evaluate("""() => {
        if(!_refPanelOpen) toggleRefPanel();
        const el=document.getElementById('ref-panel');
        el.style.left='8px'; el.style.top='8px'; el.style.right='auto';
    }""")
    page.wait_for_timeout(100)
    assert page.evaluate("() => _refPanelOpen") is True
    page.click("#ref-identify-btn")
    xy = _peak_client_xy(page, 377.3)
    page.mouse.click(xy["x"], xy["y"])
    page.wait_for_timeout(150)
    r = page.evaluate("""() => {
        const tab=_refActiveTab(); const id=tab&&tab._refIdentify;
        return { has:!!id, top:id&&id.cands[0]&&id.cands[0].label,
                 panelOpen:_refPanelOpen, popover:!!document.getElementById('ref-identify-popover') };
    }""")
    assert r["has"] is True and r["top"] == "U 4f7/2"        # identify worked with palette OPEN
    assert r["panelOpen"] is True                            # palette stayed open
    assert r["popover"] is True
    page.click("#ref-identify-btn")                          # disarm
    page.evaluate("() => { const el=document.getElementById('ref-panel'); el.style.left=el.style.top=''; if(_refPanelOpen) toggleRefPanel(); }")


def test_identify_popover_sits_above_palette(page):
    setup_u(page, 2.7)
    page.evaluate("() => { if(!_refPanelOpen) toggleRefPanel(); }")
    page.evaluate("() => _refIdentifyAt(377.3, {x:220, y:220})")   # produce the popover
    page.wait_for_timeout(120)
    z = page.evaluate("""() => {
        const pop=document.getElementById('ref-identify-popover');
        const pal=document.getElementById('ref-panel');
        return { pop: parseInt(getComputedStyle(pop).zIndex || '0', 10),
                 pal: parseInt(getComputedStyle(pal).zIndex || '0', 10) };
    }""")
    assert z["pop"] > z["pal"], z                            # popover renders ABOVE the palette
    page.evaluate("() => { _refClearIdentify(); if(_refPanelOpen) toggleRefPanel(); }")


def test_a5_passthrough_guard_fully_removed(page):
    setup_u(page, 2.7)
    page.evaluate("() => { if(!_refPanelOpen) toggleRefPanel(); }")   # palette OPEN
    # The interim helper is gone…
    assert page.evaluate("() => typeof _refUpdateIdentifyPassthrough") == "undefined"
    page.click("#ref-identify-btn")                          # arm identify
    page.wait_for_timeout(80)
    g = page.evaluate("""() => {
        const p=document.getElementById('ref-panel');
        return { mode: placeMode, cls: p.classList.contains('identify-passthrough'),
                 pe: getComputedStyle(p).pointerEvents };
    }""")
    assert g["mode"] == "identify"
    assert g["cls"] is False and g["pe"] != "none"           # no passthrough class / pointer-events guard
    page.click("#ref-identify-btn")                          # disarm
    page.evaluate("() => { if(_refPanelOpen) toggleRefPanel(); }")
