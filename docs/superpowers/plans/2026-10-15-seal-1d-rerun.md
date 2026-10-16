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
   numerics identity of `a.software` vs `b.software` (the re-run's own record). Pure, bounded (the body
   size cap of `/api/verify-fit`), shape-checked by `fitting.response_form_failure` (a malformed side is a 400,
   never compared).
3. **The replay** is an ordinary fit through the start/poll path (Cloudflare's ~100 s ceiling): the record's
   samples uploaded (`R.energies`, `R.counts`, full precision), `R.request` with `seed: O.random_seed`, Cancel.
   It is dropped when the tab closes or another fit is installed in its place — checked while it runs and again
   before its outcome is kept; an edit or a tab switch does NOT drop it: the outcome is a fact about the RECORD,
   kept beside that seal (a runtime WeakMap seal → outcome) and shown only beside that seal displayed as recorded
   (amended after Codex 1d round 1). The result is NEVER installed and NEVER changes the model, the seal or its
   state: the re-run's reply does not even tell the page the server's numerics (no `_noteServerSoftware`) — a
   deployment is learned from the next ordinary check — and its own numerics are reported on their own line,
   the record's identity against the RE-RUN's (never against the worker answering the comparison).
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
solution (a stubbed replay reply); a re-run dropped by a replaced fit or a closed tab keeps nothing (an edit only hides its outcome, a tab switch keeps it); the seal,
the model and the state never change; Cancel.

## The exact structure (owner 2026-10-15, option 3, after Codex rounds 2-9; refined in rounds 10-12)

Rounds 2-9 each found one more crafted request the endpoint compared or answered 500, check by check. The owner's
decision: `/api/compare-fits` validates EACH response against the exact structure the server writes, before comparing
anything; anything else is refused with a plain 4xx message, never a 500. `fitting.response_structure_failure(O)`
(beside the verifier's form check, excluded from the numerics digest like it) — every rule what `run_fit` writes,
verified on seal 1b's 328 records:

- the response's form (`response_form_failure`: exact keys, types, arrays of n numbers);
- every number one a float represents (an integer only if a float holds it exactly) — except a component's id and the
  id its support follows, which are labels the fit echoes (round 11: an id 9007199254740993 or 10^400 the server
  accepts); nesting no deeper than a response's; the software record no field a server does not record;
- at least one component; ids any the server accepts — `f"p{id}_x"` an identifier (it builds every parameter name
  so), not a list or object — unique by that spelling (round 10: "", "é", null, true, false are real ids);
- a component's lineshape one the server has, its parameters EXACTLY that lineshape's arguments plus `area`;
- links exactly as the fit writes them (`_make_peak_params`, round 11): a linked component's centre is
  `p<M>_center + <number>` and its amplitude `p<M>_amplitude * <number>` — both, always — and every other parameter
  is either ALL `p<M>_<the same name>` or none (one flag, `fix_fwhm`), M one OTHER component of the SAME lineshape
  whose id is not null (`constrain_to: null` is no link); the numbers spelt as Python writes a finite float, never
  `-0.0` (the fit folds −0 to 0); a linked parameter neither varies nor carries a bound (the fit leaves it
  unbounded, round 12); an unlinked component has no expression; no cycle; no chain deeper than the comparison
  follows;
- support as the fit writes it: a linked component's `support.follows` is its ROOT component's id and its verdict
  the root's; an unlinked component's support follows nothing. (Round 12 found the producer itself reading
  `constrain_to` two ways — the link by equality, the support walk by string spelling, so `constrain_to: 1.0` for id 1
  was linked but kept its own verdict; the walk now finds the master as `_make_peak_params` does. No fitted number
  moves and the page never sends such a reference; the numerics digest records it as equivalent.)
- the scattered starts list every component in order; an alternative's components likewise, each carrying exactly
  its own parameters;
- every scale a comparison measures against finite: n × the energy span, every point of the background-subtracted
  signal, every bound span; and across the two sides, the longest curve × a's span.

Evidence: every real record and every lineshape × link × lock a fit writes passes (tests); each hostile case of
rounds 1-11 is refused on side a, side b and both; an oracle deletes every key a response must have and adds a key,
in every object of a real response holding a link and an alternative, on either side, and requires 400 for each
(which keys a response may omit is decided by the object's PATH: only the software fields recorded since 2026-10-15);
a seeded fuzz of 3,000 random mutations of a real response answers
only 200 or 400. Stated limit: a fit the server accepts with a bound span no comparison can measure (±1e308) is
refused a re-run, with the reason; the page never sends such bounds.
