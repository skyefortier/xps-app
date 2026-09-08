# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 3, RUN A (2026-09-08, reviewed at 1ccfc6d / code cc0f556)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 71,848.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_r3_review_prompt.txt
Evidence at review time: node 161 pass / 0 fail / 3 known-gap todo; browser endpoint_avg_default (7 tests — the prompt said 9, run B corrected it), find_peaks_full_window, batch_roi, manual_anchor_cc_migration: 19 passed together; full pytest on the branch worktree 770 passed, 7 skipped.
Round 3: NO-GO x2 — every round-2 disposition verified closed (undo/redo same-tab 1/3/1/3, unconditional record write, _invalidateBgCache removal ruled correct, Save Fit / legacy loaders / batch intact, engine wiring deferral accepted); NEW MAJOR (both): undo/redo stacks are global and survive tab switches, so the averaging restore wrote into whichever tab was active (apply on A at 3 -> switch to legacy B -> undo changed B 1 -> 3). MINOR (both): memo whitelist list omits ic_model_comparison.py and sparse_map.py.

**Findings**

1. **MAJOR — New cross-tab undo regression.** [_restoreSnapshotEndpointAvg](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:2331) writes into whichever tab is currently active, but undo/redo stacks are global and survive tab switches. Reproduction: apply Find Peaks on A at averaging 3, switch to legacy B at 1, then undo. A source-extracted Node harness using the actual lifecycle/apply/undo functions confirms B’s DOM and record change **1 → 3**; before `cc0f556`, both stayed at 1. This newly changes another spectrum’s background setting and persists through saving. Scope history to its originating tab, or clear both stacks at appropriate tab/load boundaries; cover cross-tab undo and redo.

2. **MINOR — Follow-up checklist remains incomplete.** The [memo’s explicit whitelist list](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/docs/superpowers/plans/2026-09-03-endpoint-averaging-default.md:132) omits `ic_model_comparison.py` and `sparse_map.py`. Both reject unknown options through their own `_ALLOWED_OPTIONS`. The directory correction and both direct `_compute_background` call sites are correctly documented. Add the omitted whitelists; engine wiring can remain deferred.

The other dispositions check out:

- Same-tab apply → undo → redo → undo produces DOM/record **1/3/1/3**, with peak counts **2/1/2/1**. Interleaved peak-only snapshots discard the metadata. No inspected consumer enumerates the peaks array’s extra properties. JSON serialization and array spread ignore `_endpointAvg`; object spread would copy it.
- Apply assigns the tab record unconditionally; only the notice depends on a changed field.
- Removing `_invalidateBgCache()` is correct under the documented contract: unchecked preserves the frozen display; checked clears `fitResult`, making `updatePlot()` recompute from the panel.
- Save Fit persistence, legacy loader fallbacks, and batch propagation remain intact.

Validation: 12 focused JavaScript tests passed, plus the source-extracted behavioral checks above. The full JavaScript run encountered sandbox failures in Python-backed tests because temporary files cannot be created; browser/full pytest results were not independently rerun. No archived verdict files were read. Actual HEAD is `1ccfc6d`, whose only change after `cc0f556` is the review prompt.

VERDICT: NO-GO — Round 3 introduces cross-tab undo restoration that overwrites another spectrum’s endpoint averaging.
