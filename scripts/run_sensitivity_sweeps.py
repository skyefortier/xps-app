#!/usr/bin/env python
"""
Sensitivity sweeps for the UNVERIFIED / CONDITIONAL pipeline constants
(spec §9; PROGRESS 'Remaining work'). One-factor-at-a-time around the
defaults, on the real region anchors, measuring what actually changes:
winner identity, conditional tier/reason, absent slots, main-peak centers,
χ²ᵣ, ambiguity flags.

Constants swept (and how they are injected):
  OPTIONS-plumbed (autofit/methods/ic_model_comparison.py):
    persistence_threshold              0.7   {0.5, 0.6, 0.8, 0.9}
    absent_slot_persistence_threshold  0.7   {0.5, 0.9}
    absent_slot_area_fraction          0.02  {0.01, 0.04, 0.08}
    bic_ambiguity_threshold            2.0   {1.0, 4.0}
    noise_floor ('detection floor')    1.0   {0.5, 2.0, 5.0}
  MODULE-patched (autofit/engine.py):
    CONDITIONAL_OVERRIDE_DELTA_BIC     10.0  {5.0, 20.0, 30.0}
    PROPOSAL_FLAG_RATIO ('residual 5x')5.0   {3.0, 8.0}   [proposal pass ON]
  REGION-patched (autofit/regions/cl2p.py — CONDITIONAL constants,
  discrepancy #7):
    CL2P_RATIO_RANGE upper bound       0.55  {0.60, 0.65, 0.75}
    CL2P_SPLITTING_RANGE               (1.55,1.65)  {(1.50,1.70)}
  REGION-patched (autofit/regions/c1s.py — graphitic α cap):
    DSG_ALPHA_RANGE_GRAPHITIC upper    (cap) {0.2, 0.5}   [C 1s anchor]

Cheap anchors get every applicable sweep; the C 1s anchor runs only the
constants that need it (α cap, proposal flag ratio). Results JSONL is
resumable (done keys skipped) — safe to re-run after interruption.

Usage: venv/bin/python scripts/run_sensitivity_sweeps.py [group ...]
Groups: options, override, proposal, cl2p, c1s_alpha (default: all)
Output: docs/autofit/inventory/sensitivity_sweeps.jsonl
"""
import argparse
import json
import os
import sys
import time

REPO = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(REPO))

import autofit.engine as engine                                     # noqa: E402
import autofit.regions.cl2p as cl2p_mod                             # noqa: E402
import autofit.regions.c1s as c1s_mod                               # noqa: E402
from autofit.grammar import MaterialClass, Phase, resolve           # noqa: E402
from autofit.methods import get_method                              # noqa: E402
from autofit.reference import load_reference_fits                   # noqa: E402

DATA = os.path.join(REPO, "docs", "autofit", "test_data")
OUT = os.path.join(REPO, "docs", "autofit", "inventory",
                   "sensitivity_sweeps.jsonl")

UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
             regions=("U 4f", "Cl 2p"))
B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
            regions=("B 1s", "C 1s"))
GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")

BASE_OPTIONS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
                "enable_proposal_pass": False}

CHEAP_ANCHORS = [
    ("Cl2p_Scan",   "Cl2p_projfit_test.proj.zip", "Cl2p Scan",   "Cl 2p", [UCL4], None),
    ("Cl2p_Scan_0", "Cl2p_projfit_test.proj.zip", "Cl2p Scan_0", "Cl 2p", [UCL4], None),
    ("B1s_Scan",    "B4C-UCl4.proj.zip",          "B1s Scan",    "B 1s",  [B4C],  None),
    ("U4f_Scan",    "B4C-UCl4.proj.zip",          "U4f Scan",    "U 4f",  [UCL4], None),
]
C1S_ANCHOR = ("C1s_Scan_8", "UCl4_on_graphite.proj.zip", "C1s Scan_8",
              "C 1s", [GRAPHITE],
              ["MG2_graphAsymGL_aliph_sat_CO_C=O",
               "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O",
               "AG2_linked", "A2_linked"])

