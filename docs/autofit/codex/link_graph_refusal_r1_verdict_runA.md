Found one MAJOR gap and two MINOR gaps in the promised refusal coverage. These are incomplete fixes, not newly introduced numerical regressions.

1. **MAJOR — Python twins still silently fit an orphan as a free peak.**  
   [reference.py:149](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/autofit/reference.py:149) omits `constrain_to` when the parent is absent. Adding `frontend_shape` does not prevent that. I reproduced `linked: 2` with only peak 3 present: the twin removed the constraint and `run_fit` returned `success: true`. [The refit path](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/autofit/parity.py:237) uses this builder without the page’s preflight, so it can record a fit of a different model. Validate the graph before Python request construction.  
   **Non-physical inputs required: no.** Removing a chain’s root can produce this saved model.

2. **MINOR — A missing parent still gets admitted by `/api/fit/start`.**  
   [fitting.py:1485](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/fitting.py:1485) skips absent parents. With identical orphan requests, I reproduced `/api/fit → 400` and `/api/fit/start → 202`, with job creation invoked. The fit eventually refuses it, but the promised immediate refusal is incomplete. Reject missing parents in the shared validator.  
   **Non-physical inputs required: no.**

3. **MINOR — Duplicate IDs produce a 500 through `/api/analyze`.**  
   Uniqueness remains confined to fit-route preparation; [the shared validator](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/fitting.py:1472) does not check it. The `least_squares` analyze path reaches lmfit, raises `NameError` for duplicate parameter names, and returns “Internal analyze error.” Move uniqueness validation into the shared validator too.  
   **Non-physical inputs required: no.** Ordinary peak values suffice; the defect is duplicate bookkeeping IDs.

The blanket shape rule is broader than “cannot fit as drawn.” Under the main validator, a **GL child of a Voigt parent**, a Gaussian child of a Lorentzian parent, and a GL child of an asymmetric-GL parent all fitted successfully with zero child-curve discrepancy in my probes. This branch refuses them. That follows your explicit prohibition on cross-shape links, so I have not counted it as an unauthorized change.

The other checks were reassuring: the census reproduced exactly; pinned Python/page builder parity passed; a linked GL fit’s **complete result**, including seed and record, was identical with and without `frontend_shape`. The page guards precede Run Fit’s undo/spinner/request and Batch Fit’s target mutations. Auto-Fit constructs unlinked peaks.

Validation: 133 selected JS checks and three Python tests passed. Browser fixtures could not run under the read-only restriction. The added tests exercise real behavior, but the “every fit path” source assertions and cross-shape-only route test do not prove the missing cases above. No files changed.

**VERDICT: NO-GO.**
