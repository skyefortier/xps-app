"""Find Peaks x1 vs x0.1 toggle probe (2026-09-28; docs/findings/find-peaks-scale/README.md).
Usage (from a worktree root): python scripts/findpeaks_scale_toggles.py OUT.jsonl BUDGET_OFF(0|1) PRESEED_OFF(0|1) [BG_SCALED(0|1)]
"""
import sys, os, json, time, logging
sys.path.insert(0, '.')
OUT, BUDGET_OFF, PRESEED_OFF = sys.argv[1], sys.argv[2] == '1', sys.argv[3] == '1'
import autofit.engine as eng
if BUDGET_OFF:
    # TOTAL - CANDIDATE is the sweep's stop test: keep it huge and positive
    eng.CANDIDATE_TIMEOUT_SEC = 1e7; eng.TOTAL_ANALYSIS_TIMEOUT_SEC = 1e9
    eng.PROPOSAL_STABILITY_TIMEOUT_SEC = 1e7; eng.PROPOSAL_CANDIDATE_TIMEOUT_SEC = 1e7
BG_SCALED = len(sys.argv) > 4 and sys.argv[4] == '1'
CUR = {'c': 1.0}
if BG_SCALED:   # toggle: the background at scale c is EXACTLY c x the x1 background
    _orig_bg = eng._compute_background
    eng._compute_background = lambda x, y, bg, endpoint_avg=1: CUR['c'] * _orig_bg(x, y / CUR['c'], bg, endpoint_avg=endpoint_avg)
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.reference import load_reference_fits
cut = []
class H(logging.Handler):
    def emit(self, r):
        m = r.getMessage()
        if "budget" in m: cut.append(m[:120])
logging.getLogger("autofit.engine").addHandler(H())
g = resolve([Phase(id="graphite", material_class=MaterialClass.CONDUCTOR, regions=("C 1s",), material="graphite")], "C 1s")
CANDS = ["MG2_graphAsymGL_aliph_sat_CO_C=O", "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "AG2_linked", "A2_linked"]
picks = [("UCl4_on_graphite.proj.zip", "C1s Scan_8"), ("8-JT Graphite.proj.zip", "C1s Scan_2"), ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
         ("8-JT Graphite.proj.zip", "C1s Scan_5"), ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_2"), ("UCl4_on_graphite.proj.zip", "C1s Scan_3"),
         ("8-JT Graphite.proj.zip", "C1s Scan_7"), ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan")]
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(tuple(json.loads(l)['key']))
for proj, name in picks:
    if (proj, name) in done: continue
    rf = next(r for r in load_reference_fits(os.path.join('docs/autofit/test_data', proj)) if r.name == name)
    rows = []
    for scale in (1.0, 0.1):
        CUR['c'] = scale
        cut.clear(); t0 = time.time()
        opts = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0, "candidate_filter": CANDS, "enable_proposal_pass": False}
        if PRESEED_OFF: opts["enable_preseed"] = False
        res = get_method("ic_model_comparison").run(rf.roi_be, rf.roi_intensity * scale, grammar=g, options=opts)
        d = res.diagnostics
        w = next((c for c in res.analysis["candidates"] if c["name"] == d.get("winner")), None)
        rows.append({"scale": scale, "winner": d.get("winner"), "conditional": d.get("conditional"), "reason": d.get("conditional_reason"),
                     "chi2r": w and w["reduced_chi_sq"], "budget_cuts": len(cut), "sec": round(time.time() - t0),
                     "preseeded": len(res.analysis.get("preseeded_features") or []),
                     "cands": {c["name"]: [round(c["min_active_persistence"], 2), c["survived"], str(c["filter_reason"])[:60]] for c in res.analysis["candidates"]}})
    with open(OUT, 'a') as f: f.write(json.dumps({"key": [proj, name], "rows": rows}) + "\n")
