import ast
from collections import Counter
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import stat
import struct
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = ROOT / 'artifacts'
R = A / 'css-round-numerical-baseline-runtime-v1'
P = A / 'css-round-numerical-baseline-plan-v2'
I = A / 'css-counter-additive-install-runtime-v1'


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def body(path):
    need(path.is_relative_to(A), 'archive-only input')
    need(stat.S_ISREG(path.lstat().st_mode), 'regular archive input')
    return path.read_bytes()


def sha(path):
    return hashlib.sha256(body(path)).hexdigest()


def read(path):
    return json.loads(body(path))


refs = {
    'artifacts/css-round-numerical-baseline-runtime-v1/FILES.json': '6488e9596b36cae63c72478be7d533b57812bdd2d680507807160b1d168cbd53',
    'artifacts/css-round-numerical-baseline-runtime-v1/ROOT-FINAL-CHECK.json': '05062d791fcc2c07558885caf7786aaf6f6b6db0d9a543724a55a3da07123dec',
    'artifacts/css-round-numerical-baseline-plan-v2/FILES.json': '11a466f65680865176806642ef363bc211e451ee6c52b6256c2c170534f6de9a',
    'artifacts/css-round-numerical-baseline-plan-review-v2/FILES.json': 'f5179195af5c194daa4f8d62b57b3d26a2b26a0344eeecee56282abdd1b96e9d',
    'artifacts/css-counter-additive-install-runtime-v1/FILES.json': 'dfe49f900d2ba34410520beabc165b0cb40639ca06fcc19ebe8dab1316b51bb5',
    'artifacts/css-counter-additive-install-results-review-v1/FILES.json': '2dff296aece7b2031e6934fe959eba3705f362ce8c12ad0beb0386defc4c932e',
    'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py': '647ef06b5129e91cbace778a7231874c7a0468df1deb6f785ebdde6ad33566c5',
}
for name, digest in refs.items():
    path = ROOT / name
    need(sha(path) == digest, 'reference ' + name)
    if path.name == 'FILES.json':
        for member, expected in read(path).items():
            need(not Path(member).is_absolute() and '..' not in Path(member).parts, 'member name')
            need(sha(path.parent / member) == expected, 'member ' + member)

for name, digest in read(R / 'CAPTURE-INPUTS.json')['references'].items():
    need(sha(ROOT / name) == digest, 'capture reference')
execution = read(R / 'ROOT-EXECUTION.json')
need(execution['session'] == 61360 and execution['exit'] == execution['classification_exit'] == 0,
     'actual execution receipt')
need(execution['underlying_wpt_exit'] == 1, 'diagnostic failure exit')
need(execution['capture_sha256'] == sha(R / 'capture.py')
     == read(R / 'CAPTURE-INPUTS.json')['capture_sha256'], 'reviewed capture unchanged')
need(execution['classification_sha256'] == sha(R / 'classify.py')
     != read(R / 'CAPTURE-INPUTS.json')['classification_sha256'], 'explicit classifier revision')

fixtures = read(P / 'FIXTURES.json')
roster = read(P / 'ROSTER.json')
config = read(R / 'CONFIG.json')
expected_config = read(I / 'CONFIG.json')
expected_config.update(tests=['testing/web-platform/tests/' + f['wpt_relative'] for f in fixtures],
                       expected_subtests=roster, reftests=[], install={},
                       expected_total=42, files_expected_count=4)
need(config == expected_config, 'whole inherited configuration')
before = read(R / 'BEFORE.json')
need(before == read(R / 'FINAL.json') == read(I / 'INSTALLATION.json')['after'], 'actual installed epoch')
need(before['pins'] == read(I / 'FINAL-PINS.json') and len(before['pins']) == 599, 'prior full map')
need(before['snapshot'] == read(I / 'FINAL.json'), 'source and index snapshot')
need(len(before['installed_tests']) == 21 and len(config['modified_native_paths']) == 42, 'identity/native inventories')
need(len(config['guard_sources']) == len(config['source_pins']) == 72, 'source guards')
need(all(before['pins'][n] == h for n, h in config['source_pins'].items()), 'all guarded source bodies')
index = config['index_expectations']
need(len(index['staged_paths']) == len(index['staged_payload_sha256']) == 925
     and set(index['staged_paths']) == set(index['staged_payload_sha256']), 'full staged payload map')
