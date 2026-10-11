# Sealed fit record v6 design — Codex gate round 1, run A (commit 017d0d6)

**VERDICT: NO-GO.** V6 improves the structure, but its proposed proof still permits inconsistent records and rejects some valid ones.

Reviewed HEAD `017d0d6` against `c643c5f`; the differences are documentation only. No files changed. Below, **D** is the [design memo](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:675), **IH** is `templates/index.html`, and **F** is `fitting.py`. Code line numbers apply to `c643c5f`.

1. **BLOCKER — G4’s reduced-χ² formula uses the wrong denominator.**

   D:813 defines `n_free = result.nvarys`, but D:818 divides χ² by `max(1, n_free)`. lmfit divides by **`max(1, ndata − nvarys)`**. For 121 observations and one varying parameter, the proposed value is 120 times the correct reduced χ².

   The current-code account of lmfit’s calculation is otherwise correct: weighted residual squares are summed; reduced χ² is calculated **before** flooring reported χ² at `1e-250 * ndata`. The naming collision between lmfit’s `nfree` and this design’s `n_free` must be removed. [lmfit minimizer.py:312](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py:312), [F:2822](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:2822).

2. **BLOCKER — G3/G4 still do not close the component → envelope → residual → statistics proof.**

   V6.5 replaces the internal-consistency step with bindings, component IDs/shapes and statistics recomputation. V6.6 defines statistics from `fitted_sub`, but never explicitly requires all these relationships:

   ```text
   fitted_sub corresponds to the component sum
   fitted_y === fitted_sub + background_y
   residuals === (counts − background_y) − fitted_sub
   ```

   `/api/verify-components` checks individual curves and areas. It does not establish that the separately stored `fitted_sub` describes those components. An unrelated `fitted_sub` with consistently recomputed statistics can therefore satisfy the listed checks. An independently altered `residuals` array can also change the page’s RMSE unless its association is checked.

   Even if the old envelope-identity requirement is intended to survive implicitly, it does not bind the **new** `fitted_sub` field. State every equation, operation order, component summation order and applicable derived bound explicitly. The actual construction is at [F:2742](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:2742) and F:2827.

3. **MAJOR — G1’s projection is not yet reconstructible from its declared inputs, and its lock rule rejects valid expressions.**

   There are three distinct problems.

   - **The backend request loses frontend information.** Voigt and GL fixed at 50% can produce the same backend spec; Voigt forces `fix_gl_ratio:true` irrespective of the page’s `fixGlMix`. Inactive shape fields also disappear from the request, yet `_STARTS_MODEL_FIELDS` compares them. `project(O,R,steps)` cannot reconstruct that complete frontend model from the as-sent specs alone. IH:6929–6939, 6972–6979, 8377–8380.
   - **Expression roles override locks.** `_make_peak_params` assigns linked expressions before considering ordinary held-value semantics. My read-only probe sent a linked child with `center:999`, `fix_center:true` and splitting 2 from a parent at 285. The successful response returned centre **287**, `vary:false`, `expr:"p1_center + 2.0"`. D:757’s unconditional locked-value equality rejects it. [F:1555](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1555).
   - **Mapping units is not an exact inverse.** A locked page GL mix of `29` sends `0.29`; projecting back with multiplication gives `28.999999999999996`. The current page keeps the locked `29`. These display identically but fail the proposed exact model comparison. IH:6942, 7005.

   Pure projection is the right direction, but it needs an explicit frontend snapshot or a deliberately narrower comparison domain, and a role-aware mapping. Validate expressions, dependencies and evaluated values independently of lock flags, including chains in arbitrary order.

   “Use this solution” correctly initiates a new Run Fit; capture its actual `startPeaks` request. Merely retaining an alternative’s parameters does not give its preview a validated curve/statistics contract. IH:8777–8804, 8832, 8874.

4. **BLOCKER — G1/G2 do not adequately bind Auto-Fit’s final display frame and selected samples.**

   The stated finalisation is incomplete:

   - Auto-Fit rounds the fitted raw reference centre with `toFixed(3)`.
   - Charge correction rounds ROI and background boundaries with `toFixed(1)`.
   - It reselects observations and recomputes the background.
   - It locks centres **after** that reselection, whereas D:739 lists locking first.

   See [IH:7793](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7793), IH:5467–5480, 7808–7829 and 7855.

   D:754 proves that each saved index refers to a matching raw sample. It does **not** prove that the list is exactly the selection produced by the recorded/current ROI, including completeness and order. Nor does it specify the necessary equality between the transformed fit grid and today’s `rawBE − ccShift`. Those subtraction associations need not be bit-identical.

   Thus, matching `project(...)` does not by itself prove that the chart’s observations, component samples and statistics concern the same selected points. Reading table values from O also requires an explicit display-frame transformation for centres and bounds.

   Auto-Fit’s acceptance gates remain missing: required-anchor result, reduced-refit convergence, support and reference-centre checks. `success`, certificate and background convergence alone do not reproduce the producer’s acceptance policy. IH:7769–7788.

   **The VERIFIED RMSE description is overstated for Auto-Fit:** it divides O’s residual sum by **`be2.length` after reselection**, not necessarily O’s observation count. IH:7822.

