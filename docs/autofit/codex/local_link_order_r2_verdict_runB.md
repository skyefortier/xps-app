Round 1’s extra-evaluation defect is fixed, but the full unit still has **one MAJOR finding**.

**MAJOR — duplicate peak IDs change the committed result.** In [index.html:9334](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9334), `done` tracks IDs rather than peak objects. Once one linked peak is scheduled, another with the same ID is omitted entirely, including from the fallback. Project loading accepts duplicate IDs; I verified `_peaksLoadError` returns `null`.

Reproducer: three held Gaussians, FWHM 1, in this order:

| ID | Parent | Starting centre | Amplitude | Offset | Ratio |
|---|---|---:|---:|---:|---:|
| 1 | none | 285 | 100 | — | — |
| 2 | 1 | 280 | 1 | 2 | 0.5 |
| 2 | 1 | 281 | 2 | 4 | 0.25 |

Use 401 points, `280 + 0.05*i`, counts 10, background zero. Both engines report success:

| Result | Main `8cc3750` | HEAD |
|---|---:|---:|
| First ID-2 peak’s committed centre | 289 | 281 |
| Its committed amplitude | 25 | 2 |
| Stored χ² | 16390.396933462474 | 16420.830225973714 |

Main already mishandles duplicate identities; **the newly changed committed model and statistic** violate this unit’s “no other change” requirement. Preserve the original pass for duplicate-ID inputs and add a comparison regression; broader validation can remain deferred.

**Needs non-physical inputs:** yes in the sense of malformed model identity—duplicate IDs. All numerical inputs are finite and physically ordinary.

The remaining checks support the intended fix:

- **Dependency order:** passed 2,000 shuffled acyclic forests with branching, missing parents and mixed numeric/string IDs, plus a reversed 1,000-link chain. One application resolved them; a second was identical. This guarantee requires unique IDs.
- **Cycles/self-links:** remain non-idempotent, as explicitly deferred. The concrete self-link and two-peak cycle now match main exactly. Another 2,000 propagation comparisons preserved cycle behavior.
- **Other consumers:** for unique-ID acyclic graphs, I found no remaining half-propagated read in the Jacobian, certificate, support, record, Batch Fit or fallback.
- **Identity measurement:** reproduced **121 successful fits, 121 identical, zero differences/skips** against `8cc3750`; 57 linked tabs, no multilevel chains. `Object.is` correctly distinguishes signed zero. The shared background helper and omitted manual anchors do not invalidate this corpus comparison. This is corpus evidence, not universal identity.
- **Tests:** all four additions pass. Restoring peak-order propagation now fails all three chain tests, including the four-level case. Reintroducing the extra final χ² evaluation fails the self-link test. Recalculation is redundant only for idempotent graphs; the plan now removes the overbroad claim.
- **Scope:** no unrelated production changes found beyond the duplicate-ID behavior above.

Validation: **124 tests passed**; one backend-parity test failed because the read-only sandbox has no writable temporary directory. Review probes and identity replay made no file changes.

VERDICT: NO-GO.
tokens used
62,527
Round 1’s extra-evaluation defect is fixed, but the full unit still has **one MAJOR finding**.

**MAJOR — duplicate peak IDs change the committed result.** In [index.html:9334](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9334), `done` tracks IDs rather than peak objects. Once one linked peak is scheduled, another with the same ID is omitted entirely, including from the fallback. Project loading accepts duplicate IDs; I verified `_peaksLoadError` returns `null`.

Reproducer: three held Gaussians, FWHM 1, in this order:

| ID | Parent | Starting centre | Amplitude | Offset | Ratio |
|---|---|---:|---:|---:|---:|
| 1 | none | 285 | 100 | — | — |
| 2 | 1 | 280 | 1 | 2 | 0.5 |
| 2 | 1 | 281 | 2 | 4 | 0.25 |

Use 401 points, `280 + 0.05*i`, counts 10, background zero. Both engines report success:

| Result | Main `8cc3750` | HEAD |
|---|---:|---:|
| First ID-2 peak’s committed centre | 289 | 281 |
| Its committed amplitude | 25 | 2 |
| Stored χ² | 16390.396933462474 | 16420.830225973714 |

Main already mishandles duplicate identities; **the newly changed committed model and statistic** violate this unit’s “no other change” requirement. Preserve the original pass for duplicate-ID inputs and add a comparison regression; broader validation can remain deferred.

**Needs non-physical inputs:** yes in the sense of malformed model identity—duplicate IDs. All numerical inputs are finite and physically ordinary.

The remaining checks support the intended fix:

- **Dependency order:** passed 2,000 shuffled acyclic forests with branching, missing parents and mixed numeric/string IDs, plus a reversed 1,000-link chain. One application resolved them; a second was identical. This guarantee requires unique IDs.
- **Cycles/self-links:** remain non-idempotent, as explicitly deferred. The concrete self-link and two-peak cycle now match main exactly. Another 2,000 propagation comparisons preserved cycle behavior.
- **Other consumers:** for unique-ID acyclic graphs, I found no remaining half-propagated read in the Jacobian, certificate, support, record, Batch Fit or fallback.
- **Identity measurement:** reproduced **121 successful fits, 121 identical, zero differences/skips** against `8cc3750`; 57 linked tabs, no multilevel chains. `Object.is` correctly distinguishes signed zero. The shared background helper and omitted manual anchors do not invalidate this corpus comparison. This is corpus evidence, not universal identity.
- **Tests:** all four additions pass. Restoring peak-order propagation now fails all three chain tests, including the four-level case. Reintroducing the extra final χ² evaluation fails the self-link test. Recalculation is redundant only for idempotent graphs; the plan now removes the overbroad claim.
- **Scope:** no unrelated production changes found beyond the duplicate-ID behavior above.

Validation: **124 tests passed**; one backend-parity test failed because the read-only sandbox has no writable temporary directory. Review probes and identity replay made no file changes.

VERDICT: NO-GO.
