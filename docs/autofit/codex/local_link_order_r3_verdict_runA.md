**MAJOR — malformed graphs containing reversed chains still change results.** The ordering at [index.html:9330](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9330) also processes graphs with missing parents or duplicate IDs. Tracking objects fixes round 2’s omission, but does not preserve main’s behavior for all malformed graphs.

Reproducer: held Gaussians, FWHM 1, listed in this order; every link has offset 2 and ratio 0.5:

| ID | Parent | Initial centre | Amplitude |
|---|---:|---:|---:|
| 4 | 3 | 279 | 1 |
| 3 | 2 | 280 | 1 |
| 2 | 1 | 281 | 2 |
| 1 | 99 (missing) | 285 | 100 |

Use 401 points, `280 + 0.05*i`, counts 10, background zero. Both engines report success:

| Result | Main `8cc3750` | HEAD `b6d0f2c` |
|---|---:|---:|
| Committed ID-4 centre | 285 | 291 |
| Committed ID-4 amplitude | 0.5 | 12.5 |
| Stored χ² | 16438.864857923374 | 16097.054879782161 |

A duplicated-parent variant also fails preservation: remove ID 1’s link and append another held ID-1 peak at centre 286, amplitude 80. ID 4 changes identically; stored χ² changes from **31699.329139758258** to **31357.54121310796**.

**Needs non-physical inputs:** yes, malformed graph identity/references; no non-physical numerical values. These graphs are accepted by project loading. Their pre-existing defects are deferred, but changing their committed results violates this unit’s explicit scope. Retain the legacy propagation pass for malformed graphs and add these comparison cases; refusal remains in 0c′.

The remaining checks support the intended fix:

- **Valid ordering:** 2,000 shuffled forests with branching and mixed numeric/string IDs matched an independent recursive oracle, applied every linked object once, and were idempotent. Already ordered forests matched the legacy pass. A reversed 1,000-peak chain passed.
- **Other consumers:** for valid graphs, I found no remaining half-propagated read in the Jacobian, certificate, support, record, Batch Fit copy, or fallback.
- **Identity:** reproduced **121 successful fits, 121 exact matches, zero differences/skips**, matching the saved rows. The corpus contains 57 linked tabs and no multilevel chains. `Object.is` comparisons are sound for these results; this establishes corpus identity, not universal identity. Shared background code is unchanged, and the corpus has no manual backgrounds.
- **Tests:** the comparison genuinely executes main’s `runFitLocal`. Substituting round 2’s engine makes it fail on duplicate children; substituting main makes all three chain tests fail. The [malformed fixtures](/Users/skyefortier/xps-app/.claude/worktrees/local-links/tests/js/local_lm_descent.test.js:778) miss the combinations above.
- **Scope:** no unrelated production edits found; the malformed-graph behavior change is the outstanding issue.

Validation: **92 tests passed**; one backend-parity test failed because the read-only sandbox has no writable temporary directory. No files changed.

VERDICT: NO-GO
