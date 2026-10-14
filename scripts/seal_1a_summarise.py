"""Seal 1a′: the numbers in docs/findings/seal-1a/README.md, from the JSONL beside it.

Usage: python scripts/seal_1a_summarise.py [docs/findings/seal-1a]
"""
import json
import os
import sys

D = sys.argv[1] if len(sys.argv) > 1 else "docs/findings/seal-1a"


def rows(name):
    p = os.path.join(D, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


for name in ("statistics_tr.jsonl", "statistics_lm.jsonl"):
    R = rows(name)
    if not R:
        continue
    G = [r for r in R if "error" not in r]
    print(f"== {name}: {len(R)} targets, {len(R) - len(G)} errors, {sum(r['success'] for r in G)} converged")
    for k in ("chi_square", "reduced_chi_square", "aic", "bic"):
        v = [r["rel"][k] for r in G]
        print(f"  {k}: identical {sum(x == 0 for x in v)} / {len(v)}; max relative difference {max(v):.3g}")
    print(f"  best_fit == fitted_sub: {sum(r['best_fit_is_fitted_sub'] for r in G)} / {len(G)}; "
          f"nvarys == roles count: {sum(r['nvarys_equal'] for r in G)} / {len(G)}")
    states = {}
    for r in G:
        states[r["verify"]] = states.get(r["verify"], 0) + 1
    print(f"  in-process verification: {states}; not consistent: "
          f"{[(r['tab'], r['verify_check']) for r in G if r['verify'] != 'consistent']}")

ident = rows("refactor_identity_lm.jsonl")
ctrl = {r["id"]: r for r in rows("control_main_vs_main_lm.jsonl")}
if ident:
    differ = [r for r in ident if not r["identical"]]
    print(f"== refactor identity (main vs branch, Levenberg-Marquardt, n_perturb 3): identical "
          f"{len(ident) - len(differ)} / {len(ident)}")
    for r in differ:
        c = ctrl.get(r["id"])
        cs = "no control" if c is None else ("control identical" if c["identical"] else f"control differs {c['differ']}")
        print(f"  {r['tab']:12s} {','.join(r['shapes']):22s} differs {r['differ']}; {cs}")
    print(f"  of the differing: control also differs on "
          f"{sum(1 for r in differ if r['id'] in ctrl and not ctrl[r['id']]['identical'])}, "
          f"control identical on {sum(1 for r in differ if r['id'] in ctrl and ctrl[r['id']]['identical'])}, "
          f"no control {sum(1 for r in differ if r['id'] not in ctrl)}")

fin = rows("final_identity_differing_lm.jsonl")
if fin:
    same = sum(1 for r in fin if r["same_fit_within_rounding"] is True)
    bad = [(r["tab"], r["same_fit_within_rounding"]) for r in fin
           if not r["identical"] and r["same_fit_within_rounding"] is not True]
    print(f"== final code vs main on those targets: identical {sum(r['identical'] for r in fin)} / {len(fin)}, "
          f"same fit within rounding {same}, otherwise {bad}; added {sorted(set(a for r in fin for a in r['added']))}")
