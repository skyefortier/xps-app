**Revision 2 closes most round-1 findings, but five substantive gaps remain.** The largest is that the local verifier can establish internal consistency without establishing that its statistics describe R’s data.

Read-only review of HEAD `68f6486`, branch `seal-1c-page`. No files changed or tests run. I have treated 1b as an outstanding prerequisite, not as missing evidence that independently fails this review.

**1. Design coverage and the §13 answers**

The revised architecture is substantially aligned with V6.22: immutable R/O/D/E, exact request reconstruction, projected parameters, numerical verification, qualified recorded acceptance, and no key machinery. The provenance label remains an identity claim, as the approved design permits. See [design:1322](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1322).

I checked each entry in [plan §13](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:279):

| Round-1 finding | Round-2 assessment |
|---|---|
| Auto-Fit E and verification before commit | Substantially answered; final positive acceptance still needs an explicit condition—finding F2 below. |
| Independent consumer sources | Full numerical migration now specified; local designation and parameter-file provenance still need migration—F3. |
| Incomplete bindings/context/key | Sample, shift, link, background-effect and display-frame bindings answered; live method persistence remains incomplete—F4. |
| Provenance absent | Answered by `R.page` and §8.3. |
| 1b evidence absent | Correctly marked prerequisite; no finding for its present absence. |
| PENDING/UNCONFIRMED presentation and repaint comparison | State matrix and full-state comparison answer the original finding. |
| `_currentSupport` omitted | Explicitly included. |
| Local/Batch contract | Improved, but still incomplete—F1. |
| `_preFit` replacement | Answered by `view.initialValues`. |
| Mutators, structural dispatch, snapshot semantics | Answered in §8.1–8.2. |
| Persistence and legacy provenance | Mostly answered; new live context is not fully persisted—F4. |
| Verification ownership/retries | Partially answered—F5. |
| Visible changes and R-factor adapter | Original omissions substantially answered; small additions below. |
| Sequencing | Sound overall; refinements in answer 8. |

The retained V6.2–V6.9 requirements therefore are **not yet completely implemented by the written plan**. The remaining issues concern local data binding, Auto-Fit acceptance, consumer migration, context persistence, and verification lifecycle—not the withdrawn attestation protocol.

**2. Consumer machinery**

Keeping the helper names is sound **with the explicit consumer migrations now in §7**. Merely replacing their implementations would still be insufficient, but revision 2 no longer proposes only that.

The numerical coverage now matches the current bypasses:

| Consumer | Assessment against current code |
|---|---|
| Chart | Covered: replace reconstructed counts, live components and separately associated residual/envelope calculations. [page:11462](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11462) |
| Results, sidebar, areas, Quantify | Covered: projected parameters and O’s areas/support replace independent evaluation. [page:10057](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10057), [page:7857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7857) |
| Header, R panel | Covered by explicit state wording and the nullable R adapter. The existing header needs that change. [page:9421](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9421) |
| Uncertainties | Covered: model, stderr, support and initial values all have specified replacements. [page:13736](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13736) |
| CSV/XLSX | Covered, including `_currentSupport`. [page:13485](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13485) |
| TSV and PNG | Covered: both currently construct independent numerical data. [page:13004](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13004), [page:13068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13068) |
| Stack A/A2/B | Covered numerically by a source-view branch; verification completion also needs the lifecycle correction below. [page:10958](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10958) |
| History/undo | Separate history statistics and preview calculations are explicitly migrated; snapshot ownership is addressed. [page:16083](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16083) |
| Alternatives/certificate notice | Seal identity and differentiated state wording address the previous independent key. [page:8785](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8785) |
| Project/spectrum saves and loaders | Structural migration specified; context caveat in answer 5. |

PENDING/UNCONFIRMED may legitimately show recorded numbers and apply recorded support exclusions. The plan now specifies their qualification and prevents their status from becoming `'current'`. That resolves the original ambiguity. [plan:103](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:103)

**F3 — MAJOR: local designation and `.fit.json` remain outside the concrete adapter contract.**

