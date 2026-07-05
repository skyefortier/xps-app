# Codex re-check ROUND 3 — Phase D unit 2 — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 35,083.
Prompt: docs/autofit/codex/phaseD_unit2_recheck3_prompt.txt

(a) CLOSED. Round-2 residual probes now reject: `---`, `———`, `n/a-`, `none-`, `todo-`, `unknown-`, `n\u200b/a`, `\ufeffnone\ufeff`, `n\u2060/a`, and `no\u200bne`.

(b) CLOSED. Legitimate citations still load as `CONDITIONAL`, including:
`Tougaard, Surf. Interface Anal. 11, 453 (1988)`, `Powe95`, `10.1116/1.1247741`, `Smith & Jones 1990-1995 survey`, and `-30 mV vs SCE study`. Internal hyphen survives; leading hyphen only affects the placeholder check.

(c) NOT-CLOSED.

MAJOR [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:120): placeholder canonicalization still strips only a hand-picked edge punctuation set. Common edge markers outside that set load as citations: `n/a*`, `none*`, `todo*`, `unknown*`, `n/a #`, `none #`, `n/a_`. These are realistic spreadsheet/copy-paste footnote/comment markers, same class as the trailing-dash placeholders fixed in this commit.

(d) CLOSED for functional scope. `5ae00bf` changes `autofit/cited_values.py`, `tests/autofit/test_cited_values.py`, and the archived round-2 verdict docs; no other runtime surface is touched.

VERDICT: NO-GO
