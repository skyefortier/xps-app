# Do fits stop before the minimum? Scope check for Unit A (2026-09-28)

Owner, Unit A: "Judge convergence by whether the refit actually reached the
minimum, not by the optimiser's success flag … SCOPE CHECK FIRST: does Run
Fit, or the scattered-starts check, share the ~30-evaluation early stopping?"

## Find Peaks: where the "~30 evaluations" comes from

It is not MINPACK stopping early from a cold start. `autofit.engine.fit_candidate`
fits with `leastsq`; when that fit FAILS (the 18 000-evaluation cap) it makes
ONE warm restart from the exit point with a 2 000-evaluation budget and takes
the restart's result if its `success` flag is set. From a stalled point that
restart ends on MINPACK's `xtol` test in ~30 evaluations and reports success.
Example (8-JT C1s Scan_7, MG2, stability refit 0): the cold `leastsq` fit stalls
at χ²ᵣ 37.6 after 18 000 evaluations; the warm restart "succeeds" there in 30;
`least_squares` from the same start reaches χ²ᵣ 5.21 in 507. The code comment
assumes the failed fit had already reached the minimum; here it had not.

## Run Fit and the scattered-starts check

`scripts/fit_termination_scope.py` runs every one of the 202 committed targets
through `/api/fit` exactly as the page sends it (3 perturbed restarts, 3
scattered starts), intercepts every lmfit fit, and refines each result from its
end point with a fresh `least_squares` fit (same model, data, weights, bounds).
A descent from a minimum cannot lower χ² beyond the optimiser's stopping sliver;
from a point short of it, it does. Summary: `scripts/fit_termination_scope_analyze.py`.

| (success-flagged fits; χ² drop on refinement) | Trust-Region (page default) | Levenberg-Marquardt |
|---|---|---|
| **the fit returned to the student** | 202: drop > 1e-6 on 8, > 1e-3 on 5, > 1 % on 2 (5.7 %, 3.8 %) | 196: > 1e-6 on 32, > 1 % on 5, > 10 % on 1 (26 %, 7205f2094254) |
| perturbed restarts | 498: > 10 % on 162 | 576: > 10 % on 198 |
| scattered starts | 532: > 10 % on 29 | 480: > 10 % on 17 |
| scattered starts flagged failed | 2 (0 at a minimum) | 36 (1 at a minimum) |

Consequences: the student's result stops short on 8 / 202 (TR) and 32 / 196
(LM) targets; the perturbed restarts often "succeed" far from a minimum (they
compete by χ², so a poor one loses — but the fit it would have found is lost);
a scattered start that "succeeds" short of its minimum is counted as reaching /
not beating the fit, so the panel's counts and alternatives are affected.

## What a certificate can and cannot be

A strict rule — "a fresh descent from the end point finds no lower χ²" — would
never certify: at genuine minima a restart almost always shaves off a sliver
(TR: of 1 232 success-flagged fits only 27 refine to exactly the same χ²; 513
drop by ≤ 1e-9, 362 by 1e-9 – 1e-6). The sliver is the optimiser's own stopping
rule at work (relative χ² change ftol: 1e-8 TR, 1.5e-8 LM). The only constant
that can separate "stopped at the minimum" from "stopped short" without
introducing a new one is that ftol itself — dimensionless, not data-scaled.
Measured with it: TR returned fits exceeding their own ftol on refinement 11 /
202; LM 88 / 196; all success-flagged fits 374 / 1 232 (TR), 888 / 1 252 (LM).
