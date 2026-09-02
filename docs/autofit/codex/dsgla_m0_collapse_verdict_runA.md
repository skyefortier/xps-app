# Codex adversarial review — DSG_LA m->0 delta-kernel fix (fix-dsgla-m0-collapse, 7e7767e) — RUN A (2026-09-02, overnight session)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 98,910.
Prompt: docs/autofit/codex/dsgla_m0_collapse_review_prompt.txt
Run B on the identical prompt/repo state returned GO rating the same normalization
finding MINOR; stricter verdict governs per project rule -> unit is NO-GO, STOPPED
without iteration (overnight rule: no unsupervised iteration against a NO-GO).
The off-grid-center 9.69e-4 figure was independently reproduced by the session
(scratchpad verify_offgrid: 9.69e-04 of amplitude at center half-step off-grid).

**Findings**

1. **MAJOR**: Delta-branch normalization is not backend-parity off-grid. JS normalizes by analytic `laCasaXPSCore(0, ...)` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/templates/index.html:3892), while backend normalizes by `np.interp(center, x, ds_core)` on the supplied data grid at [fitting.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/fitting.py:220). With the test params on a 0.05 eV grid shifted half a step, I get ~`9.69e-4` of amplitude max diff, far above `1e-6`; a 0.2 eV grid gives ~`1.55e-2`. Descending grids do not add a new issue because backend reverses before interpolation, but center-between-points is common for fitted peaks. The current test center is exactly on-grid at [tests/js/lineshape_parity.test.js](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/tests/js/lineshape_parity.test.js:84), so it hides this.

2. **MINOR**: Threshold semantics differ for malformed/transient `laM`. Negative finite values match: JS takes delta; backend clamps to `0.0` then takes delta. At raw evaluator level, `NaN`/`undefined` do not take the JS delta branch and collapse through the quadrature; app-to-backend serialization instead falls back to `0.4` for non-finite `p.laM` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/templates/index.html:5993). `null`/empty string are worse in JS because coercive `<` treats them as `0`, while backend spec fallback treats them as non-finite/default. Normal UI state usually has `laM`, but [updatePeakParam](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsgla-m0-collapse/templates/index.html:5512) does not clamp `laM`.

3. **MINOR**: Boundary discontinuity is still severe just above the cutoff. On the representative on-grid case, `m=0.00099` returns center `1.0 * amplitude` and max `1.0185 * amplitude`; `m=0.001`/`0.0011` falls into the old quadrature path and evaluates to ~zero on that grid. So a user crossing exactly through `0.001` sees roughly a full-amplitude drop. This is not worse for the `>=0.001` side than pre-fix, and the visible input/fallback fit clamps generally keep `laM >= 0.05`, but the discontinuity is real for imported/scripted/fixed values.

4. **MINOR**: Caller review found no legitimate dependency on the old collapse-to-zero behavior. Chart/model/results/save/export paths route through `evalPeakArray`; `DSG_LA` then falls through to the fixed `evalPeak` path. Local LM clamps `laM` to `0.05..4.0`, linked sync propagates `laM`, and exports read the active shape fields. Disabling a peak should use visibility/amplitude, not an accidental numerical collapse.

5. **MINOR**: The two new tests pin the happy-path fix but not the risky surface. They would catch returning the unnormalised core or common wrong beta exponent normalizations with the chosen `beta=0.7`; they do not cover off-grid centers, descending off-grid grids, exact `0.001`, or malformed `laM`. I could not complete `node --test tests/js/lineshape_parity.test.js` locally because Python import of `lmfit` requires a writable temp directory, which this sandbox lacks.

VERDICT: NO-GO — the claimed frontend/backend parity fails above tolerance for realistic off-grid peak centers in the new delta branch.
