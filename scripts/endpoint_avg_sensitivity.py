"""Endpoint-averaging default investigation (no code changes).

For each real-data tab and n_avg in {1,3,5,10,20}:
  (a) EDGE SENSITIVITY: refit with the bg window as 1c sends it, then with the
      low-BE edge moved one grid point inward and (where the ROI allows) one
      point outward. Report the max change in per-peak atomic fraction, area
      and chi2r — "two students one pixel apart".
  (b) SLOPE BIAS: the anchor level the background actually uses (mean of the
      first/last cap points) versus the local linear-trend value AT the edge;
      the difference is the bias averaging introduces when the endpoint sits
      on a genuine slope. Reported at both edges.
  (c) POISSON SCATTER (C1s only): 24 seeded Poisson draws of the raw counts,
      refit at the 1c window; std of the graphite fraction and chi2r.
Append-only JSONL; rerun skips finished keys.
Run from the repo root: venv/bin/python scripts/endpoint_avg_sensitivity.py docs/autofit/inventory/endpoint_avg/results.jsonl
Summarize:             venv/bin/python scripts/endpoint_avg_summarize.py docs/autofit/inventory/endpoint_avg/results.jsonl
"""
import sys, json, zipfile, os
import numpy as np
sys.path.insert(0, '.')
import fitting

Z = 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip'
NAVG = [1, 3, 5, 10, 20]
OUT = sys.argv[1]
done = set()
if os.path.exists(OUT):
    for line in open(OUT):
        try: done.add(json.loads(line)['key'])
        except Exception: pass
def emit(rec):
    with open(OUT, 'a') as f: f.write(json.dumps(rec) + '\n')
    done.add(rec['key'])

def load_tab(name):
    z = zipfile.ZipFile(Z)
    for n in z.namelist():
        if n.endswith('.json'):
            d = json.loads(z.read(n))
            if isinstance(d, dict) and d.get('name') == name: return d
    raise KeyError(name)

def spec_of(p):
    s = dict(id=str(p['id']), name=p['name'], center=p['center'], amplitude=p['amplitude'], fwhm=p['fwhm'],
             amplitude_min=0, fix_center=bool(p.get('fixCenter')), fix_fwhm=bool(p.get('fixFwhm')),
             fix_amplitude=bool(p.get('fixAmplitude')), fix_gl_ratio=bool(p.get('fixGlMix')))
    sh = p['shape']
    if sh == 'Voigt': s.update(shape='pseudo_voigt_gl', gl_ratio=0.3)
    elif sh == 'GL': s.update(shape='pseudo_voigt_gl', gl_ratio=p['glMix'] / 100)
    elif sh == 'Gaussian': s.update(shape='gaussian')
    elif sh == 'Lorentzian': s.update(shape='lorentzian')
    elif sh == 'asym-GL': s.update(shape='asymmetric_gl', gl_ratio=(p.get('glMix') or 50) / 100, asymmetry=p.get('asymmetry') or 0, fix_asymmetry=bool(p.get('fixAsymmetry')))
    elif sh == 'LACX': s.update(shape='la_casaxps', alpha=p.get('caAlpha', 1.0), beta=p.get('caBeta', 1.0), m=p.get('caM', 50.0),
                                fix_alpha=bool(p.get('fixCaAlpha')), fix_beta=bool(p.get('fixCaBeta')), fix_m=bool(p.get('fixCaM')))
    else: raise ValueError(sh)
    if p.get('linked'):
        s.update(constrain_to=str(p['linked']), splitting=p['linkOffset'], area_ratio=p['linkRatio'], fix_fwhm=True)
    return s

def prep(tab):
    d = load_tab(tab); ui = d['ui']
    be = np.array(d['rawBE'], float) - float(d.get('ccShift') or 0)
    y = np.array(d['rawIntensity'], float)
    rmin, rmax = float(ui['roiMin']), float(ui['roiMax'])
    m = (be >= min(rmin, rmax)) & (be <= max(rmin, rmax))
    be, y = np.round(be[m], 4), np.round(y[m], 2)
    lo_t, hi_t = float(ui['bgStart']), float(ui['bgEnd']); lo, hi = min(lo_t, hi_t), max(lo_t, hi_t)
    ins = np.where((be >= lo) & (be <= hi))[0]; j0, j1 = int(ins[0]), int(ins[-1])
    names = {str(p['id']): p['name'] for p in d['peaks']}
    return be, y, [spec_of(p) for p in d['peaks']], ui, j0, j1, names

