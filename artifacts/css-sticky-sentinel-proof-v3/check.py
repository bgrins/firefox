import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def read(path):
    def unique(items):
        value = {}
        for key, item in items:
            require(key not in value, 'duplicate key')
            value[key] = item
        return value
    return json.loads(path.read_text(), object_pairs_hook=unique)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate(root, expected):
    require(sha(root / 'FILES.json') == expected, 'external inventory identity')
    entries = read(root / 'FILES.json')['files']
    names = [row['path'] for row in entries]
    require(len(names) == len(set(names)), 'duplicate path')
    for name in names:
        path = PurePosixPath(name)
        require(not path.is_absolute() and '..' not in path.parts and str(path) == name
                and name not in ['FILES.json','FREEZE.json'], 'canonical path')
    files, dirs = set(), set()
    for base, children, leaves in os.walk(root, followlinks=False):
        for name in children + leaves:
            path = Path(base) / name
            mode = path.lstat().st_mode
            if stat.S_ISREG(mode):
                files.add(path.relative_to(root).as_posix())
            elif stat.S_ISDIR(mode):
                dirs.add(path.relative_to(root).as_posix())
            else:
                raise RuntimeError('nonregular entry')
    require(files == set(names) | {'FILES.json','FREEZE.json'}, 'closed files')
    require(dirs == {str(p) for n in names for p in PurePosixPath(n).parents if str(p) != '.'}, 'closed directories')
    for entry in entries:
        require(sha(root / entry['path']) == entry['sha256'], 'file identity ' + entry['path'])
    seal = read(root / 'FREEZE.json')
    require(seal.get('manifest_sha256', seal.get('files_sha256')) == expected, 'seal binding')
    return len(entries)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest-sha', required=True)
    args = parser.parse_args()
    count = authenticate(ROOT, args.manifest_sha)
    identity = read(ROOT / 'CAPSULE-IDENTITY.json')
    inner = authenticate(ROOT / 'capsule', identity['manifest_sha256'])
    require(sha(ROOT / 'capsule/check.py') == identity['checker_sha256'], 'checker identity')
    require(sha(ROOT / 'capsule/FREEZE.json') == identity['freeze_sha256'], 'inner seal identity')
    a = read(ROOT / 'canonical-v3-complete/RESULT.json')
    require(a == read(ROOT / 'relocated-v3-complete/RESULT.json'), 'replay result drift')
    require(a['audits'] == 167 and a['cases'] == 856 and a['joined_mutants'] == 5, 'required replay roster')
    require(read(ROOT / 'relocated-v3-complete/RELOCATION.json')['exit'] == 0, 'relocation terminal')
    print(json.dumps({'status':'authenticated producer replay evidence; independent acceptance pending',
                      'outer_files':count,'inner_files':inner,'audits':a['audits']}))

if __name__ == '__main__':
    main()
