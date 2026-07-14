# Codex review — "fit the entire window" fit-range-crop fix — ROUND 2 RECHECK RUN B (2026-07-14)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/full_window_crop_fix_recheck_prompt.txt (recheck of round 1's
status-bar-reset fix, commit c3fe41f)

**Findings**

1. The "status bar" snapshot test helper is incomplete — it captures only `#sb-roi`
   and `#sb-chi`, so it would not detect unintended changes to `#fit-quality` or the
   R-factor pill (`#sb-runs`). Setup also only populates those two fields. A partial
   regression leaving stale `#fit-quality`/R-factor UI could still pass.
2. The "only two files touched" claim is not exact for commit c3fe41f:
   `git diff --name-status c3fe41f^ c3fe41f` also shows `docs/autofit/PROGRESS.md`.
   No backend Python or `/api/fit` changes present.

**Verified**

Implementation looks correct: reset block inside
`if (_fpLast && _fpLast.fitFullWindow)` (templates/index.html:14088); reset values
match `TabManager.activateTab`'s no-fit branch at 3099 (same `innerHTML`, same
tooltip removal, same em-dash literal matching `'—'`). `_updateRFactorUI(null)`
clears text and removes `data-xps-tip`; `_updateROIDisplay(null)` clears `#sb-roi`
(9782). Checked test does require both `#sb-roi` and `#sb-chi` to change. Could not
run the browser test here (no pytest for the available Python).

VERDICT: NO-GO
