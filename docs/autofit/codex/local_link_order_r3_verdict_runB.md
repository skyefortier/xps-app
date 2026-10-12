**MAJOR — malformed graphs containing reversed chains still change committed results.** The ordering code in [index.html:9338](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9338) treats a missing parent as ready and reorders its descendants. Duplicate IDs likewise do not preserve the legacy pass. This violates the explicit requirement that malformed graphs retain main’s results until unit 0c′.

Reproduced against actual `8cc3750` code with these four peaks, in order. All are held Gaussians, FWHM 1; every link has offset 2 and ratio 0.5:

| ID | Parent | Initial centre | Initial amplitude |
|---|---|---:|---:|
| 4 | 3 | 279 | 1 |
| 3 | 2 | 280 | 1 |
| 2 | 1 | 281 | 2 |
| 1 | 99 (missing) | 285 | 100 |

Use 401 points, `280 + 0.05*i`, intensity 10, background zero. Both engines report success:

| Saved result | Main | HEAD `b6d0f2c` |
|---|---:|---:|
| Peak 4 centre | 285 | 291 |
| Peak 4 amplitude | 0.5 | 12.5 |
| χ² | 16438.864857923374 | 16097.054879782161 |

A second reproduction removes the missing link and appends another root with ID 1, centre 286, amplitude 60. That duplicated-parent graph also changes peak 4 from **285 / 0.5** to **291 / 12.5**.

**Needs non-physical inputs:** malformed graph structure, yes; non-physical spectral or numerical values, no. Preserve the original pass for malformed graphs and add these combinations to the comparison regression; refusal remains separate.

The other requested checks support the intended fix:

- **Valid graphs:** 2,000 shuffled forests with branching and mixed numeric/string IDs matched an independent recursive oracle and were idempotent. Object tracking fixes the round-2 omission; first-match parent lookup matches main.
- **Consumers:** no additional half-propagated read found for valid graphs in the Jacobian, certificate, support, record, Batch Fit or fallback.
- **Identity:** reproduced **121 successful fits, 121 bit-identical comparisons, zero differences/skips**, matching the saved rows. The corpus contains 57 linked tabs and no multilevel chains. `Object.is` comparisons are sound; shared background code is unchanged, and this corpus has no manual backgrounds. This establishes corpus identity, not universal identity.
- **Tests:** the comparison really runs main’s `runFitLocal`. Restoring `39d04d6` makes it fail on duplicate children; restoring main fails all three chain tests. The new regression is genuine but omits malformed graphs containing reversed chains.
- **Scope:** no unrelated production changes found. The malformed-graph behavior above is the remaining scope violation.

Validation: **92 tests passed; one backend-parity test failed because the read-only sandbox has no writable temporary directory.** No files changed.

VERDICT: NO-GO.
