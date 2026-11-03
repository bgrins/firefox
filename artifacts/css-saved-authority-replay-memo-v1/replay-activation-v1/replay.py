import ast
import copy
import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
import types

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())
policy = read(HERE / 'POLICY.json')
assert policy['execution_enabled'] is True, 'saved replay remains disabled pending independent review'
assert len(sys.argv) == 2 and Path(sys.argv[1]).name == sys.argv[1]
output = HERE / sys.argv[1]
output.mkdir()
for path, pin in policy['references'].items():
    assert sha(ROOT / path) == pin, path


def source_module(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


memo = source_module('saved_memo', HERE / 'memo.py')
checker_path = ROOT / policy['checker']
checker = source_module('saved_checker', checker_path)
for name in ('copy', 'difflib', 'hashlib', 'importlib.util', 'json', 'os', 'pathlib',
             're', 'shutil', 'signal', 'stat', 'subprocess', 'sys', 'tempfile', 'urllib.parse'):
    importlib.import_module(name)
original = read(ROOT / policy['saved_policy'])
roles = read(checker.HERE / 'SOURCE-ROLES.json')
registry = read(HERE / 'FUNCTIONS.json')
assert len(registry) == 7
for path, record in registry.items():
    assert sha(ROOT / path) == record['sha256']
    assert sha(ROOT / record['bindings_path']) == record['bindings_sha256']
    assert record['function'] == 'validate_refresh'
forbidden = [ROOT / 'artifacts/css-registered-number-native-runtime-v1' / name
             for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json', 'SOURCE-TRANSITION.lock')]
scoped = {'policy': original, 'roles': roles}
session = memo.Session(ROOT, registry, scoped, [ROOT / 'artifacts'], forbidden)
start = time.monotonic()
try:
    with session:
        count = checker.validate_policy(original)
        assert checker.validate_policy(original) == count
        module = ast.parse(checker_path.read_text())
        main = next(node for node in module.body if isinstance(node, ast.If) and '__name__' in ast.unparse(node.test))
        mutations = next(node for node in main.body if isinstance(node, ast.Assign) and ast.unparse(node.targets[0]) == 'mutations')
        scope = dict(checker.__dict__, policy=original)
        exec(compile(ast.Module(body=[mutations], type_ignores=[]), '<exact mutation roster>', 'exec'), scope)
        assert len(scope['mutations']) == 11
        for key, value in scope['mutations']:
            bad = copy.deepcopy(original); bad[key] = value
            scoped['policy'] = bad
            checker.rejected(lambda: checker.validate_policy(bad))
        both = copy.deepcopy(original)
        both['execution_enabled'] = both['candidate_execution_enabled'] = True
        scoped['policy'] = both
        assert checker.validate_policy(both) == count
    start_index = next(i for i,node in enumerate(main.body) if isinstance(node,ast.Assign) and ast.unparse(node.targets[0])=='synthetic_policy')
    scope = dict(checker.__dict__, policy=original, count=count, mutations=scope['mutations'])
    exec(compile(ast.Module(body=main.body[start_index:], type_ignores=[]), '<exact remaining saved checks>', 'exec'), scope)
    result = {'success': True, 'consumed_inputs': count, 'binding_negatives': 11,
              'original_stream_stage_identity_tail_executed': True, 'calls': session.calls,
              'hits': session.hits, 'entries': len(session.table), 'seconds': time.monotonic()-start,
              'historical_modules_changed': False, 'native_or_browser_run': False,
              'live_guards_cached': False, 'scope': 'saved validation only; no deployment'}
except BaseException as error:
    result = {'success': False, 'error': repr(error), 'calls': session.calls, 'hits': session.hits,
              'seconds': time.monotonic()-start, 'native_or_browser_run': False}
    (output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    raise
(output/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))
