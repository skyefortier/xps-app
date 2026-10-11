# Fit recording — Codex round 5, run B (commit cebc470)

**MAJOR — unbounded record fields break standard readers.** [index.html:8621](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8621) places the entire base64 record in one field without a size bound.

Reproduced with a **successful server Gaussian fit and 4,000 manual-background anchors**:

- Plain JSON: **155,491 characters**.
- Base64 field: **207,352 characters**.
- Python `csv.reader`, with either delimiter: **`field larger than field limit (131072)`**. Pandas’ Python engine likewise rejects oversized records.
- The plain JSON also exceeds Excel’s **32,767-character** cell limit.

**Non-physical inputs required: no.** All energies and counts were finite, and the background converged. However, this is an unusually large anchor set, not a typical manual background. Ordinary-sized records passed; I found no realistic small-record Excel-size problem. The explicitly requested very-long-record guarantee fails.

Other results:

- **Placement passed:** 480 in-memory comparisons of the actual export functions covered server/local/global/legacy records, stale/unverified states, unsupported components, failed backgrounds, and optional metadata lines. CSV/TSV prefixes and both XLSX row arrays matched main. Each old placement failed.
- **Encoding passed:** tested delimiters, quotes, control characters, Unicode, component IDs and software strings; base64 decoded losslessly. Both pandas delimiters preserved the previous comment-filtered frame in 120 comparisons.
- **New test:** main’s rendering matches its original route; assertions are non-vacuous, and CI fetches full history and guards skips. Coverage remains limited to two fit examples; TSV comment-frame comparison is explicitly omitted at [test_browser_export_prefix.py:164](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/tests/test_browser_export_prefix.py:164), and long records are untested.

Validation: **95 JavaScript tests and 11 Python tests passed**. Browser and HTTP verification were blocked by read-only temporary-directory restrictions. Workspace unchanged.

VERDICT: NO-GO