need(all(before['snapshot'][k] == index[k] for k in ('head', 'index_diff_sha256', 'index_entries_sha256')), 'full index joins')
baseline = dict(before['pins'])
for role in read(P / 'OWNERSHIP-PLAN.json')['roles']:
    need((role['path'] in baseline) == role['archived_role_present'], 'exact prior absence membership')
    need(baseline.get(role['path']) is None, 'prior absence')
    baseline[role['path']] = None
need(len(baseline) == 605 and baseline == read(R / 'BASELINE-PINS.json')
     == read(R / 'FINAL-PINS.json'), 'all 605 final roles')
owned = read(R / 'OWNED-TESTS.json')
need(set(owned) == set(config['tests']) and len(owned) == 4, 'four owned fixtures')
need(len({tuple(v['identity']) for v in owned.values()}) == 4, 'distinct owned identities')
need(not ({tuple(v['identity']) for v in owned.values()}
          & {tuple(v['identity']) for v in before['installed_tests'].values()}), 'installed identities protected')
active = dict(baseline)
for f in fixtures:
    name = 'testing/web-platform/tests/' + f['wpt_relative']
    need(owned[name]['sha256'] == sha(P / f['local']) == f['sha256'], 'fixture body')
    active[name] = f['sha256']
pre = read(R / 'PRE-CAPTURE.json')
need(pre == dict(before, pins=active), 'active exact overlay')
run = read(R / 'wpt-diagnostic/RUN.json')
need(run['before'] == run['after'] == active and run['complete'] and run['exit'] == 1, 'phase preservation')
need(run['command'] == ['./mach', 'wpt', '--headless', '--processes=1',
                         '--log-raw=' + str(R / 'wpt-diagnostic/raw.json'), *config['tests']], 'exact command')
events = [json.loads(line) for line in body(R / 'wpt-diagnostic/raw.json').splitlines()]
for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
    need(run[key] == [e for e in events if e.get('action') == action], 'raw join ' + key)
need(len(run['rows']) == 42 and len(run['starts']) == len(run['ends']) == 4, '42/4 complete roster')
need(len({(r['test'], r['subtest']) for r in run['rows']}) == 42, 'unique rows')
need({e['test'] for e in run['starts']} == set(roster), 'exact files')
need(all([r['subtest'] for r in run['rows'] if r['test'] == t] == names for t, names in roster.items()), 'ordered names')
need(all(e['status'] == 'OK' for e in run['ends']), 'all harnesses OK')
helper_tree = ast.parse(body(ROOT / next(n for n in refs if n.endswith('/tests.py'))))
helper_scope = {}
exec(compile(ast.Module(body=[n for n in helper_tree.body if isinstance(n, ast.FunctionDef)
                             and n.name in ('lifecycle', 'infrastructure_faults', 'exit_matches_results')],
                        type_ignores=[]), '<pure archived lifecycle>', 'exec'), helper_scope)
need(helper_scope['lifecycle'](events, config), 'raw lifecycle')
need(helper_scope['infrastructure_faults'](events) == run['infrastructure_faults'] == [], 'no infrastructure faults')
need(helper_scope['exit_matches_results'](run['exit'], run['rows'] + run['ends']), 'metadata-aware exit')
need(read(R / 'wpt-diagnostic/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}, 'process cleanup')
need(read(R / 'CLEANUP.json') == {'removed': list(owned), 'errors': [], 'capture_error': None}, 'owned fixture cleanup')
receipt = read(R / 'ROOT-FINAL-CHECK.json')
need(receipt == {'status': 'NUMERICAL_BASELINE_PRESERVATION_PASS', 'roles': 605, 'sources': 72,
                 'installed_identities': 21, 'staged_paths': 925, 'native_paths': 42,
                 'temporary_tests_removed': 4, 'capture_error': None,
                 'final_pins_sha256': sha(R / 'FINAL-PINS.json')}, 'root preservation receipt')
architecture = read(R / 'ARCHITECTURE.json')
need(architecture['binary_pins'] == read(I / 'BUILT-BINARIES.json'), 'installed binary pair')
for name, binary in architecture['binaries'].items():
    need(binary['bits'] == 64 and binary['sha256'] == baseline[name]
         == architecture['binary_pins'][name], '64-bit binary hash join')
    header = struct.unpack('<8I', bytes.fromhex(binary['header_hex']))
    need(header[0] == 0xFEEDFACF and header[1] == binary['cpu_type'] == 16777228, 'archived architecture header')

tree = ast.parse(body(R / 'classify.py'))
start = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'policy_cases' for t in n.targets))
end = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.With))
metadata = next(n for n in tree.body if isinstance(n, ast.For)
                and isinstance(n.target, ast.Name) and n.target.id == 'row')
