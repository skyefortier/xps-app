# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 4, RUN A (2026-09-08, reviewed at 102ecd3 / code 59385df)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 72,681.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_r4_review_prompt.txt
Evidence at review time: node 162 pass / 0 fail / 3 known-gap todo; browser endpoint_avg_default (8), find_peaks_full_window, batch_roi: 15 passed together; full pytest result recorded in the round-5 header.
Round 4: NO-GO x2 — the A/B cross-tab sequence is fixed and the memo list closed (both); NEW MAJOR (both, on the prompt's own challenge): persisted tab ids are reused when a closed tab's project is reloaded, so a stale averaging entry matched the reopened tab (9 -> 3); MINOR (both): with no active tab the mirrored entry carries _tabId null and null === null passes the guard.

**Findings**

Reviewed `59385df`; actual HEAD `102ecd3` adds only the round-4 prompt. Archived verdicts were not read.

1. **MAJOR — Reused project IDs defeat the averaging guard.** [The guard]( /Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:2336) compares persisted IDs, which project loading reuses after a tab closes. Reproduction: save A at averaging **9**, change it to **3**, apply Find Peaks, close A, reload the saved project, then undo. The stale entry changes the reopened tab’s DOM and record **9 → 3**. I reproduced this using production undo, close, and project-load functions with rendering stubbed. The saved peaks can equal the snapshot’s peaks, so this introduces a background change even when the pre-existing peak restoration changes nothing. Scope averaging snapshots to the runtime tab instance, or invalidate their averaging metadata when that instance closes. The original A/B sequence is fixed, but this disposition remains open.

2. **MINOR — No-active-tab restoration is not always inert.** Closing the last tab and undoing correctly skips restoration, but creates a redo entry with `_tabId: null`. Redo then passes the `null === null` check and writes the endpoint field. Reproduced: edit the empty workspace’s field to **9**, redo, and it becomes **1**. Require an existing active tab before writing the DOM.

3. **MINOR — Memo whitelist disposition closed.** The memo now lists all six requested methods.

Validation: all **13 focused Node tests passed**. The implementation log records **162 Node passes, zero failures, and 15 browser passes**. My full Node run produced **150 passes, 12 failures caused by unavailable writable temporary directories, and 3 TODOs**; I could not independently rerun browser tests here.

VERDICT: NO-GO — A stale undo entry can overwrite a reopened project tab’s saved averaging because persisted tab IDs do not distinguish runtime tab instances.
