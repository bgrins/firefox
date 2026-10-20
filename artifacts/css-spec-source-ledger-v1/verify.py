import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def verify():
    manifest_path = HERE / 'MANIFEST.json'
    freeze = json.loads((HERE / 'FREEZE.json').read_text())
    assert digest(manifest_path.read_bytes()) == freeze['manifest_sha256']
    manifest = json.loads(manifest_path.read_text())
    expected = set()
    for entry in manifest['files']:
        relative = entry['path']
        path = HERE / relative
        assert relative not in expected
        assert not path.is_symlink() and path.resolve().is_relative_to(HERE)
        expected.add(relative)
        data = path.read_bytes()
        assert len(data) == entry['bytes'] and digest(data) == entry['sha256'], relative
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
    assert actual == expected | {'MANIFEST.json', 'FREEZE.json'}, actual ^ expected
    print(json.dumps({'status': 'PASS', 'inputs': len(expected),
                      'bytes': sum(e['bytes'] for e in manifest['files'])}))


if __name__ == '__main__':
    verify()
