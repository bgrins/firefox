import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replace(source, before, after):
    old = (BASE / before).read_bytes()
    new = (BASE / after).read_bytes()
    if source.count(old) != 1:
        raise ValueError('Replacement target count: ' + before)
    return source.replace(old, new)


def materialize(out):
    manifest = json.loads((BASE / 'NATIVE-v2.json').read_text())
    def original(path):
        return subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show',
                                        manifest['base_commit'] + ':' + path], cwd=ROOT)
    base = original(manifest['generic_path'])
    if sha(base) != manifest['base_sha256']:
        raise ValueError('Original revision mismatch')
    pre = replace(base, **manifest['replacements'][0])
    candidate = replace(pre, **manifest['replacements'][1])
    standalone = replace(base, **manifest['replacements'][1])
    values = {'base': base, 'pre_clamp': pre, 'candidate': candidate, 'standalone': standalone}
    for name, value in values.items():
        if sha(value) != manifest[name + '_sha256']:
            raise ValueError('Reconstruction mismatch: ' + name)
        (out / (name + '-calc.rs')).write_bytes(value)
    for index, (path, expected) in enumerate(manifest['helper_sha256'].items()):
        value = original(path)
        if sha(value) != expected:
            raise ValueError('Helper reconstruction mismatch: ' + path)
        (out / ('helper-' + str(index) + '.rs')).write_bytes(value)
    return manifest, values


if __name__ == '__main__':
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    materialize(out)
