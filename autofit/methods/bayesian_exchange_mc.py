"""
Method 3 — Bayesian spectral decomposition by replica-exchange Monte Carlo
(the window flagship; decision matrix entry 3).

Literature basis (all DOIs verified in the decision matrix):
- Nagata, Sugita & Okada, "Bayesian spectral deconvolution with the
  exchange Monte Carlo method", Neural Networks 25 (2012) 82,
  DOI 10.1016/j.neunet.2011.12.001 — replica exchange over an inverse-
  temperature ladder; Bayes free energy by thermodynamic integration /
  stepping-stone across the ladder; model (peak-count) selection by F.
- Tokuda, Nagata & Okada, JPSJ 86 (2017) 024001,
  DOI 10.7566/JPSJ.86.024001 — joint estimation of noise level and number
  of peaks in the same framework.
- Kumazoe/Akai et al., Sci. Rep. 13 (2023) 13221 — XPS application.

Implementation choices (documented; all sampler knobs are UNVERIFIED
tunables in the spec-§9 sense):

- Likelihood: Gaussian iid with UNKNOWN σ, log-marginalized analytically —
  for processed (non-count) XPS intensities a Gaussian model with an
  estimated noise scale is the defensible default (fitalg LIMITATIONS §8;
  spec §5).  With Jeffreys prior p(σ) ∝ 1/σ the σ-marginal log-likelihood
  is  −(n/2)·log RSS(θ) + const,  so the sampler targets RSS directly and
  the noise estimate  σ̂² = RSS/n  is a per-sample by-product (reported
  from the posterior).
- Priors: uniform within each free parameter's grammar bounds — the same
  physically-motivated bounds the least-squares path uses (an explicit,
  honest prior; spec's evidence-engine stance).
- Tempering: β ∈ geometric ladder from β_min to 1 plus β = 0 (the prior
  replica), K replicas.  Random-walk Metropolis within replicas (per-
  parameter Gaussian steps scaled to the prior width), adjacent-pair
  exchange sweeps.  Step sizes adapt toward a target acceptance DURING
  BURN-IN ONLY and are frozen afterwards (detailed balance).
- Bayes free energy: stepping-stone estimator across the ladder,
  F = −log Z(1) + log Z(0) = −Σ_k log⟨exp(−(β_{k+1}−β_k)·nE)⟩_{β_k},
  with E = ½·log-RSS energy from the σ-marginal likelihood (see
  _log_likelihood).  Log-sum-exp stabilized.
- Model (peak-count) selection: run every grammar candidate, compare F;
  report ΔF and the posterior model weights ∝ exp(−F).
- Uncertainty: per-parameter posterior median + central credible interval,
  reported with uncertainty_kind='posterior_ci' — a NEW typed kind, never
  mixed with 'covariance'/'stability_mad' numerics (spec §5 discipline).

Determinism: fully seeded (rng_seed).  Runtime scales with
n_replicas × n_sweeps × n_free_params × cost(model eval); defaults target
minutes on real regions — tests use reduced settings on synthetic spectra.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from ..engine import (
    _compute_background,
    _default_params_from_slots,
    _build_composite_model,
    _extract_fitted_components,
    _slot_prefix,
)
from ..grammar import BACKEND_SHAPE, CandidateGrammar, CandidateModel
from .base import MethodResult, PeakFitMethod

# ── UNVERIFIED sampler tunables (defaults; all overridable via options) ──────
DEFAULT_N_REPLICAS = 12
DEFAULT_BETA_MIN = 1e-4
DEFAULT_N_SWEEPS = 1500
DEFAULT_BURN_FRACTION = 0.5
DEFAULT_EXCHANGE_EVERY = 5
DEFAULT_TARGET_ACCEPT = 0.30
DEFAULT_CI_LEVEL = 0.68              # central credible interval (1σ-like)
INITIAL_STEP_FRACTION = 0.05         # of each prior width


@dataclass
class _ParamSpace:
    """Free-parameter view of a CandidateModel's lmfit Parameters."""
    names: list[str]
    lows: np.ndarray
    highs: np.ndarray
    params: Any                       # lmfit Parameters (exprs resolve here)
    composite: Any                    # lmfit composite Model

    def model_eval(self, x: np.ndarray, theta: np.ndarray) -> np.ndarray:
        for name, v in zip(self.names, theta):
            self.params[name].value = float(v)
        # update_constraints resolves expression-linked params (doublets etc.)
        self.params.update_constraints()
        return self.composite.eval(self.params, x=x)


