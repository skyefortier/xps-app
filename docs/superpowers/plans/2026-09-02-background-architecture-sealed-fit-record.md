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
`scripts/bg_window_pointsets.py` (prints the three-rule comparison table
below as its last line) and `scripts/bg_window_worked_example.py` (refits
at the exact precision `uploadToBackend` sends: BE to 4 decimals, counts
to 2) against the committed `.proj.zip` projects.

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
| today: nearest grid index per bound, end-exclusive | 12 / 166 |
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

Two contract edges, raised by Codex round 1 and documented on the helper:
the window is the contiguous span from the first to the last in-range
index, exact on a monotonic grid — which `createTab` guarantees by sorting
descending and which every project this app has written carries; a
hand-edited non-monotonic `rawBE` would make the span include
out-of-window rows, with preview and request still agreeing. And the
indices are computed on the frontend grid before `uploadToBackend` rounds
BE to 4 decimals; the backend only applies them to that same-length,
same-order session grid, so rounding cannot change which rows are used.

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
| χ²ᵣ | 1.8293 | 1.9317 | +0.10 |
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
default configuration (window = ROI bounds); 154 of the 166 committed tabs
move. The 12 tabs whose point set was already the preview's — the
C1s-style off-grid-inside-ROI case — do not move at all.

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
and `reference.py` will reconstruct them one point short (its module
docstring now says so). The durable fix
is unit 1a's `settingsSnapshot` carrying the actual indices the fit used,
so reconstruction never re-derives them. Until then, any new parity
fixture must be generated with that caveat recorded.

## Round-6 note (2026-09-22, owner instruction) — binding by key is this memo's principle, and the seal must absorb it

Two units shipped before 1a–1d carry their own "does this evidence still
describe the fit?" mechanism, and both are local instances of Part 1's
invariant ("store what was fit", read only that):

- **Scattered starts (2026-09-22):** `fitResult.startsModelKey` — the
  JSON of every peak field the request reads plus the fit context
  (background type and window, endpoint averaging, Shirley iterations,
  ROI, manual anchors, charge shift) — taken after the result is applied.
  `_startsIfCurrent(fr, key)` compares it with `_startsLiveKey()` (active
  tab) or `_startsRecordKey(t)` (record) at every read; a mismatch means
  "no longer applies": nothing shown, applied, saved or exported. `runFit`
  also captures that key before its first await and discards a result
  whose model or context was edited while it ran.
