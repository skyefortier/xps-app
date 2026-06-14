P0 FINDINGS: none

P1 FINDINGS:
- `app.py`, `templates/index.html`: validation failures are converted to `null`, then `{}` after constant removal — survey markers, tab detection, preset suggestions, RSF fallback, and NIST results silently disappear instead of surfacing a deployment/data failure.
- `xps_reference.py`: schema validation accepts any in-range numeric values and runtime performs no parity check — valid-but-drifted `be_ev` values can silently move markers, alter RSF/tab inference, and publish incorrect chemical-state energies.
- `xps_reference.py`, `templates/index.html`: duplicate element symbols, orbitals, or `orbital_key` values are not rejected — accessor object construction silently overwrites earlier records, producing incomplete or incorrect reference views.

P2 FINDINGS:
- `templates/index.html`: `_accChemicalStates()` adds `tier`, so it is not strictly `CHEMICAL_STATES`-shape-identical; parity tests rebuild JSON directly and never test either accessor’s actual output.
- `tests/test_legacy_parity.py`: cached `.stage9/legacy_raw.json` is regenerated only when absent — a stale artifact can let parity tests compare against outdated constants rather than current template source.
- `xps_reference.py`: cache invalidation relies solely on file mtimes — deployments or file replacement preserving timestamps can retain stale legacy values for the process lifetime.
- `templates/index.html`: removing `ccShift` is correct only while the chart x-scale is corrected binding energy; no shown regression test enforces that axis convention, so later raw-axis reuse would misplace markers.

