import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def main():
    assert sys.flags.isolated and not sys.flags.optimize
    analyze, observe = module('analyze'), module('observe')
    schema = json.loads((HERE / 'OBSERVATION-SCHEMA.json').read_text())
    expected = json.loads((HERE / 'EXPECTED-BASELINE.json').read_text())
    url = expected['harness'][0]['test']
    events = [{'action': 'suite_start'}, {'action': 'test_start', 'test': url}]
    records = []
    for name in schema['ids']:
        for phase in schema['phases']:
            records.append({'id': name, 'phase': phase, 'frames': [{'offset': None, 'computedOffset': 0.25, 'easing': 'linear', 'composite': 'auto', '--arbitrary': 'anything'}], 'baseline': {p: 'before' for p in schema['style_properties']}, 'computed': {p: 'after' for p in schema['style_properties']}, 'animationType': 'Anything', 'currentTime': None, 'progress': 0.4, 'effectComposite': 'replace'})
    events += [{'action': 'process_output', 'data': schema['marker'] + json.dumps(row)} for row in records]
    events += [dict(action='test_status', **row) for row in expected['subtests']]
    events += [dict(action='test_end', **expected['harness'][0]), {'action': 'suite_end'}]
    rejected = []
    with tempfile.TemporaryDirectory(prefix='custom-keyframe-parser-') as directory:
        path = Path(directory) / 'raw.jsonl'
        def write(rows):
            path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        def both():
            parsed = analyze.parse(path)
            assert analyze.rows(parsed) == analyze.rows(expected)
            assert len(observe.parse(path)) == 18
        def reject(name, rows=None, raw=None, operation=both):
            if raw is not None:
                path.write_text(raw)
            else:
                write(rows)
            try:
                operation()
            except (AssertionError, ValueError, KeyError, TypeError):
                rejected.append(name)
            else:
                raise AssertionError('Control accepted: ' + name)
        write(events)
        both()
        assert len(observe.parse(path)) == 18
        for name, action in [('missing-suite-start', 'suite_start'), ('missing-test-start', 'test_start'), ('missing-test-end', 'test_end'), ('missing-suite-end', 'suite_end')]:
            reject(name, [r for r in events if r['action'] != action])
        reject('duplicate-callback', events[:-2] + [events[-3]] + events[-2:])
        reject('missing-callback', events[:-3] + events[-2:])
        reject('duplicate-harness', events[:-1] + [events[-2]] + events[-1:])
        reject('duplicate-suite-end', events + [events[-1]])
        reject('crash', events + [{'action': 'crash'}])
        reject('error-log', events + [{'action': 'log', 'level': 'ERROR'}])
        reject('critical-log', events + [{'action': 'log', 'level': 'CRITICAL'}])
        reject('assertion-out-of-range', events + [{'action': 'assertion_count', 'count': 1, 'min_expected': 0, 'max_expected': 0}])
        for name, index, field, value in [('failed-setup', -3, 'status', 'FAIL'), ('callback-timeout', -3, 'status', 'TIMEOUT'), ('wrong-callback', -3, 'subtest', 'unknown'), ('harness-timeout', -2, 'status', 'TIMEOUT')]:
            rows = copy.deepcopy(events); rows[index][field] = value
            reject(name, rows)
        reject('missing-observation', events[:2] + events[3:])
        reject('duplicate-observation', events[:3] + [events[2]] + events[3:])
        def mutate_record(name, fn):
            rows = copy.deepcopy(events)
            row = copy.deepcopy(records[0]); fn(row)
            rows[2]['data'] = schema['marker'] + json.dumps(row)
            reject(name, rows, operation=lambda: observe.parse(path))
        for name, field, value in [('wrong-id','id','unknown'), ('wrong-phase','phase','middle'), ('bad-time-bool','currentTime',True), ('bad-time-string','currentTime','0'), ('bad-progress-infinity','progress',float('inf')), ('bad-progress-nan','progress',float('nan')), ('bad-animation-type','animationType',1), ('empty-animation-type','animationType',''), ('bad-effect-composite','effectComposite','auto'), ('frames-not-array','frames',{}), ('baseline-not-map','baseline',[]), ('unexpected-field','extra','x')]:
            mutate_record(name, lambda row,f=field,v=value: row.__setitem__(f,v))
        mutate_record('missing-field', lambda row: row.pop('currentTime'))
        mutate_record('missing-style', lambda row: row['computed'].pop('margin-left'))
        mutate_record('extra-style', lambda row: row['computed'].__setitem__('unexpected','x'))
        mutate_record('nonstring-style', lambda row: row['baseline'].__setitem__('color',1))
        mutate_record('missing-frame-field', lambda row: row['frames'][0].pop('offset'))
        mutate_record('bool-frame-offset', lambda row: row['frames'][0].__setitem__('offset',True))
        mutate_record('null-computed-offset', lambda row: row['frames'][0].__setitem__('computedOffset',None))
        mutate_record('nonstring-frame-value', lambda row: row['frames'][0].__setitem__('color',3))
        mutate_record('wrong-frame-composite', lambda row: row['frames'][0].__setitem__('composite','unknown'))
        for name, data in [('wrong-marker-version', events[2]['data'].replace('V1','V2',1)), ('prefix-before-marker', 'prefix ' + events[2]['data']), ('inner-truncation', events[2]['data'][:-3]), ('merged-observations', events[2]['data'] + events[3]['data']), ('duplicate-json-field', schema['marker'] + '{"id":"x",' + json.dumps(records[0])[1:])]:
            rows = copy.deepcopy(events); rows[2]['data'] = data
            reject(name, rows, operation=lambda: observe.parse(path))
        rows = copy.deepcopy(events); rows[2]['action'] = 'log'
        reject('marker-wrong-event', rows, operation=lambda: observe.parse(path))
        rows = copy.deepcopy(events); rows[2]['message'] = rows[2].pop('data')
        reject('marker-wrong-field', rows, operation=lambda: observe.parse(path))
        write(events)
        raw = path.read_text()
        reject('outer-truncation', raw=raw[:-5])
        reject('duplicate-outer-key', raw=raw.replace('{"action": "suite_start"}', '{"action":"suite_start","action":"suite_start"}',1))
        arbitrary = copy.deepcopy(events)
        for index in range(2,20):
            row = json.loads(arbitrary[index]['data'][len(schema['marker']):])
            row['frames'] = []
            row['currentTime'] = -123.5
            row['progress'] = 999
            row['computed'] = {p: 'uninterpreted 2em var(--x)' for p in schema['style_properties']}
            arbitrary[index]['data'] = schema['marker'] + json.dumps(row)
        write(arbitrary); both()
    print(json.dumps({'status':'PASS','rejected_controls':rejected,'positive_controls':['complete-seven-callback-eighteen-observation-stream','arbitrary-values-empty-frames-no-value-oracle']},indent=2))


if __name__ == '__main__':
    main()
