"""How tests/test_scattered_starts.py::_two_basin_problem was chosen (two-basin unit, 2026-10-09).

A grid of candidate models (main 284.5 eV, a weak shoulder at 285.25 of amplitude cA, a line
at 286.7, a satellite at 288.8; the "shoulder" component started at sc2; Poisson noise seed
ns) is fitted as the tests fit it (Levenberg-Marquardt, linear background, no perturbed
restarts, six scattered starts). A candidate QUALIFIES when the student's fit converged and
is itself a certified minimum (the certificate does not move it), no centre sits on its
±2 eV bound, an alternative is listed with chi2r at least 5 % lower that moves a component
more than 1.15 eV and an area more than 2 pp, and at least one start reaches a not-better
minimum. It is ROBUST when, with the request seed held fixed, the floating-point linear
background instead of the exact one, ulps of 5 counts (three draws), start values changed by
4 ulps (both signs) and a repeat all give the same fit within rounding
(tests/fit_equality.assert_same_fit), and start values changed by 1e-6 (both signs) give
the same solutions (same counts; centres within 0.01 eV; alternatives' areas within 0.1 pp).

    venv/bin/python scripts/two_basin_fixture_search.py [OUT.jsonl]

SELECTION (printed at the end): among the robust candidates, those whose listed alternatives
all keep every centre off its ±2 eV bound (an alternative shifted by exactly 2.0 eV sits on
the bound: a scattered start pushed to the wall, not a decomposition), the largest student
chi2r. Measured 2026-10-09: 75 candidates, 15 qualify, 7 robust, 4 of them with no
alternative on a bound; selected cA = 1400, sc2 = 285.2, ns = 2 — chi2r 46.9, its one
alternative 13.7 (gap 33.3; the other three: 3.2-3.8) reached by 4 of 6 starts. (Three
robust candidates — gaps 38.2, 33.3, 29.2 — each list an
alternative on a bound.) Its robustness is pinned by
test_the_two_basin_fixture_is_inside_its_basins."""
import copy
import itertools
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path[:0] = [ROOT, os.path.join(ROOT, "tests")]

import numpy as np  # noqa: E402

import fitting  # noqa: E402
from fit_equality import assert_same_fit  # noqa: E402

KW = dict(background_method="linear", n_perturb=0)


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def make(cA, sc2, ns):
    rng = np.random.default_rng(ns)
    x = np.arange(280.0, 295.0, 0.05)
    y = rng.poisson(300 + _g(x, 284.5, 8000, 0.8) + _g(x, 285.25, cA, 0.7) + _g(x, 286.7, 3000, 1.0)
                    + _g(x, 288.8, 600, 1.8)).astype(float)
    specs = [{"id": 1, "name": "main", "shape": "gaussian", "center": 284.6, "amplitude": 6000.0, "amplitude_min": 0, "fwhm": 1.0},
             {"id": 2, "name": "shoulder", "shape": "gaussian", "center": sc2, "amplitude": 2000.0, "amplitude_min": 0, "fwhm": 1.0},
             {"id": 3, "name": "sat", "shape": "gaussian", "center": 288.5, "amplitude": 500.0, "amplitude_min": 0, "fwhm": 2.0}]
    return x, y, specs


def fit(x, y, specs, seed=None, line=None):
    real = fitting._line_through
    if line is not None:
        fitting._line_through = line
    try:
        kws = {"method": "leastsq", **({"fit_kws": {"seed": seed}} if seed is not None else {})}
        return fitting.run_fit(x, y, specs, n_starts=6, fit_kws=kws, **KW)
    finally:
        fitting._line_through = real


def float_line(x, x0, y0, x1, y1, span=None):
    y0, y1 = float(y0), float(y1)
    slope = (y1 - y0) / (x1 - x0) if x1 != x0 else 0.0
    return fitting._explicit_background(y0 + slope * (np.asarray(x, dtype=float) - x0), "Linear")


