# Seal 1c — findings

## Legacy census (step 7, plan §11)

Every saved fit committed to the repository predates the seal. After step 7 the page installs seals only, so these
fits — and every student's save from before this release — reach the legacy path, which must be main's.

`scripts/seal_legacy_census.py` loads each committed project (`docs/autofit/test_data/*.proj.zip`) through two
running pages — this branch and main (ef750f6) — re-saves it, and compares tab by tab. Result
(`legacy_census.json`, 2026-10-15):

| | |
|---|---|
| projects / spectrum tabs with a saved fit | 7 / 121 |
| a seal installed on load | 0 |
| loaded LEGACY (the fit restored by the legacy adapter) | 81 |
| dropped to peaks only (legacy restore refused, as main) | 40 |
| restore verdict identical to main's | 121 / 121 |
| re-save identical to main's except the two new fields | 121 / 121 |
| new field `provenance` (null for a restored fit; V6.8) | 121 tabs |
| new field `ui.fitMethod` (§8.5) | 6 tabs |
| dropped fits keeping a record as provenance | 0 / 40 (none of the 121 carries a record: all predate 2026-10-10) |

The 81 / 40 split is the restore census already recorded in CLAUDE.md (81 STALE unconfirmed, 40 peaks only).
Pinned without main by `tests/test_browser_seal_step7.py::test_every_committed_saved_fit_loads_legacy_and_re_saves_without_a_seal`.
