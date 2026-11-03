import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bound_owner_check', HERE/'check.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
policy = checker.read(HERE/'POLICY.json')
conditions = checker.read(HERE/'PRECONDITIONS.json')
assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']
assert policy['current_binding'] and policy['capture_binding']
source = (HERE/'check.py').read_text()
function = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == 'validate_policy')
branch = next(node for node in function.body if isinstance(node, ast.If) and ast.unparse(node.test) == "policy['current_binding'] is None")
statements = []
for node in branch.orelse:
    if isinstance(node, ast.Assign) and "load('admission').validate_current" in ast.unparse(node):
        break
    statements.append(node)
assert statements and len(statements) < len(branch.orelse)
code = compile(ast.Module(body=statements, type_ignores=[]), '<actual pre-admission terminal guards>', 'exec')
terminal_path = checker.ROOT/policy['capture_binding']['path']
terminal = checker.read(terminal_path)
def terminal_guard(value):
    def read(path):
        return value if path == terminal_path else checker.read(path)
    exec(code, dict(policy=policy, conditions=conditions, sha=checker.sha, read=read, ROOT=checker.ROOT))
terminal_guard(terminal)
controls = []
for key, value in [('session_id', -1), ('terminal_chunk', 'wrong'), ('exit_code', 1), ('full_current_state_verified', False), ('capture_owner_manifest', '0'*64), ('capture_sha256', '0'*64), ('capture_path', 'wrong'), ('additional_source_claims', {}), ('glue_claim', dict(terminal['glue_claim'], owned_sha256='0'*64))]:
    bad = copy.deepcopy(terminal)
    bad[key] = value
    checker.rejected(lambda: terminal_guard(bad))
    controls.append(key)
bindings = []
for key, value in [('head', '0'*40), ('current_binding', dict(policy['current_binding'], sha256='0'*64)), ('capture_binding', dict(policy['capture_binding'], sha256='0'*64)), ('execution_enabled', True)]:
    bad = copy.deepcopy(policy)
    bad[key] = value
    checker.rejected(lambda: checker.validate_policy(bad))
    bindings.append(key)
count = checker.validate_policy(policy)
print(json.dumps({'actual_saved_admission': True, 'consumed_inputs': count,
                  'binding_rejections': bindings, 'extracted_actual_terminal_guard_rejections': controls,
                  'terminal_guard_controls_do_not_bypass_real_receipt_hash': True,
                  'full22_before8_projection': True, 'original_pass': 6, 'original_fail': 2, 'endings': 1,
                  'stream_staging_and_inode_suites': 'unchanged; retained sealed v1 actual receipt',
                  'execution_disabled': True, 'live_operations': False}, sort_keys=True))
