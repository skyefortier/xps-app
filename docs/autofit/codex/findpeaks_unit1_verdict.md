# Find Peaks UI unit 1 (commit 7827cda) — Codex review verdicts

## Run A
```
from ..confidence import build_confidence_vector
from ..criteria import build_criteria_panel
from ..engine import ComparisonResult, ModelReport, compare_models, _slot_prefix
from ..grammar import BACKEND_SHAPE, CandidateGrammar
from .base import MethodResult, PeakFitMethod, poisson_like_weights

_ALLOWED_OPTIONS = {
    "noise_floor", "n_refits", "rng_seed", "candidate_filter",
    "enable_proposal_pass", "persistence_threshold", "bic_ambiguity_threshold",
    "absent_slot_area_fraction", "absent_slot_persistence_threshold",
    "enable_preseed",
}

ENGINE_VERSION = "autofit-stage2"



exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"import autofit.methods; print('ok')\"" in /Users/skyefortier/xps-verify
 exited 1 in 429ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/autofit/methods/__init__.py", line 21, in <module>
    from .bayesian_exchange_mc import BayesianExchangeMCMethod
  File "/Users/skyefortier/xps-verify/autofit/methods/bayesian_exchange_mc.py", line 56, in <module>
    from ..engine import (
  File "/Users/skyefortier/xps-verify/autofit/engine.py", line 38, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

codex
No BLOCKER/MAJOR findings.

1. MINOR: [tests/test_browser_find_peaks_progress.py](/Users/skyefortier/xps-verify/tests/test_browser_find_peaks_progress.py:140) overclaims that it forces the two-phase screen-to-stabilize path. It only sets `n_refits`/`enable_proposal_pass`; the gunicorn worker still uses `SCREEN_TOP_K = 6`, and Cl 2p resolves to 4 candidates, so this is single-phase stabilizing progress. Failure scenario: screening-phase progress regresses in the real browser path, but this test still passes because it never enters screening. It also makes the elapsed-tick assertion somewhat timing-sensitive if the 4-candidate fit finishes quickly.

Other checks: the forbidden Unit 2/3 identifiers are absent from the `7827cda^..7827cda` diff; `/api/analyze` refactor preserved validation order and payload shape; callback default/raising behavior is contained; async start uses a daemon thread and atomic progress-file replacement; cleanup is TTL-bound and reachable; UI spinner cleanup goes through the same `finally` on success, start errors, poll errors, watchdog, and the empty manual-refit return.

I did not run pytest; this sandbox is read-only and this environment also lacks `lmfit`, so importing `autofit.engine` fails here.

VERDICT: GO
```

## Run B
```
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YGq5KZON' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-LkpEzsPZ' (errno=Operation not permitted)

exec
/bin/zsh -lc 'git show --name-only --format= 7827cda | sort' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vqHeltkU' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-pbXVKfnL' (errno=Operation not permitted)
app.py
autofit/engine.py
autofit/methods/base.py
autofit/methods/bayesian_exchange_mc.py
autofit/methods/ic_model_comparison.py
autofit/methods/least_squares.py
autofit/methods/max_entropy.py
autofit/methods/multivariate_mcr.py
autofit/methods/sparse_map.py
docs/autofit/PROGRESS.md
templates/index.html
tests/autofit/test_progress_callback.py
tests/js/find_peaks_progress.test.js
tests/test_api_analyze_progress.py
tests/test_browser_find_peaks_progress.py

exec
/bin/zsh -lc 'git show --no-renames --format= 7827cda -- app.py autofit/engine.py autofit/methods/base.py autofit/methods/bayesian_exchange_mc.py autofit/methods/ic_model_comparison.py autofit/methods/least_squares.py autofit/methods/max_entropy.py autofit/methods/multivariate_mcr.py autofit/methods/sparse_map.py templates/index.html docs/autofit/PROGRESS.md tests/autofit/test_progress_callback.py tests/test_api_analyze_progress.py tests/js/find_peaks_progress.test.js tests/test_browser_find_peaks_progress.py | rg "find-peaks-modal-box|fp-drag-handle|FP_TIER_META|fp-regions-filter|coverage_index" -n || true' in /Users/skyefortier/xps-verify
 succeeded in 121ms:
codex
1. MINOR `tests/test_browser_find_peaks_progress.py:140`: the browser test claims it forces the two-phase `screen -> stabilize` sweep, but it only sets UI options (`n_refits`, `enable_proposal_pass`). It does not force `SCREEN_TOP_K`, so it can pass on a stabilizing-only run and does not prove the browser sees both phases. The Flask test does cover forced two-phase via monkeypatch, but the Playwright claim is overstated.

2. MINOR `docs/autofit/PROGRESS.md:2543`: docs say `progress_cb` was added to “all 5 concrete methods,” but this commit updates six concrete method classes: least-squares, IC, Bayesian, sparse MAP, max entropy, and multivariate MCR. Low-risk doc inventory error.

No BLOCKER/MAJOR findings. `/api/analyze` refactor appears behavior-preserving; `progress_cb=None` is a true no-op for existing non-test callers; the async route returns after spawning a daemon thread; progress-file writes use per-job temp paths plus `os.replace`; the client spinner clears through the shared `finally` path, including the empty manual-refit early return. I did not run pytest in the read-only sandbox.

VERDICT: GO
```
