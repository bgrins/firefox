import sys
if not sys.flags.isolated or not sys.flags.no_site or sys.flags.optimize:raise SystemExit('Require python3 -B -I -S without optimization')
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,stat,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok,message):
    if not ok:raise ValueError(message)
def auth(mapping,base):
    for n,h in mapping.items():
        need(not Path(n).is_absolute() and '..' not in Path(n).parts,'safe pin')
        p=base/n;need(stat.S_ISREG(p.lstat().st_mode) and sha(p)==h,'pin '+n)
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--draft-sha',required=True);args=p.parse_args()
    need(sha(HERE/'DRAFT-FILES.json')==args.draft_sha,'checker draft');auth(read(HERE/'DRAFT-FILES.json'),HERE);auth(read(HERE/'REFERENCES.json'),ROOT)
    b=read(HERE/'CONFIG.json')
    need(b['ready_for_execution'] is True and type(b['session']) is int and b['session']>0 and type(b['session_exit']) is int and b['session_exit'] in (0,1) and all(isinstance(b[k],str) and b[k] for k in ('runtime','runtime_draft_sha256','terminal_state_sha256')),'actual terminal binding')
    runtime=ROOT/b['runtime'];base=ROOT/'artifacts/css-sign-zero-font-split-bound-v1'
    need(sha(runtime/'DRAFT-FILES.json')==b['runtime_draft_sha256'],'runtime draft');auth(read(runtime/'DRAFT-FILES.json'),runtime);auth(read(runtime/'REFERENCES.json'),ROOT)
    auth(read(base/'DRAFT-FILES.json'),base)
    for name,h in read(base/'DRAFT-FILES.json').items():
        if name not in ('CONFIG.json','REFERENCES.json'):need(sha(runtime/name)==h,'unchanged bound payload '+name)
    c=read(runtime/'CONFIG.json');old=read(base/'CONFIG.json')
    allowed={'ready_for_execution','execution_receipt','execution_receipt_sha256','required_seals'}
    need(c['ready_for_execution'] is True and {k:v for k,v in c.items() if k not in allowed}=={k:v for k,v in old.items() if k not in allowed},'reviewed activation delta')
    need(all(c['required_seals'].get(k)==v for k,v in old['required_seals'].items())
         and set(c['required_seals'])-set(old['required_seals'])=={'binding_review','binding_root_review','live_preflight'},'added exact activation reviews')
    need(sha(runtime/'CONFIG.json')==b['runtime_config_sha256'] and sha(ROOT/c['execution_receipt'])==c['execution_receipt_sha256']==b['preflight_receipt_sha256'],'exact activated config and preflight')
    for item in c['required_seals'].values():need(sha(ROOT/item['path'])==item['sha256'],'required review');auth(read(ROOT/item['path']),(ROOT/item['path']).parent)
    need(sha(ROOT/c['epoch_adapter'])==c['epoch_adapter_sha256'],'adapter body')
    adapter=load('sign_checker_epoch',ROOT/c['epoch_adapter']);prior_final,prior_pins,ids,original_binaries=adapter.bind(ROOT,ROOT/c['epoch'],c,read,sha,auth)
    parse=load('independent_sign_parse',HERE/'parse.py');state=read(runtime/'STATE.json');state_hash=sha(runtime/'STATE.json');need(state_hash==b['terminal_state_sha256'],'terminal state pin')
    before=read(runtime/'BEFORE.json');final=read(runtime/'FINAL.json')
    need(before==final==c['execution_snapshot'] and final['sources']==c['source_pins'] and len(final['sources'])==67,'full original67 source/index snapshot')
    need(all(final['sources'][n]==h for n,h in prior_final['sources'].items()),'installed stack continuity')
    need(set(state['restored_paths'])==set(c['sources']) and len(state['restored_paths'])==len(c['sources'])==40,'all40 saved sources restored')
    auth({n:before['sources'][n] for n in c['sources']},runtime/'original')
    need(set(c['sources'])=={n for n,h in before['sources'].items() if h!=c['head_pins'][n]}|set(c['candidate_pins']),'complete saved domain')
    need(read(runtime/'ORIGINAL-BINARIES.json')==original_binaries,'original binary roles')
    resources=read(runtime/'RESOURCES.json');need(resources==c['resource_pins'] and len(resources)==427,'exact427 resources')
    fixtures={n:sha(runtime/f) for n,f in c['install'].items()};need(len(fixtures)==2,'two owned fixtures')
    binaries=state['restored_binary_pins'];need(set(binaries)==set(original_binaries) and all(isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h) for h in binaries.values()),'both restored binary roles')
    final_pins={**resources,**final['sources'],**binaries};need(read(runtime/'FINAL-PINS.json')==final_pins,'complete final roles')
    need((runtime/'restore-build.log').is_file(),'retained restore build log')
    phases=state['phases'];need(set(phases)<=set(parse.PHASES),'known phases')
    policy=read(runtime/'SEMANTIC-FAILURES.json');valid={};phase_reports={};phase_errors={}
    for phase in parse.PHASES:
        directory=runtime/('wpt-'+phase)
        if directory.exists():
            if (directory/'CLEANUP.json').exists():
                need(read(directory/'CLEANUP.json')=={'owned_group_absent':True,'errors':[]},'attempted WPT cleanup '+phase)
            else:
                need('failure' in state and not any(directory.iterdir()),'only empty prelaunch WPT directory may lack cleanup')
        if phase not in phases:
            need(not directory.exists(),'unrecorded phase artifacts');continue
        record=phases[phase]
        try:
            expected_sources,expected_pins=parse.phase_pins(c,before,resources,fixtures,record,phase,original_binaries)
            need(record['build_exit']==0 and read(runtime/(phase+'-build.json'))=={'command':['./mach','build','binaries'],'exit':0},'phase build receipt')
            phase_binaries=record['binary_pins']
            raw=directory/'raw.json';need(stat.S_ISREG(raw.lstat().st_mode) and raw.stat().st_size<=128*1024*1024,'bounded regular raw')
            events=[json.loads(s) for s in raw.read_text().splitlines()];run=read(directory/'RUN.json')
            need(run['command']==['./mach','wpt','--headless','--processes=1','--log-raw='+str(raw),*c['tests']],'exact phase WPT command')
            need(run['before']==run['after']==expected_pins,'phase source/resource/built binary join')
            values,counts,landing=parse.phase(events,run,c,policy)
            need(read(runtime/(phase+'-LANDING.json'))==landing and counts=={k:v for k,v in record['subtests'].items() if v},'landing/count receipt')
            valid[phase]=values;phase_reports[phase]={'status':'VALIDATED','subtests':counts,'harness_OK':13,'landing':landing['counts'],'binary_pins':phase_binaries,'source_pins':expected_sources,'phase_pin_count':len(expected_pins),'raw_sha256':sha(raw),'run_sha256':sha(directory/'RUN.json')}
        except (ValueError,KeyError,TypeError,OSError) as error:
            phase_errors[phase]=str(error)
            phase_reports[phase]={'status':'INCOMPLETE_OR_REJECTED_PHASE_EVIDENCE','error':str(error)}
            for name in ('raw.json','RUN.json'):
                if (directory/name).is_file():phase_reports[phase][name+'_sha256']=sha(directory/name)
    comparisons={}
    for phase in parse.PHASES[1:]:
        basis=c['phase_repair_basis'][phase]
        if all(n in valid for n in ('baseline',phase,basis)):
            comparison=parse.compare(valid['baseline'],valid[phase],valid[basis],c,phase)
            try:
                need(read(runtime/(phase+'-COMPARISON.json'))==comparison==phases[phase]['semantic_comparison'],'independent comparison agreement '+phase)
                comparisons[phase]=comparison
            except (ValueError,KeyError,TypeError,OSError) as error:
                need('failure' in state,'completed campaign comparison evidence mismatch')
                phase_errors['comparison-'+phase]=str(error)
    status=parse.terminal(state,b['session_exit'],phase_errors,comparisons)
    if state.get('campaign_completed'):
        need(state['lint_exit']==0 and read(runtime/'fixture-lint.json')=={'command':['./mach','lint','--linter','wpt',*c['install']],'exit':0},'lint receipt')
    wpt=load('sign_final_live',ROOT/c['helpers']/'run_wpt.py');wpt.HERE,wpt.CONFIG=runtime,c
    need(wpt.snapshot()==final,'live final snapshot')
    index=c['index_expectations'];need(index['head']==final['head'] and index['index_entries_sha256']==final['index_entries_sha256'] and index['index_diff_sha256']==final['index_diff_sha256'] and len(index['staged_paths'])==925 and wpt.git('diff','--cached','--name-only').decode().splitlines()==index['staged_paths'],'semantic index925')
    for n,h in final_pins.items():
        path=ROOT/n
        if h is None:need(not path.exists() and not path.is_symlink(),'absent role '+n)
        else:need(stat.S_ISREG(path.lstat().st_mode) and sha(path)==h,'final role '+n)
    modified=[n for n in wpt.git('diff','--name-only').decode().splitlines() if not n.startswith('artifacts/')]
    need(modified==c['modified_native_paths'] and len(modified)==36 and not wpt.git('ls-files','--others','--exclude-standard','--','layout','dom','servo','mfbt'),'all original36 native differences')
    need(wpt.git('ls-files','--',*c['existing_tests']).decode().splitlines()==c['tracked_existing_tests'] and not wpt.git('ls-files','--',*c['install']),'readonly/owned tracked partition')
    need(len(ids)==11,'installed11 scope')
    for n,item in ids.items():
        path=ROOT/n;st=path.lstat();need(stat.S_ISREG(st.st_mode) and [st.st_dev,st.st_ino]==item['identity'] and sha(path)==item['sha256'],'installed identity '+n)
    absent=set(c['must_be_absent'])|set(c['install'])|{str(Path(n).with_name('.'+Path(n).name+'.sign-split-comparison.tmp')) for n in c['sources']}
    for n in absent:need(not (ROOT/n).exists() and not (ROOT/n).is_symlink(),'owned test/temp absent '+n)
    need(sha(runtime/'STATE.json')==state_hash,'terminal state stable')
    result={'status':status,'native_acceptance':False,'session':b['session'],'exit':b['session_exit'],'runtime_draft_sha256':b['runtime_draft_sha256'],'state_sha256':state_hash,'final_sha256':sha(runtime/'FINAL.json'),'final_pins_sha256':sha(runtime/'FINAL-PINS.json'),'source_count':len(final['sources']),'saved_sources':len(c['sources']),'resource_count':len(resources),'pin_count':len(final_pins),'native_modified_paths':len(modified),'staged_paths':925,'installed_tests':ids,'restored_binary_pins':binaries,'phases':phase_reports,'phase_errors':phase_errors,'variants':comparisons,'failure':state.get('failure'),'all_variants_passed':status=='COMPARISON_PASSED_VERIFIED_RESTORED','session_exit_supplied_by_root':True,'index_basis':'HEAD, full staged entries and cached binary diff plus exact925path roster; no repeated blob loop'}
    with (HERE/'ROOT-FINAL-CHECK.json').open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
