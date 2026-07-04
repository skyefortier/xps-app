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
    """NON-closed design: the two amounts vary independently (no constant
    total), so mean-centered PCA legitimately needs 2 PCs and the default
    closure=False rank must be 2 (Codex Stage-8 blocker regression case).
    Two near-pure end-member rows (as real depth profiles have) keep the
    rotational ambiguity small enough for tight recovery assertions."""
    rng = np.random.default_rng(seed)
    s1, s2 = _pure()
    a1 = np.concatenate([[950.0, 40.0], rng.uniform(200.0, 1000.0, m - 2)])
    a2 = np.concatenate([[40.0, 950.0], rng.uniform(200.0, 1000.0, m - 2)])
    D = np.outer(a1, s1) + np.outer(a2, s2)
    D = D + rng.normal(0, noise * D.max(), D.shape)
    return np.clip(D, 0.0, None), a1


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
    D, a1 = _matrix()
    C = np.array(result.analysis["concentrations"])
    # one component's concentration must correlate strongly with the known
    # component-1 amount (sign/permutation free)
    cors = [abs(float(np.corrcoef(C[:, j], a1)[0, 1])) for j in range(C.shape[1])]
    assert max(cors) > 0.99, cors


def test_payload_reconstructs_data_at_reported_lof(result):
    """Codex Stage-8 test gap: the PAYLOAD matrices must reconstruct D at
    the reported lack-of-fit (catches any normalization/scaling bug)."""
    D, _ = _matrix()
    C = np.array(result.analysis["concentrations"])
    S = np.array(result.analysis["pure_spectra"]).T
    lof = float(np.sqrt(np.sum((D - C @ S.T) ** 2) / np.sum(D ** 2)))
    assert lof == pytest.approx(result.analysis["lack_of_fit"], rel=1e-6)


def test_rank_estimator_discriminates():
    """Codex Stage-8 test gap: the estimator must not be 'always 2'.
    1-state (scaled copies) → 1; closed 2-state with closure=True → 2
    (1 centered PC + closure); the non-closed default case is the fixture."""
    rng = np.random.default_rng(7)
    s1, s2 = _pure()
    one = np.outer(rng.uniform(300, 900, 6), s1)
    one += rng.normal(0, 0.003 * one.max(), one.shape)
    r1 = get_method("multivariate_mcr").run(X, np.clip(one, 0, None))
    assert r1.diagnostics["rank"] == 1

    f = np.linspace(0.15, 0.85, 7)
    closed = np.outer(f, 800 * s1) + np.outer(1 - f, 800 * s2)
    closed += rng.normal(0, 0.003 * closed.max(), closed.shape)
    r2 = get_method("multivariate_mcr").run(X, np.clip(closed, 0, None),
                                            options={"closure": True})
    assert r2.diagnostics["rank"] == 2
    assert r2.analysis["closure_assumed"] is True
    # same closed data WITHOUT the closure claim: 1 centered PC → rank 1
    # (under-count is the honest default when closure is not asserted)
    r3 = get_method("multivariate_mcr").run(X, np.clip(closed, 0, None))
    assert r3.diagnostics["rank"] == 1


def test_nnls_rows_orientation():
    """Direct pin of the ALS building block on a known D = C·Sᵀ."""
    from autofit.methods.multivariate_mcr import _nnls_rows
    rng = np.random.default_rng(1)
    C = rng.uniform(0.5, 2.0, (5, 2))
    S = np.abs(rng.normal(size=(30, 2))) + 0.1
    D = C @ S.T
    C_hat = _nnls_rows(S, D)
    assert np.allclose(C_hat, C, atol=1e-8)
    S_hat = _nnls_rows(C, D.T)
    assert np.allclose(S_hat, S, atol=1e-8)


def test_result_kind_contract(result):
    assert result.analysis["result_kind"] == "state_decomposition"
    assert result.diagnostics["result_kind"] == "state_decomposition"
    assert result.analysis["n_states"] == result.diagnostics["rank"]
    assert result.analysis["als_converged"] is True
    assert result.analysis["dead_component_reseeds"] == 0


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
    # every grid point strictly inside the overlap — no silent edge-fill
    lo = 281.0
    hi = float(X[-4])
    assert grid[0] >= lo - 1e-9 and grid[-1] <= hi + 1e-9


def test_build_matrix_descending_grid_and_endpoint():
    """Codex Stage-8 pins: descending BE grids interpolate correctly, and a
    non-commensurate overlap span never yields grid points past the overlap
    (np.interp would silently edge-fill there)."""
    s1, _ = _pure()
    desc = X[::-1]
    grid, D = build_matrix([(X, 900 * s1), (desc, 900 * s1[::-1])])
    assert np.allclose(D[0], D[1], atol=1e-9)     # same spectrum both ways
    # non-commensurate span: overlap [0, 0.95] with step 0.2
    a = (np.arange(0.0, 1.01, 0.2), np.ones(6))
    b = (np.arange(-0.5, 0.951, 0.05), np.ones(30))
    grid2, _ = build_matrix([a, b])
    assert grid2.max() <= 0.95 + 1e-9
    with pytest.raises(ValueError, match="exceeds the overlap"):
        build_matrix([a, b], grid=np.array([0.0, 1.5]))
