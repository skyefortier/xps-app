**Revision 2 still needs changes before implementation.** Most round-1 findings are answered, but five MAJOR gaps remain.

Read-only review of `seal-1c-page`, HEAD `68f6486`; no files changed or tests run. I treated 1b exactly as the plan now describes it: an outstanding prerequisite, not missing evidence claimed as complete.

1. **Design coverage and the round-1 resolution map**

   The overall architecture now matches the retained design: immutable R/O, derived projection, step 0, explicit sample/background/frame bindings, distinct PENDING/UNCONFIRMED states, recorded acceptance, provenance, legacy handling, and migration through a complete view. Keeping `engine` and `producer` on the enclosing seal rather than duplicating them in D is reasonable, provided the view derives their presentation consistently. No withdrawn key machinery needs reinstating. See [design:1320](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1320).

   I checked every row of [plan §13:279](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:279):

   | Round-1 finding | Round-2 assessment |
   |---|---|
   | Auto-Fit E and verification before commit | Substantially answered; final positive acceptance remains omitted from the stated predicate—M2 below. |
   | Status wrappers leave independent numerical sources | §7 now explicitly migrates the consumers; local designation remains a separate missed reader—M3. |
   | Context/sample/frame bindings | The bindings are specified; persistence and lifecycle of the enlarged context remain incomplete—M4. |
   | Provenance | Answered by `R.page` and §8.3’s nonblocking classification. |
   | 1b evidence absent | Answered correctly as an explicit prerequisite. |
   | PENDING/UNCONFIRMED presentation and repaint | Answered by the matrix and comparison of state/check/reason/seal identity. |
   | `_currentSupport` | Explicitly included now. |
   | Local/Batch record and checker | Partially answered; local input associations remain unbound—M1. |
   | `_preFit` replacement | Answered by `view.initialValues`, including alternative starts. |
   | Structural dispatch, immutability, undo semantics | Answered at the plan level. |
   | Persistence, duplicate fields, stale saves, legacy provenance | Mostly answered; enlarged workspace context remains incomplete—M4. |
   | Verification lifecycle | Improved substantially; ownership and discarded-attempt recovery remain incomplete—M5. |
   | Visible changes and R adapter | Mostly answered; minor additions below. |
   | Sequencing | Sound general structure, with the adjustments in answer 8. |

2. **Consumer machinery: sound as adapters, but consumers still require migration**

   Revision 2 no longer proposes merely changing status helpers: [plan:151](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:151) supplies the full view and explicitly migrates each numerical consumer. That resolves the central round-1 objection.

   The following current bypasses are now covered by that table:

   | Consumer | Current source that must be replaced |
   |---|---|
   | Chart | Reconstructed counts, live component evaluation, differently associated residuals and background subtraction—[page:11460](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11460). |
   | Results, sidebar, areas, Quantify | Live parameters and `_peakArea`/`_areaGrid`—[page:10057](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10057), [page:7857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7857). |
   | Header, R panel, uncertainties | Top-level result fields, R level wording, `_preFit`, live support—[page:13653](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13653), [page:13736](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13736). |
   | CSV/XLSX | Live parameters, recomputed areas, `_currentSupport`—[page:13479](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13479). |
   | TSV/PNG | Independent ROI/background/model/residual construction—[page:12997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12997), [page:13068](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:13068). |
   | Stack A/A2/B | Reconstructed counts, envelopes and components—[page:10958](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10958). |
   | History/undo | Separate snapshot statistics and preview evaluation on the current grid—[page:16079](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16079), [page:11581](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11581). |
   | Alternatives/certificate | Old key identity and shared current-evidence gates—[page:8953](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8953), [page:9033](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9033). |
   | Saves/loaders | Rounded or independently reconstructed authority—covered by §8, subject to answer 5. |

   PENDING/UNCONFIRMED may show recorded values with qualification; they must not become `'current'`. The revised matrix makes that distinction adequately. Implementation must separate **displaying/previewing recorded alternatives** from **permission to use one**: today `_currentAlternative` and `_altPeaks` share `_startsIfCurrent` with the adoption handler. A truthy starts object must not itself become permission to adopt while pending. See [page:9050](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9050).

   **M3 — MAJOR: local-engine designation remains outside the specified adapter migration.** The new result is exactly `{seal, view}`, but `_isLocalFit` currently reads top-level `engine`/`objective`; `_provenanceOf` also reads top-level fields. Neither is in the adapter list, and the enumerated view omits an explicit engine/reportability contract. Leaving these readers intact makes a local sealed result look nonlocal and loses its starting-point designation through exports, stacks, undo and `.fit.json`. See [plan:189](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:189), [page:9337](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9337), and [page:9391](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9391).

   “Designation unchanged” states the intended outcome but does not specify the necessary migration. Add derived engine, objective/weighting, reportability and caveat fields, and explicitly adapt the designation/provenance helpers.

