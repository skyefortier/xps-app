# Envelope identity — Codex round 2, run B (commit 7141a0e)

Reviewed `90651e6..7141a0e`, focusing on the changes after `bf8a6c1`. **One new MAJOR prevents GO.**

1. **MAJOR — The fitted-page check accepts missing or duplicated component datasets.**  
   [`_check_fitted`](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_browser_envelope_identity.py:104) checks only the components present in `DRAWN`; it never requires exactly one drawn dataset for every server component.

   Using a real Gaussian fit, the committed JavaScript `DRAWN` reader, and the unmodified assertion:

   | Mutation | Assertion | Actual drawn-sum error / envelope height |
   |---|---|---:|
   | Remove first component | Passes | 94.5% |
   | Remove all components | Passes | 94.6% |
   | Duplicate first component | Passes | 94.5% |

   Thus the split currently accepts a conspicuous violation of its central claim. Require unique drawn IDs matching the complete server component set, and add a post-fit missing-component negative control. The existing dropped-component proof exercises the **edited envelope**, so it does not cover this gap.

2. **MINOR — The LA explanation presents a first-order expression as an exact bound.**  
   [`envelope_identity.py:17`](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/envelope_identity.py:17): non-negativity is correct, and the kernel length conservatively bounds each dot’s term count. However, normalization does not exactly “at most double” relative error. Writing \(g=\gamma_K\), two normalized evaluations can differ by up to
   \[
   \frac{4g}{(1-g)^2}|c|,
   \]
   before accounting for the final multiplication/division rounding.

   For the supported \(K\le1167\), these additional terms fit comfortably within the existing base bound’s spare margin. Document that allocation; I found no need to widen the implemented total tolerance.

The round-1 lock finding is resolved: both components’ requested values and server `vary` flags are checked. Stripping the lock flags now fails with `gaussian: amplitude varied`. The relative x-alignment finding is also resolved by explicit grid equality and the shifted-component proof. The unsupported FFT allowance is removed, and the coverage claim is appropriately narrowed.

The split is otherwise a reasonable replacement: exact background equality catches a differently computed page background, while component parity catches material wrong shapes, parameters, and stale curves. At these fixtures’ amplitudes, `1e-6` permits roughly hundredths of a count—not a student-visible drawing discrepancy. The recovery allowance accounts for floating-point addition/subtraction against the background; it is not a material tolerance widening. Those conclusions depend on fixing the missing component correspondence above.

Validation: **34 server tests passed in 74.78 seconds**, plus the in-memory mutation checks described above. Full browser execution was not rerun under the read-only restrictions. No files changed.

**VERDICT: NO-GO.**
