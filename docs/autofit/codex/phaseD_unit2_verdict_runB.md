# Codex review — Phase D unit 2 (cited_values.py, commits bed007e+24587a1) — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 64,028.
Prompt: docs/autofit/codex/phaseD_unit2_loader_prompt.txt

1. **BLOCKER** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:55): placeholder set is wrong for the stated contract. The contract/commit says `n-a` is rejected, but code rejects `n/a`; `_validate_row(... source_citation="n-a")` loads as `CONDITIONAL`.

2. **BLOCKER** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:98): non-citations are coerced into citations. JSON `source_citation: false`, `true`, `0`, or strings `"false"` / `"0"` all load after `str(...).strip()`, producing `"False"`, `"True"`, or `"0"` with `CONDITIONAL` status.

3. **MAJOR** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:210): CSV duplicate headers are silently accepted by `csv.DictReader`, which overwrites earlier cells. Concrete malformed CSV:
   `element,level,value_type,value_ev,source_citation,source_citation`
   `Cl,2p3/2,binding_energy_ev,100.0,,SYNTHETIC`
   loads using the last `source_citation`, silently dropping the first blank column. Same pattern can hide invalid duplicated `value_ev`.

4. **MINOR** [tests/autofit/test_cited_values.py](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:75): citation tests miss the actual bypasses above. They do not cover `n-a`, `"false"`, `"0"`, boolean `false`, or numeric `0`; the current suite would pass with these citation holes present.

Confirmed: the synthetic fixture is `test_only: true`, marked `SYNTHETIC`, and repo search outside `tests/**`/`docs/**` found no runtime load of `example_cited_values.json`.

VERDICT: NO-GO
