import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require isolated no-site nonoptimized Python')
sys.dont_write_bytecode=True
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
ROOT=Path(__file__).resolve().parent
PRODUCER_PIN='2bd9d96917a87bacaa2c742d8b61b9a60fe511e338d81e481582b22b90291156'
def require(ok,message):
    if not ok:raise SystemExit(message)
def unique(pairs):
    d={}
    for k,v in pairs:
        require(k not in d,'Duplicate JSON key');d[k]=v
    return d
def load(p):return json.loads(p.read_bytes(),object_pairs_hook=unique)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def authenticate(root,pin):
    require(sha(root/'FILES.json')==pin,'Manifest pin')
    files=load(root/'FILES.json');dirs={'.'}
    for name in files:
        p=Path(name);require(not p.is_absolute() and p.as_posix()==name and '..' not in p.parts,'Unsafe name')
        dirs.update(str(x) for x in p.parents)
    actual=set()
    for p in root.rglob('*'):
        rel=p.relative_to(root).as_posix();mode=p.lstat().st_mode
        if stat.S_ISDIR(mode):require(rel in dirs,'Extra directory')
        else:
            require(stat.S_ISREG(mode),'Nonregular file');actual.add(rel)
            if rel in files:require(sha(p)==files[rel],'Changed payload '+rel)
    require(actual==set(files)|{'FILES.json','FREEZE.json'},'Closed payload roster')
    return len(files)
def audit(text,names):
    rows=re.findall(r"'([^']+)' (?:does not depend on any axioms|depends on axioms: \[([^\]]*)\])",text)
    require([n for n,_ in rows]==names,'Exact audit names')
    require(all(set(x.strip() for x in ax.split(',') if x.strip())<={'propext','Quot.sound'} for _,ax in rows),'Audit axioms')
    require('sorryAx' not in text and 'error:' not in text,'Failed audit')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--files-sha256',required=True);parser.add_argument('--replay',action='store_true');parser.add_argument('--output',type=Path);args=parser.parse_args()
    count=authenticate(ROOT,args.files_sha256);authenticate(ROOT/'producer',PRODUCER_PIN)
    names=load(ROOT/'producer/AUDIT-NAMES.json');audit((ROOT/'replay/Audit.stdout').read_text(),names)
    ctext=(ROOT/'Challenges.lean').read_text();cnames=['IndependentPrimary.'+n for n in re.findall(r'^theorem (\w+)',ctext,re.M)]
    require(len(cnames)==12,'Challenge count');audit((ROOT/'CHALLENGES.stdout').read_text(),cnames)
    require(load(ROOT/'CHALLENGES-RESULT.json')['exit']==0,'Challenge exit')
    result=load(ROOT/'replay/RESULT.json');require(result['status']=='PASS' and result['audits']==40 and result['source_bindings']==26 and result['model_mutants']==3,'Producer receipt')
    commands=load(ROOT/'replay/COMMANDS.json');require(len(commands)==10,'Command roster')
    require(all(c['returncode']==0 for c in commands[:7]) and all(c['returncode']!=0 for c in commands[7:]),'Replay command results')
    guards=load(ROOT/'guards/RESULT.json');require(guards['status']=='PASS' and len(guards['controls'])==7 and all(x['exit']!=0 and x['no_output'] for x in guards['controls']),'Integrity receipts')
    binding=subprocess.run([sys.executable,'-I','-S',str(ROOT/'producer/bindings.py')],capture_output=True,text=True)
    require(binding.returncode==0 and json.loads(binding.stdout)['bindings']==26,'Source binding recheck')
    if args.replay:
        require(args.output is not None and args.output.is_absolute(),'Fresh absolute output required')
        out=args.output.resolve();require(not out.exists() and ROOT not in out.parents and out!=ROOT,'External fresh output')
        p=subprocess.run([sys.executable,'-I','-S',str(ROOT/'producer/replay.py'),'--files-sha256',PRODUCER_PIN,'--output',str(out)],capture_output=True,text=True)
        if out.exists():(out/'independent-driver.stdout').write_text(p.stdout);(out/'independent-driver.stderr').write_text(p.stderr)
        require(p.returncode==0,'Fresh producer replay failed')
        tool=load(ROOT/'producer/TOOLCHAIN.json');require(sha(Path(tool['lean']))==tool['sha256'],'Lean identity')
        env=os.environ.copy();env['LEAN_PATH']=str(out)
        p=subprocess.run([tool['lean'],str(ROOT/'Challenges.lean')],env=env,capture_output=True,text=True)
        (out/'IndependentChallenges.stdout').write_text(p.stdout);(out/'IndependentChallenges.stderr').write_text(p.stderr)
        require(p.returncode==0 and not p.stderr,'Fresh challenge compilation');audit(p.stdout,cnames)
    authenticate(ROOT,args.files_sha256)
    print(json.dumps({'status':'PASS','review_payloads':count,'producer_payloads':45,'producer_audits':40,'independent_results':12,'bindings':26,'integrity_negatives':7,'fresh_replay':args.replay,'full_native_projection':'OPEN'}))
if __name__=='__main__':main()
