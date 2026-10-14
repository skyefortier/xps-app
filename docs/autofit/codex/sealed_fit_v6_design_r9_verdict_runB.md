# Sealed fit record v6 design — Codex gate round 9, run B (commit abbb7e3)

**One MAJOR remains: a reader can expose a generation before it is durable, allowing generation reuse after a crash.**

Reviewed HEAD `abbb7e3` against `c643c5f`. Changes are documentation only. No files changed.

**MAJOR — writer serialization does not establish durable publication to readers.**

The [writer protocol](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:947) performs rename, then directory fsync. But [readers explicitly take no lock](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:953), so verification and generation requests can return the renamed state before that fsync completes. Fsyncing the temporary file does not establish durability of the directory entry. [fsync documentation](https://man7.org/linux/man-pages/man2/fsync.2.html)

A permitted sequence, with C remaining the active signing key:

1. Durable state is `(I,7,{A,B,C})`.
2. An owner command revokes A under the exclusive lock. It fsyncs the temporary file and renames `(I,8,{B,C})` over `state.json`, then pauses before directory fsync.
3. The page fetches generation `(I,8)` and successfully verifies a B-signed seal against that snapshot. It caches the authentication.
4. The server suffers a machine crash before directory fsync. Recovery retains the previous durable state `(I,7,{A,B,C})`. The browser remains open.
5. The owner revokes B. The command correctly re-reads under the lock and durably publishes `(I,8,{A,C})`.
6. Export begins afterward and fetches `(I,8)`. That matches the cached authentication, although B is now absent.

Every writer follows Revision 9. Every verification reports its actual snapshot. Every browser ordering rule holds. Nevertheless, the [generation-equality rule](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:999) admits false CURRENT. The same sequence works when B authenticated Auto-Fit’s anchor O₁.

An in-memory transition probe confirmed the generation collision. This models an allowed recovery outcome; it is not a physical crash test.

**Required:** establish durable visibility for every generation returned to a client, including recovery after writer death or fsync failure. Protecting only the owner command’s acknowledgement is insufficient. Either prevent readers from exposing uncommitted snapshots, with explicit recovery handling, or use state identities that cannot collide after rollback.

The earlier findings stand as follows:

| Finding | Revision-9 disposition |
|---|---|
| Round-8 concurrent writers allocate the same revision | **Resolved specifically:** the complete transaction is serialized. |
| Round-7 backup restoration and delayed browser observations | **Resolved specifically:** fresh restore incarnation and browser ordering address those sequences. |
| Round-4 key lifecycle, round-5 cached revocation, round-6 generation non-reuse | **Still partially unresolved end to end:** the crash sequence above remains. |
| Revision-5 supersession rollback regression | **Resolved:** superseded work is discarded without writes. |
| Other earlier BLOCKER/MAJOR findings | **Resolved at design level**, subject to the stated implementation gates. |

For the original nine questions:

| Question | Assessment |
|---|---|
| 1. VERIFIED claims | No additional substantive false VERIFIED claim found in the inspected references. Installed lmfit confirms reduced-χ²-before-floor ordering and separate `best_fit` evaluation; SciPy confirms the stated trapezoid association. |
| 2. Projection | Complete snapshots, request reconstruction, expression precedence, graph validation and shared projection address locks, chains and frontend representation. Alternative adoption captures a new request. |
| 3. Cross-record bindings | Ordered sample completeness, explicit context, normalized settings and seed checks close the earlier substitutions. The averaging prerequisite remains necessary. |
| 4. Verification and acceptance | Numerical consistency and authenticated search evidence are properly distinguished. Fresh fits require verification; offline UNCONFIRMED is coherent. Authentication remains affected by the finding above, including E. |
| 5. Statistics and areas | Associations, denominators, floors, nullable fields, support and area consumers are covered. Statistics-change magnitude remains an implementation measurement, without an unsupported advance claim. |
| 6. Local O | Dependency-ordered links and frozen finalization address snapshot consistency. The nonreportable starting-point designation remains explicit. |
| 7. Provenance | Appropriately narrowed to attestation; it does not claim identification of executed artifacts. |
| 8. Legacy and migration | Keyless policy, retained recorded-but-unsealed provenance, parameter-only imports and simultaneous consumer migration remain coherent. |
| 9. Design rules | No additional magnitude tolerance or competing numerical reader identified. |

Fresh extracted `_npPairwiseSum` probes matched NumPy 2.4.4 exactly on **28 arrays through 100,000 elements**. Universal evaluator/background stability, replay rates and prerequisite numerical effects remain unmeasured here. No full browser suite or 202-target census was run.

I found no additional defect attributable specifically to Revision 5. The remaining defect concerns Revision 9’s durable-publication protocol.

**VERDICT: NO-GO.**
