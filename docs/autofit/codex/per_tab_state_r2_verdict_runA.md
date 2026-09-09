# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 2, RUN A (2026-09-09, reviewed at f50c9f2 / code ba739f5)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 107,779.
Prompt: docs/autofit/codex/per_tab_state_r2_review_prompt.txt
Evidence at review time: node 172 pass / 0 fail / 3 known-gap todo; seven browser files (39 tests) passed together, exit-code gated; round-1 full suite on the parent: 815 passed / 7 skipped. Full pytest on this commit recorded in the round-3 header.
Round 2: NO-GO x2 — Find Peaks run/apply, debounce owner binding, fit-file explicit route, v1 import, switcher/preview/Shift+Z CLOSED (both). OPEN: BLOCKER auto-fit awaits its confirmation BEFORE capturing owner/snapshot (both); MAJOR both fit flows read method / averaging / anchors after the upload await (both); MAJOR the generic hasPeaks JSON branch applies a fit file without the owner guard (both); MAJOR batch resolves targets by id inside the loop after awaits (both); MAJOR scanner misses same-line second declarations, multiline declarators, parenthesised initialisers, regex literals corrupting depth (both); MAJOR a stored Find Peaks result is not recoverable — openFindPeaksModal never renders the active tab's stored result (B); MAJOR a pending debounced burst flushed after a later immediate action reorders history (A). MINORs: memo class wording for state / tabManager / _undoDebounce; _onLinkRatioInput mutates before its debounced push (pre-existing).

**Findings**

Reviewed `ba739f5`; checkout HEAD `f50c9f2` adds only the review prompt. Archived verdicts were not read. Eight targeted Node tests pass. The full Node run produced 160 passes, 12 sandbox temporary-directory failures, and 3 TODOs; browser/pytest evidence remains author-reported.

1. **BLOCKER — RESOLVED: Find Peaks run ownership.** [runFindPeaks](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:14328) captures owner and payload before upload, stores on that live object, rejects closed owners, and avoids rendering over another tab. The supplied browser test exercises completion after switching.

2. **BLOCKER — RESOLVED: Find Peaks apply ownership.** [applyFindPeaks](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:14548) captures owner/result before confirmation and checks identity after both confirmations, before any write. The first confirmation is synchronous; the subsequent guard is sufficient.

3. **BLOCKER — OPEN: Auto-fit still chooses its owner after confirmation.** At [line 6882](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:6882), confirmation precedes the snapshot and operational owner capture. Deferring confirmation on A, switching to B, then accepting deterministically snapshots B and replaces B’s peaks. The claim that the snapshot precedes the first await is false.

   **MAJOR also remains:** [manual fit](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:7071) reads method, averaging, and anchors after upload; auto-fit also reads anchors afterward. A deferred-upload reproduction sent B’s averaging/anchors with A’s spectrum, then accepted the result after returning to A. Capture the complete request before awaiting.

   The rollback helper itself correctly handles inactive owners and closed/reopened identity. Reactivation restores its record fields and DOM while retaining that record’s own undo stacks; the legacy omitted/id arguments correctly fall back to `snap.owner`.

4. **MAJOR — Ownership fix verified; separate ordering defect remains in finding 9.** Both direct calls capture **before** mutation: [_switchPeakShape](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:5125) precedes the family loop, and [updatePeakParam](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:5722) precedes assignment. Owner changes flush the previous burst, and closed owners are dropped. The stated direct-call ordering concern does not apply.

5. **MAJOR — OPEN: Batch targets remain bound by persisted id.** [runPropagation](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:10687) resolves each target inside the loop, after earlier awaits. Closing a later target and reopening its id causes propagation and its new undo entry to affect the replacement record; `_ownerLive(tgt)` then trivially accepts it. I reproduced this with controlled timers.

   The immediate 20 ms switch guard works, but target objects and source inputs must be captured before the batch’s first await. Deterministic timer tests are required here; the short window does not prevent testing it.

6. **MAJOR — OPEN: Generic fit JSON bypasses ownership checking.** The explicit `.fit.json` branch is guarded, but [the generic `hasPeaks` branch](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:9203) calls `_applyFitJSON` unconditionally. Deferring `legacy.json` reading on A and switching to B deterministically applies it to B. Guard every fit-application route. The v1 peak/averaging undo entry, redo clearing, and Find Peaks clearing are implemented.

7. **MAJOR — OPEN: Scanner coverage is still materially incomplete.** [The scanner](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:29) misses `let ROUND2_FORBIDDEN = [];` appended to **either actual inline script**. It also misses a second declaration on one line, multiline declarators, and parenthesized object initializers. Regex literals can corrupt its depth tracking. These are ordinary module declarations, beyond the documented closure limitation.

   Closure analysis may reasonably remain a manual-review obligation, but the async rule does not make this scanner complete. **MINOR documentation issue:** `state` and `tabManager` are ownership infrastructure, not tab-independent caches; `_undoDebounce` contains spectrum data despite class A’s “no spectrum content” definition. Document those exceptions explicitly.

8. **MINOR — RESOLVED: Lifecycle and shortcuts.** Switcher storage now contains ids; final close clears `_historyPreview`; key normalization handles uppercase `Z`. Serialization remains explicit across fit, spectrum, project JSON, and ZIP paths, excluding runtime histories/results. Organize Tabs preserves record identity; spectrum/project loaders construct fresh records.

9. **MAJOR — NEW: Deferred snapshots reorder undo history.** [_flushUndoDebounce](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:2403) appends the burst’s older snapshot after any intervening immediate action. Reproduction: change center 285→286, add another peak, then flush. First Undo removes the added peak **and** restores 285; second Undo changes it back to 286. Flush pending bursts before subsequent history operations and add a behavioral regression test.

VERDICT: NO-GO — Wrong-tab async paths, incomplete scanner enforcement, and a new undo-ordering regression remain.
