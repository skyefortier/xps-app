---
name: XPS Fitting Studio
description: Instrument-grade dark UI for XPS peak fitting and survey identification
colors:
  bg-chassis: "#0d0f14"
  bg-panel: "#131720"
  bg-control: "#1a2030"
  bg-control-raised: "#212840"
  border-hairline: "#648CDC26"
  border-strong: "#648CDC4D"
  accent-signal: "#4a9eff"
  accent-signal-bright: "#7bc4ff"
  accent-dim: "#4A9EFF26"
  state-green: "#3ddc84"
  state-red: "#ff6b6b"
  state-amber: "#ffbb44"
  state-purple: "#b48eff"
  state-coral: "#ff8c66"
  state-teal: "#44ddcc"
  ink-data: "#e8edf5"
  ink-label: "#8a9ab8"
  ink-faint: "#4a5a78"
typography:
  title:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "16px"
    fontWeight: 700
    letterSpacing: "0.04em"
  body:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: "12px"
    fontWeight: 400
  data-mono:
    fontFamily: "'SF Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace"
    fontSize: "12px"
    fontWeight: 400
rounded:
  sm: "3px"
  md: "6px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "10px"
  lg: "20px"
components:
  button:
    backgroundColor: "{colors.bg-control}"
    textColor: "{colors.ink-data}"
    rounded: "{rounded.md}"
    padding: "6px 12px"
  button-hover:
    backgroundColor: "{colors.bg-control-raised}"
    textColor: "{colors.accent-signal-bright}"
  badge:
    backgroundColor: "{colors.bg-control}"
    textColor: "{colors.ink-label}"
    typography: "{typography.data-mono}"
    rounded: "{rounded.sm}"
    padding: "2px 8px"
  panel:
    backgroundColor: "{colors.bg-panel}"
    rounded: "{rounded.md}"
---

# Design System: XPS Fitting Studio

## 1. Overview

**Creative North Star: "The Instrument Panel"**

