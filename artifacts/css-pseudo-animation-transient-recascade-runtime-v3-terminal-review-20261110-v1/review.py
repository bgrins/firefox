import hashlib,importlib.util,json,subprocess,sys,os
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];LAB=ROOT/'artifacts/css-pseudo-animation-transient-recascade-runtime-20261110-v3'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git','-c','core.fsmonitor=false',*args],cwd=ROOT,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
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
 assert begun and ended and starts==ends and len(starts)==12 and len(rows)==130
 saved=load(directory/'TEST-RESULTS.json');assert rows==flatten(saved)
 return rows
def flatten(result):
 rows={}
 for kind,field in [('assertion','subtests'),('harness','harness')]:
  for row in result[field]:
   key=(kind,row['test'],row.get('subtest'));assert key not in rows;rows[key]=row
 return rows
def main():
 digest=sha(LAB/'RUN-INPUTS.json');assert digest=='b81b1a21cb270cf75a25f6a440402120c0272b30888de9d6c12e4ceca2bd03d7'
 assert all(sha(LAB/n)==h for n,h in load(LAB/'RUN-INPUTS.json').items())
 plan=load(LAB/'RUN-PLAN.json');roles=load(LAB/'SOURCE-ROLES.json');retained=load(LAB/'runtime-inputs/retained-build.json');befores=[];groups=[]
 for name in ['baseline1','candidate1']:
  d=LAB/name;b=load(d/'BEFORE.json');r=load(d/'RESULT.json');befores.append(b)
  assert r['head']==plan['head']==b['head'] and r['runner_inputs_sha256']==digest
  assert r['restoration_verified'] and r['restoration_errors']==[]
  if name=='baseline1':
   assert r['error'] is None and r['commands']['lint']['exit_code']==0 and r['commands']['wpt']['exit_code']==1 and r['commands']['build']['skipped']
   assert raw(d)==flatten(load(LAB/'EXPECTED-BASELINE.json')) and r['sampled_binaries']==retained['binaries']
   assert load(d/'DRIVER-NOT-RUN.json')['executed'] is False
  else:
   assert r['error'] and 'driver command failed; setup classification retained' in r['error']
   assert set(r['commands'])=={'lint','driver_lint','recascade_lint','manifest_lint','build','wpt','driver'}
   assert all(r['commands'][n]['exit_code']==0 for n in ['lint','driver_lint','recascade_lint','manifest_lint','build'])
   assert r['commands']['wpt']['exit_code']==1 and r['commands']['driver']['exit_code']==1
   assert raw(d)==raw(LAB/'baseline1')
   assert r['comparison']['accepted_changes_only'] and not r['comparison']['changes'] and not r['comparison']['unexpected_detail_changes']
   build=load(d/'BUILD.json');assert build['source_sha256']=={n:role['candidate'] for n,role in roles.items()}
   assert build['head']==plan['head'] and build['mozconfig_sha256']==plan['mozconfig_sha256'] and build['command_result']==r['commands']['build']
   assert build['binaries']==r['sampled_binaries']==load(d/'SAMPLED-BINARIES.json')
   for missing in ['recascade-raw.jsonl','RECASCADE-RESULTS.json','recascade.log']:
    assert not(d/missing).exists(), missing
  assert not(d/'backups').exists();restored=load(d/'RESTORED.json')
  assert all(restored[k] for k in ['source_and_application_restored','index_preserved','temporary_fixtures_removed','mochitest_install_tree_restored','test_metadata_restored','backup_removed'])
  procs=[load(f) for f in d.glob('*.process.json')];assert len(procs)==(2 if name=='baseline1' else 7)
  assert all(x['state']=='terminal' and x['group_absent'] for x in procs);groups += [x['pgid'] for x in procs]
 spec=importlib.util.spec_from_file_location('review_bundle',LAB/'bundle.py');bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle);before=befores[0]
 for b in befores:
  assert b['index']==before['index'] and b['extra_absent']==before['extra_absent']
  for k in ['app','extras','mochitest_tree']:assert bundle.semantic(b[k])==bundle.semantic(before[k])
 assert bundle.semantic(bundle.scan(ROOT/'objdir-full.noindex/dist/Nightly.app'))==bundle.semantic(before['app'])
 assert bundle.semantic(bundle.scan(ROOT/'objdir-full.noindex/_tests/testing/mochitest'))==bundle.semantic(before['mochitest_tree'])
 assert bundle.semantic({p:bundle.entry(ROOT/p) for p in before['extras']})==bundle.semantic(before['extras'])
 assert all(not((ROOT/p).exists() or (ROOT/p).is_symlink()) for p in before['extra_absent'])
 assert all(sha(ROOT/n)==role['base'] for n,role in roles.items())
 assert all(sha(ROOT/n)==h for n,h in retained['sources'].items()) and all(sha(ROOT/n)==h for n,h in retained['binaries'].items())
 for n,h in load(LAB/'runtime-inputs/test-source-pins.json').items():assert not((ROOT/n).exists() or (ROOT/n).is_symlink()) if h is None else sha(ROOT/n)==h
 assert sha(ROOT/'mozconfig')==plan['mozconfig_sha256'] and git('rev-parse','HEAD').decode().strip()==plan['head']
 assert hashlib.sha256(git('ls-files','--stage','-z')).hexdigest()==before['index'] and not git('diff','--name-only').strip() and not git('diff','--cached','--name-only').strip()
 untracked=sorted(x.decode() for x in git('ls-files','--others','--exclude-standard','-z').split(b'\0') if x)
 assert untracked==sorted(load(ROOT/'artifacts/css-keyframe-order-combined-current-build-20261110-v1/BEFORE.json')['untracked'])
 alive={int(x[1]) for line in (HERE/'process-snapshot.txt').read_text().splitlines() if len(x:=line.split())==3 and not x[2].startswith('Z')};assert not(set(groups)&alive)
 assert not(LAB/'runtime.lock').exists()
 print(json.dumps({'status':'PASS','baseline_records':130,'baseline_statuses':dict(Counter(row['status'] for row in raw(LAB/'baseline1').values())), 'candidate_build_exit':0,'candidate_wpt_records':130,'candidate_wpt_exactly_unchanged':True,'query_driver_executed':True,'recascade_driver_executed':False,'native_acceptance':False,'app_entries_restored':len(before['app']),'mochitest_entries_restored':len(before['mochitest_tree']),'extras_and_metadata_files_restored':len(before['extras']),'originally_absent_metadata':before['extra_absent'],'source_roles_restored':len(roles),'source_test_config_HEAD_index_restored':True,'untracked_paths_preserved':len(untracked),'owned_process_groups_absent':groups},indent=2))
if __name__=='__main__':main()
