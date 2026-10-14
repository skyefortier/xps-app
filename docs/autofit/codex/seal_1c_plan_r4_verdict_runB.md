**Revision 4 may be built. I found no remaining BLOCKER or MAJOR plan gap.** The substantive findings from rounds 1–3 are answered; two wording clarifications remain MINOR.

Reviewed `seal-1c-page`, HEAD `fd37935d3a9651e50f1ee2800cfc7b96e61d97b7`. Read-only: no files changed or tests run. I treated 1b as the outstanding prerequisite explicitly stated at [plan:9](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:9). This verdict does not establish its measurements.

**1. Design coverage and verification of §13**

The plan covers the retained V6.2–V6.9 contract: R/O/D/E, exact step 0, projection, sample/context/background/frame bindings, distinct verification states, local O, identity provenance, legacy handling, and migration through one numerical view. Moving engine/producer onto the enclosing seal and deriving reportability is coherent. Acceptance remains recorded and qualified; 1d supplies the visible re-run control before the combined release. This matches [V6.22:1322](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1322).

I checked every finding category in the [§13 map](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:356):

| Earlier finding | Revision-4 assessment |
|---|---|
| R1: Auto-Fit E stored without judgment; premature commit | Closed: same-spectrum bindings, both checks, gates, derivation, and deferred commit (§6.3). |
| R1: Status wrappers leave independent numerical sources | Closed: complete view and explicit consumer migration (§7). |
| R1: Incomplete sample/context/frame/effect/key bindings | Closed: one context, finite shift, link validation, exact selection/request/background/frame checks (§§1–3). |
| R1: Provenance missing | Closed: producing-page identity and nonblocking completeness classification (§1, §8.3). |
| R1: 1b wrongly treated as complete | Closed as a planning claim: explicitly outstanding prerequisite. |
| R1: PENDING/UNCONFIRMED wording, repaint, support policy | Closed: state matrix and comparison of state/check/reason/seal identity (§5). |
| R1: `_currentSupport` omitted | Closed: explicitly migrated (§5). |
| R1: Local/Batch contract and serializable background metadata | Closed: tagged local record, ordinary metadata fields, reconstruction and judgment (§§1, 2.3, 4, 6.4). |
| R1: `_preFit` removed without replacement | Closed: `view.initialValues` from the actual starting model (§7). |
| R1: Mutators, structural dispatch, mutable views, snapshots | Closed (§8.1–8.2). |
| R1: Duplicate authority, stale saves, legacy re-save/provenance | Closed (§8.4–8.6). |
| R1: Verification lifecycle, inactive sources, restore/retry/repaint | Closed (§9). |
| R1: Visible changes and nullable R adapter | Closed (§§7, 10). |
| R1: Sequencing | Sound, with the refinements in answer 8. |
| R2: Local energies/net/weights/inventory unbound | Closed by explicit equalities (§2.3). |
| R2: O₂ positive acceptance missing | Closed at commit and restore (§6.3). |
| R2: Local designation, `.fit.json`, Batch summary | Closed by named view fields and migration rows (§7). |
| R2: Method lifecycle and producer-only settings | Closed by owner-aware context and per-tab method persistence (§§1, 3, 8.5). |
| R2: Supersession, owner liveness, activation/recovery, charts | Closed (§9). |
| R2: Visible changes, pointer, alternative display/adoption | Closed; Use also checks CURRENT inside its handler (§5). |
| R3: Charge-reference controls and Auto-Fit transformation | Closed: live binding plus explicit derived final controls (§§1, 3, 6.3). |
| R3: Local model structure accepted from O | Closed: `projectLocal` derives structure from R and changes only permitted fields (§4). |
| R3: Staged verification versus installed-seal ownership; aggregate state | Closed: STAGED attempts and explicit restored Auto-Fit aggregation (§§6.3, 9). |
| R3: Producer-bound reply after tab switch | Closed: active-owner check plus background recovery (§9). |
| R3: Retry/cache, handler gate, schema references, area/LA wording, pointer | Closed: explicit retry bypass, handler gate, context-path convention, corrected wording/references. |

