#!/usr/bin/env python3
"""NIST XPS SRD-20 archive retrieval pipeline (coverage expansion, full table).

Generalizes the original 12-element `.stage9/acquire_expand.py` run into the
committed acquisition tool for the element fit-physics / machine-tier coverage
work. For each target element it:

  1. discovers Internet Archive snapshots of the retired NIST SRD-20 query
     page (`srdata.nist.gov/xps/query_all_dat_el.asp?elm1=X`, 2004 vintage;
     falls back to the 2015/2016 `.aspx` form) via the CDX API;
  2. fetches the raw `id_` snapshot bytes, stores them + sha256 + exact source
     URL + snapshot timestamp + fetch timestamp under
     `.stage9/expand_artifacts/<Sym>_nist.html`;
  3. records the NIST-evaluated (starred) photoelectron lines literally present
     in the artifact, parsed by the ONE committed parser
     (`scripts/gen_machine_tier.py::parse_nist_html`).

ANTI-CONFABULATION CONTRACT: every recorded energy comes from a fetched
artifact; nothing from model memory. An element with no reachable/parseable
snapshot, or no NIST-evaluated line, is logged with a reason — never invented.
The only non-fetched facts are definitional periodic-table symbol/Z/name
(cross-validated against data/xps/legacy/survey-lines.json where present;
the script HARD-FAILS on any mismatch).

The manifest is resumable/mergeable: elements already `status: OK` with an
artifact on disk are not refetched (re-run to fill gaps only).

Run:  venv/bin/python scripts/acquire_nist_archive.py [Sym ...]
      (no args = the full target list below)
"""
import hashlib
import importlib.util
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ART = os.path.join(REPO, ".stage9", "expand_artifacts")
MANIFEST = os.path.join(ART, "acquire_manifest.json")

# committed parser + definitional periodic table — single source of truth
_spec = importlib.util.spec_from_file_location("gen_machine_tier", os.path.join(HERE, "gen_machine_tier.py"))
_g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_g)
parse_nist_html = _g.parse_nist_html
PERIODIC_TABLE = _g.PERIODIC_TABLE

PE_LINE = re.compile(r"^[1-7][spdf]([1357]/2)?$")   # photoelectron subshell (exclude DS-*, Auger)
UA = "Mozilla/5.0 (xps-reference-research; sourced-only)"


def validate_definitional():
    """Anchor the definitional table to committed data — hard-fail on mismatch."""
    docs = [("legacy/survey-lines.json", json.load(open(os.path.join(REPO, "data", "xps", "legacy", "survey-lines.json"))))]
    for fn in ("elements-main.json", "elements-actinides.json",
               "elements-lanthanides.json", "elements-machine.json"):
        docs.append((fn, json.load(open(os.path.join(REPO, "data", "xps", fn)))))
    for src, doc in docs:
        for el in doc["elements"]:
            sym = el["symbol"]
            if sym in PERIODIC_TABLE:
                z, name = PERIODIC_TABLE[sym]
                if el["z"] != z or el["name"] != name:
                    raise SystemExit(f"definitional mismatch vs {src} for {sym}: "
                                     f"table ({z},{name}) committed ({el['z']},{el['name']})")


