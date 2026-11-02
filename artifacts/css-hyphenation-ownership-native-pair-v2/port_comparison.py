import configparser
import hashlib
import importlib.util
import json


def compare(root, runtime, policy, original, candidate, signature):
    directory = root / policy['port_binding']['directory']
    assert hashlib.sha256((directory / 'FILES.json').read_bytes()).hexdigest() == policy['port_binding']['manifest_sha256']
    manifest = json.loads((directory / 'FILES.json').read_bytes())
    assert hashlib.sha256((directory / 'ports.py').read_bytes()).hexdigest() == manifest['ports.py']['sha256']
    spec = importlib.util.spec_from_file_location('sealed_nowrap_ports', directory / 'ports.py')
    ports = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ports)
    assert original['complete'] and candidate['complete']
    assert original['errors'] == candidate['errors'] == []
    assert original['comparison_errors'] == []
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
        outputs[role], receipts[role] = ports.normalize(events, assessment, json.loads(manifest_data), signature)
        raw_signatures[role] = { (e['test'], e['action'], e.get('subtest') or ''): signature(e) for e in assessment['rows'] + assessment['ends'] }
    key = lambda row: (row['test'], row['kind'], row.get('subtest') or '')
    before = {key(row): row for row in outputs['original']}
    after = {key(row): row for row in outputs['candidate']}
    assert set(before) == set(after) and len(before) == 741
    targets = {(page, 'test_status', name)
               for page, names in policy['wpt_lanes']['regression']['target_subtests'].items()
               for name in names}
    assert len(targets) == 289 and targets <= set(before)
    errors = [error for error in candidate['comparison_errors']
              if error != 'regression identities/status/expectations/intermittents changed']
    for identity, row in before.items():
        if (identity not in targets or row['status'] == 'PASS') and after[identity] != row:
            errors.append('preserved full signature changed: ' + str(identity))
    if any(after[identity]['status'] != 'PASS' for identity in targets):
        errors.append('ownership target did not pass')
    raw_before, raw_after = raw_signatures['original'], raw_signatures['candidate']
    changed = [key for key in raw_before if raw_before[key] != raw_after[key]]
    return {'derived_ownership_gate': not errors, 'errors': errors,
            'target_callbacks': 289, 'preserved_signatures': 452,
            'raw_changed_signatures': len(changed), 'port_bound_reftest_endings': 4,
            'role_port_evidence': receipts, 'pins': pins,
            'raw_assessments_unchanged': True, 'native_acceptance': False}
