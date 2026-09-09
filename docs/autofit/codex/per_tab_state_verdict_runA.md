# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 1, RUN A (2026-09-09, reviewed at 60b5278 / code 99d752e)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 90,958.
Prompt: docs/autofit/codex/per_tab_state_review_prompt.txt
Evidence at review time: node 167 pass / 0 fail / 3 known-gap todo; 26 browser tests across five files passed; the new per-tab tests were watched failing on main. Full pytest on the commit recorded in the round-2 header.
Round 1: NO-GO x2 — the record move is necessary but not sufficient: ASYNC producers still choose the tab at completion. BLOCKERs (both): runFindPeaks stores its result on the completion-time active tab and reads ROI/peak specs after the upload await; applyFindPeaks captures A's result, awaits confirmation, then writes the then-active tab. MAJORs: _autoFitRestore/runFit bind by persisted id (reopened same-id record accepts stale rollback/results) and read live inputs after upload; _pushUndoDebounced fires unbound pushUndo on whatever tab is active (clears B's redo); runPropagation fits whichever tab is active after its 20 ms yield; _loadSessionFile applies a fit file to the tab active after the file read; v1 fromJSON replaces the model without an undo transaction or clearing stale Find Peaks results; the allowlist scanner is line-formatting based (misses indented/multi-declarator/populated/ALL_CAPS/window.*/IIFE state; misses _accChemCache and xpsRefLinesPlugin) and the tests never exercise an async boundary. MINORs: _ssFiltered retains closed tab objects; Shift+Z key case (pre-existing).

**Findings**

The construction is incomplete: wrong-tab restores remain reachable. I reviewed `99d752e`; the checkout’s later `60b5278` changes only documentation. Isolated Node checks using the actual function bodies reproduced the failures below. I did not run pytest or Playwright.

The restore-path audit found:

| Path | Ownership assessment |
|---|---|
| Undo/redo | Synchronously reads the active record’s stacks; ordinary tab switching is sound. |
| Fit-history restore | Resolves the snapshot from the active record before writing. `_historyPreview` only draws an overlay and is cleared on activation. |
| Find Peaks | Both production and application can cross tabs across `await` boundaries. |
| Auto-fit rollback / backend fit | Uses persisted IDs rather than record identity; close/reload defeats ownership checks. |
| Batch propagation | Initially copies explicitly from source record to target record, then resumes fitting through unguarded active state. |
| Spectrum/project/ZIP loading | Spectrum loading creates a record; project loading **appends fresh records**, remaps collisions, and restores each record’s own fields. |
| v1 fit loading | Intentionally replaces the active record’s model, but leaves its previous runtime histories/results intact. |
| Organize Tabs | Reorders existing object references; preserves ownership and history. |

Serialization currently passes static inspection. `toJSON`, `.fit.json`, `.spec.json`, and both project formats select fields explicitly; there is no whole-tab spread or `structuredClone` path. ZIP uses the same `buildTabData` serializer as project JSON. JSON deep copies cover peaks/anchors, while stack entries and reference overlays serialize selected fields. Batch’s `{...p}` copies peak fields—not tab runtime containers—although nested peak metadata remains shared.

1. **BLOCKER — Find Peaks assigns the result to the completion-time tab.**  
   [`runFindPeaks`](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:14288) calls `_fpSetLast` after upload, request, and polling awaits; that setter resolves `_activeTab()` at that moment. Start analysis on A, close the modal, switch to B, and let it finish: A’s result becomes `B.findPeaks.last`. Applying it on B now satisfies the new accessor rule while injecting A’s peaks.

   The extracted-function check reproduced exactly that: A had no result; B held A’s 285 eV peak. Additionally, ROI and least-squares peak specifications are read **after** upload, permitting an A-spectrum/B-settings request. Capture the originating record and complete request inputs before awaiting; store completion on that exact surviving record and render only for its owning session.

2. **BLOCKER — Apply retains A’s result across confirmation, then writes B.**  
   [`applyFindPeaks`](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:14457) captures `_fpLast` and `peaks`, awaits `_showFindPeaksApplyConfirmModal()`, then calls active-tab `pushUndo` and replaces `state.peaks` without checking identity. It also changes the new active tab’s averaging and provenance.

   This reproduced with a deferred confirmation: switch A→B before resolving it, and B receives A’s peaks. The UI does not establish an invariant preventing this: the global Ctrl+K/P switcher remains enabled during modals. Switching to a stack during confirmation also bypasses the initial stack exclusion. Retain and revalidate the originating record after confirmation, before any mutation. The design’s promised object-identity check is absent.