OPTION_SWEEPS = {
    "persistence_threshold":             [0.5, 0.6, 0.8, 0.9],
    "absent_slot_persistence_threshold": [0.5, 0.9],
    "absent_slot_area_fraction":         [0.01, 0.04, 0.08],
    "bic_ambiguity_threshold":           [1.0, 4.0],
    "noise_floor":                       [0.5, 2.0, 5.0],
}
OVERRIDE_SWEEP = [5.0, 20.0, 30.0]      # CONDITIONAL_OVERRIDE_DELTA_BIC (10*)
PROPOSAL_SWEEP = [3.0, 8.0]             # PROPOSAL_FLAG_RATIO (5*), proposal ON
CL2P_RATIO_UPPER_SWEEP = [0.60, 0.65, 0.75]
CL2P_SPLIT_SWEEP = [(1.50, 1.70)]
C1S_ALPHA_UPPER_SWEEP = [0.2, 0.5]      # DSG_ALPHA_RANGE_GRAPHITIC cap (0.3*)


def _anchor_rf(project, name):
    return next(r for r in load_reference_fits(os.path.join(DATA, project))
                if r.name == name)


def _key(rec):
    return (rec["anchor"], rec["group"], rec["constant"],
            json.dumps(rec["value"]), json.dumps(rec.get("extra_opts") or {}))


def _done():
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                done.add(_key(json.loads(line)))
            except Exception:
                pass
    return done


def _summarize(res):
    winner = (res.diagnostics or {}).get("winner")
    analysis = res.analysis or {}
    wc = next((c for c in analysis.get("candidates", [])
               if isinstance(c, dict) and c.get("name") == winner), {}) or {}
    return {
        "success": res.success,
        "winner": winner,
        "conditional": analysis.get("conditional_tier"),
        "conditional_reason": analysis.get("conditional_reason"),
        "winner_chi_r": wc.get("reduced_chi_sq"),
        "winner_bic_star": wc.get("bic_star"),
        "winner_absent_slots": wc.get("absent_slots"),
        "winner_boundary_hits": wc.get("boundary_hits"),
        "ambiguous_pairs": analysis.get("ambiguous_pairs"),
        "peaks": {p["role"]: {"center": round(p["center"], 4),
                              "fwhm": round(p["fwhm"], 4),
                              "amplitude": round(p["amplitude"], 2)}
                  for p in (res.peaks or [])},
    }


def _run(anchor_spec, extra_opts=None, cand_filter=None):
    aname, project, name, region, phases, base_filter = anchor_spec
    rf = _anchor_rf(project, name)
    grammar = resolve(phases, region)
    opts = dict(BASE_OPTIONS, **(extra_opts or {}))
    cf = cand_filter or base_filter
    if cf:
        opts["candidate_filter"] = cf
    t0 = time.time()
    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar, options=opts)
    out = _summarize(res)
    out["runtime_s"] = round(time.time() - t0, 1)
    return out


