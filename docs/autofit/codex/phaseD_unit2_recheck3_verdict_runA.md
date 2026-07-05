# Codex re-check ROUND 3 — Phase D unit 2 — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 34,637.
Prompt: docs/autofit/codex/phaseD_unit2_recheck3_prompt.txt

1. Round-2 residual 1: CLOSED. `_validate_row` rejects `"---"`, `"———"`, `"n/a-"`, `"none-"`, `"todo-"`, and `"unknown-"`.

2. Round-2 residual 2: CLOSED. `_validate_row` rejects `"n\u200b/a"`, `"\ufeffnone\ufeff"`, and `"n\u2060/a"`.

3. Legitimate citation false-rejection check: CLOSED. These all load as `CONDITIONAL`: Tougaard citation, `Powe95`, `10.1116/1.1247741`, `Smith & Jones 1990-1995 survey`, and `-30 mV vs SCE study`.

4. New realistic laundering check: NOT-CLOSED.

**New Finding**

MAJOR [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:120): canonicalization only strips a fixed ASCII-ish edge punctuation set. Plausible placeholder forms still load as `CONDITIONAL`: `source_citation="n/a/"`, `"none/"`, `"unknown/"`, `"todo/"`, `"unknown…"`, `"none…"`, and `"<none>"`. These are the same realistic data-entry/copy-paste class as the closed trailing-dash placeholders, not homoglyph/fullwidth adversarial input.

Scope: code scope is otherwise contained. `5ae00bf` changes the loader and its test, plus adds the two archived round-2 verdict docs; no other production file is touched.

VERDICT: NO-GO
