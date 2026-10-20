import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise RuntimeError('Use python3 -I -S without optimization')
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import stat
import subprocess

ROOT = Path(__file__).resolve().parent

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate():
    for name in ['FILES.json', 'FREEZE.json']:
        require(stat.S_ISREG((ROOT / name).lstat().st_mode), 'nonregular seal')
    rows = read(ROOT / 'FILES.json')
    files = {'FILES.json', 'FREEZE.json'}
    directories = {''}
    for row in rows:
        name = row['path']
        p = PurePosixPath(name)
        require(name == p.as_posix() and not p.is_absolute() and '..' not in p.parts and name not in files, 'invalid path')
        files.add(name)
        directories.update(str(x) for x in p.parents if str(x) != '.')
    actual, dirs = set(), {''}
    for p in ROOT.rglob('*'):
        mode = p.lstat().st_mode
        name = p.relative_to(ROOT).as_posix()
        if stat.S_ISDIR(mode):
            dirs.add(name)
        else:
            require(stat.S_ISREG(mode), 'nonregular input')
            actual.add(name)
    require(actual == files and dirs == directories, 'closed roster mismatch')
    for row in rows:
        p = ROOT / row['path']
        require(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'input mismatch: ' + row['path'])
    seal = read(ROOT / 'FREEZE.json')
    require(seal['FILES_sha256'] == sha(ROOT / 'FILES.json'), 'seal mismatch')
    for name, digest in read(ROOT / 'AUTHENTICATION.json')['pins'].items():
        require(sha(ROOT / 'capsule' / name) == digest, 'producer external pin')

authenticate()
p = argparse.ArgumentParser()
p.add_argument('--replay', type=Path)
args = p.parse_args()
result = read(ROOT / 'receipts/replay/RESULT.json')
require(result['status'] == 'PASS' and result['audit_count'] == 33, 'replay result')
require(result['calibration']['snapshots'] == 138, 'snapshot count')
require(all(x['pass_gate'] for x in read(ROOT / 'receipts/GUARDS.json')), 'producer guards')
require(all(x['pass'] for x in read(ROOT / 'ADDITIONAL-GUARDS.json')), 'independent guards')
if args.replay:
    output = args.replay.resolve()
    require(output != ROOT and ROOT not in output.parents and not output.exists(), 'fresh external output required')
    command = [sys.executable, '-I', '-S', str(ROOT / 'capsule/check.py'), '--output', str(output)]
    subprocess.run(command, check=True)
    config = read(ROOT / 'capsule/TOOLCHAIN.json')
    env = {k: v for k, v in os.environ.items() if not k.startswith(('LEAN_', 'PYTHON'))}
    env['LEAN_PATH'] = str(output / 'proof')
    command = [config['lean'], str(ROOT / 'Challenges.lean')]
    run = subprocess.run(command, env=env, capture_output=True, text=True)
    (output / 'INDEPENDENT-CHALLENGES.json').write_text(json.dumps({'command': command, 'exit': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr}, indent=2) + '\n')
    require(run.returncode == 0 and not run.stderr and run.stdout.count("'IndependentAfter.") == 10, 'independent kernel challenge')
    authenticate()
print(json.dumps({'status': 'PASS', 'scope': 'conditional until-after refinement and finite source calibration'}))
