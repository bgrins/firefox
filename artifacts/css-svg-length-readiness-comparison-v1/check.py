import argparse
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
output = Path(parser.parse_args().output)
assert not output.exists() and not output.is_symlink()
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def authenticate(mapping, base):
    for name, digest in mapping.items():
        assert sha(base / name) == digest, name


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


c = read(HERE / 'CONFIG.json')
assert c['ready_for_execution'] is False
authenticate(read(HERE / 'REFERENCES.json'), ROOT)
for item in c['required_seals'].values():
    path = ROOT / item['path']
    assert sha(path) == item['sha256']
    authenticate(read(path), path.parent)
epoch = ROOT / c['epoch']
assert sha(epoch / 'FILES.json') == c['epoch_manifest_sha256']
authenticate(read(epoch / 'FILES.json'), epoch)
assert c['epoch_receipt'] == read(epoch / 'ROOT-FINAL-CHECK.json')
gate = load('readiness_gate', HERE / 'epoch_gate.py')
before, pins, oldconfig, identities = gate.bind(ROOT, epoch, read, sha, authenticate, load)
assert before['sources'] == c['source_pins']
assert len(c['guard_sources']) == 53 and set(c['guard_sources']) == set(c['source_pins']) == set(c['head_pins'])
assert set(c['sources']) == set(c['modified_native_paths']) == set(oldconfig['modified_native_paths'])
assert len(c['sources']) == 30 and len(identities) == 7 and len(pins) == 387
assert c['existing_tests'] == sorted(identities)
assert c['existing_test_pins'] == {n: v['sha256'] for n, v in identities.items()}
assert not c['tracked_existing_tests']
assert set(c['candidate_sources']) == set(c['candidate_pins']) == {'dom/svg/DOMSVGLength.cpp', 'dom/svg/DOMSVGLength.h'}
assert all(sha(ROOT / path) == c['candidate_pins'][name] for name, path in c['candidate_sources'].items())
assert len(c['install']) == 1 and set(c['install']).isdisjoint(identities)
proposal = ROOT / c['proposal']
for name, fixture in c['install'].items():
    assert (HERE / fixture).read_bytes() == (proposal / c['proposal_test_files'][name]).read_bytes()
assert c['tests'] == c['baseline_tests'] and c['expected_subtests'] == c['baseline_expected_subtests']
assert len(c['expected_subtests']) == len(c['tests']) == 7
assert sum(map(len, c['expected_subtests'].values())) == 51
assert len(c['main_tests']) == 3 and sum(len(c['expected_subtests'][n]) for n in c['main_tests']) == 25
assert sum(map(len, c['baseline_allowed_failures'].values())) == 16
resources = read(HERE / 'RESOURCES.json')
assert all(resources[n] == h for n, h in pins.items() if n not in c['epoch_receipt']['installed_binary_pins'])
for name in c['install']:
    assert resources[name] is None
    assert resources['testing/web-platform/meta/' + name.removeprefix('testing/web-platform/tests/') + '.ini'] is None
assert all(resources[n] == v['sha256'] for n, v in identities.items())
base = ROOT / 'artifacts/css-svg-absolute-factor-comparison-v1'
def function(path, name):
    text = path.read_text().replace('.svg-readiness-comparison.tmp', '.svg-factor-comparison.tmp')
    return next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
for name in ('run', 'infrastructure_faults'):
    assert ast.dump(function(HERE / 'tests.py', name)) == ast.dump(function(base / 'tests.py', name))
for name in ('replace_source', 'recovery_save'):
    assert ast.dump(function(HERE / 'run.py', name)) == ast.dump(function(base / 'run.py', name))
marker = "finally:\n    state.update(status='restoring', recovery_errors=errors)"
assert (base / 'run.py').read_text().split(marker, 1)[1] == (HERE / 'run.py').read_text().replace('.svg-readiness-comparison.tmp', '.svg-factor-comparison.tmp').split(marker, 1)[1]
for path in HERE.glob('*.py'):
    compile(path.read_text(), str(path), 'exec')


class Wpt:
    CONFIG = c
    @staticmethod
    def need(ok, why):
        if not ok:
            raise RuntimeError(why)
    @staticmethod
    def save(name, value):
        pass


tests = load('readiness_tests', HERE / 'tests.py')
passed = {'rows': [{'test': name, 'subtest': label, 'status': 'PASS'} for name, labels in c['expected_subtests'].items() for label in labels]}
baseline = copy.deepcopy(passed)
for row in baseline['rows']:
    allowed = c['baseline_allowed_failures'].get(row['test'], {}).get(row['subtest'])
    if allowed:
        row.update(allowed)
assert sum(r['status'] == 'FAIL' for r in baseline['rows']) == 16
tests.require_phase(Wpt, 'baseline', baseline)
tests.require_phase(Wpt, 'baseline', passed)
tests.require_phase(Wpt, 'candidate', passed)
tests.compare(Wpt, baseline, passed)
rejected = 0
bad_cases = []
for i in range(51):
    bad = copy.deepcopy(passed)
    bad['rows'][i].update(status='FAIL', expected='PASS', message='failure', known_intermittent=[])
    bad_cases.append(('candidate', bad))
for i, row in enumerate(baseline['rows']):
    if row['status'] == 'FAIL':
        bad = copy.deepcopy(baseline)
        bad['rows'][i]['message'] += ' changed calibration'
        bad_cases.append(('baseline', bad))
bad_cases += [('baseline', {'rows': passed['rows'][:-1]}), ('baseline', {'rows': passed['rows'] + [passed['rows'][0]]})]
for phase, bad in bad_cases:
    try:
        tests.require_phase(Wpt, phase, bad)
    except RuntimeError:
        rejected += 1
    else:
        raise AssertionError((phase, bad))
result = {'disabled': True, 'actual_epoch_joined': True, 'guards': 53, 'normalization_sources': 30,
          'candidate_sources': 2, 'installed_test_identities': 7, 'owned_new_tests': 1,
          'main_cases': 25, 'control_cases': 26, 'total_cases': 51, 'files': 7,
          'resources': len(resources), 'failure_and_roster_negatives': rejected,
          'WPT_runner_fault_parser_unchanged': True, 'atomic_helper_unchanged': True,
          'restoration_tail_unchanged_except_temp_name': True, 'native_build_browser_index_actions': False}
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
