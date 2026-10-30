import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda data: hashlib.sha256(data).hexdigest()
relative = Path('servo/components/style/properties/cascade.rs')
base = (HERE / 'base' / relative).read_bytes()
candidate = (HERE / 'candidate' / relative).read_bytes()
staged = (HERE / 'STAGED.rs').read_bytes()
assert candidate.count(staged) == 1
assert candidate.replace(staged, b'', 1) == base
delta = ''.join(difflib.unified_diff(base.decode().splitlines(True), candidate.decode().splitlines(True), fromfile='a/' + str(relative), tofile='b/' + str(relative)))
assert delta == (HERE / 'native.patch').read_text()
for path, digest in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert sha((ROOT / path).read_bytes()) == digest
for record in json.loads((HERE / 'SOURCE-EXCERPTS.json').read_bytes()).values():
    path = HERE / record['source'] if record['source'].startswith('base/') else ROOT / record['source']
    body = path.read_bytes()
    assert sha(body) == record['sha256'] and record['text'] in body.decode()
toolchain = json.loads((HERE / 'TOOLCHAIN.json').read_bytes())
assert sha(Path(toolchain['rustfmt']).read_bytes()) == toolchain['rustfmt_sha256']
config = ROOT / toolchain['config']
assert sha(config.read_bytes()) == toolchain['config_sha256']
with tempfile.TemporaryDirectory(prefix='font-metric-stage-patch-') as directory:
    scratch = Path(directory)
    file = scratch / relative
    file.parent.mkdir(parents=True)
    file.write_bytes(base)
    for reverse, expected in [(False, candidate), (True, base)]:
        command = ['patch', '--batch', '--fuzz=0', '-p1', '-i', str(HERE / 'native.patch')]
        if reverse:
            command.append('-R')
        result = subprocess.run(command, cwd=scratch, capture_output=True, text=True)
        assert result.returncode == 0 and file.read_bytes() == expected, result.stdout + result.stderr
    file.write_bytes(candidate)
    result = subprocess.run([toolchain['rustfmt'], '--check', '--config-path', str(config), str(file)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
assert not scratch.exists()
report = json.loads((HERE / 'TEST-RESULT.json').read_bytes())
assert report['staged_sha256'] == sha(staged)
assert report['support_sha256'] == sha((HERE / 'TestSupport.rs').read_bytes())
assert all(row['compile_exit'] == 0 for row in report['records'].values())
assert report['records']['positive']['run_exit'] == 0
assert all(row['run_exit'] == 101 for name, row in report['records'].items() if name != 'positive')
assert not Path(report['scratch']).exists()
print(json.dumps({'exact_addition_only': True, 'native_call_sites_added': 0, 'patch_forward_reverse': True, 'format': True, 'positive_tests': 4, 'compiled_false_controls': 6, 'scratch_absent': True}))
