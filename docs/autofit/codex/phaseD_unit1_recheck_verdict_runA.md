# Codex re-check — Phase D unit 1 dispositions (fix commit 4254ee1) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 54,201.
Prompt: docs/autofit/codex/phaseD_unit1_recheck_prompt.txt

FINDING 1: CLOSED. [coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:100) now references the Cl 2p adjudication without emitting `0.55` or `0.5` in the returned caveat. `level_structure("U", "4f")["statistical_area_ratio"]["caveat"]` has no decimal/eV empirical value. Literal digits remain only as bookkeeping/reference text: `2j+1`, `Cl 2p`, `#7`. A module grep found only one decimal/eV prose hit, [coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:180), inside a private docstring explaining theoretical ratio examples, not emitted data.

FINDING 2: CLOSED. The hardened guard in [test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:186) tracks value-bearing ancestry via `_walk`, restricts numeric `value` to `.statistical_area_ratio.`, and scans strings with the stated regex. Direct probes show it catches populated `binding_energy_ev`, wrapped `spin_orbit_splitting_ev.value = 1.6`, `"shifts by 1.6 eV"`, and `"284.8"`. It does not false-positive on `2j+1`, `1:2`, `3/2`, `(n+l, n)`, or legal statistical-ratio `value`.

FINDING 3: CLOSED. [test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:254) covers first-call and cache-hit mutation paths plus `level_structure`. Simulated removals confirm discrimination: without the first-call deepcopy, the next read returns `999.0`; without the cache-hit deepcopy, the next read returns `888.0`.

FINDING 4: CLOSED. [test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:271) pins the algorithmic outputs currently computed by the module: Cu `3d9 4s2`, Pd `4d8 5s2`, La `4f1`, Ce `4f2`, all `multiplet_prone=True`. These would break if someone silently special-cased real configurations.

New findings: none.

I could not run real `pytest` because `pytest` is unavailable; I ran direct import probes with a minimal stub. The added coverage tests passed under those probes. Commit `4254ee1` changes only `autofit/coverage.py`, `tests/autofit/test_coverage_structure.py`, and the Phase D review prompt/verdict docs.

VERDICT: GO