def summarize(r, names):
    tot = sum(p['params']['area']['value'] for p in r['individual_peaks'])
    peaks = {names[str(p['id'])]: dict(center=p['params']['center']['value'], area=p['params']['area']['value'],
             frac=100 * p['params']['area']['value'] / tot if tot else float('nan')) for p in r['individual_peaks']}
    bg = r['background_y']
    return dict(chi2r=r['statistics']['reduced_chi_square'], success=bool(r.get('success')), peaks=peaks,
                bg_edge_hi=bg[0], bg_edge_lo=bg[-1])

def fit(be, y, specs, ui, i0, i1, navg):
    r = fitting.run_fit(be, y, specs, background_method=ui['bgType'], bg_start_idx=i0, bg_end_idx=i1,
                        endpoint_avg=navg, fit_kws={'method': 'least_squares'})
    return r

for tab in ['C1s Scan', 'U4f Scan_0']:
    be, y, specs, ui, j0, j1, names = prep(tab)
    n = len(be)
    variants = {'1c': (j0, j1 + 1), 'edge_in_1': (j0, j1), 'edge_in_2': (j0, j1 - 1)}
    if j1 + 2 <= n: variants['edge_out_1'] = (j0, j1 + 2)
    for navg in NAVG:
        for vname, (i0, i1) in variants.items():
            key = f'edge|{tab}|{navg}|{vname}'
            if key in done: continue
            r = fit(be, y, specs, ui, i0, i1, navg)
            emit(dict(key=key, kind='edge', tab=tab, navg=navg, variant=vname, i0=i0, i1=i1, bg=ui['bgType'], **summarize(r, names)))
            print(key, flush=True)
    # slope bias at both edges, per n_avg (window = 1c)
    yw = y[j0:j1 + 1]; xw = be[j0:j1 + 1]
    for navg in NAVG:
        key = f'bias|{tab}|{navg}'
        if key in done: continue
        cap = min(navg, len(yw) // 4) if navg > 1 else 1
        rec = dict(key=key, kind='bias', tab=tab, navg=navg, cap=cap)
        for edge, sl in (('hi', slice(0, 20)), ('lo', slice(-20, None))):
            xs, ys = xw[sl], yw[sl]
            slope, icpt = np.polyfit(xs, ys, 1)          # local linear trend over 20 pts
            x_edge = xw[0] if edge == 'hi' else xw[-1]
            trend_at_edge = slope * x_edge + icpt
            anchor = float(np.mean(yw[:cap])) if edge == 'hi' else float(np.mean(yw[-cap:]))
            raw_edge = float(yw[0] if edge == 'hi' else yw[-1])
            resid_sd = float(np.std(ys - (slope * xs + icpt)))
            rec[edge] = dict(slope_counts_per_pt=float(slope * abs(xw[1] - xw[0])), trend_at_edge=float(trend_at_edge),
                             raw_edge=raw_edge, anchor=anchor, bias_vs_trend=anchor - float(trend_at_edge),
                             noise_sd_local=resid_sd, expected_bias=float(slope * abs(xw[1]-xw[0])) * (cap - 1) / 2 * (1 if edge == 'hi' else -1))
        emit(rec); print(key, flush=True)

# Poisson scatter on the C1s tab
be, y, specs, ui, j0, j1, names = prep('C1s Scan')
rng = np.random.default_rng(20260903)
draws = [rng.poisson(np.clip(y, 0, None)).astype(float) for _ in range(24)]
for navg in NAVG:
    for k, yd in enumerate(draws):
        key = f'noise|C1s Scan|{navg}|{k}'
        if key in done: continue
        r = fit(be, yd, specs, ui, j0, j1 + 1, navg)
        emit(dict(key=key, kind='noise', tab='C1s Scan', navg=navg, draw=k, **summarize(r, names)))
        print(key, flush=True)
print('ALL DONE', flush=True)
