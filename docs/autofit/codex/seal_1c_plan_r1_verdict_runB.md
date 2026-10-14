**The plan is not ready to build at HEAD `326bd77`.** The frozen seal is a sound foundation, but the proposed compatibility layer does not yet make every displayed value a view of that seal. Auto-Fit verification and provenance also omit requirements retained by V6.22.

This was a read-only review; no code was changed or tests run.

1. **Design coverage: substantial, but incomplete.**

   The plan correctly includes the full request snapshot, verbatim O, a derived projection, exact sample checks, server verification, five states, lossless persistence, and an unsealed-save adapter. Moving `producer` outside R is not itself a problem if it remains part of the immutable seal and selects the builder consistently. See [plan:14](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:14).

   **MAJOR — V6.4 needs one explicit relationship between the duplicated context fields.** The five checks independently use `R.roi` for sample selection and `R.context0` for the live comparison. They do not explicitly require the ROI and shift used for selection to be those of that same context. Nor does the plan state the finite-`R.ccShift` refusal or page-background-effect comparison. A narrower recorded ROI paired with a wider `context0` must fail even if its request, response, and background are internally consistent. Define selection and request reconstruction from one context, then compare its derived indices and arrays with R. The required bindings are at [design:849](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:849); the incomplete checklist is at [plan:44](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:44). Today `_roiSelect` explicitly maps NaN shift to zero, making the separate finite check material: [page:5606](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5606).

   **MAJOR — G6 provenance is missing.** Neither the seal schema nor its view captures the rendered page’s `page_sha256` and `reference_sha256`, or defines `PROVENANCE: attested / incomplete` with missing-field reasons. Keeping `O.software` and calling `_fitRecordFrom(O)` is insufficient: that function only copies server identity. The page meta tag already exists, but the existing local record reads only `xps-software`. See [design:1084](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1084), [page:5](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5), and [page:8836](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8836). V6.22 explicitly keeps this identity provenance; it does not require a server key.

   **MAJOR — the stated 1b prerequisite is not present at this HEAD.** The plan says it was rebased on 1b and that background bit-identity was measured there, but `docs/findings/seal-1b/` is absent and the branch history proceeds from 1a′ into the plan commits. Correct that claim and bring the evidence into the reviewable branch. Q5 measurements do exist separately; this finding does not invalidate those. See [plan:6](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:6), [plan:53](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:53), and the prerequisite at [design:1154](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1154).

   V6.3’s Auto-Fit requirements, V6.7’s local contract, and V6.9’s consumer migration have further gaps below. V6.8’s legacy policy is coherent in principle.

2. **Keeping the helper names is sound; keeping their consumers unchanged is not.**

   **MAJOR — the compatibility view is incomplete.** `_fitResultFromSeal` supplies several old fields, but does not specify the projected model, component curves, `fitted_sub`, residuals, areas, or support accessor required by V6.9. Existing consumers frequently calculate those independently. Merely changing `_statsState` cannot redirect those reads. Compare [plan:32](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:32) with [design:1113](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1113).

   | Consumer | Required change beyond replacing the named helpers |
   |---|---|
   | Chart | Components still evaluate live peaks; raw counts are reconstructed as `bgSubtracted + background`; residuals use raw-minus-envelope; the subtracted envelope uses `fittedY − background`. Supply O’s components, counts, residuals and `fitted_sub` directly. These floating-point associations are not interchangeable. [page:11460](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11460), [page:11517](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11517), [page:11569](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11569) |
   | Results, sidebar, areas, Quantify | Results reads live parameters and recomputes areas; the sidebar does likewise. Route fitted numerical values through projection and O’s areas, retaining live names/colors as presentation. Quantify inherits the area/support choice. [page:10057](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10057), [page:7857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7857) |
   | Header and R panel | Header qualifiers are currently tooltip-only; R can still say “Excellent fit” without a pending/unconfirmed qualifier. Supply the actual state and reason to both. [page:9418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9418), [page:13653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13653) |
   | Uncertainties | O-backed stderr can remain, but `_validateUncertainties` also reads live peaks and `_preFit`; its initial-value view needs replacement, discussed below. [page:13736](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13736) |
   | CSV/XLSX | Parameters and areas still come from live peaks. `_currentSupport`, omitted from the helper list, independently authorizes support using `p.support.fitKey`. [page:13485](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13485), [page:13522](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13522) |
   | TSV | Recomputes background, model, components and residuals regardless of current seal status. [page:13004](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13004) |
   | PNG | Independently selects the live ROI/background and pairs them with a stored envelope based partly on matching length. Both figure data and metadata need the same seal view. [page:13068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13068) |
   | Stack A/A2/B | All paths independently evaluate components; A2/B rebuild the envelope. The entry cache also needs invalidation when verification changes asynchronously. [page:10958](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10958), [page:11006](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11006) |
   | History/undo | History has separate `chi`/`rFactor` copies and displays them without seal state. Restoring the seal does not automatically replace those readers. [page:16083](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16083), [page:16145](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16145) |
   | Alternatives/certificate | Preview ownership still uses `startsModelKey`; missing current evidence is described as “model changed.” Replace identity with the seal and distinguish pending/unconfirmed/stale. Certificate and starts claims also need attribution. [page:8785](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8785), [page:8980](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8980), [page:8953](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8953) |
   | Saves/loaders | Require explicit sealed-versus-legacy branches; see answer 5. |

   **MAJOR — `_currentSupport` is a concrete missed authority.** It can return a matching old peak verdict without consulting the seal or verification status. Rewrite it alongside `_isUnsupported`; otherwise exports can report “supported” during UNCONFIRMED, or lose support altogether if the old keys disappear. [page:7841](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7841).

   Displaying recorded numbers during PENDING/UNCONFIRMED is allowed by the design. The failure is presenting them without their state, or pairing them with separately recomputed values. Also retain the full state internally: both states map to `'unverified'`, while `_refreshStatsState` currently decides whether to repaint using only that string. A PENDING→UNCONFIRMED transition can therefore leave the old explanation visible. [page:8734](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8734).

   **MINOR — specify compatibility field types.** The server’s `r_factor` is a nullable ratio; the page expects `{rPct, level}`. Derive that presentation wrapper without recalculating R, and preserve zero. [fitting.py:3020](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/fitting.py:3020), [page:13653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13653).

