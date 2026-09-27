OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e229-a474-7a52-947e-f47235a62a30
--------
user
Re-review unit F3 (the Auto-Fit C1s gate on live data), round 2: branch fix-noise-floor-scale-free. Round 1 was GO x2 (docs/autofit/codex/f3_c1s_gate_verdict_run{A,B}.md) with two MINORs on the shipped change, fixed in the latest non-merge commit: (1) isC1sTab's record path now makes exactly getROIData()'s selection (each bound open on its own side when blank, never reordered — min > max selects nothing — inclusive, corrected frame, the shift read as getCorrectedBE reads state.ccShift); (2) the caller test now proves each caller looks the tab up by tabManager.activeId and judges that tab. The parked half's write-up (docs/findings/noise-floor-occupancy/README.md) was revised after your round-1 review: the LR recommendation is withdrawn, F is recommended with the two follow-ups you named. Review git diff 895f323..HEAD for the round-1 fixes (ignore any merge of fix-fit-start-poll: those are unit 2's changes, reviewed separately), and git diff 07e0839..HEAD minus unit-2 merges for the whole unit. Plan: docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

TRY TO BREAK
a. The record path vs getROIData()/getCorrectedBE(): every input (blank / NaN / reversed / equal bounds, Infinity or NaN ccShift, an empty rawBE); performance on a long record.
b. The strengthened caller test: would it catch a caller judging an inactive record?
c. The revised parked write-up: does it now state the evidence and your round-1 findings correctly; is the recommendation sound.
d. Anything round 1 verified that these changes touched.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll compare the fixes with the live ROI code, challenge the caller test, and check the revised write-up against round 1’s findings. I’ll keep the review read-only and finish with a verdict.

exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g '*f3*' -g '*c1s*' -g '*C1s*' -g '*noise*' docs . | head -100" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-2.md
docs/superpowers/plans/2026-04-23-c1s-charge-reference-marker-phase1.md
docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md
docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md
docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md
docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md
docs/autofit/inventory/replicate_noise_survey.json
./scripts/run_c1s_full_calibration.py
./scripts/measure_replicate_noise.py
./scripts/gen_c1s_battery_fixture.py
./autofit/noise.py
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-fixes.md
./autofit/regions/c1s.py
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-followup-2.md
./docs/superpowers/plans/2026-04-23-c1s-charge-reference-marker-phase1.md
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite-implementation.md
./docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md
./docs/superpowers/plans/2026-04-24-auto-fit-c1s-graphite.md
./docs/autofit/inventory/replicate_noise_survey.json
./tests/autofit/test_noise_model.py
./tests/js/autofit_c1s_gate.test.js
./tests/autofit/fixtures/c1s_battery_expected.json
./tests/autofit/test_c1s_parity_gate.py
./tests/autofit/test_c1s_mixed_material_class.py
./tests/autofit/test_c1s_parity_battery.py
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A/C1s Scan.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 B/C1s Scan.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/3 BN-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/9 B4C-graphite 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 F/C1s Scan.xml
docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 F/C1s Scan.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_8.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_0.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_1.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_3.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/2 B4C-graphite 50%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_7.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_5.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.xml
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_4.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_2.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.VGD
docs/autofit/test_data/5 B4C-BN-graphite 33%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/C1s Scan_6.xml

exec
/bin/zsh -lc 'git status --short; git log --oneline -14; git diff --stat 895f323..HEAD; git diff --stat 07e0839..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 31ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OtU8qeLa' (errno=Operation not permitted)
 CLAUDE.md                                          |    6 +-
 docs/autofit/codex/f3_c1s_gate_recheck_prompt.txt  |    9 +
 docs/autofit/codex/f3_c1s_gate_review_prompt.txt   |   11 +
 docs/autofit/codex/f3_c1s_gate_verdict_runA.md     | 5203 ++++++++++++++++++++
 docs/autofit/codex/f3_c1s_gate_verdict_runB.md     | 4440 +++++++++++++++++
 docs/findings/noise-floor-occupancy/README.md      |  108 +
 .../variant_F_support_test.patch                   |  197 +
 .../variant_LR_likelihood_ratio.patch              |  201 +
 .../2026-09-27-f3-noise-floor-and-c1s-gate.md      |   54 +
 templates/index.html                               |   38 +-
 tests/js/autofit_c1s_gate.test.js                  |   80 +
 11 files changed, 10333 insertions(+), 14 deletions(-)

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md; do if test -f "$p"; then cat "$p"; fi; done; rg --files -g AGENTS.md -g package.json -g '"'*test*' tests/js | head -60; cat docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md; cat docs/findings/noise-floor-occupancy/README.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
tests/js/batch_propagation.test.js
tests/js/fit_acceptance.test.js
tests/js/local_lm_descent.test.js
tests/js/fp_material_mixed.test.js
tests/js/bg_window_indices.test.js
tests/js/find_peaks_periodic_table.test.js
tests/js/shape_switch_roundtrip.test.js
tests/js/unsupported_components.test.js
tests/js/find_peaks_progress.test.js
tests/js/find_peaks_coverage.test.js
tests/js/ref_core.test.js
tests/js/endpoint_avg_default.test.js
tests/js/tougaard_twin.test.js
tests/js/stale_statistics.test.js
tests/js/module_state_scan.test.js
tests/js/per_tab_state.test.js
tests/js/fit_start_poll.test.js
tests/js/find_peaks_plain_message.test.js
tests/js/scattered_starts.test.js
tests/js/find_peaks_endpoint_avg.test.js
tests/js/lineshape_roundtrip.test.js
tests/js/fp_experimental_notice.test.js
tests/js/autofit_c1s_gate.test.js
tests/js/lineshape_parity.test.js
tests/js/autofit_required.test.js
tests/js/roi_clamp_centre_warning.test.js
tests/js/autofit_zero_graphite.test.js
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
# Find Peaks' 1-count occupancy floor → scale-free: PARKED for an owner decision (2026-09-27)

Part of unit F3 (sweep M9, first bullet). The other half of F3 — the Auto-Fit
C1s gate judging a stale typed window (sweep M5) — ships on its own in
`fix-noise-floor-scale-free` and does not depend on this.

## What was found

`noise_floor` (default 1.0, never sent by the page) does two jobs in
`autofit/`:

1. a Poisson variance floor, `sigma = sqrt(max(y, noise_floor))` — the
   counting convention the server's weights use; not a decision threshold,
   left as is by both variants;
2. an OCCUPANCY threshold, `amplitude > noise_floor` — whether a fitted
   component occupies its slot (`match_components_to_slots`), whether a
   proposed slot survives (`_evaluate_proposal`), the detectability status
   (`build_confidence_vector`). A slot is "occupied" at amplitude 1.5 and not
   at 0.5 whatever the data's scale; persistence, the absent-slot test and the
   stability gate follow from it. This is the design rule's case.

Both variants replace (2) with a statistic on the component's own fit
(computed once when the component is extracted from its lmfit result and
carried on `FittedComponent.support`), leave (1) alone, and fall back to
`amplitude > 0` (a sign test) for a component with no fit behind it. They
differ in ONE line — what "occupied" means:

| variant | occupied when | patch |
|---|---|---|
| **F** — the server's support test | `fitting._component_support` "supported": Δχ² > 0 and F = (Δχ²/p) / (χ²_with/dof) ≥ 10 — the step (b) "not supported by the data" statistic and threshold | `variant_F_support_test.patch` |
| **LR** — Poisson likelihood ratio | Δχ²/p ≥ 10 on the Poisson-weighted χ², NOT divided by the fit's own misfit χ²_with/dof | `variant_LR_likelihood_ratio.patch` |

Both are scale-free (the weights make χ² dimensionless) and carry no tolerance.

## The evidence

| suite | baseline (today) | F | LR |
|---|---|---|---|
| gated real-data parity gates + stress honesty (`RUN_AUTOFIT_GATE=1`: C 1s parity, Bayesian real, candidate-pool real, U 4f unresolved, stress honesty) | 17 passed, 4 skipped | **16 passed, 1 FAILED** | 17 passed, 4 skipped |
| always-on `tests/autofit` (incl. the C 1s / region parity batteries) | green | **1 failed** (the same stress case), 556 passed | 557 passed, 7 skipped |

The failing case, `test_stress_honesty.py::test_bg_mismatch_surfaces_loudly`:
a Shirley-shaped truth fitted with a straight-line background, χ²ᵣ ≈ 280–470
for every candidate. The test requires the mismatch to be machine-visible
("conditional" tier), never a clean confident result. Today the 3-component
candidate P3 is stable but violates plausibility, enters the conditional
pool, and its bound-fixed refit wins via the decisive override →
`conditional: true`. Under F, P3's third component has F < 10 BECAUSE the fit
is so bad: F divides the gain by χ²_with/dof ≈ 284, so a component that
removes a large χ² still reads "unsupported"; it becomes an orphan, P3's
persistence drops to 0, P3 leaves the conditional pool, and P2 (χ²ᵣ 309) is
returned as a CLEAN survivor. Under LR the same component is occupied (its
gain per parameter is far above 10 Poisson units) and the result is
conditional, as today.

## Codex review of this write-up (F3 round 1, `f3_c1s_gate_verdict_run{A,B}.md`) — the recommendation below replaces the first draft's

Both runs reproduced the measurements and the mechanism (P3's third component:
Δχ² ≈ 10 702, F ≈ 9.42 with four free parameters → persistence 0, orphan rate 1,
out of the decisive-override pool). They also found three things wrong with
the first draft's recommendation of LR, all of which hold:

