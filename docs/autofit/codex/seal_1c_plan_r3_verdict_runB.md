**Revision 3 closes most earlier findings, but two MAJOR issues remain.** No BLOCKER found.

Read-only review of `seal-1c-page`, HEAD `556220189e99602309cc45fa7a26a8b7ffa80734`. No files changed or tests run. I treated 1b as the explicitly outstanding prerequisite described at [plan:9](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:9); its absence does not independently fail this review.

1. **Design coverage and verification of §13**

   The architecture substantially implements the retained design: immutable R/O/D/E, exact step 0, projected model values, numerical verification, qualified recorded acceptance, local O, identity provenance, legacy handling, and consumer migration. Moving engine/producer onto the enclosing seal and deriving reportability is reasonable. Nothing requires restoring the withdrawn key machinery.

   I checked every finding mapped in [§13](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:326):

   | Earlier finding | Revision-3 assessment |
   |---|---|
   | R1: Auto-Fit E and verification before commit | Numerical prerequisites now specified; transaction ownership needs the clarification in M2 below. |
   | R1: Wrappers leave independent numerical sources | Answered by the complete view and explicit consumer migration. |
   | R1: Context, sample, frame, effect and key bindings | Mostly answered; charge-reference binding remains missing—M1. |
   | R1: Provenance absent | Answered by `R.page` and nonblocking ATTESTED/INCOMPLETE classification. |
   | R1: 1b incorrectly claimed complete | Answered: explicitly pending. |
   | R1: PENDING/UNCONFIRMED presentation, repaint and support policy | Answered by the state matrix and comparison of state/check/reason/seal identity. |
   | R1: `_currentSupport` omitted | Explicitly included. |
   | R1: Local/Batch record and verification | Answered, including ordinary serialized background metadata. |
   | R1: `_preFit` retired without replacement | Answered by `view.initialValues`, including alternative starts. |
   | R1: Structural dispatch, mutable views and snapshot semantics | Answered at plan level. |
   | R1: Persistence, stale saves and legacy provenance | Answered by §8. |
   | R1: Verification scheduling, ownership and recovery | Substantially answered; M2 and the retry issue below remain. |
   | R1: Visible changes and R adapter | Mostly answered; minor corrections below. |
   | R1: Sequencing | Sound overall, with refinements in answer 8. |
   | R2: Local energies/net/weights/inventory unbound | Answered explicitly in §2.3. |
   | R2: O₂ positive acceptance absent | Answered at commit and restore. |
   | R2: Local designation, `.fit.json`, Batch summary | Answered explicitly in §7. |
   | R2: Method workspace lifecycle and producer-only settings | Method lifecycle answered; charge-reference controls are incorrectly classified as producer-only. |
   | R2: Supersession, owner liveness, activation and repaint | Those additions are present; tab-switch semantics remain inconsistent—M2. |
   | R2: Visible changes, pointer, alternative display/adoption | Additions and pointer corrected; Preview/Use distinction explicit. |

   **M1 — MAJOR: revision 3 explicitly removes a retained live-context binding.**

   The design includes charge-reference settings in `R.context0`, requires live context equality, and V6.22 retains those bindings. See [design:731](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:731), [design:862](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:862), and [design:1343](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1343).

   Revision 3 instead places charge-reference settings under “what has no live control” and explicitly excludes them from the live key. They **do** have live controls: `ccMethod`, `ccObs`, and `ccLit` are already captured/restored per tab. [plan:33](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:33), [plan:86](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:86), [page:3913](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3913).

   A changed reference configuration yielding the same numerical shift can therefore remain CURRENT under §3, contrary to the retained context contract—and contrary to the plan’s own release note at [plan:275](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:275). Put these controls in the live context, with their actual readers and Auto-Fit-derived final values. Keep genuine producer-only options separate.

