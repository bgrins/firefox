import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--canonical', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    review = Path(__file__).resolve().parent
    source = root / 'artifacts/css-first-order-library-integration-20261110-v1'
    manifest = json.loads((source / 'SOURCE-ONLY.json').read_bytes())
    assert len(manifest) == 50
    for name, expected in manifest.items():
        assert sha((source / name).read_bytes()) == expected, name
    authenticated = {}
    for name, repo in [('BASE.json', args.canonical), ('ORIGINS.json', root)]:
        receipt = json.loads((source / name).read_bytes())
        for path, expected in receipt['authenticated_git_objects'].items():
            data = subprocess.check_output(['git', '-C', str(repo), '-c', 'core.fsmonitor=false', 'show', receipt['commit'] + ':' + path])
            assert sha(data) == expected, (name, path)
        authenticated[name] = len(receipt['authenticated_git_objects'])
    transport = json.loads((source / 'overlay/research/derivation/TRANSPORT.json').read_bytes())
    canonical_paths = set(subprocess.check_output([
        'git', '-C', str(args.canonical), '-c', 'core.fsmonitor=false',
        'ls-tree', '-r', '--name-only', transport['canonical_base']]).decode().splitlines())
    overlay_paths = {p.relative_to(source / 'overlay').as_posix()
                     for p in (source / 'overlay').rglob('*') if p.is_file()}
    assert sorted(canonical_paths & overlay_paths) == ['README.md', 'lakefile.lean']
    accepted = json.loads((source / 'overlay/research/derivation/origin/SOURCE-ONLY.json').read_bytes())
    inverse = {b: a for a, b in transport['module_map'].items()}
    assert len(inverse) == len(transport['module_map']) == 24
    assert {r['source']: r['source_sha256'] for r in transport['records']} == accepted
    assert len({r['installed'] for r in transport['records']}) == 34
    shared = []
    changed_imports = 0
    for record in transport['records']:
        prefix = 'base' if record['shared'] else 'overlay'
        data = (source / prefix / record['installed']).read_bytes()
        assert sha(data) == record['installed_sha256']
        if record['source'].endswith('.lean'):
            def replace(match):
                nonlocal changed_imports
                module = match[1].decode()
                if module in inverse:
                    changed_imports += 1
                    return b'import ' + inverse[module].encode()
                return match[0]
            raw = re.sub(rb'^import ([A-Za-z0-9_.]+)$', replace, data, flags=re.M)
        else:
            raw = data
        assert sha(raw) == record['source_sha256'], record['source']
        signed = subprocess.check_output(['git', '-C', str(root), '-c', 'core.fsmonitor=false', 'show', transport['origin_commit'] + ':' + transport['origin_artifact'] + '/' + record['source']])
        assert raw == signed
        if record['shared']:
            shared.append(record['source'])
            assert not (source / 'overlay' / record['installed']).exists()
    assert sorted(shared) == ['CssSemantics/CssEscape.lean', 'CssSemantics/CssInput.lean']
    commands = []
    with tempfile.TemporaryDirectory(prefix='patch-', dir=review) as directory:
        work = Path(directory)
        shutil.copytree(source / 'base', work, dirs_exist_ok=True)
        for flags in [['--check'], []]:
            process = subprocess.run(['git', 'apply', *flags, str(source / 'integration.patch')], cwd=work, capture_output=True, text=True)
            commands.append({'flags': flags, 'exit': process.returncode, 'output': process.stdout + process.stderr})
            assert process.returncode == 0
        expected = {p.relative_to(source / 'base').as_posix(): p.read_bytes() for p in (source / 'base').rglob('*') if p.is_file()}
        expected.update({p.relative_to(source / 'overlay').as_posix(): p.read_bytes() for p in (source / 'overlay').rglob('*') if p.is_file()})
        actual = {p.relative_to(work).as_posix(): p.read_bytes() for p in work.rglob('*') if p.is_file()}
        assert actual == expected
        base_paths = set(p.relative_to(source / 'base').as_posix() for p in (source / 'base').rglob('*') if p.is_file())
        modified = sorted(p for p in base_paths if actual[p] != (source / 'base' / p).read_bytes())
        assert modified == ['README.md', 'lakefile.lean']
        assert actual['lakefile.lean'] == (source / 'base/lakefile.lean').read_bytes() + b'lean_lib CssDerivation\n'
        modules = {p[:-5].replace('/', '.'): data for p, data in actual.items() if p.endswith('.lean') and p != 'lakefile.lean'}
        closure, external = set(), set()
        def visit(module):
            if module not in modules:
                external.add(module)
                return
            if module in closure:
                return
            closure.add(module)
            for imported in re.findall(rb'^import ([A-Za-z0-9_.]+)$', modules[module], re.M):
                visit(imported.decode())
        visit('CssDerivation')
        assert len(closure) == 22
        assert not any('.Tools.' in m or '.Tests.' in m for m in closure)
        assert not any(re.search(rb'^def main\b', modules[m], re.M) for m in closure)
        lake = json.loads((source / 'LAKE-CLOSURE.json').read_bytes())
        assert sorted(closure) == lake['facade_transitive_local_imports']
        assert sorted(external) == lake['external_imports']
        for name, expected_hash in lake['pinned_lake_sources'].items():
            assert sha((root / name).read_bytes()) == expected_hash
        process = subprocess.run(['git', 'apply', '--reverse', str(source / 'integration.patch')], cwd=work, capture_output=True, text=True)
        assert process.returncode == 0, process.stderr
        remaining = {p.relative_to(work).as_posix(): p.read_bytes() for p in work.rglob('*') if p.is_file()}
        assert remaining == {p.relative_to(source / 'base').as_posix(): p.read_bytes() for p in (source / 'base').rglob('*') if p.is_file()}
    for name, expected_hash in manifest.items():
        assert sha((source / name).read_bytes()) == expected_hash
    result = {'status': 'pass', 'source_manifest_sha256': sha((source / 'SOURCE-ONLY.json').read_bytes()),
              'patch_sha256': sha((source / 'integration.patch').read_bytes()),
              'git_objects_authenticated': authenticated, 'transported_inputs': 34,
              'module_relocations': 24, 'changed_import_lines': changed_imports,
              'shared_dependencies': shared, 'modified_existing_files': modified,
              'overlay_collisions_with_canonical_tree': sorted(canonical_paths & overlay_paths),
              'local_import_closure': sorted(closure), 'external_imports': sorted(external),
              'same_library_collection_count': sum(m.startswith('CssDerivation') for m in closure),
              'patch_forward_and_reverse': commands, 'temporary_files_removed': True,
              'lean_or_lake_execution_by_this_checker': False}
    (review / 'CHECK.json').write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: 50 source inputs; 43 Git objects; 34 reversible transports; 22-module closure; patch forward/reverse')


if __name__ == '__main__':
    main()
