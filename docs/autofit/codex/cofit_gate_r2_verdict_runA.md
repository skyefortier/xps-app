# Codex adversarial review — u4f co-fit gate flake fix (fix-u4f-cofit-gate-flake) — round 2, RUN A (2026-09-02, reviewed at 801f386)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 170,022.
Prompt: docs/autofit/codex/cofit_gate_r2_review_prompt.txt
Round 2: run A NO-GO / run B GO — both caught the author's factually wrong 'satfree = no satellites' rationale; satellite-presence assertions are safe and required.

**Findings**

1. **MAJOR** - [tests/autofit/test_u4f_parity_gate.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/tests/autofit/test_u4f_parity_gate.py:144) rejects co-fit satellite assertions on an unsound rationale. The documented good winner `U2_mains_satfree+N0_asymGL` and bad-state winner `U1_mains_satpair+N0_pv+bfix` both have U satellite slots in [autofit/regions/u4f.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/autofit/regions/u4f.py:280). `satfree` means independently free satellites, not no satellites. So the branch still allows a co-fit result with U mains + N 1s + χ²ᵣ under 1.05× expert but no emitted U satellites, leaving the overlap allocation / N-vs-U split channel under-policed.

2. **MINOR** - The `1.05` number itself is reasonably placed from the captured value: live fixture `chiReduced` is `11.399870385521767`, known bad state is `11.688`, ratio `1.0253`, threshold about `11.97`. I would not pick a different factor without measured load-state distribution. The uncaptured morning spike values are residual risk, but branch-green under the same window is enough support for the scalar bound; it does not compensate for missing structural assertions.

3. **MINOR** - [tests/autofit/test_u4f_parity_gate.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-u4f-cofit-gate-flake/tests/autofit/test_u4f_parity_gate.py:135) still says the old failures were “always passing standalone,” while the new evidence says main’s bare assertion failed standalone under load. That is documentation drift in a rationale comment, not the primary defect.

I could not run the test here: this worktree has no `venv/bin/pytest`, no `pytest` on PATH, and system Python is missing `lmfit`.

VERDICT: NO-GO — the co-fit satellite-check rejection is factually unsupported, so the loosened χ²ᵣ assertion still leaves a documented co-fit regression channel inadequately policed.
