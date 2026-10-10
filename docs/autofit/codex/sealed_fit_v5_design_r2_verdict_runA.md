# Sealed fit record v5 design — Codex gate round 2, run A (commit 4ff4fa0)

The revision resolves much of round 1, but **the display-current proof remains unsound**.

Reviewed HEAD `4ff4fa0` against main `90651e6`; the differences are documentation only. No files changed.

1. **BLOCKER — `applyBackendResult(O)` is not an independent reconstruction of D.**

   [V5.4 step 3](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:555) requires rerunning it and comparing exactly. But the function mutates existing peaks, finds them through global state, preserves locked values, and does not reconstruct shapes, links or locks from O. See [IH:6969](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:6969).

   A read-only probe using the actual function confirmed: displayed center `99`, `fixCenter=true`, response center `10` → reapplication leaves center `99`. D and live state can agree exactly while disagreeing with O.

   Links make this more than a hypothetical corrupted-record case: the server derives linked parameters through expressions regardless of some frontend locks, while application still honors those locks. See [F:1518](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/fitting.py:1518). Auto-Fit additionally shifts and locks centers *after* application.

   **Required:** define a pure projection from recorded inputs/output and an explicit producer-specific display policy. Validate returned parameter values—including locked and linked values—independently of D. Reapplying onto D and checking a fixed point is circular.

2. **BLOCKER — R, O, D and the displayed data are insufficiently connected.**

   [Steps 1–4](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:542) compare energies but never require **`O.counts === R.counts`**. They also never establish that D’s background context, ROI/sample mapping and charge transform correspond to R.

   Concrete counterexample: with background `none`, substitute a response from different counts on the same energy grid and with the same component IDs/shapes. Its curves, residuals, statistics and acceptance flags can be internally consistent; today’s background is still zero. All stated checks can pass despite R describing different data.

   Drawing O’s model curves does not solve the raw-data binding: today’s raw-view data trace uses the live full spectrum, [IH:11049](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:11049).

   **Required:** exact request/response count correspondence; a checked mapping from recorded samples to displayed data; and a validated R→D context/frame relationship. Merely recording the index list and transform does not verify them.

3. **BLOCKER — removing evaluator comparison also removed parameter-to-curve verification.**

   Step 1 checks component IDs/shapes and the sum of their stored curves. Step 3 applies parameters and draws those stored curves. **Neither checks that a component’s parameters describe its `y`.**

   Change only `O.individual_peaks[i].params.amplitude.value`, construct D from it, and leave all curves/statistics unchanged. Every stated check can pass. The parameter table then describes a different amplitude from the plotted component.

   Drawing O eliminates the *cross-language rendering* comparison, but it does not establish O’s internal parameter/curve consistency. This is a new hole introduced by the restructuring and a surviving form of round 1’s output-model binding blocker.

   **Required:** define how that relationship is validated, or explicitly narrow the claimed proof and treat those parameters as unverified reported metadata. Areas and support statistics also need stated treatment; σ is currently the only explicit exception.

4. **MAJOR — the statistics contract still rejects valid output and contains a false code claim.**

   [D:545](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:545) says `residuals = counts − fitted_y` “exactly as the server forms it.” The server actually computes:

   ```
   y_sub     = counts - background
   fitted_y  = fitted_sub + background
   residuals = y_sub - fitted_sub
   ```

   See [F:2428](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/fitting.py:2428), [F:2689](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/fitting.py:2689), and [F:2774](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/fitting.py:2774).

   A read-only arithmetic probe with counts `1000.1`, background `900.2`, fitted-subtracted value `99.8` produced:

   | Expression | Residual |
   |---|---:|
   | Server association | `0.0999999999999801` |
   | Proposed exact check | `0.10000000000002274` |

   Further unresolved details:

   - **`fitted_sub` is not returned.** Specify its reconstruction or preserve it; subtracting background from `fitted_y` does not necessarily recover it exactly.
   - **γₙ for the final sum is insufficient by itself.** The analysis must include formation of residuals, weights, squares, divisions and square roots, including cancellation.
   - **RMSE has no stored O counterpart:** main derives it on the page, [IH:8847](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:8847).
   - **Null/zero cases need definitions:** R-factor is `null` when its denominator is zero. Installed lmfit also floors reported χ² after computing reduced χ²; literal recomputation needs those semantics. See [lmfit:312](/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py:312).

   The **n_free hypothesis can be settled now**: O exports `vary` and `expr` for model parameters. Count independent varying parameters, exclude the synthetic `area` entry, and verify `statistics.n_free_params`. See [F:2713](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/fitting.py:2713). Statistics use the **entire incoming ROI**, not the background anchor window; the weights use raw counts.

