"""CI guard for the JS suite (node --test TAP summary). Fails unless the log
carries a COMPLETE summary (tests, pass, fail, cancelled, skipped, todo), at
least --min-passed tests PASSED, none failed or was cancelled, no more than
--max-skipped were skipped and --max-todo left as todo, and the counts add up.
A suite that was skipped, shrank, or stopped early is a failure, not a pass
(Codex archive round 2: the total `tests` counts skipped tests too).
Usage: python scripts/ci_check_node_tap.py js.log --min-passed 500 [--max-skipped 0] [--max-todo 2]"""
import argparse
import re
import sys

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--min-passed", type=int, required=True)
ap.add_argument("--max-skipped", type=int, default=0)
ap.add_argument("--max-todo", type=int, default=2)
a = ap.parse_args()
text = open(a.log, encoding="utf8", errors="replace").read()
KEYS = ("tests", "pass", "fail", "cancelled", "skipped", "todo")
found = {}
for k, v in re.findall(r"^# (tests|pass|fail|cancelled|skipped|todo) (\d+)$", text, re.M):
    found[k] = int(v)                     # the last summary wins (node prints one at the end)
print(found)
problems = [f"summary line '# {k}' missing" for k in KEYS if k not in found]
if not problems:
    if found["pass"] < a.min_passed:
        problems.append(f"only {found['pass']} tests passed (floor {a.min_passed})")
    for k in ("fail", "cancelled"):
        if found[k]:
            problems.append(f"{found[k]} {k}")
    if found["skipped"] > a.max_skipped:
        problems.append(f"{found['skipped']} skipped (at most {a.max_skipped})")
    if found["todo"] > a.max_todo:
        problems.append(f"{found['todo']} todo (at most {a.max_todo})")
    if found["pass"] + found["fail"] + found["cancelled"] + found["skipped"] + found["todo"] != found["tests"]:
        problems.append("the counts do not add up to the total")
if problems:
    print("JS suite guard FAILED: " + "; ".join(problems))
    sys.exit(1)
print("JS suite guard ok")
