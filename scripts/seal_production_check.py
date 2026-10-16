"""Production browser check for the sealed fit record (deploy of 2026-10-16, both machines).

Against the page served at --url (https://xps.fortierlab.org, https://xps2.fortierlab.org, or a dev server):
  1. health;
  2. an OLD project reopened (every committed project in docs/autofit/test_data/*.proj.zip): each tab's fit
     reads as designed — legacy / stale / peaks-only, never current — and the page raises no error;
  3. a FRESH fit on a non-LA tab reads current (confirmed), and its record names --commit with git_dirty false;
  4. "Re-run this fit" on it: done, reproduced within rounding, the fit unchanged;
  5. an LA fit (a tab with an LA(α,β,m) component) reads current after its fit and on --checks more checks.
Prints one line per check and PASS / FAIL; --json writes the details.

    venv/bin/python scripts/seal_production_check.py --url URL --commit SHA [--checks 3] [--json OUT]
"""
import argparse
import base64
import glob
import json
import os
import sys
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOAD = """async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
  await _loadZipProject(new File([b], name)); }"""
SETTLE = """async () => { for (let k = 0; k < 4800 && tabManager.tabs.some(t => _sealAttempts.has(t)); k++)
  await new Promise(r => setTimeout(r, 50)); }"""
STATES = """() => tabManager.tabs.filter(t => !t.isStack).map(t => ({ tab: t.name,
  state: t.peaks && t.peaks.length ? (t.fitResult ? sealedState(t.fitResult, t).state : 'peaks-only') : 'no model',
  la: (t.peaks || []).some(p => p.shape === 'LACX') }))"""
FIT = """async ([name, checks]) => {
  const t = tabManager.tabs.find(x => x.name === name);
  tabManager.activateTab(t.id);
  await runFit();
  const settle = async () => { for (let k = 0; k < 4800 && _sealAttempts.has(t); k++) await new Promise(r => setTimeout(r, 50)); };
  await settle();
  const fr = state.fitResult, first = sealedState(fr, t);
  const again = [];
  for (let i = 0; i < checks; i++) { await _ensureVerified(t, true); await settle(); again.push(sealedState(state.fitResult, t).state); }
  renderResults();
  return { state: first.state, check: first.check, reason: first.reason, again,
           software: fr.seal && fr.seal.O ? fr.seal.O.software : null, engine: fr.seal ? fr.seal.engine : null }; }"""
PANEL = """() => { const el = document.querySelector('#results-area .seal-rerun');
  return el ? { status: el.getAttribute('data-rerun'), text: el.textContent.replace(/\\s+/g, ' ').trim(),
                button: !!el.querySelector('.seal-rerun-btn'),
                same: (el.querySelector('.seal-rerun-outcome') || { getAttribute: () => null }).getAttribute('data-same') } : null; }"""
DONE = """() => { const el = document.querySelector('#results-area .seal-rerun');
  return el && el.getAttribute('data-rerun') !== 'running' && el.getAttribute('data-rerun') !== ''; }"""
SNAP = """() => ({ seal: JSON.stringify(state.fitResult.seal), peaks: JSON.stringify(state.peaks),
               state: sealedState(state.fitResult, _activeTab()).state })"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--checks", type=int, default=3)
    ap.add_argument("--json")
    a = ap.parse_args()
    out, ok = {"url": a.url}, True

    def report(name, passed, detail):
        nonlocal ok
        ok &= bool(passed)
        out[name] = {"pass": bool(passed), "detail": detail}
        print(f"{'ok  ' if passed else 'FAIL'} {name}: {json.dumps(detail)[:400]}", flush=True)

    req = urllib.request.Request(a.url + "/api/health", headers={"User-Agent": "Mozilla/5.0 (seal production check)"})
    health = json.loads(urllib.request.urlopen(req, timeout=30).read())    # Cloudflare refuses urllib's own agent
    report("health", health.get("status") == "ok", health)
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        # 2. every committed project reopened as it was saved
        reopened, projects = {}, {}
        for f in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip"))):
            pg = br.new_page(viewport={"width": 1500, "height": 950})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(a.url + "/", wait_until="load")
            pg.evaluate(LOAD, [base64.b64encode(open(f, "rb").read()).decode(), os.path.basename(f)])
            pg.wait_for_timeout(500)
            pg.evaluate(SETTLE)
            rows = pg.evaluate(STATES)
            projects[os.path.basename(f)] = {"rows": rows, "errors": errors}
            for r in rows:
                reopened[r["state"]] = reopened.get(r["state"], 0) + 1
            pg.close()
        errs = sum(len(p["errors"]) for p in projects.values())
        report("old projects reopen as designed (never current)", "current" not in reopened and errs == 0,
               {"states": reopened, "page_errors": errs})
        # 3-5. fresh fits on one project holding both kinds
        f = os.path.join(ROOT, "docs/autofit/test_data/UCl4_on_graphite.proj.zip")
        pg = br.new_page(viewport={"width": 1500, "height": 950})
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(a.url + "/", wait_until="load")
        pg.evaluate(LOAD, [base64.b64encode(open(f, "rb").read()).decode(), os.path.basename(f)])
        pg.wait_for_timeout(500)
        rows = pg.evaluate(STATES)
        plain = next(r["tab"] for r in rows if r["state"] != "no model" and not r["la"])
        la = next(r["tab"] for r in rows if r["state"] != "no model" and r["la"])
        got = pg.evaluate(FIT, [plain, 0])
        sw = got["software"] or {}
        report("fresh fit confirmed", got["state"] == "current" and got["engine"] == "server",
               {"tab": plain, "state": got["state"], "check": got["check"], "reason": got["reason"]})
        report("record names the deployed commit, clean", sw.get("git_commit") == a.commit and sw.get("git_dirty") is False,
               {k: sw.get(k) for k in ("git_commit", "git_dirty", "numerics", "python", "os")})
        before = pg.evaluate(SNAP)
        pg.evaluate("() => { document.querySelector('#results-area .seal-rerun-btn').click(); }")
        pg.wait_for_function(DONE, timeout=600000)
        panel = pg.evaluate(PANEL)
        report("Re-run this fit", panel and panel["status"] == "done" and panel["same"] == "1" and pg.evaluate(SNAP) == before,
               panel)
        got = pg.evaluate(FIT, [la, a.checks])
        report("LA fit confirms", got["state"] == "current" and all(s == "current" for s in got["again"]),
               {"tab": la, "state": got["state"], "again": got["again"], "check": got["check"], "reason": got["reason"]})
        report("no page errors", errors == [], errors[:5])
        pg.close()
        br.close()
    out["projects"] = projects
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
