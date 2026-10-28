"""Which binding-energy axis is physically right for the committed VGD files: Avantage's (BE = hν − KE, its chart
sidecars) or the app's VGD reader (BE = 1486.6 − KE − 4.5)? Read-only.

1. Each file's own calibration record (property 981, scripts/vgd_properties.py): the reference lines it was
   calibrated on, and the kinetic energy each implies under BE = hν − KE with the file's own hν (property 105).
2. Where the files' main lines sit on each axis: the apex (highest point) of each high-resolution region, and of
   known lines in each survey within a window that holds that line on BOTH axes (the app's axis is 4.58 eV lower
   everywhere, verified by scripts/noise_counting_time.py and checked again here).
3. The committed projects' charge corrections: the raw position of the line each was referenced to.

    venv/bin/python scripts/vgd_energy_axis_check.py [--json OUT.json] > OUT.txt
"""
import argparse
import collections
import glob
import json
import os
import re
import subprocess
import sys
import zipfile

import numpy as np
import olefile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import vgd_parser  # noqa: E402
import vgd_properties as vp  # noqa: E402

HV = 1486.68                      # the decimal SourceEnergy (105) stores as a float32
APP_OFFSET = (vgd_parser.DEFAULT_PHOTON_ENERGY - vgd_parser.DEFAULT_WORK_FUNCTION) - HV   # app BE − Avantage BE
# survey windows on AVANTAGE's axis, each wide enough that the same line is the window's apex on the app's axis too
# (the window is moved by the offset for the app's axis)
SURVEY_LINES = {"C 1s": (281.0, 292.0), "O 1s": (527.0, 538.0), "Cl 2p": (195.0, 204.0), "U 4f7/2": (376.0, 386.0),
                "N 1s": (394.0, 404.0), "B 1s": (185.0, 196.0)}


def _files():
    out = subprocess.run(["git", "ls-files", "*.VGD"], capture_output=True, text=True, cwd=ROOT).stdout.split("\n")
    return [f for f in out if f]


def avantage_axis(path):
    """Avantage's BE (hν − KE from the file's own start and step, in the app's ascending-BE order), the app reader's
    BE for the same points, and the stored values."""
    with olefile.OleFileIO(os.path.join(ROOT, path)) as ole:
        start, step = vgd_parser._find_ke_axis(ole.openstream("VGSpaceAxes").read())
    be_app, y = vgd_parser.parse_vgd(os.path.join(ROOT, path))
    be_app, y = np.asarray(be_app), np.asarray(y)
    be_av = HV - (start + np.arange(be_app.size) * step)
    if be_av.size > 1 and be_av[0] > be_av[-1]:
        be_av = be_av[::-1]                       # the reader's own ordering (vgd_parser.py: increasing BE)
    return be_av, be_app, y


