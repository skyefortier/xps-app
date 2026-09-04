# Codex adversarial review — bg window inclusive (fix-bg-window-inclusive, unit 1c) — round 2, RUN B (2026-09-03, reviewed at 050aee2 / prompt commit 786bc12)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: n/a.
Prompt: docs/autofit/codex/bg_window_1c_r2_review_prompt.txt
Round 2: GO x2 — evidence generator now reproduces the memo's 12 / 151 / 166 of 166; no findings either run. Note for the record: the round-2 prompt said the C1s parity gate 'was re-run' after the fix commit — it had been collected without RUN_AUTOFIT_GATE=1 and therefore skipped; it was re-run with the flag after the round-2 launch and its result is recorded in PROGRESS/the merge note.

**Findings**

1. No BLOCKER / MAJOR / MINOR findings.

Verified the dispositions against the branch state. Note: local `HEAD` is `786bc12`, a docs-only round-2 prompt commit on top of requested `050aee2`; the reviewed code/fix commit is unchanged.

`python3 scripts/bg_window_pointsets.py` confirms the exact final lines:
`today: 12/166`, `nearest+1: 151/166`, `1c inside-range: 166/166`, and `bg window narrower than ROI: 25/166`.

Focused JS checks passed: `node --test tests/js/bg_window_indices.test.js tests/js/tougaard_twin.test.js` → 16/16 pass. Full `node --test tests/js/*.test.js` was not usable in this read-only sandbox because backend parity subprocesses fail importing Python/lmfit without a writable temp dir.

I found no remaining live frontend/static path that maps bg bounds independently of `_bgWindowIndices`, other than the deliberately retained `autofit/reference.py::bg_indices()` parity-fixture path. The memo and docstring now match the script and stated caveats.

VERDICT: GO
