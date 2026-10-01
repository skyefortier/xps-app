"""The JS-suite CI guard (scripts/ci_check_node_events.py, reading the events of
scripts/ci_node_events_reporter.mjs) against REAL node --test runs: a green run
passes; every way a run can look green without running its tests fails (Codex
archive rounds 2-5: a fully skipped suite, a skipped `describe` node leaves out
of `# skipped`, a skipped suite whose NAME carries an escaped "# TODO",
concatenated, partial or truncated logs, a failed fragment prepended, a file that
exits before its tests or defines none — node emits a synthetic pass for it —
and a deleted result line), and a test whose name merely mentions "# SKIP" is
not mistaken for a skip."""
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


class Run(str):
    """A run's event log, carrying the files it was given (the guard's --expect-files). A log
    built by splicing runs is a plain str and must name its roster explicitly (Codex round 6:
    a shared roster made the splice checks fail for the wrong reason)."""
    files = ()


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
    run = Run(dest.read_text())
    run.files = tuple(files)
    return run


def _guard(tmp_path, text, min_passed=3, files=None):
    log = tmp_path / "events.jsonl"
    log.write_text(text)
    return subprocess.run([sys.executable, GUARD, str(log), "--min-passed", str(min_passed), "--max-todo", "1",
                           "--expect-files", *(files if files is not None else text.files)],
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
    ("skipped_suite_empty_reason", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                             "describe('Find Peaks', { skip: '' }, () => {});\n"),
    ("skipped_test_empty_reason", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"
                             "test('Find Peaks', { skip: '' }, () => {});\n"),
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
    g, both = green.files, green.files + failing.files
    lines = green.splitlines(keepends=True)
    assert _guard(tmp_path, str(green), files=g).returncode == 0                          # the baseline passes
    assert _guard(tmp_path, failing + green, files=both).returncode != 0                  # two runs
    assert _guard(tmp_path, green + green, files=g).returncode != 0                       # two green runs
    assert _guard(tmp_path, "".join(lines[:-1]), files=g).returncode != 0                 # no 'end': node did not finish
    assert _guard(tmp_path, green + lines[-1][:5], files=g).returncode != 0               # a partial trailing line
    assert _guard(tmp_path, green + '{"type": "start"}\n', files=g).returncode != 0       # an unfinished second run
    fragment = "".join(l for l in failing.splitlines(keepends=True) if '"test:fail"' in l)
    assert fragment
    assert _guard(tmp_path, lines[0] + fragment + "".join(lines[1:]), files=g).returncode != 0   # a failed fragment spliced in
    no_results = "".join(l for l in lines if '"test:pass"' not in l)
    assert _guard(tmp_path, no_results, files=g).returncode != 0                          # results removed, summary kept


GOOD = HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {});\n"


@pytest.mark.parametrize("name,other", [
    ("exits_before_registering", HEAD + "process.exit(0);\ntest('Find Peaks', () => { throw new Error('unreached'); });\n"),
    ("exits_inside_its_only_test", HEAD + "test('Find Peaks', () => { process.exit(0); throw new Error('unreached'); });\n"),
    ("an_empty_file", ""),
    ("a_file_with_no_tests", "console.log('no tests');\n"),
])
def test_a_file_that_did_not_run_its_tests_fails_even_when_the_floor_is_met(tmp_path, name, other):
    # Codex round 5: node substitutes a synthetic PASS under the file's name; the other file alone
    # meets the floor of 3, so only the per-file completion check can catch it
    r = _guard(tmp_path, _events(tmp_path, name, GOOD, other))
    assert r.returncode != 0, r.stdout
    assert "did not run to completion" in r.stdout


def test_an_expected_file_absent_from_the_run_fails(tmp_path):
    text = _events(tmp_path, "one", GOOD)
    missing = tmp_path / "never_run.test.js"
    missing.write_text(GOOD)
    assert _guard(tmp_path, text).returncode == 0
    assert _guard(tmp_path, text, files=text.files + (str(missing),)).returncode != 0


def test_a_deleted_result_line_fails(tmp_path):
    # Codex round 5: every summary counter is reconciled with the results, per file and for the run
    text = _events(tmp_path, "del", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {}); "
                   "test('t', { todo: true }, () => {}); describe('s', () => { test('d', () => {}); });\n")
    assert _guard(tmp_path, text).returncode == 0
    lines = text.splitlines(keepends=True)
    todo = [i for i, l in enumerate(lines) if '"todo":true' in l]
    suite = [i for i, l in enumerate(lines) if '"kind":"suite"' in l]
    assert todo and suite
    for i in (todo[0], suite[0]):
        assert _guard(tmp_path, "".join(l for j, l in enumerate(lines) if j != i), files=text.files).returncode != 0


def test_the_run_summary_must_close_the_stream(tmp_path):
    run = _events(tmp_path, "order", GOOD)
    lines = run.splitlines(keepends=True)
    k = next(i for i, l in enumerate(lines) if l.startswith('{"type":"summary"'))
    early = [lines[0], lines[k]] + [l for i, l in enumerate(lines[1:], 1) if i != k]   # summary right after start
    assert _guard(tmp_path, "".join(lines), files=run.files).returncode == 0
    assert _guard(tmp_path, "".join(early), files=run.files).returncode != 0


def test_an_empty_todo_reason_is_still_a_todo(tmp_path):
    # Codex round 6: node gives the reason as the field's value; '' is still the directive
    run = _events(tmp_path, "todo_empty", HEAD + "test('a', () => {}); test('b', () => {}); test('c', () => {}); "
                  "test('t1', { todo: '' }, () => {}); test('t2', { todo: '' }, () => {});\n")
    r = _guard(tmp_path, run)
    assert r.returncode != 0 and "todo results (at most 1)" in r.stdout, r.stdout
