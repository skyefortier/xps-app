#!/usr/bin/env node
// Seal 1b (V5.4.4, V6.5 step 4): is the PAGE's certified background, computed from a sealed
// request's own inputs, EXACTLY the server's recorded background_y? Runs the page's own
// background section (tests/js/_page_background_source.js: computeBackgroundCore and every helper
// it calls, extracted verbatim) on each record of `seal_1b_measure.py record`. The window is given
// to the page as its form gives it — the two edge energies as text (String(v), the shortest
// round-trip decimal) — and _bgWindowIndices must recover the request's indices exactly (else the
// record is reported as such, not compared). Output: one JSON line per record.
// Usage: node scripts/seal_1b_background_twin.js RECORDS.jsonl > OUT.jsonl
const fs = require('node:fs');
const path = require('node:path');
const readline = require('node:readline');

const src = require(path.join(__dirname, '../tests/js/_page_background_source.js'))();
const B = new Function(src + '\nreturn { computeBackgroundCore, _bgWindowIndices };')();

(async () => {
  const rl = readline.createInterface({ input: fs.createReadStream(process.argv[2]) });
  for await (const line of rl) {
    const rec = JSON.parse(line);
    if (rec.status !== 200) continue;
    const be = rec.R.energies, inten = rec.R.counts, bgReq = rec.R.request.background;
    const i0 = bgReq.start_idx, i1 = bgReq.end_idx - 1;           // the request's window is end-exclusive
    const settings = { bgType: bgReq.method, endpointAvg: String(bgReq.endpoint_avg),
                       bgStart: String(be[i0]), bgEnd: String(be[i1]), anchors: [] };
    const w = B._bgWindowIndices(be, settings.bgStart, settings.bgEnd);
    const out = { id: rec.id, tab: rec.tab, method: bgReq.method, n_avg: bgReq.endpoint_avg };
    if (w.i0 !== i0 || w.i1 !== i1) {
      out.window_recovered = false;
    } else {
      const bg = B.computeBackgroundCore(be, inten, settings);
      const server = rec.O.background_y;
      let differ = 0, maxAbs = 0;
      for (let k = 0; k < server.length; k++) {
        if (bg[k] !== server[k]) { differ++; maxAbs = Math.max(maxAbs, Math.abs(bg[k] - server[k])); }
      }
      Object.assign(out, { window_recovered: true, converged: bg.converged === true,
                           identical: differ === 0 && bg.length === server.length, n_differ: differ, max_abs: maxAbs });
    }
    process.stdout.write(JSON.stringify(out) + '\n');
  }
})();
