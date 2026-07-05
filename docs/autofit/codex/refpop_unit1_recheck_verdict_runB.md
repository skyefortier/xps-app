# Codex re-check — Unit R1 dispositions — RUN B (2026-07-05, post-quota-reset retry)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 97,913.
Prompt: docs/autofit/codex/refpop_unit1_recheck_prompt.txt
NOTE: retry — attempt 1 (both runs) died on the Codex usage limit with no verdict (logged).

FINDING 1: CLOSED.  
`_add_position` only relays `expected_region_ev` / `spin_orbit` when the source transition has the key, and `coverage.structural_provenance` mirrors that omission. Direct probe: `Li 1s` legacy has neither key in bridge or coverage output; `Ti 2p3/2` machine has `spin_orbit: None`; `Cu 2p` curated carries the committed spin-orbit objects.

FINDING 2: CLOSED, with a new minor test-hardening note.  
The full-field bridge sweep catches fabricated curated `spin_orbit` and defaulted legacy region windows. The relay test catches a coverage-layer chemical-state `be_ev` mutation. Targeted tests: `10 passed`.

FINDING 3: NOT-CLOSED as a regression pin, not as current production behavior.  
`_join_machine_sidecar` itself joins by transition id and refusal is tested. But `tests/autofit/test_reference_bridge.py:251` does not actually prove the joined sidecar was the right one: the asserted `nominal_be_ev` comes from the machine transition, not from emitted joined provenance. I monkeypatched `Ti-3p` to receive the `Ti-2p3/2` sidecar and `test_machine_sidecar_join_refusal_and_uniqueness` still passed.

New MINOR: `tests/autofit/test_reference_bridge.py:221` uses `.get()` for relay comparison, so a coverage regression that synthesizes `expected_region_ev: None` / `spin_orbit: None` for legacy records would pass that relay test. Current production output is correct; this is a future-regression gap.

VERDICT: GO