2. **Consumer machinery**

   **Sound as adapters, provided §7’s consumer migrations actually happen.** Revision 3 no longer proposes that changing status helpers alone redirects numerical reads.

   | Consumer | Assessment against current page |
   |---|---|
   | Chart | Covered: replace reconstructed counts, live component evaluation, residual recomputation and envelope subtraction with the view. [page:11460](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11460) |
   | Results, sidebar, areas, Quantify | Covered: projected values and recorded areas/support replace live evaluations. Include sidebar patching and area signatures. [page:7857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7857), [page:9970](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9970) |
   | Header, R panel, uncertainties | Covered by state wording, nullable R adapter, stderr and initial-value views. [page:9418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9418), [page:13736](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13736) |
   | CSV/XLSX/TSV/PNG | Covered, including figure data and record metadata. These currently read/reconstruct independent values. [page:12997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12997), [page:13068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13068), [page:13479](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13479) |
   | Stack A/A2/B | Covered by a source-owner view branch and asynchronous cache invalidation/repaint. [page:10944](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10944) |
   | History/undo | Covered: replace copied statistics and current-grid preview evaluation; reinstall/rejudge captured seals appropriately. [page:16083](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16083) |
   | Alternatives/certificate notice | Covered: seal identity, recorded attribution and separate Preview/Use eligibility. [page:8980](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8980) |
   | Designation, saves/loaders, Batch summary | Now explicitly covered, including previously missed direct readers. [page:9391](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9391), [page:12181](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12181), [page:14324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14324) |

   I found no additional uncovered consumer family in the requested list. The migration must include subordinate readers, not merely their top-level rendering functions.

   PENDING/UNCONFIRMED may display recorded values and apply recorded support exclusions with qualification; that does not make them CURRENT. The explicit mapping at [plan:127](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:127) handles this. Enforce “Use this solution” eligibility inside its handler as well as disabling its button: today Preview and Use share `_currentAlternative`. [page:9049](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9049)

3. **Producers and step 0**

   **Run Fit and Use this solution:** sufficient proposed capture. The full starting snapshot, context, selected samples and exact wire body support reconstruction. Using `opts.startPeaks` is essential and now explicit; current code distinguishes it from the ownership snapshot. [plan:136](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:136), [page:9132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9132)

   **Auto-Fit:** the recorded evidence and numerical predicates are now sufficient: same-spectrum E, both positive acceptances, both verifications, anchor gates, exact shift/rounding/reselection/lock derivation, and the same restored-seal predicate. O₂’s added success check correctly preserves today’s independent acceptance gate. [plan:141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:141), [page:8512](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8512). M1/M2 still affect its context and lifecycle.

   **Local/Batch:** the round-2 numerical hole is closed. §2.3 now binds energies, net signal, weights and varied inventory to R, preserving the engine’s exact `net + background` weighting association. Held fields and linked final-parent values are distinguished. Batch capture occurs after target propagation/scaling, using target data. [plan:66](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:66), [page:9474](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9474), [page:14256](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14256).

4. **Mutators and shallow copies**

   **Handled at plan level.** Freezing seal and view, making the named invalidators/restamper/lazy R calculation no-ops, copying Chart.js arrays, and structurally excluding sealed results from legacy reconstruction are appropriate.

   These address actual writes at [page:5042](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5042), [page:7851](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7851), [page:3324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3324), and [page:10570](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10570).

   Sharing immutable seal references is safe. Peak-only undo retains/rejudges the installed seal; contextual undo/history/rollback reinstalls the captured seal. A history restore can legitimately remain STALE when its old context is not restored—today history restores peaks/result without the complete context. [plan:210](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:210), [page:16229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16229)

5. **Saves, loaders and legacy**

   **Achievable and coherent.** Project `{seal}` and spectrum top-level `seal`, with separately saved workspace and ignored convenience arrays, establish one authority. Both formats already retain full raw arrays; project rounding currently concerns fit-result arrays, which the sealed branch replaces. [page:12355](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12355), [page:12289](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12289)

   The early dispatch must precede spectrum reconstruction and the project-wide restore loop. Revision 3 explicitly requires this. Invalid seals must remain PEAKS-ONLY with their reason, without falling into legacy reconstruction. [plan:236](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:236), [page:12618](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12618), [page:12843](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12843)

   Q1 works as a permanent ceiling over existing reconstruction eligibility. Preserve existing background/shape restrictions beneath LEGACY; the new label must not restore statistics that today’s adapter suppresses. Persisting/showing `tab.provenance` after peaks-only fallback is now specified.

