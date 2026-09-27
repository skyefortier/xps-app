OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0e227-4d3f-7da0-af2f-7b70183dcb30
--------
user
Re-review unit 2 (long fits via start-then-poll), round 2: branch fix-fit-start-poll (stacked on fix-acceptance-holes, F2). The round-1 fixes are the latest commit on this branch that is not a merge of fix-acceptance-holes; review git diff fix-acceptance-holes..HEAD for the whole unit. Round-1 verdicts: docs/autofit/codex/fit_start_poll_verdict_run{A,B}.md; the round-1 prompt (brief, design, sites, acceptance): docs/autofit/codex/fit_start_poll_review_prompt.txt. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

ROUND-1 FINDINGS AND FIXES (plan section 6, verbatim):

**Round 1 — NO-GO ×2** (`fit_start_poll_verdict_run{A,B}.md`; the same four
findings in both):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: a re-run did not supersede — Ctrl/Cmd+F calls `runFit` past the disabled button; two jobs for one tab, the older could finish first and get the newer discarded as "model edited" | `_fitJobByOwner` (WeakMap keyed by the tab record): a new start for the same tab cancels the previous job on the server; the superseded loop returns `{ _abandoned: 'superseded' }` and its caller does NOTHING (the new fit owns spinner and result; Auto-Fit does not roll back, which would overwrite the new fit's model). Run Fit and Auto-Fit both pass their tab as `owner`. |
| 2 | MAJOR: unbounded concurrency — a thread per start, where four sync workers used to bound concurrent fits at four | each worker process runs at most `FIT_JOB_MAX_RUNNING` = 1 fit (a semaphore); the rest wait `queued` (heartbeating, cancellable, a queued job cancelled or abandoned never runs); at most `FIT_JOB_MAX_ADMITTED` = 6 running + queued per process, beyond that `/api/fit/start` answers 503 "The server is busy with other fits" at once (the page shows it as a failed fit). Production: ≤ 4 concurrent fits, as before. |
| 3 | MINOR: a cancellation observed mid-fit could surface as the solver's own error (AttributeError from Levenberg-Marquardt, RuntimeError from Nelder-Mead / DE) — an abandoned job became `error` 500 / 422 | `run_fit(cancel=)` turns any exception raised after cancellation was observed into `FitCancelled`; unrelated errors propagate unchanged |
| 4 | MINOR: `public_fit_poll_check.py` could poll a dead worker's record forever | a heartbeat older than 30 s is FAIL "lost"; a 20-minute deadline per target (the job is cancelled) |



TRY TO BREAK
a. Supersede: the WeakMap keyed by the tab record — is the SAME object passed by Run Fit, "Use this solution" (runFit({startPeaks})) and Auto-Fit; a superseded Auto-Fit that had already built its model and provisional shift (is leaving it correct?); a superseded Run Fit whose successor then fails; the spinner (who hides it); two tabs fitting at once (not superseded); the pagehide beacon; the ownership-reason order (superseded checked before tab/model).
b. Concurrency: the per-process semaphore + admission counter — can the counter leak (an exception between admit and the worker's finally; a worker thread that never starts), can a queued job starve, is the 'queued' status handled by every page path (heartbeat, abandonment, the acceptance script), does a 503 at start reach the page as a failed fit with the message (not a transport failure / local fallback), do polls stay fast while a fit runs in the same process (GIL); is 1 running per process too low (four students in parallel = four fits, as before; a fifth waits)?
c. Cancellation normalisation: FitCancelled only when cancellation was observed; an unrelated exception during a cancel-enabled fit still reports its own error; the thread-local cleared on every path.
d. Anything round 1 verified that these changes touched; the merged F2 changes (only its documents and one scanner line).
e. Tests: real, non-vacuous.

Finish with VERDICT: GO or VERDICT: NO-GO.
codex
I’ll read the review brief, prior verdicts, and full unit diff, then probe the round-1 fixes for concrete failure cases. I’ll keep this read-only and finish with a verdict.
exec
/bin/zsh -lc "pwd; rg --files -g AGENTS.md -g '*fit_start_poll*' -g '*public_fit_poll*' -g '*plan*' docs . 2>/dev/null" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle-plan.md
./scripts/public_fit_poll_check.py
./docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle-plan.md
./tests/test_fit_start_poll.py
./tests/js/fit_start_poll.test.js
docs/autofit/codex/fit_start_poll_verdict_runA.md
docs/autofit/codex/fit_start_poll_verdict_runB.md
docs/autofit/codex/fit_start_poll_review_prompt.txt
docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
docs/autofit/codex/fit_start_poll_recheck_prompt.txt
docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
./docs/autofit/codex/fit_start_poll_verdict_runA.md
./docs/autofit/codex/fit_start_poll_verdict_runB.md
./docs/autofit/codex/fit_start_poll_review_prompt.txt
./docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
./docs/autofit/codex/fit_start_poll_recheck_prompt.txt
./docs/autofit/codex/fit_start_poll_r2_verdict_runB.md

exec
/bin/zsh -lc 'git status --short; git diff --stat fix-acceptance-holes..HEAD; git log -8 --oneline' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YnloWGy7' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-wMd0w6dI' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sUc95WRe' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-o9jMzk1h' (errno=Operation not permitted)
 CLAUDE.md                                          |   28 +
 app.py                                             |  422 +-
 .../codex/fit_start_poll_recheck_prompt.txt        |   24 +
 .../autofit/codex/fit_start_poll_review_prompt.txt |  116 +
 docs/autofit/codex/fit_start_poll_verdict_runA.md  | 5464 ++++++++++++++++++
 docs/autofit/codex/fit_start_poll_verdict_runB.md  | 5967 ++++++++++++++++++++
 .../plans/2026-09-27-long-fits-start-poll.md       |  182 +
 fitting.py                                         |   89 +-
 scripts/public_fit_poll_check.py                   |   97 +
 templates/index.html                               |  203 +-
 tests/js/fit_acceptance.test.js                    |   34 +-
 tests/js/fit_start_poll.test.js                    |  176 +
 tests/js/per_tab_state.test.js                     |    1 +
 tests/js/stale_statistics.test.js                  |   31 +-
 tests/test_browser_bg_window_request.py            |    2 +-
 tests/test_browser_endpoint_avg_default.py         |    2 +-
 tests/test_fit_start_poll.py                       |  216 +
 17 files changed, 12915 insertions(+), 139 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4PFQ4ZFS' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-D2EGopwM' (errno=Operation not permitted)
5e26c36 Merge branch 'fix-acceptance-holes' into fix-fit-start-poll
0e62a7f fix(unit 2): Codex round 1 (NO-GO x2) - supersede per tab, bounded concurrency, cancellation normalised, checker deadline
3d38d73 docs(F2): Codex round 4 GO x2 - verdicts archived, release note; ready for deploy
63f7e6d fix(F2): Codex round 3 (GO x2) - a minus sign before Infinity counts only after a boundary
07e0839 Merge branch 'fix-acceptance-holes' into fix-fit-start-poll
c00c893 feat(unit 2): long fits via start-then-poll - no request of Run Fit or Auto-Fit meets the public ~100 s ceiling
0224141 fix(F2): Codex round 2 (A GO, B NO-GO) - linear token scan for the unreadable-reply message
a5a14a0 fix(F2): Codex round 1 (A GO, B NO-GO) - unverified DE refit gives no required verdict; NaN token test ignores strings

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- app.py fitting.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-bgSKXYOs' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Ocz0sWU6' (errno=Operation not permitted)
diff --git a/app.py b/app.py
index f689d5a..2dd37a5 100644
--- a/app.py
+++ b/app.py
@@ -58,6 +58,113 @@ MAX_N_PERTURB = 100
 # — no background thread or scheduler.
 SESSION_TTL_DAYS = 7
 
+# ─────────────────────────────────────────────────────────────────────────────
+# /api/fit request handling, shared by /api/fit and /api/fit/start (unit 2)
+# ─────────────────────────────────────────────────────────────────────────────
+
+def _prepare_fit_request(app, body):
+    """/api/fit's request validation, shared VERBATIM with /api/fit/start
+    (unit 2, 2026-09-27): every 400 / 404 is immediate and word-for-word the
+    same on both routes. Returns ``(kwargs_for_run_fit, None)`` or
+    ``(None, error_response)``."""
+    session_id = body.get("session_id", "")
+    _validate_session_id(session_id)
+
+    try:
+        energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
+    except KeyError:
+        return None, _err(f"Session '{session_id}' not found", 404)
+
+    # Background config
+    bg_cfg = body.get("background", {})
+    bg_method = bg_cfg.get("method", "shirley")
+    bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
+    bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
+    # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
+    try:
+        endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
+    except (TypeError, ValueError):
+        return None, _err("endpoint_avg must be an integer")
+    manual_bg = bg_cfg.get("manual_bg")
+
+    # Peak specs
+    peak_specs = body.get("peaks", [])
+    if not peak_specs:
+        return None, _err("'peaks' list is empty – provide at least one peak")
+
+    # Validate peak ids are unique
+    ids = [p.get("id") for p in peak_specs]
+    if len(ids) != len(set(ids)):
+        return None, _err("Duplicate peak ids found – each peak must have a unique 'id'")
+
+    _ALLOWED_METHODS = {
+        "leastsq", "least_squares", "nelder",
+        "differential_evolution", "basinhopping",
+    }
+    fit_method = body.get("fit_method", "leastsq")
+    if fit_method not in _ALLOWED_METHODS:
+        return None, _err(f"Unknown fit_method '{fit_method}'")
+
+    # Bounded, type-checked n_perturb (audit F7; also covers the F9
+    # ValueError-on-bad-input case for this field). Reject out-of-range or
+    # non-integer values with a clean 400 instead of a 500 or a worker hang.
+    try:
+        n_perturb = int(body.get("n_perturb", 5))
+    except (TypeError, ValueError):
+        return None, _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
+    if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
+        return None, _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
+
+    # Scattered-starts check (optional; the page sends 3). Same clean-400
+    # treatment as n_perturb; run_fit validates again for other callers.
+    n_starts = body.get("n_starts", 0)
+    if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
+        return None, _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
+    # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
+    require_component = body.get("require_component")
+    if require_component is not None and not isinstance(require_component, (str, int)):
+        return None, _err("require_component must be a peak id")
+    return dict(
+        energy=energy,
+        counts=counts,
+        peak_specs=peak_specs,
+        background_method=bg_method,
+        bg_start_idx=bg_start,
+        bg_end_idx=bg_end,
+        charge_shift_ev=0.0,
+        fit_kws={"method": fit_method},
+        manual_bg=manual_bg,
+        n_perturb=n_perturb,
+        endpoint_avg=endpoint_avg,
+        n_starts=n_starts,
+        require_component=require_component,
+    ), None
+
+
+def _run_fit_outcome(app, fit_args, cancel=None):
+    """Run the fit; return ``(status_code, body)`` exactly as /api/fit has
+    always answered (a ValueError is our own validation, 400; a RuntimeError
+    a solver-internal failure, 422 without library internals; anything else
+    500). A cancelled job returns ``(None, None)``."""
+    try:
+        result = fitting.run_fit(**fit_args, cancel=cancel)
+    except fitting.FitCancelled:
+        return None, None
+    except ValueError as exc:
+        # Our own validation: unknown shape/method, self/circular constraint,
+        # "Master peak not found", bad numeric field, etc. (audit F10/F11).
+        return 400, {"error": str(exc)}
+    except RuntimeError:
+        # Solver-internal failure (e.g. lmfit non-convergence). Log the
+        # detail; return a generic 422 that leaks no library internals.
+        app.logger.exception("Fit failed")
+        return 422, {"error": "Fit failed — see server log for details."}
+    except Exception:
+        app.logger.exception("Unexpected fitting error")
+        return 500, {"error": "Internal fitting error — see server log."}
+    return 200, result
+
+
 # ─────────────────────────────────────────────────────────────────────────────
 # Application factory
 # ─────────────────────────────────────────────────────────────────────────────
@@ -443,6 +550,172 @@ def _sweep_expired_jobs(upload_folder: str) -> None:
             pass
 
 
+# ── Fit jobs (unit 2, 2026-09-27) ────────────────────────────────────────────
+# Records are the Find Peaks job files (<job>.job.json, the same TTL sweep);
+# two small markers beside each: <job>.cancel (written by /api/fit/cancel,
+# any worker) and <job>.polled (touched by every poll). The fit thread's
+# cancel condition: the cancel marker exists, OR no poll for
+# FIT_JOB_ABANDON_SEC (a closed tab, a sleeping laptop; 180 s, above the ~1 min timer throttling browsers apply to hidden tabs).
+FIT_JOB_ABANDON_SEC = 180   # > Chrome's 1-minute timer throttling in a hidden tab: a student who switches browser tabs keeps the fit
+FIT_JOB_HEARTBEAT_SEC = 2.0
+# Concurrency (unit 2, Codex round 1). Before start-then-poll, gunicorn's four
+# SYNC workers bounded concurrent fits at four; a fit thread per start would
+# not. Each worker process runs at most FIT_JOB_MAX_RUNNING fits at once (the
+# rest wait "queued", heartbeating, cancellable) and admits at most
+# FIT_JOB_MAX_ADMITTED running + queued jobs; beyond that /api/fit/start
+# answers 503 "busy" immediately. With production's 4 workers: at most 4
+# concurrent fits, as before.
+FIT_JOB_MAX_RUNNING = 1
+FIT_JOB_MAX_ADMITTED = 6
+_FIT_JOB_RUN_SLOTS = threading.BoundedSemaphore(FIT_JOB_MAX_RUNNING)
+_FIT_JOB_ADMITTED = [0]
+_FIT_JOB_ADMIT_LOCK = threading.Lock()
+
+
+def _fit_job_admit() -> bool:
+    with _FIT_JOB_ADMIT_LOCK:
+        if _FIT_JOB_ADMITTED[0] >= FIT_JOB_MAX_ADMITTED:
+            return False
+        _FIT_JOB_ADMITTED[0] += 1
+        return True
+
+
+def _fit_job_release() -> None:
+    with _FIT_JOB_ADMIT_LOCK:
+        _FIT_JOB_ADMITTED[0] = max(0, _FIT_JOB_ADMITTED[0] - 1)
+
+
+def _fit_job_marker(job_id: str, upload_folder: str, kind: str) -> Path:
+    return Path(upload_folder) / f"{job_id}.{kind}"
+
+
+def _fit_job_write(job_id: str, upload_folder: str, data: dict) -> None:
+    """Atomic like _write_job_progress, but WITHOUT sanitising: a result's
+    NaN / Infinity reach the page exactly as /api/fit sends them (the page's
+    _readFitReply refuses them as a failed fit — unit F2)."""
+    path = _job_progress_path(job_id, upload_folder)
+    tmp = path.with_suffix(f".{threading.get_ident()}.tmp")
+    try:
+        tmp.write_text(json.dumps(data, allow_nan=True))
+        os.replace(tmp, path)
+    except OSError:
+        logging.getLogger(__name__).exception("failed to write fit job %s", job_id)
+
+
+def _fit_job_read(job_id: str, upload_folder: str):
+    path = _job_progress_path(job_id, upload_folder)
+    if not path.exists():
+        return None
+    try:
+        _fit_job_marker(job_id, upload_folder, "polled").touch()
+    except OSError:
+        pass
+    try:
+        data = json.loads(path.read_text())
+    except (OSError, ValueError):
+        data = {"status": "running", "elapsed_sec": 0.0}      # a read racing the first write
+    hb = data.get("heartbeat")
+    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
+    return data
+
+
+def _sweep_fit_job_markers(upload_folder: str) -> None:
+    """Markers left by a job whose worker died (they are removed when a job
+    finishes): same TTL as the job records, never raises."""
+    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
+    for pattern in ("*.cancel", "*.polled"):
+        try:
+            for m in Path(upload_folder).glob(pattern):
+                try:
+                    if m.stat().st_mtime < cutoff:
+                        m.unlink(missing_ok=True)
+                except OSError:
+                    pass
+        except OSError:
+            pass
+
+
+def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
+    try:
+        _fit_job_marker(job_id, upload_folder, "cancel").touch()
+    except OSError:
+        pass
+
+
+def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None:
+    """Start the fit thread and its heartbeat thread. ``run(fit_args, cancel)``
+    returns ``(status, body)``; ``(None, None)`` means cancelled."""
+    started = time.time()
+    lock = threading.Lock()
+    rec = {"status": "queued", "elapsed_sec": 0.0, "heartbeat": started}
+    _fit_job_write(job_id, upload_folder, rec)
+    _fit_job_marker(job_id, upload_folder, "polled").touch()
+    cancel_path = _fit_job_marker(job_id, upload_folder, "cancel")
+    polled_path = _fit_job_marker(job_id, upload_folder, "polled")
+    finished = threading.Event()
+
+    def cancelled() -> bool:
+        if cancel_path.exists():
+            return True
+        try:
+            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
+        except OSError:
+            return False
+
+    def heartbeat() -> None:
+        while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
+            with lock:
+                if rec["status"] not in ("running", "queued"):
+                    return
+                rec["heartbeat"] = time.time()
+                rec["elapsed_sec"] = round(time.time() - started, 1)
+                _fit_job_write(job_id, upload_folder, rec)
+
+    def worker() -> None:
+        try:
+            # queued until a run slot is free; a job cancelled or abandoned
+            # while queued never runs
+            got = False
+            while not got:
+                if cancelled():
+                    status, body = None, None
+                    break
+                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
+            if got:
+                try:
+                    with lock:
+                        rec["status"] = "running"
+                        rec["heartbeat"] = time.time()
+                        _fit_job_write(job_id, upload_folder, rec)   # visible at once, not at the next heartbeat
+                    status, body = run(fit_args, cancelled)
+                finally:
+                    _FIT_JOB_RUN_SLOTS.release()
+        except Exception as exc:                       # the record must always leave "running"
+            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
+            status, body = 500, {"error": "Internal fitting error — see server log."}
+        finally:
+            _fit_job_release()
+        with lock:
+            rec["elapsed_sec"] = round(time.time() - started, 1)
+            rec["heartbeat"] = time.time()
+            if status is None or cancel_path.exists():
+                rec.update(status="cancelled")
+            elif status == 200:
+                rec.update(status="done", result=body)
+            else:
+                rec.update(status="error", error=body.get("error"), http_status=status)
+            finished.set()
+            _fit_job_write(job_id, upload_folder, rec)
+        for kind in ("cancel", "polled"):
+            try:
+                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
+            except OSError:
+                pass
+
+    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
+    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
+
+
 def _require_json(f):
     """Decorator: return 400 if request body is not valid JSON."""
     @wraps(f)
@@ -779,94 +1052,13 @@ def _register_routes(app: Flask) -> None:
         }
         """
         body = request.get_json()
-        session_id = body.get("session_id", "")
-        _validate_session_id(session_id)
-
-        try:
-            energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
-        except KeyError:
-            return _err(f"Session '{session_id}' not found", 404)
-
-        # Background config
-        bg_cfg = body.get("background", {})
-        bg_method = bg_cfg.get("method", "shirley")
-        bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
-        bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
-        # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
-        try:
-            endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
-        except (TypeError, ValueError):
-            return _err("endpoint_avg must be an integer")
-        manual_bg = bg_cfg.get("manual_bg")
-
-        # Peak specs
-        peak_specs = body.get("peaks", [])
-        if not peak_specs:
-            return _err("'peaks' list is empty – provide at least one peak")
-
-        # Validate peak ids are unique
-        ids = [p.get("id") for p in peak_specs]
-        if len(ids) != len(set(ids)):
-            return _err("Duplicate peak ids found – each peak must have a unique 'id'")
-
-        _ALLOWED_METHODS = {
-            "leastsq", "least_squares", "nelder",
-            "differential_evolution", "basinhopping",
-        }
-        fit_method = body.get("fit_method", "leastsq")
-        if fit_method not in _ALLOWED_METHODS:
-            return _err(f"Unknown fit_method '{fit_method}'")
-
-        # Bounded, type-checked n_perturb (audit F7; also covers the F9
-        # ValueError-on-bad-input case for this field). Reject out-of-range or
-        # non-integer values with a clean 400 instead of a 500 or a worker hang.
-        try:
-            n_perturb = int(body.get("n_perturb", 5))
-        except (TypeError, ValueError):
-            return _err(f"n_perturb must be an integer between 0 and {MAX_N_PERTURB}")
-        if n_perturb < 0 or n_perturb > MAX_N_PERTURB:
-            return _err(f"n_perturb must be between 0 and {MAX_N_PERTURB}")
-
-        # Scattered-starts check (optional; the page sends 3). Same clean-400
-        # treatment as n_perturb; run_fit validates again for other callers.
-        n_starts = body.get("n_starts", 0)
-        if isinstance(n_starts, bool) or not isinstance(n_starts, int) or not 0 <= n_starts <= fitting.MAX_N_STARTS:
-            return _err(f"n_starts must be an integer between 0 and {fitting.MAX_N_STARTS}")
-        # "Is this component required?" (one extra fit; Auto-Fit asks for its anchor)
-        require_component = body.get("require_component")
-        if require_component is not None and not isinstance(require_component, (str, int)):
-            return _err("require_component must be a peak id")
-
-        try:
-            result = fitting.run_fit(
-                energy=energy,
-                counts=counts,
-                peak_specs=peak_specs,
-                background_method=bg_method,
-                bg_start_idx=bg_start,
-                bg_end_idx=bg_end,
-                charge_shift_ev=0.0,
-                fit_kws={"method": fit_method},
-                manual_bg=manual_bg,
-                n_perturb=n_perturb,
-                endpoint_avg=endpoint_avg,
-                n_starts=n_starts,
-                require_component=require_component,
-            )
-        except ValueError as exc:
-            # Our own validation: unknown shape/method, self/circular constraint,
-            # "Master peak not found", bad numeric field, etc. (audit F10/F11).
-            return _err(str(exc))
-        except RuntimeError:
-            # Solver-internal failure (e.g. lmfit non-convergence). Log the
-            # detail; return a generic 422 that leaks no library internals.
-            app.logger.exception("Fit failed")
-            return _err("Fit failed — see server log for details.", 422)
-        except Exception:
-            app.logger.exception("Unexpected fitting error")
-            return _err("Internal fitting error — see server log.", 500)
-
-        return jsonify(result)
+        fit_args, error = _prepare_fit_request(app, body)
+        if error is not None:
+            return error
+        status, out = _run_fit_outcome(app, fit_args)
+        if status != 200:
+            return _err(out["error"], status)
+        return jsonify(out)
 
     # ── Autofit analyze (opt-in Find Peaks; STRICTLY ADDITIVE — the manual
     #    /api/fit path above is untouched) ──────────────────────────────────
@@ -1060,6 +1252,60 @@ def _register_routes(app: Flask) -> None:
                     "message": "starting analysis…"}
         return jsonify(data)
 
+    # ── Long fits via start-then-poll (unit 2, 2026-09-27) ───────────────────
+    # The public URL ends a proxied request at ~100 s (Cloudflare 524; 88 s
+    # passed, 125 s failed); basinhopping on the large C 1s models takes 3–4
+    # minutes. The fit runs in a background thread on Find Peaks' job
+    # infrastructure (an atomic JSON record under the upload folder, readable
+    # by whichever gunicorn worker serves a poll); every HTTP request is short.
+    # The record: {status: queued|running|done|error|cancelled, elapsed_sec,
+    # heartbeat (epoch s, rewritten every 2 s while the fit thread lives),
+    # result (done: EXACTLY the /api/fit body), error + http_status (error:
+    # exactly what /api/fit would have answered)}.
+
+    @app.post("/api/fit/start")
+    @_require_json
+    def fit_start():
+        body = request.get_json(silent=True)
+        if not isinstance(body, dict):
+            return _err("request body must be a JSON object")
+        fit_args, error = _prepare_fit_request(app, body)
+        if error is not None:
+            return error
+        upload_folder = app.config["UPLOAD_FOLDER"]
+        if not _fit_job_admit():
+            return _err("The server is busy with other fits. Try again in a moment.", 503)
+        job_id = str(uuid.uuid4())
+        try:
+            _sweep_expired_jobs(upload_folder)
+            _sweep_fit_job_markers(upload_folder)
+            _fit_job_start(job_id, upload_folder, fit_args,
+                           lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
+        except Exception:
+            _fit_job_release()          # the job never started: its admission is returned
+            raise
+        return jsonify({"job_id": job_id}), 202
+
+    @app.get("/api/fit/progress/<job_id>")
+    def fit_progress(job_id):
+        try:
+            uuid.UUID(job_id)
+        except ValueError:
+            return _err("Invalid job_id format (expected UUID)", 400)
+        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
+        if data is None:
+            return _err(f"Job '{job_id}' not found", 404)
+        return app.response_class(json.dumps(data, allow_nan=True), mimetype="application/json")
+
+    @app.post("/api/fit/cancel/<job_id>")
+    def fit_cancel(job_id):
+        try:
+            uuid.UUID(job_id)
+        except ValueError:
+            return _err("Invalid job_id format (expected UUID)", 400)
+        _fit_job_cancel(job_id, app.config["UPLOAD_FOLDER"])
+        return jsonify({"cancelled": True})
+
     # ── Health check ──────────────────────────────────────────────────────────
 
     @app.get("/api/health")
diff --git a/fitting.py b/fitting.py
index 63785a8..6b8f511 100644
--- a/fitting.py
+++ b/fitting.py
@@ -26,6 +26,8 @@ import hashlib
 import json
 import logging
 import re
+import threading
+import time
 import warnings
 from typing import Any
 
@@ -979,6 +981,44 @@ def _make_peak_params(
     return p
 
 
+# ── Cancellation (unit 2, 2026-09-27: long fits via start-then-poll) ────────
+# A fit started through /api/fit/start runs in a background thread; the page
+# can abandon it (a re-run, a tab switch, an edited model, a closed tab). The
+# job passes ``run_fit(..., cancel=callable)``; inside that thread every
+# model.fit below receives an ``iter_cb`` that returns True — lmfit's abort —
+# once ``cancel()`` is true (checked at most every 0.25 s). Thread-local, so a
+# concurrent fit in another thread of the same worker is untouched; and
+# WITHOUT a cancel callable no ``iter_cb`` argument is passed at all, so every
+# synchronous call is made exactly as before. Never part of fit_kws: the
+# request seed cannot see it.
+_CANCEL = threading.local()
+
+
+class FitCancelled(RuntimeError):
+    """The job was cancelled while run_fit ran."""
+
+
+def _cancel_kw() -> dict:
+    fn = getattr(_CANCEL, "fn", None)
+    if fn is None:
+        return {}
+    state = {"t": 0.0, "hit": False}
+
+    def iter_cb(params, it, resid, *args, **kws):
+        if state["hit"]:
+            return True
+        now = time.monotonic()
+        if now - state["t"] >= 0.25:
+            state["t"] = now
+            if fn():
+                state["hit"] = True
+                _CANCEL.hit = True
+                return True
+        return None
+
+    return {"iter_cb": iter_cb}
+
+
 def _finite_search_box(params: Parameters, x: np.ndarray,
                        y_sub: np.ndarray) -> dict[str, dict[str, float]]:
     """Give every freely varying parameter a finite box, in place.
@@ -1062,7 +1102,7 @@ def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
     for name, (lo, hi) in requested.items():
         boxed[name].set(min=lo, max=hi)
     generated = _finite_search_box(boxed, x, y_sub)
-    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
+    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws, **_cancel_kw())
     found.box_unverified, found.search_box = bool(generated), generated
     if not generated:
         return found