def http_get(url, timeout=60, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(3 * (i + 1))
    raise last


def cdx_snapshots(elem, ext):
    """(snapshots, error) — a CDX failure is returned as an ERROR STRING,
    never collapsed into an empty result (Codex R2 review, both runs
    BLOCKER: a timeout was indistinguishable from true archive absence,
    leaving the exhaustion certification unproven). 'No snapshot' may only
    be concluded from an HTTP-successful, well-formed, EMPTY result set."""
    base = f"srdata.nist.gov/xps/query_all_dat_el.{ext}?elm1={elem}"
    q = urllib.parse.quote(base, safe="")
    # limit=200 is a sanity bound, not a practical cap: these obscure NIST
    # pages carry a handful of captures. The old limit=12 made the
    # "no starred line in ANY archived snapshot" conclusion an overclaim
    # (Codex R2 re-check, both runs: a starred snapshot at CDX row 13
    # would have been silently missed). cdx_rows in the manifest records
    # the returned count so a bound-binding listing is visible.
    url = f"https://web.archive.org/cdx/search/cdx?url={q}&output=json&limit=200"
    try:
        data = json.loads(http_get(url, timeout=45))
    except Exception as e:
        return [], f"{type(e).__name__}: {e}"
    if not isinstance(data, list):
        return [], f"malformed CDX response ({type(data).__name__})"
    rows = data[1:]
    # rows: [urlkey, timestamp, original, mimetype, statuscode, digest, length]
    snaps = [(r[1], r[2], r[4]) for r in rows if len(r) >= 5 and r[4] in ("200", "-")]
    snaps.sort(key=lambda s: s[0])      # earliest first (2004 vintage matches the parser)
    return snaps, None


def acquire(elem):
    rec = {"symbol": elem, "status": "FAILED", "reason": None,
           "snapshot_timestamp": None, "source_url": None, "sha256": None,
           "bytes": 0, "starred_pe_lines": [], "all_pe_line_count": 0,
           "snapshots_checked": 0, "cdx_errors": [], "cdx_rows": {},
           "fetch_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    snaps, errors = [], []
    for ext in ("asp", "aspx"):
        s, err = cdx_snapshots(elem, ext)
        snaps += [(ts, orig, sc, ext) for ts, orig, sc in s]
        rec["cdx_rows"][ext] = len(s)
        if err:
            errors.append(f"{ext}: {err}")
    rec["cdx_errors"] = errors
    if not snaps:
        if errors:
            # NOT proof of absence — a failed query must never be
            # certified as an empty archive (Codex R2 BLOCKER). The
            # resume logic re-probes this reason class.
            rec["reason"] = f"cdx query failed: {'; '.join(errors)}"
        else:
            rec["reason"] = "no archive snapshot of query_all_dat_el.asp(x) for this element"
        return rec

    # Iterate EVERY listed snapshot, earliest first, until a starred line
    # is found (Codex R2 review, run A MAJOR: concluding 'no starred
    # value' from only the FIRST usable artifact was not
    # archive-exhaustive — a later snapshot may carry evaluated records).
    # Candidates are parsed from a temp path; only the DECISION artifact
    # (the starred snapshot, else the first parseable one) is promoted to
    # {elem}_nist.html.
    final_path = os.path.join(ART, f"{elem}_nist.html")
    tmp_path = final_path + ".candidate"
    best = None            # (found_dict, raw_bytes) — first parseable, starless
    try:
        for ts, original, _sc, _ext in snaps:
            src = f"https://web.archive.org/web/{ts}id_/{original}"
            try:
                raw = http_get(src, timeout=60)
            except Exception as e:
                rec["reason"] = f"fetch error: {e}"
                continue
            rec["snapshots_checked"] += 1
            text = raw.decode("utf-8", "replace")
            if "All Data for" not in text:
                rec["reason"] = (f"snapshot {ts} not the element-data page "
                                 "(likely a redirect/placeholder)")
                time.sleep(1.5)     # polite spacing between snapshot fetches
                continue
            with open(tmp_path, "wb") as f:
                f.write(raw)
            recs = parse_nist_html(tmp_path)
            pe = [r for r in recs if PE_LINE.match(r["orbital"])]
            starred = sorted({(r["orbital"], r["energy"],
                               r["ref"].lstrip("*").strip())
                              for r in pe if r["evaluated"]})
            found = dict(snapshot_timestamp=ts, source_url=src,
                         sha256=hashlib.sha256(raw).hexdigest(),
                         bytes=len(raw), all_pe_line_count=len(pe),
                         starred_pe_lines=[{"orbital": o, "energy": e,
                                            "ref": rf}
                                           for o, e, rf in starred])
            if starred:
                os.replace(tmp_path, final_path)
                rec.update(found)
                rec["status"] = "OK"
                rec["reason"] = None
                return rec
            if best is None:
                best = (found, raw)
            time.sleep(1.5)         # polite spacing between snapshot fetches
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if best is not None:
        # every snapshot checked; none carries a starred line — the first
        # parseable artifact is the on-disk evidence for that conclusion
        found, raw = best
        with open(final_path, "wb") as f:
            f.write(raw)
        rec.update(found)
        rec["status"] = "FAILED"
        rec["reason"] = ("artifact fetched but no NIST-evaluated (starred) "
                         "photoelectron line in ANY archived snapshot "
                         f"({rec['snapshots_checked']} checked)")
        return rec

    # nothing usable; make sure a half-written artifact doesn't linger
    if os.path.exists(final_path) and rec["sha256"] is None:
        os.remove(final_path)
    return rec


def backfill_cdx_rows():
    """Record per-format CDX listing counts on manifest rows that predate the
    cdx_rows field (Codex R2 re-check round 2, run A NO-GO / run B MINOR:
    77/103 rows lacked the field — the 24 no-archive-snapshot rows and the
    53 OK rows — so the "max CDX listing across all probed elements" claim
    was not verifiable from committed evidence).

    EVIDENCE-ONLY: statuses, reasons, artifacts, and starred lines are never
    modified. Because the listing is fetched at backfill time (later than
    the row's acquisition), each backfilled row carries
    ``cdx_rows_backfilled_utc`` — the count describes the archive as of THAT
    date, honest provenance rather than a pretended acquisition-time record.

    A backfill result that CONTRADICTS a row's certified class is reported
    loudly and the row is left WITHOUT cdx_rows (so the certification pin
    stays honest): a ``no archive snapshot`` row whose listing is now
    non-empty, or any CDX query error. Those elements must be re-probed
    through the normal acquisition path, not patched here.
    """
    if not os.path.exists(MANIFEST):
        raise SystemExit("no manifest to backfill")
    with open(MANIFEST) as f:
        elements = json.load(f)["elements"]
    by_symbol = {r["symbol"]: r for r in elements}

    def write_manifest():
        tmp = MANIFEST + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"elements": elements}, f, indent=2)
        os.replace(tmp, MANIFEST)

    todo = [r for r in elements if not r.get("cdx_rows")]
    print(f"backfill: {len(todo)} of {len(elements)} rows lack cdx_rows", flush=True)
    contradictions = []
    for r in todo:
        el = r["symbol"]
        counts, errs = {}, []
        for ext in ("asp", "aspx"):
            s, err = cdx_snapshots(el, ext)
            counts[ext] = len(s)
            if err:
                errs.append(f"{ext}: {err}")
            time.sleep(1.0)     # polite CDX spacing
        if errs:
            contradictions.append((el, f"cdx query failed during backfill: {'; '.join(errs)}"))
            print(f"    {el}: ERROR (not recorded) — {errs}", flush=True)
            continue
        if str(r.get("reason", "")).startswith("no archive snapshot") \
                and (counts["asp"] or counts["aspx"]):
            contradictions.append(
                (el, f"no-archive-snapshot row now lists {counts} — the archive "
                     "changed; re-probe this element through the normal path"))
            print(f"    {el}: CONTRADICTION (not recorded) — {counts}", flush=True)
            continue
        r["cdx_rows"] = counts
        r["cdx_rows_backfilled_utc"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"    {el}: {counts}", flush=True)
        write_manifest()          # incremental: a killed run loses nothing
        time.sleep(1.0)
    if contradictions:
        print("\nCONTRADICTIONS / ERRORS (rows left without cdx_rows):", flush=True)
        for el, why in contradictions:
            print(f"  {el}: {why}", flush=True)
        raise SystemExit(2)
    still = [r["symbol"] for r in elements if not r.get("cdx_rows")]
    print(f"\nbackfill DONE — rows still lacking cdx_rows: {still or 'none'}", flush=True)


