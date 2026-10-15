"""Seal 1d (docs/superpowers/plans/2026-10-15-seal-1d-rerun.md): "Re-run this fit" beside every sealed server fit shown
as recorded — the record's own request and seed refitted, compared by the server's one comparator; the outcome is
shown, the scattered starts on their own line, and NOTHING the fit is changes (the seal, the model, the state).

Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import json

import pytest

pytest.importorskip("playwright.sync_api")

from test_browser_bg_window_request import browser, server  # noqa: F401,E402
from test_browser_seal_requests import SCENARIOS, _setup  # noqa: E402

SETTLE = """async () => { for (let k = 0; k < 600 && tabManager.tabs.some(t => _sealAttempts.has(t)); k++)
  await new Promise(r => setTimeout(r, 50)); }"""
PANEL = """() => { const el = document.querySelector('#results-area .seal-rerun');
  return el ? { status: el.getAttribute('data-rerun'), text: el.textContent.replace(/\\s+/g, ' ').trim(),
                button: !!el.querySelector('.seal-rerun-btn'),
                same: (el.querySelector('.seal-rerun-outcome') || { getAttribute: () => null }).getAttribute('data-same'),
                starts: (el.querySelector('.seal-rerun-starts') || { getAttribute: () => null }).getAttribute('data-same') } : null; }"""
FIT = """() => ({ seal: JSON.stringify(state.fitResult.seal), peaks: JSON.stringify(state.peaks),
               state: sealedState(state.fitResult, _activeTab()).state, same: state.fitResult.seal === window.__seal })"""
DONE = "() => { const el = document.querySelector('#results-area .seal-rerun'); return el && el.getAttribute('data-rerun') !== 'running' && el.getAttribute('data-rerun') !== ''; }"


def _page(browser, server, scenario="gauss_voigt_linear_avg3_window", local=False):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    _setup(pg, SCENARIOS[scenario])
    if local:
        pg.route("**/api/upload", lambda route: route.abort())
    pg.evaluate("async () => { await runFit(); }")
    if local:
        pg.unroute("**/api/upload")
    pg.evaluate(SETTLE)
    pg.evaluate("() => { window.__seal = state.fitResult.seal; renderResults(); }")
    return pg


def _rerun(pg):
    pg.evaluate("() => { document.querySelector('#results-area .seal-rerun-btn').click(); }")
    pg.wait_for_function(DONE, timeout=120000)
    return pg.evaluate(PANEL)


def test_a_rerun_reproduces_the_fit_and_changes_nothing(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        before = pg.evaluate(FIT)
        assert before["state"] == "current" and pg.evaluate(PANEL)["button"]
        got = _rerun(pg)
        assert got["status"] == "done" and got["same"] == "1" and "Re-run: reproduced within rounding." in got["text"], got
        assert got["starts"] == "1" and "Scattered starts on re-run: the same." in got["text"], got
        assert pg.evaluate(FIT) == before                                        # the seal, the model, the state
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


@pytest.mark.parametrize("reply,words", [
    ({"same": False, "problems": ["individual_peaks.0.params.center.value: 284.5 vs 285.1"], "n_problems": 3,
      "starts": {"same": True, "problems": []}, "numerics": {"same": True, "differing": []}},
     "Re-run: a different solution (individual_peaks.0.params.center.value: 284.5 vs 285.1; 2 more) — this fit is not unique (not stale)."),
    ({"same": True, "problems": [], "n_problems": 0, "starts": {"same": False, "problems": ["starts.n_same_as_fit: 3 vs 2"]},
      "numerics": {"same": True, "differing": []}},
     "Scattered starts on re-run: differ (starts.n_same_as_fit: 3 vs 2)."),
    ({"same": True, "problems": [], "n_problems": 0, "starts": {"same": True, "problems": []},
      "numerics": {"same": False, "differing": ["numpy 1.0.0 (here 2.4.4)"]}},
     "Re-run under other numerics (numpy 1.0.0 (here 2.4.4)): reproduced within rounding."),
])
def test_each_outcome_is_said_and_none_changes_the_fit(browser, server, reply, words):  # noqa: F811
    pg = _page(browser, server)
    try:
        before = pg.evaluate(FIT)
        pg.route("**/api/compare-fits", lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(reply)))
        got = _rerun(pg)
        assert words in got["text"], got
        assert pg.evaluate(FIT) == before
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_a_rerun_that_cannot_run_says_so(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        before = pg.evaluate(FIT)
        pg.route("**/api/fit/start", lambda route: route.fulfill(status=500, content_type="application/json", body='{"error": "boom"}'))
        got = _rerun(pg)
        assert got["status"] == "failed" and "Re-run failed: boom." in got["text"], got
        assert pg.evaluate(FIT) == before
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_cancel_and_a_replaced_fit_leave_no_outcome(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        held = []
        pg.route("**/api/fit/start", lambda route: held.append(route))
        pg.evaluate("() => { window.__r = rerunSealedFit(); }")
        pg.wait_for_function("() => document.querySelector('#results-area .seal-rerun').getAttribute('data-rerun') === 'running'")
        pg.evaluate("async () => { _cancelRerun(); await window.__r; }")
        got = pg.evaluate(PANEL)
        assert got["status"] == "" and got["button"], got                       # back to the control, nothing said
        # another fit installed while a re-run runs: the re-run is dropped, the new fit has no outcome
        pg.unroute_all(behavior="ignoreErrors")
        pg.evaluate("""() => { window.__r = rerunSealedFit();
            state.fitResult = Object.freeze({ seal: _makeSeal(structuredClone(state.fitResult.seal)) }); }""")
        pg.evaluate("async () => { await window.__r; }")
        assert pg.evaluate("() => _rerunOutcomes.has(window.__seal) || _rerunOutcomes.has(state.fitResult.seal)") is False
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_the_control_is_beside_every_sealed_server_fit_shown_as_recorded_and_nowhere_else(browser, server):  # noqa: F811
    pg = _page(browser, server, local=True)                                      # a local fit: a starting point, no re-run
    try:
        assert pg.evaluate("() => state.fitResult.seal.engine") == "local"
        assert pg.evaluate(PANEL) is None
    finally:
        pg.close()
    pg = _page(browser, server)
    try:
        assert pg.evaluate(PANEL)["button"]
        pg.evaluate("() => { state.peaks[0].center += 0.05; updatePlot(); renderResults(); }")   # STALE: nothing shown as recorded
        assert pg.evaluate(PANEL) is None
        pg.evaluate("() => { state.peaks[0].center -= 0.05; updatePlot(); renderResults(); }")
        assert pg.evaluate(PANEL)["button"]
        pg.evaluate("""() => { const v = _sealView(state.fitResult.seal);                   // an unsealed (legacy) fit
            state.fitResult = { be: v.energies.slice(), bgIntensity: v.background.slice(), fittedY: v.fittedY.slice(),
                                bgSubtracted: v.counts.map((c, i) => c - v.background[i]), chiReduced: v.statistics.chi2r,
                                rmse: v.statistics.rmse, startsModelKey: _startsLiveKey() }; renderResults(); }""")
        assert pg.evaluate(PANEL) is None
    finally:
        pg.close()
