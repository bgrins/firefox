import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('checkpoint', HERE / 'commit.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert not m.EXECUTION_ENABLED
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def reject(fn):
    try:
        fn()
    except (AssertionError, KeyError, TypeError):
        return
    raise AssertionError('negative control accepted')


def frame(body, kind=b'blob', size=None):
    return b'a' * 40 + b' ' + kind + b' ' + str(len(body) if size is None else size).encode() + b'\n' + body + b'\n'


body = b'embedded\nheader\x00bytes'
record = {'sha256': m.sha(body), 'bytes': len(body)}
for payload in (b'', body, bytes(range(256)) * 5000):
    m.verify_blob(io.BytesIO(frame(payload)), {'sha256': m.sha(payload), 'bytes': len(payload)})
bad_frames = [b'path missing\n', frame(body, b'tree'), frame(body, size=len(body)+1),
              frame(body[:-1]), frame(body).replace(body, b'x' * len(body)),
              frame(body)[:-1] + b'x', frame(body)[:-3], b'x' * 4097,
              frame(body).replace(b'a' * 40, b'g' * 40), frame(body).replace(b'blob 21', b'blob -1')]
bad_frames[-1] = b'a' * 40 + b' blob -1\n' + body + b'\n'
for value in bad_frames:
    reject(lambda value=value: m.verify_blob(io.BytesIO(value), record))


class Writer(io.BytesIO):
    def close(self):
        self.saved = self.getvalue()
        super().close()


class Process:
    def __init__(self, output, exit_code=0):
        self.stdin = Writer()
        self.stdout = io.BytesIO(output)
        self.exit_code = exit_code
        self.done = False
        self.terminated = False

    def wait(self):
        self.done = True
        return self.exit_code

    def poll(self):
        return self.exit_code if self.done else None

    def terminate(self):
        self.terminated = True


original_popen = m.subprocess.Popen
original_temp = m.tempfile.TemporaryFile
captured = []
process = Process(frame(body) + frame(b''))


def fake_popen(command, **kwargs):
    captured.append((command, kwargs))
    return process


m.subprocess.Popen = fake_popen
m.tempfile.TemporaryFile = io.BytesIO
try:
    private_env = {'GIT_INDEX_FILE': 'synthetic-private-index'}
    requests = [('HEAD:artifacts/a', record), (':artifacts/b', {'sha256': m.sha(b''), 'bytes': 0})]
    m.verify_blobs(requests, env=private_env)
    assert len(captured) == 1 and captured[0][0] == m.GIT + ['cat-file', '--batch']
    assert captured[0][1]['env'] is private_env
    assert process.stdin.saved == b'HEAD:artifacts/a\n:artifacts/b\n' and process.done
    wrapper_negatives = 0
    for output, code in [(frame(body)+b'extra',0), (frame(body),1), (b'path missing\n',0)]:
        process = Process(output, code)
        reject(lambda: m.verify_blobs([requests[0]], env=private_env))
        assert process.done and process.stdin.closed and process.stdout.closed
        wrapper_negatives += 1
    before = len(captured)
    for invalid in ('a\nb', 'a\rb', 'a\0b'):
        reject(lambda invalid=invalid: m.verify_blobs([(invalid,record)]))
    m.verify_blobs([])
    assert len(captured) == before
finally:
    m.subprocess.Popen = original_popen
    m.tempfile.TemporaryFile = original_temp

m.saved_admission()
saved = copy.deepcopy(m.BINDINGS)
for change in (lambda b:b.update(head=None), lambda b:b.update(head='invented'),
               lambda b:b.update(epoch_sha256='0'*64), lambda b:b['controls'].update(**{'OWNED.json':'0'*64})):
    m.BINDINGS = copy.deepcopy(saved)
    change(m.BINDINGS)
    m.HEAD = m.BINDINGS['head']
    m.EPOCH = m.BINDINGS['epoch_sha256']
    reject(m.saved_admission)
m.BINDINGS = saved
m.HEAD = saved['head']
m.EPOCH = saved['epoch_sha256']
selected = read(HERE / 'SELECTION.json')
base = read(HERE / 'BASE-SELECTION.json')
assert len(base) == 8516 and all(selected.get(n) == v for n,v in base.items())
for name, pin in selected.items():
    path = m.ROOT / name
    assert path.is_file() and not path.is_symlink()
    assert path.stat().st_size == pin['bytes'] and sha(path) == pin['sha256'], name
for name, digest in saved['completed_packages'].items():
    manifest = m.ROOT / name
    assert sha(manifest) == digest == selected[name]['sha256']
    value = read(manifest)
    for member, pin in value.get('files', value).items():
        path = str((manifest.parent / member).relative_to(m.ROOT))
        assert selected[path]['sha256'] == (pin['sha256'] if isinstance(pin,dict) else pin)


class GitBoundary(Exception):
    pass


def no_git(*args, **kwargs):
    assert args == ('rev-parse','HEAD')
    raise GitBoundary()


m.git = no_git
sys.argv = ['commit.py','--check']
try:
    m.main()
except GitBoundary:
    pass
else:
    raise AssertionError('first Git boundary not reached')
sys.argv = ['commit.py','--run']
reject(m.main)
print(json.dumps({'selected':len(selected),'bytes':sum(v['bytes'] for v in selected.values()),
                  'packages':len(saved['completed_packages']),'seed':len(base),
                  'blob_positives':3,'blob_negatives':10,'wrapper_positive':1,
                  'wrapper_negatives':wrapper_negatives,'unsafe_request_negatives':3,
                  'binding_negatives':4,'saved_admission':True,'first_git_mocked':True,
                  'disabled_run_rejected':True,'actual_git_or_native_operations':False}))
