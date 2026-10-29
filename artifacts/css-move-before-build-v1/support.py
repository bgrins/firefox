import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def prepare(manifest):
    policy = read(HERE / 'POLICY.json')
    owned = load('move_owned', policy['ownership_helper'])
    owned.authenticate(HERE, manifest)
    for name, pin in policy['references'].items():
        assert sha(ROOT / name) == pin
    owned.authenticate(ROOT / policy['candidate']['directory'], policy['candidate']['sha256'])
    roles = read(HERE / 'SOURCE-ROLES.json')
    assert roles == read(ROOT / policy['candidate']['directory'] / 'SOURCE.json')['files']
    assert set(roles) == set(policy['source_paths']) and len(roles) == 3
    assert not set(roles).intersection(policy['accepted_current_payloads'])
    return policy, owned, roles


def guard(policy, owned, roles):
    original = load('move_prior_guard', policy['guard_helper'])
    result = original.guard(policy, owned, roles)
    for name, expected in policy['preserved_markers'].items():
        assert result[3][name] == expected
    return result


def materialize(policy, owned):
    assert not any(os.environ.get(k) for k in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES'))
    roles = read(HERE / 'SOURCE-ROLES.json')
    patch = ROOT / policy['native_patch']['path']
    assert sha(patch) == policy['native_patch']['sha256']
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
    bases, candidates = {}, {}
    with tempfile.TemporaryDirectory(prefix='css-move-source-', dir='/private/tmp') as directory:
        directory = Path(directory)
        for name, record in roles.items():
            part = Path(name)
            assert not part.is_absolute() and '..' not in part.parts
            body = subprocess.check_output(['git', '--no-optional-locks', 'cat-file', 'blob', record['git_object']], cwd=ROOT, env=env)
            assert hashlib.sha256(body).hexdigest() == record['base_sha256']
            bases[name] = body
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
        subprocess.run(['git', 'apply', '--check', str(patch)], cwd=directory, env=env, check=True)
        subprocess.run(['git', 'apply', str(patch)], cwd=directory, env=env, check=True)
        assert {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()} == set(roles)
        for name, record in roles.items():
            path = directory / name
            assert not path.is_symlink() and sha(path) == record['candidate_sha256']
            candidates[name] = path.read_bytes()
        subprocess.run(['git', 'apply', '--reverse', '--check', str(patch)], cwd=directory, env=env, check=True)
        subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=directory, env=env, check=True)
        assert all((directory / name).read_bytes() == body for name, body in bases.items())
    return bases, candidates
