# Codex review — Tougaard bug-fix (commit 37861fd) — RUN A (2026-07-04)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 117,949.
Prompt: docs/autofit/codex/tougaard_fix_review_prompt.txt

1. **MAJOR** [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4178), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4184), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4202), [fitting.py](/Users/skyefortier/xps-app/fitting.py:997), [fitting.py](/Users/skyefortier/xps-app/fitting.py:1235)  
   Frontend Tougaard still bypasses `_applyEndpointAveraging`, while backend `/api/fit`, `/api/background`, and autofit parity paths apply `_apply_endpoint_averaging` before `tougaard_background`. With the new high-BE anchor this is no longer a small shape-only mismatch: endpoint averaging directly sets the anchor amplitude. Concrete scenario: descending 11-point window, `endpointAvg=2`, high-BE first point is a spike/outlier `10000`, second point and rest are `100`; frontend anchors Tougaard to `10000`, backend anchors to averaged `5050`. The committed JS twin test only calls `tougaardBackground` directly on the same raw array, so it does not catch the shipped caller contract mismatch.

2. **MINOR** [fitting.py](/Users/skyefortier/xps-app/fitting.py:588), [templates/index.html](/Users/skyefortier/xps-app/templates/index.html:4052)  
   The `bg[0] || 1` / `bg[0] != 0 else 1` guard means the documented high-BE anchor is not guaranteed. If the high-BE point is positive but there is no lower-BE signal contributing to `bg[0]` (e.g. `[100, 0, 0, 0]` on a descending grid), the function returns all zeros rather than matching the high-BE edge. That may be acceptable as a degenerate-input fallback, but the comment says the guard “only protects the all-zero-signal case,” which is narrower than the actual behavior. Negative-count windows also produce signed backgrounds without any explicit policy.

VERDICT: NO-GO
