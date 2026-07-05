# Codex re-check ROUND 4 (final) — Phase D unit 2 — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 69,788.
Prompt: docs/autofit/codex/phaseD_unit2_recheck4_prompt.txt

**Per-Item Status**
1. CLOSED. Round 3 probes and new true decoration probes reject under the ASCII-alphanumeric collapse in [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:125). Legit citations loaded as `CONDITIONAL`.

2. CLOSED. I found no realistic full citation that collapses exactly to a placeholder token. Bare `N. A.` or `X` reject, but those are not sufficient real citations; `T.O.D.O. et al.`, `NA 27, 100 (1990)`, `X et al.`, author-like names, DOI/URL/year forms all avoid the token set.

3. CLOSED. Proportionality ruling: the accidental-vs-adversarial line is now in the right place for this contract. The loader has type-checked required citation text, collapsed-token placeholder rejection, and a status ceiling of `CONDITIONAL` or `UNVERIFIED`, never `VERIFIED` in [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:210). Provenance relays the citation string into visible cited records in [autofit/coverage.py](/Users/skyefortier/xps-app/autofit/coverage.py:416). A missed prose placeholder is visible garbage in a conditional record, not invisible fabrication.

4. CLOSED. `7ab6f42` touches only `autofit/cited_values.py`, `tests/autofit/test_cited_values.py`, the Round 3 verdict archives, and the Round 4 prompt archive.

**Findings**
MINOR, not release-blocking: token-set/NLP tuning remains possible. Example: `"sample (see note)"` loads because it collapses to `sampleseenote`, not `sample`. That is outside the fixed structural class of non-alphanumeric decoration and lands on the human-review side of the contract.

I could not run the pytest file directly because this read-only sandbox blocks temp-file creation; I used direct `python3` probes against `_validate_row`, `load_cited_values`, and `structural_provenance`.

VERDICT: GO
