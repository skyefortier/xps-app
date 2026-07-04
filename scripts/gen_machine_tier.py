#!/usr/bin/env python3
"""Phase B machine-tier generator.

Emits the machine-source-corroborated reference tier deterministically from the
Stage-9 dual-extraction provenance, under HARD no-invention rules:

  * A transition is eligible only if its Stage-9 tier is
    `transcription-corroborated` (both independent extractions agreed) AND it is
    not already curated AND not conflict/insufficient.
  * The emitted nominal is the NIST-EVALUATED (starred) value recovered from the
    primary archived element-page HTML (.stage9/extract_claude/<El>_nist.html) —
    the only artifact that reliably marks the recommended value — and is emitted
    ONLY if that value is also present in the dual-corroborated agreed-set
    (tiers_survey.agreed_values). Rule 2 (median of context-equivalent records)
    is fully disabled: material/chemical-state class is not recoverable from the
    archived pages, so non-starred transitions are skip-logged, never promoted.
  * expected_region_ev = {min(agreed), max(agreed), observed-reference-range} —
    the one allowed derivation; spans chemical states by design (schema basis).
  * spin_orbit is always null (no fabricated splittings).

Outputs (all committed; deterministic — re-run produces byte-identical files):
  data/xps/elements-machine.json             the served machine tier
  data/xps/elements-machine.provenance.json  per-value source locator + sha256 of
                                              the artifact parsed + parse method,
                                              so every machine value is verifiable
                                              from committed data even though the
                                              raw .stage9 inputs stay gitignored
  data/xps/elements-machine.skipped.json     every non-emitted transition + reason

Inputs are gitignored Stage-9 working data; this script + its three committed
outputs are the provenance of record.
"""
import hashlib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DATA = os.path.join(REPO, "data", "xps")
STAGE9 = os.path.join(REPO, ".stage9")     # gitignored working provenance (inputs)
GENERATOR_REL = "scripts/gen_machine_tier.py"

SOURCE_ID = "nist-srd-20"

# Conflict-resolution allowlist: metal/oxide (or elemental/compound) conflicts that
# are promoted out of the skipped "conflict" bucket into the machine tier as a
# reduced/elemental nominal with a band spanning reduced -> oxidized. Each entry is
# self-validating: the generator HARD-FAILS (raise) unless, for that transition,
#   (a) a NIST-evaluated (starred) value exists in source and equals expected_nominal
#       within +/-0.1 eV (no star -> fail; this is the "V-safety" guard), and
#   (b) the legacy value equals expected_oxidized within +/-0.5 eV, and
#   (c) expected_nominal < expected_oxidized.
# The hardcoded energies are VALIDATION ONLY — the emitted nominal is the starred
# value read from source. V 2p3/2 is deliberately absent (no starred value); the two
# Auger KLL conflicts are absent (frame mismatch, not a chemical-state span).
CONFLICT_RESOLUTIONS = {
    ("Ti", "2p3/2"): {"expected_nominal": 453.98, "expected_oxidized": 459, "reduced_state": "metal",     "oxidized_state": "oxide",     "nist_ref": "Powe95"},
    ("Cr", "2p3/2"): {"expected_nominal": 574.35, "expected_oxidized": 577, "reduced_state": "metal",     "oxidized_state": "oxide",     "nist_ref": "Powe95"},
    ("Fe", "2p3/2"): {"expected_nominal": 706.86, "expected_oxidized": 711, "reduced_state": "metal",     "oxidized_state": "oxide",     "nist_ref": "Powe95"},
    ("P",  "2p3/2"): {"expected_nominal": 130.01, "expected_oxidized": 133, "reduced_state": "elemental", "oxidized_state": "phosphate", "nist_ref": "Powe95"},
}

GEN_NOTE = ("Machine-source tier: NIST-evaluated reference energy recovered by "
            "dual extraction (Claude + Codex) from NIST SRD 20 element-page "
            "snapshots and corroborated; NOT human-verified. Spin-orbit partners "
            "and chemical-state assignments are not curated. "
            "See elements-machine.provenance.json.")

