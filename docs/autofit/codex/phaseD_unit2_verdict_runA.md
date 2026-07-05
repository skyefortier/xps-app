# Codex review — Phase D unit 2 (cited_values.py, commits bed007e+24587a1) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 55,019.
Prompt: docs/autofit/codex/phaseD_unit2_loader_prompt.txt

1. **BLOCKER** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:55): citation laundering is still possible. The placeholder set omits required `n-a`, and [line 98](/Users/skyefortier/xps-app/autofit/cited_values.py:98) coerces non-string citations with `str(...)`. Concrete failures I probed: `source_citation="n-a"`, `"N-A"`, `"false"`, `"0"`, JSON `false`, and JSON `0` all load as `CONDITIONAL`. That violates “NOTHING loads without a citation.”

2. **MAJOR** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:210): CSV duplicate headers are silently accepted because `DictReader` collapses duplicate field names before validation. Concrete failure: header `element,level,value_type,value_ev,value_ev,source_citation` with row `Cl,2p3/2,binding_energy_ev,BAD,100.0,SYNTHETIC` drops the first `value_ev` cell and validates `100.0`. Same issue can silently overwrite duplicate `source_citation`. Overflow rows are fixed, but duplicate headers remain malformed CSV that can load.

3. **MINOR** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:197): the JSON schema gate is type-loose. `schema_version: true` passes because `True == 1` in Python. Also [line 204](/Users/skyefortier/xps-app/autofit/cited_values.py:204) coerces `test_only` with `bool(...)`, so `"false"` becomes `True`. This does not mint `VERIFIED`, but it weakens the declared schema contract.

4. **MINOR** [tests/autofit/test_cited_values.py](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:75): tests miss the above discriminators. They cover `N/A`, `NA`, blanks, bool numeric values, CSV overflow, and Infinity, but not `n-a`, non-string `source_citation`, duplicate CSV headers, or boolean `schema_version`.

The fixture is test-only, deliberately non-physical, forces `UNVERIFIED`, and I found no repo load of `example_cited_values.json` outside tests/docs references.

VERDICT: NO-GO
