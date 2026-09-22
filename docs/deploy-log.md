# Deploy log

What went to production (i9 LaunchAgent, xps.fortierlab.org), newest first.
One entry per deploy; an item that changes behaviour for every user gets its
own bullet even when it shipped inside a larger unit, so it can be found
later. Procedure: [DEPLOY.md](../DEPLOY.md). The xps2 droplet is deployed by
the owner and may lag.

## 2026-09-22 — "not supported by the data", step (b) (`feature-unsupported-components`)

- **Release note:** a component the fit drove to zero is now reported as
  "not supported by the data": its centre, width and uncertainties are not
  shown, it is excluded from Quantify, and both engines allow a zero
  amplitude.
- Definition: with the other components held as fitted, removing the
  component does not make the fit significantly worse (the Auto-Fit
  anchor's F statistic, F ≥ 10). Computed by the server per component
  (`individual_peaks[].support`) and by the local engine from its own
  residuals; a linked component follows its root ancestor.
- The verdict is bound to the fit that produced it (model + background /
  ROI / anchors / charge shift) and lapses on any edit until a new fit;
  exports write a Status only from a current verdict.
- Sites: sidebar card, Results table (percentages over supported
  components), uncertainty panel, Quantify (listed beneath), chart / stack
  / figure labels, CSV/XLSX (Status column, empty cells, no At%, WARNING),
  TSV header, the scattered-starts table. Local amplitude floor 1 → 0.
- Measured on the 202 committed targets: 3 of 752 components (three C 1s
  re-fits), 0 of 95 fresh starts — survivorship-biased (a collapsed
  component may have been deleted before saving).
- Codex GO ×2 (round 6); suite 975 passed / 7 skipped.

## 2026-09-22 — scattered-starts check, step (a) (`feature-scattered-starts-check`)

- **CORRECTNESS FIX FOR EVERY RUN FIT: a result is discarded if the model
  was edited while the fit was running.** The peak controls stay editable
  during a fit; a centre changed and locked mid-fit used to keep its edited
  value under the server's χ², σ and fitted curve. `runFit` now compares the
  model-plus-context key taken before its first await with the key at
  completion and, if they differ, applies nothing ("Fit discarded (model
  edited)", previous peaks and result kept). Independent of the starts check.
- Scattered-starts check: every Run Fit with ≥ 2 unlinked components runs 3
  more fits of the same method from seeded scattered starts. The student's
  result remains the fit; "N of 3 scattered starts reached this solution";
  lower-χ²ᵣ solutions listed beside it with each component's own area % and
  move from the student's start; Preview; "Use this solution" (atomic re-fit,
  one undo, recorded, exported) with a confirmation naming the component when
  it moved > 1 eV. Evidence is bound to the fit that produced it (model +
  background/ROI/anchors/charge shift) and disappears from the panel, saves
  and exports after any such change. Measured: alternative on 0 of 94
  re-fits, 6 of 84 fresh starts; median +0.54 s per Run Fit.
- `POST /api/fit` accepts `n_starts` (0–10) and returns `starts`.
- Codex GO ×2 (round 3); suite 968 passed / 7 skipped.

## 2026-09-21 — Auto-Fit anchor support check (`fix-autofit-zero-graphite-cc`)

- Auto-Fit C1s no longer derives the charge correction from a Graphite
  component the data do not support (with/without-component F statistic from
  the `/api/fit` response). Shipped by owner decision after six Codex rounds,
  all NO-GO, with documented limits: false rejection under a gross
  single-channel artefact; redundancy under overlap out of scope.
- Rollback after a rejected Auto-Fit restores the Custom-reference field.

## 2026-09-21 — request-derived seeding (`fix-seed-perturbation`)

- Every random draw in `run_fit` comes from a seed derived from the numbers
  the optimiser is handed. Before → after on 202 targets × 5 presses:
  fractions moving > 1 pp between presses 8 → 0 (Trust-Region), 12 → 0 (LM).
  Trust-Region is not bit-reproducible (owner: accept and disclose).
- **`run_fit` refuses methods outside the five supported ones** (closes
  unseeded lmfit methods reachable through `/api/analyze`).

## 2026-09-20 — Differential Evolution fix (`fix-de-finite-bounds`), findings merge

- Differential Evolution runs from the page's requests (was HTTP 422 for
  every fit with a free amplitude); never worse than the default method from
  the same start; generated search limits never reported or stored.
- `investigate-optimizer-disagreement` merged (docs and scripts only).
