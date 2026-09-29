2026-09-29T18:55:32.778393Z ERROR codex_models_manager::manager: failed to refresh available models: timeout waiting for child process to exit
OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0ee85-abaf-7573-a7d2-b2bc98ced6da
--------
user
Review unit A1 (Find Peaks determinism), round 1: branch fix-find-peaks-determinism, git diff main..HEAD (autofit/engine.py; tests/autofit/test_fit_certificate.py; tests/autofit/test_preseed_dominants.py; CLAUDE.md; docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; the scope-check findings under docs/findings/fit-termination-scope/). Owner's brief: "Find Peaks' answer must not depend on server load or on the optimiser's own termination flags. Count refits, not seconds … REMOVE the warm restart from the cap stall point … apply the certificate to refits. Certificate accepted as proposed: restart from the end point until a restart improves chi2 by less than the optimiser's own stopping tolerance; fixed restart count; out of restarts = 'not converged'. No new constant. Acceptance: identical output under light and heavy load; Scan_6 -> MG2." Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

TRY TO BREAK
a. Load independence: any remaining read of the clock (time.*, perf_counter, deadlines, budgets) that can change the OUTPUT of compare_models / run_stability_analysis / _attempt_proposal / fit_candidate / the bound-fixed override / the Bayesian method / app.py's analyze job; any count that depends on time.
b. The certificate (_certify_minimum): its tolerance is least_squares' own ftol read from scipy; the improvement is relative; restarts use least_squares (the plan explains why not leastsq); keeps the lowest-chi2 point; non-finite or raising restart = not converged; chi2 == 0; a restart that returns a HIGHER chi2; max_nfev per restart; interaction with lmfit's params (bounds, expressions), with covariance / stderr (NaN sigma now reaches the payload as null via _json_sanitize), with FitOutcome consumers (converged, lmfit_result, boundary_hits, components' supports).
c. Every former consumer of the success flag / warm restart / budgets now behaves correctly (screen convergence, deep primary reuse, stability refits, proposals, bound-fixed refits, persistence denominators).
d. The plan's measurements and §3 (the page's request on 7 scans: 3 winners differ from main — two via the screen's single-start ranking, one via the absent-slot BIC* credit): is the reasoning right; is anything there a blocker for shipping A1 as specified?
e. Tests: real and non-vacuous (the certificate tests; the clock-independence test).

Finish with VERDICT: GO or VERDICT: NO-GO.

ERROR: Reconnecting... 2/5
ERROR: Reconnecting... 3/5
codex
I’ll trace the changed fitting paths and their callers, challenge the certificate and clock-independence tests, and give a ranked verdict within this run.

exec
/bin/zsh -lc 'pwd; git status --short; git diff --stat main..HEAD; rg --files -g AGENTS.md -g CLAUDE.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 41ms:
CLAUDE.md

exec
/bin/zsh -lc 'git diff main..HEAD -- autofit/engine.py tests/autofit/test_fit_certificate.py tests/autofit/test_preseed_dominants.py; cat CLAUDE.md; cat docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md; cat docs/findings/fit-termination-scope/README.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-261Lqc6O' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HhxN4J9M' (errno=Operation not permitted)
diff --git a/autofit/engine.py b/autofit/engine.py
index dbf4fd7..65e2be0 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -134,59 +134,22 @@ PROPOSAL_AMPLITUDE_SNR = 5.0
 # keeps those guards and bounds the rounds.  UNVERIFIED tunable.
 PROPOSAL_MAX_PER_CANDIDATE = 3
 PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE = 3
-# Whole ITERATIVE proposal pass per candidate (all F2 rounds share it).
-# Raised 30 → 60 with F2: the pass may now legitimately do up to
-# PROPOSAL_MAX_PER_CANDIDATE accepted rounds of (augmented fit + stability).
-# UNVERIFIED tunable.
-PROPOSAL_CANDIDATE_TIMEOUT_SEC = 60.0
-# One augmented-model stability pass inside the proposal pass.  Replaces the
-# old min(budget, CANDIDATE_TIMEOUT_SEC) clamp, whose 25 s ceiling cut the
-# n_refits=4 stability of a slow augmented model to 3 attempts and QUANTIZED
-# the persistence gate below its threshold — measured on the real C 1s
-# motivating case (PROGRESS.md diagnosis follow-up): a ΔBIC* −86 proposal
-# with no boundary hits was rejected at persistence 2/3 = 0.67 < 0.70 purely
-# because the 4th refit never ran.  35 s fits n_refits=4 at the measured
-# ~7-8 s worst-case per refit on 191-point real data.  UNVERIFIED tunable.
-PROPOSAL_STABILITY_TIMEOUT_SEC = 35.0
-# Minimum budget (s) that must remain before an augmented-model FIT is
-# started inside the proposal pass.  A single fit_candidate at
-# FIT_CANDIDATE_MAX_NFEV runs ~10-12 s worst-case on 191-point data with no
-# internal wall clock, so starting one with less than this left would
-# overrun TOTAL_ANALYSIS_TIMEOUT_SEC — and hence the gunicorn --timeout
-# (Codex c1s-fix review, run B MAJOR).  A proposal attempt that cannot fit
-# this budget fast-rejects with 'insufficient_budget'.  UNVERIFIED tunable.
-PROPOSAL_MIN_FIT_BUDGET_SEC = 15.0
 
 # See fit_candidate() docstring: deterministic per-call ceiling on lmfit's
 # own effort, replacing its effectively-unbounded default.
 FIT_CANDIDATE_MAX_NFEV = 18000
-WARM_RESTART_MAX_NFEV = 2000     # single retry budget for a failed-but-
-                                 # finite fit (measured need: ~33 evals;
-                                 # generous headroom, still bounded)
-
-# Wall-clock ceiling on ONE candidate's entire primary-fit + stability-refit
-# pass (compare_models -> run_stability_analysis). Mirrors
-# PROPOSAL_CANDIDATE_TIMEOUT_SEC's existing per-candidate budget for the
-# later residual-proposal pass: a candidate that blows this budget stops
-# taking further stability refits rather than consuming the rest of the
-# request's time. FIT_CANDIDATE_MAX_NFEV already bounds any single call to
-# roughly 10-12s on this pipeline's DS+G cost profile, so this allows a
-# couple of such calls (primary + 1-2 refits) before cutting the rest.
-CANDIDATE_TIMEOUT_SEC = 25.0
-
-# Wall-clock ceiling on the ENTIRE compare_models sweep over all candidates
-# in the grammar. Per-candidate budgets (CANDIDATE_TIMEOUT_SEC,
-# PROPOSAL_CANDIDATE_TIMEOUT_SEC) bound any one candidate but not their sum
-# — a 29-candidate grammar at ~7s/candidate for ordinary (non-degenerate)
-# fits already runs ~3-4 minutes, and several candidates hitting the
-# DS+G-style degenerate corner push that further. Checked once per outer
-# loop iteration (compare_models): once exceeded, remaining candidates are
-# skipped and the sweep returns best-so-far, ranked normally, with
-# ComparisonResult.analysis_truncated=True — an honest partial result
-# instead of a request timeout. Deliberately below the gunicorn dev
-# --timeout so this truncation path always gets to run and respond before
-# the worker is aborted (see DEPLOY.md / dev gunicorn --timeout).
-TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0
+
+# Unit A1 (2026-09-29): NO wall-clock budget anywhere in the sweep. The
+# per-candidate 25 s, the 240 s sweep, the 60 s / 35 s proposal budgets, the
+# 15 s minimum-fit budget and the screen's share of the sweep all made Find
+# Peaks' ANSWER depend on server load (1-GTA C1s Scan_6: MG2 won or lost on
+# whether its fourth refit started before 25 s). Work is bounded by counts:
+# every candidate is screened once, SCREEN_TOP_K are deep-evaluated with
+# n_refits refits each, a proposal pass makes at most
+# PROPOSAL_MAX_PER_CANDIDATE × PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE attempts,
+# every fit is capped at FIT_CANDIDATE_MAX_NFEV / SCREEN_MAX_NFEV evaluations
+# and certified with at most CERTIFY_MAX_RESTARTS restarts. The page runs
+# Find Peaks as a polled job (/api/analyze/start), so no request waits on it.
 PROPOSAL_ENDPOINT_WARNING_BE = 1.0
 PROPOSAL_COINCIDENCE_BE = 0.5
 
@@ -251,8 +214,8 @@ GRAMMAR_AUGMENT_MAX_SEEDS = 3        # of those, at most this many augment
 # ── Two-phase sweep: screen → stabilize (unit F3, 2026-07-07) ──────────────
 # Measured motivation (PROGRESS.md diagnosis, cause a): a 29-candidate C 1s
 # grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
-# never finish inside TOTAL_ANALYSIS_TIMEOUT_SEC (240 s, deliberately below
-# the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
+# never finish inside the then 240 s sweep budget (removed in unit A1; it sat
+# below the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
 # expert-structure MG family (candidates #21-24) never evaluated.  When the
 # candidate set is larger than SCREEN_TOP_K, compare_models first fits EVERY
 # candidate once (primary fit only, SCREEN_MAX_NFEV effort cap), ranks the
@@ -269,10 +232,6 @@ SCREEN_MAX_NFEV = 6000     # measured: converging primaries on real 191-pt
                            # C 1s data use 3-5k evals; hopeless landscapes
                            # burn ≥ 18k without converging
 SCREEN_TOP_K = 6
-# The screen may spend at most this fraction of TOTAL_ANALYSIS_TIMEOUT_SEC —
-# the deep phase must always retain budget, else a very large (joint) grammar
-# could burn the whole sweep screening and deep-evaluate NOTHING.
-SCREEN_BUDGET_FRACTION = 0.6
 
 
 def _slot_prefix(role: str) -> str:
@@ -849,6 +808,53 @@ def _unphysical_width_flags(
     return flags
 
 
+# ── Convergence certificate (unit A1, 2026-09-29) ─────────────────────────────
+# A fit has reached a minimum when a fresh descent from its end point cannot
+# improve chi2 by more than the descent's OWN stopping tolerance. The descent
+# is Trust-Region (scipy least_squares, native bounds): a Levenberg-Marquardt
+# restart from a stall point reproduces the stall (MINPACK's xtol test fires in
+# ~30 evaluations — the false convergence this replaces). Restarts are repeated
+# from each improved point; a FIXED number of them (a count, not a time); out
+# of restarts, or a non-finite restart, is "not converged". No new constant:
+# the tolerance is scipy's own least_squares ftol default, read from its
+# signature, and the improvement is relative (dimensionless, scale-free).
+import inspect as _inspect
+import scipy.optimize as _scipy_optimize
+CERTIFY_FTOL = float(_inspect.signature(_scipy_optimize.least_squares).parameters["ftol"].default)
+# A COUNT, set from measurement (unit A1, 8 committed C 1s scans × 4 gate
+# candidates, primaries + all refits = 208 fits): restarts needed to certify —
+# 1: 10, 2: 173, 3: 14, 4: 5, then one fit each at 5, 6, 8, 9, 11 and 21 (flat
+# valleys: each Trust-Region run stops on its own ftol while a whole restart
+# still gains more than that). 5 left four real minima uncertified (8-JT
+# Scan_5's MG2 and MG3 primaries, so MG lost to AG2 at chi2r 42.5).
+CERTIFY_MAX_RESTARTS = 50
+
+
+def _certify_minimum(composite, y_sub, result, x, weights, max_nfev):
+    """Return (the lowest-chi2 point reached, certified)."""
+    current = result
+    chi = float(result.chisqr) if result.chisqr is not None else float("nan")
+    if not np.isfinite(chi):
+        return current, False
+    for _ in range(CERTIFY_MAX_RESTARTS):
+        try:
+            r = composite.fit(y_sub, current.params.copy(), x=x, weights=weights,
+                              method="least_squares", nan_policy="omit",
+                              max_nfev=max_nfev)
+        except Exception as exc:
+            log.debug("certificate restart raised: %s", exc)
+            return current, False
+        new = float(r.chisqr) if r.chisqr is not None else float("nan")
+        if not np.isfinite(new):
+            return current, False
+        improvement = (chi - new) / chi if chi > 0 else 0.0
+        if new < chi:
+            current, chi = r, new
+        if improvement < CERTIFY_FTOL:
+            return current, True
+    return current, False
+
+
 def fit_candidate(
     x: np.ndarray,
     y: np.ndarray,
@@ -889,25 +895,13 @@ def fit_candidate(
         result = composite.fit(y_sub, params, x=x, weights=weights,
                                method="leastsq", nan_policy="omit",
                                max_nfev=max_nfev)
-        if (not result.success and result.chisqr is not None
-                and np.isfinite(result.chisqr)):
-            # ONE warm restart (Stage-2, measured on the real diagnosis
-            # scans): a model whose optimum sits against parameter bounds
-            # stalls MINPACK on a flat transformed gradient — it reaches
-            # the minimum, then burns the whole nfev budget without
-            # satisfying ftol (success=False at a genuinely converged
-            # χ²).  Restarting AT the exit point resets leastsq's internal
-            # diag scaling and it certifies in tens of evaluations
-            # (measured: 6000 nfev burned cold → 33 nfev warm, identical
-            # χ²).  Fires ONLY on a failed-but-finite fit, so converging
-            # fits are byte-identical; cost is bounded by one
-            # WARM_RESTART_MAX_NFEV fit.
-            retry = composite.fit(y_sub, result.params.copy(), x=x,
-                                  weights=weights, method="leastsq",
-                                  nan_policy="omit",
-                                  max_nfev=WARM_RESTART_MAX_NFEV)
-            if retry.success:
-                result = retry
+        # Unit A1 (2026-09-29): convergence is CERTIFIED, not read from the
+        # optimiser's flag (_certify_minimum). The old ONE warm restart from a
+        # failed fit's exit point is gone: from a stall point MINPACK's restart
+        # satisfies xtol in ~30 evaluations and reported success at a
+        # non-minimum (8-JT C1s Scan_7: chi2r 37.6 "converged" where
+        # least_squares from the same start reaches 5.21).
+        result, certified = _certify_minimum(composite, y_sub, result, x, weights, max_nfev)
     except Exception as exc:
         log.debug("fit_candidate failed for %s: %s", model.name, exc)
         return FitOutcome(
@@ -917,9 +911,13 @@ def fit_candidate(
             n_data=len(y_sub), lmfit_result=None, background=bg,
         )
 
+    if not certified:
+        # out of restarts (or a non-finite restart): the fit did not reach a
+        # minimum — reported as not converged, whatever the optimiser's flag
+        log.debug("fit_candidate: %s not certified", model.name)
     unweighted_r = y_sub - result.best_fit
     return FitOutcome(
-        converged=bool(result.success),
+        converged=bool(certified),
         components=_extract_fitted_components(result, model),
         residual_sum_sq=float(np.sum(unweighted_r ** 2)),
         weighted_chi_sq=float(result.chisqr) if result.chisqr is not None else float("inf"),
@@ -1144,11 +1142,9 @@ class ModelStability:
     # one-off deeper minimum is a different product than a reproducible one).
     # Reporting-only; never used in ranking.
     best_basin_support: int = 0
-    # How many of the requested n_refits were actually attempted before the
-    # candidate's wall-clock budget (CANDIDATE_TIMEOUT_SEC) ran out. Equal to
-    # n_refits unless timed_out is True — used as the honest denominator for
-    # persistence/orphan_rate/convergence_rate instead of silently
-    # understating them against the full nominal n_refits.
+    # Refits attempted — always n_refits since unit A1 (no wall-clock
+    # budget); the denominator of persistence / orphan_rate / convergence_rate.
+    # timed_out is never set (kept for the payload's shape).
     n_attempted: int = 0
     timed_out: bool = False
 
@@ -1169,16 +1165,16 @@ def run_stability_analysis(
     n_refits: int = 20,
     rng_seed: int = 0,
     fixed_param_values: Optional[dict[str, float]] = None,
-    deadline: Optional[float] = None,
     fit_full_window: bool = False,
     endpoint_avg: int = 1,
 ) -> ModelStability:
     """
-    ``deadline`` is an absolute ``time.perf_counter()`` timestamp (set by
-    the caller from CANDIDATE_TIMEOUT_SEC) shared across this candidate's
-    primary fit + all its refits. Once passed, remaining refits are
-    skipped — not run and not counted as failures — so one candidate stuck
-    in a slow-but-nfev-capped region can't consume the rest of the request.
+    Unit A1 (2026-09-29): exactly ``n_refits`` refits, always — no wall-clock
+    deadline. The 25 s per-candidate budget this replaced made persistence
+    (refits reached / refits attempted) depend on server load: on 1-GTA C1s
+    Scan_6 MG2 got 3 or 4 refits depending on how busy the machine was, and
+    2/3 vs 3/4 decided the winner. Work is bounded by counts (n_refits, each
+    fit's max_nfev, the certificate's restarts).
     """
     rng = np.random.default_rng(rng_seed)
     pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
@@ -1205,14 +1201,6 @@ def run_stability_analysis(
     n_attempted = 0
     timed_out = False
     for _ in range(n_refits):
-        if deadline is not None and time.perf_counter() >= deadline:
-            timed_out = True
-            log.warning(
-                "run_stability_analysis: candidate %s hit its %.0fs budget "
-                "after %d/%d refits — remaining refits skipped",
-                model.name, CANDIDATE_TIMEOUT_SEC, n_attempted, n_refits,
-            )
-            break
         n_attempted += 1
         seed = int(rng.integers(0, 2**31 - 1))
         init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
@@ -1616,11 +1604,9 @@ class ComparisonResult:
     # weighted_bic_top, note} or None (BIC/IC math review blocker:
     # selection must not silently rest on a likelihood the fits reject).
     weighted_ic_disagreement: Optional[dict] = None
-    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
-    # evaluating every candidate in the grammar. The candidates evaluated so
-    # far are still ranked/reported normally (best-so-far) — this only flags
-    # that the comparison is partial, so a slow/pathological spectrum
-    # returns an honest incomplete result instead of a request timeout.
+    # Never set since unit A1 (the sweep budget it reported is gone: every
+    # candidate is evaluated); kept so the payload and the page keep their
+    # shape.
     analysis_truncated: bool = False
     n_candidates_evaluated: int = 0
     n_candidates_total: int = 0
@@ -2166,11 +2152,12 @@ def _attempt_proposal(
     absent_slot_area_fraction: float,
     absent_slot_persistence_threshold: float,
     diagnostic_windows: dict[str, tuple[float, float]],
-    budget_remaining: float = float("inf"),
     fit_full_window: bool = False,
     endpoint_avg: int = 1,
 ) -> tuple[Optional[ModelReport], ProposedPeakReport, str]:
-    attempt_start = time.perf_counter()
+    # Unit A1 (2026-09-29): no wall-clock budget — an attempt either runs its
+    # counted work (one augmented fit, n_refits refits) or is rejected on a
+    # data criterion; whether a proposal is accepted must not depend on load.
     base_model = base_report.model
     base_fit = base_report.primary_fit
     aug_model = _augmented_candidate(base_model, spec)
@@ -2187,16 +2174,6 @@ def _attempt_proposal(
         pr.rejection_reason = reason
         return None, pr, "fast_rejected"
 
-    # An augmented fit_candidate has no internal wall clock and runs
-    # ~10-12 s worst-case; starting one with less than PROPOSAL_MIN_FIT_
-    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
-    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
-    # caller passes budget_remaining = min(pass budget, sweep budget) left.
-    if budget_remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
-        return _fast(
-            f"insufficient_budget: {budget_remaining:.1f}s left < "
-            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")
-
     bg = _compute_background(x, y, aug_model.background, endpoint_avg=endpoint_avg)
     try:
         init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
@@ -2251,28 +2228,9 @@ def _attempt_proposal(
             f"base BIC* {base_report.bic_adjusted:.2f} by {PROPOSAL_DELTABIC_THRESHOLD:.1f}"
         )
 
-    # budget_remaining was a snapshot BEFORE the augmented fit; that fit has
-    # since consumed wall time, so the stability deadline must be computed
-    # from what's ACTUALLY left, not the stale snapshot (Codex c1s-fix
-    # review, run B MAJOR — otherwise the stability pass could run
-    # min(stale_budget, 35) s past the fit and overrun the sweep budget).
-    # The floor (not just <= 0) matters because run_stability_analysis
-    # checks its deadline at the TOP of the loop and then runs an unbounded
-    # fit_candidate — so starting stability with only a few seconds left
-    # would still overrun by ~one worst-case fit (Codex c1s-fix RE-CHECK,
-    # run B MAJOR: disposition 2 was not fully closed by the top guard).
-    remaining = budget_remaining - (time.perf_counter() - attempt_start)
-    if remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
-        pr.rejection_reason = (
-            f"insufficient_budget before stability: {remaining:.1f}s left < "
-            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s (one refit could overrun)")
-        return None, pr, "fast_rejected"
-
     stability = run_stability_analysis(
         x, y, weights, aug_model, primary,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-        deadline=time.perf_counter() + min(remaining,
-                                           PROPOSAL_STABILITY_TIMEOUT_SEC),
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2445,7 +2403,6 @@ def _bound_fixed_refit(
         x, y, weights, report.model, outcome,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
         fixed_param_values=fixed,
-        deadline=time.perf_counter() + CANDIDATE_TIMEOUT_SEC,
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2738,7 +2695,6 @@ def compare_models(
     proposal_attempts: list[tuple[str, ProposedPeakReport]] = []
     timings: list[ProposalPassTiming] = []
     n_cand = len(candidates)
-    sweep_start = time.perf_counter()
     n_evaluated = 0
     analysis_truncated = False
 
@@ -2750,16 +2706,9 @@ def compare_models(
     if n_cand > SCREEN_TOP_K:
         screen_rows: list[dict] = []
         screened: list[tuple[CandidateModel, FitOutcome, float]] = []
-        screen_deadline = sweep_start + SCREEN_BUDGET_FRACTION * TOTAL_ANALYSIS_TIMEOUT_SEC
+        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
+        # which candidates reached the deep phase used to depend on load)
         for idx, model in enumerate(candidates, 1):
-            if time.perf_counter() > screen_deadline:
-                analysis_truncated = True
-                log.warning(
-                    "compare_models: screen budget (%.0f%% of the sweep) "
-                    "exhausted after %d/%d candidates — the deep phase runs "
-                    "on what screened so far",
-                    100 * SCREEN_BUDGET_FRACTION, idx - 1, n_cand)
-                break
             log.info("[screen %2d/%d] %s", idx, n_cand, model.name)
             _report_progress(progress_cb, "screening", idx, n_cand, model.name)
             outcome = fit_candidate(x, y, weights, model,
@@ -2789,30 +2738,11 @@ def compare_models(
             [m.name for m in candidates])
 
     for idx, model in enumerate(candidates, 1):
-        # Pre-check with the candidate's own worst-case budget: a candidate
-        # STARTED just under the wire used to overshoot the sweep budget by
-        # its full stability + proposal cost (measured 310 s wall vs the
-        # 240 s budget on real data — past the gunicorn --timeout 300, i.e.
-        # the exact worker-kill this budget exists to prevent).  Truncating
-        # BEFORE starting a candidate that cannot finish keeps the worst-case
-        # wall ≈ TOTAL_ANALYSIS_TIMEOUT_SEC.
-        elapsed = time.perf_counter() - sweep_start
-        if elapsed > TOTAL_ANALYSIS_TIMEOUT_SEC - CANDIDATE_TIMEOUT_SEC:
-            analysis_truncated = True
-            log.warning(
-                "compare_models: sweep budget cannot fit another candidate "
-                "(%.0fs elapsed of %.0fs) after %d/%d — remaining candidates "
-                "skipped, returning best-so-far",
-                elapsed, TOTAL_ANALYSIS_TIMEOUT_SEC, n_evaluated, len(candidates),
-            )
-            break
+        # Unit A1: every selected candidate is evaluated — no sweep budget
         n_evaluated += 1
         log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
         _report_progress(progress_cb, "stabilizing", idx, len(candidates),
                          model.name)
-        # Shared wall-clock budget for this candidate's primary fit + all its
-        # stability refits (CANDIDATE_TIMEOUT_SEC) — see run_stability_analysis.
-        candidate_deadline = time.perf_counter() + CANDIDATE_TIMEOUT_SEC
         # reuse the screen fit as this candidate's primary (no repeated work)
         primary = screen_fit.get(model.name) or fit_candidate(
             x, y, weights, model, fit_full_window=fit_full_window,
@@ -2824,7 +2754,6 @@ def compare_models(
         stability = run_stability_analysis(
             x, y, weights, model, primary,
             noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-            deadline=candidate_deadline,
             fit_full_window=fit_full_window,
             endpoint_avg=endpoint_avg,
         )
@@ -2864,20 +2793,12 @@ def compare_models(
             # per-candidate wall budget.  Gates are unchanged per round.
             counts = dict(n_flagged=0, n_over_cap=0, n_attempted=0,
                           n_fast=0, n_stab=0, n_acc=0)
-            timed_out = False
-            pass_start = time.perf_counter()
-            # the pass never spends beyond the sweep's remaining budget —
-            # same worst-case-wall reasoning as the candidate pre-check
-            pass_budget = min(
-                PROPOSAL_CANDIDATE_TIMEOUT_SEC,
-                TOTAL_ANALYSIS_TIMEOUT_SEC - (pass_start - sweep_start))
+            timed_out = False                 # unit A1: never set (no pass budget)
+            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
             rejected: list[ProposedPeakReport] = []
             current = base_report
             current_y_fit = y_fit
             while counts["n_acc"] < PROPOSAL_MAX_PER_CANDIDATE:
-                if time.perf_counter() - pass_start > pass_budget:
-                    timed_out = True
-                    break
                 specs = _detect_residual_proposals(
                     x, y, current_y_fit, noise_floor, current.model,
                     fitted_components=current.primary_fit.components,
@@ -2894,10 +2815,6 @@ def compare_models(
                 counts["n_over_cap"] += max(len(specs) - len(attempts), 0)
                 accepted_this_round = False
                 for spec in attempts:
-                    elapsed = time.perf_counter() - pass_start
-                    if elapsed > pass_budget:
-                        timed_out = True
-                        break
                     counts["n_attempted"] += 1
                     aug_report, pr, outcome = _attempt_proposal(
                         x=x, y=y, weights=weights, base_report=current, spec=spec,
@@ -2905,7 +2822,6 @@ def compare_models(
                         absent_slot_area_fraction=absent_slot_area_fraction,
                         absent_slot_persistence_threshold=absent_slot_persistence_threshold,
                         diagnostic_windows=diagnostic_windows,
-                        budget_remaining=pass_budget - elapsed,
                         fit_full_window=fit_full_window,
                         endpoint_avg=endpoint_avg,
                     )
diff --git a/tests/autofit/test_fit_certificate.py b/tests/autofit/test_fit_certificate.py
new file mode 100644
index 0000000..950ac4d
--- /dev/null
+++ b/tests/autofit/test_fit_certificate.py
@@ -0,0 +1,137 @@
+"""Unit A1 (2026-09-29): Find Peaks judges convergence by a CERTIFICATE, not the
+optimiser's flag. A fit has reached a minimum when a fresh Trust-Region descent
+from its end point improves chi2 by less than that descent's own stopping
+tolerance (scipy least_squares' ftol); restarts repeat from each improved point
+up to CERTIFY_MAX_RESTARTS; out of restarts = not converged. The flag was wrong
+both ways: a warm restart from a stall "succeeded" in ~30 evaluations at
+chi2r 37.6 where the minimum is 5.21 (8-JT C1s Scan_7), and a refit capped at
+18 000 evaluations AT the minimum counted as failed (1-GTA C1s Scan_6)."""
+import inspect
+import os
+
+import numpy as np
+import pytest
+import scipy.optimize
+
+import autofit.engine as eng
+from autofit.grammar import MaterialClass, Phase, resolve
+from autofit.methods.base import poisson_like_weights
+from autofit.reference import load_reference_fits
+
+DATA = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "autofit", "test_data")
+G = resolve([Phase(id="graphite", material_class=MaterialClass.CONDUCTOR, regions=("C 1s",), material="graphite")], "C 1s")
+
+
+def _scan(project, name):
+    rf = next(r for r in load_reference_fits(os.path.join(DATA, project)) if r.name == name)
+    x, y = np.asarray(rf.roi_be, float), np.asarray(rf.roi_intensity, float)
+    return x, y, poisson_like_weights(y)
+
+
+def _mg2():
+    return next(c for c in G.candidates if c.name == "MG2_graphAsymGL_aliph_sat_CO_C=O")
+
+
+def test_the_tolerance_is_the_optimisers_own():
+    assert eng.CERTIFY_FTOL == inspect.signature(scipy.optimize.least_squares).parameters["ftol"].default
+    assert isinstance(eng.CERTIFY_MAX_RESTARTS, int) and eng.CERTIFY_MAX_RESTARTS >= 1
+
+
+def _kkt_violations(comp, params, x, y_net, w):
+    """Parameters along which chi2 still descends: a free parameter with a
+    non-negligible gradient, or one on a bound whose gradient points INTO the
+    box. Empty = a (constrained) local minimum."""
+    chi = lambda pp: float(np.sum(((y_net - comp.eval(pp, x=x)) * w) ** 2))
+    c0, bad = chi(params), []
+    for n, p in params.items():
+        if not p.vary or p.expr is not None:
+            continue
+        span = (p.max - p.min) if np.isfinite(p.max) and np.isfinite(p.min) else (abs(p.value) or 1.0)
+        h = 1e-6 * span
+        q = params.copy()
+        if p.value - p.min < 1e-9 * span:
+            q[n].set(value=p.value + h)
+            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
+        elif p.max - p.value < 1e-9 * span:
+            q[n].set(value=p.value - h)
+            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
+        else:
+            q[n].set(value=p.value + h); cp = chi(q); q[n].set(value=p.value - h); cm = chi(q)
+            if abs(cp - cm) / (2 * h) * span > 1e-3 * c0: bad.append(n)
+    return bad
+
+
+def test_a_stall_now_ends_at_a_constrained_local_minimum():
+    """Scan_7 MG2, stability refit 0's start. The removed warm restart
+    reported success at the leastsq stall point (chi2 5220), which is NOT a
+    minimum: a descent still lowers chi2. The certified point satisfies the
+    KKT conditions (free gradients ~0, every parameter on a bound pushing out):
+    a genuine local minimum, pinned on bounds (chi2r ~37 — a worse basin than
+    the 5.21 least_squares finds from the same start by another path)."""
+    x, y, w = _scan("8-JT Graphite.proj.zip", "C1s Scan_7")
+    model = _mg2()
+    primary = eng.fit_candidate(x, y, w, model)
+    y_net = y - primary.background
+    seed = int(np.random.default_rng(0).integers(0, 2**31 - 1))
+    init = eng.perturb_initial_params(model, seed=seed, x=x, y_net=y_net)
+    comp = eng._build_composite_model(model)
+    stall = comp.fit(y_net, init.copy(), x=x, weights=w, method="leastsq", nan_policy="omit",
+                     max_nfev=eng.FIT_CANDIDATE_MAX_NFEV)
+    assert _kkt_violations(comp, stall.params, x, y_net, w), "the stall point is not a minimum"
+    out = eng.fit_candidate(x, y, w, model, initial_params=init.copy())
+    assert out.converged
+    assert out.weighted_chi_sq < stall.chisqr
+    assert _kkt_violations(comp, out.lmfit_result.params, x, y_net, w) == []
+
+
+def _two_peak():
+    x = np.arange(280.0, 292.0, 0.05)
+    t = 500 + 8000 * np.exp(-4 * np.log(2) * ((x - 284.5) / 1.0) ** 2) + 1500 * np.exp(-4 * np.log(2) * ((x - 286.4) / 1.2) ** 2)
+    y = t + np.sqrt(t) * np.random.default_rng(5).standard_normal(x.size)
+    slot = lambda r, win: eng.ComponentSlot(role=r, region="C 1s", phase_id="p", be_window=win,
+                                            line_shape=eng.LineShape.GAUSSIAN, fwhm_range=(0.5, 2.5))
+    model = eng.CandidateModel(name="m", background=eng.BackgroundType.LINEAR,
+                               slots=(slot("a", (284.0, 285.0)), slot("b", (286.0, 287.0))))
+    return x, y, poisson_like_weights(y), model
+
+
+def test_a_fit_capped_at_the_minimum_is_certified():
+    """The Scan_6 case in general form: an optimiser that runs out of
+    evaluations while sitting at the minimum reports failure; the certificate
+    finds no descent and certifies it."""
+    x, y, w, model = _two_peak()
+    good = eng.fit_candidate(x, y, w, model)
+    assert good.converged
+    comp = eng._build_composite_model(model)
+    y_sub = y - good.background
+    capped = comp.fit(y_sub, good.lmfit_result.params.copy(), x=x, weights=w, method="leastsq",
+                      nan_policy="omit", max_nfev=3)          # starts AT the minimum, capped at once
+    assert not capped.success
+    point, certified = eng._certify_minimum(comp, y_sub, capped, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
+    assert certified
+    assert point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)
+
+
+def test_out_of_restarts_is_not_converged(monkeypatch):
+    """A start far from the minimum needs more than one restart to certify
+    (the first descends a long way); with a single restart allowed it is
+    'not converged' — whatever the optimiser says."""
+    x, y, w, model = _two_peak()
+    comp = eng._build_composite_model(model)
+    good = eng.fit_candidate(x, y, w, model)
+    y_sub = y - good.background
+    far = good.lmfit_result.params.copy()
+    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
+    short = comp.fit(y_sub, far, x=x, weights=w, method="leastsq", nan_policy="omit", max_nfev=2)
+    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 1)
+    _, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
+    assert not certified
+    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 5)
+    point, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
+    assert certified and point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)
+
+
+def test_the_warm_restart_is_gone():
+    src = inspect.getsource(eng.fit_candidate)
+    assert "retry" not in src and "WARM_RESTART" not in src
+    assert "converged=bool(certified)" in src
diff --git a/tests/autofit/test_preseed_dominants.py b/tests/autofit/test_preseed_dominants.py
index 74ec475..596c3a6 100644
--- a/tests/autofit/test_preseed_dominants.py
+++ b/tests/autofit/test_preseed_dominants.py
@@ -345,8 +345,7 @@ def test_proposal_rejected_when_stability_promotes_spurious_center_peg(monkeypat
         x=x, y=y, weights=w, base_report=base, spec=spec,
         noise_floor=1.0, n_refits=2, rng_seed=0,
         absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
-        diagnostic_windows=dict(case.grammar.diagnostic_windows),
-        budget_remaining=1e6)
+        diagnostic_windows=dict(case.grammar.diagnostic_windows))
     assert outcome == "stability_rejected"
     assert "post-stability" in (pr.rejection_reason or "")
     assert any("center@min" in h for h in pr.boundary_hits)
@@ -418,80 +417,30 @@ def test_next_proposal_index_is_max_suffix_plus_one():
     assert eng._next_proposal_index(m0) == 0
 
 
-def test_proposal_pass_respects_sweep_budget(monkeypatch):
-    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
-    clock, so a proposal attempt must fast-reject when too little sweep
-    budget remains rather than running an unbounded fit past the total
-    timeout.  With the fit-budget floor raised above any real remaining
-    budget, EVERY proposal attempt must be 'insufficient_budget' — no
-    augmented fit runs, no proposal is accepted, and the sweep still
-    returns cleanly."""
-    monkeypatch.setattr(eng, "PROPOSAL_MIN_FIT_BUDGET_SEC", 10_000.0)
+def test_no_wall_clock_can_change_the_answer(monkeypatch):
+    """Unit A1 (2026-09-29): the sweep, screen, stability and proposal
+    budgets were wall-clock and made the answer depend on server load; they
+    are gone. A clock that jumps a million seconds on every read must leave
+    the result IDENTICAL."""
     x = _grid()
     truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
              {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
     sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
     y = _noisy(sig + _linear_bg(x), 71)
-    cands = [_cand("single_main", [_slot("main_a", (195.5, 197.5))])]
-    grammar = _grammar(cands)
-    res = get_method("ic_model_comparison").run(
-        x, y, grammar=grammar,
-        options={**IC_OPTS, "enable_preseed": False})
-    assert not res.diagnostics["winner"].endswith("+prop")
-    reasons = [p["rejection_reason"] for c in res.analysis["candidates"]
-               for p in c.get("proposed_peaks", [])]
-    assert reasons, "expected at least one attempted-then-rejected proposal"
-    assert all("insufficient_budget" in (r or "") for r in reasons), reasons
-
-
-def test_stability_not_started_without_budget_after_augmented_fit(monkeypatch):
-    """Codex c1s-fix RE-CHECK (run B): the top budget guard alone did NOT
-    close the overrun — an augmented fit that PASSES the top guard then
-    consumes most of the budget must not let run_stability_analysis start
-    an unbounded refit with only a few seconds left.  The pre-stability
-    guard now fast-rejects when the DYNAMIC remaining budget is below the
-    fit floor.  Deterministic via a fake clock: attempt_start = 1000 s,
-    every later perf_counter reads 1013 s, so with budget_remaining=20 the
-    post-fit remaining is 7 s < 15 s floor — stability must NOT run."""
-    from autofit.methods.base import poisson_like_weights
-    from stress_cases import isolated_missing_peak_case
+    grammar = _grammar([_cand("single_main", [_slot("main_a", (195.5, 197.5))])])
 
-    case = isolated_missing_peak_case(seed=71)
-    x, y = case.x, case.y
-    w = poisson_like_weights(y)
-    model = case.grammar.candidates[0]
-    # real base report (unpatched clock), proposal + preseed off
-    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
-                             enable_proposal_pass=False, enable_preseed=False)
-    base_report = res.reports[0]
-    y_fit = (base_report.primary_fit.lmfit_result.best_fit
-             + base_report.primary_fit.background)
-    specs = eng._detect_residual_proposals(
-        x, y, y_fit, 1.0, model,
-        fitted_components=base_report.primary_fit.components)
-    assert specs, "expected a residual proposal at the unmodeled peak"
-
-    calls = {"n": 0}
+    def run():
+        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
+        return res.diagnostics, res.peaks, res.analysis, res.confidence
 
-    def fake_pc():
-        calls["n"] += 1
-        return 1000.0 + (0.0 if calls["n"] == 1 else 13.0)
+    normal = run()
+    ticks = {"t": 0.0}
 
-    def boom(*a, **k):
-        raise AssertionError("run_stability_analysis started without budget")
-
-    monkeypatch.setattr(eng.time, "perf_counter", fake_pc)
-    monkeypatch.setattr(eng, "run_stability_analysis", boom)
-
-    aug_report, pr, outcome = eng._attempt_proposal(
-        x=x, y=y, weights=w, base_report=base_report, spec=specs[0],
-        noise_floor=1.0, n_refits=4, rng_seed=0,
-        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
-        diagnostic_windows=dict(case.grammar.diagnostic_windows),
-        budget_remaining=20.0)          # passes the 15 s TOP guard...
-    assert outcome == "fast_rejected"   # ...but post-fit remaining 7 s < 15
-    assert aug_report is None
-    assert "insufficient_budget before stability" in (pr.rejection_reason or "")
+    def jumpy():
+        ticks["t"] += 1.0e6
+        return ticks["t"]
+    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
+    assert run() == normal
 
 
 # ── F3: two-phase sweep ────────────────────────────────────────────────────
# XPS Fitting Studio

Web application for XPS (X-ray Photoelectron Spectroscopy) peak fitting,
multi-spectrum visualization, and project management. Python/Flask backend
with an lmfit-driven peak-fitting pipeline; single-page frontend in
`templates/index.html`. Deployed at xps.fortierlab.org via a gunicorn
LaunchAgent + Cloudflare Tunnel.

## Stack

- **Backend:** Python/Flask, served by gunicorn. App factory in [app.py](app.py).
- **Fitting engine:** lmfit ≥ 1.3 (5 methods: leastsq, least_squares, nelder, differential_evolution, basinhopping).
- **Numerics:** numpy, scipy.
- **File parsing:** pandas, openpyxl (xlsx), olefile (vgd).
- **Frontend:** Single-page HTML/JS in `templates/index.html` (~8500 LOC). Vanilla JS, no build step.
- **Charting:** Chart.js 4.4 (CDN).
- **Deployment:** macOS LaunchAgent runs gunicorn on **127.0.0.1:5050** (NOT :5000 — macOS AirTunes intercepts :5000 and returns 403, so health-check :5050); Cloudflare Tunnel publishes to xps.fortierlab.org. Dev gunicorn typically runs on :5151 with `--reload` for pre-merge verification. See [DEPLOY.md](DEPLOY.md) for the full deploy sequence.

## Project Layout

```
app.py                    # Flask app factory + REST routes
fitting.py                # lmfit pipeline, lineshape impls, background algorithms
parser.py                 # File parsers (csv / tsv / txt / xy / xlsx / xls / vgd)
vgd_parser.py             # Thermo Avantage VGD binary parser (uses olefile)
templates/index.html      # Frontend — CSS + HTML + JS in one file
tests/                    # pytest suite (focused on LA + DS+G correctness)
docs/superpowers/plans/   # Agent-authored design memos and implementation plans
uploads/                  # Per-session .npz storage (gitignored)
requirements.txt
venv/                     # virtualenv (do not commit)
```

The Flask backend serves the frontend via `render_template('index.html')`
and exposes a REST API consumed by the page through fetch.

## Backend API

Per-upload sessions store parsed `(energy, counts)` arrays as compressed
`.npz` in `uploads/<session_id>.npz`. No server-side memory state —
compatible with multi-worker gunicorn.

| Method | Path | Purpose |
|---|---|---|
| `GET`    | `/`                       | Serve the frontend (`templates/index.html`). |
| `GET`    | `/api/health`             | Liveness probe. Returns `{status: "ok"}`. |
| `GET`    | `/api/peak-shapes`        | List backend-registered lineshapes (gaussian / lorentzian / pseudo_voigt_gl / asymmetric_gl / doniach_sunjic / ds_g / la_casaxps). |
| `GET`    | `/api/elements`           | Spin-orbit element presets (splitting + area ratio). |
| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
| `POST`   | `/api/parse-vgd`          | Parse Thermo Avantage VGD binary directly (no session storage). |
| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
| `DELETE` | `/api/session/<id>`       | Delete session files. |
| `POST`   | `/api/background`         | Compute background curve for a session. |
| `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |
| `POST`   | `/api/fit/start`          | The same request and validation as `/api/fit` (an immediate identical 400 / 404); runs the SAME `run_fit` in a background thread; returns `{job_id}` 202 (unit 2, 2026-09-27). |
| `GET`    | `/api/fit/progress/<id>`  | The job record: `status` running / done / error / cancelled, `elapsed_sec`, `heartbeat_age_sec`; `result` = exactly the `/api/fit` body; `error` + `http_status` = exactly what `/api/fit` would answer. |
| `POST`   | `/api/fit/cancel/<id>`    | Stop the job (every minimisation aborts via lmfit's `iter_cb`); also automatic after 180 s without a poll. |

## Frontend Architecture

### State

Module-global `state` holds the currently-active tab's working values
(swapped on tab switch by `TabManager.activateTab`):

```js
state = {
  rawBE, rawIntensity,   // full spectrum as loaded
  ccShift,               // charge-correction rigid shift (eV)
  peaks[],               // array of peak objects
  nextId,                // auto-increment peak ID
  chart,                 // Chart.js instance
  residChart,            // Residuals sub-chart instance
  fitResult,             // last fit diagnostics (be, bgIntensity, bgSubtracted, fittedY, chi, etc.)
  lineWidth,             // per-tab line width (sync of tab.lineWidth)
}
```

### Tab model

`TabManager` (a class in `templates/index.html`) holds `tabs[]` and an
`activeId`. Two tab types share the array:

- **Spectrum tab:** has `rawBE`, `rawIntensity`, `peaks`, `fitResult`, `ccShift`, `manualAnchors`, `lineWidth`, `ui` (form field snapshot incl. bg settings, ROI, charge correction method).
- **Stack tab** (`isStack: true`): viewer-only container for references to other spectrum tabs. Has `entries[{id, sourceTabId, color, visible, showFit}]`, `lineWidth`, `verticalOffset`, `_nextColorIdx`. No raw data of its own — entries resolve their source tab at render time.

Lifecycle: `createTab`, `createStackTab`, `activateTab`, `closeTab`,
`_syncActiveToRecord` (writes state-back-to-tab on switch-away). Drag-and-drop
tab reordering exists.

### Peak Object Schema — core fields

(Non-exhaustive. Additional optional fields appear for multiplet linkage, fix-flags per parameter, auto-fit asymmetry bounds, etc. Search the source for `defaultPeak` to see the full shape.)

```js
{
  id, name, color, visible,
  center, fwhm, amplitude,
  shape,       // 'Gaussian'|'Lorentzian'|'Voigt'|'GL'|'asym-GL'|'DS'|'DSG_LA'|'LACX'
  glMix,       // 0–100 (Gauss → Lorentz)
  asymmetry,   // asym-GL asymmetry index
  dsAlpha, dsGamma,                       // DS params
  laAlpha, laBeta, laM,                   // DS+G params (laAlpha=α, laBeta=Lorentzian half-width, laM=Gauss FWHM)
  caAlpha, caBeta, caM,                   // CasaXPS LA params (caM is in DATA POINTS, not eV)
  linked, linkOffset, linkRatio,          // multiplet linkage to parent peak
  isChargeReference,                      // marks this peak as the cc anchor
}
```

### Lineshapes

| ID | Description |
|----|-------------|
| `Gaussian` | Pure Gaussian |
| `Lorentzian` | Pure Lorentzian |
| `Voigt` | Pseudo-Voigt, fixed η = 0.5 on BOTH sides (A03, 2026-09-22: the request sends `gl_ratio: 0.5, fix_gl_ratio: true`; until then the server fitted η FREE from 0.3 while the page drew, integrated and exported 0.5). Use `GL` to fit the mix. |
| `GL` | Pseudo-Voigt with adjustable GL mixing (0–100) |
| `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
| `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
| `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + Gauss conv with a CONTINUOUS m (data points; σ = m/3, half-width ⌈3.5σ⌉) on both sides since the caM unit (2026-09-25). Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |

**What the page draws must be what the server fitted.** Two harnesses pin
it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
page's own `peakToBackendSpec`, fits it with `fitting.run_fit`, applies the
result with `_applyBackendParams` and requires `evalPeakArray` on the fitted
grid to equal `individual_peaks[].y` for every shape (it also pins the
Python twin `autofit.reference.peak_to_backend_spec` to the page's builder,
shape by shape); section (D) of `tests/js/lineshape_parity.test.js` sweeps
each shape's FREE parameters across the fit's bounds. Both were added in A03
(2026-09-22) after a "Voigt" was found to be fitted with η free while drawn
at 0.5; the same harnesses then found `p.glMix || 50` / `p.dsAlpha || 0.1`
sending a mix or α of exactly 0 as the default, lmfit clipping a HELD value
to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
`_make_peak_params._set` now widens a limit to a held value), and the
server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
held parameter is held at its value; what the page draws is what the
server fitted. No shape carries a tracked gap any more. LACX with m > 0 was
the last (the page drew m rounded to an integer 2m+1 kernel while the
server fits it continuously: up to 0.97 % of amplitude and 1.2 % of area on
the lab's U 4f components) until the `caM` unit, 2026-09-25:
`laTrueCasaXPS_array` now mirrors `_la_casaxps_true` (continuous σ = m/3,
half-width max(1, ⌈3.5σ⌉), `np.convolve` 'same' with the server's trim,
normalisation at the grid point nearest the centre) — ≤ 7e-16 of amplitude
on all 108 committed LA components, pinned across the α/β/m box on seven
grids incl. grids shorter than the kernel
(`docs/superpowers/plans/2026-09-25-cam-continuous.md`). DS+G was the other gap until 2026-09-22 (the page's quadrature
`laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
in area on the very box Find Peaks emits for a graphitic C 1s line);
`dsgConvolved_array` now mirrors the server's padded-grid convolution for
every m — the same FFT circular convolution — pinned at 1e-6 across the
full β/m box on eight grids, irregular grids and centres outside the
window (`docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md`). Two
server limits found there: a DS+G m just above the 0.001 delta threshold
on a coarse grid (m ≤ 0.003 at 0.1 eV, even padded length) underflows the
kernel and returns an all-zero curve — left as is, it reads as a
zero-amplitude component and step (b) flags it; and a centre OUTSIDE the
padded grid was normalised by rounding noise — fixed 2026-09-25 by a NEW
GUARDED BRANCH (normalise by the maximum), proven byte-identical for every
in-range centre against main's function (`scripts/dsg_outside_centre_identity.py`). Details of
A03 in `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.

---

## Design Rules

### Thresholds on data-scaled quantities fail

XPS spans many orders of magnitude within one spectrum, so any absolute
floor, delta or exactness cutoff will misjudge at some dynamic range. Two
units learned this independently — five intensity floors on the Auto-Fit
anchor (answer: a scale-free F test), then two tolerances on that F test
(answer: none). Prefer a scale-free comparison with no tolerance. If a
check seems to need a magnitude threshold, that is evidence the check is
formulated wrong.

(Owner, 2026-09-22. The record: the anchor unit's six Codex rounds in
`docs/autofit/codex/autofit_zero_graphite_*`, the DE unit's tolerance rounds
5–8 in `de_finite_bounds_*`, and the required-refit unit's rounds 2–3 in
`autofit_required_*`. The DE unit is the same rule seen from the other
side: every χ² comparison tolerance produced reachable false failures and
no reachable protection, and the fix was to delete the comparison.)

### Two readings of one field

When two places read the same input — the page and the server, a preview
and a fit, a comparison and the thing it compares — they must read it the
same way, or equivalent inputs get treated as different and different inputs
as equivalent. The instances so far: a "Voigt" meant η = 0.5 to the page and
a free η to the server (A03); the ROI, the preview background and the fitted
background meant three different point sets until one inclusive-bound
definition (`_bgWindowIndices`, sealed-fit-record memo Part 3); and in F1 the
fit key compared form numbers with `Number()` while the background code reads
the iteration and averaging counts with `parseInt()`, so typing "3e1" (read
as 3) matched a fit made at 30 (Codex round 2,
`docs/autofit/codex/f1_stale_statistics_r2_verdict_run{A,B}.md`). A comparison
must read each field exactly the way its consumer reads it — integers as
integers, energies through `parseFloat` — never a generic conversion
(`_fitKeyCanon`). (Owner, 2026-09-26.)

### Long fits start and poll (unit 2, 2026-09-27)

Run Fit (incl. "Use this solution") and Auto-Fit never hold a request open
for a fit: `_serverFitJob` starts it (`/api/fit/start`), polls every 0.5 s
and reads the finished record's `result` (the `/api/fit` body) with F2's
`_readFitReply` rules. So no request meets the public ~100 s ceiling (the five
largest C 1s basinhopping models completed in 213–414 s through the poll
path with no request longer than 0.28 s). Server: Find Peaks' job records
(atomic JSON under the upload folder, readable by any worker), a fit thread
and a 2 s heartbeat thread per job; `run_fit(cancel=)` gives every
`model.fit` an `iter_cb` that aborts once the job is cancelled — without it
the calls are made exactly as before (Levenberg-Marquardt byte-identical
either way). Page: the ownership rules run INSIDE the poll loop (a switched
tab or an edited model cancels the job and discards with the usual message);
a START that cannot reach the server is still a transport failure (local
fallback); a poll that cannot is retried, five in a row are; a stopped
heartbeat (> 30 s) is a failed fit; a closed page sends a cancel beacon, and
the server cancels a job nobody has polled for 180 s (above the ~1-minute
timer throttling of hidden browser tabs). A new start for the same tab
supersedes (cancels) the previous one — Auto-Fit only once its preflight has
passed, so a refused Auto-Fit leaves a running Run Fit alone; the spinner
belongs to the operation that showed it (Batch Fit shows none and hides none). Each worker process RUNS one fit at a
time (the rest wait `queued`) and admits at most 6, beyond that a 503 — with 4
workers, at most 4 concurrent fits, the bound the synchronous route had. The synchronous `/api/fit` stays
for scripts, tests and the Python twins. Plan:
`docs/superpowers/plans/2026-09-27-long-fits-start-poll.md`.

### Find Peaks does not read the clock (unit A1, 2026-09-29)

Find Peaks' answer must not depend on server load or on the optimiser's own
termination flags. No wall-clock budget anywhere in `autofit/engine.py`
(the 25 s per-candidate, 240 s sweep, proposal and screen budgets are gone —
on 1-GTA C1s Scan_6 MG2 won or lost on whether its fourth refit started
before 25 s): every candidate is screened, `SCREEN_TOP_K` are evaluated with
exactly `n_refits` refits, and work is bounded by counts and evaluation caps.
A fit's convergence is CERTIFIED (`_certify_minimum`): Trust-Region restarts
from the end point until one improves chi2 by less than Trust-Region's own
ftol (scipy's default, no new constant), at most `CERTIFY_MAX_RESTARTS` = 50
(measured: 2 for most fits, 21 at most on the committed C 1s set); out of
restarts = not converged. The old warm restart from a failed fit's exit point
is gone (it met MINPACK's xtol at the stall and reported success). Under
light and heavy load every structural field of the output is identical; the
numbers carry Trust-Region's arithmetic jitter (≤ 0.25 meV, ≤ 5e-4 relative
amplitude, the same idle-to-idle). Plan:
`docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md`.

### Timing claims are measured through the public URL

A request from a student reaches the server through Cloudflare, whose edge
ends a proxied request at ~100 s (HTTP 524; probes through
xps.fortierlab.org on 2026-09-26: 88 s passed, 125 s gave 524) — well short
of gunicorn's `--timeout 300`. "300 s covers it" was written for the DS+G
Run Fit in 2026-09-22 and was true on the i9 and false through the public
URL. A claim that a request fits inside a limit is measured through
xps.fortierlab.org, not on 127.0.0.1. (Owner, 2026-09-27;
`docs/findings/2026-09-26-public-request-ceiling.md`.)

---

## Lineshape Physics — Critical Rules

### DS (Doniach-Šunjić) Asymmetric Lineshape

The DS tail MUST always point toward **higher binding energy** (the left
side on a standard inverted BE axis). Asymmetric broadening in metals
arises from low-energy electron-hole pair excitations at the Fermi level,
which produce intensity only on the high-BE side of the core-level peak.

**Never invert the DS tail toward lower binding energy.**

Implementation convention: `dx = center − x`. The power-law term
extends the tail toward higher BE (`x > center` ⇒ `dx < 0`). The
optional exponential cutoff `gamma_asym` decays **only** on that
side — `Math.exp(gamma_asym * Math.min(dx, 0))` in the JS
`doniachSunjic`, equivalent to `exp(−gamma_asym · max(x − center, 0))`
in `fitting.py`'s `_doniach_sunjic`. When adding DS-derived shapes,
preserve this convention: the high-BE side is where `dx < 0` and where
the exponential envelope must decay.

### DS+G (formerly mislabeled "LA(α, β, m) [CasaXPS]")

The shape registered as `ds_g` in the backend (frontend enum `'DSG_LA'`,
dropdown text "DS+G") is a Doniach-Šunjić asymmetric core convolved with
a Gaussian. Despite its old label, this is NOT the CasaXPS LA
formulation. Frontend field names `laAlpha` / `laBeta` / `laM` are kept
for save-state compatibility:

| Parameter | Meaning |
|-----------|---------|
| α (`laAlpha`) | DS asymmetry index, dimensionless, 0 ≤ α < 0.5 |
| β (`laBeta`) | Lorentzian HALF-width (eV) of the DS core |
| m (`laM`) | Gaussian FWHM (eV) used in the convolution |

Tail points toward **higher** binding energy (DS physics: low-energy
electron-hole pair excitations on the high-BE side only).

Saved fits using the old `'LA'` shape value are auto-migrated on load to
`'DSG_LA'` — math is unchanged, only the label. Saved fits using the
short-lived `'DSG'` shape are auto-migrated to `'DS'` (the shape they
were actually being fit against, due to a pre-existing preview/backend
mismatch).

### LA(α, β, m) [CasaXPS] — true CasaXPS formulation

The shape registered as `la_casaxps` (frontend enum `'LACX'`, dropdown
"LA(α,β,m) [CasaXPS]") implements the genuine CasaXPS LA. Distinct field
names `caAlpha` / `caBeta` / `caM` so users do not confuse them with DS+G's
`laAlpha` / `laBeta` / `laM` (which have totally different units):

| Parameter | Meaning |
|-----------|---------|
| α (`caAlpha`) | High-BE-side exponent on the unit-amplitude Lorentzian; dimensionless, default 1.0, bounds 0.1–5.0 |
| β (`caBeta`) | Low-BE-side exponent; dimensionless, default 1.0, bounds 0.1–5.0 |
| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); continuous (the server fits it continuously so its derivative exists; the page draws the same continuous value since 2026-09-25 — it drew an integer kernel; the local engine HOLDS it exactly, since LA's curve jumps at m = 6k/7 and a smooth optimiser cannot fit it), default 50, bounds 0–499 |

α=β=1, m=0 reduces exactly to a pure Lorentzian. Increasing α
**suppresses** the high-BE tail; decreasing α extends it (BE-axis
convention; sign-flipped from CasaXPS's KE-axis description). m controls
Gaussian broadening; effective eV width ≈ (m/3) × dx where dx is the
data step size.

When implementing new LA-related lineshape parameters, **always** add
them to (use grep to find current line numbers — the file evolves):

- `defaultPeak` defaults block in `templates/index.html`
- `syncKeys` array
- `renderShapeControls` LACX param row
- `peakToBackendSpec` LACX branch
- `applyBackendResult` LACX backend-param mapping
- `runFit` JS LM free-params block + per-param clamps + linked-peak sync
- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`; DS+G's grid-aware twin is `dsgConvolved_array` — a convolved shape's scalar `evalPeak` branch ignores m and must have no caller, parity guard (C))
- `_migrateLineshapeAliases` if backwards-compat alias needed

### UCl4 U 4f Asymmetric Broadening

The asymmetric broadening in the UCl4 U 4f spectrum is due to **5f²
multiplet coupling**, not metallic screening. Do not attribute it to
Kondo screening or Doniach-Šunjić metallic behaviour. Use
multiplet-split component models, not a single DS peak.

When modeling U 4f, use `asym-GL` for the U 4f₇/₂ and 4f₅/₂ main lines,
with separate symmetric GL peaks for the multiplet satellites.

### Satellite Peaks

Satellite peaks (shake-up, shake-off, plasmon loss) use **symmetric**
lineshapes — Voigt or GL. Do not apply DS or LA lineshapes to satellites.

### Linked (Multiplet) Peaks

A linked peak derives its center, amplitude, and **all lineshape
parameters** from its parent. The sync block must cover every shape
parameter — failing to add a new param breaks spin-orbit constraints
during fitting. Search for the `syncKeys` array and the `applyParams`
closure in `runFit` when adding parameters; both need the new key.

| Parent param changes | Linked peak receives |
|----------------------|----------------------|
| `center` | `parent.center + linkOffset` |
| `amplitude` | `parent.amplitude × linkRatio` |
| `fwhm` / `shape` / `glMix` / `asymmetry` / `dsAlpha` / `dsGamma` | same value |
| `laAlpha` / `laBeta` / `laM` (DS+G params) | same value |
| `caAlpha` / `caBeta` / `caM` (CasaXPS LA params) | same value |

---

## Fitting Algorithm

### Backend (default)

`POST /api/fit` runs lmfit on the server. Selectable methods: `leastsq`
(Levenberg-Marquardt), `least_squares` (Trust-Region), `nelder`,
`differential_evolution`, `basinhopping`. The UI Method dropdown
defaults to **Trust-Region** (`least_squares`); the backend falls back
to **`leastsq`** when a request omits `fit_method`. The endpoint
returns the full result including refined params, σ bounds, χ²,
`bgIntensity`, `bgSubtracted`, and `fittedY`. Linked peaks are
constrained via lmfit parameter expressions.

`differential_evolution` samples from the parameter bounds and refuses an
open one, and the page sends `amplitude_min: 0` with no `amplitude_max`
(a free DS+G centre has no default window either), so until 2026-09-19
every ordinary request for that method returned HTTP 422. For THAT METHOD
ONLY, every candidate (the first search and each perturbed refit) is now
`_search_then_refine`: differential evolution inside a generated box
(`_finite_search_box`: open sides of freely varying parameters only —
amplitude ± max(10 × the largest |background-subtracted intensity|,
2 × |start|, 1), just the ceiling for the page, which sets the floor
itself; centre = the fitted energy range, always a real interval), then —
whenever a side was generated — an UNCONDITIONAL `least_squares`
refinement from that solution under the request's own open bounds. A box
can shape an answer that lies nowhere near its sides, so nothing is
inferred from nearness. A refinement that CONVERGED is the result — a
`least_squares` fit of the requested model under the requested bounds,
which is what the default method returns; its χ² is deliberately not
compared with the boxed search's (a descent cannot end materially above
its start, but it ends a hair above an exact start sitting on a requested
bound, and every tolerance tried for that comparison produced reachable
false failures and no reachable protection — Codex rounds 5–8). If the
refinement did not converge or raised, the search result
stays marked unverified, never displaces a verified candidate in the
perturb loop, and, if it is what `run_fit` returns, is `success: false`
naming the generated limits.
Because differential evolution ignores the start and can "converge" with
a needle-narrow component outside the fitted range, each candidate also
competes with a `least_squares` fit from its own start under the request's
bounds (`_global_or_local_candidate`: verified beats unverified, then the
lower χ² wins), so this method never returns worse than the default method
would from the same start.
Generated sides are never echoed back as `min`/`max` (the page saves
returned bounds and warns within 1 % of them). A returned DE result
therefore normally carries `least_squares` uncertainties and message.
Every other method's parameters are unchanged; `/api/analyze` reaches the
same code through `options.fit_method`. Measured on committed targets with
the page's `n_perturb: 3`: 2–75 s per fit (6–7-component C 1s models
exhaust DE's evaluation budget in every search and are rescued by the
refinement). It is not a gold standard: on one 3-component B 1s target it
returned χ²ᵣ 1.92 where Trust-Region found 1.81.

`basinhopping` follows THE SAME PATTERN since unit F2 (2026-09-26; owner
decision; plan `docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md`):
`_basinhopping_candidate` — the search, then an unconditional
`least_squares` refinement from its point under the request's bounds (the
refinement's convergence is the verdict, no χ² comparison), then a
competition with a `least_squares` fit from the same start (verified beats
unverified, then the lower χ²), for the main fit, every perturbed restart and
the required refit. Until then basinhopping always reported `success: true`
(lmfit sets it before minimising and never reads scipy's result), and
scipy's own flag is no verdict either: it marked 23 of 24 sampled committed
targets failed (BFGS "precision loss") at points equal to Trust-Region's
minimum (median relative χ²ᵣ difference 1e-9). An unverifiable search is
`success: false`. Basinhopping runs NO perturbed restarts (a global search:
with the page's `n_perturb` 3 they took 14 of 16 multi-component targets past
the 300 s server timeout, median 386 s, for χ²ᵣ identical to 1e-8; without
them median 96 s, max 256 s). NOTE: the public URL's ceiling is lower —
Cloudflare returns 524 between 88 s and 125 s — so the largest basinhopping
models still fail there
(`docs/findings/2026-09-26-public-request-ceiling.md`, not yet addressed).

**Determinacy (unit F2).** `run_fit` refuses a model with at least as many
free parameters as data points (`ValueError`, HTTP 400, "not determined by
these data: N free parameters for M data points"), and so does the local
engine: lmfit divides by max(1, nfree) and the F tests clamp dof to 1, so such
a model read as a near-perfect, fully supported fit (6 points, 2 GL
components: χ²ᵣ 2.8e-6, both "supported"). A count, not a threshold; one
degree of freedom is fitted as before.

**Reproducibility (2026-09-21).** Every random draw in `run_fit` — the
`n_perturb` restarts (the page sends 3; ±15 % on every varying parameter)
and the populations of `differential_evolution` and `basinhopping`, which
lmfit otherwise takes from numpy's GLOBAL generator — comes from one seed
that is a pure function of THE NUMBERS THE OPTIMISER IS HANDED
(`_request_seed`: SHA-256 of the energies, counts and the COMPUTED
background curve as little-endian float64, plus the canonical JSON of each
component's lineshape, each lmfit parameter's effective role — a
constrained one is its expression, a fixed one its value, a free one its
value and bounds — the method, solver options and `n_perturb`; tag
`xps-fit-seed-v1`). Settings are hashed by their EFFECT, never as sent, so
nothing the fit ignores can change the draws: a peak's name or colour, the
`fix_gl_ratio` the page still sends for a Gaussian, stale shape parameters
kept after a shape switch, the `endpoint_avg` a linear background does not
use, bounds of a fixed parameter, start values a link overrides, anchor
order, and the peaks' internal ids (parameter names and constraint
references are hashed by component POSITION: the page never reuses an id,
so a model rebuilt after deleting a peak would otherwise fit differently)
(in review each such no-op edit moved an area fraction by 15–45 pp
while the request was hashed as sent). It is a seed,
not an identity (32 bits collide; never a cache key). The response reports
it as `random_seed`; a caller's `fit_kws.fit_kws.seed` (integer in
[0, 2³²)) replaces it and is consumed, never forwarded to a solver.
`run_fit` itself accepts only the five supported methods, case-folded
(`_FIT_METHODS`): `/api/analyze` forwards `options.fit_method` without the
route's allowlist, and lmfit's `ampgo`, `dual_annealing`, … would draw
from the global generator. The seed value and the draws `run_fit` actually
makes (observed through Levenberg-Marquardt) are pinned by tests; numpy does not promise the same `default_rng` stream across
versions, so a failing pin after an upgrade is a release note ("saved
projects regenerate differently"), not something to re-pin silently.

What seeding buys and what it does not. "Identical request" means the same
data, model START values and settings — after a fit the page holds the
fitted values, so a second press is a different request; re-loading a
saved project and pressing Run Fit is the repeatable case. Measured on the
202 committed targets × 5 presses of the identical request, before → after:
Levenberg-Marquardt byte-identical on 145 → 202 targets;
Trust-Region on 51 → 145, area fractions moving by more than 1 pp between
presses on 8 → 0 targets, by more than 0.01 pp on 14 → 2 (worst 0.30 pp,
one U 4f scan where two presses in five land in a neighbouring minimum). Levenberg-Marquardt (MINPACK) and Nelder-Mead are
byte-identical. Trust-Region, the default, is NOT and cannot be made so by
seeding: the BLAS dot product (Apple Accelerate on the i9) rounds one unit
in the last place differently depending on where its argument sits in
memory (`w.dot(w)` gives two values over 16 alignments, `np.sum(w*w)`
one), `norm` inside scipy's `_lsq/trf.py` is the first call to return
different output for identical input, and the iteration amplifies that to
~1e-4 relative in an area at its stopping tolerance of 1e-8. Worse, the
perturbed restarts start from that jittering solution, and near a basin
boundary 1e-5 in a start is enough to send a restart into another minimum:
on the lab's targets that happened once (0.30 pp), but on a synthetic
five-component model two presses of the seeded request differed by 29 pp
(`tests/test_fit_reproducibility.py` docstring). Do not patch scipy
internals for this, and do not tighten the tolerance: ftol = xtol = gtol =
1e-12 on the same 202 × 5 gave FEWER byte-identical targets (123 vs 146)
and made two targets that converge today abort on the evaluation budget.
OWNER DECISION 2026-09-21: ACCEPT AND DISCLOSE; no unit for bit-identity.
Byte-identity is a software property, not a scientific one. The scientific
requirement — reloading a saved project and pressing Run Fit regenerates
the figure within meaningful precision — is met (2 of 202 targets move
more than 0.01 pp, worst 0.30 pp). The 29 pp synthetic case is the SAME
phenomenon as the local-minimum problem (near a basin boundary 1e-4 of
jitter flips the answer), so the scattered-starts cross-check unit is
already the mitigation: it exposes exactly those fits. Do not build a
second thing (a reviewer tried a deterministic perturbation base: identical
starts, results still differed; a reproducible-arithmetic BLAS is a large
project with uncertain payoff). Disclosure wording, for docs and the
student note: identical requests now give identical results on real data
in practice; the underlying arithmetic is not bit-reproducible, so a fit
sitting near a boundary between two solutions can still resolve
differently, and that is precisely the situation the multiple-starts check
is designed to surface.

**Scattered-starts check (step (a) of the 2026-09-21 unit; plan in
`docs/superpowers/plans/2026-09-21-scattered-starts-and-unsupported-components.md`).**
Every Run Fit with ≥ 2 unlinked components sends `n_starts: 3`; after the
normal fit (unchanged: THE FIT is what the student's method returned,
byte-identical with and without the check, and `n_starts` is not part of
the seed) `run_fit` runs three more fits of the SAME method from scattered
starts — drawn from a third stream of the request seed, anchored to the
REQUEST's start (amplitude ×/÷ 3, width ×/÷ 1.5, free centres ± 0.5 eV,
other bounded parameters redrawn inside the middle 90 % of their range),
clamped into the request's bounds (amplitude sign kept). "Same solution" =
every area fraction within 1 pp and every centre within 0.1 eV, COMPONENT
BY COMPONENT by id — no permutations: "C-O" and "C=O" trading places is a
different chemical reading even when both are GL lines. The response's
`starts` reports how many reached
the fit, how many ended in a solution that is NOT better (counted, never
listed — ~25 % of fits have one and listing them would train people to
ignore the panel), and `alternatives`: solutions whose χ²ᵣ is lower by more
than 0.1 %, each with its own areas and every component's centre shift
from the STUDENT'S START. Not run for `differential_evolution` /
`basinhopping`, single-component models, a fit that did not converge,
Batch Fit or the local fallback; a failure inside the check never fails
the fit. Page: one line under the Results table ("2 of 3 scattered starts
reached this solution; …" — counts, never certification language) and,
when alternatives exist, an "Other solutions found" table (your fit first;
the largest move named, amber > 0.5 eV, red > 1 eV) with Preview (the
history-preview overlay, on a copy) and "Use this solution": explicit, one
undo entry, recorded as `fitResult.chosenAlternative`, and ATOMIC by
construction — the alternative is only the START of an ordinary server fit
(`runFit({startPeaks})`); the live model is written by that fit's success
path and by nothing else, so a fit that fails, does not converge, is
discarded on a tab switch or cannot reach the server (no local fallback
here) leaves peaks and result exactly as they were, and σ, exports and
saves come through the one existing path. Every row shows EACH component's
own area % and its own move from the student's start. The evidence is
BOUND TO THE FIT THAT PRODUCED IT by COMPARISON, never by hand
invalidation (so no edit path can be forgotten): `fitResult.startsModelKey`
covers every peak field the request reads (incl. the auto-fit asymmetry
bounds) AND the fit context — background type and window, endpoint
averaging, Shirley iterations, ROI, manual anchors, charge shift — taken
after the result is applied and persisted with the counts.
`_startsIfCurrent(fr, key)` is the single accessor (`_startsLiveKey()` for
the active tab, `_startsRecordKey(t)` for a record): after any such change,
an undo or a history restore that brings back other values, the panel says
the comparison no longer applies, nothing can be previewed or applied, an
open alternative preview is dropped (`_dropStaleAltPreview`), and
saves/exports carry neither counts nor the recorded choice. A name, colour
or visibility is not part of a fit and does not invalidate it. `runFit`
captures the same key before its first await and DISCARDS a result whose
model or context was edited while it ran (the peak controls stay editable
during a fit; a newly locked centre would otherwise keep its edited value
under the server's statistics). The trigger (`n_starts`) is decided with
the other request inputs before the first await. In the RED band — and only there — it first asks,
naming the component and the distance ("This solution moves C-O by
−1.47 eV from where you placed it. Apply?"): a lower χ²ᵣ bought by
relocating a component is the measured trap (8-JT C1s Scan_1/5/6/7), and
the app must never substitute a chemical interpretation because it scored
better. Saves persist the counts (`_startsForSave`), not the alternatives'
parameter sets (regenerable from the seeded request). Measured with the
shipped code on the 202 committed targets: an alternative is shown on 0 of
94 re-fits of a saved solution and 6 of 84 not-yet-fitted starts (7.1 %;
three of them in the red band), median +0.54 s per Run Fit (90th
percentile +1.8 s). It shows that a decomposition is not unique; it cannot
say which one is correct, and four known targets defeat even ten starts.

### Client-side fallback

`runFitLocal` in `templates/index.html` is a JS Levenberg-Marquardt
implementation used as a fallback when the backend is unreachable, and
the ONLY engine Batch Fit uses. Central-difference Jacobian (centre
step scaled by the peak width), active-set step (parameters pushed into a
box wall are held fixed), max 3000 iterations. Terminates on a gradient
cosine < 1e-6, on actual and predicted relative χ² reductions both < 1e-6
in agreement, or on a relative step < 1e-8, and only after a
feasible-descent CERTIFICATE passes: no single free parameter moved by
1e-3 (scaled, inside its box) reduces the residual by more than 1e-6 of
its value, otherwise that point is taken and iteration continues. The
certificate is a coordinate (single-parameter) check, not a proof of a
local minimum along coupled directions; no exit is exempt from it.
Damping exhaustion is a FAILURE. Poisson-weighted since unit W1
(2026-09-18): it minimises Σ(w·r)² with w = 1/√max(raw counts, 1), the
server's weighting, so its statistic is a real χ²ᵣ (objective
`poisson_weighted_chi_square`); results saved by unit A0 were unweighted
and stay labelled "Residual variance". It produces no uncertainties, and it
HOLDS LA's `caM` at its exact value (it used to round it in its clamp; a
free m was tried in the `caM` unit and withdrawn: LA's curve is
discontinuous in m, `docs/superpowers/plans/2026-09-25-cam-continuous.md`).

**A local result is a STARTING POINT, not a reportable result** (keyed on
`engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
`_localFitCaveat`). Measured in unit W1 and RE-MEASURED after A03
(2026-09-22, `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`,
generator `scripts/local_server_gap.js`): weighted, it matches the server on
GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
U 4f targets where both engines reach the same minimum every component
agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
to 20.8 % area on the Voigt satellites); it still differs on the other U 4f
targets for two reasons, separated by a control arm (the server with LA's
m held at the same value): the `caM` hold (the server fits m, the local
engine holds it — on Scan_6 the whole gap), and the local descent stopping
in a worse minimum (5–13 % χ²ᵣ above the held-m server on Scan_4/5/8) —
the "several minima" case (`docs/findings/cam/local_server_gap_after_cam.json`;
both engines' amplitude floor is 0 since unit step (b)). Both engines weight by
√intensity whether the data are counts or CPS (a convention, not a
calibrated uncertainty for rates); the formula is the same but the inputs
are not bit-identical, because `uploadToBackend` rounds intensities to
2 dp before the server weights them. A03 and the `caM` unit are done and
the designation STAYS on both grounds: fitting m locally needs a
derivative-free search (its own unit), and the worse-minimum outcome
(three of nine U 4f targets) remains; the label is reconsidered only on a
re-measurement after that work. (The amplitude-bound change
DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
implemented: unit step (b), 2026-09-22, below.) The same file records that a
converged server fit is not ground truth: on a committed C 1s scan the
server's default method stopped in a local minimum the local engine
avoided.
See `docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md`.

**"Not supported by the data" (unit step (b), 2026-09-22; owner decision
2026-09-18).** A component whose amplitude the fit drove to its floor,
pinned on a bound or fitted to numerical residue is an explicit OUTCOME —
the fit did not determine it — and its centre, width and σ are not reported
as if they were. The statement needs no intensity floor (six were tried for
the Auto-Fit anchor and each rejected real components or accepted residue):
with the other components held at their fitted values, removing this one
must make the fit significantly worse — `fitting._component_support`, the
Auto-Fit anchor's F statistic (F ≥ 10; `SUPPORT_MIN_F`). The SERVER computes
it once per component (`individual_peaks[].support = {f, delta_chi2,
supported}`; a linked component `follows` its parent); the page's twin
`_componentSupportFromResponse` recomputes it from any response carrying
`counts`, `fitted_y` and the component's curve; the LOCAL engine computes
the same statistic from its own residuals and weights
(`_componentSupportCore`), so a component driven to the zero floor by Batch
Fit is an outcome there too. Linked components follow their ROOT ancestor
whatever the request order. The verdict is a property of the fit that
produced it, CONDITIONAL on the other components as fitted, so it is bound
to that fit: `p.support.fitKey` is the model-plus-context key
(`_startsLiveKey()`) taken after the values are applied, and
`_isUnsupported(p)` compares it with the live key at every read — after
the student edits any peak, lock, link, the background, ROI, anchors or
charge correction, or an undo brings back other values, nothing is
suppressed or excluded until a new fit writes a new verdict (a verdict
without a key, from an older save, is never applied; exports write a
Status only from a CURRENT verdict — stale means "not established", never
"supported"). When the key changes, `_refreshStartsEvidence` compares the
set of flagged components with what EACH consumer has rendered — sidebar
badges, Results rows and chart datasets carry the peak id / flag — and
re-renders the ones that differ — the sidebar is PATCHED IN PLACE (header, summary values, area % over the currently supported components, badge), never re-rendered, because the student may be typing in a card (a caller that already redrew the sidebar,
such as Lock All or Add Peak, therefore still gets Results, Quantify and the
chart refreshed); it runs from the lock toggles, Lock All and every
`updatePlot` (which passes `fromPlot` so the chart is not rebuilt from
inside its own rebuild). Auto-Fit locks
every centre and refines the charge shift AFTER the result is applied, so
it re-stamps its verdicts (`_restampSupport`) — those changes are part of
its result. `p.support` is persisted with the peak (saves spread the peak
whole); Batch Fit's copy and a `.fit.json` import set it to `null`
(parameters on other data: nothing established); stack tabs judge a source
component against the SOURCE record's key. Sites
(`_isUnsupported`): sidebar card (badge; centre/width "—"; excluded from the
area total), Results table (greyed row, no centre/width/σ, area kept,
percentage "—", note beneath; percentages over supported components),
uncertainty panel (one rule-0 warning, before the per-parameter alarms and
instead of the neutral "locked" note Auto-Fit's centre lock would produce),
Quantify (no row; listed beneath: "an atomic percentage of 0.0 % would be a
measurement claim"), chart / stack / figure legend labels, no figure label at
the component's (zero) maximum, CSV/XLSX (Status column, empty cells, no
At%, WARNING line — and no width of any kind: DS+G β / m and LA m are widths
too), TSV (column kept, header says so), the scattered-starts table ("Your
fit" row shows neither area % nor a move for it, and it is never the
largest move; an alternative's components are unjudged and shown as they
are). Both engines' amplitude
floor is 0 (`runFitLocal`'s clamp was 1). Measured on the 202 committed
targets: 3 of 752 components (three C 1s re-fits, F 0.95–3.9), 0 of 95 fresh
starts — but committed projects are survivorship-biased (a collapsed
component may have been deleted before saving), so the working-fit rate is
plausibly higher. Known limits, the anchor check's: a gross single-channel
artefact can mark a real component unsupported; REDUNDANCY UNDER OVERLAP is
not detected (a refit without the component is the test; step (c) does it
for the Auto-Fit anchor).

**Acceptance rule for fit outcomes (unit A0, 2026-09-15):** a fit OUTCOME
from Run Fit, Batch Fit or the local engine is shown, stored or exported
only if it converged. `runFitLocal` works on a copy and commits only on
success, returning `{success, iterations, chiReduced}`; `runFit`
treats `success !== true` from `/api/fit` as a failed fit and falls back to
the local engine only on a transport failure, never on a server-side
error. A 2xx body that was READ but is not JSON is the server's reply, not a
transport failure (unit F2): `_readFitReply` reads the text (a failure there
is transport) and parses it; a NaN / Infinity token (Flask serialises a σ it
could not compute that way) or any unparseable body is a failed fit with its
message, for Run Fit and Auto-Fit alike — until F2 it sent Run Fit to the
local engine, replacing the server's converged result, verdicts and starts
evidence with a starting point. A RESULT IS DISCARDED IF THE MODEL WAS EDITED WHILE THE FIT WAS RUNNING
(2026-09-22; a correctness fix for EVERY Run Fit, shipped with the
scattered-starts check but independent of it). The peak controls stay
editable during a fit. `runFit` captures the model-plus-context key
(`_startsLiveKey()`: every peak field the request reads, background type and
window, endpoint averaging, ROI, anchors, charge shift) beside `peakSpecs`,
before its first await, and after the tab-owner check refuses to apply a
result if that key changed: amber notice, "Fit discarded (model edited)",
previous peaks and result kept. Before this, a centre changed and locked
mid-fit kept its edited value (`applyBackendResult` honours locks) under the
server's χ², σ and fitted curve for a different model.
STATISTICS AFTER AN EDIT (unit F1, 2026-09-25; plan
`docs/superpowers/plans/2026-09-25-f1-stale-statistics.md`): χ², σ, RMSE,
the R-factor and the stored fitted curve are bound to their fit by the SAME
key (`fitResult.startsModelKey`, now stamped by every creator — `runFit`,
`runFitLocal`, `applyAutoFitResult`, re-stamped by `_restampSupport`); no
second mechanism. One accessor, `_statsState(fr, key)` (`_statsLiveState()`,
`_statsRecordState(t)`): `current` / `stale` (the model or its context
changed since — an edit, a Find Peaks apply in the default window, an undo
or history restore to other values) / `unverified` (no key: saved before
this unit — values shown with a note to re-run). Stale: Results banner
("belong to the previous model"), statistic / RMSE "—", no R panel, no σ;
header "χ²ᵣ — (model changed)", status "—", "R: —"; no per-parameter
uncertainty rule; CSV/XLSX a WARNING instead of the statistic, σ cells
empty; TSV a NOTE (its columns are the current, unfitted model); figure no
χ² and no stored "Fit" curve; chart and stack envelopes composed from the
current peaks; saves keep the key (a reload judges again) and add
`statisticsState` / `statisticsNote`. Refreshed from `updatePlot`
via `_refreshStartsEvidence` (`_refreshStatsState`, Results carries
`data-stats-state`; lock toggles and Lock All reach it too). Keys are
compared by `_sameFitKey` (each form field canonicalised through its
readers' parser: energies parseFloat, "280" = "280.0"; counts parseInt,
"3e1" ≠ "30").
Auto-Fit now discards a response whose model or context was edited while
it ran, and a transport failure after such an edit runs no local fit. A
stale save's curve and R are never re-installed on load. The model
replacement that keeps an older result is thereby covered for the
statistics. Not covered (separate units): loaded files without convergence
provenance; `p._backendParams` still rides in a stale save (not displayed;
the sealed fit record owns it). From the initial commit
until this unit the local LM step had the wrong sign and returned the
starting model as "Fit complete"; see
`docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md` and
`scripts/scan_batch_fit_signature.py`, which lists suspected saved files.

## Background Methods

| Backend id | Notes |
|---|---|
| `shirley` | Iterative Shirley (Proctor & Sherwood, *Anal. Chem.* **1982**, 54, 13, 2438–2439). Default. |
| `smart` | Shirley variant with smarter endpoint handling. |
| `smart_exp` | Experimental Shirley variant. |
| `shirley_linear` | Shirley with a linear-fallback bridge. |
| `linear` | Straight line between ROI endpoints. |
| `tougaard` | Single-pass universal cross-section K(T) = B·T/(C+T²)², B = 2866 eV², C = 1643 eV² (Tougaard, *Surf. Interface Anal.* **1988**, 11, 453; kernel max at √(C/3) ≈ 23.4 eV). Order-robust (either BE direction); amplitude anchored to the data at the high-BE edge. JS twin `tougaardBackground` must stay in numerical agreement (pinned by `tests/js/tougaard_twin.test.js`). |
| `manual` (frontend only) | User-placed anchor points; `manualAnchorBackground` in JS. |

The page's background twins (`computeBackgroundCore`: what it draws, freezes
into `fitResult.bgIntensity` at fit time, saves, and what the local engine
fits against) equal fitting.py's on the tested cases — shirley, smart and
smart_exp EXACTLY (0 difference, at equal iteration caps), tougaard to
rounding, linear on uniform grids — within the test's 1e-6 of the intensity
span, on uniform and non-uniform grids, both directions, endpoint averaging
1, 3 and 10, repeated energies and data that dip below the baseline
(`tests/js/background_parity.test.js`, unit 4 2026-09-27). The Shirley and
smart_exp twins run fitting.py's iteration operation for operation on an
ascending copy — numpy's linspace start with the endpoint pinned exactly, the
net signal clamped at zero, the background kept when no net signal is left,
the 1e-6 stop; smart clamps against the raw data; every endpoint mean is
numpy's (`_npMean`, numpy's pairwise summation: a sequential sum one rounding
step off became a different fixed point, 62.7 % of the span, Codex round 3);
finite inputs. Before the unit: Task 4's S4 / S5 (smart at averaging 10 was
1.2 % of the span away) and smart_exp 1.4 % (a 1e-4 stop, a descending grid
integrated from the other end). An iterative background is fragile: rounding
differences of one unit in the last place select different fixed points, so a
twin must match its arithmetic, not only its formula. Known gaps, pinned:
`shirley_linear` (de-listed) diverges on descending grids; linear
interpolates by index on the page and by energy on the server, equal only on
uniform grids (Task 4 cause 4); the UI's Shirley iteration count (default 5)
stops before fitting.py's convergence (Part 5 of the sealed-fit-record memo).

Use Shirley for standard core-level regions. Linear only when the
spectral window is very narrow and featureless.

## Quantification

Peak areas are integrated numerically (trapezoidal over BE grid). RSF
(relative sensitivity factor) corrections are applied in the Quantify
tab. Atomic percent = (area/RSF) / Σ(area/RSF) × 100.

---

## Charge Correction

Reference: **C 1s adventitious carbon at 284.8 eV** is the default. The
UI dropdown also offers **C 1s graphitic carbon (sp²) at 284.5 eV** as
an alternative; the Auto-Fit C1s Graphite feature uses 284.5 eV as the
fixed reference for the graphitic component it identifies.

A rigid shift (`state.ccShift`) is applied to all binding energies
before fitting. The corrected axis is produced by `getCorrectedBE()`.

Auto-Fit C1s Graphite derives that shift from the FITTED centre of its
"Graphite" component, so the data must SUPPORT that component
(`_autoFitGraphiteIsSupported`), in the one sense that needs no intensity
threshold: removing it from the fitted model must make the fit to the
server's own data significantly worse. From the `/api/fit` response alone —
`counts`, `fitted_y`, the component's curve `individual_peaks[].y`, the
server's weights 1/max(counts, 1) — F = ((χ²_without − χ²_with)/p) /
(χ²_with/dof), p = the component's free parameters; supported means
χ²_without > χ²_with and F ≥ 10 (or χ²_with = 0). A component driven to
zero, pinned on its bound or fitted to numerical residue has
χ²_without ≤ χ²_with — removing it costs nothing (true of every such
reproduction in `docs/autofit/codex/autofit_zero_graphite_*`); resolved
anchors measured F from 1.7e2 (behind a 300 000-count one-channel spike) to
1e9, and the 70 committed Graphite models F ≥ 1.1e3. Otherwise the auto-fit
is rejected and rolled back with a red notice before any charge-correction
input is touched. Until 2026-09-21 only the centre was checked (±0.3 eV of
284.50), which a zero-amplitude component always satisfies because its
centre is bounded to that window. Do NOT replace this with an intensity
floor: five were tried (relative to the strongest component, the raw span,
the background-subtracted maximum, the raw magnitude, the upload's 0.01
resolution) and each rejected real anchors or accepted residue. The same
statistic is the natural definition for the planned "component not
supported by the data" outcome. Fixtures are real `run_fit` responses:
`scripts/gen_autofit_anchor_fixtures.py` →
`tests/js/fixtures/autofit_anchor.json`. SCOPE: it answers "do the data
support this component?", not "is it graphite?".

KNOWN LIMITS of that check (owner decision 2026-09-21: shipped with them
after six Codex rounds, all NO-GO; do NOT write a seventh rule — six
intensity floors failing is the data saying no threshold on intensity can
mean "zero" independently of the data):
- It REJECTS A REAL ANCHOR when the fitted region carries a gross
  single-channel artefact (a spike of millions of counts, or a dead
  zero-count channel): that channel dominates χ²_with and drags F under 10.
  The user gets a red notice and a rolled-back model; removing the artefact
  or narrowing the ROI recovers. A recoverable refusal beats main's old
  failure mode — a non-existent component silently setting the energy
  reference for a whole spectrum.
- REDUNDANCY UNDER OVERLAP was out of scope for the support check
  (χ²_without holds the other components fixed) and is CLOSED by step (c),
  2026-09-22: Auto-Fit's request carries `require_component: <Graphite id>`
  and the server refits the model WITHOUT that component from the others'
  fitted values under the request's bounds (`fitting._component_required`,
  through the run's own fitter `fit_model` — so differential evolution's
  box/refinement machinery and the request seed apply to the refit too;
  everything linked to the removed component goes with it, transitively;
  every retained parameter is created before any expression is assigned,
  so a chain of links in any request order resolves; NO tolerance of any
  kind on the comparison — a delta floor relative to the data's power and
  then an "exactness" cutoff on the reduced fit each masked a resolved
  anchor at high dynamic range, Codex rounds 2–3, the DE unit's lesson
  again. Known limit, accepted: on NOISE-FREE data whose full fit is exact
  to machine precision F is meaningless and a truly redundant component can
  read "required"; real data never fit to machine precision) and returns
  `required: {required, f, chi2_with, chi2_without_refit, refit_converged}`
  with the same F ≥ 10 rule (a refit that did not converge gives NO verdict
  since unit F2 — `required: null, refit_converged: false` — and Auto-Fit
  refuses that anchor too: a refit stopped early had read "required", F 992,
  for a redundant anchor). `applyAutoFitResult` refuses a supported-but-
  not-required anchor exactly like an unsupported one, before any
  charge-correction input is touched ("refitting the other components
  without it fits the data as well"); the anchor id is captured with the
  other request inputs before the first await. One extra fit, Auto-Fit only; the fit
  itself is unchanged by the check, and a check that did not run never
  blocks. On the 70 committed Graphite models the anchor is required on
  all 70 (F ≥ 54, median 6.1e3 — a measurement with `require_component` over
  the un-committed target file, not a test); the round-6 reproduction (two symmetric GL
  lines, no graphite: support F ~ 1e6 with the others held, refit without it
  equal to rounding) is now refused.
- One rounding-residue construction still passes (unrounded manual
  background a rounding step under data the upload flattened; F ≈ 280).

LOGGED FOR ONE LATER UNIT (untouched): Auto-Fit anchors on a one-channel
spike, and on a featureless plateau under background None, and still
derives a charge correction from it; a rejected Auto-Fit (any reason)
leaves its `pushUndo()` entry and a cleared redo stack behind. The spike
case shares a root with the false rejection above — gross single-channel
artefacts are unhandled generally — so if this becomes a despike /
outlier-flag unit, those three are one piece of work.

Adventitious carbon referencing (284.8 eV) is the default for
convenience but has known criticisms in the XPS literature — the C 1s
position of adventitious carbon depends on surface chemistry and is not
a true universal standard. Graphitic carbon (284.5 eV) or a known
internal reference is preferable when available.

Additional fixed references in the dropdown: Au 4f₇/₂ (83.98 eV), B 1s
for B₂O₃ (192.99 eV), N 1s for BN (398.31 eV), B 1s for BN (190.74 eV),
plus a free-entry "Custom reference" option.

## File Formats Supported

| Extension | Notes |
|-----------|-------|
| `.csv`, `.tsv`, `.txt`, `.xy` | Whitespace/comma/tab/semicolon delimited. Backend `parseCSV` + frontend equivalent. |
| `.xlsx`, `.xls` | Backend `parseXLSX` (openpyxl); frontend XLSX.js for client-side parse. |
| `.vgd` | Thermo Avantage binary. Backend uses `vgd_parser.py` (olefile); frontend `parseVGD` does a heuristic Float32 extraction. |

Spectrum columns: first = BE (eV), second = intensity (counts/s). Rows
with non-numeric or missing values are skipped.

---

## Multi-Tab + Project Save/Load

The app supports multiple spectrum tabs simultaneously. Project state
saves to `.proj.json` (< 5 tabs) or `.proj.zip` (≥ 5 tabs; manifest +
per-spectrum JSON inside the archive). Schema version 3.

- **Tab IDs** are preserved across save/load. Field is top-level
  `data.activeId`; the saved active tab is re-activated on load.
- **Stack tabs persist.** Saved with `isStack: true` + their entries
  + line-width + offset; spectrum tab data lives elsewhere and is
  reached by `entry.sourceTabId` at render time.
- **Stale stack entry pruning:** if a saved stack references a source
  tab that didn't load, the entry is dropped and an amber toast tells
  the user.

## Spectrum Stacking

A stack tab visualizes multiple spectra on shared axes with per-entry
fit visualization (envelope + shaded peak components, raw-level).
The whole stack chart's behavior is governed by a small set of
invariants worth knowing before touching the code:

- **Dataset keying.** Each entry contributes 2 + 2×N_peaks datasets to
  the chart, each tagged with a stable `_stackKey` of the form
  `<entryId>:raw`, `<entryId>:env`, `<entryId>:peak:<peakId>`,
  `<entryId>:pbg:<peakId>` (the `:pbg` is a transparent fill anchor for
  the matching peak's shaded fill — Chart.js requires a real dataset
  for fill targets). Keys let in-place updates target specific datasets
  without relying on array indices, which shift when datasets reorder.

- **In-place updates preserve zoom.** `_updateStackChart` mutates
  `data` / `hidden` / `borderWidth` / `fill` on existing datasets and
  calls `chart.update('none')`. `_renderStackChart` is the destroy +
  rebuild path, used only on entry add/remove or when the active chart
  is the wrong chart (see next bullet).

- **Chart-type discriminator.** `state.chart._xpsStackTabId` is set on
  every stack chart at creation. `_updateStackChart` rebuilds whenever
  the active chart isn't tagged for the current stack tab — guards
  against in-place updates running against a stale spectrum chart or
  a different stack's chart.

- **3 render-data paths** in `_buildEntryRenderData` cover fresh
  backend fits (Path A: use fitResult.fittedY directly), fresh local-LM
  fits (Path A2: compose envelope from peaks + bgIntensity), and
  post-load reconstruction (Path B: recompute bg from raw via the
  source tab's persisted bg settings using `_computeBackgroundForSource`).
  Render data is cached on the entry as `_renderDataCache` and
  invalidated only at `_renderStackChart` rebuild.

- **Layered visibility model.** Per-entry `entry.showFit` gates whether
  the entry participates in fit visualization at all; the toolbar pills
  (Envelope, Individual Peaks, Fill, Bkgrd Sub) act as global layer
  switches on top. The `peak-fit-control` CSS class hides peak/fit
  toolbar items entirely on stack tabs (Run Fit, Batch Fit, etc.).

## Toolbar Highlights (frontend)

- **Line Width slider** (right panel, always visible): per-tab,
  persisted. Drives raw + per-peak `borderWidth`; envelope uses
  `min(width + 1, 6)` so it stays visually distinct.
- **Vertical Offset slider** (right panel, stack tabs only): vertical
  separation between visible entries.
- **`⇅ Organize Tabs`** (chart toolbar): sorts spectrum tabs as
  Survey → element-alphabetical → Other; stack tabs cluster at the
  end as a block, preserving their relative order.
- **`+ Stack` / `+ Add Spectrum ▾`** (chart toolbar): create a new
  empty stack and add open spectrum tabs to the active stack.
- **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
  + charge correction. Enabled only when the midpoint of the DATA the fit
  would use is in 270–315 eV — for the active tab the live selection
  `getROIData()` returns, never the tab record's stale window or a typed
  window reaching past the data (`isC1sTab`, unit F3 2026-09-27, sweep M5).
- **ROI past the data / centre outside the data** (2026-09-25, warn only):
  `getROIData()` has always clamped an ROI to the data it selects; the page
  now SAYS so under the ROI fields ("ROI extends past your data — clipped
  to X–Y eV" when a field reaches more than one sampling step past the
  data; amber when min > max or the window misses the data) and badges a
  peak card whose centre lies outside the selected data ("outside data").
  Neither the fields nor the peaks are ever moved; the fit, Find Peaks
  (same inclusive mask on the same corrected energies) and saves read the
  ROI exactly as before. `_roiWindowStatus` / `_refreshRoiAndCentreWarnings`,
  refreshed in place from `updatePlot`; plan
  `docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md`.
- **Manual anchor background**: place anchors on the chart for
  per-spectrum hand-tuned background curves; persisted as
  `tab.manualAnchors`.

## Tests

```
tests/test_la_continuous_m.py   # LA(α,β,m) continuity across integer-m kernel widths
tests/test_la_short_input.py    # LA edge cases on very-short input arrays
tests/test_mixed_ds_lacx_e2e.py # End-to-end: a fit with both DS+G and CasaXPS LA peaks
```

Run via `pytest tests/`.

## Reference Energies for Common Regions

There is **no demo-spectrum loader** in the app (a `loadDemo(...)`
function does not exist — earlier versions of this file were stale).
Typical regions for hand-testing:

| Region | Window | Notes |
|--------|--------|-------|
| Fe 2p | 700–740 eV | Fe(0) at 706.6, Fe(III) at 710.5, satellite at 713.5 |
| U 4f | 370–415 eV | UCl4-like U(IV); 4f₇/₂ at 380.9, 4f₅/₂ at 391.8 (offset 10.9 eV) |
| C 1s | 280–295 eV | sp², sp³, C-O, C=O, COOH components; charge ref at 284.8 eV |

## Known Issues

- Legacy document-level tooltip handlers call `e.target.closest(...)`
  without checking that the event target is an Element
  (`templates/index.html` around the `data-xps-tip` listeners); events
  targeting non-Elements throw `e.target.closest is not a function`.
  Needs an `instanceof Element` guard in a future pass.
- Gunicorn `--reload` watches Python files only — **edits to
  `templates/index.html` are NOT picked up** outside Flask debug mode
  because Jinja caches compiled templates per worker. Restart the dev
  gunicorn after template changes before browser-verifying.

## Development Workflow

- Develop on feature branches off `main`.
- Production gunicorn serves whatever is on disk at
  `templates/index.html`. Browser-verify changes on a separate dev
  gunicorn on **port 5151** (run with `--reload`) before merging.
- Merge to main only after browser verification.
- Design memos and implementation plans live under
  `docs/superpowers/plans/` and are committed alongside the changes
  they describe.
# Unit A1 — Find Peaks determinism (2026-09-29)

Owner: "Find Peaks' answer must not depend on server load or on the
optimiser's own termination flags. Count refits, not seconds … Judge
convergence by whether the refit actually reached the minimum … no new
magnitude threshold. Acceptance: identical output under light and heavy
machine load, and Scan_6 returns MG2." Scope check first:
`docs/findings/fit-termination-scope/README.md` (Run Fit shares the flag
problem; its step is A2).

## 1. What changed (`autofit/engine.py`)

| site | before | after |
|---|---|---|
| `run_stability_analysis` | refits stopped at a 25 s per-candidate deadline (shared with the primary fit) | exactly `n_refits` refits, always |
| `compare_models` screen | stopped at 60 % of a 240 s sweep budget | every candidate screened |
| `compare_models` sweep | stopped starting candidates when 240 s − 25 s had elapsed | every selected candidate evaluated |
| proposal pass | 60 s pass budget, 35 s stability budget, 15 s minimum-fit refusals (`insufficient_budget`) | none — counted work only (≤ 3 accepted rounds × ≤ 3 attempts) |
| bound-fixed refit | 25 s deadline | `n_refits` refits |
| `fit_candidate` convergence | `leastsq`'s `success` flag; on a failed fit ONE warm restart from the exit point whose flag was taken | the CERTIFICATE (`_certify_minimum`); warm restart removed |

Removed constants: `CANDIDATE_TIMEOUT_SEC`, `TOTAL_ANALYSIS_TIMEOUT_SEC`,
`PROPOSAL_CANDIDATE_TIMEOUT_SEC`, `PROPOSAL_STABILITY_TIMEOUT_SEC`,
`PROPOSAL_MIN_FIT_BUDGET_SEC`, `SCREEN_BUDGET_FRACTION`, `WARM_RESTART_MAX_NFEV`.
The clock is read only for the proposal pass's `wall_time_sec` telemetry
(`proposal_pass_timings`, not in the payload). `analysis_truncated` /
`timed_out` are never set (kept for the payload's shape).

**The certificate** (owner-accepted as proposed): after the `leastsq` fit,
restart from its end point with Trust-Region (`least_squares`, native bounds);
repeat from each improved point until a restart improves chi2 by less than
Trust-Region's own `ftol` (1e-8, read from scipy's signature — no new
constant; relative, so scale-free); at most `CERTIFY_MAX_RESTARTS` = 50
restarts (a count); out of restarts or a non-finite restart = not converged.
Trust-Region, not Levenberg-Marquardt, restarts: an LM restart from a stall
point reproduces the stall (the removed warm restart is exactly that).

## 2. Measurements

**What the old "~30-evaluation convergence" was.** 8-JT C1s Scan_7, MG2,
stability refit 0: `leastsq` stalls at chi2 5220 (18 000 evaluations, flag
False); the warm restart met MINPACK's xtol in 30 evaluations and reported
success there. That point is NOT a minimum (a descent still lowers chi2 — the
KKT check in `tests/autofit/test_fit_certificate.py`). The certified point is
chi2 5166, a genuine CONSTRAINED LOCAL minimum (free gradients ~0, all ten
parameters on bounds pushing outward) — a worse basin than the chi2r 5.21
least_squares reaches from the same start along another path. Correction to
the scope report: "37.6 vs 5.21" was a bad basin, not a point far from a
minimum; "converged" is the right verdict for it now.

**Restarts needed** (8 committed C 1s scans × the 4 gate candidates,
primaries + all refits, 208 fits): 1: 10, 2: 173, 3: 14, 4: 5, then one each
at 5, 6, 8, 9, 11, 21 (flat valleys). With 5 allowed four real minima went
uncertified (8-JT Scan_5's MG2 and MG3 primaries → AG2 at chi2r 42.5 won); 50
certifies all 208. 75 fits `leastsq` flagged as FAILED were certified (capped
at a minimum — the Scan_6 case), none of 208 left uncertified.

**Acceptance — Scan_6.** Gate options: MG2 (chi2r 2.03), as main with budgets
off; main under load had given AG2.

**Acceptance — load.** The page's own request (conductor, C 1s, proposals on,
n_refits 4, endpoint average 3; full grammar, 29–30 candidates screened, 6
deep) on 1-GTA Scan_6 and 8-JT Scan_7, idle, idle again, and with 8 CPU
burners (load average 11):

| | structural fields (winner, tier, candidate set, filter reasons, persistence, ranks, peak roles) | max Δcentre | max rel Δamplitude | max Δarea % |
|---|---|---|---|---|
| idle vs idle | identical (both scans) | 0.20 meV | 3.9e-4 | 7.6e-4 pp |
| idle vs heavy | identical (both scans) | 0.24 meV | 4.9e-4 | 9.4e-4 pp |

The residual numeric differences are Trust-Region's arithmetic jitter (the
BLAS alignment effect CLAUDE.md records; owner decision 2026-09-21 accept and
disclose), present idle-to-idle — not load. Find Peaks used only the
byte-reproducible Levenberg-Marquardt before; the certificate's Trust-Region
restarts bring the jitter in. Wall time (page request, idle): main 208–213 s,
A1 236–239 s; under load A1 342–350 s (main would have truncated).

**Screen interaction (found here).** With every screen fit certified to a
genuine local minimum, the screen now compares honest minima — and MG2's
single screen start on 8-JT Scan_7 lands in a poor one (BIC* 2277, as on main)
while most others improve, so MG2 ranks 19th of 28 and is screened out,
though its deep evaluation reaches the best BIC* of all. Page request: main
MG2 (BIC* 1776.8) vs A1 MG3 (1787.6). Measurement on six more scans: §3.

## 3. The page's own Find Peaks request: main vs A1 (7 distinct committed C 1s scans, idle)

4 of 7 winners identical (UCl4 Scan_8, UCl4 Scan_3, 1-GTA Scan, 1-GTA Scan_6 —
the last MG2 on both). 3 differ:

| scan | main (winner, BIC*) | A1 (winner, BIC*) | why |
|---|---|---|---|
| 8-JT Scan_5 | MG2, 1882.6 | MG3, 1901.5 | MG2 SCREENED OUT on A1 (screen rank 21 of 28) — its single screen start lands in a poor local minimum while the certificate carries most other screen fits to much better ones |
| 8-JT Scan_7 | MG2, 1776.8 | MG3, 1787.6 | the same (MG2 screen rank 19 of 28) |
| 1-GTA Scan_2 | MG3, 1803.9 | MG2, 1816.0 | MG3 deep-evaluated on both with the SAME chi2r 1.388; on main one MG3 slot was "absent" (BIC* drops its parameters) because refits the old flag called non-converged counted as empty; certified, the slot is populated in every refit — no credit. A1 is the honest one here |

The two screen cases pick a model with a WORSE BIC* than main's. The screen's
single-start ranking is pre-existing; the certificate changes which candidates
it happens to favour. OWNER DECISION (see the report).
# Do fits stop before the minimum? Scope check for Unit A (2026-09-28)

Owner, Unit A: "Judge convergence by whether the refit actually reached the
minimum, not by the optimiser's success flag … SCOPE CHECK FIRST: does Run
Fit, or the scattered-starts check, share the ~30-evaluation early stopping?"

## Find Peaks: where the "~30 evaluations" comes from

It is not MINPACK stopping early from a cold start. `autofit.engine.fit_candidate`
fits with `leastsq`; when that fit FAILS (the 18 000-evaluation cap) it makes
ONE warm restart from the exit point with a 2 000-evaluation budget and takes
the restart's result if its `success` flag is set. From a stalled point that
restart ends on MINPACK's `xtol` test in ~30 evaluations and reports success.
Example (8-JT C1s Scan_7, MG2, stability refit 0): the cold `leastsq` fit stalls
at χ²ᵣ 37.6 after 18 000 evaluations; the warm restart "succeeds" there in 30;
`least_squares` from the same start reaches χ²ᵣ 5.21 in 507. The code comment
assumes the failed fit had already reached the minimum; here it had not.

## Run Fit and the scattered-starts check

`scripts/fit_termination_scope.py` runs every one of the 202 committed targets
through `/api/fit` exactly as the page sends it (3 perturbed restarts, 3
scattered starts), intercepts every lmfit fit, and refines each result from its
end point with a fresh `least_squares` fit (same model, data, weights, bounds).
A descent from a minimum cannot lower χ² beyond the optimiser's stopping sliver;
from a point short of it, it does. Summary: `scripts/fit_termination_scope_analyze.py`.

| (success-flagged fits; χ² drop on refinement) | Trust-Region (page default) | Levenberg-Marquardt |
|---|---|---|
| **the fit returned to the student** | 202: drop > 1e-6 on 8, > 1e-3 on 5, > 1 % on 2 (5.7 %, 3.8 %) | 196: > 1e-6 on 32, > 1 % on 5, > 10 % on 1 (26 %, 7205f2094254) |
| perturbed restarts | 498: > 10 % on 162 | 576: > 10 % on 198 |
| scattered starts | 532: > 10 % on 29 | 480: > 10 % on 17 |
| scattered starts flagged failed | 2 (0 at a minimum) | 36 (1 at a minimum) |

Consequences: the student's result stops short on 8 / 202 (TR) and 32 / 196
(LM) targets; the perturbed restarts often "succeed" far from a minimum (they
compete by χ², so a poor one loses — but the fit it would have found is lost);
a scattered start that "succeeds" short of its minimum is counted as reaching /
not beating the fit, so the panel's counts and alternatives are affected.

## What a certificate can and cannot be

A strict rule — "a fresh descent from the end point finds no lower χ²" — would
never certify: at genuine minima a restart almost always shaves off a sliver
(TR: of 1 232 success-flagged fits only 27 refine to exactly the same χ²; 513
drop by ≤ 1e-9, 362 by 1e-9 – 1e-6). The sliver is the optimiser's own stopping
rule at work (relative χ² change ftol: 1e-8 TR, 1.5e-8 LM). The only constant
that can separate "stopped at the minimum" from "stopped short" without
introducing a new one is that ftol itself — dimensionless, not data-scaled.
Measured with it: TR returned fits exceeding their own ftol on refinement 11 /
202; LM 88 / 196; all success-flagged fits 374 / 1 232 (TR), 888 / 1 252 (LM).

exec
/bin/zsh -lc "git diff main..HEAD -- autofit/engine.py | tail -220; cat tests/autofit/test_fit_certificate.py; git diff main..HEAD -- tests/autofit/test_preseed_dominants.py; rg -n 'time\\.|perf_counter|deadline|budget|success|converged|least_squares|lmfit_result' autofit/engine.py; rg -n 'analyze|perf_counter|monotonic|deadline|TIMEOUT|time\\.' app.py; head -85 CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-SKMP3OwF' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-R6JmPzBL' (errno=Operation not permitted)
-    primary fit + all its refits. Once passed, remaining refits are
-    skipped — not run and not counted as failures — so one candidate stuck
-    in a slow-but-nfev-capped region can't consume the rest of the request.
+    Unit A1 (2026-09-29): exactly ``n_refits`` refits, always — no wall-clock
+    deadline. The 25 s per-candidate budget this replaced made persistence
+    (refits reached / refits attempted) depend on server load: on 1-GTA C1s
+    Scan_6 MG2 got 3 or 4 refits depending on how busy the machine was, and
+    2/3 vs 3/4 decided the winner. Work is bounded by counts (n_refits, each
+    fit's max_nfev, the certificate's restarts).
     """
     rng = np.random.default_rng(rng_seed)
     pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
@@ -1205,14 +1201,6 @@ def run_stability_analysis(
     n_attempted = 0
     timed_out = False
     for _ in range(n_refits):
-        if deadline is not None and time.perf_counter() >= deadline:
-            timed_out = True
-            log.warning(
-                "run_stability_analysis: candidate %s hit its %.0fs budget "
-                "after %d/%d refits — remaining refits skipped",
-                model.name, CANDIDATE_TIMEOUT_SEC, n_attempted, n_refits,
-            )
-            break
         n_attempted += 1
         seed = int(rng.integers(0, 2**31 - 1))
         init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
@@ -1616,11 +1604,9 @@ class ComparisonResult:
     # weighted_bic_top, note} or None (BIC/IC math review blocker:
     # selection must not silently rest on a likelihood the fits reject).
     weighted_ic_disagreement: Optional[dict] = None
-    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
-    # evaluating every candidate in the grammar. The candidates evaluated so
-    # far are still ranked/reported normally (best-so-far) — this only flags
-    # that the comparison is partial, so a slow/pathological spectrum
-    # returns an honest incomplete result instead of a request timeout.
+    # Never set since unit A1 (the sweep budget it reported is gone: every
+    # candidate is evaluated); kept so the payload and the page keep their
+    # shape.
     analysis_truncated: bool = False
     n_candidates_evaluated: int = 0
     n_candidates_total: int = 0
@@ -2166,11 +2152,12 @@ def _attempt_proposal(
     absent_slot_area_fraction: float,
     absent_slot_persistence_threshold: float,
     diagnostic_windows: dict[str, tuple[float, float]],
-    budget_remaining: float = float("inf"),
     fit_full_window: bool = False,
     endpoint_avg: int = 1,
 ) -> tuple[Optional[ModelReport], ProposedPeakReport, str]:
-    attempt_start = time.perf_counter()
+    # Unit A1 (2026-09-29): no wall-clock budget — an attempt either runs its
+    # counted work (one augmented fit, n_refits refits) or is rejected on a
+    # data criterion; whether a proposal is accepted must not depend on load.
     base_model = base_report.model
     base_fit = base_report.primary_fit
     aug_model = _augmented_candidate(base_model, spec)
@@ -2187,16 +2174,6 @@ def _attempt_proposal(
         pr.rejection_reason = reason
         return None, pr, "fast_rejected"
 
-    # An augmented fit_candidate has no internal wall clock and runs
-    # ~10-12 s worst-case; starting one with less than PROPOSAL_MIN_FIT_
-    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
-    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
-    # caller passes budget_remaining = min(pass budget, sweep budget) left.
-    if budget_remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
-        return _fast(
-            f"insufficient_budget: {budget_remaining:.1f}s left < "
-            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")
-
     bg = _compute_background(x, y, aug_model.background, endpoint_avg=endpoint_avg)
     try:
         init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
@@ -2251,28 +2228,9 @@ def _attempt_proposal(
             f"base BIC* {base_report.bic_adjusted:.2f} by {PROPOSAL_DELTABIC_THRESHOLD:.1f}"
         )
 
-    # budget_remaining was a snapshot BEFORE the augmented fit; that fit has
-    # since consumed wall time, so the stability deadline must be computed
-    # from what's ACTUALLY left, not the stale snapshot (Codex c1s-fix
-    # review, run B MAJOR — otherwise the stability pass could run
-    # min(stale_budget, 35) s past the fit and overrun the sweep budget).
-    # The floor (not just <= 0) matters because run_stability_analysis
-    # checks its deadline at the TOP of the loop and then runs an unbounded
-    # fit_candidate — so starting stability with only a few seconds left
-    # would still overrun by ~one worst-case fit (Codex c1s-fix RE-CHECK,
-    # run B MAJOR: disposition 2 was not fully closed by the top guard).
-    remaining = budget_remaining - (time.perf_counter() - attempt_start)
-    if remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
-        pr.rejection_reason = (
-            f"insufficient_budget before stability: {remaining:.1f}s left < "
-            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s (one refit could overrun)")
-        return None, pr, "fast_rejected"
-
     stability = run_stability_analysis(
         x, y, weights, aug_model, primary,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-        deadline=time.perf_counter() + min(remaining,
-                                           PROPOSAL_STABILITY_TIMEOUT_SEC),
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2445,7 +2403,6 @@ def _bound_fixed_refit(
         x, y, weights, report.model, outcome,
         noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
         fixed_param_values=fixed,
-        deadline=time.perf_counter() + CANDIDATE_TIMEOUT_SEC,
         fit_full_window=fit_full_window,
         endpoint_avg=endpoint_avg,
     )
@@ -2738,7 +2695,6 @@ def compare_models(
     proposal_attempts: list[tuple[str, ProposedPeakReport]] = []
     timings: list[ProposalPassTiming] = []
     n_cand = len(candidates)
-    sweep_start = time.perf_counter()
     n_evaluated = 0
     analysis_truncated = False
 
@@ -2750,16 +2706,9 @@ def compare_models(
     if n_cand > SCREEN_TOP_K:
         screen_rows: list[dict] = []
         screened: list[tuple[CandidateModel, FitOutcome, float]] = []
-        screen_deadline = sweep_start + SCREEN_BUDGET_FRACTION * TOTAL_ANALYSIS_TIMEOUT_SEC
+        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
+        # which candidates reached the deep phase used to depend on load)
         for idx, model in enumerate(candidates, 1):
-            if time.perf_counter() > screen_deadline:
-                analysis_truncated = True
-                log.warning(
-                    "compare_models: screen budget (%.0f%% of the sweep) "
-                    "exhausted after %d/%d candidates — the deep phase runs "
-                    "on what screened so far",
-                    100 * SCREEN_BUDGET_FRACTION, idx - 1, n_cand)
-                break
             log.info("[screen %2d/%d] %s", idx, n_cand, model.name)
             _report_progress(progress_cb, "screening", idx, n_cand, model.name)
             outcome = fit_candidate(x, y, weights, model,
@@ -2789,30 +2738,11 @@ def compare_models(
             [m.name for m in candidates])
 
     for idx, model in enumerate(candidates, 1):
-        # Pre-check with the candidate's own worst-case budget: a candidate
-        # STARTED just under the wire used to overshoot the sweep budget by
-        # its full stability + proposal cost (measured 310 s wall vs the
-        # 240 s budget on real data — past the gunicorn --timeout 300, i.e.
-        # the exact worker-kill this budget exists to prevent).  Truncating
-        # BEFORE starting a candidate that cannot finish keeps the worst-case
-        # wall ≈ TOTAL_ANALYSIS_TIMEOUT_SEC.
-        elapsed = time.perf_counter() - sweep_start
-        if elapsed > TOTAL_ANALYSIS_TIMEOUT_SEC - CANDIDATE_TIMEOUT_SEC:
-            analysis_truncated = True
-            log.warning(
-                "compare_models: sweep budget cannot fit another candidate "
-                "(%.0fs elapsed of %.0fs) after %d/%d — remaining candidates "
-                "skipped, returning best-so-far",
-                elapsed, TOTAL_ANALYSIS_TIMEOUT_SEC, n_evaluated, len(candidates),
-            )
-            break
+        # Unit A1: every selected candidate is evaluated — no sweep budget
         n_evaluated += 1
         log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
         _report_progress(progress_cb, "stabilizing", idx, len(candidates),
                          model.name)
-        # Shared wall-clock budget for this candidate's primary fit + all its
-        # stability refits (CANDIDATE_TIMEOUT_SEC) — see run_stability_analysis.
-        candidate_deadline = time.perf_counter() + CANDIDATE_TIMEOUT_SEC
         # reuse the screen fit as this candidate's primary (no repeated work)
         primary = screen_fit.get(model.name) or fit_candidate(
             x, y, weights, model, fit_full_window=fit_full_window,
@@ -2824,7 +2754,6 @@ def compare_models(
         stability = run_stability_analysis(
             x, y, weights, model, primary,
             noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
-            deadline=candidate_deadline,
             fit_full_window=fit_full_window,
             endpoint_avg=endpoint_avg,
         )
@@ -2864,20 +2793,12 @@ def compare_models(
             # per-candidate wall budget.  Gates are unchanged per round.
             counts = dict(n_flagged=0, n_over_cap=0, n_attempted=0,
                           n_fast=0, n_stab=0, n_acc=0)
-            timed_out = False
-            pass_start = time.perf_counter()
-            # the pass never spends beyond the sweep's remaining budget —
-            # same worst-case-wall reasoning as the candidate pre-check
-            pass_budget = min(
-                PROPOSAL_CANDIDATE_TIMEOUT_SEC,
-                TOTAL_ANALYSIS_TIMEOUT_SEC - (pass_start - sweep_start))
+            timed_out = False                 # unit A1: never set (no pass budget)
+            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
             rejected: list[ProposedPeakReport] = []
             current = base_report
             current_y_fit = y_fit
             while counts["n_acc"] < PROPOSAL_MAX_PER_CANDIDATE:
-                if time.perf_counter() - pass_start > pass_budget:
-                    timed_out = True
-                    break
                 specs = _detect_residual_proposals(
                     x, y, current_y_fit, noise_floor, current.model,
                     fitted_components=current.primary_fit.components,
@@ -2894,10 +2815,6 @@ def compare_models(
                 counts["n_over_cap"] += max(len(specs) - len(attempts), 0)
                 accepted_this_round = False
                 for spec in attempts:
-                    elapsed = time.perf_counter() - pass_start
-                    if elapsed > pass_budget:
-                        timed_out = True
-                        break
                     counts["n_attempted"] += 1
                     aug_report, pr, outcome = _attempt_proposal(
                         x=x, y=y, weights=weights, base_report=current, spec=spec,
@@ -2905,7 +2822,6 @@ def compare_models(
                         absent_slot_area_fraction=absent_slot_area_fraction,
                         absent_slot_persistence_threshold=absent_slot_persistence_threshold,
                         diagnostic_windows=diagnostic_windows,
-                        budget_remaining=pass_budget - elapsed,
                         fit_full_window=fit_full_window,
                         endpoint_avg=endpoint_avg,
                     )
"""Unit A1 (2026-09-29): Find Peaks judges convergence by a CERTIFICATE, not the
optimiser's flag. A fit has reached a minimum when a fresh Trust-Region descent
from its end point improves chi2 by less than that descent's own stopping
tolerance (scipy least_squares' ftol); restarts repeat from each improved point
up to CERTIFY_MAX_RESTARTS; out of restarts = not converged. The flag was wrong
both ways: a warm restart from a stall "succeeded" in ~30 evaluations at
chi2r 37.6 where the minimum is 5.21 (8-JT C1s Scan_7), and a refit capped at
18 000 evaluations AT the minimum counted as failed (1-GTA C1s Scan_6)."""
import inspect
import os

import numpy as np
import pytest
import scipy.optimize

import autofit.engine as eng
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods.base import poisson_like_weights
from autofit.reference import load_reference_fits

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "autofit", "test_data")
G = resolve([Phase(id="graphite", material_class=MaterialClass.CONDUCTOR, regions=("C 1s",), material="graphite")], "C 1s")


def _scan(project, name):
    rf = next(r for r in load_reference_fits(os.path.join(DATA, project)) if r.name == name)
    x, y = np.asarray(rf.roi_be, float), np.asarray(rf.roi_intensity, float)
    return x, y, poisson_like_weights(y)


def _mg2():
    return next(c for c in G.candidates if c.name == "MG2_graphAsymGL_aliph_sat_CO_C=O")


def test_the_tolerance_is_the_optimisers_own():
    assert eng.CERTIFY_FTOL == inspect.signature(scipy.optimize.least_squares).parameters["ftol"].default
    assert isinstance(eng.CERTIFY_MAX_RESTARTS, int) and eng.CERTIFY_MAX_RESTARTS >= 1


def _kkt_violations(comp, params, x, y_net, w):
    """Parameters along which chi2 still descends: a free parameter with a
    non-negligible gradient, or one on a bound whose gradient points INTO the
    box. Empty = a (constrained) local minimum."""
    chi = lambda pp: float(np.sum(((y_net - comp.eval(pp, x=x)) * w) ** 2))
    c0, bad = chi(params), []
    for n, p in params.items():
        if not p.vary or p.expr is not None:
            continue
        span = (p.max - p.min) if np.isfinite(p.max) and np.isfinite(p.min) else (abs(p.value) or 1.0)
        h = 1e-6 * span
        q = params.copy()
        if p.value - p.min < 1e-9 * span:
            q[n].set(value=p.value + h)
            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
        elif p.max - p.value < 1e-9 * span:
            q[n].set(value=p.value - h)
            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
        else:
            q[n].set(value=p.value + h); cp = chi(q); q[n].set(value=p.value - h); cm = chi(q)
            if abs(cp - cm) / (2 * h) * span > 1e-3 * c0: bad.append(n)
    return bad


def test_a_stall_now_ends_at_a_constrained_local_minimum():
    """Scan_7 MG2, stability refit 0's start. The removed warm restart
    reported success at the leastsq stall point (chi2 5220), which is NOT a
    minimum: a descent still lowers chi2. The certified point satisfies the
    KKT conditions (free gradients ~0, every parameter on a bound pushing out):
    a genuine local minimum, pinned on bounds (chi2r ~37 — a worse basin than
    the 5.21 least_squares finds from the same start by another path)."""
    x, y, w = _scan("8-JT Graphite.proj.zip", "C1s Scan_7")
    model = _mg2()
    primary = eng.fit_candidate(x, y, w, model)
    y_net = y - primary.background
    seed = int(np.random.default_rng(0).integers(0, 2**31 - 1))
    init = eng.perturb_initial_params(model, seed=seed, x=x, y_net=y_net)
    comp = eng._build_composite_model(model)
    stall = comp.fit(y_net, init.copy(), x=x, weights=w, method="leastsq", nan_policy="omit",
                     max_nfev=eng.FIT_CANDIDATE_MAX_NFEV)
    assert _kkt_violations(comp, stall.params, x, y_net, w), "the stall point is not a minimum"
    out = eng.fit_candidate(x, y, w, model, initial_params=init.copy())
    assert out.converged
    assert out.weighted_chi_sq < stall.chisqr
    assert _kkt_violations(comp, out.lmfit_result.params, x, y_net, w) == []


def _two_peak():
    x = np.arange(280.0, 292.0, 0.05)
    t = 500 + 8000 * np.exp(-4 * np.log(2) * ((x - 284.5) / 1.0) ** 2) + 1500 * np.exp(-4 * np.log(2) * ((x - 286.4) / 1.2) ** 2)
    y = t + np.sqrt(t) * np.random.default_rng(5).standard_normal(x.size)
    slot = lambda r, win: eng.ComponentSlot(role=r, region="C 1s", phase_id="p", be_window=win,
                                            line_shape=eng.LineShape.GAUSSIAN, fwhm_range=(0.5, 2.5))
    model = eng.CandidateModel(name="m", background=eng.BackgroundType.LINEAR,
                               slots=(slot("a", (284.0, 285.0)), slot("b", (286.0, 287.0))))
    return x, y, poisson_like_weights(y), model


def test_a_fit_capped_at_the_minimum_is_certified():
    """The Scan_6 case in general form: an optimiser that runs out of
    evaluations while sitting at the minimum reports failure; the certificate
    finds no descent and certifies it."""
    x, y, w, model = _two_peak()
    good = eng.fit_candidate(x, y, w, model)
    assert good.converged
    comp = eng._build_composite_model(model)
    y_sub = y - good.background
    capped = comp.fit(y_sub, good.lmfit_result.params.copy(), x=x, weights=w, method="leastsq",
                      nan_policy="omit", max_nfev=3)          # starts AT the minimum, capped at once
    assert not capped.success
    point, certified = eng._certify_minimum(comp, y_sub, capped, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert certified
    assert point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)


def test_out_of_restarts_is_not_converged(monkeypatch):
    """A start far from the minimum needs more than one restart to certify
    (the first descends a long way); with a single restart allowed it is
    'not converged' — whatever the optimiser says."""
    x, y, w, model = _two_peak()
    comp = eng._build_composite_model(model)
    good = eng.fit_candidate(x, y, w, model)
    y_sub = y - good.background
    far = good.lmfit_result.params.copy()
    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
    short = comp.fit(y_sub, far, x=x, weights=w, method="leastsq", nan_policy="omit", max_nfev=2)
    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 1)
    _, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert not certified
    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 5)
    point, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert certified and point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)


def test_the_warm_restart_is_gone():
    src = inspect.getsource(eng.fit_candidate)
    assert "retry" not in src and "WARM_RESTART" not in src
    assert "converged=bool(certified)" in src
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NEvKsmxU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-EJCB6Xwi' (errno=Operation not permitted)
diff --git a/tests/autofit/test_preseed_dominants.py b/tests/autofit/test_preseed_dominants.py
index 74ec475..596c3a6 100644
--- a/tests/autofit/test_preseed_dominants.py
+++ b/tests/autofit/test_preseed_dominants.py
@@ -345,8 +345,7 @@ def test_proposal_rejected_when_stability_promotes_spurious_center_peg(monkeypat
         x=x, y=y, weights=w, base_report=base, spec=spec,
         noise_floor=1.0, n_refits=2, rng_seed=0,
         absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
-        diagnostic_windows=dict(case.grammar.diagnostic_windows),
-        budget_remaining=1e6)
+        diagnostic_windows=dict(case.grammar.diagnostic_windows))
     assert outcome == "stability_rejected"
     assert "post-stability" in (pr.rejection_reason or "")
     assert any("center@min" in h for h in pr.boundary_hits)
@@ -418,80 +417,30 @@ def test_next_proposal_index_is_max_suffix_plus_one():
     assert eng._next_proposal_index(m0) == 0
 
 
-def test_proposal_pass_respects_sweep_budget(monkeypatch):
-    """Codex c1s-fix MAJOR (run B): an augmented fit has no internal wall
-    clock, so a proposal attempt must fast-reject when too little sweep
-    budget remains rather than running an unbounded fit past the total
-    timeout.  With the fit-budget floor raised above any real remaining
-    budget, EVERY proposal attempt must be 'insufficient_budget' — no
-    augmented fit runs, no proposal is accepted, and the sweep still
-    returns cleanly."""
-    monkeypatch.setattr(eng, "PROPOSAL_MIN_FIT_BUDGET_SEC", 10_000.0)
+def test_no_wall_clock_can_change_the_answer(monkeypatch):
+    """Unit A1 (2026-09-29): the sweep, screen, stability and proposal
+    budgets were wall-clock and made the answer depend on server load; they
+    are gone. A clock that jumps a million seconds on every read must leave
+    the result IDENTICAL."""
     x = _grid()
     truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
              {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
     sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
     y = _noisy(sig + _linear_bg(x), 71)
-    cands = [_cand("single_main", [_slot("main_a", (195.5, 197.5))])]
-    grammar = _grammar(cands)
-    res = get_method("ic_model_comparison").run(
-        x, y, grammar=grammar,
-        options={**IC_OPTS, "enable_preseed": False})
-    assert not res.diagnostics["winner"].endswith("+prop")
-    reasons = [p["rejection_reason"] for c in res.analysis["candidates"]
-               for p in c.get("proposed_peaks", [])]
-    assert reasons, "expected at least one attempted-then-rejected proposal"
-    assert all("insufficient_budget" in (r or "") for r in reasons), reasons
-
-
-def test_stability_not_started_without_budget_after_augmented_fit(monkeypatch):
-    """Codex c1s-fix RE-CHECK (run B): the top budget guard alone did NOT
-    close the overrun — an augmented fit that PASSES the top guard then
-    consumes most of the budget must not let run_stability_analysis start
-    an unbounded refit with only a few seconds left.  The pre-stability
-    guard now fast-rejects when the DYNAMIC remaining budget is below the
-    fit floor.  Deterministic via a fake clock: attempt_start = 1000 s,
-    every later perf_counter reads 1013 s, so with budget_remaining=20 the
-    post-fit remaining is 7 s < 15 s floor — stability must NOT run."""
-    from autofit.methods.base import poisson_like_weights
-    from stress_cases import isolated_missing_peak_case
+    grammar = _grammar([_cand("single_main", [_slot("main_a", (195.5, 197.5))])])
 
-    case = isolated_missing_peak_case(seed=71)
-    x, y = case.x, case.y
-    w = poisson_like_weights(y)
-    model = case.grammar.candidates[0]
-    # real base report (unpatched clock), proposal + preseed off
-    res = eng.compare_models(x, y, w, case.grammar, n_refits=2, rng_seed=0,
-                             enable_proposal_pass=False, enable_preseed=False)
-    base_report = res.reports[0]
-    y_fit = (base_report.primary_fit.lmfit_result.best_fit
-             + base_report.primary_fit.background)
-    specs = eng._detect_residual_proposals(
-        x, y, y_fit, 1.0, model,
-        fitted_components=base_report.primary_fit.components)
-    assert specs, "expected a residual proposal at the unmodeled peak"
-
-    calls = {"n": 0}
+    def run():
+        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
+        return res.diagnostics, res.peaks, res.analysis, res.confidence
 
-    def fake_pc():
-        calls["n"] += 1
-        return 1000.0 + (0.0 if calls["n"] == 1 else 13.0)
+    normal = run()
+    ticks = {"t": 0.0}
 
-    def boom(*a, **k):
-        raise AssertionError("run_stability_analysis started without budget")
-
-    monkeypatch.setattr(eng.time, "perf_counter", fake_pc)
-    monkeypatch.setattr(eng, "run_stability_analysis", boom)
-
-    aug_report, pr, outcome = eng._attempt_proposal(
-        x=x, y=y, weights=w, base_report=base_report, spec=specs[0],
-        noise_floor=1.0, n_refits=4, rng_seed=0,
-        absent_slot_area_fraction=0.02, absent_slot_persistence_threshold=0.7,
-        diagnostic_windows=dict(case.grammar.diagnostic_windows),
-        budget_remaining=20.0)          # passes the 15 s TOP guard...
-    assert outcome == "fast_rejected"   # ...but post-fit remaining 7 s < 15
-    assert aug_report is None
-    assert "insufficient_budget before stability" in (pr.rejection_reason or "")
+    def jumpy():
+        ticks["t"] += 1.0e6
+        return ticks["t"]
+    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
+    assert run() == normal
 
 
 # ── F3: two-phase sweep ────────────────────────────────────────────────────
129:# boundary cleanliness; same per-candidate wall budget).  Measured
142:# Unit A1 (2026-09-29): NO wall-clock budget anywhere in the sweep. The
143:# per-candidate 25 s, the 240 s sweep, the 60 s / 35 s proposal budgets, the
144:# 15 s minimum-fit budget and the screen's share of the sweep all made Find
216:# grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
217:# never finish inside the then 240 s sweep budget (removed in unit A1; it sat
222:# converged screens by BIC, and runs the full pipeline (stability, proposal
603:    converged: bool
609:    lmfit_result: Optional[ModelResult] = None
814:# is Trust-Region (scipy least_squares, native bounds): a Levenberg-Marquardt
818:# of restarts, or a non-finite restart, is "not converged". No new constant:
819:# the tolerance is scipy's own least_squares ftol default, read from its
823:CERTIFY_FTOL = float(_inspect.signature(_scipy_optimize.least_squares).parameters["ftol"].default)
842:                              method="least_squares", nan_policy="omit",
877:    investigation) showed a clean bimodal split: converged fits topped out
880:    leastsq(), surfacing as result.success=False) cuts off the latter
901:        # satisfies xtol in ~30 evaluations and reported success at a
902:        # non-minimum (8-JT C1s Scan_7: chi2r 37.6 "converged" where
903:        # least_squares from the same start reaches 5.21).
908:            converged=False, components=[], residual_sum_sq=float("inf"),
911:            n_data=len(y_sub), lmfit_result=None, background=bg,
916:        # minimum — reported as not converged, whatever the optimiser's flag
920:        converged=bool(certified),
926:        lmfit_result=result,
935:    if primary.lmfit_result is None:
937:    composite = primary.lmfit_result.model
938:    params = primary.lmfit_result.params
1133:    # Best converged refit found during the multi-start pass (by weighted χ²).
1146:    # budget); the denominator of persistence / orphan_rate / convergence_rate.
1173:    deadline. The 25 s per-candidate budget this replaced made persistence
1184:    n_converged = 0
1216:        if not outcome.converged:
1218:        n_converged += 1
1259:        convergence_rate=n_converged / max(n_attempted, 1),
1283:    if primary.lmfit_result is None:
1286:    return sum(1 for pname, par in primary.lmfit_result.params.items()
1545:        lm = self.primary_fit.lmfit_result
1579:    non_converged: list[tuple[CandidateModel, FitOutcome]] = field(default_factory=list)
1607:    # Never set since unit A1 (the sweep budget it reported is gone: every
1620:    # screen outcome: {name, converged, bic, selected} — screened-out
1694:                  if r.primary_fit.converged
2125:    if base_fit.lmfit_result is not None:
2126:        for pname, par in base_fit.lmfit_result.params.items():
2158:    # Unit A1 (2026-09-29): no wall-clock budget — an attempt either runs its
2186:    if not primary.converged:
2268:    y_fit_aug = (primary.lmfit_result.best_fit + primary.background
2269:                 if primary.lmfit_result is not None else np.zeros_like(y))
2372:    lm = report.primary_fit.lmfit_result
2395:    if not outcome.converged:
2409:    y_fit = (outcome.lmfit_result.best_fit + outcome.background
2410:             if outcome.lmfit_result is not None else np.zeros_like(y))
2638:            # the nfev cap (0 converged → no survivor).  Grammar families
2677:                    # phase truncates under its wall budget on rich scans
2679:                    # 21/30) — a budget truncation must never be able to
2694:    non_converged: list[tuple[CandidateModel, FitOutcome]] = []
2702:    #    deep-evaluation budget — every existing gate/battery path is ≤
2709:        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
2718:            if outcome.converged:
2721:                screen_rows.append({"name": model.name, "converged": True,
2724:                non_converged.append((model, outcome))
2725:                screen_rows.append({"name": model.name, "converged": False,
2741:        # Unit A1: every selected candidate is evaluated — no sweep budget
2750:        if not primary.converged:
2751:            non_converged.append((model, primary))
2766:        y_fit = (primary.lmfit_result.best_fit +
2768:                 if primary.lmfit_result is not None else np.zeros_like(y))
2793:            # per-candidate wall budget.  Gates are unchanged per round.
2796:            timed_out = False                 # unit A1: never set (no pass budget)
2797:            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
2838:                            pf.lmfit_result.best_fit + pf.background
2839:                            if pf.lmfit_result is not None else np.zeros_like(y))
2855:                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
2876:    result.non_converged = non_converged
199:    /api/analyze payloads: a stray np scalar must not 500 the route, and
237:    cutoff = time.time() - SESSION_TTL_DAYS * 86400
270:# adjustable defaults surfaced by /api/analyze/meta (spec §5A); anything the
273:# _register_routes local) so the shared /api/analyze helpers below can see it.
289:# /api/analyze shared helpers (Find Peaks; strictly additive — the manual
290:# /api/fit path never touches this code) — extracted so /api/analyze (sync)
291:# and /api/analyze/start + /api/analyze/progress (async, 2026-07-11) share
313:    """Everything _run_analyze_method / _build_analyze_payload need,
314:    assembled once by _validate_analyze_request."""
327:def _validate_analyze_request(body: dict, upload_folder: str) -> _AnalyzeContext:
328:    """ALL the synchronous, cheap validation /api/analyze has always done
345:        raise _AnalyzeError(f"Unknown analyze method '{method_id}' "
414:def _run_analyze_method(ctx: _AnalyzeContext, progress_cb=None):
417:    is None for the synchronous /api/analyze route (no poller to feed)."""
430:        logging.getLogger(__name__).exception("analyze failed")
431:        raise _AnalyzeError("Internal analyze error — see server log.", 500)
434:def _build_analyze_payload(ctx: _AnalyzeContext, res) -> dict:
498:def _analyze_progress_message(evt: dict) -> str:
538:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
618:    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
625:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
648:    started = time.time()
661:            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
670:                rec["heartbeat"] = time.time()
671:                rec["elapsed_sec"] = round(time.time() - started, 1)
688:                        rec["heartbeat"] = time.time()
699:            rec["elapsed_sec"] = round(time.time() - started, 1)
700:            rec["heartbeat"] = time.time()
1071:    # ── Autofit analyze (opt-in Find Peaks; STRICTLY ADDITIVE — the manual
1074:    @app.get("/api/analyze/meta")
1075:    def analyze_meta():
1100:    @app.post("/api/analyze")
1102:    def analyze():
1127:        For a long analysis (60-240s), POST /api/analyze/start + poll
1128:        GET /api/analyze/progress/<job_id> instead — same validation, same
1131:        ``_validate_analyze_request``/``_run_analyze_method``/
1132:        ``_build_analyze_payload`` under the hood (a pure extract-method
1133:        refactor — tests/test_api_analyze.py pins the contract identical).
1139:            ctx = _validate_analyze_request(body, app.config["UPLOAD_FOLDER"])
1140:            res = _run_analyze_method(ctx)
1143:        payload = _build_analyze_payload(ctx, res)
1146:    @app.post("/api/analyze/start")
1148:    def analyze_start():
1150:        Async twin of POST /api/analyze for the Find Peaks progress
1160:        existing synchronous /api/analyze already doing exactly that for
1170:        GET /api/analyze/progress/<job_id> for {status, phase,
1179:            ctx = _validate_analyze_request(body, upload_folder)
1185:        start_time = time.time()
1200:                "elapsed_sec": round(time.time() - start_time, 1),
1201:                "message": _analyze_progress_message(evt),
1206:                res = _run_analyze_method(ctx, progress_cb=_progress_cb)
1207:                payload = _build_analyze_payload(ctx, res)
1210:                    "elapsed_sec": round(time.time() - start_time, 1),
1217:                    "elapsed_sec": round(time.time() - start_time, 1),
1225:                    "analyze job %s crashed", job_id)
1228:                    "elapsed_sec": round(time.time() - start_time, 1),
1237:    @app.get("/api/analyze/progress/<job_id>")
1238:    def analyze_progress(job_id):
1239:        """Poll one analyze job's progress (Find Peaks UI, 2026-07-11).
1242:        (done only — the SAME shape /api/analyze returns), error (error
# XPS Fitting Studio

Web application for XPS (X-ray Photoelectron Spectroscopy) peak fitting,
multi-spectrum visualization, and project management. Python/Flask backend
with an lmfit-driven peak-fitting pipeline; single-page frontend in
`templates/index.html`. Deployed at xps.fortierlab.org via a gunicorn
LaunchAgent + Cloudflare Tunnel.

## Stack

- **Backend:** Python/Flask, served by gunicorn. App factory in [app.py](app.py).
- **Fitting engine:** lmfit ≥ 1.3 (5 methods: leastsq, least_squares, nelder, differential_evolution, basinhopping).
- **Numerics:** numpy, scipy.
- **File parsing:** pandas, openpyxl (xlsx), olefile (vgd).
- **Frontend:** Single-page HTML/JS in `templates/index.html` (~8500 LOC). Vanilla JS, no build step.
- **Charting:** Chart.js 4.4 (CDN).
- **Deployment:** macOS LaunchAgent runs gunicorn on **127.0.0.1:5050** (NOT :5000 — macOS AirTunes intercepts :5000 and returns 403, so health-check :5050); Cloudflare Tunnel publishes to xps.fortierlab.org. Dev gunicorn typically runs on :5151 with `--reload` for pre-merge verification. See [DEPLOY.md](DEPLOY.md) for the full deploy sequence.

## Project Layout

```
app.py                    # Flask app factory + REST routes
fitting.py                # lmfit pipeline, lineshape impls, background algorithms
parser.py                 # File parsers (csv / tsv / txt / xy / xlsx / xls / vgd)
vgd_parser.py             # Thermo Avantage VGD binary parser (uses olefile)
templates/index.html      # Frontend — CSS + HTML + JS in one file
tests/                    # pytest suite (focused on LA + DS+G correctness)
docs/superpowers/plans/   # Agent-authored design memos and implementation plans
uploads/                  # Per-session .npz storage (gitignored)
requirements.txt
venv/                     # virtualenv (do not commit)
```

The Flask backend serves the frontend via `render_template('index.html')`
and exposes a REST API consumed by the page through fetch.

## Backend API

Per-upload sessions store parsed `(energy, counts)` arrays as compressed
`.npz` in `uploads/<session_id>.npz`. No server-side memory state —
compatible with multi-worker gunicorn.

| Method | Path | Purpose |
|---|---|---|
| `GET`    | `/`                       | Serve the frontend (`templates/index.html`). |
| `GET`    | `/api/health`             | Liveness probe. Returns `{status: "ok"}`. |
| `GET`    | `/api/peak-shapes`        | List backend-registered lineshapes (gaussian / lorentzian / pseudo_voigt_gl / asymmetric_gl / doniach_sunjic / ds_g / la_casaxps). |
| `GET`    | `/api/elements`           | Spin-orbit element presets (splitting + area ratio). |
| `POST`   | `/api/upload`             | Upload a spectrum file; returns `session_id` + downsampled preview. |
| `POST`   | `/api/parse-vgd`          | Parse Thermo Avantage VGD binary directly (no session storage). |
| `GET`    | `/api/session/<id>`       | Retrieve a stored session's preview data. |
| `DELETE` | `/api/session/<id>`       | Delete session files. |
| `POST`   | `/api/background`         | Compute background curve for a session. |
| `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |
| `POST`   | `/api/fit/start`          | The same request and validation as `/api/fit` (an immediate identical 400 / 404); runs the SAME `run_fit` in a background thread; returns `{job_id}` 202 (unit 2, 2026-09-27). |
| `GET`    | `/api/fit/progress/<id>`  | The job record: `status` running / done / error / cancelled, `elapsed_sec`, `heartbeat_age_sec`; `result` = exactly the `/api/fit` body; `error` + `http_status` = exactly what `/api/fit` would answer. |
| `POST`   | `/api/fit/cancel/<id>`    | Stop the job (every minimisation aborts via lmfit's `iter_cb`); also automatic after 180 s without a poll. |

## Frontend Architecture

### State

Module-global `state` holds the currently-active tab's working values
(swapped on tab switch by `TabManager.activateTab`):

```js
state = {
  rawBE, rawIntensity,   // full spectrum as loaded
  ccShift,               // charge-correction rigid shift (eV)
  peaks[],               // array of peak objects
  nextId,                // auto-increment peak ID
  chart,                 // Chart.js instance
  residChart,            // Residuals sub-chart instance
  fitResult,             // last fit diagnostics (be, bgIntensity, bgSubtracted, fittedY, chi, etc.)
  lineWidth,             // per-tab line width (sync of tab.lineWidth)
}
```

### Tab model

`TabManager` (a class in `templates/index.html`) holds `tabs[]` and an
`activeId`. Two tab types share the array:

- **Spectrum tab:** has `rawBE`, `rawIntensity`, `peaks`, `fitResult`, `ccShift`, `manualAnchors`, `lineWidth`, `ui` (form field snapshot incl. bg settings, ROI, charge correction method).
- **Stack tab** (`isStack: true`): viewer-only container for references to other spectrum tabs. Has `entries[{id, sourceTabId, color, visible, showFit}]`, `lineWidth`, `verticalOffset`, `_nextColorIdx`. No raw data of its own — entries resolve their source tab at render time.

exec
/bin/zsh -lc "ls -d venv /Users/skyefortier/xps-app/venv; sed -n '580,815p' autofit/engine.py; sed -n '930,1015p' autofit/engine.py; sed -n '1160,1300p' autofit/engine.py; sed -n '410,570p' app.py; sed -n '1175,1275p' app.py; rg -n 'time\\.|perf_counter|budget|deadline|\\.success|stderr|converged' autofit/methods" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
/Users/skyefortier/xps-app/venv
ls: venv: No such file or directory
        else:
            p.add(f"{prefix}amplitude", value=0.0,
                  expr=f"{parent_prefix}amplitude * {ratio_expr}")

    return p


# ─────────────────────────────────────────────────────────────────────────────
# Fit outcome + component extraction
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FittedComponent:
    slot_role: str
    position: float
    fwhm: float          # width-parameter value (m_gauss for DS+G — fitalg convention)
    amplitude: float
    shape_params: dict
    line_shape: Optional[LineShape] = None


@dataclass
class FitOutcome:
    converged: bool
    components: list[FittedComponent]
    residual_sum_sq: float
    weighted_chi_sq: float
    n_params: int
    n_data: int
    lmfit_result: Optional[ModelResult] = None
    background: Optional[np.ndarray] = None
    boundary_hits: list[str] = field(default_factory=list)


def _extract_fitted_components(
    result: ModelResult, model: CandidateModel
) -> list[FittedComponent]:
    out: list[FittedComponent] = []
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        pars = result.params
        try:
            center = float(pars[f"{prefix}center"].value)
            amplitude = float(pars[f"{prefix}amplitude"].value)
            fwhm = float(pars[f"{prefix}{_width_param(slot.line_shape)}"].value)
        except KeyError:
            continue
        shape_params = {}
        for name, _, _, _ in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
            par = pars.get(f"{prefix}{name}")
            if par is not None:
                shape_params[name] = float(par.value)
        if slot.line_shape is LineShape.DS_G:
            shape_params["m_gauss"] = fwhm
        out.append(FittedComponent(
            slot_role=slot.role, position=center, fwhm=fwhm,
            amplitude=amplitude, shape_params=shape_params,
            line_shape=slot.line_shape,
        ))
    return out


# Shape-parameter names allowed to saturate at bounds per lineshape (shape
# preference, not pathology).  Width-like params are NOT excluded.
_BOUNDARY_EXCLUDED: dict[LineShape, frozenset[str]] = {
    LineShape.GAUSSIAN: frozenset(),
    LineShape.LORENTZIAN: frozenset(),
    LineShape.PSEUDO_VOIGT: frozenset({"gl_ratio"}),
    LineShape.ASYM_GL: frozenset({"gl_ratio", "asymmetry"}),
    LineShape.DS: frozenset({"alpha", "gamma_asym"}),
    LineShape.DS_G: frozenset({"alpha"}),          # beta is a WIDTH here — counted
    LineShape.LACX: frozenset({"alpha", "beta"}),  # both are exponents here
}


def _role_for_param(pname: str, role_by_prefix: dict[str, str]) -> Optional[str]:
    for prefix in sorted(role_by_prefix, key=len, reverse=True):
        if pname.startswith(prefix):
            return role_by_prefix[prefix]
    return None


def _detect_boundary_hits(params: Parameters, model: CandidateModel) -> list[str]:
    """Varying params within 1% of a finite bound → 'role:param@min|max'."""
    hits: list[str] = []
    role_by_prefix = {_slot_prefix(s.role): s.role for s in model.slots}
    shape_by_role = {s.role: s.line_shape for s in model.slots}

    for pname, par in params.items():
        if not par.vary:
            continue
        lo, hi = par.min, par.max
        if not (np.isfinite(lo) and np.isfinite(hi)) or hi <= lo:
            continue
        tol = 0.01 * (hi - lo)
        at_min = (par.value - lo) < tol
        at_max = (hi - par.value) < tol
        if not (at_min or at_max):
            continue
        role = _role_for_param(pname, role_by_prefix)
        short = pname[len(_slot_prefix(role)):] if role is not None else pname
        shape = shape_by_role.get(role)
        if shape is not None and short in _BOUNDARY_EXCLUDED.get(shape, frozenset()):
            continue
        # amplitude at min (=0) → component absent: surfaced via stability
        if short == "amplitude" and at_min:
            continue
        # relaxed doublet ratio at a bound is a real constraint violation —
        # counted (it means the data is fighting the physical ratio window).
        hits.append(f"{role or '?'}:{short}@{'min' if at_min else 'max'}")
    return hits


def _proposed_slot_pegs(outcome: FitOutcome, role: str) -> list[str]:
    """Boundary pegs for one proposed slot, using the SAME detector (and the
    same ``_BOUNDARY_EXCLUDED`` shape-endpoint policy) as every grammar slot.

    Shape endpoints (a pure-Gaussian ``gl_ratio``=0, a pure-Lorentzian
    ``gl_ratio``=1) are LEGITIMATE physics, not constraint violations — the
    grammar excludes them from boundary hits, and treating a proposal that
    reaches one as spurious would drop real pure-Gaussian/Lorentzian peaks
    (measured: the two-narrow-peak F2 case regressed to zero accepted
    proposals when shape pegs were rejected).  So the caller tolerates
    ``{role}:fwhm@max`` (the physical-width ceiling doing its job) and any
    shape endpoint, and rejects on a SUBSTANTIVE peg — ``center`` at a window
    edge, ``amplitude`` at a wall, or ``fwhm@min`` (an implausibly narrow
    spike) (Codex fwhm-cap review, run A: the accurate statement of "which
    pegs reject").
    """
    return [h for h in outcome.boundary_hits if h.startswith(f"{role}:")]


def _unphysical_width_flags(
    components: "list[FittedComponent]", model: CandidateModel
) -> list[str]:
    """Fitted components whose width reaches the ordinary physical FWHM
    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.

    A slot is grammar-sanctioned-broad — EXEMPT, because its width is region
    physics cited in the region module, not an unphysical stretch — if and
    only if it carries an explicit ``ComponentSlot.broad_justification``
    (C 1s π→π* satellite, U 4f mains, B 1s, …; see each region module for its
    citation or honest UNVERIFIED-empirical disclosure). Any other slot —
    contamination, the aliphatic main, and the region-``unassigned`` F1
    pre-seed / F2-F3 proposal slots — that fits at/above the ordinary
    ceiling is flagged: the optimizer wanted a wider (fatter) peak than an
    ordinary component physically has, the cap held it at the limit, and the
    decomposition must be reported low-confidence (routes to the CONDITIONAL
    tier via rank_and_filter) rather than silently accepted.

    ``broad_justification`` is INDEPENDENT of ``fwhm_range``'s own magnitude
    (2026-07-20 refactor, Codex-caught in the MIXED material-class review):
    the exemption used to be inferred from ``declared_hi >
    FWHM_MAX_ORDINARY_EV`` alone, which conflated "the optimizer may search
    this wide" with "this region module vouches the width is real physics".
    Widening a bound for an unrelated reason (numerical-stability headroom,
    a wider calibration envelope, MIXED material class's relaxed
    contamination ceiling) used to silently grant the vouching exemption as
    a side effect. Region-agnostic: the exemption is driven entirely by
    each slot's own declared field, so no region's cited widths are ever
    mis-flagged, and no bound can ever again disable this safety net merely
    by being wide.
    """
    slots_by_role = {s.role: s for s in model.slots}
    flags: list[str] = []
    for c in components:
        slot = slots_by_role.get(c.slot_role)
        if slot is None:
            continue
        declared_lo, declared_hi = slot.fwhm_range
        vouched = slot.broad_justification is not None
        # EFFECTIVE width (Stage-2 PHYSICAL bar): DS+G's width lives in TWO
        # params — beta (Lorentzian HWHM, eV) and m_gauss (Gaussian FWHM;
        # what comp.fwhm carries) — so the checks below must see the
        # convolved width, not the Gaussian part alone (a component could
        # otherwise be ~3+ eV wide while every width check reads 1.0:
        # exactly the 'neighbor broadened to hide a missed peak' channel).
        # Olivero & Longbothum 1977 Voigt-FWHM approximation (0.02%).
        eff_fwhm = c.fwhm
        if c.line_shape is LineShape.DS_G:
            f_l = 2.0 * float(c.shape_params.get("beta", 0.0))
            eff_fwhm = 0.5346 * f_l + np.sqrt(0.2166 * f_l ** 2 + c.fwhm ** 2)
            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
                flags.append(
                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
                    f"β={c.shape_params.get('beta', 0.0):.2f} + "
                    f"m={c.fwhm:.2f}; no known-broad justification)")
                continue
        elif c.line_shape is LineShape.ASYM_GL:
            # asym-GL broadens its high-BE side to fwhm×(1+asymmetry)
            # (fitting.py convention) — the MEAN effective width
            # fwhm×(1+asym/2) closes the remaining papering-over channel
            # (Codex Stage-2 review, run A MAJOR).
            asym = float(c.shape_params.get("asymmetry", 0.0))
            eff_fwhm = c.fwhm * (1.0 + 0.5 * asym)
            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
                flags.append(
                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
                    f"fwhm={c.fwhm:.2f}×(1+{asym:.2f}/2); no known-broad "
                    "justification)")
                continue
        # detection-family slots (scale-relative ceilings, usually > the
        # ordinary cap): a component at ≥ DETECTION_WIDTH_ABSORB_FRACTION
        # of its own ceiling (= 1.75× the DETECTED width via the 2.5×
        # ceiling) is absorbing neighboring intensity — the papering-over
        # signature in transferable units. Unaffected by broad_justification
        # (these are engine-constructed proposal/pre-seed slots, not
        # region-module-authored grammar; their ceiling is scale-relative,
        # not a physics vouch).
        if c.slot_role.startswith("detected_peak_"):
            if eff_fwhm >= DETECTION_WIDTH_ABSORB_FRACTION * declared_hi:
                flags.append(
                    f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥"
                    f"{DETECTION_WIDTH_ABSORB_FRACTION:.2f}×ceiling "
                    f"({declared_hi:.2f}eV) — ~1.75× its detected width; "
                    "likely absorbing a neighbor")
            continue
        if vouched:
            continue                       # grammar-sanctioned-broad slot
        # pegging the ordinary ceiling — same 1%-of-range tol as boundary
        # detection, so a component held AT the 2.0 cap is caught
        tol = 0.01 * (declared_hi - declared_lo) if declared_hi > declared_lo else 0.0
        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
            flags.append(
                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
                "ordinary cap (no known-broad justification)")
    return flags


# ── Convergence certificate (unit A1, 2026-09-29) ─────────────────────────────
# A fit has reached a minimum when a fresh descent from its end point cannot
# improve chi2 by more than the descent's OWN stopping tolerance. The descent
# is Trust-Region (scipy least_squares, native bounds): a Levenberg-Marquardt
# restart from a stall point reproduces the stall (MINPACK's xtol test fires in


def compute_slot_areas(
    model: CandidateModel, primary: FitOutcome, x: np.ndarray
) -> dict[str, float]:
    if primary.lmfit_result is None:
        return {}
    composite = primary.lmfit_result.model
    params = primary.lmfit_result.params
    out: dict[str, float] = {}
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        sub = next((c for c in composite.components if c.prefix == prefix), None)
        if sub is None:
            continue
        out[slot.role] = float(abs(trapezoid(sub.eval(params, x=x), x)))
    return out


def perturb_initial_params(
    model: CandidateModel,
    seed: int,
    position_jitter_eV: float = 0.15,
    fwhm_jitter_frac: float = 0.20,
    amplitude_jitter_frac: float = 0.30,
    x: Optional[np.ndarray] = None,
    y_net: Optional[np.ndarray] = None,
    fit_full_window: bool = False,
) -> Parameters:
    """
    Perturbed starting parameters for a multi-start refit (bounds-clipped).

    Port improvement over fitalg: when (x, y_net) are provided the defaults
    are data-informed — in particular the amplitude UPPER bound scales with
    the spectrum instead of the fixed 1e5 fallback, which silently clamped
    (and systematically failed) stability refits on peaks brighter than 1e5
    counts (e.g. the UCl4-BN N 1s line at ~1.06e5).
    """
    rng = np.random.default_rng(seed)
    params = _default_params_from_slots(model, x=x, y_net=y_net,
                                        fit_full_window=fit_full_window)

    def _clip(par, new_val: float) -> None:
        lo = par.min if np.isfinite(par.min) else -np.inf
        hi = par.max if np.isfinite(par.max) else np.inf
        par.set(value=float(np.clip(new_val, lo, hi)))

    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        if slot.linked_to is None:
            cp = params.get(f"{prefix}center")
            if cp is not None and cp.expr is None:
                _clip(cp, cp.value + rng.normal(0.0, position_jitter_eV))
        else:
            op = params.get(f"{prefix}offset")
            if op is not None:
                _clip(op, op.value + rng.normal(0.0, position_jitter_eV))

        fp = params.get(f"{prefix}{_width_param(slot.line_shape)}")
        if fp is not None and fp.expr is None and fp.vary:
            _clip(fp, fp.value * max(1.0 + rng.normal(0.0, fwhm_jitter_frac), 0.1))

        ap = params.get(f"{prefix}amplitude")
        if ap is not None and ap.expr is None:
            _clip(ap, ap.value * max(1.0 + rng.normal(0.0, amplitude_jitter_frac), 0.1))
    return params


# ─────────────────────────────────────────────────────────────────────────────
# Component ↔ slot matching
# ─────────────────────────────────────────────────────────────────────────────

def _is_asymmetric_component(comp: FittedComponent) -> bool:
    sp = comp.shape_params
    if comp.line_shape in (LineShape.DS, LineShape.DS_G):
        return float(sp.get("alpha", 0.0)) > ALPHA_SYMMETRY_THRESHOLD
    if comp.line_shape is LineShape.ASYM_GL:
        return float(sp.get("asymmetry", 0.0)) > ALPHA_SYMMETRY_THRESHOLD
    if comp.line_shape is LineShape.LACX:
        return abs(float(sp.get("alpha", 1.0)) - float(sp.get("beta", 1.0))) \
            > LACX_EXPONENT_ASYMMETRY
    return False


def _effective_be_window(
    slot: ComponentSlot, components: list[FittedComponent],
    y: np.ndarray,
    weights: np.ndarray,
    model: CandidateModel,
    primary_fit: FitOutcome,
    noise_floor: float,
    n_refits: int = 20,
    rng_seed: int = 0,
    fixed_param_values: Optional[dict[str, float]] = None,
    fit_full_window: bool = False,
    endpoint_avg: int = 1,
) -> ModelStability:
    """
    Unit A1 (2026-09-29): exactly ``n_refits`` refits, always — no wall-clock
    deadline. The 25 s per-candidate budget this replaced made persistence
    (refits reached / refits attempted) depend on server load: on 1-GTA C1s
    Scan_6 MG2 got 3 or 4 refits depending on how busy the machine was, and
    2/3 vs 3/4 decided the winner. Work is bounded by counts (n_refits, each
    fit's max_nfev, the certificate's restarts).
    """
    rng = np.random.default_rng(rng_seed)
    pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
    fw: dict[str, list[float]] = {s.role: [] for s in model.slots}
    am: dict[str, list[float]] = {s.role: [] for s in model.slots}
    occupied: dict[str, int] = {s.role: 0 for s in model.slots}
    n_converged = 0
    n_with_orphans = 0
    # Same widened bounds every refit was actually built with (constant
    # across this candidate's whole stability pass) — identity-matching
    # must agree with the bound the fit was allowed to search, or a
    # component correctly placed outside its ORIGINAL window becomes an
    # orphan here, tanking persistence for the very slot this option
    # exists to rescue (Codex-caught, see _effective_be_window).
    bound_overrides = _full_window_bound_overrides(model, x) if fit_full_window else None

    # Data-informed perturbation seeds (see perturb_initial_params): reuse
    # the primary fit's background rather than recomputing per refit.
    bg = primary_fit.background
    y_net = y - bg if bg is not None else None

    best_outcome: Optional[FitOutcome] = None
    refit_chis: list[float] = [float(primary_fit.weighted_chi_sq)]
    n_attempted = 0
    timed_out = False
    for _ in range(n_refits):
        n_attempted += 1
        seed = int(rng.integers(0, 2**31 - 1))
        init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
                                      fit_full_window=fit_full_window)
        if fixed_param_values:
            # bound-fixed refit stability: the constrained parameters stay
            # fixed at their bounds in every multi-start refit
            for pname, val in fixed_param_values.items():
                if pname in init:
                    init[pname].set(value=float(val), vary=False)
        outcome = fit_candidate(x, y, weights, model, initial_params=init,
                                endpoint_avg=endpoint_avg)
        if not outcome.converged:
            continue
        n_converged += 1
        refit_chis.append(float(outcome.weighted_chi_sq))
        if best_outcome is None or outcome.weighted_chi_sq < best_outcome.weighted_chi_sq:
            best_outcome = outcome
        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
                                            bound_overrides=bound_overrides)
        if slot_map.pop("__orphans__", []):
            n_with_orphans += 1
        for role, comp in slot_map.items():
            if comp is None:
                continue
            occupied[role] += 1
            pos[role].append(comp.position)
            fw[role].append(comp.fwhm)
            am[role].append(comp.amplitude)

    def _med(v):  # median or None
        return float(np.median(v)) if v else None

    def _mad(v):
        if not v:
            return None
        arr = np.asarray(v)
        return float(np.median(np.abs(arr - np.median(arr))))

    per_slot = {
        role: SlotStability(
            role=role,
            persistence=occupied[role] / max(n_attempted, 1),
            position_median=_med(pos[role]), position_mad=_mad(pos[role]),
            fwhm_median=_med(fw[role]), fwhm_mad=_mad(fw[role]),
            amplitude_median=_med(am[role]), amplitude_mad=_mad(am[role]),
        )
        for role in occupied
    }
    best_chi = min(refit_chis)
    basin_support = sum(1 for c in refit_chis
                        if c <= best_chi * (1.0 + BASIN_SUPPORT_RTOL))
    return ModelStability(
        per_slot=per_slot,
        orphan_rate=n_with_orphans / max(n_attempted, 1),
        convergence_rate=n_converged / max(n_attempted, 1),
        best_outcome=best_outcome,
        best_basin_support=basin_support,
        n_attempted=n_attempted,
        timed_out=timed_out,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Absent slots
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AbsentSlotReport:
    role: str
    persistence: float
    fitted_area: float
    main_area: float
    area_fraction: float
    threshold: float
    removed_n_params: int


def _count_slot_free_params(slot: ComponentSlot, primary: FitOutcome) -> int:
    if primary.lmfit_result is None:
        return 0
    prefix = _slot_prefix(slot.role)
    return sum(1 for pname, par in primary.lmfit_result.params.items()
               if pname.startswith(prefix) and par.vary)


def _is_main_role(role: str) -> bool:
    """Main-slot convention: bare role or region-prefixed role starts 'main'."""
    return role.split("__")[-1].startswith("main")


def _linked_groups(model: CandidateModel) -> list[list[ComponentSlot]]:
    """
    Connected components of non-main slots over ``linked_to`` edges (edges
    touching a main slot do not bind — mains are never absent-eligible, so a
    satellite linked to a main is its own group; a satellite DOUBLET
    (sat5/2 → sat7/2) is one group).

    return _AnalyzeContext(x, y, method_id, opts, peak_specs, grammar)


def _run_analyze_method(ctx: _AnalyzeContext, progress_cb=None):
    """The one genuinely slow/unpredictable step — the ONLY part that
    runs on a background thread for the async job path.  ``progress_cb``
    is None for the synchronous /api/analyze route (no poller to feed)."""
    from autofit.methods import get_method

    try:
        return get_method(ctx.method_id).run(
            ctx.x, ctx.y, grammar=ctx.grammar, peak_specs=ctx.peak_specs,
            options=ctx.opts, progress_cb=progress_cb)
    except (ValueError, TypeError) as exc:
        # the method's own option/spec validation — TypeError included:
        # a malformed option VALUE (e.g. n_refits: []) raises TypeError
        # from the methods' numeric casts (Codex re-check blocker)
        raise _AnalyzeError(f"invalid option or spec: {exc}")
    except Exception:
        logging.getLogger(__name__).exception("analyze failed")
        raise _AnalyzeError("Internal analyze error — see server log.", 500)


def _build_analyze_payload(ctx: _AnalyzeContext, res) -> dict:
    """Shape the method result into the wire payload — byte-identical to
    the pre-refactor inline logic, incl. the Stage-2 structural-only
    degradation branch (a region with zero grammar candidates still RUNS
    via the detection family; the honest structure-report stub returns
    only when detection found nothing fittable either)."""
    grammar = ctx.grammar
    if (grammar is not None and grammar.structural_only
            and not grammar.candidates and not res.success):
        non_verified = sorted({
            f"{slug}:{e['constant']}"
            for slug, entries in grammar.provenance.items()
            for e in entries if e.get("status") != "VERIFIED"
        })
        return {
            "method": ctx.method_id,
            "success": False,
            "structural_only": list(grammar.structural_only),
            "structure_report": grammar.provenance,
            "notes": grammar.notes,
            "uses_conditional_or_unverified_constants": non_verified,
            "peaks": [],
            "confidence": {},
            "message": (
                "structure known, positions UNVERIFIED — detection "
                "found no fittable features in this window; supply a "
                "cited source (autofit.cited_values schema) and "
                "curated windows to enable grammar fitting for: "
                + ", ".join(grammar.structural_only)),
            "review_gate": {
                "reviewed_by": None,
                "note": "results are candidates + honesty flags, "
                        "not ground truth — a named human review is "
                        "required before export (spec §8)",
            },
        }

    payload = {
        "method": ctx.method_id,
        "success": bool(res.success),
        # Phase D: regions that resolved structure-only in a MIXED
        # request (deep + structural) are flagged here; their derived
        # structure rides in analysis.constants_provenance.
        "structural_only": list(grammar.structural_only) if grammar else [],
        "peaks": res.peaks,
        "confidence": res.confidence,
        "analysis": res.analysis,
        "diagnostics": res.diagnostics,
        "message": res.message,
        "review_gate": {
            "reviewed_by": None,
            "note": "results are candidates + confidence flags, not "
                    "ground truth — a named human review is required "
                    "before export (spec §8)",
        },
    }
    if grammar is not None and grammar.structural_only:
        # structural regions that DID fit (detection family) still ship
        # their derived-structure report for the honesty surface
        payload["structure_report"] = grammar.provenance
        payload["notes"] = grammar.notes
    return payload


def _analyze_progress_message(evt: dict) -> str:
    """Human-readable progress line from one engine progress_cb event —
    the exact wording the goal asked for ('candidate 7 of 29 . stabilizing')."""
    phase = evt.get("phase")
    idx, total = evt.get("candidate_index"), evt.get("candidate_total")
    name = evt.get("candidate_name")
    if phase == "screening" and idx and total:
        msg = f"screening candidate {idx} of {total}"
    elif phase == "stabilizing" and idx and total:
        msg = f"candidate {idx} of {total} — stabilizing"
    else:
        return phase or "working…"
    return msg + (f" ({name})" if name else "")


def _job_progress_path(job_id: str, upload_folder: str) -> Path:
    return Path(upload_folder) / f"{job_id}.job.json"


def _write_job_progress(job_id: str, upload_folder: str, data: dict) -> None:
    """Atomic write (temp file + os.replace) — required because the
    writer (background thread, possibly in a DIFFERENT gunicorn worker
    process than whichever one later serves a poll GET) and the reader
    are never synchronized otherwise; a half-written file must never be
    visible to a concurrent poll."""
    path = _job_progress_path(job_id, upload_folder)
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(json.dumps(_json_sanitize(data)))
        os.replace(tmp, path)
    except OSError:
        logging.getLogger(__name__).exception(
            "failed to write progress for job %s", job_id)


def _sweep_expired_jobs(upload_folder: str) -> None:
    """Opportunistic TTL cleanup of stale job progress files — same
    pattern as _sweep_expired_sessions (audit F13): runs on each new job
    start, no scheduler/thread, tolerates a concurrent worker deleting the
    same file first, never raises."""
    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
    try:
        candidates = list(Path(upload_folder).glob("*.job.json"))
    except OSError:
        return
    for p in candidates:
        try:
            if p.stat().st_mtime < cutoff:
                p.unlink(missing_ok=True)
        except FileNotFoundError:
            pass
        except OSError:
            pass


# ── Fit jobs (unit 2, 2026-09-27) ────────────────────────────────────────────
# Records are the Find Peaks job files (<job>.job.json, the same TTL sweep);
# two small markers beside each: <job>.cancel (written by /api/fit/cancel,
# any worker) and <job>.polled (touched by every poll). The fit thread's
# cancel condition: the cancel marker exists, OR no poll for
# FIT_JOB_ABANDON_SEC (a closed tab, a sleeping laptop; 180 s, above the ~1 min timer throttling browsers apply to hidden tabs).
FIT_JOB_ABANDON_SEC = 180   # > Chrome's 1-minute timer throttling in a hidden tab: a student who switches browser tabs keeps the fit
FIT_JOB_HEARTBEAT_SEC = 2.0
# Concurrency (unit 2, Codex round 1). Before start-then-poll, gunicorn's four
# SYNC workers bounded concurrent fits at four; a fit thread per start would
# not. Each worker process runs at most FIT_JOB_MAX_RUNNING fits at once (the
# rest wait "queued", heartbeating, cancellable) and admits at most
# FIT_JOB_MAX_ADMITTED running + queued jobs; beyond that /api/fit/start
# answers 503 "busy" immediately. With production's 4 workers: at most 4
# concurrent fits, as before.
FIT_JOB_MAX_RUNNING = 1
FIT_JOB_MAX_ADMITTED = 6
_FIT_JOB_RUN_SLOTS = threading.BoundedSemaphore(FIT_JOB_MAX_RUNNING)
        if not isinstance(body, dict):
            return _err("request body must be a JSON object")
        upload_folder = app.config["UPLOAD_FOLDER"]
        try:
            ctx = _validate_analyze_request(body, upload_folder)
        except _AnalyzeError as exc:
            return _err(str(exc), exc.status)

        job_id = str(uuid.uuid4())
        _sweep_expired_jobs(upload_folder)
        start_time = time.time()
        _write_job_progress(job_id, upload_folder, {
            "status": "running", "phase": "starting",
            "candidate_index": None, "candidate_total": None,
            "candidate_name": None, "elapsed_sec": 0.0,
            "message": "starting analysis…",
        })

        def _progress_cb(evt: dict) -> None:
            _write_job_progress(job_id, upload_folder, {
                "status": "running",
                "phase": evt.get("phase"),
                "candidate_index": evt.get("candidate_index"),
                "candidate_total": evt.get("candidate_total"),
                "candidate_name": evt.get("candidate_name"),
                "elapsed_sec": round(time.time() - start_time, 1),
                "message": _analyze_progress_message(evt),
            })

        def _worker() -> None:
            try:
                res = _run_analyze_method(ctx, progress_cb=_progress_cb)
                payload = _build_analyze_payload(ctx, res)
                _write_job_progress(job_id, upload_folder, {
                    "status": "done", "phase": "done",
                    "elapsed_sec": round(time.time() - start_time, 1),
                    "message": "done",
                    "result": payload,
                })
            except _AnalyzeError as exc:
                _write_job_progress(job_id, upload_folder, {
                    "status": "error", "phase": "done",
                    "elapsed_sec": round(time.time() - start_time, 1),
                    "message": "failed", "error": str(exc),
                    "http_status": exc.status,
                })
            except Exception as exc:      # belt-and-suspenders: the
                # indicator must ALWAYS clear, even on a bug we didn't
                # anticipate — never let a job hang the poll forever.
                logging.getLogger(__name__).exception(
                    "analyze job %s crashed", job_id)
                _write_job_progress(job_id, upload_folder, {
                    "status": "error", "phase": "done",
                    "elapsed_sec": round(time.time() - start_time, 1),
                    "message": "failed",
                    "error": f"internal error: {exc}",
                    "http_status": 500,
                })

        threading.Thread(target=_worker, daemon=True).start()
        return jsonify({"job_id": job_id}), 202

    @app.get("/api/analyze/progress/<job_id>")
    def analyze_progress(job_id):
        """Poll one analyze job's progress (Find Peaks UI, 2026-07-11).
        {status: 'running'|'done'|'error', phase, candidate_index,
        candidate_total, candidate_name, elapsed_sec, message, result
        (done only — the SAME shape /api/analyze returns), error (error
        only)}. 404 for an unknown/expired job_id; 400 for a malformed
        one (path-traversal guard, same convention as _validate_session_id)."""
        try:
            uuid.UUID(job_id)
        except ValueError:
            return _err("Invalid job_id format (expected UUID)", 400)
        path = _job_progress_path(job_id, app.config["UPLOAD_FOLDER"])
        if not path.exists():
            return _err(f"Job '{job_id}' not found", 404)
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            # os.replace() makes writes atomic, but tolerate a read racing
            # the very first write rather than 500ing a normal poll
            data = {"status": "running", "phase": "starting",
                    "candidate_index": None, "candidate_total": None,
                    "candidate_name": None, "elapsed_sec": 0.0,
                    "message": "starting analysis…"}
        return jsonify(data)

    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
    # minutes. The fit runs in a background thread on Find Peaks' job
    # infrastructure (an atomic JSON record under the upload folder, readable
    # by whichever gunicorn worker serves a poll); every HTTP request is short.
    # The record: {status: queued|running|done|error|cancelled, elapsed_sec,
    # heartbeat (epoch s, rewritten every 2 s while the fit thread lives),
    # result (done: EXACTLY the /api/fit body), error + http_status (error:
    # exactly what /api/fit would have answered)}.

    @app.post("/api/fit/start")
    @_require_json
autofit/methods/ic_model_comparison.py:81:            "overall time budget was reached"
autofit/methods/ic_model_comparison.py:94:                         "for filtered/non-converged detail (diagnostic, not "
autofit/methods/ic_model_comparison.py:190:                "n_non_converged": len(result.non_converged),
autofit/methods/ic_model_comparison.py:232:            stderr = {}
autofit/methods/ic_model_comparison.py:234:                if pname.startswith(prefix) and par.stderr is not None:
autofit/methods/ic_model_comparison.py:235:                    stderr[pname[len(prefix):]] = float(par.stderr)
autofit/methods/ic_model_comparison.py:236:            if stderr:
autofit/methods/ic_model_comparison.py:237:                rec["stderr"] = stderr
autofit/methods/ic_model_comparison.py:325:        "non_converged": [m.name for m, _ in result.non_converged],
autofit/methods/sparse_map.py:228:            converged = kkt <= cfg["kkt_rtol"] * lam
autofit/methods/sparse_map.py:234:                                     "converged": bool(converged)})
autofit/methods/sparse_map.py:248:                                     "converged": bool(converged)})
autofit/methods/sparse_map.py:256:                   "kkt_violation": float(kkt), "converged": bool(converged)}
autofit/methods/sparse_map.py:333:            "path_fully_converged": all(r["converged"] for r in path_records),
autofit/methods/sparse_map.py:352:                         "converged": best["converged"]},
autofit/methods/least_squares.py:71:            stderr = {name: info.get("stderr") for name, info in par.items()}
autofit/methods/least_squares.py:72:            has_cov = any(v is not None for v in stderr.values())
autofit/methods/least_squares.py:76:                    "values": stderr if has_cov else None,
autofit/methods/bayesian_exchange_mc.py:271:            # not a perfectly-converged one (Codex Stage-5 finding #3) —
autofit/methods/bayesian_exchange_mc.py:336:        # re-check evidence: at reduced budgets a single run can report a
autofit/methods/bayesian_exchange_mc.py:424:        # is UNRESOLVED at this sweep budget — surfaced, never silent.
autofit/methods/multivariate_mcr.py:208:        als_converged = (final_delta is not None
autofit/methods/multivariate_mcr.py:242:            "als_converged": bool(als_converged),
autofit/methods/multivariate_mcr.py:272:                         "als_converged": bool(als_converged),
autofit/methods/max_entropy.py:148:        converged = chi_r <= cfg["chi_sq_target"]
autofit/methods/max_entropy.py:178:            "chi_sq_target_reached": bool(converged),
autofit/methods/max_entropy.py:200:                         "chi_sq_target_reached": bool(converged)},
autofit/methods/max_entropy.py:203:                     f"target {'reached' if converged else 'NOT reached'})"),

codex
The engine’s remaining clock reads feed proposal timing telemetry; I found no time-based branch controlling fits or refit counts. The certificate retains the lowest-χ² result. I’m checking the result metadata and whether the tests cover the screen and proposal paths they claim to protect.

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -q -p no:cacheprovider tests/autofit/test_fit_certificate.py tests/autofit/test_preseed_dominants.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 exited 1 in 196ms:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pytest/__main__.py", line 9, in <module>
    raise SystemExit(pytest.console_main())
                     ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism']

exec
/bin/zsh -lc "sed -n '190,360p' autofit/methods/bayesian_exchange_mc.py; sed -n '2160,2315p' autofit/engine.py; sed -n '2355,2435p' autofit/engine.py; sed -n '2690,2895p' autofit/engine.py; git diff main..HEAD -- CLAUDE.md; cat scripts/fit_termination_scope.py; cat scripts/fit_termination_scope_analyze.py; rg -n 'ANALYZE_JOB_TTL|jitter|2026-09-21|A1|determin' CLAUDE.md app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:

        if sweep % exchange_every == 0:
            for k in range(K - 1):
                swap_propose += 1
                dlog = (betas[k + 1] - betas[k]) * (lls[k] - lls[k + 1])
                if np.log(rng.uniform()) < dlog:
                    thetas[[k, k + 1]] = thetas[[k + 1, k]]
                    lls[[k, k + 1]] = lls[[k + 1, k]]
                    swap_accept += 1

        if sweep >= burn:
            post_samples.append(thetas[-1].copy())
            post_lls.append(float(lls[-1]))
            for k in range(K):
                ll_records[k].append(float(lls[k]))

    # ── Bayes free energy: stepping-stone across the ladder ──
    # log Z(1)/Z(0) = Σ_k log ⟨exp((β_{k+1}−β_k)·loglik)⟩_{β_k}
    def _stepping_stone(sl=slice(None)):
        log_z = 0.0
        for k in range(K - 1):
            d = betas[k + 1] - betas[k]
            lr = d * np.asarray(ll_records[k][sl])
            if lr.size == 0:
                return None
            m = float(np.max(lr))
            log_z += m + float(np.log(np.mean(np.exp(lr - m))))
        return -log_z

    free_energy = _stepping_stone()
    # Split-half MC error proxy (real-data validation 2026-07-03: on U 4f the
    # seed-to-seed F spread exceeded the between-model gap, silently — the
    # estimator needs an in-run error bar).  Correlated draws make this a
    # LOWER bound on the true MC error; consumers must treat close calls as
    # unresolved, not as weak wins.
    n_rec = len(ll_records[0]) if K else 0
    f_a = _stepping_stone(slice(0, n_rec // 2)) if n_rec >= 4 else None
    f_b = _stepping_stone(slice(n_rec // 2, None)) if n_rec >= 4 else None
    fe_split_err = (abs(f_a - f_b) / 2.0
                    if f_a is not None and f_b is not None else None)

    samples = np.asarray(post_samples)
    # posterior noise estimate from the σ-marginal model: σ̂² = RSS/n per
    # sample; report the posterior-median σ̂
    rss_samples = np.exp(-2.0 * np.asarray(post_lls) / n)
    sigma_hat = float(np.median(np.sqrt(rss_samples / n)))

    return {
        "samples": samples,
        "names": list(space.names),
        "free_energy": float(free_energy),
        "free_energy_split_half_error": (float(fe_split_err)
                                         if fe_split_err is not None else None),
        "sigma_hat": sigma_hat,
        "acceptance": (accept / np.maximum(propose, 1)).tolist(),
        "swap_acceptance": swap_accept / max(swap_propose, 1),
        "betas": betas.tolist(),
        "n_post": len(post_samples),
        "ess": _effective_sample_sizes(samples),
    }


def _effective_sample_sizes(samples: np.ndarray) -> list[float]:
    """
    Crude per-parameter effective sample size via the initial-positive-
    sequence truncation of the autocorrelation sum.  Random-walk chains are
    strongly autocorrelated, so credible intervals from few effective
    samples UNDERESTIMATE uncertainty — consumers must check this before
    trusting the CIs (surfaced as an explicit warning in the analysis
    payload).
    """
    if samples.ndim != 2 or len(samples) < 8:
        return []
    n, dim = samples.shape
    out = []
    for j in range(dim):
        col = samples[:, j]
        c = col - col.mean()
        var = float(np.dot(c, c)) / n
        if var <= 0 or float(np.ptp(col)) == 0.0:
            # a free sampled parameter that never moved is a STUCK chain,
            # not a perfectly-converged one (Codex Stage-5 finding #3) —
            # ESS=n here would let a zero-width "credible interval" pass
            # with no warning.  ptp==0 catches the literal never-moved case
            # that FP noise in the mean can disguise as var>0.
            out.append(0.0)
            continue
        tau = 1.0
        for lag in range(1, min(n // 2, 200)):
            rho = float(np.dot(c[:-lag], c[lag:])) / ((n - lag) * var)
            if rho <= 0.0:
                break
            tau += 2.0 * rho
        out.append(float(n / tau))
    return out


_ALLOWED_OPTIONS = {
    "n_replicas", "beta_min", "n_sweeps", "burn_fraction", "exchange_every",
    "rng_seed", "candidate_filter", "ci_level", "noise_floor",
    "seed_replicates",
    "endpoint_avg",
}


class BayesianExchangeMCMethod(PeakFitMethod):
    id = "bayesian_exchange_mc"
    label = "Bayesian (exchange Monte Carlo)"
    requires_grammar = True

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> MethodResult:
        if grammar is None:
            raise ValueError("bayesian_exchange_mc requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown bayesian_exchange_mc options: {sorted(unknown)}")

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        ci = float(opts.pop("ci_level", DEFAULT_CI_LEVEL))
        mc_kwargs = dict(
            n_replicas=int(opts.pop("n_replicas", DEFAULT_N_REPLICAS)),
            beta_min=float(opts.pop("beta_min", DEFAULT_BETA_MIN)),
            n_sweeps=int(opts.pop("n_sweeps", DEFAULT_N_SWEEPS)),
            burn_fraction=float(opts.pop("burn_fraction", DEFAULT_BURN_FRACTION)),
            exchange_every=int(opts.pop("exchange_every", DEFAULT_EXCHANGE_EVERY)),
            rng_seed=int(opts.pop("rng_seed", 0)),
        )
        opts.pop("noise_floor", None)     # accepted for symmetry; unused
        candidates = grammar.candidates
        cand_filter = opts.pop("candidate_filter", None)
        if cand_filter is not None:
            wanted = set(cand_filter)
            candidates = [c for c in candidates if c.name in wanted]

        # Independent seeded evidence replicates (Codex Stage-5 blocker #1,
        # re-check evidence: at reduced budgets a single run can report a
        # confidently-resolved F gap that a different seed flips — the
        # split-half proxy is a LOWER bound and can miss it).  k replicates
        # cost k× runtime; the across-replicate half-range is a genuine
        # independent-run MC error and dominates the split-half bound in the
        # selection warning.  Default 1 = cost-neutral single run.
        seed_replicates = int(opts.pop("seed_replicates", 1))
        if seed_replicates < 1:
            raise ValueError("seed_replicates must be >= 1")

        endpoint_avg = pop_endpoint_avg(opts)
        per_candidate: list[dict] = []
        runs: dict[str, dict] = {}
        for model in candidates:
            bg = _compute_background(x, y, model.background, endpoint_avg=endpoint_avg)
            y_net = y - bg
            try:
                space = _param_space(model, x, y_net)
                run = run_exchange_mc(x, y_net, space, weights=weights, **mc_kwargs)
                rep_fs = [run["free_energy"]]
                for j in range(1, seed_replicates):
                    rep_kwargs = dict(mc_kwargs,
                                      rng_seed=mc_kwargs["rng_seed"] + j)
                    rep_space = _param_space(model, x, y_net)
                    rep = run_exchange_mc(x, y_net, rep_space, weights=weights,
    # data criterion; whether a proposal is accepted must not depend on load.
    base_model = base_report.model
    base_fit = base_report.primary_fit
    aug_model = _augmented_candidate(base_model, spec)

    roi = (float(np.min(x)), float(np.max(x)))
    pr = ProposedPeakReport(
        role=spec.role, detection_windows=list(spec.detection_windows),
        detection_energy=spec.detection_energy, detection_ratio=spec.detection_ratio,
        proposed_center_init=spec.center_init, proposed_fwhm_init=spec.fwhm_init,
        proposed_amplitude_init=spec.amplitude_init, roi_bounds=roi,
    )

    def _fast(reason: str):
        pr.rejection_reason = reason
        return None, pr, "fast_rejected"

    bg = _compute_background(x, y, aug_model.background, endpoint_avg=endpoint_avg)
    try:
        init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
                                             fit_full_window=fit_full_window)
    except Exception as exc:
        return _fast(f"init_params_error: {exc}")

    primary = fit_candidate(x, y, weights, aug_model, initial_params=init,
                            endpoint_avg=endpoint_avg)
    if not primary.converged:
        return _fast("augmented_fit_did_not_converge")
    comp = next((c for c in primary.components if c.slot_role == spec.role), None)
    if comp is None:
        return _fast("proposed_slot_did_not_populate")

    pr.fitted_center = comp.position
    pr.fitted_fwhm = comp.fwhm
    pr.fitted_amplitude = comp.amplitude
    # A peg on the WIDTH cap alone (fwhm@max) is the ordinary physical FWHM
    # ceiling doing its job: the feature is broader than an ordinary
    # component with no known-broad justification.  KEEP such a proposal —
    # modelled at the physical limit — and let it flag the augmented report
    # (unphysical_widths + the fwhm@max boundary hit → CONDITIONAL) rather
    # than rejecting it and leaving the intensity unmodelled.  A SUBSTANTIVE
    # peg (center at a window edge, amplitude at a wall, or fwhm@MIN = an
    # implausibly narrow spike) is spurious → reject.  (Shape endpoints like
    # gl_ratio=0/1 are valid physics, excluded by the shared detector — see
    # _proposed_slot_pegs.)  NOTE this is re-evaluated AFTER the stability
    # best-outcome promotion below, since a deeper minimum can move a param
    # to a wall (Codex fwhm-cap review, run B BLOCKER).
    width_cap_hit = f"{spec.role}:fwhm@max"
    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
    if comp.amplitude <= noise_floor:
        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
    if spurious_hits:
        return _fast(f"proposed slot boundary pegs: {spurious_hits}")

    mask = (x >= comp.position - PROPOSAL_WINDOW_WIDTH) & \
           (x <= comp.position + PROPOSAL_WINDOW_WIDTH)
    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
    if comp.amplitude < PROPOSAL_AMPLITUDE_SNR * local_sigma:
        return _fast(f"amplitude {comp.amplitude:.1f} < "
                     f"{PROPOSAL_AMPLITUDE_SNR:.1f} × local σ ({local_sigma:.2f})")

    aug_bic = compute_bic(primary)
    pr.delta_bic_vs_base = aug_bic - base_report.bic_adjusted
    if not (aug_bic + PROPOSAL_DELTABIC_THRESHOLD < base_report.bic_adjusted):
        return _fast(
            f"fast pre-check: augmented primary BIC {aug_bic:.2f} does not beat "
            f"base BIC* {base_report.bic_adjusted:.2f} by {PROPOSAL_DELTABIC_THRESHOLD:.1f}"
        )

    stability = run_stability_analysis(
        x, y, weights, aug_model, primary,
        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
        fit_full_window=fit_full_window,
        endpoint_avg=endpoint_avg,
    )
    if (stability.best_outcome is not None
            and stability.best_outcome.weighted_chi_sq < primary.weighted_chi_sq):
        primary = stability.best_outcome
        comp = next((c for c in primary.components if c.slot_role == spec.role), comp)
        if comp is not None:
            pr.fitted_center = comp.position
            pr.fitted_fwhm = comp.fwhm
            pr.fitted_amplitude = comp.amplitude
    # Re-evaluate the proposed-slot pegs against the FINAL (possibly
    # stability-promoted) outcome — a deeper minimum can move a param to a
    # wall the initial fit did not touch (Codex fwhm-cap review, run B
    # BLOCKER): a stability-promoted center@min must STILL reject, and a
    # stability-INTRODUCED fwhm@max must set width_capped so the payload
    # matches the emitted decomposition.
    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
    if spurious_hits:
        pr.rejection_reason = (
            f"proposed slot boundary pegs (post-stability): {spurious_hits}")
        return None, pr, "stability_rejected"
    pr.width_capped = pr.boundary_hits == [width_cap_hit]
    sstab = stability.per_slot.get(spec.role)
    if sstab is None:
        pr.rejection_reason = "proposed slot missing from stability output"
        return None, pr, "stability_rejected"
    pr.persistence = sstab.persistence
    if sstab.persistence < PROPOSAL_PERSISTENCE_THRESHOLD:
        pr.rejection_reason = (f"persistence {sstab.persistence:.2f} < "
                               f"{PROPOSAL_PERSISTENCE_THRESHOLD:.2f}")
        return None, pr, "stability_rejected"

    y_fit_aug = (primary.lmfit_result.best_fit + primary.background
                 if primary.lmfit_result is not None else np.zeros_like(y))
    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
    slot_areas = compute_slot_areas(aug_model, primary, x)
    absent = _identify_absent_slots(
        aug_model, stability, slot_areas, primary,
        persistence_threshold=absent_slot_persistence_threshold,
        area_fraction_threshold=absent_slot_area_fraction,
    )
    aug_report = ModelReport(
        model=aug_model, primary_fit=primary, bic=compute_bic(primary),
        stability=stability, residuals=residuals,
        plausibility=PlausibilityFlags(
            boundary_hits=list(primary.boundary_hits),
            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
            orphan_peaks=stability.orphan_rate > 0.1,
        ),
        absent_slots=absent, augmented_from=base_model.name,
    )

    delta = aug_report.bic_adjusted - base_report.bic_adjusted
    pr.delta_bic_vs_base = delta
    if not (delta < -PROPOSAL_DELTABIC_THRESHOLD):
        pr.rejection_reason = (f"ΔBIC* = {delta:+.2f} does not beat "
                               f"-{PROPOSAL_DELTABIC_THRESHOLD:.1f} improvement threshold")
        return None, pr, "stability_rejected"

    lo, hi = roi
    pr.near_roi_endpoint = bool(
        abs(comp.position - lo) <= PROPOSAL_ENDPOINT_WARNING_BE
        or abs(comp.position - hi) <= PROPOSAL_ENDPOINT_WARNING_BE
    )
    pr.accepted = True
    aug_report.proposed_peaks = [pr]
    return aug_report, pr, "accepted"


def _cross_candidate_coincidences(
    attempts: list[tuple[str, ProposedPeakReport]],
) -> list[CoincidenceReport]:
    if not attempts:
        return []
    enriched = [{"base": b, "pr": pr,
                 "be": float(pr.fitted_center if pr.fitted_center is not None
                             else pr.proposed_center_init)}
                for b, pr in attempts]
    enriched.sort(key=lambda e: e["be"])
    clusters: list[list[dict]] = [[enriched[0]]]
    """
    Refit a boundary-limited candidate with each pegged parameter FIXED at
    the bound it pegged to, so its BIC* uses an honest parameter count (a
    bound-pegged free parameter invalidates the interior-Laplace BIC
    approximation).

    Honesty requirements (Codex re-check blockers/major):
    - the refit must not itself peg any NEW bound — otherwise the
      interior-Laplace comparison is invalid again → return None;
    - a FRESH stability pass runs on the bound-fixed model (the constrained
      parameters stay fixed in every multi-start refit) — no inherited
      figures;
    - NO absent-slot adjustment is applied to the refit: its BIC* uses the
      full varying-parameter count (conservative — errs against promotion).
    """
    import dataclasses

    lm = report.primary_fit.lmfit_result
    if lm is None or not report.plausibility.boundary_hits:
        return None
    params = lm.params.copy()
    fixed: dict[str, float] = {}
    for hit in report.plausibility.boundary_hits:
        try:
            role_param, side = hit.rsplit("@", 1)
            role, pname = role_param.split(":", 1)
        except ValueError:
            continue
        full = _slot_prefix(role) + pname
        par = params.get(full)
        if par is None or not par.vary:
            continue
        val = par.min if side == "min" else par.max
        par.set(value=val, vary=False)
        fixed[full] = float(val)
    if not fixed:
        return None

    outcome = fit_candidate(x, y, weights, report.model, initial_params=params,
                            endpoint_avg=endpoint_avg)
    if not outcome.converged:
        return None
    if outcome.boundary_hits:
        # fixing one wall pushed the fit onto another — still not an
        # interior optimum; no honest BIC* comparison is possible
        return None

    stability = run_stability_analysis(
        x, y, weights, report.model, outcome,
        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
        fixed_param_values=fixed,
        fit_full_window=fit_full_window,
        endpoint_avg=endpoint_avg,
    )
    y_fit = (outcome.lmfit_result.best_fit + outcome.background
             if outcome.lmfit_result is not None else np.zeros_like(y))
    return ModelReport(
        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
        primary_fit=outcome,
        bic=compute_bic(outcome),
        stability=stability,
        residuals=compute_residual_diagnostics(
            x, y, y_fit, noise_floor, diagnostic_windows),
        plausibility=PlausibilityFlags(
            boundary_hits=[],
            # width pegs that were FIXED at the cap are still at the physical
            # ceiling — a fixed-at-2.0 ordinary component is no more physical
            # than a pegged one, so keep flagging it
            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
            orphan_peaks=stability.orphan_rate > 0.1,
        ),
        absent_slots=[],                      # conservative full-k BIC*
        boundary_fixed_params=sorted(fixed),
        # carry the proposal lineage forward so a width-capped proposal
        # promoted via decisive-override keeps its width_capped/proposed_peaks
        # record on the winner row (Codex fwhm-cap review, run A MINOR)
        proposed_peaks=list(report.proposed_peaks),
        augmented_from=report.augmented_from,
    )


    else:
        augment_roles = set()

    reports: list[ModelReport] = []
    non_converged: list[tuple[CandidateModel, FitOutcome]] = []
    proposal_attempts: list[tuple[str, ProposedPeakReport]] = []
    timings: list[ProposalPassTiming] = []
    n_cand = len(candidates)
    n_evaluated = 0
    analysis_truncated = False

    # ── Unit F3: screen phase (only for candidate sets larger than the
    #    deep-evaluation budget — every existing gate/battery path is ≤
    #    SCREEN_TOP_K and unchanged) ─────────────────────────────────────
    screen_record: Optional[list[dict]] = None
    screen_fit: dict[str, FitOutcome] = {}
    if n_cand > SCREEN_TOP_K:
        screen_rows: list[dict] = []
        screened: list[tuple[CandidateModel, FitOutcome, float]] = []
        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
        # which candidates reached the deep phase used to depend on load)
        for idx, model in enumerate(candidates, 1):
            log.info("[screen %2d/%d] %s", idx, n_cand, model.name)
            _report_progress(progress_cb, "screening", idx, n_cand, model.name)
            outcome = fit_candidate(x, y, weights, model,
                                    max_nfev=SCREEN_MAX_NFEV,
                                    fit_full_window=fit_full_window,
                                    endpoint_avg=endpoint_avg)
            if outcome.converged:
                bic = compute_bic(outcome)
                screened.append((model, outcome, bic))
                screen_rows.append({"name": model.name, "converged": True,
                                    "bic": float(bic), "selected": False})
            else:
                non_converged.append((model, outcome))
                screen_rows.append({"name": model.name, "converged": False,
                                    "bic": None, "selected": False})
        screened.sort(key=lambda t: t[2])
        selected_models = screened[:SCREEN_TOP_K]
        selected_names = {m.name for m, _, _ in selected_models}
        for row in screen_rows:
            row["selected"] = row["name"] in selected_names
        screen_record = screen_rows
        screen_fit = {m.name: o for m, o, _ in selected_models}
        candidates = [m for m, _, _ in selected_models]
        log.info(
            "compare_models: screen kept %d/%d candidates for deep "
            "evaluation: %s", len(candidates), n_cand,
            [m.name for m in candidates])

    for idx, model in enumerate(candidates, 1):
        # Unit A1: every selected candidate is evaluated — no sweep budget
        n_evaluated += 1
        log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
        _report_progress(progress_cb, "stabilizing", idx, len(candidates),
                         model.name)
        # reuse the screen fit as this candidate's primary (no repeated work)
        primary = screen_fit.get(model.name) or fit_candidate(
            x, y, weights, model, fit_full_window=fit_full_window,
            endpoint_avg=endpoint_avg)
        if not primary.converged:
            non_converged.append((model, primary))
            continue

        stability = run_stability_analysis(
            x, y, weights, model, primary,
            noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
            fit_full_window=fit_full_window,
            endpoint_avg=endpoint_avg,
        )
        # Promote a deeper minimum found by the multi-start pass (see
        # ModelStability.best_outcome).
        if (stability.best_outcome is not None
                and stability.best_outcome.weighted_chi_sq
                < primary.weighted_chi_sq):
            primary = stability.best_outcome
        y_fit = (primary.lmfit_result.best_fit +
                 (primary.background if primary.background is not None else 0.0)
                 if primary.lmfit_result is not None else np.zeros_like(y))
        residuals = compute_residual_diagnostics(x, y, y_fit, noise_floor, diagnostic_windows)
        slot_areas = compute_slot_areas(model, primary, x)
        absent = _identify_absent_slots(
            model, stability, slot_areas, primary,
            persistence_threshold=absent_slot_persistence_threshold,
            area_fraction_threshold=absent_slot_area_fraction,
        )
        base_report = ModelReport(
            model=model, primary_fit=primary, bic=compute_bic(primary),
            stability=stability, residuals=residuals,
            plausibility=PlausibilityFlags(
                boundary_hits=list(primary.boundary_hits),
                unphysical_widths=_unphysical_width_flags(primary.components, model),
                orphan_peaks=stability.orphan_rate > 0.1,
            ),
            absent_slots=absent,
        )

        final_report = base_report
        if enable_proposal_pass:
            # Unit F2: ITERATIVE rounds — each accepted proposal makes the
            # augmented report the new base, detection re-runs on ITS
            # residual, and the next round may accept another peak (up to
            # PROPOSAL_MAX_PER_CANDIDATE total), all under ONE shared
            # per-candidate wall budget.  Gates are unchanged per round.
            counts = dict(n_flagged=0, n_over_cap=0, n_attempted=0,
                          n_fast=0, n_stab=0, n_acc=0)
            timed_out = False                 # unit A1: never set (no pass budget)
            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
            rejected: list[ProposedPeakReport] = []
            current = base_report
            current_y_fit = y_fit
            while counts["n_acc"] < PROPOSAL_MAX_PER_CANDIDATE:
                specs = _detect_residual_proposals(
                    x, y, current_y_fit, noise_floor, current.model,
                    fitted_components=current.primary_fit.components,
                )
                # roles must stay unique across rounds — number this round's
                # specs from one past the HIGHEST existing suffix (never a
                # count: see _next_proposal_index for the collision this
                # avoids)
                base_idx = _next_proposal_index(current.model)
                for j, spec in enumerate(specs):
                    spec.role = f"proposed_peak_{base_idx + j}"
                attempts = specs[:PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE]
                counts["n_flagged"] += len(specs)
                counts["n_over_cap"] += max(len(specs) - len(attempts), 0)
                accepted_this_round = False
                for spec in attempts:
                    counts["n_attempted"] += 1
                    aug_report, pr, outcome = _attempt_proposal(
                        x=x, y=y, weights=weights, base_report=current, spec=spec,
                        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
                        absent_slot_area_fraction=absent_slot_area_fraction,
                        absent_slot_persistence_threshold=absent_slot_persistence_threshold,
                        diagnostic_windows=diagnostic_windows,
                        fit_full_window=fit_full_window,
                        endpoint_avg=endpoint_avg,
                    )
                    proposal_attempts.append((model.name, pr))
                    if outcome == "accepted" and aug_report is not None:
                        counts["n_acc"] += 1
                        # carry earlier rounds' accepted-peak reports forward
                        # (base_report starts with [], so round 1 is a no-op)
                        aug_report.proposed_peaks = (
                            list(current.proposed_peaks) + aug_report.proposed_peaks)
                        current = aug_report
                        pf = current.primary_fit
                        current_y_fit = (
                            pf.lmfit_result.best_fit + pf.background
                            if pf.lmfit_result is not None else np.zeros_like(y))
                        accepted_this_round = True
                        break
                    rejected.append(pr)
                    counts["n_fast" if outcome == "fast_rejected" else "n_stab"] += 1
                if not accepted_this_round:
                    break
            final_report = current
            if rejected:
                # rejected attempts stay visible on whichever report we emit
                final_report.proposed_peaks = final_report.proposed_peaks + rejected
            timings.append(ProposalPassTiming(
                candidate_name=model.name, n_flagged=counts["n_flagged"],
                n_over_cap=counts["n_over_cap"],
                n_attempted=counts["n_attempted"], n_fast_rejected=counts["n_fast"],
                n_stability_rejected=counts["n_stab"], n_accepted=counts["n_acc"],
                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
            ))

        reports.append(final_report)

    result = rank_and_filter(
        reports,
        persistence_threshold=persistence_threshold,
        bic_ambiguity_threshold=bic_ambiguity_threshold,
        allow_last_resort=bool(preseed_specs),
    )
    result = _apply_decisive_override(
        x, y, weights, result,
        persistence_threshold=persistence_threshold,
        diagnostic_windows=diagnostic_windows,
        noise_floor=noise_floor,
        n_refits=n_refits,
        rng_seed=rng_seed,
        fit_full_window=fit_full_window,
        endpoint_avg=endpoint_avg,
    )
    result.non_converged = non_converged
    result.cross_candidate_coincidences = _cross_candidate_coincidences(proposal_attempts)
    result.proposal_pass_timings = timings
    result.analysis_truncated = analysis_truncated
    result.n_candidates_evaluated = n_evaluated
    result.n_candidates_total = n_cand
    # honest augmentation bookkeeping: every detected seed is surfaced;
    # the flag says whether it augmented the grammar families or rides in
    # the detection family only (GRAMMAR_AUGMENT_MAX_SEEDS cap)
    result.preseeded_features = [
        {**s.payload(), "augmented_into_grammar": s.role in augment_roles}
        for s in preseed_specs]
    result.screen = screen_record
    if pool is not None:
        # honesty surface: the full pool payload, with the F2 residual-
        # proposal attempts merged in as the 'residual_gap' source (dedup
        # by the same coincidence tolerance the seeds use)
        pool_payload = pool.payload()
        merge_residual_attempts(
            pool_payload,
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vfbv7IrD' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-b5hsrKBi' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 44eef1b..32ae229 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -226,6 +226,25 @@ workers, at most 4 concurrent fits, the bound the synchronous route had. The syn
 for scripts, tests and the Python twins. Plan:
 `docs/superpowers/plans/2026-09-27-long-fits-start-poll.md`.
 
+### Find Peaks does not read the clock (unit A1, 2026-09-29)
+
+Find Peaks' answer must not depend on server load or on the optimiser's own
+termination flags. No wall-clock budget anywhere in `autofit/engine.py`
+(the 25 s per-candidate, 240 s sweep, proposal and screen budgets are gone —
+on 1-GTA C1s Scan_6 MG2 won or lost on whether its fourth refit started
+before 25 s): every candidate is screened, `SCREEN_TOP_K` are evaluated with
+exactly `n_refits` refits, and work is bounded by counts and evaluation caps.
+A fit's convergence is CERTIFIED (`_certify_minimum`): Trust-Region restarts
+from the end point until one improves chi2 by less than Trust-Region's own
+ftol (scipy's default, no new constant), at most `CERTIFY_MAX_RESTARTS` = 50
+(measured: 2 for most fits, 21 at most on the committed C 1s set); out of
+restarts = not converged. The old warm restart from a failed fit's exit point
+is gone (it met MINPACK's xtol at the stall and reported success). Under
+light and heavy load every structural field of the output is identical; the
+numbers carry Trust-Region's arithmetic jitter (≤ 0.25 meV, ≤ 5e-4 relative
+amplitude, the same idle-to-idle). Plan:
+`docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md`.
+
 ### Timing claims are measured through the public URL
 
 A request from a student reaches the server through Cloudflare, whose edge
"""Scope check: do Run Fit's fits (main, perturbed restarts, scattered starts) end AT a minimum when they report success?
Every lmfit Model.fit call inside /api/fit is intercepted; each result is refined from its end point by a fresh
least_squares fit (same model, data, weights, bounds) and the relative chi2 drop recorded. Usage: OUT.jsonl METHOD"""
import sys, os, io, json, time
sys.path.insert(0, '.')
import numpy as np, lmfit
OUT, METHOD = sys.argv[1], sys.argv[2]
from app import create_app
app = create_app(); cl = app.test_client()
T = json.load(open('/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json'))
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)['id'])
orig = lmfit.Model.fit
calls = []
def fit(self, data, params=None, *a, **k):
    r = orig(self, data, params, *a, **k)
    if not calls or calls[-1] is not None:
        try:
            k2 = {kk: vv for kk, vv in k.items() if kk not in ('method', 'fit_kws', 'max_nfev', 'iter_cb')}
            calls.append(None)                     # refinement below must not be recorded
            ref = orig(self, data, r.params.copy(), *a, method='least_squares', **k2)
            calls.pop()
            calls.append({"method": k.get('method'), "success": bool(r.success), "nfev": int(r.nfev), "nvarys": int(r.nvarys),
                          "chisqr": float(r.chisqr), "refined": float(ref.chisqr), "redchi": float(r.redchi) if r.redchi is not None else None})
        except Exception as e:
            if calls and calls[-1] is None: calls.pop()
            calls.append({"method": k.get('method'), "error": str(e)[:80]})
    return r
lmfit.Model.fit = fit
A, B = (int(v) for v in os.environ.get('SCOPE_SLICE', '0:100000').split(':'))
for t in T[A:B]:
    if t['id'] in done: continue
    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
    r = cl.post("/api/upload", data={"file": (io.BytesIO(csv), "t.csv")}, content_type="multipart/form-data")
    sid = r.get_json()["session_id"]
    bg = t["background"]
    body = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
            "peaks": t["specs"], "fit_method": METHOD, "n_perturb": 3, "n_starts": 3}
    calls.clear(); t0 = time.time()
    resp = cl.post("/api/fit", json=body).get_json() or {}
    st = resp.get("starts") or {}
    with open(OUT, 'a') as f:
        f.write(json.dumps({"id": t["id"], "success": resp.get("success"), "starts_ran": st.get("ran"), "sec": round(time.time() - t0, 1),
                            "calls": [c for c in calls if c is not None]}) + "\n")
import json, sys, glob
sp = 'docs/findings/fit-termination-scope/'
for meth, files in (("Trust-Region (least_squares, page default)", ["scope_tr_a.jsonl", "scope_tr_b.jsonl"]), ("Levenberg-Marquardt (leastsq)", ["scope_lm_a.jsonl", "scope_lm_b.jsonl"])):
    rows = [json.loads(l) for f in files for l in open(sp + f)]
    drop = lambda c: (c["chisqr"] - c["refined"]) / c["chisqr"] if c.get("chisqr") else 0.0
    B = {"returned": [], "restart_ok": [], "start_ok": [], "start_failed_at_min": 0, "start_failed": 0}
    worst = []
    for r in rows:
        calls = [c for c in r["calls"] if "chisqr" in c]
        if not calls: continue
        head = calls[:4]; starts = calls[4:] if r.get("starts_ran") else []
        ok = [c for c in head if c["success"]]
        if r.get("success") and ok:
            ret = min(ok, key=lambda c: c["chisqr"])
            B["returned"].append(drop(ret)); worst.append((drop(ret), r["id"], ret["redchi"], ret["nfev"]))
        B["restart_ok"] += [drop(c) for c in head[1:] if c["success"]]
        for c in starts:
            if c["success"]: B["start_ok"].append(drop(c))
            else:
                B["start_failed"] += 1
                B["start_failed_at_min"] += drop(c) < 1e-6
    def dist(v):
        n = len(v)
        return f"n {n}: drop >1e-6 {sum(d > 1e-6 for d in v)}, >1e-3 {sum(d > 1e-3 for d in v)}, >1% {sum(d > 0.01 for d in v)}, >10% {sum(d > 0.1 for d in v)}"
    print("==", meth, f"({len(rows)} targets)")
    print("  returned fit (what the student gets), flagged success:", dist(B["returned"]))
    print("  perturbed restarts flagged success:                ", dist(B["restart_ok"]))
    print("  scattered starts flagged success:                  ", dist(B["start_ok"]))
    print(f"  scattered starts flagged FAILED: {B['start_failed']}, of which already at a minimum (refine drop < 1e-6): {B['start_failed_at_min']}")
    for d, i, rc, nf in sorted(worst, reverse=True)[:6]:
        print(f"     worst returned: {i}  chi2r {rc:.3f}  nfev {nf}  refine lowers chi2 by {100*d:.2f} %")
app.py:295:_ANALYZE_JOB_TTL_SEC = 3600  # job progress files are short-lived scratch
app.py:538:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
app.py:625:    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
CLAUDE.md:229:### Find Peaks does not read the clock (unit A1, 2026-09-29)
CLAUDE.md:244:numbers carry Trust-Region's arithmetic jitter (≤ 0.25 meV, ≤ 5e-4 relative
CLAUDE.md:246:`docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md`.
CLAUDE.md:442:free parameters as data points (`ValueError`, HTTP 400, "not determined by
CLAUDE.md:449:**Reproducibility (2026-09-21).** Every random draw in `run_fit` — the
CLAUDE.md:496:perturbed restarts start from that jittering solution, and near a basin
CLAUDE.md:504:OWNER DECISION 2026-09-21: ACCEPT AND DISCLOSE; no unit for bit-identity.
CLAUDE.md:510:jitter flips the answer), so the scattered-starts cross-check unit is
CLAUDE.md:512:second thing (a reviewer tried a deterministic perturbation base: identical
CLAUDE.md:521:**Scattered-starts check (step (a) of the 2026-09-21 unit; plan in
CLAUDE.md:522:`docs/superpowers/plans/2026-09-21-scattered-starts-and-unsupported-components.md`).**
CLAUDE.md:632:DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
CLAUDE.md:642:the fit did not determine it — and its centre, width and σ are not reported
CLAUDE.md:830:input is touched. Until 2026-09-21 only the centre was checked (±0.3 eV of
CLAUDE.md:842:KNOWN LIMITS of that check (owner decision 2026-09-21: shipped with them

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -s -q -p no:cacheprovider tests/autofit/test_fit_certificate.py tests/autofit/test_preseed_dominants.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "sed -n '449,519p' CLAUDE.md; sed -n '2355,2435p' autofit/engine.py; sed -n '190,255p' autofit/methods/ic_model_comparison.py; rg -n 'success|least_squares|ftol|calc_covar|max_nfev' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py | tail -65; rg -n 'deadline=|budget_remaining=|CANDIDATE_TIMEOUT_SEC|TOTAL_ANALYSIS_TIMEOUT_SEC|WARM_RESTART_MAX_NFEV|SCREEN_BUDGET_FRACTION' --glob '*.py'; rg -n 'fit_candidate|lmfit_result' autofit/methods/bayesian_exchange_mc.py; sed -n '1,110p' tests/autofit/test_preseed_dominants.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
**Reproducibility (2026-09-21).** Every random draw in `run_fit` — the
`n_perturb` restarts (the page sends 3; ±15 % on every varying parameter)
and the populations of `differential_evolution` and `basinhopping`, which
lmfit otherwise takes from numpy's GLOBAL generator — comes from one seed
that is a pure function of THE NUMBERS THE OPTIMISER IS HANDED
(`_request_seed`: SHA-256 of the energies, counts and the COMPUTED
background curve as little-endian float64, plus the canonical JSON of each
component's lineshape, each lmfit parameter's effective role — a
constrained one is its expression, a fixed one its value, a free one its
value and bounds — the method, solver options and `n_perturb`; tag
`xps-fit-seed-v1`). Settings are hashed by their EFFECT, never as sent, so
nothing the fit ignores can change the draws: a peak's name or colour, the
`fix_gl_ratio` the page still sends for a Gaussian, stale shape parameters
kept after a shape switch, the `endpoint_avg` a linear background does not
use, bounds of a fixed parameter, start values a link overrides, anchor
order, and the peaks' internal ids (parameter names and constraint
references are hashed by component POSITION: the page never reuses an id,
so a model rebuilt after deleting a peak would otherwise fit differently)
(in review each such no-op edit moved an area fraction by 15–45 pp
while the request was hashed as sent). It is a seed,
not an identity (32 bits collide; never a cache key). The response reports
it as `random_seed`; a caller's `fit_kws.fit_kws.seed` (integer in
[0, 2³²)) replaces it and is consumed, never forwarded to a solver.
`run_fit` itself accepts only the five supported methods, case-folded
(`_FIT_METHODS`): `/api/analyze` forwards `options.fit_method` without the
route's allowlist, and lmfit's `ampgo`, `dual_annealing`, … would draw
from the global generator. The seed value and the draws `run_fit` actually
makes (observed through Levenberg-Marquardt) are pinned by tests; numpy does not promise the same `default_rng` stream across
versions, so a failing pin after an upgrade is a release note ("saved
projects regenerate differently"), not something to re-pin silently.

What seeding buys and what it does not. "Identical request" means the same
data, model START values and settings — after a fit the page holds the
fitted values, so a second press is a different request; re-loading a
saved project and pressing Run Fit is the repeatable case. Measured on the
202 committed targets × 5 presses of the identical request, before → after:
Levenberg-Marquardt byte-identical on 145 → 202 targets;
Trust-Region on 51 → 145, area fractions moving by more than 1 pp between
presses on 8 → 0 targets, by more than 0.01 pp on 14 → 2 (worst 0.30 pp,
one U 4f scan where two presses in five land in a neighbouring minimum). Levenberg-Marquardt (MINPACK) and Nelder-Mead are
byte-identical. Trust-Region, the default, is NOT and cannot be made so by
seeding: the BLAS dot product (Apple Accelerate on the i9) rounds one unit
in the last place differently depending on where its argument sits in
memory (`w.dot(w)` gives two values over 16 alignments, `np.sum(w*w)`
one), `norm` inside scipy's `_lsq/trf.py` is the first call to return
different output for identical input, and the iteration amplifies that to
~1e-4 relative in an area at its stopping tolerance of 1e-8. Worse, the
perturbed restarts start from that jittering solution, and near a basin
boundary 1e-5 in a start is enough to send a restart into another minimum:
on the lab's targets that happened once (0.30 pp), but on a synthetic
five-component model two presses of the seeded request differed by 29 pp
(`tests/test_fit_reproducibility.py` docstring). Do not patch scipy
internals for this, and do not tighten the tolerance: ftol = xtol = gtol =
1e-12 on the same 202 × 5 gave FEWER byte-identical targets (123 vs 146)
and made two targets that converge today abort on the evaluation budget.
OWNER DECISION 2026-09-21: ACCEPT AND DISCLOSE; no unit for bit-identity.
Byte-identity is a software property, not a scientific one. The scientific
requirement — reloading a saved project and pressing Run Fit regenerates
the figure within meaningful precision — is met (2 of 202 targets move
more than 0.01 pp, worst 0.30 pp). The 29 pp synthetic case is the SAME
phenomenon as the local-minimum problem (near a basin boundary 1e-4 of
jitter flips the answer), so the scattered-starts cross-check unit is
already the mitigation: it exposes exactly those fits. Do not build a
second thing (a reviewer tried a deterministic perturbation base: identical
starts, results still differed; a reproducible-arithmetic BLAS is a large
project with uncertain payoff). Disclosure wording, for docs and the
student note: identical requests now give identical results on real data
in practice; the underlying arithmetic is not bit-reproducible, so a fit
sitting near a boundary between two solutions can still resolve
differently, and that is precisely the situation the multiple-starts check
is designed to surface.
    """
    Refit a boundary-limited candidate with each pegged parameter FIXED at
    the bound it pegged to, so its BIC* uses an honest parameter count (a
    bound-pegged free parameter invalidates the interior-Laplace BIC
    approximation).

    Honesty requirements (Codex re-check blockers/major):
    - the refit must not itself peg any NEW bound — otherwise the
      interior-Laplace comparison is invalid again → return None;
    - a FRESH stability pass runs on the bound-fixed model (the constrained
      parameters stay fixed in every multi-start refit) — no inherited
      figures;
    - NO absent-slot adjustment is applied to the refit: its BIC* uses the
      full varying-parameter count (conservative — errs against promotion).
    """
    import dataclasses

    lm = report.primary_fit.lmfit_result
    if lm is None or not report.plausibility.boundary_hits:
        return None
    params = lm.params.copy()
    fixed: dict[str, float] = {}
    for hit in report.plausibility.boundary_hits:
        try:
            role_param, side = hit.rsplit("@", 1)
            role, pname = role_param.split(":", 1)
        except ValueError:
            continue
        full = _slot_prefix(role) + pname
        par = params.get(full)
        if par is None or not par.vary:
            continue
        val = par.min if side == "min" else par.max
        par.set(value=val, vary=False)
        fixed[full] = float(val)
    if not fixed:
        return None

    outcome = fit_candidate(x, y, weights, report.model, initial_params=params,
                            endpoint_avg=endpoint_avg)
    if not outcome.converged:
        return None
    if outcome.boundary_hits:
        # fixing one wall pushed the fit onto another — still not an
        # interior optimum; no honest BIC* comparison is possible
        return None

    stability = run_stability_analysis(
        x, y, weights, report.model, outcome,
        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
        fixed_param_values=fixed,
        fit_full_window=fit_full_window,
        endpoint_avg=endpoint_avg,
    )
    y_fit = (outcome.lmfit_result.best_fit + outcome.background
             if outcome.lmfit_result is not None else np.zeros_like(y))
    return ModelReport(
        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
        primary_fit=outcome,
        bic=compute_bic(outcome),
        stability=stability,
        residuals=compute_residual_diagnostics(
            x, y, y_fit, noise_floor, diagnostic_windows),
        plausibility=PlausibilityFlags(
            boundary_hits=[],
            # width pegs that were FIXED at the cap are still at the physical
            # ceiling — a fixed-at-2.0 ordinary component is no more physical
            # than a pegged one, so keep flagging it
            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
            orphan_peaks=stability.orphan_rate > 0.1,
        ),
        absent_slots=[],                      # conservative full-k BIC*
        boundary_fixed_params=sorted(fixed),
        # carry the proposal lineage forward so a width-capped proposal
        # promoted via decisive-override keeps its width_capped/proposed_peaks
        # record on the winner row (Codex fwhm-cap review, run A MINOR)
        proposed_peaks=list(report.proposed_peaks),
        augmented_from=report.augmented_from,
    )


                "n_non_converged": len(result.non_converged),
                "analysis_truncated": result.analysis_truncated,
                "n_candidates_evaluated": result.n_candidates_evaluated,
                "n_candidates_total": result.n_candidates_total,
            },
            message=(message + (
                f" WARNING: filtered candidate "
                f"{result.filtered_dominant_alternative['name']} beats this "
                f"winner by ΔBIC* "
                f"{result.filtered_dominant_alternative['delta_bic_vs_winner']:.1f} "
                "but did not survive filtering "
                f"({result.filtered_dominant_alternative['filter_reason']})"
                if result.filtered_dominant_alternative else "")
                + (f" {truncation_note}." if truncation_note else "")),
        )


def _peaks_from_report(
    report: ModelReport, exclude_roles: frozenset | set = frozenset()
) -> list[dict]:
    """Winning decomposition as backend-spec-shaped dicts."""
    peaks = []
    lm = report.primary_fit.lmfit_result
    for slot in report.model.slots:
        if slot.role in exclude_roles:
            continue
        comp = next((c for c in report.primary_fit.components
                     if c.slot_role == slot.role), None)
        if comp is None:
            continue
        rec = {
            "role": slot.role,
            "region": slot.region,
            "phase_id": slot.phase_id,
            "shape": BACKEND_SHAPE[slot.line_shape],
            "center": comp.position,
            "fwhm": comp.fwhm,
            "amplitude": comp.amplitude,
            **comp.shape_params,
        }
        if lm is not None:
            prefix = _slot_prefix(slot.role)
            stderr = {}
            for pname, par in lm.params.items():
                if pname.startswith(prefix) and par.stderr is not None:
                    stderr[pname[len(prefix):]] = float(par.stderr)
            if stderr:
                rec["stderr"] = stderr
        peaks.append(rec)
    return peaks


def build_analysis_record(
    grammar: CandidateGrammar, result: ComparisonResult
) -> dict:
    """
    The tab-level ``analysis`` payload — REGENERABLE ONLY (spec §1: older
    clients drop it on resave; no human decisions may live here).
    """
    filtered_reason = {r.model.name: why for r, why in result.filtered_out}
    survivor_rank = {r.model.name: i + 1 for i, r in enumerate(result.survivors)}

    candidates = []
    for r in result.reports:
        name = r.model.name
        candidates.append({
1534:        self.set_max_nfev(max_nfev, 2000*(result.nvarys+1))
1543:        least_squares_kws = dict(jac='2-point', method='trf', ftol=1e-08,
1547:                                 jac_sparsity=None, max_nfev=2*self.max_nfev,
1550:        least_squares_kws.update(self.kws)
1551:        least_squares_kws.update(kws)
1553:        if least_squares_kws.get('Dfun', None) is not None:
1554:            least_squares_kws['jac'] = least_squares_kws.pop('Dfun')
1556:        if callable(least_squares_kws['jac']):
1557:            self.jacfcn = least_squares_kws['jac']
1558:            least_squares_kws['jac'] = self._jacobian
1560:        least_squares_kws['kwargs'].update({'apply_bounds_transformation': False})
1561:        result.call_kws = least_squares_kws
1564:            ret = least_squares(self.__residual, start_vals,
1566:                                **least_squares_kws)
1572:        # Note: scipy.optimize.least_squares is actually returning the
1578:        elif result.nfev > self.max_nfev-5:
1588:                    outattr = 'least_squares_nfev'
1609:    def leastsq(self, params=None, max_nfev=None, **kws):
1624:        max_nfev : int or None, optional
1649:        self.set_max_nfev(max_nfev, 2000*(result.nvarys+1))
1651:        lskws = dict(Dfun=None, full_output=1, col_deriv=0, ftol=1.5e-8,
1652:                     xtol=1.5e-8, gtol=0.0, maxfev=2*self.max_nfev,
1687:        if result.nfev >= self.max_nfev:
1688:            result.nfev = self.max_nfev - 1
1698:        result.success = ier in [1, 2, 3, 4]
1712:        # self.errorbars = error bars were successfully estimated
1726:    def basinhopping(self, params=None, max_nfev=None, **kws):
1739:        max_nfev : int or None, optional
1757:        self.set_max_nfev(max_nfev, 200000*(result.nvarys+1))
1761:                                disp=False, niter_success=None, seed=None,
1778:        elif result.nfev > self.max_nfev-5:
1786:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
1795:    def brute(self, params=None, Ns=20, keep=50, workers=1, max_nfev=None):
1833:        max_nfev : int or None, optional
1884:        self.set_max_nfev(max_nfev, 200000*(result.nvarys+1))
1961:        elif result.nfev > self.max_nfev-5:
1969:    def ampgo(self, params=None, max_nfev=None, **kws):
1981:        max_nfev : int, optional
2004:                    `max_nfev` instead).
2059:        self.set_max_nfev(max_nfev, 200000*(result.nvarys+1))
2087:        elif result.nfev > self.max_nfev-5:
2095:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2104:    def shgo(self, params=None, max_nfev=None, **kws):
2115:        max_nfev : int or None, optional
2138:        self.set_max_nfev(max_nfev, 200000*(result.nvarys+1))
2158:                if attr in ['success', 'message']:
2165:        elif result.nfev > self.max_nfev-5:
2172:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2180:    def dual_annealing(self, params=None, max_nfev=None, **kws):
2191:        max_nfev : int or None, optional
2212:        self.set_max_nfev(max_nfev, 200000*(result.nvarys+1))
2216:                      maxfun=2*self.max_nfev, seed=None, no_local_search=False,
2237:                if attr in ['success', 'message']:
2244:        elif result.nfev > self.max_nfev-5:
2252:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2269:            - `'least_squares'`: Least-Squares minimization, using Trust
2336:            function = self.least_squares
2475:             calc_covar=True, max_nfev=None, **fit_kws):
2487:        '`least_squares`', the objective function should return an array
2501:        - `'least_squares'`: Least-Squares minimization, using Trust Region Reflective method
2560:    calc_covar : bool, optional
2562:        solvers other than `'leastsq'` and `'least_squares'`. Requires the
2564:    max_nfev : int or None, optional
2608:                           calc_covar=calc_covar, **fit_kws)
2615:                       calc_covar=calc_covar, max_nfev=max_nfev, **fit_kws)
"""
Units F1 (pre-fit out-of-grammar dominant seeding), F2 (iterative proposal
rounds), F3 (two-phase screen→stabilize sweep) — always-on pins.

Motivating evidence: PROGRESS.md "Real multi-environment C 1s — MEASURED
DIAGNOSIS (2026-07-07)".  The real spectra stay local-only (privacy rail);
`multi_env_low_be_dominant_case` in stress_cases.py is the committed
ground-truth stand-in for the class.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    STEP,
    _cand,
    _grammar,
    _grid,
    _linear_bg,
    _noisy,
    _pv,
    _slot,
    multi_env_low_be_dominant_case,
)

import autofit.engine as eng  # noqa: E402
from autofit.methods import get_method  # noqa: E402

ETA = 0.30
IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(case, **extra):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options={**IC_OPTS, **extra})


def _covered_spectrum(seed=11):
    """Both features inside grammar windows — detection must return []."""
    x = _grid()
    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
             {"center": 199.5, "fwhm": 1.4, "height": 4000.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    cands = [_cand("P2", [_slot("main_a", (195.5, 197.5)),
                          _slot("comp_b", (198.5, 200.5))])]
    return x, y, _grammar(cands)


# ── F1: detection ──────────────────────────────────────────────────────────

def test_no_preseed_on_covered_spectrum():
    """Grammar-covered spectra must run byte-identically: zero detections,
    no '+preseed' candidates, empty preseeded_features."""
    x, y, grammar = _covered_spectrum()
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    specs = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    assert specs == []

    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
    res = _ic(case_like)
    assert res.analysis["preseeded_features"] == []
    assert not any(c["name"].endswith("+preseed")
                   for c in res.analysis["candidates"])


def test_detects_out_of_window_dominant_and_gates_weak_bump():
    """A dominant peak below every window is detected at its position; a
    weak out-of-window bump (below the fraction-of-max gate) is NOT —
    that regime stays the proposal pass's job."""
    x = _grid(186.0, 205.0)
    sig = (_pv(x, 30000.0, 191.0, 1.3, ETA)          # dominant, out-of-window
           + _pv(x, 30000.0 * 0.10, 188.5, 1.2, ETA)  # weak bump, below gate
           + _pv(x, 9000.0, 196.5, 1.2, ETA))         # in-window main
    y = _noisy(sig + _linear_bg(x), 7)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    specs = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    assert len(specs) == 1
    assert specs[0].center_init == pytest.approx(191.0, abs=0.3)
    assert specs[0].role == "preseed_dominant_0"
    # in-window features are never seeded, however large
    assert all(not (195.5 <= s.center_init <= 197.5) for s in specs)


def test_detection_descending_grid_equivalence():
    """Real raw_be grids DESCEND — detection must be order-invariant
    (np.interp-class bug family; the noise-model unit's lesson)."""
    x = _grid(186.0, 205.0)
    sig = (_pv(x, 30000.0, 191.0, 1.3, ETA)
           + _pv(x, 9000.0, 196.5, 1.2, ETA))
    y = _noisy(sig + _linear_bg(x), 7)
    cands = [_cand("P1", [_slot("main_a", (195.5, 197.5))])]
    grammar = _grammar(cands)
    bg = eng._compute_background(x, y, grammar.candidates[0].background)
    asc = eng.detect_out_of_grammar_dominants(
        x, y, bg, grammar.candidates, dict(grammar.diagnostic_windows))
    desc = eng.detect_out_of_grammar_dominants(
        x[::-1], y[::-1], bg[::-1], grammar.candidates,
        dict(grammar.diagnostic_windows))
    assert len(asc) == len(desc) == 1

 exited 2 in 2226ms:

==================================== ERRORS ====================================
____________ ERROR collecting tests/autofit/test_fit_certificate.py ____________
tests/autofit/test_fit_certificate.py:16: in <module>
    import autofit.engine as eng
autofit/engine.py:38: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism']
___________ ERROR collecting tests/autofit/test_preseed_dominants.py ___________
tests/autofit/test_preseed_dominants.py:19: in <module>
    from stress_cases import (  # noqa: E402
tests/autofit/stress_cases.py:58: in <module>
    from fitting import _SHAPE_FUNCS
fitting.py:35: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism']
=========================== short test summary info ============================
ERROR tests/autofit/test_fit_certificate.py - FileNotFoundError: [Errno 2] No...
ERROR tests/autofit/test_preseed_dominants.py - FileNotFoundError: [Errno 2] ...
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 1.87s

exec
/bin/zsh -lc "rg -n 'time\\.|perf_counter|monotonic|deadline|timeout|budget' autofit --glob '*.py'; sed -n '1510,1610p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '265,340p' autofit/methods/ic_model_comparison.py; rg -n 'Scan_6|MG2|candidate_filter' tests/autofit/test* | head -70; sed -n '870,932p' autofit/engine.py; rg -n 'component.*support|support.*component' autofit app.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
autofit/engine.py:129:# boundary cleanliness; same per-candidate wall budget).  Measured
autofit/engine.py:133:# residual.  fitalg's Iteration B was already capped/timeout-guarded; this
autofit/engine.py:142:# Unit A1 (2026-09-29): NO wall-clock budget anywhere in the sweep. The
autofit/engine.py:143:# per-candidate 25 s, the 240 s sweep, the 60 s / 35 s proposal budgets, the
autofit/engine.py:144:# 15 s minimum-fit budget and the screen's share of the sweep all made Find
autofit/engine.py:216:# grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
autofit/engine.py:217:# never finish inside the then 240 s sweep budget (removed in unit A1; it sat
autofit/engine.py:218:# below the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
autofit/engine.py:1146:    # budget); the denominator of persistence / orphan_rate / convergence_rate.
autofit/engine.py:1173:    deadline. The 25 s per-candidate budget this replaced made persistence
autofit/engine.py:1607:    # Never set since unit A1 (the sweep budget it reported is gone: every
autofit/engine.py:2158:    # Unit A1 (2026-09-29): no wall-clock budget — an attempt either runs its
autofit/engine.py:2677:                    # phase truncates under its wall budget on rich scans
autofit/engine.py:2679:                    # 21/30) — a budget truncation must never be able to
autofit/engine.py:2702:    #    deep-evaluation budget — every existing gate/battery path is ≤
autofit/engine.py:2709:        # Unit A1: EVERY candidate is screened (no wall-clock screen budget —
autofit/engine.py:2741:        # Unit A1: every selected candidate is evaluated — no sweep budget
autofit/engine.py:2793:            # per-candidate wall budget.  Gates are unchanged per round.
autofit/engine.py:2796:            timed_out = False                 # unit A1: never set (no pass budget)
autofit/engine.py:2797:            pass_start = time.perf_counter()  # telemetry only (wall_time_sec)
autofit/engine.py:2855:                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
autofit/noise.py:211:        raise ValueError("x must be strictly monotonic")
autofit/grammar.py:140:    # the DS+G Lorentzian HWHM at the C 1s core-hole lifetime.
autofit/methods/ic_model_comparison.py:81:            "overall time budget was reached"
autofit/methods/bayesian_exchange_mc.py:336:        # re-check evidence: at reduced budgets a single run can report a
autofit/methods/bayesian_exchange_mc.py:424:        # is UNRESOLVED at this sweep budget — surfaced, never silent.
        params : Parameters, optional
            Parameters to use as starting point.
        max_nfev : int or None, optional
            Maximum number of function evaluations. Defaults to
            ``2000*(nvars+1)``, where ``nvars`` is the number of variable
            parameters.
        **kws : dict, optional
            Minimizer options to pass to :scipydoc:`optimize.least_squares`.

        Returns
        -------
        MinimizerResult
            Object containing the optimized parameters and several
            goodness-of-fit statistics.


        .. versionchanged:: 0.9.0
           Return value changed to :class:`MinimizerResult`.

        """
        result = self.prepare_fit(params)
        result.method = 'least_squares'

        replace_none = lambda x, sign: sign*np.inf if x is None else x
        self.set_max_nfev(max_nfev, 2000*(result.nvarys+1))

        start_vals, lower_bounds, upper_bounds = [], [], []
        for vname in result.var_names:
            par = self.params[vname]
            start_vals.append(par.value)
            lower_bounds.append(replace_none(par.min, -1))
            upper_bounds.append(replace_none(par.max, 1))

        least_squares_kws = dict(jac='2-point', method='trf', ftol=1e-08,
                                 xtol=1e-08, gtol=1e-08, x_scale=1.0,
                                 loss='linear', f_scale=1.0, diff_step=None,
                                 tr_solver=None, tr_options={},
                                 jac_sparsity=None, max_nfev=2*self.max_nfev,
                                 verbose=0, kwargs={})

        least_squares_kws.update(self.kws)
        least_squares_kws.update(kws)

        if least_squares_kws.get('Dfun', None) is not None:
            least_squares_kws['jac'] = least_squares_kws.pop('Dfun')

        if callable(least_squares_kws['jac']):
            self.jacfcn = least_squares_kws['jac']
            least_squares_kws['jac'] = self._jacobian

        least_squares_kws['kwargs'].update({'apply_bounds_transformation': False})
        result.call_kws = least_squares_kws

        try:
            ret = least_squares(self.__residual, start_vals,
                                bounds=(lower_bounds, upper_bounds),
                                **least_squares_kws)
            result.residual = ret.fun
        except AbortFitException:
            ret = None
            result.aborted = True

        # Note: scipy.optimize.least_squares is actually returning the
        # "last evaluation", which is not necessarily the "best result"; so we
        # do that here for consistency
        if not result.aborted:
            result.nfev -= 1
            result.residual = self.__residual(ret.x, False)
        elif result.nfev > self.max_nfev-5:
            result.nfev -= 2
            _best = result.last_internal_values
            result.residual = self.__residual(_best, False)
        result._calculate_statistics()

        if not result.aborted:
            for attr in ret:
                outattr = attr
                if attr == 'nfev':
                    outattr = 'least_squares_nfev'
                setattr(result, outattr, ret[attr])

            result.x = np.atleast_1d(result.x)

            # calculate the cov_x and estimate uncertainties/correlations
            try:
                if issparse(ret.jac):
                    hess = (ret.jac.T * ret.jac).toarray()
                elif isinstance(ret.jac, LinearOperator):
                    identity = np.eye(ret.jac.shape[1], dtype=ret.jac.dtype)
                    hess = (ret.jac.T * ret.jac) * identity
                else:
                    hess = np.matmul(ret.jac.T, ret.jac)
                result.covar = np.linalg.inv(hess)
                self._calculate_uncertainties_correlations()
            except LinAlgError:
                pass

        return result

    def leastsq(self, params=None, max_nfev=None, **kws):
        """Use Levenberg-Marquardt minimization to perform a fit.
            "bic_weighted": float(r.bic_weighted),
            "n_eff_lag1": (float(r.n_eff_lag1)
                           if r.n_eff_lag1 is not None else None),
            "survived": name in survivor_rank,
            "rank": survivor_rank.get(name),
            "filter_reason": filtered_reason.get(name),
            "augmented_from": r.augmented_from,
            "boundary_fixed_params": list(r.boundary_fixed_params),
            "absent_slots": [
                {"role": a.role, "persistence": float(a.persistence),
                 "area_fraction": float(a.area_fraction)} for a in r.absent_slots
            ],
            "proposed_peaks": [
                {"role": p.role, "accepted": bool(p.accepted),
                 "fitted_center": p.fitted_center,
                 "fitted_fwhm": p.fitted_fwhm,
                 "width_capped": bool(p.width_capped),
                 "rejection_reason": p.rejection_reason,
                 "near_roi_endpoint": bool(p.near_roi_endpoint)}
                for p in r.proposed_peaks
            ],
            "residual_flags": r.residuals.flagged_windows,
            "unphysical_widths": list(r.plausibility.unphysical_widths),
            "autocorr_flag": bool(r.residuals.autocorr_flag),
            "min_active_persistence": float(r.active_min_persistence),
            "boundary_hits": r.plausibility.boundary_hits,
            # full plausibility surface (Codex Stage-2 re-review finding #3 —
            # the orphan flag was recorded but dropped from the payload)
            "unphysical_widths": r.plausibility.unphysical_widths,
            "orphan_peaks": bool(r.plausibility.orphan_peaks),
            # best-minimum honesty (re-review finding #4): how many of the
            # multi-start fits reproduced the reported minimum's χ² basin
            "best_minimum_basin_support": int(r.stability.best_basin_support),
        })

    import copy

    non_verified = sorted({
        f"{slug}:{e['constant']}"
        for slug, entries in grammar.provenance.items()
        for e in entries if e.get("status") != "VERIFIED"
    })
    return {
        "method": "ic_model_comparison",
        "engine_version": ENGINE_VERSION,
        "regions": list(grammar.regions),
        "phase_ids": list(grammar.phase_ids),
        "resolution_notes": grammar.notes,
        "conditional_tier": bool(result.conditional),
        "conditional_reason": result.conditional_reason,
        # Constants provenance — runtime-visible verification status of every
        # physical constant this fit was built on (never comments-only).
        # Deep-copied so payload consumers can't mutate the shared grammar.
        # SCOPE: region-wide (everything the resolved grammar consumes), not
        # per-candidate — a candidate that omits a slot still lists that
        # slot's constants; per-candidate provenance is logged future work.
        "constants_provenance": copy.deepcopy(grammar.provenance),
        "constants_provenance_scope": "region-wide",
        "uses_conditional_or_unverified_constants": non_verified,
        "candidates": candidates,
        "non_converged": [m.name for m, _ in result.non_converged],
        "ambiguous_pairs": [list(t) for t in result.ambiguous_pairs],
        # unit F1: out-of-grammar dominants every candidate was pre-seeded
        # with (empty = detection found nothing, candidate set unmodified)
        "preseeded_features": result.preseeded_features,
        # candidate-generation layer (2026-07-10): the OVERCOMPLETE,
        # provenance-tagged detection pool — every feature any source
        # (local_max / curvature_shoulder / residual_gap / grammar)
        # proposed, with per-feature gate outcomes and seeding decisions.
        # Features here are candidates the selection layer judged, NOT
        # confirmed peaks.  None when the layer did not run.
        "candidate_pool": result.candidate_pool,
        # unit F3: two-phase sweep record — every candidate's screen outcome
        # when the screen ran (None = classic single-phase path).  Screened-
        # out candidates are visible here, never silently dropped.
        "screen": result.screen,
tests/autofit/test_bayesian_u4f_unresolved_gate.py:47:                 "candidate_filter": ["U1b_mains_satpair_freesep",
tests/autofit/test_bayesian_method.py:125:        options={**OPTS, "candidate_filter": ["K1", "K2"]})
tests/autofit/test_bayesian_method.py:228:                 options={**OPTS, "candidate_filter": ["K2"]})
tests/autofit/test_bayesian_method.py:230:               options={**OPTS, "candidate_filter": ["K2"], "seed_replicates": 1})
tests/autofit/test_bayesian_method.py:237:               options={**OPTS, "candidate_filter": ["K2"], "seed_replicates": 2})
tests/autofit/test_bayesian_method.py:275:               options={**OPTS, "candidate_filter": ["K2"]})
tests/autofit/test_bayesian_method.py:277:               options={**OPTS, "candidate_filter": ["K2"]})
tests/autofit/test_u4f_parity_battery.py:30:# Scan_6, a flat alpha/beta/m valley) wobbles at 1.4e-4 relative across
tests/autofit/test_methods_seam.py:73:        "candidate_filter": ["A1_linked", "AG1_linked", "B2_linked"],
tests/autofit/test_methods_seam.py:122:        "candidate_filter": ["B2_linked"], "enable_proposal_pass": False,
tests/autofit/test_stage2_rereview_findings.py:134:        "candidate_filter": ["A1_linked", "AG1_linked", "B2_linked"],
tests/autofit/test_c1s_parity_gate.py:62:    ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
tests/autofit/test_c1s_parity_gate.py:68:    "MG2_graphAsymGL_aliph_sat_CO_C=O",
tests/autofit/test_c1s_parity_gate.py:76:# log).  Measured mains: Scan_2 4 meV (clean MG2), Scan_6 12 meV (clean
tests/autofit/test_c1s_parity_gate.py:86:# Scan_2/Scan_6 unchanged (0.004–0.014); Scan_8 0.0407 (conditional-tier
tests/autofit/test_c1s_parity_gate.py:122:                 "candidate_filter": GATE_CANDIDATES,
tests/autofit/test_fit_certificate.py:8:18 000 evaluations AT the minimum counted as failed (1-GTA C1s Scan_6)."""
tests/autofit/test_fit_certificate.py:32:    return next(c for c in G.candidates if c.name == "MG2_graphAsymGL_aliph_sat_CO_C=O")
tests/autofit/test_fit_certificate.py:65:    """Scan_7 MG2, stability refit 0's start. The removed warm restart
tests/autofit/test_fit_certificate.py:99:    """The Scan_6 case in general form: an optimiser that runs out of
tests/autofit/test_c1s_mixed_material_class.py:309:                         candidate_filter=["A1_linked"])
    ``max_nfev`` bounds leastsq's own effort per call. lmfit's default
    (200000*(nvars+1), see lmfit.Minimizer) is effectively unbounded: a
    candidate whose params wander to a valid-but-degenerate corner (e.g.
    DS+G's alpha/beta pinned at their bounds — a shape preference, not a
    param error; see _BOUNDARY_EXCLUDED) produces a landscape leastsq can't
    descend, and it spins for tens of thousands of evaluations without
    terminating. Diagnostic run (2026-07-05, Suggest-peaks hang
    investigation) showed a clean bimodal split: converged fits topped out
    at nfev=14890; non-convergent ones started at nfev=21604. This cap sits
    between the two so lmfit's own AbortFitException (caught internally by
    leastsq(), surfacing as result.success=False) cuts off the latter
    deterministically, without clipping legitimate slow-but-converging fits.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)

    bg = _compute_background(x, y, model.background, endpoint_avg=endpoint_avg)
    y_sub = y - bg
    composite = _build_composite_model(model)
    params = initial_params if initial_params is not None else \
        _default_params_from_slots(model, x=x, y_net=y_sub,
                                   fit_full_window=fit_full_window)

    try:
        result = composite.fit(y_sub, params, x=x, weights=weights,
                               method="leastsq", nan_policy="omit",
                               max_nfev=max_nfev)
        # Unit A1 (2026-09-29): convergence is CERTIFIED, not read from the
        # optimiser's flag (_certify_minimum). The old ONE warm restart from a
        # failed fit's exit point is gone: from a stall point MINPACK's restart
        # satisfies xtol in ~30 evaluations and reported success at a
        # non-minimum (8-JT C1s Scan_7: chi2r 37.6 "converged" where
        # least_squares from the same start reaches 5.21).
        result, certified = _certify_minimum(composite, y_sub, result, x, weights, max_nfev)
    except Exception as exc:
        log.debug("fit_candidate failed for %s: %s", model.name, exc)
        return FitOutcome(
            converged=False, components=[], residual_sum_sq=float("inf"),
            weighted_chi_sq=float("inf"),
            n_params=len([q for q in params.values() if q.vary]),
            n_data=len(y_sub), lmfit_result=None, background=bg,
        )

    if not certified:
        # out of restarts (or a non-finite restart): the fit did not reach a
        # minimum — reported as not converged, whatever the optimiser's flag
        log.debug("fit_candidate: %s not certified", model.name)
    unweighted_r = y_sub - result.best_fit
    return FitOutcome(
        converged=bool(certified),
        components=_extract_fitted_components(result, model),
        residual_sum_sq=float(np.sum(unweighted_r ** 2)),
        weighted_chi_sq=float(result.chisqr) if result.chisqr is not None else float("inf"),
        n_params=result.nvarys,
        n_data=len(y_sub),
        lmfit_result=result,
        background=bg,
        boundary_hits=_detect_boundary_hits(result.params, model),
    )


def compute_slot_areas(
autofit/methods/ic_model_comparison.py:150:                    "supports — treat EVERY component as a low-confidence "

exec
/bin/zsh -lc "nl -ba docs/superpowers/plans/2026-09-29-a1-find-peaks-determinism.md | tail -50; nl -ba tests/autofit/test_preseed_dominants.py | sed -n '416,470p'; head -c 2000 docs/findings/fit-termination-scope/scope_tr_a.jsonl; sed -n '120,175p' autofit/methods/ic_model_comparison.py; sed -n '192,220p' app.py; rg -n 'n_perturb|best_result|success' fitting.py | tail -45" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
    49	minimum; "converged" is the right verdict for it now.
    50	
    51	**Restarts needed** (8 committed C 1s scans × the 4 gate candidates,
    52	primaries + all refits, 208 fits): 1: 10, 2: 173, 3: 14, 4: 5, then one each
    53	at 5, 6, 8, 9, 11, 21 (flat valleys). With 5 allowed four real minima went
    54	uncertified (8-JT Scan_5's MG2 and MG3 primaries → AG2 at chi2r 42.5 won); 50
    55	certifies all 208. 75 fits `leastsq` flagged as FAILED were certified (capped
    56	at a minimum — the Scan_6 case), none of 208 left uncertified.
    57	
    58	**Acceptance — Scan_6.** Gate options: MG2 (chi2r 2.03), as main with budgets
    59	off; main under load had given AG2.
    60	
    61	**Acceptance — load.** The page's own request (conductor, C 1s, proposals on,
    62	n_refits 4, endpoint average 3; full grammar, 29–30 candidates screened, 6
    63	deep) on 1-GTA Scan_6 and 8-JT Scan_7, idle, idle again, and with 8 CPU
    64	burners (load average 11):
    65	
    66	| | structural fields (winner, tier, candidate set, filter reasons, persistence, ranks, peak roles) | max Δcentre | max rel Δamplitude | max Δarea % |
    67	|---|---|---|---|---|
    68	| idle vs idle | identical (both scans) | 0.20 meV | 3.9e-4 | 7.6e-4 pp |
    69	| idle vs heavy | identical (both scans) | 0.24 meV | 4.9e-4 | 9.4e-4 pp |
    70	
    71	The residual numeric differences are Trust-Region's arithmetic jitter (the
    72	BLAS alignment effect CLAUDE.md records; owner decision 2026-09-21 accept and
    73	disclose), present idle-to-idle — not load. Find Peaks used only the
    74	byte-reproducible Levenberg-Marquardt before; the certificate's Trust-Region
    75	restarts bring the jitter in. Wall time (page request, idle): main 208–213 s,
    76	A1 236–239 s; under load A1 342–350 s (main would have truncated).
    77	
    78	**Screen interaction (found here).** With every screen fit certified to a
    79	genuine local minimum, the screen now compares honest minima — and MG2's
    80	single screen start on 8-JT Scan_7 lands in a poor one (BIC* 2277, as on main)
    81	while most others improve, so MG2 ranks 19th of 28 and is screened out,
    82	though its deep evaluation reaches the best BIC* of all. Page request: main
    83	MG2 (BIC* 1776.8) vs A1 MG3 (1787.6). Measurement on six more scans: §3.
    84	
    85	## 3. The page's own Find Peaks request: main vs A1 (7 distinct committed C 1s scans, idle)
    86	
    87	4 of 7 winners identical (UCl4 Scan_8, UCl4 Scan_3, 1-GTA Scan, 1-GTA Scan_6 —
    88	the last MG2 on both). 3 differ:
    89	
    90	| scan | main (winner, BIC*) | A1 (winner, BIC*) | why |
    91	|---|---|---|---|
    92	| 8-JT Scan_5 | MG2, 1882.6 | MG3, 1901.5 | MG2 SCREENED OUT on A1 (screen rank 21 of 28) — its single screen start lands in a poor local minimum while the certificate carries most other screen fits to much better ones |
    93	| 8-JT Scan_7 | MG2, 1776.8 | MG3, 1787.6 | the same (MG2 screen rank 19 of 28) |
    94	| 1-GTA Scan_2 | MG3, 1803.9 | MG2, 1816.0 | MG3 deep-evaluated on both with the SAME chi2r 1.388; on main one MG3 slot was "absent" (BIC* drops its parameters) because refits the old flag called non-converged counted as empty; certified, the slot is populated in every refit — no credit. A1 is the honest one here |
    95	
    96	The two screen cases pick a model with a WORSE BIC* than main's. The screen's
    97	single-start ranking is pre-existing; the certificate changes which candidates
    98	it happens to favour. OWNER DECISION (see the report).
   416	                        slots=(slot("main_a"),))
   417	    assert eng._next_proposal_index(m0) == 0
   418	
   419	
   420	def test_no_wall_clock_can_change_the_answer(monkeypatch):
   421	    """Unit A1 (2026-09-29): the sweep, screen, stability and proposal
   422	    budgets were wall-clock and made the answer depend on server load; they
   423	    are gone. A clock that jumps a million seconds on every read must leave
   424	    the result IDENTICAL."""
   425	    x = _grid()
   426	    truth = [{"center": 196.5, "fwhm": 1.2, "height": 9000.0},
   427	             {"center": 201.5, "fwhm": 1.2, "height": 2500.0}]
   428	    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
   429	    y = _noisy(sig + _linear_bg(x), 71)
   430	    grammar = _grammar([_cand("single_main", [_slot("main_a", (195.5, 197.5))])])
   431	
   432	    def run():
   433	        res = get_method("ic_model_comparison").run(x, y, grammar=grammar, options={**IC_OPTS, "enable_preseed": False})
   434	        return res.diagnostics, res.peaks, res.analysis, res.confidence
   435	
   436	    normal = run()
   437	    ticks = {"t": 0.0}
   438	
   439	    def jumpy():
   440	        ticks["t"] += 1.0e6
   441	        return ticks["t"]
   442	    monkeypatch.setattr(eng.time, "perf_counter", jumpy)
   443	    assert run() == normal
   444	
   445	
   446	# ── F3: two-phase sweep ────────────────────────────────────────────────────
   447	
   448	def _many_candidate_grammar(x, y):
   449	    """SCREEN_TOP_K+2 candidates: a ladder of window variants, several of
   450	    which cannot express the data (wrong windows)."""
   451	    good = [
   452	        _cand("G1", [_slot("main_a", (195.5, 197.5))]),
   453	        _cand("G2", [_slot("main_a", (195.5, 197.5)),
   454	                     _slot("comp_b", (198.5, 200.5))]),
   455	    ]
   456	    bad = [
   457	        _cand(f"B{i}", [_slot("main_a", (200.5 + i * 0.2, 202.5 + i * 0.2))])
   458	        for i in range(eng.SCREEN_TOP_K)
   459	    ]
   460	    return _grammar(good + bad)
   461	
   462	
   463	def test_screen_phase_records_and_selects():
   464	    """More candidates than SCREEN_TOP_K → the screen runs, every candidate
   465	    appears in the record (nothing silent), at most TOP_K are selected, and
   466	    the winner is still the structurally right model."""
   467	    x, y, _ = _covered_spectrum(seed=13)
   468	    grammar = _many_candidate_grammar(x, y)
   469	    case_like = type("C", (), {"x": x, "y": y, "grammar": grammar})
   470	    res = _ic(case_like)
{"id": "fba7b6facc1a", "success": true, "starts_ran": true, "sec": 40.1, "calls": [{"method": "least_squares", "success": true, "nfev": 37, "nvarys": 16, "chisqr": 869.3485748364499, "refined": 869.3485741925542, "redchi": 4.96770614192257}, {"method": "least_squares", "success": true, "nfev": 1650, "nvarys": 16, "chisqr": 7505.988666306746, "refined": 1116.7694055236807, "redchi": 42.89136380746712}, {"method": "least_squares", "success": false, "nfev": 34000, "nvarys": 16, "chisqr": 9064.18343161076, "refined": 8325.62260486703, "redchi": 51.79533389491863}, {"method": "least_squares", "success": true, "nfev": 1177, "nvarys": 16, "chisqr": 9200.695153373605, "refined": 4831.6086408819865, "redchi": 52.575400876420595}, {"method": "least_squares", "success": true, "nfev": 763, "nvarys": 16, "chisqr": 869.3486282418917, "refined": 869.3485819613322, "redchi": 4.967706447096524}, {"method": "least_squares", "success": true, "nfev": 846, "nvarys": 16, "chisqr": 869.3488805375207, "refined": 869.3487194154936, "redchi": 4.967707888785832}, {"method": "least_squares", "success": true, "nfev": 367, "nvarys": 16, "chisqr": 869.3485865856838, "refined": 869.348579279998, "redchi": 4.967706209061051}]}
{"id": "adb8e03c67d1", "success": true, "starts_ran": true, "sec": 28.8, "calls": [{"method": "least_squares", "success": true, "nfev": 281, "nvarys": 15, "chisqr": 794.0920983868755, "refined": 794.092097818091, "redchi": 4.61681452550509}, {"method": "least_squares", "success": false, "nfev": 32000, "nvarys": 15, "chisqr": 5132.679641846506, "refined": 4646.076441536832, "redchi": 29.841160708409916}, {"method": "least_squares", "success": true, "nfev": 6693, "nvarys": 15, "chisqr": 3464.478446530354, "refined": 3102.860418240222, "redchi": 20.142316549595083}, {"method": "least_squares", "success": true, "nfev": 240, "nvarys": 15, "chisqr": 9283.00272340597, "refined": 9282.862213841045, "redchi": 53.970946066313786}, {"method": "least_squares", "success": true, "nfev": 42                for c in top.primary_fit.components if c.slot_role == r
            ]
            message += (
                f"DATA-DRIVEN component(s) at {', '.join(centers)} eV "
                "(detected/seeded/proposed, region-unassigned): chemical "
                "assignment requires human review; positions are "
                "data-driven, not literature-anchored. "
            )
        if result.conditional:
            # the conditional banner leads, but must not CLOBBER the
            # data-driven/human-review note (Stage-2: a conditional
            # detection-family winner still needs its assignment caveat)
            if result.conditional_reason == "decisive_override":
                message = (
                    "CONDITIONAL result (decisive_override): clean candidates "
                    "exist but a bound-fixed refit of a constraint-limited "
                    f"candidate dominates them — winner {top.model.name} with "
                    f"parameters fixed at bounds: {top.boundary_fixed_params}; "
                    "clean alternatives retained in the ranking "
                    "(see analysis.candidates). "
                ) + message
            elif result.conditional_reason == "unstable_last_resort":
                message = (
                    "UNSTABLE result (last resort): NO candidate passed any "
                    "selection tier — component identities are NOT stable "
                    "across refits (min persistence "
                    f"{top.active_min_persistence:.2f}, orphan rate "
                    f"{top.stability.orphan_rate:.2f}).  Showing the best "
                    f"CONVERGED model ({top.model.name}, χ²ᵣ "
                    f"{top.reduced_chi_sq:.1f}) so you can see what the data "
                    "supports — treat EVERY component as a low-confidence "
                    "suggestion; the data may not distinguish one broad "
                    "feature from several overlapping ones here. "
                ) + message
            else:
                message = (
                    "CONDITIONAL result (no_clean_survivor): no candidate "
                    "passed plausibility cleanly; ranking the stable-but-"
                    f"boundary-limited tier — winner {top.model.name} has "
                    f"constraint violations {top.plausibility.boundary_hits} "
                    "(see analysis.candidates). "
                ) + message
        if top.plausibility.unphysical_widths:
            message += (
                " LOW CONFIDENCE — width(s) held at the ordinary physical "
                f"FWHM cap ({', '.join(top.plausibility.unphysical_widths)}): "
                "the data wants a broader component than an ordinary core line "
                "physically has, but no known-broad class (satellite / plasmon "
                "/ loss) is assigned here. The width is capped at the physical "
                "limit rather than silently widened; a human should identify "
                "the feature (or justify a wider width) before trusting it."
            )
        return MethodResult(
            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
            confidence=confidence,
            diagnostics={

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _json_sanitize(obj):
    """Defensive numpy→native + non-finite→None conversion for
    /api/analyze payloads: a stray np scalar must not 500 the route, and
    inf/NaN (e.g. BIC of a degenerate fit) must not emit non-standard JSON
    that browsers refuse to parse."""
    if isinstance(obj, dict):
        return {str(k): _json_sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_sanitize(v) for v in obj]
    if isinstance(obj, np.generic):
        obj = obj.item()
    if isinstance(obj, np.ndarray):
        return [_json_sanitize(v) for v in obj.tolist()]
    if isinstance(obj, float) and not np.isfinite(obj):
        return None
    return obj


def _session_path(session_id: str, upload_folder: str) -> Path:
    return Path(upload_folder) / f"{session_id}.npz"


def _load_session(session_id: str, upload_folder: str) -> tuple[np.ndarray, np.ndarray]:
    """Load energy and counts arrays from a session file."""
1097:    reported as bounds) and ``run_fit`` does not call it a success.
1130:    if refined.success:
1141:    peak in a wide box it can converge, "successfully", with the component
1158:    if not local.success:
1161:    if searched.box_unverified or not searched.success or local.chisqr < searched.chisqr:
1172:# lmfit 1.3 sets MinimizerResult.success = True before minimising and its
1195:        if refined.success:
1201:        found.success = False
1211:    if local.success and (not candidate.success or local.chisqr < candidate.chisqr):
1233:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
1238:    solver options and ``n_perturb``.
1277:                       "n_perturb": n_perturb})
1391:        if not trial.success or trial.redchi is None or not np.isfinite(trial.redchi):
1495:    if not refit.success or getattr(refit, "box_unverified", False):
1526:            "refit_converged": bool(refit.success)}
1542:    n_perturb: int = 0,
1565:                    individual_peaks, statistics, charge_shift_applied, success
1739:            fit_kws=fit_kws, n_perturb=n_perturb)
1815:        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
1816:                  result.success, result.nfev, result.message)
1827:    # starts check excludes it — and with the page's n_perturb 3 they
1831:    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
1832:        best_result = result
1836:        for attempt in range(n_perturb):
1857:                          attempt + 1, n_perturb, trial_redchi, best_redchi)
1862:                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
1863:                if trial.success and trial_rank < best_rank:
1864:                    best_result = trial
1868:                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
1871:        if best_result is not result:
1874:            result = best_result
1884:        elif not result.success:
1898:        if not result.success:
2021:    success, message = result.success, result.message
2026:        success = False
2033:        "success": success,

codex
The three reported winner changes have plausible explanations: certification changes the single-start screen ranking in two cases, and removes an absent-slot credit caused by failed refits in the third. I haven’t found a violation of the accepted certificate rule. The clock test uses only one candidate, though, so it never exercises screening. I’m working around test-runner temporary-file probes while keeping the review read-only.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\",\"-q\",\"-p\",\"no:cacheprovider\",\"tests/autofit/test_fit_certificate.py\",\"tests/autofit/test_preseed_dominants.py\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python scripts/fit_termination_scope_analyze.py; sed -n '1830,1908p' fitting.py; sed -n '1,175p' tests/autofit/test_c1s_parity_gate.py; rg --files tests/autofit | rg 'stability|bound|engine|certificate|proposal|stage2'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
== Trust-Region (least_squares, page default) (202 targets)
  returned fit (what the student gets), flagged success: n 202: drop >1e-6 8, >1e-3 5, >1% 2, >10% 0
  perturbed restarts flagged success:                 n 498: drop >1e-6 220, >1e-3 186, >1% 173, >10% 162
  scattered starts flagged success:                   n 532: drop >1e-6 78, >1e-3 52, >1% 45, >10% 29
  scattered starts flagged FAILED: 2, of which already at a minimum (refine drop < 1e-6): 0
     worst returned: b8082a8d3a48  chi2r 2.636  nfev 161  refine lowers chi2 by 5.72 %
     worst returned: 6d5a6bd78f91  chi2r 4.734  nfev 42  refine lowers chi2 by 3.81 %
     worst returned: 1f8ceab0cf5a  chi2r 19.040  nfev 2105  refine lowers chi2 by 0.39 %
     worst returned: 975e736e57d1  chi2r 8.825  nfev 34  refine lowers chi2 by 0.12 %
     worst returned: 0e8d6d5af1f4  chi2r 6.179  nfev 72  refine lowers chi2 by 0.11 %
     worst returned: a29a6e44640b  chi2r 14.456  nfev 564  refine lowers chi2 by 0.00 %
== Levenberg-Marquardt (leastsq) (202 targets)
  returned fit (what the student gets), flagged success: n 196: drop >1e-6 32, >1e-3 10, >1% 5, >10% 1
  perturbed restarts flagged success:                 n 576: drop >1e-6 522, >1e-3 367, >1% 292, >10% 198
  scattered starts flagged success:                   n 480: drop >1e-6 94, >1e-3 53, >1% 36, >10% 17
  scattered starts flagged FAILED: 36, of which already at a minimum (refine drop < 1e-6): 1
     worst returned: 7205f2094254  chi2r 21.020  nfev 7202  refine lowers chi2 by 26.40 %
     worst returned: 66f258ea2c39  chi2r 1.731  nfev 511  refine lowers chi2 by 4.45 %
     worst returned: 574ece1ffb18  chi2r 7.458  nfev 26  refine lowers chi2 by 1.87 %
     worst returned: 18a1cbf4dbac  chi2r 2.326  nfev 308  refine lowers chi2 by 1.45 %
     worst returned: 0e8d6d5af1f4  chi2r 6.258  nfev 25  refine lowers chi2 by 1.26 %
     worst returned: 3081b83af679  chi2r 4.308  nfev 3706  refine lowers chi2 by 0.56 %
    # 96 s, max 256 s, and chi2r identical to 1e-8 on all 16).
    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
        best_result = result
        best_redchi = result.redchi if result.redchi is not None else float('inf')
        rng = perturb_rng

        for attempt in range(n_perturb):
            perturbed_params = result.params.copy()
            for pname, par in perturbed_params.items():
                if par.vary and par.value != 0:
                    # Perturb by ±15% random
                    scale = 1.0 + rng.uniform(-0.15, 0.15)
                    new_val = par.value * scale
                    # Respect bounds
                    if np.isfinite(par.min):
                        new_val = max(new_val, par.min)
                    if np.isfinite(par.max):
                        new_val = min(new_val, par.max)
                    perturbed_params[pname].set(value=new_val)
                elif par.vary and par.value == 0:
                    # For zero-valued params, add small absolute perturbation
                    perturbed_params[pname].set(value=rng.uniform(0.001, 0.05))

            try:
                trial = fit_once(perturbed_params)
                trial_redchi = trial.redchi if trial.redchi is not None else float('inf')
                log.debug("  PERTURB %d/%d  redchi=%.4f  (best=%.4f)",
                          attempt + 1, n_perturb, trial_redchi, best_redchi)
                # A candidate whose search box was never cleared by its
                # refinement (differential evolution only) does not displace
                # one that was; for every other method both flags are False.
                trial_rank = (getattr(trial, "box_unverified", False), trial_redchi)
                best_rank = (getattr(best_result, "box_unverified", False), best_redchi)
                if trial.success and trial_rank < best_rank:
                    best_result = trial
                    best_redchi = trial_redchi
                    log.debug("  *** New best found! redchi improved to %.4f", best_redchi)
            except Exception:
                log.debug("  PERTURB %d/%d  failed (exception)", attempt + 1, n_perturb)
                continue

        if best_result is not result:
            log.debug("═══ PERTURB IMPROVED FIT ═══  redchi: %.4f → %.4f",
                      result.redchi, best_redchi)
            result = best_result

    # ── Scattered starts (never changes `result`) ────────────────────────────
    starts = None
    if n_starts:
        n_unlinked = sum(1 for spec in peak_specs if spec.get("constrain_to") is None)
        if kws.get("method") not in _STARTS_METHODS:
            starts = {"ran": False, "reason": "method"}          # a global method already searches
        elif n_unlinked < 2:
            starts = {"ran": False, "reason": "single_component"}
        elif not result.success:
            starts = {"ran": False, "reason": "fit_not_converged"}
        else:
            try:
                starts = _scattered_starts(int(n_starts), fit_once, composite_model, all_params, result,
                                           peak_specs, x, starts_rng)
            except Exception as exc:                              # the check must never cost the student the fit
                log.exception("scattered starts failed")
                starts = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}

    # ── "Is this component required?" (never changes `result`) ─────────────
    required = None
    if require_component is not None:
        rprefix = f"p{require_component}_"
        if not result.success:
            required = {"ran": False, "reason": "fit_not_converged"}
        else:
            try:
                # remove the component and everything linked to it, transitively
                master_of = {str(sp["id"]): sp.get("constrain_to") for sp in peak_specs}
                removed = {str(require_component)}
                grew = True
                while grew:
                    grew = False
                    for pid, master in master_of.items():
"""
Stage-2 C 1s parity gate (spec §0/§3.1): the resolver + IC engine must
reproduce the expert C 1s reference fits within tolerance.

Parity is defined on what the grammar and the expert fits AGREE on
physically — not peak-by-peak equality, because the expert fits use freer
width conventions than the grammar caps (adventitious FWHM up to 2.66 eV
vs the ADJUDICATED uniform 2.0 eV cap — adjudication-decisions.md #5,
2026-07-03; the cap is the ruling, so exact width parity with the broadest
expert components is not expressible by construction).

Gate assertions per anchor spectrum:
1. the engine finds >= 1 surviving candidate (no forced answer, but the
   anchors are good-quality spectra — zero survivors means the grammar or
   pipeline regressed);
2. the winner's graphitic main lands within MAIN_CENTER_TOL of the expert
   graphite peak;
3. the winner includes the π→π* satellite within SATELLITE_TOL of the
   expert satellite;
4. envelope-level agreement: R-factor between the engine winner's envelope
   and the expert's saved fittedY below ENVELOPE_R_TOL.

Runtime: even reduced (3 candidates, 4 refits, proposal pass off) this takes
several minutes per anchor, so it is gated behind RUN_AUTOFIT_GATE=1 — run it
at stage checkpoints and after grammar/engine changes:

    RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_c1s_parity_gate.py

The always-on fast regression net is tests/autofit/test_c1s_parity_battery.py;
the FULL 25-candidate calibration is scripts/run_c1s_full_calibration.py.
"""

import os

import numpy as np
import pytest

if os.environ.get("RUN_AUTOFIT_GATE") != "1":
    # LOUD skip (Codex Stage-2 finding #8): this is a REQUIRED Stage-2 gate.
    # A default run does not enforce it — the always-on parity net is the
    # characterization battery.  Run this gate at every stage checkpoint and
    # after any grammar/engine change:  RUN_AUTOFIT_GATE=1 pytest <this file>
    pytest.skip(
        "SKIPPING REQUIRED STAGE GATE (C 1s parity) — slow; set "
        "RUN_AUTOFIT_GATE=1 to enforce. Do not treat a run without it as a "
        "full Stage-2 verification.",
        allow_module_level=True,
    )

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.parity import evaluate_model
from autofit.reference import load_reference_fits
from fitting import shirley_background

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")

ANCHORS = [
    ("UCl4_on_graphite.proj.zip", "C1s Scan_8"),
    ("8-JT Graphite.proj.zip", "C1s Scan_2"),
    ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
]

# Reduced representative candidate set: the MG expert-structure family, the
# AG lab-practice family, and a Biesinger-convention A competitor.
GATE_CANDIDATES = [
    "MG2_graphAsymGL_aliph_sat_CO_C=O",
    "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O",
    "AG2_linked",
    "A2_linked",
]

# Calibrated 2026-07-03; RE-calibrated 2026-07-04 under the adjudicated
# uniform 2.0 eV contamination cap (see PROGRESS.md parity-gate calibration
# log).  Measured mains: Scan_2 4 meV (clean MG2), Scan_6 12 meV (clean
# AG2), Scan_8 54 meV — the UCl4-composite anchor's expert adventitious
# widths (median 2.08 eV) exceed the cap, so its MG/AG candidates go
# boundary-limited/unstable and the winner drops to the conditional
# no_clean_survivor tier (A2_linked).  That anchor's degradation is the
# adjudicated convention meeting data that prefers wider components —
# expected, documented, not silently forced.
MAIN_CENTER_TOL_EV = 0.08
SATELLITE_TOL_EV = 0.5
# Measured domain envelope R 2026-07-04 under the adjudicated cap:
# Scan_2/Scan_6 unchanged (0.004–0.014); Scan_8 0.0407 (conditional-tier
# winner — same cap-vs-data cause as the main-center recalibration above).
ENVELOPE_R_TOL = 0.05     # Σ|engine−expert| / Σ|expert|, BE ≥ ENVELOPE_DOMAIN_MIN
# The expert fits model a low-BE 'Unknown' (~283.4 eV) that sits outside every
# grammar window (PROGRESS.md discrepancy #6 — proposal-pass territory, which
# the gate disables for runtime).  Envelope parity is asserted on the
# grammar's domain.
ENVELOPE_DOMAIN_MIN = 284.0

GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")


def _anchor(project, name):
    path = os.path.join(DATA, project)
    rf = next(r for r in load_reference_fits(path) if r.name == name)
    return rf


@pytest.fixture(scope="module")
def grammar():
    return resolve([GRAPHITE], "C 1s")


@pytest.mark.parametrize("project,name", ANCHORS,
                         ids=[f"{p}::{n}" for p, n in ANCHORS])
def test_c1s_parity_gate(grammar, project, name):
    rf = _anchor(project, name)
    expert_by_name = { (p.get("name") or "").lower(): p for p in rf.peaks }
    expert_graphite = next(v for k, v in expert_by_name.items() if "graphit" in k)
    expert_satellite = next((v for k, v in expert_by_name.items()
                             if "satellite" in k or "π" in k), None)

    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar,
        options={"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
                 "candidate_filter": GATE_CANDIDATES,
                 "enable_proposal_pass": False},
    )

    # (1) a survivor exists — clean tier preferred, conditional tier accepted
    # WITH its violations surfaced (two-tier semantics; on these composite
    # samples some lit-convention constraint typically binds somewhere)
    assert res.success, (
        f"{name}: no surviving candidate — {res.message}\n"
        + "\n".join(f"  {c['name']}: {c['filter_reason']}"
                    for c in res.analysis["candidates"])
    )
    if res.diagnostics["conditional"]:
        if res.diagnostics["conditional_reason"] == "decisive_override":
            # winner is a bound-fixed refit: constraint evidence lives in the
            # list of parameters fixed at their bounds
            assert res.diagnostics["winner_boundary_fixed_params"], (
                "override winner must record its bound-fixed parameters"
            )
        else:
            assert res.diagnostics["winner_boundary_hits"], (
                "conditional winner must carry its constraint violations"
            )

    # (2) graphitic main position parity
    main = next(p for p in res.peaks if p["role"] == "main_graphitic")
    dc = abs(main["center"] - expert_graphite["center"])
    assert dc <= MAIN_CENTER_TOL_EV, (
        f"{name}: engine graphitic main {main['center']:.3f} vs expert "
        f"{expert_graphite['center']:.3f} (Δ {dc*1000:.0f} meV)"
    )

    # (3) satellite present and positioned
    if expert_satellite is not None:
        sat = next((p for p in res.peaks if p["role"] == "satellite_pi"), None)
        assert sat is not None, f"{name}: winner has no π→π* satellite slot"
        ds = abs(sat["center"] - expert_satellite["center"])
        assert ds <= SATELLITE_TOL_EV, (
            f"{name}: satellite {sat['center']:.3f} vs expert "
            f"{expert_satellite['center']:.3f} (Δ {ds:.2f} eV)"
        )

    # (4) envelope-level parity vs the expert's saved envelope
    specs = []
    for p in res.peaks:
        spec = dict(p)
        spec.pop("role", None); spec.pop("region", None)
        spec.pop("phase_id", None); spec.pop("stderr", None)
        specs.append(spec)
    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(
        rf.roi_be, rf.roi_intensity)
    expert_env = np.asarray(rf.fit_result["fittedY"], dtype=float)
    dom = rf.roi_be >= ENVELOPE_DOMAIN_MIN
    r_factor = float(np.sum(np.abs(engine_env[dom] - expert_env[dom]))
tests/autofit/test_stage2_rereview_findings.py
tests/autofit/test_engine_doublet.py
tests/autofit/test_stage2_completeness.py
tests/autofit/test_fit_certificate.py

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '825,857p'; sed -n '295,312p' app.py; rg -n 'app\\.py|create_app|tmp_path' tests/conftest.py tests/autofit/conftest.py; rg --files docs/findings/fit-termination-scope; git log -3 --oneline" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
   825	# candidates, primaries + all refits = 208 fits): restarts needed to certify —
   826	# 1: 10, 2: 173, 3: 14, 4: 5, then one fit each at 5, 6, 8, 9, 11 and 21 (flat
   827	# valleys: each Trust-Region run stops on its own ftol while a whole restart
   828	# still gains more than that). 5 left four real minima uncertified (8-JT
   829	# Scan_5's MG2 and MG3 primaries, so MG lost to AG2 at chi2r 42.5).
   830	CERTIFY_MAX_RESTARTS = 50
   831	
   832	
   833	def _certify_minimum(composite, y_sub, result, x, weights, max_nfev):
   834	    """Return (the lowest-chi2 point reached, certified)."""
   835	    current = result
   836	    chi = float(result.chisqr) if result.chisqr is not None else float("nan")
   837	    if not np.isfinite(chi):
   838	        return current, False
   839	    for _ in range(CERTIFY_MAX_RESTARTS):
   840	        try:
   841	            r = composite.fit(y_sub, current.params.copy(), x=x, weights=weights,
   842	                              method="least_squares", nan_policy="omit",
   843	                              max_nfev=max_nfev)
   844	        except Exception as exc:
   845	            log.debug("certificate restart raised: %s", exc)
   846	            return current, False
   847	        new = float(r.chisqr) if r.chisqr is not None else float("nan")
   848	        if not np.isfinite(new):
   849	            return current, False
   850	        improvement = (chi - new) / chi if chi > 0 else 0.0
   851	        if new < chi:
   852	            current, chi = r, new
   853	        if improvement < CERTIFY_FTOL:
   854	            return current, True
   855	    return current, False
   856	
   857	
_ANALYZE_JOB_TTL_SEC = 3600  # job progress files are short-lived scratch
                            # (not sessions) — 1 hour is generous for even
                            # a slow poll UI, and far below the 7-day
                            # session TTL these files are NOT related to.


class _AnalyzeError(Exception):
    """Carries the same (message, http status) pair _err() would return —
    lets the shared validate/run helpers signal a clean 4xx/5xx from
    EITHER the synchronous route or a background job thread (which has no
    Flask response object to return early from)."""

    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__(message)
        self.status = status


class _AnalyzeContext:
rg: tests/autofit/conftest.py: No such file or directory (os error 2)
docs/findings/fit-termination-scope/scope_tr_a.jsonl
docs/findings/fit-termination-scope/scope_lm_a.jsonl
docs/findings/fit-termination-scope/scope_tr_b.jsonl
docs/findings/fit-termination-scope/scope_lm_b.jsonl
docs/findings/fit-termination-scope/README.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-OdfqdhCe' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2jMk2RqQ' (errno=Operation not permitted)
3d419eb feat(unit A1): Find Peaks determinism - refit counts instead of seconds; convergence certified, warm restart removed
a9dad63 docs(unit A): scope check - Run Fit and the scattered starts also report success short of the minimum
0bb200b docs: deploy-log entry - unit 2 (long fits start and poll), public-URL check PASS

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"
from autofit.reference import load_reference_fits
from autofit.grammar import Phase,MaterialClass,resolve
from autofit.methods import get_method
r=next(r for r in load_reference_fits(\"docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip\") if r.name==\"C1s Scan_6\")
g=resolve([Phase(id=\"graphite\",material_class=MaterialClass.CONDUCTOR,regions=(\"C 1s\",),material=\"graphite\")],\"C 1s\")
out=get_method(\"ic_model_comparison\").run(r.roi_be,r.roi_intensity,grammar=g,options={\"n_refits\":4,\"rng_seed\":0,\"noise_floor\":1.0,\"enable_proposal_pass\":True,\"endpoint_avg\":3})
print(\"SCAN6\",out.success,out.diagnostics,flush=True)
print(\"SCREEN\",len(out.analysis[\"screen\"] or []),flush=True)'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"
from types import SimpleNamespace
import autofit.engine as e
class Comp:
 def __init__(self,seq): self.seq=iter(seq); self.calls=[]
 def fit(self,*a,**k):
  self.calls.append(k)
  r=next(self.seq)
  if isinstance(r,Exception): raise r
  return SimpleNamespace(chisqr=r,params={})
for name,start,seq,expected in [(\"higher\",10,[11],(10,True)),(\"zero\",0,[0],(0,True)),(\"nan\",10,[float(\"nan\")],(10,False)),(\"raise\",10,[ValueError(\"bad\")],(10,False)),(\"keep_lower\",10,[9,11],(9,True)),(\"relative\",1e10,[1e10-10],(1e10-10,True)),(\"initial_nan\",float(\"nan\"),[],(None,False))]:
 c=Comp(seq); r,ok=e._certify_minimum(c,None,SimpleNamespace(chisqr=start,params={}),None,None,123)
 assert ok==expected[1] and (expected[0] is None or r.chisqr==expected[0])
 assert all(k[\"method\"]==\"least_squares\" and k[\"max_nfev\"]==123 for k in c.calls)
 print(name,ok,len(c.calls))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 2197ms:
/Users/skyefortier/.matplotlib is not a writable directory
higher True 1
zero True 1
nan False 1
raise False 1
keep_lower True 2
relative True 1
initial_nan False 0

 succeeded in 45067ms:
....................
20 passed in 44.68s

exec
/bin/zsh -lc "rg -n 'stderr|confidence\\.values|confidence.*null' templates/index.html | head -45; sed -n '1300,1390p' autofit/engine.py; sed -n '40,120p' autofit/methods/ic_model_comparison.py; sed -n '1715,1760p' fitting.py; cat tests/conftest.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
9016:  const stderrMap = _stale ? {} : _buildStderrMap(state.fitResult);
9076:    const par = stderrMap[String(p.id)] || {};
9077:    const centerSE = par.center ? par.center.stderr : null;
9078:    const fwhmSE   = par.fwhm   ? par.fwhm.stderr   :
9079:                     par.fwhm_l ? par.fwhm_l.stderr  : null;
11787:  const stderrMap = _stats === 'stale' ? {} : _buildStderrMap(state.fitResult);
11811:    const par = stderrMap[String(p.id)] || {};
11812:    const cse  = par.center?.stderr  ?? '';
11813:    const fse  = (par.fwhm?.stderr ?? par.fwhm_l?.stderr) ?? '';
11814:    const ase  = par.amplitude?.stderr ?? '';
12037:  const stderrMap = _buildStderrMap(state.fitResult);
12042:  for (const [rawId, params] of Object.entries(stderrMap)) {
12058:      // Locked or linked: skip the alarm-style movement/stderr checks.
12093:      // stderr AND the value barely moved → covariance matrix singular near
12095:      // "converged at start with valid stderr" (silent — normal convergence).
12096:      const se = pData.stderr;
    (sat5/2 → sat7/2) is one group).
    """
    non_main = [s for s in model.slots if not _is_main_role(s.role)]
    roles = {s.role for s in non_main}
    parent_of = {s.role: s.linked_to for s in non_main
                 if s.linked_to is not None and s.linked_to in roles}

    def root(role: str) -> str:
        while role in parent_of:
            role = parent_of[role]
        return role

    groups: dict[str, list[ComponentSlot]] = {}
    for s in non_main:
        groups.setdefault(root(s.role), []).append(s)
    return list(groups.values())


def _identify_absent_slots(
    model: CandidateModel,
    stability: ModelStability,
    slot_areas: dict[str, float],
    primary: FitOutcome,
    persistence_threshold: float = ABSENT_SLOT_PERSISTENCE_THRESHOLD,
    area_fraction_threshold: float = ABSENT_SLOT_AREA_FRACTION,
) -> list[AbsentSlotReport]:
    """
    Absent classification is ATOMIC per linked group: a slot whose amplitude
    or shape is expression-tied to a partner cannot be absent while the
    partner is present (a spin-orbit satellite pair is one physical feature).
    Every member must individually meet the persistence + area criteria for
    the group to be classified absent.

    The area fraction is normalized against the mains of the SLOT'S OWN
    (region, phase) when any exist — in a joint co-fit, normalizing against
    the global main area would let a huge foreign main (e.g. the BN N 1s
    line in a U 4f + N 1s window) dilute a real satellite of the smaller
    element below the threshold (Codex Stage-3 finding #2).  Falls back to
    the global main area for slots without same-scope mains (e.g. proposals,
    which are region-unassigned).
    """
    global_main_area = sum(a for role, a in slot_areas.items() if _is_main_role(role))
    if global_main_area <= 0:
        return []

    scoped_main_area: dict[tuple[str, str], float] = {}
    for s in model.slots:
        if _is_main_role(s.role):
            key = (s.region, s.phase_id)
            scoped_main_area[key] = scoped_main_area.get(key, 0.0) \
                + float(slot_areas.get(s.role, 0.0))

    def _member_report(slot: ComponentSlot) -> Optional[AbsentSlotReport]:
        sstab = stability.per_slot.get(slot.role)
        if sstab is None or sstab.persistence >= persistence_threshold:
            return None
        main_area = scoped_main_area.get((slot.region, slot.phase_id), 0.0)
        if main_area <= 0:
            main_area = global_main_area
        area = float(slot_areas.get(slot.role, 0.0))
        frac = area / main_area
        if frac >= area_fraction_threshold:
            return None
        return AbsentSlotReport(
            role=slot.role, persistence=sstab.persistence, fitted_area=area,
            main_area=main_area, area_fraction=frac,
            threshold=area_fraction_threshold,
            removed_n_params=_count_slot_free_params(slot, primary),
        )

    absent: list[AbsentSlotReport] = []
    for group in _linked_groups(model):
        reports = [_member_report(s) for s in group]
        if all(r is not None for r in reports):
            absent.extend(reports)  # type: ignore[arg-type]
    return absent


# ─────────────────────────────────────────────────────────────────────────────
# Residual diagnostics
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ResidualDiagnostics:
    autocorrelation_lag1: float
    autocorr_flag: bool
    window_energies: dict[str, float]
    flagged_windows: list[str]


def compute_residual_diagnostics(
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> MethodResult:
        if grammar is None:
            raise ValueError("ic_model_comparison requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown ic_model_comparison options: {sorted(unknown)}")

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        w = np.asarray(weights, dtype=float) if weights is not None \
            else poisson_like_weights(y)
        noise_floor = float(opts.pop("noise_floor", 1.0))

        result = compare_models(
            x, y, w, grammar,
            noise_floor=noise_floor,
            n_refits=int(opts.pop("n_refits", 20)),
            rng_seed=int(opts.pop("rng_seed", 0)),
            candidate_filter=opts.pop("candidate_filter", None),
            enable_proposal_pass=bool(opts.pop("enable_proposal_pass", True)),
            enable_preseed=bool(opts.pop("enable_preseed", True)),
            persistence_threshold=float(opts.pop("persistence_threshold", 0.7)),
            bic_ambiguity_threshold=float(opts.pop("bic_ambiguity_threshold", 2.0)),
            absent_slot_area_fraction=float(opts.pop("absent_slot_area_fraction", 0.02)),
            absent_slot_persistence_threshold=float(
                opts.pop("absent_slot_persistence_threshold", 0.7)),
            progress_cb=progress_cb,
            fit_full_window=bool(opts.pop("fit_full_window", False)),
            endpoint_avg=pop_endpoint_avg(opts),
        )

        analysis = build_analysis_record(grammar, result)
        truncation_note = (
            f"analysis truncated — {result.n_candidates_evaluated} of "
            f"{result.n_candidates_total} candidates evaluated before the "
            "overall time budget was reached"
            if result.analysis_truncated else None
        )
        if not result.survivors:
            return MethodResult(
                method_id=self.id, success=False, peaks=[], analysis=analysis,
                confidence={}, diagnostics={
                    "n_reports": len(result.reports),
                    "analysis_truncated": result.analysis_truncated,
                    "n_candidates_evaluated": result.n_candidates_evaluated,
                    "n_candidates_total": result.n_candidates_total,
                },
                message=("no candidate survived filter-then-rank — see analysis "
                         "for filtered/non-converged detail (diagnostic, not "
                         "prescriptive: manual attention required)"
                         + (f"; {truncation_note}" if truncation_note else "")),
            )

        top = result.survivors[0]
        # Slots classified "correctly absent" won the BIC*-adjustment benefit
        # precisely because they carry no real signal — emitting them as
        # fitted peaks would contradict that classification (Codex finding
        # #4).  They remain visible in analysis.candidates[].absent_slots.
        absent_roles = {a.role for a in top.absent_slots}
        peaks = _peaks_from_report(top, exclude_roles=absent_roles)
        confidence = {
            slot.role: build_confidence_vector(top, slot.role, noise_floor)
            for slot in top.model.slots
            if slot.role not in absent_roles
        }
        message = ""
        winner_unassigned_roles = sorted(
            slot.role for slot in top.model.slots
            if slot.region == "unassigned"
            and slot.role not in absent_roles
        )
        if winner_unassigned_roles:
            centers = [
                f"{c.position:.2f}" for r in winner_unassigned_roles
                for c in top.primary_fit.components if c.slot_role == r
        p = _make_peak_params(m, spec, prefix, ordered)
        all_params.update(p)
        composite_model = m if composite_model is None else composite_model + m

    if composite_model is None:
        raise RuntimeError("No peaks were built")
    if require_component is not None:
        ids = [str(spec["id"]) for spec in peak_specs]
        if str(require_component) not in ids:
            raise ValueError(f"require_component '{require_component}' is not one of the peaks")
        if len(ids) < 2:
            raise ValueError("require_component needs at least two components")

    # Every random draw below (the perturbed restarts; the populations of the
    # two stochastic methods, which lmfit otherwise takes from numpy's GLOBAL
    # generator) comes from this one seed, so an identical request gives
    # identical DRAWS. (Not an identical Trust-Region result: see CLAUDE.md,
    # "Reproducibility".)
    if caller_seed is not None:
        random_seed = int(caller_seed)
    else:
        random_seed = _request_seed(
            x, y, bg, [spec.get("shape", "pseudo_voigt_gl") for spec in ordered],
            [f"p{spec['id']}_" for spec in ordered], all_params,
            fit_kws=fit_kws, n_perturb=n_perturb)
    # spawn(3) yields the same first two children as spawn(2): adding the
    # scattered-starts stream leaves every existing draw (and its pins) alone.
    perturb_rng, solver_rng, starts_rng = (np.random.default_rng(child)
                                           for child in np.random.SeedSequence(random_seed).spawn(3))
    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")

    # ── Determinacy (unit F2, 2026-09-26) ─────────────────────────────────────
    # "Nothing is a fit unless it converged and is determined." With at least
    # as many free parameters as data points the model can pass through every
    # point: lmfit reports redchi = chi2 / max(1, nfree) as if it were a fit,
    # and the support / required F tests clamp their dof to 1, so such a model
    # read as a near-perfect, fully supported fit (sweep M2: 6 points, 2 GL
    # components, chi2r 2.8e-6, both "supported"). A count, not a threshold:
    # zero or negative degrees of freedom is refused outright.
    n_free_request = sum(1 for par in all_params.values() if par.vary and not par.expr)
    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
    if n_free_request >= n_data_request:
        raise ValueError(
            f"The model is not determined by these data: {n_free_request} free parameters for "
            f"{n_data_request} data points leaves no degrees of freedom. Widen the fitted range, "
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

codex
All 20 tests in the two changed test files passed. Additional probes passed for zero χ², a higher-χ² restart, non-finite results, exceptions, relative tolerance, and forwarding the evaluation cap. A full-page Scan_6 run is in progress to check the MG2 acceptance case independently of the plan.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-s\",\"-q\",\"-p\",\"no:cacheprovider\",\"tests/autofit/test_engine_doublet.py\",\"tests/autofit/test_stage2_rereview_findings.py\",\"tests/autofit/test_bayesian_method.py\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
exec
/bin/zsh -lc "nl -ba docs/findings/fit-termination-scope/README.md | head -27; nl -ba tests/autofit/test_fit_certificate.py | sed -n '1,40p'; sed -n '1460,1565p' autofit/engine.py; rg -n 'assert|"'^def test'"' tests/autofit/test_engine_doublet.py tests/autofit/test_stage2_rereview_findings.py | tail -50; rg -n 'proposal_pass_timings|\\.success' autofit/engine.py autofit/methods/ic_model_comparison.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
     1	# Do fits stop before the minimum? Scope check for Unit A (2026-09-28)
     2	
     3	Owner, Unit A: "Judge convergence by whether the refit actually reached the
     4	minimum, not by the optimiser's success flag … SCOPE CHECK FIRST: does Run
     5	Fit, or the scattered-starts check, share the ~30-evaluation early stopping?"
     6	
     7	## Find Peaks: where the "~30 evaluations" comes from
     8	
     9	It is not MINPACK stopping early from a cold start. `autofit.engine.fit_candidate`
    10	fits with `leastsq`; when that fit FAILS (the 18 000-evaluation cap) it makes
    11	ONE warm restart from the exit point with a 2 000-evaluation budget and takes
    12	the restart's result if its `success` flag is set. From a stalled point that
    13	restart ends on MINPACK's `xtol` test in ~30 evaluations and reports success.
    14	Example (8-JT C1s Scan_7, MG2, stability refit 0): the cold `leastsq` fit stalls
    15	at χ²ᵣ 37.6 after 18 000 evaluations; the warm restart "succeeds" there in 30;
    16	`least_squares` from the same start reaches χ²ᵣ 5.21 in 507. The code comment
    17	assumes the failed fit had already reached the minimum; here it had not.
    18	
    19	## Run Fit and the scattered-starts check
    20	
    21	`scripts/fit_termination_scope.py` runs every one of the 202 committed targets
    22	through `/api/fit` exactly as the page sends it (3 perturbed restarts, 3
    23	scattered starts), intercepts every lmfit fit, and refines each result from its
    24	end point with a fresh `least_squares` fit (same model, data, weights, bounds).
    25	A descent from a minimum cannot lower χ² beyond the optimiser's stopping sliver;
    26	from a point short of it, it does. Summary: `scripts/fit_termination_scope_analyze.py`.
    27	
     1	"""Unit A1 (2026-09-29): Find Peaks judges convergence by a CERTIFICATE, not the
     2	optimiser's flag. A fit has reached a minimum when a fresh Trust-Region descent
     3	from its end point improves chi2 by less than that descent's own stopping
     4	tolerance (scipy least_squares' ftol); restarts repeat from each improved point
     5	up to CERTIFY_MAX_RESTARTS; out of restarts = not converged. The flag was wrong
     6	both ways: a warm restart from a stall "succeeded" in ~30 evaluations at
     7	chi2r 37.6 where the minimum is 5.21 (8-JT C1s Scan_7), and a refit capped at
     8	18 000 evaluations AT the minimum counted as failed (1-GTA C1s Scan_6)."""
     9	import inspect
    10	import os
    11	
    12	import numpy as np
    13	import pytest
    14	import scipy.optimize
    15	
    16	import autofit.engine as eng
    17	from autofit.grammar import MaterialClass, Phase, resolve
    18	from autofit.methods.base import poisson_like_weights
    19	from autofit.reference import load_reference_fits
    20	
    21	DATA = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "autofit", "test_data")
    22	G = resolve([Phase(id="graphite", material_class=MaterialClass.CONDUCTOR, regions=("C 1s",), material="graphite")], "C 1s")
    23	
    24	
    25	def _scan(project, name):
    26	    rf = next(r for r in load_reference_fits(os.path.join(DATA, project)) if r.name == name)
    27	    x, y = np.asarray(rf.roi_be, float), np.asarray(rf.roi_intensity, float)
    28	    return x, y, poisson_like_weights(y)
    29	
    30	
    31	def _mg2():
    32	    return next(c for c in G.candidates if c.name == "MG2_graphAsymGL_aliph_sat_CO_C=O")
    33	
    34	
    35	def test_the_tolerance_is_the_optimisers_own():
    36	    assert eng.CERTIFY_FTOL == inspect.signature(scipy.optimize.least_squares).parameters["ftol"].default
    37	    assert isinstance(eng.CERTIFY_MAX_RESTARTS, int) and eng.CERTIFY_MAX_RESTARTS >= 1
    38	
    39	
    40	def _kkt_violations(comp, params, x, y_net, w):
    contributors: list[tuple[str, bool]]


@dataclass
class ProposalPassTiming:
    candidate_name: str
    n_flagged: int
    n_over_cap: int
    n_attempted: int
    n_fast_rejected: int
    n_stability_rejected: int
    n_accepted: int
    wall_time_sec: float
    timed_out: bool


@dataclass
class ModelReport:
    """Complete diagnostics for one candidate — no collapse to one scalar."""
    model: CandidateModel
    primary_fit: FitOutcome
    bic: float
    stability: ModelStability
    residuals: ResidualDiagnostics
    plausibility: PlausibilityFlags
    absent_slots: list[AbsentSlotReport] = field(default_factory=list)
    proposed_peaks: list[ProposedPeakReport] = field(default_factory=list)
    augmented_from: Optional[str] = None
    # Full lmfit param names fixed at their bounds by the decisive-override
    # bound-fixed refit (empty for ordinary reports).  Stability figures on
    # such a report are inherited from the free (pegged) fit — a documented
    # approximation.
    boundary_fixed_params: list[str] = field(default_factory=list)

    @property
    def reduced_chi_sq(self) -> float:
        dof = max(self.primary_fit.n_data - self.primary_fit.n_params, 1)
        return self.primary_fit.weighted_chi_sq / dof

    @property
    def adjusted_n_params(self) -> int:
        removed = sum(a.removed_n_params for a in self.absent_slots)
        return max(self.primary_fit.n_params - removed, 1)

    @property
    def bic_adjusted(self) -> float:
        """BIC* (heuristic — absent-slot params arithmetically subtracted;
        the BIC/IC math review requires the raw full-k and weighted
        counterparts REPORTED beside it: see bic_raw / bic_weighted)."""
        n = self.primary_fit.n_data
        rss = self.primary_fit.residual_sum_sq
        if n <= 0 or rss <= 0:
            return float("inf")
        return n * np.log(rss / n) + self.adjusted_n_params * np.log(n)

    @property
    def bic_raw(self) -> float:
        """Full-k, no absent-slot adjustment — reported beside the labeled
        heuristic so the adjustment can never silently decide alone
        (BIC/IC math review: 'large-model RSS with small-model penalty')."""
        return compute_bic(self.primary_fit)

    @property
    def bic_weighted(self) -> float:
        """Known-σ (weighted-χ²) FULL-k BIC: χ²_w + k·ln n with k = the
        actual free-parameter count (NO absent-slot adjustment — the
        adjustment is the labeled heuristic on BIC*; letting it into the
        companion criterion would let the heuristic shape the
        weighted-vs-RSS disagreement it exists to expose).  This is the
        criterion CONSISTENT with the Poisson-weighted fits; the ranking
        still uses BIC*, and weighted_ic_disagreement fires when the two
        criteria pick different survivors."""
        n = self.primary_fit.n_data
        chi = self.primary_fit.weighted_chi_sq
        if n <= 0 or not np.isfinite(chi):
            return float("inf")
        return chi + self.primary_fit.n_params * np.log(n)

    @property
    def n_eff_lag1(self) -> Optional[float]:
        """Effective sample size from the lag-1 autocorrelation of the
        weighted residuals: n·(1−ρ)/(1+ρ).  Oversampled/correlated spectra
        make the raw n in k·ln(n) (and the ΔBIC thresholds) overconfident
        — reported so consumers can see how far the independence
        assumption is stretched (BIC/IC math review)."""
        lm = self.primary_fit.lmfit_result
        if lm is None or getattr(lm, "residual", None) is None:
            return None
        r = np.asarray(lm.residual, dtype=float)
        if len(r) < 8 or float(np.std(r)) == 0.0:
            return None
        r = r - r.mean()
        rho = float(np.sum(r[:-1] * r[1:]) / np.sum(r * r))
        rho = min(max(rho, -0.99), 0.99)
        return float(len(r) * (1.0 - rho) / (1.0 + rho))

    @property
    def active_min_persistence(self) -> float:
        absent_roles = {a.role for a in self.absent_slots}
        active = [s for s in self.stability.per_slot.values() if s.role not in absent_roles]
        if not active:
            return 0.0
        return min(s.persistence for s in active)


def compute_bic(fit: FitOutcome) -> float:
tests/autofit/test_engine_doublet.py:51:def test_fixed_ratio_doublet():
tests/autofit/test_engine_doublet.py:56:    assert out.converged
tests/autofit/test_engine_doublet.py:59:    assert p32.position == pytest.approx(197.9, abs=0.03)
tests/autofit/test_engine_doublet.py:60:    assert p12.position - p32.position == pytest.approx(SPLIT, abs=0.1)
tests/autofit/test_engine_doublet.py:62:    assert p12.amplitude == pytest.approx(p32.amplitude * RATIO, rel=1e-9)
tests/autofit/test_engine_doublet.py:64:    assert p12.fwhm == pytest.approx(p32.fwhm, rel=1e-9)
tests/autofit/test_engine_doublet.py:67:def test_relaxed_ratio_doublet_recovers_true_ratio():
tests/autofit/test_engine_doublet.py:73:    assert out.converged
tests/autofit/test_engine_doublet.py:76:    assert fitted_ratio == pytest.approx(true_ratio, abs=0.02)
tests/autofit/test_engine_doublet.py:79:def test_relaxed_ratio_at_bound_is_boundary_hit():
tests/autofit/test_engine_doublet.py:85:    assert out.converged
tests/autofit/test_engine_doublet.py:86:    assert any(h.startswith("main_p12:ratio@min") for h in out.boundary_hits), \
tests/autofit/test_engine_doublet.py:90:def test_doublet_stability_persistence():
tests/autofit/test_engine_doublet.py:97:    assert stab.per_slot["main_p32"].persistence == 1.0
tests/autofit/test_engine_doublet.py:98:    assert stab.per_slot["main_p12"].persistence == 1.0
tests/autofit/test_engine_doublet.py:99:    assert stab.per_slot["main_p32"].position_mad < 0.02
tests/autofit/test_engine_doublet.py:102:def test_proposed_slot_is_phase_unassigned():
tests/autofit/test_engine_doublet.py:115:    assert prop.region == "unassigned"
tests/autofit/test_engine_doublet.py:116:    assert prop.phase_id == "unassigned"
tests/autofit/test_engine_doublet.py:119:def test_absent_normalization_is_region_scoped():
tests/autofit/test_engine_doublet.py:152:    assert absent == [], (
tests/autofit/test_stage2_rereview_findings.py:37:    assert fit.converged
tests/autofit/test_stage2_rereview_findings.py:52:def test_orphan_peaks_never_clean_survivor():
tests/autofit/test_stage2_rereview_findings.py:59:    assert clean in res.survivors
tests/autofit/test_stage2_rereview_findings.py:60:    assert orphaned not in res.survivors or res.conditional
tests/autofit/test_stage2_rereview_findings.py:62:    assert "orphan_peaks=True" in reasons[id(orphaned)]
tests/autofit/test_stage2_rereview_findings.py:65:def test_orphan_only_pool_is_conditional_tier():
tests/autofit/test_stage2_rereview_findings.py:69:    assert res.conditional is True
tests/autofit/test_stage2_rereview_findings.py:70:    assert res.conditional_reason == "no_clean_survivor"
tests/autofit/test_stage2_rereview_findings.py:71:    assert res.survivors and res.survivors[0] is orphaned
tests/autofit/test_stage2_rereview_findings.py:76:def test_basin_support_counts_reproducible_minimum():
tests/autofit/test_stage2_rereview_findings.py:84:    assert 1 <= st.best_basin_support <= 5
tests/autofit/test_stage2_rereview_findings.py:85:    assert st.best_basin_support >= 2, (
tests/autofit/test_stage2_rereview_findings.py:93:def test_sanitized_slug_collision_raises():
tests/autofit/test_stage2_rereview_findings.py:102:def test_distinct_slugs_still_resolve():
tests/autofit/test_stage2_rereview_findings.py:108:    assert g.candidates
tests/autofit/test_stage2_rereview_findings.py:128:def test_criteria_panel_uses_method_threshold():
tests/autofit/test_stage2_rereview_findings.py:137:    assert res.success
tests/autofit/test_stage2_rereview_findings.py:144:        assert panel["bic_ambiguous"] is True
tests/autofit/test_stage2_rereview_findings.py:147:        assert (gaps[1] - gaps[0]) > 2.0, "gap fell within old default; test no longer discriminates"
autofit/engine.py:880:    leastsq(), surfacing as result.success=False) cuts off the latter
autofit/engine.py:1581:    proposal_pass_timings: list[ProposalPassTiming] = field(default_factory=list)
autofit/engine.py:2878:    result.proposal_pass_timings = timings

exec
/bin/zsh -lc "rg -n 'analyze/progress|poll.*analy|analy.*poll' templates/index.html; rg -n 'apply.*Find|apply.*[Aa]naly|stderr' autofit/methods/ic_model_comparison.py; rg -n 'bound_fixed|decisive_override' tests/autofit --glob 'test_*.py' | head -30; git status --short" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
16130:// GET /api/analyze/progress/<job_id> — real engine state (candidate N of
16149:    const resp = await fetch('/api/analyze/progress/' + encodeURIComponent(jobId));
232:            stderr = {}
234:                if pname.startswith(prefix) and par.stderr is not None:
235:                    stderr[pname[len(prefix):]] = float(par.stderr)
236:            if stderr:
237:                rec["stderr"] = stderr
tests/autofit/test_stress_honesty.py:104:    2000 promotes the bound-fixed decoy via decisive_override, k=3,
tests/autofit/test_c1s_parity_gate.py:135:        if res.diagnostics["conditional_reason"] == "decisive_override":
tests/autofit/test_endpoint_avg_wiring.py:57:                        "_attempt_proposal", "_bound_fixed_refit", "_apply_decisive_override",
tests/autofit/test_b1s_cl2p_parity_gates.py:93:    assert res.diagnostics["conditional_reason"] == "decisive_override"
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CnszMyFi' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-dELqPXse' (errno=Operation not permitted)
?? docs/autofit/codex/a1_determinism_verdict_runA.md
?? docs/autofit/codex/a1_determinism_verdict_runB.md
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json

 succeeded in 42623ms:
........................
24 passed in 42.09s

exec
/bin/zsh -lc "sed -n '16125,16192p' templates/index.html; sed -n '1770,1830p' autofit/engine.py; sed -n '1,150p' tests/autofit/test_stress_honesty.py; rg -n 'time|random|seed|range\\(' autofit/methods/bayesian_exchange_mc.py | head -35" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
  const m = Math.floor(s / 60), r = s % 60;
  return m + 'm ' + r + 's';
}

// One poll payload -> the on-screen status line. `poll` is the JSON from
// GET /api/analyze/progress/<job_id> — real engine state (candidate N of
// M, screening/stabilizing), never a fake animation.
function _fpProgressText(poll) {
  const elapsed = _fpFormatElapsed(poll && poll.elapsed_sec);
  const msg = (poll && poll.message) || 'working…';
  return 'Analyzing… ' + elapsed + ' — ' + msg;
}

const FP_POLL_INTERVAL_MS = 350;
// Client-side watchdog: the actual analysis has its own server-side budget
// (TOTAL_ANALYSIS_TIMEOUT_SEC, well under this), so this only fires if a
// job's progress file stops updating entirely (e.g. a recycled gunicorn
// worker process taking the background thread down with it) — the
// indicator must NEVER spin forever even in that pathological case.
const FP_POLL_WATCHDOG_SEC = 600;

async function _fpPollJob(jobId) {
  const started = Date.now();
  while (true) {
    const resp = await fetch('/api/analyze/progress/' + encodeURIComponent(jobId));
    if (!resp.ok) {
      throw new Error('Lost the progress channel (HTTP ' + resp.status + ').');
    }
    const poll = await resp.json();
    document.getElementById('fp-status').textContent = _fpProgressText(poll);
    if (poll.status === 'done') return poll;
    if (poll.status === 'error') {
      throw new Error(poll.error || 'Analysis failed.');
    }
    if ((Date.now() - started) / 1000 > FP_POLL_WATCHDOG_SEC) {
      throw new Error('This is taking unusually long — the analysis may ' +
        'have been lost. Try again.');
    }
    await new Promise(r => setTimeout(r, FP_POLL_INTERVAL_MS));
  }
}

async function runFindPeaks() {
  const status = document.getElementById('fp-status');
  const spinner = document.getElementById('fp-spinner');
  const btn = document.getElementById('fp-run');
  // The full preserved selection, NOT anything scraped from the DOM — a
  // co-fit member filtered/collapsed out of view by the search box or the
  // periodic-table picker would be invisible to the DOM but must still be
  // submitted (see _fpToggleRegion / _fpSyncSelectionUI).
  const regions = Array.from(_fpRegionsSelected);
  if (!regions.length) { status.textContent = 'Select at least one region.'; return; }
  let options;
  try {
    options = JSON.parse(document.getElementById('fp-options').value || '{}');
  } catch (e) { status.textContent = 'Options are not valid JSON.'; return; }
  const method = document.getElementById('fp-method').value;
  // Endpoint averaging: the Background panel is the source for every method
  // that fits a background (its /api/analyze/meta default_options advertise
  // endpoint_avg — all four menu methods do); an explicit value in the
  // Advanced JSON wins. Methods that do not advertise it are not sent it
  // (their option whitelists would reject the key). The value actually
  // sent is recorded on the tab's findPeaks.last so applyFindPeaks keeps preview == fit.
  const fpMethodMeta = ((_fpMeta && _fpMeta.methods) || []).find(x => x.id === method);
  const methodTakesEp = !!(fpMethodMeta && fpMethodMeta.default_options
                           && Object.prototype.hasOwnProperty.call(fpMethodMeta.default_options, 'endpoint_avg'));
  if (methodTakesEp && options.endpoint_avg === undefined) {
    options.endpoint_avg = parseInt(document.getElementById('bg-endpoint-avg')?.value) || 1;
def _all_grammar_windows(
    candidates: list[CandidateModel],
    canonical_windows: dict[str, tuple[float, float]],
) -> list[tuple[float, float]]:
    wins = [s.be_window for c in candidates for s in c.slots]
    wins += list(canonical_windows.values())
    return wins


def _preseed_window_margin(candidates: list[CandidateModel]) -> float:
    """Mean main-FWHM midpoint across the candidate set × the proposal
    separation factor — the shared "too close to a grammar window to be a
    separate feature" convention (used identically by the dominant channel
    and the pool's curvature channel)."""
    mids = [_main_slot_fwhm_midpoint(c) for c in candidates] or [1.0]
    return PROPOSAL_GRAMMAR_SEPARATION_FACTOR * float(np.mean(mids))


def detect_out_of_grammar_dominants(
    x: np.ndarray,
    y: np.ndarray,
    background: np.ndarray,
    candidates: list[CandidateModel],
    canonical_windows: dict[str, tuple[float, float]],
    noise_floor: float = 1.0,
) -> list[PreseedSpec]:
    """
    Prominent smoothed local maxima of the background-subtracted data that
    lie outside EVERY grammar slot window and diagnostic window (+ the same
    separation margin the proposal pass uses).  Conservative by design —
    dominance (fraction-of-max) AND detection-floor SNR gates — so ordinary
    grammar-covered spectra return [] and small out-of-window features stay
    the residual-proposal pass's job.
    """
    if len(x) < max(PRESEED_SMOOTH_POINTS + 4, 8):
        return []
    # real raw_be grids DESCEND — normalize (np.interp-class bug family)
    if x[0] > x[-1]:
        x_asc, y_asc, bg_asc = x[::-1], y[::-1], background[::-1]
    else:
        x_asc, y_asc, bg_asc = x, y, background
    y_net = y_asc - bg_asc
    k = PRESEED_SMOOTH_POINTS
    kernel = np.ones(k) / k
    ys = np.convolve(y_net, kernel, mode="same")
    global_max = float(np.max(ys))
    if global_max <= 0:
        return []

    # margin: mean main-FWHM midpoint across the candidate set × the
    # proposal separation factor (the same "too close to a window to be a
    # separate feature" convention)
    margin = _preseed_window_margin(candidates)
    windows = _all_grammar_windows(candidates, canonical_windows)

    def in_any_window(be: float) -> bool:
        return any((lo - margin) <= be <= (hi + margin) for lo, hi in windows)

    found: list[PreseedSpec] = []
    edge = max(2, k // 2)     # smoothing edge — 'same' convolution damps ends
    for i in range(edge, len(ys) - edge):
"""
Always-on stress-honesty net — the KEY-CRITERION invariants from the
synthetic hard-case suite (run-brief item 2), pinned on the fast subset
(IC n_refits=4 + LS + sparse; the full battery incl. Bayesian and noise
replicates is scripts/run_stress_battery.py → stress_battery_runs.jsonl,
summarized in docs/autofit/stress-test-report.md).

Where there IS a right answer the engine must recover it; where the truth
is outside the model space the mismatch must be machine-visible; an
over-specified menu must be pruned, not populated.  Values pinned from the
2026-07-04 measurement run.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    asym_truth_case,
    bg_matched_control_case,
    bg_mismatch_case,
    isolated_missing_peak_case,
    overlap_case,
    overspecified_case,
    overspecified_decoy_case,
)
from autofit.methods import get_method  # noqa: E402

IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _ic(case):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options=dict(IC_OPTS))


@pytest.fixture(scope="module")
def sep1():
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    return case, _ic(case)


def test_resolved_doublet_recovered_clean(sep1):
    """Separation 1×FWHM at 9000 counts: distinguishable → must recover."""
    case, res = sep1
    assert res.success
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.05)


def test_resolved_doublet_ls_baseline(sep1):
    case, _ = sep1
    res = get_method("least_squares").run(
        case.x, case.y, peak_specs=case.ls_specs,
        options={"background_method": "linear"})
    assert res.success
    for t, p in zip(case.truth, res.peaks):
        assert p["center"] == pytest.approx(t["center"], abs=0.05)
        assert p["fwhm"] == pytest.approx(t["fwhm"], abs=0.1)


def test_resolved_doublet_sparse_count_only():
    """Sparse COUNT-ONLY pin — explicitly NOT a recovery claim: on this
    PV-truth case the selected atoms sit 0.45-0.75 eV off (Gaussian-atom /
    30%-Lorentzian mismatch, its documented weakness; classified
    count_ok_param_biased in the battery, never PASS).  The invariant
    worth pinning is only that the component COUNT does not hallucinate on
    a clean, well-separated doublet."""
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    res = get_method("sparse_map").run(case.x, case.y, grammar=case.grammar)
    assert res.success
    assert len(res.peaks) == 2


def test_overspecified_menu_prunes_not_invents():
    """Truth 2 peaks, menu offers up to 5: the winner must carry exactly
    the true structure — no invented components."""
    case = overspecified_case(seed=31)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    matched = 0
    for t in case.truth:
        if any(abs(p["center"] - t["center"]) < 0.3 for p in by_role.values()):
            matched += 1
    assert matched == 2


def test_inroi_decoy_pruned_not_populated():
    """The harder over-specification test (Codex stress review): a decoy
    'shoulder' window BETWEEN the true peaks, where real tail intensity
    lives — the winner must carry the true 2-component structure with the
    decoy hypothesis rejected, not a populated 3-component invention.
    Measured 2026-07-04: P2 clean, χ²ᵣ 1.10, exact recovery ON THIS BASE
    DRAW.  The battery shows the prune is noise-draw-DEPENDENT (offset
    2000 promotes the bound-fixed decoy via decisive_override, k=3,
    conditional-flagged) — stress report finding 8; this pin covers the
    base draw only."""
    case = overspecified_decoy_case(seed=32)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert len(res.peaks) == 2
    by_role = {p["role"]: p for p in res.peaks}
    for t, role in zip(case.truth, ("main_a", "main_b")):
        assert by_role[role]["center"] == pytest.approx(t["center"], abs=0.1)


def test_bg_matched_control_recovers():
    case = bg_matched_control_case(seed=62)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["conditional"] is False
    wc = next(c for c in res.analysis["candidates"] if c["name"] == "P2")
    assert wc["reduced_chi_sq"] < 2.0


def test_bg_mismatch_surfaces_loudly():
    """Shirley-shaped truth fit with a straight line: the mismatch must be
    machine-visible (conditional tier + grossly elevated χ²ᵣ), never a
    clean confident result."""
    case = bg_mismatch_case(seed=61)
    res = _ic(case)
    assert res.diagnostics["conditional"] is True
    wc = next(c for c in res.analysis["candidates"]
              if c["name"] == res.diagnostics["winner"])
    assert wc["reduced_chi_sq"] > 10.0


def test_preseed_catches_isolated_missing_peak():
    """Unit F1 (2026-07-07): the isolated unmodeled peak (28% of the main —
    above the preseed dominance gate) is now caught by the PRE-FIT seeding
    channel: same honesty contract as the proposal pass (region-unassigned
    component, human adjudication), reached before the fit so the landscape
    is sane.  The peak must be seeded, fitted at the true position, and
    surfaced in analysis.preseeded_features."""
    case = isolated_missing_peak_case(seed=71)
    res = _ic(case)
    assert res.diagnostics["winner"].endswith("+preseed")
    feats = res.analysis["preseeded_features"]
    assert len(feats) == 1
    assert feats[0]["center_be"] == pytest.approx(201.5, abs=0.3)
    seeded = [p for p in res.peaks if p["role"].startswith("preseed_dominant")]
44:Determinism: fully seeded (rng_seed).  Runtime scales with
130:    rng_seed: int = 0,
137:    rng = np.random.default_rng(rng_seed)
166:    ll_records: list[list[float]] = [[] for _ in range(K)]
168:    for sweep in range(n_sweeps):
169:        for k in range(K):
172:            for j in range(dim):
192:            for k in range(K - 1):
203:            for k in range(K):
210:        for k in range(K - 1):
221:    # seed-to-seed F spread exceeded the between-model gap, silently — the
265:    for j in range(dim):
278:        for lag in range(1, min(n // 2, 200)):
289:    "rng_seed", "candidate_filter", "ci_level", "noise_floor",
290:    "seed_replicates",
326:            rng_seed=int(opts.pop("rng_seed", 0)),
335:        # Independent seeded evidence replicates (Codex Stage-5 blocker #1,
337:        # confidently-resolved F gap that a different seed flips — the
339:        # cost k× runtime; the across-replicate half-range is a genuine
342:        seed_replicates = int(opts.pop("seed_replicates", 1))
343:        if seed_replicates < 1:
344:            raise ValueError("seed_replicates must be >= 1")
356:                for j in range(1, seed_replicates):
358:                                      rng_seed=mc_kwargs["rng_seed"] + j)
377:                # (peaks/CIs) stays the BASE seed's run — flagged for
422:        # seed-to-seed F spread flipped the winner while |ΔF| ~ 3): if the
438:                    "increase n_sweeps/n_replicas or seed_replicates before "
474:            # With seed_replicates > 1 ONLY the evidence (F) is replicated;
475:            # peaks/CIs summarize the base seed's posterior (re-check #2)
477:            "posterior_samples_seed": mc_kwargs["rng_seed"],
478:            "seed_replicates": seed_replicates,
516:    by_name = dict(zip(names, range(len(names))))
555:                    "random-walk quantiles likely UNDERESTIMATE uncertainty; "

codex
I found a remaining user-visible deadline: the page stops polling after 600 seconds, even when the job is still running and reporting progress. Its comment explicitly relies on the server budget A1 removes. I’m reproducing this path: a loaded run that crosses ten minutes can finish on the server but never deliver its result to the page.

exec
/bin/zsh -lc "command -v node; nl -ba templates/index.html | sed -n '16135,16168p'; sed -n '16200,16295p' templates/index.html; nl -ba autofit/engine.py | sed -n '139,157p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
/Users/skyefortier/.local/bin/node
 16135	  return 'Analyzing… ' + elapsed + ' — ' + msg;
 16136	}
 16137	
 16138	const FP_POLL_INTERVAL_MS = 350;
 16139	// Client-side watchdog: the actual analysis has its own server-side budget
 16140	// (TOTAL_ANALYSIS_TIMEOUT_SEC, well under this), so this only fires if a
 16141	// job's progress file stops updating entirely (e.g. a recycled gunicorn
 16142	// worker process taking the background thread down with it) — the
 16143	// indicator must NEVER spin forever even in that pathological case.
 16144	const FP_POLL_WATCHDOG_SEC = 600;
 16145	
 16146	async function _fpPollJob(jobId) {
 16147	  const started = Date.now();
 16148	  while (true) {
 16149	    const resp = await fetch('/api/analyze/progress/' + encodeURIComponent(jobId));
 16150	    if (!resp.ok) {
 16151	      throw new Error('Lost the progress channel (HTTP ' + resp.status + ').');
 16152	    }
 16153	    const poll = await resp.json();
 16154	    document.getElementById('fp-status').textContent = _fpProgressText(poll);
 16155	    if (poll.status === 'done') return poll;
 16156	    if (poll.status === 'error') {
 16157	      throw new Error(poll.error || 'Analysis failed.');
 16158	    }
 16159	    if ((Date.now() - started) / 1000 > FP_POLL_WATCHDOG_SEC) {
 16160	      throw new Error('This is taking unusually long — the analysis may ' +
 16161	        'have been lost. Try again.');
 16162	    }
 16163	    await new Promise(r => setTimeout(r, FP_POLL_INTERVAL_MS));
 16164	  }
 16165	}
 16166	
 16167	async function runFindPeaks() {
 16168	  const status = document.getElementById('fp-status');
                         && options.endpoint_avg >= 1 && options.endpoint_avg <= ENDPOINT_AVG_MAX)) {
    status.textContent = 'Advanced options: endpoint_avg must be a whole number between 1 and ' +
                         ENDPOINT_AVG_MAX + ' (got ' + JSON.stringify(options.endpoint_avg) + ').';
    return;
  }
  const engineEndpointAvg = methodTakesEp ? String(options.endpoint_avg) : LEGACY_ENDPOINT_AVG;

  btn.disabled = true;
  spinner.style.display = 'inline-block';
  status.textContent = 'Analyzing… starting…';
  try {
    // OWNER + INPUTS FIRST: everything this analysis needs is read from the
    // tab that is active NOW, before the first await; the result goes back
    // to this same record object whatever tab is active at completion.
    const owner = _opOwner();
    if (!owner) { status.textContent = 'Open a spectrum tab first.'; return; }
    // corrected-frame data, same convention as the manual fit path
    const be = getCorrectedBE();
    const inten = state.rawIntensity;
    const payload = {
      session_id: null, cc_shift: 0,
      roi: { be_min: parseFloat(document.getElementById('roi-min').value),
             be_max: parseFloat(document.getElementById('roi-max').value) },
      material_class: document.getElementById('fp-material').value,
      regions, method, options,
    };
    if (method === 'least_squares') {
      payload.peak_specs = state.peaks.map(peakToBackendSpec);
      if (!payload.peak_specs.length) {
        status.textContent = '“Refit my current peaks” needs peaks on ' +
          'this tab first — add some, or pick “Compare peak models”.';
        return;
      }
    }
    payload.session_id = await uploadToBackend(be, inten);
    const resp = await fetch('/api/analyze/start', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    // Don't assume the body is JSON before checking resp.ok — a worker
    // timeout/crash can return a bare non-JSON 500 (plain text or an HTML
    // error page), and calling .json() on that throws an opaque SyntaxError
    // instead of a message the user can act on.
    const ct = resp.headers.get('content-type') || '';
    if (!resp.ok) {
      let msg = 'HTTP ' + resp.status;
      if (ct.includes('application/json')) {
        try {
          const errBody = await resp.json();
          if (errBody && errBody.error) msg = errBody.error;
        } catch (_) { /* not actually JSON despite the header; use HTTP status */ }
      } else {
        const text = (await resp.text()).replace(/<[^>]*>/g, ' ').trim();
        if (text) msg += ': ' + text.slice(0, 300);
      }
      throw new Error(msg);
    }
    const { job_id } = await resp.json();
    const poll = await _fpPollJob(job_id);
    const body = poll.result;
    if (!_ownerLive(owner)) { status.textContent = 'Discarded — the tab was closed during the analysis.'; return; }
    _fpSetLast({ body, method, regions, fitFullWindow: !!options.fit_full_window, endpointAvg: engineEndpointAvg }, owner);
    if (!_ownerActive(owner)) {
      // The result belongs to the tab it was started on; do not show it
      // over another tab's modal.
      status.textContent = 'Results stored on tab “' + owner.name + '” — switch back to it and reopen Find Peaks to apply.';
      notify('Find Peaks finished on tab “' + owner.name + '”; its results are waiting there.', 'amber');
      return;
    }
    _fpRenderResults(body);
    status.textContent = '';
  } catch (e) {
    status.textContent = 'Failed: ' + e.message;
  } finally {
    // ALWAYS clears — success, error, and watchdog-timeout paths all land
    // here (goal: the indicator must never spin forever).
    btn.disabled = false;
    spinner.style.display = 'none';
  }
}

function _fpEsc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g,
    c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function _fpBanner(text, color) {
  return `<div style="font-size:10px;padding:5px 8px;margin:3px 0;border-left:3px solid ${color};background:var(--bg2)">${text}</div>`;
}

function _fpRenderResults(body) {
  const flags = [];
  const d = body.diagnostics || {}, a = body.analysis || {};
  const B = FP_STRINGS.banners;
  if (!body.success) flags.push(_fpBanner(_fpEsc(B.noResult), '#e05555'));
  if (d.analysis_truncated) {
   139	# own effort, replacing its effectively-unbounded default.
   140	FIT_CANDIDATE_MAX_NFEV = 18000
   141	
   142	# Unit A1 (2026-09-29): NO wall-clock budget anywhere in the sweep. The
   143	# per-candidate 25 s, the 240 s sweep, the 60 s / 35 s proposal budgets, the
   144	# 15 s minimum-fit budget and the screen's share of the sweep all made Find
   145	# Peaks' ANSWER depend on server load (1-GTA C1s Scan_6: MG2 won or lost on
   146	# whether its fourth refit started before 25 s). Work is bounded by counts:
   147	# every candidate is screened once, SCREEN_TOP_K are deep-evaluated with
   148	# n_refits refits each, a proposal pass makes at most
   149	# PROPOSAL_MAX_PER_CANDIDATE × PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE attempts,
   150	# every fit is capped at FIT_CANDIDATE_MAX_NFEV / SCREEN_MAX_NFEV evaluations
   151	# and certified with at most CERTIFY_MAX_RESTARTS restarts. The page runs
   152	# Find Peaks as a polled job (/api/analyze/start), so no request waits on it.
   153	PROPOSAL_ENDPOINT_WARNING_BE = 1.0
   154	PROPOSAL_COINCIDENCE_BE = 0.5
   155	
   156	# Component treated as asymmetric during shape-aware slot disambiguation.
   157	ALPHA_SYMMETRY_THRESHOLD = 0.01      # DS / DS+G α, asym-GL asymmetry

exec
/bin/zsh -lc "node -e 'const fs=require(\"fs\"),vm=require(\"vm\"); const html=fs.readFileSync(\"templates/index.html\",\"utf8\");const code=html.slice(html.indexOf(\"const FP_POLL_INTERVAL_MS\"),html.indexOf(\"async function runFindPeaks()\"));async function probe(ms){let calls=0;const times=[0,ms];const ctx={Date:{now:()=>times.shift()??ms},document:{getElementById:()=>({})},_fpProgressText:()=>\"active progress\",setTimeout:fn=>fn(),fetch:async()=>({ok:true,json:async()=>++calls===1?{status:\"running\",candidate_index:6}:{status:\"done\",result:{winner:\"MG2\"}}})};vm.createContext(ctx);try{const result=await vm.runInContext(code+\"\\n_fpPollJob(\\\"test\\\")\",ctx);console.log(ms/1000,\"seconds:\",JSON.stringify(result),\"polls\",calls)}catch(e){console.log(ms/1000,\"seconds:\",e.message,\"polls\",calls)}}(async()=>{await probe(599000);await probe(601000)})()'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
599 seconds: {"status":"done","result":{"winner":"MG2"}} polls 2
601 seconds: This is taking unusually long — the analysis may have been lost. Try again. polls 1

exec
/bin/zsh -lc "rg -n 'FP_POLL_WATCHDOG_SEC|_fpPollJob' tests; nl -ba autofit/engine.py | sed -n '2738,2755p'; nl -ba tests/autofit/test_fit_certificate.py | sed -n '96,139p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
tests/test_browser_per_tab_state.py:230:                window._fpPollJob = () => new Promise(r => { window.__resolvePoll = r; });
  2738	            [m.name for m in candidates])
  2739	
  2740	    for idx, model in enumerate(candidates, 1):
  2741	        # Unit A1: every selected candidate is evaluated — no sweep budget
  2742	        n_evaluated += 1
  2743	        log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
  2744	        _report_progress(progress_cb, "stabilizing", idx, len(candidates),
  2745	                         model.name)
  2746	        # reuse the screen fit as this candidate's primary (no repeated work)
  2747	        primary = screen_fit.get(model.name) or fit_candidate(
  2748	            x, y, weights, model, fit_full_window=fit_full_window,
  2749	            endpoint_avg=endpoint_avg)
  2750	        if not primary.converged:
  2751	            non_converged.append((model, primary))
  2752	            continue
  2753	
  2754	        stability = run_stability_analysis(
  2755	            x, y, weights, model, primary,
    96	
    97	
    98	def test_a_fit_capped_at_the_minimum_is_certified():
    99	    """The Scan_6 case in general form: an optimiser that runs out of
   100	    evaluations while sitting at the minimum reports failure; the certificate
   101	    finds no descent and certifies it."""
   102	    x, y, w, model = _two_peak()
   103	    good = eng.fit_candidate(x, y, w, model)
   104	    assert good.converged
   105	    comp = eng._build_composite_model(model)
   106	    y_sub = y - good.background
   107	    capped = comp.fit(y_sub, good.lmfit_result.params.copy(), x=x, weights=w, method="leastsq",
   108	                      nan_policy="omit", max_nfev=3)          # starts AT the minimum, capped at once
   109	    assert not capped.success
   110	    point, certified = eng._certify_minimum(comp, y_sub, capped, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
   111	    assert certified
   112	    assert point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)
   113	
   114	
   115	def test_out_of_restarts_is_not_converged(monkeypatch):
   116	    """A start far from the minimum needs more than one restart to certify
   117	    (the first descends a long way); with a single restart allowed it is
   118	    'not converged' — whatever the optimiser says."""
   119	    x, y, w, model = _two_peak()
   120	    comp = eng._build_composite_model(model)
   121	    good = eng.fit_candidate(x, y, w, model)
   122	    y_sub = y - good.background
   123	    far = good.lmfit_result.params.copy()
   124	    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
   125	    short = comp.fit(y_sub, far, x=x, weights=w, method="leastsq", nan_policy="omit", max_nfev=2)
   126	    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 1)
   127	    _, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
   128	    assert not certified
   129	    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 5)
   130	    point, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
   131	    assert certified and point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)
   132	
   133	
   134	def test_the_warm_restart_is_gone():
   135	    src = inspect.getsource(eng.fit_candidate)
   136	    assert "retry" not in src and "WARM_RESTART" not in src
   137	    assert "converged=bool(certified)" in src

codex
The polling failure is reproduced with the page’s actual function: the same `running → done(MG2)` responses succeed at 599 seconds, but throw “Try again” at 601 seconds without reading the completed result. That is a MAJOR integration gap after removing the server budgets. The additional doublet, stability-consumer, and Bayesian tests passed: 44 tests total so far.

exec
/bin/zsh -lc "ps -axo pid,etime,command | rg 'python -c|SCAN6' | head -8" in /Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism
 succeeded in 0ms:
zsh:1: operation not permitted: ps

 succeeded in 227367ms:
/Users/skyefortier/.matplotlib is not a writable directory
SCAN6 True {'winner': 'MG2_graphAsymGL_aliph_sat_CO_C=O+preseed', 'conditional': True, 'conditional_reason': 'no_clean_survivor', 'winner_boundary_hits': ['contamination_C=O:fwhm@max', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@max'], 'winner_unphysical_widths': ['main_aliphatic:fwhm=2.00eV≥2.0eV ordinary cap (no known-broad justification)', 'contamination_C=O:fwhm=2.00eV≥2.0eV ordinary cap (no known-broad justification)'], 'winner_boundary_fixed_params': [], 'filtered_dominant_alternative': None, 'weighted_ic_disagreement': None, 'preseeded_features': [{'role': 'preseed_curvature_0', 'center_be': 283.161, 'amplitude_net': 6797.5, 'fraction_of_max': 0.125, 'local_snr': 68.9, 'fwhm_init': 0.59, 'provenance': 'curvature_shoulder', 'gates': {'min_fraction_of_max': 0.25, 'amplitude_snr': 5.0, 'note': 'UNVERIFIED engine tunables — pre-seeded slots are region-unassigned; assignment requires human review'}, 'prom_z': 30.76, 'augmented_into_grammar': True}], 'n_survivors': 6, 'n_filtered': 6, 'n_non_converged': 1, 'analysis_truncated': False, 'n_candidates_evaluated': 6, 'n_candidates_total': 30}
SCREEN 30

codex
The verdict is NO-GO because the page’s 600-second cutoff still makes result delivery depend on load. I found no additional shipping blocker in the certificate or §3 reasoning. The full-page Scan_6 check is still running; its winner will not change the polling finding.

codex
- **MAJOR — The browser still abandons valid analyses after 600 seconds.** [templates/index.html:16159](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/templates/index.html:16159), exposed by removing the sweep deadline at [autofit/engine.py:2741](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/autofit/engine.py:2741). This checks total elapsed time, even while progress continues. I executed the actual polling function with identical `running → done(MG2)` responses: at 599 seconds it delivers MG2; at 601 seconds it throws “Try again” before fetching completion. Thus sufficient server load changes the page’s outcome from a result to failure. The watchdog explicitly assumes the removed server budget exists. Replace this total-duration cutoff with job-liveness handling that permits long counted workloads.

- **MINOR — The clock-independence test never exercises screening.** [tests/autofit/test_preseed_dominants.py:430](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/tests/autofit/test_preseed_dominants.py:430). Its one-candidate grammar, with preseeding disabled, cannot enter the `> SCREEN_TOP_K` branch. Reintroducing a screen deadline would leave this test passing while loaded full-grammar requests lose candidates. Add a clock-jump case with more than six candidates and assert complete screening and refit counts.

The certificate follows the accepted rule: relative SciPy-default `ftol`, bounded `least_squares` restarts, lowest-χ² retention, and failure on non-finite or raising restarts. Independent zero-χ², higher-χ², exception, non-finite, relative-tolerance, and evaluation-cap probes passed. I found no remaining optimizer-success consumer or clock-controlled fitting decision in the engine paths reviewed.

**Validation:** 44 tests passed. The full-page Scan_6 configuration independently returned `MG2…+preseed`, screening all 30 candidates without truncation. The scope-report aggregate measurements reproduced.

**§3 is not itself a shipping blocker for A1 as specified.** The two screen regressions expose the existing single-start selection limitation; certification does not promise the globally best basin. The absent-slot change correctly removes credit previously caused by failed refits counting as empty. The disclosed arithmetic jitter is separate from the reproduced browser deadline failure.

VERDICT: NO-GO.
tokens used
99,667
- **MAJOR — The browser still abandons valid analyses after 600 seconds.** [templates/index.html:16159](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/templates/index.html:16159), exposed by removing the sweep deadline at [autofit/engine.py:2741](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/autofit/engine.py:2741). This checks total elapsed time, even while progress continues. I executed the actual polling function with identical `running → done(MG2)` responses: at 599 seconds it delivers MG2; at 601 seconds it throws “Try again” before fetching completion. Thus sufficient server load changes the page’s outcome from a result to failure. The watchdog explicitly assumes the removed server budget exists. Replace this total-duration cutoff with job-liveness handling that permits long counted workloads.

- **MINOR — The clock-independence test never exercises screening.** [tests/autofit/test_preseed_dominants.py:430](/Users/skyefortier/xps-app/.claude/worktrees/fix-find-peaks-determinism/tests/autofit/test_preseed_dominants.py:430). Its one-candidate grammar, with preseeding disabled, cannot enter the `> SCREEN_TOP_K` branch. Reintroducing a screen deadline would leave this test passing while loaded full-grammar requests lose candidates. Add a clock-jump case with more than six candidates and assert complete screening and refit counts.

The certificate follows the accepted rule: relative SciPy-default `ftol`, bounded `least_squares` restarts, lowest-χ² retention, and failure on non-finite or raising restarts. Independent zero-χ², higher-χ², exception, non-finite, relative-tolerance, and evaluation-cap probes passed. I found no remaining optimizer-success consumer or clock-controlled fitting decision in the engine paths reviewed.

**Validation:** 44 tests passed. The full-page Scan_6 configuration independently returned `MG2…+preseed`, screening all 30 candidates without truncation. The scope-report aggregate measurements reproduced.

**§3 is not itself a shipping blocker for A1 as specified.** The two screen regressions expose the existing single-start selection limitation; certification does not promise the globally best basin. The absent-slot change correctly removes credit previously caused by failed refits counting as empty. The disclosed arithmetic jitter is separate from the reproduced browser deadline failure.

VERDICT: NO-GO.
