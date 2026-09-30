# Background methods: what each one solves, and whether it solves it (2026-09-30)

Owner: "whether the METHODS themselves are defensible. Do not defend any method
by resemblance to another program. For each of shirley, smart, smart_exp,
shirley_linear, linear, tougaard, manual: (a) the defining statement … (b) its
assumptions … (c) numerical proof the implementation solves it … (d) rewrite the
docstrings … If a method has no coherent defining statement, say so. Findings
that would change fitted numbers: REPORT, do not implement."

Method: `scripts/background_defining_statements.py` writes each statement as an
INDEPENDENT check (it never calls a method's own loop) and evaluates it on the
method's output — on every committed spectrum (121: 43 Shirley C 1s fits, 65
`smart` — 54 of them U 4f — and 13 `smart_exp`; each on its saved background
window and endpoint averaging) and on synthetic spectra. Data:
`data/measure.jsonl`. Tests: `tests/test_background_defining_statements.py`,
`tests/js/manual_background_statement.test.js`. Residuals are relative to the
data's span, max(I) − min(I). No fitted number was changed by this unit.

Notation: I the measured intensity on the window [E_min, E_max]; b_low, b_high
the intensity levels at the low- and high-BE edges; T(B) the right-hand side of
the Shirley relation,
T(B)(E) = b_low + (b_high − b_low) · ∫_{E_min}^{E} s / ∫_{E_min}^{E_max} s,  s = max(I − B, 0),
discretised by the trapezoid rule on the data's grid.

## Summary

| method | defining statement | solves it? (committed spectra) | verdict |
|---|---|---|---|
| shirley | B = T(B) | yes: ≤ 2e-11 of span read as measured; unique fixed point (5e-15) | coherent; F1, F5 |
| smart | B = min(T(B), I) (constrained Shirley) | **yes** — not a truncation (see below): ≤ 2e-11 read as measured | coherent; F1, F2, F3 |
| smart_exp | B = min(T(B), I) | yes: ≤ 2e-11 on every spectrum and averaging used | coherent; the SAME method as smart (F3) |
| shirley_linear | none | — | **incoherent: should not return to the menu** (F4) |
| linear | B affine in E through the end points | yes: exact (≤ 1.3e-16) | coherent, narrow validity; page reads it by index (F8) |
| tougaard | B = C0 + λ ∫_{E′<E} K(E − E′)(J − C0) dE′, λ from B(E_high) = J(E_high) | yes: = explicit double sum to ≤ 1e-13; ≤ 8.4e-6 of the 10×-refined integral | coherent; its physics barely exercised on these windows (F6) |
| manual | piecewise-affine through the anchors, constant outside | yes (server and page, to 1e-9) | a user curve, no physics; fallback reads a line by index (F8) |

## Per method

### shirley — B = T(B)

(a) The background rises above the low-BE level in proportion to the net
(no-loss) intensity already accumulated at lower binding energy, and meets both
edge levels. (b) Assumptions: every no-loss electron at lower BE adds the same,
energy-independent step at every higher BE in the window (constant loss
probability, all losses inside the window) — fails for structured losses
(plasmons, shake-up) and wide windows; both edges on zero net signal — fails
when a window cuts a peak tail; only positive net intensity scatters (s is the
positive part) — B itself is not kept below the data: it rises above the data on
116 of 121 committed spectra, by up to 6 % of the span, mostly at noise dips.
(c) Read as measured (n_avg = 1, 108 spectra): residual ≤ 1.7e-11; the fixed
point is unique (a start below the data reaches it to 4.8e-15); an independent
iteration reaches it in ≤ 23 steps; the page's preview default of 5 iterations
is within 8.5e-5 of the span and 0.0064 % of net area of the converged result.
With n_avg > 1 see F1. Corroboration: Shirley, Phys. Rev. B 5, 4709 (1972);
Proctor & Sherwood, Anal. Chem. 54, 13 (1982) (the docstring cited "Surf. Sci."
and CLAUDE.md "54, 13, 2438–2439" — both corrected).

