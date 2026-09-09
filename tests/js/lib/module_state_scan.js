// Module-level mutable-state scanner for templates/index.html (per-tab state
// ownership guard). AST-based: parses each inline script with acorn (vendored
// dist, MIT — tests/js/lib/acorn.js + acorn.LICENSE), so declaration SYNTAX is
// not the guard's weak point. Reports:
//   * every binding introduced by let / var / const reachable from the program
//     without crossing a function or class-method boundary — top-level, inside
//     labelled statements, unbraced if/for/while bodies and top-level blocks
//     (a block-scoped `let` in a top-level block is still module-lifetime),
//     with destructuring patterns expanded;
//   * a `const` binding is skipped ONLY when it is a plain identifier AND the
//     initialiser is provably not a mutable container: a non-regex literal
//     (a RegExp literal is an object — lastIndex is writable — and is
//     reported), a template literal, a function / arrow expression, a class
//     expression WITHOUT static state, or a unary/binary expression of those.
//     Anything else (object, array, new, call — incl. an IIFE —, conditional,
//     identifier, member) is reported; destructuring patterns are always
//     expanded and reported (defaults/rest can hold containers);
//   * static state of classes (declarations, and expressions bound by a
//     declarator): static fields with identifier / string / computed keys as
//     Class.field, and declarations inside static blocks as Class.name;
//   * `window.<name> = …` assignments anywhere (functions included).
// Documented limitation: state captured in a closure (inside an IIFE or a
// long-lived function) is invisible; the async-ownership rule is what covers
// locals that outlive a tab.
'use strict';
const acorn = require('./acorn.js');

function bindingNames(pattern, out) {
  if (!pattern) return out;
  switch (pattern.type) {
    case 'Identifier': out.push(pattern.name); break;
    case 'ObjectPattern': for (const p of pattern.properties) bindingNames(p.type === 'RestElement' ? p.argument : p.value, out); break;
    case 'ArrayPattern': for (const e of pattern.elements) bindingNames(e, out); break;
    case 'AssignmentPattern': bindingNames(pattern.left, out); break;
    case 'RestElement': bindingNames(pattern.argument, out); break;
  }
  return out;
}

// A class holds module-lifetime state if it has static fields or a static
// block — or inherits them from a superclass EXPRESSION written inline.
function classHasStaticState(cls) {
  if (cls.body.body.some(el => (el.type === 'PropertyDefinition' && el.static) || el.type === 'StaticBlock')) return true;
  return !!(cls.superClass && cls.superClass.type === 'ClassExpression' && classHasStaticState(cls.superClass));
}

// Class expressions already reported through a declarator or a superclass
// position are not reported again as anonymous classes.
const consumedClasses = new WeakSet();

function isProvablyImmutable(init) {
  if (!init) return false;
  switch (init.type) {
    case 'Literal': return !init.regex;      // a RegExp literal is a mutable object (lastIndex is writable)
    case 'TemplateLiteral': case 'ArrowFunctionExpression':
    case 'FunctionExpression': return true;
    case 'ClassExpression': return !classHasStaticState(init);   // a class with static fields IS a store
    case 'UnaryExpression': return isProvablyImmutable(init.argument);
    case 'BinaryExpression': return isProvablyImmutable(init.left) && isProvablyImmutable(init.right);
    default: return false;
  }
}

function staticKeyName(el) {
  if (el.key.type === 'Literal') return String(el.key.value);      // "store" or ["store"]
  if (!el.computed && el.key.type === 'Identifier') return el.key.name;
  return '[computed]';                                             // [Symbol.for('x')], [expr]
}

// Report a class's module-lifetime state under `<binding>.<member>`: every
// static field (identifier, string or computed key); every static block as a
// whole (`<binding>.[static block]` — what it assigns cannot be enumerated)
// plus any declarations inside it; and, recursively, the static state of an
// inline superclass expression, attributed to the subclass (it is reachable
// as `<binding>.<member>` at runtime). Conservative by construction: a class
// with any static state is always reported under SOME name, and an unbound
// class expression gets '[anonymous class]', which cannot be allowlisted.
function reportClass(name, cls, names) {
  consumedClasses.add(cls);
  for (const el of cls.body.body) {
    if (el.type === 'PropertyDefinition' && el.static) names.add(name + '.' + staticKeyName(el));
    if (el.type === 'StaticBlock') {
      names.add(name + '.[static block]');
      const inner = new Set();
      for (const st of el.body) scan(st, true, inner);
      for (const n of inner) names.add(n.startsWith('window.') ? n : name + '.' + n);
    }
  }
  if (cls.superClass && cls.superClass.type === 'ClassExpression') reportClass(name, cls.superClass, names);
}

