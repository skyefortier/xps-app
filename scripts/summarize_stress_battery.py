#!/usr/bin/env python
"""
Summarize docs/autofit/inventory/stress_battery_runs.jsonl into
docs/autofit/stress-test-report.md.

Pure reporting — no fits are run; the JSONL is the evidence of record.

Outcome classification (encoded here so the report can never drift from
its own rules):

- recover-class cases:  PASS = the method picks the true structure with
  every truth center matched within 0.15 eV; PASS_FLAGGED if it does so on
  the conditional tier / with warnings; FAIL otherwise.
- ambiguous-class cases (data constructed NOT to distinguish): outcomes are
  classed, not pass/failed — `simpler_model` (parsimony choice),
  `flagged_true` (true structure + machine-readable ambiguity signal),
  `confident_true` (true structure, NO signal — evidence the case is
  actually distinguishable: RELABEL candidate), `confident_wrong`
  (non-true, non-simpler structure with no signal — the real failure mode).
- prune-class: PASS = true structure wins and nothing extra is emitted.
- honesty-class (truth outside the model space): PASS = the mismatch is
  machine-visible (conditional tier, χ²ᵣ > 3, autocorrelation flag,
  residual flags, or proposal activity); FAIL = clean confident result.
"""
import json
import os
import sys
from collections import defaultdict

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "tests", "autofit"))
SRC = os.path.join(REPO, "docs", "autofit", "inventory",
                   "stress_battery_runs.jsonl")
OUT = os.path.join(REPO, "docs", "autofit", "stress-test-report.md")

CENTER_TOL = 0.15
# a filtered candidate whose BIC* beats the winner's by more than this is
# a BURIED DOMINANT ALTERNATIVE (same decisive threshold as the engine's
# override rule, Kass & Raftery 1995)
DECISIVE_DBIC = 10.0


def _library_expectations():
    """The case LIBRARY is the single source of truth for expectation
    labels (Codex stress review blocker: records carry generation-time
    labels, which go stale when measurement arbitrates a relabel)."""
    from stress_cases import build_all_cases
    return {c.name: c.expectation for c in build_all_cases()}


def _load():
    with open(SRC) as f:
        recs = [json.loads(l) for l in f]
    lib = _library_expectations()
    for r in recs:
        gen_label = r.get("expectation")
        lib_label = lib.get(r["case"], gen_label)
        r["expectation"] = lib_label
        r["_label_drift"] = (gen_label != lib_label and
                             f"generated under {gen_label!r}") or None
    return recs


def _centers_ok(rec):
    tm = rec.get("truth_match") or []
    return tm and all(m and m.get("d_center_ev") is not None
                      and abs(m["d_center_ev"]) <= CENTER_TOL for m in tm)


def _ambiguity_signal(rec):
    sig = []
    if rec.get("conditional"):
        sig.append(f"conditional:{rec.get('conditional_reason')}")
    if rec.get("ambiguous_pairs"):
        sig.append("ambiguous_pairs")
    if rec.get("selection_warning"):
        sig.append("selection_warning")
    if rec.get("filtered_dominant_alternative"):
        # the result-level burial flag (engine change driven by finding 0)
        fda = rec["filtered_dominant_alternative"]
        sig.append(f"filtered_dominant_alternative:{fda.get('name')}"
                   f"+{fda.get('delta_bic_vs_winner', 0):.0f}")
    return sig


def _honesty_signal(rec):
    sig = list(_ambiguity_signal(rec))
    chi = rec.get("winner_chi_reduced") or rec.get("chi_reduced")
    if chi is not None and chi > 3.0:
        sig.append(f"chi2r={chi:.1f}")
    if rec.get("winner_autocorr_flag"):
        sig.append("autocorr")
    if rec.get("winner_residual_flags"):
        sig.append("residual_flags")
    if rec.get("accepted_proposals"):
        sig.append("proposals")
    return sig


def _buried_dominant(rec):
    """A filtered candidate whose BIC* decisively beats the winner's, with
    no result-level warning — the laundering hole both Codex runs flagged:
    such a record must NEVER be classified as honest parsimony."""
    cands = rec.get("candidates") or []
    win = next((c for c in cands if c.get("name") == rec.get("winner")), None)
    if win is None or win.get("bic_star") is None:
        return None
    best_filtered = min(
        (c for c in cands
         if c.get("filter_reason") and c.get("bic_star") is not None),
        key=lambda c: c["bic_star"], default=None)
    if best_filtered is None:
        return None
    margin = win["bic_star"] - best_filtered["bic_star"]
    if margin > DECISIVE_DBIC and not _ambiguity_signal(rec):
        return {"name": best_filtered["name"], "dbic": round(margin, 1)}
    return None


