# Sealed fit record v6 design — Codex gate round 8, run B (commit 039bcbe)

Reviewed HEAD `039bcbe` against `c643c5f`, read-only. **One MAJOR remains in the trust protocol.** Changes are documentation only; no files changed.

**MAJOR — atomic state-file replacement does not establish generation uniqueness across concurrent updates.**

[V6.5’s state-file protocol](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:987) specifies an incremented revision and atomic rename, but no serialization or conditional publication of the read–modify–write transaction. Atomic rename prevents partial reads; it does not prevent competing writers publishing different states with the same generation.

Concrete counterexample:

1. State is `(I, 7)`, trusting A, B and C; C is active.
2. Two revocations read that state. One prepares removal of A; the other prepares removal of B. Both prepare revision 8.
3. The first publishes `(I, 8, {B,C})`. The page authenticates a B-signed seal and caches `(I, 8)`.
4. The second publishes `(I, 8, {A,C})`.
5. Export begins and fetches the generation afresh: `(I, 8)`. Cached B authentication still matches, although B is now absent.

An in-memory transition probe reproduced that outcome. Every reader receives a complete snapshot. **None of Revision 8’s browser-ordering rules detects it**, because the generation never changes. The same failure can preserve authentication of Auto-Fit’s anchor evidence O₁.

The design asserts non-reuse, but its specified publication mechanism does not establish that invariant. Require one serialized mutation protocol across creation, rotation, revocation and restore—such as a cross-process lock covering reread, modification, revision allocation and publication, or conditional replacement with retry. Define durable publication/recovery so a restart cannot roll the revision back. Also consolidate the [earlier separate-key/pointer instructions](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:939) with the authoritative state-file contract.

Earlier findings:

| Finding | Revision-8 disposition |
|---|---|
| Round-7 A: backup restoration reuses an incarnation | **Resolved specifically:** restore explicitly draws a fresh incarnation. |
| Round-7 B: delayed observations restore invalid authentication | **Resolved specifically:** fetch ordering, monotonic revisions and invalidation of outstanding verifications address that sequence. |
| Round-4 A4 / round-5 A1,B1 / round-6 trust-generation findings | **Still partially unresolved end to end**, because the server can publish an ambiguous generation as above. |
| Projection, locks, expressions, arbitrary-order chains and frontend representation | **Resolved at design level** by request reconstruction, expression precedence and complete graph validation. |
| Data/window/averaging/seed bindings, expired sessions and reconstruction inputs | **Resolved**, subject to the stated averaging prerequisite. |
| Auto-Fit evidence substitution, authenticated failures, final context and transaction ownership | **Resolved at design level.** Both outputs are checked, E is bound to the same spectrum, and supersession discards without writes. |
| Canonical collisions, absent/null semantics, statistics, support, areas and local finalization | **Resolved at design level.** |
| Provenance overclaim, legacy retention and consumer migration | **Resolved.** |

For the original review questions:

- **VERIFIED claims:** no additional substantive false claim found in the inspected references.
- **G1–G3:** the projection and numerical bindings close the earlier substitutions. Search evidence remains authenticated rather than recomputed; its remaining weakness is the trust-state finding above. Offline UNCONFIRMED is coherent.
- **G4:** installed lmfit confirms reduced-χ²-before-floor ordering and separate `best_fit` evaluation; SciPy confirms the trapezoid association. The extracted `_npPairwiseSum` matched NumPy 2.4.4 on **22 arrays through 100,000 elements**. Statistics-change magnitude and universal evaluator/background stability remain implementation measurements. Q5 covers the identified area consumers.
- **G5/G6:** local O’s frozen snapshot and starting-point designation are coherent. Provenance expressly stops short of identifying executed artifacts.
- **Legacy, migration and rules:** no additional missing consumer, magnitude tolerance or competing numerical reader identified.

Revision 5’s supersession regression is repaired; I found no additional Revision-5 defect. The remaining finding concerns the later state-file protocol. No browser suite or 202-target census was run.

**VERDICT: NO-GO.**
