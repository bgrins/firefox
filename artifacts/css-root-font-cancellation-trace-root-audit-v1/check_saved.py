import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys


assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OWNER = ROOT/'artifacts/css-root-font-cancellation-trace-candidate-browser-v3'
RUNTIME = ROOT/'artifacts/css-root-font-cancellation-trace-candidate-browser-runtime-v1'
PARENT = ROOT/'artifacts/css-root-font-cancellation-archive-root-audit-v2'
read = lambda path: json.loads(path.read_bytes())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
binding = read(HERE/'BINDINGS.json')
assert binding['execution_enabled'] is False and binding['pending_owner_terminal'] is False
for path, pin in binding['references'].items():
    assert sha(ROOT/path) == pin, path
for name, origin in read(HERE/'ORIGINS.json').items():
    assert sha(ROOT/origin['path']) == origin['sha256']
    expected = ''.join(difflib.unified_diff((ROOT/origin['path']).read_text().splitlines(True), (HERE/name).read_text().splitlines(True), fromfile=origin['path'], tofile=str((HERE/name).relative_to(ROOT))))
    assert (HERE/(name+'.diff')).read_text() == expected
assert sha(OWNER/'FILES.json') == binding['owner_manifest_sha256']
policy, roles = read(OWNER/'POLICY.json'), read(OWNER/'SOURCE-ROLES.json')
capture = read(ROOT/policy['current_binding']['path'])
claims = capture['payload_claims'] | capture['additional_sources']
assert len(roles) == 5 and set(roles) <= set(claims)
tree = ast.parse((HERE/'audit.py').read_text())
start = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'terminal')
end = next(i for i in range(start, len(tree.body)) if isinstance(tree.body[i], ast.Assign) and ast.unparse(tree.body[i].targets[0]) == 'baseline')
terminal_nodes = [n for n in tree.body[start:end] if 'CANONICAL' not in ast.unparse(n)]
terminal_code = compile(ast.Module(body=terminal_nodes, type_ignores=[]), '<actual audit terminal joins, live lock check excluded>', 'exec')


def terminal_check(b, override=None):
    assert sha(RUNTIME/'RESULT.json') == b['result_sha256']
    assert sha(RUNTIME/'ROOT-OWNER-TERMINAL.json') == b['terminal_sha256']
    def saved_read(path):
        return override if override is not None and path == RUNTIME/'ROOT-OWNER-TERMINAL.json' else read(path)
    exec(terminal_code, dict(binding=b, RUNTIME=RUNTIME, sha=sha, read=saved_read))


terminal_check(binding)
archive_tree = ast.parse((HERE/'archive_audit.py').read_text())
function = next(n for n in archive_tree.body if isinstance(n, ast.FunctionDef) and n.name == 'verify_archive')
start = next(i for i,n in enumerate(function.body) if isinstance(n,ast.Assign) and ast.unparse(n.targets[0]) == 'build')
end = next(i for i in range(start,len(function.body)) if isinstance(function.body[i],ast.Assign) and ast.unparse(function.body[i].targets[0]) == 'owner_dir')
archive_code = compile(ast.Module(body=function.body[start:end], type_ignores=[]), '<actual saved archive build/source joins>', 'exec')
snapshot = read(RUNTIME/'ARCHIVE-SNAPSHOT.json')


def archive_check(s):
    exec(archive_code, dict(root=ROOT, runtime=RUNTIME, policy=policy, roles=roles, claims=claims, result=read(RUNTIME/'RESULT.json'), binding=binding, snapshot=s, read=read, sha=sha))


archive_check(snapshot)
assert binding['archive_records'] == {p.name:sha(p) for p in RUNTIME.glob('ARCHIVE-*.json')}
handoff = read(RUNTIME/'ARCHIVE-HANDOFF.json')
for field, name in [('snapshot_sha256','ARCHIVE-SNAPSHOT.json'),('restoration_sha256','RESTORATION.json'),('post_sha256','POST.json')]:
    assert handoff[field] == sha(RUNTIME/name)
post = read(RUNTIME/'POST.json')
raw = read(RUNTIME/'RAW-INDEX-OBSERVATION.json')
assert raw['before'] == capture['snapshot']['index']['raw_index']
assert raw['after'] == post['index']['raw_index']
normalized = copy.deepcopy(post)
normalized['index']['raw_index'] = raw['before']
assert json.dumps(normalized,sort_keys=True,allow_nan=False) == json.dumps(capture['snapshot'],sort_keys=True,allow_nan=False)
assert raw['canonical_updated'] is False and raw['semantic_index_unchanged'] is True
negative = []


