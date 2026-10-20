import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require -I -S without optimization')
sys.dont_write_bytecode=True
import hashlib
import json
from pathlib import Path
import re
import stat
ROOT=Path(__file__).resolve().parent
def require(ok,msg):
    if not ok:raise SystemExit(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def authenticate(root,pin):
    require(sha(root/'FILES.json')==pin,'Manifest pin');m=load(root/'FILES.json');dirs={'.'}
    for n in m:
        p=Path(n);require(not p.is_absolute() and '..' not in p.parts and p.as_posix()==n,'Unsafe path');dirs.update(str(x) for x in p.parents)
    seen=set()
    for p in root.rglob('*'):
        n=p.relative_to(root).as_posix();mode=p.lstat().st_mode
        if stat.S_ISDIR(mode):require(n in dirs,'Extra directory')
        else:
            require(stat.S_ISREG(mode),'Nonregular entry');seen.add(n)
            if n in m:require(sha(p)==m[n],'Changed payload')
    require(seen==set(m)|{'FILES.json','FREEZE.json'},'Closed roster')
    return len(m)
def audit(p,names):
    text=p.read_text();rows=re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",text)
    require([n for n,_ in rows]==names,'Audit roster')
    require(all(set(a.strip() for a in ax.split(',') if a.strip())<={'propext','Classical.choice','Quot.sound'} for _,ax in rows),'Audit axioms')
    require(not any(s in text for s in ['error:','warning:','sorryAx']),'Compiler diagnostic')
require(len(sys.argv)==3 and sys.argv[1]=='--files-sha256','External manifest pin required')
count=authenticate(ROOT,sys.argv[2])
authenticate(ROOT/'producer','2e03ab14fb5c0da29fe6f8df4b564d204e536e269aa5131e59572a58a3d55fbf')
authenticate(ROOT/'corrected-producer','ba7e47fdf9896fb713de22d5975772157209b94dec6033e3126f84235ec1b25f')
for n in ['ExactTraversalBounds.lean','AUDITS.json']:
    require((ROOT/'producer'/n).read_bytes()==(ROOT/'corrected-producer'/n).read_bytes(),'Semantic refresh delta')
a=(ROOT/'producer/verify.py').read_text();b=(ROOT/'corrected-producer/verify.py').read_text()
require(a.replace('cwd=out,','cwd=HERE,').replace('"cwd": str(out)','"cwd": str(HERE)')==b,'Only cwd/receipt correction')
audit(ROOT/'corrected-replay/compile.stdout',load(ROOT/'producer/AUDITS.json'))
names=['IndependentBounds.'+n for n in re.findall(r'^theorem (\w+)',(ROOT/'Challenges.lean').read_text(),re.M)]
require(len(names)==6,'Independent result count');audit(ROOT/'CHALLENGES.stdout',names)
require(load(ROOT/'replay/COMMAND.json')['exit']==1 and load(ROOT/'corrected-replay/COMMAND.json')['exit']==0 and load(ROOT/'CHALLENGES-COMMAND.json')['exit']==0,'Command evidence')
require('must be contained in root directory' in (ROOT/'replay/compile.stderr').read_text(),'Original failure identity')
require(not (ROOT/'corrected-replay/compile.stderr').read_text() and not (ROOT/'CHALLENGES.stderr').read_text(),'Final stderr')
require(load(ROOT/'v2-verifier.log')['status']=='PASS','Corrected verifier receipt')
print(json.dumps({'status':'PASS','review_payloads':count,'producer_results':9,'independent_results':6,'v1_replay':'historical failure','native_successor':'NOT_APPROVED'}))
