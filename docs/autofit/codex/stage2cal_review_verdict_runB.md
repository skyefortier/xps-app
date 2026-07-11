# Codex review — Stage-2 Find-Peaks calibration
*Run B, 2026-07-10, codex exec read-only, effort=high, gtimeout 600.
Prompt: stage2_calibration_review_prompt.txt (range 8484679..0713c05;
HEAD at review time a6c9734).*

**Findings**

1. **BLOCKER** `autofit/engine.py:1543`: `rank_and_filter` enables `unstable_last_resort` for any nonempty report set when clean and conditional survivors are empty. `compare_models` calls it unconditionally at `autofit/engine.py:2695`, without passing any “detection found real structure” evidence. That means a grammar-covered or weak/noisy region can emit a best converged but unstable model as `success=True` even when the detection layer found nothing. The unit pin actually reinforces the hole by constructing the last-resort case with `enable_preseed=False` at `tests/autofit/test_stage2_completeness.py:242`. Current HEAD’s extra commit `a6c9734` appears to add the missing gate, but it is outside the requested `0713c05` snapshot.

2. **MAJOR** `autofit/candidates.py:424`: D0 silently truncates detection-family slots to `DETECTION_MODEL_MAX_SLOTS = 8` by amplitude at `autofit/candidates.py:388` and `autofit/candidates.py:427`, then returns the model without an overflow/truncation flag at `autofit/candidates.py:459`. The full pool payload still contains all detections, but the candidate actually fit has dropped lower-amplitude features before selection can prune. For the stated goal, a ninth resolvable shoulder can disappear without a loud candidate-level reason.

3. **MINOR** `tests/autofit/test_stage2_completeness.py:269`: “last resort never preferred over survivors” is pinned only against a clean survivor. The code ordering also protects conditional survivors (`autofit/engine.py:1539` before `autofit/engine.py:1543`), so this is not a behavior bug, but the pin does not directly discriminate the conditional-survivor interaction named in the review target.

**Other Checks**

Warm restart is bounded and honest enough: it only fires after failed-but-finite fits (`autofit/engine.py:783`), adds one 2000-nfev retry (`autofit/engine.py:796`), and downstream stability, chi-square, boundary, and width flags still judge the accepted model. Budget prose should be read as 18k + possible 2k worst case per fit.

Proposal eligibility is correctly fitted-model based: populated roles come from fitted components (`autofit/engine.py:1825`), proximity is in 0.5x fitted width units (`autofit/engine.py:1826`), and populated linked windows use `_effective_be_window` (`autofit/engine.py:1833`). An absent/unpopulated slot being proposal-eligible is intentional; selection must arbitrate duplication.

Spike guard is detection-signal only, with raw-count variance retained (`autofit/candidates.py:168`, `autofit/candidates.py:184`). The committed tests cover single-point spikes and shoulder preservation (`tests/autofit/test_cwt_detector.py:220`, `tests/autofit/test_cwt_detector.py:247`).

DS+G effective width is using the right convention: `fitting.py:154` defines `beta` as Lorentzian half-width and `fitting.py:155` defines `m_gauss` as Gaussian FWHM, so `f_L = 2 * beta` in `autofit/engine.py:711` is correct. Asym-GL remains handled through its effective side width parameter rather than the DS+G Voigt approximation; acceptable gap, not a blocker.

Read-only verification only: I did not run pytest. The committed calibration artifact supports H0 q95 ≈ 6.93, FP@7 = 29/600 = 4.83%, and broad off-center = 1/20. `/api/fit` and manual Run Fit files were not touched; `app.py` changes are confined to `/api/analyze`. New held-out ds7/ds8/Fe files are untracked, while tests only commit numeric gates.

VERDICT: NO-GO
