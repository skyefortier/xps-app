# Design memo — Per-tab state ownership: make wrong-tab restore impossible by construction

Status: IMPLEMENTED 2026-09-09 on branch feature-per-tab-state (see 'Migration' — done as written; the runtime-token guard deleted). Owner's framing (2026-09-08): the undo
stack restoring one tab's peaks into another is the SECOND instance of
global state being restored into the wrong tab (the first was the auto-fit
rollback, fixed 2026-09-02 by a tab-aware restore); two instances is a
pattern in per-tab state management, and the fix must be the general one,
not another patch on the undo stack — the same reasoning as the
`dataclasses.fields` guard and the `evalPeak` caller guard.

## The pattern, with three instances

Module-level mutable state in `templates/index.html` holds content that
belongs to ONE spectrum tab, and a later consumer applies it to whichever
tab is active at that moment.

| # | Global holder | Content | Consumer that assumed "still the same tab" | Status |
|---|---|---|---|---|
| 1 | auto-fit snapshot (`_autoFitSnapshot` local) | peaks, ccShift, ui, anchors | `_autoFitRestore` wrote into live state/DOM after a mid-flight tab switch | fixed 2026-09-02 (record-targeted restore) |
| 2 | `undoStack` / `redoStack` (index.html ~2310) | deep copies of `state.peaks` | `undo()` / `redo()` assign `state.peaks` on the active tab; stacks are never cleared on tab switch or close | OPEN — silently replaces a student's peak list |
| 3 | `_fpLast` (index.html ~13230) | Find Peaks result peaks + method/regions | `applyFindPeaks` writes `state.peaks` on the active tab; `_fpLast` is never cleared, so reopening the modal on another tab and pressing Apply injects the first tab's peaks | OPEN — same class |

The averaging-undo fix in the default-3 unit (2026-09-08) had to invent a
runtime tab token to make ONE field of the undo entry tab-safe; that is the
tell that the container itself is in the wrong place.

The counter-example already in the codebase: fit-history snapshots live ON
the tab record (`tab.snapshots`, `_autoSnapshot`), so a history restore
cannot cross tabs by construction. That is the model.

## Inventory of module-level mutable state (2026-09-08, main)

Classified by what it holds. Only class C can cause wrong-tab restore.

| Class | Meaning | Members |
|---|---|---|
| A — UI-transient | mode/handle for an interaction in progress; no spectrum content | `placeMode`, `_pendingMultipletPreset`, `_dragZoomEnabled`, `_saveMode`, `_bgSubFitInFlight`, `_autoFitConfirmResolver`, `_findPeaksApplyConfirmResolver`, `_undoDebounceTimer`, `_fpModalDrag`, `_refPaletteDrag`, `_refChipOpen*`, `_ssFocusIdx`, `_ssFiltered`, `_snapshotSuppressed` |
| B — tab-independent cache / catalogue | server payloads, palettes, counters | `_fpMeta`, `_refPayload`, `_refError`, `_refFetchPromise`, `_refSearchElements`, `_refNotesOpen`, `_accSurveyCache`, `_accChemCache`, `_nextStackNum`, `_refCompoundMarkerNextId`, `_tabRuntimeTokens` |
| B′ — chart-instance state | belongs to the chart object, reset on activation | `_origYMax/_origXMin/_origXMax/_origResidY*`, `_historyPreview` (cleared in `activateTab`) |
| **C — per-tab content held globally** | **spectrum-specific data consumed on "the active tab"** | **`undoStack`, `redoStack`, `_fpLast`**. Checked and NOT class C: `_fpRegionsSelected` + `_fpExpandedElement` are reset every time the modal opens (class A, one modal session); `_refCompoundMarkers` is a deliberately project-level overlay, serialized and restored with the project (class B, annotate); `_refGlobalSel` is the documented no-tab fallback (class B, annotate) |

`state` itself is the designed exception: it is the ACTIVE tab's working
copy, swapped wholesale by `activateTab` / `_syncActiveToRecord`. Anything
that must survive a tab switch and be reapplied later must therefore live
on the tab record, never beside `state`.

## The construction rule

1. **Per-tab content lives on the tab record.** `tab.undoStack`,
   `tab.redoStack`, `tab.findPeaks` (last result + selection). They are
   runtime-only (underscore-free names are fine; the serializers list
   fields explicitly and will not pick them up — verify with the
   round-trip tests). Closing a tab drops them with it; loading a project
   creates fresh empty ones. Cross-tab restore then has no path: `undo()`
   reads `_activeTab().undoStack`, and there is no other stack.
2. **One accessor.** `_activeTab()` (= `tabManager._getTab(tabManager.activeId)`,
   null when none) is the only way a consumer reaches per-tab runtime
   state; consumers that need the tab a result was produced for keep the
   tab OBJECT (not its id — ids are reused after project reload, see the
   default-3 round-4 finding) and compare by identity, or store the result
   on that object.
3. **Module scope holds only classes A, B, B′.** Enforced by a structural
   test: every module-level `let`/`var`/`const`-container declaration in
   `templates/index.html` must appear in an allowlist with its class; a
   new global that is not allowlisted fails the test, and the allowlist
   comment for class C is "not allowed — put it on the tab record". Same
   mechanism as `tests/js/lineshape_parity.test.js` (C) for `evalPeak`
   callers and the dirty-funnel guard in the sealed-fit-record memo.
