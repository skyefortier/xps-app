"""
Multivariate MCR-ALS validation (decision-matrix entry 5).

Synthetic ground truth: mixtures of two known non-negative "pure" spectra
with known concentration profiles.  The method must recover the rank, the
pure spectra (up to scale/permutation — rotational ambiguity is inherent
and must be STATED), and concentration profiles correlated with truth.
"""

import numpy as np
import pytest

from autofit.methods import get_method
from autofit.methods.multivariate_mcr import build_matrix

X = np.arange(280.0, 294.0, 0.1)


def _pure():
    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((X - c) / w) ** 2)
    s1 = g(284.4, 1.0, 1.0) + g(291.0, 0.15, 2.0)      # graphite-like
    s2 = g(286.3, 1.0, 1.4) + g(288.8, 0.5, 1.3)       # oxidized-like
    return s1, s2


def _matrix(m=8, seed=2, noise=0.004):
    rng = np.random.default_rng(seed)
    s1, s2 = _pure()
    fracs = np.linspace(0.1, 0.9, m)
    D = np.vstack([f * 900 * s1 + (1 - f) * 700 * s2 for f in fracs])
    D = D + rng.normal(0, noise * D.max(), D.shape)
    return np.clip(D, 0.0, None), fracs


@pytest.fixture(scope="module")
def result():
    D, _ = _matrix()
    return get_method("multivariate_mcr").run(X, D)


def test_rank_recovered(result):
    assert result.success
    assert result.diagnostics["rank"] == 2
    assert result.diagnostics["explained_variance"] > 0.999


def test_pure_spectra_recovered_up_to_permutation(result):
    s1, s2 = _pure()
    est = [np.array(s) for s in result.analysis["pure_spectra"]]
    def corr(a, b):
        return float(np.corrcoef(a, b)[0, 1])
    pairs = [(corr(est[0], s1), corr(est[1], s2)),
             (corr(est[0], s2), corr(est[1], s1))]
    best = max(min(p) for p in pairs)
    assert best > 0.98, f"pure-spectra recovery too poor: {pairs}"


def test_concentration_profile_tracks_truth(result):
    D, fracs = _matrix()
    C = np.array(result.analysis["concentrations"])
    # one component's concentration must correlate strongly with the known
    # mixing fraction (sign/permutation free)
    cors = [abs(float(np.corrcoef(C[:, j], fracs)[0, 1])) for j in range(C.shape[1])]
    assert max(cors) > 0.99, cors


def test_rotational_ambiguity_stated_and_no_fake_peaks(result):
    assert "rotational_ambiguity" in result.analysis
    assert "not THE decomposition" in result.analysis["rotational_ambiguity"]
    assert result.peaks == []                 # states, not fitted peaks
    assert result.analysis["unverified_tunables"]


def test_deterministic(result):
    D, _ = _matrix()
    r2 = get_method("multivariate_mcr").run(X, D)
    assert r2.analysis["pure_spectra"] == result.analysis["pure_spectra"]
    assert r2.diagnostics == result.diagnostics


def test_input_validation():
    m = get_method("multivariate_mcr")
    D, _ = _matrix()
    with pytest.raises(ValueError, match="2-D data matrix"):
        m.run(X, D[0])
    with pytest.raises(ValueError, match="at least 2 spectra"):
        m.run(X, D[:1])
    with pytest.raises(ValueError, match="negative entries"):
        m.run(X, D - 1000.0)
    with pytest.raises(ValueError, match="unknown multivariate_mcr options"):
        m.run(X, D, options={"bogus": 1})


def test_rank_override():
    D, _ = _matrix()
    res = get_method("multivariate_mcr").run(X, D, options={"rank": 3})
    assert res.diagnostics["rank"] == 3
    assert res.analysis["rank_source"] == "user"


def test_build_matrix_interpolates_mixed_grids():
    s1, s2 = _pure()
    spectra = [
        (X, 900 * s1),
        (X[5:-3], 700 * s2[5:-3]),                       # narrower window
        (np.arange(281.0, 292.0, 0.07),                  # different step
         np.interp(np.arange(281.0, 292.0, 0.07), X, 800 * s1)),
    ]
    grid, D = build_matrix(spectra)
    assert D.shape[0] == 3 and D.shape[1] == len(grid)
    assert grid[0] >= 281.0 - 1e-9 and grid[-1] <= X[-4] + 1e-9
