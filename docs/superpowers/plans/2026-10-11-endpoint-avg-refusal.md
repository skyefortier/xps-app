# Endpoint averaging outside 1–50 is refused, never clamped (owner, 2026-10-11)

Owner: "Run Fit (and the server) refuse endpoint averaging outside the field's own 1-50
range with a plain message — refuse, don't clamp, so no background changes. Codex x2, then
merge with the next deploy." (Logged by the fit-recording unit, Codex round 3: the page's
helpers parse the field twice, so 1e21 acted as 1 on the page and as 1e21 on the server.)

## Before

- `/api/fit`, `/api/fit/start`, `/api/background`: `max(1, int(x))` — 0 and −5 fitted at 1,
  51 or 1e21 at the window's quarter; a non-number was a 400.
- The page: every fit path read `parseInt(field) || 1` — blank and unreadable text fitted at 1;
  "1e21" was 1 to the page's helpers and 1e21 to the server; "1e1" was 1 to parseInt and 10 to
  Number. Find Peaks (archived) already refused outside 1–50 (`pop_endpoint_avg`).

## After — one rule, two twins

- `fitting.check_endpoint_avg(raw)`: a whole number from 1 to `ENDPOINT_AVG_MAX` = 50 (the
  field's max) — an integer or an integral finite float, never a bool or a string — else
  `ValueError("endpoint_avg must be a whole number from 1 to 50, got …")`, a 400 from every
  route. Called by the three routes (replacing the clamp), `run_fit`, `compute_background_only`,
  and Find Peaks' `pop_endpoint_avg`. An absent value is 1, as it always was.
- Page `_endpointAvgFailure(text)`: accepted only when the field's text is a whole number 1–50
  that `parseInt` (the helpers' reader) and `Number` read alike; otherwise "endpoint averaging
  must be a whole number from 1 to 50 (it is "…")." Run Fit (incl. "Use this solution")
  refuses before the undo entry, the spinner and any request ("Fit not run: …"); Auto-Fit in
  its preflight, leaving a running Run Fit alone ("Auto-Fit not run: …"); Batch Fit leaves
  that target unfitted with the reason. The preview is unchanged.
- A value in range computes exactly as before: no background changes. Every committed
  project's saved averaging is in range (1, 2, 6, 25, 31) — nothing committed is refused.
- Not changed: `autofit/reference.py`'s twin reads a saved ui with `max(1, int(x))` (it
  measures committed projects, all in range; an out-of-range value now reaches `run_fit` and
  is refused there).

## Tests

`tests/test_endpoint_avg_refusal.py` (the rule's table; the three routes and `run_fit` /
`compute_background_only` refuse 0, −5, 51, 1e21, 2.5, "3", True, None; absent = 1; 1, 3, 50,
3.0 fit, the background bit-identical to `compute_background`); `tests/js/fit_acceptance.test.js`
(the page reader's table; Run Fit refuses with no upload, request, undo entry or local fit;
50 fits; Batch Fit / Auto-Fit wiring); `tests/js/fit_start_poll.test.js` (an averaging refusal
in Auto-Fit's preflight leaves a running Run Fit alone); `tests/test_browser_endpoint_avg_refusal.py`
(real page: 1e21, 0, 51, 2.5, 1e1 refused with nothing sent; 50 fits with k = 50 recorded; a
Batch Fit target given 1e21 is not fitted, with the reason). Harness stubs whose blank field
used to mean 1 now hold "1". Mutation-checked: the route clamp, the Run Fit and Batch checks,
and the parseInt/Number agreement each fail a test when removed.

## Codex round 1 (NO-GO ×2) — fixed

Both runs: the entry checks work, but other readers of the field bypassed them.

| finding | fix |
|---|---|
| the fit key read the averaging with `parseInt`: "1" = "1e2", so a result was applied (and the local fallback run) after the field was changed to a refused value during the upload | `_fitKeyCanon` reads it as the refusal does: a refused text stays itself; "3" = "3.0" = " 3 " |
| restored fits, stack reconstruction, saves, TSV and the figure computed backgrounds at 51 (a restored fit at 51 read current) | the refusal is in `computeBackgroundCore` itself, so every consumer refuses through the existing not-converged path ("Background not computed: …"); an ABSENT value stays the legacy 1 |
| Batch Fit refused after the target's undo entry, peaks, settings and charge correction were replaced; a blank field went through (`_captureUI` makes it 1) | the source field is checked as typed before any target is touched |
| Find Peaks' engine (`_compute_background`, `fit_candidate`) and `autofit/parity.background_like_run_fit` accepted 0, 51, 1e21 | both call `fitting.check_endpoint_avg` |
| the saved-project twin (`autofit/reference.py`) clamped "0" to 1 and read "3.0" as 1 | `page_endpoint_avg`: the page reader twinned (JavaScript's `Number` and `parseInt` on the trimmed text), pinned equal to the page on 37 texts |
| archived Find Peaks converted the field with `parseInt(…) \|\| 1` before validating | the field as typed is refused first |
| `/api/analyze/start` created a job before the worker refused | validated in `_validate_analyze_request` |
| two tests did not prove their claim (Auto-Fit's accepted any refusal; "before the spinner" observed no spinner) | each refusal asserted by its own reason (the averaging case finds a graphite peak); a spinner counter |

Mutation-checked: the key, the core refusal (with a restore test isolated so only the refusal can
fail it — fitted at 50 on a 201-point window, saved as 51 in the settings and the key), Batch,
the engine, parity, the analyze route and the twin each fail a test when reverted.

## Codex round 2 (NO-GO ×2, the same two findings) — fixed

Round 1's engine, parity, Batch, archived Find Peaks, analyze-route and test findings resolved
(both runs: 456 / 472 background comparisons against main bit-identical for every valid value,
absent settings and accepted spellings across eight methods).

| finding | fix |
|---|---|
| clearing the field during a fit still passed the in-flight check: `_captureUI` turned a blank into "1" before the key's reader saw it (a result applied, or the local fallback run) | the capture keeps the field as typed (`?? LEGACY_ENDPOINT_AVG` only when the field does not exist) |
| a saved 0 or blank became 1 before the refusal: `_computeBackgroundForSource`, `_restoreUI` and both loaders used `endpointAvg \|\| LEGACY` (a restored fit at 0 read current) | every one defaults only an ABSENT value (`??`); a saved 0 or blank reaches the refusal |
| the Python twin's synthetic spellings (logged under the owner's rule, but cheap): Python's `strip` set vs JavaScript's `trim`, Unicode digits, `int()`'s 4 300-digit limit and radix overflow | JavaScript's whitespace set, ASCII-only digits, no big-integer conversion (a value with more than four significant digits is never 1-50); the parity table adds those spellings |

Mutation-checked (the capture and the source reader, each with an isolated test: a fit at 1
saved as blank or as 0 in the settings and the key).
