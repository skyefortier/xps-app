# Codex adversarial review — negative backend areas fix (fix-negative-backend-areas, df972d6) — RUN A (2026-09-02, overnight session)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 166,098.
Prompt: docs/autofit/codex/area_sign_review_prompt.txt
Run B on the identical prompt/repo state also returned GO (4 MINOR findings each,
no MAJOR/BLOCKER) -> unit passes, stricter-verdict rule satisfied with GO x2.

**Findings**

1. MINOR - `abs()` is correct for normal UI/autofit fits, but `run_fit` is not airtight against negative components. The registered shape bases are non-negative under the normal parameter bounds, and free UI peaks send `amplitude_min: 0`; however raw API/spec callers can still provide `amplitude_min < 0`, and linked peaks use `master_amplitude * area_ratio` with no backend positivity check at [fitting.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-negative-backend-areas/fitting.py:862). In those invalid cases, `abs(area)` would mask a negative modeled peak. The old sign was grid-direction-dependent, so it was not a reliable diagnostic, but backend validation for `amplitude_min >= 0` and `area_ratio > 0` would be cleaner.

2. MINOR - stale saved `_backendParams.area.value` can still be reserialized until refit. I found no field-level frontend reader: results, Quantify, CSV/XLSX, and spec `peakCurves[].area` compute area from frontend curves using positive step widths. But save paths spread peak objects verbatim, e.g. [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-negative-backend-areas/templates/index.html:8639), [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-negative-backend-areas/templates/index.html:8711), and [templates/index.html](/Users/skyefortier/xps-app/.claude/worktrees/fix-negative-backend-areas/templates/index.html:8820), so an old loaded-not-refit `.fit/.spec/.proj` can preserve negative `_backendParams.area.value` in the JSON metadata. That is not visible in Quantify/table exports, but it is present in user-facing saved artifacts.

3. MINOR - the new tests pin the actual regression path, but not the invalid-negative-component edge. `tests/conftest.py` inserts this worktree root before `from fitting import run_fit`, so the import is correct. The Gaussian ascending/descending tests are adequate for the changed common integration line at [fitting.py](/Users/skyefortier/xps-app/.claude/worktrees/fix-negative-backend-areas/fitting.py:1206); they do not prove every shape remains non-negative or catch negative `area_ratio`/`amplitude_min`.

4. MINOR - the in-place fixture flip is equivalent to regeneration for this change. `refit_record()` runs the solver, then copies `center`, `fwhm`, `amplitude`, and `area`; chi-square/r-factor come from `res["statistics"]` and do not depend on area sign. The reduced diff shows only `"area"` lines changed, so this avoids lmfit numeric wobble without changing fitted params.

VERDICT: GO