1. **LR is not scale-free.** "Dimensionless" is not "invariant under a change
   of intensity units": with Poisson weights the gain Δχ² scales with the
   counts, so multiplying a spectrum by 0.1 (CPS instead of counts, a
   normalisation) turned Δχ²/p = 32 into 3.2 and flipped the verdict, while F
   stayed at 16 — F is a RATIO of two χ² quantities and is invariant. The
   design rule asks for exactly that invariance. (The statistic is also a
   gain with the other components held fixed, not a refitted likelihood
   ratio; the draft's name overstated it.)
2. **The LR patch is internally inconsistent**: occupancy used Δχ²/p while
   detectability still used `support.supported` and reported
   `basis: support_f_test`, so a component could be "unoccupied" and
   `above_floor` at once, and a proposal rejection could print "F = 32.00 < 10".
3. **The stress case does not show F rejecting a real peak.** The fixture
   (`tests/autofit/stress_cases.py`) has TWO true peaks; P3's third component
   compensates for the wrong background. F calls it unsupported — defensibly —
   and the honesty flag then disappears because the "conditional" tier
   depended on keeping that background-compensating component. The F result
   also still carries `filtered_dominant_alternative` (P3, ΔBIC ≈ 153), which
   the page shows: not a silent clean answer.

Both runs, independently: **start from F** (one support definition across
the app, invariant to intensity units) and fix two things around it before
shipping:

- an unsupported component INSIDE its slot's window must not become an
  "orphan" (an unexplained extra peak) — today (and in both patches) a
  component that fails occupancy has no accepting slot and counts toward
  `orphan_rate`, a plausibility violation; "slot empty" and "peak nobody
  expects" need distinct treatment;
- the model-mismatch honesty signal must not depend on a component that only
  compensates for a wrong background — report the mismatch (χ²ᵣ ≫ 1, the
  residual structure) on its own terms.

## The decision (owner)

- **Adopt F as the occupancy statistic** (recommended, both reviewers), as a
  unit of its own with the two follow-ups above, measured on the gated and
  always-on suites; the honesty test is then re-examined against a
  mismatch signal that does not ride on P3.
- **LR**: withdrawn as a recommendation (not invariant to intensity units).
- Either way `noise_floor` survives only as the Poisson variance floor (both
  patches leave it; it keeps the raw-count assumption the server's weights
  make, which a unit change would also move).

The two patches stay here as the measured starting points:
`git apply docs/findings/noise-floor-occupancy/variant_F_support_test.patch`.

exec
/bin/zsh -lc "git diff 895f323..HEAD -- templates/index.html tests/js/autofit_c1s_gate.test.js docs/findings/noise-floor-occupancy/README.md; git diff 07e0839..HEAD -- templates/index.html tests/js/autofit_c1s_gate.test.js CLAUDE.md; rg -n 'MINOR|MAJOR|BLOCKER|VERDICT:|recommend|follow.up' docs/autofit/codex/f3_c1s_gate_verdict_runA.md docs/autofit/codex/f3_c1s_gate_verdict_runB.md | tail -70" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fZCcRLmw' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1FN8LvCW' (errno=Operation not permitted)
diff --git a/docs/findings/noise-floor-occupancy/README.md b/docs/findings/noise-floor-occupancy/README.md
index ea03259..d558c32 100644
--- a/docs/findings/noise-floor-occupancy/README.md
+++ b/docs/findings/noise-floor-occupancy/README.md
@@ -53,26 +53,56 @@ returned as a CLEAN survivor. Under LR the same component is occupied (its
 gain per parameter is far above 10 Poisson units) and the result is
 conditional, as today.
 
+## Codex review of this write-up (F3 round 1, `f3_c1s_gate_verdict_run{A,B}.md`) — the recommendation below replaces the first draft's
+
+Both runs reproduced the measurements and the mechanism (P3's third component:
+Δχ² ≈ 10 702, F ≈ 9.42 with four free parameters → persistence 0, orphan rate 1,
+out of the decisive-override pool). They also found three things wrong with
+the first draft's recommendation of LR, all of which hold:
+
+1. **LR is not scale-free.** "Dimensionless" is not "invariant under a change
+   of intensity units": with Poisson weights the gain Δχ² scales with the
+   counts, so multiplying a spectrum by 0.1 (CPS instead of counts, a
+   normalisation) turned Δχ²/p = 32 into 3.2 and flipped the verdict, while F
+   stayed at 16 — F is a RATIO of two χ² quantities and is invariant. The
+   design rule asks for exactly that invariance. (The statistic is also a
+   gain with the other components held fixed, not a refitted likelihood
+   ratio; the draft's name overstated it.)
+2. **The LR patch is internally inconsistent**: occupancy used Δχ²/p while
+   detectability still used `support.supported` and reported
+   `basis: support_f_test`, so a component could be "unoccupied" and
+   `above_floor` at once, and a proposal rejection could print "F = 32.00 < 10".
+3. **The stress case does not show F rejecting a real peak.** The fixture
+   (`tests/autofit/stress_cases.py`) has TWO true peaks; P3's third component
+   compensates for the wrong background. F calls it unsupported — defensibly —
+   and the honesty flag then disappears because the "conditional" tier
+   depended on keeping that background-compensating component. The F result
+   also still carries `filtered_dominant_alternative` (P3, ΔBIC ≈ 153), which
+   the page shows: not a silent clean answer.
+
+Both runs, independently: **start from F** (one support definition across
+the app, invariant to intensity units) and fix two things around it before
+shipping:
+
+- an unsupported component INSIDE its slot's window must not become an
+  "orphan" (an unexplained extra peak) — today (and in both patches) a
+  component that fails occupancy has no accepting slot and counts toward
+  `orphan_rate`, a plausibility violation; "slot empty" and "peak nobody
+  expects" need distinct treatment;
+- the model-mismatch honesty signal must not depend on a component that only
+  compensates for a wrong background — report the mismatch (χ²ᵣ ≫ 1, the
+  residual structure) on its own terms.
+
 ## The decision (owner)
 
-- **F** keeps ONE definition of "supported" across the app (Find Peaks would
-  judge components exactly as Run Fit's "not supported by the data" does), but
-  in a grossly mis-modelled fit it declares real components absent and can
-  turn an honest "conditional" answer into a clean one.
-- **LR** keeps today's behaviour on every gate and the honesty case; its
-  statistic differs from the server's support verdict, so after "Apply" a
-  component Find Peaks counted as occupied could still read "not supported"
-  in Run Fit's results on a very badly fitted model (the two agree whenever
-  χ²ᵣ ≈ 1).
-
-**Recommendation: LR.** Occupancy asks "did the fit put something real
-here", which is a question about the signal against counting noise, not
-against the model's own misfit; normalising by the misfit makes the answer
-depend on how wrong the rest of the model is, which is exactly what the
-honesty tier exists to report. Measured: LR changes nothing on any gate; F
-breaks the honesty contract.
-
-To apply the chosen variant: `git apply docs/findings/noise-floor-occupancy/variant_<X>.patch`
-on this branch, then the full suite, the gated suite (`RUN_AUTOFIT_GATE=1`)
-and Codex ×2. The `test_methods_seam` detectability assertion and the schema
-round-trip fixture already accept both variants' status strings.
+- **Adopt F as the occupancy statistic** (recommended, both reviewers), as a
+  unit of its own with the two follow-ups above, measured on the gated and
+  always-on suites; the honesty test is then re-examined against a
+  mismatch signal that does not ride on P3.
+- **LR**: withdrawn as a recommendation (not invariant to intensity units).
+- Either way `noise_floor` survives only as the Poisson variance floor (both
+  patches leave it; it keeps the raw-count assumption the server's weights
+  make, which a unit change would also move).
+
+The two patches stay here as the measured starting points:
+`git apply docs/findings/noise-floor-occupancy/variant_F_support_test.patch`.
diff --git a/templates/index.html b/templates/index.html
index 5d38496..8b3f506 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7763,16 +7763,15 @@ function isC1sTab(tab) {
   if (isActive && typeof getROIData === 'function') {
     be = getROIData().be;
   } else {
-    const shift = Number.isFinite(tab.ccShift) ? tab.ccShift : 0;
-    const corr = tab.rawBE.map(v => v - shift);
+    // the SAME selection getROIData() makes, on the record's own data: each
+    // bound independently open when blank, never reordered (min > max selects
+    // nothing), inclusive, corrected frame (Codex round 1)
+    const shift = isNaN(tab.ccShift) ? 0 : tab.ccShift;   // read as getCorrectedBE() reads state.ccShift
     const ui = tab.ui || {};
     const a = parseFloat(ui.roiMin), b = parseFloat(ui.roiMax);
-    if (Number.isFinite(a) && Number.isFinite(b)) {
-      const lo = Math.min(a, b), hi = Math.max(a, b);
-      be = corr.filter(v => v >= lo && v <= hi);
-    } else {
-      be = corr;                               // no window set yet: the whole scan
-    }
+    const lo = isNaN(a) ? -Infinity : a, hi = isNaN(b) ? Infinity : b;
+    be = [];
+    for (const v of tab.rawBE) { const c = v - shift; if (c >= lo && c <= hi) be.push(c); }
   }
   if (!be || !be.length) return false;
   let lo = Infinity, hi = -Infinity;
diff --git a/tests/js/autofit_c1s_gate.test.js b/tests/js/autofit_c1s_gate.test.js
index 7b07fd6..44be6db 100644
--- a/tests/js/autofit_c1s_gate.test.js
+++ b/tests/js/autofit_c1s_gate.test.js
@@ -57,9 +57,22 @@ test('a non-active record is judged on its saved window over its own corrected d
   assert.strictEqual(g({ id: 't1', rawBE: [], ui: {} }), false);
 });
 
-test('every caller of the gate is for the active tab (menu state, charge-reference permission, the Auto-Fit run)', () => {
+test('the record path makes the SAME selection getROIData() makes (Codex round 1)', () => {
+  const g = gate({ activeId: 'other', liveSel: [] });
+  // reversed bounds select nothing, exactly as the live selector does
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '295', roiMax: '280' } }), false);
+  // a blank bound is open on its own side only: 270-295 is C 1s
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '', roiMax: '295' } }), true);
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '' } }), false);
+});
+
+test('every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)', () => {
   for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
-    assert.match(extractFn(fn), /isC1sTab\(tab\)/, fn);
+    const src = extractFn(fn);
+    const lookup = src.search(/const tab = [^;]*tabManager\._getTab\(tabManager\.activeId\)/);
+    assert.ok(lookup >= 0, fn + ': the tab is looked up by tabManager.activeId');
+    assert.ok(src.indexOf('isC1sTab(tab)') > lookup, fn + ': and that tab is the one judged');
+    assert.ok(!/\btab\s*=(?!=)/.test(src.slice(lookup + 10, src.indexOf('isC1sTab(tab)'))), fn + ': not reassigned in between');
   }
   // and the ROI fields refresh the menu on every keystroke
   assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-twOV0buq' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-E8cRXtVY' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 4b92c72..7f03bea 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -936,8 +936,10 @@ invariants worth knowing before touching the code:
 - **`+ Stack` / `+ Add Spectrum ▾`** (chart toolbar): create a new
   empty stack and add open spectrum tabs to the active stack.
 - **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
-  + charge correction. Enabled only when the active ROI midpoint is in
-  270–315 eV.
+  + charge correction. Enabled only when the midpoint of the DATA the fit
+  would use is in 270–315 eV — for the active tab the live selection
+  `getROIData()` returns, never the tab record's stale window or a typed
+  window reaching past the data (`isC1sTab`, unit F3 2026-09-27, sweep M5).
 - **ROI past the data / centre outside the data** (2026-09-25, warn only):
   `getROIData()` has always clamped an ROI to the data it selects; the page
   now SAYS so under the ROI fields ("ROI extends past your data — clipped
diff --git a/templates/index.html b/templates/index.html
index 72a215e..8b3f506 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7748,20 +7748,34 @@ async function runAutoFitC1sGraphite() {
   }
 }
 
+// Is this a C 1s spectrum, as Auto-Fit C1s Graphite would fit it? Unit F3
+// (2026-09-27, sweep M5): judged on the DATA the fit would use — for the active
+// tab the live selection getROIData() returns (the typed fields, clipped to the
+// data, in the corrected frame); for any other record its saved window over
+// its own corrected data. It used to read tab.ui, which for the ACTIVE tab is
+// synced only on a tab switch or save, and the TYPED midpoint: a wide scan with
+// the record's C 1s window but a U 4f window typed in the fields passed the
+// gate, and the fit then took the U 4f line as "Graphite".
 function isC1sTab(tab) {
   if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
-  const ui = tab.ui || {};
-  let lo = parseFloat(ui.roiMin);
-  let hi = parseFloat(ui.roiMax);
-  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
-    // Fall back to full raw range (no UI ROI set yet)
-    let rmin = Infinity, rmax = -Infinity;
-    for (const v of tab.rawBE) {
-      if (v < rmin) rmin = v;
-      if (v > rmax) rmax = v;
-    }
-    lo = rmin; hi = rmax;
-  }
+  let be;
+  const isActive = typeof tabManager !== 'undefined' && tabManager && tab.id === tabManager.activeId;
+  if (isActive && typeof getROIData === 'function') {
+    be = getROIData().be;
+  } else {
+    // the SAME selection getROIData() makes, on the record's own data: each
+    // bound independently open when blank, never reordered (min > max selects
+    // nothing), inclusive, corrected frame (Codex round 1)
+    const shift = isNaN(tab.ccShift) ? 0 : tab.ccShift;   // read as getCorrectedBE() reads state.ccShift
+    const ui = tab.ui || {};
+    const a = parseFloat(ui.roiMin), b = parseFloat(ui.roiMax);
+    const lo = isNaN(a) ? -Infinity : a, hi = isNaN(b) ? Infinity : b;
+    be = [];
+    for (const v of tab.rawBE) { const c = v - shift; if (c >= lo && c <= hi) be.push(c); }
+  }
+  if (!be || !be.length) return false;
+  let lo = Infinity, hi = -Infinity;
+  for (const v of be) { if (v < lo) lo = v; if (v > hi) hi = v; }
   if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
   const mid = (lo + hi) / 2;
   return mid >= 270.0 && mid <= 315.0;
diff --git a/tests/js/autofit_c1s_gate.test.js b/tests/js/autofit_c1s_gate.test.js
new file mode 100644
index 0000000..44be6db
--- /dev/null
+++ b/tests/js/autofit_c1s_gate.test.js
@@ -0,0 +1,80 @@
+// F3 (2026-09-27, sweep M5): the Auto-Fit C1s gate judges the DATA the fit
+// would use — for the active tab the live selection getROIData() returns, for
+// any other record its saved window over its own corrected data — never the
+// active tab's record ui (synced only on a tab switch or save) and never the
+// typed midpoint of a window that reaches past the data.
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
+const lines = html.split('\n');
+function extractFn(name) {
+  const re = new RegExp('^(async )?function ' + name + '\\(');
+  const start = lines.findIndex(l => re.test(l));
+  assert.ok(start >= 0, name);
+  let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) {
+    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
+    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
+  }
+  assert.fail('unbalanced ' + name);
+}
+
+// a wide scan 270-420 eV (C 1s and a U 4f doublet), 0.5 eV steps
+const RAW = Array.from({ length: 301 }, (_, i) => 420 - 0.5 * i);
+function gate({ activeId, liveSel }) {
+  const tabManager = { activeId };
+  const getROIData = () => ({ be: liveSel, inten: liveSel.map(() => 1) });
+  return new Function('tabManager', 'getROIData', extractFn('isC1sTab') + '\nreturn isC1sTab;')(tabManager, getROIData);
+}
+const sel = (lo, hi) => RAW.filter(v => v >= lo && v <= hi);
+
+test('the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES', () => {
+  const tab = { id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } };   // stale record ui
+  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(370, 415) })(tab), false, 'judged on the live U 4f selection');
+  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(280, 295) })(tab), true, 'a live C 1s selection passes');
+});
+
+test('the SELECTED data decide, not the typed midpoint of a window that reaches past the data', () => {
+  // data 280-300 only; typed 250-400 -> typed midpoint 325 (not C 1s) but the selection is all C 1s
+  const narrow = RAW.filter(v => v >= 280 && v <= 300);
+  const tab = { id: 't1', rawBE: narrow, ccShift: 0, ui: { roiMin: '250', roiMax: '400' } };
+  assert.strictEqual(gate({ activeId: 't1', liveSel: narrow })(tab), true);
+  assert.strictEqual(gate({ activeId: 't1', liveSel: [] })(tab), false, 'an empty selection is not C 1s');
+});
+
+test('a non-active record is judged on its saved window over its own corrected data', () => {
+  const g = gate({ activeId: 'other', liveSel: sel(370, 415) });
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } }), true);
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '415' } }), false);
+  // the window is in the CORRECTED frame, as the fit is: at a 100 eV shift, corrected 280-295 selects raw
+  // 380-395, which exists — judged as C 1s; a window the shifted data do not reach selects nothing
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 100, ui: { roiMin: '280', roiMax: '295' } }), true);
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 200, ui: { roiMin: '280', roiMax: '295' } }), false,
+    'corrected 70-220 has no point in 280-295: nothing selected');
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: {} }), false, 'no window: the whole 270-420 scan, midpoint 345');
+  assert.strictEqual(g({ id: 't1', rawBE: [], ui: {} }), false);
+});
+
+test('the record path makes the SAME selection getROIData() makes (Codex round 1)', () => {
+  const g = gate({ activeId: 'other', liveSel: [] });
+  // reversed bounds select nothing, exactly as the live selector does
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '295', roiMax: '280' } }), false);
+  // a blank bound is open on its own side only: 270-295 is C 1s
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '', roiMax: '295' } }), true);
+  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '' } }), false);
+});
+
+test('every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)', () => {
+  for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
+    const src = extractFn(fn);
+    const lookup = src.search(/const tab = [^;]*tabManager\._getTab\(tabManager\.activeId\)/);
+    assert.ok(lookup >= 0, fn + ': the tab is looked up by tabManager.activeId');
+    assert.ok(src.indexOf('isC1sTab(tab)') > lookup, fn + ': and that tab is the one judged');
+    assert.ok(!/\btab\s*=(?!=)/.test(src.slice(lookup + 10, src.indexOf('isC1sTab(tab)'))), fn + ': not reassigned in between');
+  }
+  // and the ROI fields refresh the menu on every keystroke
+  assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
+  assert.match(html, /id="roi-max"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
+});
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:13:Review unit F3 (the Auto-Fit C1s gate on live data): branch fix-noise-floor-scale-free, stacked on fix-fit-start-poll. Review git diff 07e0839..HEAD (07e0839 is the unit-2 commit F3 was cut from; later unit-2 commits are NOT part of F3): templates/index.html (isC1sTab only), tests/js/autofit_c1s_gate.test.js, CLAUDE.md, docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md, and the PARKED half's write-up docs/findings/noise-floor-occupancy/ (README + two patches that are NOT applied — review the write-up's claims and the patches as proposals, and say which variant you would choose and why). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO (for the shipped gate change; the parked half is advice). Budget your time: a verdict is required within the run.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:21:d. The parked half: are the measurements and the causal explanation in the README right (engine.py _extract_fitted_components / match_components_to_slots / rank_and_filter / the decisive override); is the recommendation sound; is anything in either patch wrong regardless of the choice (the variance floor left alone, orphans, the detectability payload, the grammar.contains change).
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:23:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:517:     # to a wall (Codex fwhm-cap review, run B BLOCKER).
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:718:     # to a wall (Codex fwhm-cap review, run B BLOCKER).
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:2122:        # record on the winner row (Codex fwhm-cap review, run A MINOR)
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:3047:   168	     # to a wall (Codex fwhm-cap review, run B BLOCKER).
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4252:The parked recommendation needs qualification: the honesty fixture contains two true peaks. P3’s third component absorbs background mismatch; this case does not show F rejecting a real third peak. LR preserves the conditional warning, but that alone does not establish better occupancy detection.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4385:No BLOCKER or MAJOR found in the shipped gate change. The parked proposals need further work.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4387:1. **MAJOR — parked: “scale-free Poisson likelihood ratio” overstates the implementation.** [README.md:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:31). The LR patch computes a weighted squared-error gain with other components held fixed; it neither evaluates a Poisson likelihood nor refits the reduced model. Dimensionless does not imply invariant under intensity rescaling. In a concrete probe, scaling data, fit, and component by 0.1 changed Δχ²/p from **40 to 4**, flipping LR occupancy; F stayed **32**. All observations remained above the variance floor. This matters for the same spectrum expressed in different intensity units.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4389:2. **MAJOR — parked: LR occupancy and detectability contradict each other.** [variant_LR_likelihood_ratio.patch:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:31), also line 176. Confidence still uses `support.supported`, reports `basis: support_f_test`, and exposes only the F statistic. The probe above produces **unoccupied** alongside **`above_floor`, F = 32**. Proposal rejection can consequently print **“F = 32.00 < 10”**. Use the chosen occupancy statistic consistently, or explicitly expose two distinct assessments.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4391:3. **MAJOR — parked: F reproduces the honesty regression, but the recommendation misinterprets its cause.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). I reproduced:
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4401:4. **MINOR — shipped: inactive records use different ROI semantics.** [templates/index.html:7771](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7771). Saved `295–280` is reordered and passes, while the live selector returns nothing. On a 270–420 scan, saved `min=""`, `max=295` uses the whole scan and fails; the live selector selects 270–295 and passes. Mirror independent open bounds and preserve reversed bounds. This is nonblocking because all three current callers pass the active tab.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4403:5. **MINOR — tests: the caller assertion does not establish active-tab ownership.** [autofit_c1s_gate.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:60). Replacing a caller’s lookup with an inactive record would still satisfy `/isC1sTab\(tab\)/`. The other three tests are substantive: all three fail against `07e0839`.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4411:VERDICT: GO
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4414:No BLOCKER or MAJOR found in the shipped gate change. The parked proposals need further work.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4416:1. **MAJOR — parked: “scale-free Poisson likelihood ratio” overstates the implementation.** [README.md:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:31). The LR patch computes a weighted squared-error gain with other components held fixed; it neither evaluates a Poisson likelihood nor refits the reduced model. Dimensionless does not imply invariant under intensity rescaling. In a concrete probe, scaling data, fit, and component by 0.1 changed Δχ²/p from **40 to 4**, flipping LR occupancy; F stayed **32**. All observations remained above the variance floor. This matters for the same spectrum expressed in different intensity units.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4418:2. **MAJOR — parked: LR occupancy and detectability contradict each other.** [variant_LR_likelihood_ratio.patch:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:31), also line 176. Confidence still uses `support.supported`, reports `basis: support_f_test`, and exposes only the F statistic. The probe above produces **unoccupied** alongside **`above_floor`, F = 32**. Proposal rejection can consequently print **“F = 32.00 < 10”**. Use the chosen occupancy statistic consistently, or explicitly expose two distinct assessments.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4420:3. **MAJOR — parked: F reproduces the honesty regression, but the recommendation misinterprets its cause.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). I reproduced:
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4430:4. **MINOR — shipped: inactive records use different ROI semantics.** [templates/index.html:7771](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7771). Saved `295–280` is reordered and passes, while the live selector returns nothing. On a 270–420 scan, saved `min=""`, `max=295` uses the whole scan and fails; the live selector selects 270–295 and passes. Mirror independent open bounds and preserve reversed bounds. This is nonblocking because all three current callers pass the active tab.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4432:5. **MINOR — tests: the caller assertion does not establish active-tab ownership.** [autofit_c1s_gate.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:60). Replacing a caller’s lookup with an inactive record would still satisfy `/isC1sTab\(tab\)/`. The other three tests are substantive: all three fail against `07e0839`.
docs/autofit/codex/f3_c1s_gate_verdict_runB.md:4440:VERDICT: GO
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:13:Review unit F3 (the Auto-Fit C1s gate on live data): branch fix-noise-floor-scale-free, stacked on fix-fit-start-poll. Review git diff 07e0839..HEAD (07e0839 is the unit-2 commit F3 was cut from; later unit-2 commits are NOT part of F3): templates/index.html (isC1sTab only), tests/js/autofit_c1s_gate.test.js, CLAUDE.md, docs/superpowers/plans/2026-09-27-f3-noise-floor-and-c1s-gate.md, and the PARKED half's write-up docs/findings/noise-floor-occupancy/ (README + two patches that are NOT applied — review the write-up's claims and the patches as proposals, and say which variant you would choose and why). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO (for the shipped gate change; the parked half is advice). Budget your time: a verdict is required within the run.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:21:d. The parked half: are the measurements and the causal explanation in the README right (engine.py _extract_fitted_components / match_components_to_slots / rank_and_filter / the decisive override); is the recommendation sound; is anything in either patch wrong regardless of the choice (the variance floor left alone, orphans, the detectability payload, the grammar.contains change).
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:23:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:1862:     # to a wall (Codex fwhm-cap review, run B BLOCKER).
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:1978:      # to a wall (Codex fwhm-cap review, run B BLOCKER).
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:4905:   168	     # to a wall (Codex fwhm-cap review, run B BLOCKER).
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5144:No BLOCKER found in the shipped gate. The parked proposals need further work.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5146:- **MAJOR — parked LR is not invariant to intensity rescaling.** [README.md:33](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:33), [LR patch:120](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:120). Dimensionless does not imply scale-free. Reproduced with `y=[100,100]`, fit `[90,110]`, component `[40,40]`, and one free parameter: Δχ²/p = 32, F = 16. Multiply every intensity by 0.1: Δχ²/p = 3.2, F remains 16. LR changes from occupied to absent; every count remains above the variance floor. This matters for unit normalization, independently of legitimately collecting fewer counts. Also, the implemented statistic is a weighted component-removal gain with other components held fixed, not a refitted Poisson likelihood-ratio test.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5148:- **MAJOR — parked LR reports a different decision rule from the one it uses.** [LR patch:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:31), [LR patch:173](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:173). Detectability still consumes `support.supported` and advertises `support_f_test`. In the scaled example above, occupancy rejects the component while detectability says `above_floor`; proposal rejection can literally report **“F = 16.00 < 10.”** Carry the chosen statistic, threshold, verdict, and basis consistently through occupancy, confidence, and rejection messages. Both variants also mislabel the positive-amplitude fallback as an F-test result when no support statistic exists.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5150:- **MAJOR — both parked patches retain the conflation of absence with an unexplained extra peak.** [F patch:141](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_F_support_test.patch:141), [LR patch:145](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:145). A component rejected by `_occupies` has no accepting slot and becomes an orphan. An unsupported optional component recurring across refits therefore produces `orphan_rate=1`, triggering a plausibility violation even when absent-slot handling excludes it from active persistence. This behavior predates the proposals, but replacing occupancy expands its consequences. Unsupported components and supported components that cannot be assigned need distinct treatment.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5152:- **MINOR — inactive-record selection disagrees with the actual fit.** [index.html:7770](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7770). On a 270–420 eV scan, saved bounds `295,280` return **true** through the record path, while the active path selects nothing and returns **false**. Bounds `'',295` produce the opposite disagreement: the active selection is 270–295 and passes; the record path uses the entire scan and fails. Preserve bound order and default missing bounds independently, matching `getROIData()`. This is nonblocking because all three production callers currently supply the active tab.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5154:- **MINOR — the parked write-up overstates what the stress failure demonstrates.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). F does return `conditional:false`, but also returns `filtered_dominant_alternative` naming P3 with ΔBIC ≈ 152.95; the page displays that warning. It does not silently produce an entirely unqualified answer. Moreover, this fixture contains **two true peaks**: P3’s third component compensates for background mismatch. Calling it a rejected “real component” is unsupported.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5172:VERDICT: GO
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5175:No BLOCKER found in the shipped gate. The parked proposals need further work.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5177:- **MAJOR — parked LR is not invariant to intensity rescaling.** [README.md:33](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:33), [LR patch:120](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:120). Dimensionless does not imply scale-free. Reproduced with `y=[100,100]`, fit `[90,110]`, component `[40,40]`, and one free parameter: Δχ²/p = 32, F = 16. Multiply every intensity by 0.1: Δχ²/p = 3.2, F remains 16. LR changes from occupied to absent; every count remains above the variance floor. This matters for unit normalization, independently of legitimately collecting fewer counts. Also, the implemented statistic is a weighted component-removal gain with other components held fixed, not a refitted Poisson likelihood-ratio test.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5179:- **MAJOR — parked LR reports a different decision rule from the one it uses.** [LR patch:31](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:31), [LR patch:173](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:173). Detectability still consumes `support.supported` and advertises `support_f_test`. In the scaled example above, occupancy rejects the component while detectability says `above_floor`; proposal rejection can literally report **“F = 16.00 < 10.”** Carry the chosen statistic, threshold, verdict, and basis consistently through occupancy, confidence, and rejection messages. Both variants also mislabel the positive-amplitude fallback as an F-test result when no support statistic exists.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5181:- **MAJOR — both parked patches retain the conflation of absence with an unexplained extra peak.** [F patch:141](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_F_support_test.patch:141), [LR patch:145](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/variant_LR_likelihood_ratio.patch:145). A component rejected by `_occupies` has no accepting slot and becomes an orphan. An unsupported optional component recurring across refits therefore produces `orphan_rate=1`, triggering a plausibility violation even when absent-slot handling excludes it from active persistence. This behavior predates the proposals, but replacing occupancy expands its consequences. Unsupported components and supported components that cannot be assigned need distinct treatment.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5183:- **MINOR — inactive-record selection disagrees with the actual fit.** [index.html:7770](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7770). On a 270–420 eV scan, saved bounds `295,280` return **true** through the record path, while the active path selects nothing and returns **false**. Bounds `'',295` produce the opposite disagreement: the active selection is 270–295 and passes; the record path uses the entire scan and fails. Preserve bound order and default missing bounds independently, matching `getROIData()`. This is nonblocking because all three production callers currently supply the active tab.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5185:- **MINOR — the parked write-up overstates what the stress failure demonstrates.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). F does return `conditional:false`, but also returns `filtered_dominant_alternative` naming P3 with ΔBIC ≈ 152.95; the page displays that warning. It does not silently produce an entirely unqualified answer. Moreover, this fixture contains **two true peaks**: P3’s third component compensates for background mismatch. Calling it a rejected “real component” is unsupported.
docs/autofit/codex/f3_c1s_gate_verdict_runA.md:5203:VERDICT: GO

