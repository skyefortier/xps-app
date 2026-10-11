# Sealed fit record v6 design — Codex gate round 6, run A (commit 7373644)

Reviewed HEAD `7373644` against `c643c5f`. Changes are documentation only. **One MAJOR remains: the trust-generation contract is incomplete.** No files changed.

1. **MAJOR — round-5’s cached-authentication finding is only partially resolved.**

   [V6.5:984–993](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:984) adds refresh boundaries and an epoch check, but a counter alone does not identify the trust state.

   **Counterexample: keyring replacement.** A page caches successful authentication under key K at epoch 0. The keyring is lost and recreated with another key, also at its initial epoch. On export, the epoch fetch succeeds with the same counter. The specified rule does not invalidate the cached success, although K is unavailable. This contradicts [the explicit lost-keyring → UNCONFIRMED rule](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:950). No non-reuse or keyring-incarnation rule excludes this sequence.

   **There is also an unspecified concurrency boundary.** Verification can authenticate using K, then revocation can advance the counter before the response receives its `attest_epoch`. Attaching the latest epoch would incorrectly label an old authentication as valid under the new trust state. Per-request key reads and “every response carries an epoch” do not establish atomicity.

   **Required:** bind authentication to an immutable keyring snapshot and its non-reusable identity—for example, `{keyring_incarnation, epoch}`. Publish trust changes consistently across workers; return the generation actually checked; prevent delayed replies from restoring invalidated authentication. Keyring loss/replacement must change that identity. Apply this to both O₂ and O₁.

The other findings are resolved **at design level**:

| Earlier finding | Revision-6 disposition |
|---|---|
| Round-5 supersession rollback; round-4 two-fit ownership | **Resolved.** [V6.3:824–837](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:824) explicitly discards superseded work without writes, including both verification replies. |
| Snapshot/request binding; locks, expressions, chains and frontend representation | **Resolved.** Shared projection, request reconstruction and complete graph validation cover the reported counterexamples. |
| Anchor evidence from another spectrum, authenticated failures, original/final contexts | **Resolved.** E is bound to the same raw spectrum, positively accepted and verified; R₂ is derived and independently fitted. |
| Expired sessions and missing reconstruction inputs | **Resolved.** Explicit arrays, transport-only sessions and complete producer snapshots/settings. |
| Canonicalisation collisions and absent/null semantics | **Resolved.** Typed effective values and lossless identifier encoding. |
| Statistics, support, areas and local snapshot consistency | **Resolved.** Exact associations, shared computations and explicit prerequisite fixes. |
| Execution-provenance overclaim, legacy retention and mixed consumers | **Resolved.** Narrowed provenance claim, separate legacy provenance and simultaneous accessor migration. |

Revision 5’s supersession regression is therefore closed. I found no other unresolved earlier BLOCKER/MAJOR or additional revision-5 defect.

For the original numerical questions, inspected source confirms lmfit’s reduced-χ²-before-floor ordering, separate `best_fit` evaluation, and SciPy’s stated trapezoid association. A fresh extracted `_npPairwiseSum` probe matched NumPy 2.4.4 on **20 arrays through 100,000 elements**. No additional false VERIFIED claim or new magnitude tolerance was found in the inspected references.

Universal evaluator/background identity, replay rates and numerical effects of 0b/0c/0d remain implementation measurements. No browser suite or 202-target census was run.

**VERDICT: NO-GO.**
