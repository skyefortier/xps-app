# Stage 9 Phase 8 — Evidence Report (layered)

Migration of the legacy XPS_ELEMENTS / CHEMICAL_STATES constants to the data/xps reference system, with dual-extraction adjudication. Shown as explicit transformation layers. No fabrication; unresolved values stay flagged.

## 1. Tier adjudication (114 legacy quantitative fields)

| tier | survey (62) | chem (52) |
|---|---|---|
| transcription-corroborated | 49 | 31 |
| single-source | 0 | 2 |
| conflict | 8 | 0 |
| context-unconfirmed | 0 | 5 |
| insufficient-evidence | 5 | 14 |

`machine-source-corroborated` is claimed for NO field (both passes read the same source, NIST). Top honest tier = `transcription-corroborated`.

## 2. Correction layer (L3) — explicit transforms on the effective output

Each row: legacy value (L1=L2) -> effective (L4). Correction source shown.

| element | orbital | L1/L2 legacy | L3 correction | L4 effective | source | basis |
|---|---|---|---|---|---|---|
| C | 1s | 285 | 284.44 | 284.44 | nist-srd-20 | curated nominal (1s) |
| O | 1s | 531 | 531.4 | 531.4 | nist-srd-20 | curated nominal (1s) |
| Na | KLL | 497 | 994.4 | 994.4 | nist-srd-20* | auger KE-frame |
| Mg | KLL | 306 | 1185.65 | 1185.65 | nist-srd-20* | auger KE-frame |
| P | 2p | 133 | 130.15 | 130.15 | nist-srd-20* | elemental-nominal (metal) |
| Cl | 2p | 199 | 198.3 | 198.3 | nist-srd-20 | curated nominal (2p3/2) |
| Ti | 2p | 459 | 453.89 | 453.89 | nist-srd-20* | elemental-nominal (metal) |
| V | 2p | 517 | 512.4 | 512.4 | nist-srd-20* | elemental-nominal (metal) |
| Cr | 2p | 577 | 574.26 | 574.26 | nist-srd-20* | elemental-nominal (metal) |
| Fe | 2p | 711 | 706.92 | 706.92 | nist-srd-20* | elemental-nominal (metal) |
| Cu | 2p | 933 | 932.67 | 932.67 | nist-srd-20 | curated nominal (2p3/2) |
| Nb | 3d | 202 | 202.31 | 202.31 | nist-srd-20 | curated nominal (3d5/2) |
| U | 4f | 380 | 377.3 | 377.3 | nist-srd-20 | curated nominal (4f7/2) |
| U | 4d | 736 | 736.4 | 736.4 | nist-srd-20 | curated nominal (4d5/2) |
| U | 5d | 98 | 94.0 | 94.0 | nist-srd-20 | curated nominal (5d5/2) |

_15 survey fields carry a correction; the rest pass through legacy unchanged. *=corroborated by both extraction passes; metal/KE value, not a single-source pick._

## 3. NON-AUTHORITATIVE — unresolved, stay legacy-unverified

These have NO corroborating authoritative extraction. They retain the legacy value but are flagged non-authoritative; NOT presented as verified.

**Survey (5):** O KLL (978, insufficient-evidence), F 1s (685, insufficient-evidence), Cl 2s (270, insufficient-evidence), Br 3d (69, insufficient-evidence), Nd 3d (982, insufficient-evidence)

**Chem (19):** N 1s/Metal nitride (context-unconfirmed), N 1s/NO₃ (nitrate) (context-unconfirmed), Fe 2p3/2/Fe metal (context-unconfirmed), Fe 2p3/2/FeO (Fe²⁺) (context-unconfirmed), Fe 2p3/2/FeSO₄ (context-unconfirmed), Cu 2p3/2/Cu metal (insufficient-evidence), Cu 2p3/2/Cu₂O (Cu⁺) (insufficient-evidence), Cu 2p3/2/CuO (Cu²⁺) (insufficient-evidence), Cu 2p3/2/Cu(OH)₂ (insufficient-evidence), Cl 2p3/2/Organic Cl (C-Cl (insufficient-evidence), Cl 2p3/2/Metal chloride (insufficient-evidence), Cl 2p3/2/ClO₄⁻ (perchlora (insufficient-evidence), Au 4f7/2/Au metal (insufficient-evidence), Au 4f7/2/Au₂O₃ (Au³⁺) (insufficient-evidence), Au 4f7/2/AuCl₃ (insufficient-evidence), S 2p3/2/Thiol (S-H) (insufficient-evidence), S 2p3/2/Sulfide (S²⁻) (insufficient-evidence), S 2p3/2/Sulfate (SO₄²⁻) (insufficient-evidence), S 2p3/2/Sulfite (SO₃²⁻) (insufficient-evidence)

## 4. Provenance & process

- Phase 1: verbatim transcription, byte-exact parity (tests/test_legacy_parity.py).
- Phase 4: dual independent extraction — 4a Claude workflow (8+6 agents) + 4b Codex (gpt-5.5) — from NIST SRD 20 Internet Archive snapshots; every value evidenced (source URL + row). Unfetchable -> status record.
- Phase 5: deterministic cross-check + tiering (context-equivalence, BE proximity).
- Phase 6: fixed-seed (20260613) third-agent audit, 26/26 PASS.
- Checkpoint A (45e2c98) + B (1a8f998): Codex adversarial reviews; findings applied.
- Parity gate green: 38 tests. Legacy constants intact; NO deletion in this report.