The proposed fitResult contains only `{seal, view}`, while `_isLocalFit` currently reads top-level `engine`/`objective`. `_provenanceOf` also reads top-level fields. Leaving these helpers unchanged makes a sealed local result lose its starting-point designation in Results, Quantify, stacks, history and copied models. The plan says the designation is “unchanged,” but neither its view inventory nor its helper migration specifies the replacement. [plan:149](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:149), [plan:189](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:189), [page:9337](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9337), [page:9391](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9391).

Likewise, `.fit.json` is called “unchanged,” but `_doSaveFit` reads `fr.record`, `fr.engine`, `fr.chiReduced`, etc.; those disappear under the proposed shape. Its importer reads `fitStatistics`, not a newly introduced top-level `modelProvenance`. [plan:208](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:208), [page:12181](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12181), [page:3510](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3510).

Specify engine/reportability in the view, migrate the designation/provenance helpers, and explicitly route parameter-file serialization through that view. The Batch summary is another direct numerical reader worth naming: it currently uses `outcome.chiReduced`; require that return value to derive from the finalized local O. [page:14324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14324)

**3. Producers and step 0**

Run Fit and “Use this solution” now have sufficient proposed input capture. Capturing `opts.startPeaks` separately from the live ownership model is correct, and preserving omitted fields versus explicit null is necessary. The extraction must preserve the requests currently built at [page:9137](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9137) and [page:9170](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9170).

**F1 — BLOCKER: local O is not fully bound to R.**

Section 6.4 verifies curves on **`O.energies`**, then statistics/support in the engine’s arithmetic. It does not require:

- `O.energies === R.energies`;
- `O.net[j] === R.counts[j] - O.background.values[j]`;
- `O.weights[j] === 1 / sqrt(max(O.net[j] + O.background.values[j], 1))`.

Section 2 explicitly binds the server’s O arrays, but supplies no equivalent local identities. A local record with a different net signal and correspondingly recomputed statistics can satisfy the listed checks while R remains correctly bound to the tab. That permits CURRENT statistics for different data. [plan:55](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:55), [plan:142](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:142)

The exact association matters: today’s local engine deliberately forms weights from **net + background**, and residuals from **net − model**. [page:9474](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9474), [page:9599](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9599). V6.7 retains these requirements. [design:1070](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1070)

Make step 0 engine-specific: server request reconstruction versus local input/inventory reconstruction. Currently §2 universally requires `R.request`, while §6.4 explicitly omits it. Also resolve §4’s claim that linked fields equal the starting snapshot: linked fields must follow their **final parent**, as §6.4 and the current engine correctly say. [plan:85](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:85), [page:9585](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9585)

Batch’s target-specific capture after propagation/scaling is otherwise correct.

**F2 — MAJOR: Auto-Fit’s final positive acceptance is absent from the stated predicate.**

The revised transaction explicitly requires `O₁.success === true`, but for O₂ requires only consistency and the anchor gate. Those do not establish positive recorded acceptance: the verifier does not recompute success, and `_autoFitAnchorRefusal` does not check it. The current producer separately checks `json2.success !== true` before applying the final fit. [plan:131](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:131), [server plan:57](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-13-seal-1a-server.md:57), [page:7912](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7912), [page:8512](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8512).

Explicitly require `O₂.success === true` at commit **and when judging a restored Auto-Fit seal**. V6.3 requires the final fit to be accepted and verified. This reads acceptance as recorded; it does not restore attestation. [design:827](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:827)

The same-spectrum E binding, exact R₁/O₁→R₂ derivation, two verifications, rollback and supersession rules otherwise answer round 1.

**4. Mutators and shallow copies**

**Yes, the revised approach handles the named mutators.** Freezing both seal and view, making invalidators/restamping/lazy R calculation no-ops for sealed results, and structurally excluding sealed results from legacy reconstruction are the right boundaries. These directly address the current writes at [page:5042](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5042), [page:7851](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7851), [page:3324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3324), and [page:10570](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10570).

The snapshot distinction is now explicit and coherent: peak-only undo retains the installed seal and rejudges; contextual undo/history/rollback reinstalls the captured seal. Sharing immutable references is safe. Preserve the rule that all these installations use the same verification lifecycle. [plan:194](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:194)

**5. Saves, loaders and legacy**

