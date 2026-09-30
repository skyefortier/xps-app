"""CI guard for the JS suite. A suite that was skipped, shrank, stopped early
or was concatenated with another run is a FAILURE, not a pass.

It reads the STRUCTURED events written by scripts/ci_node_events_reporter.mjs
(one JSON object per line), never the TAP text: rounds 2-4 of the archive
unit's Codex review each found another way the text could mislead a parser
(`# tests` counts skips; node leaves a skipped describe out of `# skipped`;
several or partial summaries; a test NAME carrying an escaped "# SKIP" or
"# TODO"). Here skip, todo, suite / test and failure are node's own fields.

  * every line is a JSON object; exactly one "start" (the first line), exactly
    one "end" (the last line, written only after node's stream finished) and
    exactly one run summary;
  * no failed result, and no skipped result — test or suite, any nesting;
  * at most --max-todo todo results (a todo test may fail — node reports it as
    test:fail with todo set, and the run still succeeds — so a todo result
    counts against --max-todo, never as a failure);
  * at least --min-passed passed tests (non-todo tests, not suites), and the
    run summary agrees: passed equals that count, failed = cancelled =
    skipped = 0, success true. The workflow's floor is the suite's CURRENT pass
    count, so a test that stops registering fails CI; raise it when tests are
    added.

Usage: python scripts/ci_check_node_events.py js-events.jsonl --min-passed 508 [--max-todo 2]"""
import argparse
import json
import sys


def check(text, min_passed, max_todo):
    problems = []
    events = []
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except ValueError:
            problems.append(f"line {n} is not a JSON event")
            continue
        if not isinstance(e, dict) or "type" not in e:
            problems.append(f"line {n} is not an event object")
            continue
        events.append(e)
    types = [e["type"] for e in events]
    if types.count("start") != 1 or not types or types[0] != "start":
        problems.append("the log does not open with exactly one 'start'")
    if types.count("end") != 1 or not types or types[-1] != "end":
        problems.append("the log does not close with exactly one 'end' (node's stream did not finish, or several runs)")
    summaries = [e for e in events if e["type"] == "summary"]
    if len(summaries) != 1:
        problems.append(f"{len(summaries)} run summaries (exactly one expected)")
    results = [e for e in events if e["type"] in ("test:pass", "test:fail")]
    fails = [e for e in results if e["type"] == "test:fail" and not e.get("todo")]
    skips = [e for e in results if e.get("skip")]
    todos = [e for e in results if e.get("todo")]
    passed = [e for e in results if e["type"] == "test:pass" and e.get("kind") == "test"
              and not e.get("skip") and not e.get("todo")]
    if fails:
        problems.append(f"{len(fails)} failed result(s): " + ", ".join(repr(e.get("name")) for e in fails[:5]))
    if skips:
        problems.append(f"{len(skips)} skipped test / suite result(s): " + ", ".join(repr(e.get("name")) for e in skips[:5]))
    if len(todos) > max_todo:
        problems.append(f"{len(todos)} todo results (at most {max_todo})")
    if len(passed) < min_passed:
        problems.append(f"only {len(passed)} tests passed (floor {min_passed})")
    if len(summaries) == 1:
        c = summaries[0].get("counts") or {}
        if summaries[0].get("success") is not True:
            problems.append("the run summary does not report success")
        for k in ("failed", "cancelled", "skipped"):
            if c.get(k) != 0:
                problems.append(f"the run summary reports {k} = {c.get(k)}")
        if c.get("passed") != len(passed):
            problems.append(f"the run summary's passed ({c.get('passed')}) differs from the passed results ({len(passed)})")
    found = {"passed": len(passed), "todo": len(todos), "skipped": len(skips), "failed": len(fails),
             "summary": summaries[0].get("counts") if len(summaries) == 1 else None}
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
