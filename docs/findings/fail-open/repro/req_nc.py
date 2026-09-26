import sys; sys.path.insert(0,'/Users/skyefortier/xps-app')
import numpy as np, fitting, warnings; warnings.simplefilter('ignore')
from lmfit import Model
x=np.linspace(295,280,151); rng=np.random.default_rng(0)
g=lambda c,a,w: a*np.exp(-4*np.log(2)*((x-c)/w)**2)
y=rng.poisson(g(284.5,3000,1.0)+g(286.2,1000,1.3)+300).astype(float)
S=lambda i,c,a: dict(id=i,shape='pseudo_voigt_gl',center=c,amplitude=a,fwhm=1.2,gl_ratio=0.3,amplitude_min=0)
specs=[S(1,284.5,1500),S(2,286.2,800),S(3,284.55,1500)]   # 1 and 3 share one line: 1 is redundant
full=fitting.run_fit(x,y,specs,'shirley',fit_kws={'method':'least_squares'},n_perturb=0,require_component=1)
print('normal run          :',{k:full['required'][k] for k in ('required','f','refit_converged')})
# same check, but the reduced refit stops early (budget) -> not converged
orig=fitting._component_required
def crippled(fit_reduced, *a, **k):
    return orig(lambda p: fit_reduced.__closure__ and _early(p), *a, **k)
bg=np.array(full['background_y']); ysub=y-bg; w=1/np.sqrt(np.maximum(y,1))
m2=Model(fitting._pseudo_voigt_gl,prefix='p2_'); m3=Model(fitting._pseudo_voigt_gl,prefix='p3_'); red=m2+m3
def _early(p): return red.fit(ysub,p,x=x,weights=w,method='least_squares',max_nfev=4)
# rebuild full result params via a direct fit to feed the check
from lmfit import Parameters
fm=Model(fitting._pseudo_voigt_gl,prefix='p1_')+m2+m3
P=Parameters()
for ip in full['individual_peaks']:
    for k,v in ip['params'].items():
        if k=='area': continue
        P.add(f"p{ip['id']}_{k}",value=v['value'],min=v['min'] if v['min'] is not None else -np.inf,max=v['max'] if v['max'] is not None else np.inf)
res=orig(_early,P,['p1_'],ysub,w,full['statistics']['chi_square'],4,12)
print('refit stopped early :',{k:res[k] for k in ('required','f','refit_converged')})
