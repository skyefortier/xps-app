// Find Peaks honours the Background panel's endpoint averaging (2026-09-08,
// F3 round two). Structural pins for the two frontend rules the browser test
// cannot cover for every method:
//   * runFindPeaks injects the panel value only when the method's advertised
//     default_options include endpoint_avg, and an explicit JSON value wins;
//   * _fpMethodChanged never writes endpoint_avg into the Advanced JSON view
//     (the advertised default of 1 would silently shadow the panel).
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');

test('runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins', () => {
  const start = html.indexOf('async function runFindPeaks()');
  const body = html.slice(start, start + 9000);
  assert.match(body, /default_options[^\n]*'endpoint_avg'/, 'must consult the method meta default_options');
  assert.match(body, /options\.endpoint_avg === undefined/, 'an explicit JSON value must win');
  assert.match(body, /getElementById\('bg-endpoint-avg'\)/, 'must read the Background panel');
  assert.match(body, /endpointAvg: engineEndpointAvg/, 'must record the value sent on _fpLast');
});

test('_fpMethodChanged does not write endpoint_avg into the Advanced JSON view', () => {
  const start = html.indexOf('function _fpMethodChanged()');
  const body = html.slice(start, start + 1500);
  assert.match(body, /delete shown\.endpoint_avg/);
});
