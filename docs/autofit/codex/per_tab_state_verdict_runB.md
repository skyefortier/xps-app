# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 1, RUN B (2026-09-09, reviewed at 60b5278 / code 99d752e)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 102,254.
Prompt: docs/autofit/codex/per_tab_state_review_prompt.txt
Evidence at review time: node 167 pass / 0 fail / 3 known-gap todo; 26 browser tests across five files passed; the new per-tab tests were watched failing on main. Full pytest on the commit recorded in the round-2 header.
Round 1: NO-GO x2 — the record move is necessary but not sufficient: ASYNC producers still choose the tab at completion. BLOCKERs (both): runFindPeaks stores its result on the completion-time active tab and reads ROI/peak specs after the upload await; applyFindPeaks captures A's result, awaits confirmation, then writes the then-active tab. MAJORs: _autoFitRestore/runFit bind by persisted id (reopened same-id record accepts stale rollback/results) and read live inputs after upload; _pushUndoDebounced fires unbound pushUndo on whatever tab is active (clears B's redo); runPropagation fits whichever tab is active after its 20 ms yield; _loadSessionFile applies a fit file to the tab active after the file read; v1 fromJSON replaces the model without an undo transaction or clearing stale Find Peaks results; the allowlist scanner is line-formatting based (misses indented/multi-declarator/populated/ALL_CAPS/window.*/IIFE state; misses _accChemCache and xpsRefLinesPlugin) and the tests never exercise an async boundary. MINORs: _ssFiltered retains closed tab objects; Shift+Z key case (pre-existing).

**Findings**

The general ownership guarantee does not hold. The three structural JS tests pass, while an in-memory Node harness using the actual frontend functions reproduced wrong-tab Find Peaks storage, wrong-tab Apply, and cross-tab redo deletion. I did not run pytest or Playwright. The checkout differs from `99d752e` only by the review-prompt document.

1. **BLOCKER — Find Peaks still crosses tabs at both asynchronous boundaries.** In [runFindPeaks](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:14291), `_fpSetLast(...)` selects the active record **after** polling completes. Start analysis on A, close the modal, switch to B, and wait: A’s result becomes `B.findPeaks.last`. The harness confirmed this. Request assembly also reads ROI and, for least squares, peaks after awaiting A’s upload, allowing mixed-tab inputs.

   Separately, [applyFindPeaks](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:14458) captures A’s result locally, awaits confirmation, then writes into current `state`. Switching to B during that wait makes Apply install A’s peaks on B; the harness confirmed this too. The global Ctrl+K handler remains available during modals. Switching to a stack tab after Apply starts also bypasses the initial stack exclusion.

   Capture the originating **record object** before the first await, capture its request inputs together, and retain that ownership through storage and application. Moving a container onto a record does not establish ownership when the producer chooses the record at completion.

2. **MAJOR — Auto-fit’s earlier fix still accepts a different record with the same persisted ID.** [_autoFitRestore](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:6628) receives `fittingTabId`, then either looks up that ID or writes directly into active state when IDs match. Start auto-fit on A, close A, reload its saved project preserving A’s ID, and let the original request fail: rollback restores the old snapshot into the newly loaded record. Success handling and ordinary `runFit()` also compare IDs, allowing stale results to update matching peak IDs.

   This is an existing hole directly within the requested general fix. The design explicitly requires object identity for this scenario, but these consumers still use persisted identity.

3. **MAJOR — A’s debounce timer destroys B’s redo history.** [_pushUndoDebounced](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:2359) schedules unqualified `pushUndo` after 500 ms. Give B a redo entry, edit A, and switch to B before expiry. The callback snapshots B and clears `B.redoStack`; the harness produced `bUndo: 1, bRedo: 0, aUndo: 0`.

   This does not transfer A’s peak values, but it is a cross-tab history mutation. It can also create history on a freshly reloaded record. Capture the pre-edit snapshot and owner when scheduling; resolve or cancel pending work at lifecycle boundaries. The current trailing callback also snapshots the already-edited peaks.

