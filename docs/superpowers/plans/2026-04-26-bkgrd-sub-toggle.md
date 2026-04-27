# Background-Subtracted View Toggle — Feature Specification

**Date:** 2026-04-26
**Status:** Planning. Claude Code will produce an implementation plan next via `/superpowers:write-plan`; that plan must be reviewed before execution.
**Rollback tag:** to be created before implementation as `pre-bkgrd-sub-toggle`
**Author:** Skye Fortier, with design assistance from Claude

---

## Goal

Add a toggle pill labeled "Bkgrd Sub" to the chart's pill button row, alongside Envelope, Individual peaks, Fill peaks, Residuals, and Invert BE. When activated, the chart redraws with the background subtracted from the spectrum, peak fills, and envelope, so the user sees a flat-baseline view useful for fit-quality assessment and publication-style figures.

This is a presentation-only feature. No fitting math changes, no backend changes, no algorithmic logic.

---

## Design rationale

### Why this feature

XPS spectra ride on a curved background (Shirley, Tougaard, etc.). In the current view, peak fills are drawn on top of this curved baseline, which makes peaks look "wavy" and forces the user to mentally subtract the background to judge fit quality. Background-subtracted view is the standard presentation in XPS publications and is significantly easier to read for both fit-quality assessment and visual communication.

### Key design decisions

**Global toggle, matches existing pill behavior.** The other pill buttons (Envelope, Individual peaks, etc.) are global toggles that affect all tabs at once. The new pill follows the same convention for consistency. Per-tab state would have been more flexible but inconsistent with established UX.

**Disabled when no background is set.** If the tab's background method is "None" or no background has been computed, there is nothing to subtract and the toggle is meaningless. The pill is rendered in a faded/disabled state in this case, with a tooltip explaining why.

**Hide the background line entirely in subtracted view.** A flat-at-zero line would be technically accurate but visually noisy. Hiding it is cleaner and matches what users expect from a "subtracted view."

**Draw a thin y=0 reference line.** Since negative values can appear in subtracted view (from background-subtraction noise at endpoints), a reference line at y=0 helps the user orient. Existing gridlines aren't reliable for this because the y-axis range shifts substantially in subtracted mode.

**Don't clip negative values.** Honest rendering wins over visual cleanliness. Negative values at endpoints are diagnostic — they tell the user the background or ROI may be off. Clipping would hide that signal.

**Hover tooltip shows the number alone, no mode label.** Keeps the tooltip clean. The mode is obvious from the chart shape.

**Off by default for new tabs and old saves.** Preserves current behavior. Users who prefer subtracted view can toggle it on; the choice is then persisted in their saved files.

**Persisted in save files.** Different users have different preferences. The toggle state is part of the visualization state of a saved fit, just like ROI and background method.

---

## Specification

### UI placement

A new pill button labeled "Bkgrd Sub" appears in the chart's pill button row, after "Residuals" and before "Invert BE". Visually identical to the other pills (rounded, blue when active, white/outlined when inactive).

### Toggle states

The pill has three states:

1. **Active (subtracted view ON)** — solid blue fill, white text. Chart shows background-subtracted data.
2. **Inactive (subtracted view OFF, available)** — white fill, blue outline. Chart shows raw view (current behavior).
3. **Disabled** — faded white fill, gray text/outline, "not allowed" cursor. Pill is not clickable. Tooltip on hover: "Background subtraction is unavailable when no background method is set."

The disabled state activates whenever the tab's background method is "None" or no background data is available. When the user changes the background method to a real one (Shirley, Tougaard, Smart), the pill re-enables and remembers its previous active/inactive state.

### Chart rendering changes when toggle is ON

When subtracted view is active:

**Spectrum line.** Each data point's intensity is replaced with `raw[i] - background[i]`.

**Peak fills.** Each individual peak fill is drawn from y=0 (not from the background line). The peak's contribution is unchanged; only its baseline shifts.

**Envelope (red total fit).** Drawn as the sum of individual peaks from y=0, not from background.

**Background line.** Hidden entirely.

**Y-axis bounds.** Recompute to fit the subtracted data range. Lower bound extends below zero to accommodate negative values without clipping.

**Y=0 reference line.** A thin gray horizontal line at y=0 is drawn behind all data series.

**Y-axis label.** Unchanged ("Intensity (counts/s)"). XPS publication convention preserves this label in both views.

**Hover tooltip.** Shows the subtracted value as a plain number (e.g., "1,234 cps"), no mode indicator.

### Chart rendering when toggle is OFF

Identical to current behavior. No changes from today's app.

### Interaction with running fits

The toggle is disabled while a fit is in progress (auto-fit, manual run-fit, batch fit, propagate fit, etc.). The pill takes the disabled visual state until the fit completes, at which point it returns to its previous interactive state.

This applies regardless of whether the toggle was ON or OFF when the fit started. The chart continues to render in whatever mode it was in; the user simply can't change modes mid-fit.

### Persistence

The toggle state is part of the saved fit/project state.

**File formats affected:**
- `.fit.json` — adds a new field `bgSubtractedView: boolean` at the top level (or wherever the visualization state lives).
- `.proj.json` — same field, included per-tab if project files store per-tab state.

