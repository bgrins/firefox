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
epoch=json.loads((HERE/'CURRENT-EPOCH.json').read_text());before=a.verify_current(h,ROOT,ENV,epoch)
accept=ROOT/'artifacts/css-steps-jump-none-acceptance-v1'
manifest=json.loads((accept/'FILES.json').read_text())
for name,value in manifest.items():
 pin=value['sha256'] if isinstance(value,dict) else value
 assert sha(accept/name)==pin,name
record=json.loads((accept/'ACCEPTANCE.json').read_text());assert record['validation']['observed_repairs']==20
patch=accept/'gecko-wpt.patch';assert sha(patch)==record['patch_sha256']
head=git('rev-parse','HEAD').decode().strip()
with tempfile.TemporaryDirectory(prefix='css-steps-install-',dir='/private/tmp') as tmp:
 env=dict(ENV,GIT_INDEX_FILE=str(Path(tmp)/'index'));git('read-tree',head,env=env)
 git('apply','--cached','--check',str(patch),env=env);git('apply','--cached',str(patch),env=env)
 paths=git('diff','--cached','--name-only',head,env=env).decode().splitlines();assert set(paths)==set(record['paths'])
 bodies={n:git('show',':'+n,env=env) for n in paths}
 for n in paths:
  f=ROOT/n
  tracked=subprocess.run(GIT+['cat-file','-e',head+':'+n],cwd=ROOT,env=ENV,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
  if tracked: assert f.read_bytes()==git('show',head+':'+n),n
  else: assert not f.exists(),n
 for n,b in bodies.items():
  with (ROOT/n).open('wb' if (ROOT/n).exists() else 'xb') as f: f.write(b)
state=h.index_state(ROOT,ENV);current=copy.deepcopy(epoch)
for n in paths:
 current['pins'][n]=h.fingerprint(ROOT,n)
current['semantic_index']=h.semantic_index(state);current['raw_index_observation']['current']=state['raw_index']
current['modified_native_paths']=sorted(n for n in git('diff','--name-only').decode().splitlines() if not n.startswith('artifacts/'))
current['counts']['roles']=len(current['pins']);current['counts']['native_modified_paths']=len(current['modified_native_paths'])
after=a.verify_current(h,ROOT,ENV,current)
save(HERE/'STEPS-INSTALLATION.json',{'fix':133,'status':'ROOT_ACCEPTED_AND_EXACT_SOURCE_INSTALLED','paths':paths,'source_pins':{n:sha(ROOT/n) for n in paths},'patch_sha256':sha(patch),'browser_binary':'Restored original build; candidate was tested before restoration; not rebuilt by signing','root_adopts_acceptance':True,'accepted_manifest_sha256':sha(accept/'FILES.json'),'semantic_index_entries_and_cached_diff_preserved':before['index']['entries']==after['index']['entries'] and before['index']['cached_diff']==after['index']['cached_diff']})
save(HERE/'STEPS-INSTALLED-EPOCH.json',current);(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
print('Accepted fix133 and installed exact four-path source patch',flush=True)
