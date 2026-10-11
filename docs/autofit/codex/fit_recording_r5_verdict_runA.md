# Fit recording — Codex round 5, run A (commit cebc470)

Reviewed `52e5b4a..cebc470`, focusing on round 5.

**MAJOR — the reader regression tests do not prove their stated claim.**

- In [fit_recording.test.js:83](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/tests/js/fit_recording.test.js:83), adversarial quotes, tabs and newlines occur only in `backgroundVerdict.reason`. That field travels inside base64; it never exercises summary sanitizing. **Removing quote/tab/CR/LF sanitizing still passes all five recording tests.** Put adversarial text in component IDs and software strings that enter summaries.
- [test_browser_export_prefix.py:164](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/tests/test_browser_export_prefix.py:164) explicitly omits the TSV `comment='#'` frame comparison. Run that assertion for both formats with `sep=sep`.

**Input category:** neither test defect requires non-physical numerical inputs. This is MAJOR under your “test that does not test its claim” rule; the current sanitizer itself passed my adversarial checks.

Other results:

- **Placement:** 384 extracted-function comparisons passed across server/local/global/legacy records, current/stale/unverified states, unsupported components, failed backgrounds and every combination of the three extra notice lines. CSV/TSV preserved exact prefixes; both XLSX row arrays preserved existing content. Old placements failed each format’s independent prefix assertion.
- **Readers and encoding:** tested summary text and labels contained no forbidden delimiters. Unicode and base64 round trips passed. Both pandas comment-filtered frames matched main in 96 comparisons.
- **Size limits:** a representative 20-anchor record was 1,334 characters, comfortably within Excel’s limit. The unlimited-input claim needs qualification: crafted imports with 1,000 anchors produced 39,295 JSON characters; 4,000 anchors exceeded Python csv’s default 131,072-character field limit. These require oversized imported data beyond the UI’s 20-anchor cap, although the numerical values can remain physical.
- **Test infrastructure:** main’s template rendering appears faithful; full-history checkout is configured. Browser fixtures can skip when dependencies are unavailable, with CI’s aggregate skip guard providing protection.

Validation: **95 JS tests and 11 Python tests passed.** Browser execution was blocked by read-only temporary-directory restrictions, so actual XLSX serialization was not independently rerun. Workspace unchanged.

VERDICT: NO-GO.
