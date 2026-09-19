# How weakly determined are these decompositions? (standing findings, 2026-09)

Findings about XPS peak fitting as a practice, measured on this code and
this lab's data. They are not bug reports. A converged fit with a low
residual is not evidence that the decomposition is right or unique.

## 1. The background choice dominates the component-area error (Codex audit)

Source: Codex scientific audit of 2026-09-08, branch
`codex/scientific-code-audit-2026-09` (`docs/audit-2026-09-08.md`,
"Independent recovery and sensitivity results"; evidence
`docs/repairs-2026-09-08/sensitivity.json`). 72 fits of a constructed
two-Gaussian truth on a KNOWN integral background, three Poisson-noise
seeds, two windows, two starts, widths free or fixed at truth. Every one
of the 72 reports solver success.

| background used in the fit | widths | largest component-area error |
|---|---|---:|
| true (known) | free | 9.49 % |
| true (known) | fixed at truth | 2.68 % |
| Shirley estimated from data | free | 23.30 % |
| Shirley estimated from data | fixed at truth | 9.98 % |
| linear (misspecified) | free | 76.33 % |
| linear (misspecified) | fixed at truth | 9.44 % |

Convergence says nothing about area accuracy; the background model
dominates; fixing widths helps only when the fixed value is right.

## 2. Two optimisers, one model, two decompositions — and the server was the one in a local minimum (unit W1, 2026-09-18)

Committed project `1-GTA UCl4-graphite one set of U doublets.proj.zip`,
tab `C1s Scan_4`, six-component C 1s model propagated from `C1s Scan`
(Batch Fit start), Shirley background, identical Poisson weighting in
both engines.

| route | χ²ᵣ | "Adventitious 1" amplitude | note |
|---|---:|---:|---|
| server, Trust-Region (`least_squares`, the UI default), from the batch start | 19.056 | 3771 | converged, `success: true` |
| local engine (weighted LM), from the batch start | 18.218 | 4.5 | converged |
| server, Trust-Region, RESTARTED from the local solution | 18.212 | 0.0 | converged |
| server, Levenberg–Marquardt (`leastsq`), from the batch start | 18.212 | 0.0 | converged |
| server, basin-hopping, from the batch start | 18.212 | 0.0 | converged |

Component areas differ by up to 100 % and atomic fractions by 15
percentage points between the 19.06 and the 18.21 solutions.

What it shows:

- **The server's answer was not "the" answer.** Its default method stopped
  in a local minimum; three other routes agree on a lower χ²ᵣ. "Compare
  with Run Fit" is not a comparison with ground truth.
- **The better solution removes a component** (amplitude → 0). The data on
  that scan do not support six components; the model is over-specified
  there, which is exactly when decompositions become non-unique.
- Both solutions were reported as converged fits with acceptable-looking
  residuals. Nothing in either engine's output flagged the ambiguity.
- Practical consequence: when Batch Fit and Run Fit disagree materially,
  neither is presumed right. Re-run with a second method (Levenberg–
  Marquardt or basin-hopping) and look for a component being driven out.

**Frequency (measured 2026-09-19, 202 targets from all committed projects,
three server methods from the same start; generator, runner, analyser and
raw results in `scripts/optimizer_disagreement_*` and
`docs/findings/optimizer-disagreement/`):** the methods disagree materially
(> 1 pp of area fraction) on 39 of 202 targets (19 %); the UI default is
not the best of the three on 18 (8.9 %) and leaves a student more than 5 pp
from the best answer on 8 (4.0 %) — all 8 from not-yet-fitted starts (8 of
95, 8.4 %), none of the 107 re-fits of a saved solution, and 6 of the 8
from one project. Scan_4's "best solution removes a component" pattern is
the exception (1 case); most disagreements are different partitions among
overlapping components. No start-model feature separates the risky fits in
this dataset beyond "multi-component C 1s model". Full report:
`docs/findings/optimizer-disagreement/REPORT.md`.

Together with §1: on real C 1s data the decomposition can move by tens of
percent with the background choice AND by up to 100 % with the optimiser's
path, all under "converged". This is the argument for visible assumptions,
per-fit sensitivity checks, and never reading a low residual as proof.

Follow-ups this suggests (not scheduled): a multi-start or second-method
check that flags non-unique fits; flagging a component whose amplitude is
driven to its bound as "not supported by the data" instead of reporting its
centre/width; `differential_evolution` raises on the mirror's unbounded
specs (check what the UI sends before relying on it).

## 3. DECIDED 2026-09-18 — the amplitude lower bound (owner decision; reasoning kept below)

Local engine floor: 1. Server (`fitting.py`, `amplitude_min` default): 0.
A fixed-shape peak of true amplitude 0.1 converges to 1 locally and 0.1 on
the server (~900 % area difference; Codex W1 round 1). Do NOT assume the
server is right:

- **Against 0:** at amplitude 0 the component's centre and width are
  unidentifiable; the Jacobian columns vanish, the covariance is singular,
  and any reported σ for that component is meaningless. §2's better
  solution sits exactly there and still reports a centre and a width for
  the vanished peak. A fit that silently parks a component at 0 is
  reporting a model with fewer components under the old name.
- **Against 1:** the floor is in intensity UNITS. One count is negligible
  on a 40 000-count line and substantial on CPS data where a real weak
  satellite can be below 1. A fixed floor of 1 biases weak components
  upward by an amount that depends on how the instrument reports
  intensity, and it hides the "this component is not needed" signal.
- **Options to weigh:** (a) a unit-free floor tied to the noise at the
  component's position (e.g. a fraction of √(local intensity)); (b) allow
  0 in both engines but treat "amplitude at its lower bound" as an explicit
  outcome — flag the component as not supported by the data, exclude its
  centre/width/σ from results and quantification, and say so in exports;
  (c) keep a positive floor but make it relative to the largest peak.
- **Recommendation (not a decision):** (b), with the flag carried by the
  acceptance rule, because it turns the degenerate case into information
  instead of hiding it behind either bound. Whatever is chosen applies to
  BOTH engines; parity with a wrong bound is not an improvement.

**Decision (Skye, 2026-09-18): option (b), reasoning intact.** Allow zero
in BOTH engines, and treat "amplitude at its lower bound" as an explicit
outcome: flag the component as unsupported by the data and suppress its
centre, width and σ (results, Quantify, exports, saves). "Reporting a
centre and width for a vanished peak is precisely the class of overclaim
this project exists to remove." To be implemented in the unit that follows
the optimiser-disagreement frequency measurement, not before. Until then
the difference stays listed among the reasons a local result is a starting
point.

## 4. CONFIRMED BUG (not yet fixed) — Differential Evolution cannot run from the UI

Checked 2026-09-18 with the shipped `peakToBackendSpec` and the real
`/api/fit` route: the UI sends `amplitude_min: 0` and never an
`amplitude_max`, so every free amplitude is unbounded above, and lmfit's
`differential_evolution` requires finite bounds for every varying
parameter. Result for any model with a free amplitude (i.e. essentially
every fit): HTTP 422, "Fit failed — see server log for details"; server
log: `ValueError: differential_evolution requires finite bound for all
varying parameters`. Before unit A0 that error fell through silently to
the broken local fitter, which returned the starting model as "Fit
complete (local)" under a "server did not respond" overlay; since A0 the
user sees a red "Fit failed". The Method dropdown therefore offers an
option that cannot work. Fix options (own unit): send a finite
`amplitude_max` (e.g. a multiple of the ROI maximum) for DE, or remove DE
from the dropdown. Repro: the commands in this section's commit message.
