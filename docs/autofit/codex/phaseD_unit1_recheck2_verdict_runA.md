# Codex re-check ROUND 2 — Phase D unit 1 (fix commit 11024a0) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 50,344.
Prompt: docs/autofit/codex/phaseD_unit1_recheck2_prompt.txt

Residual: CLOSED. The exact-path guard at [test_coverage_structure.py:240](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:240) now catches `statistical_area_ratio.empirical_bound.value = 0.55`, while the legal `.statistical_area_ratio.value` still passes.

New findings:

MAJOR: [test_coverage_structure.py:201](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:201) misses `meV` string laundering. Direct probes: `"284.8"`, `"1.6 eV"`, and `"1600 eV"` are caught, but `"1,600 meV"`, `"1600 meV"`, and `"600 meV"` pass. Concrete scenario: a future caveat/source string says `"spin-orbit splitting around 1,600 meV"` under a non-value-bearing key and the guard accepts it.

MAJOR: scope is not as stated. `git diff 11024a0^ 11024a0` shows `autofit/coverage.py` changed by 101 insertions/1 deletion, including public export changes at [coverage.py:42](/Users/skyefortier/xps-app/autofit/coverage.py:42) and new `structural_provenance` API at [coverage.py:334](/Users/skyefortier/xps-app/autofit/coverage.py:334). Concrete scenario: this recheck would approve an unrelated Phase D unit 3 API addition while reviewing a Phase D unit 1 guard/docstring fix.

Notes: novel numeric keys and list-wrapped numeric `value` probes are caught. Bool leaves pass by design. An integer hidden under a whitelisted key like `occupancy` passes the guard, but I’d treat that as malicious semantic misuse of a structural field, not a realistic remaining residual.

VERDICT: NO-GO
