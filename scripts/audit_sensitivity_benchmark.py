"""Fixed-seed sensitivity experiment using independently generated spectra.

Characterization, not pass/fail: misspecified backgrounds and overlapping
components can legitimately yield different parameter estimates.
Run with --output outside the repository for a reproducible metrics artifact.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import sys
import numpy as np
from scipy.special import erf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fitting import run_fit


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    x=np.linspace(-5,5,401);sigma=1/math.sqrt(8*math.log(2))
    truth=[(1000,-.4),(600,.4)]
    signal=sum(a*np.exp(-.5*((x-c)/sigma)**2) for a,c in truth)
    cumulative=sum(a*sigma*math.sqrt(math.pi/2)*(erf((x-c)/(math.sqrt(2)*sigma))-
                   erf((-5-c)/(math.sqrt(2)*sigma))) for a,c in truth)
    bg=20+80*cumulative/cumulative[-1]
    rows=[]
    for seed in range(3):
        y=np.random.default_rng(20260908+seed).poisson(signal+bg).astype(float)
        for halfwindow in (5,1.5):
            mask=np.abs(x)<=halfwindow;xx=x[mask];yy=y[mask]
            for method in ('manual','shirley','linear'):
                for fixed_width in (False,True):
                    for offset in (-.15,.15):
                        specs=[dict(id=str(i),shape='gaussian',amplitude=a*.8,center=c+offset,
                                    center_min=c-.35,center_max=c+.35,fwhm=1,
                                    fix_fwhm=fixed_width) for i,(a,c) in enumerate(truth)]
                        out=run_fit(xx,yy,specs,background_method=method,
                            manual_bg=list(zip(x.tolist(),bg.tolist())) if method=='manual' else None,
                            fit_kws={'method':'least_squares'})
                        ps=[p['params'] for p in out['individual_peaks']]
                        # Exact truth areas over the SAME finite fitting window.
                        areas=[a*sigma*math.sqrt(math.pi/2)*(erf((xx[-1]-c)/(math.sqrt(2)*sigma))-
                               erf((xx[0]-c)/(math.sqrt(2)*sigma))) for a,c in truth]
                        rows.append(dict(seed=20260908+seed,halfwindow_ev=halfwindow,
                            background=method,known_background=method=='manual',fixed_width=fixed_width,
                            start_offset_ev=offset,success=bool(out['success']),
                            centers=[p['center']['value'] for p in ps],
                            max_center_error_ev=max(abs(p['center']['value']-c) for p,(_,c) in zip(ps,truth)),
                            relative_area_errors=[p['area']['value']/a-1 for p,a in zip(ps,areas)],
                            reported_area_stderr=[p['area']['stderr'] for p in ps],
                            reduced_chi_square=out['statistics']['reduced_chi_square']))
    summary=[]
    for method in ('manual','shirley','linear'):
        for fixed in (False,True):
            subset=[r for r in rows if r['background']==method and r['fixed_width']==fixed]
            summary.append(dict(background=method,fixed_width=fixed,fits=len(subset),
                max_abs_relative_area_error=max(abs(v) for r in subset for v in r['relative_area_errors']),
                max_center_error_ev=max(r['max_center_error_ev'] for r in subset),
                successes=sum(r['success'] for r in subset)))
    args.output.write_text(json.dumps(dict(description='72 fits: three fixed noise seeds; two windows; three backgrounds; two width constraints; two starts. Not a coverage calibration.',summary=summary,records=rows),indent=2))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
