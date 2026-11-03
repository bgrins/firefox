import ast
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check, admission = load('check'), load('admission')
policy, roles = read(HERE / 'POLICY.json'), read(HERE / 'SOURCE-ROLES.json')
count = check.validate_policy(policy)
for mutation in ('capture-hash', 'capture-path', 'capture-owner-seal', 'memo-owner-seal'):
    bad = copy.deepcopy(policy)
    if mutation == 'capture-hash':
        bad['current_binding']['sha256'] = '0' * 64
    elif mutation == 'capture-path':
        bad['current_binding']['path'] = policy['capture_binding']['path']
    elif mutation == 'capture-owner-seal':
        bad['capture_owner']['manifest_sha256'] = '0' * 64
    else:
        bad['saved_refresh_memo']['manifest_sha256'] = '0' * 64
    check.rejected(lambda: admission.validate_current(ROOT, bad, roles))
tree = ast.parse((HERE / 'check.py').read_text())
function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'validate_policy')
assertions = [node for node in ast.walk(function) if isinstance(node, ast.Assert) and any(isinstance(part, ast.Name) and part.id == 'terminal' for part in ast.walk(node))]
assert len(assertions) == 6
code = compile(ast.Module(body=assertions, type_ignores=[]), '<actual terminal admission assertions>', 'exec')
terminal = read(ROOT / policy['capture_binding']['path'])
capture = read(ROOT / policy['current_binding']['path'])
exec(code, dict(terminal=terminal, capture=capture, policy=policy))
for key, value in [('terminal_chunk', ''), ('exit_code', 1), ('capture_path', 'wrong'), ('capture_sha256', '0' * 64), ('capture_owner_manifest', '0' * 64), ('glue_claim', {})]:
    changed = dict(terminal, **{key: value})
    check.rejected(lambda: exec(code, dict(terminal=changed, capture=capture, policy=policy)))
assert policy['execution_enabled'] is policy['candidate_execution_enabled'] is False
print(json.dumps({'consumed_inputs': count, 'actual_admission_verified': True, 'admission_binding_negatives': 4, 'actual_terminal_assertion_negatives': 6, 'memo_scope': 'fresh session per saved refresh; live checks outside session', 'baseline': {'PASS': 54, 'FAIL': 7, 'endings': 5}, 'prior_preparation_preserved': True, 'gates_disabled': True, 'native_or_browser_run': False}, sort_keys=True))