This UI is the front panel of a piece of lab instrumentation. The chassis is a
deep blue-black tonal ramp; the data — spectra, fitted peaks, reference
markers — is the only thing allowed to glow. Density is a feature: the audience
is expert, the sessions are long, and every pixel of chart area matters more
than any pixel of chrome. The system explicitly rejects marketing-site
expressiveness, dashboard theater, and any decoration that competes with the
spectrum (per PRODUCT.md's anti-references).

**Key Characteristics:**
- Dark tonal chassis (4-step background ramp), hairline borders, no shadows
- Saturated color reserved for data, markers, and state — never for chrome
- Mono font for every numeric value; sans for labels and prose
- 13px body base; compact paddings; information-dense panels
- Motion limited to ≤200ms state fades

## 2. Colors

A restrained blue-gray chassis with one signal accent and a fixed six-hue data
palette.

### Primary
- **Signal Blue** (#4a9eff): primary actions, focus rings, selection state,
  active chart elements. Brightens to **Signal Sky** (#7bc4ff) on hover text.
  Washes to **Signal Dim** (rgba(74,158,255,0.15)) for selected-row tints.

### Neutral
- **Chassis** (#0d0f14): app background.
- **Panel** (#131720): header, side panels, toolbars.
- **Control** (#1a2030): buttons, inputs, selects at rest.
- **Control Raised** (#212840): hover state of controls.
- **Hairline** (rgba(100,140,220,0.15)) / **Strong Border** (rgba(100,140,220,0.3)):
  1px borders everywhere; the strong variant for emphasized chips/badges.
- **Data Ink** (#e8edf5): primary text and numbers.
- **Label Ink** (#8a9ab8): secondary labels.
- **Faint Ink** (#4a5a78): tertiary hints, disabled text — never for body copy.

### Tertiary (data + state palette)
- **Green** (#3ddc84) success/fits · **Red** (#ff6b6b) errors · **Amber**
  (#ffbb44) warnings/NIST markers · **Purple** (#b48eff), **Coral** (#ff8c66),
  **Teal** (#44ddcc) data series. Each has a 15%-alpha dim variant for tints.
  Element markers cycle through `ELEMENT_MARKER_COLORS` (15 hues) — element
  identity color comes from that array, never invented per-feature.

### Named Rules
**The Luminous Data Rule.** Saturated color belongs to data and state only.
Chrome lives in the blue-gray ramp. If a panel element is colorful and is not
a datum, a marker, or a state, it is wrong.

**The Tint-Not-Fill Rule.** Selection and emphasis use 15%-alpha dim variants
behind full-strength text — never full-saturation fills behind dark text.

## 3. Typography

**Body Font:** system sans stack (-apple-system → Roboto)
**Data/Label Mono:** 'SF Mono' → Consolas

**Character:** quiet, technical, OS-native. The sans disappears; the mono
carries the numbers and makes them scannable and alignable.

### Hierarchy
- **Title** (700, 16px, 0.04em): app header only.
- **Section label** (600, 12-13px): panel section headers.
- **Body** (400, 13px, 1.5): controls, prose, list rows.
- **Label** (400, 12px, Label Ink): field labels, secondary text.
- **Data** (mono, 10-13px): every numeric value, badge, energy, χ², eV
  readout. 13px bold mono white for chart marker labels (with dark
  text-shadow for legibility over data).

### Named Rules
**The Mono Numbers Rule.** A numeric value rendered in the sans stack is a
defect. Energies, counts, ratios, σ — always mono.

## 4. Elevation

Flat. Depth is tonal: each layer up the stack uses the next background step
(Chassis → Panel → Control → Control Raised) plus a 1px hairline border. Box
shadows are not used; the single sanctioned shadow is a text-shadow under
chart-overlay labels so they stay legible over data traces. Modal overlays
darken the backdrop rather than lifting the dialog.

### Named Rules
**The Tonal Depth Rule.** Need depth? Take one step up the background ramp and
add a hairline border. Never a box-shadow.

## 5. Components

### Buttons
- **Shape:** softly rounded (6px), 1px hairline border.
- **Default:** Control background, Data Ink text, 12-13px.
- **Hover:** Control Raised background, Signal Blue border, Signal Sky text.
- **Focus:** 2px Signal Blue outline, 2px offset (`:focus-visible`).
- **Active/pill variants:** Signal Dim background + Signal Blue border when
  toggled on (toolbar pills).

### Badges / Chips
- **Style:** mono 12px, 2px 8px padding, 3px radius, Control background,
  Strong Border, Label Ink text. State chips use the dim variant of their
  state hue with full-strength text of the same hue.

### Panels / Containers
- **Corner Style:** 6px. **Background:** Panel. **Border:** 1px Hairline.
- **Internal padding:** 10px; section gaps 8-10px; dense list rows 4-6px.

### Inputs / Selects
- **Style:** Control background, 1px Hairline border, 6px radius, Data Ink.
- **Focus:** border becomes Signal Blue, no outline glow.

### Chart Overlays (signature)
- Vertical dashed markers (1px, marker color at ~40-60% alpha) spanning the
  chart height, with bold 12-13px mono labels staggered near the top edge,
  white (photoelectron) or muted blue-gray (Auger) with black text-shadow.
  Amber dashed style is reserved for NIST chemical-state markers. New marker
  families must key datasets/draws by stable ids, update in place, and never
  reset zoom.

### Toasts
- Small bottom toasts tinted by state hue (green/amber/red dim background,
  full-hue border + text), auto-dismiss, no motion beyond fade.

## 6. Do's and Don'ts

### Do:
- **Do** reserve saturated color for data, markers, and state (the Luminous
  Data Rule); chrome stays in the ramp #0d0f14 → #212840.
- **Do** render every numeric value in the mono stack (the Mono Numbers Rule).
- **Do** take depth from the background ramp + 1px hairlines (the Tonal Depth
  Rule).
- **Do** pair every color-coded chip with a text label — meaning is never
  color-only.
- **Do** keep panel copy in non-definitive scientific language: "candidate",
  "possible", "expected region" — provenance visible (PRODUCT.md: provenance
  everywhere).
- **Do** preserve chart zoom on every in-place update (`update('none')`).

### Don't:
- **Don't** import marketing-site expressiveness — heroes, gradient washes,
  decorative motion, glassmorphism (PRODUCT.md anti-reference, verbatim).
- **Don't** build dashboard theater: big-number cards, chartjunk, color as
  decoration (PRODUCT.md anti-reference).
- **Don't** ship UI language that says "identified as" — candidates and
  evidence only (PRODUCT.md: false certainty).
- **Don't** use gradient text. The header's `.title-xps` gradient is a legacy
  exception, frozen; never repeat the pattern.
- **Don't** put gray text on colored tints below 4.5:1, and never use Faint
  Ink (#4a5a78) for body copy.
- **Don't** animate data positions; markers appear/disappear with ≤200ms
  fades or instantly, and reduced-motion users get instant.
