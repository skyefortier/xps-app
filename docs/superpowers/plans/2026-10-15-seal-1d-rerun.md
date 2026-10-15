# Seal 1d — "Re-run this fit" (REPLAY-CHECKED)

Design memo V5.4 "REPLAY-CHECKED" and V6.22 (option (b)); plan 1c §12 step 9. Owner, 2026-10-15: judge the
FIT, report the scattered starts SEPARATELY (1b's replay: every fit reproduced, the starts differed on 7 of 328).

## What it is

Acceptance is shown "as recorded — not proven" (step 8). The re-run is the proof, on demand: a visible
**Re-run this fit** button beside every sealed SERVER result (Results, under the acceptance line), never a menu
item, never automatic, never a currency verdict. It refits the record's own request with the record's own seed
and compares the two fits:

- **reproduced within rounding** — the same fit (below);
- **a re-run reached a different solution** — the fit is not unique (the scattered-starts disclosure, owner
  2026-09-21: an accepted property, NOT stale), with the largest differences named;
- **made under other numerics** — the record's numerics identity (`NUMERICS_IDENTITY_KEYS`, the 2026-10-15
  rule) differs from the server's: the outcome is reported as such, with whether the fits agree;
- **could not be re-run** — the server could not be reached, refused the request, or the refit did not converge
  (the reason).

The scattered starts are compared on their own line ("the scattered starts: the same / differ: …") and never
change the fit's outcome.

A local fit has no replay: it is a starting point (A0), and its record is the engine's own exact check
(1c §6.4); the button is not shown, the designation says why. An Auto-Fit re-runs its FINAL fit (the result
shown); its anchor fit is evidence (E), named as not re-run.

## How

1. **One comparator, the server's.** `tests/fit_equality.py`'s `assert_same_fit` becomes the app module
   `fit_equality.py` (the tests import it from there, unchanged): `fit_differences(a, b)` returns the problem
   list (empty = the same fit); `assert_same_fit` stays its assertion wrapper. No page port (a second reading
   of "the same fit" is what the design rule forbids).
2. **`POST /api/compare-fits`** `{a, b}` → `{same, problems[], starts: {same, problems[]}, numerics:
   {same, differing[]}}`: the FIT compared with `starts` removed from both; the starts compared alone; the
   numerics identity of `a.software` vs `b.software` (`fitting.numerics_difference`). Pure, bounded (the body
   size cap of `/api/verify-fit`), shape-checked by `fitting.response_form_failure` (a malformed side is a 400,
   never compared).
3. **The replay** is an ordinary fit through the start/poll path (Cloudflare's ~100 s ceiling): the record's
   samples uploaded (`R.energies`, `R.counts`, full precision), `R.request` with `seed: O.random_seed`, one
   operation token (a newer fit, an edit or a tab switch discards it — Run Fit's ownership rules), Cancel.
   The result is NEVER installed, NEVER changes the model, the seal or its state; it is kept beside the seal
   (a runtime WeakMap seal → outcome), shown until the seal changes, not saved.
4. **Wording** (Results, under the acceptance line): "Re-run: reproduced within rounding." / "Re-run: a
   different solution (… moved …) — this fit is not unique." / "Re-run under other numerics (…): …" /
   "Re-run failed: …"; then "Scattered starts on re-run: the same." or "…: differ (…)".

## Measured before review

The 202 committed targets' records (1b run v2) re-run through `/api/compare-fits`: how many reproduce, how many
reach a different solution, how many differ only in their starts (1b's replay with `fit_equality`: every fit
reproduced, the starts differed on 7).

## Tests

Server: `fit_differences` agrees with the former test helper on its whole test file (`tests/test_fit_equality.py`
unchanged, importing from the module); the endpoint's verdicts on a reproduced fit, a different minimum (the
two-basin construction), starts-only differences, other numerics, malformed sides. Browser: the button on every
sealed server result (not on local, legacy or stale ones); a re-run that reproduces; a forced different
solution (a stubbed replay reply); a discarded re-run (edit / tab switch / newer fit) shows nothing; the seal,
the model and the state never change; Cancel.