@@ -1073,7 +1113,7 @@ def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
     # passed through fit_kws would make least_squares raise.
     refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
     try:
-        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
+        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws, **_cancel_kw())
     except Exception:
         log.debug("refinement outside the search box raised", exc_info=True)
         return found
@@ -1111,7 +1151,7 @@ def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws)
         start[name].set(min=lo, max=hi)
     try:
         local = model.fit(y_sub, start, x=x, weights=weights,
-                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"))
+                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"), **_cancel_kw())
     except Exception:
         log.debug("local candidate from the start raised", exc_info=True)
         return searched
@@ -1147,11 +1187,11 @@ def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
     start = params.copy()
     for name, (lo, hi) in requested.items():
         start[name].set(min=lo, max=hi)
-    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws)
+    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws, **_cancel_kw())
     candidate = None
     try:   # from wherever the search stopped, even an evaluation-budget abort (as DE)
         refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
-                            method="least_squares", nan_policy=nan_policy)
+                            method="least_squares", nan_policy=nan_policy, **_cancel_kw())
         if refined.success:
             candidate = refined
     except Exception:
@@ -1163,7 +1203,8 @@ def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
                          "so the result is not a verified fit")
         candidate = found
     try:
-        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy)
+        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy,
+                          **_cancel_kw())
     except Exception:
         log.debug("local candidate from the start raised", exc_info=True)
         return candidate
@@ -1489,7 +1530,7 @@ def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weigh
 # Main fitting API
 # ─────────────────────────────────────────────────────────────────────────────
 
-def run_fit(
+def _run_fit_impl(
     energy: np.ndarray,
     counts: np.ndarray,
     peak_specs: list[dict[str, Any]],
@@ -1750,7 +1791,7 @@ def run_fit(
         if kws.get("method") == "basinhopping":
             bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
             return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
-        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))
+        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())
 
     def fit_once(params):
         return fit_model(composite_model, params)
@@ -2048,3 +2089,35 @@ def compute_background_only(
         "background": bg.tolist(),
         "net_counts": (y - bg).tolist(),
     }
+
+
+def run_fit(*args, cancel=None, **kwargs):
+    """Fit peaks — see ``_run_fit_impl`` for every argument and the result.
+
+    ``cancel`` (optional, unit 2): a callable polled during the fit; once it
+    returns true every remaining minimisation aborts and ``FitCancelled`` is
+    raised instead of a result. Without it this is exactly the synchronous fit
+    it always was (no ``iter_cb`` reaches any minimiser)."""
+    if cancel is None:
+        return _run_fit_impl(*args, **kwargs)
+    _CANCEL.fn, _CANCEL.hit = cancel, False
+    try:
+        result = _run_fit_impl(*args, **kwargs)
+    except Exception as exc:
+        # An aborted minimisation can surface as the solver's own error (an
+        # AttributeError from Levenberg-Marquardt, a RuntimeError from
+        # Nelder-Mead or DE): once cancellation was observed it is a
+        # cancellation, never a failed fit (unit 2, Codex round 1).
+        if getattr(_CANCEL, "hit", False):
+            raise FitCancelled("the fit was cancelled") from exc
+        raise
+    finally:
+        hit = getattr(_CANCEL, "hit", False)
+        _CANCEL.fn, _CANCEL.hit = None, False
+    if hit:
+        raise FitCancelled("the fit was cancelled")
+    return result
+
+
+run_fit.__wrapped__ = _run_fit_impl
+

exec
/bin/zsh -lc 'git diff fix-acceptance-holes..HEAD -- templates/index.html scripts/public_fit_poll_check.py tests/test_fit_start_poll.py tests/js/fit_start_poll.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PA0HZNyX' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-EviMnxQv' (errno=Operation not permitted)
diff --git a/scripts/public_fit_poll_check.py b/scripts/public_fit_poll_check.py
new file mode 100644
index 0000000..49205c6
--- /dev/null
+++ b/scripts/public_fit_poll_check.py
@@ -0,0 +1,97 @@
+#!/usr/bin/env python3
+"""Post-deploy check for unit 2 (long fits via start-then-poll), THROUGH THE
+PUBLIC URL — the path a student's browser takes, where Cloudflare ends a
+single request at ~100 s (HTTP 524).
+
+It does what the page does for Run Fit: upload, POST /api/fit/start, poll
+GET /api/fit/progress every 0.5 s until the job leaves "running"; it records
+the duration of EVERY request. PASS = the job finishes "done" with
+success true, and no request took longer than MAX_REQUEST_S.
+
+Usage:
+  python scripts/public_fit_poll_check.py targets.json [BASE_URL] [target_id ...]
+
+targets.json: the optimizer-disagreement target file (branch
+investigate-optimizer-disagreement, docs/findings/optimizer-disagreement/
+targets.json). Default targets: the five largest committed C 1s models,
+the ones that took 183-256 s even without restarts.
+"""
+import json
+import sys
+import time
+import urllib.error
+import urllib.request
+import uuid
+
+MAX_REQUEST_S = 10.0
+HEARTBEAT_LOST_S = 30.0      # as the page: a record whose heartbeat stopped is a lost fit
+DEADLINE_S = 20 * 60         # per target: never poll forever
+DEFAULT_TARGETS = ["edf39ecb66ce", "d2bd62d2f976", "496c4edd97af", "0a5f464daf3d", "8b4c2f656a80"]
+
+
+def _req(url, data=None, headers=None, method=None, timeout=60):
+    t0 = time.time()
+    req = urllib.request.Request(url, data=data, headers={"User-Agent": "xps-poll-check", **(headers or {})}, method=method)
+    try:
+        with urllib.request.urlopen(req, timeout=timeout) as r:
+            body, status = r.read(), r.status
+    except urllib.error.HTTPError as e:
+        body, status = e.read(), e.code
+    return status, body, time.time() - t0
+
+
+def run(base, t):
+    durations = []
+    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
+    bnd = uuid.uuid4().hex
+    form = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.csv\"\r\n"
+            f"Content-Type: text/csv\r\n\r\n").encode() + csv + f"\r\n--{bnd}--\r\n".encode()
+    st, body, d = _req(base + "/api/upload", form, {"Content-Type": f"multipart/form-data; boundary={bnd}"})
+    durations.append(("upload", st, d))
+    sid = json.loads(body)["session_id"]
+    bg = t["background"]
+    payload = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
+               "peaks": t["specs"], "fit_method": "basinhopping", "n_perturb": 3, "n_starts": 3}
+    st, body, d = _req(base + "/api/fit/start", json.dumps(payload).encode(), {"Content-Type": "application/json"})
+    durations.append(("start", st, d))
+    if st != 202:
+        return {"id": t["id"], "verdict": "FAIL", "why": f"start returned {st}: {body[:200]!r}", "durations": durations}
+    job = json.loads(body)["job_id"]
+    t0 = time.time()
+    while True:
+        time.sleep(0.5)
+        st, body, d = _req(base + f"/api/fit/progress/{job}")
+        durations.append(("poll", st, d))
+        rec = json.loads(body) if st == 200 else {"status": f"http {st}"}
+        if rec.get("status") not in ("running", "queued"):
+            break
+        hb = rec.get("heartbeat_age_sec")
+        if isinstance(hb, (int, float)) and hb > HEARTBEAT_LOST_S:
+            rec = {"status": "lost", "error": f"heartbeat stopped {hb:.0f} s ago (worker restarted?)"}
+            break
+        if time.time() - t0 > DEADLINE_S:
+            _req(base + f"/api/fit/cancel/{job}", b"", method="POST")
+            rec = {"status": "deadline", "error": f"no result after {DEADLINE_S} s"}
+            break
+    longest = max(x[2] for x in durations)
+    res = rec.get("result") or {}
+    ok = rec.get("status") == "done" and res.get("success") is True and longest <= MAX_REQUEST_S
+    return {"id": t["id"], "verdict": "PASS" if ok else "FAIL", "status": rec.get("status"),
+            "success": res.get("success"), "chi2r": (res.get("statistics") or {}).get("reduced_chi_square"),
+            "fit_wall_s": round(time.time() - t0, 1), "n_requests": len(durations),
+            "longest_request_s": round(longest, 2), "error": rec.get("error")}
+
+
+def main():
+    targets = json.load(open(sys.argv[1]))
+    base = sys.argv[2] if len(sys.argv) > 2 else "https://xps.fortierlab.org"
+    ids = sys.argv[3:] or DEFAULT_TARGETS
+    by_id = {t["id"]: t for t in targets}
+    results = [run(base, by_id[i]) for i in ids]
+    for r in results:
+        print(json.dumps(r))
+    print("OVERALL:", "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/templates/index.html b/templates/index.html
index bb740ac..b81fa84 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7445,6 +7445,130 @@ async function _readFitReply(resp) {
   }
 }
 
