# Fit recording — Codex round 2, run B (commit e8421dc)

Reviewed `52e5b4a..e8421dc`, focusing on the fixes after `aa7f31e`.

**MAJOR — the local/Batch certificate can incorrectly report `moved: false`.** [_localFitRecord](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8582) derives `moved` solely from centre displacements. A certificate restart that changes width or amplitude while centres are locked therefore says “not moved.”

Reproduced with a Gaussian on 280–290 eV at 0.05 eV spacing: true amplitude 100, FWHM 0.1; starting amplitude 10, FWHM 0.2; centre locked at 285. The fit takes one certificate restart and changes parameters after the first stop, but records:
```json
{"restarts":1,"moved":false,"centre_moves":[],"largest_centre_move":null}
```
Derive `moved` from accepted certificate restarts or the complete parameter displacement. Keep centre movement as a separate measurement. The local background record also still lacks the `effect` information identified in round-1 run B.

Round-1 disposition:

| Finding | Round 2 |
|---|---|
| `/api/analyze` drops record | Resolved |
| Local/Batch record incomplete | **Partially resolved; MAJOR remains above** |
| `.fit.json` drops record | Resolved |
| PNG drops record | Resolved |
| CSV/XLSX/TSV lose details | Resolved through lossless JSON |
| Numerical version absent | Resolved; bump rule documented |
| Export tests check labels/in-memory workbook | Resolved: full-record assertions and serialized XLSX readback |

The other requested regression checks were favorable:

- **First-stop snapshot:** 37 local-fit calls across 28 cases produced bit-identical existing outputs against `main`.
- **Background certificate property:** ignored by JSON and numeric array operations; no production comparison or save leakage found.
- **Imported provenance:** no changed designation, banner, Batch acceptance, reportable/caveat assignment, or current/stale decision found.
- **PNG:** the actual insertion helper passed decoder verification for RGB, RGBA, palette and grayscale images; pixels and Unicode metadata survived.
- **Meta tag:** hostile quotes, markup, ampersands and Unicode escaped and round-tripped safely. `served_the_page` accurately qualifies the identity as the serving worker’s software.
- **NUMERICS_VERSION:** its meaning and maintenance trigger are stated in code.

Validation: 11 focused Python tests passed; 124 selected JS tests passed. Writable-fixture/subprocess checks were blocked by the read-only sandbox; browser suites were not rerun. Workspace unchanged.

VERDICT: NO-GO
