import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, stat
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok, why):
    if not ok: raise RuntimeError(why)
def load(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
def auth(mapping, base):
    for n,h in mapping.items(): need(sha(base/n)==h,n)
c = read(HERE/'CONFIG.json'); state = read(HERE/'STATE.json')
auth(read(HERE/'DRAFT-FILES.json'), HERE); auth(read(HERE/'REFERENCES.json'), ROOT)
need(state['status']=='terminal' and state['complete'] and state['preserved'] and not state['native_changes'], 'terminal preservation')
gate=load('gate',HERE/'epoch_gate.py')
_, prior, expected, pins, config, installed=gate.bind(ROOT,ROOT/c['epoch'],c,read,sha,auth,load,need)
pins[c['owned_metadata']]=None
wpt=load('wpt',ROOT/c['helpers']/'run_wpt.py');wpt.CONFIG=config
need(wpt.snapshot()==expected, 'live source/index state')
need(wpt.pins(list(pins))==pins, 'live resources/binaries')
need(read(HERE/'BEFORE.json')==read(HERE/'FINAL.json')=={'snapshot':expected,'pins':pins}, 'before/final')
need(not (ROOT/c['owned_test']).exists(), 'owned fixture removed')
for n,item in installed.items():
    s=(ROOT/n).lstat();need(stat.S_ISREG(s.st_mode) and [s.st_dev,s.st_ino]==item['identity'] and sha(ROOT/n)==item['sha256'],'installed test identity')
run=read(HERE/'wpt-hidden-fallback/RUN.json')
need(run['complete'] and not run['infrastructure_faults'] and run['before']==run['after'], 'complete raw phase')
need(read(HERE/'wpt-hidden-fallback/CLEANUP.json')=={'owned_group_absent':True,'errors':[]},'process cleanup')
summary=load('classifier',HERE/'classify.py').classify(run['rows'],c['names'],need)
need(summary==read(HERE/'SUMMARY.json') and summary['counts']=={'PASS':4,'FAIL':4}, 'raw classification')
events=[json.loads(s) for s in (HERE/'wpt-hidden-fallback/raw.json').read_text().splitlines()]
need([e for e in events if e.get('action')=='test_status']==run['rows'], 'raw rows')
receipt={'status':'PRESERVED_CALIBRATED_DIAGNOSTIC','session':96209,'exit':0,
 'state_sha256':sha(HERE/'STATE.json'),'final_sha256':sha(HERE/'FINAL.json'),
 'source_count':len(expected['sources']),'pin_count':len(pins),'native_modified_paths':len(config['modified_native_paths']),
 'staged_paths':len(wpt.git('diff','--cached','--name-only','-z').split(b'\0'))-1,
 'installed_tests':installed,'installed_binary_pins':prior['installed_binary_pins'],
 'counts':summary['counts'],'raw_complete':True,'owned_fixture_removed':True,'accepted_bug':False,
 'normative_assessment':'artifacts/css-svg-length-hidden-provider-root-assessment-v1/FILES.json',
 'native_fallback_branch_observed':False}
(HERE/'ROOT-FINAL-CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('installed_tests','installed_binary_pins')},indent=2))
