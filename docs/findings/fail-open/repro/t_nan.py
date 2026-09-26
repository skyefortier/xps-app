from harness import *
import copy, re
d=json.load(open(SCR+'/ds7.json'))
sid=upload(d['csv'])
P=d['peaks']
def run(ps,label,method):
    body={'session_id':sid,'background':d['bg'],'peaks':ps,'fit_method':method,'n_perturb':3,'n_starts':3 if len(ps)>1 else 0}
    st,txt=post('/api/fit',body,raw=True)
    bad=re.findall(r'.{60}(?:NaN|-?Infinity).{20}',txt)
    try: j=json.loads(txt); succ=j.get('success')
    except Exception: succ='?'
    print(label,method,st,'success',succ,'nonfinite tokens:',len(re.findall(r'NaN|Infinity',txt)), bad[:2])
for method in ['least_squares','leastsq','nelder']:
    run(copy.deepcopy(P),'ds7 as saved',method)
    ps=copy.deepcopy(P); dup=copy.deepcopy(ps[1]); dup['id']='99'; ps.append(dup); run(ps,'ds7 + duplicate of peak 7',method)
    ps=copy.deepcopy(P); z=copy.deepcopy(ps[1]); z.update(id='98',center=292.9,amplitude=1.0,fwhm=0.3); ps.append(z); run(ps,'ds7 + tiny component at edge',method)
