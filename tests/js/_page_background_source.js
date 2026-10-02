// The page's background section as one evaluable source string, for tests that
// run the page's own background code (background math, 2026-10-01: the twins
// share helpers and constants, so a test that extracted the old named
// functions alone would miss them). Usage:
//   const src = require('./_page_background_source.js')();
//   const B = new Function(src + '\nreturn { computeBackgroundCore, _bgFailure };')();
const fs = require('node:fs');
const path = require('node:path');

const FUNCTIONS = [
  '_npPairwiseSum', '_npMean', '_bgEdgeLevels', '_bgAscending', '_bgSpan', '_npLinspace',
  '_bgCumFromHigh', '_bgShirleyMap', '_bgMaxAbsDiff', 'shirleyBackground', 'smartBackground',
  'smartExperimentalBackground', '_bgLineFailure', '_bgAnchorFailure', '_bgExact', '_bgBitLen', '_bgRatToDouble', '_bgExactLine', '_bgRoundingWithin', '_bgExactSpan', '_bgPrecisionWords', 'linearBackground', '_tougaardLoss', 'tougaardBackground',
  '_bgCertificate', '_bgExactShirleyCertificate', '_tougaardRoundingBound', '_tougaardZeroLossVerdict', '_bgPow2Exp', '_bgLdexp', '_fmt3', '_applyEndpointAveraging', 'shirleyLinearBackground', '_bgWindowIndices',
  '_bgMark', '_bgFailure', 'BgNotConverged', '_isBgNotConverged', '_certifiedBg', '_bgOrFailure',
  'computeBackgroundCore', '_computeBackgroundUnchecked',
];
const CONSTANTS = ['BG_REL_TOL', 'BG_MAX_ITER', 'BG_LABELS', '_TOUGAARD_CANCELS', '_TOUGAARD_NO_AMPLITUDE'];

module.exports = function pageBackgroundSource({ manual = 'stub' } = {}) {
  const lines = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8').split('\n');
  const take = (start) => {
    let depth = 0, seen = false;
    for (let i = start; i < lines.length; i++) {
      for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
      if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
      if (!seen && /;\s*$/.test(lines[i])) return lines.slice(start, i + 1).join('\n');
    }
    throw new Error('unbalanced at line ' + (start + 1));
  };
  const out = [];
  for (const c of CONSTANTS) {
    const i = lines.findIndex(l => l.startsWith('const ' + c + ' ='));
    if (i < 0) throw new Error('constant ' + c + ' not found');
    out.push(take(i));
  }
  for (const f of FUNCTIONS) {
    const re = new RegExp('^(async )?function ' + f + '\\(');
    const i = lines.findIndex(l => re.test(l));
    if (i < 0) throw new Error('function ' + f + ' not found');
    out.push(take(i));
  }
  if (manual === 'stub') out.push('const manualAnchorBackground = () => { throw new Error("not in this test"); };');
  return out.join('\n');
};
