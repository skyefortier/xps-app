# Sealed fit record v6 design — Codex gate round 3, run B (commit 8a4ddc5)

**Revision 3 is not ready for approval.** One display-consistency blocker remains, Auto-Fit’s context binding still contains the round-2 contradiction, and the new attestation protocol needs a concrete persistence and canonicalisation contract.

Reviewed HEAD `8a4ddc5` against `c643c5f`; differences are documentation only. Source inspection and bounded Python/JavaScript probes were read-only.

1. **BLOCKER — expression-value assignment still cannot represent every linked model.**

   [V6.3 step 1](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:757) retains the frontend shape and application rules while asserting that expression-valued fields now represent O.

   A **Voigt child linked to a GL parent** defeats that assertion:

   - The page builder sends the child’s fixed `gl_ratio: 0.5`.
   - The server replaces it with the parent’s expression-valued mix.
   - The page continues to define Voigt as **0.5**, regardless of its `glMix` field.

   My bounded production-function probe returned:

   | Quantity | Result |
   |---|---:|
   | Server success | `true` |
   | Certificate certified | `true` |
   | Child’s returned `gl_ratio` | `0.2` |
   | Child expression | `p1_gl_ratio` |
   | Maximum difference from its page-defined Voigt curve | `1.9395360519900833` |

   This requires no forged O. Snapshot→request equality, server recomputation and a producer HMAC can all pass while the displayed shape describes another model.

   Evidence: [Voigt request mapping](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6929), [server expression override](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1570), [application shape guard](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7005), [Voigt evaluator](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:4184). Mixed families are not excluded by the proposed seal; the UI’s shape-switch propagation also covers only the immediate family, [IH:5848](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5848).

   **Required:** define and validate representable linked-shape combinations. Either reject incompatible families before fitting, or explicitly project them into a frontend shape that represents O. Assigning an expression value to an inactive field is insufficient.

   **Round-2 snapshot/display blocker: partially resolved, still open.**

2. **MAJOR — Auto-Fit’s final context is still compared with the original request.**

   `R.context0` and the revised charge arithmetic address much of round 2. But [V6.4’s context binding](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:811) still requires **D’s context**, including its anchors, to reproduce `R.request.background`.

   With a nonzero final charge adjustment, the original manual anchor `280.5` becomes, for example, `280.49`. The request still contains `280.5`. This fails even when the selected sample indices remain unchanged. Round-2 run B identified precisely this contradiction.

   The revised VERIFIED finalisation description also omits an operative branch: endpoint fields are rounded only when `delta !== 0`. Unconditionally applying its stated `toFixed(1)` sequence changes an endpoint such as `280.04` even when the live path leaves it untouched. See [IH:5465](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5465).

   **Required:** compare the request with **`R.context0`**; compare live context with the independently derived **final context**. Preserve the zero-delta branch. Specify separately which final-background comparison determines currency.

   **Round-2 Auto-Fit context finding: still open.** The anchor-support arithmetic itself is now correctly distinguished from backend component support.

3. **MAJOR — HMAC is a suitable mechanism, but the signed object and key lifecycle are not yet specified sufficiently.**

   [V6.5 step 3](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:858) supplies a formula, but neither `canonical` nor “normalised R” has a defined schema or byte representation.

   Two materially different contracts remain possible:

   - Sign the normalized numerical arguments and O.
   - Sign those arguments **plus** the page snapshot, producer, original context, indices and other R fields.

   The current fit request delivers no such complete page envelope to the server. The design must specify how the producer obtains everything it promises to authenticate, and bind it to the arguments actually executed.

   Canonicalisation also needs explicit rules for field inclusion, ordering, defaults, missing versus null, numbers and serialization round trips. Ordinary Python sorted JSON is insufficient by itself: an original `285.0` can return through browser JSON as `285`, and negative zero has another round-trip issue. Signing and verification must use one versioned representation.

   “Created at first start, outside the repository” leaves important operational choices unresolved:

   - Cryptographically random key generation and persistent, permission-restricted storage.
   - Atomic creation and the same key across all workers and restarts.
   - Key identification, rotation and revocation behavior.
   - Whether the macOS deployment and xps2 droplet deliberately share a trust domain.

   Q9 already permits another server or a lost/rotated key to yield UNCONFIRMED. That is coherent; the deployment contract must make those outcomes deliberate rather than worker-dependent.

   **Security conclusions:** with complete canonical binding and an uncompromised key, attaching an attested O to a *different normalized fit request* fails authentication. Equivalent normalized requests can legitimately share the attestation. A leaked key lets its holder forge acceptance, uncertainties, alternatives and producer identity. Numerical recomputation can still reject inconsistent arrays, but cannot expose a consistently fabricated nonminimum carrying a forged certificate.

   HMAC therefore does **not** replace the numerical checks under the stated contract: authentication establishes attribution; recomputation establishes consistency under the verifier. Neither resolves finding 1. A valid MAC must also accompany the positive acceptance predicates—it does not make an authenticated failure successful.

   **Round-2 acceptance blocker: addressed conceptually, not yet closed by a reviewable protocol.**

