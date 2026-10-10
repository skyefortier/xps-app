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
