import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import contextlib
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PROPOSAL = ROOT / 'artifacts/css-attr-non-type-fallback-repair-v3'
PARENT = '4ebfb9861c95d33290f5fb472fddd78de241d043'
WPT = 'testing/web-platform/tests/css/css-values/attr-non-type-used-fallback-cycle.html'
WPT_SHA = '6f966f427d1a6884c0a666e173333d62a26b19ee779dcd70f74b4617d2dbd5a3'
SIGNERS = 'artifacts/css-local-signing-20261027-v1/allowed-signers'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false']
HELPERS = ['artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py',
           'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py']


def digest(body):
    return hashlib.sha256(body).hexdigest()


def sha(path):
    return digest(path.read_bytes())


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def git(*args, env=ENV, cwd=ROOT):
    return subprocess.check_output(GIT + list(args), env=env, cwd=cwd)


def modules():
    result = []
    for index, path in enumerate(HELPERS):
        spec = importlib.util.spec_from_file_location('partial_helper_' + str(index), ROOT / path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result.append(module)
    return result


def flags(env=ENV, cwd=ROOT):
    return {flag: digest(git('ls-files', flag, '-z', env=env, cwd=cwd))
            for flag in ('-v', '-f')}


@contextlib.contextmanager
def isolated_index():
    with tempfile.TemporaryDirectory(prefix='attr-partial-', dir='/private/tmp') as directory:
        directory = Path(directory)
        objects = directory / 'objects'
        objects.mkdir()
        index = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
        shutil.copyfile(index, directory / 'index')
        live_objects = git('rev-parse', '--path-format=absolute', '--git-path', 'objects').decode().strip()
        env = dict(ENV, GIT_INDEX_FILE=str(directory / 'index'),
                   GIT_OBJECT_DIRECTORY=str(objects), GIT_ALTERNATE_OBJECT_DIRECTORIES=live_objects)
        yield env


def staged_plan(env, parent):
    assert git('rev-parse', 'HEAD').decode().strip() == parent
    assert not git('diff', '--cached', '--name-only')
    assert sha(PROPOSAL / 'FILES.json') == '411feb02715ecbc2636fe40fe72b76de330fd535273c49f0581eddc33dc856b1'
    manifest = read(PROPOSAL / 'FILES.json')
    for name, pin in manifest.get('files', manifest).items():
        assert sha(PROPOSAL / name) == (pin['sha256'] if isinstance(pin, dict) else pin), name
    source = read(PROPOSAL / 'SOURCE-PINS.json')['paths']
    paths = sorted([*source, WPT])
    patch = PROPOSAL / 'fix-head.patch'
    git('apply', '--cached', '--check', str(patch), env=env)
    git('apply', '--cached', str(patch), env=env)
    assert git('diff', '--cached', '--name-only', parent, env=env).decode().splitlines() == paths
    blobs = {}
    for name in paths:
        entry = git('ls-files', '--stage', '--', name, env=env).decode().split()
        assert entry[0] == '100644' and entry[2] == '0'
        body = git('show', ':' + name, env=env)
        assert digest(body) == (WPT_SHA if name == WPT else source[name]['candidate_head_sha256'])
        original = git('ls-tree', parent, '--', name).decode().strip()
        blobs[name] = {'mode': entry[0], 'oid': entry[1], 'sha256': digest(body),
                       'parent_entry': original or None}
        if name != WPT:
            assert digest(git('show', parent + ':' + name)) == source[name]['head_sha256']
        else:
            assert not original, 'Fixture must be new at the supplied parent'
    return {'parent': parent, 'tree': git('write-tree', env=env).decode().strip(),
            'paths': paths, 'blobs': blobs, 'patch_sha256': sha(patch),
            'source_pins': source, 'expected_index_flags': flags(env),
            'expected_index_entries': digest(git('ls-files', '--stage', '-z', env=env)),
            'component_pins': {p: sha(ROOT / p) for p in [*HELPERS, SIGNERS]}}, \
        git('diff', '--cached', '--binary', '--full-index', parent, env=env)


def main():
    assert all(not os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
        'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    assert git('symbolic-ref', 'HEAD').decode().strip() == 'refs/heads/stylo-bloom-verification-2'
    h, a = modules()
    mode = sys.argv[1]
    if mode in ('audit', 'prepare'):
        destination = HERE
        parent = PARENT
        epoch = None
        if mode == 'prepare':
            destination = Path(sys.argv[2]).resolve()
            parent = sys.argv[3]
            epoch_path = Path(sys.argv[4]).resolve()
            assert len(parent) == 40 and all(c in '0123456789abcdef' for c in parent)
            assert sha(epoch_path) == sys.argv[5]
            epoch = read(epoch_path)
            assert epoch['semantic_index']['head'] == parent
            epoch_before = a.verify_current(h, ROOT, ENV, epoch)
        before = h.index_state(ROOT, ENV)
        nested = h.index_state(ROOT / 'artifacts/css-spec-lean', ENV)
        before_flags = flags()
        nested_flags = flags(cwd=ROOT / 'artifacts/css-spec-lean')
        with isolated_index() as env:
            plan, patch = staged_plan(env, parent)
            git('apply', '--cached', '--reverse', '--check', str(PROPOSAL / 'fix-head.patch'), env=env)
            git('apply', '--cached', '--reverse', str(PROPOSAL / 'fix-head.patch'), env=env)
            assert git('write-tree', env=env).decode().strip() == git('rev-parse', parent + '^{tree}').decode().strip()
        assert h.index_state(ROOT, ENV) == before and flags() == before_flags
        assert h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == nested
        assert flags(cwd=ROOT / 'artifacts/css-spec-lean') == nested_flags
        if epoch is not None:
            assert a.verify_current(h, ROOT, ENV, epoch) == epoch_before
            assert sha(epoch_path) == sys.argv[5]
            destination.mkdir()
            save(destination / 'PREPARE-EPOCH.json', {'path': str(epoch_path), 'sha256': sha(epoch_path)})
        save(destination / 'PLAN.json', plan)
        (destination / 'staged.patch').write_bytes(patch)
        save(destination / 'AUDIT.json', {'before': before, 'nested': nested,
             'flags': before_flags, 'nested_flags': nested_flags,
             'staged_patch_sha256': digest(patch), 'forward_reverse_transport': True,
             'native_execution': False, 'live_index_and_head_unchanged': True})
        return
    plan_directory = Path(sys.argv[-1]).resolve()
    plan = read(plan_directory / 'PLAN.json')
    for path, pin in plan['component_pins'].items():
        assert sha(ROOT / path) == pin, path
    assert sha(PROPOSAL / 'fix-head.patch') == plan['patch_sha256']
    destination = Path(sys.argv[2]).resolve()
    if mode == 'bind':
        epoch_path = Path(sys.argv[3]).resolve()
        epoch_body = epoch_path.read_bytes()
        assert digest(epoch_body) == sys.argv[4]
        epoch = json.loads(epoch_body)
        before = a.verify_current(h, ROOT, ENV, epoch)
        assert git('config', '--get', 'commit.gpgsign').strip() == b'true'
        for name, pin in plan['source_pins'].items():
            assert sha(ROOT / name) == pin['candidate_live_sha256']
        assert sha(ROOT / WPT) == WPT_SHA
        nested_flags = flags(cwd=ROOT / 'artifacts/css-spec-lean')
        with isolated_index() as env:
            actual, patch = staged_plan(env, plan['parent'])
            assert actual == plan
            assert patch == (plan_directory / 'staged.patch').read_bytes()
            remaining = git('diff', '--binary', '--full-index', env=env)
            modified = git('diff', '--name-only', env=env).decode().splitlines()
        working = {p: h.fingerprint(ROOT, p) for p in set(epoch['modified_native_paths']) | set(plan['paths'])}
        assert a.verify_current(h, ROOT, ENV, epoch) == before
        assert flags(cwd=ROOT / 'artifacts/css-spec-lean') == nested_flags
        destination.mkdir()
        (destination / 'remaining.patch').write_bytes(remaining)
        (destination / 'EPOCH.json').write_bytes(epoch_body)
        save(destination / 'BINDING.json', {'plan_sha256': sha(plan_directory / 'PLAN.json'),
             'epoch_origin': str(epoch_path), 'epoch_sha256': digest(epoch_body), 'before': before,
             'working': working, 'nested_flags': nested_flags,
             'remaining_sha256': digest(remaining), 'remaining_paths': modified,
             'staged_patch_sha256': digest(patch)})
        return
    assert mode == 'verify-after'
    binding = read(destination / 'BINDING.json')
    assert sha(plan_directory / 'PLAN.json') == binding['plan_sha256']
    assert sha(plan_directory / 'staged.patch') == binding['staged_patch_sha256']
    epoch = read(destination / 'EPOCH.json')
    assert sha(destination / 'EPOCH.json') == binding['epoch_sha256']
    commit = git('rev-parse', 'HEAD').decode().strip()
    assert git('rev-list', '--parents', '-n', '1', commit).decode().split() == [commit, plan['parent']]
    assert git('rev-parse', commit + '^{tree}').decode().strip() == plan['tree']
    assert git('diff-tree', '--no-commit-id', '--name-only', '-r', commit).decode().splitlines() == plan['paths']
    for name, value in plan['blobs'].items():
        entry = git('ls-tree', commit, '--', name).decode().split()
        assert entry[:3] == [value['mode'], 'blob', value['oid']]
        assert digest(git('show', commit + ':' + name)) == value['sha256']
    signature = subprocess.run(GIT + ['-c', 'gpg.ssh.allowedSignersFile=' + str(ROOT / SIGNERS),
                               'verify-commit', commit], cwd=ROOT, env=ENV,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert signature.returncode == 0, signature.stdout.decode()
    assert not git('diff', '--cached', '--name-only')
    assert digest(git('ls-files', '--stage', '-z')) == plan['expected_index_entries']
    assert flags() == plan['expected_index_flags']
    assert h.index_state(ROOT / 'artifacts/css-spec-lean', ENV) == binding['before']['nested_index']
    assert flags(cwd=ROOT / 'artifacts/css-spec-lean') == binding['nested_flags']
    assert {p: h.fingerprint(ROOT, p) for p in binding['working']} == binding['working']
    assert digest(git('diff', '--binary', '--full-index')) == binding['remaining_sha256']
    assert git('diff', '--name-only').decode().splitlines() == binding['remaining_paths']
    current = copy.deepcopy(epoch)
    state = h.index_state(ROOT, ENV)
    current['semantic_index'] = h.semantic_index(state)
    current['raw_index_observation']['current'] = state['raw_index']
    current['modified_native_paths'] = [p for p in binding['remaining_paths'] if not p.startswith('artifacts/')]
    current['counts']['native_modified_paths'] = len(current['modified_native_paths'])
    a.verify_current(h, ROOT, ENV, current)
    save(destination / 'POST-EPOCH.json', current)
    save(destination / 'RECEIPT.json', {'commit': commit, 'parent': plan['parent'], 'tree': plan['tree'],
         'signature_verified': True, 'exact_remaining_diff_verified': True,
         'all_epoch_pins_and_working_bodies_preserved': True, 'paths': plan['paths']})
    (destination / 'signature.log').write_bytes(signature.stdout)


if __name__ == '__main__':
    main()
