# Archive Find Peaks (hide, don't delete) — 2026-09-30

Owner: "archive Find Peaks for now. Hide it, don't delete it. Hide Find Peaks
from the UI: remove the Actions-menu entry and every other entry point so it
cannot be started. KEEP on main, running in CI: the backend, the autofit
engine, /api/analyze, and all Find Peaks tests, so it can be revived.
Everything Run Fit now shares must stay intact and working — the job/polling
infrastructure, the support F test, the scattered-starts check, the fit key,
the certificate. Saved projects whose peaks came from Find Peaks must load and
fit exactly as before. If a cached Find Peaks result exists in a saved tab, it
must not resurface anywhere in the UI. Release-note line only, no student note."

## 1. Entry points (enumerated before the change)

| site | what | disposition |
|---|---|---|
| Actions menu, `#find-peaks-menu-item` (`onclick="openFindPeaksModal()"`) | the ONLY caller of `openFindPeaksModal` anywhere in the page | removed; an HTML comment in its place says how to revive it |
| `#find-peaks-overlay` (the modal) | opened only by `openFindPeaksModal` | kept, unreachable |
| `runFindPeaks` / `applyFindPeaks` / `_fpRenderResults` | called only from the modal's own buttons (`#fp-run`, `#fp-apply`) and from each other | kept |
| keyboard shortcuts, context menus, other buttons, tooltips, help text | none reference Find Peaks (grep: outside its own block the menu item was the only mention, user-visible or in code) | — |

The Find Peaks block (`<!-- Find Peaks (beta) — opt-in grammar-driven
analysis -->` … `</script>`) is self-contained: no function outside it calls
into it (`_fp*`, `openFindPeaksModal`, `runFindPeaks`, `applyFindPeaks`).

## 2. What a saved project can carry

| data | where | disposition |
|---|---|---|
| a cached result, `tab.findPeaks.last` | runtime-only: no save path writes it; the `.fit.json` import clears it (`active.findPeaks = null`) | never rendered outside the (unreachable) modal; an injected legacy `findPeaks` in a saved tab is not restored (browser test) |
| the provenance record on applied peaks, `peak._findPeaks`; `tab._findPeaksReview` | saved with the peaks (saves spread the peak whole) | read nowhere — not rendered, not exported as a column; kept as data (the peaks load and fit exactly as before) |

## 3. Shared with Run Fit (untouched by this change — only the menu entry moved)

`/api/analyze` + its job records and heartbeat (app.py) share the fit jobs'
infrastructure (`_job_progress_path`, `FIT_JOB_HEARTBEAT_SEC`); the page's
`FIT_HEARTBEAT_LOST_SEC`; `fitting._component_support` (the F test);
the scattered-starts check; the fit key (`_startsLiveKey` / `_sameFitKey`);
the certificate (`fitting._certify_fit`, `autofit.engine._certify_minimum`).
No Python file changes. Find Peaks' own tests (Python engine, API, JS and
browser) drive it programmatically and stay in the suite.

## 4. Tests

- `tests/js/find_peaks_archived.test.js` (static): no entry point outside
  the block; the functions and modal kept; outside the block `findPeaks` is
  only cleared and `_findPeaks` / `_findPeaksReview` never read. Fails on main.
- `tests/test_browser_find_peaks_archived.py` (real browser + server): the
  page and the open Actions menu show no Find Peaks; a project whose peaks came
  from Find Peaks (run and applied programmatically) saves without a cache,
  reloads in a fresh page with an injected legacy cache, the peaks identical,
  nothing of Find Peaks visible, and Run Fit succeeds on the server with
  current statistics. The first test fails on main.

## 5. Release note (at deploy)

Find Peaks is archived: it is no longer offered in the Actions menu. Saved
projects whose peaks came from Find Peaks load and fit exactly as before.

## 6. Codex rounds

