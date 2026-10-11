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
