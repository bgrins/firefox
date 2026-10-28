import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
b=load('binding_under_test',HERE/'bindings.py')
a=load('assessment_under_test',HERE/'assess.py')
runner=load('publication_under_test',HERE/'run.py')
fixed=json.loads((HERE/'POLICY.json').read_text())
checks=load('checks_under_test',ROOT/fixed['helpers']['checks'])
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(value,message):
    if not value:raise RuntimeError(message)
h=SimpleNamespace(read=read,sha=sha,need=need,load=load)
rejected=[]
with tempfile.TemporaryDirectory(prefix='lh-original-replay-',dir='/private/tmp') as tmp:
    root=Path(tmp);here=root/'artifacts/capsule';here.mkdir(parents=True)
    def save(path,value):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
    save(here/'POLICY.json',fixed);save(here/'FILES.json',{})
    shutil.copyfile(HERE/'SIGNING-BASELINE-EPOCH.json',here/'SIGNING-BASELINE-EPOCH.json')
    shutil.copyfile(HERE/'assess.py',here/'assess.py')
    checkpath=root/fixed['helpers']['checks'];checkpath.parent.mkdir(parents=True);shutil.copyfile(ROOT/fixed['helpers']['checks'],checkpath)
    owner=root/fixed['owner_runtime'];old=owner/'original-wpt';old.mkdir(parents=True)
    meta={'path':'/synthetic/application.ini','resolved':'/synthetic/application.ini','sha256':'a'*64,'browser_build_id':'20261028000000','revision':fixed['frozen_head']}
    events=[{'action':'suite_start','run_info':dict(os='mac',debug=False,browser_build_id=meta['browser_build_id'],revision=meta['revision'])}]
    for test in fixed['tests']:
        events.append({'action':'test_start','test':test})
        for name in (fixed['target_subtests']|fixed['regression_subtests'])[test]:
            events.append({'action':'test_status','test':test,'subtest':name,'status':'FAIL' if test in fixed['target_subtests'] else 'PASS','expected':'PASS','message':'fixed'})
        events.append({'action':'test_end','test':test,'status':'OK'})
    events.append({'action':'suite_end'})
    epochs={};policies={}
    for role in ['original','candidate']:
        build=owner/(role+'-build')
        epoch=copy.deepcopy(read(HERE/'SIGNING-BASELINE-EPOCH.json'))
        epoch['reversible_line_height_phase']=dict(role=role,build_directory=str(build.relative_to(root)),source_package_manifest=fixed['source_package_manifest'],owner_runtime=fixed['owner_runtime'])
        epoch['pins'].update(fixed['source_roles'][role])
        epoch['pins'].update({n:('a' if role=='original' else 'b')*64 for n in fixed['normal_binaries']})
        epoch['installed_identities']['servo/components/style/values/specified/font.rs']=[1,2]
        if role=='candidate':epoch['modified_native_paths'].append('servo/components/style/values/specified/font.rs')
        save(build/'EPOCH.json',epoch)
        save(build/'RESULT.json',dict(command_success=True,preservation_verified=True,source_role=role,error=None,owned_processes={},publication_errors=[],browser_build_performed=True))
        save(build/'build-RESULT.json',dict(exit=0,error=None,stop_reason=None,cleanup_errors=[],owned_group_absent=True));save(build/'COMMAND.json',{})
        epochs[role]=epoch
        if role=='original':
            q=b.bind_policy(root,here,fixed,epoch,sha(build/'EPOCH.json'),'original-1',h)
            save(old/'POLICY.json',q);shutil.copyfile(build/'EPOCH.json',old/'EPOCH.json')
            assessment=a.assess(events,1,q,checks,run_binding=meta)
            assessed = copy.deepcopy(assessment)
            assessment = runner.augment_assessment(assessment, phase='original-1',
                capsule_sha=sha(here/'FILES.json'), epoch_sha=q['epoch_sha256'], policy=q,
                capsule_directory=str(here.relative_to(root)), experiment_sha='e'*64,
                execution_preserved=True)
            assert all(assessment[k] == v for k, v in assessed.items())
            collision = dict(assessed, phase='untrusted')
            try:
                runner.augment_assessment(collision, phase='original-1', capsule_sha='a'*64,
                    epoch_sha='b'*64, policy=q, capsule_directory='artifacts/capsule',
                    experiment_sha='e'*64, execution_preserved=True)
            except RuntimeError:
                rejected.append('publication field collision')
            else:
                raise AssertionError('publication replaced assessed field')
            save(old/'ASSESSMENT.json',assessment);save(old/'RESULT.json',dict(exit=1,observation_gate_passed=True,execution_error=None,preservation_error=None))
            for name in ['PRE.json','POST.json']:save(old/name,{'unchanged':True})
            for name in ['APPLICATION-METADATA.json','APPLICATION-METADATA-POST.json']:save(old/name,meta)
            save(old/'CLEANUP.json',dict(owned_group_absent=True,temporary_root_removed=True))
            (old/'raw.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events))
    q=b.bind_policy(root,here,fixed,epochs['candidate'],sha(owner/'candidate-build/EPOCH.json'),'candidate-1',h)
    b.validate_original(root,here,q,h)
    originals={p:p.read_bytes() for p in old.iterdir() if p.is_file()}
    mutations=[('changed published caveat','ASSESSMENT.json',lambda s:s.replace('Contextual line-height targets; original failures are observations, not infrastructure failures.','changed annotation')),
               ('changed raw diagnostic','raw.jsonl',lambda s:s.replace('"message": "fixed"','"message": "changed"',1)),
               ('false preservation','ASSESSMENT.json',lambda s:s.replace('"execution_preserved": true','"execution_preserved": false')),
               ('cleanup incomplete','CLEANUP.json',lambda s:s.replace('"owned_group_absent": true','"owned_group_absent": false')),
               ('altered source role','ASSESSMENT.json',lambda s:s.replace(next(iter(fixed['source_roles']['original'].values())),'f'*64)),
               ('altered fixed roster','POLICY.json',lambda s:s.replace('literal resolves before unitless line-height is used','wrong name',1))]
    for label,name,mutate in mutations:
        for path,data in originals.items():path.write_bytes(data)
        path=old/name;path.write_text(mutate(path.read_text()))
        # Re-pin the corrupted inventory to test semantic replay rather than merely file hashing.
        bad=copy.deepcopy(q);bad['original_binding']['files'],bad['original_binding']['symlinks']=b.inventory(old,h)
        try:b.validate_original(root,here,bad,h)
        except (RuntimeError,KeyError):rejected.append(label)
        else:raise AssertionError(label)
    for path,data in originals.items():path.write_bytes(data)
    candidate_epoch_path = owner/'candidate-build/EPOCH.json'
    for field in ('cached_diff', 'entries', 'head'):
        changed = copy.deepcopy(epochs['candidate'])
        changed['semantic_index'][field] = 'wrong'
        save(candidate_epoch_path, changed)
        try:b.validate_original(root,here,q,h)
        except (RuntimeError,KeyError):rejected.append('changed actual semantic field '+field)
        else:raise AssertionError(field)
    save(candidate_epoch_path, epochs['candidate'])
receipt=dict(positive=1,rejected=rejected,browser_executed=False,live_state_queried=False,scratch_removed=True,
             semantic_schema_source='SAVED-SEMANTIC-INDEX.json extracted from SIGNING-BASELINE-EPOCH.json at signed HEAD19ec304f')
(HERE/'ORIGINAL-CONTROLS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(dict(positive=1,rejected=len(rejected))))
