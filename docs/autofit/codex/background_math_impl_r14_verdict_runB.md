# Background math implementation round 14 — run B (commit d4aca1a; codex exec, reasoning high)

Reviewed `d4aca1a`, read-only. **Two MAJOR findings.**

1. **MAJOR — Tougaard’s rounding bound underflows and falsely certifies.** [fitting.py:1136](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1136), [templates/index.html:4760](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4760).

   Full window, averaging 1:

   ```text
   E = [280, 281, 282, 283]
   I = [2e-110, 3e-110, 1.3e-112, 3e-110]
   ```

   At 282 eV, both sides return `1.7680496899167594e-108`; exact Fraction evaluation gives approximately `1.7680496899166803e-108`.

   The error is **7.90453e-122**, exceeding the **2.987e-122** predicate by **2.646×**. Nevertheless, the computed bound is only **2.16657e-122**, so certification succeeds.

   Specifically, the numerator of `D * abs(L[i]) * (dL0 + dc*W0) / L0²` underflows to zero. Evaluating that term with scaled arithmetic gives approximately **3.77913e-120**, or **126.5× the predicate**. The bound’s own arithmetic silently discards the amplification error it must cover.

2. **MAJOR — Tougaard’s zero-loss branch bypasses edge-mean rounding checks.** [fitting.py:1011](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1011), [templates/index.html:4667](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4667).

   Full window, averaging 2:

   ```text
   E = [280, 281, 282, 283, 284, 285, 286, 287]
   I = [1, 1, 1, 1, 1, 1, 1, 1.0000000000000002]
   ```

   Both implementations certify a constant `1`. The exact low-edge mean is `1`; the exact high-edge mean is `1 + 2^-53`. Floating-point averaging makes them compare equal, and the all-zero loss branch returns success without invoking the bound.

   The exact loss vector is zero, so no amplitude can satisfy the unequal edge levels. The returned curve misses the high-edge anchor by **half the intensity span**, or **5×10¹¹ times the predicate**.

Both cases reproduce in both energy orders. The page’s throwing producer returns them successfully; restoration accepts both exact and six-significant-digit saved curves. `/api/background` returns **HTTP 200**, verified using in-memory sessions.

Verification: **78 Python and 64 JavaScript checks passed**, including background/certificate parity. The **1,212-case exact margin sweep**, four measurement summaries, **3/62/56 restore census**, **376 Smart comparisons**, and **2,424 upload-rounding cases** reproduced. No committed-data refusal was found. Full browser and full suites were not rerun. No files changed.

**VERDICT: NO-GO.**
