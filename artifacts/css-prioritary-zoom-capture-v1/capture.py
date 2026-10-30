import hashlib
import json
from pathlib import Path
import secrets

HERE = Path(__file__).resolve().parent
PAGE = '/css/css-properties-values-api/registered-prioritary-selection.tentative.html'
NAME = 'Prioritary selection preservation: zoom-observation'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def install(tests, output, role):
    assert role in {'original', 'candidate'}
    tests, output = Path(tests), Path(output)
    assert tests.resolve() == output.resolve() / 'tests'
    assert sha(tests / PAGE[1:]) == sha(HERE / 'candidate.html')
    directory = tests / '__research__/zoom'
    directory.mkdir(parents=True)
    for name in ['record.js', 'receive.py']:
        (directory / name).write_bytes((HERE / name).read_bytes())
    config = {'version': 1, 'nonce': secrets.token_hex(24), 'role': role, 'page': PAGE}
    save(directory / 'CONFIG.json', config)
    binding = dict(config, resources={name: sha(directory / name)
                   for name in ['record.js', 'receive.py', 'CONFIG.json']},
                   page_sha256=sha(tests / PAGE[1:]))
    save(output / 'ZOOM-BINDING.json', binding)
    return binding


def validate(payload, binding):
    assert set(payload) == {'version', 'nonce', 'role', 'page', 'row'}
    assert all(payload[k] == binding[k] for k in ['version', 'nonce', 'role', 'page'])
    row = payload['row']
    assert set(row) == {'kind', 'initial', 'phases', 'diagnosticOnly'}
    assert row['kind'] == 'zoom-observation' and row['diagnosticOnly'] is True
    assert isinstance(row['initial'], str) and len(row['initial']) < 1000
    assert isinstance(row['phases'], list) and len(row['phases']) == 2
    keys = {'phase', 'value', 'samples', 'expected', 'expectedFont', 'font', 'line', 'family',
            'writingMode', 'zoom', 'referenceFont', 'referenceWidth', 'size',
            'keywordSupported', 'zoomSyntaxSupported'}
    for index, phase in enumerate(row['phases']):
        assert set(phase) == keys and type(phase['phase']) is int and phase['phase'] == index
        assert phase['value'] == '1em' and phase['size'] == [20, 30][index]
        assert phase['expected'] is None and phase['expectedFont'] is None
        assert type(phase['keywordSupported']) is bool and type(phase['zoomSyntaxSupported']) is bool
        assert isinstance(phase['samples'], list) and len(phase['samples']) == 4
        for value in phase['samples'] + [phase[k] for k in ['font', 'line', 'family', 'writingMode',
                                                           'zoom', 'referenceFont', 'referenceWidth']]:
            assert isinstance(value, str) and len(value) < 1000
    return row


def replay(output, events):
    output = Path(output)
    directory = output / 'tests/__research__/zoom'
    binding = json.loads((output / 'ZOOM-BINDING.json').read_bytes())
    assert not (directory / 'ERRORS.jsonl').exists()
    assert all(sha(directory / name) == digest for name, digest in binding['resources'].items())
    assert sha(output / 'tests' / PAGE[1:]) == binding['page_sha256'] == sha(HERE / 'candidate.html')
    assert binding['resources']['record.js'] == sha(HERE / 'record.js')
    assert binding['resources']['receive.py'] == sha(HERE / 'receive.py')
    assert json.loads((directory / 'CONFIG.json').read_bytes()) == {k: binding[k] for k in ['version', 'nonce', 'role', 'page']}
    payload = json.loads((directory / 'REQUEST.json').read_bytes())
    row = validate(payload, binding)
    statuses = [e for e in events if e.get('action') == 'test_status' and e.get('test') == PAGE and e.get('subtest') == NAME]
    endings = [e for e in events if e.get('action') == 'test_end' and e.get('test') == PAGE]
    assert len(statuses) == len(endings) == 1
    result = {'role': binding['role'], 'page': binding['page'], 'request_sha256': sha(directory / 'REQUEST.json'), 'binding_sha256': sha(output / 'ZOOM-BINDING.json'),
              'row': row, 'test_status': statuses[0], 'test_end': endings[0],
              'capture_complete': True, 'target_correctness': None}
    return result


def review(output, events):
    result = replay(output, events)
    save(Path(output) / 'ZOOM-OBSERVATION.json', result)
    return result


def compare(original, candidate):
    assert original['role'] == 'original' and candidate['role'] == 'candidate'
    assert original['page'] == candidate['page'] == PAGE
    left, right = original['row'], candidate['row']
    assert original['capture_complete'] and candidate['capture_complete']
    differences = []
    if left['initial'] != right['initial']:
        differences.append({'field': 'initial', 'original': left['initial'], 'candidate': right['initial']})
    for index, (a, b) in enumerate(zip(left['phases'], right['phases'])):
        for key in a:
            if a[key] != b[key]:
                differences.append({'phase': index, 'field': key, 'original': a[key], 'candidate': b[key]})
    return {'rows_equal': left == right, 'differences': differences, 'target_correctness': None}