Two **MINOR** clarifications would make extraction less error-prone:

- **Keep the endpoint-averaging reader’s exception explicit.** §3’s parenthetical “integers by `parseInt`” oversimplifies today’s `_fitKeyCanon`: endpoint averaging uses refusal-aware parsing so invalid `"1e2"` cannot match valid `"1"`. The controlling instruction to reuse the existing readers is correct; preserve it precisely. [Plan:83](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:83), [page:8648](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8648).
- **Clarify the live key’s presentation exclusions.** “Every field `project` reads or writes” is broader than §7’s explicit live names/colours/visibility policy, because projection copies the whole snapshot. State the exclusions beside the key definition and pin cosmetic edits as non-staling. This reconciles the wording with §7 and current behavior. [Plan:183](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:183), [page:8622](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8622).

Neither requires a new architectural decision.

**2. Consumer machinery**

**Sound as the adapters specified in Revision 4.** Keeping helper names alone would fail; the plan now also replaces the numerical reads underneath their consumers. Its explicit mapping prevents PENDING/UNCONFIRMED from becoming `'current'`, while permitting qualified recorded values and support exclusions. [Plan:120](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:120).

I found no additional missing consumer family in the requested list:

| Consumer | Current bypass covered by the migration |
|---|---|
| Chart | Reconstructed counts, live component evaluations, residual recomputation and envelope subtraction. [Page:11460](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11460). |
| Results, sidebar, areas, Quantify | Live parameters and reevaluated areas; include sidebar patching and `_areaSignature`, not just table rendering. [Page:7857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7857), [page:9970](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9970). |
| Header and R panel | Direct result fields and insufficient state qualification. [Page:9418](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9418), [page:13653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13653). |
| Uncertainties | Backend parameters, live support and `_preFit`; the view supplies all replacements. [Page:13736](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13736). |
| CSV/XLSX | Live parameters/areas and independently keyed support. [Page:13479](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13479). |
| TSV/PNG | Independently selected ROI/background/model/residuals; PNG metadata must follow the same view as its figure. [Page:12997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12997), [page:13068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13068). |
| Stack A/A2/B | Reconstructed counts/envelopes/components. Migration includes downstream dataset construction: use `fittedSub`, rather than subtracting background from `fittedY`. [Page:10944](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10944), [page:11155](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11155). |
| History/undo | Separate snapshot statistics and current-grid preview evaluation. [Page:16079](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16079), [page:11581](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11581). |
| Alternatives/certificate notice | Old key identity and shared preview/adoption eligibility. The explicit Use handler guard closes the pending-adoption route. [Page:9033](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9033). |
| Local designation, saves/loaders | Explicitly included, including parameter-file provenance and Batch’s returned statistic. [Plan:212](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:212). |

STALE live previews remain legitimate because they are labelled previews and carry no current fit statistics. The migration must preserve that distinction throughout subordinate readers.

**3. Producers and step 0**

**Run Fit / Use this solution:** sufficient capture is specified. The full starting snapshot, context, selected arrays and exact wire body support reconstruction through one pure builder. Using `opts.startPeaks` for the alternative, separately from the live ownership snapshot, matches the current request path. Preserve omitted fields versus explicit null. [Plan:142](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:142), [page:9132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9132).

**Auto-Fit:** sufficient. E is now a full prerequisite, both recorded successes are required, both responses are verified, and the transformation into R₂ includes charge controls, rounding, shifted anchors/centres, reselection and locks. Crucially, restored seals use the same predicate. That preserves the independent final acceptance check currently at [page:8512](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8512). The control transformation matches the path through [page:7963](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7963) and `updateChargeCorrection`.

**Local / Batch:** sufficient at plan level. Numerical inputs are bound to R, and the new `projectLocal` closes the round-3 shape/lock/link substitution hole. It mirrors the engine’s actual permitted changes: assign inventoried parameters, then propagate links in dependency order. The exact `net + background` weight association is preserved. [Plan:64](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:64), [page:9474](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9474), [page:9579](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9579).

