# Product

## Register

product

## Users

XPS spectroscopists in an academic lab: the PI and graduate students working up
survey and high-resolution spectra at a desktop, usually with reference
handbooks or NIST open in a second window. Deep XPS literacy, mixed software
literacy. Deployed at xps.fortierlab.org; sessions are long, focused,
task-driven (fit this spectrum, identify that peak, quantify this surface).

## Product Purpose

Web application for XPS peak fitting, multi-spectrum visualization, and project
management. The periodic-table feature adds elemental orientation and survey
identification: click an element to see where its lines should fall on the live
spectrum; click a survey peak to get ranked candidate assignments with
evidence. Success = a student identifies survey peaks confidently without
leaving the app, and every number on screen can say where it came from.

## Brand Personality

Precise, quiet, trustworthy. A piece of lab instrumentation, not a web product:
the spectrum is the protagonist, the chrome is the chassis.

## Anti-references

- Marketing-site expressiveness: hero sections, gradient washes, decorative
  motion, "delight" flourishes.
- Dashboard theater: big-number cards, chartjunk, color as decoration.
- Bolted-on panels that import a foreign visual language instead of the app's.
- False certainty: any UI language that says "identified as" instead of
  "candidate"; uncertainty and provenance are information, never hidden.

## Design Principles

1. **Data is the interface.** The chart gets the space and the saturation;
   controls recede into the tonal chassis.
2. **Provenance everywhere.** Every numeric value can surface its source
   (citation ids, NIST reference codes, curation notes) without leaving the
   screen.
3. **Non-definitive language.** Candidates, evidence, confidence — never
   verdicts. Caveats (uncurated data, uncorrected charge) are shown, not
   suppressed.
4. **Density with hierarchy.** Information-dense panels are correct for this
   audience; hierarchy comes from type weight, mono-for-numbers, and tonal
   steps — not from whitespace inflation.
5. **Native, not bolted-on.** New features inherit the existing control-panel,
   chart, and color vocabulary exactly.

## Accessibility & Inclusion

WCAG AA contrast on the dark theme (body text ≥4.5:1). Meaning is never
color-only: strength/state chips carry text labels alongside hue. Click
targets in dense controls stay ≥24px wherever the periodic-table grid allows,
with a search/autocomplete alternative for fine-grid selection. Motion is
minimal (≤200ms state fades) and respects `prefers-reduced-motion`. Numeric
displays use the mono stack so values align and misreads are rare.
