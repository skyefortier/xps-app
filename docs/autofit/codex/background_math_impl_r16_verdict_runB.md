# Background math implementation round 16 — run B (commit 848ff1e; codex exec, reasoning high)

Reviewed `848ff1e`, read-only. **One MAJOR finding.**

**MAJOR — Linear and Manual accept final-rounding errors outside the certificate’s predicate.** [fitting.py:567](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/fitting.py:567), [templates/index.html:5092](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:5092), [manual branch:5055](/Users/skyefortier/xps-app/.claude/worktrees/bg-math-implement/templates/index.html:5055).

Select Linear with the full window:

```text
E = [0, 1, 3]
I = [1000000000000, 1000000000000, 1000000000001]
```

Manual reproduces with anchors at the two endpoints; its no-anchor fallback also reproduces.

At `E=1`, the defining affine relation gives exactly `10^12 + 1/3`. Both implementations return `1000000000000.3333740234375`.

- Exact error: **1/24576 ≈ 4.06901e−5**.
- Window span: **1**; predicate: **1e−12**.
- Error/predicate: **40,690,104×**.

The rational interpolation is correct, but converting its result to binary64 introduces this error. The explicit-background guards check only finiteness and accept it unconditionally. Correct rounding alone does not meet the requested span-relative predicate; these inputs require refusal.

Reproduced in **both energy orders**: `/api/background` returns **HTTP 200**, the page’s throwing producer accepts, `_doSaveSpectrum` saves the curve with `backgroundFailure:null`, and restoration accepts it.

Verification:

- **89 Python and 54 JavaScript checks passed**, including round-15 reproducers, producer/consumer guards, and parity.
- **128 loader cases passed** across all eight methods, both formats/orders, exact/rounded saves, and corrupted curves.
- All **606 committed Tougaard backgrounds** remain bit-identical to round 15, none refused; maximum bound/predicate **0.0432515**.
- The **1,212-case exact margin**, four measurement summaries, **3/62/56 restore census**, and **2,424-case upload comparison** reproduced.
- An additional **8,000-case Tougaard probe** found no accepted violation; 5,913 accepted cases were checked using exact rational evaluation.
- CI floor remains **538**. Full suites and browser tests were not rerun. No files changed; dispositioned issues were not re-raised.

**VERDICT: NO-GO.**
