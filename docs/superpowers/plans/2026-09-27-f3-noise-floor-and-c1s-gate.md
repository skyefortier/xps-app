# F3 — the Auto-Fit C1s gate on live data; Find Peaks' noise floor (PARKED) (2026-09-27)

Branch `fix-noise-floor-scale-free`, stacked on `fix-fit-start-poll` (unit 2,
itself on F2): deploy F2 → unit 2 → F3, three fast-forwards. F3 touches
neither Run Fit nor the job path (only `isC1sTab`), so it can be rebased onto
main alone if unit 2 is held.

Owner's brief (2026-09-27): "Find Peaks' absolute 1.0-count noise floor ->
scale-free, per the design rule. Include the Auto-Fit C1s gate judging a
stale typed window." Sources: sweep M9 (first bullet) and M5
(`docs/findings/2026-09-25-fail-open-guards-sweep.md`).

## 1. Shipped: the Auto-Fit C1s gate judges the data the fit would use (M5)

| site | before | after |
|---|---|---|
| `isC1sTab(tab)` | the midpoint of `tab.ui.roiMin/roiMax` — for the ACTIVE tab a record synced only on a tab switch or save, and the TYPED values even where they reach past the data | for the active tab the live selection `getROIData()` returns (the fields clipped to the data, corrected frame); for any other record its saved window over its own corrected data; an empty selection is not C 1s; the midpoint of the SELECTED points is tested (270–315 eV, unchanged) |
| callers (`_recomputeAutoFitMenuState`, `_isChargeRefAllowed`, `runAutoFitC1sGraphite`) | — | unchanged; all three are for the active tab; the ROI fields already refresh the menu on every keystroke |

The sweep's reproduction (a wide 270–420 eV scan, the record's window on
C 1s, a U 4f window typed in the fields without a tab switch): the menu was
enabled and the gate passed, and the fit then took the U 4f₅/₂ line as
"Graphite" (the step (c) refit refused it in the page runs, but a server
construction passed every gate with a 107 eV provisional shift). Now the gate
closes. Not in scope (sweep suggestion, a threshold of its own): bounding the
provisional shift.

Tests: `tests/js/autofit_c1s_gate.test.js` (the reproduction closes; a live
C 1s selection passes; the selected data decide, not a typed window reaching
past them; an empty selection; a non-active record judged on its own
corrected data incl. a charge shift; every caller is the active tab; the ROI
fields refresh the menu).

## 2. PARKED for an owner decision: the occupancy floor (M9)

`docs/findings/noise-floor-occupancy/README.md`: two variants implemented as
patches and measured. The first draft recommended the likelihood ratio; Codex
round 1 (both runs) showed it is NOT invariant to intensity units and its
patch was inconsistent, and that the honesty failure under F comes from a
background-compensating component in a two-peak fixture. Revised
recommendation, both reviewers: F, as its own unit, with an unsupported
in-window component kept distinct from an orphan and a mismatch signal that
does not ride on that component.

## 3. Codex rounds

**Round 1 — GO ×2 for the shipped gate** (`f3_c1s_gate_verdict_run{A,B}.md`).
MINORs fixed: the record path now makes exactly getROIData()'s selection
(each bound open on its own side when blank, never reordered, the shift read
as getCorrectedBE reads it) — nonblocking, all callers pass the active tab;
the caller test now proves each caller looks the tab up by
`tabManager.activeId` and judges that tab. Three of the four gate tests fail
on the old code. The parked half's review is recorded in the findings README
(recommendation revised to F). Round 2 confirms the MINOR fixes.

**Round 2 — GO ×2** (`f3_c1s_gate_r2_verdict_run{A,B}.md`; the record path
matched getROIData() on 18 900 and 43 350 exact comparisons). MINORs fixed:
a BEHAVIOURAL caller test (each caller run with an inactive C 1s record first
and an active U 4f record; the record reaching `isC1sTab` must be the active
one — the reviewers' mutation `tabs[0] || _getTab(activeId)` now fails it);
the parked README's stale claims replaced (LR described as what it is; only F
is a ratio; F's invariance qualified by the retained Poisson variance floor).
Round 3 confirms.

**Round 3 — GO ×2** (`f3_c1s_gate_r3_verdict_run{A,B}.md`). One MINOR from
both, fixed: the behavioural caller test ran one fixture order and an
inactive id a mutation could miss (`tabs[tabs.length − 1] || …`, `tabs[1] ||
…`, `_getTab('inactive') || …` passed); it now runs both tab orders × both
inactive ids, each caught. **Ready for deploy** (GO ×2 at rounds 1–3; the
round-3 fix is test-only).

## Rebuilt onto F2 (2026-09-27, overnight)

Unit 2 (`fix-fit-start-poll`) was parked at its round-4 limit, and the
original F3 branch `fix-noise-floor-scale-free` sits on a unit-2 merge
(07e0839), so it could not deploy fast-forward without unit 2. This branch,
`fix-noise-floor-on-f2`, is F3's four commits cherry-picked onto F2
(`fix-acceptance-holes` 3d38d73) without conflicts. `git diff 07e0839
fix-noise-floor-scale-free` and `git diff fix-acceptance-holes
fix-noise-floor-on-f2` have the same patch-id (ec9694d8…): the same
changes, and no unit-2 code. The Codex verdicts (GO ×2 in rounds 1–3) were
given on those changes. The original branch is kept as is. Suite on this
branch: JS 459 tests, 457 pass, 2 todo (by design); pytest 1006 passed,
7 skipped (fewer than on the unit-2 base: unit 2's own tests are absent).
READY FOR DEPLOY (after F2).