**Round 1 — NO-GO ×2** (`docs/autofit/codex/archive_find_peaks_verdict_run{A,B}.md`,
commit 9dc28a3; both: no remaining launch path, no cached-result or provenance
display path, runtime HTML identical to main's apart from the removed button,
backend / engine / shared fitting code unchanged, the static test fails on
main with valid block boundaries, the browser test's analysis is real):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): the JS tests — Find Peaks' own among them — do not run in CI: the workflow runs pytest only (a gap older than this unit; the owner's criterion is "all Find Peaks tests … running in CI") | `.github/workflows/autofit-gates.yml` fast-suite: `setup-node` + `node --test tests/js/*.test.js`, guarded by `scripts/ci_check_node_tap.py` (fails on any failure / cancellation or fewer than 500 tests). The JS tests that call the backend fall back to `python3`, the job's set-up interpreter. (Runs on GitHub are not observable from this machine — no `gh`.) |
| 2 | MINOR (A, B): PROGRESS.md's Unit B row cited a record absent from this branch, gave a range (k = 0.43–0.75, 1.3–2.3×) the record does not contain, and grouped the support F test with what calibration would change — a constant variance factor cancels in it | the row cites the record with its branch and commit, gives the range that record implies (0.83–2.5×) and the owner's note separately, and states that only the displayed chi2r's absolute value changes (fit, sigmas and F test are invariant) |

**Round 2 — NO-GO ×2** (`archive_find_peaks_r2_verdict_run{A,B}.md`, commit
9593e13; both: a real failing JS assertion fails node and the guard, `pipefail`
keeps it; the glob, the dependencies and the fixtures suit a fresh checkout; the
Unit B range and the invariance claim match their sources; round 1's checks hold):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): the guard counted `# tests`, which includes skipped tests: 510 skipped, 0 passed exited 0; a truncated log with only `# tests` passed too | the guard requires the complete summary, a floor on PASSED tests (500), 0 skipped, at most the 2 documented todos, no failure or cancellation, and counts that add up; `setup-node` runs `if: always()`; `tests/test_ci_check_node_tap.py` pins every case (fully skipped, shrunk, failed, cancelled, extra todo, mismatched counts, truncated) |

**Round 3 — NO-GO ×2** (`archive_find_peaks_r3_verdict_run{A,B}.md`, commit
312396a; both: the archive test fails on main; every committed guard scenario
returns its expected status; node version, glob, `always()`, dependencies and
fixtures suit CI; runtime HTML equivalent to main's apart from comments and the
removed button; backend, serialisation and shared fitting code unchanged; the
Unit B rationale matches its record):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): Node 22 leaves a skipped `describe` SUITE out of `# skipped` — the archive test wrapped in `describe.skip` beside 504 passes gave node exit 0, guard exit 0 | the guard reads the TAP STREAM (`--test-reporter=tap`): any `# SKIP` directive on a test or suite line at any nesting level fails it, whatever the summary says |
| 2 | MINOR (A, B): the guard kept the last value PER FIELD, so a green summary followed by a partial one, or a failed run followed by a green one, passed | exactly one `TAP version` header and exactly one complete, contiguous summary block after the last test line; anything else fails. `tests/test_ci_check_node_tap.py` now runs REAL node for every case (green, skipped suite, nested skip, everything skipped, failure, too many todos, too few passes, crash before the summary, concatenated runs, trailing partial summary); the round-2 guard fails the skipped-suite and concatenation cases, this one passes all nine |

Also in this round (found while fixing, not raised by Codex): the pass floor was
500 against 508 passing, so the archive file's four tests could stop registering
with CI still green. The workflow's floor is now the current pass count, 508
(raise it when tests are added; a lower count fails).

**Round 4 — NO-GO ×2** (`archive_find_peaks_r4_verdict_run{A,B}.md`, commit
d334b0e; both: ordinary skips, failures, cancellations, early exit, complete
concatenations and interleaved console output handled; the 508 floor matches
node's registration (510 tests, 2 todos, no machine-dependent registration);
runtime HTML, backend, serialisation and shared Run Fit code unchanged; no launch
or cached-result path):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): a test NAME can carry an escaped directive — `describe.skip('Find Peaks # TODO archive')` emits `ok 509 - Find Peaks \# TODO archive # SKIP`; the guard took the first match (a TODO) and missed the SKIP; conversely a passing test named `handles # SKIP` failed the guard | THE CLASS, not the case: three rounds each found another way TAP text misleads a parser, so the guard no longer reads text. `scripts/ci_node_events_reporter.mjs`, a second node reporter (the TAP one still prints to the log), writes node's STRUCTURED results — skip, todo, suite / test, failure are node's own fields — one JSON object per line between a `start` and an `end` written only after node's stream finished; `scripts/ci_check_node_events.py` (renamed from `ci_check_node_tap.py`) reads those. Names never matter |
| 2 | MINOR (A, B): partial trailing text, a failed fragment spliced into a green log, results removed with the summary kept, an unfinished `# Subtest:` after the summary — all passed | every line must be a JSON event; exactly one `start` (first), one `end` (last) and one run summary; passes are COUNTED from the results and must equal the summary's; any failed result fails (a todo test that fails is a todo — node's own semantics — counted against the todo bound). `tests/test_ci_check_node_events.py` (14 real-node cases) adds the escaped-name skip, the name that merely mentions `# SKIP`, a file that does not load, a failing todo, two green runs, a missing `end`, a partial line, a spliced failed fragment and removed results |

