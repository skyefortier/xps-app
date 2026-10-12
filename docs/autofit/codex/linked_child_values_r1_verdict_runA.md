# Linked child values (Q10 0c) — Codex round 1, run A (commit 47d5110)

Two MAJOR findings prevent approval.

1. **MAJOR — Python write-back no longer matches the page, while its equivalence test still passes.** [apply_backend_params](/Users/skyefortier/xps-app/.claude/worktrees/linked-child/autofit/reference.py:170) retains the old lock rule. Using a real GL fit response, the page takes centre `380.9038`, amplitude `9014.0152`, width `1.60047`, mix `72.3037`; Python keeps `383.8`, `300`, `3.1`, `10`. The [equivalence test](/Users/skyefortier/xps-app/.claude/worktrees/linked-child/tests/js/lineshape_roundtrip.test.js:268) supplies only `expr: null`, so it cannot detect this divergence. Update the twin and cover expression-bearing locked fields. This affects the reference/refit tooling, not Batch Fit. **Non-physical inputs required: no.**

2. **MAJOR — the LA test does not prove its claimed locked-field coverage.** The [new fixture](/Users/skyefortier/xps-app/.claude/worktrees/linked-child/tests/js/lineshape_roundtrip.test.js:164) omits `caM` and `fixCaM`; the child’s `caM` remains unlocked. I restored the old rule for **only `m`**, in memory: all six new tests and the twin-equivalence test still passed. Add a stale, locked `caM` and assert the returned expression value directly. **Non-physical inputs required: no.**

**MINOR — the alternative fixture is not a possible server solution.** In the [preview test](/Users/skyefortier/xps-app/.claude/worktrees/linked-child/tests/js/scattered_starts.test.js:306), the alternative parent amplitude is `1000` and the child ratio is `0.03`, but the asserted child amplitude is `3000`, rather than `30`. It genuinely tests copying through `_altPeaks` and fails under the old rule; it does not establish parity with a physically consistent server alternative. **Requires an inconsistent synthetic response: yes.**

The remaining checks support the implementation:

- Server expressions for the parameters being applied originate in link constraints; I found no unlinked locked parameter newly overwritten. Shape guards, including Voigt mix preservation, remain intact.
- Run Fit, Auto-Fit and successful alternative adoption use the corrected apply function. Batch Fit’s local engine already synchronizes children regardless of locks. History/restore copy stored peaks; existing stale historical records are not repaired.
- Measurement reproduced: **67 linked children, 12 carrying locks, zero active-parameter discrepancies, nine inactive Voigt mix differences**. All 12 locks are inactive `fixCaM` flags.
- All six new tests pass on HEAD and fail with the old rule. Targeted execution used an in-memory adjustment for read-only Python initialization; this was not a full-suite pass.
- No unrelated runtime changes found; workspace unchanged.

VERDICT: NO-GO.
