# Codex review — Phase D unit 1 (coverage.py, commit 884518b) — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 77,334.
Prompt: docs/autofit/codex/phaseD_unit1_coverage_prompt.txt

1. **BLOCKER** [autofit/coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:100): `_RATIO_CAVEAT` emits the empirical Cl 2p `0.55` ratio-bound observation inside every returned statistical-ratio record. Even if PROGRESS.md documents it, it is not derivable element structure and it bypasses the cited-value loader. Failure scenario: `element_structure("U")` returns a U 4f caveat carrying a Cl-specific measured ratio cap. The theoretical `0.5` is fine; the empirical `0.55` should not be emitted by this module.

2. **BLOCKER** [tests/autofit/test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:186): the anti-confabulation guard is not discriminating enough. It checks only the leaf key, so `{"spin_orbit_splitting_ev": {"value": 1.60, "unit": "eV"}}` passes because the leaf key is whitelisted as `value`; `caveat: "binding energy 284.8 eV"` also passes because strings are never scanned. Scalar `*_ev` fields are caught, but wrapped value-bearing fields and string laundering are not.

3. **MINOR** [tests/autofit/test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:160): cache isolation is implemented correctly in [autofit/coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:279), but untested. Failure scenario: returning the cached dict directly on cache hits would let one caller mutate `levels[0]["binding_energy_ev"]` and corrupt later reads while the current tests still pass.

4. **MINOR** [tests/autofit/test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:122): the requested anomaly edge cases are not pinned. Cu/Pd/La/Ce behavior is correct in the module, but a future “helpful” patch encoding real Cu/Pd anomalies could flip `multiplet_prone` for Cu/Pd while preserving total electron count and still pass the current tests.

Test execution note: I could not run pytest in this sandbox because `python3 -m pytest` reports `No module named pytest`; I used direct read-only Python import probes instead.

VERDICT: NO-GO
