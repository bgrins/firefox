import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
output = Path(args.output)
assert not output.exists() and not output.is_symlink()
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def authenticate(mapping, base):
    for name, value in mapping.items():
        assert stat.S_ISREG((base / name).lstat().st_mode)
        assert sha(base / name) == value, name


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = read(HERE / 'CONFIG.json')
assert c['ready_for_execution'] is False
authenticate(read(HERE / 'REFERENCES.json'), ROOT)
for entry in c['required_seals'].values():
    path = ROOT / entry['path']
    assert sha(path) == entry['sha256']
    authenticate(read(path), path.parent)
epoch = ROOT / c['epoch']
assert sha(epoch / 'FILES.json') == c['epoch_manifest_sha256']
authenticate(read(epoch / 'FILES.json'), epoch)
final, pins, _, installed = load('factor_epoch', HERE / 'epoch_gate.py').bind(
    ROOT, epoch, read, sha, authenticate, load)
assert c['epoch_receipt'] == read(epoch / 'ROOT-FINAL-CHECK.json')
assert len(final['sources']) == 52 and len(pins) == 372 and len(installed) == 5
assert c['source_pins'] == {**final['sources'], 'dom/svg/SVGLength.cpp': c['head_pins']['dom/svg/SVGLength.cpp']}
assert len(c['guard_sources']) == 53 and len(c['sources']) == 30
assert len(c['modified_native_paths']) == 29
assert set(c['sources']) == set(c['modified_native_paths']) | set(c['candidate_sources'])
assert c['existing_test_pins'] == {n: v['sha256'] for n, v in installed.items()}
assert len(c['install']) == 2 and set(c['install']).isdisjoint(c['existing_tests'])
assert c['tests'] == c['baseline_tests']
assert c['expected_subtests'] == c['baseline_expected_subtests']
assert len(c['tests']) == 5 and sum(map(len, c['expected_subtests'].values())) == 34
proposal = ROOT / c['proposal']
assert {n: c['expected_subtests'][n] for n in c['main_tests']} == read(proposal / 'EXPECTED-TESTS.json')
assert sum(len(c['expected_subtests'][n]) for n in c['main_tests']) == 16
for name, fixture in c['install'].items():
    assert (HERE / fixture).read_bytes() == (proposal / c['proposal_test_files'][name]).read_bytes()
assert set(c['candidate_sources']) == {'dom/svg/SVGLength.cpp'}
assert {n: sha(ROOT / path) for n, path in c['candidate_sources'].items()} == c['candidate_pins']
resources = read(HERE / 'RESOURCES.json')
assert all(resources[n] == h for n, h in pins.items() if n not in c['epoch_receipt']['installed_binary_pins'])
for name in c['install']:
    assert resources[name] is None
    assert resources['testing/web-platform/meta/' + name.removeprefix('testing/web-platform/tests/') + '.ini'] is None
assert resources['testing/web-platform/meta/svg/animations/__dir__.ini'] is None

observed = (ROOT / c['observed_smil_fixture']).parent
authenticate(c['smil_binding'], ROOT)
assert (observed / 'fixture.html').read_bytes() == (HERE / 'smil-fixture.html').read_bytes()
state, receipt = read(observed / 'STATE.json'), read(observed / 'ROOT-FINAL-CHECK.json')
observed_final = read(observed / 'FINAL.json')
assert observed_final == read(observed / 'BEFORE.json') and observed_final['snapshot'] == final
assert receipt['state_sha256'] == sha(observed / 'STATE.json') and receipt['final_sha256'] == sha(observed / 'FINAL.json')
assert state['status'] == 'terminal' and state['complete'] and state['preserved'] and not state['native_changes']
assert receipt['status'] == 'REPRODUCED_AND_PRESERVED' and receipt['exit'] == 0
assert receipt['installed_tests'] == installed and receipt['installed_binary_pins'] == c['epoch_receipt']['installed_binary_pins']
assert receipt['owned_diagnostic_removed'] and receipt['owned_process_group_absent']
assert len(observed_final['pins']) == receipt['pin_count'] == 379
assert all(observed_final['pins'][n] == h for n, h in pins.items())
assert all(resources[n] == h for n, h in observed_final['pins'].items() if n not in c['epoch_receipt']['installed_binary_pins'])
module = load('factor_tests', HERE / 'tests.py')
events = [json.loads(line) for line in (observed / 'wpt-q-smil/raw.json').read_text().splitlines()]
observed_rows = [r for r in events if r.get('action') == 'test_status']
run, summary = read(observed / 'wpt-q-smil/RUN.json'), read(observed / 'SUMMARY.json')
assert observed_rows == run['rows'] == summary['rows']
assert run['complete'] and run['exit'] == 1 and run['before'] == run['after']
assert not module.infrastructure_faults(events)
assert [r['subtest'] for r in observed_rows] == c['expected_subtests'][c['main_tests'][1]]
assert [r['status'] for r in observed_rows] == ['PASS', 'FAIL', 'FAIL', 'PASS']
assert all(r['message'] == 'assert_approx_equals: interpolated absolute position expected 24 +/- 0.001 but got 10.713623046875'
           for r in observed_rows if r['status'] == 'FAIL')
