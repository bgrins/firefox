from pathlib import Path
import json,hashlib,difflib,shutil,subprocess,tempfile,collections
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());refs={};auth={}
def put(n,v): (OUT/n).write_text(json.dumps(v,indent=2)+'\n')
def capsule(name,want=None):
 p=ROOT/'artifacts'/name;m=p/'FILES.json';h=sha(m)
 if want:assert h==want
 for n,d in read(m).items():assert sha(p/n)==d,(name,n)
 refs[str(m.relative_to(ROOT))]=h;auth[name]=len(read(m));return p
baseline=capsule('css-round-numerical-baseline-runtime-v1','6488e9596b36cae63c72478be7d533b57812bdd2d680507807160b1d168cbd53')
installed=capsule('css-counter-additive-install-runtime-v1','dfe49f900d2ba34410520beabc165b0cb40639ca06fcc19ebe8dab1316b51bb5')
plan=capsule('css-counter-additive-install-plan-v1','93dba57650187be68db6f0a6fb4ae691e371351e54b97f42a98a6451b897aff8')
fixtures=capsule('css-round-numerical-baseline-plan-v2','11a466f65680865176806642ef363bc211e451ee6c52b6256c2c170534f6de9a')
runtime=capsule('css-round-special-knowledge-repair-v2','a3749a341a430bd388fe4ff83fbd3aac128ee8ef7e5dc122a337f2d1775186f3')
finite=capsule('css-round-parse-negative-zero-repair-v2','89466aa12536371fe6b553803c23130b0c730bb433ff72c07b330025724d64ac')
for name in ['css-round-special-knowledge-repair-source-review-v1','css-round-parse-negative-zero-observer-review-v1','css-round-numerical-baseline-plan-review-v2','css-counter-additive-install-results-review-v1']:capsule(name)
path='servo/components/style/values/generics/calc.rs';original=finite/'original'/path;preimage=sha(original);assert preimage=='63a9b384909ddd08ef254dce9ca438ce8357346171caa759064e814447653637'
final=read(baseline/'FINAL.json');assert final['snapshot']['sources'][path]==preimage
assert final['snapshot']==read(installed/'FINAL.json')
for name,d in read(installed/'FINAL-PINS.json').items():assert final['pins'][name]==d
q=OUT/'original'/path;q.parent.mkdir(parents=True);shutil.copyfile(original,q)
sources={'runtime_nan_only':runtime/'runtime-nan'/path,'finite_zero_only':finite/'candidate'/path};patches={}
for name,source in sources.items():
 q=OUT/'candidate'/name/path;q.parent.mkdir(parents=True);shutil.copyfile(source,q)
 patch=''.join(difflib.unified_diff(original.read_text().splitlines(keepends=True),source.read_text().splitlines(keepends=True),fromfile='a/'+path,tofile='b/'+path));p=OUT/(name+'.patch');p.write_text(patch);patches[name]=p
records=[];combined=None
with tempfile.TemporaryDirectory(prefix='round-data-transport-') as tmp:
 scratch=Path(tmp);subprocess.run(['git','init','-q'],cwd=scratch,check=True,capture_output=True)
 q=scratch/path;q.parent.mkdir(parents=True);q.write_bytes(original.read_bytes())
 def apply(p,reverse=False):
  args=['git','apply']+(['--reverse'] if reverse else [])
  for check in [True,False]:
   r=subprocess.run(args+(['--check'] if check else [])+[str(p)],cwd=scratch,text=True,capture_output=True);assert r.returncode==0 and not r.stdout and not r.stderr,(r.returncode,r.stdout,r.stderr)
 for name,p in patches.items():
  apply(p);assert sha(q)==sha(sources[name]);apply(p,True);assert q.read_bytes()==original.read_bytes();records.append({'variant':name,'apply_reverse':True})
 for order in [list(patches),list(reversed(patches))]:
  for name in order:apply(patches[name])
  if combined is None:combined=q.read_bytes()
  else:assert combined==q.read_bytes()
  for name in reversed(order):apply(patches[name],True)
  assert q.read_bytes()==original.read_bytes();records.append({'order':order,'identical_combined_reverse':True})
