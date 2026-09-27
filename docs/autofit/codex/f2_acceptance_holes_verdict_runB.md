OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e18f-a3b0-7763-a7c3-1a4cd905735b
--------
user
Review unit F2 (holes in the acceptance rule): branch fix-acceptance-holes, git diff main..HEAD (fitting.py, templates/index.html, tests/test_fit_acceptance_holes.py, tests/test_basinhopping_outcome.py, tests/test_fit_reproducibility.py, tests/js/fit_acceptance.test.js, tests/js/stale_statistics.test.js, tests/js/autofit_required.test.js, tests/js/local_lm_descent.test.js, CLAUDE.md, docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

OWNER'S BRIEF (verbatim): "nothing is a fit unless it converged and is determined: basinhopping success from the real scipy result; a NaN in an /api/fit reply is a failed fit with a message, not a local fallback; n_free > n_data is refused as undetermined; the required verdict requires a converged refit."
Owner decisions since (verbatim in the plan, section 2): basinhopping is verified by refinement AND competes with a plain least_squares fit from the same start (the full DE pattern), because scipy's own flag failed 23 of 24 sampled fits that sit at Trust-Region's minimum; refusal at n_free >= n_data (equality accepted); an unconverged required-refit blocks the Auto-Fit anchor.

NOTE — ALSO IN THIS UNIT, BY OWNER INSTRUCTION: BASINHOPPING RUNS NO PERTURBED RESTARTS. Measured with the page's request (n_perturb 3) after the refinement change: 14 of 16 multi-component targets exceeded the production server's 300 s timeout (median 386 s, max 1066 s); without the restarts median 96 s, max 256 s, chi2r identical to 1e-8 on all 16. run_fit skips the perturb loop for basinhopping only. Review that change like the rest.

Out of scope (reported separately, docs/findings/2026-09-26-public-request-ceiling.md; do NOT treat as a finding against F2): the public URL's Cloudflare 524 ceiling between 88 s and 125 s.

PLAN SECTIONS 1-3 (sites, decisions, measurements), verbatim:

## 1. Sites

| # | hole | site | before | after |
|---|---|---|---|---|
| 1 | basinhopping always "converged" (H2) | `fitting.fit_model` → new `_basinhopping_candidate` | lmfit sets `success = True` before minimising and its basinhopping never reads scipy's result | the DE pattern in full (owner decision, §2): search → unconditional `least_squares` refinement from its point under the request's bounds (the refinement's convergence is the verdict; no χ² comparison, no tolerance) → competition with a `least_squares` fit from the same start (verified beats unverified, then lower χ²). An unverifiable search is `success: false` with its own message. `fit_model` is the ONE fitter, so the main fit, every perturbed restart and the required refit all go through it; scattered starts do not run for basinhopping. |
| 2 | a 2xx `/api/fit` reply with NaN switched to the local engine (M1) | page `_readFitReply` (new), used by `runFit` and `runAutoFitC1sGraphite` (the only two `/api/fit` callers) | `resp.json()` threw a SyntaxError, which `_asTransport` classified as a transport failure → `runFitLocal` replaced the server's converged result, verdicts and starts evidence | the body is read as text (a failure THERE is transport: the connection dropped) and parsed by the page; a body that was read but is not JSON is the server's reply → `serverError`, a failed fit with its message ("contains a non-finite number (NaN or Infinity) …" / "could not be read"), previous peaks and result kept, no fallback. Auto-Fit fails closed with the same message (it used to say "failed to converge or produced an unphysical graphite position"). The server is unchanged: the page, not a sanitiser, decides that a non-finite reply is not a fit. |
| 3 | n_data ≤ n_free read as a near-perfect, fully supported fit (M2) | `fitting.run_fit` before the fit; page `runFitLocal` after its free-parameter list | lmfit `redchi = χ²/max(1, nfree)`; the support / required F tests clamp dof to 1; the local engine clamps too | refused: `ValueError` "not determined by these data: N free parameters for M data points leaves no degrees of freedom …" (HTTP 400 on `/api/fit`; the same message through Find Peaks' refit, `/api/analyze`); the local engine fails with the same text, nothing written. A COUNT, not a threshold. Refused at n_free ≥ n_data (§2). |
| 4 | the required verdict ignored its refit's convergence (M3) | `fitting._component_required`; page `applyAutoFitResult` | `required` computed whether or not the refit converged (a refit stopped early read "required", F 992, for a redundant anchor); the page never read `refit_converged` | an unconverged refit returns `required: null, f: null, refit_converged: false, reason: "refit_not_converged"` (+ the solver message); Auto-Fit REFUSES that anchor before any charge-correction input is touched (red notice) — an anchor whose necessity could not be established must not set the energy reference of the whole spectrum. A check that did not RUN at all (older server, exception, nothing left, main fit not converged) still never blocks, as documented. |

| 5 | Auto-Fit parsed a non-2xx reply (owner, 2026-09-27) | page `runAutoFitC1sGraphite` | a Cloudflare 524 or gunicorn 500 reached `_readFitReply` and read as "the server's reply could not be read" — F2's own message misfiring | `resp.ok === false` is a failed REQUEST with its status in the message ("Auto-fit failed: Fit request failed (HTTP 524)."; a JSON `error` body's text when there is one), before any parsing, as Run Fit has done since A0 |

## 2. Decisions

- **Basinhopping (owner, 2026-09-26).** The brief said "success from the real
  scipy result". Measured first (scipy's flag recorded by a pass-through
  wrapper around the name lmfit calls): on a 1-in-8 sample of the 202
  committed targets (24 of 26 run), scipy marks **23 of 24** basinhopping fits
  failed — BFGS "Desired error not necessarily achieved due to precision
  loss" — while their χ²ᵣ equals Trust-Region's from the same start (median
  relative difference 1.3e-9; one 0.14 % worse; several better). Taken
  literally the method would fail on almost every correct fit. Owner chose:
  verify by refinement AND compete with a plain `least_squares` fit from the
  same start — the guarantee differential evolution already has ("never worse
  than the default method from the same start"). The wrapper was removed; no
  monkeypatching remains.
- **n_free = n_data is refused too.** The brief says "n_free > n_data". At
  equality there are zero degrees of freedom: the model interpolates every
  point, reduced χ² is undefined (lmfit divides by max(1, 0)) and the F tests
  run on a clamped dof of 1 — the same fault as the sweep's reproduction. The
  refusal is at n_free ≥ n_data; one degree of freedom is fitted as before.
- **An unconverged required-refit blocks Auto-Fit.** "The required verdict
  requires a converged refit": the server gives no verdict, and the page does
  not let an anchor with no verdict set the charge reference. The documented
  "a check that did not run never blocks" is kept for checks that did not
  run.

- **No perturbed restarts for basinhopping (owner, 2026-09-26).** Measured
  after the refinement change, with the page's request (`n_perturb` 3), on 16
  committed multi-component targets spread over 2–7 components (4 processes,
  8 physical cores — production runs 4 workers): median 386 s, max 1066 s,
  **14 of 16 over the 300 s server timeout**. Without the restarts: median
  96 s, max 256 s, none over 300 s, and χ²ᵣ identical on all 16 (worst
  relative difference 1e-8) — a global search gains nothing from them, the
  reason the scattered-starts check already excludes basinhopping and DE.
  `run_fit` skips the perturb loop for basinhopping (the request's
  `n_perturb` is still hashed into the seed; nothing else changes). DE keeps
  its restarts (2–75 s; not in the brief).

## 3. Measurements

| measurement | before F2 | after F2 |
|---|---|---|
| basinhopping, 1-in-8 sample of the 202 targets (26), `n_perturb` 0 | lmfit `success: true` on all (unconditional); scipy's own flag "failed" on 23 of 24 (BFGS precision loss) at Trust-Region's minimum | 26 of 26 verified; never worse than Trust-Region from the same start; up to 19 % lower χ²ᵣ; median relative difference −1.9e-10 |
| basinhopping wall time, page request, 16 multi-component targets | — | with restarts: median 386 s, max 1066 s, 14/16 > 300 s → restarts skipped: median 96 s, max 256 s, 0/16 > 300 s |

The public URL has a lower ceiling (Cloudflare 524 between 88 s and 125 s):
5 of those 16 still exceed it without restarts. Reported separately, not
fixed here: `docs/findings/2026-09-26-public-request-ceiling.md`.


TRY TO BREAK
a. _basinhopping_candidate: is every basinhopping minimisation (main fit, required refit, anything else that calls fit_model) verified; can an unverified search ever be returned with success true; does the competitor ever get the search's generated state instead of the request's start and bounds; seeding (the search seeded, the two least_squares not; the request seed unchanged; n_perturb still hashed); the 'aborted' case; the message returned; the result's params/stderr/bounds vs what the page stores; a linked (expr) parameter across the refinement; nan_policy.
b. The restart skip: anything else keyed on n_perturb (the seed, perturb_rng stream alignment for OTHER methods, the response, /api/analyze), DE unchanged, the page still sending n_perturb 3.
c. _readFitReply and Auto-Fit's new resp.ok check (site 5): is every 2xx /api/fit body read through it (Run Fit, alternative adoption, Auto-Fit) and every non-2xx one reported with its status before any parsing; can a truncated body (network) be misclassified as a server error or vice versa; the non-finite regex on a body where 'NaN' appears inside a string; the error path's message; _asTransport no longer reachable with a SyntaxError from the fit reply; resp.ok false paths unchanged; Auto-Fit's catch.
d. Determinacy refusal: count vs lmfit's nvarys (expr parameters, fixed parameters, the DE box, n_starts, the required refit's reduced model), NaN / non-finite y excluded consistently with nan_policy omit, the local engine's count vs its dof (caM held, discrete), Batch Fit's per-target message, Find Peaks' refit (/api/analyze) surfacing the ValueError, Auto-Fit.
e. Required: _component_required's new branch vs the existing non-finite branch; the page's refusal ordering (before any charge-correction input); required null from other reasons still non-blocking; the Python twin in autofit/* if any reads 'required'.
f. Tests: real, non-vacuous (would each fail without its fix?); the edited existing tests still test what they tested.
g. Docs vs code vs measurements (CLAUDE.md, plan).

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll review the diff and surrounding call paths, then check the failure cases most likely to violate the acceptance rule. I’ll keep this read-only and finish with ranked findings and a verdict.
exec
/bin/zsh -lc 'git diff main..HEAD -- fitting.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-G8Xb2j9P' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-14FSjAYD' (errno=Operation not permitted)
diff --git a/fitting.py b/fitting.py
index 03a6690..c8cdff6 100644
--- a/fitting.py
+++ b/fitting.py
@@ -1128,6 +1128,50 @@ def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws)
 # options.fit_method straight to run_fit, and lmfit also understands e.g.
 # "ampgo", "dual_annealing" and "BasinHopping", which would run with
 # numpy's global generator, unseeded.
+# ── basinhopping: verified by refinement (unit F2, 2026-09-26) ─────────────
+# lmfit 1.3 sets MinimizerResult.success = True before minimising and its
+# basinhopping never reads scipy's result, so a basinhopping fit always
+# "converged" (sweep H2). scipy's own flag is no better a verdict: on 23 of 24
+# sampled committed targets it reports the lowest local minimisation as failed
+# (BFGS "Desired error not necessarily achieved due to precision loss") while
+# the point equals Trust-Region's minimum (median relative chi2r difference
+# 1e-9). Owner decision 2026-09-26: the DE pattern, in full. Basinhopping
+# searches; an UNCONDITIONAL least_squares refinement from its point under the
+# request's bounds decides — a refinement that converged IS the candidate (no
+# chi-square comparison with the search, no tolerance: the DE unit's lesson);
+# then that candidate competes with a least_squares fit from the same start
+# (verified beats unverified, then the lower chi-square), so basinhopping is
+# never worse than the default method from the same start.
+def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
+    nan_policy = kws.get("nan_policy", "omit")
+    start = params.copy()
+    for name, (lo, hi) in requested.items():
+        start[name].set(min=lo, max=hi)
+    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws)
+    candidate = None
+    try:   # from wherever the search stopped, even an evaluation-budget abort (as DE)
+        refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
+                            method="least_squares", nan_policy=nan_policy)
+        if refined.success:
+            candidate = refined
+    except Exception:
+        log.debug("basin-hopping refinement raised", exc_info=True)
+    if candidate is None:
+        # the search's point could not be verified: it is not a converged fit
+        found.success = False
+        found.message = ("basin-hopping: the local refinement from the point it found did not converge, "
+                         "so the result is not a verified fit")
+        candidate = found
+    try:
+        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy)
+    except Exception:
+        log.debug("local candidate from the start raised", exc_info=True)
+        return candidate
+    if local.success and (not candidate.success or local.chisqr < candidate.chisqr):
+        return local
+    return candidate
+
+
 _FIT_METHODS = ("leastsq", "least_squares", "nelder", "differential_evolution", "basinhopping")
 _STOCHASTIC_METHODS = ("differential_evolution", "basinhopping")
 
@@ -1407,6 +1451,14 @@ def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weigh
             start[name].set(expr=par.expr)
     refit = fit_reduced(start)
     chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
+    if not refit.success:
+        # F2 (2026-09-26): a refit that did not converge establishes nothing
+        # either way — its chi-square is wherever the optimiser stopped (a
+        # redundant anchor read "required", F 992, from a refit stopped early;
+        # F 1.17 once it completed). No verdict; the caller decides.
+        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
+                "refit_converged": False, "reason": "refit_not_converged",
+                "message": str(getattr(refit, "message", "") or "")[:200]}
     delta = chi2_without - chi2_with
     p = max(1, int(n_free_comp))
     dof = max(1, len(y_sub) - int(n_free_total))
@@ -1648,6 +1700,22 @@ def run_fit(
     if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
         raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")
 
+    # ── Determinacy (unit F2, 2026-09-26) ─────────────────────────────────────
+    # "Nothing is a fit unless it converged and is determined." With at least
+    # as many free parameters as data points the model can pass through every
+    # point: lmfit reports redchi = chi2 / max(1, nfree) as if it were a fit,
+    # and the support / required F tests clamp their dof to 1, so such a model
+    # read as a near-perfect, fully supported fit (sweep M2: 6 points, 2 GL
+    # components, chi2r 2.8e-6, both "supported"). A count, not a threshold:
+    # zero or negative degrees of freedom is refused outright.
+    n_free_request = sum(1 for par in all_params.values() if par.vary and not par.expr)
+    n_data_request = int(np.count_nonzero(np.isfinite(y_sub)))
+    if n_free_request >= n_data_request:
+        raise ValueError(
+            f"The model is not determined by these data: {n_free_request} free parameters for "
+            f"{n_data_request} data points leaves no degrees of freedom. Widen the fitted range, "
+            f"remove components or lock parameters.")
+
     # ── Fit ───────────────────────────────────────────────────────────────────
     kws = {"method": "leastsq", "nan_policy": "omit"}
     if fit_kws:
@@ -1676,6 +1744,9 @@ def run_fit(
         if kws.get("method") == "differential_evolution":
             bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
             return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
+        if kws.get("method") == "basinhopping":
+            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
+            return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
         return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))
 
     def fit_once(params):
@@ -1707,7 +1778,13 @@ def run_fit(
                       f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)
 
     # ── Perturb and refit to escape local minima ─────────────────────────
-    if n_perturb > 0 and result.success:
+    # Not for basinhopping (unit F2, 2026-09-26, owner): it is already a global
+    # search, so perturbed restarts add nothing — the reason the scattered-
+    # starts check excludes it — and with the page's n_perturb 3 they
+    # quadrupled its time past the server's 300 s timeout on 14 of 16 sampled
+    # multi-component targets (median 386 s, max 1066 s; without them median
+    # 96 s, max 256 s, and chi2r identical to 1e-8 on all 16).
+    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
         best_result = result
         best_redchi = result.redchi if result.redchi is not None else float('inf')
         rng = perturb_rng

exec
/bin/zsh -lc 'git diff main..HEAD -- templates/index.html' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-q6EKaQEy' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2aw6w4l6' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index fedb356..c5d62fd 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7306,6 +7306,14 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
     notify('Auto-fit: the Graphite component is not required by the data — refitting the other components without it fits the data as well' + (req.f != null ? ' (F = ' + Number(req.f).toFixed(1) + ', threshold 10)' : '') + '. No charge correction was derived from it and the fit was not applied. The model gives the other components enough freedom to absorb the graphite line; lock or narrow them and try again.', 'red', true);
     return false;
   }
+  // F2 (2026-09-26): the refit without the anchor did not converge, so the
+  // server could not establish that the anchor is required. The anchor would
+  // set the energy reference of the whole spectrum: refused, like a
+  // redundant one (a check that did not RUN at all still never blocks).
+  if (req && req.ran === true && req.refit_converged === false) {
+    notify('Auto-fit: it could not be established that the data require the Graphite component — refitting the other components without it did not converge. No charge correction was derived from it and the fit was not applied. Try Run Fit, or narrow the ROI, and run Auto-Fit again.', 'red', true);
+    return false;
+  }
   if (!_autoFitGraphiteIsSupported(gPeak, json)) {
     notify('Auto-fit: the data do not support the Graphite component (removing it does not worsen the fit), so no charge correction was derived from it and the fit was not applied.', 'red', true);
     return false;
@@ -7397,6 +7405,25 @@ function applyAutoFitResult(json, graphiteRaw, roi) {
 }
 
 // Top-level entry point. Wired to the Actions menu item.
+// Read a 2xx /api/fit reply (unit F2, 2026-09-26). A failure to READ the body
+// is a transport failure (the caller may fall back to the local engine); a
+// body that was read but is not JSON is the SERVER's reply, so it is a failed
+// fit with a message — never a reason to switch engines. The case seen: an
+// uncertainty that could not be computed, serialised as NaN (Flask writes
+// NaN / Infinity tokens, which JSON.parse rejects).
+async function _readFitReply(resp) {
+  const text = await resp.text();                 // rejects only on transport
+  try { return JSON.parse(text); } catch (_) {
+    const nonFinite = /(^|[\[,:\s])(-?Infinity|NaN)([\],\x7d\s]|$)/.test(text);   // \x7d = closing brace
+    const err = new Error(nonFinite
+      ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
+      : 'The server\'s reply could not be read. The fit is treated as failed.');
+    err.serverError = true;
+    err.unreadableReply = true;
+    throw err;
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7528,7 +7555,17 @@ async function runAutoFitC1sGraphite() {
       signal: ctrl.signal,
     });
     clearTimeout(timer);
-    const json = await resp.json();
+    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
+    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
+    // reach the parser and read as "the server's reply could not be read")
+    if (resp.ok === false) {
+      let msg = null;
+      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
+      err.httpStatus = resp.status;
+      throw err;
+    }
+    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
@@ -7565,6 +7602,8 @@ async function runAutoFitC1sGraphite() {
     let msg;
     if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
       msg = 'Auto-fit exceeded the 2-minute timeout.';
+    } else if (e && (e.unreadableReply || e.httpStatus)) {
+      msg = 'Auto-fit failed: ' + e.message;
     } else if (e && e.message) {
       msg = 'Fit failed to converge or produced an unphysical graphite position.';
       console.warn('Auto-fit error:', e);
@@ -7976,8 +8015,9 @@ async function runFit(opts = {}) {
     // and leaves the model untouched (unit A0: nothing is shown as a fit
     // result unless it converged; an HTTP 400 is not a reason to silently
     // switch engines).
-    // Only a genuine transport failure (network rejection, abort, unparsable
-    // 2xx body) is marked for fallback; server errors carry `serverError`.
+    // Only a genuine transport failure (network rejection, abort, a body that
+    // could not be read) is marked for fallback; server errors — including a
+    // 2xx body that was read but is not JSON (F2) — carry `serverError`.
     const _asTransport = (e) => {
       if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
       throw e;
@@ -8009,7 +8049,9 @@ async function runFit(opts = {}) {
       err.serverError = true;
       throw err;
     }
-    try { json = await resp.json(); } catch (e) { _asTransport(e); }
+    // F2: reading the body can fail in transport; a body that was read but is
+    // not JSON is the server's reply — a failed fit, not a fallback
+    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
     if (json.error) {
       const err = new Error(json.error);
       err.serverError = true;
@@ -8320,6 +8362,13 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     }
   }
   if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');
+  // F2 (2026-09-26): with at least as many free parameters as data points the
+  // model passes through every point and reads as a near-perfect fit (the
+  // dof below is clamped to 1) — refused, as the server refuses it. A count.
+  if (freeParams.length >= be.length) {
+    return fail('the model is not determined by these data: ' + freeParams.length + ' free parameters for ' +
+                be.length + ' data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.');
+  }
 
   // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
   // (owner decision 2026-09-18: zero allowed in both engines; a component at

exec
/bin/zsh -lc 'git diff main..HEAD -- tests/test_fit_acceptance_holes.py tests/test_basinhopping_outcome.py tests/test_fit_reproducibility.py tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/autofit_required.test.js tests/js/local_lm_descent.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
les.py
new file mode 100644
index 0000000..3a0800f
--- /dev/null
+++ b/tests/test_fit_acceptance_holes.py
@@ -0,0 +1,103 @@
+"""Unit F2 (2026-09-26): holes in the acceptance rule — "nothing is a fit
+unless it converged and is determined".
+
+- A model with at least as many free parameters as data points is refused as
+  undetermined (it read as a near-perfect, fully supported fit: sweep M2).
+- The required-anchor verdict needs a CONVERGED refit (sweep M3): an
+  unconverged refit gives no verdict.
+
+The basinhopping outcome (sweep H2) and the page's handling of a NaN reply
+(sweep M1) are pinned in tests/test_basinhopping_outcome.py and
+tests/js/fit_acceptance.test.js.
+"""
+
+import io
+from types import SimpleNamespace
+
+import numpy as np
+import pytest
+from lmfit import Parameters
+
+import fitting
+from app import create_app
+
+
+def _gl(x, c, a, w):
+    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
+
+
+def _two_gl_specs():
+    # two GL components, every parameter free: centre, fwhm, amplitude, gl mix = 8
+    return [
+        {"id": "1", "shape": "pseudo_voigt_gl", "center": 284.5, "fwhm": 1.0, "amplitude": 1000.0,
+         "gl_ratio": 0.3, "fix_gl_ratio": False, "amplitude_min": 0},
+        {"id": "2", "shape": "pseudo_voigt_gl", "center": 286.0, "fwhm": 1.0, "amplitude": 400.0,
+         "gl_ratio": 0.3, "fix_gl_ratio": False, "amplitude_min": 0},
+    ]
+
+
+def _data(n):
+    x = np.linspace(283.0, 288.0, n)
+    y = 100.0 + _gl(x, 284.5, 1000.0, 1.0) + _gl(x, 286.0, 400.0, 1.0)
+    return x, y
+
+
+@pytest.mark.parametrize("n", [6, 8])          # the sweep's reproduction (6 < 8) and zero dof (8 = 8)
+def test_no_degrees_of_freedom_is_refused_as_undetermined(n):
+    x, y = _data(n)
+    with pytest.raises(ValueError, match=r"not determined by these data: 8 free parameters for %d data points" % n):
+        fitting.run_fit(x, y, _two_gl_specs(), background_method="none", fit_kws={"method": "least_squares"})
+
+
+def test_one_degree_of_freedom_is_still_a_fit_and_linked_or_locked_parameters_do_not_count():
+    x, y = _data(9)                              # 8 free, 9 points: dof 1 — determined, fitted as before
+    res = fitting.run_fit(x, y, _two_gl_specs(), background_method="none", fit_kws={"method": "least_squares"})
+    assert res["statistics"]["n_free_params"] == 8
+    # locking the mixes leaves 6 free: 7 points are then enough
+    x7, y7 = _data(7)
+    specs = _two_gl_specs()
+    for s in specs:
+        s["fix_gl_ratio"] = True
+    res = fitting.run_fit(x7, y7, specs, background_method="none", fit_kws={"method": "least_squares"})
+    assert res["statistics"]["n_free_params"] == 6
+
+
+@pytest.fixture()
+def client(tmp_path):
+    app = create_app(upload_folder=str(tmp_path))
+    app.config["TESTING"] = True
+    with app.test_client() as c:
+        yield c
+
+
+def test_api_fit_returns_the_refusal_as_a_400_with_its_message(client):
+    x, y = _data(6)
+    csv = "\n".join(f"{a:.4f},{b:.2f}" for a, b in zip(x, y))
+    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "tiny.csv")}).get_json()["session_id"]
+    resp = client.post("/api/fit", json={"session_id": sid, "background": {"method": "none"},
+                                         "peaks": _two_gl_specs(), "fit_method": "least_squares"})
+    assert resp.status_code == 400
+    assert "not determined by these data" in resp.get_json()["error"]
+
+
+def test_an_unconverged_refit_gives_no_required_verdict():
+    """The sweep's reproduction: a refit stopped early read required: true
+    (F 992) for an anchor that is redundant (F 1.17 once the refit completes)."""
+    params = Parameters()
+    params.add("p1_amplitude", value=1.0)
+    params.add("p2_amplitude", value=1.0)
+    y_sub = np.ones(50)
+    stopped = SimpleNamespace(success=False, chisqr=992.0, message="max evaluations reached")
+    out = fitting._component_required(lambda p: stopped, params, ["p1_"], y_sub, np.ones(50),
+                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
+    assert out["required"] is None
+    assert out["f"] is None
+    assert out["refit_converged"] is False
+    assert out["reason"] == "refit_not_converged"
+    assert "max evaluations" in out["message"]
+    # a converged refit still gives its verdict, unchanged
+    done = SimpleNamespace(success=True, chisqr=1.0 + 1.17 / 48, message="ok")
+    out = fitting._component_required(lambda p: done, params, ["p1_"], y_sub, np.ones(50),
+                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
+    assert out["refit_converged"] is True and out["required"] is False
+    assert out["f"] == pytest.approx(1.17)
diff --git a/tests/test_fit_reproducibility.py b/tests/test_fit_reproducibility.py
index 9ca3a77..31809a2 100644
--- a/tests/test_fit_reproducibility.py
+++ b/tests/test_fit_reproducibility.py
@@ -158,8 +158,12 @@ def _two_peaks():
     return x, y, specs
 
 
-@pytest.mark.parametrize("method,n_perturb", [("differential_evolution", 2), ("basinhopping", 1)])
-def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(monkeypatch, method, n_perturb):
+# basinhopping runs no perturbed restarts since unit F2 (a global search; the
+# restarts took it past the 300 s timeout): one seeded minimisation per fit.
+# That each further minimisation (the required refit) gets its own population
+# is pinned in tests/test_component_required.py.
+@pytest.mark.parametrize("method,n_perturb,n_min", [("differential_evolution", 2, 3), ("basinhopping", 1, 1)])
+def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(monkeypatch, method, n_perturb, n_min):
     # lmfit passes seed=None to both, i.e. numpy's GLOBAL generator: another
     # request in the same worker, or a restart, changed the answer.
     records = _spy_on_fits(monkeypatch)
@@ -169,9 +173,9 @@ def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(m
         records.append([])
         fitting.run_fit(x, y, specs, background_method="linear", n_perturb=n_perturb, fit_kws={"method": method})
     seeds = [[r["seed"] for r in run if r["method"] == method] for run in records]
-    assert len(seeds[0]) == n_perturb + 1
+    assert len(seeds[0]) == n_min
     assert all(isinstance(s, int) for s in seeds[0])
-    assert len(set(seeds[0])) == n_perturb + 1       # each minimisation its own population
+    assert len(set(seeds[0])) == n_min               # each minimisation its own population
     assert seeds[0] == seeds[1]                      # and the same ones on every press
     # the local refinement / local candidate never receives a solver seed
     assert all(r["seed"] is None for run in records for r in run if r["method"] != method)
@@ -314,8 +318,11 @@ def test_a_differently_cased_method_name_is_the_same_seeded_method(monkeypatch):
     records.append([])
     x, y, specs = _two_peaks()
     res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "BasinHopping"})
-    assert [r["method"] for r in records[0]] == ["basinhopping"]
+    # F2 (2026-09-26): the seeded search, then its refinement and the competing
+    # fit from the start (least_squares: deterministic, carry no seed)
+    assert [r["method"] for r in records[0]] == ["basinhopping", "least_squares", "least_squares"]
     assert isinstance(records[0][0]["seed"], int)
+    assert records[0][1]["seed"] is None and records[0][2]["seed"] is None
     assert res["random_seed"] == fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                                                  fit_kws={"method": "basinhopping"})["random_seed"]
 

exec
/bin/zsh -lc "sed -n '1020,1135p' fitting.py; sed -n '1370,1505p' fitting.py; sed -n '1505,1825p' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
            continue
        if name.endswith("_amplitude"):
            width = max(10.0 * y_top, 2.0 * abs(par.value), 1.0)
            lo, hi = -width, width
        elif name.endswith("_center"):
            width = span
            lo, hi = min(x_lo, par.value), max(x_hi, par.value)
        else:
            raise ValueError(
                f"differential_evolution needs finite bounds for '{name}'")
        new_min = lo if open_min else par.min
        new_max = hi if open_max else par.max
        # A bound the request did set can sit at or beyond the generated
        # side (centre_min = 300 on a 280-290 eV ROI): keep a real interval.
        if open_max and new_max <= new_min:
            new_max = new_min + width
        if open_min and new_min >= new_max:
            new_min = new_max - width
        par.set(min=new_min, max=new_max)
        generated[name] = {side: width for side, is_open in (("min", open_min), ("max", open_max)) if is_open}
    return generated


def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
    """One differential-evolution candidate: search inside a generated box,
    then refine FROM that solution with ``least_squares`` under the request's
    own (open) bounds.

    Whenever a side was generated the refinement is unconditional (a request
    that bounds everything itself is returned as found). A box can shape the answer without the
    solution lying anywhere near a side (centre and width compensate for a
    capped amplitude), and an unrefined boundary candidate can lose the
    perturb loop's comparison to a worse interior one, so every candidate is
    freed from the box before it is compared or returned. The refined fit
    replaces the search result whenever it converged; if it did not (or
    raised) the search result is returned marked
    ``box_unverified`` (with the sides we generated, so they are not
    reported as bounds) and ``run_fit`` does not call it a success.
    """
    # ``params`` may come from an earlier candidate and still carry that
    # candidate's generated sides: always start from the request's bounds.
    boxed = params.copy()
    for name, (lo, hi) in requested.items():
        boxed[name].set(min=lo, max=hi)
    generated = _finite_search_box(boxed, x, y_sub)
    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
    found.box_unverified, found.search_box = bool(generated), generated
    if not generated:
        return found
    free = found.params.copy()
    for name in generated:
        free[name].set(min=requested[name][0], max=requested[name][1])
    # Only what a local solver understands: DE options (seed, popsize, ...)
    # passed through fit_kws would make least_squares raise.
    refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
    try:
        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
    except Exception:
        log.debug("refinement outside the search box raised", exc_info=True)
        return found
    # A converged refinement IS the result: it is a least_squares fit of the
    # requested model under the requested bounds, which is what the default
    # method returns and the acceptance rule accepts. It is deliberately NOT
    # compared with the boxed search's chi-square. least_squares descends
    # from its start, so it cannot end materially above it (four review
    # rounds found no reachable case), but it does end a hair above an EXACT
    # start that sits on a requested bound (the bound transform is degenerate
    # there; the centre moves ~1e-7 eV), by an amount that depends on peak
    # width, position and counts. Every tolerance tried for that comparison
    # produced reachable false failures and no reachable protection.
    if refined.success:
        refined.box_unverified, refined.search_box = False, {}
        return refined
    return found


def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws):
    """A differential-evolution candidate that is never worse than the
    default method from the same start.

    Differential evolution ignores the starting values. On a needle-narrow
    peak in a wide box it can converge, "successfully", with the component
    outside the fitted range (chi-square 1e7 where ``least_squares`` from the
    request's start reaches 1e-4), and the refinement has nothing to descend
    to from there. So a ``least_squares`` fit from the candidate's own start,
    under the request's bounds, competes with the search: a verified result
    beats an unverified one, then the lower chi-square wins.
    """
    searched = _search_then_refine(model, params, requested, y_sub, x, weights, kws)
    start = params.copy()
    for name, (lo, hi) in requested.items():
        start[name].set(min=lo, max=hi)
    try:
        local = model.fit(y_sub, start, x=x, weights=weights,
                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"))
    except Exception:
        log.debug("local candidate from the start raised", exc_info=True)
        return searched
    if not local.success:
        return searched
    local.box_unverified, local.search_box = False, {}
    if searched.box_unverified or not searched.success or local.chisqr < searched.chisqr:
        return local
    return searched


# The methods run_fit accepts, and the two of them that draw random numbers.
# Validated HERE, not only in the /api/fit route: /api/analyze forwards
# options.fit_method straight to run_fit, and lmfit also understands e.g.
# "ampgo", "dual_annealing" and "BasinHopping", which would run with
# numpy's global generator, unseeded.
# ── basinhopping: verified by refinement (unit F2, 2026-09-26) ─────────────
# lmfit 1.3 sets MinimizerResult.success = True before minimising and its
# basinhopping never reads scipy's result, so a basinhopping fit always
# "converged" (sweep H2). scipy's own flag is no better a verdict: on 23 of 24
# sampled committed targets it reports the lowest local minimisation as failed
    return {
        "ran": True, "n_run": n_starts, "n_converged": n_converged, "n_same_as_fit": n_same,
        # solutions that are NOT better: counted, never listed (they are what a bad start looks like)
        "n_in_alternatives": sum(c["n_starts"] for c in lower),
        "n_not_better_elsewhere": sum(c["n_starts"] for c in other),
        "not_better_chi2r": sorted(c["chi2r"] for c in other),
        "fit": {"chi2r": fit_chi, "largest_centre_shift_from_start": _largest_shift(fit_comps),
                "components": [{k: c[k] for k in ("id", "area_percent", "center_shift_from_start")} for c in fit_comps]},
        "alternatives": lower,
    }


# ── "Not supported by the data": the one statement that needs no intensity floor
# (six were tried for the Auto-Fit anchor and each rejected real components or
# accepted residue). With the OTHER components held at their fitted values,
# taking this component out of the model must make the fit to the data
# significantly worse:
#     chi2_with    = sum w (y - fitted)^2          w = the fit's own weights
#     chi2_without = sum w (y - fitted + component)^2
#     F = ((chi2_without - chi2_with) / p) / (chi2_with / dof)
# A component driven to its amplitude floor, pinned on a bound or fitted to
# numerical residue has chi2_without <= chi2_with (removing it costs nothing).
# Owner decision 2026-09-18: such a component is an explicit OUTCOME — the fit
# did not determine it — and its centre, width and sigma are not reported.
# Known limits, same as the Auto-Fit anchor: a gross single-channel artefact
# inflates chi2_with and can mark a real component unsupported; redundancy
# under overlap is NOT detected (a refit without the component is the test for
# that; step (c) does it for the Auto-Fit anchor). Threshold F >= 10 (~ p 1e-9
# at these sizes); on the 202 committed targets resolved components have
# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
# they were refitted still passes. The test for that is the refit itself:
# remove the component, refit the rest from their fitted values under the
# request's own bounds, and compare the fit to the data with and without it:
#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
# p = the component's free parameters, dof = n - nvarys of the full model.
# One extra fit, so it is done only when asked for (Auto-Fit asks for its
# charge-reference anchor: an anchor that is not required must not set the
# energy reference of a whole spectrum). Same threshold as `support`.
def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
    """``fit_reduced(params)`` is the run's own fitter for the reduced model
    (the same candidate machinery and seeding the fit used, so differential
    evolution's box/refinement and the request seed apply to the refit too).
    ``removed_prefixes`` is the removed component AND everything linked to it,
    transitively. The reduced start is built in dependency order: plain
    parameters first, expressions after, so a child ordered before its parent
    in the request still resolves."""
    kept = [(name, par) for name, par in params_full.items() if not any(name.startswith(r) for r in removed_prefixes)]
    # ALL retained parameters exist before any expression is assigned, so a
    # chain of links in any request order resolves (lmfit evaluates an
    # expression when it is set).
    start = Parameters()
    for name, par in kept:
        start.add(name, value=par.value, min=par.min, max=par.max, vary=par.vary)
    for name, par in kept:
        if par.expr:
            start[name].set(expr=par.expr)
    refit = fit_reduced(start)
    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
    if not refit.success:
        # F2 (2026-09-26): a refit that did not converge establishes nothing
        # either way — its chi-square is wherever the optimiser stopped (a
        # redundant anchor read "required", F 992, from a refit stopped early;
        # F 1.17 once it completed). No verdict; the caller decides.
        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
                "refit_converged": False, "reason": "refit_not_converged",
                "message": str(getattr(refit, "message", "") or "")[:200]}
    delta = chi2_without - chi2_with
    p = max(1, int(n_free_comp))
    dof = max(1, len(y_sub) - int(n_free_total))
    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
    # change relative to the data's power, and then an "exactness" cutoff on
    # the reduced fit, each masked a resolved anchor at high dynamic range —
    # the same lesson as the DE unit). Known limit, accepted: on NOISE-FREE
    # data whose full fit is numerically exact (chi2_with ~ 1e-28) F is not
    # meaningful and a truly redundant component (two identical half-amplitude
    # components) reports "required"; real data never fit to machine precision.
    if not np.isfinite(chi2_without):
        f, required = None, True                     # the rest could not even be fitted without it
    elif delta <= 0:
        f, required = 0.0, False
    elif chi2_with == 0:
        f, required = None, True
    else:
        f = (delta / p) / (chi2_with / dof)
        required = f >= SUPPORT_MIN_F
    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
            "refit_converged": bool(refit.success)}


# ─────────────────────────────────────────────────────────────────────────────
# Main fitting API
# ─────────────────────────────────────────────────────────────────────────────

def run_fit(
    energy: np.ndarray,
    counts: np.ndarray,
    peak_specs: list[dict[str, Any]],
    background_method: str = "shirley",
    bg_start_idx: int | None = None,
    bg_end_idx: int | None = None,
    charge_shift_ev: float = 0.0,
    fit_kws: dict | None = None,
    n_perturb: int = 0,
    manual_bg: list | None = None,
    endpoint_avg: int = 1,
    n_starts: int = 0,
    require_component=None,
) -> dict[str, Any]:
    """
    Run XPS peak fitting and return a serialisable result dict.
    Run XPS peak fitting and return a serialisable result dict.

    Parameters
    ----------
    energy            : 1‑D array of binding energies (eV)
    counts            : 1‑D array of intensities (counts / CPS)
    peak_specs        : list of peak specification dicts (see _make_peak_params)
    background_method : 'shirley' | 'linear' | 'none'
    bg_start_idx      : slice start for background region (None → 0)
    bg_end_idx        : slice end for background region   (None → len)
    charge_shift_ev   : shift to apply to energy axis before fitting
    fit_kws           : extra kwargs forwarded to lmfit minimize

    Returns
    -------
    dict with keys: energy, fitted_y, background_y, residuals,
                    individual_peaks, statistics, charge_shift_applied, success
    """
    # One computation dtype: the weights are a function of the counts AND of
    # the precision they are held in (float32 counts give weights that differ
    # at 1e-8 and a different fit), and the seed hashes float64.
    energy = np.asarray(energy, dtype=float)
    counts = np.asarray(counts, dtype=float)
    if len(energy) != len(counts):
        raise ValueError("energy and counts must have the same length")
    if not peak_specs:
        raise ValueError("At least one peak specification is required")
    # Reject self/cyclic spin-orbit constraints before building lmfit exprs (F11)
    _validate_constraint_graph(peak_specs)

    # Apply charge correction
    energy = energy + charge_shift_ev

    fit_kws = dict(fit_kws or {})
    method = str(fit_kws.get("method", "leastsq")).lower()
    if method not in _FIT_METHODS:
        raise ValueError(f"Unknown fit method '{fit_kws.get('method')}'. Choices: {list(_FIT_METHODS)}")
    fit_kws["method"] = method
    # A caller's seed is consumed HERE: it replaces the request-derived one
    # and is never forwarded as a solver option (least_squares, leastsq and
    # nelder reject a 'seed' keyword).
    solver_kws = dict(fit_kws.pop("fit_kws", None) or {})
    caller_seed = solver_kws.pop("seed", None)
    if solver_kws:
        fit_kws["fit_kws"] = solver_kws
    if caller_seed is not None and (
            isinstance(caller_seed, (bool, np.bool_)) or not isinstance(caller_seed, (int, np.integer))
            or not 0 <= int(caller_seed) < 2 ** 32):
        raise ValueError("fit_kws.fit_kws.seed must be an integer in [0, 2**32)")

    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
    # narrow only the anchor window used to construct the background
    # curve. Reusing the slice for both was the bug where putting bg
    # anchors inside the ROI silently chopped the fit window — and the
    # reported χ², residuals, and σ — down to that same sub-slice.
    i0 = bg_start_idx if bg_start_idx is not None else 0
    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
    i0 = max(0, i0)
    i1 = min(len(energy), i1)
    # Normalize the user-supplied anchor pair: reversed order is a valid
    # choice — the frontend sends bg-start = higher BE and bg-end = lower
    # BE, so the index order depends on whether the data array is
    # BE-ascending or BE-descending. Treat the pair as an unordered
    # anchor window regardless of direction.
    if i0 > i1:
        i0, i1 = i1, i0
    # Bail to the full ROI only if the normalized window is genuinely
    # unusable (< 2 points): the integral / interp / linear-fit
    # functions below all need at least two distinct anchor points.
    if i1 - i0 < 2:
        i0, i1 = 0, len(energy)

    x = energy
    y = counts
    x_bg = energy[i0:i1]
    y_bg = counts[i0:i1]

    # ── Background ────────────────────────────────────────────────────────────
    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
    # physically defined only between the user's two anchor points: the
    # integral represents inelastic-loss cumulation through the peaks
    # *between* those anchors. Computing them over the full ROI would
    # let peaks outside the anchor window contribute to the loss
    # integral, which violates the model's premise. We therefore
    # compute them on [i0:i1] and flat-hold the endpoint value across
    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
    # values by construction, so constant extension is the least-bad
    # continuation. Linear backgrounds are extrapolated across the
    # full ROI (the line is well-defined outside the anchor window).
    bg_method = background_method.lower()
    bg_inner: np.ndarray | None = None

    if manual_bg is not None and bg_method == "manual":
        # manual_bg is a list of [be, intensity] anchor points from the
        # frontend. The anchors are BE-anchored (independent of i0/i1),
        # so interpolate them across the full ROI grid.
        anchors = sorted(manual_bg, key=lambda a: a[0])
        if len(anchors) >= 2:
            anchor_x = np.array([a[0] for a in anchors])
            anchor_y = np.array([a[1] for a in anchors])
            bg = np.interp(x, anchor_x, anchor_y)
        else:
            bg = linear_background(x, y)
    elif bg_method == "shirley":
        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart":
        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart_exp":
        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "shirley_linear":
        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "tougaard":
        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "linear":
        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
        # across the full ROI. The line is well-defined everywhere, so
        # constant extension would discard real information.
        if x[i1 - 1] != x[i0]:
            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
        else:
            slope = 0.0
        bg = y[i0] + slope * (x - x[i0])
    elif bg_method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{background_method}'")

    if bg_inner is not None:
        # Embed the anchor-window integral background into a full-ROI
        # array; flat-hold the endpoint value outside [i0, i1]. In the
        # common case where the user keeps bg anchors at the ROI edges
        # this is a no-op (i0=0, i1=len(y)).
        bg = np.zeros_like(y)
        if len(bg_inner) > 0:
            bg[i0:i1] = bg_inner
            if i0 > 0:
                bg[:i0] = bg_inner[0]
            if i1 < len(y):
                bg[i1:] = bg_inner[-1]

    y_sub = y - bg

    # Poisson weights: σ = √(raw counts), weight = 1/σ
    # Use raw counts (before background subtraction) for uncertainty estimate,
    # since the noise comes from the total photon counting statistics.
    # Floor at 1.0 to avoid division by zero for zero-count channels.
    sigma = np.sqrt(np.maximum(y, 1.0))
    weights = 1.0 / sigma

    # ── Build composite lmfit model ───────────────────────────────────────────
    # Sort so unconstrained (master) peaks come before constrained ones
    ordered = sorted(
        peak_specs,
        key=lambda s: 0 if s.get("constrain_to") is None else 1,
    )

    composite_model: Model | None = None
    all_params = Parameters()

    for spec in ordered:
        shape = spec.get("shape", "pseudo_voigt_gl")
        if shape not in _SHAPE_FUNCS:
            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
        func = _SHAPE_FUNCS[shape]
        prefix = f"p{spec['id']}_"
        m = Model(func, prefix=prefix)
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
            f"remove components or lock parameters.")

    # ── Fit ───────────────────────────────────────────────────────────────────
    kws = {"method": "leastsq", "nan_policy": "omit"}
    if fit_kws:
        kws.update(fit_kws)

    # Differential evolution needs a finite box and the page leaves amplitudes
    # open above: each candidate is searched in a generated box and then
    # refined under the request's own bounds (_search_then_refine). Every
    # other method fits the request's parameters exactly as before.
    def seeded(call_kws):
        """``call_kws`` with a fresh solver seed for the stochastic methods
        (one per minimisation, else every perturbed restart of differential
        evolution would replay the same population); unchanged otherwise."""
        if call_kws.get("method") not in _STOCHASTIC_METHODS:
            return call_kws
        solver_kws = dict(call_kws.get("fit_kws") or {})
        solver_kws["seed"] = int(solver_rng.integers(0, 2 ** 32 - 1))
        return {**call_kws, "fit_kws": solver_kws}

    # One fitter for any (sub)model of this request: the DE candidate machinery
    # when the method is differential evolution, else a plain seeded fit. The
    # scattered starts and the required-component refit go through it too.
    requested_bounds = {name: (par.min, par.max) for name, par in all_params.items()}

    def fit_model(model, params):
        if kws.get("method") == "differential_evolution":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        if kws.get("method") == "basinhopping":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))

    def fit_once(params):
        return fit_model(composite_model, params)

    # ── Diagnostic logging: BEFORE optimisation ──────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT START ═══  method=%s  n_data=%d", kws.get('method'), len(y_sub))
        for pname, par in sorted(all_params.items()):
            log.debug("  BEFORE  %-30s value=%12.6f  vary=%-5s  expr=%s  min=%s  max=%s",
                      pname, par.value, str(par.vary), par.expr,
                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')

    try:
        result = fit_once(all_params)
    except Exception as exc:
        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc

    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
                  result.success, result.nfev, result.message)
        for pname, par in sorted(result.params.items()):
            init = all_params[pname].value if pname in all_params else None
            delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
            log.debug("  AFTER   %-30s value=%12.6f  stderr=%s%s",
                      pname, par.value,
                      f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)

    # ── Perturb and refit to escape local minima ─────────────────────────
    # Not for basinhopping (unit F2, 2026-09-26, owner): it is already a global
    # search, so perturbed restarts add nothing — the reason the scattered-
    # starts check excludes it — and with the page's n_perturb 3 they
    # quadrupled its time past the server's 300 s timeout on 14 of 16 sampled
    # multi-component targets (median 386 s, max 1066 s; without them median
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

exec
/bin/zsh -lc "git diff main..HEAD -- CLAUDE.md docs/superpowers/plans/2026-09-26-f2-acceptance-holes.md; rg -n 'required|run_fit|nan_policy|isfinite' autofit app.py | head -160; ls -a; find .. -name AGENTS.md -print" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 1217ms:
exec
/bin/zsh -lc "sed -n '1020,1125p' fitting.py; sed -n '1390,1500p' fitting.py; sed -n '1530,1765p' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
            continue
        if name.endswith("_amplitude"):
            width = max(10.0 * y_top, 2.0 * abs(par.value), 1.0)
            lo, hi = -width, width
        elif name.endswith("_center"):
            width = span
            lo, hi = min(x_lo, par.value), max(x_hi, par.value)
        else:
            raise ValueError(
                f"differential_evolution needs finite bounds for '{name}'")
        new_min = lo if open_min else par.min
        new_max = hi if open_max else par.max
        # A bound the request did set can sit at or beyond the generated
        # side (centre_min = 300 on a 280-290 eV ROI): keep a real interval.
        if open_max and new_max <= new_min:
            new_max = new_min + width
        if open_min and new_min >= new_max:
            new_min = new_max - width
        par.set(min=new_min, max=new_max)
        generated[name] = {side: width for side, is_open in (("min", open_min), ("max", open_max)) if is_open}
    return generated


def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
    """One differential-evolution candidate: search inside a generated box,
    then refine FROM that solution with ``least_squares`` under the request's
    own (open) bounds.

    Whenever a side was generated the refinement is unconditional (a request
    that bounds everything itself is returned as found). A box can shape the answer without the
    solution lying anywhere near a side (centre and width compensate for a
    capped amplitude), and an unrefined boundary candidate can lose the
    perturb loop's comparison to a worse interior one, so every candidate is
    freed from the box before it is compared or returned. The refined fit
    replaces the search result whenever it converged; if it did not (or
    raised) the search result is returned marked
    ``box_unverified`` (with the sides we generated, so they are not
    reported as bounds) and ``run_fit`` does not call it a success.
    """
    # ``params`` may come from an earlier candidate and still carry that
    # candidate's generated sides: always start from the request's bounds.
    boxed = params.copy()
    for name, (lo, hi) in requested.items():
        boxed[name].set(min=lo, max=hi)
    generated = _finite_search_box(boxed, x, y_sub)
    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
    found.box_unverified, found.search_box = bool(generated), generated
    if not generated:
        return found
    free = found.params.copy()
    for name in generated:
        free[name].set(min=requested[name][0], max=requested[name][1])
    # Only what a local solver understands: DE options (seed, popsize, ...)
    # passed through fit_kws would make least_squares raise.
    refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
    try:
        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
    except Exception:
        log.debug("refinement outside the search box raised", exc_info=True)
        return found
    # A converged refinement IS the result: it is a least_squares fit of the
    # requested model under the requested bounds, which is what the default
    # method returns and the acceptance rule accepts. It is deliberately NOT
    # compared with the boxed search's chi-square. least_squares descends
    # from its start, so it cannot end materially above it (four review
    # rounds found no reachable case), but it does end a hair above an EXACT
    # start that sits on a requested bound (the bound transform is degenerate
    # there; the centre moves ~1e-7 eV), by an amount that depends on peak
    # width, position and counts. Every tolerance tried for that comparison
    # produced reachable false failures and no reachable protection.
    if refined.success:
        refined.box_unverified, refined.search_box = False, {}
        return refined
    return found


def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws):
    """A differential-evolution candidate that is never worse than the
    default method from the same start.

    Differential evolution ignores the starting values. On a needle-narrow
    peak in a wide box it can converge, "successfully", with the component
    outside the fitted range (chi-square 1e7 where ``least_squares`` from the
    request's start reaches 1e-4), and the refinement has nothing to descend
    to from there. So a ``least_squares`` fit from the candidate's own start,
    under the request's bounds, competes with the search: a verified result
    beats an unverified one, then the lower chi-square wins.
    """
    searched = _search_then_refine(model, params, requested, y_sub, x, weights, kws)
    start = params.copy()
    for name, (lo, hi) in requested.items():
        start[name].set(min=lo, max=hi)
    try:
        local = model.fit(y_sub, start, x=x, weights=weights,
                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"))
    except Exception:
        log.debug("local candidate from the start raised", exc_info=True)
        return searched
    if not local.success:
        return searched
    local.box_unverified, local.search_box = False, {}
    if searched.box_unverified or not searched.success or local.chisqr < searched.chisqr:
        return local
    return searched


# A component driven to its amplitude floor, pinned on a bound or fitted to
# numerical residue has chi2_without <= chi2_with (removing it costs nothing).
# Owner decision 2026-09-18: such a component is an explicit OUTCOME — the fit
# did not determine it — and its centre, width and sigma are not reported.
# Known limits, same as the Auto-Fit anchor: a gross single-channel artefact
# inflates chi2_with and can mark a real component unsupported; redundancy
# under overlap is NOT detected (a refit without the component is the test for
# that; step (c) does it for the Auto-Fit anchor). Threshold F >= 10 (~ p 1e-9
# at these sizes); on the 202 committed targets resolved components have
# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
# they were refitted still passes. The test for that is the refit itself:
# remove the component, refit the rest from their fitted values under the
# request's own bounds, and compare the fit to the data with and without it:
#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
# p = the component's free parameters, dof = n - nvarys of the full model.
# One extra fit, so it is done only when asked for (Auto-Fit asks for its
# charge-reference anchor: an anchor that is not required must not set the
# energy reference of a whole spectrum). Same threshold as `support`.
def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
    """``fit_reduced(params)`` is the run's own fitter for the reduced model
    (the same candidate machinery and seeding the fit used, so differential
    evolution's box/refinement and the request seed apply to the refit too).
    ``removed_prefixes`` is the removed component AND everything linked to it,
    transitively. The reduced start is built in dependency order: plain
    parameters first, expressions after, so a child ordered before its parent
    in the request still resolves."""
    kept = [(name, par) for name, par in params_full.items() if not any(name.startswith(r) for r in removed_prefixes)]
    # ALL retained parameters exist before any expression is assigned, so a
    # chain of links in any request order resolves (lmfit evaluates an
    # expression when it is set).
    start = Parameters()
    for name, par in kept:
        start.add(name, value=par.value, min=par.min, max=par.max, vary=par.vary)
    for name, par in kept:
        if par.expr:
            start[name].set(expr=par.expr)
    refit = fit_reduced(start)
    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
    if not refit.success:
        # F2 (2026-09-26): a refit that did not converge establishes nothing
        # either way — its chi-square is wherever the optimiser stopped (a
        # redundant anchor read "required", F 992, from a refit stopped early;
        # F 1.17 once it completed). No verdict; the caller decides.
        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
                "refit_converged": False, "reason": "refit_not_converged",
                "message": str(getattr(refit, "message", "") or "")[:200]}
    delta = chi2_without - chi2_with
    p = max(1, int(n_free_comp))
    dof = max(1, len(y_sub) - int(n_free_total))
    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
    # change relative to the data's power, and then an "exactness" cutoff on
    # the reduced fit, each masked a resolved anchor at high dynamic range —
    # the same lesson as the DE unit). Known limit, accepted: on NOISE-FREE
    # data whose full fit is numerically exact (chi2_with ~ 1e-28) F is not
    # meaningful and a truly redundant component (two identical half-amplitude
    # components) reports "required"; real data never fit to machine precision.
    if not np.isfinite(chi2_without):
        f, required = None, True                     # the rest could not even be fitted without it
    elif delta <= 0:
        f, required = 0.0, False
    elif chi2_with == 0:
        f, required = None, True
    else:
        f = (delta / p) / (chi2_with / dof)
        required = f >= SUPPORT_MIN_F
    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
            "refit_converged": bool(refit.success)}


# ─────────────────────────────────────────────────────────────────────────────
# Main fitting API
# ─────────────────────────────────────────────────────────────────────────────

def run_fit(
    energy: np.ndarray,
    counts: np.ndarray,
    peak_specs: list[dict[str, Any]],
    background_method: str = "shirley",
    bg_start_idx: int | None = None,
    bg_end_idx: int | None = None,
    charge_shift_ev: float = 0.0,
    fit_kws: dict | None = None,
    n_perturb: int = 0,
    manual_bg: list | None = None,
    endpoint_avg: int = 1,
    if not peak_specs:
        raise ValueError("At least one peak specification is required")
    # Reject self/cyclic spin-orbit constraints before building lmfit exprs (F11)
    _validate_constraint_graph(peak_specs)

    # Apply charge correction
    energy = energy + charge_shift_ev

    fit_kws = dict(fit_kws or {})
    method = str(fit_kws.get("method", "leastsq")).lower()
    if method not in _FIT_METHODS:
        raise ValueError(f"Unknown fit method '{fit_kws.get('method')}'. Choices: {list(_FIT_METHODS)}")
    fit_kws["method"] = method
    # A caller's seed is consumed HERE: it replaces the request-derived one
    # and is never forwarded as a solver option (least_squares, leastsq and
    # nelder reject a 'seed' keyword).
    solver_kws = dict(fit_kws.pop("fit_kws", None) or {})
    caller_seed = solver_kws.pop("seed", None)
    if solver_kws:
        fit_kws["fit_kws"] = solver_kws
    if caller_seed is not None and (
            isinstance(caller_seed, (bool, np.bool_)) or not isinstance(caller_seed, (int, np.integer))
            or not 0 <= int(caller_seed) < 2 ** 32):
        raise ValueError("fit_kws.fit_kws.seed must be an integer in [0, 2**32)")

    # The fit runs on the ENTIRE incoming ROI; bg_start_idx / bg_end_idx
    # narrow only the anchor window used to construct the background
    # curve. Reusing the slice for both was the bug where putting bg
    # anchors inside the ROI silently chopped the fit window — and the
    # reported χ², residuals, and σ — down to that same sub-slice.
    i0 = bg_start_idx if bg_start_idx is not None else 0
    i1 = bg_end_idx if bg_end_idx is not None else len(energy)
    i0 = max(0, i0)
    i1 = min(len(energy), i1)
    # Normalize the user-supplied anchor pair: reversed order is a valid
    # choice — the frontend sends bg-start = higher BE and bg-end = lower
    # BE, so the index order depends on whether the data array is
    # BE-ascending or BE-descending. Treat the pair as an unordered
    # anchor window regardless of direction.
    if i0 > i1:
        i0, i1 = i1, i0
    # Bail to the full ROI only if the normalized window is genuinely
    # unusable (< 2 points): the integral / interp / linear-fit
    # functions below all need at least two distinct anchor points.
    if i1 - i0 < 2:
        i0, i1 = 0, len(energy)

    x = energy
    y = counts
    x_bg = energy[i0:i1]
    y_bg = counts[i0:i1]

    # ── Background ────────────────────────────────────────────────────────────
    # Integral backgrounds (Shirley, Tougaard, Smart variants) are
    # physically defined only between the user's two anchor points: the
    # integral represents inelastic-loss cumulation through the peaks
    # *between* those anchors. Computing them over the full ROI would
    # let peaks outside the anchor window contribute to the loss
    # integral, which violates the model's premise. We therefore
    # compute them on [i0:i1] and flat-hold the endpoint value across
    # the rest of the ROI — Shirley/Tougaard asymptote to the anchor
    # values by construction, so constant extension is the least-bad
    # continuation. Linear backgrounds are extrapolated across the
    # full ROI (the line is well-defined outside the anchor window).
    bg_method = background_method.lower()
    bg_inner: np.ndarray | None = None

    if manual_bg is not None and bg_method == "manual":
        # manual_bg is a list of [be, intensity] anchor points from the
        # frontend. The anchors are BE-anchored (independent of i0/i1),
        # so interpolate them across the full ROI grid.
        anchors = sorted(manual_bg, key=lambda a: a[0])
        if len(anchors) >= 2:
            anchor_x = np.array([a[0] for a in anchors])
            anchor_y = np.array([a[1] for a in anchors])
            bg = np.interp(x, anchor_x, anchor_y)
        else:
            bg = linear_background(x, y)
    elif bg_method == "shirley":
        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart":
        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "smart_exp":
        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "shirley_linear":
        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "tougaard":
        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
    elif bg_method == "linear":
        # Extrapolate the line through (E[i0], y[i0]) ↔ (E[i1-1], y[i1-1])
        # across the full ROI. The line is well-defined everywhere, so
        # constant extension would discard real information.
        if x[i1 - 1] != x[i0]:
            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
        else:
            slope = 0.0
        bg = y[i0] + slope * (x - x[i0])
    elif bg_method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{background_method}'")

    if bg_inner is not None:
        # Embed the anchor-window integral background into a full-ROI
        # array; flat-hold the endpoint value outside [i0, i1]. In the
        # common case where the user keeps bg anchors at the ROI edges
        # this is a no-op (i0=0, i1=len(y)).
        bg = np.zeros_like(y)
        if len(bg_inner) > 0:
            bg[i0:i1] = bg_inner
            if i0 > 0:
                bg[:i0] = bg_inner[0]
            if i1 < len(y):
                bg[i1:] = bg_inner[-1]

    y_sub = y - bg

    # Poisson weights: σ = √(raw counts), weight = 1/σ
    # Use raw counts (before background subtraction) for uncertainty estimate,
    # since the noise comes from the total photon counting statistics.
    # Floor at 1.0 to avoid division by zero for zero-count channels.
    sigma = np.sqrt(np.maximum(y, 1.0))
    weights = 1.0 / sigma

    # ── Build composite lmfit model ───────────────────────────────────────────
    # Sort so unconstrained (master) peaks come before constrained ones
    ordered = sorted(
        peak_specs,
        key=lambda s: 0 if s.get("constrain_to") is None else 1,
    )

    composite_model: Model | None = None
    all_params = Parameters()

    for spec in ordered:
        shape = spec.get("shape", "pseudo_voigt_gl")
        if shape not in _SHAPE_FUNCS:
            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
        func = _SHAPE_FUNCS[shape]
        prefix = f"p{spec['id']}_"
        m = Model(func, prefix=prefix)
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
            f"remove components or lock parameters.")

    # ── Fit ───────────────────────────────────────────────────────────────────
    kws = {"method": "leastsq", "nan_policy": "omit"}
    if fit_kws:
        kws.update(fit_kws)

    # Differential evolution needs a finite box and the page leaves amplitudes
    # open above: each candidate is searched in a generated box and then
    # refined under the request's own bounds (_search_then_refine). Every
    # other method fits the request's parameters exactly as before.
    def seeded(call_kws):
        """``call_kws`` with a fresh solver seed for the stochastic methods
        (one per minimisation, else every perturbed restart of differential
        evolution would replay the same population); unchanged otherwise."""
        if call_kws.get("method") not in _STOCHASTIC_METHODS:
            return call_kws
        solver_kws = dict(call_kws.get("fit_kws") or {})
        solver_kws["seed"] = int(solver_rng.integers(0, 2 ** 32 - 1))
        return {**call_kws, "fit_kws": solver_kws}

    # One fitter for any (sub)model of this request: the DE candidate machinery
    # when the method is differential evolution, else a plain seeded fit. The
    # scattered starts and the required-component refit go through it too.
    requested_bounds = {name: (par.min, par.max) for name, par in all_params.items()}

    def fit_model(model, params):
        if kws.get("method") == "differential_evolution":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _global_or_local_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        if kws.get("method") == "basinhopping":
            bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
            return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))

    def fit_once(params):
        return fit_model(composite_model, params)

    # ── Diagnostic logging: BEFORE optimisation ──────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT START ═══  method=%s  n_data=%d", kws.get('method'), len(y_sub))
        for pname, par in sorted(all_params.items()):
            log.debug("  BEFORE  %-30s value=%12.6f  vary=%-5s  expr=%s  min=%s  max=%s",
                      pname, par.value, str(par.vary), par.expr,
                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')

    try:
        result = fit_once(all_params)

codex
The basinhopping wrapper is shared by the main fit and required refit, and the restart exclusion is specific to basinhopping. I’m checking linked parameters, omitted data, aborts, and browser error handling next. The new tests cover the main cases, but leave several of these edges untested.
exec
/bin/zsh -lc "rg -n 'venv|pytest|python3|conda' CLAUDE.md requirements-dev.txt tests/conftest.py; sed -n '1760,1790p' fitting.py; sed -n '1820,1965p' fitting.py; sed -n '1965,2150p' fitting.py; rg -n 'run_fit\\(|except|error' app.py | tail -65" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
tests/conftest.py:1:"""Make the repo root importable regardless of how pytest is invoked."""
requirements-dev.txt:5:pytest>=9.0
CLAUDE.md:27:tests/                    # pytest suite (focused on LA + DS+G correctness)
CLAUDE.md:31:venv/                     # virtualenv (do not commit)
CLAUDE.md:939:Run via `pytest tests/`.
                      pname, par.value, str(par.vary), par.expr,
                      f"{par.min:.4f}" if np.isfinite(par.min) else '-inf',
                      f"{par.max:.4f}" if np.isfinite(par.max) else 'inf')

    try:
        result = fit_once(all_params)
    except Exception as exc:
        raise RuntimeError(f"lmfit fitting failed: {exc}") from exc

    # ── Diagnostic logging: AFTER optimisation ───────────────────────────────
    if log.isEnabledFor(logging.DEBUG):
        log.debug("═══ FIT DONE ═══  success=%s  nfev=%s  message=%s",
                  result.success, result.nfev, result.message)
        for pname, par in sorted(result.params.items()):
            init = all_params[pname].value if pname in all_params else None
            delta = f"  Δ={par.value - init:+.6f}" if init is not None and abs(par.value - init) > 1e-10 else ""
            log.debug("  AFTER   %-30s value=%12.6f  stderr=%s%s",
                      pname, par.value,
                      f"{par.stderr:.6f}" if par.stderr is not None else 'None', delta)

    # ── Perturb and refit to escape local minima ─────────────────────────
    # Not for basinhopping (unit F2, 2026-09-26, owner): it is already a global
    # search, so perturbed restarts add nothing — the reason the scattered-
    # starts check excludes it — and with the page's n_perturb 3 they
    # quadrupled its time past the server's 300 s timeout on 14 of 16 sampled
    # multi-component targets (median 386 s, max 1066 s; without them median
    # 96 s, max 256 s, and chi2r identical to 1e-8 on all 16).
    if n_perturb > 0 and result.success and kws.get("method") != "basinhopping":
        best_result = result
        best_redchi = result.redchi if result.redchi is not None else float('inf')
        rng = perturb_rng
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
                        if master is not None and str(master) in removed and pid not in removed:
                            removed.add(pid); grew = True
                removed_prefixes = [f"p{pid}_" for pid in removed]
                without = None
                for m in composite_model.components:
                    if m.prefix in removed_prefixes:
                        continue
                    without = m if without is None else without + m
                if without is None:
                    required = {"ran": False, "reason": "nothing_left"}
                else:
                    n_free_comp = sum(1 for n, par in result.params.items()
                                      if n.startswith(rprefix) and par.vary and par.expr is None)
                    required = {"ran": True, **_component_required(
                        lambda params: fit_model(without, params), result.params, removed_prefixes, y_sub, weights,
                        float(result.chisqr), n_free_comp, result.nvarys)}
            except Exception as exc:                              # the check must never cost the student the fit
                log.exception("required-component refit failed")
                required = {"ran": False, "reason": "error", "error": f"{type(exc).__name__}: {exc}"[:200]}

    # Sides WE closed on the returned result (non-empty only for a
    # differential-evolution result whose refinement did not take over).
    search_box = getattr(result, "search_box", {})

    fitted_sub = result.best_fit
    fitted_y = fitted_sub + bg

    # ── Per‑peak results ──────────────────────────────────────────────────────
    individual_peaks = []
    for spec in peak_specs:
        pid = spec["id"]
        prefix = f"p{pid}_"
        peak_y = composite_model.components[
            next(i for i, c in enumerate(composite_model.components)
                 if c.prefix == prefix)
        ].eval(result.params, x=x)

        # Area by numerical integration. abs(): real XPS grids are
        # BE-descending, which makes the raw trapezoid integral negative —
        # the area is a magnitude by convention (matches autofit/engine.py).
        area = float(abs(trapezoid(peak_y, x)))

        # Parameter extraction with stderr
        param_info: dict[str, Any] = {}
        for pname in result.params:
            if pname.startswith(prefix):
                short = pname[len(prefix):]
                par = result.params[pname]
                param_info[short] = {
                    "value": float(par.value),
                    "stderr": float(par.stderr) if par.stderr is not None else None,
                    "vary": par.vary,
                    "expr": par.expr,
                    "min": float(par.min) if np.isfinite(par.min) and "min" not in search_box.get(pname, {}) else None,
                    "max": float(par.max) if np.isfinite(par.max) and "max" not in search_box.get(pname, {}) else None,
                }

        param_info["area"] = {"value": area, "stderr": None}

        # Approximate area stderr via amplitude + fwhm propagation
        amp_par = result.params.get(prefix + "amplitude")
        fwhm_par = result.params.get(prefix + "fwhm")
        if (amp_par and fwhm_par and amp_par.stderr and fwhm_par.stderr
                and amp_par.value and fwhm_par.value):
            rel_err = np.sqrt(
                (amp_par.stderr / amp_par.value) ** 2
                + (fwhm_par.stderr / fwhm_par.value) ** 2
            )
            param_info["area"]["stderr"] = abs(area) * rel_err

        n_free_comp = sum(1 for n, par in result.params.items() if n.startswith(prefix) and par.vary and par.expr is None)
        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)
        # A linked component follows its parent: it is supported exactly when the
        # parent is (its own removal test would double-count the parent's role).
        individual_peaks.append({
            "id": pid,
            "y": peak_y.tolist(),
            "params": param_info,
            "support": support,
        })

    # A linked component follows its ROOT ancestor (a grandchild follows the
    # root), whatever the request order; a cycle or a missing master leaves
    # its own verdict.
    by_id = {str(ip["id"]): ip for ip in individual_peaks}
    master_of = {str(spec["id"]): spec.get("constrain_to") for spec in peak_specs}

    def root_of(pid: str) -> str:
        seen = set()
        while master_of.get(pid) is not None and str(master_of[pid]) in by_id and pid not in seen:
            seen.add(pid)
            pid = str(master_of[pid])
        return pid

    for ip in individual_peaks:
        root = root_of(str(ip["id"]))
        if root != str(ip["id"]):
            ip["support"]["follows"] = by_id[root]["id"]
            ip["support"]["supported"] = by_id[root]["support"]["supported"]

    # ── Statistics ────────────────────────────────────────────────────────────
    # ── Statistics ────────────────────────────────────────────────────────────
    n_data = len(y_sub)
    n_free = result.nvarys
    chi_sq = float(result.chisqr) if result.chisqr is not None else None
    red_chi_sq = float(result.redchi) if result.redchi is not None else None

    residuals = (y_sub - fitted_sub).tolist()

    # R‑factor (like in crystallography: sum|obs-calc| / sum|obs|)
    r_factor = (float(np.sum(np.abs(y_sub - fitted_sub)) / np.sum(np.abs(y_sub)))
                if np.sum(np.abs(y_sub)) > 0 else None)

    success, message = result.success, result.message
    if getattr(result, "box_unverified", False):
        # Searched inside limits the request never set, and the refinement
        # that would show they did not matter did not converge to an equal
        # or better solution. The acceptance rule shows this as a failed fit.
        success = False
        message = ("differential_evolution searched inside generated limits for "
                   + ", ".join(sorted(search_box))
                   + " and a local refinement without them did not converge to an equal or better"
                     " solution. Set bounds for those parameters or use another method.")

    return {
        "success": success,
        "message": message,
        "energy": x.tolist(),
        "counts": y.tolist(),
        "fitted_y": fitted_y.tolist(),
        "background_y": bg.tolist(),
        "residuals": residuals,
        "individual_peaks": individual_peaks,
        "statistics": {
            "chi_square": chi_sq,
            "reduced_chi_square": red_chi_sq,
            "r_factor": r_factor,
            "n_data": n_data,
            "n_free_params": n_free,
            "aic": float(result.aic) if result.aic is not None else None,
            "bic": float(result.bic) if result.bic is not None else None,
        },
        "charge_shift_applied": charge_shift_ev,
        "random_seed": random_seed,
        "starts": starts,
        "required": required,
    }


def compute_background_only(
    energy: np.ndarray,
    counts: np.ndarray,
    method: str = "shirley",
    start_idx: int | None = None,
    end_idx: int | None = None,
    endpoint_avg: int = 1,
) -> dict[str, Any]:
    """Return just the background array without fitting peaks."""
    i0 = start_idx if start_idx is not None else 0
    i1 = end_idx if end_idx is not None else len(energy)
    x, y = energy[i0:i1], counts[i0:i1]

    if method == "shirley":
        bg = shirley_background(x, y, n_avg=endpoint_avg)
    elif method == "smart":
        bg = smart_background(x, y, n_avg=endpoint_avg)
    elif method == "smart_exp":
        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
    elif method == "shirley_linear":
        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
    elif method == "tougaard":
        bg = tougaard_background(x, y, n_avg=endpoint_avg)
    elif method == "linear":
        bg = linear_background(x, y)
    elif method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{method}'")

    return {
        "energy": x.tolist(),
        "background": bg.tolist(),
        "net_counts": (y - bg).tolist(),
    }
422:        logging.getLogger(__name__).exception(
434:    except OSError:
440:        except FileNotFoundError:
442:        except OSError:
508:            except XPSReferenceError as e:
509:                logging.getLogger(__name__).error(
546:        On invalid data this fails loudly with a structured error naming the
552:        except XPSReferenceError as e:
553:            logging.getLogger(__name__).error("XPS reference dataset invalid: %s", e)
554:            return jsonify({"error": e.message, "file": e.filename,
583:        except ValueError as exc:
588:        except Exception:
590:            app.logger.exception("Unexpected file-parse error")
592:            return _err("Internal parse error — see server log for details.", 500)
600:        except Exception:
601:            app.logger.exception("Failed to store session")
641:        except ValueError:
653:        except (ValueError, ImportError) as exc:
657:        except Exception:
658:            app.logger.exception("Unexpected VGD parse error")
659:            return _err("Internal VGD parse error — see server log.", 500)
677:        except KeyError:
713:        except KeyError:
722:        except (TypeError, ValueError):
731:        except ValueError as exc:
734:        except Exception:
735:            app.logger.exception("Unexpected background error")
736:            return _err("Internal background error — see server log.", 500)
787:        except KeyError:
798:        except (TypeError, ValueError):
825:        except (TypeError, ValueError):
841:            result = fitting.run_fit(
856:        except ValueError as exc:
860:        except RuntimeError:
863:            app.logger.exception("Fit failed")
865:        except Exception:
866:            app.logger.exception("Unexpected fitting error")
867:            return _err("Internal fitting error — see server log.", 500)
941:        except _AnalyzeError as exc:
972:        message, result (once done), error (once errored)}.
980:        except _AnalyzeError as exc:
1014:            except _AnalyzeError as exc:
1016:                    "status": "error", "phase": "done",
1018:                    "message": "failed", "error": str(exc),
1021:            except Exception as exc:      # belt-and-suspenders: the
1024:                logging.getLogger(__name__).exception(
1027:                    "status": "error", "phase": "done",
1030:                    "error": f"internal error: {exc}",
1040:        {status: 'running'|'done'|'error', phase, candidate_index,
1042:        (done only — the SAME shape /api/analyze returns), error (error
1047:        except ValueError:
1054:        except (OSError, ValueError):
1074:def _register_error_handlers(app: Flask) -> None:
1076:    @app.errorhandler(404)
1078:        return jsonify({"error": "Not found"}), 404
1080:    @app.errorhandler(405)
1082:        return jsonify({"error": "Method not allowed"}), 405
1084:    @app.errorhandler(413)
1086:        return jsonify({"error": "File too large (limit 50 MB)"}), 413
1088:    @app.errorhandler(500)
1089:    def internal_error(e):
1090:        app.logger.exception("Unhandled 500 error")
1091:        return jsonify({"error": "Internal server error"}), 500
1102:    except (ValueError, AttributeError):
1116:    except (TypeError, ValueError):

exec
/bin/zsh -lc "sed -n '7250,7350p' templates/index.html; sed -n '7470,7645p' templates/index.html; sed -n '8010,8165p' templates/index.html; sed -n '8260,8385p' templates/index.html; rg -n '/api/fit|runFit\\(|required|refit_converged' autofit/page* templates/index.html | tail -90" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
    if (vals[0]) vals[0].textContent = un ? dash : p.center.toFixed(2);
    if (vals[1]) vals[1].textContent = un ? dash : p.fwhm.toFixed(2);
    if (vals[2]) vals[2].textContent = (un || !(total > 0 && areas[p.id] > 0)) ? dash : ((areas[p.id] / total) * 100).toFixed(1) + '%';
    const name = item.querySelector('.peak-name'), badge = name && name.querySelector('.unsupported-badge');
    if (un && name && !badge) name.insertAdjacentHTML('beforeend', ' ' + _unsupportedBadge(p.id));
    if (!un && badge) { badge.previousSibling && badge.previousSibling.nodeType === 3 && badge.previousSibling.textContent === ' ' ? badge.previousSibling.remove() : null; badge.remove(); }
  }
}
function _unsupportedBadge(id) { return `<span class="unsupported-badge" data-peak-id="${id}" title="${_escAttr(_UNSUPPORTED_TIP)}">${_UNSUPPORTED_LABEL}</span>`; }

const _AUTOFIT_ANCHOR_MIN_F = 10;
function _autoFitGraphiteIsSupported(gPeak, json) {
  const amp = gPeak && gPeak.amplitude;
  if (!Number.isFinite(amp) || amp <= 0) return false;
  const counts = (json && json.counts) || [], fit = (json && json.fitted_y) || [];
  const ip = ((json && json.individual_peaks) || []).find(q => String(q.id) === String(gPeak.id));
  const comp = (ip && ip.y) || [];
  const n = counts.length;
  if (!n || fit.length !== n || comp.length !== n) return false;          // nothing to judge against
  let withC = 0, withoutC = 0;
  for (let i = 0; i < n; i++) {
    if (!Number.isFinite(counts[i]) || !Number.isFinite(fit[i]) || !Number.isFinite(comp[i])) continue;
    const w = 1 / Math.max(counts[i], 1), r = counts[i] - fit[i];
    withC += w * r * r;
    withoutC += w * (r + comp[i]) * (r + comp[i]);
  }
  const delta = withoutC - withC;
  if (!(delta > 0)) return false;
  let p = 0;
  for (const k in (ip.params || {})) { const q = ip.params[k]; if (q && q.vary === true && (q.expr == null || q.expr === '')) p++; }
  p = Math.max(1, p);
  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
  const dof = Math.max(1, n - nFree);
  if (withC === 0) return true;                                           // exact fit that the component is needed for
  return (delta / p) / (withC / dof) >= _AUTOFIT_ANCHOR_MIN_F;
}

function applyAutoFitResult(json, graphiteRaw, roi) {
  // 1. Locate the graphite peak in state.peaks (named "Graphite").
  const gPeak = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (!gPeak || !Number.isFinite(gPeak.center)) {
    notify('Auto-fit failed: graphite center not found in fit result.', 'red', true);
    return false;
  }
  // 1b. The charge correction below is derived from this component's fitted
  // centre and then shifts EVERY binding energy in the spectrum, so the
  // component has to exist. A Graphite amplitude driven to its lower bound
  // (the server's floor is zero; lmfit returns ~1e-12 there) still comes back
  // with a centre inside the ±0.3 eV window — a position of nothing.
  // 1c. Supported (the fit cannot drop it without cost, other components held)
  // is necessary but not sufficient: with strong overlap the OTHER components
  // could absorb the anchor if refitted. The server refits without it when
  // asked (require_component) and reports whether that made the fit
  // significantly worse. A redundant anchor is refused the same way.
  const req = json && json.required;
  if (req && req.ran === true && req.required === false) {
    notify('Auto-fit: the Graphite component is not required by the data — refitting the other components without it fits the data as well' + (req.f != null ? ' (F = ' + Number(req.f).toFixed(1) + ', threshold 10)' : '') + '. No charge correction was derived from it and the fit was not applied. The model gives the other components enough freedom to absorb the graphite line; lock or narrow them and try again.', 'red', true);
    return false;
  }
  // F2 (2026-09-26): the refit without the anchor did not converge, so the
  // server could not establish that the anchor is required. The anchor would
  // set the energy reference of the whole spectrum: refused, like a
  // redundant one (a check that did not RUN at all still never blocks).
  if (req && req.ran === true && req.refit_converged === false) {
    notify('Auto-fit: it could not be established that the data require the Graphite component — refitting the other components without it did not converge. No charge correction was derived from it and the fit was not applied. Try Run Fit, or narrow the ROI, and run Auto-Fit again.', 'red', true);
    return false;
  }
  if (!_autoFitGraphiteIsSupported(gPeak, json)) {
    notify('Auto-fit: the data do not support the Graphite component (removing it does not worsen the fit), so no charge correction was derived from it and the fit was not applied.', 'red', true);
    return false;
  }
  // 2. Validate within ±0.3 of 284.50 (the LA center bound).
  if (Math.abs(gPeak.center - 284.50) > 0.30 + 1e-6) {
    notify('Fit failed to converge or produced an unphysical graphite position.', 'red', true);
    return false;
  }
  // 3. Compute fitted raw center using APP CONVENTION:
  //    raw = corrected + state.ccShift (state.ccShift is the provisional value).
  const graphiteFittedRaw = gPeak.center + (Number.isFinite(state.ccShift) ? state.ccShift : 0);

  // 4. Drive updateChargeCorrection() to refine the shift.
  // Self-consistency: cc-obs = graphite_fitted_raw (NOT graphite_raw_BE),
  // approved design point.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  if (cm && co && cl) {
    cm.value = 'c1s';
    co.value = graphiteFittedRaw.toFixed(3);
    cl.value = '284.50';
    if (typeof updateChargeCorrection === 'function') updateChargeCorrection();
  }

  // 5. Build state.fitResult exactly as runFit() does.
  const { be: be2, inten: inten2 } = getROIData();
  const bgI2 = computeBackground(be2, inten2);
  const bgSub2 = inten2.map((v, i) => v - bgI2[i]);
  const stats = json.statistics || {};
  const chiReduced = stats.reduced_chi_square || 0;
  const rmse = Math.sqrt((json.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be2.length));
  const roiRange = { min: _arrMin(be2).toFixed(1), max: _arrMax(be2).toFixed(1) };
  // Step 2: provisional shift (APP CONVENTION).
  const provisionalShift = graphiteRaw - 284.50;

  // Step 3: assess low-BE region using provisional shift (no state mutation yet).
  const assessment = assessLowBERegion(rawBE, bgSub, provisionalShift);

  // Step 4: build the peak model (in corrected frame after provisional shift).
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  // Apply provisional shift via updateChargeCorrection so ROI/bg DOM fields
  // shift along with state.ccShift.
  const cm = document.getElementById('cc-method');
  const co = document.getElementById('cc-obs');
  const cl = document.getElementById('cc-lit');
  cm.value = 'c1s';
  co.value = graphiteRaw.toFixed(3);
  cl.value = '284.50';
  updateChargeCorrection();
  // Now build the peak list (graphite center 284.50 in this frame).
  const newPeaks = buildAutoFitModel(assessment);
  state.peaks = newPeaks;
  state.nextId = Math.max(0, ...state.peaks.map(p => p.id)) + 1;
  renderPeakList();

  // Step 5: run /api/fit with AbortController + spinner.
  _showFitSpinner();
  const spinLabel = document.getElementById('fit-spinner-label');
  if (spinLabel) spinLabel.textContent = 'Auto-fitting…';
  const runBtn = document.querySelector('.btn-green');
  if (runBtn) runBtn.disabled = true;

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(new DOMException('timeout', 'AbortError')), 120000);

  try {
    const { be: be2, inten: inten2 } = getROIData();
    const bgType = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be2, bgStart, bgEnd);
    const epAvg = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const fitMethod = document.getElementById('fit-method').value;

    // The anchor whose necessity the server must test — captured with the
    // other request inputs, before the first await (a tab switch during the
    // upload must not send another tab's id).
    const anchorId = String((state.peaks.find(p => p.name === 'Graphite') || state.peaks[0]).id);
    // the model and its fit context as sent (F1, Codex round 1): a result must
    // not be applied, and stamped current, over a model edited while it ran
    const ctxAtRequest = _startsLiveKey();
    // Build peak specs and overlay the per-peak bounds we attached in buildAutoFitModel.
    const peakSpecs = state.peaks.map(p => {
      const spec = peakToBackendSpec(p);
      if (Number.isFinite(p._afCenterMin)) spec.center_min = p._afCenterMin;
      if (Number.isFinite(p._afCenterMax)) spec.center_max = p._afCenterMax;
      if (Number.isFinite(p._afFwhmMin))   spec.fwhm_min   = p._afFwhmMin;
      if (Number.isFinite(p._afFwhmMax))   spec.fwhm_max   = p._afFwhmMax;
      spec.amplitude_min = 0;
      return spec;
    });

    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvg };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
    const resp = await fetch('/api/fit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        background: bgPayload,
        peaks: peakSpecs,
        fit_method: fitMethod,
        n_perturb: 3,
        // step (c): is the charge-reference anchor REQUIRED? The server refits
        // the model without it; a redundant anchor must not set the energy
        // reference of a whole spectrum (see applyAutoFitResult).
        require_component: anchorId,
      }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
    // reach the parser and read as "the server's reply could not be read")
    if (resp.ok === false) {
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.httpStatus = resp.status;
      throw err;
    }
    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
    if (json.error) throw new Error(json.error);
    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinner();
      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
      _autoFitRestore(snap, fittingTab);
      return;
    }

    applyBackendResult(json);

    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
    if (!ok) {
      _hideFitSpinner();
      _autoFitRestore(snap, fittingTab);
      return;
    }

    _hideFitSpinner();
    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  } catch (e) {
    clearTimeout(timer);
    _hideFitSpinner();
    // The catch path can also fire after a mid-flight tab switch (fetch
    // error/timeout after the user moved on) — same wrong-tab hazard as
    // the explicit discard branch, so it gets the same tab-aware restore.
    _autoFitRestore(snap, fittingTab);
    let msg;
    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
      msg = 'Auto-fit exceeded the 2-minute timeout.';
    } else if (e && (e.unreadableReply || e.httpStatus)) {
      msg = 'Auto-fit failed: ' + e.message;
    } else if (e && e.message) {
      msg = 'Fit failed to converge or produced an unphysical graphite position.';
      console.warn('Auto-fit error:', e);
    } else {
      msg = 'Auto-fit failed.';
    }
    notify(msg, 'red', true);
  }
}

function isC1sTab(tab) {
  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  const ui = tab.ui || {};
  let lo = parseFloat(ui.roiMin);
  let hi = parseFloat(ui.roiMax);
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
    // Fall back to full raw range (no UI ROI set yet)
    let rmin = Infinity, rmax = -Infinity;
    for (const v of tab.rawBE) {
      if (v < rmin) rmin = v;
      if (v > rmax) rmax = v;
    }
    lo = rmin; hi = rmax;
  }
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) return false;
  const mid = (lo + hi) / 2;
  return mid >= 270.0 && mid <= 315.0;
}

// ── Scattered-starts check (2026-09-21) ───────────────────────────────────────
// Every Run Fit with two or more unlinked components asks the server for three
// more fits of the SAME method from scattered starts. The student's result
// stays THE FIT; a solution with a lower reduced chi-square is listed beside it
// with its own areas and how far each component moved from the student's start
// (a relocated component must be visible at a glance: on a committed C 1s scan
// the better-scoring solution slid C-O 1.4 eV under the main line). Solutions
// that are not better are only counted. Measured on the lab's 202 fit targets:
// an alternative appears on 0 % of re-fits of a saved solution and 7 % of
// not-yet-fitted starts, for a median +0.5 s. No certification language: the
      bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
    }
    // Transport failures (server unreachable, timeout, non-JSON reply) are
    // the ONLY reason to fall back to the local optimiser. A server-side
    // validation error or a non-converged optimisation surfaces its message
    // and leaves the model untouched (unit A0: nothing is shown as a fit
    // result unless it converged; an HTTP 400 is not a reason to silently
    // switch engines).
    // Only a genuine transport failure (network rejection, abort, a body that
    // could not be read) is marked for fallback; server errors — including a
    // 2xx body that was read but is not JSON (F2) — carry `serverError`.
    const _asTransport = (e) => {
      if (e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError' || e instanceof SyntaxError)) e.transportFailure = true;
      throw e;
    };
    let sessionId;
    try { sessionId = await uploadToBackend(be, inten); } catch (e) { _asTransport(e); }
    const fitReq = {
      session_id: sessionId,
      background: bgPayload,
      peaks: peakSpecs,
      fit_method: fitMethod,
      n_perturb: 3,
      n_starts: nStarts       // the server also skips it for the global methods
    };
    let resp, json;
    try {
      resp = await fetch('/api/fit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fitReq)
      });
    } catch (e) { _asTransport(e); }
    if (resp.ok === false) {
      // HTTP failure: read a message if the body is JSON, but a 502 HTML
      // page is still a SERVER failure, never a reason to switch engines.
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.serverError = true;
      throw err;
    }
    // F2: reading the body can fail in transport; a body that was read but is
    // not JSON is the server's reply — a failed fit, not a fallback
    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
    if (json.error) {
      const err = new Error(json.error);
      err.serverError = true;
      throw err;
    }
    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
    // result that did not converge is a failed fit, not a result (audit A08:
    // until this unit success:false was applied and announced as complete).
    if (json.success !== true) {
      const err = new Error(json.message || 'the optimizer did not converge.');
      err.notConverged = true;
      throw err;
    }
    backendResult = json;

    // If the user switched tabs while the fit was running, discard the result
    // rather than overwriting the now-active tab's peaks.
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }

    // The peak controls stay editable while the fit runs. A result computed for
    // the model as it was must not be applied over an edited one (a newly locked
    // centre would keep its edited value under the server's statistics).
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }

    // Capture pre-fit values for uncertainty validation
    const _preFit = {};
    for (const p of state.peaks) {
      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
    }
    applyBackendResult(backendResult);
    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
    const stats = backendResult.statistics || {};
    const chiReduced = stats.reduced_chi_square || 0;
    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
                        fittedY: backendResult.fitted_y, roiRange, _preFit,
                        starts: backendResult.starts || null,
                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
                        chosenAlternative: opts.chosenAlternative || null };
    // a preview of an alternative always belongs to the PREVIOUS result (an identical
    // key does not make it this one's): clear it unconditionally
    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
    state.fitResult.rFactor = _computeRFactor(state.fitResult);
    _applyStatDisplay(state.fitResult);
    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
    _updateRFactorUI(state.fitResult.rFactor);
    _updateROIDisplay(roiRange);
    _hideFitSpinner();
    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  } catch (e) {
    // Fall back to local Levenberg-Marquardt
    _hideFitSpinner();
    if (!_ownerActive(fittingTab)) {
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit cancelled — tab switched during fit.', 'amber');
      return;
    }
    if (e && e.transportFailure && opts.startPeaks) {
      // Adopting an alternative needs the server: the local engine would start
      // from the live model, not from the alternative. Nothing was changed.
      document.getElementById('sb-msg').textContent = 'Fit failed';
      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
      return;
    }
    if (e && e.transportFailure && ctxAtRequest !== null && !_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      // The fallback would fit the arrays captured at the press over a model or
      // context edited since, and stamp the edited one (F1, Codex round 1).
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('The server could not be reached, and the model or its background / ROI settings were edited while the fit was running, so no local fit was run. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }
    if (e && e.transportFailure) {
      // Server unreachable: the local optimiser is the honest fallback, and
      // the overlay saying so opens only if it actually converged.
      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
      const local = runFitLocal(be, bgSubtracted, bgIntensity);
      if (local && local.success && !_snapshotSuppressed) {
        document.getElementById('localfit-warn-overlay').classList.add('open');
      }
      return;
    }
    // Server-side error or non-converged optimisation: report it; the
    // previous peaks and fit result stay exactly as they were.
    const notConverged = !!(e && e.notConverged);
    document.getElementById('sb-msg').textContent = notConverged ? 'Fit did not converge' : 'Fit failed';
    notify((notConverged ? 'Fit did not converge: ' : 'Fit failed: ') + ((e && e.message) || 'unknown error') +
           ' Previous peaks and result kept.', 'red', true);
    return;
  }

  renderPeakList();
  updatePlot();
  renderResults();
  _autoSnapshot();
}

// Label for the goodness-of-fit statistic a fit result carries. The server
// and (since unit W1, 2026-09-18) the local engine both minimise a
  cap.innerHTML = !_isLocalFit(fr) ? '&#967;&#178;&#7523;:'
    : (_isUnweightedLocal(fr) ? 'Residual variance (starting point):' : '&#967;&#178;&#7523; (local, starting point):');
}
// The statistic is displayed as ONE unit — header text + tooltip, status-bar
// caption + value — from the same fit result, or all cleared. Refreshing
// any one of them alone can pair a local value with a chi-square caption
// (Codex round 9).
function _applyStatDisplay(fr) {
  const fq = document.getElementById('fit-quality');
  const sb = document.getElementById('sb-chi');
  const st = (fr && fr === state.fitResult) ? _statsLiveState() : 'current';
  if (fr && Number.isFinite(fr.chiReduced) && st === 'stale') {
    // F1: the statistic belongs to the previous model: say so, show no number
    if (fq) { fq.textContent = _fitStatLabel(fr) + ' \u2014 (model changed)'; fq.setAttribute('data-xps-tip', _STATS_STALE_NOTE); }
    if (sb) sb.textContent = '\u2014';
  } else if (fr && Number.isFinite(fr.chiReduced)) {
    const tip = (_isLocalFit(fr) ? _LOCALFIT_TOOLTIP : _CHISQ_TOOLTIP) + (st === 'unverified' ? '\n\n' + _STATS_UNVERIFIED_NOTE : '');
    if (fq) { fq.textContent = _fitStatusText(fr); fq.setAttribute('data-xps-tip', tip); }
    if (sb) sb.textContent = fr.chiReduced.toFixed(3);
  } else {
    if (fq) { fq.innerHTML = '&#967;&#178; &mdash;'; fq.removeAttribute('data-xps-tip'); }
    if (sb) sb.textContent = '\u2014';
  }
  _applyStatCaption(fr);
  _updateLocalModelBanner();
}

// Local Levenberg-Marquardt: the fallback engine, and the ONLY engine Batch
// Fit uses.
//
// ACCEPTANCE RULE (unit A0, 2026-09-15): this function never writes to
// state.peaks or state.fitResult unless the optimiser converged. It works on
// a copy of the peak list and commits the copy on success; on
// non-convergence the previous peaks and the previous fit result are left
// exactly as they were and the caller receives { success: false }.
//
// History: from the initial commit (f20d71b) until this unit the update
// step solved JtJ.dp = +Jt.r with r = data - model, i.e. an ASCENT step, so
// every step was rejected, lambda inflated past 1e8 and the loop returned
// the STARTING model announced as "Fit complete (local LM)". The
// convergence test also compared chi-square with itself after acceptance.
// Both are pinned by tests/js/local_lm_descent.test.js, which replays the
// committed lab project; the proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md.
function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
  const maxIter = Number.isFinite(options.maxIterations) ? options.maxIterations : 3000;
  const fail = (message, iterations) => {
    _hideFitSpinner();
    document.getElementById('sb-msg').textContent = 'Local fit failed';
    notify('Local fit did not converge: ' + message + ' Previous peaks and result kept.', 'red', true);
    return { success: false, engine: 'local', message, iterations: iterations || 0 };
  };
  if (!Array.isArray(be) || be.length < 2 ||
      !Array.isArray(bgSubtracted) || bgSubtracted.length !== be.length ||
      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
    return fail('invalid or non-finite data in the fitting region.');
  }
  // POISSON WEIGHTS (unit W1): the same weighting fitting.run_fit applies on
  // the server — sigma = sqrt(raw counts), floored at 1, where the raw
  // counts are the background-subtracted signal plus the background.
  const _w = be.map((_, i) => 1 / Math.sqrt(Math.max(bgSubtracted[i] + bgIntensity[i], 1)));
  // Work on copies: live peaks are touched only on success.
  const work = state.peaks.map(p => ({ ...p }));
  if (!work.length) return fail('no peaks to fit.');
  const workPeak = id => work.find(q => q.id === id);

  const freeParams = [];
  const paramMap = [];
  for (const p of work) {
    if (!p.linked) {
      if (!p.fixCenter)    { freeParams.push(p.center);    paramMap.push({id: p.id, param: 'center'}); }
      if (!p.fixFwhm && p.shape !== 'DSG_LA') { freeParams.push(p.fwhm); paramMap.push({id: p.id, param: 'fwhm'}); }
      if (!p.fixAmplitude) { freeParams.push(p.amplitude); paramMap.push({id: p.id, param: 'amplitude'}); }
      if ((p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) {
        freeParams.push(p.glMix); paramMap.push({id: p.id, param: 'glMix'});
      }
      if (p.shape === 'asym-GL' && !p.fixAsymmetry) {
        freeParams.push(p.asymmetry); paramMap.push({id: p.id, param: 'asymmetry'});
      }
      if (p.shape === 'DS' && !p.fixDsAlpha) {
        freeParams.push(p.dsAlpha); paramMap.push({id: p.id, param: 'dsAlpha'});
      }
      if (p.shape === 'DS' && !p.fixDsGamma) {
        freeParams.push(p.dsGamma); paramMap.push({id: p.id, param: 'dsGamma'});
      }
      if (p.shape === 'DSG_LA') {
        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
      }
      if (p.shape === 'LACX') {
        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
        // caM is HELD at its value — exactly, not rounded, not a degree of
        // freedom. LA's curve jumps where its kernel half-width changes
        // (m = 6k/7), and a smooth local optimiser cannot fit a discontinuous
        // parameter: freeing it (caM unit, 2026-09-25) stalled fits at the
        // jumps and a derivative confined to one piece failed next to the
        // no-convolution threshold (Codex rounds 1–2). The server fits m;
        // Batch Fit carries the value it is given.
      }
    }
  }
  if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');
  // F2 (2026-09-26): with at least as many free parameters as data points the
  // model passes through every point and reads as a near-perfect fit (the
  // dof below is clamped to 1) — refused, as the server refuses it. A count.
  if (freeParams.length >= be.length) {
    return fail('the model is not determined by these data: ' + freeParams.length + ' free parameters for ' +
                be.length + ' data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.');
  }

  // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
  // (owner decision 2026-09-18: zero allowed in both engines; a component at
  // its floor is an explicit outcome). The active-set step holds a parameter
  // pushed into the wall, and paramScale is floored at 1, so a zero amplitude
  // is a valid, stationary point rather than a division by zero.
  function clamp(param, v) {
    if (param === 'fwhm')         return Math.max(0.1, Math.min(15, v));
    if (param === 'amplitude')    return Math.max(0, v);
    if (param === 'glMix')        return Math.max(0, Math.min(100, v));
    if (param === 'asymmetry')    return Math.max(0, Math.min(1, v));
    if (param === 'dsAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'dsGamma')      return Math.max(0, Math.min(5.0, v));
    if (param === 'laAlpha')      return Math.max(0, Math.min(0.49, v));
zsh:1: no matches found: autofit/page*

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import sys; print(sys.executable); import lmfit; print(lmfit.__version__, lmfit.__file__)'; ls /Users/skyefortier; ls /opt/homebrew/bin/python* /opt/homebrew/Caskroom/miniforge/base/bin/python*; node --test tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/autofit_required.test.js tests/js/local_lm_descent.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 exited 1 in 6136ms:
TAP version 13
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 5.218033
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
ok 2 - a required anchor proceeds; a check that did not RUN (older server, error, main fit not converged) does not block
  ---
  duration_ms: 8.351067
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 0.783312
  type: 'test'
  ...
# Subtest: a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
ok 4 - a refit that did not converge: no verdict, and Auto-Fit refuses before any charge-correction input is touched
  ---
  duration_ms: 2.093038
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 5 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 9.14392
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 6 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 7.237959
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 7 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.944862
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 8 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 8.115154
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 9 - a converged backend result is applied (sanity)
  ---
  duration_ms: 2.746397
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 10 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.627025
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 11 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 2.608727
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 12 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 2.521552
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 13 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.52062
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 14 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.770109
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 15 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.575662
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 16 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.2675
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 17 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 2.615723
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 18 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 4.268021
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 19 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.359575
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 20 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 6.396841
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 21 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.016225
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 22 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.096386
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 23 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.681794
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 24 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.396945
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 25 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 2.551891
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 26 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.39086
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 27 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.192058
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 28 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 3.419339
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 29 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 0.969111
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 30 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 2.22349
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 31 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.30184
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 32 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 2.364305
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 33 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.600669
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 34 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 2.638369
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 35 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.277568
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 36 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.503922
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 37 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.389215
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 38 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.188938
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 39 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 2.740174
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 40 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 3.837461
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 41 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 2.706202
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 42 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.382433
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 43 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 2.307247
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 44 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 2.551354
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 45 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 2.825126
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 46 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 2.527502
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 47 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 5.346215
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 48 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 2.570253
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 49 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 4.82308
  type: 'test'
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes']
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 50 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1277.402946
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 51 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 243.794375
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 52 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 13.362226
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 53 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 9.069226
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 54 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 13.526326
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 55 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 9.148411
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 56 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.68038
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 57 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 9.666277
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 58 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 45.366163
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 59 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 24.394723
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 60 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 8.246962
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 61 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 12.507719
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 62 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 11.918002
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 63 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 9.398406
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 64 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 10.429236
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 65 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1370.357837
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 66 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 61.333144
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 67 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 21.050619
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 68 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 11.944807
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 69 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 76.410269
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 70 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1179.698853
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 71 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 20.984814
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 72 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 10.645559
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 73 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 8.901821
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 74 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1422.423877
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
ok 75 - the local engine holds LA m at its exact fractional value, free or locked, and does not count it as a degree of freedom
  ---
  duration_ms: 22.658014
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 76 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 24.914787
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 77 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 19.97419
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
ok 78 - round-2 reproducer converges with m unlocked (m is held) — exact transition m = 18/7, 61 pts at 0.03 eV
  ---
  duration_ms: 9.096782
  type: 'test'
  ...
# Subtest: round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
ok 79 - round-2 reproducer converges with m unlocked (m is held) — m = 0 data, start m = 0.001
  ---
  duration_ms: 8.779461
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 80 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 10.428489
  type: 'test'
  ...
# Subtest: the local engine refuses a model with no degrees of freedom; one more point and it fits
ok 81 - the local engine refuses a model with no degrees of freedom; one more point and it fits
  ---
  duration_ms: 25.872563
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 82 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 16.872524
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 83 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 4.480105
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 84 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 7.724517
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 85 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 6.417629
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 86 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 6.476627
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 87 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 6.289383
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 88 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 2.610957
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 89 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.073635
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 90 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 12.851778
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 91 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 4.472645
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 92 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 7.094788
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 93 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 3.126292
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 94 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 2.930186
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 95 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 3.406286
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 96 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 6.732609
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 97 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.164408
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 98 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.212449
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 99 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 3.640962
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 100 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 3.919316
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 101 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 2.474052
  type: 'test'
  ...
1..101
# tests 101
# suites 0
# pass 100
# fail 1
# cancelled 0
# skipped 0
# todo 0
# duration_ms 6128.09939

exec
/bin/zsh -lc "ls -d /Users/skyefortier/xps-app/venv /Users/skyefortier/xps-verify/venv /Users/skyefortier/xps-charge/venv; sed -n '7540,7628p' templates/index.html; sed -n '1,90p' tests/js/stale_statistics.test.js; sed -n '7900,7960p' templates/index.html; sed -n '1,110p' autofit/methods/least_squares.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
/Users/skyefortier/xps-app/venv
ls: /Users/skyefortier/xps-charge/venv: No such file or directory
ls: /Users/skyefortier/xps-verify/venv: No such file or directory
    const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
    const resp = await fetch('/api/fit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        background: bgPayload,
        peaks: peakSpecs,
        fit_method: fitMethod,
        n_perturb: 3,
        // step (c): is the charge-reference anchor REQUIRED? The server refits
        // the model without it; a redundant anchor must not set the energy
        // reference of a whole spectrum (see applyAutoFitResult).
        require_component: anchorId,
      }),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
    // reach the parser and read as "the server's reply could not be read")
    if (resp.ok === false) {
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.httpStatus = resp.status;
      throw err;
    }
    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
    if (json.error) throw new Error(json.error);
    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (!_sameFitKey(_startsLiveKey(), ctxAtRequest)) {
      _hideFitSpinner();
      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
      _autoFitRestore(snap, fittingTab);
      return;
    }

    applyBackendResult(json);

    const ok = applyAutoFitResult(json, graphiteRaw, { be: be2, inten: inten2, bgIntensity: bgI, bgSubtracted: bgSub });
    if (!ok) {
      _hideFitSpinner();
      _autoFitRestore(snap, fittingTab);
      return;
    }

    _hideFitSpinner();
    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  } catch (e) {
    clearTimeout(timer);
    _hideFitSpinner();
    // The catch path can also fire after a mid-flight tab switch (fetch
    // error/timeout after the user moved on) — same wrong-tab hazard as
    // the explicit discard branch, so it gets the same tab-aware restore.
    _autoFitRestore(snap, fittingTab);
    let msg;
    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
      msg = 'Auto-fit exceeded the 2-minute timeout.';
    } else if (e && (e.unreadableReply || e.httpStatus)) {
      msg = 'Auto-fit failed: ' + e.message;
    } else if (e && e.message) {
      msg = 'Fit failed to converge or produced an unphysical graphite position.';
      console.warn('Auto-fit error:', e);
    } else {
      msg = 'Auto-fit failed.';
    }
    notify(msg, 'red', true);
  }
}

function isC1sTab(tab) {
  if (!tab || !tab.rawBE || !tab.rawBE.length) return false;
  const ui = tab.ui || {};
  let lo = parseFloat(ui.roiMin);
  let hi = parseFloat(ui.roiMax);
  if (!Number.isFinite(lo) || !Number.isFinite(hi)) {
    // Fall back to full raw range (no UI ROI set yet)
    let rmin = Infinity, rmax = -Infinity;
    for (const v of tab.rawBE) {
      if (v < rmin) rmin = v;
      if (v > rmax) rmax = v;
    }
// Unit F1 (2026-09-25): the fit STATISTICS (chi-square, sigma, R-factor, RMSE
// and the stored fitted curve) are bound to the fit that produced them by the
// SAME model-plus-context key step (b) uses — no second mechanism. After an
// edit (or a Find Peaks apply / undo that keeps the old result over a replaced
// model) they belong to the previous model: the Results panel, header, status
// bar, R, uncertainty panel, CSV/XLSX, TSV, figure and saves say so or omit
// them. Plan: docs/superpowers/plans/2026-09-25-f1-stale-statistics.md.
//
// Functions are extracted verbatim from templates/index.html and run against
// a small DOM stub.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail('unbalanced ' + name);
}
const constLine = name => { const l = lines.find(x => x.startsWith('const ' + name)); assert.ok(l, name); return l; };

// ── a DOM stub: elements by id, attributes, textContent / innerHTML ─────────
function makeDoc() {
  const els = {};
  const mk = id => ({
    id, textContent: '', innerHTML: '', style: {}, attrs: {},
    setAttribute(k, v) { this.attrs[k] = String(v); }, getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; },
    removeAttribute(k) { delete this.attrs[k]; },
  });
  for (const id of ['results-area', 'fit-quality', 'sb-chi', 'sb-runs', 'sb-chi-caption', 'quantify-area']) els[id] = mk(id);
  return { els, getElementById: id => els[id] || null, querySelector: () => null, querySelectorAll: () => [] };
}

const STATE_FNS = ['_fitKeyCanon', '_sameFitKey', '_statsState', '_statsLiveState', '_statsRecordState', '_statsNote', '_statsSaveFields'];
const STATE_CONSTS = ['_STATS_STALE_NOTE', '_STATS_UNVERIFIED_NOTE'];

// Build a sandbox with the F1 accessor, the display functions and renderResults.
function sandbox({ liveKey = 'K1' } = {}) {
  const doc = makeDoc();
  const env = { key: liveKey, quantified: null };
  const fns = [...STATE_FNS, '_fitStatLabel', '_isUnweightedLocal', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay',
    '_updateRFactorUI', '_renderRFactorPanel', 'renderResults', '_validateUncertainties'];
  const src = [...STATE_CONSTS.map(constLine), constLine('_RFACTOR_TOOLTIP'), constLine('_LOCALFIT_TOOLTIP'), constLine('_CHISQ_TOOLTIP'),
    ...fns.map(extractFn)].join('\n');
  const state = { peaks: [], fitResult: null, rawBE: [1] };
  const api = new Function('document', 'state', 'env', `
    const _startsLiveKey = () => env.key;
    const _startsRecordKey = t => t.key;
    const _isLocalFit = fr => !!(fr && fr.engine === 'local');
    const _isLocalModel = () => false;
    const _localFitCaveat = () => '';
    const _localFitDetail = () => '';
    const _updateLocalModelBanner = () => {};
    const _escHtml = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
    const _escAttr = _escHtml;
    const _buildStderrMap = fr => {
      const out = {};
      for (const ip of ((fr && fr.backendResult && fr.backendResult.individual_peaks) || [])) out[String(ip.id)] = ip.params;
      return out;
    };
    const _peakArea = p => p.amplitude;
    const _isUnsupported = () => false;
    const _unsupportedBadge = () => '';
    const _startsPanelHtml = () => '';
    const renderQuantify = (a, t) => { env.quantified = [a, t]; };
    const getROIData = () => ({ be: [1, 2, 3] });
    const getPeak = id => state.peaks.find(p => p.id === id);
    const _UNSUPPORTED_LABEL = 'not supported by the data', _UNSUPPORTED_TIP = '';
    ${src}
    return { ${[...STATE_FNS, '_applyStatDisplay', '_updateRFactorUI', 'renderResults', '_validateUncertainties'].join(', ')} };
  `)(doc, state, env);
  return { api, doc, state, env };
}

function serverResult(key) {
  return {
    chi: 12, chiReduced: 1.2346, rmse: 7.5, be: [1, 2, 3], bgIntensity: [0, 0, 0], bgSubtracted: [1, 2, 1],
    fittedY: [1, 2, 1], rFactor: { rPct: 3.21, level: 'good' },
    backendResult: { individual_peaks: [{ id: '1', params: {
      center: { value: 284.5, stderr: 0.0123, vary: true }, fwhm: { value: 1.1, stderr: 0.0456, vary: true },
  });
  return html + '</tbody></table></div></div>';
}

// The alternative's parameters on a COPY of the current peaks (null when the
// evidence no longer describes the current model).
function _altPeaks(alt) {
  if (!_startsIfCurrent(state.fitResult, _startsLiveKey())) return null;
  const peaks = JSON.parse(JSON.stringify(state.peaks));
  if (peaks.length !== alt.components.length) return null;
  for (const c of alt.components) {
    const p = peaks.find(q => String(q.id) === String(c.id));
    if (!p) return null;
    const par = {};
    for (const k in c.params) par[k] = { value: c.params[k] };
    _applyBackendParams(p, par);
  }
  return peaks;
}

function _currentAlternative(k) {
  const st = _startsIfCurrent(state.fitResult, _startsLiveKey());
  return (st && st.ran && st.alternatives && st.alternatives[k]) || null;
}

const _STARTS_STALE_MSG = 'The model has changed since this fit. Run the fit again to compare solutions.';

function previewAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const key = 'alt:' + k;
  if (_historyPreview && _historyPreview.snapId === key) { _historyClearPreview(); return; }
  _historyPreview = { snapId: key, altKey: state.fitResult.startsModelKey, peaks, fitResult: { chiReduced: alt.chi2r } };
  _updateLocalModelBanner();
  document.querySelectorAll('.hist-row').forEach(r => r.classList.remove('hist-preview-active'));
  updatePlot();
}

// Adopting an alternative is the student's decision: explicit, undoable, and
// recorded. It is ATOMIC by construction: the alternative is only the START of
// an ordinary server fit (runFit's opts.startPeaks); the live model is written
// by that fit's success path and by nothing else, so a fit that fails, does
// not converge, is discarded because the tab changed, or cannot reach the
// server leaves peaks and result exactly as they were (no local fallback
// here: the local engine would start from the live model, not from the
// alternative). runFit's own pushUndo is the single undo entry. A solution
// that moves a component more than 1 eV from where the student put it is the
// measured trap (a lower chi-square bought by a chemically absurd relocation),
// so that case — and only that case — asks first, naming the component and
// the distance.
async function useAlternative(k) {
  const alt = _currentAlternative(k);
  const peaks = alt && _altPeaks(alt);
  if (!peaks) { notify(_STARTS_STALE_MSG, 'amber', true); return; }
  const shift = alt.largest_centre_shift_from_start;
  const name = _startsPeakName(shift.id);
  if (Math.abs(shift.ev) > _STARTS_SHIFT_RED_EV &&
      !confirm(`This solution moves ${name} by ${_startsEv(shift.ev)} from where you placed it. Apply?`)) return;
  const chosen = { fromChi: state.fitResult.starts.fit.chi2r, toChi: alt.chi2r, shiftName: name, shiftEv: shift.ev };
  if (_historyPreview) _historyClearPreview();
"""
Method 1 — classical constrained least-squares (the manual-model baseline).

Thin wrapper over the EXISTING ``fitting.run_fit`` (unchanged, same code the
manual UI uses) so the method seam has an honest baseline entry.  Consumes
explicit ``peak_specs``; no grammar required.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import numpy as np

from fitting import run_fit

from ..grammar import CandidateGrammar
from .base import MethodResult, PeakFitMethod, pop_endpoint_avg

_ALLOWED_OPTIONS = {
    "background_method", "bg_start_idx", "bg_end_idx", "endpoint_avg",
    "fit_method", "n_perturb", "manual_bg",
}


class LeastSquaresMethod(PeakFitMethod):
    id = "least_squares"
    label = "Least-squares (manual model)"
    requires_grammar = False

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
        if not peak_specs:
            raise ValueError("least_squares requires explicit peak_specs (manual model)")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown least_squares options: {sorted(unknown)}")
        fit_method = opts.pop("fit_method", None)
        fit_kws = {"method": fit_method} if fit_method else None

        res = run_fit(
            np.asarray(x, dtype=float),
            np.asarray(y, dtype=float),
            peak_specs,
            background_method=opts.pop("background_method", "shirley"),
            bg_start_idx=opts.pop("bg_start_idx", None),
            bg_end_idx=opts.pop("bg_end_idx", None),
            endpoint_avg=pop_endpoint_avg(opts),
            n_perturb=opts.pop("n_perturb", 0),
            manual_bg=opts.pop("manual_bg", None),
            fit_kws=fit_kws,
        )

        peaks = []
        confidence: dict[str, dict] = {}
        for ip in res["individual_peaks"]:
            par = ip["params"]
            rec = {"id": ip["id"]}
            for name, info in par.items():
                rec[name] = info["value"]
            peaks.append(rec)
            stderr = {name: info.get("stderr") for name, info in par.items()}
            has_cov = any(v is not None for v in stderr.values())
            confidence[str(ip["id"])] = {
                "sigma_stat": {
                    "uncertainty_kind": "covariance" if has_cov else "unavailable",
                    "values": stderr if has_cov else None,
                },
                "reference_sensitivity_range": {
                    "kind": "unavailable_single_fit", "range_ev": None,
                },
            }

        stats = res["statistics"]
        return MethodResult(
            method_id=self.id,
            success=bool(res["success"]),
            peaks=peaks,
            analysis={
                "method": self.id,
                "statistics": stats,
                "note": "manual-model baseline; no candidate enumeration",
            },
            confidence=confidence,
            diagnostics={"lmfit_message": res.get("message")},
            message=res.get("message") or "",
        )

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"; import pytest; raise SystemExit(pytest.main([\"-q\", \"-p\", \"no:cacheprovider\", \"--capture=sys\", \"tests/test_fit_acceptance_holes.py\", \"tests/test_basinhopping_outcome.py\", \"tests/test_fit_reproducibility.py\", \"-k\", \"not api_fit\"]))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "rg -n 'def basinhopping|aborted|def prepare_fit' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py | tail -45; sed -n '1680,1808p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '1150,1225p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/model.py; rg -n 'required|refit_converged' autofit --glob '*.py'; rg -n 'batch.*[Ff]it|local.message|res.message|runFitLocal\\(' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
95:    """Raised when a fit is aborted by the user."""
218:    aborted : bool
219:        Whether the fit was aborted.
534:            self.result.aborted = True
536:            self.result.message = f"Fit aborted: {m}"
538:            raise AbortFitException(f"fit aborted: too many function evaluations {self.max_nfev}")
549:            self.result.aborted = True
550:            self.result.message = "Fit aborted by user callback. Could not estimate error-bars."
552:            raise AbortFitException("fit aborted by user.")
631:    def prepare_fit(self, params=None):
689:        result.aborted = False
999:        if not result.aborted:
1022:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
1096:            raise AbortFitException("fit aborted by user.")
1426:            result.aborted = True
1427:            result.message = "Fit aborted by user callback. Could not estimate error-bars."
1435:        if not result.aborted:
1570:            result.aborted = True
1575:        if not result.aborted:
1584:        if not result.aborted:
1678:        if not result.aborted:
1684:            errmsg = 'Fit aborted.'
1726:    def basinhopping(self, params=None, max_nfev=None, **kws):
1774:        if not result.aborted:
1786:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
1926:        if not result.aborted:
2075:        if not result.aborted:
2095:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2156:        if not result.aborted:
2172:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
2235:        if not result.aborted:
2252:        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
        else:
            _best = result.last_internal_values
            _cov = None
            ier = -1
            errmsg = 'Fit aborted.'

        result.nfev -= 1
        if result.nfev >= self.max_nfev:
            result.nfev = self.max_nfev - 1
        self.result.nfev = result.nfev
        try:
            result.residual = self.__residual(_best)
            result._calculate_statistics()
        except AbortFitException:
            pass

        result.ier = ier
        result.lmdif_message = errmsg
        result.success = ier in [1, 2, 3, 4]
        if ier in {1, 2, 3}:
            result.message = 'Fit succeeded.'
        elif ier == 0:
            result.message = ('Invalid Input Parameters. I.e. more variables '
                              'than data points given, tolerance < 0.0, or '
                              'no data provided.')
        elif ier == 4:
            result.message = 'One or more variable did not affect the fit.'
        elif ier == 5:
            result.message = self._err_max_evals.format(lskws['maxfev'])
        else:
            result.message = 'Tolerance seems to be too small.'

        # self.errorbars = error bars were successfully estimated
        result.errorbars = (_cov is not None)
        if result.errorbars:
            # transform the covariance matrix to "external" parameter space
            result.covar = self._int2ext_cov_x(_cov, _best)
            # calculate parameter uncertainties and correlations
            self._calculate_uncertainties_correlations()
        else:
            result.message = f'{result.message} Could not estimate error-bars.'

        np.seterr(**orig_warn_settings)

        return result

    def basinhopping(self, params=None, max_nfev=None, **kws):
        """Use the `basinhopping` algorithm to find the global minimum.

        This method calls :scipydoc:`optimize.basinhopping` using the
        default arguments. The default minimizer is ``BFGS``, but since
        lmfit supports parameter bounds for all minimizers, the user can
        choose any of the solvers present in :scipydoc:`optimize.minimize`.

        Parameters
        ----------
        params : Parameters, optional
            Contains the Parameters for the model. If None, then the
            Parameters used to initialize the Minimizer object are used.
        max_nfev : int or None, optional
            Maximum number of function evaluations (default is None). Defaults
            to ``200000*(nvarys+1)``.
        **kws : dict, optional
            Minimizer options to pass to :scipydoc:`optimize.basinhopping`.

        Returns
        -------
        MinimizerResult
            Object containing the optimization results from the
            basinhopping algorithm.


        .. versionadded:: 0.9.10

        """
        result = self.prepare_fit(params=params)
        result.method = 'basinhopping'
        self.set_max_nfev(max_nfev, 200000*(result.nvarys+1))
        basinhopping_kws = dict(niter=100, T=1.0, stepsize=0.5,
                                minimizer_kwargs=None, take_step=None,
                                accept_test=None, callback=None, interval=50,
                                disp=False, niter_success=None, seed=None,
                                target_accept_rate=0.5, stepwise_factor=0.9)

        basinhopping_kws.update(self.kws)
        basinhopping_kws.update(kws)

        x0 = result._init_vals_internal
        result.call_kws = basinhopping_kws
        try:
            ret = scipy_basinhopping(self.penalty, x0, **basinhopping_kws)
        except AbortFitException:
            pass

        if not result.aborted:
            result.message = ret.message
            result.residual = self.__residual(ret.x)
            result.nfev -= 1
        elif result.nfev > self.max_nfev-5:
            result.nfev -= 2
            _best = result.last_internal_values
            result.residual = self.__residual(_best, False)

        result._calculate_statistics()

        # calculate the cov_x and estimate uncertainties/correlations
        if (not result.aborted and self.calc_covar and HAS_NUMDIFFTOOLS and
                len(result.residual) > len(result.var_names)):
            _covar_ndt = self._calculate_covariance_matrix(ret.x)
            if _covar_ndt is not None:
                result.covar = self._int2ext_cov_x(_covar_ndt, ret.x)
                self._calculate_uncertainties_correlations()

        return result

    def brute(self, params=None, Ns=20, keep=50, workers=1, max_nfev=None):
        """Use the `brute` method to find the global minimum of a function.

        The following parameters are passed to :scipydoc:`optimize.brute`
        and cannot be changed:

        +-------------------+-------+------------------------------------+
        | :meth:`brute` arg | Value | Description                        |
        +===================+=======+====================================+
        |  `full_output`    | 1     | Return the evaluation grid and the |
        |                   |       | objective function's values on it. |
        +-------------------+-------+------------------------------------+
        |  `finish`         | None  | No "polishing" function is to be   |
        |                   |       | used after the grid search.        |
        if self.nan_policy == 'omit':
            mask = ~isnull(data)
            if mask is not None:
                data = data[mask]
            if weights is not None:
                weights = _align(weights, mask, data)

        # If independent_vars and data are alignable (pandas), align them,
        # and apply the mask from above if there is one.
        for var in self.independent_vars:
            if var not in params and var not in self.opts:
                if var not in kwargs:
                    raise ValueError(f"'Missing independent variable '{var}'")
                if not np.isscalar(kwargs[var]):
                    kwargs[var] = _align(kwargs[var], mask, data)

        if coerce_farray:
            # coerce data and independent variable(s) that are 'array-like' (list,
            # tuples, pandas Series) to float64/complex128.
            data = coerce_arraylike(data)
            for var in self.independent_vars:
                if var not in params and var in kwargs:
                    kwargs[var] = coerce_arraylike(kwargs[var])

        if fit_kws is None:
            fit_kws = {}

        output = ModelResult(self, params, method=method, iter_cb=iter_cb,
                             scale_covar=scale_covar, fcn_kws=kwargs,
                             nan_policy=self.nan_policy, calc_covar=calc_covar,
                             max_nfev=max_nfev, **fit_kws)
        output.fit(data=data, weights=weights)
        output.components = self.components
        return output

    def __add__(self, other):
        """+"""
        return CompositeModel(self, other, operator.add)

    def __sub__(self, other):
        """-"""
        return CompositeModel(self, other, operator.sub)

    def __mul__(self, other):
        """*"""
        return CompositeModel(self, other, operator.mul)

    def __truediv__(self, other):
        """/"""
        return CompositeModel(self, other, operator.truediv)


class CompositeModel(Model):
    """Combine two models (`left` and `right`) with binary operator (`op`).

    Normally, one does not have to explicitly create a `CompositeModel`,
    but can use normal Python operators ``+``, ``-``, ``*``, and ``/`` to
    combine components as in::

    >>> mod = Model(fcn1) + Model(fcn2) * Model(fcn3)

    """

    _known_ops = {operator.add: '+', operator.sub: '-',
                  operator.mul: '*', operator.truediv: '/'}

    def __init__(self, left, right, op, **kws):
        """
        Parameters
        ----------
        left : Model
            Left-hand model.
        right : Model
            Right-hand model.
        op : callable binary operator
            Operator to combine `left` and `right` models.
autofit/cited_values.py:103:        raise _reject(i, f"missing required field(s) {sorted(missing)}")
autofit/cited_values.py:128:                         "a real source citation is required")
autofit/engine.py:2674:                "at %s (%s; region-unassigned; human assignment required)",
autofit/methods/least_squares.py:6:explicit ``peak_specs``; no grammar required.
autofit/methods/ic_model_comparison.py:95:                         "prescriptive: manual attention required)"
autofit/methods/multivariate_mcr.py:29:``build_matrix``).  A grammar is NOT required (requires_grammar=False) —
1905:      <button class="btn peak-fit-control" id="btn-batch-fit" onclick="showPropagateModal()" title="Propagate fit model to other spectra">Batch Fit</button>
8143:      const local = runFitLocal(be, bgSubtracted, bgIntensity);
8304:function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
12217:  // Loud missing-load guard (mirrors the RefCore guard): batch fit depends on the
12331:    const outcome = runFitLocal(be, bgSub, bgI);

exec
/bin/zsh -lc "sed -n '740,850p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py; sed -n '680,716p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py; sed -n '790,810p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/model.py; sed -n '12298,12365p' templates/index.html; sed -n '785,870p' app.py; rg -n 'isfinite|dropna|isnan' parser.py app.py vgd_parser.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
    """

    def __init__(self, name, value=None, vary=True, min=-inf, max=inf,
                 expr=None, brute_step=None, user_data=None):
        """
        Parameters
        ----------
        name : str
            Name of the Parameter.
        value : float, optional
            Numerical Parameter value.
        vary : bool, optional
            Whether the Parameter is varied during a fit (default is True).
        min : float, optional
            Lower bound for value (default is ``-numpy.inf``, no lower
            bound).
        max : float, optional
            Upper bound for value (default is ``numpy.inf``, no upper
            bound).
        expr : str, optional
            Mathematical expression used to constrain the value during the
            fit (default is None).
        brute_step : float, optional
            Step size for grid points in the `brute` method (default is
            None).
        user_data : optional
            User-definable extra attribute used for a Parameter (default
            is None).

        Attributes
        ----------
        stderr : float
            The estimated standard error for the best-fit value.
        correl : dict
            A dictionary of the correlation with the other fitted
            Parameters of the form::

            {'decay': 0.404, 'phase': -0.020, 'frequency': 0.102}

        """
        self.name = name
        self.user_data = user_data
        self.init_value = value
        self.min = min
        self.max = max
        self.brute_step = brute_step
        self._vary = vary
        self._expr = expr
        self._expr_ast = None
        self._expr_eval = None
        self._expr_deps = []
        self._delay_asteval = False
        self.stderr = None
        self.correl = None
        self.from_internal = lambda val: float(val)
        self._val = value
        self._init_bounds()

    def set(self, value=None, vary=None, min=None, max=None, expr=None,
            brute_step=None, is_init_value=True):
        """Set or update Parameter attributes.

        Parameters
        ----------
        value : float, optional
            Numerical Parameter value.
        vary : bool, optional
            Whether the Parameter is varied during a fit.
        min : float, optional
            Lower bound for value. To remove a lower bound you must use
            ``-numpy.inf``.
        max : float, optional
            Upper bound for value. To remove an upper bound you must use
            ``numpy.inf``.
        expr : str, optional
            Mathematical expression used to constrain the value during the
            fit. To remove a constraint you must supply an empty string.
        brute_step : float, optional
            Step size for grid points in the `brute` method. To remove the
            step size you must use ``0``.
        is_init_value: bool, optional
            Whether to set value as `init_value`, when setting value.

        Notes
        -----
        Each argument to `set()` has a default value of None, which will
        leave the current value for the attribute unchanged. Thus, to lift
        a lower or upper bound, passing in None will not work. Instead,
        you must set these to ``-numpy.inf`` or ``numpy.inf``, as with::

            par.set(min=None)        # leaves lower bound unchanged
            par.set(min=-numpy.inf)  # removes lower bound

        Similarly, to clear an expression, pass a blank string, (not
        None!) as with::

            par.set(expr=None)  # leaves expression unchanged
            par.set(expr='')    # removes expression

        Explicitly setting a value or setting ``vary=True`` will also
        clear the expression.

        Finally, to clear the brute_step size, pass ``0``, not None::

            par.set(brute_step=None)  # leaves brute_step unchanged
            par.set(brute_step=0)     # removes brute_step

        """
        if vary is not None:
            self._vary = vary
            if vary:
        # determine which parameters are actually variables
        # and which are defined expressions.
        result.var_names = []  # note that this *does* belong to self...
        result.init_vals = []
        result._init_vals_internal = []
        result.params.update_constraints()
        result.nfev = 0
        result.call_kws = {}
        result.errorbars = False
        result.aborted = False
        result.success = True
        result.covar = None

        for name, par in self.result.params.items():
            par.stderr = None
            par.correl = None
            if par.expr is not None:
                par.vary = False
            if par.vary:
                result.var_names.append(name)
                result._init_vals_internal.append(par.setup_bounds())
                result.init_vals.append(par.value)

            par.init_value = par.value
            if par.name is None:
                par.name = name
        result.nvarys = len(result.var_names)
        result.init_values = {n: v for n, v in zip(result.var_names,
                                                   result.init_vals)}

        # set up reduce function for scalar minimizers
        #    1. user supplied callable
        #    2. string starting with 'neglogc' or 'negent'
        #    3. sum-of-squares
        if not callable(self.reduce_fcn):
            if isinstance(self.reduce_fcn, str):
                if self.reduce_fcn.lower().startswith('neglogc'):
            par._delay_asteval = True
            for item in self._hint_names:
                if item in hint:
                    setattr(par, item, hint[item])
            if basename in kwargs:
                setpar(par, kwargs[basename])
            # Add the new parameter to self._param_names
            if name not in self._param_names:
                self._param_names.append(name)

        # check for parameters that were initially flagged as independent
        # variables because the function signature used "key=None", "key=True",
        # or "key=False": these could actually be variables
        for key, val in kwargs.items():
            if key in params:
                continue
            if key in self.independent_vars:
                dxval = self.independent_vars_defvals.get(key, inspect._empty)
                if dxval is None or isinstance(dxval, bool):
                    name = f"{self._prefix}{key}"
                    par = Parameter(name=name)
    tgt.fitResult = null;
    tgt.modelProvenance = srcProvenance ? { ...srcProvenance, copiedFrom: sourceTab.name } : null;

    // Now activate this tab so state is populated. activateTab is a no-op
    // when the target is ALREADY active (the user switched to it during the
    // previous target's fit): then live state still holds the target's old
    // model and the post-fit sync would overwrite the propagated record —
    // load the record into live state explicitly (Codex round 3, run B).
    if (tabManager.activeId === tid) {
      state.peaks = tgt.peaks; state.nextId = tgt.nextId; state.ccShift = tgt.ccShift;
      state.fitResult = null;   // live copy of tgt.fitResult = null above (unit A0)
      tabManager._restoreUI(tgt.ui);
      renderPeakList();
      _refreshRoiAndCentreWarnings();   // this branch does not redraw: the hint must describe the target's window (Codex round 2)
    } else {
      tabManager.activateTab(tid);
    }

    // Small yield so progress message renders
    await new Promise(r => setTimeout(r, 20));
    if (_activeTab() !== tgt) {
      // The user switched tabs during the yield: fitting would read and
      // write whichever tab is active now. Stop here; targets already
      // fitted keep their results.
      notify('Batch fit stopped at ' + tgt.name + ' — the tab changed while it was running.', 'amber');
      break;
    }

    // Run local fit
    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
    const { be, inten } = getROIData();
    const bgI = computeBackground(be, inten);
    const bgSub = inten.map((v, idx) => v - bgI[idx]);
    const outcome = runFitLocal(be, bgSub, bgI);

    // Sync result back to record
    tabManager._syncActiveToRecord();

    // Read the statistic from the fit's own return value, not from live
    // state: the active tab can change while the fit runs.
    const ok = !!(outcome && outcome.success);
    results.push({ name: tgt.name, ok, roiHint: _roiHintFor(roiSt),
                   chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
                   message: ok ? null : ((outcome && outcome.message) || 'local fit did not converge') });

    await new Promise(r => setTimeout(r, 10));
  }

  _snapshotSuppressed = false;

  // Return to source tab
  tabManager.activateTab(sourceId);

  const nOk = results.filter(r => r.ok).length;
  const nFail = results.length - nOk;
  prog.textContent = `Batch complete: ${nOk} converged as starting points, ${nFail} not fitted. Run Fit on each spectrum before reporting.`;
  const roiNote = r => r.roiHint ? ` <span class="roi-hint${r.roiHint.cls ? ' ' + r.roiHint.cls : ''}" style="display:inline">${_escHtml(r.roiHint.text)}</span>` : '';
  summary.innerHTML = results.map(r => r.ok
    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)${roiNote(r)}</div>`
    : `<div class="prop-row" style="color:var(--red,#f87171)">${_escHtml(r.name)}: NOT fitted &mdash; ${_escHtml(r.message)} (model copied, no result stored)${roiNote(r)}</div>`
  ).join('') + `<div class="prop-row" style="color:var(--red,#f87171);margin-top:4px">&#9888; Charge corrections marked in red need verification</div>`;
  summary.style.display = 'block';
  btn.disabled = false;
}

// ══════════════════════════════════════════════════════════════
// FEATURE 2: NIST XPS DATABASE — CHEMICAL STATE LOOKUP
// ══════════════════════════════════════════════════════════════
        try:
            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
        except KeyError:
            return _err(f"Session '{session_id}' not found", 404)

        # Background config
        bg_cfg = body.get("background", {})
        bg_method = bg_cfg.get("method", "shirley")
        bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
        bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
        try:
            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
        except (TypeError, ValueError):
            return _err("endpoint_avg must be an integer")
        manual_bg = bg_cfg.get("manual_bg")

        # Peak specs
        peak_specs = body.get("peaks", [])
        if not peak_specs:
            return _err("'peaks' list is empty – provide at least one peak")

        # Validate peak ids are unique
        ids = [p.get("id") for p in peak_specs]
        if len(ids) != len(set(ids)):
            return _err("Duplicate peak ids found – each peak must have a unique 'id'")

        _ALLOWED_METHODS = {
            "leastsq", "least_squares", "nelder",
            "differential_evolution", "basinhopping",
        }
        fit_method = body.get("fit_method", "leastsq")
        if fit_method not in _ALLOWED_METHODS:
            return _err(f"Unknown fit_method '{fit_method}'")

        # Bounded, type-checked n_perturb (audit F7; also covers the F9
        # ValueError-on-bad-input case for this field). Reject out-of-range or
        # non-integer values with a clean 400 instead of a 500 or a worker hang.
        try:
            n_perturb = int(body.get("n_perturb", 5))
        except (TypeError, ValueError):
            return _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
        if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
            return _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")

        # Scattered-starts check (optional; the page sends 3). Same clean-400
        # treatment as n_perturb; run_fit validates again for other callers.
        n_starts = body.get("n_starts", 0)
        if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
            return _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
        # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
        require_component = body.get("require_component")
        if require_component is not None and not isinstance(require_component, (str, int)):
            return _err("require_component must be a peak id")

        try:
            result = fitting.run_fit(
                energy=energy,
                counts=counts,
                peak_specs=peak_specs,
                background_method=bg_method,
                bg_start_idx=bg_start,
                bg_end_idx=bg_end,
                charge_shift_ev=0.0,
                fit_kws={"method": fit_method},
                manual_bg=manual_bg,
                n_perturb=n_perturb,
                endpoint_avg=endpoint_avg,
                n_starts=n_starts,
                require_component=require_component,
            )
        except ValueError as exc:
            # Our own validation: unknown shape/method, self/circular constraint,
            # "Master peak not found", bad numeric field, etc. (audit F10/F11).
            return _err(str(exc))
        except RuntimeError:
            # Solver-internal failure (e.g. lmfit non-convergence). Log the
            # detail; return a generic 422 that leaks no library internals.
            app.logger.exception("Fit failed")
            return _err("Fit failed — see server log for details.", 422)
        except Exception:
            app.logger.exception("Unexpected fitting error")
            return _err("Internal fitting error — see server log.", 500)

        return jsonify(result)

app.py:103:    if isinstance(obj, float) and not np.isfinite(obj):
parser.py:130:    df.dropna(axis=1, how="all", inplace=True)
parser.py:145:            df2.dropna(axis=1, how="all", inplace=True)
parser.py:160:    mask = np.isfinite(energy) & np.isfinite(counts)
parser.py:205:        df.dropna(axis=1, how="all", inplace=True)
parser.py:206:        df.dropna(axis=0, how="all", inplace=True)
parser.py:211:            mask = np.isfinite(energy) & np.isfinite(counts)
parser.py:408:    plausible = np.isfinite(all_floats) & (all_floats >= 0) & (all_floats < 1e9)
parser.py:483:    if not np.all(np.isfinite(arr)):

codex
The JavaScript run passed 100 tests; one parity test could not start its Python backend because the read-only sandbox blocks a temporary-directory probe. Python checks are now running with that probe bypassed in memory. So far, I haven’t found a path that accepts an unverified basinhopping result or sends a parsed NaN reply to the local fallback.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"
import numpy as np, fitting
from unittest.mock import patch
x=np.linspace(280.,292.,31); y=200+5000*np.exp(-4*np.log(2)*((x-284.8)/1.2)**2)
specs=[dict(id=\"1\",shape=\"gaussian\",center=284.6,fwhm=1.,amplitude=4000.,amplitude_min=0),dict(id=\"2\",shape=\"gaussian\",center=286.6,fwhm=1.,amplitude=1500.,constrain_to=\"1\",splitting=2.,ratio=.5)]
real=fitting.Model.fit; seen=[]
def spy(self,data,params,**kw):
    r=real(self,data,params,**kw)
    seen.append((kw.get(\"method\"),r.success,getattr(r,\"aborted\",None),r.nvarys,{n:(p.expr,p.min,p.max) for n,p in r.params.items()}))
    return r
with patch.object(fitting.Model,\"fit\",spy):
    r=fitting.run_fit(x,y,specs,background_method=\"none\",fit_kws={\"method\":\"basinhopping\",\"max_nfev\":2},n_perturb=3)
print(\"ABORT_LINKED\",r[\"success\"],r[\"message\"],r[\"statistics\"])
for s in seen: print(s)
for bad in [np.nan,np.inf]:
    yy=y[:4].copy(); yy[-1]=bad
    try: fitting.run_fit(x[:4],yy,specs[:1],background_method=\"none\",fit_kws={\"method\":\"least_squares\"})
    except Exception as e: print(\"NONFINITE_Y\",bad,type(e).__name__,str(e))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "sed -n '1,105p' tests/js/local_lm_descent.test.js; sed -n '1,90p' tests/test_component_required.py; rg -n 'basinhopping|seed|n_perturb' tests/test_component_required.py; nl -ba templates/index.html | sed -n '7415,7430p;7557,7572p;7597,7615p'; rg -n 'create_app|makedirs|mkdir' app.py | head -15" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
// Local Levenberg–Marquardt: it must DESCEND and it must never present a
// non-converged attempt as a result (unit A0, 2026-09-15).
//
// Background: from the initial commit (f20d71b) until this unit, runFitLocal
// solved JᵀJ·dp = +Jᵀr with r = data − model, so every step was an ascent
// step, no step was ever accepted, and after 24 rejections λ passed 1e8 and
// the loop exited with the STARTING parameters, announced as "Fit complete
// (local LM)". Every Batch Fit called that path. The empirical proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md; this file is
// that proof turned into a regression test on the SHIPPED functions.
//
// Everything under test is extracted verbatim from templates/index.html by
// function name (brace-matched) — the same functions the browser runs.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found in templates/index.html`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts', '_fitKeyCanon', '_sameFitKey', '_statsState', '_statsLiveState'];
const CAVEAT_CONST = (html.match(/^const (_LOCAL_FIT_CAVEAT\w*|_STATS_\w+_NOTE) = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
  return { be, bgSub, bg, initial: JSON.parse(JSON.stringify(cloned)) };
}

// The objective the local engine minimises since unit W1: the Poisson-weighted
// sum of squares, w = 1/sqrt(max(raw counts, 1)), raw = bgSub + bg.
function residualSS(env, be, bgSub, bg) {
  const m = env.evalAllPeaks(be, env.state.peaks);
  return be.reduce((s, _, i) => { const raw = bgSub[i] + (bg ? bg[i] : 0); return s + (bgSub[i] - m[i]) ** 2 / Math.max(raw, 1); }, 0);
}

test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
  const tabs = loadProjectTabs();
  for (const target of ['C1s Scan_0', 'C1s Scan_4', 'C1s Scan_8']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
"""'Is this component REQUIRED?' — the refit test (unit step (c), 2026-09-22).

`support` holds the other components at their fitted values, so redundancy
under overlap escapes it (Auto-Fit anchor unit, Codex round 6: a large
Graphite component the other components could absorb if refitted). The refit
without the component is the test for that. It costs one fit, so it runs
only when asked (`require_component`); Auto-Fit asks for its anchor.
"""

import io

import numpy as np
import pytest

import fitting
from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _gl(x, a, c, w, mix=0.3):
    return fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=mix)


def _agl(x, a, c, w):
    return fitting._SHAPE_FUNCS["asymmetric_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=0.3, asymmetry=0.25)


X = np.round(np.arange(280.0, 295.0001, 0.02), 4)


def _autofit_model(graphite_amp, others):
    specs = [{"id": "1", "name": "Graphite", "shape": "asymmetric_gl", "center": 284.5, "center_min": 284.2, "center_max": 284.8,
              "amplitude": graphite_amp, "fwhm": 0.7, "gl_ratio": 0.3, "asymmetry": 0.25, "asymmetry_min": 0.1, "asymmetry_max": 0.5,
              "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0}]
    for k, (a, c, w) in enumerate(others, start=2):
        specs.append({"id": str(k), "shape": "pseudo_voigt_gl", "center": c, "amplitude": a, "fwhm": w, "gl_ratio": 0.3,
                      "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0})
    return specs


KW = dict(background_method="manual", manual_bg=[[280.0, 1000.0], [295.0, 1000.0]], n_perturb=3,
          fit_kws={"method": "least_squares"})


@pytest.mark.parametrize("method", ["least_squares", "leastsq"])
def test_a_redundant_anchor_is_supported_but_not_required(method):
    # Codex, Auto-Fit anchor unit round 6 (run B): two symmetric GL lines at
    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. In that reproduction the
    # full fit kept a LARGE Graphite (amplitude 1,081-1,894, held-others F ~
    # 1e6) because it stopped in a minimum where the anchor carries weight;
    # yet the other two components fit the data to rounding precision
    # without it.
    #
    # The premise is posed deterministically by HOLDING the anchor at 1,500
    # (inside that observed range). Until 2026-09-25 this test instead
    # started the other components at the exact truth, which lets the fit
    # drive the anchor to residue (~0.01) - the premise never formed, the
    # held-others F landed at 11-24 against the threshold of 10, and
    # Trust-Region's documented last-digit jitter (identical seed in every
    # process) moved it across: the test passed 2 of 3 runs on main. Now
    # F ~ 4e7 and the refit without the anchor is ~1e4 x better, under both
    # methods, in every process.
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1500, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs[0]["fix_amplitude"] = True
    kw = dict(KW, fit_kws={"method": method})
    res = fitting.run_fit(X, y, specs, require_component="1", **kw)
    assert res["success"] is True
    g = next(ip for ip in res["individual_peaks"] if ip["id"] == "1")
    assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
    req = res["required"]
    assert req["ran"] is True and req["refit_converged"] is True
    assert req["chi2_without_refit"] < 1e-2 * req["chi2_with"]
    assert req["required"] is False


def test_a_real_graphite_anchor_is_required():
    rng = np.random.default_rng(0)
    y = rng.poisson(1000 + _agl(X, 86000, 284.5, 0.7) + _gl(X, 14000, 285.1, 1.9) + _gl(X, 2300, 286.4, 1.4)).astype(float)
    specs = _autofit_model(80000, [(14000, 285.1, 1.9), (2300, 286.4, 1.4)])
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    req = res["required"]
48:KW = dict(background_method="manual", manual_bg=[[280.0, 1000.0], [295.0, 1000.0]], n_perturb=3,
66:    # Trust-Region's documented last-digit jitter (identical seed in every
140:    res = fitting.run_fit(X, y, specs, require_component="1", **{**KW, "n_perturb": 0, "fit_kws": {"method": "differential_evolution"}})
145:def test_the_refit_of_a_stochastic_method_is_seeded(monkeypatch):
146:    seeds = []
150:        seeds.append((kw.get("method"), (kw.get("fit_kws") or {}).get("seed")))
156:    fitting.run_fit(X, y, specs, require_component="1", **{**KW, "n_perturb": 0, "fit_kws": {"method": "basinhopping"}})
157:    bh = [s for m, s in seeds if m == "basinhopping"]
  7415	  const text = await resp.text();                 // rejects only on transport
  7416	  try { return JSON.parse(text); } catch (_) {
  7417	    const nonFinite = /(^|[\[,:\s])(-?Infinity|NaN)([\],\x7d\s]|$)/.test(text);   // \x7d = closing brace
  7418	    const err = new Error(nonFinite
  7419	      ? 'The server\'s reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.'
  7420	      : 'The server\'s reply could not be read. The fit is treated as failed.');
  7421	    err.serverError = true;
  7422	    err.unreadableReply = true;
  7423	    throw err;
  7424	  }
  7425	}
  7426	
  7427	async function runAutoFitC1sGraphite() {
  7428	  // Pre-conditions
  7429	  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  7430	  const tab = tabManager._getTab(tabManager.activeId);
  7557	    clearTimeout(timer);
  7558	    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
  7559	    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
  7560	    // reach the parser and read as "the server's reply could not be read")
  7561	    if (resp.ok === false) {
  7562	      let msg = null;
  7563	      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
  7564	      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
  7565	      err.httpStatus = resp.status;
  7566	      throw err;
  7567	    }
  7568	    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
  7569	    if (json.error) throw new Error(json.error);
  7570	    if (json.success !== true) throw new Error(json.message || 'fit did not converge');
  7571	    if (!_ownerActive(fittingTab)) {
  7572	      _hideFitSpinner();
  7597	    _hideFitSpinner();
  7598	    // The catch path can also fire after a mid-flight tab switch (fetch
  7599	    // error/timeout after the user moved on) — same wrong-tab hazard as
  7600	    // the explicit discard branch, so it gets the same tab-aware restore.
  7601	    _autoFitRestore(snap, fittingTab);
  7602	    let msg;
  7603	    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {
  7604	      msg = 'Auto-fit exceeded the 2-minute timeout.';
  7605	    } else if (e && (e.unreadableReply || e.httpStatus)) {
  7606	      msg = 'Auto-fit failed: ' + e.message;
  7607	    } else if (e && e.message) {
  7608	      msg = 'Fit failed to converge or produced an unphysical graphite position.';
  7609	      console.warn('Auto-fit error:', e);
  7610	    } else {
  7611	      msg = 'Auto-fit failed.';
  7612	    }
  7613	    notify(msg, 'red', true);
  7614	  }
  7615	}
5:    gunicorn "app:create_app()" -w 4 -b 0.0.0.0:5000
65:def create_app(upload_folder: str = "uploads", data_folder: str = "data/xps") -> Flask:
72:    Path(upload_folder).mkdir(parents=True, exist_ok=True)
1143:app = create_app()

 succeeded in 1638ms:
/Users/skyefortier/.matplotlib is not a writable directory
ABORT_LINKED True `ftol` termination condition is satisfied. {'chi_square': 13626.225935010043, 'reduced_chi_square': 486.6509262503587, 'r_factor': 0.7532806633119311, 'n_data': 31, 'n_free_params': 3, 'aic': 194.65869602428288, 'bic': 198.9606576377383}
('basinhopping', False, True, 3, {'p1_amplitude': (None, 0, inf), 'p1_center': (None, 282.6, 286.6), 'p1_fwhm': (None, 0.1, 15.0), 'p2_amplitude': ('p1_amplitude * 1.0', -inf, inf), 'p2_center': ('p1_center + 2.0', -inf, inf), 'p2_fwhm': ('p1_fwhm', -inf, inf)})
('least_squares', True, False, 3, {'p1_amplitude': (None, 0, inf), 'p1_center': (None, 282.6, 286.6), 'p1_fwhm': (None, 0.1, 15.0), 'p2_amplitude': ('p1_amplitude * 1.0', -inf, inf), 'p2_center': ('p1_center + 2.0', -inf, inf), 'p2_fwhm': ('p1_fwhm', -inf, inf)})
('least_squares', True, False, 3, {'p1_amplitude': (None, 0, inf), 'p1_center': (None, 282.6, 286.6), 'p1_fwhm': (None, 0.1, 15.0), 'p2_amplitude': ('p1_amplitude * 1.0', -inf, inf), 'p2_center': ('p1_center + 2.0', -inf, inf), 'p2_fwhm': ('p1_fwhm', -inf, inf)})
NONFINITE_Y nan ValueError The model is not determined by these data: 3 free parameters for 3 data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.
NONFINITE_Y inf ValueError The model is not determined by these data: 3 free parameters for 3 data points leaves no degrees of freedom. Widen the fitted range, remove components or lock parameters.

exec
/bin/zsh -lc "sed -n '126,170p' tests/test_component_required.py; rg -n 'box_unverified|refit_not_converged' tests/test_component_required.py tests/test_de_bounds.py; sed -n '800,820p' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/model.py; rg -n 'best_fit =' /Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/model.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
    specs3 = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)]) + [_linked("10", "9", 0.8), _linked("9", "3", 0.8)]
    res3 = fitting.run_fit(X, y, specs3, require_component="1", **KW)
    assert res3["required"]["ran"] is True, res3["required"]
    specs4 = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs4 = [specs4[0], specs4[1], _linked("4", "3", 0.8), specs4[2]]
    specs4[2]["constrain_to"] = "3"; specs4.append(_linked("5", "4", 0.8)); specs4 = [specs4[0], specs4[1], specs4[4], specs4[2], specs4[3]]
    res4 = fitting.run_fit(X, y, specs4, require_component="1", **KW)
    assert res4["required"]["ran"] is True, res4["required"]


def test_differential_evolution_goes_through_its_own_candidate_machinery():
    # Codex round 1: a direct model.fit under DE failed on the open amplitude bound -> ran:false
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    res = fitting.run_fit(X, y, specs, require_component="1", **{**KW, "n_perturb": 0, "fit_kws": {"method": "differential_evolution"}})
    assert res["success"] is True and res["required"]["ran"] is True, res["required"]
    assert res["required"]["required"] is False


def test_the_refit_of_a_stochastic_method_is_seeded(monkeypatch):
    seeds = []
    real_fit = fitting.Model.fit

    def spy(self, data, params, **kw):
        seeds.append((kw.get("method"), (kw.get("fit_kws") or {}).get("seed")))
        return real_fit(self, data, params, **kw)

    monkeypatch.setattr(fitting.Model, "fit", spy)
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4)])
    fitting.run_fit(X, y, specs, require_component="1", **{**KW, "n_perturb": 0, "fit_kws": {"method": "basinhopping"}})
    bh = [s for m, s in seeds if m == "basinhopping"]
    assert len(bh) == 2 and all(isinstance(s, int) for s in bh) and bh[0] != bh[1]


def test_known_limit_noise_free_exact_fit_reports_a_redundant_component_as_required():
    # Two identical half-amplitude components on noise-free data: removing one
    # is lossless, but the full fit is exact to machine precision (chi2 ~1e-28)
    # so F is meaningless and reads as huge. Every tolerance tried to handle
    # this masked a real anchor at high dynamic range (Codex rounds 2-3), so
    # none is applied: this is a documented limit, not a rule. Real data never
    # fit to machine precision.
    y = 1000 + _gl(X, 10000, 284.8, 1.4)                                     # unrounded: numerically exact
    specs = [{"id": "1", "name": "Graphite", "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 5000.0, "fwhm": 1.4, "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": "2", "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 5000.0, "fwhm": 1.4, "gl_ratio": 0.3, "amplitude_min": 0}]
rg: tests/test_de_bounds.py: No such file or directory (os error 2)
        # check for parameters that were initially flagged as independent
        # variables because the function signature used "key=None", "key=True",
        # or "key=False": these could actually be variables
        for key, val in kwargs.items():
            if key in params:
                continue
            if key in self.independent_vars:
                dxval = self.independent_vars_defvals.get(key, inspect._empty)
                if dxval is None or isinstance(dxval, bool):
                    name = f"{self._prefix}{key}"
                    par = Parameter(name=name)
                    setpar(par, val)
                    params.add(par)

        for p in params.values():
            p._delay_asteval = False
        return params

    def guess(self, data, x, **kws):
        """Guess starting values for the parameters of a Model.

1587:        self.best_fit = self.model.eval(params=_ret.params, **self.userkws)
2042:        self.best_fit = self.model.eval(self.params, **self.userkws)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"
import numpy as np, fitting
from unittest.mock import patch
x=np.linspace(280,292,41)
y=100+1000*np.exp(-4*np.log(2)*((x-284)/1.)**2)+500*np.exp(-4*np.log(2)*((x-288)/1.)**2)
s=[dict(id=\"1\",shape=\"gaussian\",center=284,fwhm=1,amplitude=950,amplitude_min=0),dict(id=\"2\",shape=\"gaussian\",center=288,fwhm=1,amplitude=450,amplitude_min=0)]
real=fitting.Model.fit; records=[]
def stop_reduced(self,data,params,**kw):
    reduced=len(self.components)==1
    if reduced and kw.get(\"method\")==\"least_squares\": kw[\"max_nfev\"]=1
    r=real(self,data,params,**kw)
    records.append((reduced,kw.get(\"method\"),r.success,r.chisqr))
    return r
with patch.object(fitting.Model,\"fit\",stop_reduced):
    r=fitting.run_fit(x,y,s,background_method=\"linear\",n_perturb=0,require_component=\"1\",fit_kws={\"method\":\"differential_evolution\"})
print(\"REQUIRED\",r[\"success\"],r[\"required\"])
print(\"SOLVERS\",records)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
exec
/bin/zsh -lc "node -e 'const fs=require(\"fs\"); const h=fs.readFileSync(\"templates/index.html\",\"utf8\"); const src=h.slice(h.indexOf(\"async function _readFitReply(\"),h.indexOf(\"async function runAutoFitC1sGraphite(\")); const f=new Function(src+\";return _readFitReply\")(); (async()=>{for(const body of [JSON.stringify({success:true,message:\"contains NaN in label\"}),JSON.stringify({success:true,message:\"contains NaN in label\"}).slice(0,-1)]){try{console.log(\"parsed\",await f({text:async()=>body}));}catch(e){console.log(\"rejected\",e.message)}}})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 0ms:
parsed { success: true, message: 'contains NaN in label' }
rejected The server's reply contains a non-finite number (NaN or Infinity), usually an uncertainty that could not be computed because these data do not determine the model. The fit is treated as failed.

 succeeded in 3905ms:
/Users/skyefortier/.matplotlib is not a writable directory
REQUIRED True {'ran': True, 'required': True, 'f': 2.9204584899044237e+31, 'chi2_with': 1.1923167296808578e-27, 'chi2_without_refit': 2984.6670135870336, 'refit_converged': True}
SOLVERS [(False, 'differential_evolution', False, np.float64(1.766286262007434e-12)), (False, 'least_squares', True, np.float64(4.165320870876605e-24)), (False, 'least_squares', True, np.float64(1.1923167296808578e-27)), (True, 'differential_evolution', True, np.float64(2984.6670135870336)), (True, 'least_squares', False, np.float64(2984.667013587029)), (True, 'least_squares', False, np.float64(2984.6670135869113))]

codex
I reproduced a required-refit acceptance hole with differential evolution. If its boxed search converges but both local verification fits stop early, the new guard reports `refit_converged: true` and can return `required: true`. That candidate carries `box_unverified`, which would make it fail the main-fit acceptance rule, but the required-refit guard checks only `success`.

The basinhopping abort/link probes passed: refinement preserved the expressions and bounds. The determinacy check also correctly refused data with too few finite observations.
 exited 2 in 154427ms:
.............
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/model.py:902: KeyboardInterrupt
(to show a full traceback on KeyboardInterrupt use --full-trace)
13 passed, 3 deselected in 153.95s (0:02:33)

exec
/bin/zsh -lc "nl -ba fitting.py | sed -n '1060,1099p;1450,1488p'; sed -n '7300,7323p' templates/index.html; rg -n 'except.*ValueError|method.run|method_impl.run' autofit/service.py autofit/api.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 exited 2 in 0ms:
  1060	    # candidate's generated sides: always start from the request's bounds.
  1061	    boxed = params.copy()
  1062	    for name, (lo, hi) in requested.items():
  1063	        boxed[name].set(min=lo, max=hi)
  1064	    generated = _finite_search_box(boxed, x, y_sub)
  1065	    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
  1066	    found.box_unverified, found.search_box = bool(generated), generated
  1067	    if not generated:
  1068	        return found
  1069	    free = found.params.copy()
  1070	    for name in generated:
  1071	        free[name].set(min=requested[name][0], max=requested[name][1])
  1072	    # Only what a local solver understands: DE options (seed, popsize, ...)
  1073	    # passed through fit_kws would make least_squares raise.
  1074	    refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
  1075	    try:
  1076	        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
  1077	    except Exception:
  1078	        log.debug("refinement outside the search box raised", exc_info=True)
  1079	        return found
  1080	    # A converged refinement IS the result: it is a least_squares fit of the
  1081	    # requested model under the requested bounds, which is what the default
  1082	    # method returns and the acceptance rule accepts. It is deliberately NOT
  1083	    # compared with the boxed search's chi-square. least_squares descends
  1084	    # from its start, so it cannot end materially above it (four review
  1085	    # rounds found no reachable case), but it does end a hair above an EXACT
  1086	    # start that sits on a requested bound (the bound transform is degenerate
  1087	    # there; the centre moves ~1e-7 eV), by an amount that depends on peak
  1088	    # width, position and counts. Every tolerance tried for that comparison
  1089	    # produced reachable false failures and no reachable protection.
  1090	    if refined.success:
  1091	        refined.box_unverified, refined.search_box = False, {}
  1092	        return refined
  1093	    return found
  1094	
  1095	
  1096	def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws):
  1097	    """A differential-evolution candidate that is never worse than the
  1098	    default method from the same start.
  1099	
  1450	        if par.expr:
  1451	            start[name].set(expr=par.expr)
  1452	    refit = fit_reduced(start)
  1453	    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
  1454	    if not refit.success:
  1455	        # F2 (2026-09-26): a refit that did not converge establishes nothing
  1456	        # either way — its chi-square is wherever the optimiser stopped (a
  1457	        # redundant anchor read "required", F 992, from a refit stopped early;
  1458	        # F 1.17 once it completed). No verdict; the caller decides.
  1459	        return {"required": None, "f": None, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
  1460	                "refit_converged": False, "reason": "refit_not_converged",
  1461	                "message": str(getattr(refit, "message", "") or "")[:200]}
  1462	    delta = chi2_without - chi2_with
  1463	    p = max(1, int(n_free_comp))
  1464	    dof = max(1, len(y_sub) - int(n_free_total))
  1465	    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
  1466	    # change relative to the data's power, and then an "exactness" cutoff on
  1467	    # the reduced fit, each masked a resolved anchor at high dynamic range —
  1468	    # the same lesson as the DE unit). Known limit, accepted: on NOISE-FREE
  1469	    # data whose full fit is numerically exact (chi2_with ~ 1e-28) F is not
  1470	    # meaningful and a truly redundant component (two identical half-amplitude
  1471	    # components) reports "required"; real data never fit to machine precision.
  1472	    if not np.isfinite(chi2_without):
  1473	        f, required = None, True                     # the rest could not even be fitted without it
  1474	    elif delta <= 0:
  1475	        f, required = 0.0, False
  1476	    elif chi2_with == 0:
  1477	        f, required = None, True
  1478	    else:
  1479	        f = (delta / p) / (chi2_with / dof)
  1480	        required = f >= SUPPORT_MIN_F
  1481	    return {"required": bool(required), "f": f, "chi2_with": float(chi2_with), "chi2_without_refit": chi2_without,
  1482	            "refit_converged": bool(refit.success)}
  1483	
  1484	
  1485	# ─────────────────────────────────────────────────────────────────────────────
  1486	# Main fitting API
  1487	# ─────────────────────────────────────────────────────────────────────────────
  1488	
  // is necessary but not sufficient: with strong overlap the OTHER components
  // could absorb the anchor if refitted. The server refits without it when
  // asked (require_component) and reports whether that made the fit
  // significantly worse. A redundant anchor is refused the same way.
  const req = json && json.required;
  if (req && req.ran === true && req.required === false) {
    notify('Auto-fit: the Graphite component is not required by the data — refitting the other components without it fits the data as well' + (req.f != null ? ' (F = ' + Number(req.f).toFixed(1) + ', threshold 10)' : '') + '. No charge correction was derived from it and the fit was not applied. The model gives the other components enough freedom to absorb the graphite line; lock or narrow them and try again.', 'red', true);
    return false;
  }
  // F2 (2026-09-26): the refit without the anchor did not converge, so the
  // server could not establish that the anchor is required. The anchor would
  // set the energy reference of the whole spectrum: refused, like a
  // redundant one (a check that did not RUN at all still never blocks).
  if (req && req.ran === true && req.refit_converged === false) {
    notify('Auto-fit: it could not be established that the data require the Graphite component — refitting the other components without it did not converge. No charge correction was derived from it and the fit was not applied. Try Run Fit, or narrow the ROI, and run Auto-Fit again.', 'red', true);
    return false;
  }
  if (!_autoFitGraphiteIsSupported(gPeak, json)) {
    notify('Auto-fit: the data do not support the Graphite component (removing it does not worsen the fit), so no charge correction was derived from it and the fit was not applied.', 'red', true);
    return false;
  }
  // 2. Validate within ±0.3 of 284.50 (the LA center bound).
  if (Math.abs(gPeak.center - 284.50) > 0.30 + 1e-6) {
    notify('Fit failed to converge or produced an unphysical graphite position.', 'red', true);
rg: autofit/service.py: No such file or directory (os error 2)
rg: autofit/api.py: No such file or directory (os error 2)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"
import numpy as np, fitting
from unittest.mock import patch
x=np.linspace(280,292,41)
y=100+1000*np.exp(-4*np.log(2)*((x-284.5)/1.)**2)+500*np.exp(-4*np.log(2)*((x-288)/1.)**2)+.5*np.sin(np.arange(41))
s=[dict(id=\"1\",shape=\"gaussian\",center=284.5,fwhm=1,amplitude=950,amplitude_min=0),dict(id=\"2\",shape=\"gaussian\",center=288,fwhm=1,amplitude=450,amplitude_min=0)]
real=fitting.Model.fit; records=[]
def stop_reduced(self,data,params,**kw):
    reduced=len(self.components)==1
    if reduced and kw.get(\"method\")==\"least_squares\": kw[\"max_nfev\"]=1
    r=real(self,data,params,**kw)
    records.append((reduced,kw.get(\"method\"),r.success,r.chisqr))
    return r
with patch.object(fitting.Model,\"fit\",stop_reduced):
    r=fitting.run_fit(x,y,s,background_method=\"linear\",n_perturb=0,require_component=\"1\",fit_kws={\"method\":\"differential_evolution\"})
print(\"REQUIRED\",r[\"success\"],r[\"required\"])
print(\"SOLVERS\",records)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 2857ms:
/Users/skyefortier/.matplotlib is not a writable directory
REQUIRED True {'ran': True, 'required': True, 'f': 1156948.2102037217, 'chi2_with': 0.035806814389341926, 'chi2_without_refit': 3550.889791458332, 'refit_converged': True}
SOLVERS [(False, 'differential_evolution', True, np.float64(0.0358068144041998)), (False, 'least_squares', True, np.float64(0.035806814389342044)), (False, 'least_squares', True, np.float64(0.035806814389341926)), (True, 'differential_evolution', True, np.float64(3550.889791458332)), (True, 'least_squares', False, np.float64(3550.889792503432)), (True, 'least_squares', False, np.float64(2982.9266494998274))]

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile; tempfile.tempdir=\"/tmp\"
import app, numpy as np
from unittest.mock import patch
x=np.arange(3.); y=np.ones(3)
with patch.object(app,\"_load_session\",return_value=(x,y)):
    with app.app.test_client() as c:
        r=c.post(\"/api/fit\",json={\"session_id\":\"memory-only\",\"background\":{\"method\":\"none\"},\"fit_method\":\"least_squares\",\"peaks\":[{\"id\":\"1\",\"shape\":\"gaussian\",\"center\":1,\"amplitude\":1,\"fwhm\":1}]})
        print(r.status_code,r.get_json())
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes
 succeeded in 1850ms:
/Users/skyefortier/.matplotlib is not a writable directory
400 None

codex
- **MAJOR — Required-refit guard accepts an unverified DE candidate.** [fitting.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py:1454) checks only `refit.success`. Differential evolution can return `success=True, box_unverified=True` when its boxed search converges but both least-squares verification attempts fail. The main-fit acceptance rule rejects that candidate; this guard computes a required verdict from it.

  **Reproduced:** two Gaussian components on 41 noisy points, open amplitude bounds, DE, `require_component="1"`. Limiting only the reduced model’s two least-squares calls to `max_nfev=1` produced two actual solver failures, yet the response reported `required=True`, `refit_converged=True`, and F ≈ **1,156,948**. Auto-Fit’s new refusal therefore does not block this anchor. Treat `box_unverified` as failed verification here and add this regression case.

- **MINOR — Non-finite detection mistakes string contents for numeric tokens.** [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417) applies its regex without tracking JSON strings.

  **Reproduced:** a body containing `{"success":true,"message":"contains NaN in label"}` with its final brace missing reports a non-finite number and suggests an undetermined model. There is no non-finite numeric token—only malformed JSON. Acceptance remains closed, but the diagnosis is wrong. Valid JSON containing the same string correctly passes.

No BLOCKER findings.

Validation: 100 JavaScript tests passed; one parity test was blocked by the sandbox’s temporary-directory restriction. Thirteen Python tests passed before I stopped the longer reproducibility run to bound review time. Additional probes verified basinhopping abort recovery, expression/bound preservation, and refusal when finite observations leave zero degrees of freedom. No files changed.

**VERDICT: NO-GO**
tokens used
82,904
- **MAJOR — Required-refit guard accepts an unverified DE candidate.** [fitting.py:1454](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/fitting.py:1454) checks only `refit.success`. Differential evolution can return `success=True, box_unverified=True` when its boxed search converges but both least-squares verification attempts fail. The main-fit acceptance rule rejects that candidate; this guard computes a required verdict from it.

  **Reproduced:** two Gaussian components on 41 noisy points, open amplitude bounds, DE, `require_component="1"`. Limiting only the reduced model’s two least-squares calls to `max_nfev=1` produced two actual solver failures, yet the response reported `required=True`, `refit_converged=True`, and F ≈ **1,156,948**. Auto-Fit’s new refusal therefore does not block this anchor. Treat `box_unverified` as failed verification here and add this regression case.

- **MINOR — Non-finite detection mistakes string contents for numeric tokens.** [templates/index.html:7417](/Users/skyefortier/xps-app/.claude/worktrees/fix-acceptance-holes/templates/index.html:7417) applies its regex without tracking JSON strings.

  **Reproduced:** a body containing `{"success":true,"message":"contains NaN in label"}` with its final brace missing reports a non-finite number and suggests an undetermined model. There is no non-finite numeric token—only malformed JSON. Acceptance remains closed, but the diagnosis is wrong. Valid JSON containing the same string correctly passes.

No BLOCKER findings.

Validation: 100 JavaScript tests passed; one parity test was blocked by the sandbox’s temporary-directory restriction. Thirteen Python tests passed before I stopped the longer reproducibility run to bound review time. Additional probes verified basinhopping abort recovery, expression/bound preservation, and refusal when finite observations leave zero degrees of freedom. No files changed.

**VERDICT: NO-GO**
