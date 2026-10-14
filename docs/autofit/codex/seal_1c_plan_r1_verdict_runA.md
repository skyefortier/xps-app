**The plan needs revision before implementation.** The frozen seal and derived compatibility view are sound choices, but the specified CURRENT predicate omits Auto-Fit prerequisites, and replacing the existing status helpers does not eliminate the page’s other numerical sources.

This was a read-only review of HEAD `326bd77`; no files changed or tests run.

**1. Coverage of V6.2–V6.9**

The plan covers the basic R/O structure, request reconstruction, sample selection, backend projection, numerical verification, five states, local output inventory, and the intended migration. Deriving engine/reportability instead of duplicating them in D is reasonable **if the derivation is explicitly specified**.

Three substantive gaps remain:

- **BLOCKER — Auto-Fit evidence is stored but not judged.** E appears in the schema, but none of the five CURRENT conditions checks E. The design requires R₁’s bindings against the same raw spectrum, O₁’s verification and positive recorded acceptance, the anchor gates, and exact derivation of R₂’s model/context from R₁/O₁. A valid final fit paired with unrelated or inconsistent anchor evidence could satisfy the plan’s stated predicate. See [plan:28](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:28), [plan:44](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:44), and [design:815](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:815).
- **MAJOR — The explicit page-binding contract is incomplete.** Add finite-shift refusal, seal link-graph validation, the relationship between `R.roi`/`R.ccShift` and the recorded/live context, the final display-frame equality, and the background-effect equality. Reusing `_startsLiveKey()` does not cover all recorded context: its key excludes fit method, charge-reference fields, and Auto-Fit centre/width overlays; `_captureUI()` does not capture fit method either. See [design:849](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:849), [index.html:8623](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8623), and [index.html:3904](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3904).
- **MAJOR — Provenance is missing as an implemented feature.** `_fitRecordFrom(O)` preserves server software, but does not capture the producing page’s `page_sha256`/`reference_sha256`, classify provenance as attested/incomplete, or explain missing evidence. The meta tag exists; the current software reader reads a different tag. Capture the producing page identity in the seal, preserve it on reload, and expose the required nonblocking provenance verdict. See [design:1084](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1084), [index.html:5](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5), and [index.html:8836](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8836).

Option (b) correctly removes the key machinery. It does **not** remove these requirements; V6.22 expressly preserves them.

**2. Keeping the consumer machinery**

**Sound as a compatibility layer; insufficient as specified.** Keep familiar helper names, but have them consume one complete `{state, reason, view}` result. `_statsState(fr, key)` cannot perform the required sample bindings from a model key alone: its adapters must also supply the owning tab’s raw data and complete context, including for inactive tabs.

**BLOCKER — A status-wrapper replacement leaves independent numerical sources.** The proposed `_fitResultFromSeal` lists statistics and envelope/background fields, but lacks a concrete mapping for projected model values, original counts, component curves, `fitted_sub`, residuals, areas, and support. Those are necessary to replace the following reads:

| Consumer | Current bypass requiring explicit migration |
|---|---|
| Chart | Reconstructs counts as net + background, evaluates live peaks, computes residuals as counts − envelope, and obtains the subtracted envelope by subtracting background again. Use O’s counts, component curves, residuals and `fitted_sub`; these floating-point associations are not interchangeable. [index.html:11462](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11462), [index.html:11517](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11517), [index.html:11569](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11569) |
| Results | Parameter rows read `state.peaks`; areas are recomputed. Fitted rows must read the projected view. [index.html:10057](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10057) |
| Sidebar, Quantify, areas | `_peakArea` evaluates a peak again; `_areaGrid` switches to the live grid for anything other than CURRENT. Returning a new status does not make these read O’s areas. This also reaches Auto-Fit’s 40% warning. [index.html:9907](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9907), [index.html:9950](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9950), [index.html:7721](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7721) |
| Uncertainties | `_validateUncertainties` reads live peaks, `p.support.f`, and `_preFit`. Retiring `_preFit` without deriving its replacement from R changes the movement warning. For “Use this solution”, the correct start is `startPeaks`. [index.html:13736](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13736) |
| CSV/XLSX | Rows read live parameters and recomputed areas. **`_currentSupport` is an additional authorizer omitted from the named wrapper list**; it independently trusts `p.support.fitKey`. [index.html:7841](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7841), [index.html:13487](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13487), [index.html:13522](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13522) |
| TSV | Recomputes background, model, components and residuals from live state; currently only STALE gets a qualification. [index.html:12997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12997) |
| PNG | Uses the live ROI/background and a length-only envelope compatibility check; embeds the existing record separately. [index.html:13068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13068), [index.html:13420](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13420) |
| Stack A/A2/B | A reconstructs counts; A2/B recompute envelopes; all paths recompute components from source peaks. Sealed sources need a complete view branch, including local seals. [index.html:10958](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10958) |
| History | Stores and displays separate `snap.chi`/`snap.rFactor`; preview recomputes peaks on the currently displayed grid/background. [index.html:16083](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16083), [index.html:16145](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16145), [index.html:11581](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11581) |

