# Codex review — region-module provenance honesty (Units 4-5) — ROUND 1 RUN B (2026-07-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails.
Prompt: docs/autofit/codex/region_provenance_honesty_review_prompt.txt (commit e8bf31c)

**Findings**

1. U4F_LACX_M_RANGE (0.0, 100.0) — used in real candidate param ranges,
   comment discloses "labeled set 0-8.2"/UNVERIFIED. provenance() has
   lacx_alpha_range and lacx_beta_range but no lacx_m_range — the UI can
   disclose two of three LACX shape bounds but silently omits m.
2. U4F_SAT_FWHM_RANGE (1.5, 4.5) — used for all U 4f satellite slots,
   comment discloses "UNVERIFIED-empirical (labeled set 2.09-3.30 eV)" —
   no provenance record despite satellite offset/pair-separation both
   being present.
3. ASYMGL_ASYMMETRY_RANGE (0.0, 0.5) — used in AG/MG candidate
   construction, comment discloses UNVERIFIED-empirical bracketing of
   expert reference fits — provenance() only has a broad 'asymgl_family'
   record, not the numeric bound.

**Verified**

The named C1s contamination split itself is clean (floor 0.8/CONDITIONAL
literature-only; ceiling 2.0/UNVERIFIED lab-adjudication-only; old key
gone). FWHM_RANGE_CONTAMINATION unchanged; commit e8bf31c only changes
c1s.py plus the test file. U4f satellite_offset_ev already distinguishes
lit vs labeled-set sub-ranges — no change needed there. The two Unit-5
additions match the code comments and constants. The new tests call the
real provenance() methods; three C1s tests would fail against the parent,
the U4f test would pass.

VERDICT: NO-GO
