#!/usr/bin/env python
"""
Synthetic hard-case stress battery — EVERY method against KNOWN ground
truth in the regimes the real anchors lack (run-brief item 2).

Cases: tests/autofit/stress_cases.py (parameter-level truth + seeded
Poisson noise; expectation classes recover/ambiguous/prune/honesty — the
KEY CRITERION: where the data cannot distinguish models the engine must
REPORT ambiguity, never confidently pick one; where there IS a right
answer it must recover it).

Methods × configs per case:
- least_squares       — TRUE-structure manual model (recovery baseline)
- ic_model_comparison — n_refits=4 and n_refits=12 (the 4-refit config
                        measured landing in wrong basins on razor-sharp
                        high-count surfaces — that sensitivity is itself
                        battery evidence)
- bayesian_exchange_mc — small budget (8 replicas / 600 sweeps, rng 0):
                        budget-honesty flags are part of what is measured
- sparse_map          — grammar-window dictionary (Gaussian atoms;
                        documented weaknesses are expected findings)

Noise-draw replicates: seed offsets (0, 1000, 2000) for LS/IC/sparse;
Bayesian runs the base draw only (runtime).

Output: docs/autofit/inventory/stress_battery_runs.jsonl — append-only,
resumable (done (case, variant, method, config) keys are skipped), one
record per run with the winner, truth-matched parameter errors, and every
machine-readable ambiguity/honesty signal.  The JSONL is the evidence of
record; docs/autofit/stress-test-report.md summarizes it.

Usage:  venv/bin/python scripts/run_stress_battery.py            # full
        venv/bin/python scripts/run_stress_battery.py overlap    # name filter
"""
import json
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "tests", "autofit"))

import numpy as np                                                  # noqa: E402

from autofit.methods import get_method                              # noqa: E402
from stress_cases import build_all_cases                            # noqa: E402

OUT = os.path.join(REPO, "docs", "autofit", "inventory",
                   "stress_battery_runs.jsonl")

SEED_OFFSETS = (0, 1000, 2000)
IC_CONFIGS = ({"n_refits": 4}, {"n_refits": 12})
# weights: the suite's premise is that Poisson noise makes 1/sqrt(y)
# weights CORRECT BY CONSTRUCTION — the Bayesian method defaults to UNIT
# weights (homoscedastic σ-marginalized), so the battery passes the
# Poisson weights explicitly (Codex stress review: unweighted Bayesian
# evidence would not test the intended noise regime).  The "weights" key
# is part of the resume identity.
BAYES_CFG = {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0,
             "weights": "poisson_like"}


def _key(rec):
    return (rec["case"], rec["seed_offset"], rec["method"],
            json.dumps(rec.get("config") or {}, sort_keys=True))


def _done():
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            for line in f:
                try:
                    done.add(_key(json.loads(line)))
                except Exception:
                    continue
    return done


def _emit(rec):
    with open(OUT, "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")


def _match_truth(truth, comps):
    """ONE-TO-ONE assignment of fitted components to truth peaks (greedy by
    distance; a component can serve only one truth peak — Codex stress
    review: nearest-neighbor reuse let one atom 'match' both doublet
    members).  Unmatched truth peaks record match=None."""
    pairs = sorted(
        ((abs(c["center"] - t["center"]), ti, ci)
         for ti, t in enumerate(truth)
         for ci, c in enumerate(comps)
         if c.get("center") is not None),
        key=lambda p: p[0])
    t_used, c_used, assign = set(), set(), {}
    for _, ti, ci in pairs:
        if ti in t_used or ci in c_used:
            continue
        t_used.add(ti); c_used.add(ci); assign[ti] = ci
    errs = []
    for ti, t in enumerate(truth):
        if ti not in assign:
            errs.append(None)
            continue
        best = comps[assign[ti]]
        errs.append({
            "true_center": t["center"],
            "d_center_ev": round(best["center"] - t["center"], 4),
            "d_fwhm_ev": (round(best["fwhm"] - t["fwhm"], 4)
                          if "fwhm" in t and best.get("fwhm") is not None else None),
            "matched_role": best.get("role") or best.get("id"),
        })
    return errs


def _base(case, off, method, config):
    return {"case": case.name, "regime": case.regime,
            "expectation": case.expectation, "truth_n": case.truth_n,
            "seed_offset": off, "method": method, "config": config,
            "true_candidates": list(case.true_candidates),
            "notes": case.notes}


def run_ls(case, off, done):
    rec = _base(case, off, "least_squares", {"background_method":
                "shirley" if case.bg != "linear" else "linear"})
    if _key(rec) in done:
        return
    t0 = time.time()
    try:
        res = get_method("least_squares").run(
            case.x, case.y, peak_specs=case.ls_specs,
            options=dict(rec["config"]))
        comps = [{"center": p.get("center"), "fwhm": p.get("fwhm"),
                  "id": p.get("id")} for p in res.peaks]
        rec.update(success=bool(res.success),
                   chi_reduced=res.analysis["statistics"].get("reduced_chi_square"),
                   truth_match=_match_truth(case.truth, comps))
    except Exception as e:                                   # honest failure
        rec.update(success=False, error=f"{type(e).__name__}: {e}")
    rec["runtime_s"] = round(time.time() - t0, 2)
    _emit(rec)


