// Mutation tests for the scanner behind per_tab_state.test.js: each forbidden
// example MUST be found, so the allowlist cannot be evaded by formatting.
const { test } = require('node:test');
const assert = require('node:assert');
const { scanModuleMutables } = require('./lib/module_state_scan');

const finds = (src, name) => scanModuleMutables(src).includes(name);

test('indented and multi-declarator module declarations are found', () => {
  assert.ok(finds('    let hidden = [];', 'hidden'));
  assert.ok(finds('let state = {}, hidden2 = [];', 'hidden2'));
  assert.ok(finds('var a;', 'a'));
});
test('populated containers, ALL_CAPS containers and window stores are found', () => {
  assert.ok(finds('const stash = { peaks: [] };', 'stash'));
  assert.ok(finds('const CACHE = [];', 'CACHE'));
  assert.ok(finds('function f() { window.hidden3 = []; }', 'window.hidden3'));
  assert.ok(finds('const m = new Map();', 'm'));
});
test('function-local declarations and primitive consts are not module state', () => {
  assert.ok(!finds('function f() {\n  let local = [];\n}', 'local'));
  assert.ok(!finds('const N = 50;', 'N'));
  assert.ok(!finds("const S = 'x';", 'S'));
  assert.ok(!finds('const fn = () => 1;', 'fn'));
  assert.ok(!finds('const obj = (function(){ let inner = []; return {}; })();', 'inner'));   // documented limitation: closure state
});
test('comments and strings cannot hide or fake a declaration', () => {
  assert.ok(!finds('// let fake = [];', 'fake'));
  assert.ok(!finds('const s = "let fake2 = [];";', 'fake2'));
  assert.ok(finds('/* c */ let real = [];', 'real'));
});
