# Codex re-check ROUND 2 — Phase D unit 2 — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 88,013.
Prompt: docs/autofit/codex/phaseD_unit2_recheck2_prompt.txt

1. **CLOSED**: round-1 residual probes now reject, including `n-a`, `false`, `0`, `n–a`, `None.`, `n - a`, `n\t-a`, `...`, `(none)`. Legitimate citations load: Tougaard citation, `Powe95`, DOI, URL, and `No. 5, J. Chem.`.

2. **NOT-CLOSED**: remaining placeholder laundering exists.

**MAJOR** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:112): dash-only placeholders beyond the exact `"-"` / `"--"` set still load as `CONDITIONAL`. Concrete probe: `source_citation="---"` and `"———"` load. Also `n/a-`, `none-`, `todo-`, `unknown-` load because dash is normalized but not stripped as edge punctuation. These are realistic spreadsheet/data-entry placeholders, not hostile input.

**MINOR** [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:112): invisible Unicode format chars are not canonicalized away. Concrete probes: `n\u200b/a`, `no\u200bne`, `\ufeffnone\ufeff`, `n\u2060/a` load as `CONDITIONAL`. This is plausible copy/paste damage, but less common than dash placeholders. I did not count fullwidth `ｎ／ａ` or Cyrillic homoglyphs as release-blocking; those are closer to adversarial input.

3. **CLOSED**: no false rejections found in normal citation probes. `Powe95`, DOI, URL, Tougaard reference, `No. 5, J. Chem.`, and `Nonequilibrium Surf. Sci...` all load. Internal punctuation is not stripped, only edge punctuation.

4. **CLOSED**: run-A dispositions 1-4 still hold on spot-check. Non-string citations reject, CSV duplicate/empty/overflow headers reject, strict JSON `schema_version` and boolean-only `test_only` reject bad types, and regression pins are present.

I did not run pytest because this sandbox is read-only and temp-file creation is denied; I used direct in-memory probes against `_validate_row`, `_rows_from_json`, and `_rows_from_csv`.

VERDICT: NO-GO
