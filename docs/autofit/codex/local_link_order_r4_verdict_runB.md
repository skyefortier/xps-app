**MAJOR — the well-formedness guard misses explicit falsy parent references.** At [index.html:9330](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9330), `filter(q => q.linked)` excludes `linked: 0`, `-0` and `NaN` before checking missing parents or cycles. A malformed graph containing such a reference can therefore be reordered.

Reproducer: held Gaussians, FWHM 1, listed below. Every link has offset 2 and ratio 0.5. Use 401 points, `280 + 0.05*i`, counts 10, background zero.

| ID | Parent | Initial centre | Amplitude |
|---|---:|---:|---:|
| 4 | 3 | 279 | 1 |
| 3 | 2 | 280 | 1 |
| 2 | 1 | 281 | 2 |
| 1 | 0, missing | 285 | 100 |

Both engines succeed:

| Saved result | Main `8cc3750` | HEAD `d37cdd9` |
|---|---:|---:|
| Peak 4 centre | 285 | 291 |
| Peak 4 amplitude | 0.5 | 12.5 |
| χ² | 16438.864857923374 | 16097.054879782161 |

Main historically ignores the falsy reference; the new guard also ignores it and consequently reorders the remaining chain. That violates the requested preservation of graphs with **any missing parent**. The validation must distinguish an absent link from an explicit invalid reference while retaining main’s propagation behavior on rejection.

**Needs non-physical inputs:** malformed graph structure, yes; non-physical numerical values, no.

**MAJOR — a singleton `NaN` ID passes the guard but cannot be committed.** The [uniqueness check](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9332) accepts one `NaN`, while `workPeak` and `getPeak` use strict equality, which cannot find it.

In the preceding fixture, remove the root’s link and change peak 4’s ID to `NaN`. HEAD reports success and stores χ² **16097.054879782161**, but the committed peaks evaluate to **16389.93788632**: the leaf remains at centre **279**, amplitude **1**. Main’s stored χ² was **16438.864857923374**.

The commit-lookup defect already exists on main; this unit nevertheless reorders that graph and changes its result. Preserve its legacy pass here; refusal belongs in 0c′.

**Needs non-physical inputs:** yes, a `NaN` identifier; spectral values and peak parameters remain finite.

The remaining checks passed:

- **Ordering:** 2,000 shuffled valid forests matched an independent recursive oracle and were idempotent. Another 12,000 malformed variants retained the legacy pass, including duplicate `0`/`-0` and duplicate `NaN` IDs. Numeric `1` and string `'1'` remain distinct for ordering.
- **Consumers:** no additional half-propagated read found for ordinary valid graphs in the Jacobian, certificate, support, record, Batch Fit copy or fallback.
- **Identity:** reproduced **121/121 exact matches**, zero differences/skips, matching the saved report. The corpus contains 57 linked tabs and no multilevel chains. The method supports corpus identity, not universal identity.
- **Tests:** the comparison really executes main’s fitter. Substituting `39d04d6` fails on duplicate children; substituting `b6d0f2c` fails on the missing-root chain. Substituting main fails all three chain tests. The fixtures omit the edge cases above.
- **Scope:** no unrelated production changes found.

Validation: **92 tests passed; one backend-parity test failed because the read-only sandbox has no writable temporary directory.** No files changed.

VERDICT: NO-GO
