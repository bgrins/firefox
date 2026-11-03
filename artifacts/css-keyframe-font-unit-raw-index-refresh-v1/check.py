import ast
import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location('refresh', HERE / 'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
p = m.read(HERE / 'POLICY.json')
assert p['pending_runtime_binding'] and not p['execution_enabled']
for key in ('owner', 'runtime', 'runtime_manifest_sha256', 'owner_terminal', 'actual_owner_terminal', 'audit_terminal', 'actual_audit_terminal', 'audit_script', 'live_audit', 'controls', 'raw_before', 'raw_after'):
    assert p[key] is None
try:
    m.saved(p)
except AssertionError as exc:
    assert str(exc) == 'Completed paired runtime binding is pending'
else:
    raise AssertionError('pending evidence admitted')
for name, pin in p['references'].items():
    assert m.sha(ROOT / name) == pin
parent = ROOT / 'artifacts/css-explicit-taint-combined-raw-index-refresh-v1/run.py'
def functions(path):
    source = path.read_text()
    return {n.name: ast.get_source_segment(source, n) for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)}
old, new = functions(parent), functions(HERE / 'run.py')
assert old.keys() == new.keys()
for name in ('load', 'derive', 'admit_current_raw'):
    assert old[name] == new[name]
assert old['main'].replace('native-authority combined-taint candidate restored raw observation refresh', 'native-authority keyframe-font-unit candidate restored raw observation refresh') == new['main']
epoch = {'semantic_index': {'head': 'synthetic-head', 'entries': 'same'}, 'raw_index_observation': {'current': 'before'}, 'sentinel': 'unchanged'}
pre = {'index': dict(epoch['semantic_index'], raw_index='before'), 'sources': {'unchanged': True}}
post = copy.deepcopy(pre); post['index']['raw_index'] = 'after'
raw = {'before': 'before', 'after': 'after', 'semantic_index_unchanged': True, 'canonical_updated': False}
updated = m.derive(epoch, pre, post, raw)
expected = copy.deepcopy(epoch); expected['raw_index_observation']['current'] = 'after'
assert updated == expected
bad = copy.deepcopy(post); bad['index']['entries'] = 'changed'
try:
    m.derive(epoch, pre, bad, raw)
except AssertionError:
    pass
else:
    raise AssertionError('semantic drift admitted')
actual = dict(post['index'], raw_index='fresh')
current, expected_post = m.admit_current_raw(updated, post, actual)
assert current['raw_index_observation']['current'] == expected_post['index']['raw_index'] == 'fresh'
source = (HERE / 'run.py').read_text()
start = source.index("    if actual_index['raw_index'] == epoch['raw_index_observation']['current']:")
end = source.index("    output = ROOT / policy['output']", start)
assert source.index('assert not lock.exists()') < start < source.index('output.mkdir()')
namespace = {'json': json, 'digest': m.digest}
exec('def branch(actual_index,epoch,policy,controls):\n' + source[start:end] + "    return 'write-required'\n", namespace)
with contextlib.redirect_stdout(io.StringIO()) as capture:
    assert namespace['branch']({'raw_index': 'same'}, {'raw_index_observation': {'current': 'same'}}, p, {'CURRENT-EPOCH.json': b'epoch'}) is None
assert json.loads(capture.getvalue())['updated'] is False
assert namespace['branch']({'raw_index': 'different'}, {'raw_index_observation': {'current': 'same'}}, p, {'CURRENT-EPOCH.json': b'epoch'}) == 'write-required'
print(json.dumps({'preparation_only': True, 'pending_runtime_rejected': True, 'derive_and_admit_exact': True, 'main_exact_except_label': True, 'synthetic_one_field_derivation': True, 'synthetic_semantic_change_rejected': True, 'exact_noop_branch_checked': True, 'actual_future_runtime_read': False, 'live_state_read': False, 'canonical_write': False}))
