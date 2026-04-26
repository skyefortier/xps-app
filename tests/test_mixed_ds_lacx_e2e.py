"""
Mixed-model E2E: synthesize a 2-peak spectrum (one DS, one LACX) with
distinct centers/FWHMs/amplitudes and Gaussian noise, fit through the
same code path as /api/fit, and assert each peak's parameters recover
within ~5%. Exercises the free-peak path of _make_peak_params for
'la_casaxps' alongside 'doniach_sunjic' — branch coverage the
single-peak E2E doesn't reach.
"""
import sys
sys.path.insert(0, "/home/skye/xps-app")
import numpy as np
from fitting import _doniach_sunjic, _la_casaxps_true, run_fit

rng = np.random.default_rng(7)
x = np.linspace(280, 300, 2001)

# DS peak (no metallic-screening tail in the synth — just core asymmetry)
ds_amp, ds_center, ds_fwhm = 8000.0, 285.5, 1.1
ds_alpha, ds_gamma = 0.08, 0.005

# LACX peak — asymmetric, low-BE shoulder via beta < alpha
la_amp, la_center, la_fwhm = 5000.0, 290.5, 0.9
la_alpha, la_beta, la_m = 1.2, 0.6, 25

# Synth: amplitude convention = peak height = amplitude (matches both
# backend functions' normalization).
y_ds  = _doniach_sunjic(x, amplitude=ds_amp, center=ds_center, fwhm=ds_fwhm,
                        alpha=ds_alpha, gamma_asym=ds_gamma)
y_la  = _la_casaxps_true(x, amplitude=la_amp, center=la_center, fwhm=la_fwhm,
                         alpha=la_alpha, beta=la_beta, m=la_m)
y_clean = y_ds + y_la
y_noisy = y_clean + rng.normal(0, np.sqrt(np.maximum(y_clean, 1.0)))

peak_specs = [
    {
        'id': '1',
        'shape': 'doniach_sunjic',
        'center': 285.3, 'amplitude': 7000.0, 'fwhm': 1.0,
        'alpha': 0.10, 'gamma_asym': 0.005,
    },
    {
        'id': '2',
        'shape': 'la_casaxps',
        'center': 290.7, 'amplitude': 4500.0, 'fwhm': 1.0,
        'alpha': 1.0, 'beta': 1.0, 'm': 25.0,
        'fix_m': True,
    },
]

result = run_fit(
    energy=x,
    counts=y_noisy,
    peak_specs=peak_specs,
    background_method='none',
)

assert result['success'], f"fit failed: {result.get('message')}"

# DS recovery
ds_ip = next(p for p in result['individual_peaks'] if p['id'] == '1')
got_ds_center = ds_ip['params']['center']['value']
got_ds_fwhm   = ds_ip['params']['fwhm']['value']
got_ds_amp    = ds_ip['params']['amplitude']['value']
got_ds_alpha  = ds_ip['params']['alpha']['value']

# LACX recovery
la_ip = next(p for p in result['individual_peaks'] if p['id'] == '2')
got_la_center = la_ip['params']['center']['value']
got_la_fwhm   = la_ip['params']['fwhm']['value']
got_la_amp    = la_ip['params']['amplitude']['value']
got_la_alpha  = la_ip['params']['alpha']['value']
got_la_beta   = la_ip['params']['beta']['value']

def within(label, got, true, frac):
    rel = abs(got - true) / abs(true)
    assert rel < frac, f"{label}: got {got:.4f} vs true {true:.4f} ({100*rel:.2f}% > {100*frac:.0f}%)"

within("DS center",    got_ds_center, ds_center, 0.005)
within("DS fwhm",      got_ds_fwhm,   ds_fwhm,   0.05)
within("DS amp",       got_ds_amp,    ds_amp,    0.05)
within("DS alpha",     got_ds_alpha,  ds_alpha,  0.20)  # alpha is the noisiest DS param

within("LACX center",  got_la_center, la_center, 0.005)
within("LACX fwhm",    got_la_fwhm,   la_fwhm,   0.05)
within("LACX amp",     got_la_amp,    la_amp,    0.05)
within("LACX alpha",   got_la_alpha,  la_alpha,  0.05)
within("LACX beta",    got_la_beta,   la_beta,   0.05)

print("OK — mixed DS + LACX recovered:")
print(f"  DS:   center={got_ds_center:.3f} fwhm={got_ds_fwhm:.3f} amp={got_ds_amp:.0f} alpha={got_ds_alpha:.3f}")
print(f"  LACX: center={got_la_center:.3f} fwhm={got_la_fwhm:.3f} amp={got_la_amp:.0f} alpha={got_la_alpha:.3f} beta={got_la_beta:.3f}")
