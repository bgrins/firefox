from pathlib import Path
import ast,hashlib,json,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
refs={}
def authenticate(name,want):
    p=ROOT/'artifacts'/name;m=p/'FILES.json';assert sha(m)==want
    entries=read(m)
    for n,h in entries.items():assert sha(p/n)==h,n
    refs[str(m.relative_to(ROOT))]=want
    return p,len(entries)
r,total=authenticate('css-round-knowledge-library-integration-v1','5a8dcf13388122dedefd23de6da3cae3ef514f587d3685c7fd16d962c56c7855')
p,_=authenticate('css-round-knowledge-library-integration-proposal-v1','579d92a472953f79885252d53cf126323452a1df70b803ff9d375c4145ee9a1c')
peer,_=authenticate('css-round-knowledge-library-integration-review-v1','88dc704e189c3f8bcdcc36b889b1e1640b0279aea01b284c4e6082f54978820c')
native,_=authenticate('css-counter-additive-install-runtime-v1','dfe49f900d2ba34410520beabc165b0cb40639ca06fcc19ebe8dab1316b51bb5')
checkpoint,_=authenticate('css-round-scalar-capacity-library-integration-v1','a4b7f3d72742e5adc9fb1ff0a76790e19b8ee06fe20ff4e708a06ac5677619e3')
e=read(p/'EXPECTED.json');before=read(r/'BEFORE.json');old=read(r/'prior-verification/report.json');new=read(r/'verification/report.json')
assert sha(r/'prior-verification/report.json')==before['canonical_report_sha256']==sha(checkpoint/'verification/report.json')
assert read(r/'ROOT-EXECUTION.json')=={'session':77965,'exit':0,'command':'python3 -I -S artifacts/css-round-knowledge-library-integration-v1/apply.py','canonical_check_exit':0}
assert read(r/'EXECUTION.json')['exit']==0 and read(r/'CHECK.json')['status']=='PASS_APPLIED_CANONICAL'
assert json.loads((r/'driver.log').read_text())==read(r/'CHECK.json')
assert read(r/'APPLIED.json')['postimage_sha256']==e['postimage_sha256']
for n,h in e['preimage_sha256'].items():assert sha(r/'originals'/n)==h==before['working_sha256'][n]
post={**before['working_sha256'],**e['postimage_sha256']}
assert set(new['source_sha256'])==set(old['source_sha256'])|set(e['new_paths'])
for n,h in new['source_sha256'].items():assert post[n]==h,n
assert {n for n,h in old['source_sha256'].items() if new['source_sha256'][n]!=h}==set(e['modified_paths'])&set(old['source_sha256'])
assert len(new['declaration_axioms'])==11724 and len(new['source_sha256'])==2135
assert len(old['declaration_axioms'])==11720 and len(old['source_sha256'])==2133
assert all(new['declaration_axioms'][n]==v for n,v in old['declaration_axioms'].items())
assert set(new['declaration_axioms'])-set(old['declaration_axioms'])==set(e['audit_names'])
assert new['executable_cases']==old['executable_cases']+[{'name':n,'result':v} for n,v in e['new_cases']]
assert len(new['executable_cases'])==new['executable_case_count']==12312
assert sum(not x['result'] for x in new['executable_cases'])==131
for name,item in new['commands'].items():
    assert sha(r/'verification'/(name+'.log'))==item['log_sha256']
    assert item['returncode']==(1 if name.startswith('negative-') else 0)
for name in ['axioms','executable-examples']:
    assert (r/'verification'/(name+'.log')).read_bytes().startswith((r/'prior-verification'/(name+'.log')).read_bytes())
lines=(r/'verification/executable-examples.log').read_text().splitlines()
assert lines==['PASS '+x['name']+': '+str(x['result']).lower() for x in new['executable_cases']]
code=ast.parse((p/'candidate/check.py').read_text());fn=next(n for n in code.body if isinstance(n,ast.FunctionDef) and n.name=='parse_axiom_audit');scope={'re':re,'ALLOWED_AXIOMS':{'propext','Quot.sound','Classical.choice'}}
exec(compile(ast.Module(body=[fn],type_ignores=[]),'<archived-parser>','exec'),scope)
parsed=scope['parse_axiom_audit']((r/'verification/axioms.log').read_text());assert parsed==new['declaration_axioms']
assert all(parsed[n]==['propext'] for n in e['audit_names'])
for name,terms in [('negative-child',['Type mismatch','descendant','child']),('negative-adjacent',['Type mismatch','EarlierSibling','AdjacentSibling'])]:
    log=(r/'verification'/(name+'.log')).read_text();assert all(t in log for t in terms)
n=read(r/'NATIVE-BEFORE.json');assert n==read(native/'INSTALLATION.json')['after']
assert len(n['pins'])==599 and len(n['snapshot']['sources'])==72 and len(n['installed_tests'])==21
assert len(before['parent']['staged_paths'])==925 and len(before['nested']['staged_paths'])==4
assert before['nested']['index_path'].endswith('/artifacts/css-spec-lean/.git/index')
for k in ['head','index_entries_sha256']:assert before['parent'][k]==n['snapshot'][k]
assert before['parent']['staged_diff_sha256']==n['snapshot']['index_diff_sha256']
wrapper=(r/'apply.py').read_text()
for gate in ["assert working() == post", "assert git_state(ROOT) == before['parent']", "assert git_state(LIB) == before['nested']",'assert native.verify() == native_before']:
    assert gate in wrapper
assert wrapper.index('assert native.verify() == native_before') < wrapper.index("write('CHECK.json'")
assert new['status']=='pass' and not new['browser_refinement_proved'] and not new['spec_translation_mechanically_proved']
for f in ['ROOT-EXECUTION.json','CHECK.json','BEFORE.json','NATIVE-BEFORE.json','apply.py','verification/report.json']:
    refs[str((r/f).relative_to(ROOT))]=sha(r/f)
result={'status':'CANONICAL_ROUND_KNOWLEDGE_TERMINAL_REVIEW_GO','session':77965,'exit':0,'authenticated_runtime_payloads':total,'audits':11724,'cases':12312,'sources':2135,'expected_false':131,'new_axioms':['propext'],'old_raw_audit_case_prefixes_exact':True,'six_command_receipts_hashes_verified':True,'post_source_map_derived_from_exact_preimages_and_reviewed_patch':True,'prior_working_files':len(before['working_sha256']),'unrelated_working_files':len(before['working_sha256'])-len(e['modified_paths']),'main_staged':925,'nested_staged':4,'native_before_join':{'roles':599,'sources':72,'identities':21},'final_live_preservation_evidence':'authenticated executed wrapper assertions plus root exit0/CHECK; no separate AFTER index/native map stored and no reviewer live reread','canonical_mutation_by_reviewer':False,'compiler_rerun':False,'research_theorem_credit_delta':0,'normative_coverage_delta':0,'authorship':'Reviewer authored integration proposal; application wrapper and observed execution are root-authored.'}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'REFERENCES.json').write_text(json.dumps(refs,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
