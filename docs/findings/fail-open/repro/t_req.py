import sys, json, numpy as np, warnings, time
warnings.filterwarnings('ignore')
sys.path.insert(0,'/Users/skyefortier/xps-app')
import fitting
F=fitting._SHAPE_FUNCS
x=np.round(np.arange(280.0,295.0001,0.05),4)
def agl(a,c,w): return F['asymmetric_gl'](x,amplitude=a,center=c,fwhm=w,gl_ratio=0.3,asymmetry=0.25)
def gl(a,c,w): return F['pseudo_voigt_gl'](x,amplitude=a,center=c,fwhm=w,gl_ratio=0.3)
rng=np.random.default_rng(0)
y=np.round(rng.poisson(1500+agl(86000,284.5,0.7)+gl(17000,285.3,0.8)+gl(17000,286.2,0.8)+gl(17000,287.8,0.8)+gl(17000,291.0,1.0)).astype(float),2)
def spec(i,name,shape,c,w,a,cmin,cmax,fmin,fmax,**kw):
    s=dict(id=str(i),name=name,center=c,amplitude=a,fwhm=w,amplitude_min=0,fix_center=False,fix_fwhm=False,fix_amplitude=False,fix_gl_ratio=False,shape=shape,gl_ratio=0.3,center_min=cmin,center_max=cmax,fwhm_min=fmin,fwhm_max=fmax); s.update(kw); return s
H=80000
peaks=[spec(1,'Graphite','asymmetric_gl',284.5,0.7,H,284.2,284.8,0.4,1.2,asymmetry=0.25,fix_asymmetry=False,asymmetry_min=0.1,asymmetry_max=0.5),
 spec(2,'Adv1','pseudo_voigt_gl',284.8,1.4,0.2*H,284.8,285.3,0.8,3.0),
 spec(3,'Adv2','pseudo_voigt_gl',286.2,1.6,0.2*H,285.7,286.7,0.8,3.0),
 spec(4,'Adv3','pseudo_voigt_gl',287.8,1.8,0.2*H,287.3,288.3,0.8,3.5),
 spec(5,'Sat','pseudo_voigt_gl',291.0,2.5,0.2*H,290.0,292.0,1.0,4.0)]
for m in sys.argv[1:]:
    t=time.time()
    r=fitting.run_fit(x,y,peaks,background_method='shirley',bg_start_idx=0,bg_end_idx=len(x),fit_kws={'method':m},n_perturb=3,require_component='1')
    print(m,'success',r['success'],'required',r['required'],'%.1fs'%(time.time()-t),flush=True)
