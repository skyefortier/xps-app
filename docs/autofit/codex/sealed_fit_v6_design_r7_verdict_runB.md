# Sealed fit record v6 design — Codex gate round 7, run B (commit 1447d14)

Reviewed HEAD `1447d14` against `c643c5f`, read-only. **One MAJOR remains in the authentication-cache protocol.**

**MAJOR — delayed generation observations can allow an invalidated authentication to return.** This leaves round-6 A’s delayed-reply requirement, and round-5 A1/B1’s cache-revocation finding, partially unresolved.

[The revised contract](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:987) fixes keyring replacement and correctly binds verification to one immutable server snapshot. But [the page learns its generation from every reply](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:995), without defining ordering for those observations. Only verification replies receive an explicit mismatch rejection rule.

A permitted sequence, with the same tab, seal and operation owner throughout:

1. A generation request and verification V both read `{I, 7}`; their replies are delayed.
2. Key K is revoked, advancing the server to `{I, 8}`.
3. Save’s fresh generation request returns `{I, 8}`. The page invalidates authentication.
4. The older generation request returns `{I, 7}`. Learning from that reply can reset the page’s observed generation.
5. V returns successful authentication under `{I, 7}`. It now matches the latest observation and can attach, allowing CURRENT despite K’s revocation.

“Any difference drops cached authentication” does not prevent a subsequently arriving result from restoring it. Atomic server snapshots prevent inconsistent reads; they do not order browser responses.

**Required:** define “latest” operationally. Older revisions must never replace newer observations within an incarnation. Incarnation changes need an authoritative refresh boundary that delayed replies cannot reverse. Invalidate outstanding authentication attempts when that boundary changes, and require save/export to use its completed refresh. Apply this to both O₂ and O₁.

The remaining dispositions are:

| Review area | Revision-7 assessment |
|---|---|
| Round-6 counter reuse and snapshot/response mismatch | **Resolved.** Incarnation plus revision identifies the state; verification reports the snapshot actually checked. |
| Projection, locks, expressions, chains and frontend shapes | **Resolved at design level.** Request reconstruction, expression precedence and complete graph validation cover the earlier cases. |
| Data/window/averaging/seed bindings and expired sessions | **Resolved**, with the explicitly required averaging prerequisite and shared normalization over inline arrays. |
| Auto-Fit evidence, derivation and transaction ownership | **Resolved.** Both fits have their own context; anchor evidence is bound and positively accepted. Supersession discards without restoring obsolete state. |
| Signed payload, identifier collisions and absent/null semantics | **Resolved.** Typed effective values and lossless identifiers address the reported substitutions. Trust-cache ordering remains above. |
| Statistics, support, areas and local output | **Resolved at design level.** Exact arithmetic associations, shared verification and frozen local finalization are specified. |
| Provenance, legacy and migration | **Resolved.** Execution-proof claims are withdrawn; historical provenance survives peaks-only restoration; consumers migrate together. |

For the original numerical questions, inspected lmfit source confirms reduced-χ²-before-floor ordering and the separate `best_fit` evaluation. SciPy confirms the stated trapezoid association. A fresh extracted `_npPairwiseSum` probe matched NumPy 2.4.4 exactly on **24 arrays through 100,000 elements**. No additional false VERIFIED claim or new magnitude tolerance was found in the inspected references.

Revision 5’s supersession regression is repaired; I found no additional revision-5 defect. Universal evaluator/background identity, replay rates, and numerical effects of the prerequisite changes remain implementation measurements. No browser suite or 202-target census was run. No files changed.

**VERDICT: NO-GO.**
