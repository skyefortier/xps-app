# Codex review — Unit R3 chem-state sourced-or-skip audit — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 137,187.
Prompt: docs/autofit/codex/refpop_unit3_chemstates_prompt.txt

1. MINOR [tests/test_chem_state_tier.py](/Users/skyefortier/xps-app/tests/test_chem_state_tier.py:77): the compound-summary self-invalidating pin only inspects `extract_chem_claude/groups_4a.json` and only checks raw HTML absence in `extract_chem_claude`. Concrete failure scenario: `groups_4b.json` or `extract_chem_codex/*.html` gains per-row refs/evaluated markers/raw artifacts while 4a remains unchanged, and this R3 test still passes. I verified today’s artifacts manually: both 4a and 4b have only `compound`/`be_ev` row keys, zero ref/star/evaluated fields, and no retained HTML artifacts, so this is test discrimination weakness, not a current emission path.

No BLOCKER/MAJOR findings.

Audit judgment: the sparse outcome is correct. `85b7a70` is the latest commit touching `tests/test_chem_state_tier.py`; `git show` lists only `docs/autofit/PROGRESS.md` and `tests/test_chem_state_tier.py`, with no `data/xps` changes. Active `templates/index.html` has no live `CHEMICAL_STATES` constant. Element pages lack compound/state context. Compound summaries have group/page evidence but no per-row refs, no evaluated markers, and no sha-pinned raw artifact chain; group-level URL/timestamp alone does not satisfy the legacy chemical-state record contract, where every emitted state carries its own editorial `ref`. Bridge pass-through also checks out: direct inspection returned 11 groups / 52 states / 0 bad, all with `ref`, `source`, and `UNVERIFIED`.

I could not run pytest in this read-only sandbox because pytest needs a writable temp directory for capture, so I used direct file/code inspections and Python checks instead.

VERDICT: GO
