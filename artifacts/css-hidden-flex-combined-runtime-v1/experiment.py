import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
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
parser.add_argument('--with-traces',action='store_true')
parser.add_argument('--with-timings',action='store_true')
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
spec=importlib.util.spec_from_file_location('combined_wpt',HERE/'run_wpt.py')
wpt=importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpt)
c=wpt.CONFIG
before=wpt.snapshot()
need(before==inputs['before'],'prepared state changed')
need(len(wpt.git('diff','--cached','--name-only').splitlines())==inputs['expected_staged_paths']==c['expected_staged_paths']==0,'index not empty')
need(all(not (ROOT/n).exists() for n in c['install']) and inputs['temporary_test_state']=={n:None for n in c['install']},'temporary tests must be absent')
need(wpt.pins(wpt.resource_paths(c['tests'],virtual=True),virtual=True)==inputs['resource_pins'],'test/resource/metadata changed')
original={n:(HERE/'prepared/original'/n).read_bytes() for n in c['sources']}
head={n:(HERE/'prepared/head'/n).read_bytes() for n in c['sources']}
for n in c['sources']:
    need((ROOT/n).read_bytes()==original[n] and wpt.git('show','HEAD:'+n)==head[n],'original/HEAD snapshot '+n)
FLEX='layout/generic/nsFlexContainerFrame.cpp'
ABSOLUTE='layout/generic/AbsoluteContainingBlock.cpp'
phases=[('baseline','flex-baseline.cpp','absolute-baseline.cpp'),
        ('principal-only','flex-principal.cpp','absolute-baseline.cpp'),
        ('oof-only','flex-baseline.cpp','absolute-oof.cpp'),
        ('both','flex-principal.cpp','absolute-oof.cpp')]
traces=[('trace-baseline','flex-baseline.cpp','absolute-trace-baseline.cpp'),
        ('trace-oof-only','flex-baseline.cpp','absolute-trace-oof.cpp')] if args.with_traces else []
state={'status':'starting','accepted_native_repair':False,'phases':{},'traces':{},'timings':{},'trace_requested':args.with_traces,'timing_requested':args.with_timings}
errors=[]
changed=False

def epoch():
    now=wpt.snapshot()
    need(all(now[n]==before[n] for n in ['head','index_diff_sha256','index_entries_sha256']),'HEAD/index changed')

def sources_expected(selected):
    for n in c['guard_sources']:
        expected=hashlib.sha256(selected.get(n,head[n])).hexdigest() if n in head else inputs['source_pins'][n]
        need(sha(ROOT/n)==expected,'phase source changed '+n)

def recovery_save(name,value):
    try:
        wpt.save(name,value)
    except BaseException as error:
        errors.append({'operation':'save '+name,'error':repr(error)})

