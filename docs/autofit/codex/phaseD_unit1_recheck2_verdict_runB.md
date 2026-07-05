# Codex re-check ROUND 2 — Phase D unit 1 (fix commit 11024a0) — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 52,369.
Prompt: docs/autofit/codex/phaseD_unit1_recheck2_prompt.txt

Residual: CLOSED.

Direct probes:
- Run B probe `{"statistical_area_ratio": {"empirical_bound": {"value": 0.55}}}` is CAUGHT.
- Legal direct ratio field `statistical_area_ratio.value` PASSES.
- Current `element_structure()` output across Z=1..96 has 0 guard violations.
- `pytest` is unavailable here, so I imported the test module with a stubbed `pytest` and drove `_walk` directly.

New findings:

MAJOR: [tests/autofit/test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:201) does not catch integer meV prose, especially comma-grouped values. Probe `{"note": "1,600 meV"}` PASSES, so a future caveat/source string could smuggle an empirical energy/splitting magnitude through guard-checked output. `284.8` and `1.6 eV` are caught; `1,600 meV` is not.

MINOR: Scope claim is not accurate. `11024a0` changes more than the test, `coverage.py` docstring line, and verdict archives: it adds/export `structural_provenance` in [autofit/coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:42) and defines it at [autofit/coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:334). That is production API surface in the D1 residual fix commit.

`bool` leaves pass, but I do not consider that a real empirical-value route. Integers under whitelisted keys like `occupancy` also pass; that risk looks acceptable for legitimate output because those keys are derived bookkeeping and pinned elsewhere, though a malicious patch could abuse semantic key names.

VERDICT: NO-GO
