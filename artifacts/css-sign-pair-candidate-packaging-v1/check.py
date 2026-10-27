import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
HERE = pathlib.Path(__file__).resolve().parent
BASE = '90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
PROPOSAL = ROOT / 'artifacts/css-sign-zero-font-split-proposal-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def git(cwd, *args):
    result = subprocess.run(['git', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                             *args], cwd=cwd, capture_output=True, check=True)
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    output = pathlib.Path(parser.parse_args().output).resolve()
    assert not output.exists()
    refs = read(HERE / 'REFERENCES.json')
    authenticated = {}
    for name, digest in refs.items():
        path = ROOT / name
        assert sha(path.read_bytes()) == digest, name
        manifest = read(path)
        for entry, expected in manifest.items():
            assert sha((path.parent / entry).read_bytes()) == expected, entry
        authenticated[name] = len(manifest)
    status = read(PROPOSAL / 'STATUS.json')
    roster = read(PROPOSAL / 'ROSTER.json')
    recipes = {role: read(HERE / (role + '-native.draft.json')) for role in ['raw', 'sign']}
    bodies = {}
    scope = {}
    for role, recipe in recipes.items():
        patch = (ROOT / recipe['patch']).read_bytes()
        assert sha(patch) == recipe['patch_sha256']
        paths = re.findall(r'^diff --git a/(\S+) b/\1$', patch.decode(), re.M)
        assert paths == recipe['files']
        assert len(paths) == (4 if role == 'raw' else 2)
        assert len(roster[role]) == recipe['landing_cases'] == (8 if role == 'raw' else 11)
        assert len(set(roster[role])) == len(roster[role])
        assert recipe['execution_enabled'] is False
        assert all(recipe[k] is None for k in ['acceptance', 'expected_head', 'signing_parent',
                                               'commit_hash', 'bug', 'reviewers', 'message'])
        for name in paths:
            candidate = (PROPOSAL / role / name).read_bytes()
            assert sha(candidate) == recipe['source_pins'][name]
            bodies[name] = git(ROOT, 'show', BASE + ':' + name) if name.endswith('.rs') else None
        segments = patch.decode().split('diff --git ')[1:]
        scope[role] = {paths[i]: {
            'hunks': len(re.findall(r'^@@ ', segment, re.M)),
            'added_lines': sum(x.startswith('+') and not x.startswith('+++') for x in segment.splitlines()),
            'removed_lines': sum(x.startswith('-') and not x.startswith('---') for x in segment.splitlines())
        } for i, segment in enumerate(segments)}
    assert set(recipes['raw']['files']).isdisjoint(recipes['sign']['files'])
    assert recipes['sign']['semantic_prerequisite'] == 'raw-native'
    assert recipes['sign']['independently_cherry_pickable_on_tested_base'] is False
    assert status['raw_prerequisite_for_sign'] is True
    combined = (HERE / 'combined-review-only.patch').read_bytes()
    assert combined == (PROPOSAL / 'raw.patch').read_bytes() + (PROPOSAL / 'sign.patch').read_bytes()
    for role in recipes:
        research = read(HERE / (role + '-research.draft.json'))
        assert set(research['files']) == set(research['source_pins'])
        for name, digest in research['source_pins'].items():
            assert sha((ROOT / name).read_bytes()) == digest
    with tempfile.TemporaryDirectory(prefix='sign-pair-transport-') as temporary:
        scratch = pathlib.Path(temporary)
        git(scratch, 'init', '-q')
        for name, body in bodies.items():
            if body is not None:
                path = scratch / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
        def apply(role, reverse=False):
            patch = str(PROPOSAL / (role + '.patch'))
            args = ['apply'] + (['--reverse'] if reverse else [])
            git(scratch, *args, '--check', patch)
            git(scratch, *args, patch)
        def verify_original():
            for name, body in bodies.items():
                path = scratch / name
                assert (path.read_bytes() if path.exists() else None) == body, name
        def verify_role(role):
            for name, digest in recipes[role]['source_pins'].items():
                assert sha((scratch / name).read_bytes()) == digest, name
        apply('raw')
        verify_role('raw')
        apply('raw', True)
        verify_original()
        apply('raw')
        apply('sign')
        verify_role('raw')
        verify_role('sign')
        ordered = {name: sha((scratch / name).read_bytes()) for name in bodies}
        apply('sign', True)
        verify_role('raw')
        apply('raw', True)
        verify_original()
        git(scratch, 'apply', '--check', str(HERE / 'combined-review-only.patch'))
        git(scratch, 'apply', str(HERE / 'combined-review-only.patch'))
        assert {name: sha((scratch / name).read_bytes()) for name in bodies} == ordered
        git(scratch, 'apply', '--reverse', str(HERE / 'combined-review-only.patch'))
        verify_original()
        assert not (scratch / '.git/index').exists()
    assert not scratch.exists()
    result = {
        'status': 'TRANSPORT_VERIFIED_DEPENDENT_SIGN_ACCEPTANCE_UNBOUND',
        'tested_base': BASE, 'authenticated_capsules': authenticated,
        'scope': scope, 'landing_rosters': roster,
        'base_native_sha256': {p: sha(b) for p, b in bodies.items() if b is not None},
        'ordered_postimages': ordered, 'raw_standalone_apply_reverse': True,
        'raw_then_sign_apply_reverse': True, 'combined_matches_ordered': True,
        'scratch_removed': True, 'scratch_index_created': False,
        'native_acceptance': False, 'sign_independent_on_HEAD90_claim': False,
        'terminal_runtime': None, 'terminal_root_receipt': None,
    }
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': result['status'], 'raw_paths': 4, 'sign_paths': 2,
                      'landing_cases': [8, 11], 'scratch_removed': True}))


if __name__ == '__main__':
    main()
