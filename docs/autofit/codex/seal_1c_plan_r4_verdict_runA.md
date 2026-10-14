**Revision 4 is ready to build, subject to its stated 1b prerequisite.** I found no remaining BLOCKER or MAJOR plan gap.

Read-only review of `seal-1c-page`, HEAD `fd37935d3a9651e50f1ee2800cfc7b96e61d97b7`. No files changed or tests run. This approves the implementation plan, not an implementation or release.

**1. Design coverage and verification of §13**

The plan now covers the retained V6.2–V6.9 contract: R/O/D/E, exact step 0, projection, sample/context/background/frame bindings, distinct verification states, local O, identity provenance, legacy handling, and consumer migration. Keeping engine/producer on the enclosing seal and deriving reportability is coherent. Acceptance remains recorded-only; 1d supplies the visible re-run control before release, as [V6.22 requires](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1322).

I checked every finding grouped in §13 against its substantive answer, including the later extensions:

| Earlier finding | Revision-4 assessment |
|---|---|
| R1: Auto-Fit E not judged; verification after commit | Closed: same-spectrum E bindings, both verifications, gates and exact derivation precede commit. [Plan:147](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:147) |
| R1: status wrappers leave independent numerical sources | Closed by the complete view and explicit numerical consumer migration. [Plan:181](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:181) |
| R1: finite shift, link graph, duplicated context, sample completeness, display frame, background effect, enlarged key | Closed: one context, explicit bindings, owner-aware live comparison including overlays, method and charge-reference controls. [Plan:57](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:57) |
| R1: provenance absent; 1b incorrectly claimed complete | Closed: producing-page identity and nonblocking completeness classification; 1b explicitly outstanding. [Plan:233](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:233), [plan:9](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:9) |
| R1: PENDING/UNCONFIRMED wording, repaint, support policy; omitted `_currentSupport` | Closed by the presentation matrix, separate state mappings and comparison of state/check/reason/seal identity. [Plan:120](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:120) |
| R1: local/Batch contract and array-property metadata; R2: unbound energies/net/weights/inventory | Closed: ordinary serialized background metadata, engine-specific input reconstruction and exact local arithmetic. [Plan:47](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:47), [plan:64](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:64) |
| R1: `_preFit` retired without replacement | Closed by `view.initialValues` from the actual R starting model, including alternative starts. [Plan:190](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:190) |
| R1: mutable views, restore dispatch and snapshot semantics | Closed by frozen results/views, structural dispatch, and distinct peak-only versus contextual restoration. [Plan:224](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:224) |
| R1: duplicate persistence authorities, stale saves, legacy re-save and lost provenance | Closed by whole-seal persistence, separate workspace, ignored convenience arrays and retained `tab.provenance`. [Plan:237](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:237) |
| R1/R2: verification scheduling, supersession, owner liveness, activation, recovery and repaint | Closed by the three attempt kinds and explicit attachment/recovery rules. [Plan:254](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:254) |
| R2: missing positive O₂ acceptance | Closed at both commit and restored-seal judgment. [Plan:155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:155) |
| R2: local designation, `.fit.json`, Batch summary | Closed by explicit view fields and migration rows. [Plan:191](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:191) |
| R2: method workspace lifecycle and producer-only settings | Closed: live/producer context separation and per-tab method capture, restore, persistence and repaint. [Plan:27](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:27), [plan:245](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:245) |
| R3 A-M1: local final structure accepted from O | Closed: `projectLocal` starts from R’s structure, applies only permitted free values and derived links, then requires equality with O.model. [Plan:97](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:97) |
| R3 A-M3/B-M1: charge-reference controls excluded; Auto-Fit transformation missing | Closed: controls belong to live context; R₂’s controls and shift are explicitly derived. [Plan:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:158) |
| R3 A-M2/B-M2: staged checks require premature installation; aggregate restored state; tab-switch ownership | Closed: transaction-owned STAGED checks, explicit aggregate precedence, and `_ownerActive` for producer-bound attachment. [Plan:161](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:161), [plan:261](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:261) |
| R1–R3 minor findings: R adapter, visible changes, schema/pointer corrections, Preview versus Use, retry/cache | Answered: nullable ratio adapter, expanded release notes, explicit context shorthand, handler-level CURRENT gate, uncached transport failure and forced retry. [Plan:128](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:128), [plan:274](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:274) |
| R1–R3 sequencing | Sound staged migration; refinements in answer 8 below. [Plan:338](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:338) |

