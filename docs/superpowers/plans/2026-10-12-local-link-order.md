# Q10 0b — the local engine resolves links in dependency order (owner, 2026-10-11)

Owner: "Q10: yes to all three, each its own small unit, BEFORE any seal build … measured,
Codex x2." This is the first: found by the sealed-fit v6 design gate (round 2, both runs).

## The defect

`runFitLocal`'s `applyParams` set every free parameter, then made each linked peak follow its
parent in ONE pass in peak order. A linked peak whose parent is itself linked and is listed AFTER
it read that parent's PREVIOUS values, so one application resolved only one more level of a
reversed chain. The engine keeps the χ² of an earlier application and commits a later one: its
χ² could describe another model than the peaks it commits (the gate's probes: an all-held chain
grandchild → child → root reported χ² 2237.98 against 2620.21 for the committed peaks; another
136.72 against 0.52). Ordinary doublets (one parent, one child) were never affected: the parent's
own values are set before the link pass.

## The fix

- `linkOrder`: the linked peaks sorted so each follows its parent (a fixed point over the link
  graph, peak order kept among peers); `applyParams` walks it, so one application resolves a chain
  in any order and applying the same parameters twice gives the same model. A peak whose parent is
  missing is skipped as before; a cycle keeps its peak order (graph validation is Q10 0c′).
- For a valid (acyclic) link graph one application is idempotent, so the χ² the engine keeps is
  the committed model's. A cycle or a self-link keeps its peak order and its old, non-idempotent
  behaviour unchanged (Codex round 1: an extra final χ² evaluation, tried first, changed what such
  an invalid graph committed — removed); those graphs are refused by Q10 0c′.

## Measured

- Committed models: 121 tabs with peaks, 57 with links, NONE with a chain two levels deep
  (`scripts/local_link_order_identity.js`; its census in this plan's measurement).
- Main vs this branch, the local engine on every committed tab (its own spectrum, saved peaks as
  start, saved background): 121 of 121 BIT-IDENTICAL — committed peaks, χ², χ²ᵣ, RMSE,
  iterations (`docs/findings/local-link-order/identity.json`). No committed fit changes.

## Tests

`tests/js/local_lm_descent.test.js`: a reversed three-level chain (all held, and with the root
amplitude free) and a four-level reversed chain with nothing free — every linked peak follows its
parent exactly, and the χ² kept equals the committed model's in the engine's own arithmetic. The
four-level case fails with the peak-order pass restored.

## Codex round 1 (NO-GO ×2, the same finding) — fixed

The final χ² evaluation added one more link pass, which changed what an INVALID graph (a
self-link, a cycle — finite numbers, an inconsistent graph) committed: centre 287 → 288. For
valid graphs it was redundant. Removed; the guarantee is stated for acyclic graphs; the identity
script compares numbers with `Object.is` (JSON equality would miss −0 / 0). Both runs otherwise
confirmed the dependency order (28 803 graph / order / idempotence checks incl. 1 000-peak
reversed chains, mixed id types), the other consumers, the 121 / 121 identity and the four-level
test.

## Codex round 2 (NO-GO ×2, the same finding) — fixed

The order tracked peaks by ID, so with DUPLICATE ids (a project load accepts them) a second
child sharing an id was left out of the pass and its link never applied: main committed the
first id-2 child at centre 288 / 289 and amplitude 25, the branch at its start values 281 / 2.
The order now tracks peak OBJECTS and finds each parent exactly as `applyParams` does (the first
peak with that id), so every linked peak is applied once per pass, in main's order whenever no
chain needs reordering. Regression: duplicate ids (held, and with a free root), a self-link and a
two-peak cycle run through main's `runFitLocal` (read from git at 8cc3750) beside the branch's
and must commit the same peaks and the same χ² (`Object.is`); it fails with the id-tracked order
restored. Identity re-run: 121 / 121. Both runs otherwise confirmed the order (2 000 shuffled
forests against a recursive oracle, 1 000-peak reversed chains), the consumers and the identity.
