export const meta = {
  name: 'stage9-phase4-chem-extract',
  description: 'Phase 4 chem-state extraction: Claude workers extract per-compound BEs for the orbital from NIST element-in-compound Internet Archive snapshots. No fabrication: unfetchable -> status record.',
  phases: [{ title: 'ExtractChem', detail: '6 workers over 11 element-orbital groups' }],
}

const REPO = '/Users/skyefortier/xps-app/.claude/worktrees/feature-periodic-table';
const targets = [{"element": "C", "z": 6, "orbital": "1s", "states": [{"field_id": "f0062", "state": "Graphite/C-C", "legacy_be": 284.5, "ref": "Moulder 1992"}, {"field_id": "f0063", "state": "Adventitious C-C/C-H", "legacy_be": 284.8, "ref": "ISO 19318"}, {"field_id": "f0064", "state": "C-O (alcohol/ether)", "legacy_be": 286.3, "ref": "Beamson 1992"}, {"field_id": "f0065", "state": "C=O (carbonyl)", "legacy_be": 287.8, "ref": "Beamson 1992"}, {"field_id": "f0066", "state": "O-C=O (carboxyl)", "legacy_be": 288.8, "ref": "Beamson 1992"}, {"field_id": "f0067", "state": "\u03c0\u2192\u03c0* shake-up", "legacy_be": 290.5, "ref": "Moulder 1992"}, {"field_id": "f0068", "state": "CO\u2083 (carbonate)", "legacy_be": 289.5, "ref": "Moulder 1992"}, {"field_id": "f0069", "state": "CF\u2082 (PTFE)", "legacy_be": 292, "ref": "Beamson 1992"}, {"field_id": "f0070", "state": "CF\u2083", "legacy_be": 293.5, "ref": "Beamson 1992"}]}, {"element": "O", "z": 8, "orbital": "1s", "states": [{"field_id": "f0071", "state": "Metal oxide (M-O)", "legacy_be": 530, "ref": "Moulder 1992"}, {"field_id": "f0072", "state": "Hydroxide (M-OH)", "legacy_be": 531.5, "ref": "Moulder 1992"}, {"field_id": "f0073", "state": "Adsorbed H\u2082O", "legacy_be": 533, "ref": "Moulder 1992"}, {"field_id": "f0074", "state": "SiO\u2082", "legacy_be": 532.9, "ref": "Moulder 1992"}, {"field_id": "f0075", "state": "Organic C-O", "legacy_be": 532.5, "ref": "Beamson 1992"}, {"field_id": "f0076", "state": "Organic C=O", "legacy_be": 531.8, "ref": "Beamson 1992"}]}, {"element": "N", "z": 7, "orbital": "1s", "states": [{"field_id": "f0077", "state": "Metal nitride", "legacy_be": 397, "ref": "Moulder 1992"}, {"field_id": "f0078", "state": "Amine (NH\u2082)", "legacy_be": 399.5, "ref": "Moulder 1992"}, {"field_id": "f0079", "state": "Amide (N-C=O)", "legacy_be": 400, "ref": "Beamson 1992"}, {"field_id": "f0080", "state": "NH\u2084\u207a / protonated amine", "legacy_be": 401.5, "ref": "Moulder 1992"}, {"field_id": "f0081", "state": "NO\u2083 (nitrate)", "legacy_be": 407, "ref": "Moulder 1992"}]}, {"element": "Si", "z": 14, "orbital": "2p", "states": [{"field_id": "f0082", "state": "Si metal", "legacy_be": 99.3, "ref": "Moulder 1992"}, {"field_id": "f0083", "state": "SiO\u2082", "legacy_be": 103.3, "ref": "Moulder 1992"}, {"field_id": "f0084", "state": "Si\u2083N\u2084", "legacy_be": 101.8, "ref": "Moulder 1992"}, {"field_id": "f0085", "state": "SiC", "legacy_be": 100.4, "ref": "Moulder 1992"}]}, {"element": "Fe", "z": 26, "orbital": "2p3/2", "states": [{"field_id": "f0086", "state": "Fe metal", "legacy_be": 707, "ref": "Biesinger 2011"}, {"field_id": "f0087", "state": "FeO (Fe\u00b2\u207a)", "legacy_be": 709.5, "ref": "Biesinger 2011"}, {"field_id": "f0088", "state": "Fe\u2082O\u2083 (Fe\u00b3\u207a)", "legacy_be": 710.7, "ref": "Biesinger 2011"}, {"field_id": "f0089", "state": "FeOOH", "legacy_be": 711.3, "ref": "Biesinger 2011"}, {"field_id": "f0090", "state": "FeSO\u2084", "legacy_be": 712, "ref": "Moulder 1992"}]}, {"element": "Cu", "z": 29, "orbital": "2p3/2", "states": [{"field_id": "f0091", "state": "Cu metal", "legacy_be": 932.6, "ref": "Biesinger 2017"}, {"field_id": "f0092", "state": "Cu\u2082O (Cu\u207a)", "legacy_be": 932.4, "ref": "Biesinger 2017"}, {"field_id": "f0093", "state": "CuO (Cu\u00b2\u207a)", "legacy_be": 933.6, "ref": "Biesinger 2017"}, {"field_id": "f0094", "state": "Cu(OH)\u2082", "legacy_be": 934.5, "ref": "Biesinger 2017"}]}, {"element": "Ti", "z": 22, "orbital": "2p3/2", "states": [{"field_id": "f0095", "state": "Ti metal", "legacy_be": 454, "ref": "Moulder 1992"}, {"field_id": "f0096", "state": "TiO\u2082 (Ti\u2074\u207a)", "legacy_be": 458.8, "ref": "Moulder 1992"}, {"field_id": "f0097", "state": "Ti\u2082O\u2083 (Ti\u00b3\u207a)", "legacy_be": 457.1, "ref": "Moulder 1992"}, {"field_id": "f0098", "state": "TiN", "legacy_be": 455.8, "ref": "Moulder 1992"}]}, {"element": "U", "z": 92, "orbital": "4f7/2", "states": [{"field_id": "f0099", "state": "U metal", "legacy_be": 377.3, "ref": "Moulder 1992"}, {"field_id": "f0100", "state": "UO\u2082 (U\u2074\u207a)", "legacy_be": 380, "ref": "Ilton 2007"}, {"field_id": "f0101", "state": "U\u2083O\u2088 (mixed)", "legacy_be": 380.8, "ref": "Ilton 2007"}, {"field_id": "f0102", "state": "UO\u2083 (U\u2076\u207a)", "legacy_be": 381.5, "ref": "Ilton 2007"}, {"field_id": "f0103", "state": "UCl\u2084", "legacy_be": 380.2, "ref": "Fortier 2026"}]}, {"element": "Cl", "z": 17, "orbital": "2p3/2", "states": [{"field_id": "f0104", "state": "Organic Cl (C-Cl)", "legacy_be": 200.3, "ref": "Moulder 1992"}, {"field_id": "f0105", "state": "Metal chloride", "legacy_be": 198.5, "ref": "Moulder 1992"}, {"field_id": "f0106", "state": "ClO\u2084\u207b (perchlorate)", "legacy_be": 207.5, "ref": "Moulder 1992"}]}, {"element": "Au", "z": 79, "orbital": "4f7/2", "states": [{"field_id": "f0107", "state": "Au metal", "legacy_be": 84, "ref": "Moulder 1992"}, {"field_id": "f0108", "state": "Au\u2082O\u2083 (Au\u00b3\u207a)", "legacy_be": 85.8, "ref": "Moulder 1992"}, {"field_id": "f0109", "state": "AuCl\u2083", "legacy_be": 86.5, "ref": "Moulder 1992"}]}, {"element": "S", "z": 16, "orbital": "2p3/2", "states": [{"field_id": "f0110", "state": "Thiol (S-H)", "legacy_be": 163, "ref": "Moulder 1992"}, {"field_id": "f0111", "state": "Sulfide (S\u00b2\u207b)", "legacy_be": 161.5, "ref": "Moulder 1992"}, {"field_id": "f0112", "state": "Sulfate (SO\u2084\u00b2\u207b)", "legacy_be": 169, "ref": "Moulder 1992"}, {"field_id": "f0113", "state": "Sulfite (SO\u2083\u00b2\u207b)", "legacy_be": 166.5, "ref": "Moulder 1992"}]}];

