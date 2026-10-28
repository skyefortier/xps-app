# Load messages: one grouped summary that stays (owner 2026-10-28, URGENT UX)

## The problem

Opening an older multi-tab project (for example the 21-file `1-GTA … .proj.zip`) produced up to three prominent
toasts in a row: "Saved fit not restored", "Saved fit restored as STALE" and "Saved fit record cannot be read".

- **Each one concatenated every affected tab's full reason** into one block of text.
- **All three used the same element**, so each replaced the one before.
- **Each cleared after 3 s**, so nothing could be read.

## What changed (`templates/index.html`)

- **One summary per load** (`showLoadSummary`, `#load-summary`). It sits bottom-right and does not block the page.
  It stays until dismissed (✕) or until the next load replaces it. It has a title ("Project loaded: 20 tabs.") and
  one plain line per REASON, never per tab and never naming tabs. The footer reads "Press Run Fit on a tab to refit
  it. Each tab's Results panel says what happened to its saved fit." A load that restored everything shows the
  usual short green notice instead.
- **The reasons are grouped:**
  - **Peaks only**, from `_restoreDropGroup`:
    - saved by an earlier version (no envelope or energies);
    - incomplete spectrum data;
    - a background that no longer converges;
    - saved after its model was edited;
    - stored points that cannot be matched to the data;
    - an incomplete or inconsistent record.
  - **Restored stale** (shown as saved, no statistics), from `_reportStale`:
    - cannot be confirmed (saved by an earlier version);
    - today's background differs from the fit's;
    - a Voigt mix the page no longer draws. When a tab is already counted for its background, this is said as
      "also", so tabs are not counted twice.
  - **Unreadable seals.**
  - **Stack entries removed**, previously one toast per stack.
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
| project validation errors, too many tabs, ZIP size | one short red message each (the project is not loaded) | unchanged: short, single, and the load stops |
| `.fit.json` / v1 setup / history snapshot restore | single short messages | unchanged |

Not load or restore paths, so not changed here: other prominent toasts with long text still clear after 3 s. For
example, "Auto-fit discarded because the model or its background / ROI settings were edited while it was running…".
Listed for a later decision.

## Proposed, not built: "Refit these tabs"

- **The button.** A button in the summary, "Refit these N tabs", shown when a load left tabs peaks-only or stale.
- **What it does.** It runs the page's own Run Fit on each such tab in turn, through the existing start/poll path
  (`_serverFitJob`). Each tab's saved model is the start, with the tab's method, background and ROI. The summary
  shows progress ("Refitting 4 of 18…") with a Cancel.
- **What each tab gets.**
  - The outcome of an ordinary fit: a sealed record, its own undo entry, and the scattered-starts line.
  - A failure or an edit during the run leaves that tab exactly as loaded (today's rules).
  - The red-band confirmation is never auto-accepted, and an alternative solution is never applied.
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
