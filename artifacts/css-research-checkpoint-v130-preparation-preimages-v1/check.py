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
parent = HERE.with_name('css-research-checkpoint-20261103-v129')
old, new = (parent / 'commit.py').read_text(), (HERE / 'commit.py').read_text()
marker = 'def manifest_items('
assert old[old.index(marker):].replace('v129', 'v130').replace('V129', 'V130').replace(
    'No bug - Record cancellation publication recovery and tree settlement research.',
    'No bug - Record cancellation publication and subsequent validation research.') == new[new.index(marker):]
def functions(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
for name in ('git', 'load', 'verify_blob', 'verify_blobs'):
    assert functions(old)[name] == functions(new)[name]
old_capture, capture = (parent / 'capture_current.py').read_text(), (HERE / 'capture_current.py').read_text()
point = 'for path, digest in'
assert old_capture[old_capture.index(point):].replace("bindings['rollback_preservation']['controls']", "bindings['raw_observation']['controls']") == capture[capture.index(point):]
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
baseline = m.validate_native_raw_observation(receipt)
rejects = []
def reject(label, fn):
    try:
        fn()
    except (AssertionError, KeyError):
        rejects.append(label)
    else:
        raise AssertionError('Accepted mutation: ' + label)
for key, value in [('stage', 'font-units'), ('signature_verified', False), ('commit', '0'*40),
                   ('parent', '0'*40), ('epoch_sha256', '0'*64), ('files', []), ('accepted', True),
                   ('accepted_fix_increment', 1), ('app_rebuilt', True)]:
    bad = copy.deepcopy(receipt); bad[key] = value
    reject('receipt-' + key, lambda: m.validate_native_raw_observation(bad))
saved = b['raw_observation']
with tempfile.TemporaryDirectory(prefix='research-v130-saved-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    names = ('RESULT.json', 'ROOT-TERMINAL.json', 'CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json',
             'PRE-CURRENT-EPOCH.json', 'PRE-OWNED.json', 'PRE-ROLE.json', 'BEFORE.json', 'AFTER.json')
    for name in names:
        (scratch/name).write_bytes((ROOT/saved['directory']/name).read_bytes())
    test = copy.deepcopy(b); test['raw_observation']['directory'] = str(scratch)
    m.BINDINGS = test; local = test['raw_observation']
    assert m.validate_native_raw_observation(receipt) == baseline
    result = read(scratch/'RESULT.json'); terminal = read(scratch/'ROOT-TERMINAL.json')
    def set_terminal(value):
        body = json.dumps(value).encode(); (scratch/'ROOT-TERMINAL.json').write_bytes(body)
        local['terminal_sha256'], local['terminal'] = sha(body), value
    def set_result(value):
        body = json.dumps(value).encode(); (scratch/'RESULT.json').write_bytes(body)
        local['result_sha256'] = sha(body)
        changed = copy.deepcopy(terminal); changed['result_sha256'] = sha(body); set_terminal(changed)
    for key, value in [('updated_only', 'other'), ('head', '0'*40), ('semantic_index_unchanged', False),
                       ('full_current_state_verified', False), ('owned_and_role_unchanged', False),
                       ('native_fix_increment', 1), ('actual_raw_change_cause_unestablished', False),
                       ('old_epoch_sha256', '0'*64), ('epoch_sha256', '0'*64),
                       ('old_raw', '0'*64), ('new_raw', '0'*64)]:
        bad = copy.deepcopy(result); bad[key] = value; set_result(bad)
        reject('result-' + key, lambda: m.validate_native_raw_observation(receipt))
    set_result(result)
    for key, value in [('exit_code', 1), ('result_sha256', '0'*64)]:
        bad = copy.deepcopy(terminal); bad[key] = value; set_terminal(bad)
        reject('terminal-' + key, lambda: m.validate_native_raw_observation(receipt))
    set_result(result)
    for name in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'):
        original = (scratch/name).read_bytes(); (scratch/name).write_bytes(original+b' ')
        reject('control-' + name, lambda: m.validate_native_raw_observation(receipt))
        (scratch/name).write_bytes(original)
    before, after = (scratch/'BEFORE.json').read_bytes(), (scratch/'AFTER.json').read_bytes()
    for key, value in [('head', '0'*40), ('raw_index', '0'*64), ('working_diff', '')]:
        bad = json.loads(after); bad['index'][key] = value
        body = json.dumps(bad).encode()
        for name, field in [('BEFORE.json', 'before_sha256'), ('AFTER.json', 'after_sha256')]:
            (scratch/name).write_bytes(body); local[field] = sha(body)
        reject('snapshot-' + key, lambda: m.validate_native_raw_observation(receipt))
    (scratch/'BEFORE.json').write_bytes(before); local['before_sha256'] = sha(before)
    (scratch/'AFTER.json').write_bytes(after); local['after_sha256'] = sha(after)
    bad = json.loads(after); bad['current_raw_stable_during_check'] = 1
    body = json.dumps(bad).encode(); (scratch/'AFTER.json').write_bytes(body); local['after_sha256'] = sha(body)
    reject('typed-before-after-difference', lambda: m.validate_native_raw_observation(receipt))
    (scratch/'AFTER.json').write_bytes(after); local['after_sha256'] = sha(after)
    research = read(ROOT/b['prior_research_receipt'])
    test['prior_research_receipt'] = str(scratch/'research.json')
    for key, value in [('committed', False), ('signature_verified', False), ('head', '0'*40),
                       ('accepted_fix_increment', 1), ('native_working_diff_preserved', False)]:
        bad = copy.deepcopy(research); bad[key] = value
        body = json.dumps(bad).encode(); (scratch/'research.json').write_bytes(body)
        test['prior_research_receipt_sha256'] = sha(body)
        reject('research-' + key, lambda: m.validate_native_raw_observation(receipt))
    test['prior_research_receipt'] = b['prior_research_receipt']
    test['prior_research_receipt_sha256'] = b['prior_research_receipt_sha256']
    epoch = read(scratch/'CURRENT-EPOCH.json'); epoch['unexpected_nonraw_change'] = True
    body = json.dumps(epoch).encode(); (scratch/'CURRENT-EPOCH.json').write_bytes(body)
    m.EPOCH = sha(body); local['controls']['CURRENT-EPOCH.json'] = m.EPOCH
    bad = copy.deepcopy(result); bad['epoch_sha256'] = m.EPOCH; set_result(bad)
    reject('nonraw-epoch-change-even-with-rebound-digests', lambda: m.validate_native_raw_observation(receipt))
    m.BINDINGS, m.EPOCH = b, b['epoch_sha256']
assert not scratch.exists()
assert m.validate_native_raw_observation(receipt) == baseline
reject('pending-current', m.saved_admission)
sys.argv = [str(HERE/'commit.py'), '--run']
reject('disabled-run', m.main)
assert not (HERE/'result.json').exists()
print(json.dumps({'preparation_only': True, 'selected': len(selection), 'closures': len(b['completed_packages']),
                  'references': len(b['references']), 'authority_rejections': rejects,
                  'actual_native_and_raw_observation_positive': True, 'exact_signing_private_index_rollback_tail': True,
                  'capture_live_observer_preserved': True, 'immutable_git_objects_only': True,
                  'scratch_path': str(scratch), 'scratch_absent': True}))
