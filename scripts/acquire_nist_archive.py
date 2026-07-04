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
    base = f"srdata.nist.gov/xps/query_all_dat_el.{ext}?elm1={elem}"
    q = urllib.parse.quote(base, safe="")
    url = f"https://web.archive.org/cdx/search/cdx?url={q}&output=json&limit=12"
    try:
        data = json.loads(http_get(url, timeout=45))
    except Exception:
        return []
    rows = data[1:] if data and isinstance(data, list) else []
    # rows: [urlkey, timestamp, original, mimetype, statuscode, digest, length]
    snaps = [(r[1], r[2], r[4]) for r in rows if len(r) >= 5 and r[4] in ("200", "-")]
    snaps.sort(key=lambda s: s[0])      # earliest first (2004 vintage matches the parser)
    return snaps


def acquire(elem):
    rec = {"symbol": elem, "status": "FAILED", "reason": None,
           "snapshot_timestamp": None, "source_url": None, "sha256": None,
           "bytes": 0, "starred_pe_lines": [], "all_pe_line_count": 0,
           "fetch_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    snaps = [(ts, orig, sc, "asp") for ts, orig, sc in cdx_snapshots(elem, "asp")]
    snaps += [(ts, orig, sc, "aspx") for ts, orig, sc in cdx_snapshots(elem, "aspx")]
    if not snaps:
        rec["reason"] = "no archive snapshot of query_all_dat_el.asp(x) for this element"
        return rec
    for ts, original, _sc, _ext in snaps:
        src = f"https://web.archive.org/web/{ts}id_/{original}"
        try:
            raw = http_get(src, timeout=60)
        except Exception as e:
            rec["reason"] = f"fetch error: {e}"
            continue
        path = os.path.join(ART, f"{elem}_nist.html")
        with open(path, "wb") as f:
            f.write(raw)
        text = raw.decode("utf-8", "replace")
        if "All Data for" not in text:
            rec["reason"] = f"snapshot {ts} not the element-data page (likely a redirect/placeholder)"
            continue
        recs = parse_nist_html(path)
        pe = [r for r in recs if PE_LINE.match(r["orbital"])]
        starred = sorted({(r["orbital"], r["energy"], r["ref"].lstrip("*").strip())
                          for r in pe if r["evaluated"]})
        rec.update(snapshot_timestamp=ts, source_url=src,
                   sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                   all_pe_line_count=len(pe),
                   starred_pe_lines=[{"orbital": o, "energy": e, "ref": rf} for o, e, rf in starred])
        if starred:
            rec["status"] = "OK"
            rec["reason"] = None
        else:
            rec["status"] = "FAILED"
            rec["reason"] = "artifact fetched but no NIST-evaluated (starred) photoelectron line"
        return rec
    # nothing usable; make sure a half-written artifact doesn't linger
    path = os.path.join(ART, f"{elem}_nist.html")
    if os.path.exists(path) and rec["sha256"] is None:
        os.remove(path)
    return rec


def main():
    validate_definitional()
    os.makedirs(ART, exist_ok=True)
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
        # Resumable skips: OK with artifact; FAILED-but-fetched with artifact
        # (immutable snapshot — refetching cannot change 'nothing starred');
        # FAILED with no snapshot found (probing again is pointless).
        if art_present and prior.get("sha256") and prior.get("status") in ("OK", "FAILED"):
            print(f"--- {el}: already acquired ({prior['status']}, artifact present) ---", flush=True)
            continue
        if prior.get("status") == "FAILED" and \
                str(prior.get("reason", "")).startswith("no archive snapshot"):
            print(f"--- {el}: already probed (no archive snapshot) ---", flush=True)
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
