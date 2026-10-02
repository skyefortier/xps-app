# Background math implementation round 15 — run B (commit 41b60d8; codex exec, reasoning high)

Reviewed `41b60d8`, read-only. **Two MAJOR findings.**

1. **MAJOR — Tougaard’s bound falsely certifies severe cancellation when the computed edge difference is zero.** [fitting.py:1192](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1192), [templates/index.html:4824](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4824).

   Full window, averaging **2**, using these exact binary64 inputs:

   ```text
   E = [55.4022790912908, 55.4022790912908,
        32, 32, 31.999999999999996, 31.999999999999996, 24, 24]
   I = [12, 12.000000000000002, 15.999999999999998,
        12, 12, 0.2988604543545996, 12, 12]
   ```

   Both implementations certify constant **12**. Exact Fraction evaluation of the defining relation gives approximately **−329.71280540692726** at the two 32-eV points.

   Error: **341.7128054**; predicate: **1.57011395e−11**—approximately **2.18×10¹³ times the predicate**. Nevertheless, the normalized bound is **2.05846e−15**, below its **9.81321e−13** threshold.

   The exact edge difference is `2^-50`, but the computed difference `D` is zero, eliminating every `q` contribution. Meanwhile, the exact high-edge loss is approximately **4.58869e−34**, versus a computed **1.11022e−16** before intensity normalization. The first-order expansion is used without establishing a positive lower bound on the exact denominator; its neglected interactions dominate. The certificate must refuse this conditioning or validate the ratio rigorously.

2. **MAJOR — Rescaling underflow to zero bypasses the new subnormal refusal.** [fitting.py:954](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:954), [templates/index.html:4646](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4646).

   Full window, averaging **3**:

   ```text
   η = 2^-1074
   E = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
   I = η × [1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0]
   ```

   The normalized computation passes its bound. Scaling back rounds the entire curve to zero, and the guard explicitly exempts zero. Both sides certify it.

   The exact high-edge anchor is **η/3**, so the returned zero misses by **one-third of the intensity span**, approximately **3.33×10¹¹ times the predicate**. Lost nonzero values must be detected even when they round to zero.

Both findings reproduce in **both energy orders**. The page’s throwing producer accepts them; `/api/background` returns **HTTP 200**; restoration accepts their stored curves.

Verification: **88 Python and 64 JavaScript focused checks passed**. The 1,212-case exact margin sweep, four measurement summaries, 3/62/56 restore census, and 2,424-case upload comparison reproduce. All **606 committed Tougaard backgrounds** remain bit-identical to the previous computation, with no refusals and maximum bound/predicate **0.04321**. Full browser and full suites were not rerun. No files changed.

**VERDICT: NO-GO**