5. **MAJOR — G2’s remaining request/output bindings are incomplete; the averaging premise is false on the specified base.**

   The new exact counts/energy checks correctly close v5’s straightforward “O from different counts” counterexample. Caller-seed equality is also correct. Remaining holes:

   - For `R.seed === null`, only `seed_source` is checked. Changing `O.random_seed` passes. Recompute the versioned request-derived seed from the effective request, or establish an equivalent request/output binding. F:2525–2532.
   - IDs, shapes and held values do not validate free-parameter bounds, `vary`/`expr` roles, constraint expressions or their values against R. An output describing another constraint model can pass component re-evaluation.
   - No explicit equality binds `O.fit_method` to R’s method or `charge_shift_applied` to the recorded execution shift.
   - The proposed `R.ccShift` needs an explicit place in R’s schema, distinct from the HTTP `charge_shift_ev`, which is zero.

   **D:762’s “whole number 1–50 on both sides” is not true at `c643c5f`.** The server uses `max(1, int(...))`, without a 50 cap; the page request uses `parseInt(...) || 1`; `_bgEffect` deliberately performs the additional parse needed to mirror the current background helpers. [app.py:83](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/app.py:83), IH:5038–5052, 8885. A separate branch is not deployed evidence or a declared ship prerequisite.

   `_bgWindowIndices` is usable for the adapter, but `getCorrectedBE` reads global state, and `_bgEffect` falls back to global anchors unless explicit anchors are supplied. The adapter must use explicit saved inputs and reproduce the current readers exactly.

6. **MAJOR — G3 introduces an empirical currency tolerance and overstates what component verification proves.**

   Fresh component curves are evaluated from `result.params`, so the **narrow** “parameters describe their component” construction claim is supported by F:2750–2775. It does not prove the complete response, including independently evaluated envelope, statistics, alternatives and acceptance evidence.

   For loaded records:

   - Matching numerical-version strings and library versions does not establish identical executed code or numerical-library builds.
   - LA uses `np.convolve`; DS+G uses NumPy FFTs. The claim that both have the same alignment-dependent **BLAS** convolution mechanism is unsupported. F:1424 versus F:330–332.
   - D:793–795’s fallback to **“measured rounding”** is an empirical acceptance tolerance. The envelope test’s permission for page/server **parity** is not permission to use that tolerance as a loaded-fit currency proof. [tests/envelope_identity.py:9](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/tests/envelope_identity.py:9), CLAUDE.md:170–199.
   - Allowing curve differences while still requiring an exactly equal re-evaluated area needs a separate, coherent arithmetic contract.

   The endpoint also does not verify alternatives’ scores, areas, fractions, shifts or occurrence counts, or that the certificate actually certifies this R/O. A copied `certified:true` survives a component-only evaluation. Declare such evidence explicitly as attributed producer statements, or add the required verification; currently only σ receives that limitation.

   **UNCONFIRMED offline is appropriate** when mandatory verification cannot run. It must propagate through every consumer, and any cached verification must remain bound to immutable record content and verifier identity.

7. **MAJOR — G4’s exact arithmetic and area contracts remain incomplete.**

   The arithmetic audit establishes:

   - **lmfit:** `best_fit` is a fresh `model.eval` after minimisation, not the retained model array used to calculate χ². Equality requires repeatable evaluation at the same effective parameters. [lmfit model.py:1573](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/model.py:1573).
   - **Measured change:** my bounded seven-shape probe compared recomputed χ² against lmfit for 14 model fits and found **zero difference**, including LA and DS+G. Repeated evaluations also matched in this environment. This does not establish the 202-target result or production-library behaviour. D:822’s “below rounding by construction” and D:901’s predetermined “ulp-level” size are unjustified: cancellation can amplify a small model difference relative to residual statistics.
   - **NumPy sum:** the page helper reproduces the pairwise structure. Direct extracted-JS probes matched installed NumPy 2.4.4 for positive arrays of lengths 7 through 65,537, including the 8/128 boundaries. This supports the hypothesis for these contiguous float64 reductions; it does not prove every other arithmetic path.
   - **SciPy trapezoid:** installed SciPy forms signed `dx`, then `dx * (y[i+1] + y[i]) / 2`, then sums; the caller takes the final absolute value. Multiplying by `0.5` first or summing sequentially is not the same arithmetic. [SciPy _quadrature.py:139](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/scipy/integrate/_quadrature.py:139).

   **Support is not an exact twin merely by supplying `fitted_sub`.** `_componentSupportFromResponse` immediately returns an existing support object. Its fallback sums sequentially and evaluates `(w²*r)*r`; Python computes `w²*(r²)` with NumPy summation. A read-only probe produced different `delta_chi2` values. It also needs the root-ancestor override for linked components. [IH:7636](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7636), F:2233–2249, 2802–2819.

   Complete the contract for `n_data`, parameter-role counting, positive degrees of freedom, nullable fields, AIC/BIC, support, and duplicated statistics such as `starts.fit.chi2r`. Changing only final response χ² leaves the latter derived from the old calculation. F:2171, 2206, 2853–2860.

   **Q5 correctly identifies a real area change, but understates its consumers.** Besides Results, sidebar, Quantify and CSV/XLSX, cover:

   - sidebar support patching: IH:7707;
   - Auto-Fit’s **40% graphite warning**: IH:7565;
   - alternatives’ server-calculated areas/fractions: F:2133–2145, IH:8747;
   - spectrum-save areas, already using a separate trapezoid implementation: IH:11893.

   Q5 can change a warning decision, not just displayed areas and atomic percentages.

