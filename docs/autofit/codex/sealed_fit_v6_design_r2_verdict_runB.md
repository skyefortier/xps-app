# Sealed fit record v6 design — Codex gate round 2, run B (commit be59530)

**NO-GO.** Revision 2 resolves several round-1 blockers, but still permits false DISPLAY-CURRENT results.

Reviewed design HEAD `be59530983451b8a9761f0cfdefc611e4c499e9f` against `c643c5f`; their differences are documentation only. Read-only source inspection and bounded Python/extracted-JavaScript probes completed. No files changed.

Below, D denotes the [design memo](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:705).

1. **BLOCKER — the new frontend snapshot is not bound to the request, and reproducing application rules still permits incorrect displayed parameters.**

   D:743–750 projects from `R.pageModel`, while D:803–810 verifies parameters against `R.request`. No stated check connects those two descriptions.

   Concrete false-CURRENT construction:

   - Keep a valid R/O whose requested and returned **locked amplitude is 100**.
   - Change the saved `R.pageModel` amplitude to **500**, retaining its lock.
   - Set the live model to that projection.

   The server verifies the original request and output. Projection preserves 500. The live comparison passes. Results reports 500 while O’s verified component describes amplitude 100.

   There is also a failure with an authentic request: linked expressions override frontend locks on the server, but `_applyBackendParams` still preserves the locked snapshot values. A successful Python probe returned linked child center **287**, amplitude **50.147863505457956**, FWHM **1**. Applying the extracted page function to its locked starting snapshot retained **299, 10, 3**. Both the proposed server verification and projection comparison can pass.

   Evidence: [request/expression rules](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1555), [application rules](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6998).

   **Required:** validate the producer-specific request built from the saved frontend snapshot, including Auto-Fit overlays and explicit link lookup. Separately establish that every displayed effective parameter represents O. Expression-controlled fields cannot retain contradictory locked values. The snapshot correctly solves Voigt identity, inactive fields and the locked-29 conversion problem; it does not by itself establish this second relationship.

2. **BLOCKER — saved acceptance flags are still accepted without verification or authenticated attribution.**

   [D:827–835](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:827) gates CURRENT on `success` and `certificate.certified`, but explicitly excludes certification from recomputation.

   An arbitrary nonminimum point inside the requested bounds can have entirely consistent parameters, components, envelope, residuals, areas and statistics. Give that output a copied `certified:true` and `success:true`: every listed numerical verification can pass.

   On reload, this is the **saved file’s assertion**, not an independently established statement from the producing server. Posting it to a verifier that does not check certification does not change that.

   The same problem affects DE/basinhopping `success` and Auto-Fit’s acceptance-dependent `required` verdict. Labeling diagnostic restart counts, σ and alternative scores ATTRIBUTED is coherent. Allowing an unchecked attributed flag to authorize CURRENT leaves the round-1 acceptance blocker open.

   Evidence: certification actually performs additional minimizations at [fitting.py:1921](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1921); global-method acceptance depends on refinement at [fitting.py:1751](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1751) and [fitting.py:1853](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1853).

   **Required:** verify the acceptance property, preserve a verifiable producer attestation binding it to this R/O, or explicitly narrow the status so it does not claim verified acceptance.

3. **MAJOR — Auto-Fit’s saved context and finalisation contract remain incomplete.**

   The revised operation order is correct, and rejecting changed sample indices is a useful resolution. However:

   - `finalise(..., ctx)` needs the **pre-finalisation context**. R records ROI fields, but not the original background endpoint fields. R’s background indices cannot recover those fields: many endpoint values select the same indices, yet round differently after charge correction.
   - D’s context is the displayed context inherited from V5.3. D:784–786 requires it to reproduce the original request background directly. For manual backgrounds, finalisation moves every anchor by `-delta`, so final anchors generally cannot equal the original request anchors—even when `R.idx` remains unchanged.
   - The exact charge formula is `Number((projectedAnchor.center + oldShift).toFixed(3)) - 284.50`. Rounding O’s corrected center alone is different. Finalisation also shifts **every peak center and manual anchor**, operations omitted from its enumerated contract.
   - Auto-Fit’s anchor-support gate is not the backend component-support calculation. It uses `counts - fitted_y`, sequential sums and `1/max(counts,1)`; the backend uses `(counts-background)-fitted_sub` and squared weights. Substituting backend support while claiming the producer’s exact acceptance rules preserves two arithmetic readings.

   Evidence: [Auto-Fit acceptance/finalisation](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7725), [charge transformations](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5463), [backend support](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:2233).

   **Required:** save the original context explicitly; derive the final context and compare live state with that result. Define the anchor-support arithmetic deliberately.

   Another inaccurate current-code claim remains at D:776: `getCorrectedBE` maps **NaN**, not every nonfinite shift, to zero. `Infinity` survives its `isNaN` check. See [index.html:5526](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5526).

4. **MAJOR — the local snapshot does not necessarily describe the engine’s retained χ² or its committed state.**

   [D:890–902](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:890) fixes the weights and adds the missing output fields, but “snapshot, not re-propagation” does not settle the existing mutable chain behavior.

   An extracted-page probe with three Gaussian components in reversed linked-chain order, all independent parameters locked, returned:

   | Quantity | Value |
   |---|---:|
   | Successful local result’s retained χ² | 136.71590511197607 |
   | χ² recomputed from committed final peaks | 0.5214390159923038 |

   The initial `chiSq` propagates links once. Final commit propagates again; `rawResiduals` subsequently propagates again. The retained χ² can therefore describe another snapshot. Longer chains can also distinguish the committed peaks from later working peaks.

   Evidence: [mutable propagation and χ²](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:9288), [commit and subsequent residual evaluation](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:9511).

   **Required:** choose one final snapshot and explicitly derive its curves, all statistics, support and applicable acceptance evidence from it, then commit that same snapshot. Alternatively, classify inconsistent captures as unconfirmed. This round-1 local-chain finding remains unresolved.

