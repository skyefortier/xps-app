# Codex adversarial review — manual-anchor cc migration (fix-manual-anchor-cc-migration) — round 1, RUN A (2026-09-02, reviewed at a324348)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 98,868.
Prompt: docs/autofit/codex/anchor_cc_review_prompt.txt
Round 1: NO-GO x2 — both runs found the same MAJOR (auto-fit failure rollback left anchors in the provisional cc frame); run A also found the .spec.json load gap.

**Findings**

1. MAJOR - Auto-Fit rollback now omits state it mutates. [updateChargeCorrection](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:4657) mutates the live active tab `manualAnchors` array, but [_autoFitSnapshot](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6452) and [_autoFitRestore](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6468) do not capture/restore anchors. If Auto-Fit applies the provisional CC at [templates/index.html:6676](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6676) and then upload/fit/apply fails, rollback restores `ccShift`, ROI/bg fields, and peaks, but leaves anchors in the provisional corrected frame.

2. MAJOR - The saved-spectrum audit is false for `.spec.json`. `_doSaveSpectrum` writes `manualAnchors` at [templates/index.html:8734](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:8734), but `_loadSpectrumFile` never reads `data.manualAnchors` back around [templates/index.html:8962](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:8962). Project and v1 fit load paths do restore anchors; spectrum-file roundtrip does not.

3. MINOR - The new Playwright tests pin the direct CC convention well enough for sign, composition, and live-array mutation: `+delta` or mutating a copy would fail the assertions at [tests/test_browser_manual_anchor_cc_migration.py:177](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/tests/test_browser_manual_anchor_cc_migration.py:177) and [tests/test_browser_manual_anchor_cc_migration.py:198](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/tests/test_browser_manual_anchor_cc_migration.py:198). They do not cover load/restore or Auto-Fit rollback, which is where the regression above lives.

4. MINOR - Undo remains peak-only at [templates/index.html:2306](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:2306). This fix does not newly make normal user CC edits undoable or inconsistent, but it also means anchor migration is outside the undo model.

VERDICT: NO-GO — Auto-Fit failure rollback now leaves manual anchors in the provisional corrected frame.
