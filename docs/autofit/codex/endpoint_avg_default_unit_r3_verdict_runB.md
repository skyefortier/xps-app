# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 3, RUN B (2026-09-08, reviewed at 1ccfc6d / code cc0f556)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 97,568.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_r3_review_prompt.txt
Evidence at review time: node 161 pass / 0 fail / 3 known-gap todo; browser endpoint_avg_default (7 tests — the prompt said 9, run B corrected it), find_peaks_full_window, batch_roi, manual_anchor_cc_migration: 19 passed together; full pytest on the branch worktree 770 passed, 7 skipped.
Round 3: NO-GO x2 — every round-2 disposition verified closed (undo/redo same-tab 1/3/1/3, unconditional record write, _invalidateBgCache removal ruled correct, Save Fit / legacy loaders / batch intact, engine wiring deferral accepted); NEW MAJOR (both): undo/redo stacks are global and survive tab switches, so the averaging restore wrote into whichever tab was active (apply on A at 3 -> switch to legacy B -> undo changed B 1 -> 3). MINOR (both): memo whitelist list omits ic_model_comparison.py and sparse_map.py.

**Findings**

1. **MAJOR — New cross-tab averaging corruption.** [_restoreSnapshotEndpointAvg](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:2327) writes to the active tab, but undo stacks survive tab switches and snapshots carry no tab identity. Reproduced with production functions and rendering stubs: apply on A at 3 → switch to B at 9 → undo changes B’s DOM/record to **3** → return to A → redo changes A’s DOM/record to **9**. The parent commit preserves B=9 and A=1. Scope history to its originating tab or prevent entries from crossing tab boundaries; add this regression test.

2. **MINOR — Follow-up checklist remains incomplete.** The [memo](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/docs/superpowers/plans/2026-09-03-endpoint-averaging-default.md:132) correctly adds both direct `_compute_background` calls, but its enumerated whitelist files omit `ic_model_comparison.py` and `sparse_map.py`. Both reject unknown options and need inclusion.

The same-tab apply → undo → redo → undo disposition passes, including conditional metadata mirroring and unaffected peak-only snapshots. No consumer was found that enumerates the attached array property; JSON serialization and array spread ignore it. The unconditional record assignment is correct.

Removing `_invalidateBgCache()` is correct under the accepted display contract: OFF preserves the frozen fit; ON clears `fitResult`, causing preview recomputation from the panel. Save Fit, legacy loading, and batch dispositions remain closed; engine wiring remains accepted follow-up work.

Validation: focused JavaScript tests **12/12 passed**. Full Node verification encountered sandbox temporary-file failures in Python-backed checks; browser tests were inspected, not rerun. The endpoint browser file defines **seven**, not nine, tests. Archived verdict files were not read. Actual HEAD is `1ccfc6d`, with only the review prompt added after `cc0f556`.

VERDICT: NO-GO — Round 3 introduces cross-tab undo/redo corruption of persisted endpoint averaging.