def qualifies(r, specs):
    st, c = r["starts"] or {}, r["certificate"] or {}
    on_bound = any(abs(abs(p["params"]["center"]["value"] - s["center"]) - 2.0) < 0.01
                   for p, s in zip(r["individual_peaks"], specs))
    alts = st.get("alternatives") or []
    return bool(r["success"] and c.get("certified") and not c.get("moved") and not on_bound and alts
                and alts[0]["chi2r"] < 0.95 * r["statistics"]["reduced_chi_square"]
                and abs(alts[0]["largest_centre_shift_from_start"]["ev"]) > 1.15
                and alts[0]["largest_fraction_difference_pp"] > 2 and st.get("n_not_better_elsewhere", 0) >= 1)


def robust(x, y, specs, base):
    seed, rng, why = base["random_seed"], np.random.default_rng(7), []
    strict = [("float line", y, specs, float_line, None)]
    for k in range(3):
        yy = y.copy()
        idx = rng.choice(len(y), 5, replace=False)
        yy[idx] = np.nextafter(yy[idx], np.inf if k % 2 == 0 else -np.inf)
        strict.append((f"ulps of counts {k}", yy, specs, None, seed))
    for f in (1 + 4 * 2.0 ** -53, 1 - 4 * 2.0 ** -53):
        strict.append((f"start x {f!r}", y, [{**s, **{q: s[q] * f for q in ("center", "amplitude", "fwhm")}} for s in specs], None, seed))
    strict.append(("repeat", y, specs, None, None))
    for label, yy, sp, line, sd in strict:
        r = fit(x, yy, sp, sd, line)
        try:
            assert_same_fit({**base, "random_seed": None}, {**r, "random_seed": None})
        except AssertionError as e:
            why.append(f"{label}: {str(e)[:160]}")
    for f in (1 + 1e-6, 1 - 1e-6):
        sp = [{**s, **{q: s[q] * f for q in ("center", "amplitude", "fwhm")}} for s in specs]
        r = fit(x, y, sp, seed)
        a, b = base["starts"], r["starts"]
        same = all(a[k] == b[k] for k in ("n_converged", "n_same_as_fit", "n_not_better_elsewhere", "n_in_alternatives"))
        same &= len(a["alternatives"]) == len(b["alternatives"]) and all(
            abs(p["params"]["center"]["value"] - q["params"]["center"]["value"]) < 0.01
            for p, q in zip(base["individual_peaks"], r["individual_peaks"]))
        for u, v in zip(a["alternatives"], b["alternatives"]):
            same &= all(abs(cu["params"]["center"] - cv["params"]["center"]) < 0.01 and abs(cu["area_percent"] - cv["area_percent"]) < 0.1
                        for cu, cv in zip(u["components"], v["components"]))
        if not same:
            why.append(f"start x {f!r}: a different solution")
    return why


def main(out):
    done = set()
    if os.path.exists(out):
        done = {json.loads(line)["key"] for line in open(out)}
    for cA, sc2, ns in itertools.product([0.0, 700.0, 1400.0], [285.2, 285.35, 285.45, 285.55, 285.7], [1, 2, 3, 4, 5]):
        key = f"{cA}|{sc2}|{ns}"
        if key in done:
            continue
        x, y, specs = make(cA, sc2, ns)
        base = fit(x, y, specs)
        rec = {"key": key, "chi2r": base["statistics"]["reduced_chi_square"], "qualifies": qualifies(base, specs)}
        if rec["qualifies"]:
            st = base["starts"]
            rec["alternatives"] = [(a["chi2r"], a["largest_centre_shift_from_start"]["ev"], a["largest_fraction_difference_pp"], a["n_starts"])
                                   for a in st["alternatives"]]
            rec["alternative_on_bound"] = any(abs(abs(c["params"]["center"] - s["center"]) - 2.0) < 0.01
                                              for a in st["alternatives"] for c, s in zip(a["components"], specs))
            rec["why_not_robust"] = robust(x, y, specs, copy.deepcopy(base))
            rec["robust"] = not rec["why_not_robust"]
        with open(out, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps(rec), flush=True)
    recs = [json.loads(line) for line in open(out)]
    robust_ = [r for r in recs if r.get("robust")]
    clean = [r for r in robust_ if not r["alternative_on_bound"]]
    pick = max(clean, key=lambda r: r["chi2r"]) if clean else None
    print(f"{len(recs)} candidates, {sum(r['qualifies'] for r in recs)} qualify, {len(robust_)} robust, "
          f"{len(clean)} with no alternative on a bound; selected: {pick and pick['key']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "two_basin_fixture_search.jsonl")
