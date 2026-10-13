Reviewed `e668919` against both reviewed branch tips and `b804968`. **No integration-specific BLOCKER, MAJOR, or MINOR found.**

- **Merge resolutions:** both sandbox stubs survive. The CI floor is consistent: `629 + 13 + 5 = 647`. The three functions modified by both branches—spectrum save, project save, table export—retain Q5’s implementation plus Q8’s early busy guard. No unrelated production change found.
- **Final warning:** `_autoFitPublish` installs and stamps the final result before the 40% check. That check uses Q5’s `_areaGrid()` and trapezoid calculation.
- **Busy refresh:** **yes, it can render Results and patch sidebar areas beneath the overlay.** It does not publish an accepted fit or history snapshot. Between fits, `state.fitResult` remains null; save/export guards return before synchronization or serialization.
- **Undo/redo and rollback:** production-function probes restored the previous grid, area signature, Results content, and outside-window note for both current and stale restored fits.
- **Saved areas:** both `_savedPeakAreas` and `savedPeakAreas` survived rollback and repeated Undo/Redo, then serialized verbatim through spectrum and project saves. Refused busy saves left them untouched.

**Validation:** 89 focused JavaScript tests passed, plus the integration probes above. Existing orchestration tests still use stubs; browser assertions do not directly cover every combined invariant. I did not independently reproduce the recorded full-suite totals: the full JS attempt encountered Python temporary-directory failures under the read-only sandbox, and browser/server suites were not rerun.

Non-physical inputs: no defect identified requiring classification. Preservation probes used deliberately marked historical areas. No files changed.

VERDICT: GO
