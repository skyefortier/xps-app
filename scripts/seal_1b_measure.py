"""Seal 1b (sealed fit record v6, V6.11 1b; option (b)): measure what the seal's states rest on,
on the 202 committed targets.

  record  OUT.jsonl            each target through the REAL /api/fit route, the page's request
                               (full-precision upload, the target's background, Trust-Region,
                               n_perturb 3, n_starts 3 when ≥ 2 unlinked components): R = {request,
                               energies, counts}, O = the reply as JSON — the seal's two records
  record-synthetic OUT.jsonl   the same for SYNTHETIC fits of every lineshape (the committed targets hold
                               no DS, DS+G or Lorentzian component) on every background method
  verify  RECORDS OUT.jsonl [--shake] [--url URL]
                               POST /api/verify-fit for every record in THIS (fresh) process —
                               or against a running server (--url, e.g. a 4-worker gunicorn, so
                               another worker verifies) — state and failed check per record.
                               --shake allocates arrays of random size between verifications: it
                               changes the allocation history (which alignments the evaluators'
                               arrays then receive is not observed).
  replay  RECORDS OUT.jsonl    "Re-run this fit" (V5.4 REPLAY-CHECKED): the recorded request with
                               O's seed as the caller's seed, in this process; the two compared by
                               tests/fit_equality.py (same fit within rounding) — reproduced / a
                               different solution / failed.
  sizes   RECORDS OUT.jsonl    bytes of R and O as JSON, raw and gzip-compressed.
  index   RECORDS OUT.jsonl [TARGETS]
                               one small line per record (the verbatim records are too big to commit):
                               identity, request settings, the lineshape specs the findings rest on
                               (Voigt's mix, LA's and DS+G's m), the fit's χ²ᵣ, the commit and its
                               cleanliness, the software identity's digest, and sha256 digests of the
                               record line and of R and O as JSON (the bytes `sizes` measures);
                               TARGETS adds each target's kind (own / batch).

Every phase is resumable (JSONL keyed by target id).
"""
import gzip
import io
import json
import os
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path[:0] = [ROOT, os.path.join(ROOT, "tests")]
import numpy as np  # noqa: E402

# the committed fit targets AS TODAY'S PAGE SENDS THEM (Codex 1b round 1): built by
# scripts/seal_1b_tabs.py + scripts/optimizer_disagreement_targets.js; its path in SEAL_1B_TARGETS
# — REQUIRED (Codex 1b round 2): no default, so an older target file can never be picked up silently
TARGETS = os.environ.get("SEAL_1B_TARGETS")
if not TARGETS and len(sys.argv) > 1 and sys.argv[1] in ("record", "index"):
    sys.exit("SEAL_1B_TARGETS is not set: give the target file built by scripts/seal_1b_tabs.py + "
             "scripts/optimizer_disagreement_targets.js (see docs/findings/seal-1b/v2/MANIFEST.md)")


def done_ids(out):
    return {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()


def append(out, rec):
    with open(out, "a") as f:
        f.write(json.dumps(rec) + "\n")


def records(path):
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def client():
    import tempfile
    from app import create_app
    app = create_app(upload_folder=tempfile.mkdtemp(prefix="seal1b-"))
    app.config["TESTING"] = True
    return app.test_client()


def page_request(t):
    unlinked = sum(1 for s in t["specs"] if s.get("constrain_to") is None)
    bg = t["background"]
    return {"peaks": t["specs"], "fit_method": "least_squares", "n_perturb": 3,
            "n_starts": 3 if unlinked >= 2 else 0,
            "background": {"method": bg["method"], "start_idx": bg["start_idx"], "end_idx": bg["end_idx"],
                           "endpoint_avg": bg["endpoint_avg"]}}


def record(out):
    c = client()
    T = json.load(open(TARGETS))
    done = done_ids(out)
    for t in T:
        if t["id"] in done:
            continue
        x, y = [float(v) for v in t["be"]], [float(v) for v in t["inten"]]
        csv = "\n".join(f"{a!r},{b!r}" for a, b in zip(x, y))     # what the page uploads: full precision
        sid = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
        req = {"session_id": sid, **page_request(t)}
        r = c.post("/api/fit", json=req)
        rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "shapes": sorted(set(t["shapes"])),
               "status": r.status_code, "R": {"request": req, "energies": x, "counts": y}, "O": r.get_json()}
        append(out, rec)


