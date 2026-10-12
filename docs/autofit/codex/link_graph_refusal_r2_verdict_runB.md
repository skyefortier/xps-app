**MAJOR — The Python twin still fits a graph the page refuses.**

[The builder](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/autofit/reference.py:149) stringifies the link before validating the original graph. With parent `id: 1` and child `linked: "1"`:

- The saved-file loader accepts both peaks.
- The page correctly refuses the link: its exact lookup cannot find parent `"1"`.
- The twin converts both references to `"1"`, silently creating a valid server link.
- [The actual `refit_record` path](/Users/skyefortier/xps-app/.claude/worktrees/link-graph/autofit/parity.py:237) returned **`success: true`**, recording fitted centers `284.725881994463` and `286.725881994463`.

This leaves the round-one orphan fix incomplete: serialization can erase evidence of a missing parent. Validate the original Python graph using the page’s ID-matching semantics before converting IDs. Add both mixed-type directions to the twin refusal tests; preserve valid all-number and all-string graphs.

**Non-physical inputs required:** No abnormal physical values; this requires mixed-type saved reference metadata.

The remaining evidence was reassuring:

- All 18 HTTP probes—six invalid graph cases across `/api/fit`, `/api/fit/start`, and `/api/analyze`—returned 400.
- Falsy links and family-switch tests passed. Run Fit and Batch Fit guards precede their fitting mutations.
- The census reproduced **121 tabs, 530 peaks, 67 links, zero refusals**.
- `frontend_shape` left the tested complete fit result, including seed and record, unchanged. Both pinned Python/page parity tests passed.

The blanket shape rule remains stronger than “cannot fit as drawn”: a GL child of a Voigt parent fitted successfully under main’s validator, both at mix `0.5`; HEAD refuses it. That follows the explicitly authorized cross-shape prohibition, so it is **not another finding**.

The new tests prove their sampled cases, but the twin orphan test misses the serialization collision above. Focused JS checks and five Python tests passed; browser fixtures were not rerun under the read-only restriction. No files changed. Sibling units 0b and 0c are excluded.

**VERDICT: NO-GO.**
