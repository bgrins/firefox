import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:
    raise SystemExit('Require python3 -I -S without optimization')
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib.util
import json
import re
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
spec=importlib.util.spec_from_file_location('compact_wpt',HERE/'run_wpt.py')
wpt=importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpt)
c=wpt.CONFIG
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
FLEX='layout/generic/nsFlexContainerFrame.cpp'
ABSOLUTE='layout/generic/AbsoluteContainingBlock.cpp'
phases=[('baseline','flex-baseline.cpp','absolute-baseline.cpp'),
        ('both','flex-principal.cpp','absolute-oof.cpp')]
traces=[('trace-both-column','flex-principal.cpp','absolute-oof.cpp')] if args.with_traces else []
state={'status':'starting','accepted_native_repair':False,'phases':{},'traces':{},'trace_requested':args.with_traces,'timing_requested':args.with_timings}
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

TIMING_PHASES = {'baseline', 'both'}
TIMING_FILES = ['probe.html', 'benchmark.js', 'CONFIG.json', 'run.py', 'validate.py', 'cleanup.py']

def timing_run(name, selected):
    paths = sorted(set(c['guard_sources'] + wpt.BINARIES + list(inputs['resource_pins'])))
    pins_before = wpt.pins(paths)
    timing_files = {str((HERE/'cost'/n).resolve()): sha(HERE/'cost'/n) for n in TIMING_FILES}
    expected_runner = dict(timing_files)
    for n in c['guard_sources'] + wpt.BINARIES:
        expected_runner[str((ROOT/n).resolve())] = pins_before[n]
    output = HERE/(name+'-timing')
    command = [sys.executable, '-I', '-S', str(HERE/'cost/run.py'),
               '--binary', str(ROOT/wpt.BINARIES[0]), '--output', str(output), '--label', name]
    for n in c['guard_sources']:
        command.extend(['--pin', str(ROOT/n)])
    code = wpt.command(name+'-timing-runner', command)
    pins_after = wpt.pins(paths)
    record = {'exit':code, 'before':pins_before, 'after':pins_after,
              'execution_inputs':timing_files, 'measurement_complete':False}
    wpt.save(name+'-timing-parent.json',record)
    epoch()
    sources_expected(selected)
    authenticate_payloads()
    need(pins_before == pins_after, 'timing source/binary/resource drift')
    result_path = output/'RESULT.json'
    need(result_path.is_file(), 'timing runner missing terminal cleanup receipt')
    result = json.loads(result_path.read_text())
    termination = result.get('termination') or {}
    need(result.get('before') == expected_runner and result.get('after') == expected_runner
         and result.get('stable') is True, 'timing runner pin mismatch')
    need(result.get('cleanupErrors') == [] and result.get('profileRemoved') is True
         and result.get('terminal') is True and result.get('noLiveGroup') is True
         and termination.get('terminal') is True and termination.get('noLiveGroup') is True
         and termination.get('errors') == [] and not (output/'profile').exists(),
         'timing cleanup not verified; stop and restore')
    startup = result.get('startupEnvironment') or {}
    need(startup.get('MOZ_DISABLE_SAFE_MODE_KEY') == '1'
         and startup.get('MOZ_DISABLE_UPDATE_PROCESSING') == '1'
         and startup.get('MOZ_SAFE_MODE_RESTART_removed') is True
         and type(startup.get('MOZ_SAFE_MODE_RESTART_inherited_present')) is bool,
         'controlled child startup environment missing')
    need(json.loads((output/'STARTUP-ENV.json').read_text()) == startup
         and json.loads((output/'SPAWN.json').read_text()).get('startupEnvironment') == startup,
         'startup environment receipt mismatch')
    progress = result.get('progressReceipts')
    need(type(progress) is int and 0 <= progress <= 300, 'invalid progress count')
    progress_path = output/'REQUESTS.jsonl'
    events = [json.loads(line) for line in progress_path.read_text().splitlines()] if progress_path.exists() else []
    persisted = [event['value'] for event in events if event.get('event') == 'progress-persisted']
    need(len(persisted) == progress and [value.get('sequence') for value in persisted] == list(range(progress)),
         'progress raw/count mismatch')
    record['startup_environment'] = startup
    record['progress_count'] = progress
    record['last_progress'] = persisted[-1] if persisted else None
    record['cleanup_verified'] = True
    record['runner_failure'] = result.get('failure')
    if code == 0:
        need(result.get('failure') is None and len(result.get('observations',[])) == 1,
             'successful timing runner lacks unique observation')
        validator_spec = importlib.util.spec_from_file_location('cost_validator', HERE/'cost/validate.py')
        validator = importlib.util.module_from_spec(validator_spec)
        validator_spec.loader.exec_module(validator)
        timing_config = json.loads((HERE/'cost/CONFIG.json').read_text())
        summary = validator.validate(result['observations'][0], timing_config, name)
        need(summary == json.loads((output/'SUMMARY.json').read_text()), 'timing summary disagreement')
        expected_progress = [{'stage':'script-start'}, {'stage':'config-ready','label':name}, {'stage':'fixture-start'}]
        configurations = [(k,s,n) for k in timing_config['kinds'] for s in timing_config['states'] for n in timing_config['sizes']]
        for round_no in range(-timing_config['warmup_rounds'], timing_config['measured_rounds']):
            for slot in range(len(configurations)):
                ordinal = (slot + round_no + timing_config['warmup_rounds']) % len(configurations)
                kind, visibility, count = configurations[ordinal]
                for stage in ['batch-begin','batch-end']:
                    expected_progress.append({'stage':stage,'round':round_no,'slot':slot,'ordinal':ordinal,
                                              'kind':kind,'state':visibility,'count':count})
        expected_progress.append({'stage':'result-ready','rows':summary['measuredRows']})
        expected_progress = [{'sequence':i,**value} for i,value in enumerate(expected_progress)]
        need(progress == 220 and persisted == expected_progress, 'complete measurement progress roster')
        record['measurement_complete'] = True
        record['summary'] = summary
    else:
        record['measurement_limit'] = 'Diagnostic failure retained; verified cleanup and stable inputs allow later WPT phases.'
    wpt.save(name+'-timing-parent.json',record)
    return record

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
    state['wpt_lint_exit']=wpt.command('wpt-lint',['./mach','lint','-l','wpt',*c['install']])
    need(state['wpt_lint_exit']==0,'WPT lint failed')
    for n,data in head.items():
        changed=True
        (ROOT/n).write_bytes(data)
    for name,flex,absolute in phases+traces:
        is_trace=name.startswith('trace-')
        authenticate_payloads()
        selected={FLEX:(HERE/'selected'/flex).read_bytes(),ABSOLUTE:(HERE/'selected'/absolute).read_bytes()}
        selected['layout/base/PresShell.cpp']=(HERE/'selected'/('pres-shell-trace.cpp' if is_trace else 'pres-shell-before.cpp')).read_bytes()
        selected['layout/tables/nsTableFrame.cpp']=(HERE/'selected'/('table-frame-trace.cpp' if is_trace else 'table-frame-before.cpp')).read_bytes()
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
        if args.with_timings and name in TIMING_PHASES:
            state['status']='timing '+name
            wpt.save('STATE.json',state)
            record['timing']=timing_run(name,selected)
        if is_trace:
            lines=(HERE/(name+'-wpt.log')).read_text().splitlines()
            observed=[line for line in lines if re.search(r'CV_COLUMN_(QUERY|PUBLISH)',line)]
            (HERE/name/'TRACE-LINES.json').write_text(json.dumps(observed,indent=2)+'\n')
            record['trace_line_count']=len(observed)
            record['trace_stage_counts']={stage:sum('CV_COLUMN_'+stage in line for line in observed) for stage in ['QUERY','PUBLISH']}
            need(all(record['trace_stage_counts'].values()),'trace did not reach both column observation seams')
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
        state['restored']=final==before and all(not (ROOT/n).exists() and not (ROOT/n).is_symlink() for n in c['must_be_absent'])
        recovery_save('FINAL.json',final)
    except BaseException as error:
        errors.append({'operation':'final snapshot','error':repr(error)})
    state['status']='terminal'
    recovery_save('STATE.json',state)
print(json.dumps(state,indent=2))
if 'failure' in state or errors or not state['restored'] or (changed and state.get('restore_build_exit')!=0):
    raise SystemExit(1)
