export const meta = {
  name: 'stage9-phase4a-extract',
  description: 'Phase 4a: Claude workers extract legacy survey-line BEs from authoritative NIST SRD 20 Internet Archive snapshots, with mandatory evidence. No fabrication: unfetchable -> status record.',
  phases: [{ title: 'Extract', detail: '8 parallel workers over 53 elements; NIST archive fetch + parse' }],
}

const REPO = '/Users/skyefortier/xps-app/.claude/worktrees/feature-periodic-table';
const targets = [{"element": "Li", "z": 3, "orbitals": [{"field_id": "f0000", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 55}]}, {"element": "Be", "z": 4, "orbitals": [{"field_id": "f0001", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 112}]}, {"element": "B", "z": 5, "orbitals": [{"field_id": "f0002", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 188}]}, {"element": "C", "z": 6, "orbitals": [{"field_id": "f0003", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 285}]}, {"element": "N", "z": 7, "orbitals": [{"field_id": "f0004", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 399}]}, {"element": "O", "z": 8, "orbitals": [{"field_id": "f0005", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 531}, {"field_id": "f0006", "orbital": "KLL", "transition_type": "auger", "legacy_be": 978}]}, {"element": "F", "z": 9, "orbitals": [{"field_id": "f0007", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 685}]}, {"element": "Na", "z": 11, "orbitals": [{"field_id": "f0008", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 1072}, {"field_id": "f0009", "orbital": "KLL", "transition_type": "auger", "legacy_be": 497}]}, {"element": "Mg", "z": 12, "orbitals": [{"field_id": "f0010", "orbital": "1s", "transition_type": "photoelectron", "legacy_be": 1304}, {"field_id": "f0011", "orbital": "KLL", "transition_type": "auger", "legacy_be": 306}]}, {"element": "Al", "z": 13, "orbitals": [{"field_id": "f0012", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 73}]}, {"element": "Si", "z": 14, "orbitals": [{"field_id": "f0013", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 99}, {"field_id": "f0014", "orbital": "2s", "transition_type": "photoelectron", "legacy_be": 150}]}, {"element": "P", "z": 15, "orbitals": [{"field_id": "f0015", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 133}]}, {"element": "S", "z": 16, "orbitals": [{"field_id": "f0016", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 164}, {"field_id": "f0017", "orbital": "2s", "transition_type": "photoelectron", "legacy_be": 228}]}, {"element": "Cl", "z": 17, "orbitals": [{"field_id": "f0018", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 199}, {"field_id": "f0019", "orbital": "2s", "transition_type": "photoelectron", "legacy_be": 270}]}, {"element": "K", "z": 19, "orbitals": [{"field_id": "f0020", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 293}, {"field_id": "f0021", "orbital": "2s", "transition_type": "photoelectron", "legacy_be": 378}]}, {"element": "Ca", "z": 20, "orbitals": [{"field_id": "f0022", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 347}]}, {"element": "Ti", "z": 22, "orbitals": [{"field_id": "f0023", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 459}]}, {"element": "V", "z": 23, "orbitals": [{"field_id": "f0024", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 517}]}, {"element": "Cr", "z": 24, "orbitals": [{"field_id": "f0025", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 577}]}, {"element": "Mn", "z": 25, "orbitals": [{"field_id": "f0026", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 641}]}, {"element": "Fe", "z": 26, "orbitals": [{"field_id": "f0027", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 711}]}, {"element": "Co", "z": 27, "orbitals": [{"field_id": "f0028", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 778}]}, {"element": "Ni", "z": 28, "orbitals": [{"field_id": "f0029", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 853}]}, {"element": "Cu", "z": 29, "orbitals": [{"field_id": "f0030", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 933}]}, {"element": "Zn", "z": 30, "orbitals": [{"field_id": "f0031", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 1022}]}, {"element": "Ga", "z": 31, "orbitals": [{"field_id": "f0032", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 1117}]}, {"element": "Ge", "z": 32, "orbitals": [{"field_id": "f0033", "orbital": "2p", "transition_type": "photoelectron", "legacy_be": 1217}]}, {"element": "As", "z": 33, "orbitals": [{"field_id": "f0034", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 42}]}, {"element": "Se", "z": 34, "orbitals": [{"field_id": "f0035", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 56}]}, {"element": "Br", "z": 35, "orbitals": [{"field_id": "f0036", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 69}]}, {"element": "Sr", "z": 38, "orbitals": [{"field_id": "f0037", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 134}]}, {"element": "Y", "z": 39, "orbitals": [{"field_id": "f0038", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 157}]}, {"element": "Zr", "z": 40, "orbitals": [{"field_id": "f0039", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 179}]}, {"element": "Nb", "z": 41, "orbitals": [{"field_id": "f0040", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 202}]}, {"element": "Mo", "z": 42, "orbitals": [{"field_id": "f0041", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 228}]}, {"element": "Ag", "z": 47, "orbitals": [{"field_id": "f0042", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 368}]}, {"element": "Cd", "z": 48, "orbitals": [{"field_id": "f0043", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 405}]}, {"element": "In", "z": 49, "orbitals": [{"field_id": "f0044", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 444}]}, {"element": "Sn", "z": 50, "orbitals": [{"field_id": "f0045", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 485}]}, {"element": "Sb", "z": 51, "orbitals": [{"field_id": "f0046", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 528}]}, {"element": "Te", "z": 52, "orbitals": [{"field_id": "f0047", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 573}]}, {"element": "I", "z": 53, "orbitals": [{"field_id": "f0048", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 619}]}, {"element": "Ba", "z": 56, "orbitals": [{"field_id": "f0049", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 780}]}, {"element": "La", "z": 57, "orbitals": [{"field_id": "f0050", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 836}]}, {"element": "Ce", "z": 58, "orbitals": [{"field_id": "f0051", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 882}]}, {"element": "Nd", "z": 60, "orbitals": [{"field_id": "f0052", "orbital": "3d", "transition_type": "photoelectron", "legacy_be": 982}]}, {"element": "W", "z": 74, "orbitals": [{"field_id": "f0053", "orbital": "4f", "transition_type": "photoelectron", "legacy_be": 31}]}, {"element": "Pt", "z": 78, "orbitals": [{"field_id": "f0054", "orbital": "4f", "transition_type": "photoelectron", "legacy_be": 71}]}, {"element": "Au", "z": 79, "orbitals": [{"field_id": "f0055", "orbital": "4f", "transition_type": "photoelectron", "legacy_be": 84}]}, {"element": "Pb", "z": 82, "orbitals": [{"field_id": "f0056", "orbital": "4f", "transition_type": "photoelectron", "legacy_be": 137}]}, {"element": "Bi", "z": 83, "orbitals": [{"field_id": "f0057", "orbital": "4f", "transition_type": "photoelectron", "legacy_be": 157}]}, {"element": "Th", "z": 90, "orbitals": [{"field_id": "f0058", "orbital": "4f", "transition_type": "photoelectron", "legacy_be": 333}]}, {"element": "U", "z": 92, "orbitals": [{"field_id": "f0059", "orbital": "4f", "transition_type": "photoelectron", "legacy_be": 380}, {"field_id": "f0060", "orbital": "4d", "transition_type": "photoelectron", "legacy_be": 736}, {"field_id": "f0061", "orbital": "5d", "transition_type": "photoelectron", "legacy_be": 98}]}];

