# Sealed fit record v6 design — Codex gate round 1, run B (commit 017d0d6)

**NO-GO.** V6 improves the record structure, but still permits false DISPLAY-CURRENT results and does not establish executable provenance.

Reviewed HEAD `017d0d6` against `c643c5f`; the differences are documentation only. I read V5.1–V5.9, all four v5 verdicts, the recording plan, and the relevant implementation. No files changed.

Below, **D** means the [design memo](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:687), **IH** means `templates/index.html`, **F** means `fitting.py`, and **A** means `app.py`. Repository line references apply to `c643c5f`.

1. **VERIFIED-claim audit: mostly accurate recording inventory, with material exceptions.**

   | Section | Result |
   |---|---|
   | **V6.1** | Confirmed: seed validation and mapping; persisted server/local certificates; import-time software metadata; background verdict/effect; project, spectrum, parameter-file and export recording. Confirmed that the original request remains missing, project arrays are rounded, loaders differ, and full O is not persisted. Evidence: `F:49–82, 2863–2909`; `A:129–148`; `IH:8580–8610, 11824, 11920, 12024, 12260, 12664, 13050, 13171, 13191`. |
   | **V6.3** | Correct that application uses live peaks and honors locks. “Returns D unchanged whatever O says” overstates the counterexample: unlocked fields change. More seriously, the claimed Auto-Fit operation order is wrong: charge correction, **window reselection/background computation**, then center locking—not shift, lock, reselect. `IH:7793–7819, 7855`. |
   | **V6.4** | Returned parameter metadata is accurately described. Holding the requested value applies to independent fixed parameters, **not expression-constrained parameters**. The assertion that averaging is now an integer 1–50 on both sides is false on the specified main. `A:85` truncates with `int()` and has no upper limit; `IH:5042` still double-parses averaging. |
   | **V6.6** | Correct: background subtraction, raw-count weights, lmfit’s χ² calculation and floor order, server residual association, server R-factor/null case, and `result.nvarys`. The proposed reduced-χ² formula then contradicts those facts. Auto-Fit’s RMSE denominator is the reselected `be2.length`, not necessarily O’s sample count. |
   | **V6.7** | Correct successful local return inventory, state writes, starting-point designation, and git’s exclusion of untracked files. These facts do not establish the proposed source-hash claim. |

   Under the requested ranking, the false averaging assertion and unrestricted locked-value assertion are **MAJOR**. The incorrect Auto-Fit order is also material to its projection contract.

   Minor citation corrections: the server area assignment is `F:2758`, not blank line 2759; V6.2’s references to the additive unit and recorded-but-unsealed class should point to V6.11 and V6.8.

2. **BLOCKER — G1’s projection still lacks sufficient inputs and a complete finalisation contract.**

   [`project(O,R,steps)`](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:732) can be pure, but R’s request specs cannot reconstruct the page model being compared.

   I extracted the actual request builder and confirmed that these two page models produce **identical requests**:

   - `shape:'Voigt', glMix:20, fixGlMix:true`
   - `shape:'GL', glMix:50, fixGlMix:true`

   Both request a fixed pseudo-Voigt mix of 0.5. Their page shape and inactive fields differ, and `_STARTS_MODEL_FIELDS` compares both. Similarly, linking forces `spec.fix_fwhm=true` regardless of the page’s original `fixFwhm`. See `IH:6910–6990, 8377–8380`.

   Thus **live can differ from project while the numerical model agrees**. Preserve the frontend representation needed for projection, or define and justify an effective-model comparison that deliberately excludes irrelevant fields.

   Links also invalidate V6.4’s blanket locked-value check. A direct `_make_peak_params` probe with a linked child requested at center 299, amplitude 10, FWHM 3—with all three fix flags—returned **287, 50, 1**, all `vary:false`, through parent expressions. That is intended server behavior. Expressions take precedence over those request values. `F:1555–1602`.

   Required additions:

   - Validate effective roles, expressions and their evaluated values, resolving chains independently of input order.
   - Define display conversions, including `gl_ratio × 100`, frontend shape identity, inactive fields, and transformed centers.
   - Validate Auto-Fit steps against its producer and anchor evidence. Arbitrary recorded steps must not authorize arbitrary transformations.
   - Include Auto-Fit’s acceptance gates: required-component result, refit convergence, supported anchor and center check. `IH:7769–7789`.
   - Specify alternatives separately: `_altPeaks` still applies parameters to a live-model copy while honoring locks (`IH:8777–8787`). “Use this solution” correctly becomes a new Run Fit, but R must capture that actual alternative-derived request.

   Reading Results from O closes the simple locked-table counterexample **only after the accessor applies the declared display transform**. Raw O centers after Auto-Fit would disagree with correctly shifted live centers. A parameter match alone also cannot establish agreement with O’s independently stored curves and statistics.

