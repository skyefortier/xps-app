# Scattered-starts check + "component not supported by the data" — plan

Status: APPROVED by the owner 2026-09-21 with the decisions in §5 (now
answered) and the order settled by the measurement in §6. Implementation in
three separately deployable steps, each with its own Codex pass. Evidence and owner decisions it rests on:
`docs/findings/2026-09-fit-determinacy.md` (§2, §3, §5),
`docs/findings/optimizer-disagreement/REPORT*.md`.

## 1. Decisions already made (owner, 2026-09-19 → 09-21)

- The second opinion is SCATTERED STARTS of the student's own method, not a
  second method (Trust-Region and LM share minima: the pair flags 60 % of bad
  outcomes).
- THE STUDENT'S METHOD RESULT REMAINS THE FIT. Lower-χ²ᵣ solutions appear
  beside it as alternatives, each with its own areas AND its centre
  displacements from the student's start, so a relocated component is visible
  at a glance. The app presents evidence; the chemist decides. Never
  substitute a different chemical interpretation because it scored better
  (8-JT C1s Scan_1: χ²ᵣ 12.3 by sliding C–O 1.47 eV under the main line).
- Wording: "N starts reached the same solution". No certification language,
  no "best of N".
- Presentation reuses Find Peaks' "Other models compared" pattern; no new
  dialog.
- Amplitude at its lower bound becomes an explicit outcome — the component is
  NOT SUPPORTED BY THE DATA; its centre, width and σ are suppressed. Zero is
  allowed in both engines (local floor 1 → 0). Same class of statement as
  "these starts disagree": the fit did not determine this.
- "Is the Auto-Fit anchor actually REQUIRED?" moves here, as a REFIT without
  the component (from the Auto-Fit anchor unit's limits).
- Trust-Region is not bit-reproducible; this check is the mitigation for fits
  near a basin boundary. No separate unit.
- One student note after this ships, explaining the finding and the new
  behaviour together.

## 2. New evidence for the open design choices (measured 2026-09-21)

Trust-Region, page request (`n_perturb: 3`), the scatter of
`scripts/optimizer_disagreement_run_starts.py` (amplitude ×/÷ 3, width
×/÷ 1.5, free centres ± 0.5 eV inside the request's ± 2 eV window, bounded
shape parameters redrawn inside the middle 90 % of their range), first K
starts, multi-component targets only (≥ 2 unlinked peaks):

| | re-fit of a saved solution (n = 94) | not-yet-fitted start (n = 84) |
|---|---:|---:|
| K = 3: every start within 1 pp of the fit | 69 % | 73 % |
| K = 3: some start found a LOWER χ²ᵣ, > 1 pp away | **0 %** | **8 %** |
| K = 3: only HIGHER-χ²ᵣ solutions elsewhere | 31 % | 19 % |
| K = 5: some start found a LOWER χ²ᵣ | 1 % | 10 % |
| K = 5: only HIGHER-χ²ᵣ solutions elsewhere | 38 % | 24 % |

Cost: 10 scattered Trust-Region fits take a median 1.8 s per target (90th
percentile 4.1 s); 3 starts ≈ a third of that. Reported-fit accuracy from
the earlier run: > 5 pp from the best known solution on 7.8 % of fresh
starts with the default alone, 3.2 % with 3 scattered starts, no gain from
5 or 10.

Can the server tell a fresh start from a re-fit? Not cleanly. The relative
χ² drop achieved by the first minimisation: re-fits median 4 %, 95th
percentile 50 %; fresh starts median 420 %, 5th percentile 14 %. A 50 %
threshold flags 5 % of re-fits and misses ~12 % of fresh starts.

## 3. Proposed behaviour

### 3.1 When it runs — PROPOSED DEVIATION from "fresh starts only"

Run the check on EVERY Run Fit with ≥ 2 unlinked components, not only fresh
starts. Reasons: (i) there is no reliable request-side test for "fresh"
(above), and a page-side "dirty" flag would be new state with its own
consumer list; (ii) the reason for scoping it was cost, and 3 Trust-Region
starts cost ~0.6 s; (iii) on re-fits it surfaces a lower-χ²ᵣ alternative
0 % of the time at K = 3, so it cannot nag — it simply says "3 of 3 starts
reached this solution", which is the evidence a student re-opening a saved
project wants. If you prefer fresh-only, the fallback is the 50 % χ²-drop
rule with its 5 % / 12 % error rates.

Not run: single-component and fully-linked models (B 1s / Cl 2p never
disagreed, 0 of 43); `differential_evolution` and `basinhopping` (already
global; 30–120 s each); Batch Fit and the local fallback (local engine; a
local result is already labelled a starting point); Find Peaks.

### 3.2 Server (`fitting.run_fit`, `/api/fit`)

- New optional request field `n_starts` (page sends 3; default 0 = today's
  behaviour; validated 0–10 like `n_perturb`).
- After the normal fit (first minimisation + the seeded `n_perturb`
  restarts — unchanged, and its result is THE FIT), run `n_starts`
  scattered starts with the student's method, `n_perturb = 0` each. The
  scatter draws come from a THIRD stream spawned from the same request seed,
  so they are reproducible and do not disturb the existing two streams
  (pinned seeds/draws stay valid). The scatter definition is the measured
  one in §2, anchored to the REQUEST's start (not the jittering fitted
  solution), centre windows anchored to the request's centres.
