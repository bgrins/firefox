import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def patch_for(root):
    result = ''
    for before in sorted((root / 'original').rglob('*')):
        if before.is_file():
            name = before.relative_to(root / 'original').as_posix()
            result += ''.join(difflib.unified_diff(
                before.read_text().splitlines(True),
                (root / 'candidate' / name).read_text().splitlines(True),
                fromfile='a/' + name, tofile='b/' + name))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest-sha', required=True)
    parser.add_argument('--live-root', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    if digest(root / 'MANIFEST.json') != args.manifest_sha:
        raise SystemExit('manifest authentication failed')
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    for name, expected in manifest['files'].items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise SystemExit('unsafe manifest path')
        path = root / relative
        current = path
        while current != root:
            if current.is_symlink():
                raise SystemExit('symlink input')
            current = current.parent
        if digest(path) != expected:
            raise SystemExit('input authentication failed: ' + name)
    tool = json.loads((root / 'TOOLCHAIN.json').read_text())
    if digest(Path(sys.executable).resolve()) != tool['python_sha256']:
        raise SystemExit('Python executable identity mismatch')

    with tempfile.TemporaryDirectory(prefix='fontface-common-replay-') as directory:
        temp = Path(directory)
        for relative in ['', 'backend']:
            source = root / relative
            target = temp / relative
            target.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source / 'original', target / 'original')
            shutil.copyfile(source / 'prepare.py', target / 'prepare.py')
            subprocess.run([sys.executable, str(target / 'prepare.py')], check=True)
            for expected in sorted((source / 'candidate').rglob('*')):
                if expected.is_file():
                    name = expected.relative_to(source / 'candidate')
                    if (target / 'candidate' / name).read_bytes() != expected.read_bytes():
                        raise SystemExit('candidate regeneration mismatch: ' + str(name))
            patch = 'backend-clone.patch' if relative else 'common.patch'
            if patch_for(target) != (source / patch).read_text():
                raise SystemExit('patch regeneration mismatch: ' + patch)
            if args.live_root:
                for expected in (source / 'original').rglob('*'):
                    if expected.is_file():
                        name = expected.relative_to(source / 'original')
                        if digest(args.live_root / name) != digest(expected):
                            raise SystemExit('live original changed: ' + str(name))
    print(json.dumps({'authenticated_files': len(manifest['files']),
                      'candidate_files': 16, 'patches': 2,
                      'live_originals_checked': bool(args.live_root),
                      'native_compilation': False, 'browser_execution': False}))


if __name__ == '__main__':
    main()
