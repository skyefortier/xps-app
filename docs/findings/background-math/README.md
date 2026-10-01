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
| shirley | B = T(B), reading "data" | yes: ≤ 1.7e-11 of span on all 121 | coherent; not always unique (F9); the iteration can cycle (F12); F1, F5, F10 |
| smart | B = min(T(B), I) | at n_avg = 1 yes (≤ 1.7e-11); at n_avg > 1 **no** — it mixes the readings (up to 1.1e-3) | coherent at n_avg = 1; F1, F2, F3, F12 |
| smart_exp | B = min(T(B), I), reading "levels" | yes: ≤ 1.7e-11 on all 121 | coherent; F2, F3, F12 |
| shirley_linear | B = min(L + d(1 − F(B)), I), L affine in index | yes: ≤ 3.3e-11 — except equal edge levels, where it returns L unclamped; the page's twin only on ascending grids | a coherent equation with no physical basis — a reversed step; should not return (F4); can cycle (F12) |
| linear | B affine in E through the raw end points | yes: exact (≤ 1.3e-16) | coherent, narrow validity; the page reads it by index (F8) |
| tougaard | B = C0 + λ Σ_{E′≤E} K(E−E′)(D(E′)−C0) w, λ from B(E_high) = D(E_high), reading "data" | yes: ≤ 9.2e-14 vs an independent sum; anchor exact; ≤ 8.4e-6 of an independent 10×-refined integral; a vanishing loss sum leaves λ undetermined (F11); the near-uniform fast branch approximates the sum | coherent; F1, F6, F11 |
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
the implementation, when it converges, returns the solution reached from the
edge-to-edge line; it can also cycle and return a non-solution (F12). On the
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

The same constrained problem, iterated by the projection B ← min(T(B), I) with
only the edge levels averaged — a solution when that iteration converges (it can
cycle, F12): residual ≤ 1.7e-11 on all 121 spectra and
every averaging used. At n_avg = 1 it returned the same background as `smart` on
every committed spectrum (to 1.3e-16) — an agreement of the two iterations from
the same line, not a uniqueness result (F3).

### shirley_linear — a reversed step