- Cluster the successful starts against the fit and against each other:
  same solution = every component's area fraction within 1 pp AND every
  free centre within 0.1 eV. (Both thresholds are presentation grain, not
  science: 1 pp is the grain of every table in the findings record.)
- Response gains `starts`:
  `{n_run, n_converged, n_same_as_fit, n_worse_elsewhere, alternatives: [...]}`.
  An ALTERNATIVE is a cluster with χ²ᵣ lower than the fit's by more than
  0.1 % — per your decision only lower-χ²ᵣ solutions are shown; clusters
  with higher χ²ᵣ are only COUNTED (they are what a bad start looks like,
  and would appear on ~30 % of all fits). Each alternative carries: χ²ᵣ,
  how many starts reached it, and per component: area, area %, centre,
  centre − the REQUEST's start centre, fwhm, amplitude, plus the full
  parameter set needed to apply it.
- Nothing about `success`, the fit, its statistics or its uncertainties
  changes. A failure inside the starts never fails the fit (`starts.error`).

### 3.3 Page

- Results panel, under the peak table, always (when the check ran), one
  line: "3 of 3 scattered starts reached this solution." /
  "2 of 3 scattered starts reached this solution; 1 ended in a worse one
  (χ²ᵣ 7.9)." / "… 1 found a DIFFERENT solution with a lower χ²ᵣ — see
  below. Your fit is unchanged."
- When alternatives exist: a table in the Find Peaks "Other models
  compared" style — one row per solution, first row "Your fit". Columns:
  χ²ᵣ · starts that reached it · per-component area % · largest centre
  displacement from your start (component name + eV, amber when > 0.5 eV,
  red when > 1 eV: "C–O moved +1.47 eV"). Row actions: **Preview**
  (overlay on the chart, same mechanism as the fit-history preview) and
  **Use this solution** (explicit click; undoable via `pushUndo`; applies
  through the same path as a server result and records
  `fitResult.chosenAlternative = {fromChi, toChi, maxCentreShift}` so
  exports and saves can say the student chose it).
