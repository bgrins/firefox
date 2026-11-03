import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_bytes())


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def authenticated(manifest):
    assert sha(HERE / 'FILES.json') == manifest
    records = read(HERE / 'FILES.json')
    assert set(records) == {p.name for p in HERE.iterdir()} - {'FILES.json'}
    for name, record in records.items():
        path = HERE / name
        assert path.is_file() and not path.is_symlink()
        assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes']
    policy = read(HERE / 'POLICY.json')
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin, name
    plan = read(ROOT / policy['plan'])
    assert plan['root_research_commit'] == policy['parent'] == '2701dc46ac5920adf3505885c67936287e1b037f'
    assert len(plan['files']) == 7 and plan['native_files'] == 4 and plan['test_files'] == 3
    assert policy['local_ref'] == 'refs/heads/css-selective-cancellation-standalone-2701'
    assert policy['output'] == 'artifacts/css-selective-cancellation-standalone-commit-runtime-v1'
    assert not plan['counted_as_additional_fix']
    for row in plan['files'].values():
        assert sha(ROOT / row['source']) == row['candidate_sha256']
    return policy, plan


def require_stack(receipt):
    assert receipt['stage'] == 'selective-cancellation' and receipt['signature_verified'] is True
    assert receipt['accepted_fix_increment'] == 0 and receipt['app_rebuilt'] is False
    assert len(receipt['commit']) == 40 and all(c in '0123456789abcdef' for c in receipt['commit'])
    assert receipt['files'] == sorted([
        'servo/components/style/traversal.rs', 'servo/components/style/gecko/traversal.rs',
        'servo/ports/geckolib/glue.rs',
        'testing/web-platform/tests/web-animations/animation-model/keyframe-effects/root-font-cancel-child-animation.html',
        'testing/web-platform/tests/web-animations/animation-model/keyframe-effects/root-font-cancel-child-depth.html'])


