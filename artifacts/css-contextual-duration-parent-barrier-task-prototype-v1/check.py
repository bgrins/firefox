import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUSTC = Path('/Users/bgrins/.rustup/toolchains/1.97.1-aarch64-apple-darwin/bin/rustc')
RUSTFMT = RUSTC.with_name('rustfmt')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
roles = json.loads((HERE / 'SOURCE-ROLES.json').read_bytes())
patch = []
for name, row in roles.items():
    base, candidate = HERE / 'base' / name, HERE / 'candidate' / name
    assert sha(base) == sha(ROOT / row['base_capture']) == row['base_sha256']
    assert sha(candidate) == row['candidate_sha256']
    patch.extend(difflib.unified_diff(base.read_text().splitlines(True), candidate.read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
assert ''.join(patch) == (HERE / 'native.patch').read_text()
context = (HERE / 'candidate/servo/components/style/context.rs').read_text()
core = context[context.index('/// The style input selected'):context.index('/// A helper type for stack limit checking.')]
driver = (HERE / 'candidate/servo/components/style/driver.rs').read_text()
tail = driver[driver.index('    let mut tasks = Vec::new();'):]
assert tail.endswith('    (root, tasks)\n}\n')
transfer = 'fn transfer(mut scoped_tls: ScopedTLS, root: usize) -> (usize, Vec<SequentialTask<Element>>) {\n' + tail
harness = (HERE / 'harness-prefix.rs').read_text() + core + (HERE / 'harness-tests.rs').read_text() + transfer
(HERE / 'EXTRACTED-HARNESS.rs').write_text(harness)
results = {}
with tempfile.TemporaryDirectory(prefix='css-parent-task-prototype-', dir='/private/tmp') as directory:
    temporary = Path(directory)
    scratch = temporary / 'patch'
    shutil.copytree(HERE / 'base', scratch)
    for reverse in [False, True]:
        command = ['/usr/bin/patch', '--fuzz=0', '-p1', '-i', str(HERE / 'native.patch')]
        if reverse: command.append('-R')
        result = subprocess.run(command, cwd=scratch, text=True, capture_output=True)
        assert result.returncode == 0 and 'offset' not in result.stdout.lower(), result
        for name, row in roles.items():
            assert sha(scratch / name) == row['base_sha256' if reverse else 'candidate_sha256']
    for name in roles:
        result = subprocess.run([str(RUSTFMT), '--edition', '2024', '--config', 'skip_children=true', '--emit', 'stdout', str(HERE / 'candidate' / name)], capture_output=True, text=True)
        assert result.returncode == 0, (name, result.stderr)
    variants = {
        'positive': harness,
        'false-prepared-reads-published': harness.replace('el.update_animations_with_style(before_change_style, style, tasks);', 'el.update_animations(before_change_style, tasks);'),
        'false-tasks-before-context-drop': harness.replace('    drop(scoped_tls);\n    (root, tasks)', '    for task in tasks { task.execute(); }\n    drop(scoped_tls);\n    let tasks = Vec::new();\n    (root, tasks)'),
    }
    for name, body in variants.items():
        assert name == 'positive' or body != harness
        source = temporary / (name + '.rs')
        executable = temporary / name
        source.write_text(body)
        compiled = subprocess.run([str(RUSTC), '--edition=2024', '--cfg', 'feature="gecko"', '--test', str(source), '-o', str(executable)], capture_output=True, text=True)
        assert compiled.returncode == 0, compiled.stderr
        tested = subprocess.run([str(executable), '--test-threads=1'], capture_output=True, text=True)
        (HERE / (name + '.log')).write_text(tested.stdout + tested.stderr)
        if name == 'positive':
            assert tested.returncode == 0 and '6 passed; 0 failed' in tested.stdout, tested
        else:
            assert tested.returncode != 0 and 'FAILED' in tested.stdout, tested
        results[name] = {'exit': tested.returncode, 'log_sha256': sha(HERE / (name + '.log'))}
assert not temporary.exists()
receipt = {'exact_patch_forward_reverse': True, 'whole_candidate_files_parsed_by_rustfmt': 4,
           'extracted_native_generic_methods_checked_against_mock_interfaces': True,
           'native_full_crate_compilation': False, 'runtime_fix_or_completion_claim': False,
           'tests': results, 'scratch_removed': True,
           'rustc': {'path': str(RUSTC), 'sha256': sha(RUSTC), 'version': subprocess.check_output([str(RUSTC), '--version'], text=True).strip()},
           'rustfmt': {'path': str(RUSTFMT), 'sha256': sha(RUSTFMT)}}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
