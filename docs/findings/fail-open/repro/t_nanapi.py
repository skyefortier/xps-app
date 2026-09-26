from harness import *
import re, copy
d=json.load(open(SCR+'/ds7.json'))
lines=d['csv'].split('\n')[100:140]
sid=upload('\n'.join(lines))
E=[float(l.split(',')[0]) for l in lines]
ps=copy.deepcopy(d['peaks'][:3])
for i,p in enumerate(ps): p['center']=E[40*(i+1)//4]
body={'session_id':sid,'background':{'method':'shirley','start_idx':0,'end_idx':40,'endpoint_avg':1},'peaks':ps,'fit_method':'least_squares','n_perturb':3,'n_starts':3}
st,txt=post('/api/fit',body,raw=True)
open(SCR+'/nan_body.json','w').write(txt)
print('ROI',E[0],'->',E[-1],'40 pts; peaks',[(p['id'],round(p['center'],2),round(p['amplitude']),round(p['fwhm'],2)) for p in ps])
print('status',st,'content-type json; success', re.search(r'"success":\s*(\w+)',txt).group(1), 'NaN tokens',len(re.findall('NaN',txt)))
print(re.findall(r'"center":\{[^}]*NaN[^}]*\}',txt)[:1])
print('starts', re.search(r'"starts":\{"alternatives":[^,]*,"fit"',txt) is not None, re.search(r'"n_same_as_fit":\s*\d+',txt).group(0) if re.search(r'"n_same_as_fit":\s*\d+',txt) else None)
print('supports', re.findall(r'"supported":\s*\w+',txt))
