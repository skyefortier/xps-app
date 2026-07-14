# Codex review — Find Peaks method dropdown tooltips — RUN B (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/method_tooltips_review_prompt.txt (commit 17b0518)

**Findings**

None.

**Verified**

The four `FP_STRINGS.methods` hints (templates/index.html:13016) are substantive:
each says what the method does and when to use it. Option construction
(13402) uses `s.hint || s.label || m.label || m.id`. Cross-checked
`_ANALYZE_METHODS` (app.py:167), `/api/analyze/meta` filtering (app.py:874), and
`available_methods()` (autofit/methods/__init__.py:50) — backend returns exactly the
four real IDs covered by `FP_STRINGS.methods`, each with a non-empty `hint`.
Display-only: backend labels unchanged in ic_model_comparison.py, bayesian_exchange_mc.py,
sparse_map.py, least_squares.py; `/api/analyze/meta` response shape unchanged. Static
trace of tests/test_browser_find_peaks_method_tooltips.py:123 confirms it checks the
old vague field-tooltip sentence, all four option titles, raw backend jargon
substrings, title length, title-vs-visible-text inequality, and per-method
distinguishing keywords. Could not run the browser test here (no pytest installed
for the available Python).

VERDICT: GO
