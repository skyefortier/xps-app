# Sealed fit record v6 design — Codex gate round 8, run A (commit 039bcbe)

**One MAJOR remains: concurrent trust updates can reuse a generation for different key sets.**

Reviewed HEAD `039bcbe` against `c643c5f`, read-only. Changes are documentation only.

**MAJOR — atomic state-file replacement does not serialize trust mutations.**

[V6.5:987](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:987) specifies a revision counter and atomic rename. It specifies neither an enforced single writer nor an interprocess transaction covering read, modification and publication. Atomic rename prevents partial reads; it does not prevent two writers publishing successors calculated from the same revision.

Concrete sequence, with C remaining the active signing key:

1. State is `{I, 7, keys:[A,B,C]}`. Two revocation operations read it.
2. The first removes A and publishes `{I, 8, keys:[B,C]}`.
3. The page successfully authenticates a B-signed seal and caches `{I,8}`.
4. The second removes B from its previously read snapshot and publishes `{I, 8, keys:[A,C]}`.
5. Export begins afterward and fetches the actual current generation: `{I,8}`. It matches the cached authentication although B is unavailable.

Every read sees a complete snapshot. No delayed browser response, backup restoration, software change or numerical inconsistency is needed. Revision 8’s page ordering rules cannot distinguish these two states. This contradicts [the cache-validity and next-export promises](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:993). The same failure applies when B authenticated Auto-Fit’s O₁ anchor evidence.

An in-memory transition probe reproduced the generation equality with the cached key absent.

**Required:** enforce a single updater, or serialize the complete read–modify–publish transaction across processes. Rotation, revocation, creation and restoration must participate in that protocol. A stale writer must retry against the committed state rather than overwrite it—including after a restore installs a fresh incarnation. Specify durable publication and recovery so an acknowledged generation cannot subsequently be reused.

The earlier findings stand as follows:

| Finding | Revision-8 disposition |
|---|---|
| Round-7 A: backup restoration repeats an incarnation | **Resolved for that sequence:** restoration explicitly creates a fresh incarnation. |
| Round-7 B: delayed observations roll back browser trust | **Resolved for that sequence:** issuance ordering, monotonic revisions and invalidated outstanding verifications address it. |
| Round-6 generation non-reuse; round-5 A1/B1 cached revocation; round-4 A4 key lifecycle | **Still partially resolved:** concurrent publication leaves the case above open. |
| Revision-5 supersession rollback | **Resolved:** superseded work is discarded without restoring or writing into the newer owner’s state. |
| All other earlier BLOCKER/MAJOR findings | **Resolved at design level**, subject to the stated implementation gates. |

I found no additional defect attributable specifically to Revision 5. This finding concerns the state-file generation mechanism introduced in Revision 7 and retained in Revision 8.

For the original nine questions:

| Question | Assessment |
|---|---|
| 1. VERIFIED claims and hypotheses | No additional false VERIFIED claim found in the inspected references. Installed lmfit confirms reduced-χ²-before-floor ordering and separate `best_fit` evaluation; SciPy confirms the trapezoid association. Extracted `_npPairwiseSum` matched NumPy 2.4.4 exactly on 26 binary64 arrays through 100,000 elements. |
| 2. Projection | Snapshot/request binding, expression precedence, complete graph validation and shared projection address the earlier lock, chain and representation cases. Alternatives remain previews; adoption captures a new request. |
| 3. Cross-record bindings | Explicit arrays, complete ordered selection, context, normalized settings and seed checks address the reported substitutions. The averaging prerequisite remains necessary. |
| 4. Verification and acceptance | Numerical recomputation and authenticated search evidence are appropriately distinguished. Fresh fits require verification; offline UNCONFIRMED is coherent. Authentication remains affected by the finding above, for both O₂ and O₁. |
| 5. Statistics and areas | Associations, denominators, floors, null cases, support and area consumers are specified. Statistics-change magnitude remains a measurement requirement, correctly without an advance size claim. |
| 6. Local O | Frozen finalization and dependency-ordered links address snapshot consistency; the nonreportable starting-point designation is retained. |
| 7. Provenance | Correctly narrowed to attestation, without claiming proof of executed artifacts. |
| 8. Legacy and migration | Separate retained provenance, parameter-only imports and simultaneous consumer migration remain coherent. |
| 9. Design rules | No new magnitude tolerance or competing numerical field reader identified. |

No browser suite or 202-target census was run. Universal evaluator/background identity and the numerical effects of prerequisite changes remain implementation measurements.

**VERDICT: NO-GO.**
