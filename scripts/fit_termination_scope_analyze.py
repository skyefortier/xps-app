import json, sys, glob
sp = 'docs/findings/fit-termination-scope/'
for meth, files in (("Trust-Region (least_squares, page default)", ["scope_tr_a.jsonl", "scope_tr_b.jsonl"]), ("Levenberg-Marquardt (leastsq)", ["scope_lm_a.jsonl", "scope_lm_b.jsonl"])):
    rows = [json.loads(l) for f in files for l in open(sp + f)]
    drop = lambda c: (c["chisqr"] - c["refined"]) / c["chisqr"] if c.get("chisqr") else 0.0
    B = {"returned": [], "restart_ok": [], "start_ok": [], "start_failed_at_min": 0, "start_failed": 0}
    worst = []
    for r in rows:
        calls = [c for c in r["calls"] if "chisqr" in c]
        if not calls: continue
        head = calls[:4]; starts = calls[4:] if r.get("starts_ran") else []
        ok = [c for c in head if c["success"]]
        if r.get("success") and ok:
            ret = min(ok, key=lambda c: c["chisqr"])
            B["returned"].append(drop(ret)); worst.append((drop(ret), r["id"], ret["redchi"], ret["nfev"]))
        B["restart_ok"] += [drop(c) for c in head[1:] if c["success"]]
        for c in starts:
            if c["success"]: B["start_ok"].append(drop(c))
            else:
                B["start_failed"] += 1
                B["start_failed_at_min"] += drop(c) < 1e-6
    def dist(v):
        n = len(v)
        return f"n {n}: drop >1e-6 {sum(d > 1e-6 for d in v)}, >1e-3 {sum(d > 1e-3 for d in v)}, >1% {sum(d > 0.01 for d in v)}, >10% {sum(d > 0.1 for d in v)}"
    print("==", meth, f"({len(rows)} targets)")
    print("  returned fit (what the student gets), flagged success:", dist(B["returned"]))
    print("  perturbed restarts flagged success:                ", dist(B["restart_ok"]))
    print("  scattered starts flagged success:                  ", dist(B["start_ok"]))
    print(f"  scattered starts flagged FAILED: {B['start_failed']}, of which already at a minimum (refine drop < 1e-6): {B['start_failed_at_min']}")
    for d, i, rc, nf in sorted(worst, reverse=True)[:6]:
        print(f"     worst returned: {i}  chi2r {rc:.3f}  nfev {nf}  refine lowers chi2 by {100*d:.2f} %")
