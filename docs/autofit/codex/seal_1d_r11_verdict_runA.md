**Three MINOR findings remain. No BLOCKER or MAJOR found.**

1. **The concrete round-10 runtime cases are resolved; the testing concern is only partly resolved.** The validator now accepts the listed IDs, rejects the malformed link targets/spellings, requires components, and rejects inexact integers. The corresponding regression tests pass. The new oracle still falls short of its stated coverage, detailed below. [fitting.py:247](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:247), [fitting.py:285](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:285), [tests/test_seal_1d_compare.py:221](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:221)

2. **No: the validator still rejects a server-written response and accepts structures the producer cannot write.**

   **MINOR — the integer rule rejects a valid component ID.** Path: `individual_peaks[0].id = 9007199254740993`. Using the well-posed fixture, I reproduced `/api/fit → 200, success: true`, followed by self-comparison returning **400**. The producer uses the ID’s spelling for parameter names and echoes the original integer; `_representable` instead requires every integer, including IDs, to survive float conversion exactly. Thus “any ID the server accepts” and the blanket integer rule are currently incompatible. [fitting.py:2796](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:2796), [fitting.py:3155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3155), [fitting.py:232](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:232)

   **MINOR — producer-required relationships remain unchecked.** I reproduced these accepted non-responses:

   - Set `individual_peaks[1].params.center` to `vary=false, expr="p1_center + 0.0"`, leaving its amplitude unlinked. The validator checks expressions independently, but the producer always emits centre and amplitude links together. [fitting.py:272](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:272), [fitting.py:1854](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:1854)
   - Add `individual_peaks[0].support.follows = "nonexistent"`. The schema accepts any scalar there, whereas the producer only writes an existing root component’s ID. [fitting.py:3464](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3464), [fitting.py:3177](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/fitting.py:3177)

   Both examples return **200 on a, b, and both**, with self-comparison reporting **`same: true`**.

3. **I did not reproduce a body that returns 500.** The hostile tests and 3,000-mutation fuzz pass. That is bounded evidence, not proof for every body; unexpected comparator exceptions still explicitly return 500. The demonstrated malformed responses above return 200 instead of the required 4xx. [app.py:1480](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/app.py:1480)

4. **The tests establish their sampled regressions, but not all stated claims.**

   **MINOR — the oracle skips mandatory fields.** `OPTIONAL_KEYS` applies globally by key name, so it skips deleting mandatory top-level `message` and mandatory `background_verdict.reason`. I confirmed this with an in-memory mutation allowing a missing top-level `message`: **the oracle still passed**. Requiredness must be determined by object/path. [tests/test_seal_1d_compare.py:359](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:359), [tests/test_seal_1d_compare.py:381](/Users/skyefortier/xps-app/.claude/worktrees/seal-1d/tests/test_seal_1d_compare.py:381)

   Read-only verification using in-memory upload sessions completed with **212 passed, 1 skipped** across comparison, comparator, and numerics-version tests. This included all **328 records**, the fuzz, oracle, and expanded real-fit cases. The numerics digest passed. I did not rerun the full claimed 394-test set or complete mutation campaign.

No files changed.

**VERDICT: NO-GO**
