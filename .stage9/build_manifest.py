"""
Stage 9 Phase 3 — verification manifest.

Enumerates EVERY in-scope field across the migrated dataset (53 legacy
elements + the 6 curated elements that overlap them), classified BY FIELD
TYPE, because each type carries a different evidence policy (per the Stage 9
plan):

  quantitative-energy   nominal BE / Auger KE / chemical-state E / splitting
                        -> dual-extract from authoritative sources (Phase 4)
  area-ratio            spin-orbit intensity ratio
                        -> physics-derived (degeneracy) OR source; validate vs basis
  expected-region       orientation band
                        -> CURATED SUMMARY over many observations, NOT a single value
  visibility            major/moderate/weak
                        -> EDITORIAL classification, carry from source, do NOT "verify"
  rsf                   relative sensitivity factor
                        -> OUT OF SCOPE here (SCOFIELD_RSF is a separate constant,
                           not part of the XPS_ELEMENTS/CHEMICAL_STATES migration)

Each field records the context needed for Phase-5 equivalence matching
(element / orbital / reference-state / calibration-convention / photon-source
/ energy-type). Legacy reference-state is 'unspecified' (the rounded legacy
values are unsourced — we do not know which material/state they represent),
which is itself load-bearing: a legacy value can only reach a corroborated
tier if an authoritative observation matches its (necessarily loose) context.

Output: .stage9/manifest/manifest.json  + a printed summary.
This builds the WORK-LIST for extraction; it does not extract anything.
"""
import json
from collections import Counter
from pathlib import Path

ROOT = Path("data/xps")
OUT = Path(".stage9/manifest")
OUT.mkdir(parents=True, exist_ok=True)

legacy_survey = json.load(open(ROOT / "legacy/survey-lines.json"))["elements"]
legacy_chem = json.load(open(ROOT / "legacy/chemical-states.json"))["groups"]
curated = []
for f in ("elements-main.json", "elements-actinides.json"):
    curated += json.load(open(ROOT / f))["elements"]
auger = json.load(open(ROOT / "auger-lines.json"))["elements"]

fields = []


def add(**f):
    f["field_id"] = f"f{len(fields):04d}"
    fields.append(f)


# ── Legacy survey lines: quantitative energies, dual-extract ────────────────
for el in legacy_survey:
    for ln in el["lines"]:
        add(kind="legacy-survey-line", field_type="quantitative-energy",
            evidence_policy="dual-extract-authoritative",
            element=el["symbol"], z=el["z"],
            context={"orbital": ln["orbital"], "transition_type": ln["transition_type"],
                     "reference_state": "unspecified",
                     "calibration_convention": "unspecified",
                     "photon_source": "unspecified",
                     "energy_type": "binding-energy-marker"
                     if ln["transition_type"] == "photoelectron"
                     else "legacy-auger-be-marker"},
            current_value=ln["be_ev"], current_tier="legacy-unverified",
            current_source="legacy-embedded-dataset", record_id=ln["id"])

# ── Legacy chemical states: quantitative energies, dual-extract ─────────────
for g in legacy_chem:
    for s in g["states"]:
        add(kind="legacy-chemical-state", field_type="quantitative-energy",
            evidence_policy="dual-extract-authoritative",
            element=g["element"], z=g["z"],
            context={"orbital": g["orbital"], "transition_type": "photoelectron",
                     "reference_state": s["state"], "calibration_convention": "unspecified",
                     "photon_source": "unspecified", "energy_type": "binding-energy-chemical-state"},
            current_value=s["be_ev"], current_tier="legacy-unverified",
            current_source="legacy-embedded-dataset",
            legacy_ref=s["ref"], record_id=s["id"])

