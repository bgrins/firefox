import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import textwrap

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
policy = read(HERE / 'POLICY.json')
assert not policy['execution_enabled'] and policy['pending_runtime_binding']
for key in ('actual_audit_terminal', 'actual_owner_terminal', 'audit_script', 'audit_terminal',
            'live_audit', 'owner_terminal', 'runtime_manifest_sha256', 'raw_after', 'outcome', 'archive_receipts'):
    assert policy[key] is None
for name, pin in policy['references'].items():
    assert sha(ROOT / name) == pin, name
parent = ROOT / 'artifacts/css-root-font-cancellation-raw-index-refresh-v1/run.py'
body, original = (HERE / 'run.py').read_text(), parent.read_text()
start = body.index("    archive = live['archive_observation']\n")
end = body.index("    assert sum(owner_policy['wpt_lanes'][lane]['expected_subtest_count']", start)
assert body[:start] + body[end:] == original
assert (HERE / 'RUN-DELTA.patch').read_text() == ''.join(difflib.unified_diff(
    original.splitlines(True), body.splitlines(True), fromfile=str(parent.relative_to(ROOT)),
    tofile=str((HERE / 'run.py').relative_to(ROOT))))
before, after = ast.parse(original), ast.parse(body)
for name in ('derive', 'admit_current_raw', 'main'):
    left = next(node for node in before.body if isinstance(node, ast.FunctionDef) and node.name == name)
    right = next(node for node in after.body if isinstance(node, ast.FunctionDef) and node.name == name)
    assert ast.get_source_segment(original, left) == ast.get_source_segment(body, right), name
spec = importlib.util.spec_from_file_location('pending_archive_refresh', HERE / 'run.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
try:
    module.saved(policy)
except AssertionError as error:
    assert str(error) == 'Completed paired runtime binding is pending'
else:
    raise AssertionError('pending runtime admitted')
actual_owner = read(ROOT / policy['owner']['directory'] / 'POLICY.json')
assert policy['controls'] == actual_owner['controls']
assert policy['refresh_parent'] == actual_owner['refresh_lineage']
assert sha(ROOT / policy['owner']['directory'] / 'FILES.json') == policy['owner']['manifest_sha256']
previous = ROOT / policy['refresh_parent']['directory']
assert sha(previous / 'RESULT.json') == policy['refresh_parent']['result_sha256']
epoch = read(previous / 'EPOCH.json')
assert sha(previous / 'EPOCH.json') == policy['controls']['CURRENT-EPOCH.json']
assert epoch['raw_index_observation']['current'] == policy['raw_before']
code = compile(textwrap.dedent(body[start:end]), '<actual saved archive receipt join>', 'exec')
rejects = []


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True))


with tempfile.TemporaryDirectory(prefix='css-archive-refresh-saved-', dir='/private/tmp') as scratch:
    runtime = Path(scratch)
    for name in ('candidate-build/RESULT.json', 'RESTORATION.json', 'POST.json',
                 'ARCHIVE-OWNERSHIP.json', 'ARCHIVE-VALIDATION.json'):
        write(runtime / name, {'synthetic_saved_record': name})
    write(runtime / 'ARCHIVE-SNAPSHOT.json', {'application': '/synthetic/application'})
    handoff = {'snapshot_sha256': sha(runtime / 'ARCHIVE-SNAPSHOT.json'),
               'restoration_sha256': sha(runtime / 'RESTORATION.json'),
               'post_sha256': sha(runtime / 'POST.json'), 'application': '/synthetic/application',
               'browser_execution_authorized': False, 'owner_terminal_and_independent_audit_required': True}
    write(runtime / 'ARCHIVE-HANDOFF.json', handoff)
    roles = {name: {'candidate_sha256': name} for name in ('data.rs', 'traversal.rs')}
    archive = {'status': 'verified-retained-candidate', 'archive_retained_verified': True,
               'owner_terminal_and_restoration_verified': True,
               'browser_execution_authorized': False, 'native_acceptance': False,
               'native_sources': {name: row['candidate_sha256'] for name, row in roles.items()},
               'build_receipt_sha256': sha(runtime / 'candidate-build/RESULT.json'),
               'receipt_hashes': {path.name: sha(path) for path in runtime.glob('ARCHIVE-*.json')},
               'application': '/synthetic/application'}

    def verify(value, rewrite_handoff=None):
        selected = copy.deepcopy(value)
        if rewrite_handoff is not None:
            write(runtime / 'ARCHIVE-HANDOFF.json', rewrite_handoff)
            selected['receipt_hashes']['ARCHIVE-HANDOFF.json'] = sha(runtime / 'ARCHIVE-HANDOFF.json')
        exec(code, dict(live={'archive_observation': selected}, roles=roles, runtime=runtime,
                        policy={'archive_receipts': selected['receipt_hashes']}, sha=sha, read=read))

    verify(archive)
    for key, value in [('status', 'failed-retained-untrusted'), ('archive_retained_verified', False),
                       ('owner_terminal_and_restoration_verified', False), ('browser_execution_authorized', True),
                       ('native_acceptance', True), ('native_sources', {}), ('build_receipt_sha256', 'bad'),
                       ('receipt_hashes', {})]:
        changed = copy.deepcopy(archive)
        changed[key] = value
        try:
            verify(changed)
        except AssertionError:
            rejects.append(key)
        else:
            raise AssertionError('accepted ' + key)
    for key in ('snapshot_sha256', 'restoration_sha256', 'post_sha256', 'application'):
        changed = dict(handoff, **{key: 'wrong'})
        try:
            verify(archive, changed)
        except AssertionError:
            rejects.append('handoff.' + key)
        else:
            raise AssertionError('accepted handoff.' + key)
    write(runtime / 'ARCHIVE-HANDOFF.json', handoff)
assert not Path(scratch).exists()
print(json.dumps({'references': len(policy['references']), 'only_saved_archive_join_changed': True,
                  'derive_admit_main_byte_identical': True, 'pending_admission_rejected': True,
                  'actual_previous_refresh_and_owner_controls_join': True,
                  'synthetic_archive_join_positive': True, 'archive_rejects': rejects,
                  'scratch': scratch, 'scratch_removed': True, 'live_operations': False,
                  'actual_future_runtime_replay': False, 'unchanged_suites_rerun': False}, indent=2))
