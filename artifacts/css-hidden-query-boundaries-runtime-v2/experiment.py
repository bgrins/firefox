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
cost_spec=importlib.util.spec_from_file_location('cost_hook',HERE/'cost_hook.py')
cost_hook=importlib.util.module_from_spec(cost_spec)
cost_spec.loader.exec_module(cost_hook)
c=wpt.CONFIG
need(c.get('ready_for_preparation') is True, 'draft not ready for execution')
need(cost_hook.authenticate(ROOT,c['cost'])==inputs['cost_payload_pins'],'cost inputs changed')
for n,h in inputs['prior_terminal_pins'].items():
    need(sha(ROOT/n)==h,'prior terminal receipt changed '+n)
before=wpt.snapshot()
need(before==inputs['before'],'prepared state changed')
need(len(wpt.git('diff','--cached','--name-only').splitlines())==inputs['expected_staged_paths']==c['expected_staged_paths']==0,'index not empty')
need(all(not (ROOT/n).exists() and not (ROOT/n).is_symlink() for n in c['must_be_absent']) and inputs['temporary_test_state']=={n:None for n in c['install']},'temporary tests must be absent')
need(wpt.pins(wpt.resource_paths(c['tests'],virtual=True),virtual=True)==inputs['resource_pins'],'test/resource/metadata changed')
original={n:(HERE/'prepared/original'/n).read_bytes() for n in c['sources']}
head={n:(HERE/'prepared/head'/n).read_bytes() for n in c['sources']}
for n in c['sources']:
    need((ROOT/n).read_bytes()==original[n] and wpt.git('show','HEAD:'+n)==head[n],'original/HEAD snapshot '+n)
PRES_SHELL='layout/base/PresShell.cpp'
BLOCK='layout/generic/nsBlockFrame.cpp'
phases=[('baseline','pres-shell-before.cpp','block-before.cpp',False),
        ('column-provider','pres-shell-column.cpp','block-before.cpp',False),
        ('skipped-line-block','pres-shell-before.cpp','block-skipped-line.cpp',False),
        ('both','pres-shell-column.cpp','block-skipped-line.cpp',False),
        ('standalone-baseline','pres-shell-before.cpp','block-before.cpp',True),
        ('standalone-column-provider','pres-shell-column.cpp','block-before.cpp',True),
        ('standalone-skipped-line-block','pres-shell-before.cpp','block-skipped-line.cpp',True)]
state={'status':'starting','accepted_native_repair':False,'phases':{}}
errors=[]
changed=False
installed=[]

def epoch():
    now=wpt.snapshot()
    need(all(now[n]==before[n] for n in ['head','index_diff_sha256','index_entries_sha256']),'HEAD/index changed')

def sources_expected(selected):
    for n in c['guard_sources']:
        expected=hashlib.sha256(selected.get(n,head[n])).hexdigest() if n in head else inputs['source_pins'][n]
        need(sha(ROOT/n)==expected,'phase source changed '+n)

def result_map(run):
    return {(r['test'],r['subtest']):(r['status'],r.get('message')) for r in run['rows']}

prior_runs={name:json.loads((HERE/'evidence'/('prior-'+name+'-RUN.json')).read_text())
            for name in ['baseline','column-provider','skipped-line-block','both']}
prior_keys=set(result_map(prior_runs['baseline']))
need(len(prior_keys)==66 and all(run['complete'] and set(result_map(run))==prior_keys
     for run in prior_runs.values()), 'prior four-phase oracle incomplete')
standalone_prior=json.loads((HERE/'evidence/prior-standalone-baseline-RUN.json').read_text())
need(standalone_prior['complete'] and set(result_map(standalone_prior))==prior_keys,
     'standalone historical oracle incomplete')
family_baselines={}

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
    for n,data in head.items():
        changed=True
        (ROOT/n).write_bytes(data)
    for name,pres_shell,block,standalone in phases:
        authenticate_payloads()
        selected={PRES_SHELL:(HERE/'selected'/pres_shell).read_bytes(),
                  BLOCK:(HERE/'selected'/block).read_bytes(),
                  'layout/generic/nsFlexContainerFrame.cpp':(HERE/'selected'/('flex-without104.cpp' if standalone else 'flex-accepted.cpp')).read_bytes(),
                  'layout/generic/AbsoluteContainingBlock.cpp':(HERE/'selected'/('absolute-without105.cpp' if standalone else 'absolute-accepted.cpp')).read_bytes()}
        for n,data in selected.items():
            (ROOT/n).write_bytes(data)
        epoch()
        sources_expected(selected)
        if name=='standalone-baseline':
            need(all(sha(ROOT/n)==standalone_prior['before'][n] for n in c['guard_sources']),
                 'standalone historical source roles differ')
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
        if not standalone or name=='standalone-baseline':
            prior_run=standalone_prior if standalone else prior_runs[name]
            need(all(run['before'][n]==pin for n,pin in prior_run['before'].items()
                     if n not in c['guard_sources']+wpt.BINARIES),
                 'prior66 test/resource/metadata differs '+name)
            need({key:rows[key] for key in prior_keys}==result_map(prior_run),
                 'prior66 variant oracle changed '+name)
            current_ends={r['test']:r['status'] for r in run['ends']}
            need(all(current_ends[r['test']]==r['status'] for r in prior_run['ends']),
                 'prior66 file-end oracle differs '+name)
        family='standalone' if standalone else 'main'
        if name in ['baseline','standalone-baseline']:
            family_baselines[family]=rows
        baseline_rows=family_baselines[family]
        record['comparison_family']=family
        tracked_ids={'/'+str(Path(t).relative_to('testing/web-platform/tests')) for t in c['tracked_tests']}
        record['tracked50_historical_controls']={status:sum(key[0] in tracked_ids and value[0]==status for key,value in rows.items()) for status in ['PASS','FAIL']}
        record['candidate_cases']={status:sum(key[0] not in tracked_ids and value[0]==status for key,value in rows.items()) for status in ['PASS','FAIL']}
        record['standalone_control_limit']='Removing 104/105 can fail tracked50; candidate independence uses the untracked candidate cases and this family baseline' if standalone else None
        record['prior66_exact_match']=not standalone or name=='standalone-baseline'
        changes=[{'test':key[0],'subtest':key[1],'before':baseline_rows[key],
                  'after':rows[key]} for key in sorted(rows) if rows[key]!=baseline_rows[key]]
        record['changes_from_baseline']=changes
        record['status_transitions']={label:sum(baseline_rows[k][0]+'->'+rows[k][0]==label for k in rows)
                                      for label in ['PASS->PASS','PASS->FAIL','FAIL->PASS','FAIL->FAIL']}
        wpt.save('STATE.json',state)
        if name in c['cost']['phases']:
            state['status']='cost '+name
            wpt.save('STATE.json',state)
            record['cost']=cost_hook.run(wpt,name,inputs['cost_payload_pins'],run)
            epoch()
            sources_expected(selected)
            need(wpt.pins(list(inputs['resource_pins']))==inputs['resource_pins'],'post-cost resource drift')
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
