import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def need(ok, why):
    if not ok:
        raise RuntimeError(why)

def authenticate(mapping, base):
    for name,digest in mapping.items():
        need(sha(base/name) == digest, name)

def load(name,p):
    module = type('Module',(),{})()
    exec(compile(p.read_text(),str(p),'exec'),module.__dict__)
    return module

for p in HERE.glob('*.py'):
    compile(p.read_text(),str(p),'exec')
authenticate(read(HERE/'REFERENCES.json'),ROOT)
c = read(HERE/'CONFIG.json')
assert c['ready_for_execution'] is False and c['final_review'] is None
proposal = ROOT/c['proposal'];authenticate(read(proposal/'FILES.json'),proposal)
assert (HERE/'fixture.html').read_bytes()==(proposal/'probe.html').read_bytes()
assert c['names']==read(proposal/'EXPECTED.json')['names']
epoch=ROOT/c['epoch'];assert sha(epoch/'FILES.json')==c['epoch_manifest_sha256']
authenticate(read(epoch/'FILES.json'),epoch)
assert sha(epoch/'ROOT-FINAL-CHECK.json')==c['root_receipt_sha256']
gate=load('gate',HERE/'epoch_gate.py');bound=gate.bind(ROOT,epoch,c,read,sha,authenticate,load,need)
assert len(bound[2]['sources'])==53 and len(bound[4]['modified_native_paths'])==30 and len(bound[5])==8
assert all(bound[3][n]==v for n,v in read(epoch/'FINAL.json')['pins'].items())
negatives=[]
original={n:read(epoch/n) for n in ('STATE.json','ROOT-FINAL-CHECK.json','FINAL.json')}
for label,edit in [('wrong-complete',lambda d:d['STATE.json'].update(complete=True)),
                   ('not-preserved',lambda d:d['STATE.json'].update(preserved=False)),
                   ('different-rejection',lambda d:d['STATE.json']['failure'].update(message='other')),
                   ('old20',lambda d:d['ROOT-FINAL-CHECK.json'].update(unpredicted_first_value=20)),
                   ('changed-binary',lambda d:d['ROOT-FINAL-CHECK.json'].update(installed_binary_pins={})),
                   ('changed-inode',lambda d:d['ROOT-FINAL-CHECK.json'].update(installed_tests={})),
                   ('lost-pin',lambda d:d['FINAL.json']['pins'].pop(next(iter(d['FINAL.json']['pins']))))]:
    data=copy.deepcopy(original);edit(data)
    rd=lambda p:copy.deepcopy(data[p.name]) if p.parent==epoch and p.name in data else read(p)
    try:gate.bind(ROOT,epoch,c,rd,sha,authenticate,load,need)
    except (RuntimeError,KeyError):negatives.append(label)
    else:raise AssertionError(label)
classifier=load('classifier',HERE/'classify.py')
rows=[{'subtest':name,'status':'PASS'} for name in c['names']]
assert classifier.classify(rows,c['names'],need)['counts']=={'PASS':8,'FAIL':0}

def snapshot(unit,history,first):
    size=[240,120] if history=='hidden-only' else [460,260]
    axis=0 if unit=='vw' else 1
    return {'unit':unit,'history':history,'initialSize':[240,120,240,120],'warmed':[24,12][axis],
        'fallbackSize':[300,150,300,150],'fallbackValue':[30,15][axis],'preResizeSize':[240,120],
        'first':first,'repeat':first,'hostSize':size,'postQuerySize':size+size,'postQueryValue':size[axis]/10,
        'revealSize':size+size,'revealValue':size[axis]/10,'resetSize':[240,120,240,120],'resetValue':[24,12][axis]}

def failure(index,snap,expected=None,got=None):
    r=copy.deepcopy(rows);unit,history=snap['unit'],snap['history'];axis=0 if unit=='vw' else 1
    expected=([240,120] if history=='hidden-only' else [460,260])[axis]/10 if expected is None else expected
    got=snap['first'] if got is None else got
    r[index].update(status='FAIL',message='assert_equals: current viewport hypothesis; snapshot='+json.dumps(snap,separators=(',',':'))+' expected '+str(expected)+' but got '+str(got))
    return r
accepted=[]
for index,unit,history,values in [(1,'vw','hidden-only',[30]),(2,'vw','hidden-resize',[30,24]),(4,'vh','hidden-only',[15]),(5,'vh','hidden-resize',[15,12])]:
    for value in values:
        r=failure(index,snapshot(unit,history,value));assert classifier.classify(r,c['names'],need)['counts']=={'PASS':7,'FAIL':1};accepted.append([index,value])
combined=copy.deepcopy(rows)
for index,unit,history,value in [(1,'vw','hidden-only',30),(2,'vw','hidden-resize',30),(4,'vh','hidden-only',15),(5,'vh','hidden-resize',15)]:
    combined[index]=failure(index,snapshot(unit,history,value))[index]
assert classifier.classify(combined,c['names'],need)['counts']=={'PASS':4,'FAIL':4}
bad=[]
base=snapshot('vw','hidden-resize',30)
for key,value in [('unit','vh'),('history','hidden-only'),('first',31),('repeat',float('inf')),('warmed',25),('fallbackValue',31),('postQueryValue',True),('hostSize',[461,260]),('initialSize',[240,120]),('postQuerySize',[0,0,0,-1]),('resetValue',0),('revealValue',45),('extra',0)]:
    snap=copy.deepcopy(base);snap[key]=value;bad.append(failure(2,snap))
bad.extend([failure(2,base,expected=47),failure(2,base,got=29),rows[:-1],rows[::-1],[rows[0]]*8])
for index in (0,3,6,7):bad.append(failure(index,base))
for transform in [lambda s:s.replace('{"unit":','{"unit":"vw","unit":',1),lambda s:s.replace('snapshot={','snapshot=[',1),lambda s:s.replace('current viewport hypothesis','initial dimensions calibration'),lambda s:s+'x',lambda s:s.replace('snapshot={','snapshot={'+' '*17000,1)]:
    r=failure(2,base);r[2]['message']=transform(r[2]['message']);bad.append(r)
for r in bad:
    try:classifier.classify(r,c['names'],need)
    except RuntimeError:pass
    else:raise AssertionError(r)
print(json.dumps({'syntax':True,'exact_fixture':True,'preserved_rejected_epoch_roles':396,
    'audit_extended_roles':len(bound[3]),'sources':53,'native_paths':30,'installed_test_identities':8,
    'epoch_negatives':negatives,'all_PASS_valid':True,'accepted_single_failure_shapes':accepted,
    'classifier_negatives':len(bad),'ready_for_execution':False,'final_review':None,
    'browser_native_index_actions':False},indent=2))
