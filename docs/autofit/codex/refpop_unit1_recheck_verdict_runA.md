# Codex re-check — Unit R1 dispositions — RUN A (2026-07-05, post-quota-reset retry)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 89,019.
Prompt: docs/autofit/codex/refpop_unit1_recheck_prompt.txt
NOTE: retry — attempt 1 (both runs) died on the Codex usage limit with no verdict (logged).

FINDING 1: CLOSED.  
[reference_bridge.py](/Users/skyefortier/xps-app/autofit/reference_bridge.py:119) and [coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:426) now preserve key presence. Direct probe: Li `1s` legacy has neither `expected_region_ev` nor `spin_orbit` in bridge or coverage relay; Ti `2p3/2` machine has `spin_orbit` present as `None`; Cu `2p` curated matches committed spin-orbit/window fields.

FINDING 2: CLOSED for the requested scenarios.  
The sweep at [test_reference_bridge.py](/Users/skyefortier/xps-app/tests/autofit/test_reference_bridge.py:148) checks nominal, `expected_region_ev`, and `spin_orbit` with absence semantics. The relay test at [test_reference_bridge.py](/Users/skyefortier/xps-app/tests/autofit/test_reference_bridge.py:206) catches coverage-layer value mutation. Direct mutation probes caught: fabricated curated `spin_orbit`, defaulted legacy region window, and coverage-layer chemical-state `be_ev` mutation.

FINDING 3: CLOSED.  
`_join_machine_sidecar` refuses missing sidecars at [reference_bridge.py](/Users/skyefortier/xps-app/autofit/reference_bridge.py:69). The uniqueness pin at [test_reference_bridge.py](/Users/skyefortier/xps-app/tests/autofit/test_reference_bridge.py:234) has real discrimination: Ti `2p3/2` sidecar nominal `453.98` differs from Ti `3p` `32.47`, and missing sidecar raises `ValueError`.

New finding: MINOR [test_reference_bridge.py](/Users/skyefortier/xps-app/tests/autofit/test_reference_bridge.py:221).  
The relay test uses `.get()` for optional fields, so it does not distinguish absent keys from explicit `None`. Concrete scenario: a future coverage relay regression emits `expected_region_ev: None` and `spin_orbit: None` for legacy Li `1s`; the current relay test passes. Current production code is correct, so this is a regression-test gap, not an observed bridge defect.

I could not run real `pytest` because `pytest` and `jsonschema` are unavailable in this sandbox; I used direct import probes with stubs for the missing loader/test dependencies.

VERDICT: GO
