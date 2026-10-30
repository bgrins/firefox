import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OLD=ROOT/'artifacts/css-prioritary-selection-candidate-v2'
ORIGINAL=ROOT/'artifacts/css-prioritary-selection-original77-bound-template-v1'
PROPOSAL=ROOT/'artifacts/css-prioritary-selected-declaration-proposal-v4'
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value): (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def binding(p):return {'directory':str(p.relative_to(ROOT)),'manifest_sha256':sha(p/'FILES.json')}
def authenticate(p):
 for name,record in read(p/'FILES.json').items():assert sha(p/name)==record['sha256']
for p in (OLD,ORIGINAL,PROPOSAL):authenticate(p)
assert sha(ORIGINAL/'FILES.json')=='3c10cba64b3cbaea836d37cbdcb6cd9cd7866e1202ac2a4da8b381d3d805e4ce'
for name in ['candidate.py','baseline.py','comparison.py','phases.py','wpt.py','assess.py','check_phases.py']:
 (HERE/name).write_bytes((OLD/name).read_bytes())
for name in ['inputs.py','intermediate.py','review_scope.py']:(HERE/name).write_bytes((ORIGINAL/name).read_bytes())
policy=read(ORIGINAL/'POLICY.json')
policy.update(owner_directory=str(HERE.relative_to(ROOT)),runtime_output='artifacts/css-prioritary-selection-candidate-runtime-2',predecessor=binding(ORIGINAL),candidate_lifecycle_predecessor=binding(OLD),proposal=binding(PROPOSAL),proposal_independent_review=None,provider_source_role='provider-cascade-value-candidate',restored_context_claims={},disabled_preimage=None,execution_enabled=False,candidate_execution_enabled=False,activation_pending=['Actual original77 terminal/capture/restoration and fresh current-state binding'])
pending=['head','controls','prepared_application_metadata','prepared_flag_hashes','prepared_flag_capture','execution_handoff','restoration_binding','baseline_binding','baseline_capsule','original_admission_policy_sha256']
for key in pending:policy[key]=None
proposed=read(PROPOSAL/'SOURCE-ROLES.json');prior=read(ORIGINAL/'SOURCE-ROLES.json');roles={}
for name,record in proposed.items():
 base={'path':prior[name]['base_capture'],'sha256':prior[name]['base_sha256']} if name in prior else record['base']
 roles[name]={'base_capture':base['path'],'base_sha256':base['sha256'],'candidate_capture':record['candidate']['path'],'candidate_sha256':record['candidate']['sha256']}
save('SOURCE-ROLES.json',roles)
policy['source_paths']=list(roles)
policy['semantic_original_sources']={name:record['base']['sha256'] for name,record in proposed.items()}
a=ROOT/'artifacts/css-registered-selected-color-original-runtime-2';b=ROOT/'artifacts/css-registered-selected-color-union-only-candidate-runtime-1'
for p in (a,b):authenticate(p)
original=read(a/'OUTCOMES.json');candidate=read(b/'OUTCOMES.json')
original_rows={(r['test'],r['subtest']):r for r in original['rows']}
assert len(original_rows)==45 and len(candidate['rows'])==45
improved=[]
for row in candidate['rows']:
 old,new=row['original'],row['candidate'];key=(old['test'],old['subtest'])
 assert old==original_rows[key] and key==(new['test'],new['subtest'])
 if old['status']!=new['status']:
  assert old['status']=='FAIL' and new['status']=='PASS';improved.append({'test':key[0],'subtest':key[1]})
assert len(improved)==8
targets=read(OLD/'TARGETS.json');prior_targets={(p,n) for p,ns in targets.items() for n in ns}
assert len(prior_targets)==15
forced='/forced-colors-mode/registered-prioritary-forced-color-selection.tentative.html'
targets[forced].append('Prioritary forced-color selection: auto')
for row in improved:
 assert (row['test'],row['subtest']) not in prior_targets
 targets.setdefault(row['test'],[]).append(row['subtest'])
assert sum(map(len,targets.values()))==24
save('TARGETS.json',targets)
policy['target_evidence']={'original45':binding(a),'union_only45':binding(b)}
save('TARGET-EVIDENCE.json',{'existing_targets':15,'matched_auto_targets':1,'color_only_improvements':improved,'total_disjoint_targets':24,'original45':binding(a),'union_only45':binding(b),'future_original77_counts':None,'candidate77_outcome':None})
for settings in [policy['wpt'],*policy['wpt_lanes'].values()]:
 settings['phase_revisions']={'original':None,'candidate':None};settings['harness_revision']=None
 selected={p:ns for p,ns in targets.items() if p in settings['expected_subtests']}
 assert all(set(ns)<=set(settings['expected_subtests'][p]) for p,ns in selected.items())
 count=sum(map(len,selected.values()));settings.update(target_subtests=selected,expected_target_count=count,expected_control_count=settings['expected_subtest_count']-count,expected_regression_signature_count=settings['expected_subtest_count']-count+settings['expected_page_count'])
for p in [OLD/'FILES.json',ORIGINAL/'FILES.json',PROPOSAL/'FILES.json',a/'FILES.json',b/'FILES.json',a/'OUTCOMES.json',b/'OUTCOMES.json']:
 policy['references'][str(p.relative_to(ROOT))]=sha(p)
text=(HERE/'candidate.py').read_text().replace("'prioritary-selection-candidate-v2'","'prioritary-selection-candidate77-v3'")
text=text.replace('    original_before = original_verify()\n','    original_before = original_verify()\n'+"    intermediate = load('owner_intermediate', str((HERE / 'intermediate.py').relative_to(ROOT)))\n    input_binding = load('owner_input_binding', str((HERE / 'inputs.py').relative_to(ROOT)))\n    closure = load('owner_consumed_closure', str((HERE / 'closure.py').relative_to(ROOT)))\n    closure.require_epoch_coverage(original, policy)\n    consumed_inputs = input_binding.bind_inputs(str(HERE.relative_to(ROOT)), (HERE / 'FILES.json').read_bytes(), sys.argv[2], policy['intermediate_consumed_inputs'])\n")
text=text.replace('        verified = state.a.verify_current(state.h, ROOT, env, local)\n','        verified = intermediate.verify_intermediate(state.h, ROOT, env, local, consumed_inputs)\n')
(HERE/'candidate.py').write_text(text)
text=(HERE/'phases.py').read_text().replace('== 74','== 77').replace('== 11','== 12').replace('== 85','== 89').replace('all85_signatures_equal','all89_signatures_equal').replace('clean-provider-cascade-candidate','provider-cascade-value-candidate')
(HERE/'phases.py').write_text(text)
text=(HERE/'comparison.py').read_text().replace('==74 and len(ends)==11','==77 and len(ends)==12')
text=text.replace("    return {'repair_observation_gate':not errors", "    result = {'repair_observation_gate':not errors")
text=text.replace("            'target_rows':target_rows,'native_acceptance':False}","            'target_rows':target_rows,'native_acceptance':False}\n    return json.loads(json.dumps(result))")
text=text.replace("    source=read(source_owner/'POLICY.json')\n", "    source=read(source_owner/'POLICY.json')\n    assert source['owner_directory']==capsule['directory']\n")
text=text.replace("    assert build['snapshot']['index']['working_diff']==hashlib.sha256(b'').hexdigest()", "    scope=load('original77_review_scope',root/policy['owner_directory']/'review_scope.py')\n    inputs=load('original77_input_binding',root/policy['owner_directory']/'inputs.py')\n    closure=load('original77_closure',source_owner/'closure.py')\n    expected_inputs=closure.external_inputs(root,source,read(source_owner/'SOURCE-ROLES.json'))\n    assert source['intermediate_consumed_inputs']==expected_inputs\n    effective=inputs.bind_inputs(capsule['directory'],(source_owner/'FILES.json').read_bytes(),capsule['sha256'],expected_inputs)\n    scope.require_intermediate(build['snapshot'],effective)\n    assert build['snapshot']['index']['working_diff']==hashlib.sha256(b'').hexdigest()")
(HERE/'comparison.py').write_text(text)
text=(ORIGINAL/'closure.py').read_text()
start=text.index('    bindings = ');end=text.index('    for binding in bindings:',start)
text=text[:start]+"    bindings = [policy[key] for key in ('predecessor', 'candidate_lifecycle_predecessor', 'proposal', 'suite_binding', 'capture_binding', 'intermediate_guard_binding')]\n    bindings.extend(policy['target_evidence'].values())\n    if policy['baseline_binding'] is not None:\n        bindings.append({'directory':policy['baseline_capsule']['directory'],'manifest_sha256':policy['baseline_capsule']['sha256']})\n        bindings.append(policy['baseline_binding'])\n    if policy['restoration_binding'] is not None:\n        bindings.append(policy['restoration_binding'])\n"+text[end:]
(HERE/'closure.py').write_text(text)
(HERE/'admission.py').write_text("PENDING = "+repr(tuple(pending))+"\n\n\ndef validate(root, policy):\n    assert not policy['execution_enabled'] and not policy['candidate_execution_enabled']\n    assert policy['activation_pending'] == ['Actual original77 terminal/capture/restoration and fresh current-state binding']\n    assert all(policy[name] is None for name in PENDING)\n")
spec=importlib.util.spec_from_file_location('closure',HERE/'closure.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
policy['intermediate_consumed_inputs']=m.external_inputs(ROOT,policy,roles)
save('POLICY.json',policy)
for name in ['candidate.py','baseline.py','comparison.py','phases.py']:
 (HERE/(name+'.diff')).write_text(''.join(difflib.unified_diff((OLD/name).read_text().splitlines(True),(HERE/name).read_text().splitlines(True),fromfile=str((OLD/name).relative_to(ROOT)),tofile=str((HERE/name).relative_to(ROOT)))))
print(json.dumps({'targets':targets,'consumed_pins':len(policy['intermediate_consumed_inputs']),'references':len(policy['references'])}))
