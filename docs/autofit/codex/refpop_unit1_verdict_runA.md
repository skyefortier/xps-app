# Codex review — Unit R1 reference bridge (commit d9e451b) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 92,093.
Prompt: docs/autofit/codex/refpop_unit1_bridge_prompt.txt

1. **MAJOR** [autofit/reference_bridge.py](/Users/skyefortier/xps-app/autofit/reference_bridge.py:100), [autofit/reference_bridge.py](/Users/skyefortier/xps-app/autofit/reference_bridge.py:162), [autofit/coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:424)  
   Legacy survey positions synthesize `expected_region_ev: None` and `spin_orbit: None` by absence. `legacy/survey-lines.json` records contain `be_ev`, not explicit `expected_region_ev` or `spin_orbit`, so these emitted fields are not value-identical pass-through from committed data. Concrete case: `resolve(..., "Li 1s", allow_structural_fallback=True)` emits `reference:legacy:1s` with those null fields. This violates the strict “no defaults / explicit null stays null” rail. Either commit explicit nulls in the legacy data/schema or omit non-existent fields for legacy records.

2. **MAJOR** [tests/autofit/test_reference_bridge.py](/Users/skyefortier/xps-app/tests/autofit/test_reference_bridge.py:148)  
   `test_bridge_emits_nothing_not_in_data_xps` overclaims. It only checks `(symbol, orbital, nominal_be_ev)` against source files. It does not globally verify `expected_region_ev`, `spin_orbit`, or the `reference:legacy:chemical_states` aggregate emitted through structural provenance. A fabricated Cu `spin_orbit`, a defaulted region window outside Ti, or a coverage-layer mutation of chemical-state `be_ev` could bypass this sweep. The separate chemical-state test helps, but the global anti-invention rail should cover every emitted numeric/reference value or narrow its claim.

3. **MINOR** [tests/autofit/test_reference_bridge.py](/Users/skyefortier/xps-app/tests/autofit/test_reference_bridge.py:53)  
   The sidecar join is implemented by transition id and I constructed the failure path: an empty injected machine sidecar raises `ValueError`. But there is no regression test for the refusal, and the current Ti provenance assertion may not catch a wrong-key sidecar join because Ti `2p3/2` and Ti `3p` share the same NIST code/artifact hash. Add a deliberate missing-sidecar test and assert a sidecar field that uniquely identifies the transition if available.

Status mapping judgment: the documented coexistence of `reference:*` and `fit_physics:*` status vocabularies is acceptable because both namespaces carry tier labels and both non-VERIFIED statuses still roll up. `reference:curated:* -> VERIFIED` is defensible for listed values, including current `partial` elements, because the schema says listed partial values are verified even if coverage is incomplete.

Probed boundary cases: Ti 2p, Cu 2p, legacy-only Li 1s, and Tc 3d all kept `candidates == []` and `diagnostic_windows == {}`; Tc emitted no `reference:*`; public bridge returns are deep-copied. Scoped tests run with capture disabled: 9 passed. The API structure-report test could not run in this read-only sandbox because `lmfit/dill` needs a writable temp directory during `app.py` import.

VERDICT: NO-GO
