from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
RUNTIME=ROOT/'artifacts/css-accepted-119-121-122-install-runtime-v1'
CHECKER=ROOT/'artifacts/css-accepted-119-121-122-final-checker-bound-v1'
SEALS={
    'artifacts/css-accepted-119-121-122-install-runtime-v1/FILES.json':'4a4700e2a241033ad22f258ee3d4448b8828cf4ef4b9ae9267ea9cd5617829c2',
    'artifacts/css-accepted-119-121-122-final-checker-bound-v1/FILES.json':'395a0310e7a67d3d2155febacb0b11b0289a58c647abc996d53dcf236672e108',
}


def need(ok,why):
    if not ok:raise RuntimeError(why)


def artifact(path):
    need((ROOT/'artifacts').resolve() in path.resolve().parents,'archive-only input')
    need(stat.S_ISREG(path.lstat().st_mode),'regular archive input')
    return path


def sha(path):return hashlib.sha256(artifact(path).read_bytes()).hexdigest()
def read(path):return json.loads(artifact(path).read_text())


def authenticate(mapping,base):
    for n,h in mapping.items():
        need(not Path(n).is_absolute() and '..' not in Path(n).parts,'safe artifact pin')
        need(sha(base/n)==h,'pin '+n)


def manifest(path,digest):
    need(sha(path)==digest,'manifest '+str(path))
    authenticate(read(path),path.parent)


def load(name,path):
    artifact(path)
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def recount(events,c):
    names=c['expected_subtests'];refs=set(c['reftests']);files=set(names)|refs
    rows=[];starts=[];ends=[];finished=set();active=None;state='before';registered=[]
    for e in events:
        need(isinstance(e,dict),'event object')
        a=e.get('action')
        need(a not in ('crash','suite_abort','test_abort'),'no infrastructure abort/crash')
        if a=='log':need(e.get('level','').upper() not in ('ERROR','CRITICAL'),'no error log')
        if a=='process_exit':need(e.get('exitcode',e.get('returncode',0))==0,'clean process exit')
        if a=='assertion_count':need(e.get('min_expected',0)<=e['count']<=e.get('max_expected',0),'assertion count')
        if a in ('log','process_output'):
            need(not any(word in e.get('message','')+e.get('data','') for word in
                 ('PROCESS-CRASH','TEST-UNEXPECTED-ERROR','TEST-UNEXPECTED-TIMEOUT')),'infrastructure marker')
        if a=='suite_start':
            need(state=='before','one suite start');state='running'
        elif a=='test_start':
            need(state=='running' and active is None and e['test'] in files-finished,'file start')
            active=e['test'];registered=[];starts.append(e)
        elif a=='test_status':
            need(state=='running' and active in names and e['test']==active and e['status'] in ('PASS','FAIL'),'completed active row')
            registered.append(e['subtest']);rows.append(e)
        elif a=='test_end':
            need(state=='running' and active is not None and e['test']==active,'file end')
            need(registered==(names[active] if active in names else []),'exact registration order')
            need(e['status']==('OK' if active in names else 'PASS'),'all harnesses OK and all references PASS')
            finished.add(active);active=None;ends.append(e)
        elif a=='suite_end':
            need(state=='running' and active is None and finished==files,'complete suite end');state='done'
    need(state=='done' and len(rows)==1382 and len(starts)==len(ends)==35,'complete actual scope')
    values={(e['test'],e['subtest']):{k:e.get(k) for k in ('status','message','expected','known_intermittent')} for e in rows}
    need(len(values)==1382,'unique rows')
    values.update({(e['test'],'<reftest>'):{k:e.get(k) for k in ('status','message','expected','known_intermittent')}
                   for e in ends if e['test'] in refs})
    return rows,starts,ends,values


