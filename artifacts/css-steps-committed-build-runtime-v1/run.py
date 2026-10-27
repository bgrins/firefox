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
import signal
inputs=json.loads((HERE/'INPUTS.json').read_text())
assert sha(ROOT/inputs['epoch']['path'])==inputs['epoch']['sha256']
for n,pin in inputs['helpers'].items(): assert sha(HERE/n)==pin
for n in ['GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','CC','CXX','RUSTFLAGS','CARGO_TARGET_DIR','RUSTC','RUSTC_WRAPPER','MOZ_CONFIGURE_OPTIONS','MOZ_ARTIFACT_BUILDS']: assert not os.environ.get(n),n
epoch=json.loads((ROOT/inputs['epoch']['path']).read_text());before=a.verify_current(h,ROOT,ENV,epoch);save(HERE/'BEFORE.json',before)
assert before['index']['head']=='dc8be586a97d4809aa16c8f5260d641359d14c40'
assert h.fingerprint(ROOT,'servo/components/style/values/specified/easing.rs')=='1568dd7d03e09e18a71911c38fbaaa908822fa516220c38842cee6a57350c298'
builder=load('builder',str((HERE/'build.py').relative_to(ROOT)));control=load('control',str((HERE/'process_control.py').relative_to(ROOT)))
stop=[False]
def cancelled(signum,frame):stop[0]=True
for sig in [signal.SIGTERM,signal.SIGINT]:signal.signal(sig,cancelled)
obj=ROOT/'objdir-full.noindex';env=dict(ENV,MOZCONFIG=str(ROOT/'mozconfig'),MOZ_OBJDIR=str(obj),MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',MOZ_HEADLESS='1',PYTHONDONTWRITEBYTECODE='1')
state={};error=None
try:builder.run(ROOT,obj,HERE,env,lambda:stop[0],state,control)
except BaseException as e:error=repr(e)
binaries={'objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL','objdir-full.noindex/dist/bin/gtest/XUL'}
assert binaries<=set(epoch['pins'])
current=copy.deepcopy(epoch)
for n in binaries:current['pins'][n]=h.fingerprint(ROOT,n)
assert all(current['pins'][n] for n in binaries)
index=h.index_state(ROOT,ENV);assert h.semantic_index(index)==epoch['semantic_index']
current['raw_index_observation']={'current':index['raw_index'],'before_build':before['index']['raw_index'],'bytes_equal':index['raw_index']==before['index']['raw_index'],'cause_if_changed':'not established'}
after=a.verify_current(h,ROOT,ENV,current);save(HERE/'AFTER.json',after)
save(HERE/'RESULT.json',{'status':'COMMITTED_STEPS_BUILD_PASS' if error is None and not state else 'BUILD_NOT_ACCEPTED','error':error,'outstanding_processes':state,'binaries':{n:current['pins'][n] for n in binaries},'nonbinary_roles_preserved':True,'browser_reexecution':False,'source_fix_commit':'75271a173ba0dda9d63728fa21aa12c91ddd85d1'})
assert error is None and not state
save(HERE/'CURRENT-EPOCH.json',current)
print('Committed steps build passed; source, research and indexes preserved',flush=True)
