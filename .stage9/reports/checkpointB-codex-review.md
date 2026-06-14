P0 FINDINGS:

- `tests/test_legacy_parity.py::_raw`: parity oracle disappears with the constants — after deletion, extraction cannot reconstruct the “before” values, so the gate cannot run or detect post-cutover JSON drift.
- `tests/test_legacy_hardening.py::test_js_accessor_functions_deep_equal_constants`: tests only the pre-deletion implementation — retained constants may satisfy the accessor through its normal or fallback branch; no test executes a constants-absent build and proves JSON is the sole source.
- `accessor load-failure path`: deletion changes fallback behavior to `{}` — no rendered-route test forces missing, malformed, or checksum-invalid legacy data and asserts a loud failure; users could silently receive empty markers and chemical states.

P1 FINDINGS:

- `.stage9/accessor_parity_check.mjs`: implementation is omitted from review — the Python wrapper proves only that the script prints `ACCESSOR_PARITY_OK`; normalization, projection, JSON-to-JSON comparison, or accidental use of constants could mask extra fields and value drift.
- `parity gate / allowlist enforcement`: A1 is documentation plus a regex assertion, not a computed before/after diff constrained to one approved path — unrelated behavioral changes can ship without an unallowlisted-delta failure.
- `_accSurveyElements` / `_accChemicalStates`: no forced post-deletion branch coverage — cache initialization, stale cached constants, payload absence, and fallback precedence could all differ after constants are removed.
- `chemical-state accessor boundary`: source records contain `tier`, but no shown test explicitly asserts the user-facing objects have exactly `{state, be, ref}` after deletion — advisory tier metadata could leak into modal behavior or rendering.
- `legacy checksum`: checksum is self-authored metadata, not an independent oracle — a changed JSON file with a recomputed checksum passes once the constants-based comparison is gone.
- `tests/test_legacy_parity.py`: Python dictionary equality ignores insertion order — reordered elements, orbitals, or chemical-state groups can pass despite changing iteration-dependent UI ordering.

P2 FINDINGS:

- `test_survey_marker_axis_convention_locked`: regex source inspection verifies one spelling of the draw expression, not runtime marker placement — alternate code paths, transforms, or cached marker data could still apply the shift.
- `test_counts_match_known_totals`: totals permit substitutions, reorderings, and redistributed entries — it does not protect identity or presentation behavior.
- `test_legacy_loads_through_reference_payload`: asserts only collection lengths — it does not prove payload shape, ordering, exact field projection, or that accessors consume that payload.
- `“conflicts flagged, not applied” claim`: tests establish legacy JSON equality only while constants exist; no test cross-checks the final served payload against conflict-resolution overlays, so merge precedence could apply curated values during assembly.
