# Codex adversarial review — manual-anchor cc migration (fix-manual-anchor-cc-migration) — round 3, RUN A (2026-09-02, reviewed at 07d1a53)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 112,087.
Prompt: docs/autofit/codex/anchor_cc_r3_review_prompt.txt
Round 3: GO x2 — tab-aware record-targeted restore verified; unit passes.

**Findings**

1. MINOR: The new tab-switch test catches the old live-state clobber and would fail if only anchors were restored without `peaks`/`ccShift`, but it is not a full proof of the record write set. A partial implementation could still pass while dropping `fitResult`, `nextId`, `ccMethod`, `ccLit`, ROI, or bg endpoint fields. The implementation itself writes the captured set correctly at `templates/index.html:6487`.

2. MINOR: Hostile `manualAnchors` are still accepted verbatim across load paths. I agree with the prior disposition: this is pre-existing hygiene, not escalated for this branch, though eventual validation should require numeric `{x, y}` anchors.

I found no BLOCKER or MAJOR issue in `07d1a53`. The inactive-tab restore writes all fields captured by `_autoFitSnapshot()` and all auto-fit-mutated record fields needed by later `activateTab()`: `peaks`, `fitResult`, `ccShift`, `manualAnchors`, `nextId`, and the CC/ROI/bg DOM-backed UI fields. `lineWidth` and notes are not touched by the auto-fit flow; zoom state is redrawn but preserved through the existing `_mainYMax`/`_mainXMin`/`_mainXMax` path rather than being newly mutated by the provisional fit.

VERDICT: GO