+// ── Long fits via start-then-poll (unit 2, 2026-09-27) ──────────────────────
+// The public URL ends a proxied request at ~100 s (Cloudflare 524); a
+// basinhopping fit of a large C 1s model takes 3–4 minutes. So the fit is
+// STARTED (/api/fit/start: the same validation as /api/fit, an immediate 400
+// for a bad request, else 202 + a job id) and POLLED (/api/fit/progress, a
+// short request every FIT_POLL_MS); no request of this path lasts longer than
+// a poll. The final record's `result` is exactly the body /api/fit returns,
+// read with F2's rules (_readFitReply: a body read but not JSON — a NaN — is
+// the server's failed fit). The caller's ownership rules run INSIDE the loop:
+// `guard.abandoned()` returning a reason ('tab' | 'model') cancels the job on
+// the server and returns { _abandoned: reason } — the caller discards with
+// its usual message. Transport: a START that cannot reach the server is a
+// transport failure (the caller's local fallback, as before); a poll that
+// cannot is retried and only FIT_POLL_TRANSPORT_RETRIES in a row are. A
+// record whose heartbeat stops (a restarted worker takes the fit thread with
+// it) is a failed fit, never an endless spinner. Cancellation also reaches
+// the server when the page is closed (pagehide beacon) and, server-side,
+// when polls stop for three minutes (above the ~1-minute timer throttling of a hidden browser tab).
+const FIT_POLL_MS = 500;
+const FIT_POLL_TRANSPORT_RETRIES = 5;
+const FIT_HEARTBEAT_LOST_SEC = 30;
+const _runningFitJobs = new Set();
+// The current server fit of each tab record (unit 2, Codex round 1): a new
+// start for the same tab — Ctrl/Cmd+F bypasses the disabled button, and
+// Auto-Fit and Run Fit share a tab — SUPERSEDES the previous job: it is
+// cancelled on the server and its loop returns { _abandoned: 'superseded' },
+// on which the caller does nothing at all (the new fit owns the spinner and
+// the result).
+const _fitJobByOwner = new WeakMap();
+function _cancelFitJob(jobId) {
+  try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
+}
+if (typeof window !== 'undefined' && window.addEventListener) {
+  window.addEventListener('pagehide', () => {
+    for (const id of _runningFitJobs) {
+      try { navigator.sendBeacon('/api/fit/cancel/' + encodeURIComponent(id)); } catch (_) { /* best effort */ }
+    }
+  });
+}
+function _fitHttpError(status, msg, prefix) {
+  const err = new Error(msg || ((prefix || 'Fit request failed') + ' (HTTP ' + status + ').'));
+  err.serverError = true;
+  err.httpStatus = status;
+  return err;
+}
+async function _serverFitJob(fitReq, guard) {
+  guard = guard || {};
+  const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
+  let resp;
+  try {
+    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
+                                           body: JSON.stringify(fitReq), signal: guard.signal });
+  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+  if (resp.ok === false) {
+    let msg = null;
+    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+    throw _fitHttpError(resp.status, msg);
+  }
+  let started;
+  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+  const jobId = started && started.job_id;
+  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
+  _runningFitJobs.add(jobId);
+  if (guard.owner) {
+    const prev = _fitJobByOwner.get(guard.owner);
+    if (prev && prev !== jobId) _cancelFitJob(prev);
+    _fitJobByOwner.set(guard.owner, jobId);
+  }
+  let misses = 0;
+  try {
+    while (true) {
+      await new Promise(r => setTimeout(r, FIT_POLL_MS));
+      if (guard.signal && guard.signal.aborted) {
+        _cancelFitJob(jobId);
+        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
+      }
+      if (guard.owner && _fitJobByOwner.get(guard.owner) !== jobId) return { _abandoned: 'superseded' };   // its successor cancelled it
+      const why = guard.abandoned ? guard.abandoned() : null;
+      if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
+      let pr, rec;
+      try {
+        pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
+      } catch (e) {
+        if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
+        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
+          _cancelFitJob(jobId);
+          const err = new Error('Lost contact with the server during the fit (' + ((e && e.message) || 'network error') + ').');
+          err.transportFailure = true;
+          throw err;
+        }
+        continue;
+      }
+      if (pr.ok === false) {
+        _cancelFitJob(jobId);
+        let msg = null;
+        try { const j = await pr.json(); msg = (j && j.error) || null; } catch (_) { /* non-JSON body */ }
+        throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
+      }
+      try { rec = await _readFitReply(pr); } catch (e) {
+        if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
+        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
+          _cancelFitJob(jobId);
+          if (isTransport(e)) e.transportFailure = true;
+          throw e;
+        }
+        continue;
+      }
+      misses = 0;
+      if (rec.status === 'done') return rec.result;
+      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
+      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
+      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
+        _cancelFitJob(jobId);
+        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
+                                 ' s — it was probably restarted). Run the fit again.');
+      }
+      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
+    }
+  } finally {
+    _runningFitJobs.delete(jobId);
+    if (guard.owner && _fitJobByOwner.get(guard.owner) === jobId) _fitJobByOwner.delete(guard.owner);
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7559,10 +7683,8 @@ async function runAutoFitC1sGraphite() {
       bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
     }
     const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
-    const resp = await fetch('/api/fit', {
-      method: 'POST',
-      headers: { 'Content-Type': 'application/json' },
-      body: JSON.stringify({
+    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
+    const json = await _serverFitJob({
         session_id: sessionId,
         background: bgPayload,
         peaks: peakSpecs,
@@ -7572,21 +7694,31 @@ async function runAutoFitC1sGraphite() {
         // the model without it; a redundant anchor must not set the energy
         // reference of a whole spectrum (see applyAutoFitResult).
         require_component: anchorId,
-      }),
+    }, {
+      owner: fittingTab,
       signal: ctrl.signal,
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
     });
     clearTimeout(timer);
-    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
-    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
-    // reach the parser and read as "the server's reply could not be read")
-    if (resp.ok === false) {
-      let msg = null;
-      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
-      err.httpStatus = resp.status;
-      throw err;
+    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
+    // that fit started from the model now on the tab and owns the result — no
+    // rollback here, which would overwrite it
+    if (json && json._abandoned === 'superseded') return;
+    // F2: a non-2xx reply is a failed REQUEST with its status in the message
+    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
+    // failed fit with its own message (unreadableReply).
+    if (json && json._abandoned === 'tab') {
+      _hideFitSpinner();
+      notify('Auto-fit discarded — tab switched during fit.', 'amber');
+      _autoFitRestore(snap, fittingTab);
+      return;
+    }
+    if (json && json._abandoned === 'model') {
+      _hideFitSpinner();
+      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
+      _autoFitRestore(snap, fittingTab);
+      return;
     }
-    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
@@ -8053,26 +8185,29 @@ async function runFit(opts = {}) {
       n_perturb: 3,
       n_starts: nStarts       // the server also skips it for the global methods
     };
-    let resp, json;
-    try {
-      resp = await fetch('/api/fit', {
-        method: 'POST',
-        headers: { 'Content-Type': 'application/json' },
-        body: JSON.stringify(fitReq)
-      });
-    } catch (e) { _asTransport(e); }
-    if (resp.ok === false) {
-      // HTTP failure: read a message if the body is JSON, but a 502 HTML
-      // page is still a SERVER failure, never a reason to switch engines.
-      let msg = null;
-      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
-      err.serverError = true;
-      throw err;
+    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
+    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
+    // a SERVER failure (serverError), never a reason to switch engines; a
+    // START that cannot reach the server is a transport failure, as the single
+    // request was. The ownership checks below also run inside the poll loop,
+    // so a switched tab or an edited model stops the server's work at once.
+    const json = await _serverFitJob(fitReq, {
+      owner: fittingTab,
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
+    });
+    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
+    if (json && json._abandoned === 'tab') {
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
+      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
+      return;
+    }
+    if (json && json._abandoned === 'model') {
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
+      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
+      return;
     }
-    // F2: reading the body can fail in transport; a body that was read but is
-    // not JSON is the server's reply — a failed fit, not a fallback
-    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
     if (json.error) {
       const err = new Error(json.error);
       err.serverError = true;
diff --git a/tests/js/fit_start_poll.test.js b/tests/js/fit_start_poll.test.js
new file mode 100644
index 0000000..a4b7045
--- /dev/null
+++ b/tests/js/fit_start_poll.test.js
@@ -0,0 +1,176 @@
+// Unit 2 (2026-09-27): Run Fit and Auto-Fit start the fit and poll for it
+// (_serverFitJob). Pinned: the result is the /api/fit body; a bad request's
+// message and status are the synchronous route's; ownership (a switched tab,
+// an edited model) cancels the server's job and discards; transport keeps its
+// meaning (a START that cannot reach the server may fall back to the local
+// engine; one lost poll does not; five in a row do); a lost heartbeat, a
+// cancelled or errored record are failed fits; F2's NaN rule applies to the
+// final record; the 2-minute Auto-Fit abort cancels the job.
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+
+const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
+const lines = html.split('\n');
+function extractFn(name) {
+  const re = new RegExp('^(async )?function ' + name + '\\(');
+  const start = lines.findIndex(l => re.test(l));
+  assert.ok(start >= 0, `function ${name} not found`);
+  let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) {
+    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
+    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
+  }
+  assert.fail('unbalanced ' + name);
+}
+const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };
+
+// fetch scripted by URL; every call recorded
+function server(script) {
+  const calls = [];
+  const fetch = async (url, init) => {
+    calls.push({ url, method: (init && init.method) || 'GET' });
+    const h = script(url, init, calls);
+    if (h instanceof Error) throw h;
+    return h;
+  };
+  return { fetch, calls };
+}
+const ok = (obj, status = 200) => ({ ok: true, status, text: async () => (typeof obj === 'string' ? obj : JSON.stringify(obj)) });
+const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj === undefined) throw new SyntaxError('x'); return obj; } });
+
+function make(fetch) {
+  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
+    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
+  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
+    fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
+}
+const START = '/api/fit/start';
+const isProgress = u => u.startsWith('/api/fit/progress/');
+const isCancel = u => u.startsWith('/api/fit/cancel/');
+
+test('start -> running polls -> done: the result is the /api/fit body; no job is left registered', async () => {
+  let n = 0;
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
+    : isProgress(u) ? (++n < 3 ? ok({ status: 'running', heartbeat_age_sec: 0.4 }) : ok({ status: 'done', result: { success: true, x: 1 } }))
+    : ok({}));
+  const { _serverFitJob, _runningFitJobs } = make(s.fetch);
+  assert.deepStrictEqual(await _serverFitJob({ a: 1 }, {}), { success: true, x: 1 });
+  assert.strictEqual(s.calls.filter(c => isProgress(c.url)).length, 3);
+  assert.strictEqual(_runningFitJobs.size, 0);
+  assert.ok(!s.calls.some(c => isCancel(c.url)), 'a finished job is not cancelled');
+});
+
+test('a bad request: the synchronous route\'s message and status, immediately; no poll', async () => {
+  const s = server(u => u === START ? bad(400, { error: 'n_perturb must be between 0 and 10' }) : assert.fail(u));
+  const { _serverFitJob } = make(s.fetch);
+  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /n_perturb must be between/.test(e.message));
+});
+
+test('a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)', async () => {
+  const s = server(u => new TypeError('Failed to fetch'));
+  const { _serverFitJob } = make(s.fetch);
+  await assert.rejects(_serverFitJob({}, {}), e => e.transportFailure === true && !e.serverError);
+});
+
+test('an error record is a failed fit with the synchronous message and status', async () => {
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
+    : ok({ status: 'error', http_status: 400, error: 'The model is not determined by these data: 8 free parameters for 6 data points' }));
+  const { _serverFitJob } = make(s.fetch);
+  await assert.rejects(_serverFitJob({}, {}), e => e.serverError && e.httpStatus === 400 && /not determined by these data/.test(e.message));
+});
+
+test('a done record carrying NaN is F2\'s failed fit (unreadable reply), not a transport failure', async () => {
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202)
+    : isProgress(u) ? ok('{"status": "done", "result": {"success": true, "s": NaN}}') : ok({}));
+  const { _serverFitJob } = make(s.fetch);
+  await assert.rejects(_serverFitJob({}, {}), e => e.unreadableReply === true && e.serverError && !e.transportFailure && /non-finite/.test(e.message));
+});
+
+test('one lost poll is retried; five in a row are a transport failure and cancel the job', async () => {
+  let n = 0;
+  const flaky = server(u => u === START ? ok({ job_id: 'J' }, 202)
+    : isProgress(u) ? (++n <= 4 ? new TypeError('network') : ok({ status: 'done', result: { success: true } })) : ok({}));
+  assert.deepStrictEqual(await make(flaky.fetch)._serverFitJob({}, {}), { success: true });
+  const dead = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? new TypeError('network') : ok({}));
+  await assert.rejects(make(dead.fetch)._serverFitJob({}, {}), e => e.transportFailure === true && /Lost contact/.test(e.message));
+  assert.ok(dead.calls.some(c => isCancel(c.url) && c.method === 'POST'), 'the server is told to stop');
+});
+
+test('a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner', async () => {
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 45 }) : ok({}));
+  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped working on the fit/.test(e.message));
+});
+
+test('a job cancelled on the server (abandoned) is reported, not waited for', async () => {
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : ok({ status: 'cancelled' }));
+  await assert.rejects(make(s.fetch)._serverFitJob({}, {}), e => e.serverError && /stopped on the server/.test(e.message));
+});
+
+test('ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason', async () => {
+  for (const reason of ['tab', 'model']) {
+    let polls = 0;
+    const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (polls++, ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
+    let t = 0;
+    const out = await make(s.fetch)._serverFitJob({}, { abandoned: () => (++t > 2 ? reason : null) });
+    assert.deepStrictEqual(out, { _abandoned: reason });
+    assert.ok(s.calls.some(c => isCancel(c.url) && c.method === 'POST'), reason + ': the server is told to stop');
+    assert.strictEqual(polls, 2, 'no poll after the model or tab changed');
+  }
+});
+
+test('the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError', async () => {
+  const ctrl = { aborted: false, reason: null };
+  let polls = 0;
+  const s = server(u => u === START ? ok({ job_id: 'J' }, 202) : isProgress(u) ? (++polls === 2 && (ctrl.aborted = true, ctrl.reason = Object.assign(new Error('timeout'), { name: 'AbortError' })), ok({ status: 'running', heartbeat_age_sec: 0 })) : ok({}));
+  await assert.rejects(make(s.fetch)._serverFitJob({}, { signal: ctrl }), e => e.name === 'AbortError');
+  assert.ok(s.calls.some(c => isCancel(c.url)));
+});
+
+test('Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more', () => {
+  assert.match(extractFn('runFit'), /await _serverFitJob\(fitReq, \{/);
+  assert.match(extractFn('runAutoFitC1sGraphite'), /await _serverFitJob\(\{/);
+  assert.ok(!/fetch\('\/api\/fit'/.test(html), 'no synchronous /api/fit fetch left');
+  // the ownership reasons are the ones the discard messages handle
+  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
+    const src = extractFn(fn);
+    assert.match(src, /_abandoned === 'tab'/, fn);
+    assert.match(src, /_abandoned === 'model'/, fn);
+  }
+  assert.match(html, /addEventListener\('pagehide'/, 'a closed page cancels its running fits');
+});
+
+test('a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)', async () => {
+  let n = 0;
+  let releaseFirst;
+  const gate = new Promise(r => { releaseFirst = r; });
+  const s = server(u => u === START ? ok({ job_id: 'J' + (++n) }, 202)
+    : isProgress(u) ? ok({ status: 'running', heartbeat_age_sec: 0 }) : ok({}));
+  // a poll loop that yields between polls, so two jobs can interleave
+  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
+    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
+    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
+  const { _serverFitJob } = new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob };')(
+    s.fetch, f => { setImmediate(f); return 0; }, class extends Error {});   // yield to the event loop between polls
+  const owner = { id: 'tab-1' };
+  let polls2 = 0;
+  const first = _serverFitJob({}, { owner });
+  await new Promise(r => setImmediate(r)); await new Promise(r => setImmediate(r));
+  const second = _serverFitJob({}, { owner, abandoned: () => (++polls2 > 3 ? 'tab' : null) });
+  assert.deepStrictEqual(await first, { _abandoned: 'superseded' });
+  assert.ok(s.calls.some(c => c.url === '/api/fit/cancel/J1' && c.method === 'POST'), 'the first job is cancelled on the server');
+  assert.deepStrictEqual(await second, { _abandoned: 'tab' }, 'the second runs on, owning the tab');
+  // another tab's job is not touched
+  const other = _serverFitJob({}, { owner: { id: 'tab-2' }, abandoned: () => 'model' });
+  assert.deepStrictEqual(await other, { _abandoned: 'model' });
+});
+
+test('both callers pass their tab as the owner and do nothing at all when superseded', () => {
+  for (const fn of ['runFit', 'runAutoFitC1sGraphite']) {
+    const src = extractFn(fn);
+    assert.match(src, /owner: fittingTab,/, fn);
+    assert.match(src, /if \(json && json\._abandoned === 'superseded'\) return;/, fn);
+  }
+});
diff --git a/tests/test_fit_start_poll.py b/tests/test_fit_start_poll.py
new file mode 100644
index 0000000..962bbf3
--- /dev/null
+++ b/tests/test_fit_start_poll.py
@@ -0,0 +1,216 @@
+"""Unit 2 (2026-09-27): long fits via start-then-poll.
+
+/api/fit/start validates exactly as /api/fit, runs the SAME run_fit in a
+background thread on Find Peaks' job records, and the page polls
+/api/fit/progress. Pinned here: a polled fit is the synchronous fit (same
+body; byte-identical for Levenberg-Marquardt); every validation error is
+immediate and word-for-word the same; a run_fit error becomes the same
+message and status in the record; cancel (explicit, or no poll for
+FIT_JOB_ABANDON_SEC) stops the fit within seconds; the heartbeat; every poll
+is a short request.
+"""
+
+import io
+import json
+import time
+
+import numpy as np
+import pytest
+
+import app as app_module
+from app import create_app
+
+
+def _gl(x, c, a, w):
+    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
+
+
+@pytest.fixture()
+def client(tmp_path):
+    a = create_app(upload_folder=str(tmp_path))
+    a.config["TESTING"] = True
+    with a.test_client() as c:
+        yield c
+
+
+def _upload(client, n=200, comps=((284.5, 5000, 0.9), (286.2, 1500, 1.1)), seed=3):
+    rng = np.random.default_rng(seed)
+    x = np.linspace(281.0, 292.0, n)
+    y = rng.poisson(300 + sum(_gl(x, c, a, w) for c, a, w in comps)).astype(float)
+    csv = "\n".join(f"{a:.4f},{b:.1f}" for a, b in zip(x, y))
+    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
+    assert r.status_code == 200, r.get_json()
+    return r.get_json()["session_id"]
+
+
+def _specs(comps):
+    return [{"id": str(i + 1), "shape": "pseudo_voigt_gl", "center": c + 0.1, "fwhm": w * 1.1, "amplitude": a * 0.8,
+             "gl_ratio": 0.3, "amplitude_min": 0} for i, (c, a, w) in enumerate(comps)]
+
+
+def _body(sid, comps, method="leastsq", **extra):
+    return {"session_id": sid, "background": {"method": "shirley"}, "peaks": _specs(comps),
+            "fit_method": method, "n_perturb": 1, "n_starts": 0, **extra}
+
+
+def _poll(client, job_id, limit=300.0):
+    t0, longest = time.time(), 0.0
+    while True:
+        q0 = time.time()
+        r = client.get(f"/api/fit/progress/{job_id}")
+        longest = max(longest, time.time() - q0)
+        assert r.status_code == 200
+        rec = json.loads(r.get_data(as_text=True))
+        if rec["status"] not in ("queued", "running"):
+            return rec, longest
+        assert time.time() - t0 < limit, "job did not finish"
+        time.sleep(0.2)
+
+
+COMPS = ((284.5, 5000, 0.9), (286.2, 1500, 1.1))
+
+
+def test_a_polled_fit_is_the_synchronous_fit_byte_for_byte(client):
+    sid = _upload(client)
+    sync = client.post("/api/fit", json=_body(sid, COMPS))
+    assert sync.status_code == 200
+    start = client.post("/api/fit/start", json=_body(sid, COMPS))
+    assert start.status_code == 202
+    rec, longest = _poll(client, start.get_json()["job_id"])
+    assert rec["status"] == "done"
+    # Levenberg-Marquardt is byte-identical request to request (CLAUDE.md): same seed, same body
+    assert json.dumps(rec["result"], sort_keys=True) == json.dumps(sync.get_json(), sort_keys=True)
+    assert longest < 2.0, f"a poll took {longest:.2f} s"
+
+
+@pytest.mark.parametrize("method", ["differential_evolution", "basinhopping", "least_squares"])
+def test_the_stochastic_and_default_methods_give_the_synchronous_answer(client, method):
+    sid = _upload(client)
+    body = _body(sid, COMPS, method=method, n_perturb=0)
+    sync = client.post("/api/fit", json=body).get_json()
+    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
+    res = rec["result"]
+    assert res["random_seed"] == sync["random_seed"]
+    assert res["success"] == sync["success"] is True
+    # Trust-Region (also DE's and basinhopping's refinement) is not bit-reproducible
+    # across calls (BLAS alignment, CLAUDE.md); the answer is the same fit
+    assert res["statistics"]["reduced_chi_square"] == pytest.approx(sync["statistics"]["reduced_chi_square"], rel=1e-6)
+
+
+@pytest.mark.parametrize("patch,status,fragment", [
+    ({"n_perturb": 101}, 400, "n_perturb must be between"),
+    ({"fit_method": "ampgo"}, 400, "Unknown fit_method"),
+    ({"peaks": []}, 400, "'peaks' list is empty"),
+    ({"session_id": "0" * 32}, 404, "not found"),
+])
+def test_a_bad_request_is_refused_immediately_and_identically(client, patch, status, fragment):
+    sid = _upload(client)
+    body = {**_body(sid, COMPS), **patch}
+    a = client.post("/api/fit", json=body)
+    b = client.post("/api/fit/start", json=body)
+    assert a.status_code == b.status_code == status
+    assert a.get_json() == b.get_json()
+    assert fragment in b.get_json()["error"]
+
+
+def test_a_run_fit_refusal_reaches_the_record_with_the_synchronous_message_and_status(client):
+    sid = _upload(client, n=6)                                    # 8 free parameters, 6 points (unit F2)
+    body = {**_body(sid, COMPS), "n_perturb": 0}
+    sync = client.post("/api/fit", json=body)
+    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
+    assert rec["status"] == "error"
+    assert rec["http_status"] == sync.status_code == 400
+    assert rec["error"] == sync.get_json()["error"]
+
+
+SLOW = ((283.2, 2000, 0.8), (284.5, 5000, 0.9), (285.4, 1800, 1.0), (286.6, 1500, 1.1), (288.4, 900, 1.4))
+
+
+def test_cancel_stops_a_running_fit_within_seconds(client):
+    sid = _upload(client, n=300, comps=SLOW)
+    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
+    time.sleep(1.0)
+    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
+    assert rec["status"] in ("queued", "running"), "the fixture must still be running when cancelled"
+    t0 = time.time()
+    assert client.post(f"/api/fit/cancel/{job}").status_code == 200
+    rec, _ = _poll(client, job, limit=30)
+    assert rec["status"] == "cancelled"
+    assert time.time() - t0 < 10, f"cancel took {time.time() - t0:.1f} s"
+
+
+def test_an_abandoned_job_stops_itself_when_polls_stop(client, monkeypatch):
+    monkeypatch.setattr(app_module, "FIT_JOB_ABANDON_SEC", 1.5)
+    sid = _upload(client, n=300, comps=SLOW)
+    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
+    time.sleep(6.0)                                               # nobody polls
+    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
+    assert rec["status"] == "cancelled", rec["status"]
+
+
+def test_the_heartbeat_moves_while_the_fit_runs(client):
+    sid = _upload(client, n=300, comps=SLOW)
+    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
+    time.sleep(4.5)
+    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
+    assert rec["status"] in ("queued", "running")
+    assert rec["heartbeat_age_sec"] is not None and rec["heartbeat_age_sec"] < 3.0
+    assert rec["elapsed_sec"] >= 2.0
+    client.post(f"/api/fit/cancel/{job}")
+    _poll(client, job, limit=30)
+
+
+def test_unknown_and_malformed_job_ids(client):
+    assert client.get("/api/fit/progress/not-a-uuid").status_code == 400
+    assert client.get("/api/fit/progress/00000000-0000-0000-0000-000000000000").status_code == 404
+    assert client.post("/api/fit/cancel/not-a-uuid").status_code == 400
+
+
+def test_a_non_finite_result_reaches_the_page_unsanitised(tmp_path):
+    # the page's _readFitReply refuses NaN as a failed fit (unit F2): the job
+    # record must carry it exactly as /api/fit would, never as null
+    app_module._fit_job_write("11111111-1111-1111-1111-111111111111", str(tmp_path),
+                              {"status": "done", "result": {"x": float("nan")}})
+    text = (tmp_path / "11111111-1111-1111-1111-111111111111.job.json").read_text()
+    assert "NaN" in text
+
+
+def test_concurrency_is_bounded_one_fit_runs_per_process_the_rest_queue_and_admission_is_capped(client, monkeypatch):
+    """Codex round 1: four sync workers used to bound concurrent fits at four;
+    a thread per start would not. One fit runs per worker process; the rest
+    wait "queued" (heartbeating, cancellable); beyond FIT_JOB_MAX_ADMITTED the
+    start is refused at once with 503."""
+    sid = _upload(client, n=300, comps=SLOW)
+    body = _body(sid, SLOW, method="basinhopping", n_perturb=0)
+    jobs = [client.post("/api/fit/start", json=body).get_json()["job_id"] for _ in range(3)]
+    time.sleep(1.5)
+    states = [json.loads(client.get(f"/api/fit/progress/{j}").get_data(as_text=True))["status"] for j in jobs]
+    assert states.count("running") == 1 and states.count("queued") == 2, states
+    monkeypatch.setattr(app_module, "FIT_JOB_MAX_ADMITTED", 3)
+    busy = client.post("/api/fit/start", json=body)
+    assert busy.status_code == 503 and "busy" in busy.get_json()["error"]
+    for j in jobs:
+        client.post(f"/api/fit/cancel/{j}")
+    for j in jobs:
+        rec, _ = _poll(client, j, limit=60)
+        assert rec["status"] == "cancelled"
+    # the slots are returned: a new start is admitted again
+    ok = client.post("/api/fit/start", json=body)
+    assert ok.status_code == 202
+    client.post(f"/api/fit/cancel/{ok.get_json()['job_id']}")
+    _poll(client, ok.get_json()["job_id"], limit=60)
+
+
+@pytest.mark.parametrize("method", ["leastsq", "nelder", "differential_evolution"])
+def test_a_cancel_observed_mid_fit_is_a_cancellation_never_a_solver_error(method):
+    """Codex round 1: an aborted minimisation can surface as the solver's own
+    error (AttributeError from Levenberg-Marquardt, RuntimeError from
+    Nelder-Mead / DE); once cancellation was observed run_fit raises
+    FitCancelled."""
+    import fitting
+    x = np.linspace(281.0, 292.0, 300)
+    y = 300 + sum(_gl(x, c, a, w) for c, a, w in SLOW)
+    cancel = lambda: True               # observed at the first check: the minimisation is aborted mid-fit
+    with pytest.raises(fitting.FitCancelled):
+        fitting.run_fit(x, y, _specs(SLOW), background_method="linear", n_perturb=0,
+                        fit_kws={"method": method}, cancel=cancel)

exec
/bin/zsh -lc "sed -n '550,730p' app.py; rg -n 'fit/start|fit/progress|fit/cancel|_fit_job|_FIT_JOB' app.py; git diff fix-acceptance-holes..HEAD -- fitting.py; rg -n 'BLOCKER|MAJOR|MINOR|VERDICT' docs/autofit/codex/fit_start_poll_verdict_runA.md docs/autofit/codex/fit_start_poll_verdict_runB.md | tail -28" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
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
_FIT_JOB_ADMITTED = [0]
_FIT_JOB_ADMIT_LOCK = threading.Lock()


def _fit_job_admit() -> bool:
    with _FIT_JOB_ADMIT_LOCK:
        if _FIT_JOB_ADMITTED[0] >= FIT_JOB_MAX_ADMITTED:
            return False
        _FIT_JOB_ADMITTED[0] += 1
        return True


def _fit_job_release() -> None:
    with _FIT_JOB_ADMIT_LOCK:
        _FIT_JOB_ADMITTED[0] = max(0, _FIT_JOB_ADMITTED[0] - 1)


def _fit_job_marker(job_id: str, upload_folder: str, kind: str) -> Path:
    return Path(upload_folder) / f"{job_id}.{kind}"


def _fit_job_write(job_id: str, upload_folder: str, data: dict) -> None:
    """Atomic like _write_job_progress, but WITHOUT sanitising: a result's
    NaN / Infinity reach the page exactly as /api/fit sends them (the page's
    _readFitReply refuses them as a failed fit — unit F2)."""
    path = _job_progress_path(job_id, upload_folder)
    tmp = path.with_suffix(f".{threading.get_ident()}.tmp")
    try:
        tmp.write_text(json.dumps(data, allow_nan=True))
        os.replace(tmp, path)
    except OSError:
        logging.getLogger(__name__).exception("failed to write fit job %s", job_id)


def _fit_job_read(job_id: str, upload_folder: str):
    path = _job_progress_path(job_id, upload_folder)
    if not path.exists():
        return None
    try:
        _fit_job_marker(job_id, upload_folder, "polled").touch()
    except OSError:
        pass
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        data = {"status": "running", "elapsed_sec": 0.0}      # a read racing the first write
    hb = data.get("heartbeat")
    data["heartbeat_age_sec"] = round(time.time() - hb, 1) if isinstance(hb, (int, float)) else None
    return data


def _sweep_fit_job_markers(upload_folder: str) -> None:
    """Markers left by a job whose worker died (they are removed when a job
    finishes): same TTL as the job records, never raises."""
    cutoff = time.time() - _ANALYZE_JOB_TTL_SEC
    for pattern in ("*.cancel", "*.polled"):
        try:
            for m in Path(upload_folder).glob(pattern):
                try:
                    if m.stat().st_mtime < cutoff:
                        m.unlink(missing_ok=True)
                except OSError:
                    pass
        except OSError:
            pass


def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
    try:
        _fit_job_marker(job_id, upload_folder, "cancel").touch()
    except OSError:
        pass


def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None:
    """Start the fit thread and its heartbeat thread. ``run(fit_args, cancel)``
    returns ``(status, body)``; ``(None, None)`` means cancelled."""
    started = time.time()
    lock = threading.Lock()
    rec = {"status": "queued", "elapsed_sec": 0.0, "heartbeat": started}
    _fit_job_write(job_id, upload_folder, rec)
    _fit_job_marker(job_id, upload_folder, "polled").touch()
    cancel_path = _fit_job_marker(job_id, upload_folder, "cancel")
    polled_path = _fit_job_marker(job_id, upload_folder, "polled")
    finished = threading.Event()

    def cancelled() -> bool:
        if cancel_path.exists():
            return True
        try:
            return time.time() - polled_path.stat().st_mtime > FIT_JOB_ABANDON_SEC
        except OSError:
            return False

    def heartbeat() -> None:
        while not finished.wait(FIT_JOB_HEARTBEAT_SEC):
            with lock:
                if rec["status"] not in ("running", "queued"):
                    return
                rec["heartbeat"] = time.time()
                rec["elapsed_sec"] = round(time.time() - started, 1)
                _fit_job_write(job_id, upload_folder, rec)

    def worker() -> None:
        try:
            # queued until a run slot is free; a job cancelled or abandoned
            # while queued never runs
            got = False
            while not got:
                if cancelled():
                    status, body = None, None
                    break
                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
            if got:
                try:
                    with lock:
                        rec["status"] = "running"
                        rec["heartbeat"] = time.time()
                        _fit_job_write(job_id, upload_folder, rec)   # visible at once, not at the next heartbeat
                    status, body = run(fit_args, cancelled)
                finally:
                    _FIT_JOB_RUN_SLOTS.release()
        except Exception as exc:                       # the record must always leave "running"
            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
            status, body = 500, {"error": "Internal fitting error — see server log."}
        finally:
            _fit_job_release()
        with lock:
            rec["elapsed_sec"] = round(time.time() - started, 1)
            rec["heartbeat"] = time.time()
            if status is None or cancel_path.exists():
                rec.update(status="cancelled")
            elif status == 200:
                rec.update(status="done", result=body)
            else:
                rec.update(status="error", error=body.get("error"), http_status=status)
            finished.set()
            _fit_job_write(job_id, upload_folder, rec)
        for kind in ("cancel", "polled"):
            try:
                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
            except OSError:
                pass

    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()


def _require_json(f):
    """Decorator: return 400 if request body is not valid JSON."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return _err("Request must be JSON (Content-Type: application/json)")
        return f(*args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# Spin‑orbit element presets
62:# /api/fit request handling, shared by /api/fit and /api/fit/start (unit 2)
66:    """/api/fit's request validation, shared VERBATIM with /api/fit/start
555:# two small markers beside each: <job>.cancel (written by /api/fit/cancel,
565:# FIT_JOB_MAX_ADMITTED running + queued jobs; beyond that /api/fit/start
570:_FIT_JOB_RUN_SLOTS = threading.BoundedSemaphore(FIT_JOB_MAX_RUNNING)
571:_FIT_JOB_ADMITTED = [0]
572:_FIT_JOB_ADMIT_LOCK = threading.Lock()
575:def _fit_job_admit() -> bool:
576:    with _FIT_JOB_ADMIT_LOCK:
577:        if _FIT_JOB_ADMITTED[0] >= FIT_JOB_MAX_ADMITTED:
579:        _FIT_JOB_ADMITTED[0] += 1
583:def _fit_job_release() -> None:
584:    with _FIT_JOB_ADMIT_LOCK:
585:        _FIT_JOB_ADMITTED[0] = max(0, _FIT_JOB_ADMITTED[0] - 1)
588:def _fit_job_marker(job_id: str, upload_folder: str, kind: str) -> Path:
592:def _fit_job_write(job_id: str, upload_folder: str, data: dict) -> None:
605:def _fit_job_read(job_id: str, upload_folder: str):
610:        _fit_job_marker(job_id, upload_folder, "polled").touch()
622:def _sweep_fit_job_markers(upload_folder: str) -> None:
638:def _fit_job_cancel(job_id: str, upload_folder: str) -> None:
640:        _fit_job_marker(job_id, upload_folder, "cancel").touch()
645:def _fit_job_start(job_id: str, upload_folder: str, fit_args: dict, run) -> None:
651:    _fit_job_write(job_id, upload_folder, rec)
652:    _fit_job_marker(job_id, upload_folder, "polled").touch()
653:    cancel_path = _fit_job_marker(job_id, upload_folder, "cancel")
654:    polled_path = _fit_job_marker(job_id, upload_folder, "polled")
672:                _fit_job_write(job_id, upload_folder, rec)
683:                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
689:                        _fit_job_write(job_id, upload_folder, rec)   # visible at once, not at the next heartbeat
692:                    _FIT_JOB_RUN_SLOTS.release()
697:            _fit_job_release()
708:            _fit_job_write(job_id, upload_folder, rec)
711:                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
1266:    @app.post("/api/fit/start")
1276:        if not _fit_job_admit():
1281:            _sweep_fit_job_markers(upload_folder)
1282:            _fit_job_start(job_id, upload_folder, fit_args,
1285:            _fit_job_release()          # the job never started: its admission is returned
1289:    @app.get("/api/fit/progress/<job_id>")
1295:        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
1300:    @app.post("/api/fit/cancel/<job_id>")
1306:        _fit_job_cancel(job_id, app.config["UPLOAD_FOLDER"])
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5w0KyfB6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8lsLnCfB' (errno=Operation not permitted)
diff --git a/fitting.py b/fitting.py
index 63785a8..6b8f511 100644
--- a/fitting.py
+++ b/fitting.py
@@ -26,6 +26,8 @@ import hashlib
 import json
 import logging
 import re
+import threading
+import time
 import warnings
 from typing import Any
 
@@ -979,6 +981,44 @@ def _make_peak_params(
     return p
 
 
+# ── Cancellation (unit 2, 2026-09-27: long fits via start-then-poll) ────────
+# A fit started through /api/fit/start runs in a background thread; the page
+# can abandon it (a re-run, a tab switch, an edited model, a closed tab). The
+# job passes ``run_fit(..., cancel=callable)``; inside that thread every
+# model.fit below receives an ``iter_cb`` that returns True — lmfit's abort —
+# once ``cancel()`` is true (checked at most every 0.25 s). Thread-local, so a
+# concurrent fit in another thread of the same worker is untouched; and
+# WITHOUT a cancel callable no ``iter_cb`` argument is passed at all, so every
+# synchronous call is made exactly as before. Never part of fit_kws: the
+# request seed cannot see it.
+_CANCEL = threading.local()
+
+
+class FitCancelled(RuntimeError):
+    """The job was cancelled while run_fit ran."""
+
+
+def _cancel_kw() -> dict:
+    fn = getattr(_CANCEL, "fn", None)
+    if fn is None:
+        return {}
+    state = {"t": 0.0, "hit": False}
+
+    def iter_cb(params, it, resid, *args, **kws):
+        if state["hit"]:
+            return True
+        now = time.monotonic()
+        if now - state["t"] >= 0.25:
+            state["t"] = now
+            if fn():
+                state["hit"] = True
+                _CANCEL.hit = True
+                return True
+        return None
+
+    return {"iter_cb": iter_cb}
+
+
 def _finite_search_box(params: Parameters, x: np.ndarray,
                        y_sub: np.ndarray) -> dict[str, dict[str, float]]:
     """Give every freely varying parameter a finite box, in place.
@@ -1062,7 +1102,7 @@ def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
     for name, (lo, hi) in requested.items():
         boxed[name].set(min=lo, max=hi)
     generated = _finite_search_box(boxed, x, y_sub)
-    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws)
+    found = model.fit(y_sub, boxed, x=x, weights=weights, **kws, **_cancel_kw())
     found.box_unverified, found.search_box = bool(generated), generated
     if not generated:
         return found
@@ -1073,7 +1113,7 @@ def _search_then_refine(model, params, requested, y_sub, x, weights, kws):
     # passed through fit_kws would make least_squares raise.
     refine_kws = {"method": "least_squares", "nan_policy": kws.get("nan_policy", "omit")}
     try:
-        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws)
+        refined = model.fit(y_sub, free, x=x, weights=weights, **refine_kws, **_cancel_kw())
     except Exception:
         log.debug("refinement outside the search box raised", exc_info=True)
         return found
@@ -1111,7 +1151,7 @@ def _global_or_local_candidate(model, params, requested, y_sub, x, weights, kws)
         start[name].set(min=lo, max=hi)
     try:
         local = model.fit(y_sub, start, x=x, weights=weights,
-                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"))
+                          method="least_squares", nan_policy=kws.get("nan_policy", "omit"), **_cancel_kw())
     except Exception:
         log.debug("local candidate from the start raised", exc_info=True)
         return searched
@@ -1147,11 +1187,11 @@ def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
     start = params.copy()
     for name, (lo, hi) in requested.items():
         start[name].set(min=lo, max=hi)
-    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws)
+    found = model.fit(y_sub, start.copy(), x=x, weights=weights, **kws, **_cancel_kw())
     candidate = None
     try:   # from wherever the search stopped, even an evaluation-budget abort (as DE)
         refined = model.fit(y_sub, found.params.copy(), x=x, weights=weights,
-                            method="least_squares", nan_policy=nan_policy)
+                            method="least_squares", nan_policy=nan_policy, **_cancel_kw())
         if refined.success:
             candidate = refined
     except Exception:
@@ -1163,7 +1203,8 @@ def _basinhopping_candidate(model, params, requested, y_sub, x, weights, kws):
                          "so the result is not a verified fit")
         candidate = found
     try:
-        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy)
+        local = model.fit(y_sub, start.copy(), x=x, weights=weights, method="least_squares", nan_policy=nan_policy,
+                          **_cancel_kw())
     except Exception:
         log.debug("local candidate from the start raised", exc_info=True)
         return candidate
@@ -1489,7 +1530,7 @@ def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weigh
 # Main fitting API
 # ─────────────────────────────────────────────────────────────────────────────
 
-def run_fit(
+def _run_fit_impl(
     energy: np.ndarray,
     counts: np.ndarray,
     peak_specs: list[dict[str, Any]],
@@ -1750,7 +1791,7 @@ def run_fit(
         if kws.get("method") == "basinhopping":
             bounds = {name: requested_bounds.get(name, (par.min, par.max)) for name, par in params.items()}
             return _basinhopping_candidate(model, params, bounds, y_sub, x, weights, seeded(kws))
-        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws))
+        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())
 
     def fit_once(params):
         return fit_model(composite_model, params)
@@ -2048,3 +2089,35 @@ def compute_background_only(
         "background": bg.tolist(),
         "net_counts": (y - bg).tolist(),
     }
+
+
+def run_fit(*args, cancel=None, **kwargs):
+    """Fit peaks — see ``_run_fit_impl`` for every argument and the result.
+
+    ``cancel`` (optional, unit 2): a callable polled during the fit; once it
+    returns true every remaining minimisation aborts and ``FitCancelled`` is
+    raised instead of a result. Without it this is exactly the synchronous fit
+    it always was (no ``iter_cb`` reaches any minimiser)."""
+    if cancel is None:
+        return _run_fit_impl(*args, **kwargs)
+    _CANCEL.fn, _CANCEL.hit = cancel, False
+    try:
+        result = _run_fit_impl(*args, **kwargs)
+    except Exception as exc:
+        # An aborted minimisation can surface as the solver's own error (an
+        # AttributeError from Levenberg-Marquardt, a RuntimeError from
+        # Nelder-Mead or DE): once cancellation was observed it is a
+        # cancellation, never a failed fit (unit 2, Codex round 1).
+        if getattr(_CANCEL, "hit", False):
+            raise FitCancelled("the fit was cancelled") from exc
+        raise
+    finally:
+        hit = getattr(_CANCEL, "hit", False)
+        _CANCEL.fn, _CANCEL.hit = None, False
+    if hit:
+        raise FitCancelled("the fit was cancelled")
+    return result
+
+
+run_fit.__wrapped__ = _run_fit_impl
+
docs/autofit/codex/fit_start_poll_verdict_runA.md:13:Review unit 2 (long fits via start-then-poll): branch fix-fit-start-poll, which is stacked on fix-acceptance-holes (F2, deploying first). Review git diff fix-acceptance-holes..HEAD (app.py, fitting.py, templates/index.html, tests/test_fit_start_poll.py, tests/js/fit_start_poll.test.js, tests/js/fit_acceptance.test.js, tests/js/stale_statistics.test.js, tests/js/per_tab_state.test.js, scripts/public_fit_poll_check.py, docs/superpowers/plans/2026-09-27-long-fits-start-poll.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/fit_start_poll_verdict_runA.md:128:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5441:1. **MAJOR — Re-running does not cancel the previous fit.** [templates/index.html:8176](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8176) checks only tab identity and model equality. Ctrl/Cmd+F calls `runFit()` despite the disabled button. Pressing it again with unchanged inputs starts another job; both remain polled, preventing abandonment cancellation. Reproduced: two starts, two pending polls, zero cancellations. The older fit can finish first and cause the replacement to be discarded as “model edited.” Track a per-owner invocation and cancel its predecessor.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5443:2. **MAJOR — Fit concurrency is unbounded.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672) launches two threads for every accepted start without admission control or a bounded queue. Gunicorn’s four synchronous workers therefore no longer bound concurrent fitting work. A filesystem-mocked probe accepted 12 starts in one process and retained 24 job threads. Repeated submissions or simultaneous students can accumulate CPU-heavy fits and numerical allocations, degrading polling and potentially exhausting memory. Bound active jobs and queued requests.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5445:3. **MINOR — Abandonment cancellation becomes a solver error for several methods.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105) checks `hit` only after `_run_fit_impl` returns normally. Cancellation-induced exceptions skip that check. Real numerical probes produced an `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and DE. With an expired poll marker and no explicit cancel marker, job records consequently became `error` with HTTP 500/422 instead of `cancelled`. Normalize cancellation on exceptional exits while preserving unrelated errors.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5447:4. **MINOR — The public acceptance checker can hang indefinitely.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59) stops only when status changes. If the owning worker dies, its record remains `running`; subsequent polls succeed with an increasingly stale heartbeat. The script ignores that heartbeat and has no overall deadline, so it never reports failure or advances to the remaining targets.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5451:**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_verdict_runA.md:5454:1. **MAJOR — Re-running does not cancel the previous fit.** [templates/index.html:8176](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8176) checks only tab identity and model equality. Ctrl/Cmd+F calls `runFit()` despite the disabled button. Pressing it again with unchanged inputs starts another job; both remain polled, preventing abandonment cancellation. Reproduced: two starts, two pending polls, zero cancellations. The older fit can finish first and cause the replacement to be discarded as “model edited.” Track a per-owner invocation and cancel its predecessor.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5456:2. **MAJOR — Fit concurrency is unbounded.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672) launches two threads for every accepted start without admission control or a bounded queue. Gunicorn’s four synchronous workers therefore no longer bound concurrent fitting work. A filesystem-mocked probe accepted 12 starts in one process and retained 24 job threads. Repeated submissions or simultaneous students can accumulate CPU-heavy fits and numerical allocations, degrading polling and potentially exhausting memory. Bound active jobs and queued requests.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5458:3. **MINOR — Abandonment cancellation becomes a solver error for several methods.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105) checks `hit` only after `_run_fit_impl` returns normally. Cancellation-induced exceptions skip that check. Real numerical probes produced an `AttributeError` for Levenberg–Marquardt and `RuntimeError` for Nelder–Mead and DE. With an expired poll marker and no explicit cancel marker, job records consequently became `error` with HTTP 500/422 instead of `cancelled`. Normalize cancellation on exceptional exits while preserving unrelated errors.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5460:4. **MINOR — The public acceptance checker can hang indefinitely.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59) stops only when status changes. If the owning worker dies, its record remains `running`; subsequent polls succeed with an increasingly stale heartbeat. The script ignores that heartbeat and has no overall deadline, so it never reports failure or advances to the remaining targets.
docs/autofit/codex/fit_start_poll_verdict_runA.md:5464:**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_verdict_runB.md:13:Review unit 2 (long fits via start-then-poll): branch fix-fit-start-poll, which is stacked on fix-acceptance-holes (F2, deploying first). Review git diff fix-acceptance-holes..HEAD (app.py, fitting.py, templates/index.html, tests/test_fit_start_poll.py, tests/js/fit_start_poll.test.js, tests/js/fit_acceptance.test.js, tests/js/stale_statistics.test.js, tests/js/per_tab_state.test.js, scripts/public_fit_poll_check.py, docs/superpowers/plans/2026-09-27-long-fits-start-poll.md). Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.
docs/autofit/codex/fit_start_poll_verdict_runB.md:128:Finish with VERDICT: GO or VERDICT: NO-GO.
docs/autofit/codex/fit_start_poll_verdict_runB.md:5936:1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
docs/autofit/codex/fit_start_poll_verdict_runB.md:5939:2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
docs/autofit/codex/fit_start_poll_verdict_runB.md:5942:3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
docs/autofit/codex/fit_start_poll_verdict_runB.md:5945:4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
docs/autofit/codex/fit_start_poll_verdict_runB.md:5950:**VERDICT: NO-GO**
docs/autofit/codex/fit_start_poll_verdict_runB.md:5953:1. **MAJOR — Re-running does not supersede the previous job.** [templates/index.html:8175](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:8175)  
docs/autofit/codex/fit_start_poll_verdict_runB.md:5956:2. **MAJOR — Fit execution has no concurrency limit.** [app.py:672](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:672)  
docs/autofit/codex/fit_start_poll_verdict_runB.md:5959:3. **MINOR — Cancellation exceptions bypass `FitCancelled`.** [fitting.py:2105](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/fitting.py:2105)  
docs/autofit/codex/fit_start_poll_verdict_runB.md:5962:4. **MINOR — Acceptance checker can poll a dead worker forever.** [scripts/public_fit_poll_check.py:59](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/scripts/public_fit_poll_check.py:59)  
docs/autofit/codex/fit_start_poll_verdict_runB.md:5967:**VERDICT: NO-GO**

exec
/bin/zsh -lc "git diff fix-acceptance-holes..HEAD -- templates/index.html; sed -n '1240,1315p' app.py; cat scripts/public_fit_poll_check.py; sed -n '135,200p' docs/superpowers/plans/2026-09-27-long-fits-start-poll.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mYdHJvB3' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RumKtCug' (errno=Operation not permitted)
diff --git a/templates/index.html b/templates/index.html
index bb740ac..b81fa84 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -7445,6 +7445,130 @@ async function _readFitReply(resp) {
   }
 }
 
+// ── Long fits via start-then-poll (unit 2, 2026-09-27) ──────────────────────
+// The public URL ends a proxied request at ~100 s (Cloudflare 524); a
+// basinhopping fit of a large C 1s model takes 3–4 minutes. So the fit is
+// STARTED (/api/fit/start: the same validation as /api/fit, an immediate 400
+// for a bad request, else 202 + a job id) and POLLED (/api/fit/progress, a
+// short request every FIT_POLL_MS); no request of this path lasts longer than
+// a poll. The final record's `result` is exactly the body /api/fit returns,
+// read with F2's rules (_readFitReply: a body read but not JSON — a NaN — is
+// the server's failed fit). The caller's ownership rules run INSIDE the loop:
+// `guard.abandoned()` returning a reason ('tab' | 'model') cancels the job on
+// the server and returns { _abandoned: reason } — the caller discards with
+// its usual message. Transport: a START that cannot reach the server is a
+// transport failure (the caller's local fallback, as before); a poll that
+// cannot is retried and only FIT_POLL_TRANSPORT_RETRIES in a row are. A
+// record whose heartbeat stops (a restarted worker takes the fit thread with
+// it) is a failed fit, never an endless spinner. Cancellation also reaches
+// the server when the page is closed (pagehide beacon) and, server-side,
+// when polls stop for three minutes (above the ~1-minute timer throttling of a hidden browser tab).
+const FIT_POLL_MS = 500;
+const FIT_POLL_TRANSPORT_RETRIES = 5;
+const FIT_HEARTBEAT_LOST_SEC = 30;
+const _runningFitJobs = new Set();
+// The current server fit of each tab record (unit 2, Codex round 1): a new
+// start for the same tab — Ctrl/Cmd+F bypasses the disabled button, and
+// Auto-Fit and Run Fit share a tab — SUPERSEDES the previous job: it is
+// cancelled on the server and its loop returns { _abandoned: 'superseded' },
+// on which the caller does nothing at all (the new fit owns the spinner and
+// the result).
+const _fitJobByOwner = new WeakMap();
+function _cancelFitJob(jobId) {
+  try { fetch('/api/fit/cancel/' + encodeURIComponent(jobId), { method: 'POST', keepalive: true }).catch(() => {}); } catch (_) { /* best effort */ }
+}
+if (typeof window !== 'undefined' && window.addEventListener) {
+  window.addEventListener('pagehide', () => {
+    for (const id of _runningFitJobs) {
+      try { navigator.sendBeacon('/api/fit/cancel/' + encodeURIComponent(id)); } catch (_) { /* best effort */ }
+    }
+  });
+}
+function _fitHttpError(status, msg, prefix) {
+  const err = new Error(msg || ((prefix || 'Fit request failed') + ' (HTTP ' + status + ').'));
+  err.serverError = true;
+  err.httpStatus = status;
+  return err;
+}
+async function _serverFitJob(fitReq, guard) {
+  guard = guard || {};
+  const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
+  let resp;
+  try {
+    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
+                                           body: JSON.stringify(fitReq), signal: guard.signal });
+  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+  if (resp.ok === false) {
+    let msg = null;
+    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
+    throw _fitHttpError(resp.status, msg);
+  }
+  let started;
+  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
+  const jobId = started && started.job_id;
+  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
+  _runningFitJobs.add(jobId);
+  if (guard.owner) {
+    const prev = _fitJobByOwner.get(guard.owner);
+    if (prev && prev !== jobId) _cancelFitJob(prev);
+    _fitJobByOwner.set(guard.owner, jobId);
+  }
+  let misses = 0;
+  try {
+    while (true) {
+      await new Promise(r => setTimeout(r, FIT_POLL_MS));
+      if (guard.signal && guard.signal.aborted) {
+        _cancelFitJob(jobId);
+        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
+      }
+      if (guard.owner && _fitJobByOwner.get(guard.owner) !== jobId) return { _abandoned: 'superseded' };   // its successor cancelled it
+      const why = guard.abandoned ? guard.abandoned() : null;
+      if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
+      let pr, rec;
+      try {
+        pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
+      } catch (e) {
+        if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
+        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
+          _cancelFitJob(jobId);
+          const err = new Error('Lost contact with the server during the fit (' + ((e && e.message) || 'network error') + ').');
+          err.transportFailure = true;
+          throw err;
+        }
+        continue;
+      }
+      if (pr.ok === false) {
+        _cancelFitJob(jobId);
+        let msg = null;
+        try { const j = await pr.json(); msg = (j && j.error) || null; } catch (_) { /* non-JSON body */ }
+        throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
+      }
+      try { rec = await _readFitReply(pr); } catch (e) {
+        if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
+        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
+          _cancelFitJob(jobId);
+          if (isTransport(e)) e.transportFailure = true;
+          throw e;
+        }
+        continue;
+      }
+      misses = 0;
+      if (rec.status === 'done') return rec.result;
+      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
+      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
+      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
+        _cancelFitJob(jobId);
+        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
+                                 ' s — it was probably restarted). Run the fit again.');
+      }
+      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
+    }
+  } finally {
+    _runningFitJobs.delete(jobId);
+    if (guard.owner && _fitJobByOwner.get(guard.owner) === jobId) _fitJobByOwner.delete(guard.owner);
+  }
+}
+
 async function runAutoFitC1sGraphite() {
   // Pre-conditions
   if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
@@ -7559,10 +7683,8 @@ async function runAutoFitC1sGraphite() {
       bgPayload.manual_bg = _getManualAnchors().map(a => [a.x, a.y]);
     }
     const sessionId = await uploadToBackend(be2, inten2);   // after EVERY input above is captured
-    const resp = await fetch('/api/fit', {
-      method: 'POST',
-      headers: { 'Content-Type': 'application/json' },
-      body: JSON.stringify({
+    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
+    const json = await _serverFitJob({
         session_id: sessionId,
         background: bgPayload,
         peaks: peakSpecs,
@@ -7572,21 +7694,31 @@ async function runAutoFitC1sGraphite() {
         // the model without it; a redundant anchor must not set the energy
         // reference of a whole spectrum (see applyAutoFitResult).
         require_component: anchorId,
-      }),
+    }, {
+      owner: fittingTab,
       signal: ctrl.signal,
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
     });
     clearTimeout(timer);
-    // F2: a non-2xx reply is a failed REQUEST with its status in the message,
-    // as Run Fit has done since A0 (a Cloudflare 524 or a gunicorn 500 used to
-    // reach the parser and read as "the server's reply could not be read")
-    if (resp.ok === false) {
-      let msg = null;
-      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
-      err.httpStatus = resp.status;
-      throw err;
+    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
+    // that fit started from the model now on the tab and owns the result — no
+    // rollback here, which would overwrite it
+    if (json && json._abandoned === 'superseded') return;
+    // F2: a non-2xx reply is a failed REQUEST with its status in the message
+    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
+    // failed fit with its own message (unreadableReply).
+    if (json && json._abandoned === 'tab') {
+      _hideFitSpinner();
+      notify('Auto-fit discarded — tab switched during fit.', 'amber');
+      _autoFitRestore(snap, fittingTab);
+      return;
+    }
+    if (json && json._abandoned === 'model') {
+      _hideFitSpinner();
+      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
+      _autoFitRestore(snap, fittingTab);
+      return;
     }
-    const json = await _readFitReply(resp);   // F2: an unreadable reply is a failed fit with its own message
     if (json.error) throw new Error(json.error);
     if (json.success !== true) throw new Error(json.message || 'fit did not converge');
     if (!_ownerActive(fittingTab)) {
@@ -8053,26 +8185,29 @@ async function runFit(opts = {}) {
       n_perturb: 3,
       n_starts: nStarts       // the server also skips it for the global methods
     };
-    let resp, json;
-    try {
-      resp = await fetch('/api/fit', {
-        method: 'POST',
-        headers: { 'Content-Type': 'application/json' },
-        body: JSON.stringify(fitReq)
-      });
-    } catch (e) { _asTransport(e); }
-    if (resp.ok === false) {
-      // HTTP failure: read a message if the body is JSON, but a 502 HTML
-      // page is still a SERVER failure, never a reason to switch engines.
-      let msg = null;
-      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
-      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
-      err.serverError = true;
-      throw err;
+    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
+    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
+    // a SERVER failure (serverError), never a reason to switch engines; a
+    // START that cannot reach the server is a transport failure, as the single
+    // request was. The ownership checks below also run inside the poll loop,
+    // so a switched tab or an edited model stops the server's work at once.
+    const json = await _serverFitJob(fitReq, {
+      owner: fittingTab,
+      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
+    });
+    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
+    if (json && json._abandoned === 'tab') {
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
+      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
+      return;
+    }
+    if (json && json._abandoned === 'model') {
+      _hideFitSpinner();
+      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
+      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
+      return;
     }
-    // F2: reading the body can fail in transport; a body that was read but is
-    // not JSON is the server's reply — a failed fit, not a fallback
-    try { json = await _readFitReply(resp); } catch (e) { _asTransport(e); }
     if (json.error) {
       const err = new Error(json.error);
       err.serverError = true;
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
    def fit_start():
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return _err("request body must be a JSON object")
        fit_args, error = _prepare_fit_request(app, body)
        if error is not None:
            return error
        upload_folder = app.config["UPLOAD_FOLDER"]
        if not _fit_job_admit():
            return _err("The server is busy with other fits. Try again in a moment.", 503)
        job_id = str(uuid.uuid4())
        try:
            _sweep_expired_jobs(upload_folder)
            _sweep_fit_job_markers(upload_folder)
            _fit_job_start(job_id, upload_folder, fit_args,
                           lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
        except Exception:
            _fit_job_release()          # the job never started: its admission is returned
            raise
        return jsonify({"job_id": job_id}), 202

    @app.get("/api/fit/progress/<job_id>")
    def fit_progress(job_id):
        try:
            uuid.UUID(job_id)
        except ValueError:
            return _err("Invalid job_id format (expected UUID)", 400)
        data = _fit_job_read(job_id, app.config["UPLOAD_FOLDER"])
        if data is None:
            return _err(f"Job '{job_id}' not found", 404)
        return app.response_class(json.dumps(data, allow_nan=True), mimetype="application/json")

    @app.post("/api/fit/cancel/<job_id>")
    def fit_cancel(job_id):
        try:
            uuid.UUID(job_id)
        except ValueError:
            return _err("Invalid job_id format (expected UUID)", 400)
        _fit_job_cancel(job_id, app.config["UPLOAD_FOLDER"])
        return jsonify({"cancelled": True})

    # ── Health check ──────────────────────────────────────────────────────────

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})


#!/usr/bin/env python3
"""Post-deploy check for unit 2 (long fits via start-then-poll), THROUGH THE
PUBLIC URL — the path a student's browser takes, where Cloudflare ends a
single request at ~100 s (HTTP 524).

It does what the page does for Run Fit: upload, POST /api/fit/start, poll
GET /api/fit/progress every 0.5 s until the job leaves "running"; it records
the duration of EVERY request. PASS = the job finishes "done" with
success true, and no request took longer than MAX_REQUEST_S.

Usage:
  python scripts/public_fit_poll_check.py targets.json [BASE_URL] [target_id ...]

targets.json: the optimizer-disagreement target file (branch
investigate-optimizer-disagreement, docs/findings/optimizer-disagreement/
targets.json). Default targets: the five largest committed C 1s models,
the ones that took 183-256 s even without restarts.
"""
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

MAX_REQUEST_S = 10.0
HEARTBEAT_LOST_S = 30.0      # as the page: a record whose heartbeat stopped is a lost fit
DEADLINE_S = 20 * 60         # per target: never poll forever
DEFAULT_TARGETS = ["edf39ecb66ce", "d2bd62d2f976", "496c4edd97af", "0a5f464daf3d", "8b4c2f656a80"]


def _req(url, data=None, headers=None, method=None, timeout=60):
    t0 = time.time()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "xps-poll-check", **(headers or {})}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body, status = r.read(), r.status
    except urllib.error.HTTPError as e:
        body, status = e.read(), e.code
    return status, body, time.time() - t0


def run(base, t):
    durations = []
    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
    bnd = uuid.uuid4().hex
    form = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.csv\"\r\n"
            f"Content-Type: text/csv\r\n\r\n").encode() + csv + f"\r\n--{bnd}--\r\n".encode()
    st, body, d = _req(base + "/api/upload", form, {"Content-Type": f"multipart/form-data; boundary={bnd}"})
    durations.append(("upload", st, d))
    sid = json.loads(body)["session_id"]
    bg = t["background"]
    payload = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
               "peaks": t["specs"], "fit_method": "basinhopping", "n_perturb": 3, "n_starts": 3}
    st, body, d = _req(base + "/api/fit/start", json.dumps(payload).encode(), {"Content-Type": "application/json"})
    durations.append(("start", st, d))
    if st != 202:
        return {"id": t["id"], "verdict": "FAIL", "why": f"start returned {st}: {body[:200]!r}", "durations": durations}
    job = json.loads(body)["job_id"]
    t0 = time.time()
    while True:
        time.sleep(0.5)
        st, body, d = _req(base + f"/api/fit/progress/{job}")
        durations.append(("poll", st, d))
        rec = json.loads(body) if st == 200 else {"status": f"http {st}"}
        if rec.get("status") not in ("running", "queued"):
            break
        hb = rec.get("heartbeat_age_sec")
        if isinstance(hb, (int, float)) and hb > HEARTBEAT_LOST_S:
            rec = {"status": "lost", "error": f"heartbeat stopped {hb:.0f} s ago (worker restarted?)"}
            break
        if time.time() - t0 > DEADLINE_S:
            _req(base + f"/api/fit/cancel/{job}", b"", method="POST")
            rec = {"status": "deadline", "error": f"no result after {DEADLINE_S} s"}
            break
    longest = max(x[2] for x in durations)
    res = rec.get("result") or {}
    ok = rec.get("status") == "done" and res.get("success") is True and longest <= MAX_REQUEST_S
    return {"id": t["id"], "verdict": "PASS" if ok else "FAIL", "status": rec.get("status"),
            "success": res.get("success"), "chi2r": (res.get("statistics") or {}).get("reduced_chi_square"),
            "fit_wall_s": round(time.time() - t0, 1), "n_requests": len(durations),
            "longest_request_s": round(longest, 2), "error": rec.get("error")}


def main():
    targets = json.load(open(sys.argv[1]))
    base = sys.argv[2] if len(sys.argv) > 2 else "https://xps.fortierlab.org"
    ids = sys.argv[3:] or DEFAULT_TARGETS
    by_id = {t["id"]: t for t in targets}
    results = [run(base, by_id[i]) for i in ids]
    for r in results:
        print(json.dumps(r))
    print("OVERALL:", "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL")


if __name__ == "__main__":
    main()
    venv/bin/python scripts/public_fit_poll_check.py \
        .claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json

(≈ 5 × 3–4 minutes; one production worker thread each, sequentially.) Then
once in a browser on xps.fortierlab.org: the committed UCl4-graphite project,
C1s Scan, Method = Basin-hopping, Run Fit → "Fit complete" after a few
minutes; DevTools → Network: every `/api/fit/*` request short, no 524.

## 5. Verification

- Python `tests/test_fit_start_poll.py` (14): polled = synchronous byte for
  byte (Levenberg-Marquardt), the same answer for DE / basinhopping /
  Trust-Region (same seed, χ²ᵣ to 1e-6); four bad requests refused
  immediately and identically on both routes; a run_fit refusal (F2's
  determinacy) reaches the record with the synchronous message and 400;
  cancel stops a running basinhopping fit in < 10 s; a job nobody polls
  stops itself; the heartbeat moves; malformed / unknown ids; a NaN result
  reaches the page unsanitised.
- JS `tests/js/fit_start_poll.test.js` (11): done / running / error /
  cancelled / NaN / lost heartbeat; a failed start is a transport failure;
  one lost poll retried, five are transport and cancel the job; tab / model
  abandonment cancels and returns the reason with no further poll; the
  Auto-Fit abort cancels; no page path posts to the synchronous `/api/fit`.
  The existing runFit / Auto-Fit sandboxes (`fit_acceptance`,
  `stale_statistics`) serve their scripted single reply as a finished job
  (`jobAdapter` / `pollify`) so they keep testing what they tested;
  `_runningFitJobs` allowlisted (class A) in `per_tab_state`.
- Browser (:5151, committed UCl4-graphite project): Run Fit → 1 start + 53
  polls, no synchronous `/api/fit`, "Fit complete", statistics current; a
  basinhopping fit abandoned by a tab switch and by a centre edit → the usual
  discard messages at the next poll, a cancel POST, the server job
  `cancelled` within 0.5 s; Auto-Fit → start + poll, complete, current; the
  start made unreachable → the local fallback and its overlay, as before. No
  page errors.

## 6. Codex rounds

**Round 1 — NO-GO ×2** (`fit_start_poll_verdict_run{A,B}.md`; the same four
findings in both):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR: a re-run did not supersede — Ctrl/Cmd+F calls `runFit` past the disabled button; two jobs for one tab, the older could finish first and get the newer discarded as "model edited" | `_fitJobByOwner` (WeakMap keyed by the tab record): a new start for the same tab cancels the previous job on the server; the superseded loop returns `{ _abandoned: 'superseded' }` and its caller does NOTHING (the new fit owns spinner and result; Auto-Fit does not roll back, which would overwrite the new fit's model). Run Fit and Auto-Fit both pass their tab as `owner`. |
| 2 | MAJOR: unbounded concurrency — a thread per start, where four sync workers used to bound concurrent fits at four | each worker process runs at most `FIT_JOB_MAX_RUNNING` = 1 fit (a semaphore); the rest wait `queued` (heartbeating, cancellable, a queued job cancelled or abandoned never runs); at most `FIT_JOB_MAX_ADMITTED` = 6 running + queued per process, beyond that `/api/fit/start` answers 503 "The server is busy with other fits" at once (the page shows it as a failed fit). Production: ≤ 4 concurrent fits, as before. |
| 3 | MINOR: a cancellation observed mid-fit could surface as the solver's own error (AttributeError from Levenberg-Marquardt, RuntimeError from Nelder-Mead / DE) — an abandoned job became `error` 500 / 422 | `run_fit(cancel=)` turns any exception raised after cancellation was observed into `FitCancelled`; unrelated errors propagate unchanged |
| 4 | MINOR: `public_fit_poll_check.py` could poll a dead worker's record forever | a heartbeat older than 30 s is FAIL "lost"; a 20-minute deadline per target (the job is cancelled) |



codex
The new ownership check runs only between polls. I’m checking whether an older request can still apply a result or restore Auto-Fit’s snapshot when its response arrives after a replacement starts. I’m also checking admission cleanup when thread startup fails partway through.
exec
/bin/zsh -lc "sed -n '7570,7790p' templates/index.html; sed -n '8050,8430p' templates/index.html; sed -n '1,150p' tests/js/fit_acceptance.test.js; rg -n 'fittingTab|function _ownerActive|_autoFitRestore|_showFitSpinner|_hideFitSpinner' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
}

async function runAutoFitC1sGraphite() {
  // Pre-conditions
  if (!state.rawBE || !state.rawBE.length) { notify('Load a spectrum first.', 'amber'); return; }
  const tab = tabManager._getTab(tabManager.activeId);
  if (!tab) { notify('No active tab.', 'amber'); return; }
  if (!isC1sTab(tab)) {
    notify('Auto-Fit C1s Graphite is only available for C1s spectra (ROI midpoint 270–315 eV).', 'amber');
    return;
  }
  // OWNER FIRST: the confirmation below is an await; the tab that is active
  // when it resolves may not be the one the user asked to auto-fit.
  const fittingTab = _opOwner();
  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
  // Confirmation if existing peaks
  if (state.peaks.length >= 1) {
    const proceed = await _showAutoFitConfirmModal(state.peaks.length);
    if (!proceed) return;
    if (!_ownerActive(fittingTab)) {
      notify('Auto-fit cancelled — the tab changed while the confirmation was open.', 'amber');
      return;
    }
  }

  // Snapshot for failure rollback (separate from pushUndo, which only covers peaks).
  const snap = _autoFitSnapshot();

  // Step 1: find graphite in raw BE
  const { be: corrBE, inten } = getROIData();
  if (!corrBE.length) {
    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
    return;
  }
  const bgI = computeBackground(corrBE, inten);
  const bgSub = inten.map((v, i) => v - bgI[i]);
  // App convention: raw = corrected + state.ccShift
  const curShift = Number.isFinite(state.ccShift) ? state.ccShift : 0;
  const rawBE = corrBE.map(b => b + curShift);
  const graphiteRaw = findGraphiteRawBE(rawBE, bgSub);
  if (graphiteRaw == null) {
    notify('No strong peak found in the C1s ROI; Auto-Fit cannot proceed.', 'red', true);
    return;
  }

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
    // Unit 2: started and polled, like Run Fit (the 2-minute abort still applies)
    const json = await _serverFitJob({
        session_id: sessionId,
        background: bgPayload,
        peaks: peakSpecs,
        fit_method: fitMethod,
        n_perturb: 3,
        // step (c): is the charge-reference anchor REQUIRED? The server refits
        // the model without it; a redundant anchor must not set the energy
        // reference of a whole spectrum (see applyAutoFitResult).
        require_component: anchorId,
    }, {
      owner: fittingTab,
      signal: ctrl.signal,
      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
    });
    clearTimeout(timer);
    // superseded by a newer fit on this tab (Run Fit pressed during Auto-Fit):
    // that fit started from the model now on the tab and owns the result — no
    // rollback here, which would overwrite it
    if (json && json._abandoned === 'superseded') return;
    // F2: a non-2xx reply is a failed REQUEST with its status in the message
    // (_serverFitJob throws it with httpStatus); an unreadable reply is a
    // failed fit with its own message (unreadableReply).
    if (json && json._abandoned === 'tab') {
      _hideFitSpinner();
      notify('Auto-fit discarded — tab switched during fit.', 'amber');
      _autoFitRestore(snap, fittingTab);
      return;
    }
    if (json && json._abandoned === 'model') {
      _hideFitSpinner();
      notify('Auto-fit discarded because the model or its background / ROI settings were edited while it was running. Previous peaks and result restored. Run it again.', 'amber', true);
      _autoFitRestore(snap, fittingTab);
      return;
    }
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
    html += row('Alternative ' + (k + 1), a.chi2r, a.n_starts, a.components, false,
      `<button class="btn btn-sm" onclick="previewAlternative(${k})" title="Overlay this solution on the chart; click again to clear">Preview</button>
       <button class="btn btn-sm" onclick="useAlternative(${k})" title="Run the fit again starting from this solution. Your model changes only if that fit succeeds; you can undo it.">Use this solution</button>`);
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
  await runFit({ startPeaks: peaks, chosenAlternative: chosen });
}

async function runFit(opts = {}) {
  if (!state.rawBE.length) { notify('Load a spectrum first.', 'red', true); return; }
  if (!state.peaks.length) { notify('Add at least one peak.', 'red'); return; }
  pushUndo();

  _showFitSpinner();
  document.getElementById('sb-msg').textContent = 'Fitting\u2026';

  // Capture the tab that owns this fit so that if the user switches tabs
  // mid-request, we can discard the stale result instead of corrupting the
  // now-active tab's state.
  const fittingTab = _opOwner();

  const { be, inten } = getROIData();
  const bgIntensity = computeBackground(be, inten);
  const bgSubtracted = inten.map((v, i) => v - bgIntensity[i]);

  // Try Flask backend first
  let backendResult = null;
  let ctxAtRequest = null;   // set with the other request inputs; read again by the local fallback
  try {
    const bgType  = document.getElementById('bg-type').value;
    const bgStart = parseFloat(document.getElementById('bg-start').value);
    const bgEnd   = parseFloat(document.getElementById('bg-end').value);
    // Inclusive bg window — the same point set computeBackgroundCore draws;
    // the backend slices end-exclusive, so the request sends i1 + 1.
    const bgWin = _bgWindowIndices(be, bgStart, bgEnd);
    // EVERY request input is read from the owner before the upload await:
    // peaks, method, endpoint averaging and manual anchors (Codex round 2: a
    // request could carry A's spectrum with B's averaging and anchors).
    // opts.startPeaks: the request starts from an adopted alternative; the live
    // model is still the student's until this fit succeeds (useAlternative).
    const startModel = opts.startPeaks || state.peaks;
    const peakSpecs = startModel.map(peakToBackendSpec);
    // scattered-starts check: decided HERE, with the other request inputs,
    // before the first await (a tab switch during the upload must not turn it off)
    const nStarts = _startsUnlinkedCount(startModel) >= 2 ? _STARTS_N : 0;
    // the live model and its fit context as the student pressed the button: a
    // result must not be written over a model that was edited while it ran
    ctxAtRequest = _startsLiveKey();
    const fitMethod = document.getElementById('fit-method').value;
    const epAvgVal = parseInt(document.getElementById('bg-endpoint-avg').value) || 1;
    const bgPayload = { method: bgType, start_idx: bgWin.i0, end_idx: bgWin.i1 + 1, endpoint_avg: epAvgVal };
    if (bgType === 'manual') {
      // Anchors are stored in corrected-BE space, same frame as the uploaded
      // session data; backend expects [x, y] pairs.
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
    // Unit 2: started and polled (_serverFitJob) — no request lasts longer than
    // a poll, so none meets the public URL's ~100 s ceiling. An HTTP failure is
    // a SERVER failure (serverError), never a reason to switch engines; a
    // START that cannot reach the server is a transport failure, as the single
    // request was. The ownership checks below also run inside the poll loop,
    // so a switched tab or an edited model stops the server's work at once.
    const json = await _serverFitJob(fitReq, {
      owner: fittingTab,
      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
    });
    if (json && json._abandoned === 'superseded') return;   // a newer fit on this tab owns the spinner and the result
    if (json && json._abandoned === 'tab') {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }
    if (json && json._abandoned === 'model') {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }
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
// counting-noise-weighted chi-square; local results saved by unit A0 were
// UNWEIGHTED and keep the label "Residual variance", never chi-square.
function _isUnweightedLocal(fr) { return !!(fr && fr.objective === 'unweighted_residual_variance'); }
function _fitStatLabel(fr) {
  return _isUnweightedLocal(fr) ? 'Residual variance' : 'χ²ᵣ';
}
// A LOCAL result is a STARTING POINT, not a reportable result. Measured in
// unit W1 (docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md):
// with Poisson weighting the local engine matches the server on GL-type
// models (<= 4 meV, <= 1.4 % area on the lab's C1s scans) and, since A03
// (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
// wherever the two engines reach the same minimum (5 of 9 committed U 4f
// targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
// it still differs where an LA component's m moves on the server (held,
// exactly, at its start locally - LA is discontinuous in m, caM unit) and
// where the model has several minima; and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
// Every site that shows, exports or saves a fit result carries the
// designation, keyed on persisted identity so reloaded results are labelled.
const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
const _LOCAL_FIT_CAVEAT_UNWEIGHTED = 'Local unweighted fit: a starting point, not a reportable result. Run Fit before reporting.';
function _isLocalProvenance(p) {
  return !!(p && (p.engine === 'local' || p.objective === 'unweighted_residual_variance' || p.objective === 'poisson_weighted_chi_square'));
}
function _isLocalFit(fr) { return _isLocalProvenance(fr); }
// The record that governs the active model's designation: its live result,
// else the provenance it was imported / copied / restored with.
function _governingProvenance() {
  if (state.fitResult) return state.fitResult;
  const t = _activeTab();
  return (t && t.modelProvenance) || null;
}
function _localFitDetail(fr) {
  return _isUnweightedLocal(fr)
    ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
}
// The designation follows the MODEL, not only a live fit result: parameters
// imported from a .fit.json that was saved from a local fit are a starting
// point too (tab.modelProvenance, set by fromJSON, cleared by any new fit).
function _isLocalModel() {
  if (state.fitResult) return _isLocalFit(state.fitResult);
  const t = _activeTab();
  return !!(t && _isLocalProvenance(t.modelProvenance));
}
// The designation a tab's MODEL carries: its stored provenance (imported or
// copied), else one derived from its live local result — so that undo
// snapshots and batch copies taken while a local result exists keep it.
// Persistent designation in the Peaks sidebar (visible whatever panel is
// open), refreshed with the peak list and the results.
function _updateLocalModelBanner() {
  const el = document.getElementById('local-model-banner');
  if (!el) return;
  const t = _activeTab();
  // Stack view: entries that DRAW a local source's fit curves carry the
  // designation too (the stack legend rows scroll; this banner does not).
  let stackLocal = [];
  if (t && t.isStack) {
    const tm = (typeof tabManager !== 'undefined' && tabManager) ? tabManager : null;
    stackLocal = (t.entries || []).filter(e => e.visible && e.showFit).map(e => tm && tm._getTab(e.sourceTabId))
      .filter(src => src && _isLocalFit(src.fitResult)).map(src => src.name);
  }
  const previewLocal = (typeof _historyPreview !== 'undefined') && !!_historyPreview && _isLocalFit(_historyPreview.fitResult);
  const modelLocal = !(t && t.isStack) && _isLocalModel();
  if (!modelLocal && !previewLocal && !stackLocal.length) { el.style.display = 'none'; return; }
  el.style.backgroundImage = 'linear-gradient(rgba(245,158,11,0.14), rgba(245,158,11,0.14))';
  const governing = _governingProvenance();
  el.innerHTML = modelLocal
    ? '&#9888; <strong>' + (_isUnweightedLocal(governing) ? 'Local (unweighted) model' : 'Local model (Poisson-weighted, no uncertainties)') +
      ' &mdash; a starting point, not a reportable result.</strong> ' + _localFitDetail(governing) + ' Run Fit before quantifying, exporting or reporting.'
    : stackLocal.length
      ? '&#9888; <strong>Local fit curves shown for: ' + stackLocal.map(_escHtml).join(', ') + '</strong> &mdash; starting points, not reportable results. Run Fit on those spectra before reporting.'
      : '&#9888; <strong>The history preview overlay is a local fit &mdash; a starting point, not a reportable result.</strong>';
  el.style.display = 'block';
}
function _provenanceOf(tab) {
  if (!tab) return null;
  if (tab.modelProvenance) return JSON.parse(JSON.stringify(tab.modelProvenance));
  const fr = tab.fitResult;
  if (!_isLocalFit(fr)) return null;
  return { objective: fr.objective || null, engine: fr.engine || 'local', status: fr.status || null,
           weighting: fr.weighting || null, chiReduced: fr.chiReduced ?? null,
           reportable: false, caveat: _localFitCaveat(fr), derivedFrom: 'local_fit' };
}
function _localFitCaveat(fr) {
  if (!_isLocalFit(fr)) return '';
  return _isUnweightedLocal(fr) ? _LOCAL_FIT_CAVEAT_UNWEIGHTED : _LOCAL_FIT_CAVEAT;
}
function _fitStatusText(fr) {
  const tag = !_isLocalFit(fr) ? '' : (_isUnweightedLocal(fr) ? ' (starting point)' : ' (local, starting point)');
  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
}
function _applyStatCaption(fr) {
  const cap = document.getElementById('sb-chi-caption');
  if (!cap) return;
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
// Fit acceptance rule for the backend path (unit A0, 2026-09-15): nothing is
// shown, stored or exported as a fit result unless it converged, and a
// server-side error surfaces its message instead of silently handing the
// model to the local optimiser.
//
// Before this unit runFit checked `json.error` only: an lmfit result with
// success:false was applied and announced as "Fit complete (lmfit)" (audit
// A08), and ANY thrown error — a 400 validation error included — fell back
// to runFitLocal, which then returned the starting model (A01).
//
// runFit is extracted verbatim from templates/index.html; its collaborators
// are stubbed at the boundary (DOM, fetch, upload, chart/list renderers).

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
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

// Unit 2: Run Fit starts the fit and polls for it (_serverFitJob). These
// tests script the single /api/fit reply they always did; jobAdapter serves
// that reply as a finished job (start -> 202 + id; progress -> done + result),
// and a start that throws is still a transport failure.
const POLL_SRC = [constLineOf('FIT_POLL_MS'), constLineOf('FIT_POLL_TRANSPORT_RETRIES'), constLineOf('FIT_HEARTBEAT_LOST_SEC'),
  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(n => extractFn(n))].join('\n');
function constLineOf(n) { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; }
function jobAdapter(fetchImpl) {
  let reply = null;
  return async (url, init) => {
    if (url === '/api/fit/start') {
      const r = await fetchImpl('/api/fit', init);
      if (r && r.ok === false) return r;
      reply = r;
      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
    }
    if (url.startsWith('/api/fit/progress/')) {
      const r = reply;
      return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await r.text()) + '}' };
    }
    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
    return fetchImpl(url, init);
  };
}
const immediate = f => { f(); return 0; };

function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, disabled: false,
    setAttribute() {}, removeAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, contains() { return false; }, _c: null } });
  const document = { getElementById: el, querySelector: () => el('.btn-green'), querySelectorAll: () => [] };
  const be = Array.from({ length: 50 }, (_, i) => 280 + 0.2 * i);
  const state = { rawBE: be.slice(), rawIntensity: be.map(() => 100), ccShift: 0, fitResult: { marker: 'previous' },
    peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
  const owner = { id: 7 };
  const calls = { notify: [], local: 0, applied: 0 };
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
  const factory = new Function('setTimeout', 'document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
    src + '\nreturn { runFit };');
  const noop = () => {};
  const { runFit } = factory(immediate, document, state, jobAdapter(withText(fetchImpl)), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
    noop, noop, noop, () => owner, ownerActive || (o => o === owner), () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
    b => b.map(() => 0), specImpl || (p => ({ id: p.id, shape: 'gaussian' })), () => [], () => { calls.applied++; },
    () => 0.1, '', noop, noop, noop, noop, noop, noop,
    () => { calls.local++; return { success: true, engine: 'local' }; }, false, { warn: noop, error: noop, log: noop }, noop, () => owner);
  return { runFit, state, dom, calls };
}

const okResponse = body => async () => ({ ok: true, status: 200, json: async () => body });
// F2: the page reads a 2xx /api/fit body as text and parses it itself
// (_readFitReply). A mock that only defines json() gets the matching text().
function withText(fetchImpl) {
  return async (...a) => {
    const r = await fetchImpl(...a);
    if (r && typeof r.text !== 'function' && typeof r.json === 'function') r.text = async () => JSON.stringify(await r.json());
    return r;
  };
}

test('A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown', async () => {
  const env = makeEnv({ fetchImpl: okResponse({ success: false, message: 'Fit did not converge: max evaluations', statistics: { reduced_chi_square: 999 }, individual_peaks: [] }) });
  const before = JSON.stringify(env.state.peaks);
  await env.runFit();
  assert.equal(env.calls.applied, 0, 'applyBackendResult must not run');
  assert.equal(env.calls.local, 0, 'no silent local fallback');
  assert.equal(JSON.stringify(env.state.peaks), before, 'peaks unchanged');
  assert.equal(env.state.fitResult.marker, 'previous', 'previous fit result retained');
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /did not converge/i.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.ok(!/complete/i.test(env.dom['sb-msg'].textContent), env.dom['sb-msg'].textContent);
});

test('a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser', async () => {
  const env = makeEnv({ fetchImpl: async () => ({ ok: false, status: 400, json: async () => ({ error: 'peak 1: fwhm_min must be positive' }) }) });
  const before = JSON.stringify(env.state.peaks);
  await env.runFit();
  assert.equal(env.calls.local, 0, 'a 400 is not a reason to run the local fitter');
  assert.equal(env.calls.applied, 0);
  assert.equal(JSON.stringify(env.state.peaks), before);
  assert.ok(env.calls.notify.some(n => n.kind === 'red' && /fwhm_min must be positive/.test(n.msg)), JSON.stringify(env.calls.notify));
  assert.notEqual(env.dom['localfit-warn-overlay']?.classList._c, 'open', 'no "local fit performed" overlay');
});

test('a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay', async () => {
  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  await env.runFit();
  assert.equal(env.calls.local, 1, 'local fallback used for a genuine network failure');
  assert.equal(env.dom['localfit-warn-overlay'].classList._c, 'open');
});

test('a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay', async () => {
  const env = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  // replace the stubbed local fitter with a failing one
  const failing = makeEnv({ fetchImpl: async () => { throw new TypeError('Failed to fetch'); } });
  failing.calls.local = 0;
  // rebuild with a failing runFitLocal
  const dom = failing.dom;
  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
  const noop = () => {};
  const owner = { id: 1 };
  const state = failing.state;
  const { runFit } = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
    '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
    '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
    '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab', src + '\nreturn { runFit };')(
    { getElementById: id => (dom[id] ||= { value: '', textContent: '', style: {}, setAttribute() {}, classList: { add(c) { this._c = c; }, remove() { this._c = null; }, _c: null } }), querySelector: () => ({}), querySelectorAll: () => [] },
    state, async () => { throw new TypeError('Failed to fetch'); }, async () => 'sid', noop, noop, noop, noop, () => owner, o => o === owner,
    () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }), b => b.map(() => 0), p => ({ id: p.id }), () => [], noop,
    () => 0.1, '', noop, noop, noop, noop, noop, noop, () => ({ success: false, message: 'did not converge' }), false, { warn: noop }, noop, () => owner);
  await runFit();
  assert.notEqual(dom['localfit-warn-overlay']?.classList._c, 'open', 'overlay must not claim a local fit was performed');
  void env;
});

test('a converged backend result is applied (sanity)', async () => {
2354:function _ownerActive(owner) {
6688:function _showFitSpinner() {
6697:  _showFitSpinner._timer = setTimeout(() => {
6701:function _hideFitSpinner() {
6705:  clearTimeout(_showFitSpinner._timer);
6997:function _autoFitRestore(snap, owner) {
7583:  const fittingTab = _opOwner();
7584:  if (!fittingTab) { notify('No active spectrum tab.', 'amber'); return; }
7589:    if (!_ownerActive(fittingTab)) {
7641:  _showFitSpinner();
7698:      owner: fittingTab,
7700:      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
7711:      _hideFitSpinner();
7713:      _autoFitRestore(snap, fittingTab);
7717:      _hideFitSpinner();
7719:      _autoFitRestore(snap, fittingTab);
7724:    if (!_ownerActive(fittingTab)) {
7725:      _hideFitSpinner();
7727:      _autoFitRestore(snap, fittingTab);
7731:      _hideFitSpinner();
7733:      _autoFitRestore(snap, fittingTab);
7741:      _hideFitSpinner();
7742:      _autoFitRestore(snap, fittingTab);
7746:    _hideFitSpinner();
7750:    _hideFitSpinner();
7754:    _autoFitRestore(snap, fittingTab);
8122:  _showFitSpinner();
8128:  const fittingTab = _opOwner();
8195:      owner: fittingTab,
8196:      abandoned: () => (!_ownerActive(fittingTab) ? 'tab' : (!_sameFitKey(_startsLiveKey(), ctxAtRequest) ? 'model' : null)),
8200:      _hideFitSpinner();
8206:      _hideFitSpinner();
8228:    if (!_ownerActive(fittingTab)) {
8229:      _hideFitSpinner();
8239:      _hideFitSpinner();
8270:    _hideFitSpinner();
8274:    _hideFitSpinner();
8275:    if (!_ownerActive(fittingTab)) {
8290:      _hideFitSpinner();
8463:    _hideFitSpinner();
8824:  _hideFitSpinner();

exec
/bin/zsh -lc "rg --files -g 'python*' -g 'node*' -g '*pytest*' -g '*requirements*' -g '*package*' -g AGENTS.md -g '"'!docs/**'"'; ls -d venv /Users/skyefortier/xps-app/venv 2>/dev/null; git diff fix-acceptance-holes..HEAD -- tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js tests/test_browser_bg_window_request.py tests/test_browser_endpoint_avg_default.py CLAUDE.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
requirements.txt
requirements-dev.txt
/Users/skyefortier/xps-app/venv
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YR6nztDp' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2zBr413w' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 67207b4..7acfd9a 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -52,6 +52,9 @@ compatible with multi-worker gunicorn.
 | `DELETE` | `/api/session/<id>`       | Delete session files. |
 | `POST`   | `/api/background`         | Compute background curve for a session. |
 | `POST`   | `/api/fit`                | Run lmfit on a session with peak specs; returns chi², bgIntensity, bgSubtracted, fittedY, per-peak refined params + σ. |
+| `POST`   | `/api/fit/start`          | The same request and validation as `/api/fit` (an immediate identical 400 / 404); runs the SAME `run_fit` in a background thread; returns `{job_id}` 202 (unit 2, 2026-09-27). |
+| `GET`    | `/api/fit/progress/<id>`  | The job record: `status` running / done / error / cancelled, `elapsed_sec`, `heartbeat_age_sec`; `result` = exactly the `/api/fit` body; `error` + `http_status` = exactly what `/api/fit` would answer. |
+| `POST`   | `/api/fit/cancel/<id>`    | Stop the job (every minimisation aborts via lmfit's `iter_cb`); also automatic after 180 s without a poll. |
 
 ## Frontend Architecture
 
@@ -196,6 +199,31 @@ must read each field exactly the way its consumer reads it — integers as
 integers, energies through `parseFloat` — never a generic conversion
 (`_fitKeyCanon`). (Owner, 2026-09-26.)
 
+### Long fits start and poll (unit 2, 2026-09-27)
+
+Run Fit (incl. "Use this solution") and Auto-Fit never hold a request open
+for a fit: `_serverFitJob` starts it (`/api/fit/start`), polls every 0.5 s
+and reads the finished record's `result` (the `/api/fit` body) with F2's
+`_readFitReply` rules. So no request meets the public ~100 s ceiling (the five
+largest C 1s basinhopping models completed in 213–414 s through the poll
+path with no request longer than 0.28 s). Server: Find Peaks' job records
+(atomic JSON under the upload folder, readable by any worker), a fit thread
+and a 2 s heartbeat thread per job; `run_fit(cancel=)` gives every
+`model.fit` an `iter_cb` that aborts once the job is cancelled — without it
+the calls are made exactly as before (Levenberg-Marquardt byte-identical
+either way). Page: the ownership rules run INSIDE the poll loop (a switched
+tab or an edited model cancels the job and discards with the usual message);
+a START that cannot reach the server is still a transport failure (local
+fallback); a poll that cannot is retried, five in a row are; a stopped
+heartbeat (> 30 s) is a failed fit; a closed page sends a cancel beacon, and
+the server cancels a job nobody has polled for 180 s (above the ~1-minute
+timer throttling of hidden browser tabs). A new start for the same tab
+supersedes (cancels) the previous one. Each worker process RUNS one fit at a
+time (the rest wait `queued`) and admits at most 6, beyond that a 503 — with 4
+workers, at most 4 concurrent fits, the bound the synchronous route had. The synchronous `/api/fit` stays
+for scripts, tests and the Python twins. Plan:
+`docs/superpowers/plans/2026-09-27-long-fits-start-poll.md`.
+
 ### Timing claims are measured through the public URL
 
 A request from a student reaches the server through Cloudflare, whose edge
diff --git a/tests/js/fit_acceptance.test.js b/tests/js/fit_acceptance.test.js
index 97734af..14882f4 100644
--- a/tests/js/fit_acceptance.test.js
+++ b/tests/js/fit_acceptance.test.js
@@ -31,6 +31,32 @@ function extractFn(name) {
   assert.fail('unbalanced ' + name);
 }
 
+// Unit 2: Run Fit starts the fit and polls for it (_serverFitJob). These
+// tests script the single /api/fit reply they always did; jobAdapter serves
+// that reply as a finished job (start -> 202 + id; progress -> done + result),
+// and a start that throws is still a transport failure.
+const POLL_SRC = [constLineOf('FIT_POLL_MS'), constLineOf('FIT_POLL_TRANSPORT_RETRIES'), constLineOf('FIT_HEARTBEAT_LOST_SEC'),
+  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(n => extractFn(n))].join('\n');
+function constLineOf(n) { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; }
+function jobAdapter(fetchImpl) {
+  let reply = null;
+  return async (url, init) => {
+    if (url === '/api/fit/start') {
+      const r = await fetchImpl('/api/fit', init);
+      if (r && r.ok === false) return r;
+      reply = r;
+      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
+    }
+    if (url.startsWith('/api/fit/progress/')) {
+      const r = reply;
+      return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await r.text()) + '}' };
+    }
+    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
+    return fetchImpl(url, init);
+  };
+}
+const immediate = f => { f(); return 0; };
+
 function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
   const dom = {};
   const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, disabled: false,
@@ -41,14 +67,14 @@ function makeEnv({ fetchImpl, uploadImpl, specImpl, ownerActive }) {
     peaks: [{ id: 1, name: 'p', shape: 'Gaussian', center: 285, fwhm: 1.2, amplitude: 50, glMix: 50, asymmetry: 0 }] };
   const owner = { id: 7 };
   const calls = { notify: [], local: 0, applied: 0 };
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
-  const factory = new Function('document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
+  const factory = new Function('setTimeout', 'document', 'state', 'fetch', 'uploadToBackend', 'notify', 'pushUndo', '_showFitSpinner', '_hideFitSpinner',
     '_opOwner', '_ownerActive', 'getROIData', 'computeBackground', 'peakToBackendSpec', '_getManualAnchors', 'applyBackendResult',
     '_computeRFactor', '_CHISQ_TOOLTIP', '_updateRFactorUI', '_updateROIDisplay', 'renderPeakList', 'updatePlot', 'renderResults',
     '_autoSnapshot', 'runFitLocal', '_snapshotSuppressed', 'console', '_applyStatDisplay', '_activeTab',
     src + '\nreturn { runFit };');
   const noop = () => {};
-  const { runFit } = factory(document, state, withText(fetchImpl), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
+  const { runFit } = factory(immediate, document, state, jobAdapter(withText(fetchImpl)), uploadImpl || (async () => 'sid'), (msg, kind) => calls.notify.push({ msg, kind }),
     noop, noop, noop, () => owner, ownerActive || (o => o === owner), () => ({ be: state.rawBE.slice(), inten: state.rawIntensity.slice() }),
     b => b.map(() => 0), specImpl || (p => ({ id: p.id, shape: 'gaussian' })), () => [], () => { calls.applied++; },
     () => 0.1, '', noop, noop, noop, noop, noop, noop,
@@ -104,7 +130,7 @@ test('a transport failure whose local fallback does NOT converge shows no "local
   failing.calls.local = 0;
   // rebuild with a failing runFitLocal
   const dom = failing.dom;
-  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n');
+  const src = 'const _STARTS_N = 3;\n' + lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n') + '\nlet _historyPreview = null;\n' + ['runFit', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsUnlinkedCount', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey', '_startsIfCurrent'].map(extractFn).join('\n') + '\n' + POLL_SRC;
   const noop = () => {};
   const owner = { id: 1 };
   const state = failing.state;
diff --git a/tests/js/per_tab_state.test.js b/tests/js/per_tab_state.test.js
index 7c50461..eeea2c1 100644
--- a/tests/js/per_tab_state.test.js
+++ b/tests/js/per_tab_state.test.js
@@ -34,6 +34,7 @@ const ALLOWLIST = {
   _ssFocusIdx: 'A', _ssFiltered: 'A',
   _fpMeta: 'B', _fpModalDrag: 'A', _fpRegionsSelected: 'A', _fpExpandedElement: 'A',
   _findPeaksApplyConfirmResolver: 'A',
+  _runningFitJobs: 'A', _fitJobByOwner: 'A',   // unit 2: in-flight job ids (pagehide beacon; the current job of each tab record, WeakMap keyed by the record) — no spectrum content       // unit 2: ids of in-flight server fit jobs, for the pagehide cancel beacon — no spectrum content
   _undoDebounce: 'A',         // burst buffer: DOES hold a peaks snapshot, but bound to its owner record at burst start and flushed onto that record only — the async-ownership exception to class A's 'no spectrum content'
   // Populated constant catalogues (read-only tables) and the chart plugin
   // object: class B. Listed, not skipped, so a per-tab store hidden in an
diff --git a/tests/js/stale_statistics.test.js b/tests/js/stale_statistics.test.js
index 3b36b46..f902a59 100644
--- a/tests/js/stale_statistics.test.js
+++ b/tests/js/stale_statistics.test.js
@@ -301,6 +301,31 @@ test('the refresh re-renders Results only when its rendered state differs', () =
   assert.strictEqual(env.renders, 2, 'current again');
 });
 
+// Unit 2: Auto-Fit starts the fit and polls for it (_serverFitJob). Each
+// sandbox scripts the single /api/fit reply it always did; pollify serves it
+// as a finished job, and runs the poll loop's short waits at once (the
+// 2-minute Auto-Fit timer is left pending, as before).
+const POLL_SRC = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
+  'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();', ...['_cancelFitJob', '_fitHttpError', '_serverFitJob'].map(extractFn)].join('\n');
+function pollify(deps) {
+  const inner = deps.fetch;
+  let reply = null;
+  deps.fetch = async (url, init) => {
+    if (url === '/api/fit/start') {
+      const r = await inner('/api/fit', init);
+      if (r && r.ok === false) return r;
+      reply = r;
+      return { ok: true, status: 202, text: async () => JSON.stringify({ job_id: 'job-1' }) };
+    }
+    if (url.startsWith('/api/fit/progress/')) return { ok: true, status: 200, text: async () => '{"status": "done", "result": ' + (await reply.text()) + '}' };
+    if (url.startsWith('/api/fit/cancel/')) return { ok: true, status: 200, json: async () => ({}) };
+    return inner(url, init);
+  };
+  deps.setTimeout = (f, ms) => { if (!(ms >= 60000)) f(); return 1; };
+  deps.DOMException = class extends Error { constructor(m, n) { super(m); this.name = n; } };
+  return deps;
+}
+
 // ── Codex round 1 ───────────────────────────────────────────────────────────
 function keyFns() {
   const src = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n')
@@ -379,7 +404,7 @@ test('Auto-Fit discards (and rolls back) a response when the model or context wa
       fetch: async () => ({ text: async () => JSON.stringify({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
       applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
     const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-    await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+    await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
     return out;
   };
   const edited = await run(true);
@@ -424,7 +449,7 @@ test('F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply mes
     fetch: async () => ({ text: async () => '{"success": true, "statistics": {"reduced_chi_square": NaN}}' }),
     applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
   const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
   assert.strictEqual(out.applied, 0);
   assert.strictEqual(out.restored, true);
   assert.ok(out.notes.some(([m, k]) => k === 'red' && /^Auto-fit failed: .*non-finite number/.test(m)), JSON.stringify(out.notes));
@@ -451,7 +476,7 @@ for (const [label, reply, expect] of [
     fetch: async () => reply,
     applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true, console: { warn() {} } };
   const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
-  await new Function(...Object.keys(deps), src + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
+  await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
   assert.strictEqual(out.applied, 0);
   assert.strictEqual(out.restored, true);
   assert.ok(out.notes.some(([m, k]) => k === 'red' && expect.test(m)), JSON.stringify(out.notes));
diff --git a/tests/test_browser_bg_window_request.py b/tests/test_browser_bg_window_request.py
index ec16a02..3929747 100644
--- a/tests/test_browser_bg_window_request.py
+++ b/tests/test_browser_bg_window_request.py
@@ -133,7 +133,7 @@ def _setup(page, bg_start, bg_end):
 
 
 def _captured_fit_request(page):
-    with page.expect_request("**/api/fit", timeout=30000) as req_info:
+    with page.expect_request("**/api/fit/start", timeout=30000) as req_info:   # unit 2: the same request body, started then polled
         page.evaluate("() => { runFit(); }")
     body = req_info.value.post_data_json
     page.wait_for_timeout(300)
diff --git a/tests/test_browser_endpoint_avg_default.py b/tests/test_browser_endpoint_avg_default.py
index a40ccd4..86f21cd 100644
--- a/tests/test_browser_endpoint_avg_default.py
+++ b/tests/test_browser_endpoint_avg_default.py
@@ -119,7 +119,7 @@ def test_fresh_tab_defaults_to_3_and_the_fit_request_carries_it(browser, server)
             return { tabUi: tabManager._getTab(tabManager.activeId).ui.endpointAvg,
                      dom: document.getElementById('bg-endpoint-avg').value }; }""")
         assert ui == {"tabUi": "3", "dom": "3"}, ui
-        with pg.expect_request("**/api/fit", timeout=30000) as req:
+        with pg.expect_request("**/api/fit/start", timeout=30000) as req:   # unit 2: the same request body, started then polled
             pg.evaluate("() => { runFit(); }")
         assert req.value.post_data_json["background"]["endpoint_avg"] == 3
         pg.wait_for_timeout(300)

exec
/bin/zsh -lc "sed -n '1,48p' tests/js/fit_start_poll.test.js; sed -n '2325,2370p' templates/index.html; sed -n '8250,8315p' templates/index.html; sed -n '6950,7045p' templates/index.html; sed -n '1,85p' app.py; cat tests/conftest.py 2>/dev/null" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
// Unit 2 (2026-09-27): Run Fit and Auto-Fit start the fit and poll for it
// (_serverFitJob). Pinned: the result is the /api/fit body; a bad request's
// message and status are the synchronous route's; ownership (a switched tab,
// an edited model) cancels the server's job and discards; transport keeps its
// meaning (a START that cannot reach the server may fall back to the local
// engine; one lost poll does not; five in a row do); a lost heartbeat, a
// cancelled or errored record are failed fits; F2's NaN rule applies to the
// final record; the 2-minute Auto-Fit abort cancels the job.
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
const constLine = n => { const l = lines.find(x => x.startsWith('const ' + n)); assert.ok(l, n); return l; };

// fetch scripted by URL; every call recorded
function server(script) {
  const calls = [];
  const fetch = async (url, init) => {
    calls.push({ url, method: (init && init.method) || 'GET' });
    const h = script(url, init, calls);
    if (h instanceof Error) throw h;
    return h;
  };
  return { fetch, calls };
}
const ok = (obj, status = 200) => ({ ok: true, status, text: async () => (typeof obj === 'string' ? obj : JSON.stringify(obj)) });
const bad = (status, obj) => ({ ok: false, status, json: async () => { if (obj === undefined) throw new SyntaxError('x'); return obj; } });

function make(fetch) {
  const src = [constLine('FIT_POLL_MS'), constLine('FIT_POLL_TRANSPORT_RETRIES'), constLine('FIT_HEARTBEAT_LOST_SEC'),
    'const _runningFitJobs = new Set(); const _fitJobByOwner = new WeakMap();',
    extractFn('_cancelFitJob'), extractFn('_fitHttpError'), extractFn('_readFitReply'), extractFn('_serverFitJob')].join('\n');
  return new Function('fetch', 'setTimeout', 'DOMException', src + '\nreturn { _serverFitJob, _runningFitJobs };')(
    fetch, f => f(), class extends Error { constructor(m, n) { super(m); this.name = n; } });
// UNDO / REDO
// ═══════════════════════════════════════════════════
// Undo/redo history is PER TAB — it lives on the tab record (tab.undoStack /
// tab.redoStack, runtime-only, never serialised) exactly like fit history
// (tab.snapshots). Module-level stacks were the second instance of per-tab
// content being restored into whichever tab was active (the first was the
// auto-fit rollback); with the stacks on the record there is no other stack
// to restore from, so a cross-tab restore has no path — by construction,
// not by guard (docs/superpowers/plans/2026-09-08-per-tab-state-ownership.md).
const MAX_UNDO = 50;
let _undoDebounceTimer = null;

// The one accessor for per-tab runtime state. null when no tab is active.
function _activeTab() {
  return (typeof tabManager !== 'undefined' && tabManager) ? tabManager._getTab(tabManager.activeId) : null;
}
// ASYNC OWNERSHIP RULE (Codex 2026-09-09 round 1, both runs): an operation
// that awaits — a fit, an analysis, a confirmation, a file read, a timer —
// captures the RECORD OBJECT it started on (and its inputs) before the first
// await, and afterwards either writes to that object or checks that it is
// still the active one. Persisted ids are not identity: a closed tab's id
// comes back on a NEW object after a project reload.
function _opOwner() {
  const t = _activeTab();
  return (t && !t.isStack) ? t : null;
}
function _ownerLive(owner) {
  return !!owner && typeof tabManager !== 'undefined' && !!tabManager && tabManager.tabs.includes(owner);
}
function _ownerActive(owner) {
  return _ownerLive(owner) && _activeTab() === owner;
}
// The active SPECTRUM tab with its history containers ensured; null for no
// tab or a stack tab (stack tabs have no peaks and get no history).
function _historyTab() {
  const t = _activeTab();
  if (!t || t.isStack) return null;
  if (!t.undoStack) t.undoStack = [];
  if (!t.redoStack) t.redoStack = [];
  return t;
}

// Undo snapshots are deep copies of state.peaks. An action that ALSO changes
// endpoint averaging (today: applying Find Peaks suggestions, which sets the
// panel to what the engine fitted at) passes { endpointAvg } so the snapshot
// carries the pre-action value as a non-index property; undo/redo restore it
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
  // ±0.30 upper bound (284.80), adv1's floor sits exactly at graphite's
  // ceiling, which still enforces non-overlap. A relative constraint would
  // need an lmfit derived-parameter mechanism not present in the backend.
  peaks[1]._afCenterMin = 284.80;        peaks[1]._afCenterMax = 284.80 + 0.50;
  peaks[1]._afFwhmMin   = 0.80;          peaks[1]._afFwhmMax   = 3.00;
  peaks[2]._afCenterMin = 286.20 - 0.50; peaks[2]._afCenterMax = 286.20 + 0.50;
  peaks[2]._afFwhmMin   = 0.80;          peaks[2]._afFwhmMax   = 3.00;
  peaks[3]._afCenterMin = 287.80 - 0.50; peaks[3]._afCenterMax = 287.80 + 0.50;
  peaks[3]._afFwhmMin   = 0.80;          peaks[3]._afFwhmMax   = 3.50;
  peaks[4]._afCenterMin = 291.00 - 1.00; peaks[4]._afCenterMax = 291.00 + 1.00;
  peaks[4]._afFwhmMin   = 1.00;          peaks[4]._afFwhmMax   = 4.00;
  for (let i = 5; i < peaks.length; i++) {
    peaks[i]._afCenterMin = peaks[i].center - 0.80;
    peaks[i]._afCenterMax = peaks[i].center + 0.80;
    peaks[i]._afFwhmMin   = 0.50;
    peaks[i]._afFwhmMax   = 3.00;
  }
  return peaks;
}

// Capture exactly the bits of state Auto-Fit will mutate, so a failure can
// cleanly restore the tab. Returns an opaque snapshot object.
function _autoFitSnapshot() {
  return {
    // The snapshot is taken before the auto-fit's first await, so it is the
    // natural carrier of the owning record OBJECT (async ownership rule).
    owner:        _opOwner(),
    peaks:        JSON.parse(JSON.stringify(state.peaks || [])),
    fitResult:    state.fitResult ? { ...state.fitResult } : null,
    ccShift:      state.ccShift,
    // The provisional cc shift migrates manual anchors along with peak
    // centers (data-attached convention), so rollback must restore them too
    // — omitting this left anchors stranded in the provisional frame when
    // the auto-fit failed (Codex round-1 MAJOR, both runs).
    manualAnchors: JSON.parse(JSON.stringify(_getManualAnchors())),
    modelProvenance: (() => { const o = _opOwner(); return o && o.modelProvenance ? JSON.parse(JSON.stringify(o.modelProvenance)) : null; })(),
    nextId:       state.nextId,
    ccMethodDom:  document.getElementById('cc-method')?.value || 'none',
    ccObsDom:     document.getElementById('cc-obs')?.value || '',
    ccLitDom:     document.getElementById('cc-lit')?.value || '',
    roiMinDom:    document.getElementById('roi-min')?.value || '',
    roiMaxDom:    document.getElementById('roi-max')?.value || '',
    bgStartDom:   document.getElementById('bg-start')?.value || '',
    bgEndDom:     document.getElementById('bg-end')?.value || '',
  };
}

function _autoFitRestore(snap, owner) {
  // owner is the record OBJECT the auto-fit started on — normally the one
  // the snapshot itself carries (taken before the first await). Anything
  // that is not a record object (an id from an older caller, undefined) is
  // ignored in favour of the snapshot's owner. A closed tab's id comes back
  // on a NEW object after a project reload, so an id lookup would restore a
  // stale snapshot into the reopened tab (Codex 2026-09-09).
  if (!snap) return;
  if (!owner || typeof owner !== 'object') owner = snap.owner;
  if (!_ownerLive(owner)) return;
  // If the fitting tab is no longer active (the user switched tabs while
  // the auto-fit request was in flight), restore into that tab's RECORD.
  // Writing the snapshot into live state/DOM here would clobber the newly
  // active tab with the fitting tab's pre-auto-fit state while leaving
  // the fitting tab's record in the provisional cc frame (Codex round-2
  // MAJOR — a pre-existing defect for peaks/ccShift/DOM, not just the
  // newly-migrating anchors). activateTab already synced the provisional
  // live state into the record at switch-away, so overwriting the record
  // fields with the snapshot undoes exactly that.
  if (_activeTab() !== owner) {
    const t = owner;
    if (t.isStack) return;
    t.peaks = snap.peaks;
    t.fitResult = snap.fitResult;
    t.ccShift = snap.ccShift;
    t.manualAnchors = snap.manualAnchors || [];
    t.modelProvenance = snap.modelProvenance || null;
    t.nextId = snap.nextId;
    t.ui = { ...t.ui,
      ccMethod: snap.ccMethodDom, ccObs: snap.ccObsDom, ccLit: snap.ccLitDom,
      roiMin: snap.roiMinDom, roiMax: snap.roiMaxDom,
      bgStart: snap.bgStartDom, bgEnd: snap.bgEndDom };
    return;
  }
  state.peaks     = snap.peaks;
  state.fitResult = snap.fitResult;
  state.ccShift   = snap.ccShift;
  _setManualAnchors(snap.manualAnchors || []);
  { const _t = _activeTab(); if (_t) _t.modelProvenance = snap.modelProvenance || null; }
  state.nextId    = snap.nextId;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  set('cc-method', snap.ccMethodDom);
  set('cc-obs',    snap.ccObsDom);
  set('cc-lit',    snap.ccLitDom);
  // The provisional 'c1s' correction hid the custom-target field; putting the
  // method back without its field left Custom with no visible input (same
  // rule as the tab-restore path, no change event).
  { const rf = document.getElementById('cc-ref-field'), tf = document.getElementById('cc-target-field');
    if (rf) rf.style.display = (snap.ccMethodDom === 'none') ? 'none' : 'block';
"""
app.py – XPS Peak Fitting Flask application.

Gunicorn entry point:
    gunicorn "app:create_app()" -w 4 -b 0.0.0.0:5000

Development:
    python app.py          (uses FLASK_ENV / FLASK_DEBUG from environment)
    flask --app app run    (same, using Flask CLI)

Session model
-------------
Each file upload creates a UUID session.  The parsed arrays are saved as a
compressed NumPy archive at  uploads/<session_id>.npz.  Subsequent fit /
background requests reference the session by ID.  No server‑side memory state
is required, making the app compatible with multi‑worker gunicorn.

REST API
--------
POST /api/upload            Upload a data file; returns session_id + preview data
POST /api/background        Compute background for a session
POST /api/fit               Run peak fitting; returns full result
GET  /api/peak-shapes       List available lineshape names
GET  /api/elements          List built‑in spin‑orbit element presets
GET  /api/xps-reference     Validated periodic-table reference dataset (data/xps/)
GET  /api/session/<id>      Retrieve raw session data
DELETE /api/session/<id>    Delete session files
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from functools import wraps
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

import fitting
import parser as xps_parser
import vgd_parser
from xps_reference import XPSReferenceError, load_reference_cached

# Upper bound on the Monte-Carlo uncertainty resampling count accepted by
# /api/fit. Each perturbation re-runs the full composite fit, so an unbounded
# value lets a single request occupy a worker for many minutes (audit F7).
# Adjust here if more resampling is ever needed.
MAX_N_PERTURB = 100

# Session .npz files are deleted by an opportunistic sweep this many days after
# their last modification (audit F13). The sweep runs on each new session write
# — no background thread or scheduler.
SESSION_TTL_DAYS = 7

# ─────────────────────────────────────────────────────────────────────────────
# /api/fit request handling, shared by /api/fit and /api/fit/start (unit 2)
# ─────────────────────────────────────────────────────────────────────────────

def _prepare_fit_request(app, body):
    """/api/fit's request validation, shared VERBATIM with /api/fit/start
    (unit 2, 2026-09-27): every 400 / 404 is immediate and word-for-word the
    same on both routes. Returns ``(kwargs_for_run_fit, None)`` or
    ``(None, error_response)``."""
    session_id = body.get("session_id", "")
    _validate_session_id(session_id)

    try:
        energy, counts = _load_session(session_id, app.config["UPLOAD_FOLDER"])
    except KeyError:
        return None, _err(f"Session '{session_id}' not found", 404)

    # Background config
    bg_cfg = body.get("background", {})
    bg_method = bg_cfg.get("method", "shirley")
    bg_start = _parse_int(bg_cfg.get("start_idx"), 0, len(energy))
    bg_end = _parse_int(bg_cfg.get("end_idx"), 0, len(energy), default=len(energy))
    # Clean 400 for malformed endpoint_avg instead of a 500 (audit F9).
    try:
        endpoint_avg = max(1, int(bg_cfg.get("endpoint_avg", 1)))
"""Make the repo root importable regardless of how pytest is invoked."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

exec
/bin/zsh -lc 'node --test tests/js/fit_start_poll.test.js tests/js/fit_acceptance.test.js tests/js/stale_statistics.test.js tests/js/per_tab_state.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 354ms:
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 1 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 8.399076
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 2 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 5.038909
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 3 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 3.113359
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 4 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 9.978011
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 5 - a converged backend result is applied (sanity)
  ---
  duration_ms: 3.781139
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 6 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.734298
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 7 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 3.030103
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 8 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 3.449962
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 9 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 1.813835
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 10 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 0.926786
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 11 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 0.710341
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 12 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 1.559884
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 13 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 3.471991
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 14 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 4.605337
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 15 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 1.611694
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 16 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 7.661452
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 17 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.307667
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 18 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 3.654276
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 19 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.867651
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 20 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.525102
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 21 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 3.689674
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 22 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 1.567305
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 23 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.528965
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 24 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 4.416361
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 25 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.301516
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 26 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 3.448729
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 27 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.41137
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 28 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 3.622459
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 29 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.758208
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 30 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 3.69041
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 31 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.616633
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 32 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 2.973988
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 33 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.429981
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 34 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.250538
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 35 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 4.476815
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 36 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 4.813638
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 37 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 5.232966
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 38 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 2.972309
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 39 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 3.764219
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 40 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 4.525601
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 41 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 3.446585
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 42 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 3.377459
  type: 'test'
  ...
# Subtest: a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
ok 43 - a transport failure after the model was edited mid-fit runs NO local fit (it would stamp the edited key on the old arrays)
  ---
  duration_ms: 7.81268
  type: 'test'
  ...
# Subtest: a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
ok 44 - a 200 reply containing NaN is a FAILED fit with a message: nothing applied, no local fallback
  ---
  duration_ms: 3.759534
  type: 'test'
  ...
# Subtest: a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
ok 45 - a 200 reply that is not JSON at all is a failed fit too; a body that cannot be READ is still a transport failure
  ---
  duration_ms: 7.801169
  type: 'test'
  ...
# Subtest: the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
ok 46 - the non-finite diagnosis looks at TOKENS: "NaN" inside a string is a malformed reply, not a non-finite number (Codex round 1)
  ---
  duration_ms: 0.85832
  type: 'test'
  ...
# Subtest: the token scan is linear and keeps a truncated string a string (Codex round 2)
ok 47 - the token scan is linear and keeps a truncated string a string (Codex round 2)
  ---
  duration_ms: 4.081264
  type: 'test'
  ...
# Subtest: a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
ok 48 - a minus sign counts only after a boundary: "x-Infinity" is malformed, "-Infinity" a token (Codex round 3)
  ---
  duration_ms: 0.900892
  type: 'test'
  ...
# Subtest: start -> running polls -> done: the result is the /api/fit body; no job is left registered
ok 49 - start -> running polls -> done: the result is the /api/fit body; no job is left registered
  ---
  duration_ms: 10.096902
  type: 'test'
  ...
# Subtest: a bad request: the synchronous route's message and status, immediately; no poll
ok 50 - a bad request: the synchronous route's message and status, immediately; no poll
  ---
  duration_ms: 3.490256
  type: 'test'
  ...
# Subtest: a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
ok 51 - a START that cannot reach the server is a transport failure (the caller may fall back to the local engine)
  ---
  duration_ms: 3.304165
  type: 'test'
  ...
# Subtest: an error record is a failed fit with the synchronous message and status
ok 52 - an error record is a failed fit with the synchronous message and status
  ---
  duration_ms: 3.302145
  type: 'test'
  ...
# Subtest: a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
ok 53 - a done record carrying NaN is F2's failed fit (unreadable reply), not a transport failure
  ---
  duration_ms: 3.408066
  type: 'test'
  ...
# Subtest: one lost poll is retried; five in a row are a transport failure and cancel the job
ok 54 - one lost poll is retried; five in a row are a transport failure and cancel the job
  ---
  duration_ms: 6.787384
  type: 'test'
  ...
# Subtest: a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
ok 55 - a stopped heartbeat (restarted worker) is a failed fit, never an endless spinner
  ---
  duration_ms: 2.30978
  type: 'test'
  ...
# Subtest: a job cancelled on the server (abandoned) is reported, not waited for
ok 56 - a job cancelled on the server (abandoned) is reported, not waited for
  ---
  duration_ms: 2.635852
  type: 'test'
  ...
# Subtest: ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
ok 57 - ownership inside the loop: a switched tab or an edited model cancels the job and returns the reason
  ---
  duration_ms: 5.388446
  type: 'test'
  ...
# Subtest: the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
ok 58 - the Auto-Fit abort (2 minutes) cancels the job and surfaces as an AbortError
  ---
  duration_ms: 3.491735
  type: 'test'
  ...
# Subtest: Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
ok 59 - Run Fit and Auto-Fit both go through _serverFitJob; nothing on the page posts to the synchronous /api/fit any more
  ---
  duration_ms: 2.458585
  type: 'test'
  ...
# Subtest: a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)
ok 60 - a new start for the same tab SUPERSEDES the previous job: cancelled on the server, its loop returns quietly (Codex round 1)
  ---
  duration_ms: 14.154512
  type: 'test'
  ...
# Subtest: both callers pass their tab as the owner and do nothing at all when superseded
ok 61 - both callers pass their tab as the owner and do nothing at all when superseded
  ---
  duration_ms: 0.97429
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 62 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 195.07217
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 63 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 81.775974
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 64 - the known class-C holders are gone from module scope
  ---
  duration_ms: 5.853517
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 65 - async operations capture their owning record before the first await
  ---
  duration_ms: 2.328384
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 66 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.563033
  type: 'test'
  ...
# Subtest: one accessor classifies a result against a key: none / unverified / current / stale
ok 67 - one accessor classifies a result against a key: none / unverified / current / stale
  ---
  duration_ms: 12.482604
  type: 'test'
  ...
# Subtest: the key is the step (b) key: F1 adds no second binding mechanism and no new key field
ok 68 - the key is the step (b) key: F1 adds no second binding mechanism and no new key field
  ---
  duration_ms: 3.250505
  type: 'test'
  ...
# Subtest: Results panel, current: statistic, RMSE, R and sigma are shown
ok 69 - Results panel, current: statistic, RMSE, R and sigma are shown
  ---
  duration_ms: 8.875719
  type: 'test'
  ...
# Subtest: Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
ok 70 - Results panel, stale: a banner says the statistics belong to the previous model; no chi-square, RMSE, R or sigma
  ---
  duration_ms: 7.79555
  type: 'test'
  ...
# Subtest: Results panel, unverified (older save, no key): values shown with a plain note
ok 71 - Results panel, unverified (older save, no key): values shown with a plain note
  ---
  duration_ms: 9.196519
  type: 'test'
  ...
# Subtest: status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
ok 72 - status-bar R: the previous model's R is not shown on a stale result; an unrelated rFactor argument is untouched
  ---
  duration_ms: 9.066183
  type: 'test'
  ...
# Subtest: the stored fitted curve is never drawn, saved or stacked as the fit once stale
ok 73 - the stored fitted curve is never drawn, saved or stacked as the fit once stale
  ---
  duration_ms: 3.129054
  type: 'test'
  ...
# Subtest: saves keep the key and say plainly when the statistics are stale or unverified
ok 74 - saves keep the key and say plainly when the statistics are stale or unverified
  ---
  duration_ms: 2.454263
  type: 'test'
  ...
# Subtest: CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
ok 75 - CSV: current writes the statistic and sigma; stale writes a WARNING, no statistic, no sigma
  ---
  duration_ms: 18.323057
  type: 'test'
  ...
# Subtest: XLSX: stale writes a WARNING row instead of the statistic, and no sigma
ok 76 - XLSX: stale writes a WARNING row instead of the statistic, and no sigma
  ---
  duration_ms: 5.452517
  type: 'test'
  ...
# Subtest: TSV: stale says the Model / Residual columns are the current, unfitted model
ok 77 - TSV: stale says the Model / Residual columns are the current, unfitted model
  ---
  duration_ms: 9.80656
  type: 'test'
  ...
# Subtest: the refresh re-renders Results only when its rendered state differs
ok 78 - the refresh re-renders Results only when its rendered state differs
  ---
  duration_ms: 4.575997
  type: 'test'
  ...
# Subtest: an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
ok 79 - an equivalent spelling of a form number ("280" / "280.0") is the same fit; a different value is not
  ---
  duration_ms: 4.176898
  type: 'test'
  ...
# Subtest: Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
ok 80 - Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone
  ---
  duration_ms: 3.450964
  type: 'test'
  ...
# Subtest: Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
ok 81 - Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies
  ---
  duration_ms: 11.420566
  type: 'test'
  ...
# Subtest: closing the last tab clears the Results panel, header and status statistics too
ok 82 - closing the last tab clears the Results panel, header and status statistics too
  ---
  duration_ms: 0.37317
  type: 'test'
  ...
# Subtest: reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
ok 83 - reload never installs an edited-model curve or R under the original key, and activation never computes R over an edited model
  ---
  duration_ms: 1.912313
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
ok 84 - F2: Auto-Fit on a 200 reply containing NaN fails closed with the reply message, and rolls back
  ---
  duration_ms: 4.869397
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
ok 85 - F2: Auto-Fit on a Cloudflare 524 (plain-text body) is a failed request with its status, never "could not be read"
  ---
  duration_ms: 4.645007
  type: 'test'
  ...
# Subtest: F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
ok 86 - F2: Auto-Fit on a 500 with a JSON error is a failed request with its status, never "could not be read"
  ---
  duration_ms: 3.304427
  type: 'test'
  ...
1..86
# tests 86
# suites 0
# pass 86
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 399.636006

exec
/bin/zsh -lc "node -e '
const fs = require('\\''fs'\\'');
const lines = fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'').split('\\''\\n'\\'');
function fn(name) { const s=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l)); let d=0,seen=false;for(let i=s;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\''){d++;seen=true;}if(c==='\\''}'\\'')d--;}if(seen&&d===0)return lines.slice(s,i+1).join('\\''\\n'\\'');}throw name; }
const src = ['\\''const FIT_POLL_MS=500,FIT_POLL_TRANSPORT_RETRIES=5,FIT_HEARTBEAT_LOST_SEC=30; const _runningFitJobs=new Set(),_fitJobByOwner=new WeakMap();'\\'',...['\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\''].map(fn)].join('\\''\\n'\\'');
const ok=x=>({ok:true,status:200,text:async()=>JSON.stringify(x)});
const gate=()=>{let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};};
const flush=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
function env(fetch){const waits=[];const run=new Function('\\''fetch'\\'','\\''setTimeout'\\'',src+'\\'';return _serverFitJob;'\\'')(fetch,f=>waits.push(f));return {run,waits};}
(async()=>{
let starts=0;const firstStart=gate(), cancels=[];
const e=env(async u=>u==='\\''/api/fit/start'\\''?(++starts===1?firstStart.promise:ok({job_id:'\\''NEW'\\''})):u.includes('\\''/cancel/'\\'')?(cancels.push(u),ok({})):ok({status:'\\''done'\\'',result:{winner:'\\''OLD'\\''}}));
const owner={};const old=e.run({}, {owner});const newer=e.run({}, {owner});await flush();
firstStart.resolve(ok({job_id:'\\''OLD'\\''}));await flush();e.waits.splice(0).forEach(f=>f());
console.log('\\''Out-of-order start replies:'\\'',JSON.stringify({old:await old,newer:await newer,cancels}));
for(const status of ['\\''done'\\'','\\''cancelled'\\'']){
let starts=0;const oldPoll=gate(), cancels=[];
const e=env(async u=>u==='\\''/api/fit/start'\\''?ok({job_id:++starts===1?'\\''OLD'\\'':'\\''NEW'\\''}):u.endsWith('\\''/OLD'\\'')&&u.includes('\\''/progress/'\\'')?oldPoll.promise:u.includes('\\''/cancel/'\\'')?(cancels.push(u),ok({})):ok({status:'\\''done'\\'',result:{winner:'\\''NEW'\\''}}));
const owner={};const old=e.run({}, {owner});await flush();e.waits.shift()();await flush();const newer=e.run({}, {owner});await flush();
oldPoll.resolve(ok({status,result:{winner:'\\''OLD'\\''}}));
const outcome=await old.then(x=>({returned:x}),e=>({error:e.message}));e.waits.splice(0).forEach(f=>f());
console.log('\\''Superseded in-flight poll '\\''+status+'\\'':'\\'',JSON.stringify({outcome,newer:await newer,cancels}));
}
})();'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
Out-of-order start replies: {"old":{"winner":"OLD"},"newer":{"_abandoned":"superseded"},"cancels":["/api/fit/cancel/NEW"]}
Superseded in-flight poll done: {"outcome":{"returned":{"winner":"OLD"}},"newer":{"winner":"NEW"},"cancels":["/api/fit/cancel/OLD"]}
Superseded in-flight poll cancelled: {"outcome":{"error":"The fit was stopped on the server before it finished. Run it again."},"newer":{"winner":"NEW"},"cancels":["/api/fit/cancel/OLD"]}

exec
/bin/zsh -lc "sed -n '350,415p' tests/js/stale_statistics.test.js; nl -ba templates/index.html | sed -n '7485,7571p'; nl -ba app.py | sed -n '675,720p'; sed -n '1775,1900p' fitting.py; ls /Users/skyefortier/xps-app/venv/bin/python*" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
    ['shirleyIter', '5', '5.0', true],       // parseInt: 5 either way
    ['shirleyIter', '5', '5.9', true],       // parseInt reads 5 — the same fit
    ['endpointAvg', '3', '03', true],
    ['roiMin', '280', '2.8e2', true],        // parseFloat reads 280 either way
    ['roiMin', '280', '280abc', true],       // parseFloat reads 280 (what getROIData selects)
    ['bgStart', '295', '295.5', false],
  ]) {
    const fk = k._startsModelKey(peaks, { ...ui, [field]: fitted }, 0, []);
    const lk = k._startsModelKey(peaks, { ...ui, [field]: typed }, 0, []);
    const pf = /Iter|Avg/.test(field) ? parseInt : parseFloat;
    assert.strictEqual(pf(fitted) === pf(typed), same, 'fixture: the reader agrees with the expectation');
    assert.strictEqual(k._sameFitKey(fk, lk), same, `${field} ${fitted} vs ${typed}`);
  }
  assert.ok(!k._sameFitKey(null, null) && !k._sameFitKey(a, null), 'no key never matches');
  assert.ok(!k._sameFitKey('not json', 'not json ') && k._sameFitKey('not json', 'not json'));
});

