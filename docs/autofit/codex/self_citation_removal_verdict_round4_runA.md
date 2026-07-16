# Codex review — self-citation removal — ROUND 4 RECHECK RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/self_citation_removal_recheck3_prompt.txt (recheck of
round 3's overclaim-scope finding, commit fb3941b)

**Findings**

None blocking.

**Verified**

The docstring in tests/test_chem_state_tier.py is now scoped correctly:
the accounting is for the literal string "Fortier 2026" in tracked
.json/.js/.py files, not bare "Fortier," and explicitly excludes
ordinary surname mentions like "Fortier Lab." Ran the exact command
named — `git grep -n "Fortier 2026" -- '*.json' '*.js' '*.py'` — the
file set matches the docstring's enumeration exactly: the 3 .stage9
historical files, the 2 C 1s curator-attribution JSON files, and the 3
fix-discussion test/fixture files. A broader tracked search for
"Fortier 2026" only adds the review prompt .txt files under
docs/autofit/codex/ — audit prose, not missed citation-shaped
runtime/reference data. Scope checks pass: 44b2e8a..fb3941b changes
only tests/test_chem_state_tier.py; across e7b32f5^..fb3941b, no
changes to autofit/engine.py, autofit/methods/*.py, fitting.py, app.py,
or templates/index.html. The substantive fix is sound: chemical-
states.json has 11 groups / 51 states, U 4f7/2 has only the four
remaining literature-backed states, both checksums recompute exactly.
Standing back: firmly into diminishing returns on wording — the core
self-citation removal has been substantively correct since the earlier
rounds; this commit fixes the last docstring overclaim without
introducing a new one.

VERDICT: GO
