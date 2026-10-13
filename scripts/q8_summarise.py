#!/usr/bin/env python3
"""Summarise docs/findings/q8-autofit-refit/results.json (scripts/q8_autofit_refit.py): what an
Auto-Fit shows today (A: one fit, shown after the charge shift) against the proposed final refit in
the corrected frame (B), per committed C 1s tab. Writes docs/findings/q8-autofit-refit/summary.json."""
import json, os, statistics as st

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "docs/findings/q8-autofit-refit")
rows = json.load(open(os.path.join(D, "results.json")))


def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(f * len(xs)))] if xs else None


applied = [r for r in rows if r.get("applied")]
refused = [r for r in rows if not r.get("applied")]
done = [r for r in applied if (r.get("B_status") or {}).get("ok")]
per = []
for r in done:
    A, B = r["A"], r["B"]
    pa = {p["id"]: p for p in A["peaks"]}
    dpp = [abs(p["pct"] - pa[p["id"]]["pct"]) for p in B["peaks"]]
    dfw = [abs(p["fwhm"] - pa[p["id"]]["fwhm"]) / pa[p["id"]]["fwhm"] for p in B["peaks"]]
    dam = [abs(p["amplitude"] - pa[p["id"]]["amplitude"]) / pa[p["id"]]["amplitude"] for p in B["peaks"] if pa[p["id"]]["amplitude"]]
    q5 = [abs(p["pct"] - p["server_pct"]) for p in B["peaks"] if p.get("server_pct") is not None]
    g = r["B_status"]["gates"]
    per.append({
        "tab": r["file"] + " / " + r["tab"],
        "chi2r_A": A["chi2r"], "chi2r_B": B["chi2r"], "chi2r_rel": (B["chi2r"] - A["chi2r"]) / A["chi2r"],
        "R_A": (A["rFactor"] or {}).get("rPct"), "R_B": (B["rFactor"] or {}).get("rPct"),
        "max_dpp": max(dpp), "max_dfwhm_rel": max(dfw), "max_damp_rel": max(dam) if dam else 0,
        "worst_component": max(B["peaks"], key=lambda p: abs(p["pct"] - pa[p["id"]]["pct"]))["name"],
        "A_points_vs_fitted": [A["n_points"], A["n_fitted"]],
        "warn40_A": bool(A["warn40"]), "warn40_B": bool(B["warn40"]),
        "B_anchor_supported": g["supported"], "B_anchor_required": g["required"], "B_refit_converged": g["refit_converged"],
        "q5_B_max_dpp_page_vs_server": max(q5) if q5 else None,
    })
summary = {
    "c1s_tabs": len(rows), "autofit_applied": len(applied), "autofit_refused": len(refused),
    "refusal_reasons": [{"tab": r["file"] + " / " + r["tab"], "red": [m for k, m in r["notes"] if k == "red"][:1]} for r in refused],
    "B_fit_failed": [{"tab": r["file"] + " / " + r["tab"], "status": r.get("B_status")} for r in applied if not (r.get("B_status") or {}).get("ok")],
    "compared": len(per),
    "A_window_points_differ_from_fitted_points": sum(1 for p in per if p["A_points_vs_fitted"][0] != p["A_points_vs_fitted"][1]),
    "area_pct_change_pp_max_per_tab": {"median": q([p["max_dpp"] for p in per], .5), "p90": q([p["max_dpp"] for p in per], .9),
                                       "max": max((p["max_dpp"] for p in per), default=None),
                                       "tabs_over_0_1_pp": sum(p["max_dpp"] > .1 for p in per), "tabs_over_1_pp": sum(p["max_dpp"] > 1 for p in per)},
    "fwhm_rel_change_max_per_tab": {"median": q([p["max_dfwhm_rel"] for p in per], .5), "max": max((p["max_dfwhm_rel"] for p in per), default=None)},
    "chi2r_rel_change": {"median": q([p["chi2r_rel"] for p in per], .5), "min": min((p["chi2r_rel"] for p in per), default=None),
                         "max": max((p["chi2r_rel"] for p in per), default=None),
                         "B_lower": sum(p["chi2r_rel"] < 0 for p in per), "B_higher": sum(p["chi2r_rel"] > 0 for p in per)},
    "R_change_pct_points_max": max((abs((p["R_B"] or 0) - (p["R_A"] or 0)) for p in per), default=None),
    "warn40_flips": [p["tab"] for p in per if p["warn40_A"] != p["warn40_B"]],
    "warn40_A": sum(p["warn40_A"] for p in per), "warn40_B": sum(p["warn40_B"] for p in per),
    "B_anchor_fails_gate": [p["tab"] for p in per if not (p["B_anchor_supported"] and p["B_anchor_required"] is not False and p["B_refit_converged"] is not False)],
    "q5_on_B_max_dpp_page_vs_server": max((p["q5_B_max_dpp_page_vs_server"] or 0 for p in per), default=None),
    "largest_changes": sorted(per, key=lambda p: -p["max_dpp"])[:6],
    "secs": {"A_median": st.median([r["secs_A"] for r in rows]), "B_median": st.median([r["secs_B"] for r in done]) if done else None},
}
json.dump({"summary": summary, "per_tab": per}, open(os.path.join(D, "summary.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
