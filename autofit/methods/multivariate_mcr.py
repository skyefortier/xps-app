"""
Method 5 — Multivariate decomposition: PCA rank estimate + MCR-ALS
(decision-matrix entry 5).

Literature basis (decision matrix, verified DOIs):
- Mc Evoy et al., Anal. Chem. 80 (2008) 7226, DOI 10.1021/ac8005878 (PCA
  on XPS series);
- Artyushkova & Fulghum, JESRP 121 (2001) 33,
  DOI 10.1016/S0368-2048(01)00325-5;
- Jaumot et al., Chemom. Intell. Lab. Syst. 76 (2005) 101 (MCR-ALS);
- Avval et al., JVST A 40 (2022) 063206, DOI 10.1116/6.0002082
  (chemometrics practice guide for XPS).

THIS METHOD'S JOB IS DIFFERENT from the single-spectrum fitters: given a
MATRIX of related spectra (depth profile, repeat scans, line scan) on one
BE grid, it estimates the number of independent chemical states, their
pure spectra, and per-spectrum concentrations:

    D (m spectra × n channels)  ≈  C (m×k, ≥0)  ·  Sᵀ (k×n, ≥0)

by alternating non-negative least squares from an SVD-based init
(deterministic; no RNG).  It does NOT emit fitted peaks — `peaks` is empty
by design; the decomposition lives in the analysis payload.  ROTATIONAL
AMBIGUITY is inherent to MCR (any invertible T with C T ≥ 0, T⁻¹Sᵀ ≥ 0
fits equally well) and is stated in the payload, never hidden.

Input convention: ``y`` is the 2-D data matrix (m × n), ``x`` the shared
BE grid.  Spectra on differing grids must be interpolated first (helper
``build_matrix``).  A grammar is NOT required (requires_grammar=False) —
this method is assumption-light by design; if one is passed its provenance
is echoed into the payload.

Rank selection: smallest k whose PCA cumulative explained variance ≥
``variance_target`` (0.995 — UNVERIFIED tunable), capped by ``max_rank``;
the full scree is always reported so the user can override with ``rank``.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from ..grammar import CandidateGrammar
from .base import MethodResult, PeakFitMethod

DEFAULTS = dict(
    variance_target=0.995,     # UNVERIFIED tunable (scree always reported)
    max_rank=6,                # UNVERIFIED guard
    max_als_iter=200,
    als_tol=1e-9,              # relative lack-of-fit change
)
_ALLOWED_OPTIONS = set(DEFAULTS) | {"rank"}


def build_matrix(spectra: list[tuple[np.ndarray, np.ndarray]],
                 grid: Optional[np.ndarray] = None):
    """Interpolate (x_i, y_i) spectra onto a common grid (the overlap of all
    ranges; densest input step).  Returns (x_grid, D)."""
    los = [min(float(x[0]), float(x[-1])) for x, _ in spectra]
    his = [max(float(x[0]), float(x[-1])) for x, _ in spectra]
    lo, hi = max(los), min(his)
    if hi <= lo:
        raise ValueError("spectra have no overlapping BE range")
    if grid is None:
        step = min(float(np.min(np.abs(np.diff(x)))) for x, _ in spectra)
        grid = np.arange(lo, hi + 0.5 * step, step)
    rows = []
    for x, y in spectra:
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        order = np.argsort(x)
        rows.append(np.interp(grid, x[order], y[order]))
    return grid, np.vstack(rows)


def _nnls_rows(B: np.ndarray, M: np.ndarray) -> np.ndarray:
    """Solve min ||M − X·Bᵀ|| row-wise with X ≥ 0 (scipy nnls per row)."""
    from scipy.optimize import nnls
    X = np.zeros((M.shape[0], B.shape[1]))
    for i in range(M.shape[0]):
        X[i], _ = nnls(B, M[i])
    return X


class MultivariateMCRMethod(PeakFitMethod):
    id = "multivariate_mcr"
    label = "Multivariate (PCA / MCR-ALS)"
    requires_grammar = False

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> MethodResult:
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown multivariate_mcr options: {sorted(unknown)}")
        cfg = {k: type(DEFAULTS[k])(opts.pop(k, DEFAULTS[k])) for k in DEFAULTS}
        rank_override = opts.pop("rank", None)

        x = np.asarray(x, dtype=float)
        D = np.asarray(y, dtype=float)
        if D.ndim != 2:
            raise ValueError(
                "multivariate_mcr needs a 2-D data matrix (m spectra × n "
                "channels) as y — one spectrum per row on the shared x grid "
                "(see build_matrix); single spectra belong to the other methods")
        m, n = D.shape
        if m < 2:
            raise ValueError("need at least 2 spectra for multivariate decomposition")
        if n != len(x):
            raise ValueError(f"x has {len(x)} channels but the matrix has {n}")
        if np.any(D < 0):
            # non-negativity is the load-bearing MCR constraint; negative
            # intensities (over-subtracted background) violate it
            raise ValueError("data matrix has negative entries — remove "
                             "background over-subtraction before MCR")

        # ── PCA rank estimate (scree always reported) ──
        mean = D.mean(axis=0)
        U, s, Vt = np.linalg.svd(D - mean, full_matrices=False)
        var = s ** 2
        frac = var / var.sum() if var.sum() > 0 else var
        cum = np.cumsum(frac)
        # +1: k mean-centered PCs describe k+1 chemical states (closure)
        k_auto = int(np.searchsorted(cum, cfg["variance_target"]) + 1) + 1
        k = int(rank_override) if rank_override is not None else k_auto
        k = max(1, min(k, cfg["max_rank"], m, n))

        # ── MCR-ALS from a deterministic SVD init ──
        # init S from the top-k right singular vectors of the RAW matrix,
        # clipped to ≥0 (sign chosen so each vector is mostly positive)
        U2, s2, Vt2 = np.linalg.svd(D, full_matrices=False)
        S = []
        for j in range(k):
            v = Vt2[j]
            if np.sum(v < 0) > np.sum(v > 0):
                v = -v
            S.append(np.clip(v, 0.0, None))
        S = np.asarray(S).T                    # n × k
        S[:, 0] = np.maximum(S[:, 0], 1e-12)   # keep the dominant atom nonzero

        lof_prev = None
        history = []
        for it in range(cfg["max_als_iter"]):
            C = _nnls_rows(S, D)               # m × k
            # guard: a component with all-zero concentration would make the
            # next NNLS singular — reseed it to tiny uniform
            dead = ~np.any(C > 0, axis=0)
            C[:, dead] = 1e-12
            St = _nnls_rows(C, D.T)            # n × k
            dead = ~np.any(St > 0, axis=0)
            St[:, dead] = 1e-12
            S = St
            R = D - C @ S.T
            lof = float(np.sqrt(np.sum(R ** 2) / np.sum(D ** 2)))
            history.append(lof)
            if lof_prev is not None and abs(lof_prev - lof) <= cfg["als_tol"] * max(lof_prev, 1e-30):
                break
            lof_prev = lof

        # normalize: unit-max pure spectra; scale into concentrations
        scale = S.max(axis=0)
        scale[scale <= 0] = 1.0
        S_n = S / scale
        C_n = C * scale

        explained = 1.0 - history[-1] ** 2

        analysis = {
            "method": self.id,
            "basis": "PCA rank estimate + MCR-ALS (NNLS alternation, SVD "
                     "init, non-negativity on C and S); Mc Evoy 2008 "
                     "DOI 10.1021/ac8005878; Artyushkova & Fulghum 2001 "
                     "DOI 10.1016/S0368-2048(01)00325-5; Jaumot 2005; "
                     "Avval 2022 DOI 10.1116/6.0002082",
            "n_spectra": int(m),
            "n_channels": int(n),
            "rank": int(k),
            "rank_source": "user" if rank_override is not None else
                           f"PCA cumulative variance ≥ {cfg['variance_target']} (+1 for closure)",
            "pca_scree_explained_variance": [float(f) for f in frac[:min(10, len(frac))]],
            "als_iterations": len(history),
            "lack_of_fit": history[-1],
            "explained_variance": explained,
            "pure_spectra": [[float(v) for v in S_n[:, j]] for j in range(k)],
            "concentrations": [[float(v) for v in C_n[i]] for i in range(m)],
            "be_grid": [float(v) for v in x],
            "rotational_ambiguity": (
                "MCR solutions are unique only up to rotation (any invertible "
                "T with CT ≥ 0, T⁻¹Sᵀ ≥ 0 fits equally); treat pure spectra "
                "as A feasible decomposition, not THE decomposition — "
                "constrain with known references before chemical claims"),
            "unverified_tunables": {k_: cfg[k_] for k_ in DEFAULTS},
        }
        if grammar is not None:
            import copy
            analysis["constants_provenance"] = copy.deepcopy(grammar.provenance)
            analysis["constants_provenance_scope"] = "region-wide"
        return MethodResult(
            method_id=self.id, success=True,
            peaks=[],                # by design: states, not fitted peaks
            analysis=analysis,
            confidence={},
            diagnostics={"rank": int(k), "lack_of_fit": history[-1],
                         "explained_variance": explained,
                         "als_iterations": len(history)},
            message=f"decomposed {m} spectra into {k} non-negative states "
                    f"(LOF {history[-1]:.3%})",
        )
