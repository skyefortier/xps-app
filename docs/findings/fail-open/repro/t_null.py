from harness import *
d=json.load(open(SCR+'/ds7.json'))
sid=upload(d['csv'])
import copy
def run(peaks, label, method='least_squares'):
    body={'session_id':sid,'background':d['bg'],'peaks':peaks,'fit_method':method,'n_perturb':0,'n_starts':0}
    st,j=post('/api/fit',body)
    if isinstance(j,dict) and 'individual_peaks' in j:
        out=[]
        for ip in j['individual_peaks']:
            if ip['id'] in [p['id'] for p in peaks if p.get('_t')]:
                out.append({k:(round(v['value'],4),v['min'],v['max']) for k,v in ip['params'].items() if k!='area'})
        print(label, st, 'success',j['success'], out)
    else: print(label, st, j if isinstance(j,dict) else j[:200])
P=d['peaks']
def mod(i, **kw):
    ps=copy.deepcopy(P); ps[i].update(kw); ps[i]['_t']=1; return ps
run(mod(1,center=None),'GL/Voigt center null')
run(mod(1,amplitude=None),'Voigt amplitude null')
run(mod(1,fwhm=None),'Voigt fwhm null')
g=mod(1,shape='pseudo_voigt_gl',gl_ratio=None,fix_gl_ratio=False); run(g,'GL gl_ratio null (glMix NaN)')
for shape,extra in [('ds_g',{'alpha':0.1,'beta':0.3,'m_gauss':0.4}),('gaussian',{}),('doniach_sunjic',{'alpha':0.1,'gamma_asym':0}),('la_casaxps',{'alpha':1,'beta':1,'m':50,'fix_m':True})]:
    for fld in ['center','amplitude','fwhm']:
        ps=mod(1,shape=shape,**extra); ps[1][fld]=None
        run(ps,f'{shape} {fld} null')
# linked splitting null
ps=copy.deepcopy(P); ps[2].update(constrain_to=ps[1]['id'],splitting=None,area_ratio=0.5,fix_fwhm=True); run(ps,'linked splitting null')
ps=copy.deepcopy(P); ps[2].update(constrain_to=ps[1]['id'],splitting=1.0,area_ratio=None,fix_fwhm=True); run(ps,'linked area_ratio null')
# linked constrain_to as number vs string
ps=copy.deepcopy(P); ps[2].update(constrain_to=int(ps[1]['id']),splitting=1.0,area_ratio=0.5,fix_fwhm=True); run(ps,'constrain_to numeric')
