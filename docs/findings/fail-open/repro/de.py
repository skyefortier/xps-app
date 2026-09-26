import sys,time; sys.path.insert(0,'/Users/skyefortier/xps-app')
import numpy as np, fitting, warnings; warnings.simplefilter('ignore')
x=np.linspace(295,280,151); rng=np.random.default_rng(0)
g=lambda c,a,w: a*np.exp(-4*np.log(2)*((x-c)/w)**2)
y=rng.poisson(g(284.5,3000,1.0)+g(286.2,1000,1.3)+300).astype(float)
S=lambda i,c,a: dict(id=i,shape='pseudo_voigt_gl',center=c,amplitude=a,fwhm=1.2,gl_ratio=0.3,amplitude_min=0)
# case A: anchor is real; case B: anchor is redundant (two components on the same line)
for label,specs in [("real anchor",[S(1,284.5,2000),S(2,286.2,800)]),
                    ("redundant anchor",[S(1,284.5,1500),S(2,286.2,800),S(3,284.55,1500)])]:
    t=time.time()
    r=fitting.run_fit(x,y,specs,'shirley',fit_kws={'method':'differential_evolution'},n_perturb=0,require_component=1)
    print(label,'success',r['success'],'required',{k:r['required'].get(k) for k in ('ran','required','f','refit_converged','reason')},'t=%.1fs'%(time.time()-t))
