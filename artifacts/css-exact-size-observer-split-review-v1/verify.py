import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
TRUSTED_SOURCE_PINS = {'test-source/svg__extensibility__foreignObject__containing-block.html': '203aaa66a1061f1636cb82f42cd1ce09bf359f7ede9fb2d13caece5f78453740', 'test-source/css__cssom-view__resources__elementsFromPoint.js': '7b916486bd625b2a94c13433e1da67d4d7f991118102929d15ebf8a394433255', 'test-source/css__cssom-view__elementsFromPoint-iframes.html': 'f5fe7ae500b7fe5a3b3f06fb03c31167cf246529e282fe5cb18ecec39b195806', 'test-source/svg__extensibility__foreignObject__getboundingclientrect.html': '3e7d72bc55388753d9485fd85bd2a762633427916da0b609f84de7806cfcc942', 'test-source/intersection-observer__client-rect.html': 'b11821941b70eb9f896bd2296c38cc61e9f46ae1875cd21f813326e30d5f0847', 'test-source/intersection-observer__iframe-root-with-overflow-propagation.html': 'b798dbfa8d427bc67994e5229025a5ad47833c2f293e3ec887f0bb5c76eb7a11', 'test-source/css__css-transforms__preserve-3d-flat-grouping-properties.html': '779d87ab31bf960abceeacf84ae16aa5c82d0f20b2eeacdb41f377140b4b59d3', 'test-source/css__css-transforms__3d-rendering-context-behavior.html': '09474d2c9a873793437db386c677cdfb04b670f355674bb4928fb0361ab81ef2', 'test-source/resize-observer__notify.html': 'c43cdc7e1c1fb58ac77ed84c946abc4b2337f8fba0976bb79226f7a7fdf596df', 'test-source/css__cssom-view__getClientRects-inline-with-block-child.html': '5562cc7e892d4a05bbd6d73ae5601f7860926f37019071ae67eda89d1499ec0b', 'test-source/css__cssom-view__getBoundingClientRect-empty-inline.html': '6b478e587d8db151825bd3aeed6245d2c343500f2716c8c2506ff77219ed3ac9', 'offset-source.cpp': 'f5343a2529b640e677d311e6fbb4aecabe663625ae6bc420760fc77d505f7fc8'}

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
    verify()
    result = subprocess.run([sys.executable, '-I', '-S', '-B', str(ROOT/'numeric.py')], check=True, capture_output=True, text=True)
    assert json.loads(result.stdout) == json.loads((ROOT/'FOUR-VARIANT-NUMERIC.json').read_text()), 'NUMERIC_REPLAY'
    print('numeric matrix reproduced')
