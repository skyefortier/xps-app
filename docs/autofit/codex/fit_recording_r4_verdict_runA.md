# Fit recording — Codex round 4, run A (commit 2732fda)

Reviewed `52e5b4a..2732fda`, focusing on `bcb006e..2732fda`. **No BLOCKER or MAJOR findings.**

- **Round 3 centre moves: resolved.** Fully locked fits record every component’s zero displacement, including linked children. All other successful exits call `certify()` and capture the first stop; the exact-zero initial-residual exit also passed.
- **Round 3 averaging: resolved.** `_bgEffect` matches the helpers’ double parsing and clamping. Checks covered empty, decimal, exponent, signed, huge and non-numeric values: 696 Linear curve checks and 145 integral-background checks matched the recorded `k`.
- **Rounds 1 and 2 remain intact.** No regression found in recording, persistence/export paths, whole-vector `moved`, linked/locked centre coverage, background verdicts or software identity.
- **Additivity:** 36 successful local fits across six shapes, locks and linkage had identical existing outputs against `main`. The page/server averaging discrepancy is pre-existing and appropriately deferred: correcting it would change backgrounds.

**MINOR — wording only:** [PROGRESS.md:42](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/docs/autofit/PROGRESS.md:42) says averaging values “1e21 or more” act as `1`. That generalization is inaccurate: decimal `2000000000000000000000` acts as `2`. The code correctly records `2`; the documented `1e21` reproduction is correct. **Category:** documentation about an extreme, out-of-range input; the underlying numerical discrepancy remains a logged follow-up under the owner rule.

Validation: **11 Python tests and 130 JS tests passed**. One Python-backed JS check was blocked by temporary-directory restrictions. Browser/HTTP suites were not rerun. Workspace unchanged.

VERDICT: GO