6. **Verification timing and ownership**

   Fresh-fit PENDING, all-tab loading, inactive stack sources, activation/reinstallation, whole-seal caching, owner-object liveness, operation supersession and chart repaint are now covered.

   **M2 — MAJOR: producer-bound ownership still does not implement the retained tab-switch rule, and Auto-Fit staging needs an explicit ownership case.**

   Section 9 requires `_ownerLive`, same seal, latest attempt and `_fitOpCurrent`, then says switching tabs discards only a producer attempt whose operation was superseded. But switching tabs does **not** supersede `_fitOpCurrent`: that function only compares the per-owner operation map. Active ownership is a separate check. Consequently, a producer-bound reply after switching A→B passes the stated predicate. [plan:250](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:250), [page:2382](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:2382), [page:8157](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8157)

   This conflicts with the retained producer ownership rule and the plan’s own tab-switch-discard test. Background verification of inactive loaded tabs is a separate, valid case. Require active ownership for producer-bound attempts, or explicitly invalidate those attempts on switch and subsequently recover through a background attempt. [design:986](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:986), [plan:296](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:296)

   Also specify how Auto-Fit’s **staged candidate** satisfies ownership before installation. §6.3 prohibits committing before both checks, while §9’s shared attachment rule requires the owner to hold that seal. Define transaction-owned candidate checks separately from installed-seal attachment; neither verification may require premature publication. Current Auto-Fit publication occurs only after the final gates. [page:8518](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8518)

   **MINOR — retry/cache contract:** `_ensureVerified` starts only when there is no cached result, yet “check again” is one of its triggers. Specify that unreachable failures are not reusable numerical cache results, or that explicit retry bypasses/replaces them. Otherwise the promised retry can remain UNCONFIRMED without issuing a request. [plan:242](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:242)

7. **Visible changes**

   The expanded §10 covers the material changes identified in rounds 1–2, including method persistence, restored alternatives/uncertainty warnings, historical preview grids, verification delay, Auto-Fit rollback and larger saves.

   **MINOR corrections:**

   - Reconcile the charge-reference staleness promise with M1.
   - Describe the area change against this HEAD accurately: `_peakArea` already uses the server-formula trapezoid. The new change is reading recorded areas instead of reevaluating curves. [page:9906](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9906)
   - Make the LA wording conditional: the implemented verifier returns UNCONFIRMED for failed unstable evaluation identities; it does not categorically reject every LA fit. [plan:283](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:283), [fitting.py:3526](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/fitting.py:3526)
   - Correct §1’s method-persistence reference from §8.6 to §8.5.

8. **Sub-step order within this branch**

   Keep §12’s general structure, with these boundaries:

   1. Resolve M1/M2; incorporate and assess 1b before proceeding beyond the prerequisite.
   2. Extract pure builders, projection, Auto-Fit derivation and owner-aware context capture. Add complete per-tab context persistence/change notification.
   3. Produce immutable seals and finalized local O alongside existing output.
   4. Implement bindings, states and verification management behind the switch, including staged Auto-Fit ownership, switch/close/supersession and retry recovery.
   5. Migrate every consumer group, including subordinate area/support/designation readers and alternative action guards.
   6. Implement project JSON/ZIP and spectrum persistence, early sealed dispatch and legacy provenance retention.
   7. Enable Run Fit/Use Solution, then local/Batch, then Auto-Fit. Validate each producer’s round trips and failure boundaries before enabling the next.
   8. Retire sealed-path old authorities; run the browser matrix and legacy census; finish wording and measurements.
   9. Complete 1d and review the combined release before deployment.

   Add focused cases for a changed charge-reference configuration with unchanged shift, producer verification after switching tabs, staged Auto-Fit verification before installation, and offline→“check again”→CURRENT.

**VERDICT: NO-GO.**