def classify(rec):
    if not rec.get("success"):
        return "ERROR" if rec.get("error") else "no_survivor"
    exp = rec["expectation"]
    method = rec["method"]

    if method == "least_squares":
        # true-structure baseline: report recovery quality only
        return "baseline_ok" if _centers_ok(rec) else "baseline_biased"

    if method == "sparse_map":
        # count AND positions must both hold for a PASS (Codex blocker:
        # count-only let 0.7 eV position errors pass as recovery)
        k_ok = rec.get("n_selected") == rec["truth_n"]
        if exp in ("recover", "prune"):
            if k_ok and _centers_ok(rec):
                return "PASS"
            if k_ok:
                return "count_ok_param_biased"
            return f"wrong_k={rec.get('n_selected')}"
        return f"k={rec.get('n_selected')}" + \
            ("" if not k_ok or _centers_ok(rec) else "(param_biased)")

    picked_true = bool(rec.get("winner_is_true"))
    signals = _ambiguity_signal(rec)
    emitted = rec.get("n_emitted_components")

    # evidence burial dominates every other reading for IC records
    if method == "ic_model_comparison":
        buried = _buried_dominant(rec)
        if buried and not picked_true:
            return (f"buried_dominant_alternative(FAIL:"
                    f"{buried['name']}+{buried['dbic']})")

    if exp == "recover":
        if picked_true and _centers_ok(rec):
            return "PASS_FLAGGED" if signals else "PASS"
        return f"FAIL(winner={rec.get('winner')})"
    if exp == "ambiguous":
        if picked_true:
            return "flagged_true" if (signals or rec.get("selection_warning")) \
                else "confident_true(RELABEL?)"
        if emitted is not None and emitted < rec["truth_n"]:
            return "simpler_model" if not signals else "flagged_simpler"
        if emitted is not None and emitted > rec["truth_n"] and not signals:
            return f"overclaim(winner={rec.get('winner')})"
        return f"confident_wrong(winner={rec.get('winner')})" if not signals \
            else "flagged_other"
    if exp == "prune":
        if picked_true and emitted == rec["truth_n"]:
            return "PASS_FLAGGED" if signals else "PASS"
        return f"FAIL(winner={rec.get('winner')},k={emitted})"
    if exp == "honesty":
        sig = _honesty_signal(rec)
        return f"PASS({','.join(sig)})" if sig else "FAIL(silent_clean)"
    return "unclassified"


