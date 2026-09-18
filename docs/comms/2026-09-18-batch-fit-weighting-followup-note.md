# Follow-up student note — Batch Fit is now weighted (unit W1) — DRAFT, send after deploy

Status: drafted from the measurements in
`docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md`. It
CORRECTS point 4 of the 18 September note (the "more than 100 %" sentence),
which stops being true the moment this unit is deployed. Fill in
[DEPLOY DATE]; the owner sends it.

---

Subject: XPS Fitting Studio — Batch Fit is now weighted like Run Fit; what that changes and what it does not

Hi all,

A correction to one point of my note of 18 September, because the app has
changed since.

What changed

From [DEPLOY DATE], Batch Fit (and the fallback the page uses when the
server cannot be reached) weights every data point by its counting noise,
exactly as Run Fit does on the server. It did not before: that is why I
told you its component areas could differ from Run Fit by more than 100 %.
That sentence described the unweighted optimiser and no longer applies to
fits made from [DEPLOY DATE] on. The number Batch Fit reports is now a real
reduced χ², comparable with Run Fit's.

How close is it now? I measured it on the lab's own UCl4-on-graphite
project, comparing Batch Fit with Run Fit from the same starting model:

- C 1s scans whose model uses GL and asymmetric-GL peaks (8 of 9 targets):
  centres within 4 meV, widths within 0.5 %, component areas within 1.4 %,
  atomic fractions within 0.3 percentage points, and the same χ²ᵣ to three
  digits. Before weighting the same comparison gave up to 679 meV, 44 %,
  126 % and 29 percentage points.
- One C 1s scan: the two optimisers settled on different solutions of the
  same model (one component vanishes in one of them). Batch Fit's solution
  actually had the lower χ²ᵣ (18.2 against 19.1). Neither is "the" answer;
  that model is not unique on that scan, and the areas differ by up to
  100 % between the two.
- U 4f scans (LA main lines plus Voigt satellites): no improvement. Areas
  of the satellites still differ from Run Fit by 7 to 21 %. This is not the
  weighting. It comes from two known differences between the page and the
  server: Run Fit lets a "Voigt" peak's Gaussian/Lorentzian mix vary while
  the page holds it at 50 %, and the page keeps the LA smoothing parameter
  m fixed. Both are scheduled fixes.

What stays the same

Batch Fit output is still a starting point, not a reportable result, and
the app still labels it that way ("local, starting point"). The reasons
are now specific: no uncertainties, the Voigt and LA differences above,
and the possibility of a different solution where a model is not unique.
So the instruction from 18 September stands: press Run Fit on each
spectrum before you quantify, export or report. For GL-type models you
should now see almost nothing move when you do. If something moves a lot,
that is worth a look, not a nuisance: it usually means the model has more
than one solution on that spectrum.

Everything else in the 18 September note stands, including the scanner
and the need to re-fit anything made with Batch Fit before 18 September.
Files saved by the new version record that a fit came from the page
optimiser, so the scanner identifies them from the file itself.

The measurements and the code are in the repository under
docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md.

Skye
