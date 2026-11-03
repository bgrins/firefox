import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
policy = json.loads((HERE / 'POLICY.json').read_bytes())
spec = importlib.util.spec_from_file_location('identity_ownership', ROOT / policy['ownership_helper'])
ownership = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ownership)
tree = ast.parse((HERE / 'run.py').read_text())
main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
loop = next(node for node in main.body if isinstance(node, ast.For) and ast.unparse(node.iter) == 'roles.items()')
start = next(i for i, node in enumerate(loop.body) if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 'admitted')
code = compile(ast.Module(body=loop.body[start:start + 3], type_ignores=[]), '<actual driver ownership claim>', 'exec')
with tempfile.TemporaryDirectory(prefix='caller-identity-', dir='/private/tmp') as scratch:
    root = Path(scratch)
    for name in json.loads((HERE / 'SOURCE-ROLES.json').read_bytes()):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'unchanged source')
        pin = hashlib.sha256(path.read_bytes()).hexdigest()
        admitted = ownership.claim(root, name, pin)
        capture = {'payload_claims': {name: admitted}, 'additional_sources': {}}
        scope = dict(ROOT=root, name=name, record={'base_sha256': pin}, ownership=ownership,
                     claims={}, baseline=SimpleNamespace(current_capture=lambda _: capture), policy={})
        exec(code, scope)
        assert scope['claims'][name] == admitted
        path.rename(path.with_suffix('.retained'))
        path.write_bytes(b'unchanged source')
        assert ownership.claim(root, name, pin)['identity'] != admitted['identity']
        try:
            exec(code, scope)
        except Exception as error:
            assert 'owned identity: ' + name in str(error), str(error)
        else:
            raise AssertionError('Identical bytes with replaced inode accepted')
assert not root.exists()
print(json.dumps({'actual_driver_claim_extracted': True, 'captured_identity_positive': True,
                  'identical_bytes_changed_inode_rejected': True, 'scratch_removed': True}))