wpt.save('BEFORE.json',before)
try:
    for target,source in c['install'].items():
        (ROOT/target).write_bytes((HERE/source).read_bytes())
    state['wpt_lint_exit']=wpt.command('wpt-lint',['./mach','lint','-l','wpt',*c['install']])
    need(state['wpt_lint_exit']==0,'WPT lint failed')
    for n,data in head.items():
        changed=True
        (ROOT/n).write_bytes(data)
    for name,flex,absolute in phases+traces:
        authenticate_payloads()
        is_trace=name.startswith('trace-')
        selected={FLEX:(HERE/'selected'/flex).read_bytes(),ABSOLUTE:(HERE/'selected'/absolute).read_bytes()}
        for n,data in selected.items():
            (ROOT/n).write_bytes(data)
        epoch()
        sources_expected(selected)
        need(wpt.pins(list(inputs['resource_pins']))==inputs['resource_pins'],'pre-build test/resource drift')
        state['status']='building '+name
        record=(state['traces'] if is_trace else state['phases'])[name]={}
        record['source_pins']={n:hashlib.sha256(data).hexdigest() for n,data in selected.items()}
        wpt.save('STATE.json',state)
        record['build_exit']=wpt.command(name+'-build',['./mach','build','binaries'])
        need(record['build_exit']==0,'build failed '+name)
        epoch()
        sources_expected(selected)
        state['status']='testing '+name
        wpt.save('STATE.json',state)
        record['wpt']=wpt.test_run(name,c['trace_tests'] if is_trace else c['tests'],inputs['resource_pins'])
        epoch()
        sources_expected(selected)
        run=json.loads((HERE/name/'RUN.json').read_text())
        record['status_counts']={status:sum(r['status']==status for r in run['rows']) for status in ['PASS','FAIL']}
        record['failures']=[{'test':r['test'],'subtest':r['subtest'],'message':r.get('message')} for r in run['rows'] if r['status']=='FAIL']
        if is_trace:
            lines=(HERE/(name+'-wpt.log')).read_text().splitlines()
            observed=[line for line in lines if re.search(r'\[hidden-oof-(before|return|commit)\]',line)]
            (HERE/name/'TRACE-LINES.json').write_text(json.dumps(observed,indent=2)+'\n')
            record['trace_line_count']=len(observed)
            record['trace_stage_counts']={stage:sum('[hidden-oof-'+stage+']' in line for line in observed) for stage in ['before','return','commit']}
            need(all(record['trace_stage_counts'].values()),'trace did not reach all three observation seams')
        if args.with_timings and not is_trace:
            authenticate_payloads()
            state['status']='timing '+name
            wpt.save('STATE.json',state)
            timepaths=sorted(set(list(inputs['resource_pins'])+c['guard_sources']+wpt.BINARIES))
            timebefore=wpt.pins(timepaths)
            timing_output=HERE/('timing-'+name)
            command=[sys.executable,'-I','-S',str(HERE/'timing-capsule/run.py'),
                     '--binary',str(ROOT/wpt.BINARIES[0]),'--output',str(timing_output),'--label',name]
            for path,pin in timebefore.items():
                if pin is not None:
                    command.extend(['--pin',str(ROOT/path)])
            timing=state['timings'][name]={'command':command,'before':timebefore}
            try:
                timing['exit']=wpt.command('timing-'+name,command)
            except Exception as error:
                timing['exception']=repr(error)
            timing['after']=wpt.pins(timepaths)
            need(timing['before']==timing['after'],'timing changed guarded inputs')
            epoch()
            sources_expected(selected)
            need((timing_output/'RESULT.json').is_file(),'timing missing cleanup/result receipt')
            receipt=json.loads((timing_output/'RESULT.json').read_text())
            need(receipt['profileRemoved'] and not (timing_output/'profile').exists(),'timing profile cleanup incomplete')
            need(receipt['cleanupErrors']==[] and receipt['processExitAfterOwnedTermination'] is not None,'timing browser termination/reap incomplete')
            need(receipt['stable'] and receipt['before']==receipt['after'],'timing runner input drift')
            for path,pin in timebefore.items():
                if pin is not None:
                    need(receipt['before'].get(str(ROOT/path))==pin,'timing receipt differs from parent '+path)
            for name_in_capsule in ['probe.html','benchmark.js','CONFIG.json','run.py','validate.py']:
                relative='timing-capsule/'+name_in_capsule
                need(receipt['before'].get(str(HERE/relative))==inputs['payload_pins'][relative],'timing reviewed fixture drift '+relative)
            authenticate_payloads()
            timing['result_sha256']=sha(timing_output/'RESULT.json')
            timing['complete']=timing.get('exit')==0 and (timing_output/'SUMMARY.json').is_file()
            timing['status']='complete' if timing['complete'] else 'benchmark failed; correctness phases continue'
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
    for n in c['install']:
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
        state['restored']=final==before and all(not (ROOT/n).exists() for n in c['install'])
        recovery_save('FINAL.json',final)
    except BaseException as error:
        errors.append({'operation':'final snapshot','error':repr(error)})
    state['status']='terminal'
    recovery_save('STATE.json',state)
print(json.dumps(state,indent=2))
if 'failure' in state or errors or not state['restored'] or (changed and state.get('restore_build_exit')!=0):
    raise SystemExit(1)
