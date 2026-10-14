# Sealed fit record v6 design — Codex gate round 4, run A (commit 2e44780)

Revision 4 is **not ready for approval**. Reviewed HEAD `2e44780` against `c643c5f`; the changes are documentation only. No files changed.

1. **BLOCKER — the signed representation conflates requests with different acceptance evidence.**

   [V6.5’s signed-payload contract](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:885) adopts `_canonical`, which converts every integer to a float. The normalizer accepts unrestricted integer `require_component` values ([app.py:124](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/app.py:124)), but the fitter resolves those identifiers using their exact decimal strings ([fitting.py:2706](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:2706)).

   A bounded production-function probe used two components with string IDs `"9007199254740992"` and `"9007199254740993"`:

   | Integer `require_component` | Success | Required verdict | F |
   |---|---|---|---:|
   | `9007199254740992` | true | true | 50738.1614 |
   | `9007199254740993` | true | false | 0 |

   **Both requests produce identical canonical A bytes. All output except `required` was identical.** Consequently, retaining the first O and its MAC while substituting the second request passes the proposed authentication binding. Numerical recomputation does not repair this: `required` is expressly authenticated, not recomputed.

   Auto-Fit normally sends string IDs; this counterexample concerns the broader domain accepted by the specified normalizer. It directly contradicts the claim that an attested O cannot accompany a different normalized request.

   The ordinary cases passed a bounded Python→JavaScript JSON→Python probe: booleans, strings, nested specs, nullable values, NumPy scalars, bounded `n_perturb`, integral floats and negative zero. The defect is **semantic collisions**, not ordinary JSON spelling.

   **Required:** define typed normalization before signing. Preserve identifiers losslessly as strings, or reject integers outside the supported exact range. Also resolve “absent fields become null”: `_canonical` itself distinguishes absence from null, and nested defaults can distinguish them operationally—for example, missing linked `fix_fwhm` defaults to true, whereas explicit null is false in [fitting.py:1567](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1567). Use field-specific effective defaults, not blanket null insertion.

   **Round-3 attestation finding: still open.**

2. **MAJOR — the proposed server refusal cannot distinguish the frontend shapes that caused round 3’s blocker.**

   [V6.3](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:773) requires page and server to refuse links across frontend lineshapes. But both **Voigt and GL become `pseudo_voigt_gl`** in the request. A Voigt and a GL held at 50% can send identical specs ([templates/index.html:6929](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6929)). The server does not receive `R.pageModel`.

   Comparing backend shape names therefore still accepts the original GL-parent/Voigt-child case. The design needs either validated frontend representation metadata or a precisely defined backend representability predicate. That predicate must also participate in loaded-seal validation.

   For genuinely matching frontend shapes, I found no additional missing active parameter mapping: DS, DS+G, LA and asymmetric GL have corresponding fields; Voigt→Voigt inherits the root’s fixed 0.5; valid same-shape chains preserve this property.

   Graph validity still needs an explicit rule. Removing a root deletes only its immediate children ([templates/index.html:6400](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6400)), leaving possible orphaned descendants. The builder silently omits the constraint when the parent is missing ([templates/index.html:6983](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6983)). “Different from its parent” does not define that case. The local `LINK_SYNC_KEYS` covers numeric shape parameters but excludes `shape`; dependency ordering alone does not validate the graph.

   **Required:** specify missing-parent/cycle handling and enforce the representation rule at all relevant producer and verification entry points, including local/Batch paths.

   **Round-3 representability blocker: policy addressed, enforcement contract incomplete.**

3. **MAJOR — the two-fit Auto-Fit proposal fixes the context contradiction but leaves its transaction and acceptance contract incomplete.**

   The correction is sound: seal `(R₂, O₂)` in its own frame, preserve `(R₁, O₁)` as anchor evidence, and compare each background against its own context. The `delta !== 0` endpoint-rounding branch is now correctly stated.

   However, [the new two-fit contract](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:795) does not settle:

   - What the student sees between fits, and whether the shifted model is provisional, saved, or exportable.
   - Whether O₁ must pass the complete acceptance/verification predicates before its shift is used. “Attested” alone includes authenticated failures.
   - The complete deterministic R₁/O₁→R₂ recipe, including the second request’s producer settings and treatment of overlays.
   - What happens if O₂ fails, is cancelled, becomes unverifiable, or no longer supports/requires the anchor after sample reselection and refitting.
   - How both requests retain operation ownership across the intentional context change.

   These are consequential choices. The current path performs finalisation, displays “Auto-fit complete,” snapshots, and syncs the tab ([templates/index.html:7837](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7837)); its failure paths restore the prior snapshot. Reusing that finalisation between requests would prematurely publish completion. Reusing the first request’s context guard would reject the intentional shift.

   **Required:** specify one two-fit transaction, its provisional display, complete anchor acceptance predicate, exact second-request derivation, and commit/rollback policy. Explicitly decide whether final anchor failure rejects Auto-Fit or whether the retained first fit independently justifies calibration.

   The stated fallback without 0d is coherent: nonzero shift cannot be current; zero shift permits the derived lock-only step.

   **Round-3 original/final-context finding: resolved. New two-fit contract: incomplete.**

4. **MAJOR — key provisioning and revocation still do not establish the promised worker behavior.**

   [V6.5’s lifecycle](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:897) uses `O_CREAT | O_EXCL` and loads the active key at import.

   Exclusive creation prevents competing creators; it does not prevent another worker reading the file before its 32 bytes are fully written. Likewise, moving the active pointer does not update existing workers’ imported signing keys. Deleting a revoked key does not erase their in-memory copies.

   **Required:** specify complete-key publication/readiness and worker reload or refresh behavior for rotation and revocation, including verifier caches. The signer restriction, protected storage, separate droplet trust domain and leaked-key threat statement are otherwise materially improved.

The remaining round-3 dispositions are:

| Finding | Revision-4 result |
|---|---|
| Expiring-session normalizer; missing method/settings/full peak snapshot | **Resolved at design level** |
| Original/final background context and zero-delta branch | **Resolved**, subject to completing the new two-fit workflow |
| Linked representation | **Incomplete**, finding 2 |
| Attestation contract | **Still open**, findings 1 and 4 |
| Overbroad tolerance statement | **Resolved** |

The statistics contract remains consistent with the inspected lmfit floor/denominator ordering, separate `best_fit` evaluation, and SciPy trapezoid arithmetic. No new verification tolerance was introduced. Universal evaluator/background bit stability remains an implementation measurement, not an established proof. Areas, legacy provenance retention and simultaneous consumer migration remain coherent.

**0b, 0c and 0d are correctly identified as behavior changes:** 0b can change optimization and acceptance; 0c changes displayed/subsequent starting values and refuses previously runnable models; 0d changes fitted numbers and can introduce new failures. Its impact includes degrees of freedom when centres are locked for the second fit.

Validation was read-only source inspection and bounded Python/JavaScript probes; no full browser suite or 202-target census.

**VERDICT: NO-GO.**
