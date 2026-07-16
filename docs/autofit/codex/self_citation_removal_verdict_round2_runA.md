# Codex review — self-citation removal — ROUND 2 RECHECK RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/self_citation_removal_recheck_prompt.txt (recheck of
round 1's docstring + stray-file findings, commit c37e902)

**Finding**

tests/test_legacy_parity.py:33 `_raw()`'s local comment is still stale.
It says the fixture was "mechanically verified == the original
constants" and proves "legacy JSON == the frozen original values," but
the same file's corrected module docstring now says the fixture is no
longer byte-identical to the original pre-cutover JS constant after the
UCl4 removal. A future maintainer reading `_raw()` in isolation can
still misidentify the parity oracle as the original constants instead
of the deliberately edited frozen fixture.

**Confirmed**

The two module docstrings are now coherent: 52 consistently framed as
the original transcription, 51 as the current disclosed tier. `_raw()`
does read tests/fixtures/xps_legacy_snapshot.json, not the template.
The stray temp file is gone from the current worktree and git ls-files;
history shows it added in 18d3a2e and deleted in c37e902; no
runtime/test/script references to it found. Independent checksum
recomputation matches both files. Live U 4f7/2 group has 4 states, no
Fortier refs. The C 1s "S. Fortier 2026-06" attribution is a separate
curator-decision note, not this citation issue. .stage9 hits are
historical transcription evidence, not runtime-loaded. Scope clean:
only tests/test_chem_state_tier.py, tests/test_legacy_parity.py, and
the stray-file deletion changed.

VERDICT: NO-GO
