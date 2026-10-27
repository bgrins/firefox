import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def need(ok, why):
    if not ok:
        raise RuntimeError(why)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser()
parser.add_argument('--inputs-sha',required=True)
args=parser.parse_args()
need(not (HERE/'BEFORE.json').exists(),'experiment already started')
need(sha(HERE/'INPUTS.json')==args.inputs_sha,'INPUTS external pin')
inputs=json.loads((HERE/'INPUTS.json').read_text())
def authenticate_payloads():
    for n,h in inputs['payload_pins'].items():
        need(not Path(n).is_absolute() and '..' not in Path(n).parts,'unsafe payload path')
        need(stat.S_ISREG((HERE/n).lstat().st_mode) and sha(HERE/n)==h,'payload '+n)
authenticate_payloads()
need(sha(HERE/'DRAFT-FILES.json')==inputs['draft_sha256'],'draft seal')
spec=importlib.util.spec_from_file_location('compact_wpt',HERE/'run_wpt.py')
wpt=importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpt)
c=wpt.CONFIG
need(c.get('ready_for_preparation') is True, 'draft not ready for execution')
spec=importlib.util.spec_from_file_location('bindings',HERE/'bindings.py')
bindings=importlib.util.module_from_spec(spec)
spec.loader.exec_module(bindings)
bindings.authenticate(inputs['external_pins'],ROOT)
bindings.prerequisites()
bindings.index_state(wpt)
bindings.existing_tests(wpt)
before=wpt.snapshot()
need(before==inputs['before'],'prepared state changed')
need(len(wpt.git('diff','--cached','--name-only').splitlines())==inputs['expected_staged_paths']==c['expected_staged_paths']==925,'staged research count changed')
need(all(not (ROOT/n).exists() and not (ROOT/n).is_symlink() for n in c['must_be_absent']) and inputs['temporary_test_state']=={n:None for n in c['install']},'temporary tests must be absent')
need(wpt.pins(wpt.resource_paths(c['tests'],virtual=True),virtual=True)==inputs['resource_pins'],'test/resource/metadata changed')
original={n:(HERE/'prepared/original'/n).read_bytes() for n in c['sources']}
head={n:(HERE/'prepared/head'/n).read_bytes() for n in c['sources']}
baseline={n:(HERE/c['baseline_sources'][n]).read_bytes() for n in c['sources']}
for n in c['sources']:
    need((ROOT/n).read_bytes()==original[n] and wpt.git('show','HEAD:'+n)==head[n],'original/HEAD snapshot '+n)
GRID='layout/generic/nsGridContainerFrame.cpp'
phases=['baseline','float-only']
need(list(c['phases'])==phases,'Exact two-phase roster')
state={'status':'starting','accepted_native_repair':False,'phases':{}}
errors=[]
changed=False
installed=[]

def epoch():
    now=wpt.snapshot()
    need(all(now[n]==before[n] for n in ['head','index_diff_sha256','index_entries_sha256']),'HEAD/index changed')

def sources_expected(selected):
    for n in c['guard_sources']:
        expected=hashlib.sha256(selected.get(n,baseline[n])).hexdigest() if n in baseline else c['baseline_guard_pins'][n]
        need(sha(ROOT/n)==expected,'phase source changed '+n)

def result_map(run):
    return {(r['test'],r['subtest']):(r['status'],r.get('message')) for r in run['rows']}

baseline_rows=None
existing_ids={'/'+str(Path(t).relative_to('testing/web-platform/tests')) for t in c['existing_tests']}
float_id='/css/css-contain/content-visibility/hidden-float-owner-queries.html'
need(len(existing_ids)==9 and sum(map(len,c['expected_subtests'].values()))==95,'95-case roster')
oracles=json.loads((HERE/'EXPECTED-OUTCOMES.json').read_text())
need(list(oracles['phases'])==phases,'Expected phase roster')

def recovery_save(name,value):
    try:
        wpt.save(name,value)
    except BaseException as error:
        errors.append({'operation':'save '+name,'error':repr(error)})

