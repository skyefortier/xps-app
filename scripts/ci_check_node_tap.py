"""CI guard for the JS suite (node --test, TAP reporter). A suite that was
skipped, shrank, stopped early or was concatenated with another run is a
FAILURE, not a pass. It reads the TAP STREAM, not only the summary counters
(Codex archive rounds 2-3: the counter `# tests` includes skips, and node
leaves a skipped `describe` out of `# skipped`):

  * no `# SKIP` directive on any test line, at any nesting level;
  * at most --max-todo `# TODO` directives (the documented ones);
  * exactly one TAP run (one `TAP version` header) and exactly one complete,
    contiguous summary block after the last test line: tests, pass, fail,
    cancelled, skipped, todo each exactly once;
  * at least --min-passed tests passed, none failed or cancelled, the counts
    add up. The workflow's floor is the suite's CURRENT pass count, so a test
    that stops registering (a file that exits before defining its tests, a
    deleted test) fails CI; raise it when tests are added.

Usage: python scripts/ci_check_node_tap.py js.log --min-passed 508 [--max-todo 2]"""
import argparse
import re
import sys

REQUIRED = ("tests", "pass", "fail", "cancelled", "skipped", "todo")
OPTIONAL = ("suites", "duration_ms")
SUMMARY = re.compile(r"^# (" + "|".join(REQUIRED + OPTIONAL) + r") (\d+(?:\.\d+)?)$")
TEST_LINE = re.compile(r"^\s*(?:not )?ok \d+\b(.*)$")
DIRECTIVE = re.compile(r"#\s*(SKIP|TODO)\b", re.I)


def check(text, min_passed, max_todo):
    lines = text.splitlines()
    problems = []
    headers = [i for i, l in enumerate(lines) if l.startswith("TAP version")]
    if len(headers) != 1:
        problems.append(f"{len(headers)} TAP runs in the log (exactly one expected)")
    skips = todos = 0
    last_test = -1
    for i, l in enumerate(lines):
        m = TEST_LINE.match(l)
        if m:
            last_test = i
            d = DIRECTIVE.search(m.group(1))
            if d and d.group(1).upper() == "SKIP":
                skips += 1
            elif d:
                todos += 1
    if skips:
        problems.append(f"{skips} test / suite line(s) carry a SKIP directive")
    if todos > max_todo:
        problems.append(f"{todos} TODO directives (at most {max_todo})")
    summary_idx = [i for i, l in enumerate(lines) if SUMMARY.match(l)]
    found = {}
    for i in summary_idx:
        k, v = SUMMARY.match(lines[i]).groups()
        if k in found:
            problems.append(f"summary line '# {k}' appears more than once")
        found[k] = float(v) if "." in v else int(v)
    missing = [k for k in REQUIRED if k not in found]
    if missing:
        problems.append("summary incomplete: " + ", ".join("'# " + k + "'" for k in missing) + " missing")
    if summary_idx:
        if summary_idx != list(range(summary_idx[0], summary_idx[0] + len(summary_idx))):
            problems.append("the summary lines are not one contiguous block")
        if summary_idx[0] < last_test:
            problems.append("a summary appears before the last test line")
    if not missing:
        if found["pass"] < min_passed:
            problems.append(f"only {found['pass']} tests passed (floor {min_passed})")
        for k in ("fail", "cancelled", "skipped"):
            if found[k]:
                problems.append(f"{found[k]} {k}")
        if found["todo"] > max_todo:
            problems.append(f"{found['todo']} todo (at most {max_todo})")
        if sum(found[k] for k in ("pass", "fail", "cancelled", "skipped", "todo")) != found["tests"]:
            problems.append("the counts do not add up to the total")
    return found, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("--min-passed", type=int, required=True)
    ap.add_argument("--max-todo", type=int, default=2)
    a = ap.parse_args()
    found, problems = check(open(a.log, encoding="utf8", errors="replace").read(), a.min_passed, a.max_todo)
    print(found)
    if problems:
        print("JS suite guard FAILED: " + "; ".join(problems))
        sys.exit(1)
    print("JS suite guard ok")


if __name__ == "__main__":
    main()
