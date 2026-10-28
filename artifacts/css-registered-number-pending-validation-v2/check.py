import ast
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('gtest_assess', HERE / 'assess.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
roster = json.loads((HERE / 'ROSTER.json').read_text())
old_log = ROOT / 'artifacts/css-keyframe-typed-attribute-demand-runtime-v1/gtest-1/build.log'
old = module.assess(old_log.read_text(), roster['original_gtests'])
expected = roster['candidate_gtests']
groups = {}
for name in expected:
    groups.setdefault(name.split('.')[0], []).append(name)
lines = []
for names in groups.values():
    lines.append('0:00.00 SUITE_START: gtest - running 0 tests')
    for name in names:
        lines.extend(['0:00.00 TEST_START: ' + name, '0:00.00 TEST_END: PASS'])
    lines.append('0:00.00 SUITE_END')
lines.append('0:00.00 Ran 22 test(s) from 4 test suite(s) (0 disabled), with 0 failure(s).')
synthetic = '\n'.join(lines)
module.assess(synthetic, expected)
mutants = {}
for name in expected:
    block = '0:00.00 TEST_START: ' + name + '\n0:00.00 TEST_END: PASS'
    assert synthetic.count(block) == 1
    mutants['missing:' + name] = synthetic.replace(block, '', 1)
    mutants['failing:' + name] = synthetic.replace(block, block.replace('END: PASS', 'END: FAIL'), 1)
    mutants['duplicate:' + name] = synthetic.replace(block, block + '\n' + block, 1)
mutants.update({
    'missing-end': synthetic.replace('0:00.00 TEST_END: PASS', '', 1),
    'missing-suite-end': synthetic.replace('0:00.00 SUITE_END', '', 1),
    'wrong-summary-count': synthetic.replace('Ran 22 test(s)', 'Ran 20 test(s)'),
    'wrong-summary-suites': synthetic.replace('from 4 test suite(s)', 'from 3 test suite(s)'),
    'disabled': synthetic.replace('(0 disabled)', '(1 disabled)'),
    'failure-summary': synthetic.replace('with 0 failure(s)', 'with 1 failure(s)'),
    'missing-summary': '\n'.join(lines[:-1]),
    'duplicate-summary': synthetic + '\n' + lines[-1],
    'early-summary': lines[-1] + '\n' + '\n'.join(lines[:-1]),
    'process-crash': synthetic + '\nPROCESS_CRASH',
    'unexpected': synthetic + '\nTEST_UNEXPECTED_FAIL',
})
one_suite = ['0:00.00 SUITE_START: gtest - running 0 tests']
for name in expected:
    one_suite.extend(['0:00.00 TEST_START: ' + name, '0:00.00 TEST_END: PASS'])
one_suite.append('0:00.00 SUITE_END')
for unused in range(3):
    one_suite.extend(['0:00.00 SUITE_START: gtest - running 0 tests', '0:00.00 SUITE_END'])
one_suite.append(lines[-1])
mutants['one-mixed-suite-and-three-empty-suites'] = '\n'.join(one_suite)
for name, text in mutants.items():
    try:
        module.assess(text, expected)
    except AssertionError:
        continue
    raise AssertionError('Accepted malformed report: ' + name)
ast.parse((HERE / 'run.py').read_text())
result = {
    'historical_log_sha256': hashlib.sha256(old_log.read_bytes()).hexdigest(),
    'historical_twenty_name_report_accepted': old['all_selected_passed'],
    'synthetic_twenty_two_name_report_accepted': True,
    'rejected_mutants': sorted(mutants),
    'new_native_execution': False,
}
with (HERE / 'CHECK.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print('Historical report and synthetic gate passed;', len(mutants), 'corruptions rejected')
