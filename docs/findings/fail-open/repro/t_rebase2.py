from harness import *
import numpy as np
x=np.round(np.arange(295.0,275.0,-0.1),4); rng=np.random.default_rng(3)
y=rng.poisson(1000+20000*np.exp(-4*np.log(2)*((x-285.0)/1.5)**2)).astype(float)
sid=upload('\n'.join(f'{a:.4f},{b:.2f}' for a,b in zip(x,y)))
ps=[dict(id='1',name='P',center=288.2,amplitude=5000,fwhm=1.5,amplitude_min=0,fix_center=False,fix_fwhm=False,fix_amplitude=False,fix_gl_ratio=True,shape='pseudo_voigt_gl',gl_ratio=0.5)]
for press in range(1,4):
    body={'session_id':sid,'background':{'method':'linear','start_idx':0,'end_idx':len(x),'endpoint_avg':1},'peaks':ps,'fit_method':'least_squares','n_perturb':3,'n_starts':0}
    st,j=post('/api/fit',body); c=j['individual_peaks'][0]['params']['center']
    lo,hi=c['min'],c['max']; at=(c['value']-lo<=0.01*(hi-lo)) or (hi-c['value']<=0.01*(hi-lo))
    print(f"press {press}: start {ps[0]['center']:.3f} window [{lo:.2f},{hi:.2f}] fitted {c['value']:.3f} success {j['success']} redchi {j['statistics']['reduced_chi_square']:.1f} page_at_bound_warning={at}")
    for k in ('center','amplitude','fwhm'): ps[0][k]=j['individual_peaks'][0]['params'][k]['value']
