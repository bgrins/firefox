import sys
sys.dont_write_bytecode=True
import copy, hashlib, importlib.util, json, stat
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,why):
    if not ok:raise RuntimeError(why)
def load(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def auth(mapping,base):
    for n,h in mapping.items():
        need(not Path(n).is_absolute() and '..' not in Path(n).parts,'safe reference')
        need(stat.S_ISREG((base/n).lstat().st_mode) and sha(base/n)==h,n)
for p in HERE.glob('*.py'):compile(p.read_text(),str(p),'exec')
c=read(HERE/'CONFIG.json');need(c['ready_for_execution'] is False,'disabled')
auth(read(HERE/'REFERENCES.json'),ROOT)
for key,value in c['required_seals'].items():
    if value is None:continue
    path=ROOT/value['path'];need(sha(path)==value['sha256'],key);auth(read(path),path.parent)
gate=load('gate',HERE/'epoch_gate.py')
old,pins,_,installed=gate.bind(ROOT,ROOT/c['epoch'],read,sha,auth,load)
wpt=load('wpt',ROOT/c['helpers']/'run_wpt.py');wpt.HERE=HERE;wpt.CONFIG=c
now=wpt.snapshot();need(all(now[k]==old[k] for k in old if k!='sources'),'head/index/native diff')
need(now['sources']==c['source_pins'] and all(now['sources'][n]==h for n,h in old['sources'].items()),'all current sources')
need(wpt.pins(list(pins))==pins and wpt.pins(list(read(HERE/'RESOURCES.json')))==read(HERE/'RESOURCES.json'),'all live epoch/resources')
need({n:hashlib.sha256(wpt.git('show',c['head']+':'+n)).hexdigest() for n in c['guard_sources']}==c['head_pins'],'HEAD source roles')
need({n:sha(ROOT/path) for n,path in c['candidate_sources'].items()}==c['candidate_pins'],'candidate source roles')
need([n for n in wpt.git('diff','--name-only').decode().splitlines() if not n.startswith('artifacts/')]==c['modified_native_paths'],'native roster')
need(wpt.pins(c['existing_tests'])==c['existing_test_pins'],'all readonly test bytes')
need(wpt.git('ls-files','--',*c['existing_tests']).decode().splitlines()==c['tracked_existing_tests'],'readonly test tracking')
for n,v in installed.items():
    s=(ROOT/n).lstat();need([s.st_dev,s.st_ino]==v['identity'] and sha(ROOT/n)==v['sha256'],'installed identity')
for n in c['install']:need(not (ROOT/n).exists() and not (ROOT/n).is_symlink() and not wpt.git('ls-files','--',n),'owned test absence')
need(all(not (ROOT/n).exists() and not (ROOT/n).is_symlink() for n in c['must_be_absent']),'prior temp absent')
need(sum(map(len,c['expected_subtests'].values()))==52 and len(c['tests'])==6,'52 in6')
tests=load('tests',HERE/'tests.py')
rows=[{'test':test,'subtest':name,'status':'PASS'} for test,names in c['expected_subtests'].items() for name in names]
base=copy.deepcopy(rows); witness=next(i for i,r in enumerate(base) if [r['test'],r['subtest']] in c['required_hidden_witnesses'])
base[witness].update(status='FAIL',message=c['landing_failure_prefix']+'24 but got30')
class Fake:
    CONFIG=c
    need=staticmethod(need)
    save=staticmethod(lambda name,value:None)
f=Fake();tests.require_phase(f,'baseline',{'rows':base});tests.require_phase(f,'candidate',{'rows':rows});tests.compare(f,{'rows':base},{'rows':rows})
negatives=[]
for label,phase,edit in [('calibration','baseline',lambda r:r[witness].update(message='assert_equals: initial length expected24 but got30')),('candidate-failure','candidate',lambda r:None),('duplicate','baseline',lambda r:r.__setitem__(0,r[1]))]:
    changed=copy.deepcopy(base);edit(changed)
    try:tests.require_phase(f,phase,{'rows':changed})
    except RuntimeError:negatives.append(label)
    else:raise AssertionError(label)
control=next(i for i,r in enumerate(rows) if r['test'] not in c['landing_tests'])
for label,changed in [('control-regression',copy.deepcopy(rows)),('no-hidden-witness',copy.deepcopy(rows))]:
    if label=='control-regression':changed[control].update(status='FAIL',message='regression')
    try:tests.compare(f,{'rows':base if label=='control-regression' else rows},{'rows':changed})
    except RuntimeError:negatives.append(label)
    else:raise AssertionError(label)
print(json.dumps({'status':'PASS','disabled':True,'sources':len(c['sources']),'guards':len(c['guard_sources']),'candidate_sources':len(c['candidate_sources']),'subtests':len(rows),'installed_test_identities':len(installed),'persistent_resources':len(read(HERE/'RESOURCES.json')),'negative_controls':negatives,'native_browser_index_actions':False},indent=2))
