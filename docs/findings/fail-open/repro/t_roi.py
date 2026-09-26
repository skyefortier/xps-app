from harness import *
d=json.load(open(SCR+'/ds7.json'))
sid=upload(d['csv'])
base={'session_id':sid,'cc_shift':0,'material_class':'conductor','regions':['C 1s'],'method':'ic_model_comparison','options':{'endpoint_avg':1}}
for label,roi in [('both NaN->null',{'be_min':None,'be_max':None}),('min null',{'be_min':None,'be_max':290}),('keys absent',{}),('roi null',None)]:
    b=dict(base); b['roi']=roi
    # JSON.stringify(NaN) -> null ; replicate exactly
    st,j=post('/api/analyze/start',b)
    print(label, json.dumps(b['roi']), '->', st, j)
