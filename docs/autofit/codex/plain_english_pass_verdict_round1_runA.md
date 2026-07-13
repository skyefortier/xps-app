# Codex review — plain-English pass — ROUND 1 RUN A (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/plain_english_pass_review_prompt.txt

**Finding**

templates/index.html:13269 treats `body.structural_only` as a truthy flag. The API always includes `structural_only` on normal analyze payloads as a list, even when empty (app.py:361, app.py:367). In JavaScript, `[]` is truthy, so a normal successful Find Peaks result with `structural_only: []` returns the structural-only failure paragraph ("No fittable peaks were found…") instead of the clean/conditional/unphysical-width message. This is a meaning regression in the new display layer. The guard needs to check non-empty, e.g. `Array.isArray(body.structural_only) && body.structural_only.length`.

**Other Checks**

Remaining `grammar` hits in templates/index.html and autofit/coverage_index.py are comments/docstrings/internal fields; the displayed tier labels and note strings no longer say "grammar". `_fpPlainMessage()` otherwise covers the backend message branches correctly. `_fpBoundaryHitLabel()`/`_fpWidthFlagLabel()` match the backend formats and keep failure classes distinct. The raw backend `body.message` construction was not touched. Old method labels are gone from active code.

VERDICT: NO-GO
