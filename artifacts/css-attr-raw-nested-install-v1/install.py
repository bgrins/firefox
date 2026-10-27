import copy, hashlib, importlib.util, json, os, stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
RUNTIME=ROOT/'artifacts/css-attr-raw-nested-native-runtime-v1'
PROPOSAL=ROOT/'artifacts/css-attr-raw-nested-repair-v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
spec=importlib.util.spec_from_file_location('raw_state',RUNTIME/'state.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
assert sha(PROPOSAL/'FILES.json')=='3ec8cab27096244ce30b8cbaea3af19f73c542a5658f9d9b9fbe9c396fd6ba79'
for n,h in read(PROPOSAL/'FILES.json').items():assert sha(PROPOSAL/n)==h
candidate=ROOT/'artifacts/css-attr-raw-nested-wpt-runtime-candidate-2'
assessment=read(candidate/'ASSESSMENT.json');result=read(candidate/'RESULT.json')
assert assessment['complete'] and assessment['execution_preserved'] and assessment['comparison_gate_passed']
assert result['comparison_gate_passed'] and result['execution_error'] is None and result['preservation_error'] is None
assert assessment['capsule_manifest_sha256']=='46eee2d63d2d063f4fdf5f1b48fb8dd9baf2e9d809511d7f46da3819f46caff5'
epoch_path=RUNTIME/'CURRENT-EPOCH.json';epoch=read(epoch_path)
assert epoch['raw_attribute_transition']['role']=='candidate' and epoch['raw_attribute_transition']['compiled']
assert sha(epoch_path)==assessment['epoch_sha256']
before=s.a.verify_current(s.h,ROOT,s.ENV,epoch)
flags={n:s.h.git(ROOT/n,s.ENV,'ls-files','-v','-z') for n in ['.','artifacts/css-spec-lean']}
old='testing/web-platform/tests/css/css-values/attr-cycle.html'
new='testing/web-platform/tests/css/css-values/attr-raw-nested-cycle.html'
assert sha(ROOT/old)=='3affcd49dcbe4980f21f1603a17caaa89b870822e5904fe8c958be1eed170397'
assert not (ROOT/new).exists() and not (ROOT/new).is_symlink()
info=(ROOT/old).lstat();assert stat.S_ISREG(info.st_mode)
owned={'path':old,'identity':[info.st_dev,info.st_ino],'owned_sha256':sha(ROOT/old)}
save(HERE/'PRE.json',before)
save(HERE/'INPUTS.json',{'epoch_sha256':sha(epoch_path),'assessment_sha256':sha(candidate/'ASSESSMENT.json'),'result_sha256':sha(candidate/'RESULT.json'),'old_identity':owned,'new_path_absent':new})
s.o.write_owned(ROOT,owned,(PROPOSAL/'candidate'/old).read_bytes())
with (ROOT/new).open('xb') as f:f.write((PROPOSAL/'candidate'/new).read_bytes())
current=copy.deepcopy(epoch)
for n in [old,new]:
 assert sha(ROOT/n)==sha(PROPOSAL/'candidate'/n)
 info=(ROOT/n).lstat();assert stat.S_ISREG(info.st_mode)
 current['pins'][n]=sha(ROOT/n);current['installed_identities'][n]=[info.st_dev,info.st_ino]
state=s.h.index_state(ROOT,s.ENV);sem=s.h.semantic_index(state)
for k in ['head','entries','cached_diff']:assert sem[k]==epoch['semantic_index'][k]
current['semantic_index']=sem;current['raw_index_observation']['current']=state['raw_index']
current['modified_native_paths']=sorted(set(epoch['modified_native_paths'])|{old})
current['counts']['native_modified_paths']=len(current['modified_native_paths'])
current['counts']['roles']=len(current['pins']);current['counts']['installed_identities']=len(current['installed_identities'])
after=s.a.verify_current(s.h,ROOT,s.ENV,current)
assert all(s.h.git(ROOT/n,s.ENV,'ls-files','-v','-z')==body for n,body in flags.items())
save(HERE/'POST.json',after);save(HERE/'POST-EPOCH.json',current)
epoch_path.write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
save(HERE/'RESULT.json',{'tested_fixtures_installed':{n:sha(ROOT/n) for n in [old,new]},'all_other_state_preserved':True,'native_fix_accepted':False})
print('Installed exact tested fixtures; all other state preserved',flush=True)
