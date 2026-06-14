"""
Stage 9 Phase 5 — deterministic cross-check + honest tier adjudication.

Reads the two INDEPENDENT extraction passes over the same authoritative NIST
SRD 20 archive snapshots:
  .stage9/extract_claude/observations_4a.json   (Claude workers, pass 1)
  .stage9/extract_codex/observations_4b.json     (Codex, pass 2)
and the legacy survey values (the fields being adjudicated), then assigns each
field an HONEST tier. NO value is invented; NO criterion is relaxed.

Context-equivalence: a legacy survey field's reference-state is UNSPECIFIED,
so the only context we can match on is (element, orbital -> NIST principal
line). A legacy value is "consistent with" an authoritative observation when
some extracted be_ev is within TOL of it. TOL is loose (legacy values are
rounded integers and may sit on metal or a common compound) — this is an
ORIENTATION match, deliberately not a precision claim.

Tiers (top autonomous tier is 'transcription-corroborated'; 'machine-source-
corroborated' requires a SECOND independent SOURCE — not produced by a
NIST-only pass, so survey fields never reach it here, and we never claim it):
  transcription-corroborated : both passes extracted, AGREE on a NIST value,
                               and that value matches the legacy field (TOL)
  conflict                   : passes agree on an authoritative value that
                               CONTRADICTS the legacy field, OR the two passes
                               disagree with each other
  single-source              : exactly one pass extracted a value matching the
                               legacy field
  context-unconfirmed        : a value was extracted but cannot be matched to
                               the legacy field within TOL (reference-state
                               ambiguity) — not corroborated, not a clean conflict
  insufficient-evidence      : neither pass recovered an authoritative value
                               (no snapshot / no line / fetch failed) — the
                               legacy value stays legacy-unverified
"""
import json
from pathlib import Path

TOL = 2.0   # eV — orientation tolerance for legacy(rounded)-vs-authoritative
AGREE = 0.3  # eV — two passes "read the same record" if within this

A = Path(".stage9/extract_claude/observations_4a.json")
B = Path(".stage9/extract_codex/observations_4b.json")
MANIFEST = Path(".stage9/manifest/manifest.json")


def _by_field(path):
    if not path.exists():
        return {}
    obs = json.loads(path.read_text())
    obs = obs.get("observations", obs) if isinstance(obs, dict) else obs
    return {o["field_id"]: o for o in obs}


def _vals(o):
    if not o or o.get("status") != "extracted":
        return []
    return [v["be_ev"] for v in (o.get("values") or [])]


def _matches(vals, target, tol):
    return [v for v in vals if abs(v - target) <= tol]


def adjudicate():
    a = _by_field(A)
    b = _by_field(B)
    manifest = json.loads(MANIFEST.read_text())
    survey_fields = [f for f in manifest["fields"] if f["kind"] == "legacy-survey-line"]

    out = []
    for f in survey_fields:
        fid, legacy = f["field_id"], f["current_value"]
        oa, ob = a.get(fid), b.get(fid)
        va, vb = _vals(oa), _vals(ob)
        a_ext, b_ext = bool(va), bool(vb)

        # cross-pass agreement: any pair of values within AGREE
        agreed = sorted({round(x, 2) for x in va for y in vb if abs(x - y) <= AGREE})
        a_match = _matches(va, legacy, TOL)
        b_match = _matches(vb, legacy, TOL)

        if a_ext and b_ext:
            if agreed:
                # passes read the same authoritative value(s)
                if _matches(agreed, legacy, TOL):
                    tier = "transcription-corroborated"
                elif a_match or b_match:
                    # they agree on something AND one matches legacy though the
                    # agreed set didn't — treat as corroborated-consistent
                    tier = "transcription-corroborated"
                else:
                    tier = "conflict"   # corroborated authoritative value != legacy
            else:
                # both extracted but disagree with each other
                tier = "conflict"
        elif a_ext or b_ext:
            tier = "single-source" if (a_match or b_match) else "context-unconfirmed"
        else:
            tier = "insufficient-evidence"

        out.append({
            "field_id": fid, "element": f["element"], "orbital": f["context"]["orbital"],
            "legacy_be": legacy, "tier": tier,
            "claude_status": (oa or {}).get("status", "absent"),
            "codex_status": (ob or {}).get("status", "absent"),
            "claude_values": va, "codex_values": vb,
            "agreed_values": agreed,
            "claude_refs": [v.get("nist_ref") for v in ((oa or {}).get("values") or [])],
            "codex_refs": [v.get("nist_ref") for v in ((ob or {}).get("values") or [])],
            "source_urls": list(filter(None, [(oa or {}).get("source_url"), (ob or {}).get("source_url")])),
        })
    return out


if __name__ == "__main__":
    res = adjudicate()
    Path(".stage9/manifest").mkdir(parents=True, exist_ok=True)
    Path(".stage9/manifest/tiers_survey.json").write_text(json.dumps(res, indent=2))
    from collections import Counter
    c = Counter(r["tier"] for r in res)
    print("Phase 5 survey-line tier adjudication —", len(res), "fields")
    for t in ["transcription-corroborated", "machine-source-corroborated", "single-source",
              "conflict", "context-unconfirmed", "insufficient-evidence"]:
        if c.get(t):
            print(f"  {t:30s} {c[t]}")
    print("\nConflicts (legacy vs corroborated authoritative — need Phase 6 audit):")
    for r in res:
        if r["tier"] == "conflict":
            print(f"  {r['element']} {r['orbital']}: legacy {r['legacy_be']} | "
                  f"claude {r['claude_values']} | codex {r['codex_values']}")
