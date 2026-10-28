"""Unit B: does multiplying every σ by one constant s change a fit? Measured with the real ``run_fit``.

Each fit runs through an in-memory copy of fitting.py in which the ONE line that forms σ
(``sigma = np.sqrt(np.maximum(y, 1.0))``, fitting.py:3006 — asserted to occur exactly once) is
multiplied by s; nothing else differs (s = 1 multiplies by 1.0, exactly the production code). The
seed is a function of the request's inputs, which σ is not (fitting.py ``_request_seed``), so every
scale draws the same restarts.

A fit at scale s is compared with the fit at s = 1 after its χ²-valued fields are put back on the
s = 1 scale (χ², χ²ᵣ and every χ²ᵣ inside ``starts`` × s²; AIC / BIC + n·ln s²; each component's
support Δχ² × s²) with the app's own same-fit rule (``same_fit.fit_differences``: every quantity on
its own scale, the minimum's precision, uncertainties not compared). The uncertainties, the support
F and the χ² ratio are recorded separately. s = 1 is run twice, so each method's own run-to-run
difference (Trust-Region's BLAS alignment, CLAUDE.md "Reproducibility") is measured beside it.

Targets: the 202 committed fit targets (scripts/optimizer_disagreement_targets.js, the page's own
requests; its output is gitignored, read from the path below).

    venv/bin/python scripts/noise_sigma_scale_check.py run OUT.jsonl [--procs 4]
    venv/bin/python scripts/noise_sigma_scale_check.py analyse OUT.jsonl [--json SUMMARY.json]
"""
import argparse
import json
import math
import os
import sys
import types
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
TARGETS = ("/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/"
           "docs/findings/optimizer-disagreement/targets.json")
SIGMA_LINE = "    sigma = np.sqrt(np.maximum(y, 1.0))\n"
SCALES = (("1", 1.0), ("1-repeat", 1.0), ("2", 2.0), ("sqrt0.7", math.sqrt(0.7)))

# (method, n_starts, how many targets — the first N in the file's order)
PLAN = (("leastsq", 0, 202), ("least_squares", 0, 202),
        ("least_squares", 3, 30), ("nelder", 0, 30), ("basinhopping", 0, 8))

_scaled = None


def _module():
    """fitting.py with σ multiplied by the module global _SIGMA_SCALE (asserted single replacement)."""
    global _scaled
    if _scaled is None:
        sys.path.insert(0, ROOT)
        src = open(os.path.join(ROOT, "fitting.py")).read()
        assert src.count(SIGMA_LINE) == 1, "the σ line is not where this check expects it"
        src = src.replace(SIGMA_LINE, SIGMA_LINE.rstrip("\n") + " * _SIGMA_SCALE\n")
        mod = types.ModuleType("fitting_sigma_scaled")
        mod.__file__ = os.path.join(ROOT, "fitting.py")
        mod._SIGMA_SCALE = 1.0
        sys.modules["fitting_sigma_scaled"] = mod
        exec(compile(src, mod.__file__, "exec"), mod.__dict__)
        _scaled = mod
    return _scaled


def _task(t, method, n_starts, label, s):
    m = _module()
    m._SIGMA_SCALE = s
    bg = t["background"]
    try:
        r = m.run_fit(energy=np.asarray(t["be"], float), counts=np.asarray(t["inten"], float),
                      peak_specs=t["specs"], background_method=bg["method"], bg_start_idx=bg["start_idx"],
                      bg_end_idx=bg["end_idx"], endpoint_avg=bg["endpoint_avg"], n_perturb=3,
                      n_starts=n_starts, fit_kws={"method": method})
        r = json.loads(json.dumps(r, default=float))
        err = None
    except Exception as exc:  # recorded, never hidden
        r, err = None, f"{type(exc).__name__}: {exc}"
    return {"key": f"{t['id']}|{method}|{n_starts}|{label}", "id": t["id"], "method": method,
            "n_starts": n_starts, "label": label, "s": s, "error": err, "response": r}


def run(out, procs):
    T = json.load(open(TARGETS))
    done = set()
    if os.path.exists(out):
        done = {json.loads(line)["key"] for line in open(out)}
    jobs = [(t, method, n_starts, label, s)
            for method, n_starts, n in PLAN for t in T[:n] for label, s in SCALES
            if f"{t['id']}|{method}|{n_starts}|{label}" not in done]
    print(f"{len(jobs)} fits to run ({len(done)} done)", flush=True)
    with ProcessPoolExecutor(procs) as ex, open(out, "a") as f:
        futs = [ex.submit(_task, *j) for j in jobs]
        for i, fut in enumerate(as_completed(futs), 1):
            f.write(json.dumps(fut.result()) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"{i}/{len(jobs)}", flush=True)


def _rescaled(r, s):
    """The response at scale s with its χ²-valued fields put back on the s = 1 scale."""
    r = json.loads(json.dumps(r))
    s2 = s * s
    st = r["statistics"]
    st["chi_square"] *= s2
    st["reduced_chi_square"] *= s2
    for k in ("aic", "bic"):
        st[k] += st["n_data"] * math.log(s2)
    for pk in r.get("individual_peaks") or []:
        sup = pk.get("support") or {}
        if isinstance(sup.get("delta_chi2"), (int, float)):
            sup["delta_chi2"] *= s2
    starts = r.get("starts") or {}

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("chi2r", "not_better_chi2r") and isinstance(v, (int, float)):
                    o[k] = v * s2
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(starts)
    return r


