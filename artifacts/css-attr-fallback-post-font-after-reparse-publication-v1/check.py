import copy
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / 'artifacts/css-attr-fallback-after-reparse-publication-v2'
TYPED = ROOT / 'artifacts/css-explicit-taint-typed-reparse-post-font-publication-v2'
digest = lambda body: hashlib.sha256(body).hexdigest()
read = lambda path: json.loads(path.read_bytes())
policy = read(HERE / 'POLICY.json')
pair = read(HERE / 'PAIR-BINDING.json')
assert policy['bindings'] is policy['pair_binding'] is policy['stage'] is policy['runtime_output'] is None
assert policy['enabled_modes'] == []
assert all(pair[k] is None for k in ('typed_native_receipt', 'typed_parent_research', 'current_capture', 'current_epoch_sha256'))
assert policy['publication_chain'] == read(HERE / 'CHAIN-BINDING.json')
for path, pin in policy['references'].items():
    assert digest((ROOT / path).read_bytes()) == pin, path
for name in ('transform.py', 'delivery.py', 'STAGES.json', 'native.patch'):
    assert (HERE / name).read_bytes() == (PARENT / name).read_bytes()
for name in ('chain.py', 'CHAIN-BINDING.json'):
    assert (HERE / name).read_bytes() == (TYPED / name).read_bytes()
for name in ('run.py', 'publish.py', 'evidence.py', 'POLICY.json', 'PAIR-BINDING.json'):
    expected = ''.join(difflib.unified_diff((PARENT/name).read_text().splitlines(True), (HERE/name).read_text().splitlines(True), fromfile=str((PARENT/name).relative_to(ROOT)), tofile=str((HERE/name).relative_to(ROOT))))
    assert (HERE/(name+'.diff')).read_text() == expected
old, new = (PARENT/'run.py').read_text(), (HERE/'run.py').read_text()
marker = "    controls = {n: (RUNTIME / n).read_bytes()"
assert old[old.index(marker):].replace('css-attr-fallback-after-reparse-publication-', 'css-attr-fallback-post-font-after-reparse-publication-') == new[new.index(marker):]
old_e, new_e = (PARENT/'evidence.py').read_text(), (HERE/'evidence.py').read_text()
start, end = 'def verify_completed(', 'def require_future('
assert old_e[old_e.index(start):old_e.index(end)].replace(str(PARENT.relative_to(ROOT)), str(HERE.relative_to(ROOT))) == new_e[new_e.index(start):new_e.index(end)]
for path in HERE.glob('*.py'):
    compile(path.read_bytes(), str(path), 'exec')

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

chain = load('checked_chain', HERE/'chain.py')
evidence = load('checked_evidence', HERE/'evidence.py')
stage, = read(HERE/'STAGES.json')['stages']
source = read(ROOT/'artifacts/css-explicit-attribute-taint-typed-reparse-fix-v1/SOURCE.json')
cancellation = chain.authenticated(ROOT, policy['publication_chain']['cancellation_receipt'])
assert cancellation['commit'] == '2409a410a2641c54a42feefd3c998cd58cbf028e'
future_research, future_typed, future_final = 'a'*40, 'b'*40, 'c'*40
research = {'head': future_research, 'parent': cancellation['commit'], 'committed': True,
            'signature_verified': True, 'accepted_fix_increment': 0, 'native_working_diff_preserved': True}
typed = {'stage': 'reparse', 'commit': future_typed, 'parent': future_research,
         'signature_verified': True, 'files': sorted([evidence.ROLE, evidence.TYPED_TEST]),
         'epoch_sha256': 'd'*64, 'accepted': False, 'accepted_fix_increment': 0, 'app_rebuilt': False}
prior = dict(research, head=future_final, parent=future_typed)
claim = {'path': evidence.ROLE, 'owned_sha256': stage['head_preimages'][evidence.ROLE], 'identity': [1, 2]}
capture = {'full_current_state_verified': True, 'source_transition_lock_absent': True,
           'sources_match_head': True, 'controls': {'CURRENT-EPOCH.json': 'e'*64},
           'payload_claims': {evidence.ROLE: claim}, 'sources': {evidence.ROLE: copy.deepcopy(claim)},
           'installed_identities': {evidence.ROLE: [1, 2]}, 'epoch_payload_pins': dict(stage['head_preimages']),
           'snapshot': {'index': {'cached_diff': digest(b''), 'working_diff': digest(b'')}},
           'checkpoint_receipt': {'path': 'artifacts/future-research/result.json', 'sha256': 'f'*64}, 'checkpoint': prior}
