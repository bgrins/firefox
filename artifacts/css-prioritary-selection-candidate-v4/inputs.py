import hashlib
import json
from pathlib import PurePosixPath


def bind_inputs(owner_directory, manifest_bytes, manifest_sha256, external_inputs):
    assert hashlib.sha256(manifest_bytes).hexdigest() == manifest_sha256
    owner = PurePosixPath(owner_directory)
    assert not owner.is_absolute() and '..' not in owner.parts
    result = dict(external_inputs)

    def add(path, digest):
        assert path not in result or result[path] == digest
        result[path] = digest

    for name, record in json.loads(manifest_bytes).items():
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts and name != 'FILES.json'
        add(str(owner / path), record['sha256'])
    add(str(owner / 'FILES.json'), manifest_sha256)
    return result
