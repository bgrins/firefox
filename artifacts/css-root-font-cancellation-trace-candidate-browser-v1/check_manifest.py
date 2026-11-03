import hashlib
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda body: hashlib.sha256(body).hexdigest()
manifest_bytes = (HERE / 'FILES.json').read_bytes()
manifest_sha = sha(manifest_bytes)
assert len(sys.argv) == 2 and sys.argv[1] == manifest_sha
manifest = json.loads(manifest_bytes)
policy = json.loads((HERE / 'POLICY.json').read_bytes())
actual = {str(path.relative_to(HERE)): path for path in HERE.rglob('*')
          if path.is_file() and path.name != 'FILES.json'}
assert set(manifest) == set(actual) and 'files' not in manifest
for name, path in actual.items():
    assert not path.is_symlink()
    assert manifest[name] == {'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size}
spec = importlib.util.spec_from_file_location('production_inputs', HERE / 'inputs.py')
inputs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inputs)
external = policy['intermediate_consumed_inputs']
consumed = inputs.bind_inputs(str(HERE.relative_to(ROOT)), manifest_bytes, manifest_sha, external)
expected = dict(external)
for name, record in manifest.items():
    path = str(HERE.relative_to(ROOT) / name)
    assert path not in expected
    expected[path] = record['sha256']
expected[str(HERE.relative_to(ROOT) / 'FILES.json')] = manifest_sha
assert consumed == expected
negatives = []
for label, value, digest in [
    ('original wrapper', {'files': manifest}, None),
    ('manifest self entry', dict(manifest, **{'FILES.json': {'sha256': manifest_sha}}), None),
    ('wrong manifest digest', manifest, '0' * 64),
]:
    body = json.dumps(value).encode()
    try:
        inputs.bind_inputs(str(HERE.relative_to(ROOT)), body, digest or sha(body), external)
    except (AssertionError, KeyError):
        negatives.append(label)
    else:
        raise AssertionError(label)
print(json.dumps({'manifest_sha256': manifest_sha, 'payloads': len(manifest),
                  'external_inputs': len(external), 'consumed_inputs': len(consumed),
                  'exact_production_bind_inputs': True, 'exact_owner_and_external_map': True,
                  'negative_controls': negatives, 'writes': False, 'live_operations': False}))
