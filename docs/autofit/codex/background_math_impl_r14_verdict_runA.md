# Background math implementation round 14 — run A (commit d4aca1a; codex exec, reasoning high)

Reviewed `d4aca1a`, read-only. **Two MAJOR findings.**

1. **MAJOR — Tougaard’s rounding bound underflows and falsely certifies.** [fitting.py:1136](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1136), [templates/index.html:4760](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4760).

   Full window, averaging 1:

   ```text
   E = [280, 281, 282, 283]
   I = [200, 300, 1.15, 300] × 1e-120
   ```

   Using those same binary64 inputs, both implementations return `2.3892970309604796e-116` at 282 eV. Exact Fraction evaluation gives approximately `2.3892970309601888e-116`.

   - Actual error: **2.90770e-129**, **9.73× the predicate**.
   - Predicate: **2.9885e-130**.
   - Reported bound: **2.93566e-130**, so accepted.

   The numerator of `D * abs(L[i]) * (dL[0] + dc * W[0])` underflows to zero before division. That omitted first-order contribution is approximately **6.94439e-128**. Thus the implemented bound is not rigorous. Its evaluation must preserve an upper bound or refuse when it cannot.

2. **MAJOR — The zero-loss branch bypasses precision checking and accepts an unsolvable anchor.** [fitting.py:1011](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1011), [templates/index.html:4667](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4667).

   Full window, averaging 2; repeated energies are permitted:

   ```text
   E = [281, 280, 280, 280, 280, 280, 280, 280]
   I = 1e12 + [2^-13, 0, 4, 8, 4, 8, 0, 0]
   ```

   Every discrete loss sum is exactly zero. The exact edge means differ by **2^-14 = 6.103515625e-5**, so no amplitude can satisfy the high-edge anchor. However, both floating-point means round to `1e12`; the branch certifies the constant `1e12` without checking the bound. Its anchor error exceeds the **8e-12** predicate by approximately **7.63 million times**.

Both findings reproduce in either array order: `/api/background` returns **HTTP 200**, the page’s producer accepts, and its restore check returns no failure.

Verification: **87 Python checks and 54 JavaScript checks passed**, including background and certificate parity; two Python tests were blocked by filesystem restrictions. The **1,212-case exact margin**, four measurement summaries, **3/62/56 restore census**, and **2,424-case upload comparison** reproduced. All 404 tested Tougaard target windows remained below the bound threshold. Full browser and full suites were not rerun. No files changed.

**VERDICT: NO-GO.**
