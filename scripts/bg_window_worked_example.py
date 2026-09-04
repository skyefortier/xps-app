"""Worked example for Condition 2 (run from the repo root: venv/bin/python scripts/bg_window_worked_example.py [least_squares|leastsq]): refit stored real-data tabs with the background
window as the frontend sends it TODAY (nearest index, end-exclusive) versus AFTER 1c
(inside-range, end-inclusive = exactly the preview's point set)."""
import sys, zipfile, json
import numpy as np
sys.path.insert(0, '.')
import fitting

Z = 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip'

def load_tab(name):
    z = zipfile.ZipFile(Z)
    for n in z.namelist():
        if n.endswith('.json'):
            d = json.loads(z.read(n))
            if isinstance(d, dict) and d.get('name') == name:
                return d
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

def windows(be, ui):
    lo_t, hi_t = float(ui['bgStart']), float(ui['bgEnd'])
    lo, hi = min(lo_t, hi_t), max(lo_t, hi_t)
    i0n, i1n = int(np.argmin(np.abs(be - lo_t))), int(np.argmin(np.abs(be - hi_t)))
    i0n, i1n = min(i0n, i1n), max(i0n, i1n)
    ins = np.where((be >= lo) & (be <= hi))[0]
    return dict(before=(i0n, i1n), naive_plus1=(i0n, i1n + 1), after=(int(ins[0]), int(ins[-1]) + 1))

def run(tab, method):
    d = load_tab(tab); ui = d['ui']
    be = np.array(d["rawBE"], float) - float(d.get("ccShift") or 0)   # getCorrectedBE: raw - ccShift
    y = np.array(d['rawIntensity'], float)
    rmin, rmax = float(ui['roiMin']), float(ui['roiMax'])
    m = (be >= min(rmin, rmax)) & (be <= max(rmin, rmax))
    be, y = be[m], y[m]
    # uploadToBackend sends the session grid as BE.toFixed(4), intensity.toFixed(2)
    be, y = np.round(be, 4), np.round(y, 2)
    specs = [spec_of(p) for p in d['peaks']]
    w = windows(be, ui)
    print(f"\n=== {tab}: bg={ui['bgType']} endpointAvg={ui['endpointAvg']} bgStart={ui['bgStart']} bgEnd={ui['bgEnd']} ROI {rmin}-{rmax} n={len(be)} fit_method={method}")
    for k, (i0, i1) in w.items():
        pts = list(range(i0, i1))
        print(f"  {k:12} indices [{i0}:{i1})  n={len(pts)}  BE {be[i0]:.3f} … {be[i1-1]:.3f}  (endpoint counts {y[i0]:.0f} / {y[i1-1]:.0f})")
    out = {}
    for k, (i0, i1) in w.items():
        r = fitting.run_fit(be, y, specs, background_method=ui['bgType'], bg_start_idx=i0, bg_end_idx=i1,
                            endpoint_avg=int(ui['endpointAvg']), fit_kws={'method': method})
        out[k] = r
    b = out['before']
    names = {str(p['id']): p['name'] for p in d['peaks']}
    for k in out:
        st = out[k]['statistics']
        print(f"  {k:12} success={out[k].get('success')} nfev={st.get('nfev')} χ²ᵣ={st['reduced_chi_square']:.4f}")
    for k in ('naive_plus1', 'after'):
        r = out[k]
        print(f"\n  before → {k}:")
        print(f"    χ²ᵣ  {b['statistics']['reduced_chi_square']:.4f} → {r['statistics']['reduced_chi_square']:.4f}  (Δ {r['statistics']['reduced_chi_square']-b['statistics']['reduced_chi_square']:+.4f})")
        bgb, bga = np.array(b['background_y']), np.array(r['background_y'])
        print(f"    background: max |Δ| {np.max(np.abs(bga-bgb)):.1f} counts, at low-BE edge {abs(bga[-1]-bgb[-1]):.1f}, high-BE edge {abs(bga[0]-bgb[0]):.1f}")
        tot_b = sum(p['params']['area']['value'] for p in b['individual_peaks']); tot_a = sum(p['params']['area']['value'] for p in r['individual_peaks'])
        for pb, pa in zip(b['individual_peaks'], r['individual_peaks']):
            cb, ca = pb['params']['center']['value'], pa['params']['center']['value']
            ab, aa = pb['params']['area']['value'], pa['params']['area']['value']
            print(f"    {names[str(pb['id'])]:12} center {cb:8.3f} → {ca:8.3f} ({(ca-cb)*1000:+6.1f} meV)   area {ab:10.1f} → {aa:10.1f} ({(aa/ab-1)*100:+6.2f} %)   fraction {ab/tot_b*100:6.2f} → {aa/tot_a*100:6.2f} ({(aa/tot_a-ab/tot_b)*100:+5.2f} pp)")

method = sys.argv[1] if len(sys.argv) > 1 else 'least_squares'
run('U4f Scan_0', method)
run('C1s Scan', method)