3. **Producers and exact request reconstruction**

   **Run Fit and “Use this solution”: sufficient proposed inputs.** Capturing the actual starting model, complete context, selected samples and exact wire body, then sharing one pure builder with step 0, addresses the request-reconstruction requirement. The alternative must remain `opts.startPeaks`, as revision 2 specifies; current code distinguishes it from the live ownership snapshot at [page:9132](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9132).

   **Auto-Fit:** E is now genuinely part of judgment: same-spectrum bindings, O₁ verification, positive O₁ success, anchor gates, exact derivation into R₂, both verifications before commit, rollback and supersession. This closes most of the original blocker.

   **M2 — MAJOR: the final Auto-Fit predicate omits `O₂.success === true`.** [Plan:129](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:129) explicitly requires positive O₁ acceptance, but for O₂ names numerical consistency and the anchor gate only. Numerical consistency does not establish acceptance: unit 1a′ expressly leaves `success` recorded-only. The existing page separately rejects `json2.success !== true` before checking the anchor, and the approved design requires O₂ to be **accepted, verified and anchor-valid**. See [server plan:57](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-13-seal-1a-server.md:57), [page:8511](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8511), and [design:824](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:824).

   Add the positive final acceptance requirement to both commit and restored Auto-Fit judgment. This preserves the existing producer rule without claiming acceptance is proven.

   **M1 — MAJOR: local/Batch verification does not explicitly bind O’s numerical inputs to R.** Section 6.4 checks model evaluation, statistics, parameter inventory, held/link rules and background. It does not require:

   - `O.energies === R.energies`;
   - `O.net[i] === R.counts[i] - O.background.values[i]`;
   - `O.weights[i] === 1 / sqrt(max(O.net[i] + O.background.values[i], 1))`.

   The general §2 sample equality names O’s arrays only for the server branch. Consequently, the stated local predicate permits internally consistent local statistics computed from another recorded net signal or energy grid while R still binds correctly to the tab. See [plan:53](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:53) and [plan:142](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:142).

   These associations matter: the engine weights reconstructed `net + background`, not R’s raw counts directly. That is explicit in [design:1070](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1070) and [page:9474](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:9474). Define a tagged local equivalent of step 0 with those exact identities and negative tests for each.

   Batch’s proposed capture point—after target propagation/scaling, using target data/context—is correct against [page:14256](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:14256).

4. **Mutators and shallow snapshots**

   **Addressed at the plan level.** Section 8.1 explicitly makes the invalidators, support restamping and lazy R calculation no-ops for sealed results, freezes the view, copies Chart.js arrays, and prevents legacy reconstruction from receiving a sealed result. These are the necessary boundaries against the mutations at [page:5042](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:5042), [page:7848](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:7848), [page:3324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3324), and [page:10562](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10562).

   Sharing the frozen seal through shallow snapshots is safe. Revision 2 also resolves the previously unspecified distinction between peak-only undo and contextual/history restoration. A restored historical seal may correctly be STALE against context that history did not restore; reinstalling a seal alone must not imply CURRENT. Today history restores peaks/result without restoring the complete context at [page:16229](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:16229).

   Minor wording correction: §4’s “every held and linked field … equal to `pageModel`” should defer explicitly to §6.4’s dependency rule. A linked child follows its fitted parent; its final numerical value need not equal its starting value.

