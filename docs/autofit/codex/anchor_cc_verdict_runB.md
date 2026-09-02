# Codex adversarial review — manual-anchor cc migration (fix-manual-anchor-cc-migration) — round 1, RUN B (2026-09-02, reviewed at a324348)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 85,167.
Prompt: docs/autofit/codex/anchor_cc_review_prompt.txt
Round 1: NO-GO x2 — both runs found the same MAJOR (auto-fit failure rollback left anchors in the provisional cc frame); run A also found the .spec.json load gap.

**Findings**

1. MAJOR: Auto-fit rollback now leaves anchors in the wrong frame after a failed/discarded auto-fit. `runAutoFitC1sGraphite()` snapshots state before the provisional CC change, but `_autoFitSnapshot()` does not include `manualAnchors` ([templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6452)). The new migration mutates the live anchor objects in `updateChargeCorrection()` ([templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:4657)), then failure paths call `_autoFitRestore(snap)` ([templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6759)), which restores `ccShift`, ROI/bg fields, and peaks but not anchors ([templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6468)). Result: after backend failure, invalid result, or discard, anchors remain shifted while the spectrum returns to the old correction.

2. MINOR: The saved-file audit is overstated for `.spec.json`: `_doSaveSpectrum()` writes `manualAnchors` ([templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:8734)), but `_loadSpectrumFile()` never restores them ([templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:8962)). Project load and `.fit.json` apply do restore anchors, and I did not find a load/tab-switch double-shift path, but single-spectrum roundtrip is not actually “byte-identical” for anchors.

3. MINOR: The new Playwright tests pin the normal migration sign and composition well: `+delta` and a mutate-copy-without-assign implementation would fail ([tests/test_browser_manual_anchor_cc_migration.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/tests/test_browser_manual_anchor_cc_migration.py:169)). They do not cover auto-fit rollback or saved-file restore, which is where the remaining risk sits.

VERDICT: NO-GO — Auto-fit rollback does not restore `manualAnchors` after the new provisional CC migration, leaving anchors in the wrong corrected frame on failure.
