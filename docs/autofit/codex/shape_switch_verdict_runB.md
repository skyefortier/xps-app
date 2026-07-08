# Shape-switch fix review — run B

Date: 2026-07-08. Commit: d5c3222.
Prompt: docs/autofit/codex/shape_switch_review_prompt.txt

```
1. No BLOCKER/MAJOR/MINOR findings. file: n/a; concrete failing scenario: none found; fix: none. The diff is scoped to `templates/index.html` shape-switch logic plus `tests/js/shape_switch_roundtrip.test.js`. I verified `DSG_LA -> GL -> DSG_LA` preserves `laAlpha/laBeta/laM`, width lock, and curve; LACX/DS width semantics are not newly corrupted; linked-family switching stays consistent from a consistent family; accumulated stale params are already normal for `defaultPeak` and active readers branch by shape.

Verification: `node --test tests/js/shape_switch_roundtrip.test.js` passes, 5/5.

VERDICT: GO
```
