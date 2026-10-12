One MAJOR refusal gap remains.

1. **MAJOR — The Python twin still fits an orphan when parent IDs differ by type.**  
   Reproducer: a GL root has `id: 1`; its GL child has `linked: "1"`. The page correctly refuses this: its exact lookup finds no string-ID parent. But [the Python builder](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/autofit/reference.py:150) stringifies the link and both IDs, silently connecting the child to numeric peak `1`.

   I reproduced **`success: true` through `autofit.parity.refit_record`**, which returns a record for this changed graph. Sending the link preserves evidence only when string conversion cannot resolve it to another peak. Validate the original graph using the page’s lookup semantics before serialization. Add this case to the twin’s orphan test; builder-output parity alone cannot catch the missing preflight.

   **Non-physical inputs required: no.** Ordinary positive spectra and peak parameters suffice; it requires mixed-type graph metadata accepted by the saved-file loader.

2. **MINOR — `/api/analyze/start` still admits invalid graphs before refusing them asynchronously.**  
   [Analyze request preparation](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/app.py:412) does not call the graph validator. With session loading and job side effects mocked, orphan, duplicate-ID and cross-shape requests each returned **202**; their synchronous equivalents returned **400**. No incorrect fit is established here, but immediate refusal does not cover this route. The test named [“every route refuses at once”](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/tests/test_link_graph_refusal.py:84) omits it.

   **Non-physical inputs required: no.** Invalid graph metadata suffices.

The other round 1 repairs held in the checks performed. Falsy links pass, family switches reach grandchildren, and both fit routes immediately refuse the sampled invalid graphs. Run Fit and Batch Fit guards precede their undo/spinner/target mutations. The census reproduced **121 tabs, 530 peaks, 67 links, zero refusals**.

For a valid linked GL pair, the **complete fit result** was identical with and without `frontend_shape`. The shape and twin parity tests passed. The blanket same-lineshape rule remains stricter than mathematical necessity—some cross-shape links fit as drawn—but that restriction is now explicitly documented as the owner’s policy.

Validation: **138 selected JS tests and five focused Python tests passed**, plus the in-memory route and counterexample probes. Browser fixtures were not rerun under the read-only restriction. No files changed; sibling units excluded.

**VERDICT: NO-GO.**
