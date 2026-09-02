# Codex adversarial review — manual-anchor cc migration (fix-manual-anchor-cc-migration) — round 2, RUN B (2026-09-02, reviewed at edde216)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 86,775.
Prompt: docs/autofit/codex/anchor_cc_r2_review_prompt.txt
Round 2: run A NO-GO / run B GO (stricter governs) — run A found the tab-switch-during-auto-fit restore corrupting the newly active tab (pre-existing for peaks/ccShift/DOM; anchors joined it).

**Findings**

1. MINOR - Undo still snapshots only `state.peaks`, so manual anchors remain outside Ctrl-Z. This is pre-existing and acceptable for this revision.

2. MINOR - Manual anchors are still restored verbatim in all load paths, including the new `.spec.json` path. Malformed anchor values can cause bad manual-background math/rendering, but this is broader file-schema hygiene, not a new major regression from the fix.

The round-1 MAJORs are addressed. `_autoFitSnapshot()` deep-copies anchors, so later in-place `a.x -= delta` mutations cannot alias into the snapshot, and `_autoFitRestore()` restores them on the post-provisional failure paths: upload/fetch/fit failures, tab-switch discard, and `applyAutoFitResult()` validation failure. `_loadSpectrumFile()` restores anchors before `renderPeakList()`/`updatePlot()` while the created tab is active, so saved `.spec.json` anchors round-trip.

I could not run pytest/Playwright in this sandbox; this is review-on-merits only.

VERDICT: GO
