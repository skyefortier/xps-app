No BLOCKER or MAJOR findings. Round 4 closes the backend-shape validation gap.

**MINOR, non-blocking — contradictory refusal wording.** [fitting.py:1507](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/fitting.py:1507) reports “different lineshape (GL, GL)” when different backend shapes carry identical frontend labels. Report the differing backend names here. **Non-physical inputs:** no abnormal spectrum required, but this needs inconsistent, manually supplied API metadata; the page cannot generate it. Refusal works correctly.

Validation:

- **28 HTTP probes:** all seven invalid-graph cases returned immediate 400s across all four routes.
- **21 runtime page probes:** Run Fit, alternative starting models, and Batch Fit refused before undo/spinner/request or target changes.
- **138 JavaScript tests and six focused Python tests passed**, including builder/write-back parity and local refusal.
- The tested valid fit’s complete result—including seed, record, and restarts—was identical with and without `frontend_shape`.
- Census reproduced **121 tabs, 530 peaks, 67 links, zero refusals**. Truthy-link semantics, family switches, valid chains and consistent string/number IDs remain supported. Auto-Fit builds unlinked models.

Some cross-shape links can fit as drawn; their refusal follows the owner’s documented blanket policy.

HTTP probes mocked session loading; runtime page probes used extracted functions with boundary stubs. Real-browser fixtures were not rerun under read-only restrictions. Source-pattern tests establish wiring, not exhaustive behavior.

No files changed. Sibling units excluded.

VERDICT: GO
