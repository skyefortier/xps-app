// Codex CkptA #4: exercise the REAL frontend accessor functions
// (_accSurveyElements / _accChemicalStates) against the legacy constants,
// using the server-rendered page (so LEGACY_REFERENCE is the injected data).
// Extracts the exact declarations from the rendered HTML, evals them in an
// isolated context, and deep-compares accessor output to the constants.
// argv[2] = path to rendered index.html. Prints OK/FAIL, exits 0/1.
import { readFileSync } from 'node:fs';

const html = readFileSync(process.argv[2], 'utf8');

function grab(re, label) {
  const m = html.match(re);
  if (!m) throw new Error('could not extract ' + label);
  return m[1] !== undefined ? m[1] : m[0];
}

const legacyRef = grab(/const LEGACY_REFERENCE = (.+?);\n/, 'LEGACY_REFERENCE');
const fnSurvey = grab(/(function _accSurveyElements\(\) \{[\s\S]*?\n\})/, '_accSurveyElements');
const fnChem = grab(/(function _accChemicalStates\(\) \{[\s\S]*?\n\})/, '_accChemicalStates');
const xpsEl = grab(/const XPS_ELEMENTS = (\{[\s\S]*?\n\});/, 'XPS_ELEMENTS');
const chemStates = grab(/const CHEMICAL_STATES = (\{[\s\S]*?\n\});/, 'CHEMICAL_STATES');

const body = `
  let _accSurveyCache = null, _accChemCache = null;
  const LEGACY_REFERENCE = ${legacyRef};
  const XPS_ELEMENTS = ${xpsEl};
  const CHEMICAL_STATES = ${chemStates};
  ${fnSurvey}
  ${fnChem}
  const accSurvey = _accSurveyElements();
  const accChem = _accChemicalStates();
  // accessor adds a tier field to chem states — strip for shape parity
  const accChemStripped = {};
  for (const k in accChem) accChemStripped[k] = accChem[k].map(s => ({ state: s.state, be: s.be, ref: s.ref }));
  return {
    surveyEqual: JSON.stringify(accSurvey) === JSON.stringify(XPS_ELEMENTS),
    chemEqual: JSON.stringify(accChemStripped) === JSON.stringify(CHEMICAL_STATES),
    accSurveyKeys: Object.keys(accSurvey).length,
    conSurveyKeys: Object.keys(XPS_ELEMENTS).length,
  };
`;
// eslint-disable-next-line no-new-func
const result = new Function(body)();

if (result.surveyEqual && result.chemEqual) {
  console.log('ACCESSOR_PARITY_OK survey=' + result.accSurveyKeys + '/' + result.conSurveyKeys);
  process.exit(0);
} else {
  console.log('ACCESSOR_PARITY_FAIL survey=' + result.surveyEqual + ' chem=' + result.chemEqual);
  process.exit(1);
}
