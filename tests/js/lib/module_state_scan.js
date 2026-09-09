// Module-level mutable-state scanner for templates/index.html (per-tab state
// ownership guard). Not a full parser (none is available without a build
// step); a tokenizer-level scan that:
//   (1) strips comments, string / template literals AND regex literals;
//   (2) tracks brace/paren/bracket depth so declarations are found at MODULE
//       depth regardless of indentation, one or several statements per line,
//       spanning several lines;
//   (3) handles comma-separated declarators and any initializer, including a
//       parenthesised one;
//   (4) reports `window.<name> =` stores at any depth.
// Known limitation (documented, mutation-tested): closure state inside an
// IIFE or a long-lived function is invisible — reviewers must look for it.
'use strict';

function stripNoise(src) {
  // Recursive scanner: comments, quoted strings, regex literals and template
  // literals (with nested ${ } expressions, which may themselves contain
  // strings and templates) are replaced by placeholders that keep newlines,
  // so what remains is only structural code.
  const n = src.length;
  let out = '';
  let prevSig = '';   // last significant token, to tell a regex from division
  const regexMayStart = () => prevSig === '' || '(,=:[!&|?{};+-*%<>~^'.includes(prevSig) || prevSig === 'return' || prevSig === 'typeof';
  function scanTemplate(i) {          // i at the opening backtick; returns index after the closing one
    out += '`'; i++;
    while (i < n) {
      const c = src[i];
      if (c === '\\') { i += 2; continue; }
      if (c === '`') { out += '`'; return i + 1; }
      if (c === '$' && src[i + 1] === '{') { out += '${'; i = scanCode(i + 2, true); out += '}'; continue; }
      if (c === '\n') out += '\n';
      i++;
    }
    return i;
  }
  function scanCode(i, untilBrace) {  // returns index after the unbalanced '}' when untilBrace
    let depth = 0;
    while (i < n) {
      const c = src[i], d = src[i + 1];
      if (c === '/' && d === '/') { while (i < n && src[i] !== '\n') i++; continue; }
      if (c === '/' && d === '*') { i += 2; while (i < n && !(src[i] === '*' && src[i + 1] === '/')) { if (src[i] === '\n') out += '\n'; i++; } i += 2; continue; }
      if (c === '"' || c === "'") {
        out += c; i++;
        while (i < n && src[i] !== c) { if (src[i] === '\\') { i += 2; continue; } if (src[i] === '\n') out += '\n'; i++; }
        out += c; i++; prevSig = c; continue;
      }
      if (c === '`') { i = scanTemplate(i); prevSig = '`'; continue; }
      if (c === '/' && regexMayStart()) {
        let j = i + 1, inClass = false;
        while (j < n && src[j] !== '\n') {
          if (src[j] === '\\') { j += 2; continue; }
          if (src[j] === '[') inClass = true; else if (src[j] === ']') inClass = false;
          else if (src[j] === '/' && !inClass) break;
          j++;
        }
        if (j < n && src[j] === '/') { i = j + 1; while (i < n && /[a-z]/.test(src[i])) i++; out += '/re/'; prevSig = '/'; continue; }
      }
      if (/[A-Za-z_$]/.test(c)) { const m = src.slice(i).match(/^[A-Za-z_$][\w$]*/)[0]; out += m; prevSig = m; i += m.length; continue; }
      if (untilBrace) {
        if (c === '{') depth++;
        else if (c === '}') { if (depth === 0) return i + 1; depth--; }
      }
      out += c;
      if (!/\s/.test(c)) prevSig = c;
      i++;
    }
    return i;
  }
  scanCode(0, false);
  return out;
}

// Split text into statements at depth 0 (on ';' and newlines that end a
// complete statement), tracking depth across lines.
function moduleStatements(s) {
  const stmts = [];
  let buf = '', depth = 0;
  for (const ch of s) {
    if (ch === '{' || ch === '(' || ch === '[') depth++;
    else if (ch === '}' || ch === ')' || ch === ']') depth--;
    buf += ch;
    // a statement ends at ';' at depth 0, or at a block-closing '}' at depth 0 —
    // but a '}' that closes an object INITIALISER inside a declaration
    // (`let a = {}, b = [];`) is not the end of that declaration
    const isDecl = /^\s*(let|var|const)\b/.test(buf);
    if (depth === 0 && (ch === ';' || (ch === '}' && !isDecl))) { stmts.push(buf); buf = ''; }
  }
  if (buf.trim()) stmts.push(buf);
  return stmts;
}

function scanModuleMutables(src) {
  const s = stripNoise(src);
  const names = new Set();
  for (const w of s.matchAll(/\bwindow\.([A-Za-z_$][A-Za-z0-9_$]*)\s*=[^=]/g)) names.add('window.' + w[1]);
  for (const stmt of moduleStatements(s)) {
    const m = stmt.match(/^\s*(let|var|const)\s+([\s\S]+?)\s*;?\s*$/);
    if (!m) continue;
    // split declarators on commas outside brackets
    let buf = '', d = 0;
    const parts = [];
    for (const ch of m[2]) {
      if ('([{'.includes(ch)) d++;
      if (')]}'.includes(ch)) d--;
      if (ch === ',' && d === 0) { parts.push(buf); buf = ''; } else buf += ch;
    }
    parts.push(buf);
    for (const p of parts) {
      const nm = p.match(/^\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*(=|$)/);
      if (!nm) continue;
      let init = nm[2] === '=' ? p.slice(p.indexOf('=') + 1).trim() : '';
      while (init.startsWith('(') && init.endsWith(')')) init = init.slice(1, -1).trim();   // parenthesised initialiser
      const isConst = m[1] === 'const';
      const primitive = init === '' || /^(['"`]|[-+]?\d|true|false|function\b|async\b|\/re\/|[A-Za-z_$][\w$]*\s*=>|\([^)]*\)\s*=>)/.test(init);   // '/re/' = a regex literal placeholder
      const container = /^(new\b|\[|\{|null|undefined)/.test(init);
      if (isConst && primitive && !container) continue;   // a const bound to a primitive/function is not mutable state
      names.add(nm[1]);
    }
  }
  return [...names];
}

module.exports = { scanModuleMutables, stripNoise, moduleStatements };
