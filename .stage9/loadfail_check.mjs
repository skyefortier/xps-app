// Stage 9 load-failure check. argv[2]=rendered page with null legacy injection.
// Verifies the post-cutover accessor FAILS LOUD (ok=false, returns empty, flags
// unavailable) rather than silently serving empty reference data.
import { readFileSync } from 'node:fs';
const html = readFileSync(process.argv[2], 'utf8');
const okExpr = html.match(/const LEGACY_REFERENCE_OK = ([\s\S]*?);\n/)[1];
const ref = html.match(/const LEGACY_REFERENCE = (.+?);\n/)[1];
const fn = html.match(/(function _accSurveyElements\(\) \{[\s\S]*?\n\})/)[1];
const out = new Function(`
  let _accSurveyCache=null,_refUnavailableNotified=false;
  function _accReferenceUnavailable(){_refUnavailableNotified=true;return true;}
  const LEGACY_REFERENCE=${ref};
  const LEGACY_REFERENCE_OK=${okExpr};
  ${fn}
  const s=_accSurveyElements();
  return {ok:LEGACY_REFERENCE_OK, empty:Object.keys(s).length===0, notified:_refUnavailableNotified};
`)();
console.log(JSON.stringify(out));
