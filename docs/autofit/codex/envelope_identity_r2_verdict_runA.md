# Envelope identity — Codex round 2, run A (commit 7141a0e)

Reviewed `90651e6..7141a0e`, focusing on the changes after `bf8a6c1`.

1. **MAJOR — the split check accepts missing or duplicated drawn components.**  
   [_check_fitted](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_browser_envelope_identity.py:104) checks only the component datasets it receives. It never requires a one-to-one match with the server’s components.

   Using a real Gaussian fit, the committed JavaScript `DRAWN` reader, and in-memory chart datasets, I reproduced:

   | Mutation | Check result | Maximum drawn identity gap |
   |---|---|---:|
   | Remove first component | Pass | 8,997.51 counts |
   | Remove every component | Pass | 9,000.76 counts |
   | Duplicate first component | Pass | 8,997.51 counts |

   This permits precisely the visible envelope-above-components defect the unit should prevent. The edited-state check does not cover a drawing defect restricted to server-backed fits.

   Require unique drawn IDs matching the complete server ID set, with matching array lengths, before checking parity. Add a negative proof that removes a **drawn component after fitting**.

2. **MINOR — the LA explanation presents first-order estimates as exact bounds.**  
   [The derivation](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/envelope_identity.py:17) correctly identifies non-negative convolution terms and the kernel length. However, normalization does not literally “at most double” relative error: numerator and denominator errors introduce denominator factors. Final amplitude multiplication and division also round.

   This does **not** require widening the implemented total bound for these cases. At maximum `K = 1167`, accounting for two normalized evaluations and their final arithmetic adds approximately `4.0000000013u |c|` beyond `4γ_K |c|`; the four-component summation coefficient has approximately `16u S` of remaining margin. Document that allocation explicitly.

The three original MAJOR findings are otherwise addressed:

- **FFT allowance:** removed. Separating same-implementation summation from cross-language parity is sound once component completeness is enforced.
- **Locks:** both components now have held-value and `vary=False` assertions. My in-memory lock-stripping mutation was rejected.
- **Horizontal alignment:** datasets now share an asserted x-grid, with a shifted-component negative control.

For complete component sets, the split catches wrong or stale component curves, wrong parameters that change those curves, individual grid shifts, and a drawn background differing from the server’s. The parity allowance is **0.009 counts for a 9,000-count component**, below a visible discrepancy in these fixtures. The recovery allowance scales with floating-point addition/subtraction error involving the background; it is not a meaningful widening of parity. The narrowed coverage statement accurately identifies the remaining omissions.

Validation: **34 server tests passed in 73.60 seconds**. The reader/assertion mutations ran without a browser; I did not rerun the browser suite under the read-only restrictions. No files changed.

**VERDICT: NO-GO.**
