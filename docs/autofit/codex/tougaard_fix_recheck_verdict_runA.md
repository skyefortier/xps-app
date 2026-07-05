# Codex re-check — Tougaard fix dispositions (fix commit 2731edc) — RUN A (2026-07-04 late)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/tougaard_fix_recheck_prompt.txt

**Finding 1: CLOSED**

Evidence:
- Fallback full-range path now computes `avgIn = _applyEndpointAveraging(intensity, nAvg)` and passes it to Tougaard at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184) and [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4193).
- Main sliced path now passes `_applyEndpointAveraging(inSub, nAvg)` to Tougaard at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4214).
- The pin discriminates: on the outlier-edge scenario, raw Tougaard anchors at `10000`; averaged expected/main/fallback all anchor at `3400`. So the old raw-intensity call would fail it.
- UI gates are consistent: `shirley-iter` remains disabled for Tougaard because `needsIter` excludes it, while `bg-endpoint-avg` is enabled because `needsEpAvg = needsIter || type === 'tougaard'` at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3594) and [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:12197).
- Active shipped frontend callers funnel through `computeBackgroundCore`; `computeBackground` is only a DOM wrapper at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4236). Flask serves `templates/index.html` at [app.py](/Users/skyefortier/xps-app/app.py:214).

Tracked stale HTML copies still contain old Tougaard code, but project docs and `CLAUDE.md` identify `templates/index.html` as the active frontend; I do not count those stale copies as an active shipped caller for this disposition.

**Finding 2: CLOSED**

Evidence:
- Backend comment now states the real `bg[0] == 0` guard behavior and the signed negative-count policy at [fitting.py](/Users/skyefortier/xps-app/fitting.py:587).
- JS comment mirrors that at [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4053).
- The pin covers the concrete `[100, 0, 0, 0]` case at [tests/test_tougaard_background.py](/Users/skyefortier/xps-app/tests/test_tougaard_background.py:132).
- For adversarial mixed-sign exact cancellation, the guard does not edge-match or clamp; it returns a signed, unanchored shape scaled through the `denom = 1` fallback. The “all zeros in practice” wording is accurate for the documented nonnegative no-loss case, not a universal mixed-sign claim.

**Other Checks**

No new findings.

Scope matches the expected commit footprint: only docs/prompt/verdict archives, `fitting.py`, `templates/index.html`, and the two Tougaard tests changed. `fitting.py` Tougaard executable numerics are unchanged from `37861fd`; the diff is comment-only in that function.

Verification run:
- `node --test tests/js/tougaard_twin.test.js` passed.
- I did not run pytest; importing `fitting.py` directly is blocked in this sandbox by missing `lmfit`.

VERDICT: GO
