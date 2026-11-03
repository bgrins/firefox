import hashlib, json, subprocess, tempfile
from pathlib import Path

H = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()
saved = json.loads((H / 'SOURCE.json').read_text())
native = H.parents[1] / saved['path']
assert sha(native.read_bytes()) == saved['sha256']
parts = saved['parts']
assert all(part in native.read_text() for part in parts.values())
receipt = (H / 'RECEIPT.rs').read_text()
prefix = (H / 'Support.rs').read_text() + '\n' + parts['publication']
prefix += '\nimpl Cascade {\n' + parts['initialization'] + '\n}\n'
prefix += '\nimpl Context {\n' + parts['reset'] + '\n}\n'
tests = (H / 'ADAPTER.rs').read_text() + '\n' + (H / 'Tests.rs').read_text()
def changed(old, new):
    assert receipt.count(old) == 1, old
    return receipt.replace(old, new, 1)
variants = {
    'positive': receipt,
    'ignore_unresolved': changed('if self.unresolved.contains(name)', 'if false'),
    'accept_applying': changed('if !info.publication.can_retire()', 'if false'),
    'reuse_root': changed('self.root = Arc::new(());', 'let _ = &self.root;'),
    'ignore_flags': changed('self.valid &= flags == self.flags;', 'let _ = flags;'),
    'cycle_always_invalid': changed('map.get_var(registration, name).cloned()', 'None'),
    'ignore_name_binding': changed('if info.var.as_ref().is_some_and(|var| !matches!(var, VarType::Custom(n) if n == name))', 'if false'),
}
rustc = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
records = {}
with tempfile.TemporaryDirectory(prefix='custom-initialization-receipt-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    for name, body in variants.items():
        source = prefix + '\n' + body + '\n' + tests
        path = scratch / (name + '.rs'); path.write_text(source)
        binary = scratch / name
        command = [str(rustc), '--edition=2024', '-C', 'debug-assertions=no', '--test', str(path), '-o', str(binary)]
        built = subprocess.run(command, capture_output=True, text=True)
        row = {'source_sha256': sha(source.encode()), 'compile_command': command, 'compile_exit': built.returncode, 'compile_stderr': built.stderr}
        if built.returncode == 0:
            run = subprocess.run([str(binary)], capture_output=True, text=True)
            row.update(run_exit=run.returncode, stdout=run.stdout, stderr=run.stderr)
        records[name] = row
report = {'inputs': {n: sha((H / n).read_bytes()) for n in ['test.py', 'Support.rs', 'Tests.rs', 'RECEIPT.rs', 'ADAPTER.rs', 'SOURCE.json']}, 'native_sha256': saved['sha256'], 'extracted_blocks': {n: sha(parts[n].encode()) for n in ['initialization', 'publication', 'reset']}, 'rustc_sha256': sha(rustc.read_bytes()), 'scratch': str(scratch), 'scratch_removed': not scratch.exists(), 'records': records}
(H / 'TEST-RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
for name, row in records.items():
    assert row['compile_exit'] == 0, (name, row)
    assert (row['run_exit'] == 0) == (name == 'positive'), (name, row)
print(json.dumps({'positive': records['positive']['stdout'], 'compiled_false_controls': len(records) - 1, 'scratch_removed': not scratch.exists()}))
