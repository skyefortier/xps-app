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

from typing import Any, Callable, Optional

import numpy as np

from ..grammar import CandidateGrammar
from .base import MethodResult, PeakFitMethod

DEFAULTS = dict(
    variance_target=0.995,     # UNVERIFIED tunable (scree always reported)
    max_rank=6,                # UNVERIFIED guard
    max_als_iter=200,
    als_tol=1e-3,              # relative lack-of-fit change per iteration —
                               # the MCR-ALS GUI convergence default (0.1%,
                               # Jaumot 2005); UNVERIFIED as applied to XPS
    closure=False,             # data rows sum to a constant total? ONLY then
                               # does k = centered-PCs + 1 (Codex Stage-8
                               # blocker: unconditional +1 overcounts
                               # non-closed data)
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
        n_pts = int(np.floor((hi - lo) / step + 1e-9)) + 1
        grid = lo + step * np.arange(n_pts)       # strictly inside [lo, hi]
    else:
        grid = np.asarray(grid, dtype=float)
        if grid.min() < lo - 1e-9 or grid.max() > hi + 1e-9:
            raise ValueError(
                f"supplied grid [{grid.min():g}, {grid.max():g}] exceeds the "
                f"overlap range [{lo:g}, {hi:g}] — np.interp would silently "
                "edge-fill outside it")
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
        progress_cb: Optional[Callable[[dict], None]] = None,
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
        n_pcs = int(np.searchsorted(cum, cfg["variance_target"]) + 1)
        # +1 ONLY under closure (rows sum to a constant total): k centered
        # PCs then describe k+1 states.  Non-closed data with independently
        # varying amounts needs NO adjustment (Codex Stage-8 blocker).
        k_auto = n_pcs + (1 if cfg["closure"] else 0)
        k = int(rank_override) if rank_override is not None else k_auto
        k = max(1, min(k, cfg["max_rank"], m, n))

        # ── MCR-ALS from a deterministic NNDSVD-style init ──
        # orientation by POSITIVE-vs-NEGATIVE PART NORM (not element count:
        # a few large negative channels must flip the vector even against
        # many tiny positive ones — Codex Stage-8 finding)
        U2, s2, Vt2 = np.linalg.svd(D, full_matrices=False)
        S = []
        for j in range(min(k, Vt2.shape[0])):
            v = Vt2[j]
            if np.linalg.norm(np.clip(-v, 0, None)) > np.linalg.norm(np.clip(v, 0, None)):
                v = -v
            S.append(np.clip(v, 0.0, None))
        while len(S) < k:                      # rank > available PCs: flat seeds
            S.append(np.full(n, 1.0 / n))
        S = np.asarray(S).T                    # n × k
        S[:, 0] = np.maximum(S[:, 0], 1e-12)   # keep the dominant atom nonzero

        lof_prev = None
        history = []
        reseed_events = 0
        for it in range(cfg["max_als_iter"]):
            C = _nnls_rows(S, D)               # m × k
            # dead component (all-zero concentration): reseed its spectrum
            # from the POSITIVE RESIDUAL at finite scale — a tiny-uniform
            # reseed makes the next NNLS near-singular and can fabricate
            # arbitrary "states" (Codex Stage-8 finding); count + surface.
            dead = ~np.any(C > 0, axis=0)
            if np.any(dead):
                reseed_events += int(np.sum(dead))
                R = np.clip(D - C @ S.T, 0.0, None)
                seed = R.mean(axis=0)
                if seed.max() <= 0:
                    seed = np.full(n, float(D.mean()))
                for jd in np.where(dead)[0]:
                    S[:, jd] = seed / max(seed.max(), 1e-30)
                C = _nnls_rows(S, D)
            St = _nnls_rows(C, D.T)            # n × k
            dead = ~np.any(St > 0, axis=0)
            if np.any(dead):
                reseed_events += int(np.sum(dead))
                R = np.clip(D - C @ St.T, 0.0, None)
                seed = R.mean(axis=0)
                if seed.max() <= 0:
                    seed = np.full(n, float(D.mean()))
                for jd in np.where(dead)[0]:
                    St[:, jd] = seed / max(seed.max(), 1e-30)
            S = St
            R = D - C @ S.T
            lof = float(np.sqrt(np.sum(R ** 2) / np.sum(D ** 2)))
            history.append(lof)
            if lof_prev is not None and abs(lof_prev - lof) <= cfg["als_tol"] * max(lof_prev, 1e-30):
                break
            lof_prev = lof
        final_delta = (abs(history[-2] - history[-1]) / max(history[-2], 1e-30)
                       if len(history) > 1 else None)
        als_converged = (final_delta is not None
                         and final_delta <= cfg["als_tol"])

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
            "result_kind": "state_decomposition",   # consumer contract:
            #   peaks=[] is BY DESIGN — read n_states/pure_spectra, do not
            #   interpret the empty peak list as "no result"
            "n_states": int(k),
            "rank": int(k),
            "n_centered_pcs": int(n_pcs),
            "closure_assumed": bool(cfg["closure"]),
            "rank_source": "user" if rank_override is not None else (
                f"PCA cumulative variance ≥ {cfg['variance_target']}"
                + (" +1 (closure assumed)" if cfg["closure"] else
                   " (no closure adjustment — set closure=True only when "
                   "rows sum to a constant total)")),
            "pca_scree_explained_variance": [float(f) for f in frac[:min(10, len(frac))]],
            "als_iterations": len(history),
            "als_converged": bool(als_converged),
            "als_final_relative_delta": final_delta,
            "als_max_iter_hit": len(history) >= cfg["max_als_iter"],
            "dead_component_reseeds": int(reseed_events),
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
            diagnostics={"result_kind": "state_decomposition",
                         "rank": int(k), "n_states": int(k),
                         "lack_of_fit": history[-1],
                         "explained_variance": explained,
                         "als_iterations": len(history),
                         "als_converged": bool(als_converged),
                         "dead_component_reseeds": int(reseed_events)},
            message=f"decomposed {m} spectra into {k} non-negative states "
                    f"(LOF {history[-1]:.3%}; states, not peaks — see "
                    f"analysis.pure_spectra)",
        )
