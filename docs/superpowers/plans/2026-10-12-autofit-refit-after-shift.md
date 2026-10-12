# Q8 — Auto-Fit refits after its charge shift (owner, 2026-10-12)

Owner: "Q8: SWITCH — Auto-Fit refits after its charge shift. Draft a student note (held; I send
it)." Its own unit, Codex ×2, stop for deploy approval. Measurement before the decision:
`docs/findings/q8-autofit-refit/README.md`. Design: sealed-fit v6 memo, step 0d.

## The defect

Auto-Fit made ONE fit in its provisional frame, then moved the frame by the fitted graphite
centre, re-selected the window, recomputed the background and locked every centre — and showed
that fit's statistics, curve and areas with the moved points. Its R-factor compared the fit's
curve with other points: on 18 of the 51 committed C 1s Auto-Fits it read 15–17 % for fits whose
own R is ~2 %; χ²ᵣ and the areas belonged to a fit on other points and another background.

## The change

- `applyAutoFitResult(json, …)` handles the ANCHOR fit: its gates (`_autoFitAnchorRefusal`:
  supported, required, refit converged, centre in the reference window — unchanged), the charge
  shift derived from it exactly as before, the background check on the re-selected window, and
  the centre locks. It publishes nothing.
- `runAutoFitC1sGraphite` then makes the FINAL fit: `_autoFitRequest` reads the request from the
  page as it stands after the shift (the window and points, the background, the model — its values
  from the anchor fit, every centre locked — with buildAutoFitModel's bounds, the method,
  `n_perturb` 3 and `require_component`), with its own 2-minute limit, under the same ownership and
  edit guards. The final fit's anchor is held to the same gates. `_autoFitPublish` publishes it as
  before (statistics, record, Results, one history snapshot, the 40 % warning); one undo entry
  (the existing `pushUndo` before the model is built).
- A final fit that does not converge ("Auto-fit not applied: the final fit in the corrected frame
  did not converge …"), whose anchor no longer passes ("After the refit in the corrected frame —
  …"), is discarded (tab switched, model edited) or whose request fails restores everything, as a
  failed anchor fit does; superseded by a newer fit on the tab, it writes nothing.
- Between the fits the spinner reads "Auto-Fit: anchor fitted, refitting in the corrected frame…";
  no statistics are shown (none exist until the final fit is published).

## Measured

- Before the decision (`scripts/q8_autofit_refit.py` on main, the final fit built by the harness):
  `docs/findings/q8-autofit-refit/README.md`.
- The shipped unit (`scripts/q8_autofit_refit.py` against this branch → `results_shipped.json`;
  `scripts/q8_confirm.py` → `confirm.json`): on 49 of the 50 tabs both runs fitted, what Auto-Fit
  now shows equals the measured final fit (area % ≤ 0.26 pp, χ²ᵣ ≤ 0.6 %, R ≤ 0.02 pt — Trust-Region's
  arithmetic jitter); refitting the shipped result again changes nothing (area % ≤ 3e-4 pp, χ²ᵣ
  ≤ 8e-9): Auto-Fit's result is at its minimum. B4C C1s Scan_1 differs by 11.5 pp, and three tabs
  (B4C Scan_0, Scan_8, UCl4_on_graphite Scan_4) were refused in one run and applied in the other —
  in each case main's own ANCHOR fit (an identical request) lands differently from run to run
  (the known Trust-Region non-reproducibility near a basin boundary, CLAUDE.md "Reproducibility");
  see "Run-to-run on the B4C project" below.

## Tests

- `tests/js/autofit_refit.test.js` (the deployed page's `runAutoFitC1sGraphite`, the server's job
  routes simulated): the final fit is made on the shifted window with every centre locked and is
  the only one published; a final fit that does not converge, whose anchor fails, or whose model is
  edited while it runs restores everything with its message; a refused anchor fit makes no second
  fit. Publishing the anchor fit (the old behaviour) fails 4 of 5.
- `tests/test_browser_autofit_refit.py` (real browser, real server, the committed 8-JT Graphite
  C 1s Scan): the points shown are EXACTLY the points the published fit was made on, the centres
  locked, graphite at 284.50, R < 5 %. Fails on main (the shown points are the moved ones).
- The existing Auto-Fit harnesses follow the split (the gates through `_autoFitAnchorRefusal`, the
  request through `_autoFitRequest`, the publication through `_autoFitPublish`).

## Run-to-run on the B4C project

`Q8_ONLY=B4C scripts/q8_autofit_refit.py`, three runs on main (main2 stopped after 7 tabs on a
harness crash, a NaN uncertainty in a refit reply — the harness now reads such a reply as a failed
refit) and two on this unit (`docs/findings/q8-autofit-refit/b4c_runs/`). Graphite's area % as
shown (main: the harness's final fit; the unit: Auto-Fit's result):

| Tab | main1 | main2 | main3 | unit1 | unit2 |
|---|---|---|---|---|---|
| C1s Scan | 29.4 | — | 29.4 | 29.4 | 29.4 |
| C1s Scan_0 | refused | — | 49.8 | 49.4 | refused |
| C1s Scan_1 | 5.8 | 5.8 | 5.8 | 5.8 | 5.8 |
| C1s Scan_2 / _4 / _5 / _6 / _7 | equal in every run | | | | |
| C1s Scan_3 | refused | refused | refused | refused | refused |
| C1s Scan_8 | refused | — | refused | refused | refused |

Scan_0's anchor fit is refused in some runs and applied in others on main and on the unit alike (a
NaN uncertainty in the anchor fit's reply); the measurement run's 13.2 % on Scan_1 and its applied
Scan_8 were such runs. The unit reproduces main's result wherever main's own anchor fit does.
