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
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def function(text, name):
    start = text.index('    fn ' + name + '(')
    opened = text.index('{', start)
    depth = 1
    end = opened + 1
    while depth:
        if text[end] == '{': depth += 1
        if text[end] == '}': depth -= 1
        end += 1
    return text[start:end], text[opened + 1:end - 1]

roles = json.loads((HERE / 'SOURCE-ROLES.json').read_bytes())
patch = []
for name, row in roles.items():
    base, candidate = HERE / 'base' / name, HERE / 'candidate' / name
    assert sha(base) == sha(ROOT / row['base_capture']) == row['base_sha256']
    assert sha(candidate) == row['candidate_sha256']
    patch.extend(difflib.unified_diff(base.read_text().splitlines(True), candidate.read_text().splitlines(True), fromfile='a/' + name, tofile='b/' + name))
assert ''.join(patch) == (HERE / 'native.patch').read_text()
old = (HERE / 'base/servo/components/style/matching.rs').read_text()
new = (HERE / 'candidate/servo/components/style/matching.rs').read_text()
old_finish = function(old, 'finish_restyle')[1]
new_publish = function(new, 'publish_restyle')[1]
marker = '        // First of all, update the styles.'
assert old_finish[old_finish.index(marker):] == new_publish[new_publish.index(marker):]
legacy = function(new, 'finish_restyle')[1]
assert legacy.count('self.process_animations(') == legacy.count('self.publish_restyle(') == 1
assert legacy.index('self.process_animations(') < legacy.index('self.publish_restyle(')
old_discovery = function(old, 'process_animations')[1]
normalized = old_discovery.replace('context.thread_local.tasks.push(task);', 'return Some(task);').replace('return;', 'return None;')
normalized = normalized.rstrip() + '\n        None\n    '
assert normalized == function(new, 'animation_update_task')[1]
prepare = function(new, 'prepare_restyle')[0]
assert 'set_styles' not in prepare and 'publish_restyle' not in prepare and '.tasks' not in prepare
pending = new[new.index('/// An unpublished restyle;'):new.index('/// Represents the result of comparing')]
harness = (HERE / 'harness.rs').read_text().replace('// PREPARE_METHOD', prepare).replace('// PENDING_IMPLEMENTATION', pending)
(HERE / 'EXTRACTED-HARNESS.rs').write_text(harness)
results = {}
with tempfile.TemporaryDirectory(prefix='css-parent-publication-', dir='/private/tmp') as directory:
    temporary = Path(directory)
    scratch = temporary / 'patch'
    shutil.copytree(HERE / 'base', scratch)
    for reverse in [False, True]:
        command = ['/usr/bin/patch', '--fuzz=0', '-p1', '-i', str(HERE / 'native.patch')]
        if reverse: command.append('-R')
        result = subprocess.run(command, cwd=scratch, text=True, capture_output=True)
        assert result.returncode == 0 and 'offset' not in result.stdout.lower(), result
        for name, row in roles.items(): assert sha(scratch / name) == row['base_sha256' if reverse else 'candidate_sha256']
    for name in roles:
        parsed = subprocess.run([str(RUSTFMT), '--edition', '2024', '--config', 'skip_children=true', '--emit', 'stdout', str(HERE / 'candidate' / name)], text=True, capture_output=True)
        assert parsed.returncode == 0, parsed.stderr
    variants = {
        'positive': harness,
        'false-old-published-rule-inputs': harness.replace('ElementCascadeInputs::new_from_resolved_styles(&self.styles)', 'self.element.published_inputs()'),
        'false-publication-context': harness.replace('if context.shared.traversal_flags != self.publication_flags {', 'if false {'),
        'false-style-identity-guard': harness.replace('Arc::ptr_eq(a, b)', 'a == b'),
    }
    for name, body in variants.items():
        assert name == 'positive' or body != harness
        source = temporary / (name + '.rs'); source.write_text(body)
        executable = temporary / name
        compiled = subprocess.run([str(RUSTC), '--edition=2024', '--cfg', 'feature="gecko"', '--test', str(source), '-o', str(executable)], capture_output=True, text=True)
        assert compiled.returncode == 0, compiled.stderr
        tested = subprocess.run([str(executable), '--test-threads=1'], capture_output=True, text=True)
        (HERE / (name + '.log')).write_text(tested.stdout + tested.stderr)
        if name == 'positive': assert tested.returncode == 0 and '7 passed; 0 failed' in tested.stdout, tested
        else: assert tested.returncode != 0 and 'FAILED' in tested.stdout, tested
        results[name] = {'exit': tested.returncode, 'log_sha256': sha(HERE / (name + '.log'))}
assert not temporary.exists()
receipt = {'exact_patch_forward_reverse': True, 'legacy_publication_body_byte_identical': True,
           'legacy_discovery_exact_return_task_transformation': True,
           'full_candidate_files_parsed': 2, 'tests': results, 'scratch_removed': True,
           'full_stylo_crate_compiled': False, 'driver_barrier_or_native_completion_implemented': False,
           'rustc_sha256': sha(RUSTC), 'rustfmt_sha256': sha(RUSTFMT)}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
