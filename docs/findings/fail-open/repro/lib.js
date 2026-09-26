const fs = require('fs');
const html = fs.readFileSync('/Users/skyefortier/xps-app/templates/index.html', 'utf8');
const lines = html.split('\n');
function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name + '\\(');
  const start = lines.findIndex(l => re.test(l));
  if (start < 0) throw new Error('not found ' + name);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
}
function extractConst(name) {
  const l = lines.find(l => l.startsWith('const ' + name + ' '));
  if (!l) throw new Error('const ' + name);
  return l;
}
module.exports = { extractFn, extractConst, lines, html };
