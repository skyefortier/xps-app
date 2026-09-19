#!/usr/bin/env python3
"""Run every target from optimizer_disagreement_targets.js through the three
server methods a student can realistically choose — Trust-Region
(`least_squares`, the UI default), Levenberg-Marquardt (`leastsq`) and
basin-hopping — from the SAME start, and record what each reports.
Investigation only: calls fitting.run_fit exactly as /api/fit does; changes
nothing. Resumable: results are appended to a JSONL keyed by (target, method).

Usage: python scripts/optimizer_disagreement_run.py targets.json results.jsonl [shard n_shards]
Basin-hopping takes ~2 min per target, so the run is sharded: shard i of n
handles targets k with k % n == i and appends to results.shard<i>.jsonl next
to results.jsonl; every *.jsonl in that directory counts as already done.
Merge afterwards with `cat results*.jsonl | sort -u > merged.jsonl`.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitting  # noqa: E402

METHODS = ("least_squares", "leastsq", "basinhopping")


def main(targets_path: str, out_path: str, shard: int = 0, n_shards: int = 1) -> None:
    targets = json.loads(Path(targets_path).read_text())
    done = set()
    for existing in Path(out_path).parent.glob("*.jsonl"):
        for line in existing.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                done.add((r["id"], r["method"]))
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
                if (t["id"], method) in done:
                    continue
                rec = {"id": t["id"], "method": method}
                t0 = time.time()
                try:
                    res = fitting.run_fit(x, y, t["specs"], background_method=bg["method"],
                                          bg_start_idx=bg["start_idx"], bg_end_idx=bg["end_idx"],
                                          endpoint_avg=bg["endpoint_avg"], n_perturb=0,
                                          fit_kws={"method": method})
                    st = res["statistics"]
                    rec.update(success=bool(res["success"]), message=res.get("message"),
                               chi2r=st.get("reduced_chi_square"), n_free=st.get("n_free_params"), n_data=st.get("n_data"),
                               peaks=[{"id": ip["id"], **{name: info["value"] for name, info in ip["params"].items()}}
                                      for ip in res["individual_peaks"]])
                except Exception as exc:  # a method that errors is itself a result
                    rec.update(success=False, error=f"{type(exc).__name__}: {exc}")
                rec["seconds"] = round(time.time() - t0, 2)
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
            print(f"[{k + 1}/{len(targets)}] {t['project'][:28]} {t['tab']} ({t['kind']}) done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(int(a) for a in sys.argv[3:5]))
