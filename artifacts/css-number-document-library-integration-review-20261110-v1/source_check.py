from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAPSULE = ROOT / 'artifacts/css-number-document-library-integration-20261110-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(p):
    return json.loads(p.read_text())


def main():
    manifest = load(CAPSULE / 'SOURCE-ONLY.json')
    assert sha((CAPSULE / 'SOURCE-ONLY.json').read_bytes()) == 'e73b2d189a5c7b20c5d9afa4ddc7edda92db704a6267f88ab5269ac21b18a489'
    assert all(sha((CAPSULE / n).read_bytes()) == h for n, h in manifest.items())
    base = load(CAPSULE / 'BASE.json')
    origins = load(CAPSULE / 'ORIGINS.json')
    origin_bytes = {}
    for data, repo in [(base, ROOT / 'artifacts/css-spec-lean'), (origins, ROOT)]:
        for name, expected in data['authenticated_git_objects'].items():
            raw = subprocess.check_output(['git', '-C', str(repo), '-c', 'core.fsmonitor=false', 'show', data['commit'] + ':' + name])
            assert sha(raw) == expected, name
            if data is base:
                assert raw == (CAPSULE / 'base' / name).read_bytes()
            else:
                origin_bytes[name] = raw
    tree = {str(f.relative_to(CAPSULE / 'base')): f.read_bytes() for f in (CAPSULE / 'base').rglob('*') if f.is_file()}
    overlay = {str(f.relative_to(CAPSULE / 'overlay')): f.read_bytes() for f in (CAPSULE / 'overlay').rglob('*') if f.is_file()}
    modified = sorted(n for n in overlay if n in tree and tree[n] != overlay[n])
    added = sorted(set(overlay) - set(tree))
    assert modified == sorted(['CssDerivation.lean', 'README.md', 'research/derivation/FACADE.json', 'research/derivation/README.md'])
    tree.update(overlay)
    transport = load(CAPSULE / 'overlay/research/derivation/number/TRANSPORT.json')
    source_prefix = 'artifacts/css-number-document-transfer-20261110-v1/'
    source_manifest = json.loads(origin_bytes[source_prefix + 'SOURCE-ONLY.json'])
    assert len(transport['records']) == len(source_manifest) == 62
    assert len({r['source'] for r in transport['records']}) == 62
    assert len({r['installed'] for r in transport['records']}) == 62
    inverse = {v: k for k, v in transport['module_map'].items()}
    assert len(inverse) == len(transport['module_map'])
    changed_imports = 0
    lean_count = 0
    shared = 0
    def reverse(raw):
        result = []
        for line in raw.splitlines(keepends=True):
            match = re.fullmatch(rb'import ([A-Za-z0-9_.]+)\n', line)
            if match and match[1].decode() in inverse:
                result.append(('import ' + inverse[match[1].decode()] + '\n').encode())
            else:
                result.append(line)
        return b''.join(result)
    for record in transport['records']:
        raw = tree[record['installed']]
        accepted = origin_bytes[source_prefix + record['source']]
        assert sha(raw) == record['installed_sha256']
        assert sha(accepted) == record['source_sha256'] == source_manifest[record['source']]
        if record['installed'].endswith('.lean'):
            lean_count += 1
            assert reverse(raw) == accepted
            changed_imports += sum(x != y for x, y in zip(raw.splitlines(), accepted.splitlines()))
        else:
            assert raw == accepted
        if record['shared']:
            shared += 1
            assert record['installed'] not in overlay and raw == (CAPSULE / 'base' / record['installed']).read_bytes()
    review = transport['review_boundary']
    review_raw = tree[review['installed']]
    review_origin = 'artifacts/css-number-document-transfer-review-20261110-v1/Boundary.lean'
    assert reverse(review_raw) == origin_bytes[review_origin]
    review_changes = sum(a != b for a, b in zip(review_raw.splitlines(), origin_bytes[review_origin].splitlines()))
    assert sha(review_raw) == review['installed_sha256'] and review_changes == 1
    compatibility = load(CAPSULE / 'overlay/research/derivation/number/COMPATIBILITY.json')
    assert all(sha(tree[n]) == h == base['authenticated_git_objects'][n] for n, h in compatibility.items())
    assert set(compatibility) == set(base['authenticated_git_objects']) - set(modified)
    registry = json.loads(tree['research/derivation/FACADE.json'])
    old_registry = load(CAPSULE / 'base/research/derivation/FACADE.json')
    assert all(registry[n] == h for n, h in old_registry.items() if n != 'CssDerivation.lean')
    assert tree['CssDerivation.lean'] == (CAPSULE / 'base/CssDerivation.lean').read_bytes() + b'import CssDerivation.Examples.NumberDocument\n'
    visited = set()
    active = set()
    def visit(name):
        if name in visited:
            return
        assert name not in active and name in registry
        active.add(name)
        raw = tree[name]
        assert sha(raw) == registry[name]
        assert '/Tools/' not in name and '/Tests/' not in name
        assert not re.search(rb'(?m)^def main\b', raw)
        for line in raw.splitlines():
            if not line.startswith(b'import '):
                continue
            match = re.fullmatch(rb'import ([A-Za-z0-9_.]+)', line)
            assert match
            module = match[1].decode()
            if module.split('.')[0] in ['CssDerivation', 'CssSemantics']:
                visit(module.replace('.', '/') + '.lean')
            else:
                assert module.split('.')[0] in ['Lean', 'Init', 'Std']
        active.remove(name)
        visited.add(name)
    visit('CssDerivation.lean')
    assert visited == set(registry) and len(visited) == 55
    with tempfile.TemporaryDirectory(prefix='number-integration-review-') as directory:
        work = Path(directory)
        for name in base['authenticated_git_objects']:
            dest = work / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CAPSULE / 'base' / name, dest)
        for reverse_patch in [False, True]:
            cmd = ['patch', '--batch', '-p1', '-i', str(CAPSULE / 'integration.patch')]
            if reverse_patch:
                cmd.append('-R')
            subprocess.run(cmd, cwd=work, capture_output=True, check=True)
            expected = {n: (CAPSULE / 'base' / n).read_bytes() for n in base['authenticated_git_objects']} if reverse_patch else tree
            actual = {str(f.relative_to(work)): f.read_bytes() for f in work.rglob('*') if f.is_file()}
            assert actual == expected
    report = {'status': 'pass', 'source_manifest_sha256': sha((CAPSULE / 'SOURCE-ONLY.json').read_bytes()), 'patch_sha256': sha((CAPSULE / 'integration.patch').read_bytes()), 'canonical_git_objects': len(base['authenticated_git_objects']), 'research_git_objects': len(origins['authenticated_git_objects']), 'accepted_inputs': len(source_manifest), 'accepted_lean_modules': lean_count, 'changed_import_lines': changed_imports, 'review_changed_import_lines': review_changes, 'shared_canonical_modules': shared, 'modified_existing_paths': modified, 'added_paths': len(added), 'unchanged_compatibility_inputs': len(compatibility), 'facade_sources': len(visited), 'facade_excludes_CLI_tests_main': True, 'previous_facade_source_hashes_preserved': True, 'forward_reverse_patch_exact': True, 'canonical_mutations': False}
    (HERE / 'SOURCE-CHECK.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
