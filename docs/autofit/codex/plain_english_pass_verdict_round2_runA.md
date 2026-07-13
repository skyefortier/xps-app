# Codex review — plain-English pass — ROUND 2 RECHECK RUN A (2026-07-13)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/plain_english_pass_recheck_prompt.txt (recheck of round 1's [] truthiness finding)

NO-GO finding: the fixed guard still misclassifies a real successful payload shape.

`_fpPlainMessage()` now uses `Array.isArray(body.structural_only) && body.structural_only.length` — that fixes the `[]` truthiness bug. But app.py can also emit a successful normal payload with a nonempty `structural_only` array (app.py:361 sets `success: bool(res.success)` and still includes `structural_only`; app.py:380 says structural regions that did fit still ship the structure report). This is pinned by tests/autofit/test_structural_fallback.py, which asserts `success is True`, `structural_only == ["Fe 2p"]`, and emitted peaks. The current UI still returns the false stub for that payload — reproduced directly with a payload matching that shape.

Suggested disposition: make the stub branch match the actual degraded stub shape, not merely nonempty `structural_only`, e.g. require `!body.success` and no emitted peaks in addition to the nonempty array.

Other checks: the empty-array regression test is realistic; the original structural-only stub test still passes; no other bare-array-boolean bug found in the searched areas.

VERDICT: NO-GO