test('Clear All (result -> none) re-renders Results back to its empty state; a page that never had a result is left alone', () => {
  const src = [...STATE_CONSTS.map(constLine), ...['_fitKeyCanon', '_sameFitKey', ...STATE_FNS].map(extractFn), extractFn('_refreshStatsState')].join('\n');
  const doc = makeDoc();
  const env = { renders: 0 };
  const state = { fitResult: null };
  const refresh = new Function('document', 'state', 'env', `
    const _startsLiveKey = () => 'K', _startsRecordKey = t => t.key;
    const renderResults = () => { env.renders++; document.getElementById('results-area').setAttribute('data-stats-state', _statsLiveState()); };
    const _applyStatDisplay = () => {}, _updateRFactorUI = () => {};
    ${src}
    return _refreshStatsState;`)(doc, state, env);
  refresh();
  assert.strictEqual(env.renders, 0, 'fresh page: nothing rendered yet, nothing to clear');
  doc.els['results-area'].setAttribute('data-stats-state', 'current');   // a fit was shown
  refresh();
  assert.strictEqual(env.renders, 1, 'the shown result was cleared: back to the empty state');
  refresh();
  assert.strictEqual(env.renders, 1);
});

test('Auto-Fit discards (and rolls back) a response when the model or context was edited while it ran; an unedited run applies', async () => {
  const constants = lines.slice(lines.findIndex(l => l.startsWith('const _STARTS_MODEL_FIELDS')), lines.findIndex(l => l.startsWith('const _STARTS_UI_FIELDS')) + 1).join('\n');
  const run = async (editDuringUpload) => {
    const state = { peaks: [], ccShift: 0, rawBE: [285, 284.5, 284], rawIntensity: [10, 20, 10] };
    const dom = {};
    const document = { getElementById: id => (dom[id] ??= { value: ({ 'bg-type': 'none', 'bg-start': '285', 'bg-end': '284', 'bg-endpoint-avg': '3', 'fit-method': 'leastsq' })[id] || '', style: {}, textContent: '', setAttribute() {}, classList: { add() {}, remove() {} } }), querySelector: () => ({}) };
    const tab = { id: 1 };
    const out = { restored: false, applied: 0, notes: [] };
    const tabManager = { activeId: 1, _getTab: () => tab, _captureUI: () => ({ bgType: document.getElementById('bg-type').value, roiMin: '284', roiMax: '285' }), _syncActiveToRecord() {} };
    const deps = { state, document, tabManager, notify: (m, k) => out.notes.push([m, k]), _opOwner: () => tab, _ownerActive: () => true, isC1sTab: () => true,
      _autoFitSnapshot: () => ({}), _autoFitRestore: () => { out.restored = true; }, _showAutoFitConfirmModal: async () => true,
      getROIData: () => ({ be: state.rawBE, inten: state.rawIntensity }), computeBackground: be => be.map(() => 0),
      findGraphiteRawBE: () => 284.5, assessLowBERegion: () => ({}), pushUndo() {}, updateChargeCorrection() {},
      buildAutoFitModel: () => [{ id: 1, name: 'Graphite', shape: 'Gaussian', center: 284.5, fwhm: 1, amplitude: 20 }],
      renderPeakList() {}, _showFitSpinner() {}, _hideFitSpinner() {}, AbortController, setTimeout: () => 1, clearTimeout() {},
      peakToBackendSpec: p => ({ ...p }), _getManualAnchors: () => [],
      uploadToBackend: async () => { if (editDuringUpload) document.getElementById('bg-type').value = 'linear'; return 'sid'; },
      fetch: async () => ({ text: async () => JSON.stringify({ success: true, statistics: { reduced_chi_square: 1 }, fitted_y: [10, 20, 10], residuals: [0, 0, 0] }) }),
      applyBackendResult: () => { out.applied++; }, applyAutoFitResult: () => true };
    const src = constants + '\n' + ['runAutoFitC1sGraphite', '_readFitReply', '_bgWindowIndices', '_arrMin', '_arrMax', '_startsModelKey', '_startsLiveKey', '_fitKeyCanon', '_sameFitKey'].map(extractFn).join('\n');
    await new Function(...Object.keys(pollify(deps)), src + '\n' + POLL_SRC + '\nreturn runAutoFitC1sGraphite;')(...Object.values(deps))();
    return out;
  };
  const edited = await run(true);
  assert.strictEqual(edited.applied, 0, 'nothing applied over the edited model');
  assert.strictEqual(edited.restored, true, 'rolled back');
  assert.ok(edited.notes.some(([m, k]) => k === 'amber' && /edited while it was running/.test(m)), JSON.stringify(edited.notes));
  const clean = await run(false);
  assert.strictEqual(clean.applied, 1, 'an unedited run is applied as before');
  7485	  });
  7486	}
  7487	function _fitHttpError(status, msg, prefix) {
  7488	  const err = new Error(msg || ((prefix || 'Fit request failed') + ' (HTTP ' + status + ').'));
  7489	  err.serverError = true;
  7490	  err.httpStatus = status;
  7491	  return err;
  7492	}
  7493	async function _serverFitJob(fitReq, guard) {
  7494	  guard = guard || {};
  7495	  const isTransport = e => e && !e.serverError && (e instanceof TypeError || e.name === 'AbortError');
  7496	  let resp;
  7497	  try {
  7498	    resp = await fetch('/api/fit/start', { method: 'POST', headers: { 'Content-Type': 'application/json' },
  7499	                                           body: JSON.stringify(fitReq), signal: guard.signal });
  7500	  } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
  7501	  if (resp.ok === false) {
  7502	    let msg = null;
  7503	    try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
  7504	    throw _fitHttpError(resp.status, msg);
  7505	  }
  7506	  let started;
  7507	  try { started = await _readFitReply(resp); } catch (e) { if (isTransport(e)) e.transportFailure = true; throw e; }
  7508	  const jobId = started && started.job_id;
  7509	  if (!jobId) throw _fitHttpError(resp.status, 'The server did not start the fit (no job id).');
  7510	  _runningFitJobs.add(jobId);
  7511	  if (guard.owner) {
  7512	    const prev = _fitJobByOwner.get(guard.owner);
  7513	    if (prev && prev !== jobId) _cancelFitJob(prev);
  7514	    _fitJobByOwner.set(guard.owner, jobId);
  7515	  }
  7516	  let misses = 0;
  7517	  try {
  7518	    while (true) {
  7519	      await new Promise(r => setTimeout(r, FIT_POLL_MS));
  7520	      if (guard.signal && guard.signal.aborted) {
  7521	        _cancelFitJob(jobId);
  7522	        throw guard.signal.reason || new DOMException('aborted', 'AbortError');
  7523	      }
  7524	      if (guard.owner && _fitJobByOwner.get(guard.owner) !== jobId) return { _abandoned: 'superseded' };   // its successor cancelled it
  7525	      const why = guard.abandoned ? guard.abandoned() : null;
  7526	      if (why) { _cancelFitJob(jobId); return { _abandoned: why }; }
  7527	      let pr, rec;
  7528	      try {
  7529	        pr = await fetch('/api/fit/progress/' + encodeURIComponent(jobId), { signal: guard.signal });
  7530	      } catch (e) {
  7531	        if (e && e.name === 'AbortError') { _cancelFitJob(jobId); throw e; }
  7532	        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
  7533	          _cancelFitJob(jobId);
  7534	          const err = new Error('Lost contact with the server during the fit (' + ((e && e.message) || 'network error') + ').');
  7535	          err.transportFailure = true;
  7536	          throw err;
  7537	        }
  7538	        continue;
  7539	      }
  7540	      if (pr.ok === false) {
  7541	        _cancelFitJob(jobId);
  7542	        let msg = null;
  7543	        try { const j = await pr.json(); msg = (j && j.error) || null; } catch (_) { /* non-JSON body */ }
  7544	        throw _fitHttpError(pr.status, msg, 'Lost the fit\'s progress');
  7545	      }
  7546	      try { rec = await _readFitReply(pr); } catch (e) {
  7547	        if (e && e.unreadableReply) { _cancelFitJob(jobId); throw e; }
  7548	        if (++misses >= FIT_POLL_TRANSPORT_RETRIES) {
  7549	          _cancelFitJob(jobId);
  7550	          if (isTransport(e)) e.transportFailure = true;
  7551	          throw e;
  7552	        }
  7553	        continue;
  7554	      }
  7555	      misses = 0;
  7556	      if (rec.status === 'done') return rec.result;
  7557	      if (rec.status === 'error') throw _fitHttpError(rec.http_status || 500, rec.error);
  7558	      if (rec.status === 'cancelled') throw _fitHttpError(409, 'The fit was stopped on the server before it finished. Run it again.');
  7559	      if (Number.isFinite(rec.heartbeat_age_sec) && rec.heartbeat_age_sec > FIT_HEARTBEAT_LOST_SEC) {
  7560	        _cancelFitJob(jobId);
  7561	        throw _fitHttpError(503, 'The server stopped working on the fit (no sign of it for ' + Math.round(rec.heartbeat_age_sec) +
  7562	                                 ' s — it was probably restarted). Run the fit again.');
  7563	      }
  7564	      if (typeof guard.onProgress === 'function') guard.onProgress(rec);
  7565	    }
  7566	  } finally {
  7567	    _runningFitJobs.delete(jobId);
  7568	    if (guard.owner && _fitJobByOwner.get(guard.owner) === jobId) _fitJobByOwner.delete(guard.owner);
  7569	  }
  7570	}
  7571	
   675	        try:
   676	            # queued until a run slot is free; a job cancelled or abandoned
   677	            # while queued never runs
   678	            got = False
   679	            while not got:
   680	                if cancelled():
   681	                    status, body = None, None
   682	                    break
   683	                got = _FIT_JOB_RUN_SLOTS.acquire(timeout=0.5)
   684	            if got:
   685	                try:
   686	                    with lock:
   687	                        rec["status"] = "running"
   688	                        rec["heartbeat"] = time.time()
   689	                        _fit_job_write(job_id, upload_folder, rec)   # visible at once, not at the next heartbeat
   690	                    status, body = run(fit_args, cancelled)
   691	                finally:
   692	                    _FIT_JOB_RUN_SLOTS.release()
   693	        except Exception as exc:                       # the record must always leave "running"
   694	            logging.getLogger(__name__).exception("fit job %s crashed", job_id)
   695	            status, body = 500, {"error": "Internal fitting error — see server log."}
   696	        finally:
   697	            _fit_job_release()
   698	        with lock:
   699	            rec["elapsed_sec"] = round(time.time() - started, 1)
   700	            rec["heartbeat"] = time.time()
   701	            if status is None or cancel_path.exists():
   702	                rec.update(status="cancelled")
   703	            elif status == 200:
   704	                rec.update(status="done", result=body)
   705	            else:
   706	                rec.update(status="error", error=body.get("error"), http_status=status)
   707	            finished.set()
   708	            _fit_job_write(job_id, upload_folder, rec)
   709	        for kind in ("cancel", "polled"):
   710	            try:
   711	                _fit_job_marker(job_id, upload_folder, kind).unlink(missing_ok=True)
   712	            except OSError:
   713	                pass
   714	
   715	    threading.Thread(target=worker, daemon=True, name=f"fit-{job_id[:8]}").start()
   716	    threading.Thread(target=heartbeat, daemon=True, name=f"fit-hb-{job_id[:8]}").start()
   717	
   718	
   719	def _require_json(f):
   720	    """Decorator: return 400 if request body is not valid JSON."""
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
        return model.fit(y_sub, params, x=x, weights=weights, **seeded(kws), **_cancel_kw())

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
/Users/skyefortier/xps-app/venv/bin/python
/Users/skyefortier/xps-app/venv/bin/python3
/Users/skyefortier/xps-app/venv/bin/python3.12