future_pair = copy.deepcopy(pair)
for key in ('typed_native_receipt', 'typed_parent_research', 'current_capture'):
    future_pair[key] = {'path': 'artifacts/synthetic/'+key, 'sha256': 'f'*64}
future_pair['current_epoch_sha256'] = 'e'*64
evidence.require_typed_parent(typed, research)
evidence.require_future(future_pair, typed, capture, source)
base = (ROOT/source['roles'][evidence.ROLE]['base']['path']).read_bytes()
typed_bytes = (ROOT/source['roles'][evidence.ROLE]['candidate']['path']).read_bytes()
typed_stage, = read(TYPED/'STAGES.json')['stages']
test_bytes = (ROOT/typed_stage['files'][evidence.TYPED_TEST]['path']).read_bytes()
assert digest(test_bytes) == source['test']['sha256']
allowed = str(ROOT/policy['allowed_signers'])
answers, actual_commands, future_commands = {}, [], []
assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
future_answers = {
    ('rev-list', '--parents', '-n', '1', future_research): (future_research+' '+cancellation['commit']).encode(),
    ('merge-base', '--is-ancestor', cancellation['commit'], future_research): b'',
    ('rev-list', '--parents', cancellation['commit']+'..'+future_research): (future_research+' '+cancellation['commit']).encode(),
    ('diff', '--name-only', cancellation['commit'], future_research): b'artifacts/future-research.json',
    ('-c', 'gpg.ssh.allowedSignersFile='+allowed, 'verify-commit', future_research): b'',
    ('show', future_research+':'+evidence.ROLE): base,
    ('rev-list', '--parents', '-n', '1', future_typed): (future_typed+' '+future_research).encode(),
    ('-c', 'gpg.ssh.allowedSignersFile='+allowed, 'verify-commit', future_typed): b'',
    ('diff', '--name-only', future_research, future_typed): '\n'.join(typed['files']).encode(),
    ('show', future_typed+':'+evidence.ROLE): typed_bytes,
    ('ls-tree', future_research, '--', evidence.TYPED_TEST): b'',
    ('show', future_typed+':'+evidence.TYPED_TEST): test_bytes,
    ('merge-base', '--is-ancestor', future_typed, future_final): b'',
    ('rev-list', '--parents', future_typed+'..'+future_final): (future_final+' '+future_typed).encode(),
    ('diff', '--name-only', future_typed, future_final): b'artifacts/future-fallback-research.json',
    ('-c', 'gpg.ssh.allowedSignersFile='+allowed, 'verify-commit', future_final): b'',
}

def first_git(*args):
    if args in future_answers:
        future_commands.append(list(args)); value = future_answers[args]
    else:
        assert not any(revision in str(args) for revision in (future_research, future_typed, future_final)), args
        assert args[0] in ('-c', 'merge-base', 'rev-list', 'diff', 'show', 'ls-tree')
        assert 'HEAD' not in str(args)
        actual_commands.append(list(args))
        value = subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', *args], cwd=ROOT, env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'))
    answers[args] = value
    return value

snippet = new[new.index('    typed = observed['):new.index(marker)]
compiled = compile('def joined():\n'+snippet, str(HERE/'run.py')+':exact-admission-block', 'exec')
observed = {'typed_native': typed, 'source': source, 'tested_head': chain.BASE,
            'typed_parent_research': research, 'pair_head': future_typed, 'current_capture': capture}
binding = {'head': future_final, 'snapshot': capture['snapshot'], 'controls': capture['controls'],
           'predecessor_receipt': capture['checkpoint_receipt']}
namespace = dict(ROOT=ROOT, HERE=HERE, policy=policy, observed=observed, stage=stage,
                 evidence=evidence, digest=digest, load=load, git=first_git,
                 action='install', binding=binding, prior=prior)
exec(compiled, namespace)
namespace['joined']()
assert actual_commands and future_commands
original_answers = dict(answers)
rejects = []
def reject(label, fn):
    try:
        fn()
    except AssertionError:
        rejects.append(label)
    else:
        raise AssertionError('Accepted '+label)

