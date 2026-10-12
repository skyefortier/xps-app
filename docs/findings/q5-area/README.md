# Q5 — one area definition: what changes (measured 2026-10-12; corrected after Codex round 1)

**Corrected numbers, measured as the page shows them** (`scripts/q5_areas_on_load.py`: every committed
project loaded into the page in a real browser, each tab activated; the area each reader now shows —
the server's trapezoid on the one area grid — beside the page's old rectangle sum on the same grid →
`on_load.json`):

| Quantity (121 tabs, 530 components) | Change |
|---|---|
| A component's area | median 0.007 %, 90th percentile 0.024 %, max 0.20 % (6 components > 0.1 %: π→π* satellites near a window edge) |
| A component's area % | largest per tab: median 0.002 pp, max 0.008 pp |
| Auto-Fit's 40 % graphite warning | 44 Graphite models: 0 warn before, 0 now; no flip (nearest 45.2 %) |
| The "centred outside the window" note | **0 components** after loading |

The earlier table below read the RAW records and integrated on the saved fit grid. Older saves hold
that grid in the UNCORRECTED frame: the `B4C-UCl4` B 1s scans store 175.4–191.3 eV for peaks in the
charge-corrected 181.3–197.3 eV frame, so "B-O centred at 193.0 eV, outside the window, area −17 to
−19 %" was an artefact of the measurement — B-O is inside its window, and the page never showed it
that way. The same artefact gave the old maximum of 0.034 pp. (The pre-decision table is kept below
as the record of what was shown to the owner.)

## Pre-decision measurement (raw records; superseded above)


Sealed-fit v6 Q5 (owner 2026-10-11: measure first, show the numbers before switching). Today the
page's areas (Results, sidebar, Quantify, CSV/XLSX, Auto-Fit's 40 % graphite warning) are a
rectangle sum × the first energy step (`_peakArea`); the server's (`individual_peaks[].params.area`,
the alternatives' areas and fractions) are the trapezoid on the fit grid; the spectrum save writes a
sequential trapezoid. The proposal: the server's trapezoid for every reader.

Generator: `scripts/q5_area_definitions.js` (the page's own curves on the grid each reader
integrates on) → `areas.json`. Set: every committed saved fit — 121 tabs, 530 components (93 on
their saved fit grid, 28 on the ROI grid, every grid uniform to 2e-12).

| Quantity | Change if every reader used the server's trapezoid |
|---|---|
| A component's area | median 0.007 %, 90th percentile 0.03 %; 14 components > 0.1 %, 8 > 1 % |
| A component's area % (Results, Quantify within one tab) | largest per tab: median 0.002 pp, max 0.034 pp; no tab > 0.1 pp |
| Auto-Fit's 40 % graphite warning | 44 saved Graphite models: 0 warn today, 0 would warn; no flip (nearest 45.2 %) |
| On the 51 fresh Auto-Fit results of Q8 (refit, B) | page vs server area %: max 0.017 pp; the 7 warnings the same under both |
| The spectrum save's trapezoid vs the server's | identical on every component (max relative difference 0) |

The 8 components > 1 % are all "B-O" in `B4C-UCl4` B 1s scans: centred at 193.0 eV, OUTSIDE the
175.4–191.3 eV fit window, so only the tail is inside and the end sample carries 17–19 % of its
rectangle-sum area; the trapezoid weighs that sample by half (−17 % to −19 % of a component that is
0.1–0.2 % of the total). The next six (0.10–0.20 %) are π→π* satellites near the window's edge.
Nothing else moves by more than 0.1 %.
