import sys; sys.path.insert(0,'/Users/skyefortier/xps-app')
import numpy as np, fitting, warnings; warnings.simplefilter('ignore')
x=np.linspace(295,280,151); rng=np.random.default_rng(0)
g=lambda c,a,w: a*np.exp(-4*np.log(2)*((x-c)/w)**2)
y=rng.poisson(g(284.5,3000,1.0)+g(286.2,1000,1.3)+300).astype(float)
def S(i,c,a): return dict(id=i,shape='pseudo_voigt_gl',center=c,amplitude=a,fwhm=1.2,gl_ratio=0.3,amplitude_min=0)
for label,specs,req in [("int 1 + str '1'",[S(1,284.5,2000),S("1",286.2,800)],None),
                        ("'1' + '1_a'",[S("1",284.5,2000),S("1_a",286.2,800)],"1")]:
    try:
        r=fitting.run_fit(x,y,specs,'shirley',fit_kws={'method':'least_squares'},n_perturb=0,require_component=req)
        print(label,'success',r['success'],'required',r['required'])
        for ip in r['individual_peaks']: print('   id',repr(ip['id']),'param keys',sorted(ip['params']))
    except Exception as e: print(label,'raised',type(e).__name__,str(e)[:150])