exec
/bin/zsh -lc "rg --files --hidden -g AGENTS.md -g package.json -g '"'!'"\\.git'; rg -n 'function (getROIData|getCorrectedBE|isC1sTab|_recomputeAutoFitMenuState|_isChargeRefAllowed|runAutoFitC1sGraphite)|isC1sTab\\(' templates/index.html; cat tests/js/autofit_c1s_gate.test.js; git diff 07e0839..HEAD -- templates/index.html CLAUDE.md; sed -n '5154,5174p' docs/autofit/codex/f3_c1s_gate_verdict_runA.md; sed -n '4391,4412p' docs/autofit/codex/f3_c1s_gate_verdict_runB.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
5079:function getCorrectedBE() {
5087:function getROIData() {
6099:function _isChargeRefAllowed() {
6105:  return !!(tab && isC1sTab(tab));
6712:function _recomputeAutoFitMenuState() {
6718:  const enabled = !!tab && isC1sTab(tab);
7558:async function runAutoFitC1sGraphite() {
7563:  if (!isC1sTab(tab)) {
7759:function isC1sTab(tab) {
// F3 (2026-09-27, sweep M5): the Auto-Fit C1s gate judges the DATA the fit
// would use — for the active tab the live selection getROIData() returns, for
// any other record its saved window over its own corrected data — never the
// active tab's record ui (synced only on a tab switch or save) and never the
// typed midpoint of a window that reaches past the data.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}

// a wide scan 270-420 eV (C 1s and a U 4f doublet), 0.5 eV steps
const RAW = Array.from({ length: 301 }, (_, i) => 420 - 0.5 * i);
function gate({ activeId, liveSel }) {
  const tabManager = { activeId };
  const getROIData = () => ({ be: liveSel, inten: liveSel.map(() => 1) });
  return new Function('tabManager', 'getROIData', extractFn('isC1sTab') + '\nreturn isC1sTab;')(tabManager, getROIData);
}
const sel = (lo, hi) => RAW.filter(v => v >= lo && v <= hi);

test('the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES', () => {
  const tab = { id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } };   // stale record ui
  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(370, 415) })(tab), false, 'judged on the live U 4f selection');
  assert.strictEqual(gate({ activeId: 't1', liveSel: sel(280, 295) })(tab), true, 'a live C 1s selection passes');
});

test('the SELECTED data decide, not the typed midpoint of a window that reaches past the data', () => {
  // data 280-300 only; typed 250-400 -> typed midpoint 325 (not C 1s) but the selection is all C 1s
  const narrow = RAW.filter(v => v >= 280 && v <= 300);
  const tab = { id: 't1', rawBE: narrow, ccShift: 0, ui: { roiMin: '250', roiMax: '400' } };
  assert.strictEqual(gate({ activeId: 't1', liveSel: narrow })(tab), true);
  assert.strictEqual(gate({ activeId: 't1', liveSel: [] })(tab), false, 'an empty selection is not C 1s');
});

test('a non-active record is judged on its saved window over its own corrected data', () => {
  const g = gate({ activeId: 'other', liveSel: sel(370, 415) });
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '280', roiMax: '295' } }), true);
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '415' } }), false);
  // the window is in the CORRECTED frame, as the fit is: at a 100 eV shift, corrected 280-295 selects raw
  // 380-395, which exists — judged as C 1s; a window the shifted data do not reach selects nothing
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 100, ui: { roiMin: '280', roiMax: '295' } }), true);
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 200, ui: { roiMin: '280', roiMax: '295' } }), false,
    'corrected 70-220 has no point in 280-295: nothing selected');
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: {} }), false, 'no window: the whole 270-420 scan, midpoint 345');
  assert.strictEqual(g({ id: 't1', rawBE: [], ui: {} }), false);
});

