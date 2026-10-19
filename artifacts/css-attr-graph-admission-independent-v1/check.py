import argparse
import collections
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parent
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if digest(root / 'MANIFEST.json') != args.manifest_sha:
    raise SystemExit('Manifest authentication failed')
manifest = json.loads((root / 'MANIFEST.json').read_text())
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
if actual != set(manifest['files']) | {'MANIFEST.json', 'FREEZE.json'}:
    raise SystemExit('Inventory mismatch')
for name, expected in manifest['files'].items():
    p = root / name
    if p.is_symlink() or not p.resolve().is_relative_to(root):
        raise SystemExit('Unsafe path')
    if digest(p) != expected:
        raise SystemExit('Input authentication failed: ' + name)
assert json.loads((root / 'FREEZE.json').read_text())['manifest_sha256'] == args.manifest_sha
audit = root / 'audit'
seal = json.loads((audit / 'FREEZE.json').read_text())
assert digest(audit / 'INPUTS.json') == seal['inputs_sha256']
for name, expected in json.loads((audit / 'INPUTS.json').read_text()).items():
    assert digest(audit / name) == expected

original = (root / 'proposal/original-cascade.rs').read_text()
candidate = (root / 'proposal/candidate-cascade.rs').read_text()
removed = '            if !refs.flags.intersects(ReferenceFlags::VAR) {\n                return;\n            }\n'
assert original.count(removed) == 1 and original.replace(removed, '', 1) == candidate
assert original == (root / 'root-evidence/native-original.rs').read_text()
assert candidate == (root / 'root-evidence/native-candidate.rs').read_text()
assert original == (audit / 'sources/candidate/properties__cascade.rs').read_text()
expected_patch = ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
    fromfile='a/servo/components/style/properties/cascade.rs',
    tofile='b/servo/components/style/properties/cascade.rs'))
assert expected_patch == (root / 'proposal/noncustom-collection.patch').read_text()

patch = (root / 'root-evidence/native-wpt-v1.patch').read_text()
assert digest(root / 'root-evidence/native-wpt-v1.patch') == '00393f6fca5f814524a28f2e8b659c8c5b3cd85236cf3c4146291919e1519441'
assert patch.count('diff --git ') == 2
native, test = patch.split('diff --git ')[1:]
assert [line[1:] for line in native.splitlines() if line.startswith('-') and not line.startswith('---')] == removed.splitlines()
assert not [line for line in native.splitlines() if line.startswith('+') and not line.startswith('+++')]
test_text = ''.join(line[1:] for line in test.splitlines(True) if line.startswith('+') and not line.startswith('+++'))
assert test_text == (root / 'proposal/attr-noncustom-dependency-cycles.html').read_text()
cases = json.loads(re.search(r'const cases = (.*?);\n', test_text, re.S)[1])
assert cases == json.loads((root / 'root-evidence/noncustom-cases-v1.json').read_text())
assert len(cases) == 10

anchors = {'properties.html': ['dependency-cycles', 'calculation-of-computed-values'],
           'values5.html': ['attr-substitution', 'substitution-context', 'property-replacement']}
for filename, ids in anchors.items():
    text = (audit / 'spec' / filename).read_text()
    for anchor in ids:
        assert 'id="' + anchor + '"' in text

def statuses(prefix):
    rows = {}
    counts = collections.defaultdict(collections.Counter)
    ends = 0
    for line in (root / f'root-evidence/{prefix}.jsonl').read_text().splitlines():
        r = json.loads(line)
        ends += r['action'] == 'suite_end'
        if r['action'] in ['test_status', 'test_end']:
            key = (r['action'], r['test'], r.get('subtest'))
            assert key not in rows
            rows[key] = r['status']
            counts[r['test']][r['status']] += 1
    assert ends == 1
    receipt = json.loads((root / f'root-evidence/{prefix}-receipt.json').read_text())
    assert receipt['pins_before'] == receipt['pins_after'] and receipt['all_inputs_unchanged']
    return rows, counts

base, bc = statuses('noncustom-baseline-v1')
new, nc = statuses('noncustom-candidate-v1')
assert base.keys() == new.keys() and len(base) == 217
changed = [key for key in base if base[key] != new[key]]
assert len(changed) == 4
assert all(base[key] == 'FAIL' and new[key] == 'PASS' for key in changed)
target = '/css/css-values/attr-noncustom-dependency-cycles.html'
assert dict(bc[target]) == {'FAIL': 3, 'PASS': 7, 'OK': 1}
assert dict(nc[target]) == {'PASS': 10, 'OK': 1}
diagnostic = '/css/css-values/attr-registered-relative-dependencies.html'
assert dict(bc[diagnostic]) == {'FAIL': 4, 'PASS': 9, 'OK': 1}
assert dict(nc[diagnostic]) == {'FAIL': 3, 'PASS': 10, 'OK': 1}

node = json.loads((root / 'NODE.json').read_text())
assert digest(Path(node['path'])) == node['sha256']
scripts = re.findall(r'<script>(.*?)</script>', test_text, re.S)
assert len(scripts) == 1
with tempfile.TemporaryDirectory(prefix='attr-admission-review-') as directory:
    script = Path(directory) / 'test.js'
    script.write_text(scripts[0])
    subprocess.run([node['path'], '--check', str(script)], check=True, capture_output=True)
print(json.dumps({'status': 'PASS', 'files': len(manifest['files']), 'paired_rows': 217,
                  'improvements': 4, 'unchanged': 213, 'metadata_failures_retained': 3,
                  'native_execution': False, 'browser_execution': False, 'formal_proof': False}))
