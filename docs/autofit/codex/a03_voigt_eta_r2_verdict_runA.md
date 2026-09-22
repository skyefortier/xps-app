OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0c7bc-8196-7e53-abc5-7cd48ccf6a06
--------
user
RECHECK, round 2, of unit A03: branch fix-voigt-eta-identity, git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round 1 (docs/autofit/codex/a03_voigt_eta_verdict_runA.md and runB.md, both NO-GO) found: (1) scripts/voigt_eta_measure.py took the target file's own Voigt specs as the "old free-eta" arm; (2) the release-note number was a server-curve/trapezoid comparison of two refits, not the page's saved numbers vs the page's refit numbers; (3) peakToBackendSpec (and the Python twin) sent an asym-GL mix of exactly 0 as 50 and a DS alpha of exactly 0 as 0.1 (`p.glMix || 50`, `p.dsAlpha || 0.1`), reproducible as a 6.9 % / 8.8 % drawn-vs-fitted discrepancy when locked, and the new harnesses did not cover endpoints or go through the builder; (4) the uncertainty panel told a Voigt's user to unlock a padlock that does not exist; (5) wrong numbers ("8-20 %" chi2r, "24 %", "1.60 pp") and the residual attributed to the caM clamp without a controlled comparison.

What changed since (plan §9 lists it; commit "fix(A03): Codex round 1"): both measurement arms constructed explicitly and re-run (plan §2a; docs/findings/a03/voigt_eta_summary.txt); a new scripts/voigt_saved_vs_refit.js measuring, with the page's own evalPeakArray/_peakArea integration on both sides, the saved peaks vs the refit under the A03 request with the page's n_perturb 3 on the 55 committed tabs that have a saved fit and a Voigt (plan §2b; docs/findings/a03/voigt_saved_vs_refit.json: median 0.35 pp, max 0.69 pp, none > 1 pp); both builders now fall back to a default only for a NON-NUMBER (Number.isFinite / _finite), tests/js/lineshape_roundtrip.test.js round-trips every shape parameter LOCKED AT ITS BOUNDS, and the parity sweep (D) takes its backend parameters through peakToBackendSpec; the uncertainty panel emits "fixed at 50/50 by the Voigt shape - choose GL to fit the mix" for a Voigt's gl_ratio; scripts/local_server_gap.js gained a control arm (server with every LA m HELD at its start) and the docs now attribute the residual per target (Scan_6 = the caM clamp; Scan_5/8 = the local engine in a worse minimum, chi2r +10-13 % with m held too; Scan_4 half each); every quoted number re-derived from the committed artifacts.

