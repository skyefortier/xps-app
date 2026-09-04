# Codex adversarial review — bg window inclusive (fix-bg-window-inclusive, unit 1c) — round 1, RUN B (2026-09-03, reviewed at bad191c)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: n/a.
Prompt: docs/autofit/codex/bg_window_1c_review_prompt.txt
Evidence at review time: node --test tests/js/*.test.js 155 pass / 0 fail / 3 known-gap todo; pytest tests/ on the branch worktree 758 passed, 7 skipped (6 known env-gated + 1 worktree-only skip: local-only {7,8}* C1s datasets absent from the worktree).
Round 1: NO-GO x2 — same MAJOR both runs: committed scripts/bg_window_pointsets.py still models 'after 1c' as nearest+1, so the memo's 166/166 inside-range claim was not reproducible from the shipped generator.

**Findings**

1. MAJOR [scripts/bg_window_pointsets.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/scripts/bg_window_pointsets.py:1): the committed point-set evidence script still defines “after 1c” as nearest-index plus one, not the implemented inside-range rule. Running it reports `js==after: 151`, not the memo’s claimed 166/166, so the archived justification is not reproducible from this script as stated.

2. MINOR [autofit/reference.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/autofit/reference.py:4): leaving `bg_indices()` on the old rule is acceptable for this isolated 1c unit, but the module docstring still says it reconstructs the exact frontend `/api/fit` inputs. After 1c that is only true for legacy committed fixtures; new post-1c expert fits will be reconstructed one point short until 1a.

3. MINOR [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/templates/index.html:4370): `_bgWindowIndices` is correct for the app’s normal sorted grids, blank/NaN bounds, outside bounds, one-point windows, ascending grids, and duplicate sorted points. Two residual edges are worth documenting or testing: non-monotonic saved `rawBE` can make “first match to last match” include out-of-window rows, and frontend indices are computed before `uploadToBackend()` rounds BE to 4 decimals, so boundary semantics can differ by sub-0.0001 eV even though row count/order are preserved.

4. MINOR [tests/js/bg_window_indices.test.js](/Users/skyefortier/xps-app/.claude/worktrees/fix-bg-window-inclusive/tests/js/bg_window_indices.test.js:122): the new JS tests plus the browser first case are sufficient to catch the old nearest-exclusive bug and the rejected nearest-plus-one variant. The browser second case alone is coincidental on main, but it is backed by the helper unit test at lines 48-55, so I do not see a wrong primary implementation that passes the full added set.

VERDICT: NO-GO — committed point-set evidence still models the rejected nearest+1 rule as “after 1c,” so the memo’s 166/166 rule-choice claim is not reproducible from the shipped evidence.