8. **MAJOR — G5’s local O remains an incomplete executable contract.**

   The stated successful return object is correctly cited at IH:9576. “Writes the rest into state separately” is too broad: the varied-parameter inventory and per-component sampled curves are not all persisted there.

   The proposed local schema omits `success` despite requiring it for acceptance, and does not fully define R-factor, areas, envelope/residual associations or their verification. More importantly, its weights must use the engine’s actual reconstruction:

   ```text
   1 / sqrt(max(net[i] + background[i], 1))
   ```

   Substituting independently recorded raw counts changes the arithmetic. Local sums are sequential and do not inherit lmfit’s χ² floor. [IH:9211](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:9211), IH:9318, 9523–9561.

   Linked propagation is also a single mutable pass in peak order, not a pure dependency evaluation; arbitrary-order chains need explicit handling in capture and replay. IH:9297–9305.

   `reportable:false` and the starting-point designation are correct. Preserve them through `_provenanceOf`, undo, Batch copies, `.fit.json`, history and stacks—not only the live fit-result accessor. IH:2390–2402, 9077–9135.

9. **MAJOR — G6’s proposed hash does not identify executed software.**

   Hashing source-file bytes named by `sys.modules` establishes disk contents at the hashing time. It does not establish the code objects already loaded from those files, accepted bytecode caches, later imports or runtime replacements.

   It also excludes the venv’s actual Python/native-library contents; version strings do not identify those artifacts. For the browser, a hash taken at worker import does not identify a template served later, its rendered data, or the browser executing the local fitter.

   This is a concrete deployment concern: the frontend and reference data are served from disk while Python workers require restarting. The template injects runtime reference data from configurable `XPS_DATA_DIR`. [DEPLOY.md:31](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/DEPLOY.md:31), app.py:185–189, 800–808.

   “Equals the commit’s tree” additionally needs a defined manifest: which relative paths, which files, canonical framing and which digest algorithm. A runtime subset of loaded modules is not the entire tree, and that subset is not recorded.

   Use a recoverable execution-artifact identity with a defined manifest, dependency identity and served-page identity, or withhold PROVENANCE-COMPLETE. The current proposed predicate can falsely grant it.

The remaining VERIFIED inventory in V6.1 checks out: seed transport and persistence, certificate capture, once-at-import software metadata, background verdict/effect, project/spectrum/parameter saves, export tails and PNG metadata. The starting request remains absent; project rounding, differing loaders and distributed readers remain. Qualify “arrays are memory-only”: the **complete authoritative O** is absent from saves, but some arrays, including `fittedY`, already persist.

**Legacy and migration:** V6.8’s keyless policy respects the owner’s 2026-10-05 rule. Making keyed and recorded-but-unsealed saves never current is a coherent, explicitly proposed tightening of shipped restore behaviour. The recorded class should retain its historical record even when restoration falls back to peaks-only; today that path can discard `fitResult`, so the adapter must preserve provenance separately. IH:12254–12296.

The simultaneous producer/consumer migration is appropriate. Add the sidebar/Auto-Fit area consumers above and specify pending verification, failure and ownership handling on load, tab switch and history restore. Existing fit-operation tokens do not automatically define ownership for a new asynchronous verification request.

**MINOR:** Auto-Fit operation ordering is misstated; D:712 points to V6.8 instead of the ship section; and measuring Q5 “before approval” conflicts with placing that measurement in the post-approval 1b phase.

The new empirical component tolerance violates the design-rule intent. The unresolved lock/expression, averaging, frame, support and area mappings also leave competing readings of the same fields.

**VERDICT: NO-GO.**
