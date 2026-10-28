import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNTIME = ROOT / 'artifacts/css-registered-number-native-runtime-v1'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
read = lambda p: json.loads(p.read_bytes())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT/path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

def save(p, v):
    with p.open('x') as f: json.dump(v,f,indent=2,sort_keys=True); f.write('\n')

s=load('page_sign_state','artifacts/css-registered-number-native-runtime-v1/state.py')
o=load('page_sign_owner','artifacts/css-registered-number-source-transition-v4/transition.py')
epoch=read(HERE/'CURRENT-EPOCH.json')
before=s.a.verify_current(s.h,ROOT,ENV,epoch)
receipts={n:read(HERE/(n+'-receipt.json')) for n in ['provider','random','validation','native-fix']}
parent=read(HERE/'INITIAL-EPOCH.json')['semantic_index']['head']
for n,r in receipts.items():
    assert r['parent']==parent and r['signature_verified'] and r['working_bodies_and_nested_index_preserved']
    assert s.h.git(ROOT,ENV,'rev-parse',r['commit']+'^').decode().strip()==parent
    parent=r['commit']
assert parent==epoch['semantic_index']['head']
assert epoch['modified_native_paths']==['servo/components/style/custom_properties.rs']
acceptance=read(ROOT/'artifacts/css-page-selector-validation-v1/ACCEPTANCE.json')
assert acceptance['status']=='READY_FOR_STANDALONE_SIGNED_COMMIT' and acceptance['fix']==140
payload=read(ROOT/'artifacts/css-page-selector-validation-v1/PAYLOAD.json')
assert acceptance['payload_sha256']==sha(ROOT/'artifacts/css-page-selector-validation-v1/PAYLOAD.json')
validation_pins=read(HERE/'validation-item.json')['source_pins']
assert validation_pins['artifacts/css-page-selector-validation-v1/ACCEPTANCE.json']==sha(ROOT/'artifacts/css-page-selector-validation-v1/ACCEPTANCE.json')
for name,pin in acceptance['evidence_pins'].items(): assert sha(ROOT/name)==pin
assert read(ROOT/'artifacts/css-page-selector-native-runtime-v1/candidate-build-1/RESULT.json')['command_success'] is True
assert read(ROOT/'artifacts/css-page-selector-native-runtime-v1/candidate-build-1/build-RESULT.json')['exit']==0
assert read(ROOT/'artifacts/css-page-selector-validation-v1/LINT.json')['wpt']['exit']==0
assert sorted(receipts['native-fix']['files'])==sorted(payload['files']) and len(payload['files'])==8
for name,pin in payload['source_pins'].items():
    assert sha(ROOT/name)==pin==hashlib.sha256(s.h.git(ROOT,ENV,'show',parent+':'+name)).hexdigest()
    if name in epoch['pins']: assert epoch['pins'][name]==pin
controls={n:(RUNTIME/n).read_bytes() for n in ['CURRENT-EPOCH.json','ROLE.json','OWNED.json']}
for n,b in controls.items(): assert b==(HERE/('PRE-'+n)).read_bytes()
runtime_claim=o.claim(ROOT,str((RUNTIME/'CURRENT-EPOCH.json').relative_to(ROOT)),sha(RUNTIME/'CURRENT-EPOCH.json'))
paths=['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json','artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md','artifacts/css-continuation-roadmap-20261028-v1/PLAN.md']
old={n:(ROOT/n).read_bytes() for n in paths}
for n,b in old.items():
    expected=[epoch[k][n] for k in ['pins','committed_research_working_payloads'] if n in epoch[k]]
    assert expected and all(v==hashlib.sha256(b).hexdigest() for v in expected)
ledger= json.loads(old[paths[0]])
assert ledger['committed_native_fixes']==138 and not any(v.get('fix')==140 for v in ledger['new_queue'])
entry=copy.deepcopy(acceptance['ledger_entry'])
entry.update(native_commit=parent,research_commit=receipts['validation']['commit'],companion_commit=receipts['validation']['commit'],signature_verified=True,status='COMMITTED_NATIVE_WPT')
for key,path in [('acceptance','artifacts/css-page-selector-validation-v1/ACCEPTANCE.json'),('final_build','artifacts/css-page-selector-native-runtime-v1/candidate-build-1/RESULT.json'),('final_validation','artifacts/css-page-selector-print-runtime-candidate-1/ASSESSMENT.json'),('lint','artifacts/css-page-selector-validation-v1/LINT.json')]:
    entry[key]={'path':path,'sha256':sha(ROOT/path)}
