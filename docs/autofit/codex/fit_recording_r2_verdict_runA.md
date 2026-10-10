# Fit recording — Codex round 2, run A (commit e8421dc)

Reviewed `52e5b4a..e8421dc`, focusing on the changes after `aa7f31e`. **Two MAJOR gaps remain in local/Batch Fit recording.**

1. **The local background record still omits its effective inputs.** `backgroundVerdict` contains no `effect`: effective window, averaging, and manual anchors remain absent. This leaves round-1 run B’s background-effect finding unresolved; lossless exports faithfully preserve an incomplete record. [index.html:8577](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:8577)

2. **The new certificate movement record omits linked components.** Movements are collected from `paramMap`, which excludes linked peaks. Reproduced using committed `C1s Scan_4` with a zero-amplitude child linked to component 4: certification restarted once, moving the parent and child by approximately `0.00010326510437 eV`, but `centre_moves` omitted the child entirely. Record every component’s centre displacement, including linked components. [index.html:9483](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/templates/index.html:9483)

Round-1 disposition:

| Finding | Round 2 |
|---|---|
| `/api/analyze` drops record | Resolved |
| Local/Batch record incomplete | **Partially resolved; findings above** |
| `.fit.json` drops record/provenance | Resolved |
| PNG carries no record | Resolved |
| CSV/XLSX/TSV lose fields/precision | Resolved through full JSON |
| Numerical version absent | Resolved; bump policy explicitly stated |
| Export tests check labels/in-memory XLSX | Resolved for the cited export gaps; local completeness gaps still pass |

The requested regression checks were favorable:

- **First-stop snapshot:** existing results were bit-identical against main across 54 synthetic fits and five committed spectra, including a certificate restart.
- **Background property:** no leakage into serialized arrays or production numerical comparisons found.
- **Imported provenance:** no changes found to designation, banners, Batch acceptance, reportable/caveat classification, or current/stale decisions.
- **PNG:** decoded to identical pixels; chunk CRCs and Unicode metadata round-trip passed.
- **Meta/software:** hostile quotes and markup escaped safely. `served_the_page` honestly identifies the serving worker, with that explicitly limited role.
- **Numerics version:** maintenance meaning is documented beside the constant.

Validation: 11 focused Python tests passed; 172 JS checks passed, with four Python-backed checks blocked by temporary-directory restrictions. Full browser suites were not rerun. Workspace unchanged.

VERDICT: NO-GO
