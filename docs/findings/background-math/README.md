# Background methods: what each one solves, and whether it solves it (2026-09-30)

*Revised after Codex round 1 (NO-GO ×2: the uniqueness claim was false, the
checker shared production's preprocessing, the Monte Carlo's truth was not an
exact Shirley background, F4 and F6 misstated the math; section "Codex rounds").*

Owner: "whether the METHODS themselves are defensible. Do not defend any method
by resemblance to another program. For each of shirley, smart, smart_exp,
shirley_linear, linear, tougaard, manual: (a) the defining statement … (b) its
assumptions … (c) numerical proof the implementation solves it … (d) rewrite the
docstrings … If a method has no coherent defining statement, say so. Findings
that would change fitted numbers: REPORT, do not implement."

Method: `scripts/background_defining_statements.py` writes each statement
INDEPENDENTLY of `fitting.py` — its own endpoint preprocessing, its own integrals,
its own reference solver (convergence is declared only when the returned point
satisfies the statement) — and evaluates it on the method's output under the
method's OWN reading of endpoint averaging, on every committed spectrum (121: 43
Shirley C 1s fits, 65 `smart` — 54 of them U 4f — and 13 `smart_exp`, each on its
saved window and averaging) and on synthetic spectra. Data: `data/measure.jsonl`.
Tests: `tests/test_background_defining_statements.py` (24),
`tests/js/manual_background_statement.test.js` (2). Residuals are relative to the
data's span. No fitted number was changed by this work (docstrings, comments and
two tooltip texts only).

Notation: I the measured intensity on the window [E_min, E_max]; D the intensity
as a method reads it — reading "data": the first / last n_avg points replaced by
their mean; reading "levels": the measured data, with only the edge levels b_low,
b_high read as the end means; T(B)(E) = b_low + (b_high − b_low) · ∫_{E_min}^{E} s /
∫_{E_min}^{E_max} s, s = max(D − B, 0), trapezoid rule on the data's grid.

## Summary

| method | defining statement | does the implementation solve it? (121 committed spectra) | verdict |
|---|---|---|---|
| shirley | B = T(B), reading "data" | yes: ≤ 1.7e-11 of span on all 121 | coherent; not always unique (F9); F1, F5, F10 |
| smart | B = min(T(B), I) | at n_avg = 1 yes (≤ 1.7e-11); at n_avg > 1 **no** — it mixes the readings (up to 1.1e-3) | coherent at n_avg = 1; F1, F2, F3 |
| smart_exp | B = min(T(B), I), reading "levels" | yes: ≤ 1.7e-11 on all 121 | coherent; F2, F3 |
| shirley_linear | B = min(L + d(1 − F(B)), I) | yes: ≤ 3.3e-11 | a coherent equation with no physical basis — a reversed step; should not return (F4) |
| linear | B affine in E through the raw end points | yes: exact (≤ 1.3e-16) | coherent, narrow validity; the page reads it by index (F8) |
| tougaard | B = C0 + λ Σ_{E′≤E} K(E−E′)(D(E′)−C0) w, λ from B(E_high) = D(E_high), reading "data" | yes: ≤ 9.2e-14 vs an independent sum; anchor exact; ≤ 8.4e-6 of an independent 10×-refined integral | coherent; F1, F6, F11 |
| manual | piecewise-affine through the anchors, constant outside | yes (server and page, to 1e-9) | a user curve, no physics; F8 |

## Per method

### shirley — B = T(B)

(a) The background rises above the low-BE level in proportion to the net
(no-loss) intensity already accumulated at lower binding energy, and meets both
edge levels. (b) Assumptions: every no-loss electron at lower BE adds the same,
energy-independent step at every higher BE in the window (constant loss
probability, all losses inside the window) — fails for structured losses
(plasmons, shake-up) and wide windows; both edges on zero net signal — fails when
a window cuts a peak tail; only positive net intensity scatters (s is the
positive part) — B itself is not kept below the data: it rises above it on 116 of
121 committed spectra, by up to 6 % of the span, mostly at noise dips.
(c) Under its own reading, residual ≤ 1.7e-11 on all 121 spectra; an independent
reference solution agrees to 1.8e-11. **Not unique in general (F9):** the tests
carry two 4-point spectra with several exact solutions and different net areas;
the implementation returns the solution reached from the edge-to-edge line. On the
committed spectra a second start (below the data) reaches the same solution to
1e-13 — no second solution found from that start, which is not a proof that none
exists. Corroboration: Shirley, Phys. Rev. B 5, 4709 (1972); Proctor & Sherwood,
Anal. Chem. 54, 13 (1982) (the docstring cited "Surf. Sci." and CLAUDE.md
"54, 13, 2438–2439" — both corrected; the bibliography verified by both reviewers).

