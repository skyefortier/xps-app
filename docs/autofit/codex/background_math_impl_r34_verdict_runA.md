# Background math implementation — Codex round 34, run A (commit 506be82)

## PROPORTIONALITY RULING

**Three MAJOR findings remain, all R2.** I found no new R1 defect. Under your criterion, the R2 defects still require **NO-GO**; each has a simple refusal fix.

The original round-33 runtime reproductions are fixed. However, the broader input-finiteness requirement remains incomplete, and a restored result can still contain non-finite derived counts.

1. **MAJOR — A missing raw energy becomes zero and the fit reads as current. Category (b), R2.**  
   [templates/index.html:10115](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10115)

   The code subtracts the charge shift **before** validating the raw energy. Consequently, `null - 0` becomes finite `0`.

   Concrete project record: raw energies `[null,1,2]`, stored fit energies `[0,1,2]`, zero counts/envelope/background, zero-amplitude Gaussian, RMSE `0`, Background None, and a matching fit key.

   Executing the production project loader, restore, and Results renderer with UI stubs produced **current**, fitted energies `[0,1,2]`, and only the green loaded notice. The missing energy was silently invented.

   **Reachability:** R2, requiring malformed file contents; no extreme magnitudes are needed. **Simple refusal:** validate each original `rawBE` element as a finite number before subtraction.

2. **MAJOR — A finite negative RMSE is accepted and retained as current. Categories (a)+(b), R2.**  
   [templates/index.html:10001](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10001)

   Use energies `[0,1,2]`, zero counts/envelope/background, zero-amplitude Gaussian, Background None, matching key, omitted `uploadFull`, and RMSE `-0.001`.

   The legacy `0.005` allowance accepts it. The production loader reports **current**; Results displays **`-0.0`**, and the save path preserves the impossible statistic `-0.001`. The actual RMSE is zero.

   **Reachability:** R2, because the app never computes a negative RMSE. No large inputs are necessary. At the smallest representable magnitude, `-Number.MIN_VALUE` also passes, including with `uploadFull: true`. **Simple refusal:** require a supplied RMSE to be nonnegative as well as finite.

3. **MAJOR — Restoring a stale fit can overflow its reconstructed counts, which Save Spectrum subsequently corrupts. Category (a), R2.**  
   [templates/index.html:10058](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:10058), [save reconstruction:11693](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:11693)

   Concrete record: energies `[0,1,2]`; counts and initial `bgSubtracted` all `9e307`; envelope all `-9e307`; initial background zero; zero-amplitude Gaussian; Background None; matching key; RMSE absent.

   Restore succeeds as **stale, 100%**, but installs `bgSubtracted = [Infinity,Infinity,Infinity]`. Save Spectrum reconstructs its own counts as `Infinity + (-9e307)`, still Infinity; JSON serialization writes these as `null`.

   **Reachability:** R2, requiring nonphysical magnitudes and an inconsistent record. The symmetric overflow threshold is just above `Number.MAX_VALUE / 2`; ordinary counts do not approach it. **Simple refusal:** validate the reconstructed subtracted counts before installing the restored fit.

**Round-33 fixes and derivations**

The non-finite RMSE cases, overflowing energy allowance, percentage calculation, overflowing-sum memo reproduction, and equality-guard ordering now behave correctly. Finding 1 above means the expanded requirement that *input energies themselves* be finite is not fully implemented.

My assessment of §7.21’s derivations is:

| Item | Assessment |
|---|---|
| **1 — recorded RMSE** | The division’s absolute rounding error is now correctly added after division. The square-root perturbation argument supplies the required absolute allowance. |
| **2 — scaled RMS** | The maximum residual supplies a normalized term of exactly one. Normalized underflow is negligible relative to that sum; retaining the final multiplication’s `MIN/2` error fixes the previous omission. |
| **3 — verdict** | The final relative and absolute constants have sufficient conservative margin, including evaluation rounding and the stated higher-order corrections. They are defensible derived allowances, rather than merely test-fitting constants. One numerical margin claim is overstated, below. |
| **4 — window** | The absolute widening addresses cancellation in the lower endpoint; the relative widening covers converting scaled RMS bounds to differently ordered sums of squares. I found no accepted reading cut by these margins. An infinite upper endpoint only disables that prune; accepted path sums remain separately checked. |
| **5 — memo licence** | The structural argument is sound: the state fixes available suffixes, rounded addition preserves ordering, and too-small/intermediate failures prevent memoization. Comparing scaled RMS values requires the additional separation; the stated SEP conservatively covers the sum-to-RMS discrepancy and acceptance arithmetic. |
| **6 — energy allowance** | Scaling each magnitude before addition fixes the overflow. This arithmetic argument presupposes numeric input energies; finding 1 violates that precondition before the comparison. |

**MINOR — The claimed “≥4×” relative margin is incorrect. Category (c), non-blocking.**  
[plan:1296](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/docs/superpowers/plans/2026-10-01-background-math-implement.md:1296)

Against the preceding stated coefficient, the ratio is `(2n+8)/(n/2+2.8)`: approximately **3.16 at n=2**, approaching four from below. This is a documentation overstatement; correcting it does not invalidate the sufficient final allowance. It applies already at ordinary sizes, rather than requiring an extreme numerical input.

The wider window and SEP do not loosen the leaf acceptance test. They can expose a previously pruned valid reading—or an additional reading that makes the record ambiguous. The committed census is unchanged.

**Verification and limits**

- Census reproduced **exactly**, including committed percentages: **0 current / 81 stale / 40 peaks-only**. Python twin reproduced **15 matching stale / 66 differing stale / 40 refused**.
- **61 focused JS tests passed**, including both differential tests. Their oracle removes all four RMSE/memo pruning conditions; the bisection targets transitions in the oracle’s overall restore verdict. It is useful differential coverage, not an independent numerical implementation.
- **72 additional ordinary-range restores passed**: 100–5,000 points, counts below `1e7`, both save precisions, charge frames, duplicates and unsorted records.
- **90 focused Python tests passed**; two fixtures were blocked by read-only temporary-directory permissions. Full suites were not certified in this sandbox. Focused Python-backed checks used an in-memory temporary-directory initialization workaround.
- No files changed. Logged round-31 B remains **MINOR (c), non-blocking**.

**VERDICT: NO-GO**