3. **Producers: Run Fit and Use this solution have sufficient proposed inputs; Auto-Fit and local need stronger contracts.**

   Run Fit’s proposed R can reproduce its request if captured before the first await. For Use this solution, it must capture `opts.startPeaks`, not the still-live model, and preserve `chosenAlternative` as attributed adoption history. The current producer already distinguishes these inputs: [page:9137](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9137), [page:9088](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9088). Full-precision upload is already implemented: [page:6995](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:6995).

   **BLOCKER — Auto-Fit’s E is stored but not made a prerequisite of CURRENT or commit.** “Its gates re-derivable” does not implement the retained requirements:

   - Bind R₁ to the same raw spectrum and reconstruct its request.
   - Verify O₁, require its recorded positive acceptance, and re-evaluate the anchor gates.
   - Derive the shift, moved anchors, endpoint rounding, locks and final context; require exact equality with R₂.
   - Verify O₂ and its final anchor gate before committing.
   - Keep both fits and verifications under one operation; rollback on verification failure while still owner.

   These requirements are explicit at [design:815](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:815). The plan’s CURRENT checklist verifies only `{R, O}`, and “every fresh fit PENDING” does not explain Auto-Fit’s deferred commit: [plan:28](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:28), [plan:56](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:56). Today the final response is published immediately after its existing gates, so those verifications require actual transaction changes: [page:8518](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8518).

   **MAJOR — local/Batch R, projection and verification are underspecified.** Batch sends no wire request. Local O uses `energies`, `modelSum`, `chi2`, etc., while the proposed common view expects server fields such as `energy`, `fitted_y` and `statistics`. Define engine-specific request capture, projection, verification and view adapters. Local verification must bind held values, links and `paramMap` to the recorded starting model, not merely recompute mutually consistent numbers from an arbitrary final model. Capture each Batch target after scaling and context propagation. See [plan:81](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:81), [page:9484](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9484), and [page:14256](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14256).

   Persist local background metadata as ordinary object fields: its current certificate/effect are non-index array properties that JSON omits. [page:5173](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5173).

4. **Mutators and shallow copies: the direction is correct, but the implementation boundary is incomplete.**

   Stopping `_invalidateBgCache`, `_invalidateFittedY`, `_restampSupport` and lazy R calculation from changing sealed views is explicitly planned and correct. Sharing a deeply frozen seal across snapshots is also explicitly permitted by the design. [plan:37](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:37), [design:986](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:986).

   **MAJOR — retiring `_preFit` without a derived replacement changes uncertainty rules.** The proposed view omits it, while rule 2 relies on it to detect a free parameter that barely moved and has no stderr. Derive the initial-value map from R’s actual starting model, including alternative starts; do not silently fall back to `{}`. [page:13744](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13744), [page:13798](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13798).

   The plan should explicitly say that sealed loads bypass `_restoredFitBgFailure`: it overwrites grids/backgrounds and clears evidence. Merely freezing the seal does not stop it replacing fields on a mutable view. [page:10562](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10562).

   Ordinary undo snapshots currently save peaks, not a fitResult; only contextual snapshots carry one. History and Auto-Fit snapshots carry shallow views. Define whether each restore reinstalls a captured seal or retains the current seal and becomes stale; “share the seal” alone does not specify this. [page:2400](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:2400), [page:2503](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:2503), [page:7586](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7586).

