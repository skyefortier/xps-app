# Q5 + Q8 — combined for one deploy (2026-10-13)

Owner 2026-10-12: "Each as its own unit, Codex x2, stop for my deploy approval (batched is fine)."
Each unit was reviewed on its own branch against main b804968 to Codex GO ×2; this branch merges both
(merge commits keep each unit's reviewed history) for one deploy.

| Unit | Branch | Plan | Codex |
|---|---|---|---|
| Q5 — one area definition, the server's, on one grid, for every reader | `feat-one-area` | `2026-10-12-one-area-definition.md` | GO ×2 at round 5 |
| Q8 — Auto-Fit refits after its charge shift, as one transaction | `feat-autofit-refit` | `2026-10-12-autofit-refit-after-shift.md` | GO ×2 at round 3 |

Both units merge the measurement branch `measure-q5-q8` (docs and scripts only).

## What the merge changed

- **Text conflicts:** the CI JS floor (combined count) and one test sandbox in
  `tests/js/stale_statistics.test.js`, where Q5 added an `_areaGrid` stub and Q8 an `_autoFitBlocks`
  stub (both kept). `templates/index.html` merged cleanly.
- **Where the units meet:** Auto-Fit's 40 % graphite warning (`_autoFitCheckGraphiteFraction`, Q5: the
  one area grid) is now called from Q8's `_autoFitPublish`, for the final fit; Q8's undo of an
  Auto-Fit restores the previous result, after which Q5's readers integrate on `_areaGrid()` of that
  result (current or stale) and the area signatures re-render what changed.

## Codex on the combination (round 1, GO ×2)

Both runs: no BLOCKER, MAJOR or MINOR. The merged serializers and export keep Q5's area handling and
Q8's busy guard; the floor 629 + 13 + 5 = 647; `_autoFitPublish` installs the final result before the
40 % check, which uses the one area grid; rollback and Undo / Redo restore the grid, area signature and
note for restored-current and restored-stale fits; marked historical areas survive a rollback, a refused
mid-transaction save and an Undo / Redo, then save verbatim. Observed, not a defect: while Auto-Fit's
overlay is up, the area refresh can repaint the sidebar or the no-fit note BEHIND it — nothing is
published, saved or snapshotted (state.fitResult is null between the fits). Suites on the combination:
pytest 1417 passed / 7 skipped, JS 647 passed. READY for the owner's deploy approval.
