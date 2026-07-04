# Adjudication Decisions — PROGRESS.md discrepancies

**Ruled by:** Skye (domain expert), 2026-07-03 (Fri evening), with Claude.
**Purpose:** dispositions for the Monday session and for Fable to execute. Nothing here re-litigated.

---

## Data / tagging bugs — confirmed, lint-and-fix (no science)
- **#1 `Zr 3d` RSF tags** (B4C-UCl₄, B 1s B–B/B–C) and **#2 `K 2p` RSF tags** (all 44 C 1s π→π\* satellites): **confirmed erroneous — no Zr or K in any sample.** Re-tag correctly and add the quantification lint (spec §8) to catch the pattern. **Do NOT alter the source data files.**
- The **`N 1s` RSF tag on the ~397 eV U 4f satellite: LEAVE it** — that satellite genuinely sits in N 1s territory; the tag may be deliberate.

## Reference-data exclusions — confirmed
- **#3 4-GTA UCl₄-BN B 1s fits** (χ²ᵣ up to ~10⁵): erroneous one-offs (never a real fit) → **exclude as anchors.** Confirmed.
- **#4 internally inconsistent C 1s tab** (`UCl4_on_graphite / C1s Scan_4`, `fittedY` 143 pts vs `be` 142): **exclude.** Confirmed.

## Resolved by domain knowledge — no engine change
- **#6 low-BE ~283.4 eV "Unknown":** a graphite **surface species, removed by vacuum-degassing the graphite immediately before use** — not intrinsic chemistry, not a U artifact. The proposal-pass flagging it is *correct behavior*; no grammar change. Origin recorded.
- **#8 B 1s label swap** (B–C / B–B between the two expert sources): **manual-assignment mix-up** — positions identical, only the chemistry labels differ. The engine's **position-neutral roles (low/mid/oxide) are the correct handling.** Non-issue.
- **U 4f satellite decoupling** (separation ~11.2 ≠ Δso 10.9; intensity ratio ~0.91 ≠ 0.75): **not concerning** — multifactorial and not straightforward, per Skye. No action; the **U2 (independent satellites) default stands.**

## Engine changes to make (Fable / Monday)

### Cl 2p 2:1-ratio rejection (#7) — resolved as a LINESHAPE fix, not chemistry
- **Cause:** artifact of the **shared-FWHM** doublet constraint. The 2p₁/₂ is intrinsically broader than 2p₃/₂ (Coster-Kronig), so forcing equal widths mis-partitions area and pushes the apparent ratio above 0.5.
- **ACTION:** allow the Cl 2p doublet components **independent widths** (2p₁/₂ ≥ 2p₃/₂). Expect the area ratio to return to ~0.5.
- **Then:** Cl 2p Δso/ratio can **leave CONDITIONAL** status (spec §9).
- **Ruled out:** hydrolysis / second chloride species — the UCl₄ is **strictly anhydrous** (glovebox synthesis). If independent widths do *not* resolve it, check **differential charging** (insulator-in-conductor composite) and **beam damage** (ratio vs. scan number) — secondary only.

### Width convention (#5)
- **Adventitious / contamination C 1s components → cap FWHM at ~2.0 eV** (literature-reasonable upper bound; instrument/pass-energy-dependent — a *cap*, not a target). Replace the engine's split **1.6 / 3.5 eV** contamination caps with a **uniform ~2.0 eV.**
- **Satellites (π→π\*, etc.) → NO change.** Broad satellites are a known/expected occurrence. Fable already recalibrated the satellite FWHM cap to **(1.0, 5.5) eV** to match the 44 expert fits (span 1.9–5.0 eV). Keep.

---

## Net for Monday / Fable
1. Re-tag the RSF mis-tags (#1/#2) + add the quantification lint; leave the U-satellite `N 1s` tag.
2. Cl 2p: **independent doublet widths** → ratio ~0.5 → constants off CONDITIONAL.
3. Adventitious-C FWHM cap → **~2.0 eV uniform**; satellite cap stays 5.5 eV.
4. No engine change for #3, #4, #6, #8, or the U 4f satellite gaps.