5. **Saves/loaders: achievable, and Q1 is coherent, with an explicit format boundary.**

   A project’s `{seal}` can replace its current rounded fitResult. A spectrum file needs a larger change: today it writes top-level `statistics`, `roiBE`, `background`, `fittedY`, residuals and component curves; its loader constructs authority from those fields. The new loader must prefer and validate the seal before entering that reconstruction path. Any retained convenience arrays must be derived exports that the sealed loader ignores. [page:12361](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12361), [page:12289](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12289), [page:12618](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12618).

   Keep the saved live model/context separately: a user can save edits beside an older seal, and reload must judge that relationship rather than overwrite the edits with the projected fit.

   **MAJOR — legacy provenance retention is only half specified.** The plan stores `tab.provenance` after reconstruction fails, but existing serializers and Results do not read that field. It must survive re-save/reload and remain visible when `fitResult` is null; otherwise the next save loses exactly the record V6.8 requires retaining. [plan:96](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:96), [page:12394](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12394), [page:9987](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9987).

   The legacy adapter can retain today’s reconstruction and stale reasons while imposing a separate, permanent “unsealed—never current” ceiling. Do not erase old keys before reconstruction: that machinery uses them as historical evidence. `.fit.json` should remain parameter-only with provenance, as planned.

6. **Verification timing/ownership: correct principle, incomplete lifecycle.**

   **MAJOR — load/activation scheduling does not cover every installation and consumer.** Specify one verification manager invoked on fresh installation, load, history/undo restoration when verification is unavailable, and stack-source use. Loading directly into a stack currently need not activate any source spectrum, so “others on activation” can leave every source indefinitely PENDING. The existing stack resolves source records directly: [page:10944](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10944). History restore also installs its result directly: [page:16229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16229).

   The manager needs explicit rules for:

   - Owner **object**, whole-seal identity, operation token and verification-attempt identity.
   - Discarded requests becoming retryable rather than leaving permanent PENDING.
   - A late response never replacing a newer attempt’s result.
   - Rechecking live bindings before display, even when numerical verification is cached.
   - Refreshing Results, header, support, Quantify, history and stack caches when state/reason changes.

   The existing fit-operation machinery can support this, but load/restore checks have no producing fit operation automatically: [page:8138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8138). Auto-Fit additionally needs the transaction described in answer 3.

7. **Visible changes: §7a is not exhaustive.**

   **MINOR — expand the release-change list** to include:

   - Alternatives’ parameter sets and controls surviving reload, rather than only saved counts.
   - Verification-dependent support badges, percentages and Quantify results; explain how recorded support is presented while unconfirmed.
   - Auto-Fit waiting for verification and rolling back if it cannot confirm either prerequisite fit.
   - Provenance completeness labels, including peaks-only legacy restores.
   - Seal-driven component curves/residuals/areas replacing page recomputation, including export differences.
   - The chosen stale-preview behavior after invalidators stop clearing cached backgrounds.
   - Larger saves from full responses, alternatives and Auto-Fit anchor evidence.

   These follow directly from [plan:24](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:24), the current counts-only saver at [page:8794](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8794), and the consumer changes above.

   “After ANY deploy” is too broad. A verification reports different software when the recorded software identities differ; an identical redeploy need not change them. The owner already accepted this rule in Q6. Describe its actual trigger rather than reopening the accepted policy. [fitting.py:84](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/fitting.py:84), [design:1330](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1330).

8. **Suggested sequence within the one branch.**

   1. Correct the plan and attach the missing prerequisite evidence. Define server/local schemas, context bindings, provenance, Auto-Fit derivation, and the complete view contract.
   2. Extract pure request builders and projection functions; keep existing behavior through wrappers. Test request identity, links, locks and alternative starts.
   3. Add immutable seal creation and local O finalization in parallel with existing output. Compare derived views against producer outputs without changing displayed authority yet.
   4. Add `sealedState` and the verification manager, including Auto-Fit’s two verifications. Test delayed responses, supersession, close/reload with reused tab IDs, history restoration and stack sources.
   5. Migrate consumer groups to the full view while the legacy adapter still supports existing results: chart/stack; Results/sidebar/Quantify; uncertainties/evidence/history; exports. Include `_currentSupport` and all independent numerical calculations.
   6. Add both lossless serializers and the shared sealed loader, with early sealed/legacy dispatch and provenance persistence. Test fresh, stale, pending, unconfirmed and peaks-only round trips.
   7. Enable sealed installation for every producer, remove sealed-path mutators and old authorities, then run the browser matrix and legacy census. Keep intermediate switches internal so each commit remains testable.
   8. Complete the visible-state wording, release measurements and unit 1d before the planned release.

   Add negative tests beyond the plan’s happy-path round trips: wrong-spectrum E, inconsistent R/context ROI, missing provenance, pending support exports, stale convenience arrays beside a valid seal, local held-value mismatch, and verification completion while a stack is active.

**VERDICT: NO-GO.**
