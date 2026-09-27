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
