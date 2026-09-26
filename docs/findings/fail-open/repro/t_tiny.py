from harness import *
import numpy as np, re, copy
d=json.load(open(SCR+'/ds7.json'))
lines=d['csv'].split('\n')
for n in [16,20,30,50,80]:
    sub='\n'.join(lines[100:100+n])
    sid=upload(sub)
    E=[float(l.split(',')[0]) for l in lines[100:100+n]]
    ps=copy.deepcopy(d['peaks'][:3])
    for i,p in enumerate(ps): p['center']=E[len(E)//2]+0.1*i
    body={'session_id':sid,'background':{'method':'linear','start_idx':0,'end_idx':n,'endpoint_avg':1},'peaks':ps,'fit_method':'least_squares','n_perturb':3,'n_starts':3}
    st,txt=post('/api/fit',body,raw=True)
    toks=re.findall(r'.{50}(?:NaN|-?Infinity).{10}',txt)
    try: s=json.loads(txt).get('success')
    except Exception: s='?'
    print('n points',n,'params 12 -> status',st,'success',s,'nonfinite',len(re.findall(r'NaN|Infinity',txt)),toks[:3], txt[:120] if st!=200 else '')
