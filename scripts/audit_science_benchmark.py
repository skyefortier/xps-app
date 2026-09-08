"""Independent audit benchmarks. No experimental files or production services used.

Run: venv/bin/python scripts/audit_science_benchmark.py --output /path/results.json
Exit 1 means a validation expectation failed, not an infrastructure error.
The analytical generators deliberately do not call fitting.py.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.special import voigt_profile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fitting


def gaussian(x, height, center, width):
    sigma = width / math.sqrt(8 * math.log(2))
    return height * np.exp(-0.5 * ((x - center) / sigma) ** 2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    checks = []
    def record(name, passed, **evidence):
        checks.append(dict(name=name, passed=bool(passed), **evidence))

    # Independent analytic primitives; area over a finite window matters.
    x = np.linspace(-10, 10, 2001)
    g = gaussian(x, 10, 0, 1.2)
    err = float(np.max(np.abs(fitting._gaussian(x, 10, 0, 1.2) - g)))
    record('gaussian_analytic', err < 1e-12, max_absolute_error=err)
    analytic_l = 10 / (1 + (x / 0.6) ** 2)
    err = float(np.max(np.abs(fitting._lorentzian(x, 10, 0, 1.2) - analytic_l)))
    record('lorentzian_analytic', err < 1e-12, max_absolute_error=err)
    ds = fitting._doniach_sunjic(x, 10, 0, 1.2, 0)
    record('ds_zero_asymmetry_lorentzian', np.allclose(ds, analytic_l, atol=1e-12),
           max_absolute_error=float(np.max(np.abs(ds-analytic_l))))

    # DS+G at alpha=0 MUST reduce to the Voigt convolution. Scipy's
    # Faddeeva implementation is independent of the application's FFT.
    for size in (200, 201):
        grid = -5 + np.arange(size) * .05
        expected = voigt_profile(grid, .4/math.sqrt(8*math.log(2)), .3)
        expected /= voigt_profile(0, .4/math.sqrt(8*math.log(2)), .3)
        actual = fitting._ds_g_dscore_gauss(grid, 1, 0, 0, .3, .4)
        err = float(np.max(np.abs(actual-expected)))
        record(f'dsg_voigt_oracle_{size}_points', err < 1e-4,
               max_height_fraction_error=err, tolerance=1e-4)
        reverse = fitting._ds_g_dscore_gauss(grid[::-1], 1, 0, 0, .3, .4)[::-1]
        record(f'dsg_axis_reversal_{size}_points', np.allclose(actual, reverse, atol=1e-12))

    grid=np.linspace(-10,10,400)
    y=1000*voigt_profile(grid,.4/math.sqrt(8*math.log(2)),.3)/voigt_profile(0,.4/math.sqrt(8*math.log(2)),.3)
    fitted=fitting.run_fit(grid,y,[dict(id='0',shape='ds_g',center=0,amplitude=1000,
        fwhm=.6,alpha=0,beta=.3,m_gauss=.4,fix_alpha=True,fix_beta=True,fix_m_gauss=True)],
        background_method='none',fit_kws={'method':'least_squares'})
    center=fitted['individual_peaks'][0]['params']['center']['value']
    record('dsg_even_grid_center_recovery',abs(center)<1e-4,recovered_center_ev=center,true_center_ev=0)

    # Continuous center must not change normalization discontinuously as
    # its nearest sample switches. This tests mathematical continuity,
    # not a claim of equivalence to proprietary CasaXPS output.
    grid=np.arange(-5,5.01,.1)
    left=fitting._la_casaxps_true(grid,1,.04999999,1,.5,2,30)
    right=fitting._la_casaxps_true(grid,1,.05000001,1,.5,2,30)
    jump=float(np.max(np.abs(left-right)))
    record('la_center_continuity',jump<1e-5,center_change_ev=2e-8,max_height_fraction_jump=jump)
    grid=np.arange(-10,10.001,.05)
    crop=(grid>-2)&(grid<2)
    full=fitting._la_casaxps_true(grid,1,0,1,.5,2,50)[crop]
    cropped=fitting._la_casaxps_true(grid[crop],1,0,1,.5,2,50)
    diff=float(np.max(np.abs(full-cropped)))
    record('la_window_independence_same_sampling',diff<1e-4,max_height_fraction_change=diff)

    # Constrained Gaussian areas have exact analytical ratio H2*w2/H1*w1.
    specs=[dict(id='0',shape='gaussian',amplitude=10,center=0,fwhm=1),
           dict(id='1',shape='gaussian',amplitude=5,center=5,fwhm=2,
                constrain_to='0',splitting=5,area_ratio=.5,fix_fwhm=False)]
    params=fitting.Parameters()
    for spec in specs:
        prefix=f"p{spec['id']}_"
        model=fitting.Model(fitting._gaussian,prefix=prefix)
        params.update(fitting._make_peak_params(model,spec,prefix,specs))
    params.update_constraints()
    ratio=(params['p1_amplitude'].value*params['p1_fwhm'].value)/(
           params['p0_amplitude'].value*params['p0_fwhm'].value)
    record('linked_unequal_width_area_ratio',abs(ratio-.5)<1e-12,requested_area_ratio=.5,actual_area_ratio=ratio)

    # Construct a self-consistent Shirley spectrum from a known compact
    # nonnegative signal and its cumulative integral, not the app function.
    x = np.linspace(-4, 4, 401)
    signal = 1000 * np.maximum(1 - (x/2)**2, 0)**2
    cumulative = cumulative_trapezoid(signal, x, initial=0)
    expected_bg = 20 + 80*cumulative/cumulative[-1]
    y = signal + expected_bg
    bg = fitting.shirley_background(x, y)
    err = float(np.max(np.abs(bg-expected_bg)))
    record('shirley_constructed_integral_solution', err < 1e-4,
           max_absolute_background_error=err)

    # Fit independent Gaussian mixtures under controlled noise and starts.
    recoveries=[]
    for separation in (2.0, .5):
        x = np.linspace(-5,5,401)
        centers=(-separation/2,separation/2)
        clean=gaussian(x,1000,centers[0],1)+gaussian(x,600,centers[1],1)
        for noisy in (False,True):
            y=np.random.default_rng(20260908).poisson(clean+20).astype(float) if noisy else clean+20
            for offset in (-.15, .15):
                specs=[dict(id=str(i),shape='gaussian',amplitude=a*.8,
                            center=c+offset,fwhm=.85,center_min=c-.4,center_max=c+.4)
                       for i,(a,c) in enumerate(zip((1000,600),centers))]
                result=fitting.run_fit(x,y,specs,background_method='manual',
                        manual_bg=[[-5,20],[5,20]],fit_kws={'method':'least_squares'})
                params=[p['params'] for p in result['individual_peaks']]
                center_err=max(abs(p['center']['value']-c) for p,c in zip(params,centers))
                area_err=max(abs(p['area']['value']/(a*math.sqrt(math.pi/(4*math.log(2))))-1)
                             for p,a in zip(params,(1000,600)))
                recoveries.append(dict(separation=separation,noisy=noisy,start_offset=offset,
                                       success=bool(result['success']),max_center_error_ev=center_err,
                                       max_relative_area_error=area_err))
                # Noisy overlap is characterized, not held to arbitrary
                # exact recovery requirements from one random realization.
                if not noisy:
                    record(f'noiseless_gaussian_recovery_sep{separation}_start{offset}',
                           result['success'] and center_err<1e-4 and area_err<1e-3,
                           max_center_error_ev=center_err,max_relative_area_error=area_err)

    # A fixed user-requested zero Gaussian width must survive parameter
    # construction. Evaluate model specs, independent of fit convergence.
    spec=dict(id='0',shape='ds_g',amplitude=10,center=0,
          fwhm=1,alpha=.1,beta=.3,m_gauss=0,fix_m_gauss=True)
    model=fitting.Model(fitting._ds_g_dscore_gauss,prefix='p0_')
    p=fitting._make_peak_params(model,spec,'p0_',[spec])
    actual=float(p['p0_m_gauss'].value)
    record('fixed_dsg_zero_gaussian_width_preserved',actual==0,
           requested=0,actual=actual)

    out=dict(baseline_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             seed=20260908,checks=checks,gaussian_recovery=recoveries,
             scope='Independent analytic checks and Gaussian mixtures; not full scientific certification.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2))
    print(json.dumps(dict(checks=len(checks),passed=sum(c['passed'] for c in checks),
                          failures=[c['name'] for c in checks if not c['passed']]),indent=2))
    return int(any(not c['passed'] for c in checks))


if __name__=='__main__':
    raise SystemExit(main())
