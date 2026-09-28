"""Refit-level record of one Find Peaks run on 1-GTA C1s Scan_6 (2026-09-28): per stability refit its time, nfev, convergence and
every slot support F. Usage: python scripts/findpeaks_scan6_refits.py BUDGET_OFF(0|1) OUT.json
"""
import sys, os, json, time
sys.path.insert(0, '.')
BUDGET_OFF = sys.argv[1] == '1'
import autofit.engine as eng
if BUDGET_OFF:
    eng.CANDIDATE_TIMEOUT_SEC = 1e7; eng.TOTAL_ANALYSIS_TIMEOUT_SEC = 1e9
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.reference import load_reference_fits
g = resolve([Phase(id="graphite", material_class=MaterialClass.CONDUCTOR, regions=("C 1s",), material="graphite")], "C 1s")
rf = next(r for r in load_reference_fits('docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip') if r.name == "C1s Scan_6")
log = {}
orig_stab, orig_fit = eng.run_stability_analysis, eng.fit_candidate
def stab(x, y, weights, model, primary_fit, *a, **k):
    rec = log.setdefault(model.name, [])
    def fit(*fa, **fk):
        t0 = time.perf_counter()
        o = orig_fit(*fa, **fk)
        rec.append({"sec": round(time.perf_counter() - t0, 2), "nfev": o.lmfit_result.nfev if o.lmfit_result is not None else None, "converged": o.converged, "chi2": o.weighted_chi_sq,
                    "support": {c.slot_role: (None if getattr(c, "support", None) is None else (round(c.support.get("f") or 0, 2), c.support.get("supported"), c.support.get("follows"))) for c in o.components},
                    "amp": {c.slot_role: round(c.amplitude, 1) for c in o.components}})
        return o
    eng.fit_candidate = fit
    try:
        st = orig_stab(x, y, weights, model, primary_fit, *a, **k)
    finally:
        eng.fit_candidate = orig_fit
    log[model.name + "#primary"] = {"chi2": primary_fit.weighted_chi_sq,
        "support": {c.slot_role: (None if getattr(c, "support", None) is None else (round(c.support.get("f") or 0, 2), c.support.get("supported"))) for c in primary_fit.components}}
    log[model.name + "#persistence"] = {r: round(s.persistence, 2) for r, s in st.per_slot.items()}
    log[model.name + "#n_attempted"] = st.n_attempted
    return st
eng.run_stability_analysis = stab
res = get_method("ic_model_comparison").run(rf.roi_be, rf.roi_intensity, grammar=g,
      options={"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0, "candidate_filter": ["MG2_graphAsymGL_aliph_sat_CO_C=O", "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "AG2_linked", "A2_linked"], "enable_proposal_pass": False})
print("winner", res.diagnostics["winner"], res.diagnostics["conditional"], res.diagnostics["conditional_reason"])
for c in res.analysis["candidates"]:
    print(f"  {c['name'][:44]:44s} chi2r {c['reduced_chi_sq']:.2f} minpers {c['min_active_persistence']:.2f} survived {c['survived']} absent {[a['role'] for a in c.get('absent_slots') or []]}")
json.dump(log, open(sys.argv[2], 'w'), indent=1, default=str)
