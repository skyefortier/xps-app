// Module-level mutable-state scanner for templates/index.html (per-tab state
// ownership guard). Not a full parser (none is available without a build
// step); it is a tokenizer-level scan that (1) strips comments and string /
// template literals, (2) tracks brace/paren depth so declarations are found
// at MODULE depth regardless of indentation, (3) handles comma-separated
// declarators and any initializer, (4) reports `window.<name> =` stores at
// any depth. Known limitation (documented, tested): closure state inside an
// IIFE or a long-lived function is invisible — reviewers must look for it.
'use strict';

function stripNoise(src) {
  let out = '', i = 0;
  const n = src.length;
  while (i < n) {
    const c = src[i], d = src[i + 1];
    if (c === '/' && d === '/') { while (i < n && src[i] !== '\n') i++; continue; }
    if (c === '/' && d === '*') { i += 2; while (i < n && !(src[i] === '*' && src[i + 1] === '/')) { if (src[i] === '\n') out += '\n'; i++; } i += 2; continue; }
    if (c === '"' || c === "'" || c === '`') {
      const q = c; out += q; i++;
      while (i < n && src[i] !== q) { if (src[i] === '\\') { i += 2; continue; } if (src[i] === '\n') out += '\n'; i++; }
      out += q; i++; continue;
    }
    out += c; i++;
  }
  return out;
}

// Names declared with let/var/const at depth 0 (plus window.* stores anywhere).
function scanModuleMutables(src) {
  const s = stripNoise(src);
  const names = new Set();
  let depth = 0;
  const lines = s.split('\n');
  for (const raw of lines) {
    const line = raw;
    // declarations are recognised at the depth in force at the START of the line
    if (depth === 0) {
      const m = line.match(/^\s*(let|var|const)\s+(.+?)\s*(?:;|$)/);
      if (m) {
        // split top-level declarators on commas outside brackets
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
          const init = p.slice(p.indexOf('=') + 1).trim();
          const isConst = m[1] === 'const';
          // a const bound to a primitive literal/arrow/function is not mutable state
          if (isConst && (nm[2] === '' || /^(['"`]|[-+]?\d|true|false|\(|function\b|async\b|[A-Za-z_$][\w$]*\s*=>)/.test(init)) && !/^(new\b|\[|\{|null|undefined)/.test(init)) continue;
          names.add(nm[1]);
        }
      }
    }
    for (const w of line.matchAll(/\bwindow\.([A-Za-z_$][A-Za-z0-9_$]*)\s*=[^=]/g)) names.add('window.' + w[1]);
    for (const ch of line) { if (ch === '{' || ch === '(' || ch === '[') depth++; else if (ch === '}' || ch === ')' || ch === ']') depth--; }
  }
  return [...names];
}

module.exports = { scanModuleMutables, stripNoise };
