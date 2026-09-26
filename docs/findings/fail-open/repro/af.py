import sys, numpy as np
sys.path.insert(0, '/Users/skyefortier/xps-app')
import fitting
rng = np.random.default_rng(5)
raw = np.round(np.arange(415, 369.95, -0.1), 3)
g = lambda x, c, w, a: a*np.exp(-(x-c)**2/(2*(w/2.3548)**2))
counts = rng.poisson(1500 + 8*(raw-370) + g(raw, 380.9, 1.8, 9000) + g(raw, 391.8, 1.8, 7000)).astype(float)
shift = 391.8 - 284.5            # findGraphiteRawBE's pick -> provisional shift 107.3 eV
x = np.round(raw - shift, 4)     # corrected frame the page uploads
def sp(id, name, shape, c, w, a, cmin, cmax, wmin, wmax, **kw):
    d = dict(id=str(id), name=name, center=c, amplitude=a, fwhm=w, amplitude_min=0, fix_center=False, fix_fwhm=False,
             fix_amplitude=False, fix_gl_ratio=False, shape=shape, gl_ratio=0.3, center_min=cmin, center_max=cmax, fwhm_min=wmin, fwhm_max=wmax); d.update(kw); return d
H = 7000
specs = [sp(1,'Graphite','asymmetric_gl',284.5,0.7,H,284.2,284.8,0.4,1.2,asymmetry=0.25,asymmetry_min=0.1,asymmetry_max=0.5,fix_asymmetry=False),
         sp(2,'Adventitious 1','pseudo_voigt_gl',284.8,1.4,0.2*H,284.8,285.3,0.8,3.0),
         sp(3,'Adventitious 2','pseudo_voigt_gl',286.2,1.6,0.2*H,285.7,286.7,0.8,3.0),
         sp(4,'Adventitious 3','pseudo_voigt_gl',287.8,1.8,0.2*H,287.3,288.3,0.8,3.5),
         sp(5,'sat','pseudo_voigt_gl',291.0,2.5,0.2*H,290.0,292.0,1.0,4.0),
         sp(6,'Unknown 1','pseudo_voigt_gl',273.6,1.0,0.15*H,272.8,274.4,0.5,3.0)]
n = len(x)
r = fitting.run_fit(x, counts, specs, background_method='shirley', bg_start_idx=0, bg_end_idx=n, n_perturb=3, endpoint_avg=3, require_component='1')
print('success', r['success'], r['message'][:50])
print('required', {k: r['required'][k] for k in ('ran','required','f','refit_converged') if k in r['required']})
for ip in r['individual_peaks']:
    print(ip['id'], round(ip['params']['center']['value'],3), round(ip['params']['amplitude']['value'],1), ip['support']['supported'], None if ip['support']['f'] is None else round(ip['support']['f'],1))