def run_ic(case, off, config, done):
    rec = _base(case, off, "ic_model_comparison", dict(config))
    if _key(rec) in done:
        return
    t0 = time.time()
    try:
        res = get_method("ic_model_comparison").run(
            case.x, case.y, grammar=case.grammar,
            options={**config, "rng_seed": 0, "noise_floor": 1.0,
                     "enable_proposal_pass": True})
        d, a = res.diagnostics, res.analysis
        wc = next((c for c in a["candidates"]
                   if c["name"] == d.get("winner")), {})
        comps = [{"center": p["center"], "fwhm": p.get("fwhm"),
                  "role": p.get("role")} for p in res.peaks]
        rec.update(
            success=bool(res.success),
            winner=d.get("winner"),
            winner_is_true=any(d.get("winner", "").startswith(t)
                               for t in case.true_candidates),
            n_emitted_components=len(res.peaks),
            conditional=bool(d.get("conditional")),
            conditional_reason=d.get("conditional_reason"),
            ambiguous_pairs=a.get("ambiguous_pairs"),
            filtered_dominant_alternative=d.get("filtered_dominant_alternative"),
            winner_chi_reduced=wc.get("reduced_chi_sq"),
            winner_boundary_hits=wc.get("boundary_hits"),
            winner_autocorr_flag=wc.get("autocorr_flag"),
            winner_residual_flags=wc.get("residual_flags"),
            winner_absent_slots=[s["role"] for s in wc.get("absent_slots", [])],
            accepted_proposals=[p for c in a["candidates"]
                                for p in c.get("proposed_peaks", [])
                                if p.get("accepted")],
            candidates=[{k: c.get(k) for k in
                         ("name", "reduced_chi_sq", "bic_star", "survived",
                          "filter_reason", "min_active_persistence",
                          "orphan_peaks", "boundary_hits")}
                        for c in a["candidates"]],
            truth_match=_match_truth(case.truth, comps),
        )
    except Exception as e:
        rec.update(success=False, error=f"{type(e).__name__}: {e}")
    rec["runtime_s"] = round(time.time() - t0, 2)
    _emit(rec)


def run_bayes(case, off, done):
    rec = _base(case, off, "bayesian_exchange_mc", dict(BAYES_CFG))
    if _key(rec) in done:
        return
    t0 = time.time()
    try:
        from autofit.methods.base import poisson_like_weights
        opts = {k: v for k, v in BAYES_CFG.items() if k != "weights"}
        res = get_method("bayesian_exchange_mc").run(
            case.x, case.y, weights=poisson_like_weights(case.y),
            grammar=case.grammar, options=opts)
        d, a = res.diagnostics, res.analysis
        comps = [{"center": p["center"], "fwhm": p.get("fwhm"),
                  "role": p.get("role")} for p in res.peaks]
        rec.update(
            success=bool(res.success),
            winner=d.get("winner"),
            n_emitted_components=len(res.peaks),
            winner_is_true=any((d.get("winner") or "").startswith(t)
                               for t in case.true_candidates),
            selection_warning=a.get("model_selection_warning"),
            candidates=[{k: c.get(k) for k in
                         ("name", "free_energy", "free_energy_split_half_error",
                          "free_energy_mc_error", "posterior_weight",
                          "posterior_weight_reliable",
                          "min_effective_sample_size", "rank")}
                        for c in (a.get("candidates") or [])],
            truth_match=_match_truth(case.truth, comps),
        )
    except Exception as e:
        rec.update(success=False, error=f"{type(e).__name__}: {e}")
    rec["runtime_s"] = round(time.time() - t0, 2)
    _emit(rec)


def run_sparse(case, off, done):
    rec = _base(case, off, "sparse_map", {})
    if _key(rec) in done:
        return
    t0 = time.time()
    try:
        res = get_method("sparse_map").run(
            case.x, case.y, grammar=case.grammar)
        a = res.analysis
        comps = [{"center": p.get("center"), "fwhm": p.get("fwhm"),
                  "role": p.get("role") or str(i)}
                 for i, p in enumerate(res.peaks)]
        rec.update(
            success=bool(res.success),
            n_selected=len(res.peaks),
            n_correct=(len(res.peaks) == case.truth_n),
            flags={k: a.get(k) for k in a
                   if "flag" in k or "warning" in k or "inexpressible" in k},
            truth_match=_match_truth(case.truth, comps),
        )
    except Exception as e:
        rec.update(success=False, error=f"{type(e).__name__}: {e}")
    rec["runtime_s"] = round(time.time() - t0, 2)
    _emit(rec)


def main():
    name_filter = sys.argv[1] if len(sys.argv) > 1 else ""
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    done = _done()
    for off in SEED_OFFSETS:
        for case in build_all_cases(seed_offset=off):
            if name_filter and name_filter not in case.name:
                continue
            print(f"== {case.name} (offset {off}) ==", flush=True)
            if case.ls_specs:
                run_ls(case, off, done)
            for cfg in IC_CONFIGS:
                run_ic(case, off, cfg, done)
            run_sparse(case, off, done)
            if off == 0:
                run_bayes(case, off, done)
    print("battery complete", flush=True)


if __name__ == "__main__":
    main()
