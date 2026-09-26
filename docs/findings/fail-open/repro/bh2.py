import sys, time; sys.path.insert(0,'/Users/skyefortier/xps-app')
import numpy as np, fitting, lmfit.minimizer as lm
cap={}
orig=lm.scipy_basinhopping
def spy(*a,**k):
    r=orig(*a,**k); cap.setdefault('lows',[]).append((r.lowest_optimization_result.success, r.lowest_optimization_result.message, getattr(r,'success',None))); return r
lm.scipy_basinhopping=spy
x=np.linspace(295,280,301)
rng=np.random.default_rng(1)
t=lambda c,a,w: a*np.exp(-4*np.log(2)*((x-c)/w)**2)
y=rng.poisson(t(284.5,3000,1.0)+t(286.0,1500,1.3)+t(288.5,500,1.4)+300).astype(float)
specs=[dict(id=i,shape='pseudo_voigt_gl',center=c,amplitude=a,fwhm=1.2,gl_ratio=0.3,amplitude_min=0) for i,(c,a) in enumerate([(284.6,2000),(286.1,1000),(288.4,400)])]
t0=time.time()
r=fitting.run_fit(x,y,specs,'shirley',fit_kws={'method':'basinhopping'},n_perturb=0,require_component=0)
print('run_fit success',r['success'],'redchi',r['statistics']['reduced_chi_square'],'t',round(time.time()-t0,1))
print('scipy lowest-local-result success per call:',cap['lows'])
print('required',r['required'])