wpt.save('BEFORE.json',before)
try:
    for target,source in c['install'].items():
        with (ROOT/target).open('xb') as stream:
            installed.append(target)
            stream.write((HERE/source).read_bytes())
    state['wpt_lint_exit']=wpt.command('wpt-lint',['./mach','lint','-l','wpt',*c['tests']])
    need(state['wpt_lint_exit']==0,'WPT lint failed')
    for n,data in baseline.items():
        changed=True
        (ROOT/n).write_bytes(data)
    for name in phases:
        authenticate_payloads()
        selected={path:(HERE/payload).read_bytes() for path,payload in c['phases'][name].items()}
        need(set(selected)=={GRID,'layout/base/PresShell.cpp','layout/generic/nsBlockFrame.cpp'},
             'Every phase must explicitly reset all three source roles')
        for n,data in selected.items():
            (ROOT/n).write_bytes(data)
        epoch()
        sources_expected(selected)
        need(wpt.pins(list(inputs['resource_pins']))==inputs['resource_pins'],'pre-build test/resource drift')
        state['status']='building '+name
        record=state['phases'][name]={}
        record['source_pins']={n:hashlib.sha256(data).hexdigest() for n,data in selected.items()}
        wpt.save('STATE.json',state)
        record['build_exit']=wpt.command(name+'-build',['./mach','build','binaries'])
        need(record['build_exit']==0,'build failed '+name)
        epoch()
        sources_expected(selected)
        state['status']='testing '+name
        wpt.save('STATE.json',state)
        record['wpt']=wpt.test_run(name,c['tests'],inputs['resource_pins'])
        epoch()
        sources_expected(selected)
        authenticate_payloads()
        run=json.loads((HERE/name/'RUN.json').read_text())
        record['status_counts']={status:sum(r['status']==status for r in run['rows']) for status in ['PASS','FAIL']}
        record['failures']=[{'test':r['test'],'subtest':r['subtest'],'message':r.get('message')} for r in run['rows'] if r['status']=='FAIL']
        rows=result_map(run)
        record['existing_controls']={status:sum(key[0] in existing_ids and value[0]==status for key,value in rows.items()) for status in ['PASS','FAIL']}
        if baseline_rows is None:
            baseline_rows=rows
        record['changes_from_baseline']=[{'test':key[0],'subtest':key[1],
            'before':baseline_rows[key],'after':rows[key]} for key in sorted(rows) if rows[key]!=baseline_rows[key]]
        record['status_transitions']={label:sum(baseline_rows[k][0]+'->'+rows[k][0]==label for k in rows)
                                      for label in ['PASS->PASS','PASS->FAIL','FAIL->PASS','FAIL->FAIL']}
        expected={(r['test'],r['subtest']):r for r in oracles['phases'][name]}
        need(set(rows)==set(expected),'Expected per-case roster differs')
        discrepancies=[]
        for key,value in rows.items():
            oracle=expected[key]
            if list(value) not in oracle['allowed']:
                discrepancies.append({'test':key[0],'subtest':key[1],'actual':value,'expected':oracle})
        record['expectation_discrepancies']=discrepancies
        record['visible_float_controls']={status:sum(oracle['role']=='visible-float-control' and rows[key][0]==status
            for key,oracle in expected.items()) for status in ['PASS','FAIL']}
        record['nested_hidden_classification']=[{'test':key[0],'subtest':key[1],
            'status':rows[key][0],'message':rows[key][1]} for key,oracle in expected.items()
            if oracle['role']=='nested-hidden-open-baseline']
        wpt.save('STATE.json',state)
        if name=='baseline':
            wpt.save('BASELINE-CLASSIFICATION.json',{'nested_hidden':record['nested_hidden_classification'],
                'all_float_rows':[{'test':key[0],'subtest':key[1],'status':value[0],'message':value[1]}
                                  for key,value in rows.items() if key[0] not in existing_ids],
                'scope':'First WPT assertions; visible push placement does not prove native pushed-bit coverage'})
        need(record['existing_controls']=={'PASS':79,'FAIL':0},'existing control failed '+name)
        need(record['visible_float_controls']=={'PASS':10,'FAIL':0},'visible float control failed '+name)
        need(not discrepancies,'Named outcome/diagnostic differs from expected '+name)
        need({k:v for k,v in rows.items() if k[0] in existing_ids}
             =={k:v for k,v in baseline_rows.items() if k[0] in existing_ids},'existing controls changed')
        need(record['status_transitions']['PASS->FAIL']==0,'new failure relative to baseline')
        record['expected_outcomes_match']=True
        wpt.save('STATE.json',state)
except BaseException as error:
    state['failure']={'type':type(error).__name__,'message':str(error)}
finally:
    state['status']='restoring original sources'
    state['recovery_errors']=errors
    recovery_save('STATE.json',state)
    for n,data in original.items():
        try:
            (ROOT/n).write_bytes(data)
        except BaseException as error:
            errors.append({'operation':'restore '+n,'error':repr(error)})
    for n in installed:
        try:
            (ROOT/n).unlink(missing_ok=True)
        except BaseException as error:
            errors.append({'operation':'remove temporary test '+n,'error':repr(error)})
    if changed:
        try:
            try:
                log=(HERE/'restore-build.log').open('w')
            except OSError as error:
                errors.append({'operation':'open restore log','error':repr(error)})
                log=None
            try:
                state['restore_build_exit']=subprocess.run(['./mach','build','binaries'],cwd=ROOT,env=wpt.ENV,stdout=log,stderr=subprocess.STDOUT).returncode
            finally:
                if log is not None:
                    log.close()
        except BaseException as error:
            errors.append({'operation':'restoration build','error':repr(error)})
    state['restored']=False
    try:
        final=wpt.snapshot()
        state['restored']=(final==before and all(not (ROOT/n).exists() and not (ROOT/n).is_symlink() for n in c['must_be_absent'])
                           and wpt.pins(wpt.resource_paths(c['tests'],virtual=True),virtual=True)==inputs['resource_pins'])
        recovery_save('FINAL.json',final)
    except BaseException as error:
        errors.append({'operation':'final snapshot','error':repr(error)})
    state['status']='terminal'
    recovery_save('STATE.json',state)
print(json.dumps(state,indent=2))
if 'failure' in state or errors or not state['restored'] or (changed and state.get('restore_build_exit')!=0):
    raise SystemExit(1)
