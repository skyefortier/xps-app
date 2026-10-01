// Find Peaks is ARCHIVED (owner, 2026-09-30): hidden, not deleted. It cannot
// be started from the UI; its code, /api/analyze, the autofit engine and all
// its tests stay (they drive it programmatically), so it can be revived by
// restoring its Actions-menu button. A Find Peaks result cached on a tab
// (tab.findPeaks.last, runtime-only) and the provenance record applied peaks
// carry (peak._findPeaks) must never resurface anywhere in the UI.
const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
const noComments = html.replace(/<!--[\s\S]*?-->/g, '');
const lines = html.split('\n');
const blockStart = lines.findIndex(l => l.includes('Find Peaks (beta) — opt-in grammar-driven analysis'));
const blockEnd = lines.findIndex((l, i) => i > blockStart && l.startsWith('</script>'));
const outside = lines.filter((_, i) => i < blockStart - 1 || i > blockEnd).join('\n').replace(/<!--[\s\S]*?-->/g, '');

test('the Find Peaks block is where it is expected (the checks below are about the REST of the page)', () => {
  assert.ok(blockStart > 0 && blockEnd > blockStart, 'Find Peaks block located');
  assert.ok(lines.slice(blockStart, blockEnd).join('\n').includes('function openFindPeaksModal('));
});

test('nothing outside its own block can start Find Peaks', () => {
  assert.ok(!/id="find-peaks-menu-item"/.test(noComments), 'the Actions-menu entry is removed');
  for (const fn of ['openFindPeaksModal', 'runFindPeaks', 'applyFindPeaks', '_fpRenderResults']) {
    assert.ok(!new RegExp('\\b' + fn + '\\s*\\(').test(outside), fn + ' is called from outside the Find Peaks block');
  }
  assert.ok(!/find-peaks-overlay/.test(outside), 'nothing outside the block opens its overlay');
  assert.ok(!/Find Peaks/i.test(outside.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '')), 'no user-visible mention remains');
});

test('the code is kept so it can be revived', () => {
  for (const fn of ['openFindPeaksModal', 'runFindPeaks', 'applyFindPeaks', '_fpPollJob', '_fpRenderResults']) {
    assert.ok(new RegExp('^(async )?function ' + fn + '\\(', 'm').test(html), fn + ' kept');
  }
  assert.match(html, /id="find-peaks-overlay"/);
  assert.match(html, /<!-- Find Peaks is ARCHIVED/);
});

test('a cached Find Peaks result is never saved and nothing outside the block reads one', () => {
  assert.ok(!/\bfindPeaks\b/.test(outside.replace(/active\.findPeaks = null;/, '')),
            'outside the block, a tab\'s findPeaks is only ever cleared');
  assert.ok(!/_findPeaks\b|_findPeaksReview\b/.test(outside), 'no reader of the applied peaks\' provenance record');
});