**MAJOR — PENDING/UNCONFIRMED require presentation changes beyond mapping to `'unverified'`.**

Showing their recorded values is allowed by the design; every `!== 'stale'` condition is therefore not automatically wrong. However:

- Header and Results use the old “saved without a record” explanation; the R panel/status display has no pending/unconfirmed qualification.
- `_refreshStatsState` compares the collapsed state string. PENDING → UNCONFIRMED remains `'unverified'`, so a changed reason need not repaint Results.
- If `_startsIfCurrent` returns null while verification is pending, the panel incorrectly says “The model has changed”.
- If `_isUnsupported` becomes CURRENT-only, pending/unconfirmed fits can regain positions, uncertainties and Quantify inclusion for components their recorded support excludes. Define this policy explicitly; “no σ rule changes” does not resolve it.

See [index.html:8734](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8734), [index.html:9421](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9421), [index.html:8980](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8980), and [index.html:13653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13653).

The alternative preview must remain explicitly unfitted. Replace its `startsModelKey` identity with seal identity, and label certificate/starts/σ evidence as recorded wherever presented.

**3. Producers and step 0**

| Producer | Assessment |
|---|---|
| Run Fit | **Mostly sufficient data inventory.** Capture the entire snapshot/context before the first upload await and derive the actual request with the same pure builder used by step 0. Preserve omitted fields versus explicit fields. Current capture/request sites: [index.html:9132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9132), [index.html:9170](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9170). |
| Use this solution | Explicitly record `opts.startPeaks`, not the still-live model. Keep the live pre-operation model separately for ownership checks. D must retain the chosen-alternative description; uncertainty checks derive their start from R. [index.html:9135](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9135), [index.html:9235](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9235). |
| Auto-Fit | **Insufficient judgment contract**, despite sufficient intended storage. Capture both requests before their awaits, including producer identity inside—or explicitly inherited by—E. Add all E checks and the exact derivation described in answer 1. The existing two-fit path already exists; the additional work is verification and binding, not implementing the second fit again. [index.html:8420](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8420), [index.html:8487](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8487). |
| Local / Batch | **MAJOR — R and projection are undefined for these engines.** Neither executes a server wire request. The plan’s universal server-shaped step 0, background comparison and `_applyBackendParams` projection cannot directly consume `O_local.model/curves`. Define a tagged local input record and local projection/checker, including net/background association, weights, varied inventory, held/link rules and engine options. Batch must capture each target after propagation, using that target’s arrays/context. [plan:81](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:81), [index.html:9455](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9455), [index.html:14308](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14308). |

The local O inventory itself is good. Specify that its background certificate/effect are ordinary serialized fields: currently they ride as non-index array properties and would disappear through ordinary JSON array serialization. See [index.html:5118](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5118).

**4. Mutators and shallow snapshots**

**Mostly addressed, with one important implementation boundary still needed.**

The plan explicitly stops `_invalidateBgCache`, `_invalidateFittedY`, `_restampSupport` and lazy R-factor from rewriting sealed views. Sharing a deeply frozen seal through shallow outer snapshots is safe. The current mutation/snapshot sites match the plan’s inventory: [index.html:5042](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5042), [index.html:7848](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7848), [index.html:3324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3324), and [index.html:7586](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7586).

**MAJOR — Make the legacy/ sealed dispatch structural.** `_restoredFitBgFailure` replaces arrays, adds keys and clears evidence. It must never receive a sealed view, including through either loader or a restore path. See [index.html:10513](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10513).

Also specify:

- The derived view itself is immutable or otherwise protected from writes; freezing only `seal` does not protect mutable copied fields.
- Projection produces mutable editor copies without sharing mutable nested objects with the seal.
- Auto-Fit rollback reinstalls a view from the saved seal.
- Ordinary undo is currently peak-only unless it carries `_context`; define whether it restores a seal or retains the last seal and rejudges the restored model. Do not assume every undo snapshot already contains `fitResult`. See [index.html:2400](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:2400).

**5. Saves and loaders**

**Achievable for both formats, but the plan needs explicit format dispatch and legacy re-save behavior.**

Projects already have `fitResult`; spectra currently have top-level `statistics`, `roiBE`, `background`, `fittedY` and `peakCurves`. Their loader reconstructs a result from those fields. A new spectrum `fitResult: {seal}` therefore requires an explicit sealed branch **before** that reconstruction. See [index.html:12289](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12289), [index.html:12618](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12618), and [index.html:12361](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12361).

**MAJOR — Define these persistence rules:**

