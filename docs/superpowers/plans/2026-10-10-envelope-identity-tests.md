# Envelope = background + sum of components, pinned (owner, 2026-10-10) — tests only

Owner: "Add tests pinning the identity envelope = background + sum of components, on the page
(as drawn after a fit, after editing a peak, and with components locked at bounds) and on the
server (free and locked), to rounding. Prove each fails if the identity is broken.
Tests-only, merge after Codex x2; no deploy."

Why: the 2026-09-17 student report (an envelope above the sum of its components on a UCl4
spectrum) was this identity broken on the page — asym-GL drawn with a width that grew with
distance from the centre, fixed in cf4938d (2026-08-31). Until now it was pinned only
component by component (tests/js/lineshape_parity.test.js, tests/js/lineshape_roundtrip.test.js);
nothing compared the envelope with the sum.

## Codex round 1 (NO-GO ×2) and the restructure

Both runs: (1) the DS+G "FFT term" was not derived for these implementations (the page's
recursive twiddles err by 164-604 u, not u; the complex product, the fold, the normalisation
and pocketfft's factorisation were unaccounted); (2) the amplitude / centre / width lock cases
asserted nothing (with the lock flags stripped they still passed); (3) the page check compared y
by index and ignored x (a component shifted 10 eV passed). Also: the coverage claim overstated
the bounds matrix. The deeper point of (1): after a server fit the page DRAWS its components with
its own JavaScript evaluators, and agreement between two implementations of a transcendental
formula is not a rounding bound one can derive in general. So:

- **The rounding bound is claimed only where one implementation made every curve**: the server's
  arrays, and the page's own composed envelope after an edit. `tests/envelope_identity.py`:
  4 (n + 2) u S, plus, for the server's LA (an alignment-dependent BLAS dot over non-negative
  terms), a DERIVED 4 γ_K |c| with K the kernel length. No FFT term: the server's DS+G is the same
  code on the same values twice (observed exact; if pocketfft ever proved alignment-dependent
  the test would say so — a finding, not a tolerance to widen).
- **After a fit the page identity is split** into parts with proper checks: the drawn envelope
  IS `fitted_y` and the drawn background IS `background_y` (exact equality); the server's own
  identity (the bound above); each drawn component equals the server's curve within the
  project's PARITY tolerance, 1e-6 of its amplitude (`lineshape_roundtrip.test.js` TIGHT_TOL —
  named as parity, not rounding), plus the derived rounding of recovering a drawn component
  from "component + background" (2 u (|b| + |c|): a collapsed 5e-11-amplitude component on a
  1000-count background otherwise reads the background's ulps as a gap — found by this test).
- Every drawn dataset must share the envelope's x-grid.
- Locks: every lock flag must be HELD by the server on both locked components (`vary` false, at the
  requested value), server and page (the page reads the server's response); mutation-checked
  (flags stripped before the parameters are built → the test fails).
- New proofs: a component drawn on energies shifted by 0.1 eV; a DS+G drawn with its Gaussian width
  2 % off (a DS+G-specific negative control). The old proofs now fail the parity check (the
  pre-cf4938d asym-GL; a mix of 0 drawn as 50) or the summation bound (a dropped component).
- Cases added: DS decay 0 and DS+G width 4 locked (server and page), a Gaussian with amplitude,
  centre and width all locked (page). The cases are LISTED, not "every bound of every parameter";
  absent: DS+G β 2.0 on the server (took > 6 min to certify) and LA α 0.1 with β 5 on the page
  (does not certify — an honest refusal).

Codex round 2 (NO-GO ×2, one MAJOR): after a fit the split check examined only the component
datasets it was handed, so a missing or duplicated drawn component passed (the envelope 94.5 %
of its height above the drawn sum). Now every server component must be drawn exactly once
(unique ids equal to the server's set, equal lengths) before parity is checked, with a new proof
that removes a drawn component after a fit. MINOR: the LA term's first-order derivation now
states the exact factor 4 γ_K / (1 − γ_K)² and allocates the second-order, division and
final-multiplication terms (≈ 4 u |c| at K = 1167) to the summation term's margin
((2 n + 8) u S ≥ 10 u S).

The sections below are round 1's text, kept for the record; where they differ, the sections above govern.

## The bound (`tests/envelope_identity.py`)

Point by point, |e − (b + Σ c_k)| ≤ 4 (n + 2) u S + Σ T_k, S = |b| + Σ |c_k|:
- the sum: both the envelope and our sum add the same n + 1 terms in some order, each within
  γ_n S of the exact sum, and a component evaluated twice can differ by an ulp of itself (LA's
  BLAS-backed np.convolve) — (2 γ_n + 2 u) S ≤ 4 (n + 2) u S;
- T_k, only for FFT-evaluated components (DS+G): the FFT's error is normwise, not pointwise (in
  a tail it exceeds any multiple of the local sum — measured: 16 x the pointwise bound, 5.5e-15
  of the envelope's height, before this term). T = 4 A (3 log2(L) η + u) M / peakVal, from
  Higham Thm 24.2 (η = u + γ4 (√2 + u)), the unnormalised radix-2 pair and |FFT(x)|_∞ ≤ |x|_1;
  M = max(|ds|_2 |ks|_1, |ds|_1 |ks|_2), L and peakVal are read from a copy of the page's own
  `dsgConvolved_array` at the fitted values. Measured: the DS+G gaps are 0.003-0.004 of the
  bound; in absolute terms the term is ~1e-8 counts (the old asym-GL defect: > 1e-3 of the
  envelope's height).

## Tests

Server (`tests/test_envelope_identity.py`, `fitted_y = background_y + Σ individual_peaks[].y`):
every registered lineshape free; every shape parameter locked at each bound the builder or the
server once mishandled (GL mix 0 / 1, asym-GL asymmetry 0 / 1 and both, DS α 0 / 0.5 with γ 5,
DS+G α 0 with m 0.05 and α 0.49 with β 0.05, LA m 0 / 499 and α 0.1 with β 5), amplitudes and
centres locked; every local method with perturbed restarts and scattered starts; every
background; a fit the certificate MOVED. Proofs: a component off by 1e-12, a background off by
1e-9 and a dropped component are rejected; an envelope taken from the optimiser's point while
the certificate moved the parameters (a plausible defect: `best_fit` not refreshed) is
rejected; the bound is exactly 4 (n + 2) u S (6 ulps of 1 pass, 7 fail).

Page (`tests/test_browser_envelope_identity.py`, real browser and server; what the CHART
draws — the "Fit" dataset against "Background" plus each component dataset less the
background): after a server fit, every page lineshape (the envelope drawn is the server's
`fitted_y`, statistics current); after the student edits a peak (statistics stale, the
envelope composed from the current peaks); with components locked at bounds (GL mix 0 / 100,
asym-GL mix 0 with asymmetry 1, asymmetry 0 with the amplitude locked, DS α 0 and α 0.5 with
γ 5, DS+G α 0 with m 0.05, LA m 0 / 499 and α 5 with β 0.1 — α 0.1 with β 5 together does not
certify, an honest refusal, so it is not a case). Proofs, each a real defect put back into
the page: the pre-cf4938d asym-GL (asymmetry held at 0.35: this spectrum's lines are
symmetric, so a free asymmetry fits to ~0 where the old and new formulas agree); an envelope
composed without one component; a GL mix of exactly 0 drawn as `|| 50` (A03's builder defect,
on the drawing side).