5. **Saves, loaders and legacy**

   **“The seal whole, nothing else authoritative” is achievable in both formats.** The explicit sealed branch, ignored convenience arrays, preserved edited workspace, legacy re-save path and persisted `tab.provenance` now answer the round-1 concerns. The branch must precede spectrum reconstruction at [page:12618](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12618) and project reconstruction at [page:12843](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12843).

   **M4 — MAJOR: the newly authoritative live context is not given a persistence/tab-lifecycle implementation.** Section 3 adds fit method and every producer-context field to the live key, while §8.4 retains workspace storage “as today.” Today `_captureUI` and `_restoreUI` do not capture/restore fit method; both serializers save that UI record. See [plan:72](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:72), [plan:202](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:202), [page:3904](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:3904), and [page:12398](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:12398).

   A nondefault-method fit therefore cannot reliably round-trip CURRENT under the specified unchanged workspace representation. Conversely, restoring method from R would overwrite a separately edited method and violate the promised stale-workspace round trip.

   Specify the complete per-tab workspace context, capture/restore/save paths and change notifications. Also distinguish live controls from producer-only constants/options: `n_starts`, `require_component` and local options have no generic current DOM representation. Fit method currently has no change handler to refresh the newly affected status at [page:1898](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:1898).

   Q1’s legacy adapter is coherent **provided LEGACY is a ceiling, not an erasure of existing stale restrictions**. Preserve the legacy adapter’s display eligibility and failed-background/shape reasons beneath that ceiling. Existing loaders rely on those distinctions to suppress statistics and preserve save semantics; see [page:10583](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:10583).

6. **Verification timing and ownership**

   Fresh installation, every loaded tab, inactive stack sources, restored seals without cache entries, retries and asynchronous repaint are now explicitly covered.

   **M5 — MAJOR: seal/attempt identity does not replace operation ownership, and discarded-attempt recovery is unspecified.** Section 9 attaches a response when the owner object still holds the same seal and the attempt is latest. It does not require that the owner is still live or that a fresh-fit verification’s producing operation remains current. See [plan:216](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-10-14-seal-1c-page.md:216).

   Concrete cases:

   - A newer Run Fit claims the tab while the previous installed seal is still awaiting verification. That old seal remains installed until the new fit succeeds, so the proposed checks accept the superseded operation’s reply.
   - A closed tab object can still hold the same seal.
   - A discarded attempt followed by activation has no specified restart trigger; activation is absent from §9, despite the test promising discard after a tab switch.

   The retained design explicitly requires operation ownership at [design:986](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:986); the page already provides the operation mechanism at [page:8138](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:8138).

   Preserve the good decision not to **claim** a fit operation during load. Instead, distinguish fresh-fit attempts carrying an existing operation token from background load/restore attempts; require live owner, correct installed seal and latest attempt in both cases. Define cancellation cleanup and an activation/restore `ensureVerified` path so discarded checks cannot strand a seal PENDING. Cached numerical results need not be invalidated merely because a tab was activated.

7. **Visible changes**

   The revised §10—formerly §7a—covers almost all round-1 omissions: recorded curves/areas, restored alternatives, pending/offline behavior, Auto-Fit verification rollback, context staleness, provenance and larger saves.

   **MINOR additions:**

   - The new “check again” retry control from §9.
   - If method becomes per-tab to satisfy M4, the method selector now follows tab activation and saved workspace restoration.
   - Historical fit previews will use the snapshot’s recorded grid/background rather than today’s current-grid reconstruction.
   - Include non-bit-stable evaluation among the visible UNCONFIRMED reasons; §5 names it, §10 does not.
   - Correct §10’s measurement pointer: measurements are in §12 step 8; step 9 is 1d.

   The current preview behavior being changed is at [page:11581](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c/templates/index.html:11581).

8. **Sub-step order within this branch**

   The proposed order is broadly sound. I would make these boundaries explicit:

   1. Resolve M1–M5; incorporate and review 1b before proceeding beyond the prerequisite step.
   2. Define complete workspace context and tagged server/local records. Extract pure builders, projection and Auto-Fit derivation; pin existing request behavior.
   3. Produce immutable seals and local O alongside existing results, without making them authoritative.
   4. Implement bindings, states and verification ownership behind the switch. Test local input substitution, failed O₂ acceptance, supersession, close/reload, discarded checks and inactive stack sources.
   5. Migrate consumer groups, including designation/provenance helpers and separate alternative display/adoption gates. Keep production producers on the old path until all sealed branches work.
   6. Implement both serializers/loaders and context persistence. Test current, stale, pending, unconfirmed and legacy round trips, including nondefault and edited methods.
   7. Enable Run Fit/alternative seals, then local/Batch, then Auto-Fit’s complete transaction. Verify immutable snapshots and one Auto-Fit undo/history entry.
   8. Finish state wording, legacy census, numerical/save-size measurements and 1d; review the complete release before deployment.

**VERDICT: NO-GO.**
