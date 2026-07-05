# Codex re-check ROUND 2 — Phase D unit 2 — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 30,148.
Prompt: docs/autofit/codex/phaseD_unit2_recheck2_prompt.txt

1. CLOSED. Round-1 probes and new pinned variants reject; legitimate citations load as `CONDITIONAL`.

2. NOT-CLOSED, MINOR. [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:112) does not remove Unicode format controls or apply compatibility normalization. `n\u200b/a`, `n\ufeff/a`, `\ufeffnone\ufeff`, and `n/a\u200b` load as `CONDITIONAL`. Fullwidth/homoglyph forms like `ｎ／ａ` also load, but I rate those adversarial rather than realistic accidental entry. The zero-width/BOM cases are plausible copy/paste accidents, but rare enough that I do not rate this as a blocker.

3. CLOSED. No false-rejection issue found in probes: `Powe95`, DOI, URL, Tougaard citation, `No. 5, J. Chem.`, and `None et al...` all load. `0` remains rejected as intended.

4. CLOSED. Spot-checked Round-1 dispositions: non-string citations reject, CSV duplicate/empty/overflow cases reject, strict `schema_version`/`test_only` checks hold, and pins are present.

Used direct in-memory probes; did not rely on temp files.

VERDICT: GO
