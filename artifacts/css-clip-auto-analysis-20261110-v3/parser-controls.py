import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('analysis', HERE/'analyze.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def make_wpt():
    result = [{'action': 'suite_start'}]
    existing = json.loads((HERE/'runtime-inputs/existing-iteration-callbacks.json').read_text())
    pages = [(a.CONTROL, [(n, 'FAIL' if n in a.NEW_FAILURES else 'PASS') for n in sorted(a.NEW_CONTROLS)]),
             (a.EXISTING, [(r['subtest'], r['status']) for r in existing]),
             (a.DIAGNOSTIC, [('SMIL diagnostic numeric controls are active', 'PASS')])]
    for test, callbacks in pages:
        result.append({'action': 'test_start', 'test': test})
        if test == a.DIAGNOSTIC:
            for identity, (time, underlying) in a.diagnostic_inputs().items():
                data = {'schema': 1, 'id': identity, 'time': time, 'underlying': underlying,
                        'clip': underlying, 'paused': True}
                result.append({'action': 'process_output', 'data': a.MARKER+json.dumps(data)})
        for name, status in callbacks:
            result.append({'action': 'test_status', 'test': test, 'subtest': name, 'status': status})
        result.append({'action': 'test_end', 'test': test, 'status': 'OK'})
    result.append({'action': 'suite_end'})
    return result


def make_mochi():
    result = [{'action': 'suite_start'}]
    for test in json.loads((HERE/'RUN-PLAN.json').read_text())['mochitests']:
        result.append({'action': 'test_start', 'test': test})
        for _ in range(2):
            result.append({'action': 'test_status', 'test': test, 'subtest': None, 'message': 'Repeated assertion label', 'status': 'PASS'})
        result.append({'action': 'test_end', 'test': test, 'status': 'PASS'})
    result.append({'action': 'suite_end'})
    return result


def main():
    rejected = []
    def rejects(name, operation):
        try:
            operation()
        except (AssertionError, ValueError, TypeError, KeyError):
            rejected.append(name)
        else:
            raise AssertionError('Accepted malformed control: '+name)
    with tempfile.TemporaryDirectory(prefix='clip-parser-controls-') as directory:
        def parse(rows, flavor='wpt'):
            path = Path(directory)/'raw.jsonl'
            path.write_text(''.join((row if isinstance(row, str) else json.dumps(row))+'\n' for row in rows))
            return a.parse(path, flavor)
        wpt, mochi = make_wpt(), make_mochi()
        baseline = {'wpt': parse(wpt), 'mochitest': parse(mochi, 'mochitest')}
        a.baseline_check(baseline)
        known_failure=copy.deepcopy(baseline)
        known_failure['mochitest']['subtests'][0].update(status='FAIL', expected='FAIL')
        a.baseline_check(known_failure)
        del known_failure['mochitest']['subtests'][0]['expected']
        a.baseline_check(known_failure)
        candidate = copy.deepcopy(baseline)
        for row in candidate['wpt']['subtests']:
            if row['test'] == a.CONTROL and row['subtest'] in a.NEW_FAILURES or row['test'] == a.EXISTING and row['subtest'] == a.CLIP:
                row['status'] = 'PASS'
        assert a.compare(baseline, candidate)['gate_passed']
        obs = next(i for i, row in enumerate(wpt) if row['action'] == 'process_output')
        cb = next(i for i, row in enumerate(wpt) if row['action'] == 'test_status')
        rejects('missing-observation', lambda: parse(wpt[:obs]+wpt[obs+1:]))
        rejects('duplicate-observation', lambda: parse(wpt[:obs]+[wpt[obs]]+wpt[obs:]))
        rejects('duplicate-WPT-callback', lambda: parse(wpt[:cb]+[wpt[cb]]+wpt[cb:]))
        rejects('missing-callback', lambda: parse(wpt[:cb]+wpt[cb+1:]))
        wrong_wpt=copy.deepcopy(wpt)
        next(row for row in wrong_wpt if row['action'] == 'test_end')['status']='PASS'
        rejects('WPT-PASS-harness-ending', lambda: parse(wrong_wpt))
        wrong_mochi=copy.deepcopy(mochi)
        next(row for row in wrong_mochi if row['action'] == 'test_end')['status']='OK'
        rejects('Mochitest-OK-harness-ending', lambda: parse(wrong_mochi, 'mochitest'))
        wrong_mochi=copy.deepcopy(mochi)
        next(row for row in wrong_mochi if row['action'] == 'test_end')['status']='FAIL'
        rejects('Mochitest-FAIL-harness-ending', lambda: parse(wrong_mochi, 'mochitest'))
        rejects('missing-suite-end', lambda: parse(wpt[:-1]))
        rejects('early-suite-end', lambda: parse([wpt[0], wpt[-1]]+wpt[1:-1]))
        for name, key, value in [('schema-bool', 'schema', True), ('unexpected-id', 'id', 'unknown'),
                                  ('wrong-time', 'time', 1), ('wrong-base', 'underlying', 'auto'),
                                  ('empty-clip', 'clip', ''), ('not-paused', 'paused', False),
                                  ('extra-key', 'extra', 1)]:
            rows = copy.deepcopy(wpt)
            row = json.loads(rows[obs]['data'].split(a.MARKER, 1)[1]);row[key]=value
            rows[obs]['data'] = a.MARKER+json.dumps(row)
            rejects(name, lambda rows=rows: parse(rows))
        rows=copy.deepcopy(wpt);rows[obs]['data']=a.MARKER+'{'
        rejects('malformed-observation-json', lambda: parse(rows))
        rows=copy.deepcopy(wpt);rows[obs]['data']=rows[obs]['data'].replace('"schema": 1', '"schema": 1, "schema": 1')
        rejects('duplicate-json-key', lambda: parse(rows))
        rejects('crash-record', lambda: parse(wpt+[{'action':'crash'}]))
        for name, modify in [
            ('missing-intended-improvement', lambda d: next(r for r in d['wpt']['subtests'] if r['test'] == a.CONTROL and r['subtest'] in a.NEW_FAILURES).update(status='FAIL')),
            ('extra-unrelated-improvement', lambda d: next(r for r in d['wpt']['subtests'] if r['test'] == a.EXISTING and 'align-content' in r['subtest']).update(status='PASS')),
            ('changed-svg-observation', lambda d: next(iter(d['wpt']['observations'].values())).update(clip='auto')),
            ('changed-smil-result', lambda d: d['mochitest']['subtests'][0].update(status='FAIL')),
            ('missing-smil-callback', lambda d: d['mochitest']['subtests'].pop()),
        ]:
            changed=copy.deepcopy(candidate);modify(changed)
            assert not a.compare(baseline, changed)['gate_passed'], name
            rejected.append(name)
        changed=copy.deepcopy(baseline);changed['mochitest']['subtests'][0].update(status='FAIL', expected='PASS')
        rejects('baseline-unexpected-smil-failure', lambda: a.baseline_check(changed))
    return {'status':'PASS', 'synthetic_only':True, 'positive_four_improvements_and_preserved_svg':True,
            'repeated_mochitest_names_are_disambiguated':True, 'rejected_controls':rejected,
            'browser_tests_executed':False}


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