**Round 5 — NO-GO ×2** (`archive_find_peaks_r5_verdict_run{A,B}.md`, commits
b94a847 + e6e617a — b94a847 carried only the renames, a failed `git add`, and
e6e617a the rest; both: ordinary skips, load errors, hook failures, timeouts,
cancellations, late uncaught errors, nested skips, concatenated streams and
truncations rejected; the real stream passes; 510 registered tests, 508 + 2
todos, nothing machine-dependent; implementation unchanged):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): a file whose process exits before its tests run (or an empty file, or one defining no test) gets a SYNTHETIC pass from node under the file's name, which the guard counted: 507 real passes + that = 508, node and guard exit 0 | the reporter keeps each file's own summary, which node emits only for a file that ran to completion; the guard takes `--expect-files` (the glob node runs) and requires exactly one clean summary per expected file, refuses a result from a file without one, and counts passes only from completed files |
| 2 | MINOR (A): only `passed` was reconciled with the summary; deleting a todo or a suite result line passed | every counter (tests, passed, todo, suites, topLevel) of every file summary and of the run summary is reconciled with the results, and the run summary must be the last event before `end`. `tests/test_ci_check_node_events.py` (21): the four no-completion files beside a file that alone meets the floor, an expected file absent, deleted todo / suite lines, a misplaced summary |

**Round 6 — run A GO, run B NO-GO** (`archive_find_peaks_r6_verdict_run{A,B}.md`,
commit c6358d9; both: early exits, empty files, load / hook failures, timeouts,
cancellations, late errors, nested skips, deleted / duplicated results and file
summaries, concatenation, truncation and a misplaced summary rejected even beside
508 genuine passes; the real stream passes; implementation unchanged):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): the reporter wrote `d.skip \|\| false`, so an EMPTY skip reason (`{ skip: '' }`, which node reports as `# SKIP`) became `false`; node leaves skipped suites out of its counters, so an empty skipped suite passed every reconciliation | a directive is PRESENT when node sets the field at all (`directive(d, key)`), whatever its reason; the same for todo. Pinned: an empty-reason skipped suite, an empty-reason skipped test, empty-reason todos over the bound |
| 2 | MINOR (A): the splice tests shared one roster, so the green run was checked against the failing run's files and every splice failed for the wrong reason | each run carries its own roster (`Run.files`); spliced logs name theirs explicitly; each test asserts its unaltered baseline passes |

**Round 7 — GO ×2, no findings** (`archive_find_peaks_r7_verdict_run{A,B}.md`,
commit 900c0c7): the round-6 fixes hold; adversarial node runs (skips at every
nesting with any reason, empty files, early exits, load / hook failures,
timeouts, cancellations, late errors, truncation, concatenation, deleted or
duplicated records) are rejected even beside 508 genuine passes; a 508-pass /
2-todo run passes and losing one pass fails; runtime HTML equivalent to main
apart from comments and the removed button; backend, serialisation and shared
Run Fit infrastructure unchanged; no launch or cached-result / provenance path.
Ready for the owner's deploy decision.