def file_state(path):
    if not os.path.lexists(path):
        return None
    st = path.lstat()
    assert stat.S_ISREG(st.st_mode), str(path)
    return {'sha256': sha(path), 'identity': [st.st_dev, st.st_ino], 'mode': stat.S_IMODE(st.st_mode)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('check', 'run'))
    parser.add_argument('manifest')
    args = parser.parse_args()
    policy, plan = authenticated(args.manifest)
    if args.action == 'check':
        print(json.dumps({'payloads_authenticated': 7, 'execution_enabled': policy['execution_enabled'], 'stack_receipt_pending': policy['stack_commit_receipt'] is None, 'live_actions': False}))
        return
    assert policy['execution_enabled'] is True and policy['stack_commit_receipt'] is not None
    assert not any(k.startswith('GIT_') and k != 'GIT_OPTIONAL_LOCKS' for k in os.environ)
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
    def git(*arguments, input=None, private=None):
        return subprocess.check_output(GIT + list(arguments), cwd=ROOT, env=private or env, input=input)
    def config():
        observed = {key: git('config', '--get', key).decode().strip() for key in policy['expected_signing_config']}
        assert observed == policy['expected_signing_config']
        return observed
    assert git('rev-parse', '--show-toplevel').decode().strip() == str(ROOT)
    config_before = config()
    record = policy['stack_commit_receipt']
    assert sha(ROOT / record['path']) == record['sha256']
    stack = read(ROOT / record['path']); require_stack(stack)
    assert git('rev-parse', 'HEAD').decode().strip() == stack['commit']
    branch = git('symbolic-ref', 'HEAD').decode().strip()
    assert branch != policy['local_ref']
    git('check-ref-format', policy['local_ref'])
    def absent_ref():
        result = subprocess.run(GIT + ['show-ref', '--verify', '--quiet', policy['local_ref']], cwd=ROOT, env=env)
        assert result.returncode == 1
        result = subprocess.run(GIT + ['symbolic-ref', '--quiet', policy['local_ref']], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode == 1
    absent_ref()
    index_path = Path(git('rev-parse', '--git-path', 'index').decode().strip())
    if not index_path.is_absolute(): index_path = ROOT / index_path
    controls = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
    assert not os.path.lexists(controls / 'SOURCE-TRANSITION.lock')
    def protected():
        return {'head': git('rev-parse', 'HEAD').decode().strip(), 'branch': git('symbolic-ref', 'HEAD').decode().strip(),
                'real_index': file_state(index_path),
                'canonical': {n:file_state(controls / n) for n in ('CURRENT-EPOCH.json','OWNED.json','ROLE.json')},
                'seven_working_paths': {n:file_state(ROOT / n) for n in plan['files']}}
    before = protected()
    output = ROOT / policy['output']
    output.mkdir()
    result = {'success':False,'ref_created':False,'commit':None,'parent':policy['parent'],'main_branch':branch,
              'primary_fix_increment':0,'standalone_alternative':True,'new_build_or_browser':False,
              'files':sorted(plan['files'])}
    save(output / 'PRE.json', before)
    try:
        for label, revision in [('parent',policy['parent']),('stack',stack['commit'])]:
            with (output / (label + '-signature.log')).open('xb') as stream:
                subprocess.run(GIT + ['-c','gpg.ssh.allowedSignersFile='+str(ROOT/policy['allowed_signers']),'verify-commit',revision],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
        with tempfile.TemporaryDirectory(prefix='selective-standalone-index-',dir='/private/tmp') as temporary:
            private = dict(env,GIT_INDEX_FILE=str(Path(temporary)/'index'))
            git('read-tree',policy['parent'],private=private)
            blobs = {}
            for name,row in plan['files'].items():
                entry = git('ls-tree',policy['parent'],'--',name)
                if row['base_sha256'] is None:
                    assert not entry
                else:
                    assert entry.split()[0] == b'100644'
                    assert hashlib.sha256(git('show',policy['parent']+':'+name)).hexdigest() == row['base_sha256']
                body = (ROOT / row['source']).read_bytes()
                assert hashlib.sha256(body).hexdigest() == row['candidate_sha256']
                blob = git('hash-object','-w','--stdin',input=body).decode().strip()
                blobs[name] = blob
                git('update-index','--add','--cacheinfo','100644',blob,name,private=private)
            tree = git('write-tree',private=private).decode().strip()
            assert git('diff-tree','--no-commit-id','--name-only','-r',policy['parent'],tree).decode().splitlines() == sorted(plan['files'])
            for name,row in plan['files'].items():
                assert git('ls-tree',tree,'--',name).split()[:2] == [b'100644',b'blob']
                assert hashlib.sha256(git('show',tree+':'+name)).hexdigest() == row['candidate_sha256']
            save(output/'TREE.json',{'tree':tree,'parent':policy['parent'],'blobs':blobs,'source_sha256':{n:r['candidate_sha256'] for n,r in plan['files'].items()}})
            assert protected() == before and config() == config_before
            with (output/'signing.log').open('xb') as stream:
                signed = subprocess.run(GIT+['commit-tree','-S',tree,'-p',policy['parent']],cwd=ROOT,env=private,input=(policy['message']+'\n').encode(),stdout=subprocess.PIPE,stderr=stream)
            result['signing_exit'] = signed.returncode
            assert signed.returncode == 0, 'Configured signing failed; no retry or ref creation'
            commit = signed.stdout.decode().strip()
            assert len(commit)==40 and all(c in '0123456789abcdef' for c in commit)
            result['commit'] = commit
            assert git('rev-list','--parents','-n','1',commit).decode().split() == [commit,policy['parent']]
            assert git('rev-parse',commit+'^{tree}').decode().strip()==tree
            with (output/'signature.log').open('xb') as stream:
                subprocess.run(GIT+['-c','gpg.ssh.allowedSignersFile='+str(ROOT/policy['allowed_signers']),'verify-commit',commit],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
            result['signature_verified'] = True
            assert protected() == before and config() == config_before
            absent_ref()
            git('update-ref','--no-deref','--stdin',input=('create '+policy['local_ref']+' '+commit+'\n').encode())
            result['ref_created'] = True
            result['ref'] = policy['local_ref']
            assert git('rev-parse',policy['local_ref']).decode().strip()==commit
        assert protected() == before
        result['success'] = True
    except BaseException as error:
        result['error'] = repr(error)
        raise
    finally:
        after = protected()
        result['protected_state_unchanged'] = after == before
        result['manifest_sha256'] = args.manifest
        result['stack_receipt'] = record
        save(output/'POST.json',after)
        save(output/'RESULT.json',result)
        assert after == before


if __name__ == '__main__':
    main()
