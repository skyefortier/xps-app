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
  as before. `XPS_HELPER_LOG` appends each call's duration (used for the budget below).
- Every helper call in `tests/js/` (10 calls in 6 files: lineshape_parity, lineshape_roundtrip,
  background_parity, background_not_converged, manual_background_statement, local_lm_descent)
  goes through it; no test file requires `child_process`.
- `tests/js/helper_timeout.test.js`: a helper that never reads its input and never exits is
  killed at its timeout with the plain message, promptly; so is one blocked on an input larger
  than the pipe buffer; a finishing helper returns its output and a failing one reports its own
  status, not a timeout; the default budget is finite; and no JS test file starts a process
  except through `runHelper` (source scan of every file in `tests/js/`).
- CI JS floor 582 → 587.

## The budget

Measured with `XPS_HELPER_LOG` over a full JS run: 239 helper calls, the slowest 2.46 s
(`background_parity_backend.py`; every helper ≤ 2.5 s). 300 s is ~120× that — room for a
loaded machine — and turns a stall into a failure in 5 minutes instead of a hung job.
