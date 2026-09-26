from harness import *
import numpy as np
d=json.load(open(SCR+'/ds7.json')); pg=json.load(open(SCR+'/ds7_lin.json'))
sid=upload(d['csv'])
w=pg['win']
body={'session_id':sid,'background':{'method':'linear','start_idx':w['i0'],'end_idx':w['i1']+1,'endpoint_avg':1},'peaks':d['peaks'],'fit_method':'least_squares','n_perturb':3,'n_starts':3}
st,j=post('/api/fit',body)
sb=np.array(j['background_y']); pb=np.array(pg['bg']); raw=np.array(pg['inten']); fy=np.array(j['fitted_y'])
print('window',w,'status',st,'success',j['success'])
print('max |server bg - page bg| =',round(float(np.max(np.abs(sb-pb))),1),' max net signal',round(float(np.max(raw-sb)),1))
page_r = np.sum(np.abs(raw-fy))/np.sum(np.abs(raw-pb))*100
print('server r_factor %', round(100*j['statistics']['r_factor'],2), ' page R %', round(page_r,2))
