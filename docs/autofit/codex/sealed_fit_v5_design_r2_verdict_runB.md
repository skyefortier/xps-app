# Sealed fit record v5 design — Codex gate round 2, run B (commit 4ff4fa0)

**NO-GO.** Revision 2 resolves much of round 1, but its remaining checks can still admit false DISPLAY-CURRENT results and reject valid outputs.

Reviewed HEAD `4ff4fa0` against `90651e6`; the differences are documentation only. No files changed. Below, **D** denotes the design memo, **IH** `templates/index.html`, and **F** `fitting.py`.

1. **BLOCKER — D is not independently reconstructible by `applyBackendResult(O)`.**  
   **Round-1 display-binding blocker: partially resolved.**

   [D:555](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:555) requires reapplying O and comparing exactly. But [`applyBackendResult`](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:6988) mutates global `state.peaks`; its result depends on existing peaks, shapes and locks. It does not produce a model from O alone.

   A read-only probe using the actual `_applyBackendParams` demonstrated the hole: O’s center was `10`, the displayed center was `99` with `fixCenter=true`, and reapplication left the displayed model unchanged. Thus, using D or live state as the reapplication substrate checks a fixed point, not agreement with O.

   Using the original starting model instead needs an explicit reconstruction contract. Linked parameters follow backend expressions, even where frontend locks would suppress assignment ([F:1518](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/fitting.py:1518)). Auto-Fit then performs additional operations outside `applyBackendResult`: charge correction, ROI reselection and center locking (IH:7774, 7780, 7825). Its anchor-acceptance gates also exceed `O.success`: IH:7741, 7749, 7753.

   **Required:** define a pure display projection with explicit inputs and producer-specific finalization. Validate displayed numerical values against O independently of display locks; validate the transform, links and Auto-Fit acceptance separately.

2. **BLOCKER — the residual identity is false for the actual server, and the statistics bound is incomplete.**  
   **Round-1 statistics blocker: partially resolved; new arithmetic defect.**

   [D:545](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:545) requires exact `residuals = counts − fitted_y`. The server instead computes:

   ```
   fitted_y = fitted_sub + background
   residuals = (counts − background) − fitted_sub
   ```

   See [F:2689](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/fitting.py:2689) and F:2774. Those expressions are not floating-point identities. A direct arithmetic probe gave:

   | counts | background | fitted_sub | Server residual | Proposed residual |
   |---:|---:|---:|---:|---:|
   | 12345.6 | 10000.2 | 2345.3 | 0.0999999999994543 | 0.1000000000003638 |

   This would reject an otherwise valid output.

   Moreover, O does not retain `fitted_sub`. Recovering it by subtracting background from the envelope, or summing components, needs its own error analysis. A `γ_n` bound on the final sum does not cover cancellation, weight construction, squaring, division and square roots.

   There are also statistical semantics to specify. The installed [lmfit implementation](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py:312) floors reported χ² at `1e-250 × n_data`, **after** calculating reduced χ². Consequently, the proposed formulas are not universally identical to the returned statistics even with exact residuals. F:2800 also returns no RMSE field against which to check agreement.

   **Required:** specify the retained intermediates, arithmetic order, per-statistic error bounds, null/zero cases and versioned statistical definitions. Do not repair this by widening an empirical tolerance.

3. **BLOCKER — the three records lack necessary cross-record bindings.**  
   **New defect exposed by the split; round-1 data/context binding remains incomplete.**

   [D:542](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:542) explicitly checks O’s energies against R, but never requires **`O.counts === R.counts`**.

   A concrete false-CURRENT construction is possible: retain R for spectrum A, attach a valid O for spectrum B with the same energy grid and component IDs/shapes, and use background `none`. O’s internal statistics pass; both backgrounds are zero; D can match O. No listed step detects the different counts.

   Similarly:

   - D’s background/ROI/anchor context is compared with live state, but not validated against R’s request and display transform.
   - R’s saved sample indices are never used to bind the displayed observations to the fitted observations.
   - R’s seed and O’s `random_seed` have no required equality check.
   - Adding environment information to the response creates another overlapping fact in R and O without a consistency rule.

   This matters because the chart also displays live raw observations, outside the proposed list of O-owned curves ([IH:11097](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:11097)).

   **Required:** specify and check the R→O data correspondence, R→D context mapping, and correspondence between fitted samples and displayed observations. Storing three immutable objects does not establish these relationships.

