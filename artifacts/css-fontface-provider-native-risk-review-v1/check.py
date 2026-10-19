import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

P = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--replay', action='store_true')
a = p.parse_args()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path): return json.loads(path.read_text())
f = load(P / 'FREEZE.json')
assert sha(P / 'INPUTS.json') == f['inputs_sha256']
inputs = load(P / 'INPUTS.json')
assert len(inputs) == f['entries']
for rel, expected in inputs.items(): assert sha(P / rel) == expected, rel
for name, pin in [('css-fontface-provider-candidate-v2','b8f0ccd0bf557b5abc7611cd328fdb852be45ca4a4fc4ee6a01fc98d08f3c4e7'),('css-fontface-provider-integration-v2','a5fd5a73cb71da6e176fbc20b1ba5992d847b050795cdbd70dd35910de9b39ac')]:
    q = P / 'dependencies' / name
    assert sha(q / 'FREEZE.json') == pin
    freeze = load(q / 'FREEZE.json')
    assert sha(q / 'INPUTS.json') == freeze['inputs_sha256']
    for rel, expected in load(q / 'INPUTS.json').items(): assert sha(q / rel) == expected
assert load(P / 'SOURCE-REPLAY.json')['exit'] == 0
assert all(x['exit'] != 0 and not x['output_created'] for x in load(P / 'NEGATIVE-CHECKS.json'))
if a.replay:
    integ = P / 'dependencies/css-fontface-provider-integration-v2'
    subprocess.run(['python3', str(integ / 'check.py')], check=True)
    with tempfile.TemporaryDirectory(prefix='fontface-risk-replay-') as tmp:
        for suite in ['matrix','regressions']:
            out = Path(tmp) / (suite + '.json')
            subprocess.run(['python3', str(integ / 'compare.py'), '--baseline', str(P / 'baseline' / suite), '--output', str(out)], check=True, capture_output=True)
            assert load(out) == load(P / ('BASELINE-' + suite + '.json'))
print(json.dumps({'status':'PASS','entries':len(inputs),'source_verdict':'NO_CONCRETE_NEW_BLOCKER_FOUND','runtime_acceptance':False,'negative_integrity_checks':3},indent=2))
