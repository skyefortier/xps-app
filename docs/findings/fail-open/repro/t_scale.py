import sys, json, copy, numpy as np, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'/Users/skyefortier/xps-app')
import fitting
SCR='/private/tmp/claude-501/-Users-skyefortier-xps-app/02af00e1-adfc-44c5-aadc-a32951efe70c/scratchpad'
d=json.load(open(SCR+'/ds7.json')); pg=json.load(open(SCR+'/ds7_pagebg.json'))
E=np.array(pg['be']); C=np.array(pg['inten'])
for scale in [1.0, 1e-3, 1e-4]:
    ps=copy.deepcopy(d['peaks'])
    for p in ps: p['amplitude']*=scale
    y=C*scale
    out={}
    for label,(e,c) in {'unrounded':(E,y),'uploaded (4dp/2dp)':(np.round(E,4),np.round(y,2))}.items():
        r=fitting.run_fit(e,c,ps,background_method='shirley',bg_start_idx=0,bg_end_idx=len(E),fit_kws={'method':'least_squares'},n_perturb=0)
        out[label]=(r['success'], round(r['statistics']['reduced_chi_square'],4), [ (ip['id'], ip['support']['supported'], None if ip['support']['f'] is None else round(ip['support']['f'],1)) for ip in r['individual_peaks']], [round(ip['params']['area']['value']/sum(q['params']['area']['value'] for q in r['individual_peaks'])*100,2) for ip in r['individual_peaks']])
    print('scale',scale,'max intensity',round(y.max(),4))
    for k,v in out.items(): print('   ',k,v)
