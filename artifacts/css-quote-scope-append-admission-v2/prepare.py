import copy, hashlib, importlib.util, json, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);spec.loader.exec_module(m);return m
def save(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
h=load('guard','artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch','artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
epoch=json.loads((ROOT/'artifacts/css-quote-scope-append-admission-v1/CURRENT-EPOCH.json').read_text())
state=h.index_state(ROOT,ENV)
assert h.semantic_index(state)==epoch['semantic_index']
oldraw=epoch['raw_index_observation']['current']
assert state['raw_index']!=oldraw
current=copy.deepcopy(epoch)
current['raw_index_observation']['current']=state['raw_index']
current['quote_v1_raw_index_observation']={'before':oldraw,'after':state['raw_index'],'semantic_index_exact':True,'cause':'not established','build_started':False}
flags={name:hashlib.sha256(h.git(path,ENV,'ls-files','-v','-z')).hexdigest() for name,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')]}
verified=a.verify_current(h,ROOT,ENV,current)
assert flags=={name:hashlib.sha256(h.git(path,ENV,'ls-files','-v','-z')).hexdigest() for name,path in [('root',ROOT),('nested',ROOT/'artifacts/css-spec-lean')]}
save('CURRENT-EPOCH.json',current)
save('INDEX-FLAGS.json',flags)
save('RESTORATION.json',{'status':'QUOTE_V1_SOURCE_BINARY_RESTORATION_VERIFIED','failed_outer_session':14090,'failed_outer_exit':1,'failed_outer_terminal':'7273ca','source_and_binaries_exact':True,'semantic_indexes_exact':True,'raw_index_observation':current['quote_v1_raw_index_observation'],'index_flags':flags,'preservation':verified})
print('All source, binaries and semantic staging restored; raw-index-only change recorded.',flush=True)
