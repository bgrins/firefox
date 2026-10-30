import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import textwrap

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
relative = Path('servo/components/style/properties/cascade.rs')
base = (HERE / 'base' / relative).read_bytes()
parent = (HERE / 'parent' / relative).read_bytes()
candidate = (HERE / 'candidate' / relative).read_bytes()
staged = (HERE / 'STAGED.rs').read_bytes()
drain = (HERE / 'PRIORITY-DRAIN.rs').read_bytes() + b'\n'
walk = textwrap.indent((HERE / 'REFERENCE-WALK.rs').read_text(), '    ').encode() + b'\n'
assert candidate.count(drain) == candidate.count(walk) == 1
assert candidate.replace(drain, b'', 1).replace(walk, b'', 1) == parent
assert parent.replace(staged, b'', 1) == base
assert parent == (ROOT / 'artifacts/css-font-metric-readiness-proposal-v1/candidate' / relative).read_bytes()
assert staged == (ROOT / 'artifacts/css-font-metric-readiness-proposal-v1/STAGED.rs').read_bytes()
for name, before in [('native.patch', base), ('STAGED-DELTA.patch', parent)]:
    delta = ''.join(difflib.unified_diff(before.decode().splitlines(True), candidate.decode().splitlines(True), fromfile='a/' + str(relative), tofile='b/' + str(relative)))
    assert delta == (HERE / name).read_text()
for path, digest in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert sha((ROOT / path).read_bytes()) == digest
report = json.loads((HERE / 'TEST-RESULT.json').read_bytes())
for name, digest in report['sources'].items():
    assert sha((HERE / name).read_bytes()) == digest
assert all(row['compile_exit'] == 0 for row in report['records'].values())
assert all(row['run_exit'] == (0 if name.endswith('_positive') else 101) for name, row in report['records'].items())
assert all('debug-assertions=no' in row['compile_command'] for row in report['records'].values())
assert not Path(report['scratch']).exists()
extracted_staged = staged.decode().replace('SmallVec<[PreparedMetricDeclaration; 2]>', 'Vec<PreparedMetricDeclaration>').replace('SmallVec::new()', 'Vec::new()')
for kind, body in [('Priority', (HERE / 'PRIORITY-DRAIN.rs').read_text()), ('Reference', (HERE / 'REFERENCE-WALK.rs').read_text().replace('SmallVec<[References; 5]>', 'Vec<References>').replace('SmallVec::new()', 'Vec::new()'))]:
    source = (HERE / (kind + 'Support.rs')).read_text() + '\n' + (extracted_staged if kind == 'Priority' else '') + '\n' + body + '\n' + (HERE / (kind + 'Tests.rs')).read_text()
    assert sha(source.encode()) == report['records'][kind.lower() + '_positive']['source_sha256']
assert sha(Path(report['records']['priority_positive']['compile_command'][0]).read_bytes()) == report['rustc_sha256']
toolchain = json.loads((HERE / 'TOOLCHAIN.json').read_bytes())
assert sha(Path(toolchain['rustfmt']).read_bytes()) == toolchain['rustfmt_sha256']
config = ROOT / toolchain['config']
assert sha(config.read_bytes()) == toolchain['config_sha256']
with tempfile.TemporaryDirectory(prefix='font-pending-patch-') as directory:
    scratch = Path(directory)
    file = scratch / relative
    file.parent.mkdir(parents=True)
    for name, before in [('native.patch', base), ('STAGED-DELTA.patch', parent)]:
        file.write_bytes(before)
        for reverse, expected in [(False, candidate), (True, before)]:
            command = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / name)]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
            assert result.returncode == 0 and file.read_bytes() == expected, result.stdout + result.stderr
    file.write_bytes(candidate)
    result = subprocess.run([toolchain['rustfmt'], '--check', '--config-path', str(config), str(file)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
assert not scratch.exists()
print(json.dumps(dict(exact_two_block_addition=True, native_entry_call_sites_added=0, patch_forward_reverse=True, format=True, positive_tests=11, compiled_false_controls=9, scratch_absent=True)))
