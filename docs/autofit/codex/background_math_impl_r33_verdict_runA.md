# Background math implementation — Codex round 33, run A (commit f9b2ea7)

Reviewed `f9b2ea7`, read-only. **Four runtime MAJOR findings, one proof-related MAJOR under your explicit criterion, and one MINOR.**

## PROPORTIONALITY RULING

1. **I agree with category (c) for the demonstrated round-25–31 findings.** None warrants reclassification. Round 32’s reported overflow was (a)+(b), and its two regression cases now refuse. The broader finite-only rule remains incomplete.
2. **Yes, other inputs can produce wrong numbers or false-current results.** The concrete cases below carry matching fit keys; the keyless policy does not prevent them.
3. **The new (a)/(b) findings block deploy.** Logged round-31 B remains **MINOR, category (c), non-blocking**.

**New findings**

1. **MAJOR — Infinite partial sums make the memo suppress an agreeing alternative and falsely establish uniqueness. Category (b).**  
   [templates/index.html:10316](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10316)

   Concrete spectrum record:

   - Raw energies: `[280,280,280,281,282]`.
   - Raw counts: `[2e200,3e200,0,0,0]`.
   - Fit energies: `[280,281,282]`; envelope `[1e200,0,0]`.
   - Background None; Gaussian center `280`, FWHM `1e-10`, amplitude `1e200`.
   - RMSE `1e200 * Math.sqrt(1/3)`; `uploadFull: true`; matching key; no `fitCounts`.

   The first and third samples at 280 give **two distinct agreeing readings**. The intervening, too-large reading caches a dead state with partial sum `Infinity`. The third reading then satisfies `Infinity >= Infinity` and is skipped.

   The production spectrum loader restores **current**, selecting counts `[2e200,0,0]`. Disabling only memo pruning correctly refuses it as ambiguous. Thus §7.20 entry 4’s “cut-only” argument does **not** protect currentness.

2. **MAJOR — A non-finite stored RMSE bypasses verification and remains current. Categories (a)+(b).**  
   [templates/index.html:10135](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10135), [10168](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10168)

   Use energies `[280,281,282]`, counts and `fitCounts` `[1,1,1]`, zero envelope/background, a zero-amplitude Gaussian, and matching key. Set the JSON RMSE to `1e400`, which JavaScript parses as `Infinity`.

   `hasRmse` becomes false, and `rmseVerdict` returns agreement without checking it. The production loader retains **current**, issues only the normal loaded notice, and leaves Results displaying **Infinity**, although the actual RMSE is **1**. A runtime `NaN` takes the same bypass.

3. **MAJOR — The energy-matching tolerance overflows and accepts incompatible stored points. Category (b).**  
   [templates/index.html:10124](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10124)

   Concrete project record:

   - Raw energies `[1e308,1.1e308,1.2e308]`.
   - Stored fit energies `[1.4e308,1.5e308,1.6e308]`.
   - Counts `[1,1,1]`, zero envelope/background, zero-amplitude Gaussian, RMSE `1`.
   - Matching key with charge shift zero; `uploadFull: true`.

   `Math.abs(a) + Math.abs(b)` overflows, making the energy allowance infinite. The production project loader restores **current** and replaces the incompatible stored grid with the raw grid. An overflow-safe evaluation of the allowance correctly refuses it.

   **This tolerance comparison is missing from §7.20’s inventory.**

4. **MAJOR — The stale-background notice reports an infinite percentage instead of 100%. Category (a).**  
   [templates/index.html:10054](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10054)

   Use three ordinary energies, counts and envelope `[1e307,1e307,1e307]`, Background None, a zero-amplitude Gaussian, RMSE zero, and matching key.

   Restore correctly marks the background stale, but `100 * worst / scale` overflows before division. The production loader displays **“differs … by inf %”**; the correct difference is **100%**. All supplied values are finite.

5. **MAJOR — The absolute-underflow derivation is incorrect as written. Category (b), under your explicit proof criterion.**  
   [plan:1232](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:1232)

   The division’s absolute rounding error belongs **after** dividing the accumulated sum error by `n`. The written argument divides that error by `n` again.

   Its scaled-side justification also claims the final product cannot underflow before `m` does. Counterexample: residuals `[Number.MIN_VALUE,0,0,0,0]` give nonzero `m`, normalized sum `1`, but `m * Math.sqrt(1/5)` rounds to zero.

   **I have not demonstrated that the final allowance itself is too small.** It has substantial margin and may admit a corrected proof. Nevertheless, the supplied derivation does not establish its claim as written.

6. **MINOR — The model-is-fit equality shortcut precedes its finite guard. Category (c), non-blocking.**  
   [templates/index.html:9975](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:9975)

   With equal infinite centers and zero frame difference, `_restoredModelIsFit` returns true before checking finiteness. This contradicts §7.20 entry 5. I demonstrated the helper-level failure, not a wrong displayed result from this shortcut.

**Ruling on the allowances and remaining checks**

The relative allowance is derivable rather than merely fitted: the recorded squaring/summation error, scaled divisions and squaring, division by `n`, square roots, and final multiplication fit within its margin for permitted array sizes. The first-order approximation needs that size restriction; the margin accommodates the higher-order correction.

The absolute allowance’s written proof fails as described above. Across **20,000 numerical probes**, including **6,751** cases with recorded zero RMS but positive scaled RMS, I found no final-bound violation. Those experiments are not a proof.

`ssWindow` uses the same relative and absolute terms, but its unscaled sums and memo still invalidate the claimed search safety. The caps refuse rather than accept when exhausted. The logged LA magnitude-bound limitation remains category (c) for its demonstrated consequence.

**Verification**

- Census reproduces exactly: **0 current / 81 stale / 40 peaks-only**.
- Python twin verdicts agree; two numerical fields differ by one ulp.
- All five measurement summaries and student-note preview figures reproduce.
- All **202** upload round trips, seeds, background arrays and net areas match.
- **131 focused JS tests passed**; **98 Python tests passed** before interruption, with three filesystem-blocked fixtures.
- The narrowed scattered-starts test still asserts the actual four draws. CI floor is **571**.
- Full optimizer/browser suites were not completed. No files changed.

**VERDICT: NO-GO**
