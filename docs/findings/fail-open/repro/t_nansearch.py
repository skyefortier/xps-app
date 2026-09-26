import sys, json, copy, time, numpy as np, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'/Users/skyefortier/xps-app')
import fitting
SCR='/private/tmp/claude-501/-Users-skyefortier-xps-app/02af00e1-adfc-44c5-aadc-a32951efe70c/scratchpad'
d=json.load(open(SCR+'/ds7.json'))
rows=[l.split(',') for l in d['csv'].split('\n')]
E=np.array([float(r[0]) for r in rows]); C=np.array([float(r[1]) for r in rows])
rng=np.random.default_rng(1)
t0=time.time(); found=0; n=0
shapes=['pseudo_voigt_gl','gaussian','lorentzian','doniach_sunjic','asymmetric_gl','ds_g','la_casaxps']
while time.time()-t0<420 and found<3:
    ps=copy.deepcopy(d['peaks'])
    k=rng.integers(1,4)
    for i in range(k):
        s=dict(id=str(200+i),name='x',center=float(rng.uniform(E.min(),E.max())),amplitude=float(10**rng.uniform(-2,4)),fwhm=float(rng.uniform(0.15,4)),
               amplitude_min=0,fix_center=False,fix_fwhm=False,fix_amplitude=False,fix_gl_ratio=False,shape=str(rng.choice(shapes)),gl_ratio=0.3)
        if s['shape']=='la_casaxps': s.update(alpha=1,beta=1,m=50,fix_m=True)
        if s['shape']=='ds_g': s.update(alpha=0.1,beta=0.3,m_gauss=0.4)
        ps.append(s)
    method=str(rng.choice(['least_squares','leastsq']))
    n+=1
    try:
        r=fitting.run_fit(E,C,ps,background_method='shirley',bg_start_idx=d['bg']['start_idx'],bg_end_idx=d['bg']['end_idx'],fit_kws={'method':method},n_perturb=0)
    except Exception as e:
        continue
    try: json.dumps(r,allow_nan=False)
    except ValueError:
        found+=1
        bad=[]
        for ip in r['individual_peaks']:
            for kk,v in ip['params'].items():
                for f in ('value','stderr'):
                    x=v.get(f)
                    if isinstance(x,float) and not np.isfinite(x): bad.append((ip['id'],kk,f,x))
            for kk,x in ip['support'].items():
                if isinstance(x,float) and not np.isfinite(x): bad.append((ip['id'],'support',kk,x))
        for kk,x in r['statistics'].items():
            if isinstance(x,float) and not np.isfinite(x): bad.append(('stat',kk,x))
        print('FOUND', method, 'success',r['success'], bad[:6], json.dumps([ {k:p[k] for k in ('id','shape','center','amplitude','fwhm')} for p in ps[6:]]), flush=True)
print('tried',n,'found',found,flush=True)
