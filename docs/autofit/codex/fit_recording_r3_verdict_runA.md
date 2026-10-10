# Fit recording — Codex round 3, run A (commit bcb006e)

Reviewed `52e5b4a..bcb006e`, focusing on the commit after `e8421dc`.

**MAJOR — `centre_moves` still omits every component when all parameters are locked.** The snapshot exists only inside `certify()`, but [the zero-free-parameter path](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:9355) short-circuits certification. Consequently, [record construction](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:9510) emits an empty list.

Reproduced with a Gaussian at 285 eV, FWHM 1.2, amplitude 10, all three parameters locked, on 280–290 eV at 0.05 eV spacing. Both that model and a version with a linked child return success with:

```json
{"certified":true,"restarts":0,"moved":false,"centre_moves":[],"largest_centre_move":null}
```

These successful local fits should record each component’s zero centre displacement. Capture this terminal point without changing solver behavior, and add an all-locked regression test.

Round-2 disposition:

- **Centre-only `moved`: resolved.** It now compares the complete free-parameter vector against the first stop.
- **Missing linked/locked centre movements: partially resolved.** The restart cases pass; the all-locked path above remains uncovered.
- **Missing background effect: resolved.** No difference from the server helper across 8,000 combinations covering methods, window direction/fallback, averaging, and zero/one/multiple manual anchors.

Other checks were favorable:

- Existing local outputs were bit-identical against main across 30 synthetic fits covering six shapes, locks and linkage.
- No attached-property leakage found into JSON, numeric iteration, slices, save data or stack/restore comparisons.
- Batch Fit and Run Fit fallback pass the computed background directly; reading its method introduces no identified record regression.

Validation: **11 Python tests and 123 JS tests passed**. One Python-backed JS check was blocked by temporary-directory restrictions. Browser suites were not rerun. Workspace unchanged.

VERDICT: NO-GO
