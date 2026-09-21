#!/usr/bin/env python3
"""Measure the SHIPPED scattered-starts check on every committed fit target:
what the page would show (same / not better elsewhere / alternatives with
their centre shifts) and what it costs. Each target is fitted as the page
sends it (Trust-Region, n_perturb 3, inputs rounded to 2 dp), once with
n_starts=0 and once with n_starts=K, so the added time is measured directly
and the fit itself can be checked to be unchanged.

Usage: python scripts/scattered_starts_measure.py targets.json out.jsonl [shard n_shards] [K]
"""
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitting  # noqa: E402

warnings.filterwarnings("ignore")


def main(targets_path, out_path, shard=0, n_shards=1, k=3):
    targets = json.loads(Path(targets_path).read_text())
    if n_shards > 1:
        out_path = str(Path(out_path).with_suffix("")) + f".shard{shard}.jsonl"
    with open(out_path, "w") as fh:
        for i, t in enumerate(targets):
            if i % n_shards != shard:
                continue
            b = t["background"]
            args = (np.asarray(t["be"], float), np.round(np.asarray(t["inten"], float), 2), t["specs"])
            kw = dict(background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
                      endpoint_avg=b["endpoint_avg"], n_perturb=3, fit_kws={"method": "least_squares"})
            t0 = time.time(); base = fitting.run_fit(*args, **kw); t_base = time.time() - t0
            t0 = time.time(); res = fitting.run_fit(*args, n_starts=k, **kw); t_with = time.time() - t0
            names = {str(s["id"]): s.get("name") for s in t["specs"]}
            st = res["starts"]
            rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"], "region": t["region"],
                   "n_unlinked": sum(1 for s in t["specs"] if s.get("constrain_to") is None),
                   "fit_chi2r": res["statistics"]["reduced_chi_square"], "base_chi2r": base["statistics"]["reduced_chi_square"],
                   "seconds_base": round(t_base, 2), "seconds_with": round(t_with, 2), "starts": {k2: v for k2, v in st.items() if k2 != "alternatives"}}
            if st.get("ran"):
                rec["alternatives"] = [{"chi2r": a["chi2r"], "n_starts": a["n_starts"], "dfrac_pp": a["largest_fraction_difference_pp"],
                                        "shift_name": names.get(str(a["largest_centre_shift_from_start"]["id"])),
                                        "shift_ev": a["largest_centre_shift_from_start"]["ev"]} for a in st["alternatives"]]
            fh.write(json.dumps(rec) + "\n"); fh.flush()


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], *(int(v) for v in a[2:5]))