3. **BLOCKER — G2 closes the different-counts substitution, but not all cross-record bindings.**

   The explicit O/R energy and count equalities resolve v5’s spectrum-A/spectrum-B counterexample. The remaining checks are insufficient:

   - **Selection completeness:** checking each `R.idx[j]` establishes membership, not that the list is exactly the ordered selection produced by the recorded/live ROI. With background `none`, a response for a narrower subset can satisfy every listed sample and background check while D declares a wider ROI.
   - **Derived seed:** when `R.seed === null`, only `seed_source` is checked. Changing `O.random_seed` leaves every listed check satisfied. Recompute the versioned request-derived seed from resolved inputs, or explicitly classify it as unverified provenance.
   - **Method/settings:** no explicit `O.fit_method === R.method` check; no complete binding of effective parameter roles, expressions and bounds to R. Matching IDs/shapes plus checking fixed values does not establish the same constrained model.
   - **Final display frame:** checking samples in R’s old charge frame does not establish their coordinates in the displayed frame.

   The last issue has a concrete floating-point counterexample using the page’s arithmetic:

   ```text
   raw = 284.5, old shift = 0.1, new shift = 0.14

   (raw − old) − (new − old) = 284.35999999999996
   raw − new                = 284.36
   ```

   Auto-Fit additionally rounds ROI/background bounds to one decimal place during charge correction (`IH:5471–5480`), then reselects points. An inverse translation cannot recover the original selection generally.

   The adapter must explicitly distinguish R’s computational grid from the displayed grid, verify the selected index list and final frame, and decide what happens when finalisation changes the fitted sample set. Use `_roiSelect` and the actual charge-reading semantics, including the NaN-to-zero behavior of `getCorrectedBE`; the unconditional subtraction written in D:754 is not its complete operation. See [IH:5526](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5526).

   Different background windows/averaging that **change the effect** should fail the proposed adapter/effect checks. Settings ignored by the selected background need not produce different curves. The averaging-refusal branch must be an explicit dependency rather than described as deployed.

4. **BLOCKER — G3 verifies components, not the complete fit represented by O.**

   The fresh-fit statement is correct **narrowly**: `F:2750–2753` evaluates each component using the returned parameters. It does not prove every other relationship in O.

   Most seriously, V6 adds `fitted_sub` without explicitly requiring:

   ```text
   fitted_y === fitted_sub + background_y
   residuals === (counts − background_y) − fitted_sub
   fitted_sub corresponds to the verified component sum
   ```

   V6.5’s replacement step 1 omits these identities. Even if v5’s envelope/component bound is inherited, it does not connect the **new** `fitted_sub` to that envelope.

   **False-CURRENT construction:** keep valid parameters, component curves and envelope; replace `fitted_sub`, residuals and statistics with a mutually consistent different model. Component verification passes; statistics recomputation passes; the chart and reported statistics describe different fits.

   Other unchecked evidence remains:

   - `/api/verify-components` cannot establish that a saved minimum certificate belongs to this output or that its displacement/restart details are correct.
   - `required`, alternative solutions, alternative χ²/areas/moves, and `starts.fit` are outside the stated checks.
   - “Fresh by construction” needs ownership of an immutable captured response; it must not become a persisted flag that skips verification after reload.

   Explicitly distinguish recomputed evidence from producer-attributed evidence. At present only σ receives that qualification.

   **Same software:** equality of `software.numerics` and library version strings does not establish identical evaluator code or binaries. DS+G uses FFTs (`F:329–332`); LA uses `np.convolve` (`F:1424`). The cited LA/BLAS explanation cannot simply be assigned to both.

   **Offline:** UNCONFIRMED is coherent under Q6 if server verification is mandatory. It must remain distinct from a detected mismatch, retain the saved evidence, and never authorize current statistics. Different software may also be UNCONFIRMED, but the reason should distinguish unavailable verification from a failed comparison.

