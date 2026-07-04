# Codex verdict — adjudication-implementation unit, 2026-07-04

Prompt: `adjudication_unit_review_prompt.txt` (commits a5fcd58, b25c0e3,
3d88ea0). Run TWICE per the severity-nondeterminism rail — both runs
completed and both returned **VERDICT: GO**; the stricter reading of the
shared findings governs the dispositions below.

## Findings (both runs independently converged on the same MAJOR)

1. **MAJOR** `autofit/engine.py:345` — the width-aware AREA-ratio guard was
   sufficient for the Cl 2p PV candidates but not for the general branch:
   it required only same `line_shape` (+ shared `gl_ratio` for PV). For
   `ASYM_GL` area also depends on `asymmetry`; for DS/DS_G/LACX the area is
   not `height × width` at all (and DS_G's width param is `m_gauss`, not a
   total FWHM). Failure scenario: a future free-width doublet on a non-PV
   shape silently enforces a WRONG area ratio.
   **Disposition — FIXED same-session:** the area-linked excess branch now
   refuses every shape except PSEUDO_VOIGT-with-shared-gl_ratio (explicit
   ValueError; shape-specific area factors documented FUTURE WORK); non-PV
   and mixed-shape rejection pinned in `test_cl2p_freewidth.py`.

2. **MINOR** (run A) PROGRESS.md status board still reported pre-cap C 1s
   parity numbers (main Δ 4–12 meV, R 0.004–0.014, MG winners) while the
   detailed section documented the post-cap Scan_8 degradation.
   **Disposition — FIXED:** board row updated to the post-adjudication
   numbers with the pre-cap figures marked SUPERSEDED.

3. **MINOR** (both runs) Monday-handoff item 3 still instructed
   re-adjudication of the (now-ruled, now-implemented) discrepancy set.
   **Disposition — FIXED:** item rewritten to "review implemented outcomes
   only; do not re-adjudicate".

## Verified clean by both runs

- Cl 2p inequality enforcement + joint `_retag_slot` passthrough correct;
  real-anchor rejection documented consistently (cl2p.py / parity gate /
  PROGRESS); no residual claim the hypothesis was confirmed.
- C 1s split-cap removal structural; gate recalibration honest (measured
  values, causes documented).
- Lint flag-only; N 1s leave-it honored structurally (positional territory,
  no name special-case); labeled set: all 121 tabs classified into expected
  coarse regions, no fitted tab labeled `unknown`; findings exactly
  44 K 2p flags / 20 Zr 3d flags / 54 N 1s info notes (Codex probed the
  lint directly in-sandbox).

Both runs: pytest could not run in the read-only sandbox (no writable temp
directory); static review + direct Python probing used instead.

VERDICT: GO (both runs)