4. **MAJOR — The structural guard does not enforce its stated inventory, and the tests permit the actual failures.** The [scanner](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/per_tab_state.test.js:39) is based on line formatting and initializer spelling. I verified that it misses:

   - Indented module declarations and additional comma-separated declarators.
   - Populated `const` objects, such as `const stash = { peaks: [] };`.
   - Mutable containers named in ALL_CAPS.
   - IIFE closure state, `window.*`, function properties, and properties added to allowlisted objects.

   It already misses `_accChemCache` on the existing two-declarator line and the populated `xpsRefLinesPlugin` object. Neither is itself a demonstrated wrong-tab restore, but they disprove complete enumeration. Allowlisting `state` and `tabManager` also permits arbitrary new content properties without any test change.

   The classifications need narrower claims: `state` is an explicit ownership exception, not a tab-independent cache; `_fpRegionsSelected` is reasonably modal-session state because opening resets it; compound markers are intentionally project-wide; `_refGlobalSel` is used only without a tab; `_historyPreview` is display-only and cleared on activation. None of those observations protects asynchronous local captures.

   The browser tests inject completed Find Peaks results synchronously and resolve confirmation immediately. They never exercise either failing boundary above. Serialization coverage saves one JSON project without populating `findPeaks`; it does not establish exclusion across all formats. Use syntax-aware inventory checks plus behavioral tests that suspend requests, confirmations, and timers across switches, closes, and reused IDs.

5. **MAJOR — Batch propagation loses its target after yielding.** [runPropagation](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:10646) correctly assigns cloned source peaks to `tgt.peaks`, then activates the target and awaits 20 ms. It subsequently obtains data and runs the local fit against whichever tab is active, without checking `tgt`. Closing the overlay with Escape permits normal tab interaction while processing continues. Later targets are also re-resolved from captured IDs, allowing replacement records to be selected.

   The source-to-target copy is intentional; the subsequent fit is not bound to that target. This existing path therefore also prevents the claimed general guarantee.

6. **MAJOR — Fit-file loading lacks an originating target, and preserves stale history.** [_loadSessionFile](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:9107) awaits file contents before `_applyFitJSON()` selects the active tab. Choosing a fit for A and switching before reading completes can apply it to B.

   Once invoked, [v1 `fromJSON`](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:3319) synchronously updates both active state and its record, but leaves undo, redo, and Find Peaks results intact. A pre-import redo can overwrite the imported peaks, and an undo can combine old peaks with newly imported charge correction/background settings. Treat import as a defined history transaction or reset the affected runtime content; preserving it unchanged is stale, not a coherent import boundary.

7. **MINOR — Closing a tab does not necessarily release its runtime history.** [_ssFiltered](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:12922) retains whole tab objects, and neither switcher close nor `closeTab()` clears those references. Opening the switcher, dismissing it, then closing tabs retains their stacks and Find Peaks payloads until the next switcher rebuild. Closing the final tab also leaves `_historyPreview` referenced.

   `MAX_UNDO` remains effectively bounded per tab through ordinary undo/redo transitions, but memory now scales with the sum of retained tabs’ peak histories and analysis results. Store switcher IDs or clear stale references; “removed from `tabs`” does not prove collectible.

8. **MINOR — Keyboard coverage misses an existing Shift+Z problem.** The [shortcut handler](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:5566) routes Ctrl/Cmd+Z and Ctrl+Y through the new per-tab functions, but Shift+Z still compares `e.key` with lowercase `'z'`; ordinary shifted letter events report `'Z'`. Normalize the key and exercise real keyboard events. This is pre-existing, rather than introduced by the stack migration.

The remaining requested traces did not expose another ownership failure:

| Path | Static assessment |
|---|---|
| Synchronous undo/redo | Reads the active record’s stack; no global fallback exists in the implementation. |
| Fit-history restore | Finds the snapshot on the active record and restores synchronously. `_historyPreview` only draws an overlay. |
| Activation/synchronization | Transfers peaks between the selected record and working state synchronously. |
| Spectrum/project/ZIP loading | Builds fresh records using explicit fields. Project loading **appends** records; it does not replace all existing tabs. Existing records retain their history. |
| `setSpectrum` / same-file reload | Creates another tab; does not replace the original object. |
| Organize Tabs | Reorders the same record references; preserves history ownership. |
| Serialization and overlays | Fit, spectrum, legacy `toJSON`, and both project formats select explicit fields. No whole-tab spread or `structuredClone` was found. JSON deep copies operate on peaks/manual anchors; batch spreads peak objects; stack serialization excludes render caches. No current path found that exports the three runtime containers. |

VERDICT: NO-GO — Asynchronous Find Peaks operations still transfer A’s content into B, and timer, loader, and fitting paths remain outside the claimed ownership construction.
