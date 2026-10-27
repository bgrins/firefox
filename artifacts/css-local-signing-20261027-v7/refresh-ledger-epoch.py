import copy, hashlib, importlib.util, json, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
old=json.loads((HERE/'CURRENT-EPOCH.json').read_text());new=copy.deepcopy(old)
paths=['artifacts/stylo-bloom-tools/CURRENT-COMMITS.json','artifacts/stylo-bloom-tools/PLAN-OF-RECORD.md','artifacts/stylo-bloom-tools/BUGFIX-COMMITS.md','artifacts/css-fix-readout-20261023/GROUPS.json','artifacts/css-fix-readout-20261023/README.md']
state=h.index_state(ROOT,ENV)
assert all(state[k]==old['semantic_index'][k] for k in ('head','entries','cached_diff'))
assert not h.git(ROOT,ENV,'diff','--cached','--name-only')
changes={}
for p in paths:
 digest=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
 assert p in old['pins'] and p in old['committed_research_working_payloads'] and old['pins'][p]!=digest
 changes[p]={'before':old['pins'][p],'after':digest}
 new['pins'][p]=digest;new['committed_research_working_payloads'][p]=digest
new['semantic_index']=h.semantic_index(state);new['raw_index_observation']['current']=state['raw_index']
a.verify_current(h,ROOT,ENV,new)
with (HERE/'PRE-LEDGER-EPOCH.json').open('x') as f:json.dump(old,f,indent=2);f.write('\n')
with (HERE/'LEDGER-TRANSITION.json').open('x') as f:json.dump({'paths':changes,'all_other_bodies_preserved':True,'head_and_staging_preserved':True},f,indent=2);f.write('\n')
(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(new,indent=2,sort_keys=True)+'\n')
print('Five ledger changes authenticated; all other preserved bodies unchanged')
