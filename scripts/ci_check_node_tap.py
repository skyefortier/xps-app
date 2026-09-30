"""CI guard for the JS suite (node --test TAP summary): fail unless at least
--min-tests tests ran and none failed or was cancelled — a suite that shrank or
stopped early is a failure, not a pass. Usage: python scripts/ci_check_node_tap.py js.log --min-tests 500"""
import argparse
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--min-tests", type=int, required=True)
a = ap.parse_args()
text = open(a.log, encoding="utf8", errors="replace").read()
counts = {k: int(v) for k, v in re.findall(r"^# (tests|pass|fail|cancelled|skipped|todo) (\d+)$", text, re.M)}
print(counts)
problems = []
if counts.get("tests", 0) < a.min_tests:
    problems.append(f"only {counts.get('tests', 0)} tests ran (floor {a.min_tests})")
for k in ("fail", "cancelled"):
    if counts.get(k, 0):
        problems.append(f"{counts[k]} {k}")
if problems:
    print("JS suite guard FAILED: " + "; ".join(problems))
    sys.exit(1)
print("JS suite guard ok")
