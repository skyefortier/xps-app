**Revision 3 resolves most earlier findings, but three MAJOR contract gaps remain.** This was a read-only review of `seal-1c-page`, HEAD `5562201`; no files changed or tests run. Unit 1b is correctly treated as a pending prerequisite, not an independent reason for rejection.

**1. Design coverage and verification of §13**

The architecture now substantially matches V6.2–V6.9: immutable R/O/D/E, request reconstruction, projection, exact bindings, recorded acceptance, provenance, local output, legacy handling, and a complete consumer view. Keeping engine/producer on the enclosing seal is reasonable. The withdrawn key machinery should remain withdrawn. [Design:1322](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1322)

I checked every category in the revision map:

| §13 finding, including round-2 extensions | Revision-3 assessment |
|---|---|
| Auto-Fit E, transaction, both positive acceptances | Evidence predicate answered; verification lifecycle still conflicts with it—M2 below. |
| Independent numerical consumer sources | Answered by the full view and explicit migration table. |
| Sample/context/frame/background bindings | Mostly answered; charge-reference context is removed from the live binding—M3. |
| Provenance | Answered by `R.page` and nonblocking completeness classification. |
| Missing 1b evidence | Correctly marked prerequisite. |
| PENDING/UNCONFIRMED presentation and repaint | General matrix answered; Auto-Fit aggregation remains ambiguous—M2. |
| `_currentSupport` | Explicitly migrated. |
| Local/Batch contract, background metadata, input associations, paramMap | Earlier numerical-input findings answered; final model structure remains insufficiently bound—M1. |
| `_preFit` replacement | Answered by `view.initialValues`, including alternative starts. |
| Mutators, structural dispatch, immutable views, undo semantics | Answered at plan level. |
| Persistence, stale workspace, legacy re-save, `tab.provenance` | Answered. |
| Verification ownership, closed tabs, supersession, retry triggers, repaint | Earlier omissions explicitly addressed; staged Auto-Fit needs a separate ownership rule—M2. |
| Local designation, `.fit.json`, Batch summary | Answered by view fields and explicit consumer rows. |
| Method persistence, owner-aware context, immediate repaint | Answered by §3 and §8.5. |
| Alternatives preview versus adoption | Answered: Preview allowed, Use requires CURRENT. |
| Visible changes, nullable R adapter, measurement pointer | Substantially answered; wording corrections below. |
| Sequencing | Sound overall, with refinements in answer 8. |

The map therefore overstates complete closure for local judgment, Auto-Fit lifecycle, and charge-reference binding. [Plan §13:326](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:326)

**2. Consumer machinery**

**Keeping the helper names is sound, provided §7’s consumer migration is implemented.** Revision 3 now proposes considerably more than replacing status helpers. Its separate state values prevent PENDING/UNCONFIRMED from becoming `'current'`; recorded values and recorded support may still be displayed with their qualification. [Plan:115](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:115)

The named consumer families are covered:

| Consumer | Current bypass that §7 must replace |
|---|---|
| Chart | Live component evaluation, reconstructed counts and independently associated residuals/envelope subtraction. [Page:11460](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11460) |
| Results, sidebar, areas, Quantify | Live parameters, `_peakArea`, and peak-level support. [Page:10057](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10057), [page:7857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7857) |
| Header and R panel | Top-level result fields and old state wording. [Page:9418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9418) |
| Uncertainties | Backend params, live peaks/support and `_preFit`; all have specified view replacements. [Page:13736](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13736) |
| CSV/XLSX | Live parameters/areas and independently authorized support. [Page:13479](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13479) |
| TSV/PNG | Independent ROI, background, model and residual calculations. [Page:12997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12997), [page:13068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13068) |
| Stack A/A2/B | Reconstructed counts/envelope and reevaluated components. Include the downstream background-subtracted envelope calculation, not just `_buildEntryRenderData`. [Page:10958](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10958), [page:11155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11155) |
| History/undo | Separate snapshot statistics and preview evaluation on today’s grid. [Page:16083](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16083), [page:11581](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11581) |
| Alternatives/certificate notice | Old key identity and shared display/adoption gates. [Page:8940](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8940), [page:9033](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9033) |
| Saves/loaders and local designation | Explicitly included, including `.fit.json` and Batch’s returned statistic. [Plan:198](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:198) |

I found no additional consumer family missing from the revised table. These are migration obligations: leaving those implementations unchanged would still leave second sources.

**3. Producers and step 0**

Run Fit and “Use this solution” now capture sufficient inputs. Using `opts.startPeaks` for the latter, while retaining the live model separately for ownership, matches the current producer. The shared builder must preserve field absence and exact request readings. [Plan:136](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:136), [page:9132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9132)

Auto-Fit now records sufficient evidence and explicitly requires both positive recorded acceptances, both verifications, same-spectrum E bindings, gates, and exact derivation into R₂. That closes the earlier acceptance omission; M2 concerns how those requirements execute.

**M1 — MAJOR: local judgment still accepts the final model’s structure from O rather than deriving it from R.**

The new equalities correctly bind energies, net signal, weights and `paramMap`. But local projection remains simply `O.model`, with checks for held numerical values and linked values. There is no explicit equality for component membership/order, shapes, lock flags, link structure, or other non-optimized model fields. [Plan:67](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:67), [plan:96](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:96)

A concrete counterexample to the listed checks is an all-free Gaussian in `R.pageModel`, but a Lorentzian in `O.model`, with O’s curves/statistics consistently calculated for that Lorentzian. Both shapes have the same local varied inventory—centre, FWHM, amplitude. The data bindings and numerical recomputation can pass, and the live binding then compares against the substituted `O.model`. Today the optimizer copies the starting model and only assigns inventoried parameters and derived links; it does not change shape. [Page:9479](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9479), [page:9484](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9484), [page:9579](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9579)

