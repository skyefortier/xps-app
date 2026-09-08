# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 5, RUN B (2026-09-08, reviewed at 395ada8 / code fb17b8b)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 83,020.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_r5_review_prompt.txt
Evidence at review time: node 162 pass / 0 fail / 3 known-gap todo; browser endpoint_avg_default (10), find_peaks_full_window, batch_roi, overlay_zip_roundtrip: 19 passed together; full pytest on the branch worktree 773 passed, 7 skipped (6 env-gated + local-only {7,8}* datasets absent from the worktree).
Round 5: GO x2 — reopened-project identity and null-active-tab closed (both); same-object challenge (v1 fromJSON into the active tab) ruled coherent undo, not a defect (both); WeakMap audit clear (both). Unit passes after 5 rounds.

**Findings**

1. **MAJOR — CLOSED: reopened project tabs.** The [runtime-token guard](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:2352) rejects a new tab object even when its persisted ID matches. Project loading constructs new objects, so stale averaging entries cannot overwrite the reopened tab’s saved value.

2. **MINOR — CLOSED: no active tab.** Snapshots omit averaging metadata without a live tab, and restoration rejects null lookups. Both `activeId === null` and an unresolved active ID passed the extracted-function checks.

3. **MAJOR challenge — no additional defect found.** `setSpectrum` creates a new tab. V1 `fromJSON` retains the same spectrum and replaces its fit settings. Within the existing surviving undo history, restoring historical peaks together with their averaging is coherent. The production-function check confirmed that undo restored the earlier peaks/3 and redo restored the loaded peaks/9. Resetting history on fit import would be a separate undo-policy change.

4. **MINOR — no new WeakMap issue found.** Entries retain integer tokens rather than tab references; the WeakMap does not keep closed tabs alive. Stack objects receive distinct tokens without affecting source-spectrum settings. Array metadata is omitted from JSON serialization.

Validation: 13 focused JavaScript tests and the extracted production-function checks passed. The round-5 task log records **162 pass / 0 fail** and **19 browser tests passed**. My full local JavaScript run encountered 12 backend-parity failures caused by the sandbox’s unavailable writable temporary directory; browser/full-pytest results were not independently rerun.

VERDICT: GO