SHAPES = {"gaussian": {}, "lorentzian": {}, "pseudo_voigt_gl": {"gl_ratio": 0.3},
          "asymmetric_gl": {"gl_ratio": 0.3, "asymmetry": 0.2}, "doniach_sunjic": {"alpha": 0.1, "gamma_asym": 0.0},
          "ds_g": {"alpha": 0.1, "beta": 0.3, "m_gauss": 0.4}, "la_casaxps": {"alpha": 1.2, "beta": 1.0, "m": 6.0}}
BACKGROUNDS = [{"method": "shirley", "endpoint_avg": 3}, {"method": "smart"}, {"method": "tougaard"},
               {"method": "linear"}, {"method": "none"}, {"method": "manual", "manual_bg": [[281.0, 210.0], [292.0, 190.0]]}]


def record_synthetic(out):
    c = client()
    done = done_ids(out)
    for seed in (3, 4, 5):
        rng = np.random.default_rng(seed)
        x = np.arange(280.0, 295.0, 0.05 if seed == 5 else 0.1)
        g = lambda c_, a, w: a * np.exp(-4 * np.log(2) * ((x - c_) / w) ** 2)
        y = rng.poisson(200.0 + g(284.8, 4000.0, 1.1) + g(288.6, 900.0, 1.4)).astype(float)
        for shape, extra in SHAPES.items():
            for k, bg in enumerate(BACKGROUNDS):
                tid = f"syn-{seed}-{shape}-{k}"
                if tid in done:
                    continue
                specs = [{"id": 1, "shape": shape, "center": 284.6, "amplitude": 3500.0, "fwhm": 1.2, "amplitude_min": 0, **extra},
                         {"id": 2, "shape": shape, "center": 288.9, "amplitude": 700.0, "fwhm": 1.2, "amplitude_min": 0, **extra}]
                csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(x, y))
                sid = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
                req = {"session_id": sid, "peaks": specs, "background": bg, "fit_method": "least_squares",
                       "n_perturb": 3, "n_starts": 3}
                r = c.post("/api/fit", json=req)
                append(out, {"id": tid, "project": "synthetic", "tab": tid, "shapes": [shape], "status": r.status_code,
                             "R": {"request": req, "energies": [float(v) for v in x], "counts": [float(v) for v in y]},
                             "O": r.get_json()})


