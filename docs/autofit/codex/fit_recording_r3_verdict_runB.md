# Fit recording — Codex round 3, run B (commit bcb006e)

Reviewed `52e5b4a..bcb006e`, focusing on the commit after `e8421dc`. **Two MAJOR findings remain.**

1. **Fully locked local fits omit every centre move.** The zero-free-parameter exit skips `certify()`, leaving `firstStopCentres` null. The record therefore contains `centre_moves: []` and `largest_centre_move: null`. Reproduced with a locked Gaussian and with a locked parent plus linked child. Both succeed with zero iterations; each component should have a zero displacement. Round 2’s coverage finding is only partially resolved. [index.html:9511](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:9511)

2. **The background effect can misreport the averaging actually used locally.** Entering `1000000000000000000000` in endpoint averaging produces numeric `1e21`; the background helpers parse that again as `1`, while `_bgEffect` records the window cap. On 101 points with Linear background, the record says `k: 25`, but the curve uses `k: 1`. For `x = 0…100`, `y = 100 + x²`, local endpoints are `[100, 10100]`; the server’s actual `k: 25` gives `[296, 7896]`. A successful local fit also retained this incorrect effect. Run Fit does not enforce the input’s `max="50"`. The underlying numerical discrepancy predates this round; the new record misdescribes it. [index.html:5038](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:5038)

Other checks were favorable:

- Width/amplitude-only movement is now recorded correctly.
- Forty local fits had unchanged existing outputs against `main`, including certificate restarts.
- 16,038 effect-helper comparisons matched; helper parity alone misses finding 2.
- No property leakage or changed stack/restore decisions found.
- Batch Fit and Run Fit’s fallback supply the computed background directly.

Validation: **11 Python tests and 192 JS checks passed**; five Python-backed JS checks were blocked by temporary-directory restrictions. Browser suites were not rerun.

I made no edits. Concurrent uncommitted changes addressing finding 1 appeared during review; this verdict applies to **`bcb006e`**.

VERDICT: NO-GO
