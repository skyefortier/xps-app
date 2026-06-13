// Phase 1 verbatim extractor. Reads the real JS constant literals out of
// templates/index.html and evals them in Node (exact same parser that runs
// them in the browser), so transcription is byte-faithful — no hand-copying,
// no regex value-munging. Emits raw JSON dumps for the transcriber to wrap.
import { readFileSync, writeFileSync } from 'node:fs';

const html = readFileSync('templates/index.html', 'utf8');

function grab(name, open, close) {
  // Match `const NAME = <open> ... \n<close>;` (first line-start terminator).
  const re = new RegExp('const ' + name + ' = (' +
    open.replace('[', '\\[').replace('{', '\\{') +
    '[\\s\\S]*?\\n' + close.replace(']', '\\]').replace('}', '\\}') + ');');
  const m = html.match(re);
  if (!m) throw new Error('could not locate ' + name);
  // eslint-disable-next-line no-eval
  return eval('(' + m[1] + ')');
}

const XPS_ELEMENTS = grab('XPS_ELEMENTS', '{', '}');
const ELEMENT_NAMES = grab('ELEMENT_NAMES', '{', '}');
const ELEMENT_MARKER_COLORS = grab('ELEMENT_MARKER_COLORS', '[', ']');
const CHEMICAL_STATES = grab('CHEMICAL_STATES', '{', '}');

const out = { XPS_ELEMENTS, ELEMENT_NAMES, ELEMENT_MARKER_COLORS, CHEMICAL_STATES };
writeFileSync('.stage9/legacy_raw.json', JSON.stringify(out, null, 2));

// Integrity summary for the audit trail.
const nEl = Object.keys(XPS_ELEMENTS).length;
const nLines = Object.values(XPS_ELEMENTS).reduce((a, e) => a + Object.keys(e.lines).length, 0);
const nGroups = Object.keys(CHEMICAL_STATES).length;
const nStates = Object.values(CHEMICAL_STATES).reduce((a, s) => a + s.length, 0);
console.log(JSON.stringify({ nEl, nLines, nGroups, nStates,
  nNames: Object.keys(ELEMENT_NAMES).length, nColors: ELEMENT_MARKER_COLORS.length }));
