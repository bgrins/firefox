#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


freeze = json.loads((ROOT / 'FREEZE.json').read_text())
assert sha(ROOT / 'MANIFEST.json') == freeze['manifest_sha256']
manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
for name, expected in manifest.items():
    path = ROOT / name
    assert path.resolve().is_relative_to(ROOT.resolve()) and not path.is_symlink(), name
    assert sha(path) == expected, name
assert sha(ROOT / 'input/FREEZE.json') == 'd35b20f6df3f41aebec88ae0cde99dc2d9a849ad030c875b46b058888f710191'
assert sha(ROOT / 'input/INPUTS.json') == '36039fdc92c1931b4fb35c9dc5951ec2a6b363ce3f14662ab207aa1b21c7b9d4'
baseline = json.loads((ROOT / 'baseline/baseline-v1-receipt.json').read_text())
assert baseline['pins_before'] == baseline['pins_after'] and baseline['all_inputs_unchanged']
assert baseline['suite_end_count'] == 1 and len(baseline['pins_before']) == 39
test = '/css/css-properties-values-api/registered-property-unit-token-dependencies.html'
rows = [json.loads(line) for line in (ROOT / 'baseline/baseline-v1.jsonl').read_text().splitlines()]
rows = [row for row in rows if row.get('action') == 'test_status' and row.get('test') == test]
assert len(rows) == 14 and sum(row['status'] == 'FAIL' for row in rows) == 7
prior = json.loads((ROOT / 'input/evidence/CASES.json').read_text())
predicted = {row['name'] for row in prior if row['expected'] != row['predicted_native']}
assert {row['subtest'] for row in rows if row['status'] == 'FAIL'} == predicted
result = subprocess.run([sys.executable, str(ROOT / 'input/check.py')], text=True, capture_output=True)
assert result.returncode == 0, (result.stdout, result.stderr)
print(json.dumps({'authenticated_review_files': len(manifest), 'static_replay_exit': result.returncode,
                  'static_replay_stdout': result.stdout, 'native_compiled': False,
                  'browser_run': False}, indent=2))
