import hashlib, json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args): return subprocess.check_output(GIT+list(args),cwd=ROOT,env=ENV)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 with p.open('x') as f: json.dump(v,f,indent=2,sort_keys=True); f.write('\n')
def run(script,*args,log):
 with (HERE/log).open('x') as f:
  subprocess.run([sys.executable,'-I','-S','-B',str(HERE/script),*args],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
assert (HERE/'raw-evidence-receipt.json').exists()
run('commit.py',str(HERE/'normative-research-selection.json'),log='normative-research-driver.log')
run('snapshot.py',log='snapshot-driver.log')
receipts={n:json.loads((HERE/(n+'-receipt.json')).read_text()) for n in ['raw-tools','raw-evidence','normative-research']}
snapshot=ROOT/'artifacts/css-unfinished-work-checkpoint-20261027-v7'
check=json.loads((snapshot/'CHECK.json').read_text())
lines=['# Signed research checkpoint', '', '| Commit | Work |', '| --- | --- |']
for n,description in [('raw-tools','Frozen browser comparison and isolated commit tooling'),('raw-evidence','Original/candidate evidence, failed acceptance gate, 20 passing native tests'),('normative-research','EOF oracle correction, revised 73-target proposal and numeric spec trace')]:
 lines.append('| '+receipts[n]['commit']+' | '+description+' |')
lines += ['', 'Accepted fixes remain 136; held repair 120 is excluded. No new native bugfix is accepted at this checkpoint.', '', 'The raw attribute candidate repaired all 13 original target failures but failed one historical EOF expectation. The revised expectation has two independent spec traces and seven additional controls. The new 73-target fixture requires a fresh paired browser run before accepting the repair. The saved 66-target comparison remains failed; its 329 regression assertions and six reftests passed. All 20 selected native regression tests passed.', '', 'Unfinished implementation and test work remains in the working tree and is also stored in ../css-unfinished-work-checkpoint-20261027-v7/unfinished.patch, with an exact base, source hashes, and verified forward/reverse application. This recovery patch is not an accepted production fix. Unrelated directories, the nested Lean repository and build products are excluded.', '', 'Continue from CURRENT-EPOCH.json in this signing directory, synchronized to the raw native runtime after final signing. Source remains the compiled, unaccepted raw candidate. The live historical attr-cycle.html remains unchanged and the proposed new raw WPT is not installed. Prior runtime epochs are historical.', '', 'Next: freeze the revised 73-target comparison, rebuild and run original/candidate, then commit any accepted native repair with only cascade.rs and its two WPT files. Keep fix 137 as the explicit prerequisite.']
(HERE/'CHECKPOINT.md').write_text('\n'.join(lines)+'\n')
pins={}
for n,h in json.loads((snapshot/'FILES.json').read_text()).items():
 f=snapshot/n;assert sha(f)==h;pins[str(f.relative_to(ROOT))]=h
pins[str((snapshot/'FILES.json').relative_to(ROOT))]=sha(snapshot/'FILES.json')
selected=['commit.py','prepare.py','snapshot.py','finish-signing.py','CHECKPOINT.md','INITIAL-EPOCH.json','snapshot-driver.log']
for ident in receipts:
 selected += [ident+s for s in ['-selection.json','-item.json','-receipt.json','-signature.log','-message.txt','-driver.log']]
for n in selected:
 f=HERE/n;pins[str(f.relative_to(ROOT))]=sha(f)
item={'id':'checkpoint','message':'No bug - Preserve raw attribute research and unfinished verification work. r?#firefox-style-system-reviewers','files':sorted(pins),'source_pins':pins}
save(HERE/'checkpoint-selection.json',item)
run('commit.py',str(HERE/'checkpoint-selection.json'),log='checkpoint-driver.log')
final=json.loads((HERE/'checkpoint-receipt.json').read_text())
assert git('rev-parse','HEAD').decode().strip()==final['commit']
assert not git('diff','--cached','--name-only')
sourcepins=json.loads((snapshot/'SOURCE-PINS.json').read_text())
assert all(sha(ROOT/n)==h for n,h in sourcepins.items())
assert git('-C','artifacts/css-spec-lean','rev-parse','HEAD').decode().strip()=='162b20fb7c53a0ab89b20875a965baee98fb66bb'
for n,h in pins.items():assert hashlib.sha256(git('show','HEAD:'+n)).hexdigest()==h
current=(HERE/'CURRENT-EPOCH.json').read_bytes()
(ROOT/'artifacts/css-attr-raw-nested-native-runtime-v1/CURRENT-EPOCH.json').write_bytes(current)
save(HERE/'FINAL-CHECK.json',{'head':final['commit'],'commits':{n:r['commit'] for n,r in receipts.items()}|{'checkpoint':final['commit']},'signatures_verified':True,'staging_empty':True,'snapshot_source_count':len(sourcepins),'snapshot_hashes_match':True,'unfinished_paths':check['unfinished_count'],'accepted_fixes':136,'raw_repair_accepted':False,'canonical_lean_head_unchanged':True,'current_epoch_sha256':hashlib.sha256(current).hexdigest(),'raw_runtime_epoch_synchronized':True})
print(json.dumps(json.loads((HERE/'FINAL-CHECK.json').read_text()),indent=2),flush=True)
