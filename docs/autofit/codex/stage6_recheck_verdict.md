**Finding**

[tests/test_machine_tier.py:233](/Users/skyefortier/xps-app/tests/test_machine_tier.py:233) - MAJOR: the URL regex still accepts `query_all_dat_el.aspx` via `\.aspx?`. All committed acquisition URLs are `.asp`, and `.stage9/acquire_expand.py` also targets `.asp`.  
Failure scenario: provenance could be changed to an archived `.aspx` endpoint for the same element/timestamp while artifact bytes still hash correctly, and this test would pass despite no longer pinning the exact retired SRD-20 query endpoint.  
Fix: make the endpoint exact: `query_all_dat_el\.asp`. Port handling is otherwise tight: `:81` fails, case variants fail, and only absent port or `:80` pass.

**Disposition**

Blocker 1 is closed. `_acquisition_records()` now derives all 51 `p["acquisition"]` records from provenance, and the raw `<tr>/<td>` plus `<b>*</b>` parser, agent check, and artifact SHA check run across that set. `Rh-3d5/2` and `Mg-2p3/2` are both in that set and would now be caught if tampered away from the committed starred artifact value.

Blocker 2 is closed. `_subshell()` normalizes every machine orbital format currently present (`1s`, bare `3p/3d/4d`, and spin-split `2p3/2`, `3p3/2`, `3d5/2`, `4p3/2`, `4d5/2`, `4f7/2`). A bare `3p` and `3p3/2` for the same element collide on `(element, "3p")` and fail.

I could not run pytest because `pytest` is not installed here (`python3 -m pytest`: `No module named pytest`). I did direct JSON/artifact checks instead: 51 acquisition records, no missing starred artifact matches, no duplicate starred ambiguity for emitted lines, no SHA mismatches, no agent mismatches.

VERDICT: NO-GO (blockers: 0; unresolved major: archive URL regex still accepts .aspx)
