// node --test reporter for the CI guard (scripts/ci_check_node_events.py): one JSON
// object per line for every test / suite result and for the run's summary,
// between a "start" line and an "end" line. The end line is written only once
// node's event stream has finished, so a run that stopped early has none. The
// guard reads these STRUCTURED events — skip, todo, suite / test and failure are
// node's own fields — never the TAP text, where a test name can carry an escaped
// "# SKIP" or "# TODO" (Codex archive round 4).
export default async function* ciEvents(source) {
  yield JSON.stringify({ type: 'start' }) + '\n';
  for await (const e of source) {
    const d = e.data || {};
    if (e.type === 'test:pass' || e.type === 'test:fail') {
      yield JSON.stringify({
        type: e.type, name: d.name, nesting: d.nesting, file: d.file,
        kind: d.details && d.details.type, skip: d.skip || false, todo: d.todo || false,
        failureType: (d.details && d.details.error && d.details.error.failureType) || null,
      }) + '\n';
    } else if (e.type === 'test:summary' && d.file === undefined) {
      yield JSON.stringify({ type: 'summary', counts: d.counts, success: d.success }) + '\n';
    }
  }
  yield JSON.stringify({ type: 'end' }) + '\n';
}
