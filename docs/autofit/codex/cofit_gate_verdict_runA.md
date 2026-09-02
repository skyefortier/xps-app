# Codex adversarial review — u4f co-fit gate flake fix (fix-u4f-cofit-gate-flake) — round 1, RUN A (2026-09-02, reviewed at 61ba15b)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 122,855.
Prompt: docs/autofit/codex/cofit_gate_review_prompt.txt
Round 1: run A NO-GO / run B GO (stricter governs) — both converged on a co-fit-specific ~1.05 factor instead of the borrowed 1.2.

**Findings**

1. **MAJOR** - The new bound hides a real co-fit regression channel. The remaining co-fit assertions only check N 1s presence/center/tagging, U 4f7/2 and 4f5/2 centers, and phase leakage ([test_u4f_parity_gate.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/tests/autofit/test_u4f_parity_gate.py:112)). U ratio/shape/satellite checks are in the single-region test, not this co-fit gate. The old bare chi-square assertion would still catch degraded overlap allocation, missing/weak satellites, bad N/U weight split, background drift, or poorer composed-candidate selection when centers remain acceptable. The 11.40-13.68 window is therefore not proven noise-only.

2. **MAJOR** - `CHIR_FACTOR = 1.2` is too loose for the claimed flake envelope. The best argument for 1.2 is consistency with the file-level constant and the rough/multimodal expert anchor. The stronger argument against it is that the measured bad state is only `11.69 / 11.40 = 1.025`; a co-fit-specific `1.05` would cover that with margin while preserving the gate’s fit-quality value. Given the missing co-fit satellite/envelope assertions, I would use a tighter co-fit factor or add explicit co-fit envelope/satellite checks before accepting 1.2.

3. **MAJOR** - The stated nondeterminism mechanism is only partly supported by code. Wall-clock truncation is plausible: the co-fit resolves to eight composed candidates, which exceeds `SCREEN_TOP_K = 6`, and the engine has screen/deep deadlines plus per-candidate stability cutoff ([engine.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/autofit/engine.py:2731), [engine.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/autofit/engine.py:1205)). But I did not find an order-critical process-hash path here: grammar composition is ordered, preseed/pool paths sort, and screen ranking sorts by BIC. Seed-pinning does not address wall-clock truncation, but the hash-seed part reads overstated.

4. **MINOR** - The “file’s own established bound” rationale is weaker than claimed. The single-region gate does use `CHIR_FACTOR` ([test_u4f_parity_gate.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/tests/autofit/test_u4f_parity_gate.py:90)), but there is no real in-file rationale for 1.2 beyond the terse constant comment, and that gate also has tighter U-specific structural checks than the co-fit. This is precedent, not sufficient justification.

5. **MINOR** - Alternative designs are not strictly better, but the chosen one is still overbroad. A flaky/rerun marker would normalize nondeterminism and burn runtime; moving this to the slow env-gated suite would reduce noise but weaken always-on phase-composition coverage; seed-pinning is already present and cannot pin wall-clock load. The better narrow fix is a co-fit-specific measured tolerance, preferably around 1.05, plus comment cleanup. Also, the commit says 3/8 firings while the new in-file comment says 2/5.

VERDICT: NO-GO — Widening to 1.2 is not justified for this co-fit gate because it masks a real fit-quality regression channel that the remaining assertions do not cover.
