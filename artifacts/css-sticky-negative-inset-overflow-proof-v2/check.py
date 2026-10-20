import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:raise RuntimeError("Require python3 -I -S without optimization")
sys.dont_write_bytecode=True
import argparse,hashlib,json,stat,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CAPSULE_PINS={'FILES.json': '5681c063bbd21555a538e439ed5400ac77a2a0bdcc1ae73bff9e44b5617b230a', 'FREEZE.json': '718ecd89e1130d5901cfebb9ecb6494f9dcdacd64b3202f7d394d114a62c2151', 'check.py': 'eccda5d6678afc7390acdf9454e247549a8bf0ef4e2f6673080f110b6f139712'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(c,s):
    if not c:raise RuntimeError(s)
def authenticate(pin):
    require(sha(ROOT/'FILES.json')==pin,'outer manifest identity')
    entries=json.loads((ROOT/'FILES.json').read_text())['files'];names=[x['path'] for x in entries]
    require(len(set(names))==len(names),'duplicate outer path')
    for n in names:require(not Path(n).is_absolute() and '..' not in Path(n).parts and str(Path(n))==n and n not in ['FILES.json','FREEZE.json'],'outer path')
    wanted=set(names)|{'FILES.json','FREEZE.json'};dirs={str(p) for n in wanted for p in Path(n).parents if str(p)!='.'};found=set()
    for p in ROOT.rglob('*'):
        n=str(p.relative_to(ROOT));mode=p.lstat().st_mode
        if stat.S_ISDIR(mode):require(n in dirs,'unexpected outer directory '+n)
        else:require(stat.S_ISREG(mode) and n in wanted,'unexpected outer entry '+n);found.add(n)
    require(found==wanted,'missing outer file')
    for e in entries:require(sha(ROOT/e['path'])==e['sha256'],'outer file '+e['path'])
    require(json.loads((ROOT/'FREEZE.json').read_text())['files_sha256']==pin,'outer freeze binding')
    for n,h in CAPSULE_PINS.items():require(sha(ROOT/'capsule'/n)==h,'nested capsule pin '+n)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--manifest-sha',required=True);parser.add_argument('--out');parser.add_argument('--verify-only',action='store_true');args=parser.parse_args()
    authenticate(args.manifest_sha)
    command=[sys.executable,'-I','-S',str(ROOT/'capsule/check.py'),'--manifest-sha',CAPSULE_PINS['FILES.json']]
    if args.verify_only:command+=['--verify-only']
    else:
        require(args.out is not None,'output required');out=Path(args.out).resolve();require(out!=ROOT and ROOT not in out.parents,'output must be outside sealed artifact');command+=['--out',str(out)]
    result=subprocess.run(command);require(result.returncode==0,'capsule replay failed');authenticate(args.manifest_sha)
if __name__=='__main__':main()
