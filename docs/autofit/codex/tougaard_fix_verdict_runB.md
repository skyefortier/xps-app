# Codex review — Tougaard bug-fix (commit 37861fd) — RUN B (2026-07-04)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 83,368.
Prompt: docs/autofit/codex/tougaard_fix_review_prompt.txt

1. **MAJOR** [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4202), [fitting.py](/Users/skyefortier/xps-app/fitting.py:997), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1235) — Tougaard endpoint averaging is inconsistent between shipped frontend callers and backend callers. The UI disables `endpointAvg` for Tougaard, but stale values are still sent to `/api/background` and `/api/fit`; backend applies `_apply_endpoint_averaging(...)` before `tougaard_background`, while frontend preview/stack calls `tougaardBackground(...)` on raw intensity. Concrete failure: set endpoint avg to `10`, switch to Tougaard, with high-BE endpoint `500` and next 9 points `100`; frontend anchors Tougaard to `500`, backend anchors to averaged `140`. That breaks the claimed frontend/backend twin contract exactly at the new high-BE anchor, and current tests only compare direct function calls with unaveraged data.

VERDICT: NO-GO
