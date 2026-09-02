# Codex adversarial re-review (round 2) — DSG_LA delta-kernel grid-interp normalization (fix-dsgla-m0-collapse, fcb3dd6) — RUN A (2026-09-02)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 68,917.
Prompt: docs/autofit/codex/dsgla_m0_collapse_r2_review_prompt.txt
Round 1 was NO-GO (stricter of the two runs; archived alongside). The owner
signed off on option (a) — mirror the backend's grid-interp normalization in
JS — and this round reviews that revision. Run B also returned GO ->
round 2 is GO x2; unit passes.

**Findings**

1. MINOR: Round-1 MAJOR is fixed. [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/templates/index.html:4020) now computes the DS core on the caller grid and normalizes via the same ascending-or-reversed grid interpolation as [fitting.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/fitting.py:220). Duplicate x ties are not a practical mismatch here because duplicate x samples produce identical `ds_core` values.

2. MINOR: The new tests are materially adequate for the reported miss. The half-step cases would catch analytic normalization (~`9.69e-4` amplitude-relative miss), and by inspection the descending off-grid case would catch failure to reverse orientation. A nearest-grid normalization would also miss by ~`8.7e-3`, well above `1e-6`.

3. MINOR: I accept the `NaN`/undefined `laM` behavior as pre-existing input hygiene, not a regression blocking this fix. The new array branch does coerce `NaN` to delta via `(p.laM || 0)`, while fit serialization still sanitizes non-finite `laM` to `0.4` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/templates/index.html:6045); malformed frontend state was already divergent from backend fit semantics.

4. MINOR: The `0.001` boundary discontinuity remains unchanged and should stay in the separately tracked moderate-m/quadrature work.

5. MINOR: I could not execute the full parity test locally because the read-only sandbox gives Python no usable temp directory during `lmfit` import. The failure is environmental, not an observed parity assertion failure.

VERDICT: GO
