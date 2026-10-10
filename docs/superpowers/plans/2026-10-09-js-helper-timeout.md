# JS test helper processes cannot hang (owner, 2026-10-09)

Owner: "lineshape_parity.test.js can hang when its Python helper waits on input — add a
timeout so a stall fails instead of hanging CI. Small unit." PROGRESS.md (LOGGED): every
`execFileSync` / `spawnSync` call in `tests/js/` to a helper process carries a timeout (a
stall FAILS with a plain message naming the helper); a test proves the timeout fires.

## What happened

2026-10-07: during a full JS run that had been moved to the background, the Python helper of
`tests/js/lineshape_parity.test.js` (`lineshape_parity_backend.py`, started by
`execFileSync` with `input`) sat blocked in `read()` on its stdin at 0 % CPU for 10+ minutes
(stack sampled: `_io_FileIO_readall_impl` → `read`). `execFileSync` has no timeout of its own,
so the suite never finished. A rerun detached with `< /dev/null` passed.

## Change

- `tests/js/_helper_process.js`: `runHelper(file, args, opts)` = `execFileSync` with
  `timeout` (default `HELPER_TIMEOUT_MS` = 300 s, `XPS_HELPER_TIMEOUT_MS` overrides) and
  `killSignal: 'SIGKILL'`; on `ETIMEDOUT` it throws `helper process "python3
  lineshape_parity_backend.py" did not finish within 300 s and was killed (a stalled helper
  fails the test instead of hanging the run)`. Any other failure of the helper is reported
  as before — with one stated exception: SIGKILL (so a helper that ignores SIGTERM is stopped
  too) is also the signal Node uses when it kills a helper whose output exceeds `maxBuffer`, so
  that error is still `ENOBUFS` but its `signal` reads SIGKILL instead of SIGTERM (no caller
  reads it; pinned). A timeout that is not a positive whole number of ms (0 would disable
  Node's deadline) is refused. `XPS_HELPER_LOG` appends each call's duration (used for the
  budget below).
- Every helper call in `tests/js/` (10 calls in 6 files: lineshape_parity, lineshape_roundtrip,
  background_parity, background_not_converged, manual_background_statement, local_lm_descent)
  goes through it; no test file requires `child_process`.
- `tests/js/helper_timeout.test.js`: a helper that never reads its input and never exits is
  killed at its timeout with the plain message, promptly; so is one blocked on an input larger
  than the pipe buffer; a finishing helper returns its output and a failing one reports its own
  status, not a timeout; a buffer overflow is still ENOBUFS; no caller can pass a timeout that
  disables the deadline (0, negative, fractional, NaN, Infinity, a string); and no file node can
  load from `tests/js/` (any depth, `.js` / `.mjs` / `.cjs`, the test file itself) or the CI
  reporter names the process module or calls one of its launch functions (comments included).
  Its limit: a static scan cannot see a module name built at run time. Mutation-checked: an
  aliased import behind a string holding `//`, a launch in a nested `.mjs`, and removing the
  timeout validation each fail a test.
- Codex round 1 (NO-GO x2): `timeout: 0` disabled the deadline; the scan skipped itself,
  nested modules, `.mjs` / `.cjs` and the reporter and stripped `//` inside strings; the
  SIGKILL side effect on ENOBUFS was unstated. All fixed as above.
- Codex round 2 (NO-GO x2, one finding): the wrapper was exempted by its NAME, so a nested
  `lib/_helper_process.js` passed unread. Now only its exact path is exempt, and a test runs the
  same scan over a temporary tree (the wrapper, a nested namesake, an `.mjs`, a `.cjs` behind
  a string holding `//`, a RegExp `.exec`) and requires exactly the three launches to be found
  (mutation-checked: the name-based exemption fails it). The ENOBUFS test now asserts the
  SIGKILL signal it pins (round 2 run A, MINOR).
- CI JS floor 582 → 589.

## The budget

Measured with `XPS_HELPER_LOG` over a full JS run: 239 helper calls, the slowest 2.46 s
(`background_parity_backend.py`; every helper ≤ 2.5 s). 300 s is ~120× that — room for a
loaded machine — and turns a stall into a failure in 5 minutes instead of a hung job.
