import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bindings', HERE / 'bindings.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
encode = lambda value: (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
negative = []


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(value))


def reject(name, call):
    try:
        call()
    except AssertionError:
        negative.append(name)
    else:
        raise AssertionError(name)


with tempfile.TemporaryDirectory(prefix='css-log-bindings-check-', dir='/private/tmp') as temporary:
    root = Path(temporary).resolve()
    b.ROOT = root
    b.HERE = root / 'artifacts/template'
    b.RUNTIME = root / 'artifacts/css-registered-number-native-runtime-v1'
    source = 'servo/components/style/values/generics/calc.rs'
    prior = [source] + ['accepted/' + str(i) for i in range(28)]
    minmax_tests = ['testing/web-platform/tests/minmax1.html', 'testing/web-platform/tests/minmax2.html']
    pins, identities = {}, {}
    for i, name in enumerate(prior + minmax_tests):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(('payload' + str(i)).encode())
        pins[name] = b.sha(path.read_bytes())
        identities[name] = [path.stat().st_dev, path.stat().st_ino]
    held = root / 'servo/components/style/custom_properties.rs'
    held.parent.mkdir(parents=True, exist_ok=True)
    held.write_bytes(b'held')
    metadata = 'testing/web-platform/meta/exp-log-compute.html.ini'
    (root / metadata).parent.mkdir(parents=True, exist_ok=True)
    (root / metadata).write_bytes(b'old metadata')
    pins[metadata] = b.sha((root / metadata).read_bytes())
    absent = 'testing/web-platform/meta/old-absent.html.ini'
    pins[absent] = None
    original = {'accepted_current_payloads': {n: {'sha256': pins[n]} for n in prior}}
    old_path = root / 'artifacts/css-contextual-duration-masked-nine-original-v1/POLICY.json'
    write(old_path, original)
    policy = {'minmax_files': {n: pins[n] for n in [source] + minmax_tests},
              'source_path': source, 'files': {source: {}, 'testing/web-platform/tests/log.html': {}},
              'runtime_output': 'artifacts/log-output', 'held_provider_sha256': b.sha(b'held'),
              'deleted_metadata': {'path': metadata, 'sha256': pins[metadata]}}
    write(b.HERE / 'POLICY.json', policy)
    write(b.HERE / 'INPUTS.json', {str(old_path.relative_to(root)): b.sha(old_path.read_bytes())})
    epoch = {'semantic_index': {'head': 'actual-minmax'}, 'staged_working': {},
             'modified_native_paths': ['servo/components/style/custom_properties.rs'],
             'minmax_relative_infinity_transition': {'native_commit': 'actual-minmax'},
             'pins': pins, 'installed_identities': identities, 'preserved_snapshot': {'identity': 'old-app'},
             'counts': {'accepted': 149}, 'committed_research_working_payloads': {}}
    write(b.RUNTIME / 'CURRENT-EPOCH.json', epoch)
    write(b.RUNTIME / 'OWNED.json', {})
    write(b.RUNTIME / 'ROLE.json', {'role': 'native'})
    research = {'head': 'actual-research', 'committed': True, 'signature_verified': True,
                'native_working_diff_preserved': True, 'accepted_fix_increment': 0}
    minmax = {'commit': 'actual-minmax', 'parent': 'actual-research', 'signature_verified': True,
              'accepted': False, 'app_rebuilt': False, 'accepted_fix_increment': 0,
              'files': [source] + minmax_tests, 'epoch_sha256': b.sha((b.RUNTIME / 'CURRENT-EPOCH.json').read_bytes())}
    research_path, minmax_path = root / 'artifacts/research.json', root / 'artifacts/minmax.json'
    write(research_path, research)
    write(minmax_path, minmax)
    def extract():
        return b.extract(research_path, b.sha(research_path.read_bytes()), 'refs/heads/research', minmax_path, b.sha(minmax_path.read_bytes()))
    result = extract()
    assert len(result['preserved_claims']) == 31 and result['head'] == 'actual-minmax'
    assert result['historical_markers']['preserved_snapshot'] == epoch['preserved_snapshot']
    assert result['historical_markers']['minmax_relative_infinity_transition'] == epoch['minmax_relative_infinity_transition']
    assert result['absent_metadata'] == [absent]
    del epoch['pins'][metadata]
    write(b.RUNTIME / 'CURRENT-EPOCH.json', epoch)
    minmax['epoch_sha256'] = b.sha((b.RUNTIME / 'CURRENT-EPOCH.json').read_bytes())
    write(minmax_path, minmax)
    assert extract()['preserved_claims'] == result['preserved_claims']
    for bad_pin in ('wrong', None):
        epoch['pins'][metadata] = bad_pin
        write(b.RUNTIME / 'CURRENT-EPOCH.json', epoch)
        minmax['epoch_sha256'] = b.sha((b.RUNTIME / 'CURRENT-EPOCH.json').read_bytes())
        write(minmax_path, minmax)
        reject('present wrong metadata pin ' + repr(bad_pin), extract)
    epoch['pins'][metadata] = policy['deleted_metadata']['sha256']
    write(b.RUNTIME / 'CURRENT-EPOCH.json', epoch)
    minmax['epoch_sha256'] = b.sha((b.RUNTIME / 'CURRENT-EPOCH.json').read_bytes())
    write(minmax_path, minmax)
    for field, wrong in [('parent', 'wrong'), ('signature_verified', False), ('epoch_sha256', 'stale')]:
        altered = dict(minmax, **{field: wrong})
        write(minmax_path, altered)
        reject(field, extract)
    write(minmax_path, minmax)
    path = root / minmax_tests[0]
    original_body = path.read_bytes()
    path.write_bytes(b'wrong')
    reject('changed published MinMax test', extract)
    path.write_bytes(original_body)
    (root / absent).write_bytes(b'unexpected metadata')
    reject('lost historical metadata absence', extract)
    (root / absent).unlink()
    write(research_path, dict(research, committed=False))
    reject('failed research receipt', extract)
assert not root.exists()
print(json.dumps({'synthetic_31_claim_projection': True, 'historical_markers_preserved': True, 'missing_metadata_pin_positive': True,
                  'negative_checks': negative, 'scratch_removed': True, 'live_extraction': False}, indent=2))
