**Two MINOR correctness gaps remain. No BLOCKER or MAJOR found.**

**1. Round-3 findings**

| Finding | Status |
|---|---|
| Floating-point bound spans become infinite without raising | **Resolved:** float64 subtraction is checked explicitly. [app.py:1473](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1473) |
| Hostile bounds only in `b` escape refusal | **Resolved:** both operands are checked before comparison. [app.py:1512](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1512) |
| Excessive links only in `b` escape refusal | **Partially resolved:** the plain chain is refused, but shortcut links defeat the depth check; reproduction below. [app.py:1477](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1477) |
| Earlier overflow/recursion 500s and stale plan wording | **Remain resolved:** exception catches remain; the plan correctly describes replacement/closure versus edits/tab switches. [app.py:1531](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1531), [plan:64](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/docs/superpowers/plans/2026-10-15-seal-1d-rerun.md:64) |

**2. Remaining paths**

**MINOR — an infinite half-maximum width is still compared.** The guard checks energy span, signal and bounds, but omits the derived position scales. `_half_max_width` multiplies the grid step by the number of samples above half maximum; that product can overflow despite a finite energy span. Positions then receive an infinite tolerance. [app.py:1463](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1463), [same_fit.py:118](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:118), [same_fit.py:193](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:193)

Reproduced with a response passing the form check: energy `[0, 8e307, 1.6e308]`, matching three-element arrays, component curves `[1, 1, 1]`, and starts marked not requested. The span is finite, but the width is infinite. Changing only `b`’s first peak centre to `1e307` returns **HTTP 200, `same: true`, no problems**.

**MINOR — breadth-first depth does not bound recursive link depth.** The guard’s shared `seen` set measures shortest reachability, while the comparator follows recursive paths. [app.py:1480](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1480), [same_fit.py:141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/same_fit.py:141)

Reproduced by extending the 1,100-link fixture: each link also references a `hub`, whose expression references every chain node. The long path remains, but the guard finishes within a few breadth-first levels. With this response **only in `b`**, comparison returns **200, `same: false`**. With it on both sides, recursive traversal reaches the fallback catch and returns **400**. Operand-dependent refusal therefore remains.

I reproduced no additional HTTP 500 path.

**3. Can a real fit response be refused?**

**Yes, at the intended arithmetic boundary.** Using the existing well-posed fixture, I supplied `fix_fwhm: true`, `fwhm_min: -1e308`, `fwhm_max: 1e308`. `/api/fit` returned **200 with `success: true`**, retaining those bounds; comparing that response with itself returned **400**. Fixed `center` bounds behaved identically. The producer accepts and records these bounds. [fitting.py:1777](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1777), [fitting.py:1781](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1781), [fitting.py:3009](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3009)

This follows the requested finite-span restriction; corpus compatibility is not a guarantee for every producer response.

**4. Do the tests detect their named defects?**

**Yes, for their concrete cases.** All 12 passed; disabling `_comparable_failure` in memory made all 12 fail. They omit derived-width overflow and links with shortcuts. [test_seal_1d_compare.py:155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:155)

Validation: **62 passed, 1 skipped**, using in-memory upload/session substitution. The corpus test skipped because `SEAL_1B_RECORDS` was unavailable, so I did not independently verify the 328-record claim. [test_seal_1d_compare.py:175](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:175) No files changed.

VERDICT: NO-GO