def rejects(label, action):
    try:
        action()
    except (AssertionError, KeyError):
        negative.append(label)
    else:
        raise AssertionError('accepted: '+label)


terminal = read(RUNTIME/'ROOT-OWNER-TERMINAL.json')
for key in ('result_sha256','active_manifest','launch','session','terminal_chunk','outer_group'):
    changed = copy.deepcopy(terminal)
    changed[key] = None
    rejects('actual-terminal-'+key, lambda: terminal_check(binding, changed))
for key in ('result_sha256','terminal_sha256'):
    changed = copy.deepcopy(binding)
    changed[key] = '0'*64
    rejects('binding-'+key, lambda: terminal_check(changed))
for name in roles:
    changed = copy.deepcopy(snapshot)
    changed['native_sources'][name] = '0'*64
    rejects('five-role-build-join-'+name, lambda: archive_check(changed))
changed = copy.deepcopy(snapshot)
changed['source_claims']['layout/style/GeckoBindings.cpp'][2] += 1
rejects('canonical-source-identity', lambda: archive_check(changed))

source = (HERE/'audit.py').read_text()
parent_source = (PARENT/'audit.py').read_text()
owner_baseline = (OWNER/'baseline.py').read_text()
a = owner_baseline.index("    assert not state.h.git(ROOT, env, 'merge-base'",owner_baseline.index('def observe('))
b = owner_baseline.index('    metadata_guard(policy)',a)
git_block = '\n'.join(line[4:] if line.startswith('    ') else line for line in owner_baseline[a:b].splitlines())+'\n'
assert git_block in source
assert 'policy, ownership, roles = baseline.prepare(sha(OWNER / "FILES.json"))' in source
left = source.index("receipt_binding = capture['checkpoint_receipt']")
right = source.index('assert state.h.semantic_index(index)',left)
restored = source[:left] + source[right:]
terminal_addition = "assert terminal['active_manifest'] == binding['owner_manifest_sha256']\nassert terminal['launch'] == binding['launch'] and terminal['session'] == binding['session']\nassert terminal['terminal_chunk'] == binding['terminal_chunk']\nassert terminal['outer_group'] == binding['outer_group']\n"
assert terminal_addition in restored
restored = restored.replace(terminal_addition,'').replace(', "native_authority_freshly_verified": True','')
restored = restored.replace("assert set(roles) == {'servo/components/style/data.rs', 'servo/components/style/traversal.rs', 'servo/components/style/matching.rs', 'dom/animation/EffectCompositor.cpp', 'layout/style/GeckoBindings.cpp'}", "assert set(roles) == {'servo/components/style/data.rs', 'servo/components/style/traversal.rs'}")
restored = restored.replace('css-root-font-cancellation-trace-candidate-browser-v3','css-root-font-cancellation-archive-candidate-browser-v2').replace('css-root-font-cancellation-trace-candidate-browser-runtime-v1','css-root-font-cancellation-archive-candidate-browser-runtime-v1')
assert restored == parent_source
expected_archive = (PARENT/'archive_audit.py').read_text().replace('css-root-font-cancellation-archive-candidate-browser-v2','css-root-font-cancellation-trace-candidate-browser-v3').replace('css-root-font-cancellation-archive-candidate-browser-v1/archive.py','css-root-font-cancellation-trace-candidate-browser-v3/archive.py')
assert (HERE/'archive_audit.py').read_text() == expected_archive
print(json.dumps({'success':True,'references':len(binding['references']),'actual_owner':{'launch':terminal['launch'],'session':terminal['session'],'terminal':terminal['terminal_chunk'],'exit':terminal['exit']},'source_roles':len(roles),'archive_receipts':binding['archive_records'],'negative_controls':negative,'unchanged_independent_restoration_tail':True,'fresh_authority_operations_exact_from_executed_owner':True,'baseline_prepare_preserved':True,'live_audit_or_archive_inventory_executed':False,'tested_inputs':{n:sha(HERE/n) for n in ('audit.py','archive_audit.py','BINDINGS.json','ORIGINS.json','check_saved.py')}},indent=2,sort_keys=True))
