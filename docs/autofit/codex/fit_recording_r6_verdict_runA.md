# Fit recording — Codex round 6, run A (commit c85fe29)

Reviewed `52e5b4a..c85fe29`, focusing on the commit after `cebc470`. Two MAJOR findings remain.

1. **Summary fields still exceed reader limits.** [index.html:8629](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8629) and [index.html:8638](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8638) split only JSON; summaries remain unbounded.

   A 140,000-character component ID produces a **140,091-character text line** and **140,068-character XLSX cell**. Python `csv.reader` and pandas’ Python engine reject the text with either delimiter: `field larger than field limit (131072)`. The XLSX cell exceeds 32,767 characters. Long software strings reproduce it too.

   **Non-physical inputs required: no.** This requires crafted oversized imported metadata, not ordinary generated identifiers. Bound or split summary fields too; retain the complete value in the lossless JSON.

2. **The surrogate-boundary test does not prove its claim.** [fit_recording.test.js:114](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/tests/js/fit_recording.test.js:114) claims surrogate pairs cross part boundaries, but replacing `Array.from(text)` with unsafe `text.split('')` still passes all six recording tests.

   That mutation splits `'a'.repeat(15999) + '😀'` inside the surrogate pair. Add a deliberately aligned boundary case. The current production splitter handles it correctly; this is a test defect under your severity rules.

   **Non-physical inputs required: no.** Ordinary Unicode text suffices.

Other checks:

- **Placement:** 1,536 extracted-writer comparisons passed across server/local/global/legacy records, current/stale/unverified states, unsupported components, failed backgrounds and all optional-notice combinations. Both XLSX row arrays preserved their prefixes. Each old placement failed its corresponding comparison.
- **Readers and encoding:** adversarial summaries contained no forbidden delimiters after sanitizing. UTF-8 base64 and plain-JSON reassembly passed. Both pandas engines preserved comment-filtered frames in 96 comparisons across both delimiters.
- **JSON parts:** the 8,000-anchor case passed reader limits and round trips. Numbering identifies order and count; production splitting preserves surrogate pairs. Ordinary records fit comfortably within Excel’s limit.
- **Tests:** removing comma, quote, tab, CR or LF sanitizing now fails a test; removing splitting also fails. Main’s rendering matches its original route by inspection. CI fetches full history and guards aggregate skips; browser fixtures can still skip locally.

Validation: **96 JavaScript tests and 11 Python tests passed.** Browser execution and actual XLSX serialization were not rerun under the read-only restrictions. Workspace unchanged.

VERDICT: NO-GO