assert summary['calibrated'] == receipt['calibrated'] == state['calibrated'] == 4
assert read(observed / 'wpt-q-smil/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}

base = ROOT / 'artifacts/css-svg-length-conversion-comparison-v1'
def function(path, name):
    text = path.read_text().replace('.svg-factor-comparison.tmp', '.svg-length-comparison.tmp')
    return next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
for name in ('run', 'infrastructure_faults'):
    assert ast.dump(function(HERE / 'tests.py', name)) == ast.dump(function(base / 'tests.py', name))
for name in ('replace_source', 'recovery_save'):
    assert ast.dump(function(HERE / 'run.py', name)) == ast.dump(function(base / 'run.py', name))
for name in ('run.py', 'tests.py', 'epoch_gate.py', 'check.py'):
    compile((HERE / name).read_text(), name, 'exec')


class Wpt:
    CONFIG = c
    @staticmethod
    def need(ok, why):
        if not ok:
            raise RuntimeError(why)
    @staticmethod
    def save(name, value):
        pass


rows = [{'test': name, 'subtest': label, 'status': 'PASS'} for name, labels in c['expected_subtests'].items() for label in labels]
passed = {'rows': rows, 'ends': [{'test': name, 'status': 'OK'} for name in c['expected_subtests']]}
module.require_phase(Wpt, 'baseline', passed)
module.require_phase(Wpt, 'candidate', passed)
module.compare(Wpt, passed, passed)
allowed = copy.deepcopy(passed)
for row in allowed['rows']:
    if row['test'] in c['main_tests'] and row['subtest'] in c['baseline_allowed_failure_messages']:
        row.update(status='FAIL', expected='PASS', message=c['baseline_allowed_failure_messages'][row['subtest']])
assert sum(r['status'] == 'FAIL' for r in allowed['rows']) == 8
module.require_phase(Wpt, 'baseline', allowed)
module.compare(Wpt, allowed, passed)
negative = 0
for phase, index, message in [('candidate', 0, 'converted factor'), ('baseline', 0, 'converted factor'),
                               ('baseline', 2, 'source pixel value'), ('baseline', 12, 'existing failure')]:
    bad = copy.deepcopy(passed)
    bad['rows'][index].update(status='FAIL', expected='PASS', message=message)
    try:
        module.require_phase(Wpt, phase, bad)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError((phase, index))
for kind in ('regression', 'changed-failure'):
    left, right = copy.deepcopy(passed), copy.deepcopy(passed)
    right['rows'][12].update(status='FAIL', message='new')
    if kind == 'changed-failure':
        left['rows'][12].update(status='FAIL', message='old')
    try:
        module.compare(Wpt, left, right)
    except RuntimeError:
        negative += 1
    else:
        raise AssertionError(kind)
result = {'disabled': True, 'actual_epoch_and_smil_authenticated': True,
          'guards': 53, 'normalization_sources': 30, 'modified_originals': 29,
          'owned_new_tests': 2, 'preserved_installed_tests': 5, 'main_rows': 16,
          'control_rows': 18, 'total_rows': 34, 'files': 5, 'resources': len(resources),
          'wpt_runner_fault_parser_unchanged': True,
          'atomic_replacement_recovery_save_unchanged_except_temp_name': True,
          'negative_outcome_checks': negative, 'browser_build_lint_native_actions': False}
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
