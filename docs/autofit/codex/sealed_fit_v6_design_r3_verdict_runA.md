# Sealed fit record v6 design — Codex gate round 3, run A (commit 8a4ddc5)

**Revision 3 is not ready for approval.** It resolves several round-2 findings, but display agreement and Auto-Fit binding remain incomplete, and the new authentication protocol needs a concrete contract.

Reviewed HEAD `8a4ddc5` against `c643c5f`; differences are documentation only. No files changed. Below, **D** denotes the [design memo](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:675).

1. **BLOCKER — taking expression values does not establish the claimed display agreement for every supported frontend representation.**

   D:757–770 retains the frontend shape and applies O’s expression values through `_applyBackendParams`’ field mappings. A linked **Voigt child of a GL parent** defeats this rule.

   A production `run_fit` probe returned:

   | Property | Result |
   |---|---|
   | Parent GL mix | `0.2`, held |
   | Child’s requested Voigt mix | `0.5`, held |
   | Child’s returned mix | `0.2`, expression `p1_gl_ratio` |
   | Fit success / certified | `true` / `true` |

   The server overrides the child’s fixed mix with the parent expression. But the page’s Voigt evaluator always uses **0.5**. Even assigning `child.glMix = 20` does not change that evaluator. At one sampled point, the child’s page value was **6.5625**, versus **4.500000000000001** for O’s model; maximum component difference was **2.0625 counts**.

   Evidence: [server expressions](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1570), [Voigt evaluator](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:4184), [application mapping](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7005). Such a loaded model is not rejected by the [load validator](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:15797).

   Step 0 reproduces the request correctly; server verification validates the expression correctly; an authentic HMAC would pass; live can equal projection. Nevertheless, the displayed Voigt identity contradicts the verified model.

   **Required:** define and enforce representability of expression-controlled parameters in the frontend shape. Reject incompatible linked representations or explicitly transform them into a representation that describes O. Merely bypassing locks does not finish round 2’s display-agreement blocker.

2. **MAJOR — the original/final Auto-Fit background-context confusion remains.**

   Revision 3 correctly adds `R.context0`, but **D:811–815 still requires D’s final context and anchors to reproduce `R.request.background` and its original effect**.

   Auto-Fit moves manual anchors during finalisation. For example, a shift delta of `0.01` changes anchors at `280` and `290` to `279.99` and `289.99`. Those cannot equal the original request anchors, even when the selected raw sample indices remain unchanged. This was explicitly identified in round 2 and remains in the operative predicate.

   Evidence: [the remaining check](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:811), [actual anchor migration](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5487).

   **Required:** bind **`R.context0`** to the original request/background effect; separately bind the derived final context to live state. State explicitly which context supplies each background computation.

   There is also a smaller but consequential omission in the “VERIFIED” finalisation recipe: endpoint rounding occurs only when **`delta !== 0`**. D:777–779 states it unconditionally. Preserve that branch and the actual field readers; otherwise zero-delta finalisation can change endpoint fields or sample selection. [Actual branch](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:5465).

3. **MAJOR — step 0 and request normalisation still lack a self-contained reconstruction interface.**

   D:752–756 promises to rebuild the **whole wire request** from `R.pageModel` and `R.context0`. Those declared inputs do not explicitly supply the fit-method selection or upload-generated `session_id`. `_STARTS_UI_FIELDS` excludes the method; both producers obtain the session identifier after uploading.

   More seriously, the specified shared normaliser, `_prepare_fit_request`, **loads the old session file before normalising anything**. Session files expire after seven days. Calling that function as specified cannot verify a saved seal after its session disappears, despite R containing the arrays inline.

   Evidence: [request construction](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:8874), [session-dependent preparation](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/app.py:65), [expiry](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/app.py:241).

   **Required:** factor one preparation function accepting explicit arrays and request settings, shared by fitting and verification. Define transport identifiers separately from the numerical request and specify replay’s fresh upload/session substitution.

   Producer-specific assessment:

   - **Run Fit:** feasible with explicit operation settings and transport handling.
   - **Use this solution:** capture `startPeaks`, as revision 3 now says; snapshot parent lookup is appropriate.
   - **Auto-Fit:** feasible if the deep copy retains `_afCenterMin/Max`, `_afFwhmMin/Max`, names used for anchor selection, and asymmetry overlays. Copying only `_STARTS_MODEL_FIELDS` would omit necessary fields.

