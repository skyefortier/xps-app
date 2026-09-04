# DRAFT — not sent. Student note for the background-window fix (unit 1c)

Status: draft for Skye's review. Do not send until 1c is deployed and the
deploy date below is filled in.

---

Subject: XPS Fitting Studio — background window now includes the endpoint you set (small number changes)

Hi all,

Short version: from [DEPLOY DATE], when you run a fit, the background is
anchored on the *exact* window you set in the bg-start / bg-end fields.
Until now it was anchored one data point inside that window at the
low-binding-energy end. Fits you re-run after the update will therefore
differ slightly from the same fit run before it. Nothing you already
reported was calculated incorrectly for the window the fit actually used;
that window was just one point narrower than the one you drew.

This is a different situation from the note I sent last week about the
asym-GL / LA lineshape. That one was an error in what the app reported
(the plotted curve did not match the fitted one), and the ask was to
re-check exports. This one is a correction to a definition: the on-screen
background preview always used your full window, the server-side fit used
the window minus its last point, and we have made the fit match the preview.

What changes, and by how much

- Which fits: any fit with a Shirley, Smart, Smart-exp, Tougaard or Linear
  background. Fits where you left the window at the ROI edges (the default)
  will all move a little. Fits where you typed a window bound that sits
  between two data points inside the ROI may not move at all.
- How much: it depends on the intensity step at the endpoint that is now
  included. On a real U 4f scan from the lab (Smart background, 0.1 eV
  steps) the background moved by 92 counts at the low-BE edge and 0 at the
  high-BE edge, and the fit moved by:
  - reduced χ²: 1.83 → 1.93
  - U 4f main-line centres: +0.017 eV
  - main-line areas: +0.4 to +0.5 %; satellite areas +1.6 to +4.2 %
  - atomic fractions: within 0.25 percentage points
  Treat "χ²ᵣ up to ~0.1, centres up to ~20 meV, areas up to ~4 %, fractions
  under 1 percentage point" as the expected range. Satellites and weak
  components move more than main lines because they sit on the background.

What to do

- Values already in a manuscript or thesis draft: re-run the fit once after
  the update and use the new numbers. Note in your records which fits were
  re-run. Both sets of numbers are legitimate fits; they differ only in
  whether the last window point was included.
- Values still being worked on: just keep going. Anything you fit from
  [DEPLOY DATE] onward uses the corrected window.
- Old saved projects (.proj) still open normally. The stored numbers are
  the old fit until you press Run Fit again.
- If you compare a re-run with the old result and see a change larger than
  the range above, send me the .proj file. That would mean the fit is very
  sensitive to a single data point at the window edge, which is worth
  looking at (endpoint averaging > 1 usually fixes it).

The reasoning, the measurement, and the committed script that reproduces
it are in the repository under docs/superpowers/plans/ (background
architecture memo, round-5 amendment) if you want the detail.

Skye
