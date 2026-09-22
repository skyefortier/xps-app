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

**Correction and extension (2026-09-19, same day).** The run above called
`run_fit` with `n_perturb=0`; the page's Run Fit sends `n_perturb: 3` (three
refits from a random ±15 % perturbation, best χ²ᵣ kept), so it did not
measure the shipped request. Re-measured with `n_perturb: 3`, Trust-Region
and LM, five repeats each because the perturbation is unseeded
(`REPORT_perturb3.md`, 2 020 fits). The headline barely moves: the shipped
default is more than 5 pp from the best known solution in 4.2 % of Run Fit
outcomes (7.8 % of not-yet-fitted starts, 0.9 % of saved-solution re-fits —
one re-fit target, 1-GTA C1s Scan_0, now counts because an LM perturbation
found a lower minimum than any first-run method). Two new facts:

- **Run Fit is not repeatable.** On 8 of 202 targets the identical request
  gives area fractions that differ by more than 1 pp between repeats
  (8-JT C1s Scan_6: χ²ᵣ 70.6, 18.5, 70.6, 38.3, 18.5 from five presses).
- **Trust-Region and LM are not independent.** Paired as a cross-check they
  flag only 25 of the 42 outcomes (60 %) where the default is more than
  5 pp off; in the rest both stop in the same minimum (8-JT C1s Scan_1:
  χ²ᵣ 17.55 from both, every repeat, against 12.30). Taking the better of
  the pair lowers the not-yet-fitted off-rate from 7.8 % to only 6.3 %, and
  half of what remains is unflagged — "two methods agree" would be false
  reassurance there.

A different START is a more independent second opinion than a different
local method (`REPORT_starts.md`, 2 222 fits): the better of the default
and 3 Trust-Region fits from scattered starts (amplitude ×/÷ 3, width
×/÷ 1.5, free centres ± 0.5 eV, shape parameters re-drawn inside their
bounds; median 1.8 s for ten) lowers the not-yet-fitted off-rate to 3.2 %,
with no false alarm at 5 pp in 968 outcomes; 5 or 10 starts add nothing at
5 pp. Moving at-bound shape parameters inward (7 of the 9 bad targets start
one on a bound, against 45 of 193 others) changes nothing by itself. Four
targets defeat ten scattered starts.

**"Lowest χ²ᵣ" is not "the right fit".** On 8-JT C1s Scan_1 basin-hopping
reached χ²ᵣ 12.30 by moving the C–O component 1.47 eV (inside the server's
default ± 2 eV centre window) to sit under the main line as a second broad
carbon component. The default's 17.55 keeps every component where the
student put it. Neither is established; the data do not determine this
five-component model inside those windows. A check of this kind can show
that a decomposition is not unique; it cannot say which one is correct.

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

## 4. FIXED 2026-09-20 — Differential Evolution could not run from the UI

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

**Fixed and deployed 2026-09-20** (branch `fix-de-finite-bounds`, Codex GO ×2
at round 10). For that method only, each candidate is searched inside
generated limits, refined by `least_squares` under the request's own bounds,
and competes with a plain `least_squares` fit from the same start, so it is
never worse than the default method from the same start; generated limits
are never reported or stored. Mechanism and measurements: CLAUDE.md,
"Fitting Algorithm → Backend".

## 5. Owner decisions, 2026-09-20 (after the correction above)

- The second opinion is SCATTERED STARTS of the student's own method, not a
  second method (Trust-Region and LM are not independent: §2).
- The student's method result REMAINS THE FIT. Lower-χ²ᵣ solutions appear
  beside it as alternatives with their own areas and their centre
  displacements from the student's start. The app presents evidence; the
  chemist decides; it never substitutes a different chemical interpretation
  because it scored better (8-JT C1s Scan_1).
- Agreement is worded "N starts reached the same solution", never as
  certification; no "best of N" claim.
- First, ahead of that unit: SEED the `n_perturb` perturbation from the
  request, so identical requests are byte-identical across presses, sessions
  and machines.
- Own small unit: Auto-Fit C1s must not derive the charge correction from a
  zero-amplitude Graphite component.

## 6. PATTERN — the C 1s adventitious-component migration (recorded 2026-09-22)

Not four cases: one degeneracy seen four times. In the 8-JT graphite project
the C 1s model is an asymmetric graphite line at 284.4 eV plus adventitious
components; "Adventitious 2" is the C–O component, placed by the student at
286.41 eV. On four scans a solution exists in which that component LEAVES
the C–O position, slides about 1.4 eV to lower binding energy, broadens, and
sits under the main line as a second carbon component — inside the server's
default ± 2 eV centre window, so nothing forbids it:

| scan | who found it | χ²ᵣ: student's method → migrated solution | Adventitious 2 moved |
|---|---|---|---|
| C1s Scan_1 | basin-hopping only (defeats ten scattered starts) | 17.55 → 12.30 | −1.47 eV (286.41 → 284.94; width 1.30 → 2.25 eV; area 3.5 k → 29 k) |
| C1s Scan_5 | scattered starts (2 of 3) | 33.90 → 17.26 | −1.43 eV |
| C1s Scan_6 | scattered starts (3 of 3) | 56.82 → 18.45 | −1.40 eV |
| C1s Scan_7 | scattered starts (2–3 of 3) | 35.8–64.2 → 15.47 | −1.42 eV |

(Scan_1's sign was reported loosely as "1.47 eV" and once as "+"; it is
towards LOWER binding energy, like the other three.) On Scan_7 the student's
own method also moves the component (−1.86 eV) — the model as posed does not
hold it at C–O at all.

