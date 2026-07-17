# Codex review — region-module provenance honesty (Units 4-5) — ROUND 2 RECHECK RUN B (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/region_provenance_honesty_recheck_prompt.txt (recheck of
round 1's 4 missing-provenance findings, commit 232be98)

**Findings**

None blocking.

**Verified**

Verified all four new entries directly on disk against their constants and
code comments: asymgl_asymmetry_range matches (0.0, 0.5) and the
UNVERIFIED-empirical expert-reference-fit comment; satellite_offset_range_ev
matches (5.5, 7.0) and the fitalg/UNVERIFIED-tunable comment; lacx_m_range
matches (0.0, 100.0) and the DATA POINTS/labeled-set/UNVERIFIED comment;
satellite_fwhm_ev matches (1.5, 4.5) and the UNVERIFIED-empirical
labeled-set comment. git diff --unified=0 232be98^..232be98 on both region
files shows only additions inside provenance() return lists — no
constants, build_candidates, slot construction, or param-range code
changed. The four new tests call the real provenance() methods and would
have failed with missing-key assertions against the parent. Did an
exhaustive module-level constant sweep of both files (enumerated every
constant in each) and found no fifth independent consumed constant with
comment-disclosed provenance still missing. Scope: no changes in
autofit/engine.py, autofit/methods/*.py, fitting.py, app.py, or
templates/index.html across e8bf31c^..232be98; code-impact scope limited
to the two region modules and the provenance test file.

VERDICT: GO
