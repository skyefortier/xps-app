# Codex adversarial review — u4f co-fit gate flake fix (fix-u4f-cofit-gate-flake) — round 1, RUN B (2026-09-02, reviewed at 61ba15b)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 148,234.
Prompt: docs/autofit/codex/cofit_gate_review_prompt.txt
Round 1: run A NO-GO / run B GO (stricter governs) — both converged on a co-fit-specific ~1.05 factor instead of the borrowed 1.2.

**Findings**

1. **MINOR** — The new bound does miss a real but narrow regression channel: co-fit winners with χ²ᵣ in `11.40..13.68`. The remaining assertions in [test_u4f_parity_gate.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/tests/autofit/test_u4f_parity_gate.py:112) check N 1s, U main positions, phase tags, and leakage, but do not explicitly require co-fit satellite presence or satellite/ratio quality. So the old assertion could catch mild overlap-residual or missing-satellite regressions that preserve main positions. Given the documented good state is ~7.1 and the known bad flake is ~11.69, I’d rate that window as mostly noise, but “any genuine regression” is overstated.

2. **MINOR** — `1.05` would be the stricter flake-quarantine factor from measured wobble alone: `11.69 / 11.40 = 1.025`, so `1.05` leaves headroom and closes most of the newly opened window. The case for `1.2` is consistency with the existing `CHIR_FACTOR` precedent at [test_u4f_parity_gate.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/tests/autofit/test_u4f_parity_gate.py:37), plus the fact this is a known-rough multi-modal anchor rather than a numeric battery. I’d accept `1.2`, but only because the good-state margin is large.

3. **MINOR** — The in-file precedent is real, not pure rationalization: the single-region gate already applies `CHIR_FACTOR` to expert χ²ᵣ at [test_u4f_parity_gate.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/tests/autofit/test_u4f_parity_gate.py:90). It is not perfectly analogous, though, because single-region also has explicit satellite presence, splitting, ratio, and shape-sharing assertions; the co-fit check is thinner.

4. **MINOR** — The wall-clock mechanism is plausible from code: `run_stability_analysis` skips remaining refits after a `time.perf_counter()` deadline, so load can alter which refits run and whether a deeper refit is promoted at [engine.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/autofit/engine.py:1205). Screening/deep evaluation also uses wall-clock budgets at [engine.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/autofit/engine.py:2731) and [engine.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/autofit/engine.py:2780). The specific process-hash ordering claim is less directly proven: current grammar composition is deterministic and many set-derived outputs are sorted, but project notes do document the historical 11.688 failure and the suspected unpinned hash path.

5. **MINOR** — Alternatives are not strictly better. Rerun/flaky markers would hide the same channel with worse signal. Seed pinning is already applied to refits, but cannot pin wall-clock truncation; `PYTHONHASHSEED` may help externally but is not an in-process test fix. Moving this to `RUN_AUTOFIT_GATE` would reduce suite noise but also remove normal-suite coverage of the co-fit behavior. I could not execute the test here because this worktree environment lacks `pytest` and `lmfit`.

VERDICT: GO
