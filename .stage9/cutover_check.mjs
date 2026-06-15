// Stage 9 cutover verification. argv[2]=rendered index.html, argv[3]=fixture.
// Runs the POST-CUTOVER accessor (constants absent) and checks:
//   - semantic parity BY ID vs the immutable fixture (order-independent)
//   - chem output shape is EXACTLY {state,be,ref} (no tier leak)
//   - computed value-diff vs fixture is EMPTY (verbatim parity; any unlisted
//     delta fails) — the legacy values are served unchanged
//   - the constants are genuinely absent from the served page
import { readFileSync } from 'node:fs';

const html = readFileSync(process.argv[2], 'utf8');
const fixture = JSON.parse(readFileSync(process.argv[3], 'utf8'));

function grab(re, label) {
  const m = html.match(re);
  if (!m) throw new Error('missing ' + label);
  return m[1] !== undefined ? m[1] : m[0];
}

const legacyRef = grab(/const LEGACY_REFERENCE = (.+?);\n/, 'LEGACY_REFERENCE');
const okExpr = grab(/const LEGACY_REFERENCE_OK = ([\s\S]*?);\n/, 'LEGACY_REFERENCE_OK');
const fnSurvey = grab(/(function _accSurveyElements\(\) \{[\s\S]*?\n\})/, 'survey fn');
const fnChem = grab(/(function _accChemicalStates\(\) \{[\s\S]*?\n\})/, 'chem fn');

const r = new Function(`
  let _accSurveyCache=null,_accChemCache=null,_refUnavailableNotified=false;
  function _accReferenceUnavailable(){_refUnavailableNotified=true;return true;}
  const LEGACY_REFERENCE=${legacyRef};
  const LEGACY_REFERENCE_OK=${okExpr};
  ${fnSurvey}
  ${fnChem}
  return {survey:_accSurveyElements(),chem:_accChemicalStates(),ok:LEGACY_REFERENCE_OK,notified:_refUnavailableNotified};
`)();

const diff = [];
// survey parity by element id (stable), order-independent
for (const sym of Object.keys(fixture.XPS_ELEMENTS))
  if (JSON.stringify(r.survey[sym]) !== JSON.stringify(fixture.XPS_ELEMENTS[sym])) diff.push('survey:' + sym);
for (const sym of Object.keys(r.survey))
  if (!(sym in fixture.XPS_ELEMENTS)) diff.push('survey-extra:' + sym);
// chem parity by orbital_key + EXACT shape {state,be,ref}
for (const k of Object.keys(fixture.CHEMICAL_STATES)) {
  const exp = fixture.CHEMICAL_STATES[k], got = r.chem[k];
  if (!got || got.length !== exp.length) { diff.push('chem-len:' + k); continue; }
  got.forEach((g, i) => {
    if (Object.keys(g).sort().join(',') !== 'be,ref,state') diff.push('chem-shape:' + k + '#' + i);
    else if (g.state !== exp[i].state || g.be !== exp[i].be || g.ref !== exp[i].ref) diff.push('chem-val:' + k + '#' + i);
  });
}
for (const k of Object.keys(r.chem))
  if (!(k in fixture.CHEMICAL_STATES)) diff.push('chem-extra:' + k);

const constantsAbsent = !/const\s+(XPS_ELEMENTS|CHEMICAL_STATES|_XPS_REMOVED\w*)\s*=/.test(html);
const pass = diff.length === 0 && constantsAbsent && r.ok === true;
console.log(JSON.stringify({ pass, ok: r.ok, constantsAbsent, value_diff_count: diff.length, value_diff: diff.slice(0, 12) }));
process.exit(pass ? 0 : 1);
