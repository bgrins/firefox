import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('recovery', HERE / 'publish.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
for name, pin in m.read(HERE / 'REFERENCES.json').items():
    assert m.sha(m.ROOT / name) == pin, name

cases = []
for fault in ('none', 'before-switch', 'before-detach', 'before-head', 'cas-failure', 'after-switch', 'after-head'):
    branch, carrier, new = 'refs/heads/expected', 'c' * 40, 'n' * 40
    state = {'branch': branch, 'head': carrier, 'calls': 0}
    result = {'published': False}
    if fault == 'before-switch':
        state['branch'] = 'refs/heads/other'
    if fault == 'before-detach':
        state['branch'] = None
    if fault == 'before-head':
        state['head'] = 'x' * 40
    def git(*args, data=None):
        if args == ('symbolic-ref', 'HEAD'):
            if state['branch'] is None:
                raise RuntimeError('detached HEAD')
            return state['branch'].encode()
        if args == ('rev-parse', 'HEAD'):
            return state['head'].encode()
        assert args == ('update-ref', '--stdin')
        assert data.decode().splitlines() == ['start', 'verify refs/heads/backup ' + carrier,
            'update ' + branch + ' ' + new + ' ' + carrier, 'prepare', 'commit']
        if fault == 'cas-failure':
            raise RuntimeError('backup or branch compare-and-swap rejected')
        state['calls'] += 1
        state['head'] = new
        if fault == 'after-switch':
            state['branch'] = 'refs/heads/other'
        if fault == 'after-head':
            state['head'] = carrier
        return b''
    try:
        m.publish(git, branch, 'refs/heads/backup', carrier, new, result)
    except RuntimeError:
        assert fault != 'none'
        assert result['published'] == fault.startswith('after-')
    else:
        assert fault == 'none' and result['published']
    assert state['calls'] == int(fault == 'none' or fault.startswith('after-'))
    cases.append(fault)

def forbidden(*args, **kwargs):
    raise AssertionError('subprocess forbidden')
m.subprocess.check_output = forbidden
m.subprocess.run = forbidden
old_argv, old_env = m.sys.argv, dict(os.environ)
try:
    m.sys.argv = ['publish.py', '--run']
    for name in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'):
        os.environ[name] = '/forbidden'
        try:
            m.main()
        except RuntimeError as error:
            assert str(error) == 'ambient ' + name
        else:
            raise AssertionError('ambient override accepted')
        del os.environ[name]
    try:
        m.main()
    except RuntimeError as error:
        assert str(error) == 'disabled publication recovery'
    else:
        raise AssertionError('disabled execution accepted')
finally:
    m.sys.argv = old_argv
    os.environ.clear()
    os.environ.update(old_env)
print(json.dumps({'status': 'FIX121_PUBLICATION_RECOVERY_STATIC_PASS', 'publication_cases': cases,
    'refusal_cases': 6, 'live_git_calls': 0, 'objects_refs_indices_signatures_written': False}, indent=2))
