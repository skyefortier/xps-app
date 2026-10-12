# Local link order (Q10 0b) — Codex round 1, run B (commit 086378d)

One **MAJOR** finding prevents approval.

**MAJOR — the final χ² recomputation changes deferred cycle behavior without producing a frozen model.** At [index.html:9567](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9567), `chiSq(params)` propagates links again; the following `applyParams` advances them before commit, and `rawResiduals` advances them again for RMSE. Cycles and self-links remain non-idempotent.

Reproduced with a held Gaussian at centre 285, amplitude 100, width 1, linked to itself with offset 1 and ratio 0.5:

| Result | Main | HEAD |
|---|---:|---:|
| Committed centre | 287 | 288 |
| Committed amplitude | 25 | 12.5 |
| Stored χ² | 5641.068470 | 4936.125269 |
| χ² of committed peaks | 4936.125269 | 4072.132478 |

HEAD’s RMSE also describes the subsequent state, not the committed peaks. A two-peak cycle reproduces the problem. These graphs survive project loading.

**Needs non-physical inputs:** yes—an inconsistent constraint graph; the spectrum and numerical peak values are ordinary. The inconsistency predates this unit, but the extra propagation and changed committed result are new. Keeping cycle order does not preserve cycle behavior. Since graph validation is explicitly deferred, the smallest correction is to remove the redundant recomputation and qualify the idempotence guarantee as applying to acyclic graphs.

The remaining review results:

- **Dependency order:** correct for acyclic graphs with unique IDs. I ran 28,803 graph/order/idempotence checks, including branching, missing parents, mixed numeric/string IDs, and reversed chains through 1,000 peaks. Mixed IDs retain strict matching: `1` and `"1"` are distinct, as in `workPeak`.
- **Other consumers:** for those acyclic graphs, residual evaluation resolves the complete model before the Jacobian or certificate reads it. Commit, support, and record use the resolved state. Batch Fit and fallback call this same engine; I found no additional half-propagation path.
- **Identity measurement:** independently reran the script with writes intercepted: **121 successful fits, 121 identical comparisons, zero differences or skips**. The census also matches: 57 linked tabs, no depth-two chains. Both engines use HEAD’s background helper, but that code is unchanged in this diff. The result supports the stated corpus comparison, not universal identity; JSON equality also is not literally a floating-point bit comparison.
- **Tests:** the four-level test genuinely detects restoration of peak-order propagation. Both shorter tests survive that mutation. Removing only the final recomputation leaves all three passing—as expected for acyclic graphs, where it is redundant. The plan’s “not separately testable” claim needs that qualification.
- **Scope:** beyond the recomputation issue, changes are confined to the intended fix, tests, measurement, documentation, and matching CI count.

The three new tests and 51 acceptance tests passed. Additional suites reported 76 passes and one backend-parity failure caused by the read-only sandbox’s unavailable temporary directory. No files changed.

VERDICT: NO-GO.