Specify a local projection that copies R’s structure, substitutes only permitted free outputs, propagates links using R’s graph, and requires equality with the recorded final model. Define “held” to include everything outside the allowed changes, and check the engine’s bounds/determinacy rules. Add a shape-substitution negative case.

Batch’s target-specific capture after propagation/scaling is otherwise correct. [Page:14256](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14256)

**4. Mutators and shallow copies**

**Handled at plan level.** Freezing `{seal, view}`, making invalidators/restamping/lazy R no-ops on sealed results, copying Chart.js arrays, and excluding sealed results structurally from legacy reconstruction address the actual writes. [Plan:210](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:210), [page:5042](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5042), [page:10570](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10570)

Immutable seal sharing makes shallow snapshots safe. The peak-only versus contextual restore distinction is coherent. History restoration must still rejudge against the resulting workspace: today it restores peaks/result without restoring complete context. [Page:16229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16229)

**5. Saves, loaders and legacy**

**Achievable for both formats, and Q1 is coherent.** Both formats already preserve raw arrays without the rounding applied to project fit-result arrays. Replacing the latter with the whole seal therefore supports exact data bindings. [Page:12289](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12289), [page:12355](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12355)

The plan correctly specifies:

- Early sealed/legacy dispatch, before existing reconstruction.
- Ignoring spectrum convenience arrays when a seal exists.
- Preserving the edited workspace separately from R.
- Preserving legacy evidence without manufacturing a seal.
- Saving/loading/showing `tab.provenance` after peaks-only fallback.
- Preserving the existing `.fit.json` `fitStatistics` interface. [Plan:223](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:223)

LEGACY must remain a ceiling over the old reconstruction restrictions: an old background/Voigt failure must not regain statistics merely because its outer state is now LEGACY. “As today” in the matrix supports that interpretation. [Page:10583](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10583)

**6. Verification timing and ownership**

The revised manager addresses live tab identity, newer operations, attempt identity, inactive loaded tabs, reinstall/activation triggers and affected-chart repaint.

**M2 — MAJOR: the manager and state rules do not yet implement Auto-Fit’s staged transaction consistently.**

Two explicit rules conflict:

- §6.3 requires both verifications **before installing the final seal**.
- §9 discards replies unless the owner already holds that same seal, and explicitly includes Auto-Fit among these producer-bound attempts. During either staged check, the owner should still hold its previous installed result. [Plan:141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:141), [plan:245](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:245)

Define staged verification ownership separately: live owner, current operation, transaction identity and exact staged R/O identity. Such replies may resolve the transaction without attaching a displayed result. Commit then installs the final whole seal and its complete verification result.

Also define Auto-Fit’s aggregate verification state. §5 makes any §6.3 failure STALE, while §6.3 includes both verifications being `consistent`. On reload, an outstanding or unreachable E check must yield PENDING or UNCONFIRMED—not a failed-prerequisite STALE merely because consistency has not been established. Only an actual mismatch, failed binding/gate or negative recorded acceptance should take that failure path. [Plan:102](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:102)

Test staged success, supersession at each verification boundary, and restored Auto-Fit with O₂ consistent while E is pending/unreachable/different-software.

**7. Visible changes and context**

**M3 — MAJOR: revision 3 excludes charge-reference settings from the live binding, contrary to the retained context contract.**

The approved design includes charge-reference settings in `R.context0` and requires the live context to match it. Revision 3 places those settings under producer-only inputs and explicitly excludes them from the live key. Yet these are actual persisted controls, and §10 still promises that changing them makes a fit stale. [Design:731](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:731), [design:862](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:862), [plan:33](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:33), [plan:86](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:86)

Separate actual `ccMethod`/`ccObs`/`ccLit` workspace fields from fixed Auto-Fit constants. Preserve the retained binding. Also make their R₁→R₂ transformation explicit: Auto-Fit changes the observed reference value, so placing it among “producer settings unchanged” is inconsistent with the current derivation. [Page:3913](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3913), [page:7963](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7963)

Otherwise §10 now identifies the significant visible changes, including reload uncertainties/alternatives, recorded curves, per-tab method, verification delays, Auto-Fit rollback, historical grids and larger saves.

**MINOR:** correct the context-schema references: after introducing `context0.live`, several examples still address `context0.ccShift`/`context0.roi*` directly. Also correct the §8.6 pointer for method persistence to §8.5. These should describe one concrete schema before extraction begins. [Plan:30](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:30)

**8. Suggested sequence within this branch**

1. Resolve M1–M3; incorporate/review 1b before proceeding beyond the prerequisite.
2. Extract explicit owner-aware context, request builders, server/local projections and Auto-Fit derivation. Pin existing request behavior.
3. Add per-tab method persistence and context-change notifications.
4. Produce immutable seals and local O alongside existing output; compare views without switching authority.
5. Implement bindings and verification, including staged transactions and aggregate Auto-Fit states, behind the switch.
6. Migrate all consumer groups, including downstream stack dataset construction and separate alternative display/adoption gates.
7. Add both serializers/shared sealed loader; test current, stale, pending, unconfirmed and legacy round trips.
8. Enable Run Fit/alternatives, then local/Batch, then Auto-Fit. Require each producer’s positive and negative cases before enabling the next.
9. Retire sealed-path old authorities, complete the browser matrix and legacy census, measure visible differences, and finish 1d before the combined release review.

**VERDICT: NO-GO.**
