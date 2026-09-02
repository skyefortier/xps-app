# Codex adversarial DESIGN review — background architecture (v2) — round 2, RUN A (2026-09-02)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 190,178.
Prompt: docs/autofit/codex/bg_design_r2_review_prompt.txt
Design under review: docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md (this file records the round-2 state; the committed memo is the final v4+amendments)
Round 2: NO-GO x2 — all round-1 dispositions accepted; new specific call sites (applyAutoFitResult producer, anchor-mutation dirtying, .spec.json round-trip, cc-frame exports, JS linear narrowed-window semantics, batch shirleyIter).

**Findings**

1. MAJOR: Unit 1 still misses `applyAutoFitResult()`. It rebuilds `state.fitResult` after a successful backend auto-fit using JS `computeBackground()` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:6570). The high-level frozen-array rule covers this in spirit, but the explicit consumer sweep does not.

2. MAJOR: Manual-anchor edits are not actually all invalidation call sites. `_onBgTypeChange()` calls `_invalidateBgCache()` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:12474), but anchor undo, clear, add, and remove only call `updatePlot()` at lines 12493, 12499, 12573, and 12595. The `settingsDirty` policy must add dirtying there.

3. MAJOR: `settingsDirty` is implementable, but v2 is ambiguous about ROI. Current ROI inputs do not invalidate; they only call `updatePlot()` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:2040). If v2 really means ROI edits enter “preview/unfitted” mode, that deliberately changes the frozen-fit invariant documented at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:7964). If it only means background/CC edits, narrow the wording.

4. MAJOR: `.spec.json` reload remains outside the authority boundary. `_doSaveSpectrum()` is listed, but `_loadSpectrumFile()` currently restores only stats and `fittedY`, not `roiBE/background/bgSubtracted`, at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:9000). Future saved spectra could be internally authoritative on disk but reopen through JS recomputation.

5. MINOR: Fit-history snapshots should be named in Unit 1. `_autoSnapshot()` copies `bgIntensity/bgSubtracted/fittedY` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:12234), so it is safe only if backend arrays are already frozen correctly. The preview overlay also ignores the snapshot’s own background and uses the current `plotBG` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/templates/index.html:8089).

6. MINOR: The backend-rounded `fitResult.be/counts` rule is sound. I found no consumer that requires the frontend full-precision ROI slice; residuals, R-factor, exports, and `_peakArea()` are better aligned on backend arrays. Stack Path A should also use frozen `fr.counts` for bg-sub raw data instead of realigning full-precision `rawIntensity`.

7. MINOR: Q2’s `(lo, hi + 1)` helper is coherent for reversed inputs, outside windows, single-point windows, and ascending arrays. Keeping the fix frontend-only leaves `autofit/parity.py` and battery fixtures untouched; `autofit/parity.py` still pins the backend exclusive slice contract at [autofit/parity.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/autofit/parity.py:69).

8. MINOR: `/api/background` extraction is the right direction, but the design must explicitly choose the new response shape. It currently returns only sliced `energy/background/net_counts` and treats `manual` as zeros at [fitting.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/fitting.py:1276), while `run_fit()` embeds full-ROI backgrounds and supports manual anchors at [fitting.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-manual-anchor-cc-migration/fitting.py:1038).

VERDICT: NO-GO — Unit 1 is still under-scoped around auto-fit, manual-anchor dirtying, and saved-spectrum reload semantics.
