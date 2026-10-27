import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-integer-stored-range-history-runtime-v1'
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def save(name, value):
    with (HERE / name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def publish(git, branch, backup, carrier, new, result):
    need(git('symbolic-ref', 'HEAD').decode().strip() == branch, 'prepublication branch')
    need(git('rev-parse', 'HEAD').decode().strip() == carrier, 'prepublication HEAD')
    transaction = 'start\nverify ' + backup + ' ' + carrier + '\nupdate ' + branch + ' ' + new + ' ' + carrier + '\nprepare\ncommit\n'
    git('update-ref', '--stdin', data=transaction.encode())
    result['published'] = True
    need(git('symbolic-ref', 'HEAD').decode().strip() == branch, 'postpublication branch')
    need(git('rev-parse', 'HEAD').decode().strip() == new, 'postpublication HEAD')


def main():
    need(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, 'isolated interpreter')
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        need(not os.environ.get(name), 'ambient ' + name)
    inputs = read(HERE / 'INPUTS.json')
    need(sys.argv[1:] == ['--run'] and inputs['ready'] is True, 'disabled publication recovery')
    for n, pin in inputs['local_pins'].items():
        need(sha(HERE / n) == pin, 'local pin ' + n)
    for n, pin in read(HERE / 'REFERENCES.json').items():
        need(sha(ROOT / n) == pin, 'reference pin ' + n)
    spec = importlib.util.spec_from_file_location('verified_rewrite', ROOT / 'artifacts/css-integer-stored-range-history-rewrite-v2/rewrite.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    review = m.bound(inputs['root_review'])
    need(review['status'] == 'FIX121_PUBLICATION_RECOVERY_ROOT_REVIEW_GO' and review['local_pins'] == inputs['local_pins']
         and review['git_writers_serialized'] is True, 'root review and exclusive Git writer')
    terminal = m.bound(inputs['actual_failed_terminal'])
    need(terminal['session'] == 47864 and terminal['exit'] == 1 and terminal['terminal_chunk'] == '518ee6', 'actual failed terminal')
    failed = read(RUNTIME / 'RESULT.json')
    need(failed['status'] == 'FAILED' and failed['published'] is False and failed['failure_preservation_verified'] is True, 'failed run preserved')
    mapping = read(RUNTIME / 'REWRITE-MAP.json')
    need(mapping == failed['rewrites'] and len(mapping) == 37, 'exact signed mapping')
    admission = m.bound(read(RUNTIME / 'INPUTS.json')['admission'])
    need(admission['status'] == 'FIX121_METADATA_CARRIER_ROOT_VERIFIED' and admission['metadata_validation_exit'] == 0
         and admission['root_preservation_exit'] == 0 and admission['validation_peer_GO'] is True, 'original admission')
    for item in admission['evidence']:
        m.bound(item)
    epoch, extra = m.bound(admission['epoch']), m.bound(admission['additional_selection'])
    promoted, sequence = read(RUNTIME / 'RESEARCH-PROMOTION.json'), read(RUNTIME / 'SEQUENCE.json')
    m.selection_check(extra, promoted)
    need(len(sequence) == 37 and len(promoted) == 39, 'exact planned scope')
    carrier, backup = failed['carrier'], failed['backup']
    need(admission['carrier'] == carrier, 'admitted carrier')
    branch = 'refs/heads/stylo-bloom-verification-2'
    new = mapping[m.TIP]
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    def git(*args, data=None):
        return subprocess.check_output(GIT + list(args), cwd=ROOT, env=env, input=data)
    def entries(tree, paths):
        out = {}
        for row in git('ls-tree', '-r', '-z', tree, '--', *sorted(paths)).split(b'\0'):
            if row:
                fields, path = row.split(b'\t', 1)
                mode, kind, oid = fields.decode().split()
                need(kind == 'blob', 'blob role')
                out[path.decode()] = {'mode': mode, 'blob': oid}
        return out
    def changes(a, b):
        return set(git('diff-tree', '--no-commit-id', '--name-only', '-r', '-z', a, b).decode().split('\0')) - {''}
    need(git('symbolic-ref', 'HEAD').decode().strip() == branch and git('rev-parse', 'HEAD').decode().strip() == carrier, 'initial branch/carrier')
    need(git('rev-parse', backup).decode().strip() == carrier and git('rev-parse', carrier + '^').decode().strip() == m.TIP, 'backup/carrier parent')
    need(git('rev-list', '--reverse', '--parents', m.BASE + '..' + m.TIP).decode().splitlines()
         == [e['old_commit'] + ' ' + e['old_parent'] for e in sequence], 'old linear chain')
    need(changes(m.TIP, carrier) == set(extra) | {m.META} and not entries(m.TIP, extra), 'carrier exact additions')
    selected = entries(carrier, set(extra) | set(promoted))
    need(set(selected) == set(extra) | set(promoted), 'selected carrier scope')
    for n, pin in (promoted | extra).items():
        need(selected[n]['mode'] == pin['mode'] and m.digest(git('cat-file', 'blob', selected[n]['blob'])) == pin['sha256'], 'selected body ' + n)
        need(epoch['committed_research_working_payloads'].get(n) == pin['sha256'], 'research epoch ' + n)
    need(git('show', carrier + ':' + m.META) == m.transform(git('show', m.TIP + ':' + m.META), False), 'carrier metadata')
    h = m.load('publication_guards', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    guards = m.load('publication_epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
    before = guards.verify_current(h, ROOT, env, epoch)
    save('ATTEMPT.json', {'carrier': carrier, 'new_tip': new, 'no_resigning': True})
    result = {'status': 'FAILED', 'published': False, 'carrier': carrier, 'new_tip': new, 'backup': backup, 'errors': []}
    try:
        key = git('config', '--get', 'user.signingkey').decode().strip().removeprefix('key::')
        need(key.startswith(('ssh-', 'ecdsa-')) and '\n' not in key, 'configured public key')
        with tempfile.TemporaryDirectory(prefix='fix121-publication-', dir='/private/tmp') as td:
            allowed = Path(td) / 'allowed-signers'; allowed.write_text('configured-key ' + key + '\n')
            def verify_signature(commit, label):
                with (HERE / (label + '-signature.log')).open('x') as log:
                    run = subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(allowed), 'verify-commit', commit], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
                need(run.returncode == 0, 'signature ' + label)
            parent = m.BASE
            for i, e in enumerate(sequence):
                old, replacement = e['old_commit'], mapping[e['old_commit']]
                raw = git('cat-file', 'commit', old)
                need(m.digest(raw) == e['commit_object_sha256'], 'old object')
                old_headers, old_message = raw.split(b'\n\n', 1)
                new_headers, new_message = git('cat-file', 'commit', replacement).split(b'\n\n', 1)
                author = next(line for line in old_headers.splitlines() if line.startswith(b'author '))
                need(author in new_headers.splitlines() and old_message == new_message, 'author/message')
                tree = git('rev-parse', replacement + '^{tree}').decode().strip()
                receipt = read(RUNTIME / ('new-' + str(i) + '-verified.json'))
                need(receipt == {'old': old, 'new': replacement, 'parent': parent, 'tree': tree, 'signature_verified': True}, 'verified receipt join')
                need(git('rev-list', '--parents', '-n', '1', replacement).decode().strip() == replacement + ' ' + parent, 'replacement single parent')
                old_selected = entries(old, selected)
                need(all(v == selected[n] for n, v in old_selected.items()), 'historical selected body')
                need(changes(old, replacement) == (set(selected) - set(old_selected)) | ({m.META} if i else set()), 'exact per-tree changed paths')
                need(entries(replacement, selected) == selected, 'exact selected bytes and modes')
                need(entries(replacement, {m.META})[m.META]['mode'] == '100644'
                     and git('show', replacement + ':' + m.META) == m.transform(git('show', old + ':' + m.META), i == 0), 'metadata transform')
                verify_signature(old, 'old-' + str(i)); verify_signature(replacement, 'new-' + str(i))
                parent = replacement
            verify_signature(carrier, 'carrier')
        need(parent == new and git('rev-parse', new + '^{tree}') == git('rev-parse', carrier + '^{tree}'), 'exact final carrier tree')
        need(git('rev-list', '--count', m.BASE + '..' + new).strip() == b'37', 'exact new count')
        save('REVERIFIED.json', {'rewrites': mapping, 'verified_signed_commits': 37, 'carrier_tree_exact': True, 'current_field_mapping': read(RUNTIME / 'PROPOSED-CURRENT-FIX-MAPPING.json')})
        need(guards.verify_current(h, ROOT, env, epoch) == before, 'prepublication full preservation')
        publish(git, branch, backup, carrier, new, result)
        state = h.index_state(ROOT, env)
        need(state['head'] == new and all(state[k] == before['index'][k] for k in ('entries', 'cached_diff', 'working_diff', 'raw_index')), 'postpublication index/head')
        current = copy.deepcopy(epoch); current['semantic_index'] = h.semantic_index(state)
        after = guards.verify_current(h, ROOT, env, current)
        need(after['nested_index'] == before['nested_index'], 'nested index preserved')
        need(git('symbolic-ref', 'HEAD').decode().strip() == branch and git('rev-parse', 'HEAD').decode().strip() == new, 'final branch/head')
        save('CURRENT-EPOCH.json', current)
        result.update(status='FIX121_HISTORY_PUBLICATION_RECOVERY_VERIFIED', reused_signed_commits=37, rewrites=mapping, signatures_verified=True, current_ledgers_modified=False, final_tree_exact_carrier=True, non_atomic_symbolic_head_check=True, git_writers_serialized=True)
    except BaseException as error:
        result['errors'].append(repr(error))
        try:
            state = h.index_state(ROOT, env)
            result['actual_head_after'] = state['head']
            need(git('symbolic-ref', 'HEAD').decode().strip() == branch and state['head'] == (new if result['published'] else carrier), 'failure branch/head')
            need(all(state[k] == before['index'][k] for k in ('entries', 'cached_diff', 'working_diff', 'raw_index')), 'failure index preservation')
            current = copy.deepcopy(epoch); current['semantic_index'] = h.semantic_index(state)
            after = guards.verify_current(h, ROOT, env, current)
            need(after['nested_index'] == before['nested_index'], 'failure nested index')
            result['failure_preservation_verified'] = True
        except BaseException as failure:
            result['errors'].append('preservation: ' + repr(failure))
    finally:
        save('RESULT.json', result)
    need(result['status'] == 'FIX121_HISTORY_PUBLICATION_RECOVERY_VERIFIED' and not result['errors'], 'publication failed; inspect result, no blind retry')


if __name__ == '__main__':
    main()
