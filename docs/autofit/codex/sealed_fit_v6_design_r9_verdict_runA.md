# Sealed fit record v6 design — Codex gate round 9, run A (commit abbb7e3)

Reviewed HEAD `abbb7e3` against `c643c5f`, read-only. **One MAJOR remains: crash recovery can still reuse an observed trust generation.**

**MAJOR — readers can authenticate against a state before it becomes durable.**

The [writer protocol](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:947) holds its lock through file fsync, rename and directory fsync. But [readers explicitly take no lock](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:953). They can observe the replacement between rename and directory fsync. File fsync alone does not guarantee persistence of the directory entry. [fsync documentation](https://man7.org/linux/man-pages/man2/fsync.2.html).

This permits the following crash sequence:

1. Durable state is `(I,7,{A,B,C})`; C remains active.
2. An owner command removes A and renames `(I,8,{B,C})` into place.
3. Before directory fsync completes, a worker reads that state. The page successfully authenticates a B-signed seal and caches `(I,8)`.
4. The host crashes. Recovery loses the unflushed rename and returns to `(I,7,{A,B,C})`. The browser survives on another machine.
5. Another owner command removes B, durably publishing `(I,8,{A,C})`.
6. Export begins afterward. Its fresh generation fetch returns `(I,8)`, matching the cached authentication even though B is absent.

No concurrent writers, delayed browser replies, backup restoration or numerical inconsistency is necessary. The same sequence affects Auto-Fit’s O₁ anchor evidence.

The [cache contract](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1001) cannot distinguish these states. Durability of an **acknowledged mutation** is insufficient when readers can acknowledge authentication using an **uncommitted mutation**.

**Required:** prevent generations from escaping to readers before durable commit, including recovery after an interrupted writer; alternatively, make state identities non-reusable even for observed mutations subsequently lost during recovery. Merely adding the writer lock does not establish that invariant.

A read-only protocol model reproduced matching cached/export generations with B absent. This was a state-transition probe, not filesystem crash injection.

Earlier findings:

| Finding group | Revision-9 disposition |
|---|---|
| Round-8 concurrent read–modify–publish | **Resolved for concurrent writers.** Every mutation now rereads under one exclusive lock. |
| Round-6 generation uniqueness; round-5 cached revocation; round-4 key lifecycle | **Still partially unresolved**, through the crash sequence above. |
| Round-7 backup restoration | **Resolved:** restore creates a fresh incarnation. |
| Round-7 delayed browser observations | **Resolved for the reported sequence:** issuance ordering, increasing revisions and invalidated outstanding verification prevent rollback. |
| Revision-5 supersession regression | **Resolved:** superseded operations discard staged work without restoring or writing into the newer operation. |
| Other earlier BLOCKER/MAJOR findings | **Resolved at design level**, subject to the specified implementation gates below. |

For the original nine questions:

| Question | Assessment |
|---|---|
| **1. VERIFIED claims and hypotheses** | No additional substantive false VERIFIED claim found. Installed lmfit confirms reduced-χ²-before-floor ordering and a separate `best_fit` evaluation. SciPy confirms the stated trapezoid association. An extracted `_npPairwiseSum` matched NumPy 2.4.4 exactly on 28 arrays through 100,000 elements. |
| **2. Projection** | Snapshot/request reconstruction, expression precedence, complete graph validation and shared projection address the earlier locks, chains and frontend-shape counterexamples. Alternatives remain previews; adoption makes a new request. |
| **3. Cross-record bindings** | Inline arrays, complete ordered selection, original context, normalized arguments and seed checks address the earlier substitutions. The averaging prerequisite remains necessary. |
| **4. Verification and acceptance** | Component, envelope, residual, area and support checks are specified. Search evidence is explicitly authenticated rather than recomputed. Fresh fits require verification; offline UNCONFIRMED is coherent. Authentication remains affected by the finding above, for both O₂ and O₁. |
| **5. Statistics and areas** | Associations, weights, denominators, floors, null cases and support are specified. The size of changes from recomputing statistics remains a measurement requirement. Q5 includes the identified area consumers and Auto-Fit’s warning decision. |
| **6. Local O** | Dependency-ordered links and frozen finalization address the earlier inconsistent snapshots. The local arithmetic and nonreportable starting-point designation remain explicit. |
| **7. Provenance** | Correctly narrowed to attestation; it no longer claims that source hashes or version strings prove executed artifacts. |
| **8. Legacy and migration** | Separate retained provenance, parameter-only imports and simultaneous consumer migration address the earlier omissions. Recorded-but-unsealed fits remain coherently distinguished from sealed fits. |
| **9. Design rules** | No new magnitude tolerance or competing numerical field reader identified. |

I found no additional defect introduced specifically by Revision 5. The remaining defect concerns Revision 9’s publication/recovery protocol.

No files changed. No browser suite, filesystem crash test or 202-target census was run. Universal evaluator/background identity and the numerical effects of prerequisite changes remain implementation measurements.

**VERDICT: NO-GO.**
