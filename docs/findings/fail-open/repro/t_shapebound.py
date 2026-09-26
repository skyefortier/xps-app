from harness import *
import copy
d=json.load(open(SCR+'/ds7.json'))
sid=upload(d['csv'])
def go(shape, extra, label):
    ps=copy.deepcopy(d['peaks']); p=ps[5]
    for k in ('gl_ratio',): p.pop(k,None)
    p.update(shape=shape, fix_gl_ratio=False, **extra)
    body={'session_id':sid,'background':d['bg'],'peaks':ps,'fit_method':'least_squares','n_perturb':3,'n_starts':3}
    st,j=post('/api/fit',body)
    ip=[q for q in j['individual_peaks'] if q['id']==p['id']][0]
    print(label,st,'success',j['success'])
    for k,v in ip['params'].items():
        if k=='area' or not v.get('vary'): continue
        lo,hi=v['min'],v['max']
        at = (lo is not None and hi is not None and (v['value']-lo<=0.01*(hi-lo) or hi-v['value']<=0.01*(hi-lo)))
        checked = k in ('center','fwhm','fwhm_l','amplitude','gl_ratio')
        print(f"   {k:10s} value={v['value']:.4g} min={lo} max={hi} AT_BOUND={at} page_rule1_checks={checked}")
go('la_casaxps',{'alpha':1.0,'beta':1.0,'m':50.0,'fix_alpha':False,'fix_beta':False,'fix_m':True},'LACX on peak 11')
go('doniach_sunjic',{'alpha':0.1,'gamma_asym':0.0,'fix_alpha':False,'fix_gamma_asym':False},'DS on peak 11')
go('ds_g',{'alpha':0.1,'beta':0.3,'m_gauss':0.4,'fix_alpha':False,'fix_beta':False,'fix_m_gauss':False},'DS+G on peak 11')
