# Sealed fit record v6 design — Codex gate round 7, run A (commit 1447d14)

Reviewed HEAD `1447d14` against `c643c5f`. Documentation-only changes; read-only review.

**One MAJOR remains: round-6’s trust-generation finding is only partially resolved. Backup recovery permits generation reuse.**

[V6.5 assigns `{incarnation, revision}` to the keyring state](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:987), but [restoring a backup preserves its incarnation](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1001). Nothing prevents the restored revision sequence from repeating with different keys.

Concrete counterexample:

1. Back up incarnation **I**, revision **0**, containing keys **A and B**.
2. Revoke A: state becomes **(I, 1)**, containing B. The page successfully authenticates a B-signed seal and caches that generation.
3. Restore the backup, then revoke B: state becomes **(I, 1)** again, now containing A.
4. The page observes neither intermediate operation. Its next export fetch returns **(I, 1)**, matching its cached authentication. B is unavailable, yet the cache can still authorize DISPLAY-CURRENT.

An in-memory transition probe reproduced this equality with B absent. Atomic replacement and snapshot-bound replies do not prevent it: this sequence is entirely serial.

**Required:** make generations non-reusable across backup recovery too. For example, restore the backed-up keys under a **fresh incarnation**, allowing their seals to authenticate again while invalidating previous browser caches. Alternatively, define a revision authority that cannot roll back with the backup.

This leaves **round-6 A1/B1**, and consequently the earlier cached-authentication/key-lifecycle finding, open. Fresh-keyring replacement and verification-response snapshot binding are resolved.

All other earlier BLOCKER/MAJOR findings are resolved **at design level**:

| Finding group | Assessment |
|---|---|
| Projection, locks, expressions, arbitrary-order chains, frontend representation | Complete snapshots, request reconstruction, expression precedence and graph validation address the reported cases. |
| Data/window/averaging/seed/model substitutions; expired sessions | Explicit bindings, inline arrays, shared normalization and the averaging prerequisite address them. |
| Auto-Fit anchor evidence, final context and transaction | Both fits are bound and accepted; final-frame refitting and staged publication are specified. |
| Revision-5 supersession regression | Resolved: superseded work is discarded without restoring or writing into the newer operation’s state. |
| Signed payload, identifier collisions, absent/null semantics | Typed effective values and lossless identifiers address the counterexamples. |
| Statistics, support, areas and local output | Explicit associations, shared computations and frozen local finalization address them. |
| Provenance overclaim, legacy retention and consumer migration | Narrowed attestation claims, separate retained provenance and simultaneous consumer migration remain coherent. |

For the original numerical and code questions, I found no additional substantive false VERIFIED claim in the inspected references. Installed lmfit confirms reduced-χ²-before-floor ordering and a separate `best_fit` evaluation; SciPy confirms the stated trapezoid association. Fresh extracted `_npPairwiseSum` probes matched NumPy 2.4.4 exactly on **28 arrays through 100,000 elements**. This does not establish universal evaluator/background stability.

Offline UNCONFIRMED, authenticated search evidence, local starting-point designation, area consumers and legacy policy remain coherent. No additional Revision-5 defect, new magnitude tolerance or competing numerical field reader was identified. The recovery defect above is in Revision 7’s resolution.

No browser suite or 202-target census was run; those implementation measurements remain pending.

**VERDICT: NO-GO.**
