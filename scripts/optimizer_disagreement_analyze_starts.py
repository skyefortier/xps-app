#!/usr/bin/env python3
"""Analyse the alternative-start measurement against the shipped default.

Reference per target = lowest reduced chi-square seen in ANY run of it
(n_perturb=0 x 3 methods, n_perturb=3 x 5 repeats x 2 methods, nudge, 10
scattered starts). Best known, not ground truth.

Usage: python scripts/optimizer_disagreement_analyze_starts.py <dir> [--md out.md]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

TR, LM = "least_squares", "leastsq"


def fr(rec):
    a = np.array([max(float(p.get("area") or 0.0), 0.0) for p in rec["peaks"]])
    return 100 * a / a.sum() if a.sum() > 0 else a


def ok(r):
    return r is not None and "error" not in r and r.get("chi2r") is not None and r.get("peaks")


def main(d, md_out):
    T = {t["id"]: t for t in json.loads((d / "targets.json").read_text())}
    np0 = defaultdict(dict)
    np3 = defaultdict(lambda: defaultdict(dict))
    st = defaultdict(lambda: defaultdict(dict))
    for line in (d / "results.jsonl").read_text().splitlines():
        r = json.loads(line); np0[r["id"]][r["method"]] = r
    for line in (d / "results_perturb3.jsonl").read_text().splitlines():
        r = json.loads(line); np3[r["id"]][r["method"]][r["rep"]] = r
    for f in sorted(d.glob("results_starts*.jsonl")):
        for line in f.read_text().splitlines():
            r = json.loads(line); st[r["id"]][r["variant"]][r["rep"]] = r
    rows = []
    for tid, t in T.items():
        pool = [r for r in np0[tid].values()] + [r for m in np3[tid].values() for r in m.values()] + [r for v in st[tid].values() for r in v.values()]
        pool = [r for r in pool if ok(r)]
        if not pool or "scatter" not in st[tid]:
            continue
        ref = min(pool, key=lambda r: r["chi2r"])
        rf = fr(ref)

        def off(rec, rf=rf):
            return float(np.max(np.abs(fr(rec) - rf))) if ok(rec) else float("inf")

        sc = [st[tid]["scatter"][k] for k in sorted(st[tid]["scatter"])]
        default = [np3[tid][TR][k] for k in sorted(np3[tid][TR])]
        lm = [np3[tid][LM][k] for k in sorted(np3[tid][LM])]
        rows.append(dict(
            id=tid, t=t, kind=t["kind"], n_peaks=len(t["specs"]),
            default_off=[off(r) for r in default],
            default_chi=[r["chi2r"] for r in default],
            lm_pair=[float(np.max(np.abs(fr(a) - fr(b)))) if ok(a) and ok(b) else float("inf") for a, b in zip(default, lm)],
            nudge_off=off(st[tid]["nudge"][0]), nudge_moved=st[tid]["nudge"][0].get("moved", 0),
            nudge_vs_default=float(np.max(np.abs(fr(st[tid]["nudge"][0]) - fr(default[0])))) if ok(st[tid]["nudge"][0]) else float("inf"),
            # best of the first K scattered starts, K = 3, 5, 10
            bestK={K: (min([r for r in sc[:K] if ok(r) and r.get("success")], key=lambda r: r["chi2r"], default=None)) for K in (3, 5, 10)},
            off_fn=off, seconds=sum(r.get("seconds", 0) for r in sc),
        ))
    out = []
    P = out.append
    n = len(rows)
    P("# Optimiser disagreement — is a different START a better second opinion than a different local method?\n")
    P(f"Targets: **{n}**. Reference = lowest χ²ᵣ seen in any run of the target (best known, not ground truth). "
      "'Default' = Trust-Region with the page's n_perturb: 3 (5 repeats). 'Scatter K' = best χ²ᵣ of K Trust-Region fits from seeded random starts.\n")
    P("## 1. How often the REPORTED fit is more than 5 pp (1 pp) from the reference\n")
    P("| start | default alone | better of default + LM | better of default + nudge | better of default + scatter 3 | + scatter 5 | + scatter 10 |\n|---|---:|---:|---:|---:|---:|---:|")
    for thr in (5.0, 1.0):
        for kind, lab in ((None, "all"), ("own", "saved-solution re-fit"), ("batch", "not-yet-fitted start")):
            sub = [r for r in rows if kind is None or r["kind"] == kind]
            tot = 5 * len(sub)
            cells = []
            d_alone = sum(o > thr for r in sub for o in r["default_off"])
            cells.append(d_alone)
            # default + LM
            c = 0
            for r in sub:
                tid = r["id"]
                for k, dchi in enumerate(r["default_chi"]):
                    l = np3[tid][LM][k]
                    use_lm = ok(l) and l.get("success") and l["chi2r"] < dchi
                    c += (r["off_fn"](l) if use_lm else r["default_off"][k]) > thr
            cells.append(c)
            c = 0
            for r in sub:
                nd = st[r["id"]]["nudge"][0]
                for k, dchi in enumerate(r["default_chi"]):
                    use = ok(nd) and nd.get("success") and nd["chi2r"] < dchi
                    c += (r["nudge_off"] if use else r["default_off"][k]) > thr
            cells.append(c)
            for K in (3, 5, 10):
                c = 0
                for r in sub:
                    b = r["bestK"][K]
                    for k, dchi in enumerate(r["default_chi"]):
                        use = b is not None and b["chi2r"] < dchi
                        c += (r["off_fn"](b) if use else r["default_off"][k]) > thr
                cells.append(c)
            P(f"| {lab}, > {thr:g} pp (n={tot}) | " + " | ".join(f"{c} ({100*c/tot:.1f} %)" for c in cells) + " |")
    P("")
    P("## 2. As a FLAG: when the default is more than 5 pp off, does the second opinion differ from it by more than 5 pp?\n")
    P("| start | default off (pairs) | LM flags | nudge flags | scatter-3 best flags | scatter-5 | scatter-10 | false alarms when default is fine: LM | nudge | scatter-3 | scatter-5 | scatter-10 |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    thr = 5.0
    for kind, lab in ((None, "all"), ("own", "saved-solution re-fit"), ("batch", "not-yet-fitted start")):
        sub = [r for r in rows if kind is None or r["kind"] == kind]
        offn = okn = 0
        hit = defaultdict(int); fa = defaultdict(int)
        for r in sub:
            tid = r["id"]
            for k, o in enumerate(r["default_off"]):
                dflt = np3[tid][TR][k]
                diffs = {"lm": r["lm_pair"][k],
                         "nudge": float(np.max(np.abs(fr(st[tid]["nudge"][0]) - fr(dflt)))) if ok(st[tid]["nudge"][0]) else float("inf")}
                for K in (3, 5, 10):
                    b = r["bestK"][K]
                    diffs[f"s{K}"] = float(np.max(np.abs(fr(b) - fr(dflt)))) if b is not None else float("inf")
                if o > thr:
                    offn += 1
                    for key, v in diffs.items():
                        hit[key] += v > thr
                else:
                    okn += 1
                    for key, v in diffs.items():
                        fa[key] += v > thr
        keys = ("lm", "nudge", "s3", "s5", "s10")
        P(f"| {lab} | {offn} | " + " | ".join(f"{hit[k]} ({100*hit[k]/max(offn,1):.0f} %)" for k in keys) + " | "
          + " | ".join(f"{fa[k]} of {okn} ({100*fa[k]/max(okn,1):.1f} %)" for k in keys) + " |")
    P("")
    P("A scatter 'false alarm' needs care: the best of K scattered starts differing from a default that is within 5 pp of the "
      "reference means the scattered fit found a WORSE-or-equal χ²ᵣ solution elsewhere, or a better one that is the new reference.\n")
    P("## 3. Starting on a bound\n")
    moved = [r for r in rows if r["nudge_moved"] > 0]
    P(f"Targets whose request starts a freely varying shape parameter within 1 % of a bound: **{len(moved)}** of {n} "
      f"({sum(r['kind']=='batch' for r in moved)} not-yet-fitted, {sum(r['kind']=='own' for r in moved)} re-fits).")
    bad = [r for r in rows if max(r["default_off"]) > 5]
    P(f"Of the {len(bad)} targets where the default is ever > 5 pp off, {sum(r['nudge_moved']>0 for r in bad)} start on a bound; "
      f"of the {n-len(bad)} others, {sum(r['nudge_moved']>0 for r in rows if r not in bad)} do.\n")
    P(f"Cost: 10 scattered Trust-Region fits took a median {np.median([r['seconds'] for r in rows]):.1f} s per target "
      f"(90th percentile {np.percentile([r['seconds'] for r in rows], 90):.1f} s, max {max(r['seconds'] for r in rows):.1f} s).\n")
    P("## 4. The targets where the default is ever > 5 pp off\n")
    P("| project | tab | start | default χ²ᵣ (5 repeats) | nudge χ²ᵣ | scatter-10 best χ²ᵣ | reference χ²ᵣ | scatter-10 best off (pp) |\n|---|---|---|---|---:|---:|---:|---:|")
    for r in bad:
        tid = r["id"]; b = r["bestK"][10]
        pool_ref = min([x for x in ([*np0[tid].values()] + [y for m in np3[tid].values() for y in m.values()] + [y for v in st[tid].values() for y in v.values()]) if ok(x)], key=lambda x: x["chi2r"])
        P(f"| {r['t']['project'][:16]} | {r['t']['tab']} | {r['kind']} | {', '.join(f'{c:.1f}' for c in r['default_chi'])} | "
          f"{st[tid]['nudge'][0].get('chi2r', float('nan')):.2f} | {b['chi2r'] if b else float('nan'):.2f} | {pool_ref['chi2r']:.2f} | {r['off_fn'](b) if b else float('nan'):.1f} |")
    text = "\n".join(out) + "\n"
    if md_out:
        Path(md_out).write_text(text)
    print(text)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(Path(a[0]), a[a.index("--md") + 1] if "--md" in a else None)