entry['commit_verification']={'path':str((HERE/'native-fix-receipt.json').relative_to(ROOT)),'sha256':sha(HERE/'native-fix-receipt.json')}
ledger['new_queue'].append(entry); ledger['committed_native_fixes']=139
ledger['latest_page_selector_fix']=entry
summary=(f"Fix 140 is committed as `{parent}` after verification research `{receipts['validation']['commit']}`. "
         "Page-selector matching and specificity now use the matching name and pseudo-classes on the same selector. "
         "The paired 24-print-test run changes 10 failures to passes and preserves 14 passing controls/regressions. "
         "The standalone commit contains two Rust files and three WPT/reference pairs. Six scoped Lean claims and two false controls support the bucket-filtering argument; no native-refinement or canonical CSS coverage increment is claimed. "
         "Accepted fixes: 139; tracked: 140; held fix 120 remains excluded.\n\n")
plan=old[paths[1]].decode(); title,rest=plan.split('\n',1)
roadmap='''# CSS/Stylo continuation roadmap

'''+summary+'''1. Next browser investigation: registered random syntax backtracking. The sealed v2 probe has 15 cases and 45 snapshots, including literal-initial ordinary declarations. Run against the local Nightly with support checks. Failed alternatives consume a counter outside cssparser rollback in the source; browser confirmation and any repair remain pending. Simple reparsing does not establish random-key churn.
2. Provider readiness: v5 prototype repairs pending invalidated-SCC raw-value visibility found in v4. Its finite witness rejects raw and missing-value false controls. V5 still needs configured native typechecking; production context certification, complete traversal suspension and conservative line-height scheduling remain incomplete. The live partial provider-v5 experiment is a different older prototype and stays unaccepted.
3. Registered initial retention passed configured Rust checking but needs linked-browser preservation tests and full selected-value independence validation. Its stylist base must be rebased over accepted page fix140 before installation.
4. Contextual easing dependency handoff passed Gecko Rust checking; Servo-only paths and six lifecycle WPTs remain unexecuted. CSSWG element-dependent easing policy remains unresolved. Keep generic Sign/Atan2 activation held until consumer contracts are satisfied.
5. Relative finite ModRem/Round zero-basis folding is release-confirmed with nine discrepancies and 45 matching targets. The held two-guard proposal, five-claim witness and 18-WPT proposal still need consumer review, native compilation and paired browser validation.
6. Continue Bloom milestones1–6 and broader CSS-to-implementation verification alongside observable bug discovery. Models, static source reviews and browser comparisons remain distinct evidence. Preserve accepted fixes when restoring prototypes; old source snapshots and rollback recipes require rebasing over fix140. Keep all work local.
'''
planned={paths[0]:(json.dumps(ledger,indent=2)+'\n').encode(),paths[1]:(title+'\n\n'+summary+'Earlier checkpoints below retain their historical counts and pending states.\n\n'+rest.lstrip('\n')).encode(),paths[2]:roadmap.encode()}
backup=HERE/'ledger-preimages';backup.mkdir()
for n,b in old.items():
    p=backup/n; p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
claims={n:o.claim(ROOT,n,hashlib.sha256(b).hexdigest()) for n,b in old.items()}
epoch_claim=o.claim(ROOT,str((HERE/'CURRENT-EPOCH.json').relative_to(ROOT)),sha(HERE/'CURRENT-EPOCH.json'))
current=copy.deepcopy(epoch);changed=[]
try:
    for n,b in planned.items():
        changed.append(n);o.write_owned(ROOT,claims[n],b)
        for key in ['pins','staged_working','committed_research_working_payloads']:
            if n in current[key]:current[key][n]=sha(ROOT/n)
    index=s.h.index_state(ROOT,ENV);semantic=s.h.semantic_index(index)
    assert {k:v for k,v in semantic.items() if k!='working_diff'}=={k:v for k,v in epoch['semantic_index'].items() if k!='working_diff'}
    current['semantic_index']=semantic;current['raw_index_observation']['current']=index['raw_index']
    current['page_selector_transition']['accepted']=True
    current['accepted_page_selector']={'fix':140,'native_commit':parent,'files':payload['source_pins'],'old_restoration_recipes_require_rebase':True}
    assert s.h.index_state(ROOT/'artifacts/css-spec-lean',ENV)==before['nested_index']
    s.a.verify_current(s.h,ROOT,ENV,current)
    o.write_owned(ROOT,epoch_claim,o.encoded(current))
