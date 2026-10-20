import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TRUSTED_SOURCE_PINS = {'source/DOMRect.cpp': '7f3d650772a2053cdac784410c68014a2abb2998e1b1cd4f57430585c7b12cc5', 'source/DOMRect.h': '2874c65025dac6c0291bd63b98c459d7b7e359d7e8c2a11b20231c43fd4d6cc8', 'source/Element.cpp': '951b7d3cd74041417a04109196aa0c89e3f8f37763d0dffcf966a7bceda6943e', 'source/nsLayoutUtils.cpp': '4c8af5a446595014cbd2718436af2da40ac33721a24f987cb3ef0ea16a5fc6e1', 'source/nsLayoutUtils.h': '826ed6b4f2e576b505a35e46f2add1b8b4c6f26a203827978276c2731bfc2bfc', 'source/GeometryUtils.cpp': 'ff3a254b0a5a8e0fb685850d18b1afef49082408f78d1b33bea8e2ba32336ec4', 'source/ResizeObserver.cpp': '72cd6e0e042c8cc7318899e666a1ca803ffe2ddd340080e34c6d4c6fe88efcd8', 'source/ResizeObserver.h': '5b150415cedde4ebed556ad69cccf7bcd19ef4749b28de2f898c56ec3e142845', 'source/Units.h': '0d9740a39441028d4183993c3007d9542761777cadcef865803edae4a405fa10'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    manifest = json.loads((ROOT/'FILES.json').read_text())
    freeze = json.loads((ROOT/'FREEZE.json').read_text())
    assert digest(ROOT/'FILES.json') == freeze['FILES_sha256'], 'FREEZE'
    paths = [r['path'] for r in manifest['files']]
    assert len(paths) == len(set(paths)) == freeze['payload_count'], 'ROSTER_DUPLICATE'
    for name in paths:
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts, 'PATH'
    expected_files = set(paths) | {'FILES.json', 'FREEZE.json'}
    expected_dirs = {str(p) for f in expected_files for p in Path(f).parents if str(p) != '.'}
    actual_files, actual_dirs = set(), set()
    for path in ROOT.rglob('*'):
        assert not path.is_symlink(), 'SYMLINK'
        rel = str(path.relative_to(ROOT))
        assert '__pycache__' not in path.relative_to(ROOT).parts and path.suffix not in ('.pyc', '.olean', '.o'), 'CACHE_OR_COMPILER_PRODUCT'
        if path.is_file(): actual_files.add(rel)
        elif path.is_dir(): actual_dirs.add(rel)
        else: raise AssertionError('SPECIAL_FILE')
    assert actual_files == expected_files, 'CLOSED_FILES'
    assert actual_dirs == expected_dirs, 'CLOSED_DIRECTORIES'
    for row in manifest['files']:
        path = ROOT/row['path']
        assert path.stat().st_size == row['bytes'], 'SIZE'
        assert digest(path) == row['sha256'], 'HASH'
    for path, pin in TRUSTED_SOURCE_PINS.items():
        assert digest(ROOT/path) == pin, 'SOURCE_ROLE_PIN'
    print(json.dumps({'verified': len(paths), 'source_roles': len(TRUSTED_SOURCE_PINS)}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--replay-out', type=Path)
    args = parser.parse_args()
    verify()
    if args.replay_out:
        output = args.replay_out.resolve()
        assert output != ROOT and ROOT not in output.parents, 'REPLAY_OUTSIDE_CAPSULE'
        subprocess.run([sys.executable, '-I', '-S', '-B', str(ROOT/'replay.py'), str(output)], check=True)