### smart — B = min(T(B), I)

(a) At every point either the Shirley relation holds with B ≤ I, or the
constraint B = I is active where the relation would exceed the data. Justified
by: net intensity is a non-negative count rate.

**The expectation that `smart` fails — a post-hoc clamp solving the
unconstrained problem and truncating it — is refuted, exactly.** The implemented
Shirley integrates the positive part s = max(I − B, 0), and
s(min(B, I)) = s(B): clamping changes B only where the net signal is already
zero. So T(min(B, I)) = T(B) = B and min(B, I) is a fixed point of the
constrained map. The constrained problem has a unique solution (two starts agree
to 6e-15), so `smart` IS its solution: residual ≤ 1.7e-11 and equal to an
independently iterated constrained solution to 1.8e-11 on all 108 spectra read
as measured. (It would fail for a Shirley that integrated the SIGNED net signal;
this one does not.)

(b) Assumptions: Shirley's, plus B ≤ I **pointwise on the measured counts**.
Non-negativity holds for the EXPECTED intensity; measured counts scatter below
the background, so the constraint binds on noise dips — active on a median 12 %
and up to 46 % of the points on the committed spectra. Consequence (F2).

### smart_exp — B = min(T(B), I)

The same constrained problem, solved directly by the projected iteration
B ← min(T(B), I) with the edge levels averaged and the measured data
integrated: residual ≤ 1.7e-11 on all 121 spectra and every averaging used. For
n_avg = 1 it returns the same background as `smart` (F3).

### shirley_linear — no defining statement

It returns min(L + S, I): L the line between the averaged edge levels, S a
Shirley-shaped term of the FULL edge difference, |b_low − b_high|·(1 − F), F the
cumulative fraction of the net signal above L counted from the low-BE edge. At
the low-BE edge L + S = b_low + |b_low − b_high| — above the edge level on any
sloped window (a median 5 %, up to 41 %, of the span on the committed
spectra) — and it adds a second full step on top of a line that already carries
the edge difference. No assumption about inelastic scattering yields that curve;
only the final clamp to the data restores the edges, active on a median 43 %
(up to 72 %) of the points. F4.

### linear — B affine in E through the end points

(b) The background varies linearly and no loss intensity builds up under the
peaks — reasonable for a narrow window around small peaks, not for a core level
whose loss tail lifts the high-BE side; both end points on background. Raw end
points (no endpoint averaging: one noisy end sample tilts the line). (c) Exact
(≤ 1.3e-16). The page's twin interpolates by INDEX (F8).

### tougaard — the loss-integral relation

(a) B(E) = C0 + λ ∫_{E_min}^{E} K(E − E′)(J(E′) − C0) dE′, K(T) = T/(C + T²)²,
C = 1643 eV²; C0 the low-BE edge level (everything emitted below the window, as a
constant); λ from B(E_high) = J(E_high). Explicit in J — one pass is the relation,
not an approximation of an iteration. (b) Homogeneous depth distribution and the
universal cross-section (fitted to noble / transition metals) — fails for
layered or particulate samples and sharp-plasmon materials; the out-of-window
contribution constant; the high-BE edge free of primary signal; and the window
long enough for K's shape to matter — K peaks at √(C/3) = 23.4 eV of loss. (c)
The implementation (a convolution on uniform grids) equals the explicit double
sum to ≤ 9.2e-14, and the integral on a 10×-finer grid to ≤ 8.4e-6 of the span
(≤ 8.5e-4 % of net area). Corroboration: Tougaard, Surf. Interface Anal. 11, 453
(1988) (coefficient values not re-verified against the paper text here).

### manual — piecewise-affine through the anchors

A user-drawn curve: no physical model, the defence is the user's judgement. The
server (np.interp) and the page (`manualAnchorBackground`) both equal the
definition to 1e-9, on uniform and non-uniform grids.

## Findings (F1–F8)

**Would change fitted numbers — REPORTED, not implemented:**

