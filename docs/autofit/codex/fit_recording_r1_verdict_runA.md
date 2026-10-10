# Fit recording — Codex round 1, run A (commit aa7f31e)

Reviewed `aa7f31e` against `52e5b4a`. Found seven **MAJOR** gaps.

1. **`/api/analyze` drops the record.** Its least-squares adapter calls `run_fit`, then returns fitted peaks and statistics while discarding the seed, actual fit method, background verdict, certificate and software identity. Confirmed by executing the adapter. [least_squares.py:84](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/autofit/methods/least_squares.py:84)

2. **Local and Batch Fit records are incomplete.** `_localFitRecord` stores certification success and restart count, but neither `moved` nor how far the certificate moved the fit. Software identity is always `null`. These omissions persist through every subsequent save/export. A null seed is appropriate for this deterministic engine; missing certificate details and software identity are not. [index.html:8560](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8560)

3. **`.fit.json` drops the record.** `_doSaveFit` explicitly serializes fit statistics but omits `record`; its loader also discards server-fit provenance. It should preserve this information as provenance of the saved parameters, while retaining today’s parameter-only loading behavior—without making the imported model current. [save:11721](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:11721), [load:3453](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:3453)

4. **Figure export contains none of the record.** `_doPublicationExport` downloads the canvas directly as PNG, with no record in the image, metadata or accompanying artifact. This export is outside the implementation and tests despite the requirement. [index.html:12942](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:12942)

5. **CSV, XLSX and TSV discard record data.** Their shared formatter omits individual certificate movements, the largest movement’s component ID, manual background anchors and the background reason. It also rounds movement distances. Executing the formatter showed that different anchors and component IDs produce identical exports, and `0.000012345 eV` becomes `0.0000 eV`. Preserve a lossless record alongside the readable summary. [index.html:8568](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8568)

6. **The required numerical version is absent.** Software identity contains the commit, dirty flag, Python/library versions and seed-derivation tag, but no numerical implementation version. `xps-fit-seed-v2` identifies seed derivation, not the background/solver implementation. The design also omits this owner-required field. [fitting.py:64](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/fitting.py:64)

7. **The export test does not establish its completeness claim.** It checks method and seed values, but mostly checks only labels for background, certificate and software. XLSX’s serialized file is never read: `writeFile` is replaced with inspection of the in-memory worksheet. Missing certificate subfields already pass; empty certificate/software values in TSV or XLSX could also pass. There is no recording coverage for PNG, `.fit.json` or `/api/analyze`. [test_browser_fit_recording.py:98](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/tests/test_browser_fit_recording.py:98)

The additivity checks were favorable:

- Six sampled background paths produced **bit-identical existing response fields** against main. `SEED_TAG` preserves the hashed bytes; `report` copies the existing background certificate.
- Invalid seeds produced identical 400s on both HTTP routes. Real solver replays through `/api/fit`, with session loading mocked in memory, passed `fit_equality` for **all five methods**, including required-component refits and applicable restart paths.
- No new record reads were found in current/stale, notices, locks or acceptance decisions. Project JSON/ZIP share the record-preserving serializer; project and spectrum loaders preserve the record, including seed zero.
- The replay tests genuinely compare separate fits. The browser test reuses the captured original request with the reloaded seed, consistent with the design’s stated scope.

Validation: **10 Python recording tests and 4 JS tests passed**, plus the probes above. Full browser/job suites were not rerun under the read-only constraints. Legacy decision paths appear unchanged by inspection; exhaustive byte-for-byte legacy behavior was not established.

**VERDICT: NO-GO**
