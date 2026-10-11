# Fit recording — Codex round 6, run B (commit c85fe29)

Reviewed `52e5b4a..c85fe29`, focusing on the commit after `cebc470`. Two MAJOR findings remain.

1. **Summary fields remain unbounded and break reader limits.** [index.html:8629](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8629) and [index.html:8638](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8638) split only JSON; summary values bypass splitting.

   Reproduced using `certificate.largest_centre_move.id`:
   - 140,000 characters produce a **140,098-character record line**. Python csv and pandas’ Python engine reject it with either delimiter: `field larger than field limit (131072)`.
   - 32,768 characters produce a **32,843-character XLSX summary cell**, exceeding Excel’s 32,767 limit.

   The large-record tests grow anchors and reasons, leaving summary fields short. Bound every emitted summary line/cell too, and test oversized summary values.

   **Non-physical inputs required: no.** This requires unusually large imported metadata; numerical values can remain physical.

2. **The surrogate-boundary test does not prove its claim.** [fit_recording.test.js:114](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/tests/js/fit_recording.test.js:114) adds emoji but does not force a surrogate pair onto a splitting boundary.

   Replacing `Array.from(text)` with `text.split('')` leaves **all six recording tests passing**. That mutation splits both halves of the emoji in `'x'.repeat(15999) + '😀' + 'y'` into separate parts. Add an explicitly aligned boundary case. The production splitter itself passed that case.

   **Non-physical inputs required: no.** Ordinary Unicode text exposes this test gap. This is MAJOR under your test-proof severity rule.

Other checks:

- **Placement:** 1,536 extracted-function comparisons passed across the requested fit/state combinations, both text formats and both XLSX row arrays. Restoring each old placement failed its prefix assertion.
- **Readers:** 1,536 pandas comment-frame comparisons passed across both delimiters and both engines. Sanitizer mutations removing comma, quote or whitespace handling now fail.
- **Encoding and parts:** Large anchor/Unicode records reassembled losslessly from UTF-8 base64 and plain JSON parts. Numbering, delimiter safety and JSON-part limits passed. The remaining size failure is in summaries.
- **Infrastructure:** Main’s template rendering matches its original route; CI fetches full history. Browser fixtures can skip, with CI’s skip guard providing protection.

Validation: **96 JavaScript tests and 11 backend tests passed**. Browser execution and actual XLSX serialization were not independently rerun under the read-only restrictions; XLSX comparisons used row arrays. Workspace unchanged.

VERDICT: NO-GO
