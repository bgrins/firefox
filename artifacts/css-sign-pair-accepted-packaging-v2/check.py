import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def auth(mapping, base):
    for name, digest in mapping.items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'safe pin')
        need(sha(base / name) == digest, 'pin ' + name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(args.output.is_absolute() and not args.output.exists() and not args.output.is_symlink()
         and HERE not in args.output.parents, 'absent external receipt')
    refs = read(HERE / 'REFERENCES.json')
    auth(refs, ROOT)
    capsules = {}
    for path in refs:
        if Path(path).name in ('FILES.json', 'DRAFT-FILES.json'):
            manifest = read(ROOT / path); auth(manifest, (ROOT / path).parent); capsules[path] = len(manifest)
    plan = read(HERE / 'PLAN.json')
    need(plan['execution_enabled'] is False and plan['signing_parent'] is None
         and plan['installation_pending'] is True and plan['installation'] is None,
         'disabled installation/signing boundary')
    need(plan['commit_order'] == ['raw-research','raw-native','sign-research','sign-native'], 'four ordered recipes')
    research_sets = {}
    proposal = ROOT / 'artifacts/css-sign-zero-font-split-proposal-v1'
    previous = ROOT / 'artifacts/css-sign-pair-candidate-packaging-v1'
    accepted = {}
    for role, fix in [('raw',119),('sign',120)]:
        pointer = plan['acceptance_'+role]; need(sha(ROOT/pointer['path']) == pointer['sha256'], 'acceptance pointer')
        acceptance = accepted[role] = read(ROOT/pointer['path'])
        need(acceptance['status']=='SCOPED_ACCEPTED' and acceptance['fix']==fix
             and acceptance['candidate_installed'] is False and acceptance['installation'] is None,
             'actual scoped acceptance, installation pending')
        for kind in ('research','native'):
            recipe = read(HERE/(role+'-'+kind+'.draft.json'))
            need(recipe['fix']==fix and recipe['acceptance']==pointer and recipe['execution_enabled'] is False,
                 'recipe acceptance')
            need(all(recipe[k] is None for k in ('expected_head','signing_parent','commit_hash','bug','installation')),
                 'unknown signing and install facts remain null')
            need(recipe['reviewers']==['#firefox-style-system-reviewers']
                 and recipe['message'].startswith('No bug - ')
                 and 'r?#firefox-style-system-reviewers' in recipe['message'], 'authorized message/reviewer')
            if kind=='research':
                need(set(recipe['files'])==set(recipe['source_pins']) and len(recipe['files'])==len(set(recipe['files'])), 'exact selected research map')
                need(all(n.startswith('artifacts/') for n in recipe['files']), 'research-only paths')
                auth(recipe['source_pins'],ROOT);research_sets[role]=set(recipe['files'])
            else:
                patch=ROOT/recipe['patch'];need(sha(patch)==recipe['patch_sha256']==acceptance['patch']['sha256'], 'accepted exact patch')
                need(patch.read_bytes()==(proposal/(role+'.patch')).read_bytes(), 'unchanged previously tested patch')
                paths=re.findall(r'^diff --git a/(\S+) b/\1$',patch.read_text(),re.M)
                need(paths==recipe['files']==acceptance['native_paths'] and len(paths)==(4 if role=='raw' else 2), 'native-only exact scope')
                need(not any(p.startswith('artifacts/') for p in paths), 'no tooling/docs in native commit')
                auth(recipe['source_pins'],proposal/role)
                prior=read(previous/(role+'-native.draft.json'))
                need(recipe['source_pins']==prior['source_pins'], 'same transport-certified postimages')
        if role=='sign':
            native=read(HERE/'sign-native.draft.json')
            need(acceptance['semantic_prerequisite']==119 and native['semantic_prerequisite_fix']==119
                 and native['semantic_prerequisite']=='raw-native' and native['independently_cherry_pickable_on_tested_base'] is False,
                 'Sign requires119')
            need(native['prerequisite_source_pins']=={n:h for n,h in read(HERE/'raw-native.draft.json')['source_pins'].items() if n.endswith('.rs')}, 'exact raw prerequisite postimages')
    need(not research_sets['raw'] & research_sets['sign'], 'research selections deduplicated')
    need((HERE/'combined-review-only.patch').read_bytes()==(proposal/'raw.patch').read_bytes()+(proposal/'sign.patch').read_bytes(), 'review-only combined exact concat')
    runtime=ROOT/accepted['raw']['runtime'];need(accepted['sign']['runtime']==accepted['raw']['runtime'], 'same actual campaign')
    need(sha(runtime/'FILES.json')==accepted['raw']['runtime_files_sha256']==accepted['sign']['runtime_files_sha256'], 'actual runtime manifest')
    root=read(runtime/'ROOT-FINAL-CHECK.json');state=read(runtime/'STATE.json');config=read(runtime/'CONFIG.json')
    need(root['status']=='COMPARISON_PASSED_VERIFIED_RESTORED' and root['session']==80904 and root['exit']==0,
         'successful terminal restoration')
    need(root['state_sha256']==sha(runtime/'STATE.json') and root['final_sha256']==sha(runtime/'FINAL.json')
         and root['final_pins_sha256']==sha(runtime/'FINAL-PINS.json'), 'root payload hash joins')
    need(state['status']=='terminal' and state['restored'] is True and state['restore_build_exit']==0
         and state['recovery_errors']==[] and 'failure' not in state and state['all_variants_passed'] is True,
         'actual completed and restored campaign')
    need(read(runtime/'BEFORE.json')==read(runtime/'FINAL.json')==config['execution_snapshot'], 'restored source/index snapshot')
    review=read(ROOT/'artifacts/css-sign-split-terminal-results-review-v1/CHECK.json')
    need(review['status']=='SCOPED_RESULTS_AND_ARCHIVED_RESTORATION_GO', 'independent final review')
    spec=importlib.util.spec_from_file_location('frozen_sign_tests',runtime/'tests.py');tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
    runs={};counts={}
    for phase,wanted in [('baseline',{'PASS':996,'FAIL':41}),('raw_only',{'PASS':1002,'FAIL':35}),('raw_plus_sign',{'PASS':1007,'FAIL':30})]:
        directory=runtime/('wpt-'+phase)
        events=[json.loads(line) for line in (directory/'raw.json').read_text().splitlines()]
        run=read(directory/'RUN.json');runs[phase]=run
        for action,key in [('test_status','rows'),('test_start','starts'),('test_end','ends')]:
            need([e for e in events if e.get('action')==action]==run[key], 'raw/RUN exact '+phase+'/'+key)
        need(run['complete'] and run['before']==run['after'] and not tests.infrastructure_faults(events), 'complete preserved phase')
        need(tests.exit_matches_results(run['exit'],run['rows']+run['ends']), 'metadata-aware process exit')
        need(len(run['rows'])==1037 and len(run['ends'])==13 and all(e['status']=='OK' for e in run['ends']), 'exact campaign scope')
        need(len({(r['test'],r['subtest']) for r in run['rows']})==1037, 'unique identities')
        for test,names in config['expected_subtests'].items():need([r['subtest'] for r in run['rows'] if r['test']==test]==names,'ordered frozen roster')
        counts[phase]={s:sum(r['status']==s for r in run['rows']) for s in ('PASS','FAIL')};need(counts[phase]==wanted,'actual phase outcomes')
        record=state['phases'][phase]
        expected_sources={**config['head_pins'],**{n:config['candidate_pins'][n] for n in config['phase_candidate_paths'][phase]}}
        need(record['source_before_build']==record['source_after_build'] and record['source_before_build']['sources']==expected_sources
             and record['build_exit']==0, 'phase isolation/build')
        need(all(run['before'][n]==h for n,h in {**expected_sources,**record['binary_pins']}.items()),'phase built-binary/source join')
        need(read(directory/'CLEANUP.json')=={'owned_group_absent':True,'errors':[]}, 'phase process cleanup')
    wpt=SimpleNamespace(CONFIG=config,need=need,save=lambda *args:None)
    repairs={}
    for role,phase,basis,count in [('raw','raw_only','baseline',6),('sign','raw_plus_sign','raw_only',5)]:
        comparison=json.loads(json.dumps(tests.compare(wpt,runs['baseline'],runs[phase],phase,runs[basis])))
        need(comparison==read(runtime/(phase+'-COMPARISON.json'))==review['comparisons'][phase]
             and comparison['status']=='PASSED' and len(comparison['own_repaired'])==count, 'paired preservation and independent review')
        repairs[role]=count
    selected=research_sets['raw']|research_sets['sign']
    receipt={'status':'ACCEPTED119_120_PACKAGING_VERIFIED_DISABLED','fixes':[119,120],
             'research_files':{role:len(v) for role,v in research_sets.items()},'selected_bytes':sum((ROOT/n).stat().st_size for n in selected),
             'native_paths':[4,2],'landing_cases':[8,11],'repairs':repairs,'phase_counts':counts,
             'authenticated_capsules':capsules,'execution_enabled':False,'sign_requires119':True,
             'installation_pending':True,'signed_parents_bound':False,'live_native_index_binary_reads':False,
             'replay_scope':'Selected archived provenance/phase recount; prior exact-patch transport receipts reused. No compiler/browser/Git or recursive replay.'}
    args.output.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='authenticated_capsules'}))


if __name__=='__main__':main()
