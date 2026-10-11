# Sealed fit record v6 design — Codex gate round 5, run A (commit 30ee1bb)

Reviewed HEAD `30ee1bb` against `c643c5f`; changes are documentation only. **Two MAJOR issues remain.** No files changed.

1. **MAJOR — revocation does not invalidate cached page verification. Round-4 A4 remains partially unresolved.**

   Complete-key publication and per-request worker refresh fix the server-side problems. But [V6.5:973](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:973) still caches successful verification by immutable seal identity, with history snapshots sharing that identity. No invalidation or freshness rule connects this cache to the keyring.

   Concrete sequence: verify a seal under key K; cache `ok`; revoke K; consume the same seal again. Its identity and live bindings remain unchanged, so the cached result can still authorize DISPLAY-CURRENT without reaching the server’s new keyring check. This contradicts [the promise that revoked seals read UNCONFIRMED](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:940).

   **Required:** specify the validity boundary of cached authentication, how the page discovers revocation, and when it must revalidate. Cached numerical consistency can survive; authorization by a revoked key cannot. Cover both O₂ and O₁’s keys for Auto-Fit.

2. **MAJOR — the new rollback rule explicitly includes supersession, contradicting operation ownership. Round-4 A3/B3 is not completely resolved.**

   [V6.3:829](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:829) requires rollback when superseded, restoring the previous model and context “exactly as today’s failure paths do.”

   Today deliberately does **no rollback on supersession**: [IH:8247](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8247) and [IH:8294](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8294) explain that restoration would overwrite the newer operation’s model.

   If Auto-Fit A is superseded by B, A’s terminal path must discard its private transaction. Restoring A’s original snapshot can overwrite B’s edits or result. Merely retaining one operation token does not resolve the contradictory instruction to restore after losing ownership.

   **Required:** distinguish owned failure/cancellation from supersession. Restore only while authorized to restore that tab; supersession discards private work without writing the old snapshot. Apply this to both fits and both verification replies.

The round-4 dispositions are:

| Round-4 finding | Revision-5 assessment |
|---|---|
| Dangling links, ambiguous IDs, cycles, frontend-shape ambiguity — A2/B1 | **Resolved at design level.** Whole-graph validation, `frontend_shape`, and request reconstruction cover the reported counterexamples. |
| Anchor evidence belongs to another spectrum or authenticates a failure — B2 | **Resolved.** Same-tab raw-data binding, positive acceptance, gates, and E’s inclusion in verification identity are explicit. |
| Two-fit derivation, intermediate publication, final-anchor failure — A3/B3 | **Substantially resolved**, except the supersession rule above. |
| Integer-ID collisions/overflow and absent-versus-null semantics — A1/B4 | **Resolved at design level.** Typed effective defaults and lossless string IDs remove the reported cases. |
| Partial key publication and imported worker keys — A4/B minor | **Server-side issues resolved; verification-cache lifecycle remains open.** |
| Stale revision heading | **Resolved.** |

For the remaining original review questions: I found no additional substantive false VERIFIED claim in the inspected code. The statistics associations, lmfit floor/denominator ordering, separate `best_fit` evaluation, and SciPy trapezoid arithmetic remain consistent. Twelve fresh extracted `_npPairwiseSum` probes matched NumPy exactly, through 100,000 elements; this does not establish universal identity. The canonicalization probe reproduced the old numeric-ID collision and confirmed that the proposed string encodings remain distinct.

Areas, local starting-point designation, narrowed provenance claims, legacy handling, and simultaneous consumer migration remain coherent. No new magnitude tolerance was introduced. Evaluator/background bit stability and numerical effects of 0b/0c/0d remain implementation measurements, not established results.

Validation was read-only source inspection and bounded probes; no full browser suite or 202-target census.

**VERDICT: NO-GO.**
