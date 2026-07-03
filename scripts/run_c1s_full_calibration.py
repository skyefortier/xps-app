#!/usr/bin/env python
"""
Full-grammar C 1s calibration: the entire 25-candidate C 1s grammar +
IC pipeline on real expert-fitted anchor spectra, printing winner /
survivors / flags / per-peak decomposition and the delta to the expert fit.

This is the SLOW companion to tests/autofit/test_c1s_parity_gate.py (which
uses a reduced candidate set to stay test-loop-sized).  Run when the grammar
or engine changes materially:

    venv/bin/python scripts/run_c1s_full_calibration.py            # 3 anchors
    venv/bin/python scripts/run_c1s_full_calibration.py --refits 8
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autofit.grammar import MaterialClass, Phase, resolve  # noqa: E402
from autofit.methods import get_method  # noqa: E402
from autofit.reference import load_reference_fits  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "docs", "autofit", "test_data")

ANCHORS = [
    ("UCl4_on_graphite.proj.zip", "C1s Scan_8"),
    ("8-JT Graphite.proj.zip", "C1s Scan_2"),
    ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refits", type=int, default=8)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    graphite = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                     regions=("C 1s",), material="graphite")
    grammar = resolve([graphite], "C 1s")
    print(f"grammar: {len(grammar.candidates)} candidates; refits={args.refits}")
    method = get_method("ic_model_comparison")

    for project, name in ANCHORS:
        rf = next(r for r in load_reference_fits(os.path.join(DATA, project))
                  if r.name == name)
        expert_graphite = next(
            (p for p in rf.peaks if "graphit" in (p.get("name") or "").lower()), None)
        print("=" * 84)
        print(f"{rf.project} / {rf.name}  expert χ²ᵣ={rf.fit_result.get('chiReduced'):.2f} "
              f"graphite={expert_graphite and round(expert_graphite['center'], 3)}")
        t0 = time.time()
        res = method.run(rf.roi_be, rf.roi_intensity, grammar=grammar,
                         options={"n_refits": args.refits, "rng_seed": args.seed,
                                  "noise_floor": 1.0})
        print(f"  ran {time.time() - t0:.0f}s  success={res.success}")
        a = res.analysis
        if res.success:
            print(f"  winner {res.diagnostics['winner']}  survivors "
                  f"{res.diagnostics['n_survivors']}  ambiguous "
                  f"{len(a['ambiguous_pairs'])}  bic_ambiguous "
                  f"{a['criteria_panel']['bic_ambiguous']}  conflict "
                  f"{a['criteria_panel']['criteria_conflict']}")
            for p in res.peaks:
                print(f"    {p['role']:<26} c={p['center']:.3f} "
                      f"fwhm={p['fwhm']:.3f} amp={p['amplitude']:.0f}")
            if expert_graphite:
                mg = next((p for p in res.peaks if p["role"] == "main_graphitic"), None)
                if mg:
                    print(f"  Δmain = {abs(mg['center'] - expert_graphite['center'])*1000:.0f} meV")
            surv = sorted((c for c in a["candidates"] if c["survived"]),
                          key=lambda c: c["rank"])
            print("  ranked:", [(c["name"], round(c["reduced_chi_sq"], 2))
                                for c in surv[:6]])
        else:
            print("  NO SURVIVOR:", res.message[:120])
            for c in a["candidates"]:
                print(f"    {c['name']:<34} χ²ᵣ={c['reduced_chi_sq']:.2f} "
                      f"{str(c['filter_reason'])[:70]}")


if __name__ == "__main__":
    main()
