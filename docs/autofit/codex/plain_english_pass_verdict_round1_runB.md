# Codex review — plain-English pass — ROUND 1 RUN B (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/plain_english_pass_review_prompt.txt

**Finding**

NO-GO: `_fpPlainMessage()` treats any `body.structural_only` value as the structural-only stub path. In JavaScript, `[]` is truthy, and the normal API payload always includes `structural_only: []` for non-structural results (app.py:367). So templates/index.html:13269 causes ordinary successful Find Peaks results to show "No fittable peaks were found in this window for  ..." instead of the clean/conditional/low-confidence technical details. This also silently drops conditional warnings, unphysical-width warnings, filtered-dominant-alternative notes, and truncation notes for normal payloads. The guard needs to check `Array.isArray(body.structural_only) && body.structural_only.length`.

**Other checks**: remaining `grammar` hits are comments/docstrings/internal or `roi.basis` (not rendered). The diff does not touch app.py/autofit/engine.py/ic_model_comparison.py, so `body.message` construction is unchanged. Old method labels not found in active code.

VERDICT: NO-GO
