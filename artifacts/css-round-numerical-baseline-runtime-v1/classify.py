import importlib.util
import json
import math
from pathlib import Path
import re
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLAN = ROOT / 'artifacts/css-round-numerical-baseline-plan-v2'
read = lambda p: json.loads(p.read_text())


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


config = read(HERE / 'CONFIG.json')
result = read(HERE / 'wpt-diagnostic/RUN.json')
events = [json.loads(line) for line in (HERE / 'wpt-diagnostic/raw.json').read_text().splitlines()]
path = ROOT / 'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py'
spec = importlib.util.spec_from_file_location('numerical_capture_checks', path)
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
need(result['complete'] and not tests.infrastructure_faults(events), 'complete capture without infrastructure faults')
need(tests.lifecycle(events, config), 'raw event lifecycle')
for row in result['rows'] + result['ends']:
    allowed = {'PASS', 'FAIL'} if 'subtest' in row else {'OK'}
    if 'expected' in row:
        need(row['expected'] in allowed, 'expected metadata')
    if 'known_intermittent' in row:
        need(isinstance(row['known_intermittent'], list)
             and all(s in allowed for s in row['known_intermittent']), 'intermittent metadata')
for key, action in [('rows', 'test_status'), ('starts', 'test_start'), ('ends', 'test_end')]:
    need(result[key] == [e for e in events if e.get('action') == action], 'raw/result join ' + key)
need(tests.exit_matches_results(result['exit'], result['rows'] + result['ends']), 'metadata-aware exit')
need(result['before'] == result['after'] == read(HERE / 'PRE-CAPTURE.json')['pins'], 'all phase roles')
need(len(result['rows']) == 42 and len(result['ends']) == 4
     and all(e['status'] == 'OK' for e in result['ends']), 'exact counts and harnesses')
need(all([r['subtest'] for r in result['rows'] if r['test'] == test] == names
         for test, names in read(PLAN / 'ROSTER.json').items()), 'ordered roster')
need(read(HERE / 'wpt-diagnostic/CLEANUP.json') == {'owned_group_absent': True, 'errors': []}, 'process cleanup')
need(read(HERE / 'CLEANUP.json')['errors'] == []
     and read(HERE / 'CLEANUP.json')['capture_error'] is None, 'fixture cleanup')
families = read(PLAN / 'CLASSIFICATION.json')['families']
family_by_test = {'/' + f['wpt_relative']: f['family'] for f in read(PLAN / 'FIXTURES.json')}
policy_cases = {
    'unchanged discarded unknown step': ('repeat(round(up, infinity, sign(1em - 16px)), 1px)', True),
    'retained unknown value': ('repeat(round(up, sign(1em - 16px), infinity), 1px)', False),
    'retained unknown product value': ('repeat(round(up, infinity * sign(1em - 16px), infinity), 1px)', False),
    'resolved absolute sign': ('repeat(calc(2 + round(to-zero, sign(1px), infinity)), 1px)', True),
    'invalid dimensional integer': ('repeat(round(up, 1px, 1px), 1px)', False),
}


def unique_object(pairs):
    need(len({key for key, value in pairs}) == len(pairs), 'duplicate snapshot keys')
    return dict(pairs)


classified = []
for row in result['rows']:
    family = family_by_test[row['test']]
    policy = families[family]
    name = row['subtest']
    item = {'test': row['test'], 'subtest': name, 'family': family, 'status': row['status'],
            'message': row.get('message'), 'expected': row.get('expected'),
            'known_intermittent': row.get('known_intermittent')}
    if row['status'] == 'PASS':
        item['classification'] = 'POLICY_PREDICTION_MATCH' if family == 'admission_policy' else 'PASS'
    else:
        need(row['status'] == 'FAIL' and name in policy['target_names'], 'strict control ' + name)
        message = row.get('message') or ''
        if family == 'finite_pow':
            need(message == policy['allowed_final_assertion'], 'finite calibration or unknown failure ' + name)
            item.update(classification='CALIBRATED_SEMANTIC_MISMATCH', observed=1, normative_expected=0)
        elif family in ('runtime_nan', 'infinite_guard'):
            if family == 'runtime_nan':
                label = 'NaN propagates through round and reciprocal '
            elif name == 'infinite step: observed deferred-value route':
                label = ''
            else:
                match = re.fullmatch(r'infinite step: (nearest|up|down|to-zero), (-?infinity), font (16|32)', name)
                need(match is not None, 'known independent context')
                label = 'NaN or both-infinite result for ' + match[2] + ' at font ' + match[3] + ' '
            match = re.fullmatch(re.escape('assert_equals: ' + label + 'expected 0 but got ') + r'([-+0-9.eE]+)', message)
            need(match is not None, 'numerical calibration or unknown failure ' + name)
            actual = float(match[1])
            need(math.isfinite(actual) and 0 < actual <= 1, 'finite observable opacity')
            item.update(classification='CALIBRATED_SEMANTIC_MISMATCH', observed=actual, normative_expected=0)
        else:
            prefix = 'assert_equals: source-predicted implementation policy; snapshot='
            need(message.startswith(prefix), 'policy calibration failure ' + name)
            snapshot, end = json.JSONDecoder(object_pairs_hook=unique_object).raw_decode(message[len(prefix):])
            suffix = message[len(prefix) + end:]
            match = re.fullmatch(r' expected (true|false) but got (true|false)', suffix)
            need(match is not None and set(snapshot) == {'value', 'supports', 'serialized'}, 'policy snapshot shape')
            need(isinstance(snapshot['value'], str) and type(snapshot['supports']) is bool
                 and isinstance(snapshot['serialized'], str), 'policy snapshot types')
            need(bool(snapshot['serialized']) == snapshot['supports'] == (match[2] == 'true')
                 and match[1] != match[2], 'policy snapshot consistency')
            expression, prediction = policy_cases[name.removeprefix('Round integer policy: ')]
            need(snapshot['value'] == expression and (match[1] == 'true') == prediction,
                 'exact policy expression and prediction')
            item.update(classification='POLICY_DIFFERENCE', snapshot=snapshot, normative_bug_inference=False)
    classified.append(item)
summary = {'status': 'CALIBRATED_DIAGNOSTIC_CLASSIFIED', 'subtests': 42, 'harnesses_ok': 4,
           'counts': {s: sum(r['status'] == s for r in classified) for s in ('PASS', 'FAIL')},
           'families': {family: {s: sum(r['family'] == family and r['status'] == s for r in classified)
                                 for s in ('PASS', 'FAIL')} for family in families},
           'semantic_mismatches': sum(r['classification'] == 'CALIBRATED_SEMANTIC_MISMATCH' for r in classified),
           'policy_differences': sum(r['classification'] == 'POLICY_DIFFERENCE' for r in classified),
           'required_failure_count': None, 'native_acceptance': False, 'rows': classified}
with (HERE / 'CLASSIFICATION.json').open('x') as stream:
    stream.write(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'rows'}, indent=2))
