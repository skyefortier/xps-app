"""
Stage 9 Phase 8 — full evidence report generator.

Shows the transformation as explicit LAYERS (per user direction):
  L1 legacy fixture      : the immutable snapshot of the original constants
  L2 verbatim imported   : data/xps/legacy/*.json (== L1, parity-proven)
  L3 curated correction  : adjudicated corrections — curated dataset values
                           (e.g. U 4f 380->377.3) + the 8 survey-conflict
                           resolutions (metal nominal / Auger KE). EXPLICIT
                           transforms, each with provenance.
  L4 effective output    : L2 with L3 applied where a correction exists.

Insufficient-evidence / legacy-unverified fields are marked NON-AUTHORITATIVE
and unresolved. machine-source-corroborated is claimed nowhere.
"""
import json
from pathlib import Path

R = Path("data/xps")
S = Path(".stage9")

legacy_survey = {e["symbol"]: e for e in json.load(open(R/"legacy/survey-lines.json"))["elements"]}
legacy_chem = json.load(open(R/"legacy/chemical-states.json"))["groups"]
tiers_survey = {t["field_id"]: t for t in json.load(open(S/"manifest/tiers_survey.json"))}
tiers_chem = {t["field_id"]: t for t in json.load(open(S/"manifest/tiers_chem.json"))}
manifest = json.load(open(S/"manifest/manifest.json"))

# Curated correction values: map (element, survey-family) -> curated principal nominal.
PRINCIPAL = {"f": "7/2", "d": "5/2", "p": "3/2"}
curated = {}
for f in ("elements-main.json", "elements-actinides.json"):
    for el in json.load(open(R/f))["elements"]:
        for fam in el["families"]:
            for t in fam["transitions"]:
                orb = t["orbital"]
                sub = orb[1] if len(orb) > 1 else ""
                # family principal? (e.g. 4f7/2 is principal of 4f)
                if sub in PRINCIPAL and orb.endswith(PRINCIPAL[sub]):
                    curated[(el["symbol"], fam["family"])] = (t["nominal_be_ev"], t["source"], orb)
                elif sub not in PRINCIPAL:  # s-line singlet
                    curated[(el["symbol"], fam["family"])] = (t["nominal_be_ev"], t["source"], orb)

lines = ["# Stage 9 Phase 8 — Evidence Report (layered)", "",
         "Migration of the legacy XPS_ELEMENTS / CHEMICAL_STATES constants to the "
         "data/xps reference system, with dual-extraction adjudication. Shown as "
         "explicit transformation layers. No fabrication; unresolved values stay flagged.", ""]

# ── Tier summary ────────────────────────────────────────────────────────────
from collections import Counter
cs = Counter(t["tier"] for t in tiers_survey.values())
cc = Counter(t["tier"] for t in tiers_chem.values())
lines += [f"## 1. Tier adjudication ({len(tiers_survey) + len(tiers_chem)} legacy quantitative fields)", "",
          f"| tier | survey ({len(tiers_survey)}) | chem ({len(tiers_chem)}) |", "|---|---|---|"]
for tier in ["transcription-corroborated", "single-source", "conflict",
             "context-unconfirmed", "insufficient-evidence"]:
    if cs.get(tier) or cc.get(tier):
        lines.append(f"| {tier} | {cs.get(tier,0)} | {cc.get(tier,0)} |")
lines += ["", "`machine-source-corroborated` is claimed for NO field (both passes read the "
          "same source, NIST). Top honest tier = `transcription-corroborated`.", ""]

# ── Layered view: survey fields with a correction ───────────────────────────
lines += ["## 2. Correction layer (L3) — explicit transforms on the effective output", "",
          "Each row: legacy value (L1=L2) -> effective (L4). Correction source shown.", "",
          "| element | orbital | L1/L2 legacy | L3 correction | L4 effective | source | basis |",
          "|---|---|---|---|---|---|---|"]
survey_fields = [f for f in manifest["fields"] if f["kind"] == "legacy-survey-line"]
n_corr = 0
for f in survey_fields:
    el, orb = f["element"], f["context"]["orbital"]
    legacy = f["current_value"]
    t = tiers_survey[f["field_id"]]
    corr = None; src = ""; basis = ""
    if (el, orb) in curated:
        val, src, cur_orb = curated[(el, orb)]
        if abs(val - legacy) > 0.05:
            corr = val; basis = f"curated nominal ({cur_orb})"
    if corr is None and t["tier"] == "conflict":
        r = t.get("resolution", {})
        if r.get("kind") == "elemental-nominal-with-oxidation-range":
            corr = r["elemental_nominal_ev"]; basis = "elemental-nominal (metal)"; src = "nist-srd-20*"
        elif r.get("kind") == "auger-ke-frame":
            corr = r["auger_ke_ev"]; basis = "auger KE-frame"; src = "nist-srd-20*"
    eff = corr if corr is not None else legacy
    if corr is not None:
        n_corr += 1
        lines.append(f"| {el} | {orb} | {legacy} | {corr} | {eff} | {src} | {basis} |")
lines += ["", f"_{n_corr} survey fields carry a correction; the rest pass through legacy unchanged. "
          "*=corroborated by both extraction passes; metal/KE value, not a single-source pick._", ""]

# ── Non-authoritative ───────────────────────────────────────────────────────
lines += ["## 3. NON-AUTHORITATIVE — unresolved, stay legacy-unverified", "",
          "These have NO corroborating authoritative extraction. They retain the legacy "
          "value but are flagged non-authoritative; NOT presented as verified.", ""]
na_s = [t for t in tiers_survey.values() if t["tier"] in ("insufficient-evidence", "context-unconfirmed")]
na_c = [t for t in tiers_chem.values() if t["tier"] in ("insufficient-evidence", "context-unconfirmed")]
lines.append(f"**Survey ({len(na_s)}):** " + ", ".join(f"{t['element']} {t['orbital']} ({t['legacy_be']}, {t['tier']})" for t in na_s))
lines.append("")
lines.append(f"**Chem ({len(na_c)}):** " + ", ".join(f"{t['element']} {t['orbital']}/{t.get('state','')[:16]} ({t['tier']})" for t in na_c))
lines += ["", "## 4. Provenance & process", "",
          "- Phase 1: verbatim transcription, byte-exact parity (tests/test_legacy_parity.py).",
          "- Phase 4: dual independent extraction — 4a Claude workflow (8+6 agents) + 4b Codex "
          "(gpt-5.5) — from NIST SRD 20 Internet Archive snapshots; every value evidenced "
          "(source URL + row). Unfetchable -> status record.",
          "- Phase 5: deterministic cross-check + tiering (context-equivalence, BE proximity).",
          "- Phase 6: fixed-seed (20260613) third-agent audit, 26/26 PASS.",
          "- Checkpoint A (45e2c98) + B (1a8f998): Codex adversarial reviews; findings applied.",
          "- Parity gate green: 38 tests. Legacy constants intact; NO deletion in this report.", ""]

Path(".stage9/reports/phase8_evidence_report.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
