import json, sys, numpy as np
from collections import defaultdict
rows=[json.loads(l) for l in open(sys.argv[1])]
edge=[r for r in rows if r['kind']=='edge']; bias=[r for r in rows if r['kind']=='bias']; noise=[r for r in rows if r['kind']=='noise']
NAVG=[1,3,5,10,20]
for tab in ['C1s Scan','U4f Scan_0']:
    print(f"\n=== EDGE SENSITIVITY — {tab} (one grid point at the low-BE window edge; ref = 1c window) ===")
    base={r['navg']:r for r in edge if r['tab']==tab and r['variant']=='1c'}
    peaks=list(base[1]['peaks'].keys())
    print(f"{'n_avg':>5} {'variant':>10} {'Δχ²ᵣ':>7}  {'bg lo-edge Δ':>12}  " + '  '.join(f"{p[:12]:>18}" for p in peaks))
    print(f"{'':>5} {'':>10} {'':>7}  {'(counts)':>12}  " + '  '.join(f"{'Δfrac pp / Δarea %':>18}" for p in peaks))
    for n in NAVG:
        b=base[n]
        for r in sorted([r for r in edge if r['tab']==tab and r['navg']==n and r['variant']!='1c'], key=lambda r:r['variant']):
            cells=[]
            for p in peaks:
                cells.append(f"{r['peaks'][p]['frac']-b['peaks'][p]['frac']:+6.2f} / {100*(r['peaks'][p]['area']/b['peaks'][p]['area']-1) if b['peaks'][p]['area'] else float('nan'):+6.2f}")
            print(f"{n:5d} {r['variant']:>10} {r['chi2r']-b['chi2r']:+7.3f}  {r['bg_edge_lo']-b['bg_edge_lo']:+12.1f}  " + '  '.join(f"{c:>18}" for c in cells))
    print(f"  max |Δfrac| over variants, per n_avg: " + ', '.join(f"n={n}: {max(abs(r['peaks'][p]['frac']-base[n]['peaks'][p]['frac']) for r in edge if r['tab']==tab and r['navg']==n and r['variant']!='1c' for p in peaks):.2f} pp" for n in NAVG))
    print(f"  χ²ᵣ at 1c window per n_avg: " + ', '.join(f"n={n}: {base[n]['chi2r']:.3f}" for n in NAVG))
    print(f"\n--- SLOPE BIAS — {tab} (anchor = mean of cap points; trend = local 20-pt linear fit at the edge) ---")
    print(f"{'n_avg':>5} {'cap':>4} | {'HI edge: slope/pt':>17} {'raw':>8} {'trend':>8} {'anchor':>8} {'bias':>7} {'σ_noise':>7} | {'LO edge: slope/pt':>17} {'raw':>8} {'trend':>8} {'anchor':>8} {'bias':>7} {'σ_noise':>7}")
    for r in sorted([r for r in bias if r['tab']==tab], key=lambda r:r['navg']):
        h,l=r['hi'],r['lo']
        print(f"{r['navg']:5d} {r['cap']:4d} | {h['slope_counts_per_pt']:17.1f} {h['raw_edge']:8.0f} {h['trend_at_edge']:8.0f} {h['anchor']:8.0f} {h['bias_vs_trend']:+7.1f} {h['noise_sd_local']:7.1f} | {l['slope_counts_per_pt']:17.1f} {l['raw_edge']:8.0f} {l['trend_at_edge']:8.0f} {l['anchor']:8.0f} {l['bias_vs_trend']:+7.1f} {l['noise_sd_local']:7.1f}")
print("\n=== POISSON SCATTER — C1s Scan, 24 draws, 1c window ===")
print(f"{'n_avg':>5} {'σ(graphite frac) pp':>20} {'σ(Adv.1 frac) pp':>17} {'σ(Unknown1 frac)':>17} {'mean χ²ᵣ':>9} {'σ(χ²ᵣ)':>7} {'converged':>9}")
for n in NAVG:
    rs=[r for r in noise if r['navg']==n]
    g=np.array([r['peaks']['Graphite']['frac'] for r in rs]); a=np.array([r['peaks']['Adventitious 1']['frac'] for r in rs]); u=np.array([r['peaks']['Unknown 1']['frac'] for r in rs]); c=np.array([r['chi2r'] for r in rs])
    print(f"{n:5d} {g.std(ddof=1):20.2f} {a.std(ddof=1):17.2f} {u.std(ddof=1):17.2f} {c.mean():9.3f} {c.std(ddof=1):7.3f} {sum(r['success'] for r in rs):>6d}/{len(rs)}")
