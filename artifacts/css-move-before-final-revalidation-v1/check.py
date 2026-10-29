import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
for source in HERE.glob('*.py'):
    ast.parse(source.read_text(), filename=str(source))
spec = importlib.util.spec_from_file_location('saved_replay', HERE / 'replay.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
assessment, differences = r.replay()
policy = r.read(r.PHASE / 'ASSESSMENT-POLICY.json')
metadata = r.read(r.PHASE / 'APPLICATION-METADATA.json')
checks = r.load('negative_checks', r.ROOT / policy['checks_helper'])
corrected = r.load('negative_assessor', HERE / 'assess.py')
events = [json.loads(line) for line in (r.PHASE / 'raw.jsonl').read_text().splitlines()]
names = {item['subtest'] for item in differences}
rejected = []
for name in ('missing_intermittent', 'nonempty_intermittent', 'null_intermittent',
             'old_projection_absence', 'control_message', 'missing_row', 'failed_row',
             'bad_ending', 'exit_one', 'wrong_expectation', 'extra_row', 'explicit_expected_pass'):
    items = copy.deepcopy(events)
    rows = [event for event in items if event.get('action') == 'test_status']
    target = next(row for row in rows if row['subtest'] in names)
    code = 0
    if name == 'missing_intermittent':
        del target['known_intermittent']
    elif name == 'nonempty_intermittent':
        target['known_intermittent'] = ['FAIL']
    elif name == 'null_intermittent':
        target['known_intermittent'] = None
    elif name == 'old_projection_absence':
        for row in rows:
            if row['subtest'] in names:
                del row['known_intermittent']
    elif name == 'control_message':
        next(row for row in rows if row['test'].endswith('animation-identity-restoration.html'))['message'] = 'changed'
    elif name == 'missing_row':
        items.remove(rows[0])
    elif name == 'failed_row':
        target['status'] = 'FAIL'
    elif name == 'bad_ending':
        next(event for event in items if event.get('action') == 'test_end')['status'] = 'ERROR'
    elif name == 'exit_one':
        code = 1
    elif name == 'wrong_expectation':
        target['expected'] = 'FAIL'
    elif name == 'extra_row':
        extra = copy.deepcopy(target)
        extra['subtest'] = 'not in roster'
        items.append(extra)
    else:
        target['expected'] = 'PASS'
    try:
        altered = corrected.assess(items, code, policy, checks, run_binding=metadata)
        assert not altered['comparison_gate_passed'], name
        rejected.append({'name': name, 'kind': 'gate_rejected'})
    except TypeError as error:
        assert name == 'null_intermittent' and 'NoneType' in str(error)
        rejected.append({'name': name, 'kind': 'invalid_null_list_rejected', 'error': str(error)})
print(json.dumps({'actual_completed_run_replay': True, 'browser_execution_performed': False,
                  'subtests': len(assessment['rows']), 'endings': len(assessment['ends']),
                  'exact_projection_differences': differences,
                  'only_changed_assessment_fields': ['comparison_errors', 'comparison_gate_passed'],
                  'negative_controls': rejected, 'full_live_guard_executed': False}, indent=2))
