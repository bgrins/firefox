import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import textwrap

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda data: hashlib.sha256(data).hexdigest()
relative = Path('servo/components/style/properties/cascade.rs')
for name, digest in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert sha((ROOT / name).read_bytes()) == digest
parent = (HERE / 'parent' / relative).read_bytes()
base = (HERE / 'base' / relative).read_bytes()
candidate = (HERE / 'candidate' / relative).read_bytes()
assert parent == (ROOT / 'artifacts/css-font-metric-pending-integration-v1/candidate' / relative).read_bytes()
assert base == (ROOT / 'artifacts/css-font-metric-pending-integration-v1/base' / relative).read_bytes()
assert textwrap.indent((HERE / 'PUBLICATION.rs').read_text(), '    ') in candidate.decode()
namespace = {'__file__': str(HERE / 'test.py')}
script = (HERE / 'test.py').read_text().split("cases={'positive':source}")[0]
exec(compile(script, str(HERE / 'test.py'), 'exec'), namespace)
report = json.loads((HERE / 'TEST-RESULT.json').read_bytes())
assert report['candidate_sha256'] == sha(candidate)
assert report['records']['positive']['source_sha256'] == sha(namespace['source'].encode())
assert report['blocks_sha256'] == {key: sha(value.encode()) for key, value in namespace['blocks'].items()}
assert all(row['compile_exit'] == 0 and row['run_exit'] == (0 if name == 'positive' else 101) for name, row in report['records'].items())
assert all('debug-assertions=no' in row['compile_command'] for row in report['records'].values())
assert sha(Path(report['records']['positive']['compile_command'][0]).read_bytes()) == report['rustc_sha256']
assert not Path(report['scratch']).exists()
assert not Path(json.loads((HERE / 'TEST-COMPILE-INITIAL.json').read_bytes())['scratch']).exists()
tools = json.loads((HERE / 'TOOLCHAIN.json').read_bytes())
assert sha(Path(tools['rustfmt']).read_bytes()) == tools['rustfmt_sha256']
config = ROOT / tools['config']
assert sha(config.read_bytes()) == tools['config_sha256']
with tempfile.TemporaryDirectory(prefix='semantic-publication-patch-') as directory:
    scratch = Path(directory)
    file = scratch / relative
    file.parent.mkdir(parents=True)
    for name, before in [('PARENT-DELTA.patch', parent), ('native.patch', base)]:
        expected = ''.join(difflib.unified_diff(before.decode().splitlines(True), candidate.decode().splitlines(True), fromfile='a/' + str(relative), tofile='b/' + str(relative)))
        assert expected == (HERE / name).read_text()
        file.write_bytes(before)
        for reverse, target in [(False, candidate), (True, before)]:
            command = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / name)]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
            assert result.returncode == 0 and file.read_bytes() == target, result.stdout + result.stderr
    file.write_bytes(candidate)
    result = subprocess.run([tools['rustfmt'], '--check', '--config-path', str(config), str(file)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
assert not scratch.exists()
print(json.dumps({'source_and_extraction_authenticated': True, 'patch_roundtrips': 2, 'format': True, 'extracted_tests': 5, 'compiled_false_controls': 6, 'scratch_absent': True, 'native_typecheck': False, 'enabled_suspension': False}))