5. **MAJOR — local/Batch R is distinguished, but local O and its proof remain undefined.**

   [V5.3](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:514) gives local fitting its own replay recipe, yet O remains “the whole response, verbatim” under a server-shaped schema.

   `runFitLocal` returns only success, engine, iteration counts, reduced χ² and certificate-restart count, [IH:9429](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:9429). It does not return the arrays, parameter metadata or background verdict required by V5.4. Its fitted peaks and other statistics are written separately to state.

   Consequently, the proposed literal O cannot pass the common proof, despite V5.4 explicitly allowing local DISPLAY-CURRENT.

   **Required:** define local output capture, its parameter-role/count metadata, arithmetic, acceptance evidence and display projection. Preserve its nonreportable designation. The earlier local-LM amendment establishes intent, but does not resolve this new schema conflict.

6. **MAJOR — executable provenance is improved, but dirty builds remain unidentified.**

   [R’s environment](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:511) records commit plus a dirty flag. Two different modified backends can share the same commit, dirty flag and library versions. That record cannot identify which implementation produced O, yet [PROVENANCE-COMPLETE](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:571) permits it.

   Record an actual loaded build identity tied to recoverable source/artifacts, or classify such dirty executions as provenance-incomplete. This part of round 1’s runtime-identity finding remains unresolved.

The round-1 dispositions are:

| Round-1 finding | Revision-2 disposition |
|---|---|
| False claims about names, rounding, loaders, twins, iterations, certificate improvement and keyed-save chronology | **Resolved.** No remaining false claim found in the revised V5.1/V5.2 inventory. The new residual claim is false, as above. |
| Digest-only data, wrong charge frame, missing starting specs/Auto-Fit overlays | **Resolved for the server input inventory.** Inline parsed arrays and as-sent specs cover the numerical arguments of the ordinary HTTP fit path. |
| Starting request confused with fitted state | **Conceptually resolved; proof incomplete** because of finding 1. |
| Transforming replay inputs | **Resolved.** Keeping R unchanged is correct; validating the display mapping remains necessary. |
| Statistics unverified | **Partially resolved:** findings 2–4 remain. |
| Missing global-method acceptance | **Resolved** by requiring `success`. |
| Invalid cross-language evaluator bound | **Removed from rendering**, but finding 3 replaces it with a missing consistency check. |
| Replay disagreement treated as stale; reproduction rate overstated | **Resolved.** Separate replay status and the explicitly unmeasured rate are appropriate. |
| Local-engine recipe and executable provenance | **Partially resolved:** findings 5–6. |
| Legacy policy and rationale | **Resolved.** I independently recounted 121 fits across seven archives, all keyless. Q1 is a coherent, explicitly stated tightening. |
| Duplicate certificate/key authority and mixed migration | **Substantially resolved** by one certificate, D replacing the key, and a simultaneous consumer switch. |

There is **no inherent conflict** between stored O curves and history, stacks or exports. Each consumer must use the relevant seal’s own samples, frame and curves. The revised migration explicitly includes these paths. Alternative previews need a separate contract because their parameter sets do not include stored component curves.

**MINOR migration omission:** add the parameter-only `.fit.json` save/import and `modelProvenance` explicitly. That save still serializes keys, certificate notices and statistical designation at [IH:11676](/Users/skyefortier/xps-app/.claude/worktrees/sealed-design/templates/index.html:11676); “both saves” currently names only spectrum/project persistence. Define what survives without a full seal.

The background-universality and replay-fraction claims properly remain hypotheses. Finite parity tests support the tested domain; they cannot establish universality by themselves. No reproduction census was run here.

The remaining design-rule violations are concrete competing readings: locked page values versus returned parameters, stored parameters versus stored curves, unconnected R/D contexts, and differently associated residual arithmetic. Derived error bounds are defensible, but the current statistics paragraph has not derived the bounds it requires.

**VERDICT: NO-GO.**
