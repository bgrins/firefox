import copy, hashlib, importlib.util, json, os, stat, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args,env=ENV): return subprocess.check_output(GIT+list(args),cwd=ROOT,env=env)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 with p.open('x') as f: json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
epoch=json.loads((HERE/'CURRENT-EPOCH.json').read_text());assert git('rev-parse','HEAD').decode().strip()==epoch['semantic_index']['head']
snapshot=ROOT/'artifacts/css-unfinished-work-checkpoint-20261027-v2'
assert json.loads((snapshot/'CHECK.json').read_text())['status']=='SIGNING_RECOVERY_SNAPSHOT_PASS'
base=json.loads((snapshot/'BASE.json').read_text())
report=HERE/'CHECKPOINT.md';report.write_text(report.read_text()+f"\n[Recovery patch](../css-unfinished-work-checkpoint-20261027-v2/unfinished.patch) preserves {base['paths']} remaining project working files, including {base['allowlisted_additions']} new files. Its exact forward/reverse tree roundtrip passed using temporary Git objects and index; unrelated untracked files were excluded.\n")
files=set(json.loads((HERE/'LEDGER-PATHS.json').read_text()))
selection=json.loads((snapshot/'ARTIFACT-SELECTION.json').read_text());files.update(selection)
for directory in [snapshot,ROOT/'artifacts/css-signing-recovery-preparation-v1']:
 files.update(str(p.relative_to(ROOT)) for p in directory.iterdir() if p.is_file())
for name in ['commit.py','install-steps.py','update-ledger.py','prepare-checkpoint.py','CHECKPOINT.md','LEDGER-PREIMAGES.json','FIRST-ATTEMPT.json','recovery-inputs.json']:
 files.add(str((HERE/name).relative_to(ROOT)))
for name in ['compact-borrow-research','compact-borrow-native','steps-research','steps-native']:
 for suffix in ['-receipt.json','-signature.log']:
  files.add(str((HERE/(name+suffix)).relative_to(ROOT)))
# Select only changed entries, preserving exact body/mode pins.
pins={};modes={}
for name in sorted(files):
 f=ROOT/name;pin=sha(f);mode='100755' if f.stat().st_mode & 0o111 else '100644'
 old=subprocess.run(GIT+['show','HEAD:'+name],cwd=ROOT,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 if old.returncode==0 and hashlib.sha256(old.stdout).hexdigest()==pin: continue
 pins[name]=pin;modes[name]=mode
for name,record in selection.items():
 assert sha(ROOT/name)==record['sha256']
 assert ('100755' if (ROOT/name).stat().st_mode & 0o111 else '100644')==record['mode']
for name in ['artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md','artifacts/css-fix-readout-20261023/README.md',str(report.relative_to(ROOT))]:
 import re
 f=ROOT/name
 for target in re.findall(r'\]\(([^)]+)\)',f.read_text()):
  if '://' not in target and not target.startswith('#'): assert (f.parent/target.split('#')[0]).exists(),(name,target)
item={'id':'signed-work-checkpoint','message':'No bug - Record signed CSS fixes and preserve remaining research.','files':sorted(pins),'source_pins':pins,'source_modes':modes}
save(HERE/'checkpoint-input.json',item)
print('Checkpoint selected',len(pins),'paths; recovery',base['paths'],'files',flush=True)
