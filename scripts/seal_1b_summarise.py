"""Seal 1b: the numbers in docs/findings/seal-1b/README.md, from the JSONL in one evidence folder.

Usage: python scripts/seal_1b_summarise.py [FOLDER]      (default docs/findings/seal-1b/v2;
       docs/findings/seal-1b/v1-superseded is the first run, on the obsolete targets)

Medians are true medians (the mean of the two middle values when n is even) and print their n.
"""
import json
import os
import re
import sys
from collections import Counter

D = sys.argv[1] if len(sys.argv) > 1 else "docs/findings/seal-1b/v2"
SETTINGS = ("verify_fresh_1.jsonl", "verify_fresh_2.jsonl", "verify_shake.jsonl", "verify_gunicorn.jsonl")


def rows(name):
    p = os.path.join(D, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def kind(r):
    return "synthetic" if str(r["id"]).startswith("syn-") else "committed"


def median(v):
    v = sorted(v)
    n = len(v)
    return (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2), n


def rng(v):
    v = [x for x in v if x is not None]
    return f"{min(v):.4g}–{max(v):.4g} (n {len(v)})" if v else "none"


rec = rows("records_index.jsonl")
# the first run's index (v1-superseded) carries none of the fields below its first line
full = bool(rec) and "backend_shapes" in rec[0]
by_id = {r["id"]: r for r in rec} if full else {}
if rec:
    print(f"== records: {len(rec)} ({dict(Counter(kind(r) for r in rec))}); HTTP status {dict(Counter(r['status'] for r in rec))}; "
          f"converged {sum(1 for r in rec if r.get('success'))}")
if full:
    print(f"   kind {dict(Counter(r.get('kind') or 'synthetic' for r in rec))}")
    print(f"   software identities {len({r.get('software_sha256') for r in rec})}; commits "
          f"{dict(Counter(r.get('git_commit') for r in rec))}; dirty {dict(Counter(r.get('git_dirty') for r in rec))}")
    print(f"   seed_source {dict(Counter(r.get('seed_source') for r in rec))}; fit_method {dict(Counter(r.get('fit_method') for r in rec))}; "
          f"n_perturb {dict(Counter(r.get('n_perturb') for r in rec))}; n_starts {dict(Counter(r.get('n_starts') for r in rec))}")
    for k in ("committed", "synthetic") if full else ():
        sub = [r for r in rec if kind(r) == k]
        print(f"   {k}: records holding each backend lineshape "
              f"{dict(sorted(Counter(s for r in sub for s in r['backend_shapes']).items()))}; components "
              f"{dict(sorted(Counter((p['frontend_shape'], p['shape']) for r in sub for p in r['peaks']).items(), key=str))}")
        print(f"   {k}: background method {dict(Counter(r['background']['method'] for r in sub))}; endpoint_avg "
              f"{dict(Counter(r['background']['endpoint_avg'] for r in sub))}; explicit window "
              f"{sum(r['background']['start_idx'] is not None for r in sub)}")
        P = [p for r in sub for p in r["peaks"]]
        print(f"   {k}: Voigt components (gl_ratio, fix_gl_ratio) "
              f"{dict(Counter((p.get('gl_ratio'), p.get('fix_gl_ratio')) for p in P if p['frontend_shape'] == 'Voigt'))}")
        la = [p for p in P if p["shape"] == "la_casaxps"]
        print(f"   {k}: LA components {len(la)}; (linked, fix_m sent, m varied) "
              f"{dict(Counter((p['linked'], p.get('fix_m'), p.get('m_vary')) for p in la))}; fitted m {rng([p.get('m_fitted') for p in la])}; "
              f"below the 1e-3 no-convolution threshold {sum(p['m_fitted'] < 1e-3 for p in la)}; records whose every LA m is below it "
              f"{sum(1 for r in sub if any(p['shape'] == 'la_casaxps' for p in r['peaks']) and all(p['m_fitted'] < 1e-3 for p in r['peaks'] if p['shape'] == 'la_casaxps'))}")
        dsg = [p for p in P if p["shape"] == "ds_g"]
        if dsg:
            print(f"   {k}: DS+G components {len(dsg)}; m_gauss varied {dict(Counter(p.get('m_gauss_vary') for p in dsg))}; "
                  f"fitted m_gauss {rng([p.get('m_gauss_fitted') for p in dsg])}")

all_states = Counter()
ever_unconfirmed, la_all_consistent = set(), None
for name in SETTINGS:
    R = rows(name)
    if not R:
        continue
    all_states.update(r["state"] for r in R)
    print(f"== {name}: {len(R)}; verifying pid(s) of the CLIENT process {sorted({r['pid'] for r in R})}")
    for k in ("committed", "synthetic"):
        sub = [r for r in R if kind(r) == k]
        print(f"   {k}: {dict(Counter((r['state'], r['check']) for r in sub))}")
    bad = [r for r in R if r["state"] != "consistent"]
    ever_unconfirmed |= {r["id"] for r in bad}
    print(f"   not consistent: {len(bad)}; all hold la_casaxps: "
          f"{all('la_casaxps' in by_id[r['id']]['backend_shapes'] for r in bad) if by_id else 'no index'}; "
          f"reason names la_casaxps: {sum('la_casaxps' in (r['reason'] or '') for r in bad)}; checks {dict(Counter(r['check'] for r in bad))}")
    if by_id:
        ev = {}
        for r in R:
            for s in by_id[r["id"]]["backend_shapes"]:
                ev.setdefault(s, Counter())[r["state"]] += 1
        print(f"   records holding each backend lineshape, by verdict: "
              f"{{{', '.join(f'{s}: {dict(c)}' for s, c in sorted(ev.items()))}}}")
        nola = [r for r in R if "la_casaxps" not in by_id[r["id"]]["backend_shapes"]]
        print(f"   records WITHOUT la_casaxps: {len(nola)}, verdicts {dict(Counter(r['state'] for r in nola))}")
        la_ids = {r["id"] for r in R if "la_casaxps" in by_id[r["id"]]["backend_shapes"]}
        ok = {r["id"] for r in R if r["id"] in la_ids and r["state"] == "consistent"}
        la_all_consistent = ok if la_all_consistent is None else la_all_consistent & ok
if all_states:
    print(f"== all verifications: {sum(all_states.values())}; {dict(all_states)}; mismatch {all_states.get('mismatch', 0)}")
    if by_id:
        la_ids = {i for i, r in by_id.items() if "la_casaxps" in r["backend_shapes"]}
        small = {i for i in la_ids if all(p["m_fitted"] < 1e-3 for p in by_id[i]["peaks"] if p["shape"] == "la_casaxps")}
        print(f"   LA records whose every m is below 1e-3 (no convolution): {len(small)}, unconfirmed in any setting: {len(small & ever_unconfirmed)}")
        print(f"   records holding la_casaxps: {len(la_ids)} ({dict(sorted(Counter(kind({'id': i}) for i in la_ids).items()))}); unconfirmed in at least one "
              f"setting: {len(ever_unconfirmed)} ({dict(sorted(Counter(kind({'id': i}) for i in ever_unconfirmed).items()))}); consistent in all four: "
              f"{len(la_all_consistent or ())}")

S = rows("sizes.jsonl")
if S:
    for k in ("committed", "synthetic"):
        sub = [r for r in S if kind(r) == k]
        for f in ("R_bytes", "O_bytes", "R_gzip", "O_gzip"):
            v = [r[f] for r in sub]
            m, n = median(v)
            print(f"== size {f} ({k}): median {m} (n {n}), min {min(v)}, max {max(v)}, total {sum(v)}")
    sub = [r for r in S if kind(r) == "committed"]
    mr, _ = median([r["R_bytes"] + r["O_bytes"] for r in sub])
    mg, _ = median([r["R_gzip"] + r["O_gzip"] for r in sub])
    print(f"   committed R+O per fit: median {mr} raw, {mg} gzip (each gzipped separately); 30 x median: {30 * mr} raw, {30 * mg} gzip")
    print(f"   points per committed fit: median {median([r['n'] for r in sub])}, max {max(r['n'] for r in sub)}; "
          f"components: median {median([r['n_peaks'] for r in sub])}, max {max(r['n_peaks'] for r in sub)}")

B = rows("background_twin.jsonl")
if B:
    for k in ("committed", "synthetic"):
        sub = [b for b in B if kind(b) == k]
        print(f"== background twin {k}: {len(sub)}; window recovered {sum(bool(b['window_recovered']) for b in sub)}; "
              f"converged {sum(bool(b.get('converged')) for b in sub)}; bit-identical {sum(bool(b.get('identical')) for b in sub)}; "
              f"by (method, endpoint_avg, identical) {dict(Counter((b['method'], b.get('n_avg'), b.get('identical')) for b in sub))}; differing "
              f"{[(b['tab'], b['method'], b.get('n_differ'), b.get('max_abs')) for b in sub if b.get('window_recovered') and not b.get('identical')][:10]}")

NUM = re.compile(r"^\s*([\w.\[\]]+): (-?[\d.eE+-]+) vs (-?[\d.eE+-]+)\s*$")
P = rows("replay.jsonl")
if P:
    for k in ("committed", "synthetic"):
        sub = [p for p in P if kind(p) == k]
        print(f"== replay {k}: {len(sub)}; {dict(Counter(p['outcome'] for p in sub))}; equal as sorted JSON once seed_source is "
              f"restored: {sum(bool(p.get('identical')) for p in sub)}; success before/after {dict(Counter((p['success_before'], p['success_after']) for p in sub))}")
        for p in sub:
            if p["outcome"] == "reproduced":
                continue
            lines = [l for l in (p.get("detail") or "").splitlines()[1:] if l.strip()]
            fields = [l.strip().split(":")[0] for l in lines]
            only_starts = all(f.startswith("starts.") for f in fields)
            rel = []
            for l in lines:
                m = NUM.match(l)
                if m:
                    a, b = float(m.group(2)), float(m.group(3))
                    rel.append(f"{m.group(1)} rel {abs(a - b) / max(abs(a), abs(b)):.2e}")
            print(f"   {p['tab']} {p['shapes']}: {'starts evidence only' if only_starts else 'THE FIT differs'}; "
                  f"truncated {len(p.get('detail') or '') >= 400}; {lines}; {rel}")
