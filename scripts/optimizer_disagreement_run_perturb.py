#!/usr/bin/env python3
"""Correction run for the optimiser-disagreement measurement.

The first run (optimizer_disagreement_run.py) called fitting.run_fit with
n_perturb=0. The page's Run Fit sends n_perturb=3: after the first
minimisation the server refits three times from a random +/-15 % perturbation
of the solution and keeps the lowest reduced chi-square. That is part of what
a student actually gets, so the first run did not measure the shipped path.

This run repeats Trust-Region and Levenberg-Marquardt with n_perturb=3.
The perturbation RNG is unseeded, so each (target, method) is run REPS times
and every repeat is recorded. Basin-hopping is not repeated (2 min per fit;
its n_perturb=0 results stay as a reference solution only).

Usage: python scripts/optimizer_disagreement_run_perturb.py targets.json out.jsonl [shard n_shards]
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitting  # noqa: E402

METHODS = ("least_squares", "leastsq")
N_PERTURB = 3          # what templates/index.html sends from runFit
REPS = 5


def main(targets_path: str, out_path: str, shard: int = 0, n_shards: int = 1) -> None:
    targets = json.loads(Path(targets_path).read_text())
    stem = Path(out_path).with_suffix("").name
    done = set()
    for existing in Path(out_path).parent.glob(stem + "*.jsonl"):
        for line in existing.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["id"], r["method"], r["rep"]))
    if n_shards > 1:
        out_path = str(Path(out_path).with_suffix("")) + f".shard{shard}.jsonl"
    with open(out_path, "a") as fh:
        for k, t in enumerate(targets):
            if k % n_shards != shard:
                continue
            x = np.asarray(t["be"], float)
            y = np.asarray(t["inten"], float)
            bg = t["background"]
            for method in METHODS:
                for rep in range(REPS):
                    if (t["id"], method, rep) in done:
                        continue
                    rec = {"id": t["id"], "method": method, "rep": rep, "n_perturb": N_PERTURB}
                    t0 = time.time()
                    try:
                        res = fitting.run_fit(x, y, t["specs"], background_method=bg["method"],
                                              bg_start_idx=bg["start_idx"], bg_end_idx=bg["end_idx"],
                                              endpoint_avg=bg["endpoint_avg"], n_perturb=N_PERTURB,
                                              fit_kws={"method": method})
                        st = res["statistics"]
                        rec.update(success=bool(res["success"]), message=res.get("message"),
                                   chi2r=st.get("reduced_chi_square"),
                                   peaks=[{"id": ip["id"], **{name: info["value"] for name, info in ip["params"].items()}}
                                          for ip in res["individual_peaks"]])
                    except Exception as exc:
                        rec.update(success=False, error=f"{type(exc).__name__}: {exc}")
                    rec["seconds"] = round(time.time() - t0, 2)
                    fh.write(json.dumps(rec) + "\n")
                    fh.flush()
            print(f"[{k + 1}/{len(targets)}] {t['tab']} ({t['kind']}) done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(int(a) for a in sys.argv[3:5]))
