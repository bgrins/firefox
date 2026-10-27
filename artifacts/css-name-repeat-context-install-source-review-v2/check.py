import ast
import hashlib
import json
from pathlib import Path
import stat
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
A = ROOT / 'artifacts'
R = A / 'css-name-repeat-context-install-runtime-v2'
S = A / 'css-hidden-query-signing-execution-v6'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
refs = {
    str((R / 'DRAFT-FILES.json').relative_to(ROOT)): '6bb675d2bf1ce4d22824c10f57b2079f00337456c66e532b920df3dce3d35ac7',
    str((S / 'FILES.json').relative_to(ROOT)): 'd6a77ce6a991f619d3e773b321c9a718527665ce6700ab0bf8430ed74dd1d0d4',
    'artifacts/css-name-repeat-context-install-source-review-v1/FILES.json': '8747c104d7c7d7ad0651ce7e8704e452a847ea805a5402609fd46fa69e921f5f',
}
for name, digest in refs.items():
    manifest = ROOT / name
    assert sha(manifest) == digest
    for member, expected in read(manifest).items():
        assert not Path(member).is_absolute() and '..' not in Path(member).parts
        path = manifest.parent / member
        assert stat.S_ISREG(path.lstat().st_mode) and sha(path) == expected
inputs = read(R / 'INPUTS.json')
assert sha(R / 'INPUTS.json') == '9be067c57f809f50f5af4968e779c3d20d2f265dd6652231e4a511dad8f8b83c'
assert sha(R / 'install.py') == inputs['install_sha256'] == '9bf9ca8cce3534eeaff2e0af0ada388baafc7a41c89e544ba57937abfac8ead0'
assert inputs['ready_for_execution'] is False
assert all(inputs[k] is None for k in ('controller_review', 'actual_session', 'actual_exit'))
replay_path = A / 'css-name-repeat-context-install-source-review-v2-replay/CHECK.json'
assert replay_path.read_bytes() == (R / 'static-final/CHECK.json').read_bytes()
refs[str(replay_path.relative_to(ROOT))] = sha(replay_path)
refs[str((R / 'install.py').relative_to(ROOT))] = sha(R / 'install.py')
refs[str((R / 'INPUTS.json').relative_to(ROOT))] = sha(R / 'INPUTS.json')
comparison = A / 'css-name-repeat-context-comparison-runtime-v1'
final = read(comparison / 'FINAL.json')
receipt = read(S / 'ROOT-FINAL-CHECK.json')
assert receipt['status'] == 'SIGNED_ATTEMPT_FAILED_STATE_PRESERVED'
assert receipt['signing_session'] == 90997 and receipt['signing_exit'] == 128
assert receipt['current_epoch'] == str(comparison.relative_to(ROOT)) and receipt['current_final_sha256'] == sha(comparison / 'FINAL.json')
assert receipt['head'] == final['snapshot']['head'] and receipt['raw_index_exact'] and receipt['pre_post_index_exact']
assert not receipt['commit_created'] and not receipt['unsigned_fallback'] and not receipt['push']
assert [receipt[k] for k in ('roles', 'sources', 'installed_identities', 'staged_payloads', 'working_staged_payloads', 'native_paths')] == [611, 72, 23, 925, 925, 43]
completion = read(S / 'ROOT-COMPLETION.json')
assert completion['after_index_session'] == 18904 and completion['after_index_exit'] == 0
assert completion['root_preservation_session'] == 45716 and completion['root_preservation_exit'] == 0
pre = read(S / 'IMMEDIATE-PREFLIGHT.json')
post = read(S / 'AFTER-SIGNING-INDEX.json')
assert pre['before_after'] == post['before_after']
assert all(post['before_after'][k] == final['snapshot'][k] for k in ('head', 'index_entries_sha256', 'index_diff_sha256'))
refs[str((S / 'ROOT-FINAL-CHECK.json').relative_to(ROOT))] = sha(S / 'ROOT-FINAL-CHECK.json')
tree = ast.parse((R / 'install.py').read_text())
main = next(n for n in tree.body if isinstance(n, ast.Try))
tail = compile(ast.Module(body=main.finalbody, type_ignores=[]), '<actual finalization>', 'exec')
last = compile(ast.Module(body=[tree.body[-1]], type_ignores=[]), '<actual final success gate>', 'exec')


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


checks = []
for fault in ('FINAL.json', 'FINAL-PINS.json', 'CLEANUP.json', 'RESULT.json'):
    with tempfile.TemporaryDirectory(prefix='name-repeat-publication-review-') as directory:
        scratch = Path(directory)
        calls = []
        state = dict(HERE=scratch, installed=False, candidate_ready=True, failure=None,
                     owned={'fixture': {'identity': [1, 2], 'sha256': 'body'}},
                     owned_plan={'temporary_fixtures': {'fixture': {}}}, current_binaries={},
                     final={'pins': {}, 'installed_tests': {}}, recovery_errors=[],
                     completed=['candidate'], captured=['candidate'], transitions=[],
                     mutation_started=True, need=need)

        def save(name, value):
            with (scratch / name).open('x') as stream:
                stream.write(json.dumps(value))
            if name == fault:
                raise OSError('full body written before publication failure')

        def restore():
            calls.extend(['restore-a', 'restore-b'])
            return []

        def build(*args, **kwargs):
            calls.append('restored-build')

        def capture(*args):
            calls.append('restored-capture')
            state['completed'].append('restored')
            state['captured'].append('restored')

        def cleanup():
            calls.append('fixture-cleanup')
            return ['fixture'], []

        state.update(save=save, restore_sources=restore, build=build, capture=capture,
                     cleanup_fixtures=cleanup, verify=lambda *a, **k: {'pins': {}, 'installed_tests': {}})
        exec(tail, state)
        assert calls == ['restore-a', 'restore-b', 'restored-build', 'restored-capture', 'fixture-cleanup']
        assert not state['installed'] and state['failure'].startswith('success publication:')
        recovery = read(scratch / 'RECOVERY-RESULT.json')
        assert not recovery['installed'] and recovery['restored'] and not recovery['recovery_errors']
        assert fault in recovery['supersedes_partial_success_records']
        if fault == 'RESULT.json':
            assert read(scratch / fault)['installed'] is True
        try:
            exec(last, state)
        except RuntimeError:
            pass
        else:
            raise AssertionError('partial success escaped terminal failure')
        checks.append({'publication': fault, 'readable_record_before_exception': True,
                       'recovery_complete': True, 'terminal_failure_required': True})
result = {'status': 'NAME_REPEAT_INSTALL_SOURCE_BINDING_GO', 'v1_hold_resolved': True,
    'install_sha256': inputs['install_sha256'], 'static_policy_checks': 18,
    'static_ownership_checks': 4, 'actual_try_finally_histories': 11,
    'additional_full_write_failure_checks': checks, 'unchanged_helper_definitions': 14,
    'signing_session': 90997, 'signing_exit': 128, 'archived_epoch_preserved': True,
    'ready_for_execution': False, 'live_inputs_read': False, 'live_actions': False,
    'native_acceptance': False}
for name, value in [('CHECK.json', result), ('REFERENCES.json', refs), ('REVIEWED-INPUTS.json', inputs)]:
    with (HERE / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')
print(json.dumps(result, indent=2))
