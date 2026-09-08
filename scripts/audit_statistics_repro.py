#!/usr/bin/env python3
"""Read-only scientific audit reproducers; exit 1 when an invariant fails.

Run with the isolated environment: venv/bin/python scripts/audit_statistics_repro.py
No experimental data are read. Synthetic truth is constructed independently.
The JSON records measured behavior, rather than changing expected values to
match existing implementation. Failures here are audit findings, not a claim
that every statistical or scientific path has been validated.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from lmfit import Model

from fitting import _ds_g_dscore_gauss, _gaussian, ds_g_fwhm, run_fit
from autofit.criteria import f_test, is_nested
from autofit.grammar import (
    BackgroundType, CandidateGrammar, CandidateModel, ComponentSlot, LineShape,
)
from autofit.methods.least_squares import LeastSquaresMethod
from autofit.methods.multivariate_mcr import MultivariateMCRMethod


def check(name, passed, expected, observed, source):
    return {"name": name, "passed": bool(passed), "expected": expected,
            "observed": observed, "source": source}


def mcr_checks():
    x = np.arange(7, dtype=float)
    a = np.array([0, 1, 4, 9, 4, 1, 0], dtype=float)
    b = np.array([0, 0, 0, 0, 0, 1, 4], dtype=float)
    cases = [("mcr_identical_spectra", np.tile(a, (3, 1)), 1),
             ("mcr_constant_and_variable_species",
              a[None, :] + np.arange(1., 5.)[:, None] * b[None, :], 2)]
    results = []
    for name, data, rank in cases:
        out = MultivariateMCRMethod().run(x, data).analysis
        results.append(check(name, out["rank"] == rank,
                             {"noiseless_matrix_rank": rank},
                             {"matrix_rank": int(np.linalg.matrix_rank(data)),
                              "reported_states": out["rank"],
                              "reported_centered_pcs": out["n_centered_pcs"],
                              "lack_of_fit": out["lack_of_fit"],
                              "row_sums": data.sum(axis=1).tolist()},
                             "autofit/methods/multivariate_mcr.py:140-152"))
    return results


def nesting_check():
    def slot(role, window):
        return ComponentSlot(role=role, region="synthetic", phase_id="test",
                             be_window=window, line_shape=LineShape.GAUSSIAN,
                             fwhm_range=(.5, 3.))

    small = CandidateModel(name="small", background=BackgroundType.LINEAR,
                           slots=(slot("main", (0., 10.)),))
    large = CandidateModel(name="large", background=BackgroundType.LINEAR,
                           slots=(slot("main", (20., 30.)),
                                  slot("extra", (40., 50.))))

    def report(model, rss, count):
        return SimpleNamespace(model=model, absent_slots=[], primary_fit=
                               SimpleNamespace(residual_sum_sq=rss,
                                               n_params=count, n_data=200))
    s, l = report(small, 100., 3), report(large, 80., 6)
    nested = is_nested(s, l)
    result = f_test(s, l)
    return check("f_test_disjoint_shared_parameter_bounds",
                 not nested and result is None,
                 {"nested": False, "nominal_f_test": None},
                 {"nested": nested,
                  "nominal_p_value": result.p_value if result else None},
                 "autofit/criteria.py:60-110")


def area_checks():
    x = np.linspace(-4, 4, 161)
    # Independent Gaussian truth, with known constant background.
    mean = 100 + 1000 * np.exp(-4 * np.log(2) * (x / 1.5) ** 2)
    y = np.random.default_rng(77).poisson(mean).astype(float)
    spec = dict(id=1, shape="gaussian", amplitude=900, center=0,
                fwhm=1.4, fix_center=True)
    out = run_fit(x, y, [spec], background_method="manual",
                  manual_bg=[[-4, 100], [4, 100]])
    observed = out["individual_peaks"][0]["params"]["area"]["stderr"]
    # Match production's fit exactly, retain covariance to independently
    # propagate the finite-window integral, including amplitude-width terms.
    model = Model(_gaussian)
    params = model.make_params(amplitude=900, center=0, fwhm=1.4)
    params["amplitude"].set(min=0)
    params["center"].set(vary=False)
    params["fwhm"].set(min=.1, max=15)
    fitted = model.fit(y - 100, params, x=x, weights=1 / np.sqrt(y))
    amp, width = fitted.params["amplitude"].value, fitted.params["fwhm"].value
    shape = np.exp(-4 * np.log(2) * (x / width) ** 2)
    derivative = {"amplitude": np.trapezoid(shape, x),
                  "fwhm": np.trapezoid(amp * shape * 8 * np.log(2)
                                        * x ** 2 / width ** 3, x)}
    gradient = np.array([derivative[name] for name in fitted.var_names])
    expected = float(np.sqrt(gradient @ fitted.covar @ gradient))
    correlation = fitted.params["amplitude"].correl["fwhm"]
    checks = [check("gaussian_area_full_covariance",
                    observed is not None and np.isclose(observed, expected, rtol=.01),
                    {"area_stderr": expected, "relative_tolerance": .01},
                    {"area_stderr": observed,
                     "amplitude_width_correlation": correlation},
                    "fitting.py:1230-1239")]
    spec["fix_fwhm"] = True
    fixed = run_fit(x, y, [spec], background_method="manual",
                    manual_bg=[[-4, 100], [4, 100]])
    p = fixed["individual_peaks"][0]["params"]
    expected_fixed = float(p["area"]["value"] * p["amplitude"]["stderr"]
                           / p["amplitude"]["value"])
    observed_fixed = p["area"]["stderr"]
    checks.append(check("fixed_width_area_uncertainty",
                        observed_fixed is not None and np.isclose(
                            observed_fixed, expected_fixed, rtol=.01),
                        {"area_stderr": expected_fixed},
                        {"area_stderr": observed_fixed,
                         "amplitude_stderr": p["amplitude"]["stderr"]},
                        "fitting.py:1233-1239"))
    return checks


def asymmetric_width_check():
    x = np.linspace(-10, 10, 10001)  # odd length avoids separate FFT-origin bug
    alpha, beta, gaussian_fwhm = .49, .3, .8
    y = _ds_g_dscore_gauss(x, 1, 0, alpha, beta, gaussian_fwhm)
    peak = int(np.argmax(y))
    half = y[peak] / 2
    low = np.interp(half, y[:peak + 1], x[:peak + 1])
    high = np.interp(half, y[peak:][::-1], x[peak:][::-1])
    measured = float(high - low)
    # Exercise the production width routine against independent grid-based
    # half-maximum crossings; the baseline's symmetric estimate is retained
    # as explanatory evidence, never used as the passing expectation.
    estimate = ds_g_fwhm(alpha, beta, gaussian_fwhm)
    return check("asymmetric_dsg_effective_width",
                 np.isclose(estimate, measured, rtol=.02),
                 {"curve_fwhm_ev": measured, "relative_tolerance": .02},
                 {"effective_width_estimate_ev": estimate,
                  "alpha": alpha, "beta_ev": beta,
                  "gaussian_fwhm_ev": gaussian_fwhm,
                  "under_2ev_estimate_but_over_2ev_curve":
                      bool(estimate < 2 < measured)},
                 "autofit/engine.py:798-808")


def supplied_weights_check():
    x = np.linspace(-2, 3, 61)
    shape = np.exp(-4 * np.log(2) * ((x - .5) / .5) ** 2)
    # Deliberate model discrepancy gives different weighted amplitude optima.
    y = 1 + 10 * shape + 2 * np.exp(-((x - .85) / .2) ** 2)
    specs = [dict(id=1, shape="gaussian", amplitude=10, center=.5,
                  fwhm=.5, fix_center=True, fix_fwhm=True)]
    weight_arrays = [np.ones(len(x)), np.linspace(.001, 100, len(x))]
    expected, observed = [], []
    for weights in weight_arrays:
        # Exact weighted least-squares solution for the only free parameter.
        expected.append(float(np.sum(weights ** 2 * shape * y)
                              / np.sum(weights ** 2 * shape ** 2)))
        out = LeastSquaresMethod().run(
            x, y, weights=weights, peak_specs=specs,
            options={"background_method": "none"})
        observed.append(float(out.peaks[0]["amplitude"]))
    return check("manual_method_honors_supplied_weights",
                 np.allclose(observed, expected, rtol=1e-5, atol=1e-6),
                 {"weighted_analytic_amplitudes": expected},
                 {"fitted_amplitudes": observed,
                  "identical_despite_different_weights": observed[0] == observed[1]},
                 "autofit/methods/least_squares.py:34-60")


def bayesian_budget_checks():
    from autofit.methods.bayesian_exchange_mc import (
        BayesianExchangeMCMethod, _param_space, run_exchange_mc,
    )

    slot = ComponentSlot(role="peak", region="synthetic", phase_id="test",
                         be_window=(0., 1.), line_shape=LineShape.GAUSSIAN,
                         fwhm_range=(.1, 1.))
    model = CandidateModel(name="one", background=BackgroundType.LINEAR,
                           slots=(slot,))
    grammar = CandidateGrammar(regions=("synthetic",), phase_ids=("test",),
                               candidates=[model], diagnostic_windows={})
    x = np.linspace(-2, 3, 31)
    y = 1 + 10 * np.exp(-4 * np.log(2) * ((x - .5) / .5) ** 2)
    checks = []
    try:
        result = run_exchange_mc(x, y, _param_space(model, x, y),
                                 n_replicas=2, n_sweeps=20, rng_seed=0)
        betas = result["betas"]
        observed = {"rejected": False, "betas": betas,
                    "retained_samples": result["n_post"]}
        passed = bool(len(betas) > 0 and np.isclose(betas[-1], 1.))
    except ValueError as exc:
        # Rejecting an unsupported ladder is a valid future correction.
        observed = {"rejected": True, "reason": str(exc)}
        passed = True
    checks.append(check("bayesian_two_replicas_target_posterior", passed,
                        {"accepted_final_beta": 1.,
                         "explicit_validation_rejection_also_valid": True},
                        observed,
                        "autofit/methods/bayesian_exchange_mc.py:141-143,200-202"))

    try:
        out = BayesianExchangeMCMethod().run(
            x, y, grammar=grammar,
            options={"n_replicas": 4, "n_sweeps": 2, "rng_seed": 0})
        candidates = out.analysis.get("candidates", [])
        statuses = [c.get("sigma_stat", {}).get("reliability")
                    for c in out.confidence.values()]
        reliable_weights = [c.get("posterior_weight_reliable") for c in candidates]
        samples = [c.get("n_posterior_samples") for c in candidates]
        observed = {"rejected": not out.success,
                    "retained_samples": samples,
                    "minimum_ess": [c.get("min_effective_sample_size")
                                    for c in candidates],
                    "posterior_weight_reliable": reliable_weights,
                    "interval_reliability": statuses}
        # One retained draw cannot establish interval precision or MC
        # convergence. Refusal, unavailable results, or explicit unreliable
        # labels are acceptable; no-samples rejection also passes.
        passed = not out.success or (
            all(value is not True for value in reliable_weights)
            and all(status != "ok" for status in statuses))
    except ValueError as exc:
        observed = {"rejected": True, "reason": str(exc)}
        passed = True
    checks.append(check("bayesian_insufficient_samples_not_reliable", passed,
                        {"reliable_posterior_claim": False,
                         "explicit_validation_rejection_also_valid": True},
                        observed,
                        "autofit/methods/bayesian_exchange_mc.py:425-443,544-556"))
    return checks


def main():
    results = (mcr_checks() + [nesting_check()] + area_checks()
               + [asymmetric_width_check(), supplied_weights_check()]
               + bayesian_budget_checks())
    failed = sum(not result["passed"] for result in results)
    print(json.dumps({"schema_version": 1, "synthetic_only": True,
                      "checks": results, "failed": failed,
                      "passed": len(results) - failed}, indent=2, allow_nan=False))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
