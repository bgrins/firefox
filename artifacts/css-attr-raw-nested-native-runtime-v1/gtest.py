import copy, hashlib, importlib.util, json, os, signal, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OBJ=ROOT/'objdir-full.noindex'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0',MOZCONFIG=str(ROOT/'mozconfig'),MOZ_OBJDIR=str(OBJ),MOZ_HEADLESS='1',MOZ_SKIP_PATH_PERFORMANCE_CHECK='1',PYTHONDONTWRITEBYTECODE='1')
PYTHON='/Users/bgrins/venvs/firefox/bin/python'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
h=load('preserve',ROOT/'artifacts/css-keyframe-commit-styles-implicit-clean-comparison-v1/compare.py')
a=load('epoch',ROOT/'artifacts/css-keyframe-operation-descriptor-post-signing-proposal-v2/epoch.py')
builder=load('builder',HERE/'phase.py');control=load('control',HERE/'process_control.py')
read=lambda p:json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
assert all(not os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','CC','CXX','RUSTFLAGS','CARGO_TARGET_DIR','RUSTC','RUSTC_WRAPPER','MOZ_CONFIGURE_OPTIONS','MOZ_ARTIFACT_BUILDS'))
label,kind=sys.argv[1:];assert '/' not in label;assert kind == 'gtest'
commands={'export':[PYTHON,'./mach','build','export','-j2'],'binaries':[PYTHON,'./mach','build','binaries','-j2'],'gtest':[PYTHON,'./mach','gtest',':'.join(read(HERE/'GTEST-SELECTION.json')['candidate']),'--jobs=1']}
command=commands[kind]
epoch=read(HERE/'CURRENT-EPOCH.json');before=a.verify_current(h,ROOT,ENV,epoch)
directory=HERE/label;directory.mkdir();save(directory/'PRE.json',before);save(directory/'COMMAND.json',{'command':command,'pid':os.getpid(),'kind':kind})
flags={str(root.relative_to(ROOT)) or '.':h.git(root,ENV,'ls-files','-v','-z') for root in [ROOT,ROOT/'artifacts/css-spec-lean']}
state={};publication_errors=[];stopped=False;deadline=time.monotonic()+900 if kind=='gtest' else None

def stop(signum,frame):
 global stopped
 stopped=True
for sig in (signal.SIGTERM,signal.SIGINT):signal.signal(sig,stop)
error=None
try:builder.run(ROOT,OBJ,directory,ENV,lambda:stopped or (deadline is not None and time.monotonic()>=deadline),state,control,command,publication_errors)
except BaseException as exc:error=repr(exc)
assert not state, 'Owned group remains; leave sources untouched'
current=copy.deepcopy(epoch)
for name in ['objdir-full.noindex/dist/Nightly.app/Contents/MacOS/firefox','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','objdir-full.noindex/dist/Nightly.app/Contents/MacOS/gtest/XUL','objdir-full.noindex/dist/bin/gtest/XUL']:
 assert name in current['pins'];current['pins'][name]=h.fingerprint(ROOT,name)
index=h.index_state(ROOT,ENV)
assert h.semantic_index(index)==epoch['semantic_index']
current['raw_index_observation']['current']=index['raw_index']
after=a.verify_current(h,ROOT,ENV,current)
assert all(h.git(ROOT/n,ENV,'ls-files','-v','-z')==body for n,body in flags.items())
current['raw_attribute_gtest']={'label':label,'kind':kind,'success':error is None and not publication_errors,'native_test_success_claim':False}
save(directory/'POST.json',after);save(directory/'EPOCH.json',current)
(HERE/'CURRENT-EPOCH.json').write_text(json.dumps(current,indent=2,sort_keys=True)+'\n')
save(directory/'RESULT.json',{'error':error,'publication_errors':publication_errors,'owned_processes':state,'command_success':error is None and not publication_errors,'source_candidate_retained':True,'all_unrelated_bodies_preserved':True,'browser_run':False,'normal_producer_enabled':False})
print(label,'success' if error is None else error,flush=True)
assert error is None and not publication_errors
