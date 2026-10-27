import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TIP = '46353cb413488ab446381043e2a9d91061140fb3'
BASE = '6a363fc372c9cc0734faee64ab20f03bc762e97c'
META = 'testing/web-platform/meta/css/css-easing/timing-functions-syntax-computed.html.ini'
BLOCK = b"  [Property animation-timing-function value 'steps(calc(-10), start)']\n    expected: FAIL\n"
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
read = lambda p: json.loads(p.read_text())
digest = lambda b: hashlib.sha256(b).hexdigest()


def need(ok, why):
    if not ok:
        raise RuntimeError(why)


def save(name, value):
    with (HERE / name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def bound(ref):
    need(isinstance(ref, dict), 'missing actual binding')
    p = Path(ref['path'])
    need(not p.is_absolute() and '..' not in p.parts, 'relative binding')
    body = (ROOT / p).read_bytes()
    need(digest(body) == ref['sha256'], 'binding hash ' + str(p))
    return json.loads(body)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transform(body, research):
    need(body.count(BLOCK) == 1, 'exact one metadata block')
    return body if research else body.replace(BLOCK, b'', 1)


def selection_check(extra, promoted):
    need(isinstance(extra, dict) and extra, 'reviewed additional selection required')
    need(not (set(extra) & set(promoted)), 'additional selection overlap')
    for name, item in extra.items():
        p = Path(name)
        need(name.startswith('artifacts/') and '..' not in p.parts and '\n' not in name
             and '\t' not in name and not p.is_absolute(), 'research-only path')
        need(item['mode'] in ('100644', '100755') and re.fullmatch('[0-9a-f]{64}', item['sha256']), 'selection entry')


def main():
    need(sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize, 'isolated interpreter')
    for n in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        need(not os.environ.get(n), 'ambient ' + n)
    inputs = read(HERE / 'INPUTS.json')
    need(sys.argv[1:] == ['--run'] and inputs['ready'] is True, 'disabled rewrite')
    for n, pin in inputs['local_pins'].items():
        need(digest((HERE / n).read_bytes()) == pin, 'local payload ' + n)
    for n, pin in read(HERE / 'REFERENCES.json').items():
        need(digest((ROOT / n).read_bytes()) == pin, 'helper pin ' + n)
    review = bound(inputs['root_review'])
    need(review['status'] == 'FIX121_HISTORY_REWRITE_ROOT_REVIEW_GO'
         and review['local_pins'] == inputs['local_pins'], 'review binding')
    admission = bound(inputs['admission'])
    need(admission['status'] == 'FIX121_METADATA_CARRIER_ROOT_VERIFIED'
         and admission['metadata_validation_exit'] == 0 and admission['root_preservation_exit'] == 0
         and admission['validation_peer_GO'] is True, 'actual validation/preservation/peer')
    need(admission['evidence'], 'actual evidence required')
    for ref in admission['evidence']:
        bound(ref)
    epoch = bound(admission['epoch'])
    extra = bound(admission['additional_selection'])
    promoted = read(HERE / 'RESEARCH-PROMOTION.json')
    selection_check(extra, promoted)
    sequence = read(HERE / 'SEQUENCE.json')
    need(len(sequence) == 37 and len(promoted) == 39, 'fixed plan cardinality')
    carrier = admission['carrier']
    need(re.fullmatch('[0-9a-f]{40}', carrier), 'actual carrier')
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    def git(*args, git_env=env, data=None):
        return subprocess.check_output(GIT + list(args), cwd=ROOT, env=git_env, input=data)
    def tree_entries(tree, names):
        result = {}
        for row in git('ls-tree', '-r', '-z', tree, '--', *sorted(names)).split(b'\0'):
            if row:
                fields, name = row.split(b'\t', 1)
                mode, kind, oid = fields.decode().split()
                need(kind == 'blob', 'selected blob')
                result[name.decode()] = {'mode': mode, 'blob': oid}
        return result
    def changes(a, b):
        return set(git('diff-tree', '--no-commit-id', '--name-only', '-r', '-z', a, b).decode().split('\0')) - {''}
    h = load('fold_preservation', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
    guards = load('fold_epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
    need(git('rev-parse', 'HEAD').decode().strip() == carrier and git('rev-parse', carrier + '^').decode().strip() == TIP, 'carrier on exact tip')
    need(git('--version').decode().strip() == read(HERE / 'GIT-CAPABILITY.json')['version'], 'reviewed symbolic-ref transaction Git version')
    branch = git('symbolic-ref', 'HEAD').decode().strip()
    need(branch == 'refs/heads/stylo-bloom-verification-2', 'expected branch')
    need(git('rev-list', '--reverse', '--parents', BASE + '..' + TIP).decode().splitlines()
         == [e['old_commit'] + ' ' + e['old_parent'] for e in sequence], 'exact linear range')
    need(changes(TIP, carrier) == set(extra) | {META}, 'carrier only new evidence and metadata')
    need(not tree_entries(TIP, extra), 'additional paths must be new')
    entries = tree_entries(carrier, set(extra) | set(promoted) | {META})
    need(set(entries) == set(extra) | set(promoted) | {META}, 'all carrier entries')
    for n, item in (promoted | extra).items():
        need(entries[n]['mode'] == item['mode'] and digest(git('cat-file', 'blob', entries[n]['blob'])) == item['sha256'], 'carrier selected body ' + n)
        need(epoch['committed_research_working_payloads'].get(n) == item['sha256'], 'research epoch ' + n)
    need(entries[META]['mode'] == '100644' and git('show', carrier + ':' + META) == transform(git('show', TIP + ':' + META), False), 'carrier exact metadata correction')
    before = guards.verify_current(h, ROOT, env, epoch)
    need(epoch['semantic_index']['head'] == carrier, 'post-carrier epoch')
    with (HERE / 'ATTEMPT.json').open('x') as f:
        json.dump({'carrier': carrier, 'branch': branch, 'ready': True}, f)
    result = {'status': 'FAILED', 'carrier': carrier, 'published': False, 'rewrites': {}, 'errors': []}
    try:
        key = git('config', '--get', 'user.signingkey').decode().strip().removeprefix('key::')
        need(key.startswith(('ssh-', 'ecdsa-')) and '\n' not in key, 'configured public SSH key')
        with tempfile.TemporaryDirectory(prefix='fix121-history-', dir='/private/tmp') as td:
            tmp = Path(td)
            allowed = tmp / 'allowed-signers'
            allowed.write_text('configured-key ' + key + '\n')
            def signature(commit, label):
                with (HERE / (label + '-signature.log')).open('x') as log:
                    run = subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(allowed), 'verify-commit', commit], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
                need(run.returncode == 0, 'signature ' + label)
            for i, e in enumerate(sequence):
                body = git('cat-file', 'commit', e['old_commit'])
                need(digest(body) == e['commit_object_sha256'], 'old commit object')
                signature(e['old_commit'], 'old-' + str(i))
            signature(carrier, 'carrier')
            backup = 'refs/heads/backup-fix121-metadata-' + carrier[:12]
            git('update-ref', backup, carrier, '0' * 40)
            result['backup'] = backup
            index_env = dict(env, GIT_INDEX_FILE=str(tmp / 'index'))
            parent = BASE
            for i, e in enumerate(sequence):
                old = e['old_commit']
                old_entries = tree_entries(old, set(promoted) | set(extra) | {META})
                need(old_entries[META]['mode'] == '100644', 'original metadata mode')
                for n in set(old_entries) - {META}:
                    need(old_entries[n] == entries[n], 'do not overwrite historical research variant')
                git('read-tree', old, git_env=index_env)
                updates = {n: entries[n] for n in set(promoted) | set(extra)}
                body = transform(git('show', old + ':' + META), i == 0)
                if i:
                    blob = git('hash-object', '-w', '--stdin', data=body).decode().strip()
                    updates[META] = {'mode': '100644', 'blob': blob}
                payload = ''.join(v['mode'] + ' ' + v['blob'] + '\t' + n + '\n' for n, v in sorted(updates.items())).encode()
                git('update-index', '--add', '--index-info', git_env=index_env, data=payload)
                tree = git('write-tree', git_env=index_env).decode().strip()
                expected = (set(promoted) | set(extra)) - set(old_entries)
                if i:
                    expected.add(META)
                need(changes(old, tree) == expected, 'exact per-tree changes')
                need(tree_entries(tree, updates) == updates, 'exact per-tree selected bodies/modes')
                need(git('show', tree + ':' + META) == body, 'exact per-tree metadata')
                raw = git('cat-file', 'commit', old)
                headers, message = raw.split(b'\n\n', 1)
                author = next(line for line in headers.splitlines() if line.startswith(b'author '))
                match = re.fullmatch(rb'author (.*) <([^<>]*)> ([0-9]+) ([+-][0-9]{4})', author)
                need(match is not None, 'author identity')
                signing_env = dict(env, GIT_AUTHOR_NAME=match[1].decode(), GIT_AUTHOR_EMAIL=match[2].decode(), GIT_AUTHOR_DATE=match[3].decode() + ' ' + match[4].decode())
                msg = tmp / 'message'; msg.write_bytes(message)
                with (HERE / ('new-' + str(i) + '-signing.log')).open('x') as log:
                    run = subprocess.run(GIT + ['commit-tree', '-S', tree, '-p', parent, '-F', str(msg)], cwd=ROOT, env=signing_env, stdout=subprocess.PIPE, stderr=log)
                save('new-' + str(i) + '-attempt.json', {'old': old, 'tree': tree, 'parent': parent, 'exit': run.returncode, 'stdout': run.stdout.decode()})
                need(run.returncode == 0, 'signing failed; no automatic retry')
                new = run.stdout.decode().strip()
                new_headers, new_message = git('cat-file', 'commit', new).split(b'\n\n', 1)
                need(author in new_headers.splitlines() and message == new_message, 'preserved author/message')
                need(git('rev-parse', new + '^').decode().strip() == parent and git('rev-parse', new + '^{tree}').decode().strip() == tree, 'new parent/tree')
                signature(new, 'new-' + str(i))
                result['rewrites'][old] = new
                save('new-' + str(i) + '-verified.json', {'old': old, 'new': new, 'parent': parent, 'tree': tree, 'signature_verified': True})
                parent = new
            need(git('rev-parse', parent + '^{tree}') == git('rev-parse', carrier + '^{tree}'), 'final tree exactly carrier')
            need(git('rev-list', '--count', BASE + '..' + parent).strip() == b'37', 'exact rewritten count')
            save('REWRITE-MAP.json', result['rewrites'])
            mapping = read(HERE / 'CURRENT-FIX-MAPPING.json')
            for item in mapping:
                item['proposed_current_fields'] = {k: [result['rewrites'].get(x, x) for x in v] if isinstance(v, list) else result['rewrites'].get(v, v) for k, v in item['current_fields'].items()}
            save('PROPOSED-CURRENT-FIX-MAPPING.json', mapping)
            (HERE / 'RANGE-DIFF.txt').write_bytes(git('range-diff', BASE + '..' + carrier, BASE + '..' + parent))
            need(guards.verify_current(h, ROOT, env, epoch) == before, 'full prepublication preservation')
            need(git('symbolic-ref', 'HEAD').decode().strip() == branch, 'prepublication symbolic branch')
            transaction = 'start\noption no-deref\nsymref-verify HEAD ' + branch + '\nverify ' + backup + ' ' + carrier + '\nupdate ' + branch + ' ' + parent + ' ' + carrier + '\nprepare\ncommit\n'
            git('update-ref', '--stdin', data=transaction.encode())
            result.update(published=True, new_tip=parent)
            state = h.index_state(ROOT, env)
            need(git('symbolic-ref', 'HEAD').decode().strip() == branch and state['head'] == parent, 'published branch and HEAD')
            need(all(state[k] == before['index'][k] for k in ('entries', 'cached_diff', 'working_diff', 'raw_index')), 'main index/worktree unchanged')
            current = copy.deepcopy(epoch)
            current['semantic_index'] = h.semantic_index(state)
            after = guards.verify_current(h, ROOT, env, current)
            need(after['nested_index'] == before['nested_index'], 'nested index unchanged')
            need(git('symbolic-ref', 'HEAD').decode().strip() == branch and git('rev-parse', 'HEAD').decode().strip() == parent, 'final published branch and HEAD')
            save('CURRENT-EPOCH.json', current)
            result.update(status='FIX121_METADATA_HISTORY_REWRITE_VERIFIED', signatures_verified=True, final_tree_exact_carrier=True, current_ledgers_modified=False, configured_public_key_sha256=digest(key.encode()))
    except BaseException as error:
        result['errors'].append(repr(error))
        try:
            result['actual_head_after'] = git('rev-parse', 'HEAD').decode().strip()
        except BaseException as observation:
            result['errors'].append('head observation: ' + repr(observation))
        try:
            state = h.index_state(ROOT, env)
            need(git('symbolic-ref', 'HEAD').decode().strip() == branch, 'failure symbolic branch ownership')
            need(state['head'] == (result.get('new_tip') if result['published'] else carrier), 'failure head ownership')
            need(all(state[k] == before['index'][k] for k in ('entries', 'cached_diff', 'working_diff', 'raw_index')), 'failure index/worktree preservation')
            failure_epoch = copy.deepcopy(epoch)
            failure_epoch['semantic_index'] = h.semantic_index(state)
            check = guards.verify_current(h, ROOT, env, failure_epoch)
            need(check['nested_index'] == before['nested_index'], 'failure nested preservation')
            result['failure_preservation_verified'] = True
        except BaseException as preservation:
            result['errors'].append('failure preservation: ' + repr(preservation))
    finally:
        save('RESULT.json', result)
    need(result['status'] == 'FIX121_METADATA_HISTORY_REWRITE_VERIFIED' and not result['errors'], 'rewrite failed; inspect retained result, no blind retry')


if __name__ == '__main__':
    main()
