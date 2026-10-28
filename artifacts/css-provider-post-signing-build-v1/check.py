import ast, copy, hashlib, importlib.util, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
read=lambda p:json.loads(p.read_bytes())
spec=importlib.util.spec_from_file_location('succession_check',HERE/'succession.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
policy=read(HERE/'POLICY.json');signing=ROOT/policy['signing']
initial=read(signing/'INITIAL-EPOCH.json');current=read(HERE/'INITIAL-EPOCH.json')
items=[read(signing/(n+'-item.json')) for n in read(signing/'SYNC-PLAN.json')['receipt_ids']]
module.validate_projection(initial,current,items)
mutations=[
 ('native',lambda e:e['pins'].__setitem__('servo/components/style/custom_properties.rs','0'*64)),
 ('binary',lambda e:e['pins'].__setitem__('objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','0'*64)),
 ('compiled',lambda e:e['registered_number_transition'].update(compiled=True)),
 ('accepted',lambda e:e['registered_number_transition'].update(accepted=True)),
 ('staging',lambda e:e['staged_working'].update(initial['staged_working'])),
 ('dirty-scope',lambda e:e['modified_native_paths'].append('servo/components/style/properties/cascade.rs')),
 ('working-diff',lambda e:e['semantic_index'].update(working_diff='changed')),
 ('ownership',lambda e:e['installed_identities'].__setitem__('servo/components/style/custom_properties.rs',[0,0])),
 ('nested',lambda e:e['nested_semantic_index'].update(head='0'*40)),
 ('research-credit',lambda e:e['committed_research_working_payloads'].update(unexpected='0'*64)),
]
rejected=[]
for name,mutate in mutations:
 bad=copy.deepcopy(current);mutate(bad)
 try:module.validate_projection(initial,bad,items)
 except AssertionError:rejected.append(name)
 else:raise AssertionError(name)
assert len(rejected)==10
for path,pin in read(HERE/'REFERENCES.json').items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==pin,path
src=(HERE/'build.py').read_text();ast.parse(src)
assert "s.a = s.load('build_staged_guard'" not in src
assert src.rindex('ownership.quiescent(HERE)')<src.index("s.save(directory / 'COMMAND.json'")<src.index('builder.run(')
result={'saved_signing_projection':True,'negative_controls':rejected,'references_authenticated':True,'ordinary_guard_retained':True,'own_command_after_quiescence':True,'main_executed':False,'live_state_queries':False,'git_signature_reexecution':False}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
