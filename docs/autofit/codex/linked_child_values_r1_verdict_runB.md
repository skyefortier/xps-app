# Linked child values (Q10 0c) — Codex round 1, run B (commit 47d5110)

One **MAJOR** finding blocks approval; the browser fix itself appears correct.

- **MAJOR — the Python write-back twin retains the defect, while its parity test stays green.** [autofit/reference.py:170](/Users/skyefortier/xps-app/.claude/worktrees/linked-child/autofit/reference.py:170) still rejects every locked field, including expression-valued fields. The [parity test:268](/Users/skyefortier/xps-app/.claude/worktrees/linked-child/tests/js/lineshape_roundtrip.test.js:268) supplies only `expr: null`, so it does not establish its claimed equivalence after this change. Adding one linked, locked case **in memory** makes that test fail: Python keeps centre/amplitude/FWHM **299/10/3**, while the page correctly takes **287/50/1**. This twin is used by `autofit.parity.refit_record`; its plain-value records also discard expression metadata. Align the twin and its caller’s representation, then test locked expressions explicitly. **Needs non-physical inputs: no.** This is a parity-infrastructure defect, not an additional browser regression.

Other checks:

- The server assigns expressions to these parameters only through links. The page builder forces linked width/shape constraints. Genuine unlinked locks remain protected, and Voigt’s mix write-back guard remains intact.
- Auto-Fit and ordinary fitting share the corrected application function. “Use this solution” uses `_altPeaks` and then a server fit. Local fitting, including Batch Fit, already synchronizes linked children regardless of locks. History/restore copy stored values: new snapshots carry the correction; previously stale snapshots are not repaired by this unit.
- The measurement reproduces: **67 linked children, 12 with locks, no active-parameter differences**. All 12 locks are inactive `fixCaM` flags on GL/Voigt peaks; the nine mix differences are inactive Voigt fields. The committed-data conclusion holds.
- **70/70 tests passed** across the two relevant files using an in-memory Python import bootstrap for the read-only sandbox. **All six new tests failed against `main`**, including the alternative-preview test. The LACX case does not exercise a locked `caM`.
- No unrelated implementation changes found. No files modified.

VERDICT: NO-GO.
