"""Seal 1c step 8 (plan §10, "larger saves"): how much a project grows when its fits are sealed.

Loads each committed project (docs/autofit/test_data/*.proj.zip, saved by main-era pages) into the page served at
--url, presses Run Fit on every spectrum tab that has a model (the page's default method), waits for each fit's
own check, saves the project, and reports per project: the committed file's bytes, the re-save's bytes (both as
the page writes them: a ZIP of five tabs or more, else JSON), and per tab the seal's JSON bytes, raw and gzipped.
A tab whose Run Fit is refused or fails is reported, and keeps whatever it had.

    venv/bin/python scripts/seal_1c_save_size.py --url http://127.0.0.1:PORT [--json OUT]
"""
import argparse
import base64
import glob
import gzip
import io
import json
import os
import zipfile

from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(__file__), "..")
LOAD = """async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
  await _loadZipProject(new File([b], name)); }"""
FIT_ALL = """async () => {
  const out = [];
  for (const t of tabManager.tabs.filter(x => !x.isStack && x.peaks && x.peaks.length)) {
    tabManager.activateTab(t.id);
    let err = null;
    try { await runFit(); } catch (e) { err = String(e); }
    for (let k = 0; k < 1200 && _sealAttempts.has(t); k++) await new Promise(r => setTimeout(r, 50));
    const fr = state.fitResult, seal = fr && fr.seal;
    out.push({ tab: t.name, sealed: !!seal, state: seal ? sealedState(fr, t).state : null, err,
               seal: seal ? JSON.stringify(seal) : null });
  }
  return out; }"""
SAVE = """async () => { let out = null; const o = window._downloadBlob;
  window._downloadBlob = async (blob, name) => { out = { name, b: Array.from(new Uint8Array(await blob.arrayBuffer())) }; };
  document.getElementById('save-fname').value = 'p'; await _doSaveProject();
  for (let k = 0; k < 400 && out === null; k++) await new Promise(r => setTimeout(r, 25));
  window._downloadBlob = o; return out; }"""


def _content(name, b):
    """The project's content bytes, uncompressed (a ZIP's members summed; JSON as it is): comparable across formats."""
    if name.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            return sum(i.file_size for i in z.infolist())
    return len(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip")))
    rows = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for f in files:
            raw = open(f, "rb").read()
            pg = br.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(a.url + "/", wait_until="load")
            pg.evaluate(LOAD, [base64.b64encode(raw).decode(), os.path.basename(f)])
            pg.wait_for_timeout(500)
            tabs = pg.evaluate(FIT_ALL)
            saved = pg.evaluate(SAVE)
            pg.close()
            out = bytes(saved["b"])
            rows.append({"project": os.path.basename(f), "committed_bytes": len(raw), "resaved_name": saved["name"],
                         "resaved_bytes": len(out), "committed_content": _content(f, raw),
                         "resaved_content": _content(saved["name"], out), "page_errors": errors,
                         "tabs": [{"tab": t["tab"], "sealed": t["sealed"], "state": t["state"], "err": t["err"],
                                   "seal_bytes": len(t["seal"].encode()) if t["seal"] else 0,
                                   "seal_gzip_bytes": len(gzip.compress(t["seal"].encode())) if t["seal"] else 0} for t in tabs]})
            r = rows[-1]
            ok = [t for t in r["tabs"] if t["sealed"]]
            print(f"{r['project']}: committed {r['committed_bytes']:,} B -> re-saved {r['resaved_bytes']:,} B ({r['resaved_name']}); "
                  f"content {r['committed_content']:,} -> {r['resaved_content']:,} B; "
                  f"{len(ok)}/{len(r['tabs'])} tabs sealed ({', '.join(sorted({t['state'] for t in ok}))}); "
                  f"seal median {sorted(t['seal_bytes'] for t in ok)[len(ok) // 2] if ok else 0:,} B raw, "
                  f"{sorted(t['seal_gzip_bytes'] for t in ok)[len(ok) // 2] if ok else 0:,} B gzip" + (f"; PAGE ERRORS {errors}" if errors else ""))
            for t in r["tabs"]:
                if not t["sealed"]:
                    print(f"    not sealed: {t['tab']} ({t['err'] or 'no fit'})")
        br.close()
    allt = [t for r in rows for t in r["tabs"] if t["sealed"]]
    tot_c, tot_r = sum(r["committed_bytes"] for r in rows), sum(r["resaved_bytes"] for r in rows)
    cc, cr = sum(r["committed_content"] for r in rows), sum(r["resaved_content"] for r in rows)
    print(f"total: files {tot_c:,} B -> {tot_r:,} B (x{tot_r / tot_c:.2f}); content {cc:,} -> {cr:,} B (x{cr / cc:.2f}); {len(allt)} seals, "
          f"max {max(t['seal_bytes'] for t in allt):,} B raw / {max(t['seal_gzip_bytes'] for t in allt):,} B gzip")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()
