# User note — Find Peaks now uses the Background panel's endpoint averaging

Status: READY TO SEND — deployed 2026-09-09 (Codex GO x2 after 4 rounds; full suite 811 passed, 7 skipped; C1s parity gate 3 passed).

---

Subject: XPS Fitting Studio — Find Peaks now uses your endpoint-averaging setting

From 9 September 2026, Find Peaks fits with the same endpoint averaging as the Background panel shows (3 for a new spectrum, or whatever you set), instead of always 1. Until now a manual Run Fit and a Find Peaks suggestion on the same spectrum used different averaging by default, and applying suggestions reset the panel to 1 with a notice; that reset no longer happens in normal use. If you want Find Peaks to use a different value for one run, put `"endpoint_avg": N` in its Advanced options. Nothing previously reported changes.

Skye
