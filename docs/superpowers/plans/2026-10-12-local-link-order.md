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

- A link is a truthy `linked`, as every reader of the field reads it (the request builder, the
  peak controls, the engine's pass): null, false and 0 are no link.
- `linkOrder`: for a WELL-FORMED link graph (every peak found by its own id, every link naming a
  peak that is there, no cycle) the
  linked peaks sorted so each follows its parent (a fixed point over the link graph, peak order
  kept among peers); `applyParams` walks it, so one application resolves a chain in any order and
  applying the same parameters twice gives the same model, and the χ² the engine keeps is the
  committed model's.
- Any other graph — a shared or unmatchable id, a link to a missing peak, a self-link, a cycle —
  keeps main's peak-order pass EXACTLY, its old behaviour included (Codex rounds 1-3); those
  graphs are refused by Q10 0c′, not reinterpreted here.

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

## Codex round 3 (NO-GO ×2, the same finding) — fixed

A malformed graph that also held a reversed chain was still reordered: four held peaks
4 → 3 → 2 → 1 → 99 (missing), and the same chain under a root id that two peaks share. Main
committed peak 4 at 285 / 0.5, the branch at 291 / 12.5. Round 2's object tracking had kept every
peak but still reinterpreted these graphs. Now only a well-formed graph (unique ids, every parent
present, no cycle) is reordered; anything else walks main's peak-order list unchanged. Both
reproducers and a reversed chain hanging off a cycle are added to the main-vs-branch comparison,
which fails on b6d0f2c. Identity re-run: 121 / 121. Both runs otherwise confirmed the valid-graph
order (2 000 shuffled forests against a recursive oracle; already-ordered forests match the
legacy pass; a 1 000-peak reversed chain), the consumers and the identity.

## Codex round 4 (NO-GO ×2) — one fixed, one answered by the field's reading

- **An id the lookup cannot match** (a lone peak with id NaN; strict equality never finds it)
  passed the uniqueness test, so its chain was reordered, its committed values never written and
  the χ² kept described other peaks. The test is now "every peak is found by its own id"
  (`workPeak(q.id) === q`), which also covers shared ids and 0 / −0. Added to the main-vs-branch
  comparison (fails on d37cdd9).
- **A link value of 0, −0 or NaN** above a reversed chain: both runs counted it a link to a
  missing peak, so the chain below should keep main's order. It is NOT a link to any reader of the
  field — the request builder sends no constraint for it (`if (p.linked)`), the peak controls show
  the peak as independent, main's own pass skips it (`if (!q.linked) continue`) — so the graph is
  a valid reversed chain, and main's result for it (the leaf at 285 / 0.5 instead of
  285 + 2 + 2 + 2 = 291 / 12.5) is the defect this unit fixes. One reading of the field
  (CLAUDE.md "Two readings of one field"); 0c′'s check reads it the same way. A new test pins it:
  the chain under a root linked to undefined / false / 0 / −0 commits exactly what it commits under
  null. (A saved file cannot carry NaN or "" — the loader refuses them.)
- Identity re-run: 121 / 121. Both runs otherwise confirmed the valid-graph order (2 000 shuffled
  forests), the 12 000 malformed variants that kept the legacy pass, the consumers and the
  identity.

## Codex round 5 (GO ×2) — no findings

Both runs: no BLOCKER, MAJOR or MINOR. The guard matches the engine's strict-equality lookup;
shared ids (incl. 0 / −0), an unmatchable NaN id, missing parents, self-links and cycles keep
main's pass; the falsy-link reading is supported (builder, controls and pass all read
truthiness). Adversarial checks: 18 001 and 126 417 graph cases (valid graphs against a recursive
oracle and idempotent; malformed graphs keeping the legacy order). Identity 121 / 121 reproduced.
The main-vs-branch comparison catches each earlier round's defect (39d04d6, b6d0f2c, d37cdd9).
