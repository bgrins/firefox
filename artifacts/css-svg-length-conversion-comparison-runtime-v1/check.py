import ast
import copy
import hashlib
import importlib.util
import json
import stat
import sys
from pathlib import Path

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
def authenticate(mapping, root):
    for name, digest in mapping.items():
        assert stat.S_ISREG((root / name).lstat().st_mode) and sha(root / name) == digest, name
c = read(HERE / 'CONFIG.json')
assert c['ready_for_execution'] is False
authenticate(read(HERE / 'REFERENCES.json'), ROOT)
epoch = ROOT / c['epoch']
authenticate(read(epoch / 'FILES.json'), epoch)
expected, pins, config, owned = load('svg_epoch_check', HERE / 'epoch_gate.py').bind(ROOT, epoch, read, sha, authenticate, load)
assert len(expected['sources']) == 50 and len(pins) == 356 and len(owned) == 3
proposal = ROOT / c['proposal']
sp = read(proposal / 'SOURCE-PINS.json')
assert c['source_pins'] == {**expected['sources'], **{n:v['before_sha256'] for n,v in sp.items()}}
assert len(c['guard_sources']) == 52 and len(c['sources']) == 29
assert c['modified_native_paths'] == config['modified_native_paths'] and len(c['modified_native_paths']) == 27
assert set(c['sources']) == set(c['modified_native_paths']) | set(c['candidate_sources'])
assert c['existing_test_pins'] == {n: r['sha256'] for n, r in owned.items()}
assert len(c['tests']) == 4 and sum(map(len, c['expected_subtests'].values())) == 27
assert c['tests'] == c['baseline_tests'] and c['expected_subtests'] == c['baseline_expected_subtests']
proposal = ROOT / c['proposal']
authenticate(read(proposal / 'FILES.json'), proposal)
main = next(iter(c['install']))
assert (HERE / 'fixture.html').read_bytes() == (proposal / 'candidate' / main).read_bytes()
assert c['expected_subtests'][c['main_tests'][0]] == read(proposal / 'EXPECTED-TESTS.json')
resources = read(HERE / 'RESOURCES.json')
assert resources[main] is None
meta = 'testing/web-platform/meta/' + main.removeprefix('testing/web-platform/tests/') + '.ini'
assert meta in resources and resources[meta] is None
installed_resources = {**read(epoch / 'RESOURCES.json'), **{n:v['sha256'] for n,v in owned.items()}}
assert all(resources[n] == h for n,h in installed_resources.items())
assert all(resources[n] == v['sha256'] for n,v in owned.items())
assert set(c['candidate_sources']) == set(sp)
for name,item in sp.items():
    assert c['head_pins'][name] == item['before_sha256']
    assert c['candidate_pins'][name] == sha(ROOT / c['candidate_sources'][name]) == item['candidate_sha256']
for name in ('run.py', 'tests.py', 'epoch_gate.py', 'check.py'):
    compile((HERE / name).read_text(), name, 'exec')
base = ROOT / 'artifacts/css-hidden-svg-matrix-comparison-v1'
def function(path, name):
    tree = ast.parse(path.read_text())
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
assert ast.dump(function(HERE / 'tests.py', 'run')) == ast.dump(function(base / 'tests.py', 'run'))
assert ast.dump(function(HERE / 'tests.py', 'infrastructure_faults')) == ast.dump(function(base / 'tests.py', 'infrastructure_faults'))
old_tail = (base / 'run.py').read_text().split("finally:\n    state.update(status='restoring'", 1)[1]
new_tail = (HERE / 'run.py').read_text().split("finally:\n    state.update(status='restoring'", 1)[1]
assert new_tail == old_tail.replace('.svg-matrix-comparison.tmp', '.svg-length-comparison.tmp')
class Wpt:
    CONFIG = c
    outputs = {}
    @staticmethod
    def need(value, message):
        if not value:
            raise RuntimeError(message)
    @staticmethod
    def save(name, data):
        Wpt.outputs[name] = data
module = load('svg_test_check', HERE / 'tests.py')
rows = [{'test': name, 'subtest': label, 'status': 'PASS'} for name, labels in c['expected_subtests'].items() for label in labels]
run = {'rows': rows, 'ends': [{'test': name, 'status': 'OK'} for name in c['expected_subtests']]}
module.require_phase(Wpt, 'baseline', run)
module.require_phase(Wpt, 'candidate', run)
module.compare(Wpt, run, run)
negatives = 0
for reason,index,phase in [('candidate-main',0,'candidate'),('getter',2,'baseline'),('wrong-failure-stage',0,'baseline'),('existing-control',9,'baseline')]:
    damaged = copy.deepcopy(run)
    damaged['rows'][index].update(status='FAIL', expected='PASS', message='unrelated failure')
    try:
        module.require_phase(Wpt, phase, damaged)
    except RuntimeError:
        negatives += 1
    else:
        raise AssertionError(reason)
allowed = copy.deepcopy(run)
for row in allowed['rows']:
    if row['test'] in c['main_tests'] and 'after viewport resize' in row['subtest']:
        row.update(status='FAIL', expected='PASS', message='conversion immediately after viewport resize: mismatch')
assert sum(r['status'] == 'FAIL' for r in allowed['rows']) == 4
module.require_phase(Wpt, 'baseline', allowed)
module.compare(Wpt, allowed, run)
for reason,left_value,right_value in [('regression',{'status':'PASS'},{'status':'FAIL'}),('changed-failure',{'status':'FAIL','message':'old'},{'status':'FAIL','message':'new'})]:
    left,right = copy.deepcopy(run),copy.deepcopy(run)
    left['rows'][9].update(left_value)
    right['rows'][9].update(right_value)
    try:
        module.compare(Wpt,left,right)
    except RuntimeError:
        negatives += 1
    else:
        raise AssertionError(reason)
receipt = {'disabled': True, 'archived_epoch_authenticated': True, 'guards': 52, 'normalized_sources': 29,
           'existing_native_paths': 27, 'existing_installed_tests': 3, 'new_owned_wpt': 1,
           'candidate_native_paths': 2, 'main_cases': 9, 'existing_cases': 18,
           'wpt_files': 4, 'wpt_rows': 27, 'resources': len(read(HERE / 'RESOURCES.json')),
           'python_syntax': True, 'actual_new_metadata_absence_pinned': True,
           'wpt_runner_and_fault_parser_ast_unchanged': True,
           'restoration_tail_same_except_temp_name': True,
           'outcome_negative_checks': negatives, 'baseline_conversion_failure_optional_not_required': True,
           'browser_build_lint_or_live_native_checks_executed': False}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
