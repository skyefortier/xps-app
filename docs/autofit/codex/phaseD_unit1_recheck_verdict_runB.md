# Codex re-check — Phase D unit 1 dispositions (fix commit 4254ee1) — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 77,050.
Prompt: docs/autofit/codex/phaseD_unit1_recheck_prompt.txt

**Disposition**

1. **CLOSED** - [autofit/coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:100) rewords `_RATIO_CAVEAT` by reference and removes the emitted empirical `0.55` / theoretical `0.5` prose. Direct probe of `level_structure("U", "4f")["statistical_area_ratio"]["caveat"]` found no decimal or eV-suffixed matches. Reintroducing the old caveat would match `0.55` and `0.5` under the hardened string regex. Note: the caveat is not literally digit-free (`2j+1`, `Cl 2p`, `#7`), but those are bookkeeping/reference labels, not empirical numeric values.

2. **NOT-CLOSED** - the requested probes now pass: scalar `*_ev`, wrapped `{"spin_orbit_splitting_ev": {"value": 1.6}}`, `"shifts by 1.6 eV"`, and `"284.8"` are all caught; legal strings `2j+1`, `1:2`, `3/2`, `(n+l, n)` do not false-positive. However, the guard still allows any numeric key named `value` anywhere under `.statistical_area_ratio.` at [tests/autofit/test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:235). Direct probe: adding `statistical_area_ratio["empirical_bound"] = {"value": 0.55, "source": "adjudication #7"}` produced no guard errors. That can launder the original empirical ratio as structured data.

3. **CLOSED** - [tests/autofit/test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:254) covers first-call and cache-hit mutation paths plus `level_structure`. Simulated removal of the first-call deepcopy would expose `999.0`; simulated removal of the cache-hit deepcopy would expose `888.0`, so either removed deepcopy would fail the test.

4. **CLOSED** - [tests/autofit/test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:271) pins the module’s computed outputs: Cu `3d9 4s2`, Pd `4d8 5s2`, La `4f1`, Ce `4f2`, all `multiplet_prone=True`. Real-configuration special-casing would break these assertions.

**New Finding**

- **MAJOR** - [tests/autofit/test_coverage_structure.py](/Users/skyefortier/xps-app/tests/autofit/test_coverage_structure.py:235): contextual `value` allowance is too broad. Concrete failure scenario: a future patch adds `{"statistical_area_ratio": {"value": 0.5, "empirical_bound": {"value": 0.55}}}`; the anti-confabulation guard passes because the path is inside `statistical_area_ratio`, re-opening structured empirical ratio laundering.

Pytest is unavailable here (`ModuleNotFoundError: No module named 'pytest'`), so I used direct import probes with a minimal pytest stub. Scope check: `4254ee1` touches only `autofit/coverage.py`, `tests/autofit/test_coverage_structure.py`, and `docs/autofit/codex/*`; the `coverage.py` diff is caveat text only.

VERDICT: NO-GO