- Tooltip / help text carries the disclosure wording from CLAUDE.md
  ("identical requests give identical results in practice … precisely the
  situation the multiple-starts check is designed to surface").
- Status bar and "Fit complete" toast unchanged. No modal, no blocking.

### 3.4 "Not supported by the data"

Definition — the statistic already shipped for the Auto-Fit anchor
(`_autoFitGraphiteIsSupported`), generalised to any component as
`_componentSupport(json, peakId)`: with the other components held at their
fitted values, removing the component does not make the fit significantly
worse (χ²_without ≤ χ²_with, or F < 10). A bound-pinned amplitude always
satisfies this. No intensity threshold (six failed; owner: no seventh).
Computed server-side once per fit and returned per component as
`support: {f, supported}` so every consumer reads one field; the JS twin
stays for the local engine and for loaded files.

Engines: server floor stays 0; local engine floor 1 → 0 (one line in
`runFitLocal`'s clamp; the active-set logic already holds a wall-blocked
parameter). `buildAutoFitModel` seeds and `_fpPeakFromBackend`'s
`amplitude || 1` (turns a real 0 into 1) are checked, not blindly changed.

Auto-Fit anchor, "is it REQUIRED?": after a successful Auto-Fit, ONE extra
`/api/fit` without the Graphite component (others free, same bounds). If
that refit's χ²ᵣ is not worse by F ≥ 10 for the anchor's parameters, the
anchor is redundant → same red refusal as today, different sentence. Cost:
one fit, Auto-Fit only.

### 3.5 Site table for "unsupported" (enumerated up front; Explore sweep of
`templates/index.html`, 2026-09-19 — ask Codex to BREAK this list)

