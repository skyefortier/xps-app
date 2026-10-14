"""Seal 1a′: is a branch's run_fit the same as main's on the 202 committed targets?

Loads two copies of fitting.py (main's and the branch's) into ONE process and fits each target
with both, the same request (full-precision arrays, the target's own background, n_perturb 3 as
the page sends, the target's seed derived by each copy), and compares the complete responses:
`identical` (every key byte-for-byte equal as JSON) or the keys that differ, and then whether
the two are the same fit within rounding (tests/fit_equality.py, the repo's standard). Keys named with
--ignore are left out of the comparison (e.g. `software`, which names the checkout), keys only
one side has are listed as `added` / `removed`. Resumable JSONL.

Usage: python scripts/seal_1a_identity.py MAIN_FITTING.py BRANCH_FITTING.py OUT.jsonl
           [--method leastsq] [--ignore software,statistics] [--targets PATH] [--only ID,ID]
A CONTROL (main against a copy of main) on the targets that differ separates the arithmetic's
own jitter (np.convolve / BLAS alignment, CLAUDE.md "Reproducibility") from a change.
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tests"))

TARGETS = ("/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/"
           "docs/findings/optimizer-disagreement/targets.json")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fit(mod, t, method):
    bg = t["background"]
    try:
        return mod.run_fit(np.asarray(t["be"], float), np.asarray(t["inten"], float), json.loads(json.dumps(t["specs"])),
                           background_method=bg["method"], bg_start_idx=bg["start_idx"], bg_end_idx=bg["end_idx"],
                           endpoint_avg=bg["endpoint_avg"], n_perturb=3, fit_kws={"method": method})
    except Exception as exc:  # noqa: BLE001
        return {"__error__": f"{type(exc).__name__}: {exc}"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("main"); ap.add_argument("branch"); ap.add_argument("out")
    ap.add_argument("--method", default="leastsq")
    ap.add_argument("--ignore", default="software")
    ap.add_argument("--targets", default=TARGETS)
    ap.add_argument("--only", default="", help="comma-separated target ids (a control run on a subset)")
    a = ap.parse_args()
    ignore = {k for k in a.ignore.split(",") if k}
    A, B = load(a.main, "fitting_main"), load(a.branch, "fitting_branch")
    T = json.load(open(a.targets))
    if a.only:
        T = [t for t in T if t["id"] in set(a.only.split(","))]
    done = {json.loads(l)["id"] for l in open(a.out)} if os.path.exists(a.out) else set()
    for t in T:
        if t["id"] in done:
            continue
        ra, rb = fit(A, t, a.method), fit(B, t, a.method)
        keys_a, keys_b = set(ra) - ignore, set(rb) - ignore
        shared = keys_a & keys_b                                  # a key only one side has is listed, not compared
        ca, cb = {k: ra[k] for k in shared}, {k: rb[k] for k in shared}
        added_stats = []
        if "statistics" in shared:                                # a statistic only one side reports (rmse)
            sk = set(ra["statistics"]) & set(rb["statistics"])
            added_stats = sorted(set(rb["statistics"]) - sk)
            ca["statistics"] = {k: ra["statistics"][k] for k in sk}
            cb["statistics"] = {k: rb["statistics"][k] for k in sk}
        differ = sorted(k for k in shared if json.dumps(ca[k], sort_keys=True) != json.dumps(cb[k], sort_keys=True))
        same = None
        if differ and "__error__" not in ra and "__error__" not in rb:
            from fit_equality import assert_same_fit            # the repo's "same fit within rounding"
            try:
                assert_same_fit(ca, cb)
                same = True
            except AssertionError as exc:
                same = str(exc)[:300]
        rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "shapes": sorted(set(t["shapes"])),
               "identical": not differ, "differ": differ, "same_fit_within_rounding": same,
               "added": sorted(keys_b - keys_a) + [f"statistics.{k}" for k in added_stats],
               "removed": sorted(keys_a - keys_b)}
        with open(a.out, "a") as f:
            f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