- **F1. Two readings of endpoint averaging.** With n_avg > 1, `shirley` (and
  `smart` through it) replaces the first / last n_avg points OF THE DATA by their
  mean and integrates that modified spectrum; `smart_exp` averages only to read
  the edge LEVELS and integrates the measured data. The coherent statement is
  the latter (averaging estimates a level; the relation integrates the
  measurement). Measured on the 13 committed spectra with n_avg > 1 (B 1s at 25 /
  31, U 4f at 6): up to 1.05e-3 of the span, net area median 0.18 %, max 0.32 %.
  Change: read endpoint averaging as levels only in `shirley_background` (and
  its page twin, which mirrors it). Pinned by
  `test_FINDING_shirley_with_endpoint_averaging_integrates_the_averaged_data`.
- **F2. The constraint B ≤ I on noisy counts biases net areas high.** The
  justification (net intensity non-negative) holds for the expected intensity,
  not for each measured count. Poisson Monte Carlo against a known Shirley-shaped
  background, 300 draws: unconstrained Shirley −0.12 % ± 0.11 % (s.e.) of net
  area — unbiased; the constrained problem (`smart` / `smart_exp`) +0.82 % ± 0.07 %
  (lower variance, 1.22 % vs 1.85 % per draw). On the committed spectra the
  constrained and unconstrained solutions differ by a median 0.20 %, p90 1.3 %,
  max 11.8 % of net area (constrained larger on 116 of 121). Options for the
  owner: keep and disclose; constrain against a noise-aware bound (e.g. B ≤ I +
  a multiple of the counting noise — a threshold on a data-scaled quantity, so
  it would need its own justification); or retire the constrained methods.
  Pinned by `test_FINDING_the_constraint_on_noisy_counts_biases_the_net_area_high`.
- **F5. Shirley's stop is absolute** (a change < 1e-6 intensity units), not
  relative — the design rule "thresholds on data-scaled quantities fail". The
  same spectrum in other units stops elsewhere; negligible on the committed
  spectra (at 10⁻⁶ of the units: ≤ 1.4e-5 of the span, ≤ 0.0023 % of net area).
  Change: a relative stop (or run to the fixed point). Pinned.

**Decisions, no number changes:**

- **F3. `smart` and `smart_exp` are one method.** Same problem, same unique
  solution for n_avg = 1; they differ only through F1. Offering both suggests a
  difference that is not there. (Once F1 is resolved they are identical for
  every n_avg.)
- **F4. `shirley_linear` has no coherent defining statement** — it should not
  return to the menu. It stays importable so the saved files that use it
  restore (de-listed 2026-09-03).
- **F6. Tougaard's physics is barely exercised on these windows.** Every
  committed window is 10–35 eV wide (B 1s 10–16, C 1s 14–19, Cl 2p 20, U 4f
  31–35 eV) against a kernel that peaks at 23.4 eV of loss: the integral samples
  only its rising part, λ absorbs the rest, and the curve is effectively a
  smooth one-parameter shape anchored at both edges. Defensible as a relation;
  its universal-cross-section content needs windows extending well into the loss
  region (tens of eV beyond the peak).
- **F7. The page's Shirley preview (5 iterations) vs the fit (to convergence):**
  within 8.5e-5 of the span and 0.0064 % of net area on every committed
  spectrum — the gap recorded in the sealed-fit-record memo Part 5 is negligible
  in practice.
- **F8. Linear in index vs linear in energy.** The page's `linearBackground`
  (and the manual background's < 2-anchor fallback) draws the line by index; the
  statement — and the server — is affine in energy. Equal on uniform grids only
  (already pinned as Task 4 cause 4); the page twin should read energy.

## Docstrings

`fitting.py`'s background functions now state what each solves, its assumptions
and where they fail, and the measured status — no "closer to Avantage", no
resemblance defence; the page's twins' comments and the Background menu's
tooltips likewise (the `smart_exp` tooltip said "closer to Avantage Smart
behavior").