def main():
    recs = _load()
    lines = [
        "# Synthetic hard-case stress battery — report",
        "",
        "*Generated by scripts/summarize_stress_battery.py from "
        "docs/autofit/inventory/stress_battery_runs.jsonl — do not "
        "hand-edit; re-run the script.  Classification rules are encoded in "
        "the generator's docstring/source.*",
        "",
        f"Records: {len(recs)}.  Cases: tests/autofit/stress_cases.py "
        "(parameter-level truth, seeded Poisson noise; noise-draw replicates "
        "at seed offsets 0/1000/2000 for LS/IC/sparse, base draw for the "
        "Bayesian method).  Always-on invariant net: "
        "tests/autofit/test_stress_honesty.py.",
        "",
    ]

    lines += [
        "## Key findings (curated; every claim is in the JSONL)",
        "",
        "0. **HEADLINE — filter-then-rank can bury DECISIVE evidence with "
        "no result-level trace.** Three measured instances: "
        "(a) `overlap_sep0.4_h9000` — P2 beats P1 by ΔBIC* 74–97 on EVERY "
        "noise draw and is stable (persistence 0.92–1.0), yet is "
        "plausibility-filtered (orphan matching) every time; clean P1 wins "
        "with `conditional=False`. (b) `overlap_sep0.7_h9000` offset 2000 — "
        "stable P2 (pers 0.83) orphan-filtered; clean P1 wins at "
        "ΔBIC* +944. (c) `charging_with_replica_candidate` offset 0 — the "
        "true candidate pegs `replica:center@max`, the decisive-override "
        "bound-fix does not promote it, and clean `single_main` wins at "
        "ΔBIC* +801. In all three the dominant alternative is visible only "
        "in `analysis.candidates`; nothing at the RESULT level warns. "
        "Recommendation for the criteria/stability unit: a result-level "
        "`filtered_dominant_alternative` flag whenever a filtered "
        "candidate's BIC* beats the winner's by more than the decisive "
        "threshold, plus orphan-tolerant role matching for heavily-"
        "overlapped windows. (Contrast: `overlap_sep0.4_h900` is GENUINE "
        "parsimony — P1 wins the evidence by ΔBIC* 5–12 on every draw.)",
        "1. **Multi-start depth matters on razor-sharp surfaces**: "
        "`overlap_sep0.7_h9000` offset 0 — IC at n_refits=4 lands in a "
        "wrong basin (winner P2+bfix, χ²ᵣ 5.06, max|Δc| 0.37 eV) while "
        "n_refits=12 recovers cleanly (P2, χ²ᵣ 1.58, 0.04 eV). The engine "
        "already reports `best_minimum_basin_support`; nothing consumes "
        "it yet.",
        "2. **Endpoint-anchored linear background + Lorentzian tails set a "
        "χ²ᵣ floor that GROWS with count rate** (systematic ∝ height, noise "
        "∝ √height): at the TRUE parameters, χ²ᵣ = 0.96 under the true "
        "baseline vs ≈34 under the engine's endpoint-anchored line at "
        "height 90000 (measured 1.19 vs 3.07 at height 9000; best fits "
        "land below the truth-under-wrong-background score by bending "
        "parameters to compensate). Deliberate design property of the "
        "suite (documented in stress_cases.py) — quantified evidence that "
        "absolute χ²-target criteria are miscalibrated whenever background "
        "subtraction is imperfect; the engine's iterative Shirley absorbs "
        "the same integral background well (control case χ²ᵣ 1.24). Feeds "
        "the noise-model work item.",
        "3. **The Bayesian noise model dominated its behavior**: the "
        "first battery ran it UNWEIGHTED (its homoscedastic default) and "
        "it confidently overfit P3 with no warning on three recover-class "
        "cases. Under the Poisson weights the suite's construction makes "
        "correct (this battery), two of those become TRUE picks "
        "(`sep0.7`→P2, `weak_minor_h90000`→P2+warn) and every remaining "
        "P3 pick carries a selection warning (`bg_mismatch`, "
        "`overspecified` flanking case; the in-ROI decoy is picked "
        "correctly). Quantified evidence that the noise model — not the "
        "evidence machinery — was the misdirection; feeds the noise-model "
        "work item. Cross-method note: on the buried sub-FWHM@9000 case "
        "the Bayesian evidence prefers P1 while IC's BIC* decisively "
        "prefers the (filtered) P2 — the two selection criteria "
        "legitimately disagree there (prior-volume penalty vs BIC "
        "approximation); neither result-level output mentions the other "
        "reading.",
        "4. **Sparse over-splits under atom/shape mismatch**: Gaussian "
        "atoms on 30%-Lorentzian truth select k>truth on most regimes "
        "(k=3–4 on sub-FWHM overlap and over-specified menus); the count "
        "is reliable only on separated, near-Gaussian cases — its "
        "documented regime, now quantified.",
        "5. **Sub-FWHM at LOW counts is genuine, silent parsimony**: on "
        "`overlap_sep0.4_h900` P1 legitimately wins the evidence "
        "(ΔBIC* 5–12 over P2, every draw) — an honest simpler-model "
        "choice, but still with no result-level marker that a 2-component "
        "reading is nearly as good; the trace lives in the candidate "
        "table. Pinned honest-trace test: "
        "test_subfwhm_alternative_never_silently_lost. (The HIGH-count "
        "sub-FWHM case turned out to be evidence burial — finding 0.)",
        "6. **A-priori expectation labels were arbitrated by measurement** "
        "(in both directions): `weak_minor_0.03_h2000` ambiguous→recover "
        "(IC recovers on every draw; Bayes concurs with an honest budget "
        "warning; the minor's center wobbles ±0.16 eV, one draw exceeding "
        "the 0.15 eV PASS tolerance — reported as-is). "
        "`overlap_sep0.4_h9000` ambiguous→recover (the evidence "
        "decisively distinguishes; the pipeline currently fails it — "
        "finding 0). The current battery was REGENERATED under the "
        "corrected library labels (the superseded first generation lives "
        "in git history); the summarizer reads labels from the library at "
        "report time and annotates any future generation-label drift per "
        "row.",
        "8. **In-ROI decoy prune robustness is noise-draw-dependent**: the "
        "decoy 'shoulder' case is pruned correctly on 2 of 3 noise draws "
        "(P2 clean — χ²ᵣ 1.10 on the base draw, 2.23 at offset 1000) and "
        "by the weighted Bayesian on the base draw — but at seed offset "
        "2000 BOTH IC depths promote the "
        "bound-fixed decoy candidate via the decisive-override path "
        "(winner P3_decoy+bfix, k=3, conditional=True): flagged, but "
        "structurally an INVENTED component on truth-2 data. The "
        "always-on pin covers the base draw only. Criteria-calibration "
        "material (the override's interior-optimum requirement admits a "
        "populated decoy on some draws).",
        "7. **LS true-structure baseline**: excellent on separated truth "
        "(|Δc| ≤ 0.01 eV) but drifts 0.2+ eV on sub-FWHM doublets even "
        "GIVEN the true structure — position uncertainty there is "
        "intrinsic, not a selection artifact.",
        "",
    ]

    by_case = defaultdict(list)
    for r in recs:
        by_case[(r["regime"], r["case"])].append(r)

    lines += ["## Per-case outcomes", ""]
    cur_regime = None
    for (regime, case), rows in sorted(by_case.items()):
        if regime != cur_regime:
            lines += [f"### {regime}", ""]
            cur_regime = regime
        exp = rows[0]["expectation"]
        lines += [f"**{case}** (expect: {exp}; {rows[0].get('notes', '')})",
                  "", "| method | config | offset | outcome | winner/k | χ²ᵣ | max|Δc| (eV) | t(s) |",
                  "|---|---|---|---|---|---|---|---|"]
        for r in sorted(rows, key=lambda r: (r["method"],
                                             json.dumps(r.get("config"), sort_keys=True),
                                             r["seed_offset"])):
            tm = [m for m in (r.get("truth_match") or []) if m]
            maxdc = max((abs(m["d_center_ev"]) for m in tm
                         if m.get("d_center_ev") is not None), default=None)
            chi = r.get("winner_chi_reduced") or r.get("chi_reduced")
            win = r.get("winner") or (f"k={r['n_selected']}"
                                      if r.get("n_selected") is not None else "—")
            cfg = ",".join(f"{k}={v}" for k, v in (r.get("config") or {}).items()
                           if k not in ("rng_seed",))
            drift = f" ⚠{r['_label_drift']}" if r.get("_label_drift") else ""
            lines.append(
                f"| {r['method']} | {cfg or '—'} | {r['seed_offset']} | "
                f"{classify(r)}{drift} | {win} | "
                f"{f'{chi:.2f}' if chi is not None else '—'} | "
                f"{f'{maxdc:.3f}' if maxdc is not None else '—'} | "
                f"{r.get('runtime_s', 0):.0f} |")
        lines.append("")

    # winner-stability across noise draws (IC only) — framing is
    # EXPECTATION-AWARE (Codex re-check blocker: a prune failure must not
    # be laundered as "ambiguity evidence")
    lines += ["## Winner stability across noise draws (IC)", ""]
    flips = []
    exp_by_case = {r["case"]: r["expectation"] for r in recs}
    ic = defaultdict(set)
    for r in recs:
        if r["method"] == "ic_model_comparison" and r.get("success"):
            ic[(r["case"], json.dumps(r.get("config"), sort_keys=True))].add(
                r.get("winner"))
    for (case, cfg), winners in sorted(ic.items()):
        if len(winners) > 1:
            exp = exp_by_case.get(case)
            verdict = ("instability = ambiguity evidence" if exp == "ambiguous"
                       else f"{exp} FAILS on some noise draws — "
                            "robustness deficiency, not ambiguity")
            flips.append(f"- `{case}` {cfg} (expect: {exp}): winners flip "
                         f"across noise draws: {sorted(winners)} — {verdict}")
    lines += flips or ["- none: every IC (case, config) picked the same "
                       "winner on all noise draws"]
    lines.append("")
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT} ({len(recs)} records)")


if __name__ == "__main__":
    main()