def _params(r):
    return {f"{pk['id']}.{name}": info for pk in r["individual_peaks"]
            for name, info in (pk.get("params") or {}).items() if isinstance(info, dict)}


def _compare(base, other, s):
    sys.path.insert(0, ROOT)
    from same_fit import fit_differences
    a, b = base["response"], other["response"]
    out = {"error": other["error"] or base["error"]}
    if a is None or b is None:
        return out
    out["success"] = (a.get("success"), b.get("success"))
    out["differences"] = fit_differences(a, _rescaled(b, s))
    pa, pb = _params(a), _params(b)
    out["values_bit_identical"] = all(pa[k].get("value") == pb[k].get("value") for k in pa)
    out["chi2_ratio_rel_err"] = abs(b["statistics"]["chi_square"] * s * s / a["statistics"]["chi_square"] - 1)
    ratios = [abs(pb[k]["stderr"] / pa[k]["stderr"] - 1) for k in pa
              if isinstance(pa[k].get("stderr"), (int, float)) and isinstance(pb[k].get("stderr"), (int, float))
              and pa[k]["stderr"] > 0]
    out["stderr_max_rel_change"] = max(ratios) if ratios else None
    fs = [(x.get("support") or {}).get("f") for x in a["individual_peaks"]]
    gs = [(x.get("support") or {}).get("f") for x in b["individual_peaks"]]
    fr = [abs(g / f - 1) for f, g in zip(fs, gs) if f and g]
    out["support_f_max_rel_change"] = max(fr) if fr else None
    out["support_verdicts_equal"] = ([(x.get("support") or {}).get("supported") for x in a["individual_peaks"]]
                                     == [(x.get("support") or {}).get("supported") for x in b["individual_peaks"]])
    sa, sb = a.get("starts") or {}, b.get("starts") or {}
    if sa or sb:
        keys = ("n_run", "n_converged", "n_same_as_fit", "n_in_alternatives", "n_not_better_elsewhere")
        out["starts_counts_equal"] = all(sa.get(k) == sb.get(k) for k in keys)
    return out


def analyse(path, json_out):
    rows = [json.loads(line) for line in open(path)]
    by = {}
    for r in rows:
        by.setdefault((r["id"], r["method"], r["n_starts"]), {})[r["label"]] = r
    summary = {}
    for (tid, method, n_starts), runs in sorted(by.items()):
        if "1" not in runs:
            continue
        for label, s in SCALES[1:]:
            if label not in runs:
                continue
            c = _compare(runs["1"], runs[label], s)
            grp = summary.setdefault(f"{method} n_starts={n_starts}", {}).setdefault(label, [])
            grp.append({"id": tid, **c})
    report = {}
    lines = []
    for grp, by_label in summary.items():
        report[grp] = {}
        for label, cs in by_label.items():
            ok = [c for c in cs if "differences" in c]
            same = [c for c in ok if not c["differences"]]

            def mx(k):
                v = [c[k] for c in ok if c.get(k) is not None]
                return max(v) if v else None
            rec = {"targets": len(cs), "errors": len(cs) - len(ok), "same_fit": len(same),
                   "different_fit": len(ok) - len(same),
                   "values_bit_identical": sum(1 for c in ok if c["values_bit_identical"]),
                   "success_flag_changed": sum(1 for c in ok if c["success"][0] != c["success"][1]),
                   "support_verdict_changed": sum(1 for c in ok if not c["support_verdicts_equal"]),
                   "starts_counts_changed": sum(1 for c in ok if c.get("starts_counts_equal") is False),
                   "max_chi2_ratio_rel_err_same_fit": max((c["chi2_ratio_rel_err"] for c in same), default=None),
                   "max_stderr_rel_change_same_fit": max((c["stderr_max_rel_change"] for c in same
                                                          if c["stderr_max_rel_change"] is not None), default=None),
                   "max_support_f_rel_change_same_fit": max((c["support_f_max_rel_change"] for c in same
                                                             if c["support_f_max_rel_change"] is not None),
                                                            default=None),
                   "different": [{"id": c["id"], "differences": c["differences"][:3]}
                                 for c in ok if c["differences"]]}
            report[grp][label] = rec
            lines.append(f"{grp:28s} s={label:9s} targets {rec['targets']:3d}  same fit {rec['same_fit']:3d}  "
                         f"different {rec['different_fit']:3d}  bit-identical values {rec['values_bit_identical']:3d}  "
                         f"errors {rec['errors']}  success changed {rec['success_flag_changed']}  "
                         f"support changed {rec['support_verdict_changed']}  starts changed {rec['starts_counts_changed']}")
            lines.append(f"{'':28s}   same fits: χ²·s²/χ² − 1 ≤ {rec['max_chi2_ratio_rel_err_same_fit']!s:.9}  "
                         f"σ change ≤ {rec['max_stderr_rel_change_same_fit']!s:.9}  "
                         f"support F change ≤ {rec['max_support_f_rel_change_same_fit']!s:.9}")
    print("\n".join(lines))
    if json_out:
        json.dump(report, open(json_out, "w"), indent=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "analyse"))
    ap.add_argument("path")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--json")
    a = ap.parse_args()
    run(a.path, a.procs) if a.cmd == "run" else analyse(a.path, a.json)
