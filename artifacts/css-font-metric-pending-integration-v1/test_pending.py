import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
RUSTC = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
sha = lambda b: hashlib.sha256(b).hexdigest()
staged = (HERE / 'STAGED.rs').read_text().replace('SmallVec<[PreparedMetricDeclaration; 2]>', 'Vec<PreparedMetricDeclaration>').replace('SmallVec::new()', 'Vec::new()')
priority = (HERE / 'PRIORITY-DRAIN.rs').read_text()
references = (HERE / 'REFERENCE-WALK.rs').read_text().replace('SmallVec<[References; 5]>', 'Vec<References>').replace('SmallVec::new()', 'Vec::new()')
cases = {
    'priority_positive': ('priority', priority),
    'reference_positive': ('reference', references),
}
mutants = {
    'ignore_selected_owner': ('priority', 'self.active.contains(id) || self.claimed.contains(id)', 'self.active.contains(id)'),
    'ignore_generated_pending': ('priority', 'if self.ensure_ordinary(dependency, apply) == ComputationStatus::Pending', 'if false && self.ensure_ordinary(dependency, apply) == ComputationStatus::Pending'),
    'early_completion': ('priority', 'self.active.insert(id);', 'self.active.insert(id); self.complete.insert(id);'),
    'selection_before_prerequisites': ('priority', 'if !completion.complete.contains(dependency)', 'if false && !completion.complete.contains(dependency)'),
    'drop_rollback_on_resume': ('priority', 'let state = &mut self.continuations[index].1;', 'let state = &mut self.continuations[index].1; state.prepared.clear();'),
    'starve_later_requests': ('priority', 'self.cursor = (position + 1) % requested.len();', 'self.cursor = 0;'),
    'pending_as_ready': ('reference', 'if *readiness == ReferenceReadiness::ComputationPending', 'if false && *readiness == ReferenceReadiness::ComputationPending'),
    'fallback_fifo': ('reference', 'self.queued.pop()', '(if self.queued.is_empty() { None } else { Some(self.queued.remove(0)) })'),
    'wrong_reply_accepted': ('reference', 'if self.waiting.as_ref() != Some(target)', 'if false && self.waiting.as_ref() != Some(target)'),
}
for name, (kind, old, new) in mutants.items():
    body = priority if kind == 'priority' else references
    assert body.count(old) == 1, name
    cases[name] = (kind, body.replace(old, new))
records = {}
with tempfile.TemporaryDirectory(prefix='font-pending-extracted-') as directory:
    scratch = Path(directory)
    for name, (kind, body) in cases.items():
        support = (HERE / ('PrioritySupport.rs' if kind == 'priority' else 'ReferenceSupport.rs')).read_text()
        tests = (HERE / ('PriorityTests.rs' if kind == 'priority' else 'ReferenceTests.rs')).read_text()
        source = scratch / (name + '.rs')
        source.write_text(support + '\n' + (staged if kind == 'priority' else '') + '\n' + body + '\n' + tests)
        binary = scratch / name
        command = [str(RUSTC), '--edition=2021', '-C', 'debug-assertions=no', '--test', str(source), '-o', str(binary)]
        compiled = subprocess.run(command, capture_output=True, text=True)
        row = records[name] = dict(source_sha256=sha(source.read_bytes()), compile_command=command, compile_exit=compiled.returncode, compile_stdout=compiled.stdout, compile_stderr=compiled.stderr)
        if compiled.returncode == 0:
            result = subprocess.run([str(binary)], capture_output=True, text=True)
            row.update(run_exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
report = dict(records=records, rustc_sha256=sha(RUSTC.read_bytes()), sources={p.name:sha(p.read_bytes()) for p in HERE.glob('*.rs')}, scratch=str(scratch), scratch_absent=not scratch.exists())
(HERE / 'TEST-RESULT.json').write_text(json.dumps(report, indent=2)+'\n')
assert all(row['compile_exit'] == 0 for row in records.values())
assert all(row['run_exit'] == (0 if name.endswith('_positive') else 101) for name, row in records.items())
print(json.dumps(dict(positive_tests=11, compiled_semantic_negative_controls=9, scratch_absent=report['scratch_absent'])))
