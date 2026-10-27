import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
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
    return subprocess.check_output(GIT + list(args), cwd=ROOT, env=ENV)


groups = [
    ('animation-research', 'No bug - Record animation ownership experiments and validation limits.', '''
css-keyframe-operation-descriptor-post-signing-proposal-v2
css-keyframe-operation-descriptor-post-signing-runtime-v1
css-keyframe-operation-descriptor-capture-runtime-v1
css-keyframe-transition-endpoint-gtest-proposal-v1
css-keyframe-transition-endpoint-gtest-review-v1
css-keyframe-transition-red-runtime-v1
css-keyframe-transition-red-terminal-review-v1
css-keyframe-transition-green-runtime-v1
css-keyframe-transition-green-validation-v1
css-keyframe-transition-red-green-terminal-review-v1
css-keyframe-animation-rule-owner-host-combined-v1
css-keyframe-animation-rule-owner-host-combined-v2
css-keyframe-animation-rule-owner-host-combined-review-v2
css-keyframe-animation-memory-integration-plan-v1
css-keyframe-owner-runtime-v1
css-keyframe-compact-source-borrow-proposal-v1
css-keyframe-compact-source-borrow-proposal-v2
css-keyframe-compact-source-borrow-review-v2
css-keyframe-compact-borrow-unit-runtime-v1
'''.split()),
    ('steps-research', 'No bug - Record calculated steps admission evidence and Lean model.', '''
css-contextual-steps-api-plan-v1
css-steps-jump-none-isolation-v1
css-steps-nan-oracle-trace-v1
css-steps-nan-oracle-trace-v2
css-steps-jump-none-baseline-validation-v1
css-steps-jump-none-repair-v1
css-steps-jump-none-repair-v2
css-steps-jump-none-repair-review-v1
css-steps-jump-none-repair-review-v2
css-steps-origin-clamping-model-v1
'''.split()),
]

h = load('preserve', 'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a = load('epoch', 'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
epoch = json.loads((HERE / 'LIBRARY-EPOCH.json').read_text())
shutil.copyfile(ROOT / 'artifacts/css-variables-computed-name-signing-runtime-v1/commit-item.py', HERE / 'commit-item.py')
results = []
for label, message, directories in groups:
    before = a.verify_current(h, ROOT, ENV, epoch)
    files = {}
    manifests = {}
    for directory in directories:
        folder = ROOT / 'artifacts' / directory
        manifest = folder / 'FILES.json'
        manifests[str(manifest.relative_to(ROOT))] = sha(manifest)
        files[str(manifest.relative_to(ROOT))] = sha(manifest)
        for name, expected in json.loads(manifest.read_text()).items():
            if isinstance(expected, dict):
                expected = expected['sha256']
            path = folder / name
            assert path.resolve().is_relative_to(folder.resolve()) and path.is_file() and not path.is_symlink(), name
            assert sha(path) == expected, str(path)
            files[str(path.relative_to(ROOT))] = expected
    if label == 'animation-research':
        extras = ROOT / 'artifacts/css-keyframe-compact-borrow-unit-runtime-v2'
        for path in extras.iterdir():
            if path.is_file():
                files[str(path.relative_to(ROOT))] = sha(path)
        for name in ['Cargo.toml', 'lib.rs']:
            path = extras / 'crate' / name
            assert path.is_file()
            files[str(path.relative_to(ROOT))] = sha(path)
    else:
        for path in (ROOT / 'artifacts/css-steps-jump-none-baseline-runtime-v1').iterdir():
            assert path.is_file() and not path.is_symlink()
            files[str(path.relative_to(ROOT))] = sha(path)
    tracked = set(git('ls-tree', '-r', '--name-only', 'HEAD', '--', *files).decode().splitlines())
    for name in tracked:
        assert hashlib.sha256(git('show', 'HEAD:' + name)).hexdigest() == files[name], name
        del files[name]
    assert files
    item = {'id': label, 'expected_head': before['index']['head'], 'message': message, 'files': sorted(files), 'source_pins': files}
    save(label + '-item.json', item)
    save(label + '-manifests.json', manifests)
    with (HERE / (label + '-driver.log')).open('w') as stream:
        result = subprocess.run(['python3', '-I', '-S', '-B', str(HERE / 'commit-item.py'), str(HERE / (label + '-item.json'))], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT)
    assert result.returncode == 0, 'See driver log; preserve index on failure'
    commit = git('rev-parse', 'HEAD').decode().strip()
    assert set(git('diff-tree', '--no-commit-id', '--name-only', '-r', commit).decode().splitlines()) == set(files)
    for name, expected in files.items():
        assert hashlib.sha256(git('show', commit + ':' + name)).hexdigest() == expected, name
    with (HERE / (label + '-signature.log')).open('w') as stream:
        subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(HERE / 'allowed-signers'), 'verify-commit', commit], cwd=ROOT, env=ENV, stdout=stream, stderr=subprocess.STDOUT, check=True)
    current = copy.deepcopy(epoch)
    state = h.index_state(ROOT, ENV)
    assert state['working_diff'] == before['index']['working_diff']
    assert state['cached_diff'] == before['index']['cached_diff']
    assert h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == before['nested_index']
    current['semantic_index'] = h.semantic_index(state)
    current['raw_index_observation']['current'] = state['raw_index']
    current['committed_research_working_payloads'].update(files)
    current['counts']['committed_research_payloads'] = len(current['committed_research_working_payloads'])
    after = a.verify_current(h, ROOT, ENV, current)
    save(label + '-AFTER.json', after)
    save(label + '-EPOCH.json', current)
    results.append({'id': label, 'commit': commit, 'files': len(files), 'signature_verified': True, 'native_sources_and_binaries_preserved': True, 'new_accepted_bugs': 0})
    print('Signed', label, commit, 'files', len(files), flush=True)
    epoch = current
save('RESEARCH-RESULTS.json', results)
save('CURRENT-EPOCH.json', epoch)
