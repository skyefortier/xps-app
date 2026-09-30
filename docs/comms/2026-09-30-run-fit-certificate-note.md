# Student note — Run Fit now checks that a fit really finished — HELD UNTIL DEPLOY

Status: DRAFT, held by the owner until unit A2 is deployed (owner decision
2026-09-29). Every number is from `docs/findings/runfit-certificate/README.md`
on the 202 committed fit targets with the page's own request (3 perturbed
restarts, 3 scattered starts): the changes, convergence and the new line from
the run of the SHIPPED code ("Final code", data/final_*.jsonl); the time from
the V3 measurement (the same scope, measured without other load); the
stopped-short counts from the scope check (docs/findings/fit-termination-scope/).
The owner sends it.

---

Subject: XPS Fitting Studio — Run Fit now checks that a fit actually reached its minimum

Hi all,

A short one about Run Fit, and one new line you may occasionally see under
the Results table.

What was wrong

When Run Fit reported "Fit complete", that meant the optimiser had stopped
by its own rule — not that the fit had reached the best point for your
model. On the 202 fits in our saved projects, the default method stopped
short on 8 of them and Levenberg-Marquardt on 32. Five Levenberg-Marquardt
fits were reported as failed even though they were essentially finished.

What changed

After the optimiser stops, the server now continues the SAME fit — your
model, from where it stopped — until continuing no longer improves it. Only
then is it "Fit complete". If it cannot get there, the fit is reported as not
converged, with the reason. Nothing else about the search changed: the same
restarts from the same points, the same scattered-starts check.

What you will notice

- Almost nothing, most of the time: on 198 of 202 fits (default method) the
  component areas moved by less than 1 percentage point, typically not at all.
- On a few fits the result is different, and in every such case the finished
  fit is better (a lower reduced chi-square): with the default method areas
  moved by more than 1 point on 4 of 202 fits (two multi-component C 1s fits,
  the largest 15 points, and two U 4f satellites, about 1.5 points each); with
  Levenberg-Marquardt on 2 of the 197 fits that had converged before (both
  C 1s, the largest 13 points: reduced chi-square 21.0 -> 15.5). If you re-run
  a saved fit and the areas shift, that is why.
- Separately, and not new: a few C 1s models have two solutions so close in
  quality that the default method can land in either from one run to the
  next (on one of our scans the areas differ by 22 points between the two).
  This happened before this change too; the scattered-starts line is what
  tells you when it applies to your fit.
- Five Levenberg-Marquardt fits that used to fail now complete (197 -> 202),
  and the scattered-starts line says "did not converge" far less often (on
  30 -> 3 fits).
- It costs almost no time: a median of well under a tenth of a second per
  Run Fit, under a second for nine fits in ten (measured on an otherwise
  idle server).
- NEW LINE: when finishing the fit carried a component more than 1 eV from
  where the optimiser had stopped, the Results panel says so, in red — e.g.
  "Fit continued past where the optimiser stopped; C-O moved −1.47 eV". It is
  a notice, not a question: it is still your model and your start. But a
  component that moved that far may no longer be the chemical state you
  meant, so look at it. On our 202 fits it never happened (the largest such move was
  0.04 eV), so if you do see it, it is worth a look.

What has not changed

A fit that reached a minimum is not necessarily the right chemistry, and a
model can have more than one minimum. That is still what the "N of 3
scattered starts" line is for. Re-running an identical saved fit reproduces
it within meaningful precision; the underlying arithmetic is not
bit-reproducible, so a fit that sits near a boundary between two solutions
can still resolve differently from one run to the next — and that is exactly
the situation the scattered-starts check is designed to surface.