def main():
    for n,h in SEALS.items():manifest(ROOT/n,h)
    c=read(RUNTIME/'CONFIG.json');state=read(RUNTIME/'STATE.json')
    root_receipt=read(RUNTIME/'ROOT-FINAL-CHECK.json')
    root_hash='165eefd709b256dadff5982f0018386b2618c0255e39dcc822f68ebcb47a664a'
    need(sha(RUNTIME/'ROOT-FINAL-CHECK.json')==root_hash,'genuine root receipt hash')
    need(root_receipt==read(CHECKER/'ROOT-FINAL-CHECK.json')==read(CHECKER/'root-check.log'),'root output/copy equality')
    need(state==read(RUNTIME/'driver.log'),'actual terminal driver output')
    execution=read(RUNTIME/'ROOT-CHECKER-EXECUTION.json')
    expected_execution={'runtime_session':28306,'runtime_exit':0,'root_checker_session':45302,
                        'root_checker_exit':0,'actual_exits_observed_by_root':True}
    need(all(execution[k]==v for k,v in expected_execution.items()) and read(CHECKER/'EXECUTION.json')==expected_execution,
         'actual root-observed executions')
    need(execution['root_checker_directory']==str(CHECKER.relative_to(ROOT))
         and execution['root_checker_draft_sha256']==sha(CHECKER/'DRAFT-FILES.json')
         and execution['root_checker_files_sha256']==SEALS[str(CHECKER.relative_to(ROOT)/'FILES.json')]
         and execution['root_receipt_sha256']==root_hash and execution['native_acceptance'] is False,'actual checker joins')
    manifest(ROOT/execution['checker_review']/'FILES.json',execution['checker_review_files_sha256'])
    for directory in (RUNTIME,CHECKER):
        authenticate(read(directory/'DRAFT-FILES.json'),directory)
        authenticate(read(directory/'REFERENCES.json'),ROOT)
    b=read(CHECKER/'CONFIG.json');bound=ROOT/b['bound_installer']
    need(b['ready_for_execution'] is True and b['session']==28306 and b['session_exit']==0
         and b['runtime']==str(RUNTIME.relative_to(ROOT))
         and b['runtime_draft_sha256']==sha(RUNTIME/'DRAFT-FILES.json')
         and b['runtime_config_sha256']==sha(RUNTIME/'CONFIG.json')
         and b['terminal_state_sha256']==sha(RUNTIME/'STATE.json'),'actual checker configuration')
    manifest(bound/'DRAFT-FILES.json',b['bound_installer_draft_sha256'])
    disabled=read(bound/'CONFIG.json');activation={'ready_for_execution','epoch_adapter_review','execution_review'}
    need(disabled['ready_for_execution'] is False and c['ready_for_execution'] is True
         and set(c)==set(disabled) and all(c[k]==v for k,v in disabled.items()if k not in activation), 'only reviewed activation fields')
    for n,h in read(bound/'DRAFT-FILES.json').items():
        if n not in ('CONFIG.json','REFERENCES.json'):need(sha(RUNTIME/n)==h,'reviewed bound payload '+n)
    producer=ROOT/'artifacts/css-accepted-119-121-122-install-v1'
    for n,h in read(producer/'DRAFT-FILES.json').items():
        if n not in ('CONFIG.json','REFERENCES.json','BINDING.md'):need(sha(RUNTIME/n)==h,'original reviewed science '+n)
    gates=load('review_archive_gates',RUNTIME/'gates.py')
    epoch,prior,originals,resources=gates.archive_inputs(ROOT,RUNTIME,c,read,sha,authenticate,load,need)
    before,final,pins=read(RUNTIME/'BEFORE.json'),read(RUNTIME/'FINAL.json'),read(RUNTIME/'FINAL-PINS.json')
    installation=read(RUNTIME/'INSTALLATION.json')
    need(before==c['execution_snapshot'] and before==read(ROOT/c['epoch']/'FINAL.json'),'prior restored snapshot continuity')
    need(len(originals)==7 and all(sha(RUNTIME/'original'/n)==h for n,h in originals.items()),'saved original bodies')
    need(all(sha(ROOT/c['candidate_sources'][n])==h for n,h in c['candidate_pins'].items()),'reviewed installed source bodies')
    need(final['sources']=={**before['sources'],**c['candidate_pins']} and len(final['sources'])==72,'all final sources')
    need(all(final[k]==before[k]==c['index_expectations'][k] for k in ('head','index_diff_sha256','index_entries_sha256')),
         'HEAD/full index/cached diff preserved')
    prior_config=read(ROOT/c['epoch']/'CONFIG.json')
    need(c['index_expectations']==prior_config['index_expectations']
         and len(c['index_expectations']['staged_paths'])==len(c['index_expectations']['staged_payload_sha256'])==925,'complete prior stage mapping')
    need(state['status']=='terminal' and state['installed'] is True and state['restored'] is False
         and state['recovery_errors']==[] and 'failure' not in state and state['build_exit']==state['lint_exit']==0,
         'successful installation state')
    need(state['sources']==sorted(originals) and c['accepted_fixes']==[119,121,122]
         and c['accepted_but_uninstalled_excluded_fixes']==[123,124] and c['excluded_fixes']==[120],'accepted scoped source mutation')
    accepted={n:v['sha256']for n,v in c['acceptances'].items()}
    need(state['acceptance_sha256']==installation['acceptance_sha256']==accepted,'accepted input hashes')
    fixtures={n:sha(RUNTIME/path)for n,path in c['install'].items()}
    binaries=state['installed_binary_pins']
    final_roles={**resources,**final['sources'],**{n:fixtures[n] if n in c['persistent_tests'] else None for n in fixtures},**binaries}
    need(pins==final_roles and len(resources)==505 and len(pins)==579,'full final roles')
    allowed_changes=set(originals)|set(binaries)|set(c['persistent_tests'])
    need(all(n in pins and (n in allowed_changes or pins[n]==h)for n,h in prior.items()),'every non-owned prior role preserved')
    need(all(pins[n] is None for n in c['temporary_tests']+c['must_be_absent']),'two temporary and all permanent absences')
    need(installation['before']==before and installation['after']==final
         and installation['original_source_pins']==originals and installation['installed_source_pins']==c['candidate_pins']
         and installation['prior_installed_tests']==c['installed_tests']
         and installation['temporary_tests_removed']==sorted(c['temporary_tests'])
         and installation['binary_pins']==binaries,'installation record joins')
    owned=installation['owned_tests'];identities={**c['installed_tests'],**owned}
    need(len(c['installed_tests'])==11 and len(owned)==4 and len(identities)==15
         and set(owned)==set(c['persistent_tests']) and all(owned[n]['sha256']==fixtures[n]for n in owned)
         and identities==root_receipt['installed_tests'],'eleven retained and four new installed identities')
    need(all(len(v['identity'])==2 and all(type(x)is int for x in v['identity'])
             and pins[n]==v['sha256']for n,v in identities.items())
         and len({tuple(v['identity'])for v in identities.values()})==15,'exact distinct identities and body pins')
    need(read(RUNTIME/'installed-build.json')=={'command':['./mach','build','binaries'],'exit':0}
         and read(RUNTIME/'fixture-lint.json')=={'command':['./mach','lint','--linter','wpt',*c['install']],'exit':0},'actual successful build/lint')
    need(read(RUNTIME/'ORIGINAL-BINARIES.json')==epoch['restored_binary_pins'],'actual baseline binaries')
    parse=load('review_final_parser',CHECKER/'parse.py')
    policy=load('review_install_policy',RUNTIME/'policy.py')
    architecture=load('review_architecture',RUNTIME/'architecture.py')
    phases={};outcomes={};repair_groups={}
    for phase in ('baseline','candidate'):
        directory=RUNTIME/('wpt-'+phase);events=[json.loads(line)for line in artifact(directory/'raw.json').read_text().splitlines()]
        run=read(directory/'RUN.json');rows,starts,ends,values=recount(events,c)
        need(run['rows']==rows and run['starts']==starts and run['ends']==ends
             and run['infrastructure_faults']==[] and run['complete'] is True,'independent exact raw/RUN join')
        unexpected=any(e['status']!=e.get('expected',e['status']) and e['status']not in e.get('known_intermittent',[])for e in rows+ends)
        need(run['exit']==(1 if unexpected else 0),'metadata-aware actual WPT exit')
        need(read(directory/'CLEANUP.json')=={'owned_group_absent':True,'errors':[]},'owned process group absent')
        source_map=before['sources'] if phase=='baseline' else final['sources']
        binary_map=epoch['restored_binary_pins'] if phase=='baseline' else binaries
        phase_pins={**resources,**source_map,**fixtures,**binary_map}
        need(run['before']==run['after']==phase_pins,'complete stable phase roles')
        need(run['command']==['./mach','wpt','--headless','--processes=1','--log-raw='+str(directory/'raw.json'),*c['tests']], 'actual WPT command')
        arch=read(RUNTIME/(phase+'-ARCHITECTURE.json'))
        need(arch['status']=='SUPPORTED_64_BIT_PHASE_BINARIES' and arch['binary_pins']==binary_map
             and set(arch['binaries'])==set(binary_map),'architecture byte domains')
        cpus=set()
        for n,h in binary_map.items():
            item=arch['binaries'][n]
            need(item=={**architecture.header(bytes.fromhex(item['header_hex']),item['size'],Path(n).name),'sha256':h},'exact MachO64 receipt')
            cpus.add(item['cpu_type'])
        need(len(cpus)==1,'matching CPU architecture')
        landing=parse.landing(rows,c,phase,policy.semantic_failure)
        need(landing==policy.phase(c,run,phase,need)==state['phases'][phase]==read(RUNTIME/(phase+'-LANDING.json')),'landing and calibration classifiers')
        parsed_rows,parsed_values,counts=parse.raw(events,run,c)
        need(parsed_rows==rows and parsed_values==values and counts==dict(Counter(r['status']for r in rows)),'independent parser cross-check')
        info=root_receipt['phases'][phase]
        need(info['status']=='VERIFIED' and info['counts']==counts and info['landing']==landing
             and info['raw_sha256']==sha(directory/'raw.json') and info['run_sha256']==sha(directory/'RUN.json')
             and info['architecture_sha256']==sha(RUNTIME/(phase+'-ARCHITECTURE.json'))
             and info['source_pins']==source_map and info['binary_pins']==binary_map,'root phase joins')
        outcomes[phase]=values
        phases[phase]={'counts':counts,'harness_OK':29,'reftest_PASS':6,'mandatory_landing_PASS':landing['mandatory_landing_passes'],
            'WPT_exit':run['exit'],'raw_sha256':sha(directory/'raw.json'),'run_sha256':sha(directory/'RUN.json'),
            'remaining_FAIL_by_file':dict(Counter(r['test']for r in rows if r['status']=='FAIL'))}
    old,new=outcomes['baseline'],outcomes['candidate']
    need(old.keys()==new.keys() and len(old)==1388,'paired complete outcomes')
    regressions=[list(k)for k in old if old[k]['status']=='PASS' and new[k]['status']!='PASS']
    changed=[list(k)for k in old if old[k]['status']==new[k]['status']=='FAIL' and old[k]!=new[k]]
    repaired=[list(k)for k in old if old[k]['status']=='FAIL' and new[k]['status']=='PASS']
    comparison={'status':'PASSED' if not regressions and not changed else 'REJECTED','regressions':regressions,
                'changed_failures':changed,'repaired':repaired,'forced_repair_count':None,'new_acceptance':False}
    need(comparison==parse.compare(old,new)==read(RUNTIME/'INTEGRATION-CHECK.json')==state['integration']==root_receipt['comparison'],
         'independent preservation comparison')
    need(comparison['status']=='PASSED' and len(repaired)==20,'observed twenty repairs and no regression')
    for k,v in {'status':'INSTALLED_VERIFIED','fixes':[119,121,122],'native_acceptance':False,'session':28306,'exit':0,
                'source_count':72,'saved_sources':7,'resource_count':505,'pin_count':579,'native_modified_paths':41,
                'staged_paths':925,'phase_errors':{},'failure':None,'retained_installation_record_is_current':True,
                'session_exit_supplied_by_root':True,'binary_pins':binaries}.items():need(root_receipt[k]==v,'root result '+k)
    for k,n in {'runtime_draft_sha256':'DRAFT-FILES.json','state_sha256':'STATE.json','final_sha256':'FINAL.json',
                'final_pins_sha256':'FINAL-PINS.json'}.items():need(root_receipt[k]==sha(RUNTIME/n),'root sealed state '+k)
    receipt={'status':'SCOPED_INSTALLED_INTEGRATION_GO','runtime_manifest_sha256':SEALS[str(RUNTIME.relative_to(ROOT)/'FILES.json')],
        'root_receipt_sha256':root_hash,'checker_manifest_sha256':SEALS[str(CHECKER.relative_to(ROOT)/'FILES.json')],
        **expected_execution,'phases':phases,'repairs':len(repaired),'repairs_by_file':dict(Counter(k[0]for k in repaired)),
        'regressions':regressions,'changed_retained_FAIL':changed,'source_guards':72,'saved_originals':7,
        'persistent_resources':505,'final_roles':579,'native_differences':41,'staged_paths':925,
        'retained_installed_identities':11,'new_installed_identities':4,'installed_identities':15,'temporary_fixtures_removed':2,
        'installed_binary_pins':binaries,'root_live_corroboration_authenticated':True,'reviewer_live_check_performed':False,
        'reviewer_authored_epoch_adapter':True,'reviewer_authored_installer_driver':False,
        'native_acceptance':False,'new_fix_count':0}
    (HERE/'CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
