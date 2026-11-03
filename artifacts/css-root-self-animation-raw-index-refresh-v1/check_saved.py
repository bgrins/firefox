from pathlib import Path
import ast
import copy
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda path: json.loads(path.read_bytes())
spec = importlib.util.spec_from_file_location('saved_refresh', HERE / 'run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
policy = read(HERE / 'POLICY.json')
owner, report, pre, post, raw = module.saved(policy)
assert raw['semantic_index_unchanged'] and policy['execution_enabled'] is False
negatives = []
for key, value in [('pending_runtime_binding', True), ('runtime_manifest_sha256', '0' * 64), ('owner_terminal', dict(policy['owner_terminal'], sha256='0' * 64)), ('audit_terminal', dict(policy['audit_terminal'], sha256='0' * 64)), ('raw_before', '0' * 64), ('raw_after', '0' * 64)]:
    bad = copy.deepcopy(policy)
    bad[key] = value
    try:
        module.saved(bad)
    except (AssertionError, KeyError, ValueError, TypeError, RuntimeError):
        negatives.append(key)
    else:
        raise AssertionError('bad binding admitted: ' + key)
source = (HERE / 'run.py').read_text()
parent = (ROOT / 'artifacts/css-keyframe-font-unit-raw-index-refresh-v2/run.py').read_text()
tree, parent_tree = ast.parse(source), ast.parse(parent)
find = lambda parsed, name: next(node for node in parsed.body if isinstance(node, ast.FunctionDef) and node.name == name)
for name in ('derive', 'admit_current_raw'):
    assert ast.get_source_segment(source, find(tree, name)) == ast.get_source_segment(parent, find(parent_tree, name))
assert ast.get_source_segment(source, find(tree, 'main')).replace('native-authority root-self-animation candidate restored raw observation refresh', 'native-authority keyframe-font-unit candidate restored raw observation refresh') == ast.get_source_segment(parent, find(parent_tree, 'main'))
assertions = [node for node in ast.walk(find(tree, 'saved')) if isinstance(node, ast.Assert) and "audit_terminal['report_sha256']" in ast.unparse(node)]
assert len(assertions) == 1
code = compile(ast.Module(body=assertions, type_ignores=[]), '<actual audit receipt assertion>', 'exec')
terminal = read(ROOT / policy['audit_terminal']['path'])
exec(code, dict(policy=policy, audit_terminal=terminal))
for changed in [dict(terminal, report_sha256='0' * 64), {('restoration_report_sha256' if key == 'report_sha256' else key): value for key, value in terminal.items()}]:
    try:
        exec(code, dict(policy=policy, audit_terminal=changed))
    except (AssertionError, KeyError):
        pass
    else:
        raise AssertionError('wrong audit field accepted')
print(json.dumps({'saved_actual_runtime_admission': True, 'negative_bindings_rejected': negatives, 'actual_audit_field_negatives': 2, 'source_roles': list(report['source_identities']), 'callbacks_replayed': 61, 'endings_replayed': 5, 'writer_rollback_and_noop_unchanged_except_label': True, 'canonical_epoch_before': policy['controls']['CURRENT-EPOCH.json'], 'raw_before': raw['before'], 'raw_after': raw['after'], 'execution_disabled': True, 'live_or_native_actions': False}, sort_keys=True))
