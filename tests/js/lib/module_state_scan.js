// Module-level mutable-state scanner for templates/index.html (per-tab state
// ownership guard). AST-based: parses each inline script with acorn (vendored
// dist, MIT — tests/js/lib/acorn.js + acorn.LICENSE), so declaration SYNTAX is
// not the guard's weak point. Reports:
//   * every binding introduced by let / var / const reachable from the program
//     without crossing a function or class-method boundary — top-level, inside
//     labelled statements, unbraced if/for/while bodies and top-level blocks
//     (a block-scoped `let` in a top-level block is still module-lifetime),
//     with destructuring patterns expanded;
//   * `const` bindings are skipped ONLY when the initialiser is provably not a
//     mutable container: a literal (incl. regex), a template literal, a
//     function / arrow / class expression, or a unary/binary expression of
//     those. Anything else (object, array, new, call — incl. an IIFE —,
//     conditional, identifier, member) is reported;
//   * static class fields of top-level classes, as Class.field;
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

function isProvablyImmutable(init) {
  if (!init) return false;
  switch (init.type) {
    case 'Literal': case 'TemplateLiteral': case 'ArrowFunctionExpression':
    case 'FunctionExpression': case 'ClassExpression': return true;
    case 'UnaryExpression': return isProvablyImmutable(init.argument);
    case 'BinaryExpression': return isProvablyImmutable(init.left) && isProvablyImmutable(init.right);
    default: return false;
  }
}

const FUNCTION_TYPES = new Set(['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']);

// Walk every node; `moduleScope` is true while no function boundary has been
// crossed (class bodies count as a boundary for methods, but static fields are
// reported from the class itself).
function scan(node, moduleScope, names) {
  if (!node || typeof node.type !== 'string') return;
  if (node.type === 'VariableDeclaration' && moduleScope) {
    for (const d of node.declarations) {
      if (node.kind === 'const' && isProvablyImmutable(d.init)) continue;
      for (const n of bindingNames(d.id, [])) names.add(n);
    }
  }
  if (node.type === 'ClassDeclaration' && moduleScope && node.id) {
    for (const el of node.body.body) {
      if (el.type === 'PropertyDefinition' && el.static && el.key && el.key.name) names.add(node.id.name + '.' + el.key.name);
    }
  }
  if (node.type === 'AssignmentExpression' && node.left.type === 'MemberExpression'
      && node.left.object.type === 'Identifier' && node.left.object.name === 'window'
      && node.left.property && (node.left.property.name || node.left.property.value)) {
    names.add('window.' + (node.left.property.name || node.left.property.value));
  }
  const childScope = moduleScope && !FUNCTION_TYPES.has(node.type) && node.type !== 'ClassBody';
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
