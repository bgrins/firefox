import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())
spec = importlib.util.spec_from_file_location('checkpoint', HERE / 'commit.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
b = m.BINDINGS
assert not m.EXECUTION_ENABLED and b['pending_current_admission']
assert b['current_capture_sha256'] is None and b['controls'] == {}
for path, digest in b['references'].items():
    assert sha((ROOT / path).read_bytes()) == digest, path
selection = read(HERE / 'SELECTION.json')
assert sha((HERE / 'SELECTION.json').read_bytes()) == b['selection_sha256']
assert len(selection) == b['selected_paths_before_self']
for path, row in selection.items():
    f = ROOT / path
    assert path.startswith('artifacts/') and '..' not in Path(path).parts
    assert f.is_file() and not f.is_symlink()
    assert sha(f.read_bytes()) == row['sha256'] and f.stat().st_size == row['bytes']
for path, digest in b['completed_packages'].items():
    assert sha((ROOT / path).read_bytes()) == digest == selection[path]['sha256']
    for name, row in m.manifest_items(read(ROOT / path)):
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert selection[str(Path(path).parent / name)]['sha256'] == (row['sha256'] if isinstance(row, dict) else row)
nested = read(HERE / 'NESTED-DEPENDENCIES.json')
assert len(nested['files']) == 25 and not set(nested['files']).intersection(selection)
assert nested['head'] == '162b20fb7c53a0ab89b20875a965baee98fb66bb'
for path, row in nested['files'].items():
    assert b['references'][path] == row['sha256'] == sha((ROOT / path).read_bytes())
    assert not any(Path(path).is_relative_to(Path(item).parent) for item in b['completed_packages'])
parent = HERE.with_name('css-research-checkpoint-20261103-v130')
old, new = (parent / 'commit.py').read_text(), (HERE / 'commit.py').read_text()
marker = 'def manifest_items('
assert old[old.index(marker):].replace('v130', 'v131').replace('V130', 'V131').replace(
    'No bug - Record cancellation publication and subsequent validation research.',
    'No bug - Record typed attribute taint publication and fallback research.') == new[new.index(marker):]
def functions(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
for name in ('git', 'load', 'verify_blob', 'verify_blobs'):
    assert functions(old)[name] == functions(new)[name]
old_capture, capture = (parent / 'capture_current.py').read_text(), (HERE / 'capture_current.py').read_text()
point = 'for path, digest in'
assert old_capture[old_capture.index(point):].replace("bindings['raw_observation']['controls']", "bindings['native_observation']['controls']") == capture[capture.index(point):]
for name in ('commit.py', 'capture_current.py', 'check.py'):
    compile((HERE / name).read_bytes(), name, 'exec')
git = lambda *a: subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', *a], cwd=ROOT)
assert git('rev-list', '--parents', '-n', '1', b['head']).decode().split() == [b['head'], b['native_parent']]
assert git('diff-tree', '--no-commit-id', '--name-only', '-r', b['head']).decode().splitlines() == list(b['native_files'])
tracked = set(git('ls-tree', '-r', '--name-only', '-z', b['head'], '--', 'artifacts').decode().split('\0'))
assert not tracked.intersection(selection)
for path, row in read(HERE / 'INVENTORY.json')['excluded_already_committed_exact_blobs'].items():
    assert path in tracked and path not in selection
    body = git('show', b['head'] + ':' + path)
    assert len(body) == row['bytes'] and sha(body) == row['sha256'] == sha((ROOT / path).read_bytes())
for path, digest in b['native_files'].items():
    assert sha(git('show', b['head'] + ':' + path)) == digest
receipt = read(ROOT / b['prior_receipt'])
baseline = m.validate_native_publication(receipt)
rejects = []
def reject(label, fn):
    try:
        fn()
    except (AssertionError, KeyError):
        rejects.append(label)
    else:
        raise AssertionError('Accepted mutation: ' + label)
for key, value in [('stage', 'selective-cancellation'), ('signature_verified', False), ('commit', '0'*40),
                   ('parent', '0'*40), ('epoch_sha256', '0'*64), ('files', []), ('accepted', True),
                   ('accepted_fix_increment', 1), ('app_rebuilt', True)]:
    bad = copy.deepcopy(receipt); bad[key] = value
    reject('receipt-' + key, lambda: m.validate_native_publication(bad))
saved = b['native_observation']
with tempfile.TemporaryDirectory(prefix='research-v131-saved-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    names = ('RESULT.json', 'ROOT-TERMINAL.json', 'CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json', 'SNAPSHOT.json')
    for name in names:
        (scratch/name).write_bytes((ROOT/saved['directory']/name).read_bytes())
    originals = {name:(scratch/name).read_bytes() for name in names}
    test = copy.deepcopy(b); test['native_observation']['directory'] = str(scratch)
    m.BINDINGS = test; local = test['native_observation']
    assert m.validate_native_publication(receipt) == baseline
    result = read(scratch/'RESULT.json'); terminal = read(scratch/'ROOT-TERMINAL.json')
    def set_terminal(value):
        body = json.dumps(value).encode(); (scratch/'ROOT-TERMINAL.json').write_bytes(body)
        local['terminal_sha256'], local['terminal'] = sha(body), value
    def set_result(value):
        body = json.dumps(value).encode(); (scratch/'RESULT.json').write_bytes(body)
        local['result_sha256'] = sha(body)
        changed = copy.deepcopy(terminal); changed['result_sha256'] = sha(body); set_terminal(changed)
    def restore():
        for name, body in originals.items(): (scratch/name).write_bytes(body)
        local.clear(); local.update(copy.deepcopy(saved)); local['directory'] = str(scratch)
        m.EPOCH = b['epoch_sha256']
    for key, value in [('head', '0'*40), ('full_current_state_verified', False),
                       ('source_transition_lock_absent', False), ('snapshot_sha256', '0'*64), ('controls', {})]:
        bad = copy.deepcopy(result); bad[key] = value; set_result(bad)
        reject('result-' + key, lambda: m.validate_native_publication(receipt))
    restore()
    for key, value in [('exit_code', 1), ('result_sha256', '0'*64)]:
        bad = copy.deepcopy(terminal); bad[key] = value; set_terminal(bad)
        reject('terminal-' + key, lambda: m.validate_native_publication(receipt))
    restore()
    for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'):
        (scratch/name).write_bytes(originals[name]+b' ')
        reject('control-' + name, lambda: m.validate_native_publication(receipt)); restore()
    snapshot = json.loads(originals['SNAPSHOT.json'])
    for field, value in [('head', '0'*40), ('raw_index', '0'*64), ('cached_diff', ''), ('working_diff', sha(b'dirty')),
                         ('current_raw_stable_during_check', 1), ('working_sources_binaries_research_preserved', False)]:
        bad = copy.deepcopy(snapshot)
        if field in bad['index']: bad['index'][field] = value
        else: bad[field] = value
        body = json.dumps(bad).encode(); (scratch/'SNAPSHOT.json').write_bytes(body)
        local['snapshot_sha256'] = sha(body); changed = copy.deepcopy(result); changed['snapshot_sha256'] = sha(body); set_result(changed)
        reject('snapshot-' + field, lambda: m.validate_native_publication(receipt)); restore()
    for field, value in [('committed', False), ('signature_verified', False), ('head', '0'*40),
                         ('accepted_fix_increment', 1), ('native_working_diff_preserved', False)]:
        research = read(ROOT/b['prior_research_receipt']); research[field] = value
        body = json.dumps(research).encode(); (scratch/'research.json').write_bytes(body)
        test['prior_research_receipt'] = str(scratch/'research.json'); test['prior_research_receipt_sha256'] = sha(body)
        reject('research-' + field, lambda: m.validate_native_publication(receipt))
    test['prior_research_receipt'] = b['prior_research_receipt']; test['prior_research_receipt_sha256'] = b['prior_research_receipt_sha256']
    def set_control(name, value):
        body = json.dumps(value).encode(); (scratch/name).write_bytes(body)
        local['controls'][name] = sha(body)
        changed = copy.deepcopy(result); changed['controls'] = copy.deepcopy(local['controls']); set_result(changed)
    for field, value in [('built', True), ('variant', 'fallback'), ('paired_head', '0'*40)]:
        bad = json.loads(originals['ROLE.json']); bad[field] = value; set_control('ROLE.json', bad)
        reject('role-' + field, lambda: m.validate_native_publication(receipt)); restore()
    source = 'servo/components/style/custom_properties.rs'
    bad = json.loads(originals['OWNED.json']); bad[source]['identity'][1] += 1; set_control('OWNED.json', bad)
    reject('owned-identity', lambda: m.validate_native_publication(receipt)); restore()
    for field, value in [('native_commit', '0'*40), ('files', {}), ('accepted', True), ('compiled', True), ('current_app_contains_candidate', True)]:
        bad = json.loads(originals['CURRENT-EPOCH.json']); bad['explicit_taint_reparse_publication']['reparse'][field] = value
        set_control('CURRENT-EPOCH.json', bad); m.EPOCH = local['controls']['CURRENT-EPOCH.json']
        fake = dict(receipt, epoch_sha256=m.EPOCH)
        reject('publication-' + field, lambda: m.validate_native_publication(fake)); restore()
    for field, value in [('staged_working', {'unexpected':'0'*64}), ('modified_native_paths', [source])]:
        bad = json.loads(originals['CURRENT-EPOCH.json']); bad[field] = value
        set_control('CURRENT-EPOCH.json', bad); m.EPOCH = local['controls']['CURRENT-EPOCH.json']
        fake = dict(receipt, epoch_sha256=m.EPOCH)
        reject('epoch-' + field, lambda: m.validate_native_publication(fake)); restore()
    m.BINDINGS, m.EPOCH = b, b['epoch_sha256']
assert not scratch.exists()
assert m.validate_native_publication(receipt) == baseline
reject('pending-current', m.saved_admission)
sys.argv = [str(HERE/'commit.py'), '--run']
reject('disabled-run', m.main)
assert not (HERE/'result.json').exists()
print(json.dumps({'preparation_only': True, 'selected': len(selection), 'closures': len(b['completed_packages']),
                  'references': len(b['references']), 'authority_rejections': rejects,
                  'actual_native_and_postcommit_observation_positive': True, 'raw_refresh_assumed': False,
                  'exact_signing_private_index_rollback_tail': True,
                  'capture_live_observer_preserved': True, 'immutable_git_objects_only': True,
                  'scratch_path': str(scratch), 'scratch_absent': True}))
