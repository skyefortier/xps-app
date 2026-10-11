# Sealed fit record v6 design — Codex gate round 2, run A (commit be59530)

**Revision 2 still permits false DISPLAY-CURRENT results.** The arithmetic contract is substantially improved, but projection, acceptance evidence, and local finalisation remain incomplete.

Reviewed HEAD `be595309` against `c643c5f`; differences are documentation only. No files changed. Below, **D** means the [design memo](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:675), **IH** means `templates/index.html`, and **F** means `fitting.py`.

1. **BLOCKER — G1/G2: the snapshot is not bound to the request, and reproducing application rules does not prove display agreement.**

   D:743–768 projects from `R.pageModel`; D:803–807 verifies parameters against `R.request`. No check establishes that the snapshot, passed through the request builder and producer overlays, actually produces that request.

   Consequently, a saved snapshot and live model can carry a different locked value while the request, O, curves and server verification remain unchanged. Projection preserves the substituted value and the model comparison passes.

   There is also an **honest-record counterexample**, without altering the record. My probes using the actual parameter builder and page application function produced:

   | Linked child | Requested/page snapshot | Server expression value | Page after application |
   |---|---:|---:|---:|
   | Centre, locked | 299 | 287 | 299 |
   | Amplitude, locked | 10 | 50 | 10 |
   | FWHM, locked | 3 | 1 | 3 |

   Server expressions override the child's locks; `_applyBackendParams` preserves those locked frontend fields. The proposed projection faithfully reproduces that disagreement. Results would read the snapshot-preserved numbers while curves describe O's different parameters.

   Evidence: [F:1555](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1555), [IH:6998](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:6998).

   **Required:** validate snapshot → request using explicit parent lookup and the actual Auto-Fit overlays; then separately establish effective displayed-parameter agreement with O. Expression-constrained fields need a defined application rule that cannot preserve contradictory locked values. This applies through linked chains and to linked shape parameters.

   The ordinary Voigt/GL distinction, inactive fields, DS/DS+G/LA mappings, and locked GL percentage rounding are otherwise correctly preserved by taking a frontend snapshot and sharing the application function.

2. **BLOCKER — G3: the acceptance predicate trusts a saved assertion, not an authenticated server verdict.**

   D:827–835 explicitly gates CURRENT on `O.success` and `O.certificate.certified`, while leaving certification unrecomputed. `/api/verify-fit` receives those assertions from the file. Its listed checks neither authenticate their origin nor establish that they certify this R/O.

   A nonminimum parameter set can have perfectly consistent components, background, envelope, residuals, statistics and support. Supplying `success:true` and a copied `certified:true` lets it pass the specified acceptance predicate.

   Calling certificate details “ATTRIBUTED” is appropriate for restart counts and displacement history. It does **not** establish the truth of an attributed boolean used to authorize CURRENT. The same issue affects global-method success and Auto-Fit's attributed required-component acceptance evidence.

   The actual certification involves additional minimisations, not model evaluation: [F:1954](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1954).

   **Required:** either authenticate the producer's acceptance statement bound to the complete relevant record, re-establish acceptance, or explicitly narrow the state to verified numerical consistency with unverified acceptance. The present wording promises more than the endpoint proves.

3. **MAJOR — G1/G2: Auto-Fit finalisation still lacks its original context inputs.**

   R saves the original ROI fields, shift, request background indices and anchors. The inherited D context describes the final display. Neither schema explicitly preserves the **original background form endpoints** needed to derive their rounded final values.

   Those endpoints cannot be recovered from request indices. For example, on a 0.1-eV grid, starts `280.04` and `280.09` select the same initial boundary sample. After a shift delta of `0.01`, the live code produces respectively:

   ```text
   (280.04 − 0.01).toFixed(1) → "280.0"
   (280.09 − 0.01).toFixed(1) → "280.1"
   ```

   These can select different final background windows. The request alone cannot distinguish their histories.

   Finalisation must also preserve the actual associations: add the provisional shift to the fitted anchor centre, round that raw centre, derive the new shift, then subtract the delta from peak centres and manual anchors. D:754–756's abbreviated sequence needs those operations and their inputs made explicit.

   Evidence: [IH:5463](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5463), [IH:7793](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7793).

   **Required:** record the producer and complete pre-finalisation context, derive final context from it, and compare the live context with that result. Retaining Q8's refusal when ROI samples change is correct, but insufficient to reconstruct this context.

