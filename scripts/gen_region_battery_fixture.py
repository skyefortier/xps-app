#!/usr/bin/env python
"""
Generic per-region characterization-fixture generator (successor to the
c1s/u4f-specific scripts, kept for the cookbook regions):

    venv/bin/python scripts/gen_region_battery_fixture.py "B 1s" b1s_battery_expected.json
    venv/bin/python scripts/gen_region_battery_fixture.py "Cl 2p" cl2p_battery_expected.json

Regenerate ONLY for reviewed, intentional numerics changes.
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autofit.parity import battery_eligible, refit_record  # noqa: E402
from autofit.reference import load_reference_fits  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "docs", "autofit", "test_data")
FIXTURES = os.path.join(os.path.dirname(__file__), "..", "tests", "autofit", "fixtures")


def main() -> None:
    region, out_name = sys.argv[1], sys.argv[2]
    records, skipped = [], []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            ok, reason = battery_eligible(rf, region=region)
            if not ok:
                if reason != f"not {region}":
                    skipped.append({"project": rf.project, "name": rf.name,
                                    "reason": reason})
                continue
            records.append(refit_record(rf))
    out = os.path.join(FIXTURES, out_name)
    os.makedirs(FIXTURES, exist_ok=True)
    with open(out, "w") as f:
        json.dump({"records": records, "skipped": skipped}, f, indent=1, sort_keys=True)
    print(f"{region}: {len(records)} records frozen, {len(skipped)} skipped -> {out}")
    for s in skipped:
        print(f"  skipped: {s['project']} / {s['name']} — {s['reason']}")


if __name__ == "__main__":
    main()
