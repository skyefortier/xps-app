#!/usr/bin/env python3
"""Analyse the n_perturb=3 correction run (what the page's Run Fit actually
sends) against the n_perturb=0 run, and measure what a Trust-Region /
Levenberg-Marquardt cross-check would and would not catch.

Reference solution for a target = the lowest reduced chi-square seen in ANY
run of that target (n_perturb=0: Trust-Region, LM, basin-hopping;
n_perturb=3: five repeats each of Trust-Region and LM). It is the best known
solution, not ground truth.

Usage: python scripts/optimizer_disagreement_analyze_perturb.py <dir> [--md out.md]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

CHI_TOL = 1e-3
TR, LM = "least_squares", "leastsq"


def fractions(rec):
    a = np.array([max(float(p.get("area") or 0.0), 0.0) for p in rec["peaks"]])
    return 100 * a / a.sum() if a.sum() > 0 else a


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * (c - h), 100 * (c + h))


def usable(r):
    return r is not None and "error" not in r and r.get("chi2r") is not None and r.get("peaks")


def main(d: Path, md_out):
    targets = {t["id"]: t for t in json.loads((d / "targets.json").read_text())}
    np0 = defaultdict(dict)
    for f in [d / "results.jsonl"]:
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                np0[r["id"]][r["method"]] = r
    np3 = defaultdict(lambda: defaultdict(dict))
    for f in sorted(d.glob("results_perturb3*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                np3[r["id"]][r["method"]][r["rep"]] = r

    rows = []
    for tid, t in targets.items():
        reps = sorted(set(np3[tid][TR]) & set(np3[tid][LM]))
        if not reps or not all(usable(np0[tid].get(m)) for m in (TR, LM, "basinhopping")):
            continue
        pool = [np0[tid][m] for m in (TR, LM, "basinhopping")]
        pool += [np3[tid][m][k] for m in (TR, LM) for k in reps if usable(np3[tid][m][k])]
        ref = min(pool, key=lambda r: float(r["chi2r"]))
        ref_chi, ref_fr = float(ref["chi2r"]), fractions(ref)

        def off(rec):
            """(relative chi2r excess over the reference, max fraction difference in pp, accepted?)"""
            if not usable(rec):
                return (float("inf"), float("inf"), False)
            return (float(rec["chi2r"]) / ref_chi - 1, float(np.max(np.abs(fractions(rec) - ref_fr))), bool(rec.get("success")))

        row = dict(id=tid, project=t["project"], tab=t["tab"], kind=t["kind"], region=t["region"], n_peaks=len(t["specs"]),
                   tr0=off(np0[tid][TR]), tr3=[off(np3[tid][TR][k]) for k in reps], lm3=[off(np3[tid][LM][k]) for k in reps],
                   pair=[])
        for k in reps:
            a, b = np3[tid][TR][k], np3[tid][LM][k]
            if usable(a) and usable(b):
                row["pair"].append(float(np.max(np.abs(fractions(a) - fractions(b)))))
            else:
                row["pair"].append(float("inf"))
        rows.append(row)

    n = len(rows)
    out = []
    P = out.append
    P("# Optimiser disagreement — correction: the shipped request (n_perturb = 3)\n")
    P(f"Targets analysed: **{n}** (own-model re-fits {sum(r['kind']=='own' for r in rows)}, not-yet-fitted starts "
      f"{sum(r['kind']=='batch' for r in rows)}); Trust-Region and LM each run 5 times with the page's `n_perturb: 3` "
      f"(random, unseeded). Reference = lowest χ²ᵣ seen in any run of the target (best known, not ground truth).\n")

    P("## 1. The UI default, as shipped, versus the earlier n_perturb = 0 measurement\n")
    P("Share of Run Fit outcomes (Trust-Region) whose area fractions are further than the threshold from the reference. "
      "For n_perturb = 3 the rate is averaged over the 5 repeats; 'ever' = in at least one repeat, 'always' = in all five.\n")
    P("| start | threshold | n_perturb=0 | n_perturb=3 (mean of repeats) | ever (of 5) | always (of 5) |\n|---|---|---:|---:|---:|---:|")
    for kind, lab in ((None, "all"), ("own", "saved-solution re-fit"), ("batch", "not-yet-fitted start")):
        sub = [r for r in rows if kind is None or r["kind"] == kind]
        for thr in (1.0, 5.0):
            k0 = sum(r["tr0"][1] > thr for r in sub)
            mean3 = np.mean([np.mean([o[1] > thr for o in r["tr3"]]) for r in sub]) * 100
            ever = sum(any(o[1] > thr for o in r["tr3"]) for r in sub)
            always = sum(all(o[1] > thr for o in r["tr3"]) for r in sub)
            lo, hi = wilson(ever, len(sub))
            P(f"| {lab} (n={len(sub)}) | > {thr:g} pp | {k0} ({100*k0/len(sub):.1f} %) | {mean3:.1f} % | "
              f"{ever} ({100*ever/len(sub):.1f} %, Wilson {lo:.1f}–{hi:.1f}) | {always} ({100*always/len(sub):.1f} %) |")
    P("")
    P("Same, by reduced chi-square (default's χ²ᵣ above the reference by more than 1 %):\n")
    P("| start | n_perturb=0 | n_perturb=3 (mean of repeats) | ever | always |\n|---|---:|---:|---:|---:|")
    for kind, lab in ((None, "all"), ("own", "saved-solution re-fit"), ("batch", "not-yet-fitted start")):
        sub = [r for r in rows if kind is None or r["kind"] == kind]
        k0 = sum(r["tr0"][0] > 0.01 for r in sub)
        mean3 = np.mean([np.mean([o[0] > 0.01 for o in r["tr3"]]) for r in sub]) * 100
        ever = sum(any(o[0] > 0.01 for o in r["tr3"]) for r in sub)
        always = sum(all(o[0] > 0.01 for o in r["tr3"]) for r in sub)
        P(f"| {lab} (n={len(sub)}) | {k0} ({100*k0/len(sub):.1f} %) | {mean3:.1f} % | {ever} ({100*ever/len(sub):.1f} %) | {always} ({100*always/len(sub):.1f} %) |")
    P("")
    nondet = [r for r in rows if max(o[1] for o in r["tr3"] if np.isfinite(o[1])) - min(o[1] for o in r["tr3"] if np.isfinite(o[1])) > 1.0]
    P(f"Run Fit is not repeatable on **{len(nondet)}** of {n} targets ({100*len(nondet)/n:.1f} %): the five Trust-Region repeats of the "
      f"identical request differ from each other by more than 1 pp of area fraction, because the perturbation is random.\n")
    P(f"Levenberg-Marquardt with n_perturb = 3: success=false in {sum(not o[2] for r in rows for o in r['lm3'])} of "
      f"{sum(len(r['lm3']) for r in rows)} runs; Trust-Region: {sum(not o[2] for r in rows for o in r['tr3'])} of {sum(len(r['tr3']) for r in rows)}.\n")

    P("## 2. What a Trust-Region / LM cross-check would catch (both as shipped, n_perturb = 3)\n")
    P("Each of the 5 repeats pairs one Trust-Region run with one LM run of the same request. 'Flag' = the two differ by more than "
      "the threshold in area fraction (or LM did not converge). 'Default is off' = the Trust-Region result is further than the same "
      "threshold from the reference.\n")
    P("| start | threshold | pairs | default off | of those, flagged (sensitivity) | default fine | of those, flagged (false-alarm rate) | flagged overall |\n|---|---|---:|---:|---:|---:|---:|---:|")
    for kind, lab in ((None, "all"), ("own", "saved-solution re-fit"), ("batch", "not-yet-fitted start"), ("multi", "not-yet-fitted, ≥ 2 peaks")):
        if kind == "multi":
            sub = [r for r in rows if r["kind"] == "batch" and r["n_peaks"] >= 2]
        else:
            sub = [r for r in rows if kind is None or r["kind"] == kind]
        for thr in (1.0, 5.0):
            off_n = off_flag = ok_n = ok_flag = 0
            for r in sub:
                for o, l, p in zip(r["tr3"], r["lm3"], r["pair"]):
                    flagged = p > thr or not l[2]
                    if o[1] > thr:
                        off_n += 1
                        off_flag += flagged
                    else:
                        ok_n += 1
                        ok_flag += flagged
            tot = off_n + ok_n
            P(f"| {lab} | > {thr:g} pp | {tot} | {off_n} | {off_flag} ({100*off_flag/max(off_n,1):.0f} %) | {ok_n} | "
              f"{ok_flag} ({100*ok_flag/max(ok_n,1):.1f} %) | {off_flag+ok_flag} ({100*(off_flag+ok_flag)/max(tot,1):.1f} %) |")
    P("")
    P("When the pair disagrees by more than 1 pp, which of the two has the lower χ²ᵣ (ties within 1e-3 relative):\n")
    tr_b = lm_b = tie = 0
    for r in rows:
        for o, l, p in zip(r["tr3"], r["lm3"], r["pair"]):
            if p > 1.0 and np.isfinite(p):
                if abs(o[0] - l[0]) <= CHI_TOL:
                    tie += 1
                elif o[0] < l[0]:
                    tr_b += 1
                else:
                    lm_b += 1
    P(f"Trust-Region better {tr_b}, LM better {lm_b}, tie {tie}.\n")
    P("After taking the better of the pair (the proposed behaviour), how often is the REPORTED fit still off the reference:\n")
    P("| start | threshold | reported fit off (mean of repeats) | of those, the pair had flagged |\n|---|---|---:|---:|")
    for kind, lab in ((None, "all"), ("own", "saved-solution re-fit"), ("batch", "not-yet-fitted start")):
        sub = [r for r in rows if kind is None or r["kind"] == kind]
        for thr in (1.0, 5.0):
            off_n = flagged_n = tot = 0
            for r in sub:
                for o, l, p in zip(r["tr3"], r["lm3"], r["pair"]):
                    cand = [c for c in (o, l) if c[2]] or [o]
                    best = min(cand, key=lambda c: c[0])
                    tot += 1
                    if best[1] > thr:
                        off_n += 1
                        flagged_n += (p > thr or not l[2])
            P(f"| {lab} | > {thr:g} pp | {off_n} of {tot} ({100*off_n/max(tot,1):.1f} %) | {flagged_n} ({100*flagged_n/max(off_n,1):.0f} %) |")
    P("")
    P("## 3. Targets where the shipped default is ever more than 5 pp from the reference\n")
    P("| project | tab | start | peaks | repeats off (of 5) | worst pp | n_perturb=0 pp |\n|---|---|---|---:|---:|---:|---:|")
    for r in sorted(rows, key=lambda r: -max(o[1] for o in r["tr3"] if np.isfinite(o[1]))):
        k = sum(o[1] > 5 for o in r["tr3"])
        if k:
            P(f"| {r['project'][:30]} | {r['tab']} | {r['kind']} | {r['n_peaks']} | {k} | "
              f"{max(o[1] for o in r['tr3'] if np.isfinite(o[1])):.1f} | {r['tr0'][1]:.1f} |")
    text = "\n".join(out) + "\n"
    if md_out:
        Path(md_out).write_text(text)
    print(text)


if __name__ == "__main__":
    a = sys.argv[1:]
    md = a[a.index("--md") + 1] if "--md" in a else None
    main(Path(a[0]), md)