5. **BLOCKER / MAJOR — G4 is neither exact nor complete yet.**

   **BLOCKER: wrong reduced-χ² divisor.** D:813 defines `n_free = result.nvarys`, but D:818 divides χ² by `max(1,n_free)`. The correct denominator is:

   ```text
   max(1, n_data − n_free_params)
   ```

   For 201 samples and three free parameters, the proposed statistic is **66 times** the correct reduced χ². Installed [lmfit minimizer.py:312](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py:312) settles the semantics:

   ```text
   raw_chi = sum(residual²)
   redchi  = raw_chi / max(1, ndata − nvarys)
   chisqr  = max(raw_chi, 1e−250 × ndata)
   ```

   Validate parameter counts against R’s resolved roles, require positive degrees of freedom as the server does (`F:2548–2554`), and exclude synthetic `area` metadata.

   **MAJOR: support’s named verifier trusts the answer.** `_componentSupportFromResponse` immediately returns `ip.support` when present (`IH:7650`). A probe with a zero component and forged `supported:true, f:999` returned that verdict unchanged.

   Merely supplying `fitted_sub` does not repair this. Its fallback also uses sequential sums and `(w²*r)*r`; Python uses NumPy sums and `w²*(r²)`. Finite masks and linked-root inheritance must match too. See `IH:7636–7656`; `F:2233–2249, 2802–2819`.

   The numerical hypotheses resolve as follows:

   - **lmfit statistics/floor order:** settled above.
   - **`best_fit`:** a separate evaluation, not the residual evaluation’s retained model array. `lmfit/model.py:1587` evaluates it after minimization. The minimizer recomputes a residual at the returned point (`minimizer.py:1577, 1691`), but later covariance evaluations can also occur; “LAST evaluation” is too broad.
   - **Measured statistics change:** one production-path `run_fit` probe per seven backend shapes produced **zero difference** between reported χ² and recomputation from captured `best_fit`. This is bounded evidence, not the 202-target census.
   - **“Ulp-level/below rounding by construction”: not established.** If model reevaluation changes by ε, squaring a residual changes by terms involving both `rε` and `ε²`. Cancellation prevents a universal relative-χ² ulp claim.
   - **`_npPairwiseSum`:** extracted page code matched NumPy 2.4.4 exactly on 100 positive float64 arrays, lengths 129–100,000. This supports the tested reductions; production-domain/platform exactness remains a gate.
   - **SciPy trapezoid:** installed SciPy 1.17.1 computes signed `dx * (y_next + y_previous) / 2`, then sums; F applies `abs` afterward. See [SciPy `_quadrature.py:139`](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/scipy/integrate/_quadrature.py:139).

   Complete the null/finite schema: `stderr`, bounds, certificates, R-factor and support F legitimately contain nulls. “O finite” cannot mean every field is a finite number. AIC/BIC are also in O (`F:2859–2860`) but have no specified recomputation or attribution policy. RMSE needs a fixed O-domain denominator, especially after Auto-Fit reselection.

   **Q5 is directionally correct but incomplete.** Besides Results, sidebar, Quantify and CSV/XLSX, area readers include:

   - Auto-Fit’s graphite-fraction warning: `IH:7562–7566`.
   - Sidebar support patching: `IH:7707`.
   - Scattered-starts/alternative percentages: `IH:8747–8756`, sourced from `F:2133–2146`.
   - Spectrum-file component areas: `IH:11888–11897`.

   The spectrum saver already uses a **third definition**: sequential trapezoids with `abs(dx)` per interval. On an accepted nonmonotonic grid `[0,2,1]` and unit samples, server area is **1**, spectrum-save area **3**, rectangle area **6**.

   Q5 must cover every reader, local/stale previews, integration domain, and alternative summaries—not just change `_peakArea`.

