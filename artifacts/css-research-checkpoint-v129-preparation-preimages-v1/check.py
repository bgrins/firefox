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
parent = HERE.with_name('css-research-checkpoint-20261103-v128')
old, new = (parent / 'commit.py').read_text(), (HERE / 'commit.py').read_text()
marker = 'def manifest_items('
assert old[old.index(marker):].replace('v128', 'v129').replace('V128', 'V129').replace(
    'No bug - Record font publication and animation settlement research.',
    'No bug - Record cancellation publication recovery and tree settlement research.') == new[new.index(marker):]
def functions(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
for name in ('git', 'load', 'verify_blob', 'verify_blobs'):
    assert functions(old)[name] == functions(new)[name]
old_capture, capture = (parent / 'capture_current.py').read_text(), (HERE / 'capture_current.py').read_text()
point = 'for path, digest in'
assert old_capture[old_capture.index(point):].replace("bindings['native_preservation']['controls']", "bindings['rollback_preservation']['controls']") == capture[capture.index(point):]
for name in ('commit.py', 'capture_current.py', 'check.py'):
    compile((HERE / name).read_bytes(), name, 'exec')
git = lambda *a: subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', *a], cwd=ROOT)
assert git('rev-list', '--parents', '-n', '1', b['head']).decode().split() == [b['head'], b['native_head']]
assert all(p.startswith('artifacts/') for p in git('diff', '--name-only', b['native_head'], b['head']).decode().splitlines())
tracked = set(git('ls-tree', '-r', '--name-only', '-z', b['head'], '--', 'artifacts').decode().split('\0'))
assert not tracked.intersection(selection)
for path, row in read(HERE / 'INVENTORY.json')['excluded_already_committed_exact_blobs'].items():
    assert path in tracked and path not in selection
    body = git('show', b['head'] + ':' + path)
    assert len(body) == row['bytes'] and sha(body) == row['sha256'] == sha((ROOT / path).read_bytes())
for path, digest in b['native_files'].items():
    assert sha(git('show', b['head'] + ':' + path)) == digest
receipt = read(ROOT / b['prior_receipt'])
baseline = m.validate_research_rollback(receipt)
rejects = []
def reject(label, fn):
    try:
        fn()
    except (AssertionError, KeyError):
        rejects.append(label)
    else:
        raise AssertionError('Accepted mutation: ' + label)
for key, value in [('committed', False), ('signature_verified', False), ('head', '0'*40),
                   ('parent', '0'*40), ('epoch_sha256', '0'*64), ('accepted_fix_increment', 1),
                   ('native_working_diff_preserved', False)]:
    bad = copy.deepcopy(receipt); bad[key] = value
    reject('receipt-' + key, lambda: m.validate_research_rollback(bad))
reject('native-receipt-is-not-research', lambda: m.validate_research_rollback(read(ROOT / b['native_receipt'])))
saved = b['rollback_preservation']
with tempfile.TemporaryDirectory(prefix='research-v129-saved-', dir='/private/tmp') as temporary:
    scratch = Path(temporary)
    audit, failed = scratch / 'audit', scratch / 'failed'
    audit.mkdir(); failed.mkdir()
    for n in ('REPORT.json', 'ROOT-AUDIT-TERMINAL.json', 'CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'):
        (audit/n).write_bytes((ROOT/saved['directory']/n).read_bytes())
    for n in ('INSTALL-FAILURE.json', 'PRE-CURRENT-EPOCH.json', 'PRE-OWNED.json', 'PRE-ROLE.json', 'PRE.json'):
        (failed/n).write_bytes((ROOT/saved['failed_runtime']/n).read_bytes())
    test = copy.deepcopy(b); test['rollback_preservation']['directory'] = str(audit)
    test['rollback_preservation']['failed_runtime'] = str(failed)
    m.BINDINGS = test; local = test['rollback_preservation']
    assert m.validate_research_rollback(receipt) == baseline
    report = read(audit/'REPORT.json')
    def write_report(value):
        body = json.dumps(value).encode(); (audit/'REPORT.json').write_bytes(body)
        local['report_sha256'] = sha(body)
    for key, value in [('head', '0'*40), ('epoch_sha256', '0'*64), ('full_current_state_verified', False),
                       ('rollback_verified', False), ('tracked_diff_empty', False), ('staged_diff_empty', False),
                       ('new_tests_absent', False), ('source_hashes_and_identities_restored', False),
                       ('source_transition_lock_absent', False), ('only_possible_epoch_change', 'other')]:
        bad = copy.deepcopy(report); bad[key] = value; write_report(bad)
        reject('report-' + key, lambda: m.validate_research_rollback(receipt))
    for key, value in [('raw_index', '0'*64), ('entries', '0'*64), ('working_diff', '')]:
        bad = copy.deepcopy(report); bad['snapshot']['index'][key] = value; write_report(bad)
        reject('snapshot-' + key, lambda: m.validate_research_rollback(receipt))
    write_report(report)
    for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json'):
        original = (audit/n).read_bytes(); (audit/n).write_bytes(original+b' ')
        reject('control-' + n, lambda: m.validate_research_rollback(receipt))
        (audit/n).write_bytes(original)
    original_failure = (failed/'INSTALL-FAILURE.json').read_bytes()
    for key, value in [('rollback_verified', False), ('manual_recovery_required', True)]:
        bad = json.loads(original_failure); bad[key] = value
        body = json.dumps(bad).encode(); (failed/'INSTALL-FAILURE.json').write_bytes(body)
        local['failure_sha256'] = sha(body)
        changed = copy.deepcopy(report); changed['failure_sha256'] = sha(body); write_report(changed)
        reject('failure-' + key, lambda: m.validate_research_rollback(receipt))
    (failed/'INSTALL-FAILURE.json').write_bytes(original_failure)
    local['failure_sha256'] = saved['failure_sha256']; write_report(report)
    original_terminal = (audit/'ROOT-AUDIT-TERMINAL.json').read_bytes()
    for which in ('audit', 'failed-install'):
        bad = json.loads(original_terminal)
        if which == 'audit': bad['exit_code'] = 1
        else: bad['failed_install']['exit_code'] = 0
        body = json.dumps(bad).encode(); (audit/'ROOT-AUDIT-TERMINAL.json').write_bytes(body)
        local['terminal_sha256'], local['terminal'] = sha(body), bad
        reject('terminal-' + which, lambda: m.validate_research_rollback(receipt))
    (audit/'ROOT-AUDIT-TERMINAL.json').write_bytes(original_terminal)
    local['terminal_sha256'], local['terminal'] = saved['terminal_sha256'], saved['terminal']
    epoch = read(audit/'CURRENT-EPOCH.json'); epoch['unexpected_nonraw_change'] = True
    body = json.dumps(epoch).encode(); (audit/'CURRENT-EPOCH.json').write_bytes(body)
    m.EPOCH = sha(body); local['controls']['CURRENT-EPOCH.json'] = m.EPOCH
    bad = copy.deepcopy(report); bad['epoch_sha256'] = m.EPOCH; bad['controls']['CURRENT-EPOCH.json'] = m.EPOCH
    write_report(bad)
    reject('nonraw-epoch-change-even-with-rebound-digests', lambda: m.validate_research_rollback(receipt))
    m.BINDINGS, m.EPOCH = b, b['epoch_sha256']
assert not scratch.exists()
assert m.validate_research_rollback(receipt) == baseline
reject('pending-current', m.saved_admission)
sys.argv = [str(HERE/'commit.py'), '--run']
reject('disabled-run', m.main)
assert not (HERE/'result.json').exists()
print(json.dumps({'preparation_only': True, 'selected': len(selection), 'closures': len(b['completed_packages']),
                  'references': len(b['references']), 'authority_rejections': rejects,
                  'actual_rollback_positive': True, 'exact_signing_private_index_rollback_tail': True,
                  'capture_live_observer_preserved': True, 'immutable_git_objects_only': True,
                  'scratch_path': str(scratch), 'scratch_absent': True}))
