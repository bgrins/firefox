import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('use python3 -I -S, without optimization')
sys.dont_write_bytecode = True

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

ROOT = Path(__file__).resolve().parent

def require(value, message):
    if not value:
        raise ValueError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def read(name):
    return json.loads((ROOT / name).read_text(), object_pairs_hook=unique)

def authenticate(expected):
    for name in ('FILES.json', 'FREEZE.json'):
        require(stat.S_ISREG((ROOT / name).lstat().st_mode), 'nonregular seal')
    require(digest(ROOT / 'FILES.json') == expected, 'external manifest mismatch')
    files = read('FILES.json')
    require(isinstance(files, dict) and files, 'bad manifest')
    directories = set()
    for name, value in files.items():
        require(isinstance(name, str) and isinstance(value, str), 'bad row')
        path = PurePosixPath(name)
        require(str(path) == name and not path.is_absolute() and
                '..' not in path.parts and name not in ('FILES.json', 'FREEZE.json'),
                'unsafe manifest path')
        require(len(value) == 64 and all(c in '0123456789abcdef' for c in value), 'bad digest')
        directories.update(str(parent) for parent in path.parents if str(parent) != '.')
    found = set()
    def walk(directory):
        for entry in os.scandir(directory):
            path = Path(entry.path)
            relative = path.relative_to(ROOT).as_posix()
            mode = entry.stat(follow_symlinks=False).st_mode
            if stat.S_ISDIR(mode):
                require(relative in directories, 'unexpected directory: ' + relative)
                walk(path)
            else:
                require(stat.S_ISREG(mode), 'nonregular input: ' + relative)
                if relative in ('FILES.json', 'FREEZE.json'):
                    continue
                require(relative in files, 'unexpected file: ' + relative)
                require(digest(path) == files[relative], 'input hash mismatch: ' + relative)
                found.add(relative)
    walk(ROOT)
    require(found == set(files), 'missing input')
    freeze = read('FREEZE.json')
    require(freeze['FILES_sha256'] == expected and
            freeze['check_sha256'] == digest(ROOT / 'verify.py'), 'seal mismatch')
    return files

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--files-sha256', required=True)
    args = parser.parse_args()
    files = authenticate(args.files_sha256)
    pins = read('SOURCE-PINS.json')
    capsule = ROOT / 'relocated-capsule'
    for name, value in pins.items():
        require(digest(capsule / name) == value, 'relocated source pin mismatch')
    payload = json.loads((capsule / 'FILES.json').read_text(), object_pairs_hook=unique)
    expected = set(payload) | {'FILES.json', 'FREEZE.json'}
    observed = {p.relative_to(capsule).as_posix() for p in capsule.rglob('*') if p.is_file()}
    require(observed == expected, 'nested source closure mismatch')
    for name, value in payload.items():
        require(digest(capsule / name) == value, 'relocated payload mismatch')
    for label in ('canonical', 'relocated'):
        result = read(label + '/RESULT.json')
        require(result['result'] == 'PASS' and result['inputs'] == 35 and
                result['audits'] == 74 and result['modules'] == 8 and
                result['inherited_audits'] == 23 and result['semantic_falseclaim_controls'] == 5 and
                result['FILES_sha256'] == pins['FILES.json'], 'replay result mismatch')
        commands = read(label + '/COMMANDS.json')
        require(len(commands) == 13 and all(c['exit'] == 0 for c in commands[:8]) and
                all(c['exit'] != 0 for c in commands[8:]), 'replay command outcome mismatch')
        for c in commands[8:]:
            log = (ROOT / label / (c['label'] + '.stdout')).read_text()
            require('decide' in log and 'is false' in log, 'nonsemantic rejection')
    guards = read('guards/RESULT.json')
    require([x['name'] for x in guards] == ['optimized', 'double-optimized', 'nonisolated',
            'site-enabled', 'preimport-shadow', 'extra-file', 'extra-directory',
            'symlink', 'changed-proof', 'missing-proof', 'nested-output'], 'guard roster mismatch')
    require(all(x['passed'] and x['exit'] != 0 and not x['output_created'] and
                not x['shadow_executed'] for x in guards), 'guard result mismatch')
    require([x['label'] for x in read('COMMANDS.json')] == ['canonical', 'relocated', 'guards'] and
            all(x['exit'] == 0 for x in read('COMMANDS.json')), 'outer commands mismatch')
    cleanup = read('CLEANUP.json')
    require(sum(x['bytes'] for x in cleanup['owned_completed_products_removed']) ==
            cleanup['bytes'] == read('RESULT.json')['cleanup_bytes'], 'cleanup size mismatch')
    print(json.dumps({'result': 'PASS', 'payloads': len(files), 'audits_per_replay': 74,
                      'semantic_rejections_per_replay': 5, 'guards': 11}))

if __name__ == '__main__':
    main()
