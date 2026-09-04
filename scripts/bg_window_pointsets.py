"""Which bg-window points does each side use on the committed real-data projects?
JS preview: all grid points with lo <= BE <= hi (inclusive range).
Backend today: nearest index to each typed boundary, slice [i0:i1) (drops i1).
Backend after 1c: nearest index, slice [i0:i1+1] (inclusive)."""
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
        before = set(range(i0, i1))
        after = set(range(i0, i1 + 1))
        rows.append(dict(proj=zpath.split('/')[-1][:28], tab=d.get('name'), bg=ui.get('bgType'),
                         n=len(be), lo=lo, hi=hi, js=len(js), before=len(before), after=len(after),
                         js_eq_after=(js == after), dropped_be=float(be[i1]), dropped_prev_be=float(be[i1-1]),
                         js_minus_after=sorted(js - after), after_minus_js=sorted(after - js)))
print(f"{'project':28} {'tab':14} {'bg':9} {'n':>4} {'js':>4} {'bef':>4} {'aft':>4} js==aft  dropped-pt BE  extra/missing vs JS")
for r in rows:
    print(f"{r['proj']:28} {str(r['tab'])[:14]:14} {r['bg']:9} {r['n']:4d} {r['js']:4d} {r['before']:4d} {r['after']:4d} {str(r['js_eq_after']):7}  {r['dropped_be']:9.3f}      {r['js_minus_after']} {r['after_minus_js']}")
inside = [r for r in rows if r['lo'] > min(r['lo'], r['hi']) - 1e-9 and (r['js'] < r['n'])]
print('\nTABS:', len(rows), ' js==after:', sum(r['js_eq_after'] for r in rows), ' before-count==js-count:', sum(r['before']==r['js'] for r in rows), ' bg window narrower than ROI (js<n):', sum(r['js']<r['n'] for r in rows))
