import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
c = load('capture', HERE / 'capture.py')
p = load('parser', HERE / 'classify.py')
inputs = read(HERE / 'INPUTS.json')
assert inputs['ready'] is False and inputs['execution_epoch'] is None
for n, pin in inputs['local_pins'].items():
    assert hashlib.sha256((HERE / n).read_bytes()).hexdigest() == pin
for n, pin in read(HERE / 'REFERENCES.json').items():
    assert hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == pin
rows = read(HERE / 'BASELINE-ROWS.json')
config = read(HERE / 'CONFIG.json')
assert len(rows) == 166 and len(config['tests']) == 13 and len(config['reftests']) == 2
assert sum(map(len, config['expected_subtests'].values())) == 166
for test, names in config['expected_subtests'].items():
    assert [r['subtest'] for r in rows if r['test'] == test] == names
assert not c.compare_rows(rows, rows)
changed = copy.deepcopy(rows)
changed[0]['status'] = 'FAIL'
assert len(c.compare_rows(changed, rows)) == 1
assert len(c.compare_rows(rows[:-1], rows)) == 1
try: c.compare_rows(rows + rows[:1], rows)
except RuntimeError: pass
else: raise AssertionError('duplicate accepted')
roster = read(ROOT / 'artifacts/css-keyframe-invalid-registered-endpoint-diagnostic-v1/ROSTER.json')
provider = [r for r in rows if r['test'] == '/' + roster['logical_path']]
observed = p.classify(provider, roster)
assert observed['pass_count'] == 6 and observed['fail_count'] == 4
assert all(r['classification'] == 'CALIBRATED_FINAL_HISTORY_MISMATCH' for r in observed['rows'][:4])
passing = [dict(r, status='PASS', message=None, expected=None, known_intermittent=[]) for r in provider]
assert p.classify(passing, roster)['pass_count'] == 10
assert len(c.compare_rows(passing, provider)) == 4
bad = copy.deepcopy(provider)
bad[0]['message'] = 'initial provider calibration failed'
assert p.classify(bad, roster)['rows'][0]['classification'] == 'CALIBRATION_OR_SETUP_INCONCLUSIVE'
assert (HERE / 'classify.py').read_bytes() == (ROOT / 'artifacts/css-keyframe-invalid-registered-endpoint-rerun-v1/classify.py').read_bytes()
source = (HERE / 'capture.py').read_text()
ast.parse(source)
assert "tests.run(wpt, 'diagnostic', active)" in source
assert "set(untracked) == set(epoch['untracked_native'])" in source
assert "stat.S_ISREG(info.st_mode) and [info.st_dev, info.st_ino] == owned['identity']" in source
assert "sha(path) == owned['sha256']" in source
print(json.dumps(dict(status='ANIMATION_RULE_SAMPLE_CAPTURE_STATIC_PASS', rows=166, files=13,
    crashes=2, historical_provider_classification=[6,4], all_pass_provider_accepted=True,
    browser_invoked=False, live_preservation_invoked=False)))

expected = read(HERE / 'EXPECTED-SOURCES.json')
assert len(expected) == 21 and sum(v is None for v in expected.values()) == 1
assert len(read(HERE / 'EXPECTED-UNTRACKED.json')) == 12
assert set(expected) <= set(read(HERE / 'REQUIRED-ROLES.json'))
node = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'need' and len(n.args) == 2 and isinstance(n.args[1], ast.Constant) and n.args[1].value == 'compiled candidate sources')
expr = compile(ast.Expression(node.args[0]), '<source-admission>', 'eval')
assert eval(expr, {'roles': expected, 'compiled': expected})
missing = dict(expected)
del missing[next(n for n, v in expected.items() if v is None)]
assert not eval(expr, {'roles': missing, 'compiled': expected})
changed = dict(expected)
changed[next(n for n, v in expected.items() if v is not None)] = '0' * 64
assert not eval(expr, {'roles': changed, 'compiled': expected})
print(json.dumps({'prototype_source_entries': 21, 'untracked_paths': 12, 'missing_deletion_rejected': True, 'changed_source_rejected': True}))
