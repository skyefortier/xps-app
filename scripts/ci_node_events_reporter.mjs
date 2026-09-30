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
    } else if (e.type === 'test:summary') {
      // a file's own summary comes only from a file that ran to completion; a file
      // that exited early, was empty or defined no test gets none (node then emits a
      // synthetic pass under the file's name — Codex archive round 5)
      yield JSON.stringify(d.file === undefined
        ? { type: 'summary', counts: d.counts, success: d.success }
        : { type: 'file_summary', file: d.file, counts: d.counts, success: d.success }) + '\n';
    }
  }
  yield JSON.stringify({ type: 'end' }) + '\n';
}