test('the record path makes the SAME selection getROIData() makes (Codex round 1)', () => {
  const g = gate({ activeId: 'other', liveSel: [] });
  // reversed bounds select nothing, exactly as the live selector does
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '295', roiMax: '280' } }), false);
  // a blank bound is open on its own side only: 270-295 is C 1s
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '', roiMax: '295' } }), true);
  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '' } }), false);
});

test('every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)', () => {
  for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
    const src = extractFn(fn);
    const lookup = src.search(/const tab = [^;]*tabManager\._getTab\(tabManager\.activeId\)/);
    assert.ok(lookup >= 0, fn + ': the tab is looked up by tabManager.activeId');
    assert.ok(src.indexOf('isC1sTab(tab)') > lookup, fn + ': and that tab is the one judged');
    assert.ok(!/\btab\s*=(?!=)/.test(src.slice(lookup + 10, src.indexOf('isC1sTab(tab)'))), fn + ': not reassigned in between');
  }
  // and the ROI fields refresh the menu on every keystroke
  assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
  assert.match(html, /id="roi-max"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
});
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-7ulBX0mx' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZZkFH7VV' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 4b92c72..7f03bea 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -936,8 +936,10 @@ invariants worth knowing before touching the code:
 - **`+ Stack` / `+ Add Spectrum ▾`** (chart toolbar): create a new
   empty stack and add open spectrum tabs to the active stack.
 - **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
-  + charge correction. Enabled only when the active ROI midpoint is in
-  270–315 eV.
+  + charge correction. Enabled only when the midpoint of the DATA the fit
+  would use is in 270–315 eV — for the active tab the live selection
+  `getROIData()` returns, never the tab record's stale window or a typed
+  window reaching past the data (`isC1sTab`, unit F3 2026-09-27, sweep M5).
 - **ROI past the data / centre outside the data** (2026-09-25, warn only):
   `getROIData()` has always clamped an ROI to the data it selects; the page
   now SAYS so under the ROI fields ("ROI extends past your data — clipped
diff --git a/templates/index.html b/templates/index.html
index 72a215e..8b3f506 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7748,20 +7748,34 @@ async function runAutoFitC1sGraphite() {
   }
 }
 
+// Is this a C 1s spectrum, as Auto-Fit C1s Graphite would fit it? Unit F3
+// (2026-09-27, sweep M5): judged on the DATA the fit would use — for the active
+// tab the live selection getROIData() returns (the typed fields, clipped to the
+// data, in the corrected frame); for any other record its saved window over
+// its own corrected data. It used to read tab.ui, which for the ACTIVE tab is
+// synced only on a tab switch or save, and the TYPED midpoint: a wide scan with
+// the record's C 1s window but a U 4f window typed in the fields passed the
+// gate, and the fit then took the U 4f line as "Graphite".
 function isC1sTab(tab) {
   if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
-  const ui = tab.ui || {};
-  let lo = parseFloat(ui.roiMin);
-  let hi = parseFloat(ui.roiMax);
-  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
-    // Fall back to full raw range (no UI ROI set yet)
-    let rmin = Infinity, rmax = -Infinity;
-    for (const v of tab.rawBE) {
-      if (v < rmin) rmin = v;
-      if (v > rmax) rmax = v;
-    }
-    lo = rmin; hi = rmax;
-  }
+  let be;
+  const isActive = typeof tabManager !== 'undefined' && tabManager && tab.id === tabManager.activeId;
+  if (isActive && typeof getROIData === 'function') {
+    be = getROIData().be;
+  } else {
+    // the SAME selection getROIData() makes, on the record's own data: each
+    // bound independently open when blank, never reordered (min > max selects
+    // nothing), inclusive, corrected frame (Codex round 1)
+    const shift = isNaN(tab.ccShift) ? 0 : tab.ccShift;   // read as getCorrectedBE() reads state.ccShift
+    const ui = tab.ui || {};
+    const a = parseFloat(ui.roiMin), b = parseFloat(ui.roiMax);
+    const lo = isNaN(a) ? -Infinity : a, hi = isNaN(b) ? Infinity : b;
+    be = [];
+    for (const v of tab.rawBE) { const c = v - shift; if (c >= lo && c <= hi) be.push(c); }
+  }
+  if (!be || !be.length) return false;
+  let lo = Infinity, hi = -Infinity;
+  for (const v of be) { if (v < lo) lo = v; if (v > hi) hi = v; }
   if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
   const mid = (lo + hi) / 2;
   return mid >= 270.0 && mid <= 315.0;
- **MINOR — the parked write-up overstates what the stress failure demonstrates.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). F does return `conditional:false`, but also returns `filtered_dominant_alternative` naming P3 with ΔBIC ≈ 152.95; the page displays that warning. It does not silently produce an entirely unqualified answer. Moreover, this fixture contains **two true peaks**: P3’s third component compensates for background mismatch. Calling it a rejected “real component” is unsupported.

I reproduced the central measurements by loading each patch’s source **in memory**, without applying either patch:

| Variant | Winner | Conditional | P3 minimum persistence |
|---|---|---:|---:|
| Baseline | P3+bfix | true | 1 |
| F | P2 | false | 0 |
| LR | P3+bfix | true | 1 |

P3’s third component has F ≈ **9.417**, Δχ² ≈ **10,702**, and four free parameters. The extraction → matching → persistence → decisive-override explanation is correct. The claimed complete suite totals were not independently rerun.

**I would choose F as the starting variant for the stated scale-free requirement**, then repair the absence/orphan distinction and the honesty behavior before shipping it. Neither patch is ready unchanged. LR’s passing existing gates does not establish scale invariance. Leaving the variance floor alone preserves the existing weighting convention, but neither proposal should promise arbitrary-unit invariance across that floor. The `grammar.contains` change has no internal callers and is consistent with a sign-only geometric check; it should not be presented as a support verdict.

For the shipped gate, all three callers resolve the active record. Tab activation restores data and fields before evaluating it. Stack tabs fail closed; survey tabs retain the midpoint rule. The active path correctly inherits corrected energies, inclusive clipping, independently blank bounds, and empty/reversed-window behavior. Blank ROI fields still permit Auto-Fit on a narrow C1s scan. A million-point inactive record completed without argument-spread failure, taking approximately 102 ms here, though its intermediate arrays are avoidable.

Validation: **48 relevant JS tests passed**. Running the four new tests against the old implementation produced **three failures**, confirming substantive regression coverage. The fourth test only checks source patterns; it does not prove active-tab identity or caller timing. No files were changed.

VERDICT: GO
tokens used
81,417
3. **MAJOR — parked: F reproduces the honesty regression, but the recommendation misinterprets its cause.** [README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:48). I reproduced:
   
   | Variant | Winner | Conditional |
   |---|---|---|
   | Baseline | P3+bfix | true |
   | F | P2 | false |
   | LR | P3+bfix | true |
   
   P3’s third component has Δχ² **10,702.374**, F **9.417**; F drops its persistence to zero and orphan rate becomes one. That excludes it from the decisive-override pool, as described. However, the fixture has **two true peaks** ([stress_cases.py:406](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/autofit/stress_cases.py:406)). This demonstrates an honesty flag depending on retaining a background-compensating third component; it does **not** demonstrate F rejecting a real third peak.

4. **MINOR — shipped: inactive records use different ROI semantics.** [templates/index.html:7771](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/templates/index.html:7771). Saved `295–280` is reordered and passes, while the live selector returns nothing. On a 270–420 scan, saved `min=""`, `max=295` uses the whole scan and fails; the live selector selects 270–295 and passes. Mirror independent open bounds and preserve reversed bounds. This is nonblocking because all three current callers pass the active tab.

5. **MINOR — tests: the caller assertion does not establish active-tab ownership.** [autofit_c1s_gate.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:60). Replacing a caller’s lookup with an inactive record would still satisfy `/isC1sTab\(tab\)/`. The other three tests are substantive: all three fail against `07e0839`.

The active path behaved correctly with the actual `getROIData()`: inclusive clipping, reversed and empty selections, independently blank bounds, corrected energies, stacks, and surveys. Blank ROI fields still permit Auto-Fit on a narrow C1s scan. Tab activation installs incoming state and fields before menu evaluation; click-time validation reads live data. A million-point inactive record completed without argument-limit failure, taking approximately **111 ms** locally, though it allocates intermediate arrays.

