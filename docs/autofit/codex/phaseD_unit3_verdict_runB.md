# Codex review — Phase D unit 3 (structural fallback, commit 2ef5b2c + swept-in structural_provenance) — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 157,220.
Prompt: docs/autofit/codex/phaseD_unit3_fallback_prompt.txt

1. MINOR [tests/autofit/test_structural_fallback.py:89](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:89): No regression pin that phase ambiguity runs before structural fallback. Current code is correct: direct probe with `Fe 2p` in two phases raises `PhaseAmbiguityError`. Failure scenario: a future refactor moves fallback before [autofit/grammar.py:328](/Users/skyefortier/xps-app/autofit/grammar.py:328), silently returning a structural entry instead of forcing phase disambiguation.

2. MINOR [tests/autofit/test_structural_fallback.py:188](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:188): API tests cover structure-only and unparseable paths, but do not pin mixed deep+structural or the `least_squares` grammar-`None` path. Current code is statically correct at [app.py:703](/Users/skyefortier/xps-app/app.py:703) and [app.py:761](/Users/skyefortier/xps-app/app.py:761). Failure scenario: omitting `structural_only` from a mixed method payload, or accidentally resolving fallback for `least_squares`, would not be caught by the current API tests.

Direct probes passed for structural provenance statuses, no empirical prose matches in emitted sources/notes, cited-value filtering, candidate emptiness with cited values/oxidation/joint structural requests, deep+structural composition, slug collision guard, default fallback-off behavior, and the meV string guard. I could not run pytest or Flask API probes because this read-only sandbox lacks `pytest` and `flask`.

VERDICT: GO
