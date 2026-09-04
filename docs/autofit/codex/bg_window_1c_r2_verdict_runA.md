# Codex adversarial review — bg window inclusive (fix-bg-window-inclusive, unit 1c) — round 2, RUN A (2026-09-03, reviewed at 050aee2 / prompt commit 786bc12)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: n/a.
Prompt: docs/autofit/codex/bg_window_1c_r2_review_prompt.txt
Round 2: GO x2 — evidence generator now reproduces the memo's 12 / 151 / 166 of 166; no findings either run. Note for the record: the round-2 prompt said the C1s parity gate 'was re-run' after the fix commit — it had been collected without RUN_AUTOFIT_GATE=1 and therefore skipped; it was re-run with the flag after the round-2 launch and its result is recorded in PROGRESS/the merge note.

**Findings**

1. No BLOCKER / MAJOR / MINOR findings.

Verified: `scripts/bg_window_pointsets.py` prints the requested final counts exactly; the memo now matches `12/166`, `151/166`, `166/166`, `25/166`, and `154 move / 12 unchanged`. The 1c helper, preview path, and both `/api/fit` request builders share the inside-range inclusive rule and send `end_idx = i1 + 1`. `autofit/reference.py` has only docstring changes under `autofit/**`.

I could not run the full JS suite cleanly in this restricted sandbox because Python parity helpers need a writable temp directory and `lmfit`; the focused unit-1c JS tests passed: `node --test tests/js/bg_window_indices.test.js tests/js/tougaard_twin.test.js` -> 16 pass / 0 fail.

VERDICT: GO