### smart — B = min(T(B), I)

(a) At every point either the Shirley relation holds with B ≤ I, or the
constraint B = I is active where the relation would exceed the data. Justified
by: net intensity is a non-negative count rate.

**The expectation that `smart` fails — a post-hoc clamp solving the
unconstrained problem and truncating it — does not hold when its integrand and
its clamp read the same data (n_avg = 1).** The implemented Shirley integrates the
positive part s = max(D − B, 0), and s(min(B, I)) = s(B) when D = I: clamping
changes B only where the net signal is already zero, so T(min(B, I)) = T(B) = B —
the clamp of a Shirley solution IS a solution of the constrained problem (a
correspondence between solutions; neither problem need have only one). Measured
at n_avg = 1: residual ≤ 1.7e-11 on every committed spectrum. **At n_avg > 1 the
expectation is right in effect:** the integrand reads the averaged data, the
clamp the raw data, and the result satisfies the constrained statement under
neither reading (up to 1.1e-3 of the span; F1). It would also fail for a Shirley
with a signed integrand.

(b) Assumptions: Shirley's, plus B ≤ I **pointwise on the measured counts**.
Non-negativity holds for the EXPECTED intensity; measured counts scatter below the
background, so the constraint binds on noise dips — active on a median 12 % and up
to 46 % of the points on the committed spectra. Consequence: F2.

### smart_exp — B = min(T(B), I), reading "levels"

The same constrained problem, solved by the projected iteration B ← min(T(B), I)
with only the edge levels averaged: residual ≤ 1.7e-11 on all 121 spectra and
every averaging used. At n_avg = 1 it returned the same background as `smart` on
every committed spectrum (to 1.3e-16) — an agreement of the two iterations from
the same line, not a uniqueness result (F3).

### shirley_linear — a reversed step

What it solves (corrected after Codex: it does have a statement):
B = min(L + d(1 − F(B)), I), L the line between the averaged edge levels,
d = |b_low − b_high|, F(B) the cumulative fraction of max(I − B, 0) from the low-BE
edge — satisfied to 3.3e-11. The unclamped curve meets the high-BE level, but its
step is **largest at the low-BE edge and shrinks as net signal accumulates toward
higher BE — the reverse of inelastic scattering**, and it sits d above the low-BE
level there (a median 5 %, up to 41 %, of the span); the clamp to the data is
active on a median 43 % (up to 72 %) of the points. A coherent equation, no
physical basis. F4.

### linear — B affine in E through the end points

(b) The background varies linearly and no loss intensity builds up under the
peaks — reasonable for a narrow window around small peaks, not for a core level
whose loss tail lifts the high-BE side; both end points on background. Raw end
points (no endpoint averaging: one noisy end sample tilts the line). (c) Exact
(≤ 1.3e-16). The page's twin interpolates by INDEX (F8).

### tougaard — the loss-integral relation