def apex(be, y, lo, hi):
    m = (be >= lo) & (be <= hi)
    if m.sum() < 3:
        return None
    i = np.argmax(np.where(m, y, -np.inf))
    if i == np.flatnonzero(m)[0] or i == np.flatnonzero(m)[-1]:
        return None                     # the window's edge, not a peak
    return float(be[i])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    files = _files()
    out = {"calibration": collections.Counter(), "offset": set(), "regions": collections.defaultdict(list),
           "survey": collections.defaultdict(list)}
    for f in files:
        P = vp.main_properties(os.path.join(ROOT, f))
        out["calibration"][P[981][1]] += 1
        be_av, be_app, y = avantage_axis(f)
        out["offset"].add(round(float(np.max(np.abs((be_app - be_av) - APP_OFFSET))), 12))
        name = os.path.basename(f)
        sample = f.split("/")[3].split(",")[0] if f.count("/") >= 4 else ""
        if "Survey" in name:
            for line, (lo, hi) in SURVEY_LINES.items():
                av = apex(be_av, y, lo, hi)
                app = apex(be_app, y, lo + APP_OFFSET, hi + APP_OFFSET)
                if av is not None and app is not None:
                    out["survey"][line].append((sample, av, app))
        else:
            region = name.split(" ")[0]
            i = int(np.argmax(y))
            out["regions"][region].append((sample, float(be_av[i]), float(be_app[i])))
    lines = []
    lines.append(f"{len(files)} committed VGD files")
    for cal, n in out["calibration"].items():
        lines.append(f"calibration record (property 981) in {n} files: {cal!r}")
        for m in re.finditer(r"(\w+?)\s*=\s*([0-9.]+)\s*eV", cal):
            be = float(m.group(2))
            lines.append(f"    {m.group(1):6s} BE {be:9.4f} eV  ->  KE under BE = hν − KE (hν {HV}): {HV - be:9.4f} eV")
    lines.append(f"app axis − Avantage axis, every point of every file: {APP_OFFSET:+.6f} eV "
                 f"(largest deviation {max(out['offset']):.2g} eV)")
    q = lambda v: (float(np.min(v)), float(np.median(v)), float(np.max(v)))
    lines.append("apex of each high-resolution region (its highest point), min / median / max, on each axis:")
    for region, rows in sorted(out["regions"].items()):
        av, app = q([r[1] for r in rows]), q([r[2] for r in rows])
        lines.append(f"  {region:6s} {len(rows):3d} files   Avantage {av[0]:7.2f} {av[1]:7.2f} {av[2]:7.2f}   app {app[0]:7.2f} {app[1]:7.2f} {app[2]:7.2f}")
    lines.append("by sample (high-resolution C1s apex, Avantage axis): median [min, max]")
    by = collections.defaultdict(list)
    for s, av, _ in out["regions"].get("C1s", []):
        by[s].append(av)
    for s, v in sorted(by.items()):
        lines.append(f"  {s[:40]:40s} {len(v):3d}  {np.median(v):7.2f} [{min(v):.2f}, {max(v):.2f}]")
    lines.append("survey lines (apex in a window holding the line on both axes), min / median / max:")
    for line, rows in out["survey"].items():
        av, app = q([r[1] for r in rows]), q([r[2] for r in rows])
        lines.append(f"  {line:8s} {len(rows):3d} surveys   Avantage {av[0]:7.1f} {av[1]:7.1f} {av[2]:7.1f}   app {app[0]:7.1f} {app[1]:7.1f} {app[2]:7.1f}")
    # the committed projects' charge corrections: what the reference line's raw position was on the app's axis
    cc = collections.Counter()
    for z in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip"))):
        with zipfile.ZipFile(z) as zf:
            for nm in zf.namelist():
                if not nm.endswith(".json") or nm == "manifest.json":
                    continue
                t = json.loads(zf.read(nm))
                if t.get("isStack") or t.get("ccShift") in (None, 0):
                    continue
                ui = t.get("ui") or {}
                try:
                    obs, lit = float(ui.get("ccObs")), float(ui.get("ccLit"))
                except (TypeError, ValueError):
                    continue
                # the page: shift = observed − reference, corrected BE = raw − shift (getCorrectedBE)
                cc[(str(ui.get("ccMethod")), lit, round(obs, 2), round(obs - APP_OFFSET, 2))] += 1
    lines.append("committed projects' charge corrections: reference line (method, literature eV), its observed raw "
                 "position on the app's axis and the same point on Avantage's axis: tabs")
    for (meth, lit, obs, av), n in sorted(cc.items()):
        lines.append(f"  {meth:10s} {lit:7.2f}   observed app {obs:7.2f}   Avantage {av:7.2f}   ({av - lit:+.2f} from the reference): {n}")
    print("\n".join(lines))
    if a.json:
        json.dump({"calibration": dict(out["calibration"]), "app_offset": APP_OFFSET, "regions": out["regions"],
                   "survey": out["survey"], "charge_corrections": [list(k) + [v] for k, v in cc.items()]},
                  open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