**MINOR — canonicalization wording:** §3’s parenthetical “integers by `parseInt`” should explicitly exempt endpoint averaging. Its current canonical reader uses refusal validation followed by `Number(String(v).trim())`. The plan’s instruction to reuse the actual readers is correct; the shorthand is inaccurate. Preserve that exception when extracting the new key. [Plan:86](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:86), [page:8650](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8650)

**2. Consumer machinery**

**Sound with the numerical migrations explicitly required by §7.** Keeping helper names is fine; replacing only their bodies would remain insufficient. Revision 4 requires more than that.

| Consumer | Current bypass covered by the plan |
|---|---|
| Chart | Reconstructed counts, live components, residual recomputation and envelope-minus-background. Replace with view arrays. [Page:11460](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11460) |
| Results, sidebar, areas, Quantify | Live parameters and `_peakArea` evaluation, including sidebar patching and area signatures. [Page:10057](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10057), [page:7857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7857) |
| Header and R panel | Top-level statistics and unqualified level wording. [Page:9418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9418), [page:13653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13653) |
| Uncertainties | Backend parameters, live peak support and `_preFit`; all have specified view replacements. [Page:13736](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13736) |
| CSV/XLSX | Live parameters, recomputed areas and independent `_currentSupport`. [Page:13479](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13479) |
| TSV/PNG | Independent ROI/background/model/residual construction and record metadata. [Page:12997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12997), [page:13068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13068) |
| Stack A/A2/B | Reconstructed counts/envelopes/components. Migration must include downstream dataset assembly, particularly background subtraction—not just `_buildEntryRenderData`. [Page:10944](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10944), [page:11155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11155) |
| History/undo | Separate snapshot statistics and preview evaluation on today’s grid. [Page:16079](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16079), [page:11581](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11581) |
| Alternatives/certificate notice | Old key identity, shared display/adoption eligibility and recorded-evidence wording. [Page:8785](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8785), [page:8980](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8980) |
| Designation, saves/loaders, Batch summary | Direct top-level result readers are explicitly migrated too. [Page:9391](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9391), [page:12181](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12181), [page:14324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14324) |

I found no additional omitted consumer family in the requested list.

PENDING/UNCONFIRMED may display recorded numbers and apply recorded support exclusions **with qualification**. They never map to `'current'`, and a truthy starts object does not authorize adoption: the Use handler independently requires CURRENT. That resolves the prior false-current routes.

**3. Producers and exact reconstruction**

- **Run Fit:** sufficient capture—actual starting model, complete context, selected indices/arrays and exact wire body, all used by one pure builder. This matches the current split between input capture and request submission. [Page:9132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9132)
- **Use this solution:** correctly records `opts.startPeaks`, while retaining the live pre-operation model only for ownership. `initialValues` consequently describes the alternative’s actual start.
- **Auto-Fit:** sufficient at plan level. Both complete requests/responses, same-spectrum E, positive recorded acceptance, anchor gates, charge-control transformation, rounding, reselection and locks are judged before commit and again on restore. This preserves the existing separate O₂ acceptance and anchor checks. [Page:8512](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8512)
- **Local:** now binds numerical inputs and final structure to R. In particular, preserving the engine’s `net + background` weighting association is correct. [Page:9474](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9474)
- **Batch:** capture after target propagation/scaling, using target data/context, is the right boundary. The returned summary statistic comes from the same O_local. [Page:14256](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14256)

None of these checks needs to prove the optimizer’s search history. That remains recorded acceptance under option (b).

**4. Mutators and shallow copies**