For the parked work, **I would choose F as the basis**, with model-mismatch honesty handled independently before applying it. It shares the existing support definition and avoids LR’s demonstrated rescaling sensitivity. Neither patch is ready unchanged. Leaving the variance floor alone is reasonable for this scoped change, but preserves its raw-count assumptions. Both correctly retain support through component copies; both also classify unsupported in-window components as orphans, which should be distinguished from geometrically unmatched peaks. `grammar.contains` has no current Python callers; its ignored `noise_floor` argument is therefore an API cleanup concern, not a demonstrated runtime regression.

Validation: **65 focused JavaScript tests passed**; both patches were evaluated in memory without application. The central README measurements and ranking explanation were reproduced. The complete claimed Python suite totals were not independently rerun. No files changed.

VERDICT: GO
tokens used

exec
/bin/zsh -lc 'node --test tests/js/autofit_c1s_gate.test.js; nl -ba docs/findings/noise-floor-occupancy/README.md | head -115; cat docs/findings/noise-floor-occupancy/variant_F_support_test.patch' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 49ms:
# Subtest: the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
ok 1 - the sweep reproduction: record window on C 1s, U 4f typed in the fields (no tab switch) — the gate CLOSES
  ---
  duration_ms: 3.793556
  type: 'test'
  ...
# Subtest: the SELECTED data decide, not the typed midpoint of a window that reaches past the data
ok 2 - the SELECTED data decide, not the typed midpoint of a window that reaches past the data
  ---
  duration_ms: 0.956814
  type: 'test'
  ...
# Subtest: a non-active record is judged on its saved window over its own corrected data
ok 3 - a non-active record is judged on its saved window over its own corrected data
  ---
  duration_ms: 0.596171
  type: 'test'
  ...
# Subtest: the record path makes the SAME selection getROIData() makes (Codex round 1)
ok 4 - the record path makes the SAME selection getROIData() makes (Codex round 1)
  ---
  duration_ms: 0.481722
  type: 'test'
  ...
# Subtest: every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)
ok 5 - every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)
  ---
  duration_ms: 1.631518
  type: 'test'
  ...
1..5
# tests 5
# suites 0
# pass 5
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 94.653984
     1	# Find Peaks' 1-count occupancy floor → scale-free: PARKED for an owner decision (2026-09-27)
     2	
     3	Part of unit F3 (sweep M9, first bullet). The other half of F3 — the Auto-Fit
     4	C1s gate judging a stale typed window (sweep M5) — ships on its own in
     5	`fix-noise-floor-scale-free` and does not depend on this.
     6	
     7	## What was found
     8	
     9	`noise_floor` (default 1.0, never sent by the page) does two jobs in
    10	`autofit/`:
    11	
    12	1. a Poisson variance floor, `sigma = sqrt(max(y, noise_floor))` — the
    13	   counting convention the server's weights use; not a decision threshold,
    14	   left as is by both variants;
    15	2. an OCCUPANCY threshold, `amplitude > noise_floor` — whether a fitted
    16	   component occupies its slot (`match_components_to_slots`), whether a
    17	   proposed slot survives (`_evaluate_proposal`), the detectability status
    18	   (`build_confidence_vector`). A slot is "occupied" at amplitude 1.5 and not
    19	   at 0.5 whatever the data's scale; persistence, the absent-slot test and the
    20	   stability gate follow from it. This is the design rule's case.
    21	
    22	Both variants replace (2) with a statistic on the component's own fit
    23	(computed once when the component is extracted from its lmfit result and
    24	carried on `FittedComponent.support`), leave (1) alone, and fall back to
    25	`amplitude > 0` (a sign test) for a component with no fit behind it. They
    26	differ in ONE line — what "occupied" means:
    27	
    28	| variant | occupied when | patch |
    29	|---|---|---|
    30	| **F** — the server's support test | `fitting._component_support` "supported": Δχ² > 0 and F = (Δχ²/p) / (χ²_with/dof) ≥ 10 — the step (b) "not supported by the data" statistic and threshold | `variant_F_support_test.patch` |
    31	| **LR** — Poisson likelihood ratio | Δχ²/p ≥ 10 on the Poisson-weighted χ², NOT divided by the fit's own misfit χ²_with/dof | `variant_LR_likelihood_ratio.patch` |
    32	
    33	Both are scale-free (the weights make χ² dimensionless) and carry no tolerance.
    34	
    35	## The evidence
    36	
    37	| suite | baseline (today) | F | LR |
    38	|---|---|---|---|
    39	| gated real-data parity gates + stress honesty (`RUN_AUTOFIT_GATE=1`: C 1s parity, Bayesian real, candidate-pool real, U 4f unresolved, stress honesty) | 17 passed, 4 skipped | **16 passed, 1 FAILED** | 17 passed, 4 skipped |
    40	| always-on `tests/autofit` (incl. the C 1s / region parity batteries) | green | **1 failed** (the same stress case), 556 passed | 557 passed, 7 skipped |
    41	
    42	The failing case, `test_stress_honesty.py::test_bg_mismatch_surfaces_loudly`:
    43	a Shirley-shaped truth fitted with a straight-line background, χ²ᵣ ≈ 280–470
    44	for every candidate. The test requires the mismatch to be machine-visible
    45	("conditional" tier), never a clean confident result. Today the 3-component
    46	candidate P3 is stable but violates plausibility, enters the conditional
    47	pool, and its bound-fixed refit wins via the decisive override →
    48	`conditional: true`. Under F, P3's third component has F < 10 BECAUSE the fit
    49	is so bad: F divides the gain by χ²_with/dof ≈ 284, so a component that
    50	removes a large χ² still reads "unsupported"; it becomes an orphan, P3's
    51	persistence drops to 0, P3 leaves the conditional pool, and P2 (χ²ᵣ 309) is
    52	returned as a CLEAN survivor. Under LR the same component is occupied (its
    53	gain per parameter is far above 10 Poisson units) and the result is
    54	conditional, as today.
    55	
    56	## Codex review of this write-up (F3 round 1, `f3_c1s_gate_verdict_run{A,B}.md`) — the recommendation below replaces the first draft's
    57	
    58	Both runs reproduced the measurements and the mechanism (P3's third component:
    59	Δχ² ≈ 10 702, F ≈ 9.42 with four free parameters → persistence 0, orphan rate 1,
    60	out of the decisive-override pool). They also found three things wrong with
    61	the first draft's recommendation of LR, all of which hold:
    62	
    63	1. **LR is not scale-free.** "Dimensionless" is not "invariant under a change
    64	   of intensity units": with Poisson weights the gain Δχ² scales with the
    65	   counts, so multiplying a spectrum by 0.1 (CPS instead of counts, a
    66	   normalisation) turned Δχ²/p = 32 into 3.2 and flipped the verdict, while F
    67	   stayed at 16 — F is a RATIO of two χ² quantities and is invariant. The
    68	   design rule asks for exactly that invariance. (The statistic is also a
    69	   gain with the other components held fixed, not a refitted likelihood
    70	   ratio; the draft's name overstated it.)
    71	2. **The LR patch is internally inconsistent**: occupancy used Δχ²/p while
    72	   detectability still used `support.supported` and reported
    73	   `basis: support_f_test`, so a component could be "unoccupied" and
    74	   `above_floor` at once, and a proposal rejection could print "F = 32.00 < 10".
    75	3. **The stress case does not show F rejecting a real peak.** The fixture
    76	   (`tests/autofit/stress_cases.py`) has TWO true peaks; P3's third component
    77	   compensates for the wrong background. F calls it unsupported — defensibly —
    78	   and the honesty flag then disappears because the "conditional" tier
    79	   depended on keeping that background-compensating component. The F result
    80	   also still carries `filtered_dominant_alternative` (P3, ΔBIC ≈ 153), which
    81	   the page shows: not a silent clean answer.
    82	
    83	Both runs, independently: **start from F** (one support definition across
    84	the app, invariant to intensity units) and fix two things around it before
    85	shipping:
    86	
    87	- an unsupported component INSIDE its slot's window must not become an
    88	  "orphan" (an unexplained extra peak) — today (and in both patches) a
    89	  component that fails occupancy has no accepting slot and counts toward
    90	  `orphan_rate`, a plausibility violation; "slot empty" and "peak nobody
    91	  expects" need distinct treatment;
    92	- the model-mismatch honesty signal must not depend on a component that only
    93	  compensates for a wrong background — report the mismatch (χ²ᵣ ≫ 1, the
    94	  residual structure) on its own terms.
    95	
    96	## The decision (owner)
    97	
    98	- **Adopt F as the occupancy statistic** (recommended, both reviewers), as a
    99	  unit of its own with the two follow-ups above, measured on the gated and
   100	  always-on suites; the honesty test is then re-examined against a
   101	  mismatch signal that does not ride on P3.
   102	- **LR**: withdrawn as a recommendation (not invariant to intensity units).
   103	- Either way `noise_floor` survives only as the Poisson variance floor (both
   104	  patches leave it; it keeps the raw-count assumption the server's weights
   105	  make, which a unit change would also move).
   106	
   107	The two patches stay here as the measured starting points:
   108	`git apply docs/findings/noise-floor-occupancy/variant_F_support_test.patch`.
diff --git a/autofit/confidence.py b/autofit/confidence.py
index bb74778..ab2897f 100644
--- a/autofit/confidence.py
+++ b/autofit/confidence.py
@@ -83,6 +83,9 @@ def _max_correlation(report: ModelReport, role: str) -> Optional[float]:
     return float(np.max(sub)) if sub.size else None
 
 
+from fitting import SUPPORT_MIN_F as _SUPPORT_MIN_F  # F3: one threshold, the server's
+
+
 def build_confidence_vector(
     report: ModelReport,
     role: str,
@@ -96,12 +99,19 @@ def build_confidence_vector(
                 if h.startswith(f"{role}:")]
 
     amplitude = float(comp.amplitude) if comp is not None else None
-    floor = detection_floor_multiple * noise_floor
+    # F3 (2026-09-27): detectability is the support F test on the fit
+    # (fitting._component_support, the server's statistic), not multiples of an
+    # absolute 1-count floor. above_floor = supported (F >= SUPPORT_MIN_F);
+    # present_but_poorly_constrained = the fit gains from it but not
+    # significantly; not_confidently_detected = removing it costs nothing.
+    support = getattr(comp, "support", None) if comp is not None else None
     if amplitude is None:
         detect_status = "not_fitted"
-    elif amplitude >= floor:
+    elif support is None:
+        detect_status = "above_floor" if amplitude > 0 else "not_confidently_detected"
+    elif support.get("supported"):
         detect_status = "above_floor"
-    elif amplitude > noise_floor:
+    elif (support.get("delta_chi2") or 0.0) > 0:
         detect_status = "present_but_poorly_constrained"
     else:
         detect_status = "not_confidently_detected"
@@ -122,9 +132,9 @@ def build_confidence_vector(
         },
         "detectability": {
             "amplitude": amplitude,
-            "noise_floor": noise_floor,
-            "floor_multiple": detection_floor_multiple,
-            "floor_multiple_is_tunable": True,
+            "basis": "support_f_test",       # F3: fitting._component_support, F >= SUPPORT_MIN_F
+            "support_f": (support or {}).get("f"),
+            "support_min_f": _SUPPORT_MIN_F,
             "status": detect_status,
         },
         "identifiability": {
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..9bad455 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -36,6 +36,7 @@ from typing import Callable, Optional
 
 import numpy as np
 from lmfit import Model, Parameters
+import fitting as _fitting  # F3: the server's support statistic, one definition
 from lmfit.model import ModelResult
 from scipy.integrate import trapezoid
 
@@ -637,6 +638,17 @@ class FittedComponent:
     amplitude: float
     shape_params: dict
     line_shape: Optional[LineShape] = None
+    # Unit F3 (2026-09-27): does the fit that produced this component need it?
+    # fitting._component_support on that fit — with the other components held
+    # as fitted, removing this one must make the fit significantly worse (F >=
+    # SUPPORT_MIN_F). The occupancy decisions (slot matching, the proposal
+    # gate, detectability) read this instead of an absolute amplitude floor
+    # of 1 count, which judged a slot "occupied" at amplitude 1.5 and not at
+    # 0.5 whatever the data's scale (sweep M9; design rule "thresholds on
+    # data-scaled quantities fail"). None only where no fit is behind the
+    # component (hand-built in tests): then occupancy falls back to amplitude
+    # > 0, a sign test.
+    support: Optional[dict] = None
 
 
 @dataclass
@@ -652,10 +664,46 @@ class FitOutcome:
     boundary_hits: list[str] = field(default_factory=list)
 
 
+def _component_supports(result: ModelResult) -> dict[str, dict]:
+    """``fitting._component_support`` for every peak component of an lmfit
+    result, keyed by prefix — the one definition the server uses (step (b)).
+    Empty when the result carries no data (never raises: occupancy then falls
+    back to the sign test)."""
+    try:
+        comps = result.eval_components()
+        data = np.asarray(result.data, float)
+        fitted = np.asarray(result.best_fit, float)
+        w = result.weights if result.weights is not None else np.ones_like(data)
+        w = np.broadcast_to(np.asarray(w, float), data.shape)
+        n_free_total = int(result.nvarys)
+    except Exception:
+        return {}
+    out = {}
+    for prefix, comp_y in comps.items():
+        n_free_comp = sum(1 for n, par in result.params.items()
+                          if n.startswith(prefix) and par.vary and par.expr is None)
+        try:
+            out[prefix] = _fitting._component_support(data, fitted, np.asarray(comp_y, float), w,
+                                                      n_free_comp, n_free_total)
+        except Exception:
+            continue
+    return out
+
+
+def _occupies(comp: "FittedComponent") -> bool:
+    """A slot is occupied by a component the data support (F3). No threshold
+    on any data-scaled quantity: the support F test where a fit is behind the
+    component, else the sign of its amplitude."""
+    if comp.support is not None:
+        return bool(comp.support.get("supported"))
+    return comp.amplitude > 0
+
+
 def _extract_fitted_components(
     result: ModelResult, model: CandidateModel
 ) -> list[FittedComponent]:
     out: list[FittedComponent] = []
+    supports = _component_supports(result)
     for slot in model.slots:
         prefix = _slot_prefix(slot.role)
         pars = result.params
@@ -676,6 +724,7 @@ def _extract_fitted_components(
             slot_role=slot.role, position=center, fwhm=fwhm,
             amplitude=amplitude, shape_params=shape_params,
             line_shape=slot.line_shape,
+            support=supports.get(prefix),
         ))
     return out
 
@@ -1055,7 +1104,7 @@ def match_components_to_slots(
                                       (bound_overrides or {}).get(slot.role))
         return (lo <= comp.position <= hi
                 and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
-                and comp.amplitude > noise_floor)
+                and _occupies(comp))       # F3: supported by the data, not amplitude > 1 count
 
     def _window_center(slot: ComponentSlot) -> float:
         # NEVER the widened bound (Codex-caught, round 2): this is a
@@ -1077,7 +1126,7 @@ def match_components_to_slots(
             orphans.append(FittedComponent(
                 slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                 amplitude=comp.amplitude, shape_params=comp.shape_params,
-                line_shape=comp.line_shape,
+                line_shape=comp.line_shape, support=comp.support,
             ))
             continue
 
@@ -1095,7 +1144,7 @@ def match_components_to_slots(
         claimed = FittedComponent(
             slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
             amplitude=comp.amplitude, shape_params=comp.shape_params,
-            line_shape=comp.line_shape,
+            line_shape=comp.line_shape, support=comp.support,
         )
         if incumbent is None:
             slot_map[best_slot.role] = claimed
@@ -2229,8 +2278,10 @@ def _attempt_proposal(
     # to a wall (Codex fwhm-cap review, run B BLOCKER).
     width_cap_hit = f"{spec.role}:fwhm@max"
     pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
-    if comp.amplitude <= noise_floor:
-        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
+    if not _occupies(comp):
+        f = (comp.support or {}).get("f")
+        return _fast("not supported by the data (removing it does not make the fit significantly worse"
+                     + (f", F = {f:.2f} < {_fitting.SUPPORT_MIN_F:.0f}" if f is not None else "") + ")")
     spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
     if spurious_hits:
         return _fast(f"proposed slot boundary pegs: {spurious_hits}")
diff --git a/autofit/grammar.py b/autofit/grammar.py
index c9a85cd..bed2606 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -181,11 +181,15 @@ class ComponentSlot:
     broad_justification: Optional[str] = None
 
     def contains(self, be: float, fwhm: float, amplitude: float,
-                 noise_floor: float) -> bool:
+                 noise_floor: float = 0.0) -> bool:
+        # F3 (2026-09-27): occupancy is decided by the support F test on the
+        # fit (engine._occupies); this geometric check keeps only the sign of
+        # the amplitude. ``noise_floor`` is accepted and ignored (no caller in
+        # the engine passes it any more).
         return (
             self.be_window[0] <= be <= self.be_window[1]
             and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
-            and amplitude > noise_floor
+            and amplitude > 0
         )
 
 

codex
The five gate tests pass, and the record selector now appears to match the live selector’s bound and shift rules. The README still contains the old “both are scale-free” claim above its correction. Next I’ll probe edge-case parity and mutate the caller lookups in memory to test the strengthened assertion.

exec
/bin/zsh -lc "sed -n '5068,5125p' templates/index.html; sed -n '6090,6112p' templates/index.html; sed -n '6705,6732p' templates/index.html; sed -n '7550,7605p' templates/index.html; sed -n '7759,7791p' templates/index.html; rg -n '_recomputeAutoFitMenuState|state.rawBE =|ccShift = tab|activate\\(' templates/index.html static/js/tab_manager.js; rg -n 'def _component_support|SUPPORT_MIN_F' fitting.py; rg --files -g '*tab*' -g '*python*' -g 'pyproject.toml' -g 'pytest.ini' -g 'requirements*' | head -40" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
  // xpsRefLinesPlugin gates on `chart === state.chart` and is skipped on the
  // `new Chart()` first paint (the same render-timing gap _refRenderReferenceChart
  // already works around). renderPeakList/_refOnTabChange only refresh panel/legend
  // DOM — no chart repaint — so element reference overlays (lines, bands, labels)
  // would vanish until the next hover/toggle. Re-issue the guarded reference-overlay
  // repaint so they stay painted through a charge-correction change. Leaf-level
  // chart.update('none'); positioning math and ccShift are untouched (overlays stay
  // at nominal corrected BE), and it is a no-op when no chart/spectrum/overlays exist.
  if (typeof _refRepaint === 'function') _refRepaint();
}

function getCorrectedBE() {
  const shift = isNaN(state.ccShift) ? 0 : state.ccShift;
  return state.rawBE.map(b => b - shift);
}

// ═══════════════════════════════════════════════════
// ROI FILTERING
// ═══════════════════════════════════════════════════
function getROIData() {
  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
  // NaN bounds mean the field is empty — use full range rather than filtering everything out
  const roiMin = isNaN(roiMinRaw) ? -Infinity : roiMinRaw;
  const roiMax = isNaN(roiMaxRaw) ?  Infinity : roiMaxRaw;
  const corrBE = getCorrectedBE();
  const be = [], inten = [];
  for (let i = 0; i < corrBE.length; i++) {
    if (corrBE[i] >= roiMin && corrBE[i] <= roiMax) {
      be.push(corrBE[i]);
      inten.push(state.rawIntensity[i]);
    }
  }
  return { be, inten };
}

// ── ROI past the data / centre outside the data (2026-09-25) ─────────────
// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
// the data in every fit, background, area and export — the defect was that
// nothing said so. This reports the window actually used; it writes nothing
// back into the fields, the peaks or the fit-evidence key. Find Peaks sends
// the same two numbers against the same corrected energies to a server mask
// of the same inclusive form, so this one window is the one both use.
// Plan: docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
function _roiWindowStatus() {
  const corrBE = (typeof getCorrectedBE === 'function' && state.rawBE && state.rawBE.length) ? getCorrectedBE() : [];
  if (!corrBE.length) return { state: 'no-data' };
  let dMin = Infinity, dMax = -Infinity;
  for (const v of corrBE) { if (v < dMin) dMin = v; if (v > dMax) dMax = v; }
  const lo = parseFloat(document.getElementById('roi-min').value);
  const hi = parseFloat(document.getElementById('roi-max').value);
  const { be } = getROIData();
  let sMin = Infinity, sMax = -Infinity;
  for (const v of be) { if (v < sMin) sMin = v; if (v > sMax) sMax = v; }
  const base = { dMin, dMax, lo, hi, sMin, sMax, n: be.length };
  if (Number.isFinite(lo) && Number.isFinite(hi) && lo > hi) return { ...base, state: 'inverted' };
  if (!be.length) return { ...base, state: 'no-overlap' };
// ═══════════════════════════════════════════════════
// PEAK LIST UI
// ═══════════════════════════════════════════════════
// The per-peak "Charge-correction reference (C 1s graphite)" checkbox is
// only meaningful when the user is on a C 1s spectrum AND the global
// charge-correction method is set to graphite. When either condition is
// false, the checkbox is hidden completely AND any peak that previously
// held the marker is silently unchecked, so re-entering the valid mode
// gives a clean unchecked state rather than a stale stored value.
function _isChargeRefAllowed() {
  const cm = document.getElementById('cc-method');
  if (!cm || cm.value !== 'c1s') return false;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  return !!(tab && isC1sTab(tab));
}

function _clearDisallowedChargeRef() {
  if (_isChargeRefAllowed()) return;
  for (const p of state.peaks) {
    if (p.isChargeReference) p.isChargeReference = false;
  }
  clearTimeout(_showFitSpinner._timer);
  _bgSubFitInFlight = false;
  _updateBgSubPillEnabled();
}

// Sync the Auto-Fit menu item's disabled state with the active tab.
// Called from activateTab and from ROI-input event handlers.
function _recomputeAutoFitMenuState() {
  const item = document.getElementById('auto-fit-c1s-menu-item');
  if (!item) return;
  const tab = (typeof tabManager !== 'undefined' && tabManager.activeId)
    ? tabManager._getTab(tabManager.activeId)
    : null;
  const enabled = !!tab && isC1sTab(tab);
  item.disabled = !enabled;
  if (enabled) {
    item.removeAttribute('aria-disabled');
    item.title = 'Auto-Fit C1s Graphite — one-click fit + charge correction';
  } else {
    item.setAttribute('aria-disabled', 'true');
    item.title = 'Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).';
  }
}

// Late-init for Auto-Fit menu state (in case startup runs before the
// menu item is in the DOM).
window.addEventListener('DOMContentLoaded', () => {
  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
      }
      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
    }
  } finally {
    _runningFitJobs.delete(jobId);
  }
}

async function runAutoFitC1sGraphite() {
  // Pre-conditions
  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) { notify('No active tab.', 'amber'); return; }
  if (!isC1sTab(tab)) {
    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
    return;
  }
  // OWNER FIRST: the confirmation below is an await; the tab that is active
  // when it resolves may not be the one the user asked to auto-fit.
  const fittingTab = _opOwner();
  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  // Confirmation if existing peaks
  if (state.peaks.length >= 1) {
    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
    if (!proceed) return;
    if (!_ownerActive(fittingTab)) {
      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
      return;
    }
  }

  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  const snap = _autoFitSnapshot();

  // Step 1: find graphite in raw BE
  const { be: corrBE, inten } = getROIData();
  if (!corrBE.length) {
    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
    return;
  }
  const bgI = computeBackground(corrBE, inten);
  const bgSub = inten.map((v, i) => v - bgI[i]);
  // App convention: raw = corrected + state.ccShift
  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  const rawBE = corrBE.map(b => b + curShift);
  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  if (graphiteRaw == null) {
    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
    return;
  }

  // Step 2: provisional shift (APP CONVENTION).
  const provisionalShift = graphiteRaw - 284.50;

  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);