What it is: the asymmetric tail of the graphite line and a broad symmetric
component beneath it are nearly interchangeable ways of describing the same
intensity. Giving the fit a free component with a ± 2 eV window lets it
spend that component on the main line's misfit, which lowers χ² by more than
describing a weak C–O feature ever could. The result scores better and is
chemically wrong: it reports a large second carbon species that the student
did not propose and removes the C–O the student did propose.

Consequences already acted on:
- It is THE reason the red-band confirmation exists. A lower χ²ᵣ reached by
  moving a component more than 1 eV from where the student put it is this
  pattern until shown otherwise, so adopting such a solution asks first and
  names the component and the distance; and it is why the student's method
  result remains the fit (owner decision, §5).
- The scattered-starts table shows every component's move for the same
  reason: the migration is invisible in χ²ᵣ and in a fractions-only table.

RELEVANT TO THE FIND PEAKS CANDIDATE LADDER (not yet examined): any model
space that can EXPRESS this migration will FIND it, because an information
criterion rewards exactly this trade. A candidate set that includes a free
broad component near an asymmetric main line, or centre windows wide enough
to reach it, should be expected to rank the migrated model first on graphitic
C 1s. Checks worth making there: whether candidate centre windows let an
adventitious slot reach the main line; whether the ranking can prefer
"asymmetric line + broad carbon under it" over "asymmetric line + C–O"; and
whether the result names the slot by its ROLE (so a migrated slot is still
called C–O). Narrower per-role centre windows are the structural remedy; the
manual path has only the ± 2 eV default.


## 7. A03 (2026-09-22) — a "Voigt" was fitted with a mix the page never drew; the sweep found DS+G's preview wrong across its fitted range

Generators: `scripts/voigt_eta_measure.py` (the 90 committed Voigt targets,
both requests), `scripts/local_server_gap.js` (the 18 W1 targets),
section (D) of `tests/js/lineshape_parity.test.js` (the sweep). Plan and
tables: `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.

**The Voigt identity.** `peakToBackendSpec` sent a Voigt as
`pseudo_voigt_gl` with `gl_ratio: 0.3` FREE; `evalPeak` drew η = 0.5;
`runFitLocal` held 0.5; the dropdown said "50/50"; CLAUDE.md said fixed 0.5.
On the 90 committed targets with a Voigt component (89 U 4f tabs across five
projects, one Cl 2p; 180 Voigt components): the server's free η ended at
pure Gaussian (< 0.01) on 46 of the 180 and pure Lorentzian (> 0.99) on
17, within 0.4–0.6 on 24. Every area, percentage, chart
component and export the page produced for those components was the 0.5
curve under parameters fitted for another mix: displayed area vs the fitted
curve median 11.8 %, p90 19.2 %, max 20.1 % (103 of 180 components > 10 %);
area fractions off by median 0.96 pp, max 1.60 pp (35 of 90 targets > 1 pp).
Fixed on both sides (η = 0.5 held in the request). What a student SEES
change on re-fitting a saved project is small — the fixed refit vs what the
page displayed: median 0.30 pp, max 1.02 pp (1 target > 1 pp) — because both
are the 0.5 curve; the refit vs the server's own free-η fit is median
0.93 pp, max 2.04 pp, χ²ᵣ higher by median 9.5 % (the mix is one parameter
fewer). The alternative — honour the fitted η on the page — would have made
"Voigt" a GL with a hidden slider and silently kept a shape the student had
not chosen; 63 of 180 fitted values sitting on a bound says the parameter
was not determined by the data in those fits anyway.

**The re-measurement (W1 methodology, 18 targets).** C 1s unchanged (8 of 9
within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is the §2 finding). U 4f,
W1 → A03: max Δcentre 39.7 → 28.8 meV, ΔFWHM 17.2 → 15.8 %, Δarea 20.8 →
8.9 %, Δfraction 1.4 → 0.77 pp. On the 5 of 9 targets where both engines
reach the same minimum (χ²ᵣ equal to 2–3 digits) every component is within
4.3 meV, 2.6 %, 2.0 %, 0.12 pp — the Voigt gap is gone. On the other 4 the
server's continuous LA m moved from its start of 8 to 2.7, 6.5, 10.0 and
7.9 while the local engine holds it; χ²ᵣ differs by 8–20 % (the local engine
LOWER on Scan_6, 2.657 vs 2.798), and the satellites, which share the
region, differ by up to 8.9 % in area. That residual is the `caM` clamp,
next; the "starting point" label stays until it is done and re-measured.

**The sweep.** Gaussian, Lorentzian, Voigt, GL, asym-GL and DS agree with
the server to 1e-15 across every bound. LACX with m > 0: up to 0.89 % of
amplitude when the kernel is wide against the peak (the tracked
discretisation gap). DS+G with m ≥ 0.05: the page's `laCasaXPS` quadrature
uses a step of 2·(6σ + 50β)/max(300, ⌈2·(6σ + 50β)/(β/3)⌉) — sized to the
Lorentzian core, blind to the Gaussian kernel — so at β = 2, m = 0.05 the
step is 0.67 eV against σ = 0.021 eV, the kernel weights sample nothing,
and the page's curve is 1e52 × amplitude; at β = 0.7, m = 0.05 the page's
area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
865 committed components use DS+G, so no saved figure is affected; it is the
fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
recorded as its own unit. The general lesson repeats §6's: a harness that
evaluates one representative point per shape proves nothing about the range
the optimiser can reach.
