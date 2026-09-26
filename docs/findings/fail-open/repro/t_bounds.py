from harness import *
d=json.load(open(SCR+'/ds7.json'))
sid=upload(d['csv'])
# add one of each shape
import copy
peaks=d['peaks']
base=peaks[1]
extra=[]
for i,(shape,kw) in enumerate([('gaussian',{}),('lorentzian',{}),('asymmetric_gl',{'gl_ratio':0.3,'asymmetry':0.1,'fix_asymmetry':False}),
  ('doniach_sunjic',{'alpha':0.1,'gamma_asym':0.0,'fix_alpha':False,'fix_gamma_asym':False}),
  ('ds_g',{'alpha':0.1,'beta':0.3,'m_gauss':0.4,'fix_alpha':False,'fix_beta':False,'fix_m_gauss':False}),
  ('la_casaxps',{'alpha':1.0,'beta':1.0,'m':50,'fix_alpha':False,'fix_beta':False,'fix_m':False}),
  ('pseudo_voigt_gl',{'gl_ratio':0.3})]):
    s=dict(id=str(100+i),name=shape,center=284.0+0.3*i,amplitude=1000,fwhm=1.2,amplitude_min=0,fix_center=False,fix_fwhm=False,fix_amplitude=False,fix_gl_ratio=False,shape=shape,**kw)
    extra.append(s)
body={'session_id':sid,'background':d['bg'],'peaks':peaks[:3]+extra,'fit_method':'least_squares','n_perturb':0,'n_starts':0}
st,j=post('/api/fit',body)
print(st, j.get('success') if isinstance(j,dict) else j[:300])
for ip in j['individual_peaks']:
    shape=[p for p in body['peaks'] if p['id']==ip['id']][0]['shape']
    for k,v in ip['params'].items():
        if k=='area': continue
        print(f"{shape:16s} {k:11s} vary={v['vary']!s:5s} min={v['min']} max={v['max']} stderr={'None' if v['stderr'] is None else 'num'}")