4. **MAJOR — drawing O’s curves removes the evaluator mismatch, but also leaves parameters and other reported evidence unverified.**  
   **Round-1 statistical/model consistency finding: not fully resolved.**

   Under [D:542–561](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:542), changing an O parameter value while retaining its component curve, envelope and residuals can pass the listed checks. D then adopts that value, while the chart draws the unchanged curve.

   There are still two independently readable descriptions of the component: its parameters and its stored samples. The revision no longer checks their agreement.

   The recomputation list also omits component areas and support statistics. Changing `support.supported` can alter which components contribute to reported percentages and Quantify without failing the proof (IH:9560, 9593). Support is computable from the arrays and parameter roles: [F:2185](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/fitting.py:2185).

   Area semantics need an explicit decision: the server uses trapezoidal integration, F:2705; the page uses a rectangular rule with the first grid spacing, [IH:9469](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:9469). Moving both readers behind one accessor does not select one definition.

   **Required:** define which parameter/curve relationships and derived quantities the proof verifies, and which evidence is merely attributed to the producing engine. The explicit uncertainty limitation is an improvement; it does not cover these other omissions.

5. **MAJOR — the local-engine output and verification contracts remain inconsistent.**  
   **Round-1 local-engine finding: partially resolved.**

   The separate local R recipe is appropriate. But [D:518](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:518) defines O as the whole response verbatim, followed by universal checks requiring server-shaped arrays, parameter metadata and `background_verdict`.

   [`runFitLocal` returns](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:9429) only success, engine, iteration counts, reduced χ² and certification restart count. Its curves, final parameters and other statistics are committed elsewhere. It has neither the specified server O nor server-style `params[].vary/expr`.

   Local arithmetic also consumes the supplied net array directly and reconstructs counts for weights (IH:9078, 9175). That distinction must survive normalization.

   **Required:** define engine-specific O schemas and validation branches, including local energies, exact net/background inputs, varied-parameter inventory, final curves, certification evidence and `reportable:false`. Reconcile this explicitly with the earlier local-seal amendment.

6. **MAJOR — executable provenance is improved but still not uniquely identified.**  
   **Round-1 runtime-identity finding: partially resolved.**

   [D:511](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:511) adds numerical-library versions and a browser build hash, resolving substantial omissions. But `{commit, dirty:true}` does not identify dirty backend contents: different implementations can have identical recorded environments.

   Nor does a checkout identity necessarily identify loaded Python code; deployment explicitly serves frontend files from disk while backend changes require restarting workers ([DEPLOY.md:31](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/DEPLOY.md:31)).

   **Required:** identify the executing backend artifact, or explicitly withhold PROVENANCE-COMPLETE for unidentified/dirty executions. Otherwise “same software” remains stronger than the recorded evidence supports.

The remaining round-1 dispositions are:

| Round-1 issue | Revision-2 disposition |
|---|---|
| False/overstated VERIFIED claims | Corrected: names, precision, loaders, tested-case parity, numerical ignoring of iterations, relative improvement, restore tolerance/checks, identity-test status and key/certificate chronology. |
| Server replay inputs | The explicit computational inventory is now covered: parsed inline arrays, order, starting specs, overlays, links, background arguments, run settings, seed and resolved configuration. No additional HTTP numerical input omission found. |
| Original request versus fitted model | Correctly separated structurally; finding 1 prevents full closure. |
| Transforming replay inputs | Resolved by preserving R’s frame. Display mapping still needs the checks above. |
| Global-method acceptance | Resolved by retaining and requiring `success`. |
| Invalid page/server evaluator bound | Removed from chart rendering; finding 4 identifies the remaining parameter/curve obligation. |
| Replay disagreement treated as stale | Resolved. Replay is appropriately separate from currency. |
| Duplicate certificate and extra fit key | Resolved at schema level. |
| Legacy policy | Consistent, with keyed-unsealed handling correctly identified as a tightening. |
| Incomplete retirement/migration list | The named round-1 additions are covered, including history, alternatives, legacy fields and operation-token separation. |

Some hypotheses can now be narrowed:

- **Server `n_free` is recoverable:** for the current model construction, count actual returned parameter entries with `vary === true` and no expression, excluding derived `area`; cross-check against `statistics.n_free_params` and R’s parameter roles. F:2453–2456, 2713–2722 and 2770 establish the inventory.
- **The statistical domain is the entire incoming ROI**, not the background window: F:2340–2365. Weights use original counts, F:2434–2435.
- I independently confirmed **121 saved fit records across seven archives, none with `startsModelKey`**.
- Universal background bit-identity and the exact replay-comparator success fraction remain unmeasured here. Finite fixture coverage supports tested cases, not the universal claim.

Drawing stored O curves has **no inherent conflict** with history, stacks or exports. Those consumers must receive each artifact’s own grid, transform, curves and statistics. History currently evaluates on the active plot grid (IH:11082); stack components are reevaluated (IH:10498). The migration names both paths, which addresses round 1’s omission. However, the stated `sealedState` return signature supplies only a status while claiming to be the only reader of R/O/D; it also needs to expose the validated consumer view.

Two smaller corrections: replay comparison failure alone does not prove a different solution—it can concern restart diagnostics or a failed rerun—and Q3’s “counts only” option conflicts with storing O verbatim. The “before 1e” reference also names no existing ship step.

Validation consisted of source inspection, the archive census and read-only arithmetic/application probes. No full numerical suite or 202-target replay census was performed.

**VERDICT: NO-GO.**