3. **MAJOR — Existing asynchronous fit paths still violate the general ownership rule.**  
   [`_autoFitRestore`](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:6628) targets `fittingTabId`. Close fitting tab A, reopen a saved project containing its ID, then allow the old request to fail: rollback writes the old snapshot into the newly loaded record. An extracted-function check confirmed this replacement. [`runFit`](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:6983) likewise accepts results based on ID equality, and both fit paths read additional live inputs after upload.

   [`runPropagation`](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:10646) initially targets `tgt`, but after its rendering delay calls `getROIData`, `runFitLocal`, and `_syncActiveToRecord` against whichever tab is active. These are pre-existing holes in the claimed general fix. Bind asynchronous operations to record objects, capture inputs consistently, and validate ownership after yields.

4. **MAJOR — The allowlist does not enforce its stated coverage.**  
   The [scanner](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/per_tab_state.test.js:40) checks formatting, not JavaScript scope. Actual scanner probes missed:

   - Indented top-level declarations.
   - Populated containers such as `const hidden = { peaks: [] };`.
   - Additional declarators such as `let state = {}, hidden = [];`.
   - Uppercase mutable containers.
   - `window.hidden`, `state.hidden`, and retained IIFE/function locals.

   There is already an unscanned populated module object, `xpsRefLinesPlugin`; its current contents are drawing methods, but adding per-tab content there would escape the guard. I found no additional hidden global peak store in the inspected IIFEs/window assignments; the asynchronous locals above already demonstrate the unguarded lifetime problem.

   `state` is an explicit working-copy exception, not genuinely tab-independent B state. `_refCompoundMarkers` and `_refGlobalSel` have defensible documented scopes. `_historyPreview` is defensible as display state. `_fpRegionsSelected` is session-transient only if that session remains bound to its owner; resetting on modal open does not enforce that. Use scope-aware parsing plus checks for persistent property stores and asynchronous ownership, with mutation tests proving forbidden examples fail.

5. **MAJOR — A’s debounce timer mutates B’s history.**  
   [`_pushUndoDebounced`](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:2359) schedules unbound `pushUndo` after 500 ms. Edit A, switch to B with a redo entry, and wait: the callback snapshots B and clears B’s redo stack. The function check produced `AUndo=0`, `BUndo=1`, `BRedo=0`.

   This does not copy A’s peaks into B, but it is a cross-tab history write and destructive redo loss. The callback also captures after the edit rather than preserving its pre-edit state. Debouncing must retain the owning record and pre-action snapshot, with explicit switch/close handling.

6. **MAJOR — Same-record model replacement leaves stale history available.**  
   [`fromJSON`’s v1 branch](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:3337) replaces peaks, charge correction, and background without recording the replacement or clearing undo, redo, and Find Peaks results. For example: create a redo entry, load a different fit, then redo—the previous model replaces the imported model; an averaging-bearing entry can also overwrite imported averaging. Batch replacement has the same missing lifecycle policy.

   Ownership remains within one object, but the history is stale rather than a coherent undoable import. Define replacement as either a complete undoable transaction or a runtime-history reset. `setSpectrum` and reloading raw/spec files create additional records, so they do not silently replace an existing object whose history should survive.

7. **MAJOR — The seven new tests can pass these wrong implementations.**  
   The [browser Find Peaks test](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/test_browser_per_tab_state.py:151) injects `_fpSetLast` synchronously and immediately approves confirmation. It tests neither asynchronous producer ownership nor switching during Apply. The JS tests merely require accessor text to appear; they do not establish that returned values exclusively determine reads and writes.

   A hidden global fallback could pass the structural checks and existing scenarios—for example, a fallback activated only when B already has a result. Serialization coverage exercises two-tab project JSON, without a populated Find Peaks result; ZIP/spec/fit exclusion is currently supported by inspection. Add delayed completion/confirmation, close-and-reopen identity, timer/redo preservation, and distinct A/B peak-content assertions. The reported passing suites and failures on main establish the original synchronous regression, not the broader invariant.

8. **MINOR — Closing a tab does not necessarily release its new histories.**  
   [`_ssFiltered`](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:12922) retains whole tab objects; closing the switcher or tabs does not clear that array. Consequently, closed records can retain undo/redo and Find Peaks payloads until another switcher render. Closing the final tab also leaves `_historyPreview` referenced.

   Normal undo/redo transfers preserve the 50-entry per-tab bound, but total memory scales with tab count and peak payload size. Clear stale UI references on lifecycle transitions. Button refreshes on activation/final close are sound; keyboard dispatch is unchanged, but the new tests do not exercise actual shortcuts.

VERDICT: NO-GO — asynchronous Find Peaks and fit operations still restore earlier content into the wrong tab, and the structural guard does not enforce the claimed ownership invariant.
