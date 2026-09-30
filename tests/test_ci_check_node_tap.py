"""The JS-suite CI guard (scripts/ci_check_node_tap.py) passes a complete, green
node --test summary and fails every way a suite can look green without running
(Codex archive round 2: a fully skipped suite exited 0)."""
import os
import subprocess
import sys

import pytest

GUARD = os.path.join(os.path.dirname(__file__), "..", "scripts", "ci_check_node_tap.py")


def _run(tmp_path, summary, *args):
    log = tmp_path / "js.log"
    log.write_text("ok 1 - something\n" + "".join(f"# {k} {v}\n" for k, v in summary.items()))
    return subprocess.run([sys.executable, GUARD, str(log), "--min-passed", "500", *args], capture_output=True, text=True).returncode


GREEN = {"tests": 510, "pass": 508, "fail": 0, "cancelled": 0, "skipped": 0, "todo": 2}


def test_a_complete_green_summary_passes(tmp_path):
    assert _run(tmp_path, GREEN) == 0


@pytest.mark.parametrize("bad", [
    {**GREEN, "pass": 0, "skipped": 508},                       # everything skipped
    {**GREEN, "pass": 400, "tests": 402},                       # the suite shrank
    {**GREEN, "pass": 507, "fail": 1},                          # a failure
    {**GREEN, "pass": 507, "cancelled": 1},                     # a cancellation
    {**GREEN, "pass": 505, "todo": 5},                          # more todo than documented
    {**GREEN, "pass": 505},                                     # counts do not add up
    {"tests": 510},                                             # a truncated log
])
def test_a_suite_that_did_not_really_run_fails(tmp_path, bad):
    assert _run(tmp_path, bad) != 0
