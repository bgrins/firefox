import hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];LAB=ROOT/'artifacts/css-keyframe-getter-branch-comparison-20261110-v1'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=ROOT)
def unique(pairs):
 d={}
 for k,v in pairs:
  assert k not in d;d[k]=v
 return d
def raw(directory):
 active=None;begun=ended=False;starts=set();ends=set();rows={}
 for line in (directory/'wpt-raw.jsonl').read_text().splitlines():
  row=json.loads(line,object_pairs_hook=unique);action=row['action']
  assert action!='crash' and not(action=='log' and row.get('level') in ['ERROR','CRITICAL'])
  if action=='suite_start':assert not begun and not ended;begun=True
  elif action=='test_start':
   assert begun and not ended and active is None and row['test'] not in starts;active=row['test'];starts.add(active)
  elif action in ['test_status','test_end']:
   assert begun and not ended and active==row['test']
   key=('assertion' if action=='test_status' else 'harness',row['test'],row.get('subtest'));assert key not in rows
   rows[key]={k:row[k] for k in ['test','subtest','status','message','expected','known_intermittent'] if k in row}
   if action=='test_end':assert row['status']=='OK';ends.add(active);active=None
   else:assert row['status'] in ['PASS','FAIL']
  elif action=='suite_end':assert begun and not ended and active is None;ended=True
  elif action=='assertion_count':assert row['min_expected']<=row['count']<=row['max_expected']
 assert begun and ended and starts==ends and len(starts)==13 and len(rows)==135
 saved=load(directory/'TEST-RESULTS.json');assert rows==flatten(saved)
 return rows
def flatten(result):
 rows={}
 for kind,field in [('assertion','subtests'),('harness','harness')]:
  for row in result[field]:
   key=(kind,row['test'],row.get('subtest'));assert key not in rows;rows[key]=row
 return rows
