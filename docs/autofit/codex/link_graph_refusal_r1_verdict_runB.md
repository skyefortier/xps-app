Three MAJOR findings prevent approval.

1. **MAJOR — Valid independent peaks with `linked: false` are now refused.**  
   The loader explicitly accepts `false` as “unlinked” and preserves it. The builder, controls and local engine also treat it as unlinked. [The new validator](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/templates/index.html:6460) instead searches for a parent whose ID is `false`. Reproduced: load validation returns `null`; fit validation reports “linked to a peak that is no longer in the model.” The suggested “unlink it” action is unavailable because the controls consider this peak independent.  
   **Non-physical inputs:** No; requires an accepted saved-file representation absent from the census.

2. **MAJOR — Orphans still become successful free fits through `/api/analyze` and the Python twin.**  
   “Refit my current peaks” builds specs without calling `_linkGraphFailure`. Both its builder and [the Python twin](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/autofit/reference.py:149) silently omit `constrain_to` when the parent is missing. The server consequently cannot detect the orphan. Reproduced with an ordinary positive spectrum: the twin dropped the link, and `/api/analyze` returned **HTTP 200, `success: true`**. This is the same defect the unit fixes for Run Fit, still reachable through another requested path. Validate before either builder can erase the evidence.  
   **Non-physical inputs:** No; the unit’s own deleted-root scenario produces this graph.

3. **MAJOR — A family shape switch can turn a valid chain into a refused model.**  
   [_switchPeakShape](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/templates/index.html:5866) updates only the selected parent and its immediate children. Reproduced with `3 → 2 → 1`, initially all GL: switching the root to Voigt leaves `[Voigt, Voigt, GL]`, which the new check refuses. Attempting to switch the grandchild to Voigt also returns early because its immediate parent already has that shape. The existing propagation defect now blocks fitting an otherwise valid family operation. Propagate the switch through the complete family.  
   **Non-physical inputs:** No; requires a supported chain, such as one loaded from a project.

**MINOR — Immediate, consistent refusal remains incomplete at the boundaries.**  
[The shared server validator](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/fitting.py:1472) still accepts a missing parent; I confirmed `_prepare_fit_request` returns fit arguments without an error, so `/api/fit/start` can create a job that fails later. It also lacks duplicate-ID validation for direct Python and analyze callers. Separately, page IDs `1` and `"1"` pass the new duplicate check but both serialize as `"1"`: Run Fit refuses them only after starting, while the local path accepts them. Consistently string-typed linked IDs do pass correctly.  
**Non-physical inputs:** No physical abnormalities; these require malformed graph metadata or mixed-type saved IDs.

The blanket shape rule is **stronger than “cannot fit as drawn.”** A GL child of a Voigt parent can fit and draw correctly: my probe succeeded with the child at 50% mix and maximum drawn-versus-fitted difference **5.7×10⁻¹⁴ counts**. Adding `frontend_shape` makes that same request fail. This follows the explicitly requested blanket ban, so I am not counting it as an unauthorized change, but the technical justification should acknowledge this intentional restriction.

The positive evidence holds: the census reproduces **121 tabs, 530 peaks, 67 links, zero refusals**. Focused validator tests, the local refusal test and both pinned Python/page parity tests passed. For the tested valid pair, `frontend_shape` changed neither seed, fitted curve nor full fit record, and did not appear in the result. Auto-Fit’s own builder creates unlinked peaks. Browser tests were not rerun under the read-only restriction.

The new tests prove their sampled cases, but the source-pattern test claiming “every fit path” misses the analyze/twin bypass and the accepted `false` representation. Sibling units 0b and 0c were excluded from these findings. No files were changed.

VERDICT: NO-GO.
