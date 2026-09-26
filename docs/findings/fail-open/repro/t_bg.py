from harness import *
import numpy as np, sys
d=json.load(open(SCR+'/ds7.json')); pg=json.load(open(SCR+'/ds7_pagebg.json'))
sid=upload(d['csv'])
body={'session_id':sid,'background':d['bg'],'peaks':d['peaks'],'fit_method':'least_squares','n_perturb':3,'n_starts':3}
st,j=post('/api/fit',body)
sb=np.array(j['background_y']); pb=np.array(pg['bg']); raw=np.array(pg['inten']); fy=np.array(j['fitted_y'])
print('status',st,'success',j['success'],'n',len(sb),len(pb))
print('max |server bg - page bg| =',np.max(np.abs(sb-pb)),' as % of max net signal', 100*np.max(np.abs(sb-pb))/np.max(raw-sb))
# page R factor
page_r = np.sum(np.abs(raw-fy))/np.sum(np.abs(raw-pb))*100
print('server r_factor %', 100*j['statistics']['r_factor'], ' page R %', page_r)
# envelope vs sum of components on page bg
comp=sum(np.array(ip['y']) for ip in j['individual_peaks'])
print('max |fitted_y - (page_bg + sum comps)| =', np.max(np.abs(fy-(pb+comp))))
