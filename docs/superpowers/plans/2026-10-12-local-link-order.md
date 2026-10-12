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
- Finalisation on one frozen model: χ² is taken once more at the final point, from the model
  committed. Given the dependency order this equals the kept χ² (a guarantee, not separately
  testable: no mutation of it alone can fail).

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
