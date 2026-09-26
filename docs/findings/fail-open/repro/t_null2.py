from harness import *
d=json.load(open(SCR+'/ds7.json'))
sid=upload(d['csv'])
import copy
P=d['peaks']
def run(ps,label):
    body={'session_id':sid,'background':d['bg'],'peaks':ps,'fit_method':'least_squares','n_perturb':3,'n_starts':3}
    st,j=post('/api/fit',body)
    if isinstance(j,dict) and 'individual_peaks' in j:
        ip=[q for q in j['individual_peaks'] if q['id']==ps[1]['id']][0]
        print(label, st, 'success',j['success'], 'redchi',round(j['statistics']['reduced_chi_square'],3), {k:(v['value'],v['vary'],v.get('stderr')) for k,v in ip['params'].items() if k in('amplitude','fwhm','gl_ratio','center','area')}, 'support',ip['support'], 'starts ran', (j['starts'] or {}).get('ran'))
    else: print(label, st, j)
ps=copy.deepcopy(P); ps[1].update(fwhm=None, fix_fwhm=True); run(ps,'fwhm null LOCKED')
ps=copy.deepcopy(P); ps[1].update(amplitude=None, fix_amplitude=True); run(ps,'amplitude null LOCKED')
ps=copy.deepcopy(P); ps[1].update(gl_ratio=None, fix_gl_ratio=True); run(ps,'gl_ratio null LOCKED (Voigt path)')
