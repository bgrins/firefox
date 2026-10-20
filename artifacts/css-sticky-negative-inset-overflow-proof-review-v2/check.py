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
import subprocess

ROOT = Path(__file__).resolve().parent
PRODUCER = ROOT.parent / 'css-sticky-negative-inset-overflow-proof-v2'

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    def unique(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique)

def authenticate(pin):
    require(sha(ROOT / 'FILES.json') == pin, 'external inventory identity')
    entries = read(ROOT / 'FILES.json')['files']
    names = [row['path'] for row in entries]
    require(len(names) == len(set(names)), 'duplicate path')
    for name in names:
        p = PurePosixPath(name)
        require(not p.is_absolute() and '..' not in p.parts and str(p) == name
                and name not in ['FILES.json','FREEZE.json'], 'path')
    files, dirs = set(), set()
    for base, children, leaves in os.walk(ROOT, followlinks=False):
        for name in children + leaves:
            p = Path(base) / name
            mode = p.lstat().st_mode
            if stat.S_ISREG(mode):
                files.add(p.relative_to(ROOT).as_posix())
            elif stat.S_ISDIR(mode):
                dirs.add(p.relative_to(ROOT).as_posix())
            else:
                raise RuntimeError('nonregular entry')
    require(files == set(names) | {'FILES.json','FREEZE.json'}, 'closed files')
    require(dirs == {str(p) for n in names for p in PurePosixPath(n).parents if str(p) != '.'}, 'closed directories')
    for entry in entries:
        require(sha(ROOT / entry['path']) == entry['sha256'], 'file identity')
    require(read(ROOT / 'FREEZE.json')['manifest_sha256'] == pin, 'freeze identity')
    return len(entries)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--manifest-sha', required=True)
    p.add_argument('--challenges-out', type=Path)
    args = p.parse_args()
    count = authenticate(args.manifest_sha)
    v = read(ROOT / 'VERDICT.json')
    for file, key in [('FILES.json','producer_FILES'),('FREEZE.json','producer_FREEZE'),
                      ('REPORT.md','producer_REPORT'),('check.py','producer_checker')]:
        require(sha(PRODUCER / file) == v[key], 'producer external pin')
    for entry in read(ROOT / 'INSPECTED-SOURCES.json')['files']:
        path = ROOT.parents[1] / entry['path']
        require(sha(path) == entry['sha256'], 'inspected source changed')
    for entry in read(ROOT / 'SOURCE-REPLAY-CHECK.json')['root_receipts']:
        path = ROOT.parents[1] / entry['path']
        require(sha(path) == entry['sha256'], 'root replay receipt changed')
    result = read(ROOT / 'challenges-v2/RESULT.json')
    require(result['status'] == 'PASS' and result['independent_results'] == 12, 'challenge result')
    if args.challenges_out:
        out = args.challenges_out.resolve()
        require(not out.exists() and out != ROOT and ROOT not in out.parents, 'new external challenge output')
        subprocess.run([sys.executable,'-I','-S',str(ROOT/'challenges.py'),'--output',str(out)],check=True)
    authenticate(args.manifest_sha)
    print(json.dumps({'verdict':v['verdict'],'files':count,'independent_kernel_results':12,'full_scope_obligations':8}))

if __name__ == '__main__':
    main()