function isC1sTab(tab) {
  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  let be;
  const isActive = typeof tabManager !== 'undefined' && tabManager && tab.id === tabManager.activeId;
  if (isActive && typeof getROIData === 'function') {
    be = getROIData().be;
  } else {
    // the SAME selection getROIData() makes, on the record's own data: each
    // bound independently open when blank, never reordered (min > max selects
    // nothing), inclusive, corrected frame (Codex round 1)
    const shift = isNaN(tab.ccShift) ? 0 : tab.ccShift;   // read as getCorrectedBE() reads state.ccShift
    const ui = tab.ui || {};
    const a = parseFloat(ui.roiMin), b = parseFloat(ui.roiMax);
    const lo = isNaN(a) ? -Infinity : a, hi = isNaN(b) ? Infinity : b;
    be = [];
    for (const v of tab.rawBE) { const c = v - shift; if (c >= lo && c <= hi) be.push(c); }
  }
  if (!be || !be.length) return false;
  let lo = Infinity, hi = -Infinity;
  for (const v of be) { if (v < lo) lo = v; if (v > hi) hi = v; }
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
  const mid = (lo + hi) / 2;
  return mid >= 270.0 && mid <= 315.0;
}

// ── Scattered-starts check (2026-09-21) ───────────────────────────────────────
// Every Run Fit with two or more unlinked components asks the server for three
// more fits of the SAME method from scattered starts. The student's result
// stays THE FIT; a solution with a lower reduced chi-square is listed beside it
// with its own areas and how far each component moved from the student's start
// (a relocated component must be visible at a glance: on a committed C 1s scan
// the better-scoring solution slid C-O 1.4 eV under the main line). Solutions
// that are not better are only counted. Measured on the lab's 202 fit targets:
rg: static/js/tab_manager.js: No such file or directory (os error 2)
templates/index.html:2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
templates/index.html:2068:                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
templates/index.html:3232:    state.rawBE = tab.rawBE;
templates/index.html:3234:    state.ccShift = tab.ccShift;
templates/index.html:3247:    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
templates/index.html:3304:      state.rawBE = []; state.rawIntensity = [];
templates/index.html:6712:function _recomputeAutoFitMenuState() {
templates/index.html:6732:  if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
1441:SUPPORT_MIN_F = 10.0
1444:def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
1460:            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}
1524:        required = f >= SUPPORT_MIN_F
requirements-dev.txt
requirements.txt
docs/superpowers/plans/2026-05-11-organize-tabs-button.md
docs/superpowers/plans/2026-09-08-per-tab-state-ownership.md
tests/test_browser_per_tab_state.py
tests/js/find_peaks_periodic_table.test.js
tests/js/per_tab_state.test.js
docs/autofit/codex/per_tab_state_r3_verdict_runA.md
docs/autofit/codex/per_tab_state_r6_verdict_runB.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runB.md
docs/autofit/codex/per_tab_state_verdict_runB.md
docs/autofit/codex/per_tab_state_r4_verdict_runA.md
docs/autofit/codex/per_tab_state_r7_verdict_runB.md
docs/autofit/codex/fp_periodic_table_picker_recheck_prompt.txt
docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runB.md
docs/autofit/codex/per_tab_state_r2_verdict_runA.md
docs/autofit/codex/fp_periodic_table_picker_review_prompt.txt
docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runA.md
docs/autofit/codex/per_tab_state_review_prompt.txt
docs/autofit/codex/per_tab_state_r5_review_prompt.txt
docs/autofit/codex/per_tab_state_verdict_runA.md
docs/autofit/codex/per_tab_state_r4_verdict_runB.md
docs/autofit/codex/per_tab_state_r3_verdict_runB.md
docs/autofit/codex/per_tab_state_r4_review_prompt.txt
docs/autofit/codex/per_tab_state_r6_verdict_runA.md
docs/autofit/codex/per_tab_state_r2_verdict_runB.md
docs/autofit/codex/per_tab_state_r7_review_prompt.txt
docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runA.md
docs/autofit/codex/per_tab_state_r7_verdict_runA.md
docs/autofit/codex/per_tab_state_r2_review_prompt.txt
docs/autofit/codex/per_tab_state_r6_review_prompt.txt
docs/autofit/codex/per_tab_state_r5_verdict_runB.md
docs/autofit/codex/per_tab_state_r3_review_prompt.txt
docs/autofit/codex/per_tab_state_r5_verdict_runA.md