def main():
 manifest=load(LAB/'RUN-INPUTS.json');digest=sha(LAB/'RUN-INPUTS.json');assert digest=='85f4a69529b4ec46a8a370e99a227a6c81700e089c46af4d794eae49c6d50e6f';assert all(sha(LAB/n)==d for n,d in manifest.items())
 plan=load(LAB/'RUN-PLAN.json');roles=load(LAB/'SOURCE-ROLES.json');retained=load(LAB/'runtime-inputs/retained-build.json')
 rows=[];befores=[];groups=[]
 for name,mode in [('baseline2','baseline'),('candidate1','candidate')]:
  d=LAB/name;b=load(d/'BEFORE.json');r=load(d/'RESULT.json');befores.append(b)
  assert r['mode']==mode and r['head']==plan['head']==b['head'] and r['runner_inputs_sha256']==digest
  assert r['error'] is None and r['restoration_verified'] and r['restoration_errors']==[]
  assert r['commands']['lint']['exit_code']==0 and r['commands']['wpt']['exit_code']==1
  assert set(r['commands'])=={'lint','build','wpt'}
  if mode=='baseline':assert r['commands']['build']['skipped'] and r['sampled_binaries']==retained['binaries']
  else:
   build=load(d/'BUILD.json');assert r['commands']['build']['exit_code']==0 and build['command_result']==r['commands']['build']
   assert build['head']==plan['head'] and build['mozconfig_sha256']==plan['mozconfig_sha256']
   assert build['source_sha256']=={n:role['candidate'] for n,role in roles.items()}
   assert build['binaries']==r['sampled_binaries']==load(d/'SAMPLED-BINARIES.json')
   assert r['sampled_binaries']!=retained['binaries']
  rows.append(raw(d));assert not(d/'backups').exists() and load(d/'RESTORED.json')['backup_removed']
  processes=[load(f) for f in d.glob('*.process.json')];assert len(processes)==(2 if mode=='baseline' else 3)
  assert all(x['state']=='terminal' and x['group_absent'] for x in processes);groups += [x['pgid'] for x in processes]
 assert rows[0]==flatten(load(LAB/'EXPECTED-BASELINE.json')) and rows[1]==flatten(load(LAB/'EXPECTED-CANDIDATE.json'))
 changed=[k for k in rows[0] if rows[0][k]!=rows[1][k]];assert len(changed)==3
 for key in changed:assert key[0]=='assertion' and key[1]=='/css/css-animations/getkeyframes-specified-branch.html' and rows[0][key]['status']=='FAIL' and rows[1][key]['status']=='PASS'
 assert all(r['status']=='PASS' for k,r in rows[1].items() if k[0]=='assertion' and k[1]=='/css/css-animations/getkeyframes-specified-branch.html')
 spec=importlib.util.spec_from_file_location('review_bundle',LAB/'bundle.py');bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)
 old=load(LAB/'baseline1/BEFORE.json');befores.append(old);before=befores[0]
 assert all(b['index']==before['index'] and bundle.semantic(b['app'])==bundle.semantic(before['app']) and bundle.semantic(b['extras'])==bundle.semantic(before['extras']) for b in befores)
 assert bundle.semantic(bundle.scan(ROOT/'objdir-full.noindex/dist/Nightly.app'))==bundle.semantic(before['app'])
 assert bundle.semantic({p:bundle.entry(ROOT/p) for p in before['extras']})==bundle.semantic(before['extras'])
 assert all(sha(ROOT/n)==d for n,d in retained['sources'].items()) and all(sha(ROOT/n)==d for n,d in retained['binaries'].items())
 assert all(sha(ROOT/n)==role['base'] for n,role in roles.items()) and sha(ROOT/'mozconfig')==plan['mozconfig_sha256']
 for n,d in load(LAB/'runtime-inputs/test-source-pins.json').items():assert not((ROOT/n).exists() or (ROOT/n).is_symlink()) if d is None else sha(ROOT/n)==d
 assert git('rev-parse','HEAD').decode().strip()==plan['head'] and hashlib.sha256(git('ls-files','--stage','-z')).hexdigest()==before['index']
 assert not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
 untracked=sorted(x.decode() for x in git('ls-files','--others','--exclude-standard','-z').split(b'\0') if x)
 reference=load(ROOT/'artifacts/css-keyframe-order-combined-current-build-20261110-v1/BEFORE.json')['untracked'];assert untracked==sorted(reference)
 (HERE/'UNTRACKED-PATHS.json').write_text(json.dumps(untracked,indent=2)+'\n')
 assert not(LAB/'runtime.lock').exists() and not(LAB/'baseline1/backups').exists()
 recovery=load(LAB/'baseline1/RECOVERY.json');assert recovery['status']=='PASS' and recovery['group_absent'] and recovery['backups_removed']
 failed=load(LAB/'baseline1/RESULT.json');assert failed['error'] and failed['commands']=={} and failed['sampled_binaries'] is None
 assert not(LAB/'baseline1/wpt-raw.jsonl').exists() and not(LAB/'baseline1/BUILD.json').exists()
 processes=[line.split() for line in (HERE/'process-snapshot.txt').read_text().splitlines()];alivegroups={int(x[1]) for x in processes if len(x)==3 and not x[2].startswith('Z')};alivepids={int(x[0]) for x in processes if len(x)==3 and not x[2].startswith('Z')}
 assert not set(groups+[20934])&alivegroups and 20788 not in alivepids
 print(json.dumps({'status':'PASS','baseline_records':135,'candidate_records':135,'baseline_callbacks':dict(Counter(r['status'] for k,r in rows[0].items() if k[0]=='assertion')),'candidate_callbacks':dict(Counter(r['status'] for k,r in rows[1].items() if k[0]=='assertion')),'harness_OK_each':13,'changes':changed,'all_other_complete_rows_identical':True,'native_build_exit':0,'candidate_native_and_binary_pins':True,'full_app_entries_restored':len(before['app']),'extras_restored':len(before['extras']),'untracked_paths_preserved_against_retained_receipt':len(untracked),'source_test_config_HEAD_index_restored':True,'owned_process_groups_absent':groups+[20934],'baseline1_recovery_separately_verified':True},indent=2))
if __name__=='__main__':main()