# ── Coverage-expansion elements (additive; do NOT alter the existing tiers path) ──
# Symbol -> (Z, name). Z/name are DEFINITIONAL periodic-table facts, not measured
# data — the no-invention rule governs emitted binding energies, every one of which
# is read from a fetched NIST artifact in .stage9/expand_artifacts/. Elements that
# fetch an artifact but carry no NIST-evaluated value (e.g. Rb, Cs) are skip-logged,
# never invented. Originally the 12-element EXPAND_ELEMENTS set; broadened to the
# full periodic table for the fit-physics coverage work (acquisition by the
# committed scripts/acquire_nist_archive.py; elements never acquired or with no
# starred value simply skip-log).
PERIODIC_TABLE = {
    "H": (1, "Hydrogen"), "He": (2, "Helium"), "Li": (3, "Lithium"),
    "Be": (4, "Beryllium"), "B": (5, "Boron"), "C": (6, "Carbon"),
    "N": (7, "Nitrogen"), "O": (8, "Oxygen"), "F": (9, "Fluorine"),
    "Ne": (10, "Neon"), "Na": (11, "Sodium"), "Mg": (12, "Magnesium"),
    "Al": (13, "Aluminium"), "Si": (14, "Silicon"), "P": (15, "Phosphorus"),
    "S": (16, "Sulfur"), "Cl": (17, "Chlorine"), "Ar": (18, "Argon"),
    "K": (19, "Potassium"), "Ca": (20, "Calcium"), "Sc": (21, "Scandium"),
    "Ti": (22, "Titanium"), "V": (23, "Vanadium"), "Cr": (24, "Chromium"),
    "Mn": (25, "Manganese"), "Fe": (26, "Iron"), "Co": (27, "Cobalt"),
    "Ni": (28, "Nickel"), "Cu": (29, "Copper"), "Zn": (30, "Zinc"),
    "Ga": (31, "Gallium"), "Ge": (32, "Germanium"), "As": (33, "Arsenic"),
    "Se": (34, "Selenium"), "Br": (35, "Bromine"), "Kr": (36, "Krypton"),
    "Rb": (37, "Rubidium"), "Sr": (38, "Strontium"), "Y": (39, "Yttrium"),
    "Zr": (40, "Zirconium"), "Nb": (41, "Niobium"), "Mo": (42, "Molybdenum"),
    "Tc": (43, "Technetium"), "Ru": (44, "Ruthenium"), "Rh": (45, "Rhodium"),
    "Pd": (46, "Palladium"), "Ag": (47, "Silver"), "Cd": (48, "Cadmium"),
    "In": (49, "Indium"), "Sn": (50, "Tin"), "Sb": (51, "Antimony"),
    "Te": (52, "Tellurium"), "I": (53, "Iodine"), "Xe": (54, "Xenon"),
    "Cs": (55, "Caesium"), "Ba": (56, "Barium"), "La": (57, "Lanthanum"),
    "Ce": (58, "Cerium"), "Pr": (59, "Praseodymium"), "Nd": (60, "Neodymium"),
    "Pm": (61, "Promethium"), "Sm": (62, "Samarium"), "Eu": (63, "Europium"),
    "Gd": (64, "Gadolinium"), "Tb": (65, "Terbium"), "Dy": (66, "Dysprosium"),
    "Ho": (67, "Holmium"), "Er": (68, "Erbium"), "Tm": (69, "Thulium"),
    "Yb": (70, "Ytterbium"), "Lu": (71, "Lutetium"), "Hf": (72, "Hafnium"),
    "Ta": (73, "Tantalum"), "W": (74, "Tungsten"), "Re": (75, "Rhenium"),
    "Os": (76, "Osmium"), "Ir": (77, "Iridium"), "Pt": (78, "Platinum"),
    "Au": (79, "Gold"), "Hg": (80, "Mercury"), "Tl": (81, "Thallium"),
    "Pb": (82, "Lead"), "Bi": (83, "Bismuth"), "Po": (84, "Polonium"),
    "At": (85, "Astatine"), "Rn": (86, "Radon"), "Fr": (87, "Francium"),
    "Ra": (88, "Radium"), "Ac": (89, "Actinium"), "Th": (90, "Thorium"),
    "Pa": (91, "Protactinium"), "U": (92, "Uranium"), "Np": (93, "Neptunium"),
    "Pu": (94, "Plutonium"), "Am": (95, "Americium"), "Cm": (96, "Curium"),
    "Bk": (97, "Berkelium"), "Cf": (98, "Californium"), "Es": (99, "Einsteinium"),
    "Fm": (100, "Fermium"), "Md": (101, "Mendelevium"), "No": (102, "Nobelium"),
    "Lr": (103, "Lawrencium"),
}
EXPAND_PE_LINE = re.compile(r"^[1-7][spdf]([1357]/2)?$")   # PE subshell only (exclude DS-*/Auger)
EXPAND_NOTE = ("Machine-source tier (coverage expansion): NIST-evaluated reference energy recovered "
               "from a single archived NIST SRD 20 element-page snapshot, parsed by the committed "
               "parser and cross-checked by an independent agent re-derivation; NOT human-verified. "
               "Spin-orbit partners and chemical-state assignments are not curated. "
               "See elements-machine.provenance.json.")
