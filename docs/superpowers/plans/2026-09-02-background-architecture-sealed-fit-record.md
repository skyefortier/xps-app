# Design memo v4 — Background architecture: the sealed fit record

Status: DESIGN ONLY — no code. Review history: v1/v2/v3 → Codex ×2 NO-GO
each round; every round endorsed the architecture direction and produced
converging completeness findings. Rounds 1–2 were call-site enumeration;
round 3's findings ([R3-A#]/[R3-B#]) are all instances of ONE class — "a
fit artifact consumed in a different FRAME or SETTINGS context than it was
produced in." v4 therefore restructures per the project's own pattern-gate
rule (docs: stop patching the set; make the class impossible): a sealed,
self-contained fit record with exactly one producer path, plus a single
dirty-marking funnel enforced by a structural test. Enumerations from all
three rounds become the migration checklist, not the correctness argument.

Measured symptom table (S1–S8) unchanged from v3 — see task1/task4 reports;
one addition from round 2: JS `linearBackground` also flat-holds a narrowed
window where the backend extrapolates (S8b).

## Part 1 — The sealed fit record (replaces v3's 1a/1b)

**`fitResult.sealed`** is created at exactly one point per producing flow
and is the ONLY thing any "fit" consumer may read:

```
sealed = {
  frame:      { ccShift },                 // the corrected frame the arrays live in
  be, counts, bgIntensity, bgSubtracted, fittedY,   // wholesale from backendResult
  peakResults: [ { id, name, shape, rsfKey, rsf,    // frontend metadata at fit time
                   params,                          // backend refined params + stderr
                   y } ],                           // backend individual_peaks[].y
  statistics, settingsSnapshot,             // bg method/window/n_avg used
}
```

- Arrays come wholesale from the backend response (rounded session grid —
  `uploadToBackend` rounds BE/intensity, so mixing frontend-precision `be`
  with backend arrays reintroduces a small S3). `peakResults` merges
  backend `individual_peaks[].{params,y}` with fit-time frontend metadata
  (name/shape/RSF) — the normalized per-peak export record round 3 asked
  for [R3-A3, R3-B4].
