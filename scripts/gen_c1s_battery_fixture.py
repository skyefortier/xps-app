#!/usr/bin/env python
"""
Generate tests/autofit/fixtures/c1s_battery_expected.json — the frozen
characterization records for the C 1s parity battery.

Regenerate ONLY when an intentional change to fitting.py's numerics is being
made and has been reviewed; the whole point of the fixture is that it fails
loudly on unintentional drift:

    venv/bin/python scripts/gen_c1s_battery_fixture.py
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autofit.parity import battery_eligible, refit_record  # noqa: E402
from autofit.reference import load_reference_fits  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "docs", "autofit", "test_data")
OUT = os.path.join(
    os.path.dirname(__file__), "..", "tests", "autofit", "fixtures",
    "c1s_battery_expected.json",
)


def main() -> None:
    records = []
    skipped = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            ok, reason = battery_eligible(rf, region="C 1s")
            if not ok:
                if reason != "not C 1s":
                    skipped.append({"project": rf.project, "name": rf.name,
                                    "reason": reason})
                continue
            records.append(refit_record(rf))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"records": records, "skipped": skipped}, f, indent=1, sort_keys=True)
    print(f"{len(records)} records frozen, {len(skipped)} skipped -> {OUT}")
    for s in skipped:
        print(f"  skipped: {s['project']} / {s['name']} — {s['reason']}")


if __name__ == "__main__":
    main()
