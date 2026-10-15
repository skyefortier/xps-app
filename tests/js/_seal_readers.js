// Seal 1c step 5: the readers that consult a sealed fit — and their switch — as a harness that extracts page
// functions needs them. With the switch off (the shipped page until step 7) every one of them returns at its gate,
// so nothing behind it runs; a harness includes this source beside the functions it tests.
'use strict';
const SEAL_READER_FNS = ['_readsSeal', '_sealedDisplay', '_sealComponent', '_sealUnsupported', '_ownerOfFit', '_sealStatsState',
  '_shownStats', '_sealSig', '_sealStateText', '_sealStaleNote', '_componentArea', '_shownPeak', '_exportSealState',
  '_exportRecordOf', '_chosenOf', '_altKeyOf', '_sealDesignation', '_sealReadableView', '_sealStateOf', '_fitRoiRange', '_sealProvenanceOf', '_sealProvenanceText',
  '_isLegacyFit', '_exportFitState', '_droppedLegacyFitOf'];
// `var`: a harness may concatenate this source twice; the state wording is the page's own (read, never copied)
const fs = require('node:fs'), path = require('node:path');
const PAGE = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const pageConst = name => { const m = PAGE.match(new RegExp('^const ' + name + ' = (.*);$', 'm')); if (!m) throw new Error(name); return 'var ' + name + ' = ' + m[1] + ';'; };
const SEAL_READER_CONSTS = ['var _sealIds = new WeakMap(); var _sealIdSeq = 0; var _droppedLegacyFits = new WeakMap();', pageConst('_SEAL_NOT_PROVEN'), pageConst('_LEGACY_FIT_NOTE')].join('\n');
module.exports = (extractFn) => [SEAL_READER_CONSTS, ...SEAL_READER_FNS.map(extractFn)].join('\n');
module.exports.SEAL_READER_FNS = SEAL_READER_FNS;
