# Fit recording — Codex round 1, run B (commit aa7f31e)

Reviewed `52e5b4a..aa7f31e`. Found seven **MAJOR** gaps.

1. **`/api/analyze` drops the record.** Its least-squares method calls `run_fit`, then retains only peaks, statistics, uncertainties and the message. The actual fit method, seed, background verdict, certificate and software identity disappear. This is a reachable fit-producing endpoint despite Find Peaks being archived. [least_squares.py:83](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/autofit/methods/least_squares.py:83)

2. **CSV, XLSX and TSV lose record data.** `_fitRecordRows` omits manual anchors, background reason, per-component certificate movements and the largest-movement component ID. It rounds residuals and movement distances. An executable probe confirmed that different anchors and certificate movements export identically—including a nonzero movement rendered as `0.0000 eV`. Preserve the complete record alongside the readable summary. [index.html:8568](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8568)

3. **Figure export carries no record.** `_doPublicationExport` downloads the canvas PNG without recording metadata or an accompanying record. None of the required provenance survives this export. [index.html:12940](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:12940)

4. **`.fit.json` discards the record.** Its `fitStatistics` whitelist excludes `record`. It should retain this as the saved parameters’ provenance: the format already preserves statistics and certificate notices. Importing those parameters onto another spectrum should continue to clear the active fit; retaining provenance must not change that legacy rule. [index.html:11721](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:11721)

5. **Local and Batch Fit records are incomplete.** `_localFitRecord` fabricates a summary rather than retaining the background certificate’s result: residual is always null, and background effect is absent. Its minimum certificate omits whether certification moved the solution and how far. Software identity is always null. A null seed is appropriate for this deterministic engine, but it does not justify discarding the other evidence. [index.html:8560](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8560)

6. **The required numerical version is missing.** Software records contain the Git commit, tracked-dirty flag, Python/library versions and seed-derivation tag. There is no numerical-algorithm version; `xps-fit-seed-v2` versions seed hashing, not the numerical implementation. The import-time snapshot does avoid rereading the checkout for every response. [fitting.py:64](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/fitting.py:64)

7. **The export test does not establish its completeness claim.** It checks exact method/seed text, then mostly checks that three labels exist. Missing certificate movements, anchors and other fields therefore pass. CSV/TSV checks use actual generated text; XLSX checks the workbook before serialization, without reading an exported file. There is no complete record round-trip assertion for exports, nor coverage of figure or `.fit.json` recording. [test_browser_fit_recording.py:98](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/tests/test_browser_fit_recording.py:98)

The other requested checks were reassuring:

- **Additivity:** eight-background comparisons against an in-memory copy of `main` preserved seeds and existing response fields within `fit_equality`. `SEED_TAG` hashes the same bytes; `report` copies the existing background certificate. No new record fields govern stale/current status, notices, locks or acceptance.
- **HTTP seed:** both routes share validation. The caller seed is consumed before solver options are forwarded. Replay probes passed for all five methods, with identical solver-seed sequences, perturbed starts, applicable scattered starts and required-component refits.
- **Persistence:** Run Fit, Use this solution and Auto-Fit attach the server record. Project JSON/ZIP share the record-preserving serializer and loader; spectrum save/load explicitly preserves it, including seed zero.
- **Legacy/replay:** no legacy restore-rule change found. The browser replay test genuinely compares separate fits using the original captured request and the reloaded seed; it does not demonstrate reconstruction from the save alone.

Validation: 10 focused Python tests and four recording JS tests passed. Another 121 JS tests passed; one failed because a Python subprocess could not obtain a writable temporary directory. Browser suites were not rerun. Workspace unchanged.

VERDICT: NO-GO.
