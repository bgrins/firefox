from pathlib import Path
import json,hashlib,subprocess,tempfile
root=Path('/Users/bgrins/code/firefox');p=root/'artifacts/css-round-runtime-finite-comparison-data-v1';b=root/'artifacts/css-round-numerical-baseline-runtime-v1';sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest();read=lambda q:json.loads(q.read_text());refs=read(p/'REFERENCES.json');pins=read(b/'FINAL-PINS.json');final=read(b/'FINAL.json')
assert len(pins)==605 and len(final['pins'])==599 and all(pins[n]==h for n,h in final['pins'].items())
assert len(set(pins)-set(final['pins']))==6 and all(pins[n] is None for n in set(pins)-set(final['pins']))
(p/'RESTORATION-PINS.json').write_text(json.dumps(pins,indent=2,sort_keys=True)+'\n')
roster=read(p/'ROSTER.json');fixtures=read(p/'FIXTURES.json');owned={}
for test,item in fixtures.items():
 name='testing/web-platform/tests'+test;assert pins[name] is None;owned[name]={'source':str((p/item['local']).relative_to(root)),'sha256':item['sha256'],'baseline':None,'final':None,'kind':'temporary numerical diagnostic'}
temps=read(root/'artifacts/css-counter-additive-install-plan-v1/EXPECTED-MAP.json')['temporary_controls']
for name,item in temps.items():
 assert pins[name] is None;assert sha(root/item['archive_path'])==item['sha256'];refs[item['archive_path']]=item['sha256'];owned[name]={'source':item['archive_path'],'sha256':item['sha256'],'baseline':None,'final':None,'kind':'temporary installed-suite preservation control'}
assert len(owned)==6
selected=['testing/web-platform/tests'+t for t in roster['tests']];assert all(n in pins for n in selected);assert {n for n in selected if pins[n] is None}==set(owned)
identity=final['installed_tests'];assert len(identity)==21
(p/'OWNERSHIP.json').write_text(json.dumps({'temporary_fixtures':owned,'installed_identities':identity,'strict_baseline_absences':[n for n,h in pins.items() if h is None],'phase_permanent_absences':[n for n,h in pins.items() if h is None and n not in owned],'temporary_phase_overlay':{n:v['sha256'] for n,v in owned.items()},'all_original_roles':605,'no_owned_path_in_phase_permanent_absences':True},indent=2)+'\n')
(p/'EPOCH.json').write_text(json.dumps({'authority':'actual installed123124 source stack preserved by baseline61360','installed_runtime':'artifacts/css-counter-additive-install-runtime-v1','numerical_runtime':'artifacts/css-round-numerical-baseline-runtime-v1','baseline_manifest':sha(b/'FILES.json'),'baseline_root_receipt':sha(b/'ROOT-FINAL-CHECK.json'),'baseline_terminal_review':None,'source_snapshot':final['snapshot'],'binary_pins':{n:h for n,h in pins.items() if n.endswith('/MacOS/firefox') or n.endswith('/MacOS/XUL')},'prior_role_count':605,'inherited_FINAL_native_verifier_roles':599,'additional_explicit_absence_roles':sorted(set(pins)-set(final['pins'])),'installed_identity_count':21,'native_modified_count':42,'staged_count':925,'ready_for_execution':False,'future_runtime':None,'future_session':None,'fresh_live_preflight_required':True},indent=2)+'\n')
source='servo/components/style/values/generics/calc.rs';records=[]
with tempfile.TemporaryDirectory(prefix='round-landing-transport-') as tmp:
 q=Path(tmp);subprocess.run(['git','init','-q'],cwd=q,capture_output=True,check=True);f=q/source;f.parent.mkdir(parents=True);original=(p/'original'/source).read_bytes();f.write_bytes(original)
 patchnames=['runtime_nan_only-gecko-wpt.patch','finite_zero_only-gecko-wpt.patch']
 def apply(n,reverse=False):
  args=['git','apply']+(['--reverse'] if reverse else [])
  for check in [True,False]:
   run=subprocess.run(args+(['--check'] if check else [])+[str(p/n)],cwd=q,capture_output=True,text=True);assert run.returncode==0 and run.stdout==run.stderr=='',run.stderr
 for name in patchnames:
  apply(name);variant=name.removesuffix('-gecko-wpt.patch');assert sha(f)==sha(p/'candidate'/variant/source)
  apply(name,True);assert f.read_bytes()==original;records.append({'patch':name,'apply_reverse':True})
 for order in [patchnames,list(reversed(patchnames))]:
  for name in order:apply(name)
  assert sha(f)==sha(p/'candidate/combined'/source)
  for name in reversed(order):apply(name,True)
  assert f.read_bytes()==original;assert not list(q.glob('testing/**/*.html'));records.append({'landing_order':order,'combined_exact_reverse':True})
check=read(p/'CHECK.json');check['full_restoration_roles']=605;check['temporary_owned_fixtures']=6;check['installed_identities']=21;check['landing_patch_transport']=records;check['final_pin_join']='FINAL native verifier retains599; FINAL-PINS adds six explicit None roles, all preserved in605 restoration map';(p/'CHECK.json').write_text(json.dumps(check,indent=2)+'\n');(p/'REFERENCES.json').write_text(json.dumps(refs,indent=2,sort_keys=True)+'\n')