Verify each round-1 item is actually closed (not just described), then try to break the new pieces: voigt_saved_vs_refit.js (does it use the page's numbers on BOTH sides? ROI/charge-shift handling; the bridge's n_perturb; the 55-tab roster - are saved tabs without a fitResult correctly excluded and are Batch-Fit-only tabs a problem?); the builder fix (any other `||` default in either builder that turns a legitimate 0 or false into something else? the seed: does a request with a mix of exactly 0 now hash differently than before - is that a release-note item?); the endpoint round-trips (do they exercise the LOCKED path on the server, i.e. vary false, and compare drawn vs fitted?); the control arm (is holding m via fixCaM on the start copy the right control? does the twin send fix_m?); the U 4f battery re-basing from round 1 (unchanged; still: is refit-from-refit a meaningful stationarity test?); docs vs artifacts (every number in the plan, findings §7, CLAUDE.md, the commit messages and the two code comments must match docs/findings/a03/*).

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check the diff and round-1 findings, verify the harnesses against the page and server code, then run focused checks. I’ll keep this read-only and finish with a ranked verdict.

exec
/bin/zsh -lc "pwd; git status --short; git diff --stat main..HEAD; rg --files -g 'AGENTS.md' -g '*a03*' -g '*voigt*' -g '*roundtrip*' -g '*local_server*' -g 'CLAUDE.md'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Xoy6Lqzh' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9OC0Pei4' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_r2_verdict_runB.md
?? docs/autofit/codex/a03_voigt_eta_recheck_prompt.txt
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7CQhuP1t' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Oq1fF2j1' (errno=Operation not permitted)
 CLAUDE.md                                          |   46 +-
 autofit/parity.py                                  |   23 +-
 autofit/reference.py                               |   54 +-
 docs/autofit/codex/a03_voigt_eta_review_prompt.txt |   22 +
 docs/autofit/codex/a03_voigt_eta_verdict_runA.md   | 7974 ++++++++++++++++++++
 docs/autofit/codex/a03_voigt_eta_verdict_runB.md   | 7777 +++++++++++++++++++
 docs/findings/2026-09-fit-determinacy.md           |   69 +
 docs/findings/a03/local_server_gap.json            | 3375 +++++++++
 docs/findings/a03/local_server_gap.log             |   18 +
 docs/findings/a03/voigt_eta_summary.txt            |    7 +
 docs/findings/a03/voigt_saved_vs_refit.json        | 2395 ++++++
 docs/findings/a03/voigt_saved_vs_refit.log         |   56 +
 .../plans/2026-09-22-a03-voigt-eta-identity.md     |  212 +
 scripts/bg_window_worked_example.py                |    2 +-
 scripts/endpoint_avg_sensitivity.py                |    2 +-
 scripts/gen_u4f_battery_fixture.py                 |    5 +-
 scripts/local_server_gap.js                        |  101 +
 scripts/voigt_eta_measure.py                       |  138 +
 scripts/voigt_saved_vs_refit.js                    |   61 +
 templates/index.html                               |   53 +-
 tests/autofit/battery_common.py                    |   25 +-
 tests/autofit/fixtures/u4f_battery_expected.json   | 1064 +--
 tests/autofit/test_u4f_parity_battery.py           |   13 +-
 tests/js/fit_acceptance.test.js                    |    2 +-
 tests/js/lineshape_parity.test.js                  |   94 +
 tests/js/lineshape_parity_backend.py               |   19 +-
 tests/js/lineshape_roundtrip.test.js               |  232 +
 tests/js/lineshape_roundtrip_backend.py            |   37 +
 tests/js/local_lm_server_parity_backend.py         |    3 +-
 tests/test_voigt_contract.py                       |   80 +
 30 files changed, 23381 insertions(+), 578 deletions(-)
CLAUDE.md
scripts/voigt_eta_measure.py
scripts/voigt_saved_vs_refit.js
scripts/local_server_gap.js
docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md
tests/test_browser_overlay_zip_roundtrip.py
docs/findings/a03/local_server_gap.log
docs/findings/a03/voigt_saved_vs_refit.json
docs/findings/a03/voigt_saved_vs_refit.log
docs/findings/a03/local_server_gap.json
docs/findings/a03/voigt_eta_summary.txt
tests/autofit/test_browser_schema_roundtrip.py
tests/js/shape_switch_roundtrip.test.js
tests/test_voigt_contract.py
tests/js/lineshape_roundtrip_backend.py
tests/js/lineshape_roundtrip.test.js
docs/autofit/codex/a03_voigt_eta_review_prompt.txt
docs/autofit/codex/a03_voigt_eta_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r2_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_recheck_prompt.txt
docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md

exec
/bin/zsh -lc 'cat scripts/voigt_saved_vs_refit.js scripts/voigt_eta_measure.py scripts/local_server_gap.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
#!/usr/bin/env node
// A03 (Codex round 1): what a student SEES change when a saved project with
// Voigt components is re-fitted under the fixed-eta request — measured with
// the PAGE's own numbers on both sides. For every committed spectrum tab
// that carries a saved fit and a Voigt component: the page's area of each
// saved peak (evalPeakArray over the ROI grid × step, as _peakArea; a Voigt
// at eta 0.5, an LA at its rounded m — exactly the Results table) versus the
// page's area of the same peaks after the server refit (the page's request
// builder, Trust-Region, the page's n_perturb 3, parameters written back
// through the page's _applyBackendParams). Usage: node scripts/voigt_saved_vs_refit.js [out.json]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
  throw new Error('unbalanced ' + name);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS',
  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array', 'evalPeakArray', 'getPeak', '_applyBackendParams'];
const state = { peaks: [] };
const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams };')(state);
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const DATA = path.join(ROOT, 'docs/autofit/test_data');
const area = (be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return fns.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), n_perturb: 3, targets: [] };
for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
  for (const t of tabs) {
    if (!t.fitResult || !(t.peaks || []).some(p => p.shape === 'Voigt')) continue;
    const ui = t.ui || {};
    const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
    if (!Number.isFinite(roiMin) || !Number.isFinite(roiMax) || !ui.bgType) continue;
    const be = [], inten = [];
    t.rawBE.forEach((b, i) => { const c = b - (t.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(t.rawIntensity[i]); } });
    if (be.length < 10) continue;
    const saved = JSON.parse(JSON.stringify(t.peaks));
    let srv;
    try {
      srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be, inten, peaks: saved, ui, n_perturb: 3 }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    } catch (e) { out.targets.push({ project: zp, tab: t.name, error: String(e.message).slice(0, 200) }); continue; }
    const refit = JSON.parse(JSON.stringify(saved));
    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; fns._applyBackendParams(refit[i], par); });
    const aS = saved.map(p => area(be, p)), aR = refit.map(p => area(be, p));
    const tS = aS.reduce((s, v) => s + v, 0), tR = aR.reduce((s, v) => s + v, 0);
    const comps = saved.map((p, i) => ({ name: p.name, shape: p.shape, saved_area: aS[i], refit_area: aR[i],
      dArea_pct: aS[i] ? 100 * (aR[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aR[i] / tR - aS[i] / tS) }));
    const rec = { project: zp, tab: t.name, server_success: srv.success, chi2r: srv.chi2r,
      max_dFrac_pp: Math.max(...comps.map(c => Math.abs(c.dFrac_pp))),
      max_voigt_dArea_pct: Math.max(...comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct))), comps };
    out.targets.push(rec);
    console.error(zp.slice(0, 28), t.name, 'server', srv.success, 'max Δfrac', rec.max_dFrac_pp.toFixed(2), 'pp, max Voigt Δarea', rec.max_voigt_dArea_pct.toFixed(1), '%');
  }
}
const ok = out.targets.filter(r => r.server_success);
const q = v => { v = [...v].sort((a, b) => a - b); return { median: v[Math.floor(v.length / 2)], p90: v[Math.floor(0.9 * (v.length - 1))], max: v[v.length - 1] }; };
out.summary = { n_tabs: out.targets.length, n_converged: ok.length, dFrac_pp: q(ok.map(r => r.max_dFrac_pp)), gt_1pp: ok.filter(r => r.max_dFrac_pp > 1).length, voigt_dArea_pct: q(ok.map(r => r.max_voigt_dArea_pct)) };
console.error(JSON.stringify(out.summary));
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/voigt_saved_vs_refit.json'), JSON.stringify(out, null, 1));
#!/usr/bin/env python3
"""A03 (2026-09-22): what the free-eta Voigt request did, on the committed targets.

Until A03 the page sent a "Voigt" component as pseudo_voigt_gl with gl_ratio
FREE from 0.3 while it drew, integrated and exported eta = 0.5. For every
committed target with a Voigt component this script fits the request BOTH
ways with the page's settings (Trust-Region, n_perturb 3) — (free) as sent
before A03, (fixed) eta held at 0.5 as sent since — and compares three
things per target:
  A. the 0.5 curve under the free fit's parameters (what the page drew for
     that fit) against the free fit's own curve — the reporting error that
     shipped, per component and as area fractions;
  B. the fixed fit against that 0.5 curve;
  C. the fixed fit against the free fit.
All three use the SERVER's curves and trapezoidal integration on the fitted
grid (non-Voigt components as the server fitted them); they characterise
the two requests, not a screen. The student-visible change on re-fitting a
SAVED project — the page's own integration of the saved peaks against the
page's integration of the refit — is scripts/voigt_saved_vs_refit.js.

Usage:
  python scripts/voigt_eta_measure.py targets.json out_dir shard n_shards   # one shard
  python scripts/voigt_eta_measure.py --summary out_dir                     # the numbers
targets.json is the optimizer-disagreement target file (uncommitted; built by
scripts/optimizer_disagreement_targets.js from the committed projects with
the page's CURRENT request builder). Both arms are constructed here
explicitly from the target's shapes — the target file's own Voigt specs are
never used as either baseline, so the numbers do not depend on which
builder produced the file (A03 Codex round 1).
"""
import copy
import glob
import json
import os
import statistics as st
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fitting  # noqa: E402

warnings.filterwarnings("ignore")


def _pack(r):
    return {"success": r["success"], "chi2r": r["statistics"]["reduced_chi_square"], "energy": r["energy"],
            "peaks": [{"id": ip["id"], "y": ip["y"], "params": {k: v.get("value") for k, v in ip["params"].items()}}
                      for ip in r["individual_peaks"]]}


def measure(targets_path, out_dir, shard, n_shards):
    targets = json.load(open(targets_path))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"shard{shard}.jsonl"), "w") as out:
        for k, t in enumerate(targets):
            if k % n_shards != shard:
                continue
            vidx = [i for i, sh in enumerate(t["shapes"]) if sh == "Voigt"]
            if not vidx:
                continue
            b = t["background"]
            kw = dict(background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
                      endpoint_avg=b["endpoint_avg"], n_perturb=3, fit_kws={"method": "least_squares"})
            x = np.asarray(t["be"], float)
            y = np.round(np.asarray(t["inten"], float), 2)   # the upload rounds to 2 dp
            free = copy.deepcopy(t["specs"])
            fixed = copy.deepcopy(t["specs"])
            for i in vidx:
                free[i]["gl_ratio"] = 0.3                     # the request before A03: eta free from 0.3
                free[i]["fix_gl_ratio"] = False
                fixed[i]["gl_ratio"] = 0.5                    # the request since A03: eta held at 0.5
                fixed[i]["fix_gl_ratio"] = True
            rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"],
                   "voigt_ids": [str(t["specs"][i]["id"]) for i in vidx]}
            for lab, specs in (("free", free), ("fixed", fixed)):
                try:
                    rec[lab] = _pack(fitting.run_fit(x, y, specs, **kw))
                except Exception as e:  # noqa: BLE001 — a failed fit is a row, not a crash
                    rec[lab] = {"error": str(e)[:160]}
            out.write(json.dumps(rec) + "\n")
            out.flush()


def summary(out_dir):
    recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(out_dir, "shard*.jsonl"))) for l in open(f)]
    ok = [r for r in recs if "peaks" in r["free"] and "peaks" in r["fixed"] and r["free"]["success"] and r["fixed"]["success"]]
    print(f"targets {len(recs)}, both fits converged {len(ok)}")
    area = lambda x, y: float(abs(np.trapezoid(y, x)))  # noqa: E731
    dA, dB, dC, comp = [], [], [], []
    etas = []
    chi_ratio = []
    for r in ok:
        x = np.asarray(r["free"]["energy"])
        vids = set(r["voigt_ids"])
        a_free, a_disp = [], []
        for pk in r["free"]["peaks"]:
            a = area(x, np.asarray(pk["y"]))
            a_free.append(a)
            if str(pk["id"]) in vids:
                q = pk["params"]
                etas.append(q["gl_ratio"])
                yd = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=q["amplitude"], center=q["center"], fwhm=q["fwhm"], gl_ratio=0.5)
                ad = area(x, yd)
                a_disp.append(ad)
                if a > 0:
                    comp.append(100 * (ad - a) / a)
            else:
                a_disp.append(a)
        a_fix = [area(x, np.asarray(pk["y"])) for pk in r["fixed"]["peaks"]]
        frac = lambda A: [100 * v / sum(A) for v in A]  # noqa: E731
        Ff, Fd, Fx = frac(a_free), frac(a_disp), frac(a_fix)
        dA.append(max(abs(a - b) for a, b in zip(Fd, Ff)))
        dB.append(max(abs(a - b) for a, b in zip(Fx, Fd)))
        dC.append(max(abs(a - b) for a, b in zip(Fx, Ff)))
        chi_ratio.append(r["fixed"]["chi2r"] / r["free"]["chi2r"])

    def q(v):
        v = sorted(v)
        return f"median {st.median(v):.2f}, p90 {v[int(0.9 * len(v))]:.2f}, max {v[-1]:.2f}"

    print(f"free eta of {len(etas)} Voigt components: {sum(e < 0.01 for e in etas)} at 0 (pure Gaussian), "
          f"{sum(e > 0.99 for e in etas)} at 1 (pure Lorentzian), {sum(0.4 <= e <= 0.6 for e in etas)} within 0.4–0.6")
    e = [abs(c) for c in comp]
    print(f"per-Voigt-component DISPLAYED area vs the fitted curve (%): {q(e)}; > 10 % on {sum(v > 10 for v in e)} of {len(e)}; "
          f"displayed high (eta < 0.5) {sum(c > 0 for c in comp)}, low {sum(c < 0 for c in comp)}")
    print(f"A. displayed vs free-fit fractions, max |delta| pp per target: {q(dA)}; > 1 pp on {sum(v > 1 for v in dA)} targets")
    print(f"B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: {q(dB)}; > 1 pp on {sum(v > 1 for v in dB)} targets")
    print(f"C. fixed refit vs free fit, max |delta| pp: {q(dC)}; > 1 pp on {sum(v > 1 for v in dC)} targets")
    print(f"chi2r fixed/free: {q(chi_ratio)}; fixed lower on {sum(v < 1 for v in chi_ratio)} targets (the free fit in a worse minimum)")


if __name__ == "__main__":
    if sys.argv[1] == "--summary":
        summary(sys.argv[2])
    else:
        measure(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
#!/usr/bin/env node
// Local engine vs server from the SAME scaled start on the committed
// UCl4-graphite project's Batch Fit targets (unit W1's methodology,
// 2026-09-18; re-run for A03, 2026-09-22 — the test of whether Batch Fit's
// "starting point" label can retire). Every C1s Scan_N and U4f Scan_N tab is
// a target; the source is the scan the student fitted ('C1s Scan' / 'U4f
// Scan'); the start is the source's model with amplitudes scaled to the
// target's maximum (what runPropagation does); both engines fit that start
// on the same background (the page's computeBackgroundCore; the server
// recomputes its own from the same settings). Differences are evaluated with
// the PAGE's semantics — the server's parameters written onto a copy of the
// start with _applyBackendParams, areas as _peakArea (evalPeakArray over the
// ROI grid × step) — so the comparison is about parameters, not about which
// side integrated. A third arm (Codex round 1: "movement in m alone does not
// establish that the residual is the local clamp") fits the server with every
// LA m HELD at its start (fixCaM on the copy), the one thing the local
// engine cannot move: if that arm agrees with the local engine where the
// free-m arm did not, the attribution is established by a controlled
// comparison, not inferred. Usage: node scripts/local_server_gap.js [out.json]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
  throw new Error('unbalanced ' + name);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_applyBackendParams'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
function makeEnv() {
  const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const f = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, _applyBackendParams };');
  return { ...f(document, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => new Array(be.length).fill(0)), state };
}
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const PROJECT = path.join(ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 1 << 26 }));
function target(env, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  return { be, inten, bg, bgSub: inten.map((v, i) => v - bg[i]), ui, start: cloned };
}
const area = (env, be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return env.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), regions: {} };
for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
  const names = tabs.filter(t => new RegExp('^' + sourceName.replace(' ', ' ') + '_\\d+$').test(t.name)).map(t => t.name);
  out.regions[region] = [];
  for (const name of names) {
    const env = makeEnv(); const T = target(env, sourceName, name);
    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
    const serverFit = startPeaks => {
      const r = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: startPeaks, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
      const peaks = JSON.parse(JSON.stringify(startPeaks));
      r.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(peaks[i], par); });
      return { r, peaks };
    };
    const { r: srv, peaks: serverPeaks } = serverFit(T.start);
    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, fixCaM: true } : p);
    const { r: srvHeld, peaks: serverHeldPeaks } = serverFit(heldStart);
    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p)), aH = serverHeldPeaks.map(p => area(env, T.be, p));
    const tL = aL.reduce((s, v) => s + v, 0), tS = aS.reduce((s, v) => s + v, 0), tH = aH.reduce((s, v) => s + v, 0);
    const comps = localPeaks.map((p, i) => ({ name: p.name, shape: p.shape, linked: !!p.linked,
      dCenter_meV: 1000 * (p.center - serverPeaks[i].center), dFwhm_pct: 100 * (p.fwhm / serverPeaks[i].fwhm - 1),
      dArea_pct: aS[i] ? 100 * (aL[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aL[i] / tL - aS[i] / tS),
      // the held-m arm: local vs server with every LA m held at its start
      held_dCenter_meV: 1000 * (p.center - serverHeldPeaks[i].center), held_dFwhm_pct: 100 * (p.fwhm / serverHeldPeaks[i].fwhm - 1),
      held_dArea_pct: aH[i] ? 100 * (aL[i] / aH[i] - 1) : null, held_dFrac_pp: 100 * (aL[i] / tL - aH[i] / tH),
      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM },
      server_held_m: { center: serverHeldPeaks[i].center, fwhm: serverHeldPeaks[i].fwhm, amplitude: serverHeldPeaks[i].amplitude, area: aH[i], caM: serverHeldPeaks[i].caM } }));
    const mx = f => Math.max(...comps.map(c => Math.abs(c[f]) || 0));
    out.regions[region].push({ target: name, local_success: loc.success, local_chi2r: env.state.fitResult && env.state.fitResult.chiReduced, server_success: srv.success, server_chi2r: srv.chi2r,
      server_held_m_success: srvHeld.success, server_held_m_chi2r: srvHeld.chi2r,
      max_dCenter_meV: mx('dCenter_meV'), max_dFwhm_pct: mx('dFwhm_pct'), max_dArea_pct: mx('dArea_pct'), max_dFrac_pp: mx('dFrac_pp'),
      held_max_dCenter_meV: mx('held_dCenter_meV'), held_max_dFwhm_pct: mx('held_dFwhm_pct'), held_max_dArea_pct: mx('held_dArea_pct'), held_max_dFrac_pp: mx('held_dFrac_pp'), comps });
    console.error(region, name, 'local', loc.success, (env.state.fitResult || {}).chiReduced && env.state.fitResult.chiReduced.toFixed(3), 'server', srv.success, srv.chi2r.toFixed(3), 'max Δcentre', mx('dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('dFwhm_pct').toFixed(2), '%, Δarea', mx('dArea_pct').toFixed(2), '%, Δfrac', mx('dFrac_pp').toFixed(2), 'pp',
      '| m held: server', srvHeld.chi2r.toFixed(3), 'Δcentre', mx('held_dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('held_dFwhm_pct').toFixed(2), '%, Δarea', mx('held_dArea_pct').toFixed(2), '%, Δfrac', mx('held_dFrac_pp').toFixed(2), 'pp');
  }
}
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/local_server_gap.json'), JSON.stringify(out, null, 1));

exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html autofit/parity.py autofit/reference.py tests/autofit/battery_common.py tests/autofit/test_u4f_parity_battery.py scripts/gen_u4f_battery_fixture.py tests/test_voigt_contract.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ORsECwhH' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-dExJi9pc' (errno=Operation not permitted)
diff --git a/autofit/parity.py b/autofit/parity.py
index fb09ddd..5187f85 100644
--- a/autofit/parity.py
+++ b/autofit/parity.py
@@ -36,7 +36,7 @@ from fitting import (
     tougaard_background,
     run_fit,
 )
-from .reference import ReferenceFit
+from .reference import ReferenceFit, apply_backend_params, peak_to_backend_spec
 
 
 def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
@@ -184,16 +184,30 @@ def eval_parity_relmax(rf: ReferenceFit) -> float:
     return float(np.max(np.abs(model + bg - fittedY)) / scale)
 
 
-def refit_record(rf: ReferenceFit) -> dict[str, Any]:
+def refit_record(rf: ReferenceFit, start: dict[str, Any] | None = None) -> dict[str, Any]:
     """
     Deterministic seeded refit (leastsq, no perturbation) from the saved
-    parameters.  Returns a serializable record for fixture freezing.
+    parameters.  Returns a serializable record for fixture freezing; each
+    peak also carries ``params`` (every server parameter's fitted value) so
+    the record can be the START of another refit: with ``start`` (a record
+    from this function) the saved peaks are first overwritten with that
+    record's parameters through the page's write-back twin, exactly as the
+    page holds a model after Run Fit.
     """
+    import copy
+    peaks = rf.peaks
+    if start is not None:
+        peaks = copy.deepcopy(rf.peaks)
+        by_id = {str(pk["id"]): pk for pk in start["peaks"]}
+        for p in peaks:
+            pk = by_id.get(str(p["id"]))
+            if pk is not None and pk.get("params"):
+                apply_backend_params(p, pk["params"])
     i0, i1 = rf.bg_indices()
     res = run_fit(
         rf.roi_be,
         rf.roi_intensity,
-        rf.backend_peak_specs(),
+        [peak_to_backend_spec(p, peaks) for p in peaks],
         background_method=rf.bg_method,
         bg_start_idx=i0,
         bg_end_idx=i1,
@@ -209,6 +223,7 @@ def refit_record(rf: ReferenceFit) -> dict[str, Any]:
             "fwhm": par["fwhm"]["value"],
             "amplitude": par["amplitude"]["value"],
             "area": par["area"]["value"],
+            "params": {k: v["value"] for k, v in par.items() if k != "area"},
         })
     return {
         "project": rf.project,
diff --git a/autofit/reference.py b/autofit/reference.py
index fe46d48..6bb2eb0 100644
--- a/autofit/reference.py
+++ b/autofit/reference.py
@@ -101,15 +101,18 @@ def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
     elif shape == "Lorentzian":
         spec["shape"] = "lorentzian"
     elif shape == "Voigt":
+        # A03: the fixed 50/50 mix the page draws (twin of peakToBackendSpec)
         spec["shape"] = "pseudo_voigt_gl"
-        spec["gl_ratio"] = 0.3
+        spec["gl_ratio"] = 0.5
+        spec["fix_gl_ratio"] = True
     elif shape == "GL":
         spec["shape"] = "pseudo_voigt_gl"
         spec["gl_ratio"] = p["glMix"] / 100.0
     elif shape == "asym-GL":
         spec["shape"] = "asymmetric_gl"
-        spec["gl_ratio"] = (p.get("glMix") or 50) / 100.0
-        spec["asymmetry"] = p.get("asymmetry") or 0
+        # only a NON-NUMBER falls back to the default (a 0 is a value; A03 Codex round 1)
+        spec["gl_ratio"] = (p["glMix"] if _finite(p.get("glMix")) else 50) / 100.0
+        spec["asymmetry"] = p["asymmetry"] if _finite(p.get("asymmetry")) else 0
         spec["fix_asymmetry"] = bool(p.get("fixAsymmetry"))
         if _finite(p.get("_afAsymMin")):
             spec["asymmetry_min"] = p["_afAsymMin"]
@@ -117,8 +120,8 @@ def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
             spec["asymmetry_max"] = p["_afAsymMax"]
     elif shape == "DS":
         spec["shape"] = "doniach_sunjic"
-        spec["alpha"] = p.get("dsAlpha") or 0.1
-        spec["gamma_asym"] = p.get("dsGamma") or 0.0
+        spec["alpha"] = p["dsAlpha"] if _finite(p.get("dsAlpha")) else 0.1
+        spec["gamma_asym"] = p["dsGamma"] if _finite(p.get("dsGamma")) else 0.0
         spec["fix_alpha"] = bool(p.get("fixDsAlpha"))
         spec["fix_gamma_asym"] = bool(p.get("fixDsGamma"))
     elif shape == "DSG_LA":
@@ -150,6 +153,47 @@ def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
     return spec
 
 
+def apply_backend_params(p: dict, par: dict) -> dict:
+    """Write a server component's fitted parameters onto a page peak dict, in
+    place — the twin of the page's ``_applyBackendParams`` (honours the peak's
+    locks; a shape parameter is written only for the shape that reads it, so
+    a Voigt keeps the ``glMix`` it carries for a later switch to GL). ``par``
+    is ``individual_peaks[].params`` (``{name: {"value": …}}``) or a plain
+    ``{name: value}`` map. Pinned to the page's function, shape by shape, by
+    tests/js/lineshape_roundtrip.test.js."""
+    def val(name):
+        v = par[name]
+        return v["value"] if isinstance(v, dict) else v
+    shape = p.get("shape")
+    if "center" in par and not p.get("fixCenter"):
+        p["center"] = val("center")
+    if "amplitude" in par and not p.get("fixAmplitude"):
+        p["amplitude"] = val("amplitude")
+    if "fwhm" in par and not p.get("fixFwhm"):
+        p["fwhm"] = val("fwhm")
+    if "gl_ratio" in par and shape in ("GL", "asym-GL") and not p.get("fixGlMix"):
+        p["glMix"] = val("gl_ratio") * 100
+    if "asymmetry" in par and shape == "asym-GL" and not p.get("fixAsymmetry"):
+        p["asymmetry"] = val("asymmetry")
+    if "alpha" in par and shape == "DS" and not p.get("fixDsAlpha"):
+        p["dsAlpha"] = val("alpha")
+    if "gamma_asym" in par and shape == "DS" and not p.get("fixDsGamma"):
+        p["dsGamma"] = val("gamma_asym")
+    if "alpha" in par and shape == "DSG_LA" and not p.get("fixLaAlpha"):
+        p["laAlpha"] = val("alpha")
+    if "beta" in par and shape == "DSG_LA" and not p.get("fixLaBeta"):
+        p["laBeta"] = val("beta")
+    if "m_gauss" in par and shape == "DSG_LA" and not p.get("fixLaM"):
+        p["laM"] = val("m_gauss")
+    if "alpha" in par and shape == "LACX" and not p.get("fixCaAlpha"):
+        p["caAlpha"] = val("alpha")
+    if "beta" in par and shape == "LACX" and not p.get("fixCaBeta"):
+        p["caBeta"] = val("beta")
+    if "m" in par and shape == "LACX" and not p.get("fixCaM"):
+        p["caM"] = val("m")
+    return p
+
+
 # ─────────────────────────────────────────────────────────────────────────────
 # ReferenceFit — one saved, fitted spectrum tab
 # ─────────────────────────────────────────────────────────────────────────────
diff --git a/scripts/gen_u4f_battery_fixture.py b/scripts/gen_u4f_battery_fixture.py
index a3720ce..7e0d6ec 100644
--- a/scripts/gen_u4f_battery_fixture.py
+++ b/scripts/gen_u4f_battery_fixture.py
@@ -36,7 +36,10 @@ def main() -> None:
                     skipped.append({"project": rf.project, "name": rf.name,
                                     "reason": reason})
                 continue
-            records.append(refit_record(rf))
+            rec = refit_record(rf)
+            for pk in rec["peaks"]:
+                pk.pop("params", None)   # the fixture pins numbers, not the full model
+            records.append(rec)
     os.makedirs(os.path.dirname(OUT), exist_ok=True)
     with open(OUT, "w") as f:
         json.dump({"records": records, "skipped": skipped}, f, indent=1, sort_keys=True)
diff --git a/templates/index.html b/templates/index.html
index 8393b2c..68500f2 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -5962,7 +5962,7 @@ function renderPeakForm(p) {
       <select id="pk-shape-${p.id}" class="xps-tip-select" onchange="_switchPeakShape(${p.id}, this.value)">
         <option data-tip="Pure Gaussian. Dominated by instrument broadening. Rarely used alone — most XPS peaks need some Lorentzian character." ${p.shape==='Gaussian'?'selected':''}>Gaussian</option>
         <option data-tip="Pure Lorentzian. Dominated by core-hole lifetime. Rarely used alone — too sharp for most real XPS peaks." ${p.shape==='Lorentzian'?'selected':''}>Lorentzian</option>
-        <option data-tip="50/50 Gaussian-Lorentzian mix. Good default starting point for most insulating and polymeric samples." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
+        <option data-tip="Fixed 50/50 Gaussian-Lorentzian mix (η = 0.5, not fitted). A reasonable default for most insulating and polymeric samples; choose GL to fit the mix." ${p.shape==='Voigt'?'selected':''}>Voigt</option>
         <option value="GL" data-tip="Adjustable Gaussian/Lorentzian ratio. Use when you need control over the peak shape — common for oxides, polymers, and organic materials." ${p.shape==='GL'?'selected':''}>GL pseudo-Voigt (&eta; mixing)</option>
         <option value="asym-GL" data-tip="GL with asymmetric broadening. Use for peaks with vibrational fine structure (e.g., C 1s in polymers) or when one side is broader than the other." ${p.shape==='asym-GL'?'selected':''}>Asymmetric GL</option>
         <option value="DS" data-tip="Asymmetric metallic lineshape with tail toward higher BE. Use for metals and conductive samples (e.g., Au, Cu, Fe metal). Not appropriate for insulators or oxides." ${p.shape==='DS'?'selected':''}>Doniach-&Scaron;unji&#263; (&alpha; + &gamma;)</option>
@@ -6223,15 +6223,28 @@ function peakToBackendSpec(p) {
   } else if (shape === 'Lorentzian') {
     spec.shape = 'lorentzian';
   } else if (shape === 'Voigt') {
+    // A03 (2026-09-22): Voigt IS the fixed 50/50 mix the page draws, exports
+    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
+    // the request sent eta FREE from 0.3, so the server fitted a mix the page
+    // never showed — on the 90 committed Voigt targets 60 of 180 components
+    // went to pure Gaussian and 16 to pure Lorentzian, and every area the page
+    // reported for them was the 0.5 curve's, up to 20 % off the fitted one.
+    // Fixed on both sides; use GL to fit the mix.
     spec.shape = 'pseudo_voigt_gl';
-    spec.gl_ratio = 0.3;
+    spec.gl_ratio = 0.5;
+    spec.fix_gl_ratio = true;
   } else if (shape === 'GL') {
     spec.shape = 'pseudo_voigt_gl';
     spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
   } else if (shape === 'asym-GL') {
     spec.shape = 'asymmetric_gl';
-    spec.gl_ratio = (p.glMix || 50) / 100;
-    spec.asymmetry = p.asymmetry || 0;
+    // A03 Codex round 1: `p.glMix || 50` sent a mix of 0 as 50 (and a DS α of 0
+    // as 0.1 below) — a value the page draws but never requested; locked, the
+    // server held the substitute and the drawn curve differed from the fitted
+    // one by 6.9 % (asym-GL) and 8.8 % (DS) of amplitude. Only a NON-NUMBER
+    // falls back to the default.
+    spec.gl_ratio = (Number.isFinite(p.glMix) ? p.glMix : 50) / 100;
+    spec.asymmetry = Number.isFinite(p.asymmetry) ? p.asymmetry : 0;
     spec.fix_asymmetry = !!p.fixAsymmetry;
     // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
     // For non-auto-fit peaks these fields are absent and the backend falls back
@@ -6240,8 +6253,8 @@ function peakToBackendSpec(p) {
     if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
   } else if (shape === 'DS') {
     spec.shape = 'doniach_sunjic';
-    spec.alpha      = p.dsAlpha || 0.1;
-    spec.gamma_asym = p.dsGamma || 0.0;
+    spec.alpha      = Number.isFinite(p.dsAlpha) ? p.dsAlpha : 0.1;
+    spec.gamma_asym = Number.isFinite(p.dsGamma) ? p.dsGamma : 0.0;
     spec.fix_alpha      = !!p.fixDsAlpha;
     spec.fix_gamma_asym = !!p.fixDsGamma;
   } else if (shape === 'DSG_LA') {
@@ -6282,7 +6295,10 @@ function _applyBackendParams(p, par) {
   if (par.center    && !p.fixCenter)    p.center    = par.center.value;
   if (par.amplitude && !p.fixAmplitude) p.amplitude = par.amplitude.value;
   if (par.fwhm      && !p.fixFwhm)     p.fwhm      = par.fwhm.value;
-  if (par.gl_ratio  && !p.fixGlMix)    p.glMix     = par.gl_ratio.value * 100;
+  // glMix is read only by GL / asym-GL; a Voigt's fixed 0.5 (A03) is not a
+  // fitted value and must not overwrite the mix the peak carries for a later
+  // switch to GL.
+  if (par.gl_ratio  && (p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) p.glMix = par.gl_ratio.value * 100;
   if (par.asymmetry && p.shape === 'asym-GL' && !p.fixAsymmetry) p.asymmetry = par.asymmetry.value;
   if (par.alpha && p.shape === 'DS' && !p.fixDsAlpha) p.dsAlpha = par.alpha.value;
   if (par.gamma_asym && p.shape === 'DS' && !p.fixDsGamma) p.dsGamma = par.gamma_asym.value;
@@ -7780,9 +7796,15 @@ function _fitStatLabel(fr) {
 // A LOCAL result is a STARTING POINT, not a reportable result. Measured in
 // unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
 // with Poisson weighting the local engine matches the server on GL-type
-// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) but still differs
-// where the model has Voigt or LA components (server fits the Voigt mix
-// free; caM is integer-held locally) or several minima, and it gives no
+// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
+// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
+// wherever the two engines reach the same minimum (5 of 9 committed U 4f
+// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
+// it still differs on the other 4 U 4f targets (satellite areas up to
+// 8.9 %, 0.77 pp): on one because the LA m is held at its start locally
+// (the gap closes when the server holds m too), on three because the local
+// descent stops at a higher chi2r than the server from the same start
+// (+5 to +13 %, with m held as well) - several minima - and it gives no
 // uncertainties. Unweighted A0-era results differed by more than 100 %.
 // Every site that shows, exports or saves a fit result carries the
 // designation, keyed on persisted identity so reloaded results are labelled.
@@ -7802,7 +7824,7 @@ function _governingProvenance() {
 function _localFitDetail(fr) {
   return _isUnweightedLocal(fr)
     ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
-    : 'It can differ from the server fit for Voigt or LA components, for very weak components (different parameter bounds), or where the model has several minima.';
+    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
 }
 // The designation follows the MODEL, not only a live fit result: parameters
 // imported from a .fit.json that was saved from a local fit are a starting
@@ -11248,7 +11270,7 @@ function _updateROIDisplay(roiRange) {
   el.textContent = `ROI: ${roiRange.min}\u2013${roiRange.max} eV`;
 }
 
-const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for Voigt or LA components or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
+const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
 const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the goodness of fit weighted by data uncertainty. Computed within the ROI range.\n\n\u2022 \u03c7\u00b2 \u2248 1.0 = ideal fit (residuals match expected noise)\n\u2022 \u03c7\u00b2 >> 1 = poor fit or underestimated uncertainties\n\u2022 \u03c7\u00b2 << 1 = possible overfitting or overestimated uncertainties\n\nNote: a low \u03c7\u00b2 does not guarantee a correct model \u2014 always check the R-factor and visually inspect residuals.";
 
 // Wire up custom tooltip for data-xps-tip elements (R-factor, chi-squared, etc.)
@@ -11323,6 +11345,11 @@ function _validateUncertainties() {
       //     by construction → silent
       //   - genuinely locked (vary=false, no expr): user or auto-fit set this lock
       //     → neutral info note pointing at the padlock toggle, not an alarm
+      if (pName === 'gl_ratio' && p.shape === 'Voigt') {
+        // A03: a Voigt's mix is fixed by the SHAPE (η = 0.5), not by a padlock — there is none to unlock.
+        info.push(`<li><b>${_escHtml(p.name)} / mix:</b> fixed at 50/50 by the Voigt shape — choose GL to fit the mix.</li>`);
+        continue;
+      }
       if (pData.vary === false) {
         const isLinked = pData.expr != null && pData.expr !== '';
         if (!isLinked) {
@@ -14283,7 +14310,7 @@ document.addEventListener('mousedown', function(e) {
 <div id="localfit-warn-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
   <div class="xps-modal" style="max-width:460px;border-color:var(--amber,#f59e0b)">
     <h3 style="color:var(--amber,#f59e0b)">&#9888; Local fit used (server unreachable) <button class="btn btn-sm" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">&#x2715;</button></h3>
-    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for Voigt or LA components or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
+    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
     <p style="font-size:11px;color:var(--text2);line-height:1.6;margin:0 0 12px"><strong style="color:var(--text)">Possible causes:</strong><br>
     &bull; The server may be offline or restarting<br>
     &bull; The fit request may have timed out<br>
diff --git a/tests/autofit/battery_common.py b/tests/autofit/battery_common.py
index 4c994a7..ceee984 100644
--- a/tests/autofit/battery_common.py
+++ b/tests/autofit/battery_common.py
@@ -78,24 +78,39 @@ def assert_refit_stability_and_fixture(
     center_tol=CENTER_DRIFT_TOL_EV,
     rel_tol=REL_DRIFT_TOL,
     fixture_rtol=FIXTURE_PARAM_RTOL,
+    stationarity="expert",
 ):
+    """stationarity: what the seeded refit must stay at.
+    "expert" — the saved expert fit itself (the fit is a fixed point of
+    today's fitter). "refit" — a refit FROM the refit (the fitter's own fixed
+    point): for a region whose saved fits were made under a request the page
+    no longer sends (U 4f: Voigt satellites fitted with eta free until A03,
+    2026-09-22), the expert's parameters are those of another model and the
+    "expert" base cannot hold; the frozen fixture still pins the refit's
+    numbers."""
     rec = refit_record(rf)
     assert rec["success"], f"{rf.project}/{rf.name}: seeded refit did not converge"
 
-    by_id = {str(p["id"]): p for p in rf.peaks}
-    for pk in rec["peaks"]:
+    if stationarity == "refit":
+        rec2 = refit_record(rf, start=rec)
+        assert rec2["success"], f"{rf.project}/{rf.name}: refit from the refit did not converge"
+        base, moving, base_name = rec["peaks"], rec2["peaks"], "the refit"
+    else:
+        base, moving, base_name = rf.peaks, rec["peaks"], "expert fit"
+    by_id = {str(p["id"]): p for p in base}
+    for pk in moving:
         saved = by_id[str(pk["id"])]
         dc = abs(pk["center"] - saved["center"])
         dfw = abs(pk["fwhm"] - saved["fwhm"]) / max(saved["fwhm"], 1e-9)
         dam = abs(pk["amplitude"] - saved["amplitude"]) / max(abs(saved["amplitude"]), 1e-9)
         assert dc <= center_tol, (
-            f"{rf.name} peak {pk['id']}: center drifted {dc:.4f} eV from expert fit"
+            f"{rf.name} peak {pk['id']}: center drifted {dc:.4f} eV from {base_name}"
         )
         assert dfw <= rel_tol, (
-            f"{rf.name} peak {pk['id']}: fwhm drifted {dfw:.2%} from expert fit"
+            f"{rf.name} peak {pk['id']}: fwhm drifted {dfw:.2%} from {base_name}"
         )
         assert dam <= rel_tol, (
-            f"{rf.name} peak {pk['id']}: amplitude drifted {dam:.2%} from expert fit"
+            f"{rf.name} peak {pk['id']}: amplitude drifted {dam:.2%} from {base_name}"
         )
 
     exp = expected[(rf.project, rf.name)]
diff --git a/tests/autofit/test_u4f_parity_battery.py b/tests/autofit/test_u4f_parity_battery.py
index fd2f2d2..e18df2a 100644
--- a/tests/autofit/test_u4f_parity_battery.py
+++ b/tests/autofit/test_u4f_parity_battery.py
@@ -6,6 +6,16 @@ battery_common.py).
 
 Regenerate the fixture ONLY for reviewed numerics changes:
     venv/bin/python scripts/gen_u4f_battery_fixture.py
+
+A03 (2026-09-22): the page now sends a Voigt with eta HELD at 0.5 (the mix
+it has always drawn); the 29 expert U 4f fits were saved under the old
+request (eta free from 0.3, ending at pure Gaussian or pure Lorentzian on
+most satellites), so their saved parameters belong to another model and a
+refit under today's request moves the LACX main line's width by up to 7.7 %
+and its centre by up to 8 meV (the satellites' tails changed). The fixture
+was regenerated for that reviewed change, and stationarity is measured
+against a refit FROM the refit (battery_common, stationarity="refit"): the
+fitter's own fixed point, not the pre-A03 save.
 """
 
 import pytest
@@ -48,4 +58,5 @@ def test_eval_parity(rf):
 @pytest.mark.parametrize("rf", _FITS, ids=_IDS)
 def test_refit_stability_and_fixture(rf):
     bc.assert_refit_stability_and_fixture(rf, _EXPECTED,
-                                          fixture_rtol=FIXTURE_RTOL)
+                                          fixture_rtol=FIXTURE_RTOL,
+                                          stationarity="refit")
diff --git a/tests/test_voigt_contract.py b/tests/test_voigt_contract.py
new file mode 100644
index 0000000..e123aad
--- /dev/null
+++ b/tests/test_voigt_contract.py
@@ -0,0 +1,80 @@
+"""A03 (2026-09-22): a "Voigt" component is the fixed 50/50 mix everywhere.
+
+The page draws, integrates, exports and fits locally with eta = 0.5
+(evalPeak; runFitLocal never frees glMix for a Voigt). Until A03 the
+request built by peakToBackendSpec — and its Python twin
+autofit.reference.peak_to_backend_spec — sent pseudo_voigt_gl with
+gl_ratio FREE from 0.3, so the server fitted a mix the page never showed.
+These tests pin the twin and what run_fit does with the request.
+"""
+import numpy as np
+import pytest
+
+import fitting
+from autofit.reference import peak_to_backend_spec
+
+
+def _peak(**over):
+    p = {"id": 1, "name": "sat", "shape": "Voigt", "center": 386.5, "amplitude": 3000.0, "fwhm": 1.4,
+         "glMix": 90, "fixGlMix": False}
+    p.update(over)
+    return p
+
+
+def test_twin_sends_voigt_as_fixed_half_mix():
+    spec = peak_to_backend_spec(_peak(), [_peak()])
+    assert spec["shape"] == "pseudo_voigt_gl"
+    assert spec["gl_ratio"] == 0.5
+    assert spec["fix_gl_ratio"] is True
+    # the page's glMix (kept for a later switch to GL) plays no part
+    assert peak_to_backend_spec(_peak(glMix=5), [_peak(glMix=5)])["gl_ratio"] == 0.5
+
+
+def test_twin_still_sends_gl_mix_free():
+    spec = peak_to_backend_spec(_peak(shape="GL", glMix=72), [_peak(shape="GL", glMix=72)])
+    assert spec["gl_ratio"] == pytest.approx(0.72)
+    assert spec["fix_gl_ratio"] is False
+
+
+def test_twin_sends_a_zero_as_a_zero():
+    """A 0 is a value, not an absent field (Codex round 1: `or 50` / `or 0.1`)."""
+    a = _peak(shape="asym-GL", glMix=0, asymmetry=0)
+    s = peak_to_backend_spec(a, [a])
+    assert s["gl_ratio"] == 0.0 and s["asymmetry"] == 0
+    d = _peak(shape="DS", dsAlpha=0, dsGamma=0)
+    s = peak_to_backend_spec(d, [d])
+    assert s["alpha"] == 0.0 and s["gamma_asym"] == 0.0
+    # a non-number still falls back to the default
+    d2 = _peak(shape="DS", dsAlpha=None)
+    assert peak_to_backend_spec(d2, [d2])["alpha"] == 0.1
+
+
+def test_run_fit_holds_eta_and_returns_the_half_mix_curve():
+    x = np.arange(392.0, 380.0, -0.05)
+    truth = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=3000.0, center=386.5, fwhm=1.4, gl_ratio=0.5)
+    rng = np.random.default_rng(3)
+    y = np.maximum(truth + rng.normal(0, 8, x.size), 0)   # no offset: the request carries no background
+    start = _peak(center=386.65, amplitude=2400.0, fwhm=1.7)
+    spec = peak_to_backend_spec(start, [start])
+    res = fitting.run_fit(x, y, [spec], background_method="none", fit_kws={"method": "least_squares"})
+    assert res["success"] is True
+    ip = res["individual_peaks"][0]
+    gl = ip["params"]["gl_ratio"]
+    assert gl["vary"] is False and gl["value"] == 0.5 and not gl["stderr"]   # lmfit reports 0.0 or None for a held parameter
+    q = ip["params"]
+    drawn = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](np.asarray(res["energy"]), amplitude=q["amplitude"]["value"],
+                                                    center=q["center"]["value"], fwhm=q["fwhm"]["value"], gl_ratio=0.5)
+    np.testing.assert_allclose(np.asarray(ip["y"]), drawn, rtol=0, atol=1e-9 * 3000.0)
+    assert abs(q["center"]["value"] - 386.5) < 0.02 and abs(q["fwhm"]["value"] - 1.4) < 0.03
+
+
+def test_seed_reflects_the_held_eta_not_the_old_free_start():
+    """The request seed hashes each parameter's EFFECTIVE role: a held eta of
+    0.5 and a free eta from 0.3 are different requests and draw differently."""
+    x = np.arange(392.0, 380.0, -0.05)
+    y = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=3000.0, center=386.5, fwhm=1.4, gl_ratio=0.5) + 20.0
+    spec = peak_to_backend_spec(_peak(), [_peak()])
+    old = dict(spec, gl_ratio=0.3, fix_gl_ratio=False)
+    s_new = fitting.run_fit(x, y, [spec], background_method="none", n_perturb=1)["random_seed"]
+    s_old = fitting.run_fit(x, y, [old], background_method="none", n_perturb=1)["random_seed"]
+    assert s_new != s_old

exec
/bin/zsh -lc 'cat docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md; git diff main..HEAD -- CLAUDE.md docs/findings/2026-09-fit-determinacy.md; git log --format=full main..HEAD; cat docs/findings/a03/voigt_eta_summary.txt' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
# A03 — Voigt η identity, parameter-range sweep, U 4f gap re-measurement (2026-09-22)

Branch `fix-voigt-eta-identity` off main `c6f358e`. Owner's brief (2026-09-22):
"A03: Voigt eta identity, parity-harness sweep over each shape's FREE
parameters across their fitted ranges, and re-measure the U 4f gap
afterwards. That re-measurement is the test of whether Batch Fit's
'starting point' label can retire."

## 1. The defect

A "Voigt" component had two definitions:

| site | η |
|---|---|
| `evalPeak` (chart, `_peakArea` → Results, sidebar, Quantify, CSV/XLSX/TSV, figure, stack) | 0.5 |
| `runFitLocal` (Batch Fit, fallback) | 0.5 (glMix never freed for a Voigt) |
| dropdown tooltip, CLAUDE.md lineshape table, parity harness | 0.5 |
| `peakToBackendSpec` → `/api/fit`; Python twin `autofit.reference.peak_to_backend_spec` | `gl_ratio: 0.3`, FREE |

The server fitted η; `_applyBackendParams` wrote it into `glMix`; nothing
read `glMix` for a Voigt. So every number the page produced for a Voigt
after Run Fit was the η = 0.5 curve evaluated with amplitude, width and
centre fitted for a different mix, and the chart's components did not sum
to the envelope (`fittedY` is the server's).

## 2. Measured before deciding

### 2a. The two requests (`scripts/voigt_eta_measure.py` → `docs/findings/a03/voigt_eta_summary.txt`)

The 90 committed targets with a Voigt component (89 U 4f tabs across five
projects and one Cl 2p; 180 Voigt components; 48 saved models and 42 Batch
Fit starts from `scripts/optimizer_disagreement_targets.js`), each fitted
with the page's settings (Trust-Region, `n_perturb: 3`) under BOTH requests,
constructed explicitly by the script (Codex round 1: it used to take the
target file's own Voigt specs as the "old" arm): before A03 (η free from
0.3) and since (η held at 0.5). All 180 fits converged. These rows use the
SERVER's curves and trapezoidal integration on the fitted grid; they
characterise the two requests, not a screen (that is 2b).

| | median | p90 | max |
|---|---:|---:|---:|
| free η of the 180 Voigt components | 60 < 0.01 (pure Gaussian), 16 > 0.99 (pure Lorentzian), 24 within 0.4–0.6 | | |
| the 0.5 curve under the free fit's parameters (what the page drew) vs the curve the server fitted, per Voigt | 13.9 % | 19.2 % | 20.1 % (116 of 180 > 10 %) |
| A. the same, as area fractions per target | 0.96 pp | 1.48 pp | 1.55 pp (35 of 90 > 1 pp) |
| B. fixed-η refit vs that 0.5 curve | 0.34 pp | 0.54 pp | 1.02 pp (1 of 90 > 1 pp) |
| C. fixed-η refit vs the free fit | 0.93 pp | 1.31 pp | 2.04 pp (33 of 90 > 1 pp) |
| χ²ᵣ fixed / free | 1.09 | 1.19 | 5.4 (fixed LOWER on 10 of 90: the free fit was in a worse minimum) |

Row A is the error that was shipping.

### 2b. What a student sees change (`scripts/voigt_saved_vs_refit.js` → `docs/findings/a03/voigt_saved_vs_refit.json`)

Every committed spectrum tab with a saved fit and a Voigt component (55
tabs across six projects, all converged): the PAGE's area of each saved
peak (`evalPeakArray` over the ROI grid × step, as `_peakArea` — a Voigt
at 0.5, an LA at its rounded m, exactly the Results table) against the
page's area of the same peaks after the server refit under the A03 request
(Trust-Region, the page's `n_perturb: 3`, written back through
`_applyBackendParams`).

| | median | p90 | max |
|---|---:|---:|---:|
| area fraction, per tab | 0.35 pp | 0.51 pp | 0.69 pp (0 of 55 > 1 pp) |
| a Voigt component's own area | 4.6 % | 7.6 % | 15.3 % |

That is the release-note number.

## 3. Contract chosen: fixed η = 0.5 on BOTH sides

`peakToBackendSpec` (and the twin) send `gl_ratio: 0.5, fix_gl_ratio: true`
for a Voigt; `_applyBackendParams` writes `glMix` only for GL / asym-GL (a
Voigt keeps the mix it carries for a later switch to GL); the dropdown says
"Fixed 50/50 … choose GL to fit the mix". The other candidate — make the
page honour the fitted η — would have turned "Voigt" into a GL with a
hidden slider and kept, silently, a shape the student never chose (the
owner's rule from the scattered-starts unit: never substitute an
interpretation because it scored better); 76 of 180 fitted η values on a
bound says the data did not determine the parameter in those fits. The
seed hashes each parameter's effective role, so a Voigt request draws
differently from the old one (test `test_seed_reflects_the_held_eta…`).

Sites changed: `peakToBackendSpec`, `_applyBackendParams`, the Voigt
`<option>` tooltip, `_localFitDetail`, `_LOCALFIT_TOOLTIP`, the fallback
banner, `autofit/reference.py`, `scripts/endpoint_avg_sensitivity.py`,
`scripts/bg_window_worked_example.py`, CLAUDE.md, `tests/js/fit_acceptance.test.js`.

## 4. Two harnesses that would have caught it

- `tests/js/lineshape_roundtrip.test.js` (+ `lineshape_roundtrip_backend.py`):
  for every shape, synthetic data from a truth peak, a perturbed start,
  request built by the PAGE's `peakToBackendSpec`, fitted by
  `fitting.run_fit` (no background, Trust-Region), applied by the page's
  `_applyBackendParams`, then `evalPeakArray` on the fitted grid must equal
  `individual_peaks[].y` within 1e-6 of amplitude. Plus: the Voigt request
  and write-back pins, a linked Voigt pair, a locked GL mix, and the Python
  twin deep-equal to the page's builder for every shape and a link. Run
  against main's page it fails on Voigt (0.93 % of amplitude), the Voigt
  pins and the linked pair; on the branch 10 pass, 2 todo (below).
- `tests/js/lineshape_parity.test.js` section (D): each shape's FREE
  parameters swept across `_make_peak_params`'s bounds (η 0–1, asymmetry
  0–1, DS α 0–0.5 / γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β
  0.1–5 / m 0–499, fwhm 0.1–15), one bridge call per shape.
- `tests/test_voigt_contract.py`: the twin, `run_fit` holding η and
  returning the 0.5 curve, the seed.

## 5. What the sweep found

| shape | result |
|---|---|
| Gaussian, Lorentzian, Voigt (glMix 0 and 100 ignored), GL, asym-GL, DS | ≤ 6.1e-16 of amplitude at every combination |
| DS+G, m < 0.001 (delta branch); LACX, m = 0 | exact |
| LACX, m > 0 | up to 0.89 % of amplitude where the kernel is wide against the peak (m = 50 points on a 0.1 eV peak): the tracked discretisation gap (rounded m + 2m+1 kernel on the page vs continuous m on the server). `todo`, the `caM` clamp unit. |
| DS+G, m ≥ 0.05 | the page's `laCasaXPS` quadrature sizes its step to resolve the Lorentzian core (β/3) and never the Gaussian kernel (σ = m/2.355): at β = 2, m = 0.05 the step is 0.67 eV against σ = 0.021 eV and the curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %; at the schema default (α 0.1, β 0.3, m 0.4) 3.9 %. 0 of 865 committed components use DS+G. `todo`; NOT fixed here (scope) — its own unit: port the server's padded-grid convolution to a grid-aware array evaluator, as `dsgDeltaKernel_array` already does for m < 0.001. |

## 6. The re-measurement (`scripts/local_server_gap.js` → `docs/findings/a03/local_server_gap.json`)

W1's 18 Batch Fit targets of the committed UCl4-graphite project, local
engine vs server from the same scaled start, page semantics on both sides.

| set | max Δcentre | max ΔFWHM | max Δarea | max Δfraction |
|---|---:|---:|---:|---:|
| C 1s, 8 of 9 (W1) | 3.8 meV | 0.50 % | 1.40 % | 0.32 pp |
| C 1s, 8 of 9 (A03) | 3.8 meV | 0.50 % | 1.40 % | 0.32 pp |
| C 1s Scan_4 (findings §2, unchanged) | 41.9 meV | 9.0 % | 99.9 % | 15.1 pp |
| U 4f, 9 (W1) | 39.7 meV | 17.2 % | 20.8 % | 1.4 pp |
| U 4f, 9 (A03) | 28.8 meV | 15.8 % | 8.9 % | 0.77 pp |
| U 4f, the 5 where both engines reach the same minimum (Scan_0/1/2/3/7; χ²ᵣ equal to 2–3 digits) | 4.3 meV | 2.6 % | 2.0 % | 0.12 pp |
| U 4f, the other 4 (Scan_4/5/6/8) | 28.8 meV | 15.8 % | 8.9 % | 0.77 pp |

On the 5 agreeing targets the Voigt satellites match within 2 % — the W1
gap on them (7–21 %) was the η identity and is gone. On the other 4 the
server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
7.9 while the local engine holds it at 8, and χ²ᵣ (local/server − 1) is
+9.6 %, +10.1 %, −5.0 % and +12.7 %. Movement in m alone does not
attribute the residual (Codex round 1), so the script has a CONTROL arm:
the server fitted with every LA m HELD at its start, the one thing the
local engine cannot move.

| target | local χ²ᵣ | server χ²ᵣ, m free | server χ²ᵣ, m held | local vs server, m free (Δcentre / ΔFWHM / Δarea / Δfrac) | local vs server, m held |
|---|---:|---:|---:|---|---|
| Scan_4 | 1.970 | 1.798 | 1.878 | 26.6 meV / 5.3 % / 8.3 % / 0.33 pp | 13.7 meV / 3.0 % / 5.0 % / 0.19 pp |
| Scan_5 | 2.393 | 2.174 | 2.187 | 4.7 meV / 4.3 % / 6.7 % / 0.35 pp | 6.5 meV / 3.4 % / 5.3 % / 0.25 pp |
| Scan_6 | 2.657 | 2.798 | 2.634 | 28.8 meV / 15.8 % / 8.9 % / 0.77 pp | 3.7 meV / 1.3 % / 1.4 % / 0.07 pp |
| Scan_8 | 4.656 | 4.129 | 4.118 | 5.7 meV / 5.0 % / 8.3 % / 0.32 pp | 6.3 meV / 4.9 % / 8.1 % / 0.33 pp |

So: on Scan_6 the residual IS the `caM` clamp (holding m on the server
closes it to the agreeing-target envelope). On Scan_5 and Scan_8 holding m
changes nothing — the local engine's descent stops at a χ²ᵣ 10–13 % above
the server's from the same start with the same free parameters: a worse
minimum, the "several minima" case (findings §2 had the mirror image on
C 1s Scan_4, where the local engine found the better one). Scan_4 is half
each. The residual is therefore two things, and `caM` is the smaller.

**Decision: the "starting point" designation STAYS**, on two grounds now:
the `caM` clamp (one target) and the local engine landing in a worse
minimum than Trust-Region on three of nine U 4f targets. The `caM` clamp
remains the next unit; the worse-minimum finding is recorded in findings
§7 for the local-engine work that follows it. Wording in the page updated
to say so (LA components and several minima; no longer Voigt).

## 7. Release-note line

Voigt components are now fitted at the fixed 50/50 mix the page has always
drawn; until now Run Fit let their mix vary on the server and the page
reported the 50/50 curve's area under the other mix's parameters (up to
20 % off per component). Re-fitting a saved project with Voigt components
moves an area fraction by 0.35 pp at the median and 0.69 pp at most on the
55 committed tabs (a Voigt's own area by 4.6 % at the median, 15 % at
most). Use GL to fit the mix. Also fixed: a GL mix of exactly 0 (asym-GL)
or a DS α of exactly 0 was sent to the server as 50 / 0.1.

## 8. Verification

- `tests/test_voigt_contract.py` 4 passed; full `pytest tests/` — see §9.
- JS suite: `node --test tests/js/*.test.js` (the directory form does not
  run in this node): see §9.
- Browser check (`browser_check_a03.py`, dev gunicorn :5151 from the
  worktree, re-run after round 1): the request carries `gl_ratio 0.5, fix_gl_ratio true` for
  both Voigt components; the server returns `vary: false, 0.5`; drawn vs
  fitted curve 1.3e-13 of amplitude for the Voigts (LACX 5.6e-3 — the caM
  rounding); the Results area of a Voigt equals the server curve's to
  0.0000 % (LACX −0.66 %, the same rounding); the chart dataset is the drawn curve; `glMix` unchanged in the
  live model and the saved record; Batch Fit onto U4f Scan_1 converges
  locally; no page errors.

## 9. Codex rounds

**Round 1 (`docs/autofit/codex/a03_voigt_eta_verdict_run{A,B}.md`): NO-GO ×2,
no blocker, converging findings.** Fixed:
1. MAJOR — the measurement script took the target file's own Voigt specs as
   the "old" arm, so a target file regenerated with the A03 builder would
   have made both arms identical. Both requests are now constructed
   explicitly; the generator is named correctly (`.js`); re-run (§2a).
2. MAJOR — the release-note number was a server-curve/trapezoid comparison
   of two refits, not the page's saved numbers against the page's refit
   numbers. Replaced by `scripts/voigt_saved_vs_refit.js` (§2b); the old
   rows relabelled as what they are.
3. MAJOR/MINOR — the builder sent an asym-GL mix of 0 as 50 and a DS α of 0
   as 0.1 (`p.glMix || 50`, `p.dsAlpha || 0.1`; the Python twin likewise);
   locked, the server held the substitute and the drawn curve differed from
   the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders
   (only a non-number falls back); the round-trip test now locks every shape
   parameter at its bounds; the sweep's backend parameters now come THROUGH
   `peakToBackendSpec` rather than a mapping of the harness's own.
4. MINOR — the uncertainty panel told a Voigt's user to "unlock the padlock"
   for a mix that has none: it now says the shape fixes the mix and points
   to GL.
5. MINOR — "χ²ᵣ differs by 8–20 %" was wrong (the four are +9.6, +10.1,
   −5.0, +12.7 %), the comment's "24 %" was 20 %, row A's 1.60 was 1.61 (now
   1.55 with the explicit arms); and attributing the whole residual to the
   `caM` clamp was an inference — the control arm (§6) shows it is one
   target of four.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fzHB038b' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-FdezqDyK' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index c1eeada..ef2bed8 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -110,13 +110,30 @@ tab reordering exists.
 |----|-------------|
 | `Gaussian` | Pure Gaussian |
 | `Lorentzian` | Pure Lorentzian |
-| `Voigt` | Pseudo-Voigt (Thompson et al.), fixed η = 0.5 |
+| `Voigt` | Pseudo-Voigt, fixed η = 0.5 on BOTH sides (A03, 2026-09-22: the request sends `gl_ratio: 0.5, fix_gl_ratio: true`; until then the server fitted η FREE from 0.3 while the page drew, integrated and exported 0.5). Use `GL` to fit the mix. |
 | `GL` | Pseudo-Voigt with adjustable GL mixing (0–100) |
 | `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
 | `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
 | `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
 | `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + integer-kernel Gauss conv. Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |
 
+**What the page draws must be what the server fitted.** Two harnesses pin
+it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
+page's own `peakToBackendSpec`, fits it with `fitting.run_fit`, applies the
+result with `_applyBackendParams` and requires `evalPeakArray` on the fitted
+grid to equal `individual_peaks[].y` for every shape (it also pins the
+Python twin `autofit.reference.peak_to_backend_spec` to the page's builder,
+shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
+each shape's FREE parameters across the fit's bounds. Both were added in A03
+(2026-09-22) after a "Voigt" was found to be fitted with η free while drawn
+at 0.5. Tracked gaps, `todo` in both files: LACX with m > 0 (the page draws
+a rounded integer kernel; the server fits m continuously — the `caM` clamp
+unit) and DS+G with m ≥ 0.05 (the page's quadrature `laCasaXPS` sizes its
+step to the Lorentzian core, not the Gaussian kernel, and is wrong by up to
+80 % of amplitude across the fitted β/m range — 1e52 × at β = 2, m = 0.05;
+0 of 865 committed components use DS+G; its own unit). Details in
+`docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+
 ---
 
 ## Design Rules
@@ -459,16 +476,29 @@ the integer-clamped `caM` is not optimised (carried at its start value).
 
 **A local result is a STARTING POINT, not a reportable result** (keyed on
 `engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
-`_localFitCaveat`). Measured in unit W1: weighted, it matches the server
-on GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) but still
-differs for Voigt components (the server fits their mix free — audit A03),
-LA components (`caM` held), and where the model has several minima
-(both engines' amplitude floor is 0 since unit step (b)). Both engines weight by
+`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
+(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
+generator `scripts/local_server_gap.js`): weighted, it matches the server on
+GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
+components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
+U 4f targets where both engines reach the same minimum every component
+agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
+to 20.8 % area on the Voigt satellites); it still differs on the other 4
+U 4f targets (satellite areas up to 8.9 %, 0.77 pp) for two reasons,
+separated by a control arm (the server with every LA m held at its start):
+on one target the `caM` clamp (`caM` held at its start locally while the
+server fits m continuously; holding m on the server closes the gap), on
+three the local descent stopping at a χ²ᵣ 10–13 % above the server's from
+the same start with the same free parameters — a worse minimum, the
+"several minima" case (both engines' amplitude floor is 0 since unit
+step (b)). Both engines weight by
 √intensity whether the data are counts or CPS (a convention, not a
 calibrated uncertainty for rates); the formula is the same but the inputs
 are not bit-identical, because `uploadToBackend` rounds intensities to
-2 dp before the server weights them. Retire the designation only on a
-re-measurement after A03 and the `caM` clamp. (The amplitude-bound change
+2 dp before the server weights them. A03 is done and the designation
+STAYS on both grounds; the `caM` clamp is the next unit, the worse-minimum
+outcome is recorded for the local-engine work after it, and the label is
+reconsidered only on a re-measurement after both. (The amplitude-bound change
 DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
 implemented: unit step (b), 2026-09-22, below.) The same file records that a
 converged server fit is not ground truth: on a committed C 1s scan the
diff --git a/docs/findings/2026-09-fit-determinacy.md b/docs/findings/2026-09-fit-determinacy.md
index 8ad6c2f..906034b 100644
--- a/docs/findings/2026-09-fit-determinacy.md
+++ b/docs/findings/2026-09-fit-determinacy.md
@@ -255,3 +255,72 @@ whether the result names the slot by its ROLE (so a migrated slot is still
 called C–O). Narrower per-role centre windows are the structural remedy; the
 manual path has only the ± 2 eV default.
 
+
+## 7. A03 (2026-09-22) — a "Voigt" was fitted with a mix the page never drew; the sweep found DS+G's preview wrong across its fitted range
+
+Generators: `scripts/voigt_eta_measure.py` (the 90 committed Voigt targets,
+both requests), `scripts/local_server_gap.js` (the 18 W1 targets),
+section (D) of `tests/js/lineshape_parity.test.js` (the sweep). Plan and
+tables: `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+
+**The Voigt identity.** `peakToBackendSpec` sent a Voigt as
+`pseudo_voigt_gl` with `gl_ratio: 0.3` FREE; `evalPeak` drew η = 0.5;
+`runFitLocal` held 0.5; the dropdown said "50/50"; CLAUDE.md said fixed 0.5.
+On the 90 committed targets with a Voigt component (89 U 4f tabs across five
+projects, one Cl 2p; 180 Voigt components): the server's free η ended at
+pure Gaussian (< 0.01) on 60 of the 180 and pure Lorentzian (> 0.99) on
+16, within 0.4–0.6 on 24. Every area, percentage, chart
+component and export the page produced for those components was the 0.5
+curve under parameters fitted for another mix: that curve vs the fitted one
+median 13.9 %, p90 19.2 %, max 20.1 % (116 of 180 components > 10 %); as
+area fractions median 0.96 pp, max 1.55 pp (35 of 90 targets > 1 pp; server
+curves, trapezoid). Fixed on both sides (η = 0.5 held in the request). What
+a student SEES change on re-fitting a saved project, measured with the
+PAGE's own integration of the saved peaks against the page's integration of
+the refit (`scripts/voigt_saved_vs_refit.js`, 55 committed tabs with a
+saved fit and a Voigt, six projects): an area fraction moves by median
+0.35 pp, p90 0.51 pp, max 0.69 pp (none > 1 pp); a Voigt's own area by
+median 4.6 %, max 15.3 %. The refit vs the server's own free-η fit is
+median 0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9 % (the mix is one
+parameter fewer). The alternative — honour the fitted η on the page — would
+have made "Voigt" a GL with a hidden slider and silently kept a shape the
+student had not chosen; 76 of 180 fitted values sitting on a bound says the
+parameter was not determined by the data in those fits anyway. The same
+review found the builder sending an asym-GL mix of exactly 0 as 50 and a
+DS α of exactly 0 as 0.1 (`||` defaults); locked, the drawn curve differed
+from the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders.
+
+**The re-measurement (W1 methodology, 18 targets).** C 1s unchanged (8 of 9
+within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is the §2 finding). U 4f,
+W1 → A03: max Δcentre 39.7 → 28.8 meV, ΔFWHM 17.2 → 15.8 %, Δarea 20.8 →
+8.9 %, Δfraction 1.4 → 0.77 pp. On the 5 of 9 targets where both engines
+reach the same minimum (χ²ᵣ equal to 2–3 digits) every component is within
+4.3 meV, 2.6 %, 2.0 %, 0.12 pp — the Voigt gap is gone. On the other 4 the
+server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
+7.9 while the local engine holds it; χ²ᵣ (local/server − 1) is +9.6, +10.1,
+−5.0 and +12.7 %, and the satellites, which share the region, differ by up
+to 8.9 % in area. A control arm (the server with every LA m HELD at its
+start) attributes it: on Scan_6 holding m closes the gap to 3.7 meV /
+1.3 % / 1.4 % / 0.07 pp — that one IS the `caM` clamp; on Scan_5 and Scan_8
+holding m changes nothing and the local engine's χ²ᵣ stays 10–13 % above
+the server's from the same start with the same free parameters — a WORSE
+MINIMUM (the mirror image of §2, where the local engine found the better
+one on C 1s Scan_4); Scan_4 is half each. The "starting point" label stays
+on both grounds; the `caM` clamp is the next unit, and the local engine's
+worse-minimum outcome on 3 of 9 U 4f targets is a finding for the
+local-engine work after it.
+
+**The sweep.** Gaussian, Lorentzian, Voigt, GL, asym-GL and DS agree with
+the server to 1e-15 across every bound. LACX with m > 0: up to 0.89 % of
+amplitude when the kernel is wide against the peak (the tracked
+discretisation gap). DS+G with m ≥ 0.05: the page's `laCasaXPS` quadrature
+uses a step of 2·(6σ + 50β)/max(300, ⌈2·(6σ + 50β)/(β/3)⌉) — sized to the
+Lorentzian core, blind to the Gaussian kernel — so at β = 2, m = 0.05 the
+step is 0.67 eV against σ = 0.021 eV, the kernel weights sample nothing,
+and the page's curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's
+area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
+865 committed components use DS+G, so no saved figure is affected; it is the
+fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
+recorded as its own unit. The general lesson repeats §6's: a harness that
+evaluates one representative point per shape proves nothing about the range
+the optimiser can reach.
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-q7wSZ1o7' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Yc6HuKCI' (errno=Operation not permitted)
commit 4d623f5ef2b5b4426048ef6cfbb30dc2ded509fb
Author: Skye Fortier <skyefortier@gmail.com>
Commit: Skye Fortier <skyefortier@gmail.com>

    fix(A03): Codex round 1 (NO-GO x2) - explicit measurement arms; release-note number from the page's own numbers; builders sent a mix or DS alpha of exactly 0 as the default; Voigt uncertainty note; caM attribution by a control arm
    
    - scripts/voigt_eta_measure.py constructs both requests explicitly (the
      target file's own Voigt specs were the "old" arm, which a regenerated
      file would have made identical); re-run: 60 of 180 pure Gaussian, 16
      pure Lorentzian; the 0.5 curve vs the fitted one median 13.9 %, max 20.1 %.
    - scripts/voigt_saved_vs_refit.js: the page's integration of the saved
      peaks against the page's integration of the refit (55 committed tabs):
      an area fraction moves median 0.35 pp, max 0.69 pp, none > 1 pp - the
      release-note number.
    - peakToBackendSpec and its Python twin sent an asym-GL mix of 0 as 50 and
      a DS alpha of 0 as 0.1 (`||` defaults); locked, the drawn curve differed
      from the fitted one by 6.9 % / 8.8 % of amplitude. Only a non-number
      falls back now. The round-trip test locks every shape parameter at its
      bounds; the parity sweep takes its backend parameters THROUGH
      peakToBackendSpec.
    - Uncertainty panel: a Voigt's held mix is the shape's contract, not a
      padlock to unlock; it now says so and points to GL.
    - local_server_gap.js gained a control arm (server with every LA m held):
      Scan_6's residual is the caM clamp; Scan_5/8's is the local engine
      stopping in a worse minimum (chi2r +10-13 % with m held too); Scan_4
      half each. Docs and CLAUDE.md corrected accordingly; the wrong "8-20 %",
      "24 %" and "1.60 pp" figures fixed; round-1 verdicts archived.
    
    Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>

commit 712e1363af5f44685a3c4f43722ecc9584d79709
Author: Skye Fortier <skyefortier@gmail.com>
Commit: Skye Fortier <skyefortier@gmail.com>

    fix(A03): a Voigt is the fixed 50/50 mix on BOTH sides; page->server->page identity test; parameter-range sweep; U 4f gap re-measured
    
    Until now peakToBackendSpec (and its Python twin) sent a "Voigt" as
    pseudo_voigt_gl with gl_ratio 0.3 FREE while the page drew, integrated,
    exported and fitted locally eta = 0.5. On the 90 committed Voigt targets
    (180 components) the server's eta ended at pure Gaussian on 46 and pure
    Lorentzian on 17, and every displayed Voigt area was the 0.5 curve's under
    the other mix's parameters: median 11.8 % off, max 20.1 %. The request now
    sends gl_ratio 0.5 held; _applyBackendParams writes glMix only for GL /
    asym-GL; the dropdown says fixed 50/50, use GL to fit the mix. What a
    student sees change on re-fitting a saved project: median 0.30 pp, max
    1.02 pp (scripts/voigt_eta_measure.py, docs/findings/a03/).
    
    tests/js/lineshape_roundtrip.test.js: for every shape, the request built by
    the page's own builder, fitted by fitting.run_fit, applied by the page's own
    write-back, then evalPeakArray on the fitted grid must equal
    individual_peaks[].y (fails on main's Voigt at 0.93 % of amplitude); pins
    the Python twins peak_to_backend_spec and the new apply_backend_params to
    the page, shape by shape. Parity harness section (D): each shape's free
    parameters swept across the fit's bounds. Found: DS+G's page quadrature
    (laCasaXPS) is wrong across its fitted beta/m range (1e52 x amplitude at
    beta 2 / m 0.05; 0 of 865 committed components use DS+G) - recorded as its
    own unit, not fixed here; LACX m > 0 up to 0.89 % (tracked, caM clamp).
    
    Re-measured (scripts/local_server_gap.js, W1's 18 targets): U 4f max
    area gap 20.8 -> 8.9 %, fraction 1.4 -> 0.77 pp; on the 5 of 9 targets
    where both engines reach the same minimum every component within 4.3 meV /
    2.6 % / 2.0 % / 0.12 pp; the residual is the held caM (server's m moved
    2.7-10.0 from 8). The "starting point" designation STAYS; caveat wording
    now names LA components and several minima.
    
    U 4f parity battery: the 29 expert fits were saved under the old request;
    fixture regenerated (reviewed numerics change) and stationarity measured
    against a refit FROM the refit (battery_common stationarity="refit").
    
    Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
targets 90, both fits converged 90
free eta of 180 Voigt components: 60 at 0 (pure Gaussian), 16 at 1 (pure Lorentzian), 24 within 0.4–0.6
per-Voigt-component DISPLAYED area vs the fitted curve (%): median 13.89, p90 19.18, max 20.11; > 10 % on 116 of 180; displayed high (eta < 0.5) 110, low 70
A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.48, max 1.55; > 1 pp on 35 targets
B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: median 0.34, p90 0.54, max 1.02; > 1 pp on 1 targets
C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 33 targets
chi2r fixed/free: median 1.09, p90 1.19, max 5.39; fixed lower on 10 targets (the free fit in a worse minimum)

exec
/bin/zsh -lc 'cat tests/js/lineshape_roundtrip.test.js tests/js/lineshape_roundtrip_backend.py; git diff main..HEAD -- tests/js/lineshape_parity.test.js tests/js/lineshape_parity_backend.py; ls -d .venv*; rg --files /Users/skyefortier -g AGENTS.md 2>/dev/null' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 2 in 7553ms:
exec
/bin/zsh -lc 'cat scripts/voigt_saved_vs_refit.js scripts/local_server_gap.js tests/js/local_lm_server_parity_backend.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
#!/usr/bin/env node
// A03 (Codex round 1): what a student SEES change when a saved project with
// Voigt components is re-fitted under the fixed-eta request — measured with
// the PAGE's own numbers on both sides. For every committed spectrum tab
// that carries a saved fit and a Voigt component: the page's area of each
// saved peak (evalPeakArray over the ROI grid × step, as _peakArea; a Voigt
// at eta 0.5, an LA at its rounded m — exactly the Results table) versus the
// page's area of the same peaks after the server refit (the page's request
// builder, Trust-Region, the page's n_perturb 3, parameters written back
// through the page's _applyBackendParams). Usage: node scripts/voigt_saved_vs_refit.js [out.json]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
  throw new Error('unbalanced ' + name);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS',
  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array', 'evalPeakArray', 'getPeak', '_applyBackendParams'];
const state = { peaks: [] };
const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams };')(state);
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const DATA = path.join(ROOT, 'docs/autofit/test_data');
const area = (be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return fns.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), n_perturb: 3, targets: [] };
for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
  for (const t of tabs) {
    if (!t.fitResult || !(t.peaks || []).some(p => p.shape === 'Voigt')) continue;
    const ui = t.ui || {};
    const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
    if (!Number.isFinite(roiMin) || !Number.isFinite(roiMax) || !ui.bgType) continue;
    const be = [], inten = [];
    t.rawBE.forEach((b, i) => { const c = b - (t.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(t.rawIntensity[i]); } });
    if (be.length < 10) continue;
    const saved = JSON.parse(JSON.stringify(t.peaks));
    let srv;
    try {
      srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be, inten, peaks: saved, ui, n_perturb: 3 }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    } catch (e) { out.targets.push({ project: zp, tab: t.name, error: String(e.message).slice(0, 200) }); continue; }
    const refit = JSON.parse(JSON.stringify(saved));
    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; fns._applyBackendParams(refit[i], par); });
    const aS = saved.map(p => area(be, p)), aR = refit.map(p => area(be, p));
    const tS = aS.reduce((s, v) => s + v, 0), tR = aR.reduce((s, v) => s + v, 0);
    const comps = saved.map((p, i) => ({ name: p.name, shape: p.shape, saved_area: aS[i], refit_area: aR[i],
      dArea_pct: aS[i] ? 100 * (aR[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aR[i] / tR - aS[i] / tS) }));
    const rec = { project: zp, tab: t.name, server_success: srv.success, chi2r: srv.chi2r,
      max_dFrac_pp: Math.max(...comps.map(c => Math.abs(c.dFrac_pp))),
      max_voigt_dArea_pct: Math.max(...comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct))), comps };
    out.targets.push(rec);
    console.error(zp.slice(0, 28), t.name, 'server', srv.success, 'max Δfrac', rec.max_dFrac_pp.toFixed(2), 'pp, max Voigt Δarea', rec.max_voigt_dArea_pct.toFixed(1), '%');
  }
}
const ok = out.targets.filter(r => r.server_success);
const q = v => { v = [...v].sort((a, b) => a - b); return { median: v[Math.floor(v.length / 2)], p90: v[Math.floor(0.9 * (v.length - 1))], max: v[v.length - 1] }; };
out.summary = { n_tabs: out.targets.length, n_converged: ok.length, dFrac_pp: q(ok.map(r => r.max_dFrac_pp)), gt_1pp: ok.filter(r => r.max_dFrac_pp > 1).length, voigt_dArea_pct: q(ok.map(r => r.max_voigt_dArea_pct)) };
console.error(JSON.stringify(out.summary));
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/voigt_saved_vs_refit.json'), JSON.stringify(out, null, 1));
#!/usr/bin/env node
// Local engine vs server from the SAME scaled start on the committed
// UCl4-graphite project's Batch Fit targets (unit W1's methodology,
// 2026-09-18; re-run for A03, 2026-09-22 — the test of whether Batch Fit's
// "starting point" label can retire). Every C1s Scan_N and U4f Scan_N tab is
// a target; the source is the scan the student fitted ('C1s Scan' / 'U4f
// Scan'); the start is the source's model with amplitudes scaled to the
// target's maximum (what runPropagation does); both engines fit that start
// on the same background (the page's computeBackgroundCore; the server
// recomputes its own from the same settings). Differences are evaluated with
// the PAGE's semantics — the server's parameters written onto a copy of the
// start with _applyBackendParams, areas as _peakArea (evalPeakArray over the
// ROI grid × step) — so the comparison is about parameters, not about which
// side integrated. A third arm (Codex round 1: "movement in m alone does not
// establish that the residual is the local clamp") fits the server with every
// LA m HELD at its start (fixCaM on the copy), the one thing the local
// engine cannot move: if that arm agrees with the local engine where the
// free-m arm did not, the attribution is established by a controlled
// comparison, not inferred. Usage: node scripts/local_server_gap.js [out.json]
const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8'); const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('missing ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); }
  throw new Error('unbalanced ' + name);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_applyBackendParams'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
function makeEnv() {
  const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const f = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, _applyBackendParams };');
  return { ...f(document, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => new Array(be.length).fill(0)), state };
}
const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
const PROJECT = path.join(ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(ROOT, 'static/js/batch_propagation.js'));
const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 1 << 26 }));
function target(env, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  return { be, inten, bg, bgSub: inten.map((v, i) => v - bg[i]), ui, start: cloned };
}
const area = (env, be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return env.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
const out = { generated: new Date().toISOString(), regions: {} };
for (const [region, sourceName] of [['C1s', 'C1s Scan'], ['U4f', 'U4f Scan']]) {
  const names = tabs.filter(t => new RegExp('^' + sourceName.replace(' ', ' ') + '_\\d+$').test(t.name)).map(t => t.name);
  out.regions[region] = [];
  for (const name of names) {
    const env = makeEnv(); const T = target(env, sourceName, name);
    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
    const serverFit = startPeaks => {
      const r = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: startPeaks, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
      const peaks = JSON.parse(JSON.stringify(startPeaks));
      r.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(peaks[i], par); });
      return { r, peaks };
    };
    const { r: srv, peaks: serverPeaks } = serverFit(T.start);
    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, fixCaM: true } : p);
    const { r: srvHeld, peaks: serverHeldPeaks } = serverFit(heldStart);
    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p)), aH = serverHeldPeaks.map(p => area(env, T.be, p));
    const tL = aL.reduce((s, v) => s + v, 0), tS = aS.reduce((s, v) => s + v, 0), tH = aH.reduce((s, v) => s + v, 0);
    const comps = localPeaks.map((p, i) => ({ name: p.name, shape: p.shape, linked: !!p.linked,
      dCenter_meV: 1000 * (p.center - serverPeaks[i].center), dFwhm_pct: 100 * (p.fwhm / serverPeaks[i].fwhm - 1),
      dArea_pct: aS[i] ? 100 * (aL[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aL[i] / tL - aS[i] / tS),
      // the held-m arm: local vs server with every LA m held at its start
      held_dCenter_meV: 1000 * (p.center - serverHeldPeaks[i].center), held_dFwhm_pct: 100 * (p.fwhm / serverHeldPeaks[i].fwhm - 1),
      held_dArea_pct: aH[i] ? 100 * (aL[i] / aH[i] - 1) : null, held_dFrac_pp: 100 * (aL[i] / tL - aH[i] / tH),
      local: { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, area: aL[i] }, server: { center: serverPeaks[i].center, fwhm: serverPeaks[i].fwhm, amplitude: serverPeaks[i].amplitude, area: aS[i], glMix: serverPeaks[i].glMix, caM: serverPeaks[i].caM },
      server_held_m: { center: serverHeldPeaks[i].center, fwhm: serverHeldPeaks[i].fwhm, amplitude: serverHeldPeaks[i].amplitude, area: aH[i], caM: serverHeldPeaks[i].caM } }));
    const mx = f => Math.max(...comps.map(c => Math.abs(c[f]) || 0));
    out.regions[region].push({ target: name, local_success: loc.success, local_chi2r: env.state.fitResult && env.state.fitResult.chiReduced, server_success: srv.success, server_chi2r: srv.chi2r,
      server_held_m_success: srvHeld.success, server_held_m_chi2r: srvHeld.chi2r,
      max_dCenter_meV: mx('dCenter_meV'), max_dFwhm_pct: mx('dFwhm_pct'), max_dArea_pct: mx('dArea_pct'), max_dFrac_pp: mx('dFrac_pp'),
      held_max_dCenter_meV: mx('held_dCenter_meV'), held_max_dFwhm_pct: mx('held_dFwhm_pct'), held_max_dArea_pct: mx('held_dArea_pct'), held_max_dFrac_pp: mx('held_dFrac_pp'), comps });
    console.error(region, name, 'local', loc.success, (env.state.fitResult || {}).chiReduced && env.state.fitResult.chiReduced.toFixed(3), 'server', srv.success, srv.chi2r.toFixed(3), 'max Δcentre', mx('dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('dFwhm_pct').toFixed(2), '%, Δarea', mx('dArea_pct').toFixed(2), '%, Δfrac', mx('dFrac_pp').toFixed(2), 'pp',
      '| m held: server', srvHeld.chi2r.toFixed(3), 'Δcentre', mx('held_dCenter_meV').toFixed(1), 'meV, ΔFWHM', mx('held_dFwhm_pct').toFixed(2), '%, Δarea', mx('held_dArea_pct').toFixed(2), '%, Δfrac', mx('held_dFrac_pp').toFixed(2), 'pp');
  }
}
fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/local_server_gap.json'), JSON.stringify(out, null, 1));
"""Bridge for tests/js/local_lm_descent.test.js: run the SERVER fit (fitting.run_fit,
Poisson weights, Trust-Region) from the same scaled starting model the local
engine received, so the JS test can pin local-vs-server parity (unit W1).
stdin: {be, inten, peaks (frontend peak objects), ui}; argv[1]: repo root.
"""
import json
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import fitting  # noqa: E402
from autofit.reference import peak_to_backend_spec  # noqa: E402

d = json.load(sys.stdin)
x = np.asarray(d["be"], float)
y = np.asarray(d["inten"], float)
ui = d["ui"]
specs = [peak_to_backend_spec(p, d["peaks"]) for p in d["peaks"]]
lo, hi = sorted([float(ui["bgStart"]), float(ui["bgEnd"])])
idx = [i for i, b in enumerate(x) if lo <= b <= hi]
res = fitting.run_fit(x, y, specs, background_method=ui["bgType"], bg_start_idx=idx[0], bg_end_idx=idx[-1] + 1,
                      endpoint_avg=int(ui.get("endpointAvg") or 1), fit_kws={"method": "least_squares"},
                      n_perturb=int(d.get("n_perturb") or 0))   # the page sends 3; the W1 test sends none
print(json.dumps({"success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"],
                  "peaks": [{k: v["value"] for k, v in ip["params"].items()} for ip in res["individual_peaks"]]}))

exec
/bin/zsh -lc 'cat scripts/voigt_eta_measure.py; cat docs/findings/a03/voigt_eta_summary.txt; cat docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
#!/usr/bin/env python3
"""A03 (2026-09-22): what the free-eta Voigt request did, on the committed targets.

Until A03 the page sent a "Voigt" component as pseudo_voigt_gl with gl_ratio
FREE from 0.3 while it drew, integrated and exported eta = 0.5. For every
committed target with a Voigt component this script fits the request BOTH
ways with the page's settings (Trust-Region, n_perturb 3) — (free) as sent
before A03, (fixed) eta held at 0.5 as sent since — and compares three
things per target:
  A. the 0.5 curve under the free fit's parameters (what the page drew for
     that fit) against the free fit's own curve — the reporting error that
     shipped, per component and as area fractions;
  B. the fixed fit against that 0.5 curve;
  C. the fixed fit against the free fit.
All three use the SERVER's curves and trapezoidal integration on the fitted
grid (non-Voigt components as the server fitted them); they characterise
the two requests, not a screen. The student-visible change on re-fitting a
SAVED project — the page's own integration of the saved peaks against the
page's integration of the refit — is scripts/voigt_saved_vs_refit.js.

Usage:
  python scripts/voigt_eta_measure.py targets.json out_dir shard n_shards   # one shard
  python scripts/voigt_eta_measure.py --summary out_dir                     # the numbers
targets.json is the optimizer-disagreement target file (uncommitted; built by
scripts/optimizer_disagreement_targets.js from the committed projects with
the page's CURRENT request builder). Both arms are constructed here
explicitly from the target's shapes — the target file's own Voigt specs are
never used as either baseline, so the numbers do not depend on which
builder produced the file (A03 Codex round 1).
"""
import copy
import glob
import json
import os
import statistics as st
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import fitting  # noqa: E402

warnings.filterwarnings("ignore")


def _pack(r):
    return {"success": r["success"], "chi2r": r["statistics"]["reduced_chi_square"], "energy": r["energy"],
            "peaks": [{"id": ip["id"], "y": ip["y"], "params": {k: v.get("value") for k, v in ip["params"].items()}}
                      for ip in r["individual_peaks"]]}


def measure(targets_path, out_dir, shard, n_shards):
    targets = json.load(open(targets_path))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"shard{shard}.jsonl"), "w") as out:
        for k, t in enumerate(targets):
            if k % n_shards != shard:
                continue
            vidx = [i for i, sh in enumerate(t["shapes"]) if sh == "Voigt"]
            if not vidx:
                continue
            b = t["background"]
            kw = dict(background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
                      endpoint_avg=b["endpoint_avg"], n_perturb=3, fit_kws={"method": "least_squares"})
            x = np.asarray(t["be"], float)
            y = np.round(np.asarray(t["inten"], float), 2)   # the upload rounds to 2 dp
            free = copy.deepcopy(t["specs"])
            fixed = copy.deepcopy(t["specs"])
            for i in vidx:
                free[i]["gl_ratio"] = 0.3                     # the request before A03: eta free from 0.3
                free[i]["fix_gl_ratio"] = False
                fixed[i]["gl_ratio"] = 0.5                    # the request since A03: eta held at 0.5
                fixed[i]["fix_gl_ratio"] = True
            rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"],
                   "voigt_ids": [str(t["specs"][i]["id"]) for i in vidx]}
            for lab, specs in (("free", free), ("fixed", fixed)):
                try:
                    rec[lab] = _pack(fitting.run_fit(x, y, specs, **kw))
                except Exception as e:  # noqa: BLE001 — a failed fit is a row, not a crash
                    rec[lab] = {"error": str(e)[:160]}
            out.write(json.dumps(rec) + "\n")
            out.flush()


def summary(out_dir):
    recs = [json.loads(l) for f in sorted(glob.glob(os.path.join(out_dir, "shard*.jsonl"))) for l in open(f)]
    ok = [r for r in recs if "peaks" in r["free"] and "peaks" in r["fixed"] and r["free"]["success"] and r["fixed"]["success"]]
    print(f"targets {len(recs)}, both fits converged {len(ok)}")
    area = lambda x, y: float(abs(np.trapezoid(y, x)))  # noqa: E731
    dA, dB, dC, comp = [], [], [], []
    etas = []
    chi_ratio = []
    for r in ok:
        x = np.asarray(r["free"]["energy"])
        vids = set(r["voigt_ids"])
        a_free, a_disp = [], []
        for pk in r["free"]["peaks"]:
            a = area(x, np.asarray(pk["y"]))
            a_free.append(a)
            if str(pk["id"]) in vids:
                q = pk["params"]
                etas.append(q["gl_ratio"])
                yd = fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=q["amplitude"], center=q["center"], fwhm=q["fwhm"], gl_ratio=0.5)
                ad = area(x, yd)
                a_disp.append(ad)
                if a > 0:
                    comp.append(100 * (ad - a) / a)
            else:
                a_disp.append(a)
        a_fix = [area(x, np.asarray(pk["y"])) for pk in r["fixed"]["peaks"]]
        frac = lambda A: [100 * v / sum(A) for v in A]  # noqa: E731
        Ff, Fd, Fx = frac(a_free), frac(a_disp), frac(a_fix)
        dA.append(max(abs(a - b) for a, b in zip(Fd, Ff)))
        dB.append(max(abs(a - b) for a, b in zip(Fx, Fd)))
        dC.append(max(abs(a - b) for a, b in zip(Fx, Ff)))
        chi_ratio.append(r["fixed"]["chi2r"] / r["free"]["chi2r"])

    def q(v):
        v = sorted(v)
        return f"median {st.median(v):.2f}, p90 {v[int(0.9 * len(v))]:.2f}, max {v[-1]:.2f}"

    print(f"free eta of {len(etas)} Voigt components: {sum(e < 0.01 for e in etas)} at 0 (pure Gaussian), "
          f"{sum(e > 0.99 for e in etas)} at 1 (pure Lorentzian), {sum(0.4 <= e <= 0.6 for e in etas)} within 0.4–0.6")
    e = [abs(c) for c in comp]
    print(f"per-Voigt-component DISPLAYED area vs the fitted curve (%): {q(e)}; > 10 % on {sum(v > 10 for v in e)} of {len(e)}; "
          f"displayed high (eta < 0.5) {sum(c > 0 for c in comp)}, low {sum(c < 0 for c in comp)}")
    print(f"A. displayed vs free-fit fractions, max |delta| pp per target: {q(dA)}; > 1 pp on {sum(v > 1 for v in dA)} targets")
    print(f"B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: {q(dB)}; > 1 pp on {sum(v > 1 for v in dB)} targets")
    print(f"C. fixed refit vs free fit, max |delta| pp: {q(dC)}; > 1 pp on {sum(v > 1 for v in dC)} targets")
    print(f"chi2r fixed/free: {q(chi_ratio)}; fixed lower on {sum(v < 1 for v in chi_ratio)} targets (the free fit in a worse minimum)")


if __name__ == "__main__":
    if sys.argv[1] == "--summary":
        summary(sys.argv[2])
    else:
        measure(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
targets 90, both fits converged 90
free eta of 180 Voigt components: 60 at 0 (pure Gaussian), 16 at 1 (pure Lorentzian), 24 within 0.4–0.6
per-Voigt-component DISPLAYED area vs the fitted curve (%): median 13.89, p90 19.18, max 20.11; > 10 % on 116 of 180; displayed high (eta < 0.5) 110, low 70
A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.48, max 1.55; > 1 pp on 35 targets
B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: median 0.34, p90 0.54, max 1.02; > 1 pp on 1 targets
C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 33 targets
chi2r fixed/free: median 1.09, p90 1.19, max 5.39; fixed lower on 10 targets (the free fit in a worse minimum)
# A03 — Voigt η identity, parameter-range sweep, U 4f gap re-measurement (2026-09-22)

Branch `fix-voigt-eta-identity` off main `c6f358e`. Owner's brief (2026-09-22):
"A03: Voigt eta identity, parity-harness sweep over each shape's FREE
parameters across their fitted ranges, and re-measure the U 4f gap
afterwards. That re-measurement is the test of whether Batch Fit's
'starting point' label can retire."

## 1. The defect

A "Voigt" component had two definitions:

| site | η |
|---|---|
| `evalPeak` (chart, `_peakArea` → Results, sidebar, Quantify, CSV/XLSX/TSV, figure, stack) | 0.5 |
| `runFitLocal` (Batch Fit, fallback) | 0.5 (glMix never freed for a Voigt) |
| dropdown tooltip, CLAUDE.md lineshape table, parity harness | 0.5 |
| `peakToBackendSpec` → `/api/fit`; Python twin `autofit.reference.peak_to_backend_spec` | `gl_ratio: 0.3`, FREE |

The server fitted η; `_applyBackendParams` wrote it into `glMix`; nothing
read `glMix` for a Voigt. So every number the page produced for a Voigt
after Run Fit was the η = 0.5 curve evaluated with amplitude, width and
centre fitted for a different mix, and the chart's components did not sum
to the envelope (`fittedY` is the server's).

## 2. Measured before deciding

### 2a. The two requests (`scripts/voigt_eta_measure.py` → `docs/findings/a03/voigt_eta_summary.txt`)

The 90 committed targets with a Voigt component (89 U 4f tabs across five
projects and one Cl 2p; 180 Voigt components; 48 saved models and 42 Batch
Fit starts from `scripts/optimizer_disagreement_targets.js`), each fitted
with the page's settings (Trust-Region, `n_perturb: 3`) under BOTH requests,
constructed explicitly by the script (Codex round 1: it used to take the
target file's own Voigt specs as the "old" arm): before A03 (η free from
0.3) and since (η held at 0.5). All 180 fits converged. These rows use the
SERVER's curves and trapezoidal integration on the fitted grid; they
characterise the two requests, not a screen (that is 2b).

| | median | p90 | max |
|---|---:|---:|---:|
| free η of the 180 Voigt components | 60 < 0.01 (pure Gaussian), 16 > 0.99 (pure Lorentzian), 24 within 0.4–0.6 | | |
| the 0.5 curve under the free fit's parameters (what the page drew) vs the curve the server fitted, per Voigt | 13.9 % | 19.2 % | 20.1 % (116 of 180 > 10 %) |
| A. the same, as area fractions per target | 0.96 pp | 1.48 pp | 1.55 pp (35 of 90 > 1 pp) |
| B. fixed-η refit vs that 0.5 curve | 0.34 pp | 0.54 pp | 1.02 pp (1 of 90 > 1 pp) |
| C. fixed-η refit vs the free fit | 0.93 pp | 1.31 pp | 2.04 pp (33 of 90 > 1 pp) |
| χ²ᵣ fixed / free | 1.09 | 1.19 | 5.4 (fixed LOWER on 10 of 90: the free fit was in a worse minimum) |

Row A is the error that was shipping.

### 2b. What a student sees change (`scripts/voigt_saved_vs_refit.js` → `docs/findings/a03/voigt_saved_vs_refit.json`)

Every committed spectrum tab with a saved fit and a Voigt component (55
tabs across six projects, all converged): the PAGE's area of each saved
peak (`evalPeakArray` over the ROI grid × step, as `_peakArea` — a Voigt
at 0.5, an LA at its rounded m, exactly the Results table) against the
page's area of the same peaks after the server refit under the A03 request
(Trust-Region, the page's `n_perturb: 3`, written back through
`_applyBackendParams`).

| | median | p90 | max |
|---|---:|---:|---:|
| area fraction, per tab | 0.35 pp | 0.51 pp | 0.69 pp (0 of 55 > 1 pp) |
| a Voigt component's own area | 4.6 % | 7.6 % | 15.3 % |

That is the release-note number.

## 3. Contract chosen: fixed η = 0.5 on BOTH sides

`peakToBackendSpec` (and the twin) send `gl_ratio: 0.5, fix_gl_ratio: true`
for a Voigt; `_applyBackendParams` writes `glMix` only for GL / asym-GL (a
Voigt keeps the mix it carries for a later switch to GL); the dropdown says
"Fixed 50/50 … choose GL to fit the mix". The other candidate — make the
page honour the fitted η — would have turned "Voigt" into a GL with a
hidden slider and kept, silently, a shape the student never chose (the
owner's rule from the scattered-starts unit: never substitute an
interpretation because it scored better); 76 of 180 fitted η values on a
bound says the data did not determine the parameter in those fits. The
seed hashes each parameter's effective role, so a Voigt request draws
differently from the old one (test `test_seed_reflects_the_held_eta…`).

Sites changed: `peakToBackendSpec`, `_applyBackendParams`, the Voigt
`<option>` tooltip, `_localFitDetail`, `_LOCALFIT_TOOLTIP`, the fallback
banner, `autofit/reference.py`, `scripts/endpoint_avg_sensitivity.py`,
`scripts/bg_window_worked_example.py`, CLAUDE.md, `tests/js/fit_acceptance.test.js`.

## 4. Two harnesses that would have caught it

- `tests/js/lineshape_roundtrip.test.js` (+ `lineshape_roundtrip_backend.py`):
  for every shape, synthetic data from a truth peak, a perturbed start,
  request built by the PAGE's `peakToBackendSpec`, fitted by
  `fitting.run_fit` (no background, Trust-Region), applied by the page's
  `_applyBackendParams`, then `evalPeakArray` on the fitted grid must equal
  `individual_peaks[].y` within 1e-6 of amplitude. Plus: the Voigt request
  and write-back pins, a linked Voigt pair, a locked GL mix, and the Python
  twin deep-equal to the page's builder for every shape and a link. Run
  against main's page it fails on Voigt (0.93 % of amplitude), the Voigt
  pins and the linked pair; on the branch 10 pass, 2 todo (below).
- `tests/js/lineshape_parity.test.js` section (D): each shape's FREE
  parameters swept across `_make_peak_params`'s bounds (η 0–1, asymmetry
  0–1, DS α 0–0.5 / γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β
  0.1–5 / m 0–499, fwhm 0.1–15), one bridge call per shape.
- `tests/test_voigt_contract.py`: the twin, `run_fit` holding η and
  returning the 0.5 curve, the seed.

## 5. What the sweep found

| shape | result |
|---|---|
| Gaussian, Lorentzian, Voigt (glMix 0 and 100 ignored), GL, asym-GL, DS | ≤ 6.1e-16 of amplitude at every combination |
| DS+G, m < 0.001 (delta branch); LACX, m = 0 | exact |
| LACX, m > 0 | up to 0.89 % of amplitude where the kernel is wide against the peak (m = 50 points on a 0.1 eV peak): the tracked discretisation gap (rounded m + 2m+1 kernel on the page vs continuous m on the server). `todo`, the `caM` clamp unit. |
| DS+G, m ≥ 0.05 | the page's `laCasaXPS` quadrature sizes its step to resolve the Lorentzian core (β/3) and never the Gaussian kernel (σ = m/2.355): at β = 2, m = 0.05 the step is 0.67 eV against σ = 0.021 eV and the curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %; at the schema default (α 0.1, β 0.3, m 0.4) 3.9 %. 0 of 865 committed components use DS+G. `todo`; NOT fixed here (scope) — its own unit: port the server's padded-grid convolution to a grid-aware array evaluator, as `dsgDeltaKernel_array` already does for m < 0.001. |

## 6. The re-measurement (`scripts/local_server_gap.js` → `docs/findings/a03/local_server_gap.json`)

W1's 18 Batch Fit targets of the committed UCl4-graphite project, local
engine vs server from the same scaled start, page semantics on both sides.

| set | max Δcentre | max ΔFWHM | max Δarea | max Δfraction |
|---|---:|---:|---:|---:|
| C 1s, 8 of 9 (W1) | 3.8 meV | 0.50 % | 1.40 % | 0.32 pp |
| C 1s, 8 of 9 (A03) | 3.8 meV | 0.50 % | 1.40 % | 0.32 pp |
| C 1s Scan_4 (findings §2, unchanged) | 41.9 meV | 9.0 % | 99.9 % | 15.1 pp |
| U 4f, 9 (W1) | 39.7 meV | 17.2 % | 20.8 % | 1.4 pp |
| U 4f, 9 (A03) | 28.8 meV | 15.8 % | 8.9 % | 0.77 pp |
| U 4f, the 5 where both engines reach the same minimum (Scan_0/1/2/3/7; χ²ᵣ equal to 2–3 digits) | 4.3 meV | 2.6 % | 2.0 % | 0.12 pp |
| U 4f, the other 4 (Scan_4/5/6/8) | 28.8 meV | 15.8 % | 8.9 % | 0.77 pp |

On the 5 agreeing targets the Voigt satellites match within 2 % — the W1
gap on them (7–21 %) was the η identity and is gone. On the other 4 the
server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
7.9 while the local engine holds it at 8, and χ²ᵣ (local/server − 1) is
+9.6 %, +10.1 %, −5.0 % and +12.7 %. Movement in m alone does not
attribute the residual (Codex round 1), so the script has a CONTROL arm:
the server fitted with every LA m HELD at its start, the one thing the
local engine cannot move.

| target | local χ²ᵣ | server χ²ᵣ, m free | server χ²ᵣ, m held | local vs server, m free (Δcentre / ΔFWHM / Δarea / Δfrac) | local vs server, m held |
|---|---:|---:|---:|---|---|
| Scan_4 | 1.970 | 1.798 | 1.878 | 26.6 meV / 5.3 % / 8.3 % / 0.33 pp | 13.7 meV / 3.0 % / 5.0 % / 0.19 pp |
| Scan_5 | 2.393 | 2.174 | 2.187 | 4.7 meV / 4.3 % / 6.7 % / 0.35 pp | 6.5 meV / 3.4 % / 5.3 % / 0.25 pp |
| Scan_6 | 2.657 | 2.798 | 2.634 | 28.8 meV / 15.8 % / 8.9 % / 0.77 pp | 3.7 meV / 1.3 % / 1.4 % / 0.07 pp |
| Scan_8 | 4.656 | 4.129 | 4.118 | 5.7 meV / 5.0 % / 8.3 % / 0.32 pp | 6.3 meV / 4.9 % / 8.1 % / 0.33 pp |

So: on Scan_6 the residual IS the `caM` clamp (holding m on the server
closes it to the agreeing-target envelope). On Scan_5 and Scan_8 holding m
changes nothing — the local engine's descent stops at a χ²ᵣ 10–13 % above
the server's from the same start with the same free parameters: a worse
minimum, the "several minima" case (findings §2 had the mirror image on
C 1s Scan_4, where the local engine found the better one). Scan_4 is half
each. The residual is therefore two things, and `caM` is the smaller.

**Decision: the "starting point" designation STAYS**, on two grounds now:
the `caM` clamp (one target) and the local engine landing in a worse
minimum than Trust-Region on three of nine U 4f targets. The `caM` clamp
remains the next unit; the worse-minimum finding is recorded in findings
§7 for the local-engine work that follows it. Wording in the page updated
to say so (LA components and several minima; no longer Voigt).

## 7. Release-note line

Voigt components are now fitted at the fixed 50/50 mix the page has always
drawn; until now Run Fit let their mix vary on the server and the page
reported the 50/50 curve's area under the other mix's parameters (up to
20 % off per component). Re-fitting a saved project with Voigt components
moves an area fraction by 0.35 pp at the median and 0.69 pp at most on the
55 committed tabs (a Voigt's own area by 4.6 % at the median, 15 % at
most). Use GL to fit the mix. Also fixed: a GL mix of exactly 0 (asym-GL)
or a DS α of exactly 0 was sent to the server as 50 / 0.1.

## 8. Verification

- `tests/test_voigt_contract.py` 4 passed; full `pytest tests/` — see §9.
- JS suite: `node --test tests/js/*.test.js` (the directory form does not
  run in this node): see §9.
- Browser check (`browser_check_a03.py`, dev gunicorn :5151 from the
  worktree, re-run after round 1): the request carries `gl_ratio 0.5, fix_gl_ratio true` for
  both Voigt components; the server returns `vary: false, 0.5`; drawn vs
  fitted curve 1.3e-13 of amplitude for the Voigts (LACX 5.6e-3 — the caM
  rounding); the Results area of a Voigt equals the server curve's to
  0.0000 % (LACX −0.66 %, the same rounding); the chart dataset is the drawn curve; `glMix` unchanged in the
  live model and the saved record; Batch Fit onto U4f Scan_1 converges
  locally; no page errors.

## 9. Codex rounds

**Round 1 (`docs/autofit/codex/a03_voigt_eta_verdict_run{A,B}.md`): NO-GO ×2,
no blocker, converging findings.** Fixed:
1. MAJOR — the measurement script took the target file's own Voigt specs as
   the "old" arm, so a target file regenerated with the A03 builder would
   have made both arms identical. Both requests are now constructed
   explicitly; the generator is named correctly (`.js`); re-run (§2a).
2. MAJOR — the release-note number was a server-curve/trapezoid comparison
   of two refits, not the page's saved numbers against the page's refit
   numbers. Replaced by `scripts/voigt_saved_vs_refit.js` (§2b); the old
   rows relabelled as what they are.
3. MAJOR/MINOR — the builder sent an asym-GL mix of 0 as 50 and a DS α of 0
   as 0.1 (`p.glMix || 50`, `p.dsAlpha || 0.1`; the Python twin likewise);
   locked, the server held the substitute and the drawn curve differed from
   the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders
   (only a non-number falls back); the round-trip test now locks every shape
   parameter at its bounds; the sweep's backend parameters now come THROUGH
   `peakToBackendSpec` rather than a mapping of the harness's own.
4. MINOR — the uncertainty panel told a Voigt's user to "unlock the padlock"
   for a mix that has none: it now says the shape fixes the mix and points
   to GL.
5. MINOR — "χ²ᵣ differs by 8–20 %" was wrong (the four are +9.6, +10.1,
   −5.0, +12.7 %), the comment's "24 %" was 20 %, row A's 1.60 was 1.61 (now
   1.55 with the explicit arms); and attributing the whole residual to the
   `caM` clamp was an inference — the control arm (§6) shows it is one
   target of four.

exec
/bin/zsh -lc "sed -n '35,155p' autofit/reference.py; sed -n '6200,6300p' templates/index.html; rg -n 'function _peakArea|function _getQuant|function runFit\\(|n_perturb|ccShift|roiBE' templates/index.html | head -85; sed -n '1,210p' tests/autofit/battery_common.py; cat tests/autofit/test_u4f_parity_battery.py; git log --format=full main..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:


# ─────────────────────────────────────────────────────────────────────────────
# Project loading
# ─────────────────────────────────────────────────────────────────────────────

def load_project_tabs(path: str | Path) -> list[dict]:
    """
    Return the list of raw tab dicts from a ``.proj.zip`` or ``.proj.json``.

    Zip layout (saved by ``_doSaveProject`` for >= 5 tabs): ``manifest.json``
    with ``{version: 3, spectra: [{index, filename, ...}]}`` plus one
    ``spectrum_<i>_<name>.json`` per tab.  JSON layout (< 5 tabs): a single
    object with ``tabs: [...]``.
    """
    path = Path(path)
    if path.suffix == ".zip" or path.name.endswith(".proj.zip"):
        with zipfile.ZipFile(path) as z:
            manifest = json.loads(z.read("manifest.json"))
            if manifest.get("version") != 3:
                raise ValueError(
                    f"{path.name}: unsupported project version "
                    f"{manifest.get('version')!r} (expected 3)"
                )
            tabs = []
            for entry in manifest.get("spectra", []):
                tabs.append(json.loads(z.read(entry["filename"])))
            return tabs
    data = json.loads(path.read_text())
    if not isinstance(data.get("tabs"), list):
        raise ValueError(f"{path.name}: no 'tabs' array — not a v3 project JSON")
    return data["tabs"]


# ─────────────────────────────────────────────────────────────────────────────
# peakToBackendSpec mirror (index.html:5708)
# ─────────────────────────────────────────────────────────────────────────────

def _finite(v: Any) -> bool:
    """JS Number.isFinite: true only for finite numbers (not None/str/bool)."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and np.isfinite(v)


def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
    """
    Python mirror of the frontend's ``peakToBackendSpec``.

    ``all_peaks`` is needed for the linked-peak branch (JS resolves the
    parent via ``getPeak(p.linked)`` and silently drops the constraint when
    the parent is missing).
    """
    spec: dict[str, Any] = {
        "id": str(p["id"]),
        "name": p.get("name"),
        "center": p["center"],
        "amplitude": p["amplitude"],
        "fwhm": p["fwhm"],
        "amplitude_min": 0,
        "fix_center": bool(p.get("fixCenter")),
        "fix_fwhm": bool(p.get("fixFwhm")),
        "fix_amplitude": bool(p.get("fixAmplitude")),
        "fix_gl_ratio": bool(p.get("fixGlMix")),
    }
    shape = p.get("shape")
    if shape == "Gaussian":
        spec["shape"] = "gaussian"
    elif shape == "Lorentzian":
        spec["shape"] = "lorentzian"
    elif shape == "Voigt":
        # A03: the fixed 50/50 mix the page draws (twin of peakToBackendSpec)
        spec["shape"] = "pseudo_voigt_gl"
        spec["gl_ratio"] = 0.5
        spec["fix_gl_ratio"] = True
    elif shape == "GL":
        spec["shape"] = "pseudo_voigt_gl"
        spec["gl_ratio"] = p["glMix"] / 100.0
    elif shape == "asym-GL":
        spec["shape"] = "asymmetric_gl"
        # only a NON-NUMBER falls back to the default (a 0 is a value; A03 Codex round 1)
        spec["gl_ratio"] = (p["glMix"] if _finite(p.get("glMix")) else 50) / 100.0
        spec["asymmetry"] = p["asymmetry"] if _finite(p.get("asymmetry")) else 0
        spec["fix_asymmetry"] = bool(p.get("fixAsymmetry"))
        if _finite(p.get("_afAsymMin")):
            spec["asymmetry_min"] = p["_afAsymMin"]
        if _finite(p.get("_afAsymMax")):
            spec["asymmetry_max"] = p["_afAsymMax"]
    elif shape == "DS":
        spec["shape"] = "doniach_sunjic"
        spec["alpha"] = p["dsAlpha"] if _finite(p.get("dsAlpha")) else 0.1
        spec["gamma_asym"] = p["dsGamma"] if _finite(p.get("dsGamma")) else 0.0
        spec["fix_alpha"] = bool(p.get("fixDsAlpha"))
        spec["fix_gamma_asym"] = bool(p.get("fixDsGamma"))
    elif shape == "DSG_LA":
        spec["shape"] = "ds_g"
        spec["alpha"] = p["laAlpha"] if _finite(p.get("laAlpha")) else 0.10
        spec["beta"] = p["laBeta"] if _finite(p.get("laBeta")) else 0.3
        spec["m_gauss"] = p["laM"] if _finite(p.get("laM")) else 0.4
        spec["fix_alpha"] = bool(p.get("fixLaAlpha"))
        spec["fix_beta"] = bool(p.get("fixLaBeta"))
        spec["fix_m_gauss"] = bool(p.get("fixLaM"))
    elif shape == "LACX":
        spec["shape"] = "la_casaxps"
        spec["alpha"] = p["caAlpha"] if _finite(p.get("caAlpha")) else 1.0
        spec["beta"] = p["caBeta"] if _finite(p.get("caBeta")) else 1.0
        spec["m"] = p["caM"] if _finite(p.get("caM")) else 50.0
        spec["fix_alpha"] = bool(p.get("fixCaAlpha"))
        spec["fix_beta"] = bool(p.get("fixCaBeta"))
        spec["fix_m"] = bool(p.get("fixCaM"))
    else:
        spec["shape"] = "gaussian"

    if p.get("linked"):
        parent = next((q for q in all_peaks if q.get("id") == p["linked"]), None)
        if parent is not None:
            spec["constrain_to"] = str(p["linked"])
            spec["splitting"] = p.get("linkOffset")
            spec["area_ratio"] = p.get("linkRatio")
            spec["fix_fwhm"] = True
    return spec


  if (!json || typeof json !== 'object') throw serverError('Upload returned an unexpected response.');
  if (json.error) throw serverError(json.error);
  if (!json.session_id) throw serverError('Upload returned no session id.');
  return json.session_id;
}

function peakToBackendSpec(p) {
  // All initial values go at top level — fitting.py reads spec.get("center") etc.
  const spec = {
    id: String(p.id),
    name: p.name,
    center: p.center,
    amplitude: p.amplitude,
    fwhm: p.fwhm,
    amplitude_min: 0,
    fix_center: !!p.fixCenter,
    fix_fwhm: !!p.fixFwhm,
    fix_amplitude: !!p.fixAmplitude,
    fix_gl_ratio: !!p.fixGlMix
  };
  const shape = p.shape;
  if (shape === 'Gaussian') {
    spec.shape = 'gaussian';
  } else if (shape === 'Lorentzian') {
    spec.shape = 'lorentzian';
  } else if (shape === 'Voigt') {
    // A03 (2026-09-22): Voigt IS the fixed 50/50 mix the page draws, exports
    // and fits locally (evalPeak: eta = 0.5; runFitLocal holds it). Until A03
    // the request sent eta FREE from 0.3, so the server fitted a mix the page
    // never showed — on the 90 committed Voigt targets 60 of 180 components
    // went to pure Gaussian and 16 to pure Lorentzian, and every area the page
    // reported for them was the 0.5 curve's, up to 20 % off the fitted one.
    // Fixed on both sides; use GL to fit the mix.
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = 0.5;
    spec.fix_gl_ratio = true;
  } else if (shape === 'GL') {
    spec.shape = 'pseudo_voigt_gl';
    spec.gl_ratio = p.glMix / 100;   // frontend 0-100 → backend 0-1
  } else if (shape === 'asym-GL') {
    spec.shape = 'asymmetric_gl';
    // A03 Codex round 1: `p.glMix || 50` sent a mix of 0 as 50 (and a DS α of 0
    // as 0.1 below) — a value the page draws but never requested; locked, the
    // server held the substitute and the drawn curve differed from the fitted
    // one by 6.9 % (asym-GL) and 8.8 % (DS) of amplitude. Only a NON-NUMBER
    // falls back to the default.
    spec.gl_ratio = (Number.isFinite(p.glMix) ? p.glMix : 50) / 100;
    spec.asymmetry = Number.isFinite(p.asymmetry) ? p.asymmetry : 0;
    spec.fix_asymmetry = !!p.fixAsymmetry;
    // Forward auto-fit asymmetry bounds when present (set by buildAutoFitModel).
    // For non-auto-fit peaks these fields are absent and the backend falls back
    // to its [0.0, 1.0] default.
    if (Number.isFinite(p._afAsymMin)) spec.asymmetry_min = p._afAsymMin;
    if (Number.isFinite(p._afAsymMax)) spec.asymmetry_max = p._afAsymMax;
  } else if (shape === 'DS') {
    spec.shape = 'doniach_sunjic';
    spec.alpha      = Number.isFinite(p.dsAlpha) ? p.dsAlpha : 0.1;
    spec.gamma_asym = Number.isFinite(p.dsGamma) ? p.dsGamma : 0.0;
    spec.fix_alpha      = !!p.fixDsAlpha;
    spec.fix_gamma_asym = !!p.fixDsGamma;
  } else if (shape === 'DSG_LA') {
    spec.shape = 'ds_g';
    spec.alpha   = Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10;
    spec.beta    = Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3;
    spec.m_gauss = Number.isFinite(p.laM)     ? p.laM     : 0.4;
    spec.fix_alpha   = !!p.fixLaAlpha;
    spec.fix_beta    = !!p.fixLaBeta;
    spec.fix_m_gauss = !!p.fixLaM;
  } else if (shape === 'LACX') {
    spec.shape = 'la_casaxps';
    spec.alpha = Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0;
    spec.beta  = Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0;
    spec.m     = Number.isFinite(p.caM)     ? p.caM     : 50.0;
    spec.fix_alpha = !!p.fixCaAlpha;
    spec.fix_beta  = !!p.fixCaBeta;
    spec.fix_m     = !!p.fixCaM;
  } else {
    spec.shape = 'gaussian';
  }
  if (p.linked) {
    const parent = getPeak(p.linked);
    if (parent) {
      spec.constrain_to = String(p.linked);
      spec.splitting = p.linkOffset;
      spec.area_ratio = p.linkRatio;
      spec.fix_fwhm = true;
    }
  }
  return spec;
}

// Server parameter names -> the peak's fields, honouring the peak's locks.
// Shared by a fit result and by an alternative solution (previewed on a COPY
// of the peaks, or adopted as the start of a new fit).
function _applyBackendParams(p, par) {
  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
  if (par.amplitude && !p.fixAmplitude) p.amplitude = par.amplitude.value;
  if (par.fwhm      && !p.fixFwhm)     p.fwhm      = par.fwhm.value;
  // glMix is read only by GL / asym-GL; a Voigt's fixed 0.5 (A03) is not a
  // fitted value and must not overwrite the mix the peak carries for a later
  // switch to GL.
2309:  ccShift: 0,
2497:    const shift = src ? (src.ccShift || 0) : 0;
3161:      ccShift: 0,
3200:      rawBE: [], rawIntensity: [], ccShift: 0,
3228:    state.ccShift = tab.ccShift;
3298:      state.ccShift = 0; state.nextId = 1;
3366:        ccShift: t.ccShift,
3379:        shift: state.ccShift
3430:        state.ccShift = data.chargeCorrection.shift || 0;
3431:        active.ccShift = state.ccShift;
3807:    t.ccShift = isNaN(state.ccShift) ? 0 : state.ccShift;
3851:    // (which would overwrite state.ccShift and trigger a double updatePlot)
3856:    // Update shift display from the already-restored state.ccShift
3857:    const shift = -state.ccShift;
4817:  const prevShift = state.ccShift;
4827:    state.ccShift = isNaN(obs) ? 0 : obs - 284.5;
4832:    state.ccShift = isNaN(obs) ? 0 : obs - 284.8;
4837:    state.ccShift = isNaN(obs) ? 0 : obs - 83.98;
4842:    state.ccShift = isNaN(obs) ? 0 : obs - 192.99;
4847:    state.ccShift = isNaN(obs) ? 0 : obs - 398.31;
4852:    state.ccShift = isNaN(obs) ? 0 : obs - 190.74;
4858:    state.ccShift = (isNaN(obs) || isNaN(lit)) ? 0 : obs - lit;
4862:    state.ccShift = 0;
4866:  const delta = state.ccShift - prevShift;
4895:    // need no migration — anchors persist alongside the tab's ccShift, so
4906:  const shift = -state.ccShift;
4923:  // chart.update('none'); positioning math and ccShift are untouched (overlays stay
4929:  const shift = isNaN(state.ccShift) ? 0 : state.ccShift;
5528:    // directly (no ccShift handling here).
5896:  const { be: _roiBE } = (typeof getROIData === 'function' && state.rawBE.length) ? getROIData() : { be: [] };
5899:  if (_roiBE.length) {
5900:    for (const p of state.peaks) { const a = _peakArea(p, _roiBE); _peakAreas[p.id] = a; if (!_isUnsupported(p)) totalArea += a; }
6555://   provisionalShift  : state.ccShift to apply mentally — does NOT mutate state.
6740:    ccShift:      state.ccShift,
6773:  // MAJOR — a pre-existing defect for peaks/ccShift/DOM, not just the
6782:    t.ccShift = snap.ccShift;
6794:  state.ccShift   = snap.ccShift;
6814:    const sh = -state.ccShift;
6999:  const { be: roiBE } = (typeof getROIData === 'function' && state.rawBE && state.rawBE.length) ? getROIData() : { be: [] };
7002:  if (roiBE.length) for (const p of state.peaks) { areas[p.id] = _peakArea(p, roiBE); if (!_isUnsupported(p, key)) total += areas[p.id]; }
7079:  //    raw = corrected + state.ccShift (state.ccShift is the provisional value).
7080:  const graphiteFittedRaw = gPeak.center + (Number.isFinite(state.ccShift) ? state.ccShift : 0);
7193:  // App convention: raw = corrected + state.ccShift
7194:  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
7213:  // shift along with state.ccShift.
7278:        n_perturb: 3,
7379:function _startsModelKey(peaks, ui, ccShift, anchors) {
7383:    s: Number(ccShift) || 0,
7390:  return _startsModelKey(state.peaks, ui, state.ccShift, typeof _getManualAnchors === 'function' ? _getManualAnchors() : []);
7393:function _startsRecordKey(t) { return _startsModelKey(t.peaks, t.ui, t.ccShift, t.manualAnchors); }
7600:async function runFit(opts = {}) {
7666:      n_perturb: 3,
8320:function _peakArea(p, be) {
8709://         ccShift, matching single-tab behavior.
8715://       Live ccShift (deliberate asymmetry vs A/A2).
8719:// a contiguous slice of corrBE at fit time; if ccShift hasn't drifted,
8726:  const shift = src.ccShift || 0;
8749:  const shift = src.ccShift || 0;
8806:// (peak edits, ccShift edits, re-fits all happen while user is on the
8931:      // Raw view: full-range raw at live ccShift.
8932:      rawData = src.rawBE.map((b, j) => ({ x: b - (src.ccShift || 0), y: src.rawIntensity[j] + yShift }));
8976:  // source-tab changes (peaks/fits/ccShift edited while user was on the
9114:        ds.data = src.rawBE.map((b, j) => ({ x: b - (src.ccShift || 0), y: src.rawIntensity[j] + yShift }));
9453:      const shift = activeTab.ccShift || 0;
9465:          // DIRECTLY on the corrected-BE axis — never shifted by ccShift.
9936:      shift: state.ccShift
10034:    ccShift: tab.ccShift,
10038:    roiBE: be,
10094:      ccShift: t.ccShift, chargeVerified: t.chargeVerified ?? true,
10308:  active.ccShift = data.ccShift || 0;
10309:  state.ccShift = active.ccShift;
10465:        rawBE: [], rawIntensity: [], ccShift: 0,
10480:      ccShift: t.ccShift || 0,
11140:      ['Charge correction (eV)', state.ccShift.toFixed(3)], []
11153:    csv += `# Charge correction: ${state.ccShift.toFixed(3)} eV\n\n`;
11811:  const srcShift = sourceTab.ccShift;
11841:    // ccShift is copied separately just below.
11849:    tgt.ccShift = srcShift;
11862:      state.peaks = tgt.peaks; state.nextId = tgt.nextId; state.ccShift = tgt.ccShift;
12047://     displayed corrected-BE frame — never shifted by ccShift.
"""
Shared characterization-battery harness (used by the per-region
test_*_parity_battery.py files).

Three layers per region (see test_c1s_parity_battery.py for the rationale):
roster guard, eval parity vs saved fittedY, seeded-refit stability vs the
expert fit + frozen fixture records.
"""

import glob
import json
import os

import numpy as np

from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

# Default tolerances (C 1s levels).  Per-region batteries may override:
#
# - eval_tol: bounded below by BACKGROUND-ANCHOR DRIFT — ui bg-start/end
#   fields move with post-fit charge-correction nudges and round to 0.1 eV,
#   so the nearest-index anchors can shift ±1 grid point vs fit time; for
#   'smart' backgrounds that perturbs the recomputed background by
#   O(100 counts) mid-window (measured U 4f: eval relmax ~7e-3 with the
#   deviation profile exactly matching the background, not the shapes).
# - fixture_rtol: bounded below by CROSS-PROCESS FP wobble in the LACX
#   convolution path (~6e-6 relative on fitted params; exactly 0.0 within
#   one process).  Simple shapes (C 1s) reproduce at 1e-6.
EVAL_PARITY_TOL = 1e-5
CENTER_DRIFT_TOL_EV = 0.005
REL_DRIFT_TOL = 0.005
FIXTURE_CHI_RTOL = 1e-6
FIXTURE_PARAM_RTOL = 1e-6


def battery_fits(region):
    fits = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            if battery_eligible(rf, region=region)[0]:
                fits.append(rf)
    return fits


def load_fixture(name):
    with open(os.path.join(FIXTURE_DIR, name)) as f:
        return {(r["project"], r["name"]): r for r in json.load(f)["records"]}


def assert_roster(fits, expected, min_size, min_projects, gen_script):
    assert len(fits) >= min_size, (
        f"battery shrank to {len(fits)} fits (< {min_size}) — reference data "
        "or eligibility rules changed"
    )
    projects = {rf.project for rf in fits}
    assert len(projects) >= min_projects, f"battery covers only {projects}"
    assert {(rf.project, rf.name) for rf in fits} == set(expected), (
        "battery roster no longer matches the frozen fixture — regenerate "
        f"{gen_script} only if this change is intentional"
    )


def assert_eval_parity(rf, tol=EVAL_PARITY_TOL):
    relmax = eval_parity_relmax(rf)
    assert relmax < tol, (
        f"{rf.project}/{rf.name}: python eval of saved params deviates from "
        f"saved fittedY by {relmax:.3e} (tol {tol})"
    )


def assert_refit_stability_and_fixture(
    rf, expected,
    center_tol=CENTER_DRIFT_TOL_EV,
    rel_tol=REL_DRIFT_TOL,
    fixture_rtol=FIXTURE_PARAM_RTOL,
    stationarity="expert",
):
    """stationarity: what the seeded refit must stay at.
    "expert" — the saved expert fit itself (the fit is a fixed point of
    today's fitter). "refit" — a refit FROM the refit (the fitter's own fixed
    point): for a region whose saved fits were made under a request the page
    no longer sends (U 4f: Voigt satellites fitted with eta free until A03,
    2026-09-22), the expert's parameters are those of another model and the
    "expert" base cannot hold; the frozen fixture still pins the refit's
    numbers."""
    rec = refit_record(rf)
    assert rec["success"], f"{rf.project}/{rf.name}: seeded refit did not converge"

    if stationarity == "refit":
        rec2 = refit_record(rf, start=rec)
        assert rec2["success"], f"{rf.project}/{rf.name}: refit from the refit did not converge"
        base, moving, base_name = rec["peaks"], rec2["peaks"], "the refit"
    else:
        base, moving, base_name = rf.peaks, rec["peaks"], "expert fit"
    by_id = {str(p["id"]): p for p in base}
    for pk in moving:
        saved = by_id[str(pk["id"])]
        dc = abs(pk["center"] - saved["center"])
        dfw = abs(pk["fwhm"] - saved["fwhm"]) / max(saved["fwhm"], 1e-9)
        dam = abs(pk["amplitude"] - saved["amplitude"]) / max(abs(saved["amplitude"]), 1e-9)
        assert dc <= center_tol, (
            f"{rf.name} peak {pk['id']}: center drifted {dc:.4f} eV from {base_name}"
        )
        assert dfw <= rel_tol, (
            f"{rf.name} peak {pk['id']}: fwhm drifted {dfw:.2%} from {base_name}"
        )
        assert dam <= rel_tol, (
            f"{rf.name} peak {pk['id']}: amplitude drifted {dam:.2%} from {base_name}"
        )

    exp = expected[(rf.project, rf.name)]
    assert np.isclose(rec["reduced_chi_square"], exp["reduced_chi_square"],
                      rtol=max(FIXTURE_CHI_RTOL, fixture_rtol)), (
        f"{rf.name}: χ²ᵣ {rec['reduced_chi_square']} != frozen "
        f"{exp['reduced_chi_square']} — fitting.py numerics changed"
    )
    exp_peaks = {str(p["id"]): p for p in exp["peaks"]}
    for pk in rec["peaks"]:
        ep = exp_peaks[str(pk["id"])]
        for key in ("center", "fwhm", "amplitude", "area"):
            assert np.isclose(pk[key], ep[key], rtol=fixture_rtol, atol=1e-9), (
                f"{rf.name} peak {pk['id']}: {key} {pk[key]} != frozen {ep[key]}"
            )
"""
U 4f characterization battery — pins the MANUAL fit path's LACX + linked
spin-orbit doublet + Voigt satellite numerics against 29 expert reference
fits (structure mirrors test_c1s_parity_battery.py; shared logic in
battery_common.py).

Regenerate the fixture ONLY for reviewed numerics changes:
    venv/bin/python scripts/gen_u4f_battery_fixture.py

A03 (2026-09-22): the page now sends a Voigt with eta HELD at 0.5 (the mix
it has always drawn); the 29 expert U 4f fits were saved under the old
request (eta free from 0.3, ending at pure Gaussian or pure Lorentzian on
most satellites), so their saved parameters belong to another model and a
refit under today's request moves the LACX main line's width by up to 7.7 %
and its centre by up to 8 meV (the satellites' tails changed). The fixture
was regenerated for that reviewed change, and stationarity is measured
against a refit FROM the refit (battery_common, stationarity="refit"): the
fitter's own fixed point, not the pre-A03 save.
"""

import pytest

import battery_common as bc

REGION = "U 4f"
FIXTURE = "u4f_battery_expected.json"
MIN_BATTERY_SIZE = 20
MIN_PROJECTS = 3
# Bounded by background-anchor drift / LACX FP wobble — measured and
# documented in battery_common.py.  The worst LACX tab (UCl4_on_graphite
# U4f Scan_6, a flat alpha/beta/m valley) wobbles at 1.4e-4 relative
# across PROCESSES on one platform, but 1.9e-3 across PLATFORMS (first CI
# run on ubuntu/openBLAS vs the macOS/arm64 fixture, 2026-07-04 — fwhm
# 3.00971 vs frozen 3.00396 on that tab).  3e-3 covers the measured
# cross-platform wobble with ~1.6x headroom while still catching any real
# numerics change (C 1s pins the shared machinery at 1e-6).
# Eval-parity across all 29 eligible fits: median 6.0e-3, max 1.12e-2
# (bg-anchor drift) — 1.5e-2 keeps ~34% headroom without masking a real
# 2%-level regression (Codex Stage-3 finding #4).
EVAL_TOL = 1.5e-2
FIXTURE_RTOL = 3e-3

_FITS = bc.battery_fits(REGION)
_IDS = [f"{rf.project}::{rf.name}" for rf in _FITS]
_EXPECTED = bc.load_fixture(FIXTURE)


def test_battery_roster():
    bc.assert_roster(_FITS, _EXPECTED, MIN_BATTERY_SIZE, MIN_PROJECTS,
                     "scripts/gen_u4f_battery_fixture.py")


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_eval_parity(rf):
    bc.assert_eval_parity(rf, tol=EVAL_TOL)


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_refit_stability_and_fixture(rf):
    bc.assert_refit_stability_and_fixture(rf, _EXPECTED,
                                          fixture_rtol=FIXTURE_RTOL,
                                          stationarity="refit")
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-GRnT25h8' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-C56PLqfw' (errno=Operation not permitted)
commit 4d623f5ef2b5b4426048ef6cfbb30dc2ded509fb
Author: Skye Fortier <skyefortier@gmail.com>
Commit: Skye Fortier <skyefortier@gmail.com>

    fix(A03): Codex round 1 (NO-GO x2) - explicit measurement arms; release-note number from the page's own numbers; builders sent a mix or DS alpha of exactly 0 as the default; Voigt uncertainty note; caM attribution by a control arm
    
    - scripts/voigt_eta_measure.py constructs both requests explicitly (the
      target file's own Voigt specs were the "old" arm, which a regenerated
      file would have made identical); re-run: 60 of 180 pure Gaussian, 16
      pure Lorentzian; the 0.5 curve vs the fitted one median 13.9 %, max 20.1 %.
    - scripts/voigt_saved_vs_refit.js: the page's integration of the saved
      peaks against the page's integration of the refit (55 committed tabs):
      an area fraction moves median 0.35 pp, max 0.69 pp, none > 1 pp - the
      release-note number.
    - peakToBackendSpec and its Python twin sent an asym-GL mix of 0 as 50 and
      a DS alpha of 0 as 0.1 (`||` defaults); locked, the drawn curve differed
      from the fitted one by 6.9 % / 8.8 % of amplitude. Only a non-number
      falls back now. The round-trip test locks every shape parameter at its
      bounds; the parity sweep takes its backend parameters THROUGH
      peakToBackendSpec.
    - Uncertainty panel: a Voigt's held mix is the shape's contract, not a
      padlock to unlock; it now says so and points to GL.
    - local_server_gap.js gained a control arm (server with every LA m held):
      Scan_6's residual is the caM clamp; Scan_5/8's is the local engine
      stopping in a worse minimum (chi2r +10-13 % with m held too); Scan_4
      half each. Docs and CLAUDE.md corrected accordingly; the wrong "8-20 %",
      "24 %" and "1.60 pp" figures fixed; round-1 verdicts archived.
    
    Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>

commit 712e1363af5f44685a3c4f43722ecc9584d79709
Author: Skye Fortier <skyefortier@gmail.com>
Commit: Skye Fortier <skyefortier@gmail.com>

    fix(A03): a Voigt is the fixed 50/50 mix on BOTH sides; page->server->page identity test; parameter-range sweep; U 4f gap re-measured
    
    Until now peakToBackendSpec (and its Python twin) sent a "Voigt" as
    pseudo_voigt_gl with gl_ratio 0.3 FREE while the page drew, integrated,
    exported and fitted locally eta = 0.5. On the 90 committed Voigt targets
    (180 components) the server's eta ended at pure Gaussian on 46 and pure
    Lorentzian on 17, and every displayed Voigt area was the 0.5 curve's under
    the other mix's parameters: median 11.8 % off, max 20.1 %. The request now
    sends gl_ratio 0.5 held; _applyBackendParams writes glMix only for GL /
    asym-GL; the dropdown says fixed 50/50, use GL to fit the mix. What a
    student sees change on re-fitting a saved project: median 0.30 pp, max
    1.02 pp (scripts/voigt_eta_measure.py, docs/findings/a03/).
    
    tests/js/lineshape_roundtrip.test.js: for every shape, the request built by
    the page's own builder, fitted by fitting.run_fit, applied by the page's own
    write-back, then evalPeakArray on the fitted grid must equal
    individual_peaks[].y (fails on main's Voigt at 0.93 % of amplitude); pins
    the Python twins peak_to_backend_spec and the new apply_backend_params to
    the page, shape by shape. Parity harness section (D): each shape's free
    parameters swept across the fit's bounds. Found: DS+G's page quadrature
    (laCasaXPS) is wrong across its fitted beta/m range (1e52 x amplitude at
    beta 2 / m 0.05; 0 of 865 committed components use DS+G) - recorded as its
    own unit, not fixed here; LACX m > 0 up to 0.89 % (tracked, caM clamp).
    
    Re-measured (scripts/local_server_gap.js, W1's 18 targets): U 4f max
    area gap 20.8 -> 8.9 %, fraction 1.4 -> 0.77 pp; on the 5 of 9 targets
    where both engines reach the same minimum every component within 4.3 meV /
    2.6 % / 2.0 % / 0.12 pp; the residual is the held caM (server's m moved
    2.7-10.0 from 8). The "starting point" designation STAYS; caveat wording
    now names LA components and several minima.
    
    U 4f parity battery: the 29 expert fits were saved under the old request;
    fixture regenerated (reviewed numerics change) and stationarity measured
    against a refit FROM the refit (battery_common stationarity="refit").
    
    Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>

codex
Both builders now preserve zero-valued parameters, and the endpoint tests explicitly check `vary: false` and compare the page’s drawn curve with the server’s fitted curve. I’m checking the saved-tab roster, Results-table semantics, and whether the held-m control supports the revised attribution.

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/lineshape_roundtrip.test.js tests/js/lineshape_parity.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -m pytest -p no:cacheprovider tests/test_voigt_contract.py tests/autofit/test_u4f_parity_battery.py -q' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 138ms:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pytest/__main__.py", line 9, in <module>
    raise SystemExit(pytest.console_main())
                     ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -m pytest -s -p no:cacheprovider tests/test_voigt_contract.py tests/autofit/test_u4f_parity_battery.py -q' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 2 in 1651ms:

==================================== ERRORS ====================================
________________ ERROR collecting tests/test_voigt_contract.py _________________
tests/test_voigt_contract.py:13: in <module>
    import fitting
fitting.py:33: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
__________ ERROR collecting tests/autofit/test_u4f_parity_battery.py ___________
tests/autofit/test_u4f_parity_battery.py:23: in <module>
    import battery_common as bc
tests/autofit/battery_common.py:16: in <module>
    from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
autofit/parity.py:29: in <module>
    from fitting import (
fitting.py:33: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
=========================== short test summary info ============================
ERROR tests/test_voigt_contract.py - FileNotFoundError: [Errno 2] No usable t...
ERROR tests/autofit/test_u4f_parity_battery.py - FileNotFoundError: [Errno 2]...
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 1.40s

 exited 1 in 28552ms:
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Subtest: (A) frontend vs backend parity: Gaussian
not ok 1 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1244.008551
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
    startSubtestAfterBootstrap (node:internal/test_runner/harness:296:17)
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
not ok 2 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1296.814552
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: GL
not ok 3 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1293.404491
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: Voigt
not ok 4 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1231.336256
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DS
not ok 5 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1188.153062
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
not ok 6 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1268.687322
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)
not ok 7 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1206.873338
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:174:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:179:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX at m=0 (no convolution)
not ok 8 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1241.332287
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:185:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:191:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed
not ok 9 - (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed # TODO DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above
  ---
  duration_ms: 1197.405082
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:197:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:202:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
not ok 10 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1203.714916
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:221:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:228:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
not ok 11 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1149.088486
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:221:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:228:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
not ok 12 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1145.902623
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:221:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:228:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
not ok 13 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1146.412808
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:221:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:228:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
not ok 14 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1198.867103
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:238:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:245:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 15 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.415886
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 16 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.15585
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 17 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.211103
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 18 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.272238
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 19 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.300495
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 20 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.692639
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
ok 21 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
  ---
  duration_ms: 11.421855
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 22 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.674621
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:267:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7170.363795150584, rel diff=24.2055%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:274:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (C) evalPeak() has no direct callers outside evalPeakArray()
ok 23 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 2.907543
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
not ok 24 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1193.973225
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:378:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:379:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
not ok 25 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1155.813741
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:378:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:379:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Voigt
not ok 26 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1141.18583
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:378:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:379:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: GL
not ok 27 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1152.671108
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:378:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:379:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
not ok 28 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1209.10829
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:378:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:379:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DS
not ok 29 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1127.593015
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:378:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:379:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
not ok 30 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1085.843469
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:378:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:379:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
not ok 31 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1106.735174
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:378:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:379:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP
not ok 32 - (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1176.79374
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:386:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:387:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP
not ok 33 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1086.091581
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:386:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:328:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:370:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:387:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
not ok 34 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1245.494381
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
not ok 35 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1296.142543
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
not ok 36 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1289.923345
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
not ok 37 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1230.835328
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
not ok 38 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1179.529269
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
not ok 39 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1270.626767
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 40 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1233.126428
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
not ok 41 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX # TODO LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit
  ---
  duration_ms: 1232.152499
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:124:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
not ok 42 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1183.573842
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:132:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:139:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
not ok 43 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1202.255001
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:147:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:149:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — GL mix 0 locked
not ok 44 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1151.762258
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:176:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:177:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — GL mix 100 locked
not ok 45 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1141.841544
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:176:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:177:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — asym-GL mix 0 locked
not ok 46 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1147.700868
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:176:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:177:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — asym-GL asymmetry 0 locked
not ok 47 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1202.777611
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:176:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:177:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS alpha 0 locked
not ok 48 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1202.448488
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:176:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:177:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS gamma 0 locked
not ok 49 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1161.016747
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:176:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:177:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS alpha 0.5 locked
not ok 50 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1142.489377
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:176:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:177:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
not ok 51 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1150.515361
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:188:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:110:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:189:33)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
not ok 52 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1180.776014
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:199:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:207:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
not ok 53 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1142.020026
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:217:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:226:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
1..53
# tests 53
# suites 0
# pass 8
# fail 38
# cancelled 0
# skipped 0
# todo 7
# duration_ms 28583.880791

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir=\"/tmp\"
import json, collections
from pathlib import Path
from autofit.reference import load_project_tabs
stats=collections.Counter(); details=[]
for z in sorted(Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\")):
 c=collections.Counter()
 for t in load_project_tabs(z):
  if t.get(\"isStack\") or not t.get(\"rawBE\") or not any(p.get(\"shape\")==\"Voigt\" for p in t.get(\"peaks\",[])): continue
  c[\"voigt\"]+=1
  if not t.get(\"fitResult\"): c[\"no_fit\"]+=1; continue
  c[\"fit\"]+=1; fr=t[\"fitResult\"]; ui=t.get(\"ui\",{}); sh=t.get(\"ccShift\",0)
  b=[b-sh for b in t[\"rawBE\"] if float(ui[\"roiMin\"])<=b-sh<=float(ui[\"roiMax\"])]
  if fr.get(\"be\") and b"'!=fr["be"]: details.append((z.name,t["name"],"DIFFERENT saved be",len(b),len(fr["be"]), b[:2],fr["be"][:2]))
  stats["has_fit_be"]+=bool(fr.get("be")); stats["local"]+=fr.get("engine")=="local"; stats["shifted"]+=bool(sh)
  stats["non_2dp_intensity"]+=any(abs(y-round(y,2))>1e-7 for y in t["rawIntensity"])
  stats["bg_"+ui.get("bgType","")]+=1; stats["method_"+str(ui.get("fitMethod"))]+=1
  for p in t["peaks"]:
   for k in p:
    if "support" in k.lower(): stats[k]+=1
 print(z.name,dict(c))
print("stats",dict(stats));print("grid mismatches",details)
a=json.load(open("docs/findings/a03/voigt_saved_vs_refit.json")); print("saved summary",a["summary"])
g=json.load(open("docs/findings/a03/local_server_gap.json"))
for r in g["regions"]["U4f"]:
 print(r["target"], "held chi %",100*(r["local_chi2r"]/r["server_held_m_chi2r"]-1),"free chi %",100*(r["local_chi2r"]/r["server_chi2r"]-1))
'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 117ms:
1-GTA UCl4-graphite one set of U doublets.proj.zip {'voigt': 10, 'fit': 10}
4-GTA UCl4-BN.proj.zip {'voigt': 10, 'fit': 10}
8-JT Graphite.proj.zip {}
B4C-UCl4.proj.zip {'voigt': 10, 'fit': 10}
Cl2p_projfit_test.proj.zip {'voigt': 8, 'fit': 8}
Project9_CasaXPS_newfit.proj.zip {'voigt': 7, 'fit': 7}
UCl4_on_graphite.proj.zip {'voigt': 10, 'fit': 10}
stats {'has_fit_be': 41, 'local': 0, 'shifted': 54, 'non_2dp_intensity': 55, 'bg_smart': 54, 'method_None': 55, 'bg_smart_exp': 1}
grid mismatches [('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan', 'DIFFERENT saved be', 350, 350, [405.05999999999995, 404.9599999999998], [405.06, 404.96]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_0', 'DIFFERENT saved be', 350, 350, [405.05999999999995, 404.9599999999998], [405.06, 404.96]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_1', 'DIFFERENT saved be', 349, 349, [405.20999999999987, 405.10999999999996], [405.21, 405.11]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_2', 'DIFFERENT saved be', 350, 350, [405.05999999999995, 404.9599999999998], [405.06, 404.96]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_3', 'DIFFERENT saved be', 350, 350, [405.05999999999995, 404.9599999999998], [405.06, 404.96]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_4', 'DIFFERENT saved be', 350, 350, [405.20999999999987, 405.10999999999996], [405.21, 405.11]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_5', 'DIFFERENT saved be', 350, 350, [405.05999999999995, 404.9599999999998], [405.06, 404.96]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_6', 'DIFFERENT saved be', 350, 350, [405.0609999999999, 404.9609999999998], [405.061, 404.961]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_7', 'DIFFERENT saved be', 349, 349, [404.9099999999998, 404.8099999999999], [404.91, 404.81]), ('1-GTA UCl4-graphite one set of U doublets.proj.zip', 'U4f Scan_8', 'DIFFERENT saved be', 350, 350, [405.05999999999995, 404.9599999999998], [405.06, 404.96]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan', 'DIFFERENT saved be', 326, 326, [403.8559999999998, 403.7559999999999], [403.856, 403.756]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_0', 'DIFFERENT saved be', 326, 326, [403.86399999999986, 403.76399999999995], [403.856, 403.756]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_1', 'DIFFERENT saved be', 326, 326, [403.8679999999998, 403.7679999999999], [403.856, 403.756]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_2', 'DIFFERENT saved be', 327, 327, [403.96699999999976, 403.86699999999985], [403.968, 403.868]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_3', 'DIFFERENT saved be', 327, 327, [404.01999999999975, 403.91999999999985], [403.968, 403.868]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_4', 'DIFFERENT saved be', 327, 327, [403.9899999999998, 403.8899999999999], [403.968, 403.868]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_5', 'DIFFERENT saved be', 327, 327, [403.95999999999975, 403.85999999999984], [403.96, 403.86]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_6', 'DIFFERENT saved be', 327, 327, [403.95999999999975, 403.85999999999984], [403.96, 403.86]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_7', 'DIFFERENT saved be', 327, 327, [403.95999999999975, 403.85999999999984], [403.968, 403.868]), ('4-GTA UCl4-BN.proj.zip', 'U4f Scan_8', 'DIFFERENT saved be', 327, 327, [403.95999999999975, 403.85999999999984], [403.968, 403.868]), ('B4C-UCl4.proj.zip', 'U4f Scan', 'DIFFERENT saved be', 350, 350, [406.28999999999985, 406.18999999999994], [406.29, 406.19]), ('B4C-UCl4.proj.zip', 'U4f Scan_0', 'DIFFERENT saved be', 350, 350, [406.3799999999999, 406.28], [406.38, 406.28]), ('B4C-UCl4.proj.zip', 'U4f Scan_1', 'DIFFERENT saved be', 350, 350, [406.2099999999999, 406.1099999999998], [406.21, 406.11]), ('B4C-UCl4.proj.zip', 'U4f Scan_2', 'DIFFERENT saved be', 350, 350, [406.2199999999999, 406.1199999999998], [406.22, 406.12]), ('B4C-UCl4.proj.zip', 'U4f Scan_3', 'DIFFERENT saved be', 350, 350, [406.2199999999999, 406.1199999999998], [406.22, 406.12]), ('B4C-UCl4.proj.zip', 'U4f Scan_4', 'DIFFERENT saved be', 350, 350, [406.15999999999997, 406.05999999999983], [406.16, 406.06]), ('B4C-UCl4.proj.zip', 'U4f Scan_5', 'DIFFERENT saved be', 350, 350, [406.1999999999998, 406.0999999999999], [406.2, 406.1]), ('B4C-UCl4.proj.zip', 'U4f Scan_6', 'DIFFERENT saved be', 350, 350, [406.2299999999999, 406.12999999999977], [406.23, 406.13]), ('B4C-UCl4.proj.zip', 'U4f Scan_7', 'DIFFERENT saved be', 350, 350, [406.2099999999999, 406.1099999999998], [406.21, 406.11]), ('B4C-UCl4.proj.zip', 'U4f Scan_8', 'DIFFERENT saved be', 350, 350, [406.29999999999984, 406.19999999999993], [406.3, 406.2]), ('Cl2p_projfit_test.proj.zip', 'Cl2p Scan_1', 'DIFFERENT saved be', 200, 200, [205.31999999999994, 205.2199999999998], [205.32, 205.22]), ('UCl4_on_graphite.proj.zip', 'U4f Scan', 'DIFFERENT saved be', 350, 350, [405.0589999999999, 404.9589999999998], [405.009, 404.909]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_0', 'DIFFERENT saved be', 350, 350, [405.0369999999999, 404.9369999999998], [405.037, 404.937]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_1', 'DIFFERENT saved be', 350, 350, [405.19799999999987, 405.09799999999996], [405.009, 404.909]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_2', 'DIFFERENT saved be', 350, 350, [405.05999999999995, 404.9599999999998], [405.087, 404.987]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_3', 'DIFFERENT saved be', 350, 350, [405.03399999999993, 404.9339999999998], [405.034, 404.934]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_4', 'DIFFERENT saved be', 350, 350, [405.11599999999993, 405.0159999999998], [405.087, 404.987]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_5', 'DIFFERENT saved be', 350, 350, [405.03399999999993, 404.9339999999998], [405.034, 404.934]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_6', 'DIFFERENT saved be', 350, 350, [405.06199999999995, 404.9619999999998], [405.062, 404.962]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_7', 'DIFFERENT saved be', 350, 350, [405.00999999999993, 404.9099999999998], [405.01, 404.91]), ('UCl4_on_graphite.proj.zip', 'U4f Scan_8', 'DIFFERENT saved be', 350, 350, [405.04599999999994, 404.9459999999998], [405.046, 404.946])]
saved summary {'n_tabs': 55, 'n_converged': 55, 'dFrac_pp': {'median': 0.3510427011305217, 'p90': 0.5078582976864185, 'max': 0.6882340627316421}, 'gt_1pp': 0, 'voigt_dArea_pct': {'median': 4.577004847485078, 'p90': 7.556697705435966, 'max': 15.300258030724901}}
U4f Scan_0 held chi % 0.781524047301585 free chi % 0.4893410019950917
U4f Scan_1 held chi % 1.5919548262667726 free chi % 1.294873003999597
U4f Scan_2 held chi % 0.09670776523607039 free chi % -0.1934227623375473
U4f Scan_3 held chi % -0.03938780346149917 free chi % -0.015872165788044512
U4f Scan_4 held chi % 4.911454343839439 free chi % 9.5746050466472
U4f Scan_5 held chi % 9.436116024980157 free chi % 10.074778252620087
U4f Scan_6 held chi % 0.8779852896095841 free chi % -5.014663412506004
U4f Scan_7 held chi % 0.6833112188108892 free chi % 0.3962369557254153
U4f Scan_8 held chi % 13.060127406786993 free chi % 12.744719220387957

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\",\"-p\",\"no:cacheprovider\",\"tests/test_voigt_contract.py\",\"tests/autofit/test_u4f_parity_battery.py\",\"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 5308ms:
................................................................
64 passed in 4.96s

exec
/bin/zsh -lc "sed -n '6160,6205p' templates/index.html; sed -n '3208,3255p' templates/index.html; sed -n '4860,4897p' templates/index.html; rg -n 'random_seed|request_seed|seed_payload|canonical|n_starts' fitting.py | head -50; sed -n '1,70p' tests/js/lineshape_roundtrip.test.js; rg -n 'smart_exp' fitting.py | head; rg -n 'fitCaM|caM|chiReduced|nFree' templates/index.html | awk '"'$1+0>=7850 && $1+0<=8310'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
        ? 'Lorentzian half-width parameter (\u03b3 = width/2). When \u03b1 > 0, the measured FWHM of the peak is broader than this input value because of the asymmetric tail.'
        : 'Full width at half maximum. Typical XPS peak widths range from 0.5 to 3.0 eV depending on the element, chemical state, and spectrometer resolution. Peaks from the same chemical environment should have similar FWHM values.');
    }
  }
}

function togglePeakBody(id) {
  const body = document.getElementById('peak-body-' + id);
  body.classList.toggle('open');
}

function _highlightChartPeak(peakId, highlight) {
  if (!state.chart) return;
  const datasets = state.chart.data.datasets;
  for (const ds of datasets) {
    if (ds._peakId === peakId) {
      ds.borderWidth = highlight ? 3 : 1.5;
    }
  }
  state.chart.update('none');
}

// ═══════════════════════════════════════════════════
// ═══════════════════════════════════════════════════
// FLASK BACKEND HELPERS
// ═══════════════════════════════════════════════════
async function uploadToBackend(be, inten) {
  const csv = be.map((e, i) => e.toFixed(4) + ',' + inten[i].toFixed(2)).join('\n');
  const form = new FormData();
  form.append('file', new Blob([csv], { type: 'text/plain' }), 'spectrum.csv');
  const resp = await fetch('/api/upload', { method: 'POST', body: form });
  // A server-side failure (HTTP error, error body, or no session id) is not a
  // transport failure: runFit must report it, never switch engines (unit A0).
  const serverError = (msg) => { const err = new Error(msg); err.serverError = true; return err; };
  if (resp.ok === false) {
    let msg = null;
    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
    throw serverError(msg || ('Upload failed (HTTP ' + resp.status + ').'));
  }
  const json = await resp.json();
  if (!json || typeof json !== 'object') throw serverError('Upload returned an unexpected response.');
  if (json.error) throw serverError(json.error);
  if (!json.session_id) throw serverError('Upload returned no session id.');
  return json.session_id;
}

    this.activateTab(id);
    return tab;
  }

  activateTab(id) {
    if (this.activeId === id) return;
    const tab = this._getTab(id);
    if (!tab) return;
    // Cancel any armed placement mode so a click on the new tab's chart
    // isn't consumed by a placement aimed at the previous spectrum.
    if (placeMode) togglePlaceMode(placeMode);
    // Clear stale history preview from previous tab
    if (typeof _historyPreview !== 'undefined') _historyPreview = null;
    // Save current tab's live state
    this._syncActiveToRecord();
    this.activeId = id;

    // Swap global state fields — peaks uses reference sharing
    state.rawBE = tab.rawBE;
    state.rawIntensity = tab.rawIntensity;
    state.ccShift = tab.ccShift;
    state.peaks = tab.peaks;
    state.nextId = tab.nextId;
    state.fitResult = tab.fitResult;
    state.lineWidth = tab.lineWidth ?? 1.5;

    // Restore DOM form fields
    this._restoreUI(tab.ui);
    _updateUndoButtons();   // history is per tab: buttons reflect the incoming record
    const notesEl = document.getElementById('spectrum-notes');
    if (notesEl) notesEl.value = tab.notes || '';
    this._updateCCVerifiedUI(tab.chargeVerified ?? true);
    this._updateInfoBadge(tab);
    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
    // Update chi-squared display for this tab's fit result
    _applyStatDisplay(state.fitResult);
    if (state.fitResult && state.fitResult.rFactor == null) {
      state.fitResult.rFactor = _computeRFactor(state.fitResult);
    }
    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
    _updateROIDisplay(state.fitResult ? state.fitResult.roiRange : null);
    // Reset Y zoom so chart auto-scales to this tab's data range
    // (prevents survey zoom from squishing narrow-region spectra)
    state._mainYMax = tab.yZoom || null;
    state._mainXMin = tab.xZoomMin ?? null;
    state._mainXMax = tab.xZoomMax ?? null;

    this.renderTabBar();
    targetField.style.display = 'block';
  } else {
    state.ccShift = 0;
  }

  // Shift all energy-dependent values by the change in correction
  const delta = state.ccShift - prevShift;
  if (delta !== 0) {
    // ROI boundaries
    const roiMinEl = document.getElementById('roi-min');
    const roiMaxEl = document.getElementById('roi-max');
    const roiMinVal = parseFloat(roiMinEl.value);
    const roiMaxVal = parseFloat(roiMaxEl.value);
    if (!isNaN(roiMinVal)) roiMinEl.value = (roiMinVal - delta).toFixed(1);
    if (!isNaN(roiMaxVal)) roiMaxEl.value = (roiMaxVal - delta).toFixed(1);

    // Background endpoints
    const bgStartEl = document.getElementById('bg-start');
    const bgEndEl = document.getElementById('bg-end');
    const bgStartVal = parseFloat(bgStartEl.value);
    const bgEndVal = parseFloat(bgEndEl.value);
    if (!isNaN(bgStartVal)) bgStartEl.value = (bgStartVal - delta).toFixed(1);
    if (!isNaN(bgEndVal)) bgEndEl.value = (bgEndVal - delta).toFixed(1);

    // Peak centers
    for (const p of state.peaks) {
      p.center -= delta;
    }

    // Manual background anchors. Anchors are DATA-ATTACHED like peak
    // centers (x = a data point's corrected BE at placement time, y = that
    // point's intensity), so they follow the same -delta migration as the
    // ROI/bg fields and peak centers above — NOT the reference-marker
    // convention (literature markers stay at nominal corrected BE). y is
    // untouched: intensity is unaffected by charge correction. Saved files
    // need no migration — anchors persist alongside the tab's ccShift, so
    // every save is a self-consistent snapshot.
    const ccAnchors = _getManualAnchors();
1110:def _canonical(value):
1114:        return {str(k): _canonical(value[k]) for k in sorted(value, key=str)}
1116:        return [_canonical(v) for v in value]
1124:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1167:    rest = _canonical({"shapes": list(shapes), "params": roles, "fit_kws": kws, "solver": solver,
1269:def _scattered_starts(n_starts, fit_once, model, start_params, result, peak_specs, x, rng) -> dict[str, Any]:
1276:    for _ in range(n_starts):
1291:            clusters.append({"chi2r": float(trial.redchi), "n_starts": 1, "components": comps})
1293:            home["n_starts"] += 1
1303:        "ran": True, "n_run": n_starts, "n_converged": n_converged, "n_same_as_fit": n_same,
1305:        "n_in_alternatives": sum(c["n_starts"] for c in lower),
1306:        "n_not_better_elsewhere": sum(c["n_starts"] for c in other),
1425:    n_starts: int = 0,
1614:        random_seed = int(caller_seed)
1616:        random_seed = _request_seed(
1623:                                           for child in np.random.SeedSequence(random_seed).spawn(3))
1624:    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
1625:        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")
1733:    if n_starts:
1743:                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
1906:        "random_seed": random_seed,
// Page → server → page identity (A03, 2026-09-22).
//
// The parity harness (lineshape_parity.test.js) proves the two EVALUATORS
// agree for the same parameters. It cannot see a request that asks the
// server to fit a parameter the page never draws: until A03 a "Voigt" was
// sent as pseudo_voigt_gl with gl_ratio FREE from 0.3 while evalPeak drew
// η = 0.5, so every chart component, area, percentage and export for a
// Voigt was the 0.5 curve under parameters fitted for another mix (on the
// 90 committed Voigt targets: displayed areas 12 % off the fitted curve at
// the median, 20 % at worst; 60 of 180 components had gone to pure
// Gaussian, 16 to pure Lorentzian). This test closes that class: for every
// shape, build the request with the PAGE's own peakToBackendSpec, fit it
// on the server (fitting.run_fit, no background, Trust-Region), apply the
// result with the page's own _applyBackendParams, and require the curve the
// page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
// server FITTED (individual_peaks[].y).
//
// Two shapes carry a known drawn-vs-fitted gap and are marked todo with the
// unit that owns it: LACX (the page sends m free and draws it ROUNDED —
// the caM clamp unit) and DSG_LA (the page's quadrature — see the parity
// harness's section (D)).
const { test } = require('node:test');
const assert = require('node:assert');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}
const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', 'dsgDeltaKernel_array',
  'evalPeakArray', 'getPeak', 'peakToBackendSpec', '_applyBackendParams'];
const state = { peaks: [] };
const env = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, peakToBackendSpec, _applyBackendParams };')(state);

function findPython() {
  for (const c of [process.env.XPS_PYTHON, path.join(REPO_ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3']) {
    if (c && fs.existsSync(c)) return c;
  }
  return 'python3';
}
const PYTHON = findPython();
const BRIDGE = path.join(__dirname, 'lineshape_roundtrip_backend.py');
function bridge(payload) {
  return JSON.parse(execFileSync(PYTHON, [BRIDGE, REPO_ROOT], { input: JSON.stringify(payload), encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

// A realistic BE grid, descending like a real acquisition: 12 eV, 0.05 eV step.
const CENTER = 391.8;
const GRID = Array.from({ length: 241 }, (_, i) => CENTER + 6 - 0.05 * i);
// Deterministic noise (LCG), so the fit is a real fit and the test is repeatable.
function noise(seed, n, scale) {
  let s = seed >>> 0; const out = [];
  for (let i = 0; i < n; i++) { s = (1664525 * s + 1013904223) >>> 0; out.push(scale * ((s / 4294967296) - 0.5)); }
  return out;
}
function fullPeak(over) {
342:    matching smart_experimental_background / shirley_linear_background.
413:def smart_experimental_background(
1536:    elif bg_method == "smart_exp":
1537:        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
1929:    elif method == "smart_exp":
1930:        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
7873:           weighting: fr.weighting || null, chiReduced: fr.chiReduced ?? null,
7882:  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
7897:  if (fr && Number.isFinite(fr.chiReduced)) {
7899:    if (sb) sb.textContent = fr.chiReduced.toFixed(3);
7975:        if (!p.fixCaM)     { freeParams.push(Number.isFinite(p.caM)     ? p.caM     : 50);  paramMap.push({id: p.id, param: 'caM'}); }
7998:    if (param === 'caM')          return Math.max(0,   Math.min(499, Math.round(v)));
8002:    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];
8086:  // caM is rounded to an integer by its clamp, so a finite difference cannot
8089:  const isDiscrete = j => paramMap[j].param === 'caM';
8235:  // integer-clamped caM is carried at its start value and is not one of them
8239:  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
8251:      const nFreeComp = paramMap.filter(d => d.id === wp.id && !isDiscrete(paramMap.indexOf(d))).length;
8252:      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
8261:  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
8278:         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
8280:  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };

codex
I found two mismatches in the saved-versus-refit harness: it uses the current ROI grid for saved areas, while Results prefers `fitResult.be`, and it omits the page upload’s rounding. Several committed tabs have saved grids shifted from the current ROI grid. I’m measuring the effect before assigning severity.

The test runs also hit the read-only environment’s temporary-file probe. I’m retrying with an in-memory setup that avoids that probe and keeps file writes disabled.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require(\"child_process\");const orig=cp.execFileSync;cp.execFileSync=(file,args,opts)=>{if(file.includes(\"python\")){if(args[0]===\"-c\"){args=[\"-c\",\"import tempfile; tempfile.tempdir='\\''/tmp'\\'';\\n\"+args[1],...args.slice(2)];}else{args=[\"-c\",\"import tempfile,sys,runpy; tempfile.tempdir='\\''/tmp'\\''; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='\\''__main__'\\'')\",...args];}}return orig(file,args,opts);};require(\"./tests/js/lineshape_roundtrip.test.js\"); require(\"./tests/js/lineshape_parity.test.js\");'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require(\"child_process\");const orig=cp.execFileSync;cp.execFileSync=(file,args,opts)=>{if(file.includes(\"python\")){if(args[0]===\"-c\"){args=[\"-c\",\"import tempfile; tempfile.tempdir='\\''/tmp'\\'';\\n\"+args[1],...args.slice(2)];}else{args=[\"-c\",\"import tempfile,sys,runpy; tempfile.tempdir='\\''/tmp'\\''; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='\\''__main__'\\'')\",...args];}}return orig(file,args,opts);};const fs=require(\"fs\"),Module=require(\"module\"),path=require(\"path\"); const f=path.resolve(\"scripts/voigt_saved_vs_refit.js\");const old=JSON.parse(fs.readFileSync(\"docs/findings/a03/voigt_saved_vs_refit.json\",\"utf8\"));fs.writeFileSync=(dest,data)=>{const o=JSON.parse(data);console.log(JSON.stringify({summary:o.summary,changes:o.targets.map((r,i)=>({project:r.project,tab:r.tab,old:old.targets[i].max_dFrac_pp,new:r.max_dFrac_pp,oldArea:old.targets[i].max_voigt_dArea_pct,newArea:r.max_voigt_dArea_pct})).filter(r=>Math.abs(r.new-r.old)>0.01)},null,2));};let src=fs.readFileSync(f,\"utf8\").replace(\"JSON.stringify({ be, inten, peaks: saved, ui, n_perturb: 3 })\",\"JSON.stringify({ be: be.map(x=>+x.toFixed(4)), inten: inten.map(x=>+x.toFixed(2)), peaks: saved, ui, n_perturb: 3 })\").replace(\"saved.map(p => area(be, p))\",\"saved.map(p => area(t.fitResult.be?.length ? t.fitResult.be : be, p))\");const m=new Module(f,module);m.filename=f;m.paths=module.paths;m._compile(src,f);'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir=\"/tmp\"
import fitting, numpy as np
from autofit.reference import peak_to_backend_spec
x=np.arange(12.,0.,-.05); y=np.ones(len(x))*20+fitting.pseudo_voigt_gl(x,amplitude=3000,center=6,fwhm=1.4,gl_ratio=.5)
for shape,params,key,oldvalue in [(\"asym-GL\",dict(glMix=0,asymmetry=.3),\"gl_ratio\",.5),(\"DS\",dict(dsAlpha=0,dsGamma=.2),\"alpha\",.1)]:
 p=dict(id=1,name=\"p\",shape=shape,center=6,amplitude=3000,fwhm=1.4,**params)
 new=peak_to_backend_spec(p,[p]); old=dict(new,**{key:oldvalue})
 for name,spec in [(\"before\",old),(\"after\",new)]:
  r=fitting.run_fit(x,y,[spec],background_method=\"none\",n_perturb=0)
  print(shape,name,r[\"random_seed\"])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 exited 1 in 1732ms:
/Users/skyefortier/.matplotlib is not a writable directory
Traceback (most recent call last):
  File "<string>", line 4, in <module>
AttributeError: module 'fitting' has no attribute 'pseudo_voigt_gl'. Did you mean: '_pseudo_voigt_gl'?

exec
/bin/zsh -lc "nl -ba scripts/voigt_saved_vs_refit.js | tail -36; nl -ba CLAUDE.md | sed -n '480,501p'; nl -ba tests/js/lineshape_roundtrip.test.js | sed -n '155,188p'; sed -n '1124,1177p' fitting.py; sed -n '6320,6355p' templates/index.html; rg -n 'function applyBackendResult|syncLinkedPeaks|function evalPeakArray' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    26	const DATA = path.join(ROOT, 'docs/autofit/test_data');
    27	const area = (be, p) => { const step = be.length > 1 ? Math.abs(be[1] - be[0]) : 1; return fns.evalPeakArray(be, p).reduce((s, y) => s + y, 0) * step; };
    28	const out = { generated: new Date().toISOString(), n_perturb: 3, targets: [] };
    29	for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
    30	  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
    31	  for (const t of tabs) {
    32	    if (!t.fitResult || !(t.peaks || []).some(p => p.shape === 'Voigt')) continue;
    33	    const ui = t.ui || {};
    34	    const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
    35	    if (!Number.isFinite(roiMin) || !Number.isFinite(roiMax) || !ui.bgType) continue;
    36	    const be = [], inten = [];
    37	    t.rawBE.forEach((b, i) => { const c = b - (t.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(t.rawIntensity[i]); } });
    38	    if (be.length < 10) continue;
    39	    const saved = JSON.parse(JSON.stringify(t.peaks));
    40	    let srv;
    41	    try {
    42	      srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be, inten, peaks: saved, ui, n_perturb: 3 }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    43	    } catch (e) { out.targets.push({ project: zp, tab: t.name, error: String(e.message).slice(0, 200) }); continue; }
    44	    const refit = JSON.parse(JSON.stringify(saved));
    45	    srv.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; fns._applyBackendParams(refit[i], par); });
    46	    const aS = saved.map(p => area(be, p)), aR = refit.map(p => area(be, p));
    47	    const tS = aS.reduce((s, v) => s + v, 0), tR = aR.reduce((s, v) => s + v, 0);
    48	    const comps = saved.map((p, i) => ({ name: p.name, shape: p.shape, saved_area: aS[i], refit_area: aR[i],
    49	      dArea_pct: aS[i] ? 100 * (aR[i] / aS[i] - 1) : null, dFrac_pp: 100 * (aR[i] / tR - aS[i] / tS) }));
    50	    const rec = { project: zp, tab: t.name, server_success: srv.success, chi2r: srv.chi2r,
    51	      max_dFrac_pp: Math.max(...comps.map(c => Math.abs(c.dFrac_pp))),
    52	      max_voigt_dArea_pct: Math.max(...comps.filter(c => c.shape === 'Voigt' && c.dArea_pct != null).map(c => Math.abs(c.dArea_pct))), comps };
    53	    out.targets.push(rec);
    54	    console.error(zp.slice(0, 28), t.name, 'server', srv.success, 'max Δfrac', rec.max_dFrac_pp.toFixed(2), 'pp, max Voigt Δarea', rec.max_voigt_dArea_pct.toFixed(1), '%');
    55	  }
    56	}
    57	const ok = out.targets.filter(r => r.server_success);
    58	const q = v => { v = [...v].sort((a, b) => a - b); return { median: v[Math.floor(v.length / 2)], p90: v[Math.floor(0.9 * (v.length - 1))], max: v[v.length - 1] }; };
    59	out.summary = { n_tabs: out.targets.length, n_converged: ok.length, dFrac_pp: q(ok.map(r => r.max_dFrac_pp)), gt_1pp: ok.filter(r => r.max_dFrac_pp > 1).length, voigt_dArea_pct: q(ok.map(r => r.max_voigt_dArea_pct)) };
    60	console.error(JSON.stringify(out.summary));
    61	fs.writeFileSync(process.argv[2] || path.join(ROOT, 'docs/findings/a03/voigt_saved_vs_refit.json'), JSON.stringify(out, null, 1));
   480	(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
   481	generator `scripts/local_server_gap.js`): weighted, it matches the server on
   482	GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
   483	components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
   484	U 4f targets where both engines reach the same minimum every component
   485	agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
   486	to 20.8 % area on the Voigt satellites); it still differs on the other 4
   487	U 4f targets (satellite areas up to 8.9 %, 0.77 pp) for two reasons,
   488	separated by a control arm (the server with every LA m held at its start):
   489	on one target the `caM` clamp (`caM` held at its start locally while the
   490	server fits m continuously; holding m on the server closes the gap), on
   491	three the local descent stopping at a χ²ᵣ 10–13 % above the server's from
   492	the same start with the same free parameters — a worse minimum, the
   493	"several minima" case (both engines' amplitude floor is 0 since unit
   494	step (b)). Both engines weight by
   495	√intensity whether the data are counts or CPS (a convention, not a
   496	calibrated uncertainty for rates); the formula is the same but the inputs
   497	are not bit-identical, because `uploadToBackend` rounds intensities to
   498	2 dp before the server weights them. A03 is done and the designation
   499	STAYS on both grounds; the `caM` clamp is the next unit, the worse-minimum
   500	outcome is recorded for the local-engine work after it, and the label is
   501	reconsidered only on a re-measurement after both. (The amplitude-bound change
   155	  }
   156	  const ipChild = res.individual_peaks.find(ip => String(ip.id) === '2');
   157	  assert.equal(ipChild.params.gl_ratio.value, 0.5);
   158	  assert.ok(ipChild.params.gl_ratio.expr, 'the child’s η is an expression on the parent');
   159	});
   160	
   161	// Codex round 1 reproduced two builder defects at ZERO endpoints: `p.glMix || 50`
   162	// sent an asym-GL mix of 0 as 50 and `p.dsAlpha || 0.1` a DS alpha of 0 as
   163	// 0.1 — values the page never drew; locked, the server held the substitute
   164	// and the drawn curve differed from the fitted one by 6.9 % / 8.8 % of
   165	// amplitude. Every shape parameter is now round-tripped LOCKED AT ITS BOUNDS.
   166	const LOCKED_AT_BOUNDS = [
   167	  { label: 'GL mix 0 locked',          truth: { shape: 'GL', glMix: 0, fixGlMix: true } },
   168	  { label: 'GL mix 100 locked',        truth: { shape: 'GL', glMix: 100, fixGlMix: true } },
   169	  { label: 'asym-GL mix 0 locked',     truth: { shape: 'asym-GL', glMix: 0, asymmetry: 0.3, fixGlMix: true } },
   170	  { label: 'asym-GL asymmetry 0 locked', truth: { shape: 'asym-GL', glMix: 40, asymmetry: 0, fixAsymmetry: true } },
   171	  { label: 'DS alpha 0 locked',        truth: { shape: 'DS', dsAlpha: 0, dsGamma: 0.2, fixDsAlpha: true } },
   172	  { label: 'DS gamma 0 locked',        truth: { shape: 'DS', dsAlpha: 0.2, dsGamma: 0, fixDsGamma: true } },
   173	  { label: 'DS alpha 0.5 locked',      truth: { shape: 'DS', dsAlpha: 0.5, dsGamma: 0.2, fixDsAlpha: true } },
   174	];
   175	for (const c of LOCKED_AT_BOUNDS) {
   176	  test(`locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — ${c.label}`, () => {
   177	    const { res, peaks, specs } = roundTrip(c.truth.shape, { truth: c.truth, start: {} });
   178	    const p = peaks[0];
   179	    if (p.fixGlMix) { assert.equal(specs[0].gl_ratio, c.truth.glMix / 100); assert.equal(res.individual_peaks[0].params.gl_ratio.vary, false); assert.equal(p.glMix, c.truth.glMix); }
   180	    if (p.fixAsymmetry) { assert.equal(specs[0].asymmetry, c.truth.asymmetry); assert.equal(res.individual_peaks[0].params.asymmetry.vary, false); }
   181	    if (p.fixDsAlpha) { assert.equal(specs[0].alpha, c.truth.dsAlpha); assert.equal(res.individual_peaks[0].params.alpha.vary, false); assert.equal(p.dsAlpha, c.truth.dsAlpha); }
   182	    if (p.fixDsGamma) { assert.equal(specs[0].gamma_asym, c.truth.dsGamma); assert.equal(res.individual_peaks[0].params.gamma_asym.vary, false); }
   183	    const rel = maxRelDiff(env.evalPeakArray(res.energy, p), res.individual_peaks[0].y, p.amplitude);
   184	    assert.ok(rel < TIGHT_TOL, `${c.label}: drawn vs fitted curve differ by ${(rel * 100).toExponential(3)} % of amplitude`);
   185	  });
   186	}
   187	
   188	test('a locked GL mix is sent locked, held by the server and drawn at the locked value', () => {
def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
    """The seed for every random draw of one fit: a pure function of the
    NUMBERS THE OPTIMISER IS HANDED — energies, counts and the computed
    background curve (little-endian float64), the lineshape of each component
    in fitting order, each lmfit parameter's effective role, the method,
    solver options and ``n_perturb``.

    A parameter's role is what it can do to the fit: a constrained one is its
    expression (its own start value and bounds are overridden), a fixed one
    is its value (its bounds cannot act), a free one is its value and bounds.
    Settings are hashed by their EFFECT, never as sent, so nothing the fit
    ignores can change the draws: a peak's name or colour, the
    ``fix_gl_ratio`` the page still sends for a Gaussian, stale shape
    parameters kept after a shape switch, the ``endpoint_avg`` a linear
    background does not use, anchor order, and the peaks' internal IDs —
    parameter names and constraint references are rewritten by component
    POSITION (``prefixes`` lists each component's lmfit prefix in fitting
    order), because the page never reuses an ID and the same model rebuilt
    after deleting a peak would otherwise fit differently. (Measured in review: each such
    no-op edit moved an area fraction by 15-45 percentage points while the
    request was hashed as sent.) It is a seed, not an identity: 32 bits
    collide, never use it as a cache key. Changing this derivation changes
    what saved projects regenerate: bump the version tag and say so.
    """
    kws = dict(fit_kws or {})
    solver = {k: v for k, v in dict(kws.pop("fit_kws", None) or {}).items() if k != "seed"}
    # longest prefix first so "p1_" cannot match inside "p11_"
    alias = sorted(((pre, f"c{k}_") for k, pre in enumerate(prefixes)), key=lambda a: -len(a[0]))

    def by_position(text):
        for pre, pos in alias:
            text = re.sub(r"(?<![A-Za-z0-9_])" + re.escape(pre), pos, text)
        return text

    roles = []
    for name, par in params.items():
        name = by_position(name)
        if par.expr is not None:
            roles.append([name, "expr", by_position(par.expr)])
        elif not par.vary:
            roles.append([name, "fixed", par.value])
        else:
            roles.append([name, "free", par.value, par.min, par.max])
    rest = _canonical({"shapes": list(shapes), "params": roles, "fit_kws": kws, "solver": solver,
                       "n_perturb": n_perturb})
    h = hashlib.sha256(b"xps-fit-seed-v1\0")
    for arr in (x, counts, background):
        a = np.ascontiguousarray(arr, dtype="<f8") + 0.0       # -0.0 -> 0.0 (the CSV path keeps "-0.00")
        h.update(str(a.size).encode() + b"\0" + a.tobytes())
    h.update(json.dumps(rest, sort_keys=True, separators=(",", ":"), allow_nan=True).encode())
    return int.from_bytes(h.digest()[:4], "little")            # 32 bits: what scipy's seed accepts


# ── Scattered starts: is the fit the only solution the data allow? ────────────
    p._backendParams = ipeak.params;
  }
  // the verdict describes the model as it now stands (values applied) in its fit context
  _applySupport(state.peaks, result, _startsLiveKey());
}

// LEVENBERG-MARQUARDT FITTING (local JS engine)
// ═══════════════════════════════════════════════════
// ═══════════════════════════════════════════════════
// BKGRD SUB VIEW TOGGLE
// ═══════════════════════════════════════════════════
// The pill at id="bg-sub-pill" / id="bg-sub-toggle" can be in three
// visual states (active, inactive, disabled). The disabled state
// applies whenever subtraction is meaningless: no spectrum loaded,
// bg-type is "none", or a fit is running. The pill's checked state
// is preserved across disable cycles so users get their preference
// back when bg becomes available again.

let _bgSubFitInFlight = false;

// IDs of overlay controls that don't compose with subtracted view
// (they're full-spectrum / non-bg-aware). When subtracted view is
// effectively active we disable them with the existing app
// convention (opacity 0.4 + disabled attr + title tooltip), so users
// see why their checkbox appears inert. Identical pattern to how
// `shirley-iter` is gated when bg-type doesn't need iteration.
const _BG_SUB_DEPENDENT_CONTROL_IDS = ['smooth-enable', 'deriv1-enable', 'deriv2-enable'];

function _isBgSubViewActive() {
  const toggle = document.getElementById('bg-sub-toggle');
  if (!toggle || !toggle.checked) return false;
  // Even if the pill is checked, fall back to raw view when bg is
  // unavailable (defensive: covers the moment between bg-type=none
  // and the pill recompute, and any transient bg gap).
  const bgType = document.getElementById('bg-type')?.value || 'shirley';
  if (bgType === 'none') return false;
4225:function evalPeakArray(beArr, p) {
6313:function applyBackendResult(result) {

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir=\"/tmp\"
import fitting,numpy as np,json
from pathlib import Path
from autofit.reference import peak_to_backend_spec,load_project_tabs
x=np.arange(12.,0.,-.05); y=np.ones(len(x))*20+fitting._SHAPE_FUNCS[\"pseudo_voigt_gl\"](x,amplitude=3000,center=6,fwhm=1.4,gl_ratio=.5)
for shape,params,key,oldvalue in [(\"asym-GL\",dict(glMix=0,asymmetry=.3),\"gl_ratio\",.5),(\"DS\",dict(dsAlpha=0,dsGamma=.2),\"alpha\",.1)]:
 p=dict(id=1,name=\"p\",shape=shape,center=6,amplitude=3000,fwhm=1.4,**params)
 new=peak_to_backend_spec(p,[p]); old=dict(new,**{key:oldvalue})
 for name,spec in [(\"before\",old),(\"after\",new)]:
  r=fitting.run_fit(x,y,[spec],background_method=\"none\",n_perturb=0)
  print(shape,name,r[\"random_seed\"])
for z in Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\"):
 for t in load_project_tabs(z):
  if not t.get(\"fitResult\") or not any(p.get(\"shape\")==\"Voigt\" for p in t.get(\"peaks\",[])): continue
  ui=t[\"ui\"];sh=t.get(\"ccShift\",0);lo,hi=sorted([float(ui[\"bgStart\"]),float(ui[\"bgEnd\"])])
  b=[b-sh for b in t[\"rawBE\"] if float(ui[\"roiMin\"])<=b-sh<=float(ui[\"roiMax\"])]
  i=[i for i,v in enumerate(b) if lo<=v<=hi];j=[i for i,v in enumerate(b) if lo<=round(v,4)<=hi]
  if i"'!=j: print("BG differs",z.name,t["name"],i[:1],i[-1:],j[:1],j[-1:])
'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 1805ms:
/Users/skyefortier/.matplotlib is not a writable directory
asym-GL before 1848474789
asym-GL after 605972174
DS before 1401145635
DS after 3727927737

 succeeded in 77121ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
TAP version 13
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
ok 1 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1745.422019
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
ok 2 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1715.230564
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
ok 3 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1714.754165
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
ok 4 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1752.549087
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
ok 5 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1752.682145
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
ok 6 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1758.711613
  type: 'test'
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 7 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA # TODO DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit
  ---
  duration_ms: 1907.138437
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA: drawn vs fitted curve differ by 5.462e-3 % of amplitude'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:128:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
not ok 8 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX # TODO LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit
  ---
  duration_ms: 1745.0167
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:123:3'
  failureType: 'testCodeFailure'
  error: 'LACX: drawn vs fitted curve differ by 1.467e-1 % of amplitude'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:128:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
ok 9 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1762.522948
  type: 'test'
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
ok 10 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1795.014952
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — GL mix 0 locked
ok 11 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1738.218702
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — GL mix 100 locked
ok 12 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1810.144471
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — asym-GL mix 0 locked
ok 13 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1781.921122
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — asym-GL asymmetry 0 locked
ok 14 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1756.208468
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS alpha 0 locked
ok 15 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1771.672182
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS gamma 0 locked
ok 16 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1725.973652
  type: 'test'
  ...
# Subtest: locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS alpha 0.5 locked
ok 17 - locked at a bound, the request carries the value the page draws and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1841.199349
  type: 'test'
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
ok 18 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1770.959058
  type: 'test'
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
ok 19 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1734.405382
  type: 'test'
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
ok 20 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1679.200532
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Gaussian
ok 21 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1800.244184
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
ok 22 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1698.156993
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: GL
ok 23 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1731.21708
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: Voigt
ok 24 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1801.656232
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DS
ok 25 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1698.693508
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
ok 26 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1740.731093
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)
not ok 27 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1787.71044
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:174:1'
  failureType: 'testCodeFailure'
  error: 'LACX: frontend vs backend max diff = 0.1496% of amplitude (tol 0.00009999999999999999%)'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:181:10)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (A) frontend vs backend parity: LACX at m=0 (no convolution)
ok 28 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1697.704297
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed
not ok 29 - (A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed # TODO DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above
  ---
  duration_ms: 1762.847806
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:197:1'
  failureType: 'testCodeFailure'
  error: 'DSG_LA: frontend vs backend max diff = 1.7518% of amplitude (tol 0.00009999999999999999%)'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:204:10)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
ok 30 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1812.302174
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
ok 31 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1659.69008
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
ok 32 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1846.185819
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
ok 33 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1653.021782
  type: 'test'
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
ok 34 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1619.216692
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 35 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.307051
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 36 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.124672
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 37 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.400127
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 38 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.139886
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 39 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.180163
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 40 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.246869
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
ok 41 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
  ---
  duration_ms: 10.17185
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 42 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.259918
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:267:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7170.363795150584, rel diff=24.2055%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:274:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (C) evalPeak() has no direct callers outside evalPeakArray()
ok 43 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 2.721101
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
ok 44 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1735.819128
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
ok 45 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1668.657027
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Voigt
ok 46 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1641.663697
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: GL
ok 47 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1733.490564
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
ok 48 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1752.939533
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DS
ok 49 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1702.61362
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
ok 50 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1772.912813
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
ok 51 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1667.063919
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP
not ok 52 - (D) sweep across the fitted range: DSG_LA (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 2049.162854
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:386:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA (m > 0): 36 of 36 parameter combinations diverge; worst 1.129e+55 % of amplitude at {"laAlpha":0.49,"laBeta":2,"laM":0.05}'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:388:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP
not ok 53 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1831.601464
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:386:3'
  failureType: 'testCodeFailure'
  error: 'LACX (m > 0): 81 of 108 parameter combinations diverge; worst 8.941e-1 % of amplitude at {"caAlpha":5,"caBeta":5,"caM":50,"fwhm":0.1}'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:388:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
1..53
# tests 53
# suites 0
# pass 46
# fail 0
# cancelled 0
# skipped 0
# todo 7
# duration_ms 77171.966905

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require(\"child_process\");const orig=cp.execFileSync;cp.execFileSync=(file,args,opts)=>{if(file.includes(\"python\")){if(args[0]===\"-c\"){args=[\"-c\",\"import tempfile; tempfile.tempdir='\\''/tmp'\\'';\\n\"+args[1],...args.slice(2)];}else{args=[\"-c\",\"import tempfile,sys,runpy; tempfile.tempdir='\\''/tmp'\\''; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='\\''__main__'\\'')\",...args];}}return orig(file,args,opts);};const fs=require(\"fs\"),Module=require(\"module\"),path=require(\"path\");const f=path.resolve(\"scripts/voigt_saved_vs_refit.js\");let src=fs.readFileSync(f,\"utf8\").split(\"const out =\")[0]+
"'`const rows=[];for(const zp of fs.readdirSync(DATA).filter(f=>f.endsWith(".proj.zip")).sort()){
const tabs=JSON.parse(execFileSync(PY,["-c","import sys,json;from autofit.reference import load_project_tabs;print(json.dumps(load_project_tabs(sys.argv[1])))",path.join(DATA,zp)],{encoding:"utf8",maxBuffer:1<<26}));
for(const t of tabs){if(!t.fitResult?.be?.length||!t.peaks?.some(p=>p.shape==="Voigt"))continue;
const be=t.rawBE.map(b=>b-(t.ccShift||0)).filter(b=>b>=parseFloat(t.ui.roiMin)&&b<=parseFloat(t.ui.roiMax));
const a=t.peaks.map(p=>area(be,p)), b=t.peaks.map(p=>area(t.fitResult.be,p));const ta=a.reduce((x,y)=>x+y,0),tb=b.reduce((x,y)=>x+y,0);
const d=Math.max(...a.map((x,i)=>Math.abs(100*(x/ta-b[i]/tb))));
if(d>1e-5)rows.push({project:zp,tab:t.name,dFrac_pp:d,maxAreaPct:Math.max(...a.map((x,i)=>Math.abs(100*(x/b[i]-1)))),peak0:{scriptArea:a[0],pageArea:b[0]}});
}}
console.log(JSON.stringify(rows.sort((a,b)=>b.dFrac_pp-a.dFrac_pp),null,2));`;
const m=new Module(f,module);m.filename=f;m.paths=module.paths;m._compile(src,f);'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 1390ms:
[
  {
    "project": "UCl4_on_graphite.proj.zip",
    "tab": "U4f Scan_1",
    "dFrac_pp": 0.09282396185926745,
    "maxAreaPct": 1.2231832112090446,
    "peak0": {
      "scriptArea": 60320.07742988709,
      "pageArea": 61067.03920097587
    }
  },
  {
    "project": "UCl4_on_graphite.proj.zip",
    "tab": "U4f Scan",
    "dFrac_pp": 0.05775022151539577,
    "maxAreaPct": 0.836682383253462,
    "peak0": {
      "scriptArea": 55491.044124162545,
      "pageArea": 55959.24527114783
    }
  },
  {
    "project": "UCl4_on_graphite.proj.zip",
    "tab": "U4f Scan_2",
    "dFrac_pp": 0.02456911314775434,
    "maxAreaPct": 0.30983828289152804,
    "peak0": {
      "scriptArea": 50052.93523927436,
      "pageArea": 49898.331106980964
    }
  },
  {
    "project": "UCl4_on_graphite.proj.zip",
    "tab": "U4f Scan_4",
    "dFrac_pp": 0.023852967817827864,
    "maxAreaPct": 0.36658907033612076,
    "peak0": {
      "scriptArea": 42049.05600146483,
      "pageArea": 42203.77041106153
    }
  },
  {
    "project": "4-GTA UCl4-BN.proj.zip",
    "tab": "U4f Scan_8",
    "dFrac_pp": 0.003992512185246877,
    "maxAreaPct": 0.028020403601414223,
    "peak0": {
      "scriptArea": 19231.973430441005,
      "pageArea": 19226.586063427258
    }
  },
  {
    "project": "4-GTA UCl4-BN.proj.zip",
    "tab": "U4f Scan_3",
    "dFrac_pp": 0.0035291913231039196,
    "maxAreaPct": 0.04347948831973092,
    "peak0": {
      "scriptArea": 17906.594339018466,
      "pageArea": 17901.801268632767
    }
  },
  {
    "project": "4-GTA UCl4-BN.proj.zip",
    "tab": "U4f Scan_7",
    "dFrac_pp": 0.0034370021660512506,
    "maxAreaPct": 0.025336566783129566,
    "peak0": {
      "scriptArea": 22391.197426882514,
      "pageArea": 22396.34476611341
    }
  },
  {
    "project": "4-GTA UCl4-BN.proj.zip",
    "tab": "U4f Scan_4",
    "dFrac_pp": 0.0005168213518369491,
    "maxAreaPct": 0.01965730801900545,
    "peak0": {
      "scriptArea": 20756.40546987095,
      "pageArea": 20755.7551971139
    }
  },
  {
    "project": "4-GTA UCl4-BN.proj.zip",
    "tab": "U4f Scan_2",
    "dFrac_pp": 0.00037023606584973834,
    "maxAreaPct": 0.002576099802187315,
    "peak0": {
      "scriptArea": 18693.899809857474,
      "pageArea": 18693.418248746944
    }
  },
  {
    "project": "4-GTA UCl4-BN.proj.zip",
    "tab": "U4f Scan_1",
    "dFrac_pp": 0.00021955306068327518,
    "maxAreaPct": 0.009415796538791987,
    "peak0": {
      "scriptArea": 18827.906560058538,
      "pageArea": 18827.58501667952
    }
  },
  {
    "project": "4-GTA UCl4-BN.proj.zip",
    "tab": "U4f Scan_0",
    "dFrac_pp": 0.00012994750205608252,
    "maxAreaPct": 0.00627284520200444,
    "peak0": {
      "scriptArea": 19116.710283298875,
      "pageArea": 19116.49530808943
    }
  }
]

exec
/bin/zsh -lc "nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | sed -n '85,110p'; nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | sed -n '156,202p'; sed -n '11303,11380p' templates/index.html; sed -n '184,222p' autofit/parity.py; sed -n '4220,4244p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    85	`scripts/bg_window_worked_example.py`, CLAUDE.md, `tests/js/fit_acceptance.test.js`.
    86	
    87	## 4. Two harnesses that would have caught it
    88	
    89	- `tests/js/lineshape_roundtrip.test.js` (+ `lineshape_roundtrip_backend.py`):
    90	  for every shape, synthetic data from a truth peak, a perturbed start,
    91	  request built by the PAGE's `peakToBackendSpec`, fitted by
    92	  `fitting.run_fit` (no background, Trust-Region), applied by the page's
    93	  `_applyBackendParams`, then `evalPeakArray` on the fitted grid must equal
    94	  `individual_peaks[].y` within 1e-6 of amplitude. Plus: the Voigt request
    95	  and write-back pins, a linked Voigt pair, a locked GL mix, and the Python
    96	  twin deep-equal to the page's builder for every shape and a link. Run
    97	  against main's page it fails on Voigt (0.93 % of amplitude), the Voigt
    98	  pins and the linked pair; on the branch 10 pass, 2 todo (below).
    99	- `tests/js/lineshape_parity.test.js` section (D): each shape's FREE
   100	  parameters swept across `_make_peak_params`'s bounds (η 0–1, asymmetry
   101	  0–1, DS α 0–0.5 / γ 0–5, DS+G α 0–0.49 / β 0.05–2 / m 0.05–4, LA α,β
   102	  0.1–5 / m 0–499, fwhm 0.1–15), one bridge call per shape.
   103	- `tests/test_voigt_contract.py`: the twin, `run_fit` holding η and
   104	  returning the 0.5 curve, the seed.
   105	
   106	## 5. What the sweep found
   107	
   108	| shape | result |
   109	|---|---|
   110	| Gaussian, Lorentzian, Voigt (glMix 0 and 100 ignored), GL, asym-GL, DS | ≤ 6.1e-16 of amplitude at every combination |
   156	minimum than Trust-Region on three of nine U 4f targets. The `caM` clamp
   157	remains the next unit; the worse-minimum finding is recorded in findings
   158	§7 for the local-engine work that follows it. Wording in the page updated
   159	to say so (LA components and several minima; no longer Voigt).
   160	
   161	## 7. Release-note line
   162	
   163	Voigt components are now fitted at the fixed 50/50 mix the page has always
   164	drawn; until now Run Fit let their mix vary on the server and the page
   165	reported the 50/50 curve's area under the other mix's parameters (up to
   166	20 % off per component). Re-fitting a saved project with Voigt components
   167	moves an area fraction by 0.35 pp at the median and 0.69 pp at most on the
   168	55 committed tabs (a Voigt's own area by 4.6 % at the median, 15 % at
   169	most). Use GL to fit the mix. Also fixed: a GL mix of exactly 0 (asym-GL)
   170	or a DS α of exactly 0 was sent to the server as 50 / 0.1.
   171	
   172	## 8. Verification
   173	
   174	- `tests/test_voigt_contract.py` 4 passed; full `pytest tests/` — see §9.
   175	- JS suite: `node --test tests/js/*.test.js` (the directory form does not
   176	  run in this node): see §9.
   177	- Browser check (`browser_check_a03.py`, dev gunicorn :5151 from the
   178	  worktree, re-run after round 1): the request carries `gl_ratio 0.5, fix_gl_ratio true` for
   179	  both Voigt components; the server returns `vary: false, 0.5`; drawn vs
   180	  fitted curve 1.3e-13 of amplitude for the Voigts (LACX 5.6e-3 — the caM
   181	  rounding); the Results area of a Voigt equals the server curve's to
   182	  0.0000 % (LACX −0.66 %, the same rounding); the chart dataset is the drawn curve; `glMix` unchanged in the
   183	  live model and the saved record; Batch Fit onto U4f Scan_1 converges
   184	  locally; no page errors.
   185	
   186	## 9. Codex rounds
   187	
   188	**Round 1 (`docs/autofit/codex/a03_voigt_eta_verdict_run{A,B}.md`): NO-GO ×2,
   189	no blocker, converging findings.** Fixed:
   190	1. MAJOR — the measurement script took the target file's own Voigt specs as
   191	   the "old" arm, so a target file regenerated with the A03 builder would
   192	   have made both arms identical. Both requests are now constructed
   193	   explicitly; the generator is named correctly (`.js`); re-run (§2a).
   194	2. MAJOR — the release-note number was a server-curve/trapezoid comparison
   195	   of two refits, not the page's saved numbers against the page's refit
   196	   numbers. Replaced by `scripts/voigt_saved_vs_refit.js` (§2b); the old
   197	   rows relabelled as what they are.
   198	3. MAJOR/MINOR — the builder sent an asym-GL mix of 0 as 50 and a DS α of 0
   199	   as 0.1 (`p.glMix || 50`, `p.dsAlpha || 0.1`; the Python twin likewise);
   200	   locked, the server held the substitute and the drawn curve differed from
   201	   the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders
   202	   (only a non-number falls back); the round-trip test now locks every shape
      tip.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - 320)) + 'px';
      tip.classList.add('visible');
    }, DELAY);
  }, true);
  document.addEventListener('mouseleave', function (e) {
    if (!(e.target instanceof Element) || !e.target.closest('[data-xps-tip]')) return;
    clearTimeout(timer);
    const tip = document.getElementById('xps-tooltip');
    if (tip) tip.classList.remove('visible');
  }, true);
})();

// ═══════════════════════════════════════════════════
// UNCERTAINTY VALIDATION
// ═══════════════════════════════════════════════════
function _validateUncertainties() {
  if (!state.fitResult?.backendResult?.individual_peaks) return { warnings: [], info: [] };
  const warnings = [];
  const info = [];
  const stderrMap = _buildStderrMap(state.fitResult);
  const preFit = state.fitResult._preFit || {};
  // Map backend param names to pre-fit property names
  const nameMap = { center: 'center', fwhm: 'fwhm', fwhm_l: 'fwhm', amplitude: 'amplitude', gl_ratio: 'glMix' };

  for (const [rawId, params] of Object.entries(stderrMap)) {
    const p = getPeak(Number(rawId));
    if (!p) continue;
    // Rule 0: the fit did not determine this component at all. Reported once,
    // here, instead of the per-parameter alarms (or, after Auto-Fit's centre
    // lock, the neutral "locked" note) that would otherwise misdescribe it.
    if (_isUnsupported(p)) {
      warnings.push(`<li><b>${_escHtml(p.name)}:</b> ${_UNSUPPORTED_LABEL} — with the other components held as fitted, removing it does not make the fit significantly worse${p.support.f != null ? ' (F = ' + p.support.f.toFixed(1) + ', threshold 10)' : ''}. Its centre, width and uncertainties are not reported. Try another starting position or width, lock the centre where chemistry says it belongs, or drop the component.</li>`);
      continue;
    }
    const init = preFit[Number(rawId)] || {};

    for (const [pName, pData] of Object.entries(params)) {
      if (!['center','fwhm','fwhm_l','amplitude','gl_ratio'].includes(pName)) continue;
      const val = pData.value;

      // Locked or linked: skip the alarm-style movement/stderr checks.
      //   - linked satellite (expr set): tied to master via lmfit expr; intentional
      //     by construction → silent
      //   - genuinely locked (vary=false, no expr): user or auto-fit set this lock
      //     → neutral info note pointing at the padlock toggle, not an alarm
      if (pName === 'gl_ratio' && p.shape === 'Voigt') {
        // A03: a Voigt's mix is fixed by the SHAPE (η = 0.5), not by a padlock — there is none to unlock.
        info.push(`<li><b>${_escHtml(p.name)} / mix:</b> fixed at 50/50 by the Voigt shape — choose GL to fit the mix.</li>`);
        continue;
      }
      if (pData.vary === false) {
        const isLinked = pData.expr != null && pData.expr !== '';
        if (!isLinked) {
          info.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> locked — unlock the padlock to refine.</li>`);
        }
        continue;
      }

      // Rule 1: parameter sitting at its bound (within 1% of range from min or max)
      const lo = pData.min, hi = pData.max;
      if (lo != null && hi != null && isFinite(lo) && isFinite(hi)) {
        const range = hi - lo;
        if (range > 0) {
          if ((val - lo) <= range * 0.01) {
            warnings.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> at lower bound (${lo}). Widen bounds or lock this parameter.</li>`);
            continue;
          }
          if ((hi - val) <= range * 0.01) {
            warnings.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> at upper bound (${hi}). Widen bounds or lock this parameter.</li>`);
            continue;
          }
        }
      }

      // Rule 2: param was free (vary=true, no expr) but lmfit returned no
      // stderr AND the value barely moved → covariance matrix singular near
      // this parameter. Distinct from "locked" (handled above) and from
      // "converged at start with valid stderr" (silent — normal convergence).
    return float(np.max(np.abs(model + bg - fittedY)) / scale)


def refit_record(rf: ReferenceFit, start: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Deterministic seeded refit (leastsq, no perturbation) from the saved
    parameters.  Returns a serializable record for fixture freezing; each
    peak also carries ``params`` (every server parameter's fitted value) so
    the record can be the START of another refit: with ``start`` (a record
    from this function) the saved peaks are first overwritten with that
    record's parameters through the page's write-back twin, exactly as the
    page holds a model after Run Fit.
    """
    import copy
    peaks = rf.peaks
    if start is not None:
        peaks = copy.deepcopy(rf.peaks)
        by_id = {str(pk["id"]): pk for pk in start["peaks"]}
        for p in peaks:
            pk = by_id.get(str(p["id"]))
            if pk is not None and pk.get("params"):
                apply_backend_params(p, pk["params"])
    i0, i1 = rf.bg_indices()
    res = run_fit(
        rf.roi_be,
        rf.roi_intensity,
        [peak_to_backend_spec(p, peaks) for p in peaks],
        background_method=rf.bg_method,
        bg_start_idx=i0,
        bg_end_idx=i1,
        endpoint_avg=rf.endpoint_avg,
        n_perturb=0,
    )
    peaks = []
    for ip in res["individual_peaks"]:
        par = ip["params"]
        peaks.append({
            "id": ip["id"],
            "center": par["center"]["value"],

// Compute per-peak intensities across an array of BE values. Special-cases
// LACX with non-zero m so the Gaussian convolution sees the whole grid, and
// DSG_LA below the 0.001 delta-kernel threshold so the normalisation sees
// the whole grid (see dsgDeltaKernel_array above).
function evalPeakArray(beArr, p) {
  if (p.shape === 'LACX' && Math.round(p.caM || 0) > 0) {
    const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
    const out = new Array(beArr.length);
    const amp = p.amplitude;
    for (let i = 0; i < beArr.length; i++) out[i] = amp * yArr[i];
    return out;
  }
  if (p.shape === 'DSG_LA' && (p.laM || 0) < 0.001) {
    // (p.laM || 0): negative laM matches the backend's clamp-to-0-then-delta
    // path; NaN/undefined coerce to 0 → delta, which peakToBackendSpec's
    // non-finite→default sanitisation makes unreachable in fit flows.
    const yArr = dsgDeltaKernel_array(beArr, p.center, p.laAlpha, p.laBeta);
    const amp = p.amplitude;
    return yArr.map(v => amp * v);
  }
  return beArr.map(x => evalPeak(x, p));
}

function evalAllPeaks(beArray, peaks) {

exec
/bin/zsh -lc 'tail -100 docs/autofit/codex/a03_voigt_eta_verdict_runA.md; tail -90 docs/autofit/codex/a03_voigt_eta_verdict_runB.md; rg --files docs/findings/a03; git status --short' in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
cp.execFileSync=function(file,args,opts){
 if(file.includes('\\''python'\\'')){
   if(args[0]==='\\''-c'\\'') {
     args=['\\''-c'\\'','\\''import tempfile; tempfile.tempdir=\"/tmp\"; '\\''+args[1],...args.slice(2)];
     const tabs=JSON.parse(orig(file,args,opts));
     return JSON.stringify(tabs.filter(t=>['\\''U4f Scan'\\'','\\''U4f Scan_6'\\''].includes(t.name)));
   }
   else args=['\\''-c'\\'','\\''import tempfile,sys; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; code=open(sys.argv[0]).read().replace(\"fit_kws={\", \"n_perturb=3, fit_kws={\"); exec(compile(code,sys.argv[0],\"exec\"))'\\'',...args];
 }
 return orig(file,args,opts);
};
fs.writeFileSync=function(p,data){
 const r=JSON.parse(data); for(const [region,rows] of Object.entries(r.regions)) console.log(region,JSON.stringify(rows.map(x=>({target:x.target,chi:x.server_chi2r,area:x.max_dArea_pct,frac:x.max_dFrac_pp,m:x.comps.filter(c=>c.shape==='\\''LACX'\\'').map(c=>c.server.caM)}))));
};
require('\\''./scripts/local_server_gap.js'\\'');
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 2429ms:
/Users/skyefortier/.matplotlib is not a writable directory
U4f U4f Scan_6 local true 2.657 server true 2.798 max Δcentre 28.8 meV, ΔFWHM 15.81 %, Δarea 8.88 %, Δfrac 0.77 pp
C1s []
U4f [{"target":"U4f Scan_6","chi":2.797581088893732,"area":8.88303774390109,"frac":0.7658566210456907,"m":[9.99564981324184,9.99564981324184]}]

codex
All region parity batteries pass: 118 tests. Refit-from-refit is a meaningful stationarity check, and the frozen fixture remains an independent regression check.

The main concerns are the measurement claims and missing endpoint coverage. Keeping Voigt fixed at 0.5 preserves its existing contract, and retaining “starting point” is supported. The evidence does not yet isolate the entire residual to caM.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const cp=require('\\''child_process'\\''),fs=require('\\''fs'\\''),orig=cp.execFileSync;
cp.execFileSync=function(file,args,opts){
 if(args[0]==='\\''-c'\\''){
  const tabs=JSON.parse(orig(file,['\\''-c'\\'','\\''import tempfile; tempfile.tempdir=\"/tmp\"; '\\''+args[1],...args.slice(2)],opts));
  return JSON.stringify(tabs.filter(t=>['\\''U4f Scan'\\'','\\''U4f Scan_6'\\''].includes(t.name)));
 }
 const d=JSON.parse(opts.input); d.peaks.forEach(p=>{if(p.shape==='\\''LACX'\\'')p.fixCaM=true});
 opts={...opts,input:JSON.stringify(d)};
 return orig(file,['\\''-c'\\'','\\''import tempfile,sys,runpy; tempfile.tempdir=\"/tmp\"; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name=\"__main__\")'\\'',...args],opts);
};
fs.writeFileSync=(p,data)=>{const r=JSON.parse(data); console.log(JSON.stringify(r.regions.U4f.map(x=>({target:x.target,localChi:x.local_chi2r,serverChi:x.server_chi2r,area:x.max_dArea_pct,frac:x.max_dFrac_pp,m:x.comps.filter(c=>c.shape==='\\''LACX'\\'').map(c=>c.server.caM)}))))};
require('\\''./scripts/local_server_gap.js'\\'');
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 2222ms:
/Users/skyefortier/.matplotlib is not a writable directory
U4f U4f Scan_6 local true 2.657 server true 2.634 max Δcentre 3.7 meV, ΔFWHM 1.31 %, Δarea 1.36 %, Δfrac 0.07 pp
[{"target":"U4f Scan_6","localChi":2.657291813593791,"serverChi":2.6341642390705946,"area":1.3594139989251186,"frac":0.06960876701660942,"m":[8.19934520780095,8.19934520780095]}]

codex
No BLOCKER found. Two MAJOR measurement defects prevent approval of A03 as documented.

1. **MAJOR — Regenerating inputs destroys the “old free-η” baseline.** [scripts/voigt_eta_measure.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:59) copies the input specs into `free` without restoring `gl_ratio=0.3, fix_gl_ratio=false`. The committed target generator extracts the **current page builder**, so regenerated Voigt specs already contain held 0.5. I verified this. Both measurement arms then fit the same request, producing zero differences instead of the committed summary. Explicitly construct both contracts and make regeneration self-contained; the documented `.py` target generator also does not exist—the generator is `.js`.

2. **MAJOR — The release-note numbers do not measure changes from a saved project’s displayed fractions.** [scripts/voigt_eta_measure.py:79](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:79) uses trapezoidal integration, retains server curves for non-Voigt components, and compares against a newly optimized free-η fit. The page uses rectangular integration and rounded LA smoothing. Furthermore, regenerating the 90 targets yields **48 own-model starts and 42 Batch Fit starts**, not 90 saved-tab refits. For a saved U 4f model containing LA components, neither baseline nor fraction denominator necessarily matches the screen. Measure saved page peaks versus applied refit peaks using page evaluation and integration before calling **0.30 pp / 1.02 pp** the student-visible migration impact.

3. **MINOR — The new harness misses real request/lock failures at zero endpoints.** [tests/js/lineshape_roundtrip.test.js:161](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:161) tests a locked GL mix only at 30; the sweep uses its own parameter mapping. Using the new round-trip machinery, I reproduced:
   - asym-GL, `glMix=0`, `fixGlMix=true`: request substitutes 0.5; drawn/fitted discrepancy **6.88% of amplitude**.
   - DS, `dsAlpha=0`, `fixDsAlpha=true`: request substitutes 0.1; discrepancy **8.80%**.

   These builder defects predate A03, but the claimed coverage misses them. Add endpoint lock cases and explicitly track these gaps. Comparing two matching twins cannot establish that their shared defaults are correct.

4. **MINOR — Voigt now offers an impossible unlock instruction.** Holding η at [templates/index.html:6235](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:6235) triggers `_validateUncertainties`’ generic “gl_ratio: locked — unlock the padlock to refine.” A supported, unlinked Voigt has no mix padlock. Describe the fixed shape contract and direct the user to GL instead.

5. **MINOR — Several documented numbers contradict the committed artifacts.** [plan:111](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:111) says χ²ᵣ differs by 8–20%. For Scan_4/5/6/8, the JSON gives **+9.57%, +10.07%, −5.01%, +12.74%**, relative to server χ²ᵣ. The request-builder comment says **24%** area error versus the summary’s **20.11%**; row A says **1.60 pp** versus **1.61 pp**. Correct the repeated claims in the plan, findings and CLAUDE.md.

The fixed-0.5 choice is defensible as preserving the explicit shape contract. The measurements do not establish that 0.5 is physically optimal for U 4f, and boundary-hitting alone does not establish non-identifiability.

Retaining **“starting point”** is correct. On Scan_6, using the page’s three perturbations retained the approximately 8.88% area gap. Holding server LA smoothing at its starting value reduced it to 1.36%, supporting caM as a substantial contributor without proving it explains every residual.

Refit-from-refit is meaningful, not tautological; the frozen fixture remains a separate regression check. I found no additional non-Voigt request, `/api/analyze`, or local-engine changes.

Validation: **122 Python tests passed** across the contract and region batteries; **39 JS tests passed, 7 TODOs**. Tests used an in-memory bootstrap for the read-only environment. No files changed.

**VERDICT: NO-GO**
tokens used
106,674
No BLOCKER found. Two MAJOR measurement defects prevent approval of A03 as documented.

1. **MAJOR — Regenerating inputs destroys the “old free-η” baseline.** [scripts/voigt_eta_measure.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:59) copies the input specs into `free` without restoring `gl_ratio=0.3, fix_gl_ratio=false`. The committed target generator extracts the **current page builder**, so regenerated Voigt specs already contain held 0.5. I verified this. Both measurement arms then fit the same request, producing zero differences instead of the committed summary. Explicitly construct both contracts and make regeneration self-contained; the documented `.py` target generator also does not exist—the generator is `.js`.

2. **MAJOR — The release-note numbers do not measure changes from a saved project’s displayed fractions.** [scripts/voigt_eta_measure.py:79](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:79) uses trapezoidal integration, retains server curves for non-Voigt components, and compares against a newly optimized free-η fit. The page uses rectangular integration and rounded LA smoothing. Furthermore, regenerating the 90 targets yields **48 own-model starts and 42 Batch Fit starts**, not 90 saved-tab refits. For a saved U 4f model containing LA components, neither baseline nor fraction denominator necessarily matches the screen. Measure saved page peaks versus applied refit peaks using page evaluation and integration before calling **0.30 pp / 1.02 pp** the student-visible migration impact.

3. **MINOR — The new harness misses real request/lock failures at zero endpoints.** [tests/js/lineshape_roundtrip.test.js:161](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:161) tests a locked GL mix only at 30; the sweep uses its own parameter mapping. Using the new round-trip machinery, I reproduced:
   - asym-GL, `glMix=0`, `fixGlMix=true`: request substitutes 0.5; drawn/fitted discrepancy **6.88% of amplitude**.
   - DS, `dsAlpha=0`, `fixDsAlpha=true`: request substitutes 0.1; discrepancy **8.80%**.

   These builder defects predate A03, but the claimed coverage misses them. Add endpoint lock cases and explicitly track these gaps. Comparing two matching twins cannot establish that their shared defaults are correct.

4. **MINOR — Voigt now offers an impossible unlock instruction.** Holding η at [templates/index.html:6235](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:6235) triggers `_validateUncertainties`’ generic “gl_ratio: locked — unlock the padlock to refine.” A supported, unlinked Voigt has no mix padlock. Describe the fixed shape contract and direct the user to GL instead.

5. **MINOR — Several documented numbers contradict the committed artifacts.** [plan:111](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:111) says χ²ᵣ differs by 8–20%. For Scan_4/5/6/8, the JSON gives **+9.57%, +10.07%, −5.01%, +12.74%**, relative to server χ²ᵣ. The request-builder comment says **24%** area error versus the summary’s **20.11%**; row A says **1.60 pp** versus **1.61 pp**. Correct the repeated claims in the plan, findings and CLAUDE.md.

The fixed-0.5 choice is defensible as preserving the explicit shape contract. The measurements do not establish that 0.5 is physically optimal for U 4f, and boundary-hitting alone does not establish non-identifiability.

Retaining **“starting point”** is correct. On Scan_6, using the page’s three perturbations retained the approximately 8.88% area gap. Holding server LA smoothing at its starting value reduced it to 1.36%, supporting caM as a substantial contributor without proving it explains every residual.

Refit-from-refit is meaningful, not tautological; the frozen fixture remains a separate regression check. I found no additional non-Voigt request, `/api/analyze`, or local-engine changes.

Validation: **122 Python tests passed** across the contract and region batteries; **39 JS tests passed, 7 TODOs**. Tests used an in-memory bootstrap for the read-only environment. No files changed.

**VERDICT: NO-GO**
?? docs/autofit/codex/a03_voigt_eta_verdict_runB.md

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -B -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\",\"-p\",\"no:cacheprovider\",\"tests/autofit/test_c1s_parity_battery.py\",\"-q\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '11332,11346p'; nl -ba scripts/optimizer_disagreement_targets.js | sed -n '51,65p'; nl -ba docs/findings/a03/voigt_eta_summary.txt" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
 11332	    for (const [pName, pData] of Object.entries(params)) {
 11333	      if (!['center','fwhm','fwhm_l','amplitude','gl_ratio'].includes(pName)) continue;
 11334	      const val = pData.value;
 11335	
 11336	      // Locked or linked: skip the alarm-style movement/stderr checks.
 11337	      //   - linked satellite (expr set): tied to master via lmfit expr; intentional
 11338	      //     by construction → silent
 11339	      //   - genuinely locked (vary=false, no expr): user or auto-fit set this lock
 11340	      //     → neutral info note pointing at the padlock toggle, not an alarm
 11341	      if (pData.vary === false) {
 11342	        const isLinked = pData.expr != null && pData.expr !== '';
 11343	        if (!isLinked) {
 11344	          info.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> locked — unlock the padlock to refine.</li>`);
 11345	        }
 11346	        continue;
    51	    for (const tgt of g.slice(1)) {
    52	      const scale = srcMax > 0 ? Math.max(...tgt.rawIntensity) / srcMax : 1;
    53	      const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
    54	      const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
    55	      const r = request('batch', project, tgt.name, cloned, ui, src.ccShift, tgt.rawBE, tgt.rawIntensity, src.name);
    56	      if (r && !seen.has(r.id)) { seen.add(r.id); out.push(r); }
    57	    }
    58	  }
    59	}
    60	process.stdout.write(JSON.stringify(out));
    61	process.stderr.write(`targets: ${out.length} (own ${out.filter(t => t.kind === 'own').length}, batch ${out.filter(t => t.kind === 'batch').length})\n`);
     1	targets 90, both fits converged 90
     2	free eta of 180 Voigt components: 46 at 0 (pure Gaussian), 17 at 1 (pure Lorentzian), 24 within 0.4–0.6
     3	per-Voigt-component DISPLAYED area vs the fitted curve (%): median 11.82, p90 19.18, max 20.11; > 10 % on 103 of 180; displayed high (eta < 0.5) 114, low 66
     4	A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.49, max 1.61; > 1 pp on 35 targets
     5	B. fixed refit vs displayed (what changes on screen), max |delta| pp: median 0.30, p90 0.46, max 1.02; > 1 pp on 1 targets
     6	C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 34 targets
     7	chi2r fixed/free: median 1.09, p90 1.18, max 5.39; fixed lower on 11 targets (the free fit in a worse minimum)

 succeeded in 2794ms:
...........................................................
59 passed in 2.45s

codex
No BLOCKER found. Three MAJOR findings prevent accepting A03 as complete.

1. **MAJOR — The measurement cannot reliably reproduce its old baseline.** [scripts/voigt_eta_measure.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:59) copies incoming specs into `free` without restoring `gl_ratio=0.3, fix_gl_ratio=false`. Regenerate targets using the committed target generator on this branch, and both arms receive held η=0.5: the reported old-vs-new differences collapse to zero. Explicitly construct both contracts; document the actual `.js` target generator and input preparation.

2. **MAJOR — Row B does not measure the claimed saved-project screen change.** [scripts/voigt_eta_measure.py:87](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:87) constructs “displayed” areas from a **new free-η refit**, not the saved model. It also uses server curves for non-Voigt components and trapezoidal integration, whereas Results uses page evaluators and rectangular integration. A U 4f fit with fractional LACX `m` therefore has a different denominator on screen—the plan itself records a −0.66% LACX area discrepancy. The **0.30/1.02 pp release-note claim is not established by this calculation**. Measure saved-page versus refitted-page fractions, or accurately relabel this comparison.

3. **MAJOR — The new harness misses existing request/lock identity failures at swept boundaries.** [tests/js/lineshape_roundtrip.test.js:83](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:83), [tests/js/lineshape_parity.test.js:355](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:355). The sweep builds backend parameters independently of `peakToBackendSpec`; the round trips use interior values. Reusing the new round-trip machinery, I reproduced:
   - Locked asym-GL `glMix=0`: request sends **0.5**, page retains **0**; curve discrepancy **6.88% of amplitude**.
   - Locked DS `dsAlpha=0`: request sends **0.1**, page retains **0**; discrepancy **8.80%**.

   The builder defects predate A03, but the new claimed coverage misses them. Add boundary-and-lock round trips and fix or explicitly track these gaps.

4. **MINOR — Voigt uncertainty guidance offers a nonexistent control.** [templates/index.html:11344](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:11344). After fitting an unlinked Voigt, its newly held `gl_ratio` produces “locked — unlock the padlock to refine.” Voigt has no mix padlock. Explain that the shape fixes η and direct users to GL.

5. **MINOR — Documentation overstates numerical agreement and residual causation.** [plan:111](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:111). The committed JSON gives `(local/server−1)` χ² differences of **+9.57%, +10.07%, −5.01%, +12.74%** for Scan_4/5/6/8, not “8–20%.” Movement in `m` alone does not establish that the entire residual is caused by its local clamp; no controlled comparison establishes that attribution. Also correct the template’s “24%” area comment to the summary’s **20.11%**, and row A’s **1.60 pp** to **1.61 pp**.

The fixed-0.5 contract itself is coherent with the existing page and local-engine semantics. The measurements support correcting the identity mismatch; they do not establish that 0.5 is physically optimal or that boundary η values prove non-identifiability. Keeping **“starting point”** is justified.

Refit-from-refit is a meaningful stability check, not a tautology: it reruns the optimizer after write-back, while the fixture independently pins results. Validation passed: **122 Python tests; 39 JS tests passed, 7 TODO**. The convolved-shape TODO failures reproduced. No files changed.

**VERDICT: NO-GO**
tokens used
101,611
No BLOCKER found. Three MAJOR findings prevent accepting A03 as complete.

1. **MAJOR — The measurement cannot reliably reproduce its old baseline.** [scripts/voigt_eta_measure.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:59) copies incoming specs into `free` without restoring `gl_ratio=0.3, fix_gl_ratio=false`. Regenerate targets using the committed target generator on this branch, and both arms receive held η=0.5: the reported old-vs-new differences collapse to zero. Explicitly construct both contracts; document the actual `.js` target generator and input preparation.

2. **MAJOR — Row B does not measure the claimed saved-project screen change.** [scripts/voigt_eta_measure.py:87](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_eta_measure.py:87) constructs “displayed” areas from a **new free-η refit**, not the saved model. It also uses server curves for non-Voigt components and trapezoidal integration, whereas Results uses page evaluators and rectangular integration. A U 4f fit with fractional LACX `m` therefore has a different denominator on screen—the plan itself records a −0.66% LACX area discrepancy. The **0.30/1.02 pp release-note claim is not established by this calculation**. Measure saved-page versus refitted-page fractions, or accurately relabel this comparison.

3. **MAJOR — The new harness misses existing request/lock identity failures at swept boundaries.** [tests/js/lineshape_roundtrip.test.js:83](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:83), [tests/js/lineshape_parity.test.js:355](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_parity.test.js:355). The sweep builds backend parameters independently of `peakToBackendSpec`; the round trips use interior values. Reusing the new round-trip machinery, I reproduced:
   - Locked asym-GL `glMix=0`: request sends **0.5**, page retains **0**; curve discrepancy **6.88% of amplitude**.
   - Locked DS `dsAlpha=0`: request sends **0.1**, page retains **0**; discrepancy **8.80%**.

   The builder defects predate A03, but the new claimed coverage misses them. Add boundary-and-lock round trips and fix or explicitly track these gaps.

4. **MINOR — Voigt uncertainty guidance offers a nonexistent control.** [templates/index.html:11344](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:11344). After fitting an unlinked Voigt, its newly held `gl_ratio` produces “locked — unlock the padlock to refine.” Voigt has no mix padlock. Explain that the shape fixes η and direct users to GL.

5. **MINOR — Documentation overstates numerical agreement and residual causation.** [plan:111](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md:111). The committed JSON gives `(local/server−1)` χ² differences of **+9.57%, +10.07%, −5.01%, +12.74%** for Scan_4/5/6/8, not “8–20%.” Movement in `m` alone does not establish that the entire residual is caused by its local clamp; no controlled comparison establishes that attribution. Also correct the template’s “24%” area comment to the summary’s **20.11%**, and row A’s **1.60 pp** to **1.61 pp**.

The fixed-0.5 contract itself is coherent with the existing page and local-engine semantics. The measurements support correcting the identity mismatch; they do not establish that 0.5 is physically optimal or that boundary η values prove non-identifiability. Keeping **“starting point”** is justified.

Refit-from-refit is a meaningful stability check, not a tautology: it reruns the optimizer after write-back, while the fixture independently pins results. Validation passed: **122 Python tests; 39 JS tests passed, 7 TODO**. The convolved-shape TODO failures reproduced. No files changed.

**VERDICT: NO-GO**
docs/findings/a03/local_server_gap.log
docs/findings/a03/voigt_saved_vs_refit.json
docs/findings/a03/voigt_saved_vs_refit.log
docs/findings/a03/local_server_gap.json
docs/findings/a03/voigt_eta_summary.txt
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Vcw3S11e' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-LCsN5bhA' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_r2_verdict_runB.md
?? docs/autofit/codex/a03_voigt_eta_recheck_prompt.txt

exec
/bin/zsh -lc "sed -n '7950,8028p' templates/index.html; sed -n '8072,8100p' templates/index.html; sed -n '8140,8208p' templates/index.html; cat docs/findings/a03/local_server_gap.log; rg -n '\"caM\"' docs/findings/a03/local_server_gap.json | head -15; sed -n '350,380p' docs/findings/a03/local_server_gap.json" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
  for (const p of work) {
    if (!p.linked) {
      if (!p.fixCenter)    { freeParams.push(p.center);    paramMap.push({id: p.id, param: 'center'}); }
      if (!p.fixFwhm && p.shape !== 'DSG_LA') { freeParams.push(p.fwhm); paramMap.push({id: p.id, param: 'fwhm'}); }
      if (!p.fixAmplitude) { freeParams.push(p.amplitude); paramMap.push({id: p.id, param: 'amplitude'}); }
      if ((p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) {
        freeParams.push(p.glMix); paramMap.push({id: p.id, param: 'glMix'});
      }
      if (p.shape === 'asym-GL' && !p.fixAsymmetry) {
        freeParams.push(p.asymmetry); paramMap.push({id: p.id, param: 'asymmetry'});
      }
      if (p.shape === 'DS' && !p.fixDsAlpha) {
        freeParams.push(p.dsAlpha); paramMap.push({id: p.id, param: 'dsAlpha'});
      }
      if (p.shape === 'DS' && !p.fixDsGamma) {
        freeParams.push(p.dsGamma); paramMap.push({id: p.id, param: 'dsGamma'});
      }
      if (p.shape === 'DSG_LA') {
        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
      }
      if (p.shape === 'LACX') {
        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
        if (!p.fixCaM)     { freeParams.push(Number.isFinite(p.caM)     ? p.caM     : 50);  paramMap.push({id: p.id, param: 'caM'}); }
      }
    }
  }
  if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');

  // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
  // (owner decision 2026-09-18: zero allowed in both engines; a component at
  // its floor is an explicit outcome). The active-set step holds a parameter
  // pushed into the wall, and paramScale is floored at 1, so a zero amplitude
  // is a valid, stationary point rather than a division by zero.
  function clamp(param, v) {
    if (param === 'fwhm')         return Math.max(0.1, Math.min(15, v));
    if (param === 'amplitude')    return Math.max(0, v);
    if (param === 'glMix')        return Math.max(0, Math.min(100, v));
    if (param === 'asymmetry')    return Math.max(0, Math.min(1, v));
    if (param === 'dsAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'dsGamma')      return Math.max(0, Math.min(5.0, v));
    if (param === 'laAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'laBeta')       return Math.max(0.05, Math.min(2.0, v));
    if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
    if (param === 'caAlpha')      return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caBeta')       return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caM')          return Math.max(0,   Math.min(499, Math.round(v)));
    return v;
  }
  const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];

  function applyParams(params) {
    for (let i = 0; i < params.length; i++) {
      const { id, param } = paramMap[i];
      const p = workPeak(id);
      if (p) p[param] = clamp(param, params[i]);
    }
    // Linked peaks follow their parent: centre + offset, amplitude x ratio,
    // and every lineshape parameter (the same constraint set the backend
    // enforces through lmfit expressions).
    for (const q of work) {
      if (!q.linked) continue;
      const parent = workPeak(q.linked);
      if (!parent) continue;
      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
      if (Number.isFinite(q.linkRatio))  q.amplitude = parent.amplitude * q.linkRatio;
      q.fwhm = parent.fwhm;
      for (const k of LINK_SYNC_KEYS) if (parent[k] !== undefined) q[k] = parent[k];
    }
  }

  function rawResiduals(params) {
    applyParams(params);
    const model = evalAllPeaks(be, work);
    return be.map((_, i) => bgSubtracted[i] - model[i]);
  }
  // the vector, never of the mutable working copy (which the Jacobian loop
  // leaves at its last perturbation — Codex round 5). A centre's scale is
  // its peak's width: from the vector when the width is free, from the
  // (never perturbed) fixed value otherwise.
  const fwhmIndex = {};
  paramMap.forEach((d, k) => { if (d.param === 'fwhm') fwhmIndex[d.id] = k; });
  const paramScale = (j, vec) => {
    const { id, param } = paramMap[j];
    if (param === 'center') {
      const w = fwhmIndex[id] !== undefined ? vec[fwhmIndex[id]] : (workPeak(id) || {}).fwhm;
      return Math.max(0.05, Number.isFinite(w) ? w : 1);
    }
    return Math.max(1, Math.abs(vec[j]));
  };
  // caM is rounded to an integer by its clamp, so a finite difference cannot
  // see it: it is carried at its starting value (inherited behaviour; see the
  // A0 follow-up list) and excluded from the stationarity test.
  const isDiscrete = j => paramMap[j].param === 'caM';
  // MINPACK-style termination: (ftol) actual AND predicted relative
  // reductions both below FTOL, with the linearised model agreeing with
  // the actual reduction; (xtol) relative step below XTOL; (gtol) the
  // largest cosine between the residual and any Jacobian column below
  // GTOL. Tiny steps alone never count. FTOL = 1e-6 (relative chi-square):
  // on real 6-component C1s data with a vanished component the optimiser
  // otherwise crawls a flat valley for thousands of iterations changing
  // chi-square in its 7th digit and no parameter in its 5th.
  const FTOL = 1e-6, XTOL = 1e-8, GTOL = 1e-6, SENS_MIN = 1e-12;
  // CERTIFICATE: a tentative convergence (gtol / ftol / xtol) is accepted
  // only if no feasible move of PROBE_REL (scaled) in any single free
        for (let i = 0; i < r.length; i++) JtJ[a][b] += J[a][i] * J[b][i];
      }
      for (let i = 0; i < r.length; i++) Jtr[a] += J[a][i] * r[i];
    }
    if (!Jtr.every(Number.isFinite) || !JtJ.every(row => row.every(Number.isFinite))) {
      return fail('the model derivative is not finite.', iterations);
    }
    // Sensitivity: a model that does not respond to any free parameter here
    // (e.g. a peak far outside the window) cannot be optimised — that is a
    // failure, not a stationary point.
    let sens = 0;
    for (let j = 0; j < n; j++) if (!isDiscrete(j)) sens = Math.max(sens, JtJ[j][j] * paramScale(j, params) ** 2);
    if (n > 0 && sens / Math.max(chi, 1e-300) < SENS_MIN) {
      return fail('the model has no measurable sensitivity to its free parameters in this region.', iterations);
    }
    // ACTIVE SET: a parameter whose descent direction points into a wall of
    // the parameter box (or that has no sensitivity, or is discrete) is held
    // FIXED for this step. Solving the joint system with such a parameter
    // and then clipping it would leave the other components of the step
    // meaningless and let a tiny "agreed" step pass the ftol test at a
    // non-stationary point (Codex round 2). With r = data - model,
    // d(chi)/dp_j = +2 * (J_j . r), so the descent direction is -sign(J_j . r).
    const active = [];
    let gradCos = 0;
    const rNorm = Math.sqrt(chi);
    for (let j = 0; j < n; j++) {
      if (isDiscrete(j) || !(JtJ[j][j] > 0)) continue;
      if (Jtr[j] !== 0) {
        const probe = clamp(paramMap[j].param, params[j] - Math.sign(Jtr[j]) * 1e-6 * paramScale(j, params));
        if (probe === params[j]) continue;          // blocked by the box
      }
      active.push(j);
      if (rNorm > 0) gradCos = Math.max(gradCos, Math.abs(Jtr[j]) / (Math.sqrt(JtJ[j][j]) * rNorm));
    }
    // Projected gradient test (gtol) over the active set only. A failed
    // certificate has moved the point: restart the iteration so the
    // derivatives and active set are rebuilt there.
    if (gradCos < GTOL) { if (certify()) { converged = true; break; } continue; }
    // Linear model of the residual, for the predicted reduction (ftol test).
    const JtJ0 = JtJ.map(row => row.slice());

    // Marquardt damping, then the DESCENT step on the active set:
    // JtJ_aa . dp_a = -Jt.r_a, dp = 0 for held parameters.
    const m = active.length;
    const A = active.map(a => active.map(b => (a === b ? JtJ[a][a] * (1 + lambda) + 1e-300 : JtJ[a][b])));
    const rhs = active.map(a => -Jtr[a]);
    const dpA = solveLinear(A, rhs, m);
    if (!dpA.every(Number.isFinite)) return fail('the normal equations are singular.', iterations);
    const dp = new Array(n).fill(0);
    active.forEach((a, k) => { dp[a] = dpA[k]; });
    const newParams = params.map((v, i) => clamp(paramMap[i].param, v + dp[i]));
    const step = newParams.map((v, i) => v - params[i]);
    const newChi = chiSq(newParams);

    if (Number.isFinite(newChi) && newChi < chi) {
      const actred = (chi - newChi) / Math.max(chi, 1e-300);
      // predicted reduction of the linearised problem: (2 Jt.r . (-dp) - dp.JtJ.dp) / chi
      let lin = 0, quad = 0;
      for (let a = 0; a < n; a++) {
        lin += Jtr[a] * step[a];
        for (let b = 0; b < n; b++) quad += step[a] * JtJ0[a][b] * step[b];
      }
      const prered = (-2 * lin - quad) / Math.max(chi, 1e-300);
      const relStep = Math.max(0, ...step.map((d, i) => Math.abs(d) / paramScale(i, params)));
      params = newParams;
      chi = newChi;
      acceptedSteps++;
      lambda *= 0.7;
      if (chi === 0 || (prered > 0 && actred <= FTOL && prered <= FTOL && actred / prered <= 2) || relStep <= XTOL) {
C1s C1s Scan_0 local true 4.353 server true 4.357 max Δcentre 3.8 meV, ΔFWHM 0.29 %, Δarea 0.42 %, Δfrac 0.04 pp | m held: server 4.357 Δcentre 3.8 meV, ΔFWHM 0.29 %, Δarea 0.42 %, Δfrac 0.04 pp
C1s C1s Scan_1 local true 13.074 server true 13.066 max Δcentre 2.6 meV, ΔFWHM 0.50 %, Δarea 1.40 %, Δfrac 0.32 pp | m held: server 13.066 Δcentre 2.6 meV, ΔFWHM 0.50 %, Δarea 1.40 %, Δfrac 0.32 pp
C1s C1s Scan_2 local true 4.084 server true 4.087 max Δcentre 3.5 meV, ΔFWHM 0.07 %, Δarea 0.37 %, Δfrac 0.05 pp | m held: server 4.087 Δcentre 3.5 meV, ΔFWHM 0.07 %, Δarea 0.37 %, Δfrac 0.05 pp
C1s C1s Scan_3 local true 4.425 server true 4.432 max Δcentre 1.6 meV, ΔFWHM 0.06 %, Δarea 0.13 %, Δfrac 0.02 pp | m held: server 4.432 Δcentre 1.6 meV, ΔFWHM 0.06 %, Δarea 0.13 %, Δfrac 0.02 pp
C1s C1s Scan_4 local true 18.218 server true 19.056 max Δcentre 41.9 meV, ΔFWHM 8.97 %, Δarea 99.85 %, Δfrac 15.07 pp | m held: server 19.056 Δcentre 41.9 meV, ΔFWHM 8.97 %, Δarea 99.85 %, Δfrac 15.07 pp
C1s C1s Scan_5 local true 4.331 server true 4.332 max Δcentre 0.6 meV, ΔFWHM 0.03 %, Δarea 0.06 %, Δfrac 0.00 pp | m held: server 4.332 Δcentre 0.6 meV, ΔFWHM 0.03 %, Δarea 0.06 %, Δfrac 0.00 pp
C1s C1s Scan_6 local true 5.211 server true 5.230 max Δcentre 2.1 meV, ΔFWHM 0.17 %, Δarea 0.24 %, Δfrac 0.02 pp | m held: server 5.230 Δcentre 2.1 meV, ΔFWHM 0.17 %, Δarea 0.24 %, Δfrac 0.02 pp
C1s C1s Scan_7 local true 7.994 server true 8.016 max Δcentre 1.4 meV, ΔFWHM 0.24 %, Δarea 0.36 %, Δfrac 0.04 pp | m held: server 8.016 Δcentre 1.4 meV, ΔFWHM 0.24 %, Δarea 0.36 %, Δfrac 0.04 pp
C1s C1s Scan_8 local true 2.742 server true 2.741 max Δcentre 0.8 meV, ΔFWHM 0.12 %, Δarea 0.18 %, Δfrac 0.02 pp | m held: server 2.741 Δcentre 0.8 meV, ΔFWHM 0.12 %, Δarea 0.18 %, Δfrac 0.02 pp
U4f U4f Scan_0 local true 2.065 server true 2.055 max Δcentre 1.6 meV, ΔFWHM 0.22 %, Δarea 0.17 %, Δfrac 0.01 pp | m held: server 2.049 Δcentre 2.2 meV, ΔFWHM 0.55 %, Δarea 0.34 %, Δfrac 0.01 pp
U4f U4f Scan_1 local true 2.296 server true 2.267 max Δcentre 4.3 meV, ΔFWHM 1.36 %, Δarea 1.95 %, Δfrac 0.12 pp | m held: server 2.260 Δcentre 4.5 meV, ΔFWHM 1.29 %, Δarea 1.85 %, Δfrac 0.12 pp
U4f U4f Scan_2 local true 1.936 server true 1.940 max Δcentre 1.9 meV, ΔFWHM 1.39 %, Δarea 0.38 %, Δfrac 0.02 pp | m held: server 1.934 Δcentre 1.5 meV, ΔFWHM 0.91 %, Δarea 0.21 %, Δfrac 0.02 pp
U4f U4f Scan_3 local true 1.732 server true 1.732 max Δcentre 3.0 meV, ΔFWHM 2.59 %, Δarea 1.74 %, Δfrac 0.12 pp | m held: server 1.732 Δcentre 1.4 meV, ΔFWHM 0.92 %, Δarea 0.20 %, Δfrac 0.02 pp
U4f U4f Scan_4 local true 1.970 server true 1.798 max Δcentre 26.6 meV, ΔFWHM 5.30 %, Δarea 8.32 %, Δfrac 0.33 pp | m held: server 1.878 Δcentre 13.7 meV, ΔFWHM 2.99 %, Δarea 5.01 %, Δfrac 0.19 pp
U4f U4f Scan_5 local true 2.393 server true 2.174 max Δcentre 4.7 meV, ΔFWHM 4.26 %, Δarea 6.65 %, Δfrac 0.35 pp | m held: server 2.187 Δcentre 6.5 meV, ΔFWHM 3.40 %, Δarea 5.32 %, Δfrac 0.25 pp
U4f U4f Scan_6 local true 2.657 server true 2.798 max Δcentre 28.8 meV, ΔFWHM 15.81 %, Δarea 8.88 %, Δfrac 0.77 pp | m held: server 2.634 Δcentre 3.7 meV, ΔFWHM 1.31 %, Δarea 1.36 %, Δfrac 0.07 pp
U4f U4f Scan_7 local true 1.764 server true 1.757 max Δcentre 2.6 meV, ΔFWHM 0.36 %, Δarea 0.49 %, Δfrac 0.04 pp | m held: server 1.752 Δcentre 3.0 meV, ΔFWHM 0.41 %, Δarea 0.40 %, Δfrac 0.03 pp
U4f U4f Scan_8 local true 4.656 server true 4.129 max Δcentre 5.7 meV, ΔFWHM 5.02 %, Δarea 8.31 %, Δfrac 0.32 pp | m held: server 4.118 Δcentre 6.3 meV, ΔFWHM 4.86 %, Δarea 8.07 %, Δfrac 0.33 pp
46:       "caM": 50
53:       "caM": 50
80:       "caM": 50
87:       "caM": 50
114:       "caM": 50
121:       "caM": 50
148:       "caM": 50
155:       "caM": 50
182:       "caM": 50
189:       "caM": 50
216:       "caM": 50
223:       "caM": 50
269:       "caM": 50
276:       "caM": 50
303:       "caM": 50
      "linked": false,
      "dCenter_meV": 2.4437213340888775,
      "dFwhm_pct": 0.09953132310007717,
      "dArea_pct": 0.1254847675247639,
      "dFrac_pp": 0.00956598314346968,
      "held_dCenter_meV": 2.4437213340888775,
      "held_dFwhm_pct": 0.09953132310007717,
      "held_dArea_pct": 0.1254847675247639,
      "held_dFrac_pp": 0.00956598314346968,
      "local": {
       "center": 287.45049411749454,
       "fwhm": 2.332377869622386,
       "amplitude": 1527.3418463299265,
       "area": 4201.183422647569
      },
      "server": {
       "center": 287.44805039616045,
       "fwhm": 2.330058731338076,
       "amplitude": 1526.9018538229732,
       "area": 4195.91818446826,
       "glMix": 30,
       "caM": 50
      },
      "server_held_m": {
       "center": 287.44805039616045,
       "fwhm": 2.330058731338076,
       "amplitude": 1526.9018538229732,
       "area": 4195.91818446826,
       "caM": 50
      }
     },

codex
The focused checks pass: 64 Python tests and 46 JS tests, with 7 documented TODOs. Refit-from-refit is a real second optimization, and the frozen fixture independently checks for numerical changes.

The saved-grid mismatch is measurable: for `UCl4_on_graphite / U4f Scan_1`, the harness records the first peak’s saved area as 60,320.08, while Results computes 61,067.04—a 1.22% difference. So the release-impact comparison still does not use the page’s saved numbers on both sides.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import json
a=json.load(open(\"docs/findings/a03/voigt_saved_vs_refit.json\"))
for r in a[\"targets\"][:20]: print(r[\"project\"],r[\"tab\"],r[\"max_dFrac_pp\"],r[\"max_voigt_dArea_pct\"])
g=json.load(open(\"docs/findings/a03/local_server_gap.json\"))
print([(r[\"target\"],r[\"comps\"][0][\"server_held_m\"][\"caM\"]) for r in g[\"regions\"][\"U4f\"]])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan 0.39349694352669023 5.126431961236233
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_0 0.3055324488266467 5.908429698508499
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_1 0.36706256117357977 2.81768871859176
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_2 0.1994222415056951 2.66399655352505
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_3 0.36395561525183817 4.476649957724921
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_4 0.6273039952880408 15.300258030724901
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_5 0.23558400151796333 3.153990844703858
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_6 0.2379568091072648 3.804518367711296
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_7 0.16168990854558557 3.399767774950113
1-GTA UCl4-graphite one set of U doublets.proj.zip U4f Scan_8 0.2667018883498705 5.012993460652703
4-GTA UCl4-BN.proj.zip U4f Scan 0.03892800792669737 0.5967888752685946
4-GTA UCl4-BN.proj.zip U4f Scan_0 0.19032218508965304 0
4-GTA UCl4-BN.proj.zip U4f Scan_1 0.17641729934928518 0
4-GTA UCl4-BN.proj.zip U4f Scan_2 0.498596109415983 4.697472062983287
4-GTA UCl4-BN.proj.zip U4f Scan_3 0.5909802038733369 5.955451068711803
4-GTA UCl4-BN.proj.zip U4f Scan_4 0.05842681743963851 0.6980120158225245
4-GTA UCl4-BN.proj.zip U4f Scan_5 0.49326606600346157 3.2773990083864613
4-GTA UCl4-BN.proj.zip U4f Scan_6 0.2495854384029217 2.3941498240584558
4-GTA UCl4-BN.proj.zip U4f Scan_7 0.3510427011305217 2.9254825513790994
4-GTA UCl4-BN.proj.zip U4f Scan_8 0.27712352381707994 2.514674346056356
[('U4f Scan_0', 8.19934520780095), ('U4f Scan_1', 8.19934520780095), ('U4f Scan_2', 8.19934520780095), ('U4f Scan_3', 8.19934520780095), ('U4f Scan_4', 8.19934520780095), ('U4f Scan_5', 8.19934520780095), ('U4f Scan_6', 8.19934520780095), ('U4f Scan_7', 8.19934520780095), ('U4f Scan_8', 8.19934520780095)]

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require(\"child_process\");const orig=cp.execFileSync;cp.execFileSync=(file,args,opts)=>{if(file.includes(\"python\")){if(args[0]===\"-c\"){args=[\"-c\",\"import tempfile; tempfile.tempdir='\\''/tmp'\\'';\\n\"+args[1],...args.slice(2)];}else{args=[\"-c\",\"import tempfile,sys,runpy; tempfile.tempdir='\\''/tmp'\\''; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='\\''__main__'\\'')\",...args];}}return orig(file,args,opts);};const fs=require(\"fs\"),Module=require(\"module\"),path=require(\"path\"); const f=path.resolve(\"scripts/local_server_gap.js\"); fs.writeFileSync=(dest,data)=>{const o=JSON.parse(data);console.log(JSON.stringify(o.regions.U4f.map(r=>({target:r.target,held_chi:r.server_held_m_chi2r,local_chi:r.local_chi2r,heldArea:r.held_max_dArea_pct,heldFrac:r.held_max_dFrac_pp,m:r.comps[0].server_held_m.caM})),null,2));}; let src=fs.readFileSync(f,\"utf8\").replace(\"p.shape === '\\''LACX'\\'' ? { ...p, fixCaM: true }\", \"p.shape === '\\''LACX'\\'' ? { ...p, caM: Math.round(p.caM), fixCaM: true }\").replace(\"[['\\''C1s'\\'', '\\''C1s Scan'\\''], ['\\''U4f'\\'', '\\''U4f Scan'\\'']]\",\"[['\\''U4f'\\'', '\\''U4f Scan'\\'']]\").replace(\"for (const name of names)\", \"for (const name of names.filter(n=>/_([4568])"'$/.test(n)))");const m=new Module(f,module);m.filename=f;m.paths=module.paths;m._compile(src,f);'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 16423ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
U4f U4f Scan_4 local true 1.970 server true 1.798 max Δcentre 26.6 meV, ΔFWHM 5.30 %, Δarea 8.32 %, Δfrac 0.33 pp | m held: server 1.870 Δcentre 13.4 meV, ΔFWHM 3.13 %, Δarea 5.27 %, Δfrac 0.19 pp
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
U4f U4f Scan_5 local true 2.393 server true 2.174 max Δcentre 4.7 meV, ΔFWHM 4.26 %, Δarea 6.65 %, Δfrac 0.35 pp | m held: server 2.182 Δcentre 6.3 meV, ΔFWHM 3.51 %, Δarea 5.49 %, Δfrac 0.25 pp
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
U4f U4f Scan_6 local true 2.657 server true 2.798 max Δcentre 28.8 meV, ΔFWHM 15.81 %, Δarea 8.88 %, Δfrac 0.77 pp | m held: server 2.629 Δcentre 3.6 meV, ΔFWHM 1.07 %, Δarea 1.59 %, Δfrac 0.07 pp
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/.matplotlib is not a writable directory
U4f U4f Scan_8 local true 4.656 server true 4.129 max Δcentre 5.7 meV, ΔFWHM 5.02 %, Δarea 8.31 %, Δfrac 0.32 pp | m held: server 4.117 Δcentre 5.8 meV, ΔFWHM 4.97 %, Δarea 8.24 %, Δfrac 0.32 pp
[
  {
    "target": "U4f Scan_4",
    "held_chi": 1.870376646451508,
    "local_chi": 1.9704477171249217,
    "heldArea": 5.267672920032595,
    "heldFrac": 0.18988172536209824,
    "m": 8
  },
  {
    "target": "U4f Scan_5",
    "held_chi": 2.1821605048185346,
    "local_chi": 2.3928635306048918,
    "heldArea": 5.490539532461236,
    "heldFrac": 0.2461513763683608,
    "m": 8
  },
  {
    "target": "U4f Scan_6",
    "held_chi": 2.6287976699999613,
    "local_chi": 2.657291813593791,
    "heldArea": 1.5887110733381782,
    "heldFrac": 0.06940184966579,
    "m": 8
  },
  {
    "target": "U4f Scan_8",
    "held_chi": 4.11711950166436,
    "local_chi": 4.655520835587359,
    "heldArea": 8.243232417685697,
    "heldFrac": 0.32493707104317215,
    "m": 8
  }
]

exec
/bin/zsh -lc "nl -ba scripts/local_server_gap.js | sed -n '68,82p'; nl -ba tests/js/local_lm_server_parity_backend.py | sed -n '17,28p'; nl -ba tests/js/lineshape_roundtrip.test.js | head -13; nl -ba templates/index.html | sed -n '8385,8406p'; nl -ba docs/findings/2026-09-fit-determinacy.md | sed -n '300,311p'; sed -n '1590,1625p' fitting.py; rg -n 'required|support' templates/index.html | head -20" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
    68	    const env = makeEnv(); const T = target(env, sourceName, name);
    69	    env.state.peaks = JSON.parse(JSON.stringify(T.start)); env.state.fitResult = null;
    70	    const loc = env.runFitLocal(T.be, T.bgSub, T.bg);
    71	    const localPeaks = JSON.parse(JSON.stringify(env.state.peaks));
    72	    const serverFit = startPeaks => {
    73	      const r = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/local_lm_server_parity_backend.py'), ROOT], { input: JSON.stringify({ be: T.be, inten: T.inten, peaks: startPeaks, ui: T.ui }), encoding: 'utf8', maxBuffer: 1 << 26 }));
    74	      const peaks = JSON.parse(JSON.stringify(startPeaks));
    75	      r.peaks.forEach((pp, i) => { const par = {}; for (const [k, v] of Object.entries(pp)) par[k] = { value: v }; env._applyBackendParams(peaks[i], par); });
    76	      return { r, peaks };
    77	    };
    78	    const { r: srv, peaks: serverPeaks } = serverFit(T.start);
    79	    const heldStart = T.start.map(p => p.shape === 'LACX' ? { ...p, fixCaM: true } : p);
    80	    const { r: srvHeld, peaks: serverHeldPeaks } = serverFit(heldStart);
    81	    // linked peaks: the local engine syncs them; the server returns resolved values for them too (applied above)
    82	    const aL = localPeaks.map(p => area(env, T.be, p)), aS = serverPeaks.map(p => area(env, T.be, p)), aH = serverHeldPeaks.map(p => area(env, T.be, p));
    17	y = np.asarray(d["inten"], float)
    18	ui = d["ui"]
    19	specs = [peak_to_backend_spec(p, d["peaks"]) for p in d["peaks"]]
    20	lo, hi = sorted([float(ui["bgStart"]), float(ui["bgEnd"])])
    21	idx = [i for i, b in enumerate(x) if lo <= b <= hi]
    22	res = fitting.run_fit(x, y, specs, background_method=ui["bgType"], bg_start_idx=idx[0], bg_end_idx=idx[-1] + 1,
    23	                      endpoint_avg=int(ui.get("endpointAvg") or 1), fit_kws={"method": "least_squares"},
    24	                      n_perturb=int(d.get("n_perturb") or 0))   # the page sends 3; the W1 test sends none
    25	print(json.dumps({"success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"],
    26	                  "peaks": [{k: v["value"] for k, v in ip["params"].items()} for ip in res["individual_peaks"]]}))
     1	// Page → server → page identity (A03, 2026-09-22).
     2	//
     3	// The parity harness (lineshape_parity.test.js) proves the two EVALUATORS
     4	// agree for the same parameters. It cannot see a request that asks the
     5	// server to fit a parameter the page never draws: until A03 a "Voigt" was
     6	// sent as pseudo_voigt_gl with gl_ratio FREE from 0.3 while evalPeak drew
     7	// η = 0.5, so every chart component, area, percentage and export for a
     8	// Voigt was the 0.5 curve under parameters fitted for another mix (on the
     9	// 90 committed Voigt targets: displayed areas 12 % off the fitted curve at
    10	// the median, 20 % at worst; 60 of 180 components had gone to pure
    11	// Gaussian, 16 to pure Lorentzian). This test closes that class: for every
    12	// shape, build the request with the PAGE's own peakToBackendSpec, fit it
    13	// on the server (fitting.run_fit, no background, Trust-Region), apply the
  8385	      <tbody>
  8386	  `;
  8387	
  8388	  // Fit grid for area integration. Current-format fits carry fitResult.be; older
  8389	  // saves omit it, and without a guard _peakArea(p, be) throws on be.length —
  8390	  // leaving the panel stale and aborting the tab switch. Fall back to the live ROI
  8391	  // grid, exactly as renderPeakList already does for its area/percentage column.
  8392	  let be = state.fitResult.be;
  8393	  if ((!be || !be.length) && typeof getROIData === 'function' && state.rawBE.length) {
  8394	    be = getROIData().be;
  8395	  }
  8396	  if (!be) be = [];
  8397	  const areas = state.peaks.map(p => _peakArea(p, be));
  8398	  // percentages are over the components the fit DID determine
  8399	  const totalArea = areas.reduce((s, v, i) => s + (_isUnsupported(state.peaks[i]) ? 0 : v), 0);
  8400	  const unsupportedPeaks = state.peaks.filter(p => _isUnsupported(p));
  8401	
  8402	  state.peaks.forEach((p, i) => {
  8403	    const pct = totalArea > 0 ? (areas[i] / totalArea * 100) : 0;
  8404	    const par = stderrMap[String(p.id)] || {};
  8405	    const centerSE = par.center ? par.center.stderr : null;
  8406	    const fwhmSE   = par.fwhm   ? par.fwhm.stderr   :
   300	7.9 while the local engine holds it; χ²ᵣ (local/server − 1) is +9.6, +10.1,
   301	−5.0 and +12.7 %, and the satellites, which share the region, differ by up
   302	to 8.9 % in area. A control arm (the server with every LA m HELD at its
   303	start) attributes it: on Scan_6 holding m closes the gap to 3.7 meV /
   304	1.3 % / 1.4 % / 0.07 pp — that one IS the `caM` clamp; on Scan_5 and Scan_8
   305	holding m changes nothing and the local engine's χ²ᵣ stays 10–13 % above
   306	the server's from the same start with the same free parameters — a WORSE
   307	MINIMUM (the mirror image of §2, where the local engine found the better
   308	one on C 1s Scan_4); Scan_4 is half each. The "starting point" label stays
   309	on both grounds; the `caM` clamp is the next unit, and the local engine's
   310	worse-minimum outcome on 3 of 9 U 4f targets is a finding for the
   311	local-engine work after it.
        if shape not in _SHAPE_FUNCS:
            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
        func = _SHAPE_FUNCS[shape]
        prefix = f"p{spec['id']}_"
        m = Model(func, prefix=prefix)
        p = _make_peak_params(m, spec, prefix, ordered)
        all_params.update(p)
        composite_model = m if composite_model is None else composite_model + m

    if composite_model is None:
        raise RuntimeError("No peaks were built")
    if require_component is not None:
        ids = [str(spec["id"]) for spec in peak_specs]
        if str(require_component) not in ids:
            raise ValueError(f"require_component '{require_component}' is not one of the peaks")
        if len(ids) < 2:
            raise ValueError("require_component needs at least two components")

    # Every random draw below (the perturbed restarts; the populations of the
    # two stochastic methods, which lmfit otherwise takes from numpy's GLOBAL
    # generator) comes from this one seed, so an identical request gives
    # identical DRAWS. (Not an identical Trust-Region result: see CLAUDE.md,
    # "Reproducibility".)
    if caller_seed is not None:
        random_seed = int(caller_seed)
    else:
        random_seed = _request_seed(
            x, y, bg, [spec.get("shape", "pseudo_voigt_gl") for spec in ordered],
            [f"p{spec['id']}_" for spec in ordered], all_params,
            fit_kws=fit_kws, n_perturb=n_perturb)
    # spawn(3) yields the same first two children as spawn(2): adding the
    # scattered-starts stream leaves every existing draw (and its pins) alone.
    perturb_rng, solver_rng, starts_rng = (np.random.default_rng(child)
                                           for child in np.random.SeedSequence(random_seed).spawn(3))
    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")
819:  .unsupported-badge {
3416:      // "not supported by the data" was about the data they were fitted to.
3417:      state.peaks = _normalizePeaksCRef((data.peaks || []).map(p => ({...p, support: null})));
5900:    for (const p of state.peaks) { const a = _peakArea(p, _roiBE); _peakAreas[p.id] = a; if (!_isUnsupported(p)) totalArea += a; }
5910:    const unsupported = _isUnsupported(p);
5911:    const areaPct = unsupported ? '\u2014' : (totalArea > 0 && pArea > 0 ? ((pArea / totalArea) * 100).toFixed(1) : '\u2014');
5917:        <span class="peak-name">${_escHtml(p.name)}${isLinked ? ' <span class="linked-badge">linked</span>' : ''}${p.isChargeReference ? ' <span class="chargeref-badge" title="Charge-correction reference (C 1s graphite 284.5 eV)">C-ref</span>' : ''}${unsupported ? ' ' + _unsupportedBadge(p.id) : ''}</span>
5918:        <span class="peak-info">${unsupported ? dash : p.center.toFixed(2) + ' eV'}</span>
5925:        <span class="peak-summary-val">${unsupported ? dash : p.center.toFixed(2)}</span>
5926:        <span class="peak-summary-val">${unsupported ? dash : p.fwhm.toFixed(2)}</span>
6888:// SCOPE: it answers "do the data support this component?", not "is it graphite?"
6889:// — a one-channel spike or a plateau under background None is supported.
6901://     unsupported-component unit gets the refit-without-the-component test.
6904:// ── "Not supported by the data" (unit step (b), 2026-09-22) ───────────────────
6912:// per component (`support: {f, delta_chi2, supported}`); the LOCAL engine
6916:// single-channel artefact can mark a real component unsupported; redundancy
6920:// other components as fitted: peaks carry it as `p.support` together with
6921:// `p.support.fitKey`, the key of the model and fit context at that time, and
6922:// every consumer reads it through _isUnsupported, which compares that key
6929:const _UNSUPPORTED_LABEL = 'not supported by the data';

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e 'const cp=require(\"child_process\");const orig=cp.execFileSync;cp.execFileSync=(file,args,opts)=>{if(file.includes(\"python\")){if(args[0]===\"-c\"){args=[\"-c\",\"import tempfile; tempfile.tempdir='\\''/tmp'\\'';\\n\"+args[1],...args.slice(2)];}else{args=[\"-c\",\"import tempfile,sys,runpy; tempfile.tempdir='\\''/tmp'\\''; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='\\''__main__'\\'')\",...args];}}return orig(file,args,opts);};const fs=require(\"fs\"),Module=require(\"module\"),path=require(\"path\"); const f=path.resolve(\"scripts/voigt_saved_vs_refit.js\");fs.writeFileSync=(dest,data)=>{const o=JSON.parse(data);console.log(JSON.stringify(o.targets.map(r=>({project:r.project,tab:r.tab,maxFrac:r.max_dFrac_pp,chi:r.chi2r})),null,2));};let src=fs.readFileSync(f,\"utf8\").replace(\"if ("'!t.fitResult ||", "if (zp!=='"'\\''4-GTA UCl4-BN.proj.zip'\\''||t.name"'!=='"'\\''U4f Scan_4'\\'') continue; if ("'!t.fitResult ||").replace("JSON.stringify({ be, inten, peaks: saved, ui, n_perturb: 3 })","JSON.stringify({ be: be.map(x=>+x.toFixed(4)), inten: inten.map(x=>+x.toFixed(2)), peaks: saved, ui, n_perturb: 3 })");const m=new Module(f,module);m.filename=f;m.paths=module.paths;m._compile(src,f);'"'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 5082ms:
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_4 server true max Δfrac 0.06 pp, max Voigt Δarea 0.7 %
{"n_tabs":1,"n_converged":1,"dFrac_pp":{"median":0.05838961357668149,"p90":0.05838961357668149,"max":0.05838961357668149},"gt_1pp":0,"voigt_dArea_pct":{"median":0.6970505470867194,"p90":0.6970505470867194,"max":0.6970505470867194}}
[
  {
    "project": "4-GTA UCl4-BN.proj.zip",
    "tab": "U4f Scan_4",
    "maxFrac": 0.05838961357668149,
    "chi": 18.23885213755572
  }
]

codex
The control’s `fixCaM` does reach the server as `fix_m`, but it holds 8.199345 while the local engine rounds that start to 8. I reran the four disputed targets with server m held at 8. The main conclusion survives: Scan_6’s gap largely closes; Scan_4/5/8 retain residuals.

Some claims still disagree with the artifacts: CLAUDE.md says all three remaining χ² gaps are 10–13%, but the committed held-m results give 4.91%, 9.44%, and 13.06%. The round-trip test header also still says 12% median area error instead of 13.89%.

exec
/bin/zsh -lc "sed -n '7780,7812p' templates/index.html; sed -n '6904,6968p' templates/index.html; sed -n '1,35p' docs/findings/a03/voigt_saved_vs_refit.log" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
  }

  renderPeakList();
  updatePlot();
  renderResults();
  _autoSnapshot();
}

// Label for the goodness-of-fit statistic a fit result carries. The server
// and (since unit W1, 2026-09-18) the local engine both minimise a
// counting-noise-weighted chi-square; local results saved by unit A0 were
// UNWEIGHTED and keep the label "Residual variance", never chi-square.
function _isUnweightedLocal(fr) { return !!(fr && fr.objective === 'unweighted_residual_variance'); }
function _fitStatLabel(fr) {
  return _isUnweightedLocal(fr) ? 'Residual variance' : 'χ²ᵣ';
}
// A LOCAL result is a STARTING POINT, not a reportable result. Measured in
// unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
// with Poisson weighting the local engine matches the server on GL-type
// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
// wherever the two engines reach the same minimum (5 of 9 committed U 4f
// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
// it still differs on the other 4 U 4f targets (satellite areas up to
// 8.9 %, 0.77 pp): on one because the LA m is held at its start locally
// (the gap closes when the server holds m too), on three because the local
// descent stops at a higher chi2r than the server from the same start
// (+5 to +13 %, with m held as well) - several minima - and it gives no
// uncertainties. Unweighted A0-era results differed by more than 100 %.
// Every site that shows, exports or saves a fit result carries the
// designation, keyed on persisted identity so reloaded results are labelled.
const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
const _LOCAL_FIT_CAVEAT_UNWEIGHTED = 'Local unweighted fit: a starting point, not a reportable result. Run Fit before reporting.';
// ── "Not supported by the data" (unit step (b), 2026-09-22) ───────────────────
// A component whose amplitude the fit drove to its floor, pinned on a bound, or
// fitted to numerical residue is an explicit OUTCOME: the fit did not determine
// it. Owner decision 2026-09-18: flag it, and do not report its centre, width
// or sigma as if they were determined. The statement that needs no intensity
// floor (six were tried and failed): with the OTHER components held at their
// fitted values, removing this one must make the fit significantly worse — the
// F statistic the Auto-Fit anchor check uses (F >= 10). The SERVER computes it
// per component (`support: {f, delta_chi2, supported}`); the LOCAL engine
// computes the same statistic from its own residuals (_componentSupportCore);
// the twin below recomputes it from any response carrying counts, fitted_y
// and the component's curve. Known limits are the anchor check's: a gross
// single-channel artefact can mark a real component unsupported; redundancy
// under overlap is not detected. A linked component follows its parent.
//
// The verdict is a property of THE FIT THAT PRODUCED IT, conditional on the
// other components as fitted: peaks carry it as `p.support` together with
// `p.support.fitKey`, the key of the model and fit context at that time, and
// every consumer reads it through _isUnsupported, which compares that key
// with the live one. After the student edits ANY peak, lock, link, the
// background, the ROI, anchors or the charge correction — or an undo brings
// back other values — the verdict no longer applies and nothing is suppressed
// or excluded; a new fit writes a new verdict. null = not established (no
// converged fit of this model yet, or a fit older than this unit).
const _SUPPORT_MIN_F = 10;
const _UNSUPPORTED_LABEL = 'not supported by the data';
const _UNSUPPORTED_TIP = 'With the other components held at their fitted values, removing this component does not make the fit to the data significantly worse (F < 10), so this fit did not determine it: its centre, width and uncertainties are not reported. This is an outcome of the fit, not a bug, and it is conditional on the other components. The data may still contain the species: try a different starting position or width, or lock the centre where chemistry says it belongs, and refit. Known limit: a gross single-channel artefact in the region can produce this verdict for a real component.';
// The statistic, from residuals of the fit (counts − fitted) and the component's curve.
function _componentSupportCore(counts, fitted, comp, weights, nFreeComp, nFreeTotal) {
  let withC = 0, withoutC = 0, used = 0;
  for (let i = 0; i < counts.length; i++) {
    if (!Number.isFinite(counts[i]) || !Number.isFinite(fitted[i]) || !Number.isFinite(comp[i])) continue;
    const w2 = weights[i] * weights[i], r = counts[i] - fitted[i];
    withC += w2 * r * r; withoutC += w2 * (r + comp[i]) * (r + comp[i]); used++;
  }
  const delta = withoutC - withC, p = Math.max(1, nFreeComp), dof = Math.max(1, used - nFreeTotal);
  const f = delta <= 0 ? 0 : (withC === 0 ? Infinity : (delta / p) / (withC / dof));
  return { f: Number.isFinite(f) ? f : null, delta_chi2: delta, supported: delta > 0 && (withC === 0 || f >= _SUPPORT_MIN_F) };
}
function _componentSupportFromResponse(json, peakId) {
  const counts = (json && json.counts) || [], fit = (json && json.fitted_y) || [];
  const ip = ((json && json.individual_peaks) || []).find(q => String(q.id) === String(peakId));
  if (ip && ip.support && typeof ip.support.supported === 'boolean') return ip.support;
  const comp = (ip && ip.y) || [], n = counts.length;
  if (!n || fit.length !== n || comp.length !== n) return null;
  let p = 0;
  for (const k in ((ip && ip.params) || {})) { const q = ip.params[k]; if (q && q.vary === true && (q.expr == null || q.expr === '')) p++; }
  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
  return _componentSupportCore(counts, fit, comp, counts.map(c => 1 / Math.sqrt(Math.max(c, 1))), p, nFree);
}
// Resolve links by ANCESTRY (a grandchild follows the root), independent of order.
function _supportRootOf(peaks, p, seen = new Set()) {
  if (!p.linked || seen.has(p.id)) return p;
  seen.add(p.id);
  const par = peaks.find(q => String(q.id) === String(p.linked));
  return par ? _supportRootOf(peaks, par, seen) : p;
}
// Write p.support for every peak from per-peak verdicts {id -> verdict|null}, stamped with the fit key.
function _applySupportVerdicts(peaks, verdictOf, fitKey) {
  for (const p of peaks) {
    const root = _supportRootOf(peaks, p);
    const v = verdictOf(root.id);
    p.support = v ? { f: v.f ?? null, delta_chi2: v.delta_chi2 ?? null, supported: !!v.supported, fitKey,
                      ...(root !== p ? { follows: root.id } : {}) } : null;
  }
1-GTA UCl4-graphite one set  U4f Scan server true max Δfrac 0.39 pp, max Voigt Δarea 5.1 %
1-GTA UCl4-graphite one set  U4f Scan_0 server true max Δfrac 0.31 pp, max Voigt Δarea 5.9 %
1-GTA UCl4-graphite one set  U4f Scan_1 server true max Δfrac 0.37 pp, max Voigt Δarea 2.8 %
1-GTA UCl4-graphite one set  U4f Scan_2 server true max Δfrac 0.20 pp, max Voigt Δarea 2.7 %
1-GTA UCl4-graphite one set  U4f Scan_3 server true max Δfrac 0.36 pp, max Voigt Δarea 4.5 %
1-GTA UCl4-graphite one set  U4f Scan_4 server true max Δfrac 0.63 pp, max Voigt Δarea 15.3 %
1-GTA UCl4-graphite one set  U4f Scan_5 server true max Δfrac 0.24 pp, max Voigt Δarea 3.2 %
1-GTA UCl4-graphite one set  U4f Scan_6 server true max Δfrac 0.24 pp, max Voigt Δarea 3.8 %
1-GTA UCl4-graphite one set  U4f Scan_7 server true max Δfrac 0.16 pp, max Voigt Δarea 3.4 %
1-GTA UCl4-graphite one set  U4f Scan_8 server true max Δfrac 0.27 pp, max Voigt Δarea 5.0 %
4-GTA UCl4-BN.proj.zip U4f Scan server true max Δfrac 0.04 pp, max Voigt Δarea 0.6 %
4-GTA UCl4-BN.proj.zip U4f Scan_0 server true max Δfrac 0.19 pp, max Voigt Δarea 0.0 %
4-GTA UCl4-BN.proj.zip U4f Scan_1 server true max Δfrac 0.18 pp, max Voigt Δarea 0.0 %
4-GTA UCl4-BN.proj.zip U4f Scan_2 server true max Δfrac 0.50 pp, max Voigt Δarea 4.7 %
4-GTA UCl4-BN.proj.zip U4f Scan_3 server true max Δfrac 0.59 pp, max Voigt Δarea 6.0 %
4-GTA UCl4-BN.proj.zip U4f Scan_4 server true max Δfrac 0.06 pp, max Voigt Δarea 0.7 %
4-GTA UCl4-BN.proj.zip U4f Scan_5 server true max Δfrac 0.49 pp, max Voigt Δarea 3.3 %
4-GTA UCl4-BN.proj.zip U4f Scan_6 server true max Δfrac 0.25 pp, max Voigt Δarea 2.4 %
4-GTA UCl4-BN.proj.zip U4f Scan_7 server true max Δfrac 0.35 pp, max Voigt Δarea 2.9 %
4-GTA UCl4-BN.proj.zip U4f Scan_8 server true max Δfrac 0.28 pp, max Voigt Δarea 2.5 %
B4C-UCl4.proj.zip U4f Scan server true max Δfrac 0.40 pp, max Voigt Δarea 4.7 %
B4C-UCl4.proj.zip U4f Scan_0 server true max Δfrac 0.53 pp, max Voigt Δarea 4.5 %
B4C-UCl4.proj.zip U4f Scan_1 server true max Δfrac 0.43 pp, max Voigt Δarea 4.5 %
B4C-UCl4.proj.zip U4f Scan_2 server true max Δfrac 0.69 pp, max Voigt Δarea 8.5 %
B4C-UCl4.proj.zip U4f Scan_3 server true max Δfrac 0.40 pp, max Voigt Δarea 4.8 %
B4C-UCl4.proj.zip U4f Scan_4 server true max Δfrac 0.51 pp, max Voigt Δarea 5.0 %
B4C-UCl4.proj.zip U4f Scan_5 server true max Δfrac 0.37 pp, max Voigt Δarea 4.4 %
B4C-UCl4.proj.zip U4f Scan_6 server true max Δfrac 0.48 pp, max Voigt Δarea 4.6 %
B4C-UCl4.proj.zip U4f Scan_7 server true max Δfrac 0.25 pp, max Voigt Δarea 3.2 %
B4C-UCl4.proj.zip U4f Scan_8 server true max Δfrac 0.33 pp, max Voigt Δarea 5.0 %
Cl2p_projfit_test.proj.zip U4f Scan server true max Δfrac 0.45 pp, max Voigt Δarea 7.9 %
Cl2p_projfit_test.proj.zip U4f Scan_0 server true max Δfrac 0.41 pp, max Voigt Δarea 5.5 %
Cl2p_projfit_test.proj.zip U4f Scan_1 server true max Δfrac 0.26 pp, max Voigt Δarea 3.5 %
Cl2p_projfit_test.proj.zip U4f Scan_2 server true max Δfrac 0.33 pp, max Voigt Δarea 5.0 %
Cl2p_projfit_test.proj.zip U4f Scan_3 server true max Δfrac 0.41 pp, max Voigt Δarea 7.5 %

exec
/bin/zsh -lc "rg -n '"'^function _isLocalFit|''^function _isLocalProvenance'"' templates/index.html; nl -ba docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md | sed -n '200,212p'; nl -ba scripts/voigt_eta_measure.py | sed -n '64,79p'; nl -ba autofit/reference.py | sed -n '137,146p'; git diff --numstat main..HEAD -- tests/autofit/fixtures/u4f_battery_expected.json" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
7813:function _isLocalProvenance(p) {
7816:function _isLocalFit(fr) { return _isLocalProvenance(fr); }
   200	   locked, the server held the substitute and the drawn curve differed from
   201	   the fitted one by 6.9 % / 8.8 % of amplitude. Fixed in both builders
   202	   (only a non-number falls back); the round-trip test now locks every shape
   203	   parameter at its bounds; the sweep's backend parameters now come THROUGH
   204	   `peakToBackendSpec` rather than a mapping of the harness's own.
   205	4. MINOR — the uncertainty panel told a Voigt's user to "unlock the padlock"
   206	   for a mix that has none: it now says the shape fixes the mix and points
   207	   to GL.
   208	5. MINOR — "χ²ᵣ differs by 8–20 %" was wrong (the four are +9.6, +10.1,
   209	   −5.0, +12.7 %), the comment's "24 %" was 20 %, row A's 1.60 was 1.61 (now
   210	   1.55 with the explicit arms); and attributing the whole residual to the
   211	   `caM` clamp was an inference — the control arm (§6) shows it is one
   212	   target of four.
    64	            kw = dict(background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
    65	                      endpoint_avg=b["endpoint_avg"], n_perturb=3, fit_kws={"method": "least_squares"})
    66	            x = np.asarray(t["be"], float)
    67	            y = np.round(np.asarray(t["inten"], float), 2)   # the upload rounds to 2 dp
    68	            free = copy.deepcopy(t["specs"])
    69	            fixed = copy.deepcopy(t["specs"])
    70	            for i in vidx:
    71	                free[i]["gl_ratio"] = 0.3                     # the request before A03: eta free from 0.3
    72	                free[i]["fix_gl_ratio"] = False
    73	                fixed[i]["gl_ratio"] = 0.5                    # the request since A03: eta held at 0.5
    74	                fixed[i]["fix_gl_ratio"] = True
    75	            rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"],
    76	                   "voigt_ids": [str(t["specs"][i]["id"]) for i in vidx]}
    77	            for lab, specs in (("free", free), ("fixed", fixed)):
    78	                try:
    79	                    rec[lab] = _pack(fitting.run_fit(x, y, specs, **kw))
   137	        spec["alpha"] = p["caAlpha"] if _finite(p.get("caAlpha")) else 1.0
   138	        spec["beta"] = p["caBeta"] if _finite(p.get("caBeta")) else 1.0
   139	        spec["m"] = p["caM"] if _finite(p.get("caM")) else 50.0
   140	        spec["fix_alpha"] = bool(p.get("fixCaAlpha"))
   141	        spec["fix_beta"] = bool(p.get("fixCaBeta"))
   142	        spec["fix_m"] = bool(p.get("fixCaM"))
   143	    else:
   144	        spec["shape"] = "gaussian"
   145	
   146	    if p.get("linked"):
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VVLPr312' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cBPPpjzp' (errno=Operation not permitted)
532	532	tests/autofit/fixtures/u4f_battery_expected.json

 succeeded in 299427ms:
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan server true max Δfrac 0.39 pp, max Voigt Δarea 5.1 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_0 server true max Δfrac 0.31 pp, max Voigt Δarea 5.9 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_1 server true max Δfrac 0.37 pp, max Voigt Δarea 2.8 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_2 server true max Δfrac 0.20 pp, max Voigt Δarea 2.7 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_3 server true max Δfrac 0.36 pp, max Voigt Δarea 4.5 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_4 server true max Δfrac 0.63 pp, max Voigt Δarea 15.3 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_5 server true max Δfrac 0.24 pp, max Voigt Δarea 3.2 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_6 server true max Δfrac 0.24 pp, max Voigt Δarea 3.8 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_7 server true max Δfrac 0.16 pp, max Voigt Δarea 3.4 %
/Users/skyefortier/.matplotlib is not a writable directory
1-GTA UCl4-graphite one set  U4f Scan_8 server true max Δfrac 0.27 pp, max Voigt Δarea 5.0 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan server true max Δfrac 0.04 pp, max Voigt Δarea 0.6 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_0 server true max Δfrac 0.19 pp, max Voigt Δarea 0.0 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_1 server true max Δfrac 0.18 pp, max Voigt Δarea 0.0 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_2 server true max Δfrac 0.50 pp, max Voigt Δarea 4.7 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_3 server true max Δfrac 0.59 pp, max Voigt Δarea 6.0 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_4 server true max Δfrac 0.02 pp, max Voigt Δarea 0.7 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_5 server true max Δfrac 0.49 pp, max Voigt Δarea 3.3 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_6 server true max Δfrac 0.25 pp, max Voigt Δarea 2.4 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_7 server true max Δfrac 0.35 pp, max Voigt Δarea 2.9 %
/Users/skyefortier/.matplotlib is not a writable directory
4-GTA UCl4-BN.proj.zip U4f Scan_8 server true max Δfrac 0.27 pp, max Voigt Δarea 2.5 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan server true max Δfrac 0.40 pp, max Voigt Δarea 4.7 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_0 server true max Δfrac 0.53 pp, max Voigt Δarea 4.5 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_1 server true max Δfrac 0.43 pp, max Voigt Δarea 4.5 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_2 server true max Δfrac 0.69 pp, max Voigt Δarea 8.5 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_3 server true max Δfrac 0.40 pp, max Voigt Δarea 4.8 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_4 server true max Δfrac 0.51 pp, max Voigt Δarea 5.0 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_5 server true max Δfrac 0.37 pp, max Voigt Δarea 4.4 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_6 server true max Δfrac 0.48 pp, max Voigt Δarea 4.6 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_7 server true max Δfrac 0.25 pp, max Voigt Δarea 3.2 %
/Users/skyefortier/.matplotlib is not a writable directory
B4C-UCl4.proj.zip U4f Scan_8 server true max Δfrac 0.33 pp, max Voigt Δarea 5.0 %
/Users/skyefortier/.matplotlib is not a writable directory
Cl2p_projfit_test.proj.zip U4f Scan server true max Δfrac 0.45 pp, max Voigt Δarea 7.9 %
/Users/skyefortier/.matplotlib is not a writable directory
Cl2p_projfit_test.proj.zip U4f Scan_0 server true max Δfrac 0.41 pp, max Voigt Δarea 5.5 %
/Users/skyefortier/.matplotlib is not a writable directory
Cl2p_projfit_test.proj.zip U4f Scan_1 server true max Δfrac 0.26 pp, max Voigt Δarea 3.5 %
/Users/skyefortier/.matplotlib is not a writable directory
Cl2p_projfit_test.proj.zip U4f Scan_2 server true max Δfrac 0.33 pp, max Voigt Δarea 5.0 %
/Users/skyefortier/.matplotlib is not a writable directory
Cl2p_projfit_test.proj.zip U4f Scan_3 server true max Δfrac 0.41 pp, max Voigt Δarea 7.5 %
/Users/skyefortier/.matplotlib is not a writable directory
Cl2p_projfit_test.proj.zip U4f Scan_4 server true max Δfrac 0.27 pp, max Voigt Δarea 4.1 %
/Users/skyefortier/.matplotlib is not a writable directory
Cl2p_projfit_test.proj.zip U4f Scan_5 server true max Δfrac 0.39 pp, max Voigt Δarea 6.0 %
/Users/skyefortier/.matplotlib is not a writable directory
Cl2p_projfit_test.proj.zip Cl2p Scan_1 server true max Δfrac 0.00 pp, max Voigt Δarea 7.6 %
/Users/skyefortier/.matplotlib is not a writable directory
Project9_CasaXPS_newfit.proj U4f Scan server true max Δfrac 0.45 pp, max Voigt Δarea 7.9 %
/Users/skyefortier/.matplotlib is not a writable directory
Project9_CasaXPS_newfit.proj U4f Scan_0 server true max Δfrac 0.41 pp, max Voigt Δarea 5.5 %
/Users/skyefortier/.matplotlib is not a writable directory
Project9_CasaXPS_newfit.proj U4f Scan_1 server true max Δfrac 0.26 pp, max Voigt Δarea 3.5 %
/Users/skyefortier/.matplotlib is not a writable directory
Project9_CasaXPS_newfit.proj U4f Scan_2 server true max Δfrac 0.33 pp, max Voigt Δarea 5.0 %
/Users/skyefortier/.matplotlib is not a writable directory
Project9_CasaXPS_newfit.proj U4f Scan_3 server true max Δfrac 0.41 pp, max Voigt Δarea 7.5 %
/Users/skyefortier/.matplotlib is not a writable directory
Project9_CasaXPS_newfit.proj U4f Scan_4 server true max Δfrac 0.27 pp, max Voigt Δarea 4.1 %
/Users/skyefortier/.matplotlib is not a writable directory
Project9_CasaXPS_newfit.proj U4f Scan_5 server true max Δfrac 0.39 pp, max Voigt Δarea 6.0 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan server true max Δfrac 0.44 pp, max Voigt Δarea 5.1 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_0 server true max Δfrac 0.31 pp, max Voigt Δarea 5.9 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_1 server true max Δfrac 0.39 pp, max Voigt Δarea 3.0 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_2 server true max Δfrac 0.56 pp, max Voigt Δarea 8.4 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_3 server true max Δfrac 0.36 pp, max Voigt Δarea 4.5 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_4 server true max Δfrac 0.59 pp, max Voigt Δarea 15.1 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_5 server true max Δfrac 0.24 pp, max Voigt Δarea 3.2 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_6 server true max Δfrac 0.24 pp, max Voigt Δarea 3.7 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_7 server true max Δfrac 0.13 pp, max Voigt Δarea 2.5 %
/Users/skyefortier/.matplotlib is not a writable directory
UCl4_on_graphite.proj.zip U4f Scan_8 server true max Δfrac 0.27 pp, max Voigt Δarea 5.0 %
{"n_tabs":55,"n_converged":55,"dFrac_pp":{"median":0.36399202538341113,"p90":0.5078511773600608,"max":0.6882978878015908},"gt_1pp":0,"voigt_dArea_pct":{"median":4.576983178447858,"p90":7.556793905528403,"max":15.300728079594128}}
{
  "summary": {
    "n_tabs": 55,
    "n_converged": 55,
    "dFrac_pp": {
      "median": 0.36399202538341113,
      "p90": 0.5078511773600608,
      "max": 0.6882978878015908
    },
    "gt_1pp": 0,
    "voigt_dArea_pct": {
      "median": 4.576983178447858,
      "p90": 7.556793905528403,
      "max": 15.300728079594128
    }
  },
  "changes": [
    {
      "project": "4-GTA UCl4-BN.proj.zip",
      "tab": "U4f Scan_4",
      "old": 0.05842681743963851,
      "new": 0.023915208400031307,
      "oldArea": 0.6980120158225245,
      "newArea": 0.6978320788381009
    },
    {
      "project": "UCl4_on_graphite.proj.zip",
      "tab": "U4f Scan",
      "old": 0.3934656169408135,
      "new": 0.44290653413827236,
      "oldArea": 5.125558770156213,
      "newArea": 5.126313587458919
    },
    {
      "project": "UCl4_on_graphite.proj.zip",
      "tab": "U4f Scan_1",
      "old": 0.3105736862876865,
      "new": 0.38659176117065847,
      "oldArea": 3.0305918846483815,
      "newArea": 3.008423877759192
    },
    {
      "project": "UCl4_on_graphite.proj.zip",
      "tab": "U4f Scan_2",
      "old": 0.5401828553316126,
      "new": 0.5592829242583433,
      "oldArea": 8.402943534512586,
      "newArea": 8.412187193440923
    },
    {
      "project": "UCl4_on_graphite.proj.zip",
      "tab": "U4f Scan_4",
      "old": 0.6070880313317768,
      "new": 0.5897583699314736,
      "oldArea": 15.08219531597711,
      "newArea": 15.07231573456873
    }
  ]
}

exec
/bin/zsh -lc "git status --short; nl -ba templates/index.html | sed -n '6186,6193p'; nl -ba docs/findings/a03/voigt_eta_summary.txt" in /Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8uZfgKAb' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qZnggB3X' (errno=Operation not permitted)
?? docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md
?? docs/autofit/codex/a03_voigt_eta_r2_verdict_runB.md
?? docs/autofit/codex/a03_voigt_eta_recheck_prompt.txt
  6186	async function uploadToBackend(be, inten) {
  6187	  const csv = be.map((e, i) => e.toFixed(4) + ',' + inten[i].toFixed(2)).join('\n');
  6188	  const form = new FormData();
  6189	  form.append('file', new Blob([csv], { type: 'text/plain' }), 'spectrum.csv');
  6190	  const resp = await fetch('/api/upload', { method: 'POST', body: form });
  6191	  // A server-side failure (HTTP error, error body, or no session id) is not a
  6192	  // transport failure: runFit must report it, never switch engines (unit A0).
  6193	  const serverError = (msg) => { const err = new Error(msg); err.serverError = true; return err; };
     1	targets 90, both fits converged 90
     2	free eta of 180 Voigt components: 60 at 0 (pure Gaussian), 16 at 1 (pure Lorentzian), 24 within 0.4–0.6
     3	per-Voigt-component DISPLAYED area vs the fitted curve (%): median 13.89, p90 19.18, max 20.11; > 10 % on 116 of 180; displayed high (eta < 0.5) 110, low 70
     4	A. displayed vs free-fit fractions, max |delta| pp per target: median 0.96, p90 1.48, max 1.55; > 1 pp on 35 targets
     5	B. fixed refit vs the 0.5 curve of the free fit, max |delta| pp: median 0.34, p90 0.54, max 1.02; > 1 pp on 1 targets
     6	C. fixed refit vs free fit, max |delta| pp: median 0.93, p90 1.31, max 2.04; > 1 pp on 33 targets
     7	chi2r fixed/free: median 1.09, p90 1.19, max 5.39; fixed lower on 10 targets (the free fit in a worse minimum)

codex
No BLOCKER found. One MAJOR measurement defect remains.

1. **MAJOR — The saved baseline still differs from Results.** [scripts/voigt_saved_vs_refit.js:46](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:46) integrates saved peaks on the current ROI grid. Results instead uses `fitResult.be`, falling back to the ROI only when absent.

   Concrete failure: `UCl4_on_graphite.proj.zip / U4f Scan_1` has a shifted saved grid. The harness reports the first saved peak’s area as **60,320.08**; Results computes **61,067.04**—a **1.22%** discrepancy. Saved fractions differ by up to **0.0928 pp** before any refitting.

   Correcting saved-grid selection and upload rounding in memory, then rerunning all 55 tabs, produced **median 0.3640 pp**, versus committed **0.3510 pp**. The maximum remains approximately **0.69 pp**, with none above 1 pp. Round-1 item 2 is therefore **not closed**; regenerate the artifact and release-note median.

2. **MINOR — The refit request bypasses page upload rounding.** [scripts/voigt_saved_vs_refit.js:42](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:42) sends full-precision energies and intensities. [uploadToBackend:6187](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:6187) sends four and two decimal places respectively. All 55 targets contain intensities affected by rounding. Because the seed hashes these arrays, the harness requests different restart draws from Run Fit. Preserve the page’s pre-upload background indices while reproducing its transport values.

3. **MINOR — The held-m control does not hold the local engine’s effective value.** [scripts/local_server_gap.js:79](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/local_server_gap.js:79) holds the stored **8.1993452078**; the local engine rounds it to **8**. `fixCaM → fix_m` works, so this does isolate server m movement, but it is not an exact same-m comparison.

   Rerunning Scan_4/5/6/8 with server m held at 8 preserves the qualitative conclusion. For Scan_6, however, the held-arm area gap becomes **1.59%**, versus committed **1.36%**. Distinguish stored-start and effective-local controls in the documentation.

4. **MINOR — Numerical and coverage claims remain inconsistent.**
   
   - [CLAUDE.md:491](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/CLAUDE.md:491) says three held-m χ² gaps are **10–13%**. The artifact gives **4.91%, 9.44%, 13.06%** for Scan_4/5/8.
   - [lineshape_roundtrip.test.js:9](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:9) still quotes **12%** median area error; the summary says **13.89%**.
   - [lineshape_roundtrip.test.js:165](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:165) claims every shape parameter is locked at its bounds. The seven cases omit, among others, asymmetry 1, DS gamma 5, and all LA/DS+G bound locks. The evaluator sweep does not exercise server locking.
   - Plan verification counts are stale: the round-trip file now has **18 passes, 2 TODOs**, and the Python contract has **5 tests**.
   - Commit `712e136` retains superseded numbers and attribution. Use corrected figures in the final merge message.

The other round-1 closures hold: both measurement arms explicitly restore their intended contracts; both builders preserve legitimate zeros, with no remaining equivalent `||` defaults; the endpoint cases actually assert `vary: false` and compare drawn versus fitted curves; sweep D uses the builder; and Voigt uncertainty guidance correctly points to GL.

The **55-tab, six-project roster is correct**. Tabs without `fitResult` are excluded; prospective Batch Fit starts do not belong in this saved-results comparison. The bridge receives `n_perturb: 3`.

Zero-valued asym-GL mix and DS alpha now also change request-derived seeds. That is expected from correcting the effective inputs; mention the reproducibility consequence in release notes. Refit-from-refit remains a meaningful stationarity test, with the frozen fixture providing an independent regression check.

Validation: **64 Python tests passed; 46 JS tests passed, 7 documented TODOs**. All 55 corrected measurement refits converged. No files changed.

**VERDICT: NO-GO**
tokens used
160,020
No BLOCKER found. One MAJOR measurement defect remains.

1. **MAJOR — The saved baseline still differs from Results.** [scripts/voigt_saved_vs_refit.js:46](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:46) integrates saved peaks on the current ROI grid. Results instead uses `fitResult.be`, falling back to the ROI only when absent.

   Concrete failure: `UCl4_on_graphite.proj.zip / U4f Scan_1` has a shifted saved grid. The harness reports the first saved peak’s area as **60,320.08**; Results computes **61,067.04**—a **1.22%** discrepancy. Saved fractions differ by up to **0.0928 pp** before any refitting.

   Correcting saved-grid selection and upload rounding in memory, then rerunning all 55 tabs, produced **median 0.3640 pp**, versus committed **0.3510 pp**. The maximum remains approximately **0.69 pp**, with none above 1 pp. Round-1 item 2 is therefore **not closed**; regenerate the artifact and release-note median.

2. **MINOR — The refit request bypasses page upload rounding.** [scripts/voigt_saved_vs_refit.js:42](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/voigt_saved_vs_refit.js:42) sends full-precision energies and intensities. [uploadToBackend:6187](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/templates/index.html:6187) sends four and two decimal places respectively. All 55 targets contain intensities affected by rounding. Because the seed hashes these arrays, the harness requests different restart draws from Run Fit. Preserve the page’s pre-upload background indices while reproducing its transport values.

3. **MINOR — The held-m control does not hold the local engine’s effective value.** [scripts/local_server_gap.js:79](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/scripts/local_server_gap.js:79) holds the stored **8.1993452078**; the local engine rounds it to **8**. `fixCaM → fix_m` works, so this does isolate server m movement, but it is not an exact same-m comparison.

   Rerunning Scan_4/5/6/8 with server m held at 8 preserves the qualitative conclusion. For Scan_6, however, the held-arm area gap becomes **1.59%**, versus committed **1.36%**. Distinguish stored-start and effective-local controls in the documentation.

4. **MINOR — Numerical and coverage claims remain inconsistent.**
   
   - [CLAUDE.md:491](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/CLAUDE.md:491) says three held-m χ² gaps are **10–13%**. The artifact gives **4.91%, 9.44%, 13.06%** for Scan_4/5/8.
   - [lineshape_roundtrip.test.js:9](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:9) still quotes **12%** median area error; the summary says **13.89%**.
   - [lineshape_roundtrip.test.js:165](/Users/skyefortier/xps-app/.claude/worktrees/fix-voigt-eta-identity/tests/js/lineshape_roundtrip.test.js:165) claims every shape parameter is locked at its bounds. The seven cases omit, among others, asymmetry 1, DS gamma 5, and all LA/DS+G bound locks. The evaluator sweep does not exercise server locking.
   - Plan verification counts are stale: the round-trip file now has **18 passes, 2 TODOs**, and the Python contract has **5 tests**.
   - Commit `712e136` retains superseded numbers and attribution. Use corrected figures in the final merge message.

The other round-1 closures hold: both measurement arms explicitly restore their intended contracts; both builders preserve legitimate zeros, with no remaining equivalent `||` defaults; the endpoint cases actually assert `vary: false` and compare drawn versus fitted curves; sweep D uses the builder; and Voigt uncertainty guidance correctly points to GL.

The **55-tab, six-project roster is correct**. Tabs without `fitResult` are excluded; prospective Batch Fit starts do not belong in this saved-results comparison. The bridge receives `n_perturb: 3`.

Zero-valued asym-GL mix and DS alpha now also change request-derived seeds. That is expected from correcting the effective inputs; mention the reproducibility consequence in release notes. Refit-from-refit remains a meaningful stationarity test, with the frozen fixture providing an independent regression check.

Validation: **64 Python tests passed; 46 JS tests passed, 7 documented TODOs**. All 55 corrected measurement refits converged. No files changed.

**VERDICT: NO-GO**