const N = 6;
const batches = Array.from({ length: N }, () => []);
targets.forEach((t, i) => batches[i % N].push(t));

const SCHEMA = {
  type: 'object', required: ['groups'],
  properties: { groups: { type: 'array', items: {
    type: 'object', required: ['element','orbital','status'],
    properties: {
      element: { type: 'string' }, orbital: { type: 'string' },
      status: { enum: ['extracted','no-snapshot','no-matching-line','fetch-failed'] },
      source_url: { type: 'string' },
      compound_bes: { type: 'array', items: { type: 'object', required: ['compound','be_ev'],
        properties: { compound: { type: 'string' }, be_ev: { type: 'number' } } } },
      evidence: { type: 'string' },
    } } } },
};

function prompt(batch) {
  return `You extract authoritative XPS chemical-state binding energies from NIST SRD 20. FABRICATION FORBIDDEN: report ONLY values present in a page you fetch this run; never recall from memory.

For each element E and orbital ORB below, fetch the NIST "element in compound" results page from the Internet Archive:
1. CDX: curl -s --max-time 60 "http://web.archive.org/cdx/search/cdx?url=srdata.nist.gov/xps/elm_in_comp_res.as*%3Felm1=E&output=text&fl=timestamp,original,statuscode&filter=statuscode:200&limit=40"
2. Fetch a 200 snapshot raw, saving it:
   curl -s --max-time 90 "http://web.archive.org/web/<TS>id_/http://srdata.nist.gov:80/xps/elm_in_comp_res.aspx?elm1=E" -o ${REPO}/.stage9/extract_chem_claude/E_comp.html
   (also try .asp if .aspx 404s)
3. Parse rows (Element | Spectral Line | Formula | Energy (eV)). Keep ONLY rows whose Spectral Line equals the orbital ORB (e.g. 2p3/2, 1s, 4f7/2).

Return one group object per (element, orbital):
- status "extracted": snapshot fetched AND >=1 matching-orbital row found. compound_bes = EVERY {compound: <Formula>, be_ev: <Energy>} row for that orbital literally in the HTML (report ALL; the archived page is often page 1 of several, that is fine). source_url, evidence (a few sample rows).
- "no-snapshot" / "no-matching-line" / "fetch-failed" otherwise (no compound_bes).

ABSOLUTE RULES: every be_ev MUST be a row in the HTML you fetched THIS run. Never invent. A status record is a correct result. Do NOT try to match legacy state labels — just report ALL compound BEs for the orbital; matching happens downstream.

Groups this batch:
${JSON.stringify(batch, null, 1)}

Return a group object for every (element, orbital) in the batch.`;
}

phase('ExtractChem');
const results = await parallel(
  batches.filter(b => b.length).map((batch, i) => () =>
    agent(prompt(batch), { label: `chem:batch${i + 1}`, phase: 'ExtractChem', schema: SCHEMA }))
);
const all = [];
for (const r of results) if (r && Array.isArray(r.groups)) all.push(...r.groups);
const byStatus = {};
for (const g of all) byStatus[g.status] = (byStatus[g.status] || 0) + 1;
log(`chem groups extracted ${all.length}; status ${JSON.stringify(byStatus)}`);
return { groups: all, byStatus };
