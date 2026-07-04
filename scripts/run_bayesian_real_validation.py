#!/usr/bin/env python
"""
Bayesian exchange-MC method — REAL-DATA validation + sampler-tunable study
(the Monday follow-up flagged in PROGRESS.md: the method was validated only
on synthetic ground truth; sampler tunables are UNVERIFIED).

For each region anchor (the same expert-fit anchors the IC parity gates use):

  1. run the IC method (engine defaults, gate OPTIONS) — the reference
     treatment;
  2. run the Bayesian method at the default sampler settings with 2 seeds;
  3. on the CHEAP anchors (Cl 2p, B 1s) additionally run a one-factor-at-a-
     time sweep over the UNVERIFIED sampler tunables (n_replicas, beta_min,
     n_sweeps, exchange_every) — winner stability and free-energy spread
     across seeds/settings is the evidence for promoting/demoting defaults;
  4. record everything (winner, per-candidate F/weights, σ̂, swap acceptance,
     min ESS + honesty warnings, winner peak params + posterior CIs, runtime)
     to a JSONL results file, incrementally (resumable: done (anchor, method,
     config, seed) tuples are skipped on re-run).

Usage:
  venv/bin/python scripts/run_bayesian_real_validation.py --probe   # ~1 min/anchor timing probe
  venv/bin/python scripts/run_bayesian_real_validation.py           # full battery (background-scale)
  venv/bin/python scripts/run_bayesian_real_validation.py Cl2p_Scan # one anchor only

Output: docs/autofit/inventory/bayesian_real_validation_runs.jsonl
Report assembly: docs/autofit/bayesian-real-validation.md (hand-written from
the JSONL — the JSONL is the evidence of record).
"""
import argparse
import json
import os
import sys
import time

REPO = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.abspath(REPO))

from autofit.grammar import MaterialClass, Phase, resolve          # noqa: E402
from autofit.methods import get_method                             # noqa: E402
from autofit.reference import load_reference_fits                  # noqa: E402

DATA = os.path.join(REPO, "docs", "autofit", "test_data")
OUT = os.path.join(REPO, "docs", "autofit", "inventory",
                   "bayesian_real_validation_runs.jsonl")

GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")
UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
             regions=("U 4f", "Cl 2p"))
B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
            regions=("B 1s", "C 1s"))

# Reduced C 1s candidate set = the parity gate's (full 25-candidate grammar is
# calibration-scale, not per-run scale).
C1S_GATE_CANDIDATES = [
    "MG2_graphAsymGL_aliph_sat_CO_C=O",
    "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O",
    "AG2_linked",
    "A2_linked",
]

IC_OPTIONS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
              "enable_proposal_pass": False}

ANCHORS = {
    # cheap: few candidates, few params -> OFAT tunable sweep runs here
    "Cl2p_Scan":   dict(project="Cl2p_projfit_test.proj.zip", name="Cl2p Scan",
                        region="Cl 2p", phases=[UCL4], cand_filter=None, tier="cheap"),
    "Cl2p_Scan_0": dict(project="Cl2p_projfit_test.proj.zip", name="Cl2p Scan_0",
                        region="Cl 2p", phases=[UCL4], cand_filter=None, tier="cheap"),
    "B1s_Scan":    dict(project="B4C-UCl4.proj.zip", name="B1s Scan",
                        region="B 1s", phases=[B4C], cand_filter=None, tier="cheap"),
    # expensive: LACX convolutions / many params -> default-config validation only
    "U4f_Scan":    dict(project="B4C-UCl4.proj.zip", name="U4f Scan",
                        region="U 4f", phases=[UCL4], cand_filter=None, tier="expensive"),
    "C1s_Scan_8":  dict(project="UCl4_on_graphite.proj.zip", name="C1s Scan_8",
                        region="C 1s", phases=[GRAPHITE],
                        cand_filter=C1S_GATE_CANDIDATES, tier="expensive"),
}

DEFAULTS = dict(n_replicas=12, beta_min=1e-4, n_sweeps=1500,
                burn_fraction=0.5, exchange_every=5)

# OFAT variations for the UNVERIFIED tunables (cheap anchors only).
VARIATIONS = [
    {},                            # defaults
    {"n_replicas": 8},
    {"n_replicas": 16},
    {"beta_min": 1e-3},
    {"n_sweeps": 3000},
    {"exchange_every": 1},
    {"burn_fraction": 0.3},
]
SEEDS = [0, 1]


def _anchor_rf(spec):
    path = os.path.join(DATA, spec["project"])
    return next(r for r in load_reference_fits(path) if r.name == spec["name"])