exec
/bin/zsh -lc "node --test tests/js/autofit_required.test.js tests/js/autofit_zero_graphite.test.js tests/js/roi_clamp_centre_warning.test.js tests/js/per_tab_state.test.js tests/js/unsupported_components.test.js; sed -n '1440,1465p' fitting.py; sed -n '3190,3255p' templates/index.html; nl -ba tests/js/autofit_c1s_gate.test.js | tail -23" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 310ms:
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 5.187555
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
ok 2 - a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
  ---
  duration_ms: 9.291124
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 0.882614
  type: 'test'
  ...
# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
ok 4 - a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
  ---
  duration_ms: 2.328267
  type: 'test'
  ...
# Subtest: the fixture set covers both outcomes
ok 5 - the fixture set covers both outcomes
  ---
  duration_ms: 1.233958
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
ok 6 - anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
  ---
  duration_ms: 4.267404
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
ok 7 - anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
  ---
  duration_ms: 2.486296
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
ok 8 - anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
  ---
  duration_ms: 2.577605
  type: 'test'
  ...
# Subtest: anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
ok 9 - anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
  ---
  duration_ms: 1.219081
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
ok 10 - anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
  ---
  duration_ms: 1.794992
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
ok 11 - anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
  ---
  duration_ms: 1.771199
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
ok 12 - anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
  ---
  duration_ms: 1.954196
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
ok 13 - anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
  ---
  duration_ms: 1.484373
  type: 'test'
  ...
# Subtest: anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
ok 14 - anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
  ---
  duration_ms: 1.211253
  type: 'test'
  ...
# Subtest: an anchor amplitude of 0 is refused before anything is computed
ok 15 - an anchor amplitude of 0 is refused before anything is computed
  ---
  duration_ms: 1.437486
  type: 'test'
  ...
# Subtest: an anchor amplitude of -5 is refused before anything is computed
ok 16 - an anchor amplitude of -5 is refused before anything is computed
  ---
  duration_ms: 1.037865
  type: 'test'
  ...
# Subtest: an anchor amplitude of NaN is refused before anything is computed
ok 17 - an anchor amplitude of NaN is refused before anything is computed
  ---
  duration_ms: 1.000974
  type: 'test'
  ...
# Subtest: an anchor amplitude of Infinity is refused before anything is computed
ok 18 - an anchor amplitude of Infinity is refused before anything is computed
  ---
  duration_ms: 0.777682
  type: 'test'
  ...
# Subtest: a response that lacks the fitted data or the component curve cannot vouch for an anchor
ok 19 - a response that lacks the fitted data or the component curve cannot vouch for an anchor
  ---
  duration_ms: 2.913498
  type: 'test'
  ...
# Subtest: an exact fit that needs the component is supported (chi-square with it is zero)
ok 20 - an exact fit that needs the component is supported (chi-square with it is zero)
  ---
  duration_ms: 1.120931
  type: 'test'
  ...
# Subtest: removing a component that costs nothing is the definition of unsupported
ok 21 - removing a component that costs nothing is the definition of unsupported
  ---
  duration_ms: 1.047316
  type: 'test'
  ...
# Subtest: the support check precedes every write of the charge-correction inputs
ok 22 - the support check precedes every write of the charge-correction inputs
  ---
  duration_ms: 0.498173
  type: 'test'
  ...
# Subtest: the fallback "first peak" anchor is held to the same rule
ok 23 - the fallback "first peak" anchor is held to the same rule
  ---
  duration_ms: 1.62913
  type: 'test'
  ...
# Subtest: rolling back to a Custom reference shows its target field again
ok 24 - rolling back to a Custom reference shows its target field again
  ---
  duration_ms: 0.775218
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 25 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 160.215519
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 26 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 68.286323
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 27 - the known class-C holders are gone from module scope
  ---
  duration_ms: 5.132077
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 28 - async operations capture their owning record before the first await
  ---
  duration_ms: 1.825626
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 29 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.519026
  type: 'test'
  ...
# Subtest: an ROI inside the data: no hint
ok 30 - an ROI inside the data: no hint
  ---
  duration_ms: 5.357729
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 31 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 3.373351
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 32 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 2.795063
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 33 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 3.598942
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 34 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 3.071643
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 35 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 1.908307
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 36 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 2.196804
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 37 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 4.126332
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 38 - a descending acquisition behaves the same
  ---
  duration_ms: 2.253397
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 39 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 4.668148
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 40 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 1.408157
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 41 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 1.491734
  type: 'test'
  ...
# Subtest: an unsupported component: the badge warns without reporting its suppressed centre
ok 42 - an unsupported component: the badge warns without reporting its suppressed centre
  ---
  duration_ms: 2.10733
  type: 'test'
  ...
# Subtest: manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
ok 43 - manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
  ---
  duration_ms: 9.341203
  type: 'test'
  ...
# Subtest: …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
ok 44 - …and can differ by one edge point, IN EITHER DIRECTION, when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
  ---
  duration_ms: 4.898893
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 45 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 10.929456
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 46 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 6.332859
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 47 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 5.633031
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 48 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 6.953345
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 49 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 5.254613
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 50 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 15.357496
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 51 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 6.057941
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 52 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 7.274432
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 53 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 7.099141
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 54 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 2.170007
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 55 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 1.496011
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 56 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 0.834884
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 57 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 4.586068
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 58 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 5.880506
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 59 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 8.072765
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 60 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 4.039579
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 61 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.116218
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 62 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 3.314552
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 63 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 2.671279
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 64 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 3.785072
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 65 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 9.829798
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 66 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 4.864704
  type: 'test'
  ...
