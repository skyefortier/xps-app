#!/usr/bin/env python3
"""Deterministic summary of the NIST SRD-20 acquisition manifest state —
the committed evidence record for element-coverage exhaustion (unit R2).

Reads .stage9/expand_artifacts/acquire_manifest.json (gitignored working
data) and emits docs/autofit/inventory/acquisition_exhaustion.json — the
committed, regenerable summary: which elements are archivally recoverable
(OK), which are not and WHY (the two structural reasons), and the probe
coverage span. Committed-generator rule: this script must be re-runnable
to reproduce the committed summary from the manifest at any time.

No values are emitted here — only acquisition STATE (statuses, reasons,
counts, timestamps). The values themselves live in data/xps with their
own provenance chain.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MANIFEST = os.path.join(REPO, ".stage9", "expand_artifacts",
                        "acquire_manifest.json")
OUT = os.path.join(REPO, "docs", "autofit", "inventory",
                   "acquisition_exhaustion.json")


def build():
    with open(MANIFEST) as f:
        elements = json.load(f)["elements"]
    ok = sorted(r["symbol"] for r in elements if r["status"] == "OK")
    failed = [r for r in elements if r["status"] != "OK"]

    def reason_class(r):
        reason = str(r.get("reason", ""))
        if reason.startswith("cdx query failed"):
            # NOT proof of absence — a summary containing this class is
            # NOT an exhaustion certificate (the test pins zero of these)
            return "cdx-query-failed-UNPROVEN"
        if reason.startswith("no archive snapshot"):
            return "no-archive-snapshot"
        if "no NIST-evaluated" in reason:
            return "artifact-has-no-starred-value"
        return "other-UNCLASSIFIED"

    by_reason: dict = {}
    for r in failed:
        entry = {
            "symbol": r["symbol"],
            "reason": r.get("reason"),
            "last_probe_utc": r.get("fetch_utc"),
        }
        if r.get("snapshots_checked"):
            # evidence of archive-exhaustive iteration (multi-snapshot)
            entry["snapshots_checked"] = r["snapshots_checked"]
        by_reason.setdefault(reason_class(r), []).append(entry)
    for v in by_reason.values():
        v.sort(key=lambda x: x["symbol"])

    return {
        "generated_by": "scripts/summarize_acquisition.py",
        "source_manifest": ".stage9/expand_artifacts/acquire_manifest.json "
                           "(gitignored working data; resumable, written by "
                           "scripts/acquire_nist_archive.py)",
        "probed_element_count": len(elements),
        "ok_count": len(ok),
        "ok_elements": ok,
        "failed_count": len(failed),
        "failed_by_reason": by_reason,
        "note": (
            "Element coverage is EXHAUSTED under the no-invention rule: "
            "every element of the definitional periodic table was probed "
            "against the Wayback CDX for both archived SRD-20 page formats "
            "(query_all_dat_el.asp and .aspx). 'no-archive-snapshot' "
            "elements have NO snapshot of either format in the archive "
            "(re-confirmed by a fresh re-probe after clearing their "
            "manifest rows — CDX errors at first-sweep time were "
            "indistinguishable from true absence, so the re-probe was "
            "required evidence). 'artifact-has-no-starred-value' elements "
            "have an archived page but carry no NIST-evaluated (starred) "
            "photoelectron line — including the aspx-only format, which "
            "does not display evaluation markers at all (do NOT parse "
            "aspx pages for emission; see PROGRESS.md format finding). "
            "The boundary is the archive, not the pipeline."),
    }


def main():
    summary = build()
    tmp = OUT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, OUT)
    print(f"wrote {OUT}: probed={summary['probed_element_count']} "
          f"ok={summary['ok_count']} failed={summary['failed_count']}")


if __name__ == "__main__":
    sys.exit(main())
