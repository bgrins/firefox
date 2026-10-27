import argparse, ast, copy, hashlib, importlib.util, json, stat, subprocess, sys, tempfile, types
from pathlib import Path
assert sys.flags.isolated and sys.flags.no_site and not sys.flags.optimize
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,message):
    if not ok:raise RuntimeError(message)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);out=parser.parse_args().output.resolve()
    assert not out.exists() and HERE not in out.parents;out.mkdir(parents=True)
    inputs=read(HERE/'INPUTS.json');assert inputs['ready_for_execution'] is False and inputs['controller_review'] is None
    assert inputs['actual_session'] is None and inputs['actual_exit'] is None and sha(HERE/'compare.py')==inputs['compare_sha256']
    for n,h in inputs['local_pins'].items():assert sha(HERE/n)==h,n
    for n,h in inputs['helper_pins'].items():assert sha(ROOT/n)==h,n
    for directory,h in inputs['manifests'].items():
        base=ROOT/directory;assert sha(base/'FILES.json')==h
        for n,v in read(base/'FILES.json').items():
            assert not Path(n).is_absolute() and '..' not in Path(n).parts
            assert stat.S_ISREG((base/n).lstat().st_mode) and sha(base/n)==v
    tree=ast.parse((HERE/'compare.py').read_text());functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    oldtree=ast.parse((ROOT/'artifacts/css-keyframe-tree-counting-combined-comparison-v1/compare.py').read_text());old={n.name:n for n in oldtree.body if isinstance(n,ast.FunctionDef)}
    inherited=['sha','need','save','authenticate','load','verify_roles','verify','write_source','restore_sources','build','outcomes','assess','owned_group_errors','cleanup_fixtures']
    assert all(ast.dump(functions[n])==ast.dump(old[n]) for n in inherited)
    proposal=read(HERE/'CANDIDATE.json');maps=read(HERE/'SOURCE-MAPS.json');inventories=read(HERE/'NATIVE-INVENTORIES.json');prepared=read(HERE/'PREPARED-EPOCH.json');promotion=read(HERE/'SOURCE-PROMOTION.json');path=promotion['path']
    assert set(proposal['native_paths'])=={path} and path not in prepared['snapshot']['sources'] and prepared['pins'][path]==promotion['sha256']
    assert maps['baseline']==maps['restored']==prepared['snapshot']['sources']|{path:promotion['sha256']}
    assert len(maps['baseline'])==80 and {n for n in maps['baseline'] if maps['baseline'][n]!=maps['candidate'][n]}=={path}
    assert [len(inventories[n]) for n in ['baseline','candidate','restored']]==[43,44,43]
    for n,item in proposal['native_paths'].items():
        for phase in ['original','candidate']:assert sha(ROOT/item[phase])==item[phase+'_sha256']
    assert sha(ROOT/proposal['patch'])==proposal['patch_sha256']
    for n,item in proposal['fixture'].items():assert prepared['pins'][n] is None and sha(ROOT/item['source'])==item['sha256']
    sources=read(HERE/'OUTCOME-SOURCES.json');latest=ROOT/sources['diagnostic_runtime'];controls=ROOT/sources['controls_runtime'];assert read(latest/'FINAL.json')==prepared
    previous=read(controls/'FINAL.json');assert prepared['snapshot']==previous['snapshot'] and prepared['installed_tests']==previous['installed_tests'] and all(prepared['pins'][n]==h for n,h in previous['pins'].items())
    rows=read(latest/'wpt-diagnostic/RUN.json')['rows']+[r for r in read(controls/'wpt-restored/RUN.json')['rows'] if r['test'] in sources['controls_tests']]
    assert rows==read(HERE/'OBSERVED-ROWS.json') and len(rows)==182
    roster=read(HERE/'ROSTER.json');assert len(roster['tests'])==13
    for test,names in roster['expected_subtests'].items():assert [r['subtest'] for r in rows if r['test']==test]==names
    config=read(latest/'CONFIG.json');assert all('testing/web-platform/tests'+n in config['existing_tests'] for n in sources['controls_tests']);config.update(roster)
    env={'config':config,'need':need};exec(compile(ast.Module(body=[functions['outcomes']],type_ignores=[]),'normalize','exec'),env)
    observed=env['outcomes']({'rows':rows,'ends':[]});policy=load('duration_policy',HERE/'policy.py');ideal=copy.deepcopy(observed)
    for key in policy.MANDATORY:ideal[key].update(status='PASS',message=None,expected=None,effective_expected='PASS',known_intermittent=[])
    assert not policy.assess(observed,observed,'baseline')[2] and not policy.assess(observed,observed,'restored')[2]
    assert not policy.assess(ideal,observed,'candidate')[2] and len(policy.assess(ideal,observed,'candidate')[1])==2
    negatives=[]
    for key in sorted(policy.EXPECTED-policy.OBSERVATIONAL):
        changed=copy.deepcopy(ideal);v=changed[key];v['status']='FAIL' if v['status']=='PASS' else 'PASS';v['expected']=None if v['status']==v['effective_expected'] else v['effective_expected']
        assert policy.assess(changed,observed,'candidate')[2];negatives.append(str(key))
    for phase in ['baseline','restored']:
        changed=copy.deepcopy(observed);changed[next(iter(policy.MANDATORY))]['message']='changed failure';assert policy.assess(changed,observed,phase)[2];negatives.append(phase)
    for field,value in [('expected','SKIP'),('effective_expected','SKIP'),('known_intermittent',['FAIL'])]:
        changed=copy.deepcopy(ideal);changed[next(iter(policy.OBSERVATIONAL))][field]=value;assert policy.assess(changed,observed,'candidate')[2];negatives.append(field)
    changed=copy.deepcopy(ideal);changed.pop(next(iter(changed)));assert policy.assess(changed,observed,'candidate')[2];negatives.append('missing')
    for key in policy.OBSERVATIONAL:
        changed=copy.deepcopy(ideal);changed[key]['message']='different observed assertion';r=policy.assess(changed,observed,'candidate');assert not r[2] and len(r[1])==2
    classifier=load('duration_classifier',HERE/'diagnostic/classify.py');assert not classifier.classify(read(latest/'wpt-diagnostic/RUN.json')['rows'])['errors']
    flow=next(n for n in tree.body if isinstance(n,ast.Try));code=compile(ast.Module(body=[flow],type_ignores=[]),'actual-flow','exec');scenarios=[]
    for fault in [None,'baseline-capture','source-write','candidate-build','candidate-capture','restore-source','restored-build','restored-capture','FINAL.json','FINAL-PINS.json','CLEANUP.json']:
        with tempfile.TemporaryDirectory(prefix='duration-flow-') as scratch:
            root=Path(scratch);fixture=root/'fixture.html';fixture.write_text('owned');calls=[];saved={}
            e={'ROOT':root,'HERE':root,'need':need,'sha':sha,'stat':stat,'read':read,'owned_plan':{'temporary_fixtures':{'test.html':{'source':'fixture.html','sha256':sha(fixture)}}},'restoration':{'test.html':None},'owned':{},'bodies':{path:{}},'failure':None,'recovery_errors':[],'transitions':[],'captured':[],'completed':[],'baseline_outcomes':None,'mutation_started':False,'current_binaries':{}}
            def save(n,v):
                if n==fault:raise RuntimeError('publication')
                saved[n]=copy.deepcopy(v);(root/n).write_text(json.dumps(v))
            def capture(label,phase):
                calls.append(label)
                if fault==phase+'-capture':raise RuntimeError('capture')
                e['captured'].append(label);e['completed'].append(phase)
                if phase=='baseline':e['baseline_outcomes']={}
            def write_source(n,phase):
                calls.append('write');e['mutation_started']=True
                if fault=='source-write':raise RuntimeError('write')
            def restore():
                calls.append('restore-source');return ['restore failure'] if fault=='restore-source' else []
            def build(label,phase):
                calls.append(label+'-build')
                if fault==label+'-build':raise RuntimeError('build')
            e.update(save=save,capture=capture,write_source=write_source,restore_sources=restore,build=build,verify=lambda *a,**k:{'snapshot':{},'pins':{},'installed_tests':{}})
            exec(compile(ast.Module(body=[functions[n] for n in ['owned_group_errors','cleanup_fixtures']],type_ignores=[]),'cleanup','exec'),e);exec(code,e)
            assert not (root/'test.html').exists() and 'RESULT.json' in saved
            if fault=='baseline-capture':assert 'write' not in calls and not any(c.endswith('-build') for c in calls)
            else:
                assert 'restore-source' in calls
                if fault!='restore-source':assert 'restored-build' in calls
            if fault is None:assert saved['RESULT.json']['completed_phases']==['baseline','candidate','restored'] and not saved['RESULT.json']['recovery_errors']
            else:assert saved['RESULT.json']['comparison_error'] or saved['RESULT.json']['recovery_errors']
            scenarios.append(str(fault))
    # Replay the actual archive-only initialization; all live helper imports are inert substitutes.
    init_start=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='epoch' for t in n.targets))
    init_stop=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Tuple) and any(isinstance(v,ast.Name) and v.id=='owned' for v in t.elts) for t in n.targets))
    def archive_load(name,path):
        if path.name=='validate.py':return types.SimpleNamespace(wpt=types.SimpleNamespace(ENV={}),OLD=ROOT/'artifacts/css-accepted-119-121-122-install-runtime-v1')
        if path.name in ('run_wpt.py','architecture.py'):return types.SimpleNamespace()
        return load(name,path)
    initialized={'ROOT':ROOT,'HERE':HERE,'DATA':HERE,'PRIOR':ROOT/'artifacts/css-counter-additive-install-runtime-v1','Path':Path,'stat':stat,'json':json,'hashlib':hashlib,'read':read,'inputs':inputs}
    exec(compile(ast.Module(body=[functions[n] for n in ['sha','need','authenticate','outcomes']],type_ignores=[]),'archive-functions','exec'),initialized)
    saved_init={};initialized.update(load=archive_load,save=lambda n,v:saved_init.update({n:v}))
    exec(compile(ast.Module(body=tree.body[init_start:init_stop],type_ignores=[]),'actual-initialization','exec'),initialized)
    assert len(initialized['restoration'])==696 and len(initialized['before']['snapshot']['sources'])==80
    assert len(initialized['archived_before']['snapshot']['sources'])==79 and len(initialized['observed'])==182
    assert len(initialized['repair_keys'])==2 and len(initialized['owned_plan']['temporary_fixtures'])==6
    assert initialized['config']['must_be_absent']==sorted(n for n,h in initialized['restoration'].items() if h is None and n not in initialized['proposal']['fixture'])
    assert not set(initialized['proposal']['fixture'])&set(initialized['config']['existing_tests'])
    refusal=subprocess.run([sys.executable,'-I','-S','-B',str(HERE/'compare.py')],capture_output=True,text=True);assert refusal.returncode!=0 and 'disabled or invalid activation' in refusal.stderr;(out/'disabled.stderr').write_text(refusal.stderr)
    result={'status':'KEYFRAME_CSS_DURATION_COMPARISON_STATIC_PASS','cases':182,'harnesses':13,'required_landing_PASS':6,'observed_repairs':2,'regression_controls':130,'observational_only':3,'exact_nonobservational':179,'planned_roles':696,'source_guards':80,'inventories':[43,44,43],'fixtures':6,'installed_identities':25,'staged_paths':925,'policy_negatives':len(negatives),'actual_flow_scenarios':scenarios,'inherited_functions':inherited,'actual_archive_initialization':True,'activation_disabled':True,'browser_build_execution':False,'live_native_index_reads':False}
    (out/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