- **Unsupported components (2026-09-22):** `p.support.fitKey`, the same
  key, on each peak's verdict; `_isUnsupported(p, key)` compares at every
  read; Auto-Fit re-stamps after its own locks and charge refinement
  (exactly Part 1's "seal AFTER the final programmatic charge correction").

Why it was done this way: hand invalidation in edit handlers was tried
first and lost the review rounds (a rename path deleted evidence, a lock
path missed it, an in-flight edit stamped a fresh key onto a mismatched
model). Comparison against a key derived from what the fit actually
consumed cannot forget an edit path. That is the seal's argument, made
twice more in the small.

**Instruction for 1a–1d:** absorb both into the seal; do not leave a second,
narrower binding mechanism beside it. Concretely:

1. `settingsSnapshot` + `peakResults` + `frame` ARE the key. The seal's
   identity is the request it was produced from; `_startsLiveKey()` and
   `_STARTS_MODEL_FIELDS` / `_STARTS_UI_FIELDS` become the definition of
   "the live state matches the seal" and should move into the seal's own
   `isCurrent()` (one function, one field list) rather than remain a
   parallel list that can drift from `settingsSnapshot`.
2. `fitResult.starts`, `fitResult.chosenAlternative` and each peak's
   `support` are seal contents (they were produced from the same request
   as the arrays), so they inherit the seal's currency test and its
   persistence, and the separate `startsModelKey` / `support.fitKey`
   fields are retired at migration.
3. The in-flight guard in `runFit` (key captured before the first await,
   result discarded if the live key changed) is the seal's producer-side
   rule: a seal is only ever created for the request that was sent.
4. Consumers already migrated to "read only the current evidence" — the
   starts panel, `_isUnsupported` at 15 sites, the CSV/XLSX status column,
   `_refreshStartsEvidence`'s per-consumer comparison — are the first
   consumers on the Part 1 checklist to switch to the seal, and their tests
   (`tests/js/scattered_starts.test.js`, `tests/js/unsupported_components.test.js`)
   are the acceptance tests for that switch: identical behaviour, one
   mechanism.
5. What must survive the absorption: cosmetic fields (name, colour,
   visibility) never invalidate; the sidebar is patched in place, never
   re-rendered under a typing student; each consumer is compared with its
   own rendering when currency changes.

## Round-7 note (2026-09-26, owner instruction) — legacy verification on load belongs in the seal's legacy adapter

Unit F1 (`docs/superpowers/plans/2026-09-25-f1-stale-statistics.md`) binds
χ², σ, RMSE, R and the stored fitted curve to their fit by the step (b) key.
A result saved before that key existed has none, so it reads `unverified`
("cannot be confirmed … Run Fit to confirm") — on EVERY tab of EVERY
project saved before 2026-09-26 (all 20 tabs of the committed UCl4-graphite
project). F1 deliberately does not try to recover those; the seal does.

The seal's legacy adapter, on load of a result with no key: recompute the
envelope from the SAVED peaks on the SAVED fit grid (`fitResult.be`) with the
saved background (`fitResult.bgIntensity`) and compare it with the SAVED
fitted curve (`fitResult.fittedY`). Where they agree, the statistics
demonstrably belong to that model, and the result is sealed with the loaded
model's key and reads `current`; where they disagree, or anything needed is
missing (no `fittedY`, no `be`, an older save's grid), it stays `unverified`.
Open questions for that unit, not decided here: the agreement criterion
(the design rule on data-scaled thresholds applies — prefer a comparison
with no magnitude tolerance, e.g. the same evaluator on the same grid
reproducing the saved curve to the precision the save rounded it to:
project saves round intensities to 6 significant figures); whether the
context half of the key (background type and window, ROI, anchors, charge
shift) can be taken from the saved `ui` at all, since the saved controls
are not proof of the fit's context; and local-engine results, which saved
no `fittedY`.


---

# v5 (2026-10-10, owner instruction) — the sealed fit record as a regeneration PROOF — revision 2

Status: DESIGN ONLY — no code. Revision 2 answers the design-review gate's round 1 (NO-GO ×2,
`docs/autofit/codex/sealed_fit_v5_design_r1_verdict_run{A,B}.md`): revision 1 called the
starting request and the fitted model by one name, left the statistics outside its proof, used a
summation bound as an evaluator bound, transformed the replay frame, and made a different
re-run outcome read as stale. Supersedes v4 Parts 1–2 and the Round-6/7 notes where they
conflict; v4 Parts 3–7 shipped or were overtaken (V5.1).

Owner, 2026-10-10: "a saved fit carries everything needed to regenerate it and prove it
current — inputs, settings, seed, software version, background verdict, certificate verdict —
and a loaded fit is current only if that proof checks." Every statement about the CURRENT code
is **VERIFIED** (`path:line` on main 90651e6) or **HYPOTHESIS**. IH = templates/index.html,
F = fitting.py, A = app.py, P = parser.py.

## V5.1 What shipped since v4

| piece | what it is today | VERIFIED at |
|---|---|---|
| window fix (Part 3, 1c) | inclusive `_bgWindowIndices` shared by preview and requests; the request converts its inclusive end to exclusive | IH:5125, IH:8171, IH:8734-8752 |
| twins + parity (Part 4) | page backgrounds bit-identical to fitting.py ON THE TESTED CASES (five integral methods at averaging 1 / 3 / 10, both directions; linear and manual in their own tests) — evidence, not a universal proof | `tests/js/background_parity.test.js:82-94,164`; `tests/js/manual_background_statement.test.js:53` |
| Shirley iterations (Part 5) | hidden and NUMERICALLY ignored; still read by the UI capture, the key and the serialisers | IH:3851, IH:5187, IH:8351, IH:8375 |
| shirley_linear (Part 6) | off the menu; loads | IH:3868 |
| the fit key | `startsModelKey` = JSON `{p, u, s, a}`: `_STARTS_MODEL_FIELDS`, `_STARTS_UI_FIELDS`, charge shift, anchors; stamped AFTER the result is applied | IH:8347-8358; runFit IH:8854, runFitLocal IH:9413, Auto-Fit IH:7803, `_restampSupport` IH:7666 |
| comparison | `_sameFitKey` through each field's reader (`_fitKeyCanon`); defaults are NOT folded in | IH:8367-8393 |
| in-flight discard | key captured before the first await; a result is discarded if the live key changed (it inherits the key's omissions) | IH:8747, IH:8789, IH:8831; Auto-Fit IH:8181, 8214, 8244 |
| statistics states (F1) | none / stale / unverified (no key) / current | IH:8418-8426 |
| certificate (A2) | Trust-Region restarts until the RELATIVE improvement < scipy's ftol, ≤ 50; `certificate {certified, restarts, moved, optimiser_flag, centre_moves, largest_centre_move}`; DE / basinhopping `null` | F:1868-1870, F:1873-1917 (relative: F:1898-1900), F:2815, F:2825-2831 |
| scattered starts | the request seed's third stream; `starts` counts and alternatives | F:2482-2483, F:2044-2082, F:2152-2161; page IH:8744, IH:8779 |
| background verdict | `background_certificate` → `{converged, residual, reason}`; `BackgroundNotConverged` → HTTP 422; page twins | F:1016, F:1286-1287, A:153-156, IH:4729, IH:5045-5068, IH:5178-5185 |
| seed v2 | SHA-256 tag `xps-fit-seed-v2` over energies, counts, lineshapes, parameter roles by position, fit_kws, solver, n_perturb, the background by effect; `random_seed` | F:1951-2024, F:2810 |
| full-precision upload | `String(v)`; `_exact_columns` reads it back; the parser still drops non-finite rows; `uploadFull` | IH:6861-6862, P:159-195, IH:8850 |
| legacy restore rule | the implied background against today's on the fit's samples; current needs the background within `BG_RESTORE_REL · scale + BG_REL_TOL · envScale` AND the key and Voigt checks (`_statsState`); a fit without `startsModelKey` is never current | IH:9956-10087 (tolerance IH:10058, rule IH:10053), IH:8420-8422 |
| support verdicts | bound by `p.support.fitKey` | IH:7637-7658, IH:6988-6999 |
| envelope-identity tests | NOT ON MAIN: branch `test-envelope-identity`, under review | — |

## V5.2 The gap between today and the goal (VERIFIED unless marked)

1. **Seed unsaved, unreachable over HTTP.** `random_seed` (F:2810) is read nowhere on the page;
   `backendResult` is memory-only (IH:8850); the caller seed exists in `run_fit` (F:2331-2338,
   F:2472-2473) but A:135 passes only `fit_kws={"method": fit_method}`.
2. **The request is not recorded.** The method is read at request time (IH:8750; Auto-Fit
   IH:8173) and is in neither key list (IH:8347-8351) nor `_captureUI` (IH:3846); `n_perturb`,
   `n_starts`, `require_component`, Auto-Fit's `_afCenter*` / `_afFwhm*` overlays (IH:8183-8188)
   are not in the key; and the key is taken AFTER the result is applied, so it describes the
   applied model, never the starting request (IH:8854; CLAUDE.md "What seeding buys").
3. **The certificate verdict is not persisted** (only a > 1 eV move: IH:8853, IH:8546-8549); the
   full one lives in the memory-only `backendResult`.
4. **No software or environment identity** in F, A, P, IH (grep: NOT FOUND) or the response
   (F:2791-2816); `requirements.txt:9-11` allows NumPy / SciPy / lmfit to change under one app
   commit, and `CERTIFY_FTOL` is read from the installed SciPy (F:1868).
5. **The successful background verdict is not stored**; the spectrum save writes
   `backgroundFailure: null` on success (IH:11779-11800); `fitResult` holds the page's own
   `bgIntensity` (IH:8849-8855), not the server's `background_y`.
6. **The project save rounds** `be` (4 dp), `bgIntensity` and `bgSubtracted` (6 significant
   figures) and keeps `fittedY` at full precision (IH:11826-11827, IH:11852-11860); the
   spectrum save keeps full precision.
7. **Producers differ.** Auto-Fit: no `starts`, `certificateMove`, `engine` (IH:7795-7804); the
   local engine: deterministic, no seed, its coordinate certificate's count returned (IH:9429)
   but not stored; Batch Fit is the local engine (IH:13747).
8. **Two loaders.** The spectrum loader assigns `chi`, `chiReduced`, `rmse` directly and copies
   selected metadata and `rFactor` only when truthy (IH:12104-12113); the project loader takes
   the record verbatim (IH:12290); `statisticsState` is read by the spectrum loader only
   (IH:12112-12120); `statisticsNote` is written (IH:8450) and never read.
9. **Readers that bypass any one accessor**: the chart's frozen-fit path (IH:10940-10976), the
   uncertainty display from `backendResult` (IH:9461-9465), `_validateUncertainties`
   (IH:13172), `_computeRFactor`'s fallback to live `state.peaks` (IH:13073), the history's
   shallow copies (IH:15517, IH:15665), the alternative preview's `_historyPreview.altKey`
   (IH:8501).

## V5.3 Three records, three questions

The owner's sentence asks three different things, and round 1 showed that one record answering
all three gives each a wrong answer. `fitResult.sealed` therefore has three parts, each
immutable once written, each with one purpose:

**R — the replay record: what was computed.** Exactly the inputs the server's `run_fit`
received, in ITS frame, never transformed:
- the parsed session arrays as `run_fit` saw them: energies (already charge-corrected by the
  page, `_roiSelect` IH:5513-5525: `rawBE[i] − ccShift`), counts, in order, inline (a digest
  cannot regenerate) — plus the index list `_roiSelect` returned into the tab's raw arrays;
- every peak spec AS SENT, starting values included, with Auto-Fit's overlays (IH:8183-8188) and
  links (`constrain_to`, splitting, ratio) — the exact JSON the request carried;
- the background spec as sent: method, `start_idx`, exclusive `end_idx`, `endpoint_avg` as
  parsed, every manual anchor pair (A:79-88);
- method, `n_perturb`, `n_starts`, `require_component`, `charge_shift_ev` (0 over HTTP, A:134 —
  recorded so a replay never applies the shift twice), the seed (`random_seed` returned, or the
  caller's), and the RESOLVED solver configuration;
- the environment: app version and commit (with a dirty flag), the page build's own hash, and
  the NumPy / SciPy / lmfit versions (HYPOTHESIS: obtainable at server start; the page hash from
  the served template).
- For the local engine (and Batch Fit) R is its own recipe — the background and net arrays it
  was given, the peak objects as it read them, `maxIterations`, LA's held `caM` (IH:9057-9080,
  IH:9111-9117) — never a server request.

**O — the output: what the computation returned.** The whole response, verbatim and full
precision: `success`, `message`, `energy`, `counts`, `fitted_y`, `background_y`, `residuals`,
`individual_peaks` (`id`, `shape`, `params` with stderr and bounds, `y`, `support`),
`statistics`, `certificate`, `starts` (with the alternatives' parameter sets), `required`,
`random_seed`, `charge_shift_applied` (F:2791-2816), plus NEW `background_verdict
{method, converged, residual, reason}` (additive). One copy: nothing else stores a
certificate.

**D — the display binding: what the page shows from it.** The model as applied (each peak's
fields the display and the next request read — `_STARTS_MODEL_FIELDS` — after
`applyBackendResult`), the context (the `_STARTS_UI_FIELDS`, anchors, ccShift), the DISPLAY
transform from R's frame to the shown frame (identity, or Auto-Fit's final charge shift
recorded as a transform — round 1 run A: a rigid shift is not bit-invariant, so R is never
rewritten), `chosenAlternative`, the engine, and `reportable`. D replaces `startsModelKey`;
there is one canonicalisation (`_fitKeyCanon`'s readers) and no second key.

The fit method is a setting of the NEXT fit: changing the dropdown does not change what the
statistics describe (they describe the fit R records, made with R's method). Revision 1's gap 2
"changing the method keeps a result current" is therefore correct behaviour, now recorded:
the shown result names its method from R.

## V5.4 The states, each with its own proof

**DISPLAY-CURRENT — the statistics shown describe what is shown.** All of:
1. *O is internally consistent* — finite; lengths and `energy` match R's energies exactly;
   component ids and shapes match R's specs one to one; `fitted_y = background_y + Σ y` within
   the derived summation bound (`tests/envelope_identity.py`, its FFT term for DS+G);
   `residuals = counts − fitted_y` exactly as the server forms it; and the STATISTICS RECOMPUTED
   from O's own arrays agree: χ² = Σ ((counts − background − fitted_sub) · w)², w =
   1/√max(counts, 1) (F:2433-2434), dof = n_data − n_free, χ²ᵣ, R = Σ|y_sub − fitted_sub| /
   Σ|y_sub| (F:2776-2777), RMSE, each within the derived summation bound for its own sum (γ_n of
   its terms; HYPOTHESIS: n_free recoverable from O's `params[].vary` / `expr` — to verify in
   1b). The uncertainties (σ) are NOT re-derivable from O; they are reported as the server's
   for R (stated limit; `tests/fit_equality.py` does not compare them either).
2. *The fit was accepted* — `O.success === true` (the page's rule, IH:8812); a local server
   method's `O.certificate.certified`; for DE / basinhopping their own verdict is `success`
   (F:2780-2788); `O.background_verdict.converged`.
3. *The page shows O* — D's applied model is exactly what `applyBackendResult` produces from O
   (re-run it on O and compare exactly); the live model and context equal D exactly (the same
   canonicalisation); and while DISPLAY-CURRENT the chart draws O's own component curves and
   envelope (`individual_peaks[].y`, `fitted_y`, `background_y`) transformed by D — v4 Part 1's
   rule — so no page-versus-server evaluator bound is needed (round 1: a Gaussian differs by
   up to 85× a pointwise 12u bound in a far tail; the page's evaluators are for drawing an
   EDITED model, which is not current anyway).
4. *The background is today's* — the page's certified background for R's own arrays and spec
   (through ONE adapter from R's indices / anchors to the twin's inputs) equals `O.background_y`
   exactly. HYPOTHESIS (to be proven in 1b on the committed set and the parity cases, not
   assumed): the twins are bit-identical for every R the app can produce. Where it does not hold
   — a different background arithmetic in a later version — the state is STALE "background
   changed" with the size (today's `_bgStaleNote`), the same as the restore rule.
If any step fails: STALE (F1's rules, the failed step named) or, if R / O are unusable,
PEAKS-ONLY.

**PROVENANCE-COMPLETE** — R carries every field above with an environment. A fit can be
display-current without it (a local fit, or a server that did not report its environment); the
page says which.

**REPLAY-CHECKED (on demand, never automatic, never a currency verdict)** — "Re-run this fit":
the page sends R (with its seed, a new validated HTTP field mapping to `fit_kws.fit_kws.seed`)
and reports one of: *reproduced within rounding* (`tests/fit_equality.py`'s same-minimum rules,
ported, with its stated exclusions: σ and certificate details); *a re-run reached a different
solution* (the fit is not unique — the scattered-starts line's message, owner 2026-09-21: an
accepted, disclosed property, NOT stale); *different software* (R's environment ≠ the
server's: the outcome is reported as such). The fraction of the 202 committed targets that
reproduce under this comparator is UNMEASURED — HYPOTHESIS until measured before 1e.

Tolerances, named: steps 1 and the identity use DERIVED rounding bounds (summation γ_n, the FFT
term), steps 3–4 are exact, replay uses `fit_equality`'s documented relative rules — a
same-minimum comparison, used only for REPLAY-CHECKED, never for currency.

## V5.5 Legacy saves

- **No seal, no key** (every save before 2026-09-25; all 121 committed fits — VERIFIED: no
  `startsModelKey` in the seven committed project archives): never current (owner
  2026-10-05); the restore rule stays as the adapter (stale with the reconstructed difference,
  or peaks only).
- **Key, no seal** (saves 2026-09-25 → the seal): RECOMMENDATION (owner Q1): never current
  under the new contract — they lack R (the starting request, method, seed, environment) and O
  (the server's arrays); saves before 2026-09-29 also predate the certificate. Their own curves
  and the restore rule's explanation stay. This TIGHTENS the shipped keyed restore rule; its
  tests change accordingly (they cannot all stay unchanged).
- **Sealed:** V5.4.

## V5.6 Migration: one accessor, everything else a view

`sealedState(fr, live)` → DISPLAY-CURRENT / STALE(step) / PEAKS-ONLY, and the only reader of R, O
and D. Every consumer below switches in the same release (round 1: a mixed release can show one
result with another's statistics, lose σ, or drop the seal on re-save):
the chart (IH:10940-10976), Results / header / R panel, the uncertainty display (IH:9461-9465)
and `_validateUncertainties` (IH:13172), `_computeRFactor` (its live-peaks fallback IH:13073
goes), CSV / XLSX / TSV / figure exports, Quantify, stack Paths A / A2 / B, history snapshots
(deep copies of the seal), the alternatives panel and preview (`_historyPreview.altKey`
IH:8501), the support badges, the certificate notice, both saves and both loaders (one
function; the seal persisted losslessly).
Retired (become views of the seal, or live only inside the legacy adapter, never authorising a
seal): `startsModelKey`, `restoredKey`, `loadKey`, `p.support.fitKey`, `certificateMove`,
`backgroundStale`, `voigtStale`, `restoredStale`, `statisticsState`, `statisticsNote`,
`_preFit`, `backendResult`, `beShift`, `beExact`, `uploadFull`, `_modelBe`, `fitCounts`, and
`p._backendParams` outside the legacy Voigt reading (IH:6995, IH:10423). Kept: the operation
tokens (`_fitOpCurrent` and friends) — they decide which operation may apply a result, a
different question.

## V5.7 Owner decisions requested

- Q1 (V5.5): keyed-but-unsealed saves never current (recommended)?
- Q2: REPLAY-CHECKED on demand only (recommended), or also automatic on load (one server fit
  per tab)?
- Q3: persist the alternatives' parameter sets in O (the panel survives a reload; recommended)
  or counts only as today?
- Q4: environment identity — is "different software" shown as a provenance note only
  (recommended), or does it withhold the statistics?

## V5.8 Ship order (after approval)

1a. Server: `background_verdict`, the environment in the response, the seed over HTTP
    (validated). Additive; tests.
1b. Prove V5.4 step 4's HYPOTHESIS (twins bit-identical for every R the app produces) on the
    committed set and the parity cases; measure the seal's size; measure REPLAY reproduction on
    the 202 targets.
1c. Producers write R / O / D (runFit, Use this solution, Auto-Fit, local, Batch); both saves and
    both loaders persist and read them losslessly; `sealedState` and every V5.6 consumer switch
    together; the legacy adapter routes unsealed saves. One branch, one release.
1d. REPLAY-CHECKED (Q2).
Each with Codex ×2.

## V5.9 Gate status after round 2 (NO-GO ×2) — STOPPED for the owner's review

Round 2 (`sealed_fit_v5_design_r2_verdict_run{A,B}.md`) confirms revision 2 resolved round 1's
structure: R / O / D separated, R never transformed, acceptance (`success`) required, replay
kept out of currency, the false VERIFIED claims corrected, legacy policy consistent, the
migration list complete for round 1's additions. Both runs independently found the SAME
remaining defects. They are open; the proposed resolution of each is listed for the owner's
review, not yet written into V5.3–V5.8:

| # | finding (both runs) | proposed resolution |
|---|---|---|
| G1 BLOCKER | D cannot be "exactly `applyBackendResult(O)`": it mutates live peaks and honours locks, so re-applying to D is a fixed point (run B's probe: O centre 10, displayed 99 locked — unchanged) | a PURE display projection `project(O, R, producer)` with explicit inputs (O's values, R's spec roles and links, the producer's finalisation — Auto-Fit's charge shift, ROI reselection and centre locks as recorded steps); D is compared with `project(...)`, and the displayed numbers with O directly, independently of locks |
| G2 BLOCKER | the records are not bound to each other: `O.counts = R.counts` is never required (a valid O for another spectrum on the same grid passes); R→D context, R's sample indices → the displayed observations, `R.seed = O.random_seed`, R / O environment overlap | explicit cross-record checks: O.energy and O.counts equal R's arrays exactly; R's index list into the tab's raw arrays equals the samples the chart shows as data; D's context maps to R's background spec and ROI through the one adapter; seed equality; ONE environment record (in R) |
| G3 BLOCKER | drawing O's curves removed the parameter ↔ curve check: an O parameter can change while its curve stays | each O component's `y` must equal the SERVER's evaluator at O's params on O's energies — re-evaluated by the server (an additive `verify` call in 1a: same code, same library, exact) or recorded as a server-side self-check in O; areas and support statistics recomputed (support from the arrays and parameter roles, F:2185) or attributed as the server's |
| G4 MAJOR | the statistics contract: the server's residual is `(counts − background) − fitted_sub` (F:2689, F:2774), not `counts − fitted_y` (run B's probe: 0.09999999999945 vs 0.10000000000036); `fitted_sub` is not retained; lmfit floors χ² at 1e-250·n (after χ²ᵣ); no RMSE field; areas: server trapezoid (F:2705) vs page rectangular rule (IH:9469) | retain `fitted_sub` (or the server's own statistics self-check) in O; specify each statistic's arithmetic order and its derived bound (cancellation, weights, squares, division, root), the null / zero cases and lmfit's floor; one area definition (the server's trapezoid) read through the accessor — an owner decision if the page's displayed areas change |
| G5 MAJOR | local / Batch O and its proof are undefined (runFitLocal returns success, iterations, χ²ᵣ, certifyRestarts only, IH:9429) | an engine-specific O for the local engine (energies, the exact net / background it was given, final parameters, curves, the varied-parameter inventory, its coordinate certificate, `reportable: false`) and its own DISPLAY-CURRENT branch; reconcile with v4's R4-A4 local-seal amendment |
| G6 MAJOR | provenance: `{commit, dirty}` does not identify dirty contents, and a checkout does not identify the loaded worker code | PROVENANCE-COMPLETE only for a clean, identified build: the server records the content hash of its own loaded source files at start; dirty or unidentified → provenance incomplete, said |
| G7 MINOR (A) | the parameter-only `.fit.json` save / import (IH:11676) and `modelProvenance` are missing from V5.6 | add them; a `.fit.json` carries no seal (parameters for other data — already sets support null) |
| G8 MINOR (B) | `sealedState` must expose the validated consumer view, not only a status; a replay failure is not always "a different solution" (a failed re-run, restart diagnostics); Q3's "counts only" contradicts O verbatim; "before 1e" names no step | wording fixes |

Hypotheses round 2 settled: server `n_free` = the returned parameters with `vary === true` and
no expression, excluding `area`, cross-checked with `statistics.n_free_params` (F:2453-2456,
2713-2722, 2770); the statistics' domain is the whole incoming ROI, not the background window
(F:2340-2365); weights use the raw counts (F:2434-2435). Still unmeasured: the twins'
universal bit-identity (V5.4 step 4) and the replay reproduction fraction.

Next, on the owner's decision: write G1–G8 into V5.3–V5.8 (revision 3) and run the gate again;
or decide that a narrower first unit is wanted (for example 1a alone — the server's
`background_verdict`, environment and seed over HTTP — which every design variant needs).

---

# v6 (2026-10-11, owner instruction) — the V5.9 resolutions, on the recorded fields

Status: DESIGN ONLY — no code. REVISION 9 (V6.2-V6.12 rewritten after gate rounds 1-8, each
NO-GO ×2, `docs/autofit/codex/sealed_fit_v6_design_r{1..8}_verdict_run{A,B}.md`; V6.13-V6.20
map each finding).
Owner, 2026-10-10: "park the full seal; do the RECORDING unit
first … After it deploys: revise the sealed-fit design to v6 with the six V5.9 resolutions,
built on the real recorded fields, and run the design gate again." The recording unit is
deployed (3ced8d6, 2026-10-11, `docs/deploy-log.md`). v6 writes G1–G6 (and the minor G7, G8)
into the design and replaces V5.3–V5.8 where they conflict; V5.1 / V5.2 are kept as the
history they record (their line numbers refer to 90651e6). Every statement about the CURRENT
code is **VERIFIED** (`path:line` on main c643c5f = the deployed 3ced8d6 plus docs) or
**HYPOTHESIS**. IH = templates/index.html, F = fitting.py, A = app.py, L = lmfit 1.3.4
`minimizer.py` in the production venv.

## V6.1 What the recording unit settled (VERIFIED)

| v5 gap (V5.2) | today |
|---|---|
| 1. seed unsaved, unreachable over HTTP | every response carries `random_seed` and `seed_source` ("request" / "caller") (F:2863, F:2868); `/api/fit` and `/api/fit/start` accept a validated `seed` → `fit_kws.fit_kws.seed` (A:129-136); the page saves it in `fitResult.record.seed` (IH:8580-8590) |
| 3. certificate not persisted | `certificate` whole in the response (F:2897-2909) and in `record.certificate`; the local engine's own coordinate certificate in its record (`_localFitRecord`, IH:8597: `moved` over every parameter, every component's centre move) |
| 4. no software identity | `software = {git_commit, git_dirty, python, numpy, scipy, lmfit, numerics: NUMERICS_VERSION, seed_derivation}`, read ONCE at import (F:58-79, F:47); the page carries the serving worker's copy (`<meta name="xps-software">`, IH:4; `_pageSoftware` IH:8591) for local fits |
| 5. successful background verdict not stored | `background_verdict = {method, effect, check, converged, residual, reason}` (F:2879), `effect` = the seed's own reading (`_background_effect`, F:1999); the local engine's from its own certificate and `_bgEffect` |
| saves | `fitResult.record` in projects (IH:12024), spectrum files (IH:11920, loader IH:12260), `.fit.json` (`fitStatistics.record`, IH:11824; import as `modelProvenance`, IH:3457-3458), the PNG (`XPS-Fit-Record` chunk) and every export after the existing rows (`_fitRecordTextLines` IH:8627, `_fitRecordRows` IH:8650) |

Still open, unchanged by the recording unit (VERIFIED): the starting REQUEST is not recorded
(V5.2.2); the project save rounds `be`, `bgIntensity`, `bgSubtracted` (V5.2.6); the two loaders
differ (V5.2.8); readers bypass any one accessor (V5.2.9). `fitResult.record` is a SUBSET of the
response (`fitting.RECORD_KEYS`, F:49; `_fitRecordFrom` IH:8580); some arrays already persist (`fittedY` at full precision in a project), but the COMPLETE
authoritative O does not: it is memory-only in `backendResult` (IH:8984).

## V6.2 The three records

**R — what was requested.** Exactly what the server's `run_fit` received, never transformed
(V5.3), plus what the page needs to bind it (round 1: the as-sent specs lose frontend
information — a fixed-0.5 Voigt and a GL fixed at 50 send the same spec; inactive shape fields
are not sent; a link forces `fix_fwhm`):
- `R.request` — the WIRE body exactly as sent (peak specs with starting values, bounds, roles,
  links and Auto-Fit's overlays; background spec; `fit_method`; `n_perturb`; `n_starts`;
  `require_component`; an ordinary Run Fit sends no `seed` and no `charge_shift_ev`, IH:8907).
  `session_id` is TRANSPORT metadata (an upload handle that expires after seven days, A:56,
  A:241): it is not part of R's numerical request, of step 0's comparison or of the attestation;
  a replay uploads afresh. Every comparison with O uses the NORMALISED arguments the server
  derives from the request — by ONE function, `_normalise_fit_request(body, energy, counts)`,
  factored out of `_prepare_fit_request` (A:65-148, which today loads the session first, A:70)
  so that it takes the arrays explicitly: the fit routes call it after resolving the upload, the
  verification with R's inline arrays (the seed absent → derived, `charge_shift_ev` → 0);
- `R.energies`, `R.counts` — the uploaded arrays, inline, full precision;
- `R.idx` — the indices into the tab's raw arrays that `_roiSelect` returned; `R.ccShift` — the
  page's charge shift those energies were formed with (distinct from `charge_shift_ev`);
  `R.roi` — the ROI fields as read;
- `R.pageModel` — a deep copy of the page's peak objects as the request was built — EVERY own
  field, not only `_STARTS_MODEL_FIELDS` (IH:8377): Auto-Fit's overlays `_afCenterMin/Max`,
  `_afFwhmMin/Max` and the names it selects its anchor by are read by its builder (IH:8213);
  for "Use this solution" the `startPeaks` it was given: the frontend snapshot the projection
  starts from — BOUND to `R.request` (V6.3 step 0);
- `R.context0` — the producer's complete context: every `_STARTS_UI_FIELDS` field as typed, the
  fit-method selection and the producer's settings (`n_perturb`, `n_starts`, `require_component`) (incl. the background endpoint FIELDS — request indices
  cannot recover them: on a 0.1 eV grid 280.04 and 280.09 select the same sample yet round to
  280.0 and 280.1 after a 0.01 eV shift), the anchors, the charge shift, the charge-reference
  settings; `R.producer` ('runFit', 'useSolution', 'autoFit').
R carries no environment and no seed of its own: the one environment is `O.software`, the seed
used is `O.random_seed`.

**O — what the server returned.** The response verbatim, full precision, since 3ced8d6
including `fit_method`, `random_seed`, `seed_source`, `background_verdict`, `certificate`,
`software`. ADDITIVE in 1a′ (V6.11): `fitted_sub` (the model sum; today only `fitted_y =
best_fit + bg` is returned, F:2742-2743, and `fitted_y − bg` does not recover it exactly) and
`statistics.rmse` (formed by the server over all `n_data` samples — today the page forms it, and
Auto-Fit divides by the RESELECTED `be2.length`, IH:7822, not O's count). `fitResult.record`
becomes a view of O.

**D — what the page shows.** The finalisation steps (V6.3), `chosenAlternative`, the engine,
`reportable`. The displayed model is NOT stored as authority; it is DERIVED (V6.3) and the live
model compared with it.

## V6.3 G1 — a pure projection from the frontend snapshot

`applyBackendResult` writes into the live peaks it finds by `getPeak` (IH:7017-7020) and skips
every locked field (`_applyBackendParams`, IH:6998-7016): re-applying O to the displayed model
leaves its LOCKED fields unchanged whatever O holds, so it cannot be the check.

`project(R.pageModel, O, steps)` — pure, explicit inputs:
0. *The snapshot is the request's.* The page rebuilds the wire request from `R.pageModel` and
   `R.context0` with its own builder (`peakToBackendSpec` and the producer's overlays, parents
   looked up explicitly in the snapshot, not through `getPeak`) and requires it to equal
   `R.request` exactly — a snapshot whose locked amplitude reads 500 while the request sent 100
   fails here.
1. A deep copy of `R.pageModel`; for each component, `_applyBackendParams`' OWN field rules as a
   pure function of (copy, O's params): a locked field keeps the snapshot's value (so a locked
   GL mix of 29 stays 29 — no inverse unit conversion is ever formed); a free field takes O's
   value through the same conversion the live path uses (`gl_ratio × 100`, IH:7005), so the
   result is bit-for-bit what the live application produced from the same snapshot; a parameter O reports WITH AN EXPRESSION (a linked
   component's centre, amplitude and shape parameters, F:1555-1602) takes O's value WHATEVER
   the page's lock flag — the server's expression overrides a child's lock, so a kept locked
   value would contradict the fitted curve (round 2's probe: child centre 299 / 287, amplitude
   10 / 50, FWHM 3 / 1). This CHANGES today's live path (`_applyBackendParams` keeps a linked
   child's locked fields, IH:6998-7016 — a display defect today, ship step 0c).
   *Representability.* An expression value can only be shown if the child's frontend shape READS
   that parameter: a Voigt child of a GL parent is sent `gl_ratio` 0.5 fixed, the server
   overrides it with `p1_gl_ratio` (F:1570), and the page's Voigt evaluator draws 0.5 whatever
   its `glMix` (IH:4184; round 3's probe: the fitted child differs from its drawn curve by up to
   2.06 counts, success and certified). A linked component has its parent's lineshape (CLAUDE.md
   "Linked (Multiplet) Peaks": shape is synced), but the page lets them differ (its shape-switch
   propagation reaches the immediate family only, IH:5848) and the load validator accepts it
   (IH:15797). Ship step 0c therefore validates the LINK GRAPH, on the page before any request
   (Run Fit, Auto-Fit, Batch Fit and the local engine alike) and on the server (`run_fit`, a 400),
   and in every seal's verification: every `linked` resolves to a component of the model (today
   removing a chain's root deletes only its immediate children, IH:6400, and the builder then
   silently drops the orphan's `constrain_to`, IH:6983, as the local engine silently skips it,
   IH:9285 — refused instead); ids are unique; no cycle; and a child's FRONTEND lineshape equals
   its parent's. The server cannot see the frontend shape — a Voigt and a GL both arrive as
   `pseudo_voigt_gl` (IH:6929) — so every spec carries it in a new field `frontend_shape`
   (additive; part of the normalised, attested arguments) and the server refuses a link whose
   two `frontend_shape`s differ. Plain words, no silent change; saved projects carrying such a
   model load and say so (measured in 0c). For same-shape families no other parameter is
   unrepresentable (round 4: DS, DS+G, LA and asym-GL map every expression-valued parameter;
   Voigt → Voigt keeps 0.5). One function
   serves both: the live path becomes `applyInPlace(livePeaks, project(...))`, so there is no
   second reading. After the projection, every displayed field equals O's value through the
   builder's mapping: an independent locked field's snapshot value is the value the builder
   sent (step 0), which is O's held value (verified, V6.5).
2. The producer's finalisation, DERIVED, never taken as data: `finalise(producer, O, R, ctx)`
   re-derives every step from O and the recorded context and D's recorded steps must equal it.
   Run Fit and "Use this solution": none. **Auto-Fit: none either, by refitting after its
   charge shift (ship step 0d, Q8).** Today it fits, shifts the frame, moves every centre and
   manual anchor, re-selects the window and recomputes the background, then locks the centres
   (VERIFIED IH:7793-7855, IH:5463-5490; the endpoint fields are re-rounded only when the shift
   changed, `delta !== 0`, IH:5465) — so its shown points, background and anchors are not the
   fitted ones, and no translation reconciles them in floating point (the logged Auto-Fit unit,
   CLAUDE.md). With 0d, Auto-Fit is two fits: the ANCHOR fit (R₁, O₁: the model with its
   overlays, in the original frame) decides the shift by its gates — the anchor gate in its OWN
   arithmetic (`_autoFitGraphiteIsSupported`, IH:7726: `counts − fitted_y`, weights
   1/max(counts, 1), sequential sums — by definition a different statistic from step (b)'s
   support, CLAUDE.md "Charge Correction"), the reference-centre window (IH:7769-7789, its
   existing `0.30 + 1e-6` acceptance gate, IH:7787) and `O₁.required`; the shift derived from O₁
   exactly as today (raw centre = O₁'s anchor centre + the old shift, IH:7793, `toFixed(3)`,
   IH:7803; Δ; the endpoint fields re-expressed `toFixed(1)` only when Δ ≠ 0); then, with every
   centre locked, the FINAL fit (R₂, O₂) in the new frame. The seal is (R₂, O₂, E) with the
   anchor evidence E = (R₁, O₁) INSIDE it (and so inside the verification's identity).
   *E is a full prerequisite, not a footnote:* R₁ passes every page binding of V6.4 against the
   same tab's raw data under `R₁.context0` (an authentic anchor fit of ANOTHER spectrum fails
   here); O₁ passes V6.5's verification and its POSITIVE acceptance (`success === true` — an
   authenticated failure stays a failure — as Auto-Fit requires today before its gates,
   IH:8267); the anchor gate, the reference-centre window and `O₁.required` hold. Then
   `derive(R₁, O₁)` — the projection of O₁ onto `R₁.pageModel`, every centre and manual anchor
   moved by −Δ, the endpoint fields re-rounded only when Δ ≠ 0, the overlays carried, the window
   freshly selected from the raw samples in the new frame, every centre locked, the producer's
   settings unchanged — must equal (`R₂.pageModel`, `R₂.context0`) exactly.
   *The transaction:* one operation token spans both fits and both verifications; nothing is
   published until it ends — between the fits the page shows the progress line only ("Auto-Fit:
   anchor fitted, refitting in the corrected frame …"), no statistics, no support, no snapshot,
   no save. COMMIT when O₂ is accepted, verified and its anchor still passes the gate: the
   charge correction, the model and the seal are written at once, ONE undo entry, one history
   snapshot. ROLLBACK otherwise — the final fit failed, was cancelled or superseded, could not
   be verified, or its anchor no longer passes (unsupported or not required after the refit),
   WHILE the operation still owns the tab: since nothing was published, the staged work is
   discarded and the live model, context and charge correction are exactly as they were, with
   the reason (today's failure paths restore a snapshot, IH:8283, because today's path
   publishes before it fails). SUPERSEDED — another operation took the tab: the staged work is
   discarded and NOTHING is written, neither a restore nor a message into the newer owner's
   state, exactly as today returns without rollback when superseded (IH:8247, IH:8292); the
   same for each fit's and each verification's reply. The anchor fit alone never sets a charge
   correction (recommended; Q8). Without 0d, an Auto-Fit with Δ ≠ 0 is never current (said so); with Δ = 0
   only the centre lock follows, a derived step on the lock flags alone.
3. (Round 1's `(raw − old) − (new − old)` ≠ `raw − new` is why no seal ever translates a
   frame: with 0d every displayed quantity of an Auto-Fit belongs to a fit made in that frame.)
DISPLAY-CURRENT compares the live model with `project(...)` exactly through `_fitKeyCanon`'s
readers. The Results table reads values from `project(...)`'s output (the same numbers the
model holds), and curves and statistics from O (V6.5) — never from the live peaks.
"Use this solution" is an ordinary Run Fit whose R is the request its `startPeaks` produced
(IH:8832, 8874); an alternative's PREVIEW is a preview of an unfitted model (no statistics
claim, no currency).

## V6.4 G2 — bindings the page checks (exact, explicit inputs, no globals)

The page's adapter is a pure function of saved inputs, reproducing each current reader exactly
(round 1: `getCorrectedBE` reads globals and maps a NaN shift to 0 — `isNaN`, so Infinity passes
through — IH:5526, likewise `_roiSelect` IH:5548; `_bgEffect` falls back to the live anchors). A
seal is formed only with a finite `R.ccShift` (the producer refuses otherwise), and the adapter
uses the readers exactly as they are:
- **Samples.** `R.idx` equals, element for element and in order, the selection `_roiSelect`
  makes from the tab's raw arrays with `R.ccShift` and `R.roi` (completeness and order — a
  narrower subset fails); `R.energies[j]` is that reader's corrected energy for `R.idx[j]` and
  `R.counts[j] === tab.rawIntensity[R.idx[j]]`; `O.energy` and `O.counts` equal R's exactly.
- **Display frame.** The chart's energies are formed from the raw samples and the FINAL shift by
  the same reader (`rawBE[R.idx[j]]` with `ccShift_final`) — never by translating R's energies.
- **Context → background spec.** ONE context supplies every background computation of a seal:
  `R.context0`, the context the request was built from. Through `_bgWindowIndices` (inclusive
  window → the request's exclusive `end_idx`), the averaging as the request reads it and
  `R.context0`'s own anchors (explicit, not `_getManualAnchors()`) it equals
  `R.request.background`; the LIVE context equals `R.context0` (with 0d there is no later
  context; an Auto-Fit's `R₂.context0` is itself re-derived from R₁ and O₁, V6.3); and `_bgEffect` of it
  equals `O.background_verdict.effect` (pinned on eight settings by
  `test_browser_fit_recording.py::test_the_page_records_the_background_by_its_effect_as_the_server_does`).
  PREREQUISITE: the averaging refusal (branch `feat-endpoint-avg-refusal`, not yet deployed) —
  until it ships, the page's helpers and the server read an averaging of 1e21 or more
  differently (A:85 `max(1, int(x))` at c643c5f; `_bgEffect`'s double parse, IH:5042).
- Everything the page cannot recompute itself is checked by the SERVER (V6.5).

## V6.5 The states

**DISPLAY-CURRENT** — all of:
1. *The page's bindings* — V6.4, and the live model equals `project(R.pageModel, O, steps)`
   with the steps re-derived (V6.3).
2. *The server's verification* — one `POST /api/verify-fit {R, O}` (1a′) returns `ok` and the
   verifier's `software`. Its result is CONSISTENCY UNDER THE VERIFIER'S IMPLEMENTATION: the
   verifier's code reproduces O exactly from R. It is not a proof that the producer ran the same
   code — the producer's identity is attested (V6.7) and its statements authenticated (below).
   A verifier whose `software` differs from `O.software` returns UNCONFIRMED "different
   software". Every comparison it makes is EXACT (the existing solver, certificate, Auto-Fit-gate
   and replay tolerances are untouched and are not currency identities):
   - roles: the lmfit parameters it builds from `R.request` (`_make_peak_params`, F:1555-1602,
     expressions before held values — a linked child's sent centre is overridden by its
     expression, so a held value is checked only for parameters with no expression) have O's
     `vary`, `expr`, `min`, `max`; every expression evaluates, from O's free values in
     dependency order (any request order), to O's value;
   - `O.fit_method == R.request.fit_method`; `O.charge_shift_applied == R.request.charge_shift_ev`;
     `O.random_seed` is the caller's seed, or `_request_seed` recomputed from `R.request` and R's
     arrays (F:2525-2532) — `O.seed_source` accordingly;
   - the background: run_fit's WHOLE background assembly — window normalisation, the integral
     methods through `compute_background`, linear, manual, none, the flat extension beyond the
     window (F:1314, F:2393-2475) — refactored into ONE function both `run_fit` and the
     verification call, equals `O.background_y`, and its certificate `O.background_verdict`;
   - the model: each component `y` re-evaluated from O's params on O's energies (F:2750-2755);
     `area` by the same trapezoid (F:2758: SciPy's signed `dx * (y[i+1] + y[i]) / 2`, summed,
     then `abs`); `fitted_sub` re-evaluated as `best_fit` is (a fresh composite evaluation,
     lmfit model.py:1587); then `fitted_y == fitted_sub + background_y` and `residuals ==
     (counts − background_y) − fitted_sub` (F:2743, F:2827) in those exact associations;
   - the statistics from those arrays (V6.6), AIC / BIC by lmfit's formula, `n_free_params`
     from the roles, `rmse`, the R-factor; each component's support by `_component_support`
     (F:2233) with the linked-root rule (F:2802-2819).
   Re-evaluation is exact only if every evaluator is bit-stable on this server: HYPOTHESIS for
   LA(α,β,m) (`np.convolve`, F:1424) and DS+G (NumPy FFT, F:330-332) — two different mechanisms;
   round 1's bounded probes (14 fits, seven shapes) found re-evaluation and recomputed χ² equal.
   Measured in 1b; a shape whose evaluation is not bit-stable cannot be verified exactly and its
   fits are UNCONFIRMED — never compared within a measured tolerance (design rule) — until its
   evaluator is made deterministic (owner Q7).
3. *Accepted, by the producer's AUTHENTICATED word.* Acceptance is a property of the search —
   certification restarts, a global method's refinement (F:1751, F:1853, F:1954) — which no
   evaluation reproduces; a saved `certified: true` is the FILE's assertion. So the producing
   server attests what IT received and returned. The contract (1a′):
   - *Signed bytes:* UTF-8 of `json.dumps({"v": "xps-seal-attest-1", "args": A, "out": B},
     sort_keys=True, separators=(",", ":"), ensure_ascii=True)`, where A = `_canonical` (F:1979:
     keys sorted, every number a float, −0.0 folded to 0.0, so a browser's `285` for `285.0` and
     its `0` for `−0` do not change it) of the NORMALISED numerical arguments of `run_fit`
     (energies, counts, every keyword after normalisation, `session_id` excluded), and B =
     `_canonical` of O without `attestation`. The normaliser is a recursive, versioned, TYPED
     schema, applied before fitting and before signing, so the signed form is the executed
     recipe: every field EXPANDED TO ITS EFFECTIVE VALUE, field by field (absent is not null —
     an absent `fwhm_min` means 0.1 and an explicit null means unbounded, F:1618; a link's
     absent `fix_fwhm` means true, F:1568 — each written as the bound or flag that acts, so two
     requests that execute alike sign alike and two that differ never do); identifiers (`id`,
     `constrain_to`, `require_component`) as STRINGS, losslessly (round 4: integer ids
     9007199254740992 and 9007199254740993 canonicalise to one float and their `required`
     verdicts differ; an id of 10**400 fits today and overflows `_canonical`) — a non-string id
     accepted only as an integer within ±(2⁵³ − 1) and converted to its decimal string, anything
     else refused before fitting; counts (`n_perturb`, `n_starts`, the averaging) as integers in
     their ranges; every number finite. It covers only what
     the server received: `R.pageModel`, `R.context0`, `R.idx` and `R.producer` are the page's
     and are proved by the page's bindings (V6.3 step 0, V6.4), not by the MAC.
   - *Who signs:* the fit routes, over the result `run_fit` just returned — never the
     verification, which only recomputes and compares (constant-time); a valid MAC on
     `success: false` is an authenticated failure.
   - *Keyring — ONE state, ONE writer protocol.* The keyring is a directory outside the
     repository and the upload folder (`XPS_ATTEST_KEYRING`, default `~/.xps-app/attest/`,
     0700) holding ONE authoritative file, `state.json` (0600) = `{incarnation, revision,
     active, keys: {key_id: key bytes}}` — keys are 32 bytes from `secrets.token_bytes`,
     `key_id` the first 8 bytes of SHA-256(key), hex; `O.attestation = {v, key_id, mac}`.
     EVERY mutation — creation at first start, rotation (add a key, make it active; earlier
     keys stay for verification), revocation (remove a key; its seals read UNCONFIRMED),
     restore (a backup's keys under a FRESH incarnation) — is one transaction under an
     exclusive cross-process lock (`fcntl.flock` on `keyring.lock`): re-read `state.json`,
     modify, allocate `revision = previous + 1` (a new incarnation starts at 0), write a
     temporary file, fsync it, rename it over `state.json`, fsync the directory, release. So
     two writers can never publish states with one generation — the second re-reads the
     first's committed state under the lock — and an acknowledged generation is durable: a
     restart reads the last renamed state, never an earlier one; a crash leaves only a
     temporary file, removed by the next transaction. Readers take no lock: the signer reads
     `state.json` on every signature and the verifier on every verification (cached by
     (inode, mtime, size), never beyond a change), so all four workers and every restart sign
     with the one active key, and a rotation or revocation acts on the next request in every
     worker, no in-memory key outliving its state. Mutations other than the first creation
     are an owner's command (`scripts/attest_keyring.py`), never a request path. A lost
     keyring makes every seal UNCONFIRMED (backup is the owner's choice). The droplet keeps
     its own keyring — a separate trust domain — unless the owner chooses to share one (Q9).
   - *What it proves, and not:* an attested O cannot be paired with a different normalised
     request; whoever holds the key (the server — the verifier is the same server) can forge
     statements, and a leaked key lets its holder attach `certified: true` to a consistently
     fabricated non-minimum that recomputation cannot expose. Recomputation still matters:
     authentication gives attribution, recomputation consistency under the verifier.
   With it, `O.success`,
   `O.certificate.certified`, a global method's `success`, `O.background_verdict.converged` and
   Auto-Fit's `O.required` are the producer's authenticated statements about THIS R and O. No
   matching key (another server, a rotated or lost key) → UNCONFIRMED "not attested by this
   server". (Owner Q9; the alternative — re-certifying on load — is a fit, not a check, and
   Trust-Region is not bit-reproducible.)
4. *The background is today's* — V5.4.4 (the page's certified background for R's inputs equals
   `O.background_y` exactly; HYPOTHESIS to prove in 1b, else STALE "background changed").

**AUTHENTICATED, not recomputed** (said beside them): σ; the certificate's restarts, `moved` and
centre moves; `starts` (counts, alternatives' scores, areas, fractions, moves); `required`;
messages — the producer's statements, bound to this R / O by the attestation; their truth is
what a re-run tests (REPLAY-CHECKED), not this check.

**PENDING** — while the verification is outstanding (a fresh fit included: no "by construction"
exemption); statistics shown with "confirming …". **UNCONFIRMED** — the server unreachable, a
different server software, or a shape not verifiable exactly; values shown with the reason,
never current; distinct from a detected mismatch, which is STALE / PEAKS-ONLY with the failed
check named. Owner Q6.

The verification result is owned by the WHOLE immutable seal it checked (a WeakMap from the
frozen `{R, O, D}` object to `{verifier software, result}`; R and O are never re-paired — a new
pairing is a new seal and is verified anew); the request is issued under the fit-operation
token and the tab's ownership (`_opOwner` / `_ownerActive`), and a reply for a superseded
operation or another tab is discarded. Seals are frozen, so history snapshots may share them;
edits and history restores change the live model, which step 1 re-checks.
*Trust generation.* A cached result holds two parts with different lifetimes: the numerical
consistency (a property of the seal and the verifier's software — it can be kept) and the
authentication (a property of the keyring — it cannot outlive a revocation or a replaced
keyring). The keyring's state (`state.json`, step 3's one-writer protocol) carries the generation:
`incarnation` — 128 random bits drawn when a keyring is created or restored (so a lost and
recreated keyring, a restore, or another server's never shares it) — and `revision`, allocated
under the lock by every mutation, so no two committed states share a generation.
A verification reads that file ONCE and authenticates against that snapshot, and its reply
carries the generation `{incarnation, revision}` it actually checked (never one read later). A
cached authentication is valid only while the server's CURRENT generation equals the one it
was obtained under — any difference, a new incarnation or a newer revision, drops it. The page
fetches the current generation (`GET /api/attest-generation`, which reads the same file)
whenever it loads a file, activates a tab holding a seal, or exports or saves one. Its view of
trust, `trustView = {incarnation, revision}`, changes ONLY by these rules, so no delayed reply
can reverse it: (i) every generation fetch carries a page-local sequence number, and only the
reply to the most recently ISSUED fetch may set the incarnation; (ii) within one incarnation the
revision only rises — a lower revision, from any reply, never replaces a higher one; (iii) every
verification is tagged with the `trustView` it began under, and when `trustView` changes every
outstanding verification is void — its reply is discarded whatever it says; (iv) a save or an
export awaits a generation fetch issued AFTER it began and authenticates against that result. So after a revocation, a rotation that retires the key, a lost
keyring or a move to another server, the seal is PENDING and then UNCONFIRMED at the next of
those moments, never later than its next export or save. This applies to O and to an Auto-Fit's
O₁ in E alike. Recovery: a lost keyring is a new incarnation by construction; restoring a
backup installs its keys under a FRESH incarnation (drawn at restore), so the seals they signed
authenticate again while every cache taken before the restore is dropped — no generation is ever
reused.

**PROVENANCE** (G6, V6.7) and **REPLAY-CHECKED** (V5.4 with the outcomes *reproduced within
rounding*, *a different solution*, *the re-run failed* (its message), *different software*).

## V6.6 G4 — the statistics: one association

VERIFIED today: `y_sub = y − bg` (F:2477); weights `1/√max(counts, 1)` from the RAW counts
(F:2487-2488); lmfit's residual `(data − model)·weights`, `chisqr_raw = (residual**2).sum()`
(L:318, a NumPy pairwise sum), `redchi = chisqr_raw / max(1, ndata − nvarys)` (L:325, lmfit's
`nfree`) BEFORE `chisqr = max(chisqr_raw, 1e-250·ndata)` (L:327); `aic` / `bic` from the
floored χ² (L:328-330); the response's `chi_square`, `reduced_chi_square` are lmfit's (F:2824-2825),
from a residual evaluated inside the minimiser — `best_fit` is a SEPARATE evaluation (lmfit
model.py:1587); `n_free_params = result.nvarys` (F:2823); `residuals = y_sub − fitted_sub`
unweighted (F:2827); `r_factor = Σ|y_sub − fitted_sub| / Σ|y_sub|`, `null` when 0 (F:2830-2831);
the server refuses a model with n_free ≥ n_data (CLAUDE.md "Determinacy").

The contract (1a′), names unambiguous: `n_data` = len(O.energy); `n_varys` = the parameters
with `vary` and no `expr`, the synthetic `area` excluded (= `statistics.n_free_params`);
`chi2_raw = Σ(((y_sub − fitted_sub)·w)²)` (NumPy pairwise sum); `reduced_chi_square =
chi2_raw / max(1, n_data − n_varys)`; `chi_square = max(chi2_raw, 1e-250·n_data)`; `aic`, `bic`
by lmfit's formulas from that `chi_square`; `rmse = √(Σ residuals² / n_data)`; R-factor as today.
The server REPORTS these from the arrays it returns, so its verification recomputes them
exactly. Equal to today's lmfit values whenever `best_fit` reproduces the minimiser's last model
(round 1's probes: equal on 14 fits); where not, a change whose size is MEASURED in 1a′ on the
202 targets and release-noted — no size is claimed in advance (cancellation can amplify a model
difference in a residual statistic). `starts.fit.chi2r` and the alternatives keep their own
values (ATTRIBUTED, V6.5).

Nullable by schema (not "finite everywhere"): `stderr`, `min`, `max`, `expr`, `r_factor`,
`aic` / `bic` when undefined, `support.f`, `certificate` (DE / basinhopping), `required`,
`starts`; every array and every other number finite.

**Areas — ONE definition (Q5).** Three today: the server's trapezoid as a magnitude (F:2758);
the page's rectangle sum × the first step (`_peakArea`, IH:9616-9622) — Results, sidebar,
sidebar support patching (IH:7707), Quantify, CSV/XLSX, Auto-Fit's 40 % graphite warning
(IH:7562-7566, so a decision can change, not only a number); the spectrum save's sequential
trapezoid with |dx| per interval (IH:11888-11897; on the grid [0, 2, 1] with unit samples:
server 1, spectrum save 3, rectangle 6); and the alternatives' server areas and fractions
(F:2133-2146, IH:8747-8756). Recommended: the server's, read from O (and the local O's own, the
same formula) through the accessor, for EVERY reader listed. The change is measured in 1b on
the committed set; Q5 is decided on that measurement, after 1b, before 1c.

## V6.7 G5 — the local engine's O; G6 — provenance

**Local O** (Batch Fit and the fallback; v4 R4-A4 "stores exactly what local LM fit").
PREREQUISITE (ship step 0b, a defect the gate found): today the engine propagates links in one
pass in peak order, so its retained χ² can describe another model than the peaks it commits
(round 2's probes: an all-held reversed chain reported χ² 2237.98 where its committed peaks give
2620.21; another 136.72 against 0.52; IH:9297-9305, IH:9512-9529). The engine propagates links in
dependency order (each child after its parent, a fixed point), and FINALISES by freezing one
model: every array, statistic, support verdict and certificate of the local O is derived from
that frozen snapshot, and the same snapshot is committed. The local O:
`{engine: 'local', success: true, energies, net, background (the certified array given, with
its certificate and effect), weights by the ENGINE's association — 1/√max(net + background, 1),
IH:9214, never recomputed from raw counts — the varied-parameter inventory (`paramMap`), the
frozen final model, each component's curve (`evalPeakArray` on that snapshot), the model sum, χ²
and χ²ᵣ from that snapshot in the engine's arithmetic (sequential sums, no floor, IH:9318), RMSE, R-factor
(`_computeRFactor`), areas (Q5's definition), iterations, the coordinate certificate, support
(`_componentSupportCore`), reportable: false}`. VERIFIED today it returns only `{success,
engine, iterations, acceptedSteps, chiReduced, certifyRestarts}` (IH:9576) and does not keep the
inventory or the curves. Its DISPLAY-CURRENT: the page is its own verifier (the same functions
on the snapshot: exact), V6.4's bindings, its own certified background, acceptance its
certificate. No σ; LA's `caM` held. The starting-point designation stays through every
provenance path: `_isLocalFit`, `_isLocalModel`, `_provenanceOf` (IH:9128), undo, Batch
copies, `.fit.json`, history, stacks, exports (IH:9074-9139).

**Provenance (G6) — narrowed to an ATTESTATION.** Hashing source files does not identify the
executed code (bytecode caches, later imports, replaced files), and versions do not identify
native artifacts; the frontend is served from disk independently of the worker's restart and
renders runtime reference data (DEPLOY.md:31-37; A:800-808). v6 claims no execution proof.
`PROVENANCE: attested` when the server reports, at import, a 40-hex `git_commit`,
`git_dirty === false` and NO untracked file under the checkout (`git status --porcelain` without
`--untracked-files=no`, F:73 today excludes them), plus `env_sha256` — SHA-256 of the sorted
`name==version` list of the installed distributions (the lockfile identity) — and, per rendered page,
`page_sha256` (SHA-256 of the template FILE's bytes as read for that render) and
`reference_sha256` (of the reference data injected into it), both in the meta tag — digests of
the render's inputs, so the page never hashes a text containing its own digest. Anything else:
`PROVENANCE: incomplete`, with what is missing. Never withholds the statistics (Q4).

## V6.8 Legacy saves

- No key (all 121 committed fits): V5.5, unchanged — never current; the restore rule is the
  adapter.
- Key, no record (2026-09-25 → 2026-10-10) and key + record, no seal (2026-10-11 → the seal):
  never current (Q1); a record is kept and shown as provenance EVEN when the reconstruction
  falls back to peaks-only — today `_dropRestoredFit` nulls `fitResult` and the record with it
  (IH:10585-10587), so the adapter keeps it separately (`tab.provenance`).
- `.fit.json` (G7): parameters for other data, never a seal; the record as `modelProvenance`
  (VERIFIED IH:3457-3458), support null.

## V6.9 Migration (V5.6 plus)

V5.6's consumers, plus: every area reader of V6.6; the `.fit.json` save and import and
`modelProvenance`; the record's export tail (IH:8627, IH:8650) and PNG chunk as views of O;
the verification's pending / failed / owned states on load, tab switch and history restore
(V6.5). `sealedState(fr, live)` returns `{state, failedCheck, reason, view}`; `view` (model,
curves, statistics, areas, support, attributed evidence, provenance) is the only thing consumers
read. Q3: the alternatives' parameter sets are in O (O is verbatim).

## V6.10 Owner decisions requested

- Q1: keyed and recorded-but-unsealed saves never current (recommended)?
- Q2: REPLAY-CHECKED on demand only (recommended)?
- Q3: alternatives' parameter sets kept in O (recommended)?
- Q4: incomplete provenance a note, never withholding statistics (recommended)?
- Q5: one area definition, the server's trapezoid, for every reader (recommended) — decided
  after 1b measures the change (it can flip Auto-Fit's 40 % warning)?
- Q6: every server fit verified by one server call; PENDING until then, UNCONFIRMED offline or
  on different software (recommended)?
- Q7: a lineshape whose evaluation is not bit-stable (if 1b finds one) is UNCONFIRMED until its
  evaluator is made deterministic — a separate unit (recommended), never a tolerance?
- Q8: Auto-Fit refits after its charge shift (ship 0d: two fits, the seal the final one's; it
  changes Auto-Fit's reported numbers, measured in 0d) (recommended) — or keep one fit, and an
  Auto-Fit that moved the frame is never current?
- Q9: acceptance authenticated by a server-held key (HMAC, V6.5 step 3) — seals from another
  server or after a lost key read UNCONFIRMED (recommended) — or narrow the state to
  "numerically consistent, acceptance unverified"? And: the i9 and the droplet separate trust
  domains (recommended) or one shared keyring?
- Q10: fix the defects the gate found, as their own small units before the seal: the local
  engine's link propagation (its χ² can describe another model, 0b — it can change local
  trajectories and outcomes, measured), and a linked child (0c: its fields take the server's
  expression values; a link across lineshapes refused, page and server; `_altPeaks`' value-only
  parameters, IH:8784, carry no `expr`, so an alternative's preview of a linked model follows
  the same rule)?

## V6.11 Ship order (after approval)

0.  The averaging refusal (branch `feat-endpoint-avg-refusal`) deployed. 0b. The local engine's
    dependency-ordered link propagation and frozen finalisation (Q10). 0c. A linked child's
    fields take the server's expression values on the live path, and a link across lineshapes
    is refused (Q10). 0d. Auto-Fit refits after its charge shift (Q8). Each with Codex ×2.
1a′. Server, additive: `fitted_sub`, `statistics.rmse`, the statistics formed from the returned
     arrays (the change MEASURED on the 202 targets and release-noted), the one background
     assembly, `_normalise_fit_request` with explicit arrays, `env_sha256`, untracked files in
     `git_dirty`, the attestation keyring and `O.attestation`, `POST /api/verify-fit`. Tests;
     Codex ×2.
1b.  Measure and prove: evaluator bit-stability per lineshape (Q7); V5.4.4's background
     bit-identity; the area change (Q5); the seal's size; the replay reproduction fraction.
     Then Q5 / Q7 decided.
1c.  Producers write R / O / D (Run Fit, Use this solution, Auto-Fit with its derived steps and
     gates, the local O for the fallback and Batch Fit); both saves and both loaders persist them
     losslessly; `project` replaces the live application path; `sealedState` and every V6.9
     consumer switch together; the legacy adapter routes everything unsealed. One branch, one
     release. Codex ×2.
1d.  REPLAY-CHECKED (Q2). Codex ×2.

## V6.12 What each V5.9 finding became

| finding | v6 |
|---|---|
| G1 D a fixed point of `applyBackendResult` | V6.3: `project(R.pageModel, O, steps)` — the live path's own rules as a pure function; steps re-derived; Auto-Fit's reselection not reconciled |
| G2 records not bound | V6.4 page bindings (samples complete and ordered, display frame, context); V6.5 server: roles, expressions, method, shift, derived seed |
| G3 parameters ↔ curves | V6.5: every server O verified by the server, exactly; attributed evidence named; PENDING / UNCONFIRMED |
| G4 statistics | V6.6: one association with lmfit's denominators and floor; `fitted_sub`, `rmse` in O; every identity; nullable schema; one area definition across every reader |
| G5 local O | V6.7: complete, the engine's own weights and snapshot |
| G6 provenance | V6.7: an attestation (clean commit incl. untracked, environment identity, rendered page), not an execution proof |
| G7 `.fit.json` | V6.8, V6.9 |
| G8 wording | V6.5 replay outcomes; V6.9 `sealedState` view; Q3 |

## V6.13 What changed from v6 revision 1 (gate round 1, NO-GO ×2) — revision 2

| round-1 finding (both runs unless marked) | revision 2 |
|---|---|
| BLOCKER χ²ᵣ divided by `max(1, n_free)` with n_free = nvarys | `max(1, n_data − n_varys)`; names disambiguated (V6.6) |
| BLOCKER `fitted_sub` not bound to the components, `fitted_y`, `residuals` | the server re-evaluates `fitted_sub` and checks both identities exactly (V6.5) |
| BLOCKER / MAJOR the projection cannot be rebuilt from the as-sent specs; expressions override locks; unit conversion not invertible | `R.pageModel`; the live path's own rules, no inverse conversion; held values checked only without an expression (V6.3, V6.5) |
| BLOCKER Auto-Fit order, rounding, reselection, gates | derived steps in the verified order; reselection not current (Q8); gates (V6.3) |
| BLOCKER / MAJOR derived seed, roles, bounds, method, shift unbound; selection completeness; display frame | V6.4, V6.5 |
| MAJOR averaging "1–50 on both sides" stated as deployed | a ship prerequisite (V6.4, V6.11 step 0) |
| MAJOR measured-rounding fallback (design rule) | removed: not bit-stable → UNCONFIRMED (Q7) |
| MAJOR attributed evidence unnamed (certificate, starts, required) | named ATTRIBUTED (V6.5) |
| MAJOR support twin trusts `ip.support`, different arithmetic | support recomputed by the server's own function (V6.5) |
| MAJOR AIC / BIC, nullable fields, `starts.fit.chi2r` | V6.6 |
| MAJOR area consumers incomplete; a third definition | V6.6 (every reader; Q5 after measurement) |
| MAJOR local O: success, weights, links, designation paths | V6.7 |
| MAJOR source hash ≠ executed code; manifest undefined; page served from disk | narrowed to an attestation (V6.7) |
| MAJOR verification ownership; record lost on peaks-only | V6.5 ownership; V6.8 `tab.provenance` |
| MINOR "unchanged whatever O says"; area line F:2758; section pointers; measure-before-approval order | corrected |

## V6.14 What changed from revision 2 (gate round 2, NO-GO ×2) — revision 3

Round 2 found the arithmetic contract resolved (lmfit's denominators, floor and AIC / BIC order
confirmed against the installed lmfit; `fitted_sub`'s identities; support; RMSE; no tolerance in
CURRENT; a bounded probe of all five methods rebuilt roles and seeds and re-evaluated components,
the model sum and χ² exactly; R suffices to rebuild the fit problem). Open, both runs:

| round-2 finding | revision 3 |
|---|---|
| BLOCKER the snapshot is not bound to the request; a linked child's locked fields contradict the server's expression values | V6.3 step 0 (rebuild the request from the snapshot, exact); expression-valued fields take O's value (a live-path change, ship 0c, Q10) |
| BLOCKER acceptance (`success`, `certified`, a global method's `success`, `required`) rests on the file's word | V6.5 step 3: the producer's HMAC attestation over normalised R and O (Q9) |
| MAJOR Auto-Fit's pre-finalisation context (endpoint fields), its exact charge formula, centres and anchors, its own anchor-gate arithmetic | `R.context0`, `R.producer`; V6.3 step 2 in the verified associations; the anchor gate named as the producer's own statistic |
| MAJOR the local engine's retained χ² can describe another model (reversed chains) | ship 0b: dependency-ordered propagation and a frozen finalisation; the local O derived from and committing one snapshot (V6.7) |
| MAJOR verification owned by O alone | owned by the whole frozen seal, under the operation token and tab ownership (V6.5) |
| MAJOR "same code" overclaimed by the verification | its result is consistency under the verifier's implementation; producer identity attested, statements authenticated (V6.5) |
| MAJOR (A) the background check must be run_fit's whole assembly | one shared background assembly (V6.5, 1a′) |
| MAJOR (false VERIFIED) `getCorrectedBE` maps NaN, not every non-finite shift, to 0 | corrected; seals need a finite shift (V6.4) |
| MINOR wire request vs normalised arguments; section pointers; the rendered page's own digest | `R.request` is the wire body, compared through the server's normalisation (V6.2); pointers; digests of the render's inputs (V6.7) |

## V6.15 What changed from revision 3 (gate round 3, NO-GO ×2) — revision 4

Round 3 found resolved: the local engine's frozen finalisation (0b), verification owned by the
whole seal, the verifier-relative wording, the shared background assembly, the NaN reader, the
render-input digests; the statistics contract again confirmed (lmfit, SciPy, `_npPairwiseSum`
on arrays up to 100 000). Open, both runs:

| round-3 finding | revision 4 |
|---|---|
| BLOCKER a linked child whose lineshape cannot read the parent's expression-valued parameter (a Voigt child of a GL parent: drawn at 0.5, fitted at the parent's mix) | representability: a link across lineshapes refused, page and server (0c, Q10) |
| MAJOR Auto-Fit's final context (moved anchors) still compared with the original request; the `delta !== 0` branch | one context per seal (`R.context0`); Auto-Fit refits after its shift (0d, Q8), so nothing is translated; the branch stated |
| MAJOR the shared normaliser loads the (expiring) session; `session_id`, the method and producer settings missing from step 0's inputs; Auto-Fit's overlays outside `_STARTS_MODEL_FIELDS` | `_normalise_fit_request(body, energy, counts)`; `session_id` transport-only; `R.context0` carries the method and settings; `R.pageModel` every own field |
| MAJOR the attestation's payload, canonicalisation and key lifecycle unspecified | V6.5 step 3: versioned signed bytes via `_canonical`, what is and is not covered, who signs, the keyring (creation, workers, rotation, revocation, loss, the droplet), what a leaked key can do |
| MINOR "no tolerance anywhere" too broad (Auto-Fit's `0.30 + 1e-6` gate, solver and replay tolerances) | scoped to the verification's comparisons |

## V6.16 What changed from revision 4 (gate round 4, NO-GO ×2) — revision 5

Round 4 found resolved: the expiring-session normaliser and the reconstruction inputs; the
original / final context contradiction and the zero-shift branch; the tolerance scope; the
statistics contract (again confirmed); 0b / 0c / 0d correctly stated as behaviour changes.
Open, both runs:

| round-4 finding | revision 5 |
|---|---|
| BLOCKER a dangling link (a chain's root deleted) is silently dropped from the request; the server cannot see the frontend shape (Voigt and GL are one backend shape) | 0c validates the whole link graph on page, server and verification (resolves, unique ids, no cycle, same frontend shape); every spec carries `frontend_shape` |
| BLOCKER the anchor fit not bound to this spectrum, nor required to have succeeded | E = (R₁, O₁) inside the seal and its verification identity; R₁ passes every page binding, O₁ verification and positive acceptance and the gates; R₂ = derive(R₁, O₁) exactly |
| MAJOR the two-fit transaction (what is shown between, commit, rollback, ownership, a final anchor that no longer passes) | one operation token; nothing published until the end; commit with one undo entry; rollback as today's failure paths; the anchor fit alone never sets a charge correction (Q8) |
| BLOCKER / MAJOR the signed schema: absent ≠ null; integer ids collide or overflow | a typed recursive schema expanding every field to its effective value; ids as lossless strings, integers beyond ±(2⁵³ − 1) refused |
| MAJOR / MINOR key publication and worker refresh | complete-key publication by link; per-use reads of the pointer and keyring, cached by (path, mtime, size) |
| MINOR the heading still read "revision 3" | corrected |

## V6.17 What changed from revision 5 (gate round 5, NO-GO ×2) — revision 6

Round 5 found every round-4 blocker resolved (the link graph and `frontend_shape`; the anchor
evidence's bindings and acceptance; the typed schema and lossless ids; key publication and
worker refresh) and no new false VERIFIED claim, tolerance or second reading. Open, both runs:

| round-5 finding | revision 6 |
|---|---|
| MAJOR a cached verification survives a key revocation | trust generation: `attest_epoch` on every response and on demand; a cached authentication valid for its epoch only; re-verified on load, tab activation, export and save (V6.5) |
| MAJOR the rollback rule included supersession, which would overwrite the newer operation's work | owned failure: discard staged work (nothing was published); superseded: discard and write nothing, as today (V6.3) |

## V6.18 What changed from revision 6 (gate round 6, NO-GO ×2) — revision 7

Round 6 found every earlier blocker and major resolved at design level, revision 5's
supersession error repaired, and no new false VERIFIED claim, tolerance or second reading.
Open, both runs: one MAJOR.

| round-6 finding | revision 7 |
|---|---|
| MAJOR the trust counter can repeat (a recreated keyring, another server) and a reply could carry a generation newer than the one it checked | the generation is `{incarnation, revision}` from one atomically replaced state file; a verification reports the generation of the snapshot it used; any difference drops a cached authentication; a reply of another generation is not attached (V6.5) |

## V6.19 What changed from revision 7 (gate round 7, NO-GO ×2) — revision 8

Round 7 confirmed every other finding resolved. Open: the cache protocol, one edge per run.

| round-7 finding | revision 8 |
|---|---|
| MAJOR (A) restoring a keyring backup reused its incarnation, so a generation could repeat with other keys | a restore installs the keys under a fresh incarnation |
| MAJOR (B) a delayed generation reply could roll the page's view back and let a delayed verification attach | `trustView` rules: only the latest-issued fetch sets the incarnation; the revision only rises; a verification is void once `trustView` changes; save / export await a fetch issued after they began |

## V6.20 What changed from revision 8 (gate round 8, NO-GO ×2) — revision 9

Round 8 confirmed round 7's two answers and every other finding. Open, both runs, one MAJOR:

| round-8 finding | revision 9 |
|---|---|
| MAJOR atomic replacement does not serialise mutations: two concurrent revocations could each publish revision 8 with different key sets, and a cached authentication would match the second | ONE state file and ONE writer protocol: every mutation (creation, rotation, revocation, restore) re-reads, modifies, allocates the revision and publishes durably under an exclusive cross-process lock; mutations other than the first creation are an owner's command, never a request path; the earlier separate key-file / pointer text is replaced (V6.5 step 3) |

## V6.21 Gate status after round 9 (NO-GO ×2) — STOPPED for the owner's review

**Where the design stands.** Every finding outside the attestation key's trust protocol was
resolved by round 5 and re-confirmed in rounds 5-9 by both runs: the projection and its
bindings (G1, G2), exact server verification with attributed / authenticated evidence named
(G3), the statistics, support and area contract (G4), the local engine's O (G5), provenance as
an attestation (G6), `.fit.json` and wording (G7, G8), Auto-Fit's two-fit transaction, the typed
schema, legacy and migration; no false VERIFIED claim, tolerance or second reading of a field
remains. Rounds 5-9 each found ONE further edge in the trust protocol that bounds a page's
cached authentication — a revocation outliving a cache (5), a reused counter (6), a restored
backup and a delayed reply (7), concurrent writers (8), and now a crash after a reader saw an
undurable state (9).

**Open (round 9, both runs, MAJOR).** A reader can return a generation renamed into place
before the directory fsync; a crash can lose it and a later mutation can publish the same
`{incarnation, revision}` with other keys, so a cached authentication matches a state without
its key. Proposed, NOT yet written into V6.5: give every committed state a random identity —
`state_id`, 128 bits drawn by each mutation — and make cache validity EQUALITY of
`{incarnation, state_id}` (any difference drops it); order replies only by the issuance of the
page's generation fetches (rule (i)) and the voiding of verifications begun under another view
(rule (iii)), dropping the "revision only rises" rule (a crash may legitimately go back); then
no lost state can ever be matched again, whatever is or is not durable.

**For the owner (Q9 again, now with the cost visible).** Authenticating acceptance needs a
key, and a key needs this trust protocol — five rounds have shown it is where the remaining
risk concentrates, and it is new infrastructure (a keyring, a lock, an owner command, a cache
protocol in the page). The alternative Q9 named: narrow the state to "numerically consistent
under the verifier; acceptance as recorded by the file" — no key, no keyring, no cache
protocol; a fit is DISPLAY-CURRENT on the server's re-verified consistency and the recorded
`success` / `certified` are shown as recorded, not authenticated (a forged file could claim a
non-minimum certified; the page would say the acceptance is the file's). Options: (a) take the
proposed `state_id` fix and run the gate again; (b) narrow Q9 and remove the keyring; (c) keep
authentication but move the key protocol into 1a′'s implementation review, where it can be
tested against a real filesystem rather than argued.

## V6.22 Owner decisions (2026-10-11) — the design as approved for building

- **The key: option (b).** No server key, no keyring, no attestation, no trust-generation
  protocol: V6.5 step 3's HMAC, its keyring, `attest_epoch` / `trustView` and every rule built on
  them are WITHDRAWN. Acceptance (`success`, `certificate.certified`, a global method's `success`,
  `required`) is shown AS RECORDED BY THE FILE, labelled "as recorded — not proven"; a fit is
  DISPLAY-CURRENT on the page's bindings (V6.3, V6.4) and the server's exact re-verification of
  its numbers (V6.5 step 2), with acceptance read from O and so labelled. The re-run check
  (REPLAY-CHECKED, Q2) is the real proof of acceptance and is EASY TO FIND: a visible "Re-run this
  fit" control beside every restored result, not a menu item. Q9 is moot (no trust domains).
- **Q1-Q8: the recommendations accepted.** Q5 (one area definition) and Q8 (Auto-Fit refits
  after its charge shift) are MEASURED FIRST and the numbers shown to the owner before anything
  switches.
- **Q10: yes to all three**, each its own small unit, measured, Codex ×2, BEFORE any seal build:
  0b the local engine's link propagation and frozen finalisation; 0c a linked child's fields take
  the server's expression values; 0c′ a link across lineshapes refused on page and server.
- **Order:** (1) the averaging refusal, re-checked and deployed; (2) the three Q10 units, one at a
  time; (3) the Q5 and Q8 measurements, shown to the owner; (4) the seal build with option (b),
  stopped at the owner's review before deploy.

What option (b) removes from the design: V6.5 step 3's attestation paragraph and its keyring
bullets, the trust-generation paragraph, V6.10 Q9, V6.11 1a′'s keyring and attestation items, and
the gate history V6.16-V6.21 as far as it concerns the key (kept as the record of why). What it
keeps unchanged: R / O / D, the projection and its step 0, every page binding, the server's exact
verification (now without an attestation to check), PENDING / UNCONFIRMED, the local O,
provenance as an attestation of identity only, legacy, migration, the area and Auto-Fit
measurements, and prerequisites 0 (averaging), 0b, 0c, 0c′, 0d.