def _param_space(model: CandidateModel, x, y_net) -> _ParamSpace:
    params = _default_params_from_slots(model, x=x, y_net=y_net)
    composite = _build_composite_model(model)
    names, lows, highs = [], [], []
    for name, par in params.items():
        if not par.vary or par.expr is not None:
            continue
        if not (np.isfinite(par.min) and np.isfinite(par.max)) or par.max <= par.min:
            raise ValueError(
                f"Bayesian sampler requires finite prior bounds; {name} has "
                f"[{par.min}, {par.max}]"
            )
        names.append(name)
        lows.append(par.min)
        highs.append(par.max)
    return _ParamSpace(names=names, lows=np.array(lows), highs=np.array(highs),
                       params=params, composite=composite)


def _log_likelihood(rss: float, n: int) -> float:
    """σ-marginalized Gaussian log-likelihood up to a θ-independent constant:
    ∫ N(y|f,σ)·(1/σ) dσ ∝ RSS^(−n/2)."""
    return -0.5 * n * np.log(max(rss, 1e-300))


def run_exchange_mc(
    x: np.ndarray,
    y_net: np.ndarray,
    space: _ParamSpace,
    weights: Optional[np.ndarray] = None,
    n_replicas: int = DEFAULT_N_REPLICAS,
    beta_min: float = DEFAULT_BETA_MIN,
    n_sweeps: int = DEFAULT_N_SWEEPS,
    burn_fraction: float = DEFAULT_BURN_FRACTION,
    exchange_every: int = DEFAULT_EXCHANGE_EVERY,
    rng_seed: int = 0,
) -> dict:
    """
    Replica-exchange MC over ``space`` targeting the σ-marginal posterior.
    Returns posterior samples (β=1 replica, post-burn-in), the Bayes free
    energy (stepping-stone), acceptance statistics, and the noise estimate.
    """
    rng = np.random.default_rng(rng_seed)
    n = len(y_net)
    w = np.ones(n) if weights is None else np.asarray(weights, dtype=float)

    # β ladder: 0 (prior) + geometric β_min…1
    betas = np.concatenate([[0.0],
                            np.geomspace(beta_min, 1.0, n_replicas - 1)])
    K = len(betas)
    dim = len(space.names)
    span = space.highs - space.lows

    def loglik(theta: np.ndarray) -> float:
        f = space.model_eval(x, theta)
        rss = float(np.sum((w * (y_net - f)) ** 2))
        return _log_likelihood(rss, n)

    # init: all replicas at independent uniform draws
    thetas = space.lows + rng.uniform(size=(K, dim)) * span
    lls = np.array([loglik(t) for t in thetas])
    steps = np.full((K, dim), INITIAL_STEP_FRACTION) * span
    burn = int(n_sweeps * burn_fraction)

    accept = np.zeros(K)
    propose = np.zeros(K)
    swap_accept = 0
    swap_propose = 0
    post_samples: list[np.ndarray] = []          # β=1 chain, post-burn
    post_lls: list[float] = []
    # per-replica post-burn loglik records for the stepping-stone estimator
    ll_records: list[list[float]] = [[] for _ in range(K)]

    for sweep in range(n_sweeps):
        for k in range(K):
            # one Metropolis pass over all coordinates (vectorized proposal,
            # sequential accept per coordinate keeps detailed balance simple)
            for j in range(dim):
                prop = thetas[k].copy()
                prop[j] += rng.normal(0.0, steps[k, j])
                if prop[j] < space.lows[j] or prop[j] > space.highs[j]:
                    propose[k] += 1
                    continue          # uniform prior: out-of-bounds rejected
                ll_prop = loglik(prop)
                propose[k] += 1
                if np.log(rng.uniform()) < betas[k] * (ll_prop - lls[k]):
                    thetas[k] = prop
                    lls[k] = ll_prop
                    accept[k] += 1
            # step adaptation during burn-in only
            if sweep < burn and sweep > 0 and sweep % 25 == 0:
                rate = accept[k] / max(propose[k], 1)
                factor = np.exp(0.3 * (rate - DEFAULT_TARGET_ACCEPT))
                steps[k] = np.clip(steps[k] * factor,
                                   1e-6 * span, 0.5 * span)

        if sweep % exchange_every == 0:
            for k in range(K - 1):
                swap_propose += 1
                dlog = (betas[k + 1] - betas[k]) * (lls[k] - lls[k + 1])
                if np.log(rng.uniform()) < dlog:
                    thetas[[k, k + 1]] = thetas[[k + 1, k]]
                    lls[[k, k + 1]] = lls[[k + 1, k]]
                    swap_accept += 1

        if sweep >= burn:
            post_samples.append(thetas[-1].copy())
            post_lls.append(float(lls[-1]))
            for k in range(K):
                ll_records[k].append(float(lls[k]))

    # ── Bayes free energy: stepping-stone across the ladder ──
    # log Z(1)/Z(0) = Σ_k log ⟨exp((β_{k+1}−β_k)·loglik)⟩_{β_k}
    log_z = 0.0
    for k in range(K - 1):
        d = betas[k + 1] - betas[k]
        lr = d * np.asarray(ll_records[k])
        m = float(np.max(lr))
        log_z += m + float(np.log(np.mean(np.exp(lr - m))))
    free_energy = -log_z

    samples = np.asarray(post_samples)
    # posterior noise estimate from the σ-marginal model: σ̂² = RSS/n per
    # sample; report the posterior-median σ̂
    rss_samples = np.exp(-2.0 * np.asarray(post_lls) / n)
    sigma_hat = float(np.median(np.sqrt(rss_samples / n)))

    return {
        "samples": samples,
        "names": list(space.names),
        "free_energy": float(free_energy),
        "sigma_hat": sigma_hat,
        "acceptance": (accept / np.maximum(propose, 1)).tolist(),
        "swap_acceptance": swap_accept / max(swap_propose, 1),
        "betas": betas.tolist(),
        "n_post": len(post_samples),
        "ess": _effective_sample_sizes(samples),
    }


