# Envelope identity — Codex round 3, run B (commit 2c31d8e)

**MAJOR — the “as drawn” check still counts hidden components.** [DRAWN, line 61](/Users/skyefortier/xps-app/.claude/worktrees/envelope-identity/tests/test_browser_envelope_identity.py:61) selects every `_peakId` dataset without checking chart visibility. A hidden component therefore satisfies the new completeness assertion despite being absent from the display. Chart.js supports hiding through both dataset properties and metadata; `isDatasetVisible()` checks both. [Chart.js API](https://www.chartjs.org/docs/latest/developers/api.html#isdatasetvisible-datasetindex)

Using a real Gaussian fit, the committed JavaScript reader, and in-memory chart datasets:

| Mutation | Result |
|---|---|
| Remove one or all components | Rejected |
| Duplicate a component | Rejected |
| Shorten a component | Rejected |
| Set first component’s `hidden = true` | **Passes; snapshot unchanged** |

The hidden component reaches **8,997.51 counts**. Thus a visibility regression can still produce the conspicuous envelope-above-visible-components defect this unit claims to prevent.

Require the envelope, background, and every expected component to be visible through `chart.isDatasetVisible(index)`. Add a negative proof that hides a component through Chart.js and updates the chart after fitting.

The round-2 removal/duplication finding is otherwise fixed. The revised LA explanation adequately accounts for the remaining normalization and arithmetic terms within the existing margin for these fixtures. No additional findings from reviewing the earlier fixes.

Validation: **34 server tests passed in 84.79 seconds**, plus the in-memory mutations above. Full browser execution was not rerun under the read-only restrictions. No files changed.

VERDICT: NO-GO
