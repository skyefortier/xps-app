import sys; sys.path.insert(0,'/Users/skyefortier/xps-app')
import numpy as np, fitting
x=np.array([288.,287.,286.,285.,284.,283.])
y=np.array([110.,180.,400.,900.,300.,105.])
specs=[dict(id=1,shape='pseudo_voigt_gl',center=285,amplitude=800,fwhm=1.2,gl_ratio=0.3,amplitude_min=0),
       dict(id=2,shape='pseudo_voigt_gl',center=286,amplitude=300,fwhm=1.2,gl_ratio=0.3,amplitude_min=0)]
for meth in ('least_squares','leastsq'):
    try:
        r=fitting.run_fit(x,y,specs,'linear',fit_kws={'method':meth},n_perturb=3,n_starts=3,require_component=1)
        s=r['statistics']
        print(meth,'success',r['success'],'n_data',s['n_data'],'n_free',s['n_free_params'],'chi2',s['chi_square'],'redchi',s['reduced_chi_square'])
        print('  support',[ip['support'] for ip in r['individual_peaks']])
        print('  required',r['required']); print('  starts', {k:r['starts'].get(k) for k in ('ran','n_converged','n_same_as_fit','reason')})
    except Exception as e: print(meth,'raised',type(e).__name__,e)
import json
r=fitting.run_fit(x,y,specs,'linear',fit_kws={'method':'least_squares'},n_perturb=3,n_starts=3,require_component=1)
print('6-pt response has NaN token:', 'NaN' in json.dumps(r))
# same 6 points, ONE peak (4 free params, dof 2) vs 2 peaks w/ locked widths+mix (6 free, dof 0)
s2=[dict(sp, fix_fwhm=True, fix_gl_ratio=True) for sp in specs]
r2=fitting.run_fit(x,y,s2,'linear',fit_kws={'method':'least_squares'},n_perturb=3,require_component=1)
print('6 pts, 4 free (dof 2): redchi',r2['statistics']['reduced_chi_square'],'NaN in json:', 'NaN' in json.dumps(r2))
