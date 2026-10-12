**MAJOR — falsy link targets bypass the well-formedness guard, so malformed graphs still change committed results.** At [index.html:9330](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9330), `filter(q => q.linked)` excludes numeric `0`, `-0` and `NaN` from validation. The readiness check then treats those peaks as roots and reorders their descendants.

Reproduced against actual main `8cc3750` and HEAD `d37cdd9`: held Gaussians, FWHM 1, listed below, every link offset 2 and ratio 0.5.

| ID | Parent | Initial centre | Initial amplitude |
|---|---:|---:|---:|
| 4 | 3 | 279 | 1 |
| 3 | 2 | 280 | 1 |
| 2 | 1 | 281 | 2 |
| 1 | 0, missing | 285 | 100 |

Use 401 points, `280 + 0.05*i`, counts 10, background zero. Both engines report success:

| Result | Main | HEAD |
|---|---:|---:|
| Committed ID-4 centre | 285 | 291 |
| Committed ID-4 amplitude | 0.5 | 12.5 |
| Stored χ² | 16438.864857923374 | 16097.054879782161 |

The load validator accepts `linked: 0`. I also reproduced changed results with `-0`, `NaN`, a zero-ID self-link and a cycle through ID zero.

**Needs non-physical inputs:** malformed graph references, yes; non-physical spectral values, no. The zero-target reproduction uses finite numbers and passes load validation. Preserve main’s pass for these graphs; refusal remains in 0c′. Add explicit falsy-target cases to the comparison regression.

The remaining checks support the intended fix:

- **Ordering:** 2,000 shuffled forests with truthy links matched an independent recursive oracle and were idempotent. Another 1,855 malformed operational graphs preserved peak order, including duplicate-ID edge cases. The falsy-reference hole prevents the blanket well-formedness claim.
- **Other consumers:** for correctly recognized valid graphs, I found no additional half-propagated read in the Jacobian, certificate, support, record, Batch Fit copy or fallback.
- **Identity:** reproduced **121 successful fits, 121 exact matches, zero differences/skips**, matching the saved rows. I suppressed artifact writes in memory. The script’s `Object.is` comparison is sound for the compared outputs; shared background helpers are unchanged. This establishes corpus identity, not universal identity.
- **Tests:** the comparison really executes main’s engine. Substituting `39d04d6` fails on duplicate children; substituting `b6d0f2c` fails on the missing-root chain; substituting main fails all three chain tests. The tests are genuine regressions but omit the falsy-reference cases.
- **Scope:** no unrelated production edits found. The malformed-graph behavior change above remains outside the authorized scope.

Validation: **92 tests passed; one backend-parity test failed because the read-only sandbox has no writable temporary directory.** No files changed.

VERDICT: NO-GO