“The seal whole, nothing else authoritative” is achievable in both formats. The explicit early dispatch, ignored spectrum convenience arrays, stale workspace preservation, and separately persisted legacy provenance answer the original structural concerns. The legacy adapter can preserve today’s reconstruction decisions while imposing Q1’s permanent never-current ceiling.

**F4 — MAJOR: the newly bound method has no specified workspace lifecycle.**

The plan binds fit method and promises that changing it makes the fit stale, but saves the workspace “as today.” Today `_captureUI` and `_restoreUI` omit method; both formats persist that incomplete UI object. The dropdown also has no fit-state change handler. [plan:72](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:72), [plan:202](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:202), [page:3904](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3904), [page:1898](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:1898).

Consequences include:

- An unedited fit made with a nondefault method reloading against a different method.
- A stale save losing the method edit that made it stale.
- Inactive tabs being judged using another tab’s dropdown.
- A method edit leaving already-rendered CURRENT values visible until another refresh.

Specify method capture, per-tab restoration, serialization, defaults, and immediate state refresh. Define an owner-aware context reader for inactive tabs and snapshots. Do not repair this by restoring live context from R: that would erase intentionally saved edits.

**6. Verification timing and ownership**

**F5 — MAJOR: §9 does not implement all the retained ownership and retry rules.**

The whole-seal cache, attempt identity, all-tab load scheduling and stack-cache invalidation are improvements. However, “owner still holds the same seal” is insufficient:

- A newer fitting operation can start while the previous seal remains installed. The previous verification still passes §9’s attachment test.
- A closed tab object can still hold its seal; object identity alone does not establish that the owner remains in `tabManager.tabs`.
- Activation is not a verification/retry trigger, and discarded attempts have no explicit cleanup/retry rule.
- The refresh list omits the main chart; clearing stack caches alone also does not require repainting an already-visible stack.

See [plan:216](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:216). Existing code already distinguishes owner liveness and operation currency: [page:2379](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:2379), [page:8157](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8157). The retained design explicitly requires superseded-operation replies to be discarded. [design:986](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:986)

Use separate ownership rules for producer-bound checks and background load checks. A load check should not claim a fit operation, but a producer check must retain its existing operation token. Define activation/reinstall recovery, clear discarded in-flight attempts, and explicitly repaint affected charts. Reconcile the test expecting tab-switch discard with intentional verification of inactive loaded tabs.

**7. Visible changes**

The former §7a is now §10. Its expanded list answers almost all round-1 omissions.

**MINOR:** add these consequences explicitly:

- Method becomes a persisted per-tab setting once F4 is fixed.
- The “check again” control mentioned in §9.
- Uncertainty movement warnings can reappear after reload because initial values now survive; adopted alternatives also use their actual start.
- Historical previews use their recorded grid/background rather than today’s chart grid/background. Today they are reevaluated on `plotBE` and `plotBG`. [page:11581](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11581)

Also correct §10’s measurement pointer: it says §12 step 9, while release measurements are step 8. [plan:227](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:227)

**8. Sequence within the branch**

Keep the proposed sequence, with these refinements:

1. Resolve F1–F5 and incorporate/review 1b before proceeding past the prerequisite step.
2. Extract pure builders, projection, Auto-Fit derivation and owner-aware context capture. Add method persistence and change notification.
3. Build immutable seals, complete local finalization, validation and views alongside existing production output.
4. Implement verification ownership, retries and state transitions behind the switch.
5. Migrate consumers by group, including local designation, provenance helpers, `.fit.json`, Batch summaries and chart refreshes.
6. Add project JSON/ZIP and spectrum serializers/loaders, preserving edited workspaces and legacy evidence.
7. Enable Run Fit/Use Solution, then local/Batch, then Auto-Fit. Each enablement gets its producer-specific round trips and negative checks.
8. Remove sealed-path old authorities; run the legacy census and full browser matrix; finish visible wording and measurements.
9. Complete 1d and review the combined release before deployment.

Add focused negative cases for local net/grid/weight mismatch, `O₂.success:false`, nondefault and edited method round trips, local `.fit.json` designation, and a superseded verification while its seal is still installed.

**VERDICT: NO-GO.**
