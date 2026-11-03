import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SNAPSHOT = ROOT / 'artifacts/css-root-font-cancellation-selective-handoff-candidate-browser-runtime-v1/ARCHIVE-SNAPSHOT.json'
snapshot = json.loads(SNAPSHOT.read_bytes())
APP = Path(snapshot['application'])
SOURCE = ROOT / 'artifacts/css-provider-rebind-lean-probe-v1/provider-rebind.html'
TEST = ROOT / 'testing/web-platform/tests/web-animations/animation-model/keyframe-effects/provider-rebind.html'
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', MOZ_SKIP_PATH_PERFORMANCE_CHECK='1')
sha = lambda body: hashlib.sha256(body).hexdigest()


def save(name, data):
    with (HERE / name).open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write('\n')


def archive():
    owned = Path(snapshot['owned_directory']).stat()
    assert [owned.st_dev, owned.st_ino] == snapshot['owned_identity']
    files = {}
    for directory, dirs, names in os.walk(APP, followlinks=False):
        for name in dirs + names:
            p = Path(directory) / name
            assert not p.is_symlink(), p
        for name in names:
            p = Path(directory) / name
            s = p.stat()
            assert stat.S_ISREG(s.st_mode)
            files[str(p.relative_to(APP))] = {'bytes': s.st_size, 'mode': stat.S_IMODE(s.st_mode), 'sha256': sha(p.read_bytes())}
    assert files == snapshot['files']
    return {'snapshot_sha256': sha(SNAPSHOT.read_bytes()), 'files': len(files), 'bytes': sum(r['bytes'] for r in files.values())}


def index():
    return {label: sha(subprocess.check_output(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', *args], cwd=ROOT, env=ENV)) for label, args in [('head', ['rev-parse', 'HEAD']), ('entries', ['ls-files', '--stage', '-z']), ('staged', ['diff', '--cached', '--binary']), ('working', ['diff', '--binary'])]}


assert not (RUNTIME / 'SOURCE-TRANSITION.lock').exists()
assert not TEST.exists() and not TEST.is_symlink()
controls = {n: (RUNTIME / n).read_bytes() for n in ('CURRENT-EPOCH.json', 'OWNED.json', 'ROLE.json')}
before = index()
save('BEFORE.json', {'archive': archive(), 'index': before, 'controls': {n: sha(b) for n, b in controls.items()}, 'test_sha256': sha(SOURCE.read_bytes())})
body = SOURCE.read_bytes()
with TEST.open('xb') as stream:
    stream.write(body)
identity = (TEST.stat().st_dev, TEST.stat().st_ino)
command = ['/Users/bgrins/venvs/firefox/bin/python', './mach', 'wpt', '--headless', '--binary', str(APP / 'Contents/MacOS/firefox'), '--log-raw', str(HERE / 'wpt-raw.log'), 'web-animations/animation-model/keyframe-effects/provider-rebind.html']
save('COMMAND.json', command)
try:
    with (HERE / 'wpt.log').open('x') as stream:
        result = subprocess.run(command, cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
    save('WPT-RESULT.json', {'exit_code': result.returncode})
finally:
    assert (TEST.stat().st_dev, TEST.stat().st_ino) == identity and TEST.read_bytes() == body
    TEST.unlink()
    assert all((RUNTIME / n).read_bytes() == b for n, b in controls.items())
    assert index() == before
    save('RESTORATION.json', {'archive': archive(), 'semantic_index_and_controls_unchanged': True, 'staged_test_removed': not TEST.exists()})
