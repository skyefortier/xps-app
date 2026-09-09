// Mutation tests for the AST scanner behind per_tab_state.test.js: every
// forbidden form MUST be found, so the allowlist cannot be evaded by syntax.
// The scanner parses with acorn (vendored, MIT) — a real parser, so the
// "another declaration form" class is closed rather than chased.
const { test } = require('node:test');
const assert = require('node:assert');
const { scanModuleMutables, inlineScripts } = require('./lib/module_state_scan');

const finds = (src, name) => scanModuleMutables(src).includes(name);

test('plain, indented, multi-declarator, same-line, multiline, ASI declarations', () => {
  assert.ok(finds('    let hidden = [];', 'hidden'));
  assert.ok(finds('let state = {}, hidden2 = [];', 'hidden2'));
  assert.ok(finds('var a;', 'a'));
  assert.ok(finds('let first = []; let hidden4 = [];', 'hidden4'));
  assert.ok(finds('let a = 1,\n    hidden5 = [],\n    c = 2;', 'hidden5'));
  assert.ok(finds('let harmless = []\nlet hidden12 = []', 'hidden12'));            // no semicolons (ASI)
});
test('populated containers, ALL_CAPS containers, parenthesised and conditional initialisers', () => {
  assert.ok(finds('const stash = { peaks: [] };', 'stash'));
  assert.ok(finds('const CACHE = [];', 'CACHE'));
  assert.ok(finds('const hidden6 = ([]);', 'hidden6'));
  assert.ok(finds('const hidden13 = true ? [] : [];', 'hidden13'));
  assert.ok(finds('const m = new Map();', 'm'));
  assert.ok(finds('const hidden14 = (function () { return []; })();', 'hidden14'));   // IIFE returning a container
});
test('destructuring, labelled, unbraced-if, top-level block and static class fields', () => {
  assert.ok(finds('const {hidden15} = {hidden15: []};', 'hidden15'));
  assert.ok(finds('const [hidden16] = [[]];', 'hidden16'));
  assert.ok(finds('outer: var hidden17 = [];', 'hidden17'));
  assert.ok(finds('if (true) var hidden18 = [];', 'hidden18'));
  assert.ok(finds('{ var hidden19 = []; }', 'hidden19'));
  assert.ok(finds('{ let hidden20 = []; }', 'hidden20'));                          // block-scoped but module-lifetime
  assert.ok(finds('class K { static store = []; }', 'K.store'));
  assert.ok(finds('function f() { window.hidden3 = []; }', 'window.hidden3'));
});
test('function-local declarations and primitive consts are not module state', () => {
  assert.ok(!finds('function f() {\n  let local = [];\n}', 'local'));
  assert.ok(!finds('const N = 50;', 'N'));
  assert.ok(!finds("const S = 'x';", 'S'));
  assert.ok(!finds('const fn = () => 1;', 'fn'));
  assert.ok(!finds('const RE = /^[a-z]+$/i;', 'RE'));
  assert.ok(!finds('const T = `a${1}b`;', 'T'));
  assert.ok(!finds('const obj = (function(){ let inner = []; return {}; })();', 'inner'));   // documented limitation: closure state
});
test('comments, strings, regex and nested template literals cannot hide or fake a declaration', () => {
  assert.ok(!finds('// let fake = [];', 'fake'));
  assert.ok(!finds('const s = "let fake2 = [];";', 'fake2'));
  assert.ok(finds('/* c */ let real = [];', 'real'));
  assert.ok(finds("const re = /\\{[^}]*\\}/g;\nlet hidden8 = [];", 'hidden8'));
  assert.ok(finds('if (x) y = /[{]/.test(z)\nlet hidden21 = [];', 'hidden21'));       // regex after an unbraced if
  const src = 'function r(p) {\n  return `<a>${p.x ? `<b>${p.y}</b>` : \'\'}</a>`;\n}\nlet hidden10 = [];';
  assert.ok(finds(src, 'hidden10'));
});
test('appending a forbidden declaration to each real inline script is found', () => {
  const fs = require('node:fs'); const path = require('node:path');
  const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
  const scripts = inlineScripts(html);
  assert.ok(scripts.length >= 2);
  for (const sc of scripts) {
    for (const form of ['\nlet ROUND2_FORBIDDEN = [];', '\nconst [ROUND3_FORBIDDEN] = [[]];', '\n{ var ROUND3_FORBIDDEN = []; }', '\nlet harmless = []\nlet ROUND3_FORBIDDEN = [];']) {
      const found = scanModuleMutables(sc + form);
      assert.ok(found.includes('ROUND2_FORBIDDEN') || found.includes('ROUND3_FORBIDDEN'), form);
    }
  }
});

// Codex round 4 (both runs): destructuring defaults/rest behind a primitive
// right-hand side, static fields with string/computed keys, class expressions,
// static blocks.
test('destructuring defaults and rest create containers even when the right-hand side is primitive', () => {
  assert.ok(finds('const {stash = []} = 0;', 'stash'));
  assert.ok(finds('const [...stash2] = "";', 'stash2'));
  assert.ok(finds('const {a: {deep = {}} = {}} = 0;', 'deep'));
});
test('static fields with string or computed keys, class expressions and static blocks are reported', () => {
  assert.ok(finds('class K { static "store" = []; }', 'K.store'));
  assert.ok(finds('class K { static ["store2"] = []; }', 'K.store2'));
  assert.ok(finds('const K = class { static store3 = []; };', 'K.store3'));
  assert.ok(finds('let K = class Named { static store4 = []; };', 'K.store4'));
  assert.ok(finds('class K { static { var inBlock = []; } }', 'K.inBlock'));
  assert.ok(finds('class K { static [Symbol.for("x")] = []; }', 'K.[computed]'));
});
test('a const whose initialiser is a class expression WITH static fields is not skipped', () => {
  assert.ok(finds('const Holder = class { static list = []; };', 'Holder.list'));
  assert.ok(!finds('const Pure = class { m() { return 1; } };', 'Pure'));
});
