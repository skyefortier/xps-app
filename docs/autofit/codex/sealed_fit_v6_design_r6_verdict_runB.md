# Sealed fit record v6 design — Codex gate round 6, run B (commit 7373644)

Reviewed HEAD `7373644` against `c643c5f`. Changes are documentation only; no files changed.

**One MAJOR remains: the new trust counter can repeat after keyring replacement, preserving invalid cached authentication.**

[V6.5’s cache contract](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:984) identifies trust by `attest_epoch`, a counter advanced on rotation and revocation. It does not bind that counter to a particular keyring or require a distinct generation after loss/recreation. Invalidation is described as occurring on a **newer** epoch.

A permitted counterexample:

1. The page authenticates a seal signed by K and caches success at epoch 0.
2. The keyring is lost and recreated with K′, with its counter again at 0. The browser remains open; software metadata is unchanged.
3. Export fetches `/api/attest-epoch` and receives 0.
4. The cached authentication still matches that epoch. No newer epoch triggers verification, so the seal can remain DISPLAY-CURRENT although this server cannot authenticate K.

This contradicts the explicit [lost-keyring → UNCONFIRMED promise](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:950). Independent trust domains can likewise have equal counters.

**Required:** identify the actual trust generation without reuse across keyring replacement or trust-domain changes—for example, a keyring identity plus a durable revision, with explicit recovery semantics, or an identity derived from the trusted key set. Cache validity must require that complete identity, and any mismatch must invalidate authentication. Apply it to both O₂ and O₁.

Ordinary revocation within one continuing counter sequence is now addressed. **Round-5 A1/B1 and the earlier key-lifecycle finding remain partially resolved because the replacement protocol leaves this case open.** This particular counter-reuse defect is new in Revision 6.

The other dispositions are:

| Earlier finding | Revision-6 assessment |
|---|---|
| Round-5 A2/B2: supersession restores an obsolete snapshot | **Resolved.** [The transaction rule](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:824) explicitly discards without writes or messages after ownership is lost, matching [today’s code](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8247). |
| Projection inputs, snapshot/request binding, expression overrides, linked-shape representability and invalid graphs | **Resolved at design level.** Complete snapshots, request reconstruction, expression precedence and graph validation cover the reported cases. |
| Auto-Fit context, rounding, sample reselection, anchor-evidence substitution and positive acceptance | **Resolved.** Each fit has its own context; E is independently bound and verified; the final transaction and anchor-failure outcome are specified. |
| Expired sessions, missing reconstruction settings, canonical collisions and absent/null semantics | **Resolved.** Explicit arrays, transport-only sessions, typed effective defaults and lossless IDs address the counterexamples. |
| Unauthenticated acceptance and incomplete signed payload | **Payload/signing resolved; trust lifecycle remains above.** |
| Statistics, component/envelope/residual identities, support, areas and local snapshot consistency | **Resolved at design level**, subject to the stated implementation measurements. |
| Execution-provenance overclaim, legacy provenance loss and consumer migration | **Resolved.** Claims are narrowed, provenance survives peaks-only restoration, and consumers switch together. |

For the original nine review questions:

- **VERIFIED claims:** I found no additional substantive false claim in the inspected recording, projection, background, statistics, local-engine or provenance references.
- **G1/G2:** the proposed bindings close the earlier model, data, window, averaging and seed substitutions. Alternatives remain previews; adoption captures a new request.
- **G3:** fresh fits receive verification; numerical consistency and authenticated search evidence are distinguished. Offline UNCONFIRMED is coherent. The trust finding above still affects acceptance.
- **G4:** installed lmfit confirms denominator, floor and AIC/BIC ordering; `best_fit` is a separate evaluation. SciPy confirms the stated trapezoid association. The statistics-change magnitude remains correctly unclaimed pending measurement; Q5 covers the identified area consumers.
- **G5/G6:** local frozen finalisation and starting-point designation remain coherent. Provenance expressly does not prove executed artifacts.
- **Legacy/migration/rules:** no additional missing consumer or conflicting policy found, and no new numerical tolerance or competing field reader identified.

A fresh extracted-function probe matched `_npPairwiseSum` against NumPy 2.4.4 exactly on 24 binary64 arrays through 100,000 elements. This does not establish universal evaluator/background stability. No browser suite or 202-target census was run. No additional Revision-5 defect was found beyond its supersession error, now repaired.

**VERDICT: NO-GO.**