const FUNCTION_TYPES = new Set(['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']);

// Walk every node; `moduleScope` is true while no function boundary has been
// crossed (class bodies count as a boundary for methods; static state is
// reported through reportClass).
function scan(node, moduleScope, names) {
  if (!node || typeof node.type !== 'string') return;
  if (node.type === 'VariableDeclaration' && moduleScope) {
    for (const d of node.declarations) {
      // The provably-immutable exemption applies ONLY to a plain identifier
      // binding: a destructuring pattern can introduce containers through
      // defaults or rest whatever the right-hand side is (Codex round 4).
      if (d.id.type === 'Identifier' && node.kind === 'const' && isProvablyImmutable(d.init)) continue;
      if (d.id.type === 'Identifier' && d.init && d.init.type === 'ClassExpression') {
        reportClass(d.id.name, d.init, names);
        if (node.kind === 'const') continue;    // the binding itself is constant; its static state is what we reported
      }
      for (const n of bindingNames(d.id, [])) names.add(n);
    }
  }
  if (node.type === 'CatchClause' && moduleScope && node.param) {
    for (const n of bindingNames(node.param, [])) names.add(n);   // catch bindings are declarations too
  }
  if (node.type === 'ClassDeclaration' && moduleScope && node.id) reportClass(node.id.name, node, names);
  if (node.type === 'ClassExpression' && moduleScope && !consumedClasses.has(node) && classHasStaticState(node)) {
    reportClass('[anonymous class]', node, names);
  }
  if (node.type === 'AssignmentExpression' && node.left.type === 'MemberExpression'
      && node.left.object.type === 'Identifier' && node.left.object.name === 'window'
      && node.left.property && (node.left.property.name || node.left.property.value)) {
    names.add('window.' + (node.left.property.name || node.left.property.value));
  }
  if (node.type === 'ClassBody') {
    // Computed keys and STATIC field initialisers are evaluated once, at class
    // definition time, in the enclosing scope; method bodies and instance
    // field initialisers are function-like (Codex round 6).
    for (const el of node.body) {
      if (el.computed && el.key) scan(el.key, moduleScope, names);
      if (el.type === 'PropertyDefinition' && el.static && el.value) scan(el.value, moduleScope, names);
      if (el.type === 'StaticBlock') for (const st of el.body) scan(st, moduleScope, names);
      if (el.type === 'MethodDefinition' && el.value) scan(el.value, false, names);
      if (el.type === 'PropertyDefinition' && !el.static && el.value) scan(el.value, false, names);
    }
    return;
  }
  const childScope = moduleScope && !FUNCTION_TYPES.has(node.type);
  for (const key of Object.keys(node)) {
    if (key === 'type' || key === 'start' || key === 'end' || key === 'loc') continue;
    const v = node[key];
    if (Array.isArray(v)) { for (const c of v) if (c && typeof c.type === 'string') scan(c, childScope, names); }
    else if (v && typeof v.type === 'string') scan(v, childScope, names);
  }
}

function scanModuleMutables(src) {
  const ast = acorn.parse(src, { ecmaVersion: 'latest', sourceType: 'script', allowHashBang: true });
  const names = new Set();
  scan(ast, true, names);
  return [...names];
}

// The inline scripts of templates/index.html — a Jinja template: `{{ expr }}`
// interpolations (server-injected JSON) are replaced by `null` and `{% %}`
// blocks removed so the scripts parse as plain JavaScript.
function inlineScripts(html) {
  return [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)]
    .map(m => m[1].replace(/\{%[\s\S]*?%\}/g, '').replace(/\{\{[\s\S]*?\}\}/g, 'null'));
}

module.exports = { scanModuleMutables, inlineScripts };
