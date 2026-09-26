import sys; sys.path.insert(0,'/Users/skyefortier/xps-app')
import numpy as np, fitting, warnings, math; warnings.simplefilter('ignore')
x=np.array([288.,287.,286.,285.,284.,283.]); y=np.array([110.,180.,400.,900.,300.,105.])
specs=[dict(id=1,shape='pseudo_voigt_gl',center=285,amplitude=800,fwhm=1.2,gl_ratio=0.3,amplitude_min=0),
       dict(id=2,shape='pseudo_voigt_gl',center=286,amplitude=300,fwhm=1.2,gl_ratio=0.3,amplitude_min=0)]
r=fitting.run_fit(x,y,specs,'linear',fit_kws={'method':'least_squares'},n_perturb=0)
bad=[(ip['id'],k,v['stderr']) for ip in r['individual_peaks'] for k,v in ip['params'].items() if isinstance(v.get('stderr'),float) and not math.isfinite(v['stderr'])]
print('non-finite stderr:',bad)
import app as A
a=A.create_app(upload_folder='/private/tmp/claude-501/-Users-skyefortier-xps-app/02af00e1-adfc-44c5-aadc-a32951efe70c/scratchpad/up')
with a.app_context():
    from flask import jsonify
    body=jsonify({'s':float('nan')}).get_data(as_text=True)
print('jsonify NaN ->',body)
