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
assert len(expected['sources']) == 49 and len(pins) == 337 and len(owned) == 2
assert c['source_pins'] == {**expected['sources'], 'dom/svg/SVGGraphicsElement.cpp': '1479b1fdba6c23a7f42cd739f934bf307a38b33900778e9f009c46b40ccad1c7'}
assert len(c['guard_sources']) == 50 and len(c['sources']) == 27
assert c['modified_native_paths'] == config['modified_native_paths'] and len(c['modified_native_paths']) == 26
assert set(c['sources']) == set(c['modified_native_paths']) | set(c['candidate_sources'])
assert c['existing_test_pins'] == {n: r['sha256'] for n, r in owned.items()}
assert len(c['tests']) == 7 and sum(map(len, c['expected_subtests'].values())) == 34
assert c['tests'] == c['baseline_tests'] and c['expected_subtests'] == c['baseline_expected_subtests']
proposal = ROOT / c['proposal']
authenticate(read(proposal / 'FILES.json'), proposal)
assert (HERE / 'fixture.html').read_bytes() == (proposal / 'hidden-svg-matrix-viewport-resize.html').read_bytes()
for name in ('availability-probe.html', 'validate_availability.py'):
    assert (HERE / name).read_bytes() == (proposal / name).read_bytes()
for name in ('run.py', 'tests.py', 'epoch_gate.py', 'validate_availability.py', 'check.py'):
    compile((HERE / name).read_text(), name, 'exec')
base = ROOT / 'artifacts/css-cssom-client-comparison-runtime-v1'
def function(path, name):
    tree = ast.parse(path.read_text())
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
assert ast.dump(function(HERE / 'tests.py', 'run')) == ast.dump(function(base / 'tests.py', 'run'))
assert ast.dump(function(HERE / 'tests.py', 'infrastructure_faults')) == ast.dump(function(base / 'tests.py', 'infrastructure_faults'))
old_tail = (base / 'run.py').read_text().split("finally:\n    state.update(status='restoring'", 1)[1].replace('.rounding-comparison.tmp', '.svg-matrix-comparison.tmp')
new_tail = (HERE / 'run.py').read_text().split("finally:\n    state.update(status='restoring'", 1)[1].replace("\n        recovery_save('FINAL-PINS.json', {**resources, **final['sources'], **state['restored_binary_pins']})", '')
assert old_tail == new_tail
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
for reason in ('candidate-main-fail', 'visible-baseline-fail', 'hidden-wrong-stage', 'control-unexpected'):
    damaged = copy.deepcopy(run)
    index = 1 if reason == 'hidden-wrong-stage' else 8 if reason == 'control-unexpected' else 0
    damaged['rows'][index].update(status='FAIL', expected='PASS', message='unrelated failure')
    try:
        module.require_phase(Wpt, 'baseline' if reason != 'candidate-main-fail' else 'candidate', damaged)
    except RuntimeError:
        negatives += 1
    else:
        raise AssertionError(reason)
allowed = copy.deepcopy(run)
allowed['rows'][1].update(status='FAIL', message='first matrix after viewport resize: mismatch')
module.require_phase(Wpt, 'baseline', allowed)
module.compare(Wpt, allowed, run)
receipt = {'disabled': True, 'archived_epoch_authenticated': True, 'guards': 50, 'normalized_sources': 27,
           'existing_native_paths': 26, 'existing_installed_tests': 2, 'new_owned_wpt': 1,
           'wpt_files': 7, 'wpt_rows': 34, 'resources': len(read(HERE / 'RESOURCES.json')),
           'availability_rows_each_phase': 8, 'python_syntax': True,
           'wpt_runner_and_fault_parser_ast_unchanged': True,
           'restoration_tail_same_except_temp_name_and_final_pin_receipt': True,
           'outcome_negative_checks': negatives, 'baseline_hidden_failure_optional_not_required': True,
           'browser_build_lint_or_live_native_checks_executed': False}
(HERE / 'STATIC-CHECK.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
