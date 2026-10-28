import ast
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
read = lambda p: json.loads(p.read_bytes())
source = ast.parse((HERE / 'apply.py').read_text())
function = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_projection')
namespace = {'copy': copy}
exec(compile(ast.Module(body=[function], type_ignores=[]), 'projection', 'exec'), namespace)
check = namespace['validate_projection']
epoch, policy = read(HERE / 'INITIAL-CURRENT-EPOCH.json'), read(HERE / 'POLICY.json')
roles = policy['source_roles']
current = copy.deepcopy(epoch)
for path, record in roles.items():
    for directory, key in [('v4','v4_sha256'), ('ordinary-restored','ordinary_restored_sha256'), ('original','base_sha256')]:
        body = (ROOT / policy['proposal'] / directory / path).read_bytes()
        assert hashlib.sha256(body).hexdigest() == record[key]
    for key in ['pins','committed_research_working_payloads']:
        if path in current[key]: current[key][path] = record['ordinary_restored_sha256']
current['modified_native_paths'] = ['servo/components/style/custom_properties.rs']
current['counts']['native_modified_paths'] = 1
current['registered_number_transition'].update(variant=policy['variant'],compiled=False,accepted=False,last_phase=policy['label'])
current['registered_provider_default_transition'].update(manifest_sha256=policy['proposal_manifest_sha256'],changed_native=current['modified_native_paths'],written_native=sorted(roles),accepted=False)
check(epoch,current,roles,policy)
mutations = [
    ('staging', lambda c: c['staged_working'].clear()),
    ('head', lambda c: c['semantic_index'].update(head='0'*40)),
    ('cached patch', lambda c: c['semantic_index'].update(cached_diff='wrong')),
    ('compiled', lambda c: c['registered_number_transition'].update(compiled=True)),
    ('accepted', lambda c: c['registered_number_transition'].update(accepted=True)),
    ('dirty cascade', lambda c: c['modified_native_paths'].append('servo/components/style/properties/cascade.rs')),
    ('dirty count', lambda c: c['counts'].update(native_modified_paths=2)),
    ('ownership identity', lambda c: c['installed_identities'].__setitem__(next(iter(roles)),[0,0])),
    ('binary', lambda c: c['pins'].__setitem__('objdir-full.noindex/dist/Nightly.app/Contents/MacOS/XUL','0'*64)),
    ('untracked', lambda c: c['untracked_native'].append('unexpected')),
    ('nested', lambda c: c['nested_semantic_index'].update(head='0'*40)),
    ('native body', lambda c: c['pins'].__setitem__(next(iter(roles)),'0'*64)),
]
rejected=[]
for name, mutate in mutations:
    bad=copy.deepcopy(current); mutate(bad)
    try: check(epoch,bad,roles,policy)
    except AssertionError: rejected.append(name)
    else: raise AssertionError('accepted corruption: '+name)
assert len(rejected)==12
result={'positive_projection':True,'negative_controls':rejected,'source_postimages_authenticated':True,'main_executed':False,'live_state_queries':False}
(HERE/'CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
