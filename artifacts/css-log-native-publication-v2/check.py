import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace, ModuleType

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


p = load('publish')
d = load('delivery')
assert (HERE / 'run.py').read_bytes() == (ROOT / 'artifacts/css-log-native-publication-v1/run.py').read_bytes()
assert (HERE / 'POLICY.json').read_bytes() == (ROOT / 'artifacts/css-log-native-publication-v1/POLICY.json').read_bytes()
for name, pin in p.read(HERE / 'INPUTS.json').items():
    assert p.sha(ROOT / name) == pin
for f in HERE.glob('*.py'):
    compile(f.read_bytes(), str(f), 'exec')
policy = p.read(HERE / 'POLICY.json')
assert policy['bindings'] is None and policy['enabled_modes'] == []
negative = []


def reject(name, call):
    try:
        call()
    except (AssertionError, FileExistsError, FileNotFoundError):
        negative.append(name)
    else:
        raise AssertionError(name)


with tempfile.TemporaryDirectory(prefix='css-log-publication-check-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    p.ROOT = d.ROOT = scratch
    (scratch / 'artifacts').mkdir()
    p.HERE = scratch / 'artifacts/template'
    p.HERE.mkdir()
    (p.HERE / 'run.py').write_bytes((HERE / 'run.py').read_bytes())
    (p.HERE / 'evidence.py').write_bytes((HERE / 'evidence.py').read_bytes())
    records = {'run.py': {'sha256': p.sha(p.HERE / 'run.py'), 'bytes': (p.HERE / 'run.py').stat().st_size}}
    binding = {'head': 'actual-head', 'controls': {'CURRENT-EPOCH.json': 'actual-epoch'}, 'accepted_claims': {'calc': {'sha256': 'preimage'}}}
    bound = p.bind_owner(policy, binding, 'install', 'authenticated-template', records)
    assert bound['enabled_modes'] == ['install'] and bound['bindings'] == binding
    assert bound['files'] == policy['files'] and bound['message'] == policy['message']
    owner, pin = p.create_owner(bound, 'install')
    p.authenticate(owner, pin)
    driver_spec = importlib.util.spec_from_file_location('bound_log_driver', owner / 'run.py')
    driver = importlib.util.module_from_spec(driver_spec)
    driver_spec.loader.exec_module(driver)
    helper_path = str((owner / 'evidence.py').relative_to(scratch))
    helper = driver.load('bound_log_evidence', helper_path)
    assert helper.verify(ROOT, policy)['authored_log_passes'] == 24
    helper_body = (owner / 'evidence.py').read_bytes()
    (owner / 'evidence.py').unlink()
    reject('missing bound helper authentication', lambda: p.authenticate(owner, pin))
    reject('actual driver missing helper load', lambda: driver.load('missing_log_evidence', helper_path))
    (owner / 'evidence.py').write_bytes(helper_body)
    reject('duplicate install owner', lambda: p.create_owner(bound, 'install'))
    reject('wrong owner manifest', lambda: p.authenticate(owner, 'wrong'))
    body = (owner / 'POLICY.json').read_bytes()
    (owner / 'POLICY.json').write_bytes(body + b' ')
    reject('changed owner payload', lambda: p.authenticate(owner, pin))
    (owner / 'POLICY.json').write_bytes(body)
    tests = scratch / 'testing/web-platform/tests'
    (tests / 'tools/third_party').mkdir(parents=True)
    for name, record in policy['files'].items():
        if name == policy['source_path']:
            continue
        destination = scratch / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / record['capture']).read_bytes())
    output = scratch / policy['runtime_output']
    output.mkdir()
    calls = []
    def lint(command, **kwargs):
        assert command == policy['lint_command']
        calls.append(command)
        return SimpleNamespace(returncode=0)
    d.subprocess = SimpleNamespace(run=lint, STDOUT=-2)
    class Manifest:
        def __init__(self, path, url):
            assert path == str(tests) and url == '/'
        def update(self, paths, parallel):
            assert parallel is False
            self.paths = paths
        def to_json(self):
            entries = {}
            for name, absent, changed in self.paths:
                assert absent is None and changed is True
                body = (tests / name).read_bytes()
                blob = hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
                entries[Path(name).name] = [blob, [None, {}]]
            return {'items': {'testharness': {'css': {'css-values': entries}}}}
    fake = ModuleType('manifest.manifest')
    fake.Manifest = Manifest
    sys.modules['manifest.manifest'] = fake
    d.run(policy, pin)
    receipt = p.read(output / 'delivery/DELIVERY.json')
    assert receipt['installation_manifest'] == pin and len(receipt['files']) == 1
    assert receipt['deleted_metadata'] == {policy['deleted_metadata']['path']: policy['deleted_metadata']['sha256']} and receipt['metadata_absent_verified']
    assert receipt['lint_exit'] == receipt['lint_errors'] == 0 and not receipt['browser_executed']
    assert len(calls) == 1 and receipt['manifest_command'] == list(sys.orig_argv)
    for name, expected in receipt['evidence'].items():
        assert p.sha(scratch / name) == expected
    data = p.read(output / 'delivery/SUBSET-MANIFEST.json')
    wrong = copy.deepcopy(data)
    next(iter(wrong['items']['testharness']['css']['css-values'].values()))[0] = 'wrong'
    reject('wrong manifest blob', lambda: d.verify_entries(wrong, tests, receipt['files']))
    wrong = copy.deepcopy(data)
    next(iter(wrong['items']['testharness']['css']['css-values'].values()))[1][0] = '/wrong'
    reject('wrong default URL', lambda: d.verify_entries(wrong, tests, receipt['files']))
    wrong = copy.deepcopy(data)
    wrong['items']['testharness']['css']['css-values']['extra.html'] = ['extra', [None, {}]]
    reject('extra manifest test', lambda: d.verify_entries(wrong, tests, receipt['files']))
    reject('duplicate delivery output', lambda: d.run(policy, pin))
    failed_policy = copy.deepcopy(policy)
    failed_policy['runtime_output'] = 'artifacts/failed-lint'
    (scratch / failed_policy['runtime_output']).mkdir()
    d.subprocess = SimpleNamespace(run=lambda *a, **kw: SimpleNamespace(returncode=1), STDOUT=-2)
    reject('lint failure', lambda: d.run(failed_policy, pin))
    assert not (scratch / failed_policy['runtime_output'] / 'delivery/DELIVERY.json').exists()
assert not scratch.exists()
print(json.dumps({'exact_driver_and_policy': True, 'references': len(p.read(HERE / 'INPUTS.json')), 'mocked_bound_owner_and_delivery': True, 'negative_checks': negative, 'scratch_removed': True, 'native_git_browser_lint_manifest_executed': False}, indent=2))