def main():
    validate_definitional()
    os.makedirs(ART, exist_ok=True)
    if sys.argv[1:2] == ["--backfill-cdx-rows"]:
        if sys.argv[2:]:
            raise SystemExit("--backfill-cdx-rows takes no element arguments")
        backfill_cdx_rows()
        return
    targets = sys.argv[1:] or sorted(PERIODIC_TABLE, key=lambda s: PERIODIC_TABLE[s][0])
    unknown = [t for t in targets if t not in PERIODIC_TABLE]
    if unknown:
        raise SystemExit(f"unknown element symbol(s): {unknown}")

    existing = {}
    if os.path.exists(MANIFEST):
        existing = {m["symbol"]: m for m in json.load(open(MANIFEST))["elements"]}

    out = dict(existing)

    def write_manifest():
        ordered = sorted(out.values(), key=lambda m: PERIODIC_TABLE.get(m["symbol"], (999,))[0])
        tmp = MANIFEST + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"elements": ordered}, f, indent=2)
        os.replace(tmp, MANIFEST)
        return ordered

    for el in targets:
        prior = existing.get(el) or {}
        art_present = os.path.exists(os.path.join(ART, f"{el}_nist.html"))
        # Resumable skips: OK with artifact; FAILED no-starred ONLY when the
        # conclusion is archive-exhaustive (the multi-snapshot reason text —
        # single-snapshot vintage records must be re-verified: Codex R2
        # review, run A MAJOR); FAILED with a PROVEN-empty CDX result
        # (a 'cdx query failed' reason is NOT proof and is always re-probed).
        if art_present and prior.get("sha256") and prior.get("status") == "OK":
            print(f"--- {el}: already acquired (OK, artifact present) ---", flush=True)
            continue
        if art_present and prior.get("sha256") and prior.get("status") == "FAILED" \
                and "in ANY archived snapshot" in str(prior.get("reason", "")):
            print(f"--- {el}: already exhaustively checked (no starred line in any snapshot) ---", flush=True)
            continue
        if prior.get("status") == "FAILED" and \
                str(prior.get("reason", "")).startswith("no archive snapshot"):
            print(f"--- {el}: already probed (no archive snapshot, CDX-proven empty) ---", flush=True)
            continue
        print(f"--- {el} ---", flush=True)
        r = acquire(el)
        print(f"    {r['status']}: ts={r['snapshot_timestamp']} sha={(r['sha256'] or '')[:12]} "
              f"starred={[(s['orbital'], s['energy'], s['ref']) for s in r['starred_pe_lines']]} "
              f"reason={r['reason']}", flush=True)
        out[el] = r
        write_manifest()          # incremental: a killed run loses nothing
        time.sleep(2)

    ordered = write_manifest()
    ok = [r["symbol"] for r in ordered if r["status"] == "OK"]
    print(f"\nDONE. OK={ok}\nFAILED={[r['symbol'] for r in ordered if r['status'] != 'OK']}", flush=True)


if __name__ == "__main__":
    main()
