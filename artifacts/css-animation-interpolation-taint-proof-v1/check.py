import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError('duplicate JSON key')
        result[k] = v
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def expected():
    rows = []
    for procedure, number in enumerate((11, 20, 32)):
        for mode in range(3):
            for a in (False, True):
                for b in (False, True):
                    prefix = f'{len(rows)}|{procedure}|{mode}|{str(a).lower()}|{str(b).lower()}|'
                    rows.append(prefix + (f'ok|{number}|17|{str(a or b).lower()}' if mode == 0 else 'error|-|-|-'))
        for name in ('none-none', 'some-none', 'none-some'):
            rows.append(f'{len(rows)}|{procedure}|{name}|true')
    return '\n'.join(rows) + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    manifest = read(root / 'MANIFEST.json')
    paths = set(manifest)
    assert all(Path(n).as_posix() == n and not Path(n).is_absolute() and '..' not in Path(n).parts for n in paths)
    allowed = paths | {'MANIFEST.json', 'FREEZE.json'}
    directories = {parent.as_posix() for n in allowed for parent in Path(n).parents if parent.as_posix() != '.'}
    seen = set()
    for path in root.rglob('*'):
        name = path.relative_to(root).as_posix()
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            assert name in directories, ('directory', name)
        else:
            assert stat.S_ISREG(mode) and name in allowed, ('entry', name)
            seen.add(name)
    assert seen == allowed
    for name, sha in manifest.items():
        assert digest(root / name) == sha, ('hash', name)
    freeze = read(root / 'FREEZE.json')
    assert digest(root / 'MANIFEST.json') == freeze['manifest_sha256']
    out = Path(args.out).resolve()
    assert out != root and root not in out.parents
    assert not out.exists(), 'fresh output directory required'
    tools = read(root / 'TOOLS.json')
    for tool in ('lean', 'rustc'):
        assert digest(Path(tools[tool]['path'])) == tools[tool]['sha256'], tool
    lean_root = Path(tools['lean']['path']).parent.parent
    for name, sha in read(root / 'TOOLCHAIN-LIBRARY.json').items():
        assert digest(lean_root / name) == sha, name
    out.mkdir(parents=True)
    env = dict(os.environ)
    env.pop('LEAN_PATH', None)
    env.pop('LEAN_SRC_PATH', None)
    env.pop('RUSTFLAGS', None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'

    def run(cmd, log):
        r = subprocess.run(cmd, cwd=out, env=env, text=True, capture_output=True)
        (out / log).write_text(r.stdout + r.stderr)
        assert r.returncode == 0, (cmd, r.returncode, log)
        return r.stdout

    (out / 'Provenance.lean').write_bytes((root / 'Provenance.lean').read_bytes())
    lean = run([tools['lean']['path'], str(out / 'Provenance.lean')], 'lean.log')
    axioms = read(root / 'AXIOMS.json')
    assert lean.splitlines() == axioms, 'exact axiom inventory'
    assert len(axioms) == 15 and 'sorryAx' not in lean
    bindings = read(root / 'BINDINGS.json')
    raw = {}
    for variant in ('candidate', 'omission'):
        source = out / (variant + '.rs')
        run([sys.executable, '-I', str(root / 'native.py'), variant, str(source)], variant + '.generation.log')
        assert read(Path(str(source) + '.bindings.json')) == bindings[variant]
        binary = out / variant
        run([tools['rustc']['path'], '--edition=2021', str(source), '-o', str(binary)], variant + '.compile.log')
        raw[variant] = run([str(binary)], variant + '.rows')
    reference = expected()
    (out / 'oracle.rows').write_text(reference)
    assert raw['candidate'] == reference
    rows = raw['omission'].splitlines()
    reference_rows = reference.splitlines()
    assert len(rows) == len(reference_rows) == 45
    differences = [i for i, (a, b) in enumerate(zip(rows, reference_rows)) if a != b]
    assert differences == [1, 16, 31]
    for i in differences:
        assert rows[i] == reference_rows[i].removesuffix('true') + 'false'
    controls = [reference + 'junk\n', reference.replace('|true', '|2', 1), '\n'.join(reference_rows[:-1]) + '\n']
    assert all(x != reference for x in controls)
    result = {'status': 'pass', 'lean_audits': 15, 'source_definitions_per_variant': 4,
              'native_rows_per_variant': 45, 'candidate_mismatches': 0,
              'compiled_omission_mutant_mismatches': differences, 'strict_row_negative_controls': len(controls),
              'axioms': 'exact AXIOMS.json; only propext and Quot.sound, no sorryAx',
              'boundary': 'full selected wrapper bodies; admitted payload/value/URL adapters, no full Gecko execution'}
    (out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