def replay_git(*args):
    assert args in answers, args
    value = answers[args]
    assert value is not None, args
    return value
namespace['git'] = replay_git
invoke = namespace['joined']
invoke()
for key in ('typed_native_receipt', 'typed_parent_research', 'current_capture', 'current_epoch_sha256'):
    bad = copy.deepcopy(future_pair); bad[key] = None
    reject('pending '+key, lambda: evidence.require_future(bad, typed, capture, source))
for key, value in [('head', future_final), ('committed', False), ('signature_verified', False), ('accepted_fix_increment', 1), ('native_working_diff_preserved', False)]:
    bad = dict(research); bad[key] = value
    reject('typed parent research '+key, lambda: evidence.require_typed_parent(typed, bad))
for key in ('font_receipt', 'cancellation_receipt', 'cancellation_installation', 'cancellation_delivery'):
    saved = policy['publication_chain'][key]; policy['publication_chain'][key] = None
    reject('missing prefix '+key, invoke); policy['publication_chain'][key] = saved
for label, query, value in [
    ('typed wrong parent', ('rev-list','--parents','-n','1',future_typed), (future_typed+' '+chain.FONT).encode()),
    ('typed signature failure', ('-c','gpg.ssh.allowedSignersFile='+allowed,'verify-commit',future_typed), None),
    ('extra typed native path', ('diff','--name-only',future_research,future_typed), ('\n'.join(typed['files'])+'\nservo/extra.rs').encode()),
    ('wrong typed preimage', ('show',future_research+':'+evidence.ROLE), b'changed'),
    ('wrong typed source', ('show',future_typed+':'+evidence.ROLE), b'changed'),
    ('wrong typed WPT', ('show',future_typed+':'+evidence.TYPED_TEST), b'changed'),
    ('existing typed WPT', ('ls-tree',future_research,'--',evidence.TYPED_TEST), b'exists'),
    ('native diff before typed', ('diff','--name-only',cancellation['commit'],future_research), b'servo/extra.rs'),
    ('native diff after typed', ('diff','--name-only',future_typed,future_final), b'servo/extra.rs'),
    ('merge after typed', ('rev-list','--parents',future_typed+'..'+future_final), (future_final+' '+future_typed+' '+chain.FONT).encode()),
    ('research signature failure', ('-c','gpg.ssh.allowedSignersFile='+allowed,'verify-commit',future_final), None),
]:
    answers[query] = value; reject(label, invoke); answers = dict(original_answers)
for field in ('snapshot', 'controls', 'checkpoint_receipt', 'checkpoint'):
    saved = capture[field]; capture[field] = {}; reject('capture association '+field, invoke); capture[field] = saved
for field in ('cached_diff','working_diff'):
    for value in ('', digest(b'dirty')):
        bad = copy.deepcopy(capture); bad['snapshot']['index'][field] = value
        reject('clean digest '+field+repr(value), lambda: evidence.require_future(future_pair, typed, bad, source))
extra = '9'*40
answers[('rev-list','--parents',future_typed+'..'+future_final)] = (future_final+' '+extra+'\n'+extra+' '+future_typed).encode()
answers[('diff','--name-only',extra,future_final)] = b'artifacts/research.json'
answers[('diff','--name-only',future_typed,extra)] = b'servo/hidden-change.rs'
reject('hidden native change reverted across research interval', invoke)
answers = dict(original_answers); invoke()
assert len(read(TYPED/'CHECK.json')['result']['rejections']) == 11
assert read(PARENT/'CHECK.json')['actual_schema_check']['rejecting_controls'] == 21
print(json.dumps({'references':len(policy['references']), 'actual_signed_font_cancellation_prefix':True,
                  'real_immutable_git_calls':len(actual_commands), 'synthetic_future_protocol_calls':len(future_commands),
                  'future_authority':'All typed-parent research, typed commit, post-typed research and capture values are explicit doubles, never saved to production authority.',
                  'exact_run_admission_executed':True, 'rejections':rejects,
                  'unchanged_completed_82_and_standalone_28_replay_not_repeated':True,
                  'native_stage_transform_delivery_unchanged':True, 'signing_rollback_tail_exact':True,
                  'gates_disabled_future_bindings_null':True, 'no_live_source_index_state_actions':True}, sort_keys=True))
