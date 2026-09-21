#!/usr/bin/env python3
"""How often does a fitted component land at or near the amplitude floor?

Measurement only (owner, 2026-09-21: it decides whether the "component not
supported by the data" outcome ships before the scattered-starts check).
Every target of optimizer_disagreement_targets.js is fitted as the page sends
it (Trust-Region, n_perturb 3, seeded) and each component gets the statistic
shipped for the Auto-Fit anchor: with the other components held at their
fitted values, F = ((chi2_without - chi2_with)/p) / (chi2_with/dof);
unsupported = chi2_without <= chi2_with or F < 10. Also recorded: amplitude
relative to the strongest component, and what the response reports for the
component (centre, fwhm, their standard errors) — i.e. what the page shows.

Usage: python scripts/amplitude_floor_frequency.py targets.json out.jsonl [shard n_shards]
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitting  # noqa: E402

warnings.filterwarnings("ignore")


def support(res, ip):
    c, f, g = np.array(res["counts"]), np.array(res["fitted_y"]), np.array(ip["y"])
    w, r = 1 / np.maximum(c, 1), c - f
    cw, cwo = float(np.sum(w * r * r)), float(np.sum(w * (r + g) ** 2))
    p = max(1, sum(1 for v in ip["params"].values() if v.get("vary") and not v.get("expr")))
    dof = max(1, len(c) - res["statistics"].get("n_free_params", 0))
    d = cwo - cw
    F = float("inf") if (cw == 0 and d > 0) else ((d / p) / (cw / dof) if cw > 0 else 0.0)
    return d, F


def main(targets_path, out_path, shard=0, n_shards=1):
    targets = json.loads(Path(targets_path).read_text())
    if n_shards > 1:
        out_path = str(Path(out_path).with_suffix("")) + f".shard{shard}.jsonl"
    with open(out_path, "w") as fh:
        for k, t in enumerate(targets):
            if k % n_shards != shard:
                continue
            b = t["background"]
            try:
                res = fitting.run_fit(np.asarray(t["be"], float), np.round(np.asarray(t["inten"], float), 2), t["specs"],
                                      background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
                                      endpoint_avg=b["endpoint_avg"], n_perturb=3, fit_kws={"method": "least_squares"})
            except Exception as exc:
                fh.write(json.dumps({"id": t["id"], "error": str(exc)[:200]}) + "\n")
                continue
            top = max(ip["params"]["amplitude"]["value"] for ip in res["individual_peaks"])
            names = {str(s["id"]): s.get("name") for s in t["specs"]}
            linked = {str(s["id"]): s.get("constrain_to") is not None for s in t["specs"]}
            comps = []
            for ip in res["individual_peaks"]:
                d, F = support(res, ip)
                par = ip["params"]
                comps.append({"id": ip["id"], "name": names.get(str(ip["id"])), "linked": linked.get(str(ip["id"])),
                              "amplitude": par["amplitude"]["value"], "amp_over_top": par["amplitude"]["value"] / top if top > 0 else 0.0,
                              "start_amplitude": next(s["amplitude"] for s in t["specs"] if str(s["id"]) == str(ip["id"])),
                              "dchi2": d, "F": F, "unsupported": bool(d <= 0 or F < 10),
                              "center": par["center"]["value"], "center_stderr": par["center"].get("stderr"),
                              "fwhm": par["fwhm"]["value"] if "fwhm" in par else None,
                              "fwhm_stderr": par["fwhm"].get("stderr") if "fwhm" in par else None,
                              "area": par["area"]["value"]})
            fh.write(json.dumps({"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"], "region": t["region"],
                                 "success": bool(res["success"]), "chi2r": res["statistics"]["reduced_chi_square"], "components": comps}) + "\n")
            fh.flush()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(int(a) for a in sys.argv[3:5]))
