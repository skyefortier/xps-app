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

## The decision (owner)

- **F** keeps ONE definition of "supported" across the app (Find Peaks would
  judge components exactly as Run Fit's "not supported by the data" does), but
  in a grossly mis-modelled fit it declares real components absent and can
  turn an honest "conditional" answer into a clean one.
- **LR** keeps today's behaviour on every gate and the honesty case; its
  statistic differs from the server's support verdict, so after "Apply" a
  component Find Peaks counted as occupied could still read "not supported"
  in Run Fit's results on a very badly fitted model (the two agree whenever
  χ²ᵣ ≈ 1).

**Recommendation: LR.** Occupancy asks "did the fit put something real
here", which is a question about the signal against counting noise, not
against the model's own misfit; normalising by the misfit makes the answer
depend on how wrong the rest of the model is, which is exactly what the
honesty tier exists to report. Measured: LR changes nothing on any gate; F
breaks the honesty contract.

To apply the chosen variant: `git apply docs/findings/noise-floor-occupancy/variant_<X>.patch`
on this branch, then the full suite, the gated suite (`RUN_AUTOFIT_GATE=1`)
and Codex ×2. The `test_methods_seam` detectability assertion and the schema
round-trip fixture already accept both variants' status strings.
