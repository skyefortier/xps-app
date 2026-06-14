"""
Phase 1 transcriber. Wraps the verbatim legacy dump (.stage9/legacy_raw.json,
produced by extract_legacy.mjs evaling the real JS literals) into two faithful
legacy JSON documents under data/xps/legacy/.

Faithfulness rules:
- Energies (be_ev), state labels, refs, names: VERBATIM from the dump.
- transition_type: photoelectron unless the orbital label is an Auger term
  (first char not a digit, e.g. 'KLL'); Auger BE kept VERBATIM as a legacy
  marker position (NOT converted to kinetic energy).
- z (atomic number): definitional periodic-table metadata, not a measured
  value — added so the unified accessor can place elements; flagged as such.
- Every record tagged source 'legacy-embedded-dataset', tier
  'legacy-unverified'. No NIST values merged here (that is the curated set).
"""
import hashlib
import json
from pathlib import Path

RAW = json.load(open(".stage9/legacy_raw.json"))
OUT = Path("data/xps/legacy")


# Canonical reconstructions + checksum (must match xps_reference.py exactly,
# so the loader can verify the frozen legacy data is untampered at load time).
def _canon_survey(elements):
    return {el["symbol"]: {"lines": {ln["orbital"]: ln["be_ev"] for ln in el["lines"]}}
            for el in elements}


def _canon_chem(groups):
    return {g["orbital_key"]: [{"state": s["state"], "be": s["be_ev"], "ref": s["ref"]}
                              for s in g["states"]] for g in groups}


def _checksum(canonical):
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()

# Definitional symbol -> Z (periodic table; not a measured quantity).
PT = ("H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co "
      "Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb "
      "Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os "
      "Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm "
      "Md No Lr").split()
Z = {sym: i + 1 for i, sym in enumerate(PT)}


def is_auger(orbital):
    return not orbital[0].isdigit()


# ── survey-lines.json ──────────────────────────────────────────────────────
survey_elements = []
for sym, data in RAW["XPS_ELEMENTS"].items():
    lines = []
    for orbital, be in data["lines"].items():
        auger = is_auger(orbital)
        lines.append({
            "id": f"legacy-{sym}-{orbital}",
            "orbital": orbital,
            "transition_type": "auger" if auger else "photoelectron",
            "be_ev": be,
            "be_basis": "legacy-marker-position",
            "source": "legacy-embedded-dataset",
            "tier": "legacy-unverified",
        })
    survey_elements.append({
        "symbol": sym,
        "z": Z[sym],
        "z_basis": "definitional",
        "name": RAW["ELEMENT_NAMES"].get(sym, sym),
        "lines": lines,
    })

survey_doc = {
    "schema_version": 1,
    "file_id": "legacy-survey-lines",
    "source": "legacy-embedded-dataset",
    "curation_status": "legacy-unverified",
    "provenance": "Verbatim transcription of the XPS_ELEMENTS constant embedded in "
                  "templates/index.html (rounded single-value survey-marker positions, "
                  "unsourced in origin). Auger (KLL) lines kept as legacy BE marker "
                  "positions, not converted to kinetic energy.",
    "content_sha256": _checksum(_canon_survey(survey_elements)),
    "elements": survey_elements,
}

# ── chemical-states.json ───────────────────────────────────────────────────
cs_groups = []
for key, states in RAW["CHEMICAL_STATES"].items():
    elem, orbital = key.split(" ", 1)
    cs_groups.append({
        "orbital_key": key,
        "element": elem,
        "z": Z[elem],
        "z_basis": "definitional",
        "orbital": orbital,
        "states": [{
            "id": f"legacy-cs-{elem}-{orbital.replace('/', '')}-{i}",
            "state": s["state"],
            "be_ev": s["be"],
            "ref": s["ref"],
            "source": "legacy-embedded-dataset",
            "tier": "legacy-unverified",
        } for i, s in enumerate(states)],
    })

cs_doc = {
    "schema_version": 1,
    "file_id": "legacy-chemical-states",
    "source": "legacy-embedded-dataset",
    "curation_status": "legacy-unverified",
    "provenance": "Verbatim transcription of the CHEMICAL_STATES constant embedded in "
                  "templates/index.html (NIST-modal chemical-state table). The 'ref' "
                  "strings are the legacy editorial citations, kept as-is.",
    "content_sha256": _checksum(_canon_chem(cs_groups)),
    "groups": cs_groups,
}

OUT.mkdir(parents=True, exist_ok=True)
json.dump(survey_doc, open(OUT / "survey-lines.json", "w"), indent=2, ensure_ascii=False)
(OUT / "survey-lines.json").write_text(
    json.dumps(survey_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "chemical-states.json").write_text(
    json.dumps(cs_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("survey elements:", len(survey_elements),
      "lines:", sum(len(e["lines"]) for e in survey_elements))
print("cs groups:", len(cs_groups),
      "states:", sum(len(g["states"]) for g in cs_groups))