codex
I reproduced two ownership races despite all 86 targeted JavaScript tests passing: delayed start replies let an older invocation cancel the newer one, and an in-flight poll can return a stale result—or raise a cancellation error—after being superseded. The latter can reach Auto-Fit’s rollback handler. I’ll finish checking the server cleanup and cancellation paths before issuing the verdict.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -q -p no:cacheprovider tests/test_fit_start_poll.py -k cancel_observed_mid_fit' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 exited 1 in 245ms:
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
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll']

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -q -s -p no:cacheprovider tests/test_fit_start_poll.py -k cancel_observed_mid_fit' in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 exited 2 in 1807ms:

==================================== ERRORS ====================================
________________ ERROR collecting tests/test_fit_start_poll.py _________________
tests/test_fit_start_poll.py:20: in <module>
    import app as app_module
app.py:45: in <module>
    import fitting
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
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll']
=========================== short test summary info ============================
ERROR tests/test_fit_start_poll.py - FileNotFoundError: [Errno 2] No usable t...
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 1.54s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c '
import ast, pathlib, threading, types, time, logging, uuid
tree=ast.parse(pathlib.Path(\"app.py\").read_text())
wanted={\"_fit_job_admit\",\"_fit_job_release\",\"_fit_job_start\",\"fit_start\"}
nodes=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name in wanted]
for n in nodes: n.decorator_list=[]
ns=dict(time=time,logging=logging,uuid=uuid,FIT_JOB_MAX_RUNNING=1,FIT_JOB_MAX_ADMITTED=6,FIT_JOB_HEARTBEAT_SEC=2,FIT_JOB_ABANDON_SEC=180,
_FIT_JOB_RUN_SLOTS=threading.BoundedSemaphore(1),_FIT_JOB_ADMITTED=[0],_FIT_JOB_ADMIT_LOCK=threading.Lock())
pending=[]
class Thread:
    def __init__(self,target,daemon,name): self.target,self.name=target,name
    def start(self):
        if self.name.startswith(\"fit-hb-\"): raise RuntimeError(\"can'\\''t start new thread\")
        pending.append(self.target)
class Marker:
    def touch(self): pass
    def exists(self): return False
    def stat(self): return types.SimpleNamespace(st_mtime=time.time())
    def unlink(self,**kw): pass
ns.update(threading=types.SimpleNamespace(Lock=threading.Lock,Event=threading.Event,Thread=Thread),
_fit_job_write=lambda *a:None,_fit_job_marker=lambda *a:Marker(),
app=types.SimpleNamespace(config={\"UPLOAD_FOLDER\":\"/unused\"}),
request=types.SimpleNamespace(get_json=lambda **kw:{}),
_prepare_fit_request=lambda *a:({},None),_sweep_expired_jobs=lambda *a:None,_sweep_fit_job_markers=lambda *a:None,
_run_fit_outcome=lambda *a,**kw:(200,{}),jsonify=lambda x:x)
exec(compile(ast.Module(body=nodes,type_ignores=[]),\"<actual app functions>\",\"exec\"),ns)
try: ns[\"fit_start\"]()
except RuntimeError as e: print(\"heartbeat startup failure:\",e)
print(\"after route error: admitted\",ns[\"_FIT_JOB_ADMITTED\"][0],\"worker threads started\",len(pending))
assert ns[\"_fit_job_admit\"]() # a second job, still active when first finishes
pending.pop()()
print(\"after first worker finishes: admitted\",ns[\"_FIT_JOB_ADMITTED\"][0],\"but second job still active\")
accepted=sum(ns[\"_fit_job_admit\"]() for _ in range(6))
print(\"additional admissions\",accepted,\"actual outstanding jobs\",1+accepted,\"configured cap\",ns[\"FIT_JOB_MAX_ADMITTED\"])
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
heartbeat startup failure: can't start new thread
after route error: admitted 0 worker threads started 1
after first worker finishes: admitted 0 but second job still active
additional admissions 6 actual outstanding jobs 7 configured cap 6

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c 'import tempfile,sys; tempfile.tempdir='\\''/tmp'\\''; sys.modules['\\''matplotlib'\\'']=None; import pytest; raise SystemExit(pytest.main(['\\''-q'\\'','\\''-s'\\'','\\''-p'\\'','\\''no:cacheprovider'\\'','\\''tests/test_fit_start_poll.py'\\'','\\''-k'\\'','\\''cancel_observed_mid_fit'\\'']))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 1998ms:
...
3 passed, 15 deselected in 1.65s

exec
/bin/zsh -lc "node -e '
const fs=require('\\''fs'\\''), lines=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'').split('\\''\\n'\\'');
function fn(name){const s=lines.findIndex(l=>new RegExp('\\''"'^(async )?function '"'\\''+name+'\\''\\\\('\\'').test(l));let d=0;for(let i=s;i<lines.length;i++){for(const c of lines[i]){if(c==='\\''{'\\'')d++;else if(c==='\\''}'\\'')d--;}if(d===0)return lines.slice(s,i+1).join('\\''\\n'\\'');}}
let resolveOld; const oldPoll=new Promise(r=>resolveOld=r);
const tick=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
const tab={},state={peaks:[],ccShift:0,rawBE:[285,284.5,284],rawIntensity:[10,20,10]}, dom={},waits=[],out={restores:0,hides:0,notes:[],cancels:[]};
const document={getElementById:id=>(dom[id]??={value:({'\\''bg-type'\\'':'\\''none'\\'','\\''bg-start'\\'':'\\''285'\\'','\\''bg-end'\\'':'\\''284'\\'','\\''bg-endpoint-avg'\\'':'\\''3'\\'','\\''fit-method'\\'':'\\''leastsq'\\''})[id]||'\\'''\\'',textContent:'\\'''\\''}),querySelector:()=>({})};
let starts=0;const ok=x=>({ok:true,status:200,text:async()=>JSON.stringify(x)});
const noop=()=>{};
const deps={state,document,tabManager:{activeId:1,_getTab:()=>tab},notify:(m,k)=>out.notes.push([m,k]),_opOwner:()=>tab,_ownerActive:()=>true,isC1sTab:()=>true,
_autoFitSnapshot:()=>({peaks:JSON.parse(JSON.stringify(state.peaks)),ccShift:state.ccShift}),_autoFitRestore:s=>{out.restores++;state.peaks=s.peaks;state.ccShift=s.ccShift;},_showAutoFitConfirmModal:async()=>true,
getROIData:()=>({be:state.rawBE,inten:state.rawIntensity}),computeBackground:be=>be.map(()=>0),findGraphiteRawBE:()=>284.5,assessLowBERegion:()=>({}),pushUndo:noop,updateChargeCorrection:noop,
buildAutoFitModel:()=>[{id:1,name:'\\''Graphite'\\'',center:284.5,amplitude:20,fwhm:1}],renderPeakList:noop,_showFitSpinner:noop,_hideFitSpinner:()=>out.hides++,
AbortController,setTimeout:(f,ms)=>{if(ms<60000)waits.push(f);return 1;},clearTimeout:noop,peakToBackendSpec:p=>({...p}),_getManualAnchors:()=>[],uploadToBackend:async()=>'\\''sid'\\'',
fetch:async u=>u==='\\''/api/fit/start'\\''?ok({job_id:++starts===1?'\\''AUTO'\\'':'\\''RUN'\\''}):u.includes('\\''/cancel/'\\'')?(out.cancels.push(u),ok({})):u.endsWith('\\''/AUTO'\\'')?oldPoll:ok({status:'\\''running'\\'',heartbeat_age_sec:0}),
_startsLiveKey:()=>JSON.stringify(state.peaks),_sameFitKey:(a,b)=>a===b,_startsUnlinkedCount:()=>0,console};
const src='\\''const FIT_POLL_MS=500,FIT_POLL_TRANSPORT_RETRIES=5,FIT_HEARTBEAT_LOST_SEC=30,_STARTS_N=3;const _runningFitJobs=new Set(),_fitJobByOwner=new WeakMap();\\n'\\''+['\\''_cancelFitJob'\\'','\\''_fitHttpError'\\'','\\''_readFitReply'\\'','\\''_serverFitJob'\\'','\\''runFit'\\'','\\''runAutoFitC1sGraphite'\\'','\\''_bgWindowIndices'\\'','\\''_arrMin'\\'','\\''_arrMax'\\''].map(fn).join('\\''\\n'\\'');
const api=new Function(...Object.keys(deps),src+'\\'';return {runFit,runAutoFitC1sGraphite};'\\'')(...Object.values(deps));
(async()=>{
const old=api.runAutoFitC1sGraphite();await tick();waits.shift()();await tick();
const newer=api.runFit();await tick();resolveOld(ok({status:'\\''cancelled'\\''}));await old;waits.splice(0).forEach(f=>f());await newer;
console.log(JSON.stringify({state,out}));
})();
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
{"state":{"peaks":[],"ccShift":0,"rawBE":[285,284.5,284],"rawIntensity":[10,20,10],"fitResult":null,"nextId":2},"out":{"restores":1,"hides":2,"notes":[["Auto-fit failed: The fit was stopped on the server before it finished. Run it again.","red"],["Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.","amber"]],"cancels":["/api/fit/cancel/AUTO","/api/fit/cancel/RUN"]}}

codex
The caller-level probe confirms the rollback failure: a superseded Auto-Fit restores its old snapshot, then the replacement Run Fit cancels itself because the model changed. I also reproduced a double admission release when the fit thread starts but heartbeat-thread startup fails. The three numerical cancellation tests pass; I’m wrapping up with these findings.
exec
/bin/zsh -lc "git status --short; nl -ba app.py | sed -n '1273,1288p'; nl -ba templates/index.html | sed -n '7746,7756p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-90XAE1es' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-CDDtvbwm' (errno=Operation not permitted)
?? docs/autofit/codex/fit_start_poll_r2_verdict_runA.md
?? docs/autofit/codex/fit_start_poll_r2_verdict_runB.md
  1273	        if error is not None:
  1274	            return error
  1275	        upload_folder = app.config["UPLOAD_FOLDER"]
  1276	        if not _fit_job_admit():
  1277	            return _err("The server is busy with other fits. Try again in a moment.", 503)
  1278	        job_id = str(uuid.uuid4())
  1279	        try:
  1280	            _sweep_expired_jobs(upload_folder)
  1281	            _sweep_fit_job_markers(upload_folder)
  1282	            _fit_job_start(job_id, upload_folder, fit_args,
  1283	                           lambda args, cancel: _run_fit_outcome(app, args, cancel=cancel))
  1284	        except Exception:
  1285	            _fit_job_release()          # the job never started: its admission is returned
  1286	            raise
  1287	        return jsonify({"job_id": job_id}), 202
  1288	
  7746	    _hideFitSpinner();
  7747	    notify('Auto-fit complete. χ²ᵣ = ' + (state.fitResult?.chiReduced?.toFixed(3) || '?'), 'green');
  7748	  } catch (e) {
  7749	    clearTimeout(timer);
  7750	    _hideFitSpinner();
  7751	    // The catch path can also fire after a mid-flight tab switch (fetch
  7752	    // error/timeout after the user moved on) — same wrong-tab hazard as
  7753	    // the explicit discard branch, so it gets the same tab-aware restore.
  7754	    _autoFitRestore(snap, fittingTab);
  7755	    let msg;
  7756	    if (e && (e.name === 'AbortError' || (e.message && e.message.toLowerCase().includes('aborted')))) {

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c '
import tempfile,sys
tempfile.tempdir=\"/tmp\"
sys.modules[\"matplotlib\"]=None
import fitting
old=fitting._run_fit_impl
error=ValueError(\"unrelated validation error\")
def bad(*a,**kw): raise error
fitting._run_fit_impl=bad
try:
    fitting.run_fit(cancel=lambda: True)
except ValueError as exc:
    assert exc is error
else: raise AssertionError(\"error swallowed\")
assert fitting._cancel_kw()=={}
def observed(*a,**kw):
    fitting._cancel_kw()[\"iter_cb\"](None,0,None)
    raise RuntimeError(\"solver abort\")
fitting._run_fit_impl=observed
try:
    fitting.run_fit(cancel=lambda: True)
except fitting.FitCancelled: pass
else: raise AssertionError(\"not normalized\")
assert fitting._cancel_kw()=={}
fitting._run_fit_impl=old
print(\"Unobserved cancellation preserves unrelated exception; observed cancellation normalized; thread-local cleared on both exceptional paths.\")
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll
 succeeded in 1380ms:
Unobserved cancellation preserves unrelated exception; observed cancellation normalized; thread-local cleared on both exceptional paths.

codex
1. **MAJOR — Start-response order determines ownership.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511) registers ownership only after awaiting the start response. Reproduced: invocation A starts first, B’s response arrives first, then A’s delayed response cancels B. B returns `superseded`; A returns its result. Delayed uploads permit the same reversal. Establish an invocation token before the caller’s first await.

2. **MAJOR — Superseded polls still apply results or trigger rollback.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556) handles terminal responses without rechecking ownership after the fetch/body awaits. Reproduced with the actual callers: Auto-Fit has a poll in flight; Run Fit supersedes it; the old poll returns `cancelled`. Auto-Fit throws and restores its snapshot at [templates/index.html:7754](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7754), causing the replacement to discard itself as “model edited.” A delayed `done` response also returns the obsolete result. Recheck supersession after asynchronous boundaries and before error handling, rollback, or result application; supersession must also precede timeout handling.

3. **MINOR — Partial thread startup releases admission twice.** [app.py:716](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:716), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285). If the fit thread starts but heartbeat-thread startup raises, the route releases admission although the worker remains alive. Its eventual `finally` releases again. Fault injection reproduced seven outstanding jobs against the six-job cap. Make admission release have exactly one owner after worker startup.

Validation: 86 targeted JavaScript tests and three numerical cancellation tests passed. Additional in-memory probes reproduced all findings and verified unrelated exceptions remain unchanged and cancellation thread-local state clears. Files unchanged; full server acceptance was not rerun in this read-only environment.

**VERDICT: NO-GO**
tokens used
77,361
1. **MAJOR — Start-response order determines ownership.** [templates/index.html:7511](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7511) registers ownership only after awaiting the start response. Reproduced: invocation A starts first, B’s response arrives first, then A’s delayed response cancels B. B returns `superseded`; A returns its result. Delayed uploads permit the same reversal. Establish an invocation token before the caller’s first await.

2. **MAJOR — Superseded polls still apply results or trigger rollback.** [templates/index.html:7556](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7556) handles terminal responses without rechecking ownership after the fetch/body awaits. Reproduced with the actual callers: Auto-Fit has a poll in flight; Run Fit supersedes it; the old poll returns `cancelled`. Auto-Fit throws and restores its snapshot at [templates/index.html:7754](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/templates/index.html:7754), causing the replacement to discard itself as “model edited.” A delayed `done` response also returns the obsolete result. Recheck supersession after asynchronous boundaries and before error handling, rollback, or result application; supersession must also precede timeout handling.

3. **MINOR — Partial thread startup releases admission twice.** [app.py:716](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:716), [app.py:1285](/Users/skyefortier/xps-app/.claude/worktrees/fix-fit-start-poll/app.py:1285). If the fit thread starts but heartbeat-thread startup raises, the route releases admission although the worker remains alive. Its eventual `finally` releases again. Fault injection reproduced seven outstanding jobs against the six-job cap. Make admission release have exactly one owner after worker startup.

Validation: 86 targeted JavaScript tests and three numerical cancellation tests passed. Additional in-memory probes reproduced all findings and verified unrelated exceptions remain unchanged and cancellation thread-local state clears. Files unchanged; full server acceptance was not rerun in this read-only environment.

**VERDICT: NO-GO**
