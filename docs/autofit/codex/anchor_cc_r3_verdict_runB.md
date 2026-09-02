# Codex adversarial review — manual-anchor cc migration (fix-manual-anchor-cc-migration) — round 3, RUN B (2026-09-02, reviewed at 07d1a53)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 105,922.
Prompt: docs/autofit/codex/anchor_cc_r3_review_prompt.txt
Round 3: GO x2 — tab-aware record-targeted restore verified; unit passes.

**Findings**

1. MINOR: `_autoFitRestore(snap, fittingTabId)` restores the fitting tab’s data/form state, but not `yZoom`; provisional `updatePlot()` can refresh `state._mainYMax` before `activateTab()` syncs the fitting tab record ([templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6695), [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:8375)). This is view-state drift, not data corruption.

2. MINOR: The new tab-switch test catches the cited bad implementations: live-state clobbering and failing to restore `ccShift`/peaks/anchors. It does not assert `fitResult`, `nextId`, or all ROI/bg UI fields, but the implementation does restore the snapshot-covered fields ([templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6487)).

3. MINOR: Hostile `manualAnchors` remain accepted verbatim in the v1 fit, `.spec.json`, and project load paths. I would keep this as pre-existing hygiene unless the project wants numeric anchor validation in this unit.

VERDICT: GO
