from pathlib import Path
import ast,json,hashlib,copy,types
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'artifacts/css-finite-mod-rem-comparison-runtime-v1';D=ROOT/'artifacts/css-finite-mod-rem-comparison-data-v1'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,message):
 if not ok:raise RuntimeError(message)
source=(P/'compare.py').read_text();tree=ast.parse(source);inputs=read(P/'INPUTS.json')
assert sha(P/'compare.py')==inputs['compare_sha256'] and not inputs['ready_for_execution'] and inputs['controller_review'] is None
for n,h in inputs['manifests'].items():
 p=ROOT/n/'FILES.json';assert sha(p)==h
 for name,value in read(p).items():assert sha(p.parent/name)==value
for n,h in inputs['helper_pins'].items():assert sha(ROOT/n)==h
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('outcomes','assess')]
config=read(D/'ROSTER.json');env={'need':need,'config':config};exec(compile(ast.Module(body=functions,type_ignores=[]),'<pure policy>','exec'),env)
obs=env['outcomes']({'rows':read(D/'OBSERVED-LANDING-BASELINE.json')['rows'],'ends':[]})
keys={(t,n) for t,ns in config['expected_subtests'].items() for n in ns};repair={k for k,v in obs.items() if v['status']=='FAIL'}
base={k:{'test':k[0],'subtest':k[1],'status':'PASS','message':None,'expected':None,'effective_expected':'PASS','known_intermittent':[]} for k in keys};base.update(obs)
controls=sorted(keys-set(obs));fail=controls[0];base[fail].update(status='FAIL',message='retained diagnostic',effective_expected='FAIL')
env.update(expected_keys=keys,observed=obs,baseline_outcomes=base,repair_keys=repair,landing_keys=set(obs))
assert not env['assess'](base,'baseline')[2]
candidate=copy.deepcopy(base)
for k in repair:candidate[k].update(status='PASS',message=None,expected=None,effective_expected='PASS',known_intermittent=[])
assert len(env['assess'](candidate,'candidate')[1])==16 and not env['assess'](candidate,'candidate')[2]
assert not env['assess'](base,'restored')[2]
negative=[]
def reject(label,rows,phase):
 try:bad=bool(env['assess'](rows,phase)[2])
 except RuntimeError:bad=True
 assert bad,label
 negative.append(label)
for k in repair:
 x=copy.deepcopy(candidate);x[k]=base[k];reject('missing repair '+k[1],x,'candidate')
x=copy.deepcopy(candidate);x[fail].update(status='PASS',message=None,effective_expected='PASS');reject('unapproved extra improvement',x,'candidate')
for label,field,value in [('retained failure message','message','changed'),('retained failure metadata','expected','PASS'),('retained failure intermittent','known_intermittent',['PASS'])]:
 x=copy.deepcopy(candidate);x[fail][field]=value;reject(label,x,'candidate')
x=copy.deepcopy(candidate);x[controls[1]].update(status='FAIL',message='lost pass');reject('lost control pass',x,'candidate')
x=copy.deepcopy(base);x[next(iter(repair))]['message']='changed';reject('changed observed baseline',x,'baseline')
x=copy.deepcopy(base);x[controls[1]]['message']='drift';reject('restored drift',x,'restored')
x=copy.deepcopy(candidate);x.pop(controls[1]);reject('missing identity',x,'candidate')
# Execute actual helper dispatch prefix without any path/process operation.
helper=ROOT/'artifacts/css-accepted-119-121-122-install-runtime-v1/tests.py';run=next(n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='run')
statements=[]
for n in run.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='directory' for t in n.targets):break
 statements.append(n)
prefix=compile(ast.Module(body=statements,type_ignores=[]),'<actual tests.run dispatch>','exec')
installed=read(ROOT/'artifacts/css-finite-mod-rem-runtime-v1/CONFIG.json');installed.update(config)
labels=[]
for n in ast.walk(tree):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='capture' and len(n.args)==2 and all(isinstance(a,ast.Constant) for a in n.args):labels.append((n.args[0].value,n.args[1].value))
assert sorted(phase for _,phase in labels)==['baseline','candidate','restored']
for label,phase in labels:
 e={'wpt':types.SimpleNamespace(CONFIG=installed),'phase':label};exec(prefix,e)
 assert e['c']['tests']==config['tests'] and e['c']['expected_subtests']==config['expected_subtests']
 assert sum(map(len,e['c']['expected_subtests'].values()))==700
old={'wpt':types.SimpleNamespace(CONFIG=installed),'phase':'baseline'};exec(prefix,old)
assert old['c']['expected_subtests']!=config['expected_subtests']
print(json.dumps({'status':'CONTROLLER_ARCHIVE_POLICY_REPLAY_PASS','compare_sha256':sha(P/'compare.py'),'inputs_sha256':sha(P/'INPUTS.json'),'negative_policy_checks':len(negative),'actual_helper_dispatch_labels':labels,'historical_baseline_alias_detected':True,'live_operations':False},indent=2))
