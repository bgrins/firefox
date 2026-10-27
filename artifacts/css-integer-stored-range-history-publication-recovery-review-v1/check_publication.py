import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.with_name('css-integer-stored-range-history-publication-recovery-v1') / 'publish.py'
spec = importlib.util.spec_from_file_location('publication_source', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
old, new, branch, backup = 'a' * 40, 'b' * 40, 'refs/heads/expected', 'refs/heads/backup'
records = []
for fault in ('none', 'pre-branch', 'pre-head', 'cas-refusal', 'post-branch', 'post-head', 'uncertain-return'):
    state = {'branch': branch, 'head': old, 'attempted': False, 'committed': False}
    if fault == 'pre-branch':
        state['branch'] = 'refs/heads/other'
    if fault == 'pre-head':
        state['head'] = 'c' * 40
    result = {'published': False}
    def git(*args, data=None):
        if args == ('symbolic-ref', 'HEAD'):
            return state['branch'].encode()
        if args == ('rev-parse', 'HEAD'):
            return state['head'].encode()
        assert args == ('update-ref', '--stdin')
        assert data.decode().splitlines() == ['start', 'verify ' + backup + ' ' + old,
            'update ' + branch + ' ' + new + ' ' + old, 'prepare', 'commit']
        state['attempted'] = True
        if fault == 'cas-refusal':
            raise RuntimeError('CAS refused')
        state['committed'] = True
        state['head'] = new
        if fault == 'post-branch':
            state['branch'] = 'refs/heads/other'
        if fault == 'post-head':
            state['head'] = old
        if fault == 'uncertain-return':
            raise RuntimeError('return interrupted after actual ref update')
        return b''
    error = None
    try:
        m.publish(git, branch, backup, old, new, result)
    except RuntimeError as failure:
        error = str(failure)
    assert (error is None) == (fault == 'none')
    if fault.startswith('pre-'):
        assert not state['attempted'] and result['published'] is False
    if fault.startswith('post-'):
        assert state['committed'] and result['published'] is True
    if fault == 'uncertain-return':
        assert state['head'] == new and result['published'] is False
    records.append(dict(fault=fault, error=error, state=state, result=result))
check = dict(status='ACTUAL_PUBLICATION_FUNCTION_INERT_PASS', source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             scenarios=records, git_subprocesses=0, uncertain_publication_requires_actual_head_inspection=True)
(HERE / 'PUBLICATION-CHECK.json').write_text(json.dumps(check, indent=2) + '\n')
print(json.dumps(check))
