from collections import Counter
import hashlib
import json
from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEST = '/css/css-flexbox/flex-shrink-large-finite-scaled-weights.html'
helper = runpy.run_path(str(ROOT / 'artifacts/css-flex-main-positioning-target-20261111-v2/process.py'))

def report(path):
    rows = json.loads(path.read_text())['results']
    assert len(rows) == len({r['test'] for r in rows})
    return {r['test']: r for r in rows}

before = report(HERE / 'before/wptreport.json')
after = report(HERE / 'after/wptreport.json')
prior = report(ROOT / 'artifacts/css-flex-measured-base-repair-20261111-v2/after.wptreport.json')
assert set(before) == {TEST}
assert len(after) == 30 and len(prior) == 28
assert before[TEST]['status'] == after[TEST]['status'] == 'OK'
assert Counter(s['status'] for s in before[TEST]['subtests']) == {'PASS': 48, 'FAIL': 24}
assert len({s['name'] for s in before[TEST]['subtests']}) == 72
assert Counter(s['status'] for s in after[TEST]['subtests']) == {'PASS': 72}
assert {s['name'] for s in before[TEST]['subtests']} == {s['name'] for s in after[TEST]['subtests']}
assert all(s['name'].startswith('unequal ') and
           (s['name'].endswith('factor 3e+34') or s['name'].endswith('factor 1e+38'))
           for s in before[TEST]['subtests'] if s['status'] == 'FAIL')
for test, old in prior.items():
    new = after[test]
    assert old['status'] == new['status']
    assert {(s['name'], s['status']) for s in old['subtests']} == {
        (s['name'], s['status']) for s in new['subtests']}
for phase, expected_exit in [('before', 1), ('after', 0)]:
    out = HERE / phase
    commands = json.loads((out / 'COMMANDS.json').read_text())
    assert len(commands) == 1 and commands[0]['exit'] == expected_exit
    assert helper['absent'](commands[0]['pgid'])
    lifecycle = json.loads((out / 'LIFECYCLE-FOLLOWUP.json').read_text())
    assert lifecycle['probe'] == 'absent' and lifecycle['matching_rows'] == []
    assert lifecycle['inputs_unchanged'] and lifecycle['child_exit'] == expected_exit
    argv = json.loads((out / 'ARGV.json').read_text())
    expected = {'/' + name.removeprefix('testing/web-platform/tests/')
                for name in argv if name.startswith('testing/web-platform/tests/')}
    assert expected == set(before if phase == 'before' else after)
assert all(r['status'] in ['PASS', 'OK'] for r in after.values())
assert Counter(s['status'] for r in after.values() for s in r['subtests']) == {'PASS': 355}
pins = json.loads((HERE / 'after/INPUTS.json').read_text())
assert all(hashlib.sha256((ROOT / n).read_bytes()).hexdigest() == h for n, h in pins.items())
before_pins = json.loads((HERE / 'before/INPUTS.json').read_text())
assert before_pins['testing/web-platform/tests' + TEST] == pins['testing/web-platform/tests' + TEST]
assert before_pins['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL'] != pins[
    'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL']
source = (ROOT / 'layout/generic/nsFlexContainerFrame.cpp').read_text()
assert source == (HERE / 'before.cpp').read_text().replace(
    'float GetWeight(bool aIsUsingFlexGrow)', 'double GetWeight(bool aIsUsingFlexGrow)').replace(
    'return mFlexShrink * mFlexBaseSize;', 'return double(mFlexShrink) * mFlexBaseSize;')
solver = json.loads((HERE / 'solver/run-1/RESULTS.json').read_text())
assert solver['finite-weight-bound']['output'].splitlines()[0] == 'unsat'
assert solver['overflow-witness']['output'].splitlines()[0] == 'sat'
assert all(helper['absent'](c['pgid']) for c in json.loads((HERE / 'solver/run-1/COMMANDS.json').read_text()))
transport = json.loads((HERE / 'PATCH-RESULT.json').read_text())
assert transport['head_and_combined_apply_reverse'] and transport['scratch_removed']
assert hashlib.sha256((HERE / 'standalone.patch').read_bytes()).hexdigest() == transport['patch_sha256']
result = {'status': 'PASS', 'baseline': {'PASS': 48, 'FAIL': 24}, 'fixed_new_tests': 72,
          'wpt_files': 30, 'wpt_subtests': 355, 'wpt_outcomes': 385,
          'prior_file_results_preserved': 28, 'wrapper_failures_retained': True,
          'groups_freshly_absent': True, 'native_change_lines': 2,
          'standalone_paths': 2, 'new_confirmed_browser_bugs': 1,
          'lean_binary_proof': False, 'committed': False}
(HERE / 'ROOT-VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
