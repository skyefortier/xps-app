#!/usr/bin/env python3
"""Sequential, no-invention acquisition of NIST SRD-20 element pages for the
coverage-expansion elements. Fetches the archived `query_all_dat_el.asp?elm1=X`
snapshot (the format the committed parser handles), stores raw bytes + sha256 +
exact source URL + snapshot timestamp + fetch timestamp, and records the
NIST-evaluated (starred) photoelectron lines literally present in the artifact.

Every value comes from a fetched artifact; nothing from memory. An element/level
with no reachable/parseable artifact or no starred value is logged, not invented.
"""
import hashlib
import importlib.util
import json
import os
import re
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ART = os.path.join(HERE, "expand_artifacts")
os.makedirs(ART, exist_ok=True)

ELEMENTS = ["Sc", "Ru", "Pd", "Hf", "Ta", "Re", "Os", "Ir", "Hg", "Tl", "Rb", "Cs"]

# committed parser — single source of parsing truth
spec = importlib.util.spec_from_file_location("g", os.path.join(REPO, "scripts", "gen_machine_tier.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)

PE_LINE = re.compile(r"^[1-7][spdf]([1357]/2)?$")   # photoelectron subshell (exclude DS-*, Auger)
UA = "Mozilla/5.0 (xps-reference-research; sourced-only)"


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


def cdx_snapshots(elem):
    base = f"srdata.nist.gov/xps/query_all_dat_el.asp?elm1={elem}"
    q = urllib.parse.quote(base, safe="")
    url = f"https://web.archive.org/cdx/search/cdx?url={q}&output=json&limit=12"
    try:
        data = json.loads(http_get(url, timeout=45))
    except Exception as e:
        return []
    rows = data[1:] if data and isinstance(data, list) else []
    # rows: [urlkey, timestamp, original, mimetype, statuscode, digest, length]
    snaps = [(r[1], r[2], r[4]) for r in rows if len(r) >= 5 and r[4] in ("200", "-")]
    snaps.sort(key=lambda s: s[0])      # earliest first (2004 vintage, matches existing)
    return snaps


def acquire(elem):
    rec = {"symbol": elem, "status": "FAILED", "reason": None,
           "snapshot_timestamp": None, "source_url": None, "sha256": None,
           "bytes": 0, "starred_pe_lines": [], "all_pe_line_count": 0,
           "fetch_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    snaps = cdx_snapshots(elem)
    if not snaps:
        rec["reason"] = "no archive snapshot of query_all_dat_el.asp for this element"
        return rec
    for ts, original, _sc in snaps:
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
        recs = g.parse_nist_html(path)
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
    return rec


def main():
    out = []
    for el in ELEMENTS:
        print(f"--- {el} ---", flush=True)
        r = acquire(el)
        print(f"    {r['status']}: ts={r['snapshot_timestamp']} sha={ (r['sha256'] or '')[:12] } "
              f"starred={[(s['orbital'], s['energy'], s['ref']) for s in r['starred_pe_lines']]} reason={r['reason']}", flush=True)
        out.append(r)
        time.sleep(2)
    with open(os.path.join(ART, "acquire_manifest.json"), "w") as f:
        json.dump({"elements": out}, f, indent=2)
    ok = [r["symbol"] for r in out if r["status"] == "OK"]
    print(f"\nDONE. OK={ok}  FAILED={[r['symbol'] for r in out if r['status']!='OK']}", flush=True)


if __name__ == "__main__":
    main()
