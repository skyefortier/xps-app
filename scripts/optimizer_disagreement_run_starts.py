#!/usr/bin/env python3
"""Measurement only: is a DIFFERENT START a more independent second opinion
than a different local method? The n_perturb=3 correction run showed
Trust-Region and Levenberg-Marquardt landing in the same non-best minimum
from the same start, so their agreement is weak evidence.

Two variants, Trust-Region (the UI default), n_perturb=0, per target:
  nudge   : ONE fit from the page's start, except that any freely varying
            bounded shape parameter sitting within 1 % of a bound is moved
            5 % of its range inward (lmfit's bound transform has zero
            gradient at a bound, so a parameter that starts there can stay
            pinned for every gradient method).
  scatter : K_SCATTER fits from seeded random starts: amplitude x exp(U(+-ln 3)),
            fwhm x exp(U(+-ln 1.5)), free centres +-0.5 eV (the +-2 eV centre
            window stays anchored to the page's centre), bounded shape
            parameters uniform inside the middle 90 % of their range.

Usage: python scripts/optimizer_disagreement_run_starts.py targets.json out.jsonl [shard n_shards]
"""
import copy
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitting  # noqa: E402

K_SCATTER = 10
# spec key -> (fix flag, lo, hi) per backend shape; mirrors fitting._make_peak_params
SHAPE_BOUNDS = {
    "pseudo_voigt_gl": {"gl_ratio": ("fix_gl_ratio", 0.0, 1.0)},
    "asymmetric_gl": {"gl_ratio": ("fix_gl_ratio", 0.0, 1.0), "asymmetry": ("fix_asymmetry", None, None)},
    "doniach_sunjic": {"alpha": ("fix_alpha", 0.0, 0.5), "gamma_asym": ("fix_gamma_asym", 0.0, 5.0)},
    "ds_g": {"alpha": ("fix_alpha", 0.0, 0.49), "beta": ("fix_beta", 0.05, 2.0), "m_gauss": ("fix_m_gauss", 0.05, 4.0)},
    "la_casaxps": {"alpha": ("fix_alpha", 0.1, 5.0), "beta": ("fix_beta", 0.1, 5.0)},
}


def shape_params(spec):
    for key, (fix, lo, hi) in SHAPE_BOUNDS.get(spec.get("shape", "pseudo_voigt_gl"), {}).items():
        if spec.get(fix, False) or key not in spec:
            continue
        if key == "asymmetry":
            lo, hi = spec.get("asymmetry_min", 0.0), spec.get("asymmetry_max", 1.0)
        yield key, lo, hi


def pin_centre_window(spec):
    if spec.get("shape") != "ds_g":
        spec.setdefault("center_min", spec["center"] - 2.0)
        spec.setdefault("center_max", spec["center"] + 2.0)


def nudged(specs):
    out = copy.deepcopy(specs)
    moved = 0
    for s in out:
        if s.get("constrain_to") is not None:
            continue
        for key, lo, hi in shape_params(s):
            rng_ = hi - lo
            if s[key] - lo < 0.01 * rng_:
                s[key] = lo + 0.05 * rng_
                moved += 1
            elif hi - s[key] < 0.01 * rng_:
                s[key] = hi - 0.05 * rng_
                moved += 1
    return out, moved


def scattered(specs, rng):
    out = copy.deepcopy(specs)
    for s in out:
        if s.get("constrain_to") is not None:
            continue
        pin_centre_window(s)
        if not s.get("fix_amplitude", False):
            s["amplitude"] = max(s["amplitude"], 1.0) * float(np.exp(rng.uniform(-np.log(3), np.log(3))))
        if not s.get("fix_fwhm", False):
            w = s["fwhm"] * float(np.exp(rng.uniform(-np.log(1.5), np.log(1.5))))
            s["fwhm"] = float(np.clip(w, s.get("fwhm_min", 0.1) * 1.05, s.get("fwhm_max", 15.0) * 0.95))
        if not s.get("fix_center", False):
            c = s["center"] + float(rng.uniform(-0.5, 0.5))
            if "center_min" in s:
                c = float(np.clip(c, s["center_min"] + 0.05, s["center_max"] - 0.05))
            s["center"] = c
        for key, lo, hi in shape_params(s):
            s[key] = float(rng.uniform(lo + 0.05 * (hi - lo), hi - 0.05 * (hi - lo)))
    return out


def fit(t, specs):
    x = np.asarray(t["be"], float)
    y = np.asarray(t["inten"], float)
    bg = t["background"]
    t0 = time.time()
    try:
        res = fitting.run_fit(x, y, specs, background_method=bg["method"], bg_start_idx=bg["start_idx"],
                              bg_end_idx=bg["end_idx"], endpoint_avg=bg["endpoint_avg"], n_perturb=0,
                              fit_kws={"method": "least_squares"})
        rec = dict(success=bool(res["success"]), chi2r=res["statistics"].get("reduced_chi_square"),
                   peaks=[{"id": ip["id"], **{n: i["value"] for n, i in ip["params"].items()}} for ip in res["individual_peaks"]])
    except Exception as exc:
        rec = dict(success=False, error=f"{type(exc).__name__}: {exc}")
    rec["seconds"] = round(time.time() - t0, 2)
    return rec


def main(targets_path, out_path, shard=0, n_shards=1):
    targets = json.loads(Path(targets_path).read_text())
    if n_shards > 1:
        out_path = str(Path(out_path).with_suffix("")) + f".shard{shard}.jsonl"
    with open(out_path, "w") as fh:
        for k, t in enumerate(targets):
            if k % n_shards != shard:
                continue
            specs, moved = nudged(t["specs"])
            fh.write(json.dumps({"id": t["id"], "variant": "nudge", "rep": 0, "moved": moved, **fit(t, specs)}) + "\n")
            rng = np.random.default_rng(zlib.crc32(t["id"].encode()))
            for j in range(K_SCATTER):
                fh.write(json.dumps({"id": t["id"], "variant": "scatter", "rep": j, **fit(t, scattered(t["specs"], rng))}) + "\n")
            fh.flush()
            print(f"[{k + 1}/{len(targets)}] {t['tab']} done", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(int(a) for a in sys.argv[3:5]))
