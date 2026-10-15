// Seal 1c step 7: the seal layer as a FLOW harness needs it — Auto-Fit's staged transaction and Run Fit's producer
// check answered "consistent" by stubs, so a harness can exercise the producer's own flow (discards, rollbacks,
// refusals, the order of its steps). The seal machinery itself is pinned by the browser tests
// (tests/test_browser_seal_step*.py); these stubs never stand in for it there.
'use strict';
module.exports = () => ({
  _beginStaged: () => ({}),
  _verifyStagedCheck: async () => ({ state: 'consistent', counts: true }),
  _aggregateVerdicts: vs => vs.find(v => v && v.state === 'mismatch') || vs.find(v => v && v.unreachable) || vs[0],
  _outcomeCounts: () => true,
  _commitStaged: () => ({ committed: true }),
  sealedState: () => ({ state: 'current', check: null, reason: '', view: null }),
  _sealView: seal => ({ statistics: { chi2r: seal && seal.O && seal.O.statistics ? seal.O.statistics.reduced_chi_square : 1 } }),
  _abandonStaged() {},
  _onSealVerdict() {},
  _verifySeal: () => null,
  _fitRoiRange: () => null,
});
// As SOURCE for a harness that assembles page functions into one `new Function` body: each stub is declared only
// where the harness supplies no function of that name (a `var` redeclaring a parameter keeps the parameter).
module.exports.source = () => Object.entries(module.exports()).map(([k, v]) =>
  `var ${k} = typeof ${k} !== 'undefined' ? ${k} : (${typeof v === 'function' ? v.toString().replace(/^(async )?(\w+)\(\) \{\}$/, '$1function () {}') : JSON.stringify(v)});`).join('\n');
