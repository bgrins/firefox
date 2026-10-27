from pathlib import Path
import json,hashlib,subprocess,tempfile,re
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'artifacts/css-finite-mod-rem-comparison-data-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def auth(p,h):
 assert sha(p)==h
 for n,v in read(p).items():assert sha(p.parent/n)==v,n
 return read(p)
m=auth(P/'FILES.json','791f2c473e1c774b897852592142c34ae4419fa6857412367fe0c43e5d019bfd')
for n,h in read(P/'REFERENCES.json').items():assert sha(ROOT/n)==h,n
L=lambda n:read(P/n)
e=L('BASELINE-EPOCH.json');r=ROOT/e['runtime'];auth(r/'FILES.json',e['manifest_sha256']);final=read(r/'FINAL.json')
assert sha(r/'FINAL.json')==e['final_sha256'] and sha(r/'FINAL-PINS.json')==e['final_pins_sha256']
assert final['snapshot']==e['snapshot'] and final['installed_tests']==e['installed_tests']
pins=L('RESOURCES.json');assert len(pins)==628 and len(final['pins'])==620
assert all(k in pins and pins[k]==v for k,v in final['pins'].items())
assert {k:v for k,v in pins.items() if k not in final['pins']}==L('ADDITIONAL-ROLES.json')
ro=L('ROSTER.json');assert ro['expected_total']==sum(map(len,ro['expected_subtests'].values()))==700 and len(ro['tests'])==10 and not ro['reftests']
assert ro['tests']==['testing/web-platform/tests'+t for t in ro['expected_subtests']]
assert all(len(ns)==len(set(ns)) for ns in ro['expected_subtests'].values())
old=read(ROOT/'artifacts/css-name-repeat-context-comparison-runtime-v1/CONFIG.json')
new=['round-mod-rem-invalid.html','round-mod-rem-serialize.html','mod-rem-infinite-divisor.html']
for test,names in ro['expected_subtests'].items():
 if test.split('/')[-1] not in new+['mod-rem-exact-finite-remainder.html']:assert names==old['expected_subtests'][test]
with tempfile.TemporaryDirectory(prefix='modrem-review-') as tmp:
 for name in new:
  path='testing/web-platform/tests/css/css-values/'+name;body=(P/'source'/path).read_text();assert sha(P/'source'/path)==pins[path]
  scripts=re.findall(r'<script>([\s\S]*?)</script>',body);assert len(scripts)==1
  helper='parsing' if name.endswith('invalid.html') else 'serialize' if name.endswith('serialize.html') else None
  code=(P/'source/testing/web-platform/tests/css/support'/f'{helper}-testcommon.js').read_text() if helper else ''
  js=Path(tmp)/'names.js';js.write_text('const names=[];global.test=(fn,name)=>names.push(name);global.document={querySelector:()=>({})};\n'+code+'\n'+scripts[0]+'\nconsole.log(JSON.stringify(names));')
  result=subprocess.run(['node',str(js)],capture_output=True,text=True,check=True)
  assert json.loads(result.stdout)==ro['expected_subtests']['/css/css-values/'+name]
observed=L('OBSERVED-LANDING-BASELINE.json');raw=read(r/'wpt-diagnostic/RUN.json')['rows']
assert [dict(x,test=observed['comparison_test']) for x in raw]==observed['rows']
assert [x['subtest'] for x in raw]==ro['expected_subtests'][observed['comparison_test']]
c=L('CANDIDATE.json');assert len(c['native_paths'])==1 and len(c['fixture'])==1
maps=L('SOURCE-MAPS.json');assert maps['baseline']==maps['restored']==final['snapshot']['sources'] and len(maps['baseline'])==72
for n,v in c['native_paths'].items():
 assert sha(ROOT/v['original'])==v['original_sha256']==maps['baseline'][n]
 assert sha(ROOT/v['candidate'])==v['candidate_sha256']==maps['candidate'][n]
 assert {k for k in maps['candidate'] if maps['candidate'][k]!=maps['baseline'][k]}=={n}
for n,v in c['fixture'].items():assert pins[n] is None and sha(ROOT/v['source'])==v['sha256']==observed['body_sha256']==sha(r/'fixture.html')
assert sha(ROOT/c['patch'])==c['patch_sha256']
o=L('OWNERSHIP.json');assert set(o['readonly_tests'])==set(ro['tests'])-{o['owned_fixture']}
assert len(o['tracked_readonly'])==6 and len(o['installed_readonly'])==3
assert set(o['tracked_readonly'])|set(o['installed_readonly'])==set(o['readonly_tests']) and not set(o['tracked_readonly'])&set(o['installed_readonly'])
assert o['full_installed_identities']==final['installed_tests'] and len(o['full_installed_identities'])==24
assert all(pins[n]==v for n,v in o['readonly_pins'].items())
for n,v in o['installed_readonly'].items():assert final['installed_tests'][n]==v
policy=L('POLICY.json');assert policy['full_baseline_outcomes'] is None and not policy['ready_for_execution'] and not policy['normalization_to_head90']
assert policy['observed_repair_identities']==[{'test':observed['comparison_test'],'subtest':x['subtest']} for x in raw if x['status']=='FAIL'] and policy['expected_repair_count']==16
assert not L('HISTORICAL-CONTROL-OUTCOMES.json')['authoritative_for_next_run']
print(json.dumps({'status':'MOD_REM_COMPARISON_DATA_REVIEW_GO','payloads':len(m),'subtests':700,'files':10,'roles':628,'inherited_roles':620,'source_guards':72,'installed_identities':24,'candidate_native_paths':1,'owned_fixture':1,'fresh_baseline_required':True,'exact_allowed_repairs':16,'live_actions':False},indent=2))
