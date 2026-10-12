**MAJOR — duplicate peak IDs cause the new ordering code to omit linked peaks, changing results beyond the intended chain fix.** In [index.html:9334](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9334), `done` tracks IDs rather than peak objects. Once one linked peak is processed, another with the same ID is excluded from both the dependency pass and the fallback. Also, `byId` selects the last duplicate, whereas `workPeak` selects the first.

The page can hold this input: [project loading](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:12495) preserves duplicate peak IDs.

Reproduced with three held Gaussians, width 1, 401 points spanning 280–300, counts 10 and zero background:

- Root: ID 1, centre 285, amplitude 100.
- Child: ID 2, centre 280, amplitude 1, linked to 1, offset 2, ratio 0.5.
- Another child: ID 2, centre 281, amplitude 2, linked to 1, offset 3, ratio 0.25.

Both engines report success:

| Result | Main `8cc3750` | HEAD `39d04d6` |
|---|---:|---:|
| First ID-2 entry’s committed centre | 288 | 281 |
| Its committed amplitude | 25 | 2 |
| Stored χ² | 17316.589441709737 | 16420.830225973714 |

Duplicate-ID behavior was already defective; **silently dropping a propagation operation and changing the committed result is new**. Preserve the legacy pass for ambiguous IDs in this unit, leaving validation to its separate unit.

**Needs non-physical inputs:** an invalid model with duplicate IDs, yes; non-physical spectral or numerical values, no.

The remaining checks support the intended fix:

- **Ordering and idempotence:** 2,000 shuffled forests passed against an independent recursive oracle, including branching, missing parents and mixed numeric/string IDs. Reversed chains through 1,000 peaks passed. These guarantees require unique IDs and acyclic dependencies.
- **Round 1 regression:** self-links and two-peak cycles now match main exactly. Another 500 cycles with dependent trees retained the old propagation behavior. Their existing non-idempotence remains; this branch does not refuse them.
- **Consumers:** for valid graphs, I found no remaining half-propagated read in the Jacobian, certificate, support, record, Batch Fit or fallback.
- **Identity:** independently reproduced **121 successful fits, 121 exact comparisons, zero differences or skips**, matching the saved rows. Confirmed 57 linked tabs and no multi-level chains. `Object.is` fixes the signed-zero comparison weakness. The shared background implementation is unchanged, and manual backgrounds are absent from this corpus. This establishes corpus identity, not universal identity.
- **Tests:** all four additions pass. Restoring peak-order propagation now fails all three chain tests, including the four-level case. Restoring the extra final χ² evaluation fails the self-link test. Its redundancy for valid graphs is correctly distinguished from its observable effect on invalid ones.
- **Scope:** apart from the duplicate-ID regression, production changes are confined to link ordering.

Validation: **91 tests passed; one backend-parity test failed because the read-only sandbox has no writable temporary directory.** No files changed.

VERDICT: NO-GO.
tokens used
72,721
**MAJOR — duplicate peak IDs cause the new ordering code to omit linked peaks, changing results beyond the intended chain fix.** In [index.html:9334](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9334), `done` tracks IDs rather than peak objects. Once one linked peak is processed, another with the same ID is excluded from both the dependency pass and the fallback. Also, `byId` selects the last duplicate, whereas `workPeak` selects the first.

The page can hold this input: [project loading](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:12495) preserves duplicate peak IDs.

Reproduced with three held Gaussians, width 1, 401 points spanning 280–300, counts 10 and zero background:

- Root: ID 1, centre 285, amplitude 100.
- Child: ID 2, centre 280, amplitude 1, linked to 1, offset 2, ratio 0.5.
- Another child: ID 2, centre 281, amplitude 2, linked to 1, offset 3, ratio 0.25.

Both engines report success:

| Result | Main `8cc3750` | HEAD `39d04d6` |
|---|---:|---:|
| First ID-2 entry’s committed centre | 288 | 281 |
| Its committed amplitude | 25 | 2 |
| Stored χ² | 17316.589441709737 | 16420.830225973714 |

Duplicate-ID behavior was already defective; **silently dropping a propagation operation and changing the committed result is new**. Preserve the legacy pass for ambiguous IDs in this unit, leaving validation to its separate unit.

**Needs non-physical inputs:** an invalid model with duplicate IDs, yes; non-physical spectral or numerical values, no.

The remaining checks support the intended fix:

- **Ordering and idempotence:** 2,000 shuffled forests passed against an independent recursive oracle, including branching, missing parents and mixed numeric/string IDs. Reversed chains through 1,000 peaks passed. These guarantees require unique IDs and acyclic dependencies.
- **Round 1 regression:** self-links and two-peak cycles now match main exactly. Another 500 cycles with dependent trees retained the old propagation behavior. Their existing non-idempotence remains; this branch does not refuse them.
- **Consumers:** for valid graphs, I found no remaining half-propagated read in the Jacobian, certificate, support, record, Batch Fit or fallback.
- **Identity:** independently reproduced **121 successful fits, 121 exact comparisons, zero differences or skips**, matching the saved rows. Confirmed 57 linked tabs and no multi-level chains. `Object.is` fixes the signed-zero comparison weakness. The shared background implementation is unchanged, and manual backgrounds are absent from this corpus. This establishes corpus identity, not universal identity.
- **Tests:** all four additions pass. Restoring peak-order propagation now fails all three chain tests, including the four-level case. Restoring the extra final χ² evaluation fails the self-link test. Its redundancy for valid graphs is correctly distinguished from its observable effect on invalid ones.
- **Scope:** apart from the duplicate-ID regression, production changes are confined to link ordering.

Validation: **91 tests passed; one backend-parity test failed because the read-only sandbox has no writable temporary directory.** No files changed.

VERDICT: NO-GO.
