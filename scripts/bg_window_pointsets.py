"""Which bg-window points does each side use on the committed real-data projects?

Preview (computeBackgroundCore, unchanged by 1c): all ROI grid points with
lo <= BE <= hi (inside-range, inclusive).
Three candidate request rules are compared against that preview set:
  today       : nearest grid index to each typed bound, backend slice [i0:i1)
  nearest+1   : nearest grid index, slice [i0:i1+1]   (the memo-v4 wording; REJECTED)
  1c          : inside-range inclusive indices, slice [i0:i1+1]  (what _bgWindowIndices does)
Run from the repo root:  venv/bin/python scripts/bg_window_pointsets.py
Reported in the sealed-fit-record memo, round-5 amendment (Condition 2)."""
import sys, zipfile, json, glob
import numpy as np

def nearest(be, v):
    return int(np.argmin(np.abs(be - v)))

rows = []
for zpath in sorted(glob.glob('docs/autofit/test_data/*.proj.zip')):
    z = zipfile.ZipFile(zpath)
    for n in z.namelist():
        if not n.endswith('.json'): continue
        d = json.loads(z.read(n))
        if not isinstance(d, dict) or 'rawBE' not in d: continue
        ui = d.get('ui', {})
        try:
            lo_t, hi_t = float(ui['bgStart']), float(ui['bgEnd'])
            rmin, rmax = float(ui['roiMin']), float(ui['roiMax'])
        except (KeyError, ValueError, TypeError):
            continue
        if ui.get('bgType') in ('manual', 'none', None): continue
        be = np.array(d["rawBE"], float) - float(d.get("ccShift") or 0)   # getCorrectedBE: raw - ccShift
        # ROI slice as the app does it (inclusive on the nearest ROI indices)
        be = be[(be >= min(rmin, rmax)) & (be <= max(rmin, rmax))]   # getROIData: inside-range
        lo, hi = min(lo_t, hi_t), max(lo_t, hi_t)
        js = set(np.where((be >= lo) & (be <= hi))[0].tolist())
        i0, i1 = nearest(be, lo_t), nearest(be, hi_t)
        i0, i1 = min(i0, i1), max(i0, i1)
        today = set(range(i0, i1))
        nearest_plus1 = set(range(i0, i1 + 1))
        # _bgWindowIndices: first/last inside-range index; < 2 points -> full range
        inside = np.where((be >= lo) & (be <= hi))[0]
        if len(inside) < 2:
            j0, j1 = 0, len(be) - 1
        else:
            j0, j1 = int(inside[0]), int(inside[-1])
        after_1c = set(range(j0, j1 + 1))
        rows.append(dict(proj=zpath.split('/')[-1][:28], tab=d.get('name'), bg=ui.get('bgType'),
                         n=len(be), lo=lo, hi=hi, js=len(js), today=len(today), np1=len(nearest_plus1), c1=len(after_1c),
                         js_eq_today=(js == today), js_eq_np1=(js == nearest_plus1), js_eq_1c=(js == after_1c),
                         dropped_be=float(be[i1]), np1_extra=sorted(nearest_plus1 - js)))
print(f"{'project':28} {'tab':14} {'bg':9} {'n':>4} {'prev':>4} {'today':>5} {'np+1':>4} {'1c':>4}  ==prev: today np+1 1c   nearest-pt BE  np+1 extra idx vs preview")
for r in rows:
    print(f"{r['proj']:28} {str(r['tab'])[:14]:14} {r['bg']:9} {r['n']:4d} {r['js']:4d} {r['today']:5d} {r['np1']:4d} {r['c1']:4d}  {str(r['js_eq_today'])[0]:>12} {str(r['js_eq_np1'])[0]:>4} {str(r['js_eq_1c'])[0]:>2}   {r['dropped_be']:9.3f}      {r['np1_extra']}")
n = len(rows)
print(f"\nTABS: {n}   preview == request point set —  today: {sum(r['js_eq_today'] for r in rows)}/{n}   nearest+1: {sum(r['js_eq_np1'] for r in rows)}/{n}   1c inside-range: {sum(r['js_eq_1c'] for r in rows)}/{n}")
print(f"bg window narrower than ROI: {sum(r['js']<r['n'] for r in rows)}/{n}")