4. **MAJOR — literal reuse of the existing request normalizer prevents verification after upload expiry.**

   [V6.2](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:712) requires the wire request to pass through `_prepare_fit_request`. That function first loads `session_id` from server storage and returns 404 if absent, [app.py:70](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/app.py:70). Uploads have a seven-day expiry policy, [app.py:56](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/app.py:56).

   Inline R arrays solve data preservation, but do not make this existing function independent of the original upload.

   **Required:** extract shared normalization that accepts explicitly supplied arrays. Both fitting and verification should call it, with fitting separately resolving the upload. Define `session_id` as transport metadata and specify its treatment in step 0 and the signed representation.

   This also settles how “rebuild the wire request exactly” works without inventing a new upload identifier during verification.

The remaining round-2 dispositions are:

| Finding | Revision-3 disposition |
|---|---|
| Locked child values contradict expressions | Ordinary mapped fields fixed in principle; linked-shape exception remains above |
| Local retained χ² describes another snapshot | Resolved at design level by dependency-ordered evaluation and frozen finalisation |
| Verification owned only by O | Resolved by whole-seal ownership and operation guards |
| Verifier claims “same executed code” | Resolved by the narrower verifier-consistency claim |
| Incomplete background assembly | Resolved by the proposed shared whole assembly |
| NaN versus nonfinite shift reader | Corrected |
| Rendered digest includes itself | Resolved by hashing render inputs |

Other requested checks:

- **Step 0 is implementable after the normalization clarification.** Capture actual `startPeaks` for Use this solution and the complete Auto-Fit peak objects. A `_STARTS_MODEL_FIELDS`-only whitelist would omit `_afCenterMin/Max` and `_afFwhmMin/Max`, which the [Auto-Fit overlays read](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8213). Preserve the captured method and producer-specific settings explicitly.
- **0b and 0c are correctly separated as numerical/display changes.** 0b can change optimization trajectories and acceptance, not merely the final reported χ². 0c changes displayed linked values and subsequent starting models. Also account for `_altPeaks`, which currently passes value-only parameter objects without `expr`, [IH:8784](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8784).
- **The corrected statistics contract checks out.** Installed lmfit confirms denominator, floor and AIC/BIC ordering; `best_fit` is a separate evaluation. Installed SciPy confirms signed trapezoid terms followed by summation and final absolute value. Extracted `_npPairwiseSum` matched NumPy on bounded probes through 100,000 elements. These checks do not establish universal evaluator bit stability.
- **Areas, legacy handling and migration remain coherent.** Q5 correctly follows measurement; recorded-but-unsealed provenance survives peaks-only restoration; local results retain their starting-point designation.
- **No new numerical verification tolerance is introduced.** Existing replay tolerances remain separate. Auto-Fit’s existing reference-centre gate still contains `0.30 + 1e-6`; it is an acceptance gate, not an exact identity check. The competing readings that remain are the linked Voigt semantics and original-versus-final context above.

No full browser suite or 202-target census was run. No files changed.

**VERDICT: NO-GO.**
