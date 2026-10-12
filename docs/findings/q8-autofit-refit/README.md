# Q8 — Auto-Fit refits after its charge shift: what changes (measured 2026-10-12)

Sealed-fit v6 Q8 (owner 2026-10-11: measure first, show the numbers before switching). TODAY
Auto-Fit makes one fit (A) in its provisional frame, then moves the frame by the fitted graphite
centre, re-selects the window, recomputes the background, locks every centre — and shows A's
numbers with the moved points. PROPOSED (ship step 0d): a second, final fit (B) in the corrected
frame — A's model with every centre locked, the same bounds, method, restarts and anchor check —
whose numbers are what is shown and sealed.

Generator: `scripts/q8_autofit_refit.py` (the deployed page's own `runAutoFitC1sGraphite` in a real
browser against a local server on main 432f4db; B built from the finalised page state exactly as
Auto-Fit builds its request) → `results.json`; `scripts/q8_summarise.py` → `summary.json`. Set: every
committed C 1s tab — 54; Auto-Fit applied on 51 (3 refused today, unchanged by the proposal: a
2-minute timeout, a non-finite uncertainty, an anchor refit that did not converge).

| Quantity (51 tabs) | Today (A) → proposed (B) |
|---|---|
| R-factor shown | median 3.50 % → 1.85 %; **18 tabs show R 14.8–17.3 % today and 1.6–2.2 % after** (two B 4C tabs 11–12 % → 6 %); none above 10 % after (max 7.5 %) |
| χ²ᵣ shown | median −3.6 %; 39 lower, 12 higher; range −35 % to +35 %; 17 tabs move > 10 % |
| A component's area % | largest per tab: median 0.56 pp, 75th percentile 1.75 pp, max 3.85 pp; 19 tabs > 1 pp (the Graphite component the largest mover in 17 of them) |
| A component's FWHM | largest per tab: median 1.8 %, max 37 % (excluding a zero-amplitude satellite whose width is undetermined) |
| Centres | unchanged (locked by Auto-Fit; B keeps them) |
| The anchor's gates on B | supported, required and refit converged on all 51: no Auto-Fit would roll back |
| The 40 % graphite warning | 7 tabs warn under A and the same 7 under B; no flip |
| Time | B adds a median 0.9 s (A median 2.6 s) on this machine |

Why today's numbers differ: A's fitted curve belongs to A's points in the provisional frame, but
after the shift the page pairs it with the re-selected points and the recomputed background (on 11
tabs the window even holds a different number of points). The R-factor compares those two, so on a
third of the tabs it reports a mismatch the fit does not have; χ²ᵣ and the areas belong to a fit on
other points and another background than the one drawn. B is a fit on exactly what is drawn.