except BaseException:
    for n in reversed(changed):o.write_owned(ROOT,claims[n],old[n])
    restored=copy.deepcopy(epoch);index=s.h.index_state(ROOT,ENV)
    assert s.h.semantic_index(index)==epoch['semantic_index']
    restored['raw_index_observation']['current']=index['raw_index']
    s.a.verify_current(s.h,ROOT,ENV,restored);o.write_owned(ROOT,epoch_claim,o.encoded(restored))
    raise
save(HERE/'ROADMAP-UPDATE.json',{'before':{n:hashlib.sha256(b).hexdigest() for n,b in old.items()},'after':{n:sha(ROOT/n) for n in planned},'native_commit':parent,'accepted':139,'tracked':140,'held_excluded':120})
(HERE/'CHECKPOINT.md').write_text('# Page-selector fix and research checkpoint\n\n'+summary+'The remaining live provider experiment is unaccepted. Earlier recovery snapshots remain unchanged. Accepted page sources must survive future prototype restoration.\n')
files=set(paths)
for n in ['commit.py','finish.py','INITIAL-EPOCH.json','BEFORE.json','PRE-CURRENT-EPOCH.json','PRE-ROLE.json','PRE-OWNED.json','ROADMAP-UPDATE.json','CHECKPOINT.md']:
    files.add(str((HERE/n).relative_to(ROOT)))
for ident in receipts:
    for suffix in ['-selection.json','-item.json','-receipt.json','-signature.log','-message.txt','-commit.log']:
        files.add(str((HERE/(ident+suffix)).relative_to(ROOT)))
files.update(str(p.relative_to(ROOT)) for p in backup.rglob('*') if p.is_file())
pins={n:sha(ROOT/n) for n in sorted(files)}
save(HERE/'checkpoint-selection.json',{'id':'checkpoint','files':sorted(pins),'source_pins':pins,'message':'No bug - Record page selector fix and update CSS verification roadmap. r?#firefox-style-system-reviewers'})
with (HERE/'checkpoint-driver.log').open('x') as f:
    subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'commit.py'),str(HERE/'checkpoint-selection.json')],cwd=ROOT,env=ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
final=read(HERE/'CURRENT-EPOCH.json');s.a.verify_current(s.h,ROOT,ENV,final)
checkpoint=read(HERE/'checkpoint-receipt.json')
assert checkpoint['signature_verified'] and checkpoint['working_bodies_and_nested_index_preserved']
assert checkpoint['parent']==parent and checkpoint['commit']==final['semantic_index']['head']
assert s.h.git(ROOT,ENV,'rev-parse','HEAD').decode().strip()==checkpoint['commit']
assert s.h.git(ROOT,ENV,'rev-parse','HEAD^').decode().strip()==parent
assert final['modified_native_paths']==['servo/components/style/custom_properties.rs']
assert all((RUNTIME/n).read_bytes()==b for n,b in controls.items())
try:
    o.write_owned(ROOT,runtime_claim,(HERE/'CURRENT-EPOCH.json').read_bytes())
    s.a.verify_current(s.h,ROOT,ENV,read(RUNTIME/'CURRENT-EPOCH.json'))
except BaseException as error:
    failures=[]
    try: o.write_owned(ROOT,runtime_claim,controls['CURRENT-EPOCH.json'])
    except BaseException as rollback: failures.append(repr(rollback))
    save(HERE/'SYNCHRONIZATION-FAILURE.json',{'error':repr(error),'rollback_errors':failures,'manual_recovery_required':True,'runtime_epoch_synchronized':False,'signed_head':final['semantic_index']['head'],'note':'Signed commits remain; restored old runtime metadata is not certified against the new HEAD.'})
    raise
assert all((RUNTIME/n).read_bytes()==controls[n] for n in ['ROLE.json','OWNED.json'])
save(HERE/'FINAL-CHECK.json',{'head':final['semantic_index']['head'],'native_commit':parent,'signatures_verified':True,'staging_empty':True,'accepted_fixes':139,'tracked':140,'held_excluded':120,'native_dirty_paths':1,'provider_candidate_accepted':False,'runtime_epoch_synchronized':True,'current_epoch_sha256':sha(RUNTIME/'CURRENT-EPOCH.json')})
print('Signed page-selector fix140 and checkpoint; accepted139, tracked140',flush=True)
