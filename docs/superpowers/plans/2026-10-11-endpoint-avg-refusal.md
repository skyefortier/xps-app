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

## Codex round 3 (run A GO, run B NO-GO) — fixed

Run A: no BLOCKER or MAJOR (every earlier finding resolved; 472 background comparisons against
main bit-identical). Run B, one MAJOR:

| finding | fix |
|---|---|
| a valid saved spelling the number input cannot hold ("+3", " 7 ", "0x10", "1.") became a blank when restored into the field (the input blanks text outside its floating-point grammar), and was then refused though every reader accepts it | `_restoreUI` writes an already-valid saved value as its plain decimal; a real-browser save → load → Run Fit round trip for each spelling (5 of 7 fail without it) |
| MINOR (both runs) a saved array (`[3]`) read as 3 by the page, refused by the Python twin | both refuse a non-scalar (one line each) |

Logged, not changed (run A, MINOR): measurement tooling keeps its own readers —
`tests/js/local_lm_server_parity_backend.py` (`int(value or 1)`),
`scripts/optimizer_disagreement_targets.js` (`parseInt(value) || 1`),
`scripts/bg_window_worked_example.py` (`int(...)`); none is a production reader.

## Codex round 4 — GO ×2

No BLOCKER or MAJOR in either run. Two MINOR, both logged in PROGRESS.md, not changed (the unit
stays as reviewed): a malformed saved ARRAY can still be restored into the field as its string
form (non-physical; a one-line "restore an object as blank" would close it); the measurement
tooling's own readers (logged in round 3). Ready to merge WITH THE NEXT DEPLOY (owner).

## After round 4 (owner, 2026-10-11): the logged array gap closed

The owner closed the round-4 MINOR by the one-line-refusal rule: `_restoreUI` restores a
non-scalar saved averaging (`[3]`, `["3"]`, an object) as a blank field, which is then refused
("Fit not run: endpoint averaging …"). Real-browser test for each; the array cases fail without
the line.

Test-only, same commit: `test_browser_envelope_identity`'s LACX β = 0.1 lock (split out of the
α + β case on 2026-10-11) failed 2 of 12 through the browser path on main as on this branch —
its certificate ran past 50 restarts — although it certified in all 24 fresh-process probes. The
LACX cases are now α = 5, α = 0.1 and β = 5 alone, each 12 of 12 through the browser path; β's
lower bound alone is not covered.

## Codex round 5 — GO ×2

The closing line and the LACX test change reviewed: no BLOCKER or MAJOR; the logged tooling
MINOR only. Deploy approved by the owner (2026-10-11).