const N = 8;
const batches = Array.from({ length: N }, () => []);
targets.forEach((t, i) => batches[i % N].push(t));

const SCHEMA = {
  type: 'object', required: ['observations'],
  properties: { observations: { type: 'array', items: {
    type: 'object', required: ['field_id','element','orbital','legacy_be','status'],
    properties: {
      field_id: { type: 'string' }, element: { type: 'string' }, orbital: { type: 'string' },
      legacy_be: { type: 'number' },
      status: { enum: ['extracted','no-snapshot','no-matching-line','fetch-failed'] },
      nist_line: { type: 'string' },
      values: { type: 'array', items: { type: 'object', required: ['be_ev','nist_ref'],
        properties: { be_ev: { type: 'number' }, nist_ref: { type: 'string' } } } },
      source_url: { type: 'string' }, evidence: { type: 'string' }, saved_html: { type: 'string' },
    } } } },
};

function prompt(batch) {
  return `You are extracting authoritative XPS binding-energy values from NIST SRD 20, for a scientific dataset where FABRICATION IS FORBIDDEN. Extract ONLY values you literally retrieve from a page you fetch this run; NEVER recall numbers from memory.

The live NIST site is dead, so use Internet Archive snapshots of its per-element "all data" page. For each element (symbol = E):
1. Find a snapshot via CDX (try .asp and .aspx):
   curl -s --max-time 60 "http://web.archive.org/cdx/search/cdx?url=srdata.nist.gov/xps/query_all_dat_el.as*%3Felm1=E&output=text&fl=timestamp,original,statuscode&filter=statuscode:200&limit=40"
   If empty, try url=srdata.nist.gov/xps/EngElmSrchQuery.aspx*Elm=E similarly.
2. Fetch a 200 snapshot raw (id_ = unmodified original), saving it:
   curl -s --max-time 90 "http://web.archive.org/web/<TS>id_/http://srdata.nist.gov:80/xps/query_all_dat_el.asp?elm1=E" -o ${REPO}/.stage9/extract_claude/E_nist.html
3. Parse the table (Element | Spectral Line | Energy (eV) | Reference) with python3 + regex over <tr>/<td>.

For each requested (element, orbital), map legacy family to the NIST principal line: 2p->2p3/2, 3d->3d5/2, 4f->4f7/2, 4d->4d5/2, 3p->3p3/2, 5d->5d5/2; s-lines and Auger (KLL) stay as written. Read EVERY matching row's energy + Reference code.

Per requested orbital, return one observation:
- status "extracted": snapshot fetched AND line found. values[] = EACH {be_ev, nist_ref} literally in the HTML (report ALL rows, do not average/pick); nist_line; source_url (exact archive URL fetched); evidence (matched row text); saved_html (path saved).
- "no-snapshot": no 200 snapshot exists. "no-matching-line": fetched but line absent. "fetch-failed": curl/archive errored after retries. (No values for these.)

ABSOLUTE RULES: every be_ev MUST be a row in the HTML you fetched THIS run. If unsure, use a non-"extracted" status. A status record is a correct, valuable result. Never invent.

Batch:
${JSON.stringify(batch, null, 1)}

Return observations for every (element, orbital) in the batch.`;
}

phase('Extract');
const results = await parallel(
  batches.filter(b => b.length).map((batch, i) => () =>
    agent(prompt(batch), { label: `extract:batch${i + 1}`, phase: 'Extract', schema: SCHEMA }))
);
const all = [];
for (const r of results) if (r && Array.isArray(r.observations)) all.push(...r.observations);
const byStatus = {};
for (const o of all) byStatus[o.status] = (byStatus[o.status] || 0) + 1;
log(`extracted ${all.length} observations; status ${JSON.stringify(byStatus)}`);
return { observations: all, byStatus, count: all.length };
