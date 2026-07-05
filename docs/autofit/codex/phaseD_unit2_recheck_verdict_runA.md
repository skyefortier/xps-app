# Codex re-check — Phase D unit 2 dispositions (fix commits 9062477+a9ba919) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 41,637.
Prompt: docs/autofit/codex/phaseD_unit2_recheck_prompt.txt

NOTE: the paired RUN B produced no verdict — killed by the 15-min gtimeout
watchdog mid-probe (last output: rerunning sandbox-blocked zsh here-doc probes
via python -c). Logged per rails (kill+log+proceed); round 2 re-runs x2.

**Disposition Re-Check**

1. **FINDING 1: CLOSED, with a new residual**
   Evidence: [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:103) rejects non-string `source_citation` before coercion; [line 107](/Users/skyefortier/xps-app/autofit/cited_values.py:107) strips only after type check; [lines 57-60](/Users/skyefortier/xps-app/autofit/cited_values.py:57) include `n-a`, `false`, `true`, `0`, `null`, `nil`.
   Direct probes rejected `False`, `True`, `0`, `1`, `100.0`, `[]`, `{}`, `n-a`, `N-A`, `  n-a  `, `false`, `true`, `0`, `null`, `nil`.

2. **FINDING 2: CLOSED**
   Evidence: CSV now uses `csv.reader` at [autofit/cited_values.py:227](/Users/skyefortier/xps-app/autofit/cited_values.py:227), rejects duplicate headers at [line 235](/Users/skyefortier/xps-app/autofit/cited_values.py:235), empty headers at [line 240](/Users/skyefortier/xps-app/autofit/cited_values.py:240), and overflow rows at [line 243](/Users/skyefortier/xps-app/autofit/cited_values.py:243).
   Direct probes rejected duplicate `source_citation`, duplicate `value_ev`, empty header column, overflow row, `source_citation ` vs `source_citation` via unknown field, and short rows via required-field rejection. Empty file and header-only CSV load as empty tables, which matches the “empty table loads empty” contract.

3. **FINDING 3: CLOSED**
   Evidence: [autofit/cited_values.py:209](/Users/skyefortier/xps-app/autofit/cited_values.py:209) now requires strict `int` schema version and rejects `bool`; [line 218](/Users/skyefortier/xps-app/autofit/cited_values.py:218) requires `test_only` to be `bool`.
   Direct probes rejected `schema_version: true`, `schema_version: 1.0`, `test_only: "false"`, and `test_only: 1`; accepted `schema_version: 1` and real `test_only: true`.

4. **FINDING 4: CLOSED**
   Pins are present in [tests/autofit/test_cited_values.py](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:75), [line 84](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:84), [line 200](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:200), [line 218](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:218), and [line 229](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:229). They discriminate the reverted bugs; for non-string citation specifically, `1`, `100.0`, `[]`, and `{}` still fail only because of the type check.

**New Finding**

**MAJOR** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:107): placeholder detection only does `strip().lower()` plus exact set membership. Obvious placeholder variants still load as `CONDITIONAL`: `source_citation="n–a"`, `"None."`, `"n - a"`, and `"n\t-a"`. I do not count `"12345"` as a finding; that crosses into citation-quality validation. The dash/punctuation/internal-whitespace cases are still placeholder laundering, not NLP validation.

I did not run pytest because the sandbox denied temp-file creation; I used direct in-memory probes against `_validate_row`, `_rows_from_json`, and `_rows_from_csv`.

VERDICT: NO-GO
