# Codex review — Unit R3 chem-state sourced-or-skip audit — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 105,869.
Prompt: docs/autofit/codex/refpop_unit3_chemstates_prompt.txt

1. MINOR [tests/test_chem_state_tier.py](/Users/skyefortier/xps-app/tests/test_chem_state_tier.py:77): the stale-classification pin only inspects `extract_chem_claude/groups_4a.json` and raw `.html` in `extract_chem_claude`, not the parallel `extract_chem_codex/groups_4b.json` path. Failure scenario: a future 4b rerun gains row refs or raw artifacts under `extract_chem_codex`; this test would still pass. I verified current 4b has only `compound`/`be_ev` row fields and no raw artifacts, so this is not a current emission path.

No BLOCKER/MAJOR findings. The audit outcome is sound: `85b7a70` changes only `PROGRESS.md` and `tests/test_chem_state_tier.py`; `data/xps` has zero diff. The frontend constant was removed, element pages lack compound/state context, compound summaries lack per-row refs/star/eval/sha/raw artifacts, and group `source_url` alone does not satisfy the legacy per-state `ref` contract. Focused verification passed: `11 passed`.

VERDICT: GO
