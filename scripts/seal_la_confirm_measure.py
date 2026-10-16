"""The LA unit's measurement (2026-10-15): how many fresh fits read CURRENT, and how often their record is confirmed
when checked again, on the committed projects — before (np.convolve) and after (the fixed-order convolution).

Loads each committed project (docs/autofit/test_data/*.proj.zip) into the page served at --url (run it like
production: gunicorn -w 4), presses Run Fit on every spectrum tab with a model, waits for the fit's own check, then
asks the server to check the record --checks more times ("check again": a new request each, which a multi-worker
server may answer in another process). Reports per tab its state after the fit and the states of the re-checks, and
the totals, split by whether the model holds an LA (LACX) component.

    venv/bin/python scripts/seal_la_confirm_measure.py --url http://127.0.0.1:PORT [--checks 5] [--json OUT]
"""
import argparse
import base64
import glob
import json
import os

from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOAD = """async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
  await _loadZipProject(new File([b], name)); }"""
RUN = """async (checks) => {
  const settle = async t => { for (let k = 0; k < 2400 && _sealAttempts.has(t); k++) await new Promise(r => setTimeout(r, 50)); };
  const out = [];
  for (const t of tabManager.tabs.filter(x => !x.isStack && x.peaks && x.peaks.length)) {
    tabManager.activateTab(t.id);
    const la = t.peaks.some(p => p.shape === 'LACX');
    let err = null;
    try { await runFit(); } catch (e) { err = String(e); }
    await settle(t);
    const fr = state.fitResult, sealed = !!(fr && fr.seal);
    const first = sealed ? sealedState(fr, t) : null;
    const again = [];
    if (sealed && fr.seal.engine === 'server') for (let i = 0; i < checks; i++) {
      await _ensureVerified(t, true); await settle(t);
      const s = sealedState(state.fitResult, t); again.push(s.state + (s.check ? ':' + s.check : ''));
    }
    out.push({ tab: t.name, la, sealed, err, state: first ? first.state + (first.check ? ':' + first.check : '') : null, again });
  }
  return out; }"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--checks", type=int, default=5)
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for f in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip"))):
            pg = br.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(a.url + "/", wait_until="load")
            pg.evaluate(LOAD, [base64.b64encode(open(f, "rb").read()).decode(), os.path.basename(f)])
            pg.wait_for_timeout(500)
            for r in pg.evaluate(RUN, a.checks):
                rows.append({"project": os.path.basename(f), **r, "page_errors": errors})
            pg.close()
            print(f"{os.path.basename(f)} done", flush=True)
        br.close()
    for la in (True, False):
        sel = [r for r in rows if r["la"] is la and r["sealed"]]
        first = {}
        for r in sel:
            first[r["state"]] = first.get(r["state"], 0) + 1
        again = [s for r in sel for s in r["again"]]
        conf = sum(1 for s in again if s == "current")
        print(f"{'LA' if la else 'no LA'}: {len(sel)} fits; after the fit {dict(sorted(first.items()))}; "
              f"re-checks current {conf} / {len(again)}")
    per_project = {r["project"]: len(r["page_errors"]) for r in rows}
    print(f"not sealed: {sum(1 for r in rows if not r['sealed'])}; page errors: {sum(per_project.values())}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()
