# Find Peaks UI unit 3 (commit 07e685a) — Codex review verdicts (round 1)

## Run A
```

exec
/bin/zsh -lc 'find data/xps -maxdepth 2 -type f | sort' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
data/xps/auger-lines.json
data/xps/elements-actinides.json
data/xps/elements-lanthanides.json
data/xps/elements-machine.json
data/xps/elements-machine.provenance.json
data/xps/elements-machine.skipped.json
data/xps/elements-main.json
data/xps/fit-physics.json
data/xps/legacy/chemical-states.json
data/xps/legacy/corrections.json
data/xps/legacy/schema.json
data/xps/legacy/survey-lines.json
data/xps/schema.json
data/xps/sources.json

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit import coverage; print(sum(len(coverage.element_structure(sym)['levels']) for sym in coverage.PERIODIC_TABLE)); print(len(coverage.PERIODIC_TABLE))\"" in /Users/skyefortier/xps-verify
 succeeded in 212ms:
980
96

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"exec('''import json, re\\nfrom pathlib import Path\\nfrom collections import Counter\\nfrom autofit import coverage\\nfrom autofit.regions import registered_regions\\nroot=Path(\\\"data/xps\\\")\\nkeys=set()\\ndef subshell(orb):\\n    m=re.match(r\\\""'^([1-7][spdf])'"\\\", orb)\\n    return m.group(1) if m else orb\\nfor fname in [\\\"elements-main.json\\\",\\\"elements-lanthanides.json\\\",\\\"elements-actinides.json\\\",\\\"elements-machine.json\\\"]:\\n    doc=json.loads((root/fname).read_text())\\n    els=doc.get(\\\"elements\\\", doc if isinstance(doc,list) else [])\\n    for el in els:\\n        for fam in el.get(\\\"families\\\",[]):\\n            for t in fam.get(\\\"transitions\\\",[]):\\n                keys.add((el[\\\"symbol\\\"], subshell(t[\\\"orbital\\\"])))\\nlegacy=json.loads((root/\\\"legacy/survey-lines.json\\\").read_text())\\nels=legacy.get(\\\"elements\\\", legacy if isinstance(legacy,list) else [])\\nfor el in els:\\n    for ln in el.get(\\\"lines\\\",[]):\\n        keys.add((el[\\\"symbol\\\"], subshell(ln[\\\"orbital\\\"])))\\ncurated=set(registered_regions())\\ncounts=Counter()\\nfor sym in coverage.PERIODIC_TABLE:\\n    st=coverage.element_structure(sym)\\n    for lv in st[\\\"levels\\\"]:\\n        region=f\\\"{sym} {lv[\\\\\\\"level\\\\\\\"]}\\\"\\n        if region in curated: counts[\\\"curated\\\"]+=1\\n        elif (sym, lv[\\\"level\\\"]) in keys: counts[\\\"machine\\\"]+=1\\n        else: counts[\\\"structure_only\\\"]+=1\\nprint(counts, sum(counts.values()))\\nprint((\\\"Fe\\\",\\\"2p\\\") in keys)\\n''')\"" in /Users/skyefortier/xps-verify
 exited 1 in 139ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<string>", line 28
    region=f"{sym} {lv["level"]}"
                        ^
SyntaxError: f-string: unmatched '['

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"exec('''import json, re\\nfrom pathlib import Path\\nfrom collections import Counter\\nfrom autofit import coverage\\nfrom autofit.regions import registered_regions\\nroot=Path(\\\"data/xps\\\")\\nkeys=set()\\ndef subshell(orb):\\n    m=re.match(r\\\""'^([1-7][spdf])'"\\\", orb)\\n    return m.group(1) if m else orb\\nfor fname in [\\\"elements-main.json\\\",\\\"elements-lanthanides.json\\\",\\\"elements-actinides.json\\\",\\\"elements-machine.json\\\"]:\\n    doc=json.loads((root/fname).read_text())\\n    els=doc.get(\\\"elements\\\", doc if isinstance(doc,list) else [])\\n    for el in els:\\n        for fam in el.get(\\\"families\\\",[]):\\n            for t in fam.get(\\\"transitions\\\",[]):\\n                keys.add((el[\\\"symbol\\\"], subshell(t[\\\"orbital\\\"])))\\nlegacy=json.loads((root/\\\"legacy/survey-lines.json\\\").read_text())\\nels=legacy.get(\\\"elements\\\", legacy if isinstance(legacy,list) else [])\\nfor el in els:\\n    for ln in el.get(\\\"lines\\\",[]):\\n        keys.add((el[\\\"symbol\\\"], subshell(ln[\\\"orbital\\\"])))\\ncurated=set(registered_regions())\\ncounts=Counter()\\nfor sym in coverage.PERIODIC_TABLE:\\n    st=coverage.element_structure(sym)\\n    for lv in st[\\\"levels\\\"]:\\n        region=sym+\\\" \\\"+lv[\\\"level\\\"]\\n        if region in curated: counts[\\\"curated\\\"]+=1\\n        elif (sym, lv[\\\"level\\\"]) in keys: counts[\\\"machine\\\"]+=1\\n        else: counts[\\\"structure_only\\\"]+=1\\nprint(counts, sum(counts.values()))\\nprint((\\\"Fe\\\",\\\"2p\\\") in keys)\\n''')\"" in /Users/skyefortier/xps-verify
 succeeded in 297ms:
Counter({'structure_only': 864, 'machine': 111, 'curated': 5}) 980
True

codex
I verified the 980/5/111/864 counts independently from the structural table plus raw `data/xps` JSON, without going through the missing `jsonschema` loader. I’m doing one more narrow cache-copy check by seeding the module cache directly, since the production loader cannot run in this environment.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit import coverage_index as ci; from autofit.regions import registered_regions; ci._INDEX_CACHE_KEY=frozenset(registered_regions()); ci._INDEX_CACHE=[{'region':'X 1s','roi':{'be_min':1},'tier':'machine'}]; a=ci.region_coverage_index(); a[0]['roi']['be_min']=999; b=ci.region_coverage_index(); print(b[0]['roi']['be_min'])\"" in /Users/skyefortier/xps-verify
 succeeded in 247ms:
999

codex
1. **MAJOR** [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13267): filtered multi-select state is not actually preserved when selecting the second region. `_fpRegionsChanged()` rebuilds `_fpRegionsSelected` from only currently rendered `selectedOptions`, and `runFindPeaks()` also submits only current DOM `selectedOptions` at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13418). Scenario: select `C 1s`, filter to `Fe 2p`, select it; `C 1s` is filtered out of the DOM, so the change handler collapses the selection to `["Fe 2p"]`, treats it as a single-region pick, can overwrite ROI, and submits only `Fe 2p`.

2. **MAJOR** [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:117): cached results are only shallow-copied. `roi` is a nested mutable dict, so `region_coverage_index()[i]["roi"]["be_min"] = ...` corrupts `_INDEX_CACHE` for later callers, including `/api/analyze/meta`. The test at [tests/autofit/test_coverage_index.py](/Users/skyefortier/xps-verify/tests/autofit/test_coverage_index.py:121) mutates only a top-level scalar and misses this. I confirmed the shallow-copy corruption with a direct cache-seeded one-liner.

3. **MINOR** [tests/autofit/test_coverage_index.py](/Users/skyefortier/xps-verify/tests/autofit/test_coverage_index.py:98): Fe 2p is documented as the canonical machine-tier example, but the tests allow `Fe 2p` to be either `machine` or `structure_only`; [tests/test_api_analyze_coverage.py](/Users/skyefortier/xps-verify/tests/test_api_analyze_coverage.py:53) does the same. A regression that drops sourced-position coverage for Fe 2p would still pass while contradicting the Unit 3 claim.

4. **MINOR** [tests/test_browser_find_peaks_coverage.py](/Users/skyefortier/xps-verify/tests/test_browser_find_peaks_coverage.py:174): the fallback-note browser assertion is too permissive: `"not cited grammar" in note.lower() or "sourced" in note.lower()`. A bad note like “Sourced position with cited fitting grammar” would pass because it contains `sourced`.

No BLOCKER honesty-rail violation found in the static logic: `curated` is only assigned from `registered_regions()`, the defensive fallback iterates only `curated - seen`, machine notes explicitly say not cited grammar, and `structure_only` paths keep `roi: None`. I could not call `region_coverage_index()` end-to-end with system Python because `jsonschema` is not installed in this read-only environment, but I independently verified the 980 / 5 / 111 / 864 counts from `autofit.coverage` plus raw `data/xps` JSON, and Fe 2p’s source record has `expected_region_ev` 706.5-711.

VERDICT: NO-GO
```

