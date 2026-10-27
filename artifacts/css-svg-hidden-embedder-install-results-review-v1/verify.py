from pathlib import Path
import json,hashlib,collections
R=Path('artifacts/css-svg-hidden-embedder-install-runtime-v1')
O=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((R/n).read_text())
assert sha(R/'FILES.json')=='5305ff78870d5b150141ac0f18a08149692f9423ec0b7626efa907ae41f1edbd'
manifest=read('FILES.json')
for p,v in manifest.items():assert sha(R/p)==v,p
root=read('ROOT-FINAL-CHECK.json');state=read('STATE.json');config=read('CONFIG.json');inst=read('INSTALLATION.json');before=read('BEFORE.json');final=read('FINAL.json');pins=read('FINAL-PINS.json');run=read('wpt-candidate/RUN.json')
assert sha(R/'ROOT-FINAL-CHECK.json')=='77a97d1ae0b8fdec1a7a954f873d6113aaeb312548a5b422b9474a459d39d48b'
for key,path in [('state_sha256','STATE.json'),('final_sha256','FINAL.json'),('final_pins_sha256','FINAL-PINS.json'),('raw_sha256','wpt-candidate/raw.json'),('run_sha256','wpt-candidate/RUN.json')]:assert root[key]==sha(R/path)
assert root['status']=='INSTALLED_VERIFIED' and root['session']==39391 and root['exit']==0
assert state['status']=='terminal' and state['installed'] and not state['restored'] and not state['recovery_errors']
assert state['build_exit']==state['lint_exit']==read('installed-build.json')['exit']==read('fixture-lint.json')['exit']==0
assert inst['before']==before and inst['after']==final
assert len(final['sources'])==56
assert set(inst['installed_source_pins'])==set(config['sources'])==set(config['candidate_pins'])
assert inst['installed_source_pins']==config['candidate_pins']
assert set(k for k,v in before['sources'].items() if final['sources'][k]!=v)==set(config['sources'])
for path,value in config['candidate_pins'].items():
 assert final['sources'][path]==value==sha(Path(config['candidate_sources'][path]))
 assert inst['original_source_pins'][path]==before['sources'][path]
for k in ['head','index_diff_sha256','index_entries_sha256']:assert before[k]==final[k]
assert final['head']==config['head']=='90e7c8a3c46c5e84ec0bfffc239e52ea72b2085e'
assert final['index_diff_sha256']=='3ecc566a1cb1a78aab07c4f272b627d59f7888dec4adf563274849a966047272'
assert final['index_entries_sha256']=='e52cf295947403cec7f6cba85bc15a6b539aaa5591df17101dfb5098e3747e21'
assert sum(v!=config['head_pins'][p] for p,v in before['sources'].items())==30
assert sum(v!=config['head_pins'][p] for p,v in final['sources'].items())==33
assert len(config['installed_tests'])==8 and len(inst['owned_tests'])==1
assert root['installed_tests']=={**config['installed_tests'],**inst['owned_tests']}
assert len(root['installed_tests'])==9 and root['staged_paths']==925
for path,v in inst['owned_tests'].items():assert v['sha256']==sha(R/config['install'][path])
assert state['installed_binary_pins']==inst['binary_pins']==root['installed_binary_pins']
expectedpins={**read('RESOURCES.json'),**final['sources'],**inst['binary_pins'],**{p:v['sha256'] for p,v in inst['owned_tests'].items()}}
assert pins==expectedpins and len(pins)==405
assert run['before']==run['after']==pins and run['exit']==0 and run['complete'] and not run['infrastructure_faults']
events=[json.loads(line) for line in (R/'wpt-candidate/raw.json').read_text().splitlines() if line.strip()]
rows=[e for e in events if e.get('action')=='test_status'];starts=[e for e in events if e.get('action')=='test_start'];ends=[e for e in events if e.get('action')=='test_end']
assert rows==run['rows'] and starts==run['starts'] and ends==run['ends']
assert len(rows)==101 and all(e['status']=='PASS' for e in rows)
assert len(starts)==len(ends)==12 and all(e['status']=='OK' for e in ends)
expected={(p,n) for p,names in config['expected_subtests'].items() for n in names}
assert len(expected)==101 and {(e['test'],e['subtest']) for e in rows}==expected
assert len({(e['test'],e['subtest']) for e in rows})==101
assert {e['test'] for e in starts}=={e['test'] for e in ends}==set(config['expected_subtests'])
assert sum(e.get('action')=='suite_start' for e in events)==sum(e.get('action')=='suite_end' for e in events)==1
assert not [e for e in events if e.get('action')=='crash' or e.get('level') in ['ERROR','CRITICAL'] or (e.get('action')=='process_exit' and e.get('exitcode',0)!=0)]
assert read('wpt-candidate/CLEANUP.json')=={'owned_group_absent':True,'errors':[]}
a=Path(config['acceptance']);a=a/'ACCEPTANCE.json' if a.is_dir() else a
assert sha(a)==state['acceptance_sha256']==inst['acceptance_sha256']==config['acceptance_sha256']
# The live six installed bodies and nine identities are cheap read-only joins.
for p,v in config['candidate_pins'].items():assert sha(Path(p))==v
for p,v in root['installed_tests'].items():
 f=Path(p);s=f.stat();assert sha(f)==v['sha256'] and [s.st_dev,s.st_ino]==v['identity']
check={'status':'PASS','runtime_manifest_sha256':sha(R/'FILES.json'),'authenticated_payloads':len(manifest),'raw_PASS':101,'harness_OK':12,'source_guards':56,'changed_source_paths':sorted(config['sources']),'native_inventory_before':30,'native_inventory_after':33,'final_pins':405,'staged_paths':925,'installed_test_identities':9,'six_installed_bodies_and_nine_live_inodes_checked':True,'binary_pins':inst['binary_pins'],'broad_live_index_binary_recheck':'Root authenticated receipt; no duplicate broad check','cleanup':read('wpt-candidate/CLEANUP.json')}
(O/'CHECK.json').write_text(json.dumps(check,indent=2)+'\n');print(json.dumps({k:v for k,v in check.items() if k not in ['binary_pins','changed_source_paths']},indent=2))