6. **MAJOR — G5’s local O is improved but still incomplete.**

   The proposed schema omits explicit `success`, R-factor and areas while requiring acceptance and a common consumer view. It needs a complete local projection and derived-value contract, rather than “steps 1–3 and 5” with server field names.

   Crucially, local weights use:

   ```text
   1 / sqrt(max(net[i] + background[i], 1))
   ```

   They do **not** read original raw counts directly. Preserve that association; substituting `O.counts` can change the objective through rounding. [IH:9211](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:9211).

   Local linking is also order-sensitive: `applyParams` propagates links in one pass through `work` (`IH:9297–9304`). Repeated evaluations can propagate a reversed chain differently. “Same functions, so exact” does not establish that captured final parameters, committed live peaks, curves and statistics are one snapshot for arbitrary chains.

   The starting-point policy is correctly retained. It must continue through `_isLocalFit`, `_isLocalModel`, imported provenance, undo/history, Batch copies, stack banners and exports (`IH:9074–9139`). Explicitly retain absent uncertainties and the local engine’s held `caM`.

7. **MAJOR — G6 hashes files, not necessarily executed code.**

   The proposed [source digest](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:854) does not justify PROVENANCE-COMPLETE:

   - Reading a module’s `.py` bytes does not prove those bytes produced the loaded code object; bytecode caches and subsequent file replacement break that implication.
   - `sys.modules` at `fitting` import is incomplete. `app.py` imports additional repository modules afterward (`A:45–48`); later imports are also missed.
   - Venv code, compiled extensions, BLAS/FFT binaries and build configuration are excluded. Equal version strings do not identify equal artifacts.
   - Templates are served from disk independently of backend restart. Hashing once cannot identify later rendered pages. `DEPLOY.md:31–37`.
   - Rendering injects runtime reference data and software metadata (`A:800–808`). Template-source bytes do not identify the rendered page.
   - Runtime data files are not modules. Record relevant consumed data separately; distinguish it from fit inputs already preserved inline.

   “Equals the commit’s tree” is checkable only with a specified manifest: included paths, relative-path encoding, framing and hash algorithm. A dynamic subset of loaded files cannot be reconstructed from one digest alone.

   Identify a recoverable immutable execution artifact and the actual served page, or narrow the provenance claim. Startup cost remains unmeasured; it is not the central obstacle.

8. **MAJOR completeness gaps; legacy policy itself is coherent.**

   V6.8 correctly preserves the owner’s October 5 rule: keyless saves never become current. Treating keyed and recorded-but-unsealed saves likewise is a clearly identified **tightening requiring Q1**, not existing shipped behavior.

   The simultaneous consumer switch, lossless seal persistence, `.fit.json` treatment, export tails and PNG inclusion are improvements. Remaining migration requirements:

   - Specify verification-result ownership across asynchronous loads, tab replacement, edits and history restores; a result must attach to the exact immutable O checked.
   - Preserve records when legacy reconstruction becomes peaks-only. Today `_dropRestoredFit` simply nulls `fitResult` (`IH:10585–10587`), losing its record. V6 promises that recorded-but-unsealed provenance remains shown.
   - Include the additional area consumers above and the local designation/provenance helpers explicitly.
   - Define alternative-preview evidence separately from the current primary fit.

   **MINOR ordering conflict:** Q5 says area changes are measured before approval (`D:834–835`), but V6.11 schedules that measurement after approval. Likewise 1a′ calls the χ² change measured before 1b performs the measurement.

9. **MAJOR — V6 introduces a new empirical magnitude tolerance into CURRENT.**

   D:793–795 permits component verification “within the measured rounding” if exact reevaluation fails. No bound, operation model or acceptance formula is specified. An observed maximum is not a rounding proof.

   The owner’s envelope-test wording explicitly distinguishes cross-language **parity tolerance** from a same-implementation rounding bound; it does not authorize importing a measured tolerance into DISPLAY-CURRENT. See [tests/envelope_identity.py:30](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/tests/envelope_identity.py:30) and `CLAUDE.md:174–198`.

   Competing readings also remain concrete: effective expression roles versus request fix flags; original versus reselected samples; raw counts versus locally reconstructed counts; support’s server/page arithmetic; and three area definitions.

   Existing lmfit floors and replay-comparison rules are not newly introduced violations. The new measured-tolerance fallback is.

Validation was read-only source inspection and bounded numerical/extracted-page probes. I did not run the full browser suite, 202-target census, or universal background/evaluator proof; their outcomes remain unmeasured.

**VERDICT: NO-GO.**
