import copy,hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0');GIT=['git','--no-optional-locks','-c','core.fsmonitor=false']
def git(*args):return subprocess.check_output(GIT+list(args),cwd=ROOT,env=ENV)
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def run(script,args,log):
 with (HERE/log).open('x') as f:subprocess.run([sys.executable,'-I','-S','-B',str(script),*args],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
assert (HERE/'native-fix-receipt.json').exists()
epoch=HERE/'CURRENT-EPOCH.json'
run(ROOT/'artifacts/css-attr-raw-nested-ledger-plan-v2/update.py',[
 '--signing-dir',str(HERE),'--acceptance',str(ROOT/'artifacts/css-attr-raw-nested-validation-v2/ACCEPTANCE.json'),
 '--native-receipt',str(HERE/'native-fix-receipt.json'),'--tools-receipt',str(HERE/'raw-tools-receipt.json'),
 '--validation-receipt',str(HERE/'raw-validation-receipt.json'),'--epoch',str(epoch),'--epoch-sha256',sha(epoch),
 '--original-assessment',str(ROOT/'artifacts/css-attr-raw-nested-wpt-runtime-original-2/ASSESSMENT.json'),
 '--candidate-assessment',str(ROOT/'artifacts/css-attr-raw-nested-wpt-runtime-candidate-2/ASSESSMENT.json')],'ledger-update.log')
run(HERE/'commit.py',[str(HERE/'numeric-research-selection.json')],'numeric-research-driver.log')
current=read(epoch);receipts={n:read(HERE/(n+'-receipt.json')) for n in ['raw-tools','raw-validation','native-fix','numeric-research']}
plan='artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md';ledger='artifacts/stylo-bloom-tools/CURRENT-COMMITS.json'
old={n:sha(ROOT/n) for n in [plan,ledger]}
for n,h in old.items():assert any(current[k].get(n)==h for k in ['pins','staged_working','committed_research_working_payloads'])
v=read(ROOT/ledger);v['latest_research_signing']['commits']['numeric-research']=receipts['numeric-research']['commit']
v['latest_registered_number_research']={'status':'MODEL_CHECKED_NATIVE_REPAIR_PENDING','design':'artifacts/css-registered-number-native-repair-design-v2','model':'artifacts/css-registered-number-admission-model-v1','independent_replay':'artifacts/css-registered-number-admission-model-root-replay-v1','audited_declarations':20,'kernel_examples':14,'decisive_false_controls':7,'canonical_coverage_increment':0,'native_refinement_proved':False,'numeric_self_font_cycle_policy':'INCONCLUSIVE'}
(ROOT/ledger).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
text=(ROOT/plan).read_text();title,rest=text.split('\n',1)
paragraph='Next implementation target: registered-number dependencies after selected substitution and real grammar admission. The new isolated model passes 20 audited declarations, 14 kernel examples and seven negative controls, including both lexical-flag entry paths; the independent replay also passes. Preserve valid dimension-cancelling numeric math and pending provider demands. The numeric self-font-cycle default remains unresolved by the reviewed spec. The captured native design and model live in artifacts/css-registered-number-native-repair-design-v2 and artifacts/css-registered-number-admission-model-v1; neither is a native fix or added canonical coverage. Continue production pending-provider integration and retain the Bloom milestones alongside this work.'
(ROOT/plan).write_text(title+'\n\n'+paragraph+'\n'+rest)
spec=importlib.util.spec_from_file_location('raw_state',ROOT/'artifacts/css-attr-raw-nested-native-runtime-v1/state.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
for n in [plan,ledger]:
 for k in ['pins','staged_working','committed_research_working_payloads']:
  if n in current[k]:current[k][n]=sha(ROOT/n)
state=s.h.index_state(ROOT,ENV);current['semantic_index']=s.h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index']
epoch.write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
save(HERE/'RAW-NUMERIC-ROADMAP-UPDATE.json',{'before':old,'after':{n:sha(ROOT/n) for n in old},'numeric_research_commit':receipts['numeric-research']['commit'],'native_fix_count_unchanged':137})
run(HERE/'snapshot.py',[],'snapshot-driver.log')
snapshot=ROOT/'artifacts/css-unfinished-work-checkpoint-20261027-v8'
lines=['# Signed checkpoint after fix 138','','| Commit | Work |','| --- | --- |']
for n,label in [('raw-tools','Revised WPT comparison and partial publication tools'),('raw-validation','Passed paired comparison and independent audit'),('native-fix','Raw nested attribute fix and its two WPTs'),('numeric-research','Registered-number admission model and native repair design')]:lines.append('| '+receipts[n]['commit']+' | '+label+' |')
lines += ['', 'Accepted and committed fixes:137; tracked records:138, with held120 excluded. Fix138 requires fix137. The fresh comparison changes56PASS+17FAIL to73PASS;329 regression assertions and6reftests remain passing. Both builds and installed WPT lint pass. Earlier20 native tests carry forward through identical source and GTest libraries. The old66-target failure is preserved.', '', 'The registered-number Lean artifact has20 audited declarations,14 kernel examples and7 decisive negative controls, independently replayed. It supplies a normalized design contract, not CSS parser or native refinement proof. Canonical coverage counts are unchanged. Next: implement selected substitution and actual registered-number admission before collecting semantic context requirements, preserving valid numeric math and pending demands; retain the unresolved self-font-cycle policy as observation-only.', '', 'Remaining prototypes and the five ledger updates are captured in ../css-unfinished-work-checkpoint-20261027-v8, with exact base, source hashes and forward/reverse patch verification. Native fixes stay separate from this recovery material. The working tree remains available for continuation; unrelated directories are excluded.', '', 'Resume from this signing directory CURRENT-EPOCH.json; the raw native runtime copy is synchronized after final signing. Its old experiment controller and frozen comparison capsules are historical: live WPTs are now installed and fix138 is committed. No Try, push or Phabricator action was taken.']
(HERE/'CHECKPOINT.md').write_text('\n'.join(lines)+'\n')
pins={}
def add(f):
 n=str(f.relative_to(ROOT));h=sha(f)
 existing=subprocess.run(GIT+['show','HEAD:'+n],cwd=ROOT,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 if existing.returncode==0 and hashlib.sha256(existing.stdout).hexdigest()==h:return
 pins[n]=h
for n,h in read(snapshot/'FILES.json').items():
 f=snapshot/n;assert sha(f)==h;add(f)
add(snapshot/'FILES.json')
for n in ['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json','artifacts/css-fix-readout-20261023/GROUPS.json','artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md','artifacts/css-fix-readout-20261023/README.md','artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md']:add(ROOT/n)
for n in ['commit.py','prepare.py','native.py','snapshot.py','finish.py','CHECKPOINT.md','INITIAL-EPOCH.json','RAW-LEDGER-UPDATE.json','RAW-NUMERIC-ROADMAP-UPDATE.json','ledger-update.log','snapshot-driver.log','native-driver.log','native-prepare.log','native-bind.log','native-fix-commit.log','native-fix-verification.log','native-fix-message.txt']:add(HERE/n)
for ident in receipts:
 for suffix in ['-selection.json','-item.json','-receipt.json','-signature.log','-message.txt','-driver.log']:
  f=HERE/(ident+suffix)
  if f.exists():add(f)
for d in ['native-plan','native-binding','raw-ledger-preimages']:
 for f in sorted((HERE/d).rglob('*')):
  if f.is_file():add(f)
save(HERE/'checkpoint-selection.json',{'id':'checkpoint','message':'No bug - Record signed raw attribute repair and numeric verification roadmap. r?#firefox-style-system-reviewers','files':sorted(pins),'source_pins':pins})
run(HERE/'commit.py',[str(HERE/'checkpoint-selection.json')],'checkpoint-driver.log')
final=read(HERE/'checkpoint-receipt.json');assert git('rev-parse','HEAD').decode().strip()==final['commit']
assert not git('diff','--cached','--name-only')
sourcepins=read(snapshot/'SOURCE-PINS.json');assert all(sha(ROOT/n)==h for n,h in sourcepins.items())
assert git('-C','artifacts/css-spec-lean','rev-parse','HEAD').decode().strip()=='162b20fb7c53a0ab89b20875a965baee98fb66bb'
for n,h in pins.items():assert hashlib.sha256(git('show','HEAD:'+n)).hexdigest()==h
ledger_now=read(ROOT/ledger);groups=read(ROOT/'artifacts/css-fix-readout-20261023/GROUPS.json')
assert ledger_now['committed_native_fixes']==groups['accepted']==groups['committed']==137 and groups['tracked']==138
current=epoch.read_bytes();(ROOT/'artifacts/css-attr-raw-nested-native-runtime-v1/CURRENT-EPOCH.json').write_bytes(current)
save(HERE/'FINAL-CHECK.json',{'head':final['commit'],'commits':{n:r['commit'] for n,r in receipts.items()}|{'checkpoint':final['commit']},'signatures_verified':True,'staging_empty':True,'snapshot_source_count':len(sourcepins),'snapshot_hashes_match':True,'snapshot_unfinished_paths':read(snapshot/'CHECK.json')['unfinished_count'],'accepted_fixes':137,'tracked':138,'held_excluded':120,'raw_repair_accepted':True,'canonical_lean_head_unchanged':True,'canonical_coverage_increment':0,'current_epoch_sha256':hashlib.sha256(current).hexdigest(),'raw_runtime_epoch_synchronized':True})
print((HERE/'FINAL-CHECK.json').read_text(),flush=True)