(a) B(E) = C0 + λ ∫_{E_min}^{E} K(E − E′)(D(E′) − C0) dE′, K(T) = T/(C + T²)²,
C = 1643 eV², D the end-averaged data (reading "data" — the implementation
replaces the end bands of the data, as `shirley` does; F1), C0 = D at the low-BE
edge, λ from B(E_high) = D(E_high). Explicit in D — one pass is the relation.
Undefined when the loss integral at the high-BE edge is zero (λ has no value; the
flat C0 is returned and the anchor missed — e.g. a two-point window; F11; none of
the committed spectra). (b) Homogeneous depth distribution and the universal
cross-section (fitted to noble / transition metals) — fails for layered or
particulate samples and sharp-plasmon materials; the below-window contribution
constant; the high-BE edge free of primary signal. (c) Against an independent
evaluation (its own averaging, weights and double sum): equal to ≤ 9.2e-14; the
anchor met exactly; within 8.4e-6 of the span (8.5e-4 % of net area) of an
independent 10×-refined integral. Corroboration: Tougaard, Surf. Interface Anal.
11, 453 (1988) (bibliography verified; the coefficient values not re-verified
against the paper's text).

### manual — piecewise-affine through the anchors

A user-drawn curve: no physical model; the defence is the user's judgement. The
server (np.interp) and the page (`manualAnchorBackground`) both equal the
definition to 1e-9 on uniform and non-uniform grids.

## Findings

**Would change fitted numbers — REPORTED, not implemented:**

- **F1. Two readings of endpoint averaging.** `shirley`, `smart`'s integrand and
  `tougaard` replace the first / last n_avg points OF THE DATA by their mean;
  `smart_exp` averages only to read the edge LEVELS. Each reading is a coherent
  statement (Codex: preferring one needs a modelling justification); what is not
  coherent is `smart` at n_avg > 1, which integrates one reading and clamps with
  the other. Measured on the 13 committed spectra with n_avg > 1 (B 1s at 25 / 31,
  U 4f at 6): the two Shirley readings' solutions differ by up to 1.05e-3 of the
  span, 0.33 % of net area (median 0.18 %); `smart` vs `smart_exp` up to 1.05e-3,
  0.26 %; the two Tougaard readings up to 1.2e-4. The argument for "levels": the
  averaging estimates a level from noisy edge samples; replacing samples changes
  the data the relation integrates. The argument for "data": it is one rule for
  every method. Owner decision; either way `smart` should follow one reading.
- **F2. The constraint B ≤ I on noisy counts adds net area.** Poisson Monte
  Carlo, 1000 draws, against a background that satisfies the relation exactly
  (noise-free residual ≤ 4e-17), two step sizes:

  | step | unconstrained Shirley | constrained (`smart_exp`) | the constraint's increment (paired) |
  |---|---|---|---|
  | 400 | −0.03 % ± 0.06 (no resolved bias) | +0.87 % ± 0.04 | +0.90 % ± 0.02 |
  | 4000 | **+2.29 % ± 0.17** | +3.57 % ± 0.14 | +1.28 % ± 0.04 |

  So the Shirley estimator on noisy data is itself biased at a large step
  (Codex round 1), and the constraint adds ~+1 % on top. Not attributable to the
  positive-part integrand alone: a signed integrand is worse at the large step
  (−3.6 % ± 0.9, 30 % per-draw spread); endpoint averaging (10) cuts the spread
  ~3× and the bias to +1.4 %. On the committed spectra the constrained and
  unconstrained solutions differ by a median 0.20 %, p90 1.3 %, max 11.8 % of net
  area. Options: keep and disclose; retire the constrained methods; a
  noise-aware bound (e.g. B ≤ I + k·√I — a data-scaled threshold, which the
  design rule says needs its own justification). Owner decision.
- **F5. Shirley's stop is absolute** (a change < 1e-6 intensity units) — the
  design rule "thresholds on data-scaled quantities fail". The same spectrum in
  other units stops elsewhere; negligible on the committed spectra (at 10⁻⁶ of the
  units: ≤ 1.4e-5 of the span, ≤ 0.0023 % of net area, same reading). Change: a
  relative stop on the relation's residual.
- **F10. When the data lie below the edge line everywhere, the Shirley iteration
  cannot start.** The first step's net-signal integral is zero, so the relation is
  undefined there; production returns the line (`shirley`) or the data (`smart`,
  `smart_exp`), none of which solves its statement — although solutions exist
  (Codex round 1's case, pinned). None of the committed spectra.

**Decisions, no number changes:**

- **F3. `smart` and `smart_exp` state the same problem** and at n_avg = 1
  returned the same background on every committed spectrum; they differ through
  F1. Offering both suggests a difference that, at n_avg = 1, was not measured.
- **F4. `shirley_linear` should not return to the menu:** its equation is
  coherent, its physics reversed (see above). It stays importable so the saved
  files that use it restore (de-listed 2026-09-03).
- **F6. Tougaard's kernel shape.** B 1s, C 1s and Cl 2p windows (10–20 eV)
  sample no loss beyond the kernel maximum (23.4 eV); the U 4f windows (31–35 eV)
  draw up to 30 % of the high-BE edge's integral from beyond it. Replacing K by
  its small-loss linear form and re-anchoring moves the background by up to 3.9 %
  of the span on U 4f (0.02–0.7 % on the narrower windows): the universal
  cross-section's shape matters on those windows, so its assumptions (homogeneous
  depth, transition-metal-like losses) bear directly on the U 4f backgrounds.
- **F7. The page's Shirley preview (5 iterations) vs the fit:** within 8.5e-5 of
  the span and 0.0064 % of net area on every committed spectrum, same reading —
  the gap recorded in the sealed-fit-record memo Part 5 is negligible in practice.
- **F8. Linear in index vs linear in energy.** The page's `linearBackground`
  (and the manual background's < 2-anchor fallback) draws the line by index; the
  statement — and the server — is affine in energy. Equal on uniform grids only
  (already pinned as Task 4 cause 4).
- **F9. The Shirley relation is not well posed in general** (several solutions;
  exact counterexamples pinned). The implementations return the solution reached
  from the edge-to-edge line. On the committed spectra no second solution was
  found from a second start — which cannot rule one out.
- **F11. Tougaard is undefined when its loss integral at the high-BE edge
  vanishes** (λ has no value); production returns the flat C0 and misses the
  anchor. Pinned (a two-point window); none of the committed spectra.

## Docstrings

`fitting.py`'s background functions state what each solves, its assumptions and
where they fail, and the measured status; no uniqueness claims, no "closer to
Avantage", no resemblance defence. The page's twins' comments and the Background
menu's two Smart tooltips likewise.

## Codex rounds

**Round 1 — NO-GO ×2** (`docs/autofit/codex/background_math_verdict_run{A,B}.md`,
commit 8436631; both: no fitted number changed — identical executable AST, HTML
identical after comments / tooltips; the clamp identity sound; the bibliography
correct; all 121 records reproduced):

| # | finding | fix |
|---|---|---|
| 1 | BLOCKER (A, B): the uniqueness claim is false — exact 4-point counterexamples with several solutions and different net areas; two starts agreeing proves nothing | every uniqueness claim removed (README, docstrings, CLAUDE.md, tests); F9 with the counterexamples pinned; F3 stated as an empirical agreement |
| 2 | MAJOR (A, B): the implementation cannot start when the data lie below the edge line (F10); the reference solver's "converged" tested the last update, not the returned point, and its stop scaled with absolute intensity | F10 reported and pinned; the solver declares convergence only when the RETURNED point's residual is ≤ 1e-13 of the span (test) |
| 3 | MAJOR (A, B): the Tougaard check shared production's endpoint preprocessing and fallback, and the refined integral called production | independent preprocessing, weights, double sum, anchor check and refined integral; the statement's J is the end-averaged data it really integrates (F1); F11 for the undefined case |
| 4 | MAJOR (A, B): the Monte Carlo's truth used a rectangular cumulative sum; "unbiased" was not established, and at a larger step unconstrained Shirley is biased (+2.9 %) | exact trapezoid truth (residual ≤ 4e-17), 1000 draws, two step sizes, paired increment; F2 separates the estimator's own bias from the constraint's increment |
| 5 | MAJOR (A, B): F6's "samples only the rising part" is false on the U 4f windows (30 % beyond the maximum; a linear-kernel substitute moves the curve 3.9 % of the span) | F6 restated with those measurements |
| 6 | MAJOR (A) / MINOR (B): `shirley_linear` has a statement, B = min(L + d(1 − F(B)), I), and meets the high edge | stated and verified (3.3e-11); F4 rests on the reversed step and the low-edge excess |
| 7 | MINOR (A, B): the F5 / F7 fields compared production's "data" reading with a "levels" reference | every stopping comparison uses the same reading; F1 measured separately |