EXPAND_DIR = os.path.join(STAGE9, "expand_artifacts")


def load(p):
    with open(p) as f:
        return json.load(f)


def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def parse_nist_html(path):
    """Parse a NIST SRD-20 element-page snapshot into per-record dicts.

    Each data row is four TD cells headers t1..t4 (element, spectral line,
    energy, reference); an evaluated/recommended record carries `<b>*</b>` before
    the reference code in the t4 cell.
    """
    html = open(path, encoding="utf-8", errors="replace").read()
    recs, cur = [], {}
    for m in re.finditer(r'headers="(t[1-4])"[^>]*>(.*?)</TD>', html, re.S | re.I):
        slot = m.group(1).lower()
        text = re.sub(r"<[^>]+>", "", m.group(2)).replace("&nbsp;", " ").strip()
        if slot == "t2":
            cur = {"orbital": text}
        elif slot == "t3":
            cur["energy_text"] = text
        elif slot == "t4":
            cur["evaluated"] = "*" in text
            cur["ref"] = text.lstrip("*").strip()
            try:
                cur["energy"] = float(cur.get("energy_text", ""))
            except ValueError:
                cur = {}
                continue
            if cur.get("orbital") and "energy" in cur:
                recs.append(cur)
            cur = {}
    return recs


def digest_recoverable(obs4a, obs4b, ref, val):
    """True if the (value, ref) evaluated record is also present in the 4a/4b
    digests (i.e. not HTML-only). 4b caps at 20 records and 4a is sometimes
    truncated, so late-listed evaluated records (Ag, Pt) are HTML-only."""
    for v in (obs4b.get("values") or []):
        if re.sub(r"[^A-Za-z0-9]", "", v.get("nist_ref", "")) == ref and abs(v["be_ev"] - val) < 1e-6:
            return True
    ev = obs4a.get("evidence", "") or ""
    for m in re.finditer(r"([0-9]+(?:\.[0-9]+)?)\s*\|?\s*\*?\s*([A-Za-z][A-Za-z0-9]*)", ev):
        if m.group(2) == ref and abs(float(m.group(1)) - val) < 1e-6:
            return True
    return False


def subshell(orbital):
    m = re.match(r"^([1-7][spdf])", orbital)
    return m.group(1) if m else orbital


