# Sealed fit record v6 design — Codex gate round 5, run B (commit 30ee1bb)

Revision 5 is **not ready for approval**. Two MAJOR findings remain.

Reviewed HEAD `30ee1bb` against `c643c5f`. Read-only; no files changed.

1. **MAJOR — round-4 A4 is only partially resolved: revocation does not invalidate cached verification.**

   Complete-key publication and per-use worker reads resolve the partial-file and imported-key problems. But [V6.5’s key lifecycle](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:934) promises that revoked-key seals become UNCONFIRMED, while [the verification cache](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:973) retains an `ok` result against the immutable seal without a trust-generation check, expiry or refresh rule.

   Concrete sequence: verify a seal successfully; revoke its key; continue displaying or exporting that same seal using its cached result. Neither the seal nor its live bindings changed. No new verification request is required, so the worker’s per-use keyring read is never reached. The design still permits CURRENT where its revocation contract requires UNCONFIRMED.

   **Required:** specify how cached verification learns about changed trust and when revalidation is mandatory. Apply that policy to both Auto-Fit outputs, including E. Alternatively, explicitly define an “accepted as of verification” state and revise the revocation promise accordingly.

2. **MAJOR — the new supersession rollback rule contradicts operation ownership and today’s behavior.**

   [The new transaction paragraph](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:824) explicitly includes “superseded” among outcomes that restore the previous model, context and charge correction “exactly as today’s failure paths do.”

   Today does the opposite after supersession: it returns **without rollback**, specifically to avoid overwriting the newer fit. See [the result path](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8247) and [the exception path](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8292).

   If transaction A awaits its final fit and transaction B supersedes it and commits, applying the stated rollback for A can erase B’s result. This also conflicts with V6.5’s instruction to discard superseded replies.

   **Required:** supersession must discard A’s staged work without changing the newer owner’s model, context, seal, undo or history. Distinguish that from cancellation/failure while A still owns the operation. With nothing published before commit, abandoning staged state normally needs no live-state restoration.

   **This is a new defect in revision 5’s proposed resolution of round-4 A3/B3.**

The complete round-4 disposition is:

| Round-4 finding | Revision-5 result |
|---|---|
| A1 / B4: canonicalisation collisions, overflow and absent/null semantics | **Resolved at design level:** typed effective values, lossless identifier strings and rejection before fitting |
| A2 / B1: dangling links and indistinguishable frontend shapes | **Resolved at design level:** complete graph validation across producers and verification; `frontend_shape` bound through request reconstruction and attestation |
| B2: anchor evidence unbound to the spectrum or positive acceptance | **Resolved:** E belongs to the seal’s identity; R₁ binds to the same raw spectrum; O₁ requires verification, acceptance and gates; R₂ is derived |
| A3 / B3: two-fit transaction and terminal outcomes | **Partially resolved:** publication, acceptance, final-anchor failure and commit are specified; supersession remains contradictory |
| A4: key publication, rotation and revocation | **Partially resolved:** worker behavior is repaired; cached page verification remains unspecified |
| B’s minor heading issue | **Resolved** |

For the remaining original review questions:

- **Verified claims and statistics:** no additional false claim found in the inspected recording, projection, background, local-engine and provenance references. Installed lmfit confirms reduced-χ²-before-floor ordering and a separate `best_fit` evaluation; SciPy confirms the stated trapezoid association. A fresh extracted-function probe matched `_npPairwiseSum` against NumPy 2.4.4 on 24 arrays through 100,000 elements.
- **G1–G3:** request reconstruction, expression overrides, graph validation, sample/context/seed bindings and the independently checked anchor evidence close the earlier substitution cases. Acceptance evidence remains authenticated rather than numerically reconstructed. Universal evaluator/background bit stability remains appropriately unproved and gated.
- **G4–G6:** statistics formed from returned arrays remain a measured behavior change, with no unsupported size claim. Area consumers and Q5 are covered. Local O retains its engine arithmetic and starting-point designation. Provenance is explicitly an attestation, not proof of executed artifacts.
- **Legacy, migration and design rules:** the keyless rule, recorded-but-unsealed provenance retention and simultaneous consumer migration remain coherent. No new magnitude tolerance or competing numerical reading was identified.

Validation comprised source inspection and the bounded summation probe; no browser suite or 202-target census was run.

**VERDICT: NO-GO.**
