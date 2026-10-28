# Load messages: one grouped summary that stays (owner 2026-10-28, URGENT UX)

## The problem

Opening an older multi-tab project (for example the 21-file `1-GTA … .proj.zip`) produced up to three prominent
toasts in a row: "Saved fit not restored", "Saved fit restored as STALE" and "Saved fit record cannot be read".

- **Each one concatenated every affected tab's full reason** into one block of text.
- **All three used the same element**, so each replaced the one before.
- **Each cleared after 3 s**, so nothing could be read.

## What changed (`templates/index.html`)

- **One summary per load** (`showLoadSummary`, `#load-summary`). It sits bottom-right and does not block the page.
  It stays until dismissed (✕) or until another file is loaded: a project, spectrum, folder, fit or setup file
  replaces or clears it. It is bounded to the window's height: its header and ✕ stay visible and a long body
  scrolls (round 1). A load that FAILED uses the same box with a red edge (`showLoadError`). It has a title ("Project loaded: 20 tabs.") and
  one plain line per REASON, never per tab and never naming tabs. The footer reads "Press Run Fit on a tab to refit
  it. Each tab's Results panel says what happened to its saved fit." A load that restored everything shows the
  usual short green notice instead.
- **The reasons are grouped:**
  - **Peaks only**, from `_restoreDropGroup`:
    - saved without the fitted curve or the energies the fit needs (as earlier versions saved them; said as the
      missing evidence, not as a provenance claim — round 1);
    - incomplete spectrum data;
    - a background that no longer converges;
    - saved after its model was edited;
    - stored points that cannot be matched to the data;
    - a check that could not run (its numbers exceed what its arithmetic can compare — round 1: not "damaged");
    - an incomplete or inconsistent record.
  - **Restored stale** (shown as saved, no statistics), from `_reportStale`:
    - cannot be confirmed (saved by an earlier version);
    - today's background differs from the fit's;
    - a Voigt mix the page no longer draws. When a tab is already counted for its background, this is said on that
      background's line ("In 10 of them the fit also used…"), so tabs are not counted twice (round 1).
  - **Unreadable seals.**
  - **Stack entries removed**, previously one toast per stack; the stacks are named with their counts, and each affected
    stack's own legend says how many entries were removed (a runtime note, never saved — round 1).
  - **Spectrum files missing from a ZIP**, previously a separate toast.
- **Per-tab detail stays where it was:** each tab's Results panel. Dropped fits show the "saved fit of this model was
  not restored (…)" note, stale fits F1's banner with `_restoredStaleWhy`, and unreadable seals the seal's
  "record does not hold together" banner. Every full reason string is unchanged.
- **The one-spectrum load** (`_loadSpectrumFile`) uses the same summary ("This spectrum was saved by …").

## Audit of the other load / restore message paths

| path | before | now |
|---|---|---|
| project `.proj.json` / `.proj.zip` | three concatenated prominent toasts that replaced one another, 3 s each | one grouped summary that stays |
| stacks with pruned entries | one amber toast per stack (4 s) | one line in the summary |
| `.proj.zip` with missing spectrum files | a separate amber toast (4 s) | one line in the summary |
| one-spectrum load (`.spec.json`) | a long prominent toast, 3 s | the same summary |
| folder load | "Loaded N spectra", counting files it could not read; an unreadable file was skipped silently, and a FileReader error was never handled, so the load could wait forever | it counts what became a tab ("Loaded 18 spectra."); skipped files are one line in the summary; a read error is a skipped file |
| project / spectrum / fit validation errors, too many tabs, ZIP size, manifest, version | prominent or plain toasts, 3–4 s; a peak's invalid value from the file was quoted whole (round 1: 1,438 characters for a long colour) | the same box with a red edge, until dismissed or replaced; values quoted from a file are capped at 60 characters, details at 400 |
| raw spectrum and VGD parse / upload errors; "Failed to load file" | plain toasts, 4 s, with server or exception text | the same red box |
| `.fit.json` / v1 setup / history snapshot restore | single short messages | unchanged (a fit or setup file loaded successfully clears an earlier summary) |

Not load or restore paths, so not changed here: other prominent toasts with long text still clear after 3 s. For
example, "Auto-fit discarded because the model or its background / ROI settings were edited while it was running…".
Listed for a later decision.

## Proposed, not built: "Refit these tabs"

- **The button.** A button in the summary, "Refit these N tabs", shown when a load left tabs peaks-only or stale.
- **What it does.** It runs the page's own Run Fit on each such tab in turn, through the existing start/poll path
  (`_serverFitJob`). Each tab's saved model is the start, with the tab's method, background and ROI. The summary
  shows progress ("Refitting 4 of 18…") with a Cancel.
- **What each tab gets** (round 1: corrected; ordinary Run Fit does not roll a tab back "as loaded").
  - The outcome of an ordinary server fit: a sealed record, its own undo entry (Run Fit pushes it before the request),
    and the scattered-starts line.
  - Run Fit's own rules for the rest: a fit that fails or does not converge leaves the peaks and result as they
    were; a tab edited while its fit runs keeps the edit and its result is discarded.
  - An alternative solution is never applied. Its red-band confirmation belongs to "Use this solution", not to
    Run Fit.
  - **Explicit semantics needed for the batch:**
    - Run Fit falls back to the local engine on a transport failure. The batch must not: like "Use this solution",
      it should stop or skip that tab and say so.
    - Its undo entries are per tab, not one entry for the batch.
- **What it must not be:** Batch Fit, which runs the local engine only (a starting point, not a reportable result).
- **Cost.** About 1–30 s per tab with Trust-Region and scattered starts; one fit at a time per worker, so a 20-tab
  project is minutes. The project is changed but not saved.
- **Decisions needed:**
  - which tabs: peaks-only and stale only, or every legacy fit, current ones included;
  - each tab's saved method, or the dropdown's;
  - whether to offer "Save project" when it finishes.

## Tests

- `tests/test_browser_load_summary.py` (real browser and server). It covers:
  - the two committed multi-tab legacy projects: the summary is still shown after 6 s, has no tab names and no toast,
    can be dismissed, and each tab's Results carries its reason;
  - unreadable seals, pruned stack entries and a ZIP with a missing file, said once;
  - a fully restored project, which gets the green notice;
  - a folder load with one unreadable file.
- `tests/test_browser_background_not_converged.py` now reads the summary and each tab's own reason (the full reason
  strings are asserted unchanged).
- `tests/js/fit_acceptance.test.js` and `tests/js/per_tab_state.test.js` (`_lastLoadSummary` is class A,
  UI-transient).
