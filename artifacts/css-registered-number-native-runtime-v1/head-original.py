import copy,hashlib,importlib.util,json,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('raw_state',ROOT/'artifacts/css-attr-raw-nested-native-runtime-v1/state.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
epoch=read(HERE/'CURRENT-EPOCH.json');plan=read(HERE/'RESTORATION-PLAN.json')
assert epoch['semantic_index']['head']==plan['head']
assert set(epoch['modified_native_paths'])==set(plan['paths'])
before=s.a.verify_current(s.h,ROOT,s.ENV,epoch)
flags={n:s.h.git(ROOT/n,s.ENV,'ls-files','-v','-z') for n in ['.','artifacts/css-spec-lean']}
owned={}
for name,pin in plan['paths'].items():
 info=(ROOT/name).lstat();assert stat.S_ISREG(info.st_mode) and [info.st_dev,info.st_ino]==pin['identity']
 assert sha(ROOT/name)==epoch['pins'][name]==sha(HERE/'prototype-original'/name)==pin['prototype_original']
 assert sha(HERE/'head-original'/name)==pin['head_original']
 assert hashlib.sha256(s.h.git(ROOT,s.ENV,'show',plan['head']+':'+name)).hexdigest()==pin['head_original']
 owned[name]={'path':name,'identity':pin['identity'],'owned_sha256':pin['prototype_original']}
s.save(HERE/'head-original-PRE.json',before)
for name,item in owned.items():s.o.write_owned(ROOT,item,(HERE/'head-original'/name).read_bytes())
current=copy.deepcopy(epoch)
for name,pin in plan['paths'].items():
 for key in ['pins','staged_working','committed_research_working_payloads']:
  if name in current[key]:current[key][name]=pin['head_original']
 current['installed_identities'][name]=pin['identity']
index=s.h.index_state(ROOT,s.ENV);semantic=s.h.semantic_index(index)
for key in ['head','entries','cached_diff']:assert semantic[key]==epoch['semantic_index'][key]
current['semantic_index']=semantic;current['raw_index_observation']['current']=index['raw_index']
modified=[n for n in s.h.git(ROOT,s.ENV,'diff','--name-only').decode().splitlines() if not n.startswith('artifacts/')]
assert not modified
current['modified_native_paths']=modified;current['counts']['native_modified_paths']=0;current['counts']['installed_identities']=len(current['installed_identities'])
current['registered_number_transition']={'role':'original','variant':'committed-head','compiled':False,'accepted':False,'last_transition':'head-original'}
current['prototype_overlay_state']={'installed':False,'preserved_epoch':'artifacts/css-registered-number-native-runtime-v1/INITIAL-EPOCH.json','scope':'Tracked native files temporarily restored to committed HEAD. Prior prototype transition records are historical during this phase; untracked files remain preserved.'}
after=s.a.verify_current(s.h,ROOT,s.ENV,current)
assert all(s.h.git(ROOT/n,s.ENV,'ls-files','-v','-z')==body for n,body in flags.items())
s.save(HERE/'head-original-POST.json',after);s.save(HERE/'head-original-EPOCH.json',current)
s.save(HERE/'OWNED.json',owned);s.save(HERE/'ROLE.json',{'role':'original','variant':'committed-head','built':False})
(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
print('Restored exact committed native sources; prototype bodies preserved; build required',flush=True)
