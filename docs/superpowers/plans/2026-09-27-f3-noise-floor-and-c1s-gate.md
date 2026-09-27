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

`docs/findings/noise-floor-occupancy/README.md`: both scale-free variants
implemented as patches and measured (the server's support F test breaks the
background-mismatch honesty case; a Poisson likelihood ratio passes every
gated and always-on suite). Recommendation: the likelihood ratio.

## 3. Codex rounds

(filled in as they run)
