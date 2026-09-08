# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 4, RUN B (2026-09-08, reviewed at 102ecd3 / code 59385df)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 64,314.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_r4_review_prompt.txt
Evidence at review time: node 162 pass / 0 fail / 3 known-gap todo; browser endpoint_avg_default (8), find_peaks_full_window, batch_roi: 15 passed together; full pytest result recorded in the round-5 header.
Round 4: NO-GO x2 — the A/B cross-tab sequence is fixed and the memo list closed (both); NEW MAJOR (both, on the prompt's own challenge): persisted tab ids are reused when a closed tab's project is reloaded, so a stale averaging entry matched the reopened tab (9 -> 3); MINOR (both): with no active tab the mirrored entry carries _tabId null and null === null passes the guard.

**Findings**

Reviewed `59385df` and `main...HEAD`; current HEAD `102ecd3` adds only the round-4 prompt. No archived verdict files were read.

1. **MAJOR — Tab-ID reuse still admits stale averaging restores.** The [identity guard](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:2336) fixes the reported A/B sequence, but closing A retains its history, and project loading can reuse A’s saved ID. Reproduction: apply on A at 3 → set averaging to 9 → save project → close A → reload → undo. The reopened tab’s DOM **and record change from 9 to 3**. I reproduced this using production functions in an in-memory harness, with identical peaks before and after undo. Thus it adds background-setting corruption even where pre-existing peak restoration changes nothing. Scope averaging metadata to the live tab instance or a runtime generation token.

2. **MINOR — Restoration is not always inert with no active tab.** After closing the last tab, undo creates a mirrored entry with `_tabId = null`. A subsequent redo passes the guard because `null === null`. Reproduction: close last tab → undo → edit averaging to 9 → redo; the empty panel changes back to 1. Require an existing active tab before writing the DOM, and avoid recording averaging metadata without one.

3. **MINOR — CLOSED: memo whitelist correction.** The [memo](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/docs/superpowers/plans/2026-09-03-endpoint-averaging-default.md:133) now names all six requested methods.

Validation: task logs report 162 JavaScript passes, zero failures, and 15 combined browser passes. My focused tests passed 13/13; the full JavaScript rerun encountered sandbox-related Python temporary-directory failures. The current full pytest log remains incomplete.

VERDICT: NO-GO — Reused project tab IDs let stale undo entries overwrite a reopened tab’s saved endpoint averaging.
