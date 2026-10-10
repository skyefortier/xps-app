# Envelope identity — Codex round 3, run A (commit 2c31d8e)

Reviewed `90651e6..2c31d8e`, focusing on `7141a0e..HEAD`.

**MAJOR — hidden components still count as drawn.** [DRAWN, line 61](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_browser_envelope_identity.py:61) selects every component dataset without checking Chart.js visibility. The new completeness assertion therefore accepts components absent from the visible chart. Chart.js supports hiding datasets while retaining their data. [Visibility API](https://www.chartjs.org/docs/latest/developers/api.html#isdatasetvisible-datasetindex)

Using a real Gaussian fit, the committed JavaScript reader, and in-memory chart datasets:

| Mutation | Assertion result |
|---|---|
| Remove one/all components | Rejected |
| Duplicate a component | Rejected |
| Shorten a component | Rejected |
| Hide one component | **Passes; visible sum misses 8,997.51 counts** |
| Hide all components | **Passes; visible sum misses 9,000.76 counts** |

Hiding produces an identical `DRAWN` snapshot. Require `chart.isDatasetVisible(index)` for the envelope, background, and every expected component. Add a negative proof that hides a component and updates the chart.

The round-2 removal/duplication defect is fixed. The revised LA derivation addresses the previous MINOR without widening the tolerance. I found no additional issue in the numerical bounds, lock checks, alignment checks, or disclosed coverage omissions.

Validation: **34 server tests passed in 84.42 seconds**; 27 browser tests collected. Browser execution was not rerun under read-only restrictions; the mutations above ran without a browser. No files changed.

VERDICT: NO-GO
