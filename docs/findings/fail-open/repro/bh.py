import sys; sys.path.insert(0,'/Users/skyefortier/xps-app')
import numpy as np, fitting
from lmfit import Model
# 1) lmfit basinhopping: success is never read from scipy
x=np.linspace(280,295,301)
rng=np.random.default_rng(0)
y=1000*np.exp(-4*np.log(2)*((x-285)/1.2)**2)+200
y=rng.poisson(y).astype(float)
m=Model(fitting._gaussian)
p=m.make_params(amplitude=10,center=290,fwhm=5)
p['amplitude'].min=0; p['center'].set(min=280,max=295); p['fwhm'].set(min=0.1,max=15)
# cripple local minimiser: maxiter 1 per local minimisation, niter 2
r=m.fit(y-200,p,x=x,method='basinhopping',fit_kws={'niter':1,'minimizer_kwargs':{'method':'L-BFGS-B','options':{'maxiter':1}}})
print('lmfit success=',r.success,'message=',r.message,'redchi=',r.redchi, 'center=',r.params['center'].value)
from scipy.optimize import basinhopping
