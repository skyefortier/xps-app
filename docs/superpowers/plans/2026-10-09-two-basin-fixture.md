# Two-basin fit fixture inside its basins (owner, logged 2026-10-01, promoted 2026-10-04, run 2026-10-09)

Owner, 2026-10-09: "the two-basin fixture unit (promoted earlier): fixture clearly inside
one basin, remove the _legacy_line and v1-seed pins, restore whole-fit reproducibility
tests." PROGRESS.md "NEXT" carries the full requirement (what Codex impl round 12 named the
new fixture must re-establish, and the tests susceptible to the old one).

## 1. Why the old fixture failed

`tests/test_scattered_starts.py::_two_basin_problem` was found by a probe and sat ON a basin
boundary. Measured on main 853fed6 (the `_legacy_line` pin removed for the probe):

| linear background | student fit chi2r | certificate move | scattered starts |
|---|---|---|---|
| exact (fitting._line_through) | 1.367 | 2.20 eV — the "fit" was not a minimum | 3 same, 3 not better, no alternative |
| floating point (the pin) | 2.875 | 0.14 eV | 1 same, 2 alternatives at 1.367 |

One rounding step of the background at 3 of 300 points chose the basin. Each request also
took ~27-32 s.

## 2. What "inside its basins" has to mean here — and why the fixture has no perturbed restarts

First search (n_perturb 3, as the page sends): even the best candidates changed their
student fit under a start change of 1e-9 relative. The cause is the perturbed restarts:
each redraws every varying parameter by ±15 % from the fitted point (centres clamped into
their ±2 eV window), so on a model with several minima a restart CAN start near a basin
boundary (nothing guarantees it, but on every candidate tried one did), and the fitted
point's own convergence jitter then decides which restart wins. That is
the several-minima property itself (CLAUDE.md, "Determinacy": the 29 pp synthetic case), not
a property of the scattered-starts, certificate or equality machinery these tests exercise.
The cost, stated: these tests' reproducibility claims now cover a request WITHOUT perturbed
restarts; the perturbed-restart path keeps its own coverage (the `_well_posed` tests with `KW`,
tests/test_fit_reproducibility.py). So the fixture's request is `TWO_BASIN_KW = dict(background_method="linear", n_perturb=0)`;
every other test keeps `KW` (n_perturb 3).

FINDING FOR PRODUCTION (owner, 2026-10-09): that a perturbed restart landed near a basin
boundary on EVERY candidate tried means real multi-minimum spectra can do the same in
production — the page's Run Fit sends n_perturb 3, so two presses of the same request on such
a spectrum can resolve to different minima (CLAUDE.md "Reproducibility": accepted and
disclosed, 2026-09-21). It is covered by the scattered-starts line, which exists to show
exactly that a decomposition is not unique. No new work.

"Inside its basins" is then two checks, with the request seed held fixed (the counts enter
the seed):
- rounding level, STRICT — the floating-point line instead of the exact one, ulps of 5 counts
  (three draws), start values changed by 4 ulps (both signs), a repeat: the same response
  within rounding (`tests/fit_equality.assert_same_fit`, every quantity on its own scale);
- basin level — start values changed by 1e-6 (both signs): the same solutions (counts,
  centres within 0.01 eV, alternatives' areas within 0.1 pp). (A 1e-9 change is NOT a
  rounding-level change: it moves the scattered starts' own convergence jitter — by 3e-7
  relative in an alternative's chi2r, beyond `assert_same_fit`'s chi2 tolerance of 1e-7
  (10·ftol) — without changing a basin.)

## 3. The new fixture

`scripts/two_basin_fixture_search.py` (the committed generator: grid, criteria, both
checks, the selection). Main 284.5 eV, a weak shoulder at 285.25, a line at 286.7, a
satellite at 288.8; the student starts "shoulder" at 285.2 and "sat" at 288.5. 75 candidates,
15 qualify, 7 robust. SELECTION: of the robust candidates, those whose alternatives keep every
centre off its ±2 eV bound (an alternative shifted by exactly 2.0 eV is a start pushed to the
wall, not a decomposition) — 4 — the largest student chi2r: shoulder amplitude 1400, start
285.2, noise seed 2 (gap to its alternative 33.3; the other three 3.2-3.8). Three robust
candidates (gaps 38.2, 33.3, 29.2) each list an alternative on a bound
(Codex round 1: an earlier draft said "the largest chi2 gap of the robust ones", which it is
not). The chosen fixture:
- the student's Levenberg-Marquardt fit: chi2r 46.9, certified by the certificate without a
  move ("sat" covers the 286.7 line, the satellite unfitted);
- six scattered starts: 4 reach the better decomposition (chi2r 13.7: "shoulder" moved 1.49 eV
  onto the 286.7 line, an area moved 11 pp), 1 the student's minimum, 1 a not-better minimum;
- 0.3 s per request (was ~30 s).

## 4. Changes

- `tests/test_scattered_starts.py`: the new `_two_basin_problem` and `TWO_BASIN_KW`; every
  two-basin request uses it; `test_the_starts_are_a_pure_function_of_the_request` again
  compares the WHOLE response (`assert_same_fit`) as well as the seed and the four starting
  points; NEW `test_the_two_basin_fixture_is_inside_its_basins` pins §2's strict checks (the
  floating-point line lives there as a local helper, no longer as a pin); the API test
  uploads full precision (`repr` of each double, as the page does since 2026-10-03) so its
  request seed is the fixture's.
- `tests/test_fit_equality.py`: every two-basin request uses `TWO_BASIN_KW`; the v1-seed pin
  (1228785762) in `test_a_scattered_start_objective_is_compared_at_the_objective_scale` is
  removed — the fixture's own request draws a not-better start.
- `tests/test_runfit_certificate.py`:
  `test_a_continuation_that_relocates_a_component_by_more_than_1_ev_is_reported` is now
  DELIBERATE: one line, started 2 eV from it, and only the student's Levenberg-Marquardt run
  cut off after 6 evaluations (`lmfit.Model.fit` wrapped for `method="leastsq"`); the
  certificate's Trust-Region restarts run uncapped into the line's single minimum: certified
  in 2 restarts, centre moved 1.94 eV, optimiser flag false. (Loose `ftol` / `xtol`, MINPACK's
  own `maxfev` and a centre started on its bound were tried: Levenberg-Marquardt reached the
  minimum anyway; `max_nfev` in the request caps the certificate's restarts too and leaves
  fits uncertified.) It replaces the reliance on Levenberg-Marquardt stalling by chance on
  the old fixture (CLAUDE.md updated).
- `tests/_legacy_line.py` deleted; no module pins the background arithmetic.

## 5. Verification

- The robustness test FAILS on the old fixture (both by its minimum check and, with that
  removed, by its rounding-level checks).
- The three modules: 76 passed; with `tests/test_fit_reproducibility.py` first and in reverse
  order, 120 / 120 each (the old flake depended on what ran earlier in the process).
- `scripts/two_basin_fixture_search.py` reproduces the selection: 75 candidates, 15 qualify,
  7 robust (incl. the chosen one).
- Full suites at the commit: see its message.
