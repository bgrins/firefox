import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
out = Path(args.output)
assert out.is_absolute() and not out.exists()
out.mkdir()
native = 'servo/components/style/values/specified/easing.rs'
fixture = 'testing/web-platform/tests/css/css-easing/cubic-bezier-calculated-x-range.html'
for name, side in [('PREIMAGES', 'original'), ('POSTIMAGES', 'candidate')]:
    for path, entry in json.loads((HERE / (name + '.json')).read_text()).items():
        if entry is not None:
            assert hashlib.sha256((HERE / side / path).read_bytes()).hexdigest() == entry['sha256']
original = (HERE / 'original' / native).read_text()
candidate = (HERE / 'candidate' / native).read_text()
assert original.split('    fn parse_steps(', 1)[1].split('impl TimingFunction {', 1)[0] == candidate.split('    fn parse_steps(', 1)[1].split('impl TimingFunction {', 1)[0]
assert '(x1.resolve(), y1.resolve(), x2.resolve(), y2.resolve())' in candidate
assert 'y1: y1.resolve().unwrap(),' in candidate
assert 'y2: y2.resolve().unwrap(),' in candidate
with tempfile.TemporaryDirectory(prefix='css-bezier-proposal-', dir='/private/tmp') as tmp:
    scratch = Path(tmp)
    for patch, before, after, paths in [
        ('gecko-wpt.patch', 'original', 'candidate', [native, fixture]),
        ('after-steps-native.patch', 'after-steps-original', 'after-steps-candidate', [native]),
    ]:
        tree = scratch / before
        shutil.copytree(HERE / before, tree)
        for reverse in (False, True):
            command = ['patch', '--batch', '-p1', '-i', str(HERE / patch)]
            if reverse:
                command.append('-R')
            result = subprocess.run(command, cwd=tree, capture_output=True, text=True)
            (out / (patch + ('.reverse.log' if reverse else '.apply.log'))).write_text(result.stdout + result.stderr)
            assert result.returncode == 0
            for path in paths:
                expected = HERE / (before if reverse else after) / path
                actual = tree / path
                assert actual.read_bytes() == expected.read_bytes() if expected.exists() else not actual.exists()
    html = (HERE / 'candidate' / fixture).read_text()
    script = re.findall(r'<script>(.*?)</script>', html, re.S)
    assert len(script) == 1
    js = scratch / 'fixture.js'
    js.write_text(script[0])
    result = subprocess.run(['node', '--check', str(js)], capture_output=True, text=True)
    (out / 'syntax.log').write_text(result.stdout + result.stderr)
    assert result.returncode == 0
    registration = scratch / 'registration.js'
    registration.write_text('const names=[]; global.document={getElementById(){return {};}}; global.test=(body,name)=>names.push(name);\n' + script[0] + '\nconsole.log(JSON.stringify(names));\n')
    result = subprocess.run(['node', str(registration)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    names = json.loads(result.stdout)
    assert len(names) == len(set(names)) == 36
    (out / 'NEW-ROSTER.json').write_text(json.dumps(names, indent=2) + '\n')
    for side in ['candidate', 'after-steps-candidate']:
        result = subprocess.run(['rustfmt', '--check', '--edition', '2024', '--config-path', str(ROOT / 'servo/rustfmt.toml'), str(HERE / side / native)], capture_output=True, text=True)
        (out / (side + '-rustfmt.log')).write_text(result.stdout + result.stderr)
        assert result.returncode == 0
result = {'status': 'CUBIC_BEZIER_CALC_RANGE_PROPOSAL_STATIC_PASS', 'new_cases': len(names), 'transport_variants': 2, 'steps_body_unchanged': True, 'scratch_removed': not scratch.exists(), 'native_compiled': False, 'browser_executed': False, 'acceptance': None}
(out / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
