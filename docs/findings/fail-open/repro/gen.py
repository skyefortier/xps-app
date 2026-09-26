import sys, json, numpy as np
sys.path.insert(0, '/Users/skyefortier/xps-app')
import fitting
rng = np.random.default_rng(1)
x = np.arange(295, 279.99, -0.05)
def gl(x, c, w, a, eta=0.3):
    s = w/2.3548; g = np.exp(-(x-c)**2/(2*s*s)); l = 1/(1+((x-c)/(w/2))**2)
    return a*((1-eta)*g + eta*l)
def ds(x,c,w,a,al):
    # crude asym
    dx = c-x
    return a*np.where(dx<0, 1/(1+(dx/(w/2))**2)**(1-al*1.9), 1/(1+(dx/(w/2))**2))
base = 200 + 20*(x-280)
out = {}
def spec(id, shape, center, fwhm, amp, **kw):
    d = dict(id=str(id), name='P'+str(id), center=center, amplitude=amp, fwhm=fwhm, amplitude_min=0,
             fix_center=False, fix_fwhm=False, fix_amplitude=False, fix_gl_ratio=False, shape=shape)
    d.update(kw); return d
# Scenario A: GL main line at 285.5; start centre 283.0 -> pinned at upper bound 285.0.
yA = rng.poisson(base + gl(x, 285.5, 1.2, 5000)).astype(float)
rA = fitting.run_fit(x, yA, [spec(1,'pseudo_voigt_gl',283.0,1.2,4000,gl_ratio=0.3)], background_method='linear', n_perturb=3)
out['A_center_at_bound'] = rA
# Scenario B: two GL, second placed where nothing is (amp->0), plus a very narrow spike line fwhm -> floor
yB = rng.poisson(base + gl(x, 285.0, 1.2, 5000)).astype(float)
rB = fitting.run_fit(x, yB, [spec(1,'pseudo_voigt_gl',285.0,1.2,4000,gl_ratio=0.3), spec(2,'pseudo_voigt_gl',290.0,1.0,500,gl_ratio=0.3)], background_method='linear', n_perturb=3)
out['B_amp_to_zero'] = rB
# Scenario C: DS+G line; DS with strong asymmetry -> alpha upper bound
yC = rng.poisson(base + ds(x, 284.5, 0.8, 8000, 0.45)).astype(float)
rC = fitting.run_fit(x, yC, [spec(1,'doniach_sunjic',284.5,0.8,8000,alpha=0.1,gamma_asym=0.0)], background_method='linear', n_perturb=3)
out['C_ds'] = rC
rD = fitting.run_fit(x, yC, [spec(1,'ds_g',284.5,0.8,8000,alpha=0.1,beta=0.3,m_gauss=0.4)], background_method='linear', n_perturb=3)
out['D_dsg'] = rD
# Scenario E: GL with true eta ~ 0 (pure Gauss) -> gl_ratio at lower bound
def g(x,c,w,a): s=w/2.3548; return a*np.exp(-(x-c)**2/(2*s*s))
yE = rng.poisson(base + g(x, 285.0, 1.2, 5000)).astype(float)
rE = fitting.run_fit(x, yE, [spec(1,'pseudo_voigt_gl',285.0,1.2,4000,gl_ratio=0.3)], background_method='linear', n_perturb=3)
out['E_glratio'] = rE
# LACX
rF = fitting.run_fit(x, yC, [spec(1,'la_casaxps',284.5,0.8,8000,alpha=1.0,beta=1.0,m=50.0,fix_m=False)], background_method='linear', n_perturb=3)
out['F_lacx'] = rF
slim = {}
for k, r in out.items():
    slim[k] = {'success': r['success'], 'individual_peaks': [{'id': ip['id'], 'params': ip['params'], 'support': ip.get('support')} for ip in r['individual_peaks']],
               'statistics': r['statistics']}
    print(k, r['success'])
    for ip in r['individual_peaks']:
        print('  ', ip['id'], {n: (round(v['value'],4), v.get('min'), v.get('max'), v.get('vary'), None if v.get('stderr') is None else round(v['stderr'],5)) for n, v in ip['params'].items() if n!='area'}, ip.get('support'))
json.dump(slim, open('fits.json','w'))
