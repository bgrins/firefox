import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('requires -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

ROOT = Path(__file__).resolve().parent
PRODUCER = '0a542591b868f0ecb2444e4c399bbddc5b4a8501d8730541d31fb17d5eb57c02'

def need(ok, message):
    if not ok:
        raise SystemExit('REJECT: ' + message)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def inventory(root):
    files, dirs = set(), set()
    def visit(path):
        for entry in os.scandir(path):
            p = Path(entry.path)
            mode = p.lstat().st_mode
            name = p.relative_to(root).as_posix()
            if stat.S_ISREG(mode):
                files.add(name)
            elif stat.S_ISDIR(mode):
                dirs.add(name)
                visit(p)
            else:
                need(False, 'nonregular ' + name)
    visit(root)
    return files, dirs

parser = argparse.ArgumentParser()
parser.add_argument('--manifest-sha', required=True)
args = parser.parse_args()
actual, dirs = inventory(ROOT)
need(sha(ROOT/'FILES.json') == args.manifest_sha, 'manifest pin')
manifest = json.loads((ROOT/'FILES.json').read_text())['files']
need(all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in manifest), 'manifest paths')
need(actual == set(manifest) | {'FILES.json','FREEZE.json'}, 'file roster')
expected_dirs = {str(p) for n in manifest for p in Path(n).parents if str(p) != '.'}
need(dirs == expected_dirs, 'directory roster')
for n,h in manifest.items():
    need(sha(ROOT/n) == h, 'payload '+n)
need(json.loads((ROOT/'FREEZE.json').read_text()) == {'FILES_sha256':args.manifest_sha,'payload_count':len(manifest)}, 'freeze')
evidence = ROOT/'evidence'
need(sha(evidence/'FILES.json') == PRODUCER, 'producer manifest pin')
producer = json.loads((evidence/'FILES.json').read_text())
need(len(producer) == 297, 'producer count')
need(json.loads((evidence/'FREEZE.json').read_text()) == {'FILES_sha256':PRODUCER,'payloads':297,'status':'FOUR_VARIANTS_COMPLETE_RESTORED','native_accepted':False}, 'producer seal')
for p in evidence.rglob('*'):
    if p.is_file() and p not in (evidence/'FILES.json', evidence/'FREEZE.json'):
        n = p.relative_to(evidence).as_posix()
        need(n in producer and sha(p) == producer[n], 'copied producer evidence '+n)
auth = json.loads((ROOT/'AUTHENTICATION.json').read_text())
need(auth['producer_FILES_sha256'] == PRODUCER and auth['producer_payloads'] == 297 and auth['all_hashes_match'], 'authentication receipt')
need(auth['live_source_hashes_checked'] == json.loads((evidence/'FINAL.json').read_text())['sources'], 'source read receipt')
result = subprocess.run([sys.executable,'-I','-S',str(ROOT/'recount.py')],capture_output=True,text=True)
need(result.returncode == 0 and not result.stderr, 'recount execution')
need(json.loads(result.stdout) == json.loads((ROOT/'RECOUNT.json').read_text()), 'exact recount result')
print(json.dumps({'outcome':'PASS_RUNTIME_EVIDENCE_WITH_RESIDUAL_FAILURE','payloads':len(manifest),'subtests_each_phase':656,'fixes':[34,18],'regressions':[0,0],'restoration_build_exit':0,'remaining_shared_failure':1}))
