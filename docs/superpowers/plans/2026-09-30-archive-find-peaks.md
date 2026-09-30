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