def build():
    """Assemble the three documents deterministically (no file writes)."""
    tiers = load(os.path.join(STAGE9, "manifest", "tiers_survey.json"))
    obs4a = {o["field_id"]: o for o in load(os.path.join(STAGE9, "extract_claude", "observations_4a.json"))["observations"]}
    obs4b = {o["field_id"]: o for o in load(os.path.join(STAGE9, "extract_codex", "observations_4b.json"))["observations"]}

    # Names + Z + already-curated set from COMMITTED data (not the gitignored digests).
    legacy = load(os.path.join(DATA, "legacy", "survey-lines.json"))
    info = {el["symbol"]: (el["z"], el["name"]) for el in legacy["elements"]}
    curated = set()
    for fn in ("elements-main.json", "elements-actinides.json",
               "elements-lanthanides.json", "auger-lines.json"):
        for el in load(os.path.join(DATA, fn))["elements"]:
            for fam in el["families"]:
                for t in fam["transitions"]:
                    curated.add((el["symbol"], t["orbital"]))

    def legacy_be(sym, orbital):
        """Legacy survey value for sym's matching subshell (bare-orbital marker)."""
        for el in legacy["elements"]:
            if el["symbol"] != sym:
                continue
            for ln in el["lines"]:
                if ln["orbital"] == orbital or subshell(ln["orbital"]) == subshell(orbital):
                    return ln["be_ev"]
        return None

    emitted, skipped, prov = [], [], []

    for r in tiers:
        fid = r["field_id"]
        el = r["element"]
        o = obs4a.get(fid, {})
        line = o.get("nist_line")
        tier = r["tier"]
        rec = {"element": el, "orbital": line, "field_id": fid}

        if tier != "transcription-corroborated":
            key = (el, line)
            if tier == "conflict" and key in CONFLICT_RESOLUTIONS:
                res = CONFLICT_RESOLUTIONS[key]
                html_path = os.path.join(STAGE9, "extract_claude", f"{el}_nist.html")
                if not os.path.exists(html_path):
                    raise SystemExit(f"conflict-resolution {el} {line}: source artifact {el}_nist.html missing")
                recs = parse_nist_html(html_path)
                starred = [x for x in recs if x["orbital"] == line and x["evaluated"]]
                # GUARD (a) — V-safety: a NIST-evaluated (starred) value must exist and match.
                if not starred:
                    raise SystemExit(f"conflict-resolution guard (a) FAILED for {el} {line}: no NIST-evaluated (starred) value in source")
                sval, sref = starred[0]["energy"], starred[0]["ref"]
                if abs(sval - res["expected_nominal"]) > 0.1:
                    raise SystemExit(f"conflict-resolution guard (a) FAILED for {el} {line}: starred {sval} != expected_nominal {res['expected_nominal']} (>0.1 eV)")
                if sref != res["nist_ref"]:
                    raise SystemExit(f"conflict-resolution guard (a) FAILED for {el} {line}: starred ref {sref} != expected nist_ref {res['nist_ref']}")
                agreed = r["agreed_values"]
                if not any(abs(sval - a) < 1e-6 for a in agreed):
                    raise SystemExit(f"conflict-resolution {el} {line}: starred {sval} not in dual-corroborated agreed-set")
                # GUARD (b) — legacy value is the oxidized reference.
                leg = legacy_be(el, line)
                if leg is None:
                    raise SystemExit(f"conflict-resolution {el} {line}: no legacy value found")
                if abs(leg - res["expected_oxidized"]) > 0.5:
                    raise SystemExit(f"conflict-resolution guard (b) FAILED for {el} {line}: legacy {leg} != expected_oxidized {res['expected_oxidized']} (>0.5 eV)")
                # GUARD (c) — reduced below oxidized.
                if not (res["expected_nominal"] < res["expected_oxidized"]):
                    raise SystemExit(f"conflict-resolution guard (c) FAILED for {el} {line}: expected_nominal {res['expected_nominal']} not < expected_oxidized {res['expected_oxidized']}")

                rmin = min(agreed)            # reduced-cluster minimum
                rmax = leg                    # legacy oxidized value = band high end
                def ref_for(val):
                    hits = sorted({x["ref"] for x in recs if x["orbital"] == line and abs(x["energy"] - val) < 1e-6})
                    return hits[0] if hits else None
                digest = digest_recoverable(o, obs4b.get(fid, {}), sref, sval)
                z, name = info[el]
                tid = f"{el}-{line}"
                notes = (f"Reduced/{res['reduced_state']} reference value ({sref}, NIST-evaluated) is the "
                         f"nominal; the band spans up to the {res['oxidized_state']} reference at {leg:g} eV. "
                         f"Resolved from a legacy {res['reduced_state']}/{res['oxidized_state']} conflict by the "
                         f"lower-BE = reduced rule (legacy {leg:g} eV was the {res['oxidized_state']} position). "
                         f"Machine tier — not human-verified.")
                emitted.append({
                    "z": z, "symbol": el, "name": name, "orbital": line, "id": tid,
                    "nominal": sval, "ref": sref, "rmin": rmin, "rmax": rmax,
                    "basis": "reduced-to-oxidized-chemical-state-span", "notes": notes,
                    "refs": sorted(set(r.get("claude_refs", []) + r.get("codex_refs", []))),
                })
                prov.append({
                    "id": tid, "element": el, "orbital": line,
                    "nominal_be_ev": sval,
                    "nominal_source": {
                        "database": SOURCE_ID, "nist_line": line, "nist_reference_code": sref,
                        "evaluated": True, "source_url": o.get("source_url"),
                        "source_artifact": f"{el}_nist.html",
                        "source_artifact_sha256": sha256_file(html_path),
                    },
                    "parse_method": "nist-html-starred-record",
                    "dual_extraction_corroborated": True,
                    "digest_corroborated": bool(digest),
                    "html_only_recovery": not bool(digest),
                    "expected_region_ev": {
                        "min": rmin, "min_source": ref_for(rmin),
                        "max": rmax, "max_source": "legacy-embedded-dataset",
                        "basis": "reduced-to-oxidized-chemical-state-span",
                        "agreed_distinct_energy_count": len(agreed),
                    },
                    "conflict_resolution": {
                        "rule": "lower-BE = reduced (NIST-evaluated reduced value is the nominal; the legacy oxidized value is superseded as the band's high end)",
                        "reduced_state": res["reduced_state"],
                        "oxidized_state": res["oxidized_state"],
                        "superseded_legacy_value": leg,
                        "region_basis": "reduced-to-oxidized-chemical-state-span",
                    },
                    "tier": "machine",
                })
                continue
            detail = "not dual-corroborated (Stage-9 tier)"
            if key == ("V", "2p3/2"):
                detail = ("conflict (legacy oxide vs NIST metal cluster) AND no NIST-evaluated (starred) "
                          "value in source — fails the conflict-resolution V-safety guard, not promotable")
            skipped.append({**rec, "reason": tier, "detail": detail})
            continue
        if (el, line) in curated:
            skipped.append({**rec, "reason": "already-curated",
                            "detail": "transition exists in a curated element file; additive-only, machine not emitted"})
            continue

        html_path = os.path.join(STAGE9, "extract_claude", f"{el}_nist.html")
        if not os.path.exists(html_path):
            skipped.append({**rec, "reason": "no-source-artifact",
                            "detail": f"{el}_nist.html absent"})
            continue
        recs = parse_nist_html(html_path)
        starred = [x for x in recs if x["orbital"] == line and x["evaluated"]]
        if not starred:
            skipped.append({**rec, "reason": "context-undeterminable",
                            "detail": "no NIST-evaluated (starred) value; material/chemical-state class not recoverable from the archived page, so rule 2 cannot establish a context-equivalent nominal"})
            continue

        sval, sref = starred[0]["energy"], starred[0]["ref"]
        agreed = r["agreed_values"]
        if not any(abs(sval - a) < 1e-6 for a in agreed):
            skipped.append({**rec, "reason": "evaluated-not-corroborated",
                            "detail": f"starred value {sval} ({sref}) not present in the dual-corroborated agreed-set"})
            continue

        # Region from the corroborated agreed-set (the one allowed derivation).
        rmin, rmax = min(agreed), max(agreed)

        # Source ref for each region endpoint: the alphabetically-first NIST ref
        # whose HTML record reports that energy (deterministic).
        def ref_for(val):
            hits = sorted({x["ref"] for x in recs if x["orbital"] == line and abs(x["energy"] - val) < 1e-6})
            return hits[0] if hits else None

        digest = digest_recoverable(o, obs4b.get(fid, {}), sref, sval)
        z, name = info[el]
        tid = f"{el}-{line}"

        emitted.append({
            "z": z, "symbol": el, "name": name, "orbital": line, "id": tid,
            "nominal": sval, "ref": sref, "rmin": rmin, "rmax": rmax,
            "basis": "observed-reference-range",
            "notes": (f"NIST-evaluated value ({sref}, starred on the SRD 20 element page); "
                      f"dual-extraction corroborated (present in the agreed-set). Region spans "
                      f"NIST records across chemical states. Machine tier — not human-verified."),
            "refs": sorted(set(r.get("claude_refs", []) + r.get("codex_refs", []))),
        })
        prov.append({
            "id": tid, "element": el, "orbital": line,
            "nominal_be_ev": sval,
            "nominal_source": {
                "database": SOURCE_ID,
                "nist_line": line,
                "nist_reference_code": sref,
                "evaluated": True,
                "source_url": o.get("source_url"),
                "source_artifact": f"{el}_nist.html",
                "source_artifact_sha256": sha256_file(html_path),
            },
            "parse_method": "nist-html-starred-record",
            "dual_extraction_corroborated": True,
            "digest_corroborated": bool(digest),
            "html_only_recovery": not bool(digest),
            "expected_region_ev": {
                "min": rmin, "min_source": ref_for(rmin),
                "max": rmax, "max_source": ref_for(rmax),
                "basis": "observed-reference-range",
                "agreed_distinct_energy_count": len(agreed),
            },
            "tier": "machine",
        })

    # ── Coverage-expansion path (additive) ───────────────────────────────────
    # Emit machine records for artifact-backed new elements/levels. Every
    # emitted value is the NIST-evaluated (starred) value read from a fetched
    # element-page snapshot in EXPAND_DIR; non-starred lines and artifact-less
    # elements are skip-logged. This path NEVER touches the tiers-driven
    # records above: any (element, subshell) already covered by a curated tier
    # or a tiers-driven machine record is skip-logged, never re-emitted.
    curated_sub = {(s, subshell(o)) for (s, o) in curated}
    tiers_machine_sub = {(e["symbol"], subshell(e["orbital"])) for e in emitted}
    expand_manifest = os.path.join(EXPAND_DIR, "acquire_manifest.json")
    if os.path.exists(expand_manifest):
        man = {m["symbol"]: m for m in load(expand_manifest)["elements"]}
        # Independent second-agent re-derivation (Step-4 cross-check). A value is
        # marked agent_cross_checked only if the independent pass confirms it.
        xc_path = os.path.join(EXPAND_DIR, "agent_crosscheck.json")
        xc = load(xc_path) if os.path.exists(xc_path) else {}
        for sym, (z, name) in sorted(PERIODIC_TABLE.items(), key=lambda kv: kv[1][0]):
            mrec = man.get(sym)
            art = os.path.join(EXPAND_DIR, f"{sym}_nist.html")
            if not mrec or mrec.get("status") != "OK" or not os.path.exists(art):
                reason = (mrec.get("reason") if mrec else "no acquisition record")
                skipped.append({"element": sym, "orbital": None, "reason": "no-evaluated-value",
                                "detail": f"coverage-expansion FAILED: {reason}"})
                continue
            recs = parse_nist_html(art)
            sha = sha256_file(art)
            if mrec.get("sha256") and sha != mrec["sha256"]:
                raise SystemExit(f"expansion artifact/manifest desync for {sym}: "
                                 f"disk sha {sha[:12]} != manifest {mrec['sha256'][:12]}")
            by_line = {}
            for x in recs:
                if EXPAND_PE_LINE.match(x["orbital"]):
                    by_line.setdefault(x["orbital"], []).append(x)
            for orbital in sorted(by_line):
                line_recs = by_line[orbital]
                starred = [x for x in line_recs if x["evaluated"]]
                if not starred:
                    skipped.append({"element": sym, "orbital": orbital, "reason": "context-undeterminable",
                                    "detail": "no NIST-evaluated (starred) value for this line"})
                    continue
                if (sym, subshell(orbital)) in curated_sub:
                    skipped.append({"element": sym, "orbital": orbital, "reason": "already-curated",
                                    "detail": "expansion: subshell covered by a curated element file; additive-only"})
                    continue
                if (sym, subshell(orbital)) in tiers_machine_sub:
                    skipped.append({"element": sym, "orbital": orbital, "reason": "already-machine-tier",
                                    "detail": "expansion: subshell already emitted by the Stage-9 tiers-driven machine path"})
                    continue
                sval, sref = starred[0]["energy"], starred[0]["ref"]
                energies = [x["energy"] for x in line_recs]
                rmin, rmax = min(energies), max(energies)
                def ref_for_line(val, lr=line_recs):
                    hits = sorted({x["ref"] for x in lr if abs(x["energy"] - val) < 1e-6})
                    return hits[0] if hits else None
                tid = f"{sym}-{orbital}"
                emitted.append({
                    "z": z, "symbol": sym, "name": name, "orbital": orbital, "id": tid,
                    "nominal": sval, "rmin": rmin, "rmax": rmax,
                    "basis": "observed-reference-range",
                    "curation_notes": EXPAND_NOTE,
                    "notes": (f"NIST-evaluated value ({sref}, starred on the SRD 20 element page); "
                              f"single archived snapshot, committed-parser + independent agent "
                              f"cross-checked. Region spans NIST records on the element page. "
                              f"Machine tier — not human-verified."),
                })
                prov.append({
                    "id": tid, "element": sym, "orbital": orbital,
                    "nominal_be_ev": sval,
                    "nominal_source": {
                        "database": SOURCE_ID, "nist_line": orbital, "nist_reference_code": sref,
                        "evaluated": True, "source_url": mrec["source_url"],
                        "source_artifact": f"{sym}_nist.html", "source_artifact_sha256": sha,
                        "archive_snapshot_timestamp": mrec["snapshot_timestamp"],
                        "fetch_utc": mrec["fetch_utc"],
                    },
                    "parse_method": "nist-html-starred-record",
                    "acquisition": "coverage-expansion: single archived NIST element-page snapshot",
                    "dual_extraction_corroborated": False,
                    "agent_cross_checked": bool(tid in xc and abs(xc[tid] - sval) < 1e-9),
                    "expected_region_ev": {
                        "min": rmin, "min_source": ref_for_line(rmin),
                        "max": rmax, "max_source": ref_for_line(rmax),
                        "basis": "observed-reference-range",
                        "record_count": len(line_recs),
                    },
                    "tier": "machine",
                })

    emitted.sort(key=lambda e: (e["z"], e["orbital"]))
    prov.sort(key=lambda p: p["id"])
    skipped.sort(key=lambda s: (s["element"], str(s["orbital"])))

    # ── elements-machine.json ────────────────────────────────────────────────
    elements = []
    _by_sym = {}
    for e in emitted:
        t = {
            "id": e["id"], "element": e["symbol"], "z": e["z"], "orbital": e["orbital"],
            "transition_type": "photoelectron",
            "nominal_be_ev": e["nominal"],
            "spin_orbit": None,
            "expected_region_ev": {"min": e["rmin"], "max": e["rmax"],
                                   "basis": e["basis"]},
            "visibility": {"AlKa": "machine-unassessed"},
            "source": SOURCE_ID,
            "tier": "machine",
            "notes": e["notes"],
        }
        # Group transitions under one element object (a single element may carry
        # several NIST-evaluated lines). Single-line elements (all existing 27)
        # produce byte-identical output to the prior one-object-per-line form.
        obj = _by_sym.get(e["symbol"])
        if obj is None:
            obj = {
                "symbol": e["symbol"], "z": e["z"], "name": e["name"],
                "curation_status": "machine",
                "curation_notes": e.get("curation_notes", GEN_NOTE),
                "families": [],
            }
            _by_sym[e["symbol"]] = obj
            elements.append(obj)
        fam_label = subshell(e["orbital"])
        fam = next((f for f in obj["families"] if f["family"] == fam_label), None)
        if fam is None:
            fam = {"family": fam_label, "transitions": []}
            obj["families"].append(fam)
        fam["transitions"].append(t)

    machine_doc = {"schema_version": 1, "file_id": "elements-machine", "elements": elements}
    prov_doc = {
        "note": ("Committed provenance for elements-machine.json. Each emitted machine "
                 "value is verifiable from this manifest independent of the gitignored "
                 ".stage9 working data: NIST source locator + reference code, the recovered "
                 "evaluated value, a sha256 of the artifact it was parsed from, the parse "
                 "method, and corroboration flags. Generated by " + GENERATOR_REL + "."),
        "source_database": SOURCE_ID,
        "generator": GENERATOR_REL,
        "emitted_count": len(prov),
        "transitions": prov,
    }
    skipped_doc = {
        "note": ("Every transcription-corroborated/conflict/insufficient survey transition "
                 "NOT promoted to the machine tier, with the reason. Together with "
                 "elements-machine.provenance.json this is the Phase B audit surface."),
        "reasons": {
            "already-curated": "transition exists in a curated element file (additive-only)",
            "context-undeterminable": "no NIST-evaluated value; material class not recoverable, so rule 2 cannot fire",
            "evaluated-not-corroborated": "starred value not in the dual-corroborated agreed-set",
            "conflict": "Stage-9 tier: legacy disagrees with NIST (e.g. oxide vs metal / Auger-frame)",
            "insufficient-evidence": "Stage-9 tier: not recoverable in both extractions",
            "no-evaluated-value": "coverage-expansion: artifact fetched but no NIST-evaluated (starred) photoelectron line — nothing sourceable to emit (e.g. Rb, Cs)",
            "already-machine-tier": "coverage-expansion: subshell already emitted by the Stage-9 tiers-driven machine path (additive-only)",
        },
        "skipped_count": len(skipped),
        "transitions": skipped,
    }

    return machine_doc, prov_doc, skipped_doc


def serialize(obj):
    """Canonical on-disk form (deterministic; trailing newline)."""
    return json.dumps(obj, indent=2, ensure_ascii=True, sort_keys=False) + "\n"


def main():
    machine_doc, prov_doc, skipped_doc = build()
    for name, obj in (("elements-machine.json", machine_doc),
                      ("elements-machine.provenance.json", prov_doc),
                      ("elements-machine.skipped.json", skipped_doc)):
        with open(os.path.join(DATA, name), "w") as f:
            f.write(serialize(obj))
    from collections import Counter
    ntrans = sum(len(f["transitions"]) for el in machine_doc["elements"] for f in el["families"])
    print(f"machine elements: {len(machine_doc['elements'])}  |  machine transitions: {ntrans}")
    print(f"skipped: {skipped_doc['skipped_count']} -> "
          f"{dict(Counter(s['reason'] for s in skipped_doc['transitions']))}")
    print(f"html-only recoveries: {[p['id'] for p in prov_doc['transitions'] if p.get('html_only_recovery')]}")
    print(f"coverage-expansion emitted: {[p['id'] for p in prov_doc['transitions'] if p.get('acquisition')]}")


if __name__ == "__main__":
    main()
