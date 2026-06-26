#!/usr/bin/env python3
"""Regenerate tests/fixtures/curated_records_snapshot.json from the live data.

MANUAL, DELIBERATE ACT ONLY — run this when you intend to EXTEND the protected
baseline (e.g. after adding/curating new reference records), never to silence a
failing guard. A guard failure means live scientific content diverged from the
snapshot; investigate the diff, don't regenerate.

    python tests/fixtures/regen_curated_snapshot.py   # writes the fixture in place

Captures ONLY scientific content the byte-diff guards used to protect:
  * every curated photoelectron + auger transition (whole object), keyed by id;
  * per-element scientific meta (symbol, z, name, curation_status,
    curation_notes) — EXCLUDING additive display fields (short_caveat) and the
    families array (covered by the per-transition records);
  * the legacy directory's scientific payloads (survey markers, chemical-state
    groups, correction crossrefs).
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) \
    if os.path.basename(os.path.dirname(os.path.abspath(__file__))) == "fixtures" \
    else os.environ.get("REPO_ROOT", os.getcwd())
DATA = os.path.join(REPO, "data", "xps")
OUT = os.path.join(REPO, "tests", "fixtures", "curated_records_snapshot.json")

CURATED_FILES = ("elements-main.json", "elements-actinides.json",
                 "elements-lanthanides.json", "auger-lines.json")
# Scientific element-level fields the old guard protected. Anything NOT here
# (short_caveat, families, future display/help fields) is intentionally excluded
# so additive display fields never trip the guard.
ELEMENT_META_FIELDS = ("symbol", "z", "name", "curation_status", "curation_notes")
LEGACY_PAYLOADS = {
    "survey-lines.json": "elements",
    "chemical-states.json": "groups",
    "corrections.json": "crossrefs",
}


def _load(path):
    with open(path) as f:
        return json.load(f)


def build():
    records, element_meta = {}, {}
    for fn in CURATED_FILES:
        doc = _load(os.path.join(DATA, fn))
        for el in doc["elements"]:
            meta = {k: el[k] for k in ELEMENT_META_FIELDS if k in el}
            element_meta[f"{fn}:{el['symbol']}"] = meta
            for fam in el["families"]:
                for t in fam["transitions"]:
                    assert t["id"] not in records, f"dup transition id {t['id']}"
                    records[t["id"]] = t
    legacy = {}
    for fn, key in LEGACY_PAYLOADS.items():
        doc = _load(os.path.join(DATA, "legacy", fn))
        legacy[fn] = {key: doc[key]}
    return {
        "description": (
            "Protected-baseline oracle for the curated photoelectron + auger reference "
            "records and the frozen legacy directory (data/xps/elements-main.json, "
            "elements-actinides.json, elements-lanthanides.json, auger-lines.json, "
            "legacy/). Replaces the brittle whole-file `git diff --quiet HEAD` guards "
            "(test_curated_and_legacy_content_unchanged_vs_snapshot in test_machine_tier.py "
            "and test_prior_machine_records_unchanged_vs_snapshot in "
            "test_conflict_resolution.py), which went spuriously RED on any uncommitted "
            "edit and conflated byte-identity with scientific-content identity. "
            "'records' maps transition id -> the whole transition object; 'element_meta' "
            "maps '<file>:<symbol>' -> the scientific element fields (symbol, z, name, "
            "curation_status, curation_notes) ONLY — additive display/help fields such as "
            "short_caveat and the families array are deliberately excluded so they never "
            "trip the guard; 'legacy_payloads' maps each legacy file -> its scientific "
            "payload. The guards assert every snapshot entry is still present and "
            "structurally identical in the live files (mutated value/region/tier/"
            "curation_notes/source IS caught); records added later are additive and "
            "neither protected nor blocked until this baseline is intentionally extended. "
            "THE FIXTURE IS THE SOLE ORACLE — the guards never read git/HEAD. "
            "REGENERATION IS A DELIBERATE MANUAL ACT (never inside pytest, never to "
            "silence a failure): run `python tests/fixtures/regen_curated_snapshot.py`."
        ),
        "records": dict(sorted(records.items())),
        "element_meta": dict(sorted(element_meta.items())),
        "legacy_payloads": legacy,
    }


if __name__ == "__main__":
    out = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {OUT}")
    print(f"  records={len(out['records'])} element_meta={len(out['element_meta'])} "
          f"legacy_payloads={list(out['legacy_payloads'])}")
