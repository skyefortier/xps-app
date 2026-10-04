# Student note — backgrounds are now solved and checked; what happens to saved fits — HELD UNTIL DEPLOY

Status: DRAFT, held by the owner (background-math unit, owner round 2026-10-03; not
yet approved for deploy). Every number is from the committed data:
`docs/superpowers/plans/2026-10-01-background-math-implement.md` §7 (the restore census
of the 121 committed saved fits and the 202-target measurement), the preview-vs-fit
comparison `scripts/bg_math_preview_vs_fitted.py` (63 committed fits that store both
curves). The owner sends it.

---

Subject: XPS Fitting Studio — backgrounds, and what you will see when you open an older project

Hi all,

This update changes how backgrounds are computed and checked, and what happens when you
open a project saved by an earlier version. Most of you will notice very little. Here
is what changed and why.

What was wrong

- The background drawn on screen was not the one your fit used. The page drew a quick
  preview (a Shirley stopped after a fixed number of steps) while the server fitted
  against its own fully converged background. On our 63 saved fits that stored both, they
  differed by a median of 0.8 % of the background's height (at most 7.6 %); the net area
  under them by a median of 0.5 % (at most 4.7 %, more than 1 % on 16 fits). **Results
  saved before this change were computed against a different background than the page
  showed.** The fitted numbers were the server's, consistent with its own background;
  what you saw drawn under them was not exactly that background.
- Endpoint averaging changed the data, not just the end levels: Shirley, Smart and
  Tougaard replaced the points at the window's edges by their average before computing.
- Some backgrounds were reported even when they had no solution — most often a window
  with no peak in it.

What changed

- Endpoint averaging now sets only the two edge levels the background is anchored to;
  every method computes from your measured data, and Linear now uses the same averaged
  edge levels.
- Every background is solved to convergence and then checked against its own defining
  equation. If it has no solution, the page says so under the background menu
  ("… background not converged") and nothing is fitted or exported against it. For a
  window with no peak in it, use the Linear background — the message says so.
- The page now draws exactly the background the server fits, and sends the server your
  data at full precision (it used to round intensities to two decimals).
- "Smart" and "Smart (experimental)" were the same calculation; there is now one entry,
  "Smart". Files that used either still open.
- The "Shirley iterations" setting is gone (every Shirley now runs to convergence).

What you will see when you open an older project

The page compares the background each saved fit was actually fitted against with the
one its settings give today, on the fit's own points:

- If they agree (within rounding), the fit opens exactly as it was. On our 121 saved
  fits: 15.
- If they differ, the fit opens with its OWN background and peaks, but its statistics
  (χ², R-factor, RMSE, uncertainties) are marked out of date and are not shown or
  exported, and an amber message tells you by how much the backgrounds differ. Press Run
  Fit to bring it up to date. On our saved fits: 66, nearly all because older versions
  chose the background window's end points slightly differently; most differ by under
  1 % of the background's height, at most 5 %.
- If the file does not contain enough to check (older versions sometimes saved no fitted
  curve, or not the energies it was fitted on), your peaks open and you press Run Fit.
  On our saved fits: 40.

Six fits differ under either window rule (all Smart): 4-GTA UCl4-BN B1s Scan_1 (2.95 %),
U4f Scan_0 (1.65 %), U4f Scan (1.65 %), B1s Scan_4 (1.55 %), U4f Scan_3 (1.17 %), and
UCl4_on_graphite U4f Scan_2 (0.88 %). If you reported numbers from these, re-run them.

Will my fitted numbers change if I press Run Fit again?

Almost never by much. On our 202 test fits the backgrounds themselves moved by at most
0.001 % of net area. The fit's random restarts are drawn once more in this version (they
are now seeded from your data and settings rather than from the computed background, so
they will not change again for arithmetic reasons), and six fits that sit between two
solutions landed in another one, by 1 to 29 percentage points. The "scattered starts"
line under the Results table flagged four of them ("0 of 3 scattered starts reached this
solution" or similar, often with another solution listed). It did not flag two: on those,
every scattered start reached the same answer, and on one of them (a C 1s scan) that
answer fits worse than the one the previous version found. If you see the line, your
decomposition is not unique — look at the alternatives before reporting it. If you do not
see it, that is not a guarantee: the starts are scattered around YOUR starting values, so
also try a different starting model when a component's area matters.

As before: identical requests give identical results on real data in practice; the
underlying arithmetic is not bit-reproducible, so a fit sitting near a boundary between
two solutions can still resolve differently, and that is precisely what the
scattered-starts check is there to show you.