def verify(recs, out, shake=False, url=None):
    c = None if url else client()
    rng = np.random.default_rng(0)
    done = done_ids(out)
    keep = []
    for rec in records(recs):
        if rec["id"] in done or rec["status"] != 200:
            continue
        if shake:
            keep = [np.ones(int(rng.integers(1, 5000))) for _ in range(int(rng.integers(1, 20)))]
        body = {"R": rec["R"], "O": rec["O"]}
        if url:
            req = urllib.request.Request(url.rstrip("/") + "/api/verify-fit", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            v = json.loads(urllib.request.urlopen(req, timeout=120).read())
        else:
            v = c.post("/api/verify-fit", json=body).get_json()
        append(out, {"id": rec["id"], "tab": rec["tab"], "shapes": rec["shapes"], "state": v["state"],
                     "check": v["check"], "reason": v["reason"], "pid": os.getpid(), "shake": shake, "url": url})
    del keep


def replay(recs, out):
    from fit_equality import assert_same_fit
    c = client()
    done = done_ids(out)
    for rec in records(recs):
        if rec["id"] in done or rec["status"] != 200:
            continue
        R, O = rec["R"], rec["O"]
        csv = "\n".join(f"{a!r},{b!r}" for a, b in zip(R["energies"], R["counts"]))
        sid = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
        r = c.post("/api/fit", json={**R["request"], "session_id": sid, "seed": O["random_seed"]})
        O2 = r.get_json()
        if r.status_code != 200:
            outcome, detail = "failed", O2.get("error")
        else:
            # the caller's seed is recorded as such: the one field a replay changes by construction
            a = {k: v for k, v in O.items() if k != "seed_source"}
            b = {k: v for k, v in O2.items() if k != "seed_source"}
            try:
                assert_same_fit(a, b)
                outcome, detail = "reproduced", None
            except AssertionError as exc:
                outcome, detail = "different", str(exc)[:400]
        append(out, {"id": rec["id"], "tab": rec["tab"], "shapes": rec["shapes"], "outcome": outcome,
                     "detail": detail, "identical": json.dumps(O, sort_keys=True) == json.dumps(
                         {**O2, "seed_source": O["seed_source"]}, sort_keys=True) if r.status_code == 200 else False,
                     "success_before": O["success"], "success_after": O2.get("success")})


def sizes(recs, out):
    done = done_ids(out)
    for rec in records(recs):
        if rec["id"] in done or rec["status"] != 200:
            continue
        R, O = json.dumps(rec["R"]).encode(), json.dumps(rec["O"]).encode()
        append(out, {"id": rec["id"], "tab": rec["tab"], "n": len(rec["R"]["energies"]),
                     "n_peaks": len(rec["R"]["request"]["peaks"]), "R_bytes": len(R), "O_bytes": len(O),
                     "R_gzip": len(gzip.compress(R)), "O_gzip": len(gzip.compress(O))})


def index(recs, out, targets=None):
    import hashlib
    kinds = {t["id"]: t.get("kind") for t in json.load(open(targets))} if targets else {}
    sha = lambda b: hashlib.sha256(b).hexdigest()
    with open(recs, "rb") as f, open(out, "w") as w:
        for raw in f:
            raw = raw.rstrip(b"\n")
            rec = json.loads(raw)
            R, O, req = rec["R"], rec["O"], rec["R"]["request"]
            bg = req["background"]
            fitted = {str(ip["id"]): ip["params"] for ip in O.get("individual_peaks") or []}
            peaks = []
            for p in req["peaks"]:
                e = {"frontend_shape": p.get("frontend_shape"), "shape": p["shape"],
                     "linked": p.get("constrain_to") is not None}
                fp = fitted.get(str(p["id"]), {})
                if p.get("frontend_shape") == "Voigt" or p["shape"] == "pseudo_voigt_gl":
                    e.update(gl_ratio=p.get("gl_ratio"), fix_gl_ratio=p.get("fix_gl_ratio"))
                if p["shape"] == "la_casaxps":
                    e.update(m_start=p.get("m"), fix_m=p.get("fix_m"),
                             m_vary=fp.get("m", {}).get("vary"), m_fitted=fp.get("m", {}).get("value"))
                if p["shape"] == "ds_g":
                    e.update(fix_m_gauss=p.get("fix_m_gauss"), m_gauss_vary=fp.get("m_gauss", {}).get("vary"),
                             m_gauss_fitted=fp.get("m_gauss", {}).get("value"))
                peaks.append(e)
            st = O.get("statistics") or {}
            w.write(json.dumps({
                "id": rec["id"], "project": rec["project"], "tab": rec["tab"], "kind": kinds.get(rec["id"]),
                "shapes": rec["shapes"], "backend_shapes": sorted({p["shape"] for p in req["peaks"]}),
                "status": rec["status"], "success": O.get("success"), "n": len(R["energies"]),
                "n_peaks": len(req["peaks"]), "n_free_params": st.get("n_free_params"),
                "reduced_chi_square": st.get("reduced_chi_square"),
                "fit_method": req.get("fit_method"), "n_perturb": req.get("n_perturb"), "n_starts": req.get("n_starts"),
                "background": {"method": bg["method"], "start_idx": bg.get("start_idx"), "end_idx": bg.get("end_idx"),
                               "endpoint_avg": bg.get("endpoint_avg"), "n_anchors": len(bg.get("manual_bg") or [])},
                "peaks": peaks, "random_seed": O.get("random_seed"), "seed_source": O.get("seed_source"),
                "request_digest": O.get("request_digest"),
                # the software identity verification gates on, as a digest (its full text: the run's manifest)
                "software_sha256": sha(json.dumps(O.get("software"), sort_keys=True).encode()),
                "git_commit": (O.get("software") or {}).get("git_commit"),
                "git_dirty": (O.get("software") or {}).get("git_dirty"),
                "line_sha256": sha(raw), "R_sha256": sha(json.dumps(R).encode()), "O_sha256": sha(json.dumps(O).encode()),
            }) + "\n")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "record":
        record(sys.argv[2])
    elif mode == "record-synthetic":
        record_synthetic(sys.argv[2])
    elif mode == "verify":
        url = sys.argv[sys.argv.index("--url") + 1] if "--url" in sys.argv else None
        verify(sys.argv[2], sys.argv[3], shake="--shake" in sys.argv, url=url)
    elif mode == "replay":
        replay(sys.argv[2], sys.argv[3])
    elif mode == "sizes":
        sizes(sys.argv[2], sys.argv[3])
    elif mode == "index":
        index(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    else:
        raise SystemExit(__doc__)
