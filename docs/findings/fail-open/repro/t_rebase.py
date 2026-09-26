from harness import *
import copy
d=json.load(open(SCR+'/ds7.json'))
sid=upload(d['csv'])
ps=copy.deepcopy(d['peaks']); tgt=ps[2]; tgt['center']=285.6   # saved 281.28
for press in range(1,4):
    body={'session_id':sid,'background':d['bg'],'peaks':ps,'fit_method':'least_squares','n_perturb':3,'n_starts':3}
    st,j=post('/api/fit',body)
    ip=[q for q in j['individual_peaks'] if q['id']==tgt['id']][0]; c=ip['params']['center']
    lo,hi=c['min'],c['max']; at=(c['value']-lo<=0.01*(hi-lo)) or (hi-c['value']<=0.01*(hi-lo))
    print(f"press {press}: start {tgt['center']:.3f} window [{lo:.2f},{hi:.2f}] fitted {c['value']:.3f} success {j['success']} at_bound_warning={at}")
    # page applies every unlocked fitted value back to the peaks (applyBackendResult)
    for p in ps:
        q=[x for x in j['individual_peaks'] if x['id']==p['id']][0]['params']
        for k in ('center','amplitude','fwhm'): p[k]=q[k]['value']
