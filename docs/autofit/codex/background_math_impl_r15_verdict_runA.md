# Background math implementation round 15 — run A (commit 41b60d8; codex exec, reasoning high)

**MAJOR — Tougaard’s bound certifies a large error when its denominator nearly cancels.** [fitting.py:1192](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:1192), [templates/index.html:4824](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:4824).

Concrete reproducer: full window, Tougaard, endpoint averaging **3**:

```python
E = [333., 280. + 2**-44, 280.] + [245.21875] * 9
I = [146.21875000000003, 162.78125, 75.] + [128.] * 9
```

Both implementations certify a constant **128**. Exact rational evaluation of the stated relation gives **62.58632106707016** at the second point.

- Actual error: **65.41367893292984**.
- Predicate: **8.778125e-11**.
- Error/predicate: **7.45 × 10¹¹**.
- Reported bound: **3.2042277982272133e-12**, so accepted.

The exact edge means differ by `2^-45 / 3`, but both computed means equal 128. Consequently, computed `D = 0` removes the denominator-error terms. Meanwhile, `q[0] ≈ 26.38`: the estimated denominator uncertainty already exceeds its computed magnitude. The first-order expansion provides no rigorous bound here; the neglected interactions are greatly amplified. Normalisation and the `1 + 64u` enlargement do not address this.

The computed loss is nonzero, so the new exact zero-loss guard is bypassed. This reproduces in **both array orders**: `/api/background` returns **HTTP 200**, the page’s throwing producer returns the curve, and restoration accepts it. Certification needs a justified denominator bound, or refusal when denominator uncertainty includes zero.

Verification: **79 Python tests and 54 JavaScript tests passed**, including background and certificate parity; two Python tests were blocked by filesystem restrictions. Reproduced the **1,212-case exact margin**, all four measurement summaries, **3/62/56 restore census**, and **2,424-case upload comparison**. All **606 committed Tougaard backgrounds remain bit-identical** to round 14’s predecessor, with maximum bound/predicate **0.04321**. CI floor is configured at **538**; full suites and browser tests were not rerun. No files changed.

**VERDICT: NO-GO.**