4. **MAJOR — HMAC is a sound direction, but the specified attestation is not yet an implementable authentication contract.**

   [D:858–868](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:858) leaves two essential matters undefined.

   **The signed payload.** “Canonical(normalised R, O)” does not say whether normalised R means the complete frontend record or only the server’s numerical arguments. Today the producing server receives neither `R.pageModel` nor `R.context0`, `R.idx`, or `R.producer`. Revision 3 specifies no transport for signing those fields.

   Choose an explicit, versioned payload. If it covers only the normalised numerical problem, state which remaining bindings the page proves. If it covers all R, provide its producer-side capture and transport. Include arrays, complete effective settings, and all acceptance-bearing O fields. Specify ordering, numeric/null encoding and exclusions. Browser round-tripping changes naïve Python JSON spelling—for example `1.0` becomes `1`. The existing [`_canonical`](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/fitting.py:1979) handles relevant spelling differences, but the design does not designate or version it for this protocol.

   **Key lifecycle.** “Created at first start, outside the repository” does not establish persistent, race-safe provisioning across four workers, worker replacement, restarts or deployment. Specify a cryptographically random key, protected durable storage, atomic creation, shared worker access, key identification, rotation/revocation policy and backup/loss behavior. The [separate droplet](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/DEPLOY.md:56) needs an explicit trust decision: independent keys imply the proposed cross-server UNCONFIRMED state; sharing a key makes both installations equally capable of signing.

   The security conclusions are:

   - A complete, unambiguous MAC binding prevents replaying an attested O with a **different normalised numerical R**. Equivalent wire spellings need not count as different problems.
   - Every holder of the HMAC key—including a verifier with that key—can forge producer statements.
   - A leaked-key holder can fabricate a numerically consistent nonminimum, attach `success:true` and `certified:true`, and pass the proposed recomputation. Numerical verification cannot recover search acceptance.
   - Authentication makes numerical checks redundant **for detecting file tampering**, but they still establish consistency under the current verifier and can detect producer defects. Neither authentication nor recomputation replaces the page’s live-data/model/context bindings.
   - Signing must occur over the server’s actual completed result; verification must not become a signing service for caller-supplied R/O.

   Thus round 2’s acceptance finding has a plausible resolution, but cannot yet be marked closed.

The round-2 dispositions are:

| Finding | Revision-3 disposition |
|---|---|
| Snapshot/request binding and expression-held display disagreement | **Partial:** findings 1 and 3 remain |
| Unauthenticated acceptance | **Partial:** finding 4 |
| Auto-Fit original context and finalisation | **Partial:** finding 2 |
| Local chain/objective/committed-snapshot inconsistency | **Resolved in the proposed 0b numerical contract** |
| Verification cached under O alone | **Resolved:** whole frozen seal plus operation ownership |
| “Same code” inferred from metadata | **Resolved:** explicitly verifier-relative consistency |
| Incomplete server background assembly | **Resolved:** one shared complete assembly |
| NaN versus nonfinite shift claim | **Resolved:** actual reader stated; finite seal shift required |

For the remaining review questions:

- **Prerequisites 0b/0c are correctly separated from recording.** 0b changes the optimisation’s objective evaluations and can change fitted parameters, convergence and statistics—not merely final displayed χ². 0c changes displayed linked parameters and subsequent model behavior. Both need measured effects and appropriate versioning; 0c’s scope must include finding 1. Local starting-point designation remains explicit.
- **Numerical contract:** the revised lmfit denominator, floor order, AIC/BIC, residual association and SciPy trapezoid description agree with installed source. `best_fit` is a separate evaluation. An extracted `_npPairwiseSum` probe matched NumPy exactly on 12 arrays spanning lengths 1–100,000; this is bounded evidence, not universal platform proof. Statistics-change magnitudes and LA/DS+G bit-stability remain implementation measurements.
- **Tolerance:** no empirical array-verification tolerance has returned. However, Auto-Fit’s inherited position gate still uses **`0.30 + 1e-6`** ([IH:7787](/Users/skyefortier/xps-app/.claude/worktrees/sealed-v6/templates/index.html:7787)); solver/certificate tolerances, replay comparisons and legacy restore tolerances also remain. “No tolerance anywhere” must stay scoped to the exact verification comparisons.
- **Provenance and migration:** render-input digests resolve the self-hashing problem without proving execution identity. Legacy handling, separate provenance retention, the area-consumer inventory and simultaneous accessor migration remain coherent. Q5’s measurement-before-decision ordering is correct.

Validation was read-only source inspection and bounded production-Python/extracted-JavaScript probes. No full browser suite or 202-target census was run.

**VERDICT: NO-GO.**
