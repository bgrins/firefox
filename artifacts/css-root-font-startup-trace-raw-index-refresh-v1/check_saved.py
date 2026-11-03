import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from collections import Counter


assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT/'artifacts/css-root-font-cancellation-selective-handoff-raw-index-refresh-v1'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
policy = read(HERE/'POLICY.json')
assert policy['execution_enabled'] is False and policy['pending_runtime_binding'] is False
for path, pin in policy['references'].items():
    assert sha(ROOT/path) == pin
spec = importlib.util.spec_from_file_location('bound_trace_refresh', HERE/'run.py')
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)
started = time.monotonic()
owner, report, pre, post, raw = driver.saved(policy)
elapsed = time.monotonic() - started
previous = ROOT/policy['refresh_parent']['directory']
assert sha(previous/'RESULT.json') == policy['refresh_parent']['result_sha256']
assert sha(previous/'EPOCH.json') == policy['controls']['CURRENT-EPOCH.json']
epoch = read(previous/'EPOCH.json')
updated = driver.derive(epoch, pre['snapshot'], post, raw)
normalized = copy.deepcopy(updated)
normalized['raw_index_observation']['current'] = raw['before']
assert json.dumps(normalized,sort_keys=True,allow_nan=False) == json.dumps(epoch,sort_keys=True,allow_nan=False)
source, parent_source = (HERE/'run.py').read_text(), (PARENT/'run.py').read_text()
tree, old_tree = ast.parse(source), ast.parse(parent_source)
for name in ('derive','admit_current_raw'):
    current = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == name)
    old = next(n for n in old_tree.body if isinstance(n,ast.FunctionDef) and n.name == name)
    assert ast.get_source_segment(source,current) == ast.get_source_segment(parent_source,old)
current_main = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'main')
old_main = next(n for n in old_tree.body if isinstance(n,ast.FunctionDef) and n.name == 'main')
assert ast.get_source_segment(source,current_main) == ast.get_source_segment(parent_source,old_main).replace('native-authority four-source selective handoff restored raw observation refresh','native-authority eight-source startup trace restored raw observation refresh')
negative = []


def rejects(label, action):
    try:
        action()
    except (AssertionError, KeyError, RuntimeError, ValueError):
        negative.append(label)
    else:
        raise AssertionError('accepted '+label)


for key, value in (
    ('pending_runtime_binding',True),
    ('runtime_manifest_sha256','0'*64),
    ('owner',dict(policy['owner'],manifest_sha256='0'*64)),
    ('owner_terminal',dict(policy['owner_terminal'],sha256='0'*64)),
    ('live_audit',dict(policy['live_audit'],sha256='0'*64)),
    ('audit_terminal',dict(policy['audit_terminal'],sha256='0'*64)),
    ('direct_equivalence',dict(policy['direct_equivalence'],manifest_sha256='0'*64)),
    ('archive_receipts',dict(policy['archive_receipts'], **{'ARCHIVE-HANDOFF.json':'0'*64})),
):
    changed = copy.deepcopy(policy)
    changed[key] = value
    rejects('binding-'+key, lambda: driver.saved(changed))
for label in ('canonical-already-updated','wrong-before','nonraw-post-change'):
    changed_raw, changed_post = copy.deepcopy(raw), copy.deepcopy(post)
    if label == 'canonical-already-updated': changed_raw['canonical_updated'] = True
    elif label == 'wrong-before': changed_raw['before'] = '0'*64
    else: changed_post['nested_index']['entries'] = '0'*64
    rejects(label, lambda: driver.derive(epoch,pre['snapshot'],changed_post,changed_raw))
bad_index = copy.deepcopy(post['index'])
bad_index['head'] = '0'*40
rejects('live-admission-semantic-change', lambda: driver.admit_current_raw(updated,post,bad_index))
actual_index = copy.deepcopy(post['index'])
actual_index['raw_index'] = 'a'*64
admitted, expected = driver.admit_current_raw(updated,post,actual_index)
assert admitted['raw_index_observation']['current'] == expected['index']['raw_index'] == actual_index['raw_index']
saved_function = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == 'saved')
field_guard = next(n for n in saved_function.body if isinstance(n,ast.Assert) and "audit_terminal['report_sha256']" in ast.unparse(n))
field_code = compile(ast.Module(body=[field_guard],type_ignores=[]),'<actual report_sha256 join>','exec')
actual_terminal = read(ROOT/policy['audit_terminal']['path'])
exec(field_code,dict(audit_terminal=actual_terminal,policy=policy))
aliased = copy.deepcopy(actual_terminal)
aliased['restoration_report_sha256'] = aliased.pop('report_sha256')
rejects('wrong-audit-field-alias', lambda: exec(field_code,dict(audit_terminal=aliased,policy=policy)))
for actual_key, wrong_alias in (('terminal_chunk','terminal'), ('active_audit_manifest','active_audit_manifest_sha256')):
    guard = next(n for n in saved_function.body if isinstance(n,ast.Assert) and ("audit_terminal['" + actual_key + "']") in ast.unparse(n))
    code = compile(ast.Module(body=[guard],type_ignores=[]),'<actual audit field join>','exec')
    scope = dict(audit_terminal=actual_terminal,policy=policy,ROOT=ROOT,sha=sha)
    exec(code,scope)
    bad = copy.deepcopy(actual_terminal);bad[wrong_alias] = bad.pop(actual_key)
    rejects('wrong-audit-alias-'+wrong_alias,lambda:exec(code,dict(scope,audit_terminal=bad)))
manifest_guard = next(n for n in saved_function.body if isinstance(n,ast.Assert) and 'runtime_manifest and' in ast.unparse(n))
manifest_code = compile(ast.Module(body=[manifest_guard],type_ignores=[]),'<actual flat runtime manifest>','exec')
runtime = ROOT/policy['runtime']
actual_manifest = read(runtime/'FILES.json')
exec(manifest_code,dict(runtime_manifest=actual_manifest))
rejects('wrapped-runtime-manifest',lambda:exec(manifest_code,dict(runtime_manifest={'files':actual_manifest,'verified_staging_tool_links':[]})))
rejects('runtime-manifest-extra-record-field',lambda:exec(manifest_code,dict(runtime_manifest={'x':dict(next(iter(actual_manifest.values())),unexpected=True)})))
assessment = read(runtime/'candidate-wpt-cancellation/ASSESSMENT.json')
print(json.dumps({
    'success':True,'actual_saved_runtime_replay':True,'saved_seconds':elapsed,
    'references':len(policy['references']),'source_roles':len(report['source_identities']),
    'callbacks':len(assessment['rows']),'counts':dict(Counter(r['status'] for r in assessment['rows'])),'endings':len(assessment['ends']),
    'runtime_manifest_sha256':policy['runtime_manifest_sha256'],'audit_sha256':policy['live_audit']['sha256'],
    'archive_receipts':policy['archive_receipts'],'raw':raw,
    'derive_and_admit_unchanged':True,'main_transaction_only_label_changed':True,
    'whole_epoch_unchanged_except_one_raw_field':True,'actual_raw_admission_positive':True,
    'negative_controls':negative,'execution_enabled':False,'live_main_executed':False,
    'tested_inputs':{n:sha(HERE/n) for n in ('run.py','POLICY.json','check_saved.py')},
},indent=2,sort_keys=True))
