# Follow-up student note — Batch Fit is now weighted (unit W1) — READY TO SEND (deployed 2026-09-18)

Status: numbers verified against
`docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md` and
`docs/findings/2026-09-fit-determinacy.md`. Unit W1 deployed to
xps.fortierlab.org on 2026-09-18 (Codex GO x2; production browser check
passed). It UPDATES point 4 of the earlier 18 September note: on the 18
measured scans the unweighted optimiser was the main cause of the "more
than 100 %" differences, and weighting removes that cause; every remaining
limitation is kept in the body. Framing (owner): lead with the improvement
and the measured numbers; this is the first of these notes that is good
news. The owner sends it.

---

Subject: XPS Fitting Studio — good news: Batch Fit now agrees with Run Fit on our C 1s data (measured)

Hi all,

After several notes about things that were wrong, this one is about
something that got better, with numbers.

What improved

As of today's update (18 September 2026), Batch Fit weights every data
point the same way Run Fit does on the server (by the square root of its
intensity). That was the main reason the two used to disagree. I measured
the effect on the lab's own UCl4-on-graphite project, comparing Batch Fit
with Run Fit from the same starting model:

| C 1s scans, GL / asymmetric-GL models (8 scans) | before | now |
|---|---|---|
| peak centres | up to 679 meV apart | within 4 meV |
| widths | up to 44 % | within 0.5 % |
| component areas | up to 126 % | within 1.4 % |
| atomic fractions | up to 29 percentage points | within 0.32 |
| χ²ᵣ | not comparable | same to three digits |

So for that kind of model, Batch Fit now gives you essentially the Run Fit
answer, and the χ²ᵣ it shows means the same thing as Run Fit's. (For data
recorded as counts per second, this weighting is a convention rather than a
calibrated counting uncertainty. That is equally true of Run Fit.)

One result worth knowing about

On a ninth C 1s scan the two disagreed, and Batch Fit was the one that was
right. Run Fit's default method (Trust-Region) had stopped at a poorer
solution (χ²ᵣ 19.1); Batch Fit found a better one (18.2), and when I
re-ran the server with Levenberg–Marquardt, with basin-hopping, or
restarted from Batch Fit's answer, it agreed with Batch Fit every time.
The better solution removes one of the six components altogether: the data
on that scan do not support six peaks. The two solutions differ by up to
100 % in component area, and both were reported as converged fits. The
lesson is general and not about a bug: a converged fit is not proof of a
unique answer, and neither program is automatically the referee. If Batch
Fit and Run Fit disagree on one of your spectra, re-run Run Fit with a
second method and look for a component being driven towards zero.

What still limits Batch Fit

Batch Fit output is still labelled a starting point, not a reportable
result, and the instruction from my last note stands: press Run Fit on
each spectrum before you quantify, export or report. The reasons are now
specific rather than general:

- It gives no uncertainties.
- U 4f models did not improve: satellite areas still differ from Run Fit by
  7 to 21 %. That is not the weighting. Run Fit lets a "Voigt" peak's
  Gaussian/Lorentzian mix vary while the page holds it at 50 %, and the page
  keeps the LA smoothing parameter m fixed. The Voigt difference is the
  next fix, and I will re-measure after it lands.
- The two programs use different lower limits for a peak's height, so a
  very weak component can still come out very differently (well over 100 %
  for that one component). Which limit is right is an open question I am
  deciding on its merits, not by copying one program into the other.
- Where a model has more than one solution (the scan above), they can land
  on different ones.

These figures are what I measured on those 18 scans, not a guarantee for
every model. On the GL-type C 1s models almost nothing moved when I pressed
Run Fit afterwards; if something moves a lot on yours, look at which
component moved: a very weak one, a Voigt or LA one, or a model with more
than one solution.

Everything else in my earlier note of 18 September stands, including the
scanner and the need to re-fit anything made with Batch Fit before that
date. Files saved by the new version record that a fit came from the page
optimiser, so the scanner identifies them from the file itself.

The measurements are in the repository under
docs/superpowers/plans/2026-09-18-local-engine-poisson-weighting.md and
docs/findings/2026-09-fit-determinacy.md.

Skye
