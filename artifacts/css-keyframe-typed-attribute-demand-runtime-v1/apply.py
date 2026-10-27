import copy, hashlib, importlib.util, json, os, stat, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
o=load('ownership','artifacts/css-counter-scope-append-comparison-execution-v1/compare.py')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES'))
assert h.git(ROOT,ENV,'symbolic-ref','HEAD').decode().strip()=='refs/heads/stylo-bloom-verification-2'
old=read(ROOT/'artifacts/css-local-signing-20261027-v7/CURRENT-EPOCH.json')
before=a.verify_current(h,ROOT,ENV,old)
save('BASE-EPOCH.json',old);save('BEFORE.json',before)
proposal=ROOT/'artifacts/css-keyframe-typed-attribute-demand-v1'
for directory in [proposal,ROOT/'artifacts/css-keyframe-typed-attribute-demand-review-v1']:
 for name,item in read(directory/'FILES.json').items():assert sha(directory/name)==(item['sha256'] if isinstance(item,dict) else item),name
pre=read(proposal/'LIVE-SOURCE-PINS.json');post=read(proposal/'POSTIMAGES.json')
assert len(pre)==len(post)==5 and set(pre)==set(post)
assert all(sha(ROOT/n)==old['pins'][n]==digest for n,digest in pre.items())
assert all(sha(proposal/'candidate'/n)==digest for n,digest in post.items())
h.git(ROOT,ENV,'apply','--check',str(proposal/'stack-native.patch'))
owned={}
for name in pre:
 for directory,body in [('original',(ROOT/name).read_bytes()),('candidate-v1',(proposal/'candidate'/name).read_bytes())]:
  dest=HERE/directory/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(body)
 info=(ROOT/name).lstat();assert stat.S_ISREG(info.st_mode)
 owned[name]={'path':name,'identity':[info.st_dev,info.st_ino],'owned_sha256':pre[name]}
save('PREIMAGES.json',pre);save('INITIAL-POSTIMAGES.json',post);save('OWNED-BEFORE.json',owned)
flags={str(root.relative_to(ROOT)) or '.':h.git(root,ENV,'ls-files','-v','-z') for root in [ROOT,ROOT/'artifacts/css-spec-lean']}
for name,item in owned.items():o.write_owned(ROOT,item,(proposal/'candidate'/name).read_bytes())
current=copy.deepcopy(old);current['pins'].update(post)
state=h.index_state(ROOT,ENV)
assert all(state[k]==old['semantic_index'][k] for k in ('head','entries','cached_diff'))
current['semantic_index']=h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index']
current['modified_native_paths']=sorted(n for n in h.git(ROOT,ENV,'diff','--name-only').decode().splitlines() if not n.startswith('artifacts/'))
assert set(current['modified_native_paths'])==set(old['modified_native_paths'])| (set(pre)-set(old['untracked_native']))
current['installed_identities'].update({n:item['identity'] for n,item in owned.items()})
current['counts']['native_modified_paths']=len(current['modified_native_paths']);current['counts']['installed_identities']=len(current['installed_identities'])
current['typed_demand_transition']={'sources':post,'normal_producer_enabled':False,'compiled':False,'tests_run':False,'accepted_bug_increment':0}
after=a.verify_current(h,ROOT,ENV,current)
assert all(h.git(ROOT/n,ENV,'ls-files','-v','-z')==body for n,body in flags.items())
save('APPLIED.json',{'owned':owned,'before_head':before['index']['head'],'after':after,'normal_producer_enabled':False,'compiled':False})
save('SOURCE-EPOCH.json',current);save('CURRENT-EPOCH.json',current)
selection=read(ROOT/'artifacts/css-keyframe-provider-resolver-host-runtime-v1/GTEST-SELECTION.json')['candidate']
selection.append('KeyframePresentation.RetainedEndpointPendingProviders')
save('GTEST-SELECTION.json',{'original':selection[:-1],'candidate':selection,'resolver_calls_in_new_test':22})
print('Applied five reviewed source bodies; preserved all other work; not compiled',flush=True)
