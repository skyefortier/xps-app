"""
Stage 9 Phase 5 (chemical states) — deterministic cross-check + honest tiering.

Each legacy chemical-state field is a specific compound BE (e.g. C 1s
Graphite = 284.5). The two extraction passes return ALL per-compound BEs for
the orbital from the NIST element-in-compound page; here we match each legacy
state's BE to those extracted compound BEs by proximity (label matching is
unreliable, BE proximity is the honest signal). A legacy state is corroborated
only if BOTH passes independently extracted a NIST compound with that BE.

Tiers (same honest ladder; chem-state shifts are small so TOL is tight):
  transcription-corroborated : both passes have a NIST compound BE within TOL
  single-source              : exactly one pass does
  context-unconfirmed        : compounds were extracted but none match this
                               state's BE (the specific compound/state is not
                               in the recovered NIST page — often page-1-only)
  insufficient-evidence      : no NIST compound page recovered for this element
"""
import json
from collections import Counter
from pathlib import Path

TOL = 0.8   # eV — chemical-state BEs are specific; tight tolerance

A = Path(".stage9/extract_chem_claude/groups_4a.json")
B = Path(".stage9/extract_chem_codex/groups_4b.json")
MANIFEST = Path(".stage9/manifest/manifest.json")


def _groups(path):
    if not path.exists():
        return {}
    d = json.loads(path.read_text())
    groups = d.get("groups", d) if isinstance(d, dict) else d
    out = {}
    for g in groups:
        out[(g["element"], g["orbital"])] = g
    return out


def _bes(g):
    if not g or g.get("status") != "extracted":
        return None  # None = no page recovered; [] would mean page-but-no-match
    return [c["be_ev"] for c in (g.get("compound_bes") or [])]


def adjudicate():
    a, b = _groups(A), _groups(B)
    manifest = json.loads(MANIFEST.read_text())
    chem_fields = [f for f in manifest["fields"] if f["kind"] == "legacy-chemical-state"]

    out = []
    for f in chem_fields:
        el, orb = f["element"], f["context"]["orbital"]
        legacy = f["current_value"]
        ba, bb = _bes(a.get((el, orb))), _bes(b.get((el, orb)))
        a_match = ba is not None and any(abs(v - legacy) <= TOL for v in ba)
        b_match = bb is not None and any(abs(v - legacy) <= TOL for v in bb)
        a_page = ba is not None
        b_page = bb is not None

        if a_match and b_match:
            tier = "transcription-corroborated"
        elif a_match or b_match:
            tier = "single-source"
        elif a_page or b_page:
            tier = "context-unconfirmed"   # page recovered, this state's BE not in it
        else:
            tier = "insufficient-evidence"

        out.append({
            "field_id": f["field_id"], "element": el, "orbital": orb,
            "state": f["context"]["reference_state"], "legacy_be": legacy, "tier": tier,
            "claude_page": a_page, "codex_page": b_page,
            "claude_match": a_match, "codex_match": b_match,
        })
    return out


if __name__ == "__main__":
    res = adjudicate()
    Path(".stage9/manifest/tiers_chem.json").write_text(json.dumps(res, indent=2))
    c = Counter(r["tier"] for r in res)
    print("Phase 5 chemical-state tier adjudication —", len(res), "fields")
    for t in ["transcription-corroborated", "single-source", "context-unconfirmed",
              "insufficient-evidence"]:
        if c.get(t):
            print(f"  {t:30s} {c[t]}")
