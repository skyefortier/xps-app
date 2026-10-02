# Background math implementation round 16 — run A (commit 848ff1e; codex exec, reasoning high)

Reviewed `848ff1e`, read-only. **One MAJOR finding.**

**MAJOR — Linear and manual backgrounds certify rounding errors exceeding the required predicate.** [fitting.py:567](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:567), [templates/index.html:5092](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:5092), [manual branch:5055](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:5055).

Full window, linear:

```text
E = [280, 281, 283]
I = [1000000000000, 1000000000002, 1000000000001]
```

At 281 eV, the defining affine relation gives exactly `10^12 + 1/3`. Both implementations return `1000000000000.3333740234375` and certify it.

- Actual error: `1/24576 ≈ 4.06901e−5`.
- Predicate: `BG_REL_TOL × span = 2e−12`.
- Error/predicate: **20,345,052×**.

The rational evaluation rounds correctly, but the explicit-background gate checks only finiteness. Correct rounding alone cannot meet the requested span-relative predicate on this window; it must report failure.

Reproduced in both energy orders. `/api/background` returns **HTTP 200**; the page’s throwing producer accepts; restoration accepts both exact and save-rounded curves. Manual anchors at the two endpoints reproduce the same failure. These integer inputs also survive upload rounding unchanged.

Verification: **80 Python and 54 JavaScript checks passed**; two Python fixtures were blocked by filesystem restrictions. Reproduced all four measurement summaries, the **3/62/56 restore census**, the **1,212-case exact margin**, and the **2,424-case upload comparison**. All **606 Tougaard backgrounds** remain bit-identical to round 15, none refused, maximum bound/predicate **0.04325151**. No Tougaard predicate violation surfaced in 2,500 additional extreme-scale probes. CI floor is configured at **538**; full suites and browser tests were not rerun. No files changed.

**VERDICT: NO-GO.**
