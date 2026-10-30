import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
RUSTC = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
sha = lambda body: hashlib.sha256(body).hexdigest()
staged = (HERE / 'STAGED.rs').read_text()
candidate = (HERE / 'candidate/servo/components/style/properties/cascade.rs').read_text()
assert staged in candidate
extracted = staged.replace('SmallVec<[PreparedMetricDeclaration; 2]>', 'Vec<PreparedMetricDeclaration>').replace('SmallVec::new()', 'Vec::new()')
support = (HERE / 'TestSupport.rs').read_text()
mutations = {
    'ignore_local_rollback': ('|| state.revert.is_some_and', '|| false && state.revert.is_some_and'),
    'missing_prerequisite_guard': ('if !completed.contains_all(prerequisites)', 'if false'),
    'accept_wrong_reference': ('if !std::ptr::eq(value.as_ref(), resolved.as_ref())', 'if false'),
    'drop_prepared_rollback_on_wait': ('return MetricPreparationStep::References(longhand, value.clone());', 'state.prepared.clear(); return MetricPreparationStep::References(longhand, value.clone());'),
    'eager_substitution': ('let Some(resolved) = resolved_reference.take() else {', 'let Some(resolved) = resolved_reference.take().or_else(|| Some(value.clone())) else {'),
}
publish_start = extracted.index("    fn publish_prepared_metric")
guard_start = extracted.index("        if self.ensured_prioritary", publish_start)
guard_end = extracted.index("            return Err(state);", guard_start)
mutations['publish_without_validation'] = (extracted[guard_start:guard_end], '        if false {\n')
records = {}
with tempfile.TemporaryDirectory(prefix='font-metric-staged-') as directory:
    scratch = Path(directory)
    for name in ['positive', *mutations]:
        body = extracted
        if name != 'positive':
            old, new = mutations[name]
            assert body.count(old) == 1
            body = body.replace(old, new)
        source = scratch / (name + '.rs')
        binary = scratch / name
        source.write_text(support + '\n' + body)
        command = [str(RUSTC), '--edition=2021', '--test', str(source), '-o', str(binary)]
        compile_result = subprocess.run(command, capture_output=True, text=True)
        row = records[name] = {'source_sha256': sha(source.read_bytes()), 'compile_command': command, 'compile_exit': compile_result.returncode, 'compile_stdout': compile_result.stdout, 'compile_stderr': compile_result.stderr}
        if compile_result.returncode == 0:
            result = subprocess.run([str(binary)], capture_output=True, text=True)
            row.update(run_exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    report = {'staged_sha256': sha(staged.encode()), 'support_sha256': sha(support.encode()), 'rustc_sha256': sha(RUSTC.read_bytes()), 'records': records, 'scratch': str(scratch)}
report['scratch_absent'] = not scratch.exists()
(HERE / 'TEST-RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
assert all(row['compile_exit'] == 0 for row in records.values())
assert records['positive']['run_exit'] == 0
assert all(row['run_exit'] == 101 for name, row in records.items() if name != 'positive')
print(json.dumps({'positive_tests': 4, 'compiled_semantic_negative_controls': 6, 'scratch_absent': report['scratch_absent']}))
