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
FIXTURES = ROOT / 'artifacts/css-name-repeat-context-repair-v3'
EPOCH = ROOT / 'artifacts/css-round-infinite-value-step-runtime-v1'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique_object(pairs):
    need(len({key for key, value in pairs}) == len(pairs), 'duplicate JSON key')
    return dict(pairs)


def no_constant(value):
    raise ValueError('nonfinite JSON constant')


def loads(text):
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=no_constant)


read = lambda p: loads(p.read_text())


def authenticate(directory, digest):
    need(sha(directory / 'FILES.json') == digest, 'manifest')
    for name, value in read(directory / 'FILES.json').items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'member')
        path = directory / name
        need(stat.S_ISREG(path.lstat().st_mode) and sha(path) == value, 'payload ' + name)


authenticate(FIXTURES, '454359c092351c37d751f6fcdb21b75cb7959233dfc05523183d84bb8fbeb259')
authenticate(EPOCH, '736a7240a8105a2e765a93b0d6862ce808e010fb77953869575e9188ba86fc5a')
inputs = read(HERE / 'INPUTS.json')
need(sha(HERE / 'classify.py') == inputs['classify_sha256'], 'bound classifier')
test = 'testing/web-platform/tests/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'
url = '/css/css-grid/subgrid/subgrid-contextual-name-repeat.html'
fixture_hash = '81e4da216fbf4cd31a500f4b4d8156bd633205000823a4f12057ce0c6cb5d3f3'
before = read(HERE / 'BEFORE.json')
need(before == read(EPOCH / 'FINAL.json'), 'authenticated installed epoch')
baseline = dict(before['pins'])
for name in (test, test.replace('/tests/', '/meta/') + '.ini'):
    need(name not in baseline, 'new absence role')
    baseline[name] = None
active = {**baseline, test: fixture_hash}
config = read(EPOCH / 'CONFIG.json')
config.update(tests=[test], expected_subtests={url: read(FIXTURES / 'ROSTER.json')},
              reftests=[], install={}, expected_total=10, files_expected_count=1)
need(config == read(HERE / 'CONFIG.json'), 'derived exact config')
pre = read(HERE / 'PRE-CAPTURE.json')
final = read(HERE / 'FINAL.json')
need(pre['pins'] == active and final['pins'] == baseline
     and baseline == read(HERE / 'BASELINE-PINS.json') == read(HERE / 'FINAL-PINS.json'),
     'derived full phase maps')
need(pre['snapshot'] == final['snapshot'] == before['snapshot']
     and pre['installed_tests'] == final['installed_tests'] == before['installed_tests'],
     'source/index/installed identity preservation')
owned = read(HERE / 'OWNED-TESTS.json')
need(set(owned) == {test} and owned[test]['sha256'] == fixture_hash, 'exact owned fixture')
need(set(owned[test]) == {'identity', 'sha256'} and len(owned[test]['identity']) == 2
     and all(type(v) is int for v in owned[test]['identity']), 'owned identity schema')
need(read(HERE / 'CLEANUP.json') == {'removed': [test], 'errors': [], 'capture_error': None},
     'fixture cleanup')
root = read(HERE / 'ROOT-FINAL-CHECK.json')
need(root['status'] == 'NAME_REPEAT_BASELINE_PRESERVATION_PASS'
     and root['capture_error'] is None and root['temporary_tests_removed'] == 1
     and root['final_pins_sha256'] == sha(HERE / 'FINAL-PINS.json'), 'final root receipt')
helper = ROOT / 'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py'
need(sha(helper) == '647ef06b5129e91cbace778a7231874c7a0468df1deb6f785ebdde6ad33566c5', 'helper hash')
spec = importlib.util.spec_from_file_location('name_repeat_capture_checks', helper)
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
directory = HERE / 'wpt-diagnostic'
raw = directory / 'raw.json'
need(stat.S_ISREG(raw.lstat().st_mode) and raw.stat().st_size <= 128 * 1024 * 1024, 'raw log')
events = [loads(line) for line in raw.read_text().splitlines()]
run = read(directory / 'RUN.json')
need(run['command'] == ['./mach', 'wpt', '--headless', '--processes=1',
                         '--log-raw=' + str(raw), test], 'exact command')
need(run['complete'] is True and not tests.infrastructure_faults(events)
     and run['infrastructure_faults'] == [] and tests.lifecycle(events, config), 'complete lifecycle')
for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
    need(run[key] == [e for e in events if e.get('action') == action], 'raw/RUN ' + key)
need(len(run['starts']) == len(run['ends']) == 1 and run['ends'][0]['status'] == 'OK', 'one OK harness')
need(len(run['rows']) == 10 and [r['subtest'] for r in run['rows']] == config['expected_subtests'][url]
     and all(r['test'] == url for r in run['rows']), 'ordered ten cases')
for row in run['rows'] + run['ends']:
    allowed = {'PASS', 'FAIL'} if row['action'] == 'test_status' else {'OK'}
    need(row['status'] in allowed, 'terminal status')
    if 'expected' in row:
        need(row['expected'] in allowed, 'expected metadata')
    if 'known_intermittent' in row:
        need(type(row['known_intermittent']) is list and all(s in allowed for s in row['known_intermittent']),
             'intermittent metadata')
need(tests.exit_matches_results(run['exit'], run['rows'] + run['ends'])
     and run['before'] == run['after'] == active, 'exit and capture maps')
need(read(directory / 'CLEANUP.json') == {'owned_group_absent': True, 'errors': []}, 'process cleanup')
controls = {'Name-repeat positive range after computation: calc(0)',
            'Name-repeat literal and structural safeguards remain enforced'}
observations, issues = [], []
for row in run['rows']:
    if row['status'] == 'PASS':
        continue
    if row['subtest'] not in controls and row.get('message') == (
            'assert_true: target name-repeat: declaration admission expected true got false'):
        observations.append({'test': row['test'], 'subtest': row['subtest'],
                             'classification': 'TARGET_ADMISSION_FAILURE',
                             'later_history_reached': False})
    else:
        issues.append(row)
result = {'status': 'NAME_REPEAT_BASELINE_CLASSIFIED' if not issues else 'CLASSIFICATION_REJECTED',
          'counts': {s: sum(r['status'] == s for r in run['rows']) for s in ('PASS', 'FAIL')},
          'subtests': 10, 'harnesses_ok': 1, 'admission_failures': len(observations),
          'observations': observations, 'issues': issues, 'known_bug': 2037744,
          'required_failure_count': None, 'native_acceptance': False}
with (HERE / 'CLASSIFICATION.json').open('x') as stream:
    stream.write(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: v for k, v in result.items() if k not in ('observations', 'issues')}, indent=2))
need(not issues, 'calibration or unclassified failure')
