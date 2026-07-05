# Codex re-check ROUND 4 (final) — Phase D unit 2 — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 61,240.
Prompt: docs/autofit/codex/phaseD_unit2_recheck4_prompt.txt

**Per-Item**
1. CLOSED. Round-3 probes now reject, including `n/a/`, `none/`, `<none>`, `n/a #`, and `n/a_`. New decorations I probed also reject by construction: `[[none]]`, `n/a†`, `n/a\u200d`, `\ufefftodo\ufeff`, `citation-needed`, `fixme!!!`, `(x)`, `x_x`, `no.`. Legit citations load as `CONDITIONAL`, including DOI, URL, internal/leading hyphen cases, `Doniach-Šunjić 1970`, and CJK-with-digits.

2. CLOSED. False-rejection audit found only intentionally weak “citations” that collapse exactly to tokens: `T.O.D.O.`, `N.A.`, `No.`, `X.`. Those are not adequate real citations without year/journal/DOI/context. Normal variants such as `T.O.D.O. et al. 2015`, `NA 27, 100 (1990)`, `No. 5, J. Chem.`, `Null et al. 2012`, and `X. X. Zhang 1998` do not collapse to a token and load.

3. CLOSED. Proportionality ruling: the accidental-vs-adversarial line is now in the right place for this contract. The loader requires a string citation, rejects common placeholder accidents by collapsed-token comparison, caps loaded values at `CONDITIONAL`, and provenance relays the citation visibly via `source`. A missed synonym like `nothing here` would be token-set tuning, not a structural hole, because it remains visible garbage in a human-reviewed conditional record.

4. CLOSED for functional scope. Latest commit changes only [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:125), [tests/autofit/test_cited_values.py](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:75), and Codex Phase D docs/prompts/verdict archives. No unrelated runtime surface is touched.

**Findings**
MINOR: The behavior is correct, but I did not find explicit legit-citation pins for DOI/URL/Doniach/CJK in [tests/autofit/test_cited_values.py](/Users/skyefortier/xps-app/tests/autofit/test_cited_values.py:157). Concrete scenario: a future over-aggressive filter could reject those legit forms without this specific test file catching it. This is not release-blocking because direct probes pass and the structural fix is in [autofit/cited_values.py](/Users/skyefortier/xps-app/autofit/cited_values.py:125).

I could not run pytest because this environment lacks `pytest`; I verified by importing and directly executing the loader/provenance paths.

VERDICT: GO