def _expert_summary(rf):
    return {
        "chi_reduced": rf.fit_result.get("chiReduced"),
        "peaks": [{"name": p.get("name"), "center": p.get("center"),
                   "fwhm": p.get("fwhm"), "amplitude": p.get("amplitude"),
                   "shape": p.get("shape")} for p in rf.peaks],
    }


def _key(rec):
    return (rec["anchor"], rec["method"], json.dumps(rec.get("config") or {},
            sort_keys=True), rec.get("seed"))


def _done_keys():
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            for line in f:
                try:
                    done.add(_key(json.loads(line)))
                except Exception:
                    continue
        return done
    return done


def _emit(rec):
    with open(OUT, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def run_ic(anchor, spec, rf, grammar, done):
    rec = {"anchor": anchor, "method": "ic_model_comparison",
           "config": IC_OPTIONS, "seed": IC_OPTIONS["rng_seed"]}
    if _key(rec) in done:
        print(f"  [skip] IC {anchor} already recorded")
        return
    t0 = time.time()
    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar, options=dict(IC_OPTIONS))
    rec.update(
        runtime_s=round(time.time() - t0, 1), success=res.success,
        winner=(res.diagnostics or {}).get("winner"),
        conditional=(res.analysis or {}).get("conditional"),
        candidates=[{k: c.get(k) for k in
                     ("name", "bic_star", "reduced_chi_sq", "rank",
                      "conditional", "boundary_hits")}
                    for c in (res.analysis or {}).get("candidates", [])
                    if isinstance(c, dict)],
        peaks=res.peaks, expert=_expert_summary(rf),
    )
    _emit(rec)
    print(f"  IC {anchor}: winner={rec['winner']} ({rec['runtime_s']}s)")


def run_bayes(anchor, spec, rf, grammar, config, seed, done, probe=False):
    cfg = dict(DEFAULTS, **config)
    if probe:
        cfg["n_sweeps"] = 120
    rec = {"anchor": anchor, "method": "bayesian_exchange_mc",
           "config": cfg, "seed": seed}
    if not probe and _key(rec) in done:
        print(f"  [skip] bayes {anchor} cfg={config} seed={seed} already recorded")
        return
    opts = dict(cfg, rng_seed=seed)
    if spec["cand_filter"]:
        opts["candidate_filter"] = spec["cand_filter"]
    t0 = time.time()
    res = get_method("bayesian_exchange_mc").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar, options=opts)
    dt = round(time.time() - t0, 1)
    if probe:
        print(f"  [probe] {anchor}: {dt}s at 120 sweeps "
              f"-> est {dt * cfg_scale(cfg):.0f}s at {DEFAULTS['n_sweeps']}")
        return
    rec.update(
        runtime_s=dt, success=res.success,
        winner=(res.diagnostics or {}).get("winner"),
        selection_warning=(res.analysis or {}).get("model_selection_warning"),
        candidates=(res.analysis or {}).get("candidates"),
        sigma_hat=(res.diagnostics or {}).get("sigma_hat"),
        peaks=res.peaks, confidence=res.confidence,
        expert=_expert_summary(rf),
    )
    _emit(rec)
    w = rec.get("winner")
    print(f"  bayes {anchor} cfg={config or 'default'} seed={seed}: "
          f"winner={w} ({dt}s)")


def cfg_scale(cfg):
    return DEFAULTS["n_sweeps"] / 120.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("anchors", nargs="*", help="subset of anchors to run")
    ap.add_argument("--probe", action="store_true",
                    help="timing probe only (120 sweeps, nothing recorded)")
    args = ap.parse_args()

    names = args.anchors or list(ANCHORS)
    unknown = [n for n in names if n not in ANCHORS]
    if unknown:
        raise SystemExit(f"unknown anchors: {unknown} (have {list(ANCHORS)})")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    done = _done_keys()
    for name in names:
        spec = ANCHORS[name]
        rf = _anchor_rf(spec)
        grammar = resolve(spec["phases"], spec["region"])
        print(f"== {name} ({spec['region']}, {len(grammar.candidates)} candidates) ==",
              flush=True)
        if args.probe:
            run_bayes(name, spec, rf, grammar, {}, 0, done, probe=True)
            continue
        run_ic(name, spec, rf, grammar, done)
        for seed in SEEDS:
            run_bayes(name, spec, rf, grammar, {}, seed, done)
        if spec["tier"] == "cheap":
            for var in VARIATIONS[1:]:
                run_bayes(name, spec, rf, grammar, var, SEEDS[0], done)
    print("DONE")


if __name__ == "__main__":
    main()
