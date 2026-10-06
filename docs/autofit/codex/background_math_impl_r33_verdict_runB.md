# Background math implementation — Codex round 33, run B (commit f9b2ea7)

Reviewed `f9b2ea7`, read-only. **Three demonstrated numerical/status defects remain**, plus a derivation issue under your explicit proof requirement.

## PROPORTIONALITY RULING

1. **I agree with category (c) for the demonstrated rounds 25–31 findings.** None warrants reclassification: those cases refuse the fit. Logged round-31 B remains **MINOR, non-blocking**. Round 32’s demonstrated overflow was **(a)+(b)**; that specific path is fixed.
2. **Yes, inputs can still restore an unproven result as current.** Findings 1 and 2 below reproduce this with a matching fit key. The keyless-fit policy does not prevent them.
3. **BLOCK DEPLOY for the new (a)/(b) findings below**, not for round-31 B or other refusals.

1. **MAJOR — Non-finite recorded RMSE bypasses validation. Categories (a)+(b), deploy-blocking.**  
   [templates/index.html:10135](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10135)

   `hasRmse` becomes false for `Infinity` or `NaN`; `rmseVerdict` then returns agreement without checking residuals.

   Concrete spectrum-file case:

   - Energies `[280,281,282]`, counts and `fitCounts` `[1,1,1]`.
   - Background None; zero-amplitude Gaussian; envelope/background `[0,0,0]`.
   - Matching `startsModelKey`, `uploadFull: true`.
   - JSON statistic `"rmse": 1e309`.

   Executing the production spectrum loader and Results renderer produced **`current`**, only the green loaded notice, and displayed **RMSE `Infinity`**. The mathematical RMSE is **1**. `NaN` also bypasses the restore check in memory.

   Invalid supplied statistics must be distinguished from genuinely absent legacy evidence.

2. **MAJOR — Overflowing energy allowances accept incompatible stored points. Category (b), deploy-blocking.**  
   [templates/index.html:10124](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10124)

   **This comparison is missing from §7.20:** energy matching and offset-interval intersection.

   Concrete project-style record, with `beExact` absent:

   - Raw energies `[1e308,1.1e308,1.2e308]`.
   - Stored fit energies `[1.3e308,1.4e308,1.5e308]`.
   - Zero charge shift and matching fit key.
   - Counts `[1,1,1]`, zero envelope/background, zero-amplitude Gaussian, RMSE `1`.

   Adding energy magnitudes overflows inside `eps`. Infinite allowances admit the sole ordered reading despite incompatible energies. Restore returns successfully, replaces the stored grid with the raw grid, and reports **current**.

   An in-memory control computing the allowance without the overflowing addition refuses this record. The exact-spectrum same-frame path also correctly refuses it.

3. **MAJOR — The reported background difference overflows after successful finite checks. Category (a), deploy-blocking.**  
   [templates/index.html:10054](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10054)

   With ordinary energies `[280,281,282]`, counts and envelope `[1e307,1e307,1e307]`, zero-amplitude components, stored RMSE `0`, and today’s background None, restore correctly marks the fit stale.

   However, `100 * worst / scale` becomes `Infinity`, although the difference is **100%**. The production notice says **“differs … by inf %”**. All inputs and both comparison scales are finite.

   Compute the ratio before multiplying by 100.

4. **MAJOR under the owner’s explicit derivation rule — The absolute-bound derivation is incomplete as written. Category (b).**  
   [plan:1232](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:1232)

   I found **no counterexample exceeding the implemented combined allowance**, and no evidence that these constants must be empirically fitted. Nevertheless, I cannot endorse every step of the supplied derivation:

   - The division’s absolute rounding error occurs **after** division by `n`; it cannot itself be divided by `n`. Straight operation accounting gives  
     `((2n−1)/n + 1)·MIN/2`, not the displayed expression. This remains below `1.5·MIN`, so the implemented allowance has room.
   - The claim that `m·sqrt(…)` does not underflow before `m` is false. For residuals `[MIN,0,0,0,0]`, `m = MIN` remains nonzero while the scaled RMS evaluates to zero.
   - Normalized divisions/squares that underflow also need accounting in the scaled frame before multiplication by `m`.

   These observations do **not** demonstrate an undersized final constant. They mean the stated derivation needs completion; your instruction explicitly classifies a faulty or incomplete derivation as (b).

   The relative allowance has a defensible conservative basis: recorded squaring/summation gives `γ_n`; the scaled division’s error is squared, yielding a conservative `γ_(n+2)` bound, covered by `γ_(2n)` for `n≥2`. Division, square root and multiplication must then be included. First-order approximations require a stated range and control of higher-order terms. `ssWindow` uses the same relative and absolute terms, plus its outward summation margin.

5. **MINOR — Model-equality shortcut precedes the finite guard. Category (c), non-blocking.**  
   [templates/index.html:9975](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9975)

   With equal infinite centres and zero shift, `_restoredModelIsFit` returns true before reaching its new guard. I reproduced this directly. I did not establish an additional successful restore through it; downstream model evaluation prevents the tested case. §7.20 item 5 nevertheless overstates its protection.

For the remaining finite-only inventory: the background comparison, count comparison, exact rounding predicates and background certificates showed no additional acceptance defect in the exercised extreme-value cases. Iteration stopping remains subordinate to certification. The caps refuse rather than select a surviving fit. **5,000 comparisons against disabled numerical pruning/memoization found no discrepancy**; this is supporting evidence, not a universal proof.

Verification reproduced:

- Census **0 current / 81 stale / 40 peaks-only**; Python twin classifications agree.
- All five committed measurement summaries and the student-note preview figures.
- All **202** page-format/parser round trips, backgrounds, net areas and seed-v2 seeds.
- **105 focused JS tests and 83 Python tests passed**. Four Python fixtures were blocked by read-only filesystem permissions. The narrowed scattered-starts test checks actual draws and passed.
- CI floor remains **571**. Full optimizer/browser suites were not rerun. No files changed.

**VERDICT: NO-GO**