# ── Curated transitions (already hand-verified in Stages 2/7) ───────────────
for el in curated + auger:
    for fam in el["families"]:
        for t in fam["transitions"]:
            is_auger = t["transition_type"] == "auger"
            energy = t.get("nominal_be_ev", t.get("auger_ke_ev"))
            add(kind="curated-transition", field_type="quantitative-energy",
                evidence_policy="dual-extract-authoritative",
                element=t["element"], z=t["z"],
                context={"orbital": t["orbital"], "transition_type": t["transition_type"],
                         "reference_state": "elemental-nominal",
                         "calibration_convention": "corrected-BE-frame",
                         "photon_source": "source-invariant",
                         "energy_type": "auger-kinetic-energy" if is_auger else "binding-energy-nominal"},
                current_value=energy, current_tier="curated-hand-verified",
                current_source=t["source"], record_id=t["id"])
            so = t.get("spin_orbit")
            if so:
                add(kind="curated-splitting", field_type="quantitative-energy",
                    evidence_policy="dual-extract-authoritative",
                    element=t["element"], z=t["z"],
                    context={"orbital": t["orbital"], "partner": so["partner_id"],
                             "energy_type": "spin-orbit-splitting"},
                    current_value=so["splitting_ev"], current_tier="curated-hand-verified",
                    current_source=t["source"], record_id=t["id"] + ":splitting")
                add(kind="curated-area-ratio", field_type="area-ratio",
                    evidence_policy="physics-derived-degeneracy-validate",
                    element=t["element"], z=t["z"],
                    context={"orbital": t["orbital"], "partner": so["partner_id"],
                             "basis": "2j+1 degeneracy"},
                    current_value=so["area_ratio"], current_tier="physics-derived",
                    current_source=t["source"], record_id=t["id"] + ":area_ratio")
            reg = t["expected_region_ev"]
            add(kind="curated-expected-region", field_type="expected-region",
                evidence_policy="curated-summary-multi-observation",
                element=t["element"], z=t["z"],
                context={"orbital": t["orbital"], "basis": reg["basis"]},
                current_value=[reg["min"], reg["max"]], current_tier="curated-summary",
                current_source=t["source"], record_id=t["id"] + ":region")
            for src_label, vis in t["visibility"].items():
                add(kind="curated-visibility", field_type="visibility",
                    evidence_policy="editorial-carry-no-verify",
                    element=t["element"], z=t["z"],
                    context={"orbital": t["orbital"], "source_label": src_label},
                    current_value=vis, current_tier="editorial",
                    current_source=t["source"], record_id=t["id"] + ":vis:" + src_label)

manifest = {
    "schema_version": 1,
    "purpose": "Stage 9 Phase 3 verification manifest — work-list for extraction. "
               "Field types carry different evidence policies; quantitative energies "
               "are dual-extracted, visibility is editorial, regions are curated summaries, "
               "area ratios are physics-derived.",
    "out_of_scope": {
        "rsf": "SCOFIELD_RSF is a separate constant NOT part of the XPS_ELEMENTS / "
               "CHEMICAL_STATES migration; its per-element RSF values are not enumerated "
               "or re-verified here. Flagged so the omission is explicit, not silent."
    },
    "counts_by_field_type": dict(Counter(f["field_type"] for f in fields)),
    "counts_by_kind": dict(Counter(f["kind"] for f in fields)),
    "counts_by_policy": dict(Counter(f["evidence_policy"] for f in fields)),
    "extraction_targets": sum(1 for f in fields
                              if f["evidence_policy"] == "dual-extract-authoritative"),
    "fields": fields,
}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

print("TOTAL FIELDS:", len(fields))
print("\nby field_type:")
for k, v in sorted(manifest["counts_by_field_type"].items()):
    print(f"  {k:24s} {v}")
print("\nby evidence_policy:")
for k, v in sorted(manifest["counts_by_policy"].items()):
    print(f"  {k:38s} {v}")
print("\nby kind:")
for k, v in sorted(manifest["counts_by_kind"].items()):
    print(f"  {k:28s} {v}")
print(f"\nExtraction targets (dual-extract quantitative energies): {manifest['extraction_targets']}")
print("RSF: OUT OF SCOPE (SCOFIELD_RSF not part of this migration).")
