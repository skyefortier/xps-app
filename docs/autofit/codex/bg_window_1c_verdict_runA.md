# Codex adversarial review — bg window inclusive (fix-bg-window-inclusive, unit 1c) — round 1, RUN A (2026-09-03, reviewed at bad191c)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: n/a.
Prompt: docs/autofit/codex/bg_window_1c_review_prompt.txt
Evidence at review time: node --test tests/js/*.test.js 155 pass / 0 fail / 3 known-gap todo; pytest tests/ on the branch worktree 758 passed, 7 skipped (6 known env-gated + 1 worktree-only skip: local-only {7,8}* C1s datasets absent from the worktree).
Round 1: NO-GO x2 — same MAJOR both runs: committed scripts/bg_window_pointsets.py still models 'after 1c' as nearest+1, so the memo's 166/166 inside-range claim was not reproducible from the shipped generator.

**Findings**

1. **MAJOR** [scripts/bg_window_pointsets.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/scripts/bg_window_pointsets.py:1) contradicts the Round-5 memo’s reproducibility claim. The memo says the committed script supports `1c: inside-range ... 166 / 166`, but the script still defines “Backend after 1c” as nearest-index plus `i1 + 1` and computes `after = set(range(i0, i1 + 1))` from nearest indices. Running it here prints `TABS: 166 js==after: 151`, not 166. The runtime code uses the intended helper, but the committed evidence artifact refutes the memo table at [docs/...sealed-fit-record.md](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:211).

2. **MINOR** [scripts/bg_window_worked_example.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/scripts/bg_window_worked_example.py:52) does not mirror the actual frontend upload precision. `uploadToBackend()` sends BE to 4 decimals and intensity to 2 decimals at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/templates/index.html:6004), while the worked-example script rounds BE/counts to 3/1 decimals. That makes the quoted magnitudes less exact than claimed. I could not rerun the fit magnitudes because this sandbox lacks `lmfit`.

3. **MINOR** `_bgWindowIndices()` assumes the ROI array is monotonic/contiguous even though its prose says “no point outside it is ever used.” Fresh imports are sorted descending in `createTab()` at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/templates/index.html:2994), but project restore preserves saved `rawBE` order at [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/templates/index.html:9236). On a non-monotonic restored project, first/last inclusive indices can wrap outside-of-window points into the slice. Preview and `/api/fit` still agree, so this is mainly a contract/prose edge.

I found no remaining live frontend path mapping `bg-start`/`bg-end` to `/api/fit` indices differently: `runFit` and `runAutoFitC1sGraphite` both call `_bgWindowIndices()` and send `end_idx = i1 + 1`. Stack Path B, Bkgrd-Sub, local-LM fallback, batch propagation, save/export recomputation all route through `computeBackgroundCore()`. The deliberate `autofit/reference.py::bg_indices()` divergence is exactly where the memo says it is.

The helper’s normal finite, ascending/descending, blank/NaN, outside-data, one-point, and two-point arithmetic is sound, and the backend `<2` guard agrees with the frontend request arithmetic for `/api/fit`. I also ran the two relevant node tests successfully: `tests/js/bg_window_indices.test.js` and `tests/js/tougaard_twin.test.js`.

VERDICT: NO-GO — the committed point-set evidence generator still implements and reports the rejected nearest-plus-one rule, directly contradicting the required memo justification.
