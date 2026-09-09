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
  assert.ok(!finds('const RE = /^[a-z]+$/i;', 'RE'));   // a regex literal is a constant, not state
  assert.ok(!finds('const obj = (function(){ let inner = []; return {}; })();', 'inner'));   // documented limitation: closure state
});
test('comments and strings cannot hide or fake a declaration', () => {
  assert.ok(!finds('// let fake = [];', 'fake'));
  assert.ok(!finds('const s = "let fake2 = [];";', 'fake2'));
  assert.ok(finds('/* c */ let real = [];', 'real'));
});

// Codex round 2 (both runs): forms the first scanner missed.
test('two declarations on one line, multiline declarators, parenthesised initialisers', () => {
  assert.ok(finds('let first = []; let hidden4 = [];', 'hidden4'));
  assert.ok(finds('let a = 1,\n    hidden5 = [],\n    c = 2;', 'hidden5'));
  assert.ok(finds('const hidden6 = ([]);', 'hidden6'));
  assert.ok(finds('const hidden7 = {\n  peaks: [],\n};\nlet after = [];', 'after'));
});
test('a regex literal containing a brace does not corrupt depth tracking', () => {
  assert.ok(finds("const re = /\\{[^}]*\\}/g;\nlet hidden8 = [];", 'hidden8'));
  assert.ok(finds("function f(x) { return x.replace(/[{}]/g, ''); }\nlet hidden9 = [];", 'hidden9'));
  assert.ok(!finds("const q = 6 / 2 / 1;\nlet ok = [];", 'nothing'));
});
test('appending a forbidden declaration to a real inline script is found', () => {
  const fs = require('node:fs'); const path = require('node:path');
  const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
  const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  for (const sc of scripts) {
    assert.ok(scanModuleMutables(sc + '\nlet ROUND2_FORBIDDEN = [];').includes('ROUND2_FORBIDDEN'));
  }
});

test('nested template literals (the renderPeakForm pattern) do not desynchronise the scan', () => {
  const src = 'function r(p) {\n  return `<a>${p.x ? `<b>${p.y}</b>` : \'\'}</a>`;\n}\nlet hidden10 = [];';
  assert.ok(finds(src, 'hidden10'));
  assert.ok(finds('const t = `${ {a:1}.a }`;\nlet hidden11 = [];', 'hidden11'));
});
