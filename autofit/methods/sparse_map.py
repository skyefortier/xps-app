"""
Method 4 — Sparse / MAP decomposition (decision-matrix entry 4).

Literature basis:
- MAP/sparse high-throughput XPS: STAM: Methods (2024),
  DOI 10.1080/27660400.2024.2373046 — dictionary of lineshape atoms +
  sparsity prior selects the number of components.
- Tibshirani, J. R. Stat. Soc. B 58 (1996) 267 — the LASSO (L1) estimator.

Character (per the decision matrix): FAST and auto-pruning, best for few
separated peaks; known weaknesses — grid mismatch can split peaks,
L1 shrinkage biases amplitudes (mitigated here by a debiased NNLS refit on
the selected support), and heavy overlap/asymmetric shapes are NOT its
regime (use IC/Bayesian there).

Implementation:
- Dictionary: Gaussian atoms on the DATA GRID restricted to the union of
  the grammar's slot BE windows, with a small log-spaced FWHM ladder inside
  each slot's fwhm_range.  Gaussian atoms are a documented simplification —
  asymmetric slot shapes (DS/LACX) are not dictionary-expressible here; the
  analysis payload flags any such slot.
- Solver: non-negative LASSO by cyclic coordinate descent on column-
  normalized atoms (deterministic; no RNG anywhere in this method).
- Model size: a geometric λ path from λ_max (= max correlation) downward;
  for each λ the surviving atoms are clustered (merge distance = a fraction
  of the local FWHM), the support is DEBIASED by non-negative least squares,
  and BIC = n·ln(RSS/n) + k·ln(n) (k = selected-atom count, the actual
  amplitude dofs; engine convention) picks the reported λ.
- Uncertainty: NONE is calibrated for post-selection sparse estimates —
  the confidence payload says so explicitly (typed kind
  'unavailable_post_selection'); it never fabricates a σ.

UNVERIFIED tunables (spec §9 discipline; all overridable via options and
flagged in the analysis payload): n_widths=4, n_lambdas=25,
lambda_min_ratio=1e-3, merge_fraction=0.6, cd_tol=1e-8, cd_max_iter=400.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np

from ..engine import _compute_background
from ..grammar import CandidateGrammar, LineShape
from .base import MethodResult, PeakFitMethod

_GAUSS_C = 4.0 * np.log(2.0)

DEFAULTS = dict(
    n_widths=4,
    n_lambdas=25,
    lambda_min_ratio=1e-3,
    merge_fraction=0.6,
    cd_tol=1e-8,
    cd_max_iter=400,
    # convergence = exit KKT violation ≤ kkt_rtol × λ (the stationarity
    # condition's own scale); the raw violation is always surfaced
    kkt_rtol=1e-2,
)
_ALLOWED_OPTIONS = set(DEFAULTS) | {"lambda_fixed"}

# dictionary atoms are symmetric Gaussians; these slot shapes are not
# expressible and get flagged in the payload
_ASYMMETRIC_SHAPES = {LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G,
                      LineShape.LACX}


def _gauss(x: np.ndarray, c: float, w: float) -> np.ndarray:
    return np.exp(-_GAUSS_C * ((x - c) / w) ** 2)


def _build_dictionary(x: np.ndarray, grammar: CandidateGrammar, n_widths: int):
    """Atoms (unit-height Gaussians) on the data grid within slot windows.

    Slot variants are UNIONED per role across all candidates (Codex Stage-7
    blocker #1: role-level setdefault dropped variants — a role that is
    ASYM_GL in one candidate and PV in another must still be flagged
    asymmetric, and the widest window / FWHM range must win)."""
    windows: dict[str, list[float]] = {}     # role -> [lo, hi, wlo, whi]
    asym: dict[str, bool] = {}
    for cand in grammar.candidates:
        for s in cand.slots:
            lo, hi = s.be_window
            wlo, whi = s.fwhm_range
            b = windows.get(s.role)
            if b is None:
                windows[s.role] = [lo, hi, wlo, whi]
            else:
                b[0] = min(b[0], lo)
                b[1] = max(b[1], hi)
                b[2] = min(b[2], wlo)
                b[3] = max(b[3], whi)
            asym[s.role] = asym.get(s.role, False) or (
                getattr(s, "line_shape", None) in _ASYMMETRIC_SHAPES)
    unexpressible = sorted(r for r, a in asym.items() if a)
    atoms = []          # (center, width, role)
    for role in sorted(windows):
        lo, hi, wlo, whi = windows[role]
        widths = np.geomspace(max(wlo, 1e-3), max(whi, wlo + 1e-3),
                              max(2, n_widths))
        centers = x[(x >= lo) & (x <= hi)]
        for c in centers:
            for w in widths:
                atoms.append((float(c), float(w), role))
    if not atoms:
        raise ValueError("empty dictionary: no data points inside any slot window")
    A = np.column_stack([_gauss(x, c, w) for c, w, _ in atoms])
    norms = np.linalg.norm(A, axis=0)
    keep = norms > 1e-12
    return A[:, keep], [a for a, k in zip(atoms, keep) if k], norms[keep], unexpressible


def _nn_lasso_cd(A: np.ndarray, y: np.ndarray, lam: float,
                 a0: np.ndarray, tol: float, max_iter: int):
    """Cyclic coordinate descent for min ½||y−Aa||² + λ·Σa, a ≥ 0.
    Columns of A must be unit-norm (then ||A_j||² = 1).

    Returns (a, kkt_violation): the exit-time KKT stationarity residual —
    max over j of (A_j·r − λ) for a_j = 0 and |A_j·r − λ| for a_j > 0 —
    computed on a FRESHLY recomputed residual so incremental-update drift
    cannot hide non-convergence (Codex Stage-7 finding #3)."""
    a = a0.copy()
    r = y - A @ a
    for _ in range(max_iter):
        delta = 0.0
        for j in range(A.shape[1]):
            aj = a[j]
            cj = A[:, j] @ r + aj          # since ||A_j||² == 1
            new = max(0.0, cj - lam)
            if new != aj:
                r -= A[:, j] * (new - aj)
                delta = max(delta, abs(new - aj))
                a[j] = new
        if delta < tol:
            break
    r = y - A @ a                          # exact residual at exit
    grad = A.T @ r
    active = a > 0
    kkt = 0.0
    if np.any(~active):
        kkt = max(kkt, float(np.max(grad[~active] - lam)))
    if np.any(active):
        kkt = max(kkt, float(np.max(np.abs(grad[active] - lam))))
    return a, max(kkt, 0.0)


def _cluster_support(idx: list[int], atoms, amps: np.ndarray, merge_fraction: float):
    """Merge selected atoms into peaks: greedy by center order, joining an
    atom when its gap to the LAST cluster atom is within merge_fraction ×
    the cluster's amplitude-weighted mean FWHM.  Scaling by the resolved
    feature's width (not the narrowest atom's) keeps small width-ladder
    flank atoms — the documented off-ladder-width compensation mechanism —
    inside their parent peak instead of fragmenting it."""
    sel = sorted(((atoms[j][0], atoms[j][1], atoms[j][2], amps[k], j)
                  for k, j in enumerate(idx)), key=lambda t: t[0])
    clusters: list[list[tuple]] = []
    for entry in sel:
        if clusters:
            cl = clusters[-1]
            wts = np.array([e[3] for e in cl])
            cl_w = (float(np.average([e[1] for e in cl], weights=wts))
                    if wts.sum() > 0 else cl[-1][1])
            if entry[0] - cl[-1][0] <= merge_fraction * max(cl_w, entry[1]):
                cl.append(entry)
                continue
        clusters.append([entry])
    return clusters


class SparseMAPMethod(PeakFitMethod):
    id = "sparse_map"
    label = "Sparse / MAP (fast auto)"
    requires_grammar = True

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> MethodResult:
        if grammar is None:
            raise ValueError("sparse_map requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown sparse_map options: {sorted(unknown)}")
        cfg = {k: type(DEFAULTS[k])(opts.pop(k, DEFAULTS[k])) for k in DEFAULTS}
        lambda_fixed = opts.pop("lambda_fixed", None)

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)

        bg = _compute_background(x, y, grammar.candidates[0].background)
        y_net = y - bg
        n = len(y_net)

        A, atoms, norms, unexpressible = _build_dictionary(
            x, grammar, cfg["n_widths"])
        An = A / np.linalg.norm(A, axis=0)

        lam_max = float(np.max(An.T @ y_net))
        if lam_max <= 0:
            return MethodResult(method_id=self.id, success=False,
                                message="no positive correlation with any atom")
        if lambda_fixed is not None:
            lam_path = [float(lambda_fixed)]
        else:
            lam_path = list(np.geomspace(
                lam_max * 0.999, lam_max * cfg["lambda_min_ratio"],
                cfg["n_lambdas"]))

        from scipy.optimize import nnls

        a = np.zeros(An.shape[1])
        path_records = []
        best = None
        # warm-started λ path, SPARSE→DENSE order (λ_max down; each solve
        # warm-starts from the previous, sparser, solution)
        for lam in lam_path:
            a, kkt = _nn_lasso_cd(An, y_net, lam, a,
                                  cfg["cd_tol"], cfg["cd_max_iter"])
            converged = kkt <= cfg["kkt_rtol"] * lam
            idx = [j for j in range(len(a)) if a[j] > 1e-10]
            if not idx:
                path_records.append({"lambda": lam, "n_atoms_active": 0,
                                     "bic": None, "n_peaks": 0,
                                     "kkt_violation": float(kkt),
                                     "converged": bool(converged)})
                continue
            # debiased amplitudes: NNLS on the raw (un-normalized) support;
            # the ACTIVE support is what NNLS keeps nonzero — zero-amplitude
            # atoms must not count as dof or join clusters (Codex Stage-7
            # blocker #2)
            amps_all, _ = nnls(A[:, idx], y_net)
            active = amps_all > 1e-10
            act_idx = [j for j, keep in zip(idx, active) if keep]
            amps = amps_all[active]
            if not act_idx:
                path_records.append({"lambda": lam, "n_atoms_active": 0,
                                     "bic": None, "n_peaks": 0,
                                     "kkt_violation": float(kkt),
                                     "converged": bool(converged)})
                continue
            rss = float(np.sum((y_net - A[:, act_idx] @ amps) ** 2))
            k = len(act_idx)
            bic = n * np.log(max(rss, 1e-300) / n) + k * np.log(n)
            clusters = _cluster_support(act_idx, atoms, amps, cfg["merge_fraction"])
            rec = {"lambda": float(lam), "n_atoms_active": k,
                   "n_peaks": len(clusters), "bic": float(bic),
                   "kkt_violation": float(kkt), "converged": bool(converged)}
            path_records.append(rec)
            if best is None or bic < best["bic"]:
                best = {**rec, "idx": act_idx, "amps": amps,
                        "clusters": clusters, "rss": rss}

        if best is None:
            return MethodResult(
                method_id=self.id, success=False,
                analysis={"method": self.id, "lambda_path": path_records},
                message="no λ on the path produced a non-empty support")

        # peaks from clusters (amplitude-weighted atom parameters)
        peaks, confidence = [], {}
        role_counts: dict[str, int] = {}
        for cl in best["clusters"]:
            wts = np.array([e[3] for e in cl])
            if wts.sum() <= 0:
                continue
            center = float(np.average([e[0] for e in cl], weights=wts))
            fwhm = float(np.average([e[1] for e in cl], weights=wts))
            role = cl[int(np.argmax(wts))][2]
            role_counts[role] = role_counts.get(role, 0) + 1
            role_tag = role if role_counts[role] == 1 else f"{role}#{role_counts[role]}"
            profile = np.zeros_like(x)
            for c, w, _r, amp, _j in cl:
                profile += amp * _gauss(x, c, w)
            peaks.append({
                "role": role_tag, "region": grammar.regions[0],
                "phase_id": grammar.phase_ids[0],
                "shape": "gaussian",
                "center": center, "fwhm": fwhm,
                "amplitude": float(profile.max()),
                "n_atoms": len(cl),
            })
            confidence[role_tag] = {
                "sigma_stat": {
                    # post-selection sparse estimates carry NO calibrated
                    # uncertainty — stated, never fabricated (spec §5)
                    "uncertainty_kind": "unavailable_post_selection",
                    "values": None,
                    "note": "L1-selected support; grid-quantized centers/widths; "
                            "amplitudes debiased by NNLS but post-selection "
                            "inference is not calibrated — use IC stability or "
                            "Bayesian posteriors for uncertainty",
                },
                "reference_sensitivity_range": {
                    "kind": "unavailable_single_fit", "range_ev": None,
                },
            }

        import copy

        non_verified = sorted({
            f"{slug}:{e['constant']}"
            for slug, entries in grammar.provenance.items()
            for e in entries if e.get("status") != "VERIFIED"
        })
        analysis = {
            "method": self.id,
            "basis": "L1 dictionary (NN coordinate descent) + debiased NNLS; "
                     "STAM:Methods 2024 DOI 10.1080/27660400.2024.2373046; "
                     "Tibshirani 1996 (LASSO)",
            "dictionary": {
                "atom_shape": "gaussian (symmetric — documented simplification)",
                "n_atoms": int(An.shape[1]),
                "n_widths": cfg["n_widths"],
                "asymmetric_slots_not_expressible": unexpressible,
            },
            "model_size_selection": (
                "HEURISTIC BIC on active dictionary atoms: "
                "n·ln(RSS/n) + k·ln(n), k = NNLS-active atom count — a "
                "fixed-dictionary heuristic, NOT calibrated evidence "
                "(collinear atoms make effective dof < k; λ-path selection "
                "on the same data adds post-selection optimism)"),
            "lambda_path": path_records,
            "selected_lambda": best["lambda"],
            "path_fully_converged": all(r["converged"] for r in path_records),
            "unverified_tunables": {k: cfg[k] for k in DEFAULTS},
            "regions": list(grammar.regions),
            "phase_ids": list(grammar.phase_ids),
            "constants_provenance": copy.deepcopy(grammar.provenance),
            "constants_provenance_scope": "region-wide",
            "uses_conditional_or_unverified_constants": non_verified,
            "limitations": "grid mismatch can split peaks; amplitude bias "
                           "mitigated (not removed) by debiasing; heavy "
                           "overlap / asymmetric lineshapes are out of "
                           "regime — decision-matrix entry 4",
        }
        return MethodResult(
            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
            confidence=confidence,
            diagnostics={"n_peaks": len(peaks), "bic": best["bic"],
                         "rss": best["rss"], "selected_lambda": best["lambda"],
                         "n_atoms_active": best["n_atoms_active"],
                         "kkt_violation": best["kkt_violation"],
                         "converged": best["converged"]},
        )