def _effective_sample_sizes(samples: np.ndarray) -> list[float]:
    """
    Crude per-parameter effective sample size via the initial-positive-
    sequence truncation of the autocorrelation sum.  Random-walk chains are
    strongly autocorrelated, so credible intervals from few effective
    samples UNDERESTIMATE uncertainty — consumers must check this before
    trusting the CIs (surfaced as an explicit warning in the analysis
    payload).
    """
    if samples.ndim != 2 or len(samples) < 8:
        return []
    n, dim = samples.shape
    out = []
    for j in range(dim):
        c = samples[:, j] - samples[:, j].mean()
        var = float(np.dot(c, c)) / n
        if var <= 0:
            out.append(float(n))
            continue
        tau = 1.0
        for lag in range(1, min(n // 2, 200)):
            rho = float(np.dot(c[:-lag], c[lag:])) / ((n - lag) * var)
            if rho <= 0.0:
                break
            tau += 2.0 * rho
        out.append(float(n / tau))
    return out


_ALLOWED_OPTIONS = {
    "n_replicas", "beta_min", "n_sweeps", "burn_fraction", "exchange_every",
    "rng_seed", "candidate_filter", "ci_level", "noise_floor",
}


class BayesianExchangeMCMethod(PeakFitMethod):
    id = "bayesian_exchange_mc"
    label = "Bayesian (exchange Monte Carlo)"
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
            raise ValueError("bayesian_exchange_mc requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown bayesian_exchange_mc options: {sorted(unknown)}")

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        ci = float(opts.pop("ci_level", DEFAULT_CI_LEVEL))
        mc_kwargs = dict(
            n_replicas=int(opts.pop("n_replicas", DEFAULT_N_REPLICAS)),
            beta_min=float(opts.pop("beta_min", DEFAULT_BETA_MIN)),
            n_sweeps=int(opts.pop("n_sweeps", DEFAULT_N_SWEEPS)),
            burn_fraction=float(opts.pop("burn_fraction", DEFAULT_BURN_FRACTION)),
            exchange_every=int(opts.pop("exchange_every", DEFAULT_EXCHANGE_EVERY)),
            rng_seed=int(opts.pop("rng_seed", 0)),
        )
        opts.pop("noise_floor", None)     # accepted for symmetry; unused
        candidates = grammar.candidates
        cand_filter = opts.pop("candidate_filter", None)
        if cand_filter is not None:
            wanted = set(cand_filter)
            candidates = [c for c in candidates if c.name in wanted]

        per_candidate: list[dict] = []
        runs: dict[str, dict] = {}
        for model in candidates:
            bg = _compute_background(x, y, model.background)
            y_net = y - bg
            try:
                space = _param_space(model, x, y_net)
                run = run_exchange_mc(x, y_net, space, weights=weights, **mc_kwargs)
            except Exception as exc:
                per_candidate.append({"name": model.name, "error": str(exc)})
                continue
            runs[model.name] = {"run": run, "model": model, "space": space,
                                "bg": bg, "y_net": y_net}
            min_ess = float(min(run["ess"])) if run["ess"] else 0.0
            per_candidate.append({
                "name": model.name,
                "free_energy": run["free_energy"],
                "sigma_hat": run["sigma_hat"],
                "n_components": int(model.n_components),
                "swap_acceptance": run["swap_acceptance"],
                "n_posterior_samples": int(run["n_post"]),
                "min_effective_sample_size": min_ess,
                # Honesty gate on the "calibrated uncertainty" claim: with a
                # low ESS the chains are too correlated for the credible
                # intervals to be trusted — increase n_sweeps.
                "ci_reliability_warning": (
                    "LOW effective sample size — credible intervals likely "
                    "underestimate uncertainty; increase n_sweeps"
                ) if min_ess < 50 else None,
            })

        scored = [c for c in per_candidate if "free_energy" in c]
        if not scored:
            return MethodResult(
                method_id=self.id, success=False,
                analysis={"method": self.id, "candidates": per_candidate},
                message="no candidate produced a valid posterior",
            )

        # posterior model weights ∝ exp(−F) (uniform model prior)
        fs = np.array([c["free_energy"] for c in scored])
        wts = np.exp(-(fs - fs.min()))
        wts = wts / wts.sum()
        for c, wt in zip(scored, wts):
            c["posterior_weight"] = float(wt)
        scored.sort(key=lambda c: c["free_energy"])
        for i, c in enumerate(scored):
            c["rank"] = i + 1
        winner_name = scored[0]["name"]
        win = runs[winner_name]

        import copy

        peaks, confidence = _posterior_peaks(win, ci)
        non_verified = sorted({
            f"{slug}:{e['constant']}"
            for slug, entries in grammar.provenance.items()
            for e in entries if e.get("status") != "VERIFIED"
        })
        analysis = {
            "method": self.id,
            "likelihood": "gaussian_sigma_marginalized (processed-data model; "
                          "Jeffreys prior on sigma)",
            "priors": "uniform within grammar bounds",
            "regions": list(grammar.regions),
            "phase_ids": list(grammar.phase_ids),
            "constants_provenance": copy.deepcopy(grammar.provenance),
            "constants_provenance_scope": "region-wide",
            "uses_conditional_or_unverified_constants": non_verified,
            "candidates": per_candidate,
            "model_selection": "Bayes free energy (stepping-stone across the "
                               "replica ladder); posterior weights under a "
                               "uniform model prior",
            "sampler": {k: mc_kwargs[k] for k in mc_kwargs},
        }
        return MethodResult(
            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
            confidence=confidence,
            diagnostics={
                "winner": winner_name,
                "free_energy": scored[0]["free_energy"],
                "posterior_weight": scored[0]["posterior_weight"],
                "sigma_hat": scored[0]["sigma_hat"],
                "swap_acceptance": scored[0]["swap_acceptance"],
            },
        )


def _posterior_peaks(win: dict, ci_level: float) -> tuple[list[dict], dict]:
    """Posterior-median decomposition + per-slot posterior_ci confidence."""
    run, model, space = win["run"], win["model"], win["space"]
    samples, names = run["samples"], run["names"]
    lo_q = 0.5 * (1.0 - ci_level)
    med = np.median(samples, axis=0)
    qlo = np.quantile(samples, lo_q, axis=0)
    qhi = np.quantile(samples, 1.0 - lo_q, axis=0)

    # evaluate the median parameter vector through the composite so
    # expression-linked params (doublets, satellites) resolve
    for name, v in zip(names, med):
        space.params[name].value = float(v)
    space.params.update_constraints()

    class _R:  # minimal ModelResult stand-in for _extract_fitted_components
        params = space.params

    comps = _extract_fitted_components(_R, model)

    by_name = dict(zip(names, range(len(names))))
    peaks, confidence = [], {}
    for slot in model.slots:
        comp = next((c for c in comps if c.slot_role == slot.role), None)
        if comp is None:
            continue
        peaks.append({
            "role": slot.role, "region": slot.region, "phase_id": slot.phase_id,
            "shape": BACKEND_SHAPE[slot.line_shape],
            "center": comp.position, "fwhm": comp.fwhm,
            "amplitude": comp.amplitude, **comp.shape_params,
        })
        prefix = _slot_prefix(slot.role)
        intervals = {}
        for name in names:
            if name.startswith(prefix):
                j = by_name[name]
                intervals[name[len(prefix):]] = {
                    "median": float(med[j]),
                    "ci_low": float(qlo[j]), "ci_high": float(qhi[j]),
                    "ci_level": ci_level,
                }
        confidence[slot.role] = {
            "sigma_stat": {
                # typed posterior kind — NEVER mixed with covariance /
                # stability_mad numerics (spec §5 discipline)
                "uncertainty_kind": "posterior_ci",
                "values": intervals or None,
            },
            "reference_sensitivity_range": {
                "kind": "unavailable_single_fit", "range_ev": None,
            },
        }
    return peaks, confidence
