#!/usr/bin/env python
"""
Empirical replicate-noise survey over the labeled projects' repeat scans
(run-brief item 3a) — writes the evidence to
docs/autofit/inventory/replicate_noise_survey.json and prints the table.

Pure measurement: no engine behavior changes; consumers OPT IN to the
resulting weights through the existing ``weights=`` method seam.
"""
import collections
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO)

from autofit.noise import estimate_noise_from_replicates      # noqa: E402
from autofit.reference import load_reference_fits             # noqa: E402

DATA = os.path.join(REPO, "docs", "autofit", "test_data")
OUT = os.path.join(REPO, "docs", "autofit", "inventory",
                   "replicate_noise_survey.json")

PROJECTS = (
    "Cl2p_projfit_test.proj.zip",
    "B4C-UCl4.proj.zip",
    "UCl4_on_graphite.proj.zip",
    "8-JT Graphite.proj.zip",
    "1-GTA UCl4-graphite one set of U doublets.proj.zip",
    "Project9_CasaXPS_newfit.proj.zip",
    "4-GTA UCl4-BN.proj.zip",
)


def main():
    groups = collections.defaultdict(list)
    for proj in PROJECTS:
        path = os.path.join(DATA, proj)
        if not os.path.exists(path):
            continue
        for rf in load_reference_fits(path):
            base = (rf.name.rsplit("_", 1)[0]
                    if rf.name.rsplit("_", 1)[-1].isdigit() else rf.name)
            groups[(proj, base)].append(rf)

    rows = []
    for (proj, base), fits in sorted(groups.items()):
        if len(fits) < 3:
            continue
        rec = {"project": proj, "group": base, "n_replicates": len(fits)}
        try:
            m = estimate_noise_from_replicates(
                fits[0].raw_be, [rf.raw_intensity for rf in fits])
            rec.update(m.summary())
        except ValueError as e:
            rec["error"] = str(e)
        rows.append(rec)
        b = rec.get("b")
        print(f"{proj[:12]:12s} {base:12s} n={rec['n_replicates']:2d} "
              f"a={rec.get('a', float('nan')):9.1f} "
              f"b={b if b is None else round(b, 3)!s:>7s} "
              f"drift={rec.get('drift_fraction', 0) * 100:5.1f}% "
              f"flags={[f.split(':')[0] for f in rec.get('flags', [])]}")

    with open(OUT, "w") as f:
        json.dump({"note": ("replicate-difference noise survey; see "
                            "autofit/noise.py for the estimator and its "
                            "corrections"), "rows": rows}, f, indent=1)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
