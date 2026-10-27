from collections import Counter
import math
import re

FIELDS=('status','message','expected','known_intermittent')
PHASES=('baseline','raw_only','raw_plus_sign')

def need(ok,message):
    if not ok:raise ValueError(message)

def semantic_failure(policy,name,message):
    if name not in policy or not isinstance(message,str) or len(message.encode())>4096:return False
    number=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
    m=re.fullmatch('assert_equals: (.+) expected ('+number+') but got ('+number+')',message)
    if not m:return False
    label,want,actual=m.groups();want,actual=float(want),float(actual);rule=policy[name]
    return label in rule['assertions'] and all(map(math.isfinite,(want,actual))) and want==rule['assertions'][label] and actual!=want and rule['actual_range'][0]<=actual<=rule['actual_range'][1]

def phase(events,run,c,policy):
    roster=c['expected_subtests'];names={(t,n) for t,ns in roster.items() for n in ns}
    need(len(names)==sum(map(len,roster.values()))==1037 and len(roster)==13,'exact1037/13 planned identities')
    opened=False;closed=False;active=set();finished=set();rows=[];starts=[];ends=[];faults=[]
    for e in events:
        a=e.get('action')
        if a in ('crash','suite_abort','test_abort'):faults.append(e)
        if a=='log' and e.get('level','').upper() in ('ERROR','CRITICAL'):faults.append(e)
        if a=='process_exit' and e.get('exitcode',e.get('returncode',0))!=0:faults.append(e)
        if a=='assertion_count' and not e.get('min_expected',0)<=e['count']<=e.get('max_expected',0):faults.append(e)
        if a in ('log','process_output') and any(s in e.get('message','')+e.get('data','') for s in ('PROCESS-CRASH','TEST-UNEXPECTED-ERROR','TEST-UNEXPECTED-TIMEOUT')):faults.append(e)
        if a=='suite_start':need(not opened and not closed,'single suite start');opened=True
        elif a=='suite_end':need(opened and not active and finished==set(roster),'complete suite end');closed=True;opened=False
        elif a=='test_start':
            t=e['test'];need(opened and t in roster and t not in active|finished,'test start lifecycle');active.add(t);starts.append(e)
        elif a=='test_status':need(e['test'] in active and e['status'] in ('PASS','FAIL'),'active ordinary result');rows.append(e)
        elif a=='test_end':
            t=e['test'];need(t in active and e['status']=='OK','active OK harness');active.remove(t);finished.add(t);ends.append(e)
    need(closed and not opened and not faults and len(starts)==len(ends)==13,'complete clean13 harnesses')
    need(len(rows)==len({(r['test'],r['subtest']) for r in rows})==1037,'unique1037 rows')
    for t,ns in roster.items():need([r['subtest'] for r in rows if r['test']==t]==ns,'exact ordered roster '+t)
    need(run['rows']==rows and run['starts']==starts and run['ends']==ends and run['infrastructure_faults']==[] and run['complete'] is True,'raw/RUN completeness')
    unexpected=any(e['status']!=e.get('expected',e['status']) and e['status'] not in e.get('known_intermittent',[]) for e in rows+ends)
    need(run['exit']==(1 if unexpected else 0),'metadata-aware exit')
    main=[r for r in rows if r['test'] in c['landing_tests']];need(len(main)==19,'all19 landing identities')
    failures=[r for r in main if r['status']=='FAIL']
    need(all(semantic_failure(policy,r['subtest'],r.get('message')) for r in failures),'landing calibration/control failure')
    values={(r['test'],r['subtest']):{k:r.get(k) for k in FIELDS} for r in rows}
    landing={'counts':{s:sum(r['status']==s for r in main) for s in ('PASS','FAIL')},'failures':failures,'calibration_failure_rejected':False,'required_baseline_failure_count':None,'later_semantic_assertions_after_failure':'NOT_REACHED'}
    return values,dict(Counter(r['status'] for r in rows)),landing

def compare(old,new,basis,c,which):
    need(old.keys()==new.keys()==basis.keys(),'paired identities')
    regressions=[list(k) for k in old if old[k]['status']=='PASS' and new[k]['status']!='PASS']
    changed=[list(k) for k in old if old[k]['status']==new[k]['status']=='FAIL' and old[k]!=new[k]]
    basis_regressions=[list(k) for k in basis if basis[k]['status']=='PASS' and new[k]['status']!='PASS']
    basis_changed=[list(k) for k in basis if basis[k]['status']==new[k]['status']=='FAIL' and basis[k]!=new[k]]
    repaired=[list(k) for k in old if old[k]['status']=='FAIL' and new[k]['status']=='PASS']
    own=[list(k) for k in basis if basis[k]['status']=='FAIL' and new[k]['status']=='PASS' and k[0] in c['phase_repair_tests'][which]]
    failures=[list(k) for k in new if k[0] in c['phase_required_tests'][which] and new[k]['status']!='PASS']
    return {'status':'PASSED' if not (regressions or changed or basis_regressions or basis_changed or failures) and own else 'REJECTED','regressions':regressions,'changed_failures':changed,'repaired':repaired,'repair_basis_regressions':basis_regressions,'repair_basis_changed_failures':basis_changed,'required_landing_failures':failures,'own_repaired':own,'repair_basis':c['phase_repair_basis'][which],'native_acceptance':False}

def phase_pins(c,before,resources,fixtures,record,which,binary_names):
    sources={**c['head_pins'],**{n:c['candidate_pins'][n] for n in c['phase_candidate_paths'][which]}}
    snapshot=record['source_before_build']
    need(snapshot==record['source_after_build'] and snapshot['sources']==sources
         and set(sources)==set(before['sources'])==set(c['guard_sources'])
         and all(snapshot[k]==before[k] for k in ('head','index_entries_sha256','index_diff_sha256')),
         'exact phase source map/build stability')
    need(resources==c['resource_pins'] and set(fixtures)==set(c['install']), 'phase resource/fixture domains')
    binaries=record['binary_pins']
    need(set(binaries)==set(binary_names) and all(isinstance(h,str) and re.fullmatch('[0-9a-f]{64}',h) for h in binaries.values()),'phase built binary roles')
    return sources,{**resources,**sources,**fixtures,**binaries}

def terminal(state,code,phase_errors,comparisons):
    need(state['status']=='terminal' and state['restored'] is True and state['restore_build_exit']==0 and state['recovery_errors']==[] and state['accepted_native_repair'] is False,'verified restoration terminal contract')
    if 'failure' in state:
        need(code==1 and isinstance(state['failure'],dict) and bool(state['failure'].get('message')) and not state.get('campaign_completed',False),'failed campaign terminal contract')
        return 'INFRASTRUCTURE_OR_CALIBRATION_FAILURE_VERIFIED_RESTORED'
    need(state.get('campaign_completed') is True and not phase_errors and set(state['phases'])==set(PHASES) and set(comparisons)==set(PHASES[1:]),'complete campaign evidence')
    passed=all(v['status']=='PASSED' for v in comparisons.values())
    need(type(state['all_variants_passed']) is bool and state['all_variants_passed']==passed and code==(0 if passed else 1),'semantic verdict/process exit join')
    return 'COMPARISON_PASSED_VERIFIED_RESTORED' if passed else 'SEMANTIC_REJECTION_VERIFIED_RESTORED'