- With a seal present, no duplicate curve/statistics field overrides or repairs it; an unusable seal does not silently become a current legacy reconstruction.
- Persist editor peaks/context separately. A stale save must retain both the original seal and the edited workspace, then reload stale.
- Re-saving an unsealed result must preserve its legacy evidence/provenance without manufacturing a seal or silently dropping everything under `{seal: undefined}`.
- Persist and restore `tab.provenance`, including after peaks-only fallback. Today both save schemas persist `modelProvenance`, not the proposed `tab.provenance`.
- Keep `.fit.json` parameter-only with support cleared, as today. [index.html:3498](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3498).

Q1 is coherent with existing reconstruction: the adapter can still decide which curves are displayable while an outer legacy classification prevents CURRENT. But that restriction must reach support, starts, certificate notices and exports as well as `_statsState`.

**6. Verification timing and ownership**

The whole-seal WeakMap and rejection of superseded replies are correct. The lifecycle is incomplete in two places:

- **BLOCKER — Auto-Fit must finish both verifications before committing.** The design requires one transaction spanning both fits and both checks, rollback on unconfirmed/mismatch/failure, and no writes after supersession. “Every fresh fit is published PENDING” cannot apply uniformly to Auto-Fit. Keep its progress overlay until the verified transaction commits. Current publication happens immediately after the final gate. See [design:824](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:824) and [index.html:8518](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8518).
- **MAJOR — Restore/retry ownership is underspecified.** Define verification scheduling on history/undo restore, handling of abandoned PENDING checks, and fresh ownership for loads/activation. Check tab-object identity, installed seal identity and operation/request generation before attaching a reply. Loading/activating a seal must not accidentally claim a new fitting operation and cancel another fit. Existing operation installation has that cancellation behavior. See [index.html:8138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8138).

Stack sources that have not been activated can remain pending, but must display that state. Verification completion must refresh all affected consumers, including cached stack data and pending→unconfirmed reason changes.

No withdrawn key-generation protocol needs reinstating.

**7. Visible changes**

**MINOR — §7a is incomplete and contains unsupported generalizations.** Add:

- Recorded component curves, residual associations and areas replacing browser recomputation; measure the difference against this HEAD. The trapezoid formula and two-fit Auto-Fit already exist here.
- Auto-Fit can roll back because verification is unavailable or unconfirmed, even after both optimizations succeed.
- Pending/unconfirmed behavior of support exclusions, uncertainties, alternative actions, certificate notices and Quantify.
- Edit-preview behavior after invalidation stops clearing stored background/envelope fields.
- Restored alternatives becoming available because O now retains their parameter sets.
- Provenance labels, larger saves, and changed spectrum-file structure.

**MAJOR prerequisite gap:** the referenced `docs/findings/seal-1b/` directory is absent from this checkout, although the plan cites it and claims background bit-identity was measured there. Q5/Q8 findings are present. Bring in the actual 1b evidence or mark it outstanding; do not treat it as completed. See [plan:7](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:7) and [plan:53](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:53).

Two smaller corrections:

- “After ANY deploy” should say “when the verifier’s software record differs”; identical software identity does not become different merely through deployment. [fitting.py:3305](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/fitting.py:3305).
- Define the R-factor adapter explicitly: the server returns a fraction/null; consumers expect `{rPct, level}`. Preserve null and zero correctly. [fitting.py:3020](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/fitting.py:3020), [index.html:13653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13653).

**8. Suggested sub-step order on the one branch**

1. **Complete the contracts and prerequisites.** Resolve the findings above; bring in 1b evidence. Specify tagged server/local schemas, complete view fields, legacy persistence and the state/presentation matrix.
2. **Extract pure builders and projections without changing production behavior.** Pin Run Fit, alternative starts, both Auto-Fit requests, local inputs and background context against today’s builders.
3. **Implement seal validation, page bindings and view construction behind fixture-driven tests.** Include wrong raw data, incomplete/reordered selections, finite shifts, links, contradictory contexts, nullable values and E→R₂ derivation.
4. **Prepare every consumer’s sealed branch and both persistence branches.** Keep existing production inputs on the legacy path until the sealed branches are complete. Test fixture seals across charts, tables, every export, stacks and restores.
5. **Implement verification lifecycle and UI transitions.** Test delayed/out-of-order replies, tab close/reload, supersession, edits, history restore, offline operation and pending→unconfirmed repaint.
6. **Enable Run Fit and Use this solution sealing together with their complete consumer/persistence support.** Round-trip project JSON, project ZIP and spectrum files, including stale and offline saves.
7. **Enable local/Batch seals.** Verify one frozen final snapshot, engine arithmetic, target-specific inputs, no inherited covariance, and persistent starting-point designation.
8. **Enable Auto-Fit seals last.** Keep both fits/checks inside one transaction; test every verification failure, cancellation and supersession boundary, plus one undo/history entry.
9. **Finish migration and release checks.** Remove sealed-path dependencies on old authorizers, run the legacy census including re-save, measure visible changes and file size, and review 1d before release.

This preserves a working page after each step without exposing a seal to only partially migrated consumers.

**VERDICT: NO-GO.**
