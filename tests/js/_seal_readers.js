// Seal 1c step 5: the readers that consult a sealed fit — and their switch — as a harness that extracts page
// functions needs them. With the switch off (the shipped page until step 7) every one of them returns at its gate,
// so nothing behind it runs; a harness includes this source beside the functions it tests.
'use strict';
const SEAL_READER_FNS = ['_readsSeal', '_sealedDisplay', '_sealComponent', '_sealUnsupported', '_ownerOfFit', '_sealStatsState',
  '_shownStats', '_sealSig', '_sealStateText', '_sealStaleNote', '_componentArea', '_shownPeak', '_exportSealState',
  '_exportRecordOf', '_chosenOf', '_altKeyOf', '_sealDesignation', '_sealReadableView', '_sealStateOf', '_fitRoiRange', '_sealProvenanceOf', '_sealProvenanceText'];
// `var`: a harness may concatenate this source twice
const SEAL_READER_CONSTS = 'var _SEAL_AUTHORITATIVE = false; var _sealIds = new WeakMap(); var _sealIdSeq = 0;';
module.exports = (extractFn) => [SEAL_READER_CONSTS, ...SEAL_READER_FNS.map(extractFn)].join('\n');
module.exports.SEAL_READER_FNS = SEAL_READER_FNS;