## Run B
```
# Subtest: _fpBuildRegionOptions: tolerates a missing/empty coverage array
ok 12 - _fpBuildRegionOptions: tolerates a missing/empty coverage array
  ---
  duration_ms: 0.206769
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: single curated selection shows its own note
ok 13 - _fpTierNoteFor: single curated selection shows its own note
  ---
  duration_ms: 0.231584
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: single fallback (machine) selection is honestly labeled
ok 14 - _fpTierNoteFor: single fallback (machine) selection is honestly labeled
  ---
  duration_ms: 0.26334
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: structure_only selection says no reference position
ok 15 - _fpTierNoteFor: structure_only selection says no reference position
  ---
  duration_ms: 0.157401
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: no selection is an empty string (never throws)
ok 16 - _fpTierNoteFor: no selection is an empty string (never throws)
  ---
  duration_ms: 0.13688
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: multi-region selection lists each region+tier
ok 17 - _fpTierNoteFor: multi-region selection lists each region+tier
  ---
  duration_ms: 0.200425
  type: 'test'
  ...
1..17
# tests 17
# suites 0
# pass 17
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 214.606356

codex
1. **MAJOR** [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13267): Filtered-out multi-selection is not preserved when adding the second region. `_fpRegionsChanged()` rebuilds `_fpRegionsSelected` from the current DOM `selectedOptions`, which only contains rendered options. Scenario: select `C 1s`, filter to `Fe 2p`, select `Fe 2p`; line 13270 replaces the Set with only `Fe 2p`, losing `C 1s`. `runFindPeaks()` also reads only DOM `selectedOptions` at [templates/index.html](/Users/skyefortier/xps-verify/templates/index.html:13418), so the hidden selected region would not be submitted even if the Set retained it. This contradicts the stated co-fit/filter preservation behavior.

2. **MAJOR** [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:117): Cached results are not true independent copies. The function returns `dict(e)` shallow copies, but `roi` is a nested mutable dict created at lines 72, 89, and 95. A caller can mutate `region_coverage_index()[i]["roi"]["be_min"]`, corrupting the cached original and affecting later `/api/analyze/meta` responses. The test at [tests/autofit/test_coverage_index.py](/Users/skyefortier/xps-verify/tests/autofit/test_coverage_index.py:121) only mutates a scalar top-level field, so it misses this.

3. **MINOR** [tests/test_browser_find_peaks_coverage.py](/Users/skyefortier/xps-verify/tests/test_browser_find_peaks_coverage.py:176): The Fe 2p honesty-note assertion is too permissive: `not cited grammar OR sourced` would pass a note that accidentally says something misleading like “sourced cited grammar”. This is a test gap, not a current product honesty violation; the shipped backend note says “NOT a cited fitting grammar” at [autofit/coverage_index.py](/Users/skyefortier/xps-verify/autofit/coverage_index.py:142).

4. **MINOR** [tests/autofit/test_coverage_index.py](/Users/skyefortier/xps-verify/tests/autofit/test_coverage_index.py:98): The Fe 2p unit test allows `tier in ("machine", "structure_only")`, so it would not catch the documented Fe 2p regression from sourced ROI to no sourced ROI. I independently counted the committed data path and confirmed the docs’ numbers are plausible: 980 total, 5 curated, 111 source-position-backed, 864 structure-only; Fe 2p is backed by `elements-machine.json` with `expected_region_ev` 706.5-711 eV.

No BLOCKER honesty-rail violation found: `curated` is only assigned from `registered_regions()` in the main loop, and the defensive completeness loop only iterates `curated - seen`. `machine` notes do not claim cited fitting grammar, and structure-only entries get `roi: None`.

I ran `node --test tests/js/find_peaks_coverage.test.js` successfully. Full pytest was not runnable in this sandbox with the system interpreter because `jsonschema` is not installed.

VERDICT: NO-GO
```