4. **Stack tabs** have no peaks; `undo`/`redo`/`applyFindPeaks` are no-ops
   when `_activeTab()` is null or a stack tab (today they would write into
   `state.peaks` of a stack tab).

## Rule 2 — async ownership (added 2026-09-09 after Codex round 1 of the implementation)

Moving the containers onto the record was necessary but not sufficient:
every producer that awaits (a fit, an analysis, a confirmation modal, a
file read, a debounce timer, a batch yield) was choosing the tab at
COMPLETION time. So: an operation that awaits captures the record OBJECT
it started on (`_opOwner()`) and every input it needs, before its first
await; afterwards it writes to that object (`_fpSetLast(last, owner)`,
`_autoFitRestore(snap, owner)`, `_pushUndoFor(tab)`) or checks that it is
still the active one (`_ownerActive(owner)`), and drops the work if the
owner was closed (`_ownerLive`). Persisted ids are not identity: a closed
tab's id returns on a NEW object after a project reload. Sites covered:
`runFindPeaks`, `applyFindPeaks`, `runFit`, `runAutoFitC1sGraphite`
(owner captured before its confirmation await), `runPropagation`
(targets resolved to objects before the first yield, re-validated after
it), `_loadSessionFile` (both fit-file routes), `_pushUndoDebounced`
(owner + pre-edit snapshot bound at burst start; immediate history
actions flush a pending burst first so order is preserved), and the v1
`fromJSON` import (an undoable transaction that clears a stale Find
Peaks result). A stored Find Peaks result is shown again when its tab
reopens the modal.

Classification note: `state` and `tabManager` are ownership
INFRASTRUCTURE (the active working copy and the record store), not
tab-independent caches; `_undoDebounce` is a burst buffer that does hold
a peaks snapshot but is bound to its owner record — the one deliberate
exception to class A's "no spectrum content". The scanner
(`tests/js/lib/module_state_scan.js`) parses each inline script with a
real parser (acorn, vendored under `tests/js/lib/` with its MIT licence;
the one Jinja interpolation is substituted first) and reports every
binding reachable without crossing a function boundary — destructuring,
labelled, unbraced-if, top-level blocks, class static state (any key
form; class declarations and expressions wherever they appear, including
an inline superclass whose static state is attributed to the subclass;
a static block is reported as a whole because its assignments cannot be
enumerated; an unbound class expression with static state reports as
'[anonymous class]', which cannot be allowlisted),
`window.*` stores — skipping a `const` only when it is a plain identifier
whose initialiser is provably not a container; destructuring patterns are
always reported. The allowlist check is an own-property lookup with a
validated class value, so an inherited name (`constructor`, `toString`)
cannot pass unclassified. Codex rounds 2–4 found a new declaration form
each round while the scanner was regex-based; the parser closes that
class. What remains a documented MANUAL-REVIEW boundary, outside any
declaration guard: closure state inside an IIFE or a long-lived function;
properties added at runtime to an allowlisted object (`state.x = []`,
`tabManager.x = []`); code produced by `eval` / `Function`; storage
exposed through prototype getters. Rule 2 (async ownership) is what
covers the first of these in practice; the others are reviewed by hand.

## Migration (one branch, TDD, Codex ×2)

- `pushUndo` / `undo` / `redo` / `_updateUndoButtons` → operate on
  `_activeTab().undoStack|redoStack`; `activateTab` refreshes the undo
  buttons from the incoming tab; `MAX_UNDO` per tab. The averaging
  metadata from the default-3 unit stays (an entry may still carry the
  pre-action averaging); the runtime-token guard becomes redundant but
  harmless — delete it once the per-tab stacks are in, to keep one
  mechanism.
- `_fpLast` → `tab.findPeaks = { last }` (the region selection is reset on
  every modal open and stays module-level, class A); the
  modal reads the active tab's; `applyFindPeaks` refuses (notice) if the
  result's tab object is not the active one (belt-and-braces: with the
  result stored ON the tab this cannot happen, so the check is a
  structural assertion, not a code path).
- `_refGlobalSel` and `_refCompoundMarkers`: keep; allowlist annotations
  (no-tab fallback; project-level overlay serialized with the project).

## Tests

- Browser: peaks edited on A, switch to B, undo → B unchanged and A's
  undo still available when A is re-activated; redo likewise; Find Peaks
  result produced on A cannot be applied on B (the modal on B shows no
  result); closing A drops its stacks; project reload starts with empty
  stacks; stack tab active → undo/redo/apply are no-ops.
- Structural (node): allowlisted module-level mutable state; `undo`/`redo`
  reference `_activeTab()` and no module-level `undoStack` exists.
- Existing default-3 tests keep passing (averaging undo semantics
  unchanged from the user's point of view).

## Not in scope

`state` swap mechanics, the sealed-fit-record seal (1a/1b/1d), and the
dirty funnel; this memo only moves class-C containers onto the record and
adds the guard that stops new ones appearing.
