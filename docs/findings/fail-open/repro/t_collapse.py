from harness import *
import re, copy
d=json.load(open(SCR+'/ds7.json'))
sid=upload(d['csv'])
for c,a,w in [(292.8,500,0.8),(292.5,200,0.3),(276.0,300,0.5),(275.0,100,0.2),(286.0,50,0.15)]:
    ps=copy.deepcopy(d['peaks']); z=copy.deepcopy(ps[1]); z.update(id='98',center=c,amplitude=a,fwhm=w,shape='pseudo_voigt_gl',gl_ratio=0.3,fix_gl_ratio=False); ps.append(z)
    body={'session_id':sid,'background':d['bg'],'peaks':ps,'fit_method':'least_squares','n_perturb':3,'n_starts':3}
    st,txt=post('/api/fit',body,raw=True)
    toks=re.findall(r'.{60}(?:NaN|-?Infinity).{10}',txt)
    try:
        j=json.loads(txt); ip=[q for q in j['individual_peaks'] if q['id']=='98'][0]; info=(j['success'],ip['params']['amplitude']['value'],ip['support'])
    except Exception: info='unparseable'
    print((c,a,w),st,info,'nonfinite',len(re.findall(r'NaN|Infinity',txt)),toks[:2])
