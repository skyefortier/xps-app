# Student note — Run Fit: two fits of the same model could disagree; what changed — READY TO SEND (deployed 2026-09-22)

Status: every number is from `docs/findings/2026-09-fit-determinacy.md`
(§2, §6), `docs/findings/optimizer-disagreement/REPORT*.md` and
`docs/superpowers/plans/2026-09-21-scattered-starts-and-unsupported-components.md`
(§2, §7). Deployed to xps.fortierlab.org: Differential Evolution fix
(2026-09-20), request-derived seeding (2026-09-21), scattered-starts check
(2026-09-22); each Codex GO ×2 with a production browser check
(`docs/deploy-log.md`). Scope (owner): the optimiser story only — the
finding and its mitigations. Unsupported components (steps (b), (c)) are a
different subject and will be a release-note line, not part of this note.
The disclosure sentence about bit-reproducibility is the owner's wording
(CLAUDE.md). The owner sends it.

---

Subject: XPS Fitting Studio — the same model could give two different fits; Run Fit now checks for that and shows you

Hi all,

This note is about a finding, not a bug in the usual sense, and about three
changes that went in over the last few days because of it.

What I found

I took every fitted spectrum in six of our saved projects (202 fits) and
ran each model through three of the server's methods from the same starting
point.

- The methods disagreed by more than 1 percentage point of area fraction on
  19 % of the fits. When they disagreed the typical difference was 1.6
  points, and the largest was 24.
- The default method (Trust-Region) was not always the one that did best.
  Starting from a model that had not been fitted yet — the situation you
  are in when you build a new model — it ended more than 5 points away from
  the best solution any method found about 8 % of the time. Re-fitting a
  model that was already a saved solution was much more stable (about 1 %).
  B 1s and Cl 2p models with one to three peaks never disagreed; the
  problem lives in multi-component models, C 1s above all.
- Run Fit was not repeatable. Behind the button the server restarts the fit
  a few times from randomly nudged values and keeps the best, and that
  randomness was different on every press. On one of our C 1s scans five
  presses of Run Fit on the identical model gave χ²ᵣ 70.6, 18.5, 70.6, 38.3
  and 18.5. On 8 of the 202 fits the area fractions moved by more than 1
  point from one press to the next.

All of those were reported as converged fits. None of this means a
particular published number is wrong; it means a converged fit is not proof
that the answer is the only one the data allow.

What changed

1. Run Fit is repeatable now. The random nudges are derived from the fit
   itself (your data, model, background and settings), so the same fit gives
   the same result on any press, any day, any computer. Measured on the same
   202 fits, five presses each: the number whose fractions moved by more
   than 1 point between presses went from 8 to 0. Re-opening a saved project
   and pressing Run Fit regenerates its figure. One honest caveat: identical
   requests now give identical results on real data in practice; the
   underlying arithmetic is not bit-reproducible, so a fit sitting near a
   boundary between two solutions can still resolve differently, and that is
   precisely the situation the multiple-starts check is designed to surface.
   (Note that after a fit the page holds the fitted values, so pressing Run
   Fit a second time is a new fit from a new starting point, not a repeat.)

2. Run Fit now checks whether other starting points lead somewhere else.
   For any model with two or more independent peaks, after your fit the
   server runs the same method three more times from scattered starting
   values (about half a second). Under the results table you will see a
   line such as

       3 of 3 scattered starts reached this solution.
       2 of 3 scattered starts reached this solution; 1 ended in a solution
       that is not better (χ²ᵣ 7.91).

   Read that as exactly what it says: a count. "3 of 3" means those three
   starts came back to your answer; it does not certify the fit. On our 202
   fits this is what you will see almost always.

   If a start finds a different solution with a LOWER χ²ᵣ, a table "Other
   solutions found" appears: your fit first, then each alternative with its
   own area percentages and, for every peak, how far it moved from where
   YOU placed it. You can preview an alternative on the chart, and "Use
   this solution" re-runs the fit from it (one Undo takes you back).
   Your fit is never replaced automatically. This appeared on 6 of the 84
   not-yet-fitted models in our projects and on none of the 94 saved ones.

3. A lower χ²ᵣ is not a better chemical model — please read the "move"
   column. The clearest example is ours. In the graphite C 1s project, on
   four scans there is a solution that scores much better (χ²ᵣ 12–18
   instead of 18–64) by taking the C–O component away from 286.4 eV,
   sliding it about 1.4 eV down, broadening it, and parking it under the
   main graphite line as a second large carbon species. The numbers like
   it; the chemistry does not: it invents a species you did not propose and
   deletes the one you did. The table shows such a move in red, and if you
   press "Use this solution" on it the app first asks, naming the peak and
   the distance ("This solution moves Adventitious 2 by −1.42 eV from where
   you placed it. Apply?"). The app shows you the evidence; you decide what
   is chemically sensible. If a peak wanders like this, that is a sign the
   model gives it too much freedom — lock its centre or reconsider whether
   the data support that many components.

Also changed, briefly

- Differential Evolution in the Method menu works again (it had been
  failing on every ordinary fit). It is slow (up to about a minute) and is
  not a gold standard either.
- If you edit a peak, the background or the ROI while a fit is still
  running, the result is now discarded with a message instead of being
  written over your edited model. Just press Run Fit again.
- Auto-Fit C1s now refuses, with a red message, to set the charge
  correction from a Graphite component the data do not support.

What to do

- Saved projects: nothing is required. Re-opening one and pressing Run Fit
  will now also show the scattered-starts line; on our own saved projects
  it found no better solution on any of 94 multi-component fits. That is
  reassuring, not proof.
- New multi-component models, C 1s especially: look at the line under the
  results. If alternatives appear, compare the area percentages and the
  moves before you quantify or report, and say in your notebook which
  solution you used and why.
- If the line says starts ended somewhere "not better", that is normal (it
  happens on roughly a quarter of fits) and needs no action: it is what a
  poor starting point looks like.
- The check can show that a decomposition is not unique. It cannot tell you
  which one is right, and it can miss things: on four of our scans even ten
  scattered starts did not find a better solution that a much slower method
  did. It is not run for Batch Fit, whose output remains a starting point:
  press Run Fit on each spectrum before you quantify, export or report.

As always, tell me if something looks wrong or if one of your spectra
behaves differently from what this note describes.