pure = compile(ast.Module(body=[metadata, *tree.body[start:end]], type_ignores=[]), '<pure classifier>', 'exec')


def classify(value):
    scope = {'result': value, 'json': json, 'math': math, 're': re, 'need': need,
             'families': read(P / 'CLASSIFICATION.json')['families'],
             'family_by_test': {'/' + f['wpt_relative']: f['family'] for f in fixtures}}
    exec(pure, scope)
    return scope['summary']


summary = classify(run)
need(summary == read(R / 'CLASSIFICATION.json'), 'exact independently replayed classification')
need(summary['counts'] == {'PASS': 11, 'FAIL': 31} and summary['semantic_mismatches'] == 29
     and summary['policy_differences'] == 2 and not summary['native_acceptance'], 'observed counts, no acceptance')
negative = []


def reject(label, mutate):
    value = copy.deepcopy(run)
    mutate(value)
    try:
        classify(value)
    except (RuntimeError, ValueError, TypeError, KeyError):
        negative.append(label)
    else:
        raise RuntimeError('accepted negative ' + label)


policy_index = next(i for i, r in enumerate(run['rows']) if 'snapshot=' in (r.get('message') or ''))
for label, old, new in [('policy expression', 'sign(1em - 16px)', 'sign(2em - 16px)'),
                        ('policy prediction', 'expected false but got true', 'expected true but got true'),
                        ('duplicate policy keys', '"supports":true', '"supports":false,"supports":true')]:
    reject(label, lambda v, old=old, new=new: v['rows'][policy_index].update(message=v['rows'][policy_index]['message'].replace(old, new)))
for label, field, value in [('expected metadata', 'expected', 'CRASH'),
                            ('intermittent type', 'known_intermittent', 'PASS'),
                            ('intermittent status', 'known_intermittent', ['TIMEOUT'])]:
    reject(label, lambda v, field=field, value=value: v['rows'][0].update({field: value}))
reject('harness metadata', lambda v: v['ends'][0].update(expected='FAIL'))
for label in ['opacity setter retention', 'finite in-range first opacity', 'finite in-range repeated opacity', 'stable computed value']:
    reject(label, lambda v, label=label: v['rows'][0].update(message='assert_equals: ' + label + ' expected 0 but got 1'))
for value in ['NaN', 'Infinity', '1e999', '0', '-1', '1.5']:
    reject('numeric domain ' + value, lambda v, value=value: v['rows'][0].update(message='assert_equals: expected 0 but got ' + value))
control_index = next(i for i, r in enumerate(run['rows']) if r['status'] == 'PASS' and 'control' in r['subtest'])
reject('strict control', lambda v: v['rows'][control_index].update(status='FAIL', message='assert_equals: expected 0 but got 1'))
all_pass = copy.deepcopy(run)
for row in all_pass['rows']:
    row.update(status='PASS', message=None)
need(classify(all_pass)['counts'] == {'PASS': 42, 'FAIL': 0}, 'no forced failure count')
check = {'status': 'NUMERICAL_BASELINE_TERMINAL_REVIEW_GO', 'runtime_sha256': refs[str(R.relative_to(ROOT) / 'FILES.json')],
         'session': 61360, 'exit': 0, 'wpt_exit': 1, 'raw_records': len(events),
         'counts': summary['counts'], 'families': summary['families'], 'numerical_mismatches': 29,
         'policy_differences': 2, 'harnesses_ok': 4, 'roles': 605, 'sources': 72,
         'installed_identities': 21, 'staged_paths': 925, 'native_paths': 42, 'removed_owned_fixtures': 4,
         'classification_negative_checks': negative, 'native_acceptance': False,
         'live_inputs_read': False, 'live_actions': False}
for name, value in [('CHECK.json', check), ('REFERENCES.json', refs)]:
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
print(json.dumps(check, indent=2))
