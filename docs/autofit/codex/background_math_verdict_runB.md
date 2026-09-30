# Background math round 1 — run B (commit 8436631; codex exec, reasoning high)

**No fitted numbers changed.** `fitting.py` has an identical executable AST after removing docstrings. `index.html` is identical after removing standalone JS comments and tooltip contents. Working tree untouched.

1. **BLOCKER — The uniqueness claim is false.** [README.md:69](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:69), [tests:125](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/tests/test_background_defining_statements.py:125).

   With `n_avg=1` and ascending samples:
   ```text
   E  = [0, 1,     2,     3]
   I  = [1, 1.45,  1.90,  2]
   B₁ = [1, 1.30,  1.80,  2]
   B₂ = [1, 1.375, 1.875, 2]
   ```
   Both backgrounds satisfy **both** `B=T(B)` and `B=min(T(B),I)`, with checker residuals ≤`4.5e-16`. Their net areas are **0.25 and 0.10**. The checker’s linear and below-data starts converge to B₁, missing B₂. Agreement between two starts cannot establish uniqueness—even on the committed spectra. Remove the uniqueness claims throughout README, docstrings, CLAUDE.md and tests, or establish appropriately restricted conditions.

2. **MAJOR — Tougaard’s checker does not check its stated measured-data equation.** [fitting.py:625](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:625), [checker:151](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:151).

   The statement identifies `J` as measured intensity, but production and reference both replace endpoint bands using the **same production helper**. On `B4C-UCl4.proj.zip / B1s Scan_0`, `n_avg=25`, independently evaluating the measured-data sum with averaged anchor levels differs from production by **1.1696e-4 of span**, rather than ≤`1e-13`.

   The refinement also calls production itself at [checker:182](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:182). Additionally, the copied zero-denominator fallback can report perfect agreement while violating the anchor: `E=[0,1,2]`, `I=[1,1,2]` returns `[1,1,1]`; checker discrepancy is zero, but `B(E_high)≠I(E_high)`. Specify the actual preprocessing and degenerate domain, and check the integral and anchor independently.

3. **MAJOR — F6’s “only its rising part” explanation is contradicted by the spectra.** [README.md:169](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:169), [fitting.py:645](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:645).

   The recorded widths check out: **10.3–34.8 eV**, including 54 U 4f windows of **31–34.8 eV**, extending beyond the kernel maximum at 23.4 eV. On `1-GTA … / U4f Scan_1`, **29.7%** of the high-edge integral comes from losses beyond that maximum. Replacing the kernel with its small-loss linear approximation and reanchoring changes `Cl2p_projfit_test / U4f Scan_3` by **3.89% of span**. Thus λ does not absorb the kernel’s shape dependence. Narrow-window limitations remain plausible, but this measurement-based justification fails.

4. **MAJOR — The reference solver can certify substantial residuals as converged.** [checker:106](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:106).

   Its stopping tolerance scales with absolute intensity, while reported residuals scale with span. For `E=[0,1,2,3]`, `I=1e12+[0,.45,.9,1]`, it returns `converged=True` after four iterations with a residual of **0.001953125 of span**. The uniqueness tests discard convergence flags entirely.

   Production iteration limits also need explicit qualification: `I=1e6*[1,1.49,1.91,2]` leaves a **2.4963e-6** residual after the default 200 iterations. A fixed-point identity does not certify an unfinished iteration. Check the returned residual before declaring convergence and report unresolved cases.

5. **MAJOR — The Monte Carlo neither uses an exact Shirley truth nor establishes unbiasedness.** [tests:144](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/tests/test_background_defining_statements.py:144), [README.md:144](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/README.md:144).

   `cumsum(peaks)` constructs a rectangular cumulative background, whereas the defining statement uses trapezoids. Its noise-free residual is **4.0165e-4 of span**, and fitting that noise-free spectrum already changes net area by **+0.04049%**.

   Repeating the specified 300 draws with a trapezoidal truth gives **−0.0621% ±0.1045%** for Shirley and **+0.8285% ±0.0694%** for constrained Shirley. F2’s positive-bias finding survives. However, a mean within three standard errors does **not** prove “unbiased”; report “no statistically resolved bias in this experiment.”

6. **MINOR — F5/F7’s saved measurements mix stopping error with F1.** [checker:226](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:226), [checker:258](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/scripts/background_defining_statements.py:258).

   These comparisons use production’s modified endpoint data against a reference integrating raw data. Consequently, [measure.jsonl:52](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/docs/findings/background-math/data/measure.jsonl:52) records **−0.32254%** for the five-iteration comparison and **−0.32264%** for the `1e-6` scaling comparison—far beyond the quoted bounds.

   Comparing identical endpoint semantics independently recovers the stated small maxima: approximately **0.00637%** for five iterations and **0.00229%** for scaling. The conclusions survive, but the committed measurement fields do not isolate those effects.

7. **MINOR — F4 misstates the hybrid’s mathematics.** [fitting.py:562](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-foundation/fitting.py:562).

   The cumulative integrand is `max(I−L−S,0)`, not simply the signal above L. At convergence a defining relation can be written:
   `B=min(L+|Δb|·(1−F(B)),I)`, with F integrating `max(I−B,0)`.
   On the test’s noise-free synthetic spectrum this relation holds to **1.51e-13 of span**. Also, the unclamped high-BE endpoint **does** equal `b_high`; “meets neither edge condition” is false. Keeping it de-listed can be justified by its reversed scattering contribution and wrong low-edge condition, without claiming no mathematical statement exists.

The central clamp identity **is sound** for a converged positive-part Shirley solution using the same data in both maps. It requires neither uniqueness nor resemblance to another program. It does not carry over unchanged to a signed integrand, mismatched averaged/raw data, or unfinished iterations. F1’s mismatch and F8’s index-versus-energy distinction are valid findings.

Validation: **18 Python tests and 2 JavaScript tests passed**. All **121 measurement records reproduced** within numerical tolerance. These checks do not resolve the findings above; I did not rerun the full commit suites.

The bibliographic entries are correct: [Shirley, PRB 5, 4709 (1972)](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.5.4709), [Proctor & Sherwood, Analytical Chemistry 54(1), 13–19 (1982)](https://pubs.acs.org/doi/10.1021/ac00238a008), and [Tougaard, Surface and Interface Analysis 11, 453–472 (1988)](https://analyticalsciencejournals.onlinelibrary.wiley.com/doi/10.1002/sia.740110902). This verifies the bibliography, not every attribution to the papers’ full text.

**VERDICT: NO-GO.**