5. **MAJOR — verification ownership is keyed to fewer inputs than the verifier checks.**

   The endpoint verifies `{R,O}`, but [D:843–845](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:843) caches only by frozen O.

   A different immutable R paired with the same O can reuse the successful verdict. Changing R’s method or parameter bounds can evade the server checks because the page does not independently repeat them. Freezing each object prevents mutation; it does not bind the pair.

   Existing history restoration uses shallow fit-result copies, so nested-object sharing must be addressed explicitly. See [index.html:15855](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:15855).

   **Required:** bind verification to the immutable R/O pair or whole immutable seal, plus verifier identity, and independently guard asynchronous attachment to the owning operation/tab.

6. **MAJOR — narrowing provenance to an attestation does not establish the verifier’s “same code” premise.**

   The revised **PROVENANCE: attested** label resolves the old overclaim at that label. But D:799–802 still claims that comparing software records establishes verification “with the same code that fitted.”

   Two dirty implementations can share commit, dirty flag, numerical version and installed distribution versions. A hash of `name==version` does not identify package contents or native builds. Missing identities can also compare equal. V6.7 correctly acknowledges these limitations, while V6.5 still relies on the stronger implication.

   Evidence: [software metadata construction](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:58), [revised provenance contract](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:907).

   **Required:** either establish the execution identity needed by the verifier, or describe its result as consistency under the identified verifier’s implementation, with the weaker producer attribution stated explicitly.

The requested method/reconstruction audit has a substantially positive result:

- **R contains enough numerical inputs to rebuild the original HTTP fit problem**, provided verification shares request normalization, model construction and background assembly with fitting.
- The request-derived seed is computed **before** DE generates its search box. Successful DE results use the request’s bounds after refinement/local competition; the transient box need not become their final parameter bounds.
- Perturbed starts derive from optimizer output. Their historical intermediate values cannot be recovered merely by rebuilding parameters; that requires replay. Scattered starts and `require_component` do not replace the primary result. Treating their detailed histories as attributed evidence is reasonable, subject to finding 2 for acceptance gates.
- A bounded two-component probe exercised all five methods with `n_perturb=1`, `n_starts=1` and `require_component`. Rebuilt parameter metadata and derived seeds matched in every case; envelope, residual and χ² recomputation matched exactly. The global methods correctly skipped scattered starts.
- A reversed server-linked chain successfully resolved centers in request order `3,2,1` to `289,287,285`.

The design must distinguish **wire request from normalized arguments**. Ordinary Run Fit currently omits `seed` and `charge_shift_ev`; the server supplies the defaults. Thus D:711–714’s “exactly as sent,” `seed:null`, and `R.request.charge_shift_ev` comparison are not simultaneously literal descriptions. See [request construction](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8907) and [server normalization](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/app.py:129).

The numerical revisions otherwise resolve the central round-1 arithmetic findings:

| Round-1 finding | Revision-2 disposition |
|---|---|
| Wrong reduced-χ² denominator and floor order | **Resolved.** Matches installed lmfit. |
| Missing `fitted_sub`/envelope/residual relationships | **Resolved in the proposed server contract**, using the rebuilt composite’s evaluation order. |
| Support verifier trusting `ip.support` | **Resolved for ordinary component support.** Auto-Fit’s distinct gate remains above. |
| Missing RMSE, AIC/BIC, parameter counts | **Substantially resolved.** |
| Empirical component tolerance | **Resolved.** Non-bit-stable shapes become UNCONFIRMED. |
| Frontend information loss / lock conversion | **Partially resolved; finding 1 remains.** |
| Selection completeness / derived seed / method / shift | **Improved substantially; context and normalization remain incomplete.** |
| Local output and chain consistency | **Partially resolved; finding 4 remains.** |
| Legacy record lost on peaks-only | **Resolved by the proposed separate provenance retention.** |
| Pending/offline states and ownership | **States resolved; cache binding remains incomplete.** |
| Area consumers and measurement ordering | **Named omissions addressed; Q5 correctly follows measurement.** |
| Unnamed attributed evidence | **Labels addressed; acceptance proof remains unresolved.** |

A fresh seven-shape probe found exact component/envelope reevaluation, repeated evaluation and χ² agreement for all seven backend shapes, including DS+G and LA. This is bounded evidence, not a universal bit-stability proof or the 202-target census. Installed lmfit confirms the revised denominator/floor/AIC/BIC order; installed SciPy confirms signed trapezoid terms followed by summation and final absolute value.

No new magnitude-tolerance fallback remains in the proposed CURRENT predicate. Replay still uses its expressly separate tolerance-based comparator, and legacy reconstruction retains its existing policy. The remaining design-rule problems are the competing readings identified above.

Minor corrections: the introduction points to nonexistent V6.14; the additive-unit pointer should reference V6.11. Define rendered-page hashing with an explicit exclusion or placeholder for its own embedded hash.

**VERDICT: NO-GO.**
