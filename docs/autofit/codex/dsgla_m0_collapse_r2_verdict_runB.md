# Codex adversarial re-review (round 2) — DSG_LA delta-kernel grid-interp normalization (fix-dsgla-m0-collapse, fcb3dd6) — RUN B (2026-09-02)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 76,527.
Prompt: docs/autofit/codex/dsgla_m0_collapse_r2_review_prompt.txt
Round 1 was NO-GO (stricter of the two runs; archived alongside). The owner
signed off on option (a) — mirror the backend's grid-interp normalization in
JS — and this round reviews that revision. Run A also returned GO ->
round 2 is GO x2; unit passes.

**Findings**

1. MINOR: Duplicate-x grids are not exactly `np.interp`-identical. `np.interp` returns the last duplicate value for an exact duplicate key; [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/templates/index.html:4038) stops at the first `x >= center`. For normal strictly monotonic acquisition grids, including center exactly on a unique grid point, the implementation matches the backend path in [fitting.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/fitting.py:220).

2. MINOR: I accept the negative/NaN `laM` behavior as pre-existing hygiene, not a blocking regression. Negative `laM` takes the delta path like the backend clamp-to-zero path; non-finite `laM` can now render as delta in `evalPeakArray`, but fit flows sanitize it to `0.4` in [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/templates/index.html:6045) before backend submission.

3. MINOR: The `0.001` threshold discontinuity and the moderate-`m` quadrature gap remain unchanged and separately tracked. This branch correctly scopes itself to the backend’s delta-kernel behavior below the threshold.

4. MINOR: Test adequacy is materially improved. The half-step off-grid cases would catch analytic normalization and nearest-grid normalization; the descending off-grid case would catch missing backend-style reversal. I could not run the full parity suite here because the read-only sandbox provides no usable temp directory for Python dependency imports, but the test structure and numeric sensitivity are sound.

VERDICT: GO
