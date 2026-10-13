#!/usr/bin/env python3
"""Q8 unit: does the shipped Auto-Fit show what the measurement predicted? Compares, per committed C 1s
tab, what Auto-Fit now shows (results_shipped.json's A, from scripts/q8_autofit_refit.py run against
the unit) with the measured final fit (results.json's B, built by the harness on main). Same request,
same seed: equal within Trust-Region's arithmetic jitter (CLAUDE.md "Reproducibility"). Also reports
results_shipped.json's B — a further refit of the shipped result — which shows whether Auto-Fit's
result is already at its minimum. Writes docs/findings/q8-autofit-refit/confirm.json."""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "docs/findings/q8-autofit-refit")
measured = {(r["file"], r["tab"]): r for r in json.load(open(os.path.join(D, "results.json")))}
shipped = {(r["file"], r["tab"]): r for r in json.load(open(os.path.join(D, "results_shipped.json")))}


def diff(a, b):
    # components by CENTRE (Auto-Fit locks every centre): neither the ids nor the "Unknown n" names are
    # assigned to the same component in every run. ONE-TO-ONE (Codex Q8 round 2): the assignment that
    # minimises the total centre distance; a component left without a partner counts as a full mismatch
    import numpy as np
    from scipy.optimize import linear_sum_assignment
    cost = np.array([[abs(p["center"] - q["center"]) for q in b["peaks"]] for p in a["peaks"]])
    rows, cols = linear_sum_assignment(cost)
    pairs = {r: b["peaks"][c] for r, c in zip(rows, cols)}
    def match(p):
        return pairs.get(a["peaks"].index(p), {"pct": float("inf")})
    return {"chi2r_rel": abs(a["chi2r"] - b["chi2r"]) / b["chi2r"],
            "R_pts": abs((a["rFactor"] or {}).get("rPct", 0) - (b["rFactor"] or {}).get("rPct", 0)),
            "max_dpp": max(abs(p["pct"] - match(p)["pct"]) for p in a["peaks"])}


rows, mismatch = [], []
for k, s in shipped.items():
    m = measured.get(k)
    if not m or not s.get("applied") or not (m.get("B_status") or {}).get("ok"):
        if bool(s.get("applied")) != bool(m and m.get("applied")):
            mismatch.append({"tab": " / ".join(k), "shipped_applied": s.get("applied"), "measured_applied": m and m.get("applied")})
        continue
    d = diff(s["A"], m["B"])
    d2 = diff(s["B"], s["A"]) if (s.get("B_status") or {}).get("ok") else None
    rows.append({"tab": " / ".join(k), "vs_measured": d, "refit_of_shipped": d2})
out = {"compared": len(rows), "applied_mismatch": mismatch,
       "shipped_vs_measured_max": {f: max(r["vs_measured"][f] for r in rows) for f in ("chi2r_rel", "R_pts", "max_dpp")},
       "refit_of_shipped_max": {f: max(r["refit_of_shipped"][f] for r in rows if r["refit_of_shipped"]) for f in ("chi2r_rel", "R_pts", "max_dpp")},
       "rows": rows}
json.dump(out, open(os.path.join(D, "confirm.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