q=OUT/'candidate/combined'/path;q.parent.mkdir(parents=True);q.write_bytes(combined)
(OUT/'combined.patch').write_text(''.join(difflib.unified_diff(original.read_text().splitlines(keepends=True),combined.decode().splitlines(keepends=True),fromfile='a/'+path,tofile='b/'+path)))
fixturemap={}
for c in read(fixtures/'FIXTURES.json'):
 q=OUT/c['local'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(fixtures/c['local'],q);assert sha(q)==c['sha256'];fixturemap['/'+c['wpt_relative']]={'local':c['local'],'sha256':sha(q),'family':c['family'],'names':c['names']}
for variant,family in [('runtime_nan_only','runtime_nan'),('finite_zero_only','finite_pow')]:
 test,item=next((t,v) for t,v in fixturemap.items() if v['family']==family)
 addition=''.join(difflib.unified_diff([], (OUT/item['local']).read_text().splitlines(keepends=True),fromfile='/dev/null',tofile='b/testing/web-platform/tests'+test))
 (OUT/(variant+'-gecko-wpt.patch')).write_text(patches[variant].read_text()+addition)
roster=read(plan/'WPT-ROSTER.json');newroster=read(fixtures/'ROSTER.json');assert not set(roster['expected_subtests'])&set(newroster)
union={**roster['expected_subtests'],**newroster};reftests=roster['reftests'];assert sum(map(len,roster['expected_subtests'].values()))==1442 and sum(map(len,newroster.values()))==42
assert len(union)==35 and len(reftests)==8 and not set(union)&set(reftests)
put('ROSTER.json',{'expected_subtests':union,'reftests':reftests,'tests':list(union)+reftests,'subtests':1484,'harnesses':35,'references':8,'files':43})
def outcomes(p,expected,refs):
 events=[json.loads(s) for s in p.read_text().splitlines() if s.strip()];rows=[];seen=set();ends={}
 for e in events:
  if e['action']=='test_status':
   key=(e['test'],e['subtest']);assert key not in seen;seen.add(key)
   rows.append({'test':e['test'],'subtest':e['subtest'],'status':e['status'],'message':e.get('message'),'expected':e.get('expected'),'effective_expected':e.get('expected',e['status']),'known_intermittent':e.get('known_intermittent',[])})
  if e['action']=='test_end':
   assert e['test'] not in ends;ends[e['test']]=e
 assert seen=={(t,n) for t,names in expected.items() for n in names}
 assert set(ends)==set(expected)|set(refs)
 assert all(ends[t]['status']=='OK' for t in expected)
 for t in refs:
  e=ends[t];assert e['status']=='PASS';rows.append({'test':t,'subtest':None,'status':e['status'],'message':e.get('message'),'expected':e.get('expected'),'effective_expected':e.get('expected',e['status']),'known_intermittent':e.get('known_intermittent',[])})
 return rows
oldrows=outcomes(installed/'wpt-installed/raw.json',roster['expected_subtests'],reftests);newrows=outcomes(baseline/'wpt-diagnostic/raw.json',newroster,[]);rows=oldrows+newrows
assert len(rows)==1492;assert collections.Counter(x['status'] for x in oldrows if x['subtest'] is not None)=={'PASS':1397,'FAIL':45};assert collections.Counter(x['status'] for x in newrows)=={'PASS':11,'FAIL':31}
put('ARCHIVED-OUTCOMES.json',rows)
classes=read(fixtures/'CLASSIFICATION.json')['families'];mandatory={}
for name,family in [('runtime_nan_only','runtime_nan'),('finite_zero_only','finite_pow')]:
 test=next(t for t,v in fixturemap.items() if v['family']==family);targets=[{'test':test,'subtest':n} for n in classes[family]['target_names']]
 mandatory[name]={'required_pass':{test:union[test]},'required_repairs':targets,'non_target_policy':'exact status/message/expected/known_intermittent preserved; baseline PASS stays PASS; all calibrations remain strict'}
mandatory['combined_optional']={'required_pass':{t:union[t] for t,v in fixturemap.items() if v['family'] in ['runtime_nan','finite_pow']},'required_repairs':mandatory['runtime_nan_only']['required_repairs']+mandatory['finite_zero_only']['required_repairs'],'preservation_bases':['baseline','runtime_nan_only','finite_zero_only'],'non_target_policy':mandatory['runtime_nan_only']['non_target_policy']}
keys={(r['test'],r['subtest']):r for r in rows}
for item in mandatory.values():
 for target in item['required_repairs']:assert keys[target['test'],target['subtest']]['status']=='FAIL'
put('MANDATORY.json',{'candidate_families':mandatory,'installed_mandatory':read(plan/'MANDATORY-ROSTER.json'),'no_executable_waivers':True,'parse_guard_included':False})
fullmaps={'baseline':final['snapshot']['sources']}
for name in ['runtime_nan_only','finite_zero_only','combined']:fullmaps[name]={**fullmaps['baseline'],path:sha(OUT/'candidate'/name/path)}
assert all({n for n,h in m.items() if h!=fullmaps['baseline'][n]}=={path} for name,m in fullmaps.items() if name!='baseline')
put('SOURCE-MAPS.json',{'role':'installed123124 baseline, not HEAD90 whole-tree normalization','path':path,'preimage_sha256':preimage,'source_maps':fullmaps,'source_count':72,'changes_per_candidate':1,'native_inventory_before':42,'restoration_required':'exact installed baseline map plus rebuilt binary/preservation verification'})
put('FIXTURES.json',fixturemap)
for d,files in [(baseline,['ROOT-EXECUTION.json','ROOT-FINAL-CHECK.json','FINAL.json','FINAL-PINS.json','CLASSIFICATION.json','wpt-diagnostic/raw.json','wpt-diagnostic/RUN.json']),(installed,['ROOT-FINAL-CHECK.json','FINAL.json','wpt-installed/raw.json','wpt-installed/RUN.json'])]:
 for f in files:refs[str((d/f).relative_to(ROOT))]=sha(d/f)
put('REFERENCES.json',refs)
put('CHECK.json',{'status':'DATA_CAPSULE_PASS_UNEXECUTED','authenticated_capsules':auth,'subtests':1484,'references':8,'harnesses':35,'files':43,'historical_union_subtests':{'PASS':1408,'FAIL':76},'historical_reference_PASS':8,'union_is_not_one_actual_capture':True,'scratch_transport':records,'owned_scratch_removed':True,'required_repairs':{'runtime_nan_only':8,'finite_zero_only':4},'native_candidate_applied_live':False,'new_compiler_browser_execution':False,'baseline_terminal_review':None,'ready_for_execution':False,'preparation_note':'Initial archive join expected a nested snapshot in installation FINAL; it is the flat snapshot. Corrected before any payload output/source mutation.'})
