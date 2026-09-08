# User note — endpoint averaging now defaults to 3 (new fits only)

Status: READY TO SEND — deployed 2026-09-08 (Codex GO x2 after 5 rounds; full suite 773 passed).

---

Subject: XPS Fitting Studio — background endpoint averaging now defaults to 3 for new fits

From 8 September 2026, every newly opened spectrum starts with **Endpoint avg = 3** in the Background panel instead of 1. The background's two anchor levels are then read from the mean of the three outermost points at each end of the window rather than from a single raw channel. We measured on lab data that a single-channel anchor lets one data point at the window edge move a reported atomic fraction by up to 6 percentage points; averaging three points cuts that to about 1.3, with no loss of fit quality and half the slope bias that a wider average would introduce. Nothing previously reported changes: every saved project and spectrum file carries its own setting and reopens with it, and files that predate the setting reopen at 1, exactly as they were fitted. If you prefer a different value for a particular spectrum, the field is still editable and is saved with the fit as before. One caveat: Find Peaks still fits at 1 for now (it does not read the panel yet); when you apply its suggestions the panel is set to 1 to match, with a notice. Wiring the panel value through Find Peaks is the next change.

Skye
