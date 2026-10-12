# Q5 — one area definition, the server's, for every reader (owner, 2026-10-12)

Owner: "Q5: SWITCH to the server's area everywhere. Also: any component centred outside the fit
window gets a plain note in Results ('centred outside the window — its area is poorly determined
by the data'). Measure how many saved components get the note." Its own unit, Codex ×2, stop for
deploy approval. Measurement before the decision: `docs/findings/q5-area/README.md`.

## The change

- `_peakArea(p, be)` = `_trapezoidArea(evalPeakArray(be, p), be)`: |trapezoid(y, x)| in numpy's
  order (d = diff(x); the terms d · (y[1:] + y[:-1]) / 2; their pairwise sum, `_npPairwiseSum`), so
  the page's number IS the server's `individual_peaks[].params.area`. It was a rectangle sum × the
  first step. Every reader goes through it: Results, the sidebar and its support patching, Quantify
  (which takes Results' areas), the CSV/XLSX export, Auto-Fit's 40 % graphite warning.
- The spectrum save's per-peak `area` uses the same `_trapezoidArea` (it had its own sequential
  trapezoid with |dx|: equal on every committed grid, different on a non-monotonic one).
- Results: a component whose centre lies outside the grid the fit was made on (`fitResult.be`, else
  the ROI grid — the grid Results integrates on) is named in a plain note beneath the table:
  "<name> is centred outside the window — its area is poorly determined by the data." A centre on
  the window's edge is inside.

## Measured

`scripts/q5_areas_on_load.py` (every committed project loaded into the page in a real browser) →
`docs/findings/q5-area/on_load.json`: a component's area moves by a median 0.007 % (max 0.20 %); area %
by at most 0.008 pp; no 40 % warning flips; **no saved component gets the note** after loading. The
pre-decision "8 B-O components centred outside, 17–19 %" (raw records, `scripts/q5_area_definitions.js`)
was an artefact: those B 1s saves hold their fit grid in the uncorrected frame (README).

## Tests

- `tests/js/one_area.test.js`: `_trapezoidArea` equals scipy's `abs(trapezoid(y, x))` BIT FOR BIT
  on 31 grids (2 to 1 001 points; ascending, descending, irregular; the design memo's non-monotonic
  [0, 2, 1] → 1); every reader goes through `_peakArea`; the save's own trapezoid is gone.
- `tests/js/lineshape_roundtrip.test.js`: for every lineshape, the page's trapezoid of the server's
  curve is the server's area exactly, and the page's area of its own drawn curve is within 1e-6.
- `tests/js/unsupported_components.test.js`: the Results note (one outside; two named in one note;
  a centre on the edge gets none).
- `tests/test_browser_export_prefix.py`: the earlier page (52e5b4a) is given today's area function
  before it exports, so its CSV / TSV are still an exact prefix of today's and both XLSX sheets agree
  row for row — every line, row and column other than the area values is unchanged (without the
  override the comparison fails on the area cells, which is this unit's change).

## Codex round 1 (NO-GO ×2, the same findings) — fixed

- **One grid, not only one formula.** Results integrated on the frozen `fitResult.be`, the sidebar,
  its support patching and the spectrum save on the live ROI grid: after a charge correction they
  showed different areas (1 284 vs 9 361 in the reviewers' reproduction) and Results flagged a
  component inside its window. Every reader now integrates on `_areaGrid()`: the fit's own energies
  while it is current (a restored fit's `_modelBe` — the energies the old server integrated on — else
  `fitResult.be`), otherwise the live ROI grid. The spectrum save integrates the fit's own components
  on the energies they were evaluated on (`_modelBe`), and otherwise writes what Results shows.
- **The note follows edits.** `_refreshStartsEvidence` (every `updatePlot`) compares the note's
  `data-peak-ids` with the components now outside and re-renders Results when they differ: it had
  stayed as it was while Results was already stale. It is also shown with no fit (a saved fit the
  load cannot reconstruct, a model not yet fitted), judged on the live window.
- **The count** was of raw records and of a wrongly framed grid: measured again through the page's
  own load (above) — 0.
- **Tests** prove behaviour: `tests/test_browser_one_area.py` (after a Run Fit the server's area,
  Results/Quantify, the spectrum save, the CSV and the sidebar % agree exactly; after a charge
  correction they agree on the live grid; the note appears and disappears as a centre moves while
  stale; the note with no fit — both fail on 5319bf5); `tests/js/one_area.test.js` the grid rule incl.
  `_modelBe`.
- MINOR: `scripts/q5_area_definitions.js` froze its rectangle baseline explicitly (it called the
  page's `_peakArea`, now the trapezoid) and runs again; marked superseded.
