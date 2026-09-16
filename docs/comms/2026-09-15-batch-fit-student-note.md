# Student note for the Batch Fit defect (unit A0) — DRAFT, send after deploy

Status: drafted from the proof in
`docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md` and the scanner
`scripts/scan_batch_fit_signature.py`. Fill in [DEPLOY DATE] after the
deploy; the owner sends it.

---

Subject: XPS Fitting Studio — Batch Fit never fitted anything (26 Mar – [DEPLOY DATE] 2026): re-run every Batch Fit result

Hi all,

This is not like the two notes from earlier this month. Those were about
numbers that were slightly off. This one is about results that were never
fitted at all.

**If you used Batch Fit for anything in a thesis chapter, manuscript, report
or group-meeting slide, those numbers are not fits. Re-run them.**

How to tell if a saved file is affected (do this first)

1. Run the scanner on your project and spectrum files:

       python scripts/scan_batch_fit_signature.py  ~/path/to/your/files

   It lists the tabs it suspects, with the evidence for each. It works on
   .proj.zip, .proj.json and .spec.json files, and on whole folders. It
   is a triage tool: a file with no hits is not proven clean (older files
   that lack an rmse value cannot be classified), so if you know a tab
   came from Batch Fit, re-fit it regardless.
2. Without the scanner, the signs in the app are: the σ (uncertainty)
   columns in Results are blank, and the χ²ᵣ shown for the tab is in the
   thousands or millions (a real server fit is usually between 1 and 30).
   In a saved project, tabs that came from Batch Fit also carry exactly the
   same peak centres and widths as the spectrum they were copied from.
3. Run Fit, Auto-Fit C1s Graphite and Find Peaks fit on the server, and
   server fits were correct. Two exceptions for Run Fit: if the server
   could not be reached OR returned an error, Run Fit silently switched to
   the same page optimiser (you saw the amber "Local Fit Performed" box),
   and if the server reported that its fit had not converged, Run Fit
   applied it anyway and said "Fit complete". Both are fixed now; the
   scanner catches the first, the second shows as an unusually poor fit.

What happened, plainly

Batch Fit copies your source model to each selected spectrum, scales the
peak heights, and then fits it with a small optimiser built into the web
page (not the server). That optimiser had a sign error from the app's
first version (26 March 2026); Batch Fit shipped on 30 March 2026 and has
used it ever since. Every step the optimiser proposed made the fit worse,
so it rejected every step and stopped, and the page then reported
"Fit complete (local LM)" with the copied starting model as the result.
The Results panel, the Quantify table, the CSV/XLSX exports, the figure
export and saved .proj / .spec.json files all showed that un-fitted model
as if it were a fit.

The same page optimiser was used by Run Fit whenever the server could not
be reached or returned an error. If you ever saw the amber "Local Fit
Performed" box, that result was your starting model too.

How far off

I re-fitted the lab's UCl4-on-graphite project the proper way (server fit
from the same starting model) and compared with what Batch Fit had shown:

- C 1s scans (9): centres off by 56 to 537 meV, widths by 11 to 42 %,
  component areas by 13 to 74 %, atomic fractions by 3 to 12 percentage
  points.
- U 4f scans (9): centres off by 69 to 352 meV, widths by 3 to 79 %,
  areas by 12 to 50 %, fractions by 1.5 to 9.6 percentage points.

Repeat scans that closely resemble the source are less wrong than this;
scans that differ more are worse. There is no safe subset. The repository's
own example projects contain two affected tabs.

What to do

1. Run the scanner, or open each project that used Batch Fit and look for
   the signs above.
2. On every affected tab press Run Fit (the ordinary button). The copied
   model is a fine starting point; the server fit from it is the real
   result. Then re-export.
3. Replace every affected number in anything already written. If you
   cannot tell whether a tab came from Batch Fit, re-fit it; it takes
   seconds.
4. From [DEPLOY DATE], Batch Fit uses a corrected optimiser and tells you
   per spectrum whether it converged. It is still the page optimiser: it is
   unweighted (it reports "Residual variance", not χ²ᵣ) and gives no
   uncertainties, and its answer can differ materially from the server fit.
   For anything you will publish, follow Batch Fit with Run Fit on each tab.
5. If a re-fit changes a conclusion you have already drawn, tell me. This
   was not something you did wrong.

I am sorry about this one. The proof (a replay of the shipped code on the
committed lab project), the scanner, and the fix are in the repository.

Skye
