**Two MINOR refusal gaps remain. No BLOCKER or MAJOR found.** The exact round-2 exceptions are handled, but the endpoint still compares related hostile inputs.

1. **Round-2 findings**

   | Finding | Status |
   |---|---|
   | Integer bound-span overflow returns 500 | **Exact reproduction resolved:** now 400 with an overflow reason. Floating-point spans remain unhandled; see below. [app.py:1488](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1488) |
   | Approximately 1,100 parameter links cause recursion and 500 | **Exact reproduction resolved:** now 400 naming excessive link depth. Refusal still depends on whether comparison traverses the chain. [app.py:1491](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1491) |
   | Tests paragraph still promises edit/tab-switch discard | **Resolved:** it now distinguishes replacement/closure from edits/tab switches. [plan:64](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:64) |

2. **Is every malformed or hostile input refused? No.**

   - **MINOR — floating-point span overflow is silently compared.** Set both responses’ `fwhm` bounds to floating-point `-1e308` and `1e308`, then set only `b`’s `fwhm.value` to `1e307`. Reproduced **HTTP 200, `same: true`, no problems**. Subtraction produces infinity without raising `OverflowError`, making the tolerance infinite. The new catch therefore does not refuse the input. [same_fit.py:199](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:199), [app.py:1488](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1488)

   - **MINOR — refusal depends on operand and traversal.** With an ordinary `a`, placing either the overflowing **integer** bounds or the 1,100-link chain only in `b` returns **HTTP 200, `same: false`**, rather than 400. Bounds and link metadata come from `a`; unequal parameter keys also stop traversal before following links. These are reproduced paths where hostile inputs are compared. [same_fit.py:135](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:135), [same_fit.py:244](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:244)

   Refusing these cases consistently requires validation of both sides before comparison; exception catches alone do not establish that guarantee.

3. **Does this round change ordinary comparison decisions? No.**

   The comparator is unchanged this round. The production change adds two exception handlers around its existing calls. Other exceptions still reach the logged 500 branch; I confirmed that with an injected `ValueError`. [app.py:1482](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1482), [app.py:1494](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1494)

4. **Do the new tests fail on their named defects? Yes, for their exact inputs.**

   Removing each catch independently in memory makes its corresponding test fail on HTTP 500. However, the overflow test uses **integer** bounds, and both tests compare the hostile response with its copy. They miss floating-point overflow and hostile content only in `b`. [test_seal_1d_compare.py:139](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:139), [test_seal_1d_compare.py:147](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:147)

Validation: **52 tests passed**, using in-memory upload/session substitution for read-only execution. Both mutations were detected. I did not rerun the full suite. No files changed.

VERDICT: NO-GO
