"""How far the background the page DREW (the stored preview, fitResult.bgIntensity) was from the
one the saved fit USED (its envelope less its peaks), on the fit's own points (background math,
owner round 2026-10-03; the student note's numbers). venv/bin/python scripts/bg_math_preview_vs_fitted.py"""
import sys, os, glob, numpy as np
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'); sys.path[:0]=[ROOT, os.path.join(ROOT,'tests')]; os.chdir(ROOT)
src=open('scripts/bg_math_restore_alternative.py').read(); src=src[:src.index('ap = argparse.ArgumentParser()')]
g={'__file__': os.path.join(ROOT,'scripts/bg_math_restore_alternative.py'), '__name__':'alt'}; exec(src, g)
from autofit.reference import load_reference_fits
rows=[]
for f in sorted(glob.glob('docs/autofit/test_data/*.proj.zip')):
    for rf in load_reference_fits(f):
        fr=rf.fit_result; bi=fr.get('bgIntensity'); fy=fr.get('fittedY')
        if not (isinstance(bi,list) and isinstance(fy,list) and fr.get('be') and len(bi)==len(fy)==len(fr['be'])): continue
        gg=g['fit_grid'](rf)
        if gg is None: continue
        x,y,mx=gg; specs=rf.backend_peak_specs()
        specs=[dict(s, gl_ratio=g['recorded_voigt_eta'](p)) if p.get('shape')=='Voigt' and g['recorded_voigt_eta'](p) is not None else s for s,p in zip(specs, rf.peaks)]
        used=np.asarray(fy,float)-g['evaluate_model'](mx,specs); pv=np.asarray(bi,float)
        sc=max(np.max(np.abs(used)),np.max(np.abs(pv))); d=np.max(np.abs(used-pv))/sc
        # net-area effect: (∫(y-pv) - ∫(y-used))/∫(y-used)
        net_used=abs(np.trapezoid(y-used,x)); net_pv=abs(np.trapezoid(y-pv,x))
        rows.append((100*d, 100*abs(net_pv-net_used)/net_used if net_used else np.nan, rf.project[:20], rf.name))
rows.sort(reverse=True)
a=np.array([r[0] for r in rows]); b=np.array([r[1] for r in rows])
print(len(rows),'fits; preview vs used: median %.3g %%, max %.3g %%, >1e-3 scale: %d; net-area diff median %.3g %%, max %.3g %%, >1 %%: %d' % (np.median(a),a.max(),(a>0.1).sum(),np.nanmedian(b),np.nanmax(b),(b>1).sum()))
for r in rows[:8]: print('  %.3g %% of scale, net area %.3g %%  %s / %s'%r)
