# Background math implementation — Codex round 34, run B (commit 506be82)

## PROPORTIONALITY RULING

**NO-GO under the stated criteria.** I reproduced two new R2 numerical defects and found an incomplete derivation. I found no R1 numerical failure in the ordinary-data probes. Rounds 25–31 remain category (c), including the logged round-31 B.

**The five runtime fixes from round 33 work for their reported cases.** Non-finite RMSEs refuse; energy allowances no longer overflow; percentages handle large and zero scales; overflowing search sums refuse; the model-equality guard precedes its shortcut. The sixth finding—the derivations—is only partially resolved.

### New findings

1. **MAJOR — Restore can install overflowing subtracted counts and subsequently corrupt exported counts and residuals. Category (a), R2.**  
   [templates/index.html:10058](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10058), [spectrum save:11693](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11693)

   Concrete record:

   - Energies `[280,281,282]`; counts `[a,a,a]`.
   - `a = 2**1023`, approximately `8.98846567431158e307`.
   - Gaussian: center `281`, FWHM `1`, amplitude `a`; background None.
   - Stored envelope/background `[0,0,0]`, stored subtracted counts `[a,a,a]`, **RMSE absent**, matching fit key.

   Restore succeeds as stale, with a correct `100%` notice, but installs `bgSubtracted[1] = Infinity`. Save Spectrum reconstructs the count from that value and exports **`null` for the center count and residual**, although both should be the finite number `a`. I executed the production saver and reproduced the corruption.

   This needs nonphysical magnitudes and a hand-crafted incomplete statistic record. `2**1023` is the smallest equal positive operand whose doubling overflows.

   **Simple refusal available:** require the newly computed `bgSubtracted` values to be finite before accepting the restore.

2. **MAJOR — A negative stored RMSE remains current. Categories (a)+(b), R2.**  
   [templates/index.html:10001](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10001)

   Use energies `[280,281,282]`, zero counts/envelope/background, a zero-amplitude Gaussian, background None, and a matching fit key. Omit `uploadFull` and set `rmse: -0.004`.

   Restore returns success; the production statistics accessor returns **`current`**. Results formats the RMSE as **`-0.0`**, and spectrum saving preserves `-0.004`. The true RMSE is zero.

   The smallest tested negative value, `-Number.MIN_VALUE`, also passes. This is R2 because the app’s RMS calculation never writes a negative RMSE.

   **Simple refusal available:** extend the supplied-RMSE validation to require `rmse >= 0`.

3. **MAJOR under the owner’s explicit proof criterion — §7.21 still presents first-order expressions as bounds that do not hold throughout its stated range. Category (b); R2 for the concrete large-array counterexample.**  
   [plan:1293](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:1293)

   Item 3’s substitution produces the relative coefficient
   \[
   \frac{n+5.5}{2(1-(n+8)u/2)}.
   \]
   It then bounds that coefficient by `n/2 + 2.8`. At the permitted `n = 2**26`, these are approximately:

   - Derived expression: **33,554,434.875000026**
   - Claimed upper bound: **33,554,434.8**

   The inequality is false. Items 1–2 similarly need to retain or explicitly bound higher-order terms when converting their gamma bounds into the displayed linear inequalities.

   **This does not demonstrate an undersized implemented tolerance.** Its larger constants still have substantial room. It does mean the requested derivation is not correct step by step over the claimed range. The concrete parameter counterexample is a synthetic 67-million-point case, not a demonstrated instrument spectrum.

   Refusing oversized records is simple, but the proof should still retain gamma terms and explicitly discharge the remaining margins.

### Derivation audit

| Item | Assessment |
|---|---|
| **1 — Recorded RMS** | The division’s absolute error is now correctly added after division. The absolute bound is defensible. The conversion to the displayed strict first-order relative bound needs correction. |
| **2 — Scaled RMS** | Normalization, the unit-magnitude term, and the final product’s possible underflow are now accounted for. Higher-order terms still need explicit treatment in the stated relative inequalities. |
| **3 — Verdict** | The implemented constants appear conservative, but the large-`n` inequality above is false. Also, “≥4×” is overstated: for `n=100`, `208/52.8 ≈ 3.94`. |
| **4 — Window** | Solving the tolerance inequality and adding an absolute cancellation allowance are appropriate. I found no accepted reading cut by the window. The universal proof remains dependent on the incomplete preceding bounds. |
| **5 — Memo licence** | The structural argument is sound: the same state has the same structural/count choices, and rounded addition is monotone. The important extra step—relating forward squared sums to separately scaled RMS evaluations—is addressed, but its strict numerical bound inherits the preceding proof gap. |
| **6 — Energy allowance** | Scaling each magnitude before addition fixes the overflow mechanism. The interval and offset guards reject the reported incompatible-energy cases. |

The widened window and SEP do not change the leaf acceptance predicate. I found no case where their widening introduced a false acceptance or false uniqueness. An infinite upper window endpoint disables that prune; it does not become a memoized partial sum.

### Verification and limits

- **Census reproduced exactly**, including every committed output row: **0 current / 81 stale / 40 peaks-only**. The Python twin agrees.
- **Both differential tests passed.** The oracle removes all four RMSE/memo skip sites; it retains structural checks and finite-value refusals. The bisection probes actual returned-verdict transitions, including ambiguity transitions.
- **88 ordinary-data probes passed**, covering 100–5,000 points, project/exact precision, charge shifts, both energy directions, unsorted data, and identical/distinct duplicates. No unexpected refusal or restoration was found.
- **81 focused JS tests passed; 81 Python tests passed.** Two Python fixtures were blocked by filesystem permissions. Full suites were not rerun.
- No files changed.

The demonstrated runtime defects are **R2**, with straightforward refusal fixes. Nevertheless, they meet this round’s explicit (a)/(b) blocking criteria.

**VERDICT: NO-GO**