Handled. Frozen `{seal, view}`, no-op sealed invalidators/restamping/lazy R, copied Chart.js arrays, and structural exclusion from legacy reconstruction address the actual mutation sites. In particular, `_restoredFitBgFailure` currently replaces arrays and clears evidence; it must remain unreachable for sealed results. [Page:5042](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5042), [page:3324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3324), [page:10570](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10570)

Sharing immutable seal references is safe. Peak-only undo retains/rejudges the installed seal; contextual undo/history/rollback reinstalls the captured one. History restoration can legitimately remain STALE when its context differs: today that path restores peaks/result without the complete context. [Page:16229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16229)

**5. Saves, loaders and legacy**

Achievable for both formats. Both already preserve raw arrays; the project’s rounded fit-result fields can be replaced by `{seal}`. Spectrum convenience arrays can be generated from the view and ignored on sealed load. Separately preserving the edited workspace supports a genuinely STALE round trip. [Page:12355](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12355), [page:12289](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12289)

The prescribed early dispatch must precede both spectrum reconstruction and the project-wide restore loop. Invalid seals go PEAKS-ONLY with a reason, never through legacy repair. [Page:12618](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12618), [page:12843](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12843)

Q1 is coherent as a permanent ceiling over today’s legacy eligibility rules. “LEGACY” must retain existing background/shape failure restrictions beneath it; the plan’s “as today” preserves that. `tab.provenance` persistence and display address evidence lost when reconstruction drops the result.

**6. Verification timing and ownership**

Complete at plan level:

- Fresh server Run Fit/Use results install PENDING.
- Auto-Fit checks staged candidates before publication.
- Loads verify inactive spectrum tabs, including stack sources.
- Activation and reinstalls recover missing verification.
- Producer replies require live owner, same installed seal, latest attempt, current operation **and active owner**.
- Background checks do not claim fitting operations.
- Unreachable failures remain retryable; “check again” explicitly starts a new attempt.
- Restored Auto-Fit aggregates both checks without confusing outstanding/unconfirmed evidence with a mismatch.
- Result changes repaint affected consumers and invalidate stack caches.

The added active-owner condition matters: `_fitOpCurrent` alone only checks the operation map, whereas `_ownerActive` checks the active tab object. [Page:8157](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8157), [page:2382](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:2382)

Implementation tests should exercise late old-attempt cleanup while a newer attempt is running, so clearing the old attempt cannot clear the newer one.

**7. Visible changes**

The former §7a is now §10. It identifies the material changes: recorded numerical values, restored uncertainty/alternatives, verification states and delays, Auto-Fit rollback, expanded context staleness, legacy qualification, provenance, immutable edit previews, larger saves, per-tab method, retries and historical preview grids. [Plan:285](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:285)

The area and LA wording is now accurate: the trapezoid formula already exists; reading recorded areas is the change. LA becomes UNCONFIRMED when the relevant exact evaluation fails, not categorically. I found no further material user-visible change missing from the list. Numerical differences remain to be measured, as the plan says.

**8. Order within the branch**

Use §12’s order with these implementation boundaries:

1. Incorporate and assess 1b before proceeding past the prerequisite.
2. Extract pure context readers, request builders, projections and Auto-Fit derivation; pin existing request behavior.
3. Add complete per-tab method lifecycle and context-change repaint.
4. Produce immutable seals/local O alongside existing results; compare views without switching authority.
5. Implement bindings, state aggregation and verification ownership behind the switch.
6. Migrate complete consumer groups, including subordinate area/support/designation readers and stack dataset construction.
7. Add both serializers and shared sealed loader; verify CURRENT, STALE, PENDING, UNCONFIRMED and legacy round trips.
8. Enable Run Fit/Use, then local/Batch, then Auto-Fit, validating each producer before enabling the next. Ship state wording with each enabled path.
9. Retire sealed-path old authorities; complete the browser matrix, legacy census, release measurements and 1d before release review.

Keep normal production producers on the existing path until their complete consumer and persistence paths are ready. That makes each intermediate commit working and testable.

**VERDICT: GO (the plan may be built).**
