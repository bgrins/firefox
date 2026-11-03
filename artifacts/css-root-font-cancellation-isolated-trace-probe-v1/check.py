import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
derivation = json.loads((HERE / 'DERIVATION.json').read_bytes())
source = ROOT / derivation['source']
assert sha(source) == derivation['source_sha256']
original = source.read_text()
pattern = r'^  const cases = (.*);$'
match = re.search(pattern, original, re.M)
original_cases = json.loads(match.group(1))
roster = json.loads((HERE / 'ROSTER.json').read_bytes())
assert len(roster) == 4 and len(original_cases) == 34
for name, record in roster.items():
    body = (HERE / name).read_text()
    selected = re.search(pattern, body, re.M)
    assert json.loads(selected.group(1)) == [record['case']]
    assert original_cases.count(record['case']) == 1
    assert body[:selected.start(1)] == original[:match.start(1)]
    assert body[selected.end(1):] == original[match.end(1):]
    assert sha(HERE / name) == record['sha256']
    assert hashlib.sha256((body[:selected.start(1)] + body[selected.end(1):]).encode()).hexdigest() == derivation['common_body_sha256']
    result = subprocess.run(['node', '-e', 'new (require("vm").Script)("("+require("fs").readFileSync(process.argv[1],"utf8")+")")', str(HERE / name)], capture_output=True)
    assert result.returncode == 0, result.stderr
spec = importlib.util.spec_from_file_location('isolated_assessor', HERE / 'assess.py')
assessor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assessor)
original_report = json.loads((ROOT / 'artifacts/css-root-self-animation-order-original-runtime-v1/REPORT.json').read_bytes())
fixtures = {}
for name, record in roster.items():
    row = next(row for row in original_report['cases'] if all(row[k] == v for k, v in record['case'].items()))
    report = copy.deepcopy(original_report)
    report['cases'] = [row]
    fixtures[name] = report
    result = assessor.assess(name, report)
    assert result['cases'] == 1 and result['controls_valid']
    assert not result['full34_prerequisite_verified'] and not result['candidate_acceptance']
rejected = []
name = 'child-no-read.js'
for label, mutate in [
    ('wrong scenario', lambda r: r['cases'][0].update(target='root-pseudo-font')),
    ('extra row', lambda r: r['cases'].append(copy.deepcopy(r['cases'][0]))),
    ('error', lambda r: r['errors'].append({'message': 'failure'})),
    ('cleanup', lambda r: r.update(cleanup=False)),
    ('missing first', lambda r: r['cases'][0]['samples'].pop(0)),
    ('raw mismatch', lambda r: r['cases'][0]['samples'][0].update(raw='1px')),
    ('unobserved barrier', lambda r: r['cases'][0].update(preconditionRead={'fontSize':23, 'lineHeight':37})),
    ('wrong pseudo', lambda r: r['cases'][0]['animation'].update(pseudoElement='::before')),
]:
    report = copy.deepcopy(fixtures[name])
    mutate(report)
    try:
        assessor.assess(name, report)
    except (AssertionError, KeyError):
        rejected.append(label)
    else:
        raise AssertionError(label)
invalid = copy.deepcopy(fixtures[name])
invalid['cases'][0]['disturbance']['value'] = 0
invalid['cases'][0]['controls']['emCalibration'] = False
assert assessor.assess(name, invalid)['controls_valid'] is False
for name, pin in json.loads((HERE / 'REFERENCES.json').read_bytes()).items():
    assert sha(ROOT / name) == pin
print(json.dumps({'exact_cases_only_derivations':4, 'syntax_only_no_js_execution':4,
                  'historical_row_projection_assessor_checks':4, 'rejected':rejected,
                  'invalid_calibration_remains_invalid':True, 'browser_execution':False,
                  'full34_report_fabricated':False,
                  'tested_inputs':{f.name:sha(f) for f in sorted(HERE.iterdir()) if f.suffix in ('.js','.py') or f.name in ('ROSTER.json','DERIVATION.json','REFERENCES.json')}}))
