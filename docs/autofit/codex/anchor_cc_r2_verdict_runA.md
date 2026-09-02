# Codex adversarial review — manual-anchor cc migration (fix-manual-anchor-cc-migration) — round 2, RUN A (2026-09-02, reviewed at edde216)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 84,491.
Prompt: docs/autofit/codex/anchor_cc_r2_review_prompt.txt
Round 2: run A NO-GO / run B GO (stricter governs) — run A found the tab-switch-during-auto-fit restore corrupting the newly active tab (pre-existing for peaks/ccShift/DOM; anchors joined it).

**Findings**

1. MAJOR: Auto-fit rollback is still wrong if the user switches tabs while the request is in flight. At [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6744), the tab-switch discard path calls active-tab-scoped `_autoFitRestore(snap)`; `_setManualAnchors()` writes to the currently active tab, while the fitting tab’s anchors were already mutated in place by the provisional CC shift. Same-tab upload/fit/validation failures are fixed, but this path can leave the fitting tab in the provisional frame and contaminate the newly active tab.

2. MINOR: `.spec.json` restore assigns `active.manualAnchors` after `tabManager._restoreUI(active.ui)` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:8997), while `_restoreUI()` is where the manual anchor count is refreshed at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:3711). Plot/background behavior is correct because assignment happens before `updatePlot()`, but the count can be stale immediately after loading a saved manual-bg spectrum.

3. MINOR: Hostile `manualAnchors` remain verbatim-trusted in all three load paths. I would treat this as pre-existing hygiene, not newly dangerous in the security sense: bad `x`/`y` values can produce NaN/misrender/backend rejection, but anchors are not injected into HTML.

VERDICT: NO-GO — tab-switched Auto-Fit discard still restores anchors into the wrong active tab and leaves the fitting tab’s anchors in the provisional charge-correction frame.
