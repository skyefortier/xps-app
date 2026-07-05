# Codex review — Phase D unit 1 (coverage.py, commit 884518b) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 110,585.
Prompt: docs/autofit/codex/phaseD_unit1_coverage_prompt.txt

1. **BLOCKER** [coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:100): `_RATIO_CAVEAT` emits the empirical Cl 2p `0.55` ratio-bound result in every filled p/d/f ratio record. Under the rail as written, I would not treat that as legitimate in-module provenance context: it is a repo-documented empirical fit outcome, but it is still an empirical numeric value emitted by `coverage.py` outside the cited-value loader. Concrete failure scenario: `level_structure("U", "4f")["statistical_area_ratio"]["caveat"]` now returns a Cl-anchor empirical value even though U 4f coverage should contain only derivable quantum bookkeeping.

2. **MAJOR** [test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:186): the anti-confabulation guard does not fully discriminate laundering. It catches populated `*_ev` fields and most new numeric keys, but it globally whitelists the generic key `value` and never inspects numeric strings. Concrete failure scenario: a future record like `{"empirical": {"value": 198.3}}` or a caveat string containing `"198.3 eV"` can pass the guard if the path avoids the regex, while still emitting an empirical value.

3. **MINOR** [test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:160): cache isolation is not tested, although the current implementation passes manual first-call and cache-hit mutation checks. Concrete failure scenario: removing one `copy.deepcopy` in `element_structure()` would let callers corrupt cached structures, and this test file would still pass.

VERDICT: NO-GO
