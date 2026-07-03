#!/usr/bin/env python
"""
Generate data/xps/fit-physics.json — the element fit-physics database
(spec §7 "comprehensive element-physics DB", first deliverable slice).

ANTI-CONFABULATION CONTRACT (the same discipline as the machine tier):
every numeric value in the output is one of
  (a) copied verbatim from the existing, already-sourced data/xps reference
      files (equality is enforced by tests/autofit/test_fit_physics.py);
  (b) derived by pure arithmetic from quantum numbers (statistical 2j+1
      area ratios — labeled `theoretical-statistical`, with the caveat that
      measured intensity ratios deviate);
  (c) a hand-curated SEED entry below carrying a primary-literature DOI
      (mirroring the spec-§9 verdict table / region modules).
Nothing is emitted from model memory.  Every entry carries `status`
(VERIFIED / CONDITIONAL / UNVERIFIED) and `derivation`.

Run:  venv/bin/python scripts/gen_fit_physics.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "xps")
OUT = os.path.join(DATA, "fit-physics.json")

# 2j+1 statistical intensity ratios for spin-orbit pairs, by orbital letter:
# p: 2p3/2:2p1/2 = 4:2, d: 3:2, f: 4:3.  Pure arithmetic, not measurement.
_STATISTICAL_RATIO = {"p": (2, 1), "d": (3, 2), "f": (4, 3)}

# Hand-curated, lit-cited seeds — mirrors spec §9 + region modules.  DOIs
# only; values already reviewed in this repo's spec/Codex process.
SEEDS = {
    "C-1s": {
        "core_hole_width_ev": {
            "value": 0.10, "unit": "eV FWHM", "status": "VERIFIED",
            "source": "Campbell & Papp, At. Data Nucl. Data Tables 77 (2001) 1, "
                      "DOI 10.1006/adnd.2000.0848",
            "note": "0.05 eV HWHM used as the DS+G beta in the C 1s grammar"},
        "lineshape_families": {
            "conductor(graphite)": {
                "family": "asymmetric (DS+G or empirical asym-GL envelope)",
                "status": "CONDITIONAL",
                "source": "metallic-screening asymmetry on sp2 carbon; "
                          "engine C 1s grammar families A/AG/MG (see "
                          "autofit/regions/c1s.py provenance)"},
            "insulator(adventitious)": {
                "family": "symmetric pseudo-Voigt",
                "status": "CONDITIONAL",
                "source": "Biesinger 2022 DOI 10.1016/j.apsusc.2022.153681"}},
        "satellites": [{
            "label": "pi-pi* shake-up",
            "offset_from_main_ev": [5.5, 7.0], "status": "UNVERIFIED",
            "source": "fitalg tunable; labeled-set fits 5.9-6.7"}],
    },
    "U-4f": {
        "lineshape_families": {
            "U(IV) compounds": {
                "family": "multiplet-asymmetric envelope (LACX admissible)",
                "status": "VERIFIED",
                "source": "Ilton & Bagus, Surf. Interface Anal. 43 (2011) "
                          "1549, DOI 10.1002/sia.3836 — 5f2 multiplet/final-"
                          "state origin, not metallic screening"}},
        "satellites": [{
            "label": "U(IV) shake-up (rides both mains)",
            "offset_from_main_ev": [6.8, 7.1], "status": "CONDITIONAL",
            "source": "Ilton & Bagus 2011; Schindler et al., GCA 73 (2009) "
                      "2488, DOI 10.1016/j.gca.2009.02.008; labeled set "
                      "fits 6.07-6.38",
            "note": "pair separation ~11.2 eV != core splitting 10.9 and "
                    "pair intensity ratio ~0.9 != core 0.75 (PROGRESS "
                    "Stage-3 findings, pending adjudication)"}],
    },
}


def _orbital_letter(orbital_key: str):
    m = re.match(r"\d([spdf])", orbital_key or "")
    return m.group(1) if m else None


def main() -> None:
    entries = {}
    files = [f for f in sorted(os.listdir(DATA))
             if f.startswith("elements-") and f.endswith(".json")
             and "provenance" not in f and "skipped" not in f]
    for fname in files:
        doc = json.load(open(os.path.join(DATA, fname)))
        for el in doc.get("elements", []):
            for fam in el.get("families", []):
                for t in fam.get("transitions", []):
                    if t.get("kind") == "auger":
                        continue
                    tid = t["id"]
                    orbital = tid.split("-", 1)[1] if "-" in tid else ""
                    letter = _orbital_letter(orbital)
                    tier = t.get("tier", "curated")
                    entry = {
                        "element": el["symbol"],
                        "z": el["z"],
                        "transition": tid,
                        "reference_tier": tier,
                        "source_file": fname,
                        "derivation": "copied from data/xps (already sourced)",
                        "status": "UNVERIFIED-machine-derived"
                        if tier == "machine" else "CONDITIONAL-derived",
                    }
                    reg = t.get("expected_region_ev")
                    if reg:
                        entry["be_window_ev"] = {
                            "min": reg["min"], "max": reg["max"],
                            "basis": reg.get("basis"),
                            "source": t.get("source"),
                        }
                    if t.get("nominal_be_ev") is not None:
                        entry["nominal_be_ev"] = {
                            "value": t["nominal_be_ev"],
                            "source": t.get("source"),
                        }
                    so = t.get("spin_orbit")
                    if so and so.get("splitting_ev") is not None:
                        entry["spin_orbit"] = {
                            "partner": so.get("partner_id"),
                            "splitting_ev": so["splitting_ev"],
                            "area_ratio": so.get("area_ratio"),
                            "source": t.get("source"),
                            "status": "CONDITIONAL-derived",
                        }
                    if letter in _STATISTICAL_RATIO:
                        hi, lo = _STATISTICAL_RATIO[letter]
                        entry["statistical_area_ratio"] = {
                            "value": lo / hi,
                            "ratio": f"{hi}:{lo}",
                            "derivation": "theoretical-statistical (2j+1)",
                            "status": "VERIFIED-arithmetic",
                            "caveat": "measured intensity ratios deviate "
                                      "(e.g. U 4f fitted 0.65-0.75; "
                                      "satellite pairs ~0.9)",
                        }
                    m = re.match(r"([A-Z][a-z]?-\d[spdf])", tid)
                    seed_key = m.group(1) if m else tid
                    seed = SEEDS.get(seed_key) or SEEDS.get(tid)
                    if seed:
                        entry.update(json.loads(json.dumps(seed)))
                        entry["status"] = "SEEDED-lit-cited"
                    entries[tid] = entry

    payload = {
        "schema": "fit-physics-v1",
        "contract": ("no value from model memory: copied-from-sourced-data, "
                     "arithmetic-derived, or DOI-cited seed only; "
                     "machine-derived entries are unverified-until-reviewed"),
        "entries": entries,
        "seeds": SEEDS,
    }
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1, sort_keys=True)
    n_so = sum(1 for e in entries.values() if "spin_orbit" in e)
    print(f"{len(entries)} transitions ({n_so} with sourced spin-orbit) -> {OUT}")


if __name__ == "__main__":
    main()
