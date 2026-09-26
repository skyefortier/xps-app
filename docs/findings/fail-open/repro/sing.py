import sys, numpy as np
sys.path.insert(0, '/Users/skyefortier/xps-app')
import fitting
rng = np.random.default_rng(3)
x = np.arange(295, 279.99, -0.05)
def gl(x, c, w, a, eta=0.3):
    s = w/2.3548; g = np.exp(-(x-c)**2/(2*s*s)); l = 1/(1+((x-c)/(w/2))**2)
    return a*((1-eta)*g + eta*l)
y = rng.poisson(200 + gl(x, 285.0, 1.2, 5000)).astype(float)
def spec(id, c, a, **kw):
    d = dict(id=str(id), name='P'+str(id), center=c, amplitude=a, fwhm=1.2, amplitude_min=0, fix_center=True, fix_fwhm=True,
             fix_amplitude=False, fix_gl_ratio=True, shape='pseudo_voigt_gl', gl_ratio=0.3); d.update(kw); return d
for m in ['least_squares', 'leastsq']:
    r = fitting.run_fit(x, y, [spec(1, 285.0, 2000), spec(2, 285.0, 2000)], background_method='linear', n_perturb=3, fit_kws={'method': m} if False else None)
    print(m, r['success'], r['message'][:60])
    for ip in r['individual_peaks']:
        print('  ', ip['id'], {k: (round(v['value'], 3), v['stderr']) for k, v in ip['params'].items() if k in ('amplitude',)}, ip['support'])
    break
