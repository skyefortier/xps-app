import sys, json, copy, numpy as np, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'/Users/skyefortier/xps-app')
import fitting
SCR='/private/tmp/claude-501/-Users-skyefortier-xps-app/02af00e1-adfc-44c5-aadc-a32951efe70c/scratchpad'
d=json.load(open(SCR+'/ds7.json'))
rows=[l.split(',') for l in d['csv'].split('\n')]
E=np.array([float(r[0]) for r in rows]); C=np.array([float(r[1]) for r in rows])
for start in [60,100,140]:
  for n in [20,30,40]:
    for k in [1,2,3]:
        e,c=E[start:start+n],C[start:start+n]
        ps=copy.deepcopy(d['peaks'][:k])
        for i,p in enumerate(ps): p['center']=float(e[n*(i+1)//(k+1)])
        try:
            r=fitting.run_fit(e,c,ps,background_method='shirley',bg_start_idx=0,bg_end_idx=n,fit_kws={'method':'least_squares'},n_perturb=3,n_starts=3 if k>1 else 0)
        except Exception as ex: print(start,n,k,'raised',ex); continue
        try: json.dumps(r,allow_nan=False); bad=False
        except ValueError: bad=True
        if bad: print('start',start,'n',n,'k',k,'success',r['success'],'NONFINITE', [(ip['id'],kk) for ip in r['individual_peaks'] for kk,v in ip['params'].items() if v.get('stderr') is not None and not np.isfinite(v['stderr'])], 'amps',[round(ip['params']['amplitude']['value'],3) for ip in r['individual_peaks']])
print('done')