1..66
# tests 66
# suites 0
# pass 66
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 346.035379
# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
    return tab;
  }

  createStackTab() {
    const id = 'tab_' + Math.random().toString(36).slice(2, 9);
    const tab = {
      id,
      name: '▦ Stack ' + (_nextStackNum++),
      color: '#7a7a7a',           // inert — stack tabs render no dot
      isStack: true,
      entries: [],
      _nextColorIdx: 0,
      lineWidth: 1.5,
      verticalOffset: 0,
      // Inert spectrum-tab fields kept to satisfy existing lifecycle code paths.
      isSurvey: false, chargeVerified: true,
      rawBE: [], rawIntensity: [], ccShift: 0,
      peaks: [], nextId: 1, fitResult: null,
      markedElements: [], notes: '', sourcePath: null,
      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
            endpointAvg: '1', roiMin: '', roiMax: '',
            ccMethod: 'none', ccObs: '', ccLit: '' },
    };
    this.tabs.push(tab);
    this.activateTab(id);
    return tab;
  }

  activateTab(id) {
    if (this.activeId === id) return;
    const tab = this._getTab(id);
    if (!tab) return;
    // Cancel any armed placement mode so a click on the new tab's chart
    // isn't consumed by a placement aimed at the previous spectrum.
    if (placeMode) togglePlaceMode(placeMode);
    // Clear stale history preview from previous tab
    if (typeof _historyPreview !== 'undefined') _historyPreview = null;
    // Save current tab's live state
    this._syncActiveToRecord();
    this.activeId = id;

    // Swap global state fields — peaks uses reference sharing
    state.rawBE = tab.rawBE;
    state.rawIntensity = tab.rawIntensity;
    state.ccShift = tab.ccShift;
    state.peaks = tab.peaks;
    state.nextId = tab.nextId;
    state.fitResult = tab.fitResult;
    state.lineWidth = tab.lineWidth ?? 1.5;

    // Restore DOM form fields
    this._restoreUI(tab.ui);
    _updateUndoButtons();   // history is per tab: buttons reflect the incoming record
    const notesEl = document.getElementById('spectrum-notes');
    if (notesEl) notesEl.value = tab.notes || '';
    this._updateCCVerifiedUI(tab.chargeVerified ?? true);
    this._updateInfoBadge(tab);
    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
    // Update chi-squared display for this tab's fit result
    _applyStatDisplay(state.fitResult);
    // F1: never computed over an edited model and cached under the fit's key
    // (without a stored curve _computeRFactor evaluates the CURRENT peaks)
    if (state.fitResult && state.fitResult.rFactor == null && _statsLiveState() !== 'stale') {
      state.fitResult.rFactor = _computeRFactor(state.fitResult);
    }
    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
    58	});
    59	
    60	test('the record path makes the SAME selection getROIData() makes (Codex round 1)', () => {
    61	  const g = gate({ activeId: 'other', liveSel: [] });
    62	  // reversed bounds select nothing, exactly as the live selector does
    63	  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '295', roiMax: '280' } }), false);
    64	  // a blank bound is open on its own side only: 270-295 is C 1s
    65	  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '', roiMax: '295' } }), true);
    66	  assert.strictEqual(g({ id: 't1', rawBE: RAW, ccShift: 0, ui: { roiMin: '370', roiMax: '' } }), false);
    67	});
    68	
    69	test('every caller of the gate passes the ACTIVE tab record (menu state, charge-reference permission, the Auto-Fit run)', () => {
    70	  for (const fn of ['_recomputeAutoFitMenuState', '_isChargeRefAllowed', 'runAutoFitC1sGraphite']) {
    71	    const src = extractFn(fn);
    72	    const lookup = src.search(/const tab = [^;]*tabManager\._getTab\(tabManager\.activeId\)/);
    73	    assert.ok(lookup >= 0, fn + ': the tab is looked up by tabManager.activeId');
    74	    assert.ok(src.indexOf('isC1sTab(tab)') > lookup, fn + ': and that tab is the one judged');
    75	    assert.ok(!/\btab\s*=(?!=)/.test(src.slice(lookup + 10, src.indexOf('isC1sTab(tab)'))), fn + ': not reassigned in between');
    76	  }
    77	  // and the ROI fields refresh the menu on every keystroke
    78	  assert.match(html, /id="roi-min"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
    79	  assert.match(html, /id="roi-max"[^>]*oninput="updatePlot\(\);_recomputeAutoFitMenuState\(\)"/);
    80	});

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), assert=require('\\''assert'\\''), {performance}=require('\\''perf_hooks'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''), lines=html.split('\\''\\n'\\'');
function extract(name){const start=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l));let d=0,seen=false;for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;seen=true;}else if(c==='\\''}'\\'')d--;}if(seen&&d===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}throw Error(name);}
const state={}, fields={'\\''roi-min'\\'':{},'\\''roi-max'\\'':{}}, document={getElementById:id=>fields[id]}, tm={activeId:'\\''active'\\''};
const f=new Function('\\''state'\\'','\\''document'\\'','\\''tabManager'\\'',extract('\\''getCorrectedBE'\\'')+'\\''\\n'\\''+extract('\\''getROIData'\\'')+'\\''\\n'\\''+extract('\\''isC1sTab'\\'')+'\\''\\nreturn {getROIData,isC1sTab};'\\'')(state,document,tm);
const bounds=['\\'''\\'','\\''NaN'\\'',NaN,undefined,null,'\\''270'\\'','\\''280'\\'','\\''295'\\'','\\''370'\\'','\\''420'\\'','\\''Infinity'\\'','\\''-Infinity'\\'','\\''284.5'\\'','\\''garbage'\\'','\\''  '\\''];
const shifts=[0,100,200,NaN,Infinity,-Infinity,undefined,null,'\\''100'\\'','\\''NaN'\\'','\\'''\\'',-100];
const arrays=[[],[284.5],Array.from({length:301},(_,i)=>420-i*.5),[NaN,270,284.5,295,Infinity,-Infinity],[300,280,290],[100,200],[NaN]];
let n=0;
for(const rawBE of arrays)for(const ccShift of shifts)for(const a of bounds)for(const b of bounds){state.rawBE=rawBE;state.rawIntensity=rawBE.map(()=>1);state.ccShift=ccShift;fields['\\''roi-min'\\''].value=a;fields['\\''roi-max'\\''].value=b;const tab={id:'\\''inactive'\\'',rawBE,ccShift,ui:{roiMin:a,roiMax:b}};const inactive=f.isC1sTab(tab);tab.id='\\''active'\\'';assert.strictEqual(inactive,f.isC1sTab(tab),JSON.stringify({rawBE,ccShift,a,b}));n++;}
console.log('\\''Actual live/record selector parity combinations:'\\'',n);
for(const size of [100000,1000000]){const tab={id:'\\''inactive'\\'',rawBE:Array.from({length:size},(_,i)=>280+20*i/size),ccShift:0,ui:{roiMin:'\\'''\\'',roiMax:'\\'''\\''}};const t=performance.now();assert.strictEqual(f.isC1sTab(tab),true);console.log('\\''Record points:'\\'',size,'\\''elapsed ms:'\\'',(performance.now()-t).toFixed(2));}
function callerCheck(src){const lookup=src.search(/const tab = ["'^;]*tabManager'"\\._getTab\\(tabManager\\.activeId\\)/);return lookup>=0&&src.indexOf('\\''isC1sTab(tab)'\\'')>lookup&&"'!/'"\\btab\\s*=(?"'!=)/.test(src.slice(lookup+10,src.indexOf('"'\\''isC1sTab(tab)'\\'')));}
for(const name of ['\\''_recomputeAutoFitMenuState'\\'','\\''_isChargeRefAllowed'\\'','\\''runAutoFitC1sGraphite'\\'']){const src=extract(name);console.log(name,JSON.stringify({original:callerCheck(src),simpleInactive:callerCheck(src.replace('\\''tabManager._getTab(tabManager.activeId)'\\'',\"tabManager._getTab('\\''inactive'\\'')\")),inactivePreferred:callerCheck(src.replace('\\''tabManager._getTab(tabManager.activeId)'\\'',\"tabManager._getTab('\\''inactive'\\'') || tabManager._getTab(tabManager.activeId)\"))}));}
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 201ms:
Actual live/record selector parity combinations: 18900
Record points: 100000 elapsed ms: 5.88
Record points: 1000000 elapsed ms: 49.73
_recomputeAutoFitMenuState {"original":true,"simpleInactive":false,"inactivePreferred":true}
_isChargeRefAllowed {"original":true,"simpleInactive":false,"inactivePreferred":true}
runAutoFitC1sGraphite {"original":true,"simpleInactive":false,"inactivePreferred":true}

codex
The live and record paths agreed across 18,900 combinations; a million-point record completed in about 50 ms. I also found a gap in the caller test: it rejects a direct inactive-tab lookup, but passes an expression that prefers an inactive tab and only falls back to `activeId`. All three production callers currently use the correct lookup.

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), vm=require('\\''vm'\\''), assert=require('\\''assert'\\''),path=require('\\''path'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\''),lines=html.split('\\''\\n'\\'');
function extract(name){const start=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l));let d=0,s=false;for(let i=start;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;s=true;}else if(c==='\\''}'\\'')d--;}if(s&&d===0)return lines.slice(start,i+1).join('\\''\\n'\\'');}}
const state={},fields={'\\''roi-min'\\'':{},'\\''roi-max'\\'':{}},document={getElementById:id=>fields[id]},tm={activeId:'\\''active'\\''};
const instrumented=extract('\\''isC1sTab'\\'').replace('\\''return false;'\\'','\\''return [];'\\'').replace('\\''if ("'!be || !be.length) return false;'"'\\'','\\''return be;'\\'');
const api=new Function('\\''state'\\'','\\''document'\\'','\\''tabManager'\\'',extract('\\''getCorrectedBE'\\'')+'\\''\\n'\\''+extract('\\''getROIData'\\'')+'\\''\\n'\\''+instrumented+'\\''\\nreturn {getROIData,isC1sTab};'\\'')(state,document,tm);
const bounds=['\\'''\\'','\\''NaN'\\'',NaN,undefined,null,'\\''270'\\'','\\''280'\\'','\\''295'\\'','\\''370'\\'','\\''420'\\'','\\''Infinity'\\'','\\''-Infinity'\\'','\\''284.5'\\'','\\''garbage'\\'','\\''  '\\''],shifts=[0,100,200,NaN,Infinity,-Infinity,undefined,null,'\\''100'\\'','\\''NaN'\\'','\\'''\\'',-100],arrays=[[],[284.5],Array.from({length:301},(_,i)=>420-i*.5),[NaN,270,284.5,295,Infinity,-Infinity],[300,280,290],[100,200],[NaN]];
let n=0;
for(const rawBE of arrays)for(const ccShift of shifts)for(const a of bounds)for(const b of bounds){Object.assign(state,{rawBE,ccShift,rawIntensity:rawBE.map(()=>1)});fields['\\''roi-min'\\''].value=a;fields['\\''roi-max'\\''].value=b;assert.deepStrictEqual(api.isC1sTab({id:'\\''inactive'\\'',rawBE,ccShift,ui:{roiMin:a,roiMax:b}}),api.getROIData().be);n++;}
console.log('\\''Exact selected-array parity:'\\'',n);
const originalTest=fs.readFileSync('\\''tests/js/autofit_c1s_gate.test.js'\\'','\\''utf8'\\'');
(async()=>{
for(const name of ['\\''_recomputeAutoFitMenuState'\\'','\\''_isChargeRefAllowed'\\'','\\''runAutoFitC1sGraphite'\\'']){
const mutated=extract(name).replace('\\''tabManager._getTab(tabManager.activeId)'\\'',\"tabManager._getTab('\\''inactive'\\'') || tabManager._getTab(tabManager.activeId)\");
const mutatedHtml=html.replace(extract(name),mutated);
let passes=0;
vm.runInNewContext(originalTest,{__dirname:path.resolve('\\''tests/js'\\''),require:id=>id==='\\''node:fs'\\''?{readFileSync:()=>mutatedHtml}:id==='\\''node:test'\\''?{test:(label,fn)=>{fn();passes++;}}:require(id)});
let judged;
const tabs={active:{id:'\\''active'\\''},inactive:{id:'\\''inactive'\\''}}, menu={removeAttribute(){},setAttribute(){}};
const fn=new Function('\\''state'\\'','\\''document'\\'','\\''tabManager'\\'','\\''isC1sTab'\\'','\\''notify'\\'',mutated+'\\''\\nreturn '\\''+name+'\\'';'\\'')({rawBE:[284.5]}, {getElementById:id=>id==='\\''cc-method'\\''?{value:'\\''c1s'\\''}:menu},{activeId:'\\''active'\\'',_getTab:id=>tabs[id]},tab=>{judged=tab.id;return false;},()=>{});
await fn();
assert.strictEqual(judged,'\\''inactive'\\'');console.log(name+'\\'': '\\''+passes+'\\''/5 actual test callbacks pass; runtime judges '\\''+judged);
}
})().catch(e=>{console.error(e);process.exitCode=1;});
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 56ms:
Exact selected-array parity: 18900
_recomputeAutoFitMenuState: 5/5 actual test callbacks pass; runtime judges inactive
_isChargeRefAllowed: 5/5 actual test callbacks pass; runtime judges inactive
runAutoFitC1sGraphite: 5/5 actual test callbacks pass; runtime judges inactive

exec
/bin/zsh -lc 'git status --short; git diff --check 895f323..HEAD -- templates/index.html tests/js/autofit_c1s_gate.test.js docs/findings/noise-floor-occupancy/README.md; git log --oneline --merges 07e0839..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-o006Putk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uXwUS9iA' (errno=Operation not permitted)
?? docs/autofit/codex/f3_c1s_gate_r2_verdict_runA.md
?? docs/autofit/codex/f3_c1s_gate_r2_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ydjS4y5w' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-AOdHIhHZ' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hWbtoXJG' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-j5lsyySU' (errno=Operation not permitted)

exec
/bin/zsh -lc "rg -n 'sqrt\\(np.maximum|maximum\\(.*noise_floor|noise_floor.*sqrt' autofit/engine.py autofit/noise.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
autofit/engine.py:1411:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:1856:        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
autofit/engine.py:2014:    sigma = np.sqrt(np.maximum(y, noise_floor))
autofit/engine.py:2240:    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \

exec
/bin/zsh -lc "node -e '
function support(y,fit,c){let cw=0,wo=0;for(let i=0;i<y.length;i++){const w2=1/Math.max(y[i],1),r=y[i]-fit[i];cw+=w2*r*r;wo+=w2*(r+c[i])**2;}return {delta:wo-cw,f:(wo-cw)/cw};}
for(const [name,y,fit,c] of [['\\''LR'\\'',[100,100],[90,110],[40,40]],['\\''floor'\\'',[1,100],[.99,90],[.9,22]]])for(const scale of [1,.1])console.log(name,scale,support(...[y,fit,c].map(a=>a.map(v=>v*scale))));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free
 succeeded in 0ms:
LR 1 { delta: 32, f: 16 }
LR 0.1 { delta: 3.1999999999999997, f: 15.999999999999998 }
floor 1 { delta: 10.068000000000001, f: 10.066993300669935 }
floor 0.1 { delta: 0.9322800000000002, f: 9.322706772932273 }

codex
No BLOCKER or MAJOR found in the shipped gate. Two MINORs remain:

1. **MINOR — caller test still permits judging an inactive record.** [autofit_c1s_gate.test.js:72](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:72). Replacing each caller’s lookup with `_getTab('inactive') || _getTab(tabManager.activeId)` leaves all five tests passing, while execution judges the inactive record. I reproduced this separately for all three callers. Add a behavioral assertion on the record passed to `isC1sTab`. Current production callers are correct.

2. **MINOR — parked write-up retains contradictory scale-invariance claims.** [README.md:33](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:33) still says both variants are scale-free, contradicting the correction below. The documented LR example reproduces: rescaling by 0.1 changes its statistic from 32 to 3.2. The blanket claim for F at [line 84](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:84) also needs round 1’s variance-floor qualification: with `y=[1,100]`, fit `[0.99,90]`, component `[0.9,22]`, and one free parameter, the retained floor makes F change **10.067 → 9.323** under that rescaling, flipping support. Remove the stale claim and qualify F’s invariance.

The record-path fix passed **18,900 exact selected-array comparisons** against the actual `getROIData()`/`getCorrectedBE()`, covering blank, NaN, reversed, equal and infinite bounds; finite, NaN and infinite shifts; and empty/nonfinite data. A million-point record completed in approximately **50 ms**, without argument-limit failure. **71 focused JavaScript tests passed.**

The revised stress-case explanation matches round 1. Starting from F, separating unsupported components from orphans, and making mismatch reporting independent of the compensating component remains a sound direction. The complete parked Python suites were not rerun. No files changed.

VERDICT: GO
tokens used
51,451
No BLOCKER or MAJOR found in the shipped gate. Two MINORs remain:

1. **MINOR — caller test still permits judging an inactive record.** [autofit_c1s_gate.test.js:72](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/tests/js/autofit_c1s_gate.test.js:72). Replacing each caller’s lookup with `_getTab('inactive') || _getTab(tabManager.activeId)` leaves all five tests passing, while execution judges the inactive record. I reproduced this separately for all three callers. Add a behavioral assertion on the record passed to `isC1sTab`. Current production callers are correct.

2. **MINOR — parked write-up retains contradictory scale-invariance claims.** [README.md:33](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:33) still says both variants are scale-free, contradicting the correction below. The documented LR example reproduces: rescaling by 0.1 changes its statistic from 32 to 3.2. The blanket claim for F at [line 84](/Users/skyefortier/xps-app/.claude/worktrees/fix-noise-floor-scale-free/docs/findings/noise-floor-occupancy/README.md:84) also needs round 1’s variance-floor qualification: with `y=[1,100]`, fit `[0.99,90]`, component `[0.9,22]`, and one free parameter, the retained floor makes F change **10.067 → 9.323** under that rescaling, flipping support. Remove the stale claim and qualify F’s invariance.

The record-path fix passed **18,900 exact selected-array comparisons** against the actual `getROIData()`/`getCorrectedBE()`, covering blank, NaN, reversed, equal and infinite bounds; finite, NaN and infinite shifts; and empty/nonfinite data. A million-point record completed in approximately **50 ms**, without argument-limit failure. **71 focused JavaScript tests passed.**

The revised stress-case explanation matches round 1. Starting from F, separating unsupported components from orphans, and making mismatch reporting independent of the compensating component remains a sound direction. The complete parked Python suites were not rerun. No files changed.

VERDICT: GO
