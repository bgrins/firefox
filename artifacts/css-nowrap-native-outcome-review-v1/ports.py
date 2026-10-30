import configparser
import hashlib
import json
import re

KNOWN = {
    '/css/css-text/hyphens/hyphenate-limit-chars-001.html': '/css/css-text/hyphens/reference/hyphenate-limit-chars-001-ref.html',
    '/css/css-text/hyphens/hyphens-span-001.html': '/css/css-text/hyphens/reference/hyphens-span-001-ref.html',
    '/css/css-text/line-break/line-break-anywhere-and-white-space-002.html': '/css/css-text/line-break/reference/line-break-anywhere-004-ref.html',
    '/css/css-text/word-break/word-break-break-all-062.html': '/css/css-text/word-break/reference/word-break-break-all-062-ref.html',
}


def normalize(events, assessment, manifest, signature):
    tree = manifest['items']['reftest']
    for test, reference in KNOWN.items():
        entry = tree
        for part in test[1:].split('/'):
            entry = entry[part]
        assert entry[1:] == [[None, [[reference, '==']], {}]]
    ends = {e['test']: e for e in assessment['ends'] if e['test'] in KNOWN}
    assert len(ends) == 4
    assert sum(e['test'] in KNOWN for e in assessment['ends']) == 4
    ports = set()
    normalized = []
    evidence = []
    for event in assessment['rows'] + assessment['ends']:
        row = signature(event)
        if event['action'] == 'test_end' and event['test'] in KNOWN:
            assert event['status'] == 'PASS' and event.get('expected', 'PASS') == 'PASS'
            assert event.get('known_intermittent', []) == []
            match = re.fullmatch(r'Testing http://web-platform\.test:(\d+)(/[^\s]+) == http://web-platform\.test:(\d+)(/[^\s]+)\n', event['message'])
            assert match
            port, test, other_port, reference = match.groups()
            assert port == other_port and 0 < int(port) < 65536
            assert test == event['test'] and reference == KNOWN[test]
            starts = [e for e in events if e.get('action') == 'log' and e.get('component') == 'wptserve' and e.get('message') == 'Starting https server on https://127.0.0.1:' + port]
            stops = [e for e in events if e.get('action') == 'log' and e.get('component') == 'wptserve' and e.get('message') == 'Stopped http server on 127.0.0.1:' + port]
            assert len(starts) == len(stops) == 1
            assert starts[0]['pid'] == stops[0]['pid'] and starts[0]['time'] < event['time'] < stops[0]['time']
            ports.add(int(port))
            row['message'] = 'Testing http://web-platform.test:<ROLE_PORT>' + test + ' == http://web-platform.test:<ROLE_PORT>' + reference + '\n'
            evidence.append({'test': test, 'reference': reference, 'port': int(port), 'startup': starts[0], 'shutdown': stops[0], 'raw_message': event['message']})
        normalized.append(row)
    assert len(ports) == 1
    key = lambda row: (row['test'], row['kind'], row.get('subtest') or '')
    return sorted(normalized, key=key), evidence


def compare(runtime, policy, original, candidate, signature):
    assert original['complete'] and candidate['complete']
    assert original['errors'] == candidate['errors'] == []
    assert original['comparison_errors'] == []
    assert candidate['comparison_errors'] == ['regression identities/status/expectations/intermittents changed']
    outputs = {}
    receipts = {}
    raw_signatures = {}
    pins = {}
    for role, assessment in [('original', original), ('candidate', candidate)]:
        assert len(assessment['rows']) + len(assessment['ends']) == 741
        assert len({(e['test'], e['action'], e.get('subtest') or '') for e in assessment['rows'] + assessment['ends']}) == 741
        phase = runtime / (role + '-wpt-regression')
        def read(path):
            data = path.read_bytes()
            pins[str(path)] = hashlib.sha256(data).hexdigest()
            return data
        manifest_data = read(phase / 'metadata/MANIFEST.json')
        assert hashlib.sha256(manifest_data).hexdigest() == policy['wpt_lanes']['regression']['manifests']['portable']['sha256']
        config = configparser.ConfigParser()
        config.read_string(read(phase / 'wptrunner.ini').decode())
        assert dict(config['manifest:upstream']) == {
            'tests': str(phase / 'tests'), 'metadata': str(phase / 'metadata'), 'url_base': '/', 'manifest': str(phase / 'metadata/MANIFEST.json')}
        command = json.loads(read(phase / 'COMMAND.json'))['command']
        assert [arg for arg in command if arg.startswith('--config=')] == ['--config=' + str(phase / 'wptrunner.ini')]
        events = [json.loads(line) for line in read(phase / 'raw.jsonl').decode().splitlines()]
        assert [e for e in events if e.get('action') == 'test_status'] == assessment['rows']
        assert [e for e in events if e.get('action') == 'test_end'] == assessment['ends']
        outputs[role], receipts[role] = normalize(events, assessment, json.loads(manifest_data), signature)
        raw_signatures[role] = { (e['test'], e['action'], e.get('subtest') or ''): signature(e) for e in assessment['rows'] + assessment['ends'] }
    before, after = raw_signatures['original'], raw_signatures['candidate']
    assert len(before) == len(after) == 741 and set(before) == set(after)
    changed = [key for key in before if before[key] != after[key]]
    assert set(changed) == {(test, 'test_end', '') for test in KNOWN}
    assert outputs['original'] == outputs['candidate']
    return {'derived_regression_gate': True, 'raw_signature_equality': False,
            'raw_exact_signatures': 737, 'port_bound_reftest_endings': 4,
            'corrected_equal_signatures': 741, 'role_port_evidence': receipts,
            'pins': pins, 'normalization': 'Only the two URL ports in each of four manifest-bound PASS reftest ending messages.',
            'raw_assessments_unchanged': True}
