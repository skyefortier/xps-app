# Codex re-check — Tougaard fix dispositions (fix commit 2731edc) — RUN B (2026-07-04 late)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/tougaard_fix_recheck_prompt.txt

**Finding 1: CLOSED**

`computeBackgroundCore` now averages Tougaard input in both frontend branches:

- Fallback/full-range path uses `avgIn` before Tougaard: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184)
- Main sliced path uses `_applyEndpointAveraging(inSub, nAvg)`: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4214)
- Backend parity remains: `/api/fit` and `/api/background` both call `tougaard_background(..., _apply_endpoint_averaging(...))`: [fitting.py](/Users/skyefortier/xps-app/fitting.py:1002), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1240)

UI gates are consistent:

- `shirley-iter` remains disabled for Tougaard because `needsIter` excludes it.
- endpoint averaging is enabled for Tougaard via `needsEpAvg = needsIter || type === 'tougaard'`: [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:3594), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:12197)

The new JS pin discriminates. Against `37861fd`, the same outlier case produced raw anchor `10000` vs averaged `3400` for both branches. Against `2731edc`, both branches were bit-equal to averaged expected output. `node --test tests/js/tougaard_twin.test.js` passed.

No other shipped Flask frontend caller is missed. Repo grep does find tracked stale copies (`xps-fitting-tool.html`, `templates/index.html.pre-audit`, tmp copy), but `app.py` serves `templates/index.html`, and those copies are documented out-of-scope stale artifacts.

**Finding 2: CLOSED**

Comments now state the real guard behavior and signed negative-count policy at both sites: [fitting.py](/Users/skyefortier/xps-app/fitting.py:587), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4053). The new Python pin matches the documented `[100,0,0,0]` behavior: [tests/test_tougaard_background.py](/Users/skyefortier/xps-app/tests/test_tougaard_background.py:131).

I could not run pytest because the read-only sandbox has no usable temp directory, but I executed the extracted `tougaard_background` body directly and confirmed `[100,0,0,0] -> [0,0,0,0]`. I also checked the mixed-sign cancellation edge: it returns a signed unanchored correlation, consistent with the “negative counts pass through signed; no clamping” policy.

**Scope / Numerics**

`git diff 37861fd 2731edc -- fitting.py` changes only the Tougaard guard comment; no numeric code changed. The `2731edc` file list matches the expected scope: docs, `templates/index.html`, `fitting.py`, and the two Tougaard test files.

New findings: none.

VERDICT: GO