**Backward compatibility:**
- Old `.fit.json` and `.proj.json` files without this field load as if `bgSubtractedView: false`. No migration needed.
- New saves always include the field, even when false.

**Default for new tabs:** `false` (off).

**Default for old loaded files:** `false` (off, since field is missing).

### Interaction with other pills

The new toggle is independent of all other pills. Specifically:

- **Envelope, Individual peaks, Fill peaks** all continue to honor their own toggles. In subtracted view, these elements just draw from y=0 instead of from the background line.
- **Residuals** are already shown as percentages in the lower plot, so they're already background-agnostic. No change.
- **Invert BE** flips the x-axis. The new toggle flips the y-baseline. They compose cleanly: subtracted + inverted should work without special handling.

### Edge cases

**No background computed yet.** If the user hasn't run a background calculation, the pill is disabled (same as background method = None).

**Background method changed mid-session.** When the user switches background methods (e.g., Shirley to Tougaard), the chart re-renders with the new background. If subtracted view is on, the new background is what gets subtracted. No special handling.

**Background calculation in progress.** If the background is being recomputed (rare but possible during ROI or method changes), the toggle behavior should match other UI elements — either disabled briefly or showing stale subtraction until the new background lands. Match existing patterns; don't invent a new one.

**Empty or single-point spectrum.** Defensive only: if the spectrum has zero or one points, the toggle should not crash. Either disable or no-op.

**Background array length mismatch with spectrum.** Should never happen, but defensive: if it does, disable the toggle and log a warning to the console.

---

## Scope exclusions

- No changes to background calculation logic
- No changes to fitting math
- No backend changes (`fitting.py`, `app.py` untouched)
- No new background methods
- No per-tab toggle state (global only)
- No animation between modes (instant flip)
- No keyboard shortcut (could be added later)
- No "subtracted view" indicator anywhere besides the pill itself
- No changes to how the residuals plot is rendered
- No changes to figure export (the export already captures whatever the chart currently shows, which is the right behavior)

**Deferred (future enhancement):** Subtracted-mode smoothing and derivatives. The current implementation only re-computes the spectrum line itself; smoothing, derivative, and overlay-tab overlays are hidden in subtracted view (with the controls visibly disabled to explain why). A later enhancement could re-derive those overlays from the bg-subtracted ROI data so they remain usable.

---

## Implementation notes for Claude Code

Architectural constraints:
- All changes in `templates/index.html`. No backend edits.
- Reuse existing pill button styling and event-handling patterns.
- Reuse existing chart re-rendering logic when toggle changes.
- Persist the new state field in the existing save/load JSON paths; do not invent a new file format version.
- Match the pattern used by other global toggles for state storage (likely a single boolean on the global state object).

Expected size: 200–400 lines of frontend code, mostly chart re-rendering glue.

Testing strategy:
- Browser checklist on real spectra: toggle on/off, verify shapes are drawn correctly from y=0, verify negative regions render without clipping.
- Save/load roundtrip: save with toggle ON, reload, confirm toggle returns ON.
- Backward compatibility: load an old `.fit.json` saved before this feature, confirm it opens with toggle OFF and no errors.
- Regression: confirm raw-view rendering is byte-identical to current behavior when toggle is OFF.

---

## Browser verification (for Claude Code's plan to specify)

The following test cases should be in the implementation plan:

1. **Toggle visibility and placement.** New pill appears between Residuals and Invert BE. Visually consistent with other pills.

2. **Disabled state.** On a tab with background method = None, the pill is faded and non-interactive. Tooltip explains why.

3. **Active state.** Toggle ON: spectrum, peaks, and envelope all draw from y=0. Background line hidden. Y=0 reference line visible. Y-axis bounds include any negative values.

4. **Inactive state.** Toggle OFF: chart renders identically to current behavior.

5. **Live re-render.** Toggling while looking at the chart re-renders immediately, no page reload needed.

6. **Save/load.** Save a fit with toggle ON, reload the page, drag the file back. Toggle returns to ON.

7. **Old file compatibility.** Load a `.fit.json` saved before this feature exists. No errors. Toggle is OFF.

8. **Disabled during fit.** Run an auto-fit. While the fit is running, the toggle is disabled. After the fit completes, the toggle re-enables and the chart respects whichever state it was in.

9. **Composition with Invert BE.** Toggle Subtracted ON, then Invert BE. Both work as expected.

10. **Composition with Envelope/Individual peaks/Fill peaks.** Each of those pills still hides/shows its element independently in subtracted view.

11. **Negative regions.** Pick a spectrum with noisy endpoints. Toggle ON. Confirm negative values are visible (not clipped) and the y-axis extends below zero.

12. **No background computed.** Set background method to None. Confirm pill becomes disabled. Set it back to Shirley. Confirm pill becomes enabled again and remembers its previous state.

---

## Rollback procedure

If this feature introduces regressions:

```bash
cd ~/xps-app
git revert pre-bkgrd-sub-toggle..HEAD
git push origin main
ssh root@137.184.183.202 "cd /opt/xps-app && git pull && systemctl restart xps-app"
```

---

## Related history

- 2026-04-24 — Auto-Fit C1s Graphite v2 shipped (autofit-v2-shipped tag).
- 2026-04-24 — Future considerations memo committed for non-UCl₄ samples.
- 2026-04-26 — This specification.
