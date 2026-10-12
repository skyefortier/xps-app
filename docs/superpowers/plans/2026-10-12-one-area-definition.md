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

- The switch (`scripts/q5_area_definitions.js`, 121 committed tabs, 530 components): a
  component's area moves by a median 0.007 %; area % by at most 0.034 pp; no 40 % warning flips.
- The note (`scripts/outside_window_census.js` → `docs/findings/q5-area/outside_window.json`): 8 of
  530 saved components, in 8 tabs — every "B-O" of the `B4C-UCl4` B 1s scans, centred at 193.00 eV,
  1.68 eV above the 175.42–191.32 eV window (exactly the components whose area moves 17–19 %).

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