- **Producers (the only two):** (1) `runFit`'s backend path; (2)
  `applyAutoFitResult` — which seals AFTER its final programmatic charge
  correction, with `frame.ccShift` = the final shift and `be` + per-peak
  centers rigidly shifted by the final delta (exact — a cc change is a
  rigid BE relabeling; per-channel intensities, curves, widths, σ, and χ²
  are unchanged). This resolves the auto-fit frame contract both round-3
  runs rated BLOCKER [R3-A1, R3-B2]: the seal is always in the frame the
  UI shows at completion. The local-LM path seals its own record (its JS
  background IS what it subtracted — the invariant is "store what was
  fit," not "store Python output").
- **Consumers** (migration checklist, from rounds 1–3): `updatePlot`'s
  frozen-fit path incl. per-peak curves (post-fit, un-dirty: draw
  `peakResults[].y`, not evalPeakArray(state.peaks)) [R3-B3]; the
  Bkgrd-Sub view; `_computeRFactor`; `_doSaveSpectrum` / project save
  (persist the seal; `.spec.json` and project load restore it — the
  round-trip gap [R2-A4, R3-B4]); `exportResults` / `exportFitTable`
  (columns from `peakResults`, never live `state.peaks` — the cc-frame
  export invariant, now concrete) ; `exportFigure`; stack Path A (envelope
  AND per-peak curves from the source tab's seal) [R3-A2]; fit-history
  `_autoSnapshot` (snapshot = the seal; the history preview overlay draws
  a snapshot against its OWN be/bg/fittedY, not current plotBE/plotBG)
  [R3-B3]. Batch propagation and `runFitLocal` remain JS-background
  consumers by design (verified correct all three rounds); batch must
  additionally propagate `endpointAvg` (it is background-affecting)
  [R3-B5].

## Part 2 — The dirty funnel (replaces v3's 1c call-site map)

The class-killer for "some mutation path forgot to dirty the fit": all
background-affecting inputs are written through ONE funnel —
`_setBgInput(field, value)` for the DOM fields and `_mutateAnchors(fn)`
for anchors — and the funnel is the only place `fitResult.settingsDirty`
is set. Direct writes to bg-start/bg-end/bg-type/shirley-iter/
endpoint-avg/cc fields/manualAnchors outside the funnel are forbidden and
ENFORCED by a structural test that greps the source for rogue mutations —
the same mechanism that already guards evalPeak() callers in
tests/js/lineshape_parity.test.js (C) and has held for months. Known sites
to migrate (rounds 2–3, now a checklist, not the safety argument): the
five bg-field oninput handlers, `_onBgTypeChange`, `updateChargeCorrection`,
all four anchor mutations (add/remove/undo/clear), and `maxROI()` /
`autoSetROI()` — which rewrite bg-start/bg-end and were missed by every
hand enumeration until round 3 [R3-B1], which is exactly why the funnel +
structural test replaces enumeration.

Dirty semantics (unchanged from v3, now stated against the seal): dirty
mode draws the live JS preview background marked "preview (not fitted)";
the seal is retained untouched; stats/exports read the seal and carry an
"as fitted (settings changed since)" marker; the next fit replaces the
seal. Plain ROI typing stays non-dirtying (documented frozen-fit
invariant; it does not touch bg inputs — and if a future ROI helper does,
it must go through the funnel or the structural test fails).

## Part 3 — Window fix (unchanged; verified three rounds)

`_bgWindowIndices(be)`: `lo = min`, `hi = max`, send `(lo, hi+1)`;
blank/NaN endpoint → `(0, len)`; used by BOTH request builders (runFit +
auto-fit). Backend contract untouched → autofit/parity.py + battery
fixtures byte-stable. Helper unit tests: NaN endpoints, one-point ROI,
window outside ROI. Ship note: windowed-method fit numbers move by the S2
magnitudes (χ²ᵣ +0.03, centers ±10 meV, areas ±3.2%, fractions ±0.9 pp).

## Part 4 — Twin alignment + pinned parity (unchanged)

S4 (shirley signal clamp), S5 (smart clamp target), S8 (BE-based linear +
narrowed-window extrapolation semantics), JS convergence semantics (tol
1e-6 incl. smart_exp), committed parity suite from the Task-4 harness.

## Part 5 — shirley-iter removal (unchanged; sweep incl. batch_propagation.js)

Gated on Part 4's convergence semantics; decoupled from shirley_linear if
Q4 chooses de-listing. Sweep: DOM control, computeBackground deref,
_clampShirleyIter, _captureUI/_restoreUI, _onBgTypeChange, save metadata,
serializers accept-and-ignore, computeBackgroundCore accepts-and-ignores,
static/js/batch_propagation.js + its tests.

## Part 6 — shirley_linear (unchanged): scientific review first; user picks
interim (align JS→Python with ship note, or de-list until reviewed).

## Part 7 — /api/background shared constructor (contract completed)

Extract run_fit's background construction; method-specific contract:
integral → compute on [i0:i1), flat-hold outside; linear → extrapolate
across full ROI; manual → ignores window, `manual_bg` with ≥2 anchors
interpolates, and `manual_bg` empty/absent falls back to linear exactly as
/api/fit does today (documented, not a 400 — keeps the two endpoints
identical) [R3-B6]; none/flat → zeros. Response carries the full-ROI
embedded array.

## Ship order (Unit 1 split per review [R3-B6])

1a. **Seal + producers** (runFit, auto-fit incl. frame shift, local-LM),
    persistence round-trip (.spec.json + project save/load).
1b. **Consumer migration** to the seal (chart curves, sub view, R-factor,
    saves, all exports, stack Path A, history preview).
1c. **Window fix** (`_bgWindowIndices`, both builders).
1d. **Dirty funnel + structural test.**
    (1a→1d are one branch, separately committed; 1c is independent and
    could ship first if a smaller first unit is preferred.)
2.  shirley_linear decision (gated on Q4 choice).
3.  Twin alignment + committed parity suite.
4.  shirley-iter removal.
5.  /api/background shared constructor.

Verification per unit as in v3, plus: a structural test for the dirty
funnel; an auto-fit seal test (frame.ccShift equals the final displayed
shift and sealed graphite center = 284.50 exactly); battery suite
byte-stability run for 1c.

NOT in scope: DSG_LA/LACX lineshape parity (own branches; DSG_LA GO×2),
LACX kernel decision (parked pending CasaXPS empirical check).

## Round-4 amendments (GO ×2 — fold into implementation as written)

Round 4 approved the sealed-record architecture; both runs attached
amendments that are part of the approved design:

1. **Precise seal transform for the auto-fit final-cc shift** [R4-A1]:
   shift by the final delta: `sealed.be`, peak CENTER values (and any
   center-like bounds), `settingsSnapshot.bgStart/bgEnd`, ROI/range
   labels, and anchor x if captured. Do NOT shift: counts, bgIntensity,
   bgSubtracted, fittedY, per-peak y, amplitudes, areas, FWHM/width
   params, center stderr/σ, χ², RMSE, R-factor. `settingsSnapshot` is
   defined as "settings expressed in the sealed frame."
2. **Non-dirty hydration writer** [R4-A2, R4-B3]: project/spec load, tab
   activation, undo, and history restore go through the SAME allowlisted
   writer with `{dirty: false}` (`_writeBgInput(field, value, opts)`) —
   no raw restore writes "outside" the funnel, so a future mutator cannot
   hide behind the restore exception.
3. **Allowlist-based structural guard** [R4-A3]: the grep test guards the
   named write surfaces — the bg DOM fields, `tab.ui` bg fields,
   `state.ccShift`, `manualAnchors` — not just literal element ids, so
   dynamic helpers/dispatchEvent paths cannot evade it.
4. **Legacy adapter** [R4-A5, R4-B5]: one `normalizeFitResult(raw, peaks,
   ui, ccShift)` at every load/restore boundary converts old top-level
   fitResult shapes to a seal; old saves lacking peakResults become a
   flagged partial/"legacy reconstructed" seal, never silently
   authoritative.
5. **Local-LM seal contract** [R4-A4, R4-B4]: stores exactly what local
   LM fit (JS bg, JS per-peak y, final params, local stats; stderr
   explicitly absent); the parity suite must not expect a local-LM seal
   to match Python background output.
6. **Ship order confirmed**: 1a–1d one branch (mixed sealed/unsealed
   consumers are a transient hazard); 1c separable and may land first
   with its numeric-shift expectations documented.

## Round-5 amendment (2026-09-03) — Part 3 justified and made exact (Condition 2)

Approval of this memo carried two conditions. Condition 1: unit 1c ships
alone and first, as its own branch and its own deploy, because it is the
only unit that moves reported numbers. Condition 2: the window direction
is justified here, in plain terms, before 1c is built. This section is that
justification. Everything in it is reproducible with
`scripts/bg_window_pointsets.py` and `scripts/bg_window_worked_example.py`
against the committed `.proj.zip` projects.

### The statement

The user draws a background window by typing two binding energies
(bg-start, bg-end). The on-screen preview (`computeBackgroundCore`) builds
its background from every grid point with lo ≤ BE ≤ hi — the last point the
user selected is in the window. The fit request converts each typed bound
to the nearest grid index and the backend slices `counts[i0:i1]` —
Python end-exclusive — so the fit anchors its background one grid point
INSIDE the window the user drew, on a raw single-channel value the user
never chose (endpointAvg = 1 is the default). End-exclusive slicing
silently drops the last point they selected; inclusive honours the stated
intent. That is the whole direction argument. Nothing about it depends on
which background algorithm is in use.

### The point-set contract (what 1c actually changes)

v4 said "send `(lo, hi+1)`" and left the index rule implicit. Measured
across all 166 fitted tabs in the seven committed `.proj.zip` projects,
the implicit rule matters:

| rule for the request | tabs where fit point set == preview point set |
|---|---|
| today: nearest grid index per bound, end-exclusive | 15 / 166 |
| v4 as written: nearest index, `hi+1` | 151 / 166 |
| **1c: inside-range (lo ≤ BE ≤ hi), `hi+1`** | **166 / 166** |

The 15 tabs where "nearest, hi+1" still disagrees with the preview are
all tabs whose typed bound falls off-grid *inside* the ROI: the nearest
grid point lies just OUTSIDE the typed bound (typed 279.2, grid 279.16)
and "nearest" would pull it in, while the preview excludes it. Inside-range
is also the rule `getROIData` already uses for the ROI itself, so 1c makes
the three windows in the app (ROI, preview background, fitted background)
obey one definition: a typed bound is an inclusive limit; no point outside
it is ever used; every grid point inside it is.

Concretely, 1c adds one helper and routes three callers through it:

```
_bgWindowIndices(be, bgStart, bgEnd) → { i0, i1 }   // inclusive indices
  lo = min(start, end), hi = max(start, end)
  i0 = first index with lo ≤ be[i] ≤ hi, i1 = last such index
  blank/NaN bound, or fewer than 2 points in range → { 0, be.length − 1 }
```

- `runFit` backend request: `start_idx: i0, end_idx: i1 + 1`
- `runAutoFitC1sGraphite` request: same
- `computeBackgroundCore`: takes `i0`/`i1` from the same helper (its
  current inline scan is the same rule; sharing the function makes the
  agreement structural rather than coincidental)

The backend contract is untouched (`end_idx` remains Python-exclusive, as
`/api/fit` and `/api/background` both document), so `autofit/parity.py`
and the battery fixtures stay byte-stable. `_parse_int` already clamps
`end_idx` to `[0, len]`, so `i1 + 1 == len` is legal.

### Worked example on real data

Committed `docs/autofit/test_data/1-GTA UCl4-graphite one set of U
doublets.proj.zip`, tab `U4f Scan_0`: smart background, endpointAvg 1,
bg window 405.1 / 370.1 (= the ROI bounds, the default set by maxROI),
350-point descending grid at 0.1 eV, stored model 2 × LACX + 2 × Voigt
refit from its stored parameters. Both `least_squares` and `leastsq` give
the same numbers to 4 decimals.

| | points in the background window | last (low-BE) point | counts at that anchor |
|---|---|---|---|
| today | 349 — 405.06 … 370.26 | 370.26 | 5517 |
| after 1c | 350 — 405.06 … 370.16 | 370.16 | 5425 |
| preview | 350 — identical to "after 1c" | | |

The one point that moves in is the last point of the user's window. Its
intensity differs from its neighbour by 92 counts, and because Smart/Shirley
scale the whole curve between the two anchor levels, the fitted background
shifts by 92.4 counts at the low-BE edge tapering to 0.0 at the high-BE
edge — exactly the Task 1 residual signature (max at the low-BE ROI edge,
~0 at the high-BE edge).

| quantity | today | after 1c | shift |
|---|---|---|---|
| χ²ᵣ | 1.8294 | 1.9317 | +0.10 |
| U 4f₇/₂ centre | 379.574 | 379.590 | +16.5 meV |
| U 4f₅/₂ centre | 390.474 | 390.490 | +16.5 meV |
| U 4f₇/₂ area | 44 164 | 44 360 | +0.44 % |
| U 4f₅/₂ area | 28 126 | 28 279 | +0.54 % |
| Satellite 1 area | 5 450 | 5 679 | +4.2 % |
| Satellite 2 area | 3 114 | 3 164 | +1.6 % |
| atomic fractions | | | within ±0.23 pp |

Second example, same project, tab `C1s Scan` (shirley; window 298.2 / 279.2
typed INSIDE the ROI 279.0–298.5). The typed 279.2 is off-grid; the nearest
grid point is 279.16, outside the bound. Today's request (nearest, exclusive)
ends the window at 279.26; 1c's inside-range rule also ends it at 279.26 —
this fit is UNCHANGED by 1c, and equals the preview. Had 1c used "nearest,
hi+1" it would have pulled 279.16 in (2794 counts vs 2912 one channel up):
χ²ᵣ 4.97 → 3.32 and the graphite fraction +6.2 pp — a movement the user did
not ask for and the preview never showed. This is why the rule is stated
explicitly above.

### Ship-note magnitudes (supersede v4's Part 3 line)

v4 quoted χ²ᵣ +0.03, centres ±10 meV, areas ±3.2 %, fractions ±0.9 pp; the
measurement behind those figures is not archived in the repo. The worked
example above is the archived, reproducible basis: the size of the shift is
set by the intensity step between the two candidate anchor channels and by
how strongly the model leans on the background near that edge. State it as
a mechanism plus a measured range — χ²ᵣ up to ~0.1, centres up to ~20 meV,
areas up to ~4 % (satellites move more than main lines), atomic fractions
under 1 pp — not as a single number. Which fits move: every fit whose
dropped bound maps to a grid point inside the typed range, which is the
default configuration (window = ROI bounds); 151 of the 166 committed tabs.
The C1s-style off-grid-inside-ROI case (15 / 166) does not move.

The C1s example also shows, incidentally, how much a single-channel anchor
can matter when endpointAvg = 1 (graphite fraction ±6 pp from one channel).
That is an argument for endpoint averaging in the user guidance, not a
change for 1c.

### Known divergence left in place (logged, not fixed in 1c)

`autofit/reference.py::bg_indices` reconstructs stored expert fits for the
parity gates using the OLD frontend rule (nearest index; `parity.py` then
slices end-exclusive). It must stay that way in 1c: the committed fixtures
were produced by the old frontend and are required to stay byte-stable.
Expert fits saved AFTER 1c will have been made with the inclusive window,
and `reference.py` will reconstruct them one point short. The durable fix
is unit 1a's `settingsSnapshot` carrying the actual indices the fit used,
so reconstruction never re-derives them. Until then, any new parity
fixture must be generated with that caveat recorded.
