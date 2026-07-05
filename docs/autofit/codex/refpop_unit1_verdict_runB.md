# Codex review — Unit R1 reference bridge (commit d9e451b) — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 81,707.
Prompt: docs/autofit/codex/refpop_unit1_bridge_prompt.txt

1. MINOR [tests/autofit/test_reference_bridge.py](/Users/skyefortier/xps-app/tests/autofit/test_reference_bridge.py:148): the global anti-invention sweep only asserts `(symbol, orbital, nominal_be_ev)`. It does not globally assert `expected_region_ev` or `spin_orbit`, even though those are emitted in [autofit/coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:423). Concrete failure scenario: a regression fabricates curated `spin_orbit` or `expected_region_ev` in [autofit/reference_bridge.py](/Users/skyefortier/xps-app/autofit/reference_bridge.py:100), while leaving nominal BEs correct; the sweep would still pass. I verified the current implementation is value-identical with a stricter full-field probe, so this is a test hardening issue, not an observed bridge defect.

No BLOCKER or MAJOR findings.

Status judgment: the documented tier/status coexistence is acceptable for R1 because every record carries its tier label and both [autofit/reference_bridge.py](/Users/skyefortier/xps-app/autofit/reference_bridge.py:22) and [docs/autofit/PROGRESS.md](/Users/skyefortier/xps-app/docs/autofit/PROGRESS.md:1513) explicitly disclose the deviation. Curated → VERIFIED is defensible under the schema’s “verified against cited sources” definition and the updated D3 boundary pin limiting VERIFIED sourced records to `reference:curated:*`.

Probes: scoped tests passed with capture disabled: `9 passed`. Direct probes confirmed Ti 2p, Cu 2p, legacy-only Li 1s, and uncovered Tc 3d produce `candidates == []`, `diagnostic_windows == {}`, preserve the naked `binding_energy_ev=None/UNVERIFIED`, and emit no `reference:*` records for Tc. A constructed missing machine sidecar raised `ValueError: machine transition Be-1s has no provenance sidecar record`.

VERDICT: GO
