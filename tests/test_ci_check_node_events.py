"""The JS-suite CI guard (scripts/ci_check_node_events.py, reading the events of
scripts/ci_node_events_reporter.mjs) against REAL node --test runs: a green run
passes; every way a run can look green without running its tests fails (Codex
archive rounds 2-4: a fully skipped suite, a skipped `describe` node leaves out
of `# skipped`, a skipped suite whose NAME carries an escaped "# TODO",
concatenated, partial or truncated logs, a failed fragment prepended), and a
test whose name merely mentions "# SKIP" is not mistaken for a skip."""
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
GUARD = os.path.join(ROOT, "scripts", "ci_check_node_events.py")
REPORTER = os.path.abspath(os.path.join(ROOT, "scripts", "ci_node_events_reporter.mjs"))
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is required (the CI runner has it)")

HEAD = "const { test, describe } = require('node:test');\n"
GREEN = HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {}); test('later', { todo: true }, () => {});\n"


def _events(tmp_path, name, *srcs):
    files = []
    for i, src in enumerate(srcs):
        f = tmp_path / f"{name}_{i}.test.js"
        f.write_text(src)
        files.append(str(f))
    dest = tmp_path / f"{name}.jsonl"
    subprocess.run([NODE, "--test", "--test-reporter=tap", "--test-reporter-destination=stdout",
                    f"--test-reporter={REPORTER}", f"--test-reporter-destination={dest}", *files],
                   capture_output=True, text=True)
    return dest.read_text()


def _guard(tmp_path, text, min_passed=3):
    log = tmp_path / "events.jsonl"
    log.write_text(text)
    return subprocess.run([sys.executable, GUARD, str(log), "--min-passed", str(min_passed), "--max-todo", "1"],
                          capture_output=True, text=True)


def test_a_green_run_passes(tmp_path):
    r = _guard(tmp_path, _events(tmp_path, "green", GREEN))
    assert r.returncode == 0, r.stdout


def test_a_green_run_over_several_files_passes(tmp_path):
    r = _guard(tmp_path, _events(tmp_path, "two", HEAD + "test('a', () => {}); test('b', () => {});\n",
                                 HEAD + "test('c', () => {}); test('later', { todo: true }, () => {});\n"))
    assert r.returncode == 0, r.stdout


def test_a_failing_todo_is_a_todo_not_a_failure(tmp_path):
    # the suite's two documented todos fail by design; node's run still succeeds
    r = _guard(tmp_path, _events(tmp_path, "todo_fails", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {}); "
                                 "test('known gap', { todo: true }, () => { throw new Error('gap'); });\n"))
    assert r.returncode == 0, r.stdout


def test_a_name_that_mentions_skip_or_todo_is_not_a_directive(tmp_path):
    r = _guard(tmp_path, _events(tmp_path, "names", HEAD + "test('handles # SKIP', () => {}); "
                                 "test('mentions \\\\# TODO', () => {}); test('c', () => {});\n"))
    assert r.returncode == 0, r.stdout


@pytest.mark.parametrize("name,src", [
    ("skipped_suite", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                             "describe.skip('the archive tests', () => { test('x', () => {}); });\n"),
    ("skipped_suite_escaped_todo_name", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                             "describe.skip('Find Peaks \\\\# TODO archive', () => { test('x', () => {}); });\n"),
    ("nested_skip", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                           "describe('outer', () => { test.skip('inner', () => {}); });\n"),
    ("everything_skipped", HEAD + "test.skip('a', () => {}); test.skip('b', () => {}); test.skip('c', () => {});\n"),
    ("a_failure", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {}); test('d', () => { throw new Error('x'); });\n"),
    ("too_many_todo", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                             "test('t1', { todo: true }, () => {}); test('t2', { todo: true }, () => {});\n"),
    ("too_few_passed", HEAD + "test('a', () => {});\n"),
    ("exit_inside_a_test", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => { process.exit(0); });\n"),
    ("a_file_that_does_not_load", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\nthrow new Error('load');\n"),
])
def test_a_run_that_did_not_really_run_its_tests_fails(tmp_path, name, src):
    r = _guard(tmp_path, _events(tmp_path, name, src))
    assert r.returncode != 0, r.stdout


def test_concatenated_truncated_or_spliced_logs_fail(tmp_path):
    green = _events(tmp_path, "green", GREEN)
    failing = _events(tmp_path, "failing", HEAD + "test('a', () => { throw new Error('x'); });\n")
    lines = green.splitlines(keepends=True)
    assert _guard(tmp_path, failing + green).returncode != 0                    # two runs
    assert _guard(tmp_path, green + green).returncode != 0                      # two green runs
    assert _guard(tmp_path, "".join(lines[:-1])).returncode != 0                # no 'end': node did not finish
    assert _guard(tmp_path, green + lines[-1][:5]).returncode != 0              # a partial trailing line
    assert _guard(tmp_path, green + '{"type": "start"}\n').returncode != 0      # an unfinished second run
    fragment = "".join(l for l in failing.splitlines(keepends=True) if '"test:fail"' in l)
    assert fragment
    assert _guard(tmp_path, lines[0] + fragment + "".join(lines[1:])).returncode != 0   # a failed fragment spliced in
    no_results = "".join(l for l in lines if '"test:pass"' not in l)
    assert _guard(tmp_path, no_results).returncode != 0                         # results removed, summary kept
