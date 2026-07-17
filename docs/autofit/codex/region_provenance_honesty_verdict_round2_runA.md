# Codex review — region-module provenance honesty (Units 4-5) — ROUND 2 RECHECK RUN A (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/region_provenance_honesty_recheck_prompt.txt (recheck of
round 1's 4 missing-provenance findings, commit 232be98)

**Findings**

None blocking.

**Verified**

Verified the four new records directly: asymgl_asymmetry_range (c1s.py) uses
list(ASYMGL_ASYMMETRY_RANGE), status UNVERIFIED, source reflects the
expert-reference-fit comment. satellite_offset_range_ev (c1s.py) uses
list(SATELLITE_OFFSET_RANGE), reflects the fitalg/tunable comment.
lacx_m_range (u4f.py) uses list(U4F_LACX_M_RANGE), reflects the labeled-set/
data-points comment. satellite_fwhm_ev (u4f.py) uses
list(U4F_SAT_FWHM_RANGE), reflects the labeled-set FWHM comment. git diff
232be98^..232be98 shows the edits confined to provenance() return lists;
constants and their build_candidates/slot-construction consumers unchanged.
The four new tests call the real provenance() methods and would have failed
against the parent (missing-key assertions). Did a full module-level
constant sweep of both files — no fifth missing independent disclosure
entry found. Scope: code/test changes limited to autofit/regions/c1s.py,
autofit/regions/u4f.py, and the test file across e8bf31c..232be98 — no
autofit/engine.py, autofit/methods/*.py, fitting.py, app.py, or
templates/index.html changes.

VERDICT: GO