What it solves (corrected after Codex round 1: it does have a statement):
B = min(L + d(1 − F(B)), I), L the line between the averaged edge levels
**affine in the point INDEX** (not in energy — equal only on uniform grids),
d = |b_low − b_high|, F(B) the cumulative fraction of max(I − B, 0) from the low-BE
edge — satisfied to 3.3e-11 on the committed spectra. Two exceptions the equation
does not cover (Codex round 2): when the edge levels are equal (|b_low − b_high|
below an absolute 1e-12) it returns L itself, UNCLAMPED, above the data wherever the
data dip below the line (e.g. E = 0…4, I = [10, 15, 5, 15, 10] gives a flat 10,
where the equation gives [10, 10, 5, 10, 10]); and the iteration stops if the net
integral is not positive. The page's twin (`shirleyLinearBackground`) solves the
same equation — when its iteration converges — only on an ASCENDING grid: it does not reverse a descending one
(the usual XPS order), so there its step is accumulated from the other edge — a
different curve (on a 5-point example its equation residual is 7.6 % of the span
and it differs from the server's curve by 7.8 %; the pinned page / server gap).
Like the Shirley iteration it can cycle (F12). The unclamped curve meets the high-BE level, but its
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
When the discrete loss sum at the high-BE edge is zero (e.g. a two-point window:
the kernel vanishes at T = 0, so the sum has no term, although the continuum
integral of the interpolated data would not vanish) λ is not fixed by the anchor:
if D(E_high) = C0 the solutions form a family, one per λ, and the flat C0
returned is its λ = 0 member (every member is flat only when the whole loss
vector vanishes, as on a two-point window); if D(E_high) ≠ C0 there is no
solution and the returned C0 misses the anchor (F11; none of the committed
spectra). On a grid uniform to 1e-6 of its first step the implementation
evaluates the sum as if EXACTLY uniform (index gap × first step, one weight) —
exact on a uniform grid; otherwise each separation and weight is perturbed by up
to ~1e-6 relative, and the resulting error is NOT bounded by that: measured
1.0e-8 and 2.5e-7 of the span on two 4–5-point examples, and because the anchor
divides by the high-edge sum, near cancellation it is amplified — 16 % of the
span on a constructed case where both sums are non-zero, and a nearly cancelling
sum can come out exactly zero (the anchor then missed by 33 %) (Codex rounds 3–4). (b) Homogeneous depth distribution and the universal
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

## Degenerate windows (every method)

Branches no defining statement covers, stated here once (Codex round 3's brief):
a window of fewer than two points returns zeros (every Shirley-family method and
Tougaard); `linear` with equal end energies returns the flat first intensity;
endpoint averaging reads at most n // 4 points per edge and is ignored below four
points (the checker's `band` follows the same rule). None occurs on the committed
spectra; pinned in the tests.

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
  (Codex round 1), and the constraint adds ~+1 % on top. Endpoint averaging of
  10 at the large step cuts the per-draw spread ~3× and both biases, and reduces
  but does not remove the constraint's increment. Isolated — both equations
  reading the averaged edge LEVELS, the same data: unconstrained +1.57 % ± 0.06,
  constrained +2.40 % ± 0.05, increment +1.28 → +0.83 % ± 0.01 (paired reduction
  0.44 ± 0.04 pp). The production methods at averaging 10 (`shirley` averages the
  DATA, `smart_exp` only the levels — F1) give +1.43 % ± 0.06 and +2.40 %: that
  +0.97 % difference includes 0.14 pp of F1's change of reading, not the
  constraint (Codex round 5). Whether
  the positive-part integrand is the source of the unconstrained bias is NOT
  established: the same iteration with a signed integrand fails to solve its own
  equation on ~20 of the 1000 draws at the large step (its integral turns
  non-positive, or it runs out of iterations — one such draw is −606 % in area),
  so its mean mixes failed solves with solutions and says nothing about the
  estimator (Codex round 2; an earlier draft quoted it as "worse"). On the committed spectra the constrained and
  unconstrained solutions differ by a median 0.20 %, p90 1.3 %, max 11.8 % of net
  area. Options: keep and disclose; retire the constrained methods; a
  noise-aware bound (e.g. B ≤ I + k·√I — a data-scaled threshold, which the
  design rule says needs its own justification). Owner decision.
- **F5. Shirley's stop is absolute** (a change < 1e-6 intensity units) — the
  design rule "thresholds on data-scaled quantities fail". The same spectrum in
  other units stops elsewhere; negligible on the committed spectra (at 10⁻⁶ of the
  units: ≤ 1.5e-5 of the span, ≤ 0.0023 % of net area, same reading). Option: a
  relative stop on the relation's residual. Owner decision.
- **F10. When the data lie below the edge line everywhere, the Shirley iteration
  cannot start.** The first step's net-signal integral is zero, so the relation is
  undefined there; production returns the line (`shirley`) or the data (`smart`,
  `smart_exp`), none of which solves its statement — although solutions exist
  (Codex round 1's case, pinned). None of the committed spectra. Options: report
  it as an outcome (no background), or start from another curve. Owner decision.

**Decisions, no number changes:**

- **F3. `smart` and `smart_exp` state the same problem** and at n_avg = 1
  returned the same background on every committed spectrum; they differ through
  F1. Offering both suggests a difference that, at n_avg = 1, was not measured.
- **F4. `shirley_linear` should not return to the menu:** its equation is
  coherent, its physics reversed (see above). It stays importable so the saved
  files that use it restore (de-listed 2026-09-03). Owner decision.
- **F6. Tougaard's kernel shape.** B 1s, C 1s and Cl 2p windows (10–20 eV)
  sample no loss beyond the kernel maximum (23.4 eV); the U 4f windows (31–35 eV)
  draw up to 30 % of the high-BE edge's integral from beyond it. Replacing K by
  its small-loss linear form and re-anchoring moves the background by up to 3.9 %
  of the span on U 4f (0.02–0.7 % on the narrower windows): the universal
  cross-section's shape matters on those windows, so its assumptions (homogeneous
  depth, transition-metal-like losses) bear directly on the U 4f backgrounds.
- **F7. The page's Shirley preview (5 iterations) vs the fit:** within 8.6e-5 of
  the span and 0.0064 % of net area on every committed spectrum, same reading —
  the gap recorded in the sealed-fit-record memo Part 5 is negligible in practice.
- **F8. Linear in index vs linear in energy.** The page's `linearBackground`
  (and the manual background's < 2-anchor fallback) draws the line by index; the
  statement — and the server — is affine in energy. Equal on uniform grids only
  (already pinned as Task 4 cause 4).
- **F9. The Shirley relation is not well posed in general** (several solutions;
  exact counterexamples pinned). When they converge, the implementations return
  the solution reached from the edge-to-edge line; they can also cycle and return
  a non-solution (F12). On the committed spectra no second solution was found from
  a second start — which cannot rule one out.
- **F11. Tougaard when its discrete loss sum at the high-BE edge vanishes**
  (the sampled quadrature, not the continuum integral: a two-point window has no
  term with T > 0). λ is then not determined by the anchor. With equal anchor
  levels, D(E_high) = C0, the solutions form a family, one per λ, and the returned
  flat C0 is its λ = 0 member (all flat only when the whole loss vector vanishes);
  with unequal levels there is no solution and C0 misses the anchor. The
  near-uniform fast branch can produce such a zero where the stated sum has none,
  and amplifies its approximation near cancellation (see tougaard above). All
  pinned; none of the committed spectra. Options: report the undetermined and
  unsatisfiable cases as outcomes; evaluate the stated sum on every non-uniform
  grid. Owner decision.
- **F12. The fixed-point iterations can cycle** (Codex round 3). On small
  positive spectra on uniform ascending grids `shirley`, `smart`, `smart_exp` and
  `shirley_linear` alternate between two curves forever — 2000 iterations give
  what 200 give — and return a curve that solves nothing: `shirley` 14 % of the
  span on E = 0…3, I = [2, 3, 10, 13] (an exact solution exists: [2, z, z + 5.5,
  13], z = (17 − √37)/4) and 21 % on E = 0…4, I = [11, 14, 1, 33, 40] (the Smart
  methods 11 % there), `shirley_linear` 12.5 % on I = [20, 44, 34, 41, 47]. A
  larger cap cannot help; the checker's own reference solver does not converge
  on them either. On all 121 committed spectra every iteration converged: each
  method's residual against its own statement is as in the summary — `shirley`
  and `smart_exp` ≤ 1.7e-11, `shirley_linear` ≤ 3.3e-11, `smart` ≤ 1.7e-11 at
  n_avg = 1 (at n_avg > 1 its underlying Shirley iteration converged too — ≤ 1.7e-11
  under its own reading — and its gap of up to 1.1e-3 is F1's mixed reading, not
  non-convergence). Options: (i) CERTIFY the returned background against its
  statement and report non-convergence as an outcome (as a fit that did not
  converge is) — no number changes where it converges; (ii) a fixed-point solver
  (damped iteration, a root finder) used ONLY as a fallback after a failed
  certification — changes numbers on the failing inputs only; (iii) replacing the
  iteration generally — changes numbers elsewhere too: on a converging 4-point case
  production stops at net area 0.40000537 (its absolute 1e-6 stop, F5) where the
  exact solution gives 0.4, and where several solutions exist (F9) another solver
  may select another. Owner decision.

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

**Round 2 — NO-GO ×2** (`docs/autofit/codex/background_math_r2_verdict_run{A,B}.md`,
commit 4af19e7; both: no fitted number changed; all 121 records and the
1000-draw Monte Carlo table reproduced; the independence, returned-point
convergence, non-uniqueness, F5 / F6 / F7 fixes hold; the positive-part Monte
Carlo, smart's "neither reading" and the constrained-area statistics survive):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): F2's signed-integrand figure (−3.6 % ± 0.9) mixes failed solves — ~20 of 1000 draws end on a non-positive integral or out of iterations (one −606 % in area, residual 1.6 × span) — with solutions; the "+1.4 % at averaging 10" is the positive-part method's | the inference withdrawn: F2 says the signed comparison establishes nothing; averaging 10 re-measured for BOTH methods (unconstrained +1.43 % ± 0.06, constrained +2.40 % ± 0.05) |
| 2 | MAJOR (A): the page's `shirleyLinearBackground` comment claimed the server's equation; on a descending grid it accumulates from the other edge (7.6 % of span) | comment states it solves the equation on ascending grids only; `tests/js/shirley_linear_statement.test.js` pins both (ascending uniform / non-uniform, averaging 1 / 5, residual < 1e-9; the descending example > 5 %) |
| 3 | MAJOR (A, B): `shirley_linear`'s statement omitted the equal-edge-level early return (L returned unclamped: residual 1/3–1/2 of span on a 5-point example) and did not say L is affine in INDEX | docstring, README, CLAUDE.md state both; tests pin the exception and the index-affine line (an energy-affine L differs by > 4 % on the example) |
| 4 | MAJOR (B) / MINOR (A): F11 conflated "no solution" with "λ undetermined"; and the zero is the discrete sum's, not the continuum integral's | F11, the docstring and the checker distinguish the two; both cases pinned. (Round 3 corrected this fix's own claim that the flat C0 then solves the statement "for every λ": it is the λ = 0 member of a family.) |
| 5 | MINOR (B): the Smart tooltip did not say it solves neither reading at n_avg > 1 | the tooltip says so (up to ~0.1 % of span); smart_exp's no longer calls it "the same problem as Smart" |
| 6 | MINOR (A, B): the Shirley docstring kept "≤ 0.32 %" (measured 0.3225 %) | ≤ 0.33 % |

**Round 3 — NO-GO ×2** (`docs/autofit/codex/background_math_r3_verdict_run{A,B}.md`,
commit e1077be; both: no fitted number changed; all 121 records and the Monte
Carlo — incl. averaging 10: +1.4307 % ± 0.0555 / +2.4032 % ± 0.0456 — reproduce;
the round-2 fixes hold; the degenerate branches are covered):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A, B): the iterations can CYCLE and never converge on small positive spectra (shirley 14 % / 21 % of span, the Smart methods 11 %, shirley_linear 12.5 %; 2000 iterations = 200), so "returns the solution reached" was an overclaim | F12; "returns the solution" qualified by "when it converges" (README, docstrings, CLAUDE.md, the page comment); the four cycles and the exact solution pinned. (Round 4: F9, a test comment and the smart_exp tooltip had been missed; now qualified.) |
| 2 | MAJOR (A) / MINOR (B): Tougaard's near-uniform fast branch approximates the stated sum (index separations, one weight), and a nearly cancelling high-edge sum can become exactly zero (anchor missed by 33 %) | stated in the docstring, the code comment (no longer "a pure optimization"), the README; both pinned. (Round 4: the "~1e-8 of span" quoted here was one example, not a bound — corrected.) |
| 3 | MINOR (A, B): F11's "the flat C0 solves it for every λ" is false when interior loss terms are non-zero | the flat C0 is the λ = 0 member of a family; all flat only when the whole loss vector vanishes; pinned on a uniform 4-point case |
| 4 | MINOR (B): averaging does reduce the constraint's increment (+1.28 → +0.97 %, 0.30 ± 0.04 pp) | "reduces but does not remove". (SUPERSEDED in round 5: +0.97 % / 0.30 pp compared two readings; the constraint's own increment is +0.83 % ± 0.01, reduction 0.44 ± 0.04 pp — see F2.) |
| 5 | MINOR (A): the page comment called 7.6 % (the equation residual) the page / server gap (7.8 %); F5 ≤ 1.4e-5 and F7 ≤ 8.5e-5 were exceeded (1.442e-5, 8.517e-5) | both numbers named; ≤ 1.5e-5 and ≤ 8.6e-5 |

**Round 4 — NO-GO ×2** (`docs/autofit/codex/background_math_r4_verdict_run{A,B}.md`,
commit 84f3ee0; both: no fitted number changed; 121 records and the Monte Carlo —
incl. the averaging reduction 0.3049 ± 0.0380 pp, a two-reading figure
superseded in round 5 — reproduce; the F11 family, the averaging increment, both
shirley_linear numbers and the F5 / F7 bounds hold):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A) / MINOR (B): F9, a test comment and the smart_exp tooltip ("solved directly") still claimed a solution without the convergence condition (both Smart methods return a 14 % non-solution on the pinned cycle) | qualified there and in CLAUDE.md's method row; the smart_exp docstring's and page comment's "solved directly" replaced; the round-3 table annotated |
| 2 | MAJOR (A) / MINOR (B): F12's "every implementation … ≤ 1.7e-11" contradicted smart at n_avg > 1 (1.1e-3) and shirley_linear (3.3e-11) | method-specific bounds; smart's gap attributed to F1 (its underlying Shirley iteration converged, ≤ 1.7e-11 under its own reading) |
| 3 | MAJOR (B) / MINOR (A): Tougaard's "~1e-8 of span" was one example, not a bound: 2.5e-7 on a non-cancelling grid, and 16 % of span where both high-edge sums are non-zero but nearly cancel (the anchor amplifies the error) | stated as measurements with the amplification (docstring, code comment, README); both pinned |
| 4 | MINOR (A, B): F12's "a new solver changes numbers on those inputs only" does not follow — a root finder moves a converged case (net area 0.40000537 → 0.4) and may pick another solution where several exist | three options with their scope: certify and report; a fallback solver after a failed certification (failing inputs only); a general replacement (numbers move elsewhere too); pinned |
| 5 | (A) F4, F5, F10, F11 lacked the explicit "owner decision" F1 / F2 / F12 carry | labelled, with their options |

**Round 5 — NO-GO ×2** (`docs/autofit/codex/background_math_r5_verdict_run{A,B}.md`,
commit 26fc9e2; both: no fitted number changed; 121 records and the Monte Carlo
reproduce; the round-4 repairs hold — convergence qualifications, F12's bounds and
option scopes, Tougaard's measured errors, the owner-decision labels; the
bibliography checked against the publishers' pages):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (A): F2's averaging-10 "increment" compared `shirley` (averages the DATA) with `smart_exp` (averages the levels), so it mixed F1's reading into the constraint's effect | the isolated effect, both equations on the levels reading: +1.28 → +0.83 % ± 0.01 (paired reduction 0.44 ± 0.04 pp); the production-method difference (+0.97 %, 0.14 pp of it F1) labelled as such; a seeded test pins "reduced, not removed" |
| 2 | MAJOR (B): the Smart tooltip's "wherever … it equals them" holds only when the iteration converges (a 6-point spectrum: 19.9 % of span) | "(when the iteration converges)" |
| 3 | MINOR (B): the new JS test's header said the page solves the equation on ascending grids without the convergence condition (12.5 % on the pinned cycle) | qualified |
| 4 | MINOR (A, B): the checker's header put `shirley_linear` under the "data" reading; it (and the checker's own residual) reads the levels and integrates the raw data | moved to "levels"; its statement written out; the header states that an output solves its statement only when its iteration converged |

**Round 6 — GO ×2** (`docs/autofit/codex/background_math_r6_verdict_run{A,B}.md`,
commit 211bf7f; both: no fitted number changed; 36 Python and 4 JS tests pass;
121 records and the Monte Carlo — incl. the isolated averaging comparison,
+0.8334 % ± 0.0114, reduction 0.4440 ± 0.0378 pp — reproduce; the solution claims
account for averaging, convergence, grid direction, the near-uniform approximation
and degenerate windows; F1, F2, F4, F5, F10, F11, F12 follow from the evidence and
are reserved for the owner; no resemblance-based defence). One MINOR (A, B): the
round-3 table and the round-4 header still carried the superseded two-reading
figure (+0.97 %, 0.30 pp) as the constraint's — both annotated as superseded.