| # | Site | Change |
|---|---|---|
| 1 | `renderPeakList` (sidebar card: centre ×2, fwhm, area %) | badge "not supported by the data"; centre/fwhm → "—" |
| 2 | `renderResults` (centre ± σ, fwhm ± σ, area, %) | row greyed, "—" for centre/width/σ, area 0, footnote |
| 3 | `_validateUncertainties` panel | new first rule: unsupported components listed here (today an amplitude at 0 is SILENT: the at-bound rule needs a finite max, which the page never sends); after Auto-Fit's centre lock such a component currently lands in the neutral "locked" box — it must land here instead |
| 4 | `renderQuantify` / `recalcQuantify` | excluded from the atomic-% table body, listed beneath as unsupported |
| 5 | `updatePlot` datasets + tooltip | curve hidden (it is a zero line), legend entry struck through |
| 6 | `_buildEntryRenderData` / `_buildStackDatasets` (other tabs' peaks, cached) | same as 5; cache invalidation on fit |
| 7 | `_doPublicationExport` (fills, outlines, LABEL at the component's maximum, legend) | no label, no legend entry; figure footnote optional |
| 8 | `exportFitTable` CSV/XLSX | status column; centre/width/σ cells empty; WARNING row |
| 9 | `exportResults` TSV (one curve column per peak) | column kept (zeros), header suffixed "(unsupported)" |
| 10 | saves: `_doSaveFit`, `_doSaveSpectrum`, `buildTabData` | persist `support` per peak; loads without it → recomputed by the JS twin when a fitResult with curves exists, else "unknown" (never assumed supported) |
| 11 | `applyBackendResult`, `runFitLocal` commit, `applyAutoFitResult`, `runPropagation` copy, `applyFindPeaks` | write/clear `peak.support`; Batch Fit must not silently propagate a zero amplitude (today it scales 0 → 0 and clears the fitResult) |
| 12 | undo/redo + history snapshots | carry `support` with the peak (deep copies already do) |
| 13 | linked children of an unsupported parent | whole multiplet unsupported (amplitude = parent × ratio) |
| 14 | charge correction | covered by the Auto-Fit anchor check; `isChargeReference` is decorative today (verified) |
| 15 | Find Peaks result table (engine response, pre-apply) | OUT OF SCOPE here: `autofit/engine.py` already treats amplitude@min as "component absent" in its own way |

Sites for the starts check: `runFit` (request + store `fitResult.starts`),
`renderResults` (line + table), chart preview layer, "Use this solution"
(apply + undo + provenance), saves/loads (`fitResult.starts` summary
persisted; alternatives' full parameter sets NOT persisted — they are
regenerable from the seeded request), `exportFitTable` (one line:
"scattered starts: 3 run, 3 same"), history snapshots, `app.py` validation
of `n_starts`, `/api/analyze` wrapper allowlist.

## 4. Tests and review

- Python: scatter determinism (same request → same starts and clusters),
  third stream leaves existing pinned seed/draws untouched, clustering,
  alternatives only when χ²ᵣ is lower, `n_starts` validation, a failing
  start never fails the fit, `support` on bound-pinned / residue / resolved
  fixtures (reuse `tests/js/fixtures/autofit_anchor.json`).
- A committed regression on real data: 8-JT C1s Scan_1-type targets must
  report an alternative with a > 1 eV centre displacement; saved-solution
  re-fits must report none (the 0 % row of §2, as a test over the committed
  projects).
- Node: extracted-function tests for every site in §3.5; JS twin parity
  with the server's `support`.
- Browser check on :5151, then Codex ×2 with BOTH site tables in the first
  prompt (method note 2026-09-18).
- Re-measure on the 202 targets after implementation: fraction of fresh
  starts where the page now SHOWS the better solution (target: the 8 % row)
  and the time added per Run Fit.

## 5. Decisions (owner, 2026-09-21)

1. TRIGGER: every Run Fit with ≥ 2 unlinked components (deviation accepted:
   "a classifier with 5 % / 12 % error rates is worse than not classifying";
   "3 of 3 starts reached this solution" on a re-opened project is positive
   information). Exclusions as listed in §3.1.
2. K = 3.
3. Worse solutions are COUNTED, not listed ("counting them is what tells the
   student the search was real; listing 30 % of fits' worth of bad minima
   would train people to ignore the panel").
4. "Use this solution" is offered — explicit, undoable, recorded — WITH ONE
   ADDITION: when the alternative's largest centre displacement is in the RED
   band (> 1 eV), applying it requires a confirmation that NAMES the moved
   component and the distance ("This solution moves C-O by +1.47 eV.
   Apply?"). Not a modal for every alternative; only for the case measured
   and known to be chemically dangerous (8-JT C1s Scan_1).
5. Unsupported components are excluded from the Quantify body and listed
   beneath ("0.0 % is a measurement claim; exclusion plus a named listing is
   the honest statement that the fit did not determine it").
6. The Auto-Fit "is the anchor required?" refit is in this unit, step (c).
7. Three separately deployable steps, each with its own Codex pass; (a) and
   (b) are additive and leave no inconsistent intermediate state.

## 6. Order of steps — decided by measurement (owner: "one number decides it")

Question: (b) fixes a SILENT OVERCLAIM that is live today (a component at
zero amplitude reports a centre, width and σ as though determined); (a) adds
a capability. If components land at the floor often, (b) goes first.

Measured (`scripts/amplitude_floor_frequency.py` →
`docs/findings/optimizer-disagreement/amplitude_floor.jsonl`): all 202
committed targets fitted as the page sends them (Trust-Region, `n_perturb: 3`,
seeded, inputs rounded to 2 dp), the shipped support statistic applied to
every unlinked component.

| | targets with ≥ 1 unsupported component | components unsupported |
|---|---:|---:|
| all | 3 of 202 (1.5 %, Wilson 0.5–4.3) | 3 of 752 (0.4 %) |
| re-fit of a saved solution | 3 of 107 | 3 of 399 |
| fresh start | 0 of 95 (Wilson 0–3.9) | 0 of 353 |

None is literally at zero (none below 1e-6 of the strongest component); the
three are weak C 1s components at 0.25–0.65 % of the strongest line with
F = 0.95, 2.0 and 3.9 (UCl4_on_graphite C1s Scan_4 "Unknown 2", Cl2p_projfit
C1s Scan_0 "Unknown 2", 8-JT C1s Scan_6 "Adventitious 2"). All three are
reported today WITH a centre and a width ± σ, so the overclaim is real where
it occurs. B 1s, Cl 2p, U 4f: 0 of 132. Caveat: committed projects are fits
students chose to keep; a component that collapsed may have been deleted
before saving (survivorship) — but the fresh-start rate, 0 of 95, points the
same way.

RARE → the proposed order stands: (a) scattered-starts check, (b) the
unsupported-component outcome, (c) the Auto-Fit refit.
