"""Seal 1c step 2 (plan docs/superpowers/plans/2026-10-14-seal-1c-page.md §12): the ONE request builder
(`_buildFitRequest`) and the pure projection must leave every request the page sends EXACTLY as it was.

A corpus of scenarios — lineshapes, links, locks, every background method, manual anchors, averaging,
methods — is driven through the real page and the `/api/fit/start` body captured (Playwright request
interception; `session_id` removed: transport). The bodies the page sent BEFORE the refactor are the
committed fixture `tests/fixtures/seal_1c_requests.json` (regenerate only on purpose:
SEAL_1C_RECORD=1 pytest tests/test_browser_seal_requests.py, at the commit whose requests are the
reference). Auto-Fit's FINAL request depends on its anchor fit's result, so it is pinned in the same run:
the pure derivation from the anchor request and reply must rebuild it exactly.

Skips cleanly when Playwright/Chromium are absent.
"""
import json
import os

import pytest

pytest.importorskip("playwright.sync_api")

from test_browser_bg_window_request import browser, server  # noqa: F401,E402  (shared fixtures)

FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "seal_1c_requests.json")
RECORD = os.environ.get("SEAL_1C_RECORD") == "1"

# Each scenario: a list of peaks (page fields), the background controls, the method.
SCENARIOS = {
    "gl_shirley_default": dict(peaks=[{"shape": "GL", "center": 284.8, "fwhm": 1.2, "amplitude": 6000, "glMix": 30}],
                               bg={"type": "shirley"}, method="least_squares"),
    "gauss_voigt_linear_avg3_window": dict(
        peaks=[{"shape": "Gaussian", "center": 284.8, "fwhm": 1.1, "amplitude": 5800},
               {"shape": "Voigt", "center": 286.4, "fwhm": 1.3, "amplitude": 1400}],
        bg={"type": "linear", "start": "296.0", "end": "281.0", "avg": "3"}, method="leastsq"),
    "asymgl_linked_smart": dict(
        peaks=[{"shape": "asym-GL", "center": 284.8, "fwhm": 1.0, "amplitude": 6000, "glMix": 20, "asymmetry": 0.2},
               {"shape": "asym-GL", "center": 286.4, "fwhm": 1.0, "amplitude": 1500, "glMix": 20, "asymmetry": 0.2,
                "linkTo": 0, "linkOffset": 1.6, "linkRatio": 0.25}],
        bg={"type": "smart"}, method="least_squares"),
    "ds_dsg_lacx_locks_tougaard": dict(
        peaks=[{"shape": "DS", "center": 284.8, "fwhm": 1.0, "amplitude": 6000, "dsAlpha": 0.12, "dsGamma": 0.0, "fixCenter": True},
               {"shape": "DSG_LA", "center": 286.4, "fwhm": 1.2, "amplitude": 1500, "laAlpha": 0.1, "laBeta": 0.3, "laM": 0.4, "fixLaM": True},
               {"shape": "LACX", "center": 288.0, "fwhm": 1.4, "amplitude": 400, "caAlpha": 1.2, "caBeta": 1.0, "caM": 6, "fixAmplitude": True}],
        bg={"type": "tougaard"}, method="least_squares"),
    "lorentzian_manual_anchors_nelder": dict(
        peaks=[{"shape": "Lorentzian", "center": 284.8, "fwhm": 1.0, "amplitude": 6000}],
        bg={"type": "manual", "anchors": [[296.5, 805.0], [281.2, 801.0]]}, method="nelder"),
    "gl_none_fixed_mix": dict(
        peaks=[{"shape": "GL", "center": 284.8, "fwhm": 1.2, "amplitude": 6000, "glMix": 0, "fixGlMix": True, "fixFwhm": True}],
        bg={"type": "none"}, method="least_squares"),
}


def _setup(page, sc):
    page.evaluate(
        """(sc) => {
            const raw = [], inten = [];
            const g = (be, c, a, w) => a * Math.exp(-Math.pow(be - c, 2) / (2 * w * w));
            for (let i = 0; i < 191; i++) {
                const be = Math.round((298.16 - i * 0.1) * 1000) / 1000;
                raw.push(be); inten.push(800 + g(be, 284.8, 6000, 0.7) + g(be, 286.4, 1500, 0.8) + g(be, 288.0, 400, 0.9));
            }
            tabManager.createTab('seal request corpus', raw, inten);
            const t = tabManager._getTab(tabManager.activeId);
            state.ccShift = 0; if (t) t.ccShift = 0;
            document.getElementById('roi-min').value = '279.0';
            document.getElementById('roi-max').value = '298.5';
            document.getElementById('bg-type').value = sc.bg.type;
            if (typeof _onBgTypeChange === 'function') _onBgTypeChange();
            document.getElementById('bg-start').value = sc.bg.start || '298.16';
            document.getElementById('bg-end').value = sc.bg.end || '279.16';
            if (sc.bg.avg) document.getElementById('bg-endpoint-avg').value = sc.bg.avg;
            if (sc.bg.anchors) _setManualAnchors(sc.bg.anchors.map(([x, y]) => ({ x, y })));
            document.getElementById('fit-method').value = sc.method;
            const ids = [];
            for (const spec of sc.peaks) {
                addPeak();
                const p = state.peaks[state.peaks.length - 1];
                ids.push(p.id);
                for (const [k, v] of Object.entries(spec)) {
                    if (k === 'linkTo') p.linked = ids[v];
                    else p[k] = v;
                }
            }
            updatePlot();
        }""",
        sc,
    )
    page.wait_for_timeout(150)


def _body(req):
    b = req.post_data_json
    b.pop("session_id", None)
    return b


def _run_fit_body(page):
    with page.expect_request("**/api/fit/start", timeout=30000) as info:
        page.evaluate("() => { runFit(); }")
    body = _body(info.value)
    page.wait_for_timeout(300)
    return body


@pytest.fixture(scope="module")
def corpus(browser, server):  # noqa: F811
    out = {}
    for name, sc in SCENARIOS.items():
        pg = browser.new_page(viewport={"width": 1500, "height": 950})
        pg.goto(server + "/", wait_until="load")
        try:
            _setup(pg, sc)
            out[name] = _run_fit_body(pg)
        finally:
            pg.close()
    if RECORD:
        os.makedirs(os.path.dirname(FIXTURE), exist_ok=True)
        with open(FIXTURE, "w") as f:
            json.dump(out, f, indent=1, sort_keys=True)
    return out


@pytest.mark.parametrize("name", sorted(SCENARIOS))
def test_every_run_fit_request_is_exactly_what_the_page_sent_before(corpus, name):
    with open(FIXTURE) as f:
        before = json.load(f)
    assert json.dumps(corpus[name], sort_keys=True) == json.dumps(before[name], sort_keys=True)