def _emit(rec):
    with open(OUT, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print(f"  {rec['anchor']} {rec['constant']}={rec['value']}: "
          f"winner={rec['result']['winner']} cond={rec['result']['conditional']}"
          f" ({rec['result']['runtime_s']}s)", flush=True)


def sweep_options(done):
    for anchor in CHEAP_ANCHORS:
        # baseline record (constant='<default>')
        rec = {"anchor": anchor[0], "group": "options",
               "constant": "<default>", "value": None}
        if _key(rec) not in done:
            rec["result"] = _run(anchor)
            _emit(rec)
        for const, values in OPTION_SWEEPS.items():
            for v in values:
                rec = {"anchor": anchor[0], "group": "options",
                       "constant": const, "value": v}
                if _key(rec) in done:
                    continue
                rec["result"] = _run(anchor, extra_opts={const: v})
                _emit(rec)


def sweep_override(done):
    for anchor in CHEAP_ANCHORS:
        for v in OVERRIDE_SWEEP:
            rec = {"anchor": anchor[0], "group": "override",
                   "constant": "CONDITIONAL_OVERRIDE_DELTA_BIC", "value": v}
            if _key(rec) in done:
                continue
            saved = engine.CONDITIONAL_OVERRIDE_DELTA_BIC
            try:
                engine.CONDITIONAL_OVERRIDE_DELTA_BIC = v
                rec["result"] = _run(anchor)
            finally:
                engine.CONDITIONAL_OVERRIDE_DELTA_BIC = saved
            _emit(rec)


def sweep_proposal(done):
    # proposal-pass constants only matter with the pass enabled; the C 1s
    # anchor carries the known out-of-grammar 283.4 eV component
    for anchor in (C1S_ANCHOR,):
        base = {"enable_proposal_pass": True}
        rec = {"anchor": anchor[0], "group": "proposal",
               "constant": "<default+proposal_on>", "value": None,
               "extra_opts": base}
        if _key(rec) not in done:
            rec["result"] = _run(anchor, extra_opts=base)
            _emit(rec)
        for v in PROPOSAL_SWEEP:
            rec = {"anchor": anchor[0], "group": "proposal",
                   "constant": "PROPOSAL_FLAG_RATIO", "value": v,
                   "extra_opts": base}
            if _key(rec) in done:
                continue
            saved = engine.PROPOSAL_FLAG_RATIO
            try:
                engine.PROPOSAL_FLAG_RATIO = v
                rec["result"] = _run(anchor, extra_opts=base)
            finally:
                engine.PROPOSAL_FLAG_RATIO = saved
            _emit(rec)


def sweep_cl2p(done):
    anchors = [a for a in CHEAP_ANCHORS if a[3] == "Cl 2p"]
    for anchor in anchors:
        for upper in CL2P_RATIO_UPPER_SWEEP:
            rec = {"anchor": anchor[0], "group": "cl2p",
                   "constant": "CL2P_RATIO_RANGE_upper", "value": upper}
            if _key(rec) in done:
                continue
            saved = cl2p_mod.CL2P_RATIO_RANGE
            try:
                cl2p_mod.CL2P_RATIO_RANGE = (saved[0], upper)
                rec["result"] = _run(anchor)
            finally:
                cl2p_mod.CL2P_RATIO_RANGE = saved
            _emit(rec)
        for rng in CL2P_SPLIT_SWEEP:
            rec = {"anchor": anchor[0], "group": "cl2p",
                   "constant": "CL2P_SPLITTING_RANGE", "value": list(rng)}
            if _key(rec) in done:
                continue
            saved = cl2p_mod.CL2P_SPLITTING_RANGE
            try:
                cl2p_mod.CL2P_SPLITTING_RANGE = rng
                rec["result"] = _run(anchor)
            finally:
                cl2p_mod.CL2P_SPLITTING_RANGE = saved
            _emit(rec)


def sweep_c1s_alpha(done):
    anchor = C1S_ANCHOR
    rec = {"anchor": anchor[0], "group": "options",
           "constant": "<default>", "value": None}
    if _key(rec) not in done:
        rec["result"] = _run(anchor)
        _emit(rec)
    for upper in C1S_ALPHA_UPPER_SWEEP:
        rec = {"anchor": anchor[0], "group": "c1s_alpha",
               "constant": "DSG_ALPHA_RANGE_GRAPHITIC_upper", "value": upper}
        if _key(rec) in done:
            continue
        saved = c1s_mod.DSG_ALPHA_RANGE_GRAPHITIC
        try:
            c1s_mod.DSG_ALPHA_RANGE_GRAPHITIC = (saved[0], upper)
            rec["result"] = _run(anchor)
        finally:
            c1s_mod.DSG_ALPHA_RANGE_GRAPHITIC = saved
        _emit(rec)


GROUPS = {"options": sweep_options, "override": sweep_override,
          "proposal": sweep_proposal, "cl2p": sweep_cl2p,
          "c1s_alpha": sweep_c1s_alpha}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("groups", nargs="*", default=[])
    args = ap.parse_args()
    groups = args.groups or list(GROUPS)
    unknown = [g for g in groups if g not in GROUPS]
    if unknown:
        raise SystemExit(f"unknown groups {unknown}; have {list(GROUPS)}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    done = _done()
    for g in groups:
        print(f"== sweep group: {g} ==", flush=True)
        GROUPS[g](done)
    print("DONE")


if __name__ == "__main__":
    main()
