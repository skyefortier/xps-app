# A2 round 2 — run A (commit b66d6fe; codex exec, reasoning high)

1. **MAJOR — Unsupported components still hide distinct certified minima.** [tests/fit_equality.py:120](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:120)

   Reproduced with complete `run_fit` responses, both seed 123. On 20,001 points over −500…500 eV, use a held Gaussian of height 1e6/FWHM 300, two true lines of height 10/FWHM 0.1 at ±0.25, and an unmodelled height-100/FWHM-0.1 line at 400. Fit the dominant component plus one small component with fixed width.

   Starting the small component at either ±0.25 returns **separate certified minima five widths apart**, both χ² = 2.06107080805. The objective rises between them. Both small components have `supported=False` (F ≈ 0.732), so the helper skips their curves and parameters and **accepts the complete responses**. Statistical insignificance does not make these the same minimum. The owner’s explicit condition remains unmet.

2. **MAJOR — Scattered-start objectives bypass the tightened objective tolerance.** [tests/fit_equality.py:41](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:41)

   `_OBJECTIVE` omits `chi2r`, which scattered-start reports use. Those values receive the parameter tolerance, 1e-3, instead of 1e-7.

   Using the actual two-basin test response, changing its alternative’s χ²ᵣ from **1.36691756229 to 1.36814778810 (+0.09%)** passes `assert_same_fit`. Thus the rewritten scattered-start reproducibility test still admits the objective regression round 1 required tightening. Include scattered-start objective fields in the objective comparison.

3. **MINOR — Matching infinities disable finite-sample curve comparisons.** [tests/fit_equality.py:123](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:123)

   `np.nanmax` retains infinity, making the component’s scale infinite. Reproduced from a supported two-peak response: put `+inf` at the same component sample in both copies, then add **1e9 counts at another, finite sample** in one copy. The helper accepts them. Matching non-finite masks must still leave a finite scale for comparing finite samples.

4. **MINOR — The corrected note mixes measurement runs and misidentifies affected regions.** [docs/comms/2026-09-30-run-fit-certificate-note.md:35](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/docs/comms/2026-09-30-run-fit-certificate-note.md:35)

   The final run supporting “4 of 202” has **198**, not 197, targets below 1 percentage point. Two of those four changed targets are **U4f Scan_7 in B4C-UCl4** and **U4f Scan_6 in UCl4_on_graphite**, rather than C 1s. Identify the measurement run consistently and include U 4f.

Validation: **90 focused Python tests and 122 JavaScript tests passed**; the battery passed in three processes without observed flakiness. The revised small-component proof passes and rejects through fitted quantities. Certificate exit probes and cancellation during a restart behaved correctly; V3 search ordering remains intact. Committed data confirms **0/202 displacement notices**, maxima **0.04299 eV TR / 0.01059 eV LM**. A broader run was interrupted after three passing tests to bound review time. No files changed.

**VERDICT: NO-GO**
