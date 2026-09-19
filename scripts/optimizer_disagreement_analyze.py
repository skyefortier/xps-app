#!/usr/bin/env python3
"""Analyse the optimiser-disagreement run: how often do Trust-Region (the UI
default), Levenberg-Marquardt and basin-hopping disagree from the same start,
how often is the default the worst, how large is the area/fraction spread,
and does anything VISIBLE IN ADVANCE predict it?

Usage: python scripts/optimizer_disagreement_analyze.py <dir with targets.json + results*.jsonl> [--md out.md]
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

METHODS = ("least_squares", "leastsq", "basinhopping")
LABEL = {"least_squares": "Trust-Region (UI default)", "leastsq": "Levenberg-Marquardt", "basinhopping": "basin-hopping"}
CHI_TOL = 1e-3      # relative chi2r difference counted as "beyond numerical noise"
FRAC_TOL = 0.5      # percentage points of area fraction


def load(d: Path):
    targets = {t["id"]: t for t in json.loads((d / "targets.json").read_text())}
    res = defaultdict(dict)
    # n_perturb=0 run only; results_perturb3*.jsonl belongs to optimizer_disagreement_analyze_perturb.py
    for f in sorted([*d.glob("results.jsonl"), *d.glob("results.shard*.jsonl")]):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                res[r["id"]][r["method"]] = r
    return targets, res


def fractions(rec):
    a = np.array([max(float(p.get("area") or 0.0), 0.0) for p in rec["peaks"]])
    return a, (100 * a / a.sum() if a.sum() > 0 else a)


def predictors(t):
    specs = t["specs"]
    free = [s for s in specs if not s.get("constrain_to")]
    centers = sorted((s["center"], s["fwhm"]) for s in specs)
    gaps = [(centers[i + 1][0] - centers[i][0]) / (0.5 * (centers[i + 1][1] + centers[i][1])) for i in range(len(centers) - 1)]
    amps = [s["amplitude"] for s in specs if s["amplitude"] > 0]
    inten = np.asarray(t["inten"], float)
    return {
        "n_peaks": len(specs),
        "n_points": len(inten),
        "min_gap_over_fwhm": min(gaps) if gaps else float("inf"),
        "weakest_amp_ratio": (min(amps) / max(amps)) if amps else 1.0,
        "max_counts": float(inten.max()),
        "has_voigt": float(any(s == "Voigt" for s in t["shapes"])),
        "has_lacx": float(any(s == "LACX" for s in t["shapes"])),
        "is_batch_start": float(t["kind"] == "batch"),
        "n_unlinked": len(free),
    }


def auc(pos, neg):
    """P(predictor of a disagreeing target > predictor of an agreeing one); 0.5 = useless."""
    if not pos or not neg:
        return float("nan")
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(gt / (len(pos) * len(neg)))


def main(d: Path, md_out: Path | None):
    targets, res = load(d)
    rows = []
    errors = Counter()
    for tid, t in targets.items():
        r = res.get(tid, {})
        if any(m not in r for m in METHODS):
            continue
        for m in METHODS:
            if "error" in r[m]:
                errors[(m, r[m]["error"][:60])] += 1
        if any("error" in r[m] or r[m].get("chi2r") is None for m in METHODS):
            continue
        chi = {m: float(r[m]["chi2r"]) for m in METHODS}
        best = min(chi.values())
        excess = {m: chi[m] / best - 1 for m in METHODS}
        fr = {m: fractions(r[m])[1] for m in METHODS}
        ar = {m: fractions(r[m])[0] for m in METHODS}
        dfrac = max(float(np.max(np.abs(fr[a] - fr[b]))) for a in METHODS for b in METHODS)
        big = np.max(np.vstack([fr[m] for m in METHODS]), axis=0) >= 1.0       # components holding >= 1 % somewhere
        darea = 0.0
        for a in METHODS:
            for b in METHODS:
                denom = 0.5 * (ar[a] + ar[b])
                rel = np.where((denom > 0) & big, np.abs(ar[a] - ar[b]) / np.where(denom > 0, denom, 1), 0.0)
                darea = max(darea, float(rel.max()) * 100)
        vanished = any(float(p.get("amplitude", 1.0)) <= 1e-6 * max(float(q.get("amplitude", 1.0)) for q in r[min(chi, key=chi.get)]["peaks"])
                       for p in r[min(chi, key=chi.get)]["peaks"])
        b = min(chi, key=chi.get)
        d_default = float(np.max(np.abs(fr["least_squares"] - fr[b])))          # what the UI default is off by, vs the best of the three
        raw_key = hash((tuple(np.round(t["inten"][:40], 3)), len(t["inten"])))
        rows.append(dict(id=tid, project=t["project"], tab=t["tab"], kind=t["kind"], region=t["region"], chi=chi, excess=excess,
                         d_default=d_default, raw_key=raw_key, messages={m: r[m].get("message") for m in METHODS},
                         chi_spread=max(chi.values()) / best - 1, dfrac=dfrac, darea=darea,
                         success={m: bool(r[m].get("success")) for m in METHODS},
                         worst=max(chi, key=chi.get), best=min(chi, key=chi.get), vanished_in_best=vanished, pred=predictors(t)))
    n = len(rows)
    disagree = [x for x in rows if x["chi_spread"] > CHI_TOL or x["dfrac"] > FRAC_TOL]
    default_not_best = [x for x in rows if x["excess"]["least_squares"] > CHI_TOL]
    default_worst = [x for x in default_not_best if x["worst"] == "least_squares"]
    out = []
    P = out.append
    P(f"# Optimiser disagreement — frequency measurement\n")
    P(f"Targets with all three methods completed: **{n}** of {len(targets)} "
      f"(own-model starts {sum(x['kind']=='own' for x in rows)}, batch starts {sum(x['kind']=='batch' for x in rows)}).\n")
    P(f"Disagreement criterion: χ²ᵣ spread > {CHI_TOL:g} (relative) OR area-fraction difference > {FRAC_TOL} pp.\n")
    P("## 1. How often\n")
    P("| | count | share |\n|---|---:|---:|")
    P(f"| the three methods disagree | {len(disagree)} | {100*len(disagree)/max(n,1):.1f} % |")
    P(f"| the UI default (Trust-Region) is NOT the best (χ²ᵣ > best by > {CHI_TOL:g}) | {len(default_not_best)} | {100*len(default_not_best)/max(n,1):.1f} % |")
    P(f"| the UI default is the WORST of the three | {len(default_worst)} | {100*len(default_worst)/max(n,1):.1f} % |")
    for m in METHODS:
        P(f"| {LABEL[m]} not the best | {sum(x['excess'][m] > CHI_TOL for x in rows)} | {100*sum(x['excess'][m] > CHI_TOL for x in rows)/max(n,1):.1f} % |")
    P(f"| any method reports success=false | {sum(not all(x['success'].values()) for x in rows)} | |")
    P("\nThreshold ladder (share of targets disagreeing):\n\n| fraction tolerance | " + " | ".join(f"{v} pp" for v in (0.1, 0.5, 1, 5, 10)) + " |\n|---|" + "---:|" * 5)
    P("| targets | " + " | ".join(f"{sum(x['dfrac'] > v for x in rows)} ({100*sum(x['dfrac'] > v for x in rows)/max(n,1):.1f} %)" for v in (0.1, 0.5, 1, 5, 10)) + " |")
    P("\nBy kind of start and region:\n\n| group | targets | disagree | default not best | default worst |\n|---|---:|---:|---:|---:|")
    for key in sorted({(x["kind"], x["region"]) for x in rows}):
        g = [x for x in rows if (x["kind"], x["region"]) == key]
        P(f"| {key[0]} / {key[1]} | {len(g)} | {sum(x in disagree for x in g)} | {sum(x in default_not_best for x in g)} | {sum(x in default_worst for x in g)} |")
    P("\n## 2. How large, when they disagree\n")
    if disagree:
        df = np.array([x["dfrac"] for x in disagree]); da = np.array([x["darea"] for x in disagree]); cs = np.array([x["chi_spread"] for x in disagree]) * 100
        P("| among disagreeing targets | median | 90th pct | max |\n|---|---:|---:|---:|")
        P(f"| area-fraction spread (pp) | {np.median(df):.2f} | {np.percentile(df,90):.2f} | {df.max():.2f} |")
        P(f"| component-area spread, components ≥ 1 % (%) | {np.median(da):.1f} | {np.percentile(da,90):.1f} | {da.max():.1f} |")
        P(f"| χ²ᵣ spread (%) | {np.median(cs):.2f} | {np.percentile(cs,90):.2f} | {cs.max():.2f} |")
        P(f"\nIn {sum(x['vanished_in_best'] for x in disagree)} of {len(disagree)} disagreeing targets the BEST solution drives a component to zero amplitude "
          f"(vs {sum(x['vanished_in_best'] for x in rows if x not in disagree)} of {n-len(disagree)} agreeing targets).\n")
    P("## 3. Is it predictable in advance?\n")
    P("AUC = probability that the predictor is larger for a disagreeing target than for an agreeing one (0.5 = no information; computed from the START model and the data only).\n")
    P("| predictor (known before fitting) | median, disagree | median, agree | AUC |\n|---|---:|---:|---:|")
    agree = [x for x in rows if x not in disagree]
    for k in rows[0]["pred"] if rows else []:
        a = [x["pred"][k] for x in disagree]; b = [x["pred"][k] for x in agree]
        P(f"| {k} | {np.median(a) if a else float('nan'):.3g} | {np.median(b) if b else float('nan'):.3g} | {auc(a, b):.2f} |")
    P("\n## 3b. What the UI default costs a student (Trust-Region's answer vs the best of the three)\n")
    P("| start | targets | default's fractions off by > 1 pp | > 5 pp | > 10 pp | default χ²ᵣ worse than best by > 1 % | > 10 % |\n|---|---:|---:|---:|---:|---:|---:|")
    for kind in ("own", "batch", None):
        g = [x for x in rows if kind is None or x["kind"] == kind]
        P(f"| {kind or 'all'} | {len(g)} | " + " | ".join(f"{sum(x['d_default'] > v for x in g)} ({100*sum(x['d_default'] > v for x in g)/max(len(g),1):.1f} %)" for v in (1, 5, 10))
          + " | " + " | ".join(f"{sum(x['excess']['least_squares'] > v for x in g)} ({100*sum(x['excess']['least_squares'] > v for x in g)/max(len(g),1):.1f} %)" for v in (0.01, 0.10)) + " |")
    P("\nIndependence caveat: " + f"{len({x['raw_key'] for x in rows})} distinct spectra across {len({x['project'] for x in rows})} projects (several projects share raw spectra with different models, and scans within a project are repeats of one sample).\n")
    P("| project | targets | disagree | default not best | default off by > 5 pp |\n|---|---:|---:|---:|---:|")
    for pr in sorted({x["project"] for x in rows}):
        g = [x for x in rows if x["project"] == pr]
        P(f"| {pr[:44]} | {len(g)} | {sum(x in disagree for x in g)} | {sum(x in default_not_best for x in g)} | {sum(x['d_default'] > 5 for x in g)} |")
    P("\n## 3c. Simple advance rules (target = fraction spread > 1 pp between methods)\n")
    material = [x for x in rows if x["dfrac"] > 1.0]
    P(f"Materially disagreeing targets: {len(material)} of {n}.\n\n| rule (from the START model only) | flagged | recall | precision |\n|---|---:|---:|---:|")
    rules = {
        "n_peaks >= 5": lambda q: q["n_peaks"] >= 5,
        "min gap/FWHM < 0.5 (overlap)": lambda q: q["min_gap_over_fwhm"] < 0.5,
        "weakest/strongest amplitude < 0.05": lambda q: q["weakest_amp_ratio"] < 0.05,
        "n_peaks >= 5 AND overlap < 0.5": lambda q: q["n_peaks"] >= 5 and q["min_gap_over_fwhm"] < 0.5,
        "n_peaks >= 4 OR overlap < 0.5": lambda q: q["n_peaks"] >= 4 or q["min_gap_over_fwhm"] < 0.5,
        "n_peaks >= 3": lambda q: q["n_peaks"] >= 3,
    }
    for name, fn in rules.items():
        fl = [x for x in rows if fn(x["pred"])]
        hit = [x for x in fl if x in material]
        P(f"| {name} | {len(fl)} ({100*len(fl)/n:.0f} %) | {100*len(hit)/max(len(material),1):.0f} % | {100*len(hit)/max(len(fl),1):.0f} % |")
    fails = [(x["project"][:24], x["tab"], x["kind"], m, x["messages"][m]) for x in rows for m in METHODS if not x["success"][m]]
    if fails:
        P("\nsuccess=false cases:\n"); [P(f"- {f[0]} {f[1]} ({f[2]}): {LABEL[f[3]]} — {str(f[4])[:90]}") for f in fails]
    P("\n## 4. Worst cases\n\n| project | tab | start | χ²ᵣ TR | χ²ᵣ LM | χ²ᵣ BH | fraction spread (pp) | best |\n|---|---|---|---:|---:|---:|---:|---|")
    for x in sorted(disagree, key=lambda x: -x["dfrac"])[:15]:
        P(f"| {x['project'][:24]} | {x['tab']} | {x['kind']} | {x['chi']['least_squares']:.3f} | {x['chi']['leastsq']:.3f} | {x['chi']['basinhopping']:.3f} | {x['dfrac']:.1f} | {LABEL[x['best']].split(' (')[0]} |")
    if errors:
        P("\n## Errors\n"); [P(f"- {m}: {e} ×{c}") for (m, e), c in errors.items()]
    text = "\n".join(out)
    print(text)
    if md_out:
        md_out.write_text(text + "\n")
    (d / "summary.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    d = Path(sys.argv[1]); md = Path(sys.argv[sys.argv.index("--md") + 1]) if "--md" in sys.argv else None
    main(d, md)
