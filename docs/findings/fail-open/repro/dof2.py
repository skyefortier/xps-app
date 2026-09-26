import sys; sys.path.insert(0,'/Users/skyefortier/xps-app')
import numpy as np, fitting, warnings; warnings.simplefilter('ignore')
x=np.arange(295.,279.,-1.0)            # 1 eV step C 1s window, 16 points
rng=np.random.default_rng(3)
g=lambda c,a,w: a*np.exp(-4*np.log(2)*((x-c)/w)**2)
y=rng.poisson(g(284.8,5000,1.6)+g(286.4,1200,1.8)+800).astype(float)   # NO graphite line at 284.5 distinct from AdvC
specs=[dict(id=10,shape='asymmetric_gl',center=284.5,center_min=284.2,center_max=284.8,amplitude=3000,fwhm=0.9,asymmetry=0.2,gl_ratio=0.3,amplitude_min=0)]
for i,(c,w) in enumerate([(284.8,1.4),(286.2,1.6),(287.8,1.8),(291.0,2.5)]):
    specs.append(dict(id=11+i,shape='pseudo_voigt_gl',center=c,amplitude=500,fwhm=w,gl_ratio=0.3,amplitude_min=0))
r=fitting.run_fit(x,y,specs,'shirley',fit_kws={'method':'least_squares'},n_perturb=3,require_component='10')
s=r['statistics']
print('success',r['success'],'n_data',s['n_data'],'n_free',s['n_free_params'],'redchi',s['reduced_chi_square'])
for ip in r['individual_peaks']: print(' ',ip['id'],'center %.3f'%ip['params']['center']['value'],'amp %.1f'%ip['params']['amplitude']['value'],ip['support'])
print('required',r['required'])
import json
txt=json.dumps(r); print('16-pt response has NaN token:', 'NaN' in txt, ' Infinity:', 'Infinity' in txt)