Batch correctly captures each target after propagation/scaling, using that target’s data and context. Its summary must read the finalized O’s statistic, as specified. [Page:14256](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14256), [page:14324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14324).

**4. Mutators and shallow copies**

**Handled.** Freezing `{seal, view}`, making the named mutators no-ops for sealed results, and structurally excluding seals from reconstruction address the actual writes—including lazy R calculation and `_restoredFitBgFailure`’s array replacement. [Plan:224](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:224), [page:3324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3324), [page:10570](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10570).

Sharing immutable seals through shallow snapshots is safe. The distinction between peak-only undo and contextual/history/rollback installation is now explicit. Reinstalling a historical seal must still judge the resulting workspace: today history restores peaks/result without restoring all context, so STALE can be the correct outcome. [Page:16229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16229).

**5. Saves, loaders and legacy**

**Achievable and coherent.** Both formats already preserve full raw arrays. Project rounding affects the old fit-result fields that `{seal}` replaces. The spectrum loader can ignore convenience arrays once the top-level seal is present. [Page:12289](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12289), [page:12355](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12355).

The specified early dispatch must precede both spectrum reconstruction and the project-wide restore loop. Invalid seals remain PEAKS-ONLY with a reason; they cannot fall through into legacy reconstruction. Edited workspace persists independently, preserving stale round trips. [Plan:237](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:237), [page:12618](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12618), [page:12843](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12843).

Q1 is coherent as a permanent ceiling over today’s reconstruction eligibility. LEGACY must retain existing background/shape restrictions beneath that ceiling; the plan’s “as today” policy does so. Separately saved/shown `tab.provenance` covers peaks-only fallback.

**6. Verification timing and ownership**

**Complete at the design-plan level.** Revision 4 distinguishes:

- Producer-bound verification of an installed fresh seal.
- Transaction-owned staged Auto-Fit checks, without premature publication.
- Background verification for load, activation, reinstall and recovery.

The manager checks live owner object, exact seal/attempt identity, and—where applicable—current operation and active owner. This correctly accounts for the fact that `_fitOpCurrent` alone does not detect a tab switch. [Plan:254](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:254), [page:2382](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:2382), [page:8157](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8157).

The restored Auto-Fit aggregation now correctly distinguishes outstanding/unavailable checks from actual failures. Unreachable results are not cached, explicit retry starts a new attempt, inactive loaded sources are checked, and affected charts/caches repaint. No remaining lifecycle contradiction warrants rejection.

**7. Visible changes**

The requested former §7a is now [§10:285](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:285). It identifies the material changes: recorded numerical output, restored uncertainties/alternatives, verification qualification, Auto-Fit waiting/rollback, context staleness, per-tab method, legacy ceiling, provenance, retry, larger saves and historical preview grids.

I found no additional material user-visible change missing. The corrected area and conditional LA wording accurately distinguish this unit from behavior already present at HEAD.

**8. Sub-step order within the branch**

Use §12’s order with these concrete boundaries:

1. Complete the plan gate; incorporate and assess 1b before proceeding.
2. Extract pure builders, projections, Auto-Fit derivation and owner-aware context readers. Pin existing request behavior; add method persistence/change notification.
3. Produce immutable seals and local O alongside existing output; compare views without switching authority.
4. Implement bindings, state presentation and verification behind the switch, including staged transactions, supersession, close/switch and retry recovery.
5. Migrate consumer groups, including subordinate area/support/designation readers, stack dataset construction and separate alternative display/adoption guards.
6. Add both serializers and shared sealed loading; verify current, stale, pending, unconfirmed, invalid and legacy round trips.
7. Enable Run Fit/Use Solution, then local/Batch, then Auto-Fit, validating each producer before enabling the next.
8. Remove obsolete sealed-path authorities; complete the browser matrix, legacy census and release measurements.
9. Complete 1d and review the combined release before deployment.

Implement the required state wording before enabling sealed producers, even if final editorial polish remains in step 8. That keeps each intermediate page usable and its displayed status accurate.

**VERDICT: GO (the plan may be built).**
