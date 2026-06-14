# Stage 9 Phase 4-5 Evidence — survey-line dual extraction + tiering

Dual independent extraction from NIST SRD 20 Internet Archive snapshots:
- Pass 4a: Claude workflow (8 agents, 57/62 fields extracted, full evidence)
- Pass 4b: Codex (gpt-5.5) independent read of the same NIST tables

## Tier counts (62 survey-line fields)

- transcription-corroborated: 49
- conflict: 8
- insufficient-evidence: 5

NOTE: machine-source-corroborated is NOT claimed — both passes read the SAME source (NIST); the honest top tier for a single-source dual-read is transcription-corroborated.

## Conflicts (legacy vs corroborated authoritative NIST)

- **Na KLL**: legacy 497 vs NIST [994.3, 994.5] — both extractors agree; legacy is oxide/Auger-positioned
- **Mg KLL**: legacy 306 vs NIST [1184.9, 1185.3, 1185.5, 1185.6, 1185.7, 1185.8] — both extractors agree; legacy is oxide/Auger-positioned
- **P 2p**: legacy 133 vs NIST [129.9, 130.0, 130.1, 130.2, 130.3, 130.4] — both extractors agree; legacy is oxide/Auger-positioned
- **Ti 2p**: legacy 459 vs NIST [453.2, 453.7, 453.8, 453.9, 454.0, 454.3] — both extractors agree; legacy is oxide/Auger-positioned
- **V 2p**: legacy 517 vs NIST [512.1, 512.3, 512.4, 512.6, 512.7, 512.9] — both extractors agree; legacy is oxide/Auger-positioned
- **Cr 2p**: legacy 577 vs NIST [573.8, 573.9, 574, 574.2, 574.3, 574.4] — both extractors agree; legacy is oxide/Auger-positioned
- **Fe 2p**: legacy 711 vs NIST [706.5, 706.7, 706.8, 706.9, 707.0, 707.1] — both extractors agree; legacy is oxide/Auger-positioned
- **U 5d**: legacy 98 vs NIST [93.6, 94, 94.2] — both extractors agree; legacy is oxide/Auger-positioned

## Insufficient-evidence (no recoverable archive — stay legacy-unverified)

- O KLL (legacy 978): claude=no-matching-line, codex=no-matching-line
- F 1s (legacy 685): claude=no-snapshot, codex=absent
- Cl 2s (legacy 270): claude=no-matching-line, codex=no-matching-line
- Br 3d (legacy 69): claude=no-snapshot, codex=absent
- Nd 3d (legacy 982): claude=no-snapshot, codex=absent
