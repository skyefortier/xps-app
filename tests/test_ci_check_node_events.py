"""The JS-suite CI guard (scripts/ci_check_node_tap.py) against REAL node --test
runs: a green run passes; every way a run can look green without running its
tests fails (Codex archive rounds 2-3: a fully skipped suite, a skipped
`describe` node leaves out of `# skipped`, concatenated or partial summaries)."""
import os
import shutil
import subprocess
import sys

import pytest

GUARD = os.path.join(os.path.dirname(__file__), "..", "scripts", "ci_check_node_tap.py")
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is required (the CI runner has it)")

HEAD = "const { test, describe } = require('node:test');\n"
GREEN = HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {}); test('later', { todo: true }, () => {});\n"


def _node_log(tmp_path, name, src):
    f = tmp_path / f"{name}.test.js"
    f.write_text(src)
    r = subprocess.run([NODE, "--test", "--test-reporter=tap", str(f)], capture_output=True, text=True)
    return r.stdout + r.stderr


def _guard(tmp_path, text, min_passed=3):
    log = tmp_path / "js.log"
    log.write_text(text)
    return subprocess.run([sys.executable, GUARD, str(log), "--min-passed", str(min_passed), "--max-todo", "1"],
                          capture_output=True, text=True)


def test_a_green_run_passes(tmp_path):
    r = _guard(tmp_path, _node_log(tmp_path, "green", GREEN))
    assert r.returncode == 0, r.stdout


@pytest.mark.parametrize("name,src", [
    ("skipped_suite", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                             "describe.skip('the archive tests', () => { test('x', () => {}); });\n"),
    ("nested_skip", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                           "describe('outer', () => { test.skip('inner', () => {}); });\n"),
    ("everything_skipped", HEAD + "test.skip('a', () => {}); test.skip('b', () => {}); test.skip('c', () => {});\n"),
    ("a_failure", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {}); test('d', () => { throw new Error('x'); });\n"),
    ("too_many_todo", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                             "test('t1', { todo: true }, () => {}); test('t2', { todo: true }, () => {});\n"),
    ("too_few_passed", HEAD + "test('a', () => {});\n"),
    ("crash_before_the_summary", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => { process.exit(0); });\n"),
])
def test_a_run_that_did_not_really_run_its_tests_fails(tmp_path, name, src):
    r = _guard(tmp_path, _node_log(tmp_path, name, src))
    assert r.returncode != 0, r.stdout


def test_concatenated_runs_fail(tmp_path):
    failing = _node_log(tmp_path, "failing", HEAD + "test('a', () => { throw new Error('x'); });\n")
    green = _node_log(tmp_path, "green", GREEN)
    assert _guard(tmp_path, failing + green).returncode != 0
    assert _guard(tmp_path, green + "TAP version 13\n# tests 4\n").returncode != 0      # a trailing partial run