4. **MAJOR — G5: one final local snapshot does not make the existing objective belong to it.**

   D:894–902 retains the final working snapshot and χ² “as the engine sums” it. The current engine retains an earlier `chi`, subsequently propagates links before committing live peaks, and propagates them again while computing RMSE.

   An extracted-production-function probe with an all-held Gaussian chain ordered grandchild → child → root returned:

   ```text
   success:             true
   reported χ²:         2237.979916369686
   χ² of final snapshot:2620.2061060494048
   ```

   RMSE described the final snapshot; χ² did not. This directly exercises the order-sensitive chain issue from round 1.

   Evidence: [IH:9297](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:9297), [IH:9512](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:9512), IH:9527–9529.

   **Required:** define a finalisation operation that freezes one model, derives every reported array/statistic from that snapshot, and commits that same snapshot. Merely capturing the last working peaks leaves the objective association unresolved. The corrected local weights and starting-point designation are otherwise sound.

5. **MAJOR — verification ownership must include R.**

   D:843–845 caches verification under frozen **O**, but the verified proposition concerns **`{R,O}`**.

   Reusing the same O in a new seal with a different R can reuse an `ok` issued for the original request. Page checks do not repeat the server's bounds, roles or seed verification. Immutability of O does not prevent this substitution.

   **Required:** own/cache the result by the immutable complete seal or at least the exact R/O pair, with the applicable operation ownership. The mechanism currently specified does not establish the ownership guarantee claimed.

6. **MAJOR under the requested false-VERIFIED rule — the shift-reader description remains wrong.**

   D:776 says `getCorrectedBE` maps a **non-finite** shift to zero. It uses `isNaN`, so `Infinity` remains `Infinity`. `_roiSelect` does the same. A bounded JS probe confirmed this.

   Evidence: [IH:5526](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5526), IH:5548.

   Specify the actual reader, or explicitly reject non-finite shifts before it. Do not substitute `Number.isFinite` while claiming identical reading.

The remaining requested checks resolve as follows:

| Question | Finding |
|---|---|
| **Can R reconstruct parameters and seed for every method?** | **Yes for initial parameters, effective request constraints and the master seed**, using the complete shared HTTP normalization and `run_fit` preparation. `_request_seed` hashes the ordered parameter roles before DE generates its box. |
| **DE and basinhopping** | Accepted DE refinements restore requested bounds; basinhopping refines under those bounds. Their final constraint metadata is reconstructible. Individual historical DE boxes depend on candidate starts, including optimizer results; reconstructing the entire search history requires replay, not merely rebuilding parameters. F:1767–1800, 1853–1874, 2525–2586. |
| **Perturbations, scattered starts, required refit** | R contains the recipe needed to rerun them. Perturbations depend on fitted values; scattered starts use initial parameters; the required refit starts from the fitted retained model. Seed equality establishes the seed, not that those computations actually occurred. F:2092, 2634, 2697, 2731. |
| **Exact evaluator/statistics verification** | Achievable in bounded testing. Seven fresh fits—one per backend shape—gave exact component, composite, χ² and trapezoid-area re-evaluation, including DS+G and LA. This does not prove universal production bit stability; Q7 correctly fails closed. |
| **Background verification** | Must share the complete `run_fit` background preparation. Calling `compute_background` alone is insufficient: it handles integral methods, while manual, linear, none, window normalization and extension live elsewhere. F:1314, 2393–2475. |
| **Statistics** | The corrected denominator, floor order, residual association, AIC/BIC and RMSE contract are sound. Installed lmfit confirms them. `best_fit` is a separate evaluation. |
| **Tolerance rule** | The new measured-tolerance fallback is removed. Existing replay tolerances and optimizer/acceptance thresholds remain; they must not become array-verification tolerances. |
| **Provenance** | Narrowing it to an attestation resolves the execution-proof overclaim. It does not authenticate a saved certificate. |
| **Legacy, migration, areas** | The legacy policy, separate provenance retention, enumerated area consumers and Q5 measurement order are coherent. Ownership still needs finding 5's correction. |

Thus round 1's reduced-χ² error, missing `fitted_sub` identities, support-verifier arithmetic, area-consumer omissions, averaging deployment claim, empirical verification tolerance, and executable-provenance overclaim are resolved **at the design level**. Projection/binding, acceptance evidence, Auto-Fit context, local snapshot consistency, and verification ownership remain unresolved or only partially resolved.

Minor corrections: D:678 points to nonexistent V6.14; D:727 names the wrong ship section. The rendered-page digest also needs an explicit rule excluding or blanking its own digest field.

Validation was read-only source inspection and bounded Python/JS probes; no full browser suite or 202-target census was run.

**VERDICT: NO-GO.**
