#!/usr/bin/env node
// Q10 0c′ (owner 2026-10-11): the page refuses a link graph the server cannot fit as drawn — a
// link to a peak that is gone, a self-link, a cycle, a link across lineshapes, two peaks sharing
// an id. Claim: no committed model is refused. This runs the page's own _linkGraphFailure on the
// saved peaks of every tab in every committed project and counts links and refusals.
// Usage: node scripts/link_graph_census.js. Writes docs/findings/link-graph/census.json.
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const REPO = path.join(__dirname, '..');
const PY = [path.join(REPO, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p)) || 'python3';

const lines = fs.readFileSync(path.join(REPO, 'templates/index.html'), 'utf8').split('\n');
const start = lines.findIndex(l => /^function _linkGraphFailure\(/.test(l));
if (start < 0) throw new Error('missing _linkGraphFailure');
let end = start, depth = 0, seen = false;
for (; end < lines.length; end++) {
  for (const ch of lines[end]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
  if (seen && depth === 0) break;
}
const linkGraphFailure = new Function(lines.slice(start, end + 1).join('\n') + '\nreturn _linkGraphFailure;')();

const script = 'import glob, json, sys; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs\n' +
  'out = []\nfor f in sorted(glob.glob(sys.argv[1] + "/docs/autofit/test_data/**/*.proj.*", recursive=True)):\n' +
  '    for t in load_project_tabs(f):\n        if not t.get("isStack") and t.get("peaks"):\n' +
  '            out.append({"file": f.split("/")[-1], "name": t.get("name"), "peaks": t["peaks"]})\n' +
  'print(json.dumps(out))';
const tabs = JSON.parse(execFileSync(PY, ['-c', script, REPO], { encoding: 'utf8', maxBuffer: 256 << 20 }));

const refused = [];
let links = 0, linkedTabs = 0, peaks = 0;
for (const t of tabs) {
  peaks += t.peaks.length;
  const n = t.peaks.filter(p => p.linked !== null && p.linked !== undefined && p.linked !== '').length;
  links += n; if (n) linkedTabs++;
  const why = linkGraphFailure(t.peaks);
  if (why) refused.push({ file: t.file, tab: t.name, reason: why });
}
const summary = { tabs: tabs.length, peaks, linked_tabs: linkedTabs, links, refused: refused.length, refusals: refused };
fs.writeFileSync(path.join(REPO, 'docs/findings/link-graph/census.json'), JSON.stringify(summary, null, 1) + '\n');
console.log(`committed tabs ${tabs.length}, peaks ${peaks}, links ${links} in ${linkedTabs} tabs, refused ${refused.length}`);
