"""The legacy census (seal 1c step 7, plan §11): every committed saved fit loads LEGACY and re-saves as main does.

Loads each committed project (docs/autofit/test_data/*.proj.zip) through the real page of TWO running servers —
this branch and main — and re-saves it. Per spectrum tab with a saved fit it reports whether the branch installed a
seal (never), the branch's state for it (LEGACY, or no fit when the legacy restore dropped it), main's and the
branch's restore verdict (kept / dropped), and every field of the re-saved tab record that differs between the two
saves. The only differences the seal introduces are new fields (`provenance`, the record a dropped legacy fit keeps,
V6.8; `ui.fitMethod`, §8.5); anything else is a regression of the legacy path.

    venv/bin/python scripts/seal_legacy_census.py --branch http://127.0.0.1:PORT --main http://127.0.0.1:PORT2 [--json OUT]

Start each server from its own checkout (gunicorn 'app:create_app()' -b 127.0.0.1:PORT).
"""
import argparse
import base64
import glob
import io
import json
import os
import zipfile

from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(__file__), "..")
NEW_FIELDS = {"provenance"}            # tab-record fields the seal release adds
NEW_UI_FIELDS = {"fitMethod"}

LOAD = """async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
  await _loadZipProject(new File([b], name)); }"""
SAVE = """async () => { let out = null; const o = window._downloadBlob;
  window._downloadBlob = async (blob, name) => { out = { name, b: Array.from(new Uint8Array(await blob.arrayBuffer())) }; };
  document.getElementById('save-fname').value = 'p'; await _doSaveProject();
  for (let k = 0; k < 400 && out === null; k++) await new Promise(r => setTimeout(r, 25));
  window._downloadBlob = o; return out; }"""
TABS = """(names) => tabManager.tabs.filter(t => !t.isStack && names.includes(t.name)).map(t => {
  const fr = t === _activeTab() ? state.fitResult : t.fitResult;
  return { name: t.name, kept: !!fr, sealed: !!(fr && Object.hasOwn(fr, 'seal')),
           state: (fr && typeof sealedState === 'function') ? sealedState(fr, t).state : null }; })"""


def _tabs_of_zip(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        m = json.loads(z.read("manifest.json"))
        return [json.loads(z.read(s["filename"])) for s in m.get("spectra", [])]


def _saved_tabs(saved):
    raw = bytes(saved["b"])
    return _tabs_of_zip(raw) if saved["name"].endswith(".zip") else json.loads(raw.decode())["tabs"]


def _run(base, f, names, b64, pw):
    br = pw.chromium.launch()
    try:
        pg = br.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(base + "/", wait_until="load")
        pg.evaluate(LOAD, [b64, os.path.basename(f)])
        pg.wait_for_timeout(500)
        tabs = pg.evaluate(TABS, names)
        saved = _saved_tabs(pg.evaluate(SAVE))
        return tabs, saved, errors
    finally:
        br.close()


def _diff(a, b, path=""):
    """Paths at which two JSON values differ (dict keys recursively; lists and scalars compared whole)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            out += _diff(a.get(k, "<absent>"), b.get(k, "<absent>"), f"{path}.{k}" if path else k)
        return out
    return [] if a == b else [path]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", required=True)
    ap.add_argument("--main", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip")))
    rows, problems = [], []
    with sync_playwright() as pw:
        for f in files:
            with open(f, "rb") as fh:
                raw = fh.read()
            orig = _tabs_of_zip(raw)
            names = sorted(t.get("name") for t in orig if not t.get("isStack") and t.get("fitResult"))
            if not names:
                continue
            b64 = base64.b64encode(raw).decode()
            bt, bs, be = _run(a.branch, f, names, b64, pw)
            mt, ms, me = _run(a.main, f, names, b64, pw)
            if be or me:
                problems.append({"project": os.path.basename(f), "branch_errors": be, "main_errors": me})
            bsav = {t.get("name"): t for t in bs if not t.get("isStack")}
            msav = {t.get("name"): t for t in ms if not t.get("isStack")}
            mk = {t["name"]: t for t in mt}
            for t in bt:
                d = _diff(msav.get(t["name"], {}), bsav.get(t["name"], {}))
                new = [p for p in d if p.split(".")[0] in NEW_FIELDS or (p.startswith("ui.") and p[3:] in NEW_UI_FIELDS)]
                other = [p for p in d if p not in new]
                rows.append({"project": os.path.basename(f), "tab": t["name"], "sealed": t["sealed"], "state": t["state"],
                             "kept_branch": t["kept"], "kept_main": mk.get(t["name"], {}).get("kept"),
                             "provenance_kept": (bsav.get(t["name"]) or {}).get("provenance") is not None,
                             "new_fields": new, "other_differences": other})
    n = len(rows)
    sealed = sum(r["sealed"] for r in rows)
    legacy = sum(1 for r in rows if r["state"] == "legacy")
    dropped = sum(1 for r in rows if not r["kept_branch"])
    same_verdict = sum(1 for r in rows if r["kept_branch"] == r["kept_main"])
    clean = sum(1 for r in rows if not r["other_differences"])
    print(f"{len(files)} projects, {n} spectrum tabs with a saved fit")
    print(f"  sealed on load: {sealed}   LEGACY: {legacy}   dropped to peaks only: {dropped}   (LEGACY + dropped = {legacy + dropped})")
    print(f"  restore verdict as main's: {same_verdict} / {n}")
    print(f"  dropped fits whose record is kept as provenance: {sum(1 for r in rows if not r['kept_branch'] and r['provenance_kept'])} / {dropped}"
          f"   (a restored fit saves provenance null: {sum(1 for r in rows if r['kept_branch'] and not r['provenance_kept'])} / {n - dropped})")
    print(f"  re-save identical to main's but for the new fields: {clean} / {n}")
    newc = {}
    for r in rows:
        for p in r["new_fields"]:
            newc[p] = newc.get(p, 0) + 1
    for p, c in sorted(newc.items()):
        print(f"    new field {p}: {c} tabs")
    for r in rows:
        if r["other_differences"] or r["sealed"] or r["kept_branch"] != r["kept_main"]:
            print(f"  DIFFERS {r['project']} / {r['tab']}: {r['other_differences'][:8]}")
    for p in problems:
        print(f"  PAGE ERRORS {p}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump({"rows": rows, "problems": problems}, fh, indent=1)


if __name__ == "__main__":
    main()
