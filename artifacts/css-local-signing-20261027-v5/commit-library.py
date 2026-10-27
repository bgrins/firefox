import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LIB = ROOT / 'artifacts/css-spec-lean'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(*args):
    return subprocess.check_output(GIT + list(args), cwd=LIB, env=ENV)


h = load('preserve', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
epoch = json.loads((HERE / 'INITIAL-EPOCH.json').read_text())
peer = json.loads((ROOT / 'artifacts/css-steps-origin-library-application-terminal-review-v1/CHECK.json').read_text())
assert peer['status'] == 'STEPS_ORIGIN_LIBRARY_TERMINAL_REVIEW_GO'
before = a.verify_current(h, ROOT, ENV, epoch)
save('BEFORE.json', before)
report = json.loads((LIB / '.lake/verification/report.json').read_text())
assert report['status'] == 'pass'
for name, expected in report['source_sha256'].items():
    assert sha(LIB / name) == expected, name
save('LIBRARY-VERIFICATION.json', report)
paths = sorted(raw[3:].decode() for raw in git('status', '--porcelain', '-z', '--untracked-files=all').split(b'\0') if raw and raw[3:] != b'.DS_Store')
postimages = json.loads((ROOT / 'artifacts/css-steps-origin-library-application-runtime-v1/APPLIED.json').read_text())['postimages']
assert set(paths) == set(postimages) and len(paths) == 10
assert {name: sha(LIB / name) for name in paths} == postimages
assert not git('diff', '--cached', '--name-only')
pins = {name: sha(LIB / name) for name in paths}
save('LIBRARY-PINS.json', pins)
(HERE / 'library-preexisting-staging.patch').write_bytes(git('diff', '--cached', '--binary'))
(HERE / 'library-preexisting-working.patch').write_bytes(git('diff', '--binary'))
previous = git('rev-parse', 'HEAD').decode().strip()
assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
git('add', '--', *paths)
assert sorted(git('diff', '--cached', '--name-only').decode().splitlines()) == paths
for name, expected in pins.items():
    assert hashlib.sha256(git('show', ':' + name)).hexdigest() == expected, name
message = 'Model steps() origin-sensitive integer clamping\n\nTransfer the reviewed model and examples into the canonical checker.\nNative refinement and whole-CSS conformance remain open.\n'
(HERE / 'library-message.txt').write_text(message)
with (HERE / 'library-commit.log').open('w') as stream:
    result = subprocess.run(GIT + ['commit', '--file', str(HERE / 'library-message.txt')], cwd=LIB, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
save('LIBRARY-EXECUTION.json', {'exit_code': result.returncode})
assert result.returncode == 0, 'See library-commit.log; preserve staged files on failure'
commit = git('rev-parse', 'HEAD').decode().strip()
assert commit != previous and b'gpgsig ' in git('cat-file', 'commit', commit)
assert git('rev-parse', commit + '^').decode().strip() == previous
assert sorted(git('diff-tree', '--no-commit-id', '--name-only', '-r', commit).decode().splitlines()) == paths
assert git('diff', '--cached', '--name-only') == b''
for name, expected in pins.items():
    assert hashlib.sha256(git('show', commit + ':' + name)).hexdigest() == expected
    assert sha(LIB / name) == expected
key = git('config', '--get', 'user.signingkey').decode().strip()
if key.startswith('key::'):
    key = key[5:]
elif not key.startswith(('ssh-', 'ecdsa-', 'sk-')):
    key = Path(key).expanduser().read_text().strip()
assert key.startswith(('ssh-', 'ecdsa-', 'sk-')) and '\n' not in key
(HERE / 'allowed-signers').write_text('local-checkpoint ' + key + '\n')
with (HERE / 'library-signature.log').open('w') as stream:
    subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(HERE / 'allowed-signers'), 'verify-commit', commit], cwd=LIB, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
current = copy.deepcopy(epoch)
current['nested_semantic_index'] = h.semantic_index(h.index_state(LIB, ENV))
after = a.verify_current(h, ROOT, ENV, current)
save('LIBRARY-AFTER.json', after)
save('LIBRARY-EPOCH.json', current)
(HERE / 'CURRENT-EPOCH.json').write_text(json.dumps(current, indent=2, sort_keys=True) + '\n')
save('LIBRARY-RESULT.json', {'status': 'SIGNED_SOURCE_CHECKPOINT_VERIFIED', 'commit': commit, 'parent': previous, 'files': len(paths), 'source_fingerprints': len(report['source_sha256']), 'signature_verified': True, 'native_sources_and_binaries_preserved': True, 'new_accepted_bugs': 0})
print('Signed CSS library:', commit, 'files:', len(paths), flush=True)
